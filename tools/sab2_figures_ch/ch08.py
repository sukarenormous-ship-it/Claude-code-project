"""เล่ม 2 บท 8 — สายพานคัดคู่ของคนทำงานจริง · ตัวเลขทุกตัวของ docs/sab2-part8.html

ตอน ก  correlation 0.98 ที่ไม่มีระยะให้ทำเงิน
       ด้วยมือ: แรงร่วมหักกันใน X (สี่วันสอน) · หนึ่งหน่วย σ = 1 → ส่วนของตัวเอง 1 − ρ ต่อเหรียญ → X ได้ 2(1 − ρ)
       → SD วันของ X = σ√(2(1 − ρ)) · ρ 0.80 / 0.95 / 0.98 / 0.995 ที่ σ 3.5% · Half-life → φ → √(1 − φ²) → SD แกว่ง
       (เล่ม 1 บท 13: SD² = แรงสะบัด² ÷ (1 − φ²)) → กำไรต่อไม้ ≈ 1.5 SD (เข้า 2 ออก 0.5) เทียบต้นทุนไปกลับ
       ทุกขั้นปัดสองตำแหน่งแล้วใช้ต่อ (ผู้อ่านคิดตามจากเลขบนหน้า)
       🎲 stationary_pair ที่ตั้ง SD แรงสะบัดและ φ ให้ตรงสองกรณี (ρ 0.98 HL 5 · ρ 0.995 HL 2) · sab2_engine ค่าธรรมเนียม
       0 / 0.05% / 0.15% ต่อ fill · seed 1–30 · มัธยฐาน
       📡 ช่วงเลือก: correlation ของผลตอบแทนรายวันกับ SD ของ X เทียบต้นทุนไปกลับ 0.20% (ของ 45 คู่)
ตอน ข  คู่ที่ผ่านแต่ไม่ใช่คู่ · ขาร่วม · สายพาน
       📡 ADF เหรียญเดี่ยว 10 ตัว · Engle–Granger สองทิศ (เลือกทิศที่ค่าสถิติแรงกว่า = ทดสอบ 90 ครั้ง) → 8 คู่ ทุกคู่มี LTC
       ขาร่วม: สามคู่ของ LTC ด้วยมือ (h จริงของช่วงเลือก · การขยับสมมติ) · 📡 correlation ของเงินรายวันช่วงตรวจ
       Distance Method (SSD = n × Mean² + Σ(ห่าง − Mean)²) ด้วยมือสามคู่ · Zero Crossing · Hurst (แนวคิด)
       🎲 โลกปัจจัยที่รู้คำตอบ 10 เหรียญ: แรงตลาดร่วม + 3 คู่มีเชือก (stationary_pair φ 0.9) + 1 คู่แน่นแต่ไม่มีเชือก
       (random_walk_pair แรงสะบัดเล็ก) + 1 เหรียญเดินสุ่ม + 1 เหรียญนิ่งในตัวเอง (กับดักแบบ LTC) · โลกศูนย์ (ไม่มีเชือกเลย)
       · ยาวเท่าช่วงเลือก + ช่วงตรวจ (731 + 365) · seed 1–30
ตอน ค  📡 45 คู่: ตัวชี้วัดช่วงเลือกเทียบกำไรช่วงตรวจ (การ์ดเล่ม 1 ไม้บรรทัดตรึง · ไม้บรรทัดเลื่อน 60 วัน) · Rank Correlation
       ด้วยมือห้าคู่ · ความคงอยู่ (ไม้บรรทัดเดิมทั้งอัน: Zero Crossing รอบ Mean เดิม) · สายพานบนข้อมูลจริง
ที่มา: tools/sab_research/pairs_check.py (ย้ายมาที่นี่ · ช่วงเลือกและช่วงตรวจเท่านั้น) · practitioner-research.md §2 §3 §4 §8
ช่วงทดสอบสุดท้ายไม่ถูกแตะ (load_closes("formation") และ ("validation") เท่านั้น)
"""

import itertools
import math

import sab_book as SB

SIGMA = 3.5          # SD ต่อวันของแต่ละเหรียญในตัวอย่าง (%)
RHOS = ("0.80", "0.95", "0.98", "0.99")
HLS = (2, 5)
LEG = 500            # ขา A 500 ดอลลาร์ (ทุนคู่ 1,000 แบ่งสองขา)
RETAIL_FILL = "0.15"  # ค่าธรรมเนียม 0.1% + ราคาคลาด 0.05% ต่อ fill (สมมติ · ไม่ใช่ราคาของ exchange ใด)
NF, NV = 731, 365


def _r(v, n=2):
    v = round(float(v) + 0.0, n)
    return int(v) if v == int(v) else v


def _key(rho):
    return "r" + rho.replace(".", "")


def _crossings(x, m=None):
    m = sum(x) / len(x) if m is None else m
    s = [1 if v > m else -1 for v in x]
    return sum(1 for a, b in zip(s, s[1:]) if a != b)


def _ranks(v):
    o = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    for k, i in enumerate(o):
        r[i] = k + 1
    return r


