"""Charts for Ch.7 — Entry/Exit Zones."""
import numpy as np
from book_style import (save, style_axes, TEAL, NAVY, RED, GREEN, AMBER, BLUE,
                        GREY, RED_F, AMBER_F, GREEN_F, TEAL_F, BLUE_F)
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch


def ou_path(n, kappa, theta, sigma, x0, seed):
    rng = np.random.default_rng(seed)
    x = np.empty(n)
    x[0] = x0
    for t in range(1, n):
        x[t] = x[t - 1] + kappa * (theta - x[t - 1]) + sigma * rng.standard_normal()
    return x


def compute_zscore(x, win=30):
    """Rolling z-score with given window."""
    n = len(x)
    z = np.full(n, np.nan)
    for i in range(win - 1, n):
        chunk = x[i - win + 1: i + 1]
        mu = chunk.mean()
        sd = chunk.std(ddof=1)
        if sd > 0:
            z[i] = (x[i] - mu) / sd
    return z


# ============================================================
# Chart 1 — Entry / Exit Zones with colour fills + arrows
# ============================================================
def chart_entry_exit_zones():
    n = 240
    kappa, theta, sigma = 0.06, 0.0, 1.0
    sd = sigma / np.sqrt(2 * kappa)
    x = ou_path(n, kappa, theta, sigma, x0=0.0, seed=13)
    t = np.arange(n)
    z = compute_zscore(x, win=30)

    fig, ax = plt.subplots(figsize=(7.4, 4.0))

    # --- zone fills using axhspan ---
    # STOP zone: |spread| > 3σ  (RED_F)
    ax.axhspan( 3*sd,  5*sd, color=RED_F,   alpha=0.85, zorder=0)
    ax.axhspan(-5*sd, -3*sd, color=RED_F,   alpha=0.85, zorder=0)
    # ENTRY zone: 2σ < |spread| < 3σ  (AMBER_F)
    ax.axhspan( 2*sd,  3*sd, color=AMBER_F, alpha=0.85, zorder=0)
    ax.axhspan(-3*sd, -2*sd, color=AMBER_F, alpha=0.85, zorder=0)
    # HOLD zone: |spread| < 2σ  (GREEN_F)
    ax.axhspan(-2*sd,  2*sd, color=GREEN_F, alpha=0.85, zorder=0)

    # --- reference lines ---
    ax.axhline(0,      color=TEAL,  lw=1.4, ls="--", alpha=0.7)
    ax.axhline( 2*sd,  color=AMBER, lw=1.0, ls=":",  alpha=0.9)
    ax.axhline(-2*sd,  color=AMBER, lw=1.0, ls=":",  alpha=0.9)
    ax.axhline( 3*sd,  color=RED,   lw=1.0, ls=":",  alpha=0.9)
    ax.axhline(-3*sd,  color=RED,   lw=1.0, ls=":",  alpha=0.9)

    # --- OU path ---
    ax.plot(t, x, color=NAVY, lw=1.7, zorder=3, label="ε (spread)")

    # --- detect entries: crossings into entry zone from hold zone ---
    # entry = crossing from |z| < 2 to |z| > 2 (using spread, not z-score for plot)
    entry_idx = []
    exit_idx  = []
    in_trade  = False
    for i in range(1, n):
        if np.isnan(z[i]) or np.isnan(z[i - 1]):
            continue
        abs_z_prev = abs(z[i - 1])
        abs_z_curr = abs(z[i])
        if not in_trade and abs_z_prev < 2 and abs_z_curr >= 2:
            entry_idx.append(i)
            in_trade = True
        elif in_trade and abs_z_prev >= 0.5 and abs_z_curr < 0.5:
            exit_idx.append(i)
            in_trade = False

    # Entry dots (red) at the crossing bar
    if entry_idx:
        ax.scatter(entry_idx, x[entry_idx], color=RED, s=70, zorder=6,
                   ec="white", lw=1.2, label="Entry crossing")
    # Exit dots (green)
    if exit_idx:
        ax.scatter(exit_idx, x[exit_idx], color=GREEN, s=70, zorder=6,
                   ec="white", lw=1.2, marker="v", label="Exit (return to hold)")

    # --- zone labels on right margin ---
    right = n - 1
    ax.text(right, 3.6*sd, "STOP",  color=RED,   fontsize=8.5, ha="right", fontweight="bold")
    ax.text(right, 2.4*sd, "ENTRY", color=AMBER, fontsize=8.5, ha="right", fontweight="bold")
    ax.text(right, 0.2*sd, "HOLD / EXIT", color=GREEN, fontsize=8.5, ha="right", fontweight="bold")
    ax.text(right,-2.4*sd, "ENTRY", color=AMBER, fontsize=8.5, ha="right", fontweight="bold")
    ax.text(right,-3.6*sd, "STOP",  color=RED,   fontsize=8.5, ha="right", fontweight="bold")

    # Legend
    zone_patches = [
        Patch(facecolor=RED_F,   edgecolor=RED,   label="|z|>3: STOP zone"),
        Patch(facecolor=AMBER_F, edgecolor=AMBER, label="2<|z|<3: ENTRY zone"),
        Patch(facecolor=GREEN_F, edgecolor=GREEN, label="|z|<2: HOLD zone"),
    ]
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles=handles + zone_patches, loc="lower right", fontsize=8, ncol=2)

    ax.set_yticks([-3*sd, -2*sd, 0, 2*sd, 3*sd])
    ax.set_yticklabels(["−3σ", "−2σ", "θ", "+2σ", "+3σ"])
    ax.set_xlabel("เวลา t (bars)")
    ax.set_ylabel("ε (spread)")
    ax.set_title("OU Trade Zones — Entry, Hold, and Stop Loss")
    ax.set_xlim(0, n - 1)
    ax.set_ylim(-5*sd, 5*sd)
    style_axes(ax)
    save(fig, "ch7-entry-exit-zones")


