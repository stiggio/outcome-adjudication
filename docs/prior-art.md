# Prior art

Work this project builds on. Additions are welcome via the *prior art* issue template.

## Evaluating agents and judges
- [AgentRewardBench](https://arxiv.org/abs/2504.08942): expert-annotated benchmark showing LLM judges reach roughly 70% precision on web-agent trajectories while rule-based checks undercount successes.
- [ImpossibleBench](https://arxiv.org/pdf/2510.20270): tasks that can only be passed by cheating; frontier models exploit tests, and isolating tests cuts cheating sharply.
- [SpecBench](https://arxiv.org/pdf/2605.21384): long-horizon reward hacking in coding agents.
- [EvilGenie](https://arxiv.org/pdf/2511.21654): a reward hacking benchmark; holdout tests are not foolproof.
- [Agent-assisted pull requests (arXiv 2509.14745)](https://arxiv.org/abs/2509.14745): merged is not the same as merged unmodified.

## Determinism and replay
- [Why temperature zero is not deterministic](https://zansara.substack.com/p/setting-the-temperature-to-zero-will)
- [Batch-invariant inference in practice](https://www.morphllm.com/defeating-nondeterminism-llm-inference)

## Accounting and adoption
- [Deloitte DART: accounting for outcome-based pricing in agentic AI (June 2026)](https://dart.deloitte.com/USDART/home/publications/deloitte/industry/technology/accounting-outcome-based-pricing-agentic-ai)
- [CIO Dive on Gartner adoption data (Aug 2026)](https://www.ciodive.com/news/agentic-ai-outcome-pricing-models/829023/)

## Industries that already pay for outcomes
- [IPMVP](https://energy-data.io/standards/ipmvp/): measurement and verification of energy savings against an agreed baseline.
- [FERC Enerwise settlement](https://www.ferc.gov/sites/default/files/enforcement/civil-penalties/actions/143FERC61218.pdf): a gamed demand-response baseline.
- [MedPAC on ACO benchmarks](https://www.medpac.gov/wp-content/uploads/2021/09/aco-benchmarks-medpac-nov-2021.pdf): provisional versus final settlement, ratcheting baselines.
- [Peterborough Social Impact Bond evaluation](https://discovery-pp.ucl.ac.uk/id/eprint/10038372): a counterfactual built blind to outcomes by an independent assessor.
- [Telecom revenue assurance](https://www.pwc.com/ph/en/risk-assurance/risk-assurance-insights/optimizing-revenue-with-data-analytics-differentiate-with-data.html): stage-by-stage reconciliation.
