# Baseline vs Policy 1: v0.1 Held-Out Evaluation

## Run boundary

Both frozen policies were run once on the same 30 EVALUATION cases. The agents
received only the three initial evidence categories. Policy 1 received a
step-up result only after requesting it, and the evaluator revealed the hidden
state only after each final action.

## Metric comparison

| Metric | Baseline | Policy 1 | Difference (Policy 1 - baseline) |
|---|---:|---:|---:|
| Approved | 11 | 14 | +3 |
| Human review | 10 | 6 | -4 |
| Stopped | 9 | 10 | +1 |
| Verification requests | 0 | 10 | +10 |
| Automatic decisions | 20 | 24 | +4 |
| Correct automatic decisions | 17 | 20 | +3 |
| False approvals | 3 | 4 | +1 |
| False stops | 0 | 0 | +0 |
| Automatic coverage | 66.7% | 80.0% | +13.3 percentage points |
| Automatic accuracy | 85.0% | 83.3% | -1.7 percentage points |
| Human-review rate | 33.3% | 20.0% | -13.3 percentage points |
| Verification-request rate | 0.0% | 33.3% | +33.3 percentage points |
| Fraud recall | 60.0% | 66.7% | +6.7 percentage points |
| Legitimate review rate | 46.7% | 33.3% | -13.3 percentage points |

Automatic accuracy excludes HUMAN_REVIEW because those decisions are deferred.
The risk score and its verification adjustments are points, not probabilities.

## Predeclared success criteria

| Criterion | Result |
|---|---|
| Policy 1 lowers human review | PASS |
| False approvals do not increase | FAIL |
| False stops do not increase | PASS |
| Verification is requested only for initial scores 2-3 | PASS |
| No case receives more than one verification | PASS |
| Every final action is terminal | PASS |

## Cases whose final action changed

| Case | True state | Baseline | Verification observed | Policy 1 |
|---|---|---|---|---|
| CASE-017 | LEGITIMATE | HUMAN_REVIEW | PASS | APPROVE |
| CASE-020 | LEGITIMATE | HUMAN_REVIEW | PASS | APPROVE |
| CASE-025 | FRAUDULENT | HUMAN_REVIEW | FAIL | STOP |
| CASE-030 | FRAUDULENT | HUMAN_REVIEW | PASS | APPROVE |

## Conclusion

Policy 1 is not better than the baseline under every frozen v0.1 success criterion. The failed criteria must be reported as evaluation findings rather than repaired using these same cases.

Policy 1 requested 10 automated checks.
This extra evidence cost is reported separately from human review rather than
being treated as free. These 30 cases are now used evaluation data and must not
be reused as unseen evidence for a modified policy.
