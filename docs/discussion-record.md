# Discussion Record

This file records direct discussions with practitioners, engineers,
researchers, and other community members during the Week 1 project.

The purpose is not to treat every comment as ground truth. Each response is
recorded as evidence that may challenge an assumption, suggest a test, change
the agent design, or result in no change.

---

## Reddit

### Discussion 1 — Correlated fraud signals

**Platform:** Reddit  
**Community:** r/AskStatistics  
**Question:** What’s the simplest way to avoid double-counting related fraud signals in a small Bayesian model?  
**Link:** https://www.reddit.com/r/AskStatistics/s/BZ1VEQxhVU

**Assumption before discussion:**  
New device, new IP, and location mismatch could potentially be used as
separate pieces of evidence in the probability update.

**Human response:**  
A commenter challenged the independence assumption and suggested modelling
the events as positively correlated. A follow-up discussion pointed toward
using a joint model rather than multiplying the signals independently.

**My follow-up:**  
I asked whether a small prototype could use joint probabilities, a shared
latent cause, or a simpler grouping rather than estimating a large covariance
structure.

**What I learned:**  
Treating related novelty signals as independent could double-count the same
underlying behavioural change and make the posterior overconfident.

**Design / test impact:**  
PROVISIONAL CHANGE.

For v0, new-device, new-IP, and location-mismatch will not automatically count
as three independent confirmations of fraud.

Add a legitimate-traveller test case where all three signals occur together
to check whether the model becomes falsely confident.

**Open question:**  
Whether a joint probability model or explicit latent variable is justified
with the amount of data available.

---

### Discussion 2 — What to check in a grey-area transaction

**Platform:** Reddit  
**Community:** r/fintech  
**Question:** When a payment looks suspicious but not suspicious enough to block, what do you usually check next?  
**Link:** https://www.reddit.com/r/fintech/s/mfsh3ynZBH
**Assumption before discussion:**  
An uncertain transaction should receive one additional useful check before
manual review.

**Human responses:**  
Responses suggested that isolated weak signals such as a new device or unusual
amount may not justify deeper enrichment. Step-up checks such as 3DS,
customer confirmation, or AVS/CVV verification were described as more useful
because their result may actually change the decision.

**Design / test impact:**  
CHANGE.

The Week 1 GET_MORE_EVIDENCE action will be represented by a lightweight
step-up verification rather than arbitrary deeper enrichment.

Possible outcomes:
- pass
- fail
- inconclusive

---

### Discussion 3 — Stopping evidence collection

**Platform:** Reddit  
**Community:** r/LLMDevs  
**Question:** If an agent can keep asking for more evidence, what stops it from checking forever?  
**Link:** https://www.reddit.com/r/LLMDevs/s/shbBbf8LG5

**Assumption before discussion:**  
Allow one additional evidence request, then force an action or human review.

**Human responses:**  
Several replies independently argued that another check should only be run
when its result could plausibly change the decision and when its expected
benefit justifies cost, delay, or friction. Hard limits were also suggested.

**Design / test impact:**  
NO IMMEDIATE v0 CHANGE.

Week 1 v0 will retain a one-additional-check safety cap because it is simple
and testable.

The responses expose this as a limitation rather than a principled stopping
rule. Value-of-information-based stopping becomes a candidate for the next
version / Week 2.

---

### Discussion 4 — Location mismatch

**Platform:** Reddit  
**Community:** r/payments  
**Question:** How much weight do you actually give a location mismatch in a fraud decision?  
**Link:** https://www.reddit.com/r/payments/s/LA3TVkNyE5

**Assumption before discussion:**  
Location mismatch is useful fraud evidence.

**Human response:**  
A practitioner argued that location by itself creates substantial noise due
to VPNs, roaming, and legitimate travel, and described combinations involving
device novelty plus AVS/CVV failure and unusual amount as more meaningful.

**Design / test impact:**  
CHANGE.

Location mismatch will be treated as contextual evidence rather than a strong
standalone indicator.

Add:
- legitimate travel case
- VPN/location mismatch case
- location + new device case
- location + verification failure + unusual amount case

---

### Discussion 5 — Historical behaviour

**Platform:** Reddit  
**Community:** r/AMLCompliance  
**Question:** When does a customer’s old transaction history stop being useful for fraud decisions?  
**Link:** https://www.reddit.com/r/AMLCompliance/s/v13bVHIQza

**Assumption before discussion:**  
Behaviour similar to a customer's historical activity provides evidence for
legitimacy.

**Human response:**  
A commenter pointed out that persistent scam or fraudulent behaviour can
itself become historically normal. A human investigator may recognise that
the pattern is harmful even though it is familiar.

**Design / test impact:**  
CHANGE.

Historical similarity will mean behavioural continuity, not automatic safety.

Add a test case in which a customer's current transaction resembles months of
previous suspicious activity.