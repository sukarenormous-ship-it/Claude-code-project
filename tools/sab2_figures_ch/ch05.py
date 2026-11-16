"""เล่ม 2 บท 5 — ไม้บรรทัดที่เลื่อนได้ · ค่าใหม่ที่บทใช้ (ปลั๊กอินของ tools/sab_figures.py --book sab2)

ทุกค่าคำนวณที่นี่ ไม่มีเลขลอย:
  มือ      คู่ A–B เจ็ดวัน (ตัวเลขสอน) · หน้าต่าง 4 วัน → h ของวันที่ 4–7 ด้วยสูตรบท 1 (Σ dB·dA ÷ Σ dB²) ตรวจด้วย
           Σ dB·A (เพราะ Σ dB = 0) และ sab2_stats.ols · ไม้บรรทัดของวันที่ 6 แบบเลื่อน (h 2.2) กับแบบตรึง (h 2 · Mean/SD
           ของหน้าต่างวันที่ 5) · Mean ของ X ตรวจด้วย Mean A − h × Mean B (= Intercept ของบท 1)
  บัญชี    short X 10 ชุด เปิดที่ราคาปิดวันที่ 5 ด้วย h 2 → วันที่ 6 h ใหม่ 2.2 → ปรับขา B ที่ราคาปิดวันที่ 7 (fill วันถัดไป
           แบบบท 12) · สามบัญชี (เงินสด · ของที่ถือ · Equity) · เงินจากราคา กับ "กำไร" บนจอ (X วาดด้วย h ของแต่ละวัน)
           ต่างกัน = ผลจากการนิยามใหม่ = ชุด × (h ใหม่ − h เดิม) × B · ค่าธรรมเนียมฐานเดียวของเล่ม 1 (taker 0.05% ต่อ fill)
           ตรวจทั้งบัญชีด้วย sab2_engine.run_hpath
  จำลอง    sab2_sim.drifting_price_pair (h บนราคา · 250 วันช่วงเลือก + 360 วันช่วงเทรด) สามโลก: h คงที่ 2 · h ไหล 2 → 2.2 ·
           h ไหล 2 → 2.5 · seed 1–30 · h ตรึง (ถดถอย 250 วันแรก · sab2_engine.run) เทียบหน้าต่าง 60 / 120 วัน (run_hpath)
  จริง     BTC–ETH และ LTC–DOT บนราคา (ช่วงเลือก + ช่วงตรวจ · ไม่แตะช่วงทดสอบสุดท้าย) · h หน้าต่าง 60 / 120 วัน ·
           backtest ช่วงตรวจด้วยการ์ดของบท 12 (เข้า |Z| ≥ 2 · ออก ≤ 0.5 · ถือไม่เกิน 30 วัน · fill ราคาปิดวันถัดไป)
           h ตรึง = แบบบท 12 (BTC–ETH h 24 · ไม้บรรทัดช่วงเลือก) · หน้าต่างเลื่อน: h และไม้บรรทัดวัดใหม่ทุกวันจาก W วันล่าสุด
"""

import statistics

import sab2_engine as E
import sab2_realdata as R
import sab2_sim as M
import sab2_stats as S

# ═══ ตัวเลขสอน: เจ็ดวันของคู่ A–B (A ราว 100 · B ราว 50 แบบเล่ม 1) ═══
HAND_A = [101.5, 101.0, 95.0, 94.5, 101.5, 103.0, 106.4]
HAND_B = [51, 50, 48, 47, 51, 50, 52]
W_HAND = 4
SETS_HAND = 10
FEE = E.FEE                                   # 0.05% ต่อ fill (ฐานต้นทุนเดียวของเล่ม 1 บท 11)

