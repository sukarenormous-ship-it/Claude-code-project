#!/usr/bin/env python3
"""ห้องทดลองของตอนที่ 4 — "อ่านกราฟ ε กับเส้น VaR: จากกราฟสู่กฎเทรด" (สไลด์ 6–7)

ทุกตัวเลขมาจากข้อมูลจำลองที่ "รู้เฉลย" (sas_core.demo_pair / make_pair) ไม่มีข้อมูลตลาดจริง
คู่ตัวอย่าง (good / fake / break) ถูกเลือกให้เห็นอาการชัด — ข้อสรุปทั่วไปให้ดูค่าเฉลี่ยหลายร้อยโลกเสมอ

การทดลอง (คีย์ใน figures() ใช้ชื่อในวงเล็บ)
  4a (zones)      กราฟโซนแบบสไลด์ 6–7: ε = Y − α̂ − β̂·X ของทั้ง 1,500 แท่ง โดย α̂, β̂ ประมาณจาก 750 แท่งแรก
                  เส้นเปอร์เซ็นไทล์ 1, 10, …, 90, 99 คิดจากข้อมูล "ทั้งช่วง" เหมือนในสไลด์ (= รู้อนาคต)
                  ตัวเลข: ค่าของแต่ละเส้น · จำนวนครั้งที่ตัดเส้นกลาง · การออกนอกเส้น 10/90 แต่ละครั้งนานแค่ไหน
  4b (stability)  โซนของครึ่งแรกเทียบครึ่งหลัง (หน่วย = sd ของครึ่งแรก) บนคู่ตัวอย่าง + 2,000 โลก good / fake
  4c (lookahead)  กฎ "short เหนือ P90 · long ใต้ P10 · ออกที่ P50" บน ε เส้นเดียวกัน ต่างกันที่เส้นแบ่งโซน:
                  (i) ทั้งช่วง — รู้อนาคต (ii) expanding — ทุกแท่งตั้งแต่ต้นถึงวันนี้ (iii) rolling 250 แท่งล่าสุด
                  นับผลเฉพาะ 750 แท่งหลัง (ช่วงที่ β̂ ไม่เคยเห็น) → สิ่งเดียวที่มองอนาคตคือเส้นของแบบ (i)
                  คู่ตัวอย่าง + 500 โลก good / 500 โลก fake
  (trade)         แกะหนึ่งไม้จากคู่ good ทีละบรรทัด + สูตร "หนึ่งรอบได้ราว (entry − exit)·σ/(1+β)"
  4d (threshold)  500 โลก good · walk-forward · entry 0.5–3 · exit 0 · c = 0 / 5 / 20 / 50 bps:
                  ไม้ต่อปี · กำไรต่อไม้ · ผลตอบแทนต่อปี · Sharpe  และรอบ "ถ้ารู้ค่าจริง" (threshold.known)
                  ที่ใช้ α, β, μ, σ จริง เพื่อเทียบกับสูตรในหน่วย σ จริง
  4e (exits)      entry 2 · ออกที่ z = 0 / ออกก่อนที่ 0.5 / รอถึงแถบตรงข้าม (−2 = กลับข้างทันที)
  4f (stops)      stop ∈ {ไม่มี, 4, 3} × จำกัดเวลาถือ ∈ {ไม่มี, 3 เท่าของ half-life = 36 แท่ง}
                  โลก good 500 โลก (ชุดเดียวกับ 4d) กับโลก break 1,000 โลก (สายจูงขาด ณ แท่งสุ่ม 500–1,249)
                  ไม้บรรทัดสองแบบบนโลกชุดเดียวกัน นับผลช่วงเดียวกัน (แท่ง 500–1,499 ราว 4 ปี):
                  walk-forward ที่ประมาณใหม่ทุก 21 แท่ง (stops.wf) กับไม้บรรทัดตายตัวที่ประมาณครั้งเดียวจาก
                  500 แท่งแรก (stops.fixed) — ผลของ stop ต่างกันมากระหว่างสองแบบ
  4g (pierce)     เมื่อ |z| แตะ 2.5 ครั้งแรก: กลับเข้ามาใน |z| < 0.5 ภายใน 36 แท่งบ่อยแค่ไหน (วัดด้วยไม้บรรทัด
                  ณ วันที่แตะ ไม่ขยับตาม) และผลตอบแทน 12 แท่งข้างหน้าแยกตามระดับ |z| — good เทียบ break

ข้อตกลงของตอนนี้
  • สถานะที่ตัดสินใจตอนสิ้นแท่ง t เริ่มรับผลแท่ง t+1 (lag = 1) · ตัวเลข Sharpe หลักมี lag = 2 ประกบ
  • z ของ walk-forward วัดด้วย σ ที่ประมาณจากช่วง train 250 แท่ง ไม่ใช่ σ จริง (ดู threshold.z_sd)
    จึงห้ามเรียกเกณฑ์ entry = 2 ว่า "2σ" — ค่าที่วัดได้จริงอยู่ที่ threshold.<e…>.true_sigma_at_entry
  • ผลตอบแทนคิดต่อเงินรวมสองขา (1 + |β|) · ต้นทุน c ต่อขาต่อเที่ยว · ครบรอบเสีย 2c
  • ตัวแปรที่ "ตั้งใจมองอนาคต" มีแค่ตัวเดียวและตั้งชื่อบอกไว้: lines_lookahead ใน _zone_lines (4c)

ความแม่นของตัวเลข Monte Carlo (ตรวจแล้วด้วยการรันซ้ำบนชุดโลกอื่น)
  จำนวนทศนิยมที่เก็บถูกเลือกให้หลักสุดท้ายแทบไม่ขยับเมื่อเปลี่ยนชุดโลก: ผลรวมเป็น % เต็ม · Sharpe ทศนิยม
  หนึ่งตำแหน่ง · ค่าปลาย (เปอร์เซ็นไทล์ 5 · tail10 = ค่าเฉลี่ยของ 10% ของโลกที่แย่ที่สุด) ยังแกว่งได้ราว
  ±2 จุด → ใช้เทียบระหว่างกฎบนโลกชุดเดียวกัน ไม่ใช่ค่าที่แม่นตัวต่อตัว
  ตัวเลขของคู่ตัวอย่างเส้นเดียว (zones, stability.<คู่>, lookahead.<คู่>, trade) เป็นค่าที่แน่นอนของเส้นนั้น
  จึงเก็บทศนิยมมากกว่า — แต่เป็นแค่ภาพประกอบ ไม่ใช่ค่าทั่วไป

วิธีรัน
    python3 tools/sas_exp4.py          # พิมพ์สรุปตัวเลขสำคัญ (ราว 50 วินาที)
ใช้จากโค้ด
    import sas_exp4 as E
    res = E.run()              # คำนวณทั้งหมด (เก็บผลไว้ เรียกซ้ำไม่คิดใหม่)
    E.figures()["threshold"]   # ตัวเลขที่ปัดแล้ว พร้อมลงในบท → data-f="p4.threshold.…"
    E.charts()                 # {"sas-p4-…": html}

คีย์ของ figures()  (หน่วยอยู่ท้ายชื่อคีย์: _pct, _bps, _bars, _sigma · ไม่มีหน่วย = ตัวเลขเปล่า เช่น Sharpe, z)
    about.<common|zones|stability|lookahead|trade|threshold|known|exits|stops|pierce|precision>   ข้อความบอกการตั้งค่า
    settings.*                         ค่าตั้งต้นร่วม (จำนวนแท่ง · train · ต้นทุน · จำนวนโลก · ค่าจริงของโลก good)
    zones.<good|bad|break>.*           alpha · beta · sigma_train_pct · p1_pct … p99_pct · width_p1_p99_pct · crossings
                                       bars_per_crossing · longest_one_side_bars · outside_10_90_pct · visits
                                       visit_longest_bars · visit_median_bars · last_pct · last_rank_pct
    zones.break.*                      break_bar · pre_p1_pct … pre_p99_pct (เส้นจาก 750 แท่งแรก) · first_pierce_bar
                                       before_beyond_1_99_pct · after_beyond_1_99_pct · last_middle_bar
    stability.<good|bad|break>.*       first_p10_sigma … second_p90_sigma · shift_p50_sigma · width_ratio
                                       second_outside_pct
    stability.mc.<good|bad>.*          worlds · shift_abs_p50/p5/p95_sigma · width_ratio_p50/p5/p95
                                       second_outside_p50/p5/p95_pct
    lookahead.<good|bad>.<full|expanding|rolling>.<c0|c5>.*   total_pct · sharpe · trades · max_dd_pct · open_at_end
    lookahead.<good|bad>.<…>.c5.sharpe_lag2 · total_lag2_pct
    lookahead.mc.<good|bad>.<full|expanding|rolling>.*        total_mean_pct · total_mean_pm95_pct (± ของค่าเฉลี่ย)
                                       total_p5/p50/p95_pct · profitable_pct · sharpe_mean · sharpe_lag2_mean
                                       trades_mean · total_c0_mean_pct
    lookahead.mc.<good|bad>.gap_full_minus_expanding_pct · full_beats_expanding_pct   ส่วนที่มาจากการรู้อนาคตของเส้น
    trade.*                            ไม้ตัวอย่าง: entry_bar · exit_bar · bars_held · side · z_entry · z_exit
                                       eps_entry_pct · eps_exit_pct · dy_pct · dx_pct · gross_pct · formula_pct
                                       cost_pct · net_pct  + ภาพรวมครึ่งหลังของคู่ good: trades · gross_avg_pct
                                       formula_avg_pct · hit_rate_pct · total_net_pct · z_sd_test
    threshold.<e0_5|e1|e1_5|e2|e2_5|e3>.*    entry_z · true_sigma_at_entry · trades_per_year · hold_bars
                                       in_market_pct · gross_per_trade_pct
    threshold.<e…>.<c0|c5|c20|c50>.*   net_per_trade_pct · ann_return_pct (+ _p5/_p95) · sharpe (+ _p5/_p95)
                                       profitable_pct      (c5 มี sharpe_lag2 · ann_return_lag2_pct เพิ่ม)
    threshold.best.<c0|c5|c20|c50>.*   entry_by_return · ann_return_pct · entry_by_sharpe · sharpe
                                       (entry_by_* เป็นข้อความ: "1" หรือช่วง "0.5–1" เมื่อสูสีจนแยกไม่ออก)
    threshold.known.<e…>.*             formula_pct · gross_per_trade_pct · z_in · z_out · trades_per_year
                                       ann_return_c0_pct · ann_return_c5_pct · sharpe_c5
    threshold.worlds · z_sd · z_sd_p5 · z_sd_p95
    exits.<x0|x0_5|flip>.*             exit_z · trades_per_year · hold_bars · in_market_pct · gross_per_trade_pct
    exits.<…>.<c0|c5|c20|c50>.*        เหมือน threshold
    stops.<wf|fixed>.<good|break>.worlds
    stops.<wf|fixed>.<good|break>.<none|s4|s3|t36|s4_t36|s3_t36>.*
                                       wf = ไม้บรรทัด walk-forward · fixed = ไม้บรรทัดตายตัวจาก 500 แท่งแรก
                                       sharpe_mean · sharpe_lag2_mean · total_mean/p5/p50/p95_pct · tail10_pct
                                       max_dd_mean_pct · worst_trade_p5_pct · hit_rate_pct · trades_per_year
                                       (ยกเว้น none:) diff_vs_none_pct · beats_none_pct · none_tail_pct · none_tail_helps_pct
                                       (break มี after_break_mean_pct ด้วย)
    pierce.<good|break_before|break_after>.*   events · back_pct · back_12_pct · back_24_pct · bars_to_back_median
                                       gross_mean_pct · gross_p5_pct · losing_pct
    pierce.forward.<good|break_after>.<z1_2|z2_3|z3_4|z4_up>.*    mean_pct · p5_pct · p95_pct · losing_pct · bars
"""
import bisect
import functools
import math

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

import sas_core as C
import sas_svg as V

# ───────────────────────── ค่าตั้งต้นของตอนนี้ ─────────────────────────

N = 1500                        # แท่งต่อโลก (≈ 6 ปี)
TRAIN = N // 2                  # 750 แท่งแรก: ประมาณ α̂, β̂ ของกราฟโซน (ค่าเดียวกับตอนที่ 3)
WF_TRAIN, WF_REFIT = 250, 21    # walk-forward ของ 4d–4g: ประมาณจาก 250 แท่งล่าสุด ทุก 21 แท่ง
COST = 0.0005                   # c = 5 bps ต่อขา ต่อเที่ยว
YEAR = C.DAYS_PER_YEAR
BETA, HL, SIGMA = 1.4, 12.0, 0.03          # ค่าจริงของโลก good (ค่าตั้งต้นของ make_pair)

# จำนวนโลกถูกเลือกจากความแม่นที่ต้องการ (ตรวจด้วยการเปลี่ยน seed): ค่าปลายของโลก break แกว่งมากที่สุด
WORLDS = 500                    # โลก good ของ 4c–4g และโลก fake ของ 4c
WORLDS_BREAK = 1000             # โลก break ของ 4f–4g
WORLDS_ZONE = 2000              # 4b คำนวณเร็ว (500 โลกแรกคือชุดเดียวกับ 4c)
SEED_GOOD, SEED_FAKE, SEED_BREAK = 420, 411, 430
TAIL = 0.10                     # "ปลายล่าง" = 10% ของโลกที่ผลรวมแย่ที่สุด

PCTS = (1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 99)    # เส้นของสไลด์ 6–7
ZONE_Q = (10, 50, 90)           # เส้นที่กฎของ 4c ใช้: long ใต้ P10 · ออกที่ P50 · short เหนือ P90
MIN_BARS, ROLL = 250, 250       # expanding ต้องมีอย่างน้อย 250 แท่ง · rolling ใช้ 250 แท่งล่าสุด
VARIANTS = ("full", "expanding", "rolling")

