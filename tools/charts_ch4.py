"""Charts for Ch.4 — Hedge Ratio β (Rolling OLS vs Kalman, epsilon strategies, pipeline).

SVG mapping (line → chart name):
  515  → ch4-rolling-vs-kalman   (Rolling OLS vs Kalman β over time)
  652  → ch4-epsilon-strategy    (two-panel: Kalman ε flat vs OLS ε mean-reverting)
  798  → ch4-pipeline            (6-box flowchart: Pair→Transform→Beta→ε→Diag→Exec)
  927  → ch4-correct-vs-wrong-beta (two-panel: correct β vs wrong β residuals)
  1091 → ch4-beta-roadmap        (staircase: β=1 → OLS → Rolling → Kalman)
"""
import numpy as np
from book_style import (save, style_axes, TEAL, NAVY, RED, GREEN, AMBER, BLUE,
                        GREY, RED_F, GREEN_F, BLUE_F, TEAL_F, AMBER_F)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch


# ============================================================
# Chart 1 — Rolling OLS vs Kalman β over time
# SVG at line 515 — "β ตามเวลา: Rolling OLS vs Kalman Filter"
# ============================================================
def chart_rolling_vs_kalman():
    rng = np.random.default_rng(42)
    n = 50
    t = np.arange(n)

    # True β drifts slowly
    true_beta = 1.003 + 0.002 * np.sin(2 * np.pi * t / 40)

    # Rolling OLS: noisier, sensitive to window
    rolling_beta = true_beta + rng.normal(0, 0.025, n)
    # Add a sudden jump around t=15 (window boundary effect / regime shift)
    rolling_beta[14:18] += 0.045

    # Kalman β: smooth, close to true
    kalman_beta = np.zeros(n)
    kalman_beta[0] = 1.003
    for i in range(1, n):
        kalman_beta[i] = (0.92 * kalman_beta[i - 1]
                          + 0.08 * true_beta[i]
                          + rng.normal(0, 0.003))

    fig, ax = plt.subplots(figsize=(7.2, 3.5))

    ax.axhline(1.003, color=GREY, lw=1.0, ls="--", alpha=0.7, label="Reference β = 1.003")
    ax.plot(t, rolling_beta, color=BLUE, lw=1.8, ls="--", alpha=0.85,
            label="Rolling OLS 30d (noisy)")
    ax.plot(t, kalman_beta, color=TEAL, lw=2.5, label="Kalman Filter (smooth)")

    # Highlight divergence region
    ax.axvspan(13, 19, alpha=0.15, color=RED, label="OLS window-boundary divergence")
    ax.annotate("regime shift", xy=(16, rolling_beta[16]),
                xytext=(21, rolling_beta[16] + 0.022),
                fontsize=8.5, color=RED,
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.0))

    ax.set_xlabel("t (days)", color=NAVY)
    ax.set_ylabel("β", color=NAVY)
    ax.set_title("β Over Time: Rolling OLS vs Kalman Filter")
    ax.set_xlim(0, n - 1)
    ax.legend(fontsize=9, loc="upper right")
    style_axes(ax)
    save(fig, "ch4-rolling-vs-kalman")


