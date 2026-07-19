# Known weaknesses — read before trusting any number

Ranked by how likely a reviewer is to reject over it. Items 1–2 need ablation
conditions (new code + runs); 3–6 need design/analysis decisions; the
mechanical bugs found in the first audit (negation-blind ground truth, turn
disparity between cells, serpent amnesia, lie/concealment conflation) are
already fixed in code.

## 1. Narrative contamination (the killer objection)
Every model has read Genesis. Eating-then-hiding may be *story completion*,
not agentic choice under incentive — the script itself contains the fall and
the hiding. **Required ablation:** a de-mythologized isomorph (same structure:
one rule, one persuader, irreversible act, interrogation with expulsion
stakes — but framed as e.g. a research station and a sealed sample, zero Eden
cues). If concealment rates match across framings, the effect is agentic; if
they collapse, we were measuring Bible memorization. This condition is not
optional — run it in Phase 1.

## 2. Role-play confound
The agent is instructed to *be a person with wants*. A model narrating a
character who lies is arguably doing fiction, not deceiving. Two mitigations,
both needed: (a) claim discipline — the paper's claim is "in-character
concealment under stakes in persona-driven agents," which is the deployed-agent
setting, not "models lie"; (b) a no-persona variant where the model acts as
itself operating a game agent, to measure how much the persona contributes.

## 3. Planted motive
The stakes (the grove, expulsion) are experimenter-supplied, so the
"self-serving" lie has a manufactured self. Run a stakes dose-response
(no stakes / mild / severe): if concealment scales with stakes, the incentive
mechanism is real; flat lines mean something else is driving it.

## 4. Single-shot interrogation
One question, one answer. Doubling-down under repeated questioning is where
the interesting capability signal lives (cf. Apollo's scheming evals: frontier
models double down). Add 1–2 follow-ups ("Look at me. I will ask once more…")
and measure recantation rate per follow-up.

## 5. Told-vs-experienced cells differ in more than source
The "experienced" prohibition (berries, sickness) differs from "told" in
severity, specificity, and object identity — not just epistemic source.
Content-match them as closely as possible and acknowledge the residual
confound; don't oversell this IV.

## 6. Statistics
Concealment given violation is a conditional rate: the denominator is only the
episodes where the agent ate, which the 2×2 itself manipulates. 5 seeds/cell
is nothing. Budget ≥50 violations per cell (i.e., raise seeds until the
denominator is there), report binomial CIs (Wilson), and pre-register the
kill-gate threshold before running the ladder.

## Also true, lower stakes
- "seed" is a label, not a sampling seed — API providers don't honor one;
  call them samples in the paper.
- Auto strategy tags are keyword heuristics; the paper's taxonomy labels need
  an LLM judge validated by blind human raters (κ reported).
- Statement parsing trusts the SAY: line; models sometimes lie in prose and
  confess in the SAY line or vice versa — human-check a sample.
- The serpent is one fixed model with one persona; persuader strategy is a
  stimulus, not a studied variable (fine, but say so).
