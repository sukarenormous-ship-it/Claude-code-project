"""บท 15 เล่ม 2 — ต้นทุน ขนาด และการเสื่อมของกลยุทธ์ · ค่าทุกตัวของ docs/sab2-part15.html
(ปลั๊กอินของ tools/sab_figures.py --book sab2 · แถว "บท 14" ในตาราง §4 ของแผน ซึ่งยังใช้เลขเดิม)

ตอน ก  ต้นทุนสามชั้นต่อ fill (ค่าธรรมเนียม taker 0.05% ของเล่ม 1 · ครึ่งหนึ่งของ Bid-Ask Spread 0.05% = ชั้นแรกของ
       กระดานสมมติเล่ม 1 บท 16 · ผลกระทบราคา: ราคาเลื่อน 0.02% ต่อทุก 1,000 ดอลลาร์ที่กิน → เฉลี่ยครึ่งหนึ่ง 0.01% ต่อ 1,000)
       ด้วยมือ: กำไรก่อนต้นทุน 1% ของขาต่อไม้ · 4 fill ต่อไม้ · ขาละ 1,000 → 20,000 → เส้นกำไรตามขนาดเป็นพาราโบลา
       กำไรสุทธิ = (g − 4c) × s − 4κ × s² → จุดสูงสุด s* = (g − 4c) ÷ (8κ) · จุดคุ้มทุน = 2 s*
       📡 การ์ด LTC บน DOT (บท 7 · h 3.76 · ไม้บรรทัดช่วงเลือก · 10 ชุด) ในช่วงตรวจ: กำไรก่อนต้นทุนจาก sab2_engine (fee 0)
          ต้นทุนสามชั้นคิดจากมูลค่าจริงของทุก fill ทีละขา → กำไรสุทธิเมื่อขยาย m เท่า = m·G − m·L − m²·I (พาราโบลาเดียวกัน)
       🎲 price_pair (h 2 · φ 0.9 · แรงสะบัด 0.5 · A ≈ 100 B ≈ 50 · 10 ชุด = ขาละราว 1,000) 365 วัน × 30 โลก:
          จุดสูงสุดที่ประมาณจากปีเดียว เทียบค่าจริงจาก 30 ปีรวมกัน
ตอน ข  การเสื่อม: ครึ่งแรกเทียบครึ่งหลังด้วยมือ (12 เดือนสอน · SE = SD ÷ √n · ตัวหาร n − 1) → อัตราส่วน ÷ SE ของผลต่าง
       📡 funding carry (Deribit BTC/ETH-PERPETUAL · เดือนละ 30 วัน · แบบบท 12) ปีที่ 1 · ปีที่ 2 (ช่วงเลือก) · ปีที่ 3 (ช่วงตรวจ)
          + สัญญาณที่เข้ากับ Crowding: สัดส่วนรอบที่ติดลบ · รอบที่เกิน 0.03% · ค่าเฉลี่ยต่อปี
       🎲 โลกรายได้รายเดือน (Mean 0.6% SD 0.7% · ปกติ) 24 เดือน + 12 เดือน · ขอบหายครึ่ง / ไม่หาย · 30 โลก (seed 1–30)
ตอน ค  แผนภูมิควบคุมแบบผลรวมสะสม: ที่คาด n·μ · เส้นเตือน n·μ − 1 SD × √n · เส้นลงมือ n·μ − 2 SD × √n
       ด้วยมือหกเดือน · เดือนที่ต้องรอ ≈ (2σ ÷ Δ)² · 📡 ETH/BTC ช่วงตรวจเทียบค่าคาดจากช่วงเลือก ·
       🎲 เดือนที่เห็นเมื่อขอบหายครึ่ง / หายหมด / กลับทิศ และสัญญาณหลอกเมื่อไม่มีอะไรเปลี่ยน

ข้อมูลจริงผ่าน sab2_realdata.load_closes/load_funding (ช่วงเลือกและช่วงตรวจเท่านั้น) · สถิติผ่าน sab2_stats ·
backtest ผ่าน sab2_engine.run · โลกจำลองผ่าน sab2_sim (price_pair · ROBUST_SEEDS) และ random.Random(seed) seed 1–30 ·
ตัวเลขเล่ม 1 ผ่าน sab_book.load_figures("sab")
"""

import math
import random
import statistics
from collections import defaultdict

import sab_book as SB
import sab2_engine as E
import sab2_sim as M
import sab2_stats as S
from sab2_realdata import load_closes, load_funding

SEEDS = M.ROBUST_SEEDS
MONTH = 30                        # หนึ่งเดือนของเล่ม = 30 วัน (แบบบท 12)

# ── สามชั้น (ค่าของเล่ม ไม่ใช่ราคาของ exchange ใด) ──
FEE_PCT = 0.05                    # taker ของเล่ม 1 บท 11 (ตรวจกับบัญชีมินด้านล่าง)
HALF_SPREAD_PCT = 0.05            # ครึ่งหนึ่งของ Bid-Ask Spread = ชั้นแรกของกระดานสมมติเล่ม 1 บท 16 (ตรวจด้านล่าง)
SLIDE_PER_1000 = 0.02             # ราคาเลื่อน 0.02% ต่อทุก 1,000 ดอลลาร์ที่กินกระดาน (ค่าสมมติของบท)
AVG_PER_1000 = SLIDE_PER_1000 / 2  # ราคาเฉลี่ยที่จ่ายเลื่อนครึ่งหนึ่งของจุดสุดท้าย
KAPPA = AVG_PER_1000 / 100 / 1000  # ต้นทุนผลกระทบต่อ fill = KAPPA × มูลค่า² (= 1e-7)
FILLS = 4                         # เข้า A · เข้า B · ออก A · ออก B
EDGE_PCT = 1.0                    # ด้วยมือ: กำไรก่อนต้นทุนต่อไม้ = 1% ของมูลค่าขา
SIZES = [1000, 5000, 7500, 10000, 15000, 20000]

