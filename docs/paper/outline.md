# Article outline (target: JASSS)

Working document. Every result below points to the experiment report it comes
from (`docs/experiments/`); every reference is in
`docs/research/literature-review.md`, with verified DOIs. **Before submission,
check the current JASSS author guidelines** (length, abstract limit, reference
style, code-availability statement); they are not reproduced here.

---

## 1. Positioning in one paragraph

Layered ego networks (≈ 1.5/5/15/50/150, ratio ≈ 3) are well documented. Their
emergence from a finite resource has been explained twice:

- statically, by entropy maximisation under a cost constraint (Tamarit et al.
  2018), which also predicts an *inverse regime* in resource-rich, alter-poor
  settings;
- by agent-based models tuned to the target sizes (Sutcliffe et al. 2012, JASSS).

**Our contribution is not "another model that yields Dunbar layers".** Ours is a
dynamical, heterogeneous, directed model. It:

1. recovers Tamarit's two regimes and their control parameter as the steady state
   of a process with no optimisation;
2. reduces the drivers of the layer *size* to one maintenance ratio (B/δ), with
   separate levers for the *shape* (β) and the *inner circle* (η);
3. states the condition under which layers are independent of population size;
4. shows that the same mechanism makes relationships history-dependent, with a
   probabilistic threshold and profile-specific failure modes;
5. produces asymmetric, one-sided ties from heterogeneous reciprocity
   expectations.

## 2. Title candidates

1. *From time budgets to social circles: a dynamical model of layered, asymmetric
   and history-dependent relationships*
2. *Maintenance, concentration and exposure: what sets the size and shape of
   personal networks*
3. *Social circles as steady states: an agent-based model of relationship
   dynamics under finite time*

## 3. Draft abstract (≈ 200 words, to be refined)

> Personal networks are organised in layers of increasing size and decreasing
> emotional closeness, a pattern usually attributed to the finite time people can
> invest in relationships. We present an agent-based model in which heterogeneous
> agents allocate a budget of interaction slots through invitations that can be
> accepted, declined, ignored or cancelled. Closeness grows with interactions and
> erodes at a rate that depends on the circle a tie belongs to, and on a perceived
> reciprocity deficit. Calibrated to a scaling ratio of about three, the model
> reproduces, without further tuning, the inverse regime predicted for
> resource-rich, alter-poor communities, with the same control parameter: resources
> per available alter. A sensitivity analysis shows that the size of the network is
> set almost entirely by the ratio of budget to decay. Its shape is set by how
> concentrated the allocation is, and its outer layer by exposure to new people.
> Layering is independent of population size only if tie formation does not
> accelerate with it. At the level of dyads, competition for time makes
> relationships history-dependent: the mean-field threshold between breakup and
> friendship becomes a probabilistic one, with profile-specific failure modes.
> Heterogeneous reciprocity expectations generate persistent asymmetry and
> unreciprocated ties.

## 4. Structure

Each section lists what goes in it, which experiment supports it, and its status:
✅ done, 🟡 partial, ❌ missing.

### 1 Introduction (≈ 1.5 pages)
- Layered ego networks as a stylised fact (Hill & Dunbar 2003; Zhou et al. 2005;
  Dunbar et al. 2015; Mac Carron et al. 2016). Time as the limiting resource
  (Miritello et al. 2013a,b; Saramäki et al. 2014; Roberts & Dunbar 2011b).
- Two existing explanations and their limits:
  - Tamarit et al. 2018 is static: it has no dynamics, no dyads and no history;
  - Sutcliffe et al. 2012 is tuned to the target sizes: it does not separate the
    roles of the parameters, and its sizes depend on N.
- Two further dynamic facts any model should face:
  - relationships are asymmetric and often unreciprocated (Almaatouq et al. 2016;
    Ball & Newman 2013);
  - the fate of a tie is decided early (Hidd et al. 2023; Burt 2000).
- The questions below, and the contributions listed in §1 above.

**Research questions:**
1. What sets the size and the shape of the layered network, and when do layers
   depend on population size?
2. Are relationships history-dependent under competition for time, and how does
   noise change the picture?
3. Where does persistent asymmetry come from?

### 2 Related work (≈ 1.5 pages)
- **Mechanistic layering models:**
  - Tamarit et al. 2018, 2022 (continuous version, which predicts a monotone
    distribution of tie strength; our bimodality is a sharper alternative);
  - Sutcliffe & Wang 2012; Sutcliffe, Wang & Dunbar 2012; Sutcliffe et al. 2016.
