# Research File

## Two-minute reading route

This file keeps the full research trail. For a quick understanding, read these
two sections first:

1. [Current Assumptions](#13-current-assumptions) — the boundaries I used for
   the first prototype.
2. [Research Change Log](#14-research-change-log) — what I believed at the
   start, what changed and where the design ended up.

Sections 1–12 provide the questions, sources and reasoning behind those two
summaries.

## 1. Problem Statement

The agent observes an online transaction and a small set of behavioral risk
signals. It must decide whether to approve it, request more evidence, send it
for human review, or stop it because the true fraud state is unknown at
decision time.

---

## 2. Project Objective

I want to test whether explicitly representing uncertainty can reduce
unnecessary human review without causing too many fraudulent approvals or
legitimate transaction stops.

Human review is not something the agent must eliminate. The goal is to use it
mainly for cases where an automatic decision is too risky.

---

## 3. Initial Problem Formulation

This was my starting design before the first research pass.

| Component | Initial version |
|---|---|
| Input | Transaction amount deviation, device familiarity, location change |
| Possible extra evidence | Recent transaction velocity, merchant familiarity |
| Hidden states | Legitimate / Fraudulent |
| Belief | P(Fraudulent) and P(Legitimate), summing to 1 |
| Actions | APPROVE, GET_MORE_EVIDENCE, HUMAN_REVIEW, STOP |
| Costs | Fraudulent approval, legitimate stop, human review, additional evidence |
| Feedback | Analyst decision, customer confirmation, authentication result, eventual chargeback/confirmed fraud |

The prior, likelihoods, costs and thresholds were intentionally left open at
this stage. If real comparable data was unavailable, I planned to use clearly
labelled simulation assumptions.

---

## 4. Main Research Question

Can an agent that explicitly represents uncertainty and selectively obtains
additional evidence reduce human-review workload without causing an
unacceptable increase in fraudulent approvals or legitimate transaction stops?

---

## 5. Questions I Need to Answer

1. Are Legitimate and Fraudulent enough as hidden states for the first prototype?
2. Which signals are actually useful in borderline transactions?
3. Which signals create false positives when used without enough context?
4. How should correlated signals be handled without double-counting evidence?
5. What additional check is most likely to change an uncertain decision?
6. When should the agent gather more evidence instead of escalating to a human?
7. How should fraud loss, false-stop cost and human-review cost affect the policy?
8. How should priors and likelihoods be estimated when final fraud labels are delayed?
9. When does historical customer behavior stop being comparable with the current case?
10. What should happen when the available evidence still does not justify a confident automatic decision?

### Claims I still need to verify

- Location mismatch is weak when used alone.
- Step-up authentication is useful in at least some borderline cases.
- Historical similarity does not necessarily imply that a transaction is safe.
- Human-review capacity should influence how the decision policy is evaluated.

---

## 6. Technical Terms

Terms I needed to understand for the Week 1 design:

- Hidden state
- Prior probability
- Likelihood
- Posterior probability
- Bayesian updating
- Conditional probability
- Decision threshold
- Expected cost
- Cost-sensitive decision making
- Human-in-the-loop
- Abstention / selective classification
- Calibration
- Evidence dependence
- Decision latency
- Feedback latency

---

## 7. Search Queries

- transaction fraud decision making under uncertainty
- fraud false positives device location velocity
- payment fraud manual review decision
- fraud step-up authentication borderline transaction
- fraud detection false positive vs false negative cost
- Bayesian fraud detection correlated signals
- delayed fraud labels chargebacks
- historical transaction behavior concept drift

---

## 8. Findings From the Initial Research Pass

I used existing Reddit and X discussions to challenge assumptions in the
initial design. I treated these posts as practitioner observations and research
leads, not as sources for universal fraud rates or production thresholds.

### 8.1 Reddit

| Source | What I took from it |
|---|---|
| [r/fintech — Building a real-time fraud detection system](https://www.reddit.com/r/fintech/comments/1vmdem5/building_a_realtime_fraud_detection_system/) | Location and device anomalies can have legitimate explanations; deeper checks introduce latency and false-positive trade-offs |
| [r/fintech — Real-time fraud detection with AI: What's the biggest challenge?](https://www.reddit.com/r/fintech/comments/1vfxp8t/realtime_fraud_detection_with_ai_whats_the/) | Fraud decisions often depend on several weak signals rather than one isolated flag |
| [r/dataanalysis — How I backtest a fraud rule before it ships](https://www.reddit.com/r/dataanalysis/comments/1v1roxi/how_i_backtest_a_fraud_rule_before_it_ships/) | Threshold choice affects alert volume and analyst workload; labels can be delayed or biased |
| [r/PaymentProcessing — 10K+ credit card transaction discussion](https://www.reddit.com/r/PaymentProcessing/comments/1ouertk/after_analyzing_10k_credit_card_transactions_here/) | Selective verification may be preferable to broadly declining suspicious transactions |
| [r/fintech — Fraud detection in payments platform](https://www.reddit.com/r/fintech/comments/1u3crtx/fraud_detection_in_payments_platform/) | Device, velocity and history signals can help, but delayed labels and rule overload remain problems |

The Reddit pass changed five parts of the design:

- **Location mismatch became contextual evidence.** Travel, VPN use and device
  changes can make legitimate transactions look unusual, so location alone will
  not trigger STOP.

- **The agent will reason over combinations of signals.** Amount deviation,
  device familiarity, location context and recent velocity are the current
  initial evidence candidates. No single one proves fraud.

- **Human-review workload matters.** I will report review rate alongside
  fraudulent approvals, legitimate stops and total decision cost.

- **Thresholds are policy parameters.** I will test them rather than present one
  cutoff as an industry-standard value.

- **GET_MORE_EVIDENCE remains a separate action.** Customer confirmation,
  additional authentication or another useful check may resolve some borderline
  cases before human review.

Two additional problems also came out of this research. Final fraud labels such
as chargebacks can arrive late, so an unlabeled transaction is not automatically
legitimate. Historical data can also become less comparable when customer
behavior, fraud tactics or the underlying system changes.

### 8.2 X

| Source | What I took from it |
|---|---|
| [@ltvxdotai — declined payments and real-time payment intelligence](https://x.com/ltvxdotai/status/2083171719754256755?s=20) | A payment decline can have several causes and should not be treated as proof of fraud |
| [@grimicorn — Payment Fraud Detection and the False Decline Problem](https://x.com/grimicorn/status/2087903834139935183?s=20) | Risk scoring and action policy are separate; thresholds, 3DS and false-decline cost all matter |
| [@WeAreIncognia — dynamic fraud decisioning and step-up authentication](https://x.com/WeAreIncognia/status/1278404250775805952?s=20) | Extra authentication can be applied selectively instead of adding friction to every transaction |

The X research reinforced three parts of the design:

- A risk score does not determine the action by itself. APPROVE,
  GET_MORE_EVIDENCE, HUMAN_REVIEW and STOP are policy choices with different
  costs.

- Step-up authentication gives the agent an intermediate action for uncertain
  transactions instead of forcing an immediate approve-or-stop decision.

- More evidence is not free. Additional authentication can add latency,
  customer friction and operational cost.

### Current research takeaway

The initial idea was close to a simple risk-threshold system. After this
research pass, the design became:

`initial evidence → belief → additional evidence when needed → updated belief → action`

The main unresolved questions are how to handle correlated evidence, how to set
priors and likelihoods, and when an uncertain case should gather more evidence
rather than go directly to human review.

My own Reddit/X conversations are kept separately in `discussion-record.md`.

---

## 9. Relevant X Accounts

| Account | Why I follow it |
|---|---|
| @ltvxdotai | Payment approvals, declines and delayed outcomes |
| @grimicorn | Fraud scoring, thresholds, 3DS and false declines |
| @WeAreIncognia | Identity signals and step-up authentication |
| @CardNotPresent | Card-not-present fraud and authentication |
| @JavelinStrategy | Fraud and payment research |
| @ThePaypers | Payment-industry practitioners and current discussions |
| @ACI_Worldwide | Fraud-management systems and false positives |
| @NVIDIAAI | Technical fraud/ML background |

---

## 10. Useful Papers, Articles, and Case Studies

I kept five resources that directly changed how I thought about the agent.
They are not being used to justify universal fraud rates, probabilities or
thresholds.

| Resource | What I learned | Design impact |
|---|---|---|
| [Payment Fraud Detection and the False Decline Problem — Dan Holloran](https://danholloran.me/posts/payment-fraud-detection-and-the-false-decline-problem) | Fraud scoring and the policy that acts on the score are different problems. False declines also create costs that are easy to miss. | Strengthened the case for step-up verification and for tracking legitimate stops and customer friction |
| [How I backtest a fraud rule before it ships — Fixel Smith](https://analytics.fixelsmith.com/posts/backtesting-fraud-rules/) | Historical replay should measure alert volume, known outcomes, overlap with existing rules and the effect of changing thresholds. | Led me to evaluate policies using review workload and decision cost rather than accuracy alone |
| [Reducing false positives in credit card fraud detection — MIT News](https://news.mit.edu/2018/machine-learning-financial-credit-card-fraud-0920) | Blanket rules around amount or location can incorrectly flag legitimate customers because behavior differs across people. | Supports contextual, multi-signal evidence rather than a single-anomaly STOP rule |
| [A Deep Dive of Transaction Risk Analysis for Open Banking and PSD2 — Dimuth Menikgama / WSO2](https://wso2.com/articles/2019/05/a-deep-dive-of-transaction-risk-analysis-for-open-banking-and-psd2/) | Transaction context can determine whether stronger authentication is needed, while those checks also affect latency and user experience. | Supports selective additional authentication and treating friction as part of the decision |
| [Predicting payment fraud: The power of real-time analytics — SAS / Nets](https://www.sas.com/en_us/customers/nets.html) | Real-time systems can combine spending history, geolocation and device information with automated and human fraud decisions. | Supports multi-signal reasoning and selective human involvement |

These resources influenced the design, but none of their numerical values are
being treated as universal parameters for the Week 1 simulation.

---

## Research-Informed Problem Formulation

The first research pass changed several parts of the initial design.

### Initial evidence

- Amount deviation from customer history
- Device familiarity
- Location/context novelty
- Recent transaction velocity

### Possible additional evidence

- Broader customer history
- Device or funding-source reuse
- Step-up authentication / customer confirmation

### Main changes

- Location is contextual rather than a standalone fraud signal.
- Velocity moved from additional evidence to the initial evidence set.
- GET_MORE_EVIDENCE became a meaningful action before human escalation.
- Evidence acquisition now carries latency and customer-friction costs.
- Delayed or missing labels are not treated as automatic evidence of legitimacy.
- Historical behavior is not assumed to remain comparable forever.

This remains a research-informed hypothesis rather than a validated policy.
Direct human discussions are recorded separately in `discussion-record.md`.

---

## 11. AI Use Log

I keep this log to separate AI assistance from my own decisions. It shows what
I asked AI to help with, what was useful and what I did not accept. For example,
AI suggested several numerical probabilities without supporting data. I did
not use them as real fraud probabilities; I kept any unsourced numbers clearly
labelled as simulation assumptions.

| Prompt / task | What was useful | What I rejected or corrected |
|---|---|---|
| Plan the initial research for an uncertainty-aware transaction agent | Helped identify topics such as false positives, human review, verification, latency and delayed feedback | Rejected broad communities and unverified numerical claims |
| Review the Reddit research | Helped separate useful design findings from unrelated fraud material | Did not treat individual Reddit percentages as model probabilities |
| Review the X research | Helped group findings around thresholds, step-up authentication, friction and delayed feedback | Rejected vendor performance claims and the idea that successful authentication proves legitimacy |

---

## 12. AI Errors or Weak Suggestions

| AI suggestion / omission | Correction |
|---|---|
| Initial design underplayed latency | Added latency and friction as decision costs |
| Several suggested communities were too broad | Narrowed research to payments, fraud decisioning and relevant technical communities |
| Location change was initially treated as potentially strong evidence | Reframed it as contextual evidence |
| Velocity was initially treated mainly as additional evidence | Moved it into the initial evidence set |
| AI examples used arbitrary probability/threshold values | All unsourced numerical values will be labelled simulation assumptions |
| Successful authentication could be interpreted as proof of legitimacy | Authentication is treated only as evidence that updates belief |

---

## 13. Current Assumptions

These assumptions define the first prototype and may change after testing.

- The hidden state is binary: Legitimate or Fraudulent.
- Fraud subtypes such as account takeover or card testing are test scenarios, not separate hidden states in v0.
- No single signal is assumed to prove fraud.
- Some signals may be dependent, so treating every signal as independent is an assumption that must be tested.
- Priors, likelihoods, costs and thresholds will be sourced where possible; otherwise they will be clearly labelled simulation assumptions.
- APPROVE, GET_MORE_EVIDENCE, HUMAN_REVIEW and STOP are distinct actions.
- Human review and additional verification both have cost, delay and friction.
- Authentication and analyst outcomes may arrive quickly, while chargebacks and confirmed fraud can arrive much later.
- An unlabeled transaction is not automatically legitimate.
- The project estimates transaction fraud risk; it does not model every reason a payment may fail or be declined.

---

## 14. Research Change Log

| Starting idea | What changed | Current position |
|---|---|---|
| Location change could be a strong fraud signal | Legitimate travel, VPNs and device changes can produce it | Treat location as contextual evidence |
| Velocity was mainly additional evidence | It is commonly available at decision time | Move velocity into initial evidence |
| Merchant familiarity was a main extra check | Research gave stronger support to history, device/funding reuse and authentication | Replace it as the main extra-evidence candidate |
| Borderline cases would usually go directly to human review | Selective verification can resolve some cases | Keep GET_MORE_EVIDENCE before escalation |
| More evidence was assumed to be generally helpful | Additional checks introduce delay and friction | Treat evidence gathering as costly |
| Historical labels were treated as straightforward outcomes | Labels can be delayed, missing or selected by older systems | Separate provisional, delayed and unknown outcomes |
| Historical behavior was assumed to remain comparable | Customer behavior, fraud patterns and systems can change over time | Treat historical comparability as an open assumption |
