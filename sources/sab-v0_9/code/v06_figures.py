"""Figures added or redrawn in version 0.6 (requires matplotlib).

Run after v06_enrichment_demo.py has written v06_enrichment_results.json.
All inputs are the synthetic numbers of the worked examples.
"""
import json
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIG = ROOT / "figures"
RES = json.loads((ROOT / "code" / "v06_enrichment_results.json").read_text())

NAVY, ORANGE, GREEN, RED, GREY, BLUE = "#173f73", "#d57a20", "#238065", "#b54147", "#66717c", "#2a6ebb"
plt.rcParams.update(
    {
        "font.family": ["Liberation Sans", "DejaVu Sans"],
        "font.size": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": "#e6e9ee",
        "grid.linewidth": 0.8,
        "axes.titlesize": 11.5,
        "figure.dpi": 100,
        "savefig.dpi": 200,
        "svg.fonttype": "path",
    }
)


def save(fig, name):
    fig.savefig(FIG / f"{name}.png", bbox_inches="tight", facecolor="white")
    fig.savefig(FIG / f"{name}.svg", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def note(fig, lines, y=-0.02):
    for i, line in enumerate(lines):
        fig.text(0.5, y - 0.045 * i, line, ha="center", va="top", fontsize=9, color=GREY)


def tail_risk():
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
    fig.suptitle("Small steady receipts with a rare large loss\nSynthetic rule: +1 with probability 99%, -120 with probability 1%", fontweight="bold", y=1.04)
    t = list(range(0, 81))
    path = [min(k, 60) + (-120 if k >= 61 else 0) + max(0, k - 61) for k in t]
    ax[0].plot(t, path, color=NAVY, lw=2)
    ax[0].plot(t, [-0.21 * k for k in t], color=ORANGE, lw=2, ls="--")
    ax[0].axhline(0, color=GREY, lw=0.8)
    ax[0].annotate("+60 after 60 quiet periods", (60, 60), (18, 48), color=NAVY, fontsize=10, arrowprops=dict(arrowstyle="-", color=NAVY, lw=0.8))
    ax[0].annotate("one loss of 120", (61, -60), (40, -50), color=RED, fontsize=10)
    ax[0].text(3, -24, "Expected path: -0.21 per period", color=ORANGE, fontsize=10)
    ax[0].set_title("One possible path and the expected path")
    ax[0].set_xlabel("Period")
    ax[0].set_ylabel("Cumulative P&L (money)")
    n = list(range(0, 301))
    ax[1].plot(n, [0.99 ** k for k in n], color=GREEN, lw=2)
    for k in (50, 100, 250):
        p = 0.99 ** k
        ax[1].plot([k], [p], "o", color=GREEN)
        ax[1].annotate(f"{k} periods: {p:.1%}", (k, p), (k + 8, p + 0.05), fontsize=10)
    ax[1].set_ylim(0, 1.05)
    ax[1].set_title("Chance that a sample shows no loss at all")
    ax[1].set_xlabel("Number of periods observed")
    ax[1].set_ylabel("Probability of zero loss events")
    note(fig, ["Assumed probabilities, not estimates. A quiet sample of 50 periods shows +50 while the expected result is -10.5."])
    save(fig, "tail_risk")


def margin_cash():
    rows = RES["ch03_margin_capital_125000"]["rows"][2:]
    labels = ["Opened", "Day 1\nsettled", "Day 1\ntopped up", "Expiry\nsettled"]
    free = [float(r["free_cash"]) for r in rows]
    margin = [float(r["margin"]) for r in rows]
    equity = [float(r["equity"]) for r in rows]
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.8))
    fig.suptitle("Price-hedged is not cash-hedged\nLong 1 spot, short 1 dated future, daily cash settlement, margin = 10% of futures price", fontweight="bold", y=1.05)
    x = range(len(rows))
    ax[0].bar([i - 0.2 for i in x], free, 0.4, color=BLUE, label="Free cash")
    ax[0].bar([i + 0.2 for i in x], margin, 0.4, color=ORANGE, label="Margin balance")
    for i in x:
        ax[0].text(i - 0.2, free[i] + 400, f"{free[i]:,.0f}", ha="center", fontsize=9)
        ax[0].text(i + 0.2, margin[i] + 400, f"{margin[i]:,.0f}", ha="center", fontsize=9)
        ax[0].text(i, 23500, f"Equity\n{equity[i]:,.0f}", ha="center", fontsize=9, color=NAVY, fontweight="bold")
    ax[0].set_xticks(list(x), labels)
    ax[0].set_ylim(0, 27000)
    ax[0].set_ylabel("Money")
    ax[0].set_title("Starting capital 125,000: equity barely moves, cash does")
    ax[0].legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2, frameon=False)
    rise = [0, 16000]
    ax[1].plot(rise, [1.1 * r for r in rise], color=RED, lw=2)
    ax[1].text(3300, 1500, "Cash needed = 1.1 x rise in futures price", color=RED, fontsize=9.5)
    for cash, cap, col in ((9700, "120,000", GREY), (14700, "125,000", BLUE)):
        ax[1].axhline(cash, color=col, lw=1.5, ls="--")
        ax[1].plot([cash / 1.1], [cash], "o", color=col)
        ax[1].annotate(f"capital {cap}: free cash {cash:,}\ncovers a rise of {cash / 1.1:,.0f}", (cash / 1.1, cash), (cash / 1.1 - 8600, cash + 900), fontsize=9.5, color=col)
    ax[1].axvline(10200, color=GREY, lw=0.8, ls=":")
    ax[1].text(10350, 4300, "example rise\n10,200", fontsize=9, color=GREY)
    ax[1].set_xlim(0, 16000)
    ax[1].set_ylim(0, 18000)
    ax[1].set_xlabel("One-day rise in futures price (money per BTC)")
    ax[1].set_ylabel("Cash needed that day")
    ax[1].set_title("How large a one-day rise the free cash covers")
    note(fig, ["Teaching rule with one margin rate and end-of-day top-up; real venues publish their own initial, maintenance and collateral rules."], y=-0.09)
    save(fig, "margin_cash")