- **Network-evolution models:** triadic and random encounters, decay and
  reinforcement (Jin, Girvan & Newman 2001; Davidsen et al. 2002; Kumpula et al.
  2007; Toivonen et al. 2009). Our tie-formation layer belongs to this family. Our
  contribution is the budgeted, directed, circle-structured maintenance.
- **Empirical dynamics:**
  - turnover of close ties: Wellman et al. 1997 (27% of intimate ties lasted a
    decade) versus Roy et al. 2022 (1–4% churn per year);
  - the persistence of social signatures: Saramäki et al. 2014; Heydari et al. 2018;
  - school cohorts: Escribano et al. 2021, which links to the transient from an
    empty start and to the inverse regime.
- **Asymmetry and reciprocity:** Almaatouq et al. 2016; Ball & Newman 2013.
- Statistical alternatives (stochastic actor-oriented models), one paragraph:
  different aim, inference rather than mechanism.

### 3 Model (≈ 3 pages + ODD in an appendix) ✅
- Overview figure (**Fig. 1**, ✅ draft): the agent, a directed tie (x, r, o, circle),
  the invitation life cycle (accept / decline / silence / late accept / cancel),
  and the circle hysteresis with circle-dependent decay.
- Core equations: the flow of x (decay by circle, deficit erosion), the
  allocation x^β·g(q), the acceptance probability, and the cancellation hazard.
  Source: ODD §7 and spec §4–7.
- The four archetypes as behavioural profiles (**Table 1**, from ODD Table 1).
- The PDMP simulation: exact thinning, lazy flow.
- **The mean-field limit and docking with the ABM** (convergence 0.038 → 0.015 →
  0.006). This is short in the main text; the ODD gives the details. Source:
  `tests/test_09_meanfield.py`; docking figure ✅ (Fig. 11, exp 16: error 0.047 → 0.004 from s = 1 to 4, then at the sampling floor; ABM spread ∝ s^−1/2).
- The `exploration: ties` assumption and its justification (§5.3).
- Full ODD: Appendix A (`docs/odd.md`) ✅.

### 4 Calibration and baseline behaviour (≈ 2 pages)
- **Calibration target** (pattern 1): layer ratios ≈ 3, using the thresholds and
  the rescaled budget and decay. Say explicitly that the ratios are calibrated, not
  predicted. Source: exp 02, 06 ✅.
  - **Fig. 2** (✅ draft): cumulative layers versus N = 100/200/400 (exp 06), with the
    per-archetype layers inset.
- Stationarity and independence of the start (pattern 3). Source: exp 01, 01b ✅.
  The empty and random starts agree within 2–6%.
- **Bimodal closeness distribution** (**Fig. 3**, ✅ draft;: the histogram from exp 05 at
  N = 200 exists as numbers only). The self-sustaining inner circle explains why θ4
  cannot sit above the high mode (the calibration step that failed, exp 06). Present
  it as a **testable prediction** that contrasts with the monotone distribution of
  Tamarit et al. 2022.

### 5 Results I: what sets size and shape (≈ 3 pages)
- **5.1 Sensitivity screening** (Morris, 18 factors). Source: exp 10 ✅.
  **Fig. 4** (✅ draft): μ* versus σ for the main outputs.
  - Size: B, η and δ. Shape: β. Outer layer: ν. One-sided ties: ρ*.
  - Negligible: loyalty, patience, memory, a, x0.
- **5.2 The maintenance ratio.** Source: exp 11 ✅. **Fig. 5** (✅ draft): layer sizes
  against q for the four routes.
  - B and δ collapse to first order: q explains ≥ 0.98 of the variance of log(layer), in each
    of 2 population draws (exp 15). The gaps are systematic, up to about 30% at q = ½ with the
    same sign in both draws, so do not write "exchangeable" without this qualification.
  - η deviates at the two ends, through the jump size.
  - Mean-field argument ✅ (`docs/theory/maintenance-scaling.md`, exp 13):
    - Proposition 1: the stationary state depends on Q = ηB/δ, with the corrections
      K = κ/δ and o0/B. These corrections explain the B-versus-δ gaps.
    - Proposition 2: at a fixed mean, Var x = (η/2) x(1−x)²/(1 − β_eff(1−x)),
      independent of B and δ. η therefore sets the tails, and all 24 sign
      comparisons of exp 11 agree. Widening the noise alone gives about 70% of the
      η excess on the inner circle. The 24 comparisons hold in each draw separately (exp 15).
