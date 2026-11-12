"""Worked examples for chapters 6 and 7 (version 0.9).

Chapter 6: exact Decimal arithmetic for cash-and-carry and perp funding.
Chapter 7: seeded simulations of synthetic coin prices; no market data.
Standard library only.
"""
import json
import math
import random
from decimal import Decimal as D, ROUND_HALF_UP


def r2(x):
    return str(D(x).quantize(D("0.01"), rounding=ROUND_HALF_UP))


# ------------------------------------------------------------------ chapter 6
def carry_ladder():
    s0, f0, days, cap, fee, st, hurdle = D(100000), D(103000), D(90), D(125000), D("0.0005"), D(105000), D("0.04")
    basis = f0 - s0
    fees = fee * (s0 + f0 + st)
    net = basis - fees
    opp = cap * hurdle * days / 365
    out = {
        "simple_rate_on_spot_pct": r2(basis / s0 * 365 / days * 100),
        "continuous_rate_on_spot_pct": r2(D(math.log(103000 / 100000) * 365 / 90 * 100)),
        "price_return_on_capital_pct_yr": r2(basis / cap * 365 / days * 100),
        "fees": str(fees),
        "net": str(net),
        "net_on_capital_pct_yr": r2(net / cap * 365 / days * 100),
        "opportunity_cost": r2(opp),
        "excess": r2(net - opp),
        "excess_pct_yr": r2((net - opp) / cap * 365 / days * 100),
    }
    assert fees == D(154) and net == D(2846)
    return out


def early_close(hurdle):
    cap, fee = D(125000), D("0.0005")
    s30, f30, b0 = D(101000), D(101500), D(3000)
    b30 = f30 - s30
    pnl_to_date = b0 - b30
    close_fees = fee * (s30 + f30)
    hold_fee_at_expiry = fee * s30
    hold_extra = b30 - hold_fee_at_expiry + close_fees
    opp60 = cap * D(hurdle) * 60 / 365
    return {
        "hurdle": hurdle,
        "basis_day30": str(b30),
        "pnl_to_date": str(pnl_to_date),
        "close_fees_now": str(close_fees),
        "spot_fee_if_held": str(hold_fee_at_expiry),
        "extra_from_holding": str(hold_extra),
        "extra_pct_yr_on_capital": r2(hold_extra / cap * 365 / 60 * 100),
        "opportunity_60d": r2(opp60),
        "decision": "close" if opp60 > hold_extra else "hold",
    }


def funding_scenarios():
    mark, fee_total, cap = D(100000), D(80), D(125000)
    sc = {
        "A_flat": [D("0.0001")] * 90,
        "B_decay": [D("0.0003")] * 30 + [D("0.00005")] * 60,
        "C_flip": [D("0.0001")] * 45 + [D("-0.0001")] * 45,
        "D_whipsaw": ([D("0.0001")] * 5 + [D("-0.00005")] * 3) * 11 + [D("0.0001")] * 2,
    }
    out = {}
    for k, rates in sc.items():
        assert len(rates) == 90
        flows = [mark * r for r in rates]
        cum, c = [], D(0)
        for f in flows:
            c += f
            cum.append(c)
        out[k] = {"funding_total": str(c), "net": str(c - fee_total),
                  "net_pct_yr": r2((c - fee_total) / cap * 365 / 30 * 100),
                  "cumulative": [str(x) for x in cum]}

    def with_rule(rates, k=3, refee=D(80)):
        neg, c, exits, held = 0, D(0), 0, True
        for r in rates:
            if held:
                c += mark * r
                neg = neg + 1 if r < 0 else 0
                if neg >= k:
                    held, exits = False, exits + 1
        return c, exits

    for k in ("A_flat", "B_decay", "C_flip", "D_whipsaw"):
        c, ex = with_rule(sc[k])
        out[k]["rule_exit_after_3_negative"] = {"funding": str(c), "net": str(c - fee_total), "exited": bool(ex)}
    assert out["A_flat"]["net"] == "820.0000" and out["C_flip"]["net"] == "-80.0000"
    return out


# ------------------------------------------------------------------ chapter 7
def rw(rng, n, sd):
    x, out = 0.0, []
    for _ in range(n):
        x += rng.gauss(0, sd)
        out.append(x)
    return out


def ar1(rng, n, phi, sd):
    x, out = 0.0, []
    for _ in range(n):
        x = phi * x + rng.gauss(0, sd)
        out.append(x)
    return out


def corr(a, b):
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((y - mb) ** 2 for y in b)
    return cov / math.sqrt(va * vb)


def diff(x):
    return [b - a for a, b in zip(x, x[1:])]


def ar_fit(s):
    x, y = s[:-1], s[1:]
    mx, my = sum(x) / len(x), sum(y) / len(y)
    phi = sum((a - mx) * (b - my) for a, b in zip(x, y)) / sum((a - mx) ** 2 for a in x)
    return phi


def pair_h(rng, n):
    c = rw(rng, n, 0.03)
    a = [ci + ui for ci, ui in zip(c, rw(rng, n, 0.01))]
    b = [ci + ui for ci, ui in zip(c, rw(rng, n, 0.01))]
    return a, b


def pair_c(rng, n):
    c = rw(rng, n, 0.03)
    a = [ci + ui for ci, ui in zip(c, rw(rng, n, 0.01))]
    e = ar1(rng, n, 0.9, 0.03)
    b = [ai + ei for ai, ei in zip(a, e)]
    return a, b


