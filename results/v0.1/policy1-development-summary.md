# Policy 1 Development Results

## Experiment information

- Dataset version: v0.1
- Split: DEVELOPMENT
- Cases: 10
- Policy: `policy1_step_up_v0.1`
- Initial evidence: amount deviation, device/location context, recent velocity
- Additional evidence: one step-up verification, only when requested

## Policy tested

Policy 1 preserves the baseline score. Scores zero to one are approved, scores
two to three request step-up verification, and scores four to six are stopped.
PASS subtracts one point, FAIL adds one point, and INCONCLUSIVE or UNAVAILABLE
leave the score unchanged. The original terminal thresholds are then applied.

These point changes are simulation assumptions, not calibrated probabilities.
PASS and FAIL are evidence rather than proof of the hidden state.

## Results

| Measurement | Policy 1 | Frozen baseline |
|---|---:|---:|
| Total cases | 10 | 10 |
| Approved | 6 | 3 |
| Human review | 2 | 5 |
| Stopped | 2 | 2 |
| Verification requests | 5 | 0 |
| Automatic decisions | 8 | 5 |
| Correct automatic decisions | 7 | 4 |
| False approvals | 1 | 1 |
| False stops | 0 | 0 |
| Automatic coverage | 80.0% | 50.0% |
| Automatic accuracy | 87.5% | 80.0% |
| Human-review rate | 20.0% | 50.0% |
| Fraud recall | 66.7% | 66.7% |

Automatic accuracy excludes HUMAN_REVIEW because review is a deferred action,
not a predicted hidden state.

## Case-level decisions

| Case | Initial score | Initial action | Verification observed | Final score | Final action | Hidden state |
|---|---:|---|---|---:|---|---|
| CASE-001 | 2 | GET_MORE_EVIDENCE | PASS | 1 | APPROVE | LEGITIMATE |
| CASE-002 | 2 | GET_MORE_EVIDENCE | PASS | 1 | APPROVE | LEGITIMATE |
| CASE-003 | 3 | GET_MORE_EVIDENCE | PASS | 2 | HUMAN_REVIEW | LEGITIMATE |
| CASE-004 | 2 | GET_MORE_EVIDENCE | PASS | 1 | APPROVE | LEGITIMATE |
| CASE-005 | 5 | STOP | NOT_REQUESTED | 5 | STOP | FRAUDULENT |
| CASE-006 | 0 | APPROVE | NOT_REQUESTED | 0 | APPROVE | LEGITIMATE |
| CASE-007 | 4 | STOP | NOT_REQUESTED | 4 | STOP | FRAUDULENT |
| CASE-008 | 0 | APPROVE | NOT_REQUESTED | 0 | APPROVE | FRAUDULENT |
| CASE-009 | 0 | APPROVE | NOT_REQUESTED | 0 | APPROVE | LEGITIMATE |
| CASE-010 | 3 | GET_MORE_EVIDENCE | PASS | 2 | HUMAN_REVIEW | LEGITIMATE |

## Interpretation

This development run tests one change only: replacing immediate human review
for score-two and score-three cases with one selective verification. The raw
decision CSV remains the authoritative case-level record. Any improvement is a
development finding and must not be described as held-out performance.

Policy 1 retains the known v0.1 limitation that familiar-context fraud can be
indistinguishable from legitimate behaviour when the initial evidence and
verification evidence look the same.
