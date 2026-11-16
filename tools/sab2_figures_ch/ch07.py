"""เล่ม 2 บท 7 — เข้าเมื่อไร ออกเมื่อไร: จากเส้น 2 ไปถึง "optimal" · ตัวเลขทุกตัวของ docs/sab2-part7.html

ตอน ก  มือ: เส้นทาง X 40 วันจากโลกเชือก φ 0.85 (Mean 0 · SD 1 แบบคู่ A–B ของเล่ม 1 → Z = X · ปัดหนึ่งตำแหน่ง)
       นับไม้ของเส้นเข้า 1 / 1.5 / 2 / 2.5 (ออกที่ 0.5 · สัญญาณราคาปิดวันนี้ ได้ราคาปิดวันถัดไป) → กำไรต่อไม้แบบได้ราคาตรงเส้น
       (เส้นเข้า − 0.5) × 10 ชุด − ต้นทุน 2 ต่อไม้ (เล่ม 1 บท 12) · ตรวจสองทางด้วยราคาที่ได้จริงวันถัดไป
       🎲 โลก OU ที่รู้คำตอบ (price_pair · B คงที่ 50 เพื่อให้ต้นทุนต่อไม้ราว 2 คงที่ · SD นิ่งของ X = 1 · Z = X)
       φ 0.8 / 0.9 / 0.97 · 30 โลก × 10 ปี · sab2_engine.run (เข้า L · ออก 0.5 · ถือไม่เกิน 30 วัน) · ค่าธรรมเนียม ×1 ×3 ×5
       ทุกค่า "ต่อปี" คือผลรวมของไม้ที่ปิดแล้วทั้ง 300 ปีจำลอง ÷ 300 (เอกลักษณ์ ไม้ต่อปี × (กำไรต่อไม้ − ต้นทุนต่อไม้) ตรงตัว)
ตอน ข  🎲 Threshold Model: threshold_pair (ในกรอบ ±2 เดินสุ่ม · นอกกรอบ φ 0.8) เทียบโลก OU ที่ φ และ SD เท่ากัน
       🎲 Regime Switching: regime_pair (ค่ากลางสลับ 0 ↔ 2.5 SD · φ 0.97 · อยู่สภาวะเดิมวันละ 0.998) 200 โลก × (731 + 365 วัน)
       ไม้บรรทัดจาก 731 วันแรก · เส้นที่ดีสุดในช่วงแรกตรงกับช่วงหลังกี่โลก แยกโลกที่ค่ากลางย้ายกับไม่ย้าย
ตอน ค  📡 LTC บน DOT (ราคา · h ช่วงเลือก 3.76 แบบบท 5 · 10 ชุด · ไม้บรรทัดช่วงเลือก) เส้นเข้า 1 / 1.5 / 2 / 2.5 / 3
       ช่วงเลือก (ในตัวอย่าง) แล้วเปิดช่วงตรวจหนึ่งครั้ง · เส้นเข้า 2 ช่วงตรวจต้องเท่าบท 5 (+180.51)
       🎲 คู่จำลอง φ 0.97 (ใกล้ LTC–DOT ของบท 4) 30 โลก: เส้นดีสุดของช่วงเลือกตรงกับช่วงตรวจกี่โลก
ช่วงทดสอบสุดท้ายไม่ถูกแตะ (load_closes("formation") และ ("validation") เท่านั้น)
"""

import math
import statistics

import sab_book as SB
import sab2_engine as E
import sab2_realdata as R
import sab2_sim as M
import sab2_stats as S

