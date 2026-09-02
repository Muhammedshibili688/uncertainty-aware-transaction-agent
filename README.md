# Uncertainty-Aware-Transaction-Agent

A small transaction decision-agent experiment that reasons under uncertainty.
It compares a static baseline with policies that can update risk when new
evidence becomes available, then choose whether to approve, collect more
evidence, send the case to human review, or stop the transaction.

## Problem

The agent observes an online transaction and a small set of behavioural risk
signals. It must choose one of these actions:

- approve the transaction;
- obtain additional evidence;
- send the case for human review;
- stop the transaction;

because whether the transaction is genuinely fraudulent is not known at decision time.

## Objective

The objective is to test whether an uncertainty-aware transaction policy can
reduce unnecessary human reviews compared with simpler decision policies while
controlling two costly errors:

- approving a fraudulent transaction;
- stopping a legitimate transaction.

The goal is not to build a 100% accurate fraud detector.

The goal is to study how an agent should change its belief and action, 
when the true transaction state is unknown and new evidence becomes available.

## Initial Agent Scope

### Hidden states

- Legitimate transaction
- Fraudulent transaction

### Initial evidence

- `amount_deviation`
- `device_location_context`
- `recent_velocity`

### Additional evidence

- `step_up_result_if_requested`, revealed only after the agent selects
  `GET_MORE_EVIDENCE`

### Possible actions

- APPROVE
- GET MORE EVIDENCE
- HUMAN REVIEW
- STOP

## Current Status

- [x] Problem selected
- [x] Initial objective defined
- [x] Initial research completed
- [x] Public discussions recorded
- [x] v0.1 agent specification frozen
- [x] Forty simulated cases prepared
- [x] Development and evaluation splits created
- [x] Static multi-signal baseline implemented
- [x] Baseline unit tests implemented and passing
- [x] Baseline development experiment completed
- [x] Baseline findings recorded
- [x] Policy 1 implemented
- [x] Policy 1 unit tests implemented and passing
- [x] Policy 1 development experiment completed
- [x] Policy 1 development findings recorded
- [x] Held-out comparison runner implemented and tested
- [x] Baseline and Policy 1 evaluated on the same thirty held-out cases
- [x] Held-out comparison findings recorded
- [ ] Policy 2 implemented
- [ ] Five final failures analysed
- [ ] Probability decision record completed
- [ ] Three AI reviews completed
- [ ] Preprint completed
- [ ] Work published

## Project Status

The frozen v0.1 baseline and Policy 1 have now been compared once on the same
thirty held-out evaluation cases. Policy 1 reduced human review from ten cases
to six and increased automatic coverage from 66.7 percent to 80 percent. It
also raised fraud recall from 60 percent to 66.7 percent.

However, Policy 1 increased false approvals from three to four, while false
stops remained zero. It therefore did not meet every predeclared success
criterion and is not considered better than the baseline for the stated v0.1
objective. In particular, a misleading PASS moved fraudulent CASE-030 from
baseline HUMAN_REVIEW to Policy 1 APPROVE. The evaluation cases are now used
evidence and must not be treated as unseen data for a modified policy.
