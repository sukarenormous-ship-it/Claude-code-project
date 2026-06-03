"""Charts for Ch.1 — Synthetic Process."""
import numpy as np
from book_style import (save, style_axes, TEAL, NAVY, RED, GREEN, AMBER, BLUE,
                        GREY, RED_F, AMBER_F, GREEN_F, TEAL_F, BLUE_F)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def _correlated_log_prices(n, mu, sigma, seed):
    """Two correlated log-price paths sharing ~85% of their shock."""
    rng = np.random.default_rng(seed)
    common = rng.standard_normal(n)
    idio_a = rng.standard_normal(n)
    idio_b = rng.standard_normal(n)
    corr = 0.92
    ra = mu + sigma * (corr * common + np.sqrt(1 - corr**2) * idio_a)
    rb = mu + sigma * (corr * common + np.sqrt(1 - corr**2) * idio_b)
    return np.cumsum(ra), np.cumsum(rb)


# ============================================================
# Chart 1 — Raw prices (random walk) vs spread (mean-reverting)
# ============================================================
def chart_random_vs_spread():
    n = 200
    mu, sigma = 0.0003, 0.012
    beta = 1.003

    log_a, log_b = _correlated_log_prices(n, mu, sigma, seed=42)
    spread = log_a - beta * log_b
    spread_mean = spread.mean()
    spread_std = spread.std()
    t = np.arange(n)

    fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.6))

    # Left: raw log prices
    ax = axes[0]
    ax.set_facecolor(RED_F)
    ax.plot(t, log_a, color=BLUE, lw=1.8, label="Bybit log P")
    ax.plot(t, log_b, color=RED, lw=1.8, ls="--", label="Lighter log P")
    ax.set_title("ราคาดิบ — Random Walk\nไม่มีแรงดึงกลับ", color=RED, fontsize=11)
    ax.set_xlabel("เวลา t (bars)")
    ax.set_ylabel("log Price")
    ax.legend(loc="upper left", fontsize=9)
    style_axes(ax)

    # Right: spread
    ax = axes[1]
    ax.set_facecolor(GREEN_F)
    ax.axhline(spread_mean, color=TEAL, lw=1.5, ls="--", label=r"$\theta$ (ค่ากลาง)")
    ax.axhline(spread_mean + 2*spread_std, color=AMBER, lw=1.0, ls=":", label="±2σ")
    ax.axhline(spread_mean - 2*spread_std, color=AMBER, lw=1.0, ls=":")
    ax.plot(t, spread, color=NAVY, lw=1.7, label=r"$\varepsilon$ = spread")

    # entry markers
    highs = np.where(spread > spread_mean + 1.8*spread_std)[0]
    lows  = np.where(spread < spread_mean - 1.8*spread_std)[0]
    for idx in highs[:2]:
        ax.scatter(idx, spread[idx], color=RED, s=50, zorder=5, ec="white", lw=1)
    for idx in lows[:2]:
        ax.scatter(idx, spread[idx], color=GREEN, s=50, zorder=5, ec="white", lw=1)

    ax.set_title("Spread ε — Mean-Reverting\nวนกลับหาค่ากลาง", color=GREEN, fontsize=11)
    ax.set_xlabel("เวลา t (bars)")
    ax.set_ylabel(r"$\varepsilon$")
    ax.legend(loc="upper right", fontsize=9)
    style_axes(ax)

    fig.suptitle(r"log($P_A$) เดิน random walk — แต่ $\varepsilon = \log P_A - \beta\log P_B$ กลับหาค่ากลาง",
                 y=1.04, fontsize=11.5, fontweight="bold", color=NAVY)
    fig.subplots_adjust(top=0.82, bottom=0.15, wspace=0.32)
    save(fig, "ch1-random-vs-spread")


# ============================================================
# Chart 2 — β position sizing impact
# ============================================================
def chart_beta_sizing():
    betas = [0.60, 0.913, 1.00, 1.003, 1.50]
    labels = ["β=0.60", "β=0.913\n(Bybit↔Lighter)", "β=1.00\n(1:1 เท่ากัน)", "β=1.003", "β=1.50"]
    short_b = [b * 100_000 for b in betas]
    colors  = [GREEN, TEAL, AMBER, BLUE, RED]

    fig, ax = plt.subplots(figsize=(7.4, 3.5))

    # long A bar (grey reference)
    bar_h = 0.38
    y_positions = np.arange(len(betas))

    ax.barh(y_positions, [100_000]*len(betas), bar_h, color=GREY, alpha=0.35, label="Long A = $100,000")
    bars = ax.barh(y_positions - bar_h, short_b, bar_h, color=colors, alpha=0.85, label="Short B (ขึ้นกับ β)")

    for i, (v, c) in enumerate(zip(short_b, colors)):
        ax.text(v + 1500, i - bar_h, f"${v:,.0f}", va="center", fontsize=9, color=c, fontweight="bold")

    ax.axvline(100_000, color=GREY, lw=1.2, ls="--")
    ax.set_yticks(y_positions - bar_h/2)
    ax.set_yticklabels(labels, fontsize=9.5)
    ax.set_xlabel("มูลค่า Position (USD)")
    ax.set_title("β กำหนด Position Size ของ Short B\n(Long A คงที่ = $100,000)")
    ax.set_xlim(0, 175_000)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x/1000:.0f}K"))
    ax.legend(loc="lower right", fontsize=9)
    style_axes(ax)
    save(fig, "ch1-beta-sizing")


if __name__ == "__main__":
    chart_random_vs_spread()
    chart_beta_sizing()