- **5.3 Population size and exposure.** Source: exp 02, 05 ✅. **Fig. 6** (✅ draft):
  outer layer versus N under baseline and tie-only exploration.
  - Inner circle budget-bound; outer layer exposure-bound.
  - Layers are N-independent only if tie formation does not scale with N.
  - Qualification (exp 15): N = 100 is a finite-size case. From N = 100 to 200, +close falls by
    13%, +friends by 7% and all ties rise by 9%; butterflies hold 88 of 99 possible alters at
    N = 100. Independence from N = 200 to 400 still rests on one draw (exp 06).
  - This explains the N = 500 retuning in Sutcliffe et al.
- **5.4 Inverse regime (pattern 2, not used in calibration).** Source: exp 08, 09 ✅.
  **Fig. 7** (✅ draft): μ against resources per alter B̄/(N−1).
  - The N-route and the B-route collapse.
  - The sign change is near 0.5.
  - Profile ordering: butterfly < loyal_few < avoidant ≈ transactional.

### 6 Results II: dyads, history and noise (≈ 2.5 pages)
- **6.1 Isolated versus competing dyads** (mean-field). Source: exp 03, 04 ✅.
  - Isolated dyads always become friendships, the N = 2 end of the inverse regime.
  - With competition, all four outcomes appear, start-dependence is common, and
    loyal_few behaves as all-or-nothing.
  - **Rename** "embedded dyad" (Burt's *embeddedness* means the opposite), for
    example to "dyad in a competing neighbourhood".
- **6.2 Noise turns thresholds into probabilities.** Source: exp 07 ✅. **Fig. 8**
  (✅ draft): P(friendship at the end) against x0 for loyal_few, avoidant and
  transactional, with the mean-field separatrix marked.
  - The 50% point coincides with the mean-field separatrix.
  - Mean-field-stable friendships of avoidant and transactional agents break
    under noise.
- **6.3 Relationship histories.** Source: exp 07 ✅. **Table 2**: breakup-time
  scales and survival by pair, with three regimes:
  - early failure;
  - all-or-nothing;
  - slow burn then late breakup.
- **6.4 Pairing race** (🟡): cliques of concentrated agents fragment into exclusive
  pairs; the symmetric neighbourhood is unstable.
  - Criterion derived ✅: equal sharing is unstable iff β_eff(1 − x) > 1. It
    predicts 39 of 40 mean-field cliques (exp 13).
  - It is a regime of scarce budget per partner, not a generic outcome. At
    calibrated budgets, cliques of 8 stay equal even at β = 3.
  - Population-level check ✅ (exp 14).
    - The criterion holds as a gap condition: concentrated agents have a bimodal
      closeness, and x_c bounds the empty band from below.
    - Exclusive pairs need scarcity as well. They are absent at calibrated budgets
      (≤ 5%), and reach 73–74% of loyal_few agents at B × 0.3 (exp 14, exp 15).
    - Present pairing as a scarcity regime enabled by concentration, linked to
      §5.4.

### 7 Results III: asymmetry (≈ 1.5 pages) ✅
- Source: exp 12, exp 15. **Fig. 9** (✅ draft): the unreciprocated share per counterfactual, plus
  a heatmap of the unreciprocated share by ordered archetype pair.
- **About 26–27% of friendship nominations are unreciprocated** (0.257 ± 0.021 at
  N = 100, 0.271 ± 0.023 at N = 200; intervals over population draws). They are
  concentrated on nominations of partners with high reciprocity expectations
  (butterfly → transactional 0.67 ± 0.08) or fast-eroding ties (butterfly →
  avoidant 0.51 ± 0.04).
- Counterfactuals (exp 15, difference from baseline paired by draw):
  - removing the expectation gap halves the share (−0.133 ± 0.030);
  - removing the decay gap lowers it, on different pairs (−0.093 ± 0.006);
  - removing the allocation mismatch has a minor, mixed effect (−0.053 ± 0.004);
  - the individual-noise floor is 0.064 ± 0.018;
  - mean-preserving perception noise adds little (+0.017 ± 0.007).
- Comparison with Almaatouq et al. 2016 (about 0.5): the direction and order of
  magnitude agree. The model makes a *pair-level* prediction: who is left
  unreciprocated.
- The misperception confound of exp 12 is resolved (exp 15): its fall came from the bias
  in mean perception, not from the noise.

### 8 Discussion (≈ 2 pages)
- What a dynamical model adds to Tamarit:
  - histories and switching;
  - profiles;
  - the N-condition;
  - the reduced parameters.
- **Predictions for data:**
  - bimodal closeness, or a self-sustaining inner mode;
  - in small communities, people whose ties erode fastest keep a normal layer
    structure;
  - early fate of ties by profile;
  - the outer layer scales with exposure, not with N.
- **Limitations:**
  - arbitrary time unit: exp 17 finds no single mapping (close-tie turnover and contact
    frequency disagree by a factor of 70, and finer interactions trade this against time to
    friendship);
  - no turnover gradient across the close+ and friend+ layers, and a weak contact gradient
    (exp 17);
  - sensitivity to interaction granularity (exp 18): at k = 3, asymmetry, collapse,
    Proposition 2 and the inverse regime hold, exclusive pairing weakens, and relaxation is
    much slower, so this is not yet a test at stationarity;
  - the inner circle depends on the start (about 10% at k = 1, on one seed and draw);
  - absolute sizes about 3 times smaller than Dunbar's;
  - calibrated thresholds;
  - archetypes are stylised;
  - no kin;
  - encounter-only tie formation is an assumption;
  - the mean-field ignores encounters.

### 9 Conclusion (≈ 0.5 page)

### Appendices
- A. ODD (`docs/odd.md`) ✅.
- B. Calibration procedure and the failed quantile step (exp 06) ✅.
- C. Sensitivity details: factor ranges and full indices (exp 10) ✅.
- D. Mean-field equations and docking ✅ (Fig. 11).
- E. Scaling theory: Propositions 1–2 and the stability criterion
  (`docs/theory/maintenance-scaling.md`) ✅.
- Code and data availability: CoMSES deposit plus the GitHub repository (❌).

---

## 5. What is missing before submission (priority order)

| # | Item | Why | Cost |
|---|---|---|---|
| 1 | ~~Asymmetry at population level~~ ✅ done (exp 12, with the mean-preserving rerun in exp 15) | | |
| 2 | ~~Mean-field derivation of the B/δ collapse~~ ✅ done (`docs/theory/maintenance-scaling.md`, exp 13) | | |
| 3 | ~~Seeds and populations~~ ✅ done for exp 06, 11, 12 and 14 (exp 15). Not covered: exp 07, Morris, N = 400 | | |
| 4 | Figures 1–10: ✅ drafts (`docs/paper/figures/`, captions in `docs/paper/figures.md`). Fig. 5 and 9 are drawn from exp 15. Docking: Fig. 11 | | |
| 5 | ~~Pairing race at population level~~ ✅ done (exp 14): a scarcity regime, not generic | | |
| 6 | ~~Time-unit mapping~~ ✅ done (exp 17): no single mapping exists; the unit stays arbitrary. Check the primary source of the contact-frequency rule before citing it | | |
| 7 | **Sobol on the 5 levers** | optional: quantifies variance shares and interactions | about 450 runs |
| 8 | ~~Validation on tie turnover~~ ✅ done (exp 17), with a negative result: close+ and friend+ turn over at about the same rate. To be reported as a limitation | | |
| 9 | CoMSES deposit, code freeze, DOI | JASSS expects available code | admin |

## 6. Honesty checklist (things the paper must state)
- The layer ratios of about 3 are **calibrated** (the thresholds and the
  rescaling), not predicted.
- The inverse regime **is** an out-of-sample result.
- The first embedded-dyad results were contaminated by cross-clique exploration
  and were rerun (exp 04). The topology is now fixed by construction.
- The mean-field and the ABM disagree for small budgets (butterflies, exp 07). The
  mean-field gives thresholds, not probabilities.
- Single-seed Morris: only the top factors are ranked reliably.
- The calibrated model does not separate the time scales of tie formation and close-tie
  turnover (exp 17). Do not quote tie lifetimes in real time.
- The population draw explains most of the run-to-run variance (exp 15). Report intervals
  over draws; intervals over the seeds of one draw are too narrow.
- k = 1 is a choice, not a calibrated result. The k = 3 check (exp 18) matches k = 1 only
  during relaxation, and does not show that the results are invariant to k.
