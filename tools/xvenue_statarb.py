#!/usr/bin/env python3
"""Cross-venue perp spread stat arb (full hedge) — simulator / backtester

ใช้คู่กับ docs/xvenue-statarb-design.md

แนวคิด: เปิด long perp ที่ตลาดหนึ่ง + short perp สินทรัพย์เดียวกันอีกตลาด (เช่น Lighter × Bitget/Bybit)
รวมกันเป็น delta-neutral แล้วหากำไรจาก (1) ส่วนต่างราคาข้ามตลาดที่วิ่งกลับเข้าค่าเฉลี่ย
(2) ส่วนต่าง funding ระหว่างตลาด — เป็น "arbitrage เชิงสถิติ" เพราะไม่มีอะไรบังคับให้ส่วนต่างต้องกลับ

รูปแบบข้อมูล (CSV, หนึ่งแถวต่อหนึ่ง bar เวลาเท่ากัน เช่น 1 นาที):
    ts,mid_a,mid_b,funding_a,funding_b
    funding_* = อัตรา funding ที่ "long จ่าย" ใน bar นั้น (0 ถ้า bar นั้นไม่มีการเก็บ funding)

รัน:
    python3 tools/xvenue_statarb.py                       # ข้อมูลจำลอง (ดีฟอลต์)
    python3 tools/xvenue_statarb.py --csv mydata.csv --fee-b-bps 1.0 --leverage 3
    python3 tools/xvenue_statarb.py --sweep               # ไล่ leverage ดูว่าต้องโยกเงินบ่อยแค่ไหน
"""

import argparse
import csv
import math

import numpy as np

BARS_PER_YEAR_1M = 365 * 24 * 60


# ───────────────────────── ข้อมูล ─────────────────────────

def synth(days=90, seed=7):
    """ราคาจำลอง: underlying GBM ที่มี regime ความผันผวน + spread ข้ามตลาดแบบ OU
    ที่ความกว้างแปรตามความผันผวน (ตลาดผันผวน → ราคาสองตลาดหลุดกันมากขึ้น) + funding รายชั่วโมง"""
    rng = np.random.default_rng(seed)
    n = days * 24 * 60
    # regime: 0 = เงียบ, 1 = ผันผวน (Markov สลับเฉลี่ยทุก ~3 วัน)
    regime = np.zeros(n, dtype=int)
    p_switch = 1 / (3 * 24 * 60)
    for i in range(1, n):
        regime[i] = 1 - regime[i - 1] if rng.random() < p_switch else regime[i - 1]
    ann_vol = np.where(regime == 1, 0.90, 0.35)
    sig = ann_vol / math.sqrt(BARS_PER_YEAR_1M)
    log_p = np.cumsum(rng.normal(0, sig)) + math.log(60_000)

    # spread (log) ของ A เทียบ B: OU, mean 1.5 bp, half-life ~20 นาที, σ ขึ้นกับ regime
    hl = 20.0
    phi = math.exp(-math.log(2) / hl)
    mu = 1.5e-4
    eq_sd = np.where(regime == 1, 3.5e-4, 1.5e-4)            # 6 bp vs 2 bp
    shock_sd = eq_sd * math.sqrt(1 - phi ** 2)
    x = np.empty(n)
    x[0] = mu
    eps = rng.standard_t(4, n) / math.sqrt(2)             # หางอ้วน
    for i in range(1, n):
        x[i] = mu + phi * (x[i - 1] - mu) + shock_sd[i] * eps[i]

    mid_b = np.exp(log_p)
    mid_a = mid_b * np.exp(x)

    # funding: A เก็บทุกชั่วโมง, B ทุก 8 ชั่วโมง; ค่าเฉลี่ยต่างกันเล็กน้อยและผันผวนช่วงตลาดแรง
    fa = np.zeros(n)
    fb = np.zeros(n)
    base = 1.0e-4 / 8                                    # 0.01%/8h ≈ ต่อชั่วโมง
    for i in range(0, n, 60):
        boost = 3.0 if regime[i] == 1 else 1.0
        fa[i] = base * boost + rng.normal(0, 0.6e-5 * boost)
    for i in range(0, n, 480):
        boost = 3.0 if regime[i] == 1 else 1.0
        fb[i] = 1.0e-4 * boost * 0.8 + rng.normal(0, 3e-5 * boost)
    return {"mid_a": mid_a, "mid_b": mid_b, "funding_a": fa, "funding_b": fb, "regime": regime}


