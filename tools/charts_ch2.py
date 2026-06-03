"""Charts for Ch.2 — Stochastic Calculus."""
import numpy as np
from book_style import (save, style_axes, TEAL, NAVY, RED, GREEN, AMBER, BLUE,
                        GREY, RED_F, GREEN_F, BLUE_F, TEAL_F)
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


# ============================================================
# Chart 1 — √t vs linear growth (Brownian Motion scale)
# ============================================================
def chart_sqrt_growth():
    t = np.linspace(0, 4, 400)
    fig, ax = plt.subplots(figsize=(6.8, 3.6))

    ax.plot(t, t,        color=RED,  lw=2.0, ls="--", label="Linear: t (สมมติ)")
    ax.plot(t, np.sqrt(t), color=TEAL, lw=2.5, label=r"$\sqrt{t}$ — Brownian Motion จริง")

    # annotations at t=4
    ax.annotate("", xy=(4, 4), xytext=(4, 2),
                arrowprops=dict(arrowstyle="<->", color=GREY, lw=1.2))
    ax.text(4.08, 3.1, "ต่างกัน\n2×", fontsize=9, color=GREY, va="center")

    ax.scatter([1, 2, 4], [1, np.sqrt(2), 2], color=TEAL, s=55, zorder=5, ec="white", lw=1.2)
    ax.text(1.05, 1.06, "t=1: std=1", fontsize=9, color=TEAL)
    ax.text(2.05, 1.47, f"t=2: std≈1.41", fontsize=9, color=TEAL)
    ax.text(3.65, 1.93, "t=4: std=2", fontsize=9, color=TEAL, ha="right")

    ax.set_xlabel("t (วัน)")
    ax.set_ylabel("std dev ของ W(t)")
    ax.set_title(r"BM โตตาม $\sqrt{t}$ ไม่ใช่ $t$ — ราคาขยับช้ากว่าที่คิด")
    ax.set_xlim(0, 4.3); ax.set_ylim(0, 4.5)
    ax.legend(fontsize=10)
    style_axes(ax)
    save(fig, "ch2-sqrt-growth")


# ============================================================
# Chart 2 — BM paths vs OU path (side by side)
# ============================================================
def chart_bm_vs_ou():
    rng = np.random.default_rng(7)
    n = 250
    dt = 1
    t = np.arange(n)

    fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.6), sharey=False)

    # Left: 5 BM paths
    ax = axes[0]
    ax.set_facecolor(RED_F)
    for seed in range(5):
        r = np.random.default_rng(seed*13)
        path = np.cumsum(r.standard_normal(n) * np.sqrt(dt))
        ax.plot(t, path, lw=1.2, alpha=0.8)
    ax.axhline(0, color=NAVY, lw=1.2, ls="--", alpha=0.5)
    ax.set_title("Random Walk (BM)\ndrift = 0 ไม่มีแรงดึงกลับ", color=RED, fontsize=11)
    ax.set_xlabel("t")
    ax.set_ylabel("W(t)")
    style_axes(ax)

    # Right: 5 OU paths
    ax = axes[1]
    ax.set_facecolor(GREEN_F)
    kappa, theta, sigma = 0.04, 0.0, 1.0
    sd = sigma / np.sqrt(2*kappa)
    for seed in range(5):
        r = np.random.default_rng(seed*13)
        x = np.empty(n); x[0] = r.standard_normal() * sd * 2
        for i in range(1, n):
            x[i] = x[i-1] + kappa*(theta - x[i-1]) + sigma*r.standard_normal()
        ax.plot(t, x, lw=1.2, alpha=0.8)
    ax.axhline(theta, color=TEAL, lw=1.5, ls="--", label=r"$\theta$ = 0")
    ax.axhline(+2*sd, color=AMBER, lw=1.0, ls=":", alpha=0.7)
    ax.axhline(-2*sd, color=AMBER, lw=1.0, ls=":", alpha=0.7, label="±2σ")
    ax.set_title("OU Process (Spread)\nวนรอบ θ — มีแรงดึงกลับ", color=GREEN, fontsize=11)
    ax.set_xlabel("t")
    ax.set_ylabel(r"$\varepsilon(t)$")
    ax.legend(fontsize=9)
    style_axes(ax)

    fig.suptitle("Random Walk vs OU Process — พฤติกรรมต่างกันอย่างสิ้นเชิง",
                 y=1.04, fontsize=11.5, fontweight="bold", color=NAVY)
    fig.subplots_adjust(top=0.82, bottom=0.15, wspace=0.30)
    save(fig, "ch2-bm-vs-ou")


# ============================================================
# Chart 3 — Itô correction illustration: d(log S) drift
# ============================================================
def chart_ito_correction():
    """Show that log(S) drifts at μ−½σ² not μ, via simulation."""
    rng = np.random.default_rng(99)
    n = 500
    mu, sigma = 0.05/250, 0.20/np.sqrt(250)   # daily drift & vol
    dt = 1
    n_paths = 2000

    final_log_s = []
    for _ in range(n_paths):
        dW = rng.standard_normal(n) * np.sqrt(dt)
        dS_over_S = mu * dt + sigma * dW
        log_s = np.sum(np.log(1 + dS_over_S))
        final_log_s.append(log_s)

    final_log_s = np.array(final_log_s)
    true_drift = (mu - 0.5*sigma**2) * n    # Itô
    naive_drift = mu * n                     # without correction

    fig, ax = plt.subplots(figsize=(6.8, 3.6))
    ax.hist(final_log_s, bins=60, color=TEAL, alpha=0.7, edgecolor="white", lw=0.5,
            label=f"จำลอง 2,000 paths")
    ax.axvline(true_drift,  color=GREEN, lw=2.2, ls="-",  label=f"Itô drift = μ−½σ² = {true_drift:.3f}")
    ax.axvline(naive_drift, color=RED,   lw=2.0, ls="--", label=f"ค่าผิด μ·T = {naive_drift:.3f}")
    ax.set_xlabel("log(S_T) หลัง 500 วัน")
    ax.set_ylabel("จำนวน paths")
    ax.set_title(r"Itô Correction: $d(\log S)$ drift = $\mu - \frac{1}{2}\sigma^2$  ไม่ใช่ $\mu$")
    ax.legend(fontsize=9.5)
    style_axes(ax)
    save(fig, "ch2-ito-correction")


if __name__ == "__main__":
    chart_sqrt_growth()
    chart_bm_vs_ou()
    chart_ito_correction()
