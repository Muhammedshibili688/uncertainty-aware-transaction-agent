# v0.1 Detailed Case Drafts

Version: v0.1  
Status: DRAFT  
Related registry: `case-plan-v0.1.md`  
Intended next artifact: `cases-v0.1.csv`

## Purpose

This file expands the 40 registry entries into complete, human-reviewable case cards. It is separate from the coverage plan because the plan answers **what the dataset should cover**, while this file records **how each simulated case is constructed**.

These are AI-assisted drafts, not accepted facts and not a frozen dataset. Review every case manually. A case may move from `DRAFTED` to `REVIEWED` only when you can explain and defend its story, evidence categories, hidden state, and verification outcome. Only reviewed cases should be copied into `cases-v0.1.csv`.

The rupee values and customer histories are simulation assumptions. They are not bank rules or universal fraud thresholds. Each real-world event is written first; the evidence is then derived from that event. No case is designed to force a particular policy action.

## Frozen v0.1 boundaries

The policy agent initially receives only:

- `amount_deviation`
- `device_location_context`
- `recent_velocity`

If the policy requests the single allowed extra check, it then receives:

- `step_up_result_if_requested`

The policy agent must never receive the scenario narrative, raw values, research scenario, split, case status, hidden event, true state, reasons, or leakage notes.

## Status workflow

`PLANNED` → `DRAFTED` → `REVIEWED` → `ADDED_TO_CSV` → `FROZEN`

All cases below start as `DRAFTED`.

## Common leakage review

For every case, confirm all of the following before changing its status:

- The case ID and short name do not reveal the hidden state.
- The agent does not receive the scenario description or hidden event.
- The agent does not receive `true_state`, family, split, research scenario, or reasoning.
- The additional verification result is shown only if the agent requests it.
- Verification does not mechanically copy the true state: legitimate cases may fail or be inconclusive, and fraudulent cases may pass.
- No evidence category is chosen merely to force the desired action.

## CASE-001 — Birthday group dinner

- **Status:** REVIEWED
- **Scenario family:** Borderline/conflicting
- **Research scenario:** `CORRELATED_SIGNALS`
- **Split:** `DEVELOPMENT`

### Hidden truth

- **Hidden real-world event:** The account holder pays for a birthday dinner for a group of friends.
- **True state:** `LEGITIMATE`
- **Why this label is correct:** The account holder knowingly made the purchase and received the meal.

### Scenario

The customer usually pays for small meals, but on their birthday they pay a ₹5,000 restaurant bill at a different part of the same city. The known phone is used and there is no burst of attempts.

### Raw amount information

- **Usual minimum:** ₹200
- **Usual maximum:** ₹1,500
- **Current amount:** ₹5,000
- **Derived `amount_deviation`:** `MODERATE`
- **Reason:** The bill is clearly above the customer's usual food spending, but it is plausible for a one-time group celebration.

### Device and location

- **Device status:** `KNOWN`
- **Location status:** `UNUSUAL`
- **Derived `device_location_context`:** `KNOWN_DEVICE_UNUSUAL_LOCATION`
- **Reason:** The same phone is used, while the restaurant is outside the customer's usual spending area. The birthday celebration explains both the unusual location and larger bill.

### Recent activity

- **Normal maximum attempts in one hour:** 3
- **Current attempts in one hour:** 1
- **Derived `recent_velocity`:** `NORMAL`
- **Reason:** One attempt is within the customer's normal hourly activity.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `PASS`
- **Reason:** If asked, the genuine customer can complete the check successfully.

### Research point tested

Several unusual-looking signals can come from one legitimate event. Correlated signals should not automatically be counted as independent evidence of fraud.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-002 — Traveller with replacement phone

- **Status:** REVIEWED
- **Scenario family:** Travel/new device
- **Research scenario:** `LEGITIMATE_TRAVEL`
- **Split:** `DEVELOPMENT`

### Hidden truth

- **Hidden real-world event:** The account holder buys travel supplies while away from home using a recently replaced phone.
- **True state:** `LEGITIMATE`
- **Why this label is correct:** The customer is travelling and personally makes the purchase.

### Scenario

During a planned trip, the customer uses a replacement phone to buy toiletries near the hotel. Both the device and location look unfamiliar, but they share the same legitimate travel explanation.

### Raw amount information

- **Usual minimum:** ₹100
- **Usual maximum:** ₹1,500
- **Current amount:** ₹850
- **Derived `amount_deviation`:** `NORMAL`
- **Reason:** The amount is inside the customer's ordinary small-purchase range.

### Device and location

- **Device status:** `NEW`
- **Location status:** `UNUSUAL`
- **Derived `device_location_context`:** `NEW_DEVICE_UNUSUAL_LOCATION`
- **Reason:** The phone was replaced shortly before the trip, and the customer is away from their normal area.

### Recent activity

- **Normal maximum attempts in one hour:** 2
- **Current attempts in one hour:** 1
- **Derived `recent_velocity`:** `NORMAL`
- **Reason:** There is only one attempt in the hour.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `PASS`
- **Reason:** The genuine customer has access to the replacement phone and can complete the check.

### Research point tested

A new device and unusual location may be correlated consequences of legitimate travel rather than two independent fraud signals.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-003 — Large birthday banquet

- **Status:** REVIEWED
- **Scenario family:** Large purchase
- **Research scenario:** `LARGE_LEGITIMATE_PURCHASE`
- **Split:** `DEVELOPMENT`

### Hidden truth

- **Hidden real-world event:** The account holder pays the deposit and final bill for a family birthday banquet.
- **True state:** `LEGITIMATE`
- **Why this label is correct:** The account holder arranged the event and authorized the payment.

### Scenario

A customer whose normal purchases are modest pays ₹30,000 to a banquet venue for a planned family event. The known phone is used, and there is only one attempt.

### Raw amount information

- **Usual minimum:** ₹300
- **Usual maximum:** ₹2,000
- **Current amount:** ₹30,000
- **Derived `amount_deviation`:** `HIGH`
- **Reason:** The transaction is far above the customer's normal range, even though the event makes it plausible.

### Device and location

- **Device status:** `KNOWN`
- **Location status:** `UNUSUAL`
- **Derived `device_location_context`:** `KNOWN_DEVICE_UNUSUAL_LOCATION`
- **Reason:** The customer uses the usual phone at a venue where they have not paid before.

### Recent activity

- **Normal maximum attempts in one hour:** 2
- **Current attempts in one hour:** 1
- **Derived `recent_velocity`:** `NORMAL`
- **Reason:** A single attempt does not indicate a rapid sequence.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `PASS`
- **Reason:** The genuine customer can confirm the unusual purchase.

### Research point tested

A very large relative deviation can still be legitimate; high exposure should be considered without treating it as proof of fraud.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-004 — Rapid online shopping

- **Status:** REVIEWED
- **Scenario family:** High-velocity legitimate
- **Research scenario:** `HIGH_VELOCITY_LEGITIMATE`
- **Split:** `DEVELOPMENT`

### Hidden truth

- **Hidden real-world event:** The account holder makes several separate purchases during a limited online sale.
- **True state:** `LEGITIMATE`
- **Why this label is correct:** The customer intentionally makes all purchases in the sale.

### Scenario

During a festival sale, the customer buys clothing and household items from several stores within one hour. Each payment is ordinary, but the sequence is much faster than usual.

### Raw amount information

- **Usual minimum:** ₹200
- **Usual maximum:** ₹3,000
- **Current amount:** ₹1,200
- **Derived `amount_deviation`:** `NORMAL`
- **Reason:** The current purchase is within the normal amount range.