LINES = (1, 1.5, 2, 2.5, 3)        # เส้นเข้าที่ลอง (Z-score)
HAND_LINES = (1, 1.5, 2, 2.5)
LEAVE, HOLD, SETS = 0.5, 30, 10     # การ์ดของเล่ม 1: ออกที่ 0.5 · ถือไม่เกิน 30 วัน · 10 ชุด
HAND_COST = 2                       # ต้นทุนต่อไม้ของเล่ม 1 บท 12 (สี่ fill × 0.5)
HAND_SEED, HAND_PHI, HAND_N = 161, 0.85, 40
OU_PHIS = (0.8, 0.9, 0.97)
FEE_MULTS = (1, 3, 5)
YEARS, YDAYS = 10, 365
THR_BAND, THR_SD, THR_PHI_OUT = 2.0, 0.3, 0.8
REG_PHI, REG_MU, REG_STAY, REG_WORLDS = 0.97, 2.5, 0.998, 200
F_DAYS, V_DAYS = 731, 365           # ยาวเท่าช่วงเลือกกับช่วงตรวจของเล่ม
LONG_N = 200000                     # โลกยาวหนึ่งโลกไว้วัด SD ระยะยาวและ φ ของโลกที่มีกรอบ


def _r(v, n=2):
    v = round(float(v) + 0.0, n)
    return int(v) if v == int(v) else v


def _sdz(phi):
    """แรงกระแทกต่อวันที่ทำให้ SD นิ่งของ X เท่ากับ 1"""
    return math.sqrt(1 - phi * phi)


# ───────────────────────── ตอน ก: มือ ─────────────────────────

def _hand_trades(X, L):
    """กฎการ์ดบนเส้นทางที่ปัดแล้ว: สัญญาณจากราคาปิดวัน t − 1 ได้ราคาปิดวัน t · คืนรายการไม้ (วันนับจาก 1)"""
    held, cur, out = 0, None, []
    for t in range(1, len(X)):
        z = X[t - 1]
        want = held
        if held == 0 and abs(z) >= L:
            want = -1 if z > 0 else 1
        elif held != 0 and abs(z) <= LEAVE:
            want = 0
        if want != held:
            if held == 0:
                cur = {"วันสัญญาณเข้า": t, "Xสัญญาณเข้า": X[t - 1], "วันเข้า": t + 1, "Xเข้า": X[t], "ทิศ": want}
            else:
                cur.update({"วันสัญญาณออก": t, "Xสัญญาณออก": X[t - 1], "วันออก": t + 1, "Xออก": X[t]})
                cur["Xเปลี่ยน"] = _r(cur["ทิศ"] * (cur["Xออก"] - cur["Xเข้า"]), 1)
                cur["ได้"] = _r(SETS * cur["Xเปลี่ยน"], 1)
                out.append(cur)
            held = want
    assert held == 0, "เส้นทางมือต้องปิดไม้ครบก่อนวันที่ 40"
    return out


def _hand(q):
    w = M.price_pair(seed=HAND_SEED, n=HAND_N, h=2, phi=HAND_PHI, sd=_sdz(HAND_PHI), common_sd=0.0)
    X = [_r(x, 1) for x in w["X"]]
    X = [0 if v == 0 else v for v in X]
    lines = []
    for L in HAND_LINES:
        tr = _hand_trades(X, L)
        per = _r((L - LEAVE) * SETS, 1)
        real = _r(sum(t["ได้"] for t in tr), 1)
        lines.append({"เส้น": L, "ไม้": len(tr), "ระยะ": _r(L - LEAVE, 1), "ต่อไม้": per, "รวมก่อนต้นทุน": _r(len(tr) * per, 1),
                      "ต้นทุนรวม": len(tr) * HAND_COST, "สุทธิต่อไม้": _r(per - HAND_COST, 1),
                      "สุทธิ": _r(len(tr) * (per - HAND_COST), 1),
                      "สุทธิต้นทุน0": _r(len(tr) * per, 1), "สุทธิต้นทุน6": _r(len(tr) * (per - 6), 1),
                      "สุทธิต้นทุน10": _r(len(tr) * (per - 10), 1), "สุทธิต้นทุน12": _r(len(tr) * (per - 12), 1),
                      "ต้นทุนกินหมด": per,
                      "ไม้จริง": tr, "จริงก่อนต้นทุน": real, "จริงสุทธิ": _r(real - len(tr) * HAND_COST, 1)})
    counts = [x["ไม้"] for x in lines]
    assert counts == [4, 3, 2, 1], counts
    best = max(lines, key=lambda x: x["สุทธิ"])
    assert best["เส้น"] == 2
    # วันที่ |X| ถึงแต่ละเส้น (นับวันปิด)
    reach = {str(L).replace(".", "_"): sum(1 for x in X if abs(x) >= L) for L in HAND_LINES}
    rows = [{"วัน": [i + 1 for i in range(k, k + 10)], "X": X[k:k + 10]} for k in range(0, HAND_N, 10)]
    return {"seed": HAND_SEED, "phi": HAND_PHI, "วัน": HAND_N, "X": X, "แถว": rows, "เส้น": lines,
            "ต้นทุน": HAND_COST, "ชุด": SETS, "ออก": LEAVE, "วันที่ถึง": reach,
            "สูงสุด": max(X), "ต่ำสุด": min(X)}