ENTRIES = (0.5, 1.0, 1.5, 2.0, 2.5, 3.0)
COSTS = (0.0, 0.0005, 0.002, 0.005)       # 0 / 5 / 20 / 50 bps
ENTRY, EXIT = 2.0, 0.0          # กฎหลักของ 4e–4g
EXIT_RULES = (("x0", 0.0), ("x0_5", 0.5), ("flip", -2.0))
MAX_HOLD = int(3 * HL)          # จำกัดเวลาถือ = 3 เท่าของ half-life จริง = 36 แท่ง
STOP_RULES = (("none", None, None), ("s4", 4.0, None), ("s3", 3.0, None),
              ("t36", None, MAX_HOLD), ("s4_t36", 4.0, MAX_HOLD), ("s3_t36", 3.0, MAX_HOLD))
BREAK_FROM, BREAK_TO = 500, 1250           # โลก break: สายจูงขาด ณ แท่งสุ่มในช่วงนี้ (เหลือหลังขาด ≥ 250 แท่ง)
FIX_TRAIN = BREAK_FROM          # ไม้บรรทัดตายตัวของ 4f: ประมาณครั้งเดียวจาก 500 แท่งแรก (ก่อนสายจูงขาดเสมอ)
STOP_FROM = FIX_TRAIN           # 4f: ไม้บรรทัดทั้งสองแบบเริ่มเทรดที่แท่งนี้ → เทียบกันบนช่วงเดียวกัน
PIERCE, INSIDE = 2.5, 0.5       # 4g: แตะ |z| ≥ 2.5 แล้วดูว่ากลับเข้า |z| < 0.5 หรือไม่
FWD = int(HL)                   # มองไปข้างหน้า 12 แท่ง (หนึ่ง half-life)
BUCKETS = (("z1_2", 1.0, 2.0), ("z2_3", 2.0, 3.0), ("z3_4", 3.0, 4.0), ("z4_up", 4.0, math.inf))

WF_YEARS = (N - WF_TRAIN) / YEAR           # ช่วงทดสอบของ walk-forward (4d, 4e) ≈ 4.96 ปี
STOP_YEARS = (N - STOP_FROM) / YEAR        # ช่วงทดสอบของ 4f ≈ 3.97 ปี
STAT_KEYS = ("total", "ann_return", "sharpe", "max_dd", "n_trades", "hit_rate", "time_in_market")


# ───────────────────────── เครื่องมือเล็ก ๆ ที่ใช้ซ้ำ ─────────────────────────

def _spread_from_train(d):
    """ε ของทั้งช่วง วัดด้วยไม้บรรทัด (α̂, β̂) ที่ประมาณจาก TRAIN แท่งแรกเท่านั้น"""
    r = C.ols(d["y"][:TRAIN], d["x"][:TRAIN])
    a, b = float(r["coef"][0]), float(r["coef"][1])
    return a, b, d["y"] - a - b * d["x"]


def _run_lengths(mask):
    """ความยาว (จำนวนแท่ง) ของแต่ละช่วงที่ mask เป็นจริงติดกัน"""
    m = np.concatenate([[0], np.asarray(mask, int), [0]])
    edges = np.flatnonzero(np.diff(m))
    return edges[1::2] - edges[::2]


def _round_trips(pos):
    """ไม้ที่ปิดแล้วของอนุกรมสถานะ → (แท่งที่ตัดสินใจเข้า, แท่งที่ตัดสินใจออก, ฝั่ง)
    ไม้ที่ยังเปิดค้างตอนข้อมูลจบไม่ถูกนับ · กลับข้างทันที = ออกและเข้าในแท่งเดียวกัน"""
    prev = np.concatenate([[0.0], pos[:-1]])
    opens = np.flatnonzero((pos != 0) & (pos != prev))
    closes = np.flatnonzero((prev != 0) & (pos != prev))
    opens = opens[:len(closes)]
    return opens, closes, pos[opens]


def _dist(a):
    """ค่าเฉลี่ย + เปอร์เซ็นไทล์ 5 / 50 / 95 ของผลจากหลายโลก"""
    a = np.asarray(a, float)
    p5, p50, p95 = np.percentile(a, [5, 50, 95])
    return {"mean": float(a.mean()), "p5": float(p5), "p50": float(p50), "p95": float(p95)}


def _collect(stats):
    """รายการ perf_stats ของหลายโลก → อาร์เรย์ต่อหนึ่งตัวชี้วัด"""
    return {k: np.array([s[k] for s in stats], float) for k in STAT_KEYS}


def _pairs(kind, offset, n):
    """โลกจำลอง n โลกของแบบที่กำหนด (ตัวสุ่มเดียวต่อชุด → ทำซ้ำได้ · n โลกแรกเหมือนกันทุกครั้ง)"""
    g = C.rng(offset)
    return [C.make_pair(kind, N, g) for _ in range(n)]


def _break_pairs():
    """โลกที่สายจูงขาด ณ แท่งสุ่ม (ก่อนขาดเหมือนโลก good ทุกประการ)"""
    g = C.rng(SEED_BREAK)
    out = []
    for _ in range(WORLDS_BREAK):
        bar = int(g.integers(BREAK_FROM, BREAK_TO))
        out.append(C.make_pair("break", N, g, break_at=(bar + 0.5) / N))
    return out


# ───────────────────────── 4a / 4b: กราฟโซนและความนิ่งของโซน ─────────────────────────

def _zone_stats(eps):
    """สิ่งที่ตาเห็นในกราฟโซน แปลงเป็นตัวเลข (เส้นเปอร์เซ็นไทล์คิดจากทั้งช่วง แบบในสไลด์)"""
    pc = {q: float(np.percentile(eps, q)) for q in PCTS}
    above = eps > pc[50]
    crossings = int(np.sum(above[1:] != above[:-1]))
    outside = (eps < pc[10]) | (eps > pc[90])
    visits = _run_lengths(outside)
    return {
        "pcts": pc, "crossings": crossings, "bars_per_crossing": len(eps) / max(crossings, 1),
        "longest_one_side": int(max(_run_lengths(above).max(initial=0), _run_lengths(~above).max(initial=0))),
        "outside": float(outside.mean()), "visits": int(len(visits)),
        "visit_longest": int(visits.max(initial=0)), "visit_median": float(np.median(visits)) if len(visits) else 0.0,
        "last": float(eps[-1]), "last_rank": float(np.mean(eps <= eps[-1])),
    }


def _stability(eps):
    """โซน 10/50/90 ของครึ่งแรกเทียบครึ่งหลัง ในหน่วย sd ของครึ่งแรก"""
    first, second = eps[:TRAIN], eps[TRAIN:]
    sd = float(first.std(ddof=1))
    p1 = np.percentile(first, ZONE_Q)
    p2 = np.percentile(second, ZONE_Q)
    return {"first": p1 / sd, "second": p2 / sd, "shift": float((p2[1] - p1[1]) / sd),
            "width_ratio": float((p2[2] - p2[0]) / (p1[2] - p1[0])),
            "second_outside": float(np.mean((second < p1[0]) | (second > p1[2])))}


def _break_view(eps, break_index):
    """คู่ break: เส้นที่ "มีอยู่ในมือ" ก่อนสายจูงขาด (จาก TRAIN แท่งแรก) กับสิ่งที่ ε ทำหลังจากนั้น"""
    pre = {q: float(np.percentile(eps[:TRAIN], q)) for q in (1, 10, 50, 90, 99)}
    beyond = (eps < pre[1]) | (eps > pre[99])
    middle = np.flatnonzero((eps >= pre[10]) & (eps <= pre[90]))
    pierced = np.flatnonzero(beyond[break_index:])
    return {"pre": pre, "before_beyond": float(beyond[TRAIN:break_index].mean()),
            "after_beyond": float(beyond[break_index:].mean()),
            "first_pierce_bar": int(break_index + pierced[0]), "last_middle_bar": int(middle[-1])}


def _demo(kind):
    """คู่ตัวอย่าง + ε ที่วัดด้วย α̂, β̂ ของ 750 แท่งแรก + ตัวเลขของกราฟโซน"""
    d = C.demo_pair(kind)
    a, b, eps = _spread_from_train(d)
    out = {"y": d["y"], "x": d["x"], "alpha": a, "beta": b, "eps": eps,
           "sigma_train": float(eps[:TRAIN].std(ddof=1)), "break_index": d.get("break_index"),
           "zone": _zone_stats(eps), "stability": _stability(eps)}
    if out["break_index"] is not None:
        out["break_view"] = _break_view(eps, out["break_index"])
    return out


def exp_stability_mc(kind, offset):
    """4b บน WORLDS_ZONE โลก: โซนของครึ่งหลังเลื่อน/กว้างขึ้นจากครึ่งแรกแค่ไหน (สร้างทีละโลกแล้วทิ้ง)"""
    g = C.rng(offset)
    rows = [_stability(_spread_from_train(C.make_pair(kind, N, g))[2]) for _ in range(WORLDS_ZONE)]
    return {"shift_abs": np.array([abs(r["shift"]) for r in rows]),
            "width_ratio": np.array([r["width_ratio"] for r in rows]),
            "second_outside": np.array([r["second_outside"] for r in rows])}


# ───────────────────────── กฎแถบบนโลกหนึ่งโลก (ใช้ร่วมกันทุกการทดลองที่เทรด) ─────────────────────────

def _rule(w, lag=1, pos=None, **band):
    """กฎแถบหนึ่งชุดบน z ของโลกนั้น → ผลขั้นต้นรายแท่ง สถานะ และ turnover ของช่วงทดสอบ
    w = {y, x, z, beta, start} · เทรดเฉพาะแท่ง start เป็นต้นไป (ก่อนหน้านั้นว่างเสมอ)"""
    s = w["start"]
    if pos is None:
        pos = np.zeros(len(w["y"]))
        pos[s:] = C.band_positions(w["z"][s:], **band)
    gross, info = C.spread_pnl(w["y"], w["x"], w["beta"], pos, cost_per_leg=0.0, lag=lag)
    return {"pos": pos, "gross": gross[s:], "held": info["held"][s:], "turn": info["turnover"][s:]}


def _net(r, cost):
    """หักต้นทุน c × turnover แล้วสรุปผล (สถานะชุดเดียวกันทุกระดับต้นทุน)"""
    return C.perf_stats(r["gross"] - cost * r["turn"], r["held"], cost_per_leg=cost)


def _closed_trades(r, start):
    """ไม้ที่ปิดแล้ว (lag = 1): แท่งเข้า · แท่งออก · ผลขั้นต้นของแท่งเข้า+1 … แท่งออก"""
    opens, closes, _ = _round_trips(r["pos"])
    cs = np.concatenate([[0.0], np.cumsum(r["gross"])])
    return opens, closes, cs[closes - start + 1] - cs[opens - start + 1]


# ───────────────────────── 4c: เส้นแบ่งโซนที่รู้อนาคต ─────────────────────────

def _quantile_sorted(s, q):
    """เปอร์เซ็นไทล์ q ของลิสต์ที่เรียงแล้ว (ประมาณค่าเชิงเส้น — สูตรเดียวกับ np.percentile)"""
    pos = q / 100.0 * (len(s) - 1)
    k = int(pos)
    frac = pos - k
    return s[k] + frac * (s[k + 1] - s[k]) if frac else s[k]


def _lines_full(eps):
    """(i) เส้นจากข้อมูลทั้งช่วง แบบในสไลด์ — แต่ละแท่งใช้เส้นที่คิดจากอนาคตของตัวเองด้วย"""
    return np.repeat(np.percentile(eps, ZONE_Q)[:, None], len(eps), axis=1)


def _lines_expanding(eps, min_bars=MIN_BARS, start=0):
    """(ii) เส้น ณ แท่ง t คิดจากทุกแท่งตั้งแต่ต้นถึงแท่ง t (เก็บค่าที่เห็นแล้วเป็นลิสต์เรียงลำดับ)
    start = แท่งแรกที่ต้องการเส้น (ก่อนหน้านั้นเป็น NaN) — Monte Carlo ใช้เฉพาะช่วงที่เทรด"""
    out = np.full((len(ZONE_Q), len(eps)), np.nan)
    first = max(min_bars - 1, start)
    seen = sorted(float(v) for v in eps[:first])
    for t in range(first, len(eps)):
        bisect.insort(seen, float(eps[t]))
        out[:, t] = [_quantile_sorted(seen, q) for q in ZONE_Q]
    return out


def _lines_rolling(eps, window=ROLL, start=0):
    """(iii) เส้น ณ แท่ง t คิดจาก `window` แท่งล่าสุดที่จบที่แท่ง t"""
    out = np.full((len(ZONE_Q), len(eps)), np.nan)
    first = max(window - 1, start)
    out[:, first:] = np.percentile(sliding_window_view(eps[first - window + 1:], window), ZONE_Q, axis=1)
    return out


def _zone_signal(eps, lines):
    """แปลงตำแหน่งของ ε เทียบกับเส้น P10/P50/P90 เป็นสเกลเดียว: P50 → 0 · P90 → +1 · P10 → −1
    (กฎ "short เหนือ P90 · long ใต้ P10 · ออกที่ P50" จึงเขียนเป็นกฎแถบ entry = 1, exit = 0 ได้)"""
    lo, mid, hi = lines
    with np.errstate(invalid="ignore", divide="ignore"):
        u = np.where(eps >= mid, (eps - mid) / (hi - mid), (eps - mid) / (mid - lo))
    u[~np.isfinite(u)] = np.nan
    return u


def _zone_lines(eps, start=0):
    lines_lookahead = _lines_full(eps)          # ตัวเดียวในโมดูลนี้ที่ตั้งใจให้เห็นอนาคต
    return {"full": lines_lookahead, "expanding": _lines_expanding(eps, start=start),
            "rolling": _lines_rolling(eps, start=start)}


