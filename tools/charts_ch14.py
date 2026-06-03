"""Charts for Ch.14 — Cross-venue Strategy (Leg Risk & Execution Flow)."""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from book_style import (save, style_axes, TEAL, NAVY, RED, GREEN, AMBER, BLUE,
                        GREY, RED_F, GREEN_F, BLUE_F, TEAL_F, AMBER_F)

VIOLET = "#7c3aed"


# ============================================================
# Chart 1 — Leg Risk: simultaneous vs failed execution
# ============================================================
def chart_leg_risk():
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.8))
    fig.patch.set_facecolor("white")

    for ax, (bg, title, success) in zip(axes, [
        (GREEN_F, "Both legs fill simultaneously", True),
        (RED_F,   "Leg B fails — naked position", False),
    ]):
        ax.set_facecolor(bg)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        ax.set_title(title, fontsize=9.5, fontweight="bold", pad=8,
                     color=GREEN if success else RED)

        # Exchange A box (left)
        boxa = FancyBboxPatch((0.05, 0.55), 0.36, 0.22,
                              boxstyle="round,pad=0.02",
                              facecolor=BLUE_F, edgecolor=BLUE, linewidth=1.5,
                              transform=ax.transAxes)
        ax.add_patch(boxa)
        ax.text(0.23, 0.66, "Exchange A\n(Bybit)", ha="center", va="center",
                fontsize=9, fontweight="bold", color=BLUE, transform=ax.transAxes)

        # Exchange B box (right)
        boxb_color = TEAL_F if success else RED_F
        boxb_edge = TEAL if success else RED
        boxb = FancyBboxPatch((0.59, 0.55), 0.36, 0.22,
                              boxstyle="round,pad=0.02",
                              facecolor=boxb_color, edgecolor=boxb_edge, linewidth=1.5,
                              transform=ax.transAxes)
        ax.add_patch(boxb)
        label_b = "Exchange B\n(Lighter)" if success else "Exchange B\n(Lighter) ✗"
        ax.text(0.77, 0.66, label_b, ha="center", va="center",
                fontsize=9, fontweight="bold", color=TEAL if success else RED,
                transform=ax.transAxes)

        # Signal box at top center
        sig = FancyBboxPatch((0.35, 0.82), 0.30, 0.13,
                             boxstyle="round,pad=0.02",
                             facecolor=NAVY, edgecolor="white", linewidth=1,
                             transform=ax.transAxes)
        ax.add_patch(sig)
        ax.text(0.50, 0.885, "z > 2.0 signal", ha="center", va="center",
                fontsize=8.5, color="white", transform=ax.transAxes)

        # Arrows from signal → exchanges
        for tx in [0.23, 0.77]:
            ax.annotate("", xy=(tx, 0.77), xytext=(0.50, 0.82),
                        xycoords="axes fraction", textcoords="axes fraction",
                        arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.3))

        if success:
            # Fill labels
            ax.text(0.23, 0.47, "Buy A @ $30,000 ✓", ha="center", va="center",
                    fontsize=8, color=TEAL, fontweight="bold",
                    transform=ax.transAxes)
            ax.text(0.77, 0.47, "Sell B @ $30,050 ✓", ha="center", va="center",
                    fontsize=8, color=GREEN, fontweight="bold",
                    transform=ax.transAxes)
            # Result box
            res = FancyBboxPatch((0.20, 0.10), 0.60, 0.22,
                                 boxstyle="round,pad=0.02",
                                 facecolor=GREEN_F, edgecolor=GREEN, linewidth=1.5,
                                 transform=ax.transAxes)
            ax.add_patch(res)
            ax.text(0.50, 0.21, "Spread captured: $50\n(fully hedged)", ha="center",
                    va="center", fontsize=9, color=GREEN, fontweight="bold",
                    transform=ax.transAxes)
        else:
            ax.text(0.23, 0.47, "Buy A @ $30,000 ✓", ha="center", va="center",
                    fontsize=8, color=TEAL, fontweight="bold",
                    transform=ax.transAxes)
            ax.text(0.77, 0.47, "FAILED (timeout)", ha="center", va="center",
                    fontsize=8, color=RED, fontweight="bold",
                    transform=ax.transAxes)
            # X mark on B
            ax.text(0.77, 0.66, "✗", ha="center", va="center",
                    fontsize=22, color=RED, alpha=0.4, transform=ax.transAxes)
            # Warning box
            res = FancyBboxPatch((0.10, 0.10), 0.80, 0.22,
                                 boxstyle="round,pad=0.02",
                                 facecolor=RED_F, edgecolor=RED, linewidth=2,
                                 transform=ax.transAxes)
            ax.add_patch(res)
            ax.text(0.50, 0.21, "NAKED LONG — unhedged!\nEmergency exit required",
                    ha="center", va="center", fontsize=9, color=RED, fontweight="bold",
                    transform=ax.transAxes)

    fig.suptitle("Leg Risk in Cross-venue Execution", fontsize=11.5,
                 fontweight="bold", color=NAVY, y=1.02)
    fig.subplots_adjust(wspace=0.12, top=0.88, bottom=0.05)
    save(fig, "ch14-leg-risk")


