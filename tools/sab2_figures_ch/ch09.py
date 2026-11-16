"""เล่ม 2 บท 9 — หักแรงร่วมออก เหลืออะไร · ตัวเลขทุกตัวของ docs/sab2-part9.html

ตอน ก  ด้วยมือ: สามเหรียญ (A β 1.5 · D β 0.5 · E β 1) บน BTC หกวัน · Mean ศูนย์ทุกคอลัมน์ → β = Σ(m × r) ÷ Σ(m²)
       (สูตร Slope ของบท 1) · Residual Return = r − β × m · ตรวจสองทาง: Σ residual = 0 กับ Σ(m × residual) = 0
       และผลรวมกำลังสองที่ β ± 0.1 · ทวนวิธีนับ beta ของเล่ม 1 บท 8 (เฉพาะวันที่ BTC ขยับแรง)
ตอน ข  ถือ "ส่วนที่เหลือ": ซื้อ A 500 ดอลลาร์ (5 เหรียญที่ 100) · short BTC β × 500 = 750 (0.015 BTC ที่ 50,000)
       สมุดหกวันด้วยจำนวนคงที่ เทียบ 500 × residual · Cumulative Residual · hedge ด้วย Equal-weight Index (10 ขา)
ตอน ค  📡 ช่วงเลือก: 9 เหรียญบน BTC (β · R² · SD residual · β ช่วงตรวจ) · ADF/Half-life ของ residual สะสม
       · correlation ของ residual (บน BTC กับบนดัชนี) · β จากการขยับ (LTC) เทียบ h จากระดับ log ราคา (Engle–Granger)
       🎲 factor_basket 10 เหรียญ (เหรียญ 0 = "BTC จำลอง" β 1) · β บนเหรียญ 0 หดเหลือ ~0.68 ของจริง · บนดัชนีได้ ~1
ตอน ง  Residual Reversal / Momentum: แปดสัปดาห์ด้วยมือ (ความชัน −0.5) · 📡 correlation รวม 9 เหรียญที่ 1/5/10/20 วัน
       ช่วงเลือกกับช่วงตรวจ · การ์ดเล่ม 1 บน Z หน้าต่าง 60 วันของ residual สะสม (ช่วงตรวจ · กลับทิศ กับ ตามทิศ)
       🎲 โลกมีเชือก (φ 0.9) กับโลกไม่มีเชือก (φ 1) · ประตูความเร็วแบบ Avellaneda–Lee (1/θ < 30 วัน) บนหน้าต่าง 60 วัน
ช่วงทดสอบสุดท้ายไม่ถูกแตะ (load_closes("formation") และ ("validation") เท่านั้น)
"""

import itertools
import math
import statistics

import sab_book as SB

NF, NV = 731, 365
LEG = 500
W = 60                       # หน้าต่างของไม้บรรทัดเลื่อน (Avellaneda–Lee ใช้ 60 วัน)
SIM_BETAS = [1.0, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 0.85, 1.15]   # เหรียญ 0 = BTC จำลอง
HORIZONS = (1, 5, 10, 20)


def _r(v, n=2):
    v = round(float(v) + 0.0, n)
    return int(v) if v == int(v) else v


