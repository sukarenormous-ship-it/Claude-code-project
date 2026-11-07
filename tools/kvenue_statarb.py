#!/usr/bin/env python3
"""Multi-leg (K-venue) hub-and-spoke consensus stat arb — ตัวจำลอง/backtester

ใช้คู่กับ docs/kvenue-statarb-design.md  (ฉบับ 2 ขาเดิม: tools/xvenue_statarb.py)

แนวคิด: สินทรัพย์เดียวกันซื้อขายอยู่หลายตลาดพร้อมกัน (Lighter Core = LC, Lighter on Robinhood Chain = LR,
Bitget = BG, Bybit = BY) → ถือสถานะ n[a,k] บนหลายตลาดโดยบังคับ Σ_k n[a,k] = 0 ทุกสินทรัพย์ (full hedge)
แล้วหากำไรจาก "ราคาตลาด k เทียบราคากลางข้ามตลาด (consensus)" ที่วิ่งกลับเข้าหาค่าเฉลี่ย
  • hub  = Lighter ทั้งสองตัว (ค่าธรรมเนียม 0) รับขาที่ต้องจ่ายข้ามสเปรด (taker) และรับส่วนเกินทั้งหมด
  • spoke = CEX ส่งเฉพาะ post-only (maker) และเปิดเฉพาะเมื่อส่วนต่างชนะค่าธรรมเนียมที่ต่อรองได้
  • แต่ละตลาดมี margin แยก → "รวมกันไม่มี downside แต่บางขาโดน liquidate ได้" ถูกจำลองตรงๆ

**ตัวเลขผลตอบแทนจากข้อมูลสังเคราะห์ขึ้นกับพารามิเตอร์ที่สมมติ (โดยเฉพาะ --resid-scale) ใช้ดูพฤติกรรมเชิงเปรียบเทียบเท่านั้น**

รัน:
    python3 tools/kvenue_statarb.py                         # จำลอง 4 ตลาด × 4 สินทรัพย์ 60 วัน
    python3 tools/kvenue_statarb.py --venues LC,LR,BG       # ไม่มี Bybit (ผู้ใช้ในไทย)
    python3 tools/kvenue_statarb.py --pairs-only LC-BG      # baseline 2 ขาแบบเดิม
    python3 tools/kvenue_statarb.py --sweep fees            # fees | lev | legs | thai | lcost | resid | all
    python3 tools/kvenue_statarb.py --selftest              # ตรวจ invariant (Σn=0, เงินสดไม่รั่ว ฯลฯ)
    python3 tools/kvenue_statarb.py --csv data.csv --calibrate   # วัด half-life/σ จากข้อมูลจริงก่อนเทรด

รูปแบบ CSV (long, หนึ่งแถวต่อ ts × asset × venue):
    ts,asset,venue,bid,ask,funding,mkt_open
    ts = unix วินาที (UTC) ปิด bar; funding = อัตราที่ "long จ่าย" ที่ settle ใน bar นั้น (ไม่มี = 0)
    mkt_open = 1/0 สำหรับหุ้น/ทอง (ไม่ใส่ = เปิดตลอด); venue ที่ใส่ใน --data-only ใช้ทำราคากลางอย่างเดียว
"""

import argparse
import csv
import math
import sys
from collections import defaultdict

import numpy as np

BP = 1e-4

# ───────────────────────── ค่าตั้งต้นของตลาดและสินทรัพย์ ─────────────────────────
# fee/cost หน่วย bp ต่อข้าง; lag = สัดส่วนที่ราคาตลาดนั้น "ตามไม่ทัน" การเคลื่อนของราคาจริงใน bar เดียว
# s_u/hl_u = ขนาด (bp) และ half-life (นาที) ของ residual เร็วของตลาดนั้น
VENUES = {
    "LC": dict(kind="lighter", maker=0.0, taker=0.0, adv_taker=0.7, adv_maker=0.5, hs=0.3,
               lag=0.10, s_u=0.8, hl_u=5.0, cl_load=1.0, w=0.15, off_sd=4.0),
    "LR": dict(kind="lighter", maker=0.0, taker=0.0, adv_taker=1.0, adv_maker=0.7, hs=0.5,
               lag=0.20, s_u=1.5, hl_u=10.0, cl_load=1.2, w=0.10, off_sd=6.0),
    "BG": dict(kind="cex", maker=1.0, taker=4.0, adv_taker=0.0, adv_maker=0.3, hs=0.3,
               lag=0.05, s_u=0.6, hl_u=3.0, cl_load=0.0, w=0.20, off_sd=5.0),
    "BY": dict(kind="cex", maker=1.0, taker=4.0, adv_taker=0.0, adv_maker=0.3, hs=0.2,
               lag=0.03, s_u=0.4, hl_u=3.0, cl_load=0.0, w=0.25, off_sd=3.0),
    "BN": dict(kind="data", maker=0.0, taker=0.0, adv_taker=0.0, adv_maker=0.0, hs=0.2,
               lag=0.0, s_u=0.3, hl_u=2.0, cl_load=0.0, w=0.30, off_sd=0.0),
}
HUB_KINDS = ("lighter",)

# rwa: None | "us" (เปิด จ.–ศ. 13:30–20:00 UTC) | "gold" (ปิด ศ. 21:00 – อา. 22:00 UTC)
ASSETS = {
    "BTC":  dict(P0=100_000.0, sig=(0.40, 1.00), rmult=1.0, l_imr=0.02, cex_mmr=0.005, rwa=None, cap=30, cex_h={"BG": 8, "BY": 8}, budget=0.25, b0={"LR": -2.2, "BG": -1.0}),
    "ETH":  dict(P0=3_500.0, sig=(0.55, 1.30), rmult=1.2, l_imr=0.02, cex_mmr=0.005, rwa=None, cap=30, cex_h={"BG": 8, "BY": 8}, budget=0.20, b0={"BG": -1.0}),
    "SOL":  dict(P0=180.0, sig=(0.65, 1.50), rmult=1.5, l_imr=0.02, cex_mmr=0.01, rwa=None, cap=100, cex_h={"BG": 8, "BY": 8}, budget=0.15, b0={"BG": -1.0}),
    "HYPE": dict(P0=40.0, sig=(0.80, 1.80), rmult=2.5, l_imr=0.05, cex_mmr=0.01, rwa=None, cap=100, cex_h={"BG": 4, "BY": 8}, budget=0.10, b0={"BG": -1.0}),
    "SPY":  dict(P0=680.0, sig=(0.15, 0.35), rmult=1.0, l_imr=0.02, cex_mmr=0.01, rwa="us", cap=100, cex_h={"BG": 8, "BY": 8}, budget=0.15, b0={"LR": 0.8, "BG": -1.0}),
    "QQQ":  dict(P0=600.0, sig=(0.20, 0.45), rmult=1.0, l_imr=0.0333, cex_mmr=0.01, rwa="us", cap=100, cex_h={"BG": 8, "BY": 8}, budget=0.10, b0={"LR": 3.4, "BG": -1.0}),
    "XAU":  dict(P0=4_000.0, sig=(0.14, 0.30), rmult=1.0, l_imr=0.04, cex_mmr=0.01, rwa="gold", cap=50, cex_h={"BG": 4, "BY": 8}, budget=0.15, b0={"BG": -1.0}),
}
CRYPTO = {"BTC", "ETH", "SOL", "HYPE"}
SWITCH_EXEMPT = {"BTC", "ETH"}            # CEX ไม่สลับเป็น funding รายชั่วโมงสำหรับสองตัวนี้


def corr_of(a, b):
    if a == b:
        return 1.0
    s = {a, b}
    if s <= CRYPTO:
        return 0.85 if s == {"BTC", "ETH"} else 0.70
    if s == {"SPY", "QQQ"}:
        return 0.93
    if "XAU" in s:
        return 0.10
    return 0.30


def mkt_closed(rwa, minute_of_week):
    """minute_of_week นับจากวันจันทร์ 00:00 UTC"""
    if rwa is None:
        return False
    day, mod = divmod(minute_of_week, 1440)
    if rwa == "us":
        return not (day < 5 and 13 * 60 + 30 <= mod < 20 * 60)
    if rwa == "gold":
        return (day == 4 and mod >= 21 * 60) or day == 5 or (day == 6 and mod < 22 * 60)
    return False


# ───────────────────────── ข้อมูลจำลอง ─────────────────────────

def _ar1(phi, inp):
    """y_t = phi*y_{t-1} + inp_t  (phi broadcast กับ inp[t])"""
    y = np.empty_like(inp)
    acc = np.zeros(inp.shape[1:])
    for t in range(inp.shape[0]):
        acc = phi * acc + inp[t]
        y[t] = acc
    return y


