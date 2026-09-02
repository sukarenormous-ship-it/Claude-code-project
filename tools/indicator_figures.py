#!/usr/bin/env python3
"""สร้าง docs/indicator-figures.json — ตัวเลขทุกตัวของภาคผนวก E "ตระกูลอินดิเคเตอร์"

กฎเดียวกับทั้งเล่ม: ห้ามพิมพ์ตัวเลขลอย ๆ ลงในบท ทุกตัวต้องมาจากไฟล์นี้
อินพุตคือราคารายวัน BTC ชุดเดียวกับที่ทุกบทใช้ (docs/nq-figures.json → "ราคารายวัน")
จึงไม่ต้องพึ่งข้อมูลดิบเพิ่ม และรันซ้ำได้ผลเดิมเสมอ

ข้อจำกัดที่ต้องพูดตรง ๆ (บทระบุไว้ด้วย):
  - ข้อมูลมีราคาเดียวต่อวัน (median ของ underlying_price ในสแนปช็อต) ไม่มี high/low
    → ADX ในไฟล์นี้เป็น "ค่าประมาณจากราคาปิดอย่างเดียว" (True Range = |ΔP|)
  - 57 วัน = ตัวอย่างน้อยมาก ใช้ดู "กลไก" ของสูตร ไม่ใช่หลักฐานว่าอินดิเคเตอร์ดีหรือแย่

    python3 tools/indicator_figures.py
"""

import json
import math
import os
import random
import statistics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "docs", "nq-figures.json")
OUT = os.path.join(ROOT, "docs", "indicator-figures.json")

FOCUS = "2026-08-20"          # วันที่ระบบ EMA ของมินสั่ง "ซื้อ" ที่ 70,007 (Part 3)
RSI_N, BB_N, BB_K = 14, 20, 2
MACD_FAST, MACD_SLOW, MACD_SIG = 12, 26, 9
ADX_N = 14
LR_N, LR_EMA_N = 20, 10          # หน้าต่าง regression บนราคา / บน EMA12
SEED, PATHS = 20260820, 2000


# ── เครื่องคำนวณ ───────────────────────────────────────────────────────────────
def ema(vals, n):
    """EMA มาตรฐาน (k = 2/(n+1)) เริ่มจาก SMA ของ n ค่าแรก — คืน list ยาวเท่า vals (None ช่วงอุ่นเครื่อง)"""
    k = 2 / (n + 1)
    out = [None] * len(vals)
    if len(vals) < n:
        return out
    s = sum(vals[:n]) / n
    out[n - 1] = s
    for i in range(n, len(vals)):
        s = vals[i] * k + s * (1 - k)
        out[i] = s
    return out


def rsi_wilder(prices, n=RSI_N):
    """RSI แบบ Wilder (1978): ค่าเฉลี่ยกำไร/ขาดทุนแบบ smoothing α = 1/n
    คืน list ของ dict ต่อวัน (index ตรงกับ prices; None ช่วงอุ่นเครื่อง)"""
    out = [None] * len(prices)
    deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
    gains = [max(d, 0.0) for d in deltas]
    losses = [max(-d, 0.0) for d in deltas]
    if len(deltas) < n:
        return out
    ag = sum(gains[:n]) / n
    al = sum(losses[:n]) / n
    for i in range(n - 1, len(deltas)):
        if i >= n:
            ag = (ag * (n - 1) + gains[i]) / n
            al = (al * (n - 1) + losses[i]) / n
        rs = ag / al if al > 0 else float("inf")
        rsi = 100.0 if al == 0 else 100 - 100 / (1 + rs)
        out[i + 1] = {"avg_gain": ag, "avg_loss": al, "rs": rs, "rsi": rsi,
                      "delta": deltas[i], "gain": gains[i], "loss": losses[i]}
    return out


def bollinger(prices, n=BB_N, k=BB_K):
    out = [None] * len(prices)
    for i in range(n - 1, len(prices)):
        w = prices[i - n + 1:i + 1]
        m = statistics.mean(w)
        s = statistics.pstdev(w)          # population SD — แบบที่ Bollinger ใช้
        up, lo = m + k * s, m - k * s
        out[i] = {"sma": m, "sd": s, "upper": up, "lower": lo,
                  "pct_b": (prices[i] - lo) / (up - lo) if up > lo else None}
    return out


