"""Charts for Ch.4 — Hedge Ratio β (OLS · TLS · Kalman)."""
import numpy as np
from book_style import (save, style_axes, TEAL, NAVY, RED, GREEN, AMBER, BLUE,
                        GREY, RED_F, GREEN_F, BLUE_F, TEAL_F)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D


def _sim_returns(n, beta_true, seed):
    """Simulate log-return pairs with true β."""
    rng = np.random.default_rng(seed)
    common = rng.standard_normal(n) * 0.012
    noise_a = rng.standard_normal(n) * 0.003
    noise_b = rng.standard_normal(n) * 0.003
    r_b = common + noise_b
    r_a = beta_true * common + noise_a
    return r_a, r_b


# ============================================================
# Chart 1 — OLS vs TLS scatter (2 panels)
# ============================================================
def chart_ols_vs_tls():
    rng = np.random.default_rng(77)
    n = 120
    beta_true = 0.92
    r_a, r_b = _sim_returns(n, beta_true, seed=77)

    # OLS
    beta_ols = np.cov(r_a, r_b)[0,1] / np.var(r_b, ddof=1)
    alpha_ols = np.mean(r_a) - beta_ols * np.mean(r_b)

    # TLS via eigendecomposition
    cov = np.cov(np.stack([r_a, r_b]))
    vals, vecs = np.linalg.eigh(cov)
    min_vec = vecs[:, 0]
    beta_tls = -min_vec[0] / min_vec[1]
    alpha_tls = np.mean(r_a) - beta_tls * np.mean(r_b)

    xr = np.array([r_b.min()*1.1, r_b.max()*1.1])

    fig, axes = plt.subplots(1, 2, figsize=(8.5, 3.8), sharey=True, sharex=True)

    for ax, (beta, alpha, c, title, residual_dir) in zip(axes, [
        (beta_ols, alpha_ols, BLUE, f"OLS   β={beta_ols:.3f}\nminimize ↕ vertical residual", "vertical"),
        (beta_tls, alpha_tls, GREEN, f"TLS   β={beta_tls:.3f}\nminimize ↗ perpendicular residual", "perp"),
    ]):
        ax.scatter(r_b, r_a, s=18, alpha=0.55, color=c, ec="white", lw=0.4)
        ax.plot(xr, alpha + beta * xr, color=c, lw=2.2, label=f"β={beta:.3f}")
        # ghost the other line
        other_b, other_a = (beta_tls, alpha_tls) if c == BLUE else (beta_ols, alpha_ols)
        ax.plot(xr, other_a + other_b * xr, color=GREY, lw=1.2, ls="--", alpha=0.5)

        # show a few residual lines
        idxs = rng.integers(0, n, 8)
        for i in idxs:
            y_fit = alpha + beta * r_b[i]
            if residual_dir == "vertical":
                ax.plot([r_b[i], r_b[i]], [r_a[i], y_fit], color=RED, lw=1.0, alpha=0.7)
            else:
                # perpendicular residual line
                dx = (r_a[i] - y_fit) * beta / (1 + beta**2)
                dy = -(r_a[i] - y_fit) / (1 + beta**2)
                ax.plot([r_b[i], r_b[i]+dx], [r_a[i], r_a[i]+dy], color=RED, lw=1.0, alpha=0.7)

        ax.set_xlabel("return B (r_B)")
        ax.set_ylabel("return A (r_A)")
        ax.set_title(title, fontsize=11)
        style_axes(ax)

    axes[0].set_facecolor(BLUE_F)
    axes[1].set_facecolor(GREEN_F)
    fig.suptitle(f"OLS vs TLS — β ต่างกันเล็กน้อย แต่ทิศทาง residual ต่างกัน",
                 y=1.04, fontsize=11.5, fontweight="bold", color=NAVY)
    fig.subplots_adjust(top=0.82, bottom=0.15, wspace=0.12)
    save(fig, "ch4-ols-vs-tls")


