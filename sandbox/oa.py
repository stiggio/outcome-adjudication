# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Stigg
"""Outcome adjudication sandbox: cascade -> ledger -> maturation -> payment request.

Every step prints what it receives, what it sends to a model, what comes back,
how the router reads it, and the exact ledger record it writes.

  python sandbox/oa.py run <case> [--t1 jev] [--t2 claude-sonnet] [--now ISO]
  python sandbox/oa.py event <case> <unit> accepted|material_edit|revert|reopen|dispute [--at ISO]
  python sandbox/oa.py rule <case> <unit> <question>=yes|no ... [--at ISO]
  python sandbox/oa.py mature <case> --now ISO
  python sandbox/oa.py invoice <case> --period YYYY-MM --now ISO
  python sandbox/oa.py show <case>
  python sandbox/oa.py verify <case>
  python sandbox/oa.py replay <case> <unit> [--times N] [--t1 jev]
  python sandbox/oa.py reset <case>
"""
import argparse, datetime as dt, importlib.util, json, pathlib, re, shutil, sys
import yaml

SANDBOX = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(SANDBOX))
from ledger import Ledger, LedgerError, canon, sha  # noqa: E402
import deciders  # noqa: E402

# A Tier 1 answer is accepted only when it is certain: p <= NO_MAX or p >= YES_MIN.
# Anything between goes to Tier 2. This is a fixed band, not conformal prediction.
NO_MAX, YES_MIN = 0.10, 0.90
# Tier 2 answers inside this band go to the human panel (Tier 3).
GREY = (0.35, 0.65)


def say(indent, text=""):
    for line in str(text).splitlines() or [""]:
        print("   " * indent + line)