def zstats(spread, nf):
    f = spread[:nf]
    m = sum(f) / nf
    sd = math.sqrt(sum((x - m) ** 2 for x in f) / (nf - 1))
    z = [(x - m) / sd for x in spread]
    cross = sum(1 for u, v in zip(z[:nf - 1], z[1:nf]) if (u > 0) != (v > 0))
    test = z[nf:]
    return z, cross, sum(1 for v in test if abs(v) <= 2) / len(test), max(abs(v) for v in test)


def population(seed=7, pairs=200):
    """Average behaviour of pairs with and without a long-run link."""
    rng = random.Random(seed)
    n, nf = 500, 250
    out, examples = {}, {}
    for name, maker in (("H_high_corr_no_link", pair_h), ("C_linked", pair_c)):
        rows = []
        for _ in range(pairs):
            a, b = maker(rng, n)
            s = [x - y for x, y in zip(a, b)]
            z, cross, inband, maxz = zstats(s, nf)
            rows.append({"corr": corr(diff(a), diff(b)), "phi_formation": ar_fit(s[:nf]),
                         "inband": inband, "maxz": maxz, "a": a, "b": b, "s": s})
        avg = lambda k: sum(r[k] for r in rows) / len(rows)
        out[name] = {
            "pairs": pairs,
            "return_corr_avg": round(avg("corr"), 3),
            "formation_ar1_phi_avg": round(avg("phi_formation"), 3),
            "test_share_inside_2sd_avg": round(avg("inband"), 3),
            "share_of_pairs_with_test_abs_z_above_3": round(sum(1 for r in rows if r["maxz"] > 3) / pairs, 3),
        }
        target = avg("inband")
        ex = min(rows, key=lambda r: abs(r["inband"] - target))
        examples[name] = {"return_corr": round(ex["corr"], 3), "test_inside": round(ex["inband"], 3),
                          "spread": [round(v, 5) for v in ex["s"]],
                          "ret_a": [round(v, 5) for v in diff(ex["a"])], "ret_b": [round(v, 5) for v in diff(ex["b"])]}
    out["typical_examples"] = examples
    return out


def selection_bias(seed=11, scanned=200, top=10, genuine=10):
    rng = random.Random(seed)
    n, nf = 500, 250
    rows = []
    for i in range(scanned):
        a, b = pair_h(rng, n)
        s = [x - y for x, y in zip(a, b)]
        z, cross, inband, maxz = zstats(s, nf)
        rows.append((cross, inband, maxz, z, corr(diff(a[:nf]), diff(b[:nf]))))
    rows.sort(key=lambda r: -r[0])
    best = rows[:top]
    gen = []
    for i in range(genuine):
        a, b = pair_c(rng, n)
        s = [x - y for x, y in zip(a, b)]
        z, cross, inband, maxz = zstats(s, nf)
        gen.append((cross, inband, maxz, z))
    avg = lambda xs: sum(xs) / len(xs)
    return {
        "scanned_pairs_without_link": scanned,
        "selected_top_by_formation_crossings": top,
        "all_scanned": {"formation_crossings_avg": round(avg([r[0] for r in rows]), 1),
                        "formation_return_corr_avg": round(avg([r[4] for r in rows]), 3)},
        "selected": {"formation_crossings_avg": round(avg([r[0] for r in best]), 1),
                     "formation_crossings_min": min(r[0] for r in best),
                     "test_share_inside_2sd_avg": round(avg([r[1] for r in best]), 3),
                     "test_max_abs_z_avg": round(avg([r[2] for r in best]), 2)},
        "genuine": {"formation_crossings_avg": round(avg([g[0] for g in gen]), 1),
                    "test_share_inside_2sd_avg": round(avg([g[1] for g in gen]), 3),
                    "test_max_abs_z_avg": round(avg([g[2] for g in gen]), 2)},
        "best_selected_z": [round(v, 4) for v in best[0][3]],
        "best_selected_stats": {"crossings": best[0][0], "test_inside": round(best[0][1], 3), "test_max_abs_z": round(best[0][2], 2)},
        "first_genuine_z": [round(v, 4) for v in gen[0][3]],
        "first_genuine_stats": {"crossings": gen[0][0], "test_inside": round(gen[0][1], 3), "test_max_abs_z": round(gen[0][2], 2)},
    }


def exercises():
    # ch6 ex1: capital 150,000 instead of 125,000
    cap, net, days = D(150000), D(2846), D(90)
    ex1 = {"net_pct_yr": r2(net / cap * 365 / days * 100), "opp": r2(cap * D("0.04") * days / 365),
           "excess": r2(net - cap * D("0.04") * days / 365)}
    # ch6 ex2: early close with basis 1,500 at day 30
    cap, fee, s30, f30 = D(125000), D("0.0005"), D(101000), D(102500)
    b30 = f30 - s30
    extra = b30 - fee * s30 + fee * (s30 + f30)
    opp = cap * D("0.04") * 60 / 365
    ex2 = {"extra": str(extra), "opp": r2(opp), "decision": "close" if opp > extra else "hold"}
    assert ex2["decision"] == "hold"
    return {"ch06_ex1_capital_150000": ex1, "ch06_ex2_basis_1500": ex2}


def main():
    res = {
        "scope": "Synthetic worked examples for chapters 6 and 7; no market data or backtest",
        "ch06_carry_ladder": carry_ladder(),
        "ch06_early_close_hurdle_4pct": early_close("0.04"),
        "ch06_early_close_hurdle_2pct": early_close("0.02"),
        "ch06_funding_scenarios": funding_scenarios(),
        "ch07_population": population(),
        "ch07_selection_bias": selection_bias(),
        "exercises": exercises(),
    }
    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