def macd(prices, fast=MACD_FAST, slow=MACD_SLOW, sig=MACD_SIG):
    ef, es = ema(prices, fast), ema(prices, slow)
    line = [None if (a is None or b is None) else a - b for a, b in zip(ef, es)]
    valid = [v for v in line if v is not None]
    sig_valid = ema(valid, sig)
    offset = len(line) - len(valid)
    signal = [None] * len(line)
    for i, v in enumerate(sig_valid):
        signal[offset + i] = v
    out = []
    for i in range(len(prices)):
        if line[i] is None:
            out.append(None)
            continue
        out.append({"ema_fast": ef[i], "ema_slow": es[i], "macd": line[i],
                    "signal": signal[i],
                    "hist": None if signal[i] is None else line[i] - signal[i]})
    return out


def adx_close_only(prices, n=ADX_N):
    """ADX ประมาณจากราคาปิดอย่างเดียว: TR = |ΔP|, +DM = max(ΔP,0), −DM = max(−ΔP,0)
    (ของจริงของ Wilder ใช้ high/low ซึ่งชุดข้อมูลนี้ไม่มี) — smoothing แบบ Wilder ทั้งหมด"""
    out = [None] * len(prices)
    d = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
    tr = [abs(x) for x in d]
    pdm = [max(x, 0.0) for x in d]
    ndm = [max(-x, 0.0) for x in d]
    if len(d) < 2 * n:
        return out
    s_tr, s_p, s_n = sum(tr[:n]), sum(pdm[:n]), sum(ndm[:n])
    dx_hist = []
    adx = None
    for i in range(n - 1, len(d)):
        if i >= n:
            s_tr = s_tr - s_tr / n + tr[i]
            s_p = s_p - s_p / n + pdm[i]
            s_n = s_n - s_n / n + ndm[i]
        di_p = 100 * s_p / s_tr if s_tr else 0.0
        di_n = 100 * s_n / s_tr if s_tr else 0.0
        dx = 100 * abs(di_p - di_n) / (di_p + di_n) if (di_p + di_n) else 0.0
        dx_hist.append(dx)
        if len(dx_hist) == n:
            adx = sum(dx_hist) / n
        elif len(dx_hist) > n:
            adx = (adx * (n - 1) + dx) / n
        out[i + 1] = {"di_plus": di_p, "di_minus": di_n, "dx": dx, "adx": adx}
    return out


def ols_time(y):
    """Linear regression ของค่า y บนเวลา t = 1..n (OLS ธรรมดา)
    คืน slope, intercept, ค่าฟิตปลายหน้าต่าง, R², SD ของ residual (n−2), residual วันสุดท้าย, t-stat ของ slope"""
    n = len(y)
    t = list(range(1, n + 1))
    tb, yb = sum(t) / n, sum(y) / n
    sxx = sum((a - tb) ** 2 for a in t)
    sxy = sum((a - tb) * (b - yb) for a, b in zip(t, y))
    m = sxy / sxx
    c = yb - m * tb
    fit = [c + m * a for a in t]
    res = [b - f for b, f in zip(y, fit)]
    sse = sum(x * x for x in res)
    sst = sum((b - yb) ** 2 for b in y)
    s = math.sqrt(sse / (n - 2)) if n > 2 else 0.0
    se = s / math.sqrt(sxx) if sxx else 0.0
    return {"slope": m, "intercept": c, "end": fit[-1], "r2": (1 - sse / sst) if sst else 0.0,
            "sd": s, "resid": res[-1], "t": (m / se) if se else 0.0}


def r(x, nd=2):
    return None if x is None else round(x, nd)


