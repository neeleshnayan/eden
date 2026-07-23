# Eden — Running Protocol

Standing rules, earned the hard way. Each one exists because ignoring it cost us
a run, a claim, or a day.

---

## 1. Sample → hand-check → iterate → only then run full

**Never launch a full scan on an unproven path.** The order is always:

1. **1–2 episodes.** Does it complete at all?
2. **Hand-read the transcripts.** Not the summary statistic — the actual text.
   Is the agent doing what you think? Is the persuader persuading?
3. **A small cell (n≈6).** Does the analysis code run end to end, including
   certification, on this data?
4. **Only then the full run.**

**Why, concretely.** Every instrument failure this project has had would have
been caught at step 2 or 3 for the cost of minutes, and instead was caught after
hours of wasted compute — or worse, produced a confident wrong answer:

| failure | cost | which step would have caught it |
|---|---|---|
| persuader narrated instead of tempting | 2 full runs (72 episodes) | 2 — hand-read one transcript |
| serpent ran at 4096 ctx, truncating leaked CoT | a full v3 restart | 3 — check the loaded context |
| unbounded CoT leak OOM'd the host | crashed the machine twice | 1 — one episode would have shown the growth |
| judge had no definition for new frames | would have made 100+ episodes uncertifiable | 3 — run the certifier once |
| errored episodes dropped, not retried | manufactured a fake 0% vs 25% effect | 2 — look at *which* cells errored |

**A summary statistic cannot tell you the instrument is broken.** Only reading
the raw output can. A regex pattern-count "confirmed" a prediction that hand-
checking showed was counting analyst prose (R4).

## 2. Before a full run, verify the whole path

Not just the runner — everything downstream that will touch the data:

- [ ] the frame/condition exists and renders (no stale template contamination)
- [ ] the dose overlay exists for that frame (a missing T4 situation runs with
      **no pressure** and looks like a legitimate null)
- [ ] the certifier has a definition for that frame
- [ ] the regexes pass a restraint-trap suite (verbs must govern an explicit
      object; "rather than eating **it**" must not count)
- [ ] context headroom for the longest arm
- [ ] the analysis script runs on n=6 of the new data

## 3. Fix the verdict rule before seeing the number

Write the decision criterion into the script. "≥2/12 means capability matters;
≤1/12 means the null holds" — printed by the code, decided in advance. It is the
only defence against reading a story into noise after the fact.

## 4. Errors are not missing-at-random

Violating episodes terminate early, so they are shorter and less exposed to
resource failures. Errors preferentially remove *resisting* episodes. **Always
retry, never drop** — and when a cell has errors, check which conditions they
landed in before interpreting anything.

## 5. Quote the tier

Every number carries `hand` / `judge` / `provisional`. Provisional labels are
wrong ~24% of the time in the cells that carry claims, with **per-model bias** —
so a single certifier across models manufactures between-model differences.

## 6. Relabel, never delete

Data collected under a broken instrument is usually valid data for a *different*
question. 426 episodes mislabelled `experienced` became a 426-episode no-rule
control — the exact baseline the provenance result needed.

## 7. Retractions stay visible

For a paper whose contribution is that certification must precede claims, the
correction history is the evidence we practise it. `CLAIMS.md` keeps dead claims
with their cause of death.

---

## Pre-flight checklist

Copy into the run's notes and tick before launching anything ≥30 episodes.

```
[ ] 1 episode completed end to end
[ ] transcript hand-read: agent in role, persuader persuading, action committed
[ ] certifier has a definition for this frame; restraint traps pass
[ ] dose overlay exists (not silently empty)
[ ] context headroom checked for the longest arm
[ ] n=6 pilot analysed with the real analysis script
[ ] verdict rule written into the script
[ ] resumable, and errors retried rather than dropped
[ ] GPU free (no other job) and commit headroom > 3GB
```