# ── การ์ด LTC บน DOT ของบท 7 ──
PAIR_H, PAIR_SETS = 3.76, 10

# ── ตอน ข · 12 เดือนสอน (% ต่อเดือนของมูลค่าที่ถือ · ตัวเลขตั้งโจทย์ ไม่ใช่ผลวัด) ──
HALF1 = [1.5, -0.3, 0.9, 0.0, 1.2, 0.3]
HALF2 = [0.0, 1.2, -0.3, 0.9, -0.6, 0.6]

# ── ตอน ค · หกเดือนสอน (ผลจริงรายเดือน %) เทียบที่คาด μ 0.6 SD 0.7 จาก backtest ──
LIVE6 = [0.2, -0.4, 0.5, 0.1, -0.2, 0.3]
MU_T, SD_T = 0.6, 0.7
SPIKE = 0.0003                    # รอบ 8 ชม. ที่ funding เกิน 0.03% (เกณฑ์ของบท)

SIM_MU, SIM_SD = 0.6, 0.7         # 🎲 โลกรายได้รายเดือน (ใกล้ค่าที่ประมาณได้จากช่วงเลือก)


def _r(x, n=2):
    return round(float(x) + 0.0, n)


def _three(s, q):
    """ต้นทุนสามชั้นของ fill ขาละ s ดอลลาร์"""
    fee = FEE_PCT / 100 * s
    spr = HALF_SPREAD_PCT / 100 * s
    imp = AVG_PER_1000 / 100 * s / 1000 * s
    return fee, spr, imp


def _hand(q, f1):
    rows = []
    a = (EDGE_PCT - FILLS * (FEE_PCT + HALF_SPREAD_PCT)) / 100       # (g − 4c) ต่อดอลลาร์
    b = FILLS * KAPPA                                               # 4κ
    base_net = None
    for s in SIZES:
        fee, spr, imp = _three(s, q)
        fill = fee + spr + imp
        gross = EDGE_PCT / 100 * s
        net = gross - FILLS * fill
        if s == 1000:
            base_net = net
        rows.append({"ขา": s, "ค่าธรรมเนียม": q(fee, 2), "ครึ่งspread": q(spr, 2), "ราคาเลื่อนสุด": q(SLIDE_PER_1000 * s / 1000, 2),
                     "เลื่อนเฉลี่ย": q(AVG_PER_1000 * s / 1000, 2), "ผลกระทบ": q(imp, 2), "ต่อfill": q(fill, 2),
                     "ต่อfillเปอร์เซ็นต์": q(fill / s * 100, 2), "สี่fill": q(FILLS * fill, 2),
                     "สี่fillเส้นตรง": q(FILLS * (fee + spr), 2), "สี่fillผลกระทบ": q(FILLS * imp, 2),
                     "ก่อนต้นทุน": q(gross, 2), "สุทธิ": q(net, 2), "ต่อดอลลาร์เปอร์เซ็นต์": q(net / s * 100, 2),
                     "เท่าของ1000": q(s / 1000, 1), "ถ้าเส้นตรง": q(base_net * s / 1000, 2),
                     "สูตร": q(a * s - b * s * s, 2)})
        assert abs((a * s - b * s * s) - net) < 1e-9
    peak = a / (2 * b)
    at = {r["ขา"]: r for r in rows}
    # กระดานสมมติของเล่ม 1 บท 16: ราคาเฉลี่ยที่เสีย (ครึ่ง spread + ผลกระทบ) เทียบสูตรเรียบของบทนี้
    v1 = {r["ขนาดต่อขา"]: r for r in f1["ch16"]["v2"]["capacity"]["ตาราง"]}
    cmp_rows = []
    for s in (1000, 5000, 10000, 20000):
        _, spr, imp = _three(s, q)
        cmp_rows.append({"ขา": s, "เล่ม1": q(v1[s]["เสียต่อfill"] / s * 100, 2), "เล่ม1ดอลลาร์": v1[s]["เสียต่อfill"],
                         "บทนี้": q((spr + imp) / s * 100, 2), "บทนี้ดอลลาร์": q(spr + imp, 2)})
    return {"แถว": rows, "a": q(a * 100, 2), "สี่κต่อล้าน": q(b * 1e6, 2), "κต่อล้าน": q(KAPPA * 1e6, 2),
            "จุดสูงสุด": q(peak, 0), "สุทธิสูงสุด": q(a * peak - b * peak * peak, 2), "คุ้มทุน": q(a / b, 0),
            "สูงสุดเท่าของ1000": q(peak / 1000, 1), "คุ้มทุนเท่าของ1000": q(a / b / 1000, 0),
            "ต่อดอลลาร์เล็กมาก": q(a * 100, 2), "ต่อดอลลาร์ที่สูงสุด": q((a - b * peak) * 100, 2),
            "ขยาย20เท่าเส้นตรง": at[20000]["ถ้าเส้นตรง"], "ขยาย20เท่าจริง": at[20000]["สุทธิ"],
            "ห้าพันสี่fill": at[5000]["สี่fill"], "ลดต่อพันเปอร์เซ็นต์": q(b * 1000 * 100, 2),
            "เทียบเล่ม1": cmp_rows,
            "สูตรa": {"g": EDGE_PCT, "สี่c": q(FILLS * (FEE_PCT + HALF_SPREAD_PCT), 2)},
            # แบบฝึก: ผลกระทบสองเท่า · ใช้ maker
            "แบบฝึก": _hand_drills(q, a, b)}