def synth(assets, venues, days=60, bar=60, seed=7, resid_scale=1.0, vol_share=0.25, shocks=False, lag_hl_s=1.0,
          resid_vol_elast=1.0):
    rng = np.random.default_rng(seed)
    T = int(days * 86400 // bar)
    A, K = len(assets), len(venues)
    mpb = bar / 60.0                      # นาทีต่อ bar
    bpy = 525600.0 / mpb

    # regime Markov: เงียบ ↔ ผันผวน (ค่าเฉลี่ย 6 วัน / 2 วัน ที่ vol_share=0.25; สัดส่วนช่วงผันผวนคงที่ = vol_share)
    vs = min(max(vol_share, 1e-3), 0.999)
    p01 = mpb / (6 * 1440) * (vs / 0.25)
    p10 = p01 * (1 - vs) / vs
    regime = np.zeros(T, dtype=np.int8)
    u01 = rng.random(T)
    for t in range(1, T):
        prev = regime[t - 1]
        regime[t] = (1 if u01[t] < p01 else 0) if prev == 0 else (0 if u01[t] < p10 else 1)
    # shock (stress): ราคาคริปโตวิ่งแรงใน 6 bar; บังคับ regime ผันผวน 60 bar หลังจากนั้น (สเปรดกว้าง, ADL ทำงาน)
    shock_list = []
    if shocks:
        for d_, mv in ((20, 0.12), (21, 0.08), (45, -0.20), (70, 0.15), (71, 0.10), (85, -0.15)):
            t0 = int(d_ * 86400 // bar)
            if t0 + 6 < T:
                shock_list.append((t0, mv))
                regime[t0:t0 + int(60 / mpb) + 6] = 1

    sig = np.array([[ASSETS[a]["sig"][0], ASSETS[a]["sig"][1]] for a in assets])     # (A,2)
    sig_t = sig[:, regime].T / math.sqrt(bpy)                                           # (T,A)
    g = sig[:, regime].T / sig[:, 0]                                                    # vol scaler
    # สมมติฐาน: residual ข้ามตลาดขยายตามความผันผวนยกกำลัง resid_vol_elast (1 = สัดส่วนตรง, 0 = ไม่ขยาย)
    # → "ช่วงผันผวนได้เยอะ" ในตัวจำลองมาจากสมมติฐานนี้โดยตรง ต้องวัดจากข้อมูลจริง
    gr = g ** resid_vol_elast

    C = np.array([[corr_of(a, b) for b in assets] for a in assets])
    L = np.linalg.cholesky(C)
    z = rng.standard_t(4, (T, A)) / math.sqrt(2.0)
    eps = z @ L.T
    minute = (np.arange(T) * mpb).astype(np.int64)
    mow = minute % (7 * 1440)
    closed = np.array([[mkt_closed(ASSETS[a]["rwa"], int(m)) for a in assets] for m in mow]) if any(
        ASSETS[a]["rwa"] for a in assets) else np.zeros((T, A), dtype=bool)
    r = sig_t * eps * np.where(closed, 0.5, 1.0)
    # jump ของคริปโต (~4 ครั้ง/ปี ขนาด t3 × 4%)
    for ai, a in enumerate(assets):
        if a in CRYPTO:
            nj = rng.poisson(4 * days / 365)
            for tj in rng.integers(1, T, nj):
                r[tj, ai] += 0.04 * rng.standard_t(3) / math.sqrt(3)
    # gap ตอนตลาดหุ้น/ทองเปิด
    for ai, a in enumerate(assets):
        if ASSETS[a]["rwa"]:
            opens = np.where(closed[:-1, ai] & ~closed[1:, ai])[0] + 1
            r[opens, ai] += rng.normal(0, 0.008, len(opens))
    for t0, mv in shock_list:
        for ai, a in enumerate(assets):
            if a in CRYPTO:
                r[t0:t0 + 6, ai] += mv / 6
    m = np.cumsum(r, axis=0) + np.log([ASSETS[a]["P0"] for a in assets])

    vp = [VENUES[v] for v in venues]
    phi_u = np.array([2 ** (-mpb / p["hl_u"]) for p in vp])                     # (K,)
    lag = np.array([p["lag"] for p in vp])
    s_u = np.array([p["s_u"] for p in vp]) * BP
    rmult = np.array([ASSETS[a]["rmult"] for a in assets])
    xi = rng.standard_t(4, (T, A, K)) / math.sqrt(2.0)
    # Lighter ตามราคาช้ากว่า CEX (lead-lag) แต่ไล่ทันภายใน ~1 วินาที (lag_hl_s): ที่ bar 1 นาทีแทบมองไม่เห็นในราคา
    # จึงไม่ใช่ edge ที่บัญชี Standard (หน่วง 300ms) เก็บได้ — โผล่เป็น "ต้นทุน catch-up" ตอน hedge แทน (ดู hub_px_at)
    phi_lag = 2 ** (-bar / max(lag_hl_s, 1e-9))
    inp = s_u[None, None, :] * rmult[None, :, None] * resid_scale * gr[:, :, None] \
        * np.sqrt(1 - phi_u ** 2)[None, None, :] * xi
    u = _ar1(phi_u[None, :], inp)
    if phi_lag > 1e-6:
        u += _ar1(phi_lag, -lag[None, None, :] * r[:, :, None] * np.ones((1, 1, K)))

    # factor ร่วมของ Lighter (LC/LR มี residual สัมพันธ์กัน)
    phi_c = 2 ** (-mpb / 20.0)
    cl = _ar1(phi_c, 1.0 * BP * resid_scale * gr * math.sqrt(1 - phi_c ** 2) * rng.normal(0, 1, (T, A)))
    cl_load = np.array([p["cl_load"] for p in vp])

    # basis ช้า: b0 + OU(HL 2 วัน, sd 1.5bp) + LR ขยับทุกวันศุกร์ 00:00 UTC (สัปดาห์ points)
    phi_b = 2 ** (-mpb / (2 * 1440))
    b = _ar1(phi_b, 1.5 * BP * math.sqrt(1 - phi_b ** 2) * rng.normal(0, 1, (T, A, K)))
    b0 = np.array([[ASSETS[a]["b0"].get(v, 0.0) * BP for v in venues] for a in assets])
    b += b0[None]
    if "LR" in venues:
        k = venues.index("LR")
        fri = np.where((mow == 4 * 1440) & (np.arange(T) > 0))[0]
        step = np.zeros((T, A))
        step[fri] = rng.normal(0, 2 * BP, (len(fri), A))
        b[:, :, k] += np.cumsum(step, axis=0)

    # ช่วงตลาดหุ้นปิด: ราคาแต่ละตลาดลอยแยกกัน แล้วหดกลับเร็ว (HL 3 นาที) หลังเปิด
    o = np.zeros((T, A, K))
    off_sd = np.array([p["off_sd"] for p in vp]) * BP * resid_scale
    if closed.any():
        dec = 2 ** (-mpb / 3.0)
        noise = rng.normal(0, 1, (T, A, K)) * off_sd * math.sqrt(mpb / 60.0)
        for t in range(1, T):
            cl_t = closed[t][:, None]
            o[t] = np.where(cl_t, o[t - 1] + noise[t] * gr[t][:, None], o[t - 1] * dec)

    # premium ร่วมของ perp (ขับ funding) + การรับ premium ไม่เท่ากันแต่ละตลาด
    phi_p = 2 ** (-mpb / 1440.0)
    pi = _ar1(phi_p, np.where(regime[:, None] == 1, 8.0, 2.0) * BP * math.sqrt(1 - phi_p ** 2)
              * rng.normal(0, 1, (T, A)))
    mload = np.clip(1 + 0.25 * rng.normal(0, 1, (A, K)), 0.3, 2.0)
    data_k = np.array([p["kind"] == "data" for p in vp])
    mload[:, data_k] = 1.0
    if "LR" in venues and "LC" in venues:
        mload[:, venues.index("LR")] = mload[:, venues.index("LC")] * (1 + 0.05 * rng.normal(0, 1, A))

    resid = b + u + cl[:, :, None] * cl_load + o + (mload[None] - 1.0) * pi[:, :, None]
    logmid = m[:, :, None] + pi[:, :, None] + resid
    mid = np.exp(logmid)
    hs = (np.array([p["hs"] for p in vp]) * BP)[None, None, :] * np.where(regime[:, None, None] == 1, 3.0, 1.0) \
        * np.where(closed[:, :, None], 3.0, 1.0)
    # premium ที่ใช้คิด funding: ช่วงตลาดปิด index ของแต่ละตลาดอิง EMA ราคาตัวเอง (Lighter IPM 30 นาที,
    # Bitget EMA ~20 นาที) → การลอยแยกกันช่วงปิด (o) ไม่กลายเป็น premium/funding
    prem = logmid - m[:, :, None] - o

    funding = synth_funding(assets, venues, prem, closed, bar, rng)
    return dict(mid=mid, hs=hs, funding=funding, r=r, regime=regime, closed=closed, bar=bar,
                assets=assets, venues=venues, minute=minute, shock_starts=[t0 for t0, _ in shock_list])


def synth_funding(assets, venues, prem, closed, bar, rng):
    """อัตราที่ long จ่าย settle ใน bar นั้น
    Lighter: ทุกชั่วโมง F8 = clip(μ·TW + clip(I − μ·TW, ±5bp), ±400bp), จ่าย F8/8
    CEX:     ทุก N ชม. F = clip((P̄ + clip(I − P̄, ±5bp))·N/8, ±cap); ชน cap → สลับเป็นรายชั่วโมง (ยกเว้น BTC/ETH)"""
    T, A, K = prem.shape
    mpb = bar / 60.0
    hour_bars = max(1, int(round(60 / mpb)))
    F = np.zeros((T, A, K))
    for ai, a in enumerate(assets):
        rwa = ASSETS[a]["rwa"] is not None
        for ki, v in enumerate(venues):
            kind = VENUES[v]["kind"]
            if kind == "data":
                continue
            if kind == "lighter":
                mu, I = (0.5, 0.32 * BP) if rwa else (1.0, 1.0 * BP)
                for t in range(hour_bars, T, hour_bars):
                    tw = prem[t - hour_bars:t, ai, ki].mean()
                    f8 = np.clip(mu * tw + np.clip(I - mu * tw, -5 * BP, 5 * BP), -0.04, 0.04)
                    F[t, ai, ki] = f8 / 8
            else:
                I = 0.0 if rwa else 1.0 * BP
                cap = ASSETS[a]["cap"] * BP
                N = ASSETS[a]["cex_h"].get(v, 8)
                last = 0
                t = N * hour_bars
                while t < T:
                    pw = prem[last:t, ai, ki].mean()
                    f = float(np.clip((pw + np.clip(I - pw, -5 * BP, 5 * BP)) * N / 8, -cap, cap))
                    F[t, ai, ki] = f
                    last = t
                    if abs(f) >= cap - 1e-12 and a not in SWITCH_EXEMPT:
                        N = 1
                    elif N == 1 and abs(f) < cap / 2 and rng.random() < 1 / 48:
                        N = 4
                    t += N * hour_bars
    return F


def load_csv(path, data_only, bar):
    rows = defaultdict(dict)
    assets, venues, ts_set = [], [], set()
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            ts = int(float(row["ts"]))
            a, v = row["asset"], row["venue"]
            if a not in assets:
                assets.append(a)
            if v not in venues:
                venues.append(v)
            ts_set.add(ts)
            rows[ts][(a, v)] = row
    for v in venues:
        if v not in VENUES:
            VENUES[v] = dict(VENUES["BN" if v in data_only else "BG"])
        if v in data_only:
            VENUES[v] = dict(VENUES[v], kind="data")
    for a in assets:
        if a not in ASSETS:
            ASSETS[a] = dict(ASSETS["SOL"], b0={})
    ts_list = sorted(ts_set)
    T, A, K = len(ts_list), len(assets), len(venues)
    if T > 1:
        step = int(np.median(np.diff(ts_list)))
        if step != bar:
            print(f"คำเตือน: ระยะห่าง ts ในไฟล์ = {step} วินาที แต่ --bar = {bar}; ใช้ {step} "
                  f"(แนะนำ resample เป็น bar 60 วินาทีก่อน — ข้อมูลรายวินาทีหลายสัปดาห์จะช้ามาก)", file=sys.stderr)
            bar = step
    mid = np.full((T, A, K), np.nan)
    hs = np.full((T, A, K), np.nan)
    fund = np.zeros((T, A, K))
    closed = np.zeros((T, A), dtype=bool)
    for t, ts in enumerate(ts_list):
        for (a, v), row in rows[ts].items():
            ai, ki = assets.index(a), venues.index(v)
            bid, ask = float(row["bid"]), float(row["ask"])
            mid[t, ai, ki] = (bid + ask) / 2
            hs[t, ai, ki] = (ask - bid) / (ask + bid)
            fund[t, ai, ki] = float(row.get("funding") or 0.0)
            if row.get("mkt_open") not in (None, ""):
                closed[t, ai] = row["mkt_open"] in ("0", "false", "False")
    # forward-fill ราคา (ใช้ mark-to-market ต่อเนื่อง); ขาดเกิน 5 bar ติด = stale → ห้ามใช้ทำสัญญาณ/ส่งคำสั่ง
    for t in range(1, T):
        gap = np.isnan(mid[t])
        if gap.any():
            src = mid[t - 1]
            mid[t] = np.where(gap, src, mid[t])
            hs[t] = np.where(gap, hs[t - 1], hs[t])
    stale = np.zeros((T, A, K), dtype=bool)
    run = np.zeros((A, K))
    raw_missing = np.array([[[ (a, v) not in rows[ts] for v in venues] for a in assets] for ts in ts_list])
    for t in range(T):
        run = np.where(raw_missing[t], run + 1, 0)
        stale[t] = run > 5
    lm = np.log(mid)
    cons = np.nanmean(lm, axis=2)
    r = np.vstack([np.zeros((1, A)), np.diff(cons, axis=0)])
    r = np.nan_to_num(r)
    # regime (ใช้แค่แยกผลช่วงเงียบ/ผันผวน และ ADL): ผลรวม |r| 6 ชม. ย้อนหลัง > quantile 75% ของอดีต (causal)
    w = max(1, int(6 * 3600 // bar))
    roll = np.array([np.convolve(np.abs(r[:, i]), np.ones(w), "full")[:T] for i in range(A)]).T.mean(axis=1)
    regime = np.zeros(T, dtype=np.int8)
    hb = max(1, int(3600 // bar))
    q = np.inf
    for t in range(T):
        if t >= w and t % hb == 0:
            q = np.quantile(roll[w:t + 1], 0.75)
        regime[t] = roll[t] > q
    # นาทีนับจากวันจันทร์ 00:00 UTC (unix epoch = วันพฤหัส) — run() ใช้ % 10080 หาเวลาในสัปดาห์
    minute = (np.array(ts_list, dtype=np.int64) // 60 + 3 * 1440).astype(np.int64)
    return dict(mid=mid, hs=hs, funding=fund, r=r, regime=regime, closed=closed, bar=bar,
                assets=assets, venues=venues, minute=minute, stale=stale)


# ───────────────────────── เครื่องยนต์กลยุทธ์ ─────────────────────────

DEFAULTS = dict(capital=100_000.0, lev=3.0, lalert=4.0, lxfer=5.0, rho=0.5, cex_maker=None, cex_taker=None,
                lighter_adv=None, catchup=1.0, p_touch=0.3, p_leg_fail=0.02, z_in=(2.0, 2.75, 3.5), z_out=0.3,
                kappa=1.25, max_per_pair=3, max_per_asset=6, opens_per_bar=2, H_b_h=24.0, H_v_h=4.0,
                pairs_only=None, allow_cex_cex=False, funding_on=True, liq_pen=0.005, p_adl=0.05,
                outage_rate=1.0, freeze=None, no_transfers=False, alloc=None, warmup_h=24.0, seed=7,
                dir_cap=None, close_ttl=10, no_trade=False, trade_venues=None, unit_usd=None, no_hub_pair=False,
                static_load=0.0, shock_outage=True, derisk=True)


class Layer:
    __slots__ = ("a", "i", "j", "q", "t0", "closing", "tries", "dead", "cash", "kind", "booked")

    def __init__(self, a, i, j, q, t0, kind=""):
        self.a, self.i, self.j, self.q, self.t0 = a, i, j, q, t0   # short q หน่วยที่ i, long q ที่ j
        self.closing, self.tries, self.dead = None, 0, False
        self.cash, self.kind, self.booked = 0.0, kind, False      # กระแสเงินสดจากการซื้อขายของชั้นนี้


def default_alloc(venues):
    tr = [v for v in venues if VENUES[v]["kind"] != "data"]
    hubs = [v for v in tr if VENUES[v]["kind"] in HUB_KINDS]
    spokes = [v for v in tr if v not in hubs]
    if not hubs or not spokes:
        return {v: 1 / len(tr) for v in tr}
    out = {}
    hs = {"LC": 0.7, "LR": 0.3}
    tot = sum(hs.get(h, 0.5) for h in hubs)
    hub_share = 0.5 if len(spokes) >= 2 else 0.6 if len(hubs) >= 2 else 0.5
    for h in hubs:
        out[h] = hub_share * hs.get(h, 0.5) / tot
    for s in spokes:
        out[s] = (1 - hub_share) / len(spokes)
    return out


def run(d, **kw):
    P = dict(DEFAULTS)
    P.update({k: v for k, v in kw.items() if v is not None})
    rng = np.random.default_rng(P["seed"] + 1000)
    assets, venues = d["assets"], d["venues"]
    A, K = len(assets), len(venues)
    mid, hsd, fund, r, regime, closed = d["mid"], d["hs"], d["funding"], d["r"], d["regime"], d["closed"]
    stale = d.get("stale")
    T = mid.shape[0]
    bar = d["bar"]
    mpb = bar / 60.0
    bars_h = 60.0 / mpb
    bpy = 525600.0 / mpb

    vp = []
    for v in venues:
        p = dict(VENUES[v])
        if p["kind"] == "cex":
            if P["cex_maker"] is not None:
                p["maker"] = P["cex_maker"]
            if P["cex_taker"] is not None:
                p["taker"] = P["cex_taker"]
        if p["kind"] == "lighter" and P["lighter_adv"] is not None:
            p["adv_taker"] = P["lighter_adv"] * (1.0 if v != "LR" else 1.4)
            p["adv_maker"] = P["lighter_adv"] * 0.7
        vp.append(p)
    kind = [p["kind"] for p in vp]
    trade_k = np.array([k != "data" for k in kind])
    is_hub = np.array([k in HUB_KINDS for k in kind])
    is_cex = np.array([k == "cex" for k in kind])

    # ประเภทคู่ที่อนุญาต + บทบาท (maker ที่ไหน / taker ที่ไหน)
    allowed = np.zeros((K, K), dtype=bool)
    maker_of = -np.ones((K, K), dtype=int)
    for i in range(K):
        for j in range(K):
            if i == j or not trade_k[i] or not trade_k[j]:
                continue
            if is_cex[i] != is_cex[j]:                       # CEX–Lighter: maker ที่ CEX
                allowed[i, j] = True
                maker_of[i, j] = i if is_cex[i] else j
            elif is_hub[i] and is_hub[j] and not P["no_hub_pair"]:   # LC–LR: maker ที่ LR (book บางกว่า)
                allowed[i, j] = True
                maker_of[i, j] = i if venues[i] == "LR" else j if venues[j] == "LR" else i
            elif is_cex[i] and is_cex[j] and (P["allow_cex_cex"] or max(vp[i]["maker"], vp[j]["maker"]) <= 0):
                allowed[i, j] = True
                maker_of[i, j] = i if vp[i]["maker"] <= vp[j]["maker"] else j
    if P["trade_venues"]:
        trade_k = np.array([trade_k[k] and venues[k] in P["trade_venues"] for k in range(K)])
        allowed &= trade_k[:, None] & trade_k[None, :]
    if P["pairs_only"]:
        x, y = P["pairs_only"].split("-")
        xi, yi = venues.index(x), venues.index(y)
        keep = np.zeros_like(allowed)
        keep[xi, yi] = keep[yi, xi] = True
        if maker_of[xi, yi] < 0:
            maker_of[xi, yi] = maker_of[yi, xi] = xi if is_cex[xi] else yi
        allowed = keep
        trade_k = np.array([k in (xi, yi) for k in range(K)])

    def c_maker(k):
        return vp[k]["maker"] + vp[k]["adv_maker"]

    def c_taker(k):
        return vp[k]["taker"] + vp[k]["hs"] + vp[k]["adv_taker"]

    RT = np.zeros((K, K))
    for i in range(K):
        for j in range(K):
            if allowed[i, j]:
                mk = maker_of[i, j]
                tk = j if mk == i else i
                RT[i, j] = 2 * (c_maker(mk) + c_taker(tk))

    hs_static = np.array([p["hs"] for p in vp])
    lag_k = np.array([p["lag"] if p["kind"] in HUB_KINDS else 0.0 for p in vp])
    taker_is_j = np.zeros((K, K), dtype=bool)                 # True ถ้าขา taker ของคู่ (i,j) คือ j
    for i in range(K):
        for j in range(K):
            if allowed[i, j]:
                taker_is_j[i, j] = maker_of[i, j] == i

    # ทุนและงบ
    alloc = P["alloc"] or default_alloc([v for k, v in enumerate(venues) if trade_k[k]])
    E0 = np.array([P["capital"] * alloc.get(v, 0.0) for v in venues])
    E = E0.copy()
    budget = np.array([ASSETS[a]["budget"] for a in assets])
    budget = budget / budget.sum()
    Q = P["lev"] * E0[None, :] * budget[:, None]                              # เพดาน notional ต่อ (asset, venue)
    # ขนาดชั้นคงที่ไม่ขึ้นกับการแบ่งทุน (= ขนาดชั้นของชุด 4 ตลาด: lev·ทุน·งบ/12) → เทียบชุดตลาดได้อย่างยุติธรรม
    if P["unit_usd"] is not None:
        unit_usd = np.asarray(P["unit_usd"], float)
    else:
        unit_usd = P["lev"] * P["capital"] * budget / 12.0
    dir_cap = P["dir_cap"] if P["dir_cap"] is not None else 2.0 * P["lev"] / 3.0
    blk = np.array([0 if a in CRYPTO else 1 if ASSETS[a]["rwa"] == "us" else 2 for a in assets])
    kill_th = np.array([0.01 if a in ("BTC", "ETH") else 0.02 for a in assets])

    imr = np.zeros((A, K))
    mmr = np.zeros((A, K))
    for ai, a in enumerate(assets):
        for k in range(K):
            if kind[k] == "lighter":
                imr[ai, k] = ASSETS[a]["l_imr"]
                mmr[ai, k] = 0.6 * ASSETS[a]["l_imr"]
            elif kind[k] == "cex":
                mmr[ai, k] = ASSETS[a]["cex_mmr"]
                imr[ai, k] = 2 * ASSETS[a]["cex_mmr"]

    # สถานะ
    n = np.zeros((A, K))
    layers = []
    pending = []                         # คำสั่งจาก bar ก่อน
    transfers_inflight = []              # (t_arrive, k, amt)
    outage_until = np.zeros(K, dtype=int)
    freeze = None
    if P["freeze"]:
        fv, fdays = P["freeze"].split(":")
        if fv in venues:
            t0f = int(rng.integers(int(P["warmup_h"] * bars_h), max(int(P["warmup_h"] * bars_h) + 1, T - 1)))
            freeze = (venues.index(fv), t0f, t0f + int(float(fdays) * 24 * bars_h))
    out_rate = P["outage_rate"] * np.array([3.0 if kind[k] == "lighter" else 2.0 if kind[k] == "cex" else 0 for k in range(K)])
    out_p = out_rate / bpy

    # สัญญาณ
    a_b = 1 - 2 ** (-1 / (P["H_b_h"] * bars_h))
    a_v = 1 - 2 ** (-1 / (P["H_v_h"] * bars_h))
    a_ar = 1 - 2 ** (-1 / (24 * bars_h))
    w_cons = np.array([p["w"] for p in vp])
    lm = np.log(mid)
    bhat = np.zeros((A, K))
    V = np.tile(np.eye(K) * (1 * BP) ** 2, (2, A, 1, 1))                  # [on/off-hours] × A × K × K
    s_prev = np.zeros((A, K, K))
    Sxx = np.full((A, K, K), (1 * BP) ** 2)
    Sxy = np.full((A, K, K), 0.5 * (1 * BP) ** 2)
    z_prev = np.zeros((A, K, K))
    fh = np.zeros((A, K))                 # funding ล่าสุดต่อชั่วโมง (long จ่าย)
    interval_h = np.array([[8.0 if is_cex[k] else 1.0 for k in range(K)] for _ in range(A)])
    last_settle = np.zeros((A, K), dtype=int)

    # บัญชี
    acc = defaultdict(float)
    eq_curve = np.empty(T)
    regime_pnl = np.zeros(2)
    regime_bars = np.zeros(2)
    stats = defaultdict(float)
    minEr = np.ones(K)
    maxlev = np.zeros(K)
    maxdir = np.zeros(K)
    max_unhedged = 0.0
    legcount_hist = []
    warm = int(P["warmup_h"] * bars_h)
    calib = defaultdict(list) if P["no_trade"] else None
    prev_total = E.sum()
    # σ ต่อ bar แบบ causal: EWMA ของ r² (HL 1 ชม.) — ไม่ใช้ σ จริงของตัวสร้างข้อมูล/ทั้งไฟล์
    a_s = 1 - 2 ** (-1 / max(bars_h, 1.0))
    m_sig = np.empty_like(r)
    acc_s = np.mean(r[1:int(bars_h) + 1] ** 2, axis=0) + 1e-18
    for t_ in range(T):
        acc_s = (1 - a_s) * acc_s + a_s * r[t_] ** 2
        m_sig[t_] = np.sqrt(acc_s)
    qbuf = math.sqrt(0.3 / bar)                 # กันชน adverse ~ σ ใน 300ms
    shock_starts = set(d.get("shock_starts", []))
    static_layers = []
    sum_lev = np.zeros(K)
    bars_pos = 0
    nbar_live = 0

    def trade(ai, k, dq, price, fee_bps, t, L=None):
        """ซื้อ (dq>0)/ขาย dq หน่วยที่ราคา price ณ bar t: ต้นทุน = dq·(price−mid) + fee"""
        mid_t = mid[t, ai, k]
        if L is not None:
            L.cash += -dq * price - abs(dq) * price * fee_bps * BP
        slip = dq * (price - mid_t)
        fee = abs(dq) * price * fee_bps * BP
        by_asset[assets[ai]] -= slip + fee
        E[k] -= slip + fee
        acc["slippage"] -= slip
        acc["fees"] -= fee
        acc[f"fees_{venues[k]}"] -= fee
        n[ai, k] += dq
        stats["turnover"] += abs(dq) * mid_t
        stats[f"turn_{venues[k]}"] += abs(dq) * mid_t

    def taker_px(ai, k, side, t, extra_bp=0.0):
        p = vp[k]
        bump = (hsd[t, ai, k] / 1.0 + (p["adv_taker"] + extra_bp) * BP)
        if is_hub[k]:
            bump += P["catchup"] * p["lag"] * abs(r[t, ai])
        return mid[t, ai, k] * (1 + side * bump)

    def maker_fill(ai, k, side, limit, t):
        """side=+1 ซื้อ, −1 ขาย ที่ราคา limit; คืน None ถ้าไม่ fill หรือ (frac, Δ) =
        สัดส่วนของ bar ที่ราคาวิ่งมาชน limit และ log-move ของตลาดนั้นจนถึงจุดชน — ใช้กำหนดราคา hedge
        ณ "ตอนที่ fill" แทนราคาปลาย bar (ไม่งั้น bar 1 นาทีจะทำให้ hedge ช้ากว่าความจริงหลายร้อยเท่า)"""
        hs_ = hsd[t, ai, k]
        m0, m1 = mid[t - 1, ai, k], mid[t, ai, k]
        bid, ask = m1 * (1 - hs_), m1 * (1 + hs_)
        if side < 0:
            if bid >= limit:
                cross = limit / (1 - hs_)
            elif ask >= limit and rng.random() < P["p_touch"]:
                cross = m1
            else:
                return None
        else:
            if ask <= limit:
                cross = limit / (1 + hs_)
            elif bid <= limit and rng.random() < P["p_touch"]:
                cross = m1
            else:
                return None
        tot = math.log(m1 / m0)
        dlt = math.log(cross / m0)
        frac = 1.0 if abs(tot) < 1e-12 else min(max(dlt / tot, 0.0), 1.0)
        return frac, dlt

    def hub_px_at(ai, k, side, t, fill, extra_bp=0.0):
        """ราคา IOC ที่ hub ณ จุดที่ spoke ถูก fill: interpolate ราคา hub ภายใน bar ตามสัดส่วน frac
        แล้วบวก catch-up (Lighter ตามราคาทันก่อน IOC 300ms ถึง) + ครึ่งสเปรด + adverse"""
        frac, dlt = fill
        m0, m1 = mid[t - 1, ai, k], mid[t, ai, k]
        base = m0 * (m1 / m0) ** frac
        p = vp[k]
        bump = hsd[t, ai, k] + (p["adv_taker"] + extra_bp) * BP
        if is_hub[k]:
            bump += P["catchup"] * p["lag"] * abs(dlt)
        return base * (1 + side * bump)

    def avail(k, t, ai=None):
        if ai is not None and stale is not None and stale[t, ai, k]:
            return False
        return trade_k[k] and outage_until[k] <= t

    def hedge_leg(ai, hub, side, q, t, spoke, fill, Lc):
        """ส่ง IOC ที่ hub; ถ้าพลาด ใช้บันได: hub อีกตัว → CEX อีกตัว (taker) → None (ให้ปิดขา spoke)"""
        if rng.random() >= P["p_leg_fail"] and avail(hub, t):
            trade(ai, hub, side * q, hub_px_at(ai, hub, side, t, fill), vp[hub]["taker"], t, Lc)
            return hub
        stats["leg_fail"] += 1
        for k in range(K):
            if k not in (hub, spoke) and is_hub[k] and avail(k, t):
                trade(ai, k, side * q, taker_px(ai, k, side, t, 1.0), vp[k]["taker"], t, Lc)
                return k
        for k in range(K):
            if k not in (hub, spoke) and is_cex[k] and avail(k, t):
                trade(ai, k, side * q, taker_px(ai, k, side, t, 0.5), vp[k]["taker"], t, Lc)
                return k
        return None

    def close_layer_taker(L, t):
        ai = L.a
        if L.i is not None and avail(L.i, t, ai):
            trade(ai, L.i, +L.q, taker_px(ai, L.i, +1, t), vp[L.i]["taker"], t, L)
            L.i = None
        if L.j is not None and avail(L.j, t, ai):
            trade(ai, L.j, -L.q, taker_px(ai, L.j, -1, t), vp[L.j]["taker"], t, L)
            L.j = None
        if L.i is None and L.j is None:
            L.dead = True

    def forced_reduce(ai, k, frac, px_bump, pen, t, why, sign=None):
        """ตลาด k ถูกบังคับปิดสถานะ asset ai ตามสัดส่วน frac (liquidation/ADL): ขาที่เหลือกลายเป็น orphan
        sign: ปิดเฉพาะขาทิศนั้น (+1 long / −1 short) เช่น ADL ตัดเฉพาะฝั่งที่กำไร; ตัดทีละชั้นทั้งชั้น"""
        target = abs(n[ai, k]) * frac
        done = 0.0
        for L in layers:
            if L.dead or L.a != ai or done >= target - 1e-12:
                continue
            for leg in ("i", "j"):
                if done >= target - 1e-12:
                    break
                if sign is not None and sign != (-1 if leg == "i" else +1):
                    continue
                if getattr(L, leg) == k:
                    side = +1 if leg == "i" else -1          # ปิด short = ซื้อ, ปิด long = ขาย
                    px = mid[t, ai, k] * (1 + side * px_bump)
                    q = L.q
                    trade(ai, k, side * q, px, 0.0, t, L)
                    E[k] -= pen * q * mid[t, ai, k]
                    acc["liq_penalty"] -= pen * q * mid[t, ai, k]
                    setattr(L, leg, None)
                    L.closing = "orphan"
                    done += q
        stats[why] += 1

    pair_kind = {}
    for i in range(K):
        for j in range(i + 1, K):
            if allowed[i, j]:
                pair_kind[(i, j)] = "LC-LR" if (is_hub[i] and is_hub[j]) else "CEX-CEX" if (is_cex[i] and is_cex[j]) else "CEX-Lighter"
    sig_samples = defaultdict(list)
    by_kind = defaultdict(float)
    by_asset = defaultdict(float)

    def book(L):
        if not L.booked:
            by_kind[L.kind] += L.cash
            L.booked = True

    def has_pos(ai, k, t):
        return abs(n[ai, k]) * np.nan_to_num(mid[t, ai, k]) > 1.0

    def margin_check(k, t):
        if not trade_k[k] or outage_until[k] > t:
            return
        G = np.abs(n[:, k]) * mid[t, :, k]
        MR = (G * mmr[:, k]).sum()
        if MR <= 0:
            return
        if kind[k] == "lighter":
            CR = MR * 2 / 3
            if E[k] < CR:
                for ai in range(A):
                    if has_pos(ai, k, t):
                        forced_reduce(ai, k, 1.0, 0.0, 0.0, t, "liq_full")
                acc["liq_penalty"] -= E[k]                  # LLP รับทั้งบัญชี (ส่วนที่ติดลบ LLP รับไป)
                E[k] = 0.0
                return
            guard = 0
            while E[k] < MR and guard <= A:
                guard += 1
                Gk = np.abs(n[:, k]) * mid[t, :, k]
                if Gk.max() <= 0:
                    break
                ai = int(np.argmax(Gk))
                forced_reduce(ai, k, 1.0, hsd[t, ai, k] + 5 * BP, P["liq_pen"], t, "liq_partial")
                MR = (np.abs(n[:, k]) * mid[t, :, k] * mmr[:, k]).sum()
        else:
            if E[k] < MR:
                Gt = G.sum()
                for ai in range(A):
                    if has_pos(ai, k, t):
                        forced_reduce(ai, k, 1.0, hsd[t, ai, k], 0.0, t, "liq_cex")
                pen = min(E[k], 0.005 * Gt) if E[k] > 0 else 0.0
                E[k] -= pen
                acc["liq_penalty"] -= pen
                if E[k] < 0:                                 # insurance fund รับส่วนติดลบ
                    acc["liq_penalty"] -= E[k]
                    E[k] = 0.0

    for t in range(T):
        # 1) mark-to-market
        if t > 0:
            dP = np.nan_to_num(mid[t] - mid[t - 1])
            g = (n * dP).sum(axis=0)
            for ai_, v_ in enumerate((n * dP).sum(axis=1)):
                by_asset[assets[ai_]] += v_
            E += g
            acc["price"] += g.sum()
        # 2) funding (long จ่าย)
        if P["funding_on"]:
            ft = fund[t]
            if ft.any():
                pay = -(n * mid[t] * ft)
                for ai_, v_ in enumerate(np.nan_to_num(pay).sum(axis=1)):
                    by_asset[assets[ai_]] += v_
                E += np.nan_to_num(pay.sum(axis=0))
                acc["funding"] += np.nan_to_num(pay).sum()
                nz = ft != 0
                hrs = np.maximum((t - last_settle) / bars_h, 1.0)
                fh = np.where(nz, ft / np.where(is_cex[None, :], hrs, 1.0), fh)
                last_settle = np.where(nz, t, last_settle)
        # 3) outage และเงินโอนที่มาถึง (shock → Lighter ล่มแบบ 10 ต.ค. 2025 ถ้าเปิด shock_outage)
        if t in shock_starts and P["shock_outage"]:
            for k in range(K):
                if kind[k] == "lighter" and trade_k[k]:
                    outage_until[k] = max(outage_until[k], t + int(rng.lognormal(math.log(120), 0.7) / mpb) + 1)
                    stats["outages"] += 1
        for k in range(K):
            if trade_k[k] and outage_until[k] <= t and rng.random() < out_p[k]:
                dur = int(min(12 * 60, math.exp(math.log(60) + rng.normal())) / mpb) + 1
                outage_until[k] = t + dur
                stats["outages"] += 1
        if transfers_inflight:
            keep = []
            for (ta, k, amt) in transfers_inflight:
                if ta <= t:
                    E[k] += amt
                else:
                    keep.append((ta, k, amt))
            transfers_inflight = keep
        # 4) ส่งคำสั่งที่ค้างจาก bar ก่อน
        new_pending = []
        for od in pending:
            L = od["layer"]
            ai = L.a
            if od["type"] == "open":
                mk, tk = od["maker"], od["taker"]
                side_mk = -1 if mk == L.i else +1                 # i = ขา short
                if not (avail(mk, t, ai) and avail(tk, t, ai)):
                    L.dead = True
                    continue
                fill = maker_fill(ai, mk, side_mk, od["limit"], t)
                if fill is not None:
                    trade(ai, mk, side_mk * L.q, od["limit"], vp[mk]["maker"], t, L)
                    used = hedge_leg(ai, tk, -side_mk, L.q, t, mk, fill, L)
                    if used is None:
                        trade(ai, mk, -side_mk * L.q, mid[t, ai, mk] * (1 - side_mk * hsd[t, ai, mk]), vp[mk]["taker"], t, L)
                        L.dead = True
                        book(L)
                        continue
                    if tk == L.i:
                        L.i = used
                    else:
                        L.j = used
                    layers.append(L)
                else:
                    L.dead = True
            elif od["type"] == "close":
                if L.dead:
                    continue
                if od["mode"] == "taker" or L.closing == "orphan":
                    close_layer_taker(L, t)
                    if not L.dead:
                        new_pending.append(od)
                    continue
                mk = maker_of[L.i, L.j] if (L.i is not None and L.j is not None) else None
                if mk is None or mk < 0:
                    close_layer_taker(L, t)
                    if not L.dead:                                 # ขาที่ปิดไม่ได้ (ตลาดล่ม) → ค้างคิวไว้จนปิดครบ
                        L.closing, od["mode"] = "taker", "taker"
                        new_pending.append(od)
                    continue
                tk = L.j if mk == L.i else L.i
                side_mk = +1 if mk == L.i else -1               # ปิด short = ซื้อ
                if not (avail(mk, t) and avail(tk, t)):
                    L.closing = None
                    continue
                fill = maker_fill(ai, mk, side_mk, od["limit"], t)
                if fill is not None:
                    trade(ai, mk, side_mk * L.q, od["limit"], vp[mk]["maker"], t, L)
                    trade(ai, tk, -side_mk * L.q, hub_px_at(ai, tk, -side_mk, t, fill), vp[tk]["taker"], t, L)
                    L.dead = True
                else:
                    L.closing = None                               # ลองใหม่ใน bar ถัดไป
                    L.tries += 1
        pending = new_pending
        # orphan (อีกขาโดนบังคับปิด) → ปิดขาที่เหลือด้วย taker ใน bar นี้
        for L in layers:
            if not L.dead and L.closing == "orphan":
                close_layer_taker(L, t)
        for L in layers:
            if L.dead:
                book(L)
        layers = [L for L in layers if not L.dead]

        # 5) margin / ADL
        for k in range(K):
            margin_check(k, t)
        if P["p_adl"] > 0 and regime[t] == 1:
            for ai in range(A):
                if abs(r[t, ai]) > 4 * m_sig[t, ai]:
                    for k in range(K):
                        if is_cex[k] and avail(k, t) and has_pos(ai, k, t) and np.sign(n[ai, k]) == np.sign(r[t, ai]) \
                                and rng.random() < P["p_adl"]:
                            forced_reduce(ai, k, 0.5, 0.0, 0.0, t, "adl", sign=int(np.sign(n[ai, k])))
        for L in layers:
            if not L.dead and L.closing == "orphan":
                stats["orphan_bars"] += 1
        # hedge quality (ก่อนซ่อม): |Σ_k n|·P / gross
        gross_a = (np.abs(n) * np.nan_to_num(mid[t])).sum(axis=1)
        net_units = np.abs(n.sum(axis=1)) * np.nanmean(mid[t], axis=1)
        if gross_a.max() > 0:
            max_unhedged = max(max_unhedged, float((net_units / np.maximum(gross_a, 1e-9)).max()))

        # 6) โยกเงินรายชั่วโมง
        Gk = (np.abs(n) * np.nan_to_num(mid[t])).sum(axis=0)
        if not P["no_transfers"] and t % max(1, int(bars_h)) == 0:
            for k in range(K):
                if not trade_k[k] or outage_until[k] > t:
                    continue
                if freeze and freeze[0] == k and freeze[1] <= t < freeze[2]:
                    continue
                need = E[k] < P["rho"] * E0[k] or (Gk[k] > 0 and Gk[k] > P["lxfer"] * max(E[k], 1e-9))
                if not need:
                    continue
                amt = max(E0[k] - E[k], Gk[k] / P["lev"] - E[k])
                surplus = [(E[j] - E0[j], j) for j in range(K) if j != k and trade_k[j] and outage_until[j] <= t
                           and not (freeze and freeze[0] == j and freeze[1] <= t < freeze[2])]
                if not surplus:
                    continue
                sur, src = max(surplus)
                amt = min(amt, sur)
                if amt <= 0:
                    continue
                E[src] -= amt + 1.0
                acc["transfer_cost"] -= 1.0
                if is_hub[src] and is_hub[k]:
                    delay = 240
                elif is_cex[src] and is_cex[k]:
                    delay = 10
                else:
                    delay = 30
                transfers_inflight.append((t + int(delay / mpb), k, amt))
                stats["transfers"] += 1
                stats["usd_transferred"] += amt

        # ── สถิติ per-venue ──
        live = trade_k & (E0 > 0)
        lev_now = np.where(live, Gk / np.maximum(E, 1e-9), 0)
        maxlev = np.maximum(maxlev, np.where(E > 0, lev_now, 99))
        minEr = np.minimum(minEr, np.where(live, E / np.maximum(E0, 1e-9), 1))
        cnt = (np.abs(n) * np.nan_to_num(mid[t]) > 1.0).sum(axis=1)
        legcount_hist.append(cnt)
        if t >= warm:
            nbar_live += 1
            sum_lev += lev_now
            bars_pos += int(cnt.max() > 0)
        DB = np.zeros((3, K))
        for b_ in range(3):
            sel_ = blk == b_
            if sel_.any():
                DB[b_] = (n[sel_] * np.nan_to_num(mid[t][sel_])).sum(axis=0)
        maxdir = np.maximum(maxdir, np.where(live & (E > 0), np.abs(DB).max(axis=0) / np.maximum(E, 1e-9), 0))

        # 7) สัญญาณ
        lmt = lm[t]
        ok = ~np.isnan(lmt)
        if stale is not None:
            ok &= ~stale[t]
        ok &= (outage_until <= t)[None, :] | ~trade_k[None, :]
        x = np.where(ok, lmt - bhat, np.nan)
        wv = np.where(ok, w_cons[None, :], 0.0)
        c = np.nansum(np.nan_to_num(x) * wv, axis=1) / np.maximum(wv.sum(axis=1), 1e-12)
        if t == 0:
            bhat = np.where(ok, lmt - c[:, None], 0.0)
            x = np.where(ok, lmt - bhat, np.nan)
        e = np.nan_to_num(x - c[:, None])
        mow = int(d["minute"][t]) % (7 * 1440)
        ab = np.full((A, K), a_b)
        if 4 * 1440 <= mow < 4 * 1440 + 360:                                 # สัปดาห์ points ของ LR เปลี่ยน
            for k in range(K):
                if is_hub[k]:
                    ab[:, k] = 1 - 2 ** (-1 / (2 * bars_h))
        cl_t = closed[t]
        ab[cl_t, :] = 0.0                                                      # ตลาดหุ้นปิด: แช่ basis
        bhat = np.where(ok, bhat + ab * (lmt - c[:, None] - bhat), bhat)
        st = cl_t.astype(int)
        outer = e[:, :, None] * e[:, None, :]
        pair_ok = ok[:, :, None] & ok[:, None, :]
        for s_ in (0, 1):
            sel = st == s_
            if sel.any():
                V[s_, sel] = np.where(pair_ok[sel], (1 - a_v) * V[s_, sel] + a_v * outer[sel], V[s_, sel])
        Vt = V[st, np.arange(A)]
        dg = np.diagonal(Vt, axis1=1, axis2=2)
        sig_pair = np.sqrt(np.maximum(dg[:, :, None] + dg[:, None, :] - 2 * Vt, (0.3 * BP) ** 2))
        s = e[:, :, None] - e[:, None, :]                                    # s[a,i,j] = e_i − e_j (>0: i แพง)
        Sxx = np.where(pair_ok, (1 - a_ar) * Sxx + a_ar * s_prev * s_prev, Sxx)
        Sxy = np.where(pair_ok, (1 - a_ar) * Sxy + a_ar * s * s_prev, Sxy)
        s_prev = np.where(pair_ok, s, s_prev)
        phi = np.clip(Sxy / np.maximum(Sxx, 1e-18), 1e-6, 0.999999)
        hl_bars = math.log(2) / -np.log(phi)
        z = s / sig_pair
        # gate เข้าเทรด (ใช้ร่วมกันทั้ง engine และ --calibrate)
        carry = np.zeros((A, K, K))
        if P["funding_on"]:
            hold_h = np.minimum(2 * hl_bars / bars_h, 4.0)
            carry = (fh[:, :, None] - fh[:, None, :]) * hold_h                # short i ได้ fh_i, long j จ่าย fh_j
        edge = (s - P["z_out"] * sig_pair + carry) / BP
        # ต้นทุนไป-กลับแบบ dynamic: ครึ่งสเปรดตอนนี้ + catch-up ที่คาด (λ·E|r|) ของขา taker
        tk_extra = (hsd[t] / BP - hs_static[None, :]) + P["catchup"] * lag_k[None, :] * m_sig[t][:, None] * 0.8 / BP
        RTt = RT[None] + 2 * np.where(taker_is_j[None], tk_extra[:, None, :], tk_extra[:, :, None])
        zin = P["z_in"]
        gate_mask = allowed[None] & pair_ok & (z >= zin[0]) & (z_prev >= zin[0]) & (hl_bars >= 1) \
            & (hl_bars <= 240 / mpb) & (edge >= P["kappa"] * RTt)

        if t >= warm and t % 60 == 0:
            for (i_, j_), kd in pair_kind.items():
                sig_samples[kd].extend((sig_pair[:, i_, j_][pair_ok[:, i_, j_]] / BP).tolist())
        if calib is not None and t >= warm:
            for ai in range(A):
                for i in range(K):
                    for j in range(i + 1, K):
                        if pair_ok[ai, i, j] and allowed[i, j]:
                            calib[(ai, i, j)].append((s[ai, i, j], sig_pair[ai, i, j], hl_bars[ai, i, j],
                                                      bool(gate_mask[ai, i, j] or gate_mask[ai, j, i]),
                                                      RTt[ai, i, j], int(regime[t])))

        total = E.sum() + sum(x_[2] for x_ in transfers_inflight)
        regime_pnl[regime[t]] += total - prev_total
        regime_bars[regime[t]] += 1
        prev_total = total
        eq_curve[t] = total
        if t < warm or P["no_trade"]:
            z_prev = z
            continue
        if t == warm and P["static_load"] > 0:
            # stress: book ที่ "ถือค้าง" (เช่นถือเก็บ funding/basis) long hub ตัวแรก / short CEX ตัวแรก ขนาด static_load·Q
            hubs_ = [k for k in range(K) if is_hub[k] and trade_k[k]]
            cexs_ = [k for k in range(K) if is_cex[k] and trade_k[k]]
            if hubs_ and cexs_:
                h_, c_ = hubs_[0], cexs_[0]
                for ai in range(A):
                    qs = P["static_load"] * min(Q[ai, h_], Q[ai, c_]) / mid[t, ai].mean()
                    L = Layer(ai, c_, h_, qs, t, "static")
                    trade(ai, c_, -qs, taker_px(ai, c_, -1, t), vp[c_]["taker"], t, L)
                    trade(ai, h_, +qs, taker_px(ai, h_, +1, t), vp[h_]["taker"], t, L)
                    layers.append(L)

        # ── ความเสี่ยงต่อตลาด ──
        IR = (np.abs(n) * np.nan_to_num(mid[t]) * imr).sum(axis=0)
        reduce_only = (E < IR) | (lev_now > P["lalert"]) | (E <= 0)
        # เยียวยาก่อนโยกเงิน: ลด layer ใหม่สุดบนตลาดที่ leverage เกิน alert จน ≤ lev
        for k in np.where(reduce_only & trade_k & P["derisk"])[0]:
            proj = Gk[k]
            for L in sorted(layers, key=lambda L_: -L_.t0):
                if proj <= P["lev"] * max(E[k], 0) or L.closing:
                    continue
                if k in (L.i, L.j):
                    L.closing = "taker"
                    pending.append(dict(type="close", layer=L, mode="taker"))
                    proj -= L.q * mid[t, L.a, k]
                    stats["derisk_closes"] += 1

        # ── ปิด layer ──
        hold_cap = 24 * bars_h
        for L in layers:
            if L.closing or L.dead or L.i is None or L.j is None or L.kind == "static":
                continue
            ai, i, j = L.a, L.i, L.j
            if not pair_ok[ai, i, j]:
                continue
            zz = z[ai, i, j]
            age = t - L.t0
            if zz >= 8:
                mode = "taker"
                stats["stops"] += 1
            elif age > min(6 * hl_bars[ai, i, j], hold_cap) and zz > P["z_out"]:
                mode = "taker"
                stats["timeouts"] += 1
            elif zz <= P["z_out"]:
                mode = "taker" if L.tries >= P["close_ttl"] else "maker"
            else:
                continue
            L.closing = mode
            od = dict(type="close", layer=L, mode=mode)
            if mode == "maker":
                mk = maker_of[i, j]
                side_mk = +1 if mk == i else -1
                buf = m_sig[t, ai] * qbuf * mid[t, ai, mk]
                bid = mid[t, ai, mk] * (1 - hsd[t, ai, mk])
                ask = mid[t, ai, mk] * (1 + hsd[t, ai, mk])
                od["limit"] = (bid - buf) if side_mk > 0 else (ask + buf)
            pending.append(od)

        # ── เปิด layer ใหม่ ──
        nlay_pair = defaultdict(int)
        nlay_asset = np.zeros(A, dtype=int)
        for L in layers:
            if not L.dead and L.kind != "static":
                nlay_pair[(L.a, min(L.i or 0, L.j or 0), max(L.i or 0, L.j or 0))] += 1
                nlay_asset[L.a] += 1
        cand = []
        for ai, i, j in np.argwhere(gate_mask):
            npair = nlay_pair[(ai, min(i, j), max(i, j))]
            thr = zin[min(npair, len(zin) - 1)]
            if npair >= P["max_per_pair"] or z[ai, i, j] < thr or z_prev[ai, i, j] < thr:   # persistence ที่เกณฑ์ของชั้นนั้น
                continue
            if nlay_asset[ai] >= P["max_per_asset"]:
                continue
            if reduce_only[i] or reduce_only[j] or not (avail(i, t, ai) and avail(j, t, ai)):
                continue
            # kill: ราคาหลุดราคากลางผิดปกติ (1% BTC/ETH, 2% อื่น, 3% หุ้น/ทองช่วงตลาดปิด) → ไม่เปิดใหม่ที่ตลาดนั้น
            kth = 0.03 if closed[t, ai] else kill_th[ai]
            if abs(e[ai, i]) > kth or abs(e[ai, j]) > kth:
                stats["kill_skip"] += 1
                continue
            score = (edge[ai, i, j] - P["kappa"] * RTt[ai, i, j]) / (imr[ai, i] + imr[ai, j] + 1e-9)
            cand.append((score, ai, i, j))
        cand.sort(reverse=True)
        opened = np.zeros(A, dtype=int)
        pend_pairs = set()
        n_proj = n.copy()                                  # รวมคำสั่งที่ส่งไปแล้วใน bar นี้
        for score, ai, i, j in cand:
            if opened[ai] >= P["opens_per_bar"] or (ai, i, j) in pend_pairs:
                continue
            size = unit_usd[ai] * (0.5 if closed[t, ai] else 1.0)
            pa = mid[t, ai]
            q = size / np.nanmean(pa[trade_k])
            okcap = True
            for k, sgn in ((i, -1), (j, +1)):
                newpos = (n_proj[ai, k] + sgn * q) * pa[k]
                if abs(newpos) > Q[ai, k] + 1e-9:
                    okcap = False
                if (Gk[k] + q * pa[k]) > P["lev"] * max(E[k], 0):
                    okcap = False
                nd = DB[blk[ai], k] + sgn * q * pa[k]               # ทิศสุทธิต่อตลาด แยกกลุ่ม (คริปโต/หุ้น/ทอง)
                if abs(nd) > dir_cap * max(E[k], 0) and abs(nd) > abs(DB[blk[ai], k]):
                    okcap = False
            if not okcap:
                continue
            mk = maker_of[i, j]
            tk = j if mk == i else i
            side_mk = -1 if mk == i else +1
            buf = m_sig[t, ai] * qbuf * pa[mk]
            bid = pa[mk] * (1 - hsd[t, ai, mk])
            ask = pa[mk] * (1 + hsd[t, ai, mk])
            limit = (ask + buf) if side_mk < 0 else (bid - buf)
            ki, kj = kind[i], kind[j]
            ptype = "LC-LR" if (is_hub[i] and is_hub[j]) else "CEX-CEX" if (is_cex[i] and is_cex[j]) else "CEX-Lighter"
            L = Layer(ai, i, j, q, t, ptype)
            pending.append(dict(type="open", layer=L, maker=mk, taker=tk, limit=limit))
            pend_pairs.add((ai, i, j))
            opened[ai] += 1
            Gk[i] += q * pa[i]
            Gk[j] += q * pa[j]
            DB[blk[ai], i] -= q * pa[i]
            DB[blk[ai], j] += q * pa[j]
            n_proj[ai, i] -= q
            n_proj[ai, j] += q
            stats["open_orders"] += 1
        z_prev = z

    # ── สรุป ──
    for L in layers:
        if not L.dead:
            mtm = L.cash
            if L.i is not None:
                mtm += -L.q * mid[T - 1, L.a, L.i]
            if L.j is not None:
                mtm += L.q * mid[T - 1, L.a, L.j]
            by_kind[L.kind] += mtm
    years = T / bpy
    final = E.sum() + sum(x_[2] for x_ in transfers_inflight)
    pnl = final - P["capital"]
    daily = eq_curve[::max(1, int(24 * bars_h))]
    dr = np.diff(daily) / P["capital"]
    sharpe = float(dr.mean() / dr.std() * math.sqrt(365)) if len(dr) > 2 and dr.std() > 0 else float("nan")
    peak = np.maximum.accumulate(eq_curve)
    lc = np.array(legcount_hist)
    active = lc >= 2
    res = dict(
        ann_return=pnl / P["capital"] / years,
        ann_calm=regime_pnl[0] / P["capital"] / max(regime_bars[0] / bpy, 1e-9),
        ann_vol=regime_pnl[1] / P["capital"] / max(regime_bars[1] / bpy, 1e-9),
        sharpe=sharpe, max_dd=float(((eq_curve - peak) / P["capital"]).min()),
        worst_day=float(dr.min()) if len(dr) else 0.0,
        turnover_per_day=stats["turnover"] / P["capital"] / (years * 365),
        legs_ge3_share=float((lc[active] >= 3).mean()) if active.any() else 0.0,
        avg_legs_active=float(lc[active].mean()) if active.any() else 0.0,
        max_unhedged=max_unhedged,
        avg_lev={v: float(sum_lev[k] / max(nbar_live, 1)) for k, v in enumerate(venues) if trade_k[k]},
        pos_share=bars_pos / max(nbar_live, 1), dir_cap=dir_cap,
        transfers_per_year=stats["transfers"] / years, usd_transferred=stats["usd_transferred"],
        liq_partial=stats["liq_partial"], liq_full=stats["liq_full"], liq_cex=stats["liq_cex"], adl=stats["adl"],
        leg_fail=stats["leg_fail"], outages=stats["outages"], stops=stats["stops"], timeouts=stats["timeouts"],
        derisk=stats["derisk_closes"],
        minE={v: float(minEr[k]) for k, v in enumerate(venues) if trade_k[k]},
        maxlev={v: float(maxlev[k]) for k, v in enumerate(venues) if trade_k[k]},
        maxdir={v: float(maxdir[k]) for k, v in enumerate(venues) if trade_k[k]},
        turn_share={v: stats[f"turn_{v}"] / max(stats["turnover"], 1e-9) for k, v in enumerate(venues) if trade_k[k]},
        pnl={k_: v_ for k_, v_ in acc.items() if not k_.startswith("fees_")},
        fees_by_venue={k_[5:]: v_ for k_, v_ in acc.items() if k_.startswith("fees_")},
        final_n=n.copy(), pnl_total=pnl, alloc={v: float(E0[k]) for k, v in enumerate(venues) if trade_k[k]},
        unit_usd=unit_usd.tolist(), by_kind=dict(by_kind), by_asset=dict(by_asset),
        sig_med={k_: float(np.median(v_)) for k_, v_ in sig_samples.items() if v_},
    )
    if calib is not None:
        res["calib"] = (calib, assets, venues, RT)
    return res


# ───────────────────────── แสดงผล / sweep / selftest ─────────────────────────

def show(r):
    print(f"ผลตอบแทน/ปี           : {r['ann_return']*100:7.2f}%   (ช่วงเงียบ {r['ann_calm']*100:.1f}%/ปี, ช่วงผันผวน {r['ann_vol']*100:.1f}%/ปี)")
    print(f"Sharpe รายวัน / MaxDD : {r['sharpe']:.2f} / {r['max_dd']*100:.2f}%  วันแย่สุด {r['worst_day']*100:.2f}%")
    print(f"PnL แยกส่วน ($)        : " + ", ".join(f"{k} {v:,.0f}" for k, v in sorted(r["pnl"].items())))
    print(f"PnL ตามประเภทคู่ ($)   : " + ", ".join(f"{k} {v:,.0f}" for k, v in sorted(r["by_kind"].items())) + "  (ไม่รวม funding)")
    print(f"σ คู่ (median bp)      : " + ", ".join(f"{k} {v:.2f}" for k, v in r["sig_med"].items()))
    print(f"PnL ตามสินทรัพย์ ($)   : " + ", ".join(f"{k} {v:,.0f}" for k, v in r["by_asset"].items()))
    print(f"ค่าธรรมเนียมรายตลาด    : " + ", ".join(f"{k} {v:,.0f}" for k, v in r["fees_by_venue"].items()))
    print(f"turnover/วัน (×ทุน)    : {r['turnover_per_day']:.2f}   สัดส่วน: " + ", ".join(f"{k} {v*100:.0f}%" for k, v in r["turn_share"].items()))
    print(f"จำนวนขาต่อสินทรัพย์    : เฉลี่ย {r['avg_legs_active']:.2f} ขา, เวลาที่ถือ ≥3 ขา {r['legs_ge3_share']*100:.0f}%")
    print(f"ทุนตั้งต้นต่อตลาด      : " + ", ".join(f"{k} ${v:,.0f}" for k, v in r["alloc"].items()))
    print(f"equity ต่ำสุด/ตั้งต้น  : " + ", ".join(f"{k} {v*100:.0f}%" for k, v in r["minE"].items()))
    print(f"leverage เฉลี่ยต่อตลาด : " + ", ".join(f"{k} {v:.3f}x" for k, v in r["avg_lev"].items())
          + f"  (มีสถานะ {r['pos_share']*100:.0f}% ของเวลา; เพดานทิศสุทธิ {r['dir_cap']:.1f}×equity)")
    print(f"leverage สูงสุดต่อตลาด : " + ", ".join(f"{k} {v:.2f}x" for k, v in r["maxlev"].items()))
    print(f"โยกเงินข้ามตลาด        : {r['transfers_per_year']:.1f} ครั้ง/ปี (${r['usd_transferred']:,.0f})")
    print(f"liquidation            : Lighter บางส่วน {r['liq_partial']:.0f}, Lighter ทั้งบัญชี {r['liq_full']:.0f}, CEX {r['liq_cex']:.0f}; ADL {r['adl']:.0f}")
    print(f"ขาหลุด/hedge พลาด      : {r['leg_fail']:.0f}; |Σn|·P/gross สูงสุด {r['max_unhedged']*100:.2f}%; outage {r['outages']:.0f}; stop {r['stops']:.0f}; timeout {r['timeouts']:.0f}; derisk {r['derisk']:.0f}")


def row(label, r):
    tr = {k: v for k, v in r["by_kind"].items() if k != "static"}
    tot = sum(abs(v) for v in tr.values()) or 1.0
    lclr = tr.get("LC-LR", 0.0) / tot * 100 if tr else float("nan")
    return (f"{label:<30} {r['ann_return']*100:7.1f}% {r['ann_calm']*100:7.1f}% {r['ann_vol']*100:7.1f}% "
            f"{r['max_dd']*100:6.2f}% {r['transfers_per_year']:6.1f} {r['liq_partial']+r['liq_full']+r['liq_cex']:4.0f} "
            f"{min(r['minE'].values())*100:5.0f}% {max(r['avg_lev'].values()):5.2f} {r['legs_ge3_share']*100:5.0f}% "
            f"{r['sig_med'].get('CEX-Lighter', float('nan')):5.2f} {lclr:6.0f}% {r['turnover_per_day']:6.2f}")


HDR = (f"{'ชุดทดลอง':<30} {'ret/ปี':>8} {'เงียบ':>8} {'ผันผวน':>8} {'maxDD':>7} {'โยก/ปี':>6} {'liq':>4} {'minE':>6} "
       f"{'ℓเฉลี่ย':>5} {'≥3ขา':>6} {'σC-L':>5} {'LC-LR':>7} {'turn':>6}")
HDR_NOTE = ("  ℓเฉลี่ย = leverage เฉลี่ยของตลาดที่ถือหนักสุด | ≥3ขา = % เวลาที่สินทรัพย์ถือ ≥3 ตลาดพร้อมกัน (จากเวลาที่มีสถานะ) | "
            "σC-L = σ คู่ CEX–Lighter median (bp) | LC-LR = สัดส่วนกำไรเทรดจากคู่ Lighter–Lighter | turn = turnover/วัน ×ทุน")


def sweep(name, base, kw):
    def go(label, data=None, **extra):
        k2 = dict(kw)
        k2.update(extra)
        r = run(data or base, **k2)
        print(row(label, r), flush=True)
        return r


    full = [v for v in base["venues"] if VENUES[v]["kind"] != "data"]
    print(HDR)
    print(HDR_NOTE)
    if name in ("fees", "all"):
        print("— ค่าธรรมเนียม maker ฝั่ง CEX (bp) × ชุดตลาด —")
        sets = [("2 ขา LC-BG", None, "LC-BG", False), ("2 ขา LC-LR", None, "LC-LR", False),
                ("3 ตลาด LC,LR,BG", ["LC", "LR", "BG"], None, False), ("4 ตลาด", None, None, False),
                ("4 ตลาด ไม่มีคู่ LC-LR", None, None, True)]
        for fee in (-0.5, 0.0, 1.0, 2.0, 3.0):
            for lab, vs, po, nh in sets:
                if po == "LC-LR" and fee != 1.0:
                    continue                                    # ไม่มีขา CEX: ค่าธรรมเนียม CEX ไม่มีผล
                go(f"{lab} fee={fee}", cex_maker=fee, pairs_only=po, trade_venues=vs, no_hub_pair=nh)
    if name in ("legs", "all"):
        print("— 2 ขา vs หลายขา (ข้อมูลชุดเดียวกัน 4 ตลาด, ทุนเท่ากัน) —")
        go("2 ขา LC-BG", pairs_only="LC-BG")
        go("2 ขา LC-LR", pairs_only="LC-LR")
        go("หลายขา LC,LR,BG,BY")
        go("หลายขา ไม่มีคู่ LC-LR", no_hub_pair=True)
        go("หลายขา + CEX–CEX", allow_cex_cex=True)
    if name in ("thai", "all"):
        print("— ไม่มี Bybit (ผู้ใช้ไทย) vs ครบ (ข้อมูลชุดเดียวกัน; ตลาดที่ไม่เทรดยังใช้เป็นราคาอ้างอิง) —")
        go("LC,LR,BG", trade_venues=["LC", "LR", "BG"])
        go("LC,LR,BG,BY", trade_venues=full)
        go("LC,BG,BY (ไม่ใช้ LR)", trade_venues=["LC", "BG", "BY"])
        go("LC,BG (2 ตลาด หลายเหรียญ)", trade_venues=["LC", "BG"])
        go("LC,LR (Lighter อย่างเดียว)", trade_venues=["LC", "LR"])
    if name in ("lev", "all"):
        print("— leverage ต่อตลาด: shock วันที่ 20 (+12%), 21 (+8%), 45 (−20%) + Lighter ล่ม ~2 ชม. ตอน shock —")
        print("  (ก) book เทรดสั้นอย่างเดียว | (ข) + ถือค้าง 50% ของความจุ (long LC / short BG) เหมือนถือเก็บ funding/basis")
        shock = synth(base["assets"], base["venues"], **dict(GEN, shocks=True, days=max(GEN["days"], 50)))
        for sl in (0.0, 0.5):
            for lev in (1, 2, 3, 5, 8, 12):
                go(f"{'(ข)' if sl else '(ก)'} lev={lev}", shock, lev=lev, lalert=lev * 4 / 3, lxfer=lev * 5 / 3,
                   static_load=sl)
        for lev in (3, 8, 12):
            go(f"(ข) lev={lev} ไม่โยก ไม่ derisk", shock, lev=lev, lalert=lev * 4 / 3, lxfer=lev * 5 / 3,
               static_load=0.5, no_transfers=True, derisk=False)
    if name in ("lcost", "all"):
        print("— ต้นทุนจริงของ taker บน Lighter (bp) × catch-up —")
        for la in (0.3, 0.7, 1.5, 3.0):
            for cu in (0.0, 1.0):
                go(f"lighter_adv={la} catchup={cu}", lighter_adv=la, catchup=cu)
    if name in ("resid", "all"):
        print("— ขนาด residual (สมมติฐานสำคัญที่สุด) —")
        for rs in (0.5, 0.75, 1.0, 1.5, 2.0):
            go(f"resid_scale={rs}", synth(base["assets"], base["venues"], **dict(GEN, resid_scale=rs)))
        print("— residual ขยายตามความผันผวนแค่ไหน (elasticity; 1 = สัดส่วนตรง = ค่าเริ่ม) —")
        for el in (0.0, 0.5, 1.0):
            go(f"resid_vol_elast={el}", synth(base["assets"], base["venues"], **dict(GEN, resid_vol_elast=el)))


def selftest():
    print("selftest ...")
    d = synth(["BTC", "SPY"], ["LC", "LR", "BG", "BY", "BN"], days=12, seed=3, shocks=False)
    r = run(d, p_leg_fail=0.0, p_adl=0.0, outage_rate=0.0, warmup_h=12)
    assert np.allclose(r["final_n"].sum(axis=1), 0, atol=1e-9), "Σ_k n[a,k] ต้องเป็น 0 เมื่อไม่มีขาหลุด"
    comp = sum(v for k, v in r["pnl"].items())
    assert abs(comp - r["pnl_total"]) < 1e-6 * 100_000, f"PnL แยกส่วนไม่รวมเท่ากำไรทั้งหมด {comp} vs {r['pnl_total']}"
    r0 = run(synth(["BTC"], ["LC", "BG", "BN"], days=8, seed=4, resid_scale=0.0), warmup_h=12, funding_on=False,
             p_adl=0.0, outage_rate=0.0)
    assert r0["pnl_total"] <= 1e-6, "ไม่มี residual ต้องไม่มีกำไร"
    sd = synth(["BTC", "ETH"], ["LC", "LR", "BG", "BY", "BN"], days=50, seed=5, shocks=True)
    nliq = ntr = 0
    for lev, nt, dr in ((12, True, False), (8, False, True)):              # ไม่โยก+ไม่ derisk / มีทั้งคู่
        rs = run(sd, lev=lev, lalert=lev * 4 / 3, lxfer=lev * 5 / 3, static_load=0.9, warmup_h=12, no_transfers=nt,
                 derisk=dr)
        comp = sum(v for k, v in rs["pnl"].items())
        assert abs(comp - rs["pnl_total"]) < 1e-6 * 100_000, "เงินสดรั่วระหว่าง liquidation/โยกเงิน"
        nliq += rs["liq_partial"] + rs["liq_full"] + rs["liq_cex"]
        ntr += rs["transfers_per_year"]
    assert nliq > 0 and ntr > 0, f"stress ต้องเกิดทั้ง liquidation และการโยกเงิน (liq={nliq}, โยก={ntr})"
    print("ok: Σn=0, PnL แยกส่วนรวมตรง, ไม่มี residual = ไม่มีกำไร, บัญชีไม่รั่วแม้มี liquidation "
          f"({nliq:.0f} ครั้ง) และโยกเงิน ({ntr:.1f}/ปี) ใน stress")


def calibrate(d, kw):
    r = run(d, no_trade=True, **kw)
    calib, assets, venues, RT = r["calib"]
    bar = d["bar"]
    print("วัดจากข้อมูล (ไม่เทรด): σ คู่และ half-life แยกช่วงเงียบ/ผันผวน, % เวลาที่ผ่าน gate เดียวกับที่ engine ใช้")
    print(f"{'asset':<6} {'คู่':<8} {'σ เงียบ':>8} {'σ ผันผวน':>9} {'HL นาที':>8} {'|z|≥2':>7} {'ผ่าน gate':>9} {'RT bp':>6}")
    for (ai, i, j), vals in sorted(calib.items()):
        arr = np.array([(v[0], v[1], v[2], v[4], v[5]) for v in vals])
        gate = np.mean([v[3] for v in vals])
        zz = np.abs(arr[:, 0] / arr[:, 1])
        calm, vol = arr[arr[:, 4] == 0], arr[arr[:, 4] == 1]
        sc = np.median(calm[:, 1]) / BP if len(calm) else float("nan")
        sv = np.median(vol[:, 1]) / BP if len(vol) else float("nan")
        print(f"{assets[ai]:<6} {venues[i]+'-'+venues[j]:<8} {sc:8.2f} {sv:9.2f} "
              f"{np.median(arr[:,2])*bar/60:8.1f} {np.mean(zz>=2)*100:6.1f}% {gate*100:8.2f}% {np.median(arr[:,3]):6.1f}")
    print("อัตราส่วน σ ผันผวน/σ เงียบ เทียบกับ vol ตลาดผันผวน/เงียบ → ใช้ตั้ง --resid-vol-elast; ถ้า HL > 240 นาทีหรือผ่าน gate"
          " น้อยมาก = คู่นั้นไม่คุ้ม")


GEN = dict(days=60, bar=60, seed=7, resid_scale=1.0, vol_share=0.25, shocks=False, lag_hl_s=1.0, resid_vol_elast=1.0)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv")
    ap.add_argument("--data-only", default="BN")
    ap.add_argument("--days", type=int, default=60)
    ap.add_argument("--bar", type=int, default=60)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--assets", default="BTC,ETH,HYPE,SPY")
    ap.add_argument("--venues", default="LC,LR,BG,BY", help="ตลาดที่เทรด (BN ถูกเพิ่มเป็นข้อมูลราคากลางอัตโนมัติ)")
    ap.add_argument("--capital", type=float, default=100_000)
    ap.add_argument("--lev", type=float, default=3.0, help="leverage สูงสุดต่อตลาดสำหรับเปิดความเสี่ยงใหม่")
    ap.add_argument("--cex-maker-bps", type=float)
    ap.add_argument("--cex-taker-bps", type=float)
    ap.add_argument("--lighter-adv-bps", type=float, help="ต้นทุนแฝงของ taker บน Lighter (ความหน่วง 300ms)")
    ap.add_argument("--hedge-catchup", type=float, default=1.0)
    ap.add_argument("--resid-scale", type=float, default=1.0, help="ขนาด residual ข้ามตลาด (สมมติ) — ตัวกำหนดผลตอบแทนหลัก")
    ap.add_argument("--vol-share", type=float, default=0.25)
    ap.add_argument("--lag-hl-s", type=float, default=1.0, help="Lighter ไล่ราคาทันภายในกี่วินาที (ยิ่งมาก = ยิ่งมี lead-lag edge ปลอม)")
    ap.add_argument("--resid-vol-elast", type=float, default=1.0, help="residual ∝ (vol)^e — สมมติฐาน 'ผันผวนได้เยอะ'")
    ap.add_argument("--shocks", action="store_true", help="ใส่ shock ±8–20%% + Lighter ล่ม ~2 ชม.")
    ap.add_argument("--no-shock-outage", action="store_true")
    ap.add_argument("--static-load", type=float, default=0.0, help="ถือค้าง long LC/short CEX สัดส่วนของความจุ (stress)")
    ap.add_argument("--dir-cap", type=float, help="เพดาน |ทิศสุทธิต่อตลาด|/equity (ค่าเริ่ม 2/3·lev)")
    ap.add_argument("--no-hub-pair", action="store_true", help="ปิดคู่ LC–LR")
    ap.add_argument("--pairs-only", help="เช่น LC-BG = baseline 2 ขา")
    ap.add_argument("--allow-cex-cex", action="store_true")
    ap.add_argument("--no-funding", action="store_true")
    ap.add_argument("--no-transfers", action="store_true")
    ap.add_argument("--p-adl", type=float, default=0.05)
    ap.add_argument("--outage-rate", type=float, default=1.0)
    ap.add_argument("--freeze", help="เช่น BG:5 = Bitget ระงับถอน 5 วัน")
    ap.add_argument("--sweep", choices=["fees", "legs", "thai", "lev", "lcost", "resid", "all"])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--calibrate", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        selftest()
        return
    GEN.update(days=a.days, bar=a.bar, seed=a.seed, resid_scale=a.resid_scale, vol_share=a.vol_share, shocks=a.shocks,
               lag_hl_s=a.lag_hl_s, resid_vol_elast=a.resid_vol_elast)
    if a.csv:
        d = load_csv(a.csv, set(a.data_only.split(",")), a.bar)
    else:
        venues = a.venues.split(",") + [v for v in a.data_only.split(",") if v and v not in a.venues.split(",")]
        d = synth(a.assets.split(","), venues, **GEN)
    kw = dict(capital=a.capital, lev=a.lev, lalert=a.lev * 4 / 3, lxfer=a.lev * 5 / 3, cex_maker=a.cex_maker_bps,
              cex_taker=a.cex_taker_bps, lighter_adv=a.lighter_adv_bps, catchup=a.hedge_catchup,
              pairs_only=a.pairs_only, allow_cex_cex=a.allow_cex_cex, funding_on=not a.no_funding,
              no_transfers=a.no_transfers, p_adl=a.p_adl, outage_rate=a.outage_rate, freeze=a.freeze, seed=a.seed,
              static_load=a.static_load, dir_cap=a.dir_cap, no_hub_pair=a.no_hub_pair,
              shock_outage=not a.no_shock_outage)
    if a.calibrate:
        calibrate(d, kw)
        return
    if a.sweep:
        sweep(a.sweep, d, kw)
        return
    print(f"ข้อมูล: {'CSV ' + a.csv if a.csv else 'จำลอง'} | สินทรัพย์ {','.join(d['assets'])} | ตลาด {','.join(d['venues'])} | "
          f"{d['mid'].shape[0]} bar × {d['bar']} วิ")
    show(run(d, **kw))


if __name__ == "__main__":
    main()