def _zone_test(d, eps, beta, lines):
    """เทรดตามเส้นโซนเฉพาะ TRAIN แท่งหลัง (ช่วงที่ β̂ ไม่เคยเห็น) → ผลที่ c = 0, 5 bps และ lag 2"""
    pos = np.zeros(len(eps))
    pos[TRAIN:] = C.band_positions(_zone_signal(eps[TRAIN:], lines[:, TRAIN:]), entry=1.0, exit=0.0)
    w = {"y": d["y"], "x": d["x"], "beta": beta, "start": TRAIN}
    r1, r2 = _rule(w, pos=pos), _rule(w, lag=2, pos=pos)
    return {"c0": _net(r1, 0.0), "c5": _net(r1, COST), "c5_lag2": _net(r2, COST)}


def exp_lookahead_demo(demo):
    """4c บนคู่ตัวอย่าง: กฎเดียวกัน ε เส้นเดียวกัน ต่างกันที่เส้นแบ่งโซนสามแบบ"""
    lines = _zone_lines(demo["eps"])
    out = {"lines": lines}
    for name in VARIANTS:
        out[name] = _zone_test(demo, demo["eps"], demo["beta"], lines[name])
    return out


def exp_lookahead_mc(pairs):
    """4c บนหลายโลก — ผลรวมของ 750 แท่งหลัง ที่ c = 0 และ 5 bps (และ lag 2)"""
    out = {name: {"c0": [], "c5": [], "c5_lag2": []} for name in VARIANTS}
    for w in pairs:
        _, b, eps = _spread_from_train(w)
        for name, ln in _zone_lines(eps, start=TRAIN).items():
            for k, s in _zone_test(w, eps, b, ln).items():
                out[name][k].append(s)
    return {name: {k: _collect(v) for k, v in cell.items()} for name, cell in out.items()}


# ───────────────────────── แกะหนึ่งไม้ (คู่ good ตัวอย่าง) ─────────────────────────

def exp_trade(demo):
    """ไม้แรกที่เปิดและปิดครบในครึ่งหลังของคู่ good ตัวอย่าง ด้วยไม้บรรทัดจากครึ่งแรก (α̂, β̂, μ̂, σ̂ ตายตัว)
    กฎ: เข้าเมื่อ |z| ≥ 2 ออกเมื่อ z ข้าม 0 · ไม่ได้เลือกไม้สวย: เอาไม้แรกตามลำดับเวลา"""
    eps, b, sd = demo["eps"], demo["beta"], demo["sigma_train"]
    z = C.zscore_fixed(eps, float(eps[:TRAIN].mean()), sd)
    z[:TRAIN] = np.nan
    pos = C.band_positions(z, entry=ENTRY, exit=EXIT)
    pnl, info = C.spread_pnl(demo["y"], demo["x"], b, pos, cost_per_leg=0.0)
    opens, closes, sides = _round_trips(pos)
    cum = np.cumsum(pnl)
    gross = cum[closes] - cum[opens]                  # ผลของแท่ง open+1 … close (lag = 1)
    t0, t1, side = int(opens[0]), int(closes[0]), float(sides[0])
    net = C.perf_stats((pnl - COST * info["turnover"])[TRAIN:], info["held"][TRAIN:], COST)
    return {
        "z": z, "pos": pos, "entry_bar": t0, "exit_bar": t1, "side": side,
        "z_entry": float(z[t0]), "z_exit": float(z[t1]), "eps_entry": float(eps[t0]), "eps_exit": float(eps[t1]),
        "dy": float(demo["y"][t1] - demo["y"][t0]), "dx": float(demo["x"][t1] - demo["x"][t0]),
        "gross": float(gross[0]), "formula": float(-side * (z[t0] - z[t1]) * sd / (1.0 + b)),
        "trades": int(len(gross)), "gross_avg": float(gross.mean()), "hit_rate": float(np.mean(gross > 2 * COST)),
        "formula_avg": float((ENTRY - EXIT) * sd / (1.0 + b)), "total_net": net["total"],
        "open_at_end": net["open_at_end"], "z_sd_test": float(z[TRAIN:].std()),
    }


# ───────────────────────── ไม้บรรทัดของโลก Monte Carlo ─────────────────────────

def _wf_world(d):
    """หนึ่งโลก + ไม้บรรทัด walk-forward ของมัน (z, β̂ รายแท่ง) — คิดครั้งเดียว ใช้กับทุกกฎ"""
    wf = C.walk_forward_pair(d["y"], d["x"], train=WF_TRAIN, refit=WF_REFIT)
    return {"y": d["y"], "x": d["x"], "z": wf["z"], "beta": np.where(np.isfinite(wf["beta"]), wf["beta"], 0.0),
            "start": WF_TRAIN, "eps_hat": wf["eps"], "eps_true": d["eps"], "z_sd": wf["stats"]["z_sd"],
            "break_index": d.get("break_index")}


def _stop_view(w):
    """โลก walk-forward เดิม แต่เริ่มเทรดที่แท่ง STOP_FROM — นับผลช่วงเดียวกับไม้บรรทัดตายตัวของ 4f"""
    return dict(w, start=STOP_FROM)


def _fixed_world(d):
    """โลกเดิม แต่ใช้ไม้บรรทัดตายตัว: α̂, β̂, μ̂, σ̂ จาก FIX_TRAIN แท่งแรก แล้วไม่ประมาณใหม่อีกเลย
    (ใกล้กับการลากเส้นโซนครั้งเดียวแบบในสไลด์ที่สุด)"""
    r = C.ols(d["y"][:FIX_TRAIN], d["x"][:FIX_TRAIN])
    a, b = float(r["coef"][0]), float(r["coef"][1])
    z = C.zscore_fixed(d["y"] - a - b * d["x"], float(r["resid"].mean()), float(r["resid"].std(ddof=1)))
    z[:FIX_TRAIN] = np.nan
    return {"y": d["y"], "x": d["x"], "z": z, "beta": np.full(N, b), "start": STOP_FROM,
            "break_index": d.get("break_index")}


def _rule_table(worlds, **band):
    """รันกฎหนึ่งชุดบนทุกโลก → ผลต่อระดับต้นทุน + lag 2 ที่ c = 5 bps"""
    runs = [_rule(w, **band) for w in worlds]
    out = {c: _collect([_net(r, c) for r in runs]) for c in COSTS}
    out["lag2"] = _collect([_net(_rule(w, lag=2, pos=r["pos"]), COST) for w, r in zip(worlds, runs)])
    out["runs"] = runs
    return out


# ───────────────────────── 4d: เกณฑ์เข้ากว้างหรือแคบ ─────────────────────────

def _true_sigma_at_entry(worlds, runs):
    """ตอนที่ z ของ walk-forward สั่งเข้า ε จริงอยู่ห่างค่าเฉลี่ยจริงกี่ σ จริง (เฉลี่ยทุกไม้ ทุกโลก)"""
    dist = [np.abs(w["eps_true"][_round_trips(r["pos"])[0]]) / SIGMA for w, r in zip(worlds, runs)]
    dist = np.concatenate(dist)
    return float(dist.mean()) if len(dist) else math.nan


def _known_rule(w, entry):
    """รอบ "ถ้ารู้ค่าจริง": z = ε จริง / σ จริง และ β จริง — ใช้เทียบสูตรในหน่วย σ จริงเท่านั้น"""
    kw = {"y": w["y"], "x": w["x"], "z": C.zscore_fixed(w["eps_true"], 0.0, SIGMA), "beta": BETA,
          "start": WF_TRAIN}
    r = _rule(kw, entry=entry, exit=EXIT)
    opens, closes, gross = _closed_trades(r, WF_TRAIN)
    return {"trade_gross": gross, "z_in": np.abs(kw["z"][opens]), "z_out": np.abs(kw["z"][closes]),
            "c0": _net(r, 0.0), "c5": _net(r, COST)}


def exp_threshold(worlds):
    """4d: entry 0.5–3 (exit 0) × ต้นทุน 0 / 5 / 20 / 50 bps บนโลก good — walk-forward และรอบ "ถ้ารู้ค่าจริง\""""
    out = {"wf": {}, "known": {}}
    for entry in ENTRIES:
        cell = _rule_table(worlds, entry=entry, exit=EXIT)
        cell["true_sigma_at_entry"] = _true_sigma_at_entry(worlds, cell.pop("runs"))
        out["wf"][entry] = cell
        known = [_known_rule(w, entry) for w in worlds]
        out["known"][entry] = {
            "trade_gross": np.concatenate([k["trade_gross"] for k in known]),
            "z_in": np.concatenate([k["z_in"] for k in known]), "z_out": np.concatenate([k["z_out"] for k in known]),
            "c0": _collect([k["c0"] for k in known]), "c5": _collect([k["c5"] for k in known])}
    out["z_sd"] = np.array([w["z_sd"] for w in worlds])
    return out


# ───────────────────────── 4e: ออกตรงไหน ─────────────────────────

def exp_exits(worlds):
    """4e: entry 2 · ออกที่ z = 0 · ออกก่อนที่ |z| = 0.5 · รอถึงแถบตรงข้าม (กลับข้างทันที)"""
    out = {}
    for key, exit_z in EXIT_RULES:
        cell = _rule_table(worlds, entry=ENTRY, exit=exit_z)
        cell.pop("runs")
        out[key] = cell
    return out


# ───────────────────────── 4f: stop แบบต่าง ๆ ─────────────────────────

def exp_stops(worlds, breaks=False):
    """4f: stop ที่ระดับ z × จำกัดเวลาถือ ที่ c = 5 bps · โลก break เก็บผล "หลังสายจูงขาด" แยกไว้ด้วย
    worlds มาจาก _stop_view (walk-forward) หรือ _fixed_world (ไม้บรรทัดตายตัว) — เทรดแท่ง STOP_FROM เป็นต้นไป"""
    out = {}
    for key, stop, hold in STOP_RULES:
        runs = [_rule(w, entry=ENTRY, exit=EXIT, stop=stop, max_hold=hold) for w in worlds]
        nets = [r["gross"] - COST * r["turn"] for r in runs]
        cell = _collect([C.perf_stats(net, r["held"], cost_per_leg=COST) for net, r in zip(nets, runs)])
        cell["sharpe_lag2"] = np.array([_net(_rule(w, lag=2, pos=r["pos"]), COST)["sharpe"]
                                        for w, r in zip(worlds, runs)])
        worst = [C.trade_pnls(r["held"], net, cost_per_leg=COST) for net, r in zip(nets, runs)]
        cell["worst_trade"] = np.array([float(t.min()) if len(t) else 0.0 for t in worst])
        if breaks:
            cell["after_break"] = np.array([float(net[w["break_index"] - w["start"]:].sum())
                                            for w, net in zip(worlds, nets)])
        out[key] = cell
    return out


# ───────────────────────── 4g: ทะลุเส้นนอกสุด ─────────────────────────

def _pierce_events(w, lo, hi):
    """ทุกครั้งที่ |z| ของ walk-forward ข้ามขึ้นไปถึง PIERCE ในแท่ง [lo, hi) → (กลับเข้าไหม, กี่แท่ง, ผลขั้นต้น)

    "กลับเข้า" วัดด้วยไม้บรรทัด ณ วันที่แตะ (α̂, β̂, σ̂ ชุดนั้น ไม่ขยับตามการประมาณใหม่) เพราะนั่นคือสิ่งที่
    กำหนดกำไรขาดทุนของไม้ที่เปิดวันนั้น — ถ้าปล่อยให้ไม้บรรทัดขยับ z จะ "กลับ" เองเพราะค่าเฉลี่ยเลื่อนตามราคา
    ไม้: เปิดสวนทางที่ราคาปิดของแท่งที่แตะ ถือจนกลับเข้า |z| < INSIDE หรือครบ MAX_HOLD แท่ง"""
    y, x, z, beta, eps = w["y"], w["x"], w["z"], w["beta"], w["eps_hat"]
    out = []
    t = max(lo, WF_TRAIN + 1)
    while t + MAX_HOLD < hi:
        if abs(z[t]) >= PIERCE and abs(z[t - 1]) < PIERCE:
            sigma_hat = eps[t] / z[t]                 # σ̂ ที่ใช้อยู่ ณ แท่ง t (μ̂ ของส่วนเหลือ OLS = 0)
            path = (y[t + 1:t + 1 + MAX_HOLD] - y[t]) - beta[t] * (x[t + 1:t + 1 + MAX_HOLD] - x[t])
            back = np.flatnonzero(np.abs(z[t] + path / sigma_hat) < INSIDE)
            k = int(back[0]) + 1 if len(back) else MAX_HOLD
            out.append((bool(len(back)), k, float(-np.sign(z[t]) * path[k - 1] / (1.0 + abs(beta[t])))))
            t += k
        else:
            t += 1
    return out


def _forward_by_bucket(w, lo, hi):
    """ผลขั้นต้น FWD แท่งข้างหน้าของการ "สวน z" ที่เปิด ณ แท่ง t (β̂ ณ แท่ง t) แยกตามระดับ |z| ของแท่ง t"""
    t = np.arange(max(lo, WF_TRAIN), hi - FWD)
    z, b = w["z"][t], w["beta"][t]
    fwd = -np.sign(z) * ((w["y"][t + FWD] - w["y"][t]) - b * (w["x"][t + FWD] - w["x"][t])) / (1.0 + np.abs(b))
    return {key: fwd[(np.abs(z) >= a) & (np.abs(z) < hi_z)] for key, a, hi_z in BUCKETS}


def exp_pierce(good_worlds, break_worlds):
    """4g: ทะลุ |z| ≥ 2.5 แล้วเกิดอะไรต่อ — โลก good · โลก break ก่อนขาด · โลก break หลังขาด"""
    spans = {"good": [(w, WF_TRAIN, N) for w in good_worlds],
             "break_before": [(w, WF_TRAIN, w["break_index"]) for w in break_worlds],
             "break_after": [(w, w["break_index"], N) for w in break_worlds]}
    out = {"events": {}, "forward": {}}
    for name, items in spans.items():
        ev = [e for w, lo, hi in items for e in _pierce_events(w, lo, hi)]
        out["events"][name] = {"back": np.array([e[0] for e in ev], bool), "bars": np.array([e[1] for e in ev]),
                               "gross": np.array([e[2] for e in ev])}
    for name in ("good", "break_after"):
        parts = [_forward_by_bucket(w, lo, hi) for w, lo, hi in spans[name]]
        out["forward"][name] = {key: np.concatenate([p[key] for p in parts]) for key, _, _ in BUCKETS}
    return out


