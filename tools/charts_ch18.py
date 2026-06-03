"""Charts for Ch.18 — Options Overlay: Put-Call Parity Arbitrage."""
import numpy as np
from scipy.interpolate import make_interp_spline
from book_style import (save, style_axes, TEAL, NAVY, RED, GREEN, AMBER, BLUE,
                        GREY, RED_F, GREEN_F, BLUE_F, TEAL_F, AMBER_F)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


# ============================================================
# Chart: ch18-iv-surface  — IV Smile: Near vs Far Expiry
# ============================================================
def chart_iv_surface():
    x = np.array([-0.5, -0.25, 0.0, 0.25, 0.5])
    labels = ["25Δ Put", "10Δ Put", "ATM", "10Δ Call", "25Δ Call"]

    iv_near = np.array([0.72, 0.62, 0.55, 0.57, 0.60])
    iv_far  = np.array([0.60, 0.55, 0.52, 0.53, 0.55])

    # smooth interpolation
    x_fine = np.linspace(-0.5, 0.5, 300)
    spl_near = make_interp_spline(x, iv_near, k=3)
    spl_far  = make_interp_spline(x, iv_far,  k=3)
    y_near = spl_near(x_fine)
    y_far  = spl_far(x_fine)

    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    ax.set_facecolor(BLUE_F)

    # shade arb zone (near > far everywhere here)
    ax.fill_between(x_fine, y_near, y_far,
                    where=(y_near > y_far),
                    color=AMBER, alpha=0.4, label="Calendar spread arb zone")

    # curves
    ax.plot(x_fine, y_near, color=RED,  lw=2.2, label="7-day expiry (higher, skewed)")
    ax.plot(x_fine, y_far,  color=TEAL, lw=2.2, label="30-day expiry (lower, flatter)")

    # ATM dashed line
    ax.axvline(0, color=GREY, lw=1.2, ls="--")

    # mark widest gap: at 25Δ Put (x=-0.5)
    gap_x = -0.5
    gap_y_near = float(spl_near(gap_x))
    gap_y_mid  = (gap_y_near + float(spl_far(gap_x))) / 2
    ax.scatter([gap_x], [gap_y_near], color=RED, s=70, zorder=6, ec="white", lw=1)
    ax.annotate("Calendar arb point\n(gap widest @ 25Δ Put)",
                xy=(gap_x, gap_y_near),
                xytext=(gap_x + 0.18, gap_y_near + 0.04),
                fontsize=8.5, color=RED,
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.1))

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.set_xlabel("Strike (relative to ATM / Delta)")
    ax.set_ylabel("Implied Volatility (IV)")
    ax.set_title("IV Surface Smile — Near vs Far Expiry (Calendar Spread Arb)")
    ax.legend(fontsize=9, loc="upper right")
    style_axes(ax)
    save(fig, "ch18-iv-surface")


if __name__ == "__main__":
    chart_iv_surface()