def _hand_drills(q, a, b):
    b2 = 2 * b
    p2 = a / (2 * b2)
    s5 = 5000
    fee, spr, imp = _three(s5, q)
    imp2 = 2 * imp
    maker = 0.02                                                     # maker ของเล่ม 1 (ตรวจกับบัญชีมิน)
    am = (EDGE_PCT - FILLS * maker) / 100
    pm = am / (2 * b)
    return {"ข้อ1": {"ค่าธรรมเนียม": q(fee, 2), "ครึ่งspread": q(spr, 2), "ผลกระทบ": q(imp, 2), "ต่อfill": q(fee + spr + imp, 2),
                     "สี่fill": q(4 * (fee + spr + imp), 2), "ก่อนต้นทุน": q(EDGE_PCT / 100 * s5, 2),
                     "สุทธิ": q(EDGE_PCT / 100 * s5 - 4 * (fee + spr + imp), 2),
                     "ลืมคูณสี่": q(EDGE_PCT / 100 * s5 - (fee + spr + imp), 2)},
            "ข้อ2": {"ผลกระทบห้าพัน": q(imp2, 2), "จุดสูงสุด": q(p2, 0), "สุทธิสูงสุด": q(a * p2 - b2 * p2 * p2, 2),
                     "คุ้มทุน": q(a / b2, 0), "สุทธิหนึ่งหมื่น": q(a * 10000 - b2 * 1e8, 2)},
            "ข้อ3": {"maker": maker, "สี่c": q(FILLS * maker, 2), "a": q(am * 100, 2), "จุดสูงสุด": q(pm, 0),
                     "สุทธิสูงสุด": q(am * pm - b * pm * pm, 2), "คุ้มทุน": q(am / b, 0),
                     "สุทธิเจ็ดพันห้า": q(am * 7500 - b * 7500 ** 2, 2),
                     "ต่อพันเหลือ": q(am * 1000, 1), "หักต่อพัน": q(FILLS * maker / 100 * 1000, 1),
                     "กำไรหลังเส้นตรงที่ยอด": q(am * pm, 1), "ยอดกำลังสอง": q((pm / 1000) ** 2, 2),
                     "ผลกระทบที่ยอด": q(b * pm * pm, 1)},
            "ข้อ2เพิ่ม": {"ผลกระทบต่อไม้ที่พัน": q(2 * FILLS * KAPPA * 1e6, 1), "ยอดพัน": q(p2 / 1000, 2),
                         "ยอดพันกำลังสอง": q((p2 / 1000) ** 2, 4), "กำไรหลังเส้นตรงที่ยอด": q(a * p2, 1),
                         "ผลกระทบที่ยอด": q(b2 * p2 * p2, 2), "ยอดเดิมสุทธิ": q(a * 7500 - b2 * 7500 ** 2, 2)}}


def _legs_cost(fills, sets, h):
    """มูลค่าทีละขาของทุก fill (ขา A = sets × ราคา A · ขา B = sets × h × ราคา B) → L (ส่วนเส้นตรง) · I (ส่วนผลกระทบ)"""
    lin = imp = traded = 0.0
    nlegs = 0
    for f in fills:
        for v in (sets * f["A"], sets * h * f["B"]):
            lin += (FEE_PCT + HALF_SPREAD_PCT) / 100 * v
            imp += KAPPA * v * v
            traded += v
            nlegs += 1
    return lin, imp, traded, nlegs


def _capacity(G, L, I):
    if G <= L:
        return None, None, None
    m = (G - L) / (2 * I)
    return m, m * G - m * L - m * m * I, (G - L) / I


