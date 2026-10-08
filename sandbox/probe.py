# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Stigg
"""Known-answer probes against the single-pass decider, with a visible enrichment ladder.

    python sandbox/probe.py sandbox/probes/nda.yaml [--only id,id] [--repeats N]

For every probe: send the exact request to the decider N times, print each response,
classify each p against the certainty band, and if uncertain climb
criteria -> focus -> decompose. Writes an HTML report and raw JSON to sandbox/out/probes/.
"""
import argparse, html, json, pathlib, sys
import yaml

SANDBOX = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(SANDBOX))
from deciders import jev_request as call_jev  # noqa: E402


def band_of(p, band):
    return "YES" if p >= band["yes_min"] else "NO" if p <= band["no_max"] else "UNCERTAIN"


def bar(ps, band, width=50):
    """0 ........|....................|........ 1   with one mark per repeat."""
    cells = ["·"] * (width + 1)
    cells[round(band["no_max"] * width)] = "|"
    cells[round(band["yes_min"] * width)] = "|"
    for p in ps:
        cells[round(p * width)] = "●"
    return "0 " + "".join(cells) + " 1"


def say(indent, text=""):
    for line in str(text).splitlines() or [""]:
        print("   " * indent + line)


def run_step(cfg, name, state, questions, combine=None, why=""):
    """One rung of the ladder: N repeats of one request, logged in full."""
    band = cfg["band"]
    say(1, f"┌─ STEP {name}" + (f": {why}" if why else ""))
    body = {"state": state, "model": cfg["model"], "questions": questions}
    say(2, "REQUEST  POST https://api.typesafe.ai/v1/systemone  (identical for every repeat)")
    say(3, json.dumps(body, indent=2, ensure_ascii=False))
    if combine:
        rule = "min of sub-answers (every one must be yes)" if combine == "all" else "max of sub-answers (one yes is enough)"
        say(2, f"COMBINE  {combine}: p = {rule}")
    ps, served, lat, subs = [], set(), [], []
    for i in range(cfg["repeats"]):
        _, resp, ms = call_jev(cfg["model"], state, questions)
        served.add(resp["model"]); lat.append(ms)
        answers = {k: a["noul"] for k, a in resp["answers"].items()}
        if combine == "all":
            p = min(answers.values())
        elif combine == "any":
            p = max(answers.values())
        else:
            p = answers["q"]
        ps.append(p); subs.append(answers)
        derived = "" if not combine else f"  -> {combine}({', '.join(f'{v:.2f}' for v in answers.values())}) = {p:.2f}"
        say(2, f"RESPONSE #{i + 1} ({ms} ms): {json.dumps(resp, separators=(',', ':'))}{derived}")
        say(3, f"p={p:.2f} -> {band_of(p, band)}  ({'>= ' + str(band['yes_min']) if p >= band['yes_min'] else '<= ' + str(band['no_max']) if p <= band['no_max'] else 'between ' + str(band['no_max']) + ' and ' + str(band['yes_min'])})")
    bands = [band_of(p, band) for p in ps]
    verdict = bands[0] if len(set(bands)) == 1 else "UNSTABLE"
    say(2, f"SPREAD   {bar(ps, band)}   min {min(ps):.2f}  max {max(ps):.2f}  range {max(ps) - min(ps):.2f}")
    if verdict == "UNSTABLE":
        say(2, f"VERDICT  UNSTABLE: repeats disagree ({', '.join(bands)}); identical request, different answers")
    else:
        say(2, f"VERDICT  {verdict}: all {cfg['repeats']} repeats agree")
    say(2, f"SERVED   {', '.join(sorted(served))}   latency p50 {sorted(lat)[len(lat) // 2]} ms")
    say(1, "└─")
    return {"step": name, "request": body, "ps": ps, "subs": subs, "verdict": verdict, "served": sorted(served), "latency_ms": lat}


def noul(instructions, criteria=None):
    q = {"type": "noul", "instructions": instructions}
    if criteria:
        q["criteria"] = criteria
    return q


