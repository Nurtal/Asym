# Literature review: positioning Asym for JASSS

Scope: mechanistic and empirical work on layered ego networks (Dunbar circles), tie
decay and turnover, dynamical and agent-based models of tie formation, reciprocity
asymmetry, and JASSS methodological expectations. Compiled 2026-10-31.

**Verification method.** Every DOI below was resolved against the Crossref API (title,
authors, venue, volume and pages matched). Abstracts were read from Europe PMC, OpenAlex,
Semantic Scholar, arXiv, journal pages (APS, JASSS) or the author's preprint (Burt 2002).
Where we could not read the abstract or full text, the entry says so and the summary is
marked *(content not verified against the source)*. JASSS articles before about 2010 have
no registered DOI; their jasss.org URLs were fetched and the titles checked. Nothing
below is cited from a blog or press summary.

Asym claims referred to throughout:

- **C1.** Dunbar-like cumulative layers (about 2/6/16/43, ratios about 3 after
  calibration) emerge from a finite time budget alone, with no imposed capacity.
- **C2.** The inner circle is budget-bound (independent of N). The outer layer is
  exposure-bound (encounter rate × lifetime of unmaintained ties).
- **C3.** Layer sizes are independent of N only if new-tie formation does not grow with N.
- **C4.** The closeness distribution is bimodal. The inner-circle state sustains itself
  through circle-dependent decay, so thresholds cannot be set arbitrarily.
- **C5.** Embedded dyads are bistable (breakup or friendship depending on initial
  closeness). Isolated dyads always become friendships. High β gives all-or-nothing ties.
- **C6.** Persistent asymmetry arises from heterogeneous reciprocity expectations.

---

## Summary

**What is established.** Layered ego networks are an empirical regularity across
questionnaires, Christmas cards, phone calls, Facebook and Twitter. The layers are about
1.5, 5, 15, 50 and 150, with a scaling ratio of about 3 (Hill & Dunbar 2003; Zhou et al.
2005; Dunbar et al. 2015; Mac Carron et al. 2016). Three facts are also well documented:
time spent on communication is bounded and unevenly spread (Miritello et al. 2013a,b;
Saramäki et al. 2014); friendships decay without contact, while kin decay less (Roberts &
Dunbar 2011a,b, 2015); and friendship nominations are often unreciprocated and poorly
perceived (Almaatouq et al. 2016; Ball & Newman 2013). The idea that *a finite budget plus
heterogeneous relationship costs produces layers* is not new. It is the central result of
**Tamarit, Cuesta, Dunbar & Sánchez (2018, PNAS)**, a static maximum-entropy model, and it
was argued verbally by Sutcliffe et al. (2012, BJP). **Sutcliffe, Wang & Dunbar (2012,
JASSS)** already published an agent-based model in JASSS that reproduces strong, medium
and weak layers (about 5/15/150) from trust dynamics with slower decay for strong ties.

**Biggest overlap risks.**

1. *Tamarit et al. 2018 / 2022.* Asym's C1 restates their core message ("finite capacity
   + heterogeneous cost ⇒ layers with ratio ≈ 3"). Their model also predicts a dependence
   on the number of available alters: an **inverse regime** in small communities, with
   more alters in the inner layers than in the outer ones. That prediction speaks directly
   to Asym's C2/C3. A reviewer from that group will ask whether Asym reproduces the inverse
   regime at small N, and why a dynamical model is needed at all.
2. *Sutcliffe, Wang & Dunbar 2012 (JASSS) and Sutcliffe & Wang 2012 (JASSS).* These are
   ABMs in the target journal. They have interaction-driven tie strength, decay that is
   slower for strong ties (as in C4), kin and close friends competing for the same slots,
   and parameters tuned to the SBH targets. They also report that results at N = 500
   needed retuning (an N-dependence related to C3). Asym must cite them and set itself
   apart explicitly.
3. *Jin, Girvan & Newman 2001; Davidsen et al. 2002; Kumpula et al. 2007.* These are
   classic dynamical network models with triadic-closure encounters, random encounters,
   decay of unmaintained ties and reinforcement. Asym's tie-formation layer is
   essentially this family.

**Where Asym looks novel** (no prior work found doing this):

- A *dynamical* (PDMP + mean-field ODE) account of layer formation in which the circles
  are hybrid states that feed back on decay. This gives a *mechanistic* separation of
  budget-bound inner layers from exposure-bound outer layers (C2), with an explicit
  condition for N-independence (C3).
- A predicted **bimodal** closeness distribution, with thresholds constrained by the
  dynamics (C4). This contrasts with the monotone (Boltzmann-type) allocation of Tamarit
  et al. 2022 and the unimodal gamma/Gaussian strengths of Iñiguez et al. 2023. Empirical
  support for bimodality is **weak or absent** (see §2). This is both a novelty and a risk.
- **Bistability of embedded dyads** (C5). Dyadic ODE models with multiple equilibria
  exist (Gottman et al. 2002; Felmlee & Greenberg 1999), but we found no model where
  bistability comes from *competition for a time budget inside a network*. Empirically,
  it fits the finding that a tie's lifetime is predictable from its first weeks (Hidd et
  al. 2023) and the "liability of newness" of ties (Burt 2000, 2002).
