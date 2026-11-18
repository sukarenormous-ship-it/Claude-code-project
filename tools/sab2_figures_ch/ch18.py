"""บท 18 เล่ม 2 — ปิดเล่ม: โครงงานของคุณเอง · ค่าทุกตัวของบท (ปลั๊กอินของ tools/sab_figures.py --book sab2)

ตอน ก  แบบอ่านเจ็ดคำถาม: "งานวิจัยจากกลุ่มแชต" ตัวเลขสอน (20 เหรียญ 190 คู่ · Sharpe รายเดือน 0.7 · 12 เดือน · ไม่หักต้นทุน)
       เส้นโชคแบบบท 14 (ผลดีสุดจากโชค ÷ √เดือน) · 🎲 ผู้เขียนที่ไม่มีฝีมือ 30 คน คนละ 190 แบบ × 12 เดือน
       งานจริงสองฉบับและคลังโค้ดหนึ่งชุด: ตัวเลขตามบันทึกค้นคว้า tools/sab_research/practitioner-research.md (ไม่ได้คำนวณ)
ตอน ข  โครงงานของมิน: ลงทะเบียนล่วงหน้า (กติกาที่ตรึงจากบท 1–17 · ช่วงผลที่ช่วงตรวจบอก · การตัดสินใจของแต่ละผล)
       🎲 โลกที่รู้คำตอบ: คู่แบบบท 14 (price_pair φ 0.97) กับโลกไม่มีเชือก (φ 1) 30 โลก · ปีทดสอบ 365 วันหลังช่วงเลือก 731 วัน
       📡 ช่วงทดสอบสุดท้าย — **เปิดครั้งเดียวในไฟล์นี้** (load_closes หนึ่งครั้ง · load_funding หนึ่งครั้ง) แล้วรันเฉพาะกติกาที่ลงทะเบียน:
       การ์ด LTC–DOT (h 3.76 · ไม้บรรทัดช่วงเลือก · เข้า 2 ออก 0.5 ถือไม่เกิน 30 วัน · 10 ชุด · sab2_engine.run)
       funding carry BTC / ETH (Deribit · เดือนละ 30 วัน · แผนภูมิควบคุมของบท 15 เดินต่อเป็นเดือนที่ 13–24)
ตอน ค  รายงานของต้น (ตัวเลขสอนที่แต่งขึ้น · เจ็ดจุดผิดที่ฝังไว้)
ข้อมูลจริงผ่าน sab2_realdata เท่านั้น · สถิติ sab2_stats · โลกจำลอง sab2_sim · backtest sab2_engine
"""

import math
import random
import statistics

import sab2_engine as E
import sab2_realdata as R
import sab2_sim as M
import sab2_stats as S

# ───────── การ์ดที่ตรึงไว้ (บท 7 · 14 · 15) ─────────
ENTER, LEAVE, HOLD, SETS, CAPITAL = 2, 0.5, 30, 10, 1000.0
MONTH = 30                       # เดือนของเล่ม = 30 วัน
WARN_DAYS = 60                   # บรรทัดเตือนของการ์ด (บท 7): |Z| ไม่กลับถึงเส้นออกเลย 60 วันติด → พักเปิดไม้ใหม่
F_DAYS, T_DAYS = 731, 365
SIM_PHI, SIM_SCALE, SIM_COMMON = 0.97, 3.0, 0.015     # โลกคู่แบบบท 14

# ───────── การลงทะเบียนล่วงหน้า (เขียนก่อนรันช่วงทดสอบสุดท้าย · ห้ามแก้หลังเห็นผล) ─────────
PREREG = {
    "การ์ด": {
        "เลื่อนขั้น": "สุทธิ > 0 และ Sharpe รายเดือน ≥ 2 ÷ √12 และบรรทัดเตือน 60 วันไม่ติด → จากกระดาษเป็นเงินจริงขนาดเล็ก",
        "คงกระดาษ": "สุทธิ > 0 แต่ไม่ถึงเส้น หรือบรรทัดเตือนติด → อยู่บนกระดาษอีกหนึ่งปี",
        "ปลด": "สุทธิ ≤ 0 → ปลดการ์ด LTC–DOT (กติกาปลดกลยุทธ์)",
    },
    "funding": {
        "BTC": "เดือนที่ 24 อยู่เหนือเส้นเตือน → เลื่อนจากกระดาษเป็นเงินจริงขนาดเล็ก (ใช้งบร่วมกับ carry) · "
               "ระหว่างเส้นเตือนกับเส้นลงมือ → คงกระดาษ · แตะเส้นลงมือ → หยุด",
        "ETH": "แตะเส้นลงมือ → หยุด · กลับเหนือเส้นเตือนสามเดือนติด → คืนขนาดเต็ม (บนกระดาษ) · นอกนั้นคงครึ่งขนาดบนกระดาษ",
    },
    "carry": "ชุดข้อมูลไม่มีราคา futures ที่มีวันหมดอายุ จึงทดสอบไม่ได้ · คงขนาดเล็กตามเดิม",
}

