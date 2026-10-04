# Adjudication bench

**Status: Planned.** No code yet. This page describes the intended scope so feedback can shape it before implementation.

A reproducible benchmark for adjudicators: known-outcome canary tasks, impossible canaries that can only be passed by cheating, and jointly labeled ground truth. Its headline output is the ADF(α) curve per task class.

- Task sets: public coding issues, impossible variants, open-ended drafting tasks
- Evaluators compared: rules only, single LLM judge, full cascade
- Metrics as defined in `spec/metrics.md`

See [PREREGISTRATION.md](../experiment/PREREGISTRATION.md).
