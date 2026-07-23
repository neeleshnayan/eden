"""Declarative experiment runner — the portable form of the testbed.

Every experiment so far has been a bespoke script that only runs on one machine.
That is fine for exploration and useless for scaling: to run the same design on a
120GB box, or against a frontier API, we need the design expressed as DATA and
the execution as one command.

A spec is JSON:

    {
      "name": "provenance",
      "agent": "ollamathink:gemma4:latest",
      "serpent": "ollamachat:qwen2.5:7b-instruct",
      "dose": "T4",
      "frames": ["eden"],
      "sources": ["told", "told_verified", "experienced", "observed", "norule"],
      "seeds": 30,
      "arms": {"blind": {}},
      "serpent_present": true,
      "max_tokens": 2048,
      "serpent_max_tokens": 400
    }

    python -m eden.suite specs/provenance.json --out logs/provenance.jsonl

Portable by construction:
  * the endpoint comes from OLLAMA_BASE_URL, so pointing at a remote host with
    a bigger GPU is an env var, not a code change;
  * every cell key is deterministic, so a run is resumable and two machines can
    split the same spec and concatenate results;
  * the spec is written into every row, so a log is self-describing months later.

Arms let one spec express a factorial: {"blind": {}, "sighted":
{"serpent_sees_cot": true}} runs both and tags each row.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

from .episode import run_episode

# Options an arm may override. Anything else in an arm block is a spec error
# rather than a silently ignored key — a typo'd flag that quietly does nothing
# is how an experiment ends up measuring the wrong thing.
ARM_KEYS = {
    "serpent_sees_cot", "serpent_cot_instructed", "serpent_present",
    "serpent_in_character", "serpent_selfassess", "serpent_max_tokens",
    "max_tokens", "serpent", "agent", "dose",
}


def load_spec(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        spec = json.load(f)
    for required in ("name", "agent", "dose"):
        if required not in spec:
            raise SystemExit(f"spec is missing required field: {required!r}")
    for arm, over in (spec.get("arms") or {"default": {}}).items():
        bad = set(over) - ARM_KEYS
        if bad:
            raise SystemExit(f"arm {arm!r} has unknown keys: {sorted(bad)}")
    return spec


def cells(spec: dict):
    arms = spec.get("arms") or {"default": {}}
    for arm, over in arms.items():
        for frame in spec.get("frames", ["eden"]):
            for src in spec.get("sources", ["told"]):
                for seed in range(spec.get("seeds", 12)):
                    yield arm, over, frame, src, seed


def key(arm, frame, src, seed) -> str:
    return f"{arm}|{frame}|{src}|s{seed}"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("spec")
    ap.add_argument("--out", default=None, help="default logs/<name>.jsonl")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the cell plan and exit")
    ap.add_argument("--shard", default=None, metavar="i/n",
                    help="run only shard i of n, so machines can split a spec")
    args = ap.parse_args(argv)

    spec = load_spec(args.spec)
    out_path = args.out or os.path.join("logs", f"{spec['name']}.jsonl")
    os.environ.setdefault("OLLAMA_NUM_CTX", str(spec.get("num_ctx", 16384)))
    os.environ.setdefault("OLLAMA_TIMEOUT", str(spec.get("timeout", 420)))

    plan = list(cells(spec))
    if args.shard:
        i, n = (int(x) for x in args.shard.split("/"))
        plan = [c for j, c in enumerate(plan) if j % n == i - 1]

    done = set()
    if os.path.exists(out_path):
        for line in open(out_path, encoding="utf-8"):
            try:
                r = json.loads(line)
                if "error" not in r:
                    done.add(r["k"])
            except Exception:
                pass

    todo = [c for c in plan if key(c[0], c[2], c[3], c[4]) not in done]
    print(f"{spec['name']}: {len(todo)} episodes to run "
          f"({len(done)} done, {len(plan)} in plan)", flush=True)
    print(f"  agent    {spec['agent']}")
    print(f"  serpent  {spec.get('serpent','-')}")
    print(f"  endpoint {os.environ.get('OLLAMA_BASE_URL','http://localhost:11434 (default)')}",
          flush=True)
    if args.dry_run:
        for arm, _, frame, src, seed in todo[:20]:
            print("   ", key(arm, frame, src, seed))
        if len(todo) > 20:
            print(f"    ... and {len(todo)-20} more")
        return 0

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    t_start = time.time()
    with open(out_path, "a", encoding="utf-8") as out:
        for n, (arm, over, frame, src, seed) in enumerate(todo, 1):
            k = key(arm, frame, src, seed)
            kw = dict(
                agent_model=over.get("agent", spec["agent"]),
                serpent_model=over.get("serpent", spec.get("serpent", "")),
                prohibition_source=src,
                serpent_present=over.get("serpent_present",
                                         spec.get("serpent_present", True)),
                seed=seed, frame=frame,
                temptation=over.get("dose", spec["dose"]),
                max_tokens=over.get("max_tokens", spec.get("max_tokens", 2048)),
                serpent_max_tokens=over.get("serpent_max_tokens",
                                            spec.get("serpent_max_tokens", 400)),
                serpent_sees_cot=over.get("serpent_sees_cot", False),
                serpent_cot_instructed=over.get("serpent_cot_instructed", False),
                serpent_in_character=over.get("serpent_in_character",
                                              spec.get("serpent_in_character", True)),
                serpent_selfassess=over.get("serpent_selfassess",
                                            spec.get("serpent_selfassess", True)),
            )
            t0 = time.time()
            try:
                log = run_episode(**kw)
                row = log.to_dict()
            except Exception as e:
                row = {"frame": frame, "prohibition_source": src, "seed": seed,
                       "temptation": kw["temptation"], "error": repr(e)[:300]}
            # self-describing: the spec travels with the data
            row.update(k=k, arm=arm, spec=spec["name"],
                       agent_model=kw["agent_model"], serpent_model=kw["serpent_model"])
            out.write(json.dumps(row) + "\n")
            out.flush()
            print(f"  [{n}/{len(todo)}] {k:34s} ate={str(row.get('ate','ERR')):5s} "
                  f"{time.time()-t0:5.0f}s", flush=True)

    print(f"\ndone: {len(todo)} episodes in {(time.time()-t_start)/60:.1f} min "
          f"-> {out_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
