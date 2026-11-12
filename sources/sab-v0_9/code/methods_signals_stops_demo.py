"""Exact synthetic examples for replication, forecasts, and observed-bar exits.

This is educational arithmetic and a small deterministic state machine. It is
not a market-data backtest, order-book simulator, or broker execution engine.
All prices and probabilities are supplied assumptions. Entry and exit fills
are assumed to occur at the observed prices, after the observation is known;
this deliberately idealized convention does not claim maker-order fills.
"""

from decimal import Decimal
import json


D = Decimal
ZERO = D("0")


def decimal_string(value):
    """Keep exact decimal values readable, without binary floating-point tails."""
    return "0" if value == 0 else format(value.normalize(), "f")


def serializable(value):
    if isinstance(value, Decimal):
        return decimal_string(value)
    if isinstance(value, dict):
        return {key: serializable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serializable(item) for item in value]
    return value


def replication_example():
    strike, spot, call_price, put_price, rate = map(D, ["100", "102", "6", "4", "0"])
    cash = strike  # At r = 0, cash 100 today is cash 100 at this common expiry.
    initial_synthetic_cost = call_price - put_price + cash
    assert initial_synthetic_cost == spot == D("102")
    rows = []
    for terminal_price in map(D, ["80", "100", "120"]):
        long_call = max(terminal_price - strike, ZERO)
        short_put = -max(strike - terminal_price, ZERO)
        option_pair = long_call + short_put
        synthetic = option_pair + cash
        pnl = synthetic - initial_synthetic_cost
        assert option_pair == terminal_price - strike
        assert synthetic == terminal_price
        assert pnl == terminal_price - spot
        rows.append({"terminal_stock_price": terminal_price, "long_call_payoff": long_call,
                     "short_put_payoff": short_put, "option_pair_payoff": option_pair,
                     "cash_at_expiry": cash, "synthetic_payoff": synthetic,
                     "stock_payoff": terminal_price, "pnl_of_either_position": pnl})
    assert [row["pnl_of_either_position"] for row in rows] == list(map(D, ["-22", "-2", "18"]))
    return {
        "assumptions": ["European call and put: same underlying, strike, expiry, currency and unit size",
                        "Non-dividend-paying underlying; continuously compounded interest rate is zero",
                        "No fees, financing frictions, default or early exercise in this payoff identity"],
        "strike": strike, "spot_price": spot, "call_premium": call_price,
        "put_premium": put_price, "interest_rate": rate, "cash_today": cash,
        "initial_synthetic_cost": initial_synthetic_cost,
        "identity": "max(S_T-K,0) - max(K-S_T,0) + K = S_T",
        "interpretation": "Equal initial costs and terminal payoffs; this example does not show a pricing arbitrage.",
        "rows": rows,
    }


def forecast_examples():
    q_a, q_b = D("10"), D("-10")
    expected_delta_a, expected_delta_b = D("0.8"), D("0.2")
    cost, risk_buffer = D("3"), D("1")
    gross = q_a * expected_delta_a + q_b * expected_delta_b
    expected_net = gross - cost
    margin = expected_net - risk_buffer
    assert (gross, expected_net, margin) == (D("6"), D("3"), D("2"))

    probability_win, win, loss, separate_cost = map(D, ["0.65", "1", "3", "0.1"])
    before_cost = probability_win * win - (D("1") - probability_win) * loss
    after_cost = before_cost - separate_cost
    assert before_cost == D("-0.4") and after_cost == D("-0.5")
    return {
        "fixed_quantity_forecast": {
            "quantities": {"A": q_a, "B": q_b},
            "expected_price_changes_over_same_horizon": {"A": expected_delta_a, "B": expected_delta_b},
            "forecast_gross_pnl": gross, "forecast_roundtrip_cost": cost,
            "forecast_net_before_risk_buffer": expected_net,
            "decision_risk_buffer": risk_buffer, "decision_margin": margin,
            "interpretation": "All are decision-time assumptions. The risk buffer is a policy hurdle, not a cash expense. No realized P&L is supplied.",
        },
        "separate_win_probability_example": {
            "probability_win": probability_win, "gross_pnl_if_win": win,
            "gross_pnl_if_loss": -loss, "cost_in_each_outcome": separate_cost,
            "expected_gross_pnl": before_cost, "expected_net_pnl": after_cost,
            "interpretation": "A separate hypothetical payoff distribution: 65% wins does not imply positive expected net profit.",
        },
    }