# ───────────────────────── โลกจำลอง: สรุปไม้แบบรวมทุกปี ─────────────────────────

def _pool(worlds, ruler, lines=LINES, years=YEARS):
    """worlds = [โลก] · ruler(โลก) → (Mean, SD) · คืนต่อเส้น: ไม้ต่อปี · กำไรต่อไม้ก่อนต้นทุน · ต้นทุนต่อไม้ ×1 ×3 ×5 ·
    สุทธิต่อปี (เฉพาะไม้ที่ปิด) · สัดส่วนที่ออกเพราะครบเวลา · กำไรเฉลี่ยของไม้ที่ออกที่เส้นกับที่ออกเพราะครบเวลา"""
    acc = {L: {"n": 0, "gross": 0.0, "fee": 0.0, "time": 0, "g_time": 0.0, "g_tgt": 0.0} for L in lines}
    for w in worlds:
        m, s = ruler(w)
        z = [(x - m) / s for x in w["X"]]
        for L in lines:
            r = E.run(w["A"], w["B"], 2, z, SETS, enter=L, leave=LEAVE, hold=HOLD)
            fees = {f["t"]: f["fee"] for f in r["fill_list"]}
            a = acc[L]
            for t in r["trade_list"]:
                g = t["pnl"] + fees[t["t_in"]] + fees[t["t_out"]]
                a["n"] += 1
                a["gross"] += g
                a["fee"] += fees[t["t_in"]] + fees[t["t_out"]]
                if t["reason"] == "time":
                    a["time"] += 1
                    a["g_time"] += g
                else:
                    a["g_tgt"] += g
    yrs = len(worlds) * years
    out = {}
    for L in lines:
        a = acc[L]
        n = max(1, a["n"])
        gross, fee = a["gross"] / n, a["fee"] / n
        row = {"เส้น": L, "ไม้ต่อปี": _r(a["n"] / yrs, 1), "ไม้รวม": a["n"], "กำไรต่อไม้": _r(gross, 1),
               "ระยะต่อไม้": _r(gross / SETS, 2), "ต้นทุนต่อไม้": _r(fee, 1),
               "ครบเวลาเปอร์เซ็นต์": _r(100 * a["time"] / n, 0),
               "กำไรไม้ครบเวลา": _r(a["g_time"] / max(1, a["time"]), 1),
               "กำไรไม้ถึงเส้น": _r(a["g_tgt"] / max(1, a["n"] - a["time"]), 1)}
        for k in FEE_MULTS:
            row[f"สุทธิต่อปีx{k}"] = _r(a["n"] / yrs * (gross - k * fee), 1)
            row[f"ต้นทุนต่อไม้x{k}"] = _r(k * fee, 1)
            # คิดจากเลขปัดที่หน้าแสดง (ผู้อ่านคูณตามได้ตรง): ไม้ต่อปี × (กำไรต่อไม้ − ต้นทุนต่อไม้)
            row[f"ปัดx{k}"] = _r(row["ไม้ต่อปี"] * (row["กำไรต่อไม้"] - row[f"ต้นทุนต่อไม้x{k}"]), 1)
            row[f"ปัดต่อไม้x{k}"] = _r(row["กำไรต่อไม้"] - row[f"ต้นทุนต่อไม้x{k}"], 1)
        out[str(L).replace(".", "_")] = row
    return out


