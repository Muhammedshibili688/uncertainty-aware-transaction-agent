## Decision: Freeze the static baseline

### Stage

Baseline development experiment

### Evidence used

The baseline was tested on the 10 development cases from dataset v0.1.

### Result

The baseline made five automatic decisions and deferred five cases to
human review. Four automatic decisions were correct. One fraudulent
transaction was incorrectly approved, and no legitimate transaction
was stopped.

### Important failure

CASE-008 was approved because all three initial evidence values appeared
normal. The same evidence pattern also appeared in legitimate cases.
Changing the threshold cannot distinguish these cases.

### Decision

Freeze the baseline with the following thresholds:

- APPROVE: score 0–1
- HUMAN_REVIEW: score 2–3
- STOP: score 4–6

### Reason for freezing

The baseline is simple, realistic, reproducible, and produces meaningful
strengths and failures. Changing it further using these ten cases could
overfit the baseline to the development set.

### Reason for Policy 1

Policy 1 will investigate whether one additional verification result can
reduce unnecessary human reviews in uncertain score-two and score-three
cases.

### Known limitation

Policy 1 may not solve familiar-context fraud when verification also
produces a misleading PASS result.

## Decision: Policy 1 step-up design

### Question being tested

Can one selectively requested verification reduce the baseline's 50 percent
human-review rate without increasing false approvals or false stops on the ten
development cases?

### Change from the frozen baseline

Policy 1 keeps the same three initial evidence fields, point values and score
range. It changes only the treatment of the uncertain score region:

- score 0–1: APPROVE;
- score 2–3: GET_MORE_EVIDENCE;
- score 4–6: STOP.

The additional evidence is the already defined step-up verification. The
runner reveals it only after GET_MORE_EVIDENCE, and the agent may request it at
most once.

### Verification update rule

- PASS subtracts one risk point;
- FAIL adds one risk point;
- INCONCLUSIVE leaves the score unchanged;
- UNAVAILABLE leaves the score unchanged.

The updated score is kept between zero and six. The frozen terminal thresholds
are then applied: zero to one is APPROVE, two to three is HUMAN_REVIEW, and four
to six is STOP.

### Reason for a one-point change

PASS and FAIL are useful evidence, but neither proves the hidden state. A
one-point change lets the result influence a borderline decision without
allowing a single verification outcome to override all initial evidence. These
values are transparent simulation assumptions rather than calibrated fraud
probabilities or industry standards.

### Development success criteria

- human-review rate lower than the baseline's 50 percent;
- no more than the baseline's one false approval;
- no more than the baseline's zero false stops;
- verification requested only for initial scores two and three;
- no case receives more than one verification request.

### Expected limitation

Policy 1 is not expected to solve CASE-008. Its initial evidence looks normal,
so the policy approves without requesting verification. Even if verification
were requested, this simulated familiar-context fraud has a PASS result. This
is an evidence limitation, not a threshold error.

## Result: Policy 1 development experiment

### Run boundary

Policy 1 was run on the ten DEVELOPMENT cases only. The thirty EVALUATION cases
were not used. All seventeen frozen-baseline tests and fourteen Policy 1 tests
passed before the development run.

### Observed result

- six cases were approved;
- two cases were sent to human review;
- two cases were stopped;
- five cases requested step-up verification;
- eight cases received automatic terminal decisions;
- seven automatic decisions were correct;
- one fraudulent transaction was falsely approved;
- no legitimate transaction was falsely stopped.

The human-review rate fell from 50 percent to 20 percent. Automatic coverage
rose from 50 percent to 80 percent, and automatic accuracy rose from 80 percent
to 87.5 percent. Fraud recall remained 66.7 percent because Policy 1 retained
the baseline's false approval on CASE-008.

### Cases changed by verification

CASE-001, CASE-002 and CASE-004 moved from baseline HUMAN_REVIEW to Policy 1
APPROVE after PASS reduced their score from two to one. CASE-003 and CASE-010
also returned PASS, but their score moved only from three to two, so they
remained in HUMAN_REVIEW. This shows that PASS influenced the decision without
automatically overriding all initial uncertainty.

### Success-criteria check

- Human-review rate below 50 percent: MET, at 20 percent.
- False approvals no greater than one: MET, at one.
- False stops no greater than zero: MET, at zero.
- Verification only for score two or three: MET.
- No more than one verification request per case: MET.

### Development conclusion

Policy 1 met its stated development objective by reducing unnecessary review
without increasing either costly automatic error count. The result is still a
development finding rather than held-out evidence. CASE-008 remains an explicit
limitation of the frozen v0.1 evidence and is not repaired by changing Policy 1
after this run.

## Result: baseline versus Policy 1 held-out evaluation

### Frozen comparison rule