def _real_pair(q):
    _, F = load_closes("formation", coins=["LTC", "DOT"])
    X = [a - PAIR_H * b for a, b in zip(F["LTC"], F["DOT"])]
    mx, sx = S.mean(X), S.sd(X)
    dates, V = load_closes("validation", coins=["LTC", "DOT"])
    a, b = V["LTC"], V["DOT"]
    z = [(x - PAIR_H * y - mx) / sx for x, y in zip(a, b)]
    r0 = E.run(a, b, PAIR_H, z, sets=PAIR_SETS, fee=0.0)
    r1 = E.run(a, b, PAIR_H, z, sets=PAIR_SETS)
    L, I, traded, nlegs = _legs_cost(r0["fill_list"], PAIR_SETS, PAIR_H)
    G, L, I = float(q(r0["net"], 2)), float(q(L, 2)), float(q(I, 2))   # ผู้อ่านคิดต่อจากเลขปัดบนหน้า
    m, best, be = _capacity(G, L, I)
    legA = [PAIR_SETS * f["A"] for f in r0["fill_list"]]
    legB = [PAIR_SETS * PAIR_H * f["B"] for f in r0["fill_list"]]
    pnl = [t["pnl"] for t in r0["trade_list"]]
    sd_tr = S.sd(pnl)
    curve = []
    for mult in (1, 2, 5, 10, 20, 40):
        curve.append({"เท่า": mult, "ชุด": PAIR_SETS * mult, "สุทธิ": q(mult * G - mult * L - mult * mult * I, 2),
                      "ขาAเฉลี่ย": q(mult * S.mean(legA), 0)})
    # ถ้าความลึกของกระดาน DOT/LTC บางกว่าสมมติ 4 เท่า (κ × 4) จุดสูงสุดหด 4 เท่า
    m4, best4, _ = _capacity(G, L, 4 * I)
    # ขอบ G ประมาณจากไม้ไม่กี่ไม้: G ± 2 SE (SE ของผลรวม = SD ต่อไม้ × √จำนวนไม้)
    se_G = sd_tr * math.sqrt(len(pnl))
    g_lo = G - 2 * se_G
    return {"กำไรก่อนต้นทุน": q(G, 2), "สุทธิแอป": q(r1["net"], 2), "ค่าธรรมเนียมแอป": q(r1["costs"], 2),
            "ไม้": r0["trades"], "ไม้ค้าง": abs(r0["open"]), "fill": r0["fills"], "ขาที่ซื้อขาย": nlegs,
            "มูลค่าซื้อขาย": q(traded, 0), "L": q(L, 2), "I": q(I, 2), "ขาAเฉลี่ย": q(S.mean(legA), 0),
            "ขาBเฉลี่ย": q(S.mean(legB), 0), "ขอบต่อดอลลาร์เปอร์เซ็นต์": q(G / traded * 100, 2),
            "เส้นตรงต่อดอลลาร์เปอร์เซ็นต์": q(L / traded * 100, 2),
            "เท่าสูงสุด": q(m, 1), "ชุดสูงสุด": q(PAIR_SETS * m, 0), "สุทธิสูงสุด": q(best, 2), "เท่าคุ้มทุน": q(be, 1),
            "ชุดคุ้มทุน": q(PAIR_SETS * be, 0), "ขาAที่สูงสุด": q(m * S.mean(legA), 0), "เส้น": curve,
            "κสี่เท่า": {"เท่าสูงสุด": q(m4, 1), "ชุดสูงสุด": q(PAIR_SETS * m4, 0), "สุทธิสูงสุด": q(best4, 2)},
            "สุทธิหนึ่งเท่า": q(G - L - I, 2), "ส่วนเหลือ": q(G - L, 2), "DOTต่อชุดสิบ": q(PAIR_SETS * PAIR_H, 1),
            "ต้นร้อยชุด": q(r1["net"] * 10, 0), "สี่สิบกำลังสอง": 1600, "ต่อชุดก่อนต้นทุน": q(G / PAIR_SETS, 2),
            "SDต่อไม้": q(sd_tr, 2), "SEรวม": q(se_G, 0), "รากไม้": q(math.sqrt(len(pnl)), 2), "สองSEรวม": q(2 * se_G, 0), "ไม้ปิด": len(pnl), "Gล่าง": q(g_lo, 2), "Gล่างติดลบ": g_lo < L,
            "ชนะ": r0["wins"], "ครบเวลา": sum(1 for t in r0["trade_list"] if t["reason"] == "time"),
            "ไม้บรรทัด": {"Mean": q(mx, 2), "SD": q(sx, 2)}}


def _real_funding_capacity(q, months):
    """funding carry: ขอบต่อปี (% ของมูลค่าที่ถือ) · เปิด-ปิดปีละครั้ง = 4 fill · κ เดียวกัน (สมมติว่ากระดานลึกเท่ากัน)"""
    g = sum(months) / 100
    a = g - FILLS * (FEE_PCT + HALF_SPREAD_PCT) / 100
    b = FILLS * KAPPA
    peak = a / (2 * b)
    return {"ขอบต่อปีเปอร์เซ็นต์": q(g * 100, 2), "a": q(a * 100, 2), "จุดสูงสุด": q(peak, 0),
            "สุทธิสูงสุด": q(a * peak - b * peak * peak, 0), "คุ้มทุน": q(a / b, 0)}


def _sim_capacity(q):
    """🎲 price_pair: จุดสูงสุดจากปีเดียว เทียบค่าจริงจาก 30 ปีรวม · ไม้บรรทัดรู้คำตอบ (Mean 0 · SD นิ่ง)"""
    per, GG, LL, II, trades = [], 0.0, 0.0, 0.0, 0
    nocap = 0
    for s in SEEDS:
        w = M.price_pair(seed=s, n=365, h=2.0, phi=0.9, sd=0.5)
        sdx = w["true"]["sd_stationary"]
        z = [x / sdx for x in w["X"]]
        r0 = E.run(w["A"], w["B"], 2.0, z, sets=PAIR_SETS, fee=0.0)
        G = r0["net"]
        L, I, _, _ = _legs_cost(r0["fill_list"], PAIR_SETS, 2.0)
        GG, LL, II, trades = GG + G, LL + L, II + I, trades + r0["trades"]
        m, _, _ = _capacity(G, L, I)
        if m is None:
            nocap += 1
            per.append(0.0)
        else:
            per.append(m)
    mt, bt, bet = _capacity(GG, LL, II)
    srt = sorted(per)
    lo_n = sum(1 for v in per if v < mt / 2)
    hi_n = sum(1 for v in per if v > 2 * mt)
    return {"จริงเท่า": q(mt, 1), "จริงชุด": q(PAIR_SETS * mt, 0), "จริงขา": q(PAIR_SETS * mt * 100, 0),
            "มัธยฐานเท่า": q(statistics.median(per), 1),
            "มัธยฐานชุด": q(PAIR_SETS * (srt[14] + srt[15]) / 2, 0),
            "ต่ำสุดชุด": q(PAIR_SETS * srt[0], 0), "สูงสุดชุด": q(PAIR_SETS * srt[-1], 0),
            "ไม่มีที่ว่าง": nocap, "ต่ำกว่าครึ่ง": lo_n, "เกินสองเท่า": hi_n, "โลก": len(SEEDS),
            "ไม้ต่อปี": q(trades / len(SEEDS), 1), "ขอบต่อปี": q(GG / len(SEEDS), 2),
            "sdนิ่ง": q(0.5 / math.sqrt(1 - 0.81), 2)}