def _best(rows, key):
    return max(rows.values(), key=lambda r: r[key])["เส้น"]


def _ou():
    out = {}
    for phi in OU_PHIS:
        ws = [M.price_pair(seed=s, n=YEARS * YDAYS, h=2, phi=phi, sd=_sdz(phi), common_sd=0.0) for s in M.ROBUST_SEEDS]
        rows = _pool(ws, lambda w: (0.0, 1.0))
        key = "phi" + str(phi).replace(".", "")
        out[key] = {"phi": phi, "ครึ่งชีวิต": _r(S.half_life(phi), 1), "แถว": rows,
                    "ดีสุด": {f"x{k}": _best(rows, f"ปัดx{k}") for k in FEE_MULTS},
                    "ดีสุดสุทธิ": {f"x{k}": max(r[f"ปัดx{k}"] for r in rows.values()) for k in FEE_MULTS}}
        assert all(_best(rows, f"ปัดx{k}") == _best(rows, f"สุทธิต่อปีx{k}") for k in FEE_MULTS), "เลขปัดเปลี่ยนเส้นที่ดีสุด"
    return out


# ───────────────────────── ตอน ข: เชือกที่เปลี่ยนนิสัย ─────────────────────────

def _threshold():
    ref = M.threshold_pair(seed=1, n=LONG_N, band=THR_BAND, sd=THR_SD, phi_out=THR_PHI_OUT, common_sd=0.0)
    sd_long = S.sd(ref["X"])
    phi_long = S.ar1(ref["X"])["phi"]
    ws = [M.threshold_pair(seed=s, n=YEARS * YDAYS, band=THR_BAND, sd=THR_SD, phi_out=THR_PHI_OUT, common_sd=0.0)
          for s in M.ROBUST_SEEDS]
    thr = _pool(ws, lambda w: (0.0, sd_long))
    phi_r = round(phi_long, 3)
    twin = [M.price_pair(seed=s, n=YEARS * YDAYS, h=2, phi=phi_r, sd=sd_long * _sdz(phi_r), common_sd=0.0)
            for s in M.ROBUST_SEEDS]
    ou = _pool(twin, lambda w: (0.0, sd_long))
    band_z = THR_BAND / sd_long
    return {"กรอบ": THR_BAND, "กรอบZ": _r(band_z, 1), "แรงสะบัด": THR_SD, "phiนอก": THR_PHI_OUT, "phiใน": 1,
            "sdยาว": _r(sd_long, 2), "phiประมาณ": _r(phi_long, 2), "phiประมาณ3": _r(phi_long, 3),
            "ครึ่งชีวิตประมาณ": _r(S.half_life(phi_long), 1),
            "มีกรอบ": thr, "แฝด": ou, "ดีสุดมีกรอบ": {f"x{k}": _best(thr, f"ปัดx{k}") for k in FEE_MULTS},
            "ดีสุดแฝด": {f"x{k}": _best(ou, f"ปัดx{k}") for k in FEE_MULTS}}


