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