def hedge_compare():
    rows = RES["ch04_hedge_comparison"]["rows"]
    labels = ["Equal\nunits", "Dollar\nneutral", "Price-level\nh = 1.6", "Return\nregression\nb = 1.2", "Beta\nneutral"]
    pnl = [float(r["pnl_market_minus_4pct"]) for r in rows]
    sd = [float(r["pnl_sd_excluding_a_specific"]) for r in rows]
    cols = [GREY, ORANGE, BLUE, GREEN, NAVY]
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
    fig.suptitle("One pair, five ways to size the short leg\nLong A 10,000 (beta 1.5); short B (beta 1.0, own risk 1% per period); market risk 2% per period", fontweight="bold", y=1.05)
    ax[0].bar(labels, pnl, color=cols)
    ax[0].axhline(0, color=GREY, lw=0.8)
    for i, v in enumerate(pnl):
        ax[0].text(i, v - 22 if v < 0 else 8, f"{v + 0:,.0f}".replace("-0", "0") if abs(v) < 0.5 else f"{v:,.0f}", ha="center", fontsize=10, fontweight="bold")
    ax[0].set_ylim(-470, 40)
    ax[0].set_ylabel("Price P&L (money)")
    ax[0].set_title("Market factor falls 4%, nothing else moves")
    ax[1].bar(labels, sd, color=cols)
    for i, v in enumerate(sd):
        ax[1].text(i, v + 4, f"{v:,.1f}", ha="center", fontsize=10, fontweight="bold")
    ax[1].set_ylim(0, 240)
    ax[1].set_ylabel("Std. dev. of one-period P&L (money)")
    ax[1].set_title("Model risk per period, excluding A's own risk")
    note(fig, ["Assumed one-factor model. Zero market exposure and lowest variance are different targets; neither is evidence of expected profit."], y=-0.1)
    save(fig, "hedge_compare")


def first_passage():
    cases = RES["s7a_first_passage_seeded_monte_carlo"]
    styles = [(GREEN, "-"), (NAVY, "-"), (ORANGE, "--")]
    fig, ax = plt.subplots(figsize=(12, 4.8))
    for c, (col, ls) in zip(cases, styles):
        ks = sorted(int(k) for k in c["cdf_points"])
        ys = [c["cdf_points"][str(k)] for k in ks]
        lab = f"phi = {c['phi']}, shock sd = {c['innovation_sd']}  (mean half-life {c['mean_half_life']})"
        ax.plot(ks, ys, color=col, ls=ls, lw=2, marker="o", ms=4, label=lab)
    for hl, col in ((3.11, GREEN), (68.97, ORANGE)):
        ax.axvline(hl, color=col, lw=1, ls=":")
        ax.text(hl * 1.05, 0.04, f"half-life\n{hl}", color=col, fontsize=9.5)
    ax.set_xscale("log", base=2)
    ax.set_xticks([1, 2, 4, 8, 16, 32, 64, 128], ["1", "2", "4", "8", "16", "32", "64", "128"])
    ax.set_ylim(0, 1.03)
    ax.set_xlabel("Periods since entry at X = 2 (log scale)")
    ax.set_ylabel("Share of paths that have reached X <= 1")
    ax.set_title("Half-life of the conditional mean is not the time a path first reaches the target\nSeeded simulation of an assumed AR(1), mean 0, 100,000 paths per case", fontweight="bold")
    ax.legend(loc="lower right", bbox_to_anchor=(1.0, 0.13), frameon=False)
    note(fig, ["In the slow case 44.8% of paths touch X = 3 before they reach X = 1. Simulated from assumptions; not market data."], y=0.0)
    save(fig, "first_passage")


def moving_mean():
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.4))
    t = ["t0", "t1", "t2"]
    ax[0].plot(t, [10, 10, 10], color=NAVY, lw=2, marker="o", ms=7, label="Spread mark X")
    ax[0].plot(t, [0, 8, 10], color=ORANGE, lw=2, ls="--", marker="s", ms=7, label="Estimated mean")
    ax[0].set_ylim(-0.6, 12)
    ax[0].set_title("Marks stay unchanged", fontweight="bold")
    ax[0].set_ylabel("Money / basket unit")
    ax[0].set_xlabel("Model update time")
    ax[0].legend(loc="lower right", frameon=False)
    ax[1].plot(t, [10, 2, 0], color=GREEN, lw=2, marker="o", ms=7)
    for x, v in zip(t, [10, 2, 0]):
        ax[1].annotate(str(v), (x, v), (0, 9), textcoords="offset points", ha="center")
    ax[1].set_ylim(-0.6, 12)
    ax[1].set_title("Computed residual X minus mean", fontweight="bold")
    ax[1].set_ylabel("Money / basket unit")
    ax[1].set_xlabel("Model update time")
    save(fig, "mr_moving_mean")


if __name__ == "__main__":
    tail_risk()
    margin_cash()
    hedge_compare()
    first_passage()
    moving_mean()
    print("figures written")
