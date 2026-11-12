#!/usr/bin/env python3
"""สร้าง docs/sab-figures.json — ตัวเลขทุกตัวที่หนังสือ "Stat Arb for Non Quant · เล่ม 1" ใช้

กฎเหล็กของแผน (docs/sab-book-plan.md หัวข้อ 10): ห้ามพิมพ์ตัวเลขลอย ๆ ลงในบท
ทุกตัวเลขต้องมาจากไฟล์นี้ และไฟล์นี้ต้องคำนวณซ้ำได้เหมือนเดิมทุกครั้ง (ไม่ต่อเน็ต ไม่ใช้ข้อมูลจริง)

    python3 -I tools/sab_figures.py                   # เขียนทับ docs/sab-figures.json
    python3 -I tools/sab_figures.py --check           # คำนวณใหม่แล้วเทียบกับไฟล์ ไม่เขียน (C1)
    python3 -I tools/sab_figures.py --check-original  # G1/C4: เทียบกับโค้ดต้นฉบับ v0.9 ตาม tools/sab_origmap.json

ที่มาของตรรกะ: พอร์ตจากสคริปต์ต้นฉบับ 8 ไฟล์ใน $SAB_SOURCE_DIR/code (ค่าเริ่มต้น sources/sab-v0_9)
แล้วต่อด้วยค่าใหม่ ⓝ ที่แผนสั่ง · build ไม่ import โค้ดต้นฉบับ (ต้นฉบับถูกโหลดเฉพาะตอน --check-original
เพื่อยืนยันว่าพอร์ตให้ค่าเดียวกันทุกตัว) · stdlib ล้วน
"""

import contextlib
import importlib.util
import io
import json
import math
import os
import random
import statistics
import sys
from decimal import ROUND_HALF_UP, Decimal as D, getcontext
from fractions import Fraction as Fr

getcontext().prec = 28

PREFIX = "sab"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", f"{PREFIX}-figures.json")
ORIGMAP = os.path.join(ROOT, "tools", f"{PREFIX}_origmap.json")
SOURCE_DIR = os.environ.get("SAB_SOURCE_DIR", os.path.join("sources", "sab-v0_9"))
if not os.path.isabs(SOURCE_DIR):
    SOURCE_DIR = os.path.join(ROOT, SOURCE_DIR)

ROBUST_SEEDS = list(range(1, 31))   # ชุด seed เดียวกับที่ audit ใช้ (audit/code_figures.md: seed 1–30)
SEED_FP = 20261111                  # seed ของต้นฉบับ (first passage) — ใช้ซ้ำกับการจำลองใหม่ของบท 13/17
SEED_POP, SEED_SEL = 7, 11          # seed ของต้นฉบับ บท 9 / บท 10


# ── ตัวช่วย ──────────────────────────────────────────────────────────────────
def q(x, n=2):
    """ปัดครึ่งขึ้น (แบบ r2 ของต้นฉบับ) แล้วคืนเป็นตัวเลข JSON · n = 0 คืน int"""
    d = x if isinstance(x, D) else D(str(x))
    if n <= 0:
        return int(d.quantize(D(1), rounding=ROUND_HALF_UP))
    return float(d.quantize(D(1).scaleb(-n), rounding=ROUND_HALF_UP))


def pct(x, n=1):
    """สัดส่วน (0–1) → เปอร์เซ็นต์ที่ปัดแล้ว"""
    return q(D(str(x)) * 100, n)


def s(x):
    return str(x)


# ════════════════════════════════════════════════════════════════════════════
#  ส่วน ก — พอร์ตตรรกะต้นฉบับ (สเกลต้นฉบับ · คีย์อังกฤษเหมือน *_results.json)
# ════════════════════════════════════════════════════════════════════════════

# ── v07_primer_checks.py ────────────────────────────────────────────────────
def o_v07():
    out = {}
    out["long_0.1_btc"] = D("0.1") * (D(102000) - D(100000))
    out["short_0.1_btc"] = D("-0.1") * (D(102000) - D(100000))
    notional, margin = D(10000), D(1000)
    out["leverage"] = notional / margin
    out["loss_5pct"] = notional * D("0.05")
    out["loss_5pct_share_of_margin"] = out["loss_5pct"] / margin
    out["loss_10pct"] = notional * D("0.10")
    bid, ask, fee = D(99990), D(100010), D("0.0005")
    out["spread"] = ask - bid
    out["mid"] = (ask + bid) / 2
    out["round_trip_price_cost"] = bid - ask
    out["round_trip_fees"] = fee * (ask + bid)
    out["round_trip_total"] = out["round_trip_price_cost"] - out["round_trip_fees"]
    out["round_trip_total_bps_of_mid"] = -out["round_trip_total"] / out["mid"] * 10000
    out["funding_short_1_btc"] = D(100000) * D("0.0001")
    out["self_check"] = {
        "q1": D("-0.5") * (D(98000) - D(100000)),
        "q2_notional": D(2000) * 5,
        "q2_loss": D(2000) * 5 * D("0.04"),
        "q2_share_of_margin": D(2000) * 5 * D("0.04") / D(2000),
        "q3": D(50005) - D(49995),
        "q4": D(2) * D(100000) * D("0.0001"),
        "q5": D(103000) - D(100000),
    }
    assert out["round_trip_total"] == -120 and out["round_trip_total_bps_of_mid"] == 12
    return out


# ── v06_enrichment_demo.py ──────────────────────────────────────────────────
def o_v06_tail():
    p_loss, gain, loss = D("0.01"), D(1), D(-120)
    ev = (1 - p_loss) * gain + p_loss * loss
    out = {"expected_pnl_per_period": ev, "no_loss_probability": {}}
    for n in (50, 100, 250):
        out["no_loss_probability"][str(n)] = round(0.99 ** n, 4)
    out["expected_pnl_50_periods"] = ev * 50
    out["pnl_if_no_loss_in_50_periods"] = gain * 50
    assert ev == D("-0.21")
    return out


def o_v06_margin(capital):
    """long spot 1 + short futures 1 · กติกาสอน: หลักประกัน = 10% ของราคา futures ปัจจุบัน ชำระสิ้นวัน"""
    m, s0, f0 = D("0.10"), D(100000), D(103000)
    rows, free, spot_q, margin = [], D(capital), D(0), D(0)

    def equity(px):
        return free + spot_q * px + margin

    rows.append(("start", free, D(0), margin, equity(s0)))
    free -= s0
    spot_q = D(1)
    rows.append(("buy_spot", free, spot_q * s0, margin, equity(s0)))
    im = m * f0
    free -= im
    margin += im
    rows.append(("short_future_post_margin", free, spot_q * s0, margin, equity(s0)))
    s1, f1 = D(110000), D(113200)
    vm = -(f1 - f0)
    margin += vm
    rows.append(("day1_settlement", free, spot_q * s1, margin, equity(s1)))
    required = m * f1
    top_up = required - margin
    shortfall = max(D(0), top_up - free)
    res = {"variation_margin_day1": vm, "required_margin_day1": required, "top_up_needed": top_up,
           "free_cash_before_top_up": free, "shortfall": shortfall,
           "max_one_day_future_rise_covered": (D(capital) - s0 - im) / (1 + m)}
    if shortfall == 0:
        free -= top_up
        margin += top_up
        rows.append(("day1_after_top_up", free, spot_q * s1, margin, equity(s1)))
        st = D(105000)
        margin += -(st - f1)
        rows.append(("expiry_settlement", free, spot_q * st, margin, equity(st)))
        res["equity_at_expiry"] = equity(st)
    res["rows"] = [{"event": e, "free_cash": a, "spot_value": b, "margin": c, "equity": d}
                   for e, a, b, c, d in rows]
    return res


def o_v06_funding():
    fee_rate = D("0.0002")
    spot_in, perp_in, spot_out, perp_out = D(100000), D(100050), D(99000), D(99020)
    marks = [D(100000), D(101000), D(99000)]
    rates = [D("0.0001"), D("0.0003"), D("-0.0002")]
    funding = [mk * r for mk, r in zip(marks, rates)]
    price = (spot_out - spot_in) + (perp_in - perp_out)
    fees = fee_rate * (spot_in + perp_in + spot_out + perp_out)
    net = price + sum(funding) - fees
    assert net == D("-29.114")
    return {"funding_cash_flows_to_short": funding, "funding_total": sum(funding), "price_pnl": price,
            "fees": fees, "net": net, "simple_annualised_of_0.01pct_per_8h": D("0.0001") * 3 * 365,
            "intervals_to_cover_fees_at_10_per_interval": fees / D(10)}


def o_v06_hedge():
    d_a, p_b = D(10000), D(50)
    beta_a, beta_b = D("1.5"), D("1.0")
    sig_m, sig_eb = D("0.02"), D("0.01")
    b = beta_a * beta_b * sig_m ** 2 / (beta_b ** 2 * sig_m ** 2 + sig_eb ** 2)
    methods = {"equal_units": D(100) * p_b, "dollar_neutral": d_a,
               "price_level_h_1.6": D("1.6") * D(100) * p_b,
               "return_regression_b_1.2": b * d_a, "beta_neutral": d_a * beta_a / beta_b}
    out = {"regression_slope_b": b, "rows": []}
    for name, x in methods.items():
        beta_exp = d_a * beta_a - x * beta_b
        sd = ((beta_exp * sig_m) ** 2 + (x * sig_eb) ** 2).sqrt()
        out["rows"].append({"method": name, "units_b_short": x / p_b, "value_b_short": x,
                            "net_dollar": d_a - x, "beta_exposure": beta_exp,
                            "pnl_market_minus_4pct": beta_exp * D("-0.04"),
                            "pnl_sd_excluding_a_specific": str(round(float(sd), 2)),
                            "_sd_exact": sd})
    return out


