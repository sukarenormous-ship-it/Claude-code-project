#!/usr/bin/env python3
"""ห้องทดลองของตอนที่ 5 — "คลินิก backtest: ทำไมขาดทุนตั้งแต่ยังไม่ได้เทรดจริง"

ทุกการทดลองใช้ข้อมูลจำลองที่ "รู้เฉลย" (sas_core.make_pair) แล้วทำ backtest สองแบบเทียบกัน:
แบบที่คนส่วนใหญ่เผลอทำ (ผิด) กับแบบที่ควรทำ (ถูก) แล้วรายงาน "ช่องว่าง" เป็นตัวเลข
ค่าตั้งต้นของทุกโรค ยกเว้นที่บอกไว้: 1,500 แท่งต่อโลก · walk-forward (train 250 แท่ง ประมาณใหม่ทุก 21 แท่ง)
เข้าเมื่อ |z| ≥ 2 ออกเมื่อ z ข้าม 0 · ต้นทุน c = 5 bps ต่อขาต่อเที่ยว · สถานะที่ตัดสินใจตอนสิ้นแท่ง t
เริ่มรับผลแท่ง t+1 (lag = 1) และรายงาน lag = 2 คู่กันเสมอ · z ของ walk-forward วัดด้วย σ ที่ประมาณจากช่วง train
(ไม่ใช่ σ จริง — ดู z_sd)

โรคที่ตรวจ (คีย์ใน figures() ใช้ชื่อเดียวกัน: d1 … d10)
  D1  เลือกคู่ด้วย correlation     300 โลก good เทียบ 300 โลก fake (และ fake ที่ตั้งให้ correlation เท่า good)
  D2  คัดจากหลายคู่ (selection)    400 fake + 40 good · คัดด้วย Engle-Granger บน 750 แท่งแรก แล้วดู 750 แท่งหลัง
                                  และ "10 อันดับ Sharpe สูงสุดในช่วงคัดเลือก" เทียบกับช่วงพิสูจน์ — ค่าเฉลี่ยของแค่ 10 คู่
                                  ขึ้นกับดวงของจักรวาลมาก จึงสุ่มจักรวาลซ้ำ 1,000 ครั้งจากสระเดิม (bootstrap) แล้วรายงาน
                                  ค่ากลาง + ช่วง 5–95% คู่กับผลของการสแกนจริงหนึ่งรอบ
  D3  มองอนาคต (look-ahead)       β, μ, σ จากข้อมูลทั้งช่วง เทียบ walk-forward บน good / drift / fake อย่างละ 100 โลก
      + บั๊กเรียงแกนเวลา           lag 0 / 1 / 2 — lag = 0 "ลงโทษ" กลยุทธ์ mean reversion: สถานะที่เพิ่งตัดสินใจ
                                  จากราคาปิดแท่ง t ถูกคิดผลของแท่ง t เอง ซึ่งก็คือการเคลื่อนที่ "ออกห่าง" ที่ทำให้
                                  เกิดสัญญาณเข้า (ขาดทุนทันที) และแท่งที่ z วิ่งกลับถึงค่าเฉลี่ยจนเกิดสัญญาณออก
                                  ก็ไม่ถูกนับให้ (เพราะสถานะเป็น 0 แล้วในแท่งนั้น) — เสียทั้งขาเข้าและขาออก
  D4  ต้นทุนใหญ่กว่ากำไรต่อไม้     σ_eq ∈ {0.5, 1, 2, 4}% × c ∈ {0, 2, 5, 10, 20, 50} bps อย่างละ 100 โลก
                                  เทียบกำไรขั้นต้นต่อไม้ที่วัดได้กับสูตร (entry − exit)·σ/(1+β)
  D5  หน้าต่าง z-score            หน้าต่างเลื่อน 1–32 เท่าของ half-life บนโลกปกติ และโลกที่ค่ากลางไหลช้า ๆ (200 โลก)
  D6  การดึงกลับปลอมจากราคาพิมพ์   สเปรดจริงช้า (half-life 40) + noise ของราคาที่เห็น 0.3% ต่อขา
                                  สัญญาณมาจากราคาที่เห็นทั้งสองกรณี · ลงบัญชีที่ราคาที่เห็น เทียบกับราคาจริง
  D7  stop ที่ตัดกำไรทิ้ง          stop ที่ |z| = 2.5 / 3 / 4 เทียบกับไม่มี stop บนโลก good และโลก break
  D8  สายจูงขาดแต่ไม่มีสวิตช์ตัด     300 โลก break: ไม่ทำอะไร / จำกัดเวลาถือ / เฝ้าด้วย Engle-Granger เลื่อน / ทั้งสอง
                                  และ "ราคาที่ต้องจ่าย" ของสวิตช์บนโลก good (สัญญาณเตือนผิด) · หางด้านขาดทุนวัดสองแบบ:
                                  เปอร์เซ็นไทล์ที่ 5 และค่าเฉลี่ยของ 5% ของโลกที่แย่ที่สุด (นิ่งกว่า เพราะใช้ทุกโลกในหาง)
  D9  ข้อมูลน้อยเกินจะบอกอะไร      Sharpe ของ 1 ปี: คู่ good ติดลบได้บ่อยแค่ไหน · คู่ fake ดูดีได้บ่อยแค่ไหน (1,000 โลก)
  D10 ชุดตรวจตัวเอง 6 ข้อ          คำนวณแบบกลไกบนคู่ตัวอย่าง good / fake / drift / break / noisy
                                  + อัตราผ่านของแต่ละข้อบนโลก good และ fake 300 โลก
  clinic  ตารางสรุป: อาการ · วิธีตรวจ · ตัวเลข "ทำผิด / ทำถูก / ช่องว่าง" ของแต่ละโรค

การปัดตัวเลข (สำคัญสำหรับคนเขียนบท)
  ตัวเลขจาก Monte Carlo ปัดให้หน่วยของหลักสุดท้าย ≥ ความคลาดจากการสุ่ม (SE ของค่าเฉลี่ย สัดส่วน หรือเปอร์เซ็นไทล์
  ข้ามโลก) — ค่าวิกฤตที่จำลอง ≥ 2 SE · จึงบางค่าเหลือทศนิยมหนึ่งตำแหน่ง จำนวนเต็ม หรือหลักสิบ (ให้เขียนว่า "ราว")
  แต่ค่าที่ต่างจากศูนย์ชัดเจนจะไม่ถูกปัดจนหลักแรกหาย · ตรวจแล้วด้วยการเปลี่ยนเลขสุ่มทั้งชุด: หลักสุดท้ายขยับได้ราว ±1
  ค่าของคู่ตัวอย่างคู่เดียว จำนวนนับ และสูตร เป็นข้อเท็จจริง ไม่ได้ปัดแบบนี้

วิธีรัน
    python3 tools/sas_exp5.py          # พิมพ์สรุปตัวเลขสำคัญ (ราว 50 วินาที)
ใช้จากโค้ด
    import sas_exp5 as E
    res = E.run()         # คำนวณทั้งหมด (เก็บผลไว้ เรียกซ้ำไม่คิดใหม่)
    E.figures()["d4"]     # ตัวเลขที่ปัดแล้ว พร้อมลงในบท
    E.charts()            # {"sas-p5-…": html}

คีย์ของ figures()  (ทุกค่าเป็นตัวเลขที่ปัดแล้ว · หน่วยอยู่ท้ายชื่อคีย์: _pct, _bps, _bars, _sigma)
    about.<d1…d10|common>        ข้อความสั้น ๆ บอกการตั้งค่าของแต่ละการทดลอง
    settings.*                   ค่าตั้งต้นร่วม + ค่าวิกฤต Engle-Granger ที่ 750 แท่ง
    d1.<good|fake|fake_tight>.*  sharpe_mean/p5/p50/p95 · sharpe_lag2_mean · profitable_pct · ret_corr_median · z_sd
    d2.level5|level1.*           การสแกนจริง: cutoff · selected · tp · fp · precision_pct · oos_sharpe_good/fake/all
                                 + fp_expected · precision_expected_pct · fp_p5/p95 · precision_p5/p95_pct (ถ้าสแกนจักรวาลแบบนี้ซ้ำ: ทวินาม)
    d2.top_backtest|top_eg|top_fake_only.*   ค่ากลางข้ามจักรวาล: n_good · sharpe_in · sharpe_out · drop
                                 · sharpe_in/out_p5/p95 · การสแกนจริง (วงม่วงในกราฟ): scan_sharpe_in/out · scan_n_good/fake
    d3.<good|drift|fake>.*       sharpe_lookahead · sharpe_wf · gap · profitable_*_pct
    d3.lag.<mc|demo>.lag0|lag1|lag2.*        sharpe · ann_return_pct
    d3.lag.mc.*                  gap_lag0 · lag0_return_lost_pct · lag0_entry_bar_bps · lag0_exit_bar_bps
    d4.<s0_5|s1|s2|s4>.<c0…c50>.*            sharpe · ann_return_pct · profitable_pct
    d4.<s…>.*                    gross_per_trade_bps · formula_per_trade_bps · formula_converted_bps · breakeven_c_bps
    d4.sigma_min_formula_pct|sigma_min_measured_pct.<c2…c50>   · d4.z_sd · d4.entry_true_sigma
    d5.<good|drifting>.<w12…w384|fixed>.*    sharpe · sharpe_lag2 · ann_return_pct · trades_per_year
    d5.<good|drifting>.*         best_sharpe · plateau_lo_mult–plateau_hi_mult (ช่วงที่ดีพอ ๆ กัน) · gap_*
    d5.bound.*                   เพดาน |z| ของหน้าต่างที่รวมแท่งปัจจุบัน
    d6.<tight|wide>.*            hl_print_bars · hl_true_bars · ac1_print · noise_to_sigma_pct
    d6.<tight|wide>.<wf|short>.<print_lag0|print_lag1|print_lag2|true_lag1|true_lag2>.*   sharpe · ann_return_pct
    d7.<good|break>.<none|stop4|stop3|stop2_5>.*   sharpe · total_pct · hit_rate_pct
    d8.<break|good>.<none|time|monitor_250|monitor_500|both>.*   total_mean_pct · total_p5_pct · sharpe
                                 (break มี after_mean_pct · after_p5_pct · after_worst5_mean_pct เพิ่ม)
                                 · blocked_*_pct · delay_median_*_bars
    d9.<good|slow|fake>.*        sharpe_p5/p50/p95 · negative_pct · positive_pct · above1_pct · trades_mean
    d9.five_year.<good|fake>.*   ค่าเดียวกันเมื่อดูราว 5 ปี (โลกชุด D1)
    d10.rules.* · d10.pairs.<good|fake|drift|break|noisy>.* · d10.mc.<good|fake>.pass_*_pct · pass_all_n
                                 (eg_p_text ใช้แทน eg_p เมื่อ p < 0.001 · half_life_test_bars อาจเป็น "∞")
    clinic.<d1…d9|d3_lag|battery>.*   name · symptom · test · fix · wrong_label · wrong · right_label · right · gap · unit
                                 (gap = wrong − right)
    outputs.battery              ตาราง ASCII ของชุดตรวจ สำหรับ <!--OUT:p5.outputs.battery-->

เลขสุ่ม: C.rng(500 … 599) เท่านั้น — รันกี่ครั้งก็ได้ตัวเลขเดิม
ตัวแปรที่จงใจ "โกง" ตั้งชื่อบอกไว้ตรง ๆ (z_lookahead, lag = 0) ที่เหลือไม่มีตัวไหนเห็นอนาคต
"""
import functools
import math
import os
import sys

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sas_core as C   # noqa: E402
import sas_svg as V    # noqa: E402

# ───────────────────────── ค่าตั้งต้นที่ใช้ร่วมกันทุกโรค ─────────────────────────
N = 1500                    # แท่งต่อโลก (≈ 6 ปี)
TRAIN, REFIT = 250, 21      # walk-forward: ประมาณจาก 250 แท่งล่าสุด ทุก 21 แท่ง
ENTRY, EXIT = 2.0, 0.0      # เข้าเมื่อ |z| ≥ 2 · ออกเมื่อ z ข้าม 0
COST = 0.0005               # c = 5 bps ต่อขา ต่อเที่ยว
YEAR = C.DAYS_PER_YEAR
BETA, HL = 1.4, 12.0        # ค่าจริงของโลก good (ค่าตั้งต้นของ make_pair)
HALF = N // 2               # 750 แท่งแรก = ช่วงคัดเลือก/train · 750 แท่งหลัง = ช่วงพิสูจน์/test

N_NULL = 100_000            # จำนวนโลก "ไม่มีสายจูง" ที่ใช้หาค่าวิกฤตของ Engle-Granger
D1_WORLDS = 300
D2_FAKE, D2_GOOD, D2_TOP = 400, 40, 10
D3_WORLDS = 100
D4_SIGMAS = (0.005, 0.01, 0.02, 0.04)
D4_COSTS = (0.0, 0.0002, 0.0005, 0.001, 0.002, 0.005)
D4_WORLDS = 100
D5_MULTS = (1, 2, 4, 8, 16, 32)
D5_WORLDS, D5_BURN, D5_SIGMA_MU = 200, 400, 0.002
D6_WORLDS, D6_HL, D6_NOISE, D6_SHORT_WINDOW = 200, 40.0, 0.003, 10
D6_SIGMAS = {"tight": 0.01, "wide": 0.03}
D7_STOPS = (2.5, 3.0, 4.0)
D8_WORLDS, D8_MAX_HOLD, D8_LEVEL = 300, 60, 0.10
D8_WINDOWS = (250, 500)     # สวิตช์เฝ้าสายจูงสองขนาด: ใจร้อน (250 แท่ง) กับใจเย็น (500 แท่ง)
D9_WORLDS, D9_SLOW_HL = 1000, 40.0
D2_BOOT = 1000              # จักรวาลที่สุ่มซ้ำจากสระ 440 คู่ (ดูว่า "10 อันดับแรก" แกว่งได้แค่ไหนระหว่างจักรวาล)
SE_FACTOR, BOOT_B = 1.0, 400   # กติกาการปัด: หน่วยของหลักสุดท้าย ≥ 1 × SE · bootstrap 400 รอบสำหรับ SE ของเปอร์เซ็นไทล์
CUTOFF_SE_FACTOR = 2.0         # ค่าวิกฤตที่จำลอง: เข้มกว่า (≥ 2 × SE) — ตรวจแล้วว่าทศนิยมที่สองขยับเมื่อเปลี่ยนเลขสุ่ม


# ───────────────────────── เครื่องมือเล็ก ๆ ที่ใช้ซ้ำ ─────────────────────────

def _wf(y, x, c=COST):
    """walk-forward มาตรฐานของตอนนี้ (ไม่มีพารามิเตอร์ตัวไหนเห็นอนาคต)"""
    return C.walk_forward_pair(y, x, train=TRAIN, refit=REFIT, entry=ENTRY, exit=EXIT, cost_per_leg=c)


def _book(y, x, beta, pos, c=COST, lag=1, start=TRAIN):
    """ลงบัญชีสถานะ pos (ตัดสินใจตอนสิ้นแท่ง) ที่ราคา (y, x) → (pnl, held, turnover) ของช่วงหลัง `start`
    ราคาที่ใช้ลงบัญชีไม่จำเป็นต้องเป็นราคาเดียวกับที่ใช้คิดสัญญาณ (D6 ใช้จุดนี้)"""
    b = np.where(np.isfinite(beta), beta, 0.0)
    pnl, info = C.spread_pnl(y, x, b, pos, cost_per_leg=c, lag=lag)
    return pnl[start:], info["held"][start:], info["turnover"][start:]


def _sharpe(pnl):
    return C.perf_stats(pnl)["sharpe"]


def _ann(pnl):
    return float(np.mean(pnl)) * YEAR


def _dist(a):
    """ค่าเฉลี่ย + เปอร์เซ็นไทล์ 5 / 50 / 95 ของผลจากหลายโลก"""
    a = np.asarray(a, float)
    p5, p50, p95 = np.percentile(a, [5, 50, 95])
    return {"mean": float(a.mean()), "p5": float(p5), "p50": float(p50), "p95": float(p95)}


def _ret_corr(y, x):
    """correlation ของผลตอบแทนรายแท่ง (สิ่งที่คนมักใช้เลือกคู่)"""
    return float(np.corrcoef(np.diff(y), np.diff(x))[0, 1])


# ───────────────────────── ปัดตัวเลขตามความแม่นของ Monte Carlo ─────────────────────────
# ตัวเลขจากการจำลองมีความคลาด (standard error, SE): เปลี่ยนเลขสุ่มแล้วค่าเฉลี่ยของ 300 โลกก็ขยับได้
# ถ้าพิมพ์ละเอียดกว่าความคลาด หลักท้าย ๆ คือเสียงรบกวน ไม่ใช่ข้อมูล — กติกาของโมดูลนี้:
# "หน่วยของหลักสุดท้ายที่พิมพ์ ≥ SE" (ค่าวิกฤตที่จำลอง ≥ 2 × SE) จึงบางค่าเหลือทศนิยมหนึ่งตำแหน่ง
# หรือเป็นจำนวนเต็ม/หลักสิบ (ในบทให้เขียนว่า "ราว") — แต่ไม่ปัดค่าที่ต่างจากศูนย์ชัดเจนจนหลักแรกของมันหายไป
# (4.3 ± 0.8 พิมพ์ 4 ไม่ใช่ 0) · ค่าที่ไม่ได้มาจากการสุ่มหลายโลก (สูตร จำนวนนับ คู่ตัวอย่างคู่เดียว) ไม่ต้องปัดแบบนี้

