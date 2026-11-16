"""บท 13 เล่ม 2 — เครื่อง backtest ของตัวเอง · ค่าทุกตัวของบท (ปลั๊กอินของ tools/sab_figures.py --book sab2)

ตอน ก  วงห้าขั้นด้วยมือ 10 วันบนคู่ A–B ของเล่ม 1 (X = A − 2B · ไม้บรรทัด Mean 0 SD 1 จากบท 9 เล่ม 1)
ตอน ข  สเปรดชีตของต้น: โลกจำลองที่รู้คำตอบ (ไม่มีเชือกที่เก็บได้) + Look-ahead Bias สามแบบ แก้ทีละจุด
ตอน ค  เครื่องเดียวกันบน BTC–ETH ช่วงเลือก → ช่วงตรวจ (ไม่แตะช่วงทดสอบสุดท้าย) · โลกจำลองคู่กัน · Survivorship

เครื่อง _backtest / _trades = tools/sab2_engine.run (เท่าลูปในบล็อก 💻 ของ docs/sab2-part13.html ทุกบิต — ตรวจใน selftest ของเครื่อง)
ข้อมูลจริงผ่าน sab2_realdata.load_closes เท่านั้น · สถิติผ่าน sab2_stats · โลกจำลองผ่าน sab2_sim (seed ระบุทุกที่)
"""

import math
import statistics

import sab2_engine as E
import sab2_realdata as R
import sab2_sim as M
import sab2_stats as S

FEE = 0.0005          # 0.05% ของมูลค่าต่อ fill (ฐานต้นทุนเดียวของเล่ม 1 บท 11)
ENTER, LEAVE, HOLD = 2, 0.5, 30
CAPITAL = 1000.0      # ทุนคู่ของเล่ม 1
F_SIM, T_SIM = 250, 360       # โลกจำลอง: 250 วันก่อนหน้า + 360 วัน (12 "เดือน" × 30 วัน) ของสเปรดชีต
TON_SEED, TON_RW, TON_NOISE = 14, 0.003, 0.015
SURV_DAYS, SURV_DROP, SURV_SEEDS = 731, 0.5, list(range(1, 101))   # 100 เหรียญจำลอง 731 วัน (ยาวเท่าช่วงเลือก) · หลุดรายชื่อเมื่อเหลือครึ่งของราคาเริ่ม
SIM_SETS = 5          # โลกจำลอง: 5 ชุด (ขา C ราว 1,000 แบบคู่ A–B ของเล่ม 1)


def _backtest(A, B, h, z, sets, lag=1, fee=FEE, enter=ENTER, leave=LEAVE, hold=HOLD):
    """เครื่องห้าขั้น = tools/sab2_engine.run (selftest ของเครื่องยืนยันว่าเท่าลูปในบล็อก 💻 ของหน้าทุกบิต)
    held: +1 = long X · −1 = short X · fill ที่ราคาปิดวัน t จากสัญญาณวัน t − lag · คืน (Equity รายวัน, จำนวน fill)"""
    r = E.run(A, B, h, z, sets, capital=CAPITAL, lag=lag, fee=fee, enter=enter, leave=leave, hold=hold)
    return r["equity"], r["fills"]


def _trades(A, B, h, z, sets, lag=1, fee=FEE):
    """เครื่องเดิมแต่คืนทุก fill: (วัน, ทิศใหม่, ราคา A, ราคา B, ค่าธรรมเนียม, เงินสดหลัง, เหตุ) และกำไรต่อไม้ที่ปิด"""
    r = E.run(A, B, h, z, sets, capital=CAPITAL, lag=lag, fee=fee, enter=ENTER, leave=LEAVE, hold=HOLD)
    fills = [{"t": f["t"], "ทิศ": f["side"], "A": f["A"], "B": f["B"], "ค่าธรรมเนียม": f["fee"], "เงินสด": f["cash"],
              "เหตุ": E.REASON_TH[f["reason"]], "z_ที่ใช้": f["signal"]} for f in r["fill_list"]]
    return fills, [(x["t_out"], x["pnl"]) for x in r["trade_list"]]


def _ruler(A, B, h):
    X = [a - h * b for a, b in zip(A, B)]
    return S.mean(X), S.sd(X)


def _zs(A, B, h, m, s):
    return [(a - h * b - m) / s for a, b in zip(A, B)]


# ───────────────────────── ตอน ก: สิบวันด้วยมือ ─────────────────────────

