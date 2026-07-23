# Eden — Working Abstract (v3, 2026-07-23)

*Supersedes v2. Three v2 headline claims were retracted after full judge
re-certification of the corpus — see Corrections. Numbers here are
judge-certified unless marked otherwise.*

---

**When a certifier is wrong differently for different models, a benchmark
measures its own instrument.**

Work on AI deception under pressure is largely observational: bespoke scenarios
establishing that deception can occur, with ground truth inferred from a model's
own statements or matched against a neutral-prompt baseline. We introduce a
parametric environment instrumenting the whole arc — prohibition → temptation →
violation → interrogation — with ground truth recorded at the action token, and
use it to make two arguments.

**First, a methodological one we did not set out to make.** We re-certified our
logged episodes with an independent judge (92% agreement with hand labels) and
found our own regex and self-report certifiers disagreed with it on **24% of
episodes in the cells that carry claims** — and, critically, *the error is
structured by model*: 19% disagreement on one model, 58% on another, in opposite
directions. Uniform noise cancels in a between-model comparison; **structured
bias manufactures one.** Three of our own four substantive findings did not
survive re-certification, including a "concealment is pipeline-specific" result
that dissolved once we could see the apparent lies were models *truthfully*
denying violations they had never committed. We report those retractions in
full, because they are the evidence for the claim.

**Second, a substantive one that did survive.** Decomposing violation pressure
into orthogonal ordered doses — curiosity, hardened persuasion, instrumental
necessity, deadline, second-authority duty, the agent's own principal — and
holding everything else fixed reveals **susceptibility profiles that a scalar
deception score destroys**. Gemma-4-8B is flatly insensitive to persuasion
(0 violations in 108 episodes) and breaks only when the environment makes the
forbidden act the sole route to its goal; DeepSeek-R1-14B is already at 38%
under pure persuasion. Same doses, same certifier, opposite shapes. Only the
decomposition sees the difference.

A through-line runs across three independent results, none designed to test it:
**informational and rhetorical advantage does not move constraint adherence;
structural necessity does.** A persuader given the target's private
chain-of-thought — and explicitly instructed to exploit it — achieved nothing
(0/12; a manipulation check confirms it read and used the reasoning). A dose
designed from the model's own reasoning traces to be maximally effective landed
exactly on the undesigned baseline. An adversary can name the goal, the fear and
the deadline, and still only *assert* that violation is necessary. Only the
world can make it so.

We also report a **clean null on reasoning** — a within-family toggle (same base
weights, reasoning distilled in or not) shows reasoning-off violating *more* —
and a second instrument failure specific to multi-agent evaluation: **reasoning
models cannot hold an adversarial role**, degrading into third-person narration
and analyst commentary, and degrading *worst* precisely when fed the target's
reasoning, so the confound tracks the treatment. Neither failure is visible
without per-model instrument validation, which we argue must precede any claim
in this literature.

---

## Corrections from v2 (all judge-certified, n=847)

1. **RETRACTED — "concealment is pipeline-specific."** Certified denial rates
   among violators: 0–27%, every confidence interval overlapping. The earlier
   "Qwen lies in 60–70% of violations" was the predicted cascade — a
   false-positive violation label turns a truthful denial into a recorded lie.
   Certified, these models **mostly confess**.
2. **RETRACTED — "adversarial pressure hardens resistance."** A serpent never
   lowers violations; where it acts it raises them (Qwen-7B T1: 13.8% vs 3.8%).
   The apparent hardening was a 0% floor in both conditions.
3. **RETRACTED — "the mundane frame is harder than the mythic."** eden 15%,
   office 15%. The gap was a stricter office regex. The frame survives as a
   control that *passed*: results are not a roleplay artifact.
4. **RESTATED — necessity vs persuasion is pipeline-specific**, not universal.
5. **NEW — an experienced prohibition is respected more than a stated one**
   (12.0% vs 17.1%, direction consistent across cells). A factor the design
   carried from the first run and that we had never analysed.

## Positioning

- Load-bearing novelty is the **per-model certifier-bias result** plus
  **pressure-decomposition-as-pipeline-discriminator**. Certified ground truth
  alone is shared with Scheurer 2023 and Apollo 2024; cite as precedent.
- The correction history is an asset, not an embarrassment: it is direct
  evidence that the discipline we advocate is one we practise.

## Known weaknesses (stated before a reviewer states them)

- **All subjects are ≤26B open-weight.** The methods claims survive this; the
  substantive ones do not fully.
- **The most load-bearing cell is small.** Gemma at T4 — the entire basis for
  "necessity breaks it" — is n=6 with the corpus's highest certifier error rate
  (33%). Extension running.
- **The judge is itself a model** at 92% agreement; ~8% error remains, and it
  has not been validated per-subject-model the way we demand of others.

## Next

1. Harden Gemma T4 (in flight) — the claim most exposed to review.
2. Adversary-capability ceiling test (32B persuader) — is the CoT-exposure null
   capability-bound?
3. Third architecture (R1-Distill-Llama-8B) to test whether the ladder shape
   generalises beyond Gemma and Qwen.
