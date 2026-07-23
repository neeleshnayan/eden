# Eden — Paper Skeleton (v1, 2026-07-23)

Target shape, benchmarked against *In-Context Learning Can Re-learn Forbidden
Tasks* (Xhonneux et al., 2024 — Vicuna/Starling/Llama2 7B, 19 pages, 7 figures,
cs.LG + cs.CR). Small open models, no apology, because the claim is mechanistic.

---

## The question, in one sentence

> **Does an adversary who can read a model's private reasoning gain any
> advantage over one who cannot?**

Falsifiable, answerable on 8B models, and currently untested in this exact
configuration.

## Why it is not already answered

Three adjacent literatures, none of them this:

| existing work | configuration |
|---|---|
| H-CoT, CoT Forgery, BadThink | attacker **writes into** the reasoning (hijack/inject) |
| CoT monitoring | a **monitor** reads the agent's reasoning to catch it |
| multi-agent debate persuasion | agents persuade each other, **no** CoT access |
| **this work** | attacker **reads** the target's reasoning to persuade *that target* |

The read-only case is the one deployments actually create: agent frameworks that
stream or log reasoning, dashboards, multi-agent scratchpads. And the field is
trending toward "visible reasoning is exploitable" — we find it is not, in a
setting where we can prove the attacker read and used it.

## Thesis

**The adversary is not the variable.** Constraint failure is driven by the
situation and the specification, not by adversary capability or information.

Negative half (well-powered, instrument-validated):
- hardened persuader: 0/57 on the safety-tuned model
- read-only CoT exposure: no effect at either dose, manipulation-check verified
- adversary capability: (14B probe)
- reasoning capability: reasoning-**off** violates more

Positive half:
- situational necessity moves violations from ~0% to ~40-70%
- constraint provenance (running)

## Section plan (~19pp incl. appendix)

1. **Introduction** — the question; why read-only CoT exposure is the realistic
   case; contribution bullets (3-4, each one sentence).
2. **Related work** — the three adjacent literatures above, positioned as a
   table rather than prose. Certified-ground-truth precedent: Scheurer 2023,
   Apollo 2024.
3. **Environment** — five beats (prohibition → temptation → serpent →
   action → interrogation); ground truth at the action token; the dose ladder as
   typed pressure rather than an intensity scalar; two frames as roleplay
   control. **Fig 1.**
4. **Certification** — why this section exists *before* results: a null is only
   as good as its instrument. Judge protocol, 92% vs hand labels, and the
   per-model bias result. **Fig 5.**
5. **Instrument validation** — the four failures we caught, as a methods
   contribution: certifier bias, persuader character collapse, silent context
   truncation, survivorship bias in errored episodes. **Fig 6.**
6. **Results — the null** — H9 arms at both doses with CIs; the manipulation
   check. **Figs 3, 4.**
7. **Results — what does move it** — ladder as pipeline discriminator;
   provenance. **Figs 2, 7.**
8. **Discussion** — implications for CoT monitorability and for where
   red-teaming effort should go; what would falsify us.
9. **Limitations** — stated before a reviewer states them.
10. **Appendix** — full prompts, judge rubric, per-cell tables, retraction log.

## Figures (7, all data already collected)

| # | figure | carries |
|---|---|---|
| 1 | design schematic: five beats + dose ladder | orientation |
| 2 | judge-certified ladder, rate × dose × model | pipeline discriminator |
| 3 | **H9 arms with CIs, both doses** | the headline null |
| 4 | **manipulation check: CoT-only vocabulary use by arm** | the null is not a passive attacker |
| 5 | certifier disagreement by model | methods result |
| 6 | in-character rate across v1/v2/v3 | instrument validation, visually |
| 7 | provenance: violation by constraint source | the positive half |

Figs 4 and 6 are what separate this from a careless null. Keep them in the main
body, not the appendix.

## Contribution bullets (draft — one sentence each)

- We test whether **read-only access to a model's chain-of-thought** helps an
  adversary persuade it to violate a constraint, and find no advantage across
  two pressure regimes, with a manipulation check confirming the adversary read
  and used the reasoning.
- We show **certifier error in this setting is structured by subject model**
  (19%–58%, in opposite directions), so a single certifier applied across models
  can manufacture the between-model difference a paper then reports.
- We document **four instrument failures** that each produced a confident wrong
  answer in our own pipeline, and argue instrument validation must precede any
  claim — especially a null.
- We find constraint violation is driven by **situational necessity and
  specification**, not adversary strength or information.

## Standing rules

- No capability claims. Mechanism only. Every subject is ≤26B open-weight and we
  say so in the abstract.
- Every number carries its certification tier.
- Retractions stay visible; the correction log ships in the appendix.
- Verify novelty against the literature before asserting it.

## Open before submission

1. n ≥ 30 per load-bearing cell (currently 12–26).
2. Replicate the null on a second subject family (R1-Distill-Llama-8B ready).
3. Provenance result — the positive half. If null, rescope.
4. Full related-work pass; the search so far is one round.
