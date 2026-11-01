"""Figures for the JASSS article (docs/paper/outline.md), from the results under results/.

    python experiments/figures.py [--only 2 5 ...] [--out docs/paper/figures]

Each figure is written as PDF (for the paper) and PNG (for review). Every figure
reads already-computed results; nothing is simulated here except Fig. 3, which
pools the closeness of the stored experiment-06 runs.

Colour: one fixed hue per profile, used in every figure. The four hues pass the
all-pairs colour-vision checks only at the 6–8 floor (CVD ΔE 6.9), so every
profile also gets its own marker and a direct label. Ordered quantities (the four
layers) use a single-hue blue ramp. Figures are static (print), so no hover layer.
"""
import argparse
import json
import math
import re
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402
from scipy import stats  # noqa: E402

R = Path("results")
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df"
PROFILE = {  # colour, marker, label
    "butterfly": ("#2a78d6", "o", "butterfly"),
    "loyal_few": ("#e34948", "s", "loyal-few"),
    "transactional": ("#1baf7a", "^", "transactional"),
    "avoidant": ("#eda100", "D", "avoidant"),
}
LAYER_RAMP = ["#0d366b", "#256abf", "#5598e7", "#86b6ef"]  # inner (darkest) → all ties
LAYERS = ["inner circle", "+ close friends", "+ friends", "all ties"]
ROUTE = {"B": ("#2a78d6", "o", "budget B × q"), "eta": ("#e34948", "s", "gain η × q"),
         "delta": ("#1baf7a", "^", "decay δ × 1/q"), "mixed": ("#eda100", "D", "mixed √q")}

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8.5, "axes.titlesize": 9, "axes.labelsize": 8.5,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.6, "axes.axisbelow": True, "legend.frameon": False, "lines.linewidth": 1.5,
    "lines.markersize": 5, "savefig.dpi": 200, "savefig.bbox": "tight", "text.color": INK,
    "axes.titleweight": "bold", "axes.titlelocation": "left",
})
FULL = 6.3  # JASSS text width, inches


def plain_log(ax, axis="y", ticks=None):
    """Log axis with plain-number tick labels."""
    from matplotlib.ticker import FixedLocator, NullFormatter, NullLocator
    a = ax.yaxis if axis == "y" else ax.xaxis
    if ticks is not None:
        a.set_major_locator(FixedLocator(ticks))
        a.set_ticklabels([f"{t:g}" for t in ticks])
    a.set_minor_locator(NullLocator())
    a.set_minor_formatter(NullFormatter())


def prof(name):
    return PROFILE[name.replace("_c", "")]


def save(fig, out, name):
    out.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(out / f"{name}.{ext}")
    plt.close(fig)
    print("wrote", out / name)


def ci_err(c):
    m = c["mean"]
    lo, hi = c["ci"]
    if not (np.isfinite(lo) and np.isfinite(hi)):
        return m, 0.0, 0.0
    return m, m - lo, hi - m


def wilson(k, n, z=1.96):
    if n == 0:
        return np.nan, np.nan, np.nan
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, p - (c - h), (c + h) - p


def label_end(ax, x, y, text, color=INK2, dx=4, dy=0, ha="left"):
    ax.annotate(text, (x, y), xytext=(dx, dy), textcoords="offset points", va="center", ha=ha,
                fontsize=7.5, color=color)


