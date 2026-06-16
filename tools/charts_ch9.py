"""Charts for Ch.9 — Regime-Switching OU Process."""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, Circle, FancyBboxPatch
from book_style import (save, style_axes, TEAL, NAVY, RED, GREEN, AMBER, BLUE,
                        GREY, RED_F, GREEN_F, BLUE_F, TEAL_F, AMBER_F)


# ============================================================
# Chart 1 — Markov Chain 3-State Diagram
# ============================================================
def chart_markov_chain():
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_facecolor("white")

    # Node positions
    pos = {
        "Normal":  (0.20, 0.45),
        "Stressed": (0.50, 0.75),
        "Broken":  (0.80, 0.45),
    }
    node_r = 0.10   # radius in data coords

    # ---- Draw nodes ----
    node_styles = {
        "Normal":   dict(facecolor=GREEN_F, edgecolor=GREEN,  lw=2.5),
        "Stressed": dict(facecolor=AMBER_F, edgecolor=AMBER,  lw=2.5),
        "Broken":   dict(facecolor=RED_F,   edgecolor=RED,    lw=2.5),
    }
    node_text_colors = {
        "Normal": GREEN, "Stressed": AMBER, "Broken": RED,
    }
    node_sub = {
        "Normal":   "κ=2.0, σ=small\nเทรดได้",
        "Stressed": "κ=0.8, σ↑\nลด size 50%",
        "Broken":   "κ≈0, σ↑↑\nหยุดเทรด",
    }

    for name, (cx, cy) in pos.items():
        circ = plt.Circle((cx, cy), node_r, transform=ax.transData,
                          **node_styles[name], zorder=3)
        ax.add_patch(circ)
        ax.text(cx, cy + 0.015, name, ha="center", va="center",
                fontsize=9.5, fontweight="bold", color=node_text_colors[name],
                zorder=4)
        ax.text(cx, cy - 0.028, node_sub[name], ha="center", va="center",
                fontsize=6.5, color=NAVY, zorder=4, linespacing=1.4)

    # ---- Helper: draw arrow between two nodes ----
    def arrow(src, dst, label, color, rad=0.0, label_shift=(0, 0), fontsize=7.5):
        sx, sy = pos[src]
        dx, dy = pos[dst]
        # Offset endpoints to node boundary
        vec = np.array([dx - sx, dy - sy], dtype=float)
        dist = np.linalg.norm(vec)
        unit = vec / dist
        # Start just outside src node, end just outside dst node
        start = np.array([sx, sy]) + unit * (node_r + 0.005)
        end   = np.array([dx, dy]) - unit * (node_r + 0.005)

        ap = FancyArrowPatch(
            start, end,
            connectionstyle=f"arc3,rad={rad}",
            arrowstyle="-|>",
            mutation_scale=12,
            color=color,
            lw=1.5,
            zorder=2,
        )
        ax.add_patch(ap)
        # Label at midpoint
        mid = (start + end) / 2
        # Perpendicular nudge for curved arrows
        perp = np.array([-unit[1], unit[0]])
        nudge = perp * rad * 0.4
        lx = mid[0] + nudge[0] + label_shift[0]
        ly = mid[1] + nudge[1] + label_shift[1]
        ax.text(lx, ly, label, ha="center", va="center",
                fontsize=fontsize, color=color, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.8),
                zorder=5)

    # ---- Arrows between nodes ----
    # Normal → Stressed
    arrow("Normal", "Stressed", "0.05/day", AMBER, rad=-0.25,
          label_shift=(-0.04, 0.02))
    # Stressed → Normal
    arrow("Stressed", "Normal", "0.40/day", GREEN, rad=-0.25,
          label_shift=(0.04, -0.02))
    # Stressed → Broken
    arrow("Stressed", "Broken", "0.10/day", RED, rad=-0.25,
          label_shift=(0.04, 0.02))
    # Broken → Stressed
    arrow("Broken", "Stressed", "0.20/day", AMBER, rad=-0.25,
          label_shift=(-0.04, -0.02))
    # Normal → Broken (rare, bottom curve)
    arrow("Normal", "Broken", "0.01/day\n(rare)", RED, rad=0.35,
          label_shift=(0, -0.04), fontsize=6.5)
    # Broken → Normal (very rare, bottom curve)
    arrow("Broken", "Normal", "0.005/day", GREY, rad=0.35,
          label_shift=(0, -0.08), fontsize=6.5)

    # ---- Self-loops ----
    def self_loop(name, angle_deg, color, label, label_offset=(0, 0)):
        cx, cy = pos[name]
        angle = np.deg2rad(angle_deg)
        # Loop arc: draw as circle patch
        loop_cx = cx + np.cos(angle) * (node_r * 1.55)
        loop_cy = cy + np.sin(angle) * (node_r * 1.55)
        loop_r  = node_r * 0.45
        loop = plt.Circle((loop_cx, loop_cy), loop_r,
                           fill=False, edgecolor=color, lw=1.3, zorder=2,
                           linestyle="-")
        ax.add_patch(loop)
        lx = loop_cx + np.cos(angle) * (loop_r + 0.025) + label_offset[0]
        ly = loop_cy + np.sin(angle) * (loop_r + 0.025) + label_offset[1]
        ax.text(lx, ly, label, ha="center", va="center",
                fontsize=6.5, color=color, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.8),
                zorder=5)

    self_loop("Normal",   200, GREEN, "0.94",  label_offset=(-0.03, -0.01))
    self_loop("Stressed", 90,  AMBER, "0.50",  label_offset=(0, 0.02))
    self_loop("Broken",   340, RED,   "0.75",  label_offset=(0.03, -0.01))

    ax.set_title("Regime Markov Chain — 3 States", fontsize=11, fontweight="bold",
                 color=NAVY, pad=8)

    save(fig, "ch9-markov-chain")


