"""Illustrative conditional expectations, not a fitted model or a backtest."""
from decimal import Decimal as D
from math import log, isclose
import json


def conditional_level(phi, start, periods):
    return start * phi ** periods


def mean_half_life(phi):
    """Periods for the conditional-mean deviation to halve, for 0 < phi < 1."""
    if not D(0) < phi < D(1):
        return None
    return -log(2) / log(float(phi))


def examples():
    start, units, cost, horizon = D(2), D(10), D(1), 4
    expected_net = {
        D("0.8"): D("10.808"),
        D("0.99"): D("-0.2119202"),
        D("1"): D("-1"),
        D("1.02"): D("-2.6486432"),
    }
    rows = []
    for phi in expected_net:
        end = conditional_level(phi, start, horizon)
        gross = units * (start - end)  # short a fixed basket, no rebalancing
        net = gross - cost
        assert net == expected_net[phi]
        rows.append({
            "phi": str(phi),
            "expected_next_level": str(conditional_level(phi, start, 1)),
            "expected_level_after_4_periods": str(end),
            "mean_half_life_periods": mean_half_life(phi),
            "expected_gross_pnl": str(gross),
            "expected_net_pnl": str(net),
        })
    assert isclose(mean_half_life(D("0.8")), 3.1062837195053903)
    assert isclose(mean_half_life(D("0.99")), 68.96756393652842)
    oscillating = [conditional_level(D("-0.5"), start, h) for h in range(5)]
    assert oscillating == [D(2), D(-1), D("0.5"), D("-0.25"), D("0.125")]
    marks = [D(10)] * 3
    estimated_means = [D(0), D(8), D(10)]
    residuals = [s - m for s, m in zip(marks, estimated_means)]
    actual_price_pnl = -units * (marks[-1] - marks[0])
    assert residuals == [D(10), D(2), D(0)] and actual_price_pnl == 0
    return {
        "scope": "Exact conditional expectations under assumed AR(1) coefficients; no market data or strategy validation.",
        "assumptions": {
            "conditional_innovation_mean": 0,
            "reference_mean": 0,
            "starting_spread_money_per_basket_unit": str(start),
            "fixed_short_basket_units": str(units),
            "exit_after_periods": horizon,
            "illustrative_total_cost_money": str(cost),
            "holding_weights": "fixed; fill and mark conventions assumed identical",
        },
        "ar_cases": rows,
        "negative_phi_example": [str(x) for x in oscillating],
        "moving_mean": {
            "spread_marks": [str(x) for x in marks],
            "estimated_means": [str(x) for x in estimated_means],
            "computed_residuals": [str(x) for x in residuals],
            "actual_price_pnl_fixed_holdings": str(actual_price_pnl),
        },
        "checks": "Exact arithmetic and half-life checks passed",
    }


if __name__ == "__main__":
    print(json.dumps(examples(), ensure_ascii=False, indent=2))