HAND_B = [50, 51, 52, 51.5, 51, 50, 49.5, 50, 50.5, 49]
HAND_X = [0.6, 1.4, 2.3, 2.0, 1.6, 1.1, 0.4, 0.7, -0.5, -1.2]


def _hand(q):
    B = HAND_B
    A = [round(2 * b + x, 2) for b, x in zip(B, HAND_X)]
    X = [round(a - 2 * b, 2) for a, b in zip(A, B)]
    sets = 10
    eq, n = _backtest(A, B, 2, X, sets, lag=1)
    eq0, n0 = _backtest(A, B, 2, X, sets, lag=0)
    fills, _ = _trades(A, B, 2, X, sets, lag=1)
    fills0, _ = _trades(A, B, 2, X, sets, lag=0)
    e, x = fills
    e0, x0 = fills0
    days = []
    for t in range(10):
        days.append({"วัน": t + 1, "A": q(A[t], 2), "B": q(B[t], 2), "X": q(X[t], 2), "Equity": q(eq[t], 2),
                     "Equity_ต้น": q(eq0[t], 2)})
    notional_in = 10 * e["A"] + 20 * e["B"]
    notional_out = 10 * x["A"] + 20 * x["B"]
    fee_in, fee_out = q(FEE * notional_in, 2), q(FEE * notional_out, 2)
    fee0_in, fee0_out = q(FEE * (10 * e0["A"] + 20 * e0["B"]), 2), q(FEE * (10 * x0["A"] + 20 * x0["B"]), 2)
    gain = q(10 * (X[e["t"]] - X[x["t"]]), 2)
    gain0 = q(10 * (X[e0["t"]] - X[x0["t"]]), 2)
    cash_after_in = q(CAPITAL + 10 * e["A"] - 20 * e["B"] - fee_in, 2)
    return {
        "วัน": days,
        "ชุด": sets, "h": 2, "ถือA": -sets, "ถือB": 2 * sets,
        "สัญญาณเข้า": {"วัน": e["t"], "X": q(X[e["t"] - 1], 2)},            # สัญญาณจากวันก่อน fill หนึ่งวัน
        "fillเข้า": {"วัน": e["t"] + 1, "A": q(e["A"], 2), "B": q(e["B"], 2), "X": q(X[e["t"]], 2),
                     "ขายA": q(10 * e["A"], 2), "ซื้อB": q(20 * e["B"], 2), "มูลค่ารวม": q(notional_in, 2),
                     "ค่าธรรมเนียม": fee_in, "เงินสดรับสุทธิ": q(10 * e["A"] - 20 * e["B"], 2),
                     "เงินสดหลัง": cash_after_in},
        "สัญญาณออก": {"วัน": x["t"], "X": q(X[x["t"] - 1], 2)},
        "fillออก": {"วัน": x["t"] + 1, "A": q(x["A"], 2), "B": q(x["B"], 2), "X": q(X[x["t"]], 2),
                    "ซื้อคืนA": q(10 * x["A"], 2), "ขายB": q(20 * x["B"], 2), "มูลค่ารวม": q(notional_out, 2),
                    "ค่าธรรมเนียม": fee_out, "เงินสดจ่ายสุทธิ": q(10 * x["A"] - 20 * x["B"], 2),
                    "เงินสดหลัง": q(cash_after_in - (10 * x["A"] - 20 * x["B"]) - fee_out, 2)},
        "ค่าธรรมเนียมรวม": q(fee_in + fee_out, 2),
        "ได้จากX": gain, "Xลด": q(X[e["t"]] - X[x["t"]], 2),
        "สุทธิ": q(gain - fee_in - fee_out, 2),
        "Equityจบ": q(eq[-1], 2), "จำนวนfill": n,
        "ต้น": {"เข้าX": q(X[e0["t"]], 2), "ออกX": q(X[x0["t"]], 2), "ได้จากX": gain0, "Xลด": q(X[e0["t"]] - X[x0["t"]], 2),
                "ค่าธรรมเนียม": [fee0_in, fee0_out], "ค่าธรรมเนียมรวม": q(fee0_in + fee0_out, 2),
                "สุทธิ": q(gain0 - fee0_in - fee0_out, 2), "Equityจบ": q(eq0[-1], 2),
                "ต่าง": q(eq0[-1] - eq[-1], 2), "ต่างเข้า": q(10 * (X[e0["t"]] - X[e["t"]]), 2),
                "ต่างออก": q(10 * (X[x["t"]] - X[x0["t"]]), 2),
                "เข้าA": q(e0["A"], 2), "เข้าB": q(e0["B"], 2), "ออกA": q(x0["A"], 2), "ออกB": q(x0["B"], 2)},
        "เช็กปลายวัน4": q(cash_after_in - 10 * e["A"] + 20 * e["B"], 2),
        "คิดEquityวัน6": {"ขาA": q(10 * A[5], 2), "ขาB": q(20 * B[5], 2)},
        "ผิดลืมค่าธรรมเนียม": q(CAPITAL + 10 * e["A"] - 20 * e["B"], 2),
        "แย่ลง01": {"เข้า": q(0.001 * notional_in, 2), "ออก": q(0.001 * notional_out, 2),
                    "รวม": q(0.001 * notional_in, 2) + q(0.001 * notional_out, 2),
                    "สุทธิ": q(q(gain - fee_in - fee_out, 2) - q(0.001 * notional_in, 2) - q(0.001 * notional_out, 2), 2)},
        "แบบฝึก": _hand_drills(A, B, X, q),
    }