def extend(data, D, q):
    import sab2_engine as E
    import sab2_sim as M
    import sab2_stats as S
    from sab2_realdata import load_closes

    from decimal import ROUND_HALF_UP

    def qd(x, n=2):
        d = x if isinstance(x, D) else D(str(x))
        return d.quantize(D(1).scaleb(-n), rounding=ROUND_HALF_UP)

    def spearman(a, b):
        return S.corr(_ranks(a), _ranks(b))

    def med(v):
        v = sorted(v)
        k = len(v)
        return v[k // 2] if k % 2 else (v[k // 2 - 1] + v[k // 2]) / 2

    out = {}

    # ════════════ เล่ม 1 ที่ทวน ════════════
    f1 = SB.load_figures("sab")
    c11 = f1["ch11"]["v2"]["ต้นทุน"]
    s13 = f1["ch13"]["v2"]["sdหน้า"][1]
    hl13 = {str(r["phi"]): r["ครึ่งชีวิต"] for r in f1["ch13"]["phiเป็นครึ่งชีวิต"]}
    x10 = f1["ch10"]["v2"]["ข้ามมือ20วัน"]
    out["เล่ม1"] = {"ต่อfillเปอร์เซ็นต์": c11["อัตราtakerเปอร์เซ็นต์"], "จำนวนfill": c11["จำนวนfill"],
                    "ไปกลับเปอร์เซ็นต์": _r(c11["อัตราtakerเปอร์เซ็นต์"] * c11["จำนวนfill"]),
                    "บท13": {"phi": s13["phi"], "แรงสะบัด": s13["แรงสะบัด"], "sdกำลังสอง": s13["sdกำลังสอง"], "sd": s13["sd"]},
                    "hlของ09": hl13["0.9"], "ข้าม": x10["ครั้ง"], "ข้ามวัน": x10["วัน"],
                    "เข้า": 2, "ออก": 0.5, "ถือ": 30}
    fee_book = D(str(c11["อัตราtakerเปอร์เซ็นต์"]))          # 0.05
    rt_book = fee_book * 4                                     # 0.20
    rt_retail = D(RETAIL_FILL) * 4                             # 0.60

    # ════════════ ตอน ก · 1 แรงร่วมหักกัน (สี่วันสอน) ════════════
    common = [3, -4, 2, -1]
    ownA = [D("0.2"), D("-0.1"), D("0.1"), D("-0.2")]
    ownB = [D("-0.1"), D("0.2"), D("0.1"), D("0.1")]
    days = []
    for c, a, b in zip(common, ownA, ownB):
        days.append({"ร่วม": c, "ตัวเองA": float(a), "ตัวเองB": float(b), "A": float(c + a), "B": float(c + b), "X": float(a - b)})
    out["สี่วัน"] = {"วัน": days, "Aใหญ่สุด": max(abs(d["A"]) for d in days), "Xใหญ่สุด": max(abs(d["X"]) for d in days)}

    # หนึ่งหน่วย σ = 1 แล้วขยาย × 3.5
    rho_rows = []
    for rs in RHOS:
        rho = D(rs)
        one = 1 - rho
        two = 2 * one
        root = qd(D(math.sqrt(float(two))), 2)
        day = qd(root * D(str(SIGMA)), 2)
        rho_rows.append({"rho": float(rho), "ส่วนตัวเอง": float(one), "สองเท่า": float(two), "ราก": float(root),
                         "sdวัน": float(day), "ตรง": _r(SIGMA * math.sqrt(float(two)), 2)})
    out["rho"] = {_key(rs): r_ for rs, r_ in zip(RHOS, rho_rows)}
    out["rhoแถว"] = rho_rows
    out["sigma"] = SIGMA
    out["หนึ่งหน่วย"] = {"rho": 0.98, "ส่วนตัวเอง": 0.02, "ส่วนร่วม": 0.98, "X": 0.04, "sd": 0.2, "sdคูณ": 0.7,
                         "sigmaกำลังสอง": _r(SIGMA * SIGMA), "ร่วมกำลังสอง": _r(0.98 * SIGMA * SIGMA, 3)}

    # Half-life → φ → √(1 − φ²)
    hl_rows = {}
    for hl in HLS:
        phi = qd(D(0.5 ** (1 / hl)), 2)
        p2 = qd(phi * phi, 2)
        one = 1 - p2
        root = qd(D(math.sqrt(float(one))), 2)
        hl_rows[str(hl)] = {"hl": hl, "phi": float(phi), "phiกำลังสอง": float(p2), "หนึ่งลบ": float(one), "ราก": float(root),
                            "phiจริง": _r(0.5 ** (1 / hl), 4)}
    out["hl"] = hl_rows

    # กำไรต่อไม้ เทียบต้นทุน (เข้า 2 ออก 0.5 → 1.5 SD)
    prof = {}
    grid = []
    for rs, rr in zip(RHOS, rho_rows):
        for hl in HLS:
            root = D(str(hl_rows[str(hl)]["ราก"]))
            swing = qd(D(str(rr["sdวัน"])) / root, 2)
            per = qd(D("1.5") * swing, 2)
            usd = qd(per * LEG / 100, 2)
            book = qd(rt_book * LEG / 100, 2)
            retail = qd(rt_retail * LEG / 100, 2)
            row = {"rho": rr["rho"], "hl": hl, "sdวัน": rr["sdวัน"], "ราก": float(root), "sdแกว่ง": float(swing),
                   "กำไรเปอร์เซ็นต์": float(per), "กำไรดอลลาร์": float(usd), "ต้นทุนเล่ม": float(book),
                   "ต้นทุนแอป": float(retail), "เท่าเล่ม": float(qd(usd / book, 1)), "เท่าแอป": float(qd(usd / retail, 1)),
                   "เหลือแอป": float(usd - retail), "เหลือเล่ม": float(usd - book),
                   "ต้นทุนกินแอปเปอร์เซ็นต์": float(qd(retail / usd * 100, 0))}
            prof[_key(rs) + "h" + str(hl)] = row
            grid.append(row)
    out["กำไร"] = prof
    out["กำไรแถว"] = grid
    out["ต้นทุน"] = {"เล่มต่อfill": float(fee_book), "เล่มไปกลับ": float(rt_book), "เล่มดอลลาร์": float(qd(rt_book * LEG / 100)),
                     "แอปต่อfill": float(D(RETAIL_FILL)), "แอปค่าธรรมเนียม": 0.1, "แอปคลาด": 0.05,
                     "แอปไปกลับ": float(rt_retail), "แอปดอลลาร์": float(qd(rt_retail * LEG / 100)), "ขา": LEG,
                     "เล่มต่อfillดอลลาร์": float(qd(fee_book * LEG / 100))}

    # 🎲 ตรวจด้วยโลกจำลองที่ตั้ง ρ กับ Half-life ไว้
    sim_c = {}
    for rs, hl in (("0.98", 5), ("0.99", 2), ("0.995", 2)):
        rho = float(rs)
        sd_day = SIGMA / 100 * math.sqrt(2 * (1 - rho))
        phi = 0.5 ** (1 / hl)
        acc = {"gross": [], "book": [], "retail": [], "trades": [], "corr": [], "netแอป": [], "netเล่ม": []}
        for s in M.ROBUST_SEEDS:
            w = M.stationary_pair(seed=s, n=NF, phi=phi, h=1.0, sd=sd_day, common_sd=SIGMA / 100 * math.sqrt(rho))
            A, B = w["A"], w["B"]
            z = [x / w["true"]["sd_stationary"] for x in w["X"]]
            res = {}
            for nm, fee in (("gross", 0.0), ("book", float(fee_book) / 100), ("retail", float(D(RETAIL_FILL)) / 100)):
                res[nm] = E.run(A, B, A[0] / B[0], z, sets=LEG / A[0], fee=fee, hold=30)
            n_tr = res["gross"]["trades"]
            for nm in ("gross", "book", "retail"):
                acc[nm].append(res[nm]["net"] / n_tr if n_tr else 0.0)
            acc["trades"].append(n_tr)
            acc["netแอป"].append(res["retail"]["net"])
            acc["netเล่ม"].append(res["book"]["net"])
            acc["corr"].append(S.corr(S.diff(w["logA"]), S.diff(w["logB"])))
        sim_c[_key(rs) + "h" + str(hl)] = {"rho": rho, "hl": hl, "ต่อไม้gross": _r(med(acc["gross"])),
                                            "ต่อไม้เล่ม": _r(med(acc["book"])), "ต่อไม้แอป": _r(med(acc["retail"])),
                                            "ไม้": _r(med(acc["trades"]), 1), "ปีแอป": _r(med(acc["netแอป"]), 1),
                                            "ปีเล่ม": _r(med(acc["netเล่ม"]), 1), "corr": _r(med(acc["corr"]), 2),
                                            "แอปขาดทุนโลก": sum(1 for v in acc["netแอป"] if v < 0), "โลก": len(M.ROBUST_SEEDS),
                                            "กินแอปเปอร์เซ็นต์": _r((1 - med(acc["retail"]) / med(acc["gross"])) * 100, 0)}
    out["จำลองต้นทุน"] = sim_c
    # 🔎 ลงลึก: แรงสะบัดกับการขยับรายวัน · correlation 0.995 ด้วยมือ
    deep = {}
    for hl in HLS:
        ph = D(str(hl_rows[str(hl)]["phi"]))
        k = qd(2 / (1 + ph), 2)
        deep["ตัวคูณ" + str(hl)] = float(k)
        deep["คลาด" + str(hl)] = _r((1 - 1 / math.sqrt(float(k))) * 100, 0)
    d995 = qd(D(str(SIGMA)) * D("0.1"), 2)
    sw995 = qd(d995 / D(str(hl_rows["2"]["ราก"])), 2)
    p995 = qd(D("1.5") * sw995, 2)
    u995 = qd(p995 * LEG / 100, 2)
    deep.update({"sdวัน995": float(d995), "sdแกว่ง995": float(sw995), "กำไร995": float(p995), "ดอลลาร์995": float(u995),
                 "กิน995": float(qd(qd(rt_retail * LEG / 100) / u995 * 100, 0))})
    out["ลึก"] = deep

    # ════════════ ข้อมูลจริง: 45 คู่ (ย้ายจาก pairs_check.py) ════════════
    fd, F = load_closes("formation")
    vd, V = load_closes("validation")
    coins = list(F.keys())
    RT = 4 * E.FEE
    LF = {c: S.logs(F[c]) for c in coins}
    LV = {c: S.logs(V[c]) for c in coins}

    single = {}
    for c in coins:
        a = S.adf(LF[c])
        single[c] = {"stat": _r(a["stat"]), "p": _r(a["pvalue"], 3), "pเปอร์เซ็นต์": _r(a["pvalue"] * 100, 1),
                     "ผ่าน": a["reject5"], "เส้น5": _r(a["crit"]["5%"])}
    av = S.adf(LV["LTC"])
    out["เส้นคู่"] = _r(S.engle_granger(LF["BTC"], LF["ETH"])["crit"]["5%"])
    out["เดี่ยว"] = {"เหรียญ": single, "ผ่าน": [c for c in coins if single[c]["ผ่าน"]],
                     "LTCตรวจ": _r(av["stat"]), "LTCตรวจเส้น5": _r(av["crit"]["5%"]),
                     "รองลงมา": min((c for c in coins if not single[c]["ผ่าน"]), key=lambda c: single[c]["p"])}

    P_all = {c: F[c] + V[c] for c in coins}
    rows = []
    one_dir_pass = 0
    for a, b in itertools.combinations(coins, 2):
        la, lb = LF[a], LF[b]
        eg1, eg2 = S.engle_granger(la, lb), S.engle_granger(lb, la)
        one_dir_pass += eg1["reject5"]
        if eg2["stat"] < eg1["stat"]:
            A, B, eg = b, a, eg2
        else:
            A, B, eg = a, b, eg1
        lA, lB = LF[A], LF[B]
        h = eg["h"]
        X = [p - h * q for p, q in zip(lA, lB)]
        mX, sX = S.mean(X), S.sd(X)
        ar = S.ar1(X)
        hl = S.half_life(ar["phi"])
        lags = range(2, 61)
        hx, hy = [], []
        for L_ in lags:
            dd = [X[i + L_] - X[i] for i in range(len(X) - L_)]
            hx.append(math.log(L_))
            hy.append(math.log(S.sd(dd)))
        hurst = S.ols(hx, hy)["slope"]
        ra, rb = S.diff(lA), S.diff(lB)
        vA, vB = V[A], V[B]
        A0, B0 = F[A][-1], F[B][-1]
        sets = LEG / A0
        hu = h * A0 / B0
        Xv = [p - h * q for p, q in zip(LV[A], LV[B])]
        zv = [(x - mX) / sX for x in Xv]
        rz = E.run(vA, vB, hu, zv, sets=sets, enter=2.0, leave=0.5, hold=30)
        rz0 = E.run(vA, vB, hu, zv, sets=sets, enter=2.0, leave=0.5, hold=30, fee=0.0)
        Xall = [math.log(p) - h * math.log(q) for p, q in zip(P_all[A], P_all[B])]
        zr = []
        for t in range(NF, NF + len(vd)):
            w = Xall[t - 59:t + 1]
            zr.append((Xall[t] - S.mean(w)) / S.sd(w))
        rr_ = E.run(vA, vB, hu, zr, sets=sets, enter=2.0, leave=0.5, hold=30)
        nh = len(X)
        hA = S.ols(lB[: nh // 2], lA[: nh // 2])["slope"]
        hB = S.ols(lB[nh // 2:], lA[nh // 2:])["slope"]
        egv = S.engle_granger(LV[A], LV[B])
        rows.append({
            "pair": f"{A}/{B}", "A": A, "B": B, "rho_ret": S.corr(ra, rb), "rho_lvl": S.corr(lA, lB),
            "rho_ret_val": S.corr(S.diff(LV[A]), S.diff(LV[B])),
            "eg_stat": eg["stat"], "eg_p": eg["pvalue"], "eg_pass": eg["reject5"], "h": h,
            "h_drift": abs(hB - hA) / abs(h) if h else float("nan"),
            "hl": hl, "cross": _crossings(X) / (nh / 365.0), "sd": sX, "sd_rt": sX / RT, "dsd": S.sd(S.diff(X)),
            "hurst": hurst, "net": rz["net"], "gross": rz0["net"], "trades": rz["trades"], "costs": rz["costs"],
            "time_exits": sum(1 for t_ in rz["trade_list"] if t_["reason"] == "time"), "open": rz["open"],
            "roll": rr_["net"], "eq": S.diff(rz["equity"]),
            "val_cross": _crossings(Xv, mX), "val_mean_sd": (S.mean(Xv) - mX) / sX,
            "val_mean_shift": 100 * (S.mean(Xv) - mX), "val_eg_pass": egv["reject5"],
            "val_adf_c": S.adf(Xv)["reject5"], "corr_ltc": S.corr(X, LF["LTC"]),
        })
    by = {r["pair"]: r for r in rows}

    # ── ตอน ก จริง: correlation สูงสุดของเรา กับ SD ของ X เทียบต้นทุน ──
    top_rc = sorted(rows, key=lambda r: -r["rho_ret"])[:5]
    out["จริงก"] = {
        "แถว": [{"คู่": r["pair"], "rho": _r(r["rho_ret"]), "sdวัน": _r(100 * r["dsd"]), "sd": _r(100 * r["sd"], 1),
                 "เท่า": _r(r["sd_rt"], 0)} for r in top_rc],
        "rhoสูงสุด": _r(top_rc[0]["rho_ret"]), "คู่สูงสุด": top_rc[0]["pair"],
        "เท่าต่ำสุด": _r(min(r["sd_rt"] for r in rows), 0), "เท่าสูงสุด": _r(max(r["sd_rt"] for r in rows), 0),
        "rhoต่ำสุด": _r(min(r["rho_ret"] for r in rows)),
        "BTCSOLระดับ": _r(by["BTC/SOL"]["rho_lvl"]), "BTCSOLp": _r(by["BTC/SOL"]["eg_p"]),
        "BTCSOLpเปอร์เซ็นต์": _r(by["BTC/SOL"]["eg_p"] * 100, 0), "BTCSOLrho": _r(by["BTC/SOL"]["rho_ret"]),
        "ต้นทุนไปกลับ": _r(RT * 100),
        "หนึ่งจุดห้าSD": float(qd(D("1.5") * qd(D(top_rc[0]["sd"] * 100), 1), 1)),
        "ต่อไม้ดอลลาร์": float(qd(qd(D("1.5") * qd(D(top_rc[0]["sd"] * 100), 1), 1) * LEG / 100, 1)),
    }

    # ── ตอน ข: แปดคู่ที่ผ่าน (ทดสอบสองทิศ) ──
    passes = [r for r in rows if r["eg_pass"]]
    near0 = [r for r in passes if abs(r["h"]) < 0.1]
    out["แปดคู่"] = {
        "แถว": [{"คู่": r["pair"], "h": _r(r["h"]), "stat": _r(r["eg_stat"]), "corrLTC": _r(r["corr_ltc"])}
                for r in sorted(passes, key=lambda r: r["eg_stat"])],
        "จำนวน": len(passes), "มีLTC": sum(1 for r in passes if "LTC" in r["pair"]),
        "hใกล้ศูนย์": len(near0), "hต่ำสุด": _r(min(r["h"] for r in near0)), "hสูงสุด": _r(max(r["h"] for r in near0)),
        "corrต่ำสุดใกล้ศูนย์": _r(min(r["corr_ltc"] for r in near0)),
        "ทิศเดียวผ่าน": one_dir_pass, "ทดสอบทิศเดียว": 45, "ทดสอบสองทิศ": 90,
        "โชคทิศเดียว": 2.25, "โชคสองทิศ": 4.5,
        "LTCDOT": {"h": _r(by["LTC/DOT"]["h"]), "corrLTC": _r(by["LTC/DOT"]["corr_ltc"])},
    }
    # ด้วยมือ: h −0.04 ของ LTC บน LINK
    hL = qd(D(str(by["LTC/LINK"]["h"])), 2)
    out["hศูนย์"] = {"h": float(hL), "Bขยับ": 10, "Xจากb": float(-hL * 10), "LTCขยับ": 10,
                     "ขาBดอลลาร์": float(qd(abs(hL) * LEG, 0)), "ขาB": "long" if hL < 0 else "short",
                     "ขา": LEG, "hDOT": float(qd(D(str(by["LTC/DOT"]["h"])), 2)),
                     "XจากbDOT": float(-qd(D(str(by["LTC/DOT"]["h"])), 2) * 10)}

    # ขาร่วม ด้วยมือ: สามคู่ของ LTC (h จริง · การขยับสอน)
    trio = [("LTC/BTC", "BTC", 1), ("LTC/ETH", "ETH", D("1.5")), ("LTC/SOL", "SOL", 3)]
    ltc_move = 2
    tri = []
    for pr, partner, mv in trio:
        hh = qd(D(str(by[pr]["h"])), 2)
        pnl = qd(D(LEG) * (D(ltc_move) - hh * D(str(mv))) / 100, 2)
        tri.append({"คู่": pr, "h": float(hh), "LTC": ltc_move, "คู่ขยับ": float(mv), "เงิน": float(pnl),
                    "ส่วนคู่": float(qd(-hh * D(str(mv)), 2)), "สุทธิเปอร์เซ็นต์": float(qd(D(ltc_move) - hh * D(str(mv)), 2))})
    out["สามคู่"] = {"แถว": tri, "LTCอย่างเดียว": float(qd(D(LEG) * ltc_move / 100, 0)),
                     "ต่างสูงสุด": _r(max(t["เงิน"] for t in tri) - min(t["เงิน"] for t in tri))}

    def avg_corr(names):
        cs = []
        for x, y in itertools.combinations(names, 2):
            if S.sd(by[x]["eq"]) > 0 and S.sd(by[y]["eq"]) > 0:
                cs.append(S.corr(by[x]["eq"], by[y]["eq"]))
        return S.mean(cs)

    xrpn = [r["pair"] for r in rows if "XRP" in r["pair"] and "LTC" not in r["pair"]]
    import random
    rng = random.Random(7)
    nets = [r["net"] for r in rows]
    draws = sorted(S.mean(rng.sample(nets, 8)) for _ in range(20000))
    obs = S.mean([r["net"] for r in passes])
    out["ขาร่วม"] = {
        "corrLTC": _r(avg_corr([r["pair"] for r in passes])), "corrXRP": _r(avg_corr(xrpn)),
        "corrทั้งหมด": _r(avg_corr([r["pair"] for r in rows])), "XRPคู่": len(xrpn),
        "สุ่มมัธยฐาน": _r(draws[10000], 1), "สุ่ม95": _r(draws[19000], 1), "LTCเฉลี่ย": _r(obs, 1),
        "เปอร์เซ็นไทล์": _r(100 * sum(d < obs for d in draws) / 20000, 1), "สุ่มรอบ": 20000,
        "XRPตรวจ": _r(100 * (V["XRP"][-1] / V["XRP"][0] - 1), 0),
        "XRPเฉลี่ย": _r(S.mean([by[p]["net"] for p in xrpn]), 0),
        "แยกได้สูงสุด": len(coins) // 2, "เหรียญ": len(coins),
        "อย่างน้อยหนึ่ง": _r(100 * (1 - 0.95 ** 45), 0),
        "ขาย": {c: _r(100 * (V[c][-1] / V[c][0] - 1), 0) for c in coins},
    }

    # ── Distance Method ด้วยมือ ──
    gaps = {"P": [1, 1, 1, 1, 1], "Q": [4, -4, 4, -4, 0], "R": [6, 7, 8, 9, 10]}
    dist = {}
    for k, g in gaps.items():
        m = D(sum(g)) / len(g)
        ssd = sum(x * x for x in g)
        dev = sum((D(x) - m) ** 2 for x in g)
        dist[k] = {"ห่าง": g, "SSD": ssd, "Mean": float(m), "nMean2": float(len(g) * m * m), "ส่วนแกว่ง": float(dev),
                   "ข้าม": _crossings(g, float(m)) if k != "P" else 0}
        assert D(ssd) == len(g) * m * m + dev
    out["ระยะ"] = dist

    # ── Hurst แนวคิด ──
    out["เฮิร์สต์"] = {"เดินสุ่ม": [1, 2, 4], "ช่วง": [1, 4, 16], "เชือก": [1, 1.6, 2],
                       "ต่ำสุด": _r(min(r["hurst"] for r in rows)), "สูงสุด": _r(max(r["hurst"] for r in rows)),
                       "ต่ำกว่าครึ่ง": sum(1 for r in rows if r["hurst"] < 0.5)}

    # ════════════ 🎲 โลกปัจจัยที่รู้คำตอบ ════════════
    N = NF + NV

    def world(seed, null=False):
        Fm = M.factor_basket(seed=seed * 100 + 1, n=N, n_coins=1)["F"]
        cs, kind = [], {}
        for k in range(3):
            if null:
                p = M.random_walk_pair(seed=seed * 100 + 10 + k, n=N, sd=0.01, common_sd=0.02)
            else:
                p = M.stationary_pair(seed=seed * 100 + 10 + k, n=N, phi=0.9, sd=0.01, common_sd=0.02)
            cs += [p["logA"], p["logB"]]
            kind[(2 * k, 2 * k + 1)] = "rw" if null else "rope"
        p = M.random_walk_pair(seed=seed * 100 + 13, n=N, sd=0.005, common_sd=0.02)
        cs += [p["logA"], p["logB"]]
        kind[(6, 7)] = "tight"
        cs.append(M.random_walk_pair(seed=seed * 100 + 20, n=N, common_sd=0.02)["logB"])
        Ls = [[f + c for f, c in zip(Fm, cc)] for cc in cs]
        if null:
            Ls.append([f + c for f, c in zip(Fm, M.random_walk_pair(seed=seed * 100 + 30, n=N, common_sd=0.02)["logB"])])
        else:
            Ls.append(M.factor_basket(seed=seed * 100 + 30, n=N, n_coins=1, betas=[0.0], phis=[0.97], idio_sd=0.02)["logP"][0])
            for i in range(9):
                kind[(i, 9)] = "trap"
        return Ls, kind

    def analyse(seed, null=False):
        Ls, kind = world(seed, null)
        Ps = [[math.exp(v) for v in l_] for l_ in Ls]
        sing = [S.adf(l_[:NF])["reject5"] for l_ in Ls]
        res = []
        for i, j in itertools.combinations(range(10), 2):
            e1, e2 = S.engle_granger(Ls[i][:NF], Ls[j][:NF]), S.engle_granger(Ls[j][:NF], Ls[i][:NF])
            a, b, e = (i, j, e1) if e1["stat"] <= e2["stat"] else (j, i, e2)
            h = e["h"]
            X = [p - h * q for p, q in zip(Ls[a][:NF], Ls[b][:NF])]
            mX, sX = S.mean(X), S.sd(X)
            Xv = [p - h * q for p, q in zip(Ls[a][NF:], Ls[b][NF:])]
            Av, Bv = Ps[a][NF:], Ps[b][NF:]
            r = E.run(Av, Bv, h * Ps[a][NF - 1] / Ps[b][NF - 1], [(x - mX) / sX for x in Xv], sets=LEG / Ps[a][NF - 1], hold=30)
            res.append({"kind": kind.get((i, j), "none"), "one": e1["reject5"], "best": e["reject5"], "h": h,
                        "hl": S.half_life(S.ar1(X)["phi"]), "cr": _crossings(X) / (NF / 365.0),
                        "rc": S.corr(S.diff(Ls[i][:NF]), S.diff(Ls[j][:NF])), "net": r["net"],
                        "trap": sing[i] or sing[j], "vcross": _crossings(Xv, mX)})
        return res, sing

    def pipe(rs):
        s1 = [r for r in rs if r["best"]]
        s2 = [r for r in s1 if not r["trap"] and 0.5 <= r["h"] <= 2]
        s3 = [r for r in s2 if r["hl"] <= 30 and r["cr"] >= 12]
        s4 = [r for r in s3 if r["vcross"] >= 6]
        return [rs, s1, s2, s3, s4]

    stage_names = ["45 คู่", "ผ่าน Engle–Granger", "ตัดเหรียญนิ่งเดี่ยว · h สมเหตุผล", "Half-life · Zero Crossing", "ช่วงตรวจยังข้าม Mean เดิม"]
    acc = {"rope": [[] for _ in stage_names], "other": [[] for _ in stage_names]}
    nul = {"one": [], "best": []}
    ex = {}
    extra = {"tight_top": 0, "tight_net": [], "rope_net": [], "trap_net": [], "other_net": [], "trapflag": 0, "trap_pass": [],
             "tight_pass": 0}
    for s in M.ROBUST_SEEDS:
        rs, sing = analyse(s)
        st = pipe(rs)
        for k, g in enumerate(st):
            acc["rope"][k].append(sum(1 for r in g if r["kind"] == "rope"))
            acc["other"][k].append(sum(1 for r in g if r["kind"] != "rope"))
        if s == 1:
            ex = {"rope": [sum(1 for r in g if r["kind"] == "rope") for g in st],
                  "other": [sum(1 for r in g if r["kind"] != "rope") for g in st]}
        extra["tight_top"] += int(max(rs, key=lambda r: r["rc"])["kind"] == "tight")
        extra["tight_net"].append([r["net"] for r in rs if r["kind"] == "tight"][0])
        extra["tight_pass"] += sum(1 for r in rs if r["kind"] == "tight" and r["best"])
        extra["rope_net"].append(S.mean([r["net"] for r in rs if r["kind"] == "rope"]))
        extra["trap_net"].append(S.mean([r["net"] for r in rs if r["kind"] == "trap"]))
        extra["other_net"].append(S.mean([r["net"] for r in rs if r["kind"] in ("none", "rw")]))
        extra["trapflag"] += int(sing[9])
        extra["trap_pass"].append(sum(1 for r in rs if r["kind"] == "trap" and r["best"]))
        rn, _ = analyse(s, null=True)
        nul["one"].append(sum(1 for r in rn if r["one"]))
        nul["best"].append(sum(1 for r in rn if r["best"]))
    nw = len(M.ROBUST_SEEDS)
    out["จำลองสายพาน"] = {
        "ขั้น": stage_names,
        "มีเชือกมัธยฐาน": [_r(med(v), 1) for v in acc["rope"]], "อื่นมัธยฐาน": [_r(med(v), 1) for v in acc["other"]],
        "มีเชือกเฉลี่ย": [_r(S.mean(v), 1) for v in acc["rope"]], "อื่นเฉลี่ย": [_r(S.mean(v), 1) for v in acc["other"]],
        "ตัวอย่าง": ex, "โลก": nw,
        "ครบสามโลก": sum(1 for v in acc["rope"][4] if v == 3), "หลุดอื่นศูนย์โลก": sum(1 for v in acc["other"][4] if v == 0),
        "แน่นcorrสูงสุดโลก": extra["tight_top"], "แน่นผ่านEG": extra["tight_pass"],
        "แน่นเงินมัธยฐาน": _r(med(extra["tight_net"]), 1),
        "เชือกเงินมัธยฐาน": _r(med(extra["rope_net"]), 1),
        "เชือกเงินต่ำสุด": _r(min(extra["rope_net"]), 0), "เชือกเงินสูงสุด": _r(max(extra["rope_net"]), 0), "กับดักเงินมัธยฐาน": _r(med(extra["trap_net"]), 1),
        "อื่นเงินมัธยฐาน": _r(med(extra["other_net"]), 1),
        "อื่นเงินต่ำสุด": _r(min(extra["other_net"]), 0), "อื่นเงินสูงสุด": _r(max(extra["other_net"]), 0),
        "กับดักถูกจับโลก": extra["trapflag"], "กับดักผ่านมัธยฐาน": _r(med(extra["trap_pass"]), 1),
        "ศูนย์ทิศเดียวมัธยฐาน": _r(med(nul["one"]), 1), "ศูนย์ทิศเดียวเฉลี่ย": _r(S.mean(nul["one"]), 2),
        "ศูนย์ทิศเดียวต่ำสุด": min(nul["one"]), "ศูนย์ทิศเดียวสูงสุด": max(nul["one"]),
        "ศูนย์สองทิศเฉลี่ย": _r(S.mean(nul["best"]), 2), "ศูนย์สองทิศสูงสุด": max(nul["best"]),
        "ศูนย์หกขึ้นไป": sum(1 for v in nul["one"] if v >= 6),
        "ทวินามหกเปอร์เซ็นต์": _r(100 * (1 - sum(math.comb(45, k) * 0.05 ** k * 0.95 ** (45 - k) for k in range(6))), 1),
        "ทวินามหกโลก": _r(nw * (1 - sum(math.comb(45, k) * 0.05 ** k * 0.95 ** (45 - k) for k in range(6))), 1),
        "ศูนย์ทิศเดียว": nul["one"],
        "phi": 0.9, "hlเชือก": _r(S.half_life(0.9), 1), "กับดักphi": 0.97,
    }

    # ════════════ ตอน ค: ตัวกรองไหนทำนายกำไรช่วงตรวจ ════════════
    n45 = len(rows)
    metrics = [("rho_ret", "+", "Correlation ของผลตอบแทน"), ("rho_lvl", "+", "Correlation ของระดับราคา"),
               ("eg_stat", "−", "ค่าสถิติ Engle–Granger"), ("hl", "−", "Half-life"), ("cross", "+", "Zero Crossing ต่อปี"),
               ("sd_rt", "+", "SD ของ X ÷ ต้นทุน"), ("hurst", "−", "Hurst Exponent"), ("h_drift", "−", "h ครึ่งแรกกับครึ่งหลังต่างกัน")]
    sp = []
    for m_, sign, th in metrics:
        xs = [r[m_] if r[m_] != float("inf") else 1e9 for r in rows]
        a = spearman(xs, [r["net"] for r in rows])
        b = spearman(xs, [r["roll"] for r in rows])
        helped_a = (a > 0.1) if sign == "+" else (a < -0.1)
        sp.append({"ชื่อ": th, "คีย์": m_, "ทิศ": sign, "ตรึง": _r(a), "เลื่อน": _r(b), "ช่วย": helped_a})
    out["สเปียร์แมน"] = {m_["คีย์"]: m_ for m_ in sp}
    out["สเปียร์แมนแถว"] = sp
    out["ช่วยได้"] = sum(1 for m_ in sp if m_["ช่วย"])
    out["สั่นเอง"] = {"n": n45, "nลบหนึ่ง": n45 - 1, "ราก": _r(math.sqrt(n45 - 1)), "สั่น": _r(1 / math.sqrt(n45 - 1)),
                      "สองเท่า": _r(2 / math.sqrt(n45 - 1))}

    # Rank Correlation ด้วยมือห้าคู่ (อันดับ correlation ไม่ซ้ำกันเมื่อปัดสองตำแหน่ง)
    five = ["ETH/BTC", "ADA/BTC", "LTC/ETH", "BNB/DOGE", "XRP/BNB"]
    fr = [by[p] for p in five]
    rk_c = _ranks([-r["rho_ret"] for r in fr])
    rk_n = _ranks([-r["net"] for r in fr])
    d2 = [(a - b) ** 2 for a, b in zip(rk_c, rk_n)]
    dev = [((a - 3) * (b - 3)) for a, b in zip(rk_c, rk_n)]
    out["ห้าคู่"] = {"แถว": [{"คู่": p, "rho": _r(r["rho_ret"]), "net": _r(r["net"], 0), "อันดับrho": int(a), "อันดับnet": int(b),
                              "ต่าง": int(a - b), "ต่าง2": int(dd), "คูณ": int(dv)}
                             for p, r, a, b, dd, dv in zip(five, fr, rk_c, rk_n, d2, dev)],
                     "รวมต่าง2": int(sum(d2)), "รวมคูณ": int(sum(dev)), "ผล": _r(1 - 6 * sum(d2) / 120),
                     "ผลคูณ": _r(sum(dev) / 10), "หกเท่า": int(6 * sum(d2))}
    assert abs(out["ห้าคู่"]["ผล"] - out["ห้าคู่"]["ผลคูณ"]) < 1e-9

    def grp(g):
        return {"n": len(g), "เฉลี่ย": _r(S.mean([r["net"] for r in g]), 1), "กำไร": sum(1 for r in g if r["net"] > 0),
                "เลื่อนเฉลี่ย": _r(S.mean([r["roll"] for r in g]), 1), "เลื่อนกำไร": sum(1 for r in g if r["roll"] > 0)}

    chain = [r for r in rows if r["eg_p"] < 0.10 and r["hl"] <= 30 and r["cross"] >= 12]
    groups = {
        "ทั้งหมด": grp(rows), "ผ่านEG": grp(passes),
        "rhoบน5": grp(sorted(rows, key=lambda r: -r["rho_ret"])[:5]),
        "ระดับบน5": grp(sorted(rows, key=lambda r: -r["rho_lvl"])[:5]),
        "rhoล่าง5": grp(sorted(rows, key=lambda r: r["rho_ret"])[:5]),
        "hl30": grp([r for r in rows if r["hl"] <= 30]),
        "สายพานไม่ทดสอบเดี่ยว": grp(chain),
        "hurst": grp([r for r in rows if r["hurst"] < 0.5]),
    }
    out["กลุ่ม"] = groups
    out["กลุ่มเพิ่ม"] = {
        "rhoบน5ช่วง": [_r(sorted(rows, key=lambda r: -r["rho_ret"])[4]["rho_ret"]), _r(sorted(rows, key=lambda r: -r["rho_ret"])[0]["rho_ret"])],
        "ระดับบน5ช่วง": [_r(sorted(rows, key=lambda r: -r["rho_lvl"])[4]["rho_lvl"]), _r(sorted(rows, key=lambda r: -r["rho_lvl"])[0]["rho_lvl"])],
        "rhoล่าง5XRP": all("XRP" in r["pair"] for r in sorted(rows, key=lambda r: r["rho_ret"])[:5]),
        "สายพานLTC": sum(1 for r in chain if "LTC" in r["pair"]), "สายพานXRP": sum(1 for r in chain if "XRP" in r["pair"] and "LTC" not in r["pair"]),
        "ETHBTCตรึง": _r(by["ETH/BTC"]["net"], 0), "ETHBTCเลื่อน": _r(by["ETH/BTC"]["roll"], 0),
    }

    # สายพานบนข้อมูลจริง: ทดสอบเดี่ยวก่อน
    s_single = [r for r in rows if not (single[r["A"]]["ผ่าน"] or single[r["B"]]["ผ่าน"])]
    s_eg5 = [r for r in s_single if r["eg_pass"]]
    s_eg10 = [r for r in s_single if r["eg_p"] < 0.10]
    s_speed10 = [r for r in s_eg10 if r["hl"] <= 30 and r["cross"] >= 12]
    out["สายพานจริง"] = {
        "หลังตัดเดี่ยว": len(s_single), "ตัดออก": n45 - len(s_single), "EG5": len(s_eg5), "EG10": len(s_eg10),
        "เร็ว10": len(s_speed10), "เร็ว10คู่": [r["pair"] for r in s_speed10],
        "เร็ว10เงิน": [_r(r["net"], 0) for r in s_speed10], "เร็ว10hl": [_r(r["hl"], 0) for r in s_speed10],
        "เร็ว10ข้าม": [_r(r["cross"], 1) for r in s_speed10], "เร็ว10p": [_r(r["eg_p"], 2) for r in s_speed10],
        "เร็ว10ข้ามตรวจ": [r["val_cross"] for r in s_speed10], "XRPเดี่ยวp": single["XRP"]["p"],
    }

    # ความคงอยู่: ไม้บรรทัดเดิมทั้งอัน (h และ Mean ของช่วงเลือก)
    pc = sorted(passes, key=lambda r: r["eg_stat"])
    out["คงอยู่"] = {
        "แถว": [{"คู่": r["pair"], "ข้ามเลือก": _r(r["cross"], 1), "ข้ามตรวจ": r["val_cross"], "Meanห่างsd": _r(r["val_mean_sd"]),
                 "Meanย้าย": _r(r["val_mean_shift"], 0)} for r in pc],
        "ข้ามตรวจต่ำสุด": min(r["val_cross"] for r in pc), "ข้ามตรวจสูงสุด": max(r["val_cross"] for r in pc),
        "ข้ามเลือกต่ำสุด": _r(min(r["cross"] for r in pc), 1), "ข้ามเลือกสูงสุด": _r(max(r["cross"] for r in pc), 1),
        "ห่างต่ำสุด": _r(min(r["val_mean_sd"] for r in pc)), "ห่างสูงสุด": _r(max(r["val_mean_sd"] for r in pc)),
        "ย้ายต่ำสุด": _r(min(r["val_mean_shift"] for r in pc), 0), "ย้ายสูงสุด": _r(max(r["val_mean_shift"] for r in pc), 0),
        "Meanใหม่ผ่าน": sum(1 for r in pc if r["val_adf_c"]),
        "หาใหม่ผ่าน": sum(1 for r in pc if r["val_eg_pass"]), "หาใหม่ผ่านทั้งหมด": sum(1 for r in rows if r["val_eg_pass"]),
        "หาใหม่ผ่านXRP": sum(1 for r in rows if r["val_eg_pass"] and "XRP" in r["pair"] and "LTC" not in r["pair"]),
        "rhoคงอยู่": _r(S.corr([r["rho_ret"] for r in rows], [r["rho_ret_val"] for r in rows])),
        "XRPข้ามตรวจ": max(by[p]["val_cross"] for p in xrpn),
        "XRPห่างต่ำสุด": _r(min(by[p]["val_mean_sd"] for p in xrpn), 1), "XRPห่างสูงสุด": _r(max(by[p]["val_mean_sd"] for p in xrpn), 1),
    }
    tot_tr = sum(r["trades"] for r in rows)
    out["ไม้"] = {"ไม้": tot_tr, "หมดเวลา": sum(r["time_exits"] for r in rows),
                  "หมดเวลาเปอร์เซ็นต์": _r(100 * sum(r["time_exits"] for r in rows) / tot_tr, 0),
                  "gross": _r(sum(r["gross"] for r in rows), 0), "ต้นทุน": _r(sum(r["costs"] for r in rows), 0),
                  "net": _r(sum(r["net"] for r in rows), 0), "ค้างตอนจบ": sum(1 for r in rows if r["open"] != 0),
                  "ไม่มีไม้": sum(1 for r in rows if r["trades"] == 0), "คู่": n45,
                  "ต้นทุนต่อgrossเปอร์เซ็นต์": _r(100 * sum(r["costs"] for r in rows) / sum(r["gross"] for r in rows), 0)}
    out["จริง"] = {"วันเลือก": len(fd), "วันตรวจ": len(vd), "เริ่มเลือก": fd[0], "จบเลือก": fd[-1], "เริ่มตรวจ": vd[0],
                   "จบตรวจ": vd[-1], "เหรียญ": len(coins), "คู่": n45, "ดูช่วงตรวจ": 3}
    # ตาราง 10 แถวตัวอย่าง (เรียงตาม correlation ของผลตอบแทน · ทุก ๆ 5 อันดับ)
    srt = sorted(rows, key=lambda r: -r["rho_ret"])
    out["ตัวอย่างสิบ"] = [{"คู่": r["pair"], "rho": _r(r["rho_ret"]), "p": _r(r["eg_p"]), "hl": _r(r["hl"], 0),
                           "ข้าม": _r(r["cross"], 1), "hurst": _r(r["hurst"]), "net": _r(r["net"], 0), "ไม้": r["trades"]}
                          for r in srt[::5][:9] + [by["LTC/BTC"]]]

    # กราฟกลุ่ม
    out["กราฟกลุ่ม"] = {"ชื่อ": ["ทั้ง 45 คู่", "ผ่าน EG (LTC ทั้งหมด)", "สายพานไม่ทดสอบเดี่ยว", "Correlation สูงสุด 5",
                                 "ระดับราคาสูงสุด 5", "Half-life ≤ 30", "Correlation ต่ำสุด 5"],
                        "ค่า": [groups[k]["เฉลี่ย"] for k in ("ทั้งหมด", "ผ่านEG", "สายพานไม่ทดสอบเดี่ยว", "rhoบน5", "ระดับบน5", "hl30", "rhoล่าง5")]}

    # ════════════ 🧰 คนทำงานจริง (ที่มา: practitioner-research.md · ตัวเลขตามที่บันทึก ไม่ได้คำนวณ) ════════════
    out["คนทำงานจริง"] = {
        "ปีGGR": "2006", "ปีKrauss": "2017", "ปีKraussWP": "2015", "ปีRad": "2016", "ปีClegg": "2014", "ปีCXO": "2014",
        "ปีDoFaff": "2010", "ปีDoFaff2": "2012", "ปีSarmento": "2020", "ปีAL": "2010", "ปีChan": "2007", "ปีFil": "2020",
        "ปีหลังDoFaff": "2002", "ปีPindza": "2026",
        "Radบรรจบเปอร์เซ็นต์": 62.53, "Radบรรจบกำไรเปอร์เซ็นต์": 98, "DoFaffไม่บรรจบเปอร์เซ็นต์": 32,
        "Sarmentoข้ามต่อปี": 12, "SarmentoEGเปอร์เซ็นต์": 1, "ALวัน": 30, "ALหน้าต่าง": 60, "Chanเท่า": 3,
        "Cleggผ่านเปอร์เซ็นต์": 5.0, "Cleggคงอยู่เปอร์เซ็นต์": 4.9, "Cleggปีเริ่ม": "2002", "Cleggปีจบ": "2012",
        "Filรายวันเปอร์เซ็นต์": -0.07, "Filห้านาทีเปอร์เซ็นต์": 11.61, "Filเหรียญ": 26,
        "ALselectionPool": 50, "ALnumTop": 5, "skipตัวอย่าง": 10,
        "GGRยูทิลิตี้เปอร์เซ็นต์": 71, "GGRเดือนเลือก": 12, "GGRเดือนเทรด": 6, "Pindzaต้นทุนเปอร์เซ็นต์": 0.08,
    }

    # ════════════ แบบฝึก ════════════
    exr = {}
    # ข้อ 1: ρ 0.90 · σ 3.5 · HL 5
    two = 2 * (1 - D("0.90"))
    root = qd(D(math.sqrt(float(two))), 2)
    day = qd(root * D(str(SIGMA)), 2)
    sw = qd(day / D(str(hl_rows["5"]["ราก"])), 2)
    per = qd(D("1.5") * sw, 2)
    usd = qd(per * LEG / 100, 2)
    exr["ข้อ1"] = {"rho": 0.9, "สองเท่า": float(two), "ราก": float(root), "sdวัน": float(day), "sdแกว่ง": float(sw),
                   "กำไร": float(per), "ดอลลาร์": float(usd), "เท่าเล่ม": float(qd(usd / qd(rt_book * LEG / 100), 1))}
    # ข้อ 2: ρ 0.98 · σ 2 · HL 5 · ต้นทุนแอป
    day2 = qd(D("0.2") * 2, 2)
    sw2 = qd(day2 / D(str(hl_rows["5"]["ราก"])), 2)
    per2 = qd(D("1.5") * sw2, 2)
    usd2 = qd(per2 * LEG / 100, 2)
    exr["ข้อ2"] = {"sigma": 2, "sdวัน": float(day2), "sdแกว่ง": float(sw2), "กำไร": float(per2), "ดอลลาร์": float(usd2),
                   "เท่าแอป": float(qd(usd2 / qd(rt_retail * LEG / 100), 1)), "เหลือแอป": float(usd2 - qd(rt_retail * LEG / 100))}
    # ข้อ 3: ระยะหกวัน
    g3 = [3, -1, 3, -1, 3, -1]
    m3 = D(sum(g3)) / len(g3)
    exr["ข้อ3"] = {"ห่าง": g3, "SSD": sum(x * x for x in g3), "Mean": float(m3), "nMean2": float(len(g3) * m3 * m3),
                   "ส่วนแกว่ง": float(sum((D(x) - m3) ** 2 for x in g3)), "ข้าม": _crossings(g3, float(m3))}
    out["แบบฝึก"] = exr
    out["_แบบฝึก"] = [
        {"โจทย์": "(ทำตาม) ρ 0.90 σ 3.5% Half-life 5 → SD วันของ X · กำไรต่อไม้ · เท่าของต้นทุนเล่ม", "คำตอบ": exr["ข้อ1"]["เท่าเล่ม"]},
        {"โจทย์": "(เปลี่ยนเลข) σ 2% แทน 3.5% ที่ ρ 0.98 → กำไรต่อไม้เทียบต้นทุนแอป", "คำตอบ": exr["ข้อ2"]["เท่าแอป"]},
        {"โจทย์": "(เปลี่ยนเงื่อนไข) ระยะหกวัน 3, −1, … → SSD สองวิธี · Zero Crossing", "คำตอบ": exr["ข้อ3"]["SSD"]},
        {"โจทย์": "(ตัดสินใจ) แปดคู่ผ่านและกำไรทุกคู่ในช่วงตรวจ ลงเงินทั้งแปดไหม", "คำตอบ": out["ขาร่วม"]["corrLTC"]},
        {"โจทย์": "(ถ่ายโอน · ข้อมูลจริง) ETH/BTC กับสัญญาสองตัวของเหรียญเดียว", "คำตอบ": out["จริงก"]["เท่าต่ำสุด"]},
    ]
    out["_claims"] = [
        {"id": "sab2-ch08-spread-sd",
         "ข้อความ": "SD ของผลต่างผลตอบแทนสองเหรียญที่ SD เท่ากัน σ และ correlation ρ คือ σ√(2(1 − ρ)) (ความแปรปรวนของผลต่าง "
                    "= σ² + σ² − 2ρσ²) · ตัวอย่าง ρ 0.98 σ 3.5% ได้ 0.70% ต่อวัน",
         "ระดับหลักฐาน": "ตีพิมพ์", "แหล่ง": "สูตรความแปรปรวนของผลต่าง · Krauss (2015 WP) eqs. 4–5 · practitioner-research.md §2.2", "บท": [8]},
        {"id": "sab2-ch08-ssd",
         "ข้อความ": "ผลรวมกำลังสองของระยะห่าง (SSD) ของ Distance Method = n × Mean² + ผลรวมกำลังสองรอบ Mean จึงจัดอันดับคู่ที่ "
                    "Spread แกว่งน้อยไว้บนสุด (Krauss 2015 WP pp. 6–7)",
         "ระดับหลักฐาน": "ตีพิมพ์", "แหล่ง": "Krauss, C. (2017) J. Economic Surveys 31(2) · WP FAU 09/2015", "บท": [8]},
    ]
    return out
