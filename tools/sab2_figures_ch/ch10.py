"""เล่ม 2 บท 10 — PCA: ให้ข้อมูลบอกแรงร่วมเอง · ตัวเลขทุกตัวของ docs/sab2-part10.html

ตอน ก  สองเหรียญ หมุนแกนด้วยมือ: หกวันสอน (วัน 4–6 = วัน 1–3 กลับเครื่องหมาย · Mean = 0)
       ทิศ (a, b) ที่ a² + b² = 1 จากสามเหลี่ยม 3-4-5 และ 7-24-25 (ตัวเลขลงตัว) → ค่าบนแกน a·A + b·B ต่อวัน →
       ผลรวมกำลังสองต่อทิศ (หกทิศ) → ยอด (0.8, 0.6) = 300 · ทิศตั้งฉาก (−0.6, 0.8) = 100 · รวม 400 = ΣA² + ΣB²
       ตรวจวิธีที่สอง: a²ΣA² + 2abΣAB + b²ΣB² · ตั้งชื่อ PCA / PC / Loading / Eigenvalue / Explained Variance
ตอน ข  สามเหรียญ: loading เป็นน้ำหนักพอร์ต · หกวันสอนที่แต่ละวันมีแรงเดียว (ค่าบนแกน 10 · 5 · 2.5) ·
       ชุด loading ลงตัวสองตำแหน่ง (0.48, 0.64, 0.6) (−0.36, −0.48, 0.8) (0.8, −0.6, 0) · Covariance Matrix ·
       พอร์ตกลับเป็นจำนวนเหรียญ (ราคา 40 · 10 · 200 · 1,000 ดอลลาร์ต่อหนึ่งหน่วย loading) · Gross/Net Exposure
ตอน ค  📡 10 เหรียญ ผลตอบแทน log รายวัน (%) ช่วงเลือก: PCA จากความแปรปรวนร่วม (ไม่ปรับมาตรฐาน) → PC1–PC3 ·
       PC1 เทียบตะกร้าเท่ากันกับ BTC · R² ของแต่ละเหรียญ · ช่วงตรวจ (เปิด 2 ครั้ง: PCA ทั้งช่วง · หน้าต่าง 90 วัน)
       🎲 โลกแรงเดียว (factor_basket) กับโลกสองแรง (factor_basket + กลุ่มสามเหรียญจาก factor_basket ชุดที่สอง) ·
       คำตอบจริง = eigenvector ของเมทริกซ์ความแปรปรวนร่วมจริงที่คิดจากพารามิเตอร์ · seed 1–30
ตอน ง  พังเมื่อไร: ความตรงทิศข้ามช่วง · ปรับมาตรฐาน · ADF บนผลสะสมของ 10 พอร์ต · 🧰 (practitioner-research.md §1 §4 §6)
ช่วงทดสอบสุดท้ายไม่ถูกแตะ (load_closes("formation") และ ("validation") เท่านั้น)
"""

import itertools
import math
import statistics

import sab_book as SB

UNIT = 1000                  # ดอลลาร์ต่อหนึ่งหน่วย loading (พอร์ตสอน)
PRICES3 = (40, 10, 200)      # ราคาสมมติของเหรียญ A · B · D (ตอน ข · ไม่ใช้ "C" เพราะ W12)
WIN, STEP = 90, 30           # หน้าต่างเลื่อนของ PCA จริง (วัน) · เลื่อนทีละ 30 วัน
SEEDS = list(range(1, 31))
N_COINS = 10
F_SD, IDIO_SD, G_SD = 0.03, 0.022, 0.015   # แรงตลาด · ส่วนเฉพาะ (log ต่อวัน) · แรงกลุ่มของโลกสองแรง
GROUP = [1, 1, 1, 0, 0, 0, 0, 0, 0, 0]


def _r(v, n=2):
    v = round(float(v) + 0.0, n)
    return int(v) if v == int(v) else v


def _dot(a, b):
    return math.fsum(x * y for x, y in zip(a, b))


def _align(a, b):
    """ความตรงทิศ |Σ a_i b_i| ÷ (ความยาว a × ความยาว b) · 1 = ทิศเดียวกัน (หรือกลับด้าน) · 0 = ตั้งฉาก"""
    return abs(_dot(a, b)) / math.sqrt(_dot(a, a) * _dot(b, b))


def _rets(series_list):
    """ผลตอบแทน log รายวันเป็นเปอร์เซ็นต์ จาก list ของ log ราคา"""
    return [[100 * (b - a) for a, b in zip(s, s[1:])] for s in series_list]