# ───────── ตอน ก: งานวิจัยจากกลุ่มแชต (ตัวเลขสอนที่แต่งขึ้น) ─────────
PAPER = {"เหรียญ": 20, "เดือน": 12, "Sharpe": 0.7, "ผลก่อนต้นทุน": 40, "ไม้ต่อปี": 120, "คู่ที่เลือก": 5,
         "ค่าธรรมเนียม": 0.05, "fillต่อไม้": 4}
AUTHORS = 30                     # 🎲 ผู้เขียนที่ไม่มีฝีมือ 30 คน (seed 1–30)

# ───────── ตอน ค: รายงานของต้น (ตัวเลขสอนที่แต่งขึ้น) ─────────
TON = {"เหรียญ": 300, "ผล": 62, "Sharpe": 1.1, "เดือนชนะ": 11, "เดือน": 12, "ไม้": 150, "h": 0.03,
       "ราคาP": 2.0, "ราคาQ": 2.1, "คู่ถือ": 5, "ปี": "2025"}


def _r(v, n=2):
    v = round(float(v) + 0.0, n)
    return int(v) if v == int(v) else v


def _normal_best(N, a=-10.0, b=10.0, steps=20000):
    """ผลดีสุดที่คาดได้ของ N ค่าจากการแจกแจงปกติมาตรฐานที่อิสระกัน (สูตรเดียวกับบท 14)"""
    w = (b - a) / steps
    tot = 0.0
    for i in range(steps + 1):
        x = a + i * w
        pdf = math.exp(-x * x / 2) / math.sqrt(2 * math.pi)
        tot += x * N * pdf * S.norm_cdf(x) ** (N - 1) * (0.5 if i in (0, steps) else 1.0)
    return tot * w


def _hurdle(N, months):
    """เส้นโชคแบบบท 14: ผลดีสุดจากโชค (ปัดสองตำแหน่ง) ÷ √เดือน (ปัดสองตำแหน่ง) — คิดจากเลขปัดที่หน้าแสดง"""
    root = _r(math.sqrt(months))
    best = _r(_normal_best(N))
    return {"N": N, "เดือน": months, "ราก": root, "ดีสุดจากโชค": best, "เส้น": _r(best / root)}


def _monthly(eq, cap=CAPITAL):
    """ผลรายเดือน (ทุก 30 วัน) จาก Equity · Sharpe รายเดือน = Mean ÷ SD (ตัวหาร n − 1) · แบบบท 14"""
    pts = [cap] + [eq[t] for t in range(MONTH - 1, len(eq), MONTH)]
    d = [b - a for a, b in zip(pts, pts[1:])]
    sd = S.sd(d)
    return {"เดือน": len(d), "ผล": d, "Mean": S.mean(d), "SD": sd, "Sharpe": S.mean(d) / sd if sd else 0.0}


def _get(data, path, fallback):
    """ค่าจากบทก่อน (ตรวจว่าตรงกับที่คัดลอก) · ถ้ายังไม่มีคีย์ใช้ค่าที่คัดลอก"""
    o = data
    for k in path.split("."):
        if not isinstance(o, dict) or k not in o:
            return fallback
        o = o[k]
    assert o == fallback, f"{path} = {o} ไม่ตรงกับที่คัดลอก {fallback}"
    return o


# ───────────────────────── ตอน ก ─────────────────────────

def _paper():
    p = PAPER
    pairs = p["เหรียญ"] * (p["เหรียญ"] - 1) // 2
    cost_trade = p["fillต่อไม้"] * p["ค่าธรรมเนียม"]                        # 0.2% ของขาต่อไม้
    cost_year = p["ไม้ต่อปี"] * cost_trade
    hd = _hurdle(pairs, p["เดือน"])
    hd1 = _hurdle(1, p["เดือน"])
    # 🎲 ผู้เขียนที่ไม่มีฝีมือ: แต่ละคนลอง 190 แบบ แต่ละแบบได้ผลรายเดือนสุ่มจากการแจกแจงปกติ Mean 0 (ไม่มีฝีมือเลย)
    bests = []
    for seed in M.ROBUST_SEEDS[:AUTHORS]:
        rng = random.Random(1800 + seed)
        best = -9.0
        for _ in range(pairs):
            xs = [rng.gauss(0.0, 1.0) for _ in range(p["เดือน"])]
            best = max(best, S.mean(xs) / S.sd(xs))
        bests.append(best)
    srt = sorted(bests)
    return {**p, "คู่": pairs, "ผ่านปลอมห้าเปอร์เซ็นต์": _r(pairs * 0.05, 1),
            "ต้นทุนต่อไม้": _r(cost_trade), "ต้นทุนต่อปี": _r(cost_year), "หลังต้นทุน": _r(p["ผลก่อนต้นทุน"] - cost_year),
            "ต้นทุนต่อเดือน": _r(cost_year / 12), "ไม้ต่อเดือน": _r(p["ไม้ต่อปี"] / 12),
            "เส้นโชค": hd, "เส้นสองSE": _r(2 / hd["ราก"]), "เส้นโชคแบบเดียว": hd1,
            "โลก": {"คน": AUTHORS, "ดีสุดมัธยฐาน": _r(statistics.median(bests)), "ต่ำสุด": _r(srt[0]),
                    "สูงสุด": _r(srt[-1]), "ถึงที่อ้าง": sum(1 for b in bests if b >= p["Sharpe"]),
                    "ถึงเส้นโชค": sum(1 for b in bests if b >= hd["เส้น"]),
                    "ดีสุด": [_r(b) for b in bests]}}