def _monthly(inst):
    """รายได้ funding carry รายเดือน (เดือนละ 30 วัน · % ของมูลค่าที่ถือ) ช่วงเลือก 24 เดือน + ช่วงตรวจ 12 เดือน"""
    out, rounds = [], []
    for sp in ("formation", "validation"):
        by = defaultdict(float)
        rs = load_funding(sp, instrument=inst)
        for ts, _, rate in rs:
            by[ts[:10]] += rate
        rounds.append([r for _, _, r in rs])
        d = [by[k] for k in sorted(by)]
        out.append([100 * sum(d[i:i + MONTH]) for i in range(0, len(d) - MONTH + 1, MONTH)])
    return out[0], out[1], rounds[0], rounds[1]


def _block(xs, q):
    m, s = S.mean(xs), S.sd(xs)
    return {"n": len(xs), "Mean": q(m, 2), "SD": q(s, 2), "SE": q(s / math.sqrt(len(xs)), 2), "_m": m, "_s": s}


def _ratio(a, b, q):
    """ผลต่างของ Mean ÷ SE ของผลต่าง · คิดจากเลขปัดบนหน้า (Mean · SE สองตำแหน่ง) ให้ผู้อ่านคิดตามได้ตรง"""
    diff = float(b["Mean"]) - float(a["Mean"])
    se = float(q(math.sqrt(float(a["SE"]) ** 2 + float(b["SE"]) ** 2), 2))
    return {"ผลต่าง": q(diff, 2), "SEผลต่าง": q(se, 2), "อัตราส่วน": q(diff / se, 2),
            "SEกำลังสองรวม": q(float(a["SE"]) ** 2 + float(b["SE"]) ** 2, 4)}


def _rounds(rs, q):
    return {"รอบ": len(rs), "ติดลบเปอร์เซ็นต์": q(100 * sum(r < 0 for r in rs) / len(rs), 0),
            "เกินเปอร์เซ็นต์": q(100 * sum(r > SPIKE for r in rs) / len(rs), 1),
            "ต่อปีเปอร์เซ็นต์": q(100 * S.mean(rs) * 3 * 365, 1)}


def _decay_hand(q):
    h1, h2 = _block(HALF1, q), _block(HALF2, q)
    rows = []
    for name, xs, blk in (("ครึ่งแรก", HALF1, h1), ("ครึ่งหลัง", HALF2, h2)):
        dev = [x - blk["_m"] for x in xs]
        rows.append({"ชื่อ": name, "ผล": xs, "รวม": q(sum(xs), 1), "Mean": blk["Mean"], "ห่าง": [q(d, 1) for d in dev],
                     "ห่างกำลังสอง": [q(d * d, 2) for d in dev], "รวมห่างกำลังสอง": q(sum(d * d for d in dev), 2),
                     "Var": q(S.var(xs), 2), "SD": blk["SD"], "SE": blk["SE"]})
    se1 = q(float(h1["SD"]) / math.sqrt(6), 2)                          # จากเลขปัดบนหน้า
    se_diff = q(float(se1) * float(q(math.sqrt(2), 2)), 2)
    ratio = q(abs(h2["_m"] - h1["_m"]) / float(se_diff), 2)
    # เดือนที่ต้องมีต่อครึ่ง ถ้าจะให้ผลต่าง 0.3 ถึงเส้น 2 SE (σ 0.71): n ≥ 8σ²/Δ²
    need = 8 * float(h1["SD"]) ** 2 / (h1["_m"] - h2["_m"]) ** 2
    return {"แถว": rows, "รากหก": q(math.sqrt(6), 2), "รากสอง": q(math.sqrt(2), 2), "SE": se1, "SEผลต่าง": se_diff, "ผลต่าง": q(h1["_m"] - h2["_m"], 2),
            "อัตราส่วน": ratio, "เส้น": 2, "ต่อครึ่งต้องมี": q(need, 0), "รวมต้องมี": q(2 * need, 0),
            "SEกำลังสอง": q(float(se1) ** 2, 2), "สองเท่าSEกำลังสอง": q(2 * float(se1) ** 2, 2),
            "ผลต่างสองเท่าSE": q(2 * float(se_diff), 2)}


