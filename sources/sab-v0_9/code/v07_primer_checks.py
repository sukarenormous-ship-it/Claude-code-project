"""Exact checks for the beginner primer (chapter 0) added in version 0.7.

Synthetic arithmetic only; standard library only.
"""
import json
from decimal import Decimal as D


def main():
    out = {}
    # 00.02 long / short
    out["long_0.1_btc"] = D("0.1") * (D("102000") - D("100000"))
    out["short_0.1_btc"] = D("-0.1") * (D("102000") - D("100000"))
    assert out["long_0.1_btc"] == D("200") and out["short_0.1_btc"] == D("-200")
    # 00.04 leverage
    notional, margin = D("10000"), D("1000")
    out["leverage"] = notional / margin
    out["loss_5pct"] = notional * D("0.05")
    out["loss_5pct_share_of_margin"] = out["loss_5pct"] / margin
    out["loss_10pct"] = notional * D("0.10")
    assert out["leverage"] == 10 and out["loss_5pct"] == 500
    assert out["loss_5pct_share_of_margin"] == D("0.5") and out["loss_10pct"] == margin
    # 00.05 order book
    bid, ask, fee = D("99990"), D("100010"), D("0.0005")
    out["spread"] = ask - bid
    out["mid"] = (ask + bid) / 2
    out["round_trip_price_cost"] = bid - ask
    out["round_trip_fees"] = fee * (ask + bid)
    out["round_trip_total"] = out["round_trip_price_cost"] - out["round_trip_fees"]
    out["round_trip_total_bps_of_mid"] = -out["round_trip_total"] / out["mid"] * 10000
    assert out["spread"] == 20 and out["mid"] == 100000
    assert out["round_trip_fees"] == 100 and out["round_trip_total"] == -120
    assert out["round_trip_total_bps_of_mid"] == 12
    # 00.06 funding
    out["funding_short_1_btc"] = D("100000") * D("0.0001")
    assert out["funding_short_1_btc"] == 10
    # 00.07 self-check answers
    ans = {
        "q1": D("-0.5") * (D("98000") - D("100000")),
        "q2_notional": D("2000") * 5,
        "q2_loss": D("2000") * 5 * D("0.04"),
        "q2_share_of_margin": D("2000") * 5 * D("0.04") / D("2000"),
        "q3": D("50005") - D("49995"),
        "q4": D("2") * D("100000") * D("0.0001"),
        "q5": D("103000") - D("100000"),
    }
    assert ans == {"q1": 1000, "q2_notional": 10000, "q2_loss": 400, "q2_share_of_margin": D("0.2"), "q3": 10, "q4": 20, "q5": 3000}
    out["self_check"] = ans
    print(json.dumps(out, default=str, indent=1))


if __name__ == "__main__":
    main()
