"""Charts for Ch.20 — Risk Management & Portfolio: Framework Overview + Drawdown Path."""
import numpy as np
from book_style import (save, style_axes, TEAL, NAVY, RED, GREEN, AMBER, BLUE,
                        GREY, RED_F, GREEN_F, BLUE_F, TEAL_F, AMBER_F)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch


# ============================================================
# Chart 1: ch20-framework-overview — Layered Pipeline Diagram
# ============================================================
def chart_framework_overview():
    fig, ax = plt.subplots(figsize=(7.5, 5.5))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    layers = [
        ("Data & Pair Selection",       TEAL,   "cointegrated pairs",       0.88),
        ("Cointegration Test (ADF)",    BLUE,   "ε_t residual",             0.79),
        ("OU Calibration (κ, θ, σ)",   GREEN,  "half-life, σ_stat",        0.70),
        ("Signal (z-score)",            AMBER,  "z > 2.0 → entry signal",   0.61),
        ("State Machine",               NAVY,   "OPEN / HOLD / EXIT",       0.52),
        ("Position Sizing (Kelly)",     TEAL,   "f* = edge/σ²",             0.43),
        ("Execution (Cross-venue)",     GREEN,  "fills + leg sync",         0.34),
        ("Risk Monitor (Drawdown, VaR)",RED,    "circuit breakers",         0.25),
    ]

    box_x = 0.12
    box_w = 0.62
    box_h = 0.07
    arrow_x = box_x + box_w / 2

    for i, (label, color, side_label, y_center) in enumerate(layers):
        # box
        fancy = FancyBboxPatch(
            (box_x, y_center - box_h / 2),
            box_w, box_h,
            boxstyle="round,pad=0.01",
            facecolor=color, edgecolor="white", linewidth=1.5,
            zorder=3
        )
        ax.add_patch(fancy)
        ax.text(box_x + box_w / 2, y_center, label,
                ha="center", va="center",
                fontsize=10, color="white", fontweight="bold", zorder=4)

        # side label
        ax.text(box_x + box_w + 0.025, y_center, side_label,
                ha="left", va="center",
                fontsize=8, color=color, style="italic")

        # arrow between layers
        if i < len(layers) - 1:
            next_y = layers[i + 1][3]
            ax.annotate("",
                        xy=(arrow_x, next_y + box_h / 2 + 0.005),
                        xytext=(arrow_x, y_center - box_h / 2 - 0.005),
                        arrowprops=dict(arrowstyle="->", color=GREY, lw=1.4),
                        zorder=2)

    ax.set_title("Stat Arb System — Full Pipeline", fontsize=13, fontweight="bold",
                 color=NAVY, pad=10)
    save(fig, "ch20-framework-overview")


# ============================================================
# Chart 2: ch20-drawdown-path — Cumulative P&L with Circuit Breakers
# ============================================================
def chart_drawdown_path():
    rng = np.random.default_rng(42)
    n = 200
    t = np.arange(n)

    # Phase 1: t=0–80  gradual positive drift
    p1 = np.cumsum(rng.normal(0.03, 0.5, 80))
    # Phase 2: t=80–120  drawdown to ~-8%
    p2_inc = np.cumsum(rng.normal(-0.18, 0.45, 40))
    p2 = p1[-1] + p2_inc
    # Phase 3: t=120–200  recovery
    p3_inc = np.cumsum(rng.normal(0.10, 0.40, 80))
    p3 = p2[-1] + p3_inc

    cum_pnl = np.concatenate([p1, p2, p3]) / 100  # convert to fraction (percent/100)

    # locate peak and trough in the path
    peak_idx = int(np.argmax(cum_pnl[:100]))
    trough_idx = int(np.argmin(cum_pnl))

    fig, ax = plt.subplots(figsize=(7.4, 3.5))
    ax.set_facecolor(AMBER_F)

    # fill below zero
    ax.fill_between(t, cum_pnl, 0,
                    where=(cum_pnl < 0),
                    color=RED, alpha=0.3, zorder=1)

    # main P&L line
    ax.plot(t, cum_pnl, color=NAVY, lw=1.5, zorder=3, label="Cumulative P&L")

    # circuit breaker lines
    cb_levels = [
        (-0.03, AMBER, "--", 1.2, "Warning (−3%)"),
        (-0.05, AMBER, "--", 1.2, "Reduce size (−5%)"),
        (-0.08, RED,   "--", 1.5, "Halt trading (−8%)"),
        (-0.12, RED,   "--", 2.5, "Emergency stop (−12%)"),
    ]
    for level, color, ls, lw, lbl in cb_levels:
        ax.axhline(level, color=color, ls=ls, lw=lw, zorder=2, label=lbl)

    # peak and trough markers
    ax.scatter([peak_idx],   [cum_pnl[peak_idx]],   color=GREEN, s=60, zorder=5,
               ec="white", lw=1, label=f"Peak ({cum_pnl[peak_idx]:.1%})")
    ax.scatter([trough_idx], [cum_pnl[trough_idx]], color=RED,   s=60, zorder=5,
               marker="v", ec="white", lw=1, label=f"Trough ({cum_pnl[trough_idx]:.1%})")

    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.set_xlabel("Time (bars)")
    ax.set_ylabel("Cumulative P&L")
    ax.set_title("Drawdown Path — Circuit Breaker Levels")
    ax.legend(fontsize=8.5, loc="upper left", ncol=2)
    style_axes(ax)
    save(fig, "ch20-drawdown-path")


if __name__ == "__main__":
    chart_framework_overview()
    chart_drawdown_path()
