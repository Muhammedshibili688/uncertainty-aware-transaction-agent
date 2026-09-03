# v0.2 Case Coverage Plan

Version: v0.2  
Status: FROZEN BEFORE POLICY 2 IMPLEMENTATION  
Target: 40 new cases

## Coverage summary

| Scenario family | Development | Evaluation | Total |
|---|---:|---:|---:|
| Routine legitimate transactions | 1 | 3 | 4 |
| Travel or new-device cases | 1 | 3 | 4 |
| Large-purchase cases | 1 | 3 | 4 |
| Legitimate high-velocity activity | 1 | 3 | 4 |
| Account-takeover fraud | 1 | 3 | 4 |
| Card-testing or rapid fraud | 1 | 3 | 4 |
| Familiar-context fraud | 1 | 3 | 4 |
| Misleading verification | 1 | 3 | 4 |
| Missing-information cases | 1 | 3 | 4 |
| Conflicting-evidence cases | 1 | 3 | 4 |
| **Total** | **10** | **30** | **40** |

## Development cases

| Case | Short name | Family | State | Policy 2 purpose |
|---|---|---|---|---|
| P2-001 | Independent confirmation for laptop | Large purchase | LEGITIMATE | Independent PASS may resolve score two |
| P2-002 | Remote-access purchase | Misleading verification | FRAUDULENT | Same-channel PASS must not lower risk |
| P2-003 | Same-phone emergency booking | Conflicting evidence | LEGITIMATE | Conservative rule may preserve review |
| P2-004 | New-browser account takeover | Account takeover | FRAUDULENT | FAIL remains warning evidence |
| P2-005 | Traveller hotel deposit | Travel/new device | LEGITIMATE | Independent PASS affects score three but does not override it |
| P2-006 | Monthly utility payment | Routine legitimate | LEGITIMATE | Low-risk terminal approval remains unchanged |
| P2-007 | Rapid card testing | Card testing | FRAUDULENT | High initial risk stops without verification |
| P2-008 | Missing history during shopping | Missing information | LEGITIMATE | Inconclusive evidence remains review |
| P2-009 | Familiar-session fraud | Familiar-context fraud | FRAUDULENT | Records the unresolved low-score limitation |
| P2-010 | Festival shopping burst | High-velocity legitimate | LEGITIMATE | Independent PASS may resolve score two |

## Reserved evaluation cases

| Case | Short name | Family | Split |
|---|---|---|---|
| P2-011 | Grocery subscription renewal | Routine legitimate | EVALUATION |
| P2-012 | Replacement phone while travelling | Travel/new device | EVALUATION |
| P2-013 | Known-phone remote-control fraud | Misleading verification | EVALUATION |
| P2-014 | Furniture purchase confirmation | Large purchase | EVALUATION |
| P2-015 | Low-value card-testing burst | Card testing | EVALUATION |
| P2-016 | Wedding shopping sequence | High-velocity legitimate | EVALUATION |
| P2-017 | Stolen-password takeover | Account takeover | EVALUATION |
| P2-018 | New customer with missing history | Missing information | EVALUATION |
| P2-019 | Usual-location wallet theft | Familiar-context fraud | EVALUATION |
| P2-020 | Medical travel payment | Conflicting evidence | EVALUATION |
| P2-021 | Same-device takeover with PASS | Conflicting evidence | EVALUATION |
| P2-022 | Regular streaming renewal | Routine legitimate | EVALUATION |
| P2-023 | Family-device misuse | Familiar-context fraud | EVALUATION |
| P2-024 | Airport booking from new tablet | Travel/new device | EVALUATION |
| P2-025 | Slow card-testing sequence | Card testing | EVALUATION |
| P2-026 | Same-phone appliance purchase | Conflicting evidence | EVALUATION |
| P2-027 | Overseas account takeover | Account takeover | EVALUATION |
| P2-028 | Fraud with unavailable history | Missing information | EVALUATION |
| P2-029 | Imperfect independent confirmation | Misleading verification | EVALUATION |
| P2-030 | Home renovation purchase | Large purchase | EVALUATION |
| P2-031 | Password-reset takeover | Account takeover | EVALUATION |
| P2-032 | Holiday booking burst | High-velocity legitimate | EVALUATION |
| P2-033 | Familiar merchant fraud | Familiar-context fraud | EVALUATION |
| P2-034 | Normal fuel payment | Routine legitimate | EVALUATION |
| P2-035 | Compromised-app verification | Misleading verification | EVALUATION |
| P2-036 | New phone at home | Travel/new device | EVALUATION |
| P2-037 | Maximum-risk card testing | Card testing | EVALUATION |
| P2-038 | Independent confirmation for jewellery | Large purchase | EVALUATION |
| P2-039 | Fraud with inconclusive context | Missing information | EVALUATION |
| P2-040 | Concert-ticket shopping burst | High-velocity legitimate | EVALUATION |

## Evaluation rule

The evaluation rows may be structurally validated for schema, allowed values,
counts and unique IDs. They must not be passed through Policy 2 before its
development behaviour is reviewed and the implementation is frozen.