# ============================================================
# Chart 2 — Scatter + OLS fit + residual ε time series
# ============================================================
def chart_ols_residual():
    rng = np.random.default_rng(42)
    n = 150
    beta_true = 0.914
    r_a, r_b = _sim_returns(n, beta_true, seed=42)

    beta_ols = np.cov(r_a, r_b)[0,1] / np.var(r_b, ddof=1)
    alpha_ols = np.mean(r_a) - beta_ols * np.mean(r_b)
    eps = r_a - alpha_ols - beta_ols * r_b
    eps_cum = np.cumsum(eps)   # cumulative spread

    t = np.arange(n)
    eps_std = eps_cum.std()
    fig, axes = plt.subplots(1, 2, figsize=(8.5, 3.8))

    # Left: scatter with fit
    ax = axes[0]
    xr = np.array([r_b.min()*1.1, r_b.max()*1.1])
    ax.set_facecolor(BLUE_F)
    ax.scatter(r_b, r_a, s=18, alpha=0.55, color=BLUE, ec="white", lw=0.4)
    ax.plot(xr, alpha_ols + beta_ols * xr, color=NAVY, lw=2.2,
            label=fr"$\hat{{\beta}}$ = {beta_ols:.3f}")
    ax.set_xlabel(r"$r_B = \Delta\log P_B$")
    ax.set_ylabel(r"$r_A = \Delta\log P_A$")
    ax.set_title(f"OLS regression: slope = β̂ = {beta_ols:.3f}")
    ax.legend(fontsize=10)
    style_axes(ax)

    # Right: cumulative epsilon
    ax = axes[1]
    ax.set_facecolor(TEAL_F)
    ax.axhline(eps_cum.mean(), color=TEAL, lw=1.5, ls="--", label="θ")
    ax.axhline(eps_cum.mean()+2*eps_std, color=AMBER, lw=1.0, ls=":", label="±2σ")
    ax.axhline(eps_cum.mean()-2*eps_std, color=AMBER, lw=1.0, ls=":")
    ax.plot(t, eps_cum, color=NAVY, lw=1.7)

    highs = np.where(eps_cum > eps_cum.mean()+1.7*eps_std)[0]
    lows  = np.where(eps_cum < eps_cum.mean()-1.7*eps_std)[0]
    if len(highs): ax.scatter(highs[:3], eps_cum[highs[:3]], color=RED, s=50, zorder=5, ec="white", lw=1)
    if len(lows):  ax.scatter(lows[:3],  eps_cum[lows[:3]],  color=GREEN, s=50, zorder=5, ec="white", lw=1)

    ax.set_xlabel("t (bars)")
    ax.set_ylabel(r"Cumulative $\varepsilon_t$")
    ax.set_title(r"$\varepsilon_t = \log P_A - \hat{\alpha} - \hat{\beta}\log P_B$ (mean-revert)")
    ax.legend(fontsize=9)
    style_axes(ax)

    fig.suptitle("OLS แยก log P_A เป็น 'ส่วนที่ B อธิบาย' + residual ε ที่ mean-revert",
                 y=1.04, fontsize=11, fontweight="bold", color=NAVY)
    fig.subplots_adjust(top=0.82, bottom=0.15, wspace=0.30)
    save(fig, "ch4-ols-residual")


# ============================================================
# Chart 3 — Rolling β stability (OLS rolling window)
# ============================================================
def chart_rolling_beta():
    rng = np.random.default_rng(88)
    n = 400
    t = np.arange(n)
    # beta changes: 0.90 → 0.95 → 1.05 over time (regime changes)
    beta_true = np.where(t < 150, 0.90, np.where(t < 300, 0.95, 1.05))

    common = rng.standard_normal(n) * 0.012
    noise_a = rng.standard_normal(n) * 0.003
    noise_b = rng.standard_normal(n) * 0.003
    r_b = common + noise_b
    r_a = beta_true * common + noise_a

    # rolling OLS
    window = 60
    beta_roll = np.full(n, np.nan)
    for i in range(window, n):
        rb = r_b[i-window:i]
        ra = r_a[i-window:i]
        beta_roll[i] = np.cov(ra, rb)[0,1] / np.var(rb, ddof=1)

    fig, ax = plt.subplots(figsize=(7.4, 3.5))
    ax.plot(t, beta_true, color=GREY, lw=2.0, ls="--", label="β จริง (ไม่รู้ใน practice)")
    ax.plot(t, beta_roll, color=TEAL, lw=1.8, label=f"β̂ rolling OLS (window={window}d)")
    ax.axvline(150, color=RED, lw=1.0, ls=":", alpha=0.7)
    ax.axvline(300, color=RED, lw=1.0, ls=":", alpha=0.7)
    ax.text(155, 1.07, "regime\nchange", color=RED, fontsize=8, va="top")
    ax.text(305, 1.07, "regime\nchange", color=RED, fontsize=8, va="top")
    ax.set_xlabel("t (วัน)")
    ax.set_ylabel("β̂")
    ax.set_title("Rolling OLS β — ตามทัน regime change ได้ แต่ล่าช้า (window lag)")
    ax.legend(fontsize=10)
    ax.set_ylim(0.80, 1.15)
    style_axes(ax)
    save(fig, "ch4-rolling-beta")


if __name__ == "__main__":
    chart_ols_vs_tls()
    chart_ols_residual()
    chart_rolling_beta()
