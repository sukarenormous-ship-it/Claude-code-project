"""บท 14 เล่ม 2 — ลองได้กี่ครั้งก่อนผลจะไม่มีความหมาย · ค่าทุกตัวของบท (ปลั๊กอินของ tools/sab_figures.py --book sab2)

ตอน ก  มือ: สามเส้น × ห้าช่วง (ตัวเลขสอน) → ยอดเขาของช่วงเลือก · Walk-forward สามหน้าต่าง (sab2_stats.walk_forward)
       🎲 คู่จำลองแบบ LTC–DOT (price_pair φ 0.97) กับโลกไม่มีเชือก (φ 1) · walk-forward 3 หน้าต่างบน 30 โลกต่อแบบ
ตอน ข  นับครั้งที่ลอง: ตาราง "อย่างน้อยหนึ่ง" ของเล่ม 1 บท 10 · ผลดีสุดของ N ครั้งที่ไม่มีฝีมือ (เหรียญ ±1 · การแจกแจงปกติ)
       เส้นโชค = ผลดีสุดที่คาดจากโชค × SE ของ Sharpe (≈ 1 ÷ √จำนวนเดือน) · การนับของเล่มบท 1–13 (ดึงจากคีย์บทก่อนเมื่อมี)
ตอน ค  📡 LTC บน DOT (ราคา · h ช่วงเลือก 3.76 · 10 ชุด · ไม้บรรทัดช่วงเลือก) ตาราง เส้นเข้า 5 × ถือไม่เกิน 5 = 25 แบบ
       ยอดเขาช่วงเลือก → อันดับในช่วงตรวจ · Walk-forward สามหน้าต่าง 121 วันในช่วงตรวจ (เลือก h ไม้บรรทัด และแบบ จาก 365 วันก่อนหน้า)
       🎲 โลกคู่กันแบบเดียวกัน 30 โลก (ยอดเขาไปอยู่อันดับไหน · ผ่านเส้นโชคกี่โลก)
ข้อมูลจริงผ่าน sab2_realdata.load_closes("formation"/"validation") เท่านั้น · ไม่แตะช่วงทดสอบสุดท้าย
"""

import math
import statistics

import sab_book as SB
import sab2_engine as E
import sab2_realdata as R
import sab2_sim as M
import sab2_stats as S

ENTRIES = (1, 1.5, 2, 2.5, 3)      # เส้นเข้า (Z-score) · ห้าเส้นเดียวกับบท 7
HOLDS = (10, 20, 30, 45, 60)       # ถือไม่เกินกี่วัน · 30 = การ์ดของเล่ม 1
LEAVE, SETS, CAPITAL = 0.5, 10, 1000.0
CARD = (2, 30)                     # การ์ดของเล่ม 1 (ตั้งไว้ก่อนเห็นข้อมูลชุดนี้)
F_DAYS, V_DAYS = 731, 365
WF_TRAIN, WF_TEST = 365, 121       # walk-forward: ช่วงเลือก 365 วัน · ช่วงทดสอบ 121 วัน × 3 = 363 วันของช่วงตรวจ
WF_SHIFT = 2                       # กล่องพัง: เลื่อนจุดเริ่มทุกหน้าต่างไปสองวัน
MONTH = 30                         # เดือนละ 30 วัน (คิดผลรายเดือนจาก Equity ทุก 30 วัน)
SIM_PHI, SIM_SCALE, SIM_COMMON = 0.97, 3.0, 0.015   # คู่จำลอง: เชือก φ 0.97 (แบบบท 7) · SD นิ่งของ X = 3 · แรงร่วม 1.5% ต่อวัน

# ตอน ก · ตัวเลขสอน: กำไรของสามเส้นในห้าช่วงติดกัน (ช่วงละราวสองเดือน)
HAND = {1: [30, 10, -20, 5, -10], 2: [10, 15, 10, 5, 10], 3: [-5, 25, 5, -10, 15]}
HAND_TRAIN = 2


def _r(v, n=2):
    v = round(float(v) + 0.0, n)
    return int(v) if v == int(v) else v


def _key(L, H):
    return f"{str(L).replace('.', '_')}x{H}"


# ───────────────────────── ตอน ก: มือ ─────────────────────────

