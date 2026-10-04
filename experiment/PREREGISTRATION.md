# Pre-registration: v0.2 experiment

Status: draft for comment. Thresholds are proposals and will be frozen, with a dated commit, before any data is collected.

## Hypotheses

| ID | Prediction | What would falsify it |
| --- | --- | --- |
| H1 | Evaluators with independent read access to the end state beat transcript-only evaluators on precision at equal recall | Transcript-only evaluators match them |
| H2 | Per-tenant recalibration lowers calibration error for every Tier 1 candidate | Any candidate's calibration error does not fall |
| H3 | Rules alone underbill, judges alone overbill, and the cascade beats both on billing error | Either single method matches the cascade |
| H4 | On spec-driven coding tasks the cascade reaches ADF of 80% or more at α = 1% | ADF below 80% at α = 1% |
| H5 | On open-ended drafting tasks ADF stays at or below 40% at the same α | ADF above 40% |
| H6 | Integrity checks flag at least 90% of passed impossible canaries | Fewer than 90% flagged |

## Design

1. **Tasks:** issues from public coding benchmarks, impossible variants made by mutating their tests, and a smaller set of open-ended drafting tasks for H5. Sample sizes come from a power calculation committed here before collection.
2. **Agents:** at least two publicly available coding agents, default settings.
3. **Evaluators:** rules only; a single LLM judge reading the transcript; the full cascade with three Tier 1 candidates: a single-pass decision model, a small classifier distilled from Tier 2, and a prompted LLM with constrained output.
4. **Ground truth:** two independent expert labels per unit, blind to evaluator outputs, with disagreements adjudicated; matured signals where available.
5. **Metrics:** precision and recall of fulfilled, calibration error before and after recalibration, ADF curves, p50 and p99 latency, cost per 1,000 decisions, and the replay reproduction rate. Definitions are in `spec/metrics.md`.
6. **Release:** code, task lists, labels and results, including every negative result.