### Device and location

- **Device status:** `KNOWN`
- **Location status:** `USUAL`
- **Derived `device_location_context`:** `KNOWN_DEVICE_USUAL_LOCATION`
- **Reason:** The normal phone and home location are used.

### Recent activity

- **Normal maximum attempts in one hour:** 3
- **Current attempts in one hour:** 7
- **Derived `recent_velocity`:** `HIGH`
- **Reason:** Seven attempts are more than twice the usual hourly maximum.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `PASS`
- **Reason:** The genuine shopper can complete a check if one is requested.

### Research point tested

High transaction velocity can arise from legitimate shopping and must not be treated as a fraud label by itself.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-005 — New-device account takeover

- **Status:** REVIEWED
- **Scenario family:** Account takeover
- **Research scenario:** `CLEAR_FRAUDULENT`
- **Split:** `DEVELOPMENT`

### Hidden truth

- **Hidden real-world event:** An attacker uses stolen credentials from a new device in another city.
- **True state:** `FRAUDULENT`
- **Why this label is correct:** The account holder did not authorize the purchase; stolen credentials were used.

### Scenario

Soon after obtaining the password, an attacker attempts a high-value electronics purchase from an unfamiliar device and location.

### Raw amount information

- **Usual minimum:** ₹200
- **Usual maximum:** ₹3,000
- **Current amount:** ₹18,000
- **Derived `amount_deviation`:** `HIGH`
- **Reason:** The purchase is far above the customer's usual range.

### Device and location

- **Device status:** `NEW`
- **Location status:** `UNUSUAL`
- **Derived `device_location_context`:** `NEW_DEVICE_UNUSUAL_LOCATION`
- **Reason:** Neither the device nor the location matches the customer's history.

### Recent activity

- **Normal maximum attempts in one hour:** 2
- **Current attempts in one hour:** 4
- **Derived `recent_velocity`:** `ELEVATED`
- **Reason:** Four attempts are above normal and may reflect retries by the attacker.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `FAIL`
- **Reason:** The attacker cannot complete the account-holder verification correctly.

### Research point tested

Multiple contextual warnings can support a fraud hypothesis, while the hidden state remains separate from the evidence.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-006 — Regular electricity-bill payment

- **Status:** REVIEWED
- **Scenario family:** Routine legitimate
- **Research scenario:** `CLEAR_LEGITIMATE`
- **Split:** `DEVELOPMENT`

### Hidden truth

- **Hidden real-world event:** The account holder pays the usual monthly electricity bill.
- **True state:** `LEGITIMATE`
- **Why this label is correct:** The customer knowingly pays their own bill.

### Scenario

The customer pays the electricity provider from home using the same phone and roughly the same amount as previous months.

### Raw amount information

- **Usual minimum:** ₹1,500
- **Usual maximum:** ₹3,500
- **Current amount:** ₹2,400
- **Derived `amount_deviation`:** `NORMAL`
- **Reason:** The amount falls inside the normal bill range.

### Device and location

- **Device status:** `KNOWN`
- **Location status:** `USUAL`
- **Derived `device_location_context`:** `KNOWN_DEVICE_USUAL_LOCATION`
- **Reason:** Both device and location match established behaviour.

### Recent activity

- **Normal maximum attempts in one hour:** 2
- **Current attempts in one hour:** 1
- **Derived `recent_velocity`:** `NORMAL`
- **Reason:** The single attempt is ordinary.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `PASS`
- **Reason:** The customer can complete verification if it is unexpectedly requested.

### Research point tested

The dataset needs clear legitimate examples so the policy is not evaluated only on unusual cases.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-007 — Small-value card-testing burst

- **Status:** REVIEWED
- **Scenario family:** Rapid-attempt/card-testing
- **Research scenario:** `RAPID_ATTEMPT_FRAUD`
- **Split:** `DEVELOPMENT`

### Hidden truth

- **Hidden real-world event:** An attacker tests stolen card details with many tiny authorizations.
- **True state:** `FRAUDULENT`
- **Why this label is correct:** The account holder did not make any of the attempts.

### Scenario

A series of ₹49 online attempts appears within minutes from a new device. The attacker is checking whether the stolen card is active.

### Raw amount information

- **Usual minimum:** ₹100
- **Usual maximum:** ₹3,000
- **Current amount:** ₹49
- **Derived `amount_deviation`:** `MODERATE`
- **Reason:** The amount is outside the usual range but is intentionally small, so amount alone is weak evidence.

### Device and location

- **Device status:** `NEW`
- **Location status:** `USUAL`
- **Derived `device_location_context`:** `NEW_DEVICE_USUAL_LOCATION`
- **Reason:** The online location maps to the customer's city, but the device has not been seen before.

### Recent activity

- **Normal maximum attempts in one hour:** 2
- **Current attempts in one hour:** 12
- **Derived `recent_velocity`:** `HIGH`
- **Reason:** Twelve attempts greatly exceed the normal hourly maximum.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `FAIL`
- **Reason:** The attacker cannot satisfy the account-holder check.

### Research point tested

Card testing may be signalled more strongly by rapid attempts than by transaction amount.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-008 — Remote-control malware on known phone

- **Status:** REVIEWED
- **Scenario family:** Familiar-context fraud
- **Research scenario:** `KNOWN_DEVICE_FRAUD`
- **Split:** `DEVELOPMENT`

### Hidden truth

- **Hidden real-world event:** Malware controls the customer's already trusted phone and initiates a purchase.
- **True state:** `FRAUDULENT`
- **Why this label is correct:** Malware, not the account holder, initiates the payment.

### Scenario

A fraudulent payment is made through the customer's known phone from the usual location. Device and location therefore look familiar despite the lack of authorization.

### Raw amount information

- **Usual minimum:** ₹500
- **Usual maximum:** ₹5,000
- **Current amount:** ₹4,800
- **Derived `amount_deviation`:** `NORMAL`
- **Reason:** The amount is within the upper end of normal spending.

### Device and location

- **Device status:** `KNOWN`
- **Location status:** `USUAL`
- **Derived `device_location_context`:** `KNOWN_DEVICE_USUAL_LOCATION`
- **Reason:** The compromised phone is physically in the customer's normal area.

### Recent activity

- **Normal maximum attempts in one hour:** 2
- **Current attempts in one hour:** 1
- **Derived `recent_velocity`:** `NORMAL`
- **Reason:** The attacker makes only one attempt to avoid attracting attention.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `PASS`
- **Reason:** A compromised authenticated session makes the technical check pass even though the purchase is unauthorized.

### Research point tested

Known device, usual location, and a passing check do not guarantee legitimacy.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-009 — Customer mistypes verification code

- **Status:** REVIEWED
- **Scenario family:** Misleading verification
- **Research scenario:** `LEGITIMATE_VERIFICATION_FAIL`
- **Split:** `DEVELOPMENT`

### Hidden truth

- **Hidden real-world event:** The genuine customer mistypes a one-time verification code.
- **True state:** `LEGITIMATE`
- **Why this label is correct:** The account holder intentionally made the purchase despite the input error.

### Scenario

A normal purchase from the customer's usual context is challenged. The customer enters the code incorrectly after confusing two digits.

### Raw amount information

- **Usual minimum:** ₹200
- **Usual maximum:** ₹3,000
- **Current amount:** ₹900
- **Derived `amount_deviation`:** `NORMAL`
- **Reason:** The amount is ordinary for this customer.

### Device and location

