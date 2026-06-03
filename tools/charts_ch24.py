"""Charts for Ch.24 — Case Studies: เมื่อ Model พัง (When Models Break Down)."""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from book_style import (save, style_axes, TEAL, NAVY, RED, GREEN, AMBER, BLUE,
                        GREY, RED_F, GREEN_F, BLUE_F, TEAL_F, AMBER_F, VIOLET)


# ============================================================
# Chart 1 — LTCM NAV Timeline 1997–1998
# ============================================================
def chart_ltcm_drawdown():
    # Build monthly date axis Jan 1997 – Dec 1998 (24 months)
    dates = [datetime(1997, 1, 1) + timedelta(days=30 * i) for i in range(24)]

    # Simulate NAV path
    # 1997: grow from 100 to ~210 (roughly +40% from Jan 1997 baseline)
    # Jan 1998 ≈ 210 (peak), then sharp drawdown
    nav = np.array([
        # 1997 Jan–Dec (index 0–11)
        100.0, 107.0, 114.0, 122.0, 130.0, 138.0,
        147.0, 157.0, 167.0, 178.0, 193.0, 210.0,
        # 1998 Jan–Dec (index 12–23)
        210.0, 205.0, 200.0, 198.0, 195.0, 192.0,
        190.0, 107.0,   # Aug 1998: -44% from Jan 1998 peak → ≈107
        36.0,           # Sep 1998: -83% cumulative from 1994 start → ≈36
        28.0,           # Oct 1998: -91% cumulative → ≈19 (show as 28 for chart visibility)
        20.0,           # Nov 1998
        17.0,           # Dec 1998: ~-92%
    ])

    fig, ax = plt.subplots(figsize=(7.4, 3.8))
    ax.set_facecolor(BLUE_F)
    fig.patch.set_facecolor(BLUE_F)

    # Fill under NAV
    ax.fill_between(dates, nav, alpha=0.25, color=TEAL)
    # Plot NAV line
    ax.plot(dates, nav, color=NAVY, lw=2.0, label="LTCM NAV (indexed 100 = Jan 1997)")

    # Initial value reference line
    ax.axhline(100, color=AMBER, lw=1.5, ls="--", alpha=0.8, label="Initial NAV = 100")

    # Event markers
    russia_date = datetime(1998, 8, 1)
    bailout_date = datetime(1998, 9, 1)
    ax.axvline(russia_date, color=RED, lw=1.8, ls="--", alpha=0.9)
    ax.axvline(bailout_date, color=RED, lw=1.8, ls="--", alpha=0.9)

    # Annotations
    ax.annotate("Russia Default\n(Aug 1998)", xy=(russia_date, 107),
                xytext=(datetime(1997, 9, 1), 55),
                fontsize=8.5, color=RED, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.2),
                bbox=dict(boxstyle="round,pad=0.3", facecolor=RED_F, edgecolor=RED, lw=0.8))

    ax.annotate("Fed Bailout\nOrganized\n(Sep 1998)", xy=(bailout_date, 36),
                xytext=(datetime(1998, 4, 1), 15),
                fontsize=8.5, color=RED, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.2),
                bbox=dict(boxstyle="round,pad=0.3", facecolor=RED_F, edgecolor=RED, lw=0.8))

    # Mark peak
    ax.annotate("Peak NAV ≈ 210\n(+110% from start)", xy=(datetime(1998, 1, 1), 210),
                xytext=(datetime(1997, 3, 1), 185),
                fontsize=8.5, color=NAVY,
                arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.0))

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right")

    ax.set_ylabel("NAV (indexed, Jan 1997 = 100)")
    ax.set_title("LTCM NAV — From Genius to Bailout (1997–1998)")
    ax.set_ylim(0, 240)
    ax.legend(fontsize=9, loc="upper right")
    style_axes(ax)
    save(fig, "ch24-ltcm-drawdown")


