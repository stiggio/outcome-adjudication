# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Stigg
"""Validate the specification schemas and every example in examples/."""
import json, pathlib, sys
import yaml
from jsonschema import Draft202012Validator

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMAS = {
    "success-spec": ROOT / "spec" / "success-spec.schema.json",
    "ledger-record": ROOT / "spec" / "ledger-record.schema.json",
}

def load(path):
    text = path.read_text()
    return yaml.safe_load(text) if path.suffix in (".yaml", ".yml") else json.loads(text)

def main():
    failures = 0
    validators = {}
    for name, path in SCHEMAS.items():
        schema = json.loads(path.read_text())
        Draft202012Validator.check_schema(schema)
        validators[name] = Draft202012Validator(schema)
        print(f"ok    schema  {path.relative_to(ROOT)}")
    for example in sorted((ROOT / "examples").iterdir()):
        kind = "success-spec" if ".success-spec." in example.name else "ledger-record" if example.name.startswith("ledger-record") else None
        if kind is None:
            continue
        errors = list(validators[kind].iter_errors(load(example)))
        for e in errors:
            print(f"FAIL  {example.relative_to(ROOT)}: {'/'.join(map(str, e.path))} {e.message}")
        failures += len(errors)
        if not errors:
            print(f"ok    example {example.relative_to(ROOT)}")
    sys.exit(1 if failures else 0)

if __name__ == "__main__":
    main()
