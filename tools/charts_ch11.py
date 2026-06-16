"""Charts for Ch.11 — Entry/Exit State Machine."""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from book_style import (save, style_axes, TEAL, NAVY, RED, GREEN, AMBER, BLUE,
                        GREY, RED_F, GREEN_F, BLUE_F, TEAL_F, AMBER_F)

VIOLET = "#7c3aed"


# ============================================================
# Chart 1 — State Machine Diagram
# ============================================================
def chart_state_machine():
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    # Node definitions: (label, x, y, w, h, fill, text_color)
    nodes = [
        ("NO_TRADE",    0.08, 0.45, 0.14, 0.10, GREY,   "white"),
        ("WATCH",       0.27, 0.45, 0.14, 0.10, AMBER,  "white"),
        ("PAPER_GO",    0.46, 0.45, 0.14, 0.10, BLUE,   "white"),
        ("MANUAL_GO",   0.70, 0.45, 0.14, 0.10, GREEN,  "white"),
        ("DE_RISK",     0.70, 0.28, 0.14, 0.10, RED,    "white"),
        ("EXIT",        0.46, 0.28, 0.14, 0.10, TEAL,   "white"),
        ("INVALIDATED", 0.27, 0.65, 0.14, 0.10, VIOLET, "white"),
    ]

    node_centers = {}
    for label, x, y, w, h, fill, tc in nodes:
        box = FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.015",
            facecolor=fill, edgecolor="white", linewidth=1.5,
            transform=ax.transAxes, zorder=3
        )
        ax.add_patch(box)
        cx, cy = x + w / 2, y + h / 2
        node_centers[label] = (cx, cy)
        ax.text(cx, cy, label, ha="center", va="center",
                fontsize=8.5, fontweight="bold", color=tc,
                transform=ax.transAxes, zorder=4)

    def arrow(src, dst, label, color=NAVY, rad=0.0, label_offset=(0, 0.025),
              src_side=None, dst_side=None):
        """Draw FancyArrowPatch between node centers (axes fraction coords)."""
        sx, sy = node_centers[src]
        dx, dy = node_centers[dst]

        # Adjust endpoints to node edges
        def edge_point(cx, cy, tx, ty, w=0.14, h=0.10, pad=0.012):
            vx, vy = tx - cx, ty - cy
            norm = max(abs(vx), abs(vy)) or 1
            sx_frac = (w / 2 + pad) / abs(vx / norm) if abs(vx) > 1e-9 else 1e9
            sy_frac = (h / 2 + pad) / abs(vy / norm) if abs(vy) > 1e-9 else 1e9
            frac = min(sx_frac, sy_frac)
            return cx + vx / norm * frac, cy + vy / norm * frac

        if src_side is None:
            ex1, ey1 = edge_point(sx, sy, dx, dy)
        else:
            ox = {"left": -0.07, "right": 0.07, "top": 0, "bottom": 0}[src_side]
            oy = {"left": 0, "right": 0, "top": 0.05, "bottom": -0.05}[src_side]
            ex1, ey1 = sx + ox, sy + oy

        if dst_side is None:
            ex2, ey2 = edge_point(dx, dy, sx, sy)
        else:
            ox = {"left": -0.07, "right": 0.07, "top": 0, "bottom": 0}[dst_side]
            oy = {"left": 0, "right": 0, "top": 0.05, "bottom": -0.05}[dst_side]
            ex2, ey2 = dx + ox, dy + oy

        # Convert axes fraction -> display coords for FancyArrowPatch
        trans = ax.transAxes
        p1 = trans.transform((ex1, ey1))
        p2 = trans.transform((ex2, ey2))

        arrowpatch = FancyArrowPatch(
            p1, p2,
            arrowstyle="->, head_width=4, head_length=6",
            color=color, linewidth=1.4,
            connectionstyle=f"arc3,rad={rad}",
            zorder=2,
            transform=None   # display coords
        )
        ax.add_patch(arrowpatch)

        # Label midpoint
        if rad == 0:
            mx = (ex1 + ex2) / 2 + label_offset[0]
            my = (ey1 + ey2) / 2 + label_offset[1]
        else:
            mx = (ex1 + ex2) / 2 + label_offset[0]
            my = (ey1 + ey2) / 2 + label_offset[1]
        ax.text(mx, my, label, ha="center", va="center",
                fontsize=7.5, color=color, transform=ax.transAxes, zorder=5,
                bbox=dict(fc="white", ec="none", pad=1.5, alpha=0.85))

    # Horizontal forward arrows
    arrow("NO_TRADE", "WATCH",     "z > 1.5",      NAVY,  label_offset=(0, 0.035))
    arrow("WATCH",    "PAPER_GO",  "z > 2.0",      BLUE,  label_offset=(0, 0.035))
    arrow("PAPER_GO", "MANUAL_GO", "confirm",       GREEN, label_offset=(0, 0.035))

    # MANUAL_GO → DE_RISK (downward)
    arrow("MANUAL_GO", "DE_RISK", "z > 3 / stop", RED,
          label_offset=(0.06, 0), src_side=None, dst_side=None)

    # DE_RISK → EXIT (left)
    arrow("DE_RISK", "EXIT", "flatten", TEAL, label_offset=(0, 0.035))

    # EXIT → NO_TRADE curved back arrow
    ex_cx, ex_cy = node_centers["EXIT"]
    nt_cx, nt_cy = node_centers["NO_TRADE"]
    p1 = ax.transAxes.transform((ex_cx - 0.02, ex_cy - 0.05))
    p2 = ax.transAxes.transform((nt_cx + 0.02, nt_cy - 0.05))
    back_arrow = FancyArrowPatch(
        p1, p2,
        arrowstyle="->, head_width=4, head_length=6",
        color=NAVY, linewidth=1.3,
        connectionstyle="arc3,rad=0.35",
        zorder=2,
        transform=None
    )
    ax.add_patch(back_arrow)
    ax.text(0.28, 0.14, "done", ha="center", va="center",
            fontsize=7.5, color=NAVY, transform=ax.transAxes, zorder=5,
            bbox=dict(fc="white", ec="none", pad=1.5, alpha=0.85))

    # WATCH → INVALIDATED (upward)
    w_cx, w_cy = node_centers["WATCH"]
    inv_cx, inv_cy = node_centers["INVALIDATED"]
    p1 = ax.transAxes.transform((w_cx, w_cy + 0.05))
    p2 = ax.transAxes.transform((inv_cx, inv_cy - 0.05))
    ax.add_patch(FancyArrowPatch(p1, p2,
        arrowstyle="->, head_width=4, head_length=6",
        color=VIOLET, linewidth=1.3, linestyle="dashed",
        connectionstyle="arc3,rad=0.0",
        zorder=2, transform=None))
    ax.text(w_cx - 0.07, (w_cy + inv_cy) / 2, "coint fail",
            ha="center", va="center", fontsize=7.5, color=VIOLET,
            transform=ax.transAxes, zorder=5,
            bbox=dict(fc="white", ec="none", pad=1.5, alpha=0.85))

    # MANUAL_GO → INVALIDATED
    mg_cx, mg_cy = node_centers["MANUAL_GO"]
    p1 = ax.transAxes.transform((mg_cx - 0.02, mg_cy + 0.05))
    p2 = ax.transAxes.transform((inv_cx + 0.07, inv_cy))
    ax.add_patch(FancyArrowPatch(p1, p2,
        arrowstyle="->, head_width=4, head_length=6",
        color=VIOLET, linewidth=1.3, linestyle="dashed",
        connectionstyle="arc3,rad=-0.2",
        zorder=2, transform=None))
    ax.text(0.65, 0.72, "β shift", ha="center", va="center",
            fontsize=7.5, color=VIOLET, transform=ax.transAxes, zorder=5,
            bbox=dict(fc="white", ec="none", pad=1.5, alpha=0.85))

    # Legend
    legend_x, legend_y = 0.02, 0.90
    ax.text(legend_x, legend_y, "Legend", fontsize=8, fontweight="bold",
            color=NAVY, transform=ax.transAxes)
    items = [
        (NAVY,   "-",  "Normal transition"),
        (VIOLET, "--", "Invalidation"),
    ]
    for i, (c, ls, lbl) in enumerate(items):
        ax.plot([legend_x, legend_x + 0.06],
                [legend_y - 0.07 - i * 0.06, legend_y - 0.07 - i * 0.06],
                color=c, lw=1.5, ls=ls, transform=ax.transAxes)
        ax.text(legend_x + 0.08, legend_y - 0.065 - i * 0.06, lbl,
                fontsize=7.5, color=c, va="center", transform=ax.transAxes)

    ax.set_title("Entry/Exit State Machine — 7 States", fontsize=12, pad=10)
    save(fig, "ch11-state-machine")