# ============================================================
# Chart 2 — Two-panel: Kalman ε flat vs OLS ε mean-reverting
# SVG at line 652 — "ε_t ตามเวลา: เป้าหมายต่างกันตามกลยุทธ์"
# ============================================================
def chart_epsilon_strategy():
    rng = np.random.default_rng(7)
    n = 60
    t = np.arange(n)

    # Kalman ε: nearly flat, tiny noise (funding harvest)
    raw_noise = rng.normal(0, 0.4, n)
    kernel = np.ones(8) / 8
    kalman_eps = np.convolve(raw_noise, kernel, mode='same') * 0.5

    # OLS ε: mean-reverting OU process (spread arb)
    theta = 0.0
    kappa = 0.12
    sigma = 1.2
    ols_eps = np.zeros(n)
    ols_eps[0] = theta
    for i in range(1, n):
        ols_eps[i] = (ols_eps[i - 1]
                      + kappa * (theta - ols_eps[i - 1])
                      + rng.normal(0, sigma))

    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.5))

    # ---- Left panel: Kalman / Funding Harvest ----
    ax_l = axes[0]
    ax_l.set_facecolor(TEAL_F)
    ax_l.axhline(0, color=GREY, lw=1.0, ls="--", alpha=0.7)
    ax_l.plot(t, kalman_eps, color=TEAL, lw=2.2)
    ax_l.set_xlabel("t", color=NAVY)
    ax_l.set_ylabel(r"$\varepsilon_t$", color=NAVY)
    ax_l.set_title("Kalman β — Funding Harvest\n"
                   r"$\varepsilon_t \approx 0$  (price risk ≈ 0)",
                   color=TEAL, fontsize=10)
    ax_l.set_ylim(-4, 4)
    style_axes(ax_l)

    # ---- Right panel: OLS / Spread Arbitrage ----
    ax_r = axes[1]
    ax_r.set_facecolor(BLUE_F)
    ax_r.axhline(theta, color=GREY, lw=1.0, ls="--", alpha=0.7, label=r"$\theta$")

    sd = ols_eps.std()
    entry_mask = ols_eps < -1.5 * sd
    exit_mask  = ols_eps >  1.5 * sd

    ax_r.plot(t, ols_eps, color=BLUE, lw=2.2)
    ax_r.scatter(t[entry_mask], ols_eps[entry_mask], color=RED, s=55, zorder=6,
                 marker="o", ec="white", lw=0.8, label="Entry (short spread)")
    ax_r.scatter(t[exit_mask], ols_eps[exit_mask], color=GREEN, s=55, zorder=6,
                 marker="o", ec="white", lw=0.8, label="Exit (spread reverts)")
    ax_r.set_xlabel("t", color=NAVY)
    ax_r.set_ylabel(r"$\varepsilon_t$", color=NAVY)
    ax_r.set_title("OLS β — Spread Arbitrage\n"
                   r"$\varepsilon_t$ mean-reverting → trading signals",
                   color=BLUE, fontsize=10)
    ax_r.legend(fontsize=8.5, loc="upper right")
    style_axes(ax_r)

    fig.suptitle(r"$\varepsilon_t$ Goals: Funding Harvest (Kalman) vs Spread Arb (OLS)",
                 fontsize=11.5, fontweight="bold", color=NAVY, y=1.03)
    fig.tight_layout()
    save(fig, "ch4-epsilon-strategy")