def _regime():
    sdv = _sdz(REG_PHI)
    groups = {"ย้าย": [], "ไม่ย้าย": []}
    for s in range(1, REG_WORLDS + 1):
        w = M.regime_pair(seed=s, n=F_DAYS + V_DAYS, phis=(REG_PHI, REG_PHI), mus=(0.0, REG_MU),
                          stays=(REG_STAY, REG_STAY), sd=sdv, common_sd=0.0)
        st = w["true"]["state"]
        f_state = 1 if sum(st[:F_DAYS]) > F_DAYS / 2 else 0
        v_frac = sum(1 for k in st[F_DAYS:] if k != f_state) / V_DAYS
        X = w["X"]
        m, sd = S.mean(X[:F_DAYS]), S.sd(X[:F_DAYS])
        z = [(x - m) / sd for x in X]
        res = {}
        for L in LINES:
            rf = E.run(w["A"][:F_DAYS], w["B"][:F_DAYS], 2, z[:F_DAYS], SETS, enter=L, leave=LEAVE, hold=HOLD)
            rv = E.run(w["A"][F_DAYS:], w["B"][F_DAYS:], 2, z[F_DAYS:], SETS, enter=L, leave=LEAVE, hold=HOLD)
            tv = rv["trade_list"]
            res[L] = (rf["net"], rv["net"], sum(1 for t in tv if t["reason"] == "time"), len(tv))
        groups["ย้าย" if v_frac > 0.5 else "ไม่ย้าย"].append(res)
    out = {"โลก": REG_WORLDS, "phi": REG_PHI, "ค่ากลางที่ย้าย": REG_MU, "อยู่ต่อ": REG_STAY,
           "อยู่เฉลี่ยวัน": _r(1 / (1 - REG_STAY), 0), "ครึ่งชีวิต": _r(S.half_life(REG_PHI), 1)}
    for g, rs in groups.items():
        bf = [max(LINES, key=lambda L: r[L][0]) for r in rs]
        bv = [max(LINES, key=lambda L: r[L][1]) for r in rs]
        agree = sum(1 for a, b in zip(bf, bv) if a == b)
        lines = {}
        for L in LINES:
            nt = sum(r[L][3] for r in rs)
            lines[str(L).replace(".", "_")] = {
                "เส้น": L, "เลือกมัธยฐาน": _r(statistics.median(r[L][0] for r in rs), 0),
                "ตรวจมัธยฐาน": _r(statistics.median(r[L][1] for r in rs), 0),
                "ตรวจบวก": sum(1 for r in rs if r[L][1] > 0),
                "ครบเวลาเปอร์เซ็นต์": _r(100 * sum(r[L][2] for r in rs) / max(1, nt), 0),
                "ดีสุดช่วงเลือก": sum(1 for b in bf if b == L), "ดีสุดช่วงตรวจ": sum(1 for b in bv if b == L)}
        out[g] = {"จำนวน": len(rs), "ตรงกัน": agree, "ตรงกันเปอร์เซ็นต์": _r(100 * agree / len(rs), 0), "เส้น": lines}
    return out


# ───────────────────────── ตอน ค: LTC–DOT และคู่จำลอง ─────────────────────────

def _real():
    df, pf = R.load_closes("formation", coins=["LTC", "DOT", "BTC", "ETH"])
    dv, pv = R.load_closes("validation", coins=["LTC", "DOT", "BTC", "ETH"])
    out = {"ช่วงเลือก": {"เริ่ม": df[0], "จบ": df[-1], "วัน": len(df)},
           "ช่วงตรวจ": {"เริ่ม": dv[0], "จบ": dv[-1], "วัน": len(dv)}}
    for an, bn, sets, nd in (("LTC", "DOT", 10, 2), ("BTC", "ETH", 0.01, 0)):
        fa, fb, va, vb = pf[an], pf[bn], pv[an], pv[bn]
        reg = S.ols(fb, fa)
        h = round(reg["slope"], nd) if nd else round(reg["slope"])
        xf = [a - h * b for a, b in zip(fa, fb)]
        m, s = S.mean(xf), S.sd(xf)
        zf = [(x - m) / s for x in xf]
        zv = [(a - h * b - m) / s for a, b in zip(va, vb)]
        rows = {}
        for L in LINES:
            rf = E.run(fa, fb, h, zf, sets, enter=L, leave=LEAVE, hold=HOLD)
            rv = E.run(va, vb, h, zv, sets, enter=L, leave=LEAVE, hold=HOLD)

            def pack(r):
                tl = r["trade_list"]
                return {"ผล": _r(r["net"]), "ไม้": r["trades"], "ชนะ": r["wins"], "ค่าธรรมเนียม": _r(r["costs"]),
                        "ครบเวลา": sum(1 for t in tl if t["reason"] == "time"), "ค้าง": abs(r["open"]),
                        "ลดลงมากสุด": _r(r["max_drawdown"]),
                        "กำไรต่อไม้": _r(sum(t["pnl"] for t in tl) / max(1, len(tl)))}
            rows[str(L).replace(".", "_")] = {"เส้น": L, "เลือก": pack(rf), "ตรวจ": pack(rv)}
        key = f"{an}-{bn}"
        best_f = max(rows.values(), key=lambda r: r["เลือก"]["ผล"])
        best_v = max(rows.values(), key=lambda r: r["ตรวจ"]["ผล"])
        out[key] = {"h": h, "Mean": _r(m), "SD": _r(s), "phi": _r(S.ar1(xf)["phi"], 3),
                    "ครึ่งชีวิต": _r(S.half_life(S.ar1(xf)["phi"]), 1), "ชุด": sets, "แถว": rows,
                    "ดีสุดเลือก": best_f["เส้น"], "ดีสุดตรวจ": best_v["เส้น"],
                    "Zตรวจเฉลี่ย": _r(S.mean(zv)), "Zตรวจต่ำสุด": _r(min(zv)), "Zตรวจสูงสุด": _r(max(zv)),
                    "Zเลือกต่ำสุด": _r(min(zf)), "Zเลือกสูงสุด": _r(max(zf)),
                    "วันZตรวจเกิน1": sum(1 for z in zv if abs(z) >= 1),
                    "วันZตรวจในครึ่ง": sum(1 for z in zv if abs(z) <= LEAVE),
                    "วันZเลือกในครึ่ง": sum(1 for z in zf if abs(z) <= LEAVE),
                    "Xตรวจเฉลี่ย": _r(S.mean([a - h * b for a, b in zip(va, vb)]))}
        if key == "LTC-DOT":
            pts = list(range(0, len(zf), 7)) + [len(zf) - 1]
            ptv = list(range(0, len(zv), 7)) + [len(zv) - 1]
            out[key]["กราฟ"] = {"z": [_r(zf[t]) for t in pts] + [_r(zv[t]) for t in ptv],
                                "i": pts + [len(zf) + t for t in ptv], "แบ่ง": len(zf), "รวม": len(zf) + len(zv)}
    return out


