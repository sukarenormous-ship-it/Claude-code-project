"""Checks for the worked examples added in version 0.6.

Synthetic identities only: no market data, no fitted model, no orders.
Standard library only. Exact Decimal/Fraction arithmetic is used for the
accounting examples; the first-passage section is a seeded Monte Carlo and
its printed values are rounded.
"""
from __future__ import annotations

import json
import math
import random
from decimal import Decimal as D, getcontext
from fractions import Fraction as Fr

getcontext().prec = 28


def s(x):
    return str(x)


# ---------------------------------------------------------------- chapter 1
def tail_risk():
    p_loss, gain, loss = D("0.01"), D("1"), D("-120")
    ev = (1 - p_loss) * gain + p_loss * loss
    assert ev == D("-0.21")
    out = {"expected_pnl_per_period": s(ev), "no_loss_probability": {}}
    for n in (50, 100, 250):
        out["no_loss_probability"][str(n)] = round(0.99 ** n, 4)
    out["expected_pnl_50_periods"] = s(ev * 50)
    out["pnl_if_no_loss_in_50_periods"] = s(gain * 50)
    assert ev * 50 == D("-10.50")
    return out


# ---------------------------------------------------------------- chapter 3
def margin_ledger(capital):
    """Long 1 spot, short 1 linear dated future, daily cash settlement.

    Teaching rule: margin balance must equal m * current futures price
    after each settlement (single rate, no separate maintenance level).
    """
    m = D("0.10")
    s0, f0 = D("100000"), D("103000")
    rows = []
    free = D(capital)
    spot_q, margin = D(0), D(0)

    def equity(spot_px):
        return free + spot_q * spot_px + margin

    rows.append(("start", free, D(0), margin, equity(s0)))
    free -= s0
    spot_q = D(1)
    rows.append(("buy_spot", free, spot_q * s0, margin, equity(s0)))
    im = m * f0
    free -= im
    margin += im
    rows.append(("short_future_post_margin", free, spot_q * s0, margin, equity(s0)))

    s1, f1 = D("110000"), D("113200")
    vm = -(f1 - f0)
    margin += vm
    rows.append(("day1_settlement", free, spot_q * s1, margin, equity(s1)))
    required = m * f1
    top_up = required - margin
    shortfall = max(D(0), top_up - free)
    result = {
        "variation_margin_day1": s(vm),
        "required_margin_day1": s(required),
        "top_up_needed": s(top_up),
        "free_cash_before_top_up": s(free),
        "shortfall": s(shortfall),
        "max_one_day_future_rise_covered": s(
            (D(capital) - s0 - im) / (1 + m)
        ),
    }
    assert top_up == (1 + m) * (f1 - f0)
    if shortfall == 0:
        free -= top_up
        margin += top_up
        rows.append(("day1_after_top_up", free, spot_q * s1, margin, equity(s1)))
        st = D("105000")
        margin += -(st - f1)
        rows.append(("expiry_settlement", free, spot_q * st, margin, equity(st)))
        assert equity(st) == D(capital) + (f0 - s0)
        result["equity_at_expiry"] = s(equity(st))
    result["rows"] = [
        {"event": e, "free_cash": s(a), "spot_value": s(b), "margin": s(c), "equity": s(d)}
        for e, a, b, c, d in rows
    ]
    return result


def funding_ledger():
    fee_rate = D("0.0002")
    spot_in, perp_in = D("100000"), D("100050")
    spot_out, perp_out = D("99000"), D("99020")
    marks = [D("100000"), D("101000"), D("99000")]
    rates = [D("0.0001"), D("0.0003"), D("-0.0002")]
    # short perp receives when the rate is positive
    funding = [mk * r for mk, r in zip(marks, rates)]
    price = (spot_out - spot_in) + (perp_in - perp_out)
    basis_change = (perp_in - spot_in) - (perp_out - spot_out)
    assert price == basis_change == D("30")
    fees = fee_rate * (spot_in + perp_in + spot_out + perp_out)
    net = price + sum(funding) - fees
    assert sum(funding) == D("20.5")
    assert fees == D("79.614")
    assert net == D("-29.114")
    return {
        "funding_cash_flows_to_short": [s(x) for x in funding],
        "funding_total": s(sum(funding)),
        "price_pnl": s(price),
        "fees": s(fees),
        "net": s(net),
        "simple_annualised_of_0.01pct_per_8h": s(D("0.0001") * 3 * 365),
        "intervals_to_cover_fees_at_10_per_interval": s(fees / D("10")),
    }


# ---------------------------------------------------------------- chapter 4
def hedge_comparison():
    d_a, p_b = D("10000"), D("50")
    beta_a, beta_b = D("1.5"), D("1.0")
    sig_m, sig_eb = D("0.02"), D("0.01")
    b = beta_a * beta_b * sig_m ** 2 / (beta_b ** 2 * sig_m ** 2 + sig_eb ** 2)
    assert b == D("1.2")
    methods = {
        "equal_units": D("100") * p_b,
        "dollar_neutral": d_a,
        "price_level_h_1.6": D("1.6") * D("100") * p_b,
        "return_regression_b_1.2": b * d_a,
        "beta_neutral": d_a * beta_a / beta_b,
    }
    out = {"regression_slope_b": s(b), "rows": []}
    for name, x in methods.items():
        beta_exp = d_a * beta_a - x * beta_b
        sd = ((beta_exp * sig_m) ** 2 + (x * sig_eb) ** 2).sqrt()
        out["rows"].append(
            {
                "method": name,
                "units_b_short": s(x / p_b),
                "value_b_short": s(x),
                "net_dollar": s(d_a - x),
                "beta_exposure": s(beta_exp),
                "pnl_market_minus_4pct": s(beta_exp * D("-0.04")),
                "pnl_sd_excluding_a_specific": str(round(float(sd), 2)),
            }
        )
    sds = {r["method"]: float(r["pnl_sd_excluding_a_specific"]) for r in out["rows"]}
    assert min(sds, key=sds.get) == "return_regression_b_1.2"
    return out


