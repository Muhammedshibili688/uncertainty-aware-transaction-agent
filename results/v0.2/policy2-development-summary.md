# Policy 2 v0.2 Development Result

## Run boundary

The baseline, frozen Policy 1 and Policy 2 were compared on the same ten new
v0.2 DEVELOPMENT cases. The thirty v0.2 EVALUATION cases were not executed.

## Comparison

| Metric | Baseline | Policy 1 | Policy 2 |
|---|---:|---:|---:|
| Approved | 2 | 6 | 4 |
| Human review | 7 | 2 | 4 |
| Stopped | 1 | 2 | 2 |
| Verification requests | 0 | 7 | 7 |
| False approvals | 1 | 2 | 1 |
| False stops | 0 | 0 | 0 |
| Automatic coverage | 30.0% | 80.0% | 60.0% |
| Automatic accuracy | 66.7% | 75.0% | 83.3% |
| Human-review rate | 70.0% | 20.0% | 40.0% |
| Fraud recall | 25.0% | 50.0% | 50.0% |

Automatic accuracy excludes HUMAN_REVIEW. Risk values are points rather than
probabilities.

## Frozen success criteria

| Criterion | Result |
|---|---|
| Fewer false approvals than policy1 | PASS |
| False approvals not higher than baseline | PASS |
| False stops not higher than baseline | PASS |
| Human review lower than baseline | PASS |
| Independent pass can resolve legitimate score two | PASS |
| Unreliable pass never lowers risk | PASS |
| Verification only for scores two and three | PASS |
| Maximum one request per case | PASS |
| All final actions terminal | PASS |

## Policy 2 decisions

| Case | True state | Initial score | Verification | Independence | Final score | Final action |
|---|---|---:|---|---|---:|---|
| P2-001 | LEGITIMATE | 2 | PASS | INDEPENDENT | 1 | APPROVE |
| P2-002 | FRAUDULENT | 2 | PASS | SAME_CHANNEL | 2 | HUMAN_REVIEW |
| P2-003 | LEGITIMATE | 2 | PASS | SAME_CHANNEL | 2 | HUMAN_REVIEW |
| P2-004 | FRAUDULENT | 3 | FAIL | INDEPENDENT | 4 | STOP |
| P2-005 | LEGITIMATE | 3 | PASS | INDEPENDENT | 2 | HUMAN_REVIEW |
| P2-006 | LEGITIMATE | 0 | NOT_REQUESTED | NOT_REQUESTED | 0 | APPROVE |
| P2-007 | FRAUDULENT | 4 | NOT_REQUESTED | NOT_REQUESTED | 4 | STOP |
| P2-008 | LEGITIMATE | 2 | INCONCLUSIVE | UNKNOWN | 2 | HUMAN_REVIEW |
| P2-009 | FRAUDULENT | 1 | NOT_REQUESTED | NOT_REQUESTED | 1 | APPROVE |
| P2-010 | LEGITIMATE | 2 | PASS | INDEPENDENT | 1 | APPROVE |

## Conclusion

Policy 2 met every frozen development success criterion and is now frozen before evaluation.

SAME_CHANNEL and UNKNOWN PASS are deliberately treated as unresolved rather
than as proof of legitimacy. Low-score familiar-context fraud remains an
explicit limitation. Development success does not establish held-out
performance.
