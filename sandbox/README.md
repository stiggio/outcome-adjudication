# Sandbox

**Status: Prototype.** An exploratory, runnable version of the RFC 0001 design, built to make the ideas tangible and to find where they break. It is not the reference implementation planned in `packages/` and `bench/`, and nothing here is a benchmark result.

Every command prints what it receives, what it sends to a model, what comes back, how the router reads it, and the exact ledger record it writes. The point is to watch the design work, step by step.

Two tools:

| Tool | Question it answers |
| --- | --- |
| `probe.py` | Does the fast decider give the right answer, and the same answer every time? When it is unsure, does enrichment make it sure? |
| `oa.py` | What happens to one unit of agent work from session close to a line on a payment request, through disputes, maturation and late evidence? |

## Setup

Python 3.9 or later, from the repository root:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r sandbox/requirements.txt
python -m pytest sandbox/tests          # offline, no keys needed
```

Deciders need credentials:

| Decider | Used for | Needs |
| --- | --- | --- |
| `jev` | Tier 1 (default), all probes | `export TYPESAFE_API_KEY=...` (TypeSafe console) |
| `claude-haiku`, `claude-sonnet`, `claude-opus` | Tier 2 (default `claude-sonnet`), or Tier 1 for comparison | The [Claude Code](https://claude.com/claude-code) CLI on your PATH, logged in |

All output goes to `sandbox/out/`, which is not committed.

## Where each RFC concept lives

| RFC concept | In the sandbox |
| --- | --- |
| Success specification | `cases/legal-nda/spec.yaml`, validated against `spec/success-spec.schema.json` |
| Tier 0, facts before opinions | `t0()` in `cases/legal-nda/case.py`: plain code, no model |
| Tier 1, fast decider | `deciders.py`, `Jev`: all typed questions in one call, a probability per question |
| Risk router | `oa.py`, `decide()`: a fixed [certainty band](../docs/concepts.md#certainty-band), not yet conformal |
| Tier 2, deep judge | `deciders.py`, `Claude`: asked only the questions Tier 1 was unsure about |
| Tier 3, human panel | `oa.py rule`: you type the ruling |
| Graded result | `oa.py`, `outcome_of()`: fulfilled, partial, not fulfilled, harmful |
| Decider bundle | `oa.py`, `bundle_hash()`: spec, both deciders, band and prices, hashed |
| Outcome ledger | `ledger.py`: append-only, per-customer per-month hash chains, content-addressed evidence |
| Maturation clock | `oa.py mature` and `oa.py event` |
| Pricing function | `oa.py`, `price()`: rate × q(level, goals met) × AI work share, or a credit if harmful |
| Statement of outcomes | the `ledger_roots` field on every payment request |
| Replay | `oa.py replay`: re-asks Tier 1 on the stored input snapshot |
| Canary task | a [probe](../docs/concepts.md#probe) in `probes/nda.yaml` |

## Walkthrough A: probes

A probe is one piece of evidence, one yes/no question and the answer known to be right. The decider returns `p`, the probability that the answer is yes.

```bash
python sandbox/probe.py sandbox/probes/nda.yaml --only waiver-indirect,clean
```

For each probe the output shows, in order:

1. **The probe:** the question, the expected answer and why, and the evidence given to the decider.
2. **STEP plain:** the exact request body, then every response verbatim. Each `p` is classified against the band in the probe file (`band: {no_max: 0.10, yes_min: 0.90}`): at or below 0.10 is a certain NO, at or above 0.90 a certain YES, anything between is UNCERTAIN.
3. **SPREAD:** all repeats plotted on a 0 to 1 line, with the band edges marked `|`. A wide spread means the same request gets different answers.
4. **LADDER:** if the step was uncertain, the next [enrichment](../docs/concepts.md#enrichment-ladder) step runs, again with its full request:
   - `+criteria` adds the decider's own `true` / `false` definitions to the question,
   - `+focus` replaces the evidence with only the relevant excerpt,
   - `decompose` asks atomic sub-questions and combines them in code (`all` takes the minimum, `any` the maximum).

   It stops at the first certain answer.
5. **RESULT** grades the decider's answer against the known answer. It does not say whether to bill:
   - **PASS:** certain and correct. In production the router would accept it, and the price would be computed from a correct fact.
   - **WRONG:** certain but incorrect. In production the router would still accept it, because it has no known answer to check against, so the price would be computed from a wrong fact with no human or Tier 2 ever looking. This is the dangerous case.
   - **UNRESOLVED:** still uncertain. In production it would escalate to Tier 2 or a human: slower, but the bill is not at risk.

   What a correct answer does to the price depends on the question. A correct YES to "is the clause substantive?" helps the vendor get paid. A correct YES to "does it waive injunctive relief?" makes the draft harmful, and the vendor owes a credit.

A summary table closes the run, and `sandbox/out/probes/` gets an HTML report with every request, plus the raw results as JSON.

Example output, trimmed. Your numbers will differ:

```text
PROBE waiver-indirect
   expected     : YES   because: 'Exclusive remedy' of money damages excludes injunctions without using the word.
   ┌─ STEP plain: the question as written in the probe file, no enrichment
      RESPONSE #1 (784 ms): {"model":"jev-1.13.0","answers":{"q":{"type":"noul","noul":0.83}},...}
      SPREAD   0 ·····|····································●··|····· 1   min 0.83  max 0.84
      VERDICT  UNCERTAIN: all 2 repeats agree
   LADDER   plain was UNCERTAIN -> climb to next enrichment
   ┌─ STEP +criteria: same evidence, question now carries Jev's true/false definitions
      SPREAD   0 ·····|·······································|●●··· 1   min 0.93  max 0.94
      VERDICT  YES: all 2 repeats agree
   RESULT   ✅ PASS: expected YES, got YES at step +criteria