def _hand_wf(table, train, n=5):
    """เดินหน้าด้วยมือ: เลือกเส้นที่รวมสูงสุดในช่วงเลือก แล้วดูผลช่วงถัดไป (ช่วงทดสอบยาว 1)"""
    wins = []
    for (a, b), (c, d) in S.walk_forward(n, train, 1):
        sums = {L: sum(v[a:b]) for L, v in table.items()}
        best = max(sums, key=sums.get)
        assert list(sums.values()).count(sums[best]) == 1, "เสมอในช่วงเลือก"
        oos = table[best][c]
        wins.append({"ช่วงเลือก": f"{a + 1}–{b}" if b - a > 1 else f"{a + 1}", "ช่วงทดสอบ": c + 1,
                     "รวม": {str(L): s for L, s in sums.items()}, "เลือก": best,
                     "เฉลี่ยในช่วงเลือก": _r(sums[best] / (b - a)), "ผลทดสอบ": oos,
                     "หาย": _r(sums[best] / (b - a) - oos)})
    total = sum(w["ผลทดสอบ"] for w in wins)
    promise = sum(sums_avg for sums_avg in (w["เฉลี่ยในช่วงเลือก"] for w in wins))
    cum, run = [], 0
    for w in wins:
        run += w["ผลทดสอบ"]
        cum.append(run)
    return {"หน้าต่าง": wins, "รวม": total, "สัญญา": _r(promise), "หาย": _r(promise - total),
            "หายรวมทีละหน้าต่าง": _r(sum(w["หาย"] for w in wins)), "สะสม": cum, "จำนวนหน้าต่าง": len(wins)}


def _hand(q):
    base = _hand_wf(HAND, HAND_TRAIN)
    whole = {str(L): sum(v) for L, v in HAND.items()}
    tests = [w["ช่วงทดสอบ"] - 1 for w in base["หน้าต่าง"]]
    always = {str(L): sum(v[t] for t in tests) for L, v in HAND.items()}
    # ✍️ ข้อ 2: เส้น 3 ช่วงที่ 4 เป็น +20 แทน −10 · ข้อ 3: ช่วงเลือกยาวสามช่วง
    t2 = {L: list(v) for L, v in HAND.items()}
    t2[3][3] = 20
    ex2 = _hand_wf(t2, HAND_TRAIN)
    ex3 = _hand_wf(HAND, 3)
    first_two = {str(L): v[0] + v[1] for L, v in HAND.items()}
    return {"ตาราง": {str(L): v for L, v in HAND.items()}, "ช่วง": 5, "ช่วงเลือกยาว": HAND_TRAIN,
            "สองช่วงแรก": first_two, "ยอดสองช่วงแรก": max(first_two.values()),
            "ยอดสองช่วงแรกต่อช่วง": _r(max(first_two.values()) / 2),
            "เดินหน้า": base, "ทั้งตาราง": whole, "ยอดทั้งตาราง": max(whole.values()),
            "ทุกช่วงทดสอบตามเส้น": always,
            "แบบฝึก": {"ข้อ2": ex2, "ข้อ3": ex3,
                       "ข้อ3ต่อหน้าต่าง": _r(ex3["รวม"] / ex3["จำนวนหน้าต่าง"]),
                       "เดิมต่อหน้าต่าง": _r(base["รวม"] / base["จำนวนหน้าต่าง"])}}


# ───────────────────────── ตอน ข: นับครั้งที่ลอง ─────────────────────────

def _coin_best(N):
    """ผลดีสุดที่คาดได้ของ N แบบที่ไม่มีฝีมือ แต่ละแบบได้ +1 หรือ −1 เท่า ๆ กัน: แพ้หมด (½)^N ได้ −1 นอกนั้น +1"""
    return 1 - 2 * 0.5 ** N


def _normal_best(N, a=-10.0, b=10.0, steps=20000):
    """ผลดีสุดที่คาดได้ของ N ค่าจากการแจกแจงปกติมาตรฐานที่อิสระกัน = ∫ x · N·pdf(x)·CDF(x)^(N−1) dx (อินทิเกรตเชิงตัวเลข)"""
    w = (b - a) / steps
    tot = 0.0
    for i in range(steps + 1):
        x = a + i * w
        pdf = math.exp(-x * x / 2) / math.sqrt(2 * math.pi)
        f = x * N * pdf * S.norm_cdf(x) ** (N - 1)
        tot += f * (0.5 if i in (0, steps) else 1.0)
    return tot * w