# ============================================================
# Chart 3 — Pipeline flowchart: 6 boxes with arrows
# SVG at line 798 — "β อยู่ตรงไหน — Pipeline การสร้าง Synthetic Process"
# ============================================================
def chart_pipeline():
    fig, ax = plt.subplots(figsize=(9.5, 3.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    steps = [
        # (title, detail, ref_label, fill, edge_color, text_color, is_current)
        ("1. Pair\nSelection",   "A, B share\nmechanism",    "Ch. 5",        BLUE_F,  "#93c5fd", "#1e40af", False),
        ("2. Transform\nF(A), F(B)", "price / log\n/ basis", "§4.6.1",       BLUE_F,  "#93c5fd", "#1e40af", False),
        ("3. Beta\nHedge Ratio", "OLS / Kalman\nRolling",    "Ch. 4",        TEAL_F,  TEAL,      TEAL,      True),
        ("4. Epsilon\nε=F(A)−βF(B)", "new synthetic\nprocess","Ch. 5–6",     GREEN_F, "#86efac", "#166534", False),
        ("5. Diagnostics\nStationary?", "ADF / KPSS\nhalf-life", "Ch. 5–6",  GREEN_F, "#86efac", "#166534", False),
        ("6. Execution\nViable?", "after cost\nbreakeven",   "Ch. 19",       GREEN_F, "#86efac", "#166534", False),
    ]

    box_w   = 1.45
    box_h   = 1.60
    gap     = 0.195
    start_x = 0.12
    y_c     = 1.50   # vertical centre

    for i, (title, detail, ref, fill, edge, tc, is_cur) in enumerate(steps):
        x   = start_x + i * (box_w + gap)
        lw  = 2.5 if is_cur else 1.5

        fancy = FancyBboxPatch((x, y_c - box_h / 2), box_w, box_h,
                               boxstyle="round,pad=0.08",
                               facecolor=fill, edgecolor=edge, linewidth=lw,
                               zorder=2)
        ax.add_patch(fancy)

        ax.text(x + box_w / 2, y_c + 0.42, title,
                ha="center", va="center", fontsize=8.5,
                fontweight="bold", color=tc, multialignment="center", zorder=3)

        ax.text(x + box_w / 2, y_c - 0.08, detail,
                ha="center", va="center", fontsize=7.5,
                color=NAVY, multialignment="center", zorder=3)

        ax.text(x + box_w / 2, y_c - 0.56, ref,
                ha="center", va="center", fontsize=7.0,
                color=TEAL if is_cur else GREY,
                fontweight="bold" if is_cur else "normal",
                fontstyle="normal" if is_cur else "italic",
                multialignment="center", zorder=3)

        # "This Chapter" badge on the highlighted box
        if is_cur:
            badge = FancyBboxPatch((x + box_w / 2 - 0.36, y_c + 0.74), 0.72, 0.22,
                                   boxstyle="round,pad=0.04",
                                   facecolor=TEAL, edgecolor=TEAL, zorder=4)
            ax.add_patch(badge)
            ax.text(x + box_w / 2, y_c + 0.85, "This Chapter",
                    ha="center", va="center", fontsize=6.5,
                    fontweight="bold", color="white", zorder=5)

        # Arrow to next box
        if i < len(steps) - 1:
            x_tail = x + box_w + 0.02
            x_head = x_tail + gap - 0.04
            ax.annotate("",
                        xy=(x_head, y_c), xytext=(x_tail, y_c),
                        arrowprops=dict(arrowstyle="-|>",
                                        color=NAVY, lw=1.5,
                                        mutation_scale=10),
                        zorder=3)

    ax.set_title("Where β Fits — Pipeline for Building a Synthetic Process",
                 fontsize=12, fontweight="bold", color=NAVY, pad=14)
    save(fig, "ch4-pipeline")


# ============================================================
# Chart 4 — Two-panel: correct β vs wrong β residuals
# SVG at line 927 — "β ถูก vs β ผิด — residual หน้าตาต่างกัน"
# ============================================================
def chart_correct_vs_wrong_beta():
    rng = np.random.default_rng(55)
    n = 60
    t = np.arange(n)

    # Common trending market factor (BTC ↑)
    market = np.cumsum(rng.normal(0.30, 1.0, n))

    # True β = 1.8  →  A moves ~1.8× B's factor exposure
    noise_a = rng.normal(0, 0.5, n)
    noise_b = rng.normal(0, 0.5, n)
    A = market + noise_a
    B = market / 1.8 + noise_b

    # Correct β = 1.8 → cancels market factor, ε mean-reverts
    eps_correct = A - 1.8 * B
    # Wrong β = 1.0 → residual market exposure remains, ε drifts
    eps_wrong   = A - 1.0 * B

    # Scale for reference overlay
    mkt_norm = market / market.std() * eps_wrong.std() * 0.38

    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.5))

    # ---- Left: correct β ----
    ax_l = axes[0]
    ax_l.set_facecolor(TEAL_F)
    ax_l.axhline(0, color=GREY, lw=1.0, ls="--", alpha=0.8, label="θ = 0")
    ax_l.plot(t, mkt_norm, color=GREY, lw=1.2, ls=":", alpha=0.4, label="BTC ↑ (ref)")
    ax_l.plot(t, eps_correct, color=TEAL, lw=2.2,
              label=r"$\varepsilon_t = A - 1.8B$")
    ax_l.set_xlabel("t", color=NAVY)
    ax_l.set_ylabel(r"$\varepsilon_t$", color=NAVY)
    ax_l.set_title("Correct β — ε cancels common factor\n"
                   "mean-reverts around 0",
                   color=TEAL, fontsize=10)
    ax_l.legend(fontsize=8.5)
    style_axes(ax_l)

    # ---- Right: wrong β ----
    ax_r = axes[1]
    ax_r.set_facecolor(RED_F)
    ax_r.axhline(0, color=GREY, lw=1.0, ls="--", alpha=0.8, label="θ = 0")
    ax_r.plot(t, mkt_norm, color=GREY, lw=1.2, ls=":", alpha=0.4, label="BTC ↑ (ref)")
    ax_r.plot(t, eps_wrong, color=RED, lw=2.2,
              label=r"$\varepsilon_t = A - 1.0B$ (wrong β)")
    ax_r.set_xlabel("t", color=NAVY)
    ax_r.set_ylabel(r"$\varepsilon_t$", color=NAVY)
    ax_r.set_title("Wrong β — ε retains market exposure\n"
                   "drifts with BTC → hidden directional bet",
                   color=RED, fontsize=10)
    ax_r.legend(fontsize=8.5)
    style_axes(ax_r)

    fig.suptitle("Correct vs Wrong β — Residual Behavior",
                 fontsize=12, fontweight="bold", color=NAVY, y=1.03)
    fig.tight_layout()
    save(fig, "ch4-correct-vs-wrong-beta")


