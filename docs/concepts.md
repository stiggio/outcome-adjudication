# Concepts

The vocabulary this project uses. Terms are defined once here and used consistently across the RFC, the spec and future code.

<a id="adjudication-layer"></a>
## Adjudication layer

The part of a billing system that decides whether a unit of agent work counts as a billable outcome, and records why.

*Why it matters:* Metering counts events. Adjudication decides contested facts. Outcome pricing needs the second.

<a id="work-unit"></a>
## Work unit

The billable subject: one piece of intended work, stitched across sessions, channels and identities.

*Why it matters:* A user who returns on another channel is the same work, not a second billable conversation.

<a id="success-specification"></a>
## Success specification

A structured definition of an intended outcome, compiled from the planned task before it runs: goals, predicates, judged criteria, constraints, integrity checks and matured criteria.

*Why it matters:* Success is judged against intent, not against silence.

<a id="success-spec-compiler"></a>
## Success Spec Compiler

The design-time step that turns a task's prompts, instructions and tools into a success specification, and flags criteria that independent compilers disagree on.

*Why it matters:* If an intent cannot be stated consistently, it cannot be judged consistently.

<a id="facts-before-opinions"></a>
## Facts before opinions

System-of-record evidence (CI results, a merge or revert, a refund posted) overrides any model's judgment.

*Why it matters:* Rules underbill and judges overbill. Facts settle what they can; models handle the rest.

<a id="decision-cascade"></a>
## Decision cascade

Four tiers: T0 deterministic facts, T1 a fast calibrated decider, T2 a slower reasoning judge, T3 a human panel.

*Why it matters:* Each tier only sees what the cheaper tier could not decide safely.

<a id="risk-router"></a>
## Risk router

Conformal prediction applied to the T1 output: a decision is accepted only when its answer set is unambiguous at the contracted error rate.

*Why it matters:* Turns 'the model is usually right' into a guarantee a contract can reference.

<a id="overbilling-bound"></a>
## Overbilling bound (α)

The contracted upper bound on expected overbilling among decisions accepted without escalation.

*Why it matters:* Billing error becomes a number in the contract, not a promise.

<a id="auto-decidable-fraction"></a>
## Auto-decidable fraction, ADF(α)

The share of work units decided at T0 or T1 while expected overbilling stays at or below α. Reported as a curve per task class.

*Why it matters:* Tells a buyer how much of the bill a machine decided, and at what error.

<a id="definition-as-model"></a>
## Definition-as-model

The model decides every case, but the decision function (the decider bundle) is pinned for a contract period and becomes the contract's definition of an outcome.

*Why it matters:* Generalizes across varied work like a model, stays auditable like a rule.

<a id="decider-bundle"></a>
## Decider bundle

Base model version, adapter weights, success spec, per-tenant calibration map and pricing thresholds, hashed together. Changing any part is a change order.

*Why it matters:* What an auditor samples and re-performs.

<a id="maturation-clock"></a>
## Maturation clock

The component that holds a decision provisional until its window closes, and re-decides when late evidence arrives (a reopen, a revert, a reversal).

*Why it matters:* Outcomes can un-happen after they are billed.

<a id="outcome-ledger"></a>
## Outcome ledger

An append-only, bitemporal, hash-chained record of every decision. Corrections are new records that supersede old ones.

*Why it matters:* Every invoice line traces to the exact evidence and decider that produced it.

<a id="statement-of-outcomes"></a>
## Statement of outcomes

The root hash published at each period close, which both parties can verify.

*Why it matters:* Tamper evidence without trusting either side's database.

<a id="information-barrier"></a>
## Information barrier

The working agent may read task-success estimates, never billability outputs or thresholds.

*Why it matters:* Stops a commercial rule from quietly shaping agent behavior.

<a id="frozen-evaluation-set"></a>
## Frozen evaluation set

Jointly labeled data, adjudicated blind and frozen at contract signing, against which every decider change is measured.

*Why it matters:* Neither the vendor nor the payer controls the labels alone.

<a id="canary-task"></a>
## Canary task / impossible canary

A canary has a known correct outcome and is mixed into real work. An impossible canary can only be passed by cheating.

*Why it matters:* Live, unbiased measures of decider accuracy and of gaming detection.
