# v0.1 Case Coverage Plan

Version: v0.1  
Status: FROZEN FOR V0.1 DATASET
Target: 40 cases  
Development cases: 10  
Evaluation cases: 30  
Freeze date: 2026-09-01

## 1. Purpose

This plan shows the kinds of transactions included in the v0.1 simulation. I
used it to avoid building a dataset made only of easy examples where every
warning means fraud and every normal signal means legitimacy.

The planned cases include:

- clear legitimate transactions;
- clear fraudulent transactions;
- legitimate transactions that look suspicious;
- fraudulent transactions that look familiar;
- missing evidence;
- conflicting evidence;
- correlated signals;
- misleading verification results.

This document is planning and evaluation material only. The case names,
scenario families, research points and planned hidden states must not be passed
to the agent.

The complete case stories and reasoning are in `case-drafts-v0.1.md`. The
reviewed structured cases were transferred into `cases-v0.1.csv`.

## 2. Development and evaluation split

The dataset contains two splits.

### DEVELOPMENT

The 10 development cases were available to:

- check whether the data dictionary is usable;
- perform manual probability calculations;
- debug the implementation;
- identify unclear category definitions;
- verify that the agent follows the frozen specification.

These cases could be examined while implementing the agent.

### EVALUATION

The 30 evaluation cases were held back until:

- the data dictionary is frozen;
- the policies are written;
- the probability assumptions are frozen;
- the costs and thresholds are frozen;
- the implementation passes its tests.

Evaluation results must not be used to silently tune v0.1.

If a policy is changed after viewing evaluation results, the original results
must be preserved and the change must be recorded.

## 3. Coverage summary

| Scenario family | Planned hidden state | Development | Evaluation | Total |
|---|---|---:|---:|---:|
| Routine legitimate transactions | LEGITIMATE | 1 | 3 | 4 |
| Legitimate travel/new-device cases | LEGITIMATE | 1 | 3 | 4 |
| Legitimate large-purchase cases | LEGITIMATE | 1 | 3 | 4 |
| Legitimate high-velocity activity | LEGITIMATE | 1 | 3 | 4 |
| Clear account-takeover fraud | FRAUDULENT | 1 | 3 | 4 |
| Rapid-attempt/card-testing fraud | FRAUDULENT | 1 | 3 | 4 |
| Familiar-context fraud | FRAUDULENT | 1 | 3 | 4 |
| Misleading verification outcomes | MIXED | 1 | 3 | 4 |
| Missing-information cases | MIXED | 1 | 3 | 4 |
| Borderline/conflicting/correlated evidence | MIXED | 1 | 3 | 4 |
| **Total** | | **10** | **30** | **40** |

`MIXED` is used only at the planning-family level. Every individual case must
have exactly one true state: `LEGITIMATE` or `FRAUDULENT`.

## 4. Case registry

This table is the original planning record, so its row-level status values show
where each case stood when the plan was written. The reviewed versions are in
`case-drafts-v0.1.md` and `cases-v0.1.csv`.