# ------------------------------------------------------------------- Fig. 1
def fig1(out):
    fig = plt.figure(figsize=(FULL, 4.6))
    gsp = fig.add_gridspec(2, 2, height_ratios=[1, 1.15], width_ratios=[1, 1.1], hspace=0.35, wspace=0.25)
    ax_a, ax_c, ax_b = fig.add_subplot(gsp[0, 0]), fig.add_subplot(gsp[0, 1]), fig.add_subplot(gsp[1, :])
    for ax in (ax_a, ax_b):
        ax.set_axis_off()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

    def box(ax, x, y, w, h, text, fc="#f4f3f0", ec=MUTED, size=7.2):
        ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.01,rounding_size=0.02",
                                    fc=fc, ec=ec, lw=0.8))
        ax.text(x, y, text, ha="center", va="center", fontsize=size, color=INK)

    def arrow(ax, a, b, text=None, rad=0.0, tx=None, ha="center"):
        ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=8, lw=0.9, color=INK2,
                                     connectionstyle=f"arc3,rad={rad}", shrinkA=1, shrinkB=1))
        if text:
            x, y = tx if tx else ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            ax.text(x, y, text, fontsize=6.6, color=INK2, ha=ha, va="center")

    # (a) agents and directed ties
    ax = ax_a
    ax.set_title("a  Agents and directed ties")
    box(ax, 0.15, 0.55, 0.28, 0.62, "agent i\n\nB  β  ε  δ_c\nρ*  κ  λ\nw  m  ν\nπ  τ  ℓ  α", size=6.8)
    box(ax, 0.85, 0.55, 0.28, 0.62, "agent j\n\nown\nparameters", size=6.8)
    arrow(ax, (0.3, 0.68), (0.7, 0.68), "x_ij, r_ij, o_ij, c_ij", tx=(0.5, 0.76))
    arrow(ax, (0.7, 0.42), (0.3, 0.42), "x_ji, r_ji, o_ji, c_ji", tx=(0.5, 0.34))
    ax.text(0.5, 0.05, "each side holds its own view of the tie (x_ij ≠ x_ji)", ha="center", fontsize=6.8,
            color=INK2)

    # (c) circles
    ax = ax_c
    ax.set_title("b  Circles, hysteresis and decay")
    th = [0.31, 0.60, 0.82]
    dl = [0.024, 0.0169, 0.0115, 0.0068]
    edges = [0.0, *th, 1.0]
    names = ["acquaint.", "friend", "close", "inner"]
    for k in range(4):
        ax.barh(0.45, edges[k + 1] - edges[k], left=edges[k], height=0.42, color=LAYER_RAMP[3 - k], ec="white",
                lw=1.5)
        ax.text((edges[k] + edges[k + 1]) / 2, 0.45, names[k], ha="center", va="center", fontsize=6.6,
                color="white" if k >= 1 else INK)
        ax.text((edges[k] + edges[k + 1]) / 2, 0.12, f"δ={dl[k]:g}", ha="center", va="center", fontsize=6.2,
                color=INK2)
    for t in th:
        ax.add_patch(plt.Rectangle((t - 0.025, 0.67), 0.05, 0.09, color=MUTED, lw=0))
    ax.text(0.5, 0.88, "grey: hysteresis band (promote at θ + w/2, demote at θ − w/2)", ha="center", fontsize=6.4,
            color=INK2)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)
    ax.set_yticks([])
    ax.set_xticks([0, *th, 1], ["0", *[f"{t:g}" for t in th], "1"])
    ax.set_xlabel("closeness x  (decay rate per circle below)")
    ax.grid(False)
    ax.spines["left"].set_visible(False)

    # (b) invitation life cycle
    ax = ax_b
    ax.set_title("c  Invitation life cycle (i invites j)")
    box(ax, 0.08, 0.6, 0.13, 0.2, "issue\nrate γ·F_i")
    box(ax, 0.33, 0.6, 0.15, 0.2, "pending\nholds c_wait")
    box(ax, 0.66, 0.88, 0.23, 0.19, "accepted (both sides)\nx += η(1 − x)\nr, o updated", fc="#e6f0fb")
    box(ax, 0.66, 0.6, 0.2, 0.17, "declined\ni: o += c_rej")
    box(ax, 0.33, 0.2, 0.15, 0.17, "silent")
    box(ax, 0.66, 0.2, 0.2, 0.17, "cancelled\ni: r drops")
    arrow(ax, (0.145, 0.6), (0.255, 0.6))
    arrow(ax, (0.405, 0.66), (0.56, 0.86), "ω·P_acc", tx=(0.45, 0.82))
    arrow(ax, (0.405, 0.6), (0.56, 0.6), "ω(1−P)(1−α)", tx=(0.483, 0.55))
    arrow(ax, (0.33, 0.5), (0.33, 0.285), "ω(1−P)α", tx=(0.34, 0.39), ha="left")
    arrow(ax, (0.405, 0.24), (0.6, 0.785), "ζ·P (late)", rad=0.35, tx=(0.565, 0.4), ha="left")
    arrow(ax, (0.405, 0.18), (0.56, 0.18), "hazard 1/T_ij", tx=(0.483, 0.11))
    ax.text(0.79, 0.45, "P = P_acc = σ(a0 + a·x_ji + b·g(q_ji) − c·U_j/B_j)\n"
                        "g(q) = q/(q + ρ*),  q = (r + o0)/(o + o0)\n"
                        "T_ij = τ_i (1 + h1·x_ij)\n"
                        "target: ∝ x^β·g(q), or a random tie (prob. ε)\n\n"
                        "between events:\n"
                        "dx/dt = −δ_c x − κ(1 − ℓx)·max(0, ρ* − q)·x",
            fontsize=6.4, color=INK2, va="center", ha="left", family="DejaVu Sans")
    save(fig, out, "fig1_model")


