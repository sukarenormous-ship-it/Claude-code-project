"""Charts for Ch.13 — Perpetual Basis Strategy (Funding Rate)."""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from book_style import (save, style_axes, TEAL, NAVY, RED, GREEN, AMBER, BLUE,
                        GREY, RED_F, GREEN_F, BLUE_F, TEAL_F, AMBER_F)


def ou_basis(n, kappa, theta, sigma, seed):
    """Simple OU process for basis simulation."""
    rng = np.random.default_rng(seed)
    x = np.empty(n)
    x[0] = theta
    for t in range(1, n):
        x[t] = x[t-1] + kappa * (theta - x[t-1]) + sigma * rng.standard_normal()
    return x


# ============================================================
# Chart 1 — Basis Timeline + Funding Rate
# ============================================================
def chart_basis_timeline():
    rng = np.random.default_rng(5)
    n = 200
    kappa, theta, sigma = 0.1, 0.0, 0.3

    # OU basis path
    basis = ou_basis(n, kappa, theta, sigma, seed=5)

    # Add funding spikes at every 8h settlement (t=40,80,120,160)
    spike_times = [40, 80, 120, 160]
    for st in spike_times:
        height = rng.uniform(0.5, 1.5)
        for dt in range(-4, 12):
            idx = st + dt
            if 0 <= idx < n:
                decay = np.exp(-0.3 * max(0, dt))
                basis[idx] += height * decay

    # Compute entry/exit thresholds
    entry_thresh = 0.5 * sigma   # 0.15
    exit_thresh = 0.2 * sigma    # 0.06
    stop_thresh = 1.5 * sigma    # 0.45

    # Find entry points: basis > entry_thresh (looking for short basis trade)
    in_trade = False
    entry_pts = []
    exit_pts = []
    for t in range(1, n):
        if not in_trade and basis[t] > entry_thresh:
            in_trade = True
            entry_pts.append(t)
        elif in_trade and basis[t] < exit_thresh:
            in_trade = False
            exit_pts.append(t)

    # Funding rate bars: positive at each settlement
    fund_vals = np.array([0.02, 0.05, 0.08, 0.04])   # % per 8h

    t = np.arange(n)

    fig, axes = plt.subplots(2, 1, figsize=(7.4, 4.0),
                              gridspec_kw={"height_ratios": [2, 1]}, sharex=True)

    # ---- Top panel: Basis ----
    ax0 = axes[0]
    ax0.set_facecolor(TEAL_F)
    ax0.axhline(theta, color=TEAL, lw=1.3, ls="--", alpha=0.8, label=r"Fair basis ($\theta$=0)")
    ax0.axhline(entry_thresh, color=AMBER, lw=1.2, ls="--", alpha=0.9, label=f"Entry ±{entry_thresh:.2f}")
    ax0.axhline(-entry_thresh, color=AMBER, lw=1.2, ls="--", alpha=0.9)
    ax0.axhline(stop_thresh, color=RED, lw=1.0, ls=":", alpha=0.7, label=f"Stop-loss ±{stop_thresh:.2f}")
    ax0.axhline(-stop_thresh, color=RED, lw=1.0, ls=":", alpha=0.7)
    ax0.plot(t, basis, color=NAVY, lw=1.5, label="Basis (Perp − Spot)")

    # Mark entry and exit points
    if entry_pts:
        ax0.scatter(entry_pts, basis[entry_pts], color=RED, s=60, zorder=6,
                    marker="o", ec="white", lw=0.8, label="Entry (short perp)")
    if exit_pts:
        ax0.scatter(exit_pts, basis[exit_pts], color=GREEN, s=70, zorder=6,
                    marker="^", ec="white", lw=0.8, label="Exit (basis reverts)")

    # Mark funding settlement times
    for st in spike_times:
        ax0.axvline(st, color=GREY, lw=0.8, ls=":", alpha=0.5)

    ax0.set_ylabel("Basis (Perp − Spot)")
    ax0.set_title("Perp Basis and Funding Rate — Entry at Elevated Basis")
    ax0.legend(fontsize=8.5, loc="upper left", ncol=2)
    style_axes(ax0)

    # ---- Bottom panel: Funding Rate bars ----
    ax1 = axes[1]
    ax1.set_facecolor(AMBER_F)

    bar_colors = [RED if v > 0.05 else AMBER for v in fund_vals]
    ax1.bar(spike_times, fund_vals, width=10, color=bar_colors, alpha=0.85,
            edgecolor="white", lw=0.5)

    # Add value labels on bars
    for st, fv, bc in zip(spike_times, fund_vals, bar_colors):
        ax1.text(st, fv + 0.003, f"{fv:.2f}%", ha="center", va="bottom",
                 fontsize=8, color=bc, fontweight="bold")

    # High funding annotation
    high_idx = np.argmax(fund_vals)
    ax1.annotate("High funding!", xy=(spike_times[high_idx], fund_vals[high_idx]),
                 xytext=(spike_times[high_idx] + 15, fund_vals[high_idx]),
                 fontsize=8.5, color=RED,
                 arrowprops=dict(arrowstyle="->", color=RED, lw=1.0))

    ax1.set_ylabel("Funding Rate (%)")
    ax1.set_xlabel("t (hours)")
    ax1.set_xlim(0, n - 1)
    ax1.set_ylim(0, max(fund_vals) * 1.5)
    style_axes(ax1)

    fig.subplots_adjust(hspace=0.08)
    save(fig, "ch13-basis-timeline")


