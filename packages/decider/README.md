# decider

**Status: Design.** No code yet. This page describes the intended scope so feedback can shape it before implementation.

The interface and adapters that let different model classes fill the fast-decider tier, as specified in `spec/decider-interface.md`.

- Adapters: single-pass decision models, distilled classifiers, prompted LLMs
- Per-tenant calibration and conformal risk routing
- Deterministic serving or stored output scores for replay

See [decider-interface.md](../../spec/decider-interface.md).
