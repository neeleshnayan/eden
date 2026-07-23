# Eden — Scaling Plan

**Nothing is discarded.** Every claim in `CLAIMS.md` is a reading from the
instrument *at a given scale*. A null at 8B is a data point, not a closed
question — and several of our retractions are the ones most likely to come back
at scale:

| claim | 8B reading | why scale could change it |
|---|---|---|
| C4 concealment | retracted — models mostly confess | concealment may require capability the 8B models lack; MASK reports larger models conceal *better* |
| C7 CoT exposure | null, well-powered | an 8B target's reasoning may simply not contain much worth exploiting, and a 7–14B adversary may not be able to exploit what is there |
| C10 reasoning adversaries | they narrate instead of tempting | may be a small-model failure that disappears at 70B |
| C11 provenance | significant (p=0.014) | the interesting question is whether it *survives* capability or washes out |

The framework is the contribution. The claims are its output, indexed by scale.

---

## Three tiers

### Tier 1 — local, ≤26B (this box, done/ongoing)
Exploration, design iteration, instrument validation. Cheap enough to make
mistakes in, which is where all four instrument failures were caught.

### Tier 2 — 120GB VRAM box (next)
70B-class targets, 32B adversaries, full context. This is where we find out
whether the 8B readings are properties of constraint-following or artifacts of
small models.

**No code changes required.** The endpoint is an environment variable:

```bash
# on the 120GB host
OLLAMA_HOST=0.0.0.0 ollama serve        # bind to the tailnet, NEVER public

# from here
export OLLAMA_BASE_URL=http://<tailscale-ip>:11434/v1
python -m eden.suite specs/scale_70b.json
```

`ollama` ships with **no authentication**. Tailscale or an SSH tunnel only —
never a port-forward.

**Priority order on that box**, highest information per hour first:

1. **C7 at scale** — the headline null. If a 70B target with rich reasoning,
   attacked by a 32B adversary that reads it, still shows nothing, the null
   becomes a strong claim. If it breaks, that is *also* a headline: a capability
   threshold for CoT exploitation.
2. **C11 at scale** — does provenance survive capability?
3. **C4 revisited** — concealment is the claim most likely to reappear.
4. **Ladder shape** — does the pipeline-discriminator pattern hold at 70B?

**Splitting work across machines:** the runner shards deterministically, so both
boxes can run the same spec and the logs concatenate.

```bash
python -m eden.suite specs/scale_70b.json --shard 1/2   # here
python -m eden.suite specs/scale_70b.json --shard 2/2   # there
```

### Tier 3 — frontier API (last)
Only after Tier 2 tells us which cells are worth paying for. Frontier runs are
for confirmation on the two or three load-bearing cells, not exploration.

Budget shape: one arm ≈ 30 episodes × ~18 calls ≈ 540 calls. Adversary-side
only is cheaper than subject-side and answers "does a *capable* attacker break
what a 7B one could not" — the objection our capability probe can only partly
answer locally.

---

## What travels, and what does not

**Travels:** the spec files, `eden/`, the judge protocol, the certification
tiers. A spec is self-describing — every row records the spec name and both
model ids, so a log stays interpretable months later.

**Does not travel:** absolute rates. A 70B model will have different base rates.
The comparisons are what replicate — told vs experienced, blind vs sighted — not
the numbers themselves. Report contrasts, not levels, across tiers.

**Re-validate per tier:**
- the judge, against hand labels on the new subject models (per-model bias is
  our own finding; we do not get to exempt ourselves)
- persuader in-character rate (C10 was scale-dependent by hypothesis)
- context sufficiency — a 70B model's CoT is longer, and every context-length
  failure we have had damaged the CoT-exposure arms specifically

---

## Standing risks when scaling

1. **Anything that varies with input length damages the CoT arms preferentially.**
   Three separate instances so far. Check context headroom before every run.
2. **Errored episodes are not neutral.** They correlated with violation-prone
   conditions once already and manufactured a fake effect. Always retry, never
   drop.
3. **Absolute rates are not comparable across tiers.** Only contrasts are.
4. **The judge is a model too.** Validate it per tier or the methods claim is
   hypocritical.