# ------------------------------------------------------------------- Fig. 2
def fig2(out):
    a = json.loads((R / "dunbar_calibrated_scaling/analysis.json").read_text())
    Ns = [100, 200, 400]
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(FULL, 2.7), gridspec_kw={"width_ratios": [1, 1.25]})
    for k in range(4):
        cs = [a["layering"]["conditions"][f"n{n}"]["layer_sizes"][k] for n in Ns]
        m, lo, hi = zip(*[ci_err(c) for c in cs])
        ax.errorbar(Ns, m, yerr=[lo, hi], color=LAYER_RAMP[k], marker="o", capsize=2, lw=1.5)
        label_end(ax, Ns[-1], m[-1], f"{['inner', '+close', '+friends', 'all'][k]}  {m[-1]:.3g}")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xticks(Ns, [str(n) for n in Ns])
    ax.minorticks_off()
    ax.set_xlim(85, 900)
    plain_log(ax, "y", [2, 5, 10, 20, 50])
    ax.set_xlabel("population size N")
    ax.set_ylabel("cumulative layer size (per agent)")
    ax.set_title("a  Layers do not depend on N")

    groups = ["butterfly_c", "loyal_few_c", "transactional_c", "avoidant_c"]
    byc = a["layering_by_archetype"]["conditions"]["n200"]
    x = np.arange(4)
    for gi, g in enumerate(groups):
        col, mk, lab = prof(g)
        m, lo, hi = zip(*[ci_err(c) for c in byc[g]["layer_sizes"]])
        bx.errorbar(x + (gi - 1.5) * 0.15, m, yerr=[lo, hi], fmt=mk, color=col, ms=5, capsize=1.5, label=lab,
                    mec="white", mew=0.6)
    bx.set_yscale("log")
    plain_log(bx, "y", [1, 2, 5, 10, 20, 50, 100])
    bx.set_xticks(x, ["inner", "+close", "+friends", "all"])
    bx.set_ylabel("cumulative layer size")
    bx.set_title("b  By profile (N = 200)")
    bx.legend(ncol=2, fontsize=7, loc="upper left")
    save(fig, out, "fig2_layering")


# ------------------------------------------------------------------- Fig. 3
def fig3(out):
    from asym.result import SimulationResult
    run_dir = R / "dunbar_calibrated_scaling/n200"
    files = sorted(run_dir.glob("seed_*.npz"))
    bins = np.linspace(0, 1, 41)
    pooled = defaultdict(lambda: np.zeros(len(bins) - 1))
    for f in files:
        res = SimulationResult.load(f)
        arch = {a["id"]: a.get("archetype") for a in res.config.get("agents", [])}
        g = np.array([arch.get(a) for a in res.agent_ids])
        T = res.ties
        ego = g[T["i"].astype(int)]
        for name in PROFILE:
            pooled[name] += np.histogram(T["x"][ego == f"{name}_c"], bins)[0]
        pooled["all"] += np.histogram(T["x"], bins)[0]
    th = [0.31, 0.60, 0.82]
    c = 0.5 * (bins[1:] + bins[:-1])
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(FULL, 2.5), sharex=True)
    d = pooled["all"] / pooled["all"].sum() / (bins[1] - bins[0])
    ax.bar(c, d, width=bins[1] - bins[0], color=LAYER_RAMP[1], ec="white", lw=0.8)
    ax.set_yscale("log")
    ax.set_ylabel("density (log)")
    ax.set_title("a  All ties (N = 200, 3 seeds)")
    for b_ in (ax, bx):
        for t in th:
            b_.axvline(t, color=MUTED, lw=0.8, ls=(0, (3, 2)))
    for t, nm in zip(th, ["friend", "close", "inner"]):
        ax.text(t + 0.01, ax.get_ylim()[1] * 0.6, nm, fontsize=6.8, color=INK2)
    for name, (col, mk, lab) in PROFILE.items():
        h = pooled[name]
        dd = h / h.sum() / (bins[1] - bins[0])
        bx.plot(c, dd, color=col, marker=mk, ms=3, lw=1.3, label=lab, mec="white", mew=0.4)
    bx.set_yscale("log")
    bx.set_title("b  By profile of the ego")
    bx.legend(fontsize=7, loc="lower left")
    for b_ in (ax, bx):
        b_.set_xlabel("closeness x")
    save(fig, out, "fig3_bimodal")