class SyntheticExitPolicy:
    """Fixed-quantity positions with frozen signal parameters and explicit pause.

    A = 100 + X, B = 100, X = A - B, mu = 0, sigma = 1. Side -1 is
    short 10 basket units, hence q_A=-10 and q_B=+10. Side +1 mirrors it.
    The three-bar clock counts observations AFTER the entry observation.
    Loss checks use hypothetical liquidation P&L including the unpaid exit
    fee; that exit fee becomes an actual cash charge only when the trade exits.
    Exit priority is loss limit, signal recovery, then elapsed-time limit.
    """

    def __init__(self, side=-1):
        if side not in (-1, 1):
            raise ValueError("side must be -1 (short basket) or +1 (long basket)")
        self.side = side
        self.units = D("10")
        self.mean, self.sigma = ZERO, D("1")
        self.entry_level, self.exit_level = D("2"), D("0.5")
        self.loss_limit, self.max_bars = D("15"), 3
        self.entry_cost, self.exit_cost = D("0.4"), D("0.6")
        self.position = None
        self.entries_paused = False
        self.pause_reason = None
        self.last_bar = -1
        self.observations, self.trades, self.resume_attempts = [], [], []

    @property
    def state(self):
        if self.position is not None:
            name = "OPEN_SHORT" if self.side == -1 else "OPEN_LONG"
            return name + ("_ENTRIES_PAUSED" if self.entries_paused else "")
        return "FLAT_PAUSED" if self.entries_paused else "FLAT"

    @staticmethod
    def prices(x):
        return {"A": D("100") + x, "B": D("100")}

    def pause_entries(self, reason):
        """Persist the entry gate without silently dropping an existing position."""
        self.entries_paused, self.pause_reason = True, reason

    def resume(self, *, explicit_request, checks_passed):
        if not explicit_request:
            reason = "explicit_request_required"
        elif self.position is not None:
            reason = "position_must_be_flat"
        elif not checks_passed:
            reason = "checks_not_passed"
        elif not self.entries_paused:
            reason = "not_paused"
        else:
            self.entries_paused, self.pause_reason = False, None
            reason = "resumed_flat_after_checks"
        outcome = {"accepted": reason == "resumed_flat_after_checks", "reason": reason,
                   "state_after": self.state}
        self.resume_attempts.append(outcome)
        return outcome

    def observe(self, bar, x):
        x = D(str(x))
        if bar <= self.last_bar:
            raise ValueError("Observation indices must increase strictly")
        self.last_bar = bar
        z = (x - self.mean) / self.sigma
        prices = self.prices(x)
        record = {"bar": bar, "x": x, "z": z, "prices": prices,
                  "state_before": self.state}

        if self.position is not None:
            p = self.position
            elapsed = bar - p["entry_bar"]
            gross = sum(p["quantities"][name] * (prices[name] - p["entry_prices"][name])
                        for name in ("A", "B"))
            assert gross == D(self.side) * self.units * (x - p["entry_x"])
            liquidation_pnl = gross - self.entry_cost - self.exit_cost
            record.update({"elapsed_bars": elapsed, "gross_price_pnl": gross,
                           "mark_pnl_after_paid_entry_fee": gross - self.entry_cost,
                           "net_liquidation_pnl_if_exit_now": liquidation_pnl})
            recovered = (z <= self.exit_level if self.side == -1 else z >= -self.exit_level)
            if liquidation_pnl <= -self.loss_limit:
                reason = "loss_limit"
            elif recovered:
                reason = "signal_recovery"
            elif elapsed >= self.max_bars:
                reason = "time_limit"
            else:
                reason = None
            if reason is not None:
                exit_cashflow = sum(p["quantities"][name] * prices[name] for name in ("A", "B")) - self.exit_cost
                net_cashflow = p["entry_cashflow"] + exit_cashflow
                assert net_cashflow == liquidation_pnl
                trade = {**p, "exit_bar": bar, "exit_x": x, "exit_prices": prices,
                         "elapsed_bars": elapsed, "exit_reason": reason,
                         "gross_price_pnl": gross, "entry_fee": self.entry_cost,
                         "exit_fee": self.exit_cost, "exit_cashflow": exit_cashflow,
                         "net_pnl": liquidation_pnl, "sum_of_trade_cashflows": net_cashflow}
                self.trades.append(trade)
                self.position = None
                if reason == "loss_limit":
                    self.pause_entries("loss_limit_exit")
                record.update({"event": "exit", "reason": reason,
                               "event_cashflow": exit_cashflow})
            else:
                record["event"] = "hold"
        elif self.entries_paused:
            record.update({"event": "entry_blocked_by_pause", "reason": self.pause_reason})
        else:
            triggered = (z >= self.entry_level if self.side == -1 else z <= -self.entry_level)
            if triggered:
                q_a, q_b = D(self.side) * self.units, -D(self.side) * self.units
                quantities = {"A": q_a, "B": q_b}
                entry_cashflow = -sum(quantities[name] * prices[name] for name in ("A", "B")) - self.entry_cost
                self.position = {"entry_bar": bar, "entry_x": x, "entry_prices": prices,
                                 "quantities": quantities, "entry_cashflow": entry_cashflow}
                record.update({"event": "entry", "reason": "signal_threshold",
                               "quantities": quantities, "event_cashflow": entry_cashflow})
            else:
                record["event"] = "flat"
        record["state_after"] = self.state
        self.observations.append(record)
        return record

    def snapshot(self):
        return {"side": "short" if self.side == -1 else "long", "final_state": self.state,
                "observations": list(self.observations), "trades": list(self.trades)}


