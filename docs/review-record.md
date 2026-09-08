# AI Review Record

## How to read this file

After completing the Policy 2 evaluation, I used AI to review the project from
three angles: fraud practice, probability reasoning and preprint quality. I
treated the comments as suggestions, checked them against the project evidence
and then recorded which ones I accepted or rejected. AI supported the review;
the final decisions remain mine.

## Review 1 — Practitioner review

**AI tool:** OpenAI Codex  
**Review date:** 2026-09-04  
**Material reviewed:** README, specifications, data dictionaries, policy code,
tests, evaluation results and failure analysis.

| AI review comment | Accept or reject | Reason | Change | Evidence |
|---|---|---|---|---|
| The project uses simulated cases and should not make production-performance claims. | ACCEPT | Forty designed cases are useful for testing logic, but they do not represent a payment network or real fraud prevalence. | Kept all numerical conclusions scoped to this simulation and added an explicit README limitation. | `data/cases-v0.2.csv`; `results/v0.2/policy2-evaluation-metrics.json` |
| The affected stakeholders should be named, not reduced to one accuracy number. | ACCEPT | Customers, merchants, issuers and reviewers experience different costs. | Added stakeholder and human-control notes to the README. | `README.md`; `docs/failure-analysis.md` |
| Review workload is measured, but reviewer capacity and response time are not modelled. | ACCEPT | A 40% review rate may still be operationally impossible even when it is lower than baseline. | Recorded review capacity and latency as limitations. | `results/v0.2/policy2-evaluation-metrics.json` |
| `verification_independence` is assumed to be known perfectly. | ACCEPT | A real system needs a defensible method for identifying whether the confirmation channel is genuinely separate. | Recorded this as a deployment assumption requiring a source-provenance rule. | `data/data-dictionary-v0.2.md`; `README.md` |
| The meaning of STOP could create unnecessary harm if interpreted as closing an account. | ACCEPT | The simulation decides one transaction only. It does not justify account suspension or accusation. | Clarified that STOP is transaction-scoped and should remain reversible through human support. | `docs/v0.1-spec.md`; `README.md` |
| Add many behavioural and identity features immediately to remove every false approval. | REJECT | The evaluation cases are already seen. Adding features now and testing on the same cases would overfit and would blur what Policy 2 actually tested. | Policy 2 remains frozen. New evidence belongs to a later version with new evaluation cases. | `results/v0.2/policy2-evaluation-record.json` |
| Policy 2 should be described as successful because it improved over Policy 1. | REJECT | The frozen objective also required false approvals no higher than baseline. Policy 2 had four versus baseline's three. | Retained the negative conclusion. | `results/v0.2/policy-comparison-evaluation.json` |

### Practitioner review conclusion

The implementation is suitable as a small, auditable simulation. It is not a
production fraud system. Its strongest engineering property is the explicit
evidence boundary and frozen comparison. Its main deployment gaps are simulated
data, unmeasured operational costs, uncertain evidence provenance and the lack
of identity/consent signals for familiar-context fraud.

## Review 2 — Probability review

**AI tool:** OpenAI Codex  
**Review date:** 2026-09-04  
**Material reviewed:** risk-score implementation, v0.2 parameters, evaluation
metrics, failure analysis and probability decision record.

| AI review comment | Accept or reject | Reason | Change | Evidence |
|---|---|---|---|---|
| The 0–6 risk score is not a probability and must not be reported as one. | ACCEPT | Adding points does not produce calibrated odds, even if the score is rescaled to a percentage. | The probability record explicitly separates its Bayesian example from the implemented score. | `src/agent.py`; `decisions/probability-decision-record.md` |
| The 30% prior and verification likelihoods in the worked example are not empirically estimated. | ACCEPT | No comparable labelled production dataset is available. | Labelled every probability as a simulation assumption and prohibited population-level claims. | `decisions/probability-decision-record.md` |
| A balanced simulated evaluation set cannot estimate real fraud prevalence or calibration. | ACCEPT | The 15/15 hidden-state balance was chosen for case coverage, not sampled from real traffic. | Added this limitation to the README and probability record. | `results/v0.2/policy2-evaluation-metrics.json` |
| Independence does not guarantee verification correctness. | ACCEPT | P2-029 was fraudulent despite an independent PASS. | Made P2-029 a named failure and retained non-zero fraud likelihood after PASS. | `docs/failure-analysis.md`; `decisions/probability-decision-record.md` |
| The illustrative thresholds depend on the chosen error costs. | ACCEPT | Different fraud-loss, false-stop and review costs would move the decision boundaries. | Derived the example thresholds from declared costs and called for sensitivity analysis before use. | `decisions/probability-decision-record.md` |
| Binary LEGITIMATE/FRAUDULENT states hide fraud subtype and non-fraud payment failures. | ACCEPT AS LIMITATION | The binary state is sufficient for this small experiment but not a complete operational model. | Kept the frozen states and recorded richer states as future work. | `docs/v0.1-spec.md`; `docs/failure-analysis.md` |
| Use the evaluation labels to tune the prior and likelihoods now. | REJECT | That would leak held-out outcomes into the design and make a repeated evaluation look better without new evidence. | Evaluation labels remain analysis-only. | `results/v0.2/policy2-evaluation-record.json` |
| Report Brier score and a reliability curve for the current agent. | REJECT FOR CURRENT VERSION | The implemented agent does not emit probabilities, so probability-calibration metrics would be misleading. | Reserved calibration metrics for a future probability-producing version. | `config/v0.2-parameters.json`; `decisions/probability-decision-record.md` |