def _round_mc(v, se, d=2, factor=SE_FACTOR):
    """ปัด v เริ่มที่ทศนิยม d ตำแหน่ง แล้วตัดทีละหลักจนหน่วยของหลักสุดท้าย ≥ factor × SE (หยาบสุด = หลักสิบ)
    ถ้า |v| > 2 SE (ต่างจากศูนย์ชัดเจน) จะไม่ปัดหยาบกว่าหลักแรกของ v
    ไม่เหลือทศนิยม → คืน int (JSON ไม่มี .0 และขั้นตอน fill ใส่จุลภาคให้ถูก)"""
    v, se = float(v), float(se)
    assert math.isfinite(v) and math.isfinite(se), (v, se)
    d0 = d
    while d > -1 and 10.0 ** -d < factor * se:
        d -= 1
    if v != 0 and abs(v) > 2.0 * se:
        d = min(d0, max(d, -math.floor(math.log10(abs(v)))))
    return C.rd(v, d) if d > 0 else int(round(v, d))


def _finite(a, scale=1.0):
    a = np.asarray(a, float) * scale
    return a[np.isfinite(a)]


def _mean(a, d=2, scale=1.0):
    """ค่าเฉลี่ยข้ามโลก · SE = sd/√n"""
    a = _finite(a, scale)
    return _round_mc(a.mean(), a.std(ddof=1) / math.sqrt(len(a)), d)


def _boot_se(a, stat):
    """SE ของสถิติที่ไม่มีสูตรง่าย (เปอร์เซ็นไทล์ ค่าเฉลี่ยของหาง) ด้วย bootstrap ข้ามโลก
    stat รับเมทริกซ์ (รอบ × โลก) แล้วคืนค่าต่อรอบ · ใช้ดัชนีสุ่มชุดเดิมทุกครั้ง จึงได้ผลซ้ำเดิม"""
    idx = C.rng(599).integers(0, len(a), (BOOT_B, len(a)))
    return float(np.std(stat(a[idx]), ddof=1))


def _pctl(a, q, d=2, scale=1.0):
    """เปอร์เซ็นไทล์ q ข้ามโลก (q = 50 คือค่ากลาง) · SE จาก bootstrap"""
    a = _finite(a, scale)
    return _round_mc(np.percentile(a, q), _boot_se(a, lambda m: np.percentile(m, q, axis=1)), d)


def _worst(m, q=0.05):
    """ค่าเฉลี่ยของโลกที่แย่ที่สุด q (ตามแกนสุดท้าย) — นิ่งกว่าเปอร์เซ็นไทล์ที่ 5 เพราะใช้ทุกโลกในหาง"""
    k = max(1, int(round(q * m.shape[-1])))
    return np.sort(m, axis=-1)[..., :k].mean(axis=-1)


def _tail_mean(a, d=1, scale=1.0):
    a = _finite(a, scale)
    return _round_mc(_worst(a), _boot_se(a, _worst), d)


def _share(mask, d=1):
    """% ของโลกที่เข้าเงื่อนไข · SE แบบ Agresti–Coull (ไม่เป็นศูนย์แม้ทุกโลกผ่าน)"""
    m = np.asarray(mask, bool)
    n, k = len(m), int(m.sum())
    p = (k + 2) / (n + 4)
    return _round_mc(100.0 * k / n, 100.0 * math.sqrt(p * (1 - p) / (n + 4)), d)


def _ratio_se(num, den):
    """Σnum ÷ Σden ข้ามโลก (เช่น กำไรขั้นต้นรวม ÷ จำนวนไม้รวม) และ SE แบบ delta method"""
    num, den = np.asarray(num, float), np.asarray(den, float)
    r, n = num.sum() / den.sum(), len(num)
    return float(r), float(math.sqrt(n / (n - 1) * np.sum((num - r * den) ** 2)) / abs(den.sum()))


def _ratio(num, den, d=2, scale=1.0):
    r, se = _ratio_se(num, den)
    return _round_mc(scale * r, abs(scale) * se, d)


def _quantile_se(null_sorted, q):
    """SE ของค่าวิกฤตที่ได้จากการจำลอง (ช่วงของ order statistic ±1 SE ของสัดส่วน)"""
    s, n = np.asarray(null_sorted), len(null_sorted)
    dq = math.sqrt(q * (1 - q) / n)
    return float(np.quantile(s, q + dq) - np.quantile(s, q - dq)) / 2.0


def _binom_q(n, p, q):
    """เปอร์เซ็นไทล์ q ของการแจกแจงทวินาม(n, p) — จำนวนนับที่น้อยที่สุดซึ่งความน่าจะเป็นสะสม ≥ q"""
    cum = 0.0
    for k in range(n + 1):
        cum += math.comb(n, k) * p ** k * (1 - p) ** (n - k)
        if cum >= q:
            return k
    return n


def _dec(v):
    """จำนวนทศนิยมของค่าที่ปัดแล้ว (int → 0) · รับ numpy float ได้ (กราฟส่งค่ามาเป็น numpy)"""
    if isinstance(v, (int, np.integer)):
        return 0
    s = repr(float(v))
    return 0 if "e" in s else len(s.split(".")[1])


def _gap(a, b):
    """ผลต่างของ "ค่าที่พิมพ์" สองค่า — ตัวเลขในบทบวกลบกันลงตัวพอดี"""
    d = max(_dec(a), _dec(b))
    return int(round(a - b)) if d == 0 else C.rd(a - b, d)


def _world_group(kind, n_worlds, offset, **make_kw):
    """สร้าง n_worlds โลกแบบ kind แล้ว backtest แบบ walk-forward ทุกโลก (เก็บไว้ให้โรคอื่นใช้ซ้ำ)"""
    g = C.rng(offset)
    out = []
    for _ in range(n_worlds):
        d = C.make_pair(kind, N, g, **make_kw)
        out.append({"y": d["y"], "x": d["x"], "wf": _wf(d["y"], d["x"]), "break_index": d.get("break_index")})
    return out


def _group_metrics(worlds):
    """ตัวเลขรายโลกของกลุ่ม: Sharpe (lag 1 และ 2) · ผลรวม · จำนวนไม้ · z_sd · correlation ของผลตอบแทน"""
    m = {k: [] for k in ("sharpe", "sharpe_lag2", "total", "ann", "n_trades", "z_sd", "corr")}
    for w in worlds:
        st = w["wf"]["stats"]
        p2, _, _ = _book(w["y"], w["x"], w["wf"]["beta"], w["wf"]["pos"], lag=2)
        m["sharpe"].append(st["sharpe"])
        m["sharpe_lag2"].append(_sharpe(p2))
        m["total"].append(st["total"])
        m["ann"].append(st["ann_return"])
        m["n_trades"].append(st["n_trades"])
        m["z_sd"].append(st["z_sd"])
        m["corr"].append(_ret_corr(w["y"], w["x"]))
    return {k: np.array(v, float) for k, v in m.items()}


# ───────────────────────── D1 · correlation ไม่ใช่สายจูง ─────────────────────────

def exp_d1():
    """good (มีสายจูง) เทียบ fake (ผลตอบแทนสัมพันธ์กันเพราะปัจจัยร่วม แต่ระยะห่างของราคาเป็น random walk)
    fake_tight = fake ที่ตั้งปัจจัยร่วมให้แรงขึ้นจน correlation ของผลตอบแทน ≈ คู่ good (0.90)
    เพื่อตอบคำถาม "ถ้า correlation สูงเท่ากันล่ะ" — ความผันผวนต่อแท่งของแต่ละขาเท่าเดิม"""
    worlds = {
        "good": _world_group("good", D1_WORLDS, 500),
        "fake": _world_group("fake", D1_WORLDS, 501),
        "fake_tight": _world_group("fake", D1_WORLDS, 502, sigma_m=0.0137, sigma_idio=0.0046),
    }
    return {"worlds": worlds, "metrics": {k: _group_metrics(v) for k, v in worlds.items()}}


# ───────────────────────── D2 · คัดจากหลายคู่ ─────────────────────────

def exp_d2(null_half):
    """จักรวาล 440 คู่ (400 fake + 40 good) · ช่วงคัดเลือก = 750 แท่งแรก · ช่วงพิสูจน์ = 750 แท่งหลัง
    backtest เป็น walk-forward ทั้งสองช่วง (ช่วงคัดเลือกเทรดแท่ง 250–749 · ช่วงพิสูจน์เทรดแท่ง 750–1499
    โดยใช้ 250 แท่งก่อนหน้าเป็น train) — ไม่มีพารามิเตอร์มองอนาคตเลย สิ่งเดียวที่ต่างคือ "เราเลือกจากผลที่เห็นแล้ว\""""
    g_fake, g_good = C.rng(510), C.rng(511)
    pairs = ([("fake", C.make_pair("fake", N, g_fake)) for _ in range(D2_FAKE)]
             + [("good", C.make_pair("good", N, g_good)) for _ in range(D2_GOOD)])
    is_good = np.array([k == "good" for k, _ in pairs])
    adf, s_in, s_out, tot_out = [], [], [], []
    for _, d in pairs:
        y, x = d["y"], d["x"]
        r = C.eg_test(y[:HALF], x[:HALF])
        assert (r["n_obs"], r["n_vars"], r["lags"]) == (HALF, 2, 1)     # ต้องตรงกับ null_half
        adf.append(r["adf"])
        s_in.append(_wf(y[:HALF], x[:HALF])["stats"]["sharpe"])
        st = _wf(y[HALF - TRAIN:], x[HALF - TRAIN:])["stats"]
        s_out.append(st["sharpe"])
        tot_out.append(st["total"])
    adf, s_in, s_out, tot_out = (np.array(v, float) for v in (adf, s_in, s_out, tot_out))
    cv = C.crit_values(null_half, (0.01, 0.05))
    pool = {"is_good": is_good, "adf": adf, "s_in": s_in, "s_out": s_out, "tot_out": tot_out, "cv": cv}
    # จักรวาลที่สุ่มซ้ำ (bootstrap): จั่ว 400 fake + 40 good จากสระเดิมแบบใส่คืน แล้วสแกนแบบเดียวกัน
    # "10 อันดับแรก" ของจักรวาลเดียวเป็นค่าเฉลี่ยของแค่ 10 คู่ — ขึ้นกับดวงของจักรวาลนั้นมาก จึงรายงานค่ากลาง + ช่วง 5–95%
    g = C.rng(513)
    fk, gd = np.flatnonzero(~is_good), np.flatnonzero(is_good)
    boots = [_d2_scan(np.concatenate([fk[g.integers(0, len(fk), len(fk))], gd[g.integers(0, len(gd), len(gd))]]), pool)
             for _ in range(D2_BOOT)]
    return {
        "is_good": is_good, "adf": adf, "sharpe_in": s_in, "sharpe_out": s_out, "tot_out": tot_out, "cv": cv,
        "scan": _d2_scan(np.arange(len(pairs)), pool),       # การสแกนจริงหนึ่งรอบ (จุดในกราฟ)
        "boot": boots,
        "all": {"good_in": s_in[is_good], "good_out": s_out[is_good], "fake_in": s_in[~is_good],
                "fake_out": s_out[~is_good],
                "corr_in_out_fake": float(np.corrcoef(s_in[~is_good], s_out[~is_good])[0, 1])},
    }


def _d2_scan(ix, pool):
    """สแกนจักรวาลที่ประกอบด้วยคู่ลำดับ ix ของสระ → คู่ที่ถูกเลือก (เป็นลำดับในสระ) ของแต่ละวิธี
      p5 / p1        ผ่าน Engle-Granger ที่ระดับ 5% / 1% (แยกคู่จริง/ปลอม)
      top_backtest   10 อันดับ Sharpe ช่วงคัดเลือกสูงสุด          (ทำผิด: เลือกจากผล backtest)
      top_eg         10 อันดับค่า Engle-Granger ติดลบที่สุด        (เลือกจากหลักฐานของสายจูง)
      top_fake_only  10 อันดับ Sharpe ช่วงคัดเลือก เฉพาะคู่ fake    (จักรวาลที่ไม่มีคู่จริงเลย)"""
    good, adf, s_in = pool["is_good"][ix], pool["adf"][ix], pool["s_in"][ix]
    out = {}
    for q, key in ((0.05, "p5"), (0.01, "p1")):
        sel = adf < pool["cv"][q]
        out[key] = {"good": ix[sel & good], "fake": ix[sel & ~good]}
    fake = np.flatnonzero(~good)
    out["top_backtest"] = ix[np.argsort(-s_in, kind="stable")[:D2_TOP]]
    out["top_eg"] = ix[np.argsort(adf, kind="stable")[:D2_TOP]]
    out["top_fake_only"] = ix[fake[np.argsort(-s_in[fake], kind="stable")[:D2_TOP]]]
    return out


# ───────────────────────── D3 · มองอนาคต และบั๊ก lag ─────────────────────────

def _lookahead_backtest(y, x, lag=1):
    """ทำผิดโดยตั้งใจ: β, μ, σ ประมาณจากข้อมูล "ทั้งช่วง" (รวมอนาคตของทุกแท่ง) แล้วเทรดช่วงเดียวกัน
    นับผลเฉพาะแท่งหลัง TRAIN เพื่อเทียบกับ walk-forward บนแท่งชุดเดียวกัน"""
    r = C.ols(y, x)
    z_lookahead = (r["resid"] - r["resid"].mean()) / r["resid"].std(ddof=1)
    pos = C.band_positions(z_lookahead, ENTRY, EXIT)
    return _book(y, x, np.full(len(y), float(r["coef"][1])), pos, lag=lag)[0]


def _lag0_damage(y, x, wf):
    """แยกความเสียหายของ lag = 0 (เทียบ lag = 1 ก่อนหักต้นทุน) ออกเป็นสองแท่งของแต่ละไม้:
    แท่งเข้า = แท่งที่ให้สัญญาณเข้า (lag 0 รับผลของแท่งนี้ ทั้งที่มันคือการวิ่งออกห่างที่ทำให้เกิดสัญญาณ)
    แท่งออก = แท่งที่ให้สัญญาณออก (lag 0 ไม่ได้รับผลของแท่งนี้ ทั้งที่มันคือการวิ่งกลับถึงค่าเฉลี่ย)
    คืน (ผลรวมส่วนต่างที่แท่งเข้า, ที่แท่งออก, กำไรขั้นต้นรวมของ lag 1, จำนวนไม้)"""
    p0 = _book(y, x, wf["beta"], wf["pos"], c=0.0, lag=0)[0]
    p1, held, _ = _book(y, x, wf["beta"], wf["pos"], c=0.0, lag=1)
    pos, prev = wf["pos"][TRAIN:], wf["pos"][TRAIN - 1:-1]
    entry, leave = (pos != 0) & (prev == 0), (pos == 0) & (prev != 0)
    diff = p0 - p1
    return float(diff[entry].sum()), float(diff[leave].sum()), float(p1.sum()), C.count_trades(held)


def exp_d3():
    out = {"lookahead": {}, "lag": {}}
    damage = []
    for kind, off in (("good", 520), ("drift", 521), ("fake", 522)):
        g = C.rng(off)
        rows = {"full": [], "wf": [], "full_ann": [], "wf_ann": []}
        lag_rows = {0: [], 1: [], 2: []}
        for _ in range(D3_WORLDS):
            d = C.make_pair(kind, N, g)
            y, x = d["y"], d["x"]
            wf = _wf(y, x)
            p_full = _lookahead_backtest(y, x)
            rows["full"].append(_sharpe(p_full))
            rows["full_ann"].append(_ann(p_full))
            rows["wf"].append(wf["stats"]["sharpe"])
            rows["wf_ann"].append(wf["stats"]["ann_return"])
            if kind == "good":
                for lag in lag_rows:
                    p = _book(y, x, wf["beta"], wf["pos"], lag=lag)[0]
                    lag_rows[lag].append((_sharpe(p), _ann(p)))
                damage.append(_lag0_damage(y, x, wf))
        out["lookahead"][kind] = {k: np.array(v) for k, v in rows.items()}
        if kind == "good":
            out["lag"]["mc"] = {lag: np.array(v) for lag, v in lag_rows.items()}
    out["lag"]["damage"] = np.array(damage)       # รายโลก: (แท่งเข้า, แท่งออก, กำไรขั้นต้น, จำนวนไม้)
    d = C.demo_pair("good")
    wf = _wf(d["y"], d["x"])
    out["lag"]["demo"] = {}
    for lag in (0, 1, 2):
        p = _book(d["y"], d["x"], wf["beta"], wf["pos"], lag=lag)[0]
        out["lag"]["demo"][lag] = (_sharpe(p), _ann(p), float(p.sum()))
    return out


# ───────────────────────── D4 · ต้นทุน ─────────────────────────

def exp_d4():
    """สเปรดกว้าง/แคบ × ต้นทุน — สถานะไม่ขึ้นกับต้นทุน จึง backtest ครั้งเดียวที่ c = 0 แล้วหักต้นทุนทีหลัง
    (pnl สุทธิ = pnl ขั้นต้น − c × |สถานะที่เปลี่ยน|)  และวัด "กำไรขั้นต้นต่อไม้" สองแบบ:
    walk-forward (เกณฑ์เป็นหน่วย σ ของช่วง train) กับแบบรู้ α, β, μ, σ จริง (เกณฑ์เป็น σ จริง — ตรงกับสูตร)"""
    out = {}
    for i, sig in enumerate(D4_SIGMAS):
        g = C.rng(530 + i)
        sharpe = np.empty((D4_WORLDS, len(D4_COSTS)))
        ann = np.empty_like(sharpe)
        sharpe_lag2 = np.empty(D4_WORLDS)
        # รายโลก (ใช้หา SE ของอัตราส่วนรวม เช่น กำไรรวม ÷ จำนวนไม้รวม)
        gross, turn, trades, z_sd, gross_true, trades_true = (np.empty(D4_WORLDS) for _ in range(6))
        for w in range(D4_WORLDS):
            d = C.make_pair("good", N, g, sigma_eq=sig)
            y, x = d["y"], d["x"]
            wf = _wf(y, x, c=0.0)
            p0, held, to = _book(y, x, wf["beta"], wf["pos"], c=0.0)
            for j, c in enumerate(D4_COSTS):
                p = p0 - c * to
                sharpe[w, j], ann[w, j] = _sharpe(p), _ann(p)
            sharpe_lag2[w] = _sharpe(_book(y, x, wf["beta"], wf["pos"], c=COST, lag=2)[0])
            gross[w], turn[w], trades[w], z_sd[w] = p0.sum(), to.sum(), C.count_trades(held), wf["stats"]["z_sd"]
            # แบบรู้ค่าจริง: z = ε/σ_eq (ε คือสเปรดจริงของโลกนี้)
            pos_true = C.band_positions(C.zscore_fixed(d["eps"], 0.0, sig), ENTRY, EXIT)
            pt, ht, _ = _book(y, x, np.full(N, BETA), pos_true, c=0.0)
            gross_true[w], trades_true[w] = pt.sum(), C.count_trades(ht)
        formula = (ENTRY - EXIT) * sig / (1.0 + BETA)
        out[sig] = {
            "sharpe": sharpe, "ann": ann, "sharpe_lag2_c5": sharpe_lag2,
            "gross": gross, "turn": turn, "trades": trades, "gross_true": gross_true, "trades_true": trades_true,
            "z_sd": z_sd,
            "formula_per_trade": formula,                     # (entry − exit)·σ/(1+β) — หน่วย σ จริง
            "breakeven_c_formula": formula / 2.0,             # c ที่ทำให้กำไรต่อไม้ = ต้นทุนครบรอบ 2c
        }                                                     # c เท่าทุนที่วัดได้ = Σกำไรขั้นต้น ÷ Σ|สถานะที่เปลี่ยน|
    return out


