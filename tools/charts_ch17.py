"""Charts for Ch.17 — Commodity Basis / Calendar Spread."""
import numpy as np
from book_style import (save, style_axes, TEAL, NAVY, RED, GREEN, AMBER, BLUE,
                        GREY, RED_F, GREEN_F, BLUE_F, TEAL_F, AMBER_F)
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec


# ============================================================
# Chart 1 — Contango vs Backwardation (2-panel)
# ============================================================
def chart_contango_backwardation():
    months = np.array([1, 2, 3, 6, 12])
    # Contango: price rises with expiry (storage cost)
    contango = 100 + 0.7 * months        # 100 → ~108.4
    # Backwardation: price falls with expiry (convenience yield)
    backwardation = 100 - 0.65 * months  # 100 → ~92.2

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.0, 3.6))

    # ---- Left: Contango ----
    ax1.set_facecolor(RED_F)
    ax1.plot(months, contango, color=NAVY, lw=2.0, marker="o",
             markersize=5, label="Futures F(T)")
    ax1.axhline(100, color=TEAL, lw=1.5, ls="--", label="Spot S=100")
    ax1.fill_between(months, 100, contango, color=RED, alpha=0.2,
                     label="Cost of carry")
    ax1.annotate("Contango:\nstorage cost → F>S",
                 xy=(6, contango[3]), xytext=(4, 103),
                 fontsize=8, color=RED,
                 arrowprops=dict(arrowstyle="->", color=RED, lw=1.0))
    ax1.set_xticks(months)
    ax1.set_xticklabels(["1m", "2m", "3m", "6m", "12m"])
    ax1.set_xlabel("Months to expiry")
    ax1.set_ylabel("Price")
    ax1.set_title("Contango — F(T) > Spot")
    ax1.legend(fontsize=8)
    style_axes(ax1)

    # ---- Right: Backwardation ----
    ax2.set_facecolor(GREEN_F)
    ax2.plot(months, backwardation, color=GREEN, lw=2.0, marker="o",
             markersize=5, label="Futures F(T)")
    ax2.axhline(100, color=TEAL, lw=1.5, ls="--", label="Spot S=100")
    ax2.fill_between(months, backwardation, 100, color=GREEN, alpha=0.2,
                     label="Convenience yield")
    ax2.annotate("Backwardation:\nconvenience yield → F<S",
                 xy=(6, backwardation[3]), xytext=(3.5, 96.5),
                 fontsize=8, color=GREEN,
                 arrowprops=dict(arrowstyle="->", color=GREEN, lw=1.0))
    ax2.set_xticks(months)
    ax2.set_xticklabels(["1m", "2m", "3m", "6m", "12m"])
    ax2.set_xlabel("Months to expiry")
    ax2.set_ylabel("Price")
    ax2.set_title("Backwardation — F(T) < Spot")
    ax2.legend(fontsize=8)
    style_axes(ax2)

    fig.suptitle("Contango vs Backwardation — Forward Curve Structure",
                 fontweight="bold", fontsize=12, color=NAVY, y=1.02)

    save(fig, "ch17-contango-backwardation")


# ============================================================
# Chart 2 — Basis Time-series + Z-score (2-panel stacked)
# ============================================================
def chart_basis_calendar():
    rng = np.random.default_rng(17)
    n = 180
    t = np.arange(n)

    # OU process for basis
    kappa, theta, sigma = 0.08, 0.0, 0.4
    basis = np.empty(n)
    basis[0] = 0.0
    for i in range(1, n):
        basis[i] = (basis[i - 1]
                    + kappa * (theta - basis[i - 1])
                    + sigma * rng.standard_normal())

    # Rolling 20-step z-score
    z = np.full(n, np.nan)
    win = 20
    for i in range(win, n):
        w = basis[i - win:i]
        mu, sd = w.mean(), w.std()
        if sd > 1e-8:
            z[i] = (basis[i] - mu) / sd

    # Entry/exit thresholds
    entry_thr = 0.6
    stop_thr = 1.2
    z_entry = 2.0

    fig = plt.figure(figsize=(7.4, 3.8))
    gs = gridspec.GridSpec(2, 1, height_ratios=[2, 1], hspace=0.12)
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1], sharex=ax1)

    # ---- Top: Basis ----
    ax1.set_facecolor(TEAL_F)
    ax1.plot(t, basis, color=NAVY, lw=1.5, label="Basis F(near)−F(far)")
    ax1.axhline(entry_thr, color=AMBER, lw=1.2, ls="--", label=f"±{entry_thr} entry")
    ax1.axhline(-entry_thr, color=AMBER, lw=1.2, ls="--")
    ax1.axhline(stop_thr, color=RED, lw=1.2, ls="--", label=f"±{stop_thr} stop-loss")
    ax1.axhline(-stop_thr, color=RED, lw=1.2, ls="--")
    ax1.axhline(0, color=GREY, lw=0.8, ls=":", alpha=0.7)

    # Mark entries (basis crosses entry threshold)
    entry_up = (basis[:-1] < entry_thr) & (basis[1:] >= entry_thr)
    entry_dn = (basis[:-1] > -entry_thr) & (basis[1:] <= -entry_thr)
    entry_idx = np.where(entry_up | entry_dn)[0] + 1
    ax1.scatter(entry_idx, basis[entry_idx], color=GREEN, s=40,
                zorder=5, marker="^", label="Entry signal")

    ax1.set_ylabel("Calendar Spread Basis")
    ax1.legend(fontsize=8, loc="upper right", ncol=2)
    style_axes(ax1)
    plt.setp(ax1.get_xticklabels(), visible=False)

    # ---- Bottom: Z-score ----
    ax2.set_facecolor(AMBER_F)
    ax2.plot(t, z, color=NAVY, lw=1.2, label="Z-score (20-step)")
    ax2.axhline(z_entry, color=AMBER, lw=1.2, ls="--", label=f"±{z_entry}")
    ax2.axhline(-z_entry, color=AMBER, lw=1.2, ls="--")
    ax2.axhline(0, color=GREY, lw=0.8, ls=":", alpha=0.7)
    ax2.set_ylabel("Z-score")
    ax2.set_xlabel("t (days)")
    ax2.legend(fontsize=8, loc="upper right")
    style_axes(ax2)

    fig.suptitle("Calendar Spread Basis — Entry/Exit via Z-score",
                 fontweight="bold", fontsize=12, color=NAVY)

    save(fig, "ch17-basis-calendar")


if __name__ == "__main__":
    chart_contango_backwardation()
    chart_basis_calendar()