def _hurdle(N, months):
    root = math.sqrt(months)
    best = _r(_normal_best(N))
    return {"N": N, "เดือน": months, "ราก": _r(root), "SE": _r(1 / root), "ดีสุดจากโชค": best,
            "เส้น": _r(best / _r(root))}            # คิดจากเลขปัดที่หน้าแสดง (1.97 ÷ 4.9)


def _count(data):
    """จำนวนครั้งที่แต่ละบทจดว่าเปิดช่วงตรวจ (ตามที่เขียนในหน้าและคัมภีร์เรื่อง) · ดึงจากคีย์ของบทนั้นเมื่อมี แล้วตรวจกับที่คัดลอก"""
    def get(path, fallback):
        o = data
        for k in path.split("."):
            if not isinstance(o, dict) or k not in o:
                return fallback
            o = o[k]
        assert o == fallback, f"{path} = {o} ไม่ตรงกับที่คัดลอก {fallback}"
        return o
    rows = [  # (บท, ครั้งที่เปิดช่วงตรวจ, สิ่งที่ดู)
        (2, 1, "log แก้ Z-score ของช่วงตรวจไหม"),                              # หน้า 2 · คัมภีร์ part2 (ไม่มีคีย์)
        (3, 1, "45 คู่ตรึง h จากช่วงเลือก"),                                   # หน้า 3 (ไม่มีคีย์)
        (4, 1, "Half-life และ μ ของคู่ที่เหลือ"),                              # หน้า 4 (ไม่มีคีย์)
        (5, get("ch05.ดูช่วงตรวจ", 6), "หน้าต่าง 60/120 วัน กับไม้บรรทัดตรึง สองคู่"),
        (6, 1, "Kalman เทียบหน้าต่าง"),                                        # คัมภีร์ part6 "เปิดช่วงตรวจเพิ่ม 1"
        (7, get("ch07.นับ.เปิดช่วงตรวจบทนี้", 1), "เส้นเข้า 5 เส้นพร้อมกัน"),
        (8, get("ch08.จริง.ดูช่วงตรวจ", 3), "ตัวกรอง 8 ตัวบน 45 คู่"),
        (9, get("ch09.ดูช่วงตรวจ", 4), "β ใหม่ · การ์ดสองทิศ"),
        (10, get("ch10.จริง.ดูช่วงตรวจ", 2), "PCA ทั้งช่วงและหน้าต่าง 90 วัน"),
        (11, get("ch11.ดูช่วงตรวจ", 2), "ตะกร้ากับคู่ · บันไดตัดขา"),
        (12, get("ch12.จริง.ดูช่วงตรวจ", 1), "ตารางน้ำหนักทุกแถว"),
        (13, get("ch13.v2.นับรอบ.ครั้งที่ดูช่วงตรวจ", 6), "สี่แบบของเครื่อง + สองแบบในกล่องพัง"),
    ]
    total = sum(r[1] for r in rows)
    ch5_7 = sum(r[1] for r in rows if r[0] <= 7)
    # ตัวนับสะสมในคัมภีร์ (close.ดูช่วงตรวจรวมเล่ม) ต้องเท่ากับผลรวมทีละบทพอดี — ไม่ใช่ขั้นต่ำ
    story = data.get("เรื่อง", {})
    run = 0
    for b, n, _ in rows:
        run += n
        got = (story.get(f"part{b}", {}).get("close") or {}).get("ดูช่วงตรวจรวมเล่ม")
        assert got in (None, run), f"คัมภีร์ part{b}.close.ดูช่วงตรวจรวมเล่ม = {got} ≠ ผลรวมทีละบท {run}"
    return {"บท": [{"บท": b, "ครั้ง": n, "ดู": t} for b, n, t in rows], "รวม": total,
            "รวมบท2ถึง7": ch5_7, "ตัวนับบท7": get("ch07.นับ.ดูช่วงตรวจรวม", 11),
            "ตัวนับบท13": get("ch13.v2.นับรอบ.รวมเล่ม", 29),
            "วิธีหาh": get("ch02.จำนวนวิธีรวม", 7), "คู่บท3": get("ch03.จริง.สี่สิบห้า.คู่", 45),
            "โชคบท3": get("ch03.จริง.สี่สิบห้า.คาดจากโชค", 2.25),
            "สองทิศบท8": get("ch08.แปดคู่.ทดสอบสองทิศ", 90), "ตะกร้าบท11": get("ch11.สแกน.ทดสอบไม่มีLTC", 252),
            "โชคตะกร้าบท11": get("ch11.สแกน.โชคไม่มีLTC", 12.6), "โลกศูนย์ตะกร้าบท11": get("ch11.โลกศูนย์.มัธยฐาน", 7.5),
            "บท5หน้าต่าง60": get("ch05.จริง.BTC-ETH.60.ผล", -126.04),
            "บท5หน้าต่าง120": get("ch05.จริง.BTC-ETH.120.ผล", -396.29),
            "บท5ตรึง": get("ch05.จริง.BTC-ETH.ตรึง.ผล", -55.53),
            "บท5LTCหน้าต่าง60": get("ch05.จริง.LTC-DOT.60.ผล", 619.2),
            "บท7Zตรวจเฉลี่ย": get("ch07.จริง.LTC-DOT.Zตรวจเฉลี่ย", 2.86),
            "ทดสอบช่วงเลือกรวม": 45 + 90 + 252}