# ------------------------------------------------------------------- Fig. 4
def fig4(out):
    m = json.loads((R / "morris/indices.json").read_text())
    fac = m["factors"]
    outs = {"inner": "inner circle", "all": "all ties", "mu": "layer exponent μ", "one-sided": "one-sided ties"}
    from matplotlib.ticker import MaxNLocator
    fig, axes = plt.subplots(1, 4, figsize=(FULL, 2.3), gridspec_kw={"wspace": 0.45})
    for ax, (key, title) in zip(axes, outs.items()):
        ax.xaxis.set_major_locator(MaxNLocator(3))
        ax.yaxis.set_major_locator(MaxNLocator(4))
        o = m["outputs"].index(key)
        ms = np.array([row[o] for row in m["mu_star"]], float)
        sg = np.array([row[o] for row in m["sigma"]], float)
        ax.scatter(ms, sg, s=14, color=LAYER_RAMP[1], ec="white", lw=0.5, zorder=3)
        top = np.argsort(-ms)[:4]
        for k in top:
            short = fac[k].split()[-1]
            ax.annotate(short, (ms[k], sg[k]), xytext=(3, 2), textcoords="offset points", fontsize=7, color=INK)
        lim = max(ms.max(), sg.max()) * 1.15
        ax.plot([0, lim], [0, lim], color=MUTED, lw=0.7, ls=(0, (3, 2)))
        ax.set_xlim(0, lim)
        ax.set_ylim(0, lim)
        ax.set_title(title, fontsize=8)
        ax.set_xlabel("μ* (importance)")
    axes[0].set_ylabel("σ (non-linearity)")
    fig.suptitle("Morris screening, 18 factors, r = 10 trajectories (dashed: σ = μ*)", x=0.01, ha="left",
                 fontsize=8.5, color=INK2, y=1.04)
    save(fig, out, "fig4_morris")


# ------------------------------------------------------------------- Fig. 5
def _collapse_rows():
    rob = R / "15_robustness/runs.jsonl"
    rows = []
    if rob.exists():
        rows = [json.loads(line) for line in rob.read_text().splitlines() if line.strip()]
        rows = [r for r in rows if r["block"] == "collapse"]
        for r in rows:
            r["L"] = r["layers"]
    if len({(r["q"], r["route"]) for r in rows}) < 17:
        rows = json.loads((R / "11_maintenance_collapse.json").read_text())
    return rows


def fig5(out):
    rows = _collapse_rows()
    QS = sorted({r["q"] for r in rows})
    n_runs = len(rows)
    fig, axes = plt.subplots(1, 4, figsize=(FULL, 2.4), gridspec_kw={"wspace": 0.4})
    outs = [(0, "inner circle"), (2, "+ friends"), (3, "all ties"), ("mu", "layer exponent μ")]
    for ax, (k, title) in zip(axes, outs):
        for route, (col, mk, lab) in ROUTE.items():
            ys, es = [], []
            for q in QS:
                v = [(r["mu"] if k == "mu" else r["L"][k]) for r in rows
                     if abs(r["q"] - q) < 1e-9 and (r["route"] == route or abs(q - 1) < 1e-9)]
                ys.append(np.mean(v))
                es.append((np.mean(v) - np.min(v), np.max(v) - np.mean(v)))
            ax.errorbar(QS, ys, yerr=np.array(es).T, color=col, marker=mk, ms=4, capsize=1.5, lw=1.3, label=lab, mec="white",
                        mew=0.5)
        ax.set_xscale("log", base=2)
        ax.set_xticks([0.5, 1, 2], ["½", "1", "2"])
        ax.minorticks_off()
        if k != "mu":
            ax.set_yscale("log")
            plain_log(ax, "y", {0: [0.5, 1, 2, 5, 10], 2: [5, 10, 20, 30], 3: [20, 30, 40, 50]}[k])
        ax.set_title(title, fontsize=8)
        ax.set_xlabel("q  (Q = ηB/δ × q)")
    axes[0].set_ylabel("per agent")
    axes[0].legend(fontsize=6.6, loc="upper left")
    fig.suptitle(f"Maintenance collapse: four routes to the same Q ({n_runs} runs; bars: range over runs)",
                 x=0.01, ha="left", fontsize=8.5, color=INK2, y=1.04)
    save(fig, out, "fig5_collapse")