def extend(data, D, q):
    import sab2_sim as M
    import sab2_stats as S
    from sab2_realdata import load_closes

    out = {}

    # ════════════ ค่าที่ทวนจากเล่ม 1 และบทก่อน ════════════
    f1 = SB.load_figures("sab")
    sc = f1["ch08"]["ฉาก"]
    out["เล่ม1"] = {"gross": sc["gross"], "net": sc["net"], "ขา": sc["gross"] // 2}
    h1 = data["ch01"]["หกวัน"]
    out["บท1"] = {"ผลรวมdBคูณdA": h1["ผลรวมdBคูณdA"], "ตัวหาร": h1["ตัวหาร"], "cov": h1["cov"],
                  "ผลรวมdBกำลังสอง": h1["ผลรวมdBกำลังสอง"], "varB": h1["varB"]}
    c9 = data["ch09"]["จริง"]
    out["บท9"] = {"corrresBTC": c9["corrresBTC"], "corrresEW": c9["corrresEW"], "corrresEWขนาด": abs(c9["corrresEW"])}
    r8 = data["ch08"]["rho"]["r098"]
    out["บท8"] = {"rho": r8["rho"], "sdวัน": r8["sdวัน"], "sigma": data["ch08"]["sigma"]}

    # ════════════ ตอน ก สองเหรียญ ════════════
    half = [(8, 6), (1, 7), (-7, 1)]
    days2 = half + [(-a, -b) for a, b in half]
    A = [a for a, _ in days2]
    Bc = [b for _, b in days2]
    n2 = len(days2)
    sAA = sum(a * a for a in A)
    sBB = sum(b * b for b in Bc)
    sAB = sum(a * b for a, b in days2)
    dirs = [("1", "0"), ("0.96", "0.28"), ("0.8", "0.6"), ("0.6", "0.8"), ("0.28", "0.96"), ("0", "1")]
    rows = []
    for ws in dirs:
        a, b = D(ws[0]), D(ws[1])
        assert a * a + b * b == 1
        sc3 = [a * x + b * y for x, y in half]
        ss3 = sum(s * s for s in sc3)
        f_aa, f_ab, f_bb = a * a * sAA, 2 * a * b * sAB, b * b * sBB
        sq = [D(str(q(s * s, 2))) for s in sc3]                     # ปัดสองตำแหน่งก่อนรวม (ผู้อ่านรวมจากเลขบนหน้า)
        rows.append({"a": float(a), "b": float(b), "มุม": _r(math.degrees(math.atan2(float(b), float(a))), 0),
                     "ค่า": [float(s) for s in sc3], "กำลังสอง": [float(x) for x in sq],
                     "สามวัน": float(sum(sq)), "ss": float(2 * sum(sq)),
                     "สูตรAA": _r(f_aa), "สูตรAB": _r(f_ab), "สูตรBB": _r(f_bb), "สูตร": _r(f_aa + f_ab + f_bb)})
        assert 2 * ss3 == f_aa + f_ab + f_bb
    best = max(rows, key=lambda r: r["ss"])
    p2 = [D("-0.6"), D("0.8")]
    sc_p2 = [p2[0] * x + p2[1] * y for x, y in half]
    ss_p2 = 2 * sum(s * s for s in sc_p2)
    pc = S.pca([A, Bc])
    assert abs(pc["vectors"][0][0] - 0.8) < 1e-9 and abs(pc["vectors"][1][1] - 0.8) < 1e-9
    curve = []
    for deg in range(0, 181, 3):
        t = math.radians(deg)
        a, b = math.cos(t), math.sin(t)
        curve.append([deg, _r(a * a * sAA + 2 * a * b * sAB + b * b * sBB, 2)])
    tot = sAA + sBB
    out["สองเหรียญ"] = {
        "A": A, "B": Bc, "ครึ่ง": [list(t) for t in half], "n": n2, "ตัวหาร": n2 - 1,
        "AAสามวัน": sum(a * a for a, _ in half), "BBสามวัน": sum(b * b for _, b in half), "ABสามวัน": sum(a * b for a, b in half),
        "AA": sAA, "BB": sBB, "AB": sAB, "รวม": tot,
        "varA": _r(sAA / (n2 - 1)), "varB": _r(sBB / (n2 - 1)), "cov": _r(sAB / (n2 - 1)), "varรวม": _r(tot / (n2 - 1)),
        "ทิศ": rows, "ดีสุด": best,
        "pc2": {"a": -0.6, "b": 0.8, "ค่า": [float(s) for s in sc_p2], "กำลังสอง": [float(s * s) for s in sc_p2],
                "ss": float(ss_p2)},
        "pc2มุม": _r(math.degrees(math.atan2(0.8, -0.6)), 0),
        "ทิศ7_24กำลังสอง": [float(D("0.96") ** 2), float(D("0.28") ** 2)],
        "pc1var": _r(best["ss"] / (n2 - 1)), "pc2var": _r(float(ss_p2) / (n2 - 1)),
        "pc1เปอร์เซ็นต์": _r(100 * best["ss"] / tot, 1), "pc2เปอร์เซ็นต์": _r(100 * float(ss_p2) / tot, 1),
        "เครื่องมือ": {"pc1": [_r(v) for v in pc["vectors"][0]], "pc2": [_r(v) for v in pc["vectors"][1]],
                       "explained": [_r(v) for v in pc["explained"]], "values": [_r(v) for v in pc["values"]]},
        "เส้นโค้ง": curve,
        # ความชันสามเส้น (B บนแกนตั้ง): ถดถอย B บน A · ถดถอย A บน B (กลับด้าน) · PC1
        "ชันBบนA": _r(sAB / sAA), "ชันAบนB": _r(sAB / sBB), "ชันAบนBกลับ": _r(sBB / sAB), "ชันpc1": _r(0.6 / 0.8),
        # 🔎 ทิศพิเศษ: (ตาราง ΣAA ΣAB / ΣAB ΣBB) × (0.8, 0.6) = 300 × (0.8, 0.6)
        "คูณทิศ": [_r(D("0.8") * sAA + D("0.6") * sAB), _r(D("0.8") * sAB + D("0.6") * sBB)],
        "คูณทิศพจน์": [_r(D("0.8") * sAA), _r(D("0.6") * sAB), _r(D("0.8") * sAB), _r(D("0.6") * sBB)],
        "ตรงทิศ": {"pc1กับ0.6": float(D("0.8") * D("0.6") + D("0.6") * D("0.8")), "pc1กับpc2": 0},
        # เงิน: หนึ่งหน่วย loading = 1,000 ดอลลาร์
        "เงิน": {"pc1A": 800, "pc1B": 600, "pc2A": -600, "pc2B": 800,
                 "วัน2pc2A": _r(-600 * 1 / 100), "วัน2pc2B": _r(800 * 7 / 100), "วัน2pc2": _r((-600 * 1 + 800 * 7) / 100),
                 "วัน2ค่า": float(sc_p2[1]), "วัน1pc2": float(sc_p2[0])},
    }

    # ════════════ ตอน ข สามเหรียญ ════════════
    v1 = [D("0.48"), D("0.64"), D("0.6")]
    u2 = [D("-0.36"), D("-0.48"), D("0.8")]
    v3 = [D("0.8"), D("-0.6"), D("0")]
    V = [v1, u2, v3]
    for i in range(3):
        for j in range(3):
            assert sum(x * y for x, y in zip(V[i], V[j])) == (1 if i == j else 0)
    s_mag = [D(10), D(5), D("2.5")]
    half3 = [[s_mag[k] * x for x in V[k]] for k in range(3)]          # วัน 1–3 วันละแรงเดียว
    days3 = half3 + [[-x for x in d] for d in half3]
    cols = [[float(d[i]) for d in days3] for i in range(3)]
    p3 = S.pca(cols)
    for k in range(3):
        assert all(abs(p3["vectors"][k][i] - float(V[k][i])) < 1e-9 for i in range(3)), (k, p3["vectors"][k])
    names = ["A", "B", "D"]
    ss_c = {nm: float(sum(d[i] * d[i] for d in days3)) for i, nm in enumerate(names)}
    cross = {"AB": float(sum(d[0] * d[1] for d in days3)), "AD": float(sum(d[0] * d[2] for d in days3)),
             "BD": float(sum(d[1] * d[2] for d in days3))}
    den3 = len(days3) - 1
    covm = {k: _r(v / den3) for k, v in list(ss_c.items()) + list(cross.items())}
    scores = [[float(sum(V[k][i] * d[i] for i in range(3))) for d in half3] for k in range(3)]
    ss_pc = [float(2 * s_mag[k] * s_mag[k]) for k in range(3)]
    tot3 = sum(ss_c.values())
    assert abs(tot3 - sum(ss_pc)) < 1e-9
    # วันที่ 1 ทีละขา (PC1 · PC2 · PC3)
    d1 = half3[0]
    terms_d1 = [[float(V[k][i] * d1[i]) for i in range(3)] for k in range(3)]
    d3 = half3[2]
    terms_d3 = [[float(V[k][i] * d3[i]) for i in range(3)] for k in range(3)]
    hold = []
    for k in range(3):
        dollars = [float(V[k][i] * UNIT) for i in range(3)]
        coins = [_r(dl / PRICES3[i], 2) for i, dl in enumerate(dollars)]
        hold.append({"ดอลลาร์": [_r(x) for x in dollars], "เหรียญ": coins,
                     "gross": _r(sum(abs(x) for x in dollars)), "net": _r(sum(dollars))})
    d2 = half3[1]
    pnl2 = [_r(hold[1]["ดอลลาร์"][i] * float(d2[i]) / 100) for i in range(3)]
    # กำไรรายวันของสามพอร์ต (ดอลลาร์) ทีละขา · วัน 1–3 · ทุกช่องลงตัวสองตำแหน่ง
    pnl = []
    for k in range(3):
        rowk = []
        for d in half3:
            legs = [V[k][i] * UNIT * d[i] / 100 for i in range(3)]
            rowk.append({"ขา": [_r(x) for x in legs], "รวม": _r(sum(legs))})
        pnl.append(rowk)
    mkt5 = [{"ขา": [_r(x * 5 / 100) for x in h["ดอลลาร์"]], "รวม": _r(sum(h["ดอลลาร์"]) * 5 / 100)} for h in hold]
    out["สามเหรียญ"] = {
        "วัน": [[float(x) for x in d] for d in half3], "ค่าแรง": [float(s) for s in s_mag],
        "loading": [[float(x) for x in v] for v in V],
        "loadingกำลังสอง": [[float(x * x) for x in v] for v in V],
        "ss": ss_c, "ข้าม": cross, "รวม": _r(tot3), "ตัวหาร": den3, "cov": covm, "varรวม": _r(tot3 / den3),
        "ค่าบนแกน": scores, "ssPC": ss_pc, "varPC": [_r(x / den3) for x in ss_pc],
        "เปอร์เซ็นต์": [_r(100 * x / tot3, 1) for x in ss_pc],
        "วัน1": terms_d1, "วัน3": terms_d3,
        "ราคา": list(PRICES3), "หน่วย": UNIT, "ถือ": hold, "กำไร": pnl,
        "ssกำไรpc1": _r(2 * sum(r["รวม"] ** 2 for r in pnl[0])),
        "วัน2ต่อเหรียญ": [_r(PRICES3[i] * d2[i] / 100) for i in range(3)],
        "ABพจน์": [_r(d[0] * d[1]) for d in half3], "ABสามวัน": _r(sum(d[0] * d[1] for d in half3)),
        "DDพจน์": [_r(d[2] * d[2]) for d in half3], "DDสามวัน": _r(sum(d[2] * d[2] for d in half3)),
        "ค่ากำลังสองวัน": [_r(x * x) for x in s_mag], "วัน2pnl": pnl2, "วัน2รวม": _r(sum(pnl2)),
        "วัน2ค่า": float(scores[1][1]), "ตลาด5": mkt5,
        "ตรวจcov": _r(covm["A"] + covm["B"] + covm["D"]),
    }

    # ════════════ ตอน ค 📡 ข้อมูลจริง ════════════
    fd, pf = load_closes("formation")
    vd, pv = load_closes("validation")
    coins = list(pf.keys())
    Rf = _rets([[math.log(x) for x in pf[c]] for c in coins])
    Rv = _rets([[math.log(x) for x in pv[c]] for c in coins])
    pF = S.pca(Rf)
    pV = S.pca(Rv)
    pFs = S.pca(Rf, standardize=True)
    ew = [math.fsum(r[t] for r in Rf) / N_COINS for t in range(len(Rf[0]))]
    r2btc = [S.corr(r, Rf[0]) ** 2 for r in Rf]
    r2pc1 = [S.corr(r, pF["scores"][0]) ** 2 for r in Rf]
    r2ew = [S.corr(r, ew) ** 2 for r in Rf]

    def pcdict(p, k):
        return {c: _r(p["vectors"][k][i]) for i, c in enumerate(coins)}

    sd_f = [S.sd(r) for r in Rf]

    # ส่วนที่เหลือของเก้าเหรียญหลังหักแรงร่วม (BTC แบบบท 9 · ค่าบน PC1) → correlation เฉลี่ยทุกคู่ · ADF บนส่วนที่เหลือสะสม
    def resid(y, x):
        o = S.ols(x, y)
        return [yy - o["intercept"] - o["slope"] * xx for xx, yy in zip(x, y)]

    res_stats = {}
    for nm, fac in (("BTC", Rf[0]), ("PC1", pF["scores"][0])):
        res = {i: resid(Rf[i], fac) for i in range(1, N_COINS)}
        cs = [S.corr(res[a], res[b]) for a, b in itertools.combinations(range(1, N_COINS), 2)]
        npass = sum(1 for i in res if S.adf(list(itertools.accumulate(res[i])))["reject5"])
        res_stats[nm] = {"corr": _r(statistics.mean(cs)), "adfผ่าน": npass}
    load_tab = [{"เหรียญ": c, "pc1": _r(pF["vectors"][0][i]), "pc2": _r(pF["vectors"][1][i]), "pc3": _r(pF["vectors"][2][i]),
                 "sd": _r(sd_f[i]), "r2btc": _r(r2btc[i]), "r2pc1": _r(r2pc1[i])} for i, c in enumerate(coins)]
    al = [_align(pF["vectors"][k], pV["vectors"][k]) for k in range(N_COINS)]
    best_v = [max(range(N_COINS), key=lambda j: _align(pF["vectors"][k], pV["vectors"][j])) for k in range(3)]

    def top2(vec):
        idx = sorted(range(N_COINS), key=lambda i: -abs(vec[i]))[:2]
        return [{"เหรียญ": coins[i], "loading": _r(vec[i])} for i in idx]

    # หน้าต่างเลื่อน 90 วัน (ช่วงเลือก + ช่วงตรวจ) เทียบกับ PC ของช่วงเลือกทั้งช่วง
    Rall = [a + b for a, b in zip(Rf, Rv)]
    dall = fd[1:] + vd[1:]
    roll = []
    for s0 in range(0, len(Rall[0]) - WIN + 1, STEP):
        pw = S.pca([r[s0:s0 + WIN] for r in Rall])
        roll.append({"จบ": dall[s0 + WIN - 1], "pc1เปอร์เซ็นต์": _r(100 * pw["explained"][0], 1),
                     "pc2เปอร์เซ็นต์": _r(100 * pw["explained"][1], 1),
                     "ตรงpc1": _r(_align(pw["vectors"][0], pF["vectors"][0])),
                     "ตรงpc2": _r(_align(pw["vectors"][1], pF["vectors"][1])),
                     "pc2สองตัว": [t["เหรียญ"] for t in top2(pw["vectors"][1])]})
    nval = sum(1 for r in roll if r["จบ"] > fd[-1])
    # ADF บนผลสะสมของ 10 พอร์ต (ช่วงเลือก · loading จากข้อมูลชุดเดียวกัน)
    adfs = []
    for k in range(N_COINS):
        a = S.adf(list(itertools.accumulate(pF["scores"][k])))
        adfs.append({"pc": k + 1, "stat": _r(a["stat"]), "p": _r(a["pvalue"]), "ผ่าน": bool(a["reject5"])})
    cnt_pass = sum(1 for a in adfs if a["ผ่าน"])
    pc4 = pF["vectors"][3]
    out["จริง"] = {
        "เหรียญ": coins, "วันเลือก": len(fd), "วันตรวจ": len(vd), "แถวเลือก": len(Rf[0]), "แถวตรวจ": len(Rv[0]),
        "เริ่มเลือก": fd[0], "จบเลือก": fd[-1], "เริ่มตรวจ": vd[0], "จบตรวจ": vd[-1],
        "เปอร์เซ็นต์": [_r(100 * x, 1) for x in pF["explained"]],
        "เปอร์เซ็นต์สาม": _r(100 * sum(pF["explained"][:3]), 1),
        "ค่าลักษณะ": [_r(x) for x in pF["values"]], "varรวม": _r(sum(pF["values"])),
        "ตาราง": load_tab, "pc1": pcdict(pF, 0), "pc2": pcdict(pF, 1), "pc3": pcdict(pF, 2),
        "pc1ต่ำสุด": _r(min(pF["vectors"][0])), "pc1สูงสุด": _r(max(pF["vectors"][0])),
        "pc1กำลังสองรวม": _r(sum(v * v for v in pF["vectors"][0])),
        "pc2สองตัว": top2(pF["vectors"][1]), "pc3สองตัว": top2(pF["vectors"][2]),
        "corrEW": _r(S.corr(pF["scores"][0], ew), 3), "corrEWปัด": _r(S.corr(pF["scores"][0], ew), 2), "corrBTC": _r(S.corr(pF["scores"][0], Rf[0])),
        "r2btcเฉลี่ย9": _r(statistics.mean(r2btc[1:])), "r2pc1เฉลี่ย9": _r(statistics.mean(r2pc1[1:])),
        "r2ewเฉลี่ย9": _r(statistics.mean(r2ew[1:])),
        "r2ห่าง": _r(statistics.mean(r2pc1[1:]) - statistics.mean(r2btc[1:])),
        "ส่วนที่เหลือ": res_stats,
        "r2btcต่ำสุด": {"เหรียญ": coins[1 + min(range(9), key=lambda i: r2btc[1 + i])], "ค่า": _r(min(r2btc[1:]))},
        "sdต่ำสุด": {"เหรียญ": coins[min(range(N_COINS), key=lambda i: sd_f[i])], "ค่า": _r(min(sd_f))},
        "sdสูงสุด": {"เหรียญ": coins[max(range(N_COINS), key=lambda i: sd_f[i])], "ค่า": _r(max(sd_f))},
        "มาตรฐาน": {"pc1": {c: _r(pFs["vectors"][0][i]) for i, c in enumerate(coins)},
                    "pc1ต่ำสุด": _r(min(pFs["vectors"][0])), "pc1สูงสุด": _r(max(pFs["vectors"][0])),
                    "เปอร์เซ็นต์": [_r(100 * x, 1) for x in pFs["explained"][:3]],
                    "pc2สองตัว": top2(pFs["vectors"][1]),
                    "ตรงpc2กับไม่ปรับ": _r(_align(pFs["vectors"][1], pF["vectors"][1]))},
        "ตรวจ": {"เปอร์เซ็นต์": [_r(100 * x, 1) for x in pV["explained"]],
                 "pc1": pcdict(pV, 0), "pc2": pcdict(pV, 1), "pc2สองตัว": top2(pV["vectors"][1]),
                 "corrEW": _r(S.corr(pV["scores"][0],
                                     [math.fsum(r[t] for r in Rv) / N_COINS for t in range(len(Rv[0]))]), 3)},
        "ตรงทิศ": [_r(x) for x in al], "ตรงที่ดีสุดของpc2": _r(_align(pF["vectors"][1], pV["vectors"][best_v[1]])),
        "pc2ไปตรงกับpcที่": best_v[1] + 1,
        "หน้าต่าง": roll, "หน้าต่างวัน": WIN, "หน้าต่างเลื่อน": STEP, "หน้าต่างจำนวน": len(roll), "หน้าต่างในตรวจ": nval,
        "ตรงpc2ต่ำสุด": min(r["ตรงpc2"] for r in roll), "ตรงpc2สูงสุด": max(r["ตรงpc2"] for r in roll),
        "ตรงpc1ต่ำสุด": min(r["ตรงpc1"] for r in roll),
        "pc1เปอร์เซ็นต์ต่ำสุด": min(r["pc1เปอร์เซ็นต์"] for r in roll), "pc1เปอร์เซ็นต์สูงสุด": max(r["pc1เปอร์เซ็นต์"] for r in roll),
        "หน้าต่างครึ่งต่ำ": sum(1 for r in roll if r["ตรงpc2"] < 0.5),
        "adf": adfs, "adfผ่าน": cnt_pass, "adfโชค": _r(0.05 * N_COINS),
        "pc4สองตัว": top2(pc4), "pc4LTC": _r(pc4[coins.index("LTC")]),
        "pc2adf": adfs[1]["stat"], "pc10สองตัว": top2(pF["vectors"][9]), "pc10เปอร์เซ็นต์": _r(100 * pF["explained"][9], 1),
        "ดูช่วงตรวจ": 2,
    }

    # ════════════ ตอน ค 🎲 โลกที่รู้คำตอบ ════════════
    betas = [round(0.6 + 0.8 * i / (N_COINS - 1), 3) for i in range(N_COINS)]

    def world1(seed, n):
        w = M.factor_basket(seed=seed, n=n, n_coins=N_COINS, idio_sd=IDIO_SD, factor_sd=F_SD)
        return w["logP"], w["true"]["phis"]

    def world2(seed, n):
        a, phis = world1(seed, n)
        g = M.factor_basket(seed=1000 + seed, n=n, n_coins=N_COINS, betas=GROUP, phis=[0.5] * N_COINS, idio_sd=1e-12,
                            factor_sd=G_SD, levels=[0.0] * N_COINS)
        return [[x + y for x, y in zip(p, qq)] for p, qq in zip(a, g["logP"])], phis

    def true_cov(phis, group):
        """ความแปรปรวนร่วมจริงของผลตอบแทน (%²): แรงตลาด + แรงกลุ่ม + ส่วนเฉพาะ (Δ ของ AR(1): 2σ² ÷ (1 + φ))"""
        f2, g2, i2 = (100 * F_SD) ** 2, (100 * G_SD) ** 2, (100 * IDIO_SD) ** 2
        k = N_COINS
        return [[f2 * betas[i] * betas[j] + (g2 * GROUP[i] * GROUP[j] if group else 0.0) +
                 (2 * i2 / (1 + phis[i]) if i == j else 0.0) for j in range(k)] for i in range(k)]

    _, phis0 = world1(1, 10)
    tv1, tvec1 = S.jacobi_eigen(true_cov(phis0, False))
    tv2, tvec2 = S.jacobi_eigen(true_cov(phis0, True))
    true_share1 = [x / sum(tv1) for x in tv1]
    true_share2 = [x / sum(tv2) for x in tv2]

    sims = {"W1": {"pc1": [], "pc2": [], "ตรงpc1": [], "ข้ามpc2": [], "pc2สั้น": []},
            "W2": {"pc1": [], "pc2": [], "ตรงpc2": [], "ข้ามpc2": [], "ตรงpc2สั้น": [], "pc2สั้น": []}}
    nF, nV = len(fd), len(vd)
    for s in SEEDS:
        for name, wf, tvec in (("W1", world1, tvec1), ("W2", world2, tvec2)):
            lp, _ = wf(s, nF + nV)
            R = _rets(lp)
            Ra, Rb = [r[:nF - 1] for r in R], [r[nF - 1:] for r in R]
            pa, pb = S.pca(Ra), S.pca(Rb)
            ps = S.pca([r[:WIN] for r in R])
            d_ = sims[name]
            d_["pc1"].append(100 * pa["explained"][0])
            d_["pc2"].append(100 * pa["explained"][1])
            d_["ข้ามpc2"].append(_align(pa["vectors"][1], pb["vectors"][1]))
            d_["pc2สั้น"].append(100 * ps["explained"][1])
            if name == "W1":
                d_["ตรงpc1"].append(_align(pa["vectors"][0], tvec[0]))
            else:
                d_["ตรงpc2"].append(_align(pa["vectors"][1], tvec[1]))
                d_["ตรงpc2สั้น"].append(_align(ps["vectors"][1], tvec[1]))

    def summ(v, n=2):
        return {"มัธยฐาน": _r(statistics.median(v), n), "ต่ำสุด": _r(min(v), n), "สูงสุด": _r(max(v), n)}

    out["จำลอง"] = {
        "โลก": len(SEEDS), "วัน": nF + nV, "วันเลือก": nF, "วันตรวจ": nV, "เหรียญ": N_COINS,
        "betaต่ำสุด": betas[0], "betaสูงสุด": betas[-1], "แรงตลาดsd": _r(100 * F_SD, 1), "เฉพาะsd": _r(100 * IDIO_SD, 1),
        "กลุ่มsd": _r(100 * G_SD, 1), "กลุ่มเหรียญ": sum(GROUP),
        "จริงW1pc1เปอร์เซ็นต์": _r(100 * true_share1[0], 1), "จริงW1pc2เปอร์เซ็นต์": _r(100 * true_share1[1], 1),
        "จริงW2pc2เปอร์เซ็นต์": _r(100 * true_share2[1], 1),
        "W1": {"pc1เปอร์เซ็นต์": summ(sims["W1"]["pc1"], 1), "pc2เปอร์เซ็นต์": summ(sims["W1"]["pc2"], 1),
               "ตรงpc1": summ(sims["W1"]["ตรงpc1"]), "ข้ามpc2": summ(sims["W1"]["ข้ามpc2"]),
               "pc2สั้นเปอร์เซ็นต์": summ(sims["W1"]["pc2สั้น"], 1)},
        "W2": {"pc1เปอร์เซ็นต์": summ(sims["W2"]["pc1"], 1), "pc2เปอร์เซ็นต์": summ(sims["W2"]["pc2"], 1),
               "ตรงpc2": summ(sims["W2"]["ตรงpc2"]), "ข้ามpc2": summ(sims["W2"]["ข้ามpc2"]),
               "ตรงpc2สั้น": summ(sims["W2"]["ตรงpc2สั้น"]), "pc2สั้นเปอร์เซ็นต์": summ(sims["W2"]["pc2สั้น"], 1)},
    }

    # ════════════ 🧰 คนทำงานจริง (ที่มา: practitioner-research.md §1.1 §4 §6 · ตัวเลขตามบันทึก ไม่ได้คำนวณ) ════════════
    out["คนทำงานจริง"] = {
        "ปีAL": "2010", "ปีALร่าง": "2009", "ALหน้าต่าง": 60, "ALวัน": 30,
        "ปีSarmento": "2020", "ปีSarmentoวิทยานิพนธ์": "2019", "SarmentoEGเปอร์เซ็นต์": 1, "Sarmentoข้ามต่อปี": 12,
        "SarmentoETF": 208, "Sarmentoนาที": 5, "Hurst": 0.5, "ปีArbLab": "2024",
    }

    # ════════════ แบบฝึก ════════════
    exr = {}
    # ข้อ 1: ค่าบน PC2 ของหกวัน (เลขเดิม)
    exr["ข้อ1"] = {"ค่า": out["สองเหรียญ"]["pc2"]["ค่า"], "ss": out["สองเหรียญ"]["pc2"]["ss"],
                   "var": out["สองเหรียญ"]["pc2var"], "เปอร์เซ็นต์": out["สองเหรียญ"]["pc2เปอร์เซ็นต์"]}
    # ข้อ 2: A แกว่งเป็นสองเท่า
    aa2, ab2, bb2 = 4 * sAA, 2 * sAB, sBB
    tri = []
    for ws in (("1", "0"), ("0.96", "0.28"), ("0.8", "0.6")):
        a, b = D(ws[0]), D(ws[1])
        t3 = [D(str(q(x, 2))) for x in (a * a * aa2, 2 * a * b * ab2, b * b * bb2)]
        tri.append({"a": float(a), "b": float(b), "AA": _r(t3[0]), "AB": _r(t3[1]), "BB": _r(t3[2]), "ss": _r(sum(t3))})
    pe = S.pca([[2 * x for x in A], Bc])
    exr["ข้อ2"] = {"AA": aa2, "AB": ab2, "BB": bb2, "ทิศ": tri, "ดีสุด": max(tri, key=lambda t: t["ss"])["ss"],
                   "จริงa": _r(pe["vectors"][0][0]), "จริงb": _r(pe["vectors"][0][1]),
                   "จริงss": _r(pe["values"][0] * (n2 - 1)), "รวม": aa2 + bb2,
                   "จริงเปอร์เซ็นต์": _r(100 * pe["explained"][0], 1)}
    # ข้อ 3: ตลาดขึ้น 5% ทุกเหรียญ
    exr["ข้อ3"] = {"pc3": mkt5[2], "pc2": mkt5[1], "pc1": mkt5[0]}
    # ข้อ 5: หุ้นสามตัว (ถ่ายโอน) · loading ชุดเดิมเรียงใหม่ · 500 ดอลลาร์ต่อหน่วย · ราคา 25 · 20 · 50
    pr5, unit5 = (25, 20, 50), 500
    l5 = [[0.6, 0.48, 0.64], [-0.8, 0.36, 0.48], [0.0, 0.8, -0.6]]
    h5 = [[_r(l * unit5) for l in v] for v in l5]
    exr["ข้อ5"] = {"ราคา": list(pr5), "หน่วย": unit5, "loading": l5, "ดอลลาร์": h5,
                   "หุ้น": [[_r(dl / pr5[i]) for i, dl in enumerate(h)] for h in h5],
                   "net": [_r(sum(h)) for h in h5], "gross": [_r(sum(abs(x) for x in h)) for h in h5]}
    out["แบบฝึก"] = exr
    out["_แบบฝึก"] = [
        {"โจทย์": "(ทำตาม) ค่าบนแกน PC2 (−0.6, 0.8) ของหกวัน → ผลรวมกำลังสอง · ความแปรปรวน · สัดส่วน", "คำตอบ": exr["ข้อ1"]["ss"]},
        {"โจทย์": "(เปลี่ยนเลข) A แกว่งเป็นสองเท่า → ทิศไหนแกว่งมากสุดในสามทิศ", "คำตอบ": exr["ข้อ2"]["ดีสุด"]},
        {"โจทย์": "(เปลี่ยนเงื่อนไข) ทุกเหรียญขึ้น 5% → พอร์ต PC3 และ PC2 ได้เท่าไร", "คำตอบ": mkt5[2]["รวม"]},
        {"โจทย์": "(ตัดสินใจ · ข้อมูลจริง) ต้นจะเทรดพอร์ต PC2 ของช่วงเลือก", "คำตอบ": out["จริง"]["ตรงทิศ"][1]},
        {"โจทย์": "(ถ่ายโอน) หุ้นสามตัว loading ชุดเดิมเรียงใหม่ → จำนวนหุ้นของพอร์ต PC3", "คำตอบ": exr["ข้อ5"]["หุ้น"][2][1]},
    ]
    out["_claims"] = [
        {"id": "sab2-ch10-pca-rotation",
         "ข้อความ": "PC1 คือทิศหนึ่งหน่วย (ผลรวมกำลังสองของน้ำหนัก = 1) ที่ทำให้ความแปรปรวนของ a·A + b·B มากที่สุด · การหมุนแกน "
                    "ไม่เปลี่ยนผลรวมความแปรปรวน (300 + 100 = 228 + 172) · ตัวอย่างสองเหรียญได้ทิศ (0.8, 0.6)",
         "ระดับหลักฐาน": "ตีพิมพ์", "แหล่ง": "นิยาม PCA (ค่าลักษณะเฉพาะของเมทริกซ์ความแปรปรวนร่วม) · tools/sab2_stats.py pca/jacobi_eigen",
         "บท": [10]},
        {"id": "sab2-ch10-pca-instability",
         "ข้อความ": "บนข้อมูลของเล่ม PC1 ช่วงเลือกกับช่วงตรวจชี้ทิศเดียวกัน (0.99) แต่ PC2 ตรงกันเพียง 0.08 ขณะที่โลกจำลองที่มีแรงที่สองจริงได้ 0.97",
         "ระดับหลักฐาน": "ข้อมูลของเล่ม", "แหล่ง": "tools/sab2_figures_ch/ch10.py", "บท": [10]},
    ]
    return out