# ───────────────────────── รวมทุกการทดลอง ─────────────────────────

@functools.lru_cache(maxsize=1)
def run():
    """คำนวณทุกการทดลอง (ราว 50 วินาที) — เรียกซ้ำได้ผลชุดเดิมจากหน่วยความจำ"""
    demo = {"good": _demo("good"), "bad": _demo("fake"), "break": _demo("break")}
    good_pairs, fake_pairs = _pairs("good", SEED_GOOD, WORLDS), _pairs("fake", SEED_FAKE, WORLDS)
    break_pairs = _break_pairs()
    good_worlds = [_wf_world(d) for d in good_pairs]
    break_worlds = [_wf_world(d) for d in break_pairs]
    return {
        "demo": demo,
        "stability_mc": {"good": exp_stability_mc("good", SEED_GOOD), "bad": exp_stability_mc("fake", SEED_FAKE)},
        "lookahead": {"good": exp_lookahead_demo(demo["good"]), "bad": exp_lookahead_demo(demo["bad"])},
        "lookahead_mc": {"good": exp_lookahead_mc(good_pairs), "bad": exp_lookahead_mc(fake_pairs)},
        "trade": exp_trade(demo["good"]),
        "threshold": exp_threshold(good_worlds),
        "exits": exp_exits(good_worlds),
        "stops": {
            "wf": {"good": exp_stops([_stop_view(w) for w in good_worlds]),
                   "break": exp_stops([_stop_view(w) for w in break_worlds], breaks=True)},
            "fixed": {"good": exp_stops([_fixed_world(d) for d in good_pairs]),
                      "break": exp_stops([_fixed_world(d) for d in break_pairs], breaks=True)}},
        "pierce": exp_pierce(good_worlds, break_worlds),
        "break_bars": np.array([d["break_index"] for d in break_pairs]),
    }


# ───────────────────────── figures: ปัดเลขให้พร้อมลงในบท ─────────────────────────

def _r1(v):
    return C.rd(v, 1)


def _r2(v):
    return C.rd(v, 2)


def _g(v):
    """เลขของเกณฑ์: จำนวนเต็มเก็บเป็น int (2 ไม่ใช่ 2.0)"""
    return int(v) if float(v).is_integer() else float(v)


def _key(prefix, v):
    """0.5 → e0_5 · 2.0 → e2 · 0.0005 (ต้นทุน) ใช้ _ckey แทน"""
    return prefix + f"{v:g}".replace(".", "_").replace("-", "m")


def _ckey(cost):
    return f"c{cost * 1e4:g}"


def _fig_zone(d):
    z = d["zone"]
    out = {"alpha": C.rd(d["alpha"], 3), "beta": C.rd(d["beta"], 3), "sigma_train_pct": C.pct(d["sigma_train"], 2)}
    out.update({f"p{q}_pct": C.pct(v, 2) for q, v in z["pcts"].items()})
    out.update({
        "width_p1_p99_pct": C.pct(z["pcts"][99] - z["pcts"][1], 1),
        "crossings": z["crossings"], "bars_per_crossing": C.rd(z["bars_per_crossing"], 1),
        "longest_one_side_bars": z["longest_one_side"], "outside_10_90_pct": C.pct(z["outside"], 1),
        "visits": z["visits"], "visit_longest_bars": z["visit_longest"],
        "visit_median_bars": C.rd(z["visit_median"], 1),
        "last_pct": C.pct(z["last"], 2), "last_rank_pct": C.pct(z["last_rank"], 0)})
    if d["break_index"] is not None:
        v = d["break_view"]
        out["break_bar"] = int(d["break_index"])
        out.update({f"pre_p{q}_pct": C.pct(val, 2) for q, val in v["pre"].items()})
        out.update({"before_beyond_1_99_pct": C.pct(v["before_beyond"], 0),
                    "after_beyond_1_99_pct": C.pct(v["after_beyond"], 0),
                    "first_pierce_bar": v["first_pierce_bar"], "last_middle_bar": v["last_middle_bar"]})
    return out


def _fig_stability(s):
    out = {}
    for half in ("first", "second"):
        out.update({f"{half}_p{q}_sigma": _r2(v) for q, v in zip(ZONE_Q, s[half])})
    out.update({"shift_p50_sigma": _r2(s["shift"]), "width_ratio": _r2(s["width_ratio"]),
                "second_outside_pct": C.pct(s["second_outside"], 0)})
    return out


def _fig_stability_mc(m):
    sh, wr, so = _dist(m["shift_abs"]), _dist(m["width_ratio"]), _dist(m["second_outside"])
    return {"worlds": WORLDS_ZONE,
            "shift_abs_p50_sigma": _r1(sh["p50"]), "shift_abs_p5_sigma": _r1(sh["p5"]),
            "shift_abs_p95_sigma": _r1(sh["p95"]),
            "width_ratio_p50": _r1(wr["p50"]), "width_ratio_p5": _r1(wr["p5"]), "width_ratio_p95": _r1(wr["p95"]),
            "second_outside_p50_pct": C.pct(so["p50"], 0), "second_outside_p5_pct": C.pct(so["p5"], 0),
            "second_outside_p95_pct": C.pct(so["p95"], 0)}


def _fig_lookahead_demo(la):
    out = {}
    for name in VARIANTS:
        cell = {}
        for ck in ("c0", "c5"):
            s = la[name][ck]
            cell[ck] = {"total_pct": C.pct(s["total"], 1), "sharpe": _r2(s["sharpe"]), "trades": s["n_trades"],
                        "max_dd_pct": C.pct(s["max_dd"], 1), "open_at_end": bool(s["open_at_end"])}
        cell["c5"]["sharpe_lag2"] = _r2(la[name]["c5_lag2"]["sharpe"])
        cell["c5"]["total_lag2_pct"] = C.pct(la[name]["c5_lag2"]["total"], 1)
        out[name] = cell
    return out


def _fig_lookahead_mc(m):
    out = {"worlds": WORLDS}
    for name in VARIANTS:
        t = m[name]["c5"]["total"]
        tot = _dist(t)
        out[name] = {"total_mean_pct": C.pct(tot["mean"], 0),
                     "total_mean_pm95_pct": C.pct(1.96 * t.std(ddof=1) / math.sqrt(len(t)), 1),
                     "total_p5_pct": C.pct(tot["p5"], 0), "total_p50_pct": C.pct(tot["p50"], 0),
                     "total_p95_pct": C.pct(tot["p95"], 0),
                     "profitable_pct": C.pct(np.mean(t > 0), 0),
                     "sharpe_mean": _r1(m[name]["c5"]["sharpe"].mean()),
                     "sharpe_lag2_mean": _r1(m[name]["c5_lag2"]["sharpe"].mean()),
                     "trades_mean": _r1(m[name]["c5"]["n_trades"].mean()),
                     "total_c0_mean_pct": C.pct(m[name]["c0"]["total"].mean(), 0)}
    gap = m["full"]["c5"]["total"] - m["expanding"]["c5"]["total"]
    out["gap_full_minus_expanding_pct"] = C.pct(gap.mean(), 0)
    out["full_beats_expanding_pct"] = C.pct(np.mean(gap > 0), 0)
    return out


def _fig_trade(t):
    return {
        "entry_bar": t["entry_bar"], "exit_bar": t["exit_bar"], "bars_held": t["exit_bar"] - t["entry_bar"],
        "side": "short" if t["side"] < 0 else "long",
        "z_entry": _r2(t["z_entry"]), "z_exit": _r2(t["z_exit"]),
        "eps_entry_pct": C.pct(t["eps_entry"], 2), "eps_exit_pct": C.pct(t["eps_exit"], 2),
        "dy_pct": C.pct(t["dy"], 2), "dx_pct": C.pct(t["dx"], 2),
        "gross_pct": C.pct(t["gross"], 2), "formula_pct": C.pct(t["formula"], 2),
        "cost_pct": C.pct(2 * COST, 2), "net_pct": C.pct(t["gross"] - 2 * COST, 2),
        "trades": t["trades"], "gross_avg_pct": C.pct(t["gross_avg"], 2),
        "formula_avg_pct": C.pct(t["formula_avg"], 2), "hit_rate_pct": C.pct(t["hit_rate"], 0),
        "total_net_pct": C.pct(t["total_net"], 1), "open_at_end": bool(t["open_at_end"]),
        "z_sd_test": _r2(t["z_sd_test"]),
    }


def _fig_cost_cell(a, lag2=None):
    """ตัวเลขของหนึ่งกฎที่ต้นทุนหนึ่งระดับ (a = อาร์เรย์ต่อโลกจาก _collect)"""
    trades = a["n_trades"].sum()
    ret, sh = _dist(a["ann_return"]), _dist(a["sharpe"])
    out = {"net_per_trade_pct": C.pct(a["total"].sum() / trades, 2) if trades else 0.0,
           "ann_return_pct": C.pct(ret["mean"], 1), "ann_return_p5_pct": C.pct(ret["p5"], 1),
           "ann_return_p95_pct": C.pct(ret["p95"], 1),
           "sharpe": _r1(sh["mean"]), "sharpe_p5": _r1(sh["p5"]), "sharpe_p95": _r1(sh["p95"]),
           "profitable_pct": C.pct(np.mean(a["total"] > 0), 0)}
    if lag2 is not None:
        out["sharpe_lag2"] = _r1(lag2["sharpe"].mean())
        out["ann_return_lag2_pct"] = C.pct(lag2["ann_return"].mean(), 1)
    return out


def _fig_rule(cell):
    """ส่วนที่ไม่ขึ้นกับต้นทุน + ตารางต่อระดับต้นทุน ของหนึ่งกฎ"""
    a0 = cell[0.0]
    trades = a0["n_trades"].sum()
    bars_in = a0["time_in_market"].sum() * (N - WF_TRAIN)
    out = {"trades_per_year": _r1(a0["n_trades"].mean() / WF_YEARS),
           "hold_bars": C.rd(bars_in / trades, 0) if trades else 0,
           "in_market_pct": C.pct(a0["time_in_market"].mean(), 0),
           "gross_per_trade_pct": C.pct(a0["total"].sum() / trades, 2) if trades else 0.0}
    for c in COSTS:
        out[_ckey(c)] = _fig_cost_cell(cell[c], cell["lag2"] if c == COST else None)
    return out


def _best(per_entry):
    """เกณฑ์ที่ค่าเฉลี่ยสูงสุด — รายงานเป็นช่วงถ้าเกณฑ์ข้างเคียงห่างไม่เกิน 2 เท่าของความคลาดของ "ผลต่าง"
    (วัดบนโลกชุดเดียวกัน) เพราะผู้ชนะที่ห่างกันน้อยกว่านั้นสลับกันได้เมื่อเปลี่ยนชุดโลก"""
    m = np.array(per_entry)                       # (จำนวนเกณฑ์, จำนวนโลก)
    means = m.mean(axis=1)
    b = int(np.argmax(means))
    se = (m - m[b]).std(axis=1, ddof=1) / math.sqrt(m.shape[1])
    near = [i for i in range(len(means)) if means[b] - means[i] <= 2.0 * se[i]]
    lo, hi = ENTRIES[min(near)], ENTRIES[max(near)]
    return (f"{lo:g}" if lo == hi else f"{lo:g}–{hi:g}"), float(means[b])


def _fig_threshold(th):
    out = {"worlds": WORLDS}
    zs = _dist(th["z_sd"])
    out.update({"z_sd": _r2(zs["mean"]), "z_sd_p5": _r2(zs["p5"]), "z_sd_p95": _r2(zs["p95"])})
    for entry in ENTRIES:
        cell = {"entry_z": _g(entry), "true_sigma_at_entry": _r1(th["wf"][entry]["true_sigma_at_entry"])}
        cell.update(_fig_rule(th["wf"][entry]))
        out[_key("e", entry)] = cell
    out["best"] = {}
    for c in COSTS:
        by_ret, ret = _best([th["wf"][e][c]["ann_return"] for e in ENTRIES])
        by_sh, sh = _best([th["wf"][e][c]["sharpe"] for e in ENTRIES])
        out["best"][_ckey(c)] = {"entry_by_return": by_ret, "ann_return_pct": C.pct(ret, 1),
                                 "entry_by_sharpe": by_sh, "sharpe": _r1(sh)}
    out["known"] = {}
    for entry in ENTRIES:
        k = th["known"][entry]
        out["known"][_key("e", entry)] = {
            "formula_pct": C.pct((entry - EXIT) * SIGMA / (1.0 + BETA), 2),
            "gross_per_trade_pct": C.pct(k["trade_gross"].mean(), 2),
            "z_in": _r2(k["z_in"].mean()), "z_out": _r2(k["z_out"].mean()),
            "trades_per_year": _r1(k["c0"]["n_trades"].mean() / WF_YEARS),
            "ann_return_c0_pct": C.pct(k["c0"]["ann_return"].mean(), 1),
            "ann_return_c5_pct": C.pct(k["c5"]["ann_return"].mean(), 1),
            "sharpe_c5": _r1(k["c5"]["sharpe"].mean())}
    return out


def _fig_exits(ex):
    out = {"worlds": WORLDS}
    for key, exit_z in EXIT_RULES:
        cell = {"exit_z": _g(exit_z)}
        cell.update(_fig_rule(ex[key]))
        out[key] = cell
    return out