# ============================================================
# Chart 2 — Quant Quake: Factor Crowding + Cascade
# ============================================================
def chart_quant_quake():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.5, 3.8))

    # ---- Left panel: Factor Crowding Index 2005–2007 ----
    ax1.set_facecolor(AMBER_F)
    fig.patch.set_facecolor("#f9fafb")

    # Months from Jan 2005 to Aug 2007 = 32 months
    months = np.arange(32)
    dates_left = [datetime(2005, 1, 1) + timedelta(days=30 * i) for i in range(32)]

    # Sigmoid-like rise from 0.3 to 0.85
    def sigmoid_rise(x, x0, k, low, high):
        return low + (high - low) / (1 + np.exp(-k * (x - x0)))

    rng = np.random.default_rng(24)
    crowding = sigmoid_rise(months, 20, 0.3, 0.30, 0.85) + rng.normal(0, 0.015, 32)
    crowding = np.clip(crowding, 0.25, 0.92)

    ax1.plot(dates_left, crowding, color=AMBER, lw=2.0, label="Factor Crowding Index")
    ax1.axhline(0.70, color=AMBER, lw=1.5, ls="--", alpha=0.8, label="Warning (0.70)")
    ax1.axhline(0.80, color=RED, lw=1.5, ls="--", alpha=0.8, label="Critical (0.80)")

    quake_date = datetime(2007, 8, 1)
    ax1.axvline(quake_date, color=RED, lw=1.8, ls="-", alpha=0.9)
    ax1.annotate("Quant Quake\nAug 2007", xy=(quake_date, crowding[-1]),
                 xytext=(datetime(2006, 6, 1), 0.88),
                 fontsize=8, color=RED, fontweight="bold",
                 arrowprops=dict(arrowstyle="->", color=RED, lw=1.0),
                 bbox=dict(boxstyle="round,pad=0.2", facecolor=RED_F, edgecolor=RED, lw=0.8))
    ax1.annotate("Crowding critical", xy=(quake_date, crowding[-1]),
                 xytext=(datetime(2006, 2, 1), crowding[-1] - 0.05),
                 fontsize=7.5, color=RED, style="italic")

    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    ax1.set_ylabel("Factor Crowding Index")
    ax1.set_ylim(0.2, 1.0)
    ax1.set_title("Factor Crowding 2005–2007")
    ax1.legend(fontsize=8, loc="upper left")
    style_axes(ax1)

    # ---- Right panel: Cascade PnL simulation ----
    ax2.set_facecolor(RED_F)

    rng2 = np.random.default_rng(42)
    n_steps = 40
    n_funds = 5
    colors = [TEAL, BLUE, AMBER, GREEN, VIOLET]
    labels = ["Fund A (trigger)", "Fund B", "Fund C", "Fund D", "Fund E"]

    pnl_matrix = np.zeros((n_funds, n_steps))
    # First 20 steps: normal uncorrelated random walk
    for f in range(n_funds):
        walk = np.cumsum(rng2.normal(0.002, 0.008, 20))
        pnl_matrix[f, :20] = walk

    # Step 20 onwards: cascade — all drop together
    for step in range(20, n_steps):
        for f in range(n_funds):
            # Fund A triggers first, others cascade
            delay = f * 0  # simultaneous cascade
            cascade_drop = -0.04 - 0.015 * (step - 20)
            noise = rng2.normal(0, 0.005)
            pnl_matrix[f, step] = pnl_matrix[f, 19] + cascade_drop + noise

    for f in range(n_funds):
        ax2.plot(range(n_steps), pnl_matrix[f], color=colors[f], lw=1.8,
                 label=labels[f], alpha=0.9)

    ax2.axvline(20, color=RED, lw=2.0, ls="--", alpha=0.9)
    ax2.annotate("Forced Liquidation\nTrigger", xy=(20, -0.05),
                 xytext=(22, -0.25),
                 fontsize=8, color=RED, fontweight="bold",
                 arrowprops=dict(arrowstyle="->", color=RED, lw=1.0))

    ax2.set_xlabel("Time step (days)")
    ax2.set_ylabel("Cumulative PnL (normalized)")
    ax2.set_title("Cascade Liquidation — 5 Correlated Strategies")
    ax2.legend(fontsize=7.5, loc="lower left")
    style_axes(ax2)

    fig.suptitle("Quant Quake 2007 — Factor Crowding & Cascade Liquidation",
                 fontsize=12, fontweight="bold", color=NAVY, y=1.01)
    save(fig, "ch24-quant-quake")


