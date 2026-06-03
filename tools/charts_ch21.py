"""Charts for Ch.21 — Spot↔CFD Swap Arbitrage on MT5."""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from book_style import (save, style_axes, TEAL, NAVY, RED, GREEN, AMBER, BLUE,
                        GREY, RED_F, GREEN_F, BLUE_F, TEAL_F, AMBER_F)


# ============================================================
# Chart 1 — Spot vs CFD price series + ε spread
# ============================================================
def chart_spot_cfd_spread():
    rng = np.random.default_rng(21)
    n = 200
    t = np.arange(n)

    # Simulate log-price random walk for Spot
    log_spot = np.cumsum(rng.standard_normal(n) * 0.01)

    # OU spread: ε ~ OU(κ=0.1, θ=0, σ=0.2)
    kappa, theta_ou, sigma_ou = 0.1, 0.0, 0.02
    eps = np.empty(n)
    eps[0] = 0.0
    for i in range(1, n):
        eps[i] = eps[i-1] + kappa * (theta_ou - eps[i-1]) + sigma_ou * rng.standard_normal()

    log_cfd = log_spot + eps

    # Spread stats
    eps_mean = eps.mean()
    eps_std = eps.std()

    fig, axes = plt.subplots(2, 1, figsize=(7.4, 4.0),
                             gridspec_kw={"height_ratios": [1.5, 1]}, sharex=True)

    # Top panel — price series
    ax = axes[0]
    ax.set_facecolor(BLUE_F)
    ax.plot(t, log_spot, color=NAVY, lw=1.5, label="BTC Spot")
    ax.plot(t, log_cfd, color=TEAL, lw=1.5, ls="--", label="BTC CFD (MT5)")
    ax.set_ylabel("Log Price")
    ax.legend(fontsize=9, loc="upper left")
    style_axes(ax)

    # Bottom panel — spread ε
    ax = axes[1]
    ax.set_facecolor(TEAL_F)
    ax.plot(t, eps, color=NAVY, lw=1.5, label=r"$\varepsilon$")
    ax.axhline(eps_mean, color=TEAL, lw=1.2, ls="--", label=r"$\theta=0$")
    ax.axhline(eps_mean + 2 * eps_std, color=AMBER, lw=1.0, ls=":", label=r"$\pm2\sigma$")
    ax.axhline(eps_mean - 2 * eps_std, color=AMBER, lw=1.0, ls=":")

    # Entry points: |ε| > 2σ
    entry_mask = np.abs(eps - eps_mean) > 2 * eps_std
    ax.scatter(t[entry_mask], eps[entry_mask], color=RED, s=25, zorder=6,
               marker="o", label="Entry (|ε|>2σ)")

    # Exit points: |ε| < 0.3σ
    exit_mask = np.abs(eps - eps_mean) < 0.3 * eps_std
    ax.scatter(t[exit_mask], eps[exit_mask], color=GREEN, s=30, zorder=6,
               marker="^", label="Exit (|ε|<0.3σ)")

    ax.set_ylabel(r"Spread $\varepsilon$")
    ax.set_xlabel("t (hours)")
    ax.legend(fontsize=8, loc="upper right", ncol=2)
    style_axes(ax)

    fig.suptitle("Spot↔CFD Spread — MT5 Arbitrage Signal",
                 fontsize=12, fontweight="bold", color=NAVY, y=1.01)
    fig.subplots_adjust(hspace=0.08)
    save(fig, "ch21-spot-cfd-spread")


# ============================================================
# Chart 2 — Walk-Forward Calibration diagram
# ============================================================
def chart_walkforward():
    rng = np.random.default_rng(42)

    fig, ax = plt.subplots(figsize=(7.4, 3.5))
    ax.set_facecolor("white")

    n_folds = 4
    train_w = 60
    val_w = 20
    total = n_folds * (train_w + val_w)
    t = np.arange(total)

    # Draw shaded windows
    for i in range(n_folds):
        start = i * (train_w + val_w)
        # Training window
        ax.axvspan(start, start + train_w, alpha=0.35, color=TEAL_F,
                   ec=TEAL, lw=0.8, label="Train" if i == 0 else "")
        mid_train = start + train_w / 2
        ax.text(mid_train, 1.85, "Train", ha="center", va="center",
                fontsize=8, color=TEAL, fontweight="bold")

        # Validation window
        ax.axvspan(start + train_w, start + train_w + val_w, alpha=0.5,
                   color=AMBER_F, ec=AMBER, lw=0.8, label="Validate" if i == 0 else "")
        mid_val = start + train_w + val_w / 2
        ax.text(mid_val, 1.85, "Val.", ha="center", va="center",
                fontsize=8, color=AMBER, fontweight="bold")

        # Vertical boundary lines
        for boundary in [start, start + train_w, start + train_w + val_w]:
            ax.axvline(boundary, color=GREY, lw=0.8, ls=":", alpha=0.8)

    # Realized Sharpe curve — stable with occasional dip
    sharpe = np.ones(total) * 1.3
    # Add some variation
    sharpe += rng.standard_normal(total) * 0.12
    # Dip in 2nd validation window
    dip_start = 1 * (train_w + val_w) + train_w
    sharpe[dip_start:dip_start + val_w] -= 0.55
    # Dip in 4th validation window
    dip_start2 = 3 * (train_w + val_w) + train_w
    sharpe[dip_start2:dip_start2 + val_w] -= 0.4
    # Smooth slightly
    from numpy.lib.stride_tricks import sliding_window_view
    kernel = 5
    pad = kernel // 2
    sharpe_smooth = np.convolve(sharpe, np.ones(kernel) / kernel, mode="same")

    ax.plot(t, sharpe_smooth, color=NAVY, lw=2.0, label="Realized Sharpe", zorder=5)

    # Acceptable Sharpe line
    ax.axhline(1.0, color=GREEN, lw=1.5, ls="--", label="Acceptable (Sharpe=1.0)")

    # Annotation
    ax.annotate("Roll forward every 20 days", xy=(total * 0.65, 0.55),
                xytext=(total * 0.55, 0.3), fontsize=9, color=NAVY,
                arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.0))

    ax.set_xlim(0, total)
    ax.set_ylim(0.1, 2.1)
    ax.set_xlabel("Trading Days")
    ax.set_ylabel("Realized Sharpe Ratio")
    ax.set_title("Walk-Forward Calibration — Prevent Overfitting",
                 fontweight="bold", color=NAVY)
    ax.legend(fontsize=9, loc="upper right")
    style_axes(ax)

    save(fig, "ch21-walkforward")


if __name__ == "__main__":
    chart_spot_cfd_spread()
    chart_walkforward()
