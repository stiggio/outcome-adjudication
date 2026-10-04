# FAQ

**Is this a product?**
No. It is a specification and a research program. No implementation code is published yet.

**Why not just price per conversation or per token?**
Those meters are easy to count and easy to trust, which is why most of the market uses them. They also stop tracking value once agents complete work end to end. This project asks what it would take to price the work itself without either side having to trust the other's meter.

**How is this different from LLM-as-a-judge?**
A single judge is one tier of four. Facts from systems of record override it, a calibrated fast decider handles most cases, the judge handles grey zones, and humans settle disputes. The judge never sees the agent's own claims of success.

**Who decides what counts as success?**
Both parties, before work starts, through a success specification compiled from the planned task and a frozen, jointly labeled evaluation set.

**What happens when an outcome is reversed later?**
The maturation clock re-decides it. The ledger writes a new record that supersedes the old one, and any provisional charge reverses as a credit.

**How can I help?**
See [CONTRIBUTING.md](../CONTRIBUTING.md), or email hello@stigg.io.
