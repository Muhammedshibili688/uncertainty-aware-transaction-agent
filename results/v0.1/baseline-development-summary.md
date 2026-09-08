# Baseline Development Results

## Experiment information

- Dataset version: v0.1
- Split: DEVELOPMENT
- Number of cases: 10
- Policy: baseline_static_v0.1
- Verification available: No
- Maximum risk score: 6
- Approval range: 0–1
- Human-review range: 2–3
- Stop range: 4–6

## Purpose

I started with a static baseline using amount, device/location context and
recent velocity. This gave me a simple comparison point before adding
verification or probability-based reasoning.

## Results

| Measurement | Result |
|---|---:|
| Total cases | 10 |
| Approved | 3 |
| Human review | 5 |
| Stopped | 2 |
| Automatic decisions | 5 |
| Correct automatic decisions | 4 |
| Automatic coverage | 50% |
| Automatic accuracy | 80% |
| Human-review rate | 50% |
| False approvals | 1 |
| False stops | 0 |
| Fraud recall | 66.7% |

Automatic accuracy was calculated using only APPROVE and STOP
decisions. HUMAN_REVIEW cases were counted as deferred rather than
correct.

## Correct automatic decisions

| Case | Action | True state | Observation |
|---|---|---|---|
| CASE-005 | STOP | FRAUDULENT | Multiple strong warning signals produced a high score. |
| CASE-006 | APPROVE | LEGITIMATE | All initial evidence appeared normal. |
| CASE-007 | STOP | FRAUDULENT | High velocity and unfamiliar device context produced a high score. |
| CASE-009 | APPROVE | LEGITIMATE | All initial evidence appeared normal. |

## Incorrect automatic decision

| Case | Action | True state | Failure |
|---|---|---|---|
| CASE-008 | APPROVE | FRAUDULENT | Familiar-context fraud produced the same initial evidence as ordinary legitimate behaviour. |

## Cases sent to human review

| Case | True state | Reason for review |
|---|---|---|
| CASE-001 | LEGITIMATE | Moderate amount and unusual location produced score 2. |
| CASE-002 | LEGITIMATE | New device and unusual location produced score 2. |
| CASE-003 | LEGITIMATE | High amount and unusual location produced score 3. |
| CASE-004 | LEGITIMATE | High velocity produced score 2. |
| CASE-010 | LEGITIMATE | Missing history and new-device context produced score 3. |

## Main strengths

- The baseline stopped the two clear fraud cases.
- It did not automatically stop any legitimate case.
- Its decisions were easy to reproduce and explain.
- It handled missing evidence conservatively.

## Main limitations

- Half of the cases required human review.
- Five of the seven legitimate cases were sent for review.
- Familiar-context fraud was approved when every initial signal looked normal.
- The additive score may double-count signals that share the same cause.
- The score is a risk index, not a calibrated fraud probability.

## Important edge cases

### Familiar-context fraud

CASE-008 received a score of zero because its amount, device/location
context, and velocity all appeared normal. The case demonstrates that
normal-looking evidence does not guarantee legitimacy.

### Correlated legitimate signals

CASE-001 and CASE-002 show that multiple unusual signals can come from
one legitimate event, such as a celebration or travel.

### Legitimate high velocity

CASE-004 was sent for review because of rapid activity even though the
shopping sequence was genuine.

### Missing information

CASE-010 was sent for review because missing evidence was assigned one
risk point instead of being treated as safe.

## Baseline conclusion

The baseline is useful as a realistic comparison system. It catches
clear fraud without false stops, but creates substantial human-review
work and cannot detect fraud that looks identical to familiar
legitimate behaviour.

The baseline will now be frozen before Policy 1 is designed.