def _readings():
    """ตัวเลขของสองงานและคลังโค้ด ตามบันทึกค้นคว้า §1.1 · §3.3 · §4 · §6 · §8.3 (ไม่ได้คำนวณ · ปีเป็นข้อความ)"""
    return {"GGR": {"ปี": "2006", "เดือนเลือก": 12, "เดือนเทรด": 6, "เส้นเปิดSD": 2, "คู่บน": 20, "คู่บนน้อย": 5,
                    "ยูทิลิตี้เปอร์เซ็นต์": 71, "ใหญ่สามขั้นเปอร์เซ็นต์": 74, "ผลต่อปีเปอร์เซ็นต์": 11,
                    "รอวันหายต่ำ": 30, "รอวันหายสูง": 55},
            "DoFaff": {"ปี": "2012", "หลังปี": "2002", "แบบ": 29, "ปี2010": "2010", "ไม่บรรจบเปอร์เซ็นต์": 32},
            "AL": {"ปี": "2010", "ฉบับร่างปี": "2009", "หน้าต่าง": 60, "วันกลับ": 30, "kappa": 8.4,
                   "เปิด": 1.25, "ปิดlong": 0.5, "ปิดshort": 0.75},
            "ALab": {"ปีคอมมิต": "2024", "คอมมิต": "32ccd56", "ครึ่งชีวิตสูงสุด": 365, "ข้ามขั้นต่ำ": 12,
                     "hurst": 0.5, "เก็บ": 50, "เลือก": 5, "เส้นเปิด": 2, "ข้ามบน": 10, "EGเปอร์เซ็นต์": 95},
            "Quantopian": {"ปีเก็บถาวร": "2020", "p": 0.05},
            "CK": {"ปี": "2018", "ปีเริ่มแย่": "2010", "ปีจบแย่": "2015"},
            "Rad": {"ปี": "2016", "หลังปี": "2009"},
            "Fil": {"ปี": "2020", "รายวัน": -0.07, "ห้านาที": 11.61, "เหรียญ": 26, "วิธี": 2, "ความถี่": 3},
            "Krauss": {"ปี": "2017", "งาน": 90, "กลุ่ม": 5}, "Palomar": {"บท": 15}}


# ───────────────────────── ตอน ข: ลงทะเบียน · โลกที่รู้คำตอบ ─────────────────────────

def _prereg(data):
    looks = _get(data, "เรื่อง.part17.close.ดูช่วงตรวจรวมเล่ม", 43)
    tests = _get(data, "ch14.นับ.ทดสอบช่วงเลือกรวม", 387)
    hways = _get(data, "ch02.จำนวนวิธีรวม", 7)
    grid = _get(data, "ch14.จริง.แบบ", 25)
    models = _get(data, "ch16.นับรอบ.ดูช่วงตรวจ", 7)
    t3 = _get(data, "ch03.จริง.สี่สิบห้า.คู่", 45)
    t8 = _get(data, "ch08.แปดคู่.ทดสอบสองทิศ", 90)
    t11 = _get(data, "ch11.สแกน.ทดสอบไม่มีLTC", 252)
    assert t3 + t8 + t11 == tests
    pair = data.get("ch15", {}).get("คู่จริง", {})
    gross = _get(data, "ch15.คู่จริง.กำไรก่อนต้นทุน", 193.31)
    sd_trade = _get(data, "ch15.คู่จริง.SDต่อไม้", 153.1)
    root = _get(data, "ch15.คู่จริง.รากไม้", 3.16)
    se = _get(data, "ch15.คู่จริง.SEรวม", 484)
    two = _get(data, "ch15.คู่จริง.สองSEรวม", 968)
    assert pair == {} or (pair["ไม้"] == 10 and pair["สุทธิแอป"] == 180.51)
    root12 = _r(math.sqrt(12))
    return {"ดูช่วงตรวจ": looks, "ทดสอบคัด": tests, "ทดสอบบท3": t3, "ทดสอบบท8": t8, "ทดสอบบท11": t11,
            "วิธีหาh": hways, "ตาราง": grid, "โมเดลสัญญาณ": models,
            "ช่วงการ์ด": {"กำไรก่อนต้นทุน": gross, "SDต่อไม้": sd_trade, "ไม้": 10, "รากไม้": root, "SEรวม": se,
                         "สองSEรวม": two, "ล่าง": _r(gross - two, 0), "บน": _r(gross + two, 0),
                         "สุทธิช่วงตรวจ": _get(data, "ch14.จริง.การ์ด.ตรวจ", 180.51),
                         "สุทธิช่วงเลือก": _get(data, "ch14.จริง.การ์ด.เลือก", 379.38)},
            "เส้นเลื่อนขั้น": {"ราก12": root12, "เส้น": _r(2 / root12)},
            "เส้นโชคหนึ่งแบบ": _r(_normal_best(1)), "เส้นโชคสี่สิบสาม": _hurdle(looks, 12),
            "กติกา": PREREG}


