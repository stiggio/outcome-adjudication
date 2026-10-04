# Contributing

Thank you for helping make outcome-based pricing auditable. This project is at the specification stage, so the most valuable contributions are arguments, evidence and test cases rather than code.

## Ways to contribute
1. **Critique the RFC.** Open an issue with the *feedback* template and say which audience you are writing as.
2. **Propose a spec change.** Use the *spec change* template. Accepted proposals become pull requests that update the schema, at least one example, the relevant RFC section and `CHANGELOG.md` together.
3. **Add prior art.** Use the *prior art* template with a link and one paragraph on how it relates.
4. **Contribute canary tasks.** Tasks with known outcomes, or tasks that can only be passed by cheating, strengthen the v0.2 benchmark.

## Writing conventions
- Mark claims as **Evidence** (cited), **Hypothesis** (with the test that would disprove it) or **Design choice** (with its trade-off).
- Keep the RFC vendor-neutral: describe market practice without naming providers.
- Use the vocabulary in `docs/concepts.md`. Add new terms there first.

## Before opening a pull request
```bash
pip install jsonschema pyyaml
python tools/validate.py
```

## Licensing of contributions
Code contributions are accepted under the GNU AGPL-3.0, and writing or specification contributions under CC BY-SA 4.0, matching the files they change. Before we merge code contributions, contributors will be asked to sign a Contributor License Agreement.

## Credit
Everyone whose input changes the design is credited in `CHANGELOG.md`.

## Conduct
This project follows our [Code of Conduct](CODE_OF_CONDUCT.md).
