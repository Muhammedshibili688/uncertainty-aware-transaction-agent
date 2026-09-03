# Policy 2 Hypothesis: Verification Reliability

Version: v0.2  
Status: FROZEN BEFORE IMPLEMENTATION  
Freeze date: 2026-09-02

## 1. Observation from Policy 1

Policy 1 reduced human review, but it increased false approvals from three to
four on the held-out v0.1 evaluation cases. The important new failure was
CASE-030. That fraudulent transaction began with risk score two and received a
PASS from the same potentially compromised environment. Policy 1 subtracted
one point and approved it.

Other observations were also important:

- FAIL helped move fraudulent CASE-025 from review to STOP;
- PASS safely approved legitimate CASE-017 and CASE-020;
- PASS did not automatically approve score-three CASE-040;
- three other fraudulent cases already had score zero or one and never
  requested verification.

The experiment therefore revealed two different limitations. Policy 2 focuses
on misleading PASS evidence. Low-score familiar-context fraud remains a known
evidence-coverage limitation and is not silently claimed as solved.

## 2. Research question

Can an agent preserve some of Policy 1's review reduction without increasing
false approvals by considering whether a PASS comes from an independent source?

## 3. Frozen hypothesis

If Policy 2 treats FAIL as warning evidence but allows PASS to reduce risk only
when the verification comes from an independent channel, then it should avoid
some misleading-PASS approvals while still automatically resolving legitimate
uncertain cases that receive genuinely independent confirmation.

## 4. Single intended change

Policy 2 keeps the baseline evidence categories, point values, score range and
terminal thresholds. It also keeps Policy 1's one-request limit and its request
region of scores two and three.

The only policy change is how PASS is interpreted:

- independent PASS: subtract one point;
- same-channel PASS: no score change;
- PASS with unknown independence: no score change;
- FAIL: add one point;
- INCONCLUSIVE or UNAVAILABLE: no score change.

This is an asymmetric rule. A failed check is treated conservatively as a
warning. A successful check is reassuring only when it is independent of the
environment that may be compromised.

## 5. Development success criteria

On the new v0.2 development cases, Policy 2 should:

- produce fewer false approvals than Policy 1 on the same cases;
- produce no more false approvals than the baseline on the same cases;
- keep false stops no higher than the baseline;
- keep human review lower than the baseline;
- allow at least one legitimate score-two case with independent PASS to be
  approved;
- never lower risk for SAME_CHANNEL or UNKNOWN PASS;
- request verification only for initial scores two and three;
- request verification at most once per case;
- finish every case with APPROVE, HUMAN_REVIEW or STOP.

Meeting these development criteria supports freezing the mechanism. It does not
prove held-out performance.

## 6. Known limitations

Policy 2 cannot distinguish every familiar-context fraud from a legitimate
transaction. A fraudulent score-zero or score-one case still receives APPROVE
without verification because the current initial evidence contains no warning.
Fixing that problem would require a later evidence change such as session
integrity, remote-access detection or another explicitly modelled signal.

The risk points are transparent experimental assumptions. They are not
calibrated fraud probabilities and are not presented as banking standards.

## 7. Evaluation boundary

Policy 2 may be developed using only the ten v0.2 DEVELOPMENT cases. The thirty
v0.2 EVALUATION cases must remain unused until Policy 2 is implemented, tested,
analysed on development data and frozen. If Policy 2 is changed after a future
evaluation, those evaluation cases are no longer unseen.

## 8. Post-freeze development outcome

After this hypothesis was frozen, all sixty-three project tests passed and
Policy 2 was run on the ten v0.2 DEVELOPMENT cases. It produced one false
approval compared with Policy 1's two on the same cases. It kept human review
at four cases compared with the baseline's seven and produced no false stops.
All nine predeclared development criteria were met.

Policy 2 is therefore frozen after development. The thirty v0.2 EVALUATION
cases have not been executed and remain reserved.