- **Asymmetry from heterogeneous reciprocity expectations** (C6), as opposed to status
  (Ball & Newman 2013) or perception error (Almaatouq et al. 2016). We found no ABM
  making this argument. Note that in its bare form ("an agent expecting more than balance
  always feels a deficit") it is true by construction. The publishable content is its
  network-level consequences.

**Honest caveat on C1.** In Asym the ratios of about 3 were obtained by *calibrating*
the circle thresholds and parameters toward a target ratio of 3 (experiments 02 and 06).
So, like Sutcliffe et al. 2012, Asym shows the pattern is *reachable*, not that it is
*predicted*. Tamarit et al. derive the ratio from a linear cost assumption with one
parameter. Asym's absolute sizes (about 2/6/16/43) match the **1.5/5/15/50** layers
(Dunbar et al. 2015 report an innermost layer of about 1.5), not 5/15/50/150.

**Recommended framing for JASSS.** Present Asym as a *process model that complements*
the static resource-allocation theory of Tamarit et al. Do not present it as the first
explanation of layering. The contributions to lead with:

1. **Which layer sizes are budget-bound and which are exposure-bound**, and the condition
   (non-scaling tie formation) under which layers are independent of N. Test against
   Tamarit's inverse regime at small N.
2. **Bimodality and self-sustaining inner circles** as testable predictions. Put a
   falsification test on longitudinal closeness or communication data in the paper.
3. **Bistable, history-dependent dyads under budget competition** (C5).
4. **Asymmetry from heterogeneous expectations** as a mechanism distinct from status
   and misperception.

Use the ODD protocol (Grimm et al. 2020), a global sensitivity analysis, pattern-oriented
validation against several stylised facts at once, and docking of the ODE with the ABM.
Deposit the code on CoMSES.

---

## (1) Mechanistic models of Dunbar-like layering

### Tamarit, Cuesta, Dunbar & Sánchez (2018)
*Cognitive resource allocation determines the organization of personal networks.* PNAS
115(33):8316–8321. DOI [10.1073/pnas.1719233115](https://doi.org/10.1073/pnas.1719233115) (verified; full text read via Europe PMC, PMC6099867).

**Mechanism.** The model allocates L links into r layers with costs s₁ > … > s_r, using
a multinomial prior constrained by a fixed mean number of links L and fixed mean total
resources S. The maximum-entropy posterior has one parameter μ, the Lagrange multiplier
of the resource constraint. The ratio between successive layers is e^{μ|Δs|}, so with
linear costs the inclusive circles scale geometrically with ratio e^μ. The fitted ratio
for 84 students was 2.66 (3.13 when individual ratios are averaged). **Prediction.** μ
is set by S/L. For large L (many available alters) the standard regime holds (μ > 0).
For small L (small communities) the structure **inverts** (μ < 0): the inner layers are
the most populated. They confirm this in four immigrant communities, where 75% of
networks have μ < 0, and 96% in a community of about 80 Bulgarians. The model is
**static**: there are no dynamics, no decay, no tie formation, and layers are
categories of a survey scale. It does not address bimodality.

**Relation to Asym.**

- *C1: overlaps strongly.* Budget + heterogeneous cost ⇒ layers is their headline result.
  Asym's difference is that costs and layers come out of dynamics (circle-dependent decay
  and allocation ∝ x^β) instead of being postulated.
- *C2/C3: partly overlaps, potentially contradicts.* Tamarit predict that layer
  *proportions* depend on the number of available alters (L, linked to community size).
  Asym claims N-independence above N ≈ 200. These are compatible only if, in Asym, L
  saturates with N, which is exactly what C3 says. Asym should show the small-N limit:
  at N = 100 the butterflies "run out of people", and the loyal_few profile
  4.7/5.9/6.8/22 is close to inverse. If Asym reproduces an inverse regime at small N,
  that is a strong *docking* result.
- *C4: not addressed.* Their continuum version (2022) gives a monotone distribution,
  which is in tension with bimodality (see below).
- *C5, C6: not addressed.* Note that the "isolated dyad always becomes a friendship"
  result is the dyadic analogue of their inverse regime (few alters ⇒ intense ties).

### Tamarit, Sánchez & Cuesta (2022)
*Beyond Dunbar circles: a continuous description of social relationships and resource
allocation.* Scientific Reports 12:2287. DOI [10.1038/s41598-022-06066-1](https://doi.org/10.1038/s41598-022-06066-1) (verified; full text read, PMC8831677).

This paper takes the r → ∞ limit of the 2018 model, so resources per tie are
continuous. It recovers a parameter η, the analogue of the circle ratio, and predicts and
estimates η ≈ 6 on phone-call, face-to-face and Facebook data. It again finds individuals
in the inverse regime (η < 0), where the closest relationships are over-populated. The
implied distribution of allocated resource over alters is exponential-family (truncated
Boltzmann), so **monotone, not bimodal**.

- *C1: overlaps* (layers without discrete categories).
- *C4: contradicts or competes.* The maximum-entropy null predicts a monotone
  distribution. Asym's bimodality is a sharper alternative that can be tested on the same
  continuous datasets they used.
- *C2/C3: as for the 2018 paper.*

Note: we found no separate "2022 Tamarit et al. paper on inverse layering in small
communities". The inverse regime is in the 2018 PNAS paper and is re-examined in this
2022 paper. The closest dynamic follow-up from the same group is Escribano et al. 2021
(§2).

### Sutcliffe, Dunbar, Binder & Arrow (2012)
*Relationships and the social brain: integrating psychological and evolutionary
perspectives.* British Journal of Psychology 103(2):149–168. DOI [10.1111/j.2044-8295.2011.02061.x](https://doi.org/10.1111/j.2044-8295.2011.02061.x) (verified; abstract read).

This is a verbal theory. Each layer (5-15-50-150) has asymptotic benefits but costs
(mainly time) that are roughly linear in the number of relationships. The cost-benefit
trade-off across layers produces the hierarchy. Trust, which is itself a function of time
invested, is proposed as the psychological mediator.

- *C1: supports, conceptual precursor.* Time investment is the cost and trust is built
  by time. Asym implements this informally stated mechanism.
- *C4: supports* (the investment-closeness feedback).
- *C2, C3, C5, C6: not addressed.*

### Dunbar (2018)
*The anatomy of friendship.* Trends in Cognitive Sciences 22(1):32–51. DOI [10.1016/j.tics.2017.10.004](https://doi.org/10.1016/j.tics.2017.10.004) (verified; abstract read).

A review: friendship is very costly in time and cognition, yet personal networks show
constancies in size and hierarchical structure. It argues for multidisciplinary
mechanisms (time budgets, cognitive constraints, homophily). *(Specific numerical claims
in the body were not re-checked here.)*

- *C1: supports* (time cost as a central constraint).
- Useful as the canonical review to cite for the stylised facts Asym targets.

### Zhou, Sornette, Hill & Dunbar (2005)
*Discrete hierarchical organization of social group sizes.* Proc. R. Soc. B
272:439–444. DOI [10.1098/rspb.2004.2970](https://doi.org/10.1098/rspb.2004.2970) (verified; abstract read).

A fractal analysis of many human grouping datasets identifies a discrete hierarchy of
preferred group sizes with a scaling ratio close to 3 (3–5, 9–15, 30–45, …). It is
empirical and statistical, with no mechanism. It speculates on hierarchical processing
of social nearness.

- *C1: supports the target pattern.* Note that it concerns group sizes, not only ego
  layers.
- *C4:* "discrete scale invariance" points to discreteness in closeness, which is weakly
  consistent with a multimodal closeness distribution but does not test it.

### Hill & Dunbar (2003)
*Social network size in humans.* Human Nature 14(1):53–72. DOI [10.1007/s12110-003-1016-y](https://doi.org/10.1007/s12110-003-1016-y) (verified; abstract read).

Christmas-card networks: the maximum network averaged 153.5 and the contacted network
124.9. Contact frequency is driven by passive factors (distance, work) and active ones
(emotional closeness, relatedness). Controlling for passive factors lets the
hierarchical layers be delimited.

- *C1: supports the target* (≈150 total and layering). Asym's outer layer (≈43) falls
  short in absolute size.
- *C2: supports in part.* Passive factors (distance, a form of exposure) shape contact,
  which is consistent with an exposure-bound outer layer.

### Dunbar, Arnaboldi, Conti & Passarella (2015)
*The structure of online social networks mirrors those in the offline world.* Social
Networks 43:39–47. DOI [10.1016/j.socnet.2015.04.005](https://doi.org/10.1016/j.socnet.2015.04.005) (verified; abstract read).

Two Facebook datasets and one Twitter dataset (> 185,000 egos) were analysed using
bidirectional post frequencies. Facebook is best fit by four layers and Twitter by five.
Layer sizes and contact frequencies match offline networks, and all datasets show an
**innermost layer of about 1.5 alters**.

- *C1: supports.* Asym's innermost circle (≈2) matches the 1.5 layer. Asym's four
  circles map onto 1.5/5/15/50, which is the framing we recommend.
- *C3: supports.* Online media, which raise exposure, do not enlarge the inner layers.
  That is consistent with budget-bound inner layers.

### Sutcliffe, Wang & Dunbar (2012), JASSS (the key ABM precedent)
*Social relationships and the emergence of social networks.* JASSS 15(4):3. DOI [10.18564/jasss.2059](https://doi.org/10.18564/jasss.2059) (verified; full text read on jasss.org).

In this ABM, each turn an agent either forages or socialises (forage:social ratio FM).
Partner choice is a probabilistic search favouring past successful interactions, under
four strategies (favour-the-few, medium, favour-the-many, staged). Interactions
cooperate or defect, and trust rises (log-compressed at high trust) or falls. Trust
**wanes at a rate that is smaller for strong ties**. Strong, medium and weak ties are
the *terciles* of the trust distribution. An evolutionary layer selects strategies under
wellbeing or resource fitness. Best fits gave about 6–7 strong ties, 16–17 medium ties
and about 150 total. Results needed socially-biased time budgets. At N = 500 the
**parameters had to be changed** (higher waning) because trust built more slowly when
interactions were spread over more agents. Kin seeded as strong ties *substituted* for
emergent strong ties.

- *C1: overlaps directly.* This is an ABM in JASSS, with time allocation, interaction-
  driven strength and layered output, and with parameters tuned to SBH targets (as Asym
  calibrates). Differences: Asym has no imposed capacity or terciles (circles are
  thresholds on closeness with hysteresis); it has invitation, acceptance and patience,
  directed ties with reciprocity memory, and an ODE limit.
- *C2/C3: related evidence.* Their N-dependence (retuning at N = 500) is exactly the
  issue Asym's C3 resolves. Asym can explain *why* their results depended on N:
  interactions spread over more agents.
- *C4: overlaps on mechanism.* Strength-dependent decay is assumed there too.
  Bimodality is not reported.
- *C5, C6: not addressed.* Defection is a global rate, not a partner-specific
  expectation.

### Sutcliffe & Wang (2012), JASSS
*Computational modelling of trust and social relationships.* JASSS 15(1):3. DOI [10.18564/jasss.1912](https://doi.org/10.18564/jasss.1912) (verified; full text read).

This is the precursor model. Only the "log increase / linear decrease" trust variant
produced SBH-like distributions (about 5–6 strong, 14–16 medium, about 130 weak). Kin
fill strong-tie slots. Moderate defection (≤ 5%) is tolerated, while > 10% erodes
strong ties.

- *C1, C4: overlap* (functional forms of growth and decay determine whether layering
  appears, a finding akin to Asym's "thresholds and decay ladder dominate").
- *C6: partly related.* Defection erodes trust, but there is no heterogeneity in
  expectations.

### Sutcliffe, Dunbar & Wang (2016)
*Modelling the evolution of social structure.* PLOS ONE 11(7):e0158605. DOI [10.1371/journal.pone.0158605](https://doi.org/10.1371/journal.pone.0158605) (verified; abstract read).

This extends the 2012 model to evolutionary trade-offs between foraging and social time.
Multi-level structure (few strong, more medium, many weak) emerges only in a small region
of the fitness landscape: high social time, preferential interaction, and wellbeing and
alliance benefits.

- *C1: qualifies it.* Layering is not generic in their model. Asym should report how much
  of its parameter space gives layering (a sensitivity-analysis question).

### Gonçalves, Perra & Vespignani (2011)
*Modeling users' activity on Twitter networks: validation of Dunbar's number.* PLOS ONE
6(8):e22656. DOI [10.1371/journal.pone.0022656](https://doi.org/10.1371/journal.pone.0022656) (verified; abstract and model section read).

In 1.7 M Twitter users, average tie weight saturates at about 100–200 stable
relationships. The model has agents with a finite message queue (q_max per step) who
reply preferentially, by sender degree, to a random number of messages. Finite
priority queuing plus time resources reproduce the saturation.

- *C1: supports* (finite time and attention ⇒ a bound on stable ties, without an
  explicit cap on the number of ties). No layers.
- *C2: supports* (time-budget-bound strong ties).

---

## (2) Empirical evidence from communication data

### Saramäki, Leicht, López, Roberts, Reed-Tsochas & Dunbar (2014)
*Persistence of social signatures in human communication.* PNAS 111(3):942–947. DOI [10.1073/pnas.1308540110](https://doi.org/10.1073/pnas.1308540110) (verified; abstract read).

This combines 18 months of phone records and surveys of students moving from school to
university or work. Each ego has a distinctive "social signature" (the distribution of
calls over ranked alters) that persists **despite considerable turnover** of alters.
New alters replace old ones or push them down, preserving the shape. This is attributed
to finite time and emotional resources.

- *C2: supports strongly.* The shape is conserved under turnover, which is what a budget-
  bound allocation predicts. A natural validation target for Asym is to compute the
  signature (closeness or investment vs rank) and its persistence under turnover.
- *C4: partly contradicts.* There is substantial turnover even among top alters over
  18 months, during a life transition. Asym's "self-sustaining" inner circle must still
  show realistic turnover.

### Heydari, Roberts, Dunbar & Saramäki (2018)
*Multichannel social signatures and persistent features of ego networks.* Applied
Network Science 3:8. DOI [10.1007/s41109-018-0065-4](https://doi.org/10.1007/s41109-018-0065-4) (verified; abstract read).

Signatures from calls, texts and mixed channels persist and resemble each other,
despite alter turnover.

- *C2: supports* (budget-shaped allocation is channel-independent).

### Centellegher, López, Saramäki & Lepri (2017)
*Personality traits and ego-network dynamics.* PLOS ONE 12(3):e0173110. DOI [10.1371/journal.pone.0173110](https://doi.org/10.1371/journal.pone.0173110) (verified; abstract read).

Personality affects signature persistence, turnover and rank dynamics. For example,
Openness relates to higher turnover.

- *Archetypes: supports* the use of heterogeneous behavioural profiles. It is an
  empirical anchor for "butterfly" and "loyal_few" turnover differences.

### Miritello, Moro, Lara, Martínez-López, Belchamber, Roberts & Dunbar (2013a)
*Time as a limited resource: communication strategy in mobile phone networks.* Social
Networks 35(1):89–95. DOI [10.1016/j.socnet.2013.01.003](https://doi.org/10.1016/j.socnet.2013.01.003) (verified; abstract read).

Nine billion calls from 20 M users: people with large networks do not spend
proportionally more time communicating, so their ties are weaker. Time is very unevenly
distributed, with most calls going to a few alters.

- *C1/C2: supports directly.* Total time is roughly fixed, so more ties means weaker
  ties. This is the empirical signature of a time budget without a capacity cap.

### Miritello, Lara, Cebrian & Moro (2013b)
*Limited communication capacity unveils strategies for human interaction.* Scientific
Reports 3:1950. DOI [10.1038/srep01950](https://doi.org/10.1038/srep01950) (verified; abstract read).

Using a method to detect tie de-activation (about 19 months, about 20 M people), they
find individuals have a **finite communication capacity**: the number of active ties is
bounded over time. Separating capacity from activity reveals strategies from "stable" to
"exploratory".

- *C2: supports.* The bound on active ties comes with ongoing tie turnover.
- *C3: supports.* The exploratory strategy corresponds to Asym's ε exploration (and the
  butterfly archetype). Capacity is individual-specific, not population-size-specific.

### Mac Carron, Kaski & Dunbar (2016)
*Calling Dunbar's numbers.* Social Networks 47:151–155. DOI [10.1016/j.socnet.2016.06.003](https://doi.org/10.1016/j.socnet.2016.06.003) (verified; abstract read).

Clustering of call frequencies recovers layers. The innermost and outermost layers match
SBH values, but the intermediate layers vary widely.

- *C1: supports, with a caveat* that intermediate layers are not robust in data. Asym's
  difficulty in raising the close-friend/friend ratio is less damning than it seems.
- *C4: weakly related.* Clustering finds clusters in call frequency, but this is not a
  test of bimodality.

### Roy, Bhattacharya, Dunbar & Kaski (2022)
*Turnover in close friendships.* Scientific Reports 12:11018. DOI [10.1038/s41598-022-15070-4](https://doi.org/10.1038/s41598-022-15070-4) (verified; abstract read).

National phone data: membership of the inner circle is **extremely stable** over three
years, with about 1–4% of alters changing per year. Turnover is higher at ages 17–21.
There are gender differences in terminating ties.

- *C4: supports* the self-sustaining inner circle and gives a quantitative target
  (1–4% per year). Asym should report inner-circle churn per unit time, which requires a
  time-unit mapping (see Gaps).

### Hidd, López, Centellegher, Roberts, Lepri & Dunbar (2023)
*The stability of transient relationships.* Scientific Reports 13:6120. DOI [10.1038/s41598-023-32206-2](https://doi.org/10.1038/s41598-023-32206-2) (verified; abstract read).

Phone data from the US, UK and Italy: communication with transient alters does **not
decay gradually**. It shows no dominant trend until it stops. A tie's lifetime is
predictable from call volume in the first weeks.

- *C5: supports* the bistable or all-or-nothing picture: a tie's fate is decided early,
  with no slow erosion.
- *C4: partly contradicts* Asym's continuous decay of closeness for outer ties, at least
  at the level of communication volume. Asym can reconcile this if invitations (the
  observable) stay steady while latent closeness drifts. Worth a figure.

### Escribano, Doldán-Martelli, Lapuente, Cuesta & Sánchez (2021)
*Evolution of social relationships between first-year students at middle school: from
cliques to circles.* Scientific Reports 11:11694. DOI [10.1038/s41598-021-90984-z](https://doi.org/10.1038/s41598-021-90984-z) (verified; abstract read).

Two survey waves: at first, students have few relationships, mostly intense (close to
the inverse regime). Later they have more relationships, with a smaller proportion of
intense ones. Communities stabilise around about 15. More stable groups go the other way,
toward their best relationships.

- *C1/C2: supports the dynamic view.* Layer proportions change as the number of
  available or known alters grows, which matches Asym's transient from an empty start.
  It is the empirical bridge between Tamarit's static regimes and Asym's dynamics.

### Roberts & Dunbar (2011a)
*Communication in social networks: effects of kinship, network size, and emotional
closeness.* Personal Relationships 18(3):439–452. DOI [10.1111/j.1475-6811.2010.01310.x](https://doi.org/10.1111/j.1475-6811.2010.01310.x) (verified; abstract read).

251 women: people with larger kin networks have longer times since last contact with
both kin and friends, and emotional closeness shortens the time since last contact. The
effect of closeness is stronger for kin.

- *C1/C2: supports.* Larger networks mean less contact per alter (a budget).
- *C4: supports.* Contact frequency is tied to closeness. Kin are cheaper to maintain,
  a heterogeneity that Asym lacks (no kin class).

### Roberts & Dunbar (2011b)
*The costs of family and friends: an 18-month longitudinal study of relationship
maintenance and decay.* Evolution and Human Behavior 32(3):186–197. DOI [10.1016/j.evolhumbehav.2010.08.005](https://doi.org/10.1016/j.evolhumbehav.2010.08.005) (verified). The abstract was not available through the APIs. The finding below is taken from the Oxford Department of Experimental Psychology record.

The emotional closeness of friendships was more sensitive than kin ties to declines in
contact frequency and shared activities.

- *C4: supports* decay that depends on maintenance. Note that the empirical decay depends
  on relationship *type* (kin vs friend), while Asym's depends on circle.

### Roberts & Dunbar (2015)
*Managing relationship decay: network, gender, and contextual effects.* Human Nature
26(4):426–450. DOI [10.1007/s12110-015-9242-7](https://doi.org/10.1007/s12110-015-9242-7) (verified; abstract read).

Whole active networks were followed for 18 months across a life transition. Family and
friends differ strikingly. Decline in friendship quality is mitigated by more effort, by
talking for women and by joint activities for men.

- *C4: supports.* Investment counteracts decay, which is Asym's core feedback.

### Wellman, Wong, Tindall & Nazer (1997)
*A decade of network change: turnover, persistence and stability in personal
communities.* Social Networks 19(1):27–50. DOI [10.1016/S0378-8733(96)00289-4](https://doi.org/10.1016/S0378-8733(96)00289-4) (verified; abstract read).

33 Torontonians interviewed ten years apart: **only 27% of intimate ties persisted**.
Durable ties are supportive, in frequent phone contact, or kin. Marriage caused almost
complete turnover.

- *C4: tension.* Over a decade, the inner circle is far from permanent. Asym's
  "self-sustaining" state must be quantified as a *mean residence time*, not as
  permanence. Life events (exogenous shocks) are absent from Asym.

### Wellman & Wortley (1990)
*Different strokes from different folks: community ties and social support.* American
Journal of Sociology 96(3):558–588. DOI [10.1086/229572](https://doi.org/10.1086/229572) (verified). *(The abstract was not retrieved, so the summary is not verified against the source.)*

This classic East York study shows that different ties provide different types of
support, with strong ties providing more.

- Background for the functional meaning of circles. It does not test C1–C6.

### Mok & Wellman (2007)
*Did distance matter before the Internet? Interpersonal contact and support in the
1970s.* Social Networks 29(3):430–461. DOI [10.1016/j.socnet.2007.01.009](https://doi.org/10.1016/j.socnet.2007.01.009) (verified). *(The abstract was not retrieved. Our summary is that face-to-face contact falls sharply with distance while phone contact is less affected; this is not verified against the source.)*

- *C2: weak support.* Exposure (distance or meeting opportunity) shapes contact. Asym has
  no space, which is a limitation reviewers may raise.

### Arnaboldi, Conti, Passarella & Pezzoni (2013); Arnaboldi, Guazzini & Passarella (2013)
- *Ego networks in Twitter: an experimental analysis.* IEEE INFOCOM 2013 Workshops /
  Proceedings, pp. 3459–3464. DOI [10.1109/INFCOM.2013.6567181](https://doi.org/10.1109/INFCOM.2013.6567181) (verified; abstract read). Dunbar-like circles appear in Twitter ego networks.
- *Egocentric online social networks: analysis of key features and prediction of tie
  strength in Facebook.* Computer Communications 36(10–11):1130–1144. DOI [10.1016/j.comcom.2013.03.003](https://doi.org/10.1016/j.comcom.2013.03.003) (verified; abstract read). The number of actively maintained Facebook relationships is close to 150. Recency of contact is the strongest single predictor of tie strength.

- *C1: supports the target.*
- *C4: recency as the strength predictor* is consistent with decaying closeness.

### Hidalgo & Rodríguez-Sickert (2008)
*The dynamics of a mobile phone network.* Physica A 387(12):3017–3024. DOI [10.1016/j.physa.2008.01.073](https://doi.org/10.1016/j.physa.2008.01.073) (verified; abstract read).

Persistent links tend to be reciprocal and occur among low-degree, high-clustering
users. **Reciprocity is the strongest predictor of tie persistence.**

- *C6 / g(reciprocity): supports* making reciprocity drive tie survival.
- *C5: supports.* Clustered (embedded) settings and persistence are linked. Note that
  "embedded" there means sharing neighbours, while Asym's "embedded dyad" means
  competing for budget. The paper must disambiguate these.

### Raeder, Lizardo, Hachen & Chawla (2011)
*Predictors of short-term decay of cell phone contacts in a large scale communication
network.* Social Networks 33(4):245–257. DOI [10.1016/j.socnet.2011.07.002](https://doi.org/10.1016/j.socnet.2011.07.002) (verified; arXiv abstract 1102.1753 read).

Directed edge weight, **weighted reciprocity** and tie age are the strongest predictors
of whether a tie persists over 8 weeks.

- *C4, C6: supports.* Strength, reciprocity and age protect ties.

### Navarro, Miritello, Canales, Moro & Lara (2017)
*Temporal patterns behind the strength of persistent ties.* EPJ Data Science 6:31. DOI [10.1140/epjds/s13688-017-0127-3](https://doi.org/10.1140/epjds/s13688-017-0127-3) (verified; abstract read).

Temporal rhythm predicts persistence better than intensity. A tie silent for more than
about 8× its usual inter-event time is likely to decay.

- *Patience / cancellation and decay: supports* a time-scale-relative decay rule. It
  offers a concrete stylised fact for calibrating decay rates per circle.

### Burt (2000); Burt (2002)
- *Decay functions.* Social Networks 22(1):1–28. DOI [10.1016/S0378-8733(99)00015-5](https://doi.org/10.1016/S0378-8733(99)00015-5) (verified). Abstract as indexed by ScienceDirect: the factors associated with strong relationships (inertia/prior strength, homophily, status, **embedding** through third parties) are associated with **slower decay**. Decay follows a "liability of newness" pattern.
- *Bridge decay.* Social Networks 24(4):333–363. DOI [10.1016/S0378-8733(02)00017-5](https://doi.org/10.1016/S0378-8733(02)00017-5) (verified; author's preprint read). Nine in ten bridge relations are gone the next year, and surviving relations are less subject to decay. Bridges decay faster than non-bridges early, then more slowly after year four.

- *C4: supports.* Stronger and older ties decay more slowly, which is the empirical
  basis for circle-dependent decay.
- *C5: supports.* The high early hazard and survival of those past it is the
  signature of a bistable or threshold process.
- *Terminology risk:* Burt's "embedded" ties (shared third parties) decay *slower*.
  Asym's "embedded dyads" (budget competition) are *less* likely to survive than
  isolated ones. The opposite connotation will confuse sociologists. Consider renaming
  (e.g. "competing dyad" or "budget-embedded dyad").

### Evidence on bimodal tie-strength distributions (C4)
We searched specifically and **found no primary source establishing a bimodal
distribution of emotional closeness or tie strength in ego networks.** What we found:

- Mattie, Engø-Monsen, Ling & Onnela (2018), *Understanding tie strength in social
  networks using a local "bow tie" framework*, Scientific Reports 8:9349, DOI
  [10.1038/s41598-018-27290-8](https://doi.org/10.1038/s41598-018-27290-8) (verified; full text read). They report a bimodal tie-strength distribution in Indian village networks, but it is an **artefact**: 96% of ties at maximum strength were within households. Without household ties the distribution is Poisson. It does not support C4.
- Onnela et al. (2007, PNAS, DOI [10.1073/pnas.0610245104](https://doi.org/10.1073/pnas.0610245104), verified) describe a *broad* (heavy-tailed) distribution of call-based tie strength.
- Iñiguez et al. (2023, §3) find universal gamma-like (heterogeneous) or Gaussian
  (homogeneous) strength distributions.
- Tamarit et al. (2022) imply a monotone distribution.

**Consequence.** Bimodality is Asym's most *distinctive* prediction, but it currently
lacks empirical support. Communication-volume distributions are unimodal and broad.
Two arguments are open to Asym. (i) Closeness is latent, and a bimodal latent variable
can produce a broad unimodal call distribution once heterogeneous rates and noise are
added. (ii) Questionnaire closeness on Likert scales (as in Tamarit 2018) could be
tested for bimodality. Expect reviewers to press on this.

### Further related empirical work
- Kossinets & Watts (2006), *Empirical analysis of an evolving social network*, Science
  311:88–90, DOI [10.1126/science.1116869](https://doi.org/10.1126/science.1116869) (verified; abstract read). Network evolution is driven by triadic closure and shared foci. Average properties approach equilibrium while individual properties stay unstable. This *supports* Asym's triadic-closure encounters and the "stationary layers, churning ties" picture.
- Wang, Gao, Zhou, Hu & Tian (2016), *Critical size of ego communication networks*, EPL
  114:58004, DOI [10.1209/0295-5075/114/58004](https://doi.org/10.1209/0295-5075/114/58004) (verified; abstract read). Above about 150 alters, average closeness and the share of strong ties drop. This supports a budget trade-off (C2).
- Dunbar (2016), *Do online social media cut through the constraints that limit the size
  of offline social networks?*, R. Soc. Open Sci. 3:150292, DOI [10.1098/rsos.150292](https://doi.org/10.1098/rsos.150292) (verified; abstract read). Online network sizes and inner layers match offline ones, which supports *C3* (more exposure does not enlarge the inner layers).
- Lindenfors, Wartel & Lind (2021), *"Dunbar's number" deconstructed*, Biology Letters
  17:20210158, DOI [10.1098/rsbl.2021.0158](https://doi.org/10.1098/rsbl.2021.0158) (verified; abstract read). Phylogenetic estimates of human group size have 95% CIs of 4–520, "specifying any one number is futile". This is a **framing risk**: anchor Asym on layer *ratios* and empirical ego-network data, not on 150 as a cognitive constant. That suits Asym, whose claim is that capacity is not needed.

---

## (3) Dynamical and agent-based models of tie formation and dissolution

### Jin, Girvan & Newman (2001)
*Structure of growing social networks.* Physical Review E 64:046132. DOI [10.1103/PhysRevE.64.046132](https://doi.org/10.1103/PhysRevE.64.046132) (verified; abstract read on APS and OpenAlex).

The model rests on three principles: pairs meet at a high rate if they share a mutual
friend and a low rate otherwise; acquaintances who rarely meet decay; and there is an
upper limit on the number of friendships. Together these reproduce clustering and
community structure.

- *C1: Asym differs.* Jin et al. **impose** a cap on friendships, while Asym's selling
  point is the *absence* of a cap. This contrast is worth stating explicitly.
- *C2/C3: Asym's encounter process (random + triadic) is this model's.* Decay of
  unmaintained ties is shared.
- *C4–C6: not addressed.*

### Davidsen, Ebel & Bornholdt (2002)
*Emergence of a small world from local interactions: modeling acquaintance networks.*
Physical Review Letters 88:128701. DOI [10.1103/PhysRevLett.88.128701](https://doi.org/10.1103/PhysRevLett.88.128701) (verified; abstract read).

Introductions by common acquaintances (triangle closure) plus random links, with node
turnover (*the turnover detail is from our knowledge of the paper, not the abstract*),
reproduce short paths, high clustering, and scale-free or exponential degree
distributions.

- *C2: supports by analogy.* Network size and degree are set by the balance between the
  link-creation rate and the lifetime of nodes or links. This is the "encounter rate ×
  lifetime" logic of Asym's exposure-bound outer layer.
- *C3: related.* Introductions scale with existing ties, not with N.

### Kumpula, Onnela, Saramäki, Kaski & Kertész (2007)
*Emergence of communities in weighted networks.* Physical Review Letters 99:228701. DOI [10.1103/PhysRevLett.99.228701](https://doi.org/10.1103/PhysRevLett.99.228701) (verified; abstract read).

Weights are generated dynamically and shape the topology. *(Mechanism details, from our
knowledge of the paper: weighted local search with reinforcement δ, global random
attachment, and node deletion.)* Tuning the importance of weights gives a transition from
module-free networks to networks with communities, reproducing Granovetter's weak-ties
property.

- *C5: related.* Reinforcement of used ties gives rich-get-richer weights, analogous to
  Asym's x^β. Asym's high-β all-or-nothing ties are the dyadic counterpart.
- *C3: related.* The global random-attachment probability controls structure, as Asym's
  ε does.

### Karsai, Perra & Vespignani (2014)
*Time varying networks and the weakness of strong ties.* Scientific Reports 4:4001. DOI [10.1038/srep04001](https://doi.org/10.1038/srep04001) (verified; abstract read).

From call data, they derive a simple law for ego-network growth and encode it as a
reinforcement process in activity-driven networks. *(The form p(new) = c/(c+k) is from
our knowledge of the paper.)* Strong and weak ties emerge from memory.

- *C3: closely related.* The probability of exploring a new alter falls with the number
  of known alters, so tie formation saturates. This is a data-driven version of Asym's
  "exploration toward ties only" (experiment 05), and should be cited as empirical
  justification for C3's condition.
- *C5: related* (memory-driven concentration).

### Ubaldi, Perra, Karsai, Vezzani, Burioni & Vespignani (2016); Ubaldi et al. (2017)
- *Asymptotic theory of time-varying social networks with heterogeneous activity and tie
  allocation.* Scientific Reports 6:35724. DOI [10.1038/srep35724](https://doi.org/10.1038/srep35724) (verified via Crossref). *(Abstract not retrieved. From our knowledge of the paper, with memory the degree grows sublinearly in time, without saturating.)*
- *Burstiness and tie activation strategies in time-varying social networks.* Scientific
  Reports 7:46225. DOI [10.1038/srep46225](https://doi.org/10.1038/srep46225) (verified via Crossref).

- *C2: related.* Without forgetting, the number of known alters keeps growing, so a
  stationary outer layer *requires* forgetting. That supports Asym's view that the outer
  layer is set by the lifetime of unmaintained ties.

### Iñiguez, Heydari, Kertész & Saramäki (2023)
*Universal patterns in egocentric communication networks.* Nature Communications
14:5217. DOI [10.1038/s41467-023-40888-5](https://doi.org/10.1038/s41467-023-40888-5) (verified; full text read, PMC10460427).

Across several datasets with millions of people, tie-strength distributions are
universal. The model gives a new event to alter a with probability (a+α)/(τ+kα), a
competition between **cumulative advantage and random choice**. A preferentiality
parameter β = t_r/α_r separates heterogeneous (gamma) regimes from homogeneous
(Gaussian) ones. The authors' 2026 arXiv follow-up (Adel et al., arXiv:2606.27937)
adds a bounded "bandwidth".

- *C5 (β): overlaps.* Asym's allocation ∝ x^β plus ε exploration is the same
  competition. The Iñiguez model has **no decay**, so it cannot produce bimodality or
  bistability. Asym's contribution is to show what decay plus circles add.
- *C4: competing prediction* (unimodal).
- This is the closest modern "mechanism for tie-strength heterogeneity" and must be
  cited.

### Weng, Flammini, Vespignani & Menczer (2012)
*Competition among memes in a world with limited attention.* Scientific Reports 2:335. DOI [10.1038/srep00335](https://doi.org/10.1038/srep00335) (verified via Crossref). *(Abstract not retrieved.)* This is the canonical limited-attention ABM. It is background for attention budgets, not for ties.

### Toivonen, Kovanen, Kivelä, Onnela, Saramäki & Kaski (2009)
*A comparative study of social network models: network evolution models and nodal
attribute models.* Social Networks 31(4):240–254. DOI [10.1016/j.socnet.2009.06.004](https://doi.org/10.1016/j.socnet.2009.06.004) (verified via Crossref). *(Abstract not retrieved.)* A review and comparison of the model families above. Useful for positioning Asym among network evolution models.

### Asymmetry of friendship perception and reciprocity

**Almaatouq, Radaelli, Pentland & Shmueli (2016).** *Are you your friends' friend? Poor
perception of friendship ties limits the ability to promote behavioral change.* PLOS ONE
11(3):e0151588. DOI [10.1371/journal.pone.0151588](https://doi.org/10.1371/journal.pone.0151588) (verified; full text read).

In a survey of 84 students, in 94% of nominations the nominator expected reciprocation,
but only about half of friendships were reciprocal. Perceived and reported scores
correlate at r = 0.95, meaning people project their own rating onto the alter. Influence
works along reciprocal ties or ties from influencer to target. **Tamarit et al. 2018 use
this same 84-student dataset** (their ref. 32) to fit the standard regime.

- *C6: supports the phenomenon* (persistent asymmetry plus over-expected reciprocity).
  Asym's *perception bias* parameter matches their finding. Their explanation is
  misperception, while Asym's is expectation heterogeneity, and the two can coexist.
  Validation opportunity: reproduce "about 50% reciprocal, about 94% expected" from
  Asym's r_ij versus actual x_ji.

**Ball & Newman (2013).** *Friendship networks and social status.* Network Science
1(1):16–30. DOI [10.1017/nws.2012.4](https://doi.org/10.1017/nws.2012.4) (verified; abstract read). In US school networks (Add Health), unreciprocated friendships almost always point from lower- to higher-ranked individuals, and the ranking correlates with status markers. Reciprocated and unreciprocated ties follow different statistics.

- *C6: competing explanation* (status hierarchy rather than heterogeneous expectations).
  Asym should test whether its asymmetries show an ordering (do butterflies receive more
  unreciprocated ties?). Otherwise a reviewer may argue status is the simpler
  explanation.

**Vaquera & Kao (2008).** *Do you like me as much as I like you? Friendship reciprocity
and its effects on school outcomes among adolescents.* Social Science Research
37(1):55–72. DOI [10.1016/j.ssresearch.2006.11.002](https://doi.org/10.1016/j.ssresearch.2006.11.002) (verified via Crossref; abstract not retrieved). Background on prevalence and consequences of non-reciprocity.

**Conceptual sources for heterogeneous reciprocity expectations** (all DOIs verified via
Crossref; used as theory, not re-read here): Gouldner (1960), the norm of reciprocity,
ASR 25:161, DOI [10.2307/2092623](https://doi.org/10.2307/2092623); Clark & Mills (1979), exchange vs communal relationships, JPSP 37:12–24, DOI [10.1037/0022-3514.37.1.12](https://doi.org/10.1037/0022-3514.37.1.12) (the natural grounding of the *transactional* archetype); Hall (2011), *Sex differences in friendship expectations: a meta-analysis*, JSPR 28:723–747, DOI [10.1177/0265407510386192](https://doi.org/10.1177/0265407510386192) (empirical heterogeneity of expectations); Rusbult (1980), investment model, JESP 16:172–186, DOI [10.1016/0022-1031(80)90007-4](https://doi.org/10.1016/0022-1031(80)90007-4).

- *C6:* together these establish that expectations vary, systematically by sex
  (Hall). We found **no ABM** deriving persistent network asymmetry from that
  heterogeneity. That is Asym's opening.

### Bistability and hysteresis in relationship dynamics (C5)
- **Gottman, Murray, Swanson, Tyson & Swanson (2002).** *The Mathematics of Marriage:
  Dynamic Nonlinear Models.* MIT Press. DOI [10.7551/mitpress/4499.001.0001](https://doi.org/10.7551/mitpress/4499.001.0001) (verified via Crossref). *(The book was not consulted. Our understanding is that the nonlinear influence functions in their difference-equation models produce multiple stable steady states, one positive and one negative, but this is not verified against the source.)*
- **Felmlee & Greenberg (1999).** *A dynamic systems model of dyadic interaction.*
  Journal of Mathematical Sociology 23(3):155–180. DOI [10.1080/0022250X.1999.9990218](https://doi.org/10.1080/0022250X.1999.9990218) (verified; abstract read). In a linear ODE dyad, cooperative partners reach a compromise equilibrium, while non-cooperation often destabilises it.
- **Strogatz (1988).** *Love affairs and differential equations.* Mathematics Magazine
  61(1):35. DOI [10.1080/0025570X.1988.11977342](https://doi.org/10.1080/0025570X.1988.11977342) (verified via Crossref). **Rinaldi (1998).** *Laura and Petrarch: an intriguing case of cyclical love dynamics.* SIAM J. Appl. Math. 58(4):1205–1221. DOI [10.1137/S003613999630592X](https://doi.org/10.1137/S003613999630592X) (verified via Crossref). These are classic dyadic ODEs, linear or cyclic.

- *C5: partly known for isolated dyads.* Multiple equilibria in dyadic ODEs are known.
  **Apparently novel:** bistability that *appears only when the dyad is embedded* in
  budget competition (isolated dyads in Asym are monostable). We found no prior model
  with this property. The empirical support is indirect: early-lifetime predictability
  (Hidd et al. 2023) and liability of newness (Burt 2000, 2002).
- *Hysteresis between circles* is a modelling device in Asym, not an empirical claim.
  We found no literature measuring hysteresis in closeness transitions.

### Time and attention budgets
- Gonçalves et al. (2011), Miritello et al. (2013a,b) and Saramäki et al. (2014): see
  above.
- **Hall (2019).** *How many hours does it take to make a friend?* JSPR 36(4):1278–1296
  (online 2018). DOI [10.1177/0265407518761225](https://doi.org/10.1177/0265407518761225) (verified; abstract read). Hours together, leisure activities and everyday talk predict changes in closeness. *(The often-quoted thresholds of about 50/90/200 hours for casual, regular and good friends come from the paper's body, which we did not re-read here.)* This offers a **time-unit mapping** for Asym (ADR-0006, arbitrary time unit): calibrate the hours to promotion between circles.

### Stochastic actor-oriented models (statistical alternative)
- **Snijders, van de Bunt & Steglich (2010).** *Introduction to stochastic actor-based
  models for network dynamics.* Social Networks 32(1):44–60. DOI [10.1016/j.socnet.2009.02.004](https://doi.org/10.1016/j.socnet.2009.02.004) (verified via Crossref).
- **Snijders (2001).** *The statistical evaluation of social network dynamics.*
  Sociological Methodology 31:361–395. DOI [10.1111/0081-1750.00099](https://doi.org/10.1111/0081-1750.00099) (verified via Crossref).
- **Steglich, Snijders & Pearson (2010).** *Dynamic networks and behavior: separating
  selection from influence.* Sociological Methodology 40:329–393. DOI [10.1111/j.1467-9531.2010.01225.x](https://doi.org/10.1111/j.1467-9531.2010.01225.x) (verified via Crossref).
- **Elmer, Boda & Stadtfeld (2017).** *The co-evolution of emotional well-being with weak
  and strong friendship ties.* Preprint DOI [10.31235/osf.io/ayu6k](https://doi.org/10.31235/osf.io/ayu6k) (verified). It uses *ordered* SAOMs for weak and strong ties jointly. The journal version (Network Science, 2017) is **UNVERIFIED** (DOI not confirmed).

SAOMs are continuous-time Markov models in which actors change one tie at a time to
improve an objective function. They are estimated from panel data. Asym is also a
continuous-time actor-based stochastic process (PDMP). The relationship should be spelled
out: SAOMs estimate tie-change preferences from data on binary or ordered ties, without a
budget, while Asym is a generative theory with continuous closeness, explicit time budget
and decay.

- *Reviewers will ask why a theoretical ABM is preferred over a SAOM.* Answer: (i) SAOMs
  have no resource budget, and their tie states are discrete without continuous latent
  closeness; (ii) Asym's predictions (bimodality, N-scaling, bistability) are about
  emergent macro-structure that SAOMs take as data. A strong paper could fit an ordered
  SAOM to Asym-generated panels to show which Asym mechanisms a SAOM would detect.
- For mechanism-based framing, Hedström & Ylikoski (2010), *Causal mechanisms in the
  social sciences*, Annu. Rev. Sociol. 36:49–67, DOI [10.1146/annurev.soc.012809.102632](https://doi.org/10.1146/annurev.soc.012809.102632) (verified via Crossref).

---

## (4) JASSS precedents and expectations

### JASSS precedents on friendship and social-circle dynamics
- **Sutcliffe, Wang & Dunbar (2012)**, JASSS 15(4):3, and **Sutcliffe & Wang (2012)**,
  JASSS 15(1):3. These are the direct precedents (see §1). Cite both prominently.
- **Hamill & Gilbert (2009).** *Social circles: a simple structure for agent-based
  social network models.* JASSS 12(2):3. https://www.jasss.org/12/2/3.html (no DOI;
  page verified). Agents sit on a social map and link if each is within the other's
  "social reach", giving low density, high clustering and assortativity. The paper
  explicitly states "No dynamics are proposed". Despite the name, it is not about
  Dunbar layers. Cite it as a static network generator for ABMs and to avoid the name
  clash with "circles".
- **Pujol, Flache, Delgado & Sangüesa (2005).** *How can social networks ever become
  complex? Modelling the emergence of complex networks from local social exchanges.*
  JASSS 8(4):12. https://www.jasss.org/8/4/12.html (no DOI; page verified). Complex
  networks emerge from social-exchange behaviour. *(Details beyond title and keywords
  not verified.)*
- **Zeggelink (1995).** *Evolving friendship networks: an individual-oriented approach
  implementing similarity.* Social Networks 17(2):83–110. DOI [10.1016/0378-8733(94)00246-7](https://doi.org/10.1016/0378-8733(94)00246-7) (verified via Crossref; not JASSS). This is an early individual-oriented friendship model, which reviewers in sociology will know.
- We searched jasss.org for ABMs with Dunbar layers, tie decay and reciprocity. Apart
  from the Sutcliffe papers, we found **no JASSS paper on dynamical emergence of layered
  ego networks**. That is a gap Asym fills.

### Methodological expectations
- **ODD protocol.** Grimm et al. (2006), Ecol. Model. 198:115–126, DOI [10.1016/j.ecolmodel.2006.04.023](https://doi.org/10.1016/j.ecolmodel.2006.04.023); Grimm et al. (2010), Ecol. Model. 221:2760–2768, DOI [10.1016/j.ecolmodel.2010.08.019](https://doi.org/10.1016/j.ecolmodel.2010.08.019); **Grimm et al. (2020)**, *The ODD protocol for describing agent-based and other simulation models: a second update to improve clarity, replication, and structural realism*, JASSS 23(2):7, DOI [10.18564/jasss.4259](https://doi.org/10.18564/jasss.4259) (all verified). JASSS reviewers expect an ODD (main text or appendix), now including the "Purpose and patterns" element. Asym's model-spec and ADRs map naturally onto it. Note that a PDMP has no fixed schedule, so ODD "Process overview and scheduling" must describe event rates and the ODE flow.
- **Sensitivity analysis.** ten Broeke, van Voorn & Ligtenberg (2016), JASSS 19(1):5, DOI [10.18564/jasss.2857](https://doi.org/10.18564/jasss.2857) (verified; abstract read) recommend **extended OAT as the starting point**, complemented by Sobol' variance decomposition. Ligmann-Zielinska et al. (2020), JASSS 23(1):6, DOI [10.18564/jasss.4201](https://doi.org/10.18564/jasss.4201) (verified) give purpose-driven pathways. Saltelli et al. (2010), Comput. Phys. Commun. 181:259–270, DOI [10.1016/j.cpc.2009.09.018](https://doi.org/10.1016/j.cpc.2009.09.018) (verified) give the estimator. Thiele, Kurth & Grimm (2014), JASSS 17(3):11, DOI [10.18564/jasss.2503](https://doi.org/10.18564/jasss.2503) (verified; abstract read) is the cookbook for calibration (random search, Latin hypercube, ABC) and sensitivity analysis. Asym's random-search calibration should be presented within this framework.
- **Output analysis and replicates.** Lee et al. (2015), *The complexities of agent-based
  modeling output analysis*, JASSS 18(4):4, DOI [10.18564/jasss.2897](https://doi.org/10.18564/jasss.2897) (verified). Three seeds per condition (experiment 06) will be judged insufficient. Justify the number of replicates by variance stabilisation.
- **Pattern-oriented modelling.** Grimm et al. (2005), Science 310:987–991, DOI [10.1126/science.1116681](https://doi.org/10.1126/science.1116681) (verified). Validate against *several* patterns at once (layer ratios, signature persistence, inner-circle churn, reciprocity rate, decay-hazard shape) instead of only the ratio of 3.
- **Replication and docking.** Axtell, Axelrod, Epstein & Cohen (1996), Comput. Math.
  Organ. Theory 1:123–141, DOI [10.1007/BF01299065](https://doi.org/10.1007/BF01299065) (verified); Edmonds & Hales (2003), *Replication, replication and replication*, JASSS 6(4):11, https://www.jasss.org/6/4/11.html (no DOI; verified); Wilensky & Rand (2007), *Making models match: replicating an agent-based model*, JASSS 10(4):2, https://www.jasss.org/10/4/2.html (no DOI; page verified). Asym's **ODE ↔ ABM agreement is a docking exercise** and should be presented as such. Docking against Tamarit (static limit) and against Jin et al. or Sutcliffe et al. (switching off budget or circles) would strengthen the paper.
- **Code availability.** Rollins et al. (2014), *A computational model library for
  publishing model documentation and code*, Env. Model. Softw. 61:59–64, DOI [10.1016/j.envsoft.2014.06.022](https://doi.org/10.1016/j.envsoft.2014.06.022) (verified); Janssen (2017), *The practice of archiving model code of agent-based models*, JASSS 20(1):2, DOI [10.18564/jasss.3317](https://doi.org/10.18564/jasss.3317) (verified). Deposit the code on CoMSES (OpenABM) with a DOI. JASSS strongly encourages this.
- **Modelling purpose.** Edmonds et al. (2019), *Different modelling purposes*, JASSS
  22(3):6, DOI [10.18564/jasss.3993](https://doi.org/10.18564/jasss.3993) (verified). State the purpose explicitly ("theoretical exposition" and "explanation" of stylised facts, not prediction). This matches CONTEXT.md ("validated against stylised facts, not fitted").

---

## Table: Asym claim × literature

| Claim | Status | Key references | Comment |
|---|---|---|---|
| **C1** Layers with ratio ≈ 3 from a finite time budget, no capacity | **Known in principle; partially novel in form** | Tamarit et al. 2018, 2022; Sutcliffe et al. 2012 BJP; Sutcliffe, Wang & Dunbar 2012 JASSS; Sutcliffe & Wang 2012 JASSS; Gonçalves et al. 2011; Miritello et al. 2013a | Budget ⇒ layers is Tamarit's result (static). A JASSS ABM already reproduces layers. Asym's novelty is the *dynamical* mechanism (decay ladder + allocation) and no cap. The ratio of 3 is *calibrated*, not predicted. |
| **C2** Inner budget-bound, outer exposure-bound | **Partially known** (ingredients); **apparently novel** as an explicit decomposition | Saramäki et al. 2014; Miritello et al. 2013b; Dunbar 2016; Davidsen et al. 2002; Ubaldi et al. 2016; Roy et al. 2022; Tamarit et al. 2018 (S/L dependence) | Data support budget-shaped inner allocation and churning periphery. No prior model states which layers scale with what. |
| **C3** N-independence only if tie formation does not scale with N | **Apparently novel** as a model result; consistent with data | Karsai et al. 2014 (saturating exploration); Sutcliffe, Wang & Dunbar 2012 (retuning at N = 500); Tamarit et al. 2018 (inverse regime at small L); Escribano et al. 2021; Dunbar 2016 | Must be reconciled with Tamarit's inverse regime: show the small-N limit. |
| **C4** Bimodal closeness; self-sustaining inner circle; thresholds constrained | **Mechanism known, bimodality apparently novel but empirically unsupported** | Burt 2000, 2002; Roberts & Dunbar 2011b, 2015; Raeder et al. 2011; Sutcliffe & Wang 2012 (strength-dependent waning); Roy et al. 2022 (stable inner circle) vs Wellman et al. 1997 (27% decade persistence); Tamarit et al. 2022 and Iñiguez et al. 2023 (unimodal predictions); Mattie et al. 2018 (artefactual bimodality) | Slower decay of strong ties is empirical and was used in a JASSS ABM. Bimodality contradicts the existing continuous models and lacks direct evidence. This is the highest-risk and highest-reward claim. |
| **C5** Embedded dyads bistable, isolated dyads monostable, high β all-or-nothing | **Apparently novel** (network-embedded bistability); **partially known** (dyadic multistability, cumulative advantage) | Gottman et al. 2002; Felmlee & Greenberg 1999; Iñiguez et al. 2023; Kumpula et al. 2007; Hidd et al. 2023; Burt 2002 | "Isolated dyad ⇒ friendship" parallels Tamarit's inverse regime. Rename "embedded" (Burt's meaning is opposite). |
| **C6** Asymmetry from heterogeneous reciprocity expectations | **Phenomenon known; mechanism apparently novel** (as an ABM result) | Almaatouq et al. 2016; Ball & Newman 2013; Vaquera & Kao 2008; Hall 2011; Clark & Mills 1979; Gouldner 1960; Hidalgo & Rodríguez-Sickert 2008 | Competing explanations are status and misperception. The bare statement is close to tautological, so publish its network-level consequences. |

---

## Gaps and what reviewers will likely ask

1. **"How is this different from Tamarit et al. 2018?"** Prepare a dedicated paragraph
   and, ideally, a figure. Show that Asym's stationary layer proportions can be fitted by
   Tamarit's μ, and how μ maps onto Asym parameters (budget, decay ladder, β). Show
   whether Asym reproduces the **inverse regime** at small N or for loyal_few agents.
   That makes Tamarit a special case or limit rather than a competitor.
2. **"Sutcliffe et al. already did this in JASSS."** State the differences: no imposed
   terciles or capacity; an invitation, acceptance and patience protocol; directed ties
   with reciprocity memory; a mean-field ODE; an explanation of the N-dependence they
   observed.
3. **Calibration vs emergence.** The ratios of about 3 come from calibrating thresholds
   toward 3. Reviewers will say the layering is fitted. Mitigations: (i) report the
   fraction of parameter space with ratios in [2, 4] (cf. Sutcliffe et al. 2016); (ii)
   validate on *other* patterns not used in calibration (signature persistence, inner
   churn of 1–4% per year, reciprocity about 50%, decay hazard); (iii) define layers
   from the data as Mac Carron et al. 2016 do (clustering of closeness) instead of from
   the model's own thresholds.
4. **Absolute sizes.** About 43 total ties vs 150. Either map the circles onto
   1.5/5/15/50 (Dunbar et al. 2015) or show how the budget and encounter rate scale the
   outer layer. C2 predicts the outer layer can be enlarged via exposure without
   touching the inner layers. Show that.
5. **Bimodality evidence.** Expect "show me bimodal closeness in real data". Propose a
   concrete test (Likert closeness in Tamarit/Almaatouq-type surveys; mixture versus
   unimodal fits) and discuss how latent bimodality maps onto broad unimodal call
   counts.
6. **Turnover realism.** A "self-sustaining" inner circle must still show realistic
   churn (Roy et al. 2022: 1–4% per year; Wellman et al. 1997: 27% intimate persistence
   per decade; Saramäki et al. 2014). Report residence-time distributions per circle.
   Consider exogenous life-event shocks.
7. **Time-unit mapping** (ADR-0006). Anchor time with Hall (2019) hours-to-friendship
   and Navarro et al. (2017) silence-to-decay ratios. Otherwise churn and decay results
   cannot be compared with data.
8. **ODD + sensitivity.** Full ODD (Grimm et al. 2020). Use extended OAT then Sobol'
   on the main outputs (layer sizes, ratios, bimodality index, bistability region,
   asymmetry). Use more replicates than three seeds (Lee et al. 2015).
9. **Docking.** ODE ↔ ABM agreement, plus limiting cases: no budget or circles (Jin et
   al. type), static limit (Tamarit). JASSS values this.
10. **Terminology.** "Embedded dyad" clashes with Burt and Granovetter. "Circles"
    clashes with Hamill & Gilbert's "social circles". "Inverse"/"inner" should match
    Tamarit's usage. Add a glossary table.
11. **Missing ingredients reviewers may flag.** Kin (cheaper maintenance, substitution
    for close friends; Roberts & Dunbar 2011a; Sutcliffe & Wang 2012), space or
    distance (Mok & Wellman 2007), multiplex channels (Heydari et al. 2018),
    status-driven asymmetry (Ball & Newman 2013). Acknowledge these as scope
    limitations.
12. **The "Dunbar's number" controversy.** Lindenfors et al. 2021. Asym avoids it by not
    assuming a capacity. Say so; it is a selling point.
13. **Code and data.** Deposit on CoMSES with a DOI. Make experiment YAMLs and seeds
    available. Results are currently "not versioned".

---

## References (alphabetical)

All DOIs were resolved via Crossref unless marked otherwise. "No DOI" means the item has
no registered DOI and the URL was verified instead.

- Adel, G., Bhuria, S., Catalano, A., Dorizzi, L., Federici, L., Moldovan, T., Nortier, B., Punzal, C. D., de Meijere, G., & Iñiguez, G. (2026). Preferentiality and bandwidth drive tie activity in online and offline ego networks. arXiv:2606.27937 (preprint; arXiv page verified; not peer reviewed).
- Almaatouq, A., Radaelli, L., Pentland, A., & Shmueli, E. (2016). Are you your friends' friend? Poor perception of friendship ties limits the ability to promote behavioral change. *PLOS ONE*, 11(3), e0151588. https://doi.org/10.1371/journal.pone.0151588
- Arnaboldi, V., Conti, M., Passarella, A., & Pezzoni, F. (2013). Ego networks in Twitter: an experimental analysis. *Proc. IEEE INFOCOM 2013*, 3459–3464. https://doi.org/10.1109/INFCOM.2013.6567181
- Arnaboldi, V., Guazzini, A., & Passarella, A. (2013). Egocentric online social networks: analysis of key features and prediction of tie strength in Facebook. *Computer Communications*, 36(10–11), 1130–1144. https://doi.org/10.1016/j.comcom.2013.03.003
- Axtell, R., Axelrod, R., Epstein, J. M., & Cohen, M. D. (1996). Aligning simulation models: a case study and results. *Computational and Mathematical Organization Theory*, 1, 123–141. https://doi.org/10.1007/BF01299065
- Ball, B., & Newman, M. E. J. (2013). Friendship networks and social status. *Network Science*, 1(1), 16–30. https://doi.org/10.1017/nws.2012.4
- Burt, R. S. (2000). Decay functions. *Social Networks*, 22(1), 1–28. https://doi.org/10.1016/S0378-8733(99)00015-5
- Burt, R. S. (2002). Bridge decay. *Social Networks*, 24(4), 333–363. https://doi.org/10.1016/S0378-8733(02)00017-5
- Centellegher, S., López, E., Saramäki, J., & Lepri, B. (2017). Personality traits and ego-network dynamics. *PLOS ONE*, 12(3), e0173110. https://doi.org/10.1371/journal.pone.0173110
- Clark, M. S., & Mills, J. (1979). Interpersonal attraction in exchange and communal relationships. *Journal of Personality and Social Psychology*, 37(1), 12–24. https://doi.org/10.1037/0022-3514.37.1.12
- Davidsen, J., Ebel, H., & Bornholdt, S. (2002). Emergence of a small world from local interactions: modeling acquaintance networks. *Physical Review Letters*, 88, 128701. https://doi.org/10.1103/PhysRevLett.88.128701
- Dunbar, R. I. M. (2016). Do online social media cut through the constraints that limit the size of offline social networks? *Royal Society Open Science*, 3, 150292. https://doi.org/10.1098/rsos.150292
- Dunbar, R. I. M. (2018). The anatomy of friendship. *Trends in Cognitive Sciences*, 22(1), 32–51. https://doi.org/10.1016/j.tics.2017.10.004
- Dunbar, R. I. M., Arnaboldi, V., Conti, M., & Passarella, A. (2015). The structure of online social networks mirrors those in the offline world. *Social Networks*, 43, 39–47. https://doi.org/10.1016/j.socnet.2015.04.005
- Edmonds, B., & Hales, D. (2003). Replication, replication and replication: some hard lessons from model alignment. *JASSS*, 6(4), 11. https://www.jasss.org/6/4/11.html (no DOI)
- Edmonds, B., Le Page, C., Bithell, M., Chattoe-Brown, E., Grimm, V., et al. (2019). Different modelling purposes. *JASSS*, 22(3), 6. https://doi.org/10.18564/jasss.3993
- Elmer, T., Boda, Z., & Stadtfeld, C. (2017). The co-evolution of emotional well-being with weak and strong friendship ties. Preprint, SocArXiv. https://doi.org/10.31235/osf.io/ayu6k (journal version in *Network Science*: UNVERIFIED)
- Escribano, D., Doldán-Martelli, V., Lapuente, F. J., Cuesta, J. A., & Sánchez, A. (2021). Evolution of social relationships between first-year students at middle school: from cliques to circles. *Scientific Reports*, 11, 11694. https://doi.org/10.1038/s41598-021-90984-z
- Felmlee, D. H., & Greenberg, D. F. (1999). A dynamic systems model of dyadic interaction. *Journal of Mathematical Sociology*, 23(3), 155–180. https://doi.org/10.1080/0022250X.1999.9990218
- Gonçalves, B., Perra, N., & Vespignani, A. (2011). Modeling users' activity on Twitter networks: validation of Dunbar's number. *PLOS ONE*, 6(8), e22656. https://doi.org/10.1371/journal.pone.0022656
- Gottman, J. M., Murray, J. D., Swanson, C. C., Tyson, R., & Swanson, K. R. (2002). *The Mathematics of Marriage: Dynamic Nonlinear Models*. MIT Press. https://doi.org/10.7551/mitpress/4499.001.0001
- Gouldner, A. W. (1960). The norm of reciprocity: a preliminary statement. *American Sociological Review*, 25(2), 161–178. https://doi.org/10.2307/2092623
- Grimm, V., Berger, U., Bastiansen, F., Eliassen, S., Ginot, V., et al. (2006). A standard protocol for describing individual-based and agent-based models. *Ecological Modelling*, 198, 115–126. https://doi.org/10.1016/j.ecolmodel.2006.04.023
- Grimm, V., Berger, U., DeAngelis, D. L., Polhill, J. G., Giske, J., & Railsback, S. F. (2010). The ODD protocol: a review and first update. *Ecological Modelling*, 221, 2760–2768. https://doi.org/10.1016/j.ecolmodel.2010.08.019
- Grimm, V., Railsback, S. F., Vincenot, C. E., Berger, U., Gallagher, C., et al. (2020). The ODD protocol for describing agent-based and other simulation models: a second update to improve clarity, replication, and structural realism. *JASSS*, 23(2), 7. https://doi.org/10.18564/jasss.4259
- Grimm, V., Revilla, E., Berger, U., Jeltsch, F., Mooij, W. M., et al. (2005). Pattern-oriented modeling of agent-based complex systems: lessons from ecology. *Science*, 310, 987–991. https://doi.org/10.1126/science.1116681
- Hall, J. A. (2011). Sex differences in friendship expectations: a meta-analysis. *Journal of Social and Personal Relationships*, 28(6), 723–747. https://doi.org/10.1177/0265407510386192
- Hall, J. A. (2019). How many hours does it take to make a friend? *Journal of Social and Personal Relationships*, 36(4), 1278–1296. https://doi.org/10.1177/0265407518761225
- Hamill, L., & Gilbert, N. (2009). Social circles: a simple structure for agent-based social network models. *JASSS*, 12(2), 3. https://www.jasss.org/12/2/3.html (no DOI)
- Hedström, P., & Ylikoski, P. (2010). Causal mechanisms in the social sciences. *Annual Review of Sociology*, 36, 49–67. https://doi.org/10.1146/annurev.soc.012809.102632
- Heydari, S., Roberts, S. G. B., Dunbar, R. I. M., & Saramäki, J. (2018). Multichannel social signatures and persistent features of ego networks. *Applied Network Science*, 3, 8. https://doi.org/10.1007/s41109-018-0065-4
- Hidalgo, C. A., & Rodríguez-Sickert, C. (2008). The dynamics of a mobile phone network. *Physica A*, 387(12), 3017–3024. https://doi.org/10.1016/j.physa.2008.01.073
- Hidd, V. V., López, E., Centellegher, S., Roberts, S. G. B., Lepri, B., & Dunbar, R. I. M. (2023). The stability of transient relationships. *Scientific Reports*, 13, 6120. https://doi.org/10.1038/s41598-023-32206-2
- Hill, R. A., & Dunbar, R. I. M. (2003). Social network size in humans. *Human Nature*, 14(1), 53–72. https://doi.org/10.1007/s12110-003-1016-y
- Iñiguez, G., Heydari, S., Kertész, J., & Saramäki, J. (2023). Universal patterns in egocentric communication networks. *Nature Communications*, 14, 5217. https://doi.org/10.1038/s41467-023-40888-5
- Janssen, M. A. (2017). The practice of archiving model code of agent-based models. *JASSS*, 20(1), 2. https://doi.org/10.18564/jasss.3317
- Jin, E. M., Girvan, M., & Newman, M. E. J. (2001). Structure of growing social networks. *Physical Review E*, 64, 046132. https://doi.org/10.1103/PhysRevE.64.046132
- Karsai, M., Perra, N., & Vespignani, A. (2014). Time varying networks and the weakness of strong ties. *Scientific Reports*, 4, 4001. https://doi.org/10.1038/srep04001
- Kossinets, G., & Watts, D. J. (2006). Empirical analysis of an evolving social network. *Science*, 311, 88–90. https://doi.org/10.1126/science.1116869
- Kumpula, J. M., Onnela, J.-P., Saramäki, J., Kaski, K., & Kertész, J. (2007). Emergence of communities in weighted networks. *Physical Review Letters*, 99, 228701. https://doi.org/10.1103/PhysRevLett.99.228701
- Lee, J.-S., Filatova, T., Ligmann-Zielinska, A., Hassani-Mahmooei, B., Stonedahl, F., et al. (2015). The complexities of agent-based modeling output analysis. *JASSS*, 18(4), 4. https://doi.org/10.18564/jasss.2897
- Ligmann-Zielinska, A., Siebers, P.-O., Magliocca, N., Parker, D. C., Grimm, V., et al. (2020). 'One size does not fit all': a roadmap of purpose-driven mixed-method pathways for sensitivity analysis of agent-based models. *JASSS*, 23(1), 6. https://doi.org/10.18564/jasss.4201
- Lindenfors, P., Wartel, A., & Lind, J. (2021). 'Dunbar's number' deconstructed. *Biology Letters*, 17, 20210158. https://doi.org/10.1098/rsbl.2021.0158
- Mac Carron, P., Kaski, K., & Dunbar, R. (2016). Calling Dunbar's numbers. *Social Networks*, 47, 151–155. https://doi.org/10.1016/j.socnet.2016.06.003
- Mattie, H., Engø-Monsen, K., Ling, R., & Onnela, J.-P. (2018). Understanding tie strength in social networks using a local "bow tie" framework. *Scientific Reports*, 8, 9349. https://doi.org/10.1038/s41598-018-27290-8
- Miritello, G., Lara, R., Cebrian, M., & Moro, E. (2013b). Limited communication capacity unveils strategies for human interaction. *Scientific Reports*, 3, 1950. https://doi.org/10.1038/srep01950
- Miritello, G., Moro, E., Lara, R., Martínez-López, R., Belchamber, J., Roberts, S. G. B., & Dunbar, R. I. M. (2013a). Time as a limited resource: communication strategy in mobile phone networks. *Social Networks*, 35(1), 89–95. https://doi.org/10.1016/j.socnet.2013.01.003
- Mok, D., & Wellman, B. (2007). Did distance matter before the Internet? Interpersonal contact and support in the 1970s. *Social Networks*, 29(3), 430–461. https://doi.org/10.1016/j.socnet.2007.01.009
- Navarro, H., Miritello, G., Canales, A., & Moro, E. (2017). Temporal patterns behind the strength of persistent ties. *EPJ Data Science*, 6, 31. https://doi.org/10.1140/epjds/s13688-017-0127-3
- Onnela, J.-P., Saramäki, J., Hyvönen, J., Szabó, G., Lazer, D., et al. (2007). Structure and tie strengths in mobile communication networks. *PNAS*, 104(18), 7332–7336. https://doi.org/10.1073/pnas.0610245104
- Pujol, J. M., Flache, A., Delgado, J., & Sangüesa, R. (2005). How can social networks ever become complex? Modelling the emergence of complex networks from local social exchanges. *JASSS*, 8(4), 12. https://www.jasss.org/8/4/12.html (no DOI)
- Raeder, T., Lizardo, O., Hachen, D., & Chawla, N. V. (2011). Predictors of short-term decay of cell phone contacts in a large scale communication network. *Social Networks*, 33(4), 245–257. https://doi.org/10.1016/j.socnet.2011.07.002
- Rinaldi, S. (1998). Laura and Petrarch: an intriguing case of cyclical love dynamics. *SIAM Journal on Applied Mathematics*, 58(4), 1205–1221. https://doi.org/10.1137/S003613999630592X
- Roberts, S. G. B., & Dunbar, R. I. M. (2011a). Communication in social networks: effects of kinship, network size, and emotional closeness. *Personal Relationships*, 18(3), 439–452. https://doi.org/10.1111/j.1475-6811.2010.01310.x
- Roberts, S. G. B., & Dunbar, R. I. M. (2011b). The costs of family and friends: an 18-month longitudinal study of relationship maintenance and decay. *Evolution and Human Behavior*, 32(3), 186–197. https://doi.org/10.1016/j.evolhumbehav.2010.08.005
- Roberts, S. G. B., & Dunbar, R. I. M. (2015). Managing relationship decay: network, gender, and contextual effects. *Human Nature*, 26(4), 426–450. https://doi.org/10.1007/s12110-015-9242-7
- Rollins, N. D., Barton, C. M., Bergin, S., Janssen, M. A., & Lee, A. (2014). A computational model library for publishing model documentation and code. *Environmental Modelling & Software*, 61, 59–64. https://doi.org/10.1016/j.envsoft.2014.06.022
- Roy, C., Bhattacharya, K., Dunbar, R. I. M., & Kaski, K. (2022). Turnover in close friendships. *Scientific Reports*, 12, 11018. https://doi.org/10.1038/s41598-022-15070-4
- Rusbult, C. E. (1980). Commitment and satisfaction in romantic associations: a test of the investment model. *Journal of Experimental Social Psychology*, 16(2), 172–186. https://doi.org/10.1016/0022-1031(80)90007-4
- Saltelli, A., Annoni, P., Azzini, I., Campolongo, F., Ratto, M., & Tarantola, S. (2010). Variance based sensitivity analysis of model output. Design and estimator for the total sensitivity index. *Computer Physics Communications*, 181(2), 259–270. https://doi.org/10.1016/j.cpc.2009.09.018
- Saramäki, J., Leicht, E. A., López, E., Roberts, S. G. B., Reed-Tsochas, F., & Dunbar, R. I. M. (2014). Persistence of social signatures in human communication. *PNAS*, 111(3), 942–947. https://doi.org/10.1073/pnas.1308540110
- Snijders, T. A. B. (2001). The statistical evaluation of social network dynamics. *Sociological Methodology*, 31, 361–395. https://doi.org/10.1111/0081-1750.00099
- Snijders, T. A. B., van de Bunt, G. G., & Steglich, C. E. G. (2010). Introduction to stochastic actor-based models for network dynamics. *Social Networks*, 32(1), 44–60. https://doi.org/10.1016/j.socnet.2009.02.004
- Steglich, C., Snijders, T. A. B., & Pearson, M. (2010). Dynamic networks and behavior: separating selection from influence. *Sociological Methodology*, 40, 329–393. https://doi.org/10.1111/j.1467-9531.2010.01225.x
- Strogatz, S. H. (1988). Love affairs and differential equations. *Mathematics Magazine*, 61(1), 35. https://doi.org/10.1080/0025570X.1988.11977342
- Sutcliffe, A., Dunbar, R., Binder, J., & Arrow, H. (2012). Relationships and the social brain: integrating psychological and evolutionary perspectives. *British Journal of Psychology*, 103(2), 149–168. https://doi.org/10.1111/j.2044-8295.2011.02061.x
- Sutcliffe, A., Dunbar, R., & Wang, D. (2016). Modelling the evolution of social structure. *PLOS ONE*, 11(7), e0158605. https://doi.org/10.1371/journal.pone.0158605
- Sutcliffe, A., & Wang, D. (2012). Computational modelling of trust and social relationships. *JASSS*, 15(1), 3. https://doi.org/10.18564/jasss.1912
- Sutcliffe, A., Wang, D., & Dunbar, R. (2012). Social relationships and the emergence of social networks. *JASSS*, 15(4), 3. https://doi.org/10.18564/jasss.2059
- Tamarit, I., Cuesta, J. A., Dunbar, R. I. M., & Sánchez, A. (2018). Cognitive resource allocation determines the organization of personal networks. *PNAS*, 115(33), 8316–8321. https://doi.org/10.1073/pnas.1719233115
- Tamarit, I., Sánchez, A., & Cuesta, J. A. (2022). Beyond Dunbar circles: a continuous description of social relationships and resource allocation. *Scientific Reports*, 12, 2287. https://doi.org/10.1038/s41598-022-06066-1
- ten Broeke, G., van Voorn, G., & Ligtenberg, A. (2016). Which sensitivity analysis method should I use for my agent-based model? *JASSS*, 19(1), 5. https://doi.org/10.18564/jasss.2857
- Thiele, J. C., Kurth, W., & Grimm, V. (2014). Facilitating parameter estimation and sensitivity analysis of agent-based models: a cookbook using NetLogo and 'R'. *JASSS*, 17(3), 11. https://doi.org/10.18564/jasss.2503
- Toivonen, R., Kovanen, L., Kivelä, M., Onnela, J.-P., Saramäki, J., & Kaski, K. (2009). A comparative study of social network models: network evolution models and nodal attribute models. *Social Networks*, 31(4), 240–254. https://doi.org/10.1016/j.socnet.2009.06.004
- Ubaldi, E., Perra, N., Karsai, M., Vezzani, A., Burioni, R., & Vespignani, A. (2016). Asymptotic theory of time-varying social networks with heterogeneous activity and tie allocation. *Scientific Reports*, 6, 35724. https://doi.org/10.1038/srep35724
- Ubaldi, E., Vezzani, A., Karsai, M., Perra, N., & Burioni, R. (2017). Burstiness and tie activation strategies in time-varying social networks. *Scientific Reports*, 7, 46225. https://doi.org/10.1038/srep46225
- Vaquera, E., & Kao, G. (2008). Do you like me as much as I like you? Friendship reciprocity and its effects on school outcomes among adolescents. *Social Science Research*, 37(1), 55–72. https://doi.org/10.1016/j.ssresearch.2006.11.002
- Wang, Q., Gao, J., Zhou, T., Hu, Z., & Tian, H. (2016). Critical size of ego communication networks. *EPL*, 114(5), 58004. https://doi.org/10.1209/0295-5075/114/58004
- Wellman, B., & Wortley, S. (1990). Different strokes from different folks: community ties and social support. *American Journal of Sociology*, 96(3), 558–588. https://doi.org/10.1086/229572
- Wellman, B., Wong, R. Y., Tindall, D., & Nazer, N. (1997). A decade of network change: turnover, persistence and stability in personal communities. *Social Networks*, 19(1), 27–50. https://doi.org/10.1016/S0378-8733(96)00289-4
- Weng, L., Flammini, A., Vespignani, A., & Menczer, F. (2012). Competition among memes in a world with limited attention. *Scientific Reports*, 2, 335. https://doi.org/10.1038/srep00335
- Wilensky, U., & Rand, W. (2007). Making models match: replicating an agent-based model. *JASSS*, 10(4), 2. https://www.jasss.org/10/4/2.html (no DOI)
- Zeggelink, E. (1995). Evolving friendship networks: an individual-oriented approach implementing similarity. *Social Networks*, 17(2), 83–110. https://doi.org/10.1016/0378-8733(94)00246-7
- Zhou, W.-X., Sornette, D., Hill, R. A., & Dunbar, R. I. M. (2005). Discrete hierarchical organization of social group sizes. *Proceedings of the Royal Society B*, 272, 439–444. https://doi.org/10.1098/rspb.2004.2970

**Notes on verification limits.** Volumes, article numbers and pages were taken from
Crossref metadata. The only UNVERIFIED bibliographic item is the Network Science version
of Elmer et al. (2017). Items whose *content* was not read from the source (some
Elsevier and APS abstracts, the Gottman book, mechanism details of Davidsen, Kumpula,
Karsai and Ubaldi) are flagged inline with "not verified against the source" or "from
our knowledge of the paper".