# ------------------------------------------------------------------- Fig. 6
def fig6(out):
    base = json.loads((R / "calibrated_layering_scaling/analysis.json").read_text())["layering"]["conditions"]
    ties = json.loads((R / "tie_exploration_scaling/analysis.json").read_text())["layering"]["conditions"]
    Ns = [100, 200, 400]
    fig, axes = plt.subplots(1, 2, figsize=(FULL, 2.5))
    modes = [("exploration to any agent", base, "#e34948", "s"), ("exploration to existing ties only", ties,
                                                                    "#2a78d6", "o")]
    for ax, (k, title) in zip(axes, [(0, "a  Inner circle: budget-bound"), (3, "b  All ties: exposure-bound")]):
        for lab, cond, col, mk in modes:
            m, lo, hi = zip(*[ci_err(cond[f"n{n}"]["layer_sizes"][k]) for n in Ns])
            ax.errorbar(Ns, m, yerr=[lo, hi], color=col, marker=mk, capsize=2, label=lab, mec="white", mew=0.5)
        ax.set_xscale("log")
        ax.set_xticks(Ns, [str(n) for n in Ns])
        ax.minorticks_off()
        ax.set_xlabel("population size N")
        ax.set_title(title)
        ax.set_ylim(bottom=0)
    axes[0].set_ylabel("per agent")
    axes[1].legend(fontsize=7, loc="upper left")
    save(fig, out, "fig6_exposure")


# ------------------------------------------------------------------- Fig. 7
def fig7(out):
    a = json.loads((R / "inverse_regime/analysis.json").read_text())["layer_regime"]["conditions"]
    Bbar = np.mean([20.0, 10.0, 12.5, 12.5])
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(FULL, 2.6), gridspec_kw={"wspace": 0.3})
    npts, bpts = [], []
    for cond, v in a.items():
        n = int(re.match(r"n(\d+)", cond).group(1))
        mult = {"B0p5x": 0.5, "B2x": 2.0, "B4x": 4.0}.get(cond.split("_")[1] if "_" in cond else "", 1.0)
        x = Bbar * mult / (n - 1)
        (bpts if "_" in cond else npts).append((x, *ci_err(v["mu"])))
        if cond == "n48":
            bpts.append((x, *ci_err(v["mu"])))
    for pts, lab, col, mk in [(sorted(npts), "N varies (B fixed)", "#2a78d6", "o"),
                              (sorted(bpts), "B varies (N = 48)", "#e34948", "s")]:
        x, m, lo, hi = zip(*pts)
        ax.errorbar(x, m, yerr=[lo, hi], color=col, marker=mk, capsize=2, lw=1.3, label=lab,
                    mec="white", mew=0.5)
    ax.axhline(0, color=INK2, lw=0.8)
    ax.axvline(0.5, color=MUTED, lw=0.8, ls=(0, (3, 2)))
    ax.set_xscale("log")
    plain_log(ax, "x", [0.15, 0.3, 0.5, 1, 2])
    ax.set_xlabel("resources per alter  B̄ / (N − 1)")
    ax.set_ylabel("layer exponent μ")
    ax.set_title("a  μ changes sign near 0.5")
    ax.legend(fontsize=7, loc="upper right")

    p = json.loads((R / "inverse_regime_populations/analysis.json").read_text())["layer_regime"]["conditions"]
    by = defaultdict(lambda: defaultdict(list))
    for cond, v in p.items():
        n = int(re.match(r"n(\d+)_p\d+", cond).group(1))
        for g, d in v["by_archetype"].items():
            if np.isfinite(d["mu"]["mean"]):
                by[g][n].append(d["mu"]["mean"])
    for g in ["butterfly_c", "loyal_few_c", "transactional_c", "avoidant_c"]:
        col, mk, lab = prof(g)
        ns = sorted(by[g])
        m = [np.mean(by[g][n]) for n in ns]
        e = [stats.t.ppf(0.975, len(by[g][n]) - 1) * np.std(by[g][n], ddof=1) / math.sqrt(len(by[g][n]))
             if len(by[g][n]) > 1 else 0 for n in ns]
        bx.errorbar(ns, m, yerr=e, color=col, marker=mk, capsize=1.5, lw=1.3, ms=4, mec="white", mew=0.5,
                    label=lab)
    bx.axhline(0, color=INK2, lw=0.8)
    bx.set_xscale("log")
    bx.set_xticks([12, 16, 24, 48, 100], ["12", "16", "24", "48", "100"])
    bx.minorticks_off()
    bx.set_xlabel("population size N")
    bx.set_title("b  By profile (5 draws)")
    bx.legend(fontsize=7, loc="lower right")
    save(fig, out, "fig7_inverse_regime")


