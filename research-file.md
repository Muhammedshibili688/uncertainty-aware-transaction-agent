# Research File

## 1. Problem Statement

The agent observes an online transaction and a small set of behavioral risk
signals. It must choose one from 
    [
        approve the transaction, 
        obtain additional evidence, 
        send it for human review, 
        or stop it
    ] 
because whether the transaction is genuinely
fraudulent is not known at decision time.

---

## 2. Project Objective

The objective is to test whether an uncertainty-aware transaction policy can
reduce unnecessary human reviews compared with simpler decision policies while
controlling two costly errors:

1. Approving a fraudulent transaction.
2. Stopping a legitimate transaction.

Human review is treated as useful but costly rather than something that should
be completely eliminated.

The experiment will investigate whether the agent can automate clearer cases,
seek more evidence when uncertainty may be reduced, and reserve human review
for cases where the cost of an incorrect automatic decision is too high.

---

## 3. Initial Problem Formulation

### Input

The initial version of the agent will use a small set of transaction and
behavioral signals.

Initial evidence:

- Transaction amount deviation
- Device familiarity
- Location change

Possible additional evidence:

- Recent transaction velocity
- Merchant familiarity

These signals are provisional and may change after research and discussions
with practitioners.

### Hidden States

For the first version, the hidden state is intentionally binary:

- H1: Legitimate transaction
- H2: Fraudulent transaction

The true state is not assumed to be known when the agent makes its decision.

### Belief

The agent will maintain probabilities such as:

- P(Fraudulent)
- P(Legitimate)

The probabilities must sum to 100%.

Exact prior probabilities and evidence likelihoods have not yet been selected.
They will initially be treated as clearly labelled assumptions or derived from
comparable sample data where appropriate.

### Actions

The initial action space is:

- APPROVE
- GET MORE EVIDENCE
- HUMAN REVIEW
- STOP

### Main Costs

The first version will consider at least:

- Cost of approving fraud
- Cost of stopping a legitimate transaction
- Cost of human review
- Cost of obtaining additional evidence

Exact numerical costs have not yet been assigned.

### Feedback

Possible feedback after a decision may include:

- Human analyst decision
- Chargeback or confirmed fraud report
- Customer confirmation
- Successful additional authentication

The Week 1 prototype does not yet assume that feedback automatically retrains
the agent.

---

## 4. Main Research Question

Can an agent that explicitly represents uncertainty and selectively obtains
additional evidence reduce human-review workload without causing an
unacceptable increase in fraudulent approvals or legitimate transaction stops?

---

## 5. Questions I Need to Answer

### Hidden State and Evidence

- Are "legitimate" and "fraudulent" sufficient hidden states for the first
  experiment?
- Which transaction signals are genuinely useful when a case is ambiguous?
- Which commonly used signals are misleading when considered alone?
- Which pieces of evidence are strongly correlated?
- Which additional evidence can meaningfully change a transaction decision?

### Human Review

- When should an uncertain transaction be sent to a human?
- What types of transactions should never be automatically stopped?
- What information does a human reviewer use that this agent may not have?
- When is gathering more evidence preferable to immediate human review?

### Cost

- Which error is usually more expensive: approving fraud or stopping a
  legitimate transaction?
- How should human-review cost be represented?
- Should the action threshold change when transaction value changes?

### Historical Evidence

- Which historical transactions are actually comparable with the current case?
- How old can historical behavior become before it should receive less weight?
- How should the agent behave for a new customer with little history?

### Probability

- How should the initial fraud prior be selected?
- How should evidence likelihoods be estimated for the prototype?
- How should correlated evidence be handled without double-counting risk?
- What probability ranges should lead to approve, investigate, human review,
  or stop?

---

## 6. Technical Terms

To be researched and verified.

Possible starting terms:

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
- Selective classification
- Abstention
- Calibration
- Evidence dependence
- Decision latency
- Evidence acquisition cost
- Human-review latency
- Time-to-decision

Each term will be kept only if it is useful to the actual agent design.

---

## 7. Search Queries

To be expanded during research.

Starting queries:

- transaction fraud decision making under uncertainty
- fraud detection human review decision threshold
- cost of false positive fraud detection
- cost sensitive fraud detection false negatives false positives
- transaction fraud Bayesian probability evidence
- fraud detection human in the loop review
- fraud risk model calibration
- transaction fraud behavioral signals device velocity location
- correlated fraud signals probability
- selective classification fraud detection

