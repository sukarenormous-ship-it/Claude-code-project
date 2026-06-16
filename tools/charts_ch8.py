"""Charts for Ch.8 — Jump-Diffusion OU Process."""
import numpy as np
from scipy import stats
from book_style import (save, style_axes, TEAL, NAVY, RED, GREEN, AMBER, BLUE,
                        GREY, RED_F, GREEN_F, BLUE_F, TEAL_F, AMBER_F)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def ou_path_with_jumps(n, kappa, theta, sigma, lam, jump_std, seed):
    """OU path with Merton-style jumps."""
    rng = np.random.default_rng(seed)
    x = np.empty(n); x[0] = theta
    jumps = np.zeros(n)
    for t in range(1, n):
        jump = 0
        if rng.random() < lam:          # Poisson event
            jump = rng.standard_normal() * jump_std
            jumps[t] = jump
        x[t] = x[t-1] + kappa*(theta - x[t-1]) + sigma*rng.standard_normal() + jump
    return x, jumps


# ============================================================
# Chart 1 — Fat-tail histogram: OU residuals vs Normal
# ============================================================
def chart_fat_tail_hist():
    rng = np.random.default_rng(42)
    n = 2000
    # Simulate returns with fat tails (mix of normal + jumps)
    normal_part = rng.standard_normal(n) * 1.0
    jump_mask = rng.random(n) < 0.08   # 8% jump probability
    jump_sizes = rng.standard_normal(n) * 3.5
    returns = normal_part + jump_mask * jump_sizes
    # Standardize
    returns = (returns - returns.mean()) / returns.std()

    fig, ax = plt.subplots(figsize=(7.0, 3.8))
    xr = np.linspace(-6, 6, 300)
    normal_pdf = stats.norm.pdf(xr)

    # histogram
    ax.hist(returns, bins=80, density=True, color=TEAL, alpha=0.7,
            edgecolor="white", lw=0.3, label="Spread returns จริง (fat tail)")
    ax.plot(xr, normal_pdf, color=BLUE, lw=2.5, ls="--", label="Normal(0,1)")

    # tail annotations
    tail_x = 3.5
    ax.annotate("Fat tail!\n(real > Normal)", xy=(tail_x, 0.005),
                xytext=(4.5, 0.04), fontsize=9, color=RED,
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.2))
    ax.annotate("Fat tail!", xy=(-tail_x, 0.005),
                xytext=(-6.0, 0.04), fontsize=9, color=RED,
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.2))

    # shade tails
    tail_mask_r = xr > 2.5
    tail_mask_l = xr < -2.5
    ax.fill_between(xr[tail_mask_r], normal_pdf[tail_mask_r], alpha=0.25, color=RED)
    ax.fill_between(xr[tail_mask_l], normal_pdf[tail_mask_l], alpha=0.25, color=RED)

    ax.set_xlabel("σ (standard deviations)")
    ax.set_ylabel("Probability density")
    ax.set_title("Distribution ของ Spread Returns — Fat Tail vs Normal")
    ax.set_xlim(-6.5, 6.5); ax.set_ylim(0, 0.48)
    ax.legend(fontsize=10)
    style_axes(ax)
    save(fig, "ch8-fat-tail-hist")


# ============================================================
# Chart 2 — OU path with jump detection markers
# ============================================================
def chart_jump_detection():
    n = 300
    kappa, theta, sigma = 0.05, 0.0, 0.8
    lam, jump_std = 0.04, 3.5     # ~4% chance per bar, big jump
    x, jumps = ou_path_with_jumps(n, kappa, theta, sigma, lam, jump_std, seed=99)
    t = np.arange(n)

    # Lee-Mykland style: flag |Δx| > 3 * rolling_std_of_diff
    dx = np.abs(np.diff(x, prepend=x[0]))
    roll_std = np.array([dx[max(0,i-30):i].std() if i > 5 else dx[:5].std() for i in range(n)])
    roll_std = np.where(roll_std < 1e-6, 1e-6, roll_std)
    Lstat = dx / (roll_std + 1e-9)
    detected = (Lstat > 4.0) & (np.abs(jumps) > 0)   # true positives

    fig, axes = plt.subplots(2, 1, figsize=(7.4, 4.2), sharex=True,
                             gridspec_kw={"height_ratios":[2,1]})

    # Top: OU+jump path
    ax = axes[0]
    ax.axhline(theta, color=TEAL, lw=1.3, ls="--", alpha=0.7, label=r"$\theta$")
    sd_ou = sigma / np.sqrt(2*kappa)
    ax.axhline(+2*sd_ou, color=AMBER, lw=0.9, ls=":", alpha=0.6)
    ax.axhline(-2*sd_ou, color=AMBER, lw=0.9, ls=":", alpha=0.6, label="±2σ")
    ax.plot(t, x, color=NAVY, lw=1.5, label=r"$\varepsilon_t$ (OU + jumps)")
    # mark detected jumps
    jt = np.where(detected)[0]
    ax.scatter(jt, x[jt], color=RED, s=70, zorder=6, marker="^", ec="white", lw=1,
               label=f"Jump detected ({len(jt)} events)")
    ax.set_ylabel(r"$\varepsilon$")
    ax.set_title("OU Process พร้อม Jump Events และ Lee-Mykland Detection")
    ax.legend(fontsize=9, loc="upper right")
    style_axes(ax)

    # Bottom: L-stat
    ax = axes[1]
    ax.set_facecolor(TEAL_F)
    ax.plot(t, Lstat, color=GREY, lw=1.0, alpha=0.8)
    ax.axhline(4.0, color=RED, lw=1.5, ls="--", label="Threshold c=4.0")
    ax.fill_between(t, Lstat, 4.0, where=Lstat > 4.0, alpha=0.4, color=RED)
    ax.set_ylabel(r"$|L_t|$")
    ax.set_xlabel("t (bars)")
    ax.legend(fontsize=9)
    style_axes(ax)

    fig.subplots_adjust(hspace=0.08)
    save(fig, "ch8-jump-detection")


if __name__ == "__main__":
    chart_fat_tail_hist()
    chart_jump_detection()
