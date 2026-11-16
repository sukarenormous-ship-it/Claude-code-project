"""บท 16 เล่ม 2 — รวมหลายสัญญาณ และโมเดลที่เรียนรู้เอง · ค่าทุกตัวของบท (ปลั๊กอินของ tools/sab_figures.py --book sab2)

ตอน ก  แปดวันด้วยมือ: สามสัญญาณ (Z-score · funding · ส่วนที่เหลือ) → คะแนน → Information Coefficient (Rank Correlation
       ของบท 8) สองทาง → รวมคะแนน → จากคะแนนเป็นผลที่คาด (ความชัน 0.5 · ก้นชามของบท 1) เทียบต้นทุนไปกลับ
ตอน ข  Baseline · ต้นไม้หนึ่งชั้นด้วยมือ (ลองทุกจุดตัด) · คอลัมน์สุ่ม 70 แบบ (นับตรง) · Label Leakage (ป้ายคำตอบรู้ได้วันไหน)
ตอน ค  โลกจำลองที่รู้คำตอบ (สองสัญญาณจริง + สำเนา + ตัวแปรสุ่ม 17 ตัว · 30 โลก) · ข้อมูลจริง ETH–BTC
       ช่วงเลือก → ช่วงตรวจ (ไม่แตะช่วงทดสอบสุดท้าย) · backtest หลังต้นทุนด้วย sab2_engine.run_hpath

ชุดที่เทรด: long ETH คู่ short BTC มูลค่าเท่ากัน ณ วันเข้า (h = ราคา ETH ÷ ราคา BTC ของวันสัญญาณ · ไม่ปรับระหว่างถือ)
ป้ายคำตอบ y ของวัน t = 100 × (LN(ETH/BTC) วัน t+5 − วัน t) = ผลของชุดใน 5 วันข้างหน้า เป็น % ของขาหนึ่ง
ข้อมูลจริงผ่าน sab2_realdata.load_closes/load_funding เท่านั้น · สถิติผ่าน sab2_stats · backtest ผ่าน sab2_engine ·
โลกจำลองผ่าน sab2_sim.reseed (seed 1–30) กับ random.Random(seed) แบบบท 12
"""

import math
import random
import statistics

import sab_book as SB
import sab2_engine as E
import sab2_realdata as R
import sab2_sim as M
import sab2_stats as S

H = 5              # ป้ายคำตอบ: ผล 5 วันข้างหน้า
WIN_Z = 60         # ไม้บรรทัดเลื่อน 60 วัน (บท 5)
WIN_R = 20         # ส่วนที่เหลือ 20 วัน (บท 9)
WIN_F = 7          # funding เฉลี่ย 7 วัน (21 รอบ)
FEE = 0.0005       # 0.05% ต่อ fill ต่อขา (ฐานเล่ม 1)
COST = 4 * FEE * 100   # ไปกลับของชุดสองขามูลค่าเท่ากัน = 0.2% ของขาหนึ่ง
SETS_REAL = 0.16   # ETH 0.16 เหรียญ (ขา ETH ราว 500 ณ ต้นช่วงตรวจ)
CAPITAL = 1000.0
KEYS = ("z", "f", "r")
SEEDS = list(range(1, 31))

# ───────────────────────── ตัวช่วย ─────────────────────────


