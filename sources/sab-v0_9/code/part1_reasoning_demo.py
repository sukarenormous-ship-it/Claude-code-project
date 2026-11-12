"""Exact synthetic examples for the first part of the Stat Arb learning book.

No market data, fitted model, backtest, or order submission is involved.
The forecast is a comparison value, not a cash flow. Factor scenarios are
independent one-period experiments with fixed quantities and linear returns.
"""
from decimal import Decimal as D
from fractions import Fraction as F
import json


def price_pnl(quantities, entry_prices, exit_prices):
    return sum(q * (end - start)
               for q, start, end in zip(quantities, entry_prices, exit_prices))


def rref(matrix):
    """Exact reduced row-echelon form and pivot columns, using Fractions."""
    rows = [[F(value) for value in row] for row in matrix]
    pivots, row_index = [], 0
    for column in range(len(rows[0])):
        pivot = next((i for i in range(row_index, len(rows))
                      if rows[i][column]), None)
        if pivot is None:
            continue
        rows[row_index], rows[pivot] = rows[pivot], rows[row_index]
        divisor = rows[row_index][column]
        rows[row_index] = [value / divisor for value in rows[row_index]]
        for i in range(len(rows)):
            if i == row_index:
                continue
            factor = rows[i][column]
            rows[i] = [value - factor * pivot_value
                       for value, pivot_value in zip(rows[i], rows[row_index])]
        pivots.append(column)
        row_index += 1
        if row_index == len(rows):
            break
    return rows, pivots


def nullspace(matrix):
    reduced, pivots = rref(matrix)
    free_columns = [j for j in range(len(matrix[0])) if j not in pivots]
    vectors = []
    for free in free_columns:
        vector = [F(0)] * len(matrix[0])
        vector[free] = F(1)
        for row, pivot in enumerate(pivots):
            vector[pivot] = -reduced[row][free]
        vectors.append(vector)
    return vectors


def determinant3(matrix):
    a, b, c = matrix[0]
    d, e, f = matrix[1]
    g, h, i = matrix[2]
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def exposures(weights, beta, gamma):
    return {
        "net_dollars": sum(weights),
        "gross_notional": sum(abs(weight) for weight in weights),
        "market_beta_dollars": sum(w * b for w, b in zip(weights, beta)),
        "gamma_factor_dollars": sum(w * g for w, g in zip(weights, gamma)),
    }


def factor_stress(weights, prices, beta, gamma, market=F(0),
                  gamma_return=F(0), specific=None):
    """r = beta * market + gamma * gamma_return + specific, all exact."""
    specific = specific if specific is not None else [F(0)] * len(weights)
    returns = [b * market + g * gamma_return + e
               for b, g, e in zip(beta, gamma, specific)]
    pnl_by_asset = [w * r for w, r in zip(weights, returns)]
    quantities = [w / p for w, p in zip(weights, prices)]
    price_changes = [p * r for p, r in zip(prices, returns)]
    # Two accounting representations must describe the same fixed holdings.
    assert sum(pnl_by_asset) == sum(q * dp for q, dp in zip(quantities, price_changes))
    return {"asset_returns": returns, "pnl_by_asset": pnl_by_asset,
            "price_pnl": sum(pnl_by_asset)}


def exact_values(values):
    return [str(value) for value in values]


def stress_record(name, result, **conditions):
    return {"name": name, "conditions": conditions,
            "asset_returns_exact": exact_values(result["asset_returns"]),
            "pnl_by_asset_exact": exact_values(result["pnl_by_asset"]),
            "price_pnl_exact": str(result["price_pnl"]),
            "price_pnl": float(result["price_pnl"])}