def _sim_card(bar):
    """🎲 โลกคู่แบบบท 14 · ช่วงเลือก 731 วันวัด h (Regression บนราคา) และไม้บรรทัด → การ์ดบนปีถัดไป 365 วัน"""
    sd = SIM_SCALE * math.sqrt(1 - SIM_PHI ** 2)
    out = {}
    for name, phi in (("มีเชือก", SIM_PHI), ("ไม่มีเชือก", 1.0)):
        nets, srs, trades = [], [], []
        for seed in M.ROBUST_SEEDS:
            w = M.price_pair(seed=seed, n=F_DAYS + T_DAYS, h=2, phi=phi, sd=sd, common_sd=SIM_COMMON)
            A, B = w["A"], w["B"]
            fa, fb = A[:F_DAYS], B[:F_DAYS]
            h = round(S.ols(fb, fa)["slope"], 4)
            X = [a - h * b for a, b in zip(fa, fb)]
            m, s = S.mean(X), S.sd(X)
            ta, tb = A[F_DAYS:], B[F_DAYS:]
            z = [(a - h * b - m) / s for a, b in zip(ta, tb)]
            r = E.run(ta, tb, h, z, SETS, enter=ENTER, leave=LEAVE, hold=HOLD)
            nets.append(r["net"])
            srs.append(_monthly(r["equity"])["Sharpe"])
            trades.append(r["trades"])
        srt = sorted(nets)
        out[name] = {"phi": phi, "โลก": len(nets), "มัธยฐาน": _r(statistics.median(nets)), "ต่ำสุด": _r(srt[0]),
                     "สูงสุด": _r(srt[-1]), "บวก": sum(1 for v in nets if v > 0),
                     "ถึงเส้นเลื่อนขั้น": sum(1 for n, s in zip(nets, srs) if n > 0 and _r(s) >= bar),
                     "Sharpeมัธยฐาน": _r(statistics.median(srs)), "ไม้มัธยฐาน": _r(statistics.median(trades), 1),
                     "Sharpeต่ำสุด": _r(min(srs)), "Sharpeสูงสุด": _r(max(srs)),
                     "Sharpeทุกโลก": [_r(v) for v in srs]}
    out["SDนิ่ง"] = _r(SIM_SCALE)
    out["ครึ่งชีวิต"] = _r(S.half_life(SIM_PHI), 1)
    return out


# ───────────────────────── ตอน ข: ช่วงทดสอบสุดท้าย (เปิดครั้งเดียว) ─────────────────────────