def _sim_twin():
    """คู่จำลองแบบ LTC–DOT: เชือก φ 0.97 คงที่ · h และไม้บรรทัดประมาณจาก 731 วันแรก · เส้นดีสุดช่วงแรกตรงกับช่วงหลังกี่โลก"""
    phi = 0.97
    agree, gaps, rows = 0, [], {L: {"f": [], "v": []} for L in LINES}
    bestf, bestv = [], []
    for s in M.ROBUST_SEEDS:
        w = M.price_pair(seed=s, n=F_DAYS + V_DAYS, h=2, phi=phi, sd=_sdz(phi))
        A, B = w["A"], w["B"]
        h = S.ols(B[:F_DAYS], A[:F_DAYS])["slope"]
        xf = [a - h * b for a, b in zip(A[:F_DAYS], B[:F_DAYS])]
        m, sd = S.mean(xf), S.sd(xf)
        z = [(a - h * b - m) / sd for a, b in zip(A, B)]
        res = {}
        for L in LINES:
            rf = E.run(A[:F_DAYS], B[:F_DAYS], h, z[:F_DAYS], SETS, enter=L, leave=LEAVE, hold=HOLD)
            rv = E.run(A[F_DAYS:], B[F_DAYS:], h, z[F_DAYS:], SETS, enter=L, leave=LEAVE, hold=HOLD)
            res[L] = (rf["net"], rv["net"])
            rows[L]["f"].append(rf["net"])
            rows[L]["v"].append(rv["net"])
        bf = max(LINES, key=lambda L: res[L][0])
        bv = max(LINES, key=lambda L: res[L][1])
        bestf.append(bf)
        bestv.append(bv)
        agree += bf == bv
        gaps.append(res[bf][0] * YDAYS / F_DAYS - res[bf][1])      # ต่อปี: ช่วงเลือกยาว 731 วัน
    n = len(M.ROBUST_SEEDS)
    return {"phi": phi, "ครึ่งชีวิต": _r(S.half_life(phi), 1), "โลก": n, "ตรงกัน": agree,
            "ตรงกันเปอร์เซ็นต์": _r(100 * agree / n, 0),
            "หดต่อปีมัธยฐาน": _r(statistics.median(gaps), 0),
            "เส้น": {str(L).replace(".", "_"): {"เส้น": L, "เลือกมัธยฐาน": _r(statistics.median(rows[L]["f"]), 0),
                                               "ตรวจมัธยฐาน": _r(statistics.median(rows[L]["v"]), 0),
                                               "ดีสุดช่วงเลือก": bestf.count(L), "ดีสุดช่วงตรวจ": bestv.count(L)} for L in LINES}}


