"""Charts for Ch.10 — Z-score & Robust Statistics."""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from book_style import (save, style_axes, TEAL, NAVY, RED, GREEN, AMBER, BLUE,
                        GREY, RED_F, GREEN_F, BLUE_F, TEAL_F, AMBER_F)


def _ou_path(n, kappa=0.08, theta=0.0, sigma=0.6, seed=7):
    rng = np.random.default_rng(seed)
    x = np.empty(n)
    x[0] = theta
    for t in range(1, n):
        x[t] = x[t-1] + kappa * (theta - x[t-1]) + sigma * rng.standard_normal()
    return x


def _rolling_zscore(series, W=30):
    """Rolling z-score using a causal window."""
    z = np.full(len(series), np.nan)
    for t in range(W, len(series)):
        win = series[t - W: t]
        mu = win.mean()
        sd = win.std(ddof=1)
        if sd > 1e-10:
            z[t] = (series[t] - mu) / sd
        else:
            z[t] = 0.0
    return z


# ============================================================
# Chart 1 — Z-score bands with entry/exit markers
# ============================================================
def chart_zscore_bands():
    n = 200
    W = 30
    eps = _ou_path(n, kappa=0.08, theta=0.0, sigma=0.6, seed=7)
    z = _rolling_zscore(eps, W)
    t = np.arange(n)

    fig, ax = plt.subplots(figsize=(7.4, 3.5))
    ax.set_facecolor("white")

    # ---- Background bands ----
    y_lo, y_hi = -5.5, 5.5
    # |z| > 3 → RED_F
    ax.fill_between(t, 3,  y_hi, color=RED_F,   alpha=1.0, zorder=0)
    ax.fill_between(t, y_lo, -3, color=RED_F,   alpha=1.0, zorder=0)
    # 2 < |z| < 3 → AMBER_F
    ax.fill_between(t, 2,  3,    color=AMBER_F,  alpha=1.0, zorder=0)
    ax.fill_between(t, -3, -2,   color=AMBER_F,  alpha=1.0, zorder=0)
    # |z| < 2 → GREEN_F
    ax.fill_between(t, -2,  2,   color=GREEN_F,  alpha=1.0, zorder=0)

    # ---- Horizontal reference lines ----
    for yv, color, ls in [(2, AMBER, "--"), (-2, AMBER, "--"),
                           (3, RED,   "--"), (-3, RED,   "--")]:
        ax.axhline(yv, color=color, lw=1.1, ls=ls, alpha=0.85, zorder=1)

    ax.axhline(0, color=TEAL, lw=0.8, ls="-", alpha=0.5, zorder=1)

    # ---- Z-score line ----
    ax.plot(t, z, color=NAVY, lw=1.5, zorder=2, label="Rolling z-score (W=30)")

    # ---- Entry points: |z| crosses 2.0 (from below, going outward) ----
    entry_idx = []
    for i in range(W + 1, n):
        if not np.isnan(z[i]) and not np.isnan(z[i-1]):
            if abs(z[i]) >= 2.0 and abs(z[i-1]) < 2.0:
                entry_idx.append(i)

    if entry_idx:
        ax.scatter(entry_idx, z[entry_idx], color=RED, s=55, zorder=4,
                   marker="o", ec="white", lw=0.8, label="Entry (|z| crosses 2.0)")

    # ---- Exit points: |z| returns below 0.5 ----
    exit_idx = []
    in_trade = False
    for i in range(W, n):
        if not np.isnan(z[i]):
            if not in_trade and abs(z[i]) >= 2.0:
                in_trade = True
            elif in_trade and abs(z[i]) < 0.5:
                exit_idx.append(i)
                in_trade = False

    if exit_idx:
        ax.scatter(exit_idx, z[exit_idx], color=GREEN, s=60, zorder=4,
                   marker="^", ec="white", lw=0.8, label="Exit (|z| < 0.5)")

    ax.set_xlim(0, n - 1)
    ax.set_ylim(y_lo, y_hi)
    ax.set_xlabel("t (bars)", color=NAVY)
    ax.set_ylabel("z-score", color=NAVY)
    ax.set_title("Z-score Bands — Entry / Exit Zones", fontsize=11,
                 fontweight="bold", color=NAVY)
    ax.legend(fontsize=8.5, loc="upper right", framealpha=0.9)
    style_axes(ax)
    save(fig, "ch10-zscore-bands")