# ───────────────────────── D5 · หน้าต่าง z-score ─────────────────────────

def _drifting_mean_pair(g):
    """โลก "ค่ากลางไหลช้า": คู่ good + ค่ากลางของสเปรดที่เดินสุ่มช้า ๆ (sd 0.2% ต่อแท่ง ≈ 3.2% ต่อปี ≈ 1 σ_eq)"""
    d = C.make_pair("good", N, g)
    return {"y": d["y"] + np.cumsum(D5_SIGMA_MU * g.standard_normal(N)), "x": d["x"]}


def exp_d5():
    """z จากหน้าต่างเลื่อน (include_current=False: แท่ง t ไม่อยู่ในไม้บรรทัดของตัวเอง) ขนาด k × half-life
    β ประมาณครั้งเดียวจาก 400 แท่งแรก (ช่วงที่ไม่มีหน้าต่างไหนเทรด) · นับผลแท่ง 400–1499 เท่ากันทุกหน้าต่าง
    "fixed" = μ, σ จาก 400 แท่งแรก แล้วไม่ขยับอีกเลย (ปลายสุดของ "หน้าต่างยาว")"""
    windows = [int(k * HL) for k in D5_MULTS]
    keys = windows + ["fixed"]
    out = {"windows": windows, "worlds": {}}
    share = {"incl6": [], "excl6": [], "incl12": [], "excl12": []}
    for name, off in (("good", 540), ("drifting", 541)):
        g = C.rng(off)
        acc = {k: {"sharpe": [], "sharpe_lag2": [], "ann": [], "trades": []} for k in keys}
        for _ in range(D5_WORLDS):
            d = C.make_pair("good", N, g) if name == "good" else _drifting_mean_pair(g)
            y, x = d["y"], d["x"]
            b = float(C.ols(y[:D5_BURN], x[:D5_BURN])["coef"][1])
            s = y - b * x
            for k in keys:
                if k == "fixed":
                    z = C.zscore_fixed(s, s[:D5_BURN].mean(), s[:D5_BURN].std(ddof=1))
                else:
                    z = C.zscore_rolling(s, k, include_current=False)
                z[:D5_BURN] = np.nan
                pos = C.band_positions(z, ENTRY, EXIT)
                p, held, _ = _book(y, x, np.full(N, b), pos, start=D5_BURN)
                a = acc[k]
                a["sharpe"].append(_sharpe(p))
                a["ann"].append(_ann(p))
                a["trades"].append(C.count_trades(held) / ((N - D5_BURN) / YEAR))
                a["sharpe_lag2"].append(_sharpe(_book(y, x, np.full(N, b), pos, lag=2, start=D5_BURN)[0]))
            if name == "good":       # ข้อเท็จจริงข้างเคียง: เพดาน |z| ≤ (w−1)/√w เมื่อแท่ง t อยู่ในหน้าต่างของตัวเอง
                for w in (6, 12):
                    for tag, inc in (("incl", True), ("excl", False)):
                        zz = C.zscore_rolling(s, w, include_current=inc)[D5_BURN:]
                        share[f"{tag}{w}"].append(float(np.mean(np.abs(zz) >= ENTRY)))
        out["worlds"][name] = {k: {m: np.array(v) for m, v in a.items()} for k, a in acc.items()}
    out["share_beyond_entry"] = {k: np.array(v) for k, v in share.items()}      # รายโลก
    out["bound"] = {w: (w - 1) / math.sqrt(w) for w in (6, 12)}
    return out


# ───────────────────────── D6 · ราคาพิมพ์มี noise ─────────────────────────

def _noisy_world(g, sigma_eq):
    """ราคาจริง = คู่ good ที่ดึงกลับช้า (half-life 40) · ราคาที่เห็น (print) = ราคาจริง + noise อิสระทุกแท่ง
    sd 0.3% ต่อขา (เช่น ราคาปิดเด้งไปมาระหว่าง bid กับ ask หรือราคาปิดที่ไม่ได้เกิดพร้อมกัน)"""
    d = C.make_pair("good", N, g, half_life=D6_HL, sigma_eq=sigma_eq)
    return {"y": d["y"], "x": d["x"],
            "y_obs": d["y"] + D6_NOISE * g.standard_normal(N),
            "x_obs": d["x"] + D6_NOISE * g.standard_normal(N)}


def _d6_books(w, beta, pos):
    """สถานะชุดเดียว (คิดจากราคาที่เห็น) ลงบัญชีที่ราคาที่เห็น (lag 0 = บั๊ก, 1, 2) และที่ราคาจริง (lag 1, 2)
    → (Sharpe, ผลตอบแทนต่อปี)"""
    out = {}
    for tag, (py, px) in (("print", (w["y_obs"], w["x_obs"])), ("true", (w["y"], w["x"]))):
        for lag in ((0, 1, 2) if tag == "print" else (1, 2)):
            p = _book(py, px, beta, pos, lag=lag)[0]
            out[f"{tag}_lag{lag}"] = (_sharpe(p), _ann(p))
    return out


def exp_d6():
    """สองกลยุทธ์ บนสัญญาณจากราคาที่เห็นเท่านั้น:
      wf    = walk-forward มาตรฐาน
      short = หน้าต่างเลื่อน 10 แท่ง (≈ 4 เท่าของ half-life ที่ประมาณได้จากราคาที่เห็น) — กลยุทธ์ที่คนจะออกแบบ
              ถ้าเชื่อ half-life ปลอม · β ประมาณจาก 250 แท่งแรกของราคาที่เห็น
    สองโลก: tight (σ_eq 1% — noise ของสเปรด 0.52% ใหญ่ราวครึ่งของสเปรด) และ wide (σ_eq 3% — noise เล็กเมื่อเทียบ)"""
    out = {"first_tight": None}
    for i, (name, sig) in enumerate(D6_SIGMAS.items()):
        g = C.rng(550 + i)
        acc = {"wf": [], "short": []}
        hl = {"print": [], "true": [], "ac1_print": [], "ac1_true": []}
        for k in range(D6_WORLDS):
            w = _noisy_world(g, sig)
            if name == "tight" and k == 0:
                out["first_tight"] = w                       # ใช้เป็นคู่ตัวอย่าง "noisy" ของ D10
            wf = _wf(w["y_obs"], w["x_obs"])
            acc["wf"].append(_d6_books(w, wf["beta"], wf["pos"]))
            b = float(C.ols(w["y_obs"][:TRAIN], w["x_obs"][:TRAIN])["coef"][1])
            z = C.zscore_rolling(w["y_obs"] - b * w["x_obs"], D6_SHORT_WINDOW, include_current=False)
            z[:TRAIN] = np.nan
            acc["short"].append(_d6_books(w, np.full(N, b), C.band_positions(z, ENTRY, EXIT)))
            for tag, (py, px) in (("print", (w["y_obs"], w["x_obs"])), ("true", (w["y"], w["x"]))):
                resid = C.eg_test(py, px)["resid"]
                hl[tag].append(C.fit_ar1(resid)["half_life"])
                dr = np.diff(resid)
                hl[f"ac1_{tag}"].append(float(np.corrcoef(dr[1:], dr[:-1])[0, 1]))
        out[name] = {
            "sigma_eq": sig,
            "noise_spread": D6_NOISE * math.sqrt(1.0 + BETA ** 2),
            "strategies": {s: {k: np.array([r[k] for r in rows]) for k in rows[0]} for s, rows in acc.items()},
            "hl": {k: np.array(v) for k, v in hl.items()},
        }
    return out


# ───────────────────────── D7 · stop ─────────────────────────

def _rebook_with(w, z=None, **band):
    """ใช้ z และ β ของ walk-forward เดิม เปลี่ยนเฉพาะกฎถือ (stop / max_hold) หรือ z ที่ถูกปิดบางช่วง"""
    wf = w["wf"]
    pos = C.band_positions(wf["z"] if z is None else z, ENTRY, EXIT, **band)
    return _book(w["y"], w["x"], wf["beta"], pos)


def exp_d7(good_worlds, break_worlds):
    """stop-loss ที่ |z| ≥ stop (หน่วยเดียวกับ entry = σ ของช่วง train) เทียบกับไม่มี stop"""
    out = {}
    for name, worlds in (("good", good_worlds), ("break", break_worlds)):
        res = {}
        for stop in (None,) + D7_STOPS:
            rows = []
            for w in worlds:
                p, held, _ = _rebook_with(w, stop=stop)
                st = C.perf_stats(p, held, cost_per_leg=COST)
                rows.append((st["sharpe"], st["total"], st["hit_rate"], st["n_trades"], st["avg_trade"]))
            res[stop] = np.array(rows)
        out[name] = res
    return out


# ───────────────────────── D8 · สายจูงขาด ─────────────────────────

def _monitor_ok(y, x, window, cv):
    """สวิตช์เฝ้าสายจูง: ทุกครั้งที่ประมาณใหม่ (ทุก 21 แท่ง) ทดสอบ Engle-Granger บน `window` แท่งล่าสุด
    คืน (จุดเริ่มของแต่ละบล็อก, ผ่านหรือไม่) — ไม่ผ่าน = ปิดสถานะและงดเทรดทั้งบล็อก 21 แท่งถัดไป
    ช่วงต้นที่ข้อมูลยังไม่ถึง `window` แท่งใช้เท่าที่มี (≥ 250 แท่ง) เทียบกับค่าวิกฤตเดียวกัน
    (ค่าวิกฤต 10% ที่ 250 กับ 500 แท่งต่างกันน้อยกว่าความคลาดของการจำลอง — ดู cv ใน figures)"""
    starts = np.arange(TRAIN, len(y), REFIT)
    adf = np.empty(len(starts))
    full = starts >= window
    for i in np.flatnonzero(~full):
        adf[i] = C.eg_test(y[:starts[i]], x[:starts[i]])["adf"]
    yw = sliding_window_view(y, window)[starts[full] - window]
    xw = sliding_window_view(x, window)[starts[full] - window]
    adf[full] = C.adf_stat_batch(C.resid_batch(yw, xw[:, :, None]), lags=1, const=False)
    return starts, adf < cv


def _mask_blocks(z, starts, ok):
    zm = z.copy()
    for s, passed in zip(starts, ok):
        if not passed:
            zm[s:s + REFIT] = np.nan          # z = NaN → band_positions ปิดสถานะและไม่เปิดใหม่
    return zm


def _hold_lengths(held):
    """จำนวนแท่งที่ถือของแต่ละไม้"""
    on = (np.asarray(held) != 0).astype(int)
    edges = np.flatnonzero(np.diff(np.concatenate([[0], on, [0]])))
    return edges[1::2] - edges[::2]


D8_VARIANTS = ("none", "time", "monitor_250", "monitor_500", "both")


def exp_d8(good_worlds, nulls):
    """โลก break (สายจูงขาดที่แท่ง 900) เทียบ 5 แบบ:
      none         ไม่ทำอะไร (walk-forward ประมาณใหม่ตามปกติ)
      time         จำกัดเวลาถือ 60 แท่ง (5 เท่าของ half-life)
      monitor_250  เฝ้าด้วย Engle-Granger บน 250 แท่งล่าสุด ที่ระดับ 10%
      monitor_500  เหมือนกันแต่ใช้ 500 แท่งล่าสุด (ไวน้อยกว่า แต่เตือนผิดน้อยกว่า)
      both         time + monitor_500
    แล้ววัด "ราคาที่ต้องจ่าย" ของแต่ละแบบบนโลก good ชุดเดียวกับ D1"""
    cv = {w: C.crit_values(nulls[w], (D8_LEVEL,))[D8_LEVEL] for w in D8_WINDOWS}
    break_worlds = _world_group("break", D8_WORLDS, 560)
    out = {"cv": cv, "cv_se": {w: _quantile_se(nulls[w], D8_LEVEL) for w in D8_WINDOWS}, "break_worlds": break_worlds}
    for name, worlds in (("break", break_worlds), ("good", good_worlds)):
        rows = {v: [] for v in D8_VARIANTS}
        mon = {w: {"pre": [], "post": [], "delay": []} for w in D8_WINDOWS}
        holds = []
        for w in worlds:
            k = w["break_index"]
            zm = {}
            for win in D8_WINDOWS:
                starts, ok = _monitor_ok(w["y"], w["x"], win, cv[win])
                zm[win] = _mask_blocks(w["wf"]["z"], starts, ok)
                if k:
                    mon[win]["pre"].append(float(np.mean(~ok[starts < k])))
                    mon[win]["post"].append(float(np.mean(~ok[starts >= k])))
                    hit = starts[(starts >= k) & ~ok]
                    mon[win]["delay"].append(float(hit[0] - k) if len(hit) else math.inf)
                else:
                    mon[win]["pre"].append(float(np.mean(~ok)))
            variants = {"none": {}, "time": {"max_hold": D8_MAX_HOLD},
                        "monitor_250": {"z": zm[250]}, "monitor_500": {"z": zm[500]},
                        "both": {"z": zm[500], "max_hold": D8_MAX_HOLD}}
            for v, kw in variants.items():
                p, held, _ = _rebook_with(w, **kw)
                after = float(p[k - TRAIN:].sum()) if k else math.nan
                rows[v].append((float(p.sum()), _sharpe(p), after))
                if v == "none":
                    holds.append(_hold_lengths(held))
        out[name] = {"rows": {v: np.array(r) for v, r in rows.items()},
                     "monitor": {w: {k2: np.array(v2) for k2, v2 in m.items()} for w, m in mon.items()},
                     "holds": np.concatenate(holds)}
    return out


# ───────────────────────── D9 · ข้อมูลน้อยเกินไป ─────────────────────────

def exp_d9():
    """Sharpe ที่ "เกิดขึ้นจริง" ในหนึ่งปี (252 แท่งหลัง train 250 แท่ง) ของ walk-forward ต้นทุน 5 bps
    good = คู่ good มาตรฐาน · slow = คู่ที่มีสายจูงจริงแต่ดึงกลับช้า (half-life 40 — ความได้เปรียบบางกว่า) · fake"""
    out = {}
    for name, kind, off, kw in (("good", "good", 570, {}), ("fake", "fake", 571, {}),
                                ("slow", "good", 572, {"half_life": D9_SLOW_HL})):
        g = C.rng(off)
        sh, nt = [], []
        for _ in range(D9_WORLDS):
            d = C.make_pair(kind, TRAIN + YEAR, g, **kw)
            st = _wf(d["y"], d["x"])["stats"]
            sh.append(st["sharpe"])
            nt.append(st["n_trades"])
        out[name] = {"sharpe": np.array(sh), "n_trades": np.array(nt, float)}
    return out


# ───────────────────────── D10 · ชุดตรวจตัวเอง ─────────────────────────

BATTERY_RULES = {      # เกณฑ์ผ่านของแต่ละข้อ (ตั้งไว้ก่อน แล้ววัดอัตราผ่านบนโลก good/fake ให้ดู)
    "eg_p_max": 0.05, "shift_max_sigma": 1.0, "beta_change_max": 0.15,
    "hl_min_bars": 2.0, "hl_max_bars": 60.0, "hl_test_max_ratio": 3.0,
    "breakeven_ratio_min": 3.0, "lag2_keep_min": 0.5,
}