| Case ID | Short name | Scenario family | Split | Planned state | Research point | Status |
|---|---|---|---|---|---|---|
| CASE-001 | Birthday group dinner | Borderline/conflicting/correlated evidence | DEVELOPMENT | LEGITIMATE | An unusual amount and location should not automatically force verification or stopping | DRAFTED |
| CASE-002 | Traveller with replacement phone | Legitimate travel/new-device cases | DEVELOPMENT | LEGITIMATE | A new device and unusual location may share one legitimate cause | PLANNED |
| CASE-003 | Large birthday banquet | Legitimate large-purchase cases | DEVELOPMENT | LEGITIMATE | A rare large purchase can be legitimate even when it differs from history | PLANNED |
| CASE-004 | Rapid online shopping | Legitimate high-velocity activity | DEVELOPMENT | LEGITIMATE | Several purchases in a short period can be legitimate | PLANNED |
| CASE-005 | New-device account takeover | Clear account-takeover fraud | DEVELOPMENT | FRAUDULENT | Several contextual warnings may support an account-takeover explanation | PLANNED |
| CASE-006 | Regular electricity-bill payment | Routine legitimate transactions | DEVELOPMENT | LEGITIMATE | A familiar low-risk pattern should not receive unnecessary friction | PLANNED |
| CASE-007 | Small-value card-testing burst | Rapid-attempt/card-testing fraud | DEVELOPMENT | FRAUDULENT | High velocity can be more informative than one transaction’s amount | PLANNED |
| CASE-008 | Remote-control malware on known phone | Familiar-context fraud | DEVELOPMENT | FRAUDULENT | A known device does not guarantee that the expected customer is in control | PLANNED |
| CASE-009 | Customer mistypes verification code | Misleading verification outcomes | DEVELOPMENT | LEGITIMATE | Failed verification does not prove fraud | PLANNED |
| CASE-010 | New customer without transaction history | Missing-information cases | DEVELOPMENT | LEGITIMATE | Missing historical evidence must not be interpreted automatically as safe or unsafe | PLANNED |
| CASE-011 | Monthly mobile recharge | Routine legitimate transactions | EVALUATION | LEGITIMATE | A repeated familiar payment should normally remain low risk | PLANNED |
| CASE-012 | Grocery-delivery reorder | Routine legitimate transactions | EVALUATION | LEGITIMATE | Normal evidence across several fields should support routine approval | PLANNED |
| CASE-013 | Regular school-fee instalment | Routine legitimate transactions | EVALUATION | LEGITIMATE | A recurring larger payment may still match established behaviour | PLANNED |
| CASE-014 | Airport purchase during planned travel | Legitimate travel/new-device cases | EVALUATION | LEGITIMATE | An unusual location can have a legitimate explanation | PLANNED |
| CASE-015 | New laptop used from home | Legitimate travel/new-device cases | EVALUATION | LEGITIMATE | A new device from a usual location should not automatically indicate fraud | PLANNED |
| CASE-016 | Hotel booking while roaming abroad | Legitimate travel/new-device cases | EVALUATION | LEGITIMATE | Device and location novelty can arise together during legitimate travel | PLANNED |
| CASE-017 | First expensive laptop purchase | Legitimate large-purchase cases | EVALUATION | LEGITIMATE | A transaction may be far above historical amounts without being fraudulent | PLANNED |
| CASE-018 | Urgent hospital deposit | Legitimate large-purchase cases | EVALUATION | LEGITIMATE | A high-value legitimate need may occur without comparable history | PLANNED |
| CASE-019 | Family wedding venue advance | Legitimate large-purchase cases | EVALUATION | LEGITIMATE | A rare life event can produce a valid but highly unusual payment | PLANNED |
| CASE-020 | Festival-sale shopping across stores | Legitimate high-velocity activity | EVALUATION | LEGITIMATE | Multiple purchases during a sale can create legitimate high velocity | PLANNED |
| CASE-021 | Month-end household bill payments | Legitimate high-velocity activity | EVALUATION | LEGITIMATE | Several planned payments close together should not automatically cause a stop | PLANNED |
| CASE-022 | Repeated ticket booking after payment errors | Legitimate high-velocity activity | EVALUATION | LEGITIMATE | Technical retries can resemble rapid fraudulent attempts | PLANNED |
| CASE-023 | Phished credentials used from another city | Clear account-takeover fraud | EVALUATION | FRAUDULENT | New device, unusual location and changed spending may jointly support fraud | PLANNED |
| CASE-024 | SIM swap followed by wallet funding | Clear account-takeover fraud | EVALUATION | FRAUDULENT | Control of an authentication channel may not mean the true customer is acting | PLANNED |
| CASE-025 | Stolen password used from the same city | Clear account-takeover fraud | EVALUATION | FRAUDULENT | A usual location does not rule out account takeover | PLANNED |
| CASE-026 | Repeated small authorisation attempts | Rapid-attempt/card-testing fraud | EVALUATION | FRAUDULENT | Very small amounts can still form a strong fraudulent velocity pattern | PLANNED |
| CASE-027 | Stolen card tested across subscription sites | Rapid-attempt/card-testing fraud | EVALUATION | FRAUDULENT | Several low-value merchant attempts can indicate card testing | PLANNED |
| CASE-028 | Test payments followed by larger purchase | Rapid-attempt/card-testing fraud | EVALUATION | FRAUDULENT | Fraud may begin with low-risk-looking transactions before increasing value | PLANNED |
| CASE-029 | Hijacked browser session on known device | Familiar-context fraud | EVALUATION | FRAUDULENT | Familiar device context can be misleading when a session is compromised | PLANNED |
| CASE-030 | Remote-access scam using customer’s phone | Familiar-context fraud | EVALUATION | FRAUDULENT | A real device may be used while another person controls the action | PLANNED |
| CASE-031 | Unauthorized purchase from shared home tablet | Familiar-context fraud | EVALUATION | FRAUDULENT | A known household device and usual location do not prove authorization | PLANNED |
| CASE-032 | Socially engineered customer approves verification | Misleading verification outcomes | EVALUATION | FRAUDULENT | Successful verification supports identity but does not prove legitimate intent | PLANNED |
| CASE-033 | Legitimate customer enters expired code | Misleading verification outcomes | EVALUATION | LEGITIMATE | Verification failure can result from ordinary customer error | PLANNED |
| CASE-034 | Fraud attempt during verification outage | Misleading verification outcomes | EVALUATION | FRAUDULENT | Unavailable verification provides no reassuring evidence | PLANNED |
| CASE-035 | Fraud with missing device telemetry | Missing-information cases | EVALUATION | FRAUDULENT | Missing device or location information must not become safe evidence | PLANNED |
| CASE-036 | Legitimate purchase without velocity history | Missing-information cases | EVALUATION | LEGITIMATE | Missing recent activity should not automatically force rejection | PLANNED |
| CASE-037 | Fraud on newly opened account | Missing-information cases | EVALUATION | FRAUDULENT | Lack of amount history makes comparison impossible but does not imply safety | PLANNED |
| CASE-038 | Normal-looking purchase after session compromise | Borderline/conflicting/correlated evidence | EVALUATION | FRAUDULENT | Fraud can deliberately resemble normal amount and familiar-context patterns | PLANNED |
| CASE-039 | Expensive purchase from unusual local venue | Borderline/conflicting/correlated evidence | EVALUATION | LEGITIMATE | Several suspicious-looking signals may share one legitimate explanation | PLANNED |
| CASE-040 | Same-city attacker with successful verification | Borderline/conflicting/correlated evidence | EVALUATION | FRAUDULENT | Reassuring location and verification signals can still be misleading | PLANNED |