---

## 8. Preliminary Findings From Public Discussions

These findings come from existing Reddit and X discussions reviewed during the
initial research stage. They are treated as practitioner observations and
research leads rather than verified universal facts.

### 8.1 Reddit Research Findings

The first Reddit research pass focused on transaction-level fraud signals,
false positives, manual review, additional verification, threshold selection,
analyst workload, delayed outcomes, and the use of historical transaction data.

The purpose of this research was not to obtain universal fraud statistics from
Reddit. I looked for practitioner experiences and technical discussions that
could challenge assumptions in the transaction-agent design.

### Primary Reddit Sources Reviewed

| Community | Post / discussion | Link | Main contribution to this project |
|---|---|---|---|
| r/fintech | Building a real-time fraud detection system | https://www.reddit.com/r/fintech/comments/1vmdem5/building_a_realtime_fraud_detection_system/ | Legitimate travel/VPN behavior, latency vs false-positive trade-off, deeper checks |
| r/fintech | Real-time fraud detection with AI: What's the biggest challenge? | https://www.reddit.com/r/fintech/comments/1vfxp8t/realtime_fraud_detection_with_ai_whats_the/ | Multi-signal reasoning, changing fraud behavior, false positives, proportional actions |
| r/dataanalysis | How I backtest a fraud rule before it ships | https://www.reddit.com/r/dataanalysis/comments/1v1roxi/how_i_backtest_a_fraud_rule_before_it_ships/ | Threshold testing, analyst capacity, label bias, historical comparability, delayed outcomes |
| r/PaymentProcessing | After analyzing 10K+ credit card transactions, here are 5 fraud patterns that most payment systems miss | https://www.reddit.com/r/PaymentProcessing/comments/1ouertk/after_analyzing_10k_credit_card_transactions_here/ | Transaction signals, selective verification, avoiding broad automatic declines |
| r/fintech | Fraud detection in payments platform | https://www.reddit.com/r/fintech/comments/1u3crtx/fraud_detection_in_payments_platform/ | Device/velocity signals, delayed labels, rule overload, false-positive management |

---

### Finding 1 — Location mismatch should not be treated as sufficient evidence of fraud

The Reddit research showed that legitimate customers may appear geographically
unusual because of:

- travel;
- VPN use;
- device changes;
- unusual but legitimate purchasing behavior.

One suspicious geographic signal therefore does not necessarily justify
stopping a transaction.

#### Design impact

Geographic/location mismatch will be treated as contextual evidence rather than
a standalone STOP condition.

The agent should combine location information with other evidence such as:

- device familiarity;
- transaction velocity;
- amount deviation;
- historical customer behavior.

Primary sources:

- r/fintech — Building a real-time fraud detection system
- r/fintech — Real-time fraud detection with AI: What's the biggest challenge?

---

### Finding 2 — Fraud decisions should use combinations of signals

Several Reddit discussions referred to combinations of transaction and
behavioral signals including:

- transaction velocity;
- device information;
- geographic information;
- historical behavior;
- account activity;
- funding-source reuse;
- transaction amount.

This suggests that the difficult cases are not transactions with one obvious
fraud indicator, but cases where several weak or conflicting pieces of evidence
must be interpreted together.

#### Design impact

The current initial evidence candidates are:

- transaction amount deviation from customer history;
- device familiarity;
- geographic/location mismatch;
- recent transaction velocity.

No individual signal will automatically determine that the transaction is
fraudulent.

Primary sources:

- r/fintech — Fraud detection in payments platform
- r/fintech — Real-time fraud detection with AI: What's the biggest challenge?
- r/PaymentProcessing — 10K+ credit card transaction analysis

---

### Finding 3 — Human-review capacity is part of the decision problem

The fraud-rule backtesting discussion showed that a rule can appear useful while
still creating so many alerts that it consumes a large portion of available
analyst capacity.

This means that fraud detection quality cannot be evaluated only by asking how
many fraudulent transactions a policy identifies.

The amount of human work created by the policy also matters.

#### Design impact

Human-review rate will be treated as an experimental metric.

The Week 1 experiment will compare policies using measures such as:

- fraudulent approvals;
- legitimate stops;
- human-review rate;
- total decision cost.

The objective is therefore to reduce unnecessary human review rather than to
remove humans completely.

Primary source:

- r/dataanalysis — How I backtest a fraud rule before it ships

---

### Finding 4 — Decision thresholds should be tested rather than chosen arbitrarily

The Reddit backtesting discussion showed that changing a threshold changes both:

- the amount of fraud detected;
- the amount of analyst work or legitimate activity affected.

It also argued that there is not necessarily one mathematically perfect
threshold because the useful cutoff depends on factors such as fraud cost,
analyst capacity, and confidence in available labels.

#### Design impact

The Week 1 prototype will not claim that one numerical threshold is an industry
standard.

Thresholds for:

- APPROVE;
- GET_MORE_EVIDENCE;
- HUMAN_REVIEW;
- STOP

will be experimental policy parameters.

Alternative policies will later be compared on the same simulated cases.

Primary source:

- r/dataanalysis — How I backtest a fraud rule before it ships

---

### Finding 5 — Additional evidence can be preferable to immediate rejection or human review

Reddit discussions described several situations in which uncertain transactions
can receive additional verification instead of being immediately declined.

Examples encountered during research included:

- customer confirmation;
- additional authentication;
- deeper transaction-history checks;
- device or funding-source checks.

The research also suggested that broad automatic declines can create false
positives and that verification can be applied selectively to higher-risk
cases.

#### Design impact

GET_MORE_EVIDENCE remains a separate agent action.

The conceptual policy becomes:

initial evidence
→ update belief
→ uncertainty remains
→ obtain one useful additional piece of evidence
→ update belief again
→ APPROVE / HUMAN_REVIEW / STOP

The prototype will simulate additional evidence rather than implement real
payment authentication.

Primary sources:

- r/PaymentProcessing — 10K+ credit card transaction analysis
- r/fintech — Fraud detection in payments platform
- r/fintech — Real-time fraud detection with AI: What's the biggest challenge?

---

### Finding 6 — Fraud feedback can be delayed and labels can be biased

The Reddit research showed two related problems.

First, strong fraud outcomes such as chargebacks may become available only
after the original transaction decision.

Second, historical labels may themselves be biased because transactions are
more likely to receive analyst dispositions when earlier fraud rules already
flagged them.

A transaction without a known outcome therefore cannot automatically be
treated as legitimate.

#### Design impact

The project will distinguish between:

#### Provisional feedback

- customer confirmation;
- authentication result;
- analyst disposition.

#### Delayed outcome

- chargeback;
- confirmed fraud report.

#### Unknown

- no mature outcome yet.

The project will also treat historical labels cautiously when defining priors
or evaluating policies.

Primary sources:

- r/dataanalysis — How I backtest a fraud rule before it ships
- r/fintech — Fraud detection in payments platform

---

### Finding 7 — Historical evidence is not automatically comparable with the current transaction

The backtesting research also showed that using a longer historical window is
not always better.

Historical transactions may become less representative when:

- customer behavior changes;
- fraud patterns change;
- device-tracking logic changes;
- checkout systems change;
- seasonal conditions differ.

#### Design impact

Historical comparability will remain an explicit research question.

The project will not assume that every old transaction should contribute equally
to the prior or current fraud belief.

Primary source:

- r/dataanalysis — How I backtest a fraud rule before it ships

---

### Finding 8 — Evidence acquisition has a latency cost

The Reddit research introduced a trade-off between fast initial checks and
slower, deeper checks.

A deeper fraud check may provide more useful information but can also delay the
transaction and increase customer friction.

#### Design impact

The decision model will include:

- decision latency;
- evidence-acquisition cost;
- human-review latency;
- customer friction.

This strengthens the idea that GET_MORE_EVIDENCE should be selected only when
the expected value of the additional information justifies its cost.

Primary source:

- r/fintech — Building a real-time fraud detection system

---

### Other Reddit Material Reviewed

Additional Reddit discussions were reviewed but are not treated as primary
sources for the current agent design.