def _card_final(data, dates, A, B):
    """การ์ดที่ตรึงไว้บนช่วงทดสอบสุดท้าย · h และไม้บรรทัดจากช่วงเลือก (คิดใหม่จากข้อมูลแล้วตรวจกับบท 14)"""
    _, pf = R.load_closes("formation", coins=["LTC", "DOT"])
    fa, fb = pf["LTC"], pf["DOT"]
    h = round(S.ols(fb, fa)["slope"], 2)
    X = [a - h * b for a, b in zip(fa, fb)]
    m, s = S.mean(X), S.sd(X)
    assert h == _get(data, "ch14.จริง.h", 3.76)
    assert _r(m) == _get(data, "ch14.จริง.Mean", 55.66) and _r(s) == _get(data, "ch14.จริง.SD", 10.18)
    z = [(a - h * b - m) / s for a, b in zip(A, B)]
    r = E.run(A, B, h, z, SETS, enter=ENTER, leave=LEAVE, hold=HOLD)
    mon = _monthly(r["equity"])
    tl = r["trade_list"]
    # บรรทัดเตือนของการ์ด: วันแรกที่ |Z| ไม่ถึงเส้นออกมาแล้ว 60 วันติด (นับเฉพาะในช่วงนี้)
    run_out, flag = 0, None
    for t, v in enumerate(z):
        run_out = run_out + 1 if abs(v) > LEAVE else 0
        if flag is None and run_out >= WARN_DAYS:
            flag = t
    first_in = next((t for t, v in enumerate(z) if abs(v) <= LEAVE), None)
    trades = [{"เข้า": dates[x["t_in"]], "ออก": dates[x["t_out"]], "ทิศ": "short X" if x["side"] < 0 else "long X",
               "ผล": _r(x["pnl"]), "เหตุ": E.REASON_TH[x["reason"]], "Zเข้า": _r(z[x["t_in"] - 1])} for x in tl]
    rows = [(i, x) for i, x in enumerate(tl)]
    best = max(rows, key=lambda p: p[1]["pnl"]) if rows else None
    worst = min(rows, key=lambda p: p[1]["pnl"]) if rows else None
    legs = None
    if tl:                                   # ไม้แรก: แยกเงินทีละขา (ขา LTC = −ทิศ × ชุด × ราคาเปลี่ยน · ขา DOT ตรงข้าม × h)
        x = tl[0]
        side = x["side"]
        a0, a1, b0, b1 = A[x["t_in"]], A[x["t_out"]], B[x["t_in"]], B[x["t_out"]]
        legs = {"LTCเข้า": _r(a0), "LTCออก": _r(a1), "DOTเข้า": _r(b0), "DOTออก": _r(b1),
                "ขาLTC": _r(side * SETS * (a1 - a0)), "ขาDOT": _r(-side * SETS * h * (b1 - b0)),
                "LTCเปลี่ยนเปอร์เซ็นต์": _r(100 * (a1 / a0 - 1), 1), "DOTเปลี่ยนเปอร์เซ็นต์": _r(100 * (b1 / b0 - 1), 1),
                "มูลค่าขาLTC": _r(SETS * a0), "มูลค่าขาDOT": _r(SETS * h * b0)}
    ltc_chg = 100 * (A[-1] / A[0] - 1)
    dot_chg = 100 * (B[-1] / B[0] - 1)
    return {"h": h, "Mean": _r(m), "SD": _r(s), "ชุด": SETS, "DOTต่อชุด": h, "DOTสิบชุด": _r(SETS * h, 1),
            "สุทธิ": _r(r["net"]), "ค่าธรรมเนียม": _r(r["costs"]), "ก่อนต้นทุน": _r(r["net"] + r["costs"]),
            "ไม้": r["trades"], "ชนะ": r["wins"], "ค้าง": abs(r["open"]), "fill": r["fills"],
            "ครบเวลา": sum(1 for x in tl if x["reason"] == "time"), "ถึงเป้า": sum(1 for x in tl if x["reason"] == "target"),
            "Equityต่ำสุด": _r(r["min_equity"]), "ลึกสุด": _r(r["max_drawdown"]), "Equityจบ": _r(r["equity"][-1]),
            "Zเฉลี่ย": _r(S.mean(z)), "Zแรก": _r(z[0]), "Zสุดท้าย": _r(z[-1]), "Zสูงสุด": _r(max(z)), "Zต่ำสุด": _r(min(z)),
            "วันZเกินสอง": sum(1 for v in z if abs(v) >= ENTER), "วันในเส้นออก": sum(1 for v in z if abs(v) <= LEAVE),
            "วันแรกในเส้นออก": dates[first_in] if first_in is not None else None,
            "บรรทัดเตือนวัน": dates[flag] if flag is not None else None, "บรรทัดเตือนติด": flag is not None,
            "บรรทัดเตือนลำดับวัน": (flag + 1) if flag is not None else None,
            "Sharpe": _r(mon["Sharpe"]), "เดือน": mon["เดือน"], "Meanเดือน": _r(mon["Mean"]), "SDเดือน": _r(mon["SD"]),
            "เดือนบวก": sum(1 for v in mon["ผล"] if v > 0), "ผลรายเดือน": [_r(v) for v in mon["ผล"]],
            "ไม้ทั้งหมด": trades, "ไม้ดีสุด": trades[best[0]] if best else None,
            "ไม้แย่สุด": trades[worst[0]] if worst else None,
            "ไม้แรกแยกขา": legs, "สองSDหนึ่งไม้": _r(2 * _get(data, "ch15.คู่จริง.SDต่อไม้", 153.1)),
            "LTCเปลี่ยนเปอร์เซ็นต์": _r(ltc_chg, 1), "DOTเปลี่ยนเปอร์เซ็นต์": _r(dot_chg, 1),
            "LTCแรก": _r(A[0]), "LTCท้าย": _r(A[-1]), "DOTแรก": _r(B[0]), "DOTท้าย": _r(B[-1]),
            "Xแรก": _r(A[0] - h * B[0]), "Xท้าย": _r(A[-1] - h * B[-1]),
            }