- **Device status:** `KNOWN`
- **Location status:** `USUAL`
- **Derived `device_location_context`:** `KNOWN_DEVICE_USUAL_LOCATION`
- **Reason:** The usual phone and location are present.

### Recent activity

- **Normal maximum attempts in one hour:** 2
- **Current attempts in one hour:** 1
- **Derived `recent_velocity`:** `NORMAL`
- **Reason:** There is no unusual burst of transactions.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `FAIL`
- **Reason:** The genuine customer enters the code incorrectly; the failed check is an observation, not the hidden truth.

### Research point tested

A failed verification can occur in a legitimate transaction.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-010 — New customer without transaction history

- **Status:** REVIEWED
- **Scenario family:** Missing information
- **Research scenario:** `MISSING_EVIDENCE`
- **Split:** `DEVELOPMENT`

### Hidden truth

- **Hidden real-world event:** A newly enrolled customer makes their first ordinary purchase.
- **True state:** `LEGITIMATE`
- **Why this label is correct:** The new account holder personally makes the grocery purchase.

### Scenario

The customer buys groceries soon after opening the account. There is no historical amount or velocity baseline yet.

### Raw amount information

- **Usual minimum:** Not available
- **Usual maximum:** Not available
- **Current amount:** ₹1,200
- **Derived `amount_deviation`:** `UNKNOWN`
- **Reason:** Without prior transactions, relative amount deviation cannot be calculated.

### Device and location

- **Device status:** `NEW`
- **Location status:** `USUAL`
- **Derived `device_location_context`:** `NEW_DEVICE_USUAL_LOCATION`
- **Reason:** The enrolled device is new to the system, while the location matches the declared home area.

### Recent activity

- **Normal maximum attempts in one hour:** Not available
- **Current attempts in one hour:** 1
- **Derived `recent_velocity`:** `UNKNOWN`
- **Reason:** There is no historical hourly maximum for comparison.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `PASS`
- **Reason:** The genuine new customer can complete the check.

### Research point tested

The agent must represent missing evidence explicitly instead of quietly treating it as normal or suspicious.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-011 — Monthly mobile recharge

- **Status:** REVIEWED
- **Scenario family:** Routine legitimate
- **Research scenario:** `CLEAR_LEGITIMATE`
- **Split:** `EVALUATION`

### Hidden truth

- **Hidden real-world event:** The account holder performs their regular mobile recharge.
- **True state:** `LEGITIMATE`
- **Why this label is correct:** The account holder authorized the recharge.

### Scenario

The same monthly recharge is made from the usual device and home location.

### Raw amount information

- **Usual minimum:** ₹199
- **Usual maximum:** ₹799
- **Current amount:** ₹399
- **Derived `amount_deviation`:** `NORMAL`
- **Reason:** The recharge is within the established range.

### Device and location

- **Device status:** `KNOWN`
- **Location status:** `USUAL`
- **Derived `device_location_context`:** `KNOWN_DEVICE_USUAL_LOCATION`
- **Reason:** Both contextual signals are familiar.

### Recent activity

- **Normal maximum attempts in one hour:** 2
- **Current attempts in one hour:** 1
- **Derived `recent_velocity`:** `NORMAL`
- **Reason:** One attempt is normal.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `PASS`
- **Reason:** The genuine customer would pass a check.

### Research point tested

Tests whether routine low-risk behaviour is handled consistently.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-012 — Grocery-delivery reorder

- **Status:** REVIEWED
- **Scenario family:** Routine legitimate
- **Research scenario:** `CLEAR_LEGITIMATE`
- **Split:** `EVALUATION`

### Hidden truth

- **Hidden real-world event:** The account holder reorders a typical basket from a familiar grocery service.
- **True state:** `LEGITIMATE`
- **Why this label is correct:** The customer deliberately placed the order.

### Scenario

A normal grocery order is placed from home with the known phone.

### Raw amount information

- **Usual minimum:** ₹500
- **Usual maximum:** ₹3,500
- **Current amount:** ₹1,850
- **Derived `amount_deviation`:** `NORMAL`
- **Reason:** The basket total is typical for the customer.

### Device and location

- **Device status:** `KNOWN`
- **Location status:** `USUAL`
- **Derived `device_location_context`:** `KNOWN_DEVICE_USUAL_LOCATION`
- **Reason:** The device and location match previous orders.

### Recent activity

- **Normal maximum attempts in one hour:** 3
- **Current attempts in one hour:** 1
- **Derived `recent_velocity`:** `NORMAL`
- **Reason:** Activity is below the normal maximum.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `PASS`
- **Reason:** The customer can verify the order.

### Research point tested

Provides another clear legitimate case with a different merchant context.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-013 — Regular school-fee instalment

- **Status:** REVIEWED
- **Scenario family:** Routine legitimate
- **Research scenario:** `CLEAR_LEGITIMATE`
- **Split:** `EVALUATION`

### Hidden truth

- **Hidden real-world event:** The account holder pays a scheduled school-fee instalment.
- **True state:** `LEGITIMATE`
- **Why this label is correct:** The customer knowingly pays the scheduled fee.

### Scenario

A fee amount similar to earlier instalments is paid from the usual phone and location.

### Raw amount information

- **Usual minimum:** ₹5,000
- **Usual maximum:** ₹15,000
- **Current amount:** ₹10,000
- **Derived `amount_deviation`:** `NORMAL`
- **Reason:** The amount matches the customer's established fee-payment range.

### Device and location

- **Device status:** `KNOWN`
- **Location status:** `USUAL`
- **Derived `device_location_context`:** `KNOWN_DEVICE_USUAL_LOCATION`
- **Reason:** The context is fully familiar.

### Recent activity

- **Normal maximum attempts in one hour:** 2
- **Current attempts in one hour:** 1
- **Derived `recent_velocity`:** `NORMAL`
- **Reason:** Only one payment is attempted.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `PASS`
- **Reason:** The account holder can complete verification.

### Research point tested

Checks that a relatively large absolute amount may still be normal relative to the customer's history.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-014 — Airport purchase during planned travel

- **Status:** REVIEWED
- **Scenario family:** Travel/new device
- **Research scenario:** `LEGITIMATE_TRAVEL`
- **Split:** `EVALUATION`

### Hidden truth

- **Hidden real-world event:** The account holder buys food at an airport during a planned trip.
- **True state:** `LEGITIMATE`
- **Why this label is correct:** The account holder makes the airport purchase.

### Scenario

A normal-sized purchase occurs outside the customer's home area while they travel.

### Raw amount information

- **Usual minimum:** ₹200
- **Usual maximum:** ₹2,000
- **Current amount:** ₹1,200
- **Derived `amount_deviation`:** `NORMAL`
- **Reason:** The amount remains within usual spending.

### Device and location

- **Device status:** `KNOWN`
- **Location status:** `UNUSUAL`
- **Derived `device_location_context`:** `KNOWN_DEVICE_UNUSUAL_LOCATION`
- **Reason:** The usual phone is used at an airport outside the normal area.

### Recent activity

- **Normal maximum attempts in one hour:** 2
- **Current attempts in one hour:** 2
- **Derived `recent_velocity`:** `NORMAL`
- **Reason:** Two attempts are still within the hourly norm.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `PASS`
- **Reason:** The travelling customer can complete the check.

### Research point tested

An unusual location alone can have a benign travel explanation.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-015 — New laptop used from home

- **Status:** REVIEWED
- **Scenario family:** Travel/new device
- **Research scenario:** `CORRELATED_SIGNALS`
- **Split:** `EVALUATION`

### Hidden truth

