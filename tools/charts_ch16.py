"""Charts for Ch.16 — Multi-leg Portfolio of Spreads."""
import numpy as np
from book_style import (save, style_axes, TEAL, NAVY, RED, GREEN, AMBER, BLUE,
                        GREY, RED_F, GREEN_F, BLUE_F, TEAL_F, AMBER_F)
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


# ============================================================
# Chart 1 — Covariance / Correlation Heatmap
# ============================================================
def chart_cov_matrix():
    corr = np.array([[1.00, 0.45, 0.22],
                     [0.45, 1.00, 0.18],
                     [0.22, 0.18, 1.00]])
    labels = ["BTC B↔L", "ETH B↔L", "BTC Basis"]

    fig, ax = plt.subplots(figsize=(5.0, 4.2))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    im = ax.imshow(corr, cmap="RdYlGn_r", vmin=0.0, vmax=1.0, aspect="auto")

    # Annotate cells
    for i in range(3):
        for j in range(3):
            ax.text(j, i, f"{corr[i, j]:.2f}",
                    ha="center", va="center",
                    fontsize=12, fontweight="bold",
                    color="white" if corr[i, j] > 0.5 else NAVY)

    ax.set_xticks([0, 1, 2])
    ax.set_yticks([0, 1, 2])
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_yticklabels(labels, fontsize=10)

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Correlation", fontsize=9)

    ax.set_title("Spread Correlation Matrix — Diversification Benefit")
    style_axes(ax)
    save(fig, "ch16-cov-matrix")


# ============================================================
# Chart 2 — Portfolio Weight Pie Chart
# ============================================================
def chart_portfolio_weights():
    labels = ["BTC B↔L", "ETH B↔L", "BTC Basis"]
    sizes = [50, 30, 20]
    colors = [GREEN, TEAL, AMBER]
    explode = [0.05, 0.02, 0.02]

    fig, ax = plt.subplots(figsize=(5.5, 4.2))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=None,
        colors=colors,
        explode=explode,
        autopct="%1.0f%%",
        pctdistance=0.75,
        shadow=True,
        startangle=90,
    )
    for at in autotexts:
        at.set_fontsize(12)
        at.set_fontweight("bold")
        at.set_color("white")

    ax.legend(wedges, labels,
              title="Spread",
              loc="center left",
              bbox_to_anchor=(0.85, 0.5),
              fontsize=10)

    ax.set_title("Mean-Variance Optimal Weights — 3-Spread Portfolio")
    save(fig, "ch16-portfolio-weights")


# ============================================================
# Chart 3 — Drawdown Comparison
# ============================================================
def chart_drawdown_comparison():
    n = 200
    t = np.arange(n)

    # BTC B↔L — higher volatility
    rng1 = np.random.default_rng(1)
    ret_btc = rng1.normal(0.0015, 0.025, n)
    cum_btc = np.cumsum(ret_btc)

    # ETH B↔L — moderate vol
    rng2 = np.random.default_rng(2)
    ret_eth = rng2.normal(0.001, 0.018, n)
    cum_eth = np.cumsum(ret_eth)

    # Portfolio (50/30/20 mix)
    cum_port = 0.5 * cum_btc + 0.3 * cum_eth + 0.2 * np.cumsum(
        np.random.default_rng(3).normal(0.001, 0.010, n)
    )

    def drawdown(cum):
        running_max = np.maximum.accumulate(cum)
        return cum - running_max

    dd_btc = drawdown(cum_btc)
    dd_eth = drawdown(cum_eth)
    dd_port = drawdown(cum_port)

    fig, ax = plt.subplots(figsize=(7.4, 3.5))
    fig.patch.set_facecolor(GREEN_F)
    ax.set_facecolor(GREEN_F)

    ax.plot(t, dd_btc, color=RED, lw=1.5, label="BTC B↔L")
    ax.plot(t, dd_eth, color=BLUE, lw=1.5, label="ETH B↔L")
    ax.fill_between(t, dd_port, 0, where=dd_port < 0,
                    color=TEAL, alpha=0.3, zorder=1)
    ax.plot(t, dd_port, color=TEAL, lw=2.5, label="Portfolio (50/30/20)", zorder=2)

    ax.axhline(0, color=NAVY, lw=0.8, ls="--", alpha=0.5)
    style_axes(ax)
    ax.set_xlabel("t (steps)")
    ax.set_ylabel("Drawdown")
    ax.set_title("Drawdown: Individual Spreads vs Diversified Portfolio")
    ax.legend(fontsize=9, loc="lower left")
    ax.set_xlim(0, n - 1)

    save(fig, "ch16-drawdown-comparison")


if __name__ == "__main__":
    chart_cov_matrix()
    chart_portfolio_weights()
    chart_drawdown_comparison()