# ───────────────────────── ตอน ค: ตาราง 5 × 5 และ walk-forward ─────────────────────────

def _monthly(eq, cap=CAPITAL):
    """ผลรายเดือน (เดือนละ 30 วัน) จาก Equity · Sharpe รายเดือน = Mean ÷ SD (ตัวหาร n − 1)"""
    pts = [cap] + [eq[t] for t in range(MONTH - 1, len(eq), MONTH)]
    d = [b - a for a, b in zip(pts, pts[1:])]
    sd = S.sd(d)
    return {"เดือน": len(d), "Mean": S.mean(d), "SD": sd, "Sharpe": S.mean(d) / sd if sd else 0.0}


def _ranks(vals):
    order = sorted(range(len(vals)), key=lambda i: -vals[i])
    r = [0] * len(vals)
    for k, i in enumerate(order):
        r[i] = k + 1
    return r


def _ruler(A, B, h):
    X = [a - h * b for a, b in zip(A, B)]
    return S.mean(X), S.sd(X)


def _grid(A, B, h, z, sets=SETS):
    return {(L, H): E.run(A, B, h, z, sets, enter=L, leave=LEAVE, hold=H) for L in ENTRIES for H in HOLDS}


def _fixed(fa, fb, va, vb, nd=2):
    """ตารางเต็มบนช่วงเลือก (ไม้บรรทัดจากช่วงเลือกเอง = ในช่วงที่ใช้เลือก) แล้วเดินแบบเดียวกันในช่วงตรวจ"""
    h = round(S.ols(fb, fa)["slope"], nd)
    m, s = _ruler(fa, fb, h)
    zf = [(a - h * b - m) / s for a, b in zip(fa, fb)]
    zv = [(a - h * b - m) / s for a, b in zip(va, vb)]
    gf, gv = _grid(fa, fb, h, zf), _grid(va, vb, h, zv)
    keys = list(gf)
    F = [gf[k]["net"] for k in keys]
    V = [gv[k]["net"] for k in keys]
    peak = keys[F.index(max(F))]
    rv = _ranks(V)
    return {"h": h, "m": m, "s": s, "gf": gf, "gv": gv, "keys": keys, "F": F, "V": V, "peak": peak,
            "rank_v": rv[keys.index(peak)], "spearman": S.corr(_ranks(F), rv),
            "sr_f": _monthly(gf[peak]["equity"]), "sr_v": _monthly(gv[peak]["equity"])}