# ============================================================
# Chart 2 — Outlier Effect: 2-panel before/after
# ============================================================
def chart_outlier_effect():
    n = 100
    W = 20
    rng_base = np.random.default_rng(42)
    kappa, theta, sigma = 0.10, 0.0, 0.5

    # Clean residuals
    eps_clean = np.empty(n)
    eps_clean[0] = theta
    for t in range(1, n):
        eps_clean[t] = (eps_clean[t-1]
                        + kappa * (theta - eps_clean[t-1])
                        + sigma * rng_base.standard_normal())

    # Dirty: inject huge outlier at t=50
    eps_dirty = eps_clean.copy()
    eps_dirty[50] = 20 * sigma    # 20× σ spike

    z_clean = _rolling_zscore(eps_clean, W)
    z_dirty = _rolling_zscore(eps_dirty, W)

    t = np.arange(n)
    y_lo, y_hi = -5.5, 5.5

    fig, axes = plt.subplots(1, 2, figsize=(8.5, 3.6), sharey=False)

    for ax_i, (ax, z, fc, ec, title_str) in enumerate(zip(
        axes,
        [z_clean, z_dirty],
        [GREEN_F, RED_F],
        [GREEN,   RED],
        ["Without Outlier\n— bands calibrated correctly",
         "With Outlier\n— σ inflated, signals masked"],
    )):
        ax.set_facecolor(fc)

        # Bands
        ax.fill_between(t, 3,  y_hi, color=RED_F,   alpha=0.8, zorder=0)
        ax.fill_between(t, y_lo, -3, color=RED_F,   alpha=0.8, zorder=0)
        ax.fill_between(t, 2,  3,    color=AMBER_F,  alpha=0.8, zorder=0)
        ax.fill_between(t, -3, -2,   color=AMBER_F,  alpha=0.8, zorder=0)
        ax.fill_between(t, -2,  2,   color=GREEN_F,  alpha=0.8, zorder=0)

        for yv, col, ls in [(2, AMBER, "--"), (-2, AMBER, "--"),
                              (3, RED,   "--"), (-3, RED,   "--")]:
            ax.axhline(yv, color=col, lw=1.0, ls=ls, alpha=0.75, zorder=1)
        ax.axhline(0, color=TEAL, lw=0.8, ls="-", alpha=0.4, zorder=1)

        ax.plot(t, z, color=NAVY, lw=1.5, zorder=2)

        # Frame border color
        for spine in ax.spines.values():
            spine.set_edgecolor(ec)
            spine.set_linewidth(2)

        ax.set_xlim(0, n - 1)
        ax.set_ylim(y_lo, y_hi)
        ax.set_xlabel("t (bars)", color=NAVY, fontsize=9)
        ax.set_ylabel("z-score", color=NAVY, fontsize=9)
        ax.set_title(title_str, fontsize=9, fontweight="bold", color=ec, pad=5)
        style_axes(ax)

        # Mark outlier on dirty panel
        if ax_i == 1:
            outlier_val = z_dirty[50] if not np.isnan(z_dirty[50]) else y_hi
            ax.axvline(50, color=RED, lw=1.8, ls=":", alpha=0.7, zorder=3)
            ax.annotate(
                "σ inflated →\nz-score compressed\n→ signals invisible",
                xy=(52, 0.3),
                fontsize=7, color=RED, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.3", fc="white",
                          ec=RED, alpha=0.9),
                zorder=5,
            )

    fig.suptitle("Outlier Effect on Z-score Bands", fontsize=10.5,
                 fontweight="bold", color=NAVY, y=1.01)
    fig.tight_layout()
    save(fig, "ch10-outlier-effect")


if __name__ == "__main__":
    chart_zscore_bands()
    chart_outlier_effect()