def run_probe(cfg, pr):
    qtext = cfg["questions"][pr["question"]]
    enrich = pr.get("enrich", {})
    print(f"\n{'━' * 100}")
    say(0, f"PROBE {pr['id']}")
    say(1, f"question key : {pr['question']}")
    say(1, f"question     : {qtext}")
    say(1, f"expected     : {pr['expect'].upper()}   because: {pr['why']}")
    say(1, f"enrichment   : {', '.join(enrich) if enrich else 'none defined (if uncertain -> Tier 2 / human)'}")
    say(1, "evidence (state) given to the decider:")
    say(2, pr["state"].rstrip())
    steps = [run_step(cfg, "plain", pr["state"], {"q": noul(qtext)}, why="the question as written in the probe file, no enrichment")]
    ladder = []
    if "criteria" in enrich:
        ladder.append(lambda: run_step(cfg, "+criteria", pr["state"], {"q": noul(qtext, enrich["criteria"])},
                                       why="same evidence, question now carries Jev's true/false definitions"))
    if "focus" in enrich:
        ladder.append(lambda: run_step(cfg, "+focus", enrich["focus"], {"q": noul(qtext, enrich.get("criteria"))},
                                       why="evidence narrowed to the relevant excerpt only"))
    if "decompose" in enrich:
        d = enrich["decompose"]
        ladder.append(lambda: run_step(cfg, f"decompose({d['combine']})", enrich.get("focus", pr["state"]),
                                       {k: noul(v) for k, v in d["questions"].items()}, d["combine"],
                                       why="split into atomic yes/no questions, combined in code"))
    for step in ladder:
        last = steps[-1]["verdict"]
        if last in ("YES", "NO"):
            say(1, f"LADDER   stop: {steps[-1]['step']} is certain ({last})")
            break
        say(1, f"LADDER   {steps[-1]['step']} was {last} -> climb to next enrichment")
        steps.append(step())
    else:
        if steps[-1]["verdict"] not in ("YES", "NO"):
            say(1, f"LADDER   exhausted at {steps[-1]['step']} ({steps[-1]['verdict']}) -> would escalate to Tier 2 / human panel")
    final = steps[-1]["verdict"]
    expected = pr["expect"].upper()
    status = "PASS" if final == expected else "WRONG" if final in ("YES", "NO") else "UNRESOLVED"
    mark = {"PASS": "✅", "WRONG": "❌", "UNRESOLVED": "⚠️ "}[status]
    say(1, f"RESULT   {mark} {status}: expected {expected}, got {final}" + (f" at step {steps[-1]['step']}" if final in ("YES", "NO") else ""))
    if status == "WRONG":
        say(1, "         certain but incorrect: in production the router would accept this without escalation, and the price would be computed from a wrong fact")
    return {"probe": pr, "question": qtext, "steps": steps, "final": final, "status": status,
            "resolved_by": steps[-1]["step"] if final in ("YES", "NO") else None}


