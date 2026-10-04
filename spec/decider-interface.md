# Decider interface (draft)

Any decision model can fill the Tier 1 slot if it honors this contract. The interface is what makes the decider swappable without changing the definition of an outcome.

## Input
- **Questionnaire:** the judged criteria, constraints and integrity checks from a success spec, each with an `answer_type` of `choice`, `score` or `yes_no`.
- **Evidence view:** end state read with the evaluator's own credentials, diffs, actions and the user's requests. The agent's own claims of success are removed.

## Output
- **A calibrated distribution per question.** When the decider says 0.8, it should be right about 80% of the time on the frozen evaluation set.
- **Bundle hash:** the hash of base model, adapter, success spec, calibration map and thresholds.
- **Latency class:** the budget it meets (for example, under 500 ms at p99).
- **Calibration certificate:** measured calibration error and conformal coverage on the frozen evaluation set.

## Requirements
- **Replayable.** Re-running the bundle on a stored input snapshot reproduces the decision, or the ledger stores raw output scores as a fallback.
- **Independent.** Tier 2 must come from a different model family than the agent and Tier 1.
- **Barrier-respecting.** Billability outputs are never exposed to the working agent.

## Candidate classes for the v0.2 benchmark
1. Single-pass decision models that return typed answers with probabilities.
2. Small classifiers distilled from the Tier 2 judge.
3. Prompted LLMs with constrained output.
