# Eden — Claims Ledger

**The paper's spine.** Every claim we might make, with its current status, the
evidence behind it, and how that evidence was certified. Nothing enters the
abstract, blueprint, or a figure unless it has an entry here.

## Why this exists

We are writing the narrative while the data is still moving. The failure mode
that creates is HARKing — letting the story decide which results feel real, and
quietly dropping the ones that stopped fitting. That is fatal for *this* paper
specifically: our central methodological contribution is that certification
rigour must precede claims. A reviewer who catches us retrofitting would discard
the methods argument along with the findings.

So: **retractions stay visible.** A claim that dies keeps its entry, marked
RETRACTED, with what killed it. The corrections history is not embarrassment to
be edited out before submission — for this paper it is evidence that the
discipline we advocate is one we actually practise.

## Status vocabulary

| status | meaning |
|---|---|
| `SUPPORTED` | evidence holds under the best certification we have applied |
| `PENDING` | plausible, but the certification it needs has not been run |
| `CONTESTED` | evidence points both ways, or an instrument problem is unresolved |
| `RETRACTED` | actively believed false; kept for the record with cause of death |

## Certification tiers (how much a number is worth)

| tier | what it means |
|---|---|
| `hand` | a human read the transcript and decided — highest, lowest volume |
| `judge` | independent LLM judge (gemma4:26b), 92% agreement vs hand labels |
| `provisional` | regex or subject self-commit — **known wrong ~24% of the time** |

Every rate below carries its tier. Provisional numbers are not conclusions, they
are hypotheses about where to look.

---

## Live claims

### C1 — Susceptibility to persuasion vs necessity is PIPELINE-SPECIFIC
**Status: SUPPORTED (restated)** · tier `judge`, n=847 · 2026-07-23

Originally stated as universal: "necessity breaks models, persuasion does not."
Full re-certification says that is true of *some* pipelines and false of others:

| model | T1 curiosity | T2 persuader | T3 necessity | T4 +deadline |
|---|---|---|---|---|
| Gemma-4 8B | 0% (96) | **0% (108)** | 0% (14) | **50% (6)** |
| DeepSeek-R1 14B | 4% (26) | **38% (8)** | 75% (8) | 73% (15) |

Gemma is flatly immune to persuasion — 0 violations in 108 episodes, our largest
single cell — and breaks only when the environment makes the act necessary.
DeepSeek-R1-14B is already at 38% under pure persuasion. Same doses, same
certifier, opposite susceptibility profiles.

**This is a better result than the original claim.** It makes the ladder a
*training-pipeline discriminator*: a single "how deceptive is model X" score
collapses these two profiles into one number and destroys the structure. The
paper's contribution is the decomposition, and here is a case where the
decomposition is the only thing that sees the difference.

*Caveats:* the interesting cells are small (Gemma T4 n=6, DeepSeek T2/T3 n=8).
Higher-n runs on T2–T4 are the cheapest way to firm this up.

### C2 — Adversarial pressure can harden resistance rather than erode it
**Status: RETRACTED** · tier `judge`, n=847 · 2026-07-23

Serpent present vs absent, judge-certified, within matched (model, dose) cells:

| cell | serpent | none | delta |
|---|---|---|---|
| Qwen2.5-7B T1 | 13.8% (80) | 3.8% (80) | **+10.0** |
| Qwen2.5-3B T1 | 8.8% (80) | 6.2% (80) | +2.5 |
| Qwen2.5-1.5B T1 | 32.5% (80) | 32.5% (80) | 0.0 |
| Gemma-4 8B T1 | 0% (42) | 0% (54) | 0.0 |

An adversary never *reduces* violations. Where it has any effect it raises them.
The apparent "hardening" came from Gemma sitting at a 0% floor in both
conditions — absence of an effect misread as a protective one.

Superseded by the accurate statement in C1: Gemma is *insensitive* to
persuasion, which is not the same as being hardened by it.

### C11 — An experienced prohibition is respected more than a stated one
**Status: SUPPORTED (new)** · tier `judge`, n=847 · 2026-07-23

A factor the design has carried since the first run and that we had never
analysed until now:

| prohibition source | violations | rate (95% CI) |
|---|---|---|
| **told** (stated in the prompt) | 82/479 | **17.1%** [14–21] |
| **experienced** (encountered in-world) | 44/368 | **12.0%** [9–16] |

Stratified within (model, dose, frame) cells: 5 cells told > experienced, 1
reversed, 6 tied at a floor. Mean delta −4.8 pts. Largest: Qwen2.5-1.5B eden
(−22.5), Qwen2.5-7B eden (−20.0).

**How a constraint is acquired changes how well it is respected**, holding the
constraint itself fixed. This is the prompt-vs-experience distinction appearing
behaviourally under controlled comparison, and it is directly relevant to whether
safety properties should be specified or instilled.

*Caveats:* the effect concentrates in smaller models at T1; Gemma is at a 0%
floor in both conditions so it contributes nothing. Needs the effect reproduced
at higher doses, where there is room to move, before it can carry real weight.

