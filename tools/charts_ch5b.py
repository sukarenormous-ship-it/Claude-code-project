"""Supplemental charts for Ch.5 — 4 remaining inline SVG replacements."""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from book_style import (save, style_axes, TEAL, NAVY, RED, GREEN, AMBER, BLUE,
                        GREY, RED_F, GREEN_F, BLUE_F, TEAL_F, AMBER_F, SOFT)

# ============================================================
# Chart 1 — Scatter Types (4 panels 2×2)
# ============================================================
def chart_scatter_types():
    rng = np.random.default_rng(42)
    n = 60

    fig, axes = plt.subplots(2, 2, figsize=(8.5, 4.0))

    # --- Top-left: Cointegrated (tight linear) ---
    ax = axes[0, 0]
    ax.set_facecolor(GREEN_F)
    x_tl = rng.uniform(0, 10, n)
    y_tl = 1.5 * x_tl + rng.normal(0, 0.35, n)
    m, b = np.polyfit(x_tl, y_tl, 1)
    ax.scatter(x_tl, y_tl, color=GREEN, s=18, alpha=0.75, zorder=3)
    xs = np.array([x_tl.min(), x_tl.max()])
    ax.plot(xs, m * xs + b, color=NAVY, lw=1.6, zorder=4)
    ax.set_title("Cointegrated ✓", color=NAVY, fontsize=10.5, fontweight="bold")
    ax.set_xlabel("P_B", fontsize=8.5)
    ax.set_ylabel("P_A", fontsize=8.5)
    style_axes(ax)

    # --- Top-right: Loose / noisy scatter ---
    ax = axes[0, 1]
    ax.set_facecolor(AMBER_F)
    x_tr = rng.uniform(0, 10, n)
    y_tr = 1.2 * x_tr + rng.normal(0, 3.2, n)
    m2, b2 = np.polyfit(x_tr, y_tr, 1)
    ax.scatter(x_tr, y_tr, color=AMBER, s=18, alpha=0.75, zorder=3)
    xs2 = np.array([x_tr.min(), x_tr.max()])
    ax.plot(xs2, m2 * xs2 + b2, color=NAVY, lw=1.6, zorder=4, ls="--", alpha=0.6)
    ax.set_title("Loose Spread (noisy)", color=NAVY, fontsize=10.5, fontweight="bold")
    ax.set_xlabel("P_B", fontsize=8.5)
    ax.set_ylabel("P_A", fontsize=8.5)
    style_axes(ax)

    # --- Bottom-left: Spurious I(1)+I(1) (two random walks) ---
    ax = axes[1, 0]
    ax.set_facecolor(RED_F)
    rw_b = np.cumsum(rng.normal(0, 1, n))
    rw_a = np.cumsum(rng.normal(0, 1, n))
    # Shift so both start around 0
    rw_b -= rw_b[0]
    rw_a -= rw_a[0]
    m3, b3 = np.polyfit(rw_b, rw_a, 1)
    ax.scatter(rw_b, rw_a, color=RED, s=18, alpha=0.75, zorder=3)
    xs3 = np.array([rw_b.min(), rw_b.max()])
    ax.plot(xs3, m3 * xs3 + b3, color=NAVY, lw=1.6, ls="--", alpha=0.6, zorder=4)
    ax.set_title("Spurious: I(1)+I(1)", color=NAVY, fontsize=10.5, fontweight="bold")
    ax.set_xlabel("P_B", fontsize=8.5)
    ax.set_ylabel("P_A", fontsize=8.5)
    style_axes(ax)

    # --- Bottom-right: No relationship (pure noise) ---
    ax = axes[1, 1]
    ax.set_facecolor(TEAL_F)
    x_br = rng.uniform(0, 10, n)
    y_br = rng.uniform(0, 10, n)
    ax.scatter(x_br, y_br, color=TEAL, s=18, alpha=0.75, zorder=3)
    ax.set_title("No Relationship", color=NAVY, fontsize=10.5, fontweight="bold")
    ax.set_xlabel("P_B", fontsize=8.5)
    ax.set_ylabel("P_A", fontsize=8.5)
    style_axes(ax)

    fig.suptitle("4 รูปทรง scatter — อันไหนเทรดได้ อันไหนต้องระวัง",
                 fontsize=11.5, fontweight="bold", color=NAVY, y=1.01)
    fig.subplots_adjust(hspace=0.52, wspace=0.38, top=0.88, bottom=0.12)
    save(fig, "ch5-scatter-types")