| Community | Topic | Status / use |
|---|---|---|
| r/stripe | Card testing, repeated attempts, rate limiting and processor fraud controls | Useful for transaction-velocity scenarios |
| r/DataScientist | Extreme class imbalance and fraud-model evaluation | Useful technical background; not central to Week 1 agent policy |
| r/shopify | Merchant responses to high-risk orders and manual verification | Useful merchant/HITL perspective |
| r/Banking | Payment and decline behavior | Possible source for user/issuer perspectives |
| r/hubspot | Multi-signal anomaly discussions | Peripheral; use only if directly relevant |
| r/NDIS | Manual payment-integrity reviews | Reviewed but excluded from the core project because it concerns claims/audit workflows rather than transaction-level card fraud |

Numerical fraud rates, thresholds, or performance claims made by individual
Reddit users will not be treated as verified industry values unless they can be
independently supported by a stronger source.

These findings changed the initial design from a simple risk-threshold system
toward a policy that explicitly represents uncertainty, selectively gathers
additional evidence, considers the cost of human review and latency, and
distinguishes provisional feedback from delayed ground truth.

### 8.2 X Research Findings

The first X research pass focused on payment fraud, false declines, transaction
risk signals, decision thresholds, step-up authentication, customer friction,
real-time decision making, and delayed fraud feedback.

The goal was not to obtain universal fraud statistics from X. Instead, I looked
for practitioner observations and technical discussions that could challenge
or change the design of the transaction agent.

### Primary X Sources Reviewed

| Account | Post / topic | Link | Main contribution to this project |
|---|---|---|---|
| @ltvxdotai | Colin Martin / RouteSense discussion on declined payments and real-time payment intelligence | https://x.com/ltvxdotai/status/2083171719754256755?s=20 | Different causes of payment declines; delayed fraud feedback; importance of contextual payment information |
| @grimicorn | Payment Fraud Detection and the False Decline Problem | https://x.com/grimicorn/status/2087903834139935183?s=20 | Risk signals; thresholds as policy; 3-D Secure; false-decline cost; customer friction |
| @WeAreIncognia | Dynamic fraud decisioning and step-up authentication | https://x.com/WeAreIncognia/status/1278404250775805952?s=20 | Risk-based use of additional authentication rather than applying friction to every transaction |

### Finding 1 — A payment decline is not automatically evidence of fraud

The material reviewed on X showed that declined payments can have different
causes. A transaction may be declined because of fraud controls, issuer
decisioning, cardholder circumstances, or other contextual factors.

This means that the outcome "payment declined" should not itself be treated as
proof that the hidden state is fraudulent.

#### Design impact

The Week 1 agent will estimate whether the transaction itself is legitimate or
fraudulent.

Other causes of payment failure are outside the current hidden-state model.

The prototype will therefore not use:

payment declined = fraudulent

as a decision rule.

Primary source:
@ltvxdotai

---

### Finding 2 — Fraud decisions depend on multiple contextual signals

The X research repeatedly identified combinations of signals rather than one
isolated indicator.

Examples included:

- device information;
- transaction velocity;
- transaction amount;
- card or issuer attributes;
- geographic or address information;
- behavioral information;
- previous transaction history.

#### Design impact

The prototype will not use a single suspicious signal as sufficient evidence
for a STOP decision.

The current initial evidence candidates are:

- transaction amount deviation from customer history;
- device familiarity;
- geographic/location mismatch;
- recent transaction velocity.

The exact probability contribution of each signal has not yet been assigned.

Primary source:
@grimicorn

---

### Finding 3 — Risk thresholds are policy decisions

One X discussion separated two different parts of the system:

1. producing a risk score;
2. deciding what action should follow from that score.

The action threshold represents a trade-off between accepting fraud and
incorrectly stopping legitimate customers.

There is therefore no reason to assume that one fixed threshold is universally
correct.

#### Design impact

The thresholds for:

- APPROVE;
- GET_MORE_EVIDENCE;
- HUMAN_REVIEW;
- STOP

will be treated as experimental policy parameters.

Any numerical thresholds used in the Week 1 simulation will be clearly marked
as assumptions rather than industry-standard values.

Different policies will later be compared using their resulting errors, costs,
and review workload.

Primary source:
@grimicorn

---

### Finding 4 — Step-up authentication provides an intermediate action

The X research showed that transaction handling does not need to be restricted
to a binary APPROVE or STOP choice.

For transactions that remain uncertain, an additional authentication step can
provide more evidence before a final action is taken.

