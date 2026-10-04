# ledger

**Status: Design.** No code yet. This page describes the intended scope so feedback can shape it before implementation.

An append-only, bitemporal, hash-chained store for outcome records that validate against `spec/ledger-record.schema.json`, with stage-by-stage reconciliation borrowed from telecom revenue assurance.

- Corrections are new records that supersede old ones
- Per-tenant, per-period hash chains and a published statement of outcomes
- Reconciliation: assembled = decided + pending; matured billable = rated = invoiced

See [ledger-record.schema.json](../../spec/ledger-record.schema.json).