def _ranks(v):
    """อันดับ 1..n (ค่าซ้ำได้อันดับเฉลี่ย)"""
    o = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(o):
        j = i
        while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]:
            j += 1
        for k in range(i, j + 1):
            r[o[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def ic(a, b):
    """Information Coefficient = Rank Correlation (บท 8) ระหว่างคะแนนวันนี้กับผลที่ตามมา"""
    return S.corr(_ranks(a), _ranks(b))


def _best_stump(cols, y):
    """ต้นไม้หนึ่งชั้น: ลองทุกจุดตัดของทุกตัวแปร ทั้งสองทิศ · คืน (จำนวนทายถูก, ตัวแปร, จุดตัด, ทิศ, จำนวนจุดตัดที่ลอง)
    ทิศ +1 = ทายขึ้นเมื่อค่า > จุดตัด"""
    n = len(y)
    up = [1 if v > 0 else 0 for v in y]
    best, tries = None, 0
    for j, col in enumerate(cols):
        order = sorted(range(n), key=lambda i: col[i])
        tot_up = sum(up)
        below_up = 0
        for pos in range(n - 1):
            below_up += up[order[pos]]
            a, b = col[order[pos]], col[order[pos + 1]]
            if a == b:
                continue
            tries += 1
            k = pos + 1                                   # จำนวนแถวที่ ≤ จุดตัด (ทายลง)
            correct = (k - below_up) + (tot_up - below_up)
            for dirn, c in ((1, correct), (-1, n - correct)):
                if best is None or c > best[0]:
                    best = (c, j, (a + b) / 2, dirn)
    return best + (tries,)


def _stump_acc(col, y, cut, dirn):
    return sum(1 for x, v in zip(col, y) if ((x > cut) == (v > 0)) == (dirn == 1)) / len(y)


def _r2_out(y, pred):
    m = S.mean(y)
    return 1 - sum((a - b) ** 2 for a, b in zip(y, pred)) / sum((a - m) ** 2 for a in y)


def _pair_bt(A, B, pred, sets, lo, hi, cost=COST):
    """backtest หลังต้นทุนของ 'ผลที่คาด' · เข้าเมื่อ |ผลที่คาด| > ต้นทุนไปกลับ ทางเดียวกับผลที่คาด · ถือ 5 วันแล้วปิด
    sab2_engine.run_hpath: h = A ÷ B ของวันสัญญาณ (มูลค่าเท่ากัน) · ไม่ปรับระหว่างถือ · fill ราคาปิดวันถัดไป"""
    hs = [a / b for a, b in zip(A[lo:hi], B[lo:hi])]
    sig = [None if p is None else -p for p in pred[lo:hi]]    # กฎเส้นของเครื่องสวนทิศสัญญาณ → ส่ง −ผลที่คาด
    return E.run_hpath(A[lo:hi], B[lo:hi], hs, sig, sets=sets, capital=CAPITAL, fee=FEE, enter=cost, leave=-1.0,
                       hold=H, rebalance=False)


def _bt_summary(r, q):
    return {"ผล": q(r["net"], 2), "ไม้": r["trades"], "ชนะ": r["wins"], "ค่าธรรมเนียม": q(r["costs"], 2),
            "ค้าง": abs(r["open"]), "Equityต่ำสุด": q(r["min_equity"], 2)}


# ───────────────────────── ตอน ก: แปดวันด้วยมือ ─────────────────────────

HAND_Y = [-1.2, 0.8, -2.4, 1.8, -0.4, -1.6, 1.4, 0.2]        # ผล 5 วันข้างหน้า (% ของขาหนึ่ง) วันที่ 1–8
HAND_SZ = [1, 2, -2, 0.5, -0.5, -1.5, -1, 1.5]               # คะแนน Z (= −Z ÷ 1)
HAND_SF = [-0.5, -2, 0.5, 1, -1.5, -1, 2, 1.5]               # คะแนน funding (= −funding ÷ 5)
HAND_SR = [1, 2, -2, -0.5, 0.5, -1.5, -1, 1.5]               # คะแนนส่วนที่เหลือ (= −ส่วนที่เหลือ ÷ 4)
HAND_SD = {"z": 1, "f": 5, "r": 4}


def _rank_block(score, y):
    rs, ry = _ranks(score), _ranks(y)
    d = [a - b for a, b in zip(rs, ry)]
    d2 = sum(x * x for x in d)
    n = len(y)
    cross = sum((a - (n + 1) / 2) * (b - (n + 1) / 2) for a, b in zip(rs, ry))
    sq = sum((a - (n + 1) / 2) ** 2 for a in ry)
    mid = (n + 1) / 2
    return {"อันดับ": [int(x) for x in rs], "ต่าง": [int(x) for x in d], "ต่าง2": [int(x * x) for x in d],
            "อันดับลบกลาง": [a - mid for a in rs], "อันดับผลลบกลาง": [b - mid for b in ry],
            "ผลคูณ": [(a - mid) * (b - mid) for a, b in zip(rs, ry)],
            "รวมต่าง2": int(d2), "หกเท่า": int(6 * d2), "IC": 1 - 6 * d2 / (n * (n * n - 1)),
            "ผลคูณรวม": cross, "รวมกำลังสอง": sq}


def _hand(q):
    y = HAND_Y
    n = len(y)
    ry = _ranks(y)
    raw = {"z": [-s * HAND_SD["z"] for s in HAND_SZ], "f": [-s * HAND_SD["f"] for s in HAND_SF],
           "r": [-s * HAND_SD["r"] for s in HAND_SR]}
    blocks = {"z": _rank_block(HAND_SZ, y), "f": _rank_block(HAND_SF, y), "r": _rank_block(HAND_SR, y)}
    b2 = [a + b for a, b in zip(HAND_SZ, HAND_SF)]
    b3 = [a + b + c for a, b, c in zip(HAND_SZ, HAND_SF, HAND_SR)]
    blocks["รวมสอง"] = _rank_block(b2, y)
    blocks["รวมสาม"] = _rank_block(b3, y)
    zr = sum((a - b) ** 2 for a, b in zip(_ranks(HAND_SZ), _ranks(HAND_SR)))
    # ความชันผ่านจุดกำเนิดของผลบนคะแนนรวมสอง (Mean ของคะแนน = 0 จึงเท่ากับแบบมีค่าตัดแกน)
    sxy = sum(a * b for a, b in zip(b2, y))
    sxx = sum(a * a for a in b2)
    syy = sum(v * v for v in y)
    slope = sxy / sxx
    assert abs(S.mean(b2)) < 1e-12 and abs(S.ols(b2, y)["slope"] - slope) < 1e-12
    sse = {str(b): q(syy - 2 * b * sxy + b * b * sxx, 2) for b in (0.4, 0.5, 0.6)}
    bowl = {str(b): [q((v - b * x) ** 2, 2) for x, v in zip(b2, y)] for b in (0.4, 0.6)}   # 0.5 มีทศนิยมสี่ตำแหน่ง ไม่ลงตาราง
    bowl["พลาด0.4"] = [q(v - 0.4 * x, 2) for x, v in zip(b2, y)]
    bowl["พลาด0.6"] = [q(v - 0.6 * x, 2) for x, v in zip(b2, y)]
    for k in ("0.4", "0.6"):
        lst = bowl[k]
        assert abs(sum(lst) - sse[k]) < 1e-6
    nets = {}
    for s in (0.5, 1, 2, 3):
        e = slope * s
        nets[str(s)] = {"คาด": q(e, 2), "สุทธิ": q(e - COST, 2)}
    trade_days = [i + 1 for i, s in enumerate(b2) if abs(slope * s) > COST]
    days = []
    for i in range(n):
        days.append({"วัน": i + 1, "ผล": y[i], "Z": raw["z"][i], "funding": raw["f"][i], "ส่วนที่เหลือ": raw["r"][i],
                     "คะแนนZ": HAND_SZ[i], "คะแนนfunding": HAND_SF[i], "คะแนนส่วนที่เหลือ": HAND_SR[i],
                     "รวมสอง": b2[i], "รวมสาม": b3[i], "อันดับผล": int(ry[i]),
                     "คาด": q(slope * b2[i], 2), "สุทธิ": q(abs(slope * b2[i]) - COST, 2)})
    for k, bl in blocks.items():
        bl["IC"] = q(bl["IC"], 2)
        bl["ผลคูณรวม"] = q(bl["ผลคูณรวม"], 1)
        bl["รวมกำลังสอง"] = q(bl["รวมกำลังสอง"], 1)
    return {"วัน": days, "SD": HAND_SD, "n": n, "nกำลังสามลบn": n * (n * n - 1), "อันดับกลาง": (n + 1) / 2,
            "บล็อก": blocks, "ZกับRต่าง2": int(zr), "ZกับR": q(1 - 6 * zr / (n * (n * n - 1)), 2),
            "รวมxy": q(sxy, 1), "รวมx2": q(sxx, 0), "รวมy2": q(syy, 1), "ความชัน": q(slope, 2),
            "ผลรวมกำลังสอง": sse, "ชาม": bowl, "xy": [q(a * v, 2) for a, v in zip(b2, y)], "x2": [q(a * a, 2) for a in b2], "สุทธิตามคะแนน": nets, "ต้นทุนไปกลับ": q(COST, 1),
            "คะแนนต้องเกิน": q(COST / slope, 1), "วันที่เทรด": trade_days, "จำนวนวันที่เทรด": len(trade_days),
            "สั่นเอง": q(1 / math.sqrt(n - 1), 2), "รากnลบหนึ่ง": q(math.sqrt(n - 1), 2),
            "อัตราส่วนสุทธิ": q(nets["2"]["สุทธิ"] / nets["1"]["สุทธิ"], 2)}


def _hand_tree(q):
    """ต้นไม้หนึ่งชั้นบนแปดวัน: ทายขึ้น/ลงของผล · ทุกจุดตัดของแต่ละคะแนน · คอลัมน์สุ่มทุกแบบ (70 แบบ) นับตรง"""
    y = HAND_Y
    n = len(y)
    up = [1 if v > 0 else 0 for v in y]
    out = {}
    cols = {"Z": HAND_SZ, "funding": HAND_SF, "ส่วนที่เหลือ": HAND_SR}
    for name, col in cols.items():
        order = sorted(range(n), key=lambda i: col[i])
        rows = []
        for k in range(n + 1):                          # k แถวล่างสุดทายลง ที่เหลือทายขึ้น
            correct = sum(1 for pos, i in enumerate(order) if (pos >= k) == bool(up[i]))
            rows.append(max(correct, n - correct))
        inner = rows[1:n]                              # จุดตัดจริงอยู่ระหว่างค่า (7 จุด)
        cut_rows = []
        for k in range(1, n):
            a, b = col[order[k - 1]], col[order[k]]
            if a != b:
                cut_rows.append({"จุดตัด": (a + b) / 2, "ถูก": rows[k]})
        out[name] = {"เรียง": [{"วัน": i + 1, "ค่า": col[i], "ขึ้น": bool(up[i])} for i in order],
                     "จุดตัด": cut_rows, "ดีสุด": max(inner), "จำนวนจุดตัด": len(cut_rows)}
    # คอลัมน์ที่ไม่เกี่ยวกับผลเลย: ทุกวิธีวาง ขึ้น 4 ลง 4 ในแปดอันดับ = 70 แบบ เท่ากันทุกแบบ
    import itertools
    dist = {}
    for pos in itertools.combinations(range(n), sum(up)):
        lab = [1 if i in pos else 0 for i in range(n)]
        best = 0
        for k in range(1, n):
            c = sum(1 for i in range(n) if (i >= k) == bool(lab[i]))
            best = max(best, c, n - c)
        dist[best] = dist.get(best, 0) + 1
    total = sum(dist.values())
    ge7 = dist.get(7, 0) + dist.get(8, 0)
    p7 = ge7 / total
    tries = sum(out[k]["จำนวนจุดตัด"] for k in ("Z", "funding", "ส่วนที่เหลือ"))
    out["สุ่มทุกแบบ"] = {"แบบ": total, "ดีสุด8": dist.get(8, 0), "ดีสุด7": dist.get(7, 0), "ดีสุด6": dist.get(6, 0),
                       "ดีสุด5": dist.get(5, 0), "อย่างน้อย7": ge7, "โอกาสอย่างน้อย7เปอร์เซ็นต์": q(p7 * 100, 0),
                       "ไม่ถึง7": total - ge7,
                       "สามคอลัมน์อย่างน้อยหนึ่งเปอร์เซ็นต์": q((1 - (1 - p7) ** 3) * 100, 0)}
    out["จุดตัดที่ลองสามตัวแปร"] = tries
    out["กฎที่ลองสองทิศ"] = 2 * tries
    out["ขึ้น"] = sum(up)
    out["ทายถูกเปอร์เซ็นต์ดีสุด"] = q(out["funding"]["ดีสุด"] / n * 100, 1)
    return out


# ───────────────────────── ข้อมูลจริง ETH–BTC ─────────────────────────

def _real_inputs():
    d1, p1 = R.load_closes("formation")
    d2, p2 = R.load_closes("validation")
    dates = d1 + d2
    px = {c: p1[c] + p2[c] for c in p1}
    nf = len(d1)
    fund = {}
    for split in ("formation", "validation"):
        for inst in ("BTC-PERPETUAL", "ETH-PERPETUAL"):
            for ts, _, rate in R.load_funding(split, instrument=inst):
                fund.setdefault(ts[:10], {}).setdefault(inst, []).append(rate)
    return dates, px, nf, fund


def _real_rows(dates, px, nf, fund):
    """คุณลักษณะที่รู้ได้ ณ ปิดวัน t (ใช้ข้อมูลถึงวัน t เท่านั้น) + ป้ายคำตอบ y (ผล 5 วันข้างหน้า ไม่ข้ามช่วง)"""
    n = len(dates)
    L = [math.log(e / b) for e, b in zip(px["ETH"], px["BTC"])]
    coins = list(px)
    lr = {c: [0.0] + [math.log(px[c][t] / px[c][t - 1]) for t in range(1, n)] for c in coins}
    idx = [sum(lr[c][t] for c in coins) / len(coins) for t in range(n)]
    fd = []                                  # funding ETH − BTC ของวัน t (ผลรวม 3 รอบที่ชำระแล้ว ณ 00/08/16 UTC) เป็น %
    for t in range(n):
        e = fund.get(dates[t], {}).get("ETH-PERPETUAL", [])
        b = fund.get(dates[t], {}).get("BTC-PERPETUAL", [])
        fd.append((sum(e) - sum(b)) * 100 if e and b else None)
    beta = {c: S.ols(idx[1:nf], lr[c][1:nf])["slope"] for c in ("ETH", "BTC")}   # β บนดัชนีถ่วงน้ำหนักเท่ากัน (บท 9-10) จากช่วงเลือก
    rows = [None] * n
    for t in range(WIN_Z, n):
        w = L[t - WIN_Z + 1:t + 1]
        z = (L[t] - S.mean(w)) / S.sd(w)
        fs = [x for x in fd[t - WIN_F + 1:t + 1] if x is not None]
        f = S.mean(fs) * 365                 # เปอร์เซ็นต์ต่อปี
        res = ((L[t] - L[t - WIN_R]) - (beta["ETH"] - beta["BTC"]) * math.fsum(idx[t - WIN_R + 1:t + 1])) * 100
        end = nf if t < nf else n
        y = (L[t + H] - L[t]) * 100 if t + H < end else None
        fut = None
        if t + H < end:                      # funding ของช่วงเดียวกับป้ายคำตอบ (วัน t+1..t+5) — ตัวอย่างการรั่ว
            ff = [x for x in fd[t + 1:t + H + 1] if x is not None]
            fut = S.mean(ff) * 365
        rows[t] = {"t": t, "z": z, "f": f, "r": res, "y": y, "fut": fut}
    return rows, L, lr, idx, fd, beta


def _extra_feats(t, L, fd, lr, idx, beta):
    """คุณลักษณะ 12 ตัวสำหรับโมเดลที่ 'ใส่ทุกอย่าง': Z สามหน้าต่าง · funding สามหน้าต่าง · ส่วนที่เหลือสามช่วง · ตลาด 20 วัน · SD สองเหรียญ"""
    out = []
    for w in (20, 60, 120):
        win = L[t - w + 1:t + 1]
        out.append((L[t] - S.mean(win)) / S.sd(win))
    for w in (1, 7, 30):
        xs = [x for x in fd[t - w + 1:t + 1] if x is not None]
        out.append(S.mean(xs) * 365)
    for w in (5, 20, 60):
        out.append(((L[t] - L[t - w]) - (beta["ETH"] - beta["BTC"]) * math.fsum(idx[t - w + 1:t + 1])) * 100)
    out.append(math.fsum(idx[t - 19:t + 1]) * 100)
    out.append(S.sd(lr["ETH"][t - 19:t + 1]) * 100)
    out.append(S.sd(lr["BTC"][t - 19:t + 1]) * 100)
    return out


def _real(q):
    dates, px, nf, fund = _real_inputs()
    rows, L, lr, idx, fd, beta = _real_rows(dates, px, nf, fund)
    n = len(dates)
    F = [r for r in rows[:nf] if r and r["y"] is not None]
    V = [r for r in rows[nf:] if r and r["y"] is not None]
    yF, yV = [r["y"] for r in F], [r["y"] for r in V]
    mu = {k: S.mean([r[k] for r in F]) for k in KEYS}
    sd = {k: S.sd([r[k] for r in F]) for k in KEYS}

    def sc(r, k):                          # คะแนน = −(ค่า − Mean ช่วงเลือก) ÷ SD ช่วงเลือก (ทิศที่คาดจากเหตุผล: กลับทิศทั้งสาม)
        return -(r[k] - mu[k]) / sd[k]

    out = {"วันช่วงเลือก": nf, "วันช่วงตรวจ": n - nf, "แถวช่วงเลือก": len(F), "แถวช่วงตรวจ": len(V),
           "แถวไม่ซ้อนช่วงเลือก": len(F) // H, "แถวไม่ซ้อนช่วงตรวจ": len(V) // H,
           "betaETH": q(beta["ETH"], 2), "betaBTC": q(beta["BTC"], 2)}
    out["ไม้บรรทัด"] = {k: {"Mean": q(mu[k], 2), "SD": q(sd[k], 2)} for k in KEYS}
    # สั่นเองของ IC (บท 8: 1 ÷ √(n − 1)) โดยนับเฉพาะช่วงห้าวันที่ไม่ซ้อนกัน
    out["สั่นเองช่วงเลือก"] = q(1 / math.sqrt(len(F) / H - 1), 2)
    out["สั่นเองช่วงตรวจ"] = q(1 / math.sqrt(len(V) / H - 1), 2)
    out["สั่นเองถ้านับทุกวัน"] = q(1 / math.sqrt(len(F) - 1), 2)
    out["สองเท่าสั่นเองช่วงตรวจ"] = q(2 * out["สั่นเองช่วงตรวจ"], 2)
    out["สองเท่าสั่นเองช่วงเลือก"] = q(2 * out["สั่นเองช่วงเลือก"], 2)
    # ตารางตัวอย่าง: หกวันในช่วงเลือก ห่างกัน 5 วัน (ปลายช่วงเลือก)
    sample = []
    for r in F[-30::5]:
        sample.append({"วัน": dates[r["t"]], "Z": q(r["z"], 2), "funding": q(r["f"], 2), "ส่วนที่เหลือ": q(r["r"], 2),
                       "คะแนนZ": q(sc(r, "z"), 2), "คะแนนfunding": q(sc(r, "f"), 2), "คะแนนส่วนที่เหลือ": q(sc(r, "r"), 2),
                       "ผล": q(r["y"], 2)})
    r0 = sample[0]                         # แถวที่คิดให้ดูบนหน้า: คิดจากเลขปัดบนหน้า (ไม้บรรทัดปัดสองตำแหน่ง)
    rul = {k: (q(mu[k], 2), q(sd[k], 2)) for k in KEYS}
    r0["ห่างZ"] = q(r0["Z"] - rul["z"][0], 2)
    r0["ห่างfunding"] = q(r0["funding"] - rul["f"][0], 2)
    r0["ห่างส่วนที่เหลือ"] = q(r0["ส่วนที่เหลือ"] - rul["r"][0], 2)
    assert q(-r0["ห่างZ"] / rul["z"][1], 2) == r0["คะแนนZ"]
    assert q(-r0["ห่างfunding"] / rul["f"][1], 2) == r0["คะแนนfunding"]
    assert q(-r0["ห่างส่วนที่เหลือ"] / rul["r"][1], 2) == r0["คะแนนส่วนที่เหลือ"]
    out["ตัวอย่าง"] = sample
    # IC รายสัญญาณ: ช่วงเลือก (ครึ่งแรก/ครึ่งหลัง) และช่วงตรวจ
    half = nf // 2
    h1 = [r for r in F if r["t"] < half]
    h2 = [r for r in F if r["t"] >= half]
    icd = {}
    for k in KEYS:
        icd[k] = {"ช่วงเลือก": q(ic([sc(r, k) for r in F], yF), 2),
                  "ครึ่งแรก": q(ic([sc(r, k) for r in h1], [r["y"] for r in h1]), 2),
                  "ครึ่งหลัง": q(ic([sc(r, k) for r in h2], [r["y"] for r in h2]), 2),
                  "ช่วงตรวจ": q(ic([sc(r, k) for r in V], yV), 2)}
    out["IC"] = icd
    out["corrคะแนน"] = {"Zกับส่วนที่เหลือ": q(S.corr([sc(r, "z") for r in F], [sc(r, "r") for r in F]), 2),
                        "Zกับfunding": q(S.corr([sc(r, "z") for r in F], [sc(r, "f") for r in F]), 2),
                        "fundingกับส่วนที่เหลือ": q(S.corr([sc(r, "f") for r in F], [sc(r, "r") for r in F]), 2)}
    # การรั่ว: funding ของช่วงเดียวกับป้ายคำตอบ (ช่วงเลือกเท่านั้น)
    out["รั่ว"] = {"ICอนาคต": q(ic([r["fut"] for r in F], yF), 2), "ICอดีต": q(ic([r["f"] for r in F], yF), 2)}

    # ── โมเดล (เรียนจากช่วงเลือกทั้งหมด) ──
    models = {}
    for name, ks in (("Z", ("z",)), ("รวมสาม", KEYS)):
        s = [sum(sc(r, k) for k in ks) / len(ks) for r in F]
        b = S.ols(s, yF)["slope"]
        models[name] = (lambda r, ks=ks, b=b: b * sum(sc(r, k) for k in ks) / len(ks))
        out.setdefault("ความชัน", {})[name] = q(b, 2)
        out.setdefault("ICรวม", {})[name] = {"ช่วงเลือก": q(ic(s, yF), 2),
                                            "ช่วงตรวจ": q(ic([sum(sc(r, k) for k in ks) / len(ks) for r in V], yV), 2)}
    m = S.ols_multi([[sc(r, k) for r in F] for k in KEYS], yF)
    co = m["coef"]
    models["Regression"] = lambda r: sum(co[i + 1] * sc(r, k) for i, k in enumerate(KEYS))
    out["Regression"] = {"น้ำหนัก": {k: q(co[i + 1], 2) for i, k in enumerate(KEYS)},
                         "t": {k: q(m["t"][i + 1], 2) for i, k in enumerate(KEYS)},
                         "ค่าตัดแกน": q(co[0], 2), "R2": q(m["r2"] * 100, 1),
                         "ICช่วงเลือก": q(ic([models["Regression"](r) for r in F], yF), 2),
                         "ICช่วงตรวจ": q(ic([models["Regression"](r) for r in V], yV), 2)}
    # ต้นไม้หนึ่งชั้น
    cols = [[sc(r, k) for r in F] for k in KEYS]
    c_, j_, cut, dirn, tries = _best_stump(cols, yF)
    kk = KEYS[j_]
    leaf_up = [r["y"] for r in F if sc(r, kk) > cut]
    leaf_dn = [r["y"] for r in F if sc(r, kk) <= cut]
    m_up, m_dn = S.mean(leaf_up), S.mean(leaf_dn)
    models["ต้นไม้"] = lambda r: (m_up if sc(r, kk) > cut else m_dn)
    down_F = sum(1 for v in yF if v <= 0) / len(yF)
    down_V = sum(1 for v in yV if v <= 0) / len(yV)
    out["ต้นไม้"] = {"ตัวแปร": kk, "จุดตัด": q(cut, 2), "ทิศ": dirn, "จุดตัดที่ลอง": tries, "กฎที่ลอง": 2 * tries,
                     "ถูกช่วงเลือก": q(c_ / len(yF) * 100, 1), "ถูกช่วงตรวจ": q(_stump_acc([sc(r, kk) for r in V], yV, cut, dirn) * 100, 1),
                     "ทายลงตลอดช่วงเลือก": q(down_F * 100, 1), "ทายลงตลอดช่วงตรวจ": q(down_V * 100, 1),
                     "ใบบน": q(m_up, 2), "ใบล่าง": q(m_dn, 2),
                     "แถวใบบน": len(leaf_up), "แถวใบล่าง": len(leaf_dn),
                     "สัดส่วนใบล่างช่วงเลือก": q(len(leaf_dn) / len(F) * 100, 0),
                     "สัดส่วนใบล่างช่วงตรวจ": q(sum(1 for r in V if sc(r, kk) <= cut) / len(V) * 100, 0)}
    # ใส่ทุกอย่าง 12 ตัว (เริ่มวันที่ 120 ให้หน้าต่าง 120 วันครบ)
    F12 = [r for r in F if r["t"] >= 120]
    XF = [_extra_feats(r["t"], L, fd, lr, idx, beta) for r in F12]
    XV = [_extra_feats(r["t"], L, fd, lr, idx, beta) for r in V]
    y12 = [r["y"] for r in F12]
    res12 = {}
    for name, cidx in (("สาม", [1, 4, 7]), ("สิบสอง", list(range(12)))):
        mm = S.ols_multi([[x[j] for x in XF] for j in cidx], y12)
        pf = [mm["coef"][0] + sum(mm["coef"][i + 1] * x[j] for i, j in enumerate(cidx)) for x in XF]
        pv = [mm["coef"][0] + sum(mm["coef"][i + 1] * x[j] for i, j in enumerate(cidx)) for x in XV]
        res12[name] = {"ตัวแปร": len(cidx), "R2ช่วงเลือก": q(mm["r2"] * 100, 1), "R2ช่วงตรวจ": q(_r2_out(yV, pv) * 100, 1),
                       "ICช่วงเลือก": q(ic(pf, y12), 2), "ICช่วงตรวจ": q(ic(pv, yV), 2)}
    out["ใส่ทุกอย่าง"] = res12

    # ── backtest หลังต้นทุน ──
    A, B = px["ETH"], px["BTC"]

    def preds(f):
        return [None if r is None else f(r) for r in rows]

    bt = {}
    for name, f in models.items():
        p = preds(f)
        bt[name] = {"ช่วงเลือก": _bt_summary(_pair_bt(A, B, p, SETS_REAL, WIN_Z, nf), q),
                    "ช่วงตรวจ": _bt_summary(_pair_bt(A, B, p, SETS_REAL, nf, n), q)}
    p_short = preds(lambda r: -1.0)
    bt["ขายETHตลอด"] = {"ช่วงตรวจ": _bt_summary(_pair_bt(A, B, p_short, SETS_REAL, nf, n), q),
                        "ช่วงเลือก": _bt_summary(_pair_bt(A, B, p_short, SETS_REAL, WIN_Z, nf), q)}
    # walk-forward: เรียนใหม่ทุก 30 วันจาก 365 แถวล่าสุดที่ป้ายคำตอบรู้แล้ว (ตัด 5 แถวสุดท้ายที่ป้ายยังไม่ครบ)
    wf = {}
    refits = 0
    for t0 in range(nf, n, 30):
        train = [r for r in rows[:t0] if r and r["y"] is not None and r["t"] + H < t0][-365:]
        mu2 = {k: S.mean([r[k] for r in train]) for k in KEYS}
        sd2 = {k: S.sd([r[k] for r in train]) for k in KEYS}
        mm = S.ols_multi([[-(r[k] - mu2[k]) / sd2[k] for r in train] for k in KEYS], [r["y"] for r in train])
        refits += 1
        for t in range(t0, min(t0 + 30, n)):
            wf[t] = (mm["coef"], mu2, sd2)

    def p_wf(r):
        if r["t"] not in wf:
            return None
        cc, mu2, sd2 = wf[r["t"]]
        return sum(cc[i + 1] * (-(r[k] - mu2[k]) / sd2[k]) for i, k in enumerate(KEYS))

    pw = [None if (r is None or r["t"] < nf) else p_wf(r) for r in rows]
    bt["เรียนใหม่ทุก30วัน"] = {"ช่วงตรวจ": _bt_summary(_pair_bt(A, B, pw, SETS_REAL, nf, n), q)}
    out["เรียนใหม่"] = {"ครั้ง": refits, "แถวที่เรียน": 365, "ตัดท้าย": H,
                        "ICช่วงตรวจ": q(ic([p_wf(r) for r in V], yV), 2)}
    out["backtest"] = bt
    out["มูลค่าขาETHต้นช่วงตรวจ"] = q(SETS_REAL * A[nf], 0)
    out["ETHต้นช่วงตรวจ"] = q(A[nf], 2)
    # ครั้งที่ดูช่วงตรวจในบทนี้ (ทุกแบบที่รันกับช่วงตรวจ = หนึ่งครั้ง)
    looks = ["Z", "รวมสาม", "Regression", "ต้นไม้", "ขายETHตลอด", "เรียนใหม่ทุก30วัน", "ใส่ทุกอย่างสิบสอง"]
    out["ดูช่วงตรวจ"] = len(looks)
    out["ดูช่วงตรวจรายการ"] = looks
    return out


# ───────────────────────── โลกจำลองที่รู้คำตอบ ─────────────────────────

NF_SIM, NV_SIM = 731, 365
SIM_PHI, SIM_K, SIM_PHIF, SIM_SD, SIM_NOISE, SIM_COPY = 0.97, 0.15, 0.95, 1.5, 17, 0.6
SIM_SETS = 5.0          # ขา A ราว 500 (ราคาเริ่ม 100)


def _sim_world(seed, k=SIM_K, phi=SIM_PHI, n_noise=SIM_NOISE):
    """โลกของชุดหนึ่งชุด: x = ระดับของชุด (%) · x[t+1] = φ·x[t] − k·f[t] + แรงสะบัด SD 1.5%
    f = 'funding จำลอง' AR(1) φ 0.95 SD 1 (เป็นสัญญาณจริง) · Z ของ x บนไม้บรรทัดเลื่อน 60 วัน (สัญญาณจริงเพราะ φ < 1)
    c = Z + แรงสะบัด SD 0.6 (สำเนาของ Z แบบ 'ส่วนที่เหลือ' จริง) · ตัวแปรสุ่ม 17 ตัวที่ไม่เกี่ยวกับอะไรเลย
    ราคา: B = 100·exp(แรงร่วมเดินสุ่ม 2% ต่อวัน) · A = B·exp(x/100)"""
    g = random.Random(seed)
    n = NF_SIM + NV_SIM
    f, x, cm = [0.0], [0.0], [0.0]
    for t in range(1, n):
        f.append(SIM_PHIF * f[-1] + g.gauss(0, math.sqrt(1 - SIM_PHIF ** 2)))
        x.append(phi * x[-1] - k * f[t - 1] + g.gauss(0, SIM_SD))
        cm.append(cm[-1] + g.gauss(0, 0.02))
    noise = [[g.gauss(0, 1) for _ in range(n)] for _ in range(n_noise)]
    rows = [None] * n
    for t in range(WIN_Z, n):
        w = x[t - WIN_Z + 1:t + 1]
        z = (x[t] - S.mean(w)) / S.sd(w)
        end = NF_SIM if t < NF_SIM else n
        rows[t] = {"t": t, "z": z, "f": f[t], "c": z + SIM_COPY * g.gauss(0, 1),
                   "nz": [col[t] for col in noise], "y": x[t + H] - x[t] if t + H < end else None}
    B = [100 * math.exp(v) for v in cm]
    A = [b * math.exp(v / 100) for b, v in zip(B, x)]
    return {"rows": rows, "A": A, "B": B, "seed": seed}


def _sim_analyse(w):
    rows, A, B = w["rows"], w["A"], w["B"]
    n = len(rows)
    F = [r for r in rows[:NF_SIM] if r and r["y"] is not None]
    V = [r for r in rows[NF_SIM:] if r and r["y"] is not None]
    yF, yV = [r["y"] for r in F], [r["y"] for r in V]
    ks = ("z", "f", "c")
    mu = {k: S.mean([r[k] for r in F]) for k in ks}
    sd = {k: S.sd([r[k] for r in F]) for k in ks}

    def sc(r, k):
        return -(r[k] - mu[k]) / sd[k]

    res = {}
    for k in ks:
        res["IC_" + k] = (ic([sc(r, k) for r in F], yF), ic([sc(r, k) for r in V], yV))
    models = {}
    for name, use in (("Z", ("z",)), ("รวมสอง", ("z", "f")), ("รวมสาม", ("z", "f", "c"))):
        s = [sum(sc(r, k) for k in use) / len(use) for r in F]
        b = S.ols(s, yF)["slope"]
        models[name] = (lambda r, use=use, b=b: b * sum(sc(r, k) for k in use) / len(use))
        res["IC_" + name] = (ic(s, yF), ic([sum(sc(r, k) for k in use) / len(use) for r in V], yV))
    m3 = S.ols_multi([[sc(r, k) for r in F] for k in ks], yF)
    models["Regression"] = lambda r, c=m3["coef"]: sum(c[i + 1] * sc(r, k) for i, k in enumerate(ks))
    cols20 = [[sc(r, k) for r in F] for k in ks] + [[r["nz"][j] for r in F] for j in range(SIM_NOISE)]
    m20 = S.ols_multi(cols20, yF)
    c20 = m20["coef"]
    models["ใส่ทุกอย่าง"] = lambda r: (sum(c20[i + 1] * sc(r, k) for i, k in enumerate(ks)) +
                                     sum(c20[4 + j] * r["nz"][j] for j in range(SIM_NOISE)))
    pv3 = [m3["coef"][0] + models["Regression"](r) for r in V]
    pv20 = [c20[0] + models["ใส่ทุกอย่าง"](r) for r in V]
    pf3 = [models["Regression"](r) for r in F]
    pf20 = [models["ใส่ทุกอย่าง"](r) for r in F]
    res["IC_Regression"] = (ic(pf3, yF), ic(pv3, yV))
    res["IC_ใส่ทุกอย่าง"] = (ic(pf20, yF), ic(pv20, yV))
    res["R2_3"] = (m3["r2"], _r2_out(yV, pv3))
    res["R2_20"] = (m20["r2"], _r2_out(yV, pv20))
    best = _best_stump(cols20, yF)
    c_, j_, cut, dirn, _ = best
    colV = [sc(r, ks[j_]) if j_ < 3 else r["nz"][j_ - 3] for r in V]
    res["ต้นไม้"] = (c_ / len(yF), _stump_acc(colV, yV, cut, dirn))
    res["ต้นไม้เลือกตัวสุ่ม"] = 1.0 if j_ >= 3 else 0.0
    res["ทายทางเดียว"] = (max(sum(1 for v in yF if v > 0), sum(1 for v in yF if v <= 0)) / len(yF),
                          max(sum(1 for v in yV if v > 0), sum(1 for v in yV if v <= 0)) / len(yV))
    for name, f in models.items():
        pred = [None if r is None else f(r) for r in rows]
        res["ผล_" + name] = _pair_bt(A, B, pred, SIM_SETS, NF_SIM, n)["net"]
    return res


def _sim(q):
    out = {"โลก": len(SEEDS), "ครึ่งชีวิต": q(S.half_life(SIM_PHI), 0), "φ": SIM_PHI, "k": SIM_K, "φf": SIM_PHIF, "แรงสะบัด": SIM_SD, "ตัวแปรสุ่ม": SIM_NOISE,
           "ตัวแปรรวม": SIM_NOISE + 3, "สำเนาSD": SIM_COPY}
    keys = None
    vals = {}
    for seed in SEEDS:
        r = _sim_analyse(_sim_world(seed))
        keys = keys or list(r)
        for k, v in r.items():
            vals.setdefault(k, []).append(v)

    def med(v, n=2, scale=1.0):
        return q(statistics.median(v) * scale, n)

    for k in keys:
        v = vals[k]
        if isinstance(v[0], tuple):
            scale = 100.0 if (k.startswith("R2") or k in ("ต้นไม้", "ทายทางเดียว")) else 1.0
            nd = 1 if scale == 100.0 else 2
            out[k] = {"ช่วงเลือก": med([a for a, _ in v], nd, scale), "ช่วงตรวจ": med([b for _, b in v], nd, scale)}
            if k.startswith("R2"):
                out[k]["ช่วงตรวจติดลบ"] = sum(1 for _, b in v if b < 0)
        elif k.startswith("ผล_"):
            out[k] = {"มัธยฐาน": med(v), "บวก": sum(1 for x in v if x > 0), "ต่ำสุด": q(min(v), 2), "สูงสุด": q(max(v), 2)}
        else:
            out[k] = int(sum(v))
    # รวมสองชนะ Z กี่โลก (หลังต้นทุน ช่วงตรวจ)
    out["รวมสองชนะZ"] = sum(1 for a, b in zip(vals["ผล_รวมสอง"], vals["ผล_Z"]) if a > b)
    out["Regressionชนะใส่ทุกอย่าง"] = sum(1 for a, b in zip(vals["ผล_Regression"], vals["ผล_ใส่ทุกอย่าง"]) if a > b)
    # โลกที่ไม่มีอะไรให้เก็บ: ชุดเดินสุ่ม (φ 1) และ funding จำลองไม่มีผล (k 0) · ใช้ sab2_sim.reseed
    null = M.reseed(lambda seed: _sim_world(seed, k=0.0, phi=1.0),
                    lambda w: _sim_analyse(w)["ผล_รวมสอง"], seeds=SEEDS)
    out["โลกว่าง"] = {"มัธยฐาน": q(null["median"], 2), "บวก": sum(1 for v in null["values"] if v > 0),
                     "ต่ำสุด": q(null["min"], 2), "สูงสุด": q(null["max"], 2)}
    return out, null


# ───────────────────────── รวม ─────────────────────────

def extend(data, D, q):
    hand = _hand(q)
    tree = _hand_tree(q)
    real = _real(q)
    sim, null = _sim(q)
    f1 = SB.load_figures("sab")
    ai = f1["ch18"]["บอท"]["AI"]
    vol1 = {"แม่นช่วงสอน": ai["แม่นช่วงสอน"], "แม่นช่วงหลัง": ai["แม่นช่วงหลัง"],
            "ต้องชนะเปอร์เซ็นต์": ai["ที่70"]["ต้องชนะเปอร์เซ็นต์"]}
    consts = {"ป้ายวัน": H, "หน้าต่างZ": WIN_Z, "หน้าต่างส่วนที่เหลือ": WIN_R, "หน้าต่างfunding": WIN_F,
              "รอบfunding": 3 * WIN_F, "ค่าธรรมเนียมเปอร์เซ็นต์": q(FEE * 100, 2), "ต้นทุนไปกลับ": q(COST, 1),
              "ETHเหรียญ": SETS_REAL, "ทุน": int(CAPITAL), "ขาตัวอย่าง": 500, "ปีเริ่ม": "2022", "ปีจบตรวจ": "2025"}
    # กล่อง 🧰 (ที่มา: tools/sab_research/practitioner-research.md §1.1 · §3.2–3.3 · §4 · §5 · §9.1 ·
    #  ตัวเลขตามที่บันทึกไว้ ไม่ได้คำนวณ · ปีเป็นสตริง)
    prac = {"ปีSarmento": "2020", "ปีวิทยานิพนธ์": "2019", "Sarmentop": 1, "SarmentoHurst": 0.5, "Sarmentoข้าม": 12,
            "SarmentoETF": 208, "Sarmentoนาที": 5,
            "ปีFischer": "2019", "Fischerเหรียญ": 40, "Fischerต่อวัน": 7.1, "Fischerต้นทุน": 15,
            "ปีHLZ": "2016", "HLZt": 3.0, "ปีBailey": "2014", "Sarmentoคู่": 190, "Sarmentoผิด": 9, "Sarmentoสินทรัพย์": 20}
    drills = [
        {"โจทย์": "(ทำตาม) แปดวัน คะแนน funding — อันดับ ผลรวมต่างยกกำลังสอง และ IC สองทาง", "คำตอบ": hand["บล็อก"]["f"]["IC"]},
        {"โจทย์": "(เปลี่ยนเลข) ผลวันที่ 8 เป็น +2.6 — IC ของคะแนน Z ใหม่", "คำตอบ": None},
        {"โจทย์": "(เปลี่ยนเงื่อนไข) ต้นทุนไปกลับ 0.6% — คะแนนรวมต้องเกินเท่าไร และเหลือกี่วันที่เทรด", "คำตอบ": None},
        {"โจทย์": "(ตัดสินใจ) ต้นไม้ทายถูก 62.2% ในช่วงเลือก — เอาไปใช้ไหม", "คำตอบ": real["ต้นไม้"]["ทายลงตลอดช่วงเลือก"]},
        {"โจทย์": "(ถ่ายโอน · ข้อมูลจริง) funding ของช่วงเดียวกับป้ายคำตอบ IC 0.23 — รั่วตรงไหน", "คำตอบ": real["รั่ว"]["ICอนาคต"]},
    ]
    # แบบฝึกข้อ 2: ผลวันที่ 8 เปลี่ยนจาก 0.2 เป็น 2.6 (อันดับผลของวันที่ 8 ขึ้นเป็น 8) → IC ของคะแนน Z
    y2 = list(HAND_Y)
    y2[7] = 2.6
    b2 = _rank_block(HAND_SZ, y2)
    ex2 = {"ผลใหม่": 2.6, "รวมต่าง2": b2["รวมต่าง2"], "หกเท่า": b2["หกเท่า"], "IC": q(b2["IC"], 2),
           "อันดับผลวัน8": int(_ranks(y2)[7])}
    drills[1]["คำตอบ"] = ex2["IC"]
    # แบบฝึกข้อ 3: ต้นทุนไปกลับ 0.6%
    slope = hand["ความชัน"]
    cut3 = 0.6 / slope
    b2s = [d["รวมสอง"] for d in hand["วัน"]]
    days3 = [d["วัน"] for d in hand["วัน"] if abs(d["รวมสอง"]) > cut3]
    ex3 = {"ต้นทุน": 0.6, "คะแนนต้องเกิน": q(cut3, 1), "วันที่เทรด": days3, "จำนวน": len(days3),
           "สุทธิคะแนนสาม": q(slope * 3 - 0.6, 2), "สุทธิคะแนนสอง": q(slope * 2 - 0.6, 2)}
    assert max(abs(x) for x in b2s) == 3
    drills[2]["คำตอบ"] = ex3["คะแนนต้องเกิน"]
    hand["แบบฝึก"] = {"ข้อ2": ex2, "ข้อ3": ex3}
    snoop = {"ดูช่วงตรวจ": real["ดูช่วงตรวจ"]}
    axes = {"มือ": {"x": [-3, -2, -1, 0, 1, 2, 3], "y": [-3, -2, -1, 0, 1, 2]},
            "ICโลก": [0, 0.1, 0.2, 0.3], "ICจริง": [-0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4]}
    return {"_แบบฝึก": drills, "ค่า": consts, "มือ": hand, "ต้นไม้มือ": tree, "จริง": real, "โลก": sim,
            "นับรอบ": snoop, "เล่ม1": vol1, "คนทำงานจริง": prac, "แกน": axes}