def _wf(A, B, dates=None, train=WF_TRAIN, test=WF_TEST, nd=2):
    """Walk-forward: ทุกหน้าต่างวัด h · ไม้บรรทัด · และเลือกแบบที่ดีสุดจาก 25 แบบ ด้วยช่วงเลือกของหน้าต่างเท่านั้น
    แล้วเดินแบบนั้นในช่วงทดสอบถัดไป (เริ่มว่าง · ไม้ที่ค้างตอนจบหน้าต่างคิดตามราคาปิดวันสุดท้าย)"""
    out = []
    for (a, b), (c, d) in S.walk_forward(len(A), train, test):
        h = round(S.ols(B[a:b], A[a:b])["slope"], nd)
        m, s = _ruler(A[a:b], B[a:b], h)
        z = [(p - h * x - m) / s for p, x in zip(A, B)]
        g = {k: r["net"] for k, r in _grid(A[a:b], B[a:b], h, z[a:b]).items()}
        best = max(g, key=g.get)
        r = E.run(A[c:d], B[c:d], h, z[c:d], SETS, enter=best[0], leave=LEAVE, hold=best[1])
        row = {"h": h, "Mean": _r(m), "SD": _r(s), "เส้น": best[0], "ถือ": best[1], "ในช่วงเลือก": _r(g[best]),
               "ในช่วงเลือกต่อ121วัน": _r(g[best] * test / train), "ผล": _r(r["net"]), "ไม้": r["trades"],
               "ชนะ": r["wins"], "ค้าง": abs(r["open"]), "ค่าธรรมเนียม": _r(r["costs"]),
               "Zเฉลี่ย": _r(S.mean(z[c:d]))}
        if dates:
            row.update({"เลือกเริ่ม": dates[a], "เลือกจบ": dates[b - 1], "ทดสอบเริ่ม": dates[c], "ทดสอบจบ": dates[d - 1]})
        out.append(row)
    return out


