# Specification

| File | Purpose |
| --- | --- |
| [`success-spec.schema.json`](success-spec.schema.json) | A compiled success specification: goals, predicates, judged criteria, constraints, integrity checks, matured criteria |
| [`ledger-record.schema.json`](ledger-record.schema.json) | One append-only outcome ledger record |
| [`decider-interface.md`](decider-interface.md) | The contract any decision model must honor to fill a tier |
| [`metrics.md`](metrics.md) | Definitions of α, ADF(α), calibration error and replay reproduction rate |

Schemas use JSON Schema draft 2020-12. Run `python tools/validate.py` from the repository root to check every example.

Versioning: while the spec is in draft, breaking changes are allowed with a changelog entry. From v1.0, any change to a pinned decider bundle or schema is a change order, run in shadow and disclosed before activation.