- **Hidden real-world event:** The customer activates a newly purchased laptop and makes a payment from home.
- **True state:** `LEGITIMATE`
- **Why this label is correct:** The account holder is setting up and using their own laptop.

### Scenario

The account is accessed from a new laptop, but the payment originates from the customer's usual home location.

### Raw amount information

- **Usual minimum:** ₹500
- **Usual maximum:** ₹4,000
- **Current amount:** ₹2,600
- **Derived `amount_deviation`:** `NORMAL`
- **Reason:** The transaction amount is ordinary.

### Device and location

- **Device status:** `NEW`
- **Location status:** `USUAL`
- **Derived `device_location_context`:** `NEW_DEVICE_USUAL_LOCATION`
- **Reason:** Only the device is unfamiliar; the location matches home.

### Recent activity

- **Normal maximum attempts in one hour:** 2
- **Current attempts in one hour:** 1
- **Derived `recent_velocity`:** `NORMAL`
- **Reason:** No rapid activity is present.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `PASS`
- **Reason:** The genuine customer can verify from the new computer.

### Research point tested

A new device should change uncertainty without being treated as proof of takeover.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-016 — Hotel booking while roaming abroad

- **Status:** REVIEWED
- **Scenario family:** Travel/new device
- **Research scenario:** `LEGITIMATE_TRAVEL`
- **Split:** `EVALUATION`

### Hidden truth

- **Hidden real-world event:** The account holder books an additional hotel night while abroad.
- **True state:** `LEGITIMATE`
- **Why this label is correct:** The customer personally extends the hotel stay.

### Scenario

The known phone is roaming outside the customer's usual country and is used for an urgent hotel extension.

### Raw amount information

- **Usual minimum:** ₹1,000
- **Usual maximum:** ₹8,000
- **Current amount:** ₹18,000
- **Derived `amount_deviation`:** `HIGH`
- **Reason:** The international hotel extension is well above the usual transaction range.

### Device and location

- **Device status:** `KNOWN`
- **Location status:** `UNUSUAL`
- **Derived `device_location_context`:** `KNOWN_DEVICE_UNUSUAL_LOCATION`
- **Reason:** The device is familiar, but the overseas location is not.

### Recent activity

- **Normal maximum attempts in one hour:** 2
- **Current attempts in one hour:** 1
- **Derived `recent_velocity`:** `NORMAL`
- **Reason:** The customer makes one booking attempt.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `PASS`
- **Reason:** The traveller can confirm the payment.

### Research point tested

Travel can produce both location and amount anomalies in a legitimate transaction.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-017 — First expensive laptop purchase

- **Status:** REVIEWED
- **Scenario family:** Large purchase
- **Research scenario:** `LARGE_LEGITIMATE_PURCHASE`
- **Split:** `EVALUATION`

### Hidden truth

- **Hidden real-world event:** The account holder buys a laptop after saving for it.
- **True state:** `LEGITIMATE`
- **Why this label is correct:** The customer selected and authorized the laptop purchase.

### Scenario

A ₹72,000 electronics purchase is made from home using the known phone.

### Raw amount information

- **Usual minimum:** ₹500
- **Usual maximum:** ₹5,000
- **Current amount:** ₹72,000
- **Derived `amount_deviation`:** `HIGH`
- **Reason:** The purchase is far beyond past day-to-day spending.

### Device and location

- **Device status:** `KNOWN`
- **Location status:** `USUAL`
- **Derived `device_location_context`:** `KNOWN_DEVICE_USUAL_LOCATION`
- **Reason:** The transaction occurs in the normal context.

### Recent activity

- **Normal maximum attempts in one hour:** 2
- **Current attempts in one hour:** 1
- **Derived `recent_velocity`:** `NORMAL`
- **Reason:** There is only one attempt.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `PASS`
- **Reason:** The customer can confirm the planned purchase.

### Research point tested

Tests a legitimate high-value purchase with otherwise familiar evidence.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-018 — Urgent hospital deposit

- **Status:** REVIEWED
- **Scenario family:** Large purchase
- **Research scenario:** `LARGE_LEGITIMATE_PURCHASE`
- **Split:** `EVALUATION`

### Hidden truth

- **Hidden real-world event:** The account holder pays an urgent hospital admission deposit.
- **True state:** `LEGITIMATE`
- **Why this label is correct:** The account holder knowingly pays the hospital.

### Scenario

A large payment is made at an unfamiliar hospital during a family emergency.

### Raw amount information

- **Usual minimum:** ₹500
- **Usual maximum:** ₹5,000
- **Current amount:** ₹50,000
- **Derived `amount_deviation`:** `HIGH`
- **Reason:** The deposit is far above the usual amount range.

### Device and location

- **Device status:** `KNOWN`
- **Location status:** `UNUSUAL`
- **Derived `device_location_context`:** `KNOWN_DEVICE_UNUSUAL_LOCATION`
- **Reason:** The phone is familiar, but the hospital location is new.

### Recent activity

- **Normal maximum attempts in one hour:** 2
- **Current attempts in one hour:** 1
- **Derived `recent_velocity`:** `NORMAL`
- **Reason:** Only one transaction is attempted.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `PASS`
- **Reason:** The customer can verify the urgent payment.

### Research point tested

High amount and unusual location can coexist in a genuine emergency.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-019 — Family wedding venue advance

- **Status:** REVIEWED
- **Scenario family:** Large purchase
- **Research scenario:** `LARGE_LEGITIMATE_PURCHASE`
- **Split:** `EVALUATION`

### Hidden truth

- **Hidden real-world event:** The account holder pays an advance to reserve a wedding venue.
- **True state:** `LEGITIMATE`
- **Why this label is correct:** The customer arranged the booking and authorized the advance.

### Scenario

A one-time ₹100,000 venue advance is paid from the known phone at the venue.

### Raw amount information

- **Usual minimum:** ₹1,000
- **Usual maximum:** ₹10,000
- **Current amount:** ₹100,000
- **Derived `amount_deviation`:** `HIGH`
- **Reason:** The advance is much larger than historical purchases.

### Device and location

- **Device status:** `KNOWN`
- **Location status:** `UNUSUAL`
- **Derived `device_location_context`:** `KNOWN_DEVICE_UNUSUAL_LOCATION`
- **Reason:** The customer uses the normal phone at a new merchant location.

### Recent activity

- **Normal maximum attempts in one hour:** 2
- **Current attempts in one hour:** 1
- **Derived `recent_velocity`:** `NORMAL`
- **Reason:** There is no burst of attempts.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `PASS`
- **Reason:** The customer can confirm the planned family expense.

### Research point tested

Tests whether the policy can handle a legitimate one-time high-exposure transaction.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-020 — Festival-sale shopping across stores

- **Status:** REVIEWED
- **Scenario family:** High-velocity legitimate
- **Research scenario:** `HIGH_VELOCITY_LEGITIMATE`
- **Split:** `EVALUATION`

### Hidden truth

- **Hidden real-world event:** The account holder shops at several stores during a festival sale.
- **True state:** `LEGITIMATE`
- **Why this label is correct:** The account holder makes all nine purchases.

### Scenario

Nine purchases occur within an hour from the normal phone and area. Each is part of a planned sale-day shopping trip.

### Raw amount information

- **Usual minimum:** ₹300
- **Usual maximum:** ₹3,000
- **Current amount:** ₹2,800
- **Derived `amount_deviation`:** `NORMAL`
- **Reason:** The current purchase is within the established range.

### Device and location

- **Device status:** `KNOWN`
- **Location status:** `USUAL`
- **Derived `device_location_context`:** `KNOWN_DEVICE_USUAL_LOCATION`
- **Reason:** The customer remains in the usual shopping area with the known device.

