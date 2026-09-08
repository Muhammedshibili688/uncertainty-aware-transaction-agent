# Discussion Record

I used this file to keep track of the conversations that influenced the Week 1
project. The contributors included practitioners, engineers, researchers and
other community members.

I did not treat a comment as fact just because someone posted it online. I used
each response to question an assumption, suggest a test or decide whether the
agent design should change.

---

## Completion audit

This audit separates evidence that is already recorded from activity that must
still happen on the real platforms. Research links and AI-written summaries do
not count as conversations unless I genuinely made the contribution and the
linked replies exist.

### Reddit evidence currently available

| Community | First recorded discussion | Second contribution in same community | Replies visible in supplied second-round evidence | Current status |
|---|---|---|---|---|
| r/AskStatistics | [Correlated fraud signals](https://www.reddit.com/r/AskStatistics/s/BZ1VEQxhVU) | [Imperfect verification reliability](https://www.reddit.com/r/AskStatistics/s/Coli7aNHfQ) | 1 reply supplied | Two contributions recorded; reply target not yet demonstrated |
| r/fintech | [Grey-area transaction checks](https://www.reddit.com/r/fintech/s/mfsh3ynZBH) | [Review reduction versus false approvals](https://www.reddit.com/r/fintech/s/GU1khvqkB0) | 2 replies supplied | Two contributions recorded; second discussion meets reply target |
| r/LLMDevs | [Stopping evidence collection](https://www.reddit.com/r/LLMDevs/s/shbBbf8LG5) | [How an agent should stop collecting evidence](https://www.reddit.com/r/LLMDevs/s/U1AyMMOuUH) | 5 replies supplied | Two contributions recorded; second discussion meets reply target |
| r/payments | [Location mismatch](https://www.reddit.com/r/payments/s/LA3TVkNyE5) | [Same-device authentication dependence](https://www.reddit.com/r/payments/s/B9uSDwPRd0) | 1 reply supplied | Two contributions recorded; reply target not yet demonstrated |
| r/AMLCompliance | [Historical behaviour](https://www.reddit.com/r/AMLCompliance/s/v13bVHIQza) | [Familiar behaviour as false reassurance](https://www.reddit.com/r/AMLCompliance/s/om78WpXjg1) | Reply evidence not supplied | Two contributions recorded; reply target not yet demonstrated |

Ten Reddit contribution links are now recorded across five communities. The
supplied screenshots demonstrate at least two discussions with two or more
replies: the second r/fintech discussion and the second r/LLMDevs discussion.
The target requires five such discussions, so three more qualifying reply
counts still need to be verified. A live link by itself is not treated as proof
of a reply count, and missing evidence must not be invented.

### X evidence currently available

The research file identifies eight relevant accounts:

`@ltvxdotai`, `@grimicorn`, `@WeAreIncognia`, `@CardNotPresent`,
`@JavelinStrategy`, `@ThePaypers`, `@ACI_Worldwide`, and `@NVIDIAAI`.

These are research leads, not proof that the accounts were followed or that a
discussion happened. Week 1 still requires 15–25 relevant accounts, 21–28
useful comments over seven days, and three discussions with two or more
replies.

Use the table below only for genuine activity:

| Date | Account | Post link | My first contribution | Human answer | My next answer | Design change |
|---|---|---|---|---|---|---|
| NOT RECORDED | NOT RECORDED | NOT RECORDED | NOT RECORDED | NOT RECORDED | NOT RECORDED | NOT RECORDED |

### Overall public-discussion status

`INCOMPLETE — awaiting verifiable Reddit contribution counts and genuine X activity.`

---

## Second Reddit contribution round

These entries contain my second contribution in each of the five communities.
The summaries use only the replies I saved, so they may not include every
comment currently visible on the live posts.

### r/LLMDevs — How should an agent decide when to stop collecting evidence?

**Link:** https://www.reddit.com/r/LLMDevs/s/U1AyMMOuUH

**Replies supplied:** 5

The strongest repeated suggestion was to ask whether the next check could
realistically change the action. If no possible result would change the plan,
the agent should stop collecting evidence. If a result could matter, its
expected value should be compared with latency, cost and a hard request budget.

**Project interpretation:** This supports the existing one-request cap while
showing why a future stopping rule should be based on decision relevance, not
confidence alone. It does not justify changing the already frozen Policy 2.

### r/payments — When should same-device authentication not reduce risk?

**Link:** https://www.reddit.com/r/payments/s/B9uSDwPRd0

**Replies supplied:** 1

The response described transaction and authentication on the same compromised
device as a single point of failure. It argued that the apparent second factor
does not provide meaningful separation when an attacker controls the original
environment, particularly for a high-value action.

**Project interpretation:** This directly supports Policy 2's decision not to
lower risk after a `SAME_CHANNEL` PASS.

### r/fintech — Is lower review worth more false approvals?

**Link:** https://www.reddit.com/r/fintech/s/GU1khvqkB0

**Replies supplied:** 2

One response suggested defining a maximum tolerable false-approval rate rather
than rejecting every workload trade-off immediately. Another separated the
question into the agent's assigned objective and its behaviour on edge cases.

**Project interpretation:** This supports the frozen multi-metric objective.
Review reduction is useful only inside an explicitly declared safety limit.
Because Policy 2 exceeded the baseline false-approval limit, the project keeps
the negative conclusion.

### r/AskStatistics — How should imperfect verification reliability be shown?

**Link:** https://www.reddit.com/r/AskStatistics/s/Coli7aNHfQ

**Replies supplied:** 1

The response suggested reporting a confidence interval for a proportion and
describing the improvement as a range rather than presenting one small-sample
percentage as exact performance.

**Project interpretation:** The current designed sample is too small and not
population-representative, so the project does not claim calibrated reliability.
The suggestion is retained for a future study with repeated or sampled data.

### r/AMLCompliance — Can familiar behaviour create false reassurance?

**Link:** https://www.reddit.com/r/AMLCompliance/s/om78WpXjg1

**Replies supplied:** Not recorded in the available project evidence

The question challenges the assumption that historical similarity establishes
authorization when an unauthorized person may have controlled the account for
some time.

**Project interpretation:** The question matches the failure observed in
familiar-context fraud cases, but no human response is claimed until reply
evidence is supplied.

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
