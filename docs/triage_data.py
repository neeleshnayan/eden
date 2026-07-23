"""Classify every log by trustworthiness, and build a clean derived dataset.

After a day of fast iteration the logs directory mixes data collected under
four different broken instruments with data collected after each was fixed.
Nothing here deletes anything -- data is moved or relabelled, never destroyed,
because today's junk is tomorrow's control condition.

Three statuses:

  TRUSTED     collected after all known instrument fixes; use freely
  DEGRADED    usable with a stated caveat (high error rate, superseded labels,
              mislabelled condition) -- must be filtered or relabelled first
  QUARANTINE  cannot support any claim (broken persuader, smoke tests, runs
              whose usable yield is a small biased remnant); moved out of
              logs/ so a glob cannot sweep it into an analysis by accident

The single most important transformation: episodes run before 2026-07-23 with
prohibition_source="experienced" used a text that established NO PROHIBITION at
all. They are not experienced-rule episodes; they are no-rule controls. The
clean dataset relabels them `norule_legacy` rather than dropping them, so they
keep contributing to the one comparison they can legitimately support.

  python docs/triage_data.py            # report only
  python docs/triage_data.py --apply    # move quarantine + write clean dataset
"""
import argparse
import collections
import json
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS = os.path.join(ROOT, "logs")
QUAR = os.path.join(LOGS, "quarantine")
CLEAN = os.path.join(LOGS, "clean_episodes.jsonl")

# Runs whose persuader was demonstrably not persuading (reasoning-model serpent
# narrating instead of tempting, 15-57% in-character). The arm comparisons they
# produced are uninterpretable.
BROKEN_SERPENT = {"h9_cot_exposure.jsonl", "h9_v2.jsonl"}

SMOKE = {"probe_smoke.jsonl", "smoke_office.jsonl", "pilot_3b.jsonl",
         "gemma8b_peek.jsonl", "ladder2_3b.jsonl", "ladder4_0.5b.jsonl"}

# Derived/analysis outputs, not episode data.
DERIVED = {"judged_full.jsonl", "judge_sample.jsonl", "toggle.judged.jsonl",
           "provenance.judged.jsonl", "clean_episodes.jsonl"}

# The prompts.py fix landed 2026-07-23; everything before used the no-rule text.
FIX_NOTE = "pre-2026-07-23 `experienced` text established no prohibition"


def read(path):
    rows = []
    try:
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except Exception:
                    pass
    except OSError:
        pass
    return rows


def classify(name, rows):
    """-> (status, reasons[])"""
    reasons = []
    good = [r for r in rows if "error" not in r]
    errs = len(rows) - len(good)
    err_rate = errs / max(len(rows), 1)

    if name in DERIVED:
        return "DERIVED", ["analysis output, not episode data"]
    if name in SMOKE:
        return "QUARANTINE", ["smoke test / pilot, never intended as evidence"]
    if name in BROKEN_SERPENT:
        return "QUARANTINE", ["persuader broke character (15-57% in-character); "
                              "arm comparisons uninterpretable"]
    if not good:
        return "QUARANTINE", [f"no usable episodes ({errs} errors)"]
    if err_rate > 0.30:
        reasons.append(f"{errs}/{len(rows)} = {100*err_rate:.0f}% errors "
                       f"(HTTP 500s from disk/commit exhaustion); violating "
                       f"episodes end early so survivors bias toward violations")
        return "QUARANTINE", reasons
    if err_rate > 0.10:
        reasons.append(f"{100*err_rate:.0f}% errors — check survivorship before use")

    if name.endswith(".recert.jsonl"):
        reasons.append("superseded by judge re-certification")
        return "DEGRADED", reasons

    n_exp = sum(1 for r in good if r.get("prohibition_source") == "experienced")
    if n_exp and name not in ("provenance.jsonl", "provenance_llama.jsonl"):
        reasons.append(f"{n_exp} rows labelled `experienced` but {FIX_NOTE} "
                       f"-> relabelled `norule_legacy` in the clean dataset")
        return "DEGRADED", reasons

    return ("TRUSTED", reasons) if not reasons else ("DEGRADED", reasons)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="move quarantined files and write the clean dataset")
    args = ap.parse_args()

    files = sorted(f for f in os.listdir(LOGS) if f.endswith(".jsonl"))
    verdicts = {}
    for name in files:
        rows = read(os.path.join(LOGS, name))
        verdicts[name] = (classify(name, rows), rows)

    order = {"TRUSTED": 0, "DEGRADED": 1, "QUARANTINE": 2, "DERIVED": 3}
    print(f"{'status':12s}{'episodes':>10s}  file")
    print("-" * 100)
    tally = collections.Counter()
    for name in sorted(files, key=lambda f: (order[verdicts[f][0][0]], f)):
        (status, reasons), rows = verdicts[name]
        good = sum(1 for r in rows if "error" not in r)
        tally[status] += good
        print(f"{status:12s}{good:10d}  {name}")
        for r in reasons:
            print(f"{'':12s}{'':10s}    - {r}")

    print()
    print("usable episodes by status: " +
          "  ".join(f"{k}={v}" for k, v in sorted(tally.items())))

    if not args.apply:
        print("\n(report only — pass --apply to move quarantine and write clean dataset)")
        return

    os.makedirs(QUAR, exist_ok=True)
    moved = 0
    for name, ((status, _), _) in verdicts.items():
        if status == "QUARANTINE":
            shutil.move(os.path.join(LOGS, name), os.path.join(QUAR, name))
            moved += 1

    # clean dataset: TRUSTED + DEGRADED, with the legacy relabel applied
    n_out = n_relabel = 0
    with open(CLEAN, "w", encoding="utf-8") as out:
        for name, ((status, _), rows) in sorted(verdicts.items()):
            if status not in ("TRUSTED", "DEGRADED"):
                continue
            if name.endswith(".recert.jsonl"):
                continue
            legacy = name not in ("provenance.jsonl", "provenance_llama.jsonl")
            for r in rows:
                if "error" in r or not r.get("transcript"):
                    continue
                if legacy and r.get("prohibition_source") == "experienced":
                    r["prohibition_source"] = "norule_legacy"
                    r["_relabelled"] = FIX_NOTE
                    n_relabel += 1
                r["_src"] = name
                r["_status"] = status
                out.write(json.dumps(r) + "\n")
                n_out += 1

    print(f"\nquarantined {moved} files -> logs/quarantine/")
    print(f"wrote {CLEAN}: {n_out} episodes, {n_relabel} relabelled to norule_legacy")


if __name__ == "__main__":
    main()