# ============================================================
# Chart 3 — Amaranth 2006: Nat Gas Price + Fund NAV
# ============================================================
def chart_amaranth():
    fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(7.4, 4.2),
                                          gridspec_kw={"height_ratios": [2, 1]})
    rng = np.random.default_rng(24)

    # Monthly dates Jan 2005 – Dec 2006
    n_months = 24
    dates = [datetime(2005, 1, 1) + timedelta(days=30 * i) for i in range(n_months)]

    # Natural gas price trajectory ($/MMBtu)
    # Jan 2005: 6, Sep 2005 Katrina spike: 14, Dec 2005: 10,
    # Jan 2006: 9, declining to 4 by Sep 2006, Oct 2006: 3.5
    nat_gas_key = {
        0: 6.0,    # Jan 2005
        2: 6.5,    # Mar 2005
        4: 7.0,    # May 2005
        6: 7.8,    # Jul 2005
        8: 14.0,   # Sep 2005 Katrina spike
        9: 12.0,   # Oct 2005
        10: 10.0,  # Nov 2005
        11: 10.0,  # Dec 2005
        12: 9.0,   # Jan 2006
        14: 8.5,   # Mar 2006
        16: 7.0,   # May 2006
        18: 6.0,   # Jul 2006
        20: 4.0,   # Sep 2006 blow-up
        21: 3.5,   # Oct 2006
        22: 4.0,   # Nov 2006
        23: 4.2,   # Dec 2006
    }

    # Interpolate
    nat_gas = np.zeros(n_months)
    key_idx = sorted(nat_gas_key.keys())
    for i, idx in enumerate(key_idx):
        nat_gas[idx] = nat_gas_key[idx]
    # Fill gaps with linear interpolation
    x_known = np.array(key_idx)
    y_known = np.array([nat_gas_key[k] for k in key_idx])
    nat_gas = np.interp(np.arange(n_months), x_known, y_known)
    # Add small noise
    nat_gas += rng.normal(0, 0.08, n_months)
    nat_gas = np.clip(nat_gas, 3.0, 15.0)

    # --- Top panel: Nat Gas Price ---
    ax_top.set_facecolor(TEAL_F)
    ax_top.fill_between(dates, nat_gas, alpha=0.20, color=TEAL)
    ax_top.plot(dates, nat_gas, color=NAVY, lw=2.0)

    # Katrina annotation
    katrina_date = datetime(2005, 9, 1)
    ax_top.annotate("Hurricane Katrina\n(Sep 2005)", xy=(katrina_date, nat_gas[8]),
                    xytext=(datetime(2005, 3, 1), 13.0),
                    fontsize=8.5, color=RED, fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color=RED, lw=1.2),
                    bbox=dict(boxstyle="round,pad=0.3", facecolor=RED_F, edgecolor=RED, lw=0.8))

    # Decline annotation
    ax_top.annotate("Mild winter forecast\nHigh inventory", xy=(datetime(2006, 6, 1), nat_gas[17]),
                    xytext=(datetime(2005, 11, 1), 5.5),
                    fontsize=8, color=NAVY,
                    arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.0))

    # Blow-up line
    blowup_date = datetime(2006, 9, 1)
    ax_top.axvline(blowup_date, color=RED, lw=1.8, ls="--", alpha=0.9)
    ax_top.annotate("Amaranth\nBlow-up", xy=(blowup_date, nat_gas[20]),
                    xytext=(datetime(2006, 10, 15), 6.5),
                    fontsize=8.5, color=RED, fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color=RED, lw=1.1))

    ax_top.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax_top.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax_top.set_ylabel("Nat Gas Price ($/MMBtu)")
    ax_top.set_title("Amaranth 2006 — Natural Gas Spread Blow-up")
    ax_top.set_ylim(2.5, 16.0)
    style_axes(ax_top)

    # --- Bottom panel: Fund NAV ($B) ---
    # Start $9.7B; slight growth 2005; Sep 2006: collapse to $3.1B
    fund_nav = np.array([
        # Jan–Dec 2005 (index 0–11)
        9.70, 9.75, 9.80, 9.85, 9.90, 9.95,
        10.00, 10.05, 10.10, 10.15, 10.20, 10.00,
        # Jan–Dec 2006 (index 12–23)
        9.80, 9.75, 9.70, 9.65, 9.60, 9.55,
        9.50, 9.45, 3.10,   # Sep 2006: collapse
        2.80, 3.00, 3.10,
    ])
    fund_nav += rng.normal(0, 0.01, n_months)

    ax_bot.set_facecolor(RED_F)
    ax_bot.axhline(9.7, color=AMBER, lw=1.5, ls="--", alpha=0.8, label="Initial NAV $9.7B")

    # Fill loss area
    ax_bot.fill_between(dates, fund_nav, 9.7,
                        where=(fund_nav < 9.7),
                        alpha=0.35, color=RED)
    ax_bot.plot(dates, fund_nav, color=RED, lw=2.0, label="Amaranth NAV ($B)")

    ax_bot.axvline(blowup_date, color=RED, lw=1.8, ls="--", alpha=0.9)

    ax_bot.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax_bot.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax_bot.set_ylabel("Fund NAV ($B)")
    ax_bot.set_xlabel("Date (2005–2006)")
    ax_bot.set_ylim(1.5, 11.5)
    ax_bot.legend(fontsize=8.5, loc="upper right")
    style_axes(ax_bot)

    save(fig, "ch24-amaranth")


if __name__ == "__main__":
    chart_ltcm_drawdown()
    chart_quant_quake()
    chart_amaranth()
    print("All ch24 charts saved.")