def _decay_real(q):
    out, mon = {}, {}
    for coin, inst in (("BTC", "BTC-PERPETUAL"), ("ETH", "ETH-PERPETUAL")):
        f, v, rf, rv = _monthly(inst)
        mon[coin] = (f, v)
        y1, y2, y3, fa = _block(f[:12], q), _block(f[12:], q), _block(v, q), _block(f, q)
        n1 = len(rf) // 2
        out[coin] = {"ปี1": {k: y1[k] for k in ("n", "Mean", "SD", "SE")},
                     "ปี2": {k: y2[k] for k in ("n", "Mean", "SD", "SE")},
                     "ปี3": {k: y3[k] for k in ("n", "Mean", "SD", "SE")},
                     "ช่วงเลือก": {k: fa[k] for k in ("n", "Mean", "SD", "SE")},
                     "ปี2เทียบปี1": _ratio(y1, y2, q), "ปี3เทียบช่วงเลือก": _ratio(fa, y3, q),
                     "ปี3เทียบปี2": _ratio(y2, y3, q),
                     "ปี3ต่อช่วงเลือกเปอร์เซ็นต์": q(100 * y3["_m"] / fa["_m"], 0),
                     "รอบ": {"ปี1": _rounds(rf[:n1], q), "ปี2": _rounds(rf[n1:], q), "ปี3": _rounds(rv, q)},
                     "เดือนช่วงตรวจ": [q(x, 2) for x in v], "เดือนช่วงเลือก": [q(x, 2) for x in f],
                     "รวมช่วงตรวจ": q(sum(v), 2)}
    return out, mon


def _decay_sim(q):
    """🎲 24 เดือน (ช่วงเลือก) + 12 เดือน (ช่วงตรวจ) · ขอบไม่หาย / หายครึ่ง · นับโลกที่อัตราส่วน ≤ −2"""
    res = {}
    for name, mu2 in (("ไม่หาย", SIM_MU), ("หายครึ่ง", SIM_MU / 2)):
        hits, ratios, drop = 0, [], []
        for s in SEEDS:
            rng = random.Random(1500 + s)
            f = [rng.gauss(SIM_MU, SIM_SD) for _ in range(24)]
            v = [rng.gauss(mu2, SIM_SD) for _ in range(12)]
            a, b = _block(f, q), _block(v, q)
            se = math.sqrt(a["_s"] ** 2 / 24 + b["_s"] ** 2 / 12)
            rt = (b["_m"] - a["_m"]) / se
            ratios.append(rt)
            hits += rt <= -2
            drop.append(100 * b["_m"] / a["_m"] if a["_m"] > 0 else 0.0)
        srt = sorted(drop)
        res[name] = {"เห็น": hits, "โลก": len(SEEDS), "อัตราส่วนมัธยฐาน": q(statistics.median(ratios), 2),
                     "ปี3ต่อช่วงเลือกมัธยฐาน": q((srt[14] + srt[15]) / 2, 0),
                     "ต่ำกว่าสี่สิบเปอร์เซ็นต์": sum(1 for d in drop if d < 40)}
    return res


def _funnel(cum_path, mu, sd):
    """คืนเดือนแรกที่ผลรวมสะสมต่ำกว่าเส้นเตือน (1 SD) และเส้นลงมือ (2 SD) · None = ไม่ต่ำกว่าเลย"""
    warn = act = None
    for n, c in enumerate(cum_path, start=1):
        if warn is None and c < n * mu - sd * math.sqrt(n):
            warn = n
        if act is None and c < n * mu - 2 * sd * math.sqrt(n):
            act = n
    return warn, act


def _track_hand(q):
    rows, cum = [], 0.0
    for n, x in enumerate(LIVE6, start=1):
        cum += x
        root = float(q(math.sqrt(n), 2))
        one = float(q(SD_T * root, 2))
        rows.append({"เดือน": n, "ผล": x, "สะสม": q(cum, 1), "คาด": q(n * MU_T, 1), "ราก": q(root, 2),
                     "SDสะสม": q(one, 2), "เตือน": q(n * MU_T - one, 2),
                     "ลงมือ": q(n * MU_T - 2 * one, 2), "สองSDสะสม": q(2 * one, 2),
                     "ต่ำกว่าคาด": q(n * MU_T - cum, 1)})
    warn, act = _funnel([sum(LIVE6[:k]) for k in range(1, 7)], MU_T, SD_T)
    need = []
    for name, d in (("หายครึ่ง", MU_T / 2), ("หายหมด", MU_T), ("กลับทิศ", 2 * MU_T)):
        need.append({"ชื่อ": name, "Δ": q(d, 1), "สองσหารΔ": q(2 * SD_T / d, 2), "เดือน": q((2 * SD_T / d) ** 2, 1),
                     "เดือนปัด": math.ceil((2 * SD_T / d) ** 2 - 1e-9)})
    return {"แถว": rows, "μ": MU_T, "σ": SD_T, "เตือนเดือน": warn, "ลงมือเดือน": act, "ต้องรอ": need,
            "สองσ": q(2 * SD_T, 1), "เดือนหกขาด": q(6 * MU_T - sum(LIVE6), 1)}


