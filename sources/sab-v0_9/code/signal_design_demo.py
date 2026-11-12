"""Synthetic examples connecting plotted coordinates to fixed holdings.

No market data, fitted prediction model, backtest, or order submission.
Rates use continuous annualization with ACT/365 for the stated example.
"""
from decimal import Decimal as D
from math import exp, log, isclose
import json


def implied_carry(spot, future, days):
    if spot <= 0 or future <= 0 or days <= 0:
        raise ValueError("Positive prices and strictly positive remaining days required")
    return log(float(future / spot)) * 365.0 / days


def fixed_package_pnl(spot0, future0, spot1, future1, quantity=D(1)):
    return quantity * ((spot1 - spot0) + (future0 - future1))


def examples():
    s0, f0, d0 = D(100000), D(103000), 90
    r0 = implied_carry(s0, f0, d0)
    assert isclose(r0, 0.11987736464626352, abs_tol=1e-14)

    fa = float(s0) * exp(r0 * 60 / 365)
    pa = float(f0 - s0) - (fa - float(s0))
    assert isclose(fa, 101990.13104567814, abs_tol=1e-8)
    assert isclose(pa, 1009.868954321864, abs_tol=1e-8)

    sb, fb = D(120000), D(123100)
    rb = implied_carry(sb, fb, 80)
    pb = fixed_package_pnl(s0, f0, sb, fb)
    assert rb < r0 and pb == D(-100)
    for terminal in [D(50000), D(100000), D(180000)]:
        assert fixed_package_pnl(s0, f0, terminal, terminal) == D(3000)
    try:
        implied_carry(D(180000), D(180000), 0)
        raise AssertionError("Expiry rate must not be defined as zero")
    except ValueError:
        pass

    a0, b0, a1, b1, hedge = D(105), D(50), D(54), D(25), D(2)
    ratios = [a0 / b0, a1 / b1]
    spreads = [a0 - hedge * b0, a1 - hedge * b1]
    basket_pnl = (a1 - a0) - hedge * (b1 - b0)
    assert ratios == [D("2.1"), D("2.16")]
    assert spreads == [D(5), D(4)] and basket_pnl == D(-1)

    constant_spread, mean = D(5), D(0)
    zscores = [(constant_spread - mean) / s for s in [D(1), D("2.5")]]
    assert zscores == [D(5), D(2)]

    # Assumed conditional means, not estimates from observed data.
    # y is the next change in one underlying's price, not the change in x.
    maps = []
    for x in [D(-2), D(-1), D(0), D(1), D(2)]:
        maps.append({"x": str(x), "reversal_mean_change": str(-D("0.6") * x),
                     "continuation_mean_change": str(D("0.6") * x),
                     "no_predictive_mean_change": "0"})

    return {
        "scope": "Synthetic identities and assumed response curves; no empirical strategy validation",
        "entry": {"spot": str(s0), "future": str(f0), "days": d0,
                  "continuous_rate": r0, "simple_annualized_rate": float((f0 / s0 - 1) * D(365) / D(d0)),
                  "basis": str(f0 - s0), "spot_units": 1, "linear_future_base_units": -1},
        "alternative_cases": [
            {"case": "A", "spot": float(s0), "future": fa, "days": 60,
             "rate": r0, "basis": fa - float(s0), "price_pnl": pa},
            {"case": "B", "spot": str(sb), "future": str(fb), "days": 80,
             "rate": rb, "basis": str(fb - sb), "price_pnl": str(pb)},
            {"case": "aligned_expiry", "spot": 180000, "future": 180000, "days": 0,
             "rate": None, "basis": 0, "price_pnl": 3000}],
        "ratio_and_basket": {"A": [str(a0), str(a1)], "B": [str(b0), str(b1)],
                             "ratio": [str(v) for v in ratios], "fixed_basket": [str(v) for v in spreads],
                             "holdings": [1, -2], "price_pnl": str(basket_pnl)},
        "normalization_only": {"spread": [5, 5], "mean": [0, 0], "scale": [1, 2.5],
                               "z": [str(v) for v in zscores], "price_pnl": 0},
        "assumed_response_maps": maps,
        "assumptions": ["Fixed holdings and aligned linear contract units",
                        "Price P&L excludes financing, fees, other carry and capital costs",
                        "Constant-rate path also holds spot constant",
                        "Alternative cases are not one sequential market path"],
        "checks": "Exact Decimal identities and numerical log/exp checks passed",
    }


if __name__ == "__main__":
    print(json.dumps(examples(), ensure_ascii=False, indent=2))