# ============================================================
# Chart 2 — Execution Flowchart
# ============================================================
def chart_execution_flow():
    fig, ax = plt.subplots(figsize=(6.0, 7.0))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    def box(x, y, w, h, text, color, tc="white", shape="rect"):
        if shape == "diamond":
            # Draw diamond using polygon
            cx, cy = x + w/2, y + h/2
            pts = np.array([[cx, y+h], [x+w, cy], [cx, y], [x, cy]])
            patch = plt.Polygon(pts, facecolor=color, edgecolor="white",
                                linewidth=1.5, transform=ax.transAxes, zorder=3)
            ax.add_patch(patch)
        else:
            patch = FancyBboxPatch((x, y), w, h,
                                   boxstyle="round,pad=0.012",
                                   facecolor=color, edgecolor="white", linewidth=1.5,
                                   transform=ax.transAxes, zorder=3)
            ax.add_patch(patch)
        ax.text(x + w/2, y + h/2, text, ha="center", va="center",
                fontsize=7.5, fontweight="bold", color=tc,
                transform=ax.transAxes, zorder=4,
                multialignment="center")

    def arr(x1, y1, x2, y2, color=NAVY, label="", label_side="right"):
        p1 = ax.transAxes.transform((x1, y1))
        p2 = ax.transAxes.transform((x2, y2))
        ap = FancyArrowPatch(p1, p2, arrowstyle="->, head_width=5, head_length=7",
                             color=color, lw=1.3, transform=None, zorder=2)
        ax.add_patch(ap)
        if label:
            mx = (x1 + x2) / 2 + (0.06 if label_side == "right" else -0.06)
            my = (y1 + y2) / 2
            ax.text(mx, my, label, ha="center", va="center", fontsize=7,
                    color=color, transform=ax.transAxes, zorder=5,
                    bbox=dict(fc="white", ec="none", pad=1, alpha=0.9))

    BW, BH = 0.50, 0.065     # box width/height
    DW, DH = 0.54, 0.070     # diamond width/height
    cx = 0.25                 # left edge for center-align boxes at x=cx, center=cx+BW/2=0.50

    # Layout (top to bottom): y positions (top of box)
    Y = [0.915, 0.815, 0.710, 0.595, 0.475, 0.360, 0.245, 0.130]

    # Node 0: Signal
    box(cx, Y[0], BW, BH, "Signal: z > 2.0", TEAL)
    arr(0.50, Y[0], 0.50, Y[1])

    # Node 1: Submit Leg A
    box(cx, Y[1], BW, BH, "Submit Leg A (maker)", BLUE)
    arr(0.50, Y[1], 0.50, Y[2])

    # Node 2: Leg A filled? (diamond)
    box(cx - 0.02, Y[2], DW, DH, "Leg A\nfilled?", AMBER, tc=NAVY, shape="diamond")
    # YES path: down
    arr(0.50, Y[2], 0.50, Y[3], GREEN, "YES")
    # NO path: right → Cancel
    box(0.80, Y[2]+0.001, 0.18, BH-0.002, "Cancel all\n(timeout)", RED)
    ax.annotate("", xy=(0.80, Y[2]+BH/2), xytext=(cx+DW-0.02, Y[2]+DH/2),
                xycoords="axes fraction", textcoords="axes fraction",
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.2))
    ax.text(0.72, Y[2]+DH/2+0.01, "NO", ha="center", va="center",
            fontsize=7, color=RED, transform=ax.transAxes)

    # Node 3: Submit Leg B
    box(cx, Y[3], BW, BH, "Submit Leg B (taker)", GREEN)
    arr(0.50, Y[3], 0.50, Y[4])

    # Node 4: Leg B filled? (diamond)
    box(cx - 0.02, Y[4], DW, DH, "Leg B\nfilled?", AMBER, tc=NAVY, shape="diamond")
    # YES → Trade complete
    arr(0.50, Y[4], 0.50, Y[5], GREEN, "YES")
    # NO → check partial (right side)
    box(0.80, Y[4]+0.001, 0.18, BH-0.002, "Leg B\npartial?", AMBER, tc=NAVY)
    ax.annotate("", xy=(0.80, Y[4]+BH/2), xytext=(cx+DW-0.02, Y[4]+DH/2),
                xycoords="axes fraction", textcoords="axes fraction",
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.2))
    ax.text(0.72, Y[4]+DH/2+0.01, "NO/2s", ha="center", va="center",
            fontsize=7, color=RED, transform=ax.transAxes)

    # From "Leg B partial?" → two outcomes
    # Partial YES → adjust Leg A size
    box(0.76, Y[5]+0.001, 0.22, BH-0.002, "Adjust Leg A\nsize", AMBER, tc=NAVY)
    ax.annotate("", xy=(0.87, Y[5]+BH-0.002), xytext=(0.89, Y[4]+0.001),
                xycoords="axes fraction", textcoords="axes fraction",
                arrowprops=dict(arrowstyle="->", color=AMBER, lw=1.2))
    ax.text(0.97, (Y[4]+Y[5])/2+BH/2, "Part.", ha="center", va="center",
            fontsize=7, color=AMBER, transform=ax.transAxes)
    # Partial NO → emergency flatten
    box(0.76, Y[6]+0.001, 0.22, BH-0.002, "Emergency\nflatten Leg A", RED)
    ax.annotate("", xy=(0.87, Y[6]+BH-0.002), xytext=(0.89, Y[5]+0.001),
                xycoords="axes fraction", textcoords="axes fraction",
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.2))
    ax.text(0.97, (Y[5]+Y[6])/2+BH/2, "None", ha="center", va="center",
            fontsize=7, color=RED, transform=ax.transAxes)

    # Node 5: Trade Complete
    box(cx, Y[5], BW, BH, "Trade Complete\nMonitor spread", TEAL)
    arr(0.50, Y[5], 0.50, Y[6])

    # Node 6: Exit when |z| < 0.5
    box(cx, Y[6], BW, BH, "Exit: |z| < 0.5\nClose both legs", GREEN)

    ax.set_title("Cross-venue Execution Flow", fontsize=11.5,
                 fontweight="bold", color=NAVY, pad=10)
    save(fig, "ch14-execution-flow")


if __name__ == "__main__":
    chart_leg_risk()
    chart_execution_flow()