# ═══ โลกจำลองและข้อมูลจริง ═══
F_SIM, T_SIM, SIM_SETS = 250, 360, 5          # เท่าโลกจำลองของบท 12 (ช่วงเลือก 250 วัน + ช่วงเทรด 360 วัน · 5 ชุด)
WORLDS = (("คงที่", 2.0), ("ไหลช้า", 2.2), ("ไหลเร็ว", 2.5))
WINDOWS = (60, 120)
PAIRS = (("BTC", "ETH", 0.01, 0), ("LTC", "DOT", 10, 2))   # (A, B, ชุด, ทศนิยมของ h ตรึง) · BTC–ETH ตรงบท 12
EVERY = 5                                     # จุดในกราฟทุก 5 วัน


def _r(v, n=2):
    v = round(float(v) + 0.0, n)
    return int(v) if v == int(v) else v


def _roll_h(a, b, w):
    return [None if r is None else r["slope"] for r in S.rolling_ols(b, a, w)]


def _roll_z(a, b, hs, w):
    """ไม้บรรทัดเลื่อน: วันที่ t วัด X ของ w วันล่าสุดด้วย h ของวันที่ t แล้วหา Mean · SD (ตัวหาร n − 1)"""
    z = [None] * len(a)
    for t in range(w - 1, len(a)):
        if hs[t] is None:
            continue
        xs = [a[k] - hs[t] * b[k] for k in range(t + 1 - w, t + 1)]
        z[t] = (xs[-1] - S.mean(xs)) / S.sd(xs)
    return z


def _fixed(fa, fb, va, vb, h, sets):
    """h และไม้บรรทัดตรึงจากช่วงเลือก (แบบบท 12) แล้วเดินช่วงตรวจด้วย sab2_engine.run"""
    xs = [p - h * q for p, q in zip(fa, fb)]
    m, s = S.mean(xs), S.sd(xs)
    z = [(p - h * q - m) / s for p, q in zip(va, vb)]
    return E.run(va, vb, h, z, sets)