def _track_real(q, mon):
    out = {}
    for coin in ("BTC", "ETH"):
        f, v = mon[coin]
        mu, sd = float(q(S.mean(f), 2)), float(q(S.sd(f), 2))          # เลขปัดบนหน้า (μ · σ จากช่วงเลือก)
        vr = [float(q(x, 2)) for x in v]
        cum, rows = 0.0, []
        for n, x in enumerate(vr, start=1):
            cum += x
            rt = float(q(math.sqrt(n), 2))
            one = float(q(sd * rt, 2))
            rows.append({"เดือน": n, "ผล": q(x, 2), "สะสม": q(cum, 2), "คาด": q(n * mu, 2), "ราก": q(rt, 2),
                         "SDสะสม": q(one, 2), "สองSDสะสม": q(2 * one, 2),
                         "เตือน": q(n * mu - one, 2), "ลงมือ": q(n * mu - 2 * one, 2)})
        path = [sum(vr[:k]) for k in range(1, len(vr) + 1)]
        warn = next((r["เดือน"] for r, c in zip(rows, path) if c < r["เตือน"]), None)
        act = next((r["เดือน"] for r, c in zip(rows, path) if c < r["ลงมือ"]), None)
        assert (warn, act) == _funnel([sum(v[:k]) for k in range(1, len(v) + 1)], S.mean(f), S.sd(f))
        d = mu - float(q(S.mean(v), 2))
        out[coin] = {"μ": q(mu, 2), "σ": q(sd, 2), "แถว": rows, "เตือนเดือน": warn, "ลงมือเดือน": act,
                     "ช่วงตรวจMean": q(S.mean(v), 2), "Δ": q(d, 2),
                     "ต้องรอ": q((2 * sd / d) ** 2, 0) if d > 0 else None,
                     "ปลายสะสม": q(path[-1], 2), "ปลายคาด": rows[-1]["คาด"], "ปลายลงมือ": rows[-1]["ลงมือ"],
                     "ปลายเตือน": rows[-1]["เตือน"], "ปลายบน": q(rows[-1]["คาด"] + rows[-1]["สองSDสะสม"], 2),
                     "สองSDราก12": rows[-1]["สองSDสะสม"], "ราก12": rows[-1]["ราก"],
                     "สองσ": q(2 * sd, 2), "สองσหารΔ": q(2 * sd / d, 2) if d > 0 else None,
                     "เหนือลงมือ": q(path[-1] - float(rows[-1]["ลงมือ"]), 2),
                     "ครึ่งΔ": q(mu / 2, 2), "ครึ่งสองσหารΔ": q(2 * sd / float(q(mu / 2, 2)), 2),
                     "ครึ่งต้องรอ": q((float(q(2 * sd / float(q(mu / 2, 2)), 2))) ** 2, 1)}
    return out


def _track_sim(q):
    """🎲 36 เดือนจริงหลัง backtest ที่รู้ μ 0.6 σ 0.7 · เดือนแรกที่ต่ำกว่าเส้นเตือน / เส้นลงมือ · 30 โลกต่อแบบ"""
    res = {}
    for name, mu2 in (("ไม่เปลี่ยน", SIM_MU), ("หายครึ่ง", SIM_MU / 2), ("หายหมด", 0.0), ("กลับทิศ", -SIM_MU)):
        warns, acts = [], []
        for s in SEEDS:
            rng = random.Random(2500 + s)
            v = [rng.gauss(mu2, SIM_SD) for _ in range(36)]
            path = [sum(v[:k]) for k in range(1, 37)]
            w, a = _funnel(path, SIM_MU, SIM_SD)
            warns.append(w)
            acts.append(a)

        def med(xs):
            ys = sorted(x if x is not None else 99 for x in xs)
            m = (ys[14] + ys[15]) / 2
            return None if m >= 99 else q(m, 1)
        res[name] = {"เตือนมัธยฐาน": med(warns), "ลงมือมัธยฐาน": med(acts),
                     "เตือนใน12": sum(1 for x in warns if x is not None and x <= 12),
                     "ลงมือใน12": sum(1 for x in acts if x is not None and x <= 12),
                     "ลงมือใน36": sum(1 for x in acts if x is not None),
                     "ไม่ลงมือใน36": sum(1 for x in acts if x is None)}
    return res