# ============================================================
# Chart 2 — VECM Adjustment Diagram
# ============================================================
def chart_vecm_adjustment():
    n = 80
    t = np.arange(n)

    rng = np.random.default_rng(7)

    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.8))

    # --- Left panel: A adjusts (alpha_A < 0) ---
    ax = axes[0]
    ax.set_facecolor(BLUE_F)

    # Equilibrium at 0; P_B stays flat (slight noise), P_A diverges then snaps back
    pb_l = np.zeros(n) + rng.normal(0, 0.04, n)  # B stays near 0
    pa_l = np.zeros(n)
    # Diverge from bar 15 to 30, then correct
    for i in range(1, n):
        if i < 15:
            pa_l[i] = pa_l[i-1] + rng.normal(0, 0.05)
        elif i < 30:
            pa_l[i] = pa_l[i-1] + 0.12 + rng.normal(0, 0.04)  # diverge up
        else:
            # mean-revert toward 0
            pa_l[i] = pa_l[i-1] - 0.12 * pa_l[i-1] + rng.normal(0, 0.04)

    ax.plot(t, pa_l, color=TEAL, lw=2.0, label="P_A (adjusts)")
    ax.plot(t, pb_l, color=NAVY, lw=2.0, label="P_B (leader)", ls="--")
    ax.axhline(0, color=GREY, lw=1.0, ls=":", alpha=0.6)
    ax.axvline(15, color=AMBER, lw=1.0, ls="--", alpha=0.5)
    ax.axvline(30, color=RED, lw=1.0, ls="--", alpha=0.5)
    ax.set_title("α_A < 0: P_A adjusts\n(Short A when A too high)", fontsize=9.5,
                 color=NAVY, fontweight="bold")
    ax.set_xlabel("t (bars)", fontsize=8.5)
    ax.set_ylabel("ราคา", fontsize=8.5)
    ax.legend(fontsize=8, loc="upper left")
    style_axes(ax)

    # --- Right panel: B adjusts (alpha_B > 0) ---
    ax = axes[1]
    ax.set_facecolor(AMBER_F)

    pa_r = np.zeros(n) + rng.normal(0, 0.04, n)  # A stays near 0
    pb_r = np.zeros(n)
    for i in range(1, n):
        if i < 15:
            pb_r[i] = pb_r[i-1] + rng.normal(0, 0.05)
        elif i < 30:
            pb_r[i] = pb_r[i-1] - 0.12 + rng.normal(0, 0.04)  # diverge down
        else:
            pb_r[i] = pb_r[i-1] - 0.12 * pb_r[i-1] + rng.normal(0, 0.04)  # correct

    ax.plot(t, pa_r, color=NAVY, lw=2.0, label="P_A (leader)", ls="--")
    ax.plot(t, pb_r, color=AMBER, lw=2.0, label="P_B (adjusts)")
    ax.axhline(0, color=GREY, lw=1.0, ls=":", alpha=0.6)
    ax.axvline(15, color=AMBER, lw=1.0, ls="--", alpha=0.5)
    ax.axvline(30, color=RED, lw=1.0, ls="--", alpha=0.5)
    ax.set_title("α_B > 0: P_B adjusts\n(Long B when B too low)", fontsize=9.5,
                 color=NAVY, fontweight="bold")
    ax.set_xlabel("t (bars)", fontsize=8.5)
    ax.legend(fontsize=8, loc="upper right")
    style_axes(ax)

    fig.suptitle("VECM: α coefficient determines which asset adjusts",
                 fontsize=11.5, fontweight="bold", color=NAVY, y=1.02)
    fig.subplots_adjust(wspace=0.35, top=0.85, bottom=0.18)
    save(fig, "ch5-vecm-adjustment")


