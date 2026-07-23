# Eden — Working Abstract (v2, 2026-07-22)

*Supersedes v1. Several v1 claims were RETRACTED after de-confounding and
certifier repair — see Corrections. Findings remain preliminary (small-N,
open-weight).*

---

**What actually breaks a model's constraint — and why certifying that is
harder than it looks.**

Work on AI deception under pressure is largely *observational*: bespoke
scenarios establishing that deception can occur, treating it as a roughly
uniform property of capable models. We introduce a parametric environment
instrumenting the whole arc — prohibition → temptation → violation →
interrogation — with ground truth recorded at the action token, so a later
denial is a *certified* lie. The core move is to **decompose violation pressure
into orthogonal, ordered doses** (curiosity → hardened persuasion →
instrumental necessity → deadline → second-authority duty → the agent's own
principal) and hold everything else fixed, turning "does it deceive?" into
"*which* pressure breaks *which* training pipeline, and how does it conceal?"

Two substantive findings. First, **what breaks a model is necessity, not
persuasion**: across models, situational necessity (the forbidden act becomes
the only route to a cherished goal) is far more corrosive than any persuader,
and *external pressure to transgress often hardens resistance* rather than
eroding it. Chain-of-thought traces explain the mechanism: in a
safety-tuned model that resists nearly all doses, **99% of reasoning traces
re-anchor on the agent's own goal while only 38% invoke the prohibition** —
resistance is goal-anchoring, not rule-recitation, which is precisely why the
one dose that couples the violation *to* the goal is the one that breaks it.
Second, **concealment is pipeline-specific, not universal**: under identical
certified conditions one family conceals most violations while others mostly
confess — complicating the claim that deception is an emergent property of
capable models.

We also report a **negative result and a methods contribution**, both
load-bearing. A within-family reasoning toggle (same base weights, reasoning
distilled in vs. not) shows **no evidence that explicit reasoning erodes
constraint-adherence** — an earlier apparent effect vanished under
de-confounding. And we document that **naive certifiers are model-dependent and
silently wrong**: keyword matching mis-scores counterfactual restraint ("I step
back *rather than eating* it"), self-certification fails on small reasoning
models, and thinking models starved of output budget emit empty completions
easily misread as refusals. We give a validated LLM-judge protocol (independent
judge, evidence-quoted, 92% vs. hand labels) and argue **per-model certifier
validation must precede any claim** in this literature.

---

## Corrections from v1 (all verified)

1. **RETRACTED — "Gemma's guardrails are bidirectional (refuses to play the
   tempter)."** That was our bug: gemma4 is a *thinking* model and we gave it a
   150–200 token budget; thinking consumed it, yielding an empty completion we
   misread as refusal. At 1000+ tokens it complies normally.
2. **RETRACTED — "Reasoning models rationalize past constraints" (H8).** The
   apparent effect (DeepSeek-14B vs Gemma-8B) was confounded by lab/size/
   pipeline. The de-confounded within-family toggle (qwen2.5-7b vs
   R1-distill-Qwen-7b) shows OFF ≈ ON or OFF higher, across three independent
   certification methods. Claim not supported.
3. **CORRECTED — the toggle's first "ON 96% vs OFF 38%"** was a certifier
   artifact (the subject's self-commit stamped "step back from the tree" as
   VIOLATED). Judge-certified: OFF 71% vs ON 58%.
4. **CONFIRMED — Gemma's resistance is real, not a token artifact.** Re-run with
   reasoning enabled and full budget: T1–T3 0/18, T4 3/6. Matches the original.
5. **Qwen-7B office anomaly** dissolved under re-certification (5 violations → 0).

## Positioning

- Load-bearing novelty is **pressure-decomposition as a training-pipeline
  discriminator** plus the **certifier-validation protocol** — not certified
  ground truth alone (shared with Scheurer 2023, Apollo 2024; cite as method
  precedent).
- The negative reasoning result is worth reporting: the field is pivoting to
  reasoning models and a clean null on "reasoning erodes constraints" is useful.

## Next

1. Judge-certify all logs with the validated gemma:26b judge (script ready),
   then recompute every headline on one uniform certifier.
2. **T7 ("make it squeak")** — derived from the CoT: since resistance is
   goal-anchoring and *adversaries harden it*, couple the violation tightly to
   the goal (certain remedy, not rumor), add the deadline, and **remove the
   serpent entirely**. Predicted to break the resister where persuasion cannot.
3. More seeds on load-bearing cells; frontier pilot; human-audited κ.

## Result snapshot (regex/self-commit labels — pending judge re-certification)

| dose | Gemma 8B | DeepSeek-R1 14B |
|---|---|---|
| T1 curiosity | 0% | 0% |
| T2 hardened persuader | 0% | 40% |
| T3 instrumental necessity | 0% | 75% |
| T4 necessity + deadline | 33–50% | 53% |
| T5 second-authority duty | 12% | 50% |
| T6 principal's own voice | 17% | 38% |

Reasoning toggle (judge-certified, same Qwen2.5-7B base): OFF 71% vs ON 58%.
Qwen ladder: concealment-prone (60–70% lie among violators); Gemma/DeepSeek
mostly confess.