def extend(data, D, q):
    f1 = SB.load_figures("sab")
    acct = f1["บัญชีมิน"]
    assert float(acct["ค่าธรรมเนียม"]["taker"]) == FEE_PCT and float(acct["ค่าธรรมเนียม"]["maker"]) == 0.02
    assert float(f1["_สมมติฐาน"]["กระดานสมมติ"][0][0]) == HALF_SPREAD_PCT
    cap1 = f1["ch16"]["v2"]["capacity"]
    v1 = {"ขยาย20เท่าเส้นตรง": cap1["ขยาย20เท่าถ้าเส้นตรง"], "ขยาย20เท่าจริง": [r for r in cap1["ตาราง"] if r["ขนาดต่อขา"] == 20000][0]["ต่อไม้_หลัก"],
          "ชั้นแรกเปอร์เซ็นต์": HALF_SPREAD_PCT, "ชั้นแรกดอลลาร์": f1["_สมมติฐาน"]["กระดานสมมติ"][0][1],
          "taker": FEE_PCT, "maker": 0.02, "ทุนคู่": 1000}

    hand = _hand(q, f1)
    pair = _real_pair(q)
    sim_cap = _sim_capacity(q)
    dhand = _decay_hand(q)
    dreal, mon = _decay_real(q)
    fcap = {c: _real_funding_capacity(q, mon[c][1]) for c in ("BTC", "ETH")}
    dsim = _decay_sim(q)
    thand = _track_hand(q)
    treal = _track_real(q, mon)
    tsim = _track_sim(q)

    consts = {"ค่าธรรมเนียม": FEE_PCT, "ครึ่งspread": HALF_SPREAD_PCT, "spreadเต็ม": q(2 * HALF_SPREAD_PCT, 2),
              "เลื่อนต่อพัน": SLIDE_PER_1000, "เฉลี่ยต่อพัน": AVG_PER_1000, "fill": FILLS, "ขอบ": EDGE_PCT,
              "เส้นตรงต่อfill": q(FEE_PCT + HALF_SPREAD_PCT, 2), "เกินรอบ": q(SPIKE * 100, 2), "เดือนวัน": MONTH,
              "ปีชุดข้อมูล": ["2022", "2023", "2024", "2025"], "การ์ด": {"h": PAIR_H, "ชุด": PAIR_SETS, "เข้า": 2, "ออก": 0.5, "ถือ": 30},
              "โลก": {"μ": SIM_MU, "σ": SIM_SD, "เดือนเลือก": 24, "เดือนตรวจ": 12, "เดือนจริง": 36}}
    consts["ต่อหน่วย"] = {"ต่อดอลลาร์ล้าน": 10000000, "ห้าสิบหกจุดสองห้า": q(7.5 ** 2, 2), "หนึ่งในพัน": 0.001,
                          "วันต่อปี": 365, "ยอดmakerพัน": q(11.5, 1), "สิบสองเท่าSD": q(12 * float(treal["BTC"]["σ"]), 2),
                          "ตัวอย่างVar": q(S.var(HALF1), 3), "Δกำลังสอง": q(0.09, 2), "ต่อครึ่งแม่น": q(8 * S.var(HALF1) / 0.09, 1),
                          "สิบสองกำลังสอง": 144}
    looks = {"ดูช่วงตรวจ_บทนี้": 2, "รายการ": ["การ์ด LTC–DOT ของบท 7 (ไม่เลือกค่าใหม่)", "funding carry BTC/ETH ของบท 12 (รายปี + แผนภูมิควบคุม)"]}

    # กล่อง 🧰 (ที่มา: tools/sab_research/practitioner-research.md §0 §1.2 §5 §7 · ตัวเลขตามที่บันทึกไว้ ไม่ได้คำนวณ)
    prac = {"ปีDF10": "2010", "DFไม่บรรจบ": 32, "DFอธิบายการลด": 70, "ปีDF12": "2012", "DFหลังปี": "2002",
            "ปีRad": "2016", "Radปีเริ่ม": "1962", "Radปีจบ": "2014", "Radก่อน": [91, 85, 43], "Radหลัง": [38, 33, 5],
            "ปีโอกาสลด": "2009", "ปีCK": "2018", "CKปีเริ่ม": "2010", "CKปีจบ": "2015", "CKต่อปี": 12,
            "ปีFil": "2020", "Filเหรียญ": 26, "Filรายวัน": -0.07, "Filห้านาที": 11.61, "Filนาที": 5,
            "ปีPindza": "2026", "Pindzaตัว": 10, "Pindzaต้นทุน": 0.08, "ปีKL": "2011", "KLปีเหตุ": "2007",
            "ปีFischer": "2019", "Fischerเหรียญ": 40, "Fischerต่อวัน": 7.1, "Fischerต้นทุน": 15}

    drills = [
        {"โจทย์": "(ทำตาม) ขาละ 5,000: ต้นทุนสามชั้นต่อ fill สี่ fill และกำไรสุทธิต่อไม้", "คำตอบ": hand["แบบฝึก"]["ข้อ1"]["สุทธิ"]},
        {"โจทย์": "(เปลี่ยนเลข) ราคาเลื่อนเร็วขึ้นสองเท่า: จุดสูงสุด กำไรที่จุดนั้น และจุดคุ้มทุน", "คำตอบ": hand["แบบฝึก"]["ข้อ2"]["จุดสูงสุด"]},
        {"โจทย์": "(เปลี่ยนเงื่อนไข) ใช้คำสั่งตั้งรอ maker 0.02% ไม่จ่ายครึ่ง spread: จุดสูงสุดและจุดคุ้มทุน", "คำตอบ": hand["แบบฝึก"]["ข้อ3"]["จุดสูงสุด"]},
        {"โจทย์": "(ตัดสินใจ) หกเดือนจริงยังอยู่เหนือเส้นลงมือ ต้นบอกให้เพิ่มขนาดสองเท่า", "คำตอบ": thand["ต้องรอ"][0]["เดือน"]},
        {"โจทย์": "(ถ่ายโอน · ข้อมูลจริง) funding carry BTC ช่วงตรวจ 12 เดือนเทียบแผนภูมิจากช่วงเลือก", "คำตอบ": treal["BTC"]["ปลายสะสม"]},
    ]
    consts["แกนรอ"] = {"x": [0, 6, 12, 18, 24], "y": [0, 2, 4, 6, 8]}   # กราฟ sab2-wait-curve
    return {"_แบบฝึก": drills, "ค่า": consts, "เล่ม1": v1, "มือ": hand, "คู่จริง": pair, "fundingขนาด": fcap,
            "โลกขนาด": sim_cap, "เสื่อมมือ": dhand, "เสื่อมจริง": dreal, "เสื่อมโลก": dsim,
            "ติดตามมือ": thand, "ติดตามจริง": treal, "ติดตามโลก": tsim, "ดูช่วงตรวจ": looks, "คนทำงานจริง": prac}
