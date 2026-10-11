# Sandbox

A runnable prototype of RFC 0001. It prints every step: what the decider gets, what it answers, and what lands in the ledger and on the invoice. Exploratory, not the reference implementation.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r sandbox/requirements.txt
export TYPESAFE_API_KEY=...      # for the Jev decider
```

Tier 2 uses the `claude` CLI ([Claude Code](https://claude.com/claude-code)), logged in.

## Try it

**1. Does the decider get it right?** Known-answer probes; each one is asked several times.

```bash
python sandbox/probe.py sandbox/probes/nda.yaml
```

Each answer `p` is the probability of YES. At or above 0.90 counts as a certain YES, at or below 0.10 as a certain NO, anything between as uncertain, which tries enrichment (definitions, a narrower excerpt, sub-questions). **WRONG** means certain but incorrect: in production that would be billed with no one checking.

**2. From agent output to invoice.** A legal agent drafted four NDAs and is paid $120 per good one.

```bash
python sandbox/oa.py run legal-nda                                    # judge the drafts
python sandbox/oa.py mature legal-nda --now 2026-10-12T13:00:00Z     # 7-day window closes
python sandbox/oa.py invoice legal-nda --period 2026-10 --now 2026-10-31T23:00:00Z
```

Then try `show`, `verify`, `replay <case> <unit>`, `event`, `rule` and `reset`. Run `python sandbox/oa.py -h` for the full list.

**3. Tests**, offline: `python -m pytest sandbox/tests`

## Next

- Add a probe: a new entry in `probes/nda.yaml`, with the expected answer written first.
- Add a case: copy `cases/legal-nda/`.
- Everything else (how each RFC concept maps to code, annotated walkthroughs, ledger rules, α, known limits) is in [GUIDE.md](GUIDE.md).