def load_case(name):
    path = SANDBOX / "cases" / name / "case.py"
    if not path.exists():
        sys.exit(f"no case at {path}")
    spec = importlib.util.spec_from_file_location(f"case_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.spec = yaml.safe_load(mod.SPEC.read_text())
    mod.name = name
    return mod


def ledger_for(case):
    return Ledger(SANDBOX / "out" / "runs" / case.name)


def iso(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def fmt(t):
    return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def duration(p):
    m = re.fullmatch(r"P(\d+)D", p)
    if not m:
        raise ValueError(f"only PnD windows are supported, got {p!r}")
    return dt.timedelta(days=int(m.group(1)))


def band(p):
    return "YES" if p >= YES_MIN else "NO" if p <= NO_MAX else "UNCERTAIN"


def bundle_hash(case, t1, t2):
    return sha(canon({
        "spec": case.spec, "t1": [t1.name, t1.pinned], "t2": [t2.name, t2.pinned],
        "band": [NO_MAX, YES_MIN], "grey": GREY, "rates": case.RATE, "harm_credit": case.HARM_CREDIT,
    }))


def questions(spec, t0_ids):
    """Typed questions for the model tiers: judged criteria, plus model-decided constraints and integrity checks."""
    q = {}
    for j in spec["judged_criteria"]:
        q[j["id"]] = j["question"]
    for c in spec["constraints"] + spec["integrity_checks"]:
        if c["id"] not in t0_ids and "tier_1" in c["decided_by"]:
            q[c["id"]] = f"This requirement was respected: {c['check']}"
    return q


def threshold(spec, qid):
    for j in spec["judged_criteria"]:
        if j["id"] == qid:
            return j["threshold"]
    return 0.5


def show_model_call(r, indent):
    req = dict(r["request"])
    if isinstance(req.get("state"), dict):
        say(indent, "STATE sent as a JSON object (text fields shown unescaped):")
        for k, v in req["state"].items():
            say(indent + 1, f"{k}:")
            say(indent + 2, str(v).rstrip())
        req["state"] = "<the state above>"
    say(indent, "REQUEST")
    say(indent + 1, json.dumps(req, indent=2, ensure_ascii=False))
    say(indent, f"RESPONSE ({r['latency_ms']} ms, served by {r['served_model']})")
    say(indent + 1, json.dumps(r["response"], ensure_ascii=False))


def decide(case, sub, t1, t2):
    spec = case.spec
    ev = case.evidence(sub)
    # What the decider sees: the planned task (intent) plus the end state (evidence). Never the agent's own claims.
    state = {"planned_task": spec["planned_task"].strip(), **ev}

    say(1, "┌─ TIER 0: facts (deterministic checks from case.py, no model)")
    facts = case.t0(sub)
    for k, (ok, detail) in facts.items():
        say(2, f"{k:<4} {'ok  ' if ok else 'FAIL'}  {detail}")
    trace = {"t0": {k: {"ok": v[0], "detail": v[1]} for k, v in facts.items()}, "t1": None, "t2": None, "t3": []}
    tier, answers = "tier_0", {}
    c_ids = {c["id"] for c in spec["constraints"]}
    if any(not facts[c][0] for c in c_ids if c in facts):
        say(2, "a constraint failed on facts: the outcome is harmful whatever a model says, so no model is consulted")
        say(1, "└─")
        return facts, answers, trace, tier, ev
    say(1, "└─")

    qs = questions(spec, set(facts))
    say(1, f"┌─ TIER 1: {t1.name} ({t1.pinned}), {len(qs)} questions in one call")
    r1 = t1.ask(state, qs)
    trace["t1"] = {k: r1[k] for k in ("answers", "served_model", "latency_ms", "usage")}
    tier = "tier_1"
    show_model_call(r1, 2)
    if t1.pinned and r1["served_model"] != t1.pinned:
        say(2, f"!! served model {r1['served_model']} is not the pinned {t1.pinned}: the decider bundle drifted")
    say(2, f"ROUTER  accept only certain answers: p <= {NO_MAX} (NO) or p >= {YES_MIN} (YES)")
    unsure = {}
    for k, p in r1["answers"].items():
        b = band(p)
        say(3, f"{k:<4} p={p:.2f}  {b:<9} {'accepted' if b != 'UNCERTAIN' else 'escalate to Tier 2'}")
        if b == "UNCERTAIN":
            unsure[k] = qs[k]
        else:
            answers[k] = p
    say(1, "└─")

    if unsure:
        say(1, f"┌─ TIER 2: {t2.name} ({t2.pinned}), only the {len(unsure)} uncertain questions")
        r2 = t2.ask(state, unsure)
        trace["t2"] = {k: r2[k] for k in ("answers", "served_model", "latency_ms", "usage")}
        tier = "tier_2"
        show_model_call(r2, 2)
        say(2, f"ROUTER  Tier 2 answers between {GREY[0]} and {GREY[1]} go to the human panel")
        for k, p in r2["answers"].items():
            if GREY[0] < p < GREY[1]:
                trace["t3"].append(k)
                say(3, f"{k:<4} p={p:.2f}  still unsure -> Tier 3 human panel (oa.py rule)")
            else:
                answers[k] = p
                say(3, f"{k:<4} p={p:.2f}  accepted")
        say(1, "└─")
    return facts, answers, trace, tier, ev


def outcome_of(spec, passed, log=None):
    met = {}
    for g in spec["goals"]:
        checks = [p["id"] for p in spec["predicates"] if p["goal"] == g["id"]] + [j["id"] for j in spec["judged_criteria"] if j["goal"] == g["id"]]
        met[g["id"]] = all(passed.get(c, False) for c in checks)
        if log:
            log(f"goal {g['id']} (weight {g['weight']}, {'mandatory' if g['mandatory'] else 'optional'}): "
                f"{'MET' if met[g['id']] else 'not met'}  needs {', '.join(f'{c}={passed.get(c)}' for c in checks)}")
    total = sum(g["weight"] for g in spec["goals"])
    goals_met = round(sum(g["weight"] for g in spec["goals"] if met[g["id"]]) / total, 4)
    c_ok = all(passed.get(c["id"], True) for c in spec["constraints"])
    i_ok = all(passed.get(c["id"], True) for c in spec["integrity_checks"])
    if not (c_ok and i_ok):
        level, why = "harmful", "a constraint or integrity check failed"
    elif all(met[g["id"]] for g in spec["goals"] if g["mandatory"]):
        level, why = "fulfilled", "every mandatory goal met"
    elif goals_met > 0:
        level, why = "partial", f"weighted share of goals met = {goals_met}"
    else:
        level, why = "not_fulfilled", "no goal met"
    if log:
        log(f"constraints_ok={c_ok}  integrity_ok={i_ok}")
        log(f"LEVEL {level}: {why}")
    return {"level": level, "goals_met": goals_met if level != "fulfilled" else 1, "constraints_ok": c_ok, "integrity_ok": i_ok}, met


def base_record(case, L, unit, state, outcome, tier, reason, evidence, snapshot, bundle, occurred, recorded, supersedes):
    return {
        "record_id": L.next_id(), "work_unit": unit, "tenant_chain": case.TENANT_CHAIN,
        "contract_version": case.CONTRACT, "decider_bundle": bundle, "evidence": evidence,
        "input_snapshot": snapshot, "state": state, "outcome": outcome, "decided_by": tier,
        "reason": reason, "occurred_at": fmt(occurred), "recorded_at": fmt(recorded),
        "supersedes": supersedes, "prev_hash": "",
    }


def write(L, rec, indent=1):
    """Append a record and print it, or print why the ledger refused it."""
    try:
        L.append(rec)
    except LedgerError as e:
        say(indent, f"LEDGER REFUSED: {e}")
        return None
    say(indent, f"LEDGER APPEND {rec['record_id']} (prev_hash = sha256 of the previous record in this chain)")
    say(indent + 1, json.dumps(rec, indent=2))
    return rec


def cmd_run(a):
    case = load_case(a.case)
    L = ledger_for(case)
    t1, t2 = deciders.make(a.t1), deciders.make(a.t2)
    bundle = bundle_hash(case, t1, t2)
    now = iso(a.now)
    say(0, f"CASE {case.name}: {case.spec['planned_task'].strip()}")
    say(0, f"decider bundle {bundle}")
    say(1, f"= hash of spec {case.spec['spec_version']}, T1 {t1.name}:{t1.pinned}, T2 {t2.name}:{t2.pinned}, band, prices")
    for unit, sub in case.submissions():
        if L.head(unit):
            say(0, f"\n{unit}: already in the ledger, skipped (oa.py reset {case.name} to start over)")
            continue
        print("\n" + "━" * 100)
        say(0, f"WORK UNIT {unit}   ({sub.name})")
        passed_facts, answers, trace, tier, ev = decide(case, sub, t1, t2)
        passed = {k: v[0] for k, v in passed_facts.items()}
        say(1, "┌─ OUTCOME: combine facts and accepted answers against the spec")
        for k, p in answers.items():
            say(2, f"{k:<4} p={p:.2f} vs threshold {threshold(case.spec, k)} -> {'pass' if p >= threshold(case.spec, k) else 'FAIL'}")
        passed.update({k: p >= threshold(case.spec, k) for k, p in answers.items()})
        outcome, _ = outcome_of(case.spec, passed, lambda t: say(2, t))
        for k, p in answers.items():
            outcome[f"p_{k}"] = round(p, 4)
        say(1, "└─")
        ev_hash = L.put_blob(ev)
        trace_hash = L.put_blob(trace)
        snap = L.put_blob({"state": {"planned_task": case.spec["planned_task"].strip(), **ev}, "questions": questions(case.spec, set(trace["t0"]))})
        say(1, f"EVIDENCE stored by content hash: document {ev_hash[:23]}…, decision trace {trace_hash[:23]}…, input snapshot {snap[:23]}…")
        failed = sorted(k for k, v in passed.items() if not v)
        if trace["t3"]:
            state, reason = "attempted", f"awaiting human panel on {trace['t3']}"
        else:
            state, reason = "provisional", ("all checks passed" if not failed else f"failed: {failed}")
        rec = base_record(case, L, unit, state, outcome, tier, reason, [ev_hash, trace_hash], snap, bundle, now, now + dt.timedelta(seconds=1), None)
        write(L, rec)
        say(1, f"RESULT {state} {outcome['level']} by {tier}: {reason}")


def cmd_event(a):
    case = load_case(a.case)
    L = ledger_for(case)
    head = L.head(a.unit)
    at = iso(a.at)
    say(0, f"EVENT {a.type} on {a.unit} at {a.at}; current head {head['record_id']} ({head['state']}, {head['outcome']['level']})")
    ev = L.put_blob({"event": a.type, "work_unit": a.unit, "at": a.at})
    (L.root / "events.jsonl").open("a").write(json.dumps({"unit": a.unit, "type": a.type, "at": a.at}) + "\n")
    if a.type == "accepted":
        say(1, "corroborating evidence only: nothing is written; the unit still matures when its window closes")
        return
    if a.type == "dispute":
        state, outcome, tier, reason = "disputed", head["outcome"], head["decided_by"], "dispute raised"
        say(1, "a dispute freezes the unit until a panel rules (oa.py rule)")
    else:
        state, tier, reason = "final", "tier_0", f"late evidence: {a.type} at {a.at}"
        outcome = {"level": "not_fulfilled", "goals_met": 0, "constraints_ok": True, "integrity_ok": True}
        say(1, "contrary late evidence is a Tier 0 fact: it supersedes the decision with not_fulfilled")
    rec = base_record(case, L, a.unit, state, outcome, tier, reason, [ev], head["input_snapshot"], head["decider_bundle"],
                      at, at + dt.timedelta(seconds=3), head["record_id"])
    write(L, rec)


def cmd_rule(a):
    """Tier 3 human panel: rule on specific questions and re-derive the outcome."""
    case = load_case(a.case)
    L = ledger_for(case)
    head = L.head(a.unit)
    first = next(r for r in L.records if r["work_unit"] == a.unit)
    trace = L.get_blob(first["evidence"][1])
    passed = {k: v["ok"] for k, v in trace["t0"].items()}
    for t in ("t1", "t2"):
        if trace[t]:
            passed.update({k: p >= threshold(case.spec, k) for k, p in trace[t]["answers"].items()})
    rulings = dict(r.split("=") for r in a.rulings)
    say(0, f"PANEL RULING on {a.unit} (head {head['record_id']}, {head['state']}): {rulings}")
    say(1, f"pass or fail per check before the ruling: {passed}")
    passed.update({k: v == "yes" for k, v in rulings.items()})
    outcome, _ = outcome_of(case.spec, passed, lambda t: say(1, t))
    state = "adjudicated" if head["state"] == "disputed" else "provisional"
    at = iso(a.at)
    ev = L.put_blob({"panel": a.unit, "rulings": rulings, "at": a.at})
    rec = base_record(case, L, a.unit, state, outcome, "tier_3", f"panel ruled {rulings}", [ev] + head["evidence"], head["input_snapshot"],
                      head["decider_bundle"], at, at, head["record_id"])
    write(L, rec)


def cmd_mature(a):
    case = load_case(a.case)
    L = ledger_for(case)
    now = iso(a.now)
    window = max(duration(m["window"]) for m in case.spec["matured_criteria"]) if case.spec["matured_criteria"] else dt.timedelta(0)
    say(0, f"MATURE at {a.now}: window {window.days} days from session close ({', '.join(m['check'] for m in case.spec['matured_criteria'])})")
    for unit in L.units():
        head = L.head(unit)
        if head["state"] != "provisional":
            say(1, f"{unit}: head is {head['state']}, not provisional; nothing to mature")
            continue
        closes = iso(next(r for r in L.records if r["work_unit"] == unit)["occurred_at"]) + window
        if now < closes:
            say(1, f"{unit}: window open until {fmt(closes)}")
            continue
        say(1, f"{unit}: window closed {fmt(closes)} with no contrary evidence")
        rec = base_record(case, L, unit, "matured", head["outcome"], head["decided_by"], f"window {window.days}d closed without contrary evidence",
                          head["evidence"], head["input_snapshot"], head["decider_bundle"], closes, now, head["record_id"])
        write(L, rec, 2)


def price(case, outcome):
    """The contract's pricing function: rate x q(level, goals met) x AI work share, or a credit if harmful."""
    tc = case.spec["task_class"]
    lvl = outcome["level"]
    share = outcome.get("ai_work_share", 1.0)
    if lvl == "harmful":
        return -case.HARM_CREDIT[tc], f"harmful -> credit {case.HARM_CREDIT[tc]}"
    q = 1 if lvl == "fulfilled" else outcome["goals_met"] if lvl == "partial" else 0
    return round(case.RATE[tc] * q * share, 2), f"rate {case.RATE[tc]} x q {q} x share {share}"


def cmd_invoice(a):
    case = load_case(a.case)
    L = ledger_for(case)
    now = iso(a.now)
    inv_dir = L.root / "invoices"
    inv_dir.mkdir(exist_ok=True)
    billed = {}
    for f in sorted(inv_dir.glob("*.json")):
        for line in json.loads(f.read_text())["lines"]:
            billed[line["work_unit"]] = line
    say(0, f"INVOICE period {a.period}: only matured, adjudicated or final records are billable")
    lines = []
    for unit in L.units():
        head = L.head(unit)
        prior = billed.get(unit)
        if head["state"] in ("matured", "adjudicated"):
            say(1, f"{unit}: {head['state']} -> settle as final")
            fin = base_record(case, L, unit, "final", head["outcome"], head["decided_by"], f"settled in {a.period} period close",
                              head["evidence"], head["input_snapshot"], head["decider_bundle"], now, now, head["record_id"])
            head = write(L, fin, 2) or head
        if head["state"] != "final":
            say(1, f"{unit}: {head['state']}, not billable yet")
            continue
        amount, how = price(case, head["outcome"])
        if prior and prior["record_id"] == head["record_id"]:
            say(1, f"{unit}: already billed on {prior['record_id']}")
            continue
        if prior:
            delta = round(amount - prior["amount"], 2)
            say(1, f"{unit}: was billed {prior['amount']} on {prior['record_id']}, now {amount} -> adjustment {delta}")
            if delta:
                lines.append({"work_unit": unit, "record_id": head["record_id"], "kind": "adjustment", "amount": delta,
                              "for_period": prior["period"], "why": f"{head['reason']} (supersedes billed {prior['record_id']})"})
            continue
        say(1, f"{unit}: {head['outcome']['level']} decided by {head['decided_by']} -> {how} = {amount}")
        if amount:
            lines.append({"work_unit": unit, "record_id": head["record_id"], "kind": "charge" if amount > 0 else "credit", "amount": amount,
                          "level": head["outcome"]["level"], "decided_by": head["decided_by"], "evidence": head["evidence"][0]})
    for ln in lines:
        ln.setdefault("period", a.period)
    total = round(sum(l["amount"] for l in lines), 2)
    inv = {"payment_request": f"pr_{case.name}_{a.period}_{len(list(inv_dir.glob('*.json'))) + 1}", "payer": case.TENANT_CHAIN[-1],
           "payee": case.TENANT_CHAIN[1], "period": a.period, "currency": case.CURRENCY, "lines": lines, "total": total,
           "ledger_roots": L.roots(), "issued_at": fmt(now)}
    path = inv_dir / f"{inv['payment_request']}.json"
    path.write_text(json.dumps(inv, indent=2))
    say(0, f"PAYMENT REQUEST {inv['payment_request']}: {inv['payee']} asks {inv['payer']} for {total} {case.CURRENCY}")
    say(1, json.dumps(inv, indent=2))
    say(0, f"written to {path.relative_to(SANDBOX.parent)}")


def cmd_show(a):
    case = load_case(a.case)
    L = ledger_for(case)
    for unit in L.units():
        h = L.head(unit)
        chain = [f"{r['record_id']}:{r['state']}" for r in L.records if r["work_unit"] == unit]
        say(0, f"{unit:<32} {h['outcome']['level']:<14} {h['decided_by']:<7} {' -> '.join(chain)}")


def cmd_verify(a):
    L = ledger_for(load_case(a.case))
    breaks = L.verify()
    say(0, "chain intact: every prev_hash matches the record before it" if not breaks else "\n".join(breaks))
    for k, v in L.roots().items():
        say(1, f"root {k}: {v}")


def cmd_replay(a):
    case = load_case(a.case)
    L = ledger_for(case)
    first = next(r for r in L.records if r["work_unit"] == a.unit)
    trace = L.get_blob(first["evidence"][1])
    snap = L.get_blob(first["input_snapshot"])
    if not trace["t1"]:
        sys.exit(f"{a.unit} was decided at Tier 0; there is no model call to replay")
    t1 = deciders.make(a.t1)
    state = snap["state"]
    qs = {k: v for k, v in snap["questions"].items() if k in trace["t1"]["answers"]}
    orig = trace["t1"]["answers"]
    say(0, f"REPLAY {a.unit}: re-ask {t1.name} the same questions on the stored input snapshot {first['input_snapshot'][:23]}…")
    say(1, "original answers: " + ", ".join(f"{k}={v:.2f}" for k, v in orig.items()))
    say(1, "Δp = replayed p minus original p; a flip is a Δp that crosses the pass threshold and changes the decision")
    for i in range(a.times):
        r = t1.ask(state, qs)
        flips = [k for k in qs if (r["answers"][k] >= threshold(case.spec, k)) != (orig[k] >= threshold(case.spec, k))]
        say(1, f"run {i + 1} ({r['served_model']}): " + ", ".join(f"{k}={r['answers'][k]:.2f} (Δ{r['answers'][k] - orig[k]:+.2f})" for k in qs)
            + f"   flips: {flips or 'none'}")


def cmd_reset(a):
    path = ledger_for(load_case(a.case)).root
    shutil.rmtree(path)
    say(0, f"removed {path.relative_to(SANDBOX.parent)}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="cmd", required=True)
    r = s.add_parser("run", help="judge every submission not yet in the ledger")
    r.add_argument("case"); r.add_argument("--t1", default="jev"); r.add_argument("--t2", default="claude-sonnet"); r.add_argument("--now", default="2026-10-05T12:00:00Z")
    e = s.add_parser("event", help="something happens later in the real world")
    e.add_argument("case"); e.add_argument("unit"); e.add_argument("type", choices=["accepted", "material_edit", "revert", "reopen", "dispute"]); e.add_argument("--at", default="2026-10-06T12:00:00Z")
    ru = s.add_parser("rule", help="Tier 3 human panel rules on questions")
    ru.add_argument("case"); ru.add_argument("unit"); ru.add_argument("rulings", nargs="+", metavar="question=yes|no"); ru.add_argument("--at", default="2026-10-07T12:00:00Z")
    m = s.add_parser("mature", help="close maturation windows"); m.add_argument("case"); m.add_argument("--now", required=True)
    i = s.add_parser("invoice", help="turn final records into a payment request")
    i.add_argument("case"); i.add_argument("--period", required=True); i.add_argument("--now", required=True)
    for n, h in (("show", "list work units and their record history"), ("verify", "recompute the hash chains"), ("reset", "delete this case's ledger and invoices")):
        s.add_parser(n, help=h).add_argument("case")
    rp = s.add_parser("replay", help="re-ask Tier 1 on a stored snapshot")
    rp.add_argument("case"); rp.add_argument("unit"); rp.add_argument("--times", type=int, default=3); rp.add_argument("--t1", default="jev")
    a = p.parse_args()
    try:
        globals()[f"cmd_{a.cmd}"](a)
    except RuntimeError as e:
        sys.exit(f"error: {e}")


if __name__ == "__main__":
    main()