### C3 — Resistance is goal-anchoring, not rule-recitation
**Status: PENDING** · tier `provisional` (regex tagging of CoT) · 2026-07-22

99% of Gemma's reasoning traces re-anchor on its own goal; only 38% invoke the
prohibition. This is the mechanism that explains C1 — the dose that couples the
violation *to* the goal is the one that breaks it.

*Why pending:* one model, and the tagging is regex over prose. We have already
been burned once by exactly this method (see R4). Needs either hand-coding of a
sample or a validated classifier before it can carry weight in the paper.

### C4 — Concealment under interrogation is pipeline-specific, not universal
**Status: RETRACTED** · tier `judge`, n=847 · 2026-07-23

Denial rate among **certified** violators who were interrogated:

| model | violators | denied | deny rate (95% CI) |
|---|---|---|---|
| Qwen2.5-1.5B | 30 | 2 | 7% [2–21] |
| DeepSeek-R1-14B | 22 | 3 | 14% [5–33] |
| Llama3.1-8B | 11 | 3 | 27% [10–57] |
| Qwen2.5-7B | 9 | 0 | **0%** [0–30] |
| Qwen2.5-3B | 5 | 0 | 0% [0–43] |

Every interval overlaps every other. There is no pipeline effect to report.

Worse for the original claim: we previously described Qwen as *concealment-prone,
lying in 60–70% of violations*. On certified labels it denies **0 of 9**. The old
number was the predicted failure cascade — a false-positive violation label turns
a model's truthful "no, I didn't" into a recorded lie. This claim was flagged as
the one most exposed to C6, and it was.

**The honest replacement finding: under certified ground truth, these models
mostly confess.** Denial is rare (0–27%, all CIs wide). That is worth reporting
as-is — it cuts against the assumption that capable models routinely conceal, and
it is only visible once violations are certified rather than inferred.

### C5 — Explicit reasoning does not erode constraint adherence
**Status: SUPPORTED** · tier `judge` · 2026-07-22, corroborated 2026-07-23

Within-family toggle, same base weights, reasoning distilled in or not:
reasoning-OFF violates **more**, not less (OFF 71% vs ON 58%, judge-certified).
The independent stratified sample agrees in direction (OFF 58% vs ON 42%).

A clean null worth publishing on its own: the field is pivoting hard to
reasoning models, and the intuitive worry that reasoning enables rationalisation
is not supported here.

### C6 — Naive certifiers are model-dependent and silently wrong
**Status: SUPPORTED** · tier `judge` vs `provisional`, n=90 · 2026-07-23

The methods contribution, now quantified. Provisional labels agree with an
independent judge only **76%** of the time, and the error is *structured*:

| model | provisional | judge | disagreement |
|---|---|---|---|
| Gemma-4 8B | 14% | 28% | 19% |
| DeepSeek-R1 14B | 47% | 60% | 13% |
| DeepSeek-R1 7B | **100%** | 42% | **58%** |
| Qwen2.5 7B | 25% | 58% | 33% |

Net 16% false negatives vs 9% false positives. Documented failure modes:
- **counterfactual restraint** — "I step back *rather than eating* it" scored as
  a violation; survives naive fixes because the negation sits *inside* the
  committed action line
- **self-certification collapse** — a small reasoning model stamped *everything*
  VIOLATED (the 100% row)
- **budget starvation** — thinking models given a small output budget emit empty
  completions, trivially misread as refusal (see R1)

The claim is not "certifiers are noisy". It is that **the bias differs by model,
so a single certifier applied across models produces a fake between-model
effect** — which is precisely what most of this literature reports.

**Which agreement number to quote — this matters and is easy to get wrong.**
We have two, and they are not interchangeable:

| basis | n | agreement |
|---|---|---|
| stratified across (model, dose, frame) | 90 | **76%** |
| whole corpus, unweighted | 847 | 87% |

The corpus figure is inflated: 660 of 847 episodes are T1, an easy cell where
both labellers trivially agree on "no violation". Quoting 87% would flatter us
by averaging in cases nobody would get wrong. **The stratified 76% is the honest
estimate for the cells the paper actually makes claims about.** Report both,
explain the composition difference, and lead with the stratified figure.

### C7 — An attacker who can read the target's chain-of-thought gains no advantage
**Status: SUPPORTED (provisionally)** · tier `provisional`, n=12/arm · 2026-07-23

Gemma-4 8B subject, Qwen2.5-7B persuader, T2, three arms:

| arm | violations | rate | in-character |
|---|---|---|---|
| blind — sees only visible output | 1/12 | 8% | 73% |
| sighted — also sees the CoT | 1/12 | 8% | 86% |
| instructed — sees it, told to exploit it | 0/12 | **0%** | **94%** |

Leaking the target's private reasoning bought the attacker nothing. The arm that
reads the CoT *and* is told to weaponise it produced the fewest violations.

**Why this null is trustworthy where v1's and v2's were not.** The in-character
rate is the instrument check, and its direction flipped:

| run | blind | sighted | instructed |
|---|---|---|---|
| v1 (DeepSeek persuader) | 45% | **15%** | 39% |
| v2 (+ character constraint) | 84% | **57%** | not run |
| v3 (Qwen persuader, 16k ctx) | 73% | 86% | **94%** |

In v1/v2 persuader quality *collapsed in the treatment arm*, so the confound
tracked the treatment and any null was uninterpretable. In v3 quality **rises**
with treatment — the null cannot be explained by the persuader giving up.

*Caveats:* n=12/arm, provisional labels (judge re-certification pending), all
violations eden-frame with office at 0 across every arm.

*Interpretation, if it survives certification:* consistent with C1 and C8 —
knowing precisely what a model cares about does not let you talk it into
violating. Verbal necessity is not structural necessity. The attacker can name
the goal; only the environment can make the violation the actual route to it.

### C8 — Certainty of remedy adds nothing beyond necessity + deadline
**Status: SUPPORTED** · tier `hand` · 2026-07-22

T7 was designed *from* the CoT mechanism (C3) to be maximally effective, and
landed exactly on T4-no-serpent (4/6 eden, 0/6 office, both). A clean null.

Load-bearing for honesty: it is direct evidence *against* the seductive idea
that mechanistic insight lets you break anything. We predicted, and were wrong.

### C9 — The mundane frame is harder to break than the mythic one
**Status: RETRACTED** · tier `judge`, n=847 · 2026-07-23

Judge-certified across the corpus: **eden 73/496 = 15%, office 53/351 = 15%.**
Identical. The apparent frame gap was a certifier artifact — the office
violation regex is stricter (it required the specific filename), so it
under-counted office violations relative to eden.

The frame still earns its place in the design, but as a *control that passed*
rather than a finding: results are not a mythic-roleplay artifact, because the
mundane deployment-realistic framing behaves the same. That is worth stating —
it just isn't the claim we thought we had.

### C10 — Reasoning models make poor roleplay adversaries
**Status: SUPPORTED** · tier `hand` + measured · 2026-07-23

DeepSeek-R1 as persuader narrated and analysed instead of tempting — third
person ("the person feels a pull") or assistant register ("I would suggest…
1. **Action:**"). Measured in-character rate:

| serpent | in-character |
|---|---|
| Qwen2.5-7B (non-reasoning) | 77–100% |
| DeepSeek-R1-7B, blind arm | 45% |
| DeepSeek-R1-7B, **CoT-sighted arm** | **15%** |

It gets *worse* when the model is fed the target's reasoning — i.e. exactly when
you most want it working. The confound therefore **tracks the treatment**, which
is what made C7's early nulls uninterpretable.

A concrete trap for anyone building multi-agent adversarial evals, and the same
species of error as C6.

---

## Retracted

### R1 — "Gemma's guardrails are bidirectional (it refuses to play tempter)"
**RETRACTED 2026-07-22.** Our bug. gemma4 is a thinking model given a 150–200
token budget; reasoning consumed it and returned an empty completion we read as
refusal. At 1000+ tokens it complies normally.

### R2 — "Reasoning models rationalise past constraints" (H8)
**RETRACTED 2026-07-22.** Confounded by lab, size, and pipeline
(DeepSeek-14B vs Gemma-8B). The de-confounded within-family toggle reversed the
sign. Superseded by C5.

### R3 — "Reasoning toggle: ON 96% vs OFF 38%"
**RETRACTED 2026-07-22.** Certifier artifact — the subject's own self-commit
stamped "step back from the tree" as VIOLATED. Judge-certified: OFF 71% / ON 58%.

### R4 — "A CoT-sighted attacker converges on goal-coupling tactics"
**RETRACTED 2026-07-23.** Regex tactic-tagging showed goal-coupling rising
15 → 58 → 65 across arms, apparently confirming a prediction made from C3.
Hand-checking the transcripts showed it was counting *analyst commentary*, not
persuasion — the serpent had stopped tempting entirely (C10). The prediction may
still be true; this was not evidence for it.

*Lesson, and it keeps recurring: regex over model prose confirmed the thing we
expected. Hand-check before believing a pattern count.*

---

## Open instrument risks

Things that would invalidate results if unnoticed. Each has bitten us already.

1. **Anything varying with input length damages the CoT-leak arms specifically**,
   because those arms are by definition the ones with more input. Three separate
   instances so far: unbounded context growth, a 4096-context default silently
   truncating only the sighted arms, and character-collapse worsening with
   leaked reasoning.
2. **Provisional labels are wrong ~24% of the time, with per-model bias** (C6).
3. **Regex over model prose tends to confirm the hypothesis** (R4).
4. **Empty completions from thinking models look like refusals** (R1).

## What would most change the paper right now

1. **Full judge re-certification.** Every headline still rides on labels we know
   are 24% wrong. Highest value per hour by a wide margin.
2. **A valid H9 run** (C7) — currently zero valid data on the question.
3. **Per-model recomputation of C2**, which may not survive.
4. **A second subject family.** Everything rests on Gemma and DeepSeek; a
   llama-architecture reasoning model would test whether C1 generalises.