def _hand_drills(A, B, X, q):
    """ข้อ 2: ราคาปิดวันที่ 8 ของ A เป็น 100.2 (X 0.2) · ข้อ 3: fill ช้าสองวัน (สัญญาณวัน t ได้ราคาวัน t + 2)"""
    A2 = list(A)
    A2[7] = 100.2
    X2 = [round(a - 2 * b, 2) for a, b in zip(A2, B)]
    eq2, _ = _backtest(A2, B, 2, X2, 10, lag=1)
    out_n2 = 10 * A2[7] + 20 * B[7]
    eq3, _ = _backtest(A, B, 2, X, 10, lag=2)
    f3, _ = _trades(A, B, 2, X, 10, lag=2)
    e3, x3 = f3
    n_in3, n_out3 = 10 * e3["A"] + 20 * e3["B"], 10 * x3["A"] + 20 * x3["B"]
    return {"ข้อ2": {"A8": 100.2, "X8": q(X2[7], 2), "ซื้อคืนA": q(10 * A2[7], 2), "มูลค่ารวม": q(out_n2, 2),
                     "ค่าธรรมเนียม": q(FEE * out_n2, 2), "ได้จากX": q(10 * (X2[3] - X2[7]), 2),
                     "สุทธิ": q(eq2[-1] - CAPITAL, 2), "Equityจบ": q(eq2[-1], 2)},
            "ข้อ3": {"วันเข้า": e3["t"] + 1, "Xเข้า": q(X[e3["t"]], 2), "วันออก": x3["t"] + 1, "Xออก": q(X[x3["t"]], 2),
                     "ค่าธรรมเนียมเข้า": q(FEE * n_in3, 2), "ค่าธรรมเนียมออก": q(FEE * n_out3, 2),
                     "มูลค่าเข้า": q(n_in3, 2), "มูลค่าออก": q(n_out3, 2),
                     "ได้จากX": q(10 * (X[e3["t"]] - X[x3["t"]]), 2), "สุทธิ": q(eq3[-1] - CAPITAL, 2),
                     "Equityจบ": q(eq3[-1], 2)}}


# ───────────────────────── ตอน ข: สเปรดชีตของต้น (โลกจำลอง) ─────────────────────────

def _ton_world(seed=TON_SEED, n=F_SIM + T_SIM):
    """ไม่มีเชือกที่เก็บได้: ระยะห่าง log เดินสุ่มช้า ๆ (SD 0.3% ต่อวัน) + แรงสะบัดรายวัน 1.5% ที่หายไปในวันเดียว (φ 0)
    ราคา C ≈ 100 · D ≈ 50 · ใช้ random_walk_pair กับ stationary_pair(φ = 0) seed + 500 เป็นแรงสะบัด"""
    w = M.random_walk_pair(seed=seed, n=n, sd=TON_RW)
    noise = M.stationary_pair(seed=seed + 500, n=n, phi=0.0, sd=TON_NOISE)["X"]
    return {"A": [math.exp(v + e) for v, e in zip(w["logA"], noise)], "B": w["B"], "seed": seed}