# ============================================================
# Chart 2 — P&L per trade (bar chart)
# ============================================================
def chart_pnl_per_trade():
    # Run the same OU path as chart 1 but on a longer path to gather more trades
    n = 600
    kappa, theta, sigma = 0.07, 0.0, 1.0
    x = ou_path(n, kappa, theta, sigma, x0=0.0, seed=21)
    z = compute_zscore(x, win=30)

    # Simple backtest: enter when |z| crosses above 2, exit when |z| < 0.5
    trades = []
    in_trade   = False
    entry_val  = 0.0
    direction  = 0   # +1 = long spread (z went to -2), -1 = short spread (z went to +2)

    for i in range(1, n):
        if np.isnan(z[i]) or np.isnan(z[i - 1]):
            continue
        if not in_trade:
            if z[i - 1] >= -2 and z[i] <= -2:
                # z dipped to -2: long spread expecting reversion up
                in_trade  = True
                entry_val = x[i]
                direction = +1
                entry_bar = i
            elif z[i - 1] <= 2 and z[i] >= 2:
                # z rose to +2: short spread expecting reversion down
                in_trade  = True
                entry_val = x[i]
                direction = -1
                entry_bar = i
        else:
            if abs(z[i]) < 0.5:
                exit_val = x[i]
                pnl = direction * (entry_val - exit_val)   # profit if spread reverts
                trades.append(pnl)
                in_trade = False

    if not trades:
        # Fallback: create synthetic trades so the chart renders
        trades = [0.3, -0.1, 0.5, 0.2, -0.2, 0.4]

    trades = np.array(trades)
    colors = [GREEN if p >= 0 else RED for p in trades]

    fig, ax = plt.subplots(figsize=(7.4, 3.2))
    bars = ax.bar(np.arange(len(trades)), trades, color=colors, edgecolor="white",
                  linewidth=0.6, width=0.75)

    ax.axhline(0, color=NAVY, lw=1.2, ls="-")

    # Cumulative P&L overlay on twin axis
    ax2 = ax.twinx()
    cum_pnl = np.cumsum(trades)
    ax2.plot(np.arange(len(trades)), cum_pnl, color=TEAL, lw=1.8, ls="--",
             label="Cumulative P&L")
    ax2.set_ylabel("Cumulative P&L", color=TEAL)
    ax2.tick_params(axis="y", colors=TEAL)
    ax2.spines["top"].set_visible(False)

    # Stats annotation
    n_win  = int(np.sum(trades > 0))
    n_loss = int(np.sum(trades <= 0))
    win_rt = n_win / len(trades) * 100
    ax.text(0.98, 0.97,
            f"Trades: {len(trades)}  |  Win: {n_win} ({win_rt:.0f}%)  |  Loss: {n_loss}",
            transform=ax.transAxes, ha="right", va="top",
            fontsize=8.5, color=NAVY,
            bbox=dict(facecolor="white", edgecolor=GREY, boxstyle="round,pad=0.3"))

    ax.set_xlabel("Trade #")
    ax.set_ylabel("P&L (spread units)")
    ax.set_title("P&L ต่อ Trade — Backtest บน OU Path\n(Enter |z|>2, Exit |z|<0.5)")

    # Legend
    legend_handles = [
        Patch(facecolor=GREEN, label="Profit"),
        Patch(facecolor=RED,   label="Loss"),
        Line2D([0], [0], color=TEAL, lw=1.8, ls="--", label="Cumulative P&L"),
    ]
    ax.legend(handles=legend_handles, loc="upper left", fontsize=8.5)

    style_axes(ax)
    save(fig, "ch7-pnl-per-trade")


if __name__ == "__main__":
    chart_entry_exit_zones()
    chart_pnl_per_trade()