def _funding_final(data, rows):
    """funding carry บนช่วงทดสอบสุดท้าย: เดือนละ 30 วัน (% ของมูลค่าที่ถือ) · แผนภูมิควบคุมของบท 15 เดินต่อเดือนที่ 13–24"""
    out = {}
    for coin, inst in (("BTC", "BTC-PERPETUAL"), ("ETH", "ETH-PERPETUAL")):
        by = {}
        for ts, i, rate in rows:
            if i == inst:
                by[ts[:10]] = by.get(ts[:10], 0.0) + rate
        d = [by[k] for k in sorted(by)]
        fin = [100 * sum(d[i:i + MONTH]) for i in range(0, len(d) - MONTH + 1, MONTH)]
        tr = data.get("ch15", {}).get("ติดตามจริง", {}).get(coin)
        val = [float(x) for x in data["ch15"]["เสื่อมจริง"][coin]["เดือนช่วงตรวจ"]]
        mu, sd = float(tr["μ"]), float(tr["σ"])
        path = val + [float(_r(x)) for x in fin]
        cum, chart = 0.0, []
        for n, x in enumerate(path, start=1):
            cum += x
            rt = float(_r(math.sqrt(n)))
            one = float(_r(sd * rt))
            chart.append({"เดือน": n, "ผล": _r(x), "สะสม": _r(cum), "คาด": _r(n * mu), "ราก": _r(rt),
                          "เตือน": _r(n * mu - one), "ลงมือ": _r(n * mu - 2 * one), "สองSDสะสม": _r(2 * one)})
        cums = [sum(path[:k]) for k in range(1, len(path) + 1)]
        under_w = [c < r["เตือน"] for c, r in zip(cums, chart)]
        under_a = [c < r["ลงมือ"] for c, r in zip(cums, chart)]
        first_w = next((r["เดือน"] for r, u in zip(chart, under_w) if u), None)
        first_a = next((r["เดือน"] for r, u in zip(chart, under_a) if u), None)
        assert first_w == tr["เตือนเดือน"] or (first_w is not None and tr["เตือนเดือน"] is not None and first_w <= 12) \
            or (tr["เตือนเดือน"] is None and (first_w is None or first_w > 12))
        # กลับเหนือเส้นเตือนสามเดือนติด (นับเฉพาะเดือนที่ 13–24)
        streak, back3 = 0, None
        for r, u in zip(chart[12:], under_w[12:]):
            streak = 0 if u else streak + 1
            if back3 is None and streak >= 3:
                back3 = r["เดือน"]
        last = chart[-1]
        out[coin] = {"μ": tr["μ"], "σ": tr["σ"], "เดือนทดสอบ": [_r(x) for x in fin], "เดือน": len(fin),
                     "Mean": _r(S.mean(fin)), "SD": _r(S.sd(fin)),
                     "เดือนติดลบ": sum(1 for x in fin if x < 0),
                     "รอบ": len([1 for _, i, _r_ in rows if i == inst]),
                     "รอบติดลบเปอร์เซ็นต์": _r(100 * sum(1 for _, i, x in rows if i == inst and x < 0)
                                               / max(1, len([1 for _, i, _x in rows if i == inst])), 0),
                     "แผนภูมิ": chart, "เตือนเดือนแรก": first_w, "ลงมือเดือนแรก": first_a,
                     "ใต้เตือนเดือน24": under_w[-1], "ใต้ลงมือในปีทดสอบ": any(under_a[12:]),
                     "เดือนใต้เตือนในปีทดสอบ": sum(under_w[12:]), "กลับเหนือเตือนสามเดือน": back3,
                     "ปลายสะสม": last["สะสม"], "ปลายคาด": last["คาด"], "ปลายเตือน": last["เตือน"],
                     "ปลายลงมือ": last["ลงมือ"], "สะสมเดือน12": chart[11]["สะสม"],
                     "ปีทดสอบสะสม": _r(sum(float(_r(x)) for x in fin)),
                     "ช่วงปีคาดล่าง": _r(12 * mu - 2 * float(_r(sd * float(_r(math.sqrt(12)))))),
                     "ช่วงปีคาดบน": _r(12 * mu + 2 * float(_r(sd * float(_r(math.sqrt(12))))))}
    return out


def _final(data):
    """เปิดช่วงทดสอบสุดท้ายครั้งเดียว: ราคาปิดหนึ่งครั้ง (LTC · DOT) · funding หนึ่งครั้ง (Deribit BTC · ETH)"""
    dates, px = R.load_closes("final_test", unlock_final=True, coins=["LTC", "DOT"])
    rows = R.load_funding("final_test", unlock_final=True, venue="deribit")
    card = _card_final(data, dates, px["LTC"], px["DOT"])
    fund = _funding_final(data, rows)
    return {"เริ่ม": dates[0], "จบ": dates[-1], "วัน": len(dates), "การ์ด": card, "funding": fund,
            "ครั้งที่เปิด": 1}