Before reading the evaluation outcomes, the comparison runner encoded the same
decision rule used during development: Policy 1 would be called better only if
it lowered human review without increasing false approvals or false stops. It
also had to request verification only for initial scores two and three, request
no more than once per case, and always finish with a terminal action.

### Run boundary

All forty-three tests passed before the evaluation command was run. The frozen
baseline and frozen Policy 1 were then run once on the same thirty EVALUATION
cases. Both policies received only the three permitted initial evidence fields.
Policy 1 saw a step-up result only after requesting it, and hidden true states
were used only by the evaluator after final decisions.

## Hypothesis: Policy 2 evidence-reliability rule

### Problem observed

Policy 1 treated every PASS verification result as equally trustworthy and
subtracted one risk point. In the held-out evaluation, this reduced unnecessary
reviews for legitimate transactions, but it also moved fraudulent CASE-030
from HUMAN_REVIEW to APPROVE.

The verification was successful because the fraud happened through the
customer's known device. Therefore, the PASS result was not independent of the
possibly compromised transaction environment.

### Research question

Can the agent reduce human review without increasing false approvals by
considering the reliability and independence of verification evidence?

### Hypothesis

If Policy 2 treats FAIL as strong warning evidence, but allows PASS to reduce
risk only when the verification comes from an independent and trustworthy
channel, it should prevent misleading PASS results from automatically approving
fraud while still resolving some legitimate uncertain transactions.

### Proposed change

Policy 2 will preserve the frozen initial evidence fields, initial risk score
and action thresholds.

For initial scores two and three, the agent may request verification.

The verification update will depend on evidence quality:

- FAIL adds one risk point;
- independent PASS subtracts one risk point;
- same-channel PASS does not change the score;
- PASS with unknown independence does not change the score;
- INCONCLUSIVE does not change the score;
- UNAVAILABLE does not change the score.

When verification does not change the score, the transaction remains in
HUMAN_REVIEW.

### Why this may work

A failed verification provides direct evidence that something may be wrong.
A successful verification is weaker because a fraudster may control the known
device, session or authentication method.

Requiring an independent confirmation prevents one potentially compromised
source from confirming itself.

### Expected result

Compared with Policy 1, Policy 2 is expected to:

- prevent score-two fraudulent transactions from being approved solely because
  of a misleading PASS;
- keep false approvals no higher than the baseline;
- preserve the useful STOP decision created by a FAIL result;
- continue reducing some human reviews when genuinely independent confirmation
  is available;
- avoid increasing false stops.

### Known limitation

Policy 2 may still miss fraudulent transactions with initial scores zero or
one because those cases contain no visible warning under the current evidence
design.

Solving that problem will require a later evidence-model update rather than
another threshold adjustment.

### Success criteria

Policy 2 will be considered better only if, on new unseen cases:

- false approvals are no higher than the baseline and lower than Policy 1;
- false stops are no higher than the baseline;
- human-review rate remains lower than the baseline;
- verification reduces risk only when its source is independent;
- no transaction receives more than the permitted number of evidence requests;
- every transaction eventually reaches APPROVE, HUMAN_REVIEW or STOP.

### Held-out results

| Metric | Baseline | Policy 1 |
|---|---:|---:|
| Approved | 11 | 14 |
| Human review | 10 | 6 |
| Stopped | 9 | 10 |
| Verification requests | 0 | 10 |
| Automatic decisions | 20 | 24 |
| Correct automatic decisions | 17 | 20 |
| False approvals | 3 | 4 |
| False stops | 0 | 0 |
| Automatic coverage | 66.7% | 80.0% |
| Automatic accuracy | 85.0% | 83.3% |
| Fraud recall | 60.0% | 66.7% |

Automatic accuracy covers only APPROVE and STOP decisions. HUMAN_REVIEW remains
deferred and is not counted as correct or incorrect.

### Changed final actions

- CASE-017 and CASE-020 were legitimate transactions that moved from
  HUMAN_REVIEW to APPROVE after PASS.
- CASE-025 was fraudulent and moved from HUMAN_REVIEW to STOP after FAIL.
- CASE-030 was fraudulent but moved from HUMAN_REVIEW to APPROVE after a
  misleading PASS.

### Evaluation conclusion

Policy 1 reduced the human-review rate from 33.3 percent to 20 percent and
improved fraud recall by stopping one additional fraudulent case. However, it
also increased false approvals from three to four and reduced automatic
accuracy from 85 percent to 83.3 percent. Because false approvals increased,
Policy 1 failed one of the frozen safety criteria and is not better than the
baseline for the complete stated objective.

This is a valid negative result. Policy 1 must not be changed and retested on
these same thirty cases as though they were still held out. Any later Policy 2
must be presented as a new design motivated by this failure and evaluated on
new unseen evidence.