def run_path(values, side=-1):
    policy = SyntheticExitPolicy(side=side)
    for bar, x in enumerate(values):
        policy.observe(bar, x)
    return policy


def stops_examples():
    paths = {
        "convergence": ["0", "2.1", "1.7", "0.4"],
        "time": ["0", "2.1", "2.0", "1.9", "1.8"],
        "gap": ["0", "2.1", "2.8", "4.1"],
    }
    policies = {name: run_path(values) for name, values in paths.items()}
    expected = {"convergence": ("signal_recovery", D("16"), 3),
                "time": ("time_limit", D("2"), 4),
                "gap": ("loss_limit", D("-21"), 3)}
    for name, policy in policies.items():
        assert len(policy.trades) == 1 and policy.position is None
        trade = policy.trades[0]
        assert (trade["exit_reason"], trade["net_pnl"], trade["exit_bar"]) == expected[name]
        assert trade["entry_bar"] == 1
    gap_trade = policies["gap"].trades[0]
    stop_x = D("2.1") + (D("15") - D("1")) / D("10")
    assert stop_x == D("3.5")
    assert -D("10") * (stop_x - D("2.1")) - D("1") == -D("15")
    assert gap_trade["net_pnl"] < -D("15")

    mirror = run_path(["0", "-2.1", "-1.7", "-0.4"], side=1)
    assert mirror.trades[0]["net_pnl"] == D("16")
    assert mirror.trades[0]["quantities"] == {"A": D("10"), "B": D("-10")}

    paused = run_path(paths["gap"])
    assert paused.state == "FLAT_PAUSED"
    for bar, x in [(4, "3.8"), (5, "2.4")]:
        observed = paused.observe(bar, x)
        assert observed["event"] == "entry_blocked_by_pause"
        assert paused.position is None and len(paused.trades) == 1
    assert not paused.resume(explicit_request=False, checks_passed=True)["accepted"]
    assert not paused.resume(explicit_request=True, checks_passed=False)["accepted"]
    assert paused.state == "FLAT_PAUSED"
    assert paused.resume(explicit_request=True, checks_passed=True)["accepted"]
    assert paused.state == "FLAT" and paused.position is None

    # Pausing entries is separate from monitoring and closing existing risk.
    open_pause = run_path(["0", "2.1"])
    open_pause.pause_entries("independent_risk_review")
    denied_while_open = open_pause.resume(explicit_request=True, checks_passed=True)
    assert denied_while_open["reason"] == "position_must_be_flat"
    open_pause.observe(2, "0.4")
    assert open_pause.state == "FLAT_PAUSED" and open_pause.trades[0]["net_pnl"] == D("16")
    assert open_pause.resume(explicit_request=True, checks_passed=True)["accepted"]
    return {
        "frozen_signal": {"definition": "X = A - B", "mean": ZERO, "sigma": D("1"),
                          "B_price": D("100"), "A_price": "100 + X"},
        "rules": {"short_entry_z_at_least": D("2"), "short_exit_z_at_most": D("0.5"),
                  "basket_units": D("10"), "entry_fee": D("0.4"), "exit_fee": D("0.6"),
                  "loss_limit_on_net_liquidation_pnl": D("15"), "max_bars_after_entry": 3,
                  "exit_precedence": ["loss_limit", "signal_recovery", "time_limit"],
                  "fill_convention": "Observe each bar, then assume entry/exit at that exact observed price. No intrabar prices, order book, queue or maker fills are modeled.",
                  "accounting_scope": "Fixed-quantity linear price P&L and two explicit fees only; no financing, borrow availability, margin, market impact or other cash flows modeled."},
        "short_loss_threshold_in_x_for_this_entry": stop_x,
        "loss_overshoot_in_gap_case": -gap_trade["net_pnl"] - D("15"),
        "paths": {name: policy.snapshot() for name, policy in policies.items()},
        "long_symmetry_check": mirror.snapshot(),
        "persistent_pause_demo": {"observations": paused.observations,
                                  "resume_attempts": paused.resume_attempts,
                                  "final_state": paused.state,
                                  "blocked_entry_observations": 2,
                                  "closed_trade_count": len(paused.trades),
                                  "resume_attempt_while_open": denied_while_open,
                                  "existing_position_still_monitored_while_entries_paused": True,
                                  "interpretation": "Reaching a new entry signal does not clear a pause. Only an explicit request after flatness and successful checks re-arms entries; no new trade is automatically submitted by resume()."},
    }


