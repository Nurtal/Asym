"""Shared functional forms of the model (docs/model-spec.md §4–7).

Both the PDMP engine and the mean-field solver use these functions, so the two
levels of description cannot drift apart. They work on Python floats and on NumPy
arrays alike.
"""
from __future__ import annotations

import math

import numpy as np


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def reciprocity_ratio(r, o, o0):
    """q = (r + o0) / (o + o0): perceived return on own investment, with a neutral prior."""
    return (r + o0) / (o + o0)


def reciprocity_weight(q, rho_star):
    """g(q): saturating, increasing weight of perceived reciprocity, in [0, 1)."""
    return q / (q + rho_star)  # q > 0 because o0 > 0


def deficit(q, rho_star):
    """D = max(0, ρ* − q)."""
    return np.maximum(0.0, rho_star - q)


def closeness_drift(x, q, delta, kappa, ell, rho_star, mu_s=0.0):
    """dx/dt between events: decay, loyalty-damped deficit erosion, optional surplus boost."""
    dx = -delta * x - kappa * (1.0 - ell * x) * deficit(q, rho_star) * x
    if mu_s:
        dx = dx + mu_s * np.maximum(0.0, q - rho_star) * x * (1.0 - x)
    return dx


def advance_tie_flow(x, r, o, dt, *, delta, kappa, ell, rho_star, lam, o0, mu_s=0.0, max_step=0.05):
    """Advance (x, r, o) of one tie over dt with the deterministic flow.

    r and o decay exponentially (closed form). x decays in closed form when the flow
    is pure decay; otherwise it is integrated with fixed-step RK4.
    """
    if dt <= 0:
        return x, r, o
    decay = math.exp(-lam * dt)
    if kappa == 0.0 and mu_s == 0.0:
        return x * math.exp(-delta * dt), r * decay, o * decay
    n = max(1, math.ceil(dt / max_step))
    h = dt / n

    def f(xx, s):
        e = math.exp(-lam * s)
        q = (r * e + o0) / (o * e + o0)
        return float(closeness_drift(xx, q, delta, kappa, ell, rho_star, mu_s))

    s = 0.0
    for _ in range(n):
        k1 = f(x, s)
        k2 = f(x + 0.5 * h * k1, s + 0.5 * h)
        k3 = f(x + 0.5 * h * k2, s + 0.5 * h)
        k4 = f(x + h * k3, s + h)
        x = x + h / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
        s += h
    x = min(1.0, max(0.0, x))
    return x, r * decay, o * decay


def interaction_jump(x, eta):
    """Closeness after an accepted interaction: x + η(1 − x)."""
    return x + eta * (1.0 - x)


def capacity_factor(n_in_circle, target, cost):
    """Soft circle-capacity variant: closeness gains shrink when a circle is over its target.

    The factor is 1 / (1 + cost · max(0, n − K) / K).
    """
    excess = np.maximum(0.0, n_in_circle - target) / target
    return 1.0 / (1.0 + cost * excess)


def acceptance_probability(x_ji, g_ji, load_j, a0, a, b, c):
    """P_acc = σ(a0 + a·x_ji + b·g(q_ji) − c·U_j/B_j)."""
    return sigmoid(a0 + a * x_ji + b * g_ji - c * load_j)


def patience(tau, h1, x):
    """T_ij = τ_i · (1 + h1·x_ij)."""
    return tau * (1.0 + h1 * x)


def cancellation_hazard(tau, h1, x):
    return 1.0 / patience(tau, h1, x)


def cancellation_drop(r, psi, ell, x, t_wait):
    """r after cancelling a pending invitation that waited t_wait."""
    return np.maximum(0.0, r - psi * (1.0 - ell * x) * t_wait)


def mean_perception(pi, sigma_p):
    """E[e^{π+ξ}], ξ ~ N(0, σ_p²)."""
    return np.exp(pi + 0.5 * sigma_p**2)


def initial_circle(x, thresholds):
    """Circle index (1..4) of a closeness value, ignoring hysteresis."""
    return 1 + sum(1 for th in thresholds if x >= th)


def circle_transition(circle, x, thresholds, w):
    """Circle after one hysteresis check: promote, demote, or stay (one step at most)."""
    if circle < len(thresholds) + 1 and x >= thresholds[circle - 1] + 0.5 * w:
        return circle + 1
    if circle > 1 and x < thresholds[circle - 2] - 0.5 * w:
        return circle - 1
    return circle


def circle_transition_array(circle, x, thresholds, w):
    """Vectorised ``circle_transition`` (same rule) for integer circle arrays (0 = no tie)."""
    th = np.concatenate([[-np.inf], np.asarray(thresholds, dtype=float), [np.inf]])  # th[c] = lower bound of c+1
    c = np.asarray(circle)
    up = th[np.clip(c, 0, len(th) - 1)]  # lower bound of circle c+1 (= th[c])
    down = th[np.clip(c - 1, 0, len(th) - 1)]  # lower bound of circle c (= th[c-1])
    exists = c > 0
    promote = exists & (c < len(thresholds) + 1) & (x >= up + 0.5 * w)
    demote = exists & ~promote & (c > 1) & (x < down - 0.5 * w)
    return np.where(promote, c + 1, np.where(demote, c - 1, c))