# ============================================================
# Chart 2 — OU Path with State Overlays
# ============================================================
def chart_ou_state_path():
    rng = np.random.default_rng(42)
    n = 300
    kappa, theta, sigma = 0.06, 0.0, 0.9

    # Simulate OU
    x = np.empty(n)
    x[0] = theta
    for t in range(1, n):
        x[t] = x[t-1] + kappa * (theta - x[t-1]) + sigma * rng.standard_normal()

    # Rolling z-score (window=40)
    window = 40
    z = np.full(n, np.nan)
    for i in range(window, n):
        seg = x[i - window:i]
        mu, sd = seg.mean(), seg.std()
        if sd > 1e-9:
            z[i] = (x[i] - mu) / sd

    # Determine state for coloring
    state_colors = []
    in_trade = False
    past_paper = False
    for i in range(n):
        if np.isnan(z[i]):
            state_colors.append(("NO_TRADE", GREY))
            continue
        az = abs(z[i])
        if az > 3.0:
            state_colors.append(("DE_RISK", RED))
            in_trade = True
            past_paper = True
        elif az < 0.5 and in_trade:
            state_colors.append(("EXIT", TEAL))
            in_trade = False
            past_paper = False
        elif az >= 2.0 and past_paper:
            state_colors.append(("MANUAL_GO", GREEN))
            in_trade = True
        elif az >= 2.0 and not past_paper:
            state_colors.append(("PAPER_GO", BLUE))
            past_paper = True
            in_trade = True
        elif az >= 1.5:
            state_colors.append(("WATCH", AMBER))
        else:
            state_colors.append(("NO_TRADE", GREY))

    t = np.arange(n)

    fig, axes = plt.subplots(2, 1, figsize=(8.5, 4.5), sharex=True,
                             gridspec_kw={"height_ratios": [2, 1]})

    # --- Top panel: OU path ---
    ax = axes[0]
    ax.set_facecolor(TEAL_F)

    # fill_between for each state
    state_color_map = {
        "NO_TRADE": GREY, "WATCH": AMBER,
        "PAPER_GO": BLUE, "MANUAL_GO": GREEN,
        "DE_RISK":  RED,  "EXIT": TEAL,
    }
    for state, col in state_color_map.items():
        mask = np.array([sc[0] == state for sc in state_colors])
        if mask.any():
            ax.fill_between(t, x.min() - 0.5, x.max() + 0.5,
                            where=mask, alpha=0.15, color=col, step="mid")

    ax.plot(t, x, color=NAVY, lw=1.3, label="OU spread")
    ax.axhline(0, color=TEAL, lw=0.8, ls="--", alpha=0.6)
    ax.set_ylabel("Spread value")
    ax.set_title("OU Spread Path — State Machine Activations")

    # Legend patches
    legend_patches = [
        mpatches.Patch(color=GREY,  alpha=0.6, label="NO_TRADE"),
        mpatches.Patch(color=AMBER, alpha=0.6, label="WATCH"),
        mpatches.Patch(color=BLUE,  alpha=0.6, label="PAPER_GO"),
        mpatches.Patch(color=GREEN, alpha=0.6, label="MANUAL_GO"),
        mpatches.Patch(color=RED,   alpha=0.6, label="DE_RISK"),
        mpatches.Patch(color=TEAL,  alpha=0.6, label="EXIT"),
    ]
    ax.legend(handles=legend_patches, fontsize=7.5, ncol=3, loc="upper right")
    style_axes(ax)

    # --- Bottom panel: z-score ---
    ax2 = axes[1]
    ax2.set_facecolor(BLUE_F)
    ax2.plot(t, z, color=NAVY, lw=1.2)
    ax2.axhline( 1.5, color=GREY,  lw=1.0, ls="--", label="±1.5 (WATCH)")
    ax2.axhline(-1.5, color=GREY,  lw=1.0, ls="--")
    ax2.axhline( 2.0, color=AMBER, lw=1.0, ls="--", label="±2.0 (PAPER_GO)")
    ax2.axhline(-2.0, color=AMBER, lw=1.0, ls="--")
    ax2.axhline( 3.0, color=RED,   lw=1.0, ls="--", label="±3.0 (DE_RISK)")
    ax2.axhline(-3.0, color=RED,   lw=1.0, ls="--")
    ax2.axhline( 0,   color=TEAL,  lw=0.7, ls=":", alpha=0.5)
    ax2.set_ylabel("z-score")
    ax2.set_xlabel("t (bars)")
    ax2.legend(fontsize=7.5, loc="upper right")
    style_axes(ax2)

    fig.subplots_adjust(hspace=0.08)
    save(fig, "ch11-ou-state-path")