Examples encountered during research included:

- one-time passcode;
- biometric confirmation;
- confirmation through a banking application.

#### Design impact

This finding strengthens GET_MORE_EVIDENCE as a core action in the agent.

The conceptual process becomes:

initial evidence
→ current belief
→ uncertainty remains
→ obtain one useful additional piece of evidence
→ update belief
→ approve, review, or stop

The Week 1 prototype will simulate the result of additional authentication. It
will not implement a real authentication system.

Primary sources:
@grimicorn
@WeAreIncognia

---

### Finding 5 — Additional evidence creates latency and customer friction

Additional verification can reduce uncertainty, but obtaining more information
is not free.

Authentication challenges and other checks may:

- delay the transaction;
- create additional user interaction;
- increase customer friction;
- cause abandonment;
- consume operational resources.

Therefore, gathering more evidence should not automatically be considered the
best action whenever uncertainty exists.

#### Design impact

The agent's cost model will consider:

- fraudulent approval cost;
- legitimate transaction stop cost;
- evidence-acquisition cost;
- human-review cost;
- decision latency;
- customer friction.

This introduces an additional policy question:

"Is the expected value of this additional evidence greater than the latency,
friction, and operational cost of obtaining it?"

Primary sources:
@grimicorn
@WeAreIncognia

---

### Finding 6 — Final fraud feedback can arrive after the original decision

The X research also showed that strong fraud outcomes may not be available when
the original transaction decision is made.

Fraud confirmation may arrive later, while some other signals may become
available sooner.

#### Design impact

The prototype will conceptually distinguish between:

#### Provisional feedback

- step-up authentication result;
- customer confirmation;
- human analyst disposition.

#### Delayed outcome

- chargeback;
- confirmed fraud report.

A transaction with no mature outcome will not automatically be considered
legitimate.

This introduces feedback latency as an explicit limitation of the decision
process.

Primary source:
@ltvxdotai

---

### Other X Material Reviewed

The following accounts or posts were also encountered during the initial X
research. They helped identify recurring themes or possible sources for further
discussion, but they did not independently cause a major design change.

| Account | Topic observed | How it may be useful |
|---|---|---|
| @CardNotPresent | Card-not-present fraud, authentication, and false declines | Further research on the trade-off between fraud prevention and legitimate declines |
| @JavelinStrategy | Authentication, fraud prevention, and customer friction | Potential research reports and practitioner discussion |
| @ThePaypers | Payment fraud and customer-friction discussions | Industry context and possible practitioners to follow |
| @ACI_Worldwide | Fraud management and false-positive reduction | Vendor perspective; numerical claims require independent verification |
| @NVIDIAAI | ML infrastructure and fraud-detection technologies | Technical background, but not central to the Week 1 decision policy |
| @BlueSnapInc | Card-not-present false declines | Additional context for false-decline research |
| @INETCOInsight | Real-time fraud detection and customer friction | Potential source for latency and operational trade-offs |
| @Vibhansh_mehta | User report of a legitimate transaction being treated as fraud | Anecdotal example of customer impact |

Claims from individual X posts, vendor accounts, and promotional material will
not be treated as authoritative numerical evidence without independent
verification.

---

## 9. Relevant X Accounts

The purpose of following relevant X accounts is to find practitioners,
engineers, researchers, users, and critics who can challenge the assumptions in
the project.

The goal is not to collect followers or generic AI/fraud content.

| Account | Role / relevance | Verified relevant? | Notes |
|---|---|---|---|
| @ltvxdotai | Payment infrastructure, approval/decline behavior, real-time payment intelligence | Yes | Primary research source; useful for payment-decision context and delayed feedback |
| @grimicorn | Payment fraud, risk scoring, 3DS, thresholds and false declines | Yes | Primary research source; directly relevant to the agent policy |
| @WeAreIncognia | Identity, behavioral risk and step-up authentication | Yes | Primary research source; relevant to GET_MORE_EVIDENCE and friction |
| @CardNotPresent | Card-not-present payments and fraud | Yes | Useful for false-decline and authentication discussions |
| @JavelinStrategy | Payments and fraud research | Yes | Useful for reports on fraud, authentication and customer friction |
| @ThePaypers | Payment industry publication | Yes | Useful for identifying practitioners and current payment-risk discussions |
| @ACI_Worldwide | Payment and fraud-management technology | Yes | Vendor perspective; useful but claims should be independently checked |
| @NVIDIAAI | AI/ML infrastructure and fraud-detection examples | Yes | Technical background; lower priority for Week 1 policy design |

