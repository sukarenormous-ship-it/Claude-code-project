"""เล่ม 2 บท 11 — ตะกร้าหลายขา · ตัวเลขทุกตัวของ docs/sab2-part11.html

ตอน ก  ขาที่สาม (ด้วยมือ)
       ก·1 เงื่อนไขสองข้อของเล่ม 1 (บท 8 · ภาคผนวก F §3): มูลค่าสุทธิศูนย์ + beta exposure ศูนย์ → ต้องมีขาที่สามที่ β ต่างจาก B
       ก·2 หกวันสอน (log × 100 จาก Mean): A = 0.5·B + 0.5·D + ส่วนเล็ก · dB ⟂ dD ⟂ ส่วนเล็ก (เลือกให้คิดด้วยมือได้)
           → ถดถอยคู่ A บน B ได้ 0.5 แต่ X ของคู่เดินตาม D · ตะกร้าได้ 0.5/0.5 และ X คือส่วนเล็ก · ตรวจสองทาง (ผลคูณกับ dB, dD
           เป็นศูนย์ · ขยับน้ำหนักแล้วผลรวมกำลังสองโต) · sab2_stats.ols_multi ยืนยัน
ตอน ข  ทดสอบตะกร้าและราคาที่จ่ายเพิ่ม
       ข·1 เหรียญมั่ว E ทำให้ผลรวมกำลังสองลดจาก 6 เป็น 5 เสมอ → 🎲 โลกศูนย์ (เดินสุ่มล้วน) เส้น 5% ตามจำนวนเหรียญ 2–9
           (adf_pvalue_sim n_vars = N) · ตะกร้า 9 เหรียญของต้น (BTC บน 8 เหรียญ ช่วงเลือก) ค่าสถิติ −5.02
       ข·2 ต้นทุนไปกลับตามมูลค่าสองฝั่ง · จำนวน fill · Legging Risk (แต่ละขาได้ราคาตามแผน 90% อิสระกัน → 0.9^k)
ตอน ค  🎲 โลกตะกร้าที่รู้คำตอบ (A = 0.5·B + 0.5·D + X · X เป็น AR(1) φ 0.9) · 📡 สแกนตะกร้า 3 เหรียญ ช่วงเลือก
       ทดสอบเหรียญเดี่ยวก่อน (LTC ออก) · 84 ตะกร้า × 3 ทิศ · ตะกร้าดีสุดเทียบคู่ดีสุด (ไม่มี LTC) ในช่วงตรวจ หลังต้นทุน
       (การ์ดเล่ม 1 · ไม้บรรทัดตรึง · sab2_engine.run_basket) — เปิดช่วงตรวจครั้งที่ 1 ของบท
ตอน ง  ตะกร้าแบบเบาบาง: XRP บน 8 เหรียญ → ตัดขาที่น้ำหนัก < 0.1 แล้วถดถอยใหม่จนไม่มีขาเล็ก · เส้น 5% ตามจำนวนขา ·
       ช่วงตรวจของบันได (เปิดช่วงตรวจครั้งที่ 2) · 🎲 โลกตะกร้า + เหรียญเดินสุ่มที่ไม่เกี่ยว 6 ตัว
ช่วงทดสอบสุดท้ายไม่ถูกแตะ (load_closes("formation") และ ("validation") เท่านั้น)
"""

import itertools
import math

import sab_book as SB

NF, NV = 731, 365
LEG = 500                      # ขาแรก 500 ดอลลาร์ (ทุนคู่ 1,000 ของเล่ม 1)
SEEDS = list(range(1, 31))
WORLDS_SMALL = 1000            # โลกเดินสุ่มต่อจำนวนเหรียญ (เส้น 5% ของตะกร้า 4–9 เหรียญ)
WORLDS = 2000                  # โลกเดินสุ่มของคู่และตะกร้า 3 เหรียญ (ค่า p ของข้อมูลจริง)
FILL_OK = 0.9                  # โอกาสที่ขาหนึ่งได้ราคาตามแผน (สมมติ · อิสระกัน)
SPARSE_CUT = 0.1               # ตัดขาที่น้ำหนัก (สัดส่วนเงินต่อขาแรก) เล็กกว่านี้


def _r(v, n=2):
    v = round(float(v) + 0.0, n)
    return int(v) if v == int(v) else v


def _crossings(x):
    m = sum(x) / len(x)
    s = [1 if v > m else -1 for v in x]
    return sum(1 for a, b in zip(s, s[1:]) if a != b)


