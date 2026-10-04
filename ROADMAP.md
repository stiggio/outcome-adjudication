# Roadmap

Milestones, not dates. Each milestone ships with a changelog entry and an updated RFC.

## v0.1: Request for comments (current)
- [x] RFC 0001 published
- [x] Success specification and ledger record schemas, with validated examples
- [x] Metric definitions: overbilling bound α, ADF(α), calibration error, replay reproduction rate
- [x] Pre-registered hypotheses H1 to H6
- [ ] Four-week comment window closes; feedback triaged into issues

## v0.2: Experiment results
- [ ] Freeze thresholds and power calculation (dated commit)
- [ ] Task set: public coding issues, impossible variants, open-ended drafting tasks
- [ ] Expert double-labeling, blind to evaluator outputs
- [ ] Compare rules only, a single LLM judge, and the full cascade with three fast-decider candidates
- [ ] Publish ADF curves, calibration error, latency, cost and every negative result

## v0.3: Reference components (alpha)
- [ ] `spec-compiler`: planned task → success spec, with ambiguity detection
- [ ] `decider`: interface plus adapters for single-pass decision models, distilled classifiers and prompted LLMs
- [ ] `ledger`: bitemporal, hash-chained record store with stage-by-stage reconciliation
- [ ] `bench`: reproducible adjudication benchmark with canaries and impossible canaries

## v1.0: Stable specification
- [ ] Schemas frozen with a versioning and change-order policy
- [ ] Conformance tests any implementation can run