Additional accounts will be added during the discussion phase if their recent
posts are directly relevant to:

- uncertainty;
- fraud decisioning;
- false declines;
- evidence gathering;
- human review;
- customer friction;
- latency;
- calibration.

The final set should include a mixture of practitioners, engineers,
researchers, users, and critics rather than only fraud-technology vendors.

---

## 10. Useful Papers, Articles, Repositories, or Datasets

The following resources were encountered during the initial research.

They are useful because they address specific questions in the agent design
rather than simply describing fraud detection in general.

| Resource | Type | What I learned | Design impact |
|---|---|---|---|
| Payment Fraud Detection and the False Decline Problem — Danny Holloran | Article | Transaction risk decisions use contextual signals; thresholds determine the action after scoring; 3DS can provide an intermediate challenge; false declines create costs that are difficult to observe | Strengthened GET_MORE_EVIDENCE and added false-stop, friction and latency costs |
| How I backtest a fraud rule before it ships — FixelSmith | Practitioner article | Candidate fraud rules should be replayed against historical outcomes, threshold volume should be measured, overlap with existing alerts matters, and analyst capacity is a real constraint | Influenced the plan to compare policies using error rates, review rate and decision cost rather than accuracy alone |
| Reducing false positives in credit card fraud detection — MIT News / Rob Matheson | Article | Blanket rules based on signals such as amount or location can incorrectly flag legitimate transactions because customer behavior varies | Supports using combinations of contextual evidence instead of treating one anomaly as sufficient |
| A Deep Dive of Transaction Risk Analysis for Open Banking and PSD2 — Dimuth Menikgama / WSO2 | Technical article | Transaction context can be used to decide whether stronger authentication is required, while real-time risk processing itself can affect authorization latency | Supports risk-based evidence acquisition and treating latency as part of decision cost |
| SAS / Nets fraud-prevention case study | Industry case study | Real-time fraud systems combine historical spending behavior, geolocation and device data; different risk levels can result in different automatic or human actions | Supports multi-signal evidence, proportional actions and selective human review |

These resources are used as research inputs rather than as proof that one
specific probability, threshold, latency, or fraud rate is universally valid.

---

## Research-Informed Problem Formulation

After reviewing existing Reddit and X discussions, several parts of the initial
formulation changed.

### Updated Initial Evidence

- Transaction amount deviation from customer history
- Device familiarity
- Geographic/location mismatch
- Recent transaction velocity

### Updated Additional Evidence

- Broader historical customer behavior
- Device or funding-source reuse
- Step-up authentication or customer confirmation

### Other Design Changes

- Location mismatch is now treated as contextual evidence rather than a
  standalone fraud signal.
- Recent velocity was moved from additional evidence to initial evidence.
- GET_MORE_EVIDENCE became a more important action before human escalation.
- Evidence acquisition now has explicit latency and customer-friction costs.
- Historical labels are treated cautiously because outcomes may be delayed or
  biased.
- Historical evidence is not assumed to remain equally comparable over time.

This is still a provisional design. It will be challenged through direct human
discussions before the first testable agent policy is finalized.

## 11. AI Prompts Used

AI was used to help organize the research process, generate search terms,
identify questions that required human input, and critique the developing agent
design.

### Prompt 1 — Research Planning

"Before creating research-file.md, what research, keywords, communities, and
people do I need to check inside Reddit and X for an uncertainty-aware
transaction agent?"

### Result

The AI suggested focusing the research on:

- transaction evidence;
- false positives;
- false negatives;
- human review;
- additional verification;
- decision costs;
- latency;
- delayed feedback.

It also suggested search terms and candidate Reddit/X communities and accounts.

### What I accepted

- Organizing research around questions that can change the agent design.
- Searching specifically for false positives, manual review, step-up
  authentication, transaction signals and decision costs.
- Separating passive research from my own human discussions.
- Recording whether each finding changes an assumption, test case, cost, or
  policy.

### What I rejected or changed

- Broad communities that were not directly relevant to transaction-level
  payment fraud.