def _fig_stops(st, worlds, breaks=False):
    """ตัวเลขของ 4f · tail10 = ค่าเฉลี่ยของ 10% ของโลกที่ผลรวมแย่ที่สุด (นิ่งกว่าเปอร์เซ็นไทล์ 5)
    none_tail = ผลของกฎนี้ "ในโลกกลุ่มเดียวกับ 10% ที่แย่ที่สุดเมื่อไม่มี stop" (เทียบเป็นคู่ โลกต่อโลก)"""
    out = {"worlds": worlds}
    base = st["none"]["total"]
    k = max(1, int(round(TAIL * len(base))))
    worst_none = np.argsort(base)[:k]
    for key, _, _ in STOP_RULES:
        a = st[key]
        tot = _dist(a["total"])
        cell = {"sharpe_mean": _r1(a["sharpe"].mean()), "sharpe_lag2_mean": _r1(a["sharpe_lag2"].mean()),
                "total_mean_pct": C.pct(tot["mean"], 0), "total_p5_pct": C.pct(tot["p5"], 0),
                "total_p50_pct": C.pct(tot["p50"], 0), "total_p95_pct": C.pct(tot["p95"], 0),
                "tail10_pct": C.pct(np.sort(a["total"])[:k].mean(), 0),
                "max_dd_mean_pct": C.pct(a["max_dd"].mean(), 0),
                "worst_trade_p5_pct": C.pct(np.percentile(a["worst_trade"], 5), 1),
                "hit_rate_pct": C.pct(a["hit_rate"].mean(), 0),
                "trades_per_year": _r1(a["n_trades"].mean() / STOP_YEARS)}
        if key != "none":
            cell["beats_none_pct"] = C.pct(np.mean(a["total"] > base), 0)
            cell["diff_vs_none_pct"] = C.pct((a["total"] - base).mean(), 0)
            cell["none_tail_pct"] = C.pct(a["total"][worst_none].mean(), 0)
            cell["none_tail_helps_pct"] = C.pct(np.mean(a["total"][worst_none] > base[worst_none]), 0)
        if breaks:
            cell["after_break_mean_pct"] = C.pct(a["after_break"].mean(), 0)
        out[key] = cell
    return out


def _fig_pierce(p):
    out = {"touch_z": PIERCE, "inside_z": INSIDE, "window_bars": MAX_HOLD, "forward_bars": FWD,
           "worlds_good": WORLDS, "worlds_break": WORLDS_BREAK}
    for name, e in p["events"].items():
        back = e["back"]
        out[name] = {"events": int(len(back)), "back_pct": C.pct(back.mean(), 0),
                     "back_12_pct": C.pct(np.mean(back & (e["bars"] <= FWD)), 0),
                     "back_24_pct": C.pct(np.mean(back & (e["bars"] <= 2 * FWD)), 0),
                     "bars_to_back_median": int(round(float(np.median(e["bars"][back])))) if back.any() else 0,
                     "gross_mean_pct": C.pct(e["gross"].mean(), 1),
                     "gross_p5_pct": C.pct(np.percentile(e["gross"], 5), 1),
                     "losing_pct": C.pct(np.mean(e["gross"] < 0), 0)}
    out["forward"] = {}
    for name, cells in p["forward"].items():
        out["forward"][name] = {
            key: {"mean_pct": C.pct(v.mean(), 1), "p5_pct": C.pct(np.percentile(v, 5), 1),
                  "p95_pct": C.pct(np.percentile(v, 95), 1), "losing_pct": C.pct(np.mean(v < 0), 0),
                  "bars": int(len(v))}
            for key, v in cells.items()}
    return out


def _about():
    c_bps = COST * 1e4
    return {
        "common": f"ข้อมูลจำลองทั้งหมด {N:,} แท่งรายวันต่อโลก (ราว 6 ปี) · ผลตอบแทนคิดต่อเงินรวมสองขา · "
                  "สถานะที่ตัดสินใจสิ้นแท่ง t รับผลตั้งแต่แท่ง t+1 (lag 1) และรายงาน lag 2 ประกบ · "
                  "c = ต้นทุนต่อขาต่อเที่ยว (ครบรอบเสีย 2c)",
        "precision": "ตัวเลข Monte Carlo ปัดตามความแม่นที่วัดได้จากการรันซ้ำบนชุดโลกอื่น: ผลรวมเป็น % เต็ม · "
                     "Sharpe ทศนิยมหนึ่งตำแหน่ง · ค่าเฉลี่ยขยับได้ไม่เกินหนึ่งหน่วยของหลักสุดท้าย · tail10 ขยับได้ราว "
                     "±2 จุด และ p5 ของโลก break ขยับได้ถึง ±4 จุด จึงใช้ tail10 และใช้เทียบระหว่างกฎบนโลกชุดเดียวกัน "
                     "(ลำดับของกฎคงที่ทุกชุดโลกที่ลอง) · ตัวเลขของคู่ตัวอย่างเส้นเดียวเป็นค่าแน่นอนของเส้นนั้น "
                     "(ภาพประกอบ ไม่ใช่ค่าทั่วไป)",
        "zones": f"คู่ตัวอย่าง good / fake (คีย์ bad) / break · ε = Y − α̂ − β̂·X ของทั้ง {N:,} แท่ง "
                 f"โดย α̂, β̂ ประมาณจาก {TRAIN} แท่งแรกเท่านั้น · เส้นเปอร์เซ็นไทล์ 1, 10, …, 90, 99 คิดจากทั้งช่วง "
                 "เหมือนสไลด์ (รู้อนาคต) · crossings = จำนวนครั้งที่ ε ตัดเส้น P50 · visits = จำนวนครั้งที่ออกนอกเส้น "
                 "P10/P90 (สัดส่วนเวลานอกเส้นเป็น 20% เสมอโดยนิยาม จึงต้องดูว่าออกไปครั้งละนานแค่ไหนแทน) · "
                 f"คู่ break: pre_p… = เส้นที่คิดจาก {TRAIN} แท่งแรก (ก่อนสายจูงขาด)",
        "stability": f"แบ่งครึ่ง {TRAIN} / {N - TRAIN} แท่ง · P10/P50/P90 ของแต่ละครึ่งหารด้วย sd ของครึ่งแรก · "
                     "second_outside = สัดส่วนเวลาของครึ่งหลังที่อยู่นอกเส้น P10–P90 ของครึ่งแรก (ถ้าโซนนิ่ง ≈ 20%) · "
                     f"Monte Carlo {WORLDS_ZONE:,} โลก good และ {WORLDS_ZONE:,} โลก fake",
        "lookahead": "กฎ short เหนือ P90 · long ใต้ P10 · ออกที่ P50 บน ε เส้นเดียวกับกราฟโซน · เส้นสามแบบ: full = "
                     f"ทั้ง {N:,} แท่ง (รู้อนาคต) · expanding = ทุกแท่งตั้งแต่ต้นถึงวันนั้น · rolling = {ROLL} แท่งล่าสุด · "
                     f"นับผลเฉพาะแท่ง {TRAIN}–{N - 1} (ช่วงที่ β̂ ไม่เคยเห็น ราว 3 ปี) · c = 0 และ {c_bps:g} bps · "
                     f"Monte Carlo {WORLDS} โลก good และ {WORLDS} โลก fake ที่ c = {c_bps:g} bps · total_mean_pm95 = "
                     "ครึ่งความกว้างของช่วงเชื่อมั่น 95% ของค่าเฉลี่ย · คู่ตัวอย่าง fake เทรดเพียง 2–3 ไม้ในช่วงที่นับผล "
                     "และไม้สุดท้ายยังเปิดค้าง (ตีมูลค่าที่ราคาสุดท้าย) จึงใช้เป็นภาพประกอบเท่านั้น",
        "trade": f"คู่ good ตัวอย่าง · ไม้บรรทัดตายตัวจาก {TRAIN} แท่งแรก (α̂, β̂, μ̂, σ̂) · เข้า |z| ≥ {ENTRY:g} ออกเมื่อ z "
                 f"ข้าม {EXIT:g} · เทรดเฉพาะแท่ง {TRAIN}–{N - 1} · ไม้ที่แกะ = ไม้แรกตามลำดับเวลา (ไม่ได้เลือก) · "
                 f"ต้นทุนครบรอบ 2c = {2 * c_bps:g} bps · gross_pct = (z เข้า − z ออก)·σ̂/(1+β̂) พอดี (formula_pct) "
                 "เพราะเมื่อ β คงที่ กำไรของไม้คือการเปลี่ยนของ ε หารด้วย 1+β̂ — เป็นเอกลักษณ์ ไม่ใช่การยืนยันสูตร · "
                 "สูตรแบบประมาณใช้ z เข้า/ออกตามเกณฑ์ (formula_avg_pct) เทียบกับค่าเฉลี่ยจริง (gross_avg_pct)",
        "threshold": f"{WORLDS} โลก good (β {BETA} · half-life {HL:g} แท่ง · σ {SIGMA * 100:g}%) · walk-forward: train "
                     f"{WF_TRAIN} แท่ง ประมาณใหม่ทุก {WF_REFIT} แท่ง · ทดสอบแท่ง {WF_TRAIN}–{N - 1} (ราว "
                     f"{WF_YEARS:.1f} ปีต่อโลก) · entry 0.5–3 · exit 0 · c = 0 / 5 / 20 / 50 bps · สถานะชุดเดียวกัน"
                     "ทุกต้นทุน · กำไรต่อไม้ = ผลรวมทุกโลก ÷ จำนวนไม้ทุกโลก · z วัดด้วย σ ของช่วง train (ดู z_sd) · "
                     "best: ถ้าเกณฑ์ข้างเคียงสูสีจนแยกไม่ออก (ห่างไม่เกิน 2 เท่าของความคลาด) จะรายงานเป็นช่วง · "
                     "0.5 คือค่าต่ำสุดในตาราง: ที่ c = 0 เกณฑ์ที่ต่ำกว่านี้ยังได้มากกว่าอีก จึงห้ามสรุปว่า 0.5 "
                     "ดีที่สุดเมื่อไม่มีต้นทุน (ที่ 5 bps ขึ้นไป จุดสูงสุดอยู่ในตารางจริง)",
        "known": f"รอบ \"ถ้ารู้ค่าจริง\" บน {WORLDS} โลกชุดเดียวกัน: z = ε จริง ÷ σ จริง และใช้ β จริง — ทำไม่ได้ใน"
                 "ชีวิตจริง มีไว้เทียบกับสูตร (entry − exit)·σ/(1+β) ในหน่วย σ จริงเท่านั้น · z_in / z_out = ระยะจาก 0 "
                 "ตอนเข้า/ออกจริง · gross_per_trade นับเฉพาะไม้ที่ปิดแล้ว",
        "exits": f"{WORLDS} โลก good ชุดเดียวกัน · walk-forward · entry {ENTRY:g} · exit 0 (ถึงค่าเฉลี่ย) · 0.5 (ออกก่อน) · "
                 "−2 (รอถึงแถบตรงข้ามแล้วกลับข้างทันที) · c = 0 / 5 / 20 / 50 bps",
        "stops": f"entry {ENTRY:g} · exit {EXIT:g} · c = {c_bps:g} bps · stop ที่ |z| = 4 หรือ 3 × จำกัดเวลาถือ {MAX_HOLD} "
                 f"แท่ง (3 เท่าของ half-life จริง {HL:g} แท่ง — ในชีวิตจริงต้องประมาณเอง) · โลก good {WORLDS} โลก "
                 f"(ชุดเดียวกับ threshold) · โลก break {WORLDS_BREAK:,} โลก (สายจูงขาด ณ แท่งสุ่ม {BREAK_FROM}–"
                 f"{BREAK_TO - 1} ก่อนขาดเหมือนโลก good) · ไม้บรรทัดสองแบบบนโลกชุดเดียวกัน เทรดและนับผลช่วงเดียวกัน "
                 f"แท่ง {STOP_FROM}–{N - 1} (ราว {STOP_YEARS:.0f} ปี): wf = walk-forward (train {WF_TRAIN} ประมาณใหม่ทุก "
                 f"{WF_REFIT} แท่ง) · fixed = ประมาณครั้งเดียวจาก {FIX_TRAIN} แท่งแรกแล้วไม่ประมาณใหม่ · total = "
                 "ผลรวมตลอดช่วงที่นับผล · tail10 = ค่าเฉลี่ยของ 10% ของโลกที่แย่ที่สุดของกฎนั้น · none_tail = ผลของกฎนั้น"
                 "ในโลกกลุ่ม 10% ที่แย่ที่สุดเมื่อไม่มี stop · none_tail_helps = สัดส่วนของโลกกลุ่มนั้นที่กฎนี้ทำได้ดีกว่า"
                 "ไม่มี stop · worst_trade = ไม้ที่แย่ที่สุดของแต่ละโลก · ตัวเลขชุดนี้นับช่วงสั้นกว่า threshold/exits "
                 "จึงอย่านำผลรวมมาเทียบข้ามชุด",
        "pierce": f"โลก walk-forward ({WORLDS} โลก good · {WORLDS_BREAK:,} โลก break) · เหตุการณ์ = |z| ข้ามขึ้นถึง "
                  f"{PIERCE:g} · กลับ = |z| < {INSIDE:g} ภายใน {MAX_HOLD} แท่ง วัดด้วยไม้บรรทัด ณ วันที่แตะ (ไม่ขยับตาม"
                  f"การประมาณใหม่) · gross = ผลของการเปิดสวนทางวันนั้นแล้วถือจนกลับหรือครบ {MAX_HOLD} แท่ง (ก่อนต้นทุน) "
                  f"· forward = ผล {FWD} แท่งข้างหน้าของการสวน z แยกตามระดับ |z| (นับทุกแท่ง แท่งที่ติดกันซ้อนกัน "
                  "จึงไม่อิสระต่อกัน)",
    }