# ============================================================
# Chart 2 — Regime-Colored OU Timeline
# ============================================================
def chart_regime_timeline():
    rng = np.random.default_rng(12)
    n = 400
    kappa = 0.05
    theta = 0.0
    sigma = 0.8
    dt = 1.0

    # Simulate OU with regime-dependent σ
    x = np.empty(n)
    x[0] = theta
    for t in range(1, n):
        if t < 120:
            s = sigma              # Normal
        elif t < 200:
            s = sigma * 2.0        # Stressed — double σ
        elif t < 260:
            s = sigma * 1.5        # Broken — reduced reversion + drift
        elif t < 330:
            s = sigma * 2.0        # Stressed again
        else:
            s = sigma              # Normal

        # Broken regime: reduce kappa so spread diverges
        if 200 <= t < 260:
            k_eff = kappa * 0.05
            drift = 0.02           # slight upward drift
        else:
            k_eff = kappa
            drift = 0.0

        x[t] = (x[t-1]
                + k_eff * (theta - x[t-1]) * dt
                + drift
                + s * rng.standard_normal() * np.sqrt(dt))

    t = np.arange(n)
    sd_stat = sigma / np.sqrt(2 * kappa)  # stationary std under Normal params

    fig, ax = plt.subplots(figsize=(7.4, 3.5))
    ax.set_facecolor("white")

    # Background fills per regime
    regime_bands = [
        (0,   120, GREEN_F, "Normal",   GREEN),
        (120, 200, AMBER_F, "Stressed", AMBER),
        (200, 260, RED_F,   "Broken",   RED),
        (260, 330, AMBER_F, "Stressed", AMBER),
        (330, n,   GREEN_F, "Normal",   GREEN),
    ]
    for t0, t1, fc, label, ec in regime_bands:
        ax.axvspan(t0, t1 - 1, facecolor=fc, alpha=1.0, zorder=0)

    # Reference lines
    ax.axhline(theta,     color=TEAL,  lw=1.3, ls="--", alpha=0.9, label=r"$\theta=0$", zorder=1)
    ax.axhline(+2*sd_stat, color=AMBER, lw=0.9, ls=":",  alpha=0.7, label="±2σ",        zorder=1)
    ax.axhline(-2*sd_stat, color=AMBER, lw=0.9, ls=":",  alpha=0.7,                      zorder=1)

    # OU path
    ax.plot(t, x, color=NAVY, lw=1.5, zorder=2, label=r"$\varepsilon_t$ (OU)")

    # Legend patches for regimes
    legend_patches = [
        mpatches.Patch(facecolor=GREEN_F, edgecolor=GREEN, lw=1.5, label="Normal"),
        mpatches.Patch(facecolor=AMBER_F, edgecolor=AMBER, lw=1.5, label="Stressed"),
        mpatches.Patch(facecolor=RED_F,   edgecolor=RED,   lw=1.5, label="Broken"),
    ]

    ax.set_xlabel("t (bars)", color=NAVY)
    ax.set_ylabel(r"$\varepsilon$", color=NAVY)
    ax.set_title("Spread Colored by Hidden Regime State", fontsize=11, fontweight="bold", color=NAVY)
    ax.set_xlim(0, n - 1)

    # Two legend groups
    l1 = ax.legend(handles=legend_patches, loc="upper left", fontsize=8.5, framealpha=0.9)
    ax.add_artist(l1)
    ax.legend(loc="upper right", fontsize=8.5, framealpha=0.9)

    style_axes(ax)
    save(fig, "ch9-regime-timeline")


if __name__ == "__main__":
    chart_markov_chain()
    chart_regime_timeline()