# ------------------------------------------------------------------- Fig. 8
def fig8(out):
    j = json.loads((R / "07_stochastic_switching.json").read_text())
    fig, axes = plt.subplots(1, 3, figsize=(FULL, 2.3), sharey=True)
    for ax, name in zip(axes, ["loyal_few", "avoidant", "transactional"]):
        col, mk, lab = PROFILE[name]
        rs = [r for r in j["runs"] if r["pair"] == [name, name]]
        xs = sorted({r["x0"] for r in rs})
        pts = [wilson(sum(r["final"] == "high" for r in rs if r["x0"] == x), sum(r["x0"] == x for r in rs)) for x in xs]
        p, lo, hi = zip(*pts)
        ax.errorbar(xs, p, yerr=[lo, hi], color=col, marker=mk, capsize=2, lw=1.4, mec="white", mew=0.5)
        mf = j["mf"][f"{name}-{name}"]
        mx = sorted((float(k), v) for k, v in mf.items())
        hi_x = [x for x, v in mx if v >= 0.31]
        if hi_x:
            first = hi_x[0]
            prev = max([x for x, _ in mx if x < first], default=first)
            sep = 0.5 * (first + prev)
            ax.axvline(sep, color=INK2, lw=0.9, ls=(0, (3, 2)))
            ax.text(sep + 0.01, 0.06, "mean-field\nseparatrix", fontsize=6.6, color=INK2)
        ax.axhline(0.5, color=GRID, lw=0.8)
        ax.set_title(lab, fontsize=8.5)
        ax.set_xlabel("initial closeness x0")
        ax.set_ylim(-0.03, 1.03)
    axes[0].set_ylabel("P(friendship at the end)")
    fig.suptitle("Dyad in a competing neighbourhood: noise turns the threshold into a probability "
                 "(40 runs per point, Wilson 95% CI)", x=0.01, ha="left", fontsize=8.5, color=INK2, y=1.04)
    save(fig, out, "fig8_switching")