def figures(res=None):
    """ตัวเลขทุกตัวของตอนที่ 4 (ปัดแล้ว) → ใช้กับ data-f="p4.<path>\""""
    res = res or run()
    demo = res["demo"]
    stability = {k: _fig_stability(demo[k]["stability"]) for k in demo}
    stability["mc"] = {k: _fig_stability_mc(res["stability_mc"][k]) for k in ("good", "bad")}
    lookahead = {k: _fig_lookahead_demo(res["lookahead"][k]) for k in ("good", "bad")}
    lookahead["mc"] = {k: _fig_lookahead_mc(res["lookahead_mc"][k]) for k in ("good", "bad")}
    bb = res["break_bars"]
    stops = {}
    for ruler in ("wf", "fixed"):
        st = res["stops"][ruler]
        stops[ruler] = {"good": _fig_stops(st["good"], WORLDS),
                        "break": _fig_stops(st["break"], WORLDS_BREAK, breaks=True)}
    return {
        "about": _about(),
        "settings": {"bars": N, "train_bars": TRAIN, "test_bars": N - TRAIN, "worlds": WORLDS,
                     "worlds_break": WORLDS_BREAK, "worlds_zone": WORLDS_ZONE,
                     "cost_bps": int(round(COST * 1e4)), "round_trip_bps": int(round(2 * COST * 1e4)),
                     "wf_train_bars": WF_TRAIN, "wf_refit_bars": WF_REFIT, "wf_test_years": C.rd(WF_YEARS, 1),
                     "fixed_train_bars": FIX_TRAIN, "stop_from_bar": STOP_FROM, "stop_test_years": C.rd(STOP_YEARS, 1),
                     "beta_true": BETA, "half_life_true_bars": int(HL), "sigma_true_pct": int(round(SIGMA * 100)),
                     "max_hold_bars": MAX_HOLD, "roll_bars": ROLL, "expanding_min_bars": MIN_BARS,
                     "break_bar_min": int(bb.min()), "break_bar_max": int(bb.max()),
                     "break_bar_median": int(np.median(bb))},
        "zones": {k: _fig_zone(demo[k]) for k in demo},
        "stability": stability,
        "lookahead": lookahead,
        "trade": _fig_trade(res["trade"]),
        "threshold": _fig_threshold(res["threshold"]),
        "exits": _fig_exits(res["exits"]),
        "stops": stops,
        "pierce": _fig_pierce(res["pierce"]),
    }


# ───────────────────────── charts ─────────────────────────

COST_NAMES = {0.0: "ไม่มีต้นทุน", 0.0005: "c = 5 bps", 0.002: "c = 20 bps", 0.005: "c = 50 bps"}
STOP_LABELS = {"none": "ไม่มี stop", "s4": "stop ที่ |z| = 4", "s3": "stop ที่ |z| = 3",
               "t36": f"จำกัดเวลาถือ {MAX_HOLD} แท่ง", "s4_t36": f"stop 4 + จำกัด {MAX_HOLD} แท่ง",
               "s3_t36": f"stop 3 + จำกัด {MAX_HOLD} แท่ง"}
BUCKET_LABELS = {"z1_2": "|z| 1–2", "z2_3": "|z| 2–3", "z3_4": "|z| 3–4", "z4_up": "|z| ≥ 4"}


def _n(v, d=2, sign=False):
    return V.num(v, d, sign=sign)


def _chart_zones(cid, res, key, alt, cap):
    d = res["demo"][key]
    pcts = {q: v * 100 for q, v in d["zone"]["pcts"].items()}
    return V.zone_chart(cid, d["eps"] * 100, pcts, alt, cap, mark_last=True,
                        titles=("การกระจายของ ε", "ε ตามเวลา (%) กับเส้นเปอร์เซ็นไทล์"))


def _chart_zones_good(cid, res, f):
    z = f["zones"]["good"]
    return _chart_zones(
        cid, res, "good",
        "กราฟโซนของคู่ที่มีสายจูง: ε แกว่งรอบเส้นกลาง ออกนอกเส้นนอกแล้วกลับเข้ามาเร็ว",
        f"ข้อมูลจำลอง · คู่ที่มีสายจูงจริง (แบบสไลด์ 6) · ε วัดด้วย α̂, β̂ จาก {TRAIN} แท่งแรก ส่วนเส้นคิดจากทั้ง "
        f"{N:,} แท่งเหมือนในสไลด์ · ให้สังเกต: ε ตัดเส้นกลาง {z['crossings']} ครั้ง (เฉลี่ยทุก "
        f"{_n(z['bars_per_crossing'], 1)} แท่ง) และออกนอกเส้น 10%/90% รวม {z['visits']} ครั้ง ครั้งที่นานที่สุด"
        f"เพียง {z['visit_longest_bars']} แท่ง — ออกไปทีไรก็ถูกดึงกลับ")


def _chart_zones_bad(cid, res, f):
    z, g = f["zones"]["bad"], f["zones"]["good"]
    return _chart_zones(
        cid, res, "bad",
        "กราฟโซนของคู่ที่ไม่มีสายจูง: ε ไหลไปค้างฝั่งเดียวเป็นช่วงยาว และจุดล่าสุดอยู่นอกทุกเส้น",
        f"ข้อมูลจำลอง · คู่ที่ไม่มีสายจูง (แบบสไลด์ 7) · สร้างกราฟด้วยวิธีเดียวกับรูปก่อนทุกขั้นตอน · ให้สังเกต: ε ตัด"
        f"เส้นกลางเพียง {z['crossings']} ครั้ง ค้างฝั่งเดียวนานสุด {z['longest_one_side_bars']} แท่ง ออกนอกเส้น "
        f"10%/90% ครั้งเดียวนานถึง {z['visit_longest_bars']} แท่ง และโซนกว้าง {_n(z['width_p1_p99_pct'], 1)}% "
        f"(คู่ที่ดี {_n(g['width_p1_p99_pct'], 1)}%) — เส้นลากได้เสมอ แต่ไม่มีอะไรดึง ε กลับมาหาเส้น")


def _chart_zones_break(cid, res, f):
    d, z = res["demo"]["break"], f["zones"]["break"]
    pre = d["break_view"]["pre"]
    bi = d["break_index"]
    hl = [(pre[99] * 100, "P99", V.BLUE), (pre[90] * 100, "P90", V.BLUE), (pre[50] * 100, "P50", V.INK),
          (pre[10] * 100, "P10", V.RED), (pre[1] * 100, "P1", V.RED)]
    return V.stacked_panels(
        cid, [{"y": d["eps"] * 100, "title": "ε ของคู่ที่สายจูงขาดกลางทาง (%)",
               "sub": f"เส้นประ = เปอร์เซ็นไทล์ที่คิดจาก {TRAIN} แท่งแรก", "color": V.DARK, "hlines": hl,
               "zero": False}],
        f"ε ของคู่ break: {bi} แท่งแรกแกว่งอยู่ในโซน หลังสายจูงขาด ε อยู่นอกเส้นนอกสุดเป็นส่วนใหญ่ "
        f"และหลังแท่ง {z['last_middle_bar']} ไม่กลับเข้าโซนกลางอีก",
        f"ข้อมูลจำลอง · คู่ที่สายจูงขาดที่แท่ง {bi:,} · เส้นทั้งห้าคิดจาก {TRAIN} แท่งแรก (สิ่งที่คุณมีในมือก่อนเกิดเรื่อง) · "
        f"ก่อนขาด ε อยู่นอกเส้น P1–P99 เพียง {_n(z['before_beyond_1_99_pct'], 0)}% ของเวลา · หลังขาดอยู่นอกเส้น "
        f"{_n(z['after_beyond_1_99_pct'], 0)}% ของเวลา และหลังแท่ง {z['last_middle_bar']:,} ไม่กลับเข้าโซนกลาง "
        "(P10–P90) อีกเลย — วันที่ ε ทะลุเส้น 99% กราฟหน้าตาเหมือนโอกาสทองทุกประการ",
        xlabel="แท่งที่ (วัน)", panel_h=250, xbands=[(bi, N - 1, f"หลังสายจูงขาด (แท่ง {bi:,})", V.RED)])


def _chart_lookahead_lines(cid, res, f):
    d = res["demo"]["bad"]
    lines = res["lookahead"]["bad"]["lines"]
    b = f["lookahead"]["bad"]
    names = ["ε", "P90 · short เหนือเส้นนี้", "P50 · ออก", "P10 · long ใต้เส้นนี้"]
    colors = [V.DARK, V.BLUE, V.AMBER, V.RED]
    titles = {"full": ("เส้นจากข้อมูลทั้งช่วง — รู้อนาคต", f"ผลรวม {_n(b['full']['c5']['total_pct'], 1, True)}%"),
              "expanding": ("เส้นจากทุกแท่งตั้งแต่ต้นถึงวันนั้น (expanding)",
                            f"ผลรวม {_n(b['expanding']['c5']['total_pct'], 1, True)}%"),
              "rolling": (f"เส้นจาก {ROLL} แท่งล่าสุด (rolling)",
                          f"ผลรวม {_n(b['rolling']['c5']['total_pct'], 1, True)}%")}
    panels = [{"y": [d["eps"] * 100] + [ln * 100 for ln in lines[k][::-1]], "title": titles[k][0],
               "sub": titles[k][1], "color": colors, "names": names if k == "full" else None, "zero": False}
              for k in VARIANTS]
    counts = sorted({b[k]["c5"]["trades"] for k in VARIANTS})
    trades = f"{counts[0]}" if len(counts) == 1 else f"{counts[0]}–{counts[-1]}"
    still_open = all(b[k]["c5"]["open_at_end"] for k in VARIANTS)
    return V.stacked_panels(
        cid, panels,
        "ε ของคู่ที่ไม่มีสายจูง กับเส้น P10/P50/P90 สามแบบ: เส้นจากทั้งช่วงอยู่นิ่ง เส้นที่ใช้ได้จริงขยับตามราคา",
        f"ข้อมูลจำลอง · คู่ที่ไม่มีสายจูง · ε เส้นเดียวกันทั้งสามกรอบ (หน่วย %) ต่างกันที่เส้นแบ่งโซน · เส้นจากทั้งช่วง"
        f"รู้ล่วงหน้าว่า ε จะไปไกลแค่ไหน จึงวางตัวได้พอดี · เส้นที่คุณมีจริง ณ วันนั้นวิ่งตามหลัง ε เสมอ · ผลรวมของกฎ"
        f"เดียวกันในช่วงที่นับผล (หลังต้นทุน {f['settings']['cost_bps']} bps): "
        f"{_n(b['full']['c5']['total_pct'], 1, True)}% เมื่อรู้อนาคต เทียบกับ "
        f"{_n(b['expanding']['c5']['total_pct'], 1, True)}% และ {_n(b['rolling']['c5']['total_pct'], 1, True)}% "
        f"เมื่อใช้เส้นที่รู้แค่อดีต · เส้นเดียวนี้เทรดเพียง {trades} ไม้"
        + ("และไม้สุดท้ายยังเปิดค้าง" if still_open else "") + " — ภาพรวมจริงดูจาก"
        f"ค่าเฉลี่ย {WORLDS} โลกในรูปถัดไป",
        xlabel="แท่งที่ (วัน)", panel_h=150, share_y=True,
        xbands=[(TRAIN, N - 1, f"ช่วงที่นับผล (แท่ง {TRAIN}–{N - 1:,})")])


def _chart_lookahead(cid, res, f):
    mc = f["lookahead"]["mc"]
    labels = {"full": "เส้นจากทั้งช่วง (รู้อนาคต)", "expanding": "expanding (รู้แค่อดีต)",
              "rolling": f"rolling {ROLL} แท่ง (รู้แค่อดีต)"}
    colors = {"full": V.AMBER, "expanding": V.BLUE, "rolling": V.PURPLE}
    rows = [{"label": f"{world}\n{labels[k]}", "mid": mc[key][k]["total_mean_pct"], "lo": mc[key][k]["total_p5_pct"],
             "hi": mc[key][k]["total_p95_pct"], "color": colors[k]}
            for key, world in (("good", "มีสายจูง"), ("bad", "ไม่มีสายจูง")) for k in VARIANTS]
    g, b = mc["good"], mc["bad"]
    return V.dot_interval(
        cid, rows,
        "ผลรวมของกฎโซนเมื่อใช้เส้นสามแบบ บนโลกที่มีสายจูงและไม่มีสายจูง",
        f"ข้อมูลจำลอง {WORLDS} โลกต่อแบบ · ผลรวมของ {N - TRAIN} แท่งหลัง (ราว 3 ปี) หลังต้นทุน "
        f"{f['settings']['cost_bps']} bps · คู่ที่มีสายจูง: เส้นแบบไหนก็ได้ผลใกล้กัน "
        f"({_n(g['full']['total_mean_pct'], 0)}% เทียบ {_n(g['expanding']['total_mean_pct'], 0)}%) · "
        f"คู่ที่ไม่มีสายจูง: เส้นที่รู้อนาคตทำให้ดูเหมือนได้กำไรเฉลี่ย {_n(b['full']['total_mean_pct'], 0)}% "
        f"(กำไร {b['full']['profitable_pct']}% ของโลก) ทั้งที่เส้นที่ใช้ได้จริงให้ "
        f"{_n(b['expanding']['total_mean_pct'], 0)}% ± {_n(b['expanding']['total_mean_pm95_pct'], 1)} "
        f"(กำไร {b['expanding']['profitable_pct']}% ของโลก ≈ โยนเหรียญ) "
        "— การรู้อนาคตของเส้นแทบไม่ช่วยคู่ที่ดี แต่แต่งหน้าให้คู่ที่ไม่มีอะไรเลย",
        xlabel="ผลรวมของช่วงที่นับผล (% ของเงินรวมสองขา)", fmt=lambda v: _n(v, 0) + "%", mid_name="ค่าเฉลี่ย",
        row_h=42)


