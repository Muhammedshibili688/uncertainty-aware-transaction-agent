# v0.2 Simulation Data Dictionary

Version: v0.2  
Status: FROZEN FOR POLICY 2 DEVELOPMENT  
Freeze date: 2026-09-02

## 1. Purpose

This is the column guide for the v0.2 simulated transaction data. It keeps the
v0.1 evidence fields and adds one field showing whether a requested
verification came from an independent source.

The dataset is designed for a transparent policy experiment. It is not real
bank data and should not be used to claim production fraud performance.

## 2. Evidence visibility

### Initially visible to the agent

- `amount_deviation`
- `device_location_context`
- `recent_velocity`

### Revealed only after GET_MORE_EVIDENCE

- `step_up_result_if_requested`
- `verification_independence_if_requested`

Both additional values remain hidden when no verification is requested.

### Evaluator-only fields

All remaining fields provide simulation context, auditing information or the
hidden answer. They must never enter the agent input.

## 3. Column definitions

### 3.1 `case_id`

A unique identifier such as `P2-001`. It supports auditing and must not encode
the hidden state. The agent does not receive it.

### 3.2 `scenario_name`

A short human-readable title. It is documentation only and is hidden from the
agent.

### 3.3 `scenario_description`

A plain-language description of what the simulated customer or attacker is
doing. It may explain the true situation, so it is evaluator-only.

### 3.4 `research_scenario`

A coverage tag used to check scenario variety. Allowed values are:

- `ROUTINE_LEGITIMATE`
- `TRAVEL_OR_NEW_DEVICE`
- `LARGE_PURCHASE`
- `HIGH_VELOCITY_LEGITIMATE`
- `ACCOUNT_TAKEOVER`
- `CARD_TESTING`
- `FAMILIAR_CONTEXT_FRAUD`
- `MISLEADING_VERIFICATION`
- `MISSING_INFORMATION`
- `CONFLICTING_EVIDENCE`

### 3.5 `split`

Either `DEVELOPMENT` or `EVALUATION`. Policy 2 may be changed using development
findings only. Evaluation rows remain reserved until the policy is frozen.

### 3.6 `true_state`

The hidden answer: `LEGITIMATE` or `FRAUDULENT`. The evaluator reads it only
after the policy returns a final action.

### 3.7 `usual_amount_min`

The lower end of the simulated customer's usual amount range. A blank value
means the history is unavailable. It must be zero or greater when present.

### 3.8 `usual_amount_max`

The upper end of the simulated usual range. A blank value means unavailable.
When both bounds exist the maximum must not be below the minimum.

### 3.9 `transaction_amount`

The simulated current transaction amount. It must be zero or greater.

### 3.10 `amount_deviation`

The permitted summary of the amount comparison:

- `NORMAL`: within or close to established behaviour; zero points;
- `MODERATE`: noticeably unusual; one point;
- `HIGH`: strongly unusual; two points;
- `UNKNOWN`: comparison cannot be made; one uncertainty point.

### 3.11 `device_status`

Either `KNOWN`, `NEW` or `UNKNOWN`. This raw field is used to audit the combined
context category and is not directly passed to the policy.

### 3.12 `location_status`

Either `USUAL`, `UNUSUAL` or `UNKNOWN`. It is evaluator-only raw context.

### 3.13 `device_location_context`

The combined category visible to the agent:

- `KNOWN_DEVICE_USUAL_LOCATION`: zero points;
- `KNOWN_DEVICE_UNUSUAL_LOCATION`: one point;
- `NEW_DEVICE_USUAL_LOCATION`: one point;
- `NEW_DEVICE_UNUSUAL_LOCATION`: two points;
- `UNKNOWN`: one uncertainty point.

### 3.14 `normal_max_attempts_1h`

The simulated customer's normal maximum attempts in one hour. Blank means the
history is unavailable.

### 3.15 `recent_attempts_1h`

The observed attempts in the current hour. Blank means current activity could
not be measured.

### 3.16 `recent_velocity`

The visible activity category:

- `NORMAL`: within expected activity; zero points;
- `ELEVATED`: unusual but not extreme; one point;
- `HIGH`: far above normal or rapid attempts; two points;
- `UNKNOWN`: comparison is unavailable; one uncertainty point.

### 3.17 `step_up_result_if_requested`

The result that the simulation reveals only when the policy requests it:

- `PASS`
- `FAIL`
- `INCONCLUSIVE`
- `UNAVAILABLE`

PASS and FAIL do not directly reveal the true state.

### 3.18 `verification_independence_if_requested`

The source relationship revealed with the requested result:

- `INDEPENDENT`: a separate trusted channel not controlled by the same
  transaction session;
- `SAME_CHANNEL`: the same device or session is used and may share the same
  compromise;
- `UNKNOWN`: the simulation cannot establish independence.

This value describes evidence quality. It is not a fraud label. For example, a
fraudulent transaction can receive an INDEPENDENT PASS because real checks are
not perfect, and a legitimate transaction can receive FAIL.

### 3.19 `category_reasoning`

A human explanation of how the visible categories and verification metadata
were assigned. It is used for review and never passed to the agent.

## 4. Row validation rules

1. Every case ID is non-empty and unique.
2. Every row belongs to exactly one split.
3. Every hidden state and category uses an allowed value.
4. Device and location raw values agree with their combined category.
5. Missing comparisons use `UNKNOWN` rather than pretending to be normal.
6. Verification result and independence remain hidden until requested.
7. The agent initially receives exactly three fields.
8. The agent never receives scenario text or the hidden state.
9. PASS is not automatically interpreted as reliable.
10. Development and evaluation files are derived reproducibly from the master
    v0.2 CSV.

## 5. Canonical column order

```text
case_id
scenario_name
scenario_description
research_scenario
split
true_state
usual_amount_min
usual_amount_max
transaction_amount
amount_deviation
device_status
location_status
device_location_context
normal_max_attempts_1h
recent_attempts_1h
recent_velocity
step_up_result_if_requested
verification_independence_if_requested
category_reasoning
```

## 6. Versioning rule

v0.1 files remain unchanged. Any later evidence or category change requires a
new versioned specification, dictionary and dataset rather than silently
rewriting v0.2 history.
