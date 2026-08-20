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

- [x] Problem selected
- [x] Initial objective defined
- [ ] Research completed
- [ ] Reddit discussions completed
- [ ] X discussions completed
- [ ] Probability model designed
- [ ] Agent/simulation implemented
- [ ] Test cases prepared
- [ ] Policies compared
- [ ] Failure analysis completed
- [ ] Preprint completed
- [ ] Work published

## Project Status

This project is currently in the research and problem-formulation stage.
Probabilities, thresholds, costs, and experimental results have not yet been
finalized.