def _hand():
    A, B, w = HAND_A, HAND_B, W_HAND
    wins = []
    for t in range(w - 1, len(A)):
        idx = list(range(t + 1 - w, t + 1))
        a, b = [A[k] for k in idx], [B[k] for k in idx]
        ma, mb = S.mean(a), S.mean(b)
        dA, dB = [x - ma for x in a], [x - mb for x in b]
        sxy = sum(p * q for p, q in zip(dB, dA))
        sxx = sum(p * p for p in dB)
        h = sxy / sxx
        chk = sum(p * q for p, q in zip(dB, a))
        assert abs(chk - sxy) < 1e-9 and abs(S.ols(b, a)["slope"] - h) < 1e-9
        xs = [p - h * q for p, q in zip(a, b)]
        mx = S.mean(xs)
        assert abs(mx - (ma - h * mb)) < 1e-9
        sd = S.sd(xs)
        wins.append({"วันที่": [k + 1 for k in idx], "A": a, "B": b, "MeanA": _r(ma), "MeanB": _r(mb),
                     "dA": [_r(v) for v in dA], "dB": [_r(v) for v in dB],
                     "dBคูณdA": [_r(p * q) for p, q in zip(dB, dA)], "dBกำลังสอง": [_r(p * p) for p in dB],
                     "dBคูณA": [_r(p * q) for p, q in zip(dB, a)],
                     "รวมdBคูณdA": _r(sxy), "รวมdBกำลังสอง": _r(sxx), "h": _r(h),
                     "X": [_r(v) for v in xs], "MeanX": _r(mx), "hคูณMeanB": _r(h * mb), "SD": _r(sd),
                     "ห่างX": [_r(v - mx) for v in xs], "ห่างXกำลังสอง": [_r((v - mx) ** 2) for v in xs],
                     "รวมห่างกำลังสอง": _r(sum((v - mx) ** 2 for v in xs)), "Var": _r(sd * sd),
                     "Z": _r((xs[-1] - mx) / sd)})
    hs = [None] * (w - 1) + [x["h"] for x in wins]
    assert hs[3:] == [2, 2, 2.2, 2.2], hs
    w5, w6 = wins[1], wins[2]                    # หน้าต่างที่จบวันที่ 5 และวันที่ 6
    # ไม้บรรทัดตรึง (h 2 · Mean/SD จากหน้าต่างวันที่ 5) วัด X ของวันที่ 6
    x6_old = A[5] - 2 * B[5]
    z_fixed = (x6_old - w5["MeanX"]) / S.sd([A[k] - 2 * B[k] for k in range(1, 5)])
    # หน้าต่างวันที่ 3–6 แต่ยังใช้ h 2
    xs_h2 = [A[k] - 2 * B[k] for k in range(2, 6)]
    hand = {"A": A, "B": B, "หน้าต่าง": w, "หน้าต่างต่อวัน": wins, "h": hs,
            "วัน6": {"Xเดิม": _r(x6_old), "Zตรึง": _r(z_fixed), "SDตรึง": _r(w5["SD"]),
                     "Zตรึงจากเลขปัด": _r(x6_old / w5["SD"]), "Zเลื่อนจากเลขปัด": _r((w6["X"][-1] - w6["MeanX"]) / w6["SD"]),
                     "Xh2หน้าต่าง": [_r(v) for v in xs_h2], "Meanh2": _r(S.mean(xs_h2)),
                     "Zh2เลื่อนMean": _r((xs_h2[-1] - S.mean(xs_h2)) / S.sd(xs_h2)),
                     "ห่างMeanเลื่อน": _r(w6["X"][-1] - w6["MeanX"]), "ห่างMeanตรึง": _r(x6_old - w5["MeanX"])},
            "MeanXกระโดด": _r(w6["MeanX"] - w5["MeanX"]), "hคูณBกระโดด": _r((w6["h"] - w5["h"]) * w6["MeanB"]),
            "hเปลี่ยน": _r(w6["h"] - w5["h"])}

    # ═══ บัญชี: short X 10 ชุดตั้งแต่ราคาปิดวันที่ 5 (h 2) · h วันที่ 6 = 2.2 → ปรับขา B ที่ราคาปิดวันที่ 7 ═══
    n, h0, h1 = SETS_HAND, hs[4], hs[5]
    qa, qb = -n, n * h0                          # short X: ขาย A 10 · ซื้อ B 20
    cash5 = 1000 - qa * A[4] - qb * B[4]         # ทุนคู่ 1,000 (ไม่คิดค่าธรรมเนียมตอนเปิด เพื่อแยกเรื่อง)
    rows = []
    for t in (4, 5, 6):
        rows.append({"วันที่": t + 1, "A": A[t], "B": B[t], "เงินสด": _r(cash5), "ถือA": qa, "ถือB": _r(qb),
                     "มูลค่าA": _r(qa * A[t]), "มูลค่าB": _r(qb * B[t]),
                     "Equity": _r(cash5 + qa * A[t] + qb * B[t]),
                     "h": hs[t], "Xจอ": _r(A[t] - hs[t] * B[t])})
    money = [_r(qa * (A[t] - A[t - 1]) + qb * (B[t] - B[t - 1])) for t in (5, 6)]
    legA = [_r(qa * (A[t] - A[t - 1])) for t in (5, 6)]
    legB = [_r(qb * (B[t] - B[t - 1])) for t in (5, 6)]
    chart = [_r(-n * ((A[t] - hs[t] * B[t]) - (A[t - 1] - hs[t - 1] * B[t - 1]))) for t in (5, 6)]
    redef = [_r(c - m) for c, m in zip(chart, money)]
    # ปรับขา B ที่ราคาปิดวันที่ 7: เป้า 10 × 2.2 = 22 เหรียญ
    buy = n * h1 - qb
    val = buy * B[6]
    fee = FEE * val
    cash7 = cash5 - val - fee
    eq7 = cash7 + qa * A[6] + (qb + buy) * B[6]
    eq7_before = cash5 + qa * A[6] + qb * B[6]
    # ตรวจด้วยเครื่องกลาง: เปิดที่วันที่ 5 (สัญญาณวันที่ 4) · ไม่คิดค่าธรรมเนียมตอนเปิด → fee ใส่ทีหลังเฉพาะการปรับ
    sig = [0, 0, 0, 3, 3, 3, 3]
    rh = E.run_hpath(A, B, [2, 2, 2, 2, 2, 2.2, 2.2], sig, SETS_HAND, capital=1000.0, fee=0.0, hold=None)
    assert abs(rh["price_pnl"] - sum(money)) < 1e-9 and abs(rh["chart_pnl"] - sum(chart)) < 1e-9
    assert abs(rh["equity"][-1] - (eq7 + fee)) < 1e-9 and rh["rebalances"] == 1
    ledger = {"ชุด": n, "h0": h0, "h1": h1, "แถว": rows, "เงินจากราคา": money, "ขาA": legA, "ขาB": legB,
              "จอ": chart, "นิยามใหม่": redef,
              "รวมเงิน": _r(sum(money)), "รวมจอ": _r(sum(chart)), "รวมนิยามใหม่": _r(sum(redef)),
              "สูตรนิยามใหม่วัน6": _r(n * (h1 - h0) * B[5]), "สูตรนิยามใหม่รวม": _r(n * (h1 - h0) * B[6]),
              "ซื้อBเพิ่ม": _r(buy), "มูลค่าที่ซื้อ": _r(val), "ค่าธรรมเนียมปรับ": _r(fee), "ค่าธรรมเนียมปรับ3": _r(fee, 3),
              "เงินสดหลังปรับ": _r(cash7), "Equityก่อนปรับ": _r(eq7_before), "Equityหลังปรับ": _r(eq7),
              "ถือBหลังปรับ": _r(qb + buy), "เงินสดเปิด": _r(cash5),
              "ขายAเปิด": _r(-qa * A[4]), "ซื้อBเปิด": _r(qb * B[4]),
              "Xจอ5": rows[0]["Xจอ"], "Xจอ6": rows[1]["Xจอ"], "Xจอ7": rows[2]["Xจอ"],
              "Xจอเปลี่ยนวัน6": _r(rows[1]["Xจอ"] - rows[0]["Xจอ"]),
              "Xh2วัน6": _r(A[5] - h0 * B[5]), "ราคาส่วนX": _r((A[5] - A[4]) - h0 * (B[5] - B[4])),
              "hส่วนX": _r(-(h1 - h0) * B[5]),
              "Aขยับ": [_r(A[t] - A[t - 1]) for t in (5, 6)], "Bขยับ": [_r(B[t] - B[t - 1]) for t in (5, 6)]}
    # ✍️ ข้อ 2: ถ้า A วันที่ 6 เป็น 101.5 แทน 103
    a2 = A[:5] + [101.5]
    b2 = B[:6]
    h6b = S.ols(b2[2:6], a2[2:6])["slope"]
    ex2 = {"A6": 101.5, "รวมdBคูณA": _r(sum((b2[k] - S.mean(b2[2:6])) * a2[k] for k in range(2, 6))), "h": _r(h6b),
           "นิยามใหม่": _r(n * (h6b - h0) * B[5]), "เงินวัน6": _r(qa * (101.5 - A[4]) + qb * (B[5] - B[4])),
           "MeanA": _r(S.mean(a2[2:6])), "MeanX": _r(S.mean(a2[2:6]) - h6b * S.mean(b2[2:6]))}
    ex2["จอวัน6"] = _r(ex2["เงินวัน6"] + ex2["นิยามใหม่"])
    # ✍️ ข้อ 3: long X 10 ชุดแทน short (ทุกอย่างกลับเครื่องหมาย)
    ex3 = {"เงิน": _r(-sum(money)), "จอ": _r(-sum(chart)), "นิยามใหม่": _r(-sum(redef)),
           "เงินวัน6": _r(-money[0]), "จอวัน6": _r(-chart[0]), "นิยามใหม่วัน6": _r(-redef[0])}
    return hand, ledger, ex2, ex3