# ------------------------------------------------------------------- Fig. 9
def fig9(out):
    a = json.loads((R / "asymmetry_mechanisms/analysis.json").read_text())["asymmetry"]["conditions"]
    rob = R / "15_robustness/runs.jsonl"
    order = [("baseline", "baseline"), ("no_deficit", "no expectation gap"), ("same_decay", "no decay gap"),
             ("same_allocation", "no budget/β gap"), ("misperception", "+ perception noise*"),
             ("average_only", "no profiles (noise only)")]
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(FULL, 2.8), gridspec_kw={"width_ratios": [1.2, 1], "wspace": 0.75})
    y = np.arange(len(order))[::-1]
    for yi, (key, lab) in zip(y, order):
        m, lo, hi = ci_err(a[key]["unreciprocated"])
        ax.barh(yi, m, height=0.55, color=LAYER_RAMP[1] if key == "baseline" else "#86b6ef", ec="white")
        ax.errorbar(m, yi, xerr=[[lo], [hi]], color=INK, capsize=2, lw=0.9)
        ax.text(m + hi + 0.008, yi, f"{m:.2f}", va="center", fontsize=7, color=INK)
    ax.set_yticks(y, [lab for _, lab in order])
    ax.set_xlabel("share of friendship nominations not reciprocated")
    ax.set_title("a  Counterfactuals (N = 100, 5 seeds)")
    ax.grid(axis="y", visible=False)
    ax.set_xlim(0, 0.36)
    ax.text(0, -0.32, "* biased: raises perceived reciprocity on average", transform=ax.transAxes, fontsize=6.4,
            color=INK2)

    gs = ["butterfly_c", "loyal_few_c", "transactional_c", "avoidant_c"]
    M = np.full((4, 4), np.nan)
    for i, gi in enumerate(gs):
        for k, gk in enumerate(gs):
            d = a["baseline"]["by_pair"].get(f"{gi}->{gk}")
            if d:
                M[i, k] = d["unreciprocated"]["mean"]
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("blue", ["#f0f6fd", "#86b6ef", "#256abf", "#0d366b"])
    im = bx.imshow(M, cmap=cmap, vmin=0, vmax=0.8)
    for i in range(4):
        for k in range(4):
            if np.isfinite(M[i, k]):
                bx.text(k, i, f"{M[i, k]:.2f}", ha="center", va="center", fontsize=7,
                        color="white" if M[i, k] > 0.45 else INK)
    labels = [prof(g)[2] for g in gs]
    bx.set_xticks(range(4), labels, rotation=30, ha="right")
    bx.set_yticks(range(4), labels)
    bx.set_xlabel("nominated (alter)")
    bx.set_ylabel("nominating (ego)", labelpad=2)
    bx.grid(False)
    bx.set_title("b  Not reciprocated, by pair")
    cb = fig.colorbar(im, ax=bx, fraction=0.046, pad=0.04)
    cb.outline.set_visible(False)
    cb.ax.tick_params(labelsize=6.5)
    save(fig, out, "fig9_asymmetry")


# ------------------------------------------------------------------ Fig. 10
def fig10(out):
    abm = json.loads((R / "13_scaling_theory/abm.json").read_text())
    p14 = json.loads((R / "14_pairing_population.json").read_text())
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(FULL, 2.6), gridspec_kw={"wspace": 0.35})
    bins = [0.2, 0.35, 0.5, 0.65, 0.8, 0.95]
    centres = [0.5 * (a + b) for a, b in zip(bins, bins[1:])]
    for route, (col, mk, lab) in [("B", ROUTE["B"]), ("eta", ROUTE["eta"]), ("delta", ROUTE["delta"])]:
        lab = {"B": "budget B × 2", "eta": "gain η × 2", "delta": "decay δ / 2"}[route]
        m = np.concatenate([r["mean"] for r in abm if r["route"] == route])
        v = np.concatenate([r["var"] for r in abm if r["route"] == route])
        ys = []
        for lo, hi in zip(bins, bins[1:]):
            k = (m >= lo) & (m < hi)
            ys.append(np.median(v[k] / (m[k] * (1 - m[k]) ** 2)) if k.sum() >= 5 else np.nan)
        ax.plot(centres, ys, color=col, marker=mk, label=lab, mec="white", mew=0.5)
    ax.set_xlabel("mean closeness of the tie")
    ax.set_ylabel("Var x / [x (1 − x)²]")
    ax.set_title("a  Tie noise at q = 2")
    ax.legend(fontsize=7, loc="upper left")
    ax.set_ylim(bottom=0)

    hom = [r for r in p14 if r["kind"] == "homogeneous" and r["b_mult"] == 1.0]
    edges = np.linspace(0, 1, 51)
    c = 0.5 * (edges[1:] + edges[:-1])
    ramp = ["#86b6ef", "#5598e7", "#256abf", "#184f95", "#0d366b"]
    for b, col in zip([0.5, 1.0, 1.5, 2.0, 3.0], ramp):
        h = np.mean([r["hist"] for r in hom if r["beta"] == b], axis=0)
        h = np.where(h > 0, h, np.nan)
        bx.plot(c, h / (edges[1] - edges[0]), color=col, lw=1.3, label=f"β = {b:g}")
        be = 0.95 * b
        if be > 1:
            xc = 1 - 1 / be
            bx.plot([xc], [3e-3], marker="v", color=col, ms=6, clip_on=False)
    bx.set_yscale("log")
    bx.set_ylim(2e-3, 50)
    bx.set_xlim(0, 1)
    bx.legend(fontsize=6.6, loc="upper center", ncol=3)
    plain_log(bx, "y", [0.01, 0.1, 1, 10])
    bx.set_xlabel("closeness x")
    bx.set_ylabel("density (log)")
    bx.set_title("b  Gap above x_c (▼), B = 12.5")
    save(fig, out, "fig10_theory")


