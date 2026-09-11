# Uncertainty-Aware Transaction Agent

This project studies a simple question: **when should a transaction agent act,
and when should it ask for more evidence?**

The agent does not know whether a transaction is legitimate or fraudulent when
it makes its decision. It uses visible warning signals, may request one
verification, and then chooses `APPROVE`, `HUMAN_REVIEW`, or `STOP`.

> **Current conclusion:** Policy 2 made verification safer than Policy 1, but it
> did not beat the baseline on every frozen success criterion. This is a useful
> negative result, not a production fraud-detection claim.

## Project at a glance

| Question | Answer |
|---|---|
| What is hidden? | Whether the transaction is `LEGITIMATE` or `FRAUDULENT` |
| What can the agent initially see? | Amount deviation, device/location context and recent velocity |
| What may it request? | One step-up verification result |
| What changed in v0.2? | The agent also considers whether a PASS came from an independent channel |
| What can it do? | `APPROVE`, `GET_MORE_EVIDENCE`, `HUMAN_REVIEW`, `STOP` |
| Is the score a probability? | No. It is a transparent 0–6 risk-point ranking |
| Is this production performance? | No. Results come from small, designed simulation cases |

## Architecture

![Uncertainty-aware transaction-agent architecture](docs/architecture.png)

The diagram shows the decision boundary in simple terms. The agent sees the
transaction evidence and may request one verification before choosing a final
action. The legitimate/fraudulent state remains hidden until the evaluator
checks the completed decision.

## How the policies evolved

| Version | What it does | Why it was introduced |
|---|---|---|
| Baseline | Adds points from three initial signals and applies fixed action bands | Provides a simple, explainable comparison point |
| Policy 1 | Requests one verification for scores 2–3; PASS lowers risk and FAIL raises it | Tests whether one extra check can resolve uncertain cases |
| Policy 2 | Lowers risk only when PASS comes from an independent channel | Prevents a compromised device from confirming its own transaction |

Policy 2 still treats an independent PASS as evidence rather than proof. This
matters because one fraudulent evaluation case passed the independent check.

## Experiment design

Each dataset version contains 40 manually reviewed simulation cases:

| Dataset | Used to design and debug | Reserved for one-time evaluation |
|---|---:|---:|
| v0.1 | 10 cases | 30 cases |
| v0.2 | 10 cases | 30 cases |

The policy was frozen after development and before its evaluation cases were
opened. Once evaluated, those cases became seen evidence and cannot be reused
as an unseen test for a modified policy.

## Held-out results

The two tables belong to different designed datasets. Compare policies within
one table; do not treat v0.1 and v0.2 as one continuous benchmark.

### v0.1 evaluation: Baseline versus Policy 1

| Policy | Human reviews | False approvals | False stops | Automatic coverage |
|---|---:|---:|---:|---:|
| Baseline | 10 | 3 | 0 | 66.7% |
| Policy 1 | 6 | 4 | 0 | 80.0% |

Policy 1 handled more transactions automatically, but it approved one more
fraudulent transaction. It therefore failed the complete objective.

### v0.2 evaluation: Baseline versus Policy 1 versus Policy 2

| Policy | Human reviews | False approvals | False stops | Automatic coverage |
|---|---:|---:|---:|---:|
| Baseline | 19 | 3 | 0 | 36.7% |
| Policy 1 | 7 | 7 | 0 | 76.7% |
| Policy 2 | 12 | 4 | 0 | 60.0% |

Policy 2 corrected several unsafe same-channel approvals from Policy 1. It also
used fewer human reviews than the baseline. However, its four false approvals
were still above the baseline limit of three, so Policy 2 was **not declared
the winner**.

## What the failures taught us

| Lesson | Plain-language meaning |
|---|---|
| Possession is not authorization | A familiar phone may still be used by the wrong person |
| Familiar behaviour is not proof | Fraud can resemble the customer's normal activity |
| Same-channel confirmation can be circular | A compromised device should not confirm itself |
| Independent checks can still fail | Separation improves evidence quality but does not guarantee truth |

The full case-by-case analysis is in
[`docs/failure-analysis.md`](docs/failure-analysis.md).

## Week 1 completion status

| Area | Status |
|---|---|
| Research, frozen specifications and datasets | Complete |
| Baseline, Policy 1 and Policy 2 implementation | Complete |
| Development and held-out evaluation | Complete |
| Automated checks | 71 tests passed in the last verified run |
| Failure and probability analysis | Complete |
| Practitioner, probability and preprint AI reviews | Complete; my final confirmation is still required |
| Week 1 preprint | Complete draft; final proofreading still required |
| Reddit evidence | 10 contribution links recorded; reply-count target still incomplete |
| X participation evidence | Incomplete |
| Publication | Not completed |

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

### Cost interpretation

The current comparison reports false approvals, false stops, human reviews and
verification requests separately. It does not claim a monetary saving because
the project has no reliable real-world cost for any of those outcomes.

The probability decision record contains one illustrative cost example, but
those numbers are simulation assumptions. A future cost-sensitive version
should choose and justify its costs before evaluation, calculate total cost on
new unseen cases and show how the conclusion changes under other reasonable
cost choices.

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