def load_csv(path):
    cols = {"mid_a": [], "mid_b": [], "funding_a": [], "funding_b": []}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            for k in cols:
                cols[k].append(float(row.get(k) or 0.0))
    return {k: np.asarray(v) for k, v in cols.items()}


# ───────────────────────── กลยุทธ์ ─────────────────────────

def backtest(d, *, capital=100_000.0, leverage=3.0, ewm_hl=360, z_layers=(1.5, 2.5, 3.5),
             z_exit=0.3, max_hold=240, fee_a_bps=0.0, fee_b_bps=2.0, slip_bps=0.5,
             min_edge_bps=1.0, carry_weight=1.0, rebalance_at=0.5, warmup=720):
    """คืนค่า dict สถิติ

    capital แบ่งครึ่งไว้สองตลาด; notional สูงสุดต่อขา = leverage × capital/2
    ตำแหน่ง = ชั้นละ 1/len(z_layers) ของ notional สูงสุด (เข้าแบบขั้นบันไดเมื่อ |z| กว้างขึ้น)
    pos > 0 หมายถึง long A / short B (เมื่อ A ถูกกว่าปกติ)
    rebalance_at: ถ้า equity ของตลาดใดเหลือ < rebalance_at × equity เริ่มต้นของตลาดนั้น → นับว่าต้องโยกเงิน
    """
    mid_a, mid_b = d["mid_a"], d["mid_b"]
    fa, fb = d["funding_a"], d["funding_b"]
    n = len(mid_a)
    x = np.log(mid_a) - np.log(mid_b)

    alpha = 1 - math.exp(-math.log(2) / ewm_hl)
    max_notional = leverage * capital / 2
    layer = max_notional / len(z_layers)
    cost_rt_bps = 2 * (fee_a_bps + fee_b_bps) + 4 * slip_bps   # เปิด+ปิด สองขา

    m, v = x[0], (2e-4) ** 2
    pos_layers = 0          # มีเครื่องหมาย: +k = long A k ชั้น
    held = 0
    eq_a = eq_b = capital / 2
    min_buf = 1.0
    transfers = 0
    pnl_spread = pnl_fund = pnl_fee = 0.0
    trades = 0
    equity_curve = np.empty(n)
    notional_a = 0.0        # notional ที่ถือ (USD, + = long) ณ ราคาปัจจุบัน
    notional_b = 0.0

    for t in range(n):
        if t > 0:
            ra = mid_a[t] / mid_a[t - 1] - 1
            rb = mid_b[t] / mid_b[t - 1] - 1
            ga, gb = notional_a * ra, notional_b * rb
            eq_a += ga
            eq_b += gb
            pnl_spread += ga + gb
            notional_a *= 1 + ra
            notional_b *= 1 + rb
        # funding: long จ่าย rate × notional
        fund = -notional_a * fa[t] - notional_b * fb[t]
        eq_a += -notional_a * fa[t]
        eq_b += -notional_b * fb[t]
        pnl_fund += fund

        # อัปเดตค่าเฉลี่ย/ความแปรปรวนแบบ EWMA (ใช้ข้อมูลถึง t เท่านั้น)
        dev = x[t] - m
        m += alpha * dev
        v = (1 - alpha) * (v + alpha * dev * dev)
        sd = math.sqrt(max(v, 1e-12))
        z = (x[t] - m) / sd

        # margin buffer ต่อขา: equity / (notional/leverage) — ต่ำกว่า rebalance_at ⇒ โยกเงิน
        for side in ("a", "b"):
            eq = eq_a if side == "a" else eq_b
            init = capital / 2
            if abs(notional_a) > 0 and eq < rebalance_at * init:
                transfers += 1
                tot = eq_a + eq_b
                eq_a = eq_b = tot / 2           # โยกให้เท่ากัน (สมมติโยกได้ทันที)
            min_buf = min(min_buf, eq / init)

        if t < warmup:
            equity_curve[t] = eq_a + eq_b
            continue

        # ── ตัดสินใจ ──
        # carry ที่คาดว่าจะได้ต่อ bar ถ้า long A/short B: ใช้ funding ล่าสุดแบบประมาณ (EW)
        target = pos_layers
        exp_edge_bps = abs(x[t] - m) * 1e4
        if pos_layers == 0:
            k = sum(abs(z) >= zl for zl in z_layers)
            if k > 0 and exp_edge_bps - cost_rt_bps >= min_edge_bps:
                target = -k if z > 0 else k        # A แพงไป → short A / long B
        else:
            same_dir = (pos_layers > 0 and z < 0) or (pos_layers < 0 and z > 0)
            k = sum(abs(z) >= zl for zl in z_layers)
            if same_dir and k > abs(pos_layers):
                target = int(math.copysign(k, pos_layers))   # เติมชั้น
            if (pos_layers > 0 and z > -z_exit) or (pos_layers < 0 and z < z_exit) or held >= max_hold:
                target = 0
        if target != pos_layers:
            delta = (target - pos_layers) * layer
            # ปรับขนาดตามราคาปัจจุบัน: ขา A = +delta, ขา B = -delta
            fee = abs(delta) * (fee_a_bps + fee_b_bps + 2 * slip_bps) * 1e-4
            eq_a -= abs(delta) * (fee_a_bps + slip_bps) * 1e-4
            eq_b -= abs(delta) * (fee_b_bps + slip_bps) * 1e-4
            pnl_fee -= fee
            if target == 0:
                notional_a = notional_b = 0.0
            else:
                notional_a += delta
                notional_b -= delta
            trades += 1
            held = 0 if target == 0 or pos_layers == 0 else held
            pos_layers = target
        if pos_layers != 0:
            held += 1
        equity_curve[t] = eq_a + eq_b

    total = eq_a + eq_b - capital
    years = n / BARS_PER_YEAR_1M
    rets = np.diff(equity_curve[::1440]) / capital
    sharpe = (rets.mean() / rets.std() * math.sqrt(365)) if rets.std() > 0 else float("nan")
    peak = np.maximum.accumulate(equity_curve)
    mdd = ((equity_curve - peak) / capital).min()
    return {
        "leverage": leverage,
        "ann_return": total / capital / years,
        "sharpe_daily": sharpe,
        "max_dd": mdd,
        "trades": trades,
        "pnl_spread": pnl_spread,
        "pnl_funding": pnl_fund,
        "pnl_fees": pnl_fee,
        "transfers": transfers,
        "min_leg_equity_ratio": min_buf,
        "cost_rt_bps": cost_rt_bps,
    }