def _battery(y, x, null_half, wf=None):
    """ชุดตรวจ 6 ข้อ คิดแบบกลไกล้วน ๆ จากราคาสองเส้น (ครึ่งแรก = train · ครึ่งหลัง = test)
      1 eg_p        p-value ของ Engle-Granger บนครึ่งแรก
      2 shift       ค่าเฉลี่ยของสเปรดครึ่งหลัง (ประกอบด้วย α, β ของครึ่งแรก) เลื่อนจากครึ่งแรกกี่ σ ของครึ่งแรก
      3 beta        β ของครึ่งแรก เทียบกับ β ที่ประมาณใหม่จากครึ่งหลัง
      4 half-life   ของสเปรดครึ่งแรกอยู่ในช่วง 2–60 แท่ง และครึ่งหลังไม่ยาวเกิน 3 เท่าของครึ่งแรก
                    (ตัวเลข half-life มีความหมายเมื่อข้อ 1 ผ่านเท่านั้น)
      5 breakeven   กำไรขั้นต้นต่อไม้ของ walk-forward เทียบกับต้นทุน: c ที่เท่าทุน ÷ c ที่ใช้ (5 bps)
      6 lag         Sharpe เมื่อได้ราคาช้าไปหนึ่งแท่ง (lag 2) เทียบกับ lag 1"""
    tr = C.eg_test(y[:HALF], x[:HALF])
    assert (tr["n_obs"], tr["n_vars"], tr["lags"]) == (HALF, 2, 1)     # ต้องตรงกับ null_half
    a, b = tr["alpha"], float(tr["beta"][0])
    mu, sd = float(tr["resid"].mean()), float(tr["resid"].std(ddof=1))
    eps_test = y[HALF:] - a - b * x[HALF:]
    b_test = float(C.ols(y[HALF:], x[HALF:])["coef"][1])
    wf = wf or _wf(y, x)
    p1, held, to = _book(y, x, wf["beta"], wf["pos"])
    p2 = _book(y, x, wf["beta"], wf["pos"], lag=2)[0]
    gross = float(p1.sum() + COST * to.sum())
    n_tr = C.count_trades(held)
    m = {
        "eg_adf": tr["adf"], "eg_p": C.p_value(tr["adf"], null_half),
        "shift": (float(eps_test.mean()) - mu) / sd,
        "beta_train": b, "beta_test": b_test, "beta_change": b_test / b - 1.0,
        "hl_train": C.fit_ar1(tr["resid"])["half_life"], "hl_test": C.fit_ar1(eps_test)["half_life"],
        "n_trades": n_tr, "edge_per_trade": gross / n_tr if n_tr else 0.0,
        "breakeven_c": float(gross / to.sum()) if to.sum() else 0.0,
        "sharpe_lag1": _sharpe(p1), "sharpe_lag2": _sharpe(p2), "z_sd": wf["stats"]["z_sd"],
    }
    m["breakeven_ratio"] = m["breakeven_c"] / COST
    R = BATTERY_RULES
    m["pass"] = {
        "eg": m["eg_p"] < R["eg_p_max"],
        "shift": abs(m["shift"]) < R["shift_max_sigma"],
        "beta": abs(m["beta_change"]) < R["beta_change_max"],
        "hl": (R["hl_min_bars"] <= m["hl_train"] <= R["hl_max_bars"]
               and m["hl_test"] <= R["hl_test_max_ratio"] * m["hl_train"]),
        "breakeven": bool(m["breakeven_ratio"] >= R["breakeven_ratio_min"]),
        "lag": bool(m["sharpe_lag1"] > 0 and m["sharpe_lag2"] >= R["lag2_keep_min"] * m["sharpe_lag1"]),
    }
    m["n_pass"] = int(sum(m["pass"].values()))
    return m


def exp_d10(d1_worlds, noisy_world, null_half):
    pairs = {k: _battery(d["y"], d["x"], null_half) for k, d in
             ((k, C.demo_pair(k)) for k in ("good", "fake", "drift", "break"))}
    pairs["noisy"] = _battery(noisy_world["y_obs"], noisy_world["x_obs"], null_half)
    mc = {k: [_battery(w["y"], w["x"], null_half, wf=w["wf"]) for w in d1_worlds[k]] for k in ("good", "fake")}
    return {"pairs": pairs, "mc": mc}


# ───────────────────────── รวมทุกการทดลอง ─────────────────────────

@functools.lru_cache(maxsize=1)
def run():
    """คำนวณทุกโรค (ราว 50 วินาที) — เรียกซ้ำได้ผลชุดเดิมจากหน่วยความจำ"""
    null_half = C.mc_null_eg(HALF, 2, n_sim=N_NULL, lags=1, g=C.rng(512))
    nulls = {w: C.mc_null_eg(w, 2, n_sim=N_NULL, lags=1, g=C.rng(561 + i)) for i, w in enumerate(D8_WINDOWS)}
    d1 = exp_d1()
    d6 = exp_d6()
    d8 = exp_d8(d1["worlds"]["good"], nulls)
    return {
        "cv_half": C.crit_values(null_half, (0.01, 0.05, 0.10)),
        "cv_half_se": {q: _quantile_se(null_half, q) for q in (0.01, 0.05)},
        "d1": d1, "d2": exp_d2(null_half), "d3": exp_d3(), "d4": exp_d4(), "d5": exp_d5(), "d6": d6,
        "d7": exp_d7(d1["worlds"]["good"], d8["break_worlds"]), "d8": d8, "d9": exp_d9(),
        "d10": exp_d10(d1["worlds"], d6["first_tight"], null_half),
    }


# ───────────────────────── figures: ตัวเลขที่ปัดแล้ว พร้อมลงในบท ─────────────────────────

CHECKS = ("eg", "shift", "beta", "hl", "breakeven", "lag")       # ลำดับข้อ 1–6 ของชุดตรวจ D10
TEST_YEARS = (N - TRAIN) / YEAR


def _sigma_key(sig):
    return "s" + ("%g" % (sig * 100)).replace(".", "_")           # 0.005 → "s0_5"


def _cost_key(c):
    return "c%d" % round(c * 1e4)                                  # 0.0005 → "c5"


def _fig_d1(d1):
    out = {"worlds": D1_WORLDS}
    for k, m in d1["metrics"].items():
        s = m["sharpe"]
        out[k] = {
            "sharpe_mean": _mean(s), "sharpe_p5": _pctl(s, 5), "sharpe_p50": _pctl(s, 50), "sharpe_p95": _pctl(s, 95),
            "sharpe_lag2_mean": _mean(m["sharpe_lag2"]), "profitable_pct": _share(m["total"] > 0),
            "ann_return_pct": _mean(m["ann"], 2, 100), "ret_corr_median": _pctl(m["corr"], 50),
            "trades_per_year": _mean(m["n_trades"] / TEST_YEARS, 1), "z_sd": _mean(m["z_sd"]),
        }
    out["gap_sharpe"] = _gap(out["good"]["sharpe_mean"], out["fake_tight"]["sharpe_mean"])
    return out


def _d2_level(d2, key, q, cv_se):
    """คัดด้วย Engle-Granger ที่ระดับ q: ผลของการสแกนจริง (จำนวนนับ = ข้อเท็จจริงของรอบนี้)
    + ค่าคาดหมาย + ช่วง 5–95% ข้ามจักรวาลที่สุ่มซ้ำ (จักรวาลอื่นได้ตัวเลขต่างจากรอบนี้แค่ไหน)"""
    sc, s_out, tot = d2["scan"][key], d2["sharpe_out"], d2["tot_out"]
    tp, fp = len(sc["good"]), len(sc["fake"])
    # ค่าวิกฤตจำลองจากโลกไม่มีสายจูง → จำนวน fake ที่หลุดเข้ามา ~ ทวินาม(400, q) ในทุกจักรวาลแบบนี้
    fp_exp, fp_lo, fp_hi = q * D2_FAKE, _binom_q(D2_FAKE, q, 0.05), _binom_q(D2_FAKE, q, 0.95)
    out = {"cutoff": _round_mc(d2["cv"][q], cv_se[q], factor=CUTOFF_SE_FACTOR), "tp": tp, "fp": fp, "selected": tp + fp,
           "precision_pct": C.pct(tp / (tp + fp), 0), "power_pct": C.pct(tp / D2_GOOD, 0),
           "fp_rate_pct": C.pct(fp / D2_FAKE, 1),
           "fp_expected": int(round(fp_exp)), "precision_expected_pct": C.pct(tp / (tp + fp_exp), 0),
           "fp_p5": fp_lo, "fp_p95": fp_hi,
           "precision_p5_pct": C.pct(tp / (tp + fp_hi), 0), "precision_p95_pct": C.pct(tp / (tp + fp_lo), 0)}
    for tag, idx in (("good", sc["good"]), ("fake", sc["fake"]),
                     ("all", np.concatenate([sc["good"], sc["fake"]]))):
        if len(idx) >= 2:                 # ค่าเฉลี่ยของคู่ที่ถูกเลือก (คู่ fake มีแค่ไม่กี่คู่ จึงปัดหยาบ)
            out[f"oos_sharpe_{tag}"] = _mean(s_out[idx])
        if len(idx) >= 10:                # สัดส่วนที่กำไร: มีความหมายเมื่อมีอย่างน้อย 10 คู่
            out[f"oos_profitable_{tag}_pct"] = _share(tot[idx] > 0, 0)
    return out


def _d2_top(d2, key):
    """10 อันดับแรกตามวิธี key: ค่ากลางข้าม 1,000 จักรวาลที่สุ่มซ้ำ (ใช้อ้างในบท) + ช่วง 5–95% + ผลของการสแกนจริง (วงม่วงในกราฟ)
    ค่ากลาง = ค่าเฉลี่ยของคู่ที่ติดอันดับ ถ่วงด้วยความถี่ที่ติด · SE ≈ √(Σw² × ความแปรปรวน) เพราะสระมีแค่ 440 คู่"""
    s_in, s_out, good, tot = d2["sharpe_in"], d2["sharpe_out"], d2["is_good"].astype(float), d2["tot_out"]
    boots = [b[key] for b in d2["boot"]]
    w = np.bincount(np.concatenate(boots), minlength=len(s_in)).astype(float)
    w /= w.sum()

    def centre(x):
        c = float(w @ x)
        return c, math.sqrt(float(w @ (x - c) ** 2) * float(w @ w))

    sc, out = d2["scan"][key], {}
    for tag, x in (("in", s_in), ("out", s_out)):
        c, se = centre(x)
        per = np.array([x[b].mean() for b in boots])      # ค่าเฉลี่ย 10 อันดับของแต่ละจักรวาล
        out[f"sharpe_{tag}"] = _round_mc(c, se)
        # ขอบช่วง 5–95% ข้ามจักรวาล: ปัดหยาบเท่าค่ากลาง (สระเดียวกัน ความคลาดเท่ากัน)
        out[f"sharpe_{tag}_p5"], out[f"sharpe_{tag}_p95"] = (_round_mc(v, se) for v in np.percentile(per, [5, 95]))
    c, se = centre(good)
    out.update({"n_good": _round_mc(D2_TOP * c, D2_TOP * se, 0),
                "scan_sharpe_in": _mean(s_in[sc]), "scan_sharpe_out": _mean(s_out[sc]),
                "scan_n_good": int(good[sc].sum()), "scan_n_fake": int(D2_TOP - good[sc].sum()),
                "scan_out_profitable": int(np.sum(tot[sc] > 0))})
    out["drop"] = _gap(out["sharpe_in"], out["sharpe_out"])
    return out


def _fig_d2(d2, cv_se):
    a = d2["all"]
    r, n = a["corr_in_out_fake"], len(a["fake_in"])
    return {
        "n_pairs": D2_FAKE + D2_GOOD, "n_fake": D2_FAKE, "n_good": D2_GOOD, "top_n": D2_TOP,
        "select_bars": HALF, "prove_bars": N - HALF, "universes": D2_BOOT,
        "level5": _d2_level(d2, "p5", 0.05, cv_se), "level1": _d2_level(d2, "p1", 0.01, cv_se),
        "top_backtest": _d2_top(d2, "top_backtest"), "top_eg": _d2_top(d2, "top_eg"),
        "top_fake_only": _d2_top(d2, "top_fake_only"),
        "all": {"good_sharpe_in": _mean(a["good_in"]), "good_sharpe_out": _mean(a["good_out"]),
                "fake_sharpe_in": _mean(a["fake_in"]), "fake_sharpe_out": _mean(a["fake_out"]),
                "fake_sharpe_in_p95": _pctl(a["fake_in"], 95),
                "fake_corr_in_out": _round_mc(r, (1 - r * r) / math.sqrt(n - 1))},
    }


def _fig_d3(d3):
    out = {"worlds": D3_WORLDS}
    for kind, v in d3["lookahead"].items():
        la, wf = _mean(v["full"]), _mean(v["wf"])
        out[kind] = {
            "sharpe_lookahead": la, "sharpe_wf": wf, "gap": _gap(la, wf),
            "ann_lookahead_pct": _mean(v["full_ann"], 2, 100), "ann_wf_pct": _mean(v["wf_ann"], 2, 100),
            "profitable_lookahead_pct": _share(v["full_ann"] > 0, 0), "profitable_wf_pct": _share(v["wf_ann"] > 0, 0),
        }
    mc, demo = d3["lag"]["mc"], d3["lag"]["demo"]
    lag = {"mc": {}, "demo": {}}
    for k in (0, 1, 2):
        lag["mc"][f"lag{k}"] = {"sharpe": _mean(mc[k][:, 0]), "ann_return_pct": _mean(mc[k][:, 1], 2, 100),
                                "profitable_pct": _share(mc[k][:, 1] > 0, 0)}
        lag["demo"][f"lag{k}"] = {"sharpe": C.rd(demo[k][0], 2), "ann_return_pct": C.pct(demo[k][1], 2),
                                  "total_pct": C.pct(demo[k][2], 1)}      # คู่ตัวอย่างคู่เดียว: ข้อเท็จจริง ไม่ใช่ค่าประมาณ
    m = lag["mc"]
    m["gap_lag0"] = _gap(m["lag0"]["sharpe"], m["lag1"]["sharpe"])
    m["gap_lag2"] = _gap(m["lag2"]["sharpe"], m["lag1"]["sharpe"])
    m["lag0_return_lost_pct"] = _ratio(mc[1][:, 1] - mc[0][:, 1], mc[1][:, 1], 0, 100)   # 1 − Σผล lag0 ÷ Σผล lag1
    dmg = d3["lag"]["damage"]                     # รายโลก: แท่งเข้า · แท่งออก · กำไรขั้นต้น (lag 1) · จำนวนไม้
    m["gross_per_trade_bps"] = _ratio(dmg[:, 2], dmg[:, 3], 0, 1e4)
    m["lag0_entry_bar_bps"] = _ratio(dmg[:, 0], dmg[:, 3], 0, 1e4)        # ส่วนที่ lag 0 เสียที่แท่งเข้า (ต่อไม้)
    m["lag0_exit_bar_bps"] = _ratio(dmg[:, 1], dmg[:, 3], 0, 1e4)         # ส่วนที่ lag 0 เสียที่แท่งออก (ต่อไม้)
    out["lag"] = lag
    return out


def _fig_d4(d4):
    out = {"worlds": D4_WORLDS, "half_life_bars": int(HL), "beta": BETA,
           "formula_sigma_over_c": C.rd(2.0 * (1.0 + BETA) / (ENTRY - EXIT), 1)}
    over_c, over_c_se, zs, zs_se = [], [], [], []
    for sig, v in d4.items():
        cell = {"sigma_pct": C.pct(sig, 1)}
        for j, c in enumerate(D4_COSTS):
            cell[_cost_key(c)] = {"sharpe": _mean(v["sharpe"][:, j]), "ann_return_pct": _mean(v["ann"][:, j], 2, 100),
                                  "profitable_pct": _share(v["ann"][:, j] > 0, 0)}
        f = v["formula_per_trade"]
        z, z_se = float(v["z_sd"].mean()), float(v["z_sd"].std(ddof=1) / math.sqrt(D4_WORLDS))
        g, g_se = _ratio_se(v["gross"], v["trades"])
        gt, gt_se = _ratio_se(v["gross_true"], v["trades_true"])
        be, be_se = _ratio_se(v["gross"], v["turn"])          # c ที่ทำให้ผลรวมสุทธิทุกโลก = 0 พอดี
        cell.update({
            "gross_per_trade_bps": _round_mc(1e4 * g, 1e4 * g_se, 1),
            "gross_per_trade_true_bps": _round_mc(1e4 * gt, 1e4 * gt_se, 1),
            "formula_per_trade_bps": C.bps(f, 1),
            "formula_converted_bps": _round_mc(1e4 * f / z, 1e4 * f * z_se / z ** 2, 1),
            "wf_to_formula_ratio": _round_mc(g / f, g_se / f), "true_to_formula_ratio": _round_mc(gt / f, gt_se / f),
            "breakeven_c_bps": _round_mc(1e4 * be, 1e4 * be_se, 1),
            "breakeven_c_formula_bps": C.bps(v["breakeven_c_formula"], 1),
            "trades_per_year": _mean(v["trades"] / TEST_YEARS, 1),
            "trades_per_year_true": _mean(v["trades_true"] / TEST_YEARS, 1),
            "z_sd": _mean(v["z_sd"]), "sharpe_lag2_c5": _mean(v["sharpe_lag2_c5"]),
        })
        out[_sigma_key(sig)] = cell
        over_c.append(sig / be)
        over_c_se.append(sig * be_se / be ** 2)
        zs.append(z)
        zs_se.append(z_se)
    k = len(D4_SIGMAS)
    out["measured_sigma_over_c"] = _round_mc(np.mean(over_c), math.sqrt(np.sum(np.square(over_c_se))) / k, 1)
    z, z_se = float(np.mean(zs)), math.sqrt(np.sum(np.square(zs_se))) / k
    out["z_sd"] = _round_mc(z, z_se)
    out["entry_true_sigma"] = C.rd(ENTRY / out["z_sd"], 2)       # จาก z_sd ที่พิมพ์ — "2 ÷ 1.25" ในบทคิดเลขได้ตรง
    out["sigma_min_formula_pct"] = {_cost_key(c): C.pct(2.0 * c * (1.0 + BETA) / (ENTRY - EXIT), 3)
                                    for c in D4_COSTS[1:]}
    # ใช้อัตราส่วนที่พิมพ์แล้ว เพื่อให้ "c × อัตราส่วน" ในบทคิดเลขได้ตรง
    out["sigma_min_measured_pct"] = {_cost_key(c): C.pct(c * out["measured_sigma_over_c"], 3) for c in D4_COSTS[1:]}
    return out


def _plateau(res, windows, best):
    """หน้าต่างที่ Sharpe ต่างจากหน้าต่างที่ดีที่สุดไม่เกิน 2 SE (เทียบแบบจับคู่บนโลกชุดเดียวกัน)
    — ค่าที่ดีที่สุดค่าเดียวขึ้นกับเลขสุ่ม แต่ "ช่วงที่ดีพอ ๆ กัน" นิ่งกว่า"""
    near = []
    for w in windows:
        dlt = res[w]["sharpe"] - res[best]["sharpe"]
        if dlt.mean() > -SE_FACTOR * dlt.std(ddof=1) / math.sqrt(len(dlt)) or w == best:
            near.append(w)
    return min(near), max(near)