def _chart_trade(cid, res, f):
    t, ft = res["trade"], f["trade"]
    lo, hi = max(TRAIN, t["entry_bar"] - 30), t["exit_bar"] + 22
    bars = np.arange(lo, hi + 1)
    side = "short" if t["side"] < 0 else "long"
    return V.line_chart(
        cid, bars, [{"name": "z ของสเปรด", "y": t["z"][lo:hi + 1], "color": V.DARK}],
        "z ของคู่ good รอบไม้ตัวอย่าง: เข้าเมื่อ z แตะ 2 ออกเมื่อ z ข้าม 0",
        f"ข้อมูลจำลอง · คู่ที่มีสายจูง · ไม้แรกของครึ่งหลัง: สิ้นแท่ง {ft['entry_bar']} z = {_n(ft['z_entry'])} → เปิด "
        f"{side} สเปรด · สิ้นแท่ง {ft['exit_bar']} z = {_n(ft['z_exit'])} → ปิด · ถือ {ft['bars_held']} แท่ง ได้ "
        f"{_n(ft['gross_pct'])}% ของเงินรวมสองขา หักต้นทุนครบรอบ {_n(ft['cost_pct'])}% เหลือ {_n(ft['net_pct'])}% · "
        f"z วัดด้วย σ̂ ของ {TRAIN} แท่งแรก",
        xlabel="แท่งที่ (วัน)", ylabel="z", markers=False,
        hlines=[(ENTRY, f"เข้า short: z ≥ {ENTRY:g}", V.RED), (EXIT, f"ออก: z ข้าม {EXIT:g}"),
                (-ENTRY, f"เข้า long: z ≤ {_n(-ENTRY, 0)}", V.GREEN)],
        xbands=[(t["entry_bar"], t["exit_bar"], f"ถือ {ft['bars_held']} แท่ง")],
        callouts=[(t["entry_bar"], t["z_entry"], f"เข้า · z = {_n(ft['z_entry'])}", -70, -26),
                  (t["exit_bar"], t["z_exit"], f"ออก · z = {_n(ft['z_exit'])}", -64, 44)])


def _chart_threshold(cid, res, f):
    """สามกรอบแกน x ร่วม (ไม้ต่อปี · กำไรต่อไม้ · ผลตอบแทนต่อปี) มีจุดที่เกณฑ์ที่ทดสอบจริง และวงใหญ่ที่จุดสูงสุด
    ของผลตอบแทนต่อปีแต่ละระดับต้นทุน — ให้เห็นว่าจุดสูงสุดขยับออกเมื่อต้นทุนสูงขึ้น"""
    th = f["threshold"]
    keys = [_key("e", e) for e in ENTRIES]
    xs = np.array(ENTRIES, float)
    styles = [(COST_NAMES[c], V.SERIES[i], V.DASHES[i]) for i, c in enumerate(COSTS)]
    panels = [("จำนวนไม้ต่อปี", None, [[th[k]["trades_per_year"] for k in keys]], [(None, V.DARK, None)], False),
              ("กำไรสุทธิต่อไม้", "% ของเงินรวมสองขา",
               [[th[k][_ckey(c)]["net_per_trade_pct"] for k in keys] for c in COSTS], styles, False),
              ("ผลตอบแทนต่อปี (%)", "= ไม้ต่อปี × กำไรต่อไม้",
               [[th[k][_ckey(c)]["ann_return_pct"] for k in keys] for c in COSTS], styles, True)]
    left, right, width, ph, bottom = 58, 18, 760, 118, 46
    tops, y = [], 0.0
    for i, p in enumerate(panels):
        y += 15 + 17 * (2 if p[4] else 1) + (6 if i else 0)     # กรอบล่างมี legend ยาว → จองสองแถว
        tops.append(y)
        y += ph
    fig = V.Fig(cid, width, y + bottom)
    xlim = (ENTRIES[0] - 0.12, ENTRIES[-1] + 0.12)
    for i, (title, sub, ys, sty, mark_best) in enumerate(panels):
        ylim = V.auto_lim(*[np.asarray(v, float) for v in ys], include=(0.0,), n=4)
        pan = fig.panel(xlim, ylim, x=left, y=tops[i], w=width - left - right, h=ph)
        pan.grid(n=4, xticks=list(ENTRIES)).yaxis()
        if ylim[0] < 0 < ylim[1]:
            pan.hline(0.0, color="#94a3b8")
        for v, (_, color, dash) in zip(ys, sty):
            pan.line(xs, v, color, dash=dash)
            pan.scatter(xs, v, color, r=3.2, ring=True)
            if mark_best:
                b = int(np.argmax(v))
                pan.scatter([xs[b]], [v[b]], color, r=6.5, ring=True)
        pan.title(title, sub)
        items = [(nm, col, "line", dash) for nm, col, dash in sty if nm]
        if mark_best:
            items.append(("จุดสูงสุดของแต่ละเส้น", V.INK, "ring"))
        if items:
            pan.legend(items)
        last = i == len(panels) - 1
        pan.xaxis(ticks=list(ENTRIES), labels=[f"{e:g}" for e in ENTRIES] if last else False,
                  title="เกณฑ์เข้า: เปิดสถานะเมื่อ |z| ≥ ค่านี้ (z วัดด้วย σ ของช่วง train)" if last else None)
    best = th["best"]
    return fig.svg(
        "เกณฑ์เข้ากว้างขึ้น: ไม้ต่อปีลดลง กำไรต่อไม้เพิ่มขึ้น และเกณฑ์ที่ให้ผลตอบแทนต่อปีสูงสุดขยับออกเมื่อต้นทุนสูงขึ้น",
        f"ข้อมูลจำลอง {WORLDS} โลกที่มีสายจูง · walk-forward · ออกที่ z = 0 · ค่าเฉลี่ยทุกโลก · จุด = เกณฑ์ที่ทดสอบ · "
        f"เกณฑ์กว้างขึ้น ไม้น้อยลง ({_n(th['e0_5']['trades_per_year'], 1)} → {_n(th['e3']['trades_per_year'], 1)} "
        f"ไม้ต่อปี) แต่ไม้อ้วนขึ้น ({_n(th['e0_5']['gross_per_trade_pct'])}% → {_n(th['e3']['gross_per_trade_pct'])}% "
        f"ก่อนต้นทุน) · วงใหญ่ = เกณฑ์ที่ให้ผลตอบแทนต่อปีสูงสุด ขยับออกตามต้นทุน: "
        f"{best['c5']['entry_by_return']} ที่ 5 bps → {best['c20']['entry_by_return']} ที่ 20 bps → "
        f"{best['c50']['entry_by_return']} ที่ 50 bps (เมื่อไม่มีต้นทุน 0.5 คือขอบล่างของตาราง) · "
        f"z วัดด้วย σ ของช่วง train: z = 2 ตรงกับราว {_n(th['e2']['true_sigma_at_entry'], 1)} σ จริง")


def _stop_rows(st):
    rows = []
    for world, name, color in (("good", "สายจูงอยู่", V.GREEN), ("break", "สายจูงขาด", V.RED)):
        for key, _, _ in STOP_RULES:
            c = st[world][key]
            rows.append({"label": f"{name} · {STOP_LABELS[key]}", "mid": c["total_mean_pct"],
                         "lo": c["total_p5_pct"], "hi": c["total_p95_pct"], "color": color})
    return rows


def _stop_cap_head(f, ruler_text):
    return (f"ข้อมูลจำลอง {WORLDS} โลกที่สายจูงอยู่ และ {WORLDS_BREAK:,} โลกที่สายจูงขาด ณ แท่งสุ่ม · {ruler_text} · "
            f"ผลรวมของแท่ง {STOP_FROM}–{N - 1:,} (ราว {_n(f['settings']['stop_test_years'], 0)} ปี) หลังต้นทุน "
            f"{f['settings']['cost_bps']} bps · ")


def _chart_stop(cid, res, f):
    st = f["stops"]["wf"]
    g, b = st["good"], st["break"]
    return V.dot_interval(
        cid, _stop_rows(st),
        "ผลรวมของกฎเดียวกันเมื่อใส่ stop แบบต่าง ๆ บนโลกที่สายจูงอยู่และโลกที่สายจูงขาด (ไม้บรรทัด walk-forward)",
        _stop_cap_head(f, f"ไม้บรรทัด walk-forward (ประมาณใหม่ทุก {WF_REFIT} แท่ง)")
        + f"สายจูงอยู่: stop ที่ |z| = 3 ลดผลรวมเฉลี่ยจาก {_n(g['none']['total_mean_pct'], 0)}% เหลือ "
        f"{_n(g['s3']['total_mean_pct'], 0)}% (อัตราชนะ {g['none']['hit_rate_pct']}% → {g['s3']['hit_rate_pct']}%) · "
        f"สายจูงขาด: ค่าเฉลี่ยของ 10% ของโลกที่แย่ที่สุด {_n(b['none']['tail10_pct'], 0)}% เมื่อไม่มี stop เทียบ "
        f"{_n(b['s4']['tail10_pct'], 0)}% (stop 4) และ {_n(b['s3']['tail10_pct'], 0)}% (stop 3) — stop ที่ระดับ z "
        f"ไม่ได้ทำให้ปลายล่างดีขึ้น · จำกัดเวลาถือ {MAX_HOLD} แท่งได้ {_n(b['t36']['tail10_pct'], 0)}%",
        xlabel="ผลรวมตลอดช่วงสอบ (% ของเงินรวมสองขา)", fmt=lambda v: _n(v, 0) + "%", mid_name="ค่าเฉลี่ย",
        row_h=30)


def _chart_stop_fixed(cid, res, f):
    st = f["stops"]["fixed"]
    g, b = st["good"], st["break"]
    return V.dot_interval(
        cid, _stop_rows(st),
        "ผลรวมของกฎเดียวกันเมื่อใส่ stop แบบต่าง ๆ เมื่อใช้ไม้บรรทัดตายตัว",
        _stop_cap_head(f, f"โลกชุดเดียวกับรูปก่อน แต่ไม้บรรทัดตายตัว: ประมาณครั้งเดียวจาก {FIX_TRAIN} แท่งแรกแล้วไม่แตะอีก "
                          "(แบบลากเส้นโซนครั้งเดียว)")
        + f"สายจูงอยู่: stop ที่ |z| = 3 ลดผลรวมเฉลี่ยจาก {_n(g['none']['total_mean_pct'], 0)}% เหลือ "
        f"{_n(g['s3']['total_mean_pct'], 0)}% · สายจูงขาด: ค่าเฉลี่ยของ 10% ของโลกที่แย่ที่สุด "
        f"{_n(b['none']['tail10_pct'], 0)}% เมื่อไม่มี stop · stop ที่ |z| = 4 ดึงขึ้นเป็น "
        f"{_n(b['s4']['tail10_pct'], 0)}% และในกลุ่มโลกที่แย่ที่สุดเมื่อไม่มี stop นั้น stop ที่ |z| = 4 ทำได้ดีกว่า "
        f"{b['s4']['none_tail_helps_pct']}% ของโลก · แลกกับค่าเฉลี่ยที่ลดจาก {_n(b['none']['total_mean_pct'], 0)}% "
        f"เหลือ {_n(b['s4']['total_mean_pct'], 0)}%",
        xlabel="ผลรวมตลอดช่วงสอบ (% ของเงินรวมสองขา)", fmt=lambda v: _n(v, 0) + "%", mid_name="ค่าเฉลี่ย",
        row_h=30)


def _chart_pierce(cid, res, f):
    p = f["pierce"]
    rows = []
    for key in BUCKET_LABELS:
        for world, name, color in (("good", "สายจูงอยู่", V.GREEN), ("break_after", "หลังสายจูงขาด", V.RED)):
            c = p["forward"][world][key]
            rows.append({"label": f"{BUCKET_LABELS[key]} · {name}", "mid": c["mean_pct"], "lo": c["p5_pct"],
                         "hi": c["p95_pct"], "color": color})
    g, b = p["forward"]["good"], p["forward"]["break_after"]
    return V.dot_interval(
        cid, rows,
        f"ผลตอบแทน {FWD} แท่งข้างหน้าของการเปิดสวน z แยกตามระดับ |z| ในโลกที่สายจูงอยู่และหลังสายจูงขาด",
        f"ข้อมูลจำลอง {WORLDS} โลกที่สายจูงอยู่ และ {WORLDS_BREAK:,} โลกที่สายจูงขาด · ผลขั้นต้น {FWD} แท่งข้างหน้า "
        f"(หนึ่ง half-life) ของการเปิดสวน z ณ ระดับ |z| ต่าง ๆ · สายจูงอยู่: ยิ่ง z ไกล ค่าเฉลี่ยยิ่งสูง "
        f"({_n(g['z1_2']['mean_pct'], 1)}% → {_n(g['z4_up']['mean_pct'], 1)}%) — จุดที่ stop สั่งตัดคือจุดที่ค่าคาดหวัง"
        f"สูงที่สุด · หลังสายจูงขาด: ที่ |z| ≥ 4 ค่าเฉลี่ยเหลือ {_n(b['z4_up']['mean_pct'], 1)}% และปลายล่างลึกถึง "
        f"{_n(b['z4_up']['p5_pct'], 1)}% · เมื่อ |z| แตะ {PIERCE:g} ครั้งแรก ε กลับเข้ามาภายใน {MAX_HOLD} แท่ง "
        f"{p['good']['back_pct']}% ของครั้งในโลกที่สายจูงอยู่ แต่เพียง {p['break_after']['back_pct']}% หลังสายจูงขาด "
        "— ทั้งสองกรณีหน้าตาเหมือนกันบนกราฟ ณ วันที่แตะ",
        xlabel=f"ผลขั้นต้น {FWD} แท่งข้างหน้า (% ของเงินรวมสองขา)", fmt=lambda v: _n(v, 1) + "%",
        mid_name="ค่าเฉลี่ย", row_h=32)