def _decide(pre, card, fund):
    """ใช้กติกาที่ลงทะเบียนไว้ (ไม่มีดุลยพินิจหลังเห็นผล)"""
    bar = pre["เส้นเลื่อนขั้น"]["เส้น"]
    if card["สุทธิ"] <= 0:
        c = "ปลด"
    elif card["Sharpe"] >= bar and not card["บรรทัดเตือนติด"]:
        c = "เลื่อนขั้น"
    else:
        c = "คงกระดาษ"
    b = fund["BTC"]
    if b["ใต้ลงมือในปีทดสอบ"]:
        fb = "หยุด"
    elif not b["ใต้เตือนเดือน24"]:
        fb = "เลื่อนขั้น"
    else:
        fb = "คงกระดาษ"
    e = fund["ETH"]
    if e["ใต้ลงมือในปีทดสอบ"]:
        fe = "หยุด"
    elif e["กลับเหนือเตือนสามเดือน"] is not None:
        fe = "คืนขนาดเต็ม"
    else:
        fe = "คงครึ่ง"
    return {"การ์ด": c, "fundingBTC": fb, "fundingETH": fe, "carry": "คงเล็ก"}


# ───────────────────────── ตอน ค: รายงานของต้น ─────────────────────────

def _ton():
    t = TON
    pairs = t["เหรียญ"] * (t["เหรียญ"] - 1) // 2
    cost_year = t["ไม้"] * PAPER["fillต่อไม้"] * PAPER["ค่าธรรมเนียม"]
    hd = _hurdle(pairs, t["เดือน"])
    q_value = t["h"] * t["ราคาQ"]                                       # มูลค่าขา Q ต่อ P หนึ่งเหรียญ
    return {**t, "คู่": pairs, "เหรียญลบหนึ่ง": t["เหรียญ"] - 1, "ผ่านปลอมห้าเปอร์เซ็นต์": _r(pairs * 0.05, 1), "ต้นทุนต่อปี": _r(cost_year),
            "หลังต้นทุน": _r(t["ผล"] - cost_year), "ไม้ต่อเดือน": _r(t["ไม้"] / 12),
            "ต้นทุนต่อเดือน": _r(t["ไม้"] / 12 * PAPER["fillต่อไม้"] * PAPER["ค่าธรรมเนียม"]),
            "เส้นโชค": hd, "มูลค่าขาQ": _r(q_value), "ขาQเปอร์เซ็นต์": _r(100 * q_value / t["ราคาP"], 1),
            "shortQรวม": t["คู่ถือ"]}


def _days(a, b):
    import datetime as dt
    d0, d1 = dt.date.fromisoformat(a), dt.date.fromisoformat(b)
    return [(d0 + dt.timedelta(days=i)).isoformat() for i in range((d1 - d0).days + 1)]


# ───────────────────────── รวม ─────────────────────────

