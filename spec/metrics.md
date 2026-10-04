# Metric definitions (v0.1)

## α: the overbilling bound

The contracted upper bound on expected overbilling among decisions accepted without escalation. A decision overbills when a unit is billed as fulfilled, or at a higher grade, than the frozen, jointly labeled ground truth supports.

## Auto-decidable fraction, ADF(α)

The share of units decided at Tier 0 or Tier 1 while expected overbilling among those accepted decisions stays at or below α:

```
ADF(α) = units accepted at Tier 0 or Tier 1 / all units
         subject to  E[overbilling | accepted] ≤ α
```

Report ADF as a curve over α for each task class, measured on the frozen evaluation set.

## Calibration error

Expected calibration error of each judged criterion's probabilities against the frozen set, reported before and after per-tenant recalibration, with the binning scheme stated.

## Replay reproduction rate

The share of ledger records whose decision is reproduced exactly when the pinned decider bundle is re-run on the stored input snapshot.

## The frozen evaluation set

Jointly labeled by both contract parties, adjudicated blind to evaluator outputs, and frozen at contract signing. A new decider bundle is promoted only if it improves calibration error and the α bound on this set.
