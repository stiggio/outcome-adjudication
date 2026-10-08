# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Stigg
"""Lawyer agent billed per drafted NDA. Evidence is the document itself."""
import pathlib, re

HERE = pathlib.Path(__file__).parent
SPEC = HERE / "spec.yaml"
TENANT_CHAIN = ["platform", "lexdraft_agents", "acme_robotics"]
CONTRACT = "c-2026-10-legal-v1"
RATE = {"nda_draft": 120.00}
HARM_CREDIT = {"nda_draft": 60.00}
CURRENCY = "USD"

HEADINGS = ["definition", "exclusions", "obligations", "term", "return of materials", "remedies", "governing law"]


def submissions():
    return [(f"wu_{p.stem}", p) for p in sorted((HERE / "submissions").glob("*.md"))]


def evidence(path):
    return {"document": path.read_text()}


def t0(path):
    text = path.read_text()
    low = text.lower()
    heads = [h for h in HEADINGS if re.search(rf"^#+ .*{h}", low, re.M)]
    missing = sorted(set(HEADINGS) - set(heads))
    return {
        "p1": (not missing, f"missing headings: {missing}" if missing else "all headings present"),
        "p2": ("acme robotics, inc." in low and "northwind labs llc" in low, "string match on both legal names"),
        "p3": (
            "delaware" in low and bool(re.search(r"\b(2|two)\b.{0,12}years?", low)) and bool(re.search(r"\b(3|three)\b.{0,12}years?", low)),
            "Delaware + 2-year + 3-year mentions",
        ),
        "c1": (not re.search(r"\[[A-Z][A-Z _]+\]|\bTBD\b|lorem ipsum", text), "placeholder regex"),
    }
