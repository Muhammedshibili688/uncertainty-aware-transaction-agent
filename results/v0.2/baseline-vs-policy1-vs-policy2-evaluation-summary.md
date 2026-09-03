# v0.2 Held-Out Evaluation: Baseline vs Policy 1 vs Policy 2

## Run boundary

All three frozen policies processed the same thirty v0.2 EVALUATION cases once.
The pre-evaluation policy and dataset hashes were verified before execution.
The baseline saw no verification. Policy 1 saw only a requested verification
result. Policy 2 saw a requested result and independence value. Hidden states
were used only after final actions.

## Metrics

| Metric | Baseline | Policy 1 | Policy 2 |
|---|---:|---:|---:|
| Approved | 7 | 18 | 13 |
| Human review | 19 | 7 | 12 |
| Stopped | 4 | 5 | 5 |
| Verification requests | 0 | 19 | 19 |
| Automatic decisions | 11 | 23 | 18 |
| Correct automatic decisions | 8 | 16 | 14 |
| False approvals | 3 | 7 | 4 |
| False stops | 0 | 0 | 0 |
| Automatic coverage | 36.7% | 76.7% | 60.0% |
| Automatic accuracy | 72.7% | 69.6% | 77.8% |
| Human-review rate | 63.3% | 23.3% | 40.0% |
| Fraud recall | 26.7% | 33.3% | 33.3% |

Automatic accuracy excludes HUMAN_REVIEW because review is deferred. Risk
values are points rather than calibrated probabilities.

## Frozen success criteria

| Criterion | Result |
|---|---|
| Fewer false approvals than policy1 | PASS |
| False approvals not higher than baseline | FAIL |
| False stops not higher than baseline | PASS |
| Human review lower than baseline | PASS |
| Independent pass can resolve legitimate score two | PASS |
| Unreliable pass never lowers risk | PASS |
| Verification only for scores two and three | PASS |
| Maximum one request per case | PASS |
| All final actions terminal | PASS |

## Policy 1 to Policy 2 action changes

| Case | True state | Policy 1 | Verification | Independence | Policy 2 |
|---|---|---|---|---|---|
| P2-013 | FRAUDULENT | APPROVE | PASS | SAME_CHANNEL | HUMAN_REVIEW |
| P2-016 | LEGITIMATE | APPROVE | PASS | SAME_CHANNEL | HUMAN_REVIEW |
| P2-021 | FRAUDULENT | APPROVE | PASS | SAME_CHANNEL | HUMAN_REVIEW |
| P2-026 | LEGITIMATE | APPROVE | PASS | SAME_CHANNEL | HUMAN_REVIEW |
| P2-035 | FRAUDULENT | APPROVE | PASS | SAME_CHANNEL | HUMAN_REVIEW |

## Policy 2 automatic errors

| Case | True state | Initial score | Verification | Independence | Action |
|---|---|---:|---|---|---|
| P2-019 | FRAUDULENT | 0 | NOT_REQUESTED | NOT_REQUESTED | APPROVE |
| P2-023 | FRAUDULENT | 1 | NOT_REQUESTED | NOT_REQUESTED | APPROVE |
| P2-029 | FRAUDULENT | 2 | PASS | INDEPENDENT | APPROVE |
| P2-033 | FRAUDULENT | 0 | NOT_REQUESTED | NOT_REQUESTED | APPROVE |

## Conclusion

Policy 2 failed at least one frozen held-out criterion and cannot be called better for the complete stated objective.

These cases are now used evaluation evidence. Policy 2 must not be changed and
rerun on them as though they were unseen. Any later change requires a new
version and new evaluation cases.