def show(r):
    print(f"leverage/ขา        : {r['leverage']:.1f}x")
    print(f"ผลตอบแทนต่อปี      : {r['ann_return']*100:6.2f}%")
    print(f"Sharpe (รายวัน)     : {r['sharpe_daily']:.2f}")
    print(f"Max drawdown       : {r['max_dd']*100:6.2f}% ของทุน")
    print(f"จำนวนครั้งปรับ pos : {r['trades']}")
    print(f"PnL spread / funding / fee : {r['pnl_spread']:,.0f} / {r['pnl_funding']:,.0f} / {r['pnl_fees']:,.0f}")
    print(f"ต้นทุนไป-กลับ      : {r['cost_rt_bps']:.1f} bp")
    print(f"ต้องโยกเงินข้ามตลาด : {r['transfers']} ครั้ง; equity ขาที่แย่สุดเหลือ {r['min_leg_equity_ratio']*100:.0f}% ของตั้งต้น")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv")
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--leverage", type=float, default=3.0)
    ap.add_argument("--fee-a-bps", type=float, default=0.0, help="ค่าธรรมเนียมตลาด A ต่อข้าง (Lighter standard = 0)")
    ap.add_argument("--fee-b-bps", type=float, default=2.0, help="ค่าธรรมเนียมตลาด B ต่อข้าง (CEX maker/ที่ต่อรองได้)")
    ap.add_argument("--slip-bps", type=float, default=0.5)
    ap.add_argument("--sweep", action="store_true", help="ไล่ leverage 1–10x")
    a = ap.parse_args()

    d = load_csv(a.csv) if a.csv else synth(a.days)
    kw = dict(fee_a_bps=a.fee_a_bps, fee_b_bps=a.fee_b_bps, slip_bps=a.slip_bps)
    if a.sweep:
        print(f"{'lev':>4} {'ret/yr':>8} {'maxDD':>7} {'โยกเงิน':>8} {'equityขาต่ำสุด':>14}")
        for lev in (1, 2, 3, 5, 8, 10):
            r = backtest(d, leverage=lev, **kw)
            print(f"{lev:>4} {r['ann_return']*100:7.1f}% {r['max_dd']*100:6.1f}% {r['transfers']:>8} {r['min_leg_equity_ratio']*100:13.0f}%")
    else:
        show(backtest(d, leverage=a.leverage, **kw))


if __name__ == "__main__":
    main()