- Treating all suggested accounts as verified before manually checking them.
- Using numerical values from individual Reddit/X posts as universal fraud
  probabilities.
- Building a complex ML or production-serving system before the Week 1
  probability design is complete.

---

### Prompt 2 — Interpreting Reddit Research

"What should I look for when searching fraud-related terms on Reddit, and how
should the findings affect the transaction agent?"

### Result

The AI suggested extracting:

- useful evidence;
- misleading signals;
- human-review conditions;
- additional evidence;
- cost and latency;
- feedback;
- new failure cases.

### What I accepted

The useful rule:

A research finding should ideally change at least one of:

- an assumption;
- an input signal;
- a probability update;
- an action;
- a cost;
- a test case;
- a failure condition.

### What I rejected or changed

I did not keep unrelated material about:

- healthcare-payment audits;
- general business-account restrictions;
- fake-document detection;
- merchant compliance;
- unrelated chargeback procedures.

These were different decision problems from the transaction-level agent.

---

### Prompt 3 — Reviewing X Findings

"I collected these X findings about false declines, fraud signals, thresholds,
step-up authentication, friction and delayed feedback. Which findings are
actually relevant to the agent and what should change?"

### Result

The AI helped group the useful X findings into:

- decline cause;
- contextual evidence;
- threshold policy;
- additional authentication;
- latency/friction;
- delayed feedback.

### What I accepted

- Keeping only findings that directly affect the agent policy.
- Treating step-up authentication as additional evidence rather than a final
  fraud verdict.
- Adding decision latency, customer friction and feedback latency to the
  project.
- Separating risk score generation from the policy that maps risk to an action.

### What I rejected or need to verify

- Numerical claims from vendor posts.
- Large industry-loss estimates that were not traced to their original source.
- Promotional claims about model accuracy or fraud reduction.
- The assumption that successful authentication guarantees that a transaction
  is legitimate.

---

## 12. Important AI Errors or Weak Suggestions

This section records cases where AI recommendations were incomplete,
unsupported, too broad, or changed after additional research.

| AI suggestion / omission | Problem with it | What I did instead |
|---|---|---|
| The first technical-term list did not include latency | GET_MORE_EVIDENCE and HUMAN_REVIEW both introduce delay, so latency is part of the actual decision problem | Added decision latency, evidence-acquisition cost, human-review latency, time-to-decision and feedback latency |
| Some initial Reddit community suggestions were too broad | Communities about healthcare claims, real-estate documents or unrelated fraud processes did not match the transaction-level decision problem | Narrowed the research toward payment processing, fintech, merchants, fraud analysis and transaction decisioning |
| Recent transaction velocity was initially placed mainly under additional evidence | Research repeatedly showed velocity as a common immediately useful transaction-risk signal | Moved recent transaction velocity into the initial evidence set |
| Merchant familiarity was initially proposed as a main additional signal | The research collected stronger support for historical behavior, device/funding-source reuse and step-up authentication | Replaced merchant familiarity as a primary additional-evidence candidate |
| Location change was initially treated as potentially strong evidence | Research showed legitimate travel, VPN use and other behavior can produce location anomalies | Treat location mismatch as contextual evidence that should be combined with other signals |
| Additional verification was initially treated mainly as beneficial information | Research showed authentication introduces latency and customer friction | Added evidence-acquisition cost, latency and friction to the policy |
| AI examples sometimes used illustrative probability, latency or threshold values | Example numbers could be mistaken for real-world standards | Numerical values will only be used as clearly labeled simulation assumptions unless supported by verified data |
| Successful authentication could appear to be strong proof of legitimacy | Authentication confirms something about identity/authorization but does not necessarily prove the underlying transaction is non-fraudulent | Treat authentication result as evidence that updates belief rather than final ground truth |

---

## 13. Assumptions

The current assumptions are provisional and may change after human discussions
and testing.

### State assumptions

- The hidden state is binary for the Week 1 prototype:
  - legitimate;
  - fraudulent.
- More detailed fraud categories such as account takeover, card testing or
  first-party fraud will be represented as scenarios or failure cases rather
  than separate hidden states.

### Evidence assumptions

- The initial evidence candidates are:
  - transaction amount deviation from customer history;
  - device familiarity;
  - geographic/location mismatch;
  - recent transaction velocity.
