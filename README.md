# Uncertainty-Aware-Transaction-Agent

Probability-based transaction decision agent reasoning under unceratinity, 
updates fraud-risk as new evidence become avaliable, 
and decide whether to approve a transaction, 
collect more evidence, send it for human review, or stop it.

## Problem

The agent observes an online transaction and a small set of behavioral risk signals. 
It must choose one from; 
    [
        approve the transaction, 
        obtain additional evidence, 
        send it for human review, 
        block it
    ]

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

- Transaction amount deviation
- Device familiarity
- Location change

### Additional evidence

- Recent transaction velocity
- Merchant familiarity

### Possible actions

- APPROVE
- GET MORE EVIDENCE
- HUMAN REVIEW
- STOP

## Current Status

## Current Status

- [x] Problem selected
- [x] Initial objective defined
- [x] Initial research completed
- [x] Public discussions recorded
- [x] v0.1 agent specification frozen
- [x] Forty simulated cases prepared
- [x] Development and evaluation splits created
- [x] Static multi-signal baseline implemented
- [ ] Baseline unit tests implemented and passing
- [x] Baseline development experiment completed
- [x] Baseline findings recorded
- [ ] Policy 1 implemented
- [ ] Policy 1 development experiment completed
- [ ] Policy 2 implemented
- [ ] Final evaluation completed
- [ ] Five final failures analysed
- [ ] Probability decision record completed
- [ ] Three AI reviews completed
- [ ] Preprint completed
- [ ] Work published

## Project Status

The frozen v0.1 dataset and static baseline are complete. The baseline
was tested on ten development cases. It made five automatic decisions,
sent five cases to human review, produced one false approval, and
produced no false stops.

The next stage is Policy 1, which will test whether one step-up
verification can reduce unnecessary human reviews without increasing
costly automatic errors. The thirty evaluation cases remain reserved
for comparison after the baseline, Policy 1, and Policy 2 are frozen.