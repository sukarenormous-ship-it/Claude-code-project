"""เล่ม 2 บท 6 — เชื่อข้อมูลใหม่แค่ไหน: Kalman แบบคิดด้วยมือ · ตัวเลขทุกตัวของ docs/sab2-part6.html

ตอน ก  ค่ากลางของ X (หนึ่งมิติ) · สองก้อนความไม่แน่นอน: ค่าเดิม SD 1 (P = 1) กับค่าที่เห็น SD 2 (R = 4)
       → ลองน้ำหนัก 0 · 0.1 · 0.2 · 0.3 · 0.5 · 1 → ก้นชามที่ 0.2 = P ÷ (P + R)
       ห้าวันด้วยมือ (Q = 1 · R = 4 · เริ่ม 10.6 กับ P 0.8) ปัดสองตำแหน่งทุกขั้นแบบที่ผู้อ่านคิดตาม
       → ตรวจกับ sab2_stats.kalman_hedge (x = 1 ทุกวัน = ค่ากลางหนึ่งมิติ) · K นิ่งที่ 0.39 · Q = 0 → ค่าเฉลี่ยธรรมดา
ตอน ข  h (ไม่ใช่ค่ากลาง) · ค่าที่อ่านได้ของวันนั้น = การขยับ A ÷ การขยับ B สั่น R ÷ (การขยับ B)²
       สามวันด้วยมือ (R = 1 · Q = 0.01 · เริ่ม h 0.8 กับ P 0.24) ตรวจสองแบบ (แบบค่าที่อ่าน vs แบบ kalman_hedge)
       🎲 drifting_h_pair (h 1.0 → 1.5 · 731 วัน) กับ stationary_pair (h คงที่ 1) · seed 1–30 · Kalman บนการขยับ log รายวัน
       เทียบ rolling 20 / 60 / 120 วัน · วัดระยะห่างเฉลี่ยจาก h จริง (ค่าสัมบูรณ์) ตั้งแต่วันที่ 121
ตอน ค  📡 BTC (A) บน ETH (B) การขยับ log รายวัน · ช่วงเลือก (ประเมินวันที่ 121 เป็นต้นไป) และช่วงตรวจ (เปิดหนึ่งครั้ง ·
       ตัวกรองเดินต่อเนื่องจากช่วงเลือก · rolling ใช้หน้าต่างย้อนเข้าช่วงเลือกได้) · R จาก Regression ทั้งช่วงเลือก
       · ทุก h เป็นค่า "ก่อนเห็นวันนั้น" (beta_prior / หน้าต่างที่จบเมื่อวาน) → SD ของเงินรายวันของชุด BTC 10,000 ดอลลาร์
       คู่ short ETH h × 10,000 ดอลลาร์ · การเปลี่ยน h เฉลี่ยต่อวัน → ค่าธรรมเนียมปรับ hedge ต่อปี (fee 0.05% เท่า sab2_engine)
ช่วงทดสอบสุดท้ายไม่ถูกแตะ (load_closes("formation") และ ("validation") เท่านั้น)
"""

import math

import sab_book as SB

Q_SDS = (0, 0.01, 0.03, 0.1)     # SD ของการขยับของ h ต่อวันที่ "บอก" ตัวกรอง → q = sd²
WINDOWS = (20, 60, 120)
START = 120                             # วันแรกที่ทุกวิธีมีค่า (rolling 120 ต้องใช้ 120 วันก่อน) · index ของการขยับ
FEE = 0.0005                            # ค่าธรรมเนียมต่อขาที่ปรับ (เท่า sab2_engine.run ค่าเริ่มต้น)
NOTIONAL = 10000                        # ขา BTC 10,000 ดอลลาร์


def _kn(sdq):
    """ชื่อคีย์ของ Kalman ตาม sd ของ Q (ห้ามมีจุดในคีย์ เพราะ data-key ใช้จุดคั่นชั้น) · 0.01 → k001"""
    return "k" + str(sdq).replace(".", "")


def _r(v, n=2):
    v = round(float(v) + 0.0, n)
    return int(v) if v == int(v) else v