# ============================================================
# Chart 5 — Staircase roadmap: β=1 → OLS → Rolling → Kalman
# SVG at line 1091 — "ขั้นบันได β — ไต่จาก baseline ไป dynamic"
# ============================================================
def chart_beta_roadmap():
    fig, ax = plt.subplots(figsize=(8.5, 3.8))
    ax.set_xlim(0, 9)
    ax.set_ylim(0, 4.6)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    # Baseline complexity axis
    ax.annotate("", xy=(8.8, 0.45), xytext=(0.2, 0.45),
                arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.8, mutation_scale=12))
    ax.text(4.5, 0.17,
            "Complexity + Overfitting Risk  →",
            ha="center", va="center", fontsize=9.5, color=RED, fontweight="bold")

    # 4 staircase boxes — each higher
    boxes = [
        # (x, y_bottom, label, sublabel, fill, edge, text_color)
        (0.3,  0.7,  "1.  β = 1",       "Baseline\nStart Here",       GREEN_F, GREEN,  "#166534"),
        (2.5,  1.3,  "2.  OLS β",        "Compare vs β=1\nBetter ε?",   BLUE_F,  BLUE,   "#1e40af"),
        (4.7,  1.9,  "3.  Rolling OLS",  "If β drifts\nwith regime",    AMBER_F, AMBER,  "#92400e"),
        (6.9,  2.5,  "4.  Kalman β",     "Later — when\ndata is enough", TEAL_F, TEAL,   TEAL),
    ]

    bw = 1.80   # box width
    bh = 0.90   # box height

    for i, (bx, by, label, sub, fill, edge, tc) in enumerate(boxes):
        fancy = FancyBboxPatch((bx, by), bw, bh,
                               boxstyle="round,pad=0.10",
                               facecolor=fill, edgecolor=edge, linewidth=1.8,
                               zorder=2)
        ax.add_patch(fancy)
        ax.text(bx + bw / 2, by + bh * 0.63, label,
                ha="center", va="center", fontsize=11,
                fontweight="bold", color=tc, zorder=3)
        ax.text(bx + bw / 2, by + bh * 0.22, sub,
                ha="center", va="center", fontsize=8,
                color=NAVY, multialignment="center", zorder=3)

        # Dashed riser arrow to next box
        if i < len(boxes) - 1:
            nx, ny = boxes[i + 1][0], boxes[i + 1][1]
            ax.annotate("",
                        xy=(nx + 0.10, ny + bh * 0.50),
                        xytext=(bx + bw - 0.10, by + bh * 0.50),
                        arrowprops=dict(arrowstyle="-|>", color=GREY,
                                        lw=1.5, mutation_scale=9,
                                        connectionstyle="arc3,rad=-0.30",
                                        linestyle="dashed"),
                        zorder=3)

    ax.set_title("β Method Roadmap — Start Simple, Earn Complexity",
                 fontsize=12, fontweight="bold", color=NAVY, pad=12)

    ax.text(4.5, 0.0,
            "Don't jump straight to Kalman — prove β=1 or OLS is insufficient first",
            ha="center", va="bottom", fontsize=8.5, color=GREY, style="italic")

    save(fig, "ch4-beta-roadmap")


if __name__ == "__main__":
    chart_rolling_vs_kalman()
    chart_epsilon_strategy()
    chart_pipeline()
    chart_correct_vs_wrong_beta()
    chart_beta_roadmap()