### Recent activity

- **Normal maximum attempts in one hour:** 3
- **Current attempts in one hour:** 9
- **Derived `recent_velocity`:** `HIGH`
- **Reason:** Nine attempts greatly exceed the normal hourly maximum.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `PASS`
- **Reason:** The shopper can complete verification.

### Research point tested

A rapid sequence can be genuine even when the velocity signal is strongly unusual.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-021 — Month-end household bill payments

- **Status:** REVIEWED
- **Scenario family:** High-velocity legitimate
- **Research scenario:** `HIGH_VELOCITY_LEGITIMATE`
- **Split:** `EVALUATION`

### Hidden truth

- **Hidden real-world event:** The account holder pays several household bills together on payday.
- **True state:** `LEGITIMATE`
- **Why this label is correct:** The customer intentionally pays each household bill.

### Scenario

Electricity, internet, phone, insurance, and other bills are paid in one sitting.

### Raw amount information

- **Usual minimum:** ₹500
- **Usual maximum:** ₹6,000
- **Current amount:** ₹4,500
- **Derived `amount_deviation`:** `NORMAL`
- **Reason:** The current bill amount is typical.

### Device and location

- **Device status:** `KNOWN`
- **Location status:** `USUAL`
- **Derived `device_location_context`:** `KNOWN_DEVICE_USUAL_LOCATION`
- **Reason:** The customer uses the normal phone at home.

### Recent activity

- **Normal maximum attempts in one hour:** 4
- **Current attempts in one hour:** 8
- **Derived `recent_velocity`:** `ELEVATED`
- **Reason:** Eight payments are above the usual maximum but reflect a monthly routine.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `PASS`
- **Reason:** The customer can confirm the bill-payment session.

### Research point tested

Elevated velocity may result from batching legitimate obligations.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-022 — Repeated ticket booking after payment errors

- **Status:** REVIEWED
- **Scenario family:** High-velocity legitimate
- **Research scenario:** `HIGH_VELOCITY_LEGITIMATE`
- **Split:** `EVALUATION`

### Hidden truth

- **Hidden real-world event:** The account holder retries a train-ticket purchase after gateway errors.
- **True state:** `LEGITIMATE`
- **Why this label is correct:** The customer is repeatedly attempting the same genuine booking.

### Scenario

The booking site reports temporary failures, causing the customer to retry the same intended purchase several times.

### Raw amount information

- **Usual minimum:** ₹500
- **Usual maximum:** ₹5,000
- **Current amount:** ₹6,800
- **Derived `amount_deviation`:** `MODERATE`
- **Reason:** The family booking is somewhat above the usual ticket amount but still plausible.

### Device and location

- **Device status:** `KNOWN`
- **Location status:** `USUAL`
- **Derived `device_location_context`:** `KNOWN_DEVICE_USUAL_LOCATION`
- **Reason:** The normal device and home location are used.

### Recent activity

- **Normal maximum attempts in one hour:** 2
- **Current attempts in one hour:** 6
- **Derived `recent_velocity`:** `HIGH`
- **Reason:** Six attempts are far above normal, although they stem from payment errors.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `INCONCLUSIVE`
- **Reason:** The verification service times out during one retry, so it cannot confirm or reject the customer.

### Research point tested

Retries and an inconclusive check can increase uncertainty even when the underlying transaction is legitimate.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-023 — Phished credentials from another city

- **Status:** REVIEWED
- **Scenario family:** Account takeover
- **Research scenario:** `CLEAR_FRAUDULENT`
- **Split:** `EVALUATION`

### Hidden truth

- **Hidden real-world event:** An attacker uses credentials captured through a phishing page.
- **True state:** `FRAUDULENT`
- **Why this label is correct:** The account holder did not authorize the phone purchase.

### Scenario

The attacker signs in from another city and tries to buy an expensive phone.

### Raw amount information

- **Usual minimum:** ₹300
- **Usual maximum:** ₹4,000
- **Current amount:** ₹22,000
- **Derived `amount_deviation`:** `HIGH`
- **Reason:** The amount is far above the customer's typical spending.

### Device and location

- **Device status:** `NEW`
- **Location status:** `UNUSUAL`
- **Derived `device_location_context`:** `NEW_DEVICE_UNUSUAL_LOCATION`
- **Reason:** Both device and city are unseen in the customer's history.

### Recent activity

- **Normal maximum attempts in one hour:** 2
- **Current attempts in one hour:** 2
- **Derived `recent_velocity`:** `NORMAL`
- **Reason:** The attacker limits attempts to stay within ordinary velocity.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `FAIL`
- **Reason:** The attacker lacks the required account-holder factor.

### Research point tested

A clear takeover need not involve high velocity.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-024 — SIM swap followed by wallet funding

- **Status:** REVIEWED
- **Scenario family:** Account takeover
- **Research scenario:** `FRAUDULENT_VERIFICATION_PASS`
- **Split:** `EVALUATION`

### Hidden truth

- **Hidden real-world event:** An attacker takes control of the customer's mobile number through a SIM swap.
- **True state:** `FRAUDULENT`
- **Why this label is correct:** The attacker, not the account holder, initiates the wallet funding.

### Scenario

After the SIM swap, the attacker funds a digital wallet and can receive the customer's SMS code.

### Raw amount information

- **Usual minimum:** ₹200
- **Usual maximum:** ₹3,000
- **Current amount:** ₹10,000
- **Derived `amount_deviation`:** `HIGH`
- **Reason:** The wallet funding is well above ordinary spending.

### Device and location

- **Device status:** `NEW`
- **Location status:** `USUAL`
- **Derived `device_location_context`:** `NEW_DEVICE_USUAL_LOCATION`
- **Reason:** The attacker uses a new device but operates in the same city.

### Recent activity

- **Normal maximum attempts in one hour:** 2
- **Current attempts in one hour:** 5
- **Derived `recent_velocity`:** `HIGH`
- **Reason:** Five attempts exceed twice the normal maximum.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `PASS`
- **Reason:** The hijacked phone number receives the verification code, so the technical check passes.

### Research point tested

A passing verification can be fraudulent when the verification channel itself is compromised.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-025 — Stolen password used from same city

- **Status:** REVIEWED
- **Scenario family:** Account takeover
- **Research scenario:** `CLEAR_FRAUDULENT`
- **Split:** `EVALUATION`

### Hidden truth

- **Hidden real-world event:** An attacker uses a stolen password from within the customer's home city.
- **True state:** `FRAUDULENT`
- **Why this label is correct:** The password is stolen and the customer did not make the purchase.

### Scenario

The location appears usual at city level, but the login comes from a new device and requests a large purchase.

### Raw amount information

- **Usual minimum:** ₹500
- **Usual maximum:** ₹4,000
- **Current amount:** ₹15,000
- **Derived `amount_deviation`:** `HIGH`
- **Reason:** The amount is substantially above normal.

### Device and location

- **Device status:** `NEW`
- **Location status:** `USUAL`
- **Derived `device_location_context`:** `NEW_DEVICE_USUAL_LOCATION`
- **Reason:** Coarse location looks familiar while the device does not.

### Recent activity

- **Normal maximum attempts in one hour:** 2
- **Current attempts in one hour:** 1
- **Derived `recent_velocity`:** `NORMAL`
- **Reason:** The attacker makes only one attempt.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `FAIL`
- **Reason:** The attacker cannot complete the additional account-holder check.

### Research point tested

A usual location is weak evidence when location is coarse or attackers operate nearby.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-026 — Repeated small authorization attempts