def lot_rounding():
    prices = [Fr(100), Fr(50), Fr(200), Fr(80)]
    beta = [Fr(12, 10), Fr(8, 10), Fr(1), Fr(11, 10)]
    g = [Fr(1, 2), Fr(-1, 2), Fr(2, 10), Fr(-2, 10)]
    exact_value = [Fr(20000, 52) * w for w in (15, 11, -18, -8)]
    exact_q = [v / p for v, p in zip(exact_value, prices)]
    out = {"exact_quantities": [str(round(float(q), 2)) for q in exact_q]}
    for lot in (1, 10):
        q = [Fr(round(float(x) / lot) * lot) for x in exact_q]
        d = [a * p for a, p in zip(q, prices)]
        net = sum(d)
        be = sum(x * y for x, y in zip(d, beta))
        ge = sum(x * y for x, y in zip(d, g))
        out[f"lot_{lot}"] = {
            "quantities": [int(x) for x in q],
            "values": [int(x) for x in d],
            "net": str(float(net)),
            "beta_exposure": str(float(be)),
            "g_exposure": str(float(ge)),
            "gross": str(float(sum(abs(x) for x in d))),
            "pnl_market_minus_5pct": str(float(be * Fr(-5, 100))),
            "pnl_g_plus_3pct": str(float(ge * Fr(3, 100))),
        }
    return out


# ------------------------------------------------------------- supplement 7A
def first_passage(seed=20261111, paths=100_000, max_steps=5_000):
    rng = random.Random(seed)
    out = []
    for phi, sig in ((0.8, 0.1), (0.8, 0.5), (0.99, 0.5)):
        times, up_first = [], 0
        for _ in range(paths):
            x, t, touched_up = 2.0, 0, False
            while t < max_steps:
                x = phi * x + rng.gauss(0.0, sig)
                t += 1
                if x >= 3.0 and not touched_up:
                    touched_up = True
                if x <= 1.0:
                    break
            times.append(t)
            up_first += touched_up
        times.sort()
        n = len(times)
        out.append(
            {
                "phi": phi,
                "innovation_sd": sig,
                "mean_half_life": round(math.log(0.5) / math.log(phi), 2),
                "median_first_passage": times[n // 2],
                "mean_first_passage": round(sum(times) / n, 1),
                "p90_first_passage": times[int(0.9 * n)],
                "share_done_within_4": round(sum(t <= 4 for t in times) / n, 3),
                "share_touching_3_before_1": round(up_first / n, 3),
                "cdf_points": {
                    str(k): round(sum(t <= k for t in times) / n, 4)
                    for k in (1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128)
                },
            }
        )
    return out


def exercise_checks():
    # chapter 3, exercise 7
    m, f0, f1, s0, s1 = D("0.10"), D("103000"), D("111000"), D("100000"), D("108100")
    margin = m * f0 - (f1 - f0)
    top_up = m * f1 - margin
    assert top_up == D("8800") == (1 + m) * (f1 - f0)
    free_after = D("9700") - top_up
    equity_change = (s1 - s0) - (f1 - f0)
    assert free_after == D("900") and equity_change == D("100")
    # chapter 4, exercise 4
    def slope(sig_eb):
        return D("1.5") * D("0.0004") / (D("0.0004") + sig_eb ** 2)
    assert slope(D("0")) == D("1.5")
    b2 = slope(D("0.02"))
    assert b2 == D("0.75")
    def sd(x, sig_eb):
        return float((((D("15000") - x) * D("0.02")) ** 2 + (x * sig_eb) ** 2).sqrt())
    sds = {k: round(sd(D(v), D("0.02")), 1) for k, v in (("b", "7500"), ("dollar", "10000"), ("beta", "15000"))}
    assert sds == {"b": 212.1, "dollar": 223.6, "beta": 300.0}
    # supplement 7A, exercise 4
    drift = 10 * 2 * (1 - 0.99 ** 12)
    assert round(drift, 2) == 2.27
    return {
        "ch03_ex7": {"top_up": s(top_up), "free_cash_after": s(free_after), "equity_change": s(equity_change)},
        "ch04_ex4": {"b_if_no_specific_risk": "1.5", "b_if_specific_sd_2pct": s(b2), "pnl_sd": sds},
        "s7a_ex4_expected_price_gain_12_periods": round(drift, 2),
    }


def main():
    result = {
        "scope": "Synthetic worked examples added in v0.6; no market data or backtest",
        "ch01_tail_risk": tail_risk(),
        "ch03_margin_capital_125000": margin_ledger("125000"),
        "ch03_margin_capital_120000": margin_ledger("120000"),
        "ch03_funding": funding_ledger(),
        "ch04_hedge_comparison": hedge_comparison(),
        "ch04_lot_rounding": lot_rounding(),
        "s7a_first_passage_seeded_monte_carlo": first_passage(),
        "exercise_checks": exercise_checks(),
        "checks": "all exact identities passed; Monte Carlo values are rounded",
    }
    print(json.dumps(result, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
