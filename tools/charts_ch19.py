"""Charts for Ch.19 — Cost Analysis & Edge: Edge Waterfall."""
import numpy as np
from book_style import (save, style_axes, TEAL, NAVY, RED, GREEN, AMBER, BLUE,
                        GREY, RED_F, GREEN_F, BLUE_F, TEAL_F, AMBER_F)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


# ============================================================
# Chart: ch19-edge-waterfall — Gross Spread → Net Edge
# ============================================================
def chart_edge_waterfall():
    labels = ["Gross\nSpread", "Fees\n(2×taker)", "Bid-Ask\nSpread", "Slippage", "Funding", "NET\nEDGE"]
    # increments (positive = gain, negative = cost)
    increments = [0.30, -0.10, -0.04, -0.03, -0.02, 0.0]  # last bar is total
    net_edge = 0.30 - 0.10 - 0.04 - 0.03 - 0.02  # = 0.11

    # Running totals for waterfall: bar bottoms
    # Gross: 0 → 0.30
    # Fees: 0.30 → 0.20  (bottom=0.20, height=0.10 going down)
    # Bid-ask: 0.20 → 0.16
    # Slippage: 0.16 → 0.13
    # Funding: 0.13 → 0.11
    # Net: 0 → 0.11 (standalone total bar)

    bottoms = [0, 0.20, 0.16, 0.13, 0.11, 0]
    heights = [0.30, 0.10, 0.04, 0.03, 0.02, net_edge]
    colors  = [GREEN, RED, RED, RED, RED, TEAL]

    # connector y values (top of each bar going into next)
    connector_tops = [0.30, 0.20, 0.16, 0.13, 0.11]

    x = np.arange(len(labels))

    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    ax.set_facecolor(BLUE_F)

    bars = ax.bar(x, heights, bottom=bottoms, color=colors, width=0.55,
                  edgecolor="white", linewidth=0.8, zorder=3)

    # connectors between bars (horizontal dashed lines at top of each step)
    for i in range(len(connector_tops)):
        top = connector_tops[i]
        ax.plot([x[i] + 0.275, x[i+1] - 0.275], [top, top],
                color=GREY, lw=1.0, ls="--", zorder=2)

    # horizontal break-even line at y=0
    ax.axhline(0, color=RED, lw=1.5, ls="--", zorder=4, label="Break-even (0%)")

    # value labels on bars
    bar_label_vals = ["+0.30%", "−0.10%", "−0.04%", "−0.03%", "−0.02%", "+0.11%"]
    for i, (b, h, lbl) in enumerate(zip(bottoms, heights, bar_label_vals)):
        ypos = b + h + 0.004 if i != 1 and i != 2 and i != 3 and i != 4 else b - 0.012
        # for cost bars, label above the top (which is the bottom of the bar visually)
        if i in [1, 2, 3, 4]:  # cost bars — label above their top (bottom value)
            ypos = bottoms[i] + heights[i] + 0.004
        ax.text(x[i], ypos, lbl, ha="center", va="bottom",
                fontsize=8.5, fontweight="bold",
                color=colors[i] if i != 5 else TEAL)

    # annotate net edge final bar
    ax.annotate("Net Edge = 0.11%",
                xy=(x[5], net_edge), xytext=(x[5] - 0.5, net_edge + 0.06),
                fontsize=9, color=TEAL, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=TEAL, lw=1.1))

    # annotation pointing to cost bars
    ax.annotate("Min viable:\nfees < ½×gross",
                xy=(x[1], 0.25), xytext=(x[1] + 0.9, 0.27),
                fontsize=8, color=RED,
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.0))

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.2f}%"))
    ax.set_ylabel("P&L contribution (%)")
    ax.set_title("Edge Waterfall — Gross Spread to Net Edge (bp)")
    ax.set_ylim(-0.02, 0.37)
    ax.legend(fontsize=9)
    style_axes(ax)
    save(fig, "ch19-edge-waterfall")


if __name__ == "__main__":
    chart_edge_waterfall()