def examples():
    return serializable({
        "scope": "Synthetic payoff identities, supplied forecasts and deterministic observed-bar rules only; no market-data fitting, strategy backtest or broker engine.",
        "replication": replication_example(), "forecast": forecast_examples(),
        "stops": stops_examples(),
        "checks_passed": ["European option/cash payoff identity and equal initial cost",
                          "Forecast gross, expected net and policy margin remain distinct",
                          "65 percent win probability can have negative expected net P&L",
                          "Each stopped trade reconciles fixed-quantity price P&L with cash flows",
                          "Convergence, elapsed-time and gap-loss exits use observed prices",
                          "Mirrored long-basket case has exact net P&L 16",
                          "Entry pause persists and explicit resume requires flatness and checks"],
    })


if __name__ == "__main__":
    result = examples()
    print(json.dumps({
        "scope": "Synthetic identities and state transitions; no market-data backtest",
        "replicated_expiry_payoffs": [row["synthetic_payoff"] for row in result["replication"]["rows"]],
        "forecast_gross_expected_net_decision_margin": [result["forecast"]["fixed_quantity_forecast"][key]
            for key in ["forecast_gross_pnl", "forecast_net_before_risk_buffer", "decision_margin"]],
        "separate_high_win_rate_expected_net": result["forecast"]["separate_win_probability_example"]["expected_net_pnl"],
        "exit_cases_net_pnl": {name: data["trades"][0]["net_pnl"] for name, data in result["stops"]["paths"].items()},
        "long_symmetry_net_pnl": result["stops"]["long_symmetry_check"]["trades"][0]["net_pnl"],
        "pause_checks": "passed", "checks": "all exact Decimal checks passed",
    }, ensure_ascii=False, separators=(",", ":")))
