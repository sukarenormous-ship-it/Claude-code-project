#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ห้องทดลองของตอนที่ 2 — "นิ่งหรือไม่นิ่ง: ใบอนุญาตของทั้งวิชา" (สไลด์ 3)

ทุกอย่างในไฟล์นี้เป็น "ข้อมูลจำลอง" ที่เราสร้างเองและรู้เฉลย: รู้ว่าเส้นไหนมีแรงดึงกลับ (φ < 1)
และเส้นไหนไม่มี (φ = 1) จึงวัดได้ตรง ๆ ว่าเครื่องมือแต่ละตัวตอบถูกบ่อยแค่ไหน
ตอนนี้ไม่มีการเทรดและไม่มีต้นทุน — เป็นเรื่องของ "อนุกรมเส้นเดียว" ล้วน ๆ

แบบจำลองเดียวที่ใช้ทั้งไฟล์:  x_t = φ·x_{t−1} + e_t
    φ = 1  random walk (ไม่มีแรงดึงกลับ)      φ < 1  AR(1) ดึงกลับ · half-life = −ln2 / ln φ
    φ = 0  noise ล้วน (กลับถึงค่าเฉลี่ยในแท่งเดียว)

การทดลอง
  2a  slide3     จำลองรูปของสไลด์ 3 (200 แท่ง): random walk กับ noise ที่นิ่ง — สองเส้นนี้ใช้ตัวเลขสุ่ม
                 ชุดเดียวกัน (เส้นไม่นิ่ง = ผลบวกสะสมของเส้นนิ่ง) · ค่าเฉลี่ยและ sd ของครึ่งแรกเทียบครึ่งหลัง
  2h  eye        การตรวจด้วยตาสามข้อ วัดเป็นตัวเลขบนสองเส้นของ 2a: (1) ค่าเฉลี่ยสองครึ่งห่างกันกี่ sd
                 (2) ข้ามค่าเฉลี่ยกี่ครั้ง (3) ช่วงสูง–ต่ำของ 50 แท่งแรกเทียบกับทั้ง 200 แท่ง
                 + Monte Carlo 10,000 โลก (random walk · AR(1) half-life 10 · noise) — ข้อสุดท้ายนี้สำคัญ:
                 AR(1) ที่นิ่งจริงแต่ดึงกลับช้าดูไม่ "นิ่ง" ด้วยตาได้ง่าย การตรวจด้วยตาจึงเป็นแค่ด่านกรอง
  2b  halves     "ฮิสโทแกรมโกหก" (500 แท่ง · 10,000 โลก): |ค่าเฉลี่ยครึ่งแรก − ครึ่งหลัง| ÷ sd รวม
                 ของ random walk · AR(1) half-life 40 · AR(1) half-life 10 · noise
  2c  vargrowth  sd ของการเปลี่ยนแปลงใน h แท่ง (h = 1 … 250): random walk โตตาม √h ไม่มีเพดาน
                 ส่วน AR(1) half-life 10 ชนเพดาน σ·√2 · ตัวเลขหลักมาจากสูตร (แบบจำลองรู้แน่นอน)
                 และตรวจด้วยการจำลอง 20,000 โลก (จุดในกราฟ)
  hand adf_hand  ADF "คิดมือ" บน 250 แท่ง: ถดถอย Δx_t บน x_{t−1} → ความชัน, standard error, ค่า t
                 สองเส้นจากตัวเลขสุ่มชุดเดียวกัน ต่างกันที่ φ ตัวเดียว (0.933 กับ 1)
  2d  adf_null   การแจกแจงของค่า t ของ ADF เมื่อความจริงคือ random walk (500 แท่ง · 400,000 เส้น):
                 เส้นตัด 1/5/10% · ค่ากลาง · P(t < −1.645), P(t < −2) = ความผิดพลาดถ้าเปิดตาราง normal
  2e  power      ADF จับแรงดึงกลับที่มีจริงได้บ่อยแค่ไหน: half-life {5,10,20,40,80} × n {125,250,500,1000}
                 ช่องละ 2,000 โลก + กวาดละเอียดตามอัตราส่วน n ÷ half-life → กฎหัวแม่มือ "ต้องมีข้อมูลกี่เท่า"
  2f  spurious   regression ลวง: random walk อิสระ 20,000 คู่ (500 แท่ง) — correlation ของระดับ, ค่า t
                 ของความชัน เทียบกับ correlation ของการเปลี่ยนแปลงรายวัน · และสองแบบของคู่ที่ correlation
                 ของผลตอบแทนเท่ากัน แต่แบบหนึ่งมีสายจูง อีกแบบไม่มี (แบบละ 2,000 โลก)
  2g  hl_bias    half-life ที่ประมาณได้สั้นกว่าจริงเมื่อข้อมูลน้อย (ของจริง 12 แท่ง · n = 125 … 1000 · 10,000 โลก)
                 และ random walk ที่ "ได้ half-life เป็นตัวเลข" ทั้งที่ไม่มีแรงดึงกลับ

วิธีรัน
    python3 tools/sas_exp2.py          พิมพ์สรุปตัวเลขสำคัญ (ราว 40 วินาที — ส่วนใหญ่คือการจำลองเส้นตัด)

หมายเหตุสำหรับคนอ่านโค้ด
  • ADF ของห้องทดลองใช้ lags = 1 มีค่าคงที่ (C.adf_stat) · เส้นตัดทุกตัวมาจากการจำลอง random walk
    อย่างน้อย 100,000 เส้นที่ "ความยาวและ lags เดียวกับตัวสถิติ" (ฟังก์ชัน adf_null) — ไม่เปิดตารางสำเร็จรูป
  • ตัวอย่างคิดมือใช้ lags = 0 (สมการสั้นที่สุด) จึงเทียบกับเส้นตัดของ lags = 0 แยกต่างหาก
  • โลกตัวอย่างของ 2a และของตัวอย่างคิดมือ = โลกที่สถิติหลักทุกตัว "ใกล้ค่ากลางของทุกโลกที่สุด"
    (ฟังก์ชัน typical_world) — ไม่ใช่โลกที่สวยที่สุด · คู่ตัวอย่างของ 2f คือคู่ที่ |correlation| อยู่ที่
    เปอร์เซ็นไทล์ 75 พอดี (หนึ่งในสี่ของคู่ทั้งหมดดูเกี่ยวกันยิ่งกว่านั้น)
  • การปัดเลข: หลักสุดท้ายที่พิมพ์ต้องไม่เปลี่ยนเมื่อเปลี่ยน seed — สัดส่วนจาก Monte Carlo จึงเป็นเปอร์เซ็นต์เต็ม
    (ตาราง power คลาดได้ราว ±2 จุด) และเส้นตัดสองตำแหน่งคลาดได้ราว ±0.01

คีย์ของ figures()  (ทุกค่าปัดแล้ว · _pct = เปอร์เซ็นต์ · _bars = จำนวนแท่ง · _sigma = หน่วย sd ·
                   _med/_p5/_p95 = ค่ากลางและช่วง 5–95% ของ Monte Carlo)
    about.*                  คำอธิบายสั้นของแต่ละการทดลองและค่าที่ตั้งไว้ (about.precision = ความแม่นของการปัด)
    slide3.rw / .noise       mean_h1, mean_h2, sd_h1, sd_h2, mean_all, sd_all, min, max, adf, adf_verdict
    eye.rw / .noise          gap_sigma, crossings, range_first, range_all, range_ratio_pct (โลกตัวอย่าง)
    eye.mc.<rw|ar1|noise>    gap_*_sigma, gap_gt1_pct, crossings_*, range_ratio_*_pct, adf_pass_pct
    halves.<rw|ar1_slow|ar1|noise>   gap_*_sigma, gap_gt1_pct, sd_ratio_med
    vargrowth.*              step_sd_pct, ceiling_pct, sim_within_pct ·
                             vargrowth.h<h>: rw_theory_pct, ar1_theory_pct, rw_times (= √h), ar1_times
    adf_hand.st / .rw        n_reg, sxx, sqrt_sxx, sxy, slope, intercept, resid_sd, se, t, phi_hat, pull_pct,
                             half_life_bars, verdict, adf_lags1, verdict_lags1 · adf_hand.mc.*
    adf_null.*               crit1, crit5, crit10, median, p_lt_1645_pct, p_lt_2_pct, p_lt_0_pct, crit5_by_n.*
    power.hl<HL>.n<n>_pct    ตาราง power · power.crit5.n<n> · power.fine.n<n>.r<ratio>_pct ·
                             power.rule.* (อัตราส่วน n ÷ half-life ที่ได้ power 80% — ค่าประมาณ ·
                             k_round5 = กฎที่ปัดแล้ว · n_for_demo_hl_bars = k_round5 × 12)
    spurious.*               corr_levels_abs_*, corr_gt05_pct, t_gt2_pct, t_abs_med, corr_changes_abs_*,
                             t_changes_gt2_pct, chance_t_gt2_pct · spurious.example.* ·
                             spurious.same_corr.fake / .leash
    hl_bias.n<n>.*           hl_med_bars, hl_p5_bars, hl_p95_bars, short_pct, phi_med · hl_bias.rw.*

ชื่อกราฟ: sas-p2-slide3 · sas-p2-eye-tests · sas-p2-halves · sas-p2-variance-growth ·
          sas-p2-adf-by-hand · sas-p2-adf-null · sas-p2-power · sas-p2-power-ratio ·
          sas-p2-spurious · sas-p2-spurious-example · sas-p2-halflife-bias
