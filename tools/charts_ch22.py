"""Charts for Ch.22 — Options-Based Stat Arb."""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from book_style import (save, style_axes, TEAL, NAVY, RED, GREEN, AMBER, BLUE,
                        GREY, RED_F, GREEN_F, BLUE_F, TEAL_F, AMBER_F)


# ============================================================
# Chart 1 — IV time series (BTC & ETH) + ε_IV spread
# ============================================================
def chart_iv_spread():
    rng = np.random.default_rng(22)
    n = 150
    t = np.arange(n)

    # BTC IV ~55% with noise
    btc_base = 55.0
    btc_noise = np.cumsum(rng.standard_normal(n) * 0.5)
    btc_noise -= btc_noise.mean()
    btc_iv = btc_base + btc_noise * 0.6 + rng.standard_normal(n) * 0.8

    # ETH IV ~52%, slightly lower
    eth_base = 52.0
    eth_noise = btc_noise * 0.85 + rng.standard_normal(n) * 0.7
    eth_noise -= eth_noise.mean()
    eth_iv = eth_base + eth_noise * 0.6 + rng.standard_normal(n) * 0.8

    # Compute β, θ, ε
    beta_iv = np.cov(btc_iv, eth_iv)[0, 1] / np.var(eth_iv, ddof=1)
    eps_iv = btc_iv - beta_iv * eth_iv
    theta_iv = eps_iv.mean()
    sigma_iv = eps_iv.std()

    # 2σ bands for each IV series (rolling)
    btc_mean = btc_iv.mean()
    btc_std = btc_iv.std()
    eth_mean = eth_iv.mean()
    eth_std = eth_iv.std()

    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(8.5, 3.8))

    # Left: IV time series
    ax_left.set_facecolor(TEAL_F)
    ax_left.plot(t, btc_iv, color=TEAL, lw=1.5, label="BTC IV")
    ax_left.plot(t, eth_iv, color=BLUE, lw=1.5, label="ETH IV")
    ax_left.axhline(btc_mean + 2 * btc_std, color=AMBER, lw=0.9, ls="--", alpha=0.7)
    ax_left.axhline(btc_mean - 2 * btc_std, color=AMBER, lw=0.9, ls="--", alpha=0.7,
                    label="±2σ bands")
    ax_left.axhline(eth_mean + 2 * eth_std, color=AMBER, lw=0.9, ls="--", alpha=0.5)
    ax_left.axhline(eth_mean - 2 * eth_std, color=AMBER, lw=0.9, ls="--", alpha=0.5)
    ax_left.set_ylabel("Implied Volatility (%)")
    ax_left.set_xlabel("t (hours)")
    ax_left.legend(fontsize=9)
    style_axes(ax_left)

    # Right: ε_IV spread
    ax_right.set_facecolor(GREEN_F)
    ax_right.plot(t, eps_iv, color=NAVY, lw=1.5, label=r"$\varepsilon_{IV}$")
    ax_right.axhline(theta_iv, color=TEAL, lw=1.2, ls="--", label=r"$\theta_{IV}$")
    ax_right.axhline(theta_iv + 2 * sigma_iv, color=AMBER, lw=1.0, ls=":",
                     label=r"$\pm2\sigma$ (entry)")
    ax_right.axhline(theta_iv - 2 * sigma_iv, color=AMBER, lw=1.0, ls=":")

    # Entry points
    entry_mask = np.abs(eps_iv - theta_iv) > 2 * sigma_iv
    ax_right.scatter(t[entry_mask], eps_iv[entry_mask], color=RED, s=25,
                     zorder=6, marker="o", label="Entry")

    # Exit points
    exit_mask = np.abs(eps_iv - theta_iv) < 0.3 * sigma_iv
    ax_right.scatter(t[exit_mask], eps_iv[exit_mask], color=GREEN, s=30,
                     zorder=6, marker="^", label="Exit")

    ax_right.set_ylabel(r"$\varepsilon_{IV}$ = BTC IV $-$ ETH IV $- \theta$")
    ax_right.set_xlabel("t (hours)")
    ax_right.legend(fontsize=8, ncol=2)
    style_axes(ax_right)

    fig.suptitle("IV Stat Arb: BTC vs ETH Implied Volatility Spread",
                 fontsize=12, fontweight="bold", color=NAVY)
    fig.tight_layout()
    save(fig, "ch22-iv-spread")