def _real(q, data, looks_before):
    df, pf = R.load_closes("formation", coins=["LTC", "DOT"])
    dv, pv = R.load_closes("validation", coins=["LTC", "DOT"])
    fa, fb, va, vb = pf["LTC"], pf["DOT"], pv["LTC"], pv["DOT"]
    fx = _fixed(fa, fb, va, vb)
    # ต้องตรงบท 7: คอลัมน์ถือ 30 วัน = แถวเส้นเข้าของบท 7
    ch7 = data.get("ch07", {}).get("จริง", {}).get("LTC-DOT", {}).get("แถว", {})
    for L in ENTRIES:
        row = ch7.get(str(L).replace(".", "_"))
        if row:
            assert _r(fx["gf"][(L, 30)]["net"]) == row["เลือก"]["ผล"], "ช่วงเลือกไม่ตรงบท 7"
            assert _r(fx["gv"][(L, 30)]["net"]) == row["ตรวจ"]["ผล"], "ช่วงตรวจไม่ตรงบท 7"
    zf = [(a - fx["h"] * b - fx["m"]) / fx["s"] for a, b in zip(fa, fb)]
    first25 = next(v for v in zf if abs(v) >= 2.5)          # ครั้งแรกที่ |Z| ถึง 2.5 ในช่วงเลือก (กระโดดเกิน 3 วันเดียวกัน)
    cells = {}
    for k in fx["keys"]:
        cells[_key(*k)] = {"เส้น": k[0], "ถือ": k[1], "เลือก": _r(fx["gf"][k]["net"]), "ตรวจ": _r(fx["gv"][k]["net"]),
                           "ไม้เลือก": fx["gf"][k]["trades"], "ไม้ตรวจ": fx["gv"][k]["trades"]}
    keys, F, V = fx["keys"], fx["F"], fx["V"]
    peak = fx["peak"]
    vbest = keys[V.index(max(V))]
    sr_vbest = _monthly(fx["gv"][vbest]["equity"])
    card = fx["gv"][CARD]
    # walk-forward ในช่วงตรวจ: ข้อมูลเริ่ม 365 วันก่อนวันแรกของช่วงตรวจ
    A, B, D = fa + va, fb + vb, df + dv
    s0 = F_DAYS - WF_TRAIN
    wf = _wf(A[s0:], B[s0:], D[s0:])
    wf_shift = _wf(A[s0 + WF_SHIFT:], B[s0 + WF_SHIFT:], D[s0 + WF_SHIFT:])
    hf = _hurdle(len(keys), fx["sr_f"]["เดือน"])
    hv = _hurdle(len(keys), fx["sr_v"]["เดือน"])
    sr_f = _r(fx["sr_f"]["Sharpe"])
    return {
        "ช่วงเลือก": {"เริ่ม": df[0], "จบ": df[-1], "วัน": len(df)},
        "ช่วงตรวจ": {"เริ่ม": dv[0], "จบ": dv[-1], "วัน": len(dv)},
        "h": fx["h"], "Mean": _r(fx["m"]), "SD": _r(fx["s"]), "ชุด": SETS, "แบบ": len(keys),
        "DOTต่อชุดรวม": _r(SETS * fx["h"]),
        "Zแรกที่ถึง2_5เลือก": _r(first25, 1), "ไม้เลือกเส้น2_5": fx["gf"][(2.5, 30)]["trades"],
        "ช่อง": cells,
        "ยอด": {"เส้น": peak[0], "ถือ": peak[1], "เลือก": _r(max(F)), "ตรวจ": _r(fx["gv"][peak]["net"]),
                "อันดับตรวจ": fx["rank_v"], "Sharpeเลือก": sr_f, "เดือนเลือก": fx["sr_f"]["เดือน"],
                "Meanเดือนเลือก": _r(fx["sr_f"]["Mean"]), "SDเดือนเลือก": _r(fx["sr_f"]["SD"]),
                "Sharpeตรวจ": _r(fx["sr_v"]["Sharpe"]), "tเลือก": _r(sr_f * hf["ราก"]),
                "ไม้เลือก": fx["gf"][peak]["trades"], "ไม้ตรวจ": fx["gv"][peak]["trades"]},
        "ยอดตรวจ": {"เส้น": vbest[0], "ถือ": vbest[1], "ตรวจ": _r(max(V)), "เลือก": _r(fx["gf"][vbest]["net"]),
                    "อันดับเลือก": _ranks(F)[keys.index(vbest)], "Sharpeตรวจ": _r(sr_vbest["Sharpe"]),
                    "เดือน": sr_vbest["เดือน"]},
        "การ์ด": {"เส้น": CARD[0], "ถือ": CARD[1], "เลือก": _r(fx["gf"][CARD]["net"]), "ตรวจ": _r(card["net"]),
                  "อันดับเลือก": _ranks(F)[keys.index(CARD)], "อันดับตรวจ": _ranks(V)[keys.index(CARD)]},
        "ตรวจมัธยฐาน": _r(statistics.median(V)), "ตรวจบวก": sum(1 for v in V if v > 0),
        "ตรวจต่ำสุด": _r(min(V)), "เลือกมัธยฐาน": _r(statistics.median(F)), "เลือกบวก": sum(1 for v in F if v > 0),
        "อันดับสัมพันธ์": _r(fx["spearman"]),
        "เส้นโชคเลือก": hf, "เส้นโชคตรวจ": hv, "เส้นโชคตรวจเล่ม": _hurdle(looks_before, fx["sr_v"]["เดือน"]),
        "เดินหน้า": {"หน้าต่าง": wf, "รวม": _r(sum(w["ผล"] for w in wf)),
                     "สัญญารวม": _r(sum(w["ในช่วงเลือกต่อ121วัน"] for w in wf)),
                     "ไม้รวม": sum(w["ไม้"] for w in wf), "วันทดสอบ": WF_TEST * len(wf),
                     "วันทิ้ง": len(dv) - WF_TEST * len(wf),
                     "หาย": _r(sum(w["ในช่วงเลือกต่อ121วัน"] for w in wf) - sum(w["ผล"] for w in wf)),
                     "หายทีละหน้าต่าง": [_r(w["ในช่วงเลือกต่อ121วัน"] - w["ผล"]) for w in wf],
                     "เลื่อนวัน": WF_SHIFT, "เลื่อนรวม": _r(sum(w["ผล"] for w in wf_shift)),
                     "เลื่อนหน้าต่าง": [{"เส้น": w["เส้น"], "ถือ": w["ถือ"], "ผล": w["ผล"]} for w in wf_shift]},
        "แกนกราฟ": {"x": [0, 500, 1000, 1500], "y": [-400, 0, 400, 800]},
    }