"""
import functools
import inspect
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sas_core as C  # noqa: E402
import sas_svg as V  # noqa: E402

# ─────────────────────────────── ค่าที่ตั้งไว้ ───────────────────────────────
LAGS = 1                                   # ADF ของห้องทดลอง: lags 1 ตายตัว
# จำนวนโลก: ตัวเลขที่พิมพ์ต้องนิ่งพอที่หลักสุดท้ายไม่เปลี่ยนเมื่อเปลี่ยน seed — การทดลองที่ถูก (ไม่มี ADF
# ทีละหลายพันเส้นยาว ๆ) จึงใช้ 10,000 โลก ส่วน 2e (ตาราง power) กับคู่ correlation เท่ากันใช้ 2,000 ตามสเปก
WORLDS = 2000                              # 2e power (ช่องละ) · 2f คู่ correlation เท่ากัน
WORLDS_BIG = 10_000                        # 2a/2h · 2b · ADF คิดมือ · 2g
VG_WORLDS, VG_CHUNK = 20_000, 2_000        # 2c จุดที่วัดจากการจำลอง (คิดทีละก้อน ประหยัดหน่วยความจำ)
N_SIM_NULL = 100_000                       # random walk ที่ใช้หาเส้นตัด (เลขที่พิมพ์ลงบทต้อง ≥ 100,000)
N_SIM_HEAD = 400_000                       # 2d: ตารางเส้นตัดหลักของบท (500 แท่ง) — ให้หลักที่สองของเส้นตัดคลาดไม่เกินราว ±0.01
NULL_CHUNK = 10_000                        # จำลองทีละก้อน จะได้ไม่กินหน่วยความจำ (ผลเท่ากับจำลองรวดเดียว)

HL_FAST, HL_SLOW = 10.0, 40.0              # half-life ของ AR(1) "ดึงเร็ว" และ "ดึงช้า"
PHI_FAST = C.phi_from_half_life(HL_FAST)

SLIDE_N, EYE_FIRST = 200, 50               # 2a / 2h
HALVES_N = 500                             # 2b
VG_N, VG_SIGMA = 500, 0.03                 # 2c: AR(1) σ ระยะยาว 3% (ขนาดเดียวกับสเปรดของคู่ตัวอย่าง)
HORIZONS = (1, 5, 20, 60, 120, 250)
# จุดที่ใช้วาดเส้นในกราฟ (แกน h เป็นสเกลจริง จะได้เห็นรูปทรง √h ตามจริง) — มี HORIZONS อยู่ในนี้ทุกตัว
VG_CURVE_H = tuple(sorted(set(range(1, 21)) | set(range(25, 251, 5)) | set(HORIZONS)))
HAND_N = 250                               # ตัวอย่างคิดมือ
NULL_N = 500                               # 2d
POWER_HL = (5, 10, 20, 40, 80)             # 2e
POWER_N = (125, 250, 500, 1000)
POWER_TARGET = 0.80
FINE_N = (250, 500, 1000)                  # 2e กวาดละเอียด: half-life = n ÷ อัตราส่วน
FINE_RATIOS = (10, 15, 20, 25, 30, 35, 40, 50, 60)
SPUR_PAIRS, SPUR_N, SPUR_PCTILE = 20_000, 500, 75  # 2f (สเปกขั้นต่ำ 5,000 คู่ — ใช้มากกว่าเพื่อให้ % นิ่ง)
SPUR_CHUNK = 5_000
HLB_TRUE = 12.0                            # 2g
HLB_N = (125, 250, 500, 1000)
HLB_RW_N = 500

# seed: offset 200–299 เป็นของตอนที่ 2
OFF_SLIDE, OFF_HALVES, OFF_VG, OFF_HAND = 200, 210, 215, 220
OFF_NULL = {(125, 1): 230, (200, 1): 231, (250, 1): 232, (250, 0): 233, (500, 1): 234, (1000, 1): 235}
OFF_POWER, OFF_FINE = 240, 241
OFF_SPUR, OFF_SAME_CORR = 250, 251
OFF_HLB, OFF_HLB_RW = 260, 261

EYE_KEYS = ("gap", "crossings", "range_ratio")


# ─────────────────────────────── เครื่องมือเล็ก ๆ ───────────────────────────────
def adf_null(n_obs, lags=LAGS):
    """ค่า ADF ของ random walk แท้ ๆ (เรียงจากน้อยไปมาก) — ไม้บรรทัดของ "ไม่มีแรงดึงกลับ"
    ต้องใช้ n_obs และ lags ชุดเดียวกับตัวสถิติที่จะเอามาเทียบเสมอ"""
    return _adf_null(int(n_obs), int(lags))      # ส่งต่อแบบระบุครบ: adf_null(500) กับ adf_null(500, 1) ใช้ cache เดียวกัน


@functools.lru_cache(maxsize=None)
def _adf_null(n_obs, lags):
    g = C.rng(OFF_NULL[(n_obs, lags)])
    parts = [C.mc_null_adf(n_obs, n_sim=NULL_CHUNK, lags=lags, g=g) for _ in range(null_sims(n_obs, lags) // NULL_CHUNK)]
    return np.sort(np.concatenate(parts))


def null_sims(n_obs, lags=LAGS):
    """จำนวน random walk ที่ใช้หาเส้นตัดของ (n_obs, lags) นี้"""
    return N_SIM_HEAD if (n_obs, lags) == (NULL_N, LAGS) else N_SIM_NULL


def crit5(n_obs, lags=LAGS):
    return C.crit_values(adf_null(n_obs, lags))[0.05]


def verdict(adf, crit):
    """ผ่าน = ปฏิเสธ random walk ที่ระดับ 5% (ค่า ADF ติดลบกว่าเส้นตัด)"""
    return "ผ่าน" if adf < crit else "ไม่ผ่าน"


def from_shocks(e, phi):
    """x_t = φ·x_{t−1} + e_t จากตัวเลขสุ่มชุด e (โลก × เวลา) — เปลี่ยน φ ตัวเดียว ตัวเลขสุ่มไม่เปลี่ยน
    φ = 1 → random walk (ผลบวกสะสมของ e) · φ = 0 → e เอง · 0 < φ < 1 → AR(1) ที่เริ่มจากการแจกแจงนิ่ง
    ของตัวเอง (แบบเดียวกับ C.ar1 — ต่างกันแค่รับตัวเลขสุ่มจากข้างนอก)"""
    e = np.asarray(e, float)
    if phi >= 1.0:
        return np.cumsum(e, axis=1)
    x = np.empty_like(e)
    x[:, 0] = e[:, 0] / math.sqrt(1.0 - phi * phi)
    for t in range(1, e.shape[1]):
        x[:, t] = phi * x[:, t - 1] + e[:, t]
    return x


def half_gap(x):
    """ตรวจด้วยตาข้อ 1: |ค่าเฉลี่ยครึ่งแรก − ครึ่งหลัง| ÷ sd รวมของสองครึ่ง (ทีละแถว)"""
    h = x.shape[1] // 2
    a, b = x[:, :h], x[:, h:2 * h]
    pooled = np.sqrt((a.var(axis=1, ddof=1) + b.var(axis=1, ddof=1)) / 2.0)
    return np.abs(a.mean(axis=1) - b.mean(axis=1)) / pooled


def half_sd_ratio(x):
    """sd ของครึ่งที่กว้างกว่า ÷ sd ของครึ่งที่แคบกว่า (1 = กว้างเท่ากัน)"""
    h = x.shape[1] // 2
    a, b = x[:, :h].std(axis=1, ddof=1), x[:, h:2 * h].std(axis=1, ddof=1)
    return np.maximum(a, b) / np.minimum(a, b)


def mean_crossings(x):
    """ตรวจด้วยตาข้อ 2: จำนวนครั้งที่เส้นข้ามค่าเฉลี่ยของตัวเอง"""
    d = x - x.mean(axis=1, keepdims=True)
    return np.sum(np.diff(np.sign(d), axis=1) != 0, axis=1)


def range_ratio(x, first=EYE_FIRST):
    """ตรวจด้วยตาข้อ 3: ช่วงสูง–ต่ำของ `first` แท่งแรก ÷ ช่วงสูง–ต่ำของทั้งเส้น"""
    return np.ptp(x[:, :first], axis=1) / np.ptp(x, axis=1)


def eye_stats(x):
    return {"gap": half_gap(x), "crossings": mean_crossings(x), "range_ratio": range_ratio(x)}


def typical_world(*stats):
    """index ของโลกที่สถิติ "ทุกตัว" อยู่ใกล้ค่ากลางของทุกโลกที่สุด — วัดจากตัวที่ห่างกึ่งกลางที่สุด
    (ระยะห่างเชิงอันดับ: 0 = อยู่ที่ค่ากลางพอดี · 0.5 = สุดขอบ)
    ใช้เลือกโลกตัวอย่างแบบไม่ลำเอียง: ไม่ใช่โลกที่อาการหนักสุด และไม่ใช่โลกที่บังเอิญดูดี"""
    worst = np.zeros(len(stats[0]))
    for s in stats:
        rank = np.argsort(np.argsort(s, kind="stable"), kind="stable") / (len(s) - 1.0)
        worst = np.maximum(worst, np.abs(rank - 0.5))
    return int(np.argmin(worst))


def row_corr(a, b):
    """correlation ทีละแถวของอาร์เรย์ (โลก × เวลา)"""
    a = a - a.mean(axis=1, keepdims=True)
    b = b - b.mean(axis=1, keepdims=True)
    return (a * b).sum(axis=1) / np.sqrt((a * a).sum(axis=1) * (b * b).sum(axis=1))


def corr_to_t(r, n):
    """ค่า t ของความชันใน regression ตัวแปรเดียว (มีค่าคงที่) คิดจาก correlation ตรง ๆ:
    t = r·√((n−2)/(1−r²)) — เท่ากับที่ C.ols ให้ทุกประการ แต่คิดได้ทีละหลายพันคู่"""
    return r * np.sqrt((n - 2.0) / (1.0 - r * r))


def reject_rate(x, crit):
    """สัดส่วนของแถวที่ ADF ปฏิเสธ random walk (ค่า t ต่ำกว่าเส้นตัด)"""
    return float(np.mean(C.adf_stat_batch(x, lags=LAGS) < crit))


def ratio_at(ratios, power, target=POWER_TARGET):
    """อัตราส่วนที่ power แตะเป้า — ลากเส้นตรงระหว่างสองจุดที่คร่อมเป้า (เป็นค่าประมาณ ไม่ใช่ค่าที่วัดตรง ๆ)"""
    for i in range(1, len(ratios)):
        if power[i - 1] < target <= power[i]:
            w = (target - power[i - 1]) / (power[i] - power[i - 1])
            return ratios[i - 1] + w * (ratios[i] - ratios[i - 1])
    return math.nan


# ─────────────────────────────── 2a + 2h: สไลด์ 3 และการตรวจด้วยตา ───────────────────────────────
def series_summary(x, crit):
    """ตัวเลขของเส้นตัวอย่างหนึ่งเส้น: ครึ่งแรก/ครึ่งหลัง · การตรวจด้วยตาสามข้อ · ADF"""
    h = len(x) // 2
    row = x[None, :]
    return {"x": x, "mean_h1": x[:h].mean(), "mean_h2": x[h:].mean(),
            "sd_h1": x[:h].std(ddof=1), "sd_h2": x[h:].std(ddof=1),
            "mean_all": x.mean(), "sd_all": x.std(ddof=1), "min": x.min(), "max": x.max(),
            "gap": half_gap(row)[0], "crossings": int(mean_crossings(row)[0]),
            "min_first": x[:EYE_FIRST].min(), "max_first": x[:EYE_FIRST].max(),
            "range_first": np.ptp(x[:EYE_FIRST]), "range_all": np.ptp(x), "range_ratio": range_ratio(row)[0],
            "adf": C.adf_stat(x, lags=LAGS), "crit5": crit}


def exp_slide3():
    """2a + 2h — สามเส้นจากตัวเลขสุ่มชุดเดียวกัน (φ = 1, φ ของ half-life 10, φ = 0) × 2,000 โลก"""
    e = C.rng(OFF_SLIDE).standard_normal((WORLDS_BIG, SLIDE_N))
    fam = {"rw": from_shocks(e, 1.0), "ar1": from_shocks(e, PHI_FAST), "noise": from_shocks(e, 0.0)}
    crit = crit5(SLIDE_N)
    mc = {k: dict(eye_stats(x), adf_pass=reject_rate(x, crit)) for k, x in fam.items()}
    k = typical_world(*[mc[s][name] for s in ("rw", "noise") for name in EYE_KEYS])
    return {"world": k, "crit5": crit, "mc": mc, "t": np.arange(SLIDE_N),
            "demo": {s: series_summary(fam[s][k], crit) for s in ("rw", "noise")}}


# ─────────────────────────────── 2b: ค่าเฉลี่ยสองครึ่ง ───────────────────────────────
def exp_halves():
    g = C.rng(OFF_HALVES)
    fam = {"rw": np.cumsum(g.standard_normal((WORLDS_BIG, HALVES_N)), axis=1),
           "ar1_slow": C.ar1_batch(WORLDS_BIG, HALVES_N, HL_SLOW, 1.0, g),
           "ar1": C.ar1_batch(WORLDS_BIG, HALVES_N, HL_FAST, 1.0, g),
           "noise": g.standard_normal((WORLDS_BIG, HALVES_N))}
    return {k: {"gap": half_gap(x), "sd_ratio": half_sd_ratio(x)} for k, x in fam.items()}


# ─────────────────────────────── 2c: sd โตตามเวลาหรือไม่ ───────────────────────────────
def exp_vargrowth():
    """random walk กับ AR(1) ที่ "ขยับต่อวันเท่ากัน" — ต่างกันที่ขยับแล้วสะสมหรือถูกดึงกลับ"""
    g = C.rng(OFF_VG)
    step = VG_SIGMA * math.sqrt(2.0 * (1.0 - PHI_FAST))          # sd ของการเปลี่ยนแปลงหนึ่งแท่งของ AR(1)

    def rw_sd(h):                                                # สูตร: ขยับอิสระ h ครั้ง → sd โตตาม √h
        return step * math.sqrt(h)

    def ar1_sd(h):                                               # สูตร: Var(x_{t+h} − x_t) = 2σ²(1 − φ^h)
        return VG_SIGMA * math.sqrt(2.0 * (1.0 - PHI_FAST ** h))

    # วัดจริงจากการจำลอง: ผลรวมกำลังสองของการเปลี่ยนแปลง h แท่ง (ทุกโลก ทุกจุดเริ่ม) สะสมทีละก้อน
    # (ค่าเฉลี่ยจริงของการเปลี่ยนแปลงเป็น 0 ทั้งสองแบบ จึงใช้ √(ค่าเฉลี่ยของกำลังสอง) เป็น sd)
    ss = {k: np.zeros(len(HORIZONS)) for k in ("rw", "ar1")}
    cnt = np.zeros(len(HORIZONS))
    for _ in range(VG_WORLDS // VG_CHUNK):
        paths = {"rw": np.cumsum(step * g.standard_normal((VG_CHUNK, VG_N)), axis=1),
                 "ar1": C.ar1_batch(VG_CHUNK, VG_N, HL_FAST, VG_SIGMA, g)}
        for i, h in enumerate(HORIZONS):
            for k, x in paths.items():
                ss[k][i] += float(np.sum((x[:, h:] - x[:, :-h]) ** 2))
            cnt[i] += VG_CHUNK * (VG_N - h)
    sim = {k: np.sqrt(v / cnt) for k, v in ss.items()}
    theory = {"rw": np.array([rw_sd(h) for h in HORIZONS]), "ar1": np.array([ar1_sd(h) for h in HORIZONS])}
    dev = max(float(np.max(np.abs(sim[k] / theory[k] - 1.0))) for k in sim)
    return {"step": step, "ceiling": VG_SIGMA * math.sqrt(2.0), "rw": sim["rw"], "ar1": sim["ar1"],
            "rw_theory": theory["rw"], "ar1_theory": theory["ar1"], "max_dev": dev,
            "curve": {"rw": [rw_sd(h) for h in VG_CURVE_H], "ar1": [ar1_sd(h) for h in VG_CURVE_H]}}


# ─────────────────────────────── ADF คิดมือ ───────────────────────────────
def by_hand(x):
    """ADF แบบสั้นที่สุด (lags 0) คิดทีละขั้นเหมือนทำในสเปรดชีต: Δx_t = a + γ·x_{t−1} + e_t
    γ = Sxy/Sxx · se = s/√Sxx · t = γ/se   (γ = φ − 1 จึงติดลบเมื่อมีแรงดึงกลับ)"""
    lag, d = x[:-1], np.diff(x)
    sxx = float(np.sum((lag - lag.mean()) ** 2))
    sxy = float(np.sum((lag - lag.mean()) * (d - d.mean())))
    slope = sxy / sxx
    icpt = float(d.mean() - slope * lag.mean())
    resid = d - icpt - slope * lag
    s = math.sqrt(float(resid @ resid) / (len(d) - 2))
    se = s / math.sqrt(sxx)
    out = {"x": x, "lag": lag, "d": d, "n_reg": len(d), "sxx": sxx, "sxy": sxy, "slope": slope,
           "intercept": icpt, "resid_sd": s, "se": se, "t": slope / se, "phi_hat": 1.0 + slope,
           "half_life": C.half_life_from_phi(1.0 + slope), "adf_lags1": C.adf_stat(x, lags=1)}
    assert abs(out["t"] - C.adf_stat(x, lags=0)) < 1e-8, "คิดมือต้องได้เท่ากับ C.adf_stat(lags=0)"
    # ค่าเฉลี่ยของ Δx ในห้าช่วงของระดับเมื่อวาน (ช่วงละหนึ่งในห้าของข้อมูล) — ไว้วาดรูป
    order = np.argsort(lag, kind="stable")
    groups = np.array_split(order, 5)
    out["bin_x"] = np.array([lag[i].mean() for i in groups])
    out["bin_d"] = np.array([d[i].mean() for i in groups])
    return out


def exp_hand():
    e = C.rng(OFF_HAND).standard_normal((WORLDS_BIG, HAND_N))
    st, rw = from_shocks(e, PHI_FAST), from_shocks(e, 1.0)
    t_st, t_rw = C.adf_stat_batch(st, lags=0), C.adf_stat_batch(rw, lags=0)
    # โลกตัวอย่าง = ค่า t ทั้งแบบคิดมือ (lags 0) และแบบที่ห้องทดลองใช้ (lags 1) ของทั้งสองเส้นอยู่ใกล้ค่ากลาง
    # (กันไม่ให้ตัวอย่างไปตกในโลกที่สองแบบตัดสินไม่ตรงกัน ซึ่งไม่ใช่ภาพปกติ)
    k = typical_world(t_st, t_rw, C.adf_stat_batch(st, lags=LAGS), C.adf_stat_batch(rw, lags=LAGS))
    c0, c1 = crit5(HAND_N, 0), crit5(HAND_N, 1)
    # สัดส่วน random walk ที่ได้ความชันติดลบ = P(t < 0) ของการแจกแจงใต้ null (lags 0 · 250 แท่ง) —
    # คิดจาก null 100,000 เส้นซึ่งแม่นกว่าโลกชุดตัวอย่าง (ความชันกับค่า t มีเครื่องหมายเดียวกันเสมอ)
    neg = float(np.mean(adf_null(HAND_N, 0) < 0.0))
    return {"world": k, "crit5_lags0": c0, "crit5_lags1": c1, "st": by_hand(st[k]), "rw": by_hand(rw[k]),
            "mc": {"t_st": t_st, "t_rw": t_rw, "pass_st": float(np.mean(t_st < c0)),
                   "pass_rw": float(np.mean(t_rw < c0)), "neg_slope_rw": neg}}


# ─────────────────────────────── 2d: ADF เมื่อความจริงคือ random walk ───────────────────────────────
def exp_null():
    null = adf_null(NULL_N)
    return {"null": null, "crit": C.crit_values(null), "median": float(np.median(null)),
            "mean": float(np.mean(null)), "p_lt_1645": float(np.mean(null < -1.645)),
            "p_lt_2": float(np.mean(null < -2.0)), "p_lt_0": float(np.mean(null < 0.0)),
            "crit5_by_n": {n: crit5(n) for n in (125, 200, 250, 500, 1000)}}


# ─────────────────────────────── 2e: power ───────────────────────────────
def grid_rule(grid):
    """อัตราส่วน n ÷ half-life ที่เล็กที่สุด "ในตาราง" ซึ่งทุกช่องตั้งแต่อัตราส่วนนั้นขึ้นไปได้ power ≥ 80%
    และอัตราส่วนก่อนหน้า (ที่ยังไม่ถึง) — แล้วลากเส้นตรงระหว่างค่าเฉลี่ยของสองอัตราส่วนนั้น"""
    cells = {}
    for i, hl in enumerate(POWER_HL):
        for j, n in enumerate(POWER_N):
            cells.setdefault(n / hl, []).append(grid[i, j])
    ratios = sorted(cells)
    ok = [min(cells[r]) >= POWER_TARGET for r in ratios]
    i = next(k for k in range(len(ratios)) if all(ok[k:]))
    lo, hi = ratios[i - 1], ratios[i]
    interp = ratio_at([lo, hi], [float(np.mean(cells[lo])), float(np.mean(cells[hi]))])
    return {"reach": hi, "reach_min": min(cells[hi]), "below": lo, "below_min": min(cells[lo]),
            "below_max": max(cells[lo]), "interp": interp}


def exp_power():
    crit = {n: crit5(n) for n in POWER_N}
    g = C.rng(OFF_POWER)
    grid = np.array([[reject_rate(C.ar1_batch(WORLDS, n, hl, 1.0, g), crit[n]) for n in POWER_N]
                     for hl in POWER_HL])
    g = C.rng(OFF_FINE)
    fine = np.array([[reject_rate(C.ar1_batch(WORLDS, n, n / r, 1.0, g), crit[n]) for r in FINE_RATIOS]
                     for n in FINE_N])
    pooled = fine.mean(axis=0)
    return {"crit": crit, "grid": grid, "rule": grid_rule(grid), "fine": fine, "fine_pooled": pooled,
            "fine_interp": ratio_at(FINE_RATIOS, pooled),
            "fine_interp_n": {n: ratio_at(FINE_RATIOS, fine[i]) for i, n in enumerate(FINE_N)}}


# ─────────────────────────────── 2f: regression ลวง ───────────────────────────────
def same_corr_pairs():
    """สองแบบของคู่ที่ correlation ของผลตอบแทนรายวัน "เท่ากันโดยตั้งใจ":
    fake = ไม่มีสายจูง (C.make_pair "fake") · leash = มีสายจูง (C.make_pair "good" ที่ปรับ σ ของ ε ให้
    correlation ของผลตอบแทนเท่ากับแบบ fake) — ทดสอบ ADF บน "สเปรดจริง" ที่รู้เฉลย (ไม่ต้องประมาณ β)"""
    dflt = {k: p.default for k, p in inspect.signature(C.make_pair).parameters.items()}
    hl = dflt["half_life"]
    # fake: Δy = m + i_y, Δx = m + i_x → corr = σ_m² / (σ_m² + σ_i²)
    target = dflt["sigma_m"] ** 2 / (dflt["sigma_m"] ** 2 + dflt["sigma_idio"] ** 2)
    # good: Δy = β·Δx + Δε → corr = β·σ_x / √(β²σ_x² + Var(Δε)) โดย Var(Δε) = 2(1−φ)·σ_ε² → แก้หา σ_ε
    phi = C.phi_from_half_life(hl)
    sigma_eq = (dflt["beta"] * dflt["sigma_x"] * math.sqrt(1.0 / target ** 2 - 1.0)
                / math.sqrt(2.0 * (1.0 - phi)))
    g = C.rng(OFF_SAME_CORR)
    crit = crit5(SPUR_N)
    out = {"target": target, "sigma_eq": sigma_eq, "half_life": hl}
    for kind, name in (("fake", "fake"), ("good", "leash")):
        ret_corr, spreads = [], []
        for _ in range(WORLDS):
            d = C.make_pair(kind, SPUR_N, g, sigma_eq=sigma_eq, half_life=hl)
            ret_corr.append(np.corrcoef(np.diff(d["y"]), np.diff(d["x"]))[0, 1])
            spreads.append(d["y"] - d["x"] if kind == "fake" else d["eps"])
        out[name] = {"ret_corr": np.array(ret_corr), "adf_pass": reject_rate(np.array(spreads), crit)}
    return out


def spurious_chunks():
    """คู่ random walk อิสระทีละก้อน (ลำดับตัวเลขสุ่มตายตัว เรียกซ้ำได้ผลเดิม)"""
    g = C.rng(OFF_SPUR)
    for _ in range(SPUR_PAIRS // SPUR_CHUNK):
        y = np.cumsum(g.standard_normal((SPUR_CHUNK, SPUR_N)), axis=1)
        x = np.cumsum(g.standard_normal((SPUR_CHUNK, SPUR_N)), axis=1)
        yield y, x


def exp_spurious():
    cl, cc = [], []
    for y, x in spurious_chunks():
        cl.append(row_corr(y, x))
        cc.append(row_corr(np.diff(y, axis=1), np.diff(x, axis=1)))
    cl, cc = np.concatenate(cl), np.concatenate(cc)
    tl, tc = corr_to_t(cl, SPUR_N), corr_to_t(cc, SPUR_N - 1)
    # คู่ตัวอย่าง: |correlation| อยู่ที่เปอร์เซ็นไทล์ 75 พอดี · เลือกจากคู่ที่ correlation เป็นบวก (เครื่องหมายสุ่มได้
    # ทั้งสองทางเท่า ๆ กัน คู่ที่เป็นบวกแค่ดูง่ายกว่าว่า "เดินไปด้วยกัน" — ไม่ได้ทำให้ตัวอย่างแรงขึ้น)
    gap = np.abs(cl - np.percentile(np.abs(cl), SPUR_PCTILE))
    k = int(np.argmin(np.where(cl > 0, gap, np.inf)))
    for i, (y, x) in enumerate(spurious_chunks()):               # เล่นตัวเลขสุ่มซ้ำจนถึงก้อนของคู่ตัวอย่าง
        if i == k // SPUR_CHUNK:
            y, x = y[k % SPUR_CHUNK], x[k % SPUR_CHUNK]
            break
    assert abs(row_corr(y[None], x[None])[0] - cl[k]) < 1e-12, "เล่นซ้ำต้องได้คู่เดิม"
    r = C.ols(y, x)                                               # คู่ตัวอย่าง: คิดด้วย OLS ตัวเต็ม
    assert abs(float(r["t"][1]) - tl[k]) < 1e-6 * max(1.0, abs(tl[k])), "สูตรลัดของ t ต้องตรงกับ C.ols"
    example = {"y": y, "x": x, "corr_levels": cl[k], "t": float(r["t"][1]), "r2": r["r2"],
               "slope": float(r["coef"][1]), "corr_changes": cc[k], "t_changes": tc[k]}
    return {"corr_levels": cl, "corr_changes": cc, "t_levels": tl, "t_changes": tc, "example": example,
            "same_corr": same_corr_pairs()}


# ─────────────────────────────── 2g: half-life ที่ประมาณได้ ───────────────────────────────
def exp_hlbias():
    g = C.rng(OFF_HLB)
    by_n = {}
    for n in HLB_N:
        fits = [C.fit_ar1(row) for row in C.ar1_batch(WORLDS_BIG, n, HLB_TRUE, 1.0, g)]
        by_n[n] = {"hl": np.array([f["half_life"] for f in fits]), "phi": np.array([f["phi"] for f in fits])}
    rw = np.cumsum(C.rng(OFF_HLB_RW).standard_normal((WORLDS_BIG, HLB_RW_N)), axis=1)
    hl_rw = np.array([C.fit_ar1(row)["half_life"] for row in rw])
    return {"by_n": by_n, "rw_hl": hl_rw, "rw_adf_pass": reject_rate(rw, crit5(HLB_RW_N))}


# ─────────────────────────────── run / figures ───────────────────────────────
@functools.lru_cache(maxsize=1)
def run():
    """คำนวณทุกการทดลอง (ผลเหมือนเดิมทุกครั้ง เพราะ seed ตายตัว)"""
    return {"slide3": exp_slide3(), "halves": exp_halves(), "vargrowth": exp_vargrowth(), "hand": exp_hand(),
            "null": exp_null(), "power": exp_power(), "spurious": exp_spurious(), "hlbias": exp_hlbias()}


# ── การปัดเลข: หลักสุดท้ายที่พิมพ์ต้องนิ่งเมื่อเปลี่ยน seed (ตรวจแล้วด้วยการรันซ้ำที่ seed อื่น) ──
#    สัดส่วนจาก 2,000–20,000 โลก → เปอร์เซ็นต์เต็ม (คลาดได้ราว ±0.5–1 จุด) · ระยะห่างหน่วย sd → _rg
def _rg(v):
    """ค่าที่ ≥ 0.1 ปัด 1 ตำแหน่ง ค่าที่เล็กกว่านั้นปัด 2 ตำแหน่ง (0.06 ยังเป็น 0.06 ไม่กลายเป็น 0.1)"""
    return C.rd(v, 2 if abs(v) < 0.1 else 1)


def _mc3(prefix, arr, d=2, scale=1.0, suffix=""):
    """ค่ากลาง + ช่วง 5–95% ของ Monte Carlo เป็นสามคีย์ <prefix>_med/_p5/_p95<suffix>
    d = จำนวนทศนิยม หรือฟังก์ชันปัดเลข"""
    rnd = d if callable(d) else (lambda v: C.rd(v, d))
    lo, mid, hi = np.percentile(np.asarray(arr, float) * scale, [5, 50, 95])
    return {f"{prefix}_med{suffix}": rnd(mid), f"{prefix}_p5{suffix}": rnd(lo), f"{prefix}_p95{suffix}": rnd(hi)}


def _fig_slide3(sl):
    def one(d):
        out = {k: C.rd(d[k], 2) for k in ("mean_h1", "mean_h2", "sd_h1", "sd_h2", "mean_all", "sd_all",
                                          "min", "max", "adf")}
        out["adf_verdict"] = verdict(d["adf"], d["crit5"])
        return out

    return {"n_bars": SLIDE_N, "half_bars": SLIDE_N // 2, "worlds": WORLDS_BIG, "seed_offset": str(OFF_SLIDE),
            "world_index": str(sl["world"]), "adf_crit5": C.rd(sl["crit5"], 2), "n_sim_null": null_sims(SLIDE_N),
            "rw": one(sl["demo"]["rw"]), "noise": one(sl["demo"]["noise"])}


def _fig_eye(sl):
    def one(d):
        return {"gap_sigma": C.rd(d["gap"], 2), "crossings": int(d["crossings"]),
                "range_first": C.rd(d["range_first"], 2), "range_all": C.rd(d["range_all"], 2),
                "range_ratio_pct": C.pct(d["range_ratio"], 0)}

    def mc(m):
        out = _mc3("gap", m["gap"], _rg, suffix="_sigma")
        out.update(_mc3("crossings", m["crossings"], 0))
        out.update(_mc3("range_ratio", m["range_ratio"], 0, scale=100.0, suffix="_pct"))
        out["gap_gt1_pct"] = C.pct(np.mean(m["gap"] > 1.0), 0)
        out["adf_pass_pct"] = C.pct(m["adf_pass"], 0)
        return out

    out = {"n_bars": SLIDE_N, "first_bars": EYE_FIRST, "worlds": WORLDS_BIG, "half_life_bars": C.rd(HL_FAST, 0)}
    out.update({k: one(sl["demo"][k]) for k in ("rw", "noise")})
    out["mc"] = {k: mc(sl["mc"][k]) for k in ("rw", "ar1", "noise")}
    return out


def _fig_halves(hv):
    out = {"n_bars": HALVES_N, "worlds": WORLDS_BIG, "half_life_bars": C.rd(HL_FAST, 0),
           "half_life_slow_bars": C.rd(HL_SLOW, 0)}
    for k, m in hv.items():
        out[k] = dict(_mc3("gap", m["gap"], _rg, suffix="_sigma"), gap_gt1_pct=C.pct(np.mean(m["gap"] > 1.0), 0),
                      sd_ratio_med=C.rd(np.median(m["sd_ratio"]), 1))
    return out


def _fig_vargrowth(vg):
    out = {"n_bars": VG_N, "worlds": VG_WORLDS, "half_life_bars": C.rd(HL_FAST, 0),
           "sigma_eq_pct": C.pct(VG_SIGMA, 0), "step_sd_pct": C.pct(vg["step"], 2),
           "ceiling_pct": C.pct(vg["ceiling"], 2),
           # จุดจำลองห่างจากสูตรไม่เกินกี่ % (ปัดขึ้นเป็นจำนวนเต็ม — เป็นขอบบน จึงนิ่งเมื่อเปลี่ยน seed)
           "sim_within_pct": int(math.ceil(100.0 * vg["max_dev"]))}
    for i, h in enumerate(HORIZONS):
        out[f"h{h}"] = {"rw_theory_pct": C.pct(vg["rw_theory"][i], 2), "ar1_theory_pct": C.pct(vg["ar1_theory"][i], 2),
                        "rw_times": C.rd(vg["rw_theory"][i] / vg["rw_theory"][0], 1),
                        "ar1_times": C.rd(vg["ar1_theory"][i] / vg["ar1_theory"][0], 1)}
    return out


def _fig_hand(hd):
    def chain(d):
        """เลขของห่วงโซ่คิดมือ ปัดให้ "คิดตามด้วยเลขที่พิมพ์แล้วได้เลขที่พิมพ์ในขั้นถัดไป" ทุกขั้น
        (Sxy ÷ Sxx = γ · s ÷ √Sxx = se · γ ÷ se = t) — เริ่มที่ γ 4 ตำแหน่ง se 5 ตำแหน่ง
        ถ้าบังเอิญตกขอบการปัดจนต่อกันไม่ตรง ค่อยเพิ่มทศนิยมทีละหนึ่ง"""
        t = C.rd(d["t"], 2)
        for p in range(4):
            c = {"sxx": C.rd(d["sxx"], 2 + p), "sqrt_sxx": C.rd(math.sqrt(d["sxx"]), 3 + p),
                 "sxy": C.rd(d["sxy"], 2 + p), "slope": C.rd(d["slope"], 4 + p),
                 "resid_sd": C.rd(d["resid_sd"], 4 + p), "se": C.rd(d["se"], 5 + p), "t": t}
            if (C.rd(c["sxy"] / c["sxx"], 4 + p) == c["slope"] and C.rd(c["resid_sd"] / c["sqrt_sxx"], 5 + p) == c["se"]
                    and C.rd(c["slope"] / c["se"], 2) == t):
                return c
        raise ValueError("เลขคิดมือที่ปัดแล้วต่อกันไม่ตรง แม้เพิ่มทศนิยมแล้ว")

    def one(d, c0, c1):
        hl = d["half_life"]
        out = {"n_reg": d["n_reg"]}
        out.update(chain(d))
        out.update({"intercept": C.rd(d["intercept"], 4), "phi_hat": C.rd(d["phi_hat"], 4),
                    "pull_pct": C.pct(-d["slope"], 1),
                    "half_life_bars": C.rd(hl, 1) if math.isfinite(hl) else "ไม่มี",
                    "verdict": verdict(d["t"], c0), "adf_lags1": C.rd(d["adf_lags1"], 2),
                    "verdict_lags1": verdict(d["adf_lags1"], c1)})
        return out

    c0, c1, m = hd["crit5_lags0"], hd["crit5_lags1"], hd["mc"]
    return {"n_bars": HAND_N, "worlds": WORLDS_BIG, "seed_offset": str(OFF_HAND), "world_index": str(hd["world"]),
            "half_life_bars": C.rd(HL_FAST, 0), "phi_true": C.rd(PHI_FAST, 4),
            "slope_true": C.rd(PHI_FAST - 1.0, 4), "pull_true_pct": C.pct(1.0 - PHI_FAST, 1),
            "crit5_lags0": C.rd(c0, 2), "crit5_lags1": C.rd(c1, 2), "n_sim_null": null_sims(HAND_N, 0),
            "st": one(hd["st"], c0, c1), "rw": one(hd["rw"], c0, c1),
            "mc": dict(_mc3("t_st", m["t_st"], 1), **_mc3("t_rw", m["t_rw"], 1),
                       pass_st_pct=C.pct(m["pass_st"], 0), pass_rw_pct=C.pct(m["pass_rw"], 0),
                       neg_slope_rw_pct=C.pct(m["neg_slope_rw"], 0))}


def _normal_cdf(z):
    return 0.5 * math.erfc(-z / math.sqrt(2.0))


def _fig_null(nu):
    return {"n_bars": NULL_N, "n_sim": null_sims(NULL_N), "lags": LAGS,
            "crit1": C.rd(nu["crit"][0.01], 2), "crit5": C.rd(nu["crit"][0.05], 2),
            "crit10": C.rd(nu["crit"][0.10], 2), "median": C.rd(nu["median"], 2), "mean": C.rd(nu["mean"], 2),
            "p_lt_1645_pct": C.pct(nu["p_lt_1645"], 0), "p_lt_2_pct": C.pct(nu["p_lt_2"], 0),
            "p_lt_0_pct": C.pct(nu["p_lt_0"], 0),
            "normal_p_lt_1645_pct": C.pct(_normal_cdf(-1.645), 1), "normal_p_lt_2_pct": C.pct(_normal_cdf(-2.0), 1),
            "p_lt_1645_times": C.rd(nu["p_lt_1645"] / _normal_cdf(-1.645), 1),
            "p_lt_2_times": C.rd(nu["p_lt_2"] / _normal_cdf(-2.0), 0),
            "crit5_by_n_sims": N_SIM_NULL,
            "crit5_by_n": {f"n{n}": C.rd(v, 2) for n, v in nu["crit5_by_n"].items()}}


def _fig_power(pw):
    ru = pw["rule"]
    k = int(5 * round(pw["fine_interp"] / 5.0))
    out = {"worlds": WORLDS, "lags": LAGS, "n_sim_null": N_SIM_NULL, "target_pct": C.pct(POWER_TARGET, 0),
           "crit5": {f"n{n}": C.rd(v, 2) for n, v in pw["crit"].items()}}
    for i, hl in enumerate(POWER_HL):
        out[f"hl{hl}"] = {f"n{n}_pct": C.pct(pw["grid"][i, j], 0) for j, n in enumerate(POWER_N)}
    out["fine"] = {f"n{n}": {f"r{r}_pct": C.pct(pw["fine"][i, j], 0) for j, r in enumerate(FINE_RATIOS)}
                   for i, n in enumerate(FINE_N)}
    out["fine"]["pooled"] = {f"r{r}_pct": C.pct(v, 0) for r, v in zip(FINE_RATIOS, pw["fine_pooled"])}
    out["rule"] = {"grid_ratio": C.rd(ru["reach"], 0), "grid_ratio_min_pct": C.pct(ru["reach_min"], 0),
                   "grid_below_ratio": C.rd(ru["below"], 0), "grid_below_min_pct": C.pct(ru["below_min"], 0),
                   "grid_below_max_pct": C.pct(ru["below_max"], 0), "grid_interp_ratio": C.rd(ru["interp"], 0),
                   "fine_interp_ratio": C.rd(pw["fine_interp"], 0), "k_round5": k,
                   # ตัวอย่างใช้กฎ (เลขคณิตของกฎที่ปัดแล้ว): สเปรด half-life 12 แท่ง → k × 12 แท่ง
                   "demo_hl_bars": C.rd(HLB_TRUE, 0), "n_for_demo_hl_bars": k * C.rd(HLB_TRUE, 0)}
    out["rule"].update({f"fine_interp_n{n}": C.rd(v, 0) for n, v in pw["fine_interp_n"].items()})
    return out


def _fig_spurious(sp):
    ex, sc = sp["example"], sp["same_corr"]
    al, ac = np.abs(sp["corr_levels"]), np.abs(sp["corr_changes"])
    out = {"pairs": SPUR_PAIRS, "n_bars": SPUR_N,
           "corr_gt05_pct": C.pct(np.mean(al > 0.5), 0), "corr_gt08_pct": C.pct(np.mean(al > 0.8), 0),
           "t_gt2_pct": C.pct(np.mean(np.abs(sp["t_levels"]) > 2.0), 0),
           "t_abs_med": C.rd(np.median(np.abs(sp["t_levels"])), 0),
           # การเปลี่ยนแปลงรายวันไม่เกี่ยวกันจริง → |t| > 2 ควรเกิดโดยบังเอิญราว 2·Φ(−2) ≈ 4.6% (เทียบกันที่ 1 ตำแหน่ง)
           "t_changes_gt2_pct": C.pct(np.mean(np.abs(sp["t_changes"]) > 2.0), 1),
           "chance_t_gt2_pct": C.pct(2.0 * _normal_cdf(-2.0), 1),
           "t_changes_abs_med": C.rd(np.median(np.abs(sp["t_changes"])), 1)}
    out.update(_mc3("corr_levels_abs", al, 2))
    out.update(_mc3("corr_changes_abs", ac, lambda v: C.rd(v, 3 if v < 0.01 else 2)))
    out["example"] = {"pctile": SPUR_PCTILE, "corr_levels": C.rd(ex["corr_levels"], 2), "t": C.rd(ex["t"], 1),
                      "r2_pct": C.pct(ex["r2"], 0), "slope": C.rd(ex["slope"], 2),
                      "corr_changes": C.rd(ex["corr_changes"], 2), "t_changes": C.rd(ex["t_changes"], 2)}
    out["same_corr"] = {"worlds": WORLDS, "n_bars": SPUR_N, "target_corr": C.rd(sc["target"], 2),
                        "leash_sigma_eq_pct": C.pct(sc["sigma_eq"], 1),
                        "leash_half_life_bars": C.rd(sc["half_life"], 0), "adf_crit5": C.rd(crit5(SPUR_N), 2)}
    for k in ("fake", "leash"):
        out["same_corr"][k] = dict(_mc3("ret_corr", sc[k]["ret_corr"], 2),
                                   adf_pass_pct=C.pct(sc[k]["adf_pass"], 0))
    return out


def _fig_hlbias(hb):
    phi = C.phi_from_half_life(HLB_TRUE)
    out = {"true_bars": C.rd(HLB_TRUE, 0), "phi_true": C.rd(phi, 3), "worlds": WORLDS_BIG}
    for n, m in hb["by_n"].items():
        out[f"n{n}"] = dict(_mc3("hl", m["hl"], 1, suffix="_bars"), short_pct=C.pct(np.mean(m["hl"] < HLB_TRUE), 0),
                            phi_med=C.rd(np.median(m["phi"]), 3),
                            hl_med_ratio_pct=C.pct(np.median(m["hl"]) / HLB_TRUE, 0),
                            n_over_hl=C.rd(n / HLB_TRUE, 0))
    hl = hb["rw_hl"]
    out["rw"] = {"n_bars": HLB_RW_N, "worlds": WORLDS_BIG, "finite_pct": C.pct(np.mean(np.isfinite(hl)), 0),
                 "hl_med_bars": C.rd(np.median(hl), 0), "hl_med_over_n_pct": C.pct(np.median(hl) / HLB_RW_N, 0),
                 "hl_p5_bars": C.rd(np.percentile(hl, 5), 0), "adf_pass_pct": C.pct(hb["rw_adf_pass"], 0)}
    return out


def _about():
    return {
        "data": "ข้อมูลจำลองทั้งหมด สร้างจากตัวสุ่มที่ทำซ้ำได้ ไม่มีการเทรดและไม่มีต้นทุนในตอนนี้ "
                "โลกตัวอย่างของแต่ละรูปคือโลกที่สถิติหลักอยู่ใกล้ค่ากลางของ Monte Carlo ที่สุด ข้อสรุปทั่วไปให้ดูจาก Monte Carlo",
        "model": "ทุกเส้นมาจากสมการเดียว x(t) = φ·x(t−1) + e(t) โดย φ = 1 คือ random walk "
                 f"φ = {PHI_FAST:.3f} คือ AR(1) half-life {HL_FAST:g} แท่ง และ φ = 0 คือ noise ล้วน",
        "precision": "ตัวเลข Monte Carlo ปัดให้หลักสุดท้ายนิ่งเมื่อเปลี่ยน seed: สัดส่วนเป็นเปอร์เซ็นต์เต็ม (คลาดได้ราว ±1 จุด "
                     "ตาราง power ราว ±2 จุด) เส้นตัดสองตำแหน่งคลาดได้ราว ±0.01",
        "slide3": f"จำลองรูปสไลด์ 3 จำนวน {SLIDE_N} แท่ง เส้นไม่นิ่งคือผลบวกสะสมของเส้นนิ่ง (ตัวเลขสุ่มชุดเดียวกัน sd 1 หน่วย) "
                  f"เลือกโลกตัวอย่างจาก {WORLDS_BIG:,} โลก",
        "eye": f"การตรวจด้วยตาสามข้อบนเส้น {SLIDE_N} แท่ง: ระยะห่างของค่าเฉลี่ยสองครึ่งหารด้วย sd รวมของสองครึ่ง "
               f"จำนวนครั้งที่ข้ามค่าเฉลี่ยของทั้งเส้น และช่วงสูงถึงต่ำของ {EYE_FIRST} แท่งแรกเทียบกับทั้งเส้น "
               f"Monte Carlo {WORLDS_BIG:,} โลกต่อชนิด",
        "halves": f"ค่าเฉลี่ยครึ่งแรกเทียบครึ่งหลังของเส้น {HALVES_N} แท่ง Monte Carlo {WORLDS_BIG:,} โลกต่อชนิด "
                  f"(random walk, AR(1) half-life {HL_SLOW:g}, AR(1) half-life {HL_FAST:g}, noise)",
        "vargrowth": f"sd ของการเปลี่ยนแปลงใน h แท่ง AR(1) half-life {HL_FAST:g} แท่ง σ ระยะยาว {VG_SIGMA * 100:g}% "
                     "ส่วน random walk ตั้งให้ขยับต่อแท่งเท่ากัน ค่าหลักมาจากสูตร (รู้แบบจำลองแน่นอน) "
                     f"และตรวจด้วยการจำลอง {VG_WORLDS:,} โลก โลกละ {VG_N} แท่ง",
        "adf_hand": f"ADF คิดมือบน {HAND_N} แท่ง ใช้สมการสั้นที่สุด (lags 0 มีค่าคงที่) สองเส้นใช้ตัวเลขสุ่มชุดเดียวกัน "
                    f"ต่างกันที่ φ เลือกโลกที่ค่า t ของทั้งสองเส้นใกล้ค่ากลางของ {WORLDS_BIG:,} โลกที่สุด",
        "adf": f"ADF ของห้องทดลองใช้ lags {LAGS} มีค่าคงที่ เส้นตัดทุกตัวมาจากการจำลอง random walk อย่างน้อย "
               f"{N_SIM_NULL:,} เส้นที่ความยาวและ lags เดียวกับตัวสถิติ",
        "adf_null": f"การแจกแจงของค่า t ของ ADF เมื่อความจริงคือ random walk ยาว {NULL_N} แท่ง จำนวน "
                    f"{null_sims(NULL_N):,} เส้น",
        "power": f"อัตราที่ ADF ปฏิเสธ random walk ที่ระดับ 5% เมื่อความจริงคือ AR(1) ช่องละ {WORLDS:,} โลก "
                 "กฎหัวแม่มือได้จากการกวาดอัตราส่วน n ต่อ half-life แล้วลากเส้นตรงระหว่างจุดที่คร่อม 80% จึงเป็นค่าประมาณ",
        "spurious": f"random walk อิสระ {SPUR_PAIRS:,} คู่ ยาว {SPUR_N} แท่ง ถดถอยเส้นหนึ่งบนอีกเส้น (มีค่าคงที่) "
                    f"คู่ตัวอย่างคือคู่ที่ค่า correlation สัมบูรณ์อยู่ที่เปอร์เซ็นไทล์ {SPUR_PCTILE}",
        "same_corr": f"สองชนิดของคู่ที่ correlation ของผลตอบแทนรายวันเท่ากันโดยตั้งใจ ชนิดละ {WORLDS:,} โลก ยาว {SPUR_N} แท่ง "
                     "ทดสอบ ADF บนสเปรดจริงที่รู้เฉลย",
        "hl_bias": f"half-life จริง {HLB_TRUE:g} แท่ง ประมาณด้วย AR(1) จากข้อมูล n แท่ง Monte Carlo {WORLDS_BIG:,} โลกต่อค่า n "
                   f"และ random walk ยาว {HLB_RW_N} แท่งอีก {WORLDS_BIG:,} โลก",
    }


def figures(res=None):
    res = res or run()
    return {"about": _about(), "slide3": _fig_slide3(res["slide3"]), "eye": _fig_eye(res["slide3"]),
            "halves": _fig_halves(res["halves"]), "vargrowth": _fig_vargrowth(res["vargrowth"]),
            "adf_hand": _fig_hand(res["hand"]), "adf_null": _fig_null(res["null"]),
            "power": _fig_power(res["power"]), "spurious": _fig_spurious(res["spurious"]),
            "hl_bias": _fig_hlbias(res["hlbias"])}


# ─────────────────────────────── charts ───────────────────────────────
def _n(v, d=None):
    """ตัวเลขสำหรับคำบรรยายใต้รูป (เครื่องหมายลบแบบ U+2212)"""
    return V.minus(f"{v:,.{d}f}" if d is not None else f"{v:,}" if isinstance(v, int) else f"{v}")


def _chart_slide3(sl, fg):
    d, f = sl["demo"], fg["slide3"]
    rows = [{"y": d["rw"]["x"], "title": "ไม่นิ่ง: random walk", "hist_title": "ฮิสโทแกรม",
             "color": V.RED, "mean": True},
            {"y": d["noise"]["x"], "title": "นิ่ง: noise รอบค่าเฉลี่ยคงที่", "hist_title": "ฮิสโทแกรม",
             "color": V.BLUE, "mean": True}]
    cap = (f"ข้อมูลจำลอง {SLIDE_N} แท่ง · สองเส้นนี้มาจาก<b>ตัวเลขสุ่มชุดเดียวกัน</b>: เส้นล่างคือตัวเลขสุ่มแต่ละแท่ง "
           f"เส้นบนคือผลบวกสะสมของมัน · เส้นบน ค่าเฉลี่ยครึ่งแรก {_n(f['rw']['mean_h1'], 2)} ครึ่งหลัง "
           f"{_n(f['rw']['mean_h2'], 2)} — ฮิสโทแกรมจึงเป็นแค่บันทึกว่าเส้นเคยเดินผ่านตรงไหน ไม่ได้บอกว่าจะกลับไปตรงไหน "
           f"· เส้นล่าง {_n(f['noise']['mean_h1'], 2)} กับ {_n(f['noise']['mean_h2'], 2)} ฮิสโทแกรมทรงระฆังใช้ทำนายได้")
    return V.series_with_hist("sas-p2-slide3", rows,
                              "สองแถว: random walk ที่ไหลออกจากค่าเฉลี่ยกับฮิสโทแกรมที่ไม่เป็นทรง "
                              "และ noise ที่แกว่งรอบค่าเฉลี่ยคงที่กับฮิสโทแกรมทรงระฆัง",
                              cap, xlabel="แท่งที่", hist_xlabel="ค่าของอนุกรม")


def _chart_eye(sl, fg):
    f = fg["eye"]
    fig = V.Fig("sas-p2-eye-tests", 760, 444)
    fig.legend([("ค่าเฉลี่ยของแต่ละครึ่ง", V.INK, "line"), (f"ค่าเฉลี่ยทั้ง {SLIDE_N} แท่ง", "#64748b", "line", "4 4"),
                (f"ช่วงสูง–ต่ำของ {EYE_FIRST} แท่งแรก", V.AMBER, "band")], 742, 20, anchor="end")
    half = SLIDE_N // 2
    ticks = [0, 49, 99, 149, SLIDE_N - 1]                      # index 49 = แท่งที่ 50
    for i, (key, name, color) in enumerate((("rw", "random walk", V.RED), ("noise", "noise ที่นิ่ง", V.BLUE))):
        d, fe = sl["demo"][key], f[key]
        last = i == 1
        p = fig.panel((0, SLIDE_N - 1), V.auto_lim(d["x"], n=4), x=58, y=62 + 196 * i, w=684, h=140)
        p.band(d["min_first"], d["max_first"], V.AMBER, 0.16)
        p.grid(n=4).yaxis()
        p.vline(EYE_FIRST - 0.5, color="#94a3b8").vline(half - 0.5, color="#94a3b8")
        p.hline(d["mean_all"], color="#64748b")
        p.line(sl["t"], d["x"], color)
        p.line([0, half - 1], [d["mean_h1"]] * 2, V.INK, width=3.2)
        p.line([half, SLIDE_N - 1], [d["mean_h2"]] * 2, V.INK, width=3.2)
        p.xaxis(ticks=ticks, labels=[str(t + 1) for t in ticks], title="แท่งที่" if last else None)
        p.title(name, f"ค่าเฉลี่ยสองครึ่งห่างกัน {_n(fe['gap_sigma'], 2)} sd · ข้ามค่าเฉลี่ย {fe['crossings']} ครั้ง · "
                      f"{EYE_FIRST} แท่งแรกกว้าง {fe['range_ratio_pct']}% ของทั้งช่วง")
    m_rw, m_ar, m_no = f["mc"]["rw"], f["mc"]["ar1"], f["mc"]["noise"]
    cap = (f"ข้อมูลจำลอง · การตรวจด้วยตาสามข้อบนสองเส้นของรูปก่อนหน้า (เส้นประแนวตั้ง = แท่งที่ {EYE_FIRST} "
           f"กับแท่งที่ {half} ที่แบ่งครึ่ง) · random walk: ค่าเฉลี่ยของสองครึ่ง (เส้นดำหนา) "
           f"ห่างกัน {_n(f['rw']['gap_sigma'], 2)} sd ข้ามค่าเฉลี่ยแค่ {f['rw']['crossings']} ครั้ง และเส้นเดินออกนอกแถบสีส้ม "
           f"(ช่วงของ {EYE_FIRST} แท่งแรก) ไปเรื่อย ๆ จนแถบเหลือเพียง {f['rw']['range_ratio_pct']}% ของทั้งช่วง "
           f"· noise ที่นิ่ง: ห่างกัน {_n(f['noise']['gap_sigma'], 2)} sd ข้าม {f['noise']['crossings']} ครั้ง "
           f"และ {EYE_FIRST} แท่งแรกก็กว้างถึง {f['noise']['range_ratio_pct']}% ของทั้งช่วงแล้ว "
           f"· ค่ากลางของ {WORLDS_BIG:,} โลก: ข้ามค่าเฉลี่ย {m_rw['crossings_med']} กับ {m_no['crossings_med']} ครั้ง "
           f"แต่ AR(1) ที่นิ่งจริง (half-life {HL_FAST:g} แท่ง) ข้ามเพียง {m_ar['crossings_med']} ครั้ง "
           f"— การตรวจด้วยตาเป็นแค่ด่านกรอง ไม่ใช่คำตัดสิน")
    return fig.svg("สองกรอบ: random walk กับ noise ที่นิ่ง พร้อมค่าเฉลี่ยของแต่ละครึ่ง เส้นค่าเฉลี่ยรวม "
                   "และแถบช่วงสูงต่ำของห้าสิบแท่งแรก", cap)


def _chart_halves(hv, fg):
    f = fg["halves"]
    names = (("noise", "noise ล้วน", V.BLUE), ("ar1", f"ดึงกลับเร็ว\n(half-life {HL_FAST:g} แท่ง)", V.BLUE),
             ("ar1_slow", f"ดึงกลับช้า\n(half-life {HL_SLOW:g} แท่ง)", V.AMBER), ("rw", "random walk\n(ไม่ดึงกลับ)", V.RED))
    rows = [{"label": lab, "mid": f[k]["gap_med_sigma"], "lo": f[k]["gap_p5_sigma"], "hi": f[k]["gap_p95_sigma"],
             "color": c} for k, lab, c in names]
    cap = (f"ข้อมูลจำลอง {WORLDS_BIG:,} โลกต่อแถว เส้นละ {HALVES_N} แท่ง · ถ้าฮิสโทแกรมเชื่อได้ ค่าเฉลี่ยของครึ่งแรกกับครึ่งหลัง"
           f"ต้องแทบไม่ต่างกัน · random walk ห่างกันค่ากลาง <b>{_n(f['rw']['gap_med_sigma'])} sd</b> "
           f"และห่างเกิน 1 sd ใน {f['rw']['gap_gt1_pct']}% ของโลก · เส้นที่ดึงกลับเร็วห่างเพียง "
           f"{_n(f['ar1']['gap_med_sigma'])} sd · แต่เส้นที่นิ่งจริงแบบดึงกลับช้า (half-life {HL_SLOW:g} แท่ง) "
           f"ก็ห่างเกิน 1 sd ได้ใน {f['ar1_slow']['gap_gt1_pct']}% ของโลก — ข้อนี้ใช้ยกธงให้ตรวจต่อ ไม่ใช่ใช้รับรองหรือคัดทิ้ง")
    return V.dot_interval("sas-p2-halves", rows,
                          "ระยะห่างของค่าเฉลี่ยครึ่งแรกกับครึ่งหลังของอนุกรมสี่ชนิด random walk ห่างที่สุด",
                          cap, xlabel="ค่าเฉลี่ยครึ่งแรกกับครึ่งหลังห่างกัน (หน่วย: sd)",
                          fmt=lambda v: V.num(v, 2 if abs(v) < 0.1 else 1))


def _chart_vargrowth(vg, fg):
    f = fg["vargrowth"]
    h_last = HORIZONS[-1]
    fl = f[f"h{h_last}"]
    hs = np.array(VG_CURVE_H, float)
    rw_c, ar_c = 100 * np.array(vg["curve"]["rw"]), 100 * np.array(vg["curve"]["ar1"])
    ceil = 100 * vg["ceiling"]
    fig = V.Fig("sas-p2-variance-growth", 760, 340)
    p = fig.panel((0, h_last + 4), (0, 20), x=58, y=58, w=548, h=230)
    p.grid(yticks=[0, 5, 10, 15, 20], xticks=[1, 50, 100, 150, 200, 250])
    p.yaxis(ticks=[0, 5, 10, 15, 20], fmt=lambda v: f"{v:.0f}%", title="sd ของการเปลี่ยนแปลงใน h แท่ง")
    p.hline(ceil, color=V.BLUE, label=f"เพดาน σ·√2 = {_n(f['ceiling_pct'], 2)}%", pos="out", label_color=V.BLUE)
    p.line(hs, rw_c, V.RED, width=2.2)
    p.line(hs, ar_c, V.BLUE, width=2.2)
    p.scatter(HORIZONS, 100 * np.array(vg["rw"]), V.RED, r=4.5, ring=True)
    p.scatter(HORIZONS, 100 * np.array(vg["ar1"]), V.BLUE, r=4.5, ring=True)
    p.xaxis(ticks=[1, 50, 100, 150, 200, 250], title="ระยะเวลา h (แท่ง)")
    # ป้ายวางใต้เส้นสีแดง (ช่องว่างระหว่างสองเส้น) จะได้ไม่ทับเส้น
    p.callout(h_last, 100 * vg["rw_theory"][-1], f"{h_last} แท่ง: {_n(fl['rw_theory_pct'], 2)}%", -96, 78, V.RED)
    fig.legend([("random walk (ไม่ดึงกลับ)", V.RED, "line"), (f"AR(1) half-life {HL_FAST:g} แท่ง (ดึงกลับ)", V.BLUE, "line"),
                (f"จุด = วัดจากการจำลอง {VG_WORLDS:,} โลก", V.MUTED, "dot")], 742, 20, anchor="end")
    cap = (f"เส้น = สูตร · จุด = ข้อมูลจำลอง {VG_WORLDS:,} โลก (ห่างจากสูตรไม่เกิน {f['sim_within_pct']}%) "
           f"· สองแบบขยับต่อแท่งเท่ากัน ({_n(f['step_sd_pct'], 2)}%) แต่ยิ่งรอนาน random walk ยิ่งไปไกล: "
           f"{h_last} แท่งไป {_n(fl['rw_theory_pct'], 2)}% (โต {_n(fl['rw_times'], 1)} เท่า = √{h_last}) "
           f"· sd ของการเปลี่ยนแปลงของเส้นที่มีแรงดึงกลับหยุดโตที่ราว {_n(f['ceiling_pct'], 2)}% "
           f"— \"ไกลจากค่าเฉลี่ย\" มีความหมายก็ต่อเมื่อมีเพดานแบบนี้")
    return fig.svg("sd ของการเปลี่ยนแปลงตามระยะเวลา: random walk โตตามรากที่สองของเวลาไม่หยุด ส่วน AR(1) ชนเพดาน", cap)


def _chart_hand(hd, fg):
    f = fg["adf_hand"]
    fig = V.Fig("sas-p2-adf-by-hand", 760, 372)
    fig.legend([("หนึ่งจุด = หนึ่งแท่ง", V.BLUE, "dot"), ("เส้น regression (ความชัน = γ)", V.RED, "line"),
                ("ค่าเฉลี่ยของ Δx ในแต่ละช่วงของระดับเมื่อวาน", V.PURPLE, "ring")], 742, 20, anchor="end")
    ylim = V.auto_lim(hd["st"]["d"], hd["rw"]["d"], n=4)
    spec = (("st", f"มีแรงดึงกลับ (φ = {_n(f['phi_true'], 3)})", 58, 300),
            ("rw", "random walk (φ = 1)", 430, 312))
    for key, name, x0, w in spec:
        d, fe = hd[key], f[key]
        xl = V.auto_lim(d["lag"], pad=0.04, n=4)
        p = fig.panel(xl, ylim, x=x0, y=66, w=w, h=236)
        p.grid(n=4, xticks=V.nice_ticks(xl[0], xl[1], 4)).yaxis(title="Δx ของวันนี้" if key == "st" else None)
        p.hline(0.0, color="#94a3b8", dash=None)
        p.scatter(d["lag"], d["d"], V.BLUE, r=2.2, opacity=0.4)
        xe = np.array(xl)
        p.line(xe, d["intercept"] + d["slope"] * xe, V.RED, hero=True)
        p.scatter(d["bin_x"], d["bin_d"], V.PURPLE, r=4.5, ring=True)
        p.xaxis(ticks=V.nice_ticks(xl[0], xl[1], 4), title="ระดับของเมื่อวาน x(t−1)")
        p.title(name, f"γ = {_n(fe['slope'], 4)} · t = {_n(fe['t'], 2)}")
    m = f["mc"]
    cap = (f"ข้อมูลจำลอง {HAND_N} แท่ง · สองเส้นใช้ตัวเลขสุ่มชุดเดียวกัน ต่างกันที่ φ ตัวเดียว · ADF คือการถามว่า "
           f"\"เมื่อวานอยู่สูง วันนี้มีแนวโน้มลงไหม\" · ซ้าย: ความชัน {_n(f['st']['slope'], 4)} หารด้วย standard error "
           f"{_n(f['st']['se'])} ได้ t = <b>{_n(f['st']['t'], 2)}</b> ({f['st']['verdict']}เกณฑ์ {_n(f['crit5_lags0'], 2)}) "
           f"· ขวา: ความชัน {_n(f['rw']['slope'], 4)} ได้ t = <b>{_n(f['rw']['t'], 2)}</b> ({f['rw']['verdict']}) "
           f"— ความชันของ random walk ก็ติดลบเล็กน้อยแทบทุกครั้ง ({m['neg_slope_rw_pct']}% ของ "
           f"{f['n_sim_null']:,} เส้น) จึงใช้ตาราง normal ตัดสินไม่ได้ · และเส้นที่ดึงกลับจริงแบบซ้ายมือ "
           f"ผ่านเกณฑ์เพียง {m['pass_st_pct']}% ของ {WORLDS_BIG:,} โลก")
    return fig.svg("จุดกระจายของการเปลี่ยนแปลงวันนี้เทียบกับระดับเมื่อวาน สองกรอบ: อนุกรมที่มีแรงดึงกลับ "
                   "เส้น regression เอียงลงชัดกว่า random walk", cap)


def _chart_null(nu, fg):
    f = fg["adf_null"]
    c5 = nu["crit"][0.05]
    step = 0.105                                  # ความกว้างช่อง: ให้ −1.645 ตกบนขอบช่องพอดี (สีจะได้ไม่คร่อมเส้น)
    xlim = (-1.645 - 32 * step, -1.645 + 34 * step)
    cap = (f"ข้อมูลจำลอง: random walk แท้ ๆ {f['n_sim']:,} เส้น ยาว {NULL_N} แท่ง — ไม่มีเส้นไหนมีแรงดึงกลับเลย "
           f"แต่ค่า t ของ ADF กองอยู่แถว {_n(f['median'], 2)} ไม่ใช่ 0 · ถ้าเปิดตาราง normal (ผ่านเมื่อ t &lt; −1.645) "
           f"จะบอกว่า \"มีแรงดึงกลับ\" ถึง <b>{f['p_lt_1645_pct']}%</b> ของเส้น (แท่งสีส้ม) แทนที่จะเป็น 5% "
           f"· เกณฑ์ที่ผิดพลาด 5% จริงคือ t &lt; {_n(f['crit5'], 2)}")
    return V.hist_chart("sas-p2-adf-null", nu["null"],
                        "ฮิสโทแกรมของค่า t ของ ADF เมื่อความจริงคือ random walk เลื่อนไปทางลบ "
                        "พร้อมเส้นเกณฑ์ของตาราง normal และเส้นเส้นตัดจริง",
                        cap, bins=66, xlim=xlim, xlabel="ค่า t ของ ADF", ylabel="จำนวนเส้น",
                        shade=(None, -1.645, V.AMBER),
                        vlines=[(c5, f"เส้นตัดจริง 5% = {_n(f['crit5'], 2)}", V.RED),
                                (-1.645, "ตาราง normal 5% = −1.645", V.MUTED)])


def _chart_power(pw, fg):
    f = fg["power"]
    vals = [[f[f"hl{hl}"][f"n{n}_pct"] for n in POWER_N] for hl in POWER_HL]
    cap = (f"ข้อมูลจำลอง {WORLDS:,} โลกต่อช่อง · ทุกช่อง<b>มีแรงดึงกลับจริง</b> ตัวเลข = % ของโลกที่ ADF จับได้ (ระดับ 5%) "
           f"· half-life 20 แท่งกับข้อมูล 250 แท่ง จับได้เพียง {f['hl20']['n250_pct']}% — \"ไม่ผ่าน ADF\" จึงไม่ได้แปลว่า "
           f"\"ไม่นิ่ง\" อาจแค่ข้อมูลสั้นไป · ช่องที่ข้อมูลยาว {f['rule']['grid_below_ratio']} เท่าของ half-life "
           f"ได้เพียง {f['rule']['grid_below_min_pct']}–{f['rule']['grid_below_max_pct']}% ส่วนช่องที่ยาว "
           f"{f['rule']['grid_ratio']} เท่าขึ้นไปได้ {f['rule']['grid_ratio_min_pct']}% ขึ้นไป "
           f"(จุดตัด {f['target_pct']}% ที่ละเอียดกว่านี้ ดูรูปถัดไป)")
    return V.heat_table("sas-p2-power", [f"half-life {hl} แท่ง" for hl in POWER_HL],
                        [f"{n:,} แท่ง" for n in POWER_N], vals,
                        "ตารางอัตราที่ ADF จับแรงดึงกลับได้ ตาม half-life และจำนวนแท่ง: ข้อมูลยาวและ half-life สั้นจับได้เกือบทุกครั้ง",
                        cap, fmt="{:.0f}%", row_title="ความจริง", col_title="ความยาวข้อมูล (n)", lo=0, hi=100)


def _chart_power_ratio(pw, fg):
    f = fg["power"]["rule"]
    series = [{"name": f"n = {n:,} แท่ง", "y": 100 * pw["fine"][i]} for i, n in enumerate(FINE_N)]
    cap = (f"ข้อมูลจำลอง {WORLDS:,} โลกต่อจุด · แกนนอนคือ \"ข้อมูลยาวกี่เท่าของ half-life\" · สามเส้น (ความยาวข้อมูลต่างกัน) "
           f"แทบทับกัน แปลว่าสิ่งที่กำหนดโอกาสจับได้คืออัตราส่วนนี้ ไม่ใช่จำนวนแท่งเฉย ๆ · เส้นตัด 80% ที่ราว "
           f"<b>{f['fine_interp_ratio']} เท่า</b> (ค่าประมาณจากการลากเส้นระหว่างจุด) ปัดเป็นกฎหัวแม่มือ "
           f"n ≳ {f['k_round5']} × half-life — half-life {f['demo_hl_bars']} แท่งจึงต้องการข้อมูลราว "
           f"{f['k_round5']} × {f['demo_hl_bars']} = {f['n_for_demo_hl_bars']:,} แท่ง")
    return V.line_chart("sas-p2-power-ratio", list(FINE_RATIOS), series,
                        "โอกาสที่ ADF จับแรงดึงกลับได้ เทียบกับอัตราส่วนจำนวนแท่งต่อ half-life สามความยาวข้อมูล",
                        cap, xlabel="จำนวนแท่ง ÷ half-life", ylabel="ADF จับได้ (% ของโลก)", ylim=(0, 100),
                        xticks=list(FINE_RATIOS), yfmt=lambda v: f"{v:.0f}%", markers=True,
                        hlines=[(100 * POWER_TARGET, "เป้า 80%")])


def _chart_spurious(sp, fg):
    f = fg["spurious"]
    edges = np.linspace(-1.0, 1.0, 41)
    mids = (edges[:-1] + edges[1:]) / 2
    fig = V.Fig("sas-p2-spurious", 760, 418)
    tops = (("corr_levels", "correlation ของระดับ", f"|correlation| เกิน 0.5 ใน {f['corr_gt05_pct']}% ของคู่"),
            ("corr_changes", "correlation ของการเปลี่ยนแปลงรายวัน (คู่เดียวกัน)", "กองอยู่ที่ศูนย์ ตรงกับความจริง"))
    for i, (key, title, sub) in enumerate(tops):
        share = 100.0 * np.histogram(sp[key], bins=edges)[0] / SPUR_PAIRS
        last = i == 1
        p = fig.panel((-1.0, 1.0), (0.0, float(share.max()) * 1.12), x=58, y=50 + 178 * i, w=684, h=124)
        p.grid(n=3).yaxis(fmt=lambda v: f"{v:.0f}%")
        p.hist(edges, share, V.BLUE, colors=[V.RED if abs(m) > 0.5 else V.BLUE for m in mids], opacity=0.88)
        p.xaxis(ticks=[-1, -0.5, 0, 0.5, 1], title="ค่า correlation" if last else None)
        p.title(title, sub)
        if not last:
            p.legend([("|correlation| > 0.5", V.RED, "rect")])
    cap = (f"ข้อมูลจำลอง: random walk {SPUR_PAIRS:,} คู่ที่<b>สุ่มแยกกันโดยสิ้นเชิง</b> ยาว {SPUR_N} แท่ง · แกนตั้ง = % ของคู่ "
           f"· บน: correlation ของระดับกระจายเต็มช่วง ค่ากลางของขนาด {_n(f['corr_levels_abs_med'], 2)} และ regression "
           f"ของระดับให้ |t| เกิน 2 ถึง {f['t_gt2_pct']}% ของคู่ · ล่าง: พอวัดจากการเปลี่ยนแปลงรายวัน "
           f"ค่ากลางเหลือ {_n(f['corr_changes_abs_med'], 2)} และ |t| เกิน 2 เพียง {_n(f['t_changes_gt2_pct'])}% "
           f"(ใกล้ {_n(f['chance_t_gt2_pct'])}% ที่ควรเกิดโดยบังเอิญ)")
    return fig.svg("สองฮิสโทแกรมของ correlation ระหว่าง random walk ที่ไม่เกี่ยวกัน: ของระดับกระจายกว้างทั้งช่วง "
                   "ของการเปลี่ยนแปลงรายวันกองแคบอยู่ที่ศูนย์", cap)


def _chart_spurious_example(sp, fg):
    ex, f = sp["example"], fg["spurious"]["example"]
    panels = [{"y": [ex["y"], ex["x"]], "title": "random walk สองเส้นที่สุ่มแยกกัน",
               "names": ["เส้นที่ 1", "เส้นที่ 2"], "color": [V.BLUE, V.AMBER]}]
    cap = (f"ข้อมูลจำลอง {SPUR_N} แท่ง · สองเส้นนี้ไม่มีอะไรเกี่ยวกันเลย แต่ correlation ของระดับ = "
           f"<b>{_n(f['corr_levels'], 2)}</b> และ regression ให้ t = {_n(f['t'], 1)} (R² {f['r2_pct']}%) "
           f"· correlation ของการเปลี่ยนแปลงรายวันของคู่เดียวกัน = {_n(f['corr_changes'], 2)} "
           f"· นี่ไม่ใช่คู่ที่แย่ที่สุด: หนึ่งในสี่ของ {SPUR_PAIRS:,} คู่ที่จำลอง ดูเกี่ยวกันยิ่งกว่านี้")
    return V.stacked_panels("sas-p2-spurious-example", panels,
                            "random walk สองเส้นที่สุ่มแยกกัน แต่ดูเหมือนเคลื่อนไหวสัมพันธ์กัน", cap,
                            xlabel="แท่งที่", panel_h=190)


def _chart_hlbias(hb, fg):
    f = fg["hl_bias"]
    rows = [{"label": f"n = {n:,} แท่ง\n({f[f'n{n}']['n_over_hl']} เท่าของ half-life)",
             "mid": f[f"n{n}"]["hl_med_bars"], "lo": f[f"n{n}"]["hl_p5_bars"], "hi": f[f"n{n}"]["hl_p95_bars"]}
            for n in HLB_N]
    a, b = f[f"n{HLB_N[0]}"], f[f"n{HLB_N[-1]}"]
    cap = (f"ข้อมูลจำลอง {WORLDS_BIG:,} โลกต่อแถว · half-life จริงคือ {f['true_bars']} แท่งทุกแถว · ข้อมูล {HLB_N[0]} แท่ง "
           f"ประมาณได้ค่ากลาง <b>{_n(a['hl_med_bars'], 1)} แท่ง</b> ({a['short_pct']}% ของโลกได้สั้นกว่าจริง) "
           f"และแกว่งตั้งแต่ {_n(a['hl_p5_bars'], 1)} ถึง {_n(a['hl_p95_bars'], 1)} · ข้อมูล {HLB_N[-1]:,} แท่ง "
           f"ได้ {_n(b['hl_med_bars'], 1)} แท่ง — สเปรดจริงมักกลับช้ากว่าที่ตัวเลขนี้บอก")
    return V.dot_interval("sas-p2-halflife-bias", rows,
                          "half-life ที่ประมาณได้ตามจำนวนแท่ง: ข้อมูลน้อยได้ค่าสั้นกว่าของจริงและแกว่งกว้าง",
                          cap, zero=False, xlabel="half-life ที่ประมาณได้ (แท่ง)", fmt=lambda v: V.num(v, 1),
                          vlines=[(HLB_TRUE, f"ของจริง = {HLB_TRUE:g} แท่ง", V.RED)])


def charts(res=None):
    res = res or run()
    fg = figures(res)
    return {
        "sas-p2-slide3": _chart_slide3(res["slide3"], fg),
        "sas-p2-eye-tests": _chart_eye(res["slide3"], fg),
        "sas-p2-halves": _chart_halves(res["halves"], fg),
        "sas-p2-variance-growth": _chart_vargrowth(res["vargrowth"], fg),
        "sas-p2-adf-by-hand": _chart_hand(res["hand"], fg),
        "sas-p2-adf-null": _chart_null(res["null"], fg),
        "sas-p2-power": _chart_power(res["power"], fg),
        "sas-p2-power-ratio": _chart_power_ratio(res["power"], fg),
        "sas-p2-spurious": _chart_spurious(res["spurious"], fg),
        "sas-p2-spurious-example": _chart_spurious_example(res["spurious"], fg),
        "sas-p2-halflife-bias": _chart_hlbias(res["hlbias"], fg),
    }


# ─────────────────────────────── สรุปเมื่อรันตรง ๆ ───────────────────────────────
def main():
    fg = figures()
    s3, ey, hv, vg, hd = fg["slide3"], fg["eye"], fg["halves"], fg["vargrowth"], fg["adf_hand"]
    nu, pw, sp, hb = fg["adf_null"], fg["power"], fg["spurious"], fg["hl_bias"]
    line = "─" * 78
    print("ห้องทดลองตอนที่ 2 — นิ่งหรือไม่นิ่ง: ใบอนุญาตของทั้งวิชา  (ข้อมูลจำลองทั้งหมด)")
    print(line)
    print(f"2a  รูปของสไลด์ 3  ({s3['n_bars']} แท่ง · ADF ต้องต่ำกว่า {s3['adf_crit5']} จึงผ่าน)")
    for key, name in (("rw", "random walk   "), ("noise", "noise ที่นิ่ง ")):
        d = s3[key]
        print(f"    {name} ค่าเฉลี่ย ครึ่งแรก {d['mean_h1']:+.2f} ครึ่งหลัง {d['mean_h2']:+.2f} · sd {d['sd_h1']:.2f} / "
              f"{d['sd_h2']:.2f} · ทั้งช่วง sd {d['sd_all']:.2f} · ADF {d['adf']:.2f} ({d['adf_verdict']})")
    print(f"2h  การตรวจด้วยตาสามข้อ  (ค่าเฉลี่ยสองครึ่งห่างกันกี่ sd · ข้ามค่าเฉลี่ยกี่ครั้ง · "
          f"{ey['first_bars']} แท่งแรกกว้างกี่ % ของทั้งช่วง)")
    for key, name in (("rw", "random walk       "), ("ar1", f"AR(1) half-life {ey['half_life_bars']}"),
                      ("noise", "noise ที่นิ่ง     ")):
        m = ey["mc"][key]
        if key in ey:                                  # AR(1) มีเฉพาะ Monte Carlo (ไม่ได้อยู่ในรูปของสไลด์)
            d = ey[key]
            print(f"    {name} โลกตัวอย่าง {d['gap_sigma']:.2f} sd · {d['crossings']} ครั้ง · {d['range_ratio_pct']}%")
        else:
            print(f"    {name} (ไม่มีในรูป — ดูเฉพาะ Monte Carlo)")
        print(f"        {ey['worlds']:,} โลก: {m['gap_med_sigma']} sd ({m['gap_p5_sigma']} ถึง "
              f"{m['gap_p95_sigma']}) เกิน 1 sd {m['gap_gt1_pct']}% · {m['crossings_med']} ครั้ง ({m['crossings_p5']} ถึง "
              f"{m['crossings_p95']}) · {m['range_ratio_med_pct']}% ({m['range_ratio_p5_pct']} ถึง {m['range_ratio_p95_pct']}) · "
              f"ADF ผ่าน {m['adf_pass_pct']}%")
    print(line)
    print(f"2b  ฮิสโทแกรมโกหก  ({hv['n_bars']} แท่ง · {hv['worlds']:,} โลก · ค่าเฉลี่ยครึ่งแรกกับครึ่งหลังห่างกันกี่ sd)")
    for key, name in (("rw", "random walk         "), ("ar1_slow", f"AR(1) half-life {hv['half_life_slow_bars']}  "),
                      ("ar1", f"AR(1) half-life {hv['half_life_bars']}  "), ("noise", "noise               ")):
        d = hv[key]
        print(f"    {name} ค่ากลาง {d['gap_med_sigma']} ({d['gap_p5_sigma']} ถึง {d['gap_p95_sigma']}) · "
              f"ห่างเกิน 1 sd {d['gap_gt1_pct']}% ของโลก · sd ครึ่งกว้าง/ครึ่งแคบ {d['sd_ratio_med']}")
    print(line)
    print(f"2c  sd ของการเปลี่ยนแปลงใน h แท่ง  (ขยับต่อแท่งเท่ากัน {vg['step_sd_pct']}% · เพดานของ AR(1) "
          f"{vg['ceiling_pct']}% · ตามสูตร · จำลอง {vg['worlds']:,} โลกได้ห่างจากสูตรไม่เกิน {vg['sim_within_pct']}%)")
    print("        h      random walk      AR(1) half-life 10")
    for h in HORIZONS:
        d = vg[f"h{h}"]
        print(f"      {h:>3}    {d['rw_theory_pct']:>6}%          {d['ar1_theory_pct']:>5}%"
              f"           โต {d['rw_times']} เท่า / {d['ar1_times']} เท่า")
    print(line)
    print(f"ADF คิดมือ  ({hd['n_bars']} แท่ง · Δx_t = a + γ·x_(t−1) · γ จริงของเส้นที่ดึงกลับ = {hd['slope_true']} · "
          f"ต้องได้ t ต่ำกว่า {hd['crit5_lags0']})")
    for key, name in (("st", f"φ = {hd['phi_true']} (ดึงกลับ)"), ("rw", "φ = 1 (random walk)  ")):
        d = hd[key]
        print(f"    {name}  Sxy {d['sxy']} ÷ Sxx {d['sxx']} = γ {d['slope']} · se = {d['resid_sd']} ÷ √Sxx "
              f"{d['sqrt_sxx']} = {d['se']} · "
              f"t = {d['t']:.2f} ({d['verdict']}) · half-life ที่อ่านได้ {d['half_life_bars']} แท่ง · "
              f"ADF lags 1 = {d['adf_lags1']:.2f} ({d['verdict_lags1']})")
    m = hd["mc"]
    print(f"    {hd['worlds']:,} โลก: t ของเส้นที่ดึงกลับ ค่ากลาง {m['t_st_med']} ({m['t_st_p5']} ถึง {m['t_st_p95']}) "
          f"ผ่าน {m['pass_st_pct']}% · random walk {m['t_rw_med']} ({m['t_rw_p5']} ถึง {m['t_rw_p95']}) "
          f"ผ่าน {m['pass_rw_pct']}% · ความชันติดลบ {m['neg_slope_rw_pct']}% (จาก {hd['n_sim_null']:,} เส้น)")
    print(line)
    print(f"2d  ADF เมื่อความจริงคือ random walk  ({nu['n_bars']} แท่ง · {nu['n_sim']:,} เส้น · lags {nu['lags']})")
    print(f"    เส้นตัด 1% {nu['crit1']:.2f} · 5% {nu['crit5']:.2f} · 10% {nu['crit10']:.2f} · ค่ากลาง {nu['median']:.2f} · "
          f"ติดลบ {nu['p_lt_0_pct']}% ของเส้น")
    print(f"    ถ้าใช้ตาราง normal: P(t < −1.645) = {nu['p_lt_1645_pct']}% (ควรเป็น {nu['normal_p_lt_1645_pct']}% → ผิด "
          f"{nu['p_lt_1645_times']} เท่า) · P(t < −2) = {nu['p_lt_2_pct']}% (ควรเป็น {nu['normal_p_lt_2_pct']}% → ผิด "
          f"{nu['p_lt_2_times']} เท่า)")
    print(f"    เส้นตัด 5% ตามความยาวข้อมูล ({nu['crit5_by_n_sims']:,} เส้นต่อความยาว): " + " · ".join(f"{k[1:]} แท่ง {v:.2f}" for k, v in nu["crit5_by_n"].items()))
    print(line)
    print(f"2e  power ของ ADF ที่ระดับ 5%  ({pw['worlds']:,} โลกต่อช่อง · ทุกช่องมีแรงดึงกลับจริง)")
    print("      half-life   " + "".join(f"n={n:<7}" for n in POWER_N))
    for hl in POWER_HL:
        print(f"      {hl:>5}       " + "".join(f"{pw[f'hl{hl}'][f'n{n}_pct']:>3}%     " for n in POWER_N))
    print("    กวาดตามอัตราส่วน n ÷ half-life:  " + "  ".join(f"{r}" for r in FINE_RATIOS))
    for n in FINE_N:
        print(f"      n = {n:<5}                     " + "  ".join(f"{pw['fine'][f'n{n}'][f'r{r}_pct']:>2}" for r in FINE_RATIOS))
    ru = pw["rule"]
    print(f"    ในตาราง: อัตราส่วน {ru['grid_ratio']} เท่าได้อย่างน้อย {ru['grid_ratio_min_pct']}% · {ru['grid_below_ratio']} "
          f"เท่าได้ {ru['grid_below_min_pct']}–{ru['grid_below_max_pct']}% · ลากเส้นตรงระหว่างสองจุดนี้ → ราว "
          f"{ru['grid_interp_ratio']} เท่า")
    print(f"    กวาดละเอียด: power 80% ที่ราว {ru['fine_interp_ratio']} เท่าของ half-life (ค่าประมาณ · แยกตาม n: "
          + " · ".join(f"{n} → {ru[f'fine_interp_n{n}']}" for n in FINE_N) + f") → กฎหัวแม่มือ n ≳ {ru['k_round5']} × half-life")
    print(f"    เช่น สเปรด half-life {ru['demo_hl_bars']} แท่ง ต้องมีข้อมูลราว {ru['k_round5']} × {ru['demo_hl_bars']} = "
          f"{ru['n_for_demo_hl_bars']:,} แท่ง จึงจะมีโอกาสราว 80% ที่ ADF จับได้")
    print(line)
    print(f"2f  regression ลวง  (random walk อิสระ {sp['pairs']:,} คู่ · {sp['n_bars']} แท่ง)")
    print(f"    ระดับ: |corr| ค่ากลาง {sp['corr_levels_abs_med']:.2f} ({sp['corr_levels_abs_p5']:.2f} ถึง "
          f"{sp['corr_levels_abs_p95']:.2f}) · |corr| > 0.5 ใน {sp['corr_gt05_pct']}% · |t| > 2 ใน {sp['t_gt2_pct']}% · "
          f"|t| ค่ากลาง {sp['t_abs_med']}")
    print(f"    การเปลี่ยนแปลงรายวัน: |corr| ค่ากลาง {sp['corr_changes_abs_med']} · |t| > 2 ใน "
          f"{sp['t_changes_gt2_pct']}% (โดยบังเอิญควรเป็นราว {sp['chance_t_gt2_pct']}%)")
    ex = sp["example"]
    print(f"    คู่ตัวอย่าง (เปอร์เซ็นไทล์ {ex['pctile']}): corr ระดับ {ex['corr_levels']:+.2f} · t {ex['t']:+.1f} · "
          f"R² {ex['r2_pct']}% · corr การเปลี่ยนแปลง {ex['corr_changes']:+.2f}")
    sc = sp["same_corr"]
    for key, name in (("fake", "ไม่มีสายจูง"), ("leash", "มีสายจูง  ")):
        d = sc[key]
        print(f"    {name}: corr ของผลตอบแทน {d['ret_corr_med']:.2f} ({d['ret_corr_p5']:.2f} ถึง {d['ret_corr_p95']:.2f}) · "
              f"ADF บนสเปรดจริงผ่าน {d['adf_pass_pct']}% ของ {sc['worlds']:,} โลก")
    print(line)
    print(f"2g  half-life ที่ประมาณได้  (ของจริง {hb['true_bars']} แท่ง · {hb['worlds']:,} โลกต่อแถว)")
    for n in HLB_N:
        d = hb[f"n{n}"]
        print(f"    n = {n:<5} ค่ากลาง {d['hl_med_bars']} แท่ง ({d['hl_p5_bars']} ถึง {d['hl_p95_bars']}) · "
              f"สั้นกว่าจริง {d['short_pct']}% ของโลก · φ ค่ากลาง {d['phi_med']} (จริง {hb['phi_true']})")
    d = hb["rw"]
    print(f"    random walk {d['n_bars']} แท่ง: ได้ half-life เป็นตัวเลข {d['finite_pct']}% ของโลก ค่ากลาง "
          f"{d['hl_med_bars']} แท่ง ({d['hl_med_over_n_pct']}% ของจำนวนแท่ง) ทั้งที่ ADF ผ่านเพียง {d['adf_pass_pct']}%")
    print(line)
    print("กราฟ: " + " · ".join(sorted(charts())))


if __name__ == "__main__":
    main()