# ============================================================
# Chart 3 — Crossing Rate E[X] = (1/π)·arccos(φ)
# ============================================================
def chart_crossing_rate():
    phi = np.linspace(0.01, 0.999, 600)
    e_cross = (1 / np.pi) * np.arccos(phi)

    fig, ax = plt.subplots(figsize=(7.0, 3.5))
    ax.set_facecolor(TEAL_F)

    # Fill below curve
    ax.fill_between(phi, 0, e_cross, color=RED_F, alpha=0.85, zorder=1)

    # Main curve
    ax.plot(phi, e_cross, color=TEAL, lw=2.2, zorder=3,
            label="E[Crossings] = (1/π)·arccos(φ)")

    # Vertical lines
    phi_vals = [0.5, 0.9, 0.98]
    hl_labels = ["half-life≈1.4", "half-life≈6.6", "half-life≈34.3"]
    vline_colors = [GREEN, AMBER, RED]
    for pv, hl, vc in zip(phi_vals, hl_labels, vline_colors):
        ec_val = (1 / np.pi) * np.arccos(pv)
        ax.axvline(pv, color=vc, lw=1.5, ls="--", alpha=0.8, zorder=2)
        ax.text(pv + 0.005, ec_val + 0.010, hl, fontsize=8, color=vc,
                fontweight="bold", va="bottom")

    # Sweet spot shading for BTC/ETH typical range φ=0.85-0.95
    ax.axvspan(0.85, 0.95, alpha=0.18, color=AMBER, zorder=1)
    ax.text(0.90, 0.28, "BTC/ETH\ntypical range", fontsize=8, color=AMBER,
            ha="center", fontweight="bold")

    ax.set_xlabel("φ (AR(1) coefficient)", fontsize=10, color=NAVY)
    ax.set_ylabel("E[Mean Crossings per bar]", fontsize=10, color=NAVY)
    ax.set_title("E[Mean Crossings per bar] = (1/π)·arccos(φ)",
                 fontsize=11.5, fontweight="bold", color=NAVY)
    ax.set_xlim(0, 1.0)
    ax.set_ylim(bottom=-0.005)
    ax.legend(fontsize=9, loc="upper right")
    style_axes(ax)

    fig.subplots_adjust(bottom=0.18)
    save(fig, "ch5-crossing-rate")


# ============================================================
# Chart 4 — Pair Selection Funnel (horizontal)
# ============================================================
def chart_pair_funnel():
    fig, ax = plt.subplots(figsize=(7.0, 4.5))
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    stages = [
        ("100+ คู่ทั้งหมด",
         1.00, BLUE, "#1d4ed8"),
        ("Correlation > 0.85  →  ~30",
         0.70, TEAL, "#0f766e"),
        ("ADF p < 0.05  →  ~15",
         0.50, GREEN, "#15803d"),
        ("Half-life 5–30 bars  →  ~8",
         0.35, AMBER, "#b45309"),
        ("Sharpe > 1.0  →  3–5 คู่",
         0.20, RED, "#b91c1c"),
    ]

    n = len(stages)
    row_height = 0.13
    gap = 0.05
    total_h = n * row_height + (n - 1) * gap
    start_y = (1.0 - total_h) / 2.0

    colors_fill = [BLUE_F, TEAL_F, GREEN_F, AMBER_F, RED_F]

    for i, (label, width, edge_color, text_color) in enumerate(stages):
        y = start_y + (n - 1 - i) * (row_height + gap)
        x_left = (1.0 - width) / 2.0
        rect = mpatches.FancyBboxPatch(
            (x_left, y), width, row_height,
            boxstyle="round,pad=0.015",
            facecolor=colors_fill[i],
            edgecolor=edge_color,
            linewidth=2.0,
            transform=ax.transAxes,
            zorder=2
        )
        ax.add_patch(rect)
        ax.text(0.5, y + row_height / 2, label,
                ha="center", va="center",
                fontsize=9.5, fontweight="bold",
                color=text_color,
                transform=ax.transAxes, zorder=3)

        # Draw downward arrow between stages
        if i < n - 1:
            arrow_y_top = y
            arrow_y_bot = y - gap
            ax.annotate("",
                        xy=(0.5, arrow_y_bot),
                        xytext=(0.5, arrow_y_top),
                        xycoords="axes fraction",
                        textcoords="axes fraction",
                        arrowprops=dict(arrowstyle="->, head_width=0.3, head_length=0.5",
                                        color=GREY, lw=1.5),
                        zorder=4)

    ax.set_title("Pair Selection Funnel — Stage-by-Stage Filter",
                 fontsize=12, fontweight="bold", color=NAVY, pad=10)
    save(fig, "ch5-pair-funnel")


if __name__ == "__main__":
    chart_scatter_types()
    chart_vecm_adjustment()
    chart_crossing_rate()
    chart_pair_funnel()
