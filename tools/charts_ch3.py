"""Charts for Ch.3 — Ornstein-Uhlenbeck Process."""
import numpy as np
from book_style import (save, style_axes, TEAL, NAVY, RED, GREEN, AMBER, BLUE,
                        GREY, RED_F, AMBER_F, GREEN_F, TEAL_F, BLUE_F)
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


def ou_path(n, kappa, theta, sigma, x0, seed):
    rng = np.random.default_rng(seed)
    x = np.empty(n); x[0] = x0
    for t in range(1, n):
        x[t] = x[t-1] + kappa*(theta - x[t-1]) + sigma*rng.standard_normal()
    return x


# ============================================================
# Chart 1 — Half-life + trade zones (signature OU figure)
# ============================================================
def chart_halflife_zones():
    n = 220
    kappa, theta, sigma = 0.06, 0.0, 1.0
    sd = sigma/np.sqrt(2*kappa)            # stationary std
    x = ou_path(n, kappa, theta, sigma, x0=2.6*sd, seed=11)
    t = np.arange(n)

    fig, ax = plt.subplots(figsize=(7.4, 3.9))
    # zones (bands as horizontal spans)
    ax.axhspan( 3*sd,  4.2*sd, color=RED_F);   ax.axhspan(-4.2*sd, -3*sd, color=RED_F)
    ax.axhspan( 2*sd,  3*sd,   color=AMBER_F); ax.axhspan(-3*sd,  -2*sd, color=AMBER_F)
    ax.axhspan(-2*sd,  2*sd,   color=GREEN_F)
    # reference lines
    ax.axhline(0, color=TEAL, lw=1.5, ls="--")
    for s, c in [(2, AMBER), (-2, AMBER), (3, RED), (-3, RED)]:
        ax.axhline(s*sd, color=c, lw=1.0, ls=":")
    # expected (deterministic) decay overlay from x0
    exp = theta + (x[0]-theta)*np.exp(-kappa*t)
    ax.plot(t, exp, color=GREY, lw=1.4, ls=(0,(6,4)), label="E[ε_t] (decay)")
    # the realised OU path
    ax.plot(t, x, color=NAVY, lw=1.7, label="ε_t (spread)")

    # half-life marker
    hl = np.log(2)/kappa
    ax.axvline(hl, color=GREY, lw=1.0, ls=":")
    ax.annotate("τ½ = ln2/κ", xy=(hl, exp[int(hl)]), xytext=(hl+12, 2.2*sd),
                fontsize=9.5, color=NAVY,
                arrowprops=dict(arrowstyle="->", color=GREY, lw=1))
    # entry / exit markers
    ax.scatter([0], [x[0]], color=RED, s=55, zorder=6, ec="white", lw=1.2)
    ax.annotate("ENTRY (>2σ)", xy=(0, x[0]), xytext=(6, x[0]+0.25*sd),
                fontsize=9.5, color=RED, fontweight="bold")
    exit_i = next(i for i in range(int(hl), n) if abs(x[i]) < 0.5*sd)
    ax.scatter([exit_i], [x[exit_i]], color=GREEN, s=55, zorder=6, ec="white", lw=1.2)
    ax.annotate("EXIT (≈θ)", xy=(exit_i, x[exit_i]), xytext=(exit_i+5, 0.9*sd),
                fontsize=9.5, color=GREEN, fontweight="bold")

    # zone labels on right
    ax.text(n*0.995, 3.4*sd, "STOP",  color=RED,   fontsize=8.5, ha="right", fontweight="bold")
    ax.text(n*0.995, 2.4*sd, "ENTRY", color=AMBER, fontsize=8.5, ha="right", fontweight="bold")
    ax.text(n*0.995, 0.15*sd,"HOLD→EXIT", color=GREEN, fontsize=8.5, ha="right", fontweight="bold")

    ax.set_yticks([-3*sd,-2*sd,0,2*sd,3*sd])
    ax.set_yticklabels(["−3σ","−2σ","θ","+2σ","+3σ"])
    ax.set_xlabel("เวลา t (bars)"); ax.set_ylabel("ε (spread)")
    ax.set_title("OU Process — Zone การ Trade และ Half-Life")
    ax.set_xlim(0, n-1); ax.set_ylim(-4.2*sd, 4.2*sd)
    ax.legend(loc="lower right")
    style_axes(ax)
    save(fig, "ch3-halflife-zones")