- **Status:** REVIEWED
- **Scenario family:** Rapid-attempt/card-testing
- **Research scenario:** `RAPID_ATTEMPT_FRAUD`
- **Split:** `EVALUATION`

### Hidden truth

- **Hidden real-world event:** An attacker submits many tiny authorization requests to validate card details.
- **True state:** `FRAUDULENT`
- **Why this label is correct:** The account holder did not submit the authorizations.

### Scenario

Fifteen ₹10 attempts arrive from an unfamiliar device within an hour.

### Raw amount information

- **Usual minimum:** ₹100
- **Usual maximum:** ₹3,000
- **Current amount:** ₹10
- **Derived `amount_deviation`:** `MODERATE`
- **Reason:** The tiny amount falls outside the normal range, but it is not a large-exposure signal.

### Device and location

- **Device status:** `NEW`
- **Location status:** `UNUSUAL`
- **Derived `device_location_context`:** `NEW_DEVICE_UNUSUAL_LOCATION`
- **Reason:** Both contextual fields differ from history.

### Recent activity

- **Normal maximum attempts in one hour:** 2
- **Current attempts in one hour:** 15
- **Derived `recent_velocity`:** `HIGH`
- **Reason:** Fifteen attempts are far beyond ordinary activity.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `FAIL`
- **Reason:** The attacker cannot complete verification.

### Research point tested

Very small amounts combined with extreme velocity can represent card testing.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-027 — Stolen card tested across subscription sites

- **Status:** REVIEWED
- **Scenario family:** Rapid-attempt/card-testing
- **Research scenario:** `RAPID_ATTEMPT_FRAUD`
- **Split:** `EVALUATION`

### Hidden truth

- **Hidden real-world event:** Stolen card details are tested on several low-cost subscription merchants.
- **True state:** `FRAUDULENT`
- **Why this label is correct:** A third party is testing stolen payment details.

### Scenario

Eleven small online authorizations occur quickly. Device telemetry is new, and reliable transaction location is unavailable.

### Raw amount information

- **Usual minimum:** ₹200
- **Usual maximum:** ₹4,000
- **Current amount:** ₹79
- **Derived `amount_deviation`:** `MODERATE`
- **Reason:** The amount is below the customer's normal range and resembles a validation charge.

### Device and location

- **Device status:** `NEW`
- **Location status:** `UNKNOWN`
- **Derived `device_location_context`:** `UNKNOWN`
- **Reason:** The device is new, but the online merchant does not provide dependable location evidence; the combined field is therefore unknown.

### Recent activity

- **Normal maximum attempts in one hour:** 2
- **Current attempts in one hour:** 11
- **Derived `recent_velocity`:** `HIGH`
- **Reason:** The burst is far above the customer's normal maximum.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `INCONCLUSIVE`
- **Reason:** The merchant flow returns insufficient verification information.

### Research point tested

Card-testing evidence can remain strong even when one contextual field and verification are inconclusive.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-028 — Test payments followed by larger purchase

- **Status:** REVIEWED
- **Scenario family:** Rapid-attempt/card-testing
- **Research scenario:** `RAPID_ATTEMPT_FRAUD`
- **Split:** `EVALUATION`

### Hidden truth

- **Hidden real-world event:** An attacker makes small tests and then attempts a high-value purchase.
- **True state:** `FRAUDULENT`
- **Why this label is correct:** The account holder made none of the attempts.

### Scenario

Several tiny authorizations are followed by a ₹25,000 electronics transaction from the same new device.

### Raw amount information

- **Usual minimum:** ₹300
- **Usual maximum:** ₹4,000
- **Current amount:** ₹25,000
- **Derived `amount_deviation`:** `HIGH`
- **Reason:** The final transaction is far above the normal range.

### Device and location

- **Device status:** `NEW`
- **Location status:** `UNUSUAL`
- **Derived `device_location_context`:** `NEW_DEVICE_UNUSUAL_LOCATION`
- **Reason:** The device and location are unfamiliar.

### Recent activity

- **Normal maximum attempts in one hour:** 2
- **Current attempts in one hour:** 8
- **Derived `recent_velocity`:** `HIGH`
- **Reason:** Eight recent attempts greatly exceed normal activity.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `FAIL`
- **Reason:** The attacker cannot pass the account-holder check.

### Research point tested

A rapid testing sequence may escalate into a larger attempted loss.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-029 — Hijacked browser session on known device

- **Status:** REVIEWED
- **Scenario family:** Familiar-context fraud
- **Research scenario:** `FAMILIAR_BEHAVIOUR_FRAUD`
- **Split:** `EVALUATION`

### Hidden truth

- **Hidden real-world event:** An attacker hijacks an authenticated browser session on the customer's computer.
- **True state:** `FRAUDULENT`
- **Why this label is correct:** The attacker controls the session; the account holder did not authorize the purchase.

### Scenario

A purchase is made through a trusted browser session from home, producing familiar device and location evidence.

### Raw amount information

- **Usual minimum:** ₹500
- **Usual maximum:** ₹5,000
- **Current amount:** ₹6,000
- **Derived `amount_deviation`:** `MODERATE`
- **Reason:** The amount is only moderately above the usual range.

### Device and location

- **Device status:** `KNOWN`
- **Location status:** `USUAL`
- **Derived `device_location_context`:** `KNOWN_DEVICE_USUAL_LOCATION`
- **Reason:** The hijacked session runs on the customer's known computer at home.

### Recent activity

- **Normal maximum attempts in one hour:** 2
- **Current attempts in one hour:** 1
- **Derived `recent_velocity`:** `NORMAL`
- **Reason:** Only one transaction is attempted.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `PASS`
- **Reason:** The already authenticated session satisfies the technical check.

### Research point tested

Historical resemblance and trusted context can still accompany fraud.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-030 — Remote-access scam using customer's phone

- **Status:** REVIEWED
- **Scenario family:** Familiar-context fraud
- **Research scenario:** `KNOWN_DEVICE_FRAUD`
- **Split:** `EVALUATION`

### Hidden truth

- **Hidden real-world event:** A scammer remotely controls the customer's phone and initiates a transfer.
- **True state:** `FRAUDULENT`
- **Why this label is correct:** The transfer results from deception and is treated as unauthorized fraud in this simulated case.

### Scenario

The customer is deceived into installing remote-access software. The scammer uses the known phone from the usual home location.

### Raw amount information

- **Usual minimum:** ₹500
- **Usual maximum:** ₹5,000
- **Current amount:** ₹25,000
- **Derived `amount_deviation`:** `HIGH`
- **Reason:** The transfer is much larger than normal spending.

### Device and location

- **Device status:** `KNOWN`
- **Location status:** `USUAL`
- **Derived `device_location_context`:** `KNOWN_DEVICE_USUAL_LOCATION`
- **Reason:** The fraud occurs through the customer's real phone at home.

### Recent activity

- **Normal maximum attempts in one hour:** 2
- **Current attempts in one hour:** 2
- **Derived `recent_velocity`:** `NORMAL`
- **Reason:** Two attempts remain within the normal maximum.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `PASS`
- **Reason:** The scammer guides the customer through the check, so it passes despite deceptive authorization.

### Research point tested

Verification may confirm possession or interaction without proving informed intent.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-031 — Unauthorized purchase from shared home tablet

- **Status:** REVIEWED
- **Scenario family:** Familiar-context fraud
- **Research scenario:** `KNOWN_DEVICE_FRAUD`
- **Split:** `EVALUATION`

### Hidden truth

