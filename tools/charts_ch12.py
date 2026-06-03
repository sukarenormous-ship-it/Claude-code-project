"""Charts for Ch.12 — Position Sizing: Kelly Criterion."""
import numpy as np
import matplotlib.pyplot as plt
from book_style import (save, style_axes, TEAL, NAVY, RED, GREEN, AMBER, BLUE,
                        GREY, RED_F, GREEN_F, BLUE_F, TEAL_F, AMBER_F)


# ============================================================
# Chart 1 — Kelly Criterion: Growth vs Fraction Invested
# ============================================================
def chart_kelly_curve():
    p = 0.55
    q = 0.45
    b = 1.0
    f_star = (p * b - q) / b   # = 0.10
    half_kelly = f_star / 2    # = 0.05

    f = np.linspace(1e-6, 0.999, 600)
    # Clip to avoid log(0) near f=1
    f_clip = np.minimum(f, 1 - 1e-6)
    g = p * np.log(1 + b * f_clip) + q * np.log(1 - f_clip)

    fig, ax = plt.subplots(figsize=(7.0, 3.8))
    ax.set_facecolor(BLUE_F)

    # Ruin zone shading (f > 0.20)
    ruin_mask = f > 0.20
    ax.fill_between(f[ruin_mask], g[ruin_mask],
                    g[ruin_mask].min() - 0.05,
                    color=RED_F, alpha=0.35, label="Overbetting / Ruin", zorder=1)
    ax.axvspan(0.20, 1.0, color=RED_F, alpha=0.25, zorder=1)

    # Optimal zone shading (0.05 to 0.15)
    opt_mask = (f >= 0.05) & (f <= 0.15)
    ax.fill_between(f[opt_mask], g[opt_mask],
                    g.min() - 0.05,
                    color=GREEN_F, alpha=0.5, label="Optimal Zone", zorder=2)

    # Growth curve
    ax.plot(f, g, color=TEAL, lw=2.5, label="g(f) = p·log(1+b·f)+q·log(1-f)", zorder=3)

    # Horizontal break-even
    ax.axhline(0, color=NAVY, lw=0.9, ls=":", alpha=0.6, label="Break-even (g=0)")

    # f* vertical
    ax.axvline(f_star, color=RED, lw=1.8, ls="--", zorder=4)
    ax.text(f_star + 0.012, g.max() * 0.85,
            r"$f^* = 10\%$", color=RED, fontsize=9.5, va="top", zorder=5)

    # Half-Kelly vertical
    ax.axvline(half_kelly, color=AMBER, lw=1.6, ls="--", zorder=4)
    ax.text(half_kelly + 0.012, g.max() * 0.6,
            r"$\frac{1}{2}f^* = 5\%$", color=AMBER, fontsize=9.5, va="top", zorder=5)

    ax.set_xlabel("Fraction invested (f)")
    ax.set_ylabel("Expected log growth g(f)")
    ax.set_xlim(0, 1)
    ax.set_ylim(g.min() - 0.01, g.max() + 0.03)
    ax.set_title("Kelly Criterion — Growth vs Fraction Invested")
    ax.legend(fontsize=8.5, loc="lower left")
    style_axes(ax)
    save(fig, "ch12-kelly-curve")


# ============================================================
# Chart 2 — Position Size vs Half-Life
# ============================================================
def chart_half_life_sizing():
    hl = np.linspace(1, 60, 300)

    # Normalize to 1.0 at HL=10
    ref_hl = 10.0

    raw_kelly = np.ones_like(hl)                          # flat reference
    hl_scaled = (ref_hl / hl)                             # size ∝ 1/HL, =1 at HL=10
    bounded   = np.clip(hl_scaled, 0.1, 2.0)              # bounded version

    fig, ax = plt.subplots(figsize=(7.0, 3.5))
    ax.set_facecolor(TEAL_F)

    ax.plot(hl, raw_kelly, color=GREY,  lw=1.8, ls="--",
            label="Raw Kelly (flat reference)")
    ax.plot(hl, hl_scaled, color=TEAL,  lw=2.0,
            label=r"Half-life scaled (size $\propto 1/HL$)")
    ax.plot(hl, bounded,   color=NAVY,  lw=1.5, ls=":",
            label="Bounded (min 0.1, max 2.0)")

    # Vertical markers
    ax.axvline(7,  color=AMBER, lw=1.2, ls=":", alpha=0.8)
    ax.text(7 + 0.8, 1.85, "Min useful\n(HL=7)", color=AMBER, fontsize=8)

    ax.axvline(30, color=BLUE, lw=1.2, ls=":", alpha=0.8)
    ax.text(30 + 0.8, 1.85, "Typical pair\n(HL=30)", color=BLUE, fontsize=8)

    ax.set_xlabel("Half-life (days)")
    ax.set_ylabel("Relative position size\n(normalized at HL=10)")
    ax.set_xlim(1, 60)
    ax.set_ylim(0, 2.3)
    ax.set_title("Position Size vs Half-Life — Shorter Reversion = Larger Safe Size")
    ax.legend(fontsize=8.5, loc="upper right")
    style_axes(ax)
    save(fig, "ch12-half-life-sizing")


if __name__ == "__main__":
    chart_kelly_curve()
    chart_half_life_sizing()