def _plateau_txt(cell):
    """"8–16" หรือ "8" (ถ้าช่วงที่ดีพอ ๆ กันมีหน้าต่างเดียว)"""
    lo, hi = cell["plateau_lo_mult"], cell["plateau_hi_mult"]
    return f"{lo}" if lo == hi else f"{lo}–{hi}"


def _fig_d5(d5):
    out = {"worlds": D5_WORLDS, "burn_bars": D5_BURN, "half_life_bars": int(HL),
           "sigma_mu_pct": C.pct(D5_SIGMA_MU, 1), "sigma_mu_year_pct": C.pct(D5_SIGMA_MU * math.sqrt(YEAR), 1)}
    ws = d5["windows"]
    for name, res in d5["worlds"].items():
        cell = {}
        for k, a in res.items():
            cell["fixed" if k == "fixed" else f"w{k}"] = {
                "sharpe": _mean(a["sharpe"]), "sharpe_lag2": _mean(a["sharpe_lag2"]),
                "ann_return_pct": _mean(a["ann"], 2, 100), "trades_per_year": _mean(a["trades"], 1)}
        best = max(ws, key=lambda w: res[w]["sharpe"].mean())
        lo, hi = _plateau(res, ws, best)
        b = cell[f"w{best}"]["sharpe"]
        cell.update({"best_sharpe": b,          # หน้าต่างที่ดีที่สุดค่าเดียวขึ้นกับเลขสุ่ม — ให้อ้างช่วง plateau แทน
                     "plateau_lo_mult": int(lo / HL), "plateau_hi_mult": int(hi / HL),
                     "gap_shortest": _gap(cell[f"w{ws[0]}"]["sharpe"], b),
                     "gap_longest": _gap(cell[f"w{ws[-1]}"]["sharpe"], b), "gap_fixed": _gap(cell["fixed"]["sharpe"], b)})
        out[name] = cell
    sh = d5["share_beyond_entry"]
    out["bound"] = {"w6": C.rd(d5["bound"][6], 2), "w12": C.rd(d5["bound"][12], 2),
                    "share_incl_w6_pct": _mean(sh["incl6"], 1, 100), "share_excl_w6_pct": _mean(sh["excl6"], 1, 100),
                    "share_incl_w12_pct": _mean(sh["incl12"], 1, 100), "share_excl_w12_pct": _mean(sh["excl12"], 1, 100)}
    return out


def _fig_d6(d6):
    out = {"worlds": D6_WORLDS, "half_life_true_bars": int(D6_HL), "noise_leg_pct": C.pct(D6_NOISE, 1),
           "noise_spread_pct": C.pct(D6_NOISE * math.sqrt(1.0 + BETA ** 2), 2), "short_window_bars": D6_SHORT_WINDOW}
    for name in D6_SIGMAS:
        v = d6[name]
        cell = {"sigma_eq_pct": C.pct(v["sigma_eq"], 1),
                "noise_to_sigma_pct": C.pct(v["noise_spread"] / v["sigma_eq"], 0),
                "hl_print_bars": _pctl(v["hl"]["print"], 50, 1), "hl_true_bars": _pctl(v["hl"]["true"], 50, 1),
                "ac1_print": _pctl(v["hl"]["ac1_print"], 50), "ac1_true": _pctl(v["hl"]["ac1_true"], 50)}
        for strat, res in v["strategies"].items():
            s = {k: {"sharpe": _mean(a[:, 0]), "ann_return_pct": _mean(a[:, 1], 2, 100)} for k, a in res.items()}
            s["gap_sharpe"] = _gap(s["print_lag1"]["sharpe"], s["true_lag1"]["sharpe"])
            s["gap_ann_return_pct"] = _gap(s["print_lag1"]["ann_return_pct"], s["true_lag1"]["ann_return_pct"])
            cell[strat] = s
        out[name] = cell
    return out


def _stop_key(stop):
    return "none" if stop is None else "stop" + ("%g" % stop).replace(".", "_")     # 2.5 → "stop2_5"


def _fig_d7(d7):
    out = {"worlds_good": D1_WORLDS, "worlds_break": D8_WORLDS}
    for name, res in d7.items():
        cell = {}
        for stop, r in res.items():
            cell[_stop_key(stop)] = {
                "sharpe": _mean(r[:, 0]), "total_pct": _mean(r[:, 1], 1, 100), "total_p5_pct": _pctl(r[:, 1], 5, 1, 100),
                "hit_rate_pct": _mean(r[:, 2], 0, 100), "trades_per_year": _mean(r[:, 3] / TEST_YEARS, 1),
                "avg_trade_bps": _mean(r[:, 4], 0, 1e4)}
        cell["gap_tightest"] = _gap(cell[_stop_key(D7_STOPS[0])]["sharpe"], cell["none"]["sharpe"])
        out[name] = cell
    return out


def _fig_d8(d8):
    out = {"worlds": D8_WORLDS, "break_bar": int(0.6 * N), "after_bars": N - int(0.6 * N),
           "max_hold_bars": D8_MAX_HOLD, "level_pct": int(D8_LEVEL * 100),
           "cutoff_250": _round_mc(d8["cv"][250], d8["cv_se"][250], factor=CUTOFF_SE_FACTOR),
           "cutoff_500": _round_mc(d8["cv"][500], d8["cv_se"][500], factor=CUTOFF_SE_FACTOR)}
    for name in ("break", "good"):
        v = d8[name]
        cell = {}
        for var, r in v["rows"].items():
            c = {"total_mean_pct": _mean(r[:, 0], 1, 100), "total_p5_pct": _pctl(r[:, 0], 5, 1, 100),
                 "sharpe": _mean(r[:, 1])}
            if name == "break":
                c.update({"after_mean_pct": _mean(r[:, 2], 1, 100), "after_p5_pct": _pctl(r[:, 2], 5, 1, 100),
                          "after_p95_pct": _pctl(r[:, 2], 95, 1, 100),
                          "after_worst5_mean_pct": _tail_mean(r[:, 2], 1, 100),
                          "after_loss_pct": _share(r[:, 2] < 0, 0)})
            cell[var] = c
        for w, m in v["monitor"].items():
            if name == "break":
                cell[f"blocked_before_{w}_pct"] = _mean(m["pre"], 0, 100)
                cell[f"blocked_after_{w}_pct"] = _mean(m["post"], 0, 100)
                found = np.isfinite(m["delay"])
                cell[f"detected_{w}_pct"] = _share(found, 0)
                cell[f"delay_median_{w}_bars"] = _pctl(m["delay"][found], 50, 0)
            else:
                cell[f"blocked_{w}_pct"] = _mean(m["pre"], 0, 100)
        cell["hold_median_bars"] = _pctl(v["holds"], 50, 0)
        cell["hold_over_limit_pct"] = _share(v["holds"] >= D8_MAX_HOLD, 1)
        out[name] = cell
    g = out["good"]
    g["price_sharpe_250"] = _gap(g["monitor_250"]["sharpe"], g["none"]["sharpe"])
    g["price_sharpe_500"] = _gap(g["monitor_500"]["sharpe"], g["none"]["sharpe"])
    return out


def _fig_d9(d9, d1):
    out = {"worlds": D9_WORLDS, "test_bars": YEAR, "slow_half_life_bars": int(D9_SLOW_HL)}

    def block(s):
        return {"sharpe_mean": _mean(s), "sharpe_p5": _pctl(s, 5), "sharpe_p50": _pctl(s, 50), "sharpe_p95": _pctl(s, 95),
                "negative_pct": _share(s < 0), "positive_pct": _share(s > 0), "above1_pct": _share(s > 1)}

    for k, v in d9.items():
        out[k] = block(v["sharpe"])
        out[k].update({"trades_mean": _mean(v["n_trades"], 1), "no_trade_pct": _share(v["n_trades"] == 0)})
    out["five_year"] = {k: block(d1["metrics"][k]["sharpe"]) for k in ("good", "fake")}   # มองยาวขึ้น: โลกชุด D1
    out["five_year_worlds"] = D1_WORLDS
    return out


def _hl_text(v):
    """half-life ที่ไม่จำกัด (φ ≥ 1) เก็บเป็นข้อความ — JSON ไม่มี inf"""
    return C.rd(v, 1) if math.isfinite(v) else "∞"


def _p_round(p):
    """p-value จากโลกจำลอง N_NULL โลก — ปัดตามความคลาดของการนับ"""
    return _round_mc(p, math.sqrt(max(p * (1 - p), 1.0 / N_NULL) / N_NULL), 4)


def _p_text(p):
    return "< 0.001" if p < 0.001 else str(_p_round(p))


def _fig_battery(m):
    """ชุดตรวจของคู่ตัวอย่างคู่เดียว — คำนวณตรง ๆ จากราคาสองเส้น (ไม่ใช่ค่าเฉลี่ยจากการสุ่ม) จึงเก็บทศนิยมตามปกติ"""
    failed = [str(i + 1) for i, c in enumerate(CHECKS) if not m["pass"][c]]
    out = {
        "eg_adf": C.rd(m["eg_adf"], 2), "eg_p": _p_round(m["eg_p"]), "eg_p_text": _p_text(m["eg_p"]),
        "shift_sigma": C.rd(m["shift"], 2),
        "beta_train": C.rd(m["beta_train"], 3), "beta_test": C.rd(m["beta_test"], 3),
        "beta_change_pct": C.pct(m["beta_change"], 1),
        "half_life_train_bars": _hl_text(m["hl_train"]), "half_life_test_bars": _hl_text(m["hl_test"]),
        "trades": int(m["n_trades"]), "edge_per_trade_bps": C.bps(m["edge_per_trade"], 0),
        "breakeven_c_bps": C.bps(m["breakeven_c"], 1), "breakeven_ratio": C.rd(m["breakeven_ratio"], 1),
        "sharpe_lag1": C.rd(m["sharpe_lag1"], 2), "sharpe_lag2": C.rd(m["sharpe_lag2"], 2), "z_sd": C.rd(m["z_sd"], 2),
        "passed": m["n_pass"], "failed_checks": ", ".join(failed) if failed else "ไม่มี",
    }
    for c in CHECKS:
        out[f"pass_{c}"] = "ผ่าน" if m["pass"][c] else "ไม่ผ่าน"
    return out


def _fig_d10(d10):
    R = BATTERY_RULES
    out = {
        "rules": {"eg_p_max": R["eg_p_max"], "shift_max_sigma": R["shift_max_sigma"],
                  "beta_change_max_pct": int(R["beta_change_max"] * 100),
                  "hl_min_bars": int(R["hl_min_bars"]), "hl_max_bars": int(R["hl_max_bars"]),
                  "hl_test_max_ratio": int(R["hl_test_max_ratio"]),
                  "breakeven_ratio_min": int(R["breakeven_ratio_min"]),
                  "lag2_keep_min_pct": int(R["lag2_keep_min"] * 100), "cost_bps": C.bps(COST, 0)},
        "pairs": {k: _fig_battery(m) for k, m in d10["pairs"].items()},
        "mc": {"worlds": D1_WORLDS},
    }
    for k, ms in d10["mc"].items():
        cell = {f"pass_{c}_pct": _share([m["pass"][c] for m in ms], 0) for c in CHECKS}
        all6 = [m["n_pass"] == len(CHECKS) for m in ms]
        cell["pass_all_pct"] = _share(all6)
        cell["pass_all_n"] = int(np.sum(all6))          # จำนวนโลก (เมื่อเป็นเหตุการณ์หายาก ให้อ้างจำนวนนับ)
        cell["pass_5plus_pct"] = _share([m["n_pass"] >= len(CHECKS) - 1 for m in ms])
        cell["passed_median"] = int(np.median([m["n_pass"] for m in ms]))
        for key, src, absolute, d, scale in (("eg_p", "eg_p", False, 3, 1), ("shift_abs_sigma", "shift", True, 2, 1),
                                             ("beta_change_abs_pct", "beta_change", True, 1, 100),
                                             ("half_life_train_bars", "hl_train", False, 1, 1),
                                             ("breakeven_ratio", "breakeven_ratio", False, 1, 1)):
            a = np.array([m[src] for m in ms], float)
            a = np.abs(a) if absolute else a
            for q in ((5, 50) if key == "half_life_train_bars" else (5, 50, 95)):   # หางขวาของ half-life ยาวมาก
                cell[f"{key}_p{q}"] = _pctl(a, q, d, scale)
        out["mc"][k] = cell
    return out


def _battery_table(pairs):
    """ตาราง ASCII ของชุดตรวจ (ใช้กับ <!--OUT:p5.outputs.battery-->) — คอลัมน์ตรงกันเพราะไม่มีอักษรไทย"""
    names = list(pairs)

    def num(v, fmt):
        return format(v, fmt) if math.isfinite(v) else "inf"

    rows = [
        ("1 EG p-value (train half)", [_p_text(pairs[k]["eg_p"]).replace(" ", "") for k in names]),
        ("2 mean shift, test vs train (sigma)", [num(pairs[k]["shift"], "+.2f") for k in names]),
        ("3 beta, train half", [num(pairs[k]["beta_train"], ".3f") for k in names]),
        ("  beta, test half", [num(pairs[k]["beta_test"], ".3f") for k in names]),
        ("4 half-life, train (bars)", [num(pairs[k]["hl_train"], ".1f") for k in names]),
        ("  half-life, test (bars)", [num(pairs[k]["hl_test"], ".1f") for k in names]),
        ("5 break-even c / assumed c", [num(pairs[k]["breakeven_ratio"], ".1f") for k in names]),
        ("6 Sharpe, lag 1", [num(pairs[k]["sharpe_lag1"], ".2f") for k in names]),
        ("  Sharpe, lag 2", [num(pairs[k]["sharpe_lag2"], ".2f") for k in names]),
        ("checks passed (of 6)", [str(pairs[k]["n_pass"]) for k in names]),
        ("checks failed", [",".join(str(i + 1) for i, c in enumerate(CHECKS) if not pairs[k]["pass"][c]) or "-"
                           for k in names]),
    ]
    lines = [f"{'check':<36}" + "".join(f"{k:>10}" for k in names), "-" * (36 + 10 * len(names))]
    lines += [f"{label:<36}" + "".join(f"{c:>10}" for c in cells) for label, cells in rows]
    return "\n".join(lines)


