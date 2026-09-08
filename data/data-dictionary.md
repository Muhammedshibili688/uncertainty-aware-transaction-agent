# v0.1 Simulation Data Dictionary

Version: v0.1
Status: FROZEN FOR V0.1 EXPERIMENT
Freeze date: 2026-09-01

## 1. Purpose

This is the column guide for the simulated transaction data used in the v0.1
experiment.

Each row in `cases-v0.1.csv` represents one simulated online transaction.

The dataset contains:

- information initially visible to the agent;
- a verification result revealed only if the agent requests it;
- hidden ground truth used only for evaluation;
- human-readable notes explaining how the case was designed.

The dataset does not contain real customers, real transactions or personal
information.

## 2. Information-access rules

The columns are divided into four access groups.

### 2.1 Initially visible to the agent

The agent may use these columns before its first action:

- amount_deviation
- device_location_context
- recent_velocity

### 2.2 Revealed only when requested

The agent may see this column only after selecting GET_MORE_EVIDENCE:

- step_up_result_if_requested

If the agent does not request verification, this value must remain hidden.

### 2.3 Evaluation-only information

The agent must never see these columns while making a decision:

- true_state
- research_scenario
- category_reasoning

These columns are used only to evaluate or explain the experiment.

### 2.4 Documentation-only information

These columns help a human understand how the evidence categories were created,
but they are not provided directly to the v0.1 policy:

- scenario_name
- scenario_description
- usual_amount_min
- usual_amount_max
- transaction_amount
- device_status
- location_status
- normal_max_attempts_1h
- recent_attempts_1h

The agent receives the derived categorical evidence instead of these raw
descriptions and values.

## 3. Column definitions

### 3.1 case_id

Purpose:

A unique identifier for the simulated transaction.

Type:

Text.

Format:

`CASE-001`, `CASE-002`, `CASE-003`, and so on.

Required:

Yes.

Agent access:

The experiment runner may use it to identify the case, but it must not affect
the decision.

Rules:

- Every case must have a unique ID.
- The ID must not reveal whether the case is legitimate or fraudulent.
- Do not use IDs such as `FRAUD-001` or `LEGIT-001`.

Example:

`CASE-001`

### 3.2 scenario_name

Purpose:

A short human-readable name for the scenario.

Type:

Text.

Required:

Yes.

Agent access:

No. Documentation only.

Rules:

The name must not be passed to the policy because it may reveal the intended
answer.

Example:

`Legitimate traveller using a new phone`

### 3.3 scenario_description

Purpose:

A short plain-language description of what is happening in the simulated case.

Type:

Text.

Required:

Yes.

Agent access:

No. Documentation only.

Rules:

The description should contain enough context for a human to understand why
the evidence categories and true state were assigned.

The description is not passed to the agent because words such as "attacker",
"stolen" or "legitimate customer" would reveal the hidden state.

Example:

`A customer travelling abroad uses a recently purchased phone to make a
purchase that is within their normal spending range.`

### 3.4 research_scenario

Purpose:

Records which research-informed scenario or assumption the case is testing.

Type:

Categorical text.

Required:

Yes.

Agent access:

No. Evaluation only.

Allowed values:

- CLEAR_LEGITIMATE
- CLEAR_FRAUDULENT
- LEGITIMATE_TRAVEL
- LARGE_LEGITIMATE_PURCHASE
- KNOWN_DEVICE_FRAUD
- HIGH_VELOCITY_LEGITIMATE
- RAPID_ATTEMPT_FRAUD
- FRAUDULENT_VERIFICATION_PASS
- LEGITIMATE_VERIFICATION_FAIL
- LEGITIMATE_VERIFICATION_INCONCLUSIVE
- FAMILIAR_BEHAVIOUR_FRAUD
- MISSING_EVIDENCE
- CORRELATED_SIGNALS
- BORDERLINE
- OTHER

Rules:

More than one case may use the same research scenario. If a case tests several
ideas, select the most important one and explain the others in
`category_reasoning`.

### 3.5 split

Purpose:

Separates cases used while designing and debugging the agent from cases used
for the final evaluation.

Type:

Categorical text.

Required:

Yes.

Agent access:

No. Evaluation only.

Allowed values:

- DEVELOPMENT
- EVALUATION

Meaning:

- DEVELOPMENT: The case may be used to check calculations, debug code and
  improve implementation before the final policy is frozen.
- EVALUATION: The case is used only after the policy and parameters are frozen.

Rules:

- The agent must not receive this value as evidence.
- Evaluation results must not be used to tune the v0.1 policy.
- If a policy is changed after viewing evaluation results, the original results
  must be preserved and the change must be recorded.

### 3.6 true_state

Purpose:

The simulated ground truth.

Type:

Categorical text.

Required:

Yes.

Agent access:

No. Evaluation only.

Allowed values:

