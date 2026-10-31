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
- Overview figure (**Fig. 1**, ❌): the agent, a directed tie (x, r, o, circle),
  the invitation life cycle (accept / decline / silence / late accept / cancel),
  and the circle hysteresis with circle-dependent decay.
- Core equations: the flow of x (decay by circle, deficit erosion), the
  allocation x^β·g(q), the acceptance probability, and the cancellation hazard.
  Source: ODD §7 and spec §4–7.
- The four archetypes as behavioural profiles (**Table 1**, from ODD Table 1).
- The PDMP simulation: exact thinning, lazy flow.
- **The mean-field limit and docking with the ABM** (convergence 0.038 → 0.015 →
  0.006). This is short in the main text; the ODD gives the details. Source:
  `tests/test_09_meanfield.py`, with a dedicated docking figure (❌).
- The `exploration: ties` assumption and its justification (§5.3).
- Full ODD: Appendix A (`docs/odd.md`) ✅.

### 4 Calibration and baseline behaviour (≈ 2 pages)
- **Calibration target** (pattern 1): layer ratios ≈ 3, using the thresholds and
  the rescaled budget and decay. Say explicitly that the ratios are calibrated, not
  predicted. Source: exp 02, 06 ✅.
  - **Fig. 2** (❌): cumulative layers versus N = 100/200/400 (exp 06), with the
    per-archetype layers inset.
- Stationarity and independence of the start (pattern 3). Source: exp 01, 01b ✅.
  The empty and random starts agree within 2–6%.
- **Bimodal closeness distribution** (**Fig. 3**, 🟡: the histogram from exp 05 at
  N = 200 exists as numbers only). The self-sustaining inner circle explains why θ4
  cannot sit above the high mode (the calibration step that failed, exp 06). Present
  it as a **testable prediction** that contrasts with the monotone distribution of
  Tamarit et al. 2022.

### 5 Results I: what sets size and shape (≈ 3 pages)
- **5.1 Sensitivity screening** (Morris, 18 factors). Source: exp 10 ✅.
  **Fig. 4** (❌): μ* versus σ for the main outputs.
  - Size: B, η and δ. Shape: β. Outer layer: ν. One-sided ties: ρ*.
  - Negligible: loyalty, patience, memory, a, x0.
- **5.2 The maintenance ratio.** Source: exp 11 ✅. **Fig. 5** (❌): layer sizes
  against q for the four routes.
  - B and δ are exchangeable (R² ≥ 0.985 for every layer).
  - η deviates at the two ends, through the jump size.
  - Add the mean-field argument (❌, see §6).
- **5.3 Population size and exposure.** Source: exp 02, 05 ✅. **Fig. 6** (❌):
  outer layer versus N under baseline and tie-only exploration.
  - Inner circle budget-bound; outer layer exposure-bound.
  - Layers are N-independent only if tie formation does not scale with N.
  - This explains the N = 500 retuning in Sutcliffe et al.
- **5.4 Inverse regime (pattern 2, not used in calibration).** Source: exp 08, 09 ✅.
  **Fig. 7** (❌): μ against resources per alter B̄/(N−1).
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
  (❌): P(friendship at the end) against x0 for loyal_few, avoidant and
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
  pairs; the symmetric neighbourhood is unstable. **Needs the population-level
  check** before it can be claimed beyond cliques (❌).

### 7 Results III: asymmetry (≈ 1.5 pages) ✅
- Source: exp 12. **Fig. 9** (❌): the unreciprocated share per counterfactual, plus
  a heatmap of the unreciprocated share by ordered archetype pair.
- **About 24–28% of friendship nominations are unreciprocated.** They are
  concentrated on nominations of partners with high reciprocity expectations
  (butterfly → transactional 0.63–0.71) or fast-eroding ties (butterfly →
  avoidant 0.53).
- Counterfactuals:
  - removing the expectation gap halves the share (0.276 → 0.122);
  - removing the decay gap lowers it to 0.182, on different pairs;
  - removing the allocation mismatch has a minor, mixed effect (0.222);
  - the individual-noise floor is 0.067.
- Comparison with Almaatouq et al. 2016 (about 0.5): the direction and order of
  magnitude agree. The model makes a *pair-level* prediction: who is left
  unreciprocated.
- Follow-up: the misperception condition is confounded (perception mean > 1), so
  it needs a mean-preserving rerun.

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
  - arbitrary time unit;
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
- D. Mean-field equations and docking ✅ / 🟡 (the docking figure is missing).
- Code and data availability: CoMSES deposit plus the GitHub repository (❌).

---

## 5. What is missing before submission (priority order)

| # | Item | Why | Cost |
|---|---|---|---|
| 1 | ~~Asymmetry at population level~~ ✅ done (exp 12); a mean-preserving misperception rerun is still open | | |
| 2 | **Mean-field derivation of the B/δ collapse** (§5.2) | Gives the paper its analytical result and explains the η deviation | analytical work plus a check |
| 3 | **Seeds and populations** | Reviewers expect many more than 3–5 seeds; claims at small N need population draws | rerun exp 06, 07 and 11 with more seeds, a few hours |
| 4 | **Figures 1–8** | none exist yet; all the data does | plotting script per figure |
| 5 | **Pairing race at population level** (§6.4) | otherwise drop it or keep it as an observation | 1 experiment |
| 6 | **Time-unit mapping** (Hall 2019: hours to make a friend) | needed to compare tie lifetimes with data | modest |
| 7 | **Sobol on the 5 levers** | optional: quantifies variance shares and interactions | about 450 runs |
| 8 | **Validation pattern not used in calibration**, beyond the inverse regime: tie turnover (Roy et al. 2022; Wellman et al. 1997) | pattern-oriented validation | 1 experiment |
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