# ── สร้างตัวเลข ────────────────────────────────────────────────────────────────
def build():
    with open(SRC) as fh:
        fig = json.load(fh)
    px = fig["ราคารายวัน"]
    days = sorted(px)
    p = [px[d] for d in days]
    idx = {d: i for i, d in enumerate(days)}
    f = idx[FOCUS]
    prev_day = days[f - 1]
    daily_sd_pct = 100 * statistics.pstdev([p[i] / p[i - 1] - 1 for i in range(1, len(p))])

    # ── RSI ──────────────────────────────────────────────────────────────────
    R = rsi_wilder(p)
    rf, rp = R[f], R[f - 1]
    rsi_days = [(days[i], R[i]["rsi"]) for i in range(len(p)) if R[i] is not None]
    above70 = [(d, v) for d, v in rsi_days if v > 70]
    below30 = [(d, v) for d, v in rsi_days if v < 30]
    first_above = above70[0] if above70 else None
    peak = max(rsi_days, key=lambda t: t[1])
    rsi_block = {
        "คำอธิบาย": f"RSI({RSI_N}) แบบ Wilder smoothing บนราคารายวันจริง",
        "วันที่มี RSI": len(rsi_days),
        "แทนค่าวันโฟกัส": {
            "วันที่": FOCUS,
            "ราคาเมื่อวาน": p[f - 1], "ราคาวันนี้": p[f],
            "เปลี่ยนแปลงวันนี้": r(rf["delta"]),
            "กำไรวันนี้": r(rf["gain"]), "ขาดทุนวันนี้": r(rf["loss"]),
            "avg_gain เมื่อวาน": r(rp["avg_gain"]), "avg_loss เมื่อวาน": r(rp["avg_loss"]),
            "avg_gain วันนี้": r(rf["avg_gain"]), "avg_loss วันนี้": r(rf["avg_loss"]),
            "RS": r(rf["rs"]), "RSI": r(rf["rsi"]),
            "สัดส่วนขาขึ้นเปอร์เซ็นต์": r(100 * rf["avg_gain"] / (rf["avg_gain"] + rf["avg_loss"]), 1),
        },
        "RSI เมื่อวานโฟกัส": {"วันที่": prev_day, "RSI": r(rp["rsi"])},
        "จำนวนวันเกิน70": len(above70),
        "จำนวนวันต่ำกว่า30": len(below30),
        "สัดส่วนวันเกิน70เปอร์เซ็นต์": r(100 * len(above70) / len(rsi_days), 1),
        "ครั้งแรกที่เกิน70": None if not first_above else {
            "วันที่": first_above[0], "RSI": r(first_above[1]), "ราคา": p[idx[first_above[0]]],
            "ราคาวันสุดท้าย": p[-1],
            "ราคาเปลี่ยนหลังจากนั้นเปอร์เซ็นต์": r(100 * (p[-1] / p[idx[first_above[0]]] - 1), 2),
            "จำนวนวันที่เหลือ": len(days) - 1 - idx[first_above[0]],
        },
        "RSI สูงสุด": {"วันที่": peak[0], "RSI": r(peak[1])},
        "RSI วันสุดท้าย": {"วันที่": days[-1], "RSI": r(rsi_days[-1][1])},
        "RSI ต่ำสุด": {"วันที่": min(rsi_days, key=lambda t: t[1])[0], "RSI": r(min(rsi_days, key=lambda t: t[1])[1])},
        "ครึ่งชีวิตของ smoothing วัน": r(-1 / (math_log(1 - 1 / RSI_N)) * math_log(2), 1),
        "รายวัน": [{"วันที่": d, "RSI": r(v, 1)} for d, v in rsi_days],
    }

    # ── MACD ─────────────────────────────────────────────────────────────────
    M = macd(p)
    mf = M[f]
    crosses = []
    for i in range(1, len(p)):
        a, b = M[i - 1], M[i]
        if a and b and a["hist"] is not None and b["hist"] is not None and a["hist"] * b["hist"] < 0:
            crosses.append({"วันที่": days[i], "ทิศ": "ขึ้น" if b["hist"] > 0 else "ลง",
                            "MACD": r(b["macd"]), "signal": r(b["signal"]), "ราคา": p[i]})
    m_valid = [(days[i], M[i]) for i in range(len(p)) if M[i] and M[i]["hist"] is not None]
    m_first, m_last = m_valid[0], m_valid[-1]
    macd_block = {
        "คำอธิบาย": f"MACD({MACD_FAST},{MACD_SLOW},{MACD_SIG}) บนราคารายวันจริง",
        "แทนค่าวันโฟกัส": {
            "วันที่": FOCUS, "ราคา": p[f],
            "EMA12": r(mf["ema_fast"]), "EMA26": r(mf["ema_slow"]),
            "MACD": r(mf["macd"]), "signal": r(mf["signal"]), "histogram": r(mf["hist"]),
            "MACD เป็นเปอร์เซ็นต์ของราคา": r(100 * mf["macd"] / p[f], 2),
        },
        "จุดตัด": crosses,
        "จำนวนจุดตัด": len(crosses),
        "ขนาดเทียบข้ามเวลา": {
            "วันแรก": {"วันที่": m_first[0], "MACD": r(m_first[1]["macd"]), "ราคา": p[idx[m_first[0]]],
                       "เปอร์เซ็นต์ของราคา": r(100 * m_first[1]["macd"] / p[idx[m_first[0]]], 2)},
            "วันสุดท้าย": {"วันที่": m_last[0], "MACD": r(m_last[1]["macd"]), "ราคา": p[idx[m_last[0]]],
                          "เปอร์เซ็นต์ของราคา": r(100 * m_last[1]["macd"] / p[idx[m_last[0]]], 2)},
        },
    }

    # ── Bollinger ────────────────────────────────────────────────────────────
    B = bollinger(p)
    bf = B[f]
    b_valid = [(days[i], B[i], p[i]) for i in range(len(p)) if B[i]]
    above = [(d, b, q) for d, b, q in b_valid if q > b["upper"]]
    below = [(d, b, q) for d, b, q in b_valid if q < b["lower"]]
    sd_series = [(d, b["sd"]) for d, b, _ in b_valid]
    sd_min, sd_max = min(sd_series, key=lambda t: t[1]), max(sd_series, key=lambda t: t[1])
    bb_block = {
        "คำอธิบาย": f"Bollinger Bands SMA{BB_N} ± {BB_K}σ (population SD) บนราคารายวันจริง",
        "วันที่มีแบนด์": len(b_valid),
        "แทนค่าวันโฟกัส": {
            "วันที่": FOCUS, "ราคา": p[f],
            "SMA20": r(bf["sma"]), "SD20": r(bf["sd"]),
            "แบนด์บน": r(bf["upper"]), "แบนด์ล่าง": r(bf["lower"]),
            "ราคาเหนือแบนด์บน": r(p[f] - bf["upper"]),
            "จำนวนSDเหนือค่าเฉลี่ย": r((p[f] - bf["sma"]) / bf["sd"]),
            "pctB": r(bf["pct_b"], 3),
        },
        "จำนวนวันเหนือแบนด์บน": len(above),
        "จำนวนวันใต้แบนด์ล่าง": len(below),
        "สัดส่วนวันนอกแบนด์เปอร์เซ็นต์": r(100 * (len(above) + len(below)) / len(b_valid), 1),
        "สัดส่วนตามทฤษฎีปกติเปอร์เซ็นต์": 4.55,   # นอก ±2σ ของการแจกแจงปกติ (สองข้างรวม)
        "สัดส่วนในแบนด์ตามทฤษฎีปกติเปอร์เซ็นต์": 95.45,
        "วันเหนือแบนด์บน": [{"วันที่": d, "ราคา": q, "แบนด์บน": r(b["upper"]), "pctB": r(b["pct_b"], 2)} for d, b, q in above],
        "SD เปลี่ยนแค่ไหน": {
            "ต่ำสุด": {"วันที่": sd_min[0], "SD": r(sd_min[1])},
            "สูงสุด": {"วันที่": sd_max[0], "SD": r(sd_max[1])},
            "เท่า": r(sd_max[1] / sd_min[1], 1),
        },
    }

    # ── ADX (ประมาณ) ─────────────────────────────────────────────────────────
    A = adx_close_only(p)
    af = A[f]
    a_valid = [(days[i], A[i]) for i in range(len(p)) if A[i] and A[i]["adx"] is not None]
    adx_block = {
        "คำอธิบาย": f"ADX({ADX_N}) ประมาณจากราคาปิดอย่างเดียว — TR = |ΔP| (ไม่มี high/low ในชุดข้อมูล) ค่าจะ 'แรง' กว่า ADX จริงเพราะ TR ไม่รวมช่วงแกว่งระหว่างวัน",
        "เป็นค่าประมาณ": True,
        "แทนค่าวันโฟกัส": {
            "วันที่": FOCUS,
            "DI_plus": r(af["di_plus"], 1), "DI_minus": r(af["di_minus"], 1),
            "DX": r(af["dx"], 1), "ADX": None if af["adx"] is None else r(af["adx"], 1),
        },
        "ADX วันแรกที่คำนวณได้": {"วันที่": a_valid[0][0], "ADX": r(a_valid[0][1]["adx"], 1)} if a_valid else None,
        "ADX วันสุดท้าย": {"วันที่": a_valid[-1][0], "ADX": r(a_valid[-1][1]["adx"], 1)} if a_valid else None,
        "ADX สูงสุด": {"วันที่": max(a_valid, key=lambda t: t[1]["adx"])[0],
                     "ADX": r(max(a_valid, key=lambda t: t[1]["adx"])[1]["adx"], 1)} if a_valid else None,
        "เกณฑ์ที่นิยม": 25,
    }

    # ── Linear Regression (บนราคา และบน EMA) ─────────────────────────────────
    e12 = ema(p, MACD_FAST)
    e20 = ema(p, LR_N)

    def lr_snapshot(date):
        i = idx[date]
        o = ols_time(p[i - LR_N + 1:i + 1])
        return {
            "วันที่": date, "ราคา": p[i],
            "slope ต่อวัน": r(o["slope"]), "intercept": r(o["intercept"]),
            "ค่าฟิตปลายหน้าต่าง (LSMA)": r(o["end"]),
            "R2": r(o["r2"], 3), "SD residual": r(o["sd"]),
            "residual วันนี้": r(o["resid"]), "residual เป็นกี่ SD": r(o["resid"] / o["sd"]),
            "t-stat ของ slope": r(o["t"]),
            "ช่องบน +2SD": r(o["end"] + 2 * o["sd"]), "ช่องล่าง −2SD": r(o["end"] - 2 * o["sd"]),
            "SMA20": r(statistics.mean(p[i - LR_N + 1:i + 1])), "EMA20": r(e20[i]),
        }

    def lr_on_ema_snapshot(date):
        i = idx[date]
        oe = ols_time(e12[i - LR_EMA_N + 1:i + 1])
        op = ols_time(p[i - LR_EMA_N + 1:i + 1])
        return {
            "วันที่": date,
            "regression บน EMA12": {"slope ต่อวัน": r(oe["slope"]), "R2": r(oe["r2"], 3)},
            "regression บนราคา": {"slope ต่อวัน": r(op["slope"]), "R2": r(op["r2"], 3)},
        }

    k12 = 2 / (MACD_FAST + 1)
    lr_block = {
        "คำอธิบาย": f"OLS ของราคาบนเวลา หน้าต่าง {LR_N} วัน (Linear Regression Indicator / LSMA / channel) และ OLS ของ EMA12 บนเวลา หน้าต่าง {LR_EMA_N} วัน",
        "หน้าต่างราคา": LR_N, "หน้าต่างบนEMA": LR_EMA_N,
        "แทนค่าวันโฟกัส": lr_snapshot(FOCUS),
        "ก่อนวิ่ง": lr_snapshot("2026-08-15"),
        "วันสุดท้าย": lr_snapshot(days[-1]),
        "regression บน EMA เทียบบนราคา": {
            "วันโฟกัส": lr_on_ema_snapshot(FOCUS),
            "ก่อนวิ่ง": lr_on_ema_snapshot("2026-08-15"),
            "วันสุดท้าย": lr_on_ema_snapshot(days[-1]),
        },
        "ความชัน EMA หนึ่งวันคืออะไร": {
            "วันที่": FOCUS,
            "EMA12 วันนี้ − เมื่อวาน": r(e12[f] - e12[f - 1]),
            "k × (ราคาวันนี้ − EMA12 เมื่อวาน)": r(k12 * (p[f] - e12[f - 1])),
            "k": r(k12, 4),
            "ราคาวันนี้": p[f], "EMA12 เมื่อวาน": r(e12[f - 1]),
        },
        "ความช้าบนเทรนด์เส้นตรง (วัน)": {
            "คำอธิบาย": "ถ้าราคาเป็นเส้นตรงสมบูรณ์ ค่าเฉลี่ยจะตามหลังเส้นนั้นกี่วัน — (n−1)/2 สำหรับ SMA และ EMA(k=2/(n+1)); ปลาย regression = 0",
            "SMA20 / EMA20": (LR_N - 1) / 2, "EMA12": (MACD_FAST - 1) / 2, "EMA26": (MACD_SLOW - 1) / 2, "LSMA20": 0,
        },
    }

    # ── ฐานภายใต้ความสุ่ม (สถานี ②) ───────────────────────────────────────────
    rng = random.Random(SEED)
    sd = daily_sd_pct / 100
    n_days = len(p)
    rsi_hits = rsi_tot = bb_hits = bb_tot = 0
    lr_t_hits = lr_tot = lr_out = 0
    r2_price, r2_ema = [], []
    for _ in range(PATHS):
        q = [p[0]]
        for _ in range(n_days - 1):
            q.append(q[-1] * (1 + rng.gauss(0, sd)))
        for x in rsi_wilder(q):
            if x is not None:
                rsi_tot += 1
                rsi_hits += (x["rsi"] > 70 or x["rsi"] < 30)
        for i, b in enumerate(bollinger(q)):
            if b is not None:
                bb_tot += 1
                bb_hits += (q[i] > b["upper"] or q[i] < b["lower"])
        qe = ema(q, MACD_FAST)
        for i in range(LR_N - 1, n_days):
            o = ols_time(q[i - LR_N + 1:i + 1])
            lr_tot += 1
            lr_t_hits += abs(o["t"]) > 2
            lr_out += abs(o["resid"]) > 2 * o["sd"]
        for i in range(MACD_FAST - 1 + LR_EMA_N - 1, n_days):
            r2_price.append(ols_time(q[i - LR_EMA_N + 1:i + 1])["r2"])
            r2_ema.append(ols_time(qe[i - LR_EMA_N + 1:i + 1])["r2"])
    base_block = {
        "คำอธิบาย": f"จำลองราคาสุ่มล้วน (ไม่มี drift, ความผันผวนรายวันเท่า BTC ชุดนี้) {PATHS} เส้น × {n_days} วัน เมล็ดสุ่ม {SEED}",
        "ความผันผวนรายวันที่ใช้เปอร์เซ็นต์": r(daily_sd_pct, 2),
        "RSI นอก 30/70 ภายใต้ความสุ่มเปอร์เซ็นต์": r(100 * rsi_hits / rsi_tot, 1),
        "ราคานอกแบนด์ ±2σ ภายใต้ความสุ่มเปอร์เซ็นต์": r(100 * bb_hits / bb_tot, 1),
        "regression 20 วัน |t| เกิน 2 ภายใต้ความสุ่มเปอร์เซ็นต์": r(100 * lr_t_hits / lr_tot, 1),
        "ราคานอกช่อง regression ±2SD ภายใต้ความสุ่มเปอร์เซ็นต์": r(100 * lr_out / lr_tot, 1),
        "R2 เฉลี่ย regression 10 วัน": {"บนราคา": r(statistics.mean(r2_price), 3), "บน EMA12": r(statistics.mean(r2_ema), 3)},
        "R2 มัธยฐาน regression 10 วัน": {"บนราคา": r(statistics.median(r2_price), 3), "บน EMA12": r(statistics.median(r2_ema), 3)},
        "หมายเหตุ": "RSI เป็นอัตราส่วน จึงไม่ขึ้นกับระดับความผันผวน — ฐานนี้ใช้ได้กับสินทรัพย์ไหนก็ได้ที่เดินสุ่มแบบสมมาตร แต่จะเปลี่ยนทันทีเมื่อมี drift หรือ autocorrelation · t-stat ของ regression บนราคาที่เดินสุ่มไม่มีความหมายทางสถิติ (spurious regression) ตัวเลขนี้แสดงว่ามันโดนบ่อยแค่ไหน",
    }

    # ── สามเสียงในวันเดียว ────────────────────────────────────────────────────
    focus_block = {
        "วันที่": FOCUS, "ราคา": p[f],
        "สัญญาณ EMA ของ Part 3": "ซื้อ",
        "RSI": r(rf["rsi"], 1),
        "MACD histogram": r(mf["hist"]),
        "pctB": r(bf["pct_b"], 2),
        "ADX ประมาณ": None if af["adx"] is None else r(af["adx"], 1),
        "ราคาวันสุดท้าย": p[-1],
        "เปลี่ยนแปลงถึงวันสุดท้ายเปอร์เซ็นต์": r(100 * (p[-1] / p[f] - 1), 2),
        "จำนวนวันหลังโฟกัส": len(days) - 1 - f,
    }

    return {
        "_อ่านก่อน": "สร้างด้วย tools/indicator_figures.py จาก docs/nq-figures.json (ราคารายวัน BTC ชุดเดียวกับทั้งเล่ม) — ห้ามแก้ด้วยมือ",
        "ช่วงข้อมูล": {"ตั้งแต่": days[0], "ถึง": days[-1], "จำนวนวัน": len(days)},
        "วันโฟกัส": focus_block,
        "RSI": rsi_block,
        "MACD": macd_block,
        "Bollinger": bb_block,
        "ADX": adx_block,
        "LinearRegression": lr_block,
        "ฐานภายใต้ความสุ่ม": base_block,
    }


def math_log(x):
    import math
    return math.log(x)


if __name__ == "__main__":
    data = build()
    with open(OUT, "w") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("เขียน", os.path.relpath(OUT, ROOT))