def extend(data, D, q):
    import sab2_sim as M
    import sab2_stats as S
    from sab2_realdata import load_closes

    from decimal import ROUND_HALF_UP

    def qd(x, n=2):
        """ปัดครึ่งขึ้นแบบที่ผู้อ่านคิดตามด้วยมือ คืน Decimal (ใช้ต่อในขั้นถัดไป)"""
        d = x if isinstance(x, D) else D(str(x))
        return d.quantize(D(1).scaleb(-n), rounding=ROUND_HALF_UP)

    out = {}

    # ════════════ เล่ม 1 ที่ทวน ════════════
    fig1 = SB.load_figures("sab")
    v1 = fig1["ch14"]["v2"]["ไม้บรรทัดเลื่อน"]
    s13 = fig1["ch13"]["v2"]["sdหน้า"][1]
    out["ปีKalman"] = "1960"
    # กล่อง 🧰 (ที่มา: tools/sab_research/practitioner-research.md §3.1 · §6 · §7 · ตัวเลขตามที่บันทึกไว้ ไม่ได้คำนวณ)
    out["คนทำงานจริง"] = {"ปีAL": "2010", "หน้าต่างAL": 60, "ปีGGR": "2006", "ปีCK": "2018", "ปีClegg": "2014",
                          "Cleggผ่านต่อปีเปอร์เซ็นต์": 5.0, "Cleggยังผ่านปีถัดไปเปอร์เซ็นต์": 4.9, "Cleggปีเริ่ม": "2002",
                          "Cleggปีจบ": "2012", "ปีสรุปCXO": "2014", "หัวข้อPalomar": "15.4"}
    out["เส้นเข้าที่จะลอง"] = [1.5, 2, 2.5]
    out["เล่ม1"] = {"ช้า": v1["ช้า"], "X": v1["X"], "ช่วงช้าMean": [r["Mean"] for r in v1["ช่วงช้า"]],
                    "ช่วงช้าระยะ": [r["ระยะ"] for r in v1["ช่วงช้า"]],
                    "บท13": {k: s13[k] for k in ("phi", "แรงสะบัด", "phiกำลังสองปัด", "แรงสะบัดกำลังสอง", "sdกำลังสอง", "sd", "หดเหลือ")}}

    # ════════════ ตอน ก · 1 สองก้อน ════════════
    old, P1, seen, R1 = D(10), D(1), D(13), D(4)
    ws = [D("0"), D("0.1"), D("0.2"), D("0.3"), D("0.5"), D("1")]
    rows = []
    for w in ws:
        a, b = (1 - w) ** 2 * P1, w * w * R1
        rows.append({"w": float(w), "เดิมส่วน": float(qd(1 - w, 2)), "ก้อนเดิม": float(qd(a, 2)), "ก้อนใหม่": float(qd(b, 2)),
                     "รวม": float(qd(a + b, 2)), "ค่าใหม่": float(qd(old + w * (seen - old), 2))})
    K0 = P1 / (P1 + R1)
    assert min(rows, key=lambda r: r["รวม"])["w"] == float(K0)
    two = {"เดิม": 10, "P": 1, "sdเดิม": 1, "เห็น": 13, "R": 4, "sdเห็น": 2, "แถว": rows, "K": float(K0),
           "ห่าง": 3, "เลื่อน": float(K0 * 3), "ใหม่": float(old + K0 * 3), "Pใหม่": float(P1 * R1 / (P1 + R1)),
           "sdใหม่": float(qd(D(math.sqrt(0.8)), 2)), "หนึ่งลบK": float(1 - K0), "ถ่วง": float(qd((R1 * old + P1 * seen) / (P1 + R1), 2)),
           "Rคูณเดิม": 40, "Pคูณเห็น": 13, "PบวกR": 5}
    # ตัวอย่างหนึ่งแถวของก้อนความคลาดเคลื่อน (w = 0.5): ค่าเดิมพลาด +1 ค่าที่เห็นพลาด −2
    two["ตัวอย่างพลาด"] = {"เดิม": 1, "เห็น": -2, "ผสม": float(D("0.5") * 1 + D("0.5") * -2)}
    out["สองก้อน"] = two

    # ════════════ ตอน ก · 2 ห้าวันด้วยมือ (ปัดทุกขั้น) ════════════
    Q, R = D(1), D(4)
    m, P = D("10.6"), D("0.8")
    reads = [12, 11, 14, 13, 15]
    days = []
    for t, x in enumerate(reads, 1):
        Pp = qd(P + Q, 2)
        K = qd(Pp / (Pp + R), 2)
        gap = qd(D(x) - m, 2)
        move = qd(K * gap, 2)
        m_new = qd(m + move, 2)
        P_new = qd((1 - K) * Pp, 2)
        days.append({"วัน": t, "Pเดิม": float(P), "Pทาย": float(Pp), "PบวกR": float(qd(Pp + R, 2)), "K": float(K),
                     "เห็น": x, "เดิม": float(m), "ห่าง": float(gap), "เลื่อน": float(move), "ใหม่": float(m_new),
                     "หนึ่งลบK": float(qd(1 - K, 2)), "Pใหม่": float(P_new)})
        m, P = m_new, P_new
    # ตรวจกับ sab2_stats (ไม่ปัด) — ค่ากลางหนึ่งมิติ = kalman_hedge ที่ x = 1 ทุกวัน
    kf = S.kalman_hedge([1.0] * len(reads), reads, q=1.0, r=4.0, beta0=10.6, p0=0.8)
    for d, kb, kg in zip(days, kf["beta"], kf["gain"]):
        assert abs(d["ใหม่"] - kb) < 0.03 and abs(d["K"] - kg) < 0.006, (d, kb, kg)
    # ตรวจวิธีที่สอง (ถ่วงน้ำหนัก) ของวันที่ 1 จากเลขปัด
    d1 = days[0]
    w_avg = (D(str(d1["Pทาย"])) * D(d1["เห็น"]) + R * D(str(d1["เดิม"]))) / (D(str(d1["Pทาย"])) + R)
    five = {"Q": 1, "R": 4, "sdQ": 1, "sdR": 2, "เริ่ม": 10.6, "Pเริ่ม": 0.8, "เห็น": reads, "วัน": days,
            "ตรวจวัน1": {"Pคูณเห็น": float(qd(D(str(d1["Pทาย"])) * D(d1["เห็น"]), 2)), "Rคูณเดิม": float(qd(R * D(str(d1["เดิม"])), 2)),
                         "ผล": float(qd(w_avg, 2)), "PทายคูณRหารรวม": float(qd(D(str(d1["Pทาย"])) * R / (D(str(d1["Pทาย"])) + R), 2))},
            "pyค่าสุดท้าย": _r(kf["beta"][-1]), "pyKสุดท้าย": _r(kf["gain"][-1])}
    # K นิ่ง (สูตรปิด): P_ทาย = (Q + √(Q² + 4QR)) / 2 · K = P_ทาย ÷ (P_ทาย + R)
    pp = (1 + math.sqrt(1 + 16)) / 2
    k_ss = pp / (pp + 4)
    five["Pนิ่ง"] = _r(pp)
    five["Kนิ่ง"] = _r(k_ss)
    five["Pนิ่งบวกR"] = _r(_r(pp) + 4)
    five["Pหลังนิ่ง"] = _r((1 - _r(k_ss)) * _r(pp))
    five["อายุเฉลี่ย"] = _r((1 - _r(k_ss)) / _r(k_ss))
    five["หน้าต่างเทียบ"] = _r(2 / _r(k_ss) - 1, 1)
    five["อายุหน้าต่าง4"] = 1.5
    kk = _r(k_ss)
    five["น้ำหนักย้อนหลัง"] = [_r(kk * (1 - kk) ** j) for j in range(5)]
    five["อายุคูณน้ำหนักห้าวัน"] = _r(sum(j * kk * (1 - kk) ** j for j in range(5)))
    five["ครึ่งชีวิตตาม"] = _r(S.half_life(1 - _r(k_ss)), 1)
    # K คงที่ 0.2 (ความเร็วของเล่ม 1 บท 14) บนห้าวันเดียวกัน และค่าเฉลี่ยธรรมดาของห้าวัน
    m2, fixed = D("10.6"), []
    for x in reads:
        m2 = qd(m2 + D("0.2") * (D(x) - m2), 2)
        fixed.append(float(m2))
    five["Kคงที่02"] = fixed
    five["Meanห้าวัน"] = float(qd(D(sum(reads)) / 5, 2))
    out["ห้าวัน"] = five
    # กราฟ sab2-kalman-weights: น้ำหนักของข้อมูลอายุ 0–7 วัน · หน้าต่าง 4 วัน (เท่ากันแล้วตัดขาด) กับ K นิ่ง 0.39 (จางลงทีละ 1 − K)
    out["น้ำหนักอายุ"] = {"อายุ": list(range(8)), "K": kk, "หนึ่งลบK": _r(1 - kk),
                          "Kalman": [_r(kk * (1 - kk) ** j) for j in range(8)],
                          "หน้าต่าง4": [0.25] * 4 + [0] * 4, "แกน": [0, 0.1, 0.2, 0.3, 0.4]}

    # ════════════ ตอน ก · 3 Q = 0 → ค่าเฉลี่ยธรรมดา ════════════
    m, P, reads0 = D(10), D(4), [12, 11, 14, 13]
    zrows, hist = [], [D(10)]
    for x in reads0:
        K = P / (P + R)
        m = m + K * (D(x) - m)
        P = (1 - K) * P
        hist.append(D(x))
        avg = sum(hist) / len(hist)
        assert abs(m - avg) < D("1e-12")
        zrows.append({"เห็น": x, "Pทาย": float(qd(P / (1 - K), 2)), "K": float(qd(K, 2)), "Kเศษส่วน": f"1/{len(hist)}",
                      "ใหม่": float(qd(m, 2)), "Mean": float(qd(avg, 2)), "รวม": int(sum(hist)), "จำนวน": len(hist),
                      "PบวกR": float(qd(qd(P / (1 - K), 2) + R, 2))})
    out["Qศูนย์"] = {"เริ่ม": 10, "P": 4, "R": 4, "แถว": zrows}

    # ตาราง K นิ่งตาม Q ÷ R (R = 4)
    kt = []
    for ratio in (0.01, 0.1, 0.25, 1, 4):
        Qx = ratio * 4
        ppx = (Qx + math.sqrt(Qx * Qx + 16 * Qx)) / 2
        kx = ppx / (ppx + 4)
        kt.append({"QหารR": ratio, "Q": _r(Qx), "K": _r(kx), "หน้าต่าง": _r(2 / kx - 1, 1), "ครึ่งชีวิต": _r(S.half_life(1 - kx), 1)})
    out["ตารางK"] = kt

    # fails ตอน ก: ค่าที่เห็นผิดหนึ่งวัน (ไส้เทียน 30) ที่ K 0.39 · และ Q = 0 หลัง 100 วัน (K ราว 1/101)
    last = days[-1]["ใหม่"]
    out["พังก"] = {"ไส้เทียน": 30, "ห่าง": _r(30 - last), "เลื่อน": _r(_r(k_ss) * _r(30 - last)), "ใหม่": _r(last + _r(k_ss) * _r(30 - last)),
                  "วันQศูนย์": 100, "KQศูนย์": _r(1 / 101, 3),
                  "ครึ่งชีวิตQศูนย์": _r(S.half_life(1 - 1 / 101), 0), "กระโดด": 5}

    # ════════════ ตอน ข · 1 h ด้วยมือ สามวัน ════════════
    Qh, Rh = D("0.01"), D(1)
    h, Ph = D("0.8"), D("0.24")
    hdays_in = [(D(2), D("2.4")), (D("0.5"), D("1.0")), (D(-3), D("-3.3"))]
    hrows = []
    for x, y in hdays_in:
        Pp = qd(Ph + Qh, 2)
        reading = qd(y / x, 2)
        Rr = qd(Rh / (x * x), 2)
        K = qd(Pp / (Pp + Rr), 2)
        gap = qd(reading - h, 2)
        move = qd(K * gap, 2)
        h_new = qd(h + move, 2)
        P_new = qd((1 - K) * Pp, 2)
        # วิธีที่สอง: แบบ kalman_hedge (K แบบเงิน = P·x ÷ (P·x² + R) · ใช้ (y − h·x))
        Kc = Pp * x / (Pp * x * x + Rh)
        h_code = h + Kc * (y - h * x)
        hrows.append({"B": float(x), "A": float(y), "Pทาย": float(Pp), "อ่าน": float(reading), "Bกำลังสอง": float(x * x),
                      "Rหาร": float(Rr), "PบวกRหาร": float(qd(Pp + Rr, 2)), "K": float(K), "เดิม": float(h), "ห่าง": float(gap),
                      "เลื่อน": float(move), "ใหม่": float(h_new), "Pใหม่": float(P_new),
                      "หนึ่งลบK": float(qd(1 - K, 2)), "Kเงิน": float(qd(Kc, 3)), "พลาดเงิน": float(qd(y - h * x, 2)), "ใหม่แบบเงิน": float(qd(h_code, 2))})
        assert abs(h_code - h_new) <= D("0.011"), (h_code, h_new)
        h, Ph = h_new, P_new
    kfh = S.kalman_hedge([2.0, 0.5, -3.0], [2.4, 1.0, -3.3], q=0.01, r=1.0, beta0=0.8, p0=0.24)
    out["hมือ"] = {"ตัวอย่างh": 0.8, "ตัวอย่างB": 2, "ตัวอย่างทาย": 1.6, "Q": 0.01, "R": 1, "sdQ": 0.1, "sdR": 1, "เริ่ม": 0.8, "Pเริ่ม": 0.24, "sdเริ่ม": _r(math.sqrt(0.24)), "วัน": hrows,
                  "py": [_r(v) for v in kfh["beta"]]}
    # กราฟ sab2-kalman-reads: ค่าที่อ่านได้ ± SD ของมัน (รากของ R ÷ B² = 1 ÷ |B| เมื่อ R = 1) กับ h ที่ตัวกรองได้แต่ละวัน
    out["กราฟอ่าน"] = {"sdอ่าน": [_r(1 / abs(r["B"])) for r in hrows], "แกน": [0, 1, 2, 3, 4]}

    # ════════════ ตอน ข · 2 🎲 โลกที่ h ไหล และโลกที่ h คงที่ ════════════
    def track(w, burn=60):
        a, b = S.diff(w["logA"]), S.diff(w["logB"])
        hp = w["true"].get("h_path") or [w["true"]["h"]] * len(w["logA"])
        true = hp[1:]
        o = S.ols(b[:burn], a[:burn])
        r = o["sigma"] ** 2
        res, paths = {}, {}
        for sdq in Q_SDS:
            hs = S.kalman_hedge(b, a, q=sdq * sdq, r=r, beta0=o["slope"], p0=1.0)["beta_prior"]
            res[_kn(sdq)] = S.mean([abs(x - t) for x, t in zip(hs[START:], true[START:])])
            paths[_kn(sdq)] = hs
        for win in WINDOWS:
            ro = S.rolling_ols(b, a, win)
            hs = [None] + [z["slope"] if z else None for z in ro[:-1]]
            res[f"r{win}"] = S.mean([abs(x - t) for x, t in zip(hs[START:], true[START:])])
            paths[f"r{win}"] = hs
        fixed = S.ols(b[:START], a[:START])["slope"]
        res["คงที่"] = S.mean([abs(fixed - t) for t in true[START:]])
        return res, paths, true

    sim = {"n": 731, "h0": 1.0, "h1": 1.5, "phi": 0.9, "เริ่มวัด": START + 1, "seed": [1, 30]}
    for name, world, kw in (("ไหล", M.drifting_h_pair, dict(n=731, h0=1.0, h1=1.5, phi=0.9)),
                            ("คงที่", M.stationary_pair, dict(n=731, h=1.0, phi=0.9))):
        allres = [track(world(seed=s, **kw))[0] for s in M.ROBUST_SEEDS]
        tab = {}
        for key in allres[0]:
            vals = sorted(x[key] for x in allres)
            tab[key] = {"มัธยฐาน": _r((vals[14] + vals[15]) / 2), "ต่ำสุด": _r(vals[0]), "สูงสุด": _r(vals[-1])}
        sim[name] = tab
        # Kalman ชนะ rolling 60 กี่โลก (q sd 0.01)
        sim[name]["k001ชนะr60"] = sum(x["k001"] < x["r60"] for x in allres)
        sim[name]["k001ชนะคงที่"] = sum(x["k001"] < x["คงที่"] for x in allres)
    # ตัวอย่างหนึ่งโลก (seed 1) ไว้วาดกราฟ: ทุก 10 วัน
    res1, paths1, true1 = track(M.drifting_h_pair(seed=1, n=731, h0=1.0, h1=1.5, phi=0.9))
    idx = list(range(START, len(true1), 10))
    sim["กราฟ"] = {"วัน": [i + 1 for i in idx], "จริง": [_r(true1[i], 3) for i in idx],
                  "k001": [_r(paths1["k001"][i], 3) for i in idx], "k01": [_r(paths1["k01"][i], 3) for i in idx],
                  "r60": [_r(paths1["r60"][i], 3) for i in idx]}
    sim["ตัวอย่าง"] = {k: _r(v) for k, v in res1.items()}
    sim["r_sim"] = _r(S.ols(S.diff(M.drifting_h_pair(seed=1, n=731)["logB"])[:60],
                           S.diff(M.drifting_h_pair(seed=1, n=731)["logA"])[:60])["sigma"] * 100, 1)
    out["จำลอง"] = sim

    # ════════════ ตอน ค 📡 BTC บน ETH ════════════
    df, pf = load_closes("formation")
    dv, pv = load_closes("validation")
    dates = df + dv
    la, lb = S.logs(pf["BTC"] + pv["BTC"]), S.logs(pf["ETH"] + pv["ETH"])
    a, b = S.diff(la), S.diff(lb)
    dd = dates[1:]
    nf = len(df) - 1                        # จำนวนการขยับในช่วงเลือก (730)
    o = S.ols(b[:nf], a[:nf])
    r = o["sigma"] ** 2
    ov = S.ols(b[nf:], a[nf:])
    meth = {"คงที่": [o["slope"]] * len(a)}
    for win in WINDOWS:
        ro = S.rolling_ols(b, a, win)
        meth[f"r{win}"] = [None] + [z["slope"] if z else None for z in ro[:-1]]
    kres = {}
    for sdq in Q_SDS:
        kres[sdq] = S.kalman_hedge(b, a, q=sdq * sdq, r=r, beta0=1.0, p0=1.0)
        meth[_kn(sdq)] = kres[sdq]["beta_prior"]

    def sd_pnl(hs, lo, hi):
        return S.sd([a[i] - hs[i] * b[i] for i in range(lo, hi)]) * NOTIONAL

    def turn(hs, lo, hi):
        return S.mean([abs(hs[i] - hs[i - 1]) for i in range(lo + 1, hi)])

    tab = {}
    for key, hs in meth.items():
        tf, tv = turn(hs, START, nf), turn(hs, nf, len(a))
        tab[key] = {"sdเลือก": _r(sd_pnl(hs, START, nf), 0), "sdตรวจ": _r(sd_pnl(hs, nf, len(a)), 0),
                    "เปลี่ยนต่อวันเลือก": _r(tf, 3), "เปลี่ยนต่อวันตรวจ": _r(tv, 3),
                    "ซื้อขายต่อวันเลือก": _r(tf * NOTIONAL, 0), "ซื้อขายต่อวันตรวจ": _r(tv * NOTIONAL, 0),
                    "ค่าธรรมเนียมต่อปีเลือก": _r(tf * NOTIONAL * FEE * 365, 0),
                    "ค่าธรรมเนียมต่อปีตรวจ": _r(tv * NOTIONAL * FEE * 365, 0),
                    "ต่ำสุดตรวจ": _r(min(hs[nf:]), 2), "สูงสุดตรวจ": _r(max(hs[nf:]), 2),
                    "ต่ำสุดเลือก": _r(min(hs[START:nf]), 2), "สูงสุดเลือก": _r(max(hs[START:nf]), 2)}
    best_f = min(tab, key=lambda k: tab[k]["sdเลือก"] if k != "คงที่" else 1e9)
    best_v = min(tab, key=lambda k: tab[k]["sdตรวจ"])
    real = {"วันเลือก": len(df), "วันตรวจ": len(dv), "ขยับเลือก": nf, "ขยับตรวจ": len(a) - nf,
            "เริ่มวัด": dd[START], "จบเลือก": df[-1], "เริ่มตรวจ": dv[0], "จบตรวจ": dv[-1],
            "hเลือก": _r(o["slope"]), "R2เลือก": _r(o["r2"]), "sdRเปอร์เซ็นต์": _r(o["sigma"] * 100), "R": _r(r * 10000, 1),
            "hตรวจ": _r(ov["slope"]), "ตาราง": tab, "ดีสุดเลือก": best_f, "ดีสุดตรวจ": best_v,
            "ค่าธรรมเนียม": FEE * 100, "ขา": NOTIONAL, "แบบที่ลอง": len(Q_SDS) + len(WINDOWS),
            "Kalmanที่ลอง": len(Q_SDS)}
    # K ในหน่วยเดียวกับตอน ข (สัดส่วนที่เลื่อนเข้าหาค่าที่อ่านได้) ของวันที่ ETH ขยับ 1%: P ÷ (P + R ÷ x²)
    for s in Q_SDS:
        Pm = S.mean(kres[s]["P"][START:nf]) + s * s
        x = 0.01
        real.setdefault("Kวัน1", {})[_kn(s)] = _r(Pm / (Pm + r / (x * x)), 3)
    real["ท้ายช่วงเลือก"] = {k: _r(meth[k][nf]) for k in ("r60", "r120", "k001", "k01")}
    # วันธรรมดา: ETH ขยับขนาด SD ของช่วงเลือก → ความคลาดของค่าที่อ่านได้ R ÷ x² · K นิ่ง · หน้าต่างที่อายุเฉลี่ยเท่ากัน
    xs_ = S.sd(b[:nf])
    rt = r / (xs_ * xs_)
    real["ETHsdเปอร์เซ็นต์"] = _r(xs_ * 100)
    real["Rหารวันธรรมดา"] = _r(rt)
    real["sdอ่านวันธรรมดา"] = _r(math.sqrt(rt))
    for s_ in Q_SDS:
        Qx = s_ * s_
        ppx = (Qx + math.sqrt(Qx * Qx + 4 * Qx * rt)) / 2
        kx = ppx / (ppx + rt) if ppx > 0 else 0.0
        real.setdefault("Kนิ่งวันธรรมดา", {})[_kn(s_)] = _r(kx, 3)
        real.setdefault("หน้าต่างเทียบ", {})[_kn(s_)] = _r(2 / kx - 1, 0) if kx > 0 else None
    # ตารางตัวอย่างหนึ่งแถวทุก 73 วัน (ช่วงเลือก) + วันแรก/วันสุดท้ายของช่วงตรวจ
    rows = []
    for i in list(range(START, nf, 73))[:8] + [nf, len(a) - 1]:
        rows.append({"วัน": dd[i], "BTC": _r(a[i] * 100), "ETH": _r(b[i] * 100), "อ่าน": _r(_r(a[i] * 100) / _r(b[i] * 100)),
                     "r60": _r(meth["r60"][i]),
                     "k001": _r(meth["k001"][i]), "k01": _r(meth["k01"][i])})
    real["แถว"] = rows
    # วันที่ Kalman เร็วกระโดดมากที่สุดในช่วงเลือก
    hs = meth["k01"]
    j = max(range(START, nf - 1), key=lambda i: abs(b[i]))          # วันที่ ETH ขยับแรงที่สุดในช่วงที่วัด
    real["กระโดด"] = {"วัน": dd[j], "BTC": _r(a[j] * 100), "ETH": _r(b[j] * 100), "อ่าน": _r(a[j] / b[j]),
                      "k01ก่อน": _r(hs[j]), "k01หลัง": _r(hs[j + 1]), "k001ก่อน": _r(meth["k001"][j]),
                      "k001หลัง": _r(meth["k001"][j + 1]), "r60ก่อน": _r(meth["r60"][j]), "r60หลัง": _r(meth["r60"][j + 1]),
                      "k01อีก10วัน": _r(hs[j + 11]), "k001อีก10วัน": _r(meth["k001"][j + 11]),
                      "sdอ่านวันนั้น": _r(math.sqrt(r) / abs(b[j]))}
    for s_ in Q_SDS:
        Pp = kres[s_]["P"][j - 1] + s_ * s_
        real["กระโดด"]["K" + _kn(s_)] = _r(Pp / (Pp + r / (b[j] * b[j])), 2)
    # กราฟ: ทุก 5 วัน ตั้งแต่ START ถึงจบช่วงตรวจ
    gi = list(range(START, len(a), 5))
    real["กราฟ"] = {"i": [i - START for i in gi], "วัน": [dd[i] for i in gi], "เส้นแบ่ง": nf - START,
                    "r60": [_r(meth["r60"][i], 3) for i in gi], "k001": [_r(meth["k001"][i], 3) for i in gi],
                    "k01": [_r(meth["k01"][i], 3) for i in gi], "ปีป้าย": [[i - START, dd[i][:7]] for i in range(START, len(a)) if dd[i][5:10] in ("01-01", "07-01")]}
    # เทียบกับ "ไม่ปรับเลย" ในช่วงตรวจ: ลดลงกี่เปอร์เซ็นต์
    real["ซื้อขายต่อวันk01"] = tab["k01"]["ซื้อขายต่อวันตรวจ"]
    real["ค่าธรรมเนียมต่อวันk01"] = _r(tab["k01"]["ซื้อขายต่อวันตรวจ"] * FEE)
    real["ลดตรวจk001"] = _r((1 - tab["k001"]["sdตรวจ"] / tab["คงที่"]["sdตรวจ"]) * 100, 0)
    real["ลดตรวจr60"] = _r((1 - tab["r60"]["sdตรวจ"] / tab["คงที่"]["sdตรวจ"]) * 100, 0)
    real["เพิ่มเลือกk01"] = _r((tab["k01"]["sdเลือก"] / tab["k0"]["sdเลือก"] - 1) * 100, 0)
    # 💻 บรรทัดที่พิมพ์: SD ช่วงเลือกของ k0.01 กับ r60
    out["จริง"] = real

    # ════════════ fails ตอน ค: คู่ไม่มีเชือกก็ได้ h ที่ "ตามทัน" ════════════
    nr = []
    for s in M.ROBUST_SEEDS:
        w = M.random_walk_pair(seed=s, n=731)
        aa, bb = S.diff(w["logA"]), S.diff(w["logB"])
        o2 = S.ols(bb[:60], aa[:60])
        hs2 = S.kalman_hedge(bb, aa, q=1e-4, r=o2["sigma"] ** 2, beta0=o2["slope"], p0=1.0)["beta_prior"]
        mae = S.mean([abs(x - 1.0) for x in hs2[START:]])
        x = [la_ - hh * lb_ for la_, lb_, hh in zip(w["logA"][1:], w["logB"][1:], hs2)]
        hf = S.ols(bb[:START], aa[:START])["slope"]
        xf = [la_ - hf * lb_ for la_, lb_ in zip(w["logA"][1:], w["logB"][1:])]
        nr.append((mae, S.adf(x[START:])["reject5"], S.adf(xf[START:])["reject5"]))
    mids = sorted(v[0] for v in nr)[14:16]
    out["ไม่มีเชือก"] = {"ห่างhมัธยฐาน": _r(sum(mids) / 2),
                         "ผ่านADF": sum(v[1] for v in nr),
                         "ผ่านADFคงที่": sum(v[2] for v in nr), "โลก": len(nr),
                         "ผ่านเปอร์เซ็นต์": _r(100 * sum(v[1] for v in nr) / len(nr), 0)}

    # ════════════ แบบฝึก ════════════
    ex = {}
    # ข้อ 1: วันที่ 6 ต่อจากห้าวัน (เห็น 14) · ปัดทุกขั้น
    d5 = days[-1]
    Pp6 = qd(D(str(d5["Pใหม่"])) + Q, 2)
    K6 = qd(Pp6 / (Pp6 + R), 2)
    gap6 = qd(D(14) - D(str(d5["ใหม่"])), 2)
    m6 = qd(D(str(d5["ใหม่"])) + qd(K6 * gap6, 2), 2)
    ex["ข้อ1"] = {"เห็น": 14, "Pทาย": float(Pp6), "K": float(K6), "ห่าง": float(gap6), "ใหม่": float(m6),
                 "เลื่อน": float(qd(K6 * gap6, 2)), "PบวกR": float(qd(Pp6 + R, 2)),
                 "ลืมQตัวหาร": float(qd(D(str(d5["Pใหม่"])) + R, 2)), "ลืมQ": float(qd(D(str(d5["Pใหม่"])) / (D(str(d5["Pใหม่"])) + R), 2))}
    # ข้อ 2: เปลี่ยน R เป็น 1 (เครื่องอ่านแม่นขึ้น) ที่วันที่ 1 ของห้าวัน
    Pp = qd(D("0.8") + Q, 2)
    K2 = qd(Pp / (Pp + 1), 2)
    ex["ข้อ2"] = {"R": 1, "Pทาย": float(Pp), "K": float(K2), "ใหม่": float(qd(D("10.6") + K2 * (D(12) - D("10.6")), 2)),
                 "Kเดิม": days[0]["K"], "ใหม่เดิม": days[0]["ใหม่"], "ลืมQ": float(qd(D("0.8") / D("1.8"), 2)),
                 "เลื่อน": float(qd(K2 * D("1.4"), 2)), "PบวกR": float(qd(Pp + 1, 2))}
    # ข้อ 3: เริ่มไม่มั่นใจ P 4 (Q 1 R 4) → K วันแรก
    m, P = D("10.6"), D(4)
    ks = []
    for x in reads[:3]:
        Pp = qd(P + Q, 2)
        K = qd(Pp / (Pp + R), 2)
        m = qd(m + qd(K * qd(D(x) - m, 2), 2), 2)
        P = qd((1 - K) * Pp, 2)
        ks.append(float(K))
    ex["ข้อ3"] = {"Pเริ่ม": 4, "K": ks, "Pทายวัน1": 5, "PบวกRวัน1": 9}
    # ข้อ 5 (ข้อมูลจริง): วันกระโดด กับ K ของ q sd 0.01 — คำนวณจาก Kวัน1 ไม่ใช้ ใช้ตัวเลขในตาราง
    ex["ข้อ5"] = {"ค่าธรรมเนียมk01": tab["k01"]["ค่าธรรมเนียมต่อปีตรวจ"], "ค่าธรรมเนียมk001": tab["k001"]["ค่าธรรมเนียมต่อปีตรวจ"],
                 "ต่างsd": _r(tab["k01"]["sdตรวจ"] - tab["k001"]["sdตรวจ"], 0)}
    out["แบบฝึก"] = ex
    out["_แบบฝึก"] = [
        {"โจทย์": "(ทำตาม) วันที่ 6 เห็น 14 · ทาย P · K · ค่ากลางใหม่", "คำตอบ": ex["ข้อ1"]["ใหม่"]},
        {"โจทย์": "(เปลี่ยนเลข) R = 1 แทน 4 ที่วันที่ 1 → K และค่ากลางใหม่", "คำตอบ": ex["ข้อ2"]["K"]},
        {"โจทย์": "(เปลี่ยนเงื่อนไข) เริ่มไม่มั่นใจ P 4 → K สามวันแรก", "คำตอบ": ks[0]},
        {"โจทย์": "(ตัดสินใจ) เลือก Q จากช่วงเลือกแล้วได้ Q = 0 — ใช้ต่อไหม", "คำตอบ": tab["k0"]["sdตรวจ"]},
        {"โจทย์": "(ถ่ายโอน · ข้อมูลจริง) Kalman เร็ว vs กลาง ช่วงตรวจ ค่าธรรมเนียมกับ SD", "คำตอบ": ex["ข้อ5"]["ต่างsd"]},
    ]
    out["_claims"] = [{"id": "sab2-ch06-kalman",
                       "ข้อความ": "ตัวกรอง Kalman หนึ่งมิติในบทนี้ (ทาย P + Q · K = P ÷ (P + R) · ใหม่ = เดิม + K × (เห็น − เดิม) · P ใหม่ = (1 − K) × P) "
                                  "คือรูปมาตรฐานของ Kalman (1960) ที่สถานะเดินสุ่ม · คำนวณด้วย tools/sab2_stats.kalman_hedge (ทดสอบแล้วว่า Q = 0 "
                                  "ให้ผลเท่ากำลังสองน้อยสุดแบบเวียน)",
                       "ระดับหลักฐาน": "ตีพิมพ์", "แหล่ง": "Kalman, R. E. (1960) A New Approach to Linear Filtering and Prediction Problems, "
                                                        "J. Basic Engineering 82(1)", "บท": [6]}]
    return out
