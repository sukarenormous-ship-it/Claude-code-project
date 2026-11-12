"""Chapter 3: original, synthetic cash-and-holdings accounting examples.

Run with Python 3: python ch03_ledger_demo.py
No market data, network access, broker connection, or strategy backtest is used.
One currency; unit multiplier = 1; idealized cash instruments with shorting.
Cash includes short-sale proceeds for accounting; it is NOT available margin.
The script separately models cash fees and fill-price effects, never both for
the same execution cost. All assumptions and costs are illustrative.
"""

from dataclasses import dataclass, field
from decimal import Decimal
import json


def D(value):
    return Decimal(str(value))


def check(actual, expected, label):
    if actual != D(expected):
        raise AssertionError(f"{label}: {actual} != {expected}")


@dataclass
class Account:
    cash: Decimal
    quantity: dict = field(default_factory=lambda: {"A": D(0), "B": D(0)})

    def fill(self, symbol, signed_quantity, fill_price, cash_fee=0):
        """Positive quantity buys; negative quantity sells or opens a short."""
        delta, price, fee = D(signed_quantity), D(fill_price), D(cash_fee)
        self.cash -= delta * price + fee
        self.quantity[symbol] += delta

    def charge(self, cash_cost):
        self.cash -= D(cash_cost)

    def holdings_value(self, marks):
        return sum((q * marks[s] for s, q in self.quantity.items()), D(0))

    def equity(self, marks):
        return self.cash + self.holdings_value(marks)

    def snapshot(self, marks):
        return {"cash": self.cash, "quantity": dict(self.quantity),
                "holdings_value": self.holdings_value(marks),
                "equity": self.equity(marks)}


def open_pair():
    account = Account(D(1000))
    account.fill("A", 10, 100)
    account.fill("B", -20, 50)
    return account


def main():
    p0 = {"A": D(100), "B": D(50)}
    p1 = {"A": D(102), "B": D("50.5")}

    # 1. Fixed units: compare per-leg P&L with independently updated cash.
    fixed = open_pair()
    start = fixed.snapshot(p0)
    leg_pnl = {s: fixed.quantity[s] * (p1[s] - p0[s]) for s in p0}
    gross_pnl = sum(leg_pnl.values())
    h = D(2)  # units of B per unit of A in this price-spread example
    spread0, spread1 = p0["A"] - h * p0["B"], p1["A"] - h * p1["B"]
    check(gross_pnl, 10, "per-leg gross P&L")
    check(fixed.equity(p1) - start["equity"], gross_pnl, "marked equity change")
    check(D(10) * (spread1 - spread0), gross_pnl, "fixed-h spread change")
    fixed.fill("A", -10, p1["A"])
    fixed.fill("B", 20, p1["B"])
    check(fixed.cash, 1010, "cash after closing both legs")

    # 2. Cash-only cost budget: entry 4, holding 3, exit 5; fills equal marks.
    # These costs do not additionally include a second slippage deduction.
    costed = open_pair()
    cost_ledger = [{"event": "opened_before_costs", **costed.snapshot(p0)}]
    costed.charge(4)
    cost_ledger.append({"event": "after_entry_cost", **costed.snapshot(p0)})
    costed.charge(3)
    cost_ledger.append({"event": "after_price_move_and_holding_cost",
                        **costed.snapshot(p1)})
    costed.fill("A", -10, p1["A"])
    costed.fill("B", 20, p1["B"])
    costed.charge(5)
    cost_ledger.append({"event": "closed_after_exit_cost", **costed.snapshot(p1)})
    net_pnl = costed.cash - D(1000)
    check(net_pnl, -2, "net P&L from final cash")
    check(gross_pnl - D(4 + 3 + 5), net_pnl, "gross less cash costs")
    check(cost_ledger[1]["equity"], 996, "entry equity")
    check(cost_ledger[2]["equity"], 1003, "holding equity")

    # 3. Re-estimating a model changes no holdings or account cash by itself.
    unchanged = open_pair()
    old_h, new_h = D(2), D("1.8")
    old_spread = p0["A"] - old_h * p0["B"]
    new_spread = p0["A"] - new_h * p0["B"]
    check(new_spread - old_spread, 10, "parameter-only spread change")
    check(unchanged.equity(p0), 1000, "parameter-only unchanged equity")

    # 4. Actual hedge adjustment: buy back 2 B at the unchanged mark.
    rebalanced = open_pair()
    rebalance_before = rebalanced.snapshot(p0)
    rebalanced.fill("B", 2, 50)
    rebalance_after = rebalanced.snapshot(p0)
    check(rebalanced.cash, 900, "cash pays for hedge adjustment")
    check(rebalanced.holdings_value(p0), 100, "new marked holdings value")
    check(rebalanced.equity(p0), 1000, "self-financing rebalance before fee")
    rebalanced.charge(1)
    check(rebalanced.equity(p0), 999, "rebalance fee reduces equity")

    # 5. Fill prices already contain execution drag relative to marks.
    slipped = Account(D(1000))
    slipped.fill("A", 10, "100.1")
    slipped.fill("B", -20, "49.95")
    execution_drag = D(10) * (D("100.1") - p0["A"]) + D(20) * (p0["B"] - D("49.95"))
    check(execution_drag, 2, "execution drag at entry")
    check(slipped.equity(p0), 998, "fill-based entry equity")
    check(slipped.equity(p1), 1008, "later equity without double-counting drag")

    # 6. A partially filled target does not create the requested exposure.
    partial = Account(D(1000))
    partial.fill("A", 10, 100)
    partial.fill("B", -8, 50)  # target was -20; only -8 has actually filled
    partial_pnl = partial.equity(p1) - partial.equity(p0)
    check(partial_pnl, 16, "P&L from actual fills, not target holdings")

    result = {
        "data_status": "original synthetic accounting examples; no alpha test",
        "fixed_hedge": {"start": start, "leg_pnl": leg_pnl,
                        "spread_before": spread0, "spread_after": spread1,
                        "gross_pnl": gross_pnl, "closing_cash": fixed.cash,
                        "gross_exposure_before_costs": D(2000),
                        "gross_exposure_to_equity_before_costs": D(2)},
        "cost_ledger": cost_ledger,
        "net_pnl": net_pnl,
        "net_return_on_initial_equity": net_pnl / D(1000),
        "parameter_only": {"h_before": old_h, "h_after": new_h,
                           "spread_before": old_spread, "spread_after": new_spread,
                           "actual_equity": unchanged.equity(p0), "price_pnl": D(0)},
        "rebalance": {"before": rebalance_before, "after_before_fee": rebalance_after,
                      "after_fee": rebalanced.snapshot(p0)},
        "execution_slippage": {"entry_snapshot": slipped.snapshot(p0),
                               "entry_drag_already_in_cash": execution_drag,
                               "later_equity": slipped.equity(p1)},
        "partial_fill": {"actual_start": partial.snapshot(p0),
                         "actual_price_pnl": partial_pnl,
                         "fully_filled_target_price_pnl": gross_pnl},
        "checks": "all exact Decimal checks passed"
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
