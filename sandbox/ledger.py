# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Stigg
"""Append-only, bitemporal, hash-chained outcome ledger.

Enforces what the RFC says in prose but the v0.1 schema does not:
cross-field outcome invariants, a state machine on supersession, single-head
supersession (no forks), and a defined canonical form so prev_hash is checkable.
"""
import hashlib, json, pathlib
from jsonschema import Draft202012Validator

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
_schema = Draft202012Validator(json.loads((REPO_ROOT / "spec/ledger-record.schema.json").read_text()))

# Which state may supersede which. The RFC's Figure 2, made explicit.
TRANSITIONS = {
    None: {"attempted", "provisional"},
    "attempted": {"provisional", "disputed"},
    "provisional": {"provisional", "matured", "final", "disputed"},
    "matured": {"final", "disputed"},
    "disputed": {"adjudicated"},
    "adjudicated": {"final"},
    "final": set(),  # RFC is silent on evidence after finality; we refuse it and report it
}


def canon(obj):
    # Stand-in for RFC 8785 (JCS): sorted keys, no whitespace, UTF-8.
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha(b):
    return "sha256:" + hashlib.sha256(b).hexdigest()


class LedgerError(Exception):
    pass


class Ledger:
    def __init__(self, root):
        self.root = pathlib.Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "ledger.jsonl"
        self.blobs = self.root / "blobs"
        self.blobs.mkdir(exist_ok=True)
        self.records = [json.loads(l) for l in self.path.read_text().splitlines()] if self.path.exists() else []

    # content-addressed evidence store, so replay has bytes and not just hashes
    def put_blob(self, obj):
        data = canon(obj)
        h = sha(data)
        (self.blobs / h.split(":")[1]).write_bytes(data)
        return h

    def get_blob(self, h):
        return json.loads((self.blobs / h.split(":")[1]).read_bytes())

    @staticmethod
    def chain_key(rec):
        return (rec["tenant_chain"][-1], rec["recorded_at"][:7])  # per paying customer, per month

    def _chain(self, key):
        return [r for r in self.records if self.chain_key(r) == key]

    @staticmethod
    def genesis(key):
        return sha(f"genesis:{key[0]}:{key[1]}".encode())

    def by_id(self, rid):
        return next((r for r in self.records if r["record_id"] == rid), None)

    def head(self, work_unit):
        """Current record for a unit: the one nothing supersedes."""
        recs = [r for r in self.records if r["work_unit"] == work_unit]
        superseded = {r["supersedes"] for r in recs if r["supersedes"]}
        heads = [r for r in recs if r["record_id"] not in superseded]
        return heads[-1] if heads else None

    def units(self):
        seen = []
        for r in self.records:
            if r["work_unit"] not in seen:
                seen.append(r["work_unit"])
        return seen

    def check(self, rec):
        problems = [e.message for e in _schema.iter_errors(rec)]
        o = rec["outcome"]
        if o["level"] == "fulfilled" and not (o["constraints_ok"] and o["integrity_ok"] and o["goals_met"] == 1):
            problems.append("fulfilled requires constraints_ok, integrity_ok and goals_met == 1")
        if (not o["constraints_ok"] or not o["integrity_ok"]) and o["level"] != "harmful":
            problems.append("a constraint or integrity failure must be level harmful")
        if rec["recorded_at"] < rec["occurred_at"]:
            problems.append("recorded_at precedes occurred_at")
        if rec["state"] != "attempted" and not rec["evidence"]:
            problems.append("a decision needs at least one evidence hash")
        if self.by_id(rec["record_id"]):
            problems.append("duplicate record_id")
        parent = None
        if rec["supersedes"]:
            parent = self.by_id(rec["supersedes"])
            if parent is None:
                problems.append("supersedes an unknown record")
            elif parent["work_unit"] != rec["work_unit"]:
                problems.append("supersedes a record of another work unit")
            elif self.head(rec["work_unit"])["record_id"] != parent["record_id"]:
                problems.append("fork: parent is already superseded")
        elif self.head(rec["work_unit"]):
            problems.append("unit already has records; new decision must supersede its head")
        prev_state = parent["state"] if parent else None
        if rec["state"] not in TRANSITIONS.get(prev_state, set()):
            problems.append(f"illegal transition {prev_state} -> {rec['state']}")
        return problems

    def append(self, rec):
        chain = self._chain(self.chain_key(rec))
        rec["prev_hash"] = sha(canon(chain[-1])) if chain else self.genesis(self.chain_key(rec))
        problems = self.check(rec)
        if problems:
            raise LedgerError(f"{rec['record_id']} rejected: " + "; ".join(problems))
        self.records.append(rec)
        with self.path.open("a") as f:
            f.write(json.dumps(rec, sort_keys=True) + "\n")
        return rec

    def next_id(self):
        return f"or_{len(self.records) + 1:04d}"

    def verify(self):
        """Recompute every chain from the file on disk. Returns list of breaks."""
        on_disk = [json.loads(l) for l in self.path.read_text().splitlines()] if self.path.exists() else []
        breaks, last = [], {}
        for r in on_disk:
            key = self.chain_key(r)
            expected = sha(canon(last[key])) if key in last else self.genesis(key)
            if r["prev_hash"] != expected:
                breaks.append(f"{r['record_id']} ({key[0]} {key[1]}): prev_hash mismatch")
            last[key] = r
        return breaks

    def roots(self):
        last = {}
        for r in self.records:
            last[self.chain_key(r)] = r
        return {f"{k[0]} {k[1]}": sha(canon(v)) for k, v in last.items()}
