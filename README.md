# Uncertainty-Aware-Transaction-Agent

A small transaction decision-agent experiment that reasons under uncertainty.
It compares a static baseline with policies that can update risk when new
evidence becomes available, then choose whether to approve, collect more
evidence, send the case to human review, or stop the transaction.

## Problem

The agent observes an online transaction and a small set of behavioural risk
signals. It must choose one of these actions:

- approve the transaction;
- obtain additional evidence;
- send the case for human review;
- stop the transaction;

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

- `amount_deviation`
- `device_location_context`
- `recent_velocity`

### Additional evidence

- `step_up_result_if_requested`, revealed only after the agent selects
  `GET_MORE_EVIDENCE`
- `verification_independence_if_requested`, added in v0.2 and revealed with
  the requested result only to Policy 2

### Possible actions

- APPROVE
- GET MORE EVIDENCE
- HUMAN REVIEW
- STOP

## Current Status

- [x] Problem selected
- [x] Initial objective defined
- [x] Initial research file completed
- [x] Five Reddit discussion summaries recorded
- [ ] Required Reddit contribution and reply counts verified
- [ ] Required X account, comment and discussion evidence recorded
- [x] v0.1 agent specification frozen
- [x] Forty simulated cases prepared
- [x] Development and evaluation splits created
- [x] Static multi-signal baseline implemented
- [x] Baseline unit tests implemented and passing
- [x] Baseline development experiment completed
- [x] Baseline findings recorded
- [x] Policy 1 implemented
- [x] Policy 1 unit tests implemented and passing
- [x] Policy 1 development experiment completed
- [x] Policy 1 development findings recorded
- [x] Held-out comparison runner implemented and tested
- [x] Baseline and Policy 1 evaluated on the same thirty held-out cases
- [x] Held-out comparison findings recorded
- [x] Policy 2 hypothesis and v0.2 evidence contract frozen
- [x] Forty new v0.2 cases prepared with a reproducible 10/30 split
- [x] Policy 2 implemented and unit tested
- [x] Policy 2 development experiment completed
- [x] Policy 2 frozen after meeting development criteria
- [x] Policy 2 held-out runner implemented and protected against reruns
- [x] Policy 2 evaluated once on the thirty reserved v0.2 cases
- [x] Policy 2 held-out findings and artifact hashes recorded
- [x] Five final incorrect decisions analysed
- [x] Probability decision record completed
- [x] README reproduction instructions documented
- [x] Practitioner and probability AI reviews recorded
- [ ] Project-owner review dispositions confirmed
- [ ] Preprint AI review completed
- [ ] Preprint completed
- [ ] Work published

## Project Status

The frozen v0.1 baseline and Policy 1 have now been compared once on the same
thirty held-out evaluation cases. Policy 1 reduced human review from ten cases
to six and increased automatic coverage from 66.7 percent to 80 percent. It
also raised fraud recall from 60 percent to 66.7 percent.

However, Policy 1 increased false approvals from three to four, while false
stops remained zero. It therefore did not meet every predeclared success
criterion and is not considered better than the baseline for the stated v0.1
objective. In particular, a misleading PASS moved fraudulent CASE-030 from
baseline HUMAN_REVIEW to Policy 1 APPROVE. The evaluation cases are now used
evidence and must not be treated as unseen data for a modified policy.

Policy 2 v0.2 tested a narrower reliability hypothesis. It subtracts one
risk point after PASS only when the result comes from an independent channel.
SAME_CHANNEL and UNKNOWN PASS leave the score unchanged, while FAIL still adds
one point. On ten new development cases, Policy 2 reduced Policy 1's false
approvals from two to one, kept false stops at zero and used four human reviews
compared with the baseline's seven. All nine Policy 2 development criteria were
met, so the design was frozen before evaluation.

All seventy-one project tests passed before the one-time v0.2 held-out run.
Across the thirty reserved cases, Policy 2 reduced human review from the
baseline's nineteen cases to twelve and made no false stops. It also reduced
Policy 1's false approvals from seven to four, but the baseline had only three
false approvals. Because Policy 2 exceeded that frozen baseline safety limit,
it is **not better for the complete stated objective**. Its four false approvals
were P2-019, P2-023, P2-029 and P2-033.

The v0.2 evaluation cases are now seen evidence and must not be reused as unseen
data for a changed policy. Any further design requires a new version and newly
reserved evaluation cases.

## Reproducing the project

### Requirements

- Python 3.10 or newer
- Git
- No third-party Python packages; the current implementation uses the Python
  standard library

Run the commands from the repository root:

```powershell
cd "C:\VScode\Agentic AI\uncertainty-aware-transaction-agent"
python --version
```

### Run the complete automated test suite

```powershell
python -m unittest discover -s tests -v
```

The verified project state contains 71 passing tests. Tests cover score
boundaries, invalid inputs, hidden-label leakage, evidence-request limits,
dataset-split protection, freeze hashes and evaluation-output protection.

### Recreate the data splits in a development copy

These commands deterministically rewrite the split CSV files from their master
files. Run them only in a development copy if you want to preserve an entirely
clean frozen checkout.

```powershell
python .\scripts\split_cases.py
python .\scripts\split_cases_v0.2.py
```

Expected data boundaries:

| Dataset | Development | Evaluation |
|---|---:|---:|
| v0.1 | 10 | 30 |
| v0.2 | 10 | 30 |

### Run the development experiments

These commands overwrite their development result artifacts with reproducible
results:

```powershell
python .\src\run_baseline.py
python .\src\run_policy1.py
python .\src\run_policy2.py
```

Development results are written under `results/v0.1/` and `results/v0.2/`.

### Held-out evaluation rule

The v0.1 and v0.2 held-out evaluations have already been executed. Their cases
are now seen evidence. Do not rerun either evaluation and describe it as a new
unseen test.

The protected Policy 2 runner is:

```powershell
python .\src\run_policy2_evaluation.py
```

In this repository it should refuse to run because evaluation outputs already
exist. That refusal protects the recorded experiment. An independent
reproduction may run the command only in a disposable pre-evaluation copy where
the result files are absent; such a run reproduces the calculation but is not a
new held-out evaluation.

The final comparison is recorded in:

- `results/v0.2/baseline-vs-policy1-vs-policy2-evaluation-summary.md`
- `results/v0.2/policy-comparison-evaluation.json`
- `results/v0.2/policy2-evaluation-record.json`

### Metric interpretation

- A false approval is a fraudulent transaction given `APPROVE`.
- A false stop is a legitimate transaction given `STOP`.
- Human-review rate is the share sent to `HUMAN_REVIEW`.
- Automatic coverage includes only `APPROVE` and `STOP`.
- Automatic accuracy is calculated only over automatic decisions.
- `HUMAN_REVIEW` is deferred and is not counted as correct.
- The 0–6 risk score is an ordinal point score, not a probability.

## Stakeholders, limitations and human control

The main affected stakeholders are customers, merchants, issuers/payment
providers and human fraud reviewers. The simulation does not estimate how the
cost is divided among them.

Important limitations:

- all cases are designed simulations rather than sampled production traffic;
- the balanced evaluation set does not estimate real fraud prevalence;
- point scores and evidence adjustments are not calibrated probabilities;
- review-team capacity, queue time and service-level targets are not modelled;
- the system assumes verification-source independence is available and correct;
- device and behavioural familiarity cannot establish customer authorization;
- verification friction and monetary error costs are discussed but not measured.

`STOP` means stopping the individual simulated transaction. It does not mean
closing an account, accusing a customer or taking an irreversible action. A
production system would require notification, appeal, recovery and human
support procedures.
