# Eden — a testbed for constraint-following under pressure

A minimal, local, frugal environment for one question:

> **What makes a model violate a stated constraint — the adversary, or the
> situation and the specification?**

An agent is given a prohibition, tempted along a typed dose ladder, and
interrogated. Ground truth is recorded at the **action token**, so a later
denial is a *certified* lie rather than an inferred one. Everything runs on
consumer hardware (Ollama, ≤26B open-weight models).

The working thesis, after de-confounding: **the adversary is largely not the
variable.** Persuasion, chain-of-thought exposure, and adversary capability
move constraint violation little; situational necessity and how the constraint
was *acquired* move it a lot. See `docs/CLAIMS.md` for the live ledger — every
claim with its evidence, certification tier, and status, retractions kept
visible.

## Running an experiment

Experiments are declarative JSON specs; one command runs any of them against any
endpoint:

```bash
python -m eden.suite specs/provenance.json
```

- `OLLAMA_BASE_URL=http://<host>:11434/v1` points at a remote GPU — no code change.
- Runs are resumable and shardable (`--shard 1/2`), so two machines split one spec.
- Every row records its spec and model, so a log is self-describing.

**Always judge-certify; never trust regex labels.** Regex certification is
model- and scenario-dependent (it mislabelled 50% of one model's episodes). The
independent judge (`eden/judge.py`, gemma4:26b, 92% vs hand labels) is the
standard.

## Map of the repo

| path | what |
|---|---|
| `eden/episode.py` | the five-beat episode engine |
| `eden/prompts.py`, `eden/scenarios.py` | frames, dose ladder, prohibition conditions |
| `eden/suite.py` | declarative runner (the one trusted path) |
| `eden/judge.py` | independent LLM-judge certifier |
| `eden/models.py` | provider dispatch (ollama / openai-compat / remote) |
| `specs/*.json` | experiment definitions |
| `logs/clean_episodes.jsonl` | **start analyses here** — triaged, relabelled |
| `docs/dashboard.html` | live results, rebuilt from logs |

## The docs (read in this order)

1. **`CLAIMS.md`** — the spine: every claim, status, evidence, tier, date.
2. **`PROTOCOL.md`** — how we run: sample → hand-check → iterate → full run.
3. **`DATA_MANIFEST.md`** — what data is trusted, degraded, quarantined, and why.
4. **`CREDIBILITY.md`** — what reviewers attack and our answer to each.
5. **`ABSTRACT.md`** / **`PAPER_SKELETON.md`** — the paper as it stands.
6. **`SCALING.md`** — the 8B → 70B → frontier path; claims are scale-indexed.

`PAPER_BLUEPRINT.md` is the original plan, kept for history; it predates the
thesis pivot and is superseded by the docs above.

## Standing principles

- No capability claims — mechanism only; every subject is ≤26B open-weight.
- Every number carries its certification tier.
- Retractions stay visible: for a paper arguing that certification must precede
  claims, the correction history is the evidence we practise it.
- Relabel, never delete — today's broken run is tomorrow's control condition.