# ============================================================
# Chart 2 — Basis Trade P&L (10 simulated trades)
# ============================================================
def chart_basis_pnl():
    rng = np.random.default_rng(42)

    n_trades = 10
    # ~70% win rate: 7 wins, 3 losses
    wins = np.array([True, True, False, True, True, True, False, True, True, False])
    pnl = np.where(wins,
                   rng.uniform(0.10, 0.22, n_trades),   # wins: +0.10% to +0.22%
                   -rng.uniform(0.06, 0.11, n_trades))  # losses: -0.06% to -0.11%

    # Force a realistic distribution
    pnl = np.array([0.15, 0.18, -0.08, 0.12, 0.20, 0.14, -0.07, 0.16, 0.11, -0.09])
    wins = pnl > 0
    cum_pnl = np.cumsum(pnl)

    fig, ax = plt.subplots(figsize=(7.0, 3.5))
    ax.set_facecolor(GREEN_F)

    trade_ids = np.arange(1, n_trades + 1)
    bar_colors = [GREEN if w else RED for w in wins]
    bars = ax.bar(trade_ids, pnl * 100, color=bar_colors, alpha=0.85,
                  edgecolor="white", lw=0.6)

    # Value labels on bars
    for bar, p in zip(bars, pnl):
        ypos = bar.get_height()
        va = "bottom" if ypos >= 0 else "top"
        offset = 0.005 if ypos >= 0 else -0.005
        ax.text(bar.get_x() + bar.get_width() / 2,
                ypos * 100 + offset * 100,
                f"{p*100:+.2f}%", ha="center", va=va, fontsize=8,
                color=NAVY, fontweight="bold")

    # Twin axis: cumulative P&L
    ax2 = ax.twinx()
    ax2.plot(trade_ids, cum_pnl * 100, color=TEAL, lw=2.2, ls="--",
             marker="o", markersize=5, label="Cumulative P&L (%)")
    ax2.axhline(0, color=GREY, lw=0.8, alpha=0.5)
    ax2.set_ylabel("Cumulative P&L (%)", color=TEAL)
    ax2.tick_params(axis="y", labelcolor=TEAL)
    ax2.spines[["top"]].set_visible(False)

    # Annotation summary
    n_win = wins.sum()
    avg_win = pnl[wins].mean() * 100
    avg_loss = abs(pnl[~wins].mean()) * 100
    ax.annotate(
        f"Win rate: {n_win}/{n_trades} = {n_win/n_trades:.0%} | "
        f"Avg win: +{avg_win:.2f}% | Avg loss: −{avg_loss:.2f}%",
        xy=(0.5, 0.92), xycoords="axes fraction",
        ha="center", fontsize=9, color=NAVY,
        bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=GREY, alpha=0.85))

    ax.set_xlabel("Trade #")
    ax.set_ylabel("Per-trade P&L (%)")
    ax.set_title("Basis Trade P&L — 10 Simulated Trades")
    ax.set_xticks(trade_ids)
    style_axes(ax)

    # Legend patches
    win_patch = mpatches.Patch(color=GREEN, alpha=0.85, label="Win")
    loss_patch = mpatches.Patch(color=RED, alpha=0.85, label="Loss")
    ax.legend(handles=[win_patch, loss_patch], fontsize=9, loc="lower left")

    save(fig, "ch13-basis-pnl")


if __name__ == "__main__":
    chart_basis_timeline()
    chart_basis_pnl()
