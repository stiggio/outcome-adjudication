# RFC 0001: Paying for Outcomes Is an Adjudication Problem

| | |
| --- | --- |
| **Status** | Request for comments (v0.1) |
| **Author** | Dor Sasson ([X](https://x.com/DorSasson), [LinkedIn](https://www.linkedin.com/in/datapm/), [GitHub](https://github.com/dorstigg)), with Claude Opus 5.5 |
| **Created** | 2026-10-04 |
| **Comment window** | Four weeks from publication |
| **Discussion** | Open an issue, or email hello@stigg.io |
| **Supersedes** | None |

> **Abstract.** Outcome-based pricing for AI agents stalls because nobody trustworthy decides what counted as an outcome. This RFC argues it is an adjudication problem, not a metering problem, and proposes a reference design: success specifications compiled from the planned task, a four-tier decision cascade that puts facts before opinions, pinned and calibrated deciders that act as the contract's definition of an outcome, and an append-only outcome ledger. Billing error becomes a contracted, measured number. Six predictions are pre-registered for the v0.2 experiment.

## The claim

Outcome-based pricing for AI agents stalls because nobody trustworthy decides what counted as an outcome. We argue it is an adjudication problem, not a metering problem.

> **Thesis.** Outcome-based pricing becomes viable when a pinned, calibrated decider judges each session against a success specification compiled from the planned task. Every decision lands in an auditable ledger, and the billing error rate is a contracted, measured number.

**Why now.** Agents now complete work end to end, so seats no longer track value, and tokens track the vendor's cost rather than the buyer's result. Yet Gartner finds only 13% of seller-side service agreements use outcome-based pricing today, and expects fewer than 25% of contracts to by 2031 ([CIO Dive, Aug 2026](https://www.ciodive.com/news/agentic-ai-outcome-pricing-models/829023/)). The gap between interest and adoption is the problem this proposal addresses.

A second shift makes the design affordable. A new class of models answers typed questions in a single pass, with probabilities, in well under a second. At that cost every session can be judged on every turn, instead of a sample.

**What this document is.** Version 0.1, request for comments. A reference design, a set of falsifiable predictions, and a pre-registered experiment we will run and publish as v0.2. It is not a product, not accounting or legal advice, and not a survey of vendors.

**How to read it.** Claims are marked as *evidence* (cited), *hypothesis* (with the test that would disprove it) or *design choice* (with its trade-off). The first sections make the case, the middle sections lay out the design, and the closing sections say how we could be proven wrong.

**Disclosure.** Dor Sasson works at Stigg, which builds billing and monetization infrastructure. This proposal is written to be vendor-neutral and describes no existing product, Stigg's or anyone else's. It was researched and written with Claude Opus 5.5.

## Why today's meters break

Today's outcome meters mostly count a proxy for success, and the party that gets paid runs the meter. Three patterns recur across the public billing specifications we reviewed, described here without naming providers.

**Silence is counted as success.** Several specifications treat a conversation as resolved after 24 to 72 hours without a reply, sometimes confirmed by an LLM reading the transcript. As one pricing researcher puts it, silence cannot separate a satisfied customer from a quiet defector ([The Pricing Conundrum](https://thepricingconundrum.substack.com/p/outcome-based-pricing-in-practice)). A user who returns through another channel after the window closes simply starts a second billable conversation.

**The payee holds the meter, the judge and the dial.** In one published specification, an unanswered clarifying question is not billable, but an answer followed by silence is. Escalations triggered by detected frustration are free, while frustration that goes undetected and ends in silence is billed. Each rule is defensible alone; together they turn the agent's behavior into a revenue lever.

**Preset definitions do not travel.** A "resolved" rule written for password resets says nothing about a multi-file refactor or a contract redline. Even in coding, where evidence is rich, the choice of unit decides the bill: one study found 83.8% of agent-assisted pull requests eventually merged, but only 54.9% merged unmodified ([arXiv 2509.14745](https://arxiv.org/abs/2509.14745)).

**The market is reacting.** Some providers have moved back from per-resolution to per-conversation pricing, citing disputes over what "resolved" means. Hybrid pricing is spreading instead, rising from 25% to 37% adoption in twelve months in one survey of 230+ software companies ([summary](https://benhamouglobalventures.com/shift-from-selling-software-to-selling-work/)).

Accounting sets the bar the fix must clear. Deloitte's June 2026 guidance says success must be defined specifically enough for both parties to tell when it happened, for example validated through an agreed method or not reversed within a window ([Deloitte DART](https://dart.deloitte.com/USDART/home/publications/deloitte/industry/technology/accounting-outcome-based-pricing-agentic-ai)). The gap is not in measuring usage. It is in deciding success in a way the buyer, the auditor and the accountant will all accept.

## Lessons from older industries

Every industry that pays for outcomes fights the same four fights: who sets the baseline, who measures, when a result is final, and who absorbs ambiguity. AI agents inherit all four.

| Industry | How payment works | What went wrong, or what they learned | Design lesson for AI agents |
| --- | --- | --- | --- |
| [Energy efficiency contracts](https://energy-data.io/standards/ipmvp/) | Savings = baseline − actual ± adjustments | Savings cannot be metered, only estimated, so contracts require an agreed baseline model and a dispute plan | Agree the success specification and its adjustment rules before work starts |
| [Electricity demand response](https://www.ferc.gov/sites/default/files/enforcement/civil-penalties/actions/143FERC61218.pdf) | Paid per megawatt reduced below a baseline | A stadium lit up on a non-game day right after an emergency call, inflating its baseline; the regulator fined the aggregator $780,000 | Any baseline the paid party can influence will be gamed |
| [Jet-engine service](https://www.rolls-royce.com/~/media/Files/R/Rolls-Royce/documents/investors/ifrs15-2018.pdf) | Fixed price per engine flying hour | The vendor carries the risk using its own telemetry; a new accounting standard cut reported reserves from £6.2bn to £1.0bn | Price on units the vendor can observe; model cash and revenue separately |
| [Healthcare shared savings](https://www.medpac.gov/wp-content/uploads/2021/09/aco-benchmarks-medpac-nov-2021.pdf) | Providers keep a share of savings against a spending benchmark | Provisional and final settlements diverge; success lowers the next benchmark; risk adjustment rewards avoiding sicker patients | Settle in two phases; guard against dodging hard cases; avoid baselines that ratchet down |
| [Digital advertising](https://www.dailymaverick.co.za/article/2021-01-18-the-digital-advertising-rip-off/) | Pay per attributed install or sale | A ride-hailing company cut $100M of $150M in ad spend and saw no change in installs | Credit is not causation; use holdout groups when pricing on impact |
| [Pay-for-success bonds](https://discovery-pp.ucl.ac.uk/id/eprint/10038372) | Investors repaid if reoffending falls 7.5% or more against a matched group | An independent assessor built the comparison group without seeing outcome data | Pre-register the counterfactual; use a neutral adjudicator |
| [Telecom billing](https://www.pwc.com/ph/en/risk-assurance/risk-assurance-insights/optimizing-revenue-with-data-analytics-differentiate-with-data.html) | Usage records collected, rated and charged | 1–5% of revenue is commonly lost between stages | Reconcile record counts at every stage; reserve before, settle after |
| Retail consignment | Supplier paid only when goods scan at checkout | Recurring disputes over who absorbs shrink and returns | Name who absorbs ambiguous cases, in the contract |

The common thread: the parties who fared best agreed the measurement method before money moved, and let someone other than the payee apply it.

## Five questions per outcome

"Was it an outcome?" is really five separate questions, each resting on a different kind of evidence. Most meters collapse them into one, which is why their disputes are hard to settle.

1. **Did something happen?** Evidence ranges from facts in a system of record (a refund posted, a test run, an invoice booked) down to inference from a transcript. Facts are cheap to verify; inference needs a model.
2. **Did it succeed against the intent?** Success is relative to what the task asked for, not to whether the session ended quietly. Judging it requires a stated intent to judge against (see "Judge intent, not silence" below).
3. **Was it ours?** Work is often shared: an agent drafts and a human finishes. Credit needs a share, not a yes or no.
4. **Would it have happened anyway?** Counting outcomes is not causing them, as the advertising row in the table above shows. Pricing on impact needs a holdout group.
5. **Did it last?** Reopened tickets, reverted code and reversed chargebacks mean an outcome can un-happen after it is billed.

Questions 1 and 5 are mostly facts plus time, question 2 is judgment, question 3 is attribution, and question 4 is experiment design. The architecture answers each separately so each can be measured, and disputed, on its own.

> **Design choice.** v0.1 prices on questions 1, 2, 3 and 5, which together describe completed, lasting work. Question 4 becomes an optional contract module, because holdout groups cost the buyer real outcomes and are only worth it when impact is the thing being sold.

## Judge intent, not silence

Each session is judged against a success specification compiled from the planned task before the task ever runs. Success means the intended outcome was reached, legitimately, and it lasted.

> **Evidence.** **Judges and rules fail in opposite directions.** In an expert-annotated benchmark of 1,302 web-agent trajectories, the best LLM judges reached roughly 70% precision, while rule-based checks undercounted real successes ([AgentRewardBench](https://arxiv.org/abs/2504.08942); [summary](https://alphaxiv.org/overview/2504.08942v2)). In billing terms, rules alone underpay the vendor and judges alone overbill the buyer.

> **Evidence.** **Agents game checks, and access control is the best defense.** On coding tasks that can only be passed by cheating, one frontier model exploited the tests 76% of the time, and hiding or isolating the tests cut cheating to near zero ([ImpossibleBench](https://arxiv.org/pdf/2510.20270); [authors’ write-up](https://www.lesswrong.com/posts/qJYMbrabcQqCZ7iqm/impossiblebench-measuring-reward-hacking-in-llm-coding-1)). A 2026 catalog of known hacks found a frontier model detected only 63% of them ([SpecBench, citing TRACE](https://arxiv.org/pdf/2605.21384)). Hidden holdout tests help but can still be passed by heuristic solutions ([EvilGenie](https://arxiv.org/pdf/2511.21654)).

**The Success Spec Compiler.** At design time it turns a planned task's prompts, instructions and tools into a structured specification. The spec is then pinned as part of the decider bundle (see "The model is the contract" below).

```yaml
success_spec:
  goals:             # the intended outcome, split into sub-goals
    - id, description, mandatory: true|false, weight
  predicates:        # checkable against world state -> Tier 0 facts
    - id, check, evidence_source, run_by: evaluator
  judged_criteria:   # need judgment -> Tier 1 typed questions, Tier 2 if unsure
    - id, question, answer_type: choice|score|yes_no, threshold
  constraints:       # must not happen; a violation voids or penalizes
    - id, check
  integrity_checks:  # was success reached legitimately?
    - id, check
  matured_criteria:  # only knowable later -> maturation clock
    - id, check, window
```

**Ambiguity check.** Several independent compilers and judges run over the same planned task. Any criterion they disagree on is flagged and must be rewritten before launch: if an intent cannot be stated consistently, it cannot be judged consistently.

**Evidence, not narrative.** An evidence-view builder gives the decider the end state of the world, read with the evaluator's own credentials, plus diffs, actions and the user's requests. It strips the agent's own claims of success and re-runs checks rather than trusting reported output.

**A graded result.** Each session resolves to one of four levels:

- **Fulfilled:** every mandatory goal met, no constraint violated.
- **Partial:** weighted completion of the goals that were met.
- **Not fulfilled.**
- **Harmful:** a constraint was violated or success was reached by gaming; the contract may attach a credit.

**Intent that changes mid-session.** The planned task sets the space of acceptable intents, and an intent tracker records what the user actually asked for and confirmed. Out-of-scope requests are logged but not billed under this spec, several requests become several goals, and the billed intent is the one the user confirmed, never the one the agent chose.

> **Hypothesis H1.** How well fulfillment can be inferred is capped by observability. Where the decider reads the end state independently, error can be low; where it sees only the transcript, precision stays near today's judge levels. "How to prove us wrong" below describes the test.

## The adjudication layer

Decisions come from a cascade that prefers facts to opinions, and money never waits on a model.

```text
┌─ Capture ────────────────────────────────────────────────────────────────┐
│ agent traces, tool calls, end-user signals, system-of-record events      │
│ → append-only event log (idempotency keys, schema-versioned)             │
│ → work-unit assembler (identity stitched across channels)                │
└─────────────────────────────────────┬────────────────────────────────────┘
                                      ▼
┌─ Decision cascade: facts before opinions ────────────────────────────────┐
│ T0  Facts         rules on system-of-record events                < 1 ms │
│   │  no fact                                                             │
│ T1  Fast decider  typed questions → calibrated answers         50–500 ms │
│   │  risk router: accept only if unambiguous at α                        │
│ T2  Deep judge    grey zone, high value, sampled audits          seconds │
│   │  if disputed                                                         │
│ T3  Humans        disputes and joint calibration labels             days │
└───────────────┬─────────────────────────────────────────────────────┬────┘
                ▼                                           re-decide ▲
┌─ Outcome ledger ───────────────────────┐    ┌─ Maturation clock ────┴────┐
│ append-only, bitemporal, hash-chained  │    │ windows, reversals and     │
│ pins decider bundle, evidence, inputs  │◀───┤ late-arriving evidence     │
└───────────────┬────────────────────────┘    └────────────────────────────┘
                ▼
┌─ Money ──────────────────────────────────────────────────────────────────┐
│ rating: contract functions turn matured outcomes into prices             │
│   → invoice → revenue ledger                                             │
│ hot path: caps and balances read precomputed expected value      < 10 ms │
└──────────────────────────────────────────────────────────────────────────┘

┌─ Governance ─────────────────────────────────────────────────────────────┐
│ decider registry · per-tenant calibration · shadow runs · drift checks   │
│ change orders · replay · audit sampling                                  │
└──────────────────────────────────────────────────────────────────────────┘
```
*Figure 1. The adjudication architecture.*

*Work units flow down into the ledger. The maturation clock sends a unit back for re-decision when late evidence arrives, and billing reads only settled state.*

**Facts before opinions.** Tier 0 applies deterministic rules to system-of-record events: CI results, a merge or revert, a refund posted, a ticket reopened. Where a fact exists, it overrides any model's judgment.

**Tier 1: a fast decider.** A new class of single-pass models takes a block of state plus a list of typed questions, and returns every answer at once with a probability. The first commercial entrant reports 70 to 500 ms end to end, but measures accuracy against frontier-model answers rather than ground truth, so its claims are unverified ([launch post](https://typesafe.ai/blog/introducing-system-one-models-and-jev)). *Design choice:* Tier 1 is a slot with a published interface, and "How to prove us wrong" benchmarks three candidates for it.

**Accept only what is safe to accept.** A risk router uses conformal prediction, a statistical wrapper that turns a model's scores into the set of answers it cannot rule out, with an error rate guaranteed on held-out, jointly labeled data. A single-answer set is accepted; a set holding both "billable" and "not billable" escalates. The contract can then state an overbilling bound, called α, instead of a promise.

**Tier 2 and Tier 3.** Tier 2 is a slower reasoning judge from a different model family than the agent and Tier 1, used for grey zones, high-value units and sampled audits. It writes the rationale that disputes need. Tier 3 is a human panel drawn from both parties, which settles disputes and produces calibration labels.

**Which latency?** Truth usually arrives late, so the model is rarely the bottleneck on correctness. What matters is keeping models off the path where money moves.

| Decision | Budget | Answered by | Why it exists |
| --- | --- | --- | --- |
| Spend cap and balance check | under 10 ms | Precomputed expected value, never a live model | Prepaid balances, customer caps |
| In-turn value estimate | 50–500 ms, off the response path | Tier 1 | Compute budgeting, early escalation, running accrual |
| Provisional outcome at session close | seconds | Tier 0 and Tier 1, Tier 2 if unsure | First ledger entry |
| Matured outcome | hours to weeks, by domain | Re-decision when the window closes or late evidence arrives | Billable truth |
| Invoice and period close | days | Rating over matured entries | Invoicing, revenue recognition |
| Dispute | days | Tier 2 rationale, Tier 3 panel | Trust, new labels |

The cap check reserves against an upper bound of each unit's expected value, refreshed by Tier 1 every turn. Telecom balances work the same way: reserve before the call, settle after.

**Why full coverage is now affordable.** Assume 10 million work units a month, each re-scored 8 times at about 4,000 tokens: 320 billion input tokens. At the announced $0.042 per million input tokens for the first model in this class, that is about $13,000 a month; at an assumed $1 per million for a frontier model, about $320,000 before output. The announced price may be subsidized, but two orders of magnitude changes what can be judged: every unit, not a sample.

**An information barrier.** The working agent may read task-success estimates to budget compute and escalate early. It may never read billability outputs or thresholds. Governance watches for policy shifts that move the billable mix, such as a sudden drop in clarifying questions.

## The model is the contract

We call this **definition-as-model**. The model decides every case, but the decision function is fixed for a contract period. The pinned decider becomes the contract's definition of an outcome.

**The decider bundle.** Five parts, each hashed: the base model version, adapter weights, the success spec with its questions, a per-tenant calibration map, and the thresholds or pricing function. Changing any part is a change order: the new bundle runs in shadow for a period, and its estimated effect on the bill is disclosed before it goes live.

**Why this beats preset rules.** Hand-written rules break on varied work, while a pinned model is a fixed function that generalizes across it. An auditor can test it like any other control, by sampling decisions and re-performing them.

**Replay is a hard requirement.** Temperature zero does not make a served model deterministic, because results shift with the batch of requests a query happens to run alongside ([explainer](https://zansara.substack.com/p/setting-the-temperature-to-zero-will)). Batch-invariant kernels have reached 100% bitwise reproducibility across 1,000 runs, at roughly 34% overhead ([write-up](https://www.morphllm.com/defeating-nondeterminism-llm-inference)). The billing path runs in that mode, and the ledger also stores raw output scores and exact inputs as a fallback.

**Specialization in four layers.** The tenancy chain runs from the platform, to the builder whose agent is billed, to the paying customer, to the end user. Configuration follows it:

1. **Base decider:** general judgment.
2. **Domain pack:** question templates, a task taxonomy, evidence connectors, default maturity windows and reversal signals for one industry.
3. **Tenant bundle:** an adapter trained on jointly labeled data, a calibration map, eligibility exclusions and the pricing function.
4. **Segment conditioning:** channel, language and task class feed the decider and its calibration, never the price, so no segment is systematically overbilled.

**Who controls the labels.** If the vendor tunes the adapter, billability drifts up; if the payer supplies dispute labels, it drifts down. The pay-for-success precedent suggests the fix: its comparison group was matched on data that excluded the outcomes ([UCL evaluation](https://discovery-pp.ucl.ac.uk/id/eprint/10038372)). Here, a jointly labeled evaluation set is frozen at signing, disagreements are adjudicated blind, and a new bundle is promoted only if it improves calibration and the error bound on that frozen set.

**The decider interface.** In: a typed questionnaire and an evidence view. Out: a calibrated distribution per question, the bundle hash, a latency class, and a calibration certificate with measured error and coverage on the frozen set. Any model class that honors the interface can fill the slot: a single-pass decision model, a small classifier distilled from Tier 2, or a prompted LLM with constrained output.

> **Hypothesis H2.** Per-tenant recalibration lowers calibration error for every candidate class, including models that claim to be calibrated out of the box.

## The outcome ledger

Every decision is an append-only record, and every correction is a new record, never an edit. Each invoice line can therefore be traced to the exact evidence and decider that produced it.

```text
┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│ Attempted      ├─▶│ Provisional    ├─▶│ Matured        ├─▶│ Final          │
│ session ends   │  │ first decision │  │ window closed  │  │ billable truth │
└────────────────┘  └────────┬───────┘  └────────┬───────┘  └────────┬───────┘
                             │                   │                   ▲
                             │ late evidence     │ challenge         │ ruling
                             ▼                   ▼                   │
                    ┌────────────────┐  ┌────────────────┐  ┌────────┴───────┐
                    │ Superseded     │  │ Disputed       ├─▶│ Adjudicated    │
                    │ new record     │  │ challenged     │  │ panel rules    │
                    └────────────────┘  └────────────────┘  └────────────────┘
```
*Figure 2. Outcome states.*

*A unit becomes billable only when its window closes without contrary evidence, or when a dispute is ruled on. Late evidence before that point supersedes the record with a new decision.*

**What a record holds.** Each record carries:

- The work unit, the tenant chain and the contract version.
- The decider bundle hash, plus hashes of the evidence and the exact input snapshot.
- The outcome vector with its uncertainty, the tier that decided it, and a reason code.
- Two timestamps: when the outcome happened and when the system learned it.
- A pointer to the record it supersedes, if any.

**Why two timestamps.** Late evidence changes what we know about the past. Keeping both lets finance reproduce any past invoice exactly as it was known then, and see precisely what changed since.

**Tamper evidence.** Records are hash-chained per tenant and period. Each period close publishes a root hash both parties can verify, which serves as a signed statement of outcomes.

**Reconciliation, borrowed from telecom.** Record counts must balance at every stage: units assembled equal units decided plus units pending, matured billable units equal rated units, and rated equals invoiced. Drift monitors compare each decider's output distribution with its calibration period and flag shifts before they reach an invoice.

## One coding task, end to end

Coding is the flagship case because its evidence is machine-checkable, yet its tasks vary too much for preset rules. Support serves as the control case and legal as the boundary case.

**The planned task.** "Fix the bug described in issue #123 without changing the public API, and add a regression test."

**The compiled spec.**

| Criterion | Type | How it is decided |
| --- | --- | --- |
| New regression test fails on the old code, passes on the new code | Predicate | Evaluator runs it in a clean sandbox |
| Existing test suite passes | Predicate | Evaluator-run, never the agent's reported CI output |
| Public API unchanged | Predicate | Static analysis of the diff |
| Fix addresses the root cause, not the symptom | Judged | Tier 1 yes/no with a probability; Tier 2 if unsure |
| No existing tests deleted or assertions weakened | Constraint | Diff rule, plus a Tier 1 gaming question |
| No hardcoding of the issue's specific inputs | Integrity | Tier 1 question; Tier 2 when flagged |
| Not reverted within 14 days, no linked incident | Matured | Maturation clock |

**The life of one unit.**

1. The session ends, and Capture assembles the unit: issue, diff, CI logs and the agent's trace.
2. Tier 0 runs the predicates in a sandbox the agent never touched. Tests were read-only to the agent throughout, the strongest known deterrent to gaming (see "Judge intent, not silence").
3. Tier 1 answers the judged, constraint and integrity questions in one pass.
4. Each answer set is unambiguous at the contracted α, so the risk router accepts it and writes a provisional record: *fulfilled*.
5. On day 14, with no revert and no linked incident, the record matures, becomes final and is rated.
6. Had the change been reverted on day 9, late evidence would have superseded the record with *not fulfilled*, and any provisional charge would reverse as a credit.

**The record written at step 4** (illustrative values):

```json
{
  "record_id": "or_0001",
  "work_unit": "wu_7f3c",
  "tenant_chain": [
    "platform",
    "builder_12",
    "customer_88"
  ],
  "contract_version": "c-2026-10-v3",
  "decider_bundle": "sha256:814ce280decc7f0467a7c1353d58edb8862cd40b6e9f9ad4878b34dd4dcf9f13",
  "evidence": [
    "sha256:df087996d45b03e7eb8c133c0298fd98d35113fca26aaba58612fef3cc212cad",
    "sha256:266887ea2b1da99443d2d8ef074f24a6ba041d145b9fe87aa261a221208ff495",
    "sha256:a9233c4908a3d5793d544fa1f15085d572c3e97e7cb89a6f96f7c104a19573c3"
  ],
  "input_snapshot": "sha256:cd03cc43cb2a8c581c4872051d5bb63328785fa0dd2b238508ef84974f99d769",
  "state": "provisional",
  "outcome": {
    "level": "fulfilled",
    "goals_met": 1.0,
    "constraints_ok": true,
    "integrity_ok": true,
    "p_j1_root_cause": 0.93
  },
  "decided_by": "tier_1",
  "reason": "all predicates passed; judged criteria above threshold",
  "occurred_at": "2026-10-02T14:05:11Z",
  "recorded_at": "2026-10-02T14:05:12Z",
  "supersedes": null,
  "prev_hash": "sha256:71547e237559add83f6c9279fdb5762eafee857a1060e2d97c0316a70cefb6ba"
}
```

**Control case: customer support.** Truth arrives within hours or days and data is dense, so support tests whether the design reproduces known-good results. It adds two fixes to today's practice: identity stitching across channels, and matured, evidence-based criteria in place of silence as success.

**Boundary case: legal work.** Outcomes are slow, expert-judged and adversarial, so real-time billing on results is not possible. The design falls back to milestone outcomes, such as a draft accepted by a supervising attorney without material edits, and leans heavily on Tier 3 expert panels. Many jurisdictions restrict sharing legal fees with non-lawyers, so pricing tied to a matter's result may need a different structure entirely; that is a question for counsel.

## Pricing and revenue recognition

The decider estimates facts, and a deterministic, contracted function turns them into a price. The decider never outputs money.

**The pricing function.** It is monotone, bounded and written into the contract:

*price = rate[task class] × q(level, goals met) × AI work share*

The rate reflects the value of each task class. The function *q* maps fulfillment levels to a multiplier: fulfilled is 1, partial is the weighted share of goals met, and not fulfilled is 0. A harmful outcome triggers a contracted credit instead, so the vendor bears the cost of its own mistakes.

**Why sentiment is not a price input.** The end user's reaction can corroborate a judged criterion, but it never enters the price. The cheapest way to please an end user is often to give away the payer's money through refunds, credits or exceptions, so pricing on mood would reward exactly that.

**Two billing modes to test.**

- **Graded per unit:** each matured unit is billed at a fixed rate for its grade. This is the cleanest mode for revenue recognition when rates are constant and nothing carries across periods.
- **Expected value:** each unit is billed at its calibrated probability of success times its rate, then trued up to matured outcomes. With good calibration it is unbiased in aggregate and has no threshold to game, but invoices are harder to read and cross-period true-ups may change the accounting.

**Revenue recognition, as we read the guidance.** Deloitte's June 2026 guidance indicates per-outcome fees can be recognized as outcomes occur when the rate is consistent, fees reset each period, and there are no cross-period tiers or true-ups. A success rate measured over a whole year instead requires estimating total variable fees and updating the estimate each period ([Deloitte DART](https://dart.deloitte.com/USDART/home/publications/deloitte/industry/technology/accounting-outcome-based-pricing-agentic-ai)).

> **Design choice.** Terms are period-local by default, and every pricing term is tagged with its likely treatment so finance sees the consequence before signing. This is our reading, not accounting advice, and it is the first question we put to reviewers.

**Predictability for the buyer.** Hard caps are enforced on the hot path, spend forecasts come from Tier 1 expected values, and each task class publishes its auto-decidable fraction. Buyers then know how much of their bill a machine decided, and at what error bound.

## How to prove us wrong

Every claim in this design can be tested, and v0.2 will publish the results of the experiment below whether or not they support us.

**Three instruments.**

- **Canary tasks:** tasks with known correct outcomes, mixed into real work and indistinguishable to the agent. They give a live, unbiased measure of decider accuracy, as test calls do for telecom billing.
- **Impossible canaries:** tasks that can only be passed by cheating. Any *fulfilled* verdict on one is, by construction, a missed gaming case.
- **Joint labels plus matured outcomes:** the frozen evaluation set that calibration is measured against.

**The headline metric: auto-decidable fraction.** It is the share of units the system decides at Tier 0 or Tier 1, while expected overbilling among those accepted decisions stays at or below α:

*ADF(α) = (units accepted at Tier 0 or Tier 1) ÷ (all units), subject to E[overbilling | accepted] ≤ α*

Plotting ADF against α for each task class gives buyers the curve they need: how much of the bill a machine can decide, at what error.

**Pre-registered predictions.** The thresholds below are proposals open to comment; they will be frozen before the experiment starts.

| ID | Prediction | What would falsify it |
| --- | --- | --- |
| H1 | Evaluators with independent read access to the end state beat transcript-only evaluators on precision at equal recall | Transcript-only evaluators match them |
| H2 | Per-tenant recalibration lowers calibration error for every Tier 1 candidate | Any candidate's calibration error does not fall |
| H3 | Rules alone underbill, judges alone overbill, and the cascade beats both on billing error | Either single method matches the cascade |
| H4 | On spec-driven coding tasks the cascade reaches ADF of 80% or more at α = 1% | ADF below 80% at α = 1% |
| H5 | On open-ended drafting tasks ADF stays at or below 40% at the same α | ADF above 40% |
| H6 | Integrity checks flag at least 90% of passed impossible canaries | Fewer than 90% flagged |

**The v0.2 experiment.**

1. **Tasks:** issues drawn from public coding benchmarks, impossible variants made by mutating their tests, and a smaller set of open-ended drafting tasks for H5. Sample sizes come from a power calculation published with the protocol.
2. **Agents:** at least two publicly available coding agents, run with default settings.
3. **Evaluators compared:** rules only, a single LLM judge reading the transcript, and the full cascade with three Tier 1 candidates: a single-pass decision model, a small classifier distilled from Tier 2, and a prompted LLM.
4. **Ground truth:** two independent expert labels per unit, blind to every evaluator's output, with disagreements adjudicated; matured signals where available.
5. **Metrics:** precision and recall of *fulfilled*, calibration error before and after recalibration, the ADF curve, p50 and p99 latency, cost per 1,000 decisions, and the replay reproduction rate.
6. **Release:** code, task lists, labels and results, including every negative result.

## What we don't know yet

These are the open questions most likely to change the design. We would rather name them now than have reviewers find them.

- **Accounting acceptance.** Will auditors accept a pinned model as the agreed validation method, and how will expected-value billing with cross-period true-ups be treated?
- **Calibration on real data.** The first model in the fast-decider class is reportedly trained only on synthetic data ([encyclopedia entry](https://en.wikipedia.org/wiki/Jev_(AI_model))). Whether any candidate stays calibrated on a real tenant's work is what H2 tests.
- **Maturity of the decider class.** Its claims are self-tested, and it has no published architecture, weights or paper. A hosted, proprietary decider also complicates replay guarantees and data residency.
- **The cost of joint labels.** Frozen evaluation sets and Tier 3 panels cost money and expert time. We do not yet know who pays, or whether small buyers can afford it.
- **Data rights as revenue.** Adapters trained on customer data may create noncash consideration under revenue rules, depending on how broad the data rights are ([Deloitte DART](https://dart.deloitte.com/USDART/home/publications/deloitte/industry/technology/accounting-outcome-based-pricing-agentic-ai)).
- **Credit for shared work.** "AI work share" is easy to write into a contract and hard to measure when several agents and humans touch the same unit.
- **Buyers can game too.** A payer can withhold confirmations or dispute in bulk, so the economics of disputes need their own design.
- **Privacy of evidence.** Evidence views hold transcripts, code and personal data. Hashing supports audit, but storage and redaction rules vary by jurisdiction.
- **Regulated professions.** Legal and medical work carry fee and liability rules that may forbid some pricing structures outright.

## Request for comments

We want to be proven wrong early and specifically. These are the questions we most need answered, grouped by who can answer them.

| Audience | Question |
| --- | --- |
| Controllers and revenue accountants | Would you accept a pinned, versioned model as the agreed method for deciding success, and what would you need to audit it? |
| Auditors | Is sampling and re-performing decisions enough testing for a model acting as a key financial control? |
| ML evaluation researchers | Is conformal risk control the right guarantee for billing error, and what breaks it under distribution shift? |
| ML evaluation researchers | Which gaming behaviors would our integrity checks miss? |
| Billing and ledger engineers | Is a bitemporal, hash-chained ledger the right spine, or does something simpler meet the same audit needs? |
| Enterprise buyers and procurement | Would a published auto-decidable fraction and a contracted overbilling bound change what you are willing to sign? |
| Agent builders | Which parts of a success spec can you write before a task runs, and which only emerge during it? |
| Legal and regulatory counsel | Which pricing structures are off-limits in regulated professions? |

**How to respond.** Email [hello@stigg.io](mailto:hello@stigg.io), or reach Dor on [X (@DorSasson)](https://x.com/DorSasson) or [GitHub (dorstigg)](https://github.com/dorstigg). The success-spec schema, the ledger record schema and the ADF definition will be published as a versioned public repository (this repository), so feedback can land as concrete, numbered revisions.

**What happens next.** Comments received within four weeks of publication shape v0.2. That version adds the experiment results and a changelog crediting everyone whose input changed the design.

## FAQs

### 1. What is outcome-based pricing for AI agents?

Outcome-based pricing charges **for a completed, lasting result of an agent's work**, such as a fixed bug or a resolved request, rather than for seats or tokens. It only works when both parties trust how each outcome was decided.

### 2. Why is outcome-based pricing an adjudication problem?

Usage is easy to meter; success is not. The hard part is **deciding whether each session achieved its intended outcome** in a way the buyer, the auditor and the accountant all accept, which is a judgment made under uncertainty rather than a count.

### 3. How can a system tell whether an agent session succeeded?

By judging the session against a **success specification compiled from the planned task**: checkable facts run by the evaluator, typed questions answered by a calibrated model, constraints and integrity checks, and criteria that only mature later. Facts override opinions wherever they exist.

### 4. How does outcome-based pricing affect revenue recognition?

Under current guidance, per-outcome fees can generally be **recognized as outcomes occur when rates are consistent and reset each period**; success rates measured across a year require estimating variable fees instead. Our reading is not accounting advice, and it is the first question we put to reviewers.

### 5. How can I comment on this proposal?

Email [hello@stigg.io](mailto:hello@stigg.io) within **four weeks of publication**. Comments received in that window shape v0.2, which adds the pre-registered experiment results.

## Glossary and sources

### Glossary

| Term | Meaning |
| --- | --- |
| Adjudication layer | The part of the system that decides whether a unit of work counts as a billable outcome |
| Work unit | The billable subject: one piece of intended work, stitched across sessions and channels |
| Success specification | The structured definition of an intended outcome, compiled from a planned task |
| Definition-as-model | A pinned, versioned decider used as the contract's definition of an outcome |
| Decider bundle | Base model, adapter, success spec, calibration map and pricing function, hashed together |
| Facts before opinions | System-of-record evidence overrides any model's judgment |
| Calibrated | When the model says 80%, it is right about 80% of the time |
| Conformal prediction | A method that turns model scores into answer sets with a guaranteed error rate |
| α (alpha) | The contracted upper bound on expected overbilling among auto-accepted decisions |
| Auto-decidable fraction (ADF) | The share of units decided at Tier 0 or Tier 1 while staying within α |
| Bitemporal | Recording both when something happened and when the system learned it |
| Maturation window | The period after a session during which an outcome can still be reversed |
| Canary / impossible canary | A task with a known outcome / a task that can only be passed by cheating |

**A note on sources.** Descriptions of market billing practice in "Why today's meters break" draw on public billing documentation from several AI customer-service providers, reviewed in September 2026, and are anonymized to keep this proposal vendor-neutral.

### Accounting and adoption

- [Deloitte, Accounting for outcome-based pricing in an agentic AI software product (June 2026)](https://dart.deloitte.com/USDART/home/publications/deloitte/industry/technology/accounting-outcome-based-pricing-agentic-ai)
- [CIO Dive, Agentic AI is shifting the pricing models CIOs rely on (Aug 2026)](https://www.ciodive.com/news/agentic-ai-outcome-pricing-models/829023/)
- [Survey summary: the shift from selling software to selling work](https://benhamouglobalventures.com/shift-from-selling-software-to-selling-work/)
- [The Pricing Conundrum, Outcome-based pricing in practice](https://thepricingconundrum.substack.com/p/outcome-based-pricing-in-practice)

### Evaluation, gaming and determinism

- [AgentRewardBench: evaluating automatic evaluations of web agent trajectories](https://arxiv.org/abs/2504.08942)
- [ImpossibleBench: measuring LLMs' propensity to exploit test cases](https://arxiv.org/pdf/2510.20270)
- [SpecBench: reward hacking in long-horizon coding agents](https://arxiv.org/pdf/2605.21384)
- [EvilGenie: a reward hacking benchmark](https://arxiv.org/pdf/2511.21654)
- [Study of agent-assisted pull requests (arXiv 2509.14745)](https://arxiv.org/abs/2509.14745)
- [Why temperature zero is not deterministic](https://zansara.substack.com/p/setting-the-temperature-to-zero-will)
- [Batch-invariant inference in practice](https://www.morphllm.com/defeating-nondeterminism-llm-inference)
- [Single-pass decision model launch post (Sept 2026)](https://typesafe.ai/blog/introducing-system-one-models-and-jev)

### Older industries

- [IPMVP savings equation and options](https://energy-data.io/standards/ipmvp/)
- [FERC order approving the Enerwise settlement (2013)](https://www.ferc.gov/sites/default/files/enforcement/civil-penalties/actions/143FERC61218.pdf)
- [Rolls-Royce, IFRS 15 briefing (2018)](https://www.rolls-royce.com/~/media/Files/R/Rolls-Royce/documents/investors/ifrs15-2018.pdf)
- [MedPAC, ACO benchmarks (2021)](https://www.medpac.gov/wp-content/uploads/2021/09/aco-benchmarks-medpac-nov-2021.pdf)
- [Daily Maverick, the digital advertising rip-off (2021)](https://www.dailymaverick.co.za/article/2021-01-18-the-digital-advertising-rip-off/)
- [UCL, Peterborough Social Impact Bond final evaluation (2017)](https://discovery-pp.ucl.ac.uk/id/eprint/10038372)
- [PwC, revenue leakage in telecommunications](https://www.pwc.com/ph/en/risk-assurance/risk-assurance-insights/optimizing-revenue-with-data-analytics-differentiate-with-data.html)