def extend(data, D, q):
    import sab2_engine as E
    import sab2_sim as M
    import sab2_stats as S
    from sab2_realdata import load_closes

    from decimal import ROUND_HALF_UP

    def qd(x, n=2):
        d = x if isinstance(x, D) else D(str(x))
        return d.quantize(D(1).scaleb(-n), rounding=ROUND_HALF_UP)

    out = {}

    # ════════════ เล่ม 1 ที่ทวน ════════════
    f1 = SB.load_figures("sab")
    sc = f1["ch08"]["ฉาก"]
    hb = f1["ch08"]["hedgeBTCเต็ม"]
    c11 = f1["ch11"]["v2"]["ต้นทุน"]
    out["เล่ม1"] = {"Aมูลค่า": sc["Aมูลค่า"], "betaA": sc["betaA"], "betaexposureA": sc["betaexposureA"],
                    "betaexposureสุทธิ": sc["betaexposureสุทธิ"], "hedgeเต็ม": hb["มูลค่า"],
                    "ต่อfillเปอร์เซ็นต์": c11["อัตราtakerเปอร์เซ็นต์"], "เข้า": 2, "ออก": 0.5, "ถือ": 30,
                    "นับAรวม": 30, "นับBTCรวม": 20, "นับเกณฑ์": 2}

    # ════════════ ตอน ก · ด้วยมือ: สามเหรียญบน BTC หกวัน ════════════
    m = [2, -2, 1, -1, 0, 0]
    coins_h = {"A": [3, -3, 2, -1, 1, -2], "D": [1, -1, 1, 0, -1, 0], "E": [2, -2, 0, -2, 1, 1]}
    smm = sum(x * x for x in m)
    hand = {"m": m, "smm": smm}
    for k, r in coins_h.items():
        smr = sum(a * b for a, b in zip(m, r))
        beta = D(smr) / D(smm)
        res = [D(b) - beta * a for a, b in zip(m, r)]
        ssr = sum(e * e for e in res)
        srr = sum(x * x for x in r)
        cum, run = [], D(0)
        for e in res:
            run += e
            cum.append(float(run))
        hand[k] = {"r": r, "mr": [a * b for a, b in zip(m, r)], "smr": smr, "beta": float(beta),
                   "fit": [float(beta * a) for a in m], "res": [float(e) for e in res], "ssr": float(ssr),
                   "srr": srr, "อธิบาย": float(srr - ssr), "r2": float(qd((D(srr) - ssr) / D(srr), 2)),
                   "sumres": float(sum(res)), "smres": float(sum(D(a) * e for a, e in zip(m, res))), "cum": cum,
                   "นับเล่ม1": float(D(abs(r[0]) + abs(r[1])) / D(abs(m[0]) + abs(m[1])))}
    # ผลรวมกำลังสองที่ β ± 0.1 (A): 10 × 0.01 + 5.5
    for b in ("1.4", "1.6"):
        bb = D(b)
        res = [D(y) - bb * x for x, y in zip(m, coins_h["A"])]
        hand["A"]["ssr" + b.replace(".", "")] = float(sum(e * e for e in res))
        hand["A"]["res" + b.replace(".", "")] = [float(e) for e in res]
    hand["A"]["เพิ่ม"] = float(D(smm) * D("0.01"))
    out["มือ"] = hand

    # ════════════ ตอน ข · ถือส่วนที่เหลือของ A เป็นจำนวนเหรียญ ════════════
    pa0, pb0 = D(100), D(50000)
    beta = D(str(hand["A"]["beta"]))
    qa = D(LEG) / pa0
    bval = beta * LEG
    qb = bval / pb0
    rows = []
    pa, pb = pa0, pb0
    cum_l = D(0)
    cum_r = D(0)
    for a_, m_, e in zip(coins_h["A"], m, hand["A"]["res"]):
        na = pa * (1 + D(a_) / 100)
        nb = pb * (1 + D(m_) / 100)
        la = qa * (na - pa)
        lb = -qb * (nb - pb)
        cum_l += la + lb
        cum_r += D(str(e))
        rows.append({"A": float(qd(na, 2)), "BTC": float(qd(nb, 0)), "ขาA": float(qd(la, 2)), "ขาBTC": float(qd(lb, 2)),
                     "รวม": float(qd(la + lb, 2)), "ห้าร้อยคูณ": float(qd(D(str(e)) * LEG / 100, 2)),
                     "สะสมเงิน": float(qd(cum_l, 2)), "สะสมresidual": float(cum_r),
                     "สะสมห้าร้อยคูณ": float(qd(cum_r * LEG / 100, 2)), "Aขยับ": a_, "BTCขยับ": m_, "res": e})
        pa, pb = na, nb
    out["ถือ"] = {"V": LEG, "Aราคา": int(pa0), "BTCราคา": int(pb0), "Aจำนวน": float(qa), "BTCมูลค่า": float(bval),
                  "BTCจำนวน": float(qb), "หน่วยต่อA": float(beta * pa0 / pb0), "exposureA": float(LEG * beta),
                  "exposureBTC": float(-bval), "exposureสุทธิ": float(LEG * beta - bval),
                  "วัน": rows, "วัน1ขาA": rows[0]["ขาA"], "วัน1ขาBTC": rows[0]["ขาBTC"],
                  "คลาดสูงสุด": max(abs(D(str(r_["รวม"])) - D(str(r_["ห้าร้อยคูณ"]))) for r_ in rows),
                  "จบเงิน": rows[-1]["สะสมเงิน"], "ยอดสะสมสูงสุด": max(r_["สะสมresidual"] for r_ in rows),
                  "ยอดเงินสูงสุด": max(r_["สะสมห้าร้อยคูณ"] for r_ in rows)}
    out["ถือ"]["คลาดสูงสุด"] = float(out["ถือ"]["คลาดสูงสุด"])
    # hedge ด้วยดัชนีถ่วงเท่ากัน 10 เหรียญ (A อยู่ในดัชนีด้วย)
    per = bval / 10
    fee = D(str(c11["อัตราtakerเปอร์เซ็นต์"])) / 100
    traded_btc = D(LEG) + bval
    traded_idx = (D(LEG) - per) + per * 9
    out["ดัชนี"] = {"ต่อขา": float(per), "Aสุทธิ": float(D(LEG) - per), "ขา": 10, "ขาBTC": 2,
                    "มูลค่าซื้อขายBTC": float(traded_btc), "มูลค่าซื้อขายดัชนี": float(traded_idx),
                    "ค่าธรรมเนียมBTC": float(qd(traded_btc * fee, 2)), "ค่าธรรมเนียมดัชนี": float(qd(traded_idx * fee, 2)),
                    "เก้าขา": float(per * 9)}

    # ════════════ ตอน ค · 📡 ข้อมูลจริง: 9 เหรียญบน BTC ════════════
    fd, F = load_closes("formation")
    vd, V = load_closes("validation")
    coins = list(F.keys())
    alts = [c for c in coins if c != "BTC"]
    LF = {c: S.logs(F[c]) for c in coins}
    LV = {c: S.logs(V[c]) for c in coins}
    RF = {c: S.diff(LF[c]) for c in coins}
    RV = {c: S.diff(LV[c]) for c in coins}
    ew = [sum(RF[c][t] for c in coins) / len(coins) for t in range(len(RF["BTC"]))]
    real = {}
    resF, resV, resE = {}, {}, {}
    for c in alts:
        o = S.ols(RF["BTC"], RF[c])
        ov = S.ols(RV["BTC"], RV[c])
        oe = S.ols(ew, RF[c])
        b = o["slope"]
        resF[c] = [y - b * x for x, y in zip(RF["BTC"], RF[c])]
        resV[c] = [y - b * x for x, y in zip(RV["BTC"], RV[c])]
        resE[c] = oe["residuals"]
        C = [0.0]                                   # Cumulative Residual: ผลรวมของ residual return (α หักออกแล้ว)
        for e in o["residuals"]:
            C.append(C[-1] + e)
        ad = S.adf(C)
        ar = S.ar1(C)
        real[c] = {"beta": _r(b), "alphaเปอร์เซ็นต์": _r(o["intercept"] * 100, 3), "r2": _r(o["r2"]),
                   "sdres": _r(o["sigma"] * 100), "betaV": _r(ov["slope"]), "r2V": _r(ov["r2"]),
                   "betaEW": _r(oe["slope"]), "adf": _r(ad["stat"]), "p": _r(ad["pvalue"], 3),
                   "pเปอร์เซ็นต์": _r(ad["pvalue"] * 100, 1), "hl": _r(S.half_life(ar["phi"]), 0),
                   "phi": _r(ar["phi"], 3), "เพิ่มเปอร์เซ็นต์": _r((ov["slope"] / b - 1) * 100, 0)}
    order = sorted(alts, key=lambda c: real[c]["beta"])

    def avgc(Dd):
        v = [S.corr(Dd[a], Dd[b]) for a, b in itertools.combinations(alts, 2)]
        return sum(v) / len(v)

    eg_ltc = S.engle_granger(LF["LTC"], LF["BTC"])
    adf_ltc = S.adf(LF["LTC"])
    b_ltc = S.ols(RF["BTC"], RF["LTC"])["slope"]
    a_ltc = S.ols(RF["BTC"], RF["LTC"])["intercept"]
    out["จริง"] = {
        "เหรียญ": real, "ลำดับ": order, "จำนวน": len(alts), "วันเลือก": len(fd), "วันตรวจ": len(vd),
        "เริ่มเลือก": fd[0], "จบเลือก": fd[-1], "เริ่มตรวจ": vd[0], "จบตรวจ": vd[-1],
        "betaต่ำสุด": min(real[c]["beta"] for c in alts), "betaสูงสุด": max(real[c]["beta"] for c in alts),
        "betaต่ำสุดเหรียญ": min(alts, key=lambda c: real[c]["beta"]), "betaสูงสุดเหรียญ": max(alts, key=lambda c: real[c]["beta"]),
        "betaVต่ำสุด": min(real[c]["betaV"] for c in alts), "betaVสูงสุด": max(real[c]["betaV"] for c in alts),
        "betaขึ้นทุกตัว": all(real[c]["betaV"] > real[c]["beta"] for c in alts),
        "betaเฉลี่ย": _r(S.mean([real[c]["beta"] for c in alts])), "betaVเฉลี่ย": _r(S.mean([real[c]["betaV"] for c in alts])),
        "r2ต่ำสุด": min(real[c]["r2"] for c in alts), "r2สูงสุด": max(real[c]["r2"] for c in alts),
        "corrดิบ": _r(avgc(RF)), "corrresBTC": _r(avgc(resF)), "corrresEW": _r(avgc(resE)),
        "corrresBTCตรวจ": _r(avgc(resV)),
        "adfผ่าน": sum(1 for c in alts if real[c]["adf"] <= S.adf(LF["ETH"])["crit"]["5%"]),
        "เส้น5": _r(S.adf(LF["ETH"])["crit"]["5%"]),
        "adfดีสุดเหรียญ": min(alts, key=lambda c: real[c]["adf"]),
        "hlต่ำสุด": min(real[c]["hl"] for c in alts), "hlสูงสุด": max(real[c]["hl"] for c in alts),
        "LTC": {"betaคืน": _r(b_ltc), "hระดับ": _r(eg_ltc["h"]), "adfเดี่ยว": _r(adf_ltc["stat"]), "alphaเปอร์เซ็นต์": _r(a_ltc * 100, 2),
                "alphaปี": _r(_r(a_ltc * 100, 2) * 365, 0)},
    }
    out["จริง"]["หนึ่งส่วนเก้า"] = _r(-1 / (len(alts) - 1), 2)

    # ════════════ ตอน ค · 🎲 โลกปัจจัยที่รู้ β ════════════
    def fworld(seed, phi):
        return M.factor_basket(seed=seed, n=NF + NV, n_coins=10, betas=SIM_BETAS, phis=[phi] * 10)

    def sim_one(seed, phi):
        w = fworld(seed, phi)
        L, P = w["logP"], w["P"]
        R = [S.diff(l[:NF]) for l in L]
        ewk = [sum(R[i][t] for i in range(10)) / 10 for t in range(NF - 1)]
        bb = [S.ols(R[0], R[i])["slope"] for i in range(1, 10)]
        be = [S.ols(ewk, R[i])["slope"] for i in range(1, 10)]
        resb = [[y - b * x for x, y in zip(R[0], R[i])] for b, i in zip(bb, range(1, 10))]
        cb = statistics.mean(S.corr(resb[a], resb[b]) for a, b in itertools.combinations(range(9), 2))
        xs, ys = [], []
        net = netm = 0.0
        tr = 0
        for j, i in enumerate(range(1, 10)):
            b = bb[j]
            e = [(L[i][t] - L[i][t - 1]) - b * (L[0][t] - L[0][t - 1]) for t in range(NF, NF + NV)]
            s20 = [sum(e[k:k + 20]) for k in range(0, len(e) - 19, 20)]
            xs += s20[:-1]
            ys += s20[1:]
            Cc = [L[i][t] - b * L[0][t] for t in range(NF - (W - 1), NF + NV)]
            z = [0.0] * len(Cc)
            for t in range(W - 1, len(Cc)):
                ww = Cc[t - W + 1:t + 1]
                z[t] = (Cc[t] - S.mean(ww)) / S.sd(ww)
            A_ = P[i][NF - (W - 1):]
            B_ = P[0][NF - (W - 1):]
            a0, b0 = P[i][NF - 1], P[0][NF - 1]
            r1 = E.run(A_, B_, b * a0 / b0, z, sets=LEG / a0, hold=30)
            r2 = E.run(A_, B_, b * a0 / b0, [-v for v in z], sets=LEG / a0, hold=30)
            net += r1["net"]
            netm += r2["net"]
            tr += r1["trades"]
        ratio_b = statistics.mean(x / t for x, t in zip(bb, SIM_BETAS[1:]))
        ratio_e = statistics.mean(x / t for x, t in zip(be, SIM_BETAS[1:]))
        return {"rb": ratio_b, "re": ratio_e, "cb": cb, "pc": S.corr(xs, ys), "net": net, "netm": netm, "tr": tr}

    sims = {}
    for nm, phi in (("เชือก", 0.9), ("ไม่มีเชือก", 1.0)):
        rs = [sim_one(s, phi) for s in M.ROBUST_SEEDS]
        med = statistics.median
        sims[nm] = {"phi": phi, "betaBTCส่วน": _r(med([r["rb"] for r in rs])), "betaEWส่วน": _r(med([r["re"] for r in rs])),
                    "corrres": _r(med([r["cb"] for r in rs])), "pc20": _r(med([r["pc"] for r in rs])),
                    "net": _r(med([r["net"] for r in rs]), 1), "netm": _r(med([r["netm"] for r in rs]), 1),
                    "บวก": sum(1 for r in rs if r["net"] > 0), "บวกm": sum(1 for r in rs if r["netm"] > 0),
                    "ไม้": _r(med([r["tr"] for r in rs]), 1), "netต่ำสุด": _r(min(r["net"] for r in rs), 1),
                    "netสูงสุด": _r(max(r["net"] for r in rs), 1)}
    # ที่มาของการหด: ความแปรปรวนรายวันของแรงร่วมกับข่าวของ BTC จำลองเอง (หน่วย 0.0001)
    w0 = fworld(1, 0.9)["true"]
    vf = w0["factor_sd"] ** 2 * 10000
    vu = 2 * w0["idio_sd"] ** 2 / (1 + 0.9) * 10000
    sims["หด"] = {"แรงร่วม": _r(vf, 1), "ข่าวBTC": _r(vu, 1), "รวม": _r(vf + vu, 1),
                  "ส่วน": _r(_r(vf, 1) / _r(vf + vu, 1)), "factorsd": _r(w0["factor_sd"] * 100, 1),
                  "idiosd": _r(w0["idio_sd"] * 100, 1), "โลก": len(M.ROBUST_SEEDS), "วัน": NF + NV,
                  "betaต่ำ": min(SIM_BETAS[1:]), "betaสูง": max(SIM_BETAS[1:]), "hlเชือก": _r(S.half_life(0.9), 1)}
    out["จำลอง"] = sims

    # ════════════ ตอน ง · ด้วยมือ: แปดสัปดาห์ของส่วนที่เหลือ ════════════
    wk = [3, -1, 3, -2, 1, -3, -1, 3]
    x7, y7 = wk[:-1], wk[1:]
    up = [b for a, b in zip(x7, y7) if a > 0]
    dn = [b for a, b in zip(x7, y7) if a < 0]
    sxy = sum(a * b for a, b in zip(x7, y7))
    sxx = sum(a * a for a in x7)
    out["สัปดาห์"] = {"ค่า": wk, "คู่": [[a, b] for a, b in zip(x7, y7)], "ผลคูณ": [a * b for a, b in zip(x7, y7)],
                      "กำลังสอง": [a * a for a in x7], "sxy": sxy, "sxx": sxx, "slope": float(D(sxy) / D(sxx)),
                      "syy": sum(b * b for b in y7), "ขึ้นถัดไป": up, "ลงถัดไป": dn,
                      "ขึ้นเฉลี่ย": float(D(sum(up)) / len(up)), "ลงเฉลี่ย": float(D(sum(dn)) / len(dn)),
                      "ขึ้นจำนวน": len(up), "ลงจำนวน": len(dn), "ผลรวมขึ้น": sum(up), "ผลรวมลง": sum(dn),
                      "sumx": sum(x7), "sumy": sum(y7)}

    # ════════════ ตอน ง · 📡 correlation รวมตามระยะ ════════════
    hz = {}
    for k in HORIZONS:
        row = {"k": k}
        for nm, Dd in (("F", resF), ("V", resV)):
            xs, ys = [], []
            for c in alts:
                e = Dd[c]
                s = [sum(e[i:i + k]) for i in range(0, len(e) - k + 1, k)]
                xs += s[:-1]
                ys += s[1:]
            cc = S.corr(xs, ys)
            row[nm] = _r(cc, 2)
            row[nm + "3"] = _r(cc, 3)
            row["n" + nm] = len(xs)
            row["se" + nm] = _r(1 / math.sqrt(len(xs)), 2)
            row["เท่า" + nm] = _r(abs(cc) * math.sqrt(len(xs)), 1)
        hz[str(k)] = row
    out["ระยะ"] = hz
    out["ระยะแถว"] = [hz[str(k)] for k in HORIZONS]

    # ════════════ ตอน ง · 📡 การ์ดเล่ม 1 บน Z ของ residual สะสม (ช่วงตรวจ) ════════════
    bt = {}
    tot = totm = cst = 0.0
    trs = tex = opn = 0
    for c in alts:
        b = real[c]["beta"]
        b = S.ols(RF["BTC"], RF[c])["slope"]
        A_ = F[c][-(W - 1):] + V[c]
        B_ = F["BTC"][-(W - 1):] + V["BTC"]
        Cc = [math.log(a) - b * math.log(x) for a, x in zip(A_, B_)]
        z = [0.0] * len(Cc)
        for t in range(W - 1, len(Cc)):
            ww = Cc[t - W + 1:t + 1]
            z[t] = (Cc[t] - S.mean(ww)) / S.sd(ww)
        a0, b0 = F[c][-1], F["BTC"][-1]
        r1 = E.run(A_, B_, b * a0 / b0, z, sets=LEG / a0, hold=30)
        r2 = E.run(A_, B_, b * a0 / b0, [-v for v in z], sets=LEG / a0, hold=30)
        te = sum(1 for t_ in r1["trade_list"] if t_["reason"] == "time")
        bt[c] = {"net": _r(r1["net"], 1), "netm": _r(r2["net"], 1), "ไม้": r1["trades"], "ไม้m": r2["trades"],
                 "หมดเวลา": te, "ค้าง": int(r1["open"] != 0), "ค้างm": int(r2["open"] != 0), "ต้นทุน": _r(r1["costs"], 1),
                 "ชนะ": r1["wins"], "Aขึ้นเปอร์เซ็นต์": _r((V[c][-1] / V[c][0] - 1) * 100, 0)}
        tot += r1["net"]
        totm += r2["net"]
        trs += r1["trades"]
        tex += te
        opn += int(r1["open"] != 0)
        cst += r1["costs"]
    exx = [c for c in alts if c != "XRP"]
    out["การ์ด"] = {"เหรียญ": bt, "รวม": _r(tot, 1), "รวมm": _r(totm, 1), "ไม้": trs, "หมดเวลา": tex, "ค้าง": opn,
                    "ค้างm": sum(bt[c]["ค้างm"] for c in alts), "ต้นทุน": _r(cst, 1),
                    "ไม่รวมXRP": _r(sum(bt[c]["net"] for c in exx), 1), "ไม่รวมXRPm": _r(sum(bt[c]["netm"] for c in exx), 1),
                    "บวก": sum(1 for c in alts if bt[c]["net"] > 0), "บวกm": sum(1 for c in alts if bt[c]["netm"] > 0),
                    "ไม้ต่อเหรียญเฉลี่ย": _r(trs / len(alts), 1),
                    "BTCขึ้นเปอร์เซ็นต์": _r((V["BTC"][-1] / V["BTC"][0] - 1) * 100, 0)}

    # ════════════ ประตูความเร็วแบบ Avellaneda–Lee บนหน้าต่าง 60 วัน ════════════
    tau = 30
    phi_cut = math.exp(-1 / tau)

    def gate_frac(Cc, step=5):
        k = n = 0
        for t in range(W, len(Cc) + 1, step):
            p = S.ar1(Cc[t - W:t])["phi"]
            n += 1
            if 0 < p < phi_cut:
                k += 1
        return k / n

    fr_real = []
    for c in alts:
        b = S.ols(RF["BTC"], RF[c])["slope"]
        fr_real.append(gate_frac([a - b * x for a, x in zip(LF[c], LF["BTC"])]))

    def gate_sim(phi):
        vals = []
        for s in M.ROBUST_SEEDS:
            w = M.factor_basket(seed=s, n=NF, n_coins=10, betas=SIM_BETAS, phis=[phi] * 10)
            L = w["logP"]
            R = [S.diff(l) for l in L]
            f = []
            for i in range(1, 10):
                b = S.ols(R[0], R[i])["slope"]
                f.append(gate_frac([a - b * x for a, x in zip(L[i], L[0])]))
            vals.append(statistics.mean(f))
        return statistics.median(vals)

    out["ประตู"] = {"tau": tau, "phiตัด": _r(phi_cut, 2), "hlตัด": _r(tau * math.log(2), 1), "หน้าต่าง": W,
                    "จริงเปอร์เซ็นต์": _r(statistics.mean(fr_real) * 100, 0),
                    "จริงต่ำสุด": _r(min(fr_real) * 100, 0), "จริงสูงสุด": _r(max(fr_real) * 100, 0),
                    "เดินสุ่มเปอร์เซ็นต์": _r(gate_sim(1.0) * 100, 0), "เชือกเปอร์เซ็นต์": _r(gate_sim(0.9) * 100, 0),
                    "ทุกวัน": 5}

    # ════════════ 🧰 คนทำงานจริง (ที่มา: practitioner-research.md · ตัวเลขตามที่บันทึก ไม่ได้คำนวณ) ════════════
    out["คนทำงานจริง"] = {
        "ปีAL": "2010", "ปีALpre": "2009", "ALหน้าต่าง": 60, "ALวัน": 30, "ALkappa": 8.4, "ALปีวัน": 252,
        "ALเข้า": 1.25, "ALออกlong": -0.5, "ALออกshort": 0.75,
        "ปีChen": "2019", "ปีKL": "2011", "ปีKLเหตุ": "2007", "ปีFischer": "2019", "Fischerเหรียญ": 40,
        "Fischerbps": 7.1, "Fischerต้นทุนbps": 15,
    }

    # ════════════ แบบฝึก ════════════
    g = [4, -4, 1, -1, 2, -2]
    smg = sum(a * b for a, b in zip(m, g))
    bg = D(smg) / D(smm)
    rg = [float(D(y) - bg * x) for x, y in zip(m, g)]
    ex = {"ข้อ1": {"g": g, "smr": smg, "beta": float(bg), "res": rg, "sumres": float(sum(D(str(v)) for v in rg)),
                   "smres": float(sum(D(a) * D(str(e)) for a, e in zip(m, rg))), "res5": rg[4]}}
    # ข้อ 2: เหรียญ D β 0.5 · ถือส่วนที่เหลือ 800 ดอลลาร์ · D ราคา 20 · BTC 40,000 · วันที่ BTC +3% D +2%
    V2, pd2, pbt2 = D(800), D(20), D(40000)
    bd = D(str(hand["D"]["beta"]))
    ex["ข้อ2"] = {"V": 800, "ราคา": 20, "BTCราคา": 40000, "จำนวน": float(V2 / pd2), "BTCมูลค่า": float(bd * V2),
                  "BTCจำนวน": float(bd * V2 / pbt2), "BTCขยับ": 3, "Dขยับ": 2,
                  "ขาD": float(V2 * 2 / 100), "ขาBTC": float(-bd * V2 * 3 / 100),
                  "รวม": float(V2 * 2 / 100 - bd * V2 * 3 / 100), "res": float(2 - bd * 3)}
    # ข้อ 3: ข่าวของ BTC จำลองเพิ่มเป็นสองเท่า → β หดเหลือเท่าไร
    vf1 = D(str(sims["หด"]["แรงร่วม"]))
    vu2 = D(str(sims["หด"]["ข่าวBTC"])) * 2
    ex["ข้อ3"] = {"ข่าวสองเท่า": float(vu2), "รวม": float(vf1 + vu2), "ส่วน": float(qd(vf1 / (vf1 + vu2), 2)),
                  "betaจริง": 1.2, "betaได้": float(qd(D("1.2") * qd(vf1 / (vf1 + vu2), 2), 2)),
                  "betaได้เดิม": float(qd(D("1.2") * D(str(sims["หด"]["ส่วน"])), 2))}
    out["แบบฝึก"] = ex
    out["_แบบฝึก"] = [
        {"โจทย์": "(ทำตาม) เหรียญ G หกวันบน BTC → β · residual · ตรวจสองทาง", "คำตอบ": ex["ข้อ1"]["beta"]},
        {"โจทย์": "(เปลี่ยนเลข) ถือส่วนที่เหลือของ D 800 ดอลลาร์ → จำนวนเหรียญ · วันที่ BTC +3% D +2%", "คำตอบ": ex["ข้อ2"]["รวม"]},
        {"โจทย์": "(เปลี่ยนเงื่อนไข) ข่าวของ BTC จำลองแรงขึ้นสองเท่า → β ที่ได้หดเหลือเท่าไร", "คำตอบ": ex["ข้อ3"]["ส่วน"]},
        {"โจทย์": "(ตัดสินใจ · ข้อมูลจริง) แบบตามทิศได้กำไรในช่วงตรวจ เปลี่ยนไปเทรดตามทิศไหม", "คำตอบ": out["การ์ด"]["ไม่รวมXRPm"]},
        {"โจทย์": "(ถ่ายโอน · ข้อมูลจริง) LTC: β จากการขยับ 0.84 กับ h จากระดับ log ราคา −0.04", "คำตอบ": out["จริง"]["LTC"]["betaคืน"]},
    ]
    out["ดูช่วงตรวจ"] = 4
    # เลขกลางทางที่หน้าคิดให้ดู (ผู้อ่านคิดตามได้จากเลขบนหน้า)
    out["เลขมือ"] = {
        "resกำลังสอง": [float(D(str(e)) * D(str(e))) for e in hand["A"]["res"]], "betaลอง": [1.4, 1.6],
        "ขาAวัน6มูลค่า": float(qd(D(str(rows[4]["A"])) * qa, 2)),
        "SOLขาBTC": float(qd(D(str(real["SOL"]["beta"])) * LEG, 0)), "BNBขาBTC": float(qd(D(str(real["BNB"]["beta"])) * LEG, 0)),
        "การขยับต่อเหรียญ": len(fd) - 1,
        "XRPขาหลังขึ้น": float(qd(D(LEG) * (1 + D(str(bt["XRP"]["Aขึ้นเปอร์เซ็นต์"])) / 100), 0)),
        "มูลค่าเท่ากันเหลือ": float(bval - LEG), "DขาBTC": float(D(str(hand["D"]["beta"])) * LEG),
        "Gวัน1": float(D(str(ex["ข้อ1"]["beta"])) * 2), "หนึ่งส่วนเก้าบวก": 0.11, "คู่เหรียญ": 36,
    }
    out["แกน"] = {"มือ": [-4, -3, -2, -1, 0, 1, 2, 3], "beta": [0, 0.5, 1, 1.5, 2], "ระยะ": [-0.2, -0.1, 0, 0.1]}
    out["_claims"] = [
        {"id": "sab2-ch09-attenuation",
         "ข้อความ": "เมื่อตัวแทนตลาดมีส่วนเฉพาะตัวปนอยู่ ค่า β ที่ถดถอยได้จะหดลงตามสัดส่วน ความแปรปรวนของแรงร่วม ÷ ความแปรปรวนรวม "
                    "ของตัวแทนนั้น (errors-in-variables) · โลกจำลองของบทได้ราว 0.68 ของค่าจริง",
         "ระดับหลักฐาน": "ตีพิมพ์", "แหล่ง": "ผลมาตรฐานของการถดถอยเมื่อตัวแปรต้นมีความคลาด (errors-in-variables) · คำนวณซ้ำในปลั๊กอิน", "บท": [9]},
        {"id": "sab2-ch09-al-gate",
         "ข้อความ": "Avellaneda & Lee (2010) ถดถอยหุ้นแต่ละตัวบนปัจจัยจากข้อมูลหรือ ETF ของกลุ่ม ใช้หน้าต่าง 60 วัน "
                    "เก็บเฉพาะตัวที่ κ > 252/30 และเข้าเมื่อ |s| > 1.25 ออก long ที่ −0.50 ออก short ที่ 0.75 · ไม่ใช้การทดสอบเป็นประตู",
         "ระดับหลักฐาน": "ตีพิมพ์", "แหล่ง": "practitioner-research.md §1.1 §3.3 (NYU preprint June 2009 §4)", "บท": [9]},
    ]
    return out
