# Failure Analysis

## Purpose

This analysis examines five incorrect automatic decisions made during the
v0.2 held-out comparison. Four came from Policy 2. The fifth came from Policy 1
and is included because it shows the specific failure that Policy 2 was meant
to reduce.

Human review is not counted as correct or incorrect here. It is a deferred
decision: the agent has admitted that it does not have enough information to
act safely by itself.

## Result being analysed

| Policy | False approvals | False stops | Human reviews |
|---|---:|---:|---:|
| Baseline | 3 | 0 | 19 |
| Policy 1 | 7 | 0 | 7 |
| Policy 2 | 4 | 0 | 12 |

Policy 2 reduced false approvals compared with Policy 1, but it still had one
more false approval than the baseline. This is why Policy 2 was not declared
better for the complete frozen objective.

## Failure 1 — Normal-looking possession is not authorization

### Case

`P2-019`: Usual-location wallet theft.

### What happened

A thief used an unlocked known phone near the customer's home. The transaction
amount was normal, the device and location looked familiar, and recent
activity was normal.

### Agent calculation

| Evidence | Value | Points |
|---|---|---:|
| Amount deviation | NORMAL | 0 |
| Device/location context | KNOWN_DEVICE_USUAL_LOCATION | 0 |
| Recent velocity | NORMAL | 0 |
| **Initial score** | | **0** |

Score zero caused an immediate `APPROVE`. No verification was requested. The
hidden state was later revealed as `FRAUDULENT`, so this was a false approval.

### Failure condition

**Known-device possession mistaken for customer authorization.**

The evidence describes the environment, but it cannot establish who is using
the device. Changing the same score threshold would also block many legitimate
normal-looking transactions. A future version would need a new ownership or
session-integrity signal rather than another adjustment fitted to this case.

## Failure 2 — A mild amount warning stayed below the evidence-request boundary

### Case

`P2-023`: Family-device misuse.

### What happened

A family member used the customer's familiar tablet without permission. The
amount was moderately above the customer's usual range, but the device,
location and velocity appeared normal.

### Agent calculation

| Evidence | Value | Points |
|---|---|---:|
| Amount deviation | MODERATE | 1 |
| Device/location context | KNOWN_DEVICE_USUAL_LOCATION | 0 |
| Recent velocity | NORMAL | 0 |
| **Initial score** | | **1** |

Score one was still inside the automatic-approval region. Policy 2 therefore
approved without asking for verification. The hidden state was
`FRAUDULENT`.

### Failure condition

**Familiar device mistaken for an authorized user.**

The one visible warning was not enough to distinguish misuse from a legitimate
slightly unusual purchase. This exposes a missing identity/consent signal. It
does not, by itself, prove that all score-one transactions should be sent to
review.

## Failure 3 — Independent verification is useful but not infallible

### Case

`P2-029`: Imperfect independent confirmation.

### What happened

The amount was high, while the device/location context and velocity looked
normal. Policy 2 requested evidence because the initial score was two. The
separate channel returned `PASS`, even though the transaction was fraudulent.

### Agent calculation

| Stage | Calculation | Result |
|---|---|---:|
| Initial evidence | 2 + 0 + 0 | 2 |
| Initial action | Score 2 | GET_MORE_EVIDENCE |
| Independent PASS adjustment | 2 - 1 | 1 |
| Final action | Score 1 | APPROVE |

### Failure condition

**Independent confirmation treated as stronger than its real reliability.**

Independence prevents the same compromised channel from confirming itself, but
it does not guarantee correctness. A fraudster may also defeat or manipulate a
separate check. Policy 2 correctly treats PASS as evidence rather than proof,
but the one-point reduction still crossed the approval boundary in this case.

This is the most important new Policy 2 failure because it challenges the main
Policy 2 hypothesis directly.

## Failure 4 — Familiar behaviour can hide stolen credentials

### Case

`P2-033`: Familiar-merchant fraud.

### What happened

Stolen wallet credentials were used for a normal-sized purchase at a familiar
merchant. Every initial evidence category looked normal.

### Agent calculation

| Evidence | Value | Points |
|---|---|---:|
| Amount deviation | NORMAL | 0 |
| Device/location context | KNOWN_DEVICE_USUAL_LOCATION | 0 |
| Recent velocity | NORMAL | 0 |
| **Initial score** | | **0** |

Policy 2 approved immediately, and the hidden state was later revealed as
`FRAUDULENT`.

### Failure condition

**Behavioural familiarity mistaken for safety.**

History can tell the agent that a transaction resembles previous behaviour;
it cannot prove that the present transaction is authorized. The current
evidence set contains no signal capable of separating this case from an
ordinary legitimate purchase.

## Failure 5 — A compromised channel confirmed itself in Policy 1

### Case

`P2-013`: Known-phone remote-control fraud, evaluated under Policy 1.

### What happened

A remote-access scam controlled the customer's usual phone. The amount was
high, but the familiar device/location and normal velocity contributed no
additional points. The in-app check returned `PASS` through that same
compromised phone.

### Policy 1 calculation

| Stage | Calculation | Result |
|---|---|---:|
| Initial evidence | 2 + 0 + 0 | 2 |
| Initial action | Score 2 | GET_MORE_EVIDENCE |
| PASS adjustment | 2 - 1 | 1 |
| Final action | Score 1 | APPROVE |

The hidden state was `FRAUDULENT`, so Policy 1 made a false approval.

### Failure condition

**Self-confirmation through a compromised channel.**

Policy 1 used the PASS result without considering where it came from. Policy 2
addressed this failure: `SAME_CHANNEL` PASS caused no score reduction, so
Policy 2 sent P2-013 to human review. This is an improvement, but it did not
solve the other four false approvals.

## Error-cost judgement

The highest-cost error class in this project is **approving a fraudulent
transaction**. It can create direct financial exposure, customer harm,
investigation work and loss of trust. A legitimate stop is also harmful because
it interrupts a real customer, but it can often be corrected through another
payment attempt or human intervention. No legitimate transaction was stopped
in the v0.2 held-out comparison, so the experiment provides no observed false-
stop case from which to estimate that cost.

Among Policy 2's four false approvals, P2-029 had the largest simulated
transaction amount at 26,000. That amount is exposure, not a measured realized
loss. Across all five cases analysed here, Policy 1's P2-013 had the largest
amount at 36,000.

These rankings are project assumptions. The simulation does not include
chargeback recovery, customer lifetime value, regulatory consequences or
different loss responsibility between customer, merchant and issuer.

## Failure families learned from the five cases

| Failure family | Cases | Main limitation |
|---|---|---|
| Possession is not authorization | P2-019, P2-023 | Missing identity or consent evidence |
| Familiarity is not safety | P2-033 | Behavioural similarity cannot prove legitimacy |
| Independent evidence can still be wrong | P2-029 | Verification reliability is not calibrated |
| Same-channel confirmation can be circular | P2-013 under Policy 1 | Evidence dependence was ignored |

## Decision after analysis

Policy 2 will remain frozen. These evaluation cases are now seen evidence and
will not be used to tune and retest Policy 2 as though they were unseen.

A future version may investigate identity/consent evidence, session-integrity
signals, verification reliability or a calibrated probability model. Any such
change must have a new version, a development set and newly reserved evaluation
cases.