# ============================================================
# Chart 3 — Grid Levels on OU Spread
# ============================================================
def chart_grid_levels():
    """Visualise buy/sell grid levels on a mean-reverting OU spread."""
    rng = np.random.default_rng(42)
    n = 200
    kappa, theta, sigma = 0.08, 0.001, 0.003

    # Simulate OU (log-spread style values matching the ch11 example)
    eps = np.empty(n)
    eps[0] = theta
    for i in range(1, n):
        eps[i] = eps[i-1] + kappa * (theta - eps[i-1]) + sigma * rng.standard_normal()

    sigma_stat = eps.std()
    t = np.arange(n)

    fig, ax = plt.subplots(figsize=(7.0, 3.8))
    ax.set_facecolor("#f8fafc")

    # ---- horizontal grid levels ----
    levels = [-3, -2, -1, 0, 1, 2, 3]
    level_colors = {
        3:  RED,   2:  RED,   1:  RED,
        0:  TEAL,
        -1: BLUE, -2: BLUE, -3: BLUE,
    }
    level_ls = {3: (2, 2), 2: (3, 2), 1: (5, 3),
                0: (),
                -1: (5, 3), -2: (3, 2), -3: (2, 2)}

    for lv in levels:
        y_val = theta + lv * sigma_stat
        col = level_colors[lv]
        ls_dash = level_ls[lv]
        ls = (0, ls_dash) if ls_dash else "-"
        lw = 1.4 if lv != 0 else 1.8
        ax.axhline(y_val, color=col, lw=lw, ls=ls, alpha=0.85, zorder=2)
        label = f"+{lv}σ" if lv > 0 else (f"{lv}σ" if lv < 0 else "θ")
        ax.text(-3, y_val, label, fontsize=7.5, color=col,
                va="center", ha="right", fontweight="bold")

    # ---- buy/sell zone fills ----
    sell_top = theta + 3 * sigma_stat
    sell_bot = theta + 1 * sigma_stat
    buy_top  = theta - 1 * sigma_stat
    buy_bot  = theta - 3 * sigma_stat
    ax.axhspan(sell_bot, sell_top, alpha=0.08, color=RED, zorder=1)
    ax.axhspan(buy_bot,  buy_top,  alpha=0.08, color=BLUE, zorder=1)

    # ---- OU path ----
    ax.plot(t, eps, color=NAVY, lw=1.5, zorder=3, label="ε (spread)")

    # ---- buy/sell markers ----
    for i in range(1, n):
        # cross below -1σ going down → BUY
        lv1_down = theta - sigma_stat
        if eps[i] < lv1_down <= eps[i-1]:
            ax.annotate("", xy=(i, eps[i]),
                        xytext=(i, eps[i] - sigma_stat * 0.4),
                        arrowprops=dict(arrowstyle="->, head_width=0.3",
                                        color=BLUE, lw=1.4))
        # cross above +1σ going up → SELL
        lv1_up = theta + sigma_stat
        if eps[i] > lv1_up >= eps[i-1]:
            ax.annotate("", xy=(i, eps[i]),
                        xytext=(i, eps[i] + sigma_stat * 0.4),
                        arrowprops=dict(arrowstyle="->, head_width=0.3",
                                        color=RED, lw=1.4))

    # Zone labels
    ax.text(n * 0.85, theta + 1.6 * sigma_stat, "← Sell zone",
            fontsize=8, color=RED, fontweight="bold", va="center")
    ax.text(n * 0.85, theta - 1.6 * sigma_stat, "← Buy zone",
            fontsize=8, color=BLUE, fontweight="bold", va="center")

    ax.set_xlim(-5, n)
    ax.set_xlabel("t (bars)", fontsize=9.5)
    ax.set_ylabel("ε (spread value)", fontsize=9.5)
    ax.set_title("Grid Levels บน ε — Buy ด้านล่าง (สีน้ำเงิน), Sell ด้านบน (สีแดง)",
                 fontsize=11.5, fontweight="bold", color=NAVY)
    ax.legend(fontsize=9, loc="upper right")
    style_axes(ax)

    fig.subplots_adjust(bottom=0.15, left=0.10)
    save(fig, "ch11-grid-levels")


if __name__ == "__main__":
    chart_state_machine()
    chart_ou_state_path()
    chart_grid_levels()
