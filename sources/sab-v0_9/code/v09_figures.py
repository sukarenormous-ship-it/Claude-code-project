"""Figures for chapters 6 and 7 (version 0.9). Requires matplotlib.

Run after v09_ch06_ch07_demo.py has written v09_ch06_ch07_results.json.
"""
import json
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIG = ROOT / "figures"
R = json.loads((ROOT / "code" / "v09_ch06_ch07_results.json").read_text())
NAVY, ORANGE, GREEN, RED, GREY, BLUE = "#173f73", "#d57a20", "#238065", "#b54147", "#66717c", "#2a6ebb"
plt.rcParams.update({"font.family": ["Liberation Sans", "DejaVu Sans"], "font.size": 11, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.grid": True, "axes.axisbelow": True, "grid.color": "#e6e9ee",
                     "axes.titlesize": 11.5, "savefig.dpi": 200, "svg.fonttype": "path"})


def save(fig, name):
    for ext in ("png", "svg"):
        fig.savefig(FIG / f"{name}.{ext}", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def note(fig, text, y):
    fig.text(0.5, y, text, ha="center", va="top", fontsize=9, color=GREY)


def carry_ladder():
    c = R["ch06_carry_ladder"]
    labels = ["Rate on spot\n(simple, screen)", "Price gain on\ncapital 125,000", "After fees\n154", "Excess over\n4% alternative"]
    vals = [float(c["simple_rate_on_spot_pct"]), float(c["price_return_on_capital_pct_yr"]),
            float(c["net_on_capital_pct_yr"]), float(c["excess_pct_yr"])]
    fig, ax = plt.subplots(figsize=(11, 4.6))
    ax.bar(labels, vals, color=[GREY, BLUE, NAVY, GREEN], width=0.6)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.25, f"{v:.2f}%", ha="center", fontweight="bold")
    ax.set_ylim(0, 14)
    ax.set_ylabel("Simple annualised rate (% per year)")
    ax.set_title("From the rate on the screen to the return on the capital you tie up\n"
                 "Long 1 BTC spot at 100,000, short dated future at 103,000, 90 days, held to expiry", fontweight="bold")
    note(fig, "Synthetic numbers. Capital includes the 25,000 cash reserve for margin calls (section 03.09). "
              "Fees 0.05% on three trades; futures settlement fee assumed zero.", -0.03)
    save(fig, "carry_ladder")


def funding_scenarios():
    s = R["ch06_funding_scenarios"]
    fig, ax = plt.subplots(figsize=(11, 4.8))
    x = list(range(1, 91))
    styles = {"A_flat": (NAVY, "-", "A: +0.01% every interval"), "B_decay": (GREEN, "-", "B: +0.03% then +0.005%"),
              "C_flip": (RED, "-", "C: +0.01% then -0.01%"), "D_whipsaw": (GREY, ":", "D: alternating, see exercise")}
    for k, (col, ls, lab) in styles.items():
        ax.plot(x, [float(v) for v in s[k]["cumulative"]], color=col, ls=ls, lw=2, label=lab)
    cumC = [float(v) for v in s["C_flip"]["cumulative"]]
    ax.plot([48], [cumC[47]], "o", color=RED)
    ax.annotate("rule: exit after 3 negative\nintervals, keeps 420", (48, cumC[47]), (58, 680), color=RED, fontsize=9.5,
                arrowprops=dict(arrowstyle="-", color=RED, lw=0.8))
    ax.axhline(80, color=ORANGE, ls="--", lw=1.5)
    ax.text(58, 30, "fees to open and close = 80", color=ORANGE, fontsize=9.5)
    ax.set_xlabel("Funding interval (8 hours each, 90 intervals = 30 days)")
    ax.set_ylabel("Cumulative funding received (money)")
    ax.set_title("Funding on a short perp hedged with spot: the same position, four rate paths\n"
                 "1 BTC, mark held at 100,000 to isolate funding", fontweight="bold")
    ax.legend(loc="upper left", frameon=False, fontsize=9.5)
    note(fig, "Assumed rate paths, not market data. Price P&L of the two legs is set to zero here; "
              "real basis changes add to or subtract from these lines.", -0.02)
    save(fig, "funding_scenarios")