def report_html(cfg, results, path):
    def svg(ps):
        w, h = 260, 22
        x = lambda p: 6 + p * (w - 12)
        marks = "".join(f'<circle cx="{x(p):.1f}" cy="11" r="4.5" class="dot"/>' for p in ps)
        return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="p values">'
                f'<rect x="{x(0)}" y="9" width="{x(cfg["band"]["no_max"]) - x(0):.1f}" height="4" class="no"/>'
                f'<rect x="{x(cfg["band"]["no_max"]):.1f}" y="9" width="{x(cfg["band"]["yes_min"]) - x(cfg["band"]["no_max"]):.1f}" height="4" class="mid"/>'
                f'<rect x="{x(cfg["band"]["yes_min"]):.1f}" y="9" width="{x(1) - x(cfg["band"]["yes_min"]):.1f}" height="4" class="yes"/>'
                f"{marks}</svg>")
    rows = []
    for r in results:
        pr = r["probe"]
        steps = "".join(
            f'<div class="step"><span class="sn">{html.escape(s["step"])}</span>{svg(s["ps"])}'
            f'<span class="v v-{s["verdict"]}">{s["verdict"]}</span><span class="ps">{", ".join(f"{p:.2f}" for p in s["ps"])}</span>'
            f'<details><summary>request sent</summary><pre>{html.escape(json.dumps(s["request"], indent=2, ensure_ascii=False))}</pre></details></div>'
            for s in r["steps"])
        rows.append(f'<section class="probe"><header><h2>{html.escape(pr["id"])}</h2><span class="st st-{r["status"]}">{r["status"]}</span>'
                    f'<span class="exp">expect <b>{pr["expect"].upper()}</b></span></header>'
                    f'<p class="why">{html.escape(pr["why"])}</p><p class="q">Q: {html.escape(r["question"])}</p>'
                    f'<pre class="state">{html.escape(pr["state"].strip())}</pre>{steps}</section>')
    counts = {k: sum(r["status"] == k for r in results) for k in ("PASS", "WRONG", "UNRESOLVED")}
    plain_certain = sum(r["steps"][0]["verdict"] in ("YES", "NO") for r in results)
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Jev Probe Report</title><style>
:root{{--bg:#fafaf9;--fg:#1c1917;--mut:#78716c;--card:#fff;--line:#e7e5e4;--yes:#15803d;--no:#b91c1c;--mid:#d6d3d1;--dot:#1c1917;--warn:#b45309}}
@media (prefers-color-scheme:dark){{:root{{--bg:#1c1917;--fg:#f5f5f4;--mut:#a8a29e;--card:#292524;--line:#44403c;--yes:#4ade80;--no:#f87171;--mid:#57534e;--dot:#f5f5f4;--warn:#fbbf24}}}}
body{{background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif;margin:0;padding:24px 16px}}
main{{max-width:900px;margin:0 auto}} h1{{font-size:22px;margin:0 0 4px}} .sub{{color:var(--mut);margin:0 0 20px}}
.probe{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:0 0 14px}}
header{{display:flex;gap:10px;align-items:center;flex-wrap:wrap}} h2{{font-size:16px;margin:0;font-family:ui-monospace,monospace}}
.st{{font-size:12px;font-weight:700;padding:2px 8px;border-radius:99px;border:1px solid}} .st-PASS{{color:var(--yes)}} .st-WRONG{{color:var(--no)}} .st-UNRESOLVED{{color:var(--warn)}}
.exp{{color:var(--mut);font-size:13px}} .why,.q{{margin:6px 0;font-size:14px}} .why{{color:var(--mut)}}
pre{{white-space:pre-wrap;word-break:break-word;font:12.5px/1.45 ui-monospace,monospace;background:var(--bg);border:1px solid var(--line);border-radius:6px;padding:8px;margin:6px 0}}
.step{{display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px;border-top:1px dashed var(--line);padding:6px 0}}
.sn{{font:13px ui-monospace,monospace;min-width:120px}} .ps{{color:var(--mut);font:12.5px ui-monospace,monospace}}
.v{{font-weight:700;font-size:12px;min-width:84px}} .v-YES{{color:var(--yes)}} .v-NO{{color:var(--no)}} .v-UNCERTAIN,.v-UNSTABLE{{color:var(--warn)}}
details{{flex-basis:100%}} summary{{cursor:pointer;color:var(--mut);font-size:12.5px}}
svg .yes{{fill:var(--yes);opacity:.5}} svg .no{{fill:var(--no);opacity:.5}} svg .mid{{fill:var(--mid)}} svg .dot{{fill:var(--dot);opacity:.6}}
</style></head><body><main><h1>Jev probe report</h1>
<p class="sub">{len(results)} probes · {cfg['repeats']} repeats each · band NO ≤ {cfg['band']['no_max']} &lt; uncertain &lt; {cfg['band']['yes_min']} ≤ YES ·
{counts['PASS']} pass, {counts['WRONG']} wrong, {counts['UNRESOLVED']} unresolved · {plain_certain}/{len(results)} certain without enrichment</p>
{''.join(rows)}</main></body></html>"""
    path.write_text(doc)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("probes")
    ap.add_argument("--only")
    ap.add_argument("--repeats", type=int)
    a = ap.parse_args()
    path = pathlib.Path(a.probes)
    cfg = yaml.safe_load(path.read_text())
    if a.repeats:
        cfg["repeats"] = a.repeats
    probes = [p for p in cfg["probes"] if not a.only or p["id"] in a.only.split(",")]
    for p in probes:  # YAML reads bare yes/no as booleans
        p["expect"] = {True: "yes", False: "no"}.get(p["expect"], p["expect"])
    print(f"band: NO <= {cfg['band']['no_max']} < UNCERTAIN < {cfg['band']['yes_min']} <= YES   repeats: {cfg['repeats']}   model: {cfg['model']}")
    results = []
    for pr in probes:
        r = run_probe(cfg, pr)
        results.append(r)
    print(f"\n{'━' * 100}\nSUMMARY")
    print(f"   {'probe':<30} {'expect':<7} {'ladder':<62} result")
    for r in results:
        ladder = " -> ".join(f"{s['step']}:{s['verdict']}" for s in r["steps"])
        print(f"   {r['probe']['id']:<30} {r['probe']['expect'].upper():<7} {ladder:<62} {r['status']}")
    counts = {k: sum(r["status"] == k for r in results) for k in ("PASS", "WRONG", "UNRESOLVED")}
    plain = sum(r["steps"][0]["verdict"] in ("YES", "NO") for r in results)
    print(f"\n   {counts['PASS']} pass · {counts['WRONG']} wrong · {counts['UNRESOLVED']} unresolved · {plain}/{len(results)} certain with the plain question")
    out_dir = SANDBOX / "out" / "probes"
    out_dir.mkdir(parents=True, exist_ok=True)
    report_html(cfg, results, out_dir / f"{path.stem}.report.html")
    (out_dir / f"{path.stem}.results.json").write_text(json.dumps(results, indent=1, default=str))
    print(f"   report: {(out_dir / f'{path.stem}.report.html').relative_to(SANDBOX.parent)}")
    print(f"   raw:    {(out_dir / f'{path.stem}.results.json').relative_to(SANDBOX.parent)}")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        sys.exit(f"error: {e}")