def _sim():
    """โลกคู่กัน 30 โลกต่อแบบ (seed 1–30 · 1,096 วัน = ช่วงเลือก + ช่วงตรวจ): มีเชือก φ 0.97 · ไม่มีเชือก φ 1 (ระยะห่างเดินสุ่ม)
    ตารางคงที่ (ยอดเขาช่วงเลือกไปอันดับไหนในช่วงตรวจ · ผ่านเส้นโชคไหม) และ walk-forward สามหน้าต่างแบบข้อมูลจริง"""
    sd = SIM_SCALE * math.sqrt(1 - SIM_PHI ** 2)
    hurdle = _hurdle(len(ENTRIES) * len(HOLDS), F_DAYS // MONTH)["เส้น"]
    t3 = _r(3 / _r(math.sqrt(F_DAYS // MONTH)))
    out = {}
    for name, phi in (("มีเชือก", SIM_PHI), ("ไม่มีเชือก", 1.0)):
        rk, sp, srf, vv, wf, wfin, top5, passed, passed3 = [], [], [], [], [], [], 0, 0, 0
        for seed in M.ROBUST_SEEDS:
            w = M.price_pair(seed=seed, n=F_DAYS + V_DAYS, h=2, phi=phi, sd=sd, common_sd=SIM_COMMON)
            A, B = w["A"], w["B"]
            assert min(A) > 0
            fx = _fixed(A[:F_DAYS], B[:F_DAYS], A[F_DAYS:], B[F_DAYS:], nd=4)
            rk.append(fx["rank_v"])
            top5 += fx["rank_v"] <= 5
            sp.append(fx["spearman"])
            s = fx["sr_f"]["Sharpe"]
            srf.append(s)
            passed += _r(s) > hurdle
            passed3 += _r(s) > t3
            vv.append(fx["gv"][fx["peak"]]["net"])
            s0 = F_DAYS - WF_TRAIN
            rows = _wf(A[s0:], B[s0:], nd=4)
            wf.append(sum(r["ผล"] for r in rows))
            wfin.append(sum(r["ในช่วงเลือกต่อ121วัน"] for r in rows))
        n = len(M.ROBUST_SEEDS)
        out[name] = {"phi": phi, "โลก": n, "อันดับมัธยฐาน": _r(statistics.median(rk), 1), "ติดห้าอันดับ": top5,
                     "อันดับสัมพันธ์มัธยฐาน": _r(statistics.median(sp)),
                     "Sharpeยอดมัธยฐาน": _r(statistics.median(srf)), "ผ่านเส้นโชค": passed, "ผ่านt3": passed3,
                     "ยอดในช่วงตรวจมัธยฐาน": _r(statistics.median(vv)), "ยอดในช่วงตรวจบวก": sum(1 for x in vv if x > 0),
                     "เดินหน้ามัธยฐาน": _r(statistics.median(wf)), "เดินหน้าบวก": sum(1 for x in wf if x > 0),
                     "เดินหน้าต่ำสุด": _r(min(wf)), "เดินหน้าสูงสุด": _r(max(wf)),
                     "สัญญามัธยฐาน": _r(statistics.median(wfin))}
    out["SDนิ่ง"] = _r(SIM_SCALE)
    out["ครึ่งชีวิต"] = _r(S.half_life(SIM_PHI), 1)
    out["เส้นโชค"] = hurdle
    out["เส้นt3"] = t3
    return out


def extend(data, D, q):
    hand = _hand(q)
    coin = {"สองแบบ": {"ผลลัพธ์": [[1, 1, 1], [1, -1, 1], [-1, 1, 1], [-1, -1, -1]], "คาด": _r(_coin_best(2))},
            "คาด": {str(N): _r(_coin_best(N)) for N in (1, 2, 3, 5, 10)}}
    count = _count(data)
    normal = {str(N): _r(_normal_best(N)) for N in sorted({1, 2, 5, 10, 25, count["รวม"], 100, 252})}
    v1 = SB.load_figures("sab")["ch10"]["ลองหลายครั้ง"]
    vol1 = {"ลองหลายครั้ง": {k: v1[k] for k in ("1", "10", "20", "50", "100")}}
    real = _real(q, data, count["รวม"])
    sim = _sim()
    small = _hurdle(5, 16)                    # ตัวอย่างมือ: 5 แบบ × 16 เดือน
    looks = {   # การดูช่วงตรวจของบทนี้ (ตาราง 25 แบบรันรอบเดียว = หนึ่งครั้ง) ต่อจากตัวนับสะสมบท 2–13
        "ครั้ง": 3, "รายการ": ["ตาราง 25 แบบทั้งช่วงตรวจ (ครั้งเดียว 25 ผล)", "walk-forward สามหน้าต่าง",
                               "walk-forward เลื่อนสองวัน (กล่องพัง)"],
        "ผลที่เห็น": 25 + 1 + 1, "รวมเล่มหลังบทนี้": count["รวม"] + 3}
    mine = (data.get("เรื่อง", {}).get("part14", {}).get("close") or {}).get("ดูช่วงตรวจรวมเล่ม")
    assert mine in (None, looks["รวมเล่มหลังบทนี้"]), f"คัมภีร์ part14.close.ดูช่วงตรวจรวมเล่ม = {mine}"
    prac = {   # กล่อง 🧰 · ที่มา tools/sab_research/practitioner-research.md §3.2 · §3.3 · §5 · §7 (ตัวเลขตามที่บันทึก ไม่ได้คำนวณ)
        "ปีKrauss": "2015", "คู่Krauss": 1225, "ปลอมKrauss": 61, "ปีDoFaff": "2012", "แบบDoFaff": 29,
        "ปีHLZ": "2016", "tHLZ": 3, "ปีBLdP": "2014", "ปีSarmento": "2019", "สินทรัพย์Sarmento": 20,
        "คู่Sarmento": 190, "ผิดSarmento": 9, "ปีFil": "2020", "ปีGGR": "2006", "ปีAL": "2010", "วันAL": 60,
        "ปีCK": "2018", "ปีบรรยายQuantopian": "2020"}
    drills = [
        {"โจทย์": "(ทำตาม) หน้าต่างที่ 2 ของตารางมือ: รวมสามเส้นในช่วง 2–3 · เลือกเส้นไหน · ผลช่วง 4 · รวมทั้งสามหน้าต่าง",
         "คำตอบ": hand["เดินหน้า"]["รวม"]},
        {"โจทย์": "(เปลี่ยนเลข) เส้น 3 ช่วง 4 เป็น +20 แทน −10 — ผล walk-forward รวม และส่วนที่หาย",
         "คำตอบ": hand["แบบฝึก"]["ข้อ2"]["รวม"]},
        {"โจทย์": "(เปลี่ยนเงื่อนไข) ช่วงเลือกยาวสามช่วง — มีกี่หน้าต่าง เลือกเส้นไหน ได้ต่อหน้าต่างเท่าไร",
         "คำตอบ": hand["แบบฝึก"]["ข้อ3"]["รวม"]},
        {"โจทย์": "(ตัดสินใจ · ข้อมูลจริง) ต้นบอกว่ายอดเขา t 3.43 ผ่านเส้น 3 และผ่านเส้นโชค 0.4 จึงลงเงิน — เห็นด้วยไหม",
         "คำตอบ": real["ยอด"]["อันดับตรวจ"]},
        {"โจทย์": "(ถ่ายโอน) เพื่อนลอง 100 แบบบนหุ้น 36 เดือน Sharpe รายเดือน 0.45 — ผ่านเส้นโชคไหม",
         "คำตอบ": _hurdle(100, 36)["เส้น"]},
    ]
    extra = {"ร้อยแบบ24เดือน": _hurdle(100, 24), "ยี่สิบห้าแบบ36เดือน": _hurdle(25, 36)}
    friend = _hurdle(100, 36)
    friend["Sharpe"] = 0.45
    friend["t"] = _r(0.45 * friend["ราก"])
    return {"_แบบฝึก": drills, "มือ": hand, "เหรียญ": coin, "ปกติ": normal, "เส้นโชคตัวอย่าง": small,
            "เล่ม1": vol1, "นับ": count, "จริง": real, "จำลอง": sim, "ดูช่วงตรวจบทนี้": looks,
            "เพื่อน": friend, "เส้นโชคอื่น": extra, "คนทำงานจริง": prac, "แกนกราฟโลก": [-200, 0, 200, 400, 600], "แกนเส้นโชค": [-0.5, 0, 0.5, 1],
            "ค่า": {"เส้นเข้า": list(ENTRIES), "ถือ": list(HOLDS), "เส้นออก": LEAVE, "ชุด": SETS, "ทุน": int(CAPITAL),
                    "เดือนวัน": MONTH, "ช่วงเลือกวัน": WF_TRAIN, "ช่วงทดสอบวัน": WF_TEST,
                    "ค่าธรรมเนียมเปอร์เซ็นต์": 0.05}}
