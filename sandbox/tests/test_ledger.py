# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Stigg
"""Offline tests: no model calls, no API keys. Run: python -m pytest sandbox/tests"""
import copy, json, pathlib, sys

import pytest, yaml
from jsonschema import Draft202012Validator

SANDBOX = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SANDBOX))
from ledger import Ledger, LedgerError, canon, sha  # noqa: E402
import oa  # noqa: E402

H = "sha256:" + "0" * 64


def record(L, unit="wu_1", state="provisional", supersedes=None, level="fulfilled", at="2026-10-05T12:00:00Z", **outcome):
    o = {"level": level, "goals_met": 1, "constraints_ok": True, "integrity_ok": True}
    o.update(outcome)
    return {
        "record_id": L.next_id(), "work_unit": unit, "tenant_chain": ["platform", "builder", "customer"],
        "contract_version": "c1", "decider_bundle": H, "evidence": [H], "input_snapshot": H, "state": state,
        "outcome": o, "decided_by": "tier_1", "reason": "test", "occurred_at": at, "recorded_at": at,
        "supersedes": supersedes, "prev_hash": "",
    }


@pytest.fixture
def L(tmp_path):
    return Ledger(tmp_path)


def test_chain_links_each_record_to_the_previous_one(L):
    a = L.append(record(L))
    b = L.append(record(L, state="matured", supersedes=a["record_id"]))
    assert a["prev_hash"] == Ledger.genesis(("customer", "2026-10"))
    assert b["prev_hash"] == sha(canon(a))
    assert L.verify() == []


def test_head_follows_supersession(L):
    a = L.append(record(L))
    b = L.append(record(L, state="matured", supersedes=a["record_id"]))
    assert L.head("wu_1")["record_id"] == b["record_id"]


@pytest.mark.parametrize("outcome", [
    {"constraints_ok": False},
    {"integrity_ok": False},
    {"goals_met": 0.5},
])
def test_fulfilled_requires_every_check(L, outcome):
    with pytest.raises(LedgerError, match="fulfilled requires"):
        L.append(record(L, **outcome))


def test_failed_constraint_must_be_harmful(L):
    with pytest.raises(LedgerError, match="must be level harmful"):
        L.append(record(L, level="partial", goals_met=0.5, constraints_ok=False))


def test_recorded_before_occurred_is_rejected(L):
    rec = record(L)
    rec["recorded_at"] = "2026-10-01T00:00:00Z"
    with pytest.raises(LedgerError, match="recorded_at precedes occurred_at"):
        L.append(rec)


def test_two_records_cannot_supersede_the_same_parent(L):
    a = L.append(record(L))
    L.append(record(L, state="disputed", supersedes=a["record_id"]))
    with pytest.raises(LedgerError, match="fork"):
        L.append(record(L, state="matured", supersedes=a["record_id"]))


def test_final_cannot_be_superseded(L):
    a = L.append(record(L, state="provisional"))
    f = L.append(record(L, state="final", supersedes=a["record_id"]))
    with pytest.raises(LedgerError, match="illegal transition final -> final"):
        L.append(record(L, state="final", level="not_fulfilled", goals_met=0, supersedes=f["record_id"]))


def test_second_decision_must_supersede_the_head(L):
    L.append(record(L))
    with pytest.raises(LedgerError, match="must supersede its head"):
        L.append(record(L))


def test_editing_a_record_in_place_breaks_the_chain(L):
    L.append(record(L, unit="wu_1"))
    L.append(record(L, unit="wu_2"))
    lines = L.path.read_text().splitlines()
    first = json.loads(lines[0])
    first["outcome"]["level"] = "partial"
    lines[0] = json.dumps(first, sort_keys=True)
    L.path.write_text("\n".join(lines) + "\n")
    assert any("prev_hash mismatch" in b for b in L.verify())


def test_rechained_rewrite_is_not_detected_without_an_external_root(L):
    """Known limitation: whoever operates the ledger can rewrite and re-chain an open period.
    Only a root held by someone else (published, countersigned) exposes it."""
    L.append(record(L, unit="wu_1"))
    L.append(record(L, unit="wu_2"))
    root_before = L.roots()["customer 2026-10"]
    recs = [json.loads(l) for l in L.path.read_text().splitlines()]
    recs[0]["reason"] = "rewritten"
    prev = Ledger.genesis(("customer", "2026-10"))
    for r in recs:
        r["prev_hash"] = prev
        prev = sha(canon(r))
    L.path.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in recs))
    rewritten = Ledger(L.root)
    assert rewritten.verify() == []
    assert rewritten.roots()["customer 2026-10"] != root_before


def test_blobs_are_content_addressed(L):
    h = L.put_blob({"a": 1})
    assert h == sha(canon({"a": 1}))
    assert L.get_blob(h) == {"a": 1}


def test_nda_case_spec_is_a_valid_success_spec():
    schema = json.loads((SANDBOX.parent / "spec" / "success-spec.schema.json").read_text())
    spec = yaml.safe_load((SANDBOX / "cases" / "legal-nda" / "spec.yaml").read_text())
    assert list(Draft202012Validator(schema).iter_errors(spec)) == []


def test_nda_tier0_facts():
    case = oa.load_case("legal-nda")
    facts = {p.stem: case.t0(p) for _, p in case.submissions()}
    assert all(ok for ok, _ in facts["nda-01-good"].values())
    assert all(ok for ok, _ in facts["nda-02-hollow"].values()), "hollow draft passes every fact; only judgment catches it"
    assert facts["nda-04-placeholder-waiver"]["c1"][0] is False


def test_outcome_levels():
    spec = oa.load_case("legal-nda").spec
    all_pass = {k: True for k in ("p1", "p2", "p3", "j1", "j2", "c1", "c2", "i1")}
    assert oa.outcome_of(spec, all_pass)[0]["level"] == "fulfilled"
    assert oa.outcome_of(spec, {**all_pass, "i1": False})[0]["level"] == "harmful"
    assert oa.outcome_of(spec, {**all_pass, "j2": False})[0] == {"level": "partial", "goals_met": 0.8, "constraints_ok": True, "integrity_ok": True}