# ============================================================
# Chart 2 — Vol smile with 25Δ marks
# ============================================================
def chart_vol_smile():
    # X axis: 25Δ Put, 10Δ Put, ATM, 10Δ Call, 25Δ Call
    x_labels = ["25Δ Put", "10Δ Put", "ATM", "10Δ Call", "25Δ Call"]
    x = np.arange(len(x_labels))

    normal  = np.array([0.65, 0.57, 0.52, 0.54, 0.58])
    crash   = np.array([0.82, 0.68, 0.55, 0.53, 0.56])
    bull    = np.array([0.60, 0.55, 0.52, 0.57, 0.65])

    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    ax.set_facecolor(BLUE_F)

    # Plot smiles
    ax.plot(x, normal, color=TEAL, lw=2, marker="o", ms=6, label="Normal")
    ax.plot(x, crash, color=RED, lw=2, marker="s", ms=6, label="Crash fear")
    ax.plot(x, bull, color=GREEN, lw=2, marker="^", ms=6, label="Bull run")

    # Shade excess put premium (crash vs normal on put side: x=0,1,2)
    put_side = slice(0, 3)
    x_put = x[put_side]
    ax.fill_between(x_put, normal[put_side], crash[put_side],
                    alpha=0.3, color=RED, label="Excess put premium")

    # Shade excess call premium (bull vs normal on call side: x=2,3,4)
    call_side = slice(2, 5)
    x_call = x[call_side]
    ax.fill_between(x_call, normal[call_side], bull[call_side],
                    alpha=0.3, color=GREEN, label="Excess call premium")

    # Vertical dashed at ATM (x=2)
    ax.axvline(2, color=GREY, lw=1.2, ls="--", alpha=0.8)
    ax.text(2.05, 0.83, "ATM", fontsize=9, color=GREY)

    ax.set_xticks(x)
    ax.set_xticklabels(x_labels)
    ax.set_ylabel("Implied Volatility")
    ax.set_ylim(0.48, 0.87)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.set_title("Vol Smile — Skew Regime (Normal vs Crash vs Bull)",
                 fontweight="bold", color=NAVY)
    ax.legend(loc="upper right", fontsize=9)
    style_axes(ax)

    save(fig, "ch22-vol-smile")


# ============================================================
# Chart 3 — Risk Reversal (25Δ) z-score signal
# ============================================================
def chart_rr_zscore():
    rng = np.random.default_rng(33)
    n = 150
    t = np.arange(n)

    # OU process for RR: κ=0.08, θ=-2.0%, σ=1.5%
    kappa, theta_rr, sigma_rr = 0.08, -2.0, 1.5
    rr = np.empty(n)
    rr[0] = theta_rr
    for i in range(1, n):
        rr[i] = rr[i-1] + kappa * (theta_rr - rr[i-1]) + sigma_rr * rng.standard_normal()

    # Rolling z-score (full-window)
    rr_mean = rr.mean()
    rr_std = rr.std()
    z = (rr - rr_mean) / rr_std

    # Entry threshold
    entry_mask = np.abs(z) > 2.0

    fig, axes = plt.subplots(2, 1, figsize=(7.4, 3.5),
                             gridspec_kw={"height_ratios": [2, 1]}, sharex=True)

    # Top: RR time series
    ax = axes[0]
    ax.set_facecolor(TEAL_F)
    ax.plot(t, rr, color=NAVY, lw=1.5, label=r"RR$_{25\Delta}$")
    ax.axhline(rr_mean, color=TEAL, lw=1.2, ls="--", label=r"$\theta_{RR}$")
    ax.axhline(rr_mean + 2 * rr_std, color=AMBER, lw=1.0, ls=":",
               label=r"$\theta \pm 2\sigma$")
    ax.axhline(rr_mean - 2 * rr_std, color=AMBER, lw=1.0, ls=":")

    # Mark entry points on top panel
    ax.scatter(t[entry_mask], rr[entry_mask], color=RED, s=30, zorder=6,
               marker="o", label="|z|>2 Entry")

    ax.set_ylabel(r"RR$_{25\Delta}$ (%)")
    ax.legend(fontsize=8, loc="upper right", ncol=2)
    style_axes(ax)

    # Bottom: z-score
    ax = axes[1]
    ax.set_facecolor(BLUE_F)
    ax.plot(t, z, color=NAVY, lw=1.2)
    ax.axhline(0, color=GREY, lw=0.8)
    ax.axhline(2.0, color=AMBER, lw=1.2, ls="--", label="±2 (entry)")
    ax.axhline(-2.0, color=AMBER, lw=1.2, ls="--")
    ax.axhline(3.0, color=RED, lw=1.0, ls="--", label="±3 (stop)")
    ax.axhline(-3.0, color=RED, lw=1.0, ls="--")
    ax.fill_between(t, z, 2.0, where=z > 2.0, alpha=0.25, color=AMBER)
    ax.fill_between(t, z, -2.0, where=z < -2.0, alpha=0.25, color=AMBER)

    ax.set_ylabel("z-score")
    ax.set_xlabel("t (hours)")
    ax.legend(fontsize=8, loc="upper right")
    style_axes(ax)

    fig.suptitle(r"Risk Reversal (25$\Delta$) — Skew Stat Arb Signal",
                 fontsize=12, fontweight="bold", color=NAVY, y=1.01)
    fig.subplots_adjust(hspace=0.08)
    save(fig, "ch22-rr-zscore")


if __name__ == "__main__":
    chart_iv_spread()
    chart_vol_smile()
    chart_rr_zscore()
