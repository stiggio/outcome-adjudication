# spec-compiler

**Status: Design.** No code yet. This page describes the intended scope so feedback can shape it before implementation.

Turns a planned task's prompts, instructions and tools into a success specification that validates against `spec/success-spec.schema.json`. Runs several independent compilers and flags criteria they disagree on as ambiguous.

- Input: planned task (prompts, instructions, tool list)
- Output: success spec plus an ambiguity report
- Never infers success criteria from agent behavior, only from intent

See [0001-outcome-adjudication.md](../../docs/rfc/0001-outcome-adjudication.md).