## 5. Planned-state summary

| Planned state | Development | Evaluation | Total |
|---|---:|---:|---:|
| LEGITIMATE | 7 | 15 | 22 |
| FRAUDULENT | 3 | 15 | 18 |
| **Total** | **10** | **30** | **40** |

The distribution is designed for scenario coverage. It is not intended to
represent the fraud rate of a real payment system.

The development split contains more legitimate cases because several early
research questions focus on false alarms and unnecessary friction.

The evaluation split contains 15 legitimate and 15 fraudulent cases so that
the policy comparison can inspect both error directions clearly.

This balance is an evaluation design choice, not an estimate of real-world
class prevalence.

## 6. Status meanings

- `PLANNED`: The case exists only in this coverage plan.
- `DRAFTED`: A complete case card has been written in
  `case-drafts-v0.1.md`.
- `REVIEWED`: The hidden state, evidence categories, verification outcome,
  research purpose and leakage checks have been manually reviewed.
- `ADDED_TO_CSV`: The reviewed case has been transferred to
  `cases-v0.1.csv`.
- `FROZEN`: The case is included in the frozen dataset used for the experiment.

A case must move through the statuses in this order:

```text
PLANNED
    ↓
DRAFTED
    ↓
REVIEWED
    ↓
ADDED_TO_CSV
    ↓
FROZEN
```
## 7. Case-design rules

Every detailed case must:

1. Describe one hidden real-world event.
2. Have exactly one true state: LEGITIMATE or FRAUDULENT.
3. Explain the customer’s stated amount history.
4. State the current transaction amount.
5. State whether the device is KNOWN, NEW or UNKNOWN.
6. State whether the location is USUAL, UNUSUAL or UNKNOWN.
7. State the normal and current one-hour transaction activity.
8. Derive the evidence categories using the frozen data dictionary.
9. Define what the verification result would be if requested.
10. Explain why the verification result is plausible.
11. Explain which research finding the case tests.
12. Confirm that the agent-visible fields do not reveal the hidden state.

Hidden state must follow from the simulated event. It must not be assigned
because the evidence looks suspicious or reassuring.

The evidence must follow from the raw case facts. It must not be selected to
force the policy to produce a preferred action.

The case plan does not define the correct action. The policies determine
whether to approve, request verification, escalate or stop.

## 8. Agent-visible and hidden information

At the first decision point, the policy receives only:
- amount_deviation;
- device_location_context;
- recent_velocity.

If the policy chooses GET_MORE_EVIDENCE, it may then receive:
- step_up_result_if_requested.

The policy must never receive:
- scenario_name;
- scenario_description;
- research_scenario;
- split;
- planned_state;
- true_state;
- category_reasoning;
- the hidden real-world event.

The true state is revealed only after the final action.

## 9. Case-drafting order

Cases will be drafted in this order:
1. Write CASE-001 through CASE-010.
2. Review whether the frozen evidence design can represent the development
   cases.
3. Complete at least one manual probability update.
4. Define and test the initial policies using development cases only.
5. Write CASE-011 through CASE-040.
6. Review and transfer the evaluation cases into cases-v0.1.csv.
7. Freeze the policies, parameters and evaluation dataset.
8. Run the final evaluation.

The 30 evaluation cases must not be used to tune v0.1.

## 10. Review checklist

Before marking a case REVIEWED, confirm:
- The case ID does not reveal its hidden state.
- The scenario name is not passed to the policy.
- The scenario description is not passed to the policy.
- The hidden event clearly supports the true state.
- The true state is either LEGITIMATE or FRAUDULENT.
- Raw amount information supports the amount category.
- Device and location values support the combined category.
- Recent activity supports the velocity category.
- Missing information uses UNKNOWN.
- The verification result is plausible.
- PASS and FAIL are not treated as direct copies of the true state.
- The case tests a documented research question.
- The evidence was not selected to force a desired action.
- The category reasoning is understandable in plain language.
- The agent receives only permitted evidence.

## 11. Plan limitations

This plan was created for a small manual simulation. It does not represent all
forms of transaction fraud or all legitimate customer behaviour.
The planned cases are deliberately varied and partly balanced. Therefore:
- their proportions do not represent real fraud prevalence;
- performance on these cases does not estimate production accuracy;
- the case designer’s knowledge may introduce confirmation bias;
- scenario descriptions simplify real payment systems;
- device, location, amount and velocity are represented categorically;
- the one-hour velocity window is a simulation assumption;
- verification outcomes are simulated;
- delayed labels are not modelled in full.
These limitations will be reported with the experiment results and in the
preprint.

## 12. Freeze declaration

Before freezing this case plan, I confirmed that:
- all 40 case slots are listed;
- each scenario family has one development and three evaluation cases;
- the evaluation split contains both legitimate and fraudulent cases;
- all frozen v0.1 evidence variables are covered;
- missing, conflicting, correlated and misleading evidence are represented;
- no case name or ID will be passed to the policy;
- the planned cases address the important findings from the research and human
  discussions.

Status: FROZEN FOR V0.1 DATASET
Freeze date: 2026-09-01

After freezing, a change to scenario-family counts, split assignments or
required coverage must be recorded in the change log.

## 13. Change log

|Version | Date	| Change | Reason | Cases affected |
|---|---|---|---|---|
|v0.1 | 2026-09-01 | Froze the 40-case coverage plan | Preserve the reviewed coverage used by the first experiment | CASE-001 to CASE-040 |