def _clinic(f):
    """ตารางคลินิก: โรค → อาการ · วิธีตรวจ · วิธีแก้ · ตัวเลขทำผิด/ทำถูก/ช่องว่าง (ดึงจากตัวเลขที่ปัดแล้วชุดเดียวกัน)
    คีย์ d1 … d9 ตรงกับโรคข้อ 1–9 ของบท (ข้อ 10 ข้อมูลเสีย ไม่มีการทดลองในโมดูลนี้) · battery = ชุดตรวจ D10"""
    def row(name, symptom, test, fix, wrong_label, wrong, right_label, right, unit):
        return {"name": name, "symptom": symptom, "test": test, "fix": fix, "wrong_label": wrong_label,
                "wrong": wrong, "right_label": right_label, "right": right, "gap": _gap(wrong, right), "unit": unit}

    d1, d2, d3, d4, d5, d6, d7, d8, d9, d10 = (f[k] for k in ("d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8",
                                                               "d9", "d10"))
    g5 = d5["good"]
    return {
        "d1": row("คู่ไม่มีสายจูง (เลือกจาก correlation)",
                  "ผลออกมาเหมือนโยนเหรียญ: ไม้ที่ได้กับไม้ที่เสียพอ ๆ กัน ไม้ที่เสียค้างนาน สเปรดไม่กลับมาที่เดิม",
                  "Engle-Granger บนช่วง train และดูว่าค่ากลางของสเปรดช่วง test เลื่อนไปกี่ σ (ชุดตรวจข้อ 1–2)",
                  "หาเหตุผลทางเศรษฐกิจของสายจูงก่อน แล้วใช้สถิติยืนยัน — correlation สูงไม่ใช่หลักฐานของสายจูง",
                  "Sharpe เฉลี่ยของคู่ fake ที่ correlation 0.90", d1["fake_tight"]["sharpe_mean"],
                  "Sharpe เฉลี่ยของคู่ good ที่ correlation 0.90", d1["good"]["sharpe_mean"], "Sharpe"),
        "d2": row("คัดจากหลายคู่ แล้วเชื่อผลของช่วงที่ใช้คัด",
                  "คู่ที่เลือกมาสวยมากในช่วงที่ใช้เลือก แต่พอเดินหน้าต่อผลหายไป",
                  "กันข้อมูลช่วงพิสูจน์ไว้ไม่ให้แตะตอนคัด แล้วนับว่าคัดมาจากกี่คู่ (ยิ่งมาก ยิ่งต้องเข้มกับค่า p)",
                  "คัดด้วยหลักฐานของสายจูง ไม่ใช่ด้วย Sharpe ของ backtest และตัดสินจากช่วงพิสูจน์เท่านั้น",
                  "Sharpe ช่วงคัดเลือกของ 10 อันดับแรก (จักรวาล fake ล้วน · ค่ากลางของ 1,000 จักรวาล)",
                  d2["top_fake_only"]["sharpe_in"],
                  "Sharpe ช่วงพิสูจน์ของ 10 คู่เดียวกัน", d2["top_fake_only"]["sharpe_out"], "Sharpe"),
        "d3": row("พารามิเตอร์มองอนาคต (β, μ, σ จากทั้งช่วง)",
                  "backtest ดีเกินจริง โดยเฉพาะกับคู่ที่ไม่มีสายจูง — พอประมาณแบบเดินหน้ากำไรหายเกือบหมด",
                  "รันซ้ำแบบ walk-forward แล้วเทียบ Sharpe สองแบบ",
                  "ทุกค่าที่ใช้ตัดสินใจ ณ แท่ง t ต้องประมาณจากข้อมูลถึงแท่ง t เท่านั้น",
                  "Sharpe ของคู่ fake เมื่อใช้ β, μ, σ ทั้งช่วง", d3["fake"]["sharpe_lookahead"],
                  "Sharpe ของคู่ fake แบบ walk-forward", d3["fake"]["sharpe_wf"], "Sharpe"),
        "d3_lag": row("ลืมเลื่อนสถานะ (lag = 0)",
                      "กลยุทธ์ที่ควรกำไรกลับแย่ลงมากหรือขาดทุนสม่ำเสมอ ทั้งที่สเปรดดึงกลับจริง",
                      "ลอง lag 0, 1, 2: ถ้า lag 1 ดีกว่า lag 0 มาก แปลว่าโค้ดเดิมจับคู่สถานะกับผลตอบแทนผิดแท่ง",
                      "สถานะที่ตัดสินใจตอนสิ้นแท่ง t รับผลตั้งแต่แท่ง t+1",
                      "Sharpe ของคู่ good เมื่อ lag = 0", d3["lag"]["mc"]["lag0"]["sharpe"],
                      "Sharpe ของคู่ good เมื่อ lag = 1", d3["lag"]["mc"]["lag1"]["sharpe"], "Sharpe"),
        "d4": row("ต้นทุนใหญ่กว่ากำไรต่อไม้",
                  "ก่อนหักต้นทุนกำไรดี หลังหักติดลบ — ยิ่งสเปรดแคบยิ่งเป็น",
                  "วัดกำไรขั้นต้นเฉลี่ยต่อไม้ แล้วเทียบกับต้นทุนครบรอบ 2c (ชุดตรวจข้อ 5)",
                  "เลือกสเปรดที่กว้างพอเมื่อเทียบกับต้นทุน เข้าให้ไกลขึ้น หรือเลิกเทรดคู่นั้น",
                  "Sharpe ที่ σ 0.5% เมื่อไม่คิดต้นทุน", d4["s0_5"]["c0"]["sharpe"],
                  "Sharpe ที่ σ 0.5% เมื่อ c = 20 bps", d4["s0_5"]["c20"]["sharpe"], "Sharpe"),
        "d5": row("หน้าต่าง z-score ผิดขนาด",
                  "สั้นไป: เข้าออกถี่ กำไรต่อไม้เล็ก · ยาวไป: ถือค้างนานเมื่อค่ากลางเลื่อน",
                  "ลองหน้าต่าง 1–32 เท่าของ half-life แล้วดูว่า Sharpe เปลี่ยนเร็วแค่ไหน",
                  "ใช้หน้าต่างราว 4–16 เท่าของ half-life และอย่าเลือกค่าที่ผลดีอยู่ค่าเดียว",
                  "Sharpe ที่หน้าต่าง 1 เท่าของ half-life (โลกปกติ)", g5["w12"]["sharpe"],
                  f"Sharpe ที่หน้าต่างดีที่สุด (โลกปกติ · {_plateau_txt(g5)} เท่าของ half-life ให้ผลพอ ๆ กัน)",
                  g5["best_sharpe"], "Sharpe"),
        "d6": row("การดึงกลับปลอมจาก noise ของราคา",
                  "half-life ที่ประมาณได้สั้นผิดปกติ กำไรมาจากไม้สั้น ๆ จำนวนมาก และหายไปเมื่อได้ราคาช้าหนึ่งแท่ง",
                  "เทียบ lag 1 กับ lag 2 และดู half-life (ชุดตรวจข้อ 4 และ 6)",
                  "ลงบัญชีด้วยราคาที่ซื้อขายได้จริง (bid/ask หรือแท่งถัดไป) และใช้ข้อมูลที่บันทึกพร้อมกัน",
                  "Sharpe เมื่อลงบัญชีที่ราคาที่เห็น (สเปรดแคบ σ 1%)", d6["tight"]["wf"]["print_lag1"]["sharpe"],
                  "Sharpe เมื่อลงบัญชีที่ราคาจริง", d6["tight"]["wf"]["true_lag1"]["sharpe"], "Sharpe"),
        "d7": row("stop ที่ตัดกำไรทิ้ง",
                  "อัตราชนะตกฮวบ ไม้ที่โดน stop มักกลับมาถูกทางหลังจากเราออกไปแล้ว",
                  "รันกฎเดิมโดยถอด stop ออก แล้วเทียบ Sharpe กับอัตราชนะ",
                  "ถ้าต้องมี ให้วาง stop ไกล และใช้สวิตช์ระดับคู่ (D8) แทน stop ระดับไม้",
                  "Sharpe ของคู่ good เมื่อ stop ที่ z = 2.5", d7["good"]["stop2_5"]["sharpe"],
                  "Sharpe ของคู่ good เมื่อไม่มี stop", d7["good"]["none"]["sharpe"], "Sharpe"),
        "d8": row("สายจูงขาด แต่ไม่มีสวิตช์ตัด",
                  "กำไรดีมาตลอด แล้วขาดทุนก้อนใหญ่ไม่กี่ครั้งกินกำไรเกือบหมด",
                  "ทดสอบ Engle-Granger ซ้ำบนข้อมูลล่าสุดเป็นระยะ และดูผลแยกช่วงก่อน/หลัง",
                  "เฝ้าด้วยหน้าต่างที่ยาวพอ (500 แท่ง) — หน้าต่างสั้นเตือนผิดบ่อยจนกินกำไรของคู่ที่ดี",
                  "ค่าเฉลี่ยของโลกที่แย่ที่สุด 5% หลังสายจูงขาด เมื่อไม่มีสวิตช์",
                  d8["break"]["none"]["after_worst5_mean_pct"],
                  "ค่าเดียวกันเมื่อเฝ้าด้วย EG 500 แท่ง", d8["break"]["monitor_500"]["after_worst5_mean_pct"],
                  "% ของเงินรวมสองขา"),
        "d9": row("ข้อมูลน้อยเกินจะบอกอะไร",
                  "ตัดสินจาก backtest หนึ่งปีที่มีไม่กี่ไม้ — คู่ปลอมก็ดูดีได้ คู่จริงก็ดูแย่ได้",
                  "นับจำนวนไม้ และถามว่า Sharpe ที่เห็นอยู่ในช่วงที่คู่ไม่มีสายจูงก็ทำได้หรือไม่",
                  "ใช้ข้อมูลยาวขึ้น ทดสอบหลายคู่ที่มีสายจูงแบบเดียวกัน และอย่าสรุปจากปีเดียว",
                  "โอกาสที่คู่ fake ได้ Sharpe > 1 ใน 1 ปี", d9["fake"]["above1_pct"],
                  "โอกาสเดียวกันเมื่อดูราว 5 ปี", d9["five_year"]["fake"]["above1_pct"], "% ของโลก"),
        "battery": row("ไม่เคยตรวจเองก่อนเชื่อ backtest",
                       "ไม่รู้ว่าโรคไหน เพราะดูแต่เส้นกำไรสะสม",
                       "ชุดตรวจ 6 ข้อ: EG · ค่ากลางเลื่อน · β เปลี่ยน · half-life · จุดเท่าทุนของต้นทุน · lag 1 เทียบ lag 2",
                       "รันชุดตรวจก่อนทุกครั้ง แล้วไล่แก้ตามข้อที่ไม่ผ่าน",
                       "สัดส่วนโลก fake ที่ผ่านครบ 6 ข้อ", d10["mc"]["fake"]["pass_all_pct"],
                       "สัดส่วนโลก good ที่ผ่านครบ 6 ข้อ", d10["mc"]["good"]["pass_all_pct"], "% ของโลก"),
    }


def _about():
    return {
        "common": f"ข้อมูลจำลอง {N:,} แท่งต่อโลก · walk-forward: train {TRAIN} แท่ง ประมาณใหม่ทุก {REFIT} แท่ง · "
                  f"เข้า |z| ≥ {ENTRY:g} ออก z = {EXIT:g} · ต้นทุน c = {COST * 1e4:g} bps ต่อขาต่อเที่ยว · "
                  "lag 1 เป็นมาตรฐาน และรายงาน lag 2 คู่กัน · z วัดด้วย σ ของช่วง train",
        "rounding": "ตัวเลขจาก Monte Carlo ปัดให้หน่วยของหลักสุดท้าย ≥ ความคลาดจากการสุ่ม (SE) — ค่าวิกฤตที่จำลอง ≥ 2 SE — "
                    "จึงบางค่าเป็นทศนิยมหนึ่งตำแหน่ง จำนวนเต็ม หรือหลักสิบ ให้เขียนว่า \"ราว\" · หลักสุดท้ายยังขยับได้ราว ±1 "
                    "เมื่อเปลี่ยนเลขสุ่ม · ค่าของคู่ตัวอย่างคู่เดียว จำนวนนับ และสูตร ไม่ได้ปัดแบบนี้",
        "d1": f"{D1_WORLDS} โลกต่อกลุ่ม: good · fake (ค่าตั้งต้น) · fake_tight (ปัจจัยร่วมแรงขึ้นจน correlation ของ"
              "ผลตอบแทนเท่าคู่ good) · ทดสอบราว 5 ปีต่อโลก",
        "d2": f"สระ {D2_FAKE} คู่ fake + {D2_GOOD} คู่ good · คัดด้วย Engle-Granger บน {HALF} แท่งแรก (ค่าวิกฤตจำลอง "
              f"{N_NULL:,} โลก) · ช่วงคัดเลือกเทรดแท่ง {TRAIN}–{HALF - 1} ช่วงพิสูจน์เทรดแท่ง {HALF}–{N - 1} "
              f"เป็น walk-forward ทั้งคู่ · level* = การสแกนจริงหนึ่งรอบ · top_* = ค่ากลางของ {D2_BOOT:,} จักรวาลที่สุ่มซ้ำ"
              "จากสระ (scan_* = รอบจริง)",
        "d3": f"{D3_WORLDS} โลกต่อแบบ (good, drift, fake) · มองอนาคต = β, μ, σ จากทั้ง {N:,} แท่ง · นับผลแท่ง "
              f"{TRAIN}–{N - 1} เท่ากันทั้งสองวิธี · lag 0/1/2 ใช้สถานะชุดเดียวกันของ walk-forward บนโลก good",
        "d4": f"{D4_WORLDS} โลกต่อค่า σ_eq (0.5, 1, 2, 4%) · half-life {HL:g} แท่ง · β = {BETA} · "
              "c = 0, 2, 5, 10, 20, 50 bps · สถานะชุดเดียวกันทุกต้นทุน",
        "d5": f"{D5_WORLDS} โลกต่อแบบ · z จากหน้าต่างเลื่อน 12–384 แท่ง (1–32 เท่าของ half-life) ไม่รวมแท่งปัจจุบัน · "
              f"β จาก {D5_BURN} แท่งแรก · นับผลแท่ง {D5_BURN}–{N - 1} · โลกค่ากลางไหล: ค่ากลางเดินสุ่ม sd "
              f"{D5_SIGMA_MU * 100:g}% ต่อแท่ง · c = 5 bps",
        "d6": f"{D6_WORLDS} โลกต่อแบบ · สเปรดจริง half-life {D6_HL:g} แท่ง (σ_eq 1% หรือ 3%) · ราคาที่เห็น = ราคาจริง + "
              f"noise sd {D6_NOISE * 100:g}% ต่อขา · สัญญาณจากราคาที่เห็นเสมอ · c = 5 bps",
        "d7": f"stop ที่ |z| = 2.5, 3, 4 (หน่วย σ ของช่วง train) บนโลก good {D1_WORLDS} โลก (ชุด D1) และโลก break "
              f"{D8_WORLDS} โลก (ชุด D8) · c = 5 bps",
        "d8": f"{D8_WORLDS} โลก break (สายจูงขาดที่แท่ง {int(0.6 * N)}) · จำกัดเวลาถือ {D8_MAX_HOLD} แท่ง · "
              f"สวิตช์ Engle-Granger ที่ระดับ {int(D8_LEVEL * 100)}% บน 250 หรือ 500 แท่งล่าสุด ตรวจทุก {REFIT} แท่ง · "
              f"ราคาที่ต้องจ่ายวัดบนโลก good {D1_WORLDS} โลก · worst5 = ค่าเฉลี่ยของ 5% ของโลกที่แย่ที่สุด",
        "d9": f"{D9_WORLDS:,} โลกต่อแบบ · train {TRAIN} แท่ง แล้ววัด Sharpe ของ {YEAR} แท่งถัดไป (1 ปี) · "
              f"good = half-life {HL:g} · slow = half-life {D9_SLOW_HL:g} · fake · c = 5 bps",
        "d10": f"ชุดตรวจ 6 ข้อ: ครึ่งแรก {HALF} แท่ง = train ครึ่งหลัง = test · ข้อ 5–6 ใช้ walk-forward ทั้งเส้น · "
               f"คู่ตัวอย่าง 5 คู่ (good, fake, drift, break ของชุด + noisy = โลกแรกของ D6 แบบ σ_eq 1% ใช้ราคาที่เห็น) "
               f"+ อัตราผ่านบนโลก good/fake {D1_WORLDS} โลก (ชุด D1)",
        "demo_note": "คู่ตัวอย่าง (demo) ถูกเลือกให้เห็นอาการชัด ข้อสรุปทั่วไปให้ดูค่าเฉลี่ยจากหลายโลก",
    }


def figures(res=None):
    """ตัวเลขทุกตัวของตอนที่ 5 (ปัดแล้ว) → ใช้กับ data-f="p5.<path>\""""
    res = res or run()
    f = {
        "about": _about(),
        "settings": {"bars": N, "train_bars": TRAIN, "refit_bars": REFIT, "entry_z": int(ENTRY), "exit_z": int(EXIT),
                     "cost_bps": int(round(COST * 1e4)), "round_trip_bps": int(round(2 * COST * 1e4)),
                     "null_worlds": N_NULL, "test_years": C.rd(TEST_YEARS, 1),
                     "eg_cutoff_750_5pct": _round_mc(res["cv_half"][0.05], res["cv_half_se"][0.05], factor=CUTOFF_SE_FACTOR),
                     "eg_cutoff_750_1pct": _round_mc(res["cv_half"][0.01], res["cv_half_se"][0.01], factor=CUTOFF_SE_FACTOR)},
        "d1": _fig_d1(res["d1"]), "d2": _fig_d2(res["d2"], res["cv_half_se"]), "d3": _fig_d3(res["d3"]),
        "d4": _fig_d4(res["d4"]), "d5": _fig_d5(res["d5"]), "d6": _fig_d6(res["d6"]), "d7": _fig_d7(res["d7"]),
        "d8": _fig_d8(res["d8"]), "d9": _fig_d9(res["d9"], res["d1"]), "d10": _fig_d10(res["d10"]),
    }
    f["clinic"] = _clinic(f)
    f["outputs"] = {"battery": _battery_table(res["d10"]["pairs"])}
    return f


# ───────────────────────── charts ─────────────────────────

def _txt(v, sign=False):
    """พิมพ์ค่าที่ปัดแล้วด้วยจำนวนทศนิยมเท่าที่เก็บไว้ (1.6 → "1.6" ไม่ใช่ "1.60")"""
    return V.num(v, _dec(v), sign=sign)


def _shown_as(pairs, sign=False):
    """fmt ของกราฟ: วางจุดที่ค่าดิบ แต่พิมพ์ตัวเลขชุดเดียวกับ figures (ค่าที่ปัดแล้ว)"""
    table = {float(raw): _txt(shown, sign) for raw, shown in pairs}
    return lambda v: table.get(float(v), V.num(v, 1, sign=sign))


def _chart_corr(cid, res, f):
    m, d = res["d1"]["metrics"], f["d1"]
    rows, shown = [], []
    for k, label, color in (("good", "คู่ good — มีสายจูง", V.BLUE), ("fake", "คู่ fake — ไม่มีสายจูง", V.RED),
                            ("fake_tight", "คู่ fake ที่ correlation สูงขึ้น", V.RED)):
        s = m[k]["sharpe"]
        raw = (float(s.mean()), float(np.percentile(s, 5)), float(np.percentile(s, 95)))
        rows.append({"label": f"{label}\ncorrelation {_txt(d[k]['ret_corr_median'])}", "mid": raw[0], "lo": raw[1],
                     "hi": raw[2], "color": color})
        shown += zip(raw, (d[k]["sharpe_mean"], d[k]["sharpe_p5"], d[k]["sharpe_p95"]))
    t = d["fake_tight"]
    return V.dot_interval(
        cid, rows,
        "Sharpe ของ walk-forward บนสามกลุ่ม: คู่ที่มีสายจูงอยู่เหนือศูนย์ทั้งช่วง ส่วนคู่ที่ไม่มีสายจูงกระจายรอบศูนย์ "
        "ไม่ว่า correlation จะสูงแค่ไหน",
        f"ข้อมูลจำลอง {D1_WORLDS} โลกต่อกลุ่ม ทดสอบราว 5 ปีต่อโลก หลังต้นทุน 5 bps · จุด = ค่าเฉลี่ย เส้น = ช่วง 5–95% · "
        f"คู่ fake ที่ correlation ของผลตอบแทนสูงถึง {_txt(t['ret_corr_median'])} เท่ากับคู่ good "
        f"ยังได้ Sharpe เฉลี่ยราว {_txt(t['sharpe_mean'])} และกำไรเพียงราว {t['profitable_pct']}% ของโลก (เท่ากับโยนเหรียญ) "
        f"ขณะที่คู่ good ได้ราว {_txt(d['good']['sharpe_mean'])} — correlation สูงไม่ได้บอกว่ามีสายจูง",
        xlabel="Sharpe ต่อปี (walk-forward · lag 1)", fmt=_shown_as(shown), mid_name="ค่าเฉลี่ย")