```

Options: `--only id,id` runs some probes, `--repeats N` overrides the repeat count.

### Probes and the overbilling bound α

α is the RFC's [overbilling bound](../docs/concepts.md#overbilling-bound): a number in the contract that caps how often the machine may overcharge without a human checking. In the words of `spec/metrics.md`, it is the upper bound on expected overbilling among decisions accepted without escalation. With α = 1%, of every 1,000 units billed automatically (decided at Tier 0 or Tier 1), at most about 10 may be billed higher than the truth supports.

Nobody knows the right answers in production, so α is measured on the frozen evaluation set: cases both parties labeled at signing. Probes are a small version of that set, and a WRONG result is the kind of event α counts. Only some WRONGs count, though:

1. **Only overbilling counts.** A certain, wrong answer that underpays the vendor is not counted against α. The RFC bounds overbilling only; nothing bounds underbilling.
2. **It counts wrong bills, not wrong answers.** A probe grades one question, while a unit's bill combines several. A wrong answer that does not change the grade does not change the bill. Small per-question error rates can also add up to a larger per-bill rate.
3. **It holds only while production resembles the labeled set.** If the work drifts, or an agent learns to write drafts that fool the decider, the real rate can exceed α while the measured rate still looks fine.

The sandbox does not compute α yet. Its router accepts any answer outside a fixed band, which only means the decider sounded confident. The RFC's router is calibrated on the labeled set with conformal prediction, so that the error rate among accepted answers is guaranteed. A natural next step: treat the probes as the labeled set, record which question each probe feeds and in which direction a wrong answer moves the price, and report the measured overbilling rate among auto-accepted answers.

## Walkthrough B: one month of a legal drafting agent

The case: a vendor's legal agent drafts mutual NDAs for a buyer and is paid $120 per NDA the supervising attorney keeps, with a $60 credit for a harmful draft. `cases/legal-nda/submissions/` holds four drafts, each written to exercise a different path:

| Draft | Built to test |
| --- | --- |
| `nda-01-good` | The happy path |
| `nda-02-hollow` | Every heading and fact is present, but the clauses say nothing. Tier 0 passes it; only judgment can catch it |
| `nda-03-oneway-injection` | Obligations bind one party only, plus a hidden note telling the reviewer the draft was approved |
| `nda-04-placeholder-waiver` | A leftover `[COUNTERPARTY NAME]` and a waiver of injunctive relief |

The clock is simulated: every command takes the time it happens at (`--now`, `--at`), so a 7-day window can close in one command.

**1. Judge every draft at session close.**

```bash
python sandbox/oa.py run legal-nda
```

For each draft:
- **TIER 0** prints each fact check and its result.
- **TIER 1** prints the planned task and the document exactly as sent, the request with every typed question, and the raw response.
- **ROUTER** says which answers are certain enough to accept and which escalate.
- **TIER 2** repeats the same for the escalated questions only. Its answers in the grey zone are sent to the panel.
- **OUTCOME** checks each accepted answer against the spec's threshold, then each goal, and derives the level.
- **LEDGER APPEND** prints the full record, including the hash that links it to the previous record.

`--t1` and `--t2` pick the deciders; for example `--t1 claude-haiku` compares a prompted LLM at Tier 1.

**2. Things happen later.**

```bash
python sandbox/oa.py rule  legal-nda wu_nda-03-oneway-injection j1=yes --at 2026-10-07T10:00:00Z  # panel settles a grey-zone question
python sandbox/oa.py event legal-nda wu_nda-01-good accepted   --at 2026-10-08T09:00:00Z         # attorney keeps the draft
python sandbox/oa.py event legal-nda wu_nda-02-hollow dispute  --at 2026-10-08T15:00:00Z         # vendor disputes the grade
python sandbox/oa.py rule  legal-nda wu_nda-02-hollow c2=yes   --at 2026-10-10T11:00:00Z         # panel rules on the dispute
```

Each prints the current record, what the event means, and the record it writes, or why the ledger refused it. `rule` shows pass or fail per check before the ruling, then re-derives the outcome goal by goal.

**3. Close the windows and bill.**

```bash
python sandbox/oa.py mature  legal-nda --now 2026-10-12T13:00:00Z
python sandbox/oa.py invoice legal-nda --period 2026-10 --now 2026-10-31T23:00:00Z
```

`invoice` settles each matured or adjudicated unit as final and prices it, showing the arithmetic. It then prints the payment request from the vendor to the buyer: one line per unit, each pointing at its ledger record and evidence hash, with the period's ledger root attached.

**4. Inspect, verify, replay.**

```bash
python sandbox/oa.py show   legal-nda                          # each unit's record history
python sandbox/oa.py verify legal-nda                          # recompute every hash chain
python sandbox/oa.py replay legal-nda wu_nda-01-good --times 5 # same snapshot, asked again
python sandbox/oa.py event  legal-nda wu_nda-01-good material_edit --at 2026-11-03T10:00:00Z
python sandbox/oa.py reset  legal-nda                          # start over
```

`replay` prints Δp, the replayed probability minus the original, and any *flip*: a Δp that crosses the pass threshold and so changes the decision. The late `material_edit` after the unit is final is refused, because v0.1 does not say what happens to evidence after finality.

## Command reference

| Command | Does | Options |
| --- | --- | --- |
| `run <case>` | Judge every submission not yet in the ledger | `--t1` (default `jev`), `--t2` (default `claude-sonnet`), `--now` |
| `event <case> <unit> <type>` | Record later evidence: `accepted`, `material_edit`, `revert`, `reopen`, `dispute` | `--at` |
| `rule <case> <unit> q=yes\|no ...` | Tier 3 panel ruling on named questions | `--at` |
| `mature <case>` | Mature provisional units whose window has closed | `--now` (required) |
| `invoice <case>` | Settle and price final units into a payment request | `--period YYYY-MM`, `--now` (both required) |
| `show <case>` | Each unit's current grade and record history | |
| `verify <case>` | Recompute the hash chains | |
| `replay <case> <unit>` | Re-ask Tier 1 on the stored input snapshot | `--times N`, `--t1` |
| `reset <case>` | Delete the case's ledger and invoices | |

## Add your own

**A probe.** Add an entry to `probes/nda.yaml`, or a new file with the same shape: `id`, `question` (a key under `questions:`), `expect` (`yes` or `no`), `why`, `state`, and optionally `enrich` with any of `criteria`, `focus`, `decompose`. Write the expected answer before you run it.

**A case.** Create `cases/<name>/` with:

- `spec.yaml`: a success spec that validates against `spec/success-spec.schema.json`.
- `case.py`, which must define:
  - `SPEC`: path to the spec
  - `TENANT_CHAIN`: platform, vendor, paying customer
  - `CONTRACT`, `RATE`, `HARM_CREDIT` and `CURRENCY`, keyed by `task_class`
  - `submissions()`: returns `(work_unit_id, path)` pairs
  - `evidence(path)`: returns a dict, the end state the decider sees
  - `t0(path)`: returns `{check_id: (ok, detail)}` for every predicate and every Tier 0 constraint
- The submissions themselves.

Then `python sandbox/oa.py run <name>`.

## Sandbox rules beyond the v0.1 schema

The ledger enforces rules the RFC states in prose but `spec/ledger-record.schema.json` does not encode. They are proposals, not part of the spec:

- `fulfilled` requires `constraints_ok`, `integrity_ok` and `goals_met == 1`; any failed constraint or integrity check must be `harmful`.
- `recorded_at` may not precede `occurred_at`; every decision cites at least one evidence hash.
- A new decision on a unit must supersede its current head, and two records may not supersede the same parent.
- Supersession follows a state machine: `attempted → provisional → matured → final`, `provisional → final` on contrary late evidence, `→ disputed → adjudicated → final`. Nothing supersedes `final`.
- `prev_hash` is the SHA-256 of the previous record in the same customer and month, serialized with sorted keys and no whitespace. The first record links to a genesis hash.

## Known limits

- The router is a fixed band, not conformal prediction, so it carries no error-rate guarantee.
- Routing is per question, not per decision, so a unit already settled as harmful can still wait on the panel for an unrelated question.
- `oa.py` does not run the enrichment ladder; only `probe.py` does.
- The Claude CLI does not report which build served a call, so a Claude pin cannot be verified; Jev reports its served version.
- One tenant per case, and one maturation window per spec: the longest one.
- Evidence blobs are stored in full, with no redaction or erasure.
- The tool only checks the hash chain internally. It cannot catch an operator who rewrites the open period and recomputes every hash; `tests/test_ledger.py` demonstrates this.