def _med(v):
    v = sorted(v)
    k = len(v)
    return v[k // 2] if k % 2 else (v[k // 2 - 1] + v[k // 2]) / 2


def extend(data, D, q):
    import sab2_engine as E
    import sab2_sim as M
    import sab2_stats as S
    from sab2_realdata import load_closes

    out = {}

    # ════════════ เล่ม 1 ที่ทวน ════════════
    f1 = SB.load_figures("sab")
    c11 = f1["ch11"]["v2"]["ต้นทุน"]
    s8 = f1["ch08"]["ฉาก"]
    w8 = f1["ch08"]["สามวิธี"]
    fee_pct = c11["อัตราtakerเปอร์เซ็นต์"]                 # 0.05
    out["เล่ม1"] = {"ต่อfillเปอร์เซ็นต์": fee_pct, "เข้า": 2, "ออก": 0.5, "ถือ": 30, "ทุนคู่": 1000,
                    "บท8": {"Aมูลค่า": s8["Aมูลค่า"], "betaA": s8["betaA"], "betaB": s8["betaBTC"],
                            "Bมูลค่า": w8["มูลค่าเท่ากัน"]["มูลค่าB"], "betaexposure": w8["มูลค่าเท่ากัน"]["betaexposure"],
                            "ตลาดลง4": w8["มูลค่าเท่ากัน"]["BTCลง4"], "neutralB": w8["betaneutral"]["มูลค่าB"],
                            "neutralสุทธิ": w8["betaneutral"]["มูลค่าสุทธิ"]}}
    A1, bA, bB = s8["Aมูลค่า"], s8["betaA"], s8["betaBTC"]

    # ════════════ ก·1 ขาที่สาม: สองสมการ ════════════
    def third(beta_d, a=A1):
        # มูลค่า: a + dB + dD = 0 · beta: bA·a + bB·dB + βD·dD = 0 → dD = −(bA − bB)·a ÷ (βD − bB)
        if beta_d == bB:
            return None
        dd = -(bA - bB) * a / (beta_d - bB)
        db = -a - dd
        mv = -4
        return {"beta": _r(beta_d), "D": _r(dd), "B": _r(db), "gross": _r(abs(a) + abs(db) + abs(dd)),
                "สุทธิ": _r(a + db + dd), "betaexp": _r(bA * a + bB * db + beta_d * dd),
                "ลง4A": _r(a * bA * mv / 100), "ลง4B": _r(db * bB * mv / 100), "ลง4D": _r(dd * beta_d * mv / 100),
                "ส่วนเกินbeta": _r((bA - bB) * a)}
    out["ขาที่สาม"] = {"b2": third(2.0), "b05": third(0.5), "b125": third(1.25), "ส่วนเกิน": _r((bA - bB) * A1),
                      "betaต่าง": _r(bA - bB)}
    t2, t05 = out["ขาที่สาม"]["b2"], out["ขาที่สาม"]["b05"]
    rt = lambda g: _r(2 * fee_pct / 100 * g)  # noqa: E731   ไปกลับ = เปิด + ปิด = 2 × ค่าธรรมเนียม × มูลค่าสองฝั่ง
    out["ต้นทุนมือ"] = {"คู่gross": A1 + w8["มูลค่าเท่ากัน"]["มูลค่าB"], "ไปกลับคู่": rt(A1 + w8["มูลค่าเท่ากัน"]["มูลค่าB"]),
                       "ไปกลับb2": rt(t2["gross"]), "ไปกลับb05": rt(t05["gross"]),
                       "ขาดDสุทธิ": _r(A1 + t2["B"]), "ขาดDbeta": _r(bA * A1 + bB * t2["B"]),
                       "ขาดDลง4": _r(t2["ลง4A"] + t2["ลง4B"])}

    # ════════════ ก·2 หกวันสอน ════════════
    dB = [-2, 4, -2, -2, 4, -2]
    dD = [-6, -4, -2, 2, 4, 6]
    e = [1, -1, -1, 1, 1, -1]
    dA = [int(0.5 * b + 0.5 * d + x) for b, d, x in zip(dB, dD, e)]
    dot = lambda u, v: sum(a * b for a, b in zip(u, v))  # noqa: E731
    sBB, sDD, sBA, sDA, sAA = dot(dB, dB), dot(dD, dD), dot(dB, dA), dot(dD, dA), dot(dA, dA)
    wB, wD = sBA / sBB, sDA / sDD
    xp = [a - wB * b for a, b in zip(dA, dB)]
    xb = [a - wB * b - wD * d for a, b, d in zip(dA, dB, dD)]
    ssr_p, ssr_b = dot(xp, xp), dot(xb, xb)
    m = S.ols_multi([dB, dD], dA)
    mp = S.ols(dB, dA)
    nudge = 0.6
    xn = [a - wB * b - nudge * d for a, b, d in zip(dA, dB, dD)]
    out["มือ"] = {"dB": dB, "dD": dD, "dA": dA, "e": e, "BB": sBB, "DD": sDD, "BA": sBA, "DA": sDA, "AA": sAA,
                  "BD": dot(dB, dD), "wB": _r(wB), "wD": _r(wD), "Xคู่": [_r(v) for v in xp], "Xตะกร้า": [_r(v) for v in xb],
                  "SSRคู่": _r(ssr_p), "SSRตะกร้า": _r(ssr_b), "อธิบายคู่": _r(sAA - ssr_p), "อธิบายตะกร้า": _r(sAA - ssr_b),
                  "R2คู่": _r(1 - ssr_p / sAA), "R2ตะกร้า": _r(1 - ssr_b / sAA),
                  "ข้ามคู่": _crossings(xp), "ข้ามตะกร้า": _crossings(xb),
                  "eB": dot(xb, dB), "eD": dot(xb, dD), "ขยับwD": nudge, "SSRขยับ": _r(dot(xn, xn)),
                  "ขยับส่วนเพิ่ม": _r((nudge - wD) ** 2 * sDD),
                  "Xคู่ครึ่งแรก": _r(sum(xp[:3]) / 3), "Xคู่ครึ่งหลัง": _r(sum(xp[3:]) / 3),
                  "ols": {"wB": _r(m["coef"][1]), "wD": _r(m["coef"][2]), "ค่าตัด": _r(m["coef"][0]),
                          "SSR": _r(sum(r * r for r in m["residuals"])), "คู่h": _r(mp["slope"]),
                          "คู่SSR": _r(sum(r * r for r in mp["residuals"]))},
                  "เงิน": {"A": 1000, "B": _r(1000 * wB), "D": _r(1000 * wD), "สุทธิ": _r(1000 - 1000 * wB - 1000 * wD)}}

    # ════════════ ข·1 เหรียญมั่ว E · เส้นตัดสินตามจำนวนเหรียญ ════════════
    dE = [1, -1, 0, -1, 1, 0]
    sEE, sEe = dot(dE, dE), dot(dE, xb)
    wE = sEe / sEE
    xe = [v - wE * u for v, u in zip(xb, dE)]
    m4 = S.ols_multi([dB, dD, dE], dA)
    out["เหรียญมั่ว"] = {"dE": dE, "EE": sEE, "Ee": sEe, "wE": _r(wE), "SSR": _r(dot(xe, xe)), "ลด": _r(ssr_b - dot(xe, xe)),
                        "ลดเปอร์เซ็นต์": _r(100 * (ssr_b - dot(xe, xe)) / ssr_b, 0), "EB": dot(dE, dB), "ED": dot(dE, dD),
                        "olsSSR": _r(sum(r * r for r in m4["residuals"])), "olswE": _r(m4["coef"][3])}

    crit_rows = []
    for k in range(2, 10):
        nw = WORLDS if k <= 3 else WORLDS_SMALL
        null = S.adf_null(NF, nw, 1, 0, k)
        crit_rows.append({"N": k, "เส้น5": _r(null[int(0.05 * nw) - 1]), "เส้น1": _r(null[int(0.01 * nw) - 1]),
                          "มัธยฐาน": _r(_med(null)), "โลก": nw})
    out["เส้นตามขา"] = {"แถว": crit_rows, "N": [r["N"] for r in crit_rows], "เส้น5": [r["เส้น5"] for r in crit_rows],
                        "มัธยฐาน": [r["มัธยฐาน"] for r in crit_rows],
                        "Mac2": _r(S.adf_crit(NF - 1, 2)["5%"]), "Mac3": _r(S.adf_crit(NF - 1, 3)["5%"]),
                        "Mac3_1": _r(S.adf_crit(NF - 1, 3)["1%"]), "Mac2_1": _r(S.adf_crit(NF - 1, 2)["1%"])}

    # ════════════ ข้อมูลจริง (ช่วงเลือก) ════════════
    dates_f, f = load_closes("formation")
    dates_v, v = load_closes("validation")
    coins = list(f)
    L = {c: S.logs(f[c]) for c in coins}
    single = {c: S.adf(L[c]) for c in coins}
    out["เดี่ยว"] = {c: {"stat": _r(single[c]["stat"]), "pเปอร์เซ็นต์": _r(100 * single[c]["pvalue"], 1)} for c in coins}
    out["เดี่ยว"]["เส้น5"] = _r(single["BTC"]["crit"]["5%"])
    nolt = [c for c in coins if not single[c]["reject5"]]                 # LTC ออก

    def psim(stat, k):
        return S.adf_pvalue_sim(stat, NF, worlds=WORLDS if k <= 3 else WORLDS_SMALL, n_vars=k)

    # ตะกร้าของต้น: BTC บน 8 เหรียญที่ไม่ผ่านเดี่ยว
    ton_x = [c for c in nolt if c != "BTC"]
    eg_ton = S.engle_granger_multi(L["BTC"], [L[c] for c in ton_x])
    p_ton = psim(eg_ton["stat"], 9)
    out["ต้น"] = {"stat": _r(eg_ton["stat"]), "p": _r(p_ton["pvalue"], 2), "pเปอร์เซ็นต์": _r(100 * p_ton["pvalue"], 0),
                 "เส้น5": _r(p_ton["crit"]["5%"]), "ขา": 1 + len(ton_x), "ไม่มี": "LTC",
                 "Mac2": out["เส้นตามขา"]["Mac2"], "ผ่านคู่": eg_ton["stat"] < S.adf_crit(NF - 1, 2)["5%"],
                 "fill": 2 * (1 + len(ton_x))}

    # ════════════ ข·2 ต้นทุนและ Legging Risk ════════════
    def legs_row(k):
        return {"ขา": k, "fillไปกลับ": 2 * k, "ครบ": _r(FILL_OK ** k), "ครบเปอร์เซ็นต์": _r(100 * FILL_OK ** k, 0),
                "พลาดอย่างน้อยหนึ่ง": _r(100 - 100 * FILL_OK ** k, 0)}
    out["ขาพลาด"] = {"p": FILL_OK, "pเปอร์เซ็นต์": int(100 * FILL_OK), "k2": legs_row(2), "k3": legs_row(3), "k5": legs_row(5),
                    "k9": legs_row(9)}

    # ════════════ 📡 สแกนตะกร้า 3 เหรียญ ════════════
    crit3 = S.adf_crit(NF - 1, 3)["5%"]
    scan, scan_ltc = [], []
    tests = 0
    for combo in itertools.combinations(coins, 3):
        best = None
        for y in combo:
            xs = [c for c in combo if c != y]
            r = S.engle_granger_multi(L[y], [L[x] for x in xs])
            tests += 1
            if best is None or r["stat"] < best["stat"]:
                best = {"stat": r["stat"], "y": y, "xs": xs, "w": r["weights"]}
        (scan_ltc if "LTC" in combo else scan).append(best)
    scan.sort(key=lambda r: r["stat"])
    scan_ltc.sort(key=lambda r: r["stat"])
    n_free = len(scan)
    pass_free = [r for r in scan if r["stat"] < crit3]
    pass_ltc = [r for r in scan_ltc if r["stat"] < crit3]
    out["สแกน"] = {"ตะกร้าทั้งหมด": n_free + len(scan_ltc), "ตะกร้ามีLTC": len(scan_ltc), "ผ่านมีLTC": len(pass_ltc),
                  "ตะกร้าไม่มีLTC": n_free, "ทดสอบไม่มีLTC": 3 * n_free, "ผ่านไม่มีLTC": len(pass_free),
                  "โชคไม่มีLTC": _r(0.05 * 3 * n_free, 1), "เส้น5": _r(crit3),
                  "บนสุดรวม": {"stat": _r(scan_ltc[0]["stat"] if scan_ltc[0]["stat"] < scan[0]["stat"] else scan[0]["stat"]),
                              "ชื่อ": "/".join([scan_ltc[0]["y"]] + scan_ltc[0]["xs"])},
                  "ผ่านมีXRP": sum(1 for r in pass_free if "XRP" in [r["y"]] + r["xs"]),
                  "แถว": [{"ชื่อ": r["y"] + " บน " + " กับ ".join(r["xs"]), "stat": _r(r["stat"]),
                           "w": [_r(w) for w in r["w"]]} for r in scan[:5]]}

    # คู่ดีสุดที่ไม่มี LTC (Engle–Granger สองทิศ)
    pairs = []
    for a, b in itertools.combinations(nolt, 2):
        for y, x in ((a, b), (b, a)):
            r = S.engle_granger(L[y], L[x])
            pairs.append((r["stat"], y, x))
    pairs.sort()
    bp = pairs[0]
    top = scan[0]

    def evaluate(y, xs, look=True, zpath=False):
        eg = S.engle_granger_multi(L[y], [L[x] for x in xs])
        w, res = eg["weights"], eg["residuals"]
        mu, sd = S.mean(res), S.sd(res)
        ar = S.ar1(res)
        py0 = f[y][-1]
        units = [1.0] + [-wi * py0 / f[x][-1] for wi, x in zip(w, xs)]
        sets = LEG / py0
        legs_val = [LEG] + [-wi * LEG for wi in w]                        # ดอลลาร์ต่อขา ณ ปิดช่วงเลือก (long ตะกร้า)
        zf = [(L[y][t] - sum(wi * L[x][t] for wi, x in zip(w, xs)) - eg["intercept"] - mu) / sd for t in range(NF)]
        rf = E.run_basket([f[y]] + [f[x] for x in xs], units, zf, sets=sets)
        row = {"ชื่อ": y + " บน " + " กับ ".join(xs), "ขา": 1 + len(xs), "stat": _r(eg["stat"]),
               "w": [_r(x) for x in w], "hl": _r(S.half_life(ar["phi"]), 1), "sdเปอร์เซ็นต์": _r(100 * sd, 1),
               "เลือกnet": _r(rf["net"], 1), "เลือกไม้": rf["trades"],
               "gross": _r(sum(abs(x) for x in legs_val), 1), "สุทธิ": _r(sum(legs_val), 1),
               "ไปกลับ": _r(2 * fee_pct / 100 * sum(abs(x) for x in legs_val)), "fillไปกลับ": 2 * (1 + len(xs)),
               "ดอลลาร์ขา": [_r(x, 1) for x in legs_val]}
        pv = psim(eg["stat"], 1 + len(xs))
        row.update({"p": _r(pv["pvalue"], 3), "pเปอร์เซ็นต์": _r(100 * pv["pvalue"], 1), "เส้น5": _r(pv["crit"]["5%"])})
        if look:
            zv = [(math.log(v[y][t]) - sum(wi * math.log(v[x][t]) for wi, x in zip(w, xs)) - eg["intercept"] - mu) / sd
                  for t in range(NV)]
            rv = E.run_basket([v[y]] + [v[x] for x in xs], units, zv, sets=sets)
            row.update({"ตรวจnet": _r(rv["net"], 1), "ตรวจไม้": rv["trades"], "ตรวจต้นทุน": _r(rv["costs"], 1),
                        "ตรวจก่อนต้นทุน": _r(rv["net"] + rv["costs"], 1), "ตรวจค้าง": rv["open"],
                        "ตรวจหมดเวลา": sum(1 for t in rv["trade_list"] if t["reason"] == "time"),
                        "ตรวจZเฉลี่ย": _r(S.mean(zv)), "ตรวจZสูงสุด": _r(max(zv), 1),
                        "ตรวจequityต่ำสุด": _r(rv["min_equity"], 1)})
            if zpath:
                row["zpath"] = [_r(x) for x in zf + zv]
        return row

    best_b = evaluate(top["y"], top["xs"], zpath=True)
    best_p = evaluate(bp[1], [bp[2]], zpath=True)
    xrp_v = (v["XRP"][-1] / v["XRP"][0] - 1) * 100
    out["จริง"] = {"วันเลือก": NF, "วันตรวจ": NV, "เริ่มเลือก": dates_f[0], "จบเลือก": dates_f[-1],
                  "เริ่มตรวจ": dates_v[0], "จบตรวจ": dates_v[-1], "เหรียญ": len(coins),
                  "ตะกร้า": best_b, "คู่": best_p, "XRPตรวจเปอร์เซ็นต์": _r(xrp_v, 0),
                  "ตะกร้าแย่กว่า": _r(best_b["ตรวจnet"] - best_p["ตรวจnet"], 1),
                  "ต้นทุนเพิ่ม": _r(best_b["ตรวจต้นทุน"] - best_p["ตรวจต้นทุน"], 1),
                  "แกนวัน": {"เลือก0": dates_f[0], "ตรวจ0": dates_v[0], "จบ": dates_v[-1], "n": NF + NV}}

    # ════════════ ง เบาบาง: XRP บน 8 เหรียญ ════════════
    y0 = top["y"]
    xs_full = [c for c in nolt if c != y0]
    full = S.engle_granger_multi(L[y0], [L[x] for x in xs_full])
    t_full = full["ols"]["t"][1:]
    se_full = full["ols"]["se"][1:]
    ladder_sets = [xs_full]
    cur = xs_full
    while True:
        r = S.engle_granger_multi(L[y0], [L[x] for x in cur])
        keep = [x for x, w in zip(cur, r["weights"]) if abs(w) >= SPARSE_CUT]
        if keep == cur or not keep:
            break
        ladder_sets.append(keep)
        cur = keep
    ladder = [evaluate(y0, xs) for xs in ladder_sets]
    if best_p["ชื่อ"] not in [r["ชื่อ"] for r in ladder] and bp[1] == y0:
        ladder.append({k: val for k, val in best_p.items() if k != "zpath"})
    out["เบาบาง"] = {"ตัวแปร": y0, "เต็ม": {"ชื่อ": xs_full, "w": [_r(w) for w in full["weights"]],
                                          "se": [_r(s) for s in se_full], "t": [_r(t, 1) for t in t_full]},
                     "ตัด": SPARSE_CUT, "บันได": ladder, "ขาบันได": [r["ขา"] for r in ladder],
                     "ปลายตรงตะกร้าสแกน": sorted(ladder_sets[-1]) == sorted(top["xs"]),
                     "ขาที่ตัดรอบแรก": [x for x in xs_full if x not in ladder_sets[1]] if len(ladder_sets) > 1 else []}
    # มือ: น้ำหนัก ÷ SE ของขาเล็กสุดและใหญ่สุด
    i_small = min(range(len(xs_full)), key=lambda i: abs(full["weights"][i]))
    i_big = max(range(len(xs_full)), key=lambda i: abs(full["weights"][i]))
    out["เบาบาง"]["เล็กสุด"] = {"ชื่อ": xs_full[i_small], "w": _r(full["weights"][i_small], 3), "se": _r(se_full[i_small]),
                               "t": _r(t_full[i_small], 1), "ดอลลาร์": _r(abs(full["weights"][i_small]) * LEG, 1)}
    ws_, ss_ = round(full["weights"][i_small], 2), round(se_full[i_small], 2)
    wb_, sb_ = round(full["weights"][i_big], 2), round(se_full[i_big], 2)
    out["เบาบาง"]["เลขปัด"] = {"เล็กw": _r(ws_), "เล็กดอลลาร์": _r(abs(ws_) * LEG), "เล็กt": _r(ws_ / ss_),
                               "ใหญ่w": _r(wb_), "ใหญ่ดอลลาร์": _r(abs(wb_) * LEG), "ใหญ่t": _r(wb_ / sb_, 1)}
    out["เบาบาง"]["ใหญ่สุด"] = {"ชื่อ": xs_full[i_big], "w": _r(full["weights"][i_big]), "se": _r(se_full[i_big]),
                               "t": _r(t_full[i_big], 1), "ดอลลาร์": _r(abs(full["weights"][i_big]) * LEG, 1)}

    # ════════════ 🎲 โลกตะกร้าที่รู้คำตอบ ════════════
    n_all = NF + NV
    crit2 = S.adf_crit(NF - 1, 2)["5%"]
    crit9 = S.adf_null(NF, WORLDS_SMALL, 1, 0, 9)[int(0.05 * WORLDS_SMALL) - 1]
    sim = {"คู่ผ่าน": 0, "ตะกร้าผ่าน": 0, "wB": [], "wD": [], "hl": [], "netB": [], "netP": [], "costB": [], "costP": [],
           "เต็มผ่าน": 0, "เบาบางตรง": 0, "หลอกมัธยฐาน": [], "sdเต็ม": [], "sdสาม": [], "netเต็ม": [], "netสาม": [],
           "sdในเต็ม": [], "sdในสาม": [], "ไม้เต็ม": [], "ไม้สาม": []}
    example = None
    for s in SEEDS:
        sp = M.stationary_pair(seed=s, n=n_all, phi=0.9)
        dw = M.random_walk_pair(seed=1000 + s, n=n_all)["logB"]
        lb, x = sp["logB"], sp["X"]
        la = [math.log(2.0) + 0.5 * b + 0.5 * d + xx for b, d, xx in zip(lb, dw, x)]
        PA, PB, PD = [math.exp(u) for u in la], [math.exp(u) for u in lb], [math.exp(u) for u in dw]
        egp = S.engle_granger(la[:NF], lb[:NF])
        egb = S.engle_granger_multi(la[:NF], [lb[:NF], dw[:NF]])
        sim["คู่ผ่าน"] += egp["reject5"]
        sim["ตะกร้าผ่าน"] += egb["stat"] < crit3
        sim["wB"].append(egb["weights"][0])
        sim["wD"].append(egb["weights"][1])
        sim["hl"].append(S.half_life(S.ar1(egb["residuals"])["phi"]))

        def bt(prices_log, prices, w, icpt, res):
            mu, sd = S.mean(res), S.sd(res)
            z = [(prices_log[0][t] - sum(wi * prices_log[j + 1][t] for j, wi in enumerate(w)) - icpt - mu) / sd
                 for t in range(NF, n_all)]
            p0 = prices[0][NF - 1]
            units = [1.0] + [-wi * p0 / prices[j + 1][NF - 1] for j, wi in enumerate(w)]
            return E.run_basket([p[NF:] for p in prices], units, z, sets=LEG / p0)

        rb = bt([la, lb, dw], [PA, PB, PD], egb["weights"], egb["intercept"], egb["residuals"])
        rp = bt([la, lb], [PA, PB], [egp["h"]], egp["intercept"], egp["residuals"])
        sim["netB"].append(rb["net"])
        sim["netP"].append(rp["net"])
        sim["costB"].append(rb["costs"])
        sim["costP"].append(rp["costs"])
        if s == SEEDS[0]:
            example = {"คู่": [_r(100 * u, 1) for u in egp["residuals"][::3]],
                       "ตะกร้า": [_r(100 * u, 1) for u in egb["residuals"][::3]],
                       "คู่stat": _r(egp["stat"]), "ตะกร้าstat": _r(egb["stat"]), "ทุก": 3, "n": NF}
        # เบาบาง: เพิ่มเหรียญเดินสุ่มที่ไม่เกี่ยว 6 ตัว
        junk = [M.random_walk_pair(seed=2000 + 10 * s + j, n=n_all)["logB"] for j in range(6)]
        cols = [lb[:NF], dw[:NF]] + [jj[:NF] for jj in junk]
        egf = S.engle_granger_multi(la[:NF], cols)
        sim["เต็มผ่าน"] += egf["stat"] < crit9
        sim["หลอกมัธยฐาน"].append(_med([abs(w) for w in egf["weights"][2:]]))
        cur = list(range(8))
        while True:
            r = S.engle_granger_multi(la[:NF], [cols[i] for i in cur])
            keep = [i for i, w in zip(cur, r["weights"]) if abs(w) >= SPARSE_CUT]
            if keep == cur or not keep:
                break
            cur = keep
        sim["เบาบางตรง"] += cur == [0, 1]

        def oos_sd(w, icpt, series):
            res = [la[t] - icpt - sum(wi * s_[t] for wi, s_ in zip(w, series)) for t in range(NF, n_all)]
            return S.sd(res)
        sim["sdเต็ม"].append(oos_sd(egf["weights"], egf["intercept"], [lb, dw] + junk))
        sim["sdสาม"].append(oos_sd(egb["weights"], egb["intercept"], [lb, dw]))
        rfull = bt([la, lb, dw] + junk, [PA, PB, PD] + [[math.exp(u) for u in jj] for jj in junk],
                   egf["weights"], egf["intercept"], egf["residuals"])
        sim["netเต็ม"].append(rfull["net"])
        sim["netสาม"].append(rb["net"])
        sim["sdในเต็ม"].append(S.sd(egf["residuals"]))
        sim["sdในสาม"].append(S.sd(egb["residuals"]))
        sim["ไม้เต็ม"].append(rfull["trades"])
        sim["ไม้สาม"].append(rb["trades"])
    ns = len(SEEDS)
    out["จำลอง"] = {"โลก": ns, "phi": 0.9, "hlจริง": _r(math.log(2) / -math.log(0.9), 1), "wจริง": 0.5,
                    "คู่ผ่าน": sim["คู่ผ่าน"], "ตะกร้าผ่าน": sim["ตะกร้าผ่าน"],
                    "wBมัธยฐาน": _r(_med(sim["wB"])), "wBต่ำ": _r(min(sim["wB"])), "wBสูง": _r(max(sim["wB"])),
                    "wDมัธยฐาน": _r(_med(sim["wD"])), "wDต่ำ": _r(min(sim["wD"])), "wDสูง": _r(max(sim["wD"])),
                    "hlมัธยฐาน": _r(_med(sim["hl"]), 1),
                    "netตะกร้ามัธยฐาน": _r(_med(sim["netB"]), 1), "netตะกร้าต่ำ": _r(min(sim["netB"]), 1),
                    "netตะกร้าสูง": _r(max(sim["netB"]), 1), "ตะกร้าบวก": sum(1 for x in sim["netB"] if x > 0),
                    "netคู่มัธยฐาน": _r(_med(sim["netP"]), 1), "netคู่ต่ำ": _r(min(sim["netP"]), 1),
                    "netคู่สูง": _r(max(sim["netP"]), 1), "คู่บวก": sum(1 for x in sim["netP"] if x > 0),
                    "ต้นทุนตะกร้ามัธยฐาน": _r(_med(sim["costB"]), 1), "ต้นทุนคู่มัธยฐาน": _r(_med(sim["costP"]), 1),
                    "ตัวอย่าง": example, "เส้น9": _r(crit9), "เส้น3": _r(crit3), "เส้น2": _r(crit2),
                    "เต็มผ่าน": sim["เต็มผ่าน"], "เบาบางตรง": sim["เบาบางตรง"],
                    "หลอกมัธยฐาน": _r(_med(sim["หลอกมัธยฐาน"])),
                    "sdเต็มมัธยฐาน": _r(100 * _med(sim["sdเต็ม"])), "sdสามมัธยฐาน": _r(100 * _med(sim["sdสาม"])),
                    "sdเต็มแย่กว่า": sum(1 for a, b in zip(sim["sdเต็ม"], sim["sdสาม"]) if a > b),
                    "netเต็มมัธยฐาน": _r(_med(sim["netเต็ม"]), 1), "netสามมัธยฐาน": _r(_med(sim["netสาม"]), 1),
                    "เต็มแย่กว่า": sum(1 for a, b in zip(sim["netเต็ม"], sim["netสาม"]) if a < b),
                    "sdในเต็มมัธยฐาน": _r(100 * _med(sim["sdในเต็ม"])), "sdในสามมัธยฐาน": _r(100 * _med(sim["sdในสาม"])),
                    "ไม้เต็มมัธยฐาน": _r(_med(sim["ไม้เต็ม"]), 1), "ไม้สามมัธยฐาน": _r(_med(sim["ไม้สาม"]), 1),
                    "กว้างขึ้นเต็มเปอร์เซ็นต์": _r(100 * (_med(sim["sdเต็ม"]) / _med(sim["sdในเต็ม"]) - 1), 0),
                    "กว้างขึ้นสามเปอร์เซ็นต์": _r(100 * (_med(sim["sdสาม"]) / _med(sim["sdในสาม"]) - 1), 0)}

    # โลกศูนย์ 9 เหรียญเดินสุ่ม: 84 ตะกร้า × 3 ทิศ ผ่านโดยบังเอิญกี่ตะกร้า
    zero = []
    for s in SEEDS:
        ws = [M.random_walk_pair(seed=3000 + 10 * s + j, n=NF)["logB"] for j in range(9)]
        cnt = 0
        for combo in itertools.combinations(range(9), 3):
            st = min(S.engle_granger_multi(ws[yy], [ws[x] for x in combo if x != yy])["stat"] for yy in combo)
            cnt += st < crit3
        zero.append(cnt)
    out["โลกศูนย์"] = {"เหรียญ": 9, "ตะกร้า": 84, "มัธยฐาน": _r(_med(zero), 1), "เฉลี่ย": _r(sum(zero) / len(zero), 1),
                      "ต่ำ": min(zero), "สูง": max(zero), "โลก": len(zero),
                      "ศูนย์โลก": sum(1 for z in zero if z == 0), "สองหรือน้อยกว่า": sum(1 for z in zero if z <= 2)}

    # ════════════ 🧰 คนทำงานจริง (ที่มา: practitioner-research.md · ตัวเลขตามที่บันทึก ไม่ได้คำนวณ) ════════════
    out["คนทำงานจริง"] = {
        "ปีCK": "2018", "ปีCKWP": "2016", "CKเดือนเลือก": 48, "CKปีเริ่ม": "1990", "CKปีจบ": "2015", "CKต่อปีเปอร์เซ็นต์": 12,
        "CKปีเสื่อม": "2010", "ปีLN": "2019", "LNเหรียญ": 4, "LNปีข้อมูลเริ่ม": "2017", "LNปีข้อมูลจบ": "2018",
        "ปีGK": "2024", "GKเหรียญ": 10, "GKชนะ": 5, "GKทั้งหมด": 6, "CKเกณฑ์เปอร์เซ็นต์": 5,
    }

    # ════════════ ดูช่วงตรวจ ════════════
    out["ดูช่วงตรวจ"] = 2

    # ════════════ แบบฝึก ════════════
    exr = {}
    r3 = third(3.0)
    exr["ข้อ1"] = r3
    p95 = 0.95
    exr["ข้อ2"] = {"p": p95, "k2": _r(p95 ** 2), "k3": _r(p95 ** 3), "k9": _r(p95 ** 9),
                   "k2เปอร์เซ็นต์": _r(100 * p95 ** 2, 0), "k3เปอร์เซ็นต์": _r(100 * p95 ** 3, 0),
                   "k9เปอร์เซ็นต์": _r(100 * p95 ** 9, 0), "k2ดิบ": _r(p95 ** 2, 4), "บวกตรง": _r(1 - 9 * (1 - p95))}
    dE2 = [0, -1, 0, 2, 1, -2]
    s22, s2e = dot(dE2, dE2), dot(dE2, xb)
    exr["ข้อ3"] = {"dE": dE2, "EE": s22, "Ee": s2e, "w": _r(s2e / s22), "SSR": _r(ssr_b - s2e ** 2 / s22),
                   "ลดได้": _r(s2e ** 2 / s22),
                   "ลดเปอร์เซ็นต์": _r(100 * (s2e ** 2 / s22) / ssr_b, 0), "EB": dot(dE2, dB), "ED": dot(dE2, dD)}
    out["แบบฝึก"] = exr
    out["_แบบฝึก"] = [
        {"โจทย์": "(ทำตาม) ขาที่สาม β 3 → มูลค่า D, B · gross · ตลาดลง 4%", "คำตอบ": r3["D"]},
        {"โจทย์": "(เปลี่ยนเลข) แต่ละขาได้ราคาตามแผน 95% → ครบ 2 / 3 / 9 ขา", "คำตอบ": exr["ข้อ2"]["k3"]},
        {"โจทย์": "(เปลี่ยนเงื่อนไข) เพิ่มเหรียญมั่ว E อีกตัว → น้ำหนัก · ผลรวมกำลังสองที่เหลือ", "คำตอบ": exr["ข้อ3"]["SSR"]},
        {"โจทย์": "(ตัดสินใจ) ตะกร้า 9 เหรียญของต้น ค่าสถิติ −5.02", "คำตอบ": out["ต้น"]["เส้น5"]},
        {"โจทย์": "(ถ่ายโอน · ข้อมูลจริง) ตะกร้าบนสุดของ 120 ตะกร้ามี LTC", "คำตอบ": out["สแกน"]["ผ่านมีLTC"]},
    ]
    out["_claims"] = [
        {"id": "sab2-ch11-crit-n",
         "ข้อความ": "เส้น 5% ของ Engle–Granger เลื่อนลงเมื่อจำนวนตัวแปรในตะกร้าเพิ่ม (MacKinnon 2010 case c: N = 2 ราว −3.34 · "
                    "N = 3 ราว −3.75 ที่ 730 แถว) · เล่มยืนยันด้วยโลกเดินสุ่ม 1,000–2,000 โลกต่อ N",
         "ระดับหลักฐาน": "ตีพิมพ์", "แหล่ง": "MacKinnon, J.G. (2010) Critical Values for Cointegration Tests, QED WP 1227 · "
                                                   "tools/sab2_stats.py adf_crit / adf_pvalue_sim", "บท": [11]},
    ]
    return out