def _chart_selection(cid, res, f):
    d2, d = res["d2"], f["d2"]
    s_in, s_out, good = d2["sharpe_in"], d2["sharpe_out"], d2["is_good"]
    top = d2["scan"]["top_backtest"]
    lo = math.floor(min(s_in.min(), s_out.min()) * 2) / 2
    hi = math.ceil(max(s_in.max(), s_out.max()) * 2) / 2
    ticks = [t for t in V.nice_ticks(lo, hi, 7) if lo <= t <= hi]
    items = [(f"คู่ fake {D2_FAKE} คู่", V.RED, "dot"), (f"คู่ good {D2_GOOD} คู่", V.BLUE, "dot"),
             (f"{D2_TOP} อันดับ Sharpe สูงสุดในช่วงคัดเลือก", V.PURPLE, "ring"), ("เส้น y = x", V.MUTED, "line", "5 4")]
    fig = V.Fig(cid, 760, 452)
    p = fig.panel((lo, hi), (lo, hi), x=62, y=66, w=678, h=336)
    p.grid(yticks=ticks, xticks=ticks).yaxis(ticks=ticks, title="Sharpe ในช่วงพิสูจน์ (แท่ง 750–1499)")
    p.legend(items)
    p.hline(0, color=V.AXIS, dash=None, width=1.0).vline(0, color=V.AXIS, dash=None, width=1.0)
    p.line([lo, hi], [lo, hi], V.MUTED, width=1.2, dash="5 4")
    p.scatter(s_in[~good], s_out[~good], V.RED, r=2.3, opacity=0.4)
    p.scatter(s_in[good], s_out[good], V.BLUE, r=3.2, opacity=0.9)
    rings = "".join(f'<circle cx="{p.X(a):.1f}" cy="{p.Y(b):.1f}" r="7"/>' for a, b in zip(s_in[top], s_out[top]))
    fig.add(f'<g fill="none" stroke="{V.PURPLE}" stroke-width="2">{rings}</g>')      # วงกลวง: ยังเห็นสีของจุดข้างใน
    p.xaxis(ticks=ticks, title="Sharpe ในช่วงคัดเลือก (แท่ง 250–749)")
    tb, tf = d["top_backtest"], d["top_fake_only"]
    return fig.svg(
        "จุดกระจายของ Sharpe ช่วงคัดเลือกเทียบกับช่วงพิสูจน์ของ 440 คู่: คู่ fake เป็นก้อนกลมรอบศูนย์ที่ไม่เอียงตามเส้นทแยง "
        "คู่ good อยู่มุมขวาบน",
        f"ข้อมูลจำลอง {D2_FAKE + D2_GOOD} คู่ · แต่ละจุดคือหนึ่งคู่ · ก้อนสีแดง (fake) ไม่เอียงตามเส้น y = x: "
        f"Sharpe ช่วงคัดเลือกบอกอะไรเกี่ยวกับช่วงพิสูจน์ไม่ได้ (correlation {_txt(d['all']['fake_corr_in_out'])}) · "
        f"วงม่วงคือ {D2_TOP} อันดับแรกของการสแกนรอบนี้ ({tb['scan_n_good']} คู่จริง {tb['scan_n_fake']} คู่ปลอม) · "
        f"ถ้าสุ่มจักรวาลแบบนี้ซ้ำ {D2_BOOT:,} ครั้ง {D2_TOP} อันดับแรกเฉลี่ยราว {_txt(tb['sharpe_in'])} ในช่วงคัดเลือก "
        f"เหลือราว {_txt(tb['sharpe_out'])} ในช่วงพิสูจน์ · ถ้าจักรวาลมีแต่คู่ fake: จากราว {_txt(tf['sharpe_in'])} "
        f"เหลือราว {_txt(tf['sharpe_out'])}")


def _chart_lookahead(cid, res, f):
    d = f["d3"]
    kinds = ("good", "drift", "fake")
    return V.grouped_bars(
        cid, ["good\nสายจูงจริง β คงที่", "drift\nสายจูงจริง แต่ β เลื่อน", "fake\nไม่มีสายจูง"],
        [{"name": "β, μ, σ จากข้อมูลทั้งช่วง (มองอนาคต)", "values": [d[k]["sharpe_lookahead"] for k in kinds],
          "color": V.RED},
         {"name": "walk-forward (ใช้ข้อมูลถึงแท่งนั้นเท่านั้น)", "values": [d[k]["sharpe_wf"] for k in kinds],
          "color": V.BLUE}],
        "Sharpe เฉลี่ยของ backtest ที่ใช้พารามิเตอร์จากทั้งช่วง เทียบกับ walk-forward บนโลกสามแบบ",
        f"ข้อมูลจำลอง {D3_WORLDS} โลกต่อแบบ หลังต้นทุน 5 bps · ที่อันตรายที่สุดคือคู่ fake: การมองอนาคตทำให้คู่ที่ไม่มีสายจูง "
        f"ดูเหมือนได้ Sharpe ราว {_txt(d['fake']['sharpe_lookahead'])} (กำไรราว {d['fake']['profitable_lookahead_pct']}% "
        f"ของโลก) ทั้งที่ของจริงคือราว {_txt(d['fake']['sharpe_wf'])} · คู่ good ต่างกันเล็กน้อย · คู่ drift กลับแย่ลงเมื่อใช้ "
        "β ค่าเดียวทั้งช่วง เพราะ β ค่าเดียวตาม β ที่เลื่อนไม่ทัน",
        ylabel="Sharpe เฉลี่ย", fmt=_txt)


def _chart_lag(cid, res, f):
    mc, noisy = f["d3"]["lag"]["mc"], f["d6"]["tight"]["wf"]
    return V.grouped_bars(
        cid, ["lag 0 (บั๊ก)\nรับผลของแท่งที่ให้สัญญาณ", "lag 1 (มาตรฐาน)\nเริ่มรับผลแท่งถัดไป",
              "lag 2 (เข้มกว่า)\nได้ราคาช้าไปหนึ่งแท่ง"],
        [{"name": f"คู่ good ราคาสะอาด ({D3_WORLDS} โลก)", "values": [mc[f"lag{k}"]["sharpe"] for k in (0, 1, 2)],
          "color": V.BLUE},
         {"name": f"คู่ที่ราคามี noise 0.3% ต่อขา ({D6_WORLDS} โลก)",
          "values": [noisy[f"print_lag{k}"]["sharpe"] for k in (0, 1, 2)], "color": V.AMBER}],
        "Sharpe เฉลี่ยเมื่อเลื่อนสถานะ 0, 1, 2 แท่ง: คู่ราคาสะอาดเสียมากที่ lag 0 ส่วนคู่ที่ราคามี noise ดีเฉพาะที่ lag 1",
        f"ข้อมูลจำลอง · สถานะชุดเดียวกัน เปลี่ยนเฉพาะแท่งที่เริ่มรับผล · คู่ good: lag 0 ทำให้ Sharpe ตกจากราว "
        f"{_txt(mc['lag1']['sharpe'])} เหลือราว {_txt(mc['lag0']['sharpe'])} ส่วน lag 2 เปลี่ยนน้อย ({_txt(mc['lag2']['sharpe'])}) · "
        f"คู่ที่ราคามี noise (σ_eq 1%): lag 1 ได้ราว {_txt(noisy['print_lag1']['sharpe'])} แต่ lag 2 เหลือราว "
        f"{_txt(noisy['print_lag2']['sharpe'])} — กำไรที่หายเมื่อช้าไปหนึ่งแท่งคือกำไรจาก noise ไม่ใช่จากสายจูง",
        ylabel="Sharpe เฉลี่ย", fmt=_txt)


def _chart_cost_grid(cid, res, f):
    d = f["d4"]
    keys = [_sigma_key(s) for s in D4_SIGMAS]
    cols = [_cost_key(c) for c in D4_COSTS]
    values = [[d[k][c]["sharpe"] for c in cols] for k in keys]
    s = d["s0_5"]
    return V.heat_table(
        cid, [f"σ = {sig * 100:g}%" for sig in D4_SIGMAS], [f"{c * 1e4:g}" for c in D4_COSTS], values,
        "ตาราง Sharpe เฉลี่ยตามความกว้างของสเปรดและต้นทุน: มุมซ้ายล่างเป็นบวก มุมขวาบนติดลบ",
        f"ข้อมูลจำลอง {D4_WORLDS} โลกต่อแถว · half-life 12 แท่ง · ตัวเลข = Sharpe เฉลี่ยหลังต้นทุน · ไล่จากซ้ายไปขวาในแถวบนสุด: "
        f"สเปรดแคบ 0.5% เริ่มที่ราว {_txt(s['c0']['sharpe'], True)} และติดลบตั้งแต่ c = 20 bps "
        f"({_txt(s['c20']['sharpe'], True)}) · จุดเท่าทุนที่วัดได้คือ c ราว {_txt(s['breakeven_c_bps'])} bps "
        f"หรือกล่าวอีกแบบ สเปรดต้องกว้างอย่างน้อยราว {_txt(d['measured_sigma_over_c'])} เท่าของ c จึงจะเท่าทุน "
        f"(สูตรที่คิดด้วย σ จริงบอก {_txt(d['formula_sigma_over_c'])} เท่า)",
        scale="div", fmt=lambda v: _txt(v, True), row_title="ความกว้างของสเปรด (σ_eq)",
        col_title="ต้นทุนต่อขาต่อเที่ยว c (bps)")


def _chart_window(cid, res, f):
    d, d5 = f["d5"], res["d5"]
    ws = d5["windows"]
    n = len(ws)
    # จุด "ไม่เลื่อน" เป็นกฎคนละแบบ จึงแยกออกมาทางขวาและไม่ต่อเส้น (NaN ตรงกลางตัดเส้น)
    x = list(range(n)) + [n - 0.3, n + 0.4]
    ticks, labels = list(range(n)) + [n + 0.4], [f"{k}×" for k in D5_MULTS] + ["ไม่เลื่อน"]

    def ys(name):                             # วาดค่าเฉลี่ยดิบ (รูปทรงของเส้นแม่นกว่าค่าที่ปัดแล้ว)
        r = d5["worlds"][name]
        return [float(r[w]["sharpe"].mean()) for w in ws] + [math.nan, float(r["fixed"]["sharpe"].mean())]

    series = [{"name": label, "y": ys(name), "color": color}
              for name, label, color in (("good", "โลกปกติ (ค่ากลางคงที่)", V.BLUE),
                                         ("drifting", "โลกที่ค่ากลางไหลช้า ๆ", V.AMBER))]
    g, dr = d["good"], d["drifting"]
    return V.line_chart(
        cid, x, series,
        "Sharpe เฉลี่ยตามขนาดหน้าต่างของ z-score: หน้าต่างสั้นแย่ทั้งสองโลก หน้าต่างยาวแย่เฉพาะโลกที่ค่ากลางไหล",
        f"ข้อมูลจำลอง {D5_WORLDS} โลกต่อแบบ หลังต้นทุน 5 bps · หน้าต่าง 1× (12 แท่ง) วิ่งตามสเปรดจนเหลือ Sharpe ราว "
        f"{_txt(g['w12']['sharpe'])} เทียบกับราว {_txt(g['best_sharpe'])} ที่ {_plateau_txt(g)}× "
        f"(ช่วงที่ดีพอ ๆ กัน) · ในโลกที่ค่ากลางไหล หน้าต่างยาวเกินไปก็เสีย: ราว {_txt(dr['best_sharpe'])} ที่ "
        f"{_plateau_txt(dr)}× เหลือราว {_txt(dr['w384']['sharpe'])} ที่ 32× และราว "
        f"{_txt(dr['fixed']['sharpe'])} เมื่อไม่เลื่อนเลย (จุดขวาสุด = μ, σ จาก 400 แท่งแรกตลอด)",
        xlabel="ขนาดหน้าต่าง เป็นจำนวนเท่าของ half-life (1× = 12 แท่ง)",
        ylabel="Sharpe เฉลี่ย", xticks=ticks, xlabels=labels, zero=True, markers=True, yfmt=lambda v: V.num(v, 1))


def _chart_micro(cid, res, f):
    d = f["d6"]
    cells = [(d[w][s]) for w in ("tight", "wide") for s in ("wf", "short")]
    short = cells[1]
    return V.grouped_bars(
        cid, ["สเปรดแคบ σ 1%\nwalk-forward", "สเปรดแคบ σ 1%\nหน้าต่างสั้น 10 แท่ง",
              "สเปรดกว้าง σ 3%\nwalk-forward", "สเปรดกว้าง σ 3%\nหน้าต่างสั้น 10 แท่ง"],
        [{"name": "ลงบัญชีที่ราคาที่เห็น · lag 1", "values": [c["print_lag1"]["ann_return_pct"] for c in cells],
          "color": V.RED},
         {"name": "ที่ราคาที่เห็น · lag 2", "values": [c["print_lag2"]["ann_return_pct"] for c in cells],
          "color": V.AMBER},
         {"name": "ที่ราคาจริง · lag 1", "values": [c["true_lag1"]["ann_return_pct"] for c in cells],
          "color": V.BLUE}],
        "ผลตอบแทนต่อปีของกลยุทธ์เดียวกันเมื่อลงบัญชีสามแบบ: ที่ราคาที่เห็นได้กำไรสูง แต่ที่ราคาจริงหรือเมื่อช้าไปหนึ่งแท่ง "
        "กำไรหายหรือกลายเป็นขาดทุน",
        f"ข้อมูลจำลอง {D6_WORLDS} โลกต่อแบบ · สเปรดจริงดึงกลับช้า (half-life 40 แท่ง) แต่ราคาที่เห็นมี noise 0.3% ต่อขา "
        f"ทำให้ half-life ที่ประมาณได้เหลือราว {_txt(d['tight']['hl_print_bars'])} แท่ง (σ 1%) · กลยุทธ์หน้าต่างสั้นที่ออกแบบตาม "
        f"half-life ปลอมนี้ได้ราว {_txt(short['print_lag1']['ann_return_pct'], True)}% ต่อปีในบัญชี แต่ที่ราคาจริงคือราว "
        f"{_txt(short['true_lag1']['ann_return_pct'], True)}% · สังเกตว่าแท่งสีส้ม (lag 2) สูงพอ ๆ กับแท่งน้ำเงิน (ราคาจริง) "
        "ทุกกลุ่ม: ไม่ต้องรู้ราคาจริงก็ตรวจได้ด้วยการเลื่อนอีกหนึ่งแท่ง",
        ylabel="ผลตอบแทนเฉลี่ยต่อปี (% ของเงินรวมสองขา)", fmt=lambda v: _txt(v, True))


def _chart_stops(cid, res, f):
    d = f["d7"]
    keys = ["none"] + [_stop_key(s) for s in reversed(D7_STOPS)]
    g, b = d["good"], d["break"]
    return V.grouped_bars(
        cid, ["ไม่มี stop"] + [f"stop ที่ |z| = {s:g}" for s in reversed(D7_STOPS)],
        [{"name": f"โลก good ({D1_WORLDS} โลก)", "values": [g[k]["sharpe"] for k in keys], "color": V.BLUE},
         {"name": f"โลก break — สายจูงขาดกลางทาง ({D8_WORLDS} โลก)", "values": [b[k]["sharpe"] for k in keys],
          "color": V.AMBER}],
        "Sharpe เฉลี่ยเมื่อวาง stop ใกล้ขึ้นเรื่อย ๆ: ลดลงทั้งในโลกที่สายจูงดีและโลกที่สายจูงขาด",
        f"ข้อมูลจำลอง หลังต้นทุน 5 bps · เข้าที่ |z| = 2 · ยิ่ง stop ใกล้ ยิ่งตัดไม้ที่กำลังจะกลับมา: ในโลก good "
        f"อัตราชนะตกจากราว {g['none']['hit_rate_pct']}% เหลือราว {g['stop2_5']['hit_rate_pct']}% และ Sharpe จากราว "
        f"{_txt(g['none']['sharpe'])} เหลือราว {_txt(g['stop2_5']['sharpe'])} · stop ไม่ได้ช่วยแม้ในโลกที่สายจูงขาด "
        f"(Sharpe ราว {_txt(b['none']['sharpe'])} เหลือราว {_txt(b['stop2_5']['sharpe'])} และโลกที่แย่ที่สุด 5% แย่ลงจากราว "
        f"{_txt(b['none']['total_p5_pct'], True)}% เป็นราว {_txt(b['stop2_5']['total_p5_pct'], True)}%)",
        ylabel="Sharpe เฉลี่ย", fmt=_txt)


def _chart_killswitch(cid, res, f):
    rows_raw, d = res["d8"]["break"]["rows"], f["d8"]
    b, g = d["break"], d["good"]
    labels = {
        "none": "ไม่มีสวิตช์", "time": f"จำกัดเวลาถือ {D8_MAX_HOLD} แท่ง",
        "monitor_250": "เฝ้าด้วย EG 250 แท่ง", "monitor_500": "เฝ้าด้วย EG 500 แท่ง",
        "both": "EG 500 แท่ง + จำกัดเวลาถือ",
    }
    rows, shown = [], []
    for v in D8_VARIANTS:
        a = 100.0 * rows_raw[v][:, 2]
        raw = (float(a.mean()), float(np.percentile(a, 5)), float(np.percentile(a, 95)))
        rows.append({"label": f"{labels[v]}\nบนโลก good: Sharpe {_txt(g[v]['sharpe'])}",
                     "mid": raw[0], "lo": raw[1], "hi": raw[2], "color": V.RED if v == "none" else V.BLUE})
        shown += zip(raw, (b[v]["after_mean_pct"], b[v]["after_p5_pct"], b[v]["after_p95_pct"]))
    return V.dot_interval(
        cid, rows,
        "กำไรขาดทุนหลังสายจูงขาดของห้าวิธี: สวิตช์ Engle-Granger ตัดหางด้านขาดทุนให้สั้นลงมาก แลกกับค่าเฉลี่ยและหางด้านกำไร"
        "ที่ลดลง",
        f"ข้อมูลจำลอง {D8_WORLDS} โลก break · ผลรวม {d['after_bars']} แท่งหลังสายจูงขาด หลังต้นทุน 5 bps · "
        f"ไม่มีสวิตช์: 5% ของโลกที่แย่ที่สุดขาดทุนเฉลี่ยราว {_txt(abs(b['none']['after_worst5_mean_pct']))}% · "
        f"จำกัดเวลาถืออย่างเดียวช่วยได้บ้าง (ราว {_txt(abs(b['time']['after_worst5_mean_pct']))}%) · สวิตช์ EG 500 แท่งหดเหลือ"
        f"ราว {_txt(abs(b['monitor_500']['after_worst5_mean_pct']))}% แต่ค่าเฉลี่ยหลังขาดก็ลดจากราว "
        f"{_txt(b['none']['after_mean_pct'], True)}% เป็นราว {_txt(b['monitor_500']['after_mean_pct'], True)}% และ Sharpe บนโลก good "
        f"ลดจากราว {_txt(g['none']['sharpe'])} เป็นราว {_txt(g['monitor_500']['sharpe'])} · สวิตช์ 250 แท่งเตือนผิดราว "
        f"{g['blocked_250_pct']}% ของเวลาบนคู่ที่ดี (Sharpe เหลือราว {_txt(g['monitor_250']['sharpe'])})",
        xlabel="กำไรขาดทุนสะสมหลังสายจูงขาด (% ของเงินรวมสองขา)", fmt=_shown_as(shown, True),
        mid_name="ค่าเฉลี่ย")