def corr_vs_coint():
    p = R["ch07_population"]
    ex = p["typical_examples"]
    h, c = ex["H_high_corr_no_link"], ex["C_linked"]
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.8))
    ax[0].scatter([v * 100 for v in h["ret_a"]], [v * 100 for v in h["ret_b"]], s=7, color=BLUE, alpha=0.5,
                  label=f"No long-run link: corr {h['return_corr']:.2f}")
    ax[0].scatter([v * 100 for v in c["ret_a"]], [v * 100 for v in c["ret_b"]], s=7, color=ORANGE, alpha=0.5,
                  label=f"Linked pair: corr {c['return_corr']:.2f}")
    ax[0].set_xlabel("Daily return of coin A (%)")
    ax[0].set_ylabel("Daily return of coin B (%)")
    ax[0].set_title("Daily returns: the unlinked pair looks tighter")
    ax[0].legend(loc="upper left", frameon=False, fontsize=9.5)
    t = list(range(500))
    ax[1].plot(t, h["spread"], color=BLUE, lw=1.6, label="No long-run link")
    ax[1].plot(t, c["spread"], color=ORANGE, lw=1.6, label="Linked pair")
    ax[1].axvline(250, color=GREY, ls=":", lw=1)
    ax[1].text(255, min(h["spread"] + c["spread"]) * 0.97, "test period", color=GREY, fontsize=9.5)
    ax[1].set_xlabel("Day")
    ax[1].set_ylabel("Log price A minus log price B")
    ax[1].set_title("Spread level: only the linked pair is pulled back")
    ax[1].legend(loc="lower left", frameon=False, fontsize=9.5)
    fig.suptitle("High return correlation is not a long-run link\nOne typical pair of each kind from 200 simulated pairs",
                 fontweight="bold", y=1.04)
    note(fig, "Synthetic prices. Averages over 200 pairs: return correlation 0.90 vs 0.72; "
              "share of test days inside the formation 2-sd band 59.7% vs 91.8%.", -0.02)
    save(fig, "corr_vs_coint")


def selection_bias():
    s = R["ch07_selection_bias"]
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6), sharey=True)
    for a, z, st, title, col in ((ax[0], s["best_selected_z"], s["best_selected_stats"], "Best of 200 unlinked pairs, chosen on formation data", RED),
                                 (ax[1], s["first_genuine_z"], s["first_genuine_stats"], "A pair with a real long-run link", GREEN)):
        t = list(range(len(z)))
        a.plot(t, z, color=col, lw=1.3)
        a.axhspan(-2, 2, color="#eef1f5", zorder=0)
        a.axvline(250, color=GREY, ls=":", lw=1)
        a.axhline(0, color=GREY, lw=0.8)
        a.set_title(title, fontsize=11)
        a.set_xlabel("Day (formation 0-249, test 250-499)")
        a.text(258, 5.3, f"test days inside band: {st['test_inside']:.0%}\nlargest |z| in test: {st['test_max_abs_z']}",
               fontsize=9.5, color=col)
    ax[0].set_ylabel("z-score using formation mean and sd")
    ax[0].set_ylim(-6.5, 6.5)
    fig.suptitle("Scanning many pairs finds some that only looked good in the past", fontweight="bold", y=1.0)
    note(fig, "Synthetic prices, seeded. Selected 10 of 200 unlinked pairs by mean crossings in formation: "
              "on average 60.2% of test days inside the band, against 93.7% for 10 linked pairs.", -0.02)
    save(fig, "selection_bias")


if __name__ == "__main__":
    carry_ladder()
    funding_scenarios()
    corr_vs_coint()
    selection_bias()
    print("figures written")