def _sim():
    out = {}
    example = {}
    for name, h1 in WORLDS:
        res = {k: [] for k in ("ตรึง", "60", "120")}
        err = {k: [] for k in res}
        err_end = {k: [] for k in res}
        trades = {k: [] for k in res}
        redef, creb, nreb, rng60, rng120 = [], [], [], [], []
        for sd_ in M.ROBUST_SEEDS:
            w = M.drifting_price_pair(seed=sd_, n=F_SIM + T_SIM, h0=2.0, h1=h1)
            a, b, hp = w["A"], w["B"], w["true"]["h_path"]
            hf = S.ols(b[:F_SIM], a[:F_SIM])["slope"]
            r = _fixed(a[:F_SIM], b[:F_SIM], a[F_SIM:], b[F_SIM:], hf, SIM_SETS)
            res["ตรึง"].append(r["net"])
            trades["ตรึง"].append(r["trades"])
            err["ตรึง"].append(statistics.mean(abs(hf - h) for h in hp[F_SIM:]))
            err_end["ตรึง"].append(abs(hf - hp[-1]))
            rolls = {}
            for wd in WINDOWS:
                hh = _roll_h(a, b, wd)
                zz = _roll_z(a, b, hh, wd)
                rr = E.run_hpath(a[F_SIM:], b[F_SIM:], hh[F_SIM:], zz[F_SIM:], SIM_SETS)
                res[str(wd)].append(rr["net"])
                trades[str(wd)].append(rr["trades"])
                err[str(wd)].append(statistics.mean(abs(x - h) for x, h in zip(hh[F_SIM:], hp[F_SIM:])))
                err_end[str(wd)].append(abs(hh[-1] - hp[-1]))
                rolls[wd] = hh
                if wd == 120:
                    rng120.append((min(hh[F_SIM:]), max(hh[F_SIM:])))
                if wd == 60:
                    redef.append(rr["redefinition"])
                    creb.append(rr["costs_rebalance"])
                    nreb.append(rr["rebalances"])
                    rng60.append((min(hh[F_SIM:]), max(hh[F_SIM:])))
            if sd_ == M.ROBUST_SEEDS[0]:
                example[name] = {"seed": sd_, "จริง": [_r(v, 3) for v in hp[::EVERY]], "ตรึง": _r(hf, 3),
                                 "60": [None if v is None else _r(v, 3) for v in rolls[60][::EVERY]],
                                 "120": [None if v is None else _r(v, 3) for v in rolls[120][::EVERY]]}
        out[name] = {"h1": h1,
                     "มัธยฐาน": {k: _r(statistics.median(v)) for k, v in res.items()},
                     "บวก": {k: sum(1 for x in v if x > 0) for k, v in res.items()},
                     "ไม้มัธยฐาน": {k: _r(statistics.median(v), 1) for k, v in trades.items()},
                     "คลาดเฉลี่ย": {k: _r(statistics.median(v), 3) for k, v in err.items()},
                     "คลาดวันสุดท้าย": {k: _r(statistics.median(v), 2) for k, v in err_end.items()},
                     "นิยามใหม่60มัธยฐาน": _r(statistics.median(redef), 1),
                     "ค่าปรับ60มัธยฐาน": _r(statistics.median(creb)),
                     "ครั้งปรับ60มัธยฐาน": _r(statistics.median(nreb), 1),
                     "h60ต่ำสุด": _r(min(x[0] for x in rng60)), "h60สูงสุด": _r(max(x[1] for x in rng60)),
                     "h120ต่ำสุด": _r(min(x[0] for x in rng120)), "h120สูงสุด": _r(max(x[1] for x in rng120))}
    out["กราฟ"] = example["ไหลช้า"]
    out["กราฟ"]["วันแบ่ง"] = F_SIM
    out["ช่วงเลือก"], out["ช่วงเทรด"], out["ชุด"], out["โลก"] = F_SIM, T_SIM, SIM_SETS, len(M.ROBUST_SEEDS)
    return out