- Additional evidence may include:
  - broader historical customer behavior;
  - device or funding-source reuse;
  - step-up authentication or customer confirmation.
- No individual evidence signal is assumed to prove fraud by itself.
- Some evidence signals may be statistically dependent.
- Correlated signals must not be blindly treated as independent evidence.

### Probability assumptions

- P(Fraudulent) + P(Legitimate) = 1.
- The exact prior probability has not yet been finalized.
- Evidence likelihoods have not yet been finalized.
- If verified comparable data cannot be obtained, the Week 1 experiment will
  use clearly labeled synthetic assumptions.
- Risk scores should not automatically be assumed to be calibrated
  probabilities.

### Policy assumptions

- APPROVE, GET_MORE_EVIDENCE, HUMAN_REVIEW and STOP are distinct actions.
- Action thresholds are policy parameters, not universal mathematical
  constants.
- Human review is useful but has a non-zero cost.
- Additional evidence may sometimes be cheaper than immediate human review.
- Additional evidence is only valuable when its expected information gain
  justifies its cost, latency and customer friction.

### Feedback assumptions

- Authentication results and analyst decisions can provide relatively early
  evidence.
- Chargebacks or confirmed fraud may arrive later.
- An unlabeled transaction is not automatically legitimate.
- The Week 1 prototype will not automatically retrain itself from feedback.

### Scope assumptions

- The project models transaction fraud risk.
- It does not attempt to diagnose every reason that a payment can fail.
- A payment decline is therefore not equivalent to the hidden state
  "fraudulent."
- The Week 1 goal is decision-making under uncertainty rather than production
  fraud-model deployment.

No numerical probability, threshold, latency, fraud rate, or cost should
currently be interpreted as a verified real-world value unless explicitly
sourced.

---

## 14. Research Changes

The following changes were made after reviewing Reddit, X and other technical
material.

| Original idea | New evidence / feedback | Change made | Why |
|---|---|---|---|
| Location change could act as a strong fraud indicator | Research showed that legitimate travel, VPN use and other normal behavior can create geographic anomalies | Treat location mismatch as contextual evidence and combine it with other signals | A single geographic anomaly can create false positives |
| Recent transaction velocity was mainly considered additional evidence | Fraud discussions repeatedly identified velocity as an immediately useful risk signal | Move recent transaction velocity into the initial evidence set | It is often available at decision time and becomes especially useful when combined with other evidence |
| Merchant familiarity was a main additional-evidence candidate | Research produced stronger support for historical behavior, device/funding-source reuse and additional authentication | Replace merchant familiarity as a primary additional-evidence candidate | The newer evidence options are more directly connected to resolving transaction uncertainty |
| An uncertain transaction would mainly be sent to human review | Reddit and X research showed that additional verification can sometimes resolve uncertainty before escalation | Keep GET_MORE_EVIDENCE as a separate action before HUMAN_REVIEW | Human review has operational cost and latency |
| More evidence was assumed to be useful whenever uncertainty remained | X research showed that verification adds checkout friction and delay | Add value-of-information, evidence cost, latency and customer friction to the policy | Additional information is useful only when the expected benefit exceeds its cost |
| Fixed probability bands could directly determine actions | X research separated model/risk scoring from the business policy that maps the score to an action | Treat thresholds as experimental policy parameters and compare alternative policies | There is no universally correct approve/review/stop threshold |
| Payment decline could be interpreted mainly as fraud risk | X research showed that declined payments have multiple causes | Keep payment-failure causes outside the binary fraud hidden state | Not every failed or declined payment is fraudulent |
| Historical labels were initially treated as straightforward ground truth | Research showed that labels may be delayed and biased toward transactions selected by previous systems | Distinguish provisional feedback, delayed outcomes and unknown cases | Unlabeled does not mean legitimate |
| Historical behavior was initially assumed to remain directly comparable | Research showed that customer behavior, fraud patterns and systems can change | Add historical comparability and concept drift as research concerns | Old evidence may not represent the current transaction environment |
| Successful additional authentication could appear to strongly confirm legitimacy | Research showed that authentication should be interpreted as another observation rather than complete ground truth | Treat authentication as evidence that updates the belief | A successful authentication event does not prove every aspect of the transaction is legitimate |