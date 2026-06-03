"""Charts for Ch.5 — ADF Test & Cointegration."""
import numpy as np
from book_style import (save, style_axes, TEAL, NAVY, RED, GREEN, AMBER, BLUE,
                        GREY, RED_F, GREEN_F, BLUE_F, TEAL_F)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats


# ============================================================
# Chart 1 — Stationary vs Non-stationary (3 panels)
# ============================================================
def chart_stationary_vs_nonstationary():
    n = 200
    t = np.arange(n)

    # Panel 1: I(1) random walk (seed=1)
    rng1 = np.random.default_rng(1)
    rw = np.cumsum(rng1.standard_normal(n) * 1.0)

    # Panel 2: I(1) with drift (seed=2)
    rng2 = np.random.default_rng(2)
    drift = 0.04
    rw_drift = np.cumsum(rng2.standard_normal(n) * 1.0 + drift)

    # Panel 3: Stationary OU process (seed=3)
    rng3 = np.random.default_rng(3)
    kappa = 0.15
    theta = 0.0
    sigma = 1.0
    ou = np.zeros(n)
    ou[0] = rng3.standard_normal() * 1.0
    for i in range(1, n):
        ou[i] = ou[i-1] + kappa * (theta - ou[i-1]) + sigma * rng3.standard_normal()

    fig, axes = plt.subplots(1, 3, figsize=(8.5, 3.6))

    # --- Panel 1: Random walk ---
    ax = axes[0]
    ax.set_facecolor(RED_F)
    ax.plot(t, rw, color=NAVY, lw=1.6)
    ax.axhline(rw.mean(), color=GREY, lw=1.0, ls="--", alpha=0.7)
    ax.set_title("I(1) — Random Walk\nADF: ไม่ reject H₀  (unit root)", fontsize=10.5)
    ax.set_xlabel("t")
    ax.set_ylabel("εₜ")
    style_axes(ax)

    # --- Panel 2: Random walk with drift ---
    ax = axes[1]
    ax.set_facecolor(RED_F)
    ax.plot(t, rw_drift, color=RED, lw=1.6)
    ax.axhline(rw_drift.mean(), color=GREY, lw=1.0, ls="--", alpha=0.7)
    ax.set_title("I(1) + Drift\nADF: ไม่ reject H₀  (unit root)", fontsize=10.5)
    ax.set_xlabel("t")
    style_axes(ax)

    # --- Panel 3: Stationary OU ---
    ax = axes[2]
    ax.set_facecolor(GREEN_F)
    ou_mean = ou.mean()
    ou_std = ou.std()
    ax.axhline(ou_mean, color=TEAL, lw=1.5, ls="--", label="θ (mean)")
    ax.axhspan(ou_mean - ou_std, ou_mean + ou_std, alpha=0.18, color=TEAL)
    ax.plot(t, ou, color=TEAL, lw=1.6)
    ax.set_title("I(0) — Stationary OU\nADF: reject H₀  (stationary)", fontsize=10.5)
    ax.set_xlabel("t")
    ax.legend(fontsize=8.5, loc="upper right")
    style_axes(ax)

    fig.suptitle("Stationary vs Non-stationary — ADF Test ตัดสินด้วยสถิติ",
                 y=1.04, fontsize=11.5, fontweight="bold", color=NAVY)
    fig.subplots_adjust(top=0.82, bottom=0.18, wspace=0.35)
    save(fig, "ch5-stationary-vs-nonstat")


