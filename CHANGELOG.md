# Changelog

All notable changes to the specification and RFCs. Contributors whose input changed the design are credited inline.

## Unreleased
- Sandbox prototype (`sandbox/`): a runnable cascade (Tier 0 facts, a single-pass decider at Tier 1, an LLM judge at Tier 2, human panel rulings at Tier 3), a hash-chained ledger with supersession rules, maturation, a contract pricing function that emits payment requests, and known-answer probes with an enrichment ladder. One worked case: a legal drafting agent billed per mutual NDA. Contributed by Dor Bar.
- Concepts: probe, certainty band, enrichment ladder.

## v0.1, 2026-10-04
- RFC 0001 published for comment.
- Schemas: success specification, outcome ledger record.
- Metrics: overbilling bound α, auto-decidable fraction ADF(α), calibration error, replay reproduction rate.
- Pre-registration of hypotheses H1 to H6 for the v0.2 experiment.
- Examples: coding bug fix (provisional and superseded records), customer support resolution.