# ------------------------------------------------------------------ Fig. 11
def fig11(out):
    d = json.loads((R / "16_docking.json").read_text())
    fig, axes = plt.subplots(1, 3, figsize=(FULL, 2.4), gridspec_kw={"wspace": 0.38, "width_ratios": [1, 1, 1.15]})
    dirs = [("ab", "#2a78d6", "a → b"), ("ba", "#e34948", "b → a")]
    for ax, sc in zip(axes[:2], (1, 16)):
        row = next(r for r in d if r["regime"] == "sustained" and r["s"] == sc)
        t = np.array(row["t"])
        for key, col, lab in dirs:
            m, sd = np.array(row[f"abm_mean_{key}"]), np.array(row[f"abm_sd_{key}"])
            ax.fill_between(t, m - sd, m + sd, color=col, alpha=0.15, lw=0)
            ax.plot(t, m, color=col, lw=1.5, label=f"ABM mean ± SD, {lab}")
            ax.plot(t, row[f"mf_{key}"], color=INK, lw=1.0, ls=(0, (3, 2)))
        ax.set_title(f"{'a' if sc == 1 else 'b'}  scale s = {sc}")
        ax.set_xlabel("time")
        ax.set_ylim(0, 1)
    axes[0].set_ylabel("closeness x")
    axes[0].plot([], [], color=INK, lw=1.0, ls=(0, (3, 2)), label="mean-field")
    axes[0].legend(fontsize=6.2, loc="lower left")

    ax = axes[2]
    for regime, mk, col in (("sustained", "o", "#2a78d6"), ("decaying", "s", "#e34948")):
        rows = sorted((r for r in d if r["regime"] == regime), key=lambda r: r["s"])
        ss = np.array([r["s"] for r in rows])
        ax.plot(ss, [r["max_error"] for r in rows], color=col, marker=mk, label=f"max |ABM mean − MF|, {regime}",
                mec="white", mew=0.5)
        ax.plot(ss, [np.mean(r["abm_sd_ab"]) for r in rows], color=col, marker=mk, ls=(0, (1, 1.5)), lw=1.2,
                mfc="white", label=f"ABM SD (time mean), {regime}")
    ss = np.array([1, 64])
    floor = [r["sampling_floor"] for r in d if r["regime"] == "sustained"]
    ax.plot(ss, 0.09 * ss ** -0.5, color=MUTED, lw=0.8)
    ax.text(1.1, 0.1, "∝ s^−1/2", fontsize=6.6, color=INK2)
    ax.fill_between(sorted({r["s"] for r in d}), 0, floor, color=GRID, lw=0, label="sampling floor (n = 200)")
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    plain_log(ax, "y", [0.001, 0.003, 0.01, 0.03, 0.1])
    ax.set_xticks([1, 4, 16, 64], ["1", "4", "16", "64"])
    ax.set_ylim(8e-4, 0.15)
    ax.set_xlabel("scale s (budget × s, jumps / s)")
    ax.set_title("c  Convergence")
    h, l = ax.get_legend_handles_labels()
    fig.legend(h, l, fontsize=6.6, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.2))
    save(fig, out, "fig11_docking")


FIGS = {1: fig1, 2: fig2, 3: fig3, 4: fig4, 5: fig5, 6: fig6, 7: fig7, 8: fig8, 9: fig9, 10: fig10, 11: fig11}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", type=int, nargs="+", default=list(FIGS))
    ap.add_argument("--out", default="docs/paper/figures")
    a = ap.parse_args()
    for k in a.only:
        FIGS[k](Path(a.out))


if __name__ == "__main__":
    main()