def extend(data, D, q):
    paper = _paper()
    reads = _readings()
    pre = _prereg(data)
    sim = _sim_card(pre["เส้นเลื่อนขั้น"]["เส้น"])
    fin = _final(data)
    dec = _decide(pre, fin["การ์ด"], fin["funding"])
    ton = _ton()
    fb, fe = fin["funding"]["BTC"]["แผนภูมิ"], fin["funding"]["ETH"]["แผนภูมิ"]
    need24 = _r(fb[23]["เตือน"] - fb[22]["สะสม"])          # ✍️ ข้อ 2: เดือนที่ 24 ต้องได้เท่าไรจึงจบเหนือเส้นเตือน
    card = fin["การ์ด"]
    ex = {"BTCต้องได้เดือน24": need24, "BTCสะสมเดือน23": fb[22]["สะสม"], "BTCเตือน24": fb[23]["เตือน"],
          "BTCได้เดือน24": fb[23]["ผล"], "ETHเตือนเดือนแรก": fin["funding"]["ETH"]["เตือนเดือนแรก"],
          "ETHสะสมเดือน15": fe[14]["สะสม"], "ETHลงมือเดือน15": fe[14]["ลงมือ"],
          "ETHสะสมเดือน14": fe[13]["สะสม"], "ETHลงมือเดือน14": fe[13]["ลงมือ"],
          "คู่นับซ้ำ": PAPER["เหรียญ"] * (PAPER["เหรียญ"] - 1), "ต้นทุนลืมfill": _r(PAPER["ไม้ต่อปี"] * PAPER["ค่าธรรมเนียม"]),
          "BTCผิดเดือน24": _r(fb[23]["เตือน"] - fb[23]["สะสม"]),
          "สามช่วง": [pre["ช่วงการ์ด"]["สุทธิช่วงเลือก"], pre["ช่วงการ์ด"]["สุทธิช่วงตรวจ"], card["สุทธิ"]]}
    drills = [
        {"โจทย์": "(ทำตาม) งานวิจัยจากกลุ่มแชต: จำนวนคู่ ผ่านปลอมที่คาด ต้นทุนต่อปี และเส้นโชค 190 แบบ 12 เดือน",
         "คำตอบ": paper["เส้นโชค"]["เส้น"]},
        {"โจทย์": "(เปลี่ยนเลข · ช่วงทดสอบสุดท้าย) เดือนที่ 24 ของ funding carry BTC ต้องได้เท่าไรจึงจบเหนือเส้นเตือน",
         "คำตอบ": need24},
        {"โจทย์": "(เปลี่ยนเงื่อนไข · ช่วงทดสอบสุดท้าย) ถ้ากติกา ETH คือหยุดเมื่อแตะเส้นเตือน จะหยุดเดือนไหน",
         "คำตอบ": ex["ETHเตือนเดือนแรก"]},
        {"โจทย์": "(ตัดสินใจ · ช่วงทดสอบสุดท้าย) การ์ดบวกทั้งสามช่วง ต้นบอกให้ขยายเป็น 100 ชุด", "คำตอบ": card["ไม้"]},
        {"โจทย์": "(ถ่ายโอน) เติมแบบอ่านเจ็ดคำถามให้งานที่เลือกเอง · ตัวอย่าง Fil และ Kristoufek 2020",
         "คำตอบ": reads["Fil"]["รายวัน"]},
    ]
    d10 = data.get("ch10", {}).get("จริง", {}).get("ตรงทิศ")
    recall = {"เส้นโชคบท14": _get(data, "ch14.จริง.เส้นโชคเลือก.เส้น", 0.4),
              "การ์ดส่วนที่เหลือบท9": _get(data, "ch09.การ์ด.รวม", -1515.1),
              "PC2ข้ามช่วงบท10": d10[1] if d10 else 0.08,
              "ตัวกรองดีสุดบท8": _get(data, "ch08.สเปียร์แมน.rho_ret.ตรึง", 0.17),
              "สายพานผ่านบท8": _get(data, "ch08.สายพานจริง.EG5", 0),
              "BTCETHบท13": _get(data, "ch13.v2.จริง.ผล", -55.53),
              "ICเลือกบท16": _get(data, "ch16.จริง.IC.z.ช่วงเลือก", 0.14),
              "ICตรวจบท16": _get(data, "ch16.จริง.IC.z.ช่วงตรวจ", -0.13),
              "ETHเตือนบท15": _get(data, "ch15.ติดตามจริง.ETH.เตือนเดือน", 6),
              "BTCสะสมบท15": _get(data, "ch15.ติดตามจริง.BTC.ปลายสะสม", 7.35),
              "ETHสะสมบท15": _get(data, "ch15.ติดตามจริง.ETH.ปลายสะสม", 2.62),
              "ครึ่งชีวิตLTCDOTบท4": _get(data, "ch04.จริง.คู่.LTC-DOT.ช่วงเลือก.ครึ่งชีวิต", 22.5),
              "Zตรวจเฉลี่ยบท7": _get(data, "ch07.จริง.LTC-DOT.Zตรวจเฉลี่ย", 2.86),
              "วันช่วงเลือก": F_DAYS,
              "ต้นบท13ก่อน": _get(data, "ch13.v2.ต้น.ผล.ต้นเดิม.ผล", 576.38),
              "ต้นบท13หลัง": _get(data, "ch13.v2.ต้น.ผล.แก้h.ผล", -19.87),
              "ภาคผนวกKเริ่ม": "2025-01-01", "ภาคผนวกKจบ": "2026-11-14"}
    assert d10 is None or d10[1] == 0.08
    try:                                       # ภาคผนวก K ของเล่ม 1 (ช่วงวันที่ผู้อ่านเคยเห็นราคา BTC/ETH)
        import sab_book as SB
        k = SB.load_figures("sab")["realdata"]
        recall["ภาคผนวกKเริ่ม"] = k["แหล่ง"]["แถวแรก"]["วัน"]
        recall["ภาคผนวกKจบ"] = k["แหล่ง"]["วันสุดท้าย"]
        recall["ภาคผนวกKBTCท้าย"] = k["แหล่ง"]["BTCวันสุดท้าย"]
        recall["ภาคผนวกKไม้"] = k["ทดสอบ"]["ไม้"]
    except (KeyError, ImportError):
        pass
    seen = sum(1 for dd in _days(fin["เริ่ม"], fin["จบ"]) if recall["ภาคผนวกKเริ่ม"] <= dd <= recall["ภาคผนวกKจบ"])
    recall["วันที่เคยเห็น"] = seen
    axes = {"ผู้เขียน": [0.5, 1, 1.5, 2, 2.5], "Sharpeโลก": [-0.5, 0, 0.5, 1],
            "funding": [0, 4, 8, 12], "เดือน": [1, 6, 12, 18, 24],
            "แผนที่x": [-800, -400, 0, 400, 800, 1200], "แผนที่y": [-0.5, 0, 0.5, 1]}   # กราฟ sab2-decide-map
    return {"_แบบฝึก": drills, "แกน": axes, "ทวน": recall, "แบบฝึก": ex, "กระดาษ": paper, "อ่าน": reads, "ลงทะเบียน": pre, "โลก": sim, "สุดท้าย": fin, "ตัดสิน": dec, "ต้น": ton}