def _four_versions(w, sets=SIM_SETS):
    """ต้นเดิม → แก้ fill → แก้ไม้บรรทัด → แก้ h (= เครื่องซื่อ) · คืนผลแต่ละแบบ + ค่าที่ใช้"""
    A, B = w["A"], w["B"]
    fA, fB, tA, tB = A[:F_SIM], B[:F_SIM], A[F_SIM:], B[F_SIM:]
    r2 = lambda x: round(x, 2)  # noqa: E731  (ชีตแสดงและใช้ค่าที่ปัดสองตำแหน่ง ผู้อ่านคิดซ้ำได้ตรง)
    hT = r2(S.ols(tB, tA)["slope"])
    hF = r2(S.ols(fB, fA)["slope"])
    mT, sT = map(r2, _ruler(tA, tB, hT))
    mFT, sFT = map(r2, _ruler(fA, fB, hT))
    mF, sF = map(r2, _ruler(fA, fB, hF))
    cfg = [("ต้นเดิม", hT, mT, sT, 0), ("แก้fill", hT, mT, sT, 1), ("แก้ไม้บรรทัด", hT, mFT, sFT, 1), ("แก้h", hF, mF, sF, 1)]
    out = {}
    for name, h, m, s, lag in cfg:
        z = _zs(tA, tB, h, m, s)
        eq, n = _backtest(tA, tB, h, z, sets, lag=lag)
        fills, closed = _trades(tA, tB, h, z, sets, lag=lag)
        months = [0.0] * 12
        cnt = [0] * 12
        for t, pnl in closed:
            months[t // 30] += pnl
            cnt[t // 30] += 1
        out[name] = {"h": h, "m": m, "s": s, "lag": lag, "eq": eq, "n": n, "z": z, "fills": fills, "closed": closed,
                     "เดือน": months, "ไม้ต่อเดือน": cnt}
    return out


def _ton(q):
    w = _ton_world()
    v = _four_versions(w)
    A, B = w["A"][F_SIM:], w["B"][F_SIM:]
    ton = v["ต้นเดิม"]
    keys = ["ต้นเดิม", "แก้fill", "แก้ไม้บรรทัด", "แก้h"]
    res = {k: {"ผล": q(v[k]["eq"][-1] - CAPITAL, 2), "fill": v[k]["n"], "ไม้ปิด": len(v[k]["closed"]),
               "ไม้ชนะ": sum(1 for _, p in v[k]["closed"] if p > 0),
               "เดือนมีไม้ปิด": sum(1 for c in v[k]["ไม้ต่อเดือน"] if c),
               "เดือนขาดทุน": sum(1 for p, c in zip(v[k]["เดือน"], v[k]["ไม้ต่อเดือน"]) if c and p < 0)} for k in keys}
    months = [{"เดือน": i + 1, "ไม้": ton["ไม้ต่อเดือน"][i], "กำไร": q(ton["เดือน"][i], 2)} for i in range(12)]
    # แถวตัวอย่างรอบไม้แรกของต้น: วันก่อนสัญญาณ · วันสัญญาณ · วันถัดไป
    f0 = ton["fills"][0]
    t0 = f0["t"]
    hT, mT, sT = ton["h"], ton["m"], ton["s"]
    rows = []
    for t in range(t0 - 1, t0 + 3):
        pa, pb = round(A[t], 2), round(B[t], 2)          # ชีตแสดงราคาสองตำแหน่ง → X และ Z คิดซ้ำจากตัวเลขที่เห็นได้ตรง
        X = round(pa - hT * pb, 2)
        rows.append({"วัน": t + 1, "P": q(pa, 2), "Q": q(pb, 2), "QคูณH": q(hT * pb, 2), "X": q(X, 2),
                     "ห่างMean": q(X - mT, 2), "Z": q((X - mT) / sT, 2)})
    sig = rows[1]
    nxt = rows[2]
    fx = ton["fills"][1]          # ไม้แรกปิด
    honest_fill_X = q(A[t0 + 1] - hT * B[t0 + 1], 2)
    # ราคาเข้าออกไม้แรกของต้นเทียบกับ fill วันถัดไป (h และไม้บรรทัดเดิม)
    # ── 30 โลก (seed 1–30) ──
    agg = {k: [] for k in keys}
    fees_h, gross_h = [], []      # เครื่องที่ซื่อครบ: ค่าธรรมเนียมรวมต่อโลก และผลก่อนค่าธรรมเนียม (ไว้เทียบว่า Median ≈ −ค่าธรรมเนียม)
    mono = 0
    for sd in M.ROBUST_SEEDS:
        vv = _four_versions(_ton_world(seed=sd))
        r = [vv[k]["eq"][-1] - CAPITAL for k in keys]
        for k, x in zip(keys, r):
            agg[k].append(x)
        fh = sum(f["ค่าธรรมเนียม"] for f in vv["แก้h"]["fills"])
        fees_h.append(fh)
        gross_h.append(r[-1] + fh)
    many = {k: {"มัธยฐาน": q(statistics.median(agg[k]), 2), "บวก": sum(1 for x in agg[k] if x > 0),
                "ต่ำสุด": q(min(agg[k]), 2), "สูงสุด": q(max(agg[k]), 2)} for k in keys}
    p_pos = many["แก้h"]["บวก"] / len(M.ROBUST_SEEDS)
    return {
        "seed": TON_SEED, "วันในชีต": T_SIM, "วันก่อนหน้า": F_SIM, "แรงเดินสุ่มเปอร์เซ็นต์": q(TON_RW * 100, 1),
        "แรงสะบัดเปอร์เซ็นต์": q(TON_NOISE * 100, 1),
        "hต้น": q(hT, 2), "Meanต้น": q(mT, 2), "SDต้น": q(sT, 2),
        "hก่อนหน้า": q(v["แก้h"]["h"], 2), "Meanก่อนหน้า": q(v["แก้h"]["m"], 2), "SDก่อนหน้า": q(v["แก้h"]["s"], 2),
        "Meanก่อนหน้า_hต้น": q(v["แก้ไม้บรรทัด"]["m"], 2), "SDก่อนหน้า_hต้น": q(v["แก้ไม้บรรทัด"]["s"], 2),
        "ผล": res, "เดือน": months,
        "แถว": rows, "วันสัญญาณ": sig["วัน"], "Xสัญญาณ": sig["X"], "Zสัญญาณ": sig["Z"],
        "Xวันถัดไป": nxt["X"], "Zวันถัดไป": nxt["Z"], "ทิศไม้แรก": "short" if f0["ทิศ"] < 0 else "long",
        "ไม้แรกออกวัน": fx["t"] + 1, "Xออกไม้แรก": q(xo := round(round(A[fx["t"]], 2) - hT * round(B[fx["t"]], 2), 2), 2),
        "ไม้แรกต้นได้จากX": q(SIM_SETS * (sig["X"] - xo), 2), "ไม้แรกต้นXลด": q(sig["X"] - xo, 2),
        "ไม้แรกต่างวันเข้า": q(SIM_SETS * (sig["X"] - nxt["X"]), 2), "ไม้แรกXต่างวันเข้า": q(sig["X"] - nxt["X"], 2),
        "Xfillซื่อ": honest_fill_X,
        "สามสิบโลก": many, "วันที่เหลือหลังไม้แรก": T_SIM - sig["วัน"], "แกนกราฟ": [0, 200, 400, 600],
        "สัดส่วนโลกไม่มีเชือกที่บวก": q(p_pos * 100, 0),
        "ซื่อครบ": {"ค่าธรรมเนียมมัธยฐาน": q(statistics.median(fees_h), 2),
                    "ก่อนค่าธรรมเนียมมัธยฐาน": q(statistics.median(gross_h), 2)},
        "_p": p_pos,
    }


# ───────────────────────── ตอน ค: ข้อมูลจริง BTC–ETH ─────────────────────────

def _real(q):
    df, pf = R.load_closes("formation", coins=["BTC", "ETH"])
    dv, pv = R.load_closes("validation", coins=["BTC", "ETH"])
    fA, fB, A, B = pf["BTC"], pf["ETH"], pv["BTC"], pv["ETH"]
    reg = S.ols(fB, fA)
    h = round(reg["slope"])
    m, s = _ruler(fA, fB, h)
    z = _zs(A, B, h, m, s)
    sets = 0.01
    eq, n = _backtest(A, B, h, z, sets)
    fills, closed = _trades(A, B, h, z, sets)
    fees = sum(f["ค่าธรรมเนียม"] for f in fills)
    # ทั้งช่วงเลือก + ช่วงตรวจ (ไม่แตะช่วงทดสอบสุดท้าย) สำหรับเวอร์ชันโกง
    FA, FB = fA + A, fB + B
    hFV = round(S.ols(FB, FA)["slope"])
    mFV, sFV = _ruler(FA, FB, hFV)
    mF_hFV, sF_hFV = _ruler(fA, fB, hFV)
    ver = {}
    for name, hh, mm, ss, lag in [("ต้นเดิม", hFV, mFV, sFV, 0), ("แก้fill", hFV, mFV, sFV, 1),
                                  ("แก้ไม้บรรทัด", hFV, mF_hFV, sF_hFV, 1), ("แก้h", h, m, s, 1)]:
        zz = _zs(A, B, hh, mm, ss)
        e2, n2 = _backtest(A, B, hh, zz, sets, lag=lag)
        ver[name] = {"ผล": q(e2[-1] - CAPITAL, 2), "fill": n2, "ต่ำสุด": q(min(e2), 2), "h": hh}
    eq_ton, _ = _backtest(A, B, hFV, _zs(A, B, hFV, mFV, sFV), sets, lag=0)
    lag2, _ = _backtest(A, B, h, z, sets, lag=2)
    fee3, _ = _backtest(A, B, h, z, sets, fee=FEE * 3)
    nofee, _ = _backtest(A, B, h, z, sets, fee=0.0)
    # ในช่วงเลือกเอง (ในตัวอย่าง: ไม้บรรทัดวัดจากข้อมูลเดียวกัน)
    zf = _zs(fA, fB, h, m, s)
    eqf, nf = _backtest(fA, fB, h, zf, sets)
    tmin = min(range(len(eq)), key=lambda t: eq[t])
    zmax_t = max(range(len(z)), key=lambda t: z[t])
    sample = []
    for f in fills[:4]:
        t = f["t"]
        sample.append({"วันสัญญาณ": dv[t - 1], "Zสัญญาณ": q(f["z_ที่ใช้"], 2), "วันfill": dv[t],
                       "BTC": q(f["A"], 2), "ETH": q(f["B"], 2), "ทำ": f["เหตุ"],
                       "ทิศ": {1: "long X", -1: "short X", 0: "ปิด"}[f["ทิศ"]],
                       "ค่าธรรมเนียม": q(f["ค่าธรรมเนียม"], 2), "Equity": q(eq[t], 2)})
    tz = zmax_t
    x24, x29 = A[tz] - h * B[tz], A[tz] - hFV * B[tz]
    peak = {"วัน": dv[tz], "BTC": q(A[tz], 2), "ETH": q(B[tz], 2), "ETHคูณh": q(h * B[tz], 2), "X": q(x24, 2),
            "ห่างMean": q(x24 - m, 2), "Z": q(z[tz], 2), "Zลืมลบ": q(x24 / s, 2), "ETHคูณhต้น": q(hFV * B[tz], 2), "Xต้น": q(x29, 2),
            "ห่างMeanต้น": q(x29 - mFV, 2), "Zต้น": q((x29 - mFV) / sFV, 2)}
    first = fills[0]
    notional0 = sets * first["A"] + sets * h * first["B"]
    return {
        "ช่วงเลือก": {"เริ่ม": df[0], "จบ": df[-1], "วัน": len(df)},
        "ช่วงตรวจ": {"เริ่ม": dv[0], "จบ": dv[-1], "วัน": len(dv)},
        "hถดถอย": q(reg["slope"], 2), "h": h, "Mean": q(m, 2), "SD": q(s, 2),
        "เส้นเข้าบน": q(m + 2 * s, 2), "เส้นเข้าล่าง": q(m - 2 * s, 2),
        "สองเท่าSDปัด": q(2 * q(s, 2), 2),                                   # หน้าแสดงการคิดจากเลขปัดที่ผู้อ่านเห็น
        "เส้นเข้าบนจากเลขปัด": q(q(m, 2) + 2 * q(s, 2), 2), "เส้นเข้าล่างจากเลขปัด": q(q(m, 2) - 2 * q(s, 2), 2),
        "ชุด": sets, "BTCต่อชุด": sets, "ETHต่อชุด": q(sets * h, 2),
        "Zต่ำสุด": q(min(z), 2), "Zสูงสุด": q(max(z), 2), "วันZสูงสุด": dv[zmax_t],
        "วันที่Zเกิน2": sum(1 for x in z if abs(x) >= ENTER),
        "วันแรก": {"วัน": dv[0], "BTC": q(A[0], 2), "ETH": q(B[0], 2), "ETHคูณh": q(h * B[0], 2), "X": q(A[0] - h * B[0], 2),
                   "ห่างMean": q(A[0] - h * B[0] - m, 2), "Z": q(z[0], 2)},
        "fillแรก": {"ขาBTC": q(sets * fills[0]["A"], 2), "ขาETH": q(sets * h * fills[0]["B"], 2)},
        "fill": n, "ไม้ปิด": len(closed), "ไม้ค้างตอนจบ": n - 2 * len(closed), "ไม้ชนะ": sum(1 for _, p in closed if p > 0),
        "ออกเพราะเวลา": sum(1 for f in fills if f["เหตุ"] == "เวลา"),
        "ค่าธรรมเนียมรวม": q(fees, 2), "ผล": q(eq[-1] - CAPITAL, 2), "Equityจบ": q(eq[-1], 2),
        "Equityต่ำสุด": q(eq[tmin], 2), "วันEquityต่ำสุด": dv[tmin], "ลดลงมากสุด": q(CAPITAL - eq[tmin], 2),
        "ก่อนค่าธรรมเนียม": q(nofee[-1] - CAPITAL, 2),
        "fillช้าสองวัน": q(lag2[-1] - CAPITAL, 2), "ค่าธรรมเนียมสามเท่า": q(fee3[-1] - CAPITAL, 2),
        "ค่าธรรมเนียมสามเท่าเปอร์เซ็นต์": q(FEE * 300, 2),
        "มูลค่าไม้แรก": q(notional0, 2), "ค่าธรรมเนียมไม้แรก": q(first["ค่าธรรมเนียม"], 2),
        "hทั้งสองช่วง": hFV, "Meanทั้งสองช่วง": q(mFV, 2), "SDทั้งสองช่วง": q(sFV, 2),
        "เวอร์ชัน": ver,
        "ในช่วงเลือก": {"ผล": q(eqf[-1] - CAPITAL, 2), "fill": nf},
        "ตัวอย่าง": sample, "วันสูงสุด": peak,
        "แกนกราฟ": [600, 800, 1000, 1200], "ป้ายวันกราฟ": [0, 13, 26, 39, 52],
        "BTCต่ำสุดช่วงตรวจ": q(min(A), 2), "BTCสูงสุดช่วงตรวจ": q(max(A), 2),
        "ต่ำสุดรายสัปดาห์": q(min(eq[::7]), 2),
        "เส้นมูลค่า": {"ซื่อ": [q(x, 2) for x in eq[::7]] + [q(eq[-1], 2)],
                       "ต้นเดิม": [q(x, 2) for x in eq_ton[::7]] + [q(eq_ton[-1], 2)],
                       "วัน": dv[::7] + [dv[-1]]},
        "_eq": eq, "_dates": dv,
    }


def _worlds(q):
    """โลกที่รู้คำตอบคู่กับข้อมูลจริง: มีเชือก φ 0.9 · เชือกขาดตั้งแต่วันแรกของช่วงเทรด · ไม่มีเชือกที่เก็บได้ (โลกของต้น)"""
    def honest(w):
        A, B = w["A"], w["B"]
        h = S.ols(B[:F_SIM], A[:F_SIM])["slope"]
        m, s = _ruler(A[:F_SIM], B[:F_SIM], h)
        z = _zs(A[F_SIM:], B[F_SIM:], h, m, s)
        eq, n = _backtest(A[F_SIM:], B[F_SIM:], h, z, SIM_SETS)
        return {"ผล": eq[-1] - CAPITAL, "ต่ำสุด": min(eq), "zmax": max(abs(x) for x in z)}
    out = {}
    for name, world in [("มีเชือก", lambda sd: M.stationary_pair(seed=sd, n=F_SIM + T_SIM, phi=0.9)),
                        ("เชือกขาด", lambda sd: M.broken_pair(seed=sd, n=F_SIM + T_SIM, break_at=F_SIM, phi_before=0.9,
                                                              phi_after=1.0))]:
        vals = [honest(world(sd)) for sd in M.ROBUST_SEEDS]
        out[name] = {"มัธยฐาน": q(statistics.median(v["ผล"] for v in vals), 2),
                     "บวก": sum(1 for v in vals if v["ผล"] > 0),
                     "มัธยฐานต่ำสุดEquity": q(statistics.median(v["ต่ำสุด"] for v in vals), 2),
                     "มัธยฐานZสูงสุด": q(statistics.median(v["zmax"] for v in vals), 2)}
    return out


def _survivors(q):
    """100 เหรียญจำลอง (ราคาเริ่ม 50 · เดินสุ่ม SD 3% ต่อวัน ไม่มีใครเก่งกว่าใคร · seed 1–100)
    หลุดรายชื่อ "เหรียญใหญ่" เมื่อราคาเคยลงเหลือไม่ถึงครึ่งของราคาเริ่ม"""
    ratios, alive = [], []
    for sd in SURV_SEEDS:
        b = M.random_walk_pair(seed=sd, n=SURV_DAYS)["B"]
        start = b[0]
        dead = min(b) < SURV_DROP * start
        ratios.append(b[-1] / start)
        alive.append(not dead)
    surv = [r for r, a in zip(ratios, alive) if a]
    return {"เหรียญ": len(ratios), "ถูกถอด": len(ratios) - len(surv), "รอด": len(surv),
            "เกณฑ์ถอดเปอร์เซ็นต์": q(SURV_DROP * 100, 0), "วัน": SURV_DAYS,
            "มัธยฐานทุกเหรียญ": q(statistics.median(ratios), 2), "มัธยฐานเฉพาะที่รอด": q(statistics.median(surv), 2),
            "บวกทุกเหรียญ": sum(1 for r in ratios if r > 1), "บวกเฉพาะที่รอด": sum(1 for r in surv if r > 1)}


def extend(data, D, q):
    hand = _hand(q)
    ton = _ton(q)
    real = _real(q)
    worlds = _worlds(q)
    surv = _survivors(q)
    p = ton.pop("_p")
    real.pop("_eq")
    real.pop("_dates")
    runs = 6          # สี่แบบในตารางของตอน ค + fill ช้าสองวัน + ค่าธรรมเนียมสามเท่า (ทุกครั้งที่รันกับช่วงตรวจ = หนึ่งครั้ง)
    snoop = {"ครั้งที่ดูช่วงตรวจ": runs, "ครั้งถัดไป": runs + 1, "โอกาสบวกต่อครั้งเปอร์เซ็นต์": q(p * 100, 0),
             "โอกาสมีอย่างน้อยหนึ่งครั้งบวกเปอร์เซ็นต์": q((1 - (1 - p) ** runs) * 100, 0),
             "สิบครั้งเปอร์เซ็นต์": q((1 - (1 - p) ** 10) * 100, 0)}
    consts = {"ค่าธรรมเนียมเปอร์เซ็นต์": q(FEE * 100, 2), "แย่ลงเปอร์เซ็นต์": 0.1, "เส้นเข้า": ENTER, "เส้นออก": LEAVE,
              "ถือไม่เกิน": HOLD, "ทุน": int(CAPITAL), "ปี": [2022, 2024, 2025, 2026], "จำนวนเหรียญชุดข้อมูล": 10,
              "วันชุดข้อมูลก่อนทดสอบ": 731 + 365, "วันหาย": 0}
    drills = [
        {"โจทย์": "(ทำตาม) A–B สิบวัน ได้ราคาวันถัดไป 10 ชุด — ค่าธรรมเนียมตอนเข้า เงินสดหลังเข้า Equity วันที่ 6 และ Equity จบ",
         "คำตอบ": hand["Equityจบ"]},
        {"โจทย์": "(เปลี่ยนเลข) A วันที่ 8 ปิดที่ 100.2 — Equity จบ และตรวจด้วยราคาของชุด",
         "คำตอบ": hand["แบบฝึก"]["ข้อ2"]["Equityจบ"]},
        {"โจทย์": "(เปลี่ยนเงื่อนไข) ได้ราคาปิดสองวันหลังสัญญาณ — วันและ X ที่เข้าออก และ Equity จบ",
         "คำตอบ": hand["แบบฝึก"]["ข้อ3"]["Equityจบ"]},
        {"โจทย์": "(ตัดสินใจ) แก้ fill แล้วยังได้ +119.22 ต้นจะเพิ่มทุนสองเท่า — เห็นด้วยไหม",
         "คำตอบ": ton["ผล"]["แก้h"]["ผล"]},
        {"โจทย์": "(ถ่ายโอน · ข้อมูลจริง) 2025-05-07 คิด X และ Z แบบซื่อ (h 24 ไม้บรรทัดช่วงเลือก) กับแบบชีตของต้น (h 29 สองช่วง)",
         "คำตอบ": real["วันสูงสุด"]["Z"]},
    ]
    # กล่อง 🧰 (ที่มา: tools/sab_research/practitioner-research.md §1.1–1.2 · §4 · §5 · §7 · ตัวเลขตามที่บันทึกไว้ ไม่ได้คำนวณ)
    prac = {"ปีGGR": "2006", "รอวันลดต่ำ": 0.3, "รอวันลดสูง": 0.55,
            "ปีRad": "2016", "Radปีเริ่ม": "1962", "Radปีจบ": "2014", "ระยะก่อน": 0.91, "ระยะหลัง": 0.38,
            "ปีโอกาสลด": "2009", "ปีCK": "2018", "CKปีเริ่ม": "2010", "CKปีจบ": "2015", "ปีFil": "2020",
            "Filเหรียญ": 26, "Filรายวัน": -0.07, "Filห้านาที": 11.61, "Filนาที": 5, "ปีPindza": "2026",
            "Pindzaตัว": 10, "Pindzaต้นทุน": 0.08}
    return {"_แบบฝึก": drills, "v2": {"ค่า": consts, "มือ": hand, "ต้น": ton, "จริง": real, "โลก": worlds, "ผู้รอด": surv, "นับรอบ": snoop}, "คนทำงานจริง": prac}