### Probability review conclusion

The project currently has two separate objects: an implemented ordinal risk
policy and one illustrative probability decision record. That separation is
correct and must remain visible. The probability example explains belief
updating, but it is not calibrated and should not be used to claim real-world
fraud risk.

## Review 3 — Preprint review

**AI tool:** OpenAI Codex

**Review date:** 2026-09-05

**Material reviewed:** `paper/week1-preprint.md` together with the frozen
specifications, result summaries, failure analysis, probability decision record
and README.

| AI review comment | Accept or reject | Reason | Change | Evidence |
|---|---|---|---|---|
| The report must not call the 0–6 score a fraud probability. | ACCEPT | The implementation ranks warning evidence but does not estimate calibrated odds. | The preprint repeatedly calls it an ordinal risk index and keeps the Bayesian exercise separate. | `src/agent.py`; `decisions/probability-decision-record.md`; `paper/week1-preprint.md` |
| The report should present Policy 2 as a negative result under the full frozen objective. | ACCEPT | Policy 2 reduced Policy 1 false approvals but still produced four compared with the baseline's three. | The abstract, results and conclusion state that Policy 2 did not beat the complete objective. | `results/v0.2/policy-comparison-evaluation.json` |
| v0.1 and v0.2 percentages should not be described as one continuous benchmark. | ACCEPT | The versions use separate designed evaluation sets. | Results are divided into separate v0.1 and v0.2 subsections; comparisons are made only within each version. | `data/cases-evaluation-v0.1.csv`; `data/cases-evaluation-v0.2.csv` |
| The meaning of the 71 tests should be explained. | ACCEPT | Readers could mistake software checks for evaluated transactions. | The reproducibility section distinguishes 71 software checks from the 10/30 transaction splits. | `tests/`; `paper/week1-preprint.md` |
| The designed and balanced cases must not support production-performance claims. | ACCEPT | Scenario coverage is not a sample of live fraud prevalence. | The abstract, dataset section and limitations scope every metric to the simulation. | `data/cases-v0.2.csv`; `paper/week1-preprint.md` |
| The failure analysis should explain mechanisms, not only list wrong predictions. | ACCEPT | Knowing why a decision failed is more useful than reporting a count alone. | The preprint groups failures into missing authorization evidence and imperfect verification reliability. | `docs/failure-analysis.md` |
| Public-discussion requirements should be presented as complete because ten Reddit links exist. | REJECT | Ten contribution links do not prove that five discussions received two replies, and they do not complete the X requirement. | The preprint and discussion audit retain an explicit incomplete status. | `docs/discussion-record.md` |
| The report should propose Policy 3 thresholds using the revealed evaluation cases. | REJECT | Those cases are now seen; tuning on them would weaken the experimental boundary. | Future work requires a new version and new unseen evaluation cases. | `results/v0.2/policy2-evaluation-record.json` |

### Preprint review conclusion

The preprint matches the frozen policies and recorded metrics. It separates the
point score from probability, keeps the failed success criterion visible and
states the limits of the simulation. I still need to complete my own final read
before publication. Public-discussion evidence remains a separate requirement.

## My final check

- [ ] I read all three reviews and can explain each accepted and rejected comment.
- [ ] I checked that no review comment silently changed frozen Policy 2.
- [ ] I confirmed that all probabilities and costs without comparable data are
  labelled simulation assumptions.
- [ ] I read the preprint and confirmed that its claims match the recorded
  results and limitations.

I will treat these as final project decisions only after completing the checks
above.