# ============================================================
# Chart 2 — ADF Critical Values
# ============================================================
def chart_adf_critical_values():
    # ADF test statistic distribution is non-normal (Dickey-Fuller distribution),
    # but for illustration we show a shifted/scaled curve resembling the DF distribution.
    # We use a t-distribution with df=25 shifted left to approximate DF distribution shape.
    x = np.linspace(-6.0, 2.5, 600)
    # Use a shifted, slightly-skewed curve to mimic DF distribution
    # DF distribution ~ N(-1.5, 1) skewed left; approximate with norm loc=-1.5, scale=1.1
    pdf = stats.norm.pdf(x, loc=-1.5, scale=1.1)
    # Make it look slightly left-skewed using a gamma transform for visual clarity
    # Use a mixture: mostly norm(-1.5,1) + slight left tail boost
    pdf_skewed = pdf * (1 + 0.4 * np.maximum(0, -x - 2.5))
    pdf_skewed /= np.trapezoid(pdf_skewed, x)   # renormalize

    # ADF critical values (MacKinnon, no constant / with constant typical)
    cv_1 = -3.44   # 1%
    cv_5 = -2.86   # 5%
    cv_10 = -2.57  # 10%

    fig, ax = plt.subplots(figsize=(6.8, 3.6))
    ax.set_facecolor(BLUE_F)

    # Fill rejection region (left of 10% critical value)
    mask_rej = x <= cv_10
    ax.fill_between(x, 0, pdf_skewed, where=mask_rej,
                    color=RED, alpha=0.25, label="Rejection region")

    # Fill very strong rejection (left of 1%)
    mask_1pct = x <= cv_1
    ax.fill_between(x, 0, pdf_skewed, where=mask_1pct,
                    color=RED, alpha=0.50)

    # Fill 1–5% zone
    mask_5pct = (x > cv_1) & (x <= cv_5)
    ax.fill_between(x, 0, pdf_skewed, where=mask_5pct,
                    color=AMBER, alpha=0.45)

    # Fill 5–10% zone
    mask_10pct = (x > cv_5) & (x <= cv_10)
    ax.fill_between(x, 0, pdf_skewed, where=mask_10pct,
                    color=AMBER, alpha=0.22)

    # PDF curve
    ax.plot(x, pdf_skewed, color=NAVY, lw=2.2)

    # Vertical lines for critical values
    ymax_at = {cv_1: float(pdf_skewed[np.argmin(np.abs(x - cv_1))]),
               cv_5: float(pdf_skewed[np.argmin(np.abs(x - cv_5))]),
               cv_10: float(pdf_skewed[np.argmin(np.abs(x - cv_10))])}

    ax.axvline(cv_1,  color=RED,   lw=2.0, ls="--")
    ax.axvline(cv_5,  color=AMBER, lw=2.0, ls="--")
    ax.axvline(cv_10, color=GREEN, lw=1.8, ls=":")

    # Labels for critical values
    y_top = pdf_skewed.max()
    ax.text(cv_1 - 0.08, y_top * 0.78, f"1%\n{cv_1}", color=RED,
            fontsize=8.5, ha="right", fontweight="bold")
    ax.text(cv_5 - 0.08, y_top * 0.88, f"5%\n{cv_5}", color=AMBER,
            fontsize=8.5, ha="right", fontweight="bold")
    ax.text(cv_10 + 0.10, y_top * 0.78, f"10%\n{cv_10}", color=GREEN,
            fontsize=8.5, ha="left", fontweight="bold")

    # Annotation arrow pointing to rejection zone
    ax.annotate("ค่า test stat\nที่ reject H₀",
                xy=(cv_1 - 0.8, pdf_skewed[np.argmin(np.abs(x - (cv_1 - 0.8)))] * 0.6),
                xytext=(-5.2, y_top * 0.55),
                fontsize=9, color=RED, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.4),
                ha="center")

    # Zero line
    ax.axhline(0, color=GREY, lw=0.8)

    ax.set_xlabel("ADF test statistic", color=NAVY)
    ax.set_ylabel("Density", color=NAVY)
    ax.set_title("ADF Critical Values — reject H₀ เมื่อ test stat ต่ำกว่า critical value",
                 fontsize=11, fontweight="bold", color=NAVY)
    ax.set_xlim(-6.2, 2.8)
    ax.set_ylim(bottom=-0.005)

    # Legend patches
    patches = [
        mpatches.Patch(color=RED, alpha=0.7, label="reject H₀: p < 1%"),
        mpatches.Patch(color=AMBER, alpha=0.6, label="reject H₀: p 1–5%"),
        mpatches.Patch(color=AMBER, alpha=0.3, label="borderline: p 5–10%"),
    ]
    ax.legend(handles=patches, fontsize=8.5, loc="upper left")

    style_axes(ax)
    fig.subplots_adjust(bottom=0.15)
    save(fig, "ch5-adf-critical")


if __name__ == "__main__":
    chart_stationary_vs_nonstationary()
    chart_adf_critical_values()