def charts(res=None):
    """กราฟทุกรูปของตอนที่ 4 → {ชื่อ: html}  (สร้างจากผลการรันชุดเดียวกับ figures)"""
    res = res or run()
    f = figures(res)
    builders = {
        "sas-p4-zones-good": _chart_zones_good,
        "sas-p4-zones-bad": _chart_zones_bad,
        "sas-p4-zones-break": _chart_zones_break,
        "sas-p4-lookahead-lines": _chart_lookahead_lines,
        "sas-p4-lookahead": _chart_lookahead,
        "sas-p4-trade": _chart_trade,
        "sas-p4-threshold": _chart_threshold,
        "sas-p4-stop": _chart_stop,
        "sas-p4-stop-fixed": _chart_stop_fixed,
        "sas-p4-pierce": _chart_pierce,
    }
    return {cid: build(cid, res, f) for cid, build in builders.items()}


# ───────────────────────── สรุปเมื่อรันตรง ๆ ─────────────────────────

def _print_summary(f):
    s, z, st = f["settings"], f["zones"], f["stability"]
    la, tr, th, ex, sp, pc = f["lookahead"], f["trade"], f["threshold"], f["exits"], f["stops"], f["pierce"]
    line = "─" * 78
    print(f"ห้องทดลองตอนที่ 4 — อ่านกราฟ ε กับเส้น VaR (ข้อมูลจำลองทั้งหมด · {s['bars']:,} แท่งต่อโลก)")
    print(f"Monte Carlo: {s['worlds']} โลก good / fake · {s['worlds_break']:,} โลก break · 4b ใช้ {s['worlds_zone']:,} โลก")

    print(f"\n{line}\n4a  กราฟโซน: ε จาก α̂, β̂ ของ {s['train_bars']} แท่งแรก · เส้นจากทั้งช่วง (แบบสไลด์)\n{line}")
    print(f"{'':10s}{'β̂':>7s}{'P1%':>8s}{'P10%':>8s}{'P50%':>8s}{'P90%':>8s}{'P99%':>8s}{'ตัดเส้นกลาง':>13s}"
          f"{'ค้างฝั่งเดียวนานสุด':>20s}{'ออกนอก 10/90':>14s}{'นานสุด':>8s}")
    for k, name in (("good", "good"), ("bad", "bad (fake)"), ("break", "break")):
        v = z[k]
        print(f"{name:10s}{v['beta']:7.3f}{v['p1_pct']:8.2f}{v['p10_pct']:8.2f}{v['p50_pct']:8.2f}{v['p90_pct']:8.2f}"
              f"{v['p99_pct']:8.2f}{v['crossings']:10d} ครั้ง{v['longest_one_side_bars']:14d} แท่ง"
              f"{v['visits']:9d} ครั้ง{v['visit_longest_bars']:6d} แท่ง")
    v = z["break"]
    print(f"คู่ break (สายจูงขาดแท่ง {v['break_bar']}): นอกเส้น P1–P99 ของ {s['train_bars']} แท่งแรก "
          f"{v['before_beyond_1_99_pct']}% ของเวลาก่อนขาด → {v['after_beyond_1_99_pct']}% หลังขาด · "
          f"หลังแท่ง {v['last_middle_bar']} ไม่กลับเข้า P10–P90 อีก")

    print(f"\n{line}\n4b  โซนครึ่งแรกเทียบครึ่งหลัง (หน่วย = sd ของครึ่งแรก)\n{line}")
    for k in ("good", "bad", "break"):
        v = st[k]
        print(f"{k:6s} ครึ่งแรก P10/P50/P90 = {v['first_p10_sigma']:+.2f} / {v['first_p50_sigma']:+.2f} / "
              f"{v['first_p90_sigma']:+.2f}   ครึ่งหลัง = {v['second_p10_sigma']:+.2f} / {v['second_p50_sigma']:+.2f} / "
              f"{v['second_p90_sigma']:+.2f}   ครึ่งหลังอยู่นอกเส้นครึ่งแรก {v['second_outside_pct']}% ของเวลา")
    for k in ("good", "bad"):
        v = st["mc"][k]
        print(f"MC {v['worlds']:,} โลก {k:4s}: |เส้นกลางเลื่อน| ค่ากลาง {v['shift_abs_p50_sigma']} sd "
              f"(5–95%: {v['shift_abs_p5_sigma']} ถึง {v['shift_abs_p95_sigma']}) · ครึ่งหลังนอกเส้น "
              f"{v['second_outside_p50_pct']}% ({v['second_outside_p5_pct']} ถึง {v['second_outside_p95_pct']}%)")

    print(f"\n{line}\n4c  เส้นที่รู้อนาคต: short เหนือ P90 · long ใต้ P10 · ออกที่ P50 · นับผล {s['test_bars']} แท่งหลัง"
          f"\n{line}")
    for k in ("good", "bad"):
        for name in VARIANTS:
            a, b = la[k][name]["c0"], la[k][name]["c5"]
            print(f"คู่ตัวอย่าง {k:4s} {name:9s}: c=0 ผลรวม {a['total_pct']:+6.1f}% Sharpe {a['sharpe']:+5.2f} · "
                  f"c=5bps ผลรวม {b['total_pct']:+6.1f}% Sharpe {b['sharpe']:+5.2f} (lag 2: {b['sharpe_lag2']:+5.2f}) · "
                  f"{b['trades']} ไม้")
    for k in ("good", "bad"):
        for name in VARIANTS:
            v = la["mc"][k][name]
            print(f"MC {la['mc'][k]['worlds']} โลก {k:4s} {name:9s}: ผลรวมเฉลี่ย {v['total_mean_pct']:+4d}% "
                  f"(±{v['total_mean_pm95_pct']}) (5–95%: {v['total_p5_pct']:+d} ถึง {v['total_p95_pct']:+d}) · "
                  f"กำไร {v['profitable_pct']}% ของโลก · Sharpe {v['sharpe_mean']:+.1f} (lag 2: {v['sharpe_lag2_mean']:+.1f})")
        print(f"   → ส่วนต่างจากการรู้อนาคตของเส้น ({k}): {la['mc'][k]['gap_full_minus_expanding_pct']:+d} จุด")

    print(f"\n{line}\nแกะหนึ่งไม้ (คู่ good ตัวอย่าง · ไม้บรรทัดจาก {s['train_bars']} แท่งแรก)\n{line}")
    print(f"สิ้นแท่ง {tr['entry_bar']}: z = {tr['z_entry']:+.2f} (ε = {tr['eps_entry_pct']:+.2f}%) → เปิด {tr['side']} สเปรด")
    print(f"สิ้นแท่ง {tr['exit_bar']}: z = {tr['z_exit']:+.2f} (ε = {tr['eps_exit_pct']:+.2f}%) → ปิด · ถือ "
          f"{tr['bars_held']} แท่ง · Y เปลี่ยน {tr['dy_pct']:+.2f}% · X เปลี่ยน {tr['dx_pct']:+.2f}%")
    print(f"กำไรขั้นต้น {tr['gross_pct']:.2f}% ของเงินรวมสองขา (= (z เข้า − z ออก)·σ̂/(1+β̂) = {tr['formula_pct']:.2f}%) "
          f"− ต้นทุน {tr['cost_pct']:.2f}% = สุทธิ {tr['net_pct']:.2f}%")
    print(f"ทั้งครึ่งหลัง: {tr['trades']} ไม้ · ขั้นต้นเฉลี่ย {tr['gross_avg_pct']:.2f}% ต่อไม้ (สูตร 2σ̂/(1+β̂) = "
          f"{tr['formula_avg_pct']:.2f}%) · ชนะ {tr['hit_rate_pct']}% · ผลรวมสุทธิ {tr['total_net_pct']:+.1f}%")

    print(f"\n{line}\n4d  เกณฑ์เข้า (walk-forward · {th['worlds']} โลก good · exit 0) — z วัดด้วย σ ของช่วง train: "
          f"sd(z) นอกตัวอย่าง = {th['z_sd']} ({th['z_sd_p5']}–{th['z_sd_p95']})\n{line}")
    print(f"{'entry':>6s}{'σ จริงตอนเข้า':>15s}{'ไม้/ปี':>8s}{'ถือ(แท่ง)':>11s}{'ขั้นต้น/ไม้':>12s}"
          + "".join(f"{'ผล/ปี c=' + _ckey(c)[1:]:>13s}" for c in COSTS) + f"{'Sharpe c=5':>12s}{'(lag 2)':>9s}")
    for e in ENTRIES:
        v = th[_key("e", e)]
        print(f"{e:6g}{v['true_sigma_at_entry']:15.1f}{v['trades_per_year']:8.1f}{v['hold_bars']:11d}"
              f"{v['gross_per_trade_pct']:11.2f}%"
              + "".join(f"{v[_ckey(c)]['ann_return_pct']:12.1f}%" for c in COSTS)
              + f"{v['c5']['sharpe']:12.1f}{v['c5']['sharpe_lag2']:9.1f}")
    print("เกณฑ์ที่ให้ผลตอบแทนต่อปีสูงสุด: "
          + " · ".join(f"c = {_ckey(c)[1:]} bps → {th['best'][_ckey(c)]['entry_by_return']}" for c in COSTS))
    print("เกณฑ์ที่ให้ Sharpe สูงสุด:      "
          + " · ".join(f"c = {_ckey(c)[1:]} bps → {th['best'][_ckey(c)]['entry_by_sharpe']}" for c in COSTS))
    print("ถ้ารู้ค่าจริง (z = ε จริง ÷ σ จริง): สูตร (entry − exit)·σ/(1+β) เทียบกำไรขั้นต้นต่อไม้ที่เกิดจริง")
    for e in ENTRIES:
        v = th["known"][_key("e", e)]
        print(f"{e:6g}: สูตร {v['formula_pct']:.2f}% · จริง {v['gross_per_trade_pct']:.2f}% "
              f"(เข้าจริงที่ |z| = {v['z_in']:.2f} ออกเลย 0 ไป {v['z_out']:.2f}) · {v['trades_per_year']:.1f} ไม้/ปี")

    print(f"\n{line}\n4e  จุดออก (entry 2 · walk-forward · {ex['worlds']} โลก good)\n{line}")
    for key, name in (("x0", "ออกที่ z = 0"), ("x0_5", "ออกก่อนที่ |z| = 0.5"), ("flip", "รอถึงแถบตรงข้าม (−2)")):
        v = ex[key]
        print(f"{name:24s}: {v['trades_per_year']:.1f} ไม้/ปี · ถือ {v['hold_bars']} แท่ง · อยู่ในตลาด "
              f"{v['in_market_pct']}% · c=5bps: {v['c5']['net_per_trade_pct']:.2f}%/ไม้ · {v['c5']['ann_return_pct']:.1f}%/ปี "
              f"· Sharpe {v['c5']['sharpe']:.1f} (lag 2: {v['c5']['sharpe_lag2']:.1f})")

    for ruler, title in (("wf", f"walk-forward (ประมาณใหม่ทุก {s['wf_refit_bars']} แท่ง)"),
                         ("fixed", f"ไม้บรรทัดตายตัว (ประมาณครั้งเดียวจาก {s['fixed_train_bars']} แท่งแรก)")):
        print(f"\n{line}\n4f  stop — {title} · entry 2 · exit 0 · c = {s['cost_bps']} bps · นับผลแท่ง "
              f"{s['stop_from_bar']}–{s['bars'] - 1}\n{line}")
        for world, name in (("good", "โลกที่สายจูงอยู่"), ("break", "โลกที่สายจูงขาด")):
            print(f"{name} ({sp[ruler][world]['worlds']:,} โลก)")
            print(f"  {'':26s}{'Sharpe':>8s}{'ผลรวมเฉลี่ย':>13s}{'p5':>7s}{'tail10':>9s}{'ในโลกแย่สุดของ none':>22s}"
                  f"{'DD เฉลี่ย':>11s}")
            for key in STOP_LABELS:
                v = sp[ruler][world][key]
                paired = (f"{v['none_tail_pct']:+5d}% (ดีกว่า {v['none_tail_helps_pct']:3d}%)" if key != "none"
                          else f"{'':>20s}")
                print(f"  {STOP_LABELS[key]:26s}{v['sharpe_mean']:8.1f}{v['total_mean_pct']:12d}%"
                      f"{v['total_p5_pct']:6d}%{v['tail10_pct']:8d}%  {paired}{v['max_dd_mean_pct']:9d}%")

    print(f"\n{line}\n4g  เมื่อ |z| แตะ {pc['touch_z']} ครั้งแรก (ไม้บรรทัด ณ วันที่แตะ · ดูต่อ {pc['window_bars']} แท่ง)\n{line}")
    for key, name in (("good", "โลกที่สายจูงอยู่"), ("break_before", "โลก break ก่อนขาด"),
                      ("break_after", "โลก break หลังขาด")):
        v = pc[key]
        print(f"{name:20s}: {v['events']:6,d} ครั้ง · กลับเข้า |z| < {pc['inside_z']} {v['back_pct']}% "
              f"(ค่ากลาง {v['bars_to_back_median']} แท่ง) · ผลเฉลี่ยของการสวน {v['gross_mean_pct']:+.1f}% · "
              f"เปอร์เซ็นไทล์ 5 {v['gross_p5_pct']:+.1f}% · ขาดทุน {v['losing_pct']}% ของครั้ง")
    print(f"ผล {pc['forward_bars']} แท่งข้างหน้าของการสวน z แยกตามระดับ |z| (ค่าเฉลี่ย · ช่วง 5–95%)")
    for key, name in BUCKET_LABELS.items():
        g, b = pc["forward"]["good"][key], pc["forward"]["break_after"][key]
        print(f"  {name:8s} สายจูงอยู่ {g['mean_pct']:+.1f}% ({g['p5_pct']:+.1f} ถึง {g['p95_pct']:+.1f}) · "
              f"หลังขาด {b['mean_pct']:+.1f}% ({b['p5_pct']:+.1f} ถึง {b['p95_pct']:+.1f})")


if __name__ == "__main__":
    _print_summary(figures())