- LEGITIMATE
- FRAUDULENT

Rules:

- Every case must have exactly one true state.
- The true state must not be passed to either policy.
- It is revealed only after the final action.
- UNKNOWN is not allowed as a true state.

### 3.7 usual_amount_min

Purpose:

The lower end of the customer's stated usual transaction range.

Type:

Number.

Required:

No.

Agent access:

No. Documentation only.

Missing value:

Leave empty when comparable history is unavailable.

Rules:

The value is simulated and does not represent a real customer.

### 3.8 usual_amount_max

Purpose:

The upper end of the customer's stated usual transaction range.

Type:

Number.

Required:

No.

Agent access:

No. Documentation only.

Missing value:

Leave empty when comparable history is unavailable.

Rules:

The value must be greater than or equal to `usual_amount_min`.

### 3.9 transaction_amount

Purpose:

The amount of the simulated current transaction.

Type:

Number.

Required:

Yes.

Agent access:

No. Documentation only.

Rules:

- The amount must be zero or greater.
- All cases use the same abstract currency units.
- The experiment does not claim that these amounts represent industry fraud
  thresholds.

### 3.10 amount_deviation

Purpose:

The amount-based categorical evidence received by the agent.

Type:

Categorical text.

Required:

Yes.

Agent access:

Yes, initially visible.

Allowed values:

- NORMAL
- MODERATE
- HIGH
- UNKNOWN

Meaning:

- NORMAL: The amount is within or reasonably close to the stated normal range.
- MODERATE: The amount is outside the normal range but remains reasonably
  plausible.
- HIGH: The amount is substantially outside the stated normal range.
- UNKNOWN: Comparable amount history is unavailable.

Rules:

- UNKNOWN must not be treated as NORMAL.
- The assigned category must agree with the raw amount description.
- The reason for the category must be recorded in `category_reasoning`.

### 3.11 device_status

Purpose:

Records whether the simulated device is familiar to the customer.

Type:

Categorical text.

Required:

Yes.

Agent access:

No. Documentation only.

Allowed values:

- KNOWN
- NEW
- UNKNOWN

Meaning:

- KNOWN: The device has previously been associated with the customer.
- NEW: The device has not previously been associated with the customer.
- UNKNOWN: Device familiarity cannot be determined.

The simulation does not process a real device fingerprint.

### 3.12 location_status

Purpose:

Records whether the transaction location is usual for the customer.

Type:

Categorical text.

Required:

Yes.

Agent access:

No. Documentation only.

Allowed values:

- USUAL
- UNUSUAL
- UNKNOWN

Meaning:

- USUAL: The location is consistent with the customer's stated behaviour.
- UNUSUAL: The location is not consistent with the customer's stated
  behaviour.
- UNKNOWN: Location context cannot be determined.

### 3.13 device_location_context

Purpose:

The combined device-and-location evidence received by the agent.

Type:

Categorical text.

Required:

Yes.

Agent access:

Yes, initially visible.

Allowed values:

- KNOWN_DEVICE_USUAL_LOCATION
- KNOWN_DEVICE_UNUSUAL_LOCATION
- NEW_DEVICE_USUAL_LOCATION
- NEW_DEVICE_UNUSUAL_LOCATION
- UNKNOWN

Derivation rules:

- KNOWN + USUAL = KNOWN_DEVICE_USUAL_LOCATION
- KNOWN + UNUSUAL = KNOWN_DEVICE_UNUSUAL_LOCATION
- NEW + USUAL = NEW_DEVICE_USUAL_LOCATION
- NEW + UNUSUAL = NEW_DEVICE_UNUSUAL_LOCATION
- If device or location is UNKNOWN, the combined value is UNKNOWN.

Reason for combining:

Device and location changes may result from the same real-world event.
Combining them prevents v0.1 from automatically counting them as two
independent confirmations of fraud.

### 3.14 normal_max_attempts_1h

Purpose:

The maximum number of transaction attempts normally expected from the
simulated customer within one hour.

Type:

Whole number.

Required:

No.

Agent access:

No. Documentation only.

Missing value:

Leave empty when comparable recent history is unavailable.

Rules:

- The number must be zero or greater.
- The one-hour window is a v0.1 simulation assumption.
- It is not presented as an industry-standard fraud window.

### 3.15 recent_attempts_1h

Purpose:

The number of transaction attempts made during the most recent simulated
one-hour period.

Type:

Whole number.

Required:

No when velocity is UNKNOWN; otherwise required.

Agent access:

No. Documentation only.

Rules:

The value must be zero or greater.

### 3.16 recent_velocity

Purpose:

The recent-activity evidence received by the agent.

Type:

Categorical text.

Required:

Yes.

Agent access:

Yes, initially visible.

Allowed values:

- NORMAL
- ELEVATED
- HIGH
- UNKNOWN

Meaning:

- NORMAL: Recent activity is consistent with the customer's stated normal
  behaviour.
- ELEVATED: Recent activity is above normal but still reasonably plausible.
- HIGH: The case contains rapid or repeated activity that is strongly unusual
  for the customer.
- UNKNOWN: Comparable recent-activity history is unavailable.

Rules:

- UNKNOWN must not be treated as NORMAL.
- The assigned category must agree with the stated attempt counts.
- The reason for the category must be recorded in `category_reasoning`.
- These categories are simulation assumptions, not production thresholds.

### 3.17 step_up_result_if_requested

Purpose:

Stores the verification result that will be revealed if the agent selects
GET_MORE_EVIDENCE.

Type:

Categorical text.

Required:

Yes.

Agent access:

Conditionally visible.

Allowed values:

- PASS
- FAIL
- INCONCLUSIVE
- UNAVAILABLE

Meaning:

- PASS: The simulated verification succeeds.
- FAIL: The simulated verification fails or is rejected.
- INCONCLUSIVE: The check produces a result but does not resolve identity
  confidently.
- UNAVAILABLE: The check cannot be performed.

Rules:

- This value must remain hidden unless verification is requested.
- PASS is allowed for both LEGITIMATE and FRAUDULENT cases.
- FAIL is allowed for both LEGITIMATE and FRAUDULENT cases.
- The result is evidence and not ground truth.
- NOT_REQUESTED is not stored in this column. NOT_REQUESTED belongs in the
  generated decision record when the agent does not request verification.

### 3.18 category_reasoning

Purpose:

Explains why the evidence categories, verification result and hidden state were
assigned.

Type:

Text.

Required:

Yes.

Agent access:

No. Evaluation only.

Rules:

The explanation should answer:

1. Why was `amount_deviation` assigned?
2. Why was `device_location_context` assigned?
3. Why was `recent_velocity` assigned?
4. Why would the verification produce its stated result?
5. Why is the true state LEGITIMATE or FRAUDULENT?
6. Which research assumption does this case test?

This column must not be passed to the agent.

## 4. Dataset validation rules

Before using `cases.csv`, the following checks must pass:

1. Every `case_id` is unique.
2. Every case has exactly one `true_state`.
3. `true_state` is either LEGITIMATE or FRAUDULENT.
4. Every initially visible evidence value belongs to its allowed category.
5. `device_location_context` agrees with `device_status` and
   `location_status`.
6. UNKNOWN is used when the required comparison information is unavailable.
7. `step_up_result_if_requested` uses an allowed value.
8. PASS and FAIL are not treated as direct copies of the true state.
9. The policy receives only:
   - amount_deviation;
   - device_location_context;
   - recent_velocity.
10. Verification is revealed only after GET_MORE_EVIDENCE.
11. The policy never receives:
   - true_state;
   - scenario_name;
   - scenario_description;
   - research_scenario;
   - category_reasoning.
12. Every required research-informed scenario appears at least once.
13. The dataset contains both LEGITIMATE and FRAUDULENT cases.
14. The dataset contains clear, borderline, misleading and missing-evidence
    cases.
15. Every case includes a human-readable explanation.

## 5. CSV format and column order

The v0.1 simulated cases are stored in:

`data/cases-v0.1.csv`

The file uses UTF-8 encoding and contains one header row followed by one row
for each simulated transaction.

The columns must appear in this order:

1. case_id
2. scenario_name
3. scenario_description
4. research_scenario
5. split
6. true_state
7. usual_amount_min
8. usual_amount_max
9. transaction_amount
10. amount_deviation
11. device_status
12. location_status
13. device_location_context
14. normal_max_attempts_1h
15. recent_attempts_1h
16. recent_velocity
17. step_up_result_if_requested
18. category_reasoning

The CSV header will be:

```csv
case_id,scenario_name,scenario_description,research_scenario,split,true_state,usual_amount_min,usual_amount_max,transaction_amount,amount_deviation,device_status,location_status,device_location_context,normal_max_attempts_1h,recent_attempts_1h,recent_velocity,step_up_result_if_requested,category_reasoning
```

## 6. Dataset limitations

The dataset is manually simulated and does not estimate real-world fraud
prevalence or production performance.

The case designer knows the hidden state while creating each case. This can
introduce confirmation bias by making fraudulent cases look too suspicious and
legitimate cases look too safe.

To reduce this problem, the dataset must include misleading, conflicting,
borderline and missing-evidence cases.

The baseline and uncertainty-aware policies use the same cases so that the
comparison is fair.

## 7. Freeze declaration

Before freezing this data dictionary, I verified that:

- every column has a clear meaning;
- every categorical column has an allowed-value list;
- agent-visible and hidden information are separated;
- the schema agrees with `v0.1-spec.md`;
- no real customer data is included.

Freeze date: 2026-09-01
Status: FROZEN FOR V0.1 EXPERIMENT
