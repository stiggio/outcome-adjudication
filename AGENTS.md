# AGENTS.md

Instructions for AI coding agents working in this repository. Humans: see README.md and CONTRIBUTING.md.

## What this repo is
A specification and research program, not a library. There is no implementation code yet. Do not invent APIs, results or benchmark numbers.

## Layout
- `docs/rfc/` RFCs. RFC 0001 is the source of truth for definitions.
- `docs/concepts.md` defined vocabulary. Use these terms exactly as defined.
- `spec/` JSON Schemas (draft 2020-12) and metric definitions.
- `examples/` must validate against `spec/`.
- `experiment/` pre-registration. Never edit frozen thresholds after the freeze commit.
- `packages/`, `bench/` design notes only.

## Commands
- Validate everything: `pip install jsonschema pyyaml && python tools/validate.py`

## Rules
- Any change to a schema must update at least one example, the RFC section it implements, and `CHANGELOG.md` in the same pull request.
- Label claims in prose as Evidence (with a citation), Hypothesis (with a falsification test) or Design choice (with its trade-off).
- Keep the RFC vendor-neutral: describe market practice without naming providers.
- No em-dashes in prose.

## Definition of done
- `python tools/validate.py` passes.
- New terms are added to `docs/concepts.md`.
- `CHANGELOG.md` has an entry.
