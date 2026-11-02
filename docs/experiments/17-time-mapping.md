# Experiment 17: mapping the model time unit to real time

Script: `experiments/17_time_mapping.py`. Report: `results/17_time_mapping.md`; raw
results: `results/17_time_mapping*.json`. Neither is versioned.

**Conclusion: the calibrated model has no single conversion to real time.** The time
unit stays arbitrary (ADR-0006), and the paper should not quote tie lifetimes in real
time.

## Question

Each empirical anchor below gives its own number of model units per week. If they agreed,
the mapping would be credible. All measures come from the calibrated population of exp 06
(N = 100, random start as in exp 10, window 300–700, one population draw, 2 seeds).

## Anchors and the status of their sources

| anchor | empirical value | source | status |
|---|---|---|---|
| contact, 5-layer | at least weekly | Sutcliffe et al. 2012, via Dunbar | **secondary sources only**; check the primary before citing |
| contact, 15-layer | at least monthly | same | same |
| turnover, inner layers | 1–4% of alters per year; 2% used | Roy et al. 2022, *Sci. Rep.* 12:11018 | verified in the text |
| turnover, outer layers | ≤ 30% per year | none | **a convention, and an upper bound** |
| hours to friendship | about 50 h to casual friend, 90 h to friend, more than 200 h to close friend | Hall 2019, via the University of Kansas summary | verified in that summary, not in the paper; it does not state clearly whether the figures are cumulative |
| time to friendship | within the first 9 weeks of college | Hall 2019, study 2 | the design covers 9 weeks (2 + 7), which limits what it can show |
| liability of newness | 9 in 10 bridges gone the next year | Burt 2002 | verified in the literature review; weak anchor, since bridges among colleagues are not new acquaintances |

The script earlier credited the 30% to Saramäki et al. 2014 and Kempnich et al. 2024.
Neither supports it as an annual rate in what could be consulted. Saramäki et al. follow
a life transition, with a Jaccard index of 0.36–0.44 between intervals for the top 20
alters, and the available summaries of Kempnich et al. give no such rate. The "one member
of the 5-layer per decade" rule reached us only through the press, so Roy et al. replaces
it.

The earlier report averaged the anchors to 1.28 units per week. That average has been
removed: an upper bound cannot be averaged with point values.

## Results at the calibrated point (k = 1)

| anchor | units per week |
|---|---|
| contact, weekly (close+) | 5.88 |
| contact, monthly (friend+) | 2.87 |
| turnover 2% per year (close+) | 0.08 (0.04–0.17 for 1–4%) |
| turnover ≤ 30% per year (friend+) | ≤ 1.90 |

- **The contact and turnover anchors disagree by a factor of 70 for close ties.** At the
  contact mapping, 76% of close+ ties would be lost per year, against 1–4% in the data.
- **The hours are impossible.** With Hall's 90 h over a median of 7 interactions, one
  interaction lasts 12.9 h, and an agent would spend 472 h per week socialising. A week
  has 168 h.
- **Time to friendship agrees:** 52 units gives 9 weeks at the contact mapping. This
  agreement is at the edge of what Hall's design could observe, so it is weak.

## Does interaction granularity explain the mismatch?

A model interaction may stand for many real contacts. Setting B × k with η, the
investment unit and the cancellation drop / k makes interactions finer at the same
Q = ηB/δ (Proposition 1).

| k | layers | mismatch, contact vs close+ turnover | close+ loss per year at contact mapping | hours per interaction | social h/week | weeks to friend at contact mapping |
|---|---|---|---|---|---|---|
| 1 | 2.0 / 6.1 / 15.7 / 40.2 | 70× | 76% | 12.9 | 472 | 9 |
| 3 | 1.3 / 4.7 / 15.1 / 49.2 | 9× | 17% | 2.4 | 86 | 72 |
| 6 | 1.0 / 4.5 / 14.5 / 53.4 | 3× | 7% | 1.0 | 37 | 163 |

- **Granularity explains most of the turnover and hours problems.** At k = 6, an
  interaction lasts about an hour, social time is possible, and turnover nears the data.
  This fits Proposition 2: a smaller η means less noise, and so fewer threshold crossings.
- **It worsens time to friendship.** Friendship takes 88 interactions and more than three
  years at k = 6, against 9 weeks at k = 1. Formation and turnover pull k in opposite
  directions.
- **It is not the calibrated model.** At the same Q the inner circle halves and the total
  rises by a third, as Proposition 2 predicts: less noise means thinner tails. The k > 1
  rows would need recalibrating before they could be compared with the data as results.

**Correction from exp 18:** the k > 1 rows were measured over 300–700, while the model is
still relaxing. Their layers, and so the comparison with Proposition 2 above, are partly
transient. A later window, at a recalibrated k = 3, gives similar time measures (7×, 13%,
77 h, 71 weeks). k = 6 was not rechecked. See `18-k3-sensitivity.md`.

## Unit-free checks

These do not depend on any mapping, so they test the model directly. Both are weak
points that hold across k:

- **Contact gradient:** the ratio of minimum contact rates between close+ and friend+ is
  1.9–2.1, against 4.35 for weekly versus monthly.
- **Turnover gradient:** the loss hazard of close+ relative to friend+ is 0.9–1.3, so the
  two layers turn over at about the same rate. In the data, close ties are the more stable
  (Roy et al. 2022), and turnover is largest among lower-ranking alters (Saramäki et al.
  2014). The friend+ layer contains the close+ ties, which narrows the measured contrast,
  so this comparison understates any true gradient. The inner circle alone does retain
  more than close+ (0.85 vs 0.80 over 50 units at k = 1).

New ties do show a liability of newness: 79–82% are gone within 200 units, with a median
lifetime of 65 units at k = 1. This corrects an earlier 26%, caused by a bug that counted
re-created ties as surviving forever.

## Consequences for the paper

- Keep the arbitrary unit, and report dimensionless results.
- State the mismatch as a limitation: the calibrated model does not separate the time
  scales of tie formation (weeks) and close-tie turnover (decades).
- Item 8 of the outline (validation on turnover) has a negative result to report: the model
  does not reproduce the turnover gradient across layers at these settings.

## Limits

- One population draw and 2 seeds at N = 100. Exp 15 shows that the draw matters, so the
  values above are indicative. The factor-of-ten contrasts are far larger than that spread.
- "Minimum contact" read as the 10th percentile is a choice.
- Retention over 50 units counts a tie that left and returned as retained.
- k above 6 was not run: the event log would approach the 3.5 GB memory cap.
- Runs: 2 min at k = 1, 6 min at k = 3, 12 min at k = 6, with one worker; peak memory
  0.5, 1.2 and 2.1 GB.