def extend(data, D, q):
    out = {}
    f1 = SB.load_figures("sab")["ch12"]["v2"]["ก่อนเข้า"]
    out["เล่ม1"] = {"เส้นเข้า": 2, "เส้นออก": LEAVE, "ถือ": HOLD, "ชุด": SETS, "ระยะต่อชุด": f1["ระยะต่อชุด"],
                    "กลับถึงเส้นออก": f1["กลับถึงเส้นออกได้"], "ต้นทุน": f1["ต้นทุน"], "เหลือ": f1["เหลือ"]}
    assert f1["ต้นทุน"] == HAND_COST
    hand = _hand(q)
    out["มือ"] = hand
    ou = _ou()
    out["ou"] = ou
    out["มีกรอบ"] = _threshold()
    out["สลับ"] = _regime()
    real = _real()
    out["จริง"] = real
    out["แฝด"] = _sim_twin()
    # ต้องตรงบท 5: เส้นเข้า 2 ของ LTC–DOT ช่วงตรวจ (h ตรึงจากช่วงเลือก) = ผลตรึงของบท 5
    ch5 = data.get("ch05", {}).get("จริง", {}).get("LTC-DOT", {}).get("ตรึง", {})
    if "ผล" in ch5:
        assert ch5["ผล"] == real["LTC-DOT"]["แถว"]["2"]["ตรวจ"]["ผล"], "เส้นเข้า 2 ช่วงตรวจไม่ตรงบท 5"
    ch4 = data.get("ch04", {}).get("จริง", {}).get("คู่", {}).get("LTC-DOT", {})
    out["อ้างบท4"] = {"ครึ่งชีวิต": ch4.get("ช่วงเลือก", {}).get("ครึ่งชีวิต"), "Meanเลือก": ch4.get("ช่วงเลือก", {}).get("Mean"),
                      "Meanตรวจ": ch4.get("ตรวจตรึงh", {}).get("Mean")}
    out["อ้างบท5"] = {"ตรึง": ch5.get("ผล")}
    # การนับ: แบบที่ลองบนข้อมูลจริง และการเปิดช่วงตรวจ (ต่อจากบท 6 ที่นับรวม 7 ครั้ง)
    prev = data.get("เรื่อง", {}).get("part6", {}).get("close", {}).get("สมุดวิจัย_BTC–ETH_hขยับได้_บท6", {}).get("ดูช่วงตรวจรวม", 7)
    out["นับ"] = {"เส้นที่ลอง": len(LINES), "เปิดช่วงตรวจบทนี้": 1, "ดูช่วงตรวจก่อนบทนี้": prev, "ดูช่วงตรวจรวม": prev + 1}
    # กล่อง 🧰 (ที่มา: tools/sab_research/practitioner-research.md §1.1 · §1.2 · §4 · §6 · §7 · §8.5 — ตัวเลขตามที่บันทึกไว้ ไม่ได้คำนวณ)
    out["คนทำงานจริง"] = {"ปีAL": "2010", "ALเปิด": 1.25, "ALปิดlong": 0.5, "ALปิดshort": 0.75, "ALวันกลับ": 30, "ALหน้าต่าง": 60,
                          "ปีGGR": "2006", "GGRเปิด": 2, "GGRรอวันลดล่าง": 30, "GGRรอวันลดบน": 55,
                          "ปีRLF": "2016", "RLFไม้กลับมาเปอร์เซ็นต์": 62.53, "RLFไม้กลับมาบวกเปอร์เซ็นต์": 98,
                          "ปีDF": "2010", "DFไม่กลับเปอร์เซ็นต์": 32, "ปีEGJ": "2009", "EGJวัน": 10, "EGJเดือน": 6,
                          "Chanเท่า": 3, "ปีChan": "2007",
                          "เล่มครบเวลา": 297, "เล่มออกรวม": 312}
    lt = real["LTC-DOT"]
    hl = hand["เส้น"]
    out["แบบฝึก"] = {
        "ข้อ1": {"ต้นทุน": 4, "สุทธิ": [_r(x["ไม้"] * (x["ต่อไม้"] - 4), 1) for x in hl],
                 "สุทธิต่อไม้": [_r(x["ต่อไม้"] - 4, 1) for x in hl]},
        "ข้อ2": {"ออก": 0, "ต่อไม้": [_r(x["เส้น"] * SETS, 1) for x in hl],
                 "สุทธิ": [_r(x["ไม้"] * (x["เส้น"] * SETS - HAND_COST), 1) for x in hl]},
        "ข้อ3": {"ไม้ต่อปี": ou["phi09"]["แถว"]["2"]["ไม้ต่อปี"], "กำไรต่อไม้": ou["phi09"]["แถว"]["2"]["กำไรต่อไม้"]},
        "ข้อ5": {"ผล": {k: v["เลือก"]["ผล"] for k, v in real["BTC-ETH"]["แถว"].items()}},
    }
    ex3 = ou["phi09"]["แถว"]
    out["แบบฝึก"]["ข้อ3"].update({
        "ต้นทุน8": 8, "สุทธิ": {k: _r(v["ไม้ต่อปี"] * (v["กำไรต่อไม้"] - 8), 1) for k, v in ex3.items()}})
    out["_แบบฝึก"] = [
        {"โจทย์": "(ทำตาม) ต้นทุน 4 ต่อไม้ · สุทธิของเส้น 1 / 1.5 / 2 / 2.5 บนเส้นทาง 40 วัน", "คำตอบ": out["แบบฝึก"]["ข้อ1"]["สุทธิ"][2]},
        {"โจทย์": "(เปลี่ยนเลข) ออกที่ 0 แทน 0.5 (นับไม้เท่าเดิม) · สุทธิของสี่เส้น", "คำตอบ": out["แบบฝึก"]["ข้อ2"]["สุทธิ"][2]},
        {"โจทย์": "(เปลี่ยนเงื่อนไข) โลก φ 0.9 ต้นทุนต่อไม้ 8 · เส้นไหนดีสุด", "คำตอบ": out["แบบฝึก"]["ข้อ3"]["สุทธิ"]["2"]},
        {"โจทย์": "(ตัดสินใจ) LTC–DOT ช่วงตรวจเส้น 2.5 ได้ +498.2 · เปลี่ยนการ์ดเป็น 2.5 ไหม", "คำตอบ": lt["แถว"]["2_5"]["ตรวจ"]["ผล"]},
        {"โจทย์": "(ถ่ายโอน · ข้อมูลจริง) BTC–ETH ช่วงเลือก ห้าเส้น · เส้นไหนดีสุดและแปลว่าอะไร", "คำตอบ": real["BTC-ETH"]["แถว"]["2"]["เลือก"]["ผล"]},
    ]
    out["_claims"] = [{"id": "sab2-ch07-al-thresholds",
                       "ข้อความ": "Avellaneda & Lee (2010) เปิดเมื่อ |s| > 1.25 ปิด long ที่ −0.50 ปิด short ที่ 0.75 และคัดเฉพาะชื่อที่กลับเร็วกว่า "
                                  "30 วันบนหน้าต่าง 60 วัน · GGR (2006) เปิดที่ 2 SD และการเปิดวันถัดไปทำให้กำไรลดราว 30–55 bps · "
                                  "Rad, Low & Faff (2016) ไม้ที่กลับมาบรรจบกำไรเกิน 98% ไม้ที่ไม่กลับแบกหางซ้าย",
                       "ระดับหลักฐาน": "ตีพิมพ์", "แหล่ง": "tools/sab_research/practitioner-research.md §1.1 · §1.2 · §4", "บท": [7]}]
    return out