def _chart_sample_size(cid, res, f):
    d9, d = res["d9"], f["d9"]
    edges = np.arange(-4.0, 5.01, 0.5)
    x = (edges[:-1] + edges[1:]) / 2

    def density(k):
        s = np.clip(d9[k]["sharpe"], edges[0], edges[-1] - 1e-9)
        return 100.0 * np.histogram(s, edges)[0] / len(s)

    return V.line_chart(
        cid, x,
        [{"name": "คู่ good (half-life 12)", "y": density("good"), "color": V.BLUE},
         {"name": "คู่ที่สายจูงจริงแต่ช้า (half-life 40)", "y": density("slow"), "color": V.AMBER},
         {"name": "คู่ fake (ไม่มีสายจูง)", "y": density("fake"), "color": V.RED}],
        "การกระจายของ Sharpe หนึ่งปีของคู่สามแบบ ซ้อนทับกันเป็นบริเวณกว้าง",
        f"ข้อมูลจำลอง {D9_WORLDS:,} โลกต่อแบบ · Sharpe ที่เกิดขึ้นจริงใน 1 ปี (เฉลี่ยเพียงราว {_txt(d['good']['trades_mean'])} ไม้) "
        f"หลังต้นทุน 5 bps · คู่ fake ได้ Sharpe เกิน 1 ราว {_txt(d['fake']['above1_pct'])}% ของโลก ขณะที่คู่ที่มีสายจูงจริง"
        f"แต่ช้าติดลบราว {_txt(d['slow']['negative_pct'])}% ของโลก — ปีเดียวแยกสองแบบนี้ออกจากกันไม่ได้",
        xlabel="Sharpe ที่เกิดขึ้นจริงใน 1 ปี (ช่องละ 0.5)", ylabel="% ของโลก", markers=False,
        vlines=[(0, "Sharpe 0"), (1, "Sharpe 1")], zero=True, yfmt=lambda v: V.num(v, 0))


def _chart_battery(cid, res, f):
    mc, R = f["d10"]["mc"], f["d10"]["rules"]
    labels = [
        f"1 · Engle-Granger ช่วง train: p < {R['eg_p_max']}",
        f"2 · ค่ากลางช่วง test เลื่อน < {R['shift_max_sigma']:g} σ",
        f"3 · β ช่วง test ต่างจาก train < {R['beta_change_max_pct']}%",
        f"4 · half-life {R['hl_min_bars']}–{R['hl_max_bars']} แท่ง และไม่ยืดเกิน {R['hl_test_max_ratio']} เท่า",
        f"5 · c ที่เท่าทุน ≥ {R['breakeven_ratio_min']} เท่าของ c ที่ใช้",
        f"6 · Sharpe lag 2 ≥ {R['lag2_keep_min_pct']}% ของ lag 1",
        "ผ่านครบทั้ง 6 ข้อ",
    ]
    keys = [f"pass_{c}_pct" for c in CHECKS] + ["pass_all_pct"]
    gm, fm = mc["good"], mc["fake"]
    return V.heat_table(
        cid, labels, ["โลก good\nมีสายจูง", "โลก fake\nไม่มีสายจูง"], [[gm[k], fm[k]] for k in keys],
        "ตารางอัตราผ่านของชุดตรวจหกข้อ: โลกที่มีสายจูงผ่านเกือบทุกข้อ โลกที่ไม่มีสายจูงแทบไม่มีโลกไหนผ่านครบ",
        f"ข้อมูลจำลอง {D1_WORLDS} โลกต่อแบบ · ตัวเลข = % ของโลกที่ผ่านข้อนั้น (ปัดตามความแม่นของการจำลอง) · ข้อ 1–4 จับ "
        f"\"ไม่มีสายจูง\" ได้ดี ส่วนข้อ 5–6 คู่ fake ผ่านได้ราวครึ่งหนึ่งเพราะผลของมันคือการโยนเหรียญ (สองข้อนี้มีไว้จับต้นทุน"
        f"และ noise ของราคา) · ผ่านครบหกข้อ: โลก good ราว {_txt(gm['pass_all_pct'])}% · โลก fake {fm['pass_all_n']} ใน "
        f"{D1_WORLDS} โลก",
        scale="seq", fmt=lambda v: f"{V.num(v, 0 if float(v).is_integer() else _dec(v))}%", lo=0, hi=100, w=640)


def charts(res=None):
    """กราฟทุกรูปของตอนที่ 5 → {ชื่อ: html}  (สร้างจากผลการรันชุดเดียวกับ figures)"""
    res = res or run()
    f = figures(res)
    builders = {
        "sas-p5-corr-vs-coint": _chart_corr,
        "sas-p5-selection": _chart_selection,
        "sas-p5-lookahead": _chart_lookahead,
        "sas-p5-lag": _chart_lag,
        "sas-p5-cost-grid": _chart_cost_grid,
        "sas-p5-window": _chart_window,
        "sas-p5-micro": _chart_micro,
        "sas-p5-stops": _chart_stops,
        "sas-p5-killswitch": _chart_killswitch,
        "sas-p5-sample-size": _chart_sample_size,
        "sas-p5-battery": _chart_battery,
    }
    return {cid: build(cid, res, f) for cid, build in builders.items()}


# ───────────────────────── สรุปเมื่อรันตรง ๆ ─────────────────────────

def _print_summary(f):
    P = print
    d1, d2, d3, d4, d5, d6, d7, d8, d9, d10 = (f[k] for k in ("d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8",
                                                               "d9", "d10"))
    P("ห้องทดลองตอนที่ 5 — คลินิก backtest (ข้อมูลจำลองทั้งหมด)")
    P(f"ค่าตั้งต้น: {f['about']['common']}")
    P(f"การปัด: {f['about']['rounding']}")

    P(f"\nD1 · correlation ไม่ใช่สายจูง  ({d1['worlds']} โลกต่อกลุ่ม)")
    for k, name in (("good", "good (มีสายจูง)"), ("fake", "fake (ไม่มีสายจูง)"), ("fake_tight", "fake ที่ correlation สูง")):
        v = d1[k]
        P(f"  {name:<24} correlation {v['ret_corr_median']} · Sharpe เฉลี่ย {v['sharpe_mean']:+} "
          f"(5–95%: {v['sharpe_p5']:+} ถึง {v['sharpe_p95']:+}) · lag 2: {v['sharpe_lag2_mean']:+} · "
          f"กำไร {v['profitable_pct']}% ของโลก · z_sd {v['z_sd']}")

    P(f"\nD2 · คัดจาก {d2['n_pairs']} คู่ ({d2['n_fake']} fake + {d2['n_good']} good) ด้วย Engle-Granger บน {d2['select_bars']} แท่งแรก")
    for key, name in (("level5", "ระดับ 5%"), ("level1", "ระดับ 1%")):
        v = d2[key]
        P(f"  {name} (ค่าวิกฤต {v['cutoff']}): เลือกได้ {v['selected']} คู่ = จริง {v['tp']} + ปลอม {v['fp']} "
          f"(คาดหมาย {v['fp_expected']} · จักรวาลอื่น {v['fp_p5']}–{v['fp_p95']}) → ความแม่น {v['precision_pct']}% · "
          f"Sharpe ช่วงพิสูจน์: จริง {v['oos_sharpe_good']:+} ปลอม {v['oos_sharpe_fake']:+} รวม {v['oos_sharpe_all']:+}")
    P(f"  10 อันดับแรก (ค่ากลางของ {d2['universes']:,} จักรวาลที่สุ่มซ้ำ · ในวงเล็บ = ช่วง 5–95% ของช่วงพิสูจน์):")
    for key, name in (("top_backtest", "Sharpe ช่วงคัดเลือกสูงสุด"), ("top_eg", "ค่า EG ติดลบที่สุด"),
                      ("top_fake_only", "Sharpe สูงสุด (จักรวาล fake ล้วน)")):
        v = d2[key]
        P(f"    {name:<34} คู่จริงราว {v['n_good']} · Sharpe ช่วงคัดเลือก {v['sharpe_in']:+} → ช่วงพิสูจน์ "
          f"{v['sharpe_out']:+} ({v['sharpe_out_p5']:+} ถึง {v['sharpe_out_p95']:+}) · รอบจริง: {v['scan_sharpe_in']:+} → "
          f"{v['scan_sharpe_out']:+}")

    P(f"\nD3 · มองอนาคต: β, μ, σ จากทั้งช่วง เทียบ walk-forward  ({d3['worlds']} โลกต่อแบบ)")
    for k in ("good", "drift", "fake"):
        v = d3[k]
        P(f"  {k:<6} Sharpe มองอนาคต {v['sharpe_lookahead']:+} · walk-forward {v['sharpe_wf']:+} · ช่องว่าง "
          f"{v['gap']:+} · กำไร {v['profitable_lookahead_pct']}% เทียบ {v['profitable_wf_pct']}% ของโลก")
    mc, demo = d3["lag"]["mc"], d3["lag"]["demo"]
    P("  บั๊กเรียงแกนเวลา (คู่ good): " + " · ".join(
        f"lag {k}: Sharpe {mc[f'lag{k}']['sharpe']:+} ({mc[f'lag{k}']['ann_return_pct']:+}%/ปี)" for k in (0, 1, 2)))
    P("  คู่ตัวอย่าง good:           " + " · ".join(f"lag {k}: {demo[f'lag{k}']['sharpe']:+}" for k in (0, 1, 2)))
    P(f"  lag 0 เสียต่อไม้: ที่แท่งเข้า {mc['lag0_entry_bar_bps']:+} bps · ที่แท่งออก {mc['lag0_exit_bar_bps']:+} bps "
      f"(กำไรขั้นต้นต่อไม้ของ lag 1 ราว {mc['gross_per_trade_bps']:+} bps · ผลตอบแทนหายราว {mc['lag0_return_lost_pct']}%)")

    P(f"\nD4 · ต้นทุน: Sharpe เฉลี่ย (แถว = σ_eq · คอลัมน์ = c เป็น bps)  ({d4['worlds']} โลกต่อแถว)")
    cols = [_cost_key(c) for c in D4_COSTS]
    P("  σ_eq    " + "".join(f"{c[1:]:>7}" for c in cols) + "   กำไรขั้นต้น/ไม้ (bps): วัดได้ · สูตร · สูตร÷z_sd   c เท่าทุน (bps)")
    for sig in D4_SIGMAS:
        v = d4[_sigma_key(sig)]
        P(f"  {sig * 100:>4g}%   " + "".join(f"{v[c]['sharpe']:>+7}" for c in cols)
          + f"   {v['gross_per_trade_bps']:>8} · {v['formula_per_trade_bps']:>6} · {v['formula_converted_bps']:>6}"
          + f"   {v['breakeven_c_bps']:>8}")
    P(f"  z_sd เฉลี่ย {d4['z_sd']} → entry 2 ≈ {d4['entry_true_sigma']} σ จริง · สเปรดต้องกว้าง ≥ "
      f"{d4['measured_sigma_over_c']} เท่าของ c (สูตร: {d4['formula_sigma_over_c']} เท่า)")

    P(f"\nD5 · หน้าต่าง z-score: Sharpe เฉลี่ย  ({d5['worlds']} โลกต่อแบบ)")
    keys = [f"w{int(k * HL)}" for k in D5_MULTS] + ["fixed"]
    P("  หน้าต่าง (แท่ง)   " + "".join(f"{k.lstrip('w'):>8}" for k in keys))
    for name, label in (("good", "โลกปกติ      "), ("drifting", "ค่ากลางไหลช้า")):
        P(f"  {label}    " + "".join(f"{d5[name][k]['sharpe']:>+8}" for k in keys)
          + f"   ช่วงที่ดีพอ ๆ กัน {_plateau_txt(d5[name])}×")
    P(f"  เพดาน |z| เมื่อรวมแท่งปัจจุบัน: 6 แท่ง → {d5['bound']['w6']} · 12 แท่ง → {d5['bound']['w12']}")

    P(f"\nD6 · noise ของราคา 0.3% ต่อขา บนสเปรดจริง half-life 40  ({d6['worlds']} โลกต่อแบบ)")
    for w, label in (("tight", "σ_eq 1%"), ("wide", "σ_eq 3%")):
        v = d6[w]
        P(f"  {label}: half-life จากราคาที่เห็น {v['hl_print_bars']} แท่ง · จากราคาจริง {v['hl_true_bars']} แท่ง "
          f"(noise ของสเปรด = {v['noise_to_sigma_pct']}% ของ σ_eq)")
        for s, sl in (("wf", "walk-forward     "), ("short", "หน้าต่างสั้น 10 แท่ง")):
            r = v[s]
            P(f"    {sl} Sharpe: ราคาที่เห็น lag 0/1/2 = {r['print_lag0']['sharpe']:+} / "
              f"{r['print_lag1']['sharpe']:+} / {r['print_lag2']['sharpe']:+} · ราคาจริง lag 1 = "
              f"{r['true_lag1']['sharpe']:+} · ผลตอบแทน/ปี {r['print_lag1']['ann_return_pct']:+}% เทียบ "
              f"{r['true_lag1']['ann_return_pct']:+}%")

    P("\nD7 · stop  (Sharpe เฉลี่ย · อัตราชนะ · 5% แย่สุดของผลรวม)")
    for name in ("good", "break"):
        P(f"  โลก {name:<6}" + " · ".join(
            f"{'ไม่มี' if k == 'none' else 'z=' + k[4:].replace('_', '.')}: {d7[name][k]['sharpe']:+} "
            f"({d7[name][k]['hit_rate_pct']}% · {d7[name][k]['total_p5_pct']:+}%)"
            for k in ["none"] + [_stop_key(s) for s in reversed(D7_STOPS)]))

    P(f"\nD8 · สายจูงขาดที่แท่ง {d8['break_bar']}  ({d8['worlds']} โลก break · ราคาที่ต้องจ่ายวัดบนโลก good)")
    names = {"none": "ไม่มีสวิตช์", "time": "จำกัดเวลาถือ 60 แท่ง", "monitor_250": "EG 250 แท่ง",
             "monitor_500": "EG 500 แท่ง", "both": "EG 500 + จำกัดเวลา"}
    for v in D8_VARIANTS:
        b, g = d8["break"][v], d8["good"][v]
        P(f"  {names[v]:<22} หลังขาด: เฉลี่ย {b['after_mean_pct']:+}% · เปอร์เซ็นไทล์ 5 {b['after_p5_pct']:+}% · "
          f"เฉลี่ย 5% แย่สุด {b['after_worst5_mean_pct']:+}% · Sharpe ทั้งช่วง {b['sharpe']:+} | โลก good: Sharpe {g['sharpe']:+}")
    P(f"  สวิตช์ปิดเทรดบนโลก good: 250 แท่ง {d8['good']['blocked_250_pct']}% ของเวลา · 500 แท่ง "
      f"{d8['good']['blocked_500_pct']}% · ตรวจพบหลังขาด (ค่ากลาง): {d8['break']['delay_median_250_bars']} / "
      f"{d8['break']['delay_median_500_bars']} แท่ง")

    P(f"\nD9 · Sharpe ของ 1 ปี  ({d9['worlds']:,} โลกต่อแบบ)")
    for k, label in (("good", "good (half-life 12)"), ("slow", "slow (half-life 40)"), ("fake", "fake")):
        v = d9[k]
        P(f"  {label:<20} 5/50/95%: {v['sharpe_p5']:+} / {v['sharpe_p50']:+} / {v['sharpe_p95']:+} · "
          f"ติดลบ {v['negative_pct']}% · เกิน 1: {v['above1_pct']}% · เฉลี่ย {v['trades_mean']} ไม้")
    v = d9["five_year"]["fake"]
    P(f"  fake เมื่อดูราว 5 ปี: เกิน 1 เหลือ {v['above1_pct']}% (5–95%: {v['sharpe_p5']:+} ถึง {v['sharpe_p95']:+})")

    P("\nD10 · ชุดตรวจตัวเอง 6 ข้อ บนคู่ตัวอย่าง")
    P("  " + f["outputs"]["battery"].replace("\n", "\n  "))
    for k in ("good", "fake"):
        v = d10["mc"][k]
        P(f"  อัตราผ่านบนโลก {k} {d10['mc']['worlds']} โลก: " + " · ".join(
            f"ข้อ {i + 1}: {v[f'pass_{c}_pct']}%" for i, c in enumerate(CHECKS))
          + f" · ครบ 6 ข้อ: {v['pass_all_pct']}% ({v['pass_all_n']} โลก)")

    P("\nตารางคลินิก (ทำผิด → ทำถูก)")
    for k, r in f["clinic"].items():
        P(f"  {k:<7} {r['name']}: {r['wrong']:+} → {r['right']:+}  [{r['unit']}]")


if __name__ == "__main__":
    _print_summary(figures())