- **Hidden real-world event:** Another household member uses saved payment credentials without permission.
- **True state:** `FRAUDULENT`
- **Why this label is correct:** The account holder did not give permission for the purchase.

### Scenario

A shared tablet previously trusted by the account is used at home to make an unauthorized purchase.

### Raw amount information

- **Usual minimum:** ₹500
- **Usual maximum:** ₹5,000
- **Current amount:** ₹7,000
- **Derived `amount_deviation`:** `MODERATE`
- **Reason:** The amount is above normal but not extreme.

### Device and location

- **Device status:** `KNOWN`
- **Location status:** `USUAL`
- **Derived `device_location_context`:** `KNOWN_DEVICE_USUAL_LOCATION`
- **Reason:** The shared device and home location are both familiar.

### Recent activity

- **Normal maximum attempts in one hour:** 2
- **Current attempts in one hour:** 1
- **Derived `recent_velocity`:** `NORMAL`
- **Reason:** There is only one purchase.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `PASS`
- **Reason:** Saved credentials and access to the shared device allow the check to pass.

### Research point tested

A familiar device and home location do not establish who actually authorized a transaction.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-032 — Socially engineered customer approves verification

- **Status:** REVIEWED
- **Scenario family:** Misleading verification
- **Research scenario:** `FRAUDULENT_VERIFICATION_PASS`
- **Split:** `EVALUATION`

### Hidden truth

- **Hidden real-world event:** A scammer persuades the customer to approve a verification request for the scammer's transaction.
- **True state:** `FRAUDULENT`
- **Why this label is correct:** The customer did not knowingly intend the attacker's transfer.

### Scenario

The attacker initiates a large transfer and impersonates bank support, telling the customer to approve the prompt.

### Raw amount information

- **Usual minimum:** ₹500
- **Usual maximum:** ₹5,000
- **Current amount:** ₹30,000
- **Derived `amount_deviation`:** `HIGH`
- **Reason:** The transfer is far above the normal range.

### Device and location

- **Device status:** `NEW`
- **Location status:** `UNUSUAL`
- **Derived `device_location_context`:** `NEW_DEVICE_UNUSUAL_LOCATION`
- **Reason:** The transaction originates from the attacker's unfamiliar device and location.

### Recent activity

- **Normal maximum attempts in one hour:** 2
- **Current attempts in one hour:** 2
- **Derived `recent_velocity`:** `NORMAL`
- **Reason:** The number of attempts is not unusual.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `PASS`
- **Reason:** The customer approves the prompt under deception, so the check passes.

### Research point tested

A verification pass is evidence, not ground truth; social engineering can produce a misleading pass.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-033 — Legitimate customer enters expired code

- **Status:** REVIEWED
- **Scenario family:** Misleading verification
- **Research scenario:** `LEGITIMATE_VERIFICATION_FAIL`
- **Split:** `EVALUATION`

### Hidden truth

- **Hidden real-world event:** The account holder enters a code after it has expired.
- **True state:** `LEGITIMATE`
- **Why this label is correct:** The account holder intentionally initiated the purchase.

### Scenario

A normal home purchase receives a challenge, but the customer is interrupted and submits the code too late.

### Raw amount information

- **Usual minimum:** ₹200
- **Usual maximum:** ₹3,000
- **Current amount:** ₹950
- **Derived `amount_deviation`:** `NORMAL`
- **Reason:** The amount is typical.

### Device and location

- **Device status:** `KNOWN`
- **Location status:** `USUAL`
- **Derived `device_location_context`:** `KNOWN_DEVICE_USUAL_LOCATION`
- **Reason:** The normal phone and location are used.

### Recent activity

- **Normal maximum attempts in one hour:** 2
- **Current attempts in one hour:** 1
- **Derived `recent_velocity`:** `NORMAL`
- **Reason:** Activity is ordinary.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `FAIL`
- **Reason:** The correct customer uses an expired code, causing a failed result.

### Research point tested

Failed verification does not perfectly identify fraud.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-034 — Fraud attempt during verification outage

- **Status:** REVIEWED
- **Scenario family:** Misleading verification
- **Research scenario:** `MISSING_EVIDENCE`
- **Split:** `EVALUATION`

### Hidden truth

- **Hidden real-world event:** An attacker attempts a purchase while the step-up service is unavailable.
- **True state:** `FRAUDULENT`
- **Why this label is correct:** Stolen credentials are used without the account holder's authorization.

### Scenario

A new-device transaction from an unusual location arrives during a verification-system outage.

### Raw amount information

- **Usual minimum:** ₹300
- **Usual maximum:** ₹4,000
- **Current amount:** ₹18,000
- **Derived `amount_deviation`:** `HIGH`
- **Reason:** The amount is far above normal.

### Device and location

- **Device status:** `NEW`
- **Location status:** `UNUSUAL`
- **Derived `device_location_context`:** `NEW_DEVICE_UNUSUAL_LOCATION`
- **Reason:** Both context signals are unfamiliar.

### Recent activity

- **Normal maximum attempts in one hour:** 2
- **Current attempts in one hour:** 2
- **Derived `recent_velocity`:** `NORMAL`
- **Reason:** The attempt count alone is not unusual.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `UNAVAILABLE`
- **Reason:** The verification service is down, so no result can be obtained.

### Research point tested

The agent must decide under missing additional evidence rather than interpreting service failure as a pass or fail.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-035 — Fraud with missing device telemetry

- **Status:** REVIEWED
- **Scenario family:** Missing information
- **Research scenario:** `MISSING_EVIDENCE`
- **Split:** `EVALUATION`

### Hidden truth

- **Hidden real-world event:** An attacker uses a channel that does not provide reliable device telemetry.
- **True state:** `FRAUDULENT`
- **Why this label is correct:** The account holder did not authorize the purchase.

### Scenario

A high-value purchase from an unusual region arrives with the device field missing.

### Raw amount information

- **Usual minimum:** ₹300
- **Usual maximum:** ₹3,500
- **Current amount:** ₹12,000
- **Derived `amount_deviation`:** `HIGH`
- **Reason:** The amount is well above the usual range.

### Device and location

- **Device status:** `UNKNOWN`
- **Location status:** `UNUSUAL`
- **Derived `device_location_context`:** `UNKNOWN`
- **Reason:** Because device status is missing, the combined device-location category must remain unknown.

### Recent activity

- **Normal maximum attempts in one hour:** 2
- **Current attempts in one hour:** 4
- **Derived `recent_velocity`:** `ELEVATED`
- **Reason:** Four attempts exceed the normal maximum.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `INCONCLUSIVE`
- **Reason:** The available verification response is incomplete and cannot establish a result.

### Research point tested

Unknown device context must remain unknown; it should not be silently converted into new or known.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-036 — Legitimate purchase without velocity history

- **Status:** REVIEWED
- **Scenario family:** Missing information
- **Research scenario:** `MISSING_EVIDENCE`
- **Split:** `EVALUATION`

### Hidden truth

- **Hidden real-world event:** A genuine customer makes a purchase after velocity-history data was lost during migration.
- **True state:** `LEGITIMATE`
- **Why this label is correct:** The account holder knowingly makes the purchase.

### Scenario

The amount, device, and location look ordinary, but no historical hourly-attempt baseline is available.

### Raw amount information

- **Usual minimum:** ₹500
- **Usual maximum:** ₹4,000
- **Current amount:** ₹2,300
- **Derived `amount_deviation`:** `NORMAL`
- **Reason:** The amount fits the retained transaction history.

### Device and location

