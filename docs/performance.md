# Engine performance (ticket 14)

Benchmark: `python benchmarks/bench_engine.py --n 1000 --horizon 50`. The population is
25% of each built-in archetype, started from a random graph (mean degree 10) with
γ = 0.5. Measured on one core of an 8-core Linux machine, Python 3.13.

| Version | Wall-clock (N=1000, 50 time units) | Loop iterations/s |
|---|---|---|
| before (commit 8836daa) | 181.9 s | 1,099 |
| after (this ticket) | 23.4 s | 10,006 |

N = 200 over 50 time units now takes 3.7 s. The 10-seed × 2-condition layering
experiment (N = 200, 300 time units) runs in a few minutes on 6 workers.

## What changed

1. **Event channels.** Previously, every channel's rate list was rebuilt at each
   event, at a cost of O(pending invitations). Pending invitations now live in
   O(1) pools (unanswered / silent / all). Cancellation uses thinning against the
   population-wide bound max(1/τ), so the simulation stays exact.
2. **Scalar fast paths.** `forms` used to call `np.maximum` on Python floats. The
   shared forms now take a scalar branch, while the mean-field solver keeps the
   array path.
3. **Closed-form flow without deficit.** Between events, q moves monotonically
   towards 1. If q ≥ ρ* at both ends of an interval there is no erosion, and x
   decays in closed form. RK4 is used only for ties in deficit, with the default
   sub-step raised from 0.05 to 0.2 (error below 1e-6 at the default rates).
4. **One housekeeping pass.** Housekeeping no longer advances every tie twice.

Changing how cancellations are sampled changed the random-number stream, so
individual runs differ from the earlier commits. Distributions are unchanged: every
statistical test passes.

## Profile after optimisation (N = 1000)

The time now splits roughly evenly between:

- tie flow integration (`advance` / `advance_tie_flow`), dominated by the periodic
  housekeeping pass over all ~12k ties every `check_interval` = 0.25;
- circle checks (`check_tie`);
- the per-event loop (`_rate_components`, `choose_target`).

No single Python function dominates any more.

## Recommendation on a Rust port (ADR-0005)

**Not warranted yet.** At ~0.5 s per model time unit for N = 1000, a 300-unit run
takes about 2.5 minutes. A 10-seed ensemble then fits in minutes on a multi-core
machine, which is enough for the paper's planned experiments. The next steps, in
order:

1. Raise `simulation.check_interval` where circle-timing precision allows. Cost
   scales linearly with 1/check_interval.
2. Store tie state in structure-of-arrays form so that housekeeping (flow +
   circle checks) becomes one vectorised NumPy (or numba) pass.
3. Port the event loop to Rust (PyO3/maturin) behind `simulate` only if ensembles
   of N ≥ 5000 or horizons ≥ 10⁴ become necessary. The test suite pins the
   behaviour, so a port can be validated without touching experiments or metrics.