def _real():
    df, pf = R.load_closes("formation")
    dv, pv = R.load_closes("validation")
    out = {"ช่วงเลือก": [df[0], df[-1], len(df)], "ช่วงตรวจ": [dv[0], dv[-1], len(dv)]}
    for an, bn, sets, nd in PAIRS:
        fa, fb, va, vb = pf[an], pf[bn], pv[an], pv[bn]
        nf = len(fa)
        reg = S.ols(fb, fa)
        hfix = round(reg["slope"], nd) if nd else round(reg["slope"])
        fx = _fixed(fa, fb, va, vb, hfix, sets)
        A, B = fa + va, fb + vb
        key = f"{an}-{bn}"
        d = {"hช่วงเลือก": _r(reg["slope"]), "hตรึง": hfix, "ชุด": sets,
             "ตรึง": {"ผล": _r(fx["net"]), "ไม้": fx["trades"], "ชนะ": fx["wins"], "ค่าธรรมเนียม": _r(fx["costs"]),
                      "ค้าง": abs(fx["open"]), "ทิศค้าง": fx["open"]},
             "Aเริ่มตรวจ": _r(va[0]), "Bเริ่มตรวจ": _r(vb[0], 3)}
        series = {}
        for wd in WINDOWS:
            hs = _roll_h(A, B, wd)
            zz = _roll_z(A, B, hs, wd)
            rr = E.run_hpath(va, vb, hs[nf:], zz[nf:], sets)
            rn = E.run_hpath(va, vb, hs[nf:], zz[nf:], sets, rebalance=False)
            hf_ = [v for v in hs[:nf] if v is not None]
            hv = hs[nf:]
            d[str(wd)] = {"ผล": _r(rr["net"]), "ไม้": rr["trades"], "ชนะ": rr["wins"],
                          "ค่าธรรมเนียมเข้าออก": _r(rr["costs_trade"]), "ค่าปรับ": _r(rr["costs_rebalance"]),
                          "ครั้งปรับ": rr["rebalances"], "ค้าง": abs(rr["open"]), "ทิศค้าง": rr["open"],
                          "เงินจากราคา": _r(rr["price_pnl"]), "จอ": _r(rr["chart_pnl"]),
                          "นิยามใหม่": _r(rr["redefinition"]), "ไม่ปรับ": _r(rn["net"]),
                          "hตรวจต่ำสุด": _r(min(hv)), "hตรวจสูงสุด": _r(max(hv)),
                          "hตรวจมัธยฐาน": _r(statistics.median(hv)), "วันhติดลบตรวจ": sum(1 for v in hv if v < 0),
                          "hเลือกต่ำสุด": _r(min(hf_)), "hเลือกสูงสุด": _r(max(hf_)),
                          "วันhติดลบเลือก": sum(1 for v in hf_ if v < 0),
                          "ค่าปรับต่อครั้ง": _r(rr["costs_rebalance"] / max(1, rr["rebalances"]), 3)}
            series[wd] = hs
        if key == "BTC-ETH":
            pts = list(range(WINDOWS[0] - 1, len(A), EVERY))
            d["กราฟ"] = {"วัน": pts, "60": [_r(series[60][t]) for t in pts],
                         "120": [None if series[120][t] is None else _r(series[120][t]) for t in pts],
                         "แบ่ง": nf, "วันรวม": len(A), "ตรึง": _r(reg["slope"])}
            step = len(dv) // 10
            d["สิบแถว"] = [{"วันที่": dv[t], "A": _r(va[t]), "B": _r(vb[t]), "h60": _r(series[60][nf + t]),
                            "h120": _r(series[120][nf + t]), "ETHต่อชุด60": _r(sets * series[60][nf + t]),
                            "ETHต่อชุดตรึง": _r(sets * hfix)} for t in range(0, len(dv), step)][:10]
        out[key] = d
    return out


