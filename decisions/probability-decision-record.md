# Probability Decision Record

## Purpose and boundary

I worked through development case `P2-001` to show, step by step, how new
evidence could update a probability belief.

It does **not** convert the implemented 0–6 risk score into a probability. The
implemented score is an ordinal risk index. The probabilities, likelihoods,
costs and thresholds below are clearly labelled simulation assumptions because
this project does not have comparable production data for estimating them.

The case's simulated true state is hidden until the decision is finished.

## Case and audit data

| Audit item | Recorded value |
|---|---|
| Case | P2-001 — Independent confirmation for laptop |
| Decision date | 2026-09-04 |
| Data version | v0.2 DEVELOPMENT |
| Agent implementation | `src/agent.py` |
| Model version | `probability-example-v0.1` — manual simulation, no learned model |
| Policy reference | `policy2_reliability_aware_v0.2` |
| Repository commit used as reference | `72b3fbf` |
| Hidden label available to decision maker | No |

## Initial decision record

### Evidence observed

The customer is buying a work laptop for 72,000. Their usual amount range is
500–5,000. The transaction therefore has a `HIGH` amount deviation. It uses a
known device in the usual location and the recent transaction velocity is
normal.

| Initial evidence | Observed value |
|---|---|
| Amount deviation | HIGH |
| Device/location context | KNOWN_DEVICE_USUAL_LOCATION |
| Recent velocity | NORMAL |

The narrative description and true state are not given to the agent.

### Hidden states and prior belief

| Hidden state | Meaning | Prior belief |
|---|---|---:|
| LEGITIMATE | The account holder authorized the purchase | 70% |
| FRAUDULENT | The account holder did not authorize it | 30% |
| **Total** | | **100%** |

The 30% fraud belief is a judgement made for this worked example after seeing
the high amount together with otherwise familiar behaviour. It is not an
estimated population fraud rate.

### Available actions and simulated costs

Cost units are illustrative rather than currency.

| Action | If legitimate | If fraudulent | Interpretation |
|---|---:|---:|---|
| APPROVE | 0 | 100 | Fraud is allowed to proceed |
| GET_MORE_EVIDENCE | 2 | 2 | Delay and customer friction from one check |
| HUMAN_REVIEW | 10 | 10 | Analyst workload and decision delay |
| STOP | 25 | 0 | A real customer is incorrectly interrupted |

The highest cost is assigned to approving fraud. This expresses the project's
safety priority; it is not an industry-standard cost table.

### Illustrative probability policy

- If `P(FRAUDULENT) < 10%`, choose `APPROVE`.
- If `P(FRAUDULENT) > 60%`, choose `STOP`.
- Between 10% and 60%, request one useful affordable check when available.
- If the single check does not resolve the case, choose `HUMAN_REVIEW`.
- Never request evidence more than once.

The 10% approval boundary follows from the simplified costs: approving has
expected cost `100 × P(FRAUDULENT)`, while review costs 10 units. The 60% stop
boundary follows from comparing the expected legitimate-stop cost
`25 × P(LEGITIMATE)` with the 10-unit review cost. These boundaries would need
sensitivity testing and real cost estimates before any operational use.

At a 30% fraud belief, neither automatic action is justified. The initial
decision is therefore `GET_MORE_EVIDENCE`.

## New evidence

The customer completes a `PASS` confirmation through an `INDEPENDENT` channel.
This is evidence for legitimacy, but it is not proof.

For this worked example, the assumed likelihoods are:

| Possible verification outcome | P(outcome \| LEGITIMATE) | P(outcome \| FRAUDULENT) |
|---|---:|---:|
| Independent PASS | 90% | 20% |
| Independent FAIL | 5% | 60% |
| Inconclusive or unavailable | 5% | 20% |
| **Total** | **100%** | **100%** |

These likelihoods are simulation assumptions. They make PASS more likely for a
legitimate customer while allowing the important alternative explanation that
a fraudulent transaction can still pass.

## Posterior calculation after the observed PASS

Unnormalised belief weights:

- `LEGITIMATE: 0.70 × 0.90 = 0.63`
- `FRAUDULENT: 0.30 × 0.20 = 0.06`
- `Total evidence weight: 0.63 + 0.06 = 0.69`

Normalised posterior:

- `P(LEGITIMATE | independent PASS) = 0.63 / 0.69 = 91.3%`
- `P(FRAUDULENT | independent PASS) = 0.06 / 0.69 = 8.7%`
- `Total = 100.0%`, subject to rounding.

## Updated decision

The posterior fraud belief is 8.7%, which is below the illustrative 10%
approval threshold. The updated action is therefore `APPROVE`.

After the action is fixed, the simulator reveals that P2-001 is `LEGITIMATE`.
The action happened to be correct in this case, but one correct example does
not validate the assumed probabilities or prove that independent PASS is
perfect.

## Alternative unsafe evidence check

If the same case had produced an independent `FAIL`, the illustrative posterior
would have been:

- fraudulent weight: `0.30 × 0.60 = 0.18`;
- legitimate weight: `0.70 × 0.05 = 0.035`;
- posterior fraud belief: `0.18 / (0.18 + 0.035) = 83.7%`.

That value is above the 60% stop threshold, so the counterfactual action would
be `STOP`. This check records evidence for both the safe and unsafe hidden-state
explanations rather than examining only reassuring evidence.

## What this record does and does not establish

This record shows the mechanics of prior belief, likelihood, posterior belief,
cost and threshold-based action selection. It does not establish calibration.
Calibration would require a larger set of comparable labelled transactions,
out-of-sample probability predictions and measurements such as reliability
curves or Brier score.

The implemented Policy 2 still uses risk points. A future probability-based
agent would be a new version and would require new development and evaluation
data.