def examples():
    quantities = [D(10), D(-20)]
    entry_mid = [D(100), D(50)]
    forecast_exit = [D(102), D("50.4")]
    realized_exit = [D(102), D("50.6")]
    actual_entry_fills = [D("100.2"), D("49.95")]
    forecast_gross = price_pnl(quantities, entry_mid, forecast_exit)
    realized_ideal_gross = price_pnl(quantities, entry_mid, realized_exit)
    actual_gross = price_pnl(quantities, actual_entry_fills, realized_exit)
    fill_difference = actual_gross - realized_ideal_gross
    fees, holding_carry = D(2), D(1)
    actual_net = actual_gross - fees - holding_carry
    assert (forecast_gross, realized_ideal_gross, actual_gross, actual_net) == (
        D(12), D(8), D(5), D(2))
    assert fill_difference == D(-3)
    assert realized_ideal_gross + fill_difference - fees - holding_carry == actual_net
    assert sum(-q * (fill - mid)
               for q, fill, mid in zip(quantities, actual_entry_fills, entry_mid)) == fill_difference

    weights3 = [F(5000), F(5000), F(-10000)]
    beta3 = [F(6, 5), F(4, 5), F(1)]
    gamma3 = [F(1, 2), F(-1, 2), F(1, 5)]
    prices3 = [F(100), F(50), F(200)]
    exposure3 = exposures(weights3, beta3, gamma3)
    assert exposure3 == {"net_dollars": 0, "gross_notional": 20000,
                         "market_beta_dollars": 0, "gamma_factor_dollars": -2000}
    quantities3 = [w / p for w, p in zip(weights3, prices3)]
    assert quantities3 == [F(50), F(100), F(-50)]

    market_stress = factor_stress(weights3, prices3, beta3, gamma3, market=F(-1, 20))
    gamma_stress = factor_stress(weights3, prices3, beta3, gamma3, gamma_return=F(3, 100))
    specific_stress = factor_stress(weights3, prices3, beta3, gamma3,
                                    specific=[F(0), F(-1, 50), F(0)])
    updated_beta3 = [F(7, 5), beta3[1], beta3[2]]
    updated_exposure3 = exposures(weights3, updated_beta3, gamma3)
    changed_beta_stress = factor_stress(weights3, prices3, updated_beta3,
                                       gamma3, market=F(-1, 20))
    assert [r["price_pnl"] for r in [market_stress, gamma_stress, specific_stress,
                                     changed_beta_stress]] == [F(0), F(-60), F(-100), F(-50)]
    assert updated_exposure3["market_beta_dollars"] == F(1000)

    matrix3 = [[F(1)] * 3, beta3, gamma3]
    _, pivots3 = rref(matrix3)
    assert len(pivots3) == 3 and nullspace(matrix3) == []
    assert determinant3(matrix3) == F(-2, 25)

    beta4 = beta3 + [F(11, 10)]
    gamma4 = gamma3 + [F(-1, 5)]
    prices4 = prices3 + [F(80)]
    matrix4 = [[F(1)] * 4, beta4, gamma4]
    _, pivots4 = rref(matrix4)
    basis4 = nullspace(matrix4)
    assert len(pivots4) == 3 and len(basis4) == 1
    direction = basis4[0]
    if direction[0] < 0:
        direction = [-value for value in direction]
    weights4 = [value * F(20000) / sum(abs(v) for v in direction) for value in direction]
    expected_weights4 = [F(75000, 13), F(55000, 13), F(-90000, 13), F(-40000, 13)]
    assert weights4 == expected_weights4
    integer_direction = [F(15), F(11), F(-18), F(-8)]
    assert all(sum(a * b for a, b in zip(row, integer_direction)) == 0 for row in matrix4)
    exposure4 = exposures(weights4, beta4, gamma4)
    assert exposure4 == {"net_dollars": 0, "gross_notional": 20000,
                         "market_beta_dollars": 0, "gamma_factor_dollars": 0}
    quantities4 = [w / p for w, p in zip(weights4, prices4)]
    assert quantities4 == [F(750, 13), F(1100, 13), F(-450, 13), F(-500, 13)]
    specific4 = factor_stress(weights4, prices4, beta4, gamma4,
                             specific=[F(0), F(-1, 50), F(0), F(0)])
    assert specific4["price_pnl"] == F(-1100, 13)

    return {
        "scope": "Reproducible synthetic identities only; no data fitting, alpha estimate, or backtest",
        "bridge": {
            "assets": ["A", "B"], "fixed_quantities": exact_values(quantities),
            "timing": {"entry_reference": "Decision-time mids at t0",
                       "entry_fills": "Illustrative later fills, after the decision",
                       "exit": "A common later exit time; exit marks and fills coincide by assumption"},
            "entry_mid": exact_values(entry_mid), "forecast_exit": exact_values(forecast_exit),
            "realized_exit_marks_and_fills": exact_values(realized_exit),
            "actual_entry_fills": exact_values(actual_entry_fills),
            "forecast_gross": str(forecast_gross), "realized_ideal_mid_gross": str(realized_ideal_gross),
            "actual_fill_gross": str(actual_gross), "fill_price_difference": str(fill_difference),
            "fees": str(fees), "holding_carry_cost": str(holding_carry), "actual_net": str(actual_net),
            "realized_bridge": "8 - 3 - 2 - 1 = 2",
            "forecast_comparison_gap": str(realized_ideal_gross - forecast_gross),
            "interpretation": [
                "Forecast gross 12 is not booked as cash or realized profit.",
                "The forecast-versus-realized gap is a diagnostic comparison, not a separate cash charge.",
                "This bridge fixes quantities and exit fills, changing entry prices before subtracting fees and carry.",
                "Entry mids are decision-time references; actual entry fills occur later and need not match those earlier quotes.",
                "No order-book path, queue model, or maker-fill eligibility is simulated; fill prices are illustrative inputs.",
                "Attribution is bookkeeping under specified counterfactuals, not a causal or order-independent decomposition.",
                "Fill-price impact is already included in actual gross 5; do not deduct it again as slippage.",
                "Fees 2 and holding carry 1 are separate assumed costs, charged once.",
            ],
        },
        "factor_model": {
            "equation": "r_i = beta_i * f_market + gamma_i * f_gamma + epsilon_i",
            "price_pnl_equation": "price_PnL = sum(w_i * r_i) = sum(q_i * price_change_i)",
            "weight_definition": "w_i = q_i * initial_price_i; signed USD notionals, not capital fractions",
            "three_asset": {
                "assets": ["A", "B", "C"], "weights_usd_exact": exact_values(weights3),
                "prices_exact": exact_values(prices3), "quantities_exact": exact_values(quantities3),
                "beta_exact": exact_values(beta3), "gamma_exact": exact_values(gamma3),
                "exposures_exact": {key: str(value) for key, value in exposure3.items()},
                "all_three_constraints_rank": len(pivots3),
                "all_three_constraints_determinant": str(determinant3(matrix3)),
                "all_three_constraints_nullity": 0,
                "updated_beta_A": str(updated_beta3[0]),
                "updated_market_beta_dollars": str(updated_exposure3["market_beta_dollars"]),
                "independent_stresses": [
                    stress_record("Market factor -5%", market_stress, market_return="-1/20"),
                    stress_record("Gamma factor +3%", gamma_stress, gamma_factor_return="3/100"),
                    stress_record("B-specific return -2%", specific_stress, B_specific_return="-1/50"),
                    stress_record("Beta A becomes 1.4, market -5%", changed_beta_stress,
                                  beta_A="7/5", market_return="-1/20"),
                ],
            },
            "four_asset": {
                "assets": ["A", "B", "C", "D"], "beta_exact": exact_values(beta4),
                "gamma_exact": exact_values(gamma4), "rank": len(pivots4), "nullity": len(basis4),
                "nullspace_integer_direction": exact_values(integer_direction),
                "weights_usd_exact": exact_values(weights4), "weights_usd": [float(w) for w in weights4],
                "prices_exact": exact_values(prices4), "quantities_exact": exact_values(quantities4),
                "exposures_exact": {key: str(value) for key, value in exposure4.items()},
                "B_specific_stress": stress_record("B-specific return -2%", specific4,
                                                    B_specific_return="-1/50"),
            },
            "interpretation": [
                "Each stress starts from the stated portfolio; the rows are independent, not a sequential or automatically additive path.",
                "The net, beta, and gamma constraints are independent for these particular loading matrices.",
                "A nonzero algebraic solution with four assets is not evidence of alpha or feasible execution.",
                "Borrowing, trade lots, liquidity, financing, fees, position limits, and changing loadings require additional checks.",
                "Specific asset risk remains after the three model constraints are satisfied.",
                "Gross notional 20000 is not a capital budget; a portfolio return requires a separately specified capital denominator.",
            ],
        },
        "checks": "Exact Decimal bridge and Fraction ranks, nullspaces, exposures, stresses, and quantity-price identities passed",
    }


if __name__ == "__main__":
    result = examples()
    bridge = result["bridge"]
    model = result["factor_model"]
    compact = {
        "scope": result["scope"],
        "bridge": {key: bridge[key] for key in ["forecast_gross", "realized_ideal_mid_gross",
                   "actual_fill_gross", "fill_price_difference", "fees", "holding_carry_cost", "actual_net"]},
        "three_asset_independent_stress_pnl": [row["price_pnl_exact"]
                   for row in model["three_asset"]["independent_stresses"]],
        "constraint_ranks": [model["three_asset"]["all_three_constraints_rank"], model["four_asset"]["rank"]],
        "constraint_nullities": [model["three_asset"]["all_three_constraints_nullity"], model["four_asset"]["nullity"]],
        "four_asset_weights_usd_exact": model["four_asset"]["weights_usd_exact"],
        "four_asset_quantities_exact": model["four_asset"]["quantities_exact"],
        "checks": result["checks"],
    }
    print(json.dumps(compact, ensure_ascii=False, separators=(",", ":")))
