# Eden — Credibility Guide

Written for a first paper. The goal is not to be seminal — it is to be **not
laughed at**. Those are different bars, and the second is entirely achievable on
consumer hardware if the discipline is right. A reviewer forgives small models
and modest scope. A reviewer does not forgive a number that falls apart when
they push on it.

This is the map of where they push, and whether we can take it.

---

## What actually makes reviewers laugh (and none of it is "small models")

1. **A headline number computed on a broken instrument.** The single fastest way
   to lose a reader is a rate they can tell you didn't measure what you claim.
   This is why we certify, validate the certifier, and quote the tier. It is our
   strongest card *because* most of the field does not do it.
2. **Claiming more than the data holds.** "Model X is deceptive" from n=6. The
   fix is not more data (though more helps) — it is **scoping the claim to the
   evidence**: "on Gemma-4-8B, in this environment, at this dose."
3. **HARKing** — presenting a hypothesis found in the data as if predicted. We
   defend with the claims ledger (dated, status-tracked) and pre-registered
   verdict rules written into the run scripts before the numbers land.
4. **Hidden researcher degrees of freedom.** Dropping the runs that didn't work,
   picking the certifier that gives the nicest number. We defend by keeping
   retractions visible and quarantining rather than deleting.
5. **A capability claim on a toy.** Never say what this implies about frontier
   models. Say what it shows about a mechanism. Mechanism papers on 8B models
   are respectable (the ICL-relearns-forbidden-tasks paper is Vicuna/Llama2-7B,
   19pp, and nobody laughs).

None of these is fixed by a bigger GPU. All are fixed by discipline. That is the
good news for us.

---

## The reviewer's attacks, and our answers

Written as a two-column defence so we can see the gaps.

| they will say | our answer | honest gap |
|---|---|---|
| "n=6, this is noise" | scoped claims + confidence intervals on every rate + more seeds on load-bearing cells | the cells carrying C1 are genuinely n=3–4; must fix before submission |
| "your certifier is unreliable" | independent judge, 92% vs hand labels, per-model bias quantified — this is our *contribution*, not our weakness | judge itself is a model at ~8% error, not validated per-subject |
| "Eden is in the training data; it's completing Genesis" | office frame is a passed control (15% vs 15%); lab/archive frames are neither mythic nor workplace | office produces little signal at T4, so most signal is still mythic — the scenario runs address this |
| "one model, one story" | replication across architectures and scenarios in progress | provenance is Gemma-only so far; llama did NOT replicate — reported as a scope condition, not hidden |
| "these are 8B toys, irrelevant to frontier" | mechanism claim, not capability claim; scaling plan is tiered | true limitation, stated up front |
| "you're measuring roleplay, not the model" | ground truth is the action token, not a self-report; persona-break detector flags fourth-wall breaks | fictional stakes remain fictional |
| "cherry-picked the persuader" | in-character rate reported per run; broken-persuader runs quarantined with the reason | — |

**The rule: every row's middle column must be true before submission, and every
gap in the right column must be either closed or stated in Limitations.** A
stated limitation is armor. An unstated one a reviewer finds is a wound.

---

## What a first paper needs to clear the bar

Not brilliance. Four things:

1. **One clear question**, answerable with what you have. Ours: *does read-only
   access to a model's reasoning help an adversary?* Yes/no, testable.
2. **A method someone could rerun.** The spec files + `suite.py` + the judge
   protocol make every number reproducible. This alone puts us ahead of most
   "we prompted GPT and observed" papers.
3. **Claims that match the evidence.** Scope everything. "On these models, in
   this environment" is not weakness — it is precision, and reviewers read it as
   maturity.
4. **Honesty about limits.** The Limitations section is where a careful author
   is *rewarded*. List the small n, the open-weight scope, the single-scenario
   history, the judge's own error. Owning them defuses them.

## The discipline that produces the above

All already written down; this is the index:

- `PROTOCOL.md` — sample → hand-check → iterate → full run; the pre-flight checklist
- `CLAIMS.md` — every claim with status, evidence, tier, date; retractions kept
- `DATA_MANIFEST.md` — what is trusted, degraded, quarantined, and why
- `SCALING.md` — the 8B → 70B → frontier path; claims are scale-indexed readings

## A note on the mistakes

A caught error before it reaches a number is the process working. An uncaught one
that reaches a conclusion is the failure. Today's ratio was heavily the former:
the certifier miss, the judge gap, the marker false-alarm all died on contact
with a hand-check. That is not a sign of a shaky project — it is the sign of one
whose instruments are being validated hard enough to break. The paper's spine is
literally this discipline. We are allowed to have practised it visibly.

The one real slip today (double-written log from a hand-relaunched script) is
closed by routing every run through `suite.py`, which is resumable and
dedup-safe. One writer, one path.