# ============================================================
# Chart 2 — AR(1) b-value comparison (3 panels)
# ============================================================
def chart_ar1_bvalues():
    n = 80
    panels = [
        (0.99, RED,   "b = 0.99 (ช้ามาก)",  "คล้าย random walk", RED_F),
        (0.90, GREEN, "b = 0.90 (กลางๆ ✓)", "Intraday trade ได้", GREEN_F),
        (0.50, BLUE,  "b = 0.50 (เร็วมาก)",  "กลับใน 1–2 steps",   BLUE_F),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(7.6, 3.0), sharey=True)
    for ax, (b, c, title, note, fillc) in zip(axes, panels):
        kappa = -np.log(b)
        x = ou_path(n, kappa, 0.0, 1.0, x0=3.0, seed=5)
        ax.set_facecolor(fillc)
        ax.axhline(0, color=TEAL, lw=1.0, ls="--")
        ax.plot(x, color=c, lw=1.8)
        hl = np.log(2)/kappa
        if hl < n:
            ax.axvline(hl, color=GREY, lw=0.9, ls=":")
        ax.set_title(f"{title}\n{note}", fontsize=10.5, color=c)
        ax.set_xlim(0, n-1); ax.set_ylim(-3.6, 3.6)
        style_axes(ax)
    axes[0].set_ylabel("ε")
    axes[0].text(0.04, 0.06, "θ", transform=axes[0].transAxes, color=TEAL, fontsize=10)
    fig.suptitle("ค่า b ใน AR(1) บอกความเร็ว mean-reversion", y=1.08, fontsize=12, fontweight="bold", color=NAVY)
    fig.supxlabel("t (bars)", fontsize=10, color=NAVY, y=0.02)
    fig.subplots_adjust(bottom=0.14, top=0.78)
    save(fig, "ch3-ar1-bvalues")


# ============================================================
# Chart 3 — Walk-forward rolling windows (Gantt style)
# ============================================================
def chart_walkforward():
    fig, ax = plt.subplots(figsize=(7.6, 2.8))
    train, test, slide = 90, 30, 30
    rows = [("W1", 0), ("W2", 30), ("W3", 60), ("W4", 90), ("W5", 120)]
    for i, (lab, start) in enumerate(rows):
        y = len(rows) - i
        a = 0.9 - i*0.12
        ax.broken_barh([(start, train)], (y-0.32, 0.64), facecolors=BLUE, alpha=a, edgecolor="white")
        ax.broken_barh([(start+train, test)], (y-0.32, 0.64), facecolors=GREEN, alpha=0.9, edgecolor="white")
        ax.text(start+train/2, y, f"Train 90d", ha="center", va="center", color="white", fontsize=9, fontweight="bold")
        ax.text(start+train+test/2, y, "Test", ha="center", va="center", color="white", fontsize=8.5, fontweight="bold")
        ax.text(-6, y, lab, ha="right", va="center", color=NAVY, fontsize=9.5, fontweight="bold")

    ax.set_xlim(-12, 245); ax.set_ylim(0.0, len(rows)+0.8)
    ax.set_yticks([]); ax.set_xlabel("วันที่ (เวลาเดินหน้า → ห้าม shuffle)")
    ax.set_title("Walk-Forward — Rolling Windows ตามเวลา")
    ax.grid(axis="y", visible=False)
    legend = [Line2D([0],[0], color=BLUE, lw=8, label="Train window (fit parameters)"),
              Line2D([0],[0], color=GREEN, lw=8, label="Test window (วัด PnL จริง)")]
    ax.legend(handles=legend, loc="upper center", bbox_to_anchor=(0.5, -0.30),
              ncol=2, fontsize=9)
    fig.subplots_adjust(bottom=0.32)
    style_axes(ax)
    save(fig, "ch3-walkforward")


if __name__ == "__main__":
    chart_halflife_zones()
    chart_ar1_bvalues()
    chart_walkforward()