- **Device status:** `KNOWN`
- **Location status:** `USUAL`
- **Derived `device_location_context`:** `KNOWN_DEVICE_USUAL_LOCATION`
- **Reason:** The contextual records are available and familiar.

### Recent activity

- **Normal maximum attempts in one hour:** Not available
- **Current attempts in one hour:** 1
- **Derived `recent_velocity`:** `UNKNOWN`
- **Reason:** The current attempt count is known, but there is no normal baseline for comparison.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `PASS`
- **Reason:** The genuine customer can complete verification.

### Research point tested

One evidence field can be missing while other fields remain informative.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-037 — Fraud on newly opened account

- **Status:** REVIEWED
- **Scenario family:** Missing information
- **Research scenario:** `MISSING_EVIDENCE`
- **Split:** `EVALUATION`

### Hidden truth

- **Hidden real-world event:** A synthetic identity account is opened and immediately used for fraud.
- **True state:** `FRAUDULENT`
- **Why this label is correct:** The account was created and used with fraudulent intent.

### Scenario

The account has no meaningful amount or velocity history. Several purchases are attempted from a new device and unusual location.

### Raw amount information

- **Usual minimum:** Not available
- **Usual maximum:** Not available
- **Current amount:** ₹9,000
- **Derived `amount_deviation`:** `UNKNOWN`
- **Reason:** No historical spending range exists for comparison.

### Device and location

- **Device status:** `NEW`
- **Location status:** `UNUSUAL`
- **Derived `device_location_context`:** `NEW_DEVICE_UNUSUAL_LOCATION`
- **Reason:** The device is newly observed and the location differs from the declared profile.

### Recent activity

- **Normal maximum attempts in one hour:** Not available
- **Current attempts in one hour:** 5
- **Derived `recent_velocity`:** `UNKNOWN`
- **Reason:** Five attempts are observed, but no personal normal maximum exists.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `FAIL`
- **Reason:** The actor cannot complete the stronger identity check.

### Research point tested

Missing baselines should not be confused with reassuring normal evidence.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-038 — Normal-looking purchase after session compromise

- **Status:** REVIEWED
- **Scenario family:** Borderline/conflicting
- **Research scenario:** `FAMILIAR_BEHAVIOUR_FRAUD`
- **Split:** `EVALUATION`

### Hidden truth

- **Hidden real-world event:** An attacker studies the customer's history and imitates an ordinary purchase.
- **True state:** `FRAUDULENT`
- **Why this label is correct:** The account holder did not initiate or authorize the transaction.

### Scenario

Using a compromised session, the attacker makes one small purchase from the known device and usual location.

### Raw amount information

- **Usual minimum:** ₹500
- **Usual maximum:** ₹3,000
- **Current amount:** ₹1,800
- **Derived `amount_deviation`:** `NORMAL`
- **Reason:** The amount deliberately matches normal behaviour.

### Device and location

- **Device status:** `KNOWN`
- **Location status:** `USUAL`
- **Derived `device_location_context`:** `KNOWN_DEVICE_USUAL_LOCATION`
- **Reason:** The compromised session preserves familiar device and location signals.

### Recent activity

- **Normal maximum attempts in one hour:** 3
- **Current attempts in one hour:** 1
- **Derived `recent_velocity`:** `NORMAL`
- **Reason:** The attacker avoids rapid activity.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `PASS`
- **Reason:** The existing trusted session satisfies verification.

### Research point tested

A transaction can closely resemble history and still be fraudulent.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-039 — Expensive purchase from unusual local venue

- **Status:** REVIEWED
- **Scenario family:** Borderline/conflicting
- **Research scenario:** `BORDERLINE`
- **Split:** `EVALUATION`

### Hidden truth

- **Hidden real-world event:** The account holder buys jewellery for a family occasion.
- **True state:** `LEGITIMATE`
- **Why this label is correct:** The customer selected the jewellery and authorized payment.

### Scenario

A large purchase is made from the known phone at a jewellery store in an unfamiliar part of the same city.

### Raw amount information

- **Usual minimum:** ₹500
- **Usual maximum:** ₹4,000
- **Current amount:** ₹40,000
- **Derived `amount_deviation`:** `HIGH`
- **Reason:** The jewellery purchase is far above ordinary spending.

### Device and location

- **Device status:** `KNOWN`
- **Location status:** `UNUSUAL`
- **Derived `device_location_context`:** `KNOWN_DEVICE_UNUSUAL_LOCATION`
- **Reason:** The phone is familiar, while the specialist merchant location is new.

### Recent activity

- **Normal maximum attempts in one hour:** 2
- **Current attempts in one hour:** 1
- **Derived `recent_velocity`:** `NORMAL`
- **Reason:** There is only one attempt.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `PASS`
- **Reason:** The genuine customer can confirm the purchase.

### Research point tested

Conflicting evidence should preserve uncertainty instead of forcing a fraud label.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## CASE-040 — Same-city attacker with successful verification

- **Status:** REVIEWED
- **Scenario family:** Borderline/conflicting
- **Research scenario:** `FRAUDULENT_VERIFICATION_PASS`
- **Split:** `EVALUATION`

### Hidden truth

- **Hidden real-world event:** An attacker in the same city uses stolen credentials and a compromised verification channel.
- **True state:** `FRAUDULENT`
- **Why this label is correct:** The account holder did not authorize the transaction.

### Scenario

The location appears usual at city level. The attacker uses a new device, makes one purchase, and successfully passes the compromised check.

### Raw amount information

- **Usual minimum:** ₹500
- **Usual maximum:** ₹4,000
- **Current amount:** ₹9,000
- **Derived `amount_deviation`:** `HIGH`
- **Reason:** The amount is above the customer's normal range.

### Device and location

- **Device status:** `NEW`
- **Location status:** `USUAL`
- **Derived `device_location_context`:** `NEW_DEVICE_USUAL_LOCATION`
- **Reason:** Coarse location is familiar, but the device is not.

### Recent activity

- **Normal maximum attempts in one hour:** 2
- **Current attempts in one hour:** 1
- **Derived `recent_velocity`:** `NORMAL`
- **Reason:** A single attempt looks ordinary.

### Additional evidence if requested

- **`step_up_result_if_requested`:** `PASS`
- **Reason:** The attacker has compromised the verification channel, producing a passing result.

### Research point tested

Usual location, normal velocity, and a verification pass can coexist with fraud.

### Leakage review

Passes the common leakage checks as drafted. Only the three derived initial evidence values may be shown before a step-up request; the hidden truth and all narrative explanations remain evaluator-only.

## Manual review record

Use this table while reviewing the drafts. Do not mark a case `REVIEWED` merely because every field is filled.

| Case range | What to check | Reviewer status |
|---|---|---|
| CASE-001–CASE-010 | Review these development cases first. Revise definitions or derivation rules only if a real inconsistency is found. | NOT STARTED |
| CASE-011–CASE-040 | Keep these evaluation labels hidden while developing the policy. Review them for realism and leakage without tuning the policy to their outcomes. | NOT STARTED |

For each case, ask:

1. Could this event realistically happen?
2. Do the raw values support every derived category?
3. Is the hidden state based on authorization, rather than on whether the evidence looks suspicious?
4. Could the verification outcome realistically occur for that hidden state?
5. Are correlated signals explained without double-counting them as independent facts?
6. Would the policy see only the frozen v0.1 evidence?
7. Can you explain the case in your own words?

After reviewing a case, update its registry status to `REVIEWED`. Then copy its structured fields into the CSV and change the status to `ADDED_TO_CSV`. Use `FROZEN` only after the whole v0.1 dataset has passed consistency and leakage checks.