def extend(data, D, q):
    hand, ledger, ex2, ex3 = _hand()
    sim = _sim()
    real = _real()

    import sab_book as SB
    fig1 = SB.load_figures("sab")
    v11 = fig1["ch11"]["v2"]
    v14 = fig1["ch14"]["v2"]["ไม้บรรทัดเฉลี่ย4"]
    vol1 = {"takerเปอร์เซ็นต์": v11["ต้นทุน"]["อัตราtakerเปอร์เซ็นต์"],
            "ปรับhedgeมูลค่า": v11["ปรับhedge"]["มูลค่าที่ซื้อคืน"], "ปรับhedgeค่าธรรมเนียม": v11["ปรับhedge"]["ค่าธรรมเนียม"],
            "ปรับhedgeEquity": v11["ปรับhedge"]["equityหลังค่าธรรมเนียม"],
            "MA4Mean": v14["แถว"][2]["Mean"], "MA4Z": v14["แถว"][2]["Z"], "MA4X": v14["X"], "MA4สุทธิ": v14["สุทธิ"]}
    ch1 = data.get("ch01", {}).get("จริง", {})
    if ch1.get("หน้าต่าง60"):
        assert (ch1["หน้าต่าง60"]["ต่ำสุด"], ch1["หน้าต่าง60"]["สูงสุด"]) == \
            (real["BTC-ETH"]["60"]["hเลือกต่ำสุด"], real["BTC-ETH"]["60"]["hเลือกสูงสุด"]), "หน้าต่าง 60 วันไม่ตรงบท 1"
    ch12 = data.get("ch12", {}).get("จริง", {})
    if "ผล" in ch12:
        assert ch12["ผล"] == real["BTC-ETH"]["ตรึง"]["ผล"], "h ตรึงไม่ตรงบท 12"

    be, ld = real["BTC-ETH"], real["LTC-DOT"]
    looks = 2 * (1 + len(WINDOWS))
    ch = {"เล่ม1": vol1, "มือ": hand, "บัญชี": ledger, "จำลอง": sim, "จริง": real,
          "ดูช่วงตรวจ": looks, "แบบฝึก2": ex2, "แบบฝึก3": ex3}
    ch["_แบบฝึก"] = [
        {"โจทย์": "(ทำตาม) หน้าต่างวันที่ 4–7: Σ dB·dA 30.8 ÷ Σ dB² 14 → h · Mean ของ X", "คำตอบ": hand["หน้าต่างต่อวัน"][3]["h"]},
        {"โจทย์": "(เปลี่ยนเลข) A วันที่ 6 = 101.5 → h ของหน้าต่างวันที่ 3–6 และผลจากการนิยามใหม่", "คำตอบ": ex2["h"]},
        {"โจทย์": "(เปลี่ยนเงื่อนไข) long X 10 ชุดแทน short → เงินจริงและตัวเลขบนจอ", "คำตอบ": ex3["นิยามใหม่"]},
        {"โจทย์": "(ตัดสินใจ) LTC–DOT หน้าต่าง 60 วันได้มากกว่า h ตรึงในช่วงตรวจ — เปลี่ยนไปใช้เลยไหม", "คำตอบ": ld["60"]["ผล"]},
        {"โจทย์": "(ถ่ายโอน · ข้อมูลจริง) LTC–DOT หน้าต่าง 120 วัน บนจอเทียบเงินจริง", "คำตอบ": ld["120"]["จอ"]},
    ]
    ch["_claims"] = [{"id": "sab2-ch05-taker",
                      "ข้อความ": "ค่าธรรมเนียมของการปรับขา B ใช้ฐานเดียวของเล่ม 1 (taker 0.05% ต่อ fill × มูลค่าที่ซื้อขาย) "
                                 "ไม่รวมราคาที่แย่กว่าราคากลาง",
                      "ระดับหลักฐาน": "ค่าของเล่ม", "แหล่ง": "เล่ม 1 บท 11 (sab-part11.html) · tools/sab2_engine.py FEE", "บท": [5]}]
    _ = (be, D, q)
    return ch