def o_v06_first_passage(seed=SEED_FP, paths=100_000, max_steps=5_000, cases=((0.8, 0.1), (0.8, 0.5), (0.99, 0.5))):
    """พอร์ต first_passage() ทุกการเรียก RNG ตรงต้นฉบับ + ค่าเสริมของเล่มใหม่ (ขึ้นต้น _)"""
    rng = random.Random(seed)
    out = []
    for phi, sig in cases:
        times, up_first = [], 0
        hl = math.log(0.5) / math.log(phi)
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
        out.append({
            "phi": phi, "innovation_sd": sig, "mean_half_life": round(hl, 2),
            "median_first_passage": times[n // 2], "mean_first_passage": round(sum(times) / n, 1),
            "p90_first_passage": times[int(0.9 * n)],
            "share_done_within_4": round(sum(t <= 4 for t in times) / n, 3),
            "share_touching_3_before_1": round(up_first / n, 3),
            "cdf_points": {str(k): round(sum(t <= k for t in times) / n, 4)
                           for k in (1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128)},
            # ⓝ errata 24: "ราว 85%" ของต้นฉบับ = สัดส่วนที่แตะ ≤ 1 ภายในครึ่งชีวิต (นับช่วงเต็ม ≤ ครึ่งชีวิต)
            "_share_done_within_half_life": sum(t <= hl for t in times) / n,
            "_share_touching_3_before_1_exact": up_first / n,
            "_stationary_sd": sig / math.sqrt(1 - phi * phi),
        })
    return out


def o_v06_exercises():
    m, f0, f1, s0, s1 = D("0.10"), D(103000), D(111000), D(100000), D(108100)
    margin = m * f0 - (f1 - f0)
    top_up = m * f1 - margin
    free_after = D(9700) - top_up
    equity_change = (s1 - s0) - (f1 - f0)

    def slope(sig_eb):
        return D("1.5") * D("0.0004") / (D("0.0004") + sig_eb ** 2)

    def sd(x, sig_eb):
        return float((((D(15000) - x) * D("0.02")) ** 2 + (x * sig_eb) ** 2).sqrt())

    sds = {k: round(sd(D(v), D("0.02")), 1) for k, v in (("b", "7500"), ("dollar", "10000"), ("beta", "15000"))}
    drift = 10 * 2 * (1 - 0.99 ** 12)
    return {"ch03_ex7": {"top_up": top_up, "free_cash_after": free_after, "equity_change": equity_change},
            "ch04_ex4": {"b_if_no_specific_risk": slope(D(0)), "b_if_specific_sd_2pct": slope(D("0.02")), "pnl_sd": sds},
            "s7a_ex4_expected_price_gain_12_periods": round(drift, 2)}


# ── v09_ch06_ch07_demo.py ───────────────────────────────────────────────────
def r2s(x):
    return D(x).quantize(D("0.01"), rounding=ROUND_HALF_UP)


def carry_ladder(fee=D("0.0005"), basis=D(3000), cap=D(125000), hurdle=D("0.04"),
                 s0=D(100000), days=D(90), st=D(105000)):
    """บันได carry (ตรรกะ carry_ladder ของต้นฉบับ ขยายให้เปลี่ยนค่าธรรมเนียม/basis/ทุน/hurdle ได้)"""
    f0 = s0 + basis
    fees = fee * (s0 + f0 + st)
    net = basis - fees
    opp = cap * hurdle * days / 365
    return {"basis": basis, "simple_rate_on_spot_pct": basis / s0 * 365 / days * 100,
            "price_return_on_capital_pct_yr": basis / cap * 365 / days * 100,
            "fees": fees, "net": net, "net_on_capital_pct_yr": net / cap * 365 / days * 100,
            "opportunity_cost": opp, "excess": net - opp,
            "excess_pct_yr": (net - opp) / cap * 365 / days * 100}


def o_v09_carry():
    c = carry_ladder()
    return {"simple_rate_on_spot_pct": r2s(c["simple_rate_on_spot_pct"]),
            "continuous_rate_on_spot_pct": r2s(D(math.log(103000 / 100000) * 365 / 90 * 100)),
            "price_return_on_capital_pct_yr": r2s(c["price_return_on_capital_pct_yr"]),
            "fees": c["fees"], "net": c["net"], "net_on_capital_pct_yr": r2s(c["net_on_capital_pct_yr"]),
            "opportunity_cost": r2s(c["opportunity_cost"]), "excess": r2s(c["excess"]),
            "excess_pct_yr": r2s(c["excess_pct_yr"])}


def early_close(hurdle, s30=D(101000), f30=D(101500), cap=D(125000), fee=D("0.0005"), b0=D(3000)):
    b30 = f30 - s30
    close_fees = fee * (s30 + f30)
    hold_fee = fee * s30
    hold_extra = b30 - hold_fee + close_fees
    opp60 = cap * D(hurdle) * 60 / 365
    return {"hurdle": hurdle, "basis_day30": b30, "pnl_to_date": b0 - b30, "close_fees_now": close_fees,
            "spot_fee_if_held": hold_fee, "extra_from_holding": hold_extra,
            "extra_pct_yr_on_capital": hold_extra / cap * 365 / 60 * 100,
            "opportunity_60d": opp60, "decision": "close" if opp60 > hold_extra else "hold"}


FUNDING_PATHS = {
    "A_flat": [D("0.0001")] * 90,
    "B_decay": [D("0.0003")] * 30 + [D("0.00005")] * 60,
    "C_flip": [D("0.0001")] * 45 + [D("-0.0001")] * 45,
    "D_whipsaw": ([D("0.0001")] * 5 + [D("-0.00005")] * 3) * 11 + [D("0.0001")] * 2,
}


def funding_path(rates, fee_total=D(80), mark=D(100000), cap=D(125000)):
    cum, c = [], D(0)
    for r in rates:
        c += mark * r
        cum.append(c)
    neg, rc, held = 0, D(0), True
    for r in rates:
        if held:
            rc += mark * r
            neg = neg + 1 if r < 0 else 0
            if neg >= 3:
                held = False
    return {"funding_total": c, "net": c - fee_total, "net_pct_yr": (c - fee_total) / cap * 365 / 30 * 100,
            "cumulative": cum,
            "rule_exit_after_3_negative": {"funding": rc, "net": rc - fee_total, "exited": not held}}


# ── บท 7 ต้นฉบับ: คู่จำลอง (ทุกการเรียก RNG ตรงต้นฉบับ) ────────────────────────
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


def ar_fit(series):
    x, y = series[:-1], series[1:]
    mx, my = sum(x) / len(x), sum(y) / len(y)
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / sum((a - mx) ** 2 for a in x)


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
    return z, cross, sum(1 for v in test if abs(v) <= 2) / len(test), max(abs(v) for v in test), m, sd


def o_v09_population(seed=SEED_POP, pairs=200, series=True):
    rng = random.Random(seed)
    n, nf = 500, 250
    out, examples = {}, {}
    for name, maker in (("H_high_corr_no_link", pair_h), ("C_linked", pair_c)):
        rows = []
        for _ in range(pairs):
            a, b = maker(rng, n)
            sp = [x - y for x, y in zip(a, b)]
            z, cross, inband, maxz, _, _ = zstats(sp, nf)
            ra, rb = diff(a), diff(b)
            # ค่าเสริม ⓝ (ไม่แตะ RNG): ทิศเดียวกัน · กรอบรั่ว (ค่ากลาง/ระยะแกว่งจากทั้ง 500 วัน) · เกณฑ์ ≥ 85%
            m2 = sum(sp) / n
            sd2 = math.sqrt(sum((x - m2) ** 2 for x in sp) / (n - 1))
            leak = sum(1 for x in sp[nf:] if abs((x - m2) / sd2) <= 2) / (n - nf)
            rows.append({"corr": corr(ra, rb), "phi_formation": ar_fit(sp[:nf]), "inband": inband, "maxz": maxz,
                         "same": sum(1 for u, v in zip(ra, rb) if (u > 0) == (v > 0)) / len(ra), "leak": leak,
                         "a": a, "b": b, "s": sp})
        avg = lambda k: sum(r[k] for r in rows) / len(rows)
        phis = sorted(r["phi_formation"] for r in rows)
        out[name] = {
            "pairs": pairs,
            "return_corr_avg": round(avg("corr"), 3),
            "formation_ar1_phi_avg": round(avg("phi_formation"), 3),
            "test_share_inside_2sd_avg": round(avg("inband"), 3),
            "share_of_pairs_with_test_abs_z_above_3": round(sum(1 for r in rows if r["maxz"] > 3) / pairs, 3),
            "_corr_avg": avg("corr"), "_inband_avg": avg("inband"), "_phi_avg": avg("phi_formation"),
            "_phi_median": statistics.median(phis),
            "_half_life_median": statistics.median(math.log(0.5) / math.log(p) for p in phis if 0 < p < 1),
            "_same_direction_avg": avg("same"), "_leak_band_inband_avg": avg("leak"),
            "_share_pass_85": sum(1 for r in rows if r["inband"] >= 0.85) / pairs,
            "_maxz_avg": avg("maxz"),
        }
        target = avg("inband")
        ex = min(rows, key=lambda r: abs(r["inband"] - target))
        examples[name] = {"return_corr": round(ex["corr"], 3), "test_inside": round(ex["inband"], 3)}
        if series:
            examples[name]["spread"] = [round(v, 5) for v in ex["s"]]
    out["typical_examples"] = examples
    return out


def o_v09_selection(seed=SEED_SEL, scanned=200, top=10, genuine=10, series=True):
    rng = random.Random(seed)
    n, nf = 500, 250
    rows = []
    for _ in range(scanned):
        a, b = pair_h(rng, n)
        sp = [x - y for x, y in zip(a, b)]
        z, cross, inband, maxz, m, sd = zstats(sp, nf)
        rows.append((cross, inband, maxz, z, corr(diff(a[:nf]), diff(b[:nf])), a, b, sp, m, sd))
    rows.sort(key=lambda r: -r[0])
    best = rows[:top]
    gen = []
    for _ in range(genuine):
        a, b = pair_c(rng, n)
        sp = [x - y for x, y in zip(a, b)]
        z, cross, inband, maxz, _, _ = zstats(sp, nf)
        gen.append((cross, inband, maxz, z))
    avg = lambda xs: sum(xs) / len(xs)
    b0 = best[0]
    test_z = b0[3][nf:]
    imin = min(range(len(test_z)), key=lambda i: test_z[i])
    out = {
        "all_scanned": {"formation_crossings_avg": round(avg([r[0] for r in rows]), 1),
                        "formation_return_corr_avg": round(avg([r[4] for r in rows]), 3)},
        "selected": {"formation_crossings_avg": round(avg([r[0] for r in best]), 1),
                     "formation_crossings_min": min(r[0] for r in best),
                     "test_share_inside_2sd_avg": round(avg([r[1] for r in best]), 3),
                     "test_max_abs_z_avg": round(avg([r[2] for r in best]), 2)},
        "genuine": {"formation_crossings_avg": round(avg([g[0] for g in gen]), 1),
                    "test_share_inside_2sd_avg": round(avg([g[1] for g in gen]), 3),
                    "test_max_abs_z_avg": round(avg([g[2] for g in gen]), 2)},
        "best_selected_stats": {"crossings": b0[0], "test_inside": round(b0[1], 3), "test_max_abs_z": round(b0[2], 2)},
        "first_genuine_stats": {"crossings": gen[0][0], "test_inside": round(gen[0][1], 3),
                                "test_max_abs_z": round(gen[0][2], 2)},
        # ค่าเสริม ⓝ
        "_all_inband_avg": avg([r[1] for r in rows]), "_all_maxz_avg": avg([r[2] for r in rows]),
        "_sel_inband_avg": avg([r[1] for r in best]), "_sel_maxz_avg": avg([r[2] for r in best]),
        "_gen_inband_avg": avg([g[1] for g in gen]), "_gen_maxz_avg": avg([g[2] for g in gen]),
        "_best_min_z": test_z[imin], "_best_min_day": imin + 1, "_best_sd": b0[9],
        "_best_pair": {"a": b0[5], "b": b0[6], "z": b0[3]},
        "_selected_worse_than_genuine": avg([r[1] for r in best]) < avg([g[1] for g in gen]),
    }
    if series:
        out["best_selected_z"] = [round(v, 4) for v in b0[3]]
        out["first_genuine_z"] = [round(v, 4) for v in gen[0][3]]
    return out


def o_v09_exercises():
    cap, net, days = D(150000), D(2846), D(90)
    ex1 = {"net_pct_yr": r2s(net / cap * 365 / days * 100), "opp": r2s(cap * D("0.04") * days / 365),
           "excess": r2s(net - cap * D("0.04") * days / 365)}
    e2 = early_close("0.04", f30=D(102500))
    ex2 = {"extra": e2["extra_from_holding"], "opp": r2s(e2["opportunity_60d"]), "decision": e2["decision"]}
    return {"ch06_ex1_capital_150000": ex1, "ch06_ex2_basis_1500": ex2}


# ── mean_reversion_demo.py ──────────────────────────────────────────────────
def o_mean_reversion():
    start, units, cost, horizon = D(2), D(10), D(1), 4
    rows = []
    for phi in (D("0.8"), D("0.99"), D(1), D("1.02")):
        end = start * phi ** horizon
        gross = units * (start - end)
        hl = -math.log(2) / math.log(float(phi)) if D(0) < phi < D(1) else None
        rows.append({"phi": phi, "expected_next_level": start * phi,
                     "expected_level_after_4_periods": end, "mean_half_life_periods": hl,
                     "expected_gross_pnl": gross, "expected_net_pnl": gross - cost,
                     "_levels": [start * phi ** h for h in range(horizon + 1)]})
    marks = [D(10)] * 3
    means = [D(0), D(8), D(10)]
    return {"ar_cases": rows,
            "negative_phi_example": [start * D("-0.5") ** h for h in range(5)],
            "moving_mean": {"spread_marks": marks, "estimated_means": means,
                            "computed_residuals": [a - b for a, b in zip(marks, means)],
                            "actual_price_pnl_fixed_holdings": -units * (marks[-1] - marks[0])}}


# ── signal_design_demo.py ───────────────────────────────────────────────────
def o_signal_design():
    s0, f0, d0 = D(100000), D(103000), 90
    r0 = math.log(float(f0 / s0)) * 365.0 / d0
    fa = float(s0) * math.exp(r0 * 60 / 365)
    pa = float(f0 - s0) - (fa - float(s0))
    sb, fb = D(120000), D(123100)
    rb = math.log(float(fb / sb)) * 365.0 / 80
    pb = (sb - s0) + (f0 - fb)
    a0, b0, a1, b1, hedge = D(105), D(50), D(54), D(25), D(2)
    return {
        "entry": {"spot": s0, "future": f0, "days": d0, "continuous_rate": r0,
                  "simple_annualized_rate": float((f0 / s0 - 1) * D(365) / D(d0)), "basis": f0 - s0},
        "alternative_cases": [
            {"case": "A", "spot": float(s0), "future": fa, "days": 60, "rate": r0, "basis": fa - float(s0), "price_pnl": pa},
            {"case": "B", "spot": sb, "future": fb, "days": 80, "rate": rb, "basis": fb - sb, "price_pnl": pb,
             "_spot_leg": sb - s0, "_future_leg": f0 - fb},
            {"case": "aligned_expiry", "spot": 180000, "future": 180000, "days": 0, "rate": None, "basis": 0,
             "price_pnl": 3000}],
        "ratio_and_basket": {"A": [a0, a1], "B": [b0, b1], "ratio": [a0 / b0, a1 / b1],
                             "fixed_basket": [a0 - hedge * b0, a1 - hedge * b1], "holdings": [1, -2],
                             "price_pnl": (a1 - a0) - hedge * (b1 - b0)},
        "normalization_only": {"spread": [5, 5], "mean": [0, 0], "scale": [1, 2.5],
                               "z": [D(5) / D(1), D(5) / D("2.5")], "price_pnl": 0},
    }


# ── methods_signals_stops_demo.py (เครื่องสถานะการ์ดกติกา) ──────────────────
class ExitPolicy:
    """พอร์ต SyntheticExitPolicy: ตะกร้าคงจำนวน 10 ชุด · เข้า 2 · ออก 0.5 · งบ 15 · ครบ 3 ช่วง · ต้นทุน 0.4 + 0.6
    ลำดับ ขาดทุน → สัญญาณ → เวลา · ออกเพราะงบ → หยุดเปิดไม้ใหม่ (FLAT_PAUSED)"""

    def __init__(self, side=-1):
        self.side, self.units = side, D(10)
        self.entry_level, self.exit_level = D(2), D("0.5")
        self.loss_limit, self.max_bars = D(15), 3
        self.entry_cost, self.exit_cost = D("0.4"), D("0.6")
        self.position, self.paused = None, False
        self.observations, self.trades, self.resume_attempts = [], [], []

    @property
    def state(self):
        if self.position is not None:
            return ("OPEN_SHORT" if self.side == -1 else "OPEN_LONG") + ("_ENTRIES_PAUSED" if self.paused else "")
        return "FLAT_PAUSED" if self.paused else "FLAT"

    def resume(self, explicit_request, checks_passed):
        if not explicit_request:
            reason = "explicit_request_required"
        elif self.position is not None:
            reason = "position_must_be_flat"
        elif not checks_passed:
            reason = "checks_not_passed"
        elif not self.paused:
            reason = "not_paused"
        else:
            self.paused, reason = False, "resumed_flat_after_checks"
        out = {"accepted": reason == "resumed_flat_after_checks", "reason": reason, "state_after": self.state}
        self.resume_attempts.append(out)
        return out

    def observe(self, bar, x):
        x = D(str(x))
        rec = {"bar": bar, "x": x, "state_before": self.state}
        if self.position is not None:
            p = self.position
            elapsed = bar - p["entry_bar"]
            gross = D(self.side) * self.units * (x - p["entry_x"])
            liq = gross - self.entry_cost - self.exit_cost
            rec.update({"elapsed_bars": elapsed, "gross_price_pnl": gross, "net_liquidation_pnl_if_exit_now": liq})
            recovered = x <= self.exit_level if self.side == -1 else x >= -self.exit_level
            reason = ("loss_limit" if liq <= -self.loss_limit else "signal_recovery" if recovered
                      else "time_limit" if elapsed >= self.max_bars else None)
            if reason:
                self.trades.append({"entry_bar": p["entry_bar"], "entry_x": p["entry_x"], "exit_bar": bar,
                                    "exit_x": x, "elapsed_bars": elapsed, "exit_reason": reason,
                                    "gross_price_pnl": gross, "net_pnl": liq,
                                    "_time_limit_also": elapsed >= self.max_bars})
                self.position = None
                if reason == "loss_limit":
                    self.paused = True
                rec.update({"event": "exit", "reason": reason})
            else:
                rec["event"] = "hold"
        elif self.paused:
            rec["event"] = "entry_blocked_by_pause"
        elif (x >= self.entry_level if self.side == -1 else x <= -self.entry_level):
            self.position = {"entry_bar": bar, "entry_x": x}
            rec["event"] = "entry"
        else:
            rec["event"] = "flat"
        rec["state_after"] = self.state
        self.observations.append(rec)
        return rec


def run_path(values, side=-1):
    pol = ExitPolicy(side)
    for bar, x in enumerate(values):
        pol.observe(bar, x)
    return pol


STOP_PATHS = {"convergence": ["0", "2.1", "1.7", "0.4"], "time": ["0", "2.1", "2.0", "1.9", "1.8"],
              "gap": ["0", "2.1", "2.8", "4.1"]}
# ⓝ เส้นทาง 4 (errata 37): งบและเวลาครบพร้อมกันที่ช่วงที่ 3 → −17 · ค่ากลางทางเลือกโดยสคริปต์นี้ (แผนกำหนดแค่ปลายทาง −17)
PATH4 = ["0", "2.1", "2.6", "3.0", "3.7"]


def o_methods():
    pols = {k: run_path(v) for k, v in STOP_PATHS.items()}
    stop_x = D("2.1") + (D(15) - D(1)) / D(10)
    paused = run_path(STOP_PATHS["gap"])
    for bar, x in ((4, "3.8"), (5, "2.4")):
        paused.observe(bar, x)
    paused.resume(False, True)
    paused.resume(True, False)
    paused.resume(True, True)
    mirror = run_path(["0", "-2.1", "-1.7", "-0.4"], side=1)
    return {
        "forecast": {
            "fixed_quantity_forecast": {"forecast_gross_pnl": D(6), "forecast_roundtrip_cost": D(3),
                                        "forecast_net_before_risk_buffer": D(3), "decision_risk_buffer": D(1),
                                        "decision_margin": D(2)},
            "separate_win_probability_example": {
                "probability_win": D("0.65"), "gross_pnl_if_win": D(1), "gross_pnl_if_loss": D(-3),
                "cost_in_each_outcome": D("0.1"),
                "expected_gross_pnl": D("0.65") * 1 - D("0.35") * 3,
                "expected_net_pnl": D("0.65") * 1 - D("0.35") * 3 - D("0.1")}},
        "stops": {
            "rules": {"short_entry_z_at_least": D(2), "short_exit_z_at_most": D("0.5"), "basket_units": D(10),
                      "entry_fee": D("0.4"), "exit_fee": D("0.6"), "loss_limit_on_net_liquidation_pnl": D(15),
                      "max_bars_after_entry": 3},
            "short_loss_threshold_in_x_for_this_entry": stop_x,
            "loss_overshoot_in_gap_case": -pols["gap"].trades[0]["net_pnl"] - D(15),
            "paths": {k: {"observations": p.observations, "trades": p.trades, "final_state": p.state}
                      for k, p in pols.items()},
            "long_symmetry_check": {"trades": mirror.trades},
            "persistent_pause_demo": {"observations": paused.observations, "resume_attempts": paused.resume_attempts,
                                      "final_state": paused.state,
                                      "blocked_entry_observations": sum(1 for o in paused.observations
                                                                        if o["event"] == "entry_blocked_by_pause"),
                                      "closed_trade_count": len(paused.trades)},
            "_path4": run_path(PATH4),
        },
    }


# ── ch03_ledger_demo.py ─────────────────────────────────────────────────────
def o_ch03():
    p0 = {"A": D(100), "B": D(50)}
    p1 = {"A": D(102), "B": D("50.5")}
    q = {"A": D(10), "B": D(-20)}
    leg = {k: q[k] * (p1[k] - p0[k]) for k in q}
    gross = sum(leg.values())
    cash0 = D(1000) - sum(q[k] * p0[k] for k in q)          # = 1,000 (ขา short ได้เงินเข้า)
    eq = lambda cash, marks: cash + sum(q[k] * marks[k] for k in q)
    rebalance_cash = cash0 - D(2) * D(50)
    slipped_cash = D(1000) - (D(10) * D("100.1") + D(-20) * D("49.95"))
    drag = D(10) * (D("100.1") - p0["A"]) + D(20) * (p0["B"] - D("49.95"))
    partial_q = {"A": D(10), "B": D(-8)}
    partial_pnl = sum(partial_q[k] * (p1[k] - p0[k]) for k in partial_q)
    return {
        "fixed_hedge": {"leg_pnl": leg, "spread_before": p0["A"] - 2 * p0["B"], "spread_after": p1["A"] - 2 * p1["B"],
                        "gross_pnl": gross, "closing_cash": cash0 + q["A"] * -1 * -p1["A"] * 0 + D(1000) + gross - D(1000),
                        "gross_exposure_before_costs": D(2000), "gross_exposure_to_equity_before_costs": D(2)},
        "cost_ledger": [{"equity": D(1000)}, {"equity": D(996)}, {"equity": eq(cash0 - 7, p1)},
                        {"equity": D(1000) + gross - 12}],
        "net_pnl": gross - D(4 + 3 + 5),
        "net_return_on_initial_equity": (gross - D(12)) / D(1000),
        "parameter_only": {"h_before": D(2), "h_after": D("1.8"), "spread_before": p0["A"] - 2 * p0["B"],
                           "spread_after": p0["A"] - D("1.8") * p0["B"], "actual_equity": eq(cash0, p0),
                           "price_pnl": D(0)},
        "rebalance": {"after_before_fee": {"cash": rebalance_cash, "holdings_value": D(10) * 100 - D(18) * 50,
                                           "equity": rebalance_cash + D(10) * 100 - D(18) * 50},
                      "after_fee": {"equity": rebalance_cash + D(10) * 100 - D(18) * 50 - 1}},
        "execution_slippage": {"entry_snapshot": {"equity": slipped_cash + sum(q[k] * p0[k] for k in q)},
                               "entry_drag_already_in_cash": drag,
                               "later_equity": slipped_cash + sum(q[k] * p1[k] for k in q)},
        "partial_fill": {"actual_price_pnl": partial_pnl, "fully_filled_target_price_pnl": gross,
                         "_net_long_value": partial_q["A"] * p0["A"] + partial_q["B"] * p0["B"]},
    }


# ── part1_reasoning_demo.py (ส่วน bridge เท่านั้น — factor model ชุด beta 1.2/0.8 ตัดตาม errata 31) ──
def o_part1():
    qty = [D(10), D(-20)]
    mid, fexit, rexit, fills = [D(100), D(50)], [D(102), D("50.4")], [D(102), D("50.6")], [D("100.2"), D("49.95")]
    pnl = lambda a, b: sum(qq * (y - x) for qq, x, y in zip(qty, a, b))
    fg, rg, ag = pnl(mid, fexit), pnl(mid, rexit), pnl(fills, rexit)
    fees, carry = D(2), D(1)
    return {"bridge": {"forecast_gross": fg, "realized_ideal_mid_gross": rg, "actual_fill_gross": ag,
                       "fill_price_difference": ag - rg, "fees": fees, "holding_carry_cost": carry,
                       "actual_net": ag - fees - carry, "forecast_comparison_gap": rg - fg}}


def originals_port():
    """โครงเดียวกับผลต้นฉบับ (ต่อแฟ้ม) — ใช้เติม _ต้นฉบับ และให้ G1 เทียบได้ตรงตัว"""
    v06_hedge = o_v06_hedge()
    return {
        "v07_primer_checks": o_v07(),
        "v06_enrichment_demo": {
            "ch01_tail_risk": o_v06_tail(),
            "ch03_margin_capital_125000": o_v06_margin("125000"),
            "ch03_margin_capital_120000": o_v06_margin("120000"),
            "ch03_funding": o_v06_funding(),
            "ch04_hedge_comparison": v06_hedge,
            "s7a_first_passage_seeded_monte_carlo": o_v06_first_passage(),
            "exercise_checks": o_v06_exercises(),
        },
        "v09_ch06_ch07_demo": {
            "ch06_carry_ladder": o_v09_carry(),
            "ch06_early_close_hurdle_4pct": early_close("0.04"),
            "ch06_early_close_hurdle_2pct": early_close("0.02"),
            "ch06_funding_scenarios": {k: funding_path(v) for k, v in FUNDING_PATHS.items()},
            "ch07_population": o_v09_population(),
            "ch07_selection_bias": o_v09_selection(),
            "exercises": o_v09_exercises(),
        },
        "mean_reversion_demo": o_mean_reversion(),
        "signal_design_demo": o_signal_design(),
        "methods_signals_stops_demo": o_methods(),
        "ch03_ledger_demo": o_ch03(),
        "part1_reasoning_demo": o_part1(),
    }


# ════════════════════════════════════════════════════════════════════════════
#  ส่วน ข — ค่าใหม่ ⓝ ที่แผนสั่ง
# ════════════════════════════════════════════════════════════════════════════
BOOK = [(D("0.0005"), D(2000)), (D("0.0010"), D(3000)), (D("0.0020"), D(5000)),
        (D("0.0040"), D(10000)), (D("0.0080"), D(20000))]
MIX_MAIN = (D("0.60"), D("0.25"), D("0.15"))
MIX_ALT = (D("0.45"), D("0.20"), D("0.35"))
OUTCOMES = (D(16), D(2), D(-21))
CARD_GROSS_NOTIONAL = D(2021)   # 10 × 102.1 + 20 × 50 ที่จุดเข้า X = 2.1 (A = 100 + X · B = 50)


def book_slip(size):
    """ราคาเฉลี่ยที่เสียเทียบ mid เมื่อกินกระดานสมมติด้วยขนาด size (ต่อขา) · None = กระดานไม่พอ"""
    rem, cost = size, D(0)
    for p, qty in BOOK:
        take = min(rem, qty)
        cost += take * p
        rem -= take
        if rem <= 0:
            return cost / size
    return None


def capacity(mix, sizes=(500, 1000, 2000, 3000, 5000, 7500, 10000, 20000), fee=D("0.0005")):
    """capacity ด้วยค่าคาดหมายต่อรอบ (tools/sab_research/design/plan_check/capacity_ev.py)"""
    ev = sum(p * o for p, o in zip(mix, OUTCOMES))
    edge = (ev + 1) / CARD_GROSS_NOTIONAL          # คืนต้นทุน 1 ของการ์ด → กำไรจากราคาก่อนต้นทุนต่อมูลค่าสองขา
    rows = []
    for size in sizes:
        sl = book_slip(D(size))
        net = edge - 2 * fee - 2 * sl
        rows.append({"ขนาดต่อขา": size, "ส่วนต่างราคาเฉลี่ยเปอร์เซ็นต์": q(sl * 100), "edgeสุทธิเปอร์เซ็นต์": q(net * 100),
                     "ต่อรอบ": q(net * 2 * size)})
    return {"ค่าคาดหมายหลังต้นทุนการ์ด": q(ev), "edgeก่อนต้นทุนเปอร์เซ็นต์": q(edge * 100), "ตาราง": rows}


def drawdown(seed, trades=100):
    rng = random.Random(seed)
    seq = []
    for _ in range(trades):
        u = rng.random()
        seq.append(16 if u < 0.60 else 2 if u < 0.85 else -21)
    cum, peak, peak_i, deepest, longest, cur_len = 0, 0, 0, 0, 0, 0
    curve = []
    for i, x in enumerate(seq, 1):
        cum += x
        curve.append(cum)
        if cum >= peak:
            peak, cur_len = cum, 0
        else:
            cur_len += 1
            deepest = max(deepest, peak - cum)
            longest = max(longest, cur_len)
    return {"ลึกสุด": -deepest, "นานสุดไม้": longest, "ผลรวม100ไม้": cum,
            "ไม้ชนะ": sum(1 for x in seq if x > 0), "ไม้เสีย": sum(1 for x in seq if x < 0), "_curve": curve}


def three_worlds(seed=SEED_FP, trials=100_000, start=2.0, sd=0.5, phis=(0.80, 0.99, 1.00)):
    """กฎเดียวสามโลก ⓝ: การ์ดบท 12 (short ตะกร้า 10 ชุดที่ X = start · งบ −15 · ออก 0.5 · ครบ 3 ช่วง · ต้นทุน 1)"""
    rng = random.Random(seed)
    out = {}
    for phi in phis:
        reasons = {"งบ": 0, "เป้า": 0, "เวลา": 0}
        nets, wins = [], 0
        for _ in range(trials):
            x = start
            for t in range(1, 4):
                x = phi * x + rng.gauss(0.0, sd)
                liq = 10 * (start - x) - 1
                if liq <= -15:
                    r = "งบ"
                elif x <= 0.5:
                    r = "เป้า"
                elif t >= 3:
                    r = "เวลา"
                else:
                    continue
                reasons[r] += 1
                nets.append(liq)
                wins += liq > 0
                break
        out[f"{phi:.2f}"] = {"ออกเพราะเป้าเปอร์เซ็นต์": pct(reasons["เป้า"] / trials),
                             "ออกเพราะงบเปอร์เซ็นต์": pct(reasons["งบ"] / trials),
                             "ออกเพราะเวลาเปอร์เซ็นต์": pct(reasons["เวลา"] / trials),
                             "ไม้กำไรเปอร์เซ็นต์": pct(wins / trials),
                             "ค่าคาดหมายต่อไม้ก่อนค่าถือ": q(sum(nets) / trials),
                             "ค่าคาดหมายต่อไม้หลังค่าถือ": None}
    return out


def random_walk_table(seed=SEED_FP, steps=10, start=2):
    rng = random.Random(seed)
    moves = [1 if rng.random() < 0.5 else -1 for _ in range(steps)]
    walk, x = [start], start
    for m in moves:
        x += m
        walk.append(x)
    ar = [q(D(start) * D("0.8") ** t, 2) for t in range(steps + 1)]
    return {"ก้าว": moves, "เดินสุ่ม": walk, "เหลือ80เปอร์เซ็นต์": ar,
            "ค่าเฉลี่ยของก้าวที่คาด": 0, "ค่าเฉลี่ยของก้าวในตัวอย่าง": q(D(sum(moves)) / steps, 1)}


def fake_money(sel, leg=1000):
    """เทรดคู่อันดับ 1 ของบท 10 บนกระดาษด้วยการ์ดบท 12 ขาละ 1,000 (จำนวนคงที่ · ราคา = e^log) · ก่อนค่าถือ"""
    a, b, z = sel["_best_pair"]["a"], sel["_best_pair"]["b"], sel["_best_pair"]["z"]
    nf, n = 250, len(z)
    PA = [100 * math.exp(v) for v in a]
    PB = [100 * math.exp(v) for v in b]
    trades, pos, paused = [], None, False
    for i in range(nf, n):
        if pos is not None:
            el = i - pos["i"]
            gross = pos["qa"] * (PA[i] - PA[pos["i"]]) + pos["qb"] * (PB[i] - PB[pos["i"]])
            liq = gross - 1
            rec = z[i] <= 0.5 if pos["side"] < 0 else z[i] >= -0.5
            r = "งบ" if liq <= -15 else "เป้า" if rec else "เวลา" if el >= 3 else None
            if r:
                trades.append({"วันเข้า": pos["i"] - nf + 1, "zเข้า": q(z[pos["i"]]), "วันออก": i - nf + 1,
                               "zออก": q(z[i]), "เหตุออก": r, "สุทธิ": q(liq)})
                pos = None
                paused = paused or r == "งบ"
        elif not paused and abs(z[i]) >= 2:
            side = -1 if z[i] > 0 else 1        # z > 0 → short ส่วนต่าง (short A · long B)
            pos = {"i": i, "side": side, "qa": side * leg / PA[i], "qb": -side * leg / PB[i]}
    open_pnl = None
    if pos is not None:
        open_pnl = q(pos["qa"] * (PA[-1] - PA[pos["i"]]) + pos["qb"] * (PB[-1] - PB[pos["i"]]) - 1)
    nets = [t["สุทธิ"] for t in trades]
    return {"ไม้": trades, "รวมสุทธิ": q(sum(nets)) if nets else 0, "ไม้แย่สุด": min(nets) if nets else None,
            "ถือค้างตอนจบ": open_pnl, "หยุดเปิดเพราะงบ": paused}


# ════════════════════════════════════════════════════════════════════════════
#  ส่วน ค — ประกอบ JSON (ตัวเลขที่ปัดแล้วตามที่บทพิมพ์)
# ════════════════════════════════════════════════════════════════════════════
def build_min():
    thb, rate = 50000, 35
    total_usd = D(thb) / D(rate)
    return {
        "หน่วย": "ดอลลาร์ (stablecoin สกุลดอลลาร์)", "บาทต่อดอลลาร์": rate, "เงินบาท": thb,
        "เงินบนexchange": 1250, "เงินบนexchangeบาท": 1250 * rate, "เงินนอกexchangeบาท": thb - 1250 * rate,
        "สเกล": 0.01, "ค่าธรรมเนียม": {"taker": 0.05, "maker": 0.02, "มินในnq": 0.1}, "hurdle": 4,
        "กฎ1%": {"ทุนรวมดอลลาร์": q(total_usd), "เพดานต่อไม้": q(total_usd / 100), "เพดานต่อไม้บาท": thb // 100,
                 "งบ15เป็นเปอร์เซ็นต์ของทุนรวม": q(D(15) / total_usd * 100),
                 "เสีย21เป็นเปอร์เซ็นต์ของทุนรวม": q(D(21) / total_usd * 100), "เพดานรวมหยุดทบทวนเปอร์เซ็นต์": -20},
        "beta": {"A": 1.5, "B": 1.0, "A_stress": 1.7},
        "BTC": {"spot": 100000, "bid": 99990, "ask": 100010, "futures": 103000, "วันถึงหมดอายุ": 90,
                "basis": 3000, "ราคาชำระ": 105000},
        "ทุนภาค1": {"รวม": 125000, "spot": 100000, "หลักประกัน": 10300, "เงินสดอิสระ": 14700},
        "กติกาหลักประกันเปอร์เซ็นต์": 10,
        "ต้นทุนหนึ่งรอบต่อขา": {"เปอร์เซ็นต์": 0.12, "ส่วนต่างราคา": 20, "ค่าธรรมเนียม": 100},
        "funding": {"ต่อรอบเปอร์เซ็นต์": 0.01, "ชั่วโมงต่อรอบในตัวอย่าง": 8},
        "คู่": {"A": 100, "B": 50, "h": 2, "ทุนคู่": 1000, "ชุด": 10, "จำนวนA": 10, "จำนวนB": -20},
        "ไม้บรรทัด": {"ค่ากลาง": 0, "ระยะแกว่งปกติ": 1},
        "การ์ด": {"เข้า": 2, "ออก": 0.5, "ช่วงถือสูงสุด": 3, "งบขาดทุนสุทธิ": -15, "ต้นทุนเข้า": 0.4,
                  "ต้นทุนออก": 0.6, "ลำดับ": ["ขาดทุน", "สัญญาณ", "เวลา"]},
        "ค่าถือคู่": {"ต่อรอบเปอร์เซ็นต์": 0.01, "มูลค่าขา": 1000, "ต่อรอบ": 0.1, "รอบต่อช่วง": None,
                      "หมายเหตุ": "รอบต่อช่วงตรึงในเฟส 0 (แผน 3.5) — ยังไม่มีค่า · ตาราง 'หลังค่าถือ' ทุกตารางเป็น null จนกว่าจะตรึง"},
        "seed": {"บท9": SEED_POP, "บท10": SEED_SEL, "บท13": SEED_FP, "seed_robustness": "1–30",
                 "drawdown": f"{SEED_FP} (ชั่วคราว — แผนให้ตรึงในเฟส 0)"},
    }


def build_assumptions():
    return {
        "กติกาหลักประกัน": 10,
        "กระดานสมมติ": [[0.05, 2000], [0.10, 3000], [0.20, 5000], [0.40, 10000], [0.80, 20000]],
        "สัดส่วนตอนจบ": {"หลัก": [0.60, 0.25, 0.15], "เทียบ": [0.45, 0.20, 0.35], "ผล": [16, 2, -21]},
        "มูลค่าสองขาของการ์ด": 2021,
        "สมมติฐานที่สคริปต์นี้ตั้ง (ต้องยืนยันในเฟส 0)": {
            "ch04.dist": "ราคา spot ขึ้น x% และ basis 3,200 แบบคืนวันที่ 9 (ทำให้แถว 10% = 11,220 ตรงตัวอย่างหลัก)",
            "แบบฝึก.ch05": "ราคาชำระ = ราคา futures ตอนเปิด 61,200 (โจทย์ในแผนไม่ระบุ)",
            "ch12.เส้นทาง4": "X = 0 → 2.1 → 2.6 → 3.0 → 3.7 (แผนระบุแค่ปลายทาง −17)",
            "ch13.กฎเดียวสามโลก": "เริ่มไม้ที่ X = 2 · แรงสะบัด (sd ของการสุ่มต่อช่วง) 0.5 ทั้งสามโลก · 100,000 ไม้ · seed 20261111",
            "ch13.เดินสุ่ม": "ก้าว ±1 สิบช่วงจาก seed 20261111 เริ่มที่ 2",
            "ch15.เงินก็หลอกได้": "ราคา = 100 × e^(log ของต้นฉบับ) · จำนวนคงที่ขาละ 1,000 ณ จุดเข้า · ช่วง = วัน · ต้นทุนการ์ด 1 · ก่อนค่าถือ",
            "ch17.drawdown": "ตัวอย่าง seed 20261111 · การกระจาย seed 1–30 · 100 ไม้",
        },
    }


def build(orig):
    v06, v09 = orig["v06_enrichment_demo"], orig["v09_ch06_ch07_demo"]
    v07, sd_, mr = orig["v07_primer_checks"], orig["signal_design_demo"], orig["mean_reversion_demo"]
    mss, l3, p1 = orig["methods_signals_stops_demo"], orig["ch03_ledger_demo"], orig["part1_reasoning_demo"]
    m125, m120 = v06["ch03_margin_capital_125000"], v06["ch03_margin_capital_120000"]
    pop, sel = v09["ch07_population"], v09["ch07_selection_bias"]
    H, C = pop["H_high_corr_no_link"], pop["C_linked"]
    fp = v06["s7a_first_passage_seeded_monte_carlo"]
    stops = mss["stops"]
    trade = lambda k: stops["paths"][k]["trades"][0]
    p4 = stops["_path4"].trades[0]

    # ── บท 0 ──
    ch00 = {
        "basis": 3000, "basisเปอร์เซ็นต์": q(D(3000) / D(100000) * 100, 1),
        "ปลายทาง": [{"ราคาวันหมดอายุ": t, "ขาspot": t - 100000, "ขาshortfutures": 103000 - t,
                     "รวม": (t - 100000) + (103000 - t)} for t in (60000, 100000, 150000)],
        "long01BTCราคาขึ้น2000": q(v07["long_0.1_btc"], 0), "short01BTCราคาขึ้น2000": q(v07["short_0.1_btc"], 0),
        "funding_short1BTCต่อรอบ": q(v07["funding_short_1_btc"], 0),
    }

    # ── บท 1 ──
    rt01 = {"ค่าธรรมเนียม": -q(D("0.001") * D(200000), 0)}
    rt01["รวม"] = -20 + rt01["ค่าธรรมเนียม"]
    rt01.update({"เปอร์เซ็นต์": q(D(-rt01["รวม"]) / D(1000), 2), "สองขา": 2 * rt01["รวม"],
                 "3000ลบสองขา": 3000 + 2 * rt01["รวม"]})
    ch01 = {
        "ต้นทุนไปกลับ": {"bid": 99990, "ask": 100010, "mid": q(v07["mid"], 0), "ส่วนต่าง": q(v07["spread"], 0),
                          "ส่วนต่างราคา": q(v07["round_trip_price_cost"], 0),
                          "ค่าธรรมเนียม": -q(v07["round_trip_fees"], 0), "รวม": q(v07["round_trip_total"], 0),
                          "เปอร์เซ็นต์": q(v07["round_trip_total_bps_of_mid"] / 100, 2),
                          "สองขา": q(2 * v07["round_trip_total"], 0),
                          "3000ลบสองขา": q(3000 + 2 * v07["round_trip_total"], 0)},
        "ต้นทุนไปกลับที่0.1": rt01,
        "leverage": {"หลักประกัน": 1000, "ถือ": 10000, "เท่า": q(v07["leverage"], 0),
                     "สวน5เปอร์เซ็นต์": -q(v07["loss_5pct"], 0),
                     "สวน5เปอร์เซ็นต์ส่วนของหลักประกัน": pct(v07["loss_5pct_share_of_margin"], 0),
                     "สวน10เปอร์เซ็นต์": -q(v07["loss_10pct"], 0)},
        "ได้ขาเดียว": {"วางซื้อ": 99.9, "วางขาย": 100.1, "ได้สองฝั่ง": q(D("100.1") - D("99.9"), 1),
                       "ราคาลง": 99.5, "ได้ขาเดียว": q(D("99.5") - D("99.9"), 1)},
        "ปมกำไรอยู่ที่หนึ่ง": {"ราคาขึ้น": 10000, "ขาspot": 10000, "ขาfutures": -10000, "รวม": 0,
                               "หลักประกันเหลือ": 10300 - 10000},
    }

    # ── บท 2 ──
    tail = v06["ch01_tail_risk"]
    ch02 = {
        "หางหนึ่งเปอร์เซ็นต์": {"โอกาสชนะ": 99, "ได้": 1, "เสีย": -120,
                                 "ค่าคาดหมายต่อรอบ": q(tail["expected_pnl_per_period"]),
                                 "ค่าคาดหมาย50รอบ": q(tail["expected_pnl_50_periods"]),
                                 "ถ้าไม่เห็นวันเสีย50รอบ": q(tail["pnl_if_no_loss_in_50_periods"], 0)},
        "ไม่เห็นวันเสีย": {str(n): pct(D("0.99") ** n) for n in (10, 20, 50, 100, 250)},
        "ช่วงในภาพหาง": 50,
        "เหรียญ": {"ได้": 4, "เสีย": -2, "ค่าคาดหมาย": q(D("0.5") * 4 + D("0.5") * -2, 0)},
        "โจทย์funding": {"funding": 5, "ราคา": -7, "ไม่hedge": -2, "hedgeครบ": 5},
    }

    # ── บท 3 ──
    rows = m125["rows"]
    case_b = sd_["alternative_cases"][1]
    case_a = sd_["alternative_cases"][0]
    ch03 = {
        "เปิดไม้": {"ทุน": q(rows[0]["free_cash"], 0), "ซื้อspot": 100000, "เงินสดหลังซื้อspot": q(rows[1]["free_cash"], 0),
                    "หลักประกัน": q(rows[2]["margin"], 0), "เงินสดอิสระ": q(rows[2]["free_cash"], 0),
                    "equity": q(rows[2]["equity"], 0)},
        "simpleบนจอ": q(carry_ladder()["simple_rate_on_spot_pct"]),
        "กรณี1_simple": {"วันที่เหลือ": 60, "spot": 100000, "futures": q(D(100000) * (1 + D(3000) / D(100000) * 60 / 90), 0),
                         "กำไรจากราคา": q(D(3000) - D(3000) * 60 / 90, 0)},
        "กรณี2": {"spot": q(case_b["spot"], 0), "futures": q(case_b["future"], 0), "basis": q(case_b["basis"], 0),
                  "ขาspot": q(case_b["_spot_leg"], 0), "ขาfutures": q(case_b["_future_leg"], 0),
                  "รวม": q(case_b["price_pnl"], 0)},
        "ลงลึก": {"continuousเปอร์เซ็นต์": q(D(str(sd_["entry"]["continuous_rate"])) * 100),
                  "futuresแบบexp": q(case_a["future"]), "กำไรจากราคาแบบexp": q(case_a["price_pnl"])},
    }

    # ── บท 4 ──
    free125 = D(14700)
    after_day1 = free125 - m125["top_up_needed"]
    dist = []
    for x in (5, 10, 15):
        s1 = D(100000) * (1 + D(x) / 100)
        f1 = s1 + 3200
        top = D("1.1") * (f1 - 103000)
        dist.append({"spotขึ้นเปอร์เซ็นต์": x, "futures": q(f1, 0), "ต้องโอน": q(top, 0),
                     "ขาดที่ทุน125000": q(max(D(0), top - free125), 0),
                     "ขาดที่ทุน120000": q(max(D(0), top - D(9700)), 0)})
    ch04 = {
        "คืนวันที่9": {"spot": 110000, "futures": 113200},
        "ต้องโอน": q(m125["top_up_needed"], 0), "variation_margin": q(m125["variation_margin_day1"], 0),
        "หลักประกันที่ต้องมี": q(m125["required_margin_day1"], 0),
        "หลักประกันหลังชำระ": q(m125["rows"][3]["margin"], 0),
        "equity_เปลี่ยน": q(m125["rows"][3]["equity"] - 125000, 0), "equity": q(m125["rows"][3]["equity"], 0),
        "เงินสดอิสระหลังโอน": q(after_day1, 0), "equityวันหมดอายุ": q(m125["equity_at_expiry"], 0),
        "กันชน": {"125000": pct(m125["max_one_day_future_rise_covered"] / 103000),
                  "120000": pct(m120["max_one_day_future_rise_covered"] / 103000),
                  "150000": pct(o_v06_margin("150000")["max_one_day_future_rise_covered"] / 103000)},
        "กันชนเงิน": {"125000": q(m125["max_one_day_future_rise_covered"]),
                      "120000": q(m120["max_one_day_future_rise_covered"])},
        "ต้นทุน": 120000, "ต้นเงินสดอิสระ": q(m120["free_cash_before_top_up"], 0), "ต้นขาด": q(m120["shortfall"], 0),
        "ต้นequity": q(m120["rows"][3]["equity"], 0),
        "หลังวันแรกรับได้อีก": pct(after_day1 / D("1.1") / 113200),
        "dist": dist,
    }

    # ── บท 5 ──
    def ladder_row(c):
        return {"basis": q(c["basis"], 0), "บนจอ": q(c["simple_rate_on_spot_pct"]),
                "ต่อทุน": q(c["price_return_on_capital_pct_yr"]), "ค่าธรรมเนียม": q(c["fees"]),
                "สุทธิ": q(c["net"]), "หลังค่าธรรมเนียม": q(c["net_on_capital_pct_yr"]),
                "ค่าเสียโอกาส": q(c["opportunity_cost"]), "ส่วนเกิน": q(c["excess"]),
                "ส่วนเกินเปอร์เซ็นต์": q(c["excess_pct_yr"])}

    main = carry_ladder()
    ch05 = {
        "บันได": ladder_row(main),
        "บันไดที่0.1": ladder_row(carry_ladder(fee=D("0.001"))),
        "continuousเปอร์เซ็นต์": q(v09["ch06_carry_ladder"]["continuous_rate_on_spot_pct"]),
        "hurdle9": ladder_row(carry_ladder(hurdle=D("0.09"))),
        "ทุนกับกันชน": [{"ทุน": c, "ส่วนเกินเปอร์เซ็นต์": q(carry_ladder(cap=D(c))["excess_pct_yr"]),
                         "หลังค่าธรรมเนียม": q(carry_ladder(cap=D(c))["net_on_capital_pct_yr"]),
                         "กันชน": pct(o_v06_margin(str(c))["max_one_day_future_rise_covered"] / 103000)}
                        for c in (120000, 125000, 150000)],
        "บันไดแย่ง": [{"basis": b, "บนจอ": q(carry_ladder(basis=D(b))["simple_rate_on_spot_pct"]),
                       "หลังค่าธรรมเนียม": q(carry_ladder(basis=D(b))["net_on_capital_pct_yr"]),
                       "ส่วนเกินเปอร์เซ็นต์": q(carry_ladder(basis=D(b))["excess_pct_yr"])}
                      for b in (3000, 2500, 2000, 1500, 1000, 500)],
        "สุทธิ2846เทียบ2760": {"ถือจนชำระ": q(main["net"], 0), "ปิดเองสองขาtaker": 2760},
    }

    # ── บท 6 ──
    e4, e2h = v09["ch06_early_close_hurdle_4pct"], v09["ch06_early_close_hurdle_2pct"]
    entry_fees = D("0.0005") * (100000 + 103000)
    realized30 = D(3000) - 500 - entry_fees - e4["close_fees_now"]
    released = D(125000) + realized30
    opp_released = released * D("0.04") * 60 / 365
    net_carry = main["net"]
    ch06 = {
        "วันที่30": {"spot": 101000, "futures": 101500, "basis": q(e4["basis_day30"], 0),
                     "กำไรถึงวันนี้": q(e4["pnl_to_date"], 0), "ค่าธรรมเนียมปิดตอนนี้": q(e4["close_fees_now"]),
                     "ค่าธรรมเนียมspotถ้าถือ": q(e4["spot_fee_if_held"], 1),
                     "ถือได้เพิ่ม": q(e4["extra_from_holding"]),
                     "ถือได้เพิ่มเปอร์เซ็นต์ต่อปี": q(e4["extra_pct_yr_on_capital"]),
                     "เสียโอกาส60วัน": q(e4["opportunity_60d"]),
                     "เสียโอกาสบนเงินที่ปลดได้": q(opp_released), "เงินที่ปลดได้": q(released),
                     "ปิดดีกว่า": [q(e4["opportunity_60d"] - e4["extra_from_holding"]),
                                   q(opp_released - e4["extra_from_holding"])],
                     "ตัดสินที่hurdle4": "ปิด" if e4["decision"] == "close" else "ถือ",
                     "เสียโอกาสที่hurdle2": q(e2h["opportunity_60d"]),
                     "ตัดสินที่hurdle2": "ปิด" if e2h["decision"] == "close" else "ถือ",
                     "จุดเปลี่ยนhurdle": q(e4["extra_from_holding"] / (D(125000) * 60 / 365) * 100)},
        "มินปิด": {"ต่อ1BTC": q(realized30), "ของมิน": q(realized30 / 100)},
        "ถือถึงวันหมดอายุ": {"ราคาชำระ": 105000, "ขายspotได้": 104900,
                              "กำไรจากราคา": (104900 - 100000) + (103000 - 105000)},
        "รอบชดเชย": {"กำไรต่อรอบ": q(net_carry, 0), "เสียทั้ง125000": q(D(125000) / net_carry, 0),
                     "เสียทั้ง125000_ทศนิยม": q(D(125000) / net_carry),
                     "ปี": q(D(125000) / net_carry * 90 / 365, 1),
                     "เสียเฉพาะ25000": q(D(25000) / net_carry, 1),
                     "ปี25000": q(D(25000) / net_carry * 90 / 365, 1)},
        "dist": [{"basisวันที่30": b,
                  "ถือได้เพิ่ม": q(early_close("0.04", f30=D(101000 + b))["extra_from_holding"]),
                  "เสียโอกาส60วัน": q(early_close("0.04", f30=D(101000 + b))["opportunity_60d"]),
                  "ตัดสิน": "ปิด" if early_close("0.04", f30=D(101000 + b))["decision"] == "close" else "ถือ"}
                 for b in (500, 1500, 2500)],
    }

    # ── บท 7 ──
    fl = v06["ch03_funding"]
    fs = v09["ch06_funding_scenarios"]
    names = {"A_flat": "ราบ", "B_decay": "พุ่งแล้วแผ่ว", "C_flip": "กลับขั้ว", "D_whipsaw": "สลับ"}
    taker = {k: funding_path(v, fee_total=D(200)) for k, v in FUNDING_PATHS.items()}
    opp30 = D(125000) * D("0.04") * 30 / 365
    flat = fs["A_flat"]
    part1_total = realized30 + fl["net"] + fs["C_flip"]["rule_exit_after_3_negative"]["net"] \
        + fs["D_whipsaw"]["rule_exit_after_3_negative"]["net"]

    def crowd(rate, fee):
        tot = D(rate) * 100000 * 90
        return q((tot - fee) / 125000 * 365 / 30 * 100)

    ch07 = {
        "สามรอบ": {"funding": [q(x) for x in fl["funding_cash_flows_to_short"]], "fundingรวม": q(fl["funding_total"], 1),
                   "กำไรจากราคา": q(fl["price_pnl"], 0), "ค่าธรรมเนียม": q(fl["fees"], 3), "สุทธิ": q(fl["net"], 3),
                   "รอบที่พอค่าธรรมเนียม": q(fl["intervals_to_cover_fees_at_10_per_interval"], 2),
                   "รอบที่พอค่าธรรมเนียมปัด": q(fl["intervals_to_cover_fees_at_10_per_interval"], 0)},
        "บันไดfunding": {"บนจอ": pct(fl["simple_annualised_of_0.01pct_per_8h"], 2),
                         "ต่อทุน": q(flat["funding_total"] / 125000 * 365 / 30 * 100),
                         "หลังค่าธรรมเนียม": q(flat["net_pct_yr"]),
                         "ส่วนเกินเปอร์เซ็นต์": q((flat["net"] - opp30) / 125000 * 365 / 30 * 100)},
        "สี่เส้นทาง": {names[k]: {"fundingรวม": q(fs[k]["funding_total"], 0), "สุทธิmaker": q(fs[k]["net"], 0),
                                  "สุทธิmakerเปอร์เซ็นต์": q(fs[k]["net_pct_yr"]),
                                  "กฎmaker": q(fs[k]["rule_exit_after_3_negative"]["net"], 0),
                                  "ออกตามกฎ": fs[k]["rule_exit_after_3_negative"]["exited"],
                                  "สุทธิtaker": q(taker[k]["net"], 0), "สุทธิtakerเปอร์เซ็นต์": q(taker[k]["net_pct_yr"]),
                                  "กฎtaker": q(taker[k]["rule_exit_after_3_negative"]["net"], 0)}
                       for k in FUNDING_PATHS},
        "ค่าธรรมเนียมเปิดปิด": {"maker": 80, "taker": 200},
        "fundingถูกแย่ง": [{"ต่อรอบเปอร์เซ็นต์": r, "สุทธิtakerเปอร์เซ็นต์": crowd(D(str(r)) / 100, 200),
                            "สุทธิmakerเปอร์เซ็นต์": crowd(D(str(r)) / 100, 80)} for r in (0.01, 0.005, 0.003)],
        "บัญชีสะสมภาค1": {"ต่อ1BTC": q(part1_total), "ของมิน": q(part1_total / 100),
                          "รายการ": {"ปิดcarry": q(realized30), "perpสามรอบ": q(fl["net"], 3),
                                     "เดือนกลับขั้ว": q(fs["C_flip"]["rule_exit_after_3_negative"]["net"], 0),
                                     "เดือนสลับ": q(fs["D_whipsaw"]["rule_exit_after_3_negative"]["net"], 0)}},
        "กราฟ": {names[k]: [q(x, 2) for x in fs[k]["cumulative"]] for k in FUNDING_PATHS},
    }

    # ── บท 8 ──
    hc = v06["ch04_hedge_comparison"]
    rows_h = {r["method"]: r for r in hc["rows"]}
    k10 = D("0.1")
    three = [("จำนวนเท่ากัน", "equal_units"), ("มูลค่าเท่ากัน", "dollar_neutral"), ("betaneutral", "beta_neutral")]
    ch08 = {
        "ขาเดียว": {"A": 1000, "BTCลงเปอร์เซ็นต์": -4, "Aลงเปอร์เซ็นต์": -6, "ขาA": -60, "ขาshortBTC": 40, "รวม": -20},
        "สามวิธี": {th: {"จำนวนB": q(rows_h[en]["units_b_short"] * k10, 0), "มูลค่าB": q(rows_h[en]["value_b_short"] * k10, 0),
                          "betaexposure": q(rows_h[en]["beta_exposure"] * k10, 0),
                          "BTCลง4": q(rows_h[en]["pnl_market_minus_4pct"] * k10, 0)} for th, en in three},
        "stress_B1": {"ขา500": -5, "ขา1000": -10, "ขา1500": -15},
        "beta_stress": {"A": 1000, "hedgeBTC": 1500, "betaเดิม": 1.5, "betaใหม่": 1.7,
                        "exposure": q(D(1000) * D("1.7") - 1500, 0), "BTCลง5": q((D(1000) * D("1.7") - 1500) * D("-0.05"), 0)},
        "hedgeด้วยperp": {"มูลค่า": 1500, "fundingต่อรอบเปอร์เซ็นต์": 0.01, "ต่อรอบ": q(D(1500) * D("0.0001"), 2)},
        "ปัดlot": {"ต้องการBTC": q(D(1500) / D(100000), 3),
                   "ปัดลง": {"BTC": 0.01, "exposure": q(D(1500) - D("0.01") * 100000, 0)},
                   "ปัดขึ้น": {"BTC": 0.02, "exposure": q(D(1500) - D("0.02") * 100000, 0)}},
        "ลงลึก": {"regression_b": q(hc["regression_slope_b"], 1), "h_ราคา": 1.6,
                  "sd": {th: q(rows_h[en]["_sd_exact"] * k10) for th, en in
                         [("จำนวนเท่ากัน", "equal_units"), ("มูลค่าเท่ากัน", "dollar_neutral"), ("h16", "price_level_h_1.6"),
                          ("b12", "return_regression_b_1.2"), ("betaneutral", "beta_neutral")]},
                  "มูลค่าB": {"h16": q(rows_h["price_level_h_1.6"]["value_b_short"] * k10, 0),
                              "b12": q(rows_h["return_regression_b_1.2"]["value_b_short"] * k10, 0)}},
    }
    ch08["stress_B1"] = {f"ขา{v}": q(-D(v) * D("0.01"), 0) for v in (500, 1000, 1500)}

    # ── บท 9 ──
    def same_dir(r):
        return pct(D(0.5) + D(math.asin(r) / math.pi), 1)

    ex = pop["typical_examples"]
    ch09 = {
        "จำลอง": {"คู่ต่อแบบ": 200, "วัน": 500, "ช่วงเลือก": 250, "seed": SEED_POP},
        "ไม่มีเชือก": {"corr": q(H["return_corr_avg"], 2), "corr3": q(H["return_corr_avg"], 3),
                       "ในกรอบ": pct(H["test_share_inside_2sd_avg"]),
                       "คู่ที่เกิน3": pct(H["share_of_pairs_with_test_abs_z_above_3"], 0),
                       "ทิศเดียวกัน": pct(H["_same_direction_avg"]), "phi": q(H["formation_ar1_phi_avg"], 3)},
        "มีเชือก": {"corr": q(C["return_corr_avg"], 2), "corr3": q(C["return_corr_avg"], 3),
                    "ในกรอบ": pct(C["test_share_inside_2sd_avg"]),
                    "คู่ที่เกิน3": pct(C["share_of_pairs_with_test_abs_z_above_3"], 0),
                    "ทิศเดียวกัน": pct(C["_same_direction_avg"]), "phi": q(C["formation_ar1_phi_avg"], 3)},
        "คู่ตัวอย่าง": {"ไม่มีเชือก": {"corr": q(ex["H_high_corr_no_link"]["return_corr"], 2),
                                       "ในกรอบ": pct(ex["H_high_corr_no_link"]["test_inside"])},
                        "มีเชือก": {"corr": q(ex["C_linked"]["return_corr"], 2),
                                    "ในกรอบ": pct(ex["C_linked"]["test_inside"])}},
        "ตารางแปลงcorrelation": [{"corr": r, "ทิศเดียวกันเปอร์เซ็นต์": same_dir(r)}
                                 for r in (0, 0.2, 0.4, 0.5, 0.6, 0.72, 0.8, 0.9, 0.95, 0.99)],
        "ลงลึก": {"phi": q(H["formation_ar1_phi_avg"], 3),
                  "ครึ่งชีวิตจากค่าเฉลี่ยphi": q(math.log(0.5) / math.log(H["formation_ar1_phi_avg"]), 1),
                  "ครึ่งชีวิตจากมัธยฐานphi": q(math.log(0.5) / math.log(H["_phi_median"]), 1),
                  "มัธยฐานครึ่งชีวิตรายคู่": q(H["_half_life_median"], 1)},
        "กราฟ": {"ไม่มีเชือก": ex["H_high_corr_no_link"]["spread"], "มีเชือก": ex["C_linked"]["spread"]},
    }

    # ── บท 10 ──
    tries = {str(n): pct(1 - D("0.95") ** n) for n in (1, 10, 20, 50, 100)}
    ch10 = {
        "ค้น": {"คู่ที่ค้น": 200, "คัด": 10, "คู่จริง": 10, "seed": SEED_SEL},
        "ทั้ง200คู่": {"ข้ามค่ากลาง": q(sel["all_scanned"]["formation_crossings_avg"], 1),
                       "corr": q(sel["all_scanned"]["formation_return_corr_avg"], 3),
                       "ในกรอบ": pct(sel["_all_inband_avg"]), "ระยะสูงสุดเฉลี่ย": q(sel["_all_maxz_avg"])},
        "10อันดับแรก": {"ข้ามค่ากลาง": q(sel["selected"]["formation_crossings_avg"], 1),
                        "ข้ามน้อยสุด": sel["selected"]["formation_crossings_min"],
                        "ในกรอบ": pct(sel["selected"]["test_share_inside_2sd_avg"]),
                        "ระยะสูงสุดเฉลี่ย": q(sel["selected"]["test_max_abs_z_avg"])},
        "คู่จริง": {"ข้ามค่ากลาง": q(sel["genuine"]["formation_crossings_avg"], 1),
                    "ในกรอบ": pct(sel["genuine"]["test_share_inside_2sd_avg"]),
                    "ระยะสูงสุดเฉลี่ย": q(sel["genuine"]["test_max_abs_z_avg"])},
        "อันดับ1": {"ข้ามค่ากลาง": sel["best_selected_stats"]["crossings"],
                    "ในกรอบ": pct(sel["best_selected_stats"]["test_inside"]),
                    "ระยะสูงสุด": q(sel["best_selected_stats"]["test_max_abs_z"]),
                    "zต่ำสุด": q(sel["_best_min_z"]), "วันทดสอบที่ต่ำสุด": sel["_best_min_day"],
                    "ระยะlog": q(sel["_best_min_z"] * sel["_best_sd"], 4),
                    "ห่างจากค่ากลางเปอร์เซ็นต์": q((math.exp(sel["_best_min_z"] * sel["_best_sd"]) - 1) * 100, 1)},
        "คู่จริงตัวแรก": {"ข้ามค่ากลาง": sel["first_genuine_stats"]["crossings"],
                          "ในกรอบ": pct(sel["first_genuine_stats"]["test_inside"]),
                          "ระยะสูงสุด": q(sel["first_genuine_stats"]["test_max_abs_z"])},
        "กรอบรั่ว": {"ไม่มีเชือก": pct(H["_leak_band_inband_avg"]), "มีเชือก": pct(C["_leak_band_inband_avg"]),
                     "ไม่มีเชือกไม่รั่ว": pct(H["test_share_inside_2sd_avg"]), "มีเชือกไม่รั่ว": pct(C["test_share_inside_2sd_avg"])},
        "เกณฑ์ในกรอบ85": {"ปล่อยคู่ปลอม": pct(H["_share_pass_85"]), "ตัดคู่จริง": pct(1 - C["_share_pass_85"], 0)},
        "ลองหลายครั้ง": tries,
        "กราฟ": {"อันดับ1": sel["best_selected_z"], "คู่จริง": sel["first_genuine_z"]},
    }

    # ── บท 11 ──
    ch11 = {
        "เปิด": {"ทุน": 1000, "A": {"จำนวน": 10, "ราคา": 100}, "B": {"จำนวน": -20, "ราคา": 50}, "ชุด": 10},
        "ราคาใหม่": {"A": 102, "B": 50.5},
        "ขา": {"A": q(l3["fixed_hedge"]["leg_pnl"]["A"], 0), "B": q(l3["fixed_hedge"]["leg_pnl"]["B"], 0)},
        "กำไรจากราคา": q(l3["fixed_hedge"]["gross_pnl"], 0),
        "Xก่อนหลัง": [q(l3["fixed_hedge"]["spread_before"], 0), q(l3["fixed_hedge"]["spread_after"], 0)],
        "ต้นทุน": {"เข้า": 4, "ระหว่างถือ": 3, "ออก": 5, "รวม": 12},
        "equityระหว่างทาง": [q(r["equity"], 0) for r in l3["cost_ledger"]],
        "สุทธิ": q(l3["net_pnl"], 0), "สุทธิต่อทุนเปอร์เซ็นต์": pct(l3["net_return_on_initial_equity"]),
        "gross": q(l3["fixed_hedge"]["gross_exposure_before_costs"], 0),
        "grossต่อทุน": q(l3["fixed_hedge"]["gross_exposure_to_equity_before_costs"], 0),
        "สุทธิต่อgrossเปอร์เซ็นต์": q(l3["net_pnl"] / l3["fixed_hedge"]["gross_exposure_before_costs"] * 100, 1),
        "คุ้มทุนต่อชุด": q(D(12) / D(10), 1),
        "hเปลี่ยน": {"hเดิม": q(l3["parameter_only"]["h_before"], 0), "hใหม่": q(l3["parameter_only"]["h_after"], 1),
                     "Xเดิม": q(l3["parameter_only"]["spread_before"], 0), "Xใหม่": q(l3["parameter_only"]["spread_after"], 0),
                     "กำไร": q(l3["parameter_only"]["price_pnl"], 0), "equity": q(l3["parameter_only"]["actual_equity"], 0)},
        "sdเปลี่ยน": {"X": 5, "sd": [1, 2.5], "z": [q(z, 0) for z in sd_["normalization_only"]["z"]]},
        "ปรับhedge": {"Bจาก": -20, "Bเป็น": -18, "เงินสด": [1000, q(l3["rebalance"]["after_before_fee"]["cash"], 0)],
                      "มูลค่าถือ": q(l3["rebalance"]["after_before_fee"]["holdings_value"], 0),
                      "equity": q(l3["rebalance"]["after_before_fee"]["equity"], 0),
                      "หลังค่าธรรมเนียม1": q(l3["rebalance"]["after_fee"]["equity"], 0)},
        "สัดส่วนกับตะกร้า": {"A": [q(v, 0) for v in sd_["ratio_and_basket"]["A"]],
                              "B": [q(v, 0) for v in sd_["ratio_and_basket"]["B"]],
                              "สัดส่วน": [q(v, 2) for v in sd_["ratio_and_basket"]["ratio"]],
                              "ตะกร้า": [q(v, 0) for v in sd_["ratio_and_basket"]["fixed_basket"]],
                              "กำไร": q(sd_["ratio_and_basket"]["price_pnl"], 0)},
    }

    # ── บท 12 ──
    total_usd = D(50000) / D(35)
    ev_main = sum(p * o for p, o in zip(MIX_MAIN, OUTCOMES))
    ev_alt = sum(p * o for p, o in zip(MIX_ALT, OUTCOMES))
    path_out = lambda t, xs: {"X": [q(D(x), 1) for x in xs], "เหตุออก": {"loss_limit": "งบ", "signal_recovery": "เป้า",
                                                                       "time_limit": "เวลา"}[t["exit_reason"]],
                              "ช่วงที่ถือ": t["elapsed_bars"], "กำไรจากราคา": q(t["gross_price_pnl"], 0),
                              "สุทธิ": q(t["net_pnl"], 0), "ค่าถือ": None, "สุทธิหลังค่าถือ": None}
    ch12 = {
        "จุดเข้า": 2.1,
        "เส้นทาง": {"1": path_out(trade("convergence"), STOP_PATHS["convergence"]),
                    "2": path_out(trade("time"), STOP_PATHS["time"]),
                    "3": path_out(trade("gap"), STOP_PATHS["gap"]),
                    "4": {**path_out(p4, PATH4), "เวลาครบพร้อมกัน": p4["_time_limit_also"]}},
        "เส้นขาดทุนถึงงบ": q(stops["short_loss_threshold_in_x_for_this_entry"], 1),
        "เกินงบ": q(stops["loss_overshoot_in_gap_case"], 0),
        "สมมาตรlong": q(stops["long_symmetry_check"]["trades"][0]["net_pnl"], 0),
        "ต้องชนะเปอร์เซ็นต์": q(D(21) / D(37) * 100, 0), "ต้องชนะทศนิยม": q(D(21) / D(37) * 100),
        "สัดส่วนตอนจบ": {"หลัก": {"สัดส่วน": [60, 25, 15], "ค่าคาดหมาย": q(ev_main)},
                          "เทียบ": {"สัดส่วน": [45, 20, 35], "ค่าคาดหมาย": q(ev_alt)}},
        "กฎ1": {"ทุนรวมดอลลาร์": q(total_usd), "เพดานต่อไม้": q(total_usd / 100),
                "งบ15เปอร์เซ็นต์": q(D(15) / total_usd * 100), "เสีย21เปอร์เซ็นต์": q(D(21) / total_usd * 100)},
        "มูลค่าสองขา": 2021,
        "บัญชีคู่หลังไม้2": q(trade("convergence")["net_pnl"] + trade("time")["net_pnl"], 0),
        "ไม้3บนกระดาษที่28": q(-10 * (D("2.8") - D("2.1")) - 1, 0),
    }

    # ── บท 13 ──
    ar = {f"{float(r['phi']):.2f}": r for r in mr["ar_cases"]}
    fp3 = fp[2]
    hl_table = [{"ครึ่งชีวิต": h, "phi": q(D(0.5 ** (1 / h)), 3)} for h in (1, 2, 3, 4, 5, 7, 10, 14, 20, 30, 50, 69, 100)]
    ch13 = {
        "ตารางphi": {k: {"ระดับ": [q(v, 4) for v in r["_levels"]], "สุทธิ4ช่วง": q(r["expected_net_pnl"]),
                          "กำไรก่อนต้นทุน": q(r["expected_gross_pnl"], 4),
                          "ครึ่งชีวิต": q(r["mean_half_life_periods"]) if r["mean_half_life_periods"] else None,
                          "ครึ่งชีวิตปัด": q(r["mean_half_life_periods"], 0) if r["mean_half_life_periods"] else None}
                     for k, r in ar.items()},
        "กติกาตารางphi": {"เริ่ม": 2, "ช่วงถือ": 4, "ชุด": 10, "ต้นทุน": 1},
        "ครึ่งชีวิตเป็นphi": hl_table,
        "phiเป็นครึ่งชีวิต": [{"phi": p, "ครึ่งชีวิต": q(math.log(0.5) / math.log(p), 1)}
                             for p in (0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.976, 0.98, 0.99)],
        "phiลบ": [q(v, 3) for v in mr["negative_phi_example"]],
        "เดินสุ่ม": random_walk_table(),
        "กฎเดียวสามโลก": three_worlds(),
        "แตะเป้า": [{"phi": r["phi"], "แรงสะบัด": r["innovation_sd"], "ครึ่งชีวิต": r["mean_half_life"],
                     "ระยะzของจุดเข้า": q(2 / r["_stationary_sd"], 2 if r["_stationary_sd"] > 1 else 1),
                     "มัธยฐานช่วง": r["median_first_passage"], "เฉลี่ยช่วง": r["mean_first_passage"],
                     "p90ช่วง": r["p90_first_passage"], "จบใน4ช่วงเปอร์เซ็นต์": pct(r["share_done_within_4"]),
                     "แตะก่อนครึ่งชีวิตเปอร์เซ็นต์": pct(r["_share_done_within_half_life"]),
                     "ขึ้นถึง3ก่อนเปอร์เซ็นต์": pct(r["share_touching_3_before_1"])} for r in fp],
        "แตะเป้าแบบปัด": {"มัธยฐาน": fp3["median_first_passage"],
                          "แตะก่อนครึ่งชีวิตปัด": pct(fp3["_share_done_within_half_life"], 0),
                          "ขึ้นถึง3ก่อน": pct(fp3["share_touching_3_before_1"])},
        "กราฟcdf": [{"phi": r["phi"], "แรงสะบัด": r["innovation_sd"], "cdf": r["cdf_points"]} for r in fp],
        "ราคาที่คาด12ช่วง": v06["exercise_checks"]["s7a_ex4_expected_price_gain_12_periods"],
    }

    # ── บท 14 ──
    pp = stops["persistent_pause_demo"]
    ch14 = {
        "เส้นทาง": [q(o["x"], 1) for o in pp["observations"]],
        "เหตุการณ์": [o["event"] for o in pp["observations"]],
        "บล็อก": pp["blocked_entry_observations"], "ขอกลับมา": len(pp["resume_attempts"]),
        "ขอกลับมาสำเร็จ": sum(1 for r in pp["resume_attempts"] if r["accepted"]),
        "ราคาการพัก": q(10 * (D("3.8") - D("2.4")) - 1, 0),
        "ค่ากลางเลื่อน": {"X": [q(v, 0) for v in mr["moving_mean"]["spread_marks"]],
                          "ค่ากลาง": [q(v, 0) for v in mr["moving_mean"]["estimated_means"]],
                          "ระยะ": [q(v, 0) for v in mr["moving_mean"]["computed_residuals"]],
                          "กำไร": q(mr["moving_mean"]["actual_price_pnl_fixed_holdings"], 0)},
        "บัญชีคู่": q(sum(trade(k)["net_pnl"] for k in STOP_PATHS), 0),
    }

    # ── บท 15 ──
    br = p1["bridge"]
    ch15 = {
        "สะพาน": {"คาด": q(br["forecast_gross"], 0), "ราคาจริง": q(br["realized_ideal_mid_gross"], 0),
                  "ราคาที่ซื้อขายได้": q(br["actual_fill_gross"], 0), "หลังค่าธรรมเนียม": q(br["actual_fill_gross"] - br["fees"], 0),
                  "หลังค่าถือ": q(br["actual_net"], 0), "ผลของราคาfill": q(br["fill_price_difference"], 0),
                  "ค่าธรรมเนียม": -q(br["fees"], 0), "ค่าใช้จ่ายระหว่างถือ": -q(br["holding_carry_cost"], 0),
                  "คาดพลาด": q(br["forecast_comparison_gap"], 0)},
        "ลองหลายครั้ง": {k: tries[k] for k in ("1", "10", "50")},
        "เงินก็หลอกได้": fake_money(sel),
        "ตารางจำนวนรอบ": None,
    }

    # ── บท 16 ──
    pf = l3["partial_fill"]
    taker_fee = lambda xin, xout: D("0.0005") * ((10 * (100 + D(xin)) + 1000) + (10 * (100 + D(xout)) + 1000))
    fee_rows = {"1": taker_fee("2.1", "0.4"), "2": taker_fee("2.1", "1.8"), "3": taker_fee("2.1", "4.1")}
    gross3 = {"1": trade("convergence")["gross_price_pnl"], "2": trade("time")["gross_price_pnl"],
              "3": trade("gap")["gross_price_pnl"]}
    ch16 = {
        "ได้ขาเดียวบางส่วน": {"Aได้": 10, "Bเป้า": -20, "Bได้": -8, "longสุทธิ": q(pf["_net_long_value"], 0),
                              "ผลจริง": q(pf["actual_price_pnl"], 0), "ผลที่ตั้งใจ": q(pf["fully_filled_target_price_pnl"], 0)},
        "fillแย่กว่าmid": {"A": 100.1, "B": 49.95, "เสีย": q(l3["execution_slippage"]["entry_drag_already_in_cash"], 0),
                           "equityตอนเข้า": q(l3["execution_slippage"]["entry_snapshot"]["equity"], 0),
                           "equityภายหลัง": q(l3["execution_slippage"]["later_equity"], 0)},
        "ต้นทุนtakerของการ์ด": {k: q(v) for k, v in fee_rows.items()},
        "บัญชีคู่taker": {"ต้นทุนต่อไม้โดยประมาณ": 2,
                          "ไม้": [q(gross3[k] - 2, 0) for k in ("1", "2", "3")],
                          "รวม": q(sum(gross3[k] - 2 for k in gross3), 0),
                          "รวมแบบคิดค่าธรรมเนียมจริง": q(sum(gross3[k] - fee_rows[k] for k in gross3))},
        "capacity": {"หลัก": capacity(MIX_MAIN), "เทียบ": capacity(MIX_ALT)},
        "netting": {"คู่1B": -20, "คู่2B": 10, "สุทธิB": -10},
        "notradebuffer": None,
    }
    cap_main = {r["ขนาดต่อขา"]: r["ต่อรอบ"] for r in ch16["capacity"]["หลัก"]["ตาราง"]}
    ch16["capacity"]["ขนาดต่อขา"] = [1000, 5000, 10000, 20000]
    ch16["capacity"]["ต่อรอบ"] = [cap_main[x] for x in (1000, 5000, 10000, 20000)]

    # ── บท 17 ──
    dd = drawdown(SEED_FP)
    ch17 = {
        "รอบชดเชย": [ch06["รอบชดเชย"]["เสียทั้ง125000"], ch06["รอบชดเชย"]["เสียเฉพาะ25000"]],
        "ชนะ99": ch02["หางหนึ่งเปอร์เซ็นต์"]["ค่าคาดหมายต่อรอบ"],
        "ชนะ65": q(mss["forecast"]["separate_win_probability_example"]["expected_net_pnl"], 1),
        "ต้องชนะคู่": ch12["ต้องชนะเปอร์เซ็นต์"],
        "basisหดครึ่ง": ch05["บันไดแย่ง"][3]["ส่วนเกินเปอร์เซ็นต์"],
        "capacity": [cap_main[5000], cap_main[20000]],
        "leverageสวน10หมด": ch01["leverage"]["สวน10เปอร์เซ็นต์"],
        "ต้นทุนสองขาเป็นรอบfunding": {"ต้นทุน": 240, "fundingต่อรอบ": 10, "รอบ": 240 // 10},
        "ส่วนเกินcarryเทียบfunding": [ch05["บันได"]["ส่วนเกินเปอร์เซ็นต์"], ch07["บันไดfunding"]["ส่วนเกินเปอร์เซ็นต์"]],
        "ต้นขาด": ch04["ต้นขาด"],
        "drawdown": {"ตัวอย่าง": {k: v for k, v in dd.items() if not k.startswith("_")},
                     "กราฟ": dd["_curve"]},
        "ภาค1ต่อ1BTC": ch07["บัญชีสะสมภาค1"]["ต่อ1BTC"], "ภาค1ของมิน": ch07["บัญชีสะสมภาค1"]["ของมิน"],
        "คู่ตามกลยุทธ์": ch16["บัญชีคู่taker"]["รวม"],
    }

    # ── บท 18 ──
    sw = mss["forecast"]["separate_win_probability_example"]
    ch18 = {
        "บอทชนะ65": {"ชนะ": 65, "ได้": q(sw["gross_pnl_if_win"], 0), "เสีย": q(sw["gross_pnl_if_loss"], 0),
                     "ต้นทุน": q(sw["cost_in_each_outcome"], 1), "ก่อนต้นทุน": q(sw["expected_gross_pnl"], 1),
                     "ค่าคาดหมาย": q(sw["expected_net_pnl"], 1),
                     "100ครั้ง": {"ได้": 65, "เสีย": -105, "ต้นทุน": -10, "รวม": q(sw["expected_net_pnl"] * 100, 0)},
                     "คุ้มทุนเปอร์เซ็นต์": q((D(3) + D("0.1")) / D(4) * 100, 1)},
    }

    data = {
        "_อ่านก่อน": ("สร้างโดย tools/sab_figures.py — ห้ามแก้ด้วยมือ · ตัวเลขในคีย์บท (ch00–ch18 · เลขบทเล่มใหม่) "
                      "ปัดแล้วตามที่บทพิมพ์ · ค่าเต็มของต้นฉบับอยู่ใต้ _ต้นฉบับ (คีย์ = แฟ้ม:path) · "
                      "seed: บท 9 = 7 · บท 10 = 11 · บท 13 = 20261111 · seed_robustness = 1–30 · "
                      "ค่าธรรมเนียม: taker 0.05% (cash-and-carry) · maker 0.02% (perp) + คอลัมน์ taker · "
                      "null = ยังตรึงไม่ได้ (ดู บัญชีมิน.ค่าถือคู่ และ _สมมติฐาน)"),
        "บัญชีมิน": build_min(),
        "_สมมติฐาน": build_assumptions(),
        "เรื่อง": {"_หมายเหตุ": "คัมภีร์เรื่อง (partN.open/close) เป็นงานเฟส 0 — ยังว่าง"},
        "ch00": ch00, "ch01": ch01, "ch02": ch02, "ch03": ch03, "ch04": ch04, "ch05": ch05, "ch06": ch06,
        "ch07": ch07, "ch08": ch08, "ch09": ch09, "ch10": ch10, "ch11": ch11, "ch12": ch12, "ch13": ch13,
        "ch14": ch14, "ch15": ch15, "ch16": ch16, "ch17": ch17, "ch18": ch18,
        "seed_robustness": build_robustness(sel, pop, fp),
        "_claims": [{"id": "basis-long-leverage", "ข้อความ": "ฝั่ง long futures ยอมจ่ายเพื่อถือ exposure โดยวางเงินน้อย",
                     "ระดับหลักฐาน": "สมมติฐาน", "แหล่ง": None, "บท": [2, 5]}],
        "แบบฝึก": build_drills(),
        "แบบฝึก_v09": build_drills_v09(orig),
        "_errata": build_errata(),
    }
    data["_ต้นฉบับ"] = build_originals_strings(orig)
    return data


def build_robustness(sel, pop, fp):
    """ค่าที่บทอ้างจาก seed เดียว → min / มัธยฐาน / max ข้าม seed 1–30 (ตัวอย่าง = seed ของต้นฉบับ)"""
    def summ(example, vals, n=1, scale=1):
        vs = [v * scale for v in vals]
        return {"ตัวอย่าง": example, "มัธยฐาน": q(statistics.median(vs), n), "ต่ำสุด": q(min(vs), n),
                "สูงสุด": q(max(vs), n), "จำนวนseed": len(vs)}

    sels = [o_v09_selection(seed=sd, series=False) for sd in ROBUST_SEEDS]
    pops = [o_v09_population(seed=sd, series=False) for sd in ROBUST_SEEDS]
    fps = [o_v06_first_passage(seed=sd, cases=((0.99, 0.5),))[0] for sd in ROBUST_SEEDS]
    fakes = [fake_money(x) for x in sels]
    dds = [drawdown(sd) for sd in ROBUST_SEEDS]
    H = lambda p: p["H_high_corr_no_link"]
    C = lambda p: p["C_linked"]
    fp3 = fp[2]
    return {
        "_อ่านก่อน": "seed 1–30 (ชุดเดียวกับ audit) · ตัวอย่าง = ค่าที่บทใช้จาก seed ของต้นฉบับ (7 · 11 · 20261111)",
        "ch09": {
            "ในกรอบไม่มีเชือก": summ(pct(H(pop)["test_share_inside_2sd_avg"]), [H(p)["_inband_avg"] for p in pops], 1, 100),
            "ในกรอบมีเชือก": summ(pct(C(pop)["test_share_inside_2sd_avg"]), [C(p)["_inband_avg"] for p in pops], 1, 100),
            "corrไม่มีเชือก": summ(q(H(pop)["_corr_avg"], 3), [H(p)["_corr_avg"] for p in pops], 3),
            "corrมีเชือก": summ(q(C(pop)["_corr_avg"], 3), [C(p)["_corr_avg"] for p in pops], 3),
            "phiไม่มีเชือก": summ(q(H(pop)["_phi_avg"], 3), [H(p)["_phi_avg"] for p in pops], 3),
            "คู่ที่เกิน3มีเชือก": summ(pct(C(pop)["share_of_pairs_with_test_abs_z_above_3"], 0),
                                     [C(p)["share_of_pairs_with_test_abs_z_above_3"] for p in pops], 0, 100),
            "ทิศเดียวกันไม่มีเชือก": summ(pct(H(pop)["_same_direction_avg"]), [H(p)["_same_direction_avg"] for p in pops], 1, 100),
            "ทิศเดียวกันมีเชือก": summ(pct(C(pop)["_same_direction_avg"]), [C(p)["_same_direction_avg"] for p in pops], 1, 100),
        },
        "ch10": {
            "ระยะสูงสุดเฉลี่ย": summ(q(sel["selected"]["test_max_abs_z_avg"]), [x["_sel_maxz_avg"] for x in sels], 2),
            "ในกรอบ": summ(pct(sel["selected"]["test_share_inside_2sd_avg"]), [x["_sel_inband_avg"] for x in sels], 1, 100),
            "ในกรอบคู่จริง": summ(pct(sel["genuine"]["test_share_inside_2sd_avg"]), [x["_gen_inband_avg"] for x in sels], 1, 100),
            "ระยะสูงสุดคู่จริง": summ(q(sel["genuine"]["test_max_abs_z_avg"]), [x["_gen_maxz_avg"] for x in sels], 2),
            "ทั้ง200ในกรอบ": summ(pct(sel["_all_inband_avg"]), [x["_all_inband_avg"] for x in sels], 1, 100),
            "ข้ามค่ากลาง10อันดับ": summ(q(sel["selected"]["formation_crossings_avg"], 1),
                                      [x["selected"]["formation_crossings_avg"] for x in sels], 1),
            "คู่ที่คัดแย่กว่าคู่จริง": {"จำนวนseed": sum(1 for x in sels if x["_selected_worse_than_genuine"]),
                                        "จาก": len(sels)},
            "กรอบรั่วไม่มีเชือก": summ(pct(H(pop)["_leak_band_inband_avg"]), [H(p)["_leak_band_inband_avg"] for p in pops], 1, 100),
            "เกณฑ์85ปล่อยคู่ปลอม": summ(pct(H(pop)["_share_pass_85"]), [H(p)["_share_pass_85"] for p in pops], 1, 100),
            "เกณฑ์85ตัดคู่จริง": summ(pct(1 - C(pop)["_share_pass_85"], 0), [1 - C(p)["_share_pass_85"] for p in pops], 0, 100),
        },
        "ch13": {
            "มัธยฐานแตะเป้า": summ(fp3["median_first_passage"], [r["median_first_passage"] for r in fps], 0),
            "แตะก่อนครึ่งชีวิต": summ(pct(fp3["_share_done_within_half_life"]),
                                    [r["_share_done_within_half_life"] for r in fps], 1, 100),
            "ขึ้นถึง3ก่อน": summ(pct(fp3["share_touching_3_before_1"]), [r["_share_touching_3_before_1_exact"] for r in fps], 1, 100),
        },
        "ch15": {
            "รวมสุทธิ": summ(fake_money(sel)["รวมสุทธิ"], [f["รวมสุทธิ"] for f in fakes], 2),
            "จำนวนไม้": summ(len(fake_money(sel)["ไม้"]), [len(f["ไม้"]) for f in fakes], 0),
            "seedที่หยุดเพราะงบ": sum(1 for f in fakes if f["หยุดเปิดเพราะงบ"]),
        },
        "ch17": {
            "ลึกสุด": summ(drawdown(SEED_FP)["ลึกสุด"], [d["ลึกสุด"] for d in dds], 0),
            "นานสุดไม้": summ(drawdown(SEED_FP)["นานสุดไม้"], [d["นานสุดไม้"] for d in dds], 0),
            "ผลรวม100ไม้": summ(drawdown(SEED_FP)["ผลรวม100ไม้"], [d["ผลรวม100ไม้"] for d in dds], 0),
        },
    }


def build_drills():
    c5 = carry_ladder(basis=D(1200), cap=D(75000), s0=D(60000), days=D(60), st=D(61200))
    c5h = carry_ladder(basis=D(600), cap=D(75000), s0=D(60000), days=D(60), st=D(60600))
    # (ข) ทุน 125,000 วันที่สองราคา futures ขึ้นอีก 3% จาก 113,200
    rise2 = D(113200) * D("0.03")
    top2 = D("1.1") * rise2
    free_after1 = {c: D(c) - 100000 - 10300 - D(11220) for c in (125000, 150000)}
    return {
        "_หมายเหตุ": "ยังไม่ครบทุกบท — เติมเมื่อเขียน ✍️ ของบทนั้น",
        "ch04": [{"ทุน": 150000, "กันชน": pct(o_v06_margin("150000")["max_one_day_future_rise_covered"] / 103000)},
                 {"ทุน": 125000, "ขึ้นวันที่สองเปอร์เซ็นต์": 3, "ต้องโอนวันที่สอง": q(top2, 1),
                  "เงินสดอิสระหลังวันแรก": q(free_after1[125000], 0), "ขาด": q(top2 - free_after1[125000], 1),
                  "ทุน150000ขาด": q(max(D(0), top2 - free_after1[150000]), 1)}],
        "ch05": [{"spot": 60000, "futures": 61200, "วัน": 60, "ทุน": 75000,
                  "บันได": {"บนจอ": q(c5["simple_rate_on_spot_pct"]), "ต่อทุน": q(c5["price_return_on_capital_pct_yr"]),
                            "หลังค่าธรรมเนียม": q(c5["net_on_capital_pct_yr"]), "ส่วนเกินเปอร์เซ็นต์": q(c5["excess_pct_yr"])},
                  "basisเหลือครึ่ง": {"บนจอ": q(c5h["simple_rate_on_spot_pct"]), "ต่อทุน": q(c5h["price_return_on_capital_pct_yr"]),
                                      "หลังค่าธรรมเนียม": q(c5h["net_on_capital_pct_yr"]), "ส่วนเกินเปอร์เซ็นต์": q(c5h["excess_pct_yr"])},
                  "สมมติฐาน": "ราคาชำระ = 61,200 (ดู _สมมติฐาน)"},
                 {"ทุน": 150000, "หลังค่าธรรมเนียม": q(carry_ladder(cap=D(150000))["net_on_capital_pct_yr"]),
                  "ค่าเสียโอกาส": q(carry_ladder(cap=D(150000))["opportunity_cost"]),
                  "ส่วนเกิน": q(carry_ladder(cap=D(150000))["excess"])}],
        "ch06": [{"basisวันที่30": 1500, "ถือได้เพิ่ม": q(early_close("0.04", f30=D(102500))["extra_from_holding"]),
                  "เสียโอกาส": q(early_close("0.04", f30=D(102500))["opportunity_60d"]), "ตัดสิน": "ถือ"}],
        "ch08": [{"ต้องการBTC": 0.015, "ปัดเป็น": 0.01, "exposure": 500}, {"ต้องการBTC": 0.015, "ปัดเป็น": 0.02, "exposure": -500}],
        "ch10": [{"ลอง": 10, "โอกาสบังเอิญต่อครั้ง": 5, "เจออย่างน้อยหนึ่ง": pct(1 - D("0.95") ** 10)}],
        "ch18": [{"ชนะ": 65, "ได้": 1, "เสีย": 3, "ต้นทุน": 0.1, "ค่าคาดหมาย": -0.5, "คุ้มทุนเปอร์เซ็นต์": 77.5}],
    }


def build_drills_v09(orig):
    v07 = orig["v07_primer_checks"]["self_check"]
    ex = orig["v06_enrichment_demo"]["exercise_checks"]
    v9 = orig["v09_ch06_ch07_demo"]["exercises"]
    return {
        "00.07": {"ข้อ1": q(v07["q1"], 0), "ข้อ2มูลค่า": q(v07["q2_notional"], 0), "ข้อ2เสีย": q(v07["q2_loss"], 0),
                  "ข้อ2ส่วนของหลักประกัน": pct(v07["q2_share_of_margin"], 0), "ข้อ3": q(v07["q3"], 0),
                  "ข้อ4": q(v07["q4"], 0), "ข้อ5": q(v07["q5"], 0)},
        "03_ข้อ7": {"ต้องโอน": q(ex["ch03_ex7"]["top_up"], 0), "เงินสดอิสระหลังโอน": q(ex["ch03_ex7"]["free_cash_after"], 0),
                    "equityเปลี่ยน": q(ex["ch03_ex7"]["equity_change"], 0)},
        "04_ข้อ4": {"bไม่มีความเสี่ยงเฉพาะ": q(ex["ch04_ex4"]["b_if_no_specific_risk"], 1),
                    "bความเสี่ยงเฉพาะ2": q(ex["ch04_ex4"]["b_if_specific_sd_2pct"], 2),
                    "sd": {k: q(v, 1) for k, v in ex["ch04_ex4"]["pnl_sd"].items()}},
        "06_ข้อ1": {"หลังค่าธรรมเนียม": q(v9["ch06_ex1_capital_150000"]["net_pct_yr"]),
                    "ค่าเสียโอกาส": q(v9["ch06_ex1_capital_150000"]["opp"]),
                    "ส่วนเกิน": q(v9["ch06_ex1_capital_150000"]["excess"])},
        "06_ข้อ2": {"ถือได้เพิ่ม": q(v9["ch06_ex2_basis_1500"]["extra"]), "เสียโอกาส": q(v9["ch06_ex2_basis_1500"]["opp"]),
                    "ตัดสิน": "ถือ" if v9["ch06_ex2_basis_1500"]["decision"] == "hold" else "ปิด"},
    }


def build_errata():
    """แผน 1.4 — ค่าที่ JSON นี้ถือเป็นค่าที่แก้แล้ว (ต้นฉบับผิดในเนื้อความ ไม่ใช่ในโค้ด เว้นแต่ระบุ)"""
    return [
        {"ข้อ": 1, "ต้นฉบับ": "12 − 8 = −4", "แก้": "8 − 12 = −4", "คีย์": "ch15/สะพาน/คาดพลาด"},
        {"ข้อ": 2, "ต้นฉบับ": "+5 − 7 = −2 ไม่ระบุสถานะ", "แก้": "ไม่ hedge −2 · hedge ครบ +5", "คีย์": "ch02/โจทย์funding"},
        {"ข้อ": 3, "ต้นฉบับ": "ภาพหาง 60 ช่วง", "แก้": "50 ช่วง", "คีย์": "ch02/ช่วงในภาพหาง"},
        {"ข้อ": 10, "ต้นฉบับ": "ข้อสรุป beta neutral ยืนบนคอลัมน์ sd", "แก้": "stress B ขยับเอง 1% → −5/−10/−15 · sd ไป 🔎",
         "คีย์": "ch08/stress_B1"},
        {"ข้อ": 13, "ต้นฉบับ": "25,000 cash reserve", "แก้": "25,000 = หลักประกัน 10,300 + เงินสดอิสระ 14,700", "คีย์": "ch03/เปิดไม้"},
        {"ข้อ": 14, "ต้นฉบับ": "รองรับการขึ้นได้ราว 13% ต่อวัน", "แก้": "สะสม 13.0% · หลังวันแรกรับได้อีก 2.8%",
         "คีย์": "ch04/หลังวันแรกรับได้อีก"},
        {"ข้อ": 15, "ต้นฉบับ": "ค่าธรรมเนียม 0.05% → 0.02% เงียบ ๆ", "แก้": "maker 0.02% + คอลัมน์ taker", "คีย์": "ch07/สี่เส้นทาง"},
        {"ข้อ": 17, "ต้นฉบับ": "correlation = ขยับทางเดียวกันบ่อยแค่ไหน", "แก้": "ทิศเดียวกัน 85.7% / 75.6% + ตารางแปลง",
         "คีย์": "ch09/ตารางแปลงcorrelation"},
        {"ข้อ": 19, "ต้นฉบับ": "แถวทั้ง 200 คู่ว่าง · seed 11 เบาที่สุด", "แก้": "เติมแถว + มัธยฐาน 30 seed",
         "คีย์": "ch10/ทั้ง200คู่ · seed_robustness/ch10"},
        {"ข้อ": 22, "ต้นฉบับ": "10 × 1.7 − 1", "แก้": "10 × (2.1 − 0.4) − 1 = 16", "คีย์": "ch12/เส้นทาง/1"},
        {"ข้อ": 24, "ต้นฉบับ": "ราว 85% · กฎเปลี่ยนเงียบ", "แก้": "85.6% → ราว 86% · ระยะ z ของจุดเข้า 12.0 / 2.4 / 0.56",
         "คีย์": "ch13/แตะเป้า"},
        {"ข้อ": 31, "ต้นฉบับ": "ชุด beta 1.2/0.8 · stress beta A → 1.4 (−50 บน gross 20,000)",
         "แก้": "ชุดเดียว 1.5/1.0 · beta A 1.5 → 1.7 · BTC −5% → −10", "คีย์": "ch08/beta_stress"},
        {"ข้อ": 32, "ต้นฉบับ": "ห่าง 0.18 (log)", "แก้": "ราว 16–17% (e^(−0.1803) − 1)", "คีย์": "ch10/อันดับ1/ห่างจากค่ากลางเปอร์เซ็นต์"},
        {"ข้อ": 34, "ต้นฉบับ": "เสียโอกาส 821.92 ไม่บอกว่าเป็นค่าประมาณ", "แก้": "บนทุนตั้งต้น 821.92 · บนเงินที่ปลดได้ 837.02",
         "คีย์": "ch06/วันที่30"},
        {"ข้อ": 35, "ต้นฉบับ": "ครึ่งชีวิต 28.5 ไม่บอกที่มา", "แก้": "จากค่าเฉลี่ย φ · มัธยฐาน 33.3", "คีย์": "ch09/ลงลึก"},
        {"ข้อ": 37, "ต้นฉบับ": "ปิดตามกฎแม้สุทธิติดลบ (ตัวอย่างแสดงไม่ได้)", "แก้": "เส้นทาง 4 −17", "คีย์": "ch12/เส้นทาง/4"},
    ]


def _get(obj, path):
    for seg in path.split("/") if path else []:
        obj = obj[int(seg)] if isinstance(obj, list) else obj[seg]
    return obj


def load_origmap():
    with open(ORIGMAP, encoding="utf-8") as fh:
        return json.load(fh)


def build_originals_strings(orig):
    """_ต้นฉบับ: ค่าเต็ม (สตริง) ของพอร์ตที่สเกลต้นฉบับ สำหรับทุกค่าสเกลาร์ที่ origmap จับคู่"""
    om = load_origmap()
    out = {}
    for thai, e in om["จับคู่"].items():
        v = _get(orig[e["file"]], e["path"])
        if isinstance(v, (list, dict)) or v is None:
            continue
        out[f"{e['file']}:{e['path']}"] = v if isinstance(v, (str, bool)) else str(v)
    return dict(sorted(out.items()))


def compute():
    return build(originals_port())


def dump(data):
    return json.dumps(data, ensure_ascii=False, indent=1) + "\n"


# ════════════════════════════════════════════════════════════════════════════
#  ส่วน ง — G1 / C4: เทียบกับโค้ดต้นฉบับ
# ════════════════════════════════════════════════════════════════════════════
def load_original(stem):
    path = os.path.join(SOURCE_DIR, "code", stem + ".py")
    spec = importlib.util.spec_from_file_location(f"sab_orig_{stem}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)          # ชื่อโมดูลไม่ใช่ "__main__" → บล็อก __main__ ของต้นฉบับไม่ทำงาน
    return mod


def run_original(stem, call):
    mod = load_original(stem)
    if call == "examples()":
        return json.loads(json.dumps(mod.examples(), ensure_ascii=False, default=str))
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        mod.main()
    return json.loads(buf.getvalue())


def numeric_leaves(obj, prefix=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from numeric_leaves(v, f"{prefix}/{k}" if prefix else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from numeric_leaves(v, f"{prefix}/{i}" if prefix else str(i))
    elif isinstance(obj, bool) or obj is None:
        return
    elif isinstance(obj, (int, float)):
        yield prefix
    elif isinstance(obj, str):
        try:
            D(obj)
            yield prefix
        except Exception:
            return


def dec(v):
    return v if isinstance(v, D) else D(str(v))


def matches(orig_v, sab_v, k, places=None, translate=None):
    if isinstance(orig_v, list):
        return isinstance(sab_v, list) and len(orig_v) == len(sab_v) and all(
            matches(a, b, k, places, translate) for a, b in zip(orig_v, sab_v))
    if translate is not None or isinstance(orig_v, bool):
        return (translate or {}).get(str(orig_v), orig_v) == sab_v
    if sab_v is None:
        return False
    target = dec(orig_v) * D(k)
    if isinstance(sab_v, str):
        return dec(sab_v) == target
    if places is None:
        places = 0 if isinstance(sab_v, int) else max(0, -D(repr(sab_v)).as_tuple().exponent)
    rounded = target.quantize(D(1).scaleb(-places), rounding=ROUND_HALF_UP) if places else \
        target.quantize(D(1), rounding=ROUND_HALF_UP)
    return rounded == dec(sab_v)


def check_original(sab):
    om = load_origmap()
    fails, outputs = [], {}
    print(f"G1 · โค้ดต้นฉบับจาก {os.path.relpath(SOURCE_DIR, ROOT)}/code")
    for stem, meta in om["แฟ้ม"].items():
        outputs[stem] = run_original(stem, meta["เรียก"])
        with open(os.path.join(SOURCE_DIR, "code", meta["ผล"]), encoding="utf-8") as fh:
            stored = json.load(fh)
        same = stored == outputs[stem]
        print(f"  {'✓' if same else '✗'} {stem}.{meta['เรียก'].rstrip('()')}() = {meta['ผล']}")
        if not same:
            fails.append(f"{stem}: ผลที่รันได้ไม่ตรง {meta['ผล']}")
    ok_map = 0
    for thai, e in om["จับคู่"].items():
        try:
            ov = _get(outputs[e["file"]], e["path"])
            sv = _get(sab, thai)
        except (KeyError, IndexError, TypeError) as exc:
            fails.append(f"{thai}: หา path ไม่เจอ ({exc!r})")
            continue
        if matches(ov, sv, e.get("k", "1"), e.get("ปัด"), e.get("แปล")):
            ok_map += 1
        else:
            fails.append(f"{thai} = {sv!r} แต่ต้นฉบับ {e['file']}:{e['path']} = {ov!r} × {e.get('k', '1')}")
    ok_str = 0
    for key, v in sab.get("_ต้นฉบับ", {}).items():
        stem, path = key.split(":", 1)
        ov = _get(outputs[stem], path)
        if (str(ov) == v) if isinstance(ov, str) and not _isnum(ov) else (ov == v if isinstance(ov, bool) else dec(ov) == dec(v)):
            ok_str += 1
        else:
            fails.append(f"_ต้นฉบับ {key} = {v!r} แต่ต้นฉบับ = {ov!r}")
    # นับค่าที่ยังไม่จับคู่
    covered = {}
    for e in om["จับคู่"].values():
        covered.setdefault(e["file"], []).append(e["path"])
    excluded = {stem: list(d) for stem, d in om.get("_ไม่ใช้", {}).items()}
    total = mapped = skipped = 0
    unmapped = []
    under = lambda p, prefixes: any(p == x or p.startswith(x + "/") for x in prefixes)
    for stem, out in outputs.items():
        for leaf in numeric_leaves(out):
            total += 1
            if under(leaf, covered.get(stem, [])):
                mapped += 1
            elif under(leaf, excluded.get(stem, [])):
                skipped += 1
            else:
                unmapped.append(f"{stem}:{leaf}")
    print(f"  คีย์ไทยที่จับคู่ (C4): {ok_map}/{len(om['จับคู่'])} ตรง × k")
    print(f"  _ต้นฉบับ (สตริงเต็ม): {ok_str}/{len(sab.get('_ต้นฉบับ', {}))} ตรงตัว")
    print(f"  ค่าตัวเลขในผลต้นฉบับ {total} ค่า: จับคู่ {mapped} · ประกาศว่าไม่ใช้ (มีเหตุผลใน origmap) {skipped} · "
          f"ยังไม่จับคู่ {len(unmapped)}")
    for u in unmapped[:40]:
        print("    ยังไม่จับคู่:", u)
    for f in fails[:60]:
        print("  ✗", f)
    return not fails and not unmapped


def _isnum(x):
    try:
        D(x)
        return True
    except Exception:
        return False


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--check-original" in args:
        if not os.path.isdir(os.path.join(SOURCE_DIR, "code")):
            sys.exit(f"ไม่พบโค้ดต้นฉบับที่ {SOURCE_DIR}/code — ตั้งตัวแปร SAB_SOURCE_DIR")
        with open(OUT, encoding="utf-8") as fh:
            sab = json.load(fh)
        ok = check_original(sab)
        print("G1 ผ่าน ✓" if ok else "G1 ไม่ผ่าน")
        sys.exit(0 if ok else 1)
    data = compute()
    text = dump(data)
    if "--check" in args:
        with open(OUT, encoding="utf-8") as fh:
            old = fh.read()
        if old != text:
            a, b = json.loads(old), json.loads(text)
            diffs = []

            def walk(x, y, p=""):
                if isinstance(x, dict) and isinstance(y, dict):
                    for k in sorted(set(x) | set(y)):
                        walk(x.get(k, "<ไม่มี>"), y.get(k, "<ไม่มี>"), f"{p}/{k}")
                elif isinstance(x, list) and isinstance(y, list) and len(x) == len(y):
                    for i, (u, v) in enumerate(zip(x, y)):
                        walk(u, v, f"{p}/{i}")
                elif x != y:
                    diffs.append(f"{p}: ไฟล์ {x!r} · คำนวณใหม่ {y!r}")

            walk(a, b)
            for d_ in diffs[:40]:
                print(" ", d_)
            print(f"{os.path.basename(OUT)} ไม่ตรงกับการคำนวณ ({len(diffs)} จุด) — รัน tools/sab_figures.py ใหม่")
            sys.exit(1)
        print(f"{os.path.basename(OUT)} ตรงกับการคำนวณ ✓")
    else:
        with open(OUT, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("เขียน", os.path.relpath(OUT, ROOT))
