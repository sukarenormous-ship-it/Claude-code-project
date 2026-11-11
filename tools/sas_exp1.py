#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ห้องทดลองของตอนที่ 1 — "เดิมพันกับอะไร: ตัดตลาดทิ้ง แล้วเหลืออะไร" (สไลด์ 1–2)

ทุกอย่างในไฟล์นี้เป็น "ข้อมูลจำลอง" ที่เราสร้างเองและรู้เฉลย จึงตอบได้ตรง ๆ ว่าสเปรดแต่ละแบบ
เหลืออะไรอยู่ข้างใน — ซึ่งกับข้อมูลจริงไม่มีใครบอกได้

การทดลอง
  1a  slide2    จำลองรูปของสไลด์ 2 (200 แท่ง): A กับ B ขี่คลื่นร่วมลูกเดียวกัน + Risk ที่สุ่มเป็น
                noise "ในระดับราคา" → A − B แกว่งรอบศูนย์ · แล้วเปลี่ยนบรรทัดเดียว (เอาตัวเลขสุ่มชุดเดิม
                ไปบวกสะสม = ข่าวถาวร) → A − B ไม่กลับมา · Monte Carlo 2,000 โลกยืนยันว่าไม่ใช่โชคของโลกเดียว
  1b  neutral   "เป็นกลางต่อตลาด ≠ กลับสู่ค่าเฉลี่ย" (1,000 แท่ง): สองโลกที่ปัจจัยร่วมเหมือนกัน
                loading เท่ากัน และเรื่องเฉพาะตัวผันผวนต่อวันเท่ากัน ต่างกันข้อเดียว —
                โลก T เรื่องเฉพาะตัวเป็นข่าวชั่วคราว (AR(1) half-life 8 แท่ง) · โลก P เป็นข่าวถาวร
                (random walk) · วัด corr กับตลาด, ADF, sd ช่วงแรกเทียบทั้งช่วง, variance ratio, ช่วงกว้าง
                และ Monte Carlo 2,000 โลก
  walk          ตัวอย่างคิดมือ: ผลตอบแทนหนึ่งวันของ A, B และสเปรด แยกทีละปัจจัย เมื่อ loading ไม่เท่ากัน
  1c  unequal   loading ไม่เท่ากัน: A − B · A − β·B (β ที่ตัดตลาดพอดี / β จาก OLS) ·
                A − (B, C) · A − (B, C, D) ทั้งน้ำหนักจริงและน้ำหนักที่ประมาณจาก regression
                น้ำหนักทุกตัวประมาณจาก 500 แท่งแรก (train) แล้ววัดผลใน 1,000 แท่งถัดไป (test)
                → ส่วนของปัจจัยที่ตัดไม่หมดคือ random walk ที่ซ่อนอยู่ในสเปรด

วิธีรัน
    python3 tools/sas_exp1.py          พิมพ์สรุปตัวเลขสำคัญ (ราว 30–40 วินาที)

ตัวเลขมาจากสามแหล่ง — อ่านคีย์ให้ออกว่าตัวไหนเป็นแบบไหน
  • โลกตัวอย่าง (คีย์ชั้นบนสุดของแต่ละการทดลอง) = โลกเดียวที่ใช้วาดกราฟ เลือกด้วยกติกาที่เขียนไว้ในโค้ด
    (typical_offset) ไม่ได้เลือกด้วยตา: จากโลกผู้สมัคร 20–40 โลก เอาโลกที่สถิติสำคัญทุกตัวอยู่ใกล้
    ค่ากลางของ Monte Carlo ที่สุด · demo_max_dev_pct = สถิติเหล่านั้นห่างจากเปอร์เซ็นไทล์ที่ 50 ไม่เกินกี่จุด
  • .mc = Monte Carlo 2,000 โลก (ค่ากลาง + ช่วง 5–95%) — ใช้กับข้อสรุปทั่วไปเสมอ
    ปัดทศนิยมตามความแม่นที่วัดได้จริง (รันซ้ำด้วย seed อื่นสี่ชุด หลักสุดท้ายขยับได้ราว ±1):
    สัดส่วนโลกที่ ADF ผ่าน ส่วนแบ่งตามระยะถือ และส่วนแบ่งรายวัน เป็นจำนวนเต็ม % · สัดส่วนโลกมีความคลาด
    มาตรฐานไม่เกิน mc_se_pct (= 1.1 จุดที่ 2,000 โลก) จึงควรเขียนว่า "ราว 57%" ไม่ใช่ "57.0%"
  • .theory = คิดจากสูตรของแบบจำลองตรง ๆ (ไม่มีความคลาดจากการสุ่ม) — ใช้ได้เมื่อรู้ loading จริง
    สำหรับ β/น้ำหนักจาก regression ของผลตอบแทน ใช้ "น้ำหนักที่ regression เข้าหาเมื่อข้อมูลยาวไม่สิ้นสุด"

ข้อควรระวังเวลาอ่านผลของ 1c (ตัวเลขออกมาอย่างนี้จริง ไม่ได้ปรับการทดลองให้ "สวย")
  • เรื่องเฉพาะตัวในโลกนี้แกว่งแรง (1.22% ต่อวัน มากกว่าตลาด) ปัจจัยที่เหลือจึงเป็นส่วนน้อยของความแปรปรวน
    "รายวัน" (A − B ราว 17%) แต่เป็นส่วนใหญ่ของความแปรปรวนของ "การเปลี่ยนแปลง 250 แท่ง" (ราว 81%)
  • ADF (lags 1) จึง "ผ่าน" ในโลกส่วนใหญ่ทั้งที่สเปรดมี random walk ซ่อนอยู่จริง (A − B ผ่านเกินครึ่งของโลก)
    เพราะ noise ชั่วคราวก้อนใหญ่บัง random walk ก้อนเล็กไว้ · เพิ่ม lags เป็น 10 ก็ยังผ่านราวหนึ่งในสาม
    → อย่าใช้ ADF ตัวเดียวเป็นหลักฐานว่า "ตัดปัจจัยหมดแล้ว" ให้ดู sd ที่โตตามเวลาและ chg250_sd_pct ประกอบ
  • regression ของ "ผลตอบแทน" ให้น้ำหนักต่ำกว่าค่าที่ตัดปัจจัยได้พอดี แม้ข้อมูลยาวไม่สิ้นสุด (attenuation:
    ตัวช่วยมี noise ของตัวเอง) เช่น D ได้ราว 0.43 แทน 0.7 · regression ของ "ระดับราคา" ใกล้ค่าจริงกว่า
    แต่แกว่งกว้างเมื่อ train 500 แท่ง
  • สเปรดทุกแบบวัดต่อ A 1 หน่วย (ไม่ได้หารด้วยเงินรวมสองขา gross) — ไม่มีการเทรด ไม่มีต้นทุน

คีย์ของ figures()  (ทุกค่าปัดแล้ว · _pct = เปอร์เซ็นต์ · _bars = จำนวนแท่ง)
    about.*                 คำอธิบายสั้นของแต่ละการทดลองและค่าที่ตั้งไว้ (ภาษาไทย)
    slide2.level / .perm    โลกตัวอย่าง: แบบสไลด์ (noise ในระดับ) / แบบข่าวถาวร: corr_levels, corr_changes,
                            spread_sd, spread_change_sd, zero_cross, adf, adf_verdict …
    slide2.mc.level / .perm Monte Carlo: zero_cross_med/_p5/_p95, corr_levels_med/_p5/_p95, maxabs_med, reject_pct
    neutral.t / .p          โลกตัวอย่าง T / P: corr_spread_mkt, adf, sd_first250_pct, sd_all_pct, vr20,
                            range_pct, zero_cross … · neutral.mc.t / .p = Monte Carlo
    walk.*                  ตัวอย่างคิดมือ (day, a, b, c, d, ab, beta_mkt, three, equal)
    unequal.load.*          loading ของ A, B, C, D · unequal.onebeta.* ตาราง "β หนึ่งตัวตัดได้หนึ่งปัจจัย"
    unequal.two_best.*      ตัวช่วยสองตัว (B, C) ที่ดีที่สุดเท่าที่ทำได้ — ปัจจัยยังเหลือ
    unequal.<แบบ>.*         แบบ = ab | beta_mkt | beta_ols | beta_lvl | two | three_est | three_lvl | three_true
                            ชั้นบน = โลกตัวอย่าง (w_b, w_c, w_d, left_*, share_*_pct, corr_mkt, adf, sd_*)
                            .mc = Monte Carlo (reject_pct, reject_lags10_pct, hz_h*_pct, share_*_pct, chg250_sd_pct …)
                            .theory = สูตร (factor_h*_pct, chg250_sd_pct · beta_ols / three_est มี w_* ที่ข้อมูลไม่จำกัด)

ชื่อกราฟ: sas-p1-slide2 · sas-p1-slide2-permanent · sas-p1-neutral-not-reverting ·
          sas-p1-one-beta · sas-p1-factor-leftover · sas-p1-three-spreads · sas-p1-horizon-share
"""
import functools
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sas_core as C  # noqa: E402
import sas_svg as V  # noqa: E402

# ─────────────────────────────── ค่าที่ตั้งไว้ ───────────────────────────────
SLIDE_N = 200                                              # จำนวนแท่งของรูปสไลด์ 2
SLIDE_LEVEL = 100.0
SLIDE_WAVES = ((6.0, 160.0), (3.0, 90.0), (2.0, 55.0))     # (ขนาด, คาบ) ของคลื่น Market, Size, Growth
SLIDE_NOISE = 1.0                                          # sd ของ Risk(A), Risk(B) ในหน่วยราคา

N_BARS = 1000                                              # ช่วงที่ใช้วัดผล (1b ทั้งหมด · 1c ช่วง test)
N_TRAIN = 500                                              # 1c: ช่วงที่ใช้ประมาณน้ำหนัก
WORLDS = 2000                                              # จำนวนโลกของ Monte Carlo (ทุกการทดลอง)
CHUNK = 500                                                # สร้างโลกทีละก้อน กันหน่วยความจำบวม
MC_SE_PCT = round(100.0 * (0.25 / WORLDS) ** 0.5, 1)       # ความคลาดมาตรฐานสูงสุดของ "สัดส่วนโลก" (ที่ 50%)
N_SIM_NULL = 100_000                                       # จำนวน random walk ที่ใช้หาค่าวิกฤตที่พิมพ์ลงบท
N_SIM_NULL_ALT = 20_000                                    # ใช้เฉพาะนับสัดส่วนที่ lags = 10 (ไม่พิมพ์ค่าวิกฤต)
ADF_LAGS_ALT = 10
VR_Q = 20
HORIZONS = (1, 5, 20, 60, 120, 250)                        # ระยะถือ (แท่ง) ที่วัดส่วนแบ่งของปัจจัย

FACTORS = ("m", "s", "g")
FACTOR_SD = np.array([0.010, 0.005, 0.006])                # sd ต่อวันของ Market, Size, Growth
HALF_LIFE = 8.0                                            # เรื่องเฉพาะตัวแบบชั่วคราว: AR(1)
SIGMA_EQ = 0.03
PHI = C.phi_from_half_life(HALF_LIFE)
# sd ของ "การเปลี่ยนแปลงต่อวัน" ของ AR(1) = σ_eq·√(2(1−φ)) — โลก P ใช้ค่านี้เป็น σ ของ random walk
IDIO_CHANGE_SD = SIGMA_EQ * float(np.sqrt(2.0 * (1.0 - PHI)))

LOAD = {"a": (1.3, 0.4, 1.2), "b": (0.8, 1.0, 0.3), "c": (1.0, 0.2, 0.3), "d": (1.2, 0.2, 1.5)}
L_A = np.array(LOAD["a"])
L_HEDGE = np.array([LOAD["b"], LOAD["c"], LOAD["d"]])      # แถว = B, C, D · คอลัมน์ = Market, Size, Growth

# วันตัวอย่างสำหรับคิดมือ (หน่วย % ทั้งหมด): ตลาด +1.0, Size −0.8, Growth +0.8
WALK_F = (1.0, -0.8, 0.8)
WALK_IDIO = {"a": 0.2, "b": -0.16, "c": 0.04, "d": -0.1}

CONSTRUCTIONS = ("ab", "beta_mkt", "beta_ols", "beta_lvl", "two", "three_est", "three_lvl", "three_true")
ESTIMATED = ("beta_ols", "beta_lvl", "three_est", "three_lvl")
RETURN_REG = {"beta_ols": (0,), "three_est": (0, 1, 2)}    # regression ของผลตอบแทน: ใช้ตัวช่วยตัวไหนบ้าง

# seed: โลกผู้สมัครของโลกตัวอย่าง (เลือกด้วย typical_offset) · Monte Carlo · การแจกแจงของ ADF
CAND_SLIDE, CAND_NEUTRAL, CAND_UNEQUAL = range(100, 120), range(120, 150), range(150, 190)
OFF_NULL_1000, OFF_NULL_200, OFF_NULL_ALT = 190, 191, 192
OFF_SLIDE_MC, OFF_NEUTRAL_MC, OFF_UNEQUAL_MC = 193, 194, 195


# ─────────────────────────────── เครื่องมือเล็ก ๆ ───────────────────────────────
@functools.lru_cache(maxsize=None)
def adf_null(n_obs, lags, n_sim, offset):
    """การแจกแจงของค่า ADF ใต้ "ไม่มีแรงดึงกลับ" — ต้องใช้ n_obs และ lags ชุดเดียวกับตัวสถิติจริง"""
    return C.mc_null_adf(n_obs, n_sim=n_sim, lags=lags, g=C.rng(offset))


def row_corr(a, b):
    """correlation ทีละแถวของอาร์เรย์ (โลก × เวลา)"""
    a = a - a.mean(axis=1, keepdims=True)
    b = b - b.mean(axis=1, keepdims=True)
    return (a * b).sum(axis=1) / np.sqrt((a * a).sum(axis=1) * (b * b).sum(axis=1))


def zero_crossings(s):
    """จำนวนครั้งที่เส้นข้ามศูนย์ (ทีละแถว) — วิธีนับแบบบ้าน ๆ ว่า "กลับมาบ่อยแค่ไหน\""""
    return np.sum(np.diff(np.sign(s), axis=-1) != 0, axis=-1)


def verdict(adf, crit5):
    """ผ่าน = ปฏิเสธ random walk ที่ระดับ 5% (ค่า ADF ติดลบกว่าค่าวิกฤต)"""
    return "ผ่าน" if adf < crit5 else "ไม่ผ่าน"


def level_stats(s):
    """สถิติของสเปรดระดับ (โลก × เวลา) ที่วัดจากเส้นสเปรดอย่างเดียว"""
    sd250 = s[:, :250].std(axis=1, ddof=1)
    sd_all = s.std(axis=1, ddof=1)
    return {"adf": C.adf_stat_batch(s, lags=1), "sd250": sd250, "sd_all": sd_all, "sd_ratio": sd_all / sd250,
            "range": s.max(axis=1) - s.min(axis=1), "zero_cross": zero_crossings(s)}


def chunks(worlds):
    """แบ่ง Monte Carlo เป็นก้อนละ CHUNK โลก (ใช้ตัวสุ่มตัวเดียวต่อเนื่องกัน ผลจึงทำซ้ำได้)"""
    return [min(CHUNK, worlds - i) for i in range(0, worlds, CHUNK)]


def concat(parts):
    """ต่อผลของ Monte Carlo หลายก้อน (dict ของอาร์เรย์ที่มีแกนแรกเป็นโลก) เข้าด้วยกัน"""
    return {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}


def pctile_of(v, arr):
    """v อยู่ที่เปอร์เซ็นไทล์เท่าไรของ arr (0–1 · ค่าที่เท่ากันนับครึ่ง)"""
    arr = np.asarray(arr, float)
    return 0.5 * (np.mean(arr < v) + np.mean(arr <= v))


def typical_offset(candidates, mc_ref):
    """เลือกโลกตัวอย่างด้วยกติกาที่เขียนไว้ล่วงหน้า แทนการเลือกด้วยตา (ซึ่งมักได้โลกที่ "สวยเกินจริง")
    candidates = {offset: {ชื่อสถิติ: ค่าของโลกนั้น}} · mc_ref = {ชื่อสถิติ: ค่าจาก Monte Carlo}
    คะแนนของโลก = สถิติที่ห่างจากค่ากลางมากที่สุด (ระยะจากเปอร์เซ็นไทล์ 50) → เอาโลกที่คะแนนน้อยสุด"""
    def worst(st):
        return max(abs(pctile_of(st[k], mc_ref[k]) - 0.5) for k in mc_ref)
    best = min(candidates, key=lambda off: (worst(candidates[off]), off))
    return best, worst(candidates[best])


# ─────────────────────────────── 1a  รูปของสไลด์ 2 ───────────────────────────────
def slide_stats(a, b, crit5):
    s = a - b
    ds = np.diff(s)
    adf = C.adf_stat(s, lags=1)
    return {"spread": s, "corr_levels": float(np.corrcoef(a, b)[0, 1]),
            "corr_changes": float(np.corrcoef(np.diff(a), np.diff(b))[0, 1]),
            "spread_sd": float(s.std(ddof=1)), "spread_mean": float(s.mean()),
            "spread_min": float(s.min()), "spread_max": float(s.max()), "spread_end": float(s[-1]),
            "maxabs": float(np.abs(s).max()),
            "spread_ac1": float(np.corrcoef(s[1:], s[:-1])[0, 1]), "spread_change_sd": float(ds.std(ddof=1)),
            "zero_cross": int(zero_crossings(s)), "adf": float(adf), "adf_verdict": verdict(adf, crit5)}


def slide_world(offset, crit5):
    """A = คลื่นร่วม + Risk(A) · B = คลื่นร่วม + Risk(B) — สองแบบที่ใช้ตัวเลขสุ่มชุดเดียวกันทุกตัว
    level: Risk = e_t (noise ในระดับราคา แบบที่สไลด์วาด) · perm: Risk = e_1 + … + e_t (ข่าวถาวร)"""
    g = C.rng(offset)
    t = np.arange(SLIDE_N)
    phase = g.uniform(0.0, 2.0 * np.pi, len(SLIDE_WAVES))
    common = SLIDE_LEVEL + sum(amp * np.sin(2.0 * np.pi * t / period + ph)
                               for (amp, period), ph in zip(SLIDE_WAVES, phase))
    e = g.standard_normal((2, SLIDE_N)) * SLIDE_NOISE
    level = {"a": common + e[0], "b": common + e[1]}
    perm = {"a": common + np.cumsum(e[0]), "b": common + np.cumsum(e[1])}
    for world in (level, perm):
        world.update(slide_stats(world["a"], world["b"], crit5))
    return {"t": t, "common": common, "level": level, "perm": perm}


def slide_mc(crit5):
    """รูปสไลด์ใน WORLDS โลก — สเปรดขึ้นกับ Risk อย่างเดียว (คลื่นร่วมหักล้างกันหมด)
    ส่วน corr ของระดับราคาต้องมีคลื่นด้วย จึงสุ่มเฟสของคลื่นทีละโลก"""
    g = C.rng(OFF_SLIDE_MC)
    e = g.standard_normal((WORLDS, 2, SLIDE_N)) * SLIDE_NOISE
    t = np.arange(SLIDE_N)
    phase = g.uniform(0.0, 2.0 * np.pi, (WORLDS, len(SLIDE_WAVES)))
    common = SLIDE_LEVEL + sum(amp * np.sin(2.0 * np.pi * t / period + phase[:, [j]])
                               for j, (amp, period) in enumerate(SLIDE_WAVES))
    out = {}
    for name, risk in (("level", e), ("perm", np.cumsum(e, axis=2))):
        s = risk[:, 0] - risk[:, 1]
        adf = C.adf_stat_batch(s, lags=1)
        out[name] = {"zero_cross": zero_crossings(s), "maxabs": np.abs(s).max(axis=1), "adf": adf,
                     "reject": float(np.mean(adf < crit5)),
                     "corr_levels": row_corr(common + risk[:, 0], common + risk[:, 1])}
    return out


def exp_slide2():
    crit = C.crit_values(adf_null(SLIDE_N, 1, N_SIM_NULL, OFF_NULL_200))
    mc = slide_mc(crit[0.05])
    cands = {off: slide_world(off, crit[0.05]) for off in CAND_SLIDE}
    ref = {"level_zero_cross": mc["level"]["zero_cross"], "perm_zero_cross": mc["perm"]["zero_cross"],
           "perm_maxabs": mc["perm"]["maxabs"]}
    stats = {off: {"level_zero_cross": w["level"]["zero_cross"], "perm_zero_cross": w["perm"]["zero_cross"],
                   "perm_maxabs": w["perm"]["maxabs"]} for off, w in cands.items()}
    off, dev = typical_offset(stats, ref)
    out = dict(cands[off])
    out.update({"crit": crit, "mc": mc, "offset": off, "dev": dev})
    return out


# ─────────────────────────────── 1b  เป็นกลางต่อตลาด ≠ กลับสู่ค่าเฉลี่ย ───────────────────────────────
def neutral_world(g, worlds):
    """ราคา (log) ของ A, B ในโลก T และโลก P — ปัจจัยร่วมเส้นเดียวกันทั้งสองโลก loading = 1 ทุกตัว"""
    f = g.standard_normal((worlds, N_BARS, 3)) * FACTOR_SD
    common = np.cumsum(f.sum(axis=2), axis=1)[:, None, :]
    idio_t = C.ar1_batch(worlds * 2, N_BARS, HALF_LIFE, SIGMA_EQ, g).reshape(worlds, 2, N_BARS)
    idio_p = np.cumsum(g.standard_normal((worlds, 2, N_BARS)) * IDIO_CHANGE_SD, axis=2)
    return {"market": f[:, :, 0], "t": {"price": common + idio_t, "idio": idio_t},
            "p": {"price": common + idio_p, "idio": idio_p}}


def neutral_stats(price, idio, market, keep_path=False):
    a, b = price[:, 0], price[:, 1]
    s = a - b
    ds, da, db, m = np.diff(s, axis=1), np.diff(a, axis=1), np.diff(b, axis=1), market[:, 1:]
    out = level_stats(s)
    out.update({"idio_change_sd": np.diff(idio, axis=2).std(axis=2, ddof=1).mean(axis=1),
                "spread_change_sd": ds.std(axis=1, ddof=1), "corr_ab_returns": row_corr(da, db),
                "corr_a_mkt": row_corr(da, m), "corr_spread_mkt": row_corr(ds, m),
                "vr20": np.array([C.variance_ratio(row, VR_Q) for row in s]),
                "min": s.min(axis=1), "max": s.max(axis=1), "end": s[:, -1], "absend": np.abs(s[:, -1])})
    if keep_path:
        out.update({"spread": s, "a": a, "b": b})
    return out


def neutral_both(w, keep_path=False):
    return {k: neutral_stats(w[k]["price"], w[k]["idio"], w["market"], keep_path) for k in ("t", "p")}


# สถิติที่ใช้เลือกโลกตัวอย่างของ 1b: ทุกตัวที่กราฟและข้อความจะหยิบไปพูดถึง
DEMO_STATS_NEUTRAL = (tuple(("t", s) for s in ("adf", "sd_ratio", "vr20", "corr_spread_mkt"))
                      + tuple(("p", s) for s in ("adf", "sd_ratio", "vr20", "corr_spread_mkt", "absend", "zero_cross")))


def exp_neutral():
    null = adf_null(N_BARS, 1, N_SIM_NULL, OFF_NULL_1000)
    crit = C.crit_values(null)
    g = C.rng(OFF_NEUTRAL_MC)
    parts = [neutral_both(neutral_world(g, n)) for n in chunks(WORLDS)]
    mc = {k: concat([p[k] for p in parts]) for k in ("t", "p")}
    for k in ("t", "p"):
        mc[k]["reject"] = float(np.mean(mc[k]["adf"] < crit[0.05]))
    cands = {off: neutral_both(neutral_world(C.rng(off), 1), keep_path=True) for off in CAND_NEUTRAL}
    off, dev = typical_offset({o: {f"{k}_{s}": float(c[k][s][0]) for k, s in DEMO_STATS_NEUTRAL}
                               for o, c in cands.items()},
                              {f"{k}_{s}": mc[k][s] for k, s in DEMO_STATS_NEUTRAL})
    demo = cands[off]
    for k in ("t", "p"):
        demo[k]["adf_p"] = C.p_value(float(demo[k]["adf"][0]), null)
        demo[k]["hl_fit"] = C.fit_ar1(demo[k]["spread"][0])["half_life"]
    return {"crit": crit, "demo": demo, "mc": mc, "offset": off, "dev": dev}


# ─────────────────────────────── ตัวอย่างคิดมือ: ผลตอบแทนหนึ่งวัน ───────────────────────────────
def exp_walkthrough():
    """ผลตอบแทน (%) หนึ่งวันของ A, B, C, D และของสเปรดสามแบบ แยกเป็น ปัจจัย × loading ทีละตัว"""
    f = np.array(WALK_F)
    keys = ("a", "b", "c", "d")
    asset = {k: {"parts": np.array(LOAD[k]) * f, "idio": WALK_IDIO[k]} for k in keys}
    for k in keys:
        asset[k]["total"] = float(asset[k]["parts"].sum() + asset[k]["idio"])
    idio_hedge = np.array([WALK_IDIO[k] for k in ("b", "c", "d")])
    ret_hedge = np.array([asset[k]["total"] for k in ("b", "c", "d")])

    def spread(w):
        w = np.asarray(w, float)
        parts = (L_A - w @ L_HEDGE) * f
        idio = WALK_IDIO["a"] - float(w @ idio_hedge)
        return {"w": w, "parts": parts, "idio": idio, "factor": float(parts.sum()),
                "total": float(parts.sum() + idio), "legs": w * ret_hedge, "hedge_ret": float(w @ ret_hedge)}

    fixed = fixed_weights()
    equal_a, equal_b = float(f.sum() + WALK_IDIO["a"]), float(f.sum() + WALK_IDIO["b"])
    return {"f": f, "asset": asset, "ab": spread(fixed["ab"]), "beta_mkt": spread(fixed["beta_mkt"]),
            "three": spread(fixed["three_true"]),
            "equal": {"a_total": equal_a, "b_total": equal_b, "spread": equal_a - equal_b}}


# ─────────────────────────────── 1c  loading ไม่เท่ากัน ───────────────────────────────
def unequal_world(g, worlds):
    """ราคา (log) ของ A, B, C, D ยาว train + test แท่ง — เรื่องเฉพาะตัวของทุกตัวเป็นข่าวชั่วคราว"""
    n = N_TRAIN + N_BARS
    f = g.standard_normal((worlds, n, 3)) * FACTOR_SD
    idio = C.ar1_batch(worlds * 4, n, HALF_LIFE, SIGMA_EQ, g).reshape(worlds, 4, n)
    loads = np.vstack([L_A, L_HEDGE])
    price = np.einsum("wtk,ak->wat", np.cumsum(f, axis=1), loads) + idio
    return {"f": f, "idio": idio, "price": price}


def fixed_weights():
    """น้ำหนัก (ของ B, C, D) ที่คิดจาก loading จริง — รู้ได้เพราะเราสร้างโลกนี้เอง"""
    lb, lc = L_HEDGE[0], L_HEDGE[1]
    two = np.linalg.solve(np.array([lb[:2], lc[:2]]).T, L_A[:2])       # B, C ตัด Market กับ Size พอดี
    three = np.linalg.solve(L_HEDGE.T, L_A)                           # B, C, D ตัดครบสามปัจจัย
    return {"ab": np.array([1.0, 0.0, 0.0]), "beta_mkt": np.array([L_A[0] / lb[0], 0.0, 0.0]),
            "two": np.array([two[0], two[1], 0.0]), "three_true": three}


def population_weights(legs):
    """น้ำหนักที่ regression ของ "ผลตอบแทน" เข้าหาเมื่อข้อมูลยาวไม่สิ้นสุด (คิดจากสูตรของแบบจำลอง)
    = Cov(ผลตอบแทนของตัวช่วย)⁻¹ · Cov(ตัวช่วย, A) · ความแปรปรวนของการขยับรายวันของเรื่องเฉพาะตัว
    ของตัวช่วยอยู่ในตัวหารด้วย น้ำหนักจึงต่ำกว่าค่าที่ตัดปัจจัยได้พอดีเสมอ (attenuation) — ไม่ใช่ noise จากการสุ่ม"""
    lh, var_f = L_HEDGE[list(legs)], np.diag(FACTOR_SD ** 2)
    cov_h = lh @ var_f @ lh.T + IDIO_CHANGE_SD ** 2 * np.eye(len(legs))
    w = np.zeros(3)
    w[list(legs)] = np.linalg.solve(cov_h, lh @ var_f @ L_A)
    return w


def estimated_weights(world):
    """น้ำหนักที่ประมาณจากช่วง train เท่านั้น (ไม่เห็นช่วง test)
    beta_ols / three_est = regression ของ "ผลตอบแทน" · beta_lvl / three_lvl = regression ของ "ระดับ log price\""""
    price = world["price"][:, :, :N_TRAIN]
    ret = np.diff(price, axis=2)
    out = {k: np.zeros((len(price), 3)) for k in ESTIMATED}
    for i in range(len(price)):
        out["beta_ols"][i, 0] = C.ols(ret[i, 0], ret[i, 1:2].T)["coef"][1]
        out["beta_lvl"][i, 0] = C.ols(price[i, 0], price[i, 1:2].T)["coef"][1]
        out["three_est"][i] = C.ols(ret[i, 0], ret[i, 1:].T)["coef"][1:]
        out["three_lvl"][i] = C.ols(price[i, 0], price[i, 1:].T)["coef"][1:]
    return out


def all_weights(world):
    worlds = len(world["price"])
    out = {k: np.tile(v, (worlds, 1)) for k, v in fixed_weights().items()}
    out.update(estimated_weights(world))
    return out


def horizon_ms(lvl):
    """ค่าเฉลี่ยกำลังสองของ "การเปลี่ยนแปลง h แท่ง" (ทีละโลก) สำหรับทุก h ใน HORIZONS"""
    return np.column_stack([np.mean((lvl[:, h:] - lvl[:, :-h]) ** 2, axis=1) for h in HORIZONS])


def evaluate(world, w, crit5, crit5_alt, keep_path=False):
    """วัดสเปรด A − w·(B, C, D) ในช่วง test · แยกผลตอบแทนของสเปรดเป็น 3 ปัจจัย + เรื่องเฉพาะตัว
    (แยกได้เพราะรู้เฉลย: ส่วนของปัจจัย k = loading ที่เหลือ × ผลตอบแทนของปัจจัย k)"""
    f, idio, price = world["f"][:, N_TRAIN:], world["idio"][:, :, N_TRAIN:], world["price"][:, :, N_TRAIN:]
    left = L_A - w @ L_HEDGE
    s = price[:, 0] - np.einsum("wj,wjt->wt", w, price[:, 1:])
    fac_ret = f * left[:, None, :]
    idio_lvl = idio[:, 0] - np.einsum("wj,wjt->wt", w, idio[:, 1:])
    fac_lvl = np.cumsum(fac_ret.sum(axis=2), axis=1)
    # ความแปรปรวนรายวันของแต่ละส่วน (ไม่รวม covariance ข้ามส่วน ซึ่งเป็นศูนย์ตามแบบจำลอง)
    comp_var = np.column_stack([fac_ret[:, 1:, k].var(axis=1, ddof=1) for k in range(3)]
                               + [np.diff(idio_lvl, axis=1).var(axis=1, ddof=1)])
    ds = np.diff(s, axis=1)
    out = level_stats(s)
    adf_alt = C.adf_stat_batch(s, lags=ADF_LAGS_ALT)
    out.update({"w": w, "left": left, "comp_var": comp_var,
                "share": comp_var / comp_var.sum(axis=1, keepdims=True),
                "left_sd": np.sqrt((left ** 2 * FACTOR_SD ** 2).sum(axis=1)),
                "corr_mkt": row_corr(ds, f[:, 1:, 0]), "daily_sd": ds.std(axis=1, ddof=1),
                "pass": out["adf"] < crit5, "pass_alt": adf_alt < crit5_alt,
                "hz_vf": horizon_ms(fac_lvl), "hz_vi": horizon_ms(idio_lvl),
                "chg250_ms": np.mean((s[:, 250:] - s[:, :-250]) ** 2, axis=1)})
    if keep_path:
        full = world["price"][:, 0] - np.einsum("wj,wjt->wt", w, world["price"][:, 1:])
        out["full"] = full - full[:, :N_TRAIN].mean(axis=1, keepdims=True)   # วัดจากค่าเฉลี่ยช่วง train เท่านั้น
    return out


def evaluate_all(world, crit5, crit5_alt, keep_path=False):
    weights = all_weights(world)
    return {k: evaluate(world, weights[k], crit5, crit5_alt, keep_path) for k in CONSTRUCTIONS}


def theory(w):
    """ค่าตามสูตรของแบบจำลองสำหรับน้ำหนัก w (ไม่มีการสุ่ม): ส่วนแบ่งของปัจจัยตามระยะถือ h
    — ปัจจัยที่เหลือสะสมตาม h · เรื่องเฉพาะตัว (AR(1)) อิ่มตัวที่ 2σ²(1−φ^h) ต่อขา"""
    left = L_A - w @ L_HEDGE
    vf1 = float((left ** 2 * FACTOR_SD ** 2).sum())

    def var_parts(h):
        return h * vf1, 2.0 * SIGMA_EQ ** 2 * (1.0 - PHI ** h) * (1.0 + float((w ** 2).sum()))

    share = {h: var_parts(h)[0] / sum(var_parts(h)) for h in HORIZONS}
    return {"w": w, "left": left, "left_sd": np.sqrt(vf1), "share": share, "chg250_sd": np.sqrt(sum(var_parts(250)))}


def one_beta_table(beta_pop):
    """β ตัวเดียวกับสินทรัพย์ B: β แต่ละค่าเหลือ loading เท่าไรในแต่ละปัจจัย (คิดจาก loading จริง)"""
    lb, var = L_HEDGE[0], FACTOR_SD ** 2
    best = float((L_A * lb * var).sum() / (lb * lb * var).sum())      # β ที่ทำให้ปัจจัยที่เหลือผันผวนน้อยสุด
    rows = (("b1", 1.0), ("kill_m", L_A[0] / lb[0]), ("kill_s", L_A[1] / lb[1]), ("kill_g", L_A[2] / lb[2]),
            ("best", best), ("ols", beta_pop))
    out = {}
    for key, beta in rows:
        left = L_A - beta * lb
        out[key] = {"beta": float(beta), "left": left, "left_sd": float(np.sqrt((left ** 2 * var).sum()))}
    out["a_alone_sd"] = float(np.sqrt((L_A ** 2 * var).sum()))
    return out


def two_hedge_best():
    """ตัวช่วยสองตัว (B, C) ที่ "ดีที่สุดเท่าที่ทำได้": น้ำหนักที่ทำให้ปัจจัยที่เหลือผันผวนน้อยสุด
    (weighted least squares ของ loading โดยถ่วงด้วยความแปรปรวนของปัจจัย) — ยังไงก็ไม่เป็นศูนย์"""
    x, var = L_HEDGE[:2].T, FACTOR_SD ** 2                   # 3 ปัจจัย × 2 ตัวช่วย
    w = np.linalg.solve(x.T @ (x * var[:, None]), x.T @ (L_A * var))
    left = L_A - x @ w
    return {"w": w, "left": left, "left_sd": float(np.sqrt((left ** 2 * var).sum()))}


# สถิติที่ใช้เลือกโลกตัวอย่างของ 1c: สิ่งที่กราฟและข้อความจะหยิบไปพูดถึง
DEMO_STATS_UNEQUAL = (("ab", "adf"), ("ab", "sd_all"), ("ab", "sd_ratio"), ("ab", "corr_mkt"),
                      ("beta_ols", "sd_all"), ("beta_ols", "w_b"), ("three_est", "sd_all"), ("three_est", "w_d"),
                      ("three_true", "sd_all"), ("three_true", "sd_ratio"), ("three_true", "corr_mkt"))


def _stat(r, name):
    return r["w"][:, {"w_b": 0, "w_c": 1, "w_d": 2}[name]] if name.startswith("w_") else r[name]


def exp_unequal():
    crit5 = C.crit_values(adf_null(N_BARS, 1, N_SIM_NULL, OFF_NULL_1000))[0.05]
    crit5_alt = C.crit_values(adf_null(N_BARS, ADF_LAGS_ALT, N_SIM_NULL_ALT, OFF_NULL_ALT))[0.05]
    g = C.rng(OFF_UNEQUAL_MC)
    parts = [evaluate_all(unequal_world(g, n), crit5, crit5_alt) for n in chunks(WORLDS)]
    mc = {k: concat([p[k] for p in parts]) for k in CONSTRUCTIONS}
    for r in mc.values():
        vf, vi = r["hz_vf"].mean(axis=0), r["hz_vi"].mean(axis=0)
        r["hz_share"] = vf / (vf + vi)                         # รวมทุกโลก ทุกจุดเริ่ม
        r["share_pooled"] = r["comp_var"].mean(axis=0) / r["comp_var"].mean(axis=0).sum()
        r["chg250_sd"] = float(np.sqrt(r["chg250_ms"].mean()))
        r["reject"], r["reject_alt"] = float(r["pass"].mean()), float(r["pass_alt"].mean())
    cands = {off: evaluate_all(unequal_world(C.rng(off), 1), crit5, crit5_alt, keep_path=True)
             for off in CAND_UNEQUAL}
    off, dev = typical_offset({o: {f"{k}_{s}": float(_stat(c[k], s)[0]) for k, s in DEMO_STATS_UNEQUAL}
                               for o, c in cands.items()},
                              {f"{k}_{s}": _stat(mc[k], s) for k, s in DEMO_STATS_UNEQUAL})
    theo = {k: theory(w) for k, w in fixed_weights().items()}
    theo.update({k: theory(population_weights(legs)) for k, legs in RETURN_REG.items()})
    return {"crit5": crit5, "fixed": fixed_weights(), "cond": float(np.linalg.cond(L_HEDGE)),
            "demo": cands[off], "mc": mc, "theory": theo, "offset": off, "dev": dev,
            "onebeta": one_beta_table(float(theo["beta_ols"]["w"][0])), "two_best": two_hedge_best()}


# ─────────────────────────────── run / figures ───────────────────────────────
@functools.lru_cache(maxsize=1)
def run():
    """คำนวณทุกการทดลอง (ผลเหมือนเดิมทุกครั้ง เพราะ seed ตายตัว)"""
    return {"slide2": exp_slide2(), "neutral": exp_neutral(), "walk": exp_walkthrough(), "unequal": exp_unequal()}


def ipct(v):
    """สัดส่วน → เปอร์เซ็นต์จำนวนเต็ม (ใช้กับตัวเลข Monte Carlo ที่แม่นได้ราว ±1 จุด)"""
    return int(round(100.0 * float(v)))


def _mc3(prefix, arr, d=2, scale=1.0, suffix=""):
    """ค่ากลาง + ช่วง 5–95% ของ Monte Carlo เป็นสามคีย์ <prefix>_med/_p5/_p95<suffix> (d = None → จำนวนเต็ม)"""
    vals = np.percentile(np.asarray(arr, float) * scale, [50, 5, 95])
    fmt = (lambda v: int(round(float(v)))) if d is None else (lambda v: C.rd(v, d))
    return {f"{prefix}_{q}{suffix}": fmt(v) for q, v in zip(("med", "p5", "p95"), vals)}


def _demo_info(res, candidates):
    return {"demo_offset": str(res["offset"]), "demo_candidates": f"{candidates[0]}-{candidates[-1]}",
            "demo_max_dev_pct": ipct(res["dev"])}


def _fig_slide(st):
    return {"corr_levels": C.rd(st["corr_levels"], 2), "corr_changes": C.rd(st["corr_changes"], 2),
            "spread_sd": C.rd(st["spread_sd"], 2), "spread_mean": C.rd(st["spread_mean"], 2),
            "spread_min": C.rd(st["spread_min"], 1), "spread_max": C.rd(st["spread_max"], 1),
            "spread_end": C.rd(st["spread_end"], 1), "maxabs": C.rd(st["maxabs"], 1),
            "spread_ac1": C.rd(st["spread_ac1"], 2),
            "spread_change_sd": C.rd(st["spread_change_sd"], 2), "zero_cross": st["zero_cross"],
            "adf": C.rd(st["adf"], 2), "adf_verdict": st["adf_verdict"]}


def _fig_slide_mc(m):
    out = {"reject_pct": ipct(m["reject"]), "maxabs_med": C.rd(np.median(m["maxabs"]), 0)}
    out.update(_mc3("zero_cross", m["zero_cross"], None))
    out.update(_mc3("corr_levels", m["corr_levels"], 2))
    return out


def _fig_neutral_demo(d, crit5):
    adf = float(d["adf"][0])
    p = d["adf_p"]
    hl = d["hl_fit"]
    return {"idio_change_sd_pct": C.pct(d["idio_change_sd"][0], 2),
            "spread_change_sd_pct": C.pct(d["spread_change_sd"][0], 2),
            "corr_ab_returns": C.rd(d["corr_ab_returns"][0], 2), "corr_a_mkt": C.rd(d["corr_a_mkt"][0], 2),
            "corr_spread_mkt": C.rd(d["corr_spread_mkt"][0], 2),
            "adf": C.rd(adf, 2), "adf_verdict": verdict(adf, crit5),
            # p = 0 จากการจำลองแปลว่า "น้อยกว่า 1/จำนวนโลก" ไม่ใช่ศูนย์จริง
            "adf_p": C.rd(p, 3) if p > 0 else f"< {1.0 / N_SIM_NULL:.5f}",
            "sd_first250_pct": C.pct(d["sd250"][0], 1), "sd_all_pct": C.pct(d["sd_all"][0], 1),
            "sd_ratio": C.rd(d["sd_ratio"][0], 2), "vr20": C.rd(d["vr20"][0], 2),
            "range_pct": C.pct(d["range"][0], 1), "min_pct": C.pct(d["min"][0], 1),
            "max_pct": C.pct(d["max"][0], 1), "end_pct": C.pct(d["end"][0], 1),
            "zero_cross": int(d["zero_cross"][0]),
            # half-life ของโลก P ไม่มีความหมาย (ADF ไม่ผ่าน) เก็บไว้ให้เห็นว่า random walk ก็ให้เลขจำกัดได้
            "hl_fit_bars": int(round(hl)) if np.isfinite(hl) else "inf"}


def _fig_neutral_mc(m):
    out = {"reject_pct": ipct(m["reject"]), "corr_ab_returns_med": C.rd(np.median(m["corr_ab_returns"]), 2)}
    out.update(_mc3("adf", m["adf"], 1))
    out.update(_mc3("corr_spread_mkt", m["corr_spread_mkt"], 2))
    out.update(_mc3("sd_ratio", m["sd_ratio"], 1))
    out.update(_mc3("sd_all", m["sd_all"], None, 100.0, "_pct"))
    out["range_med_pct"] = int(round(100.0 * float(np.median(m["range"]))))   # หางของช่วงกว้างแกว่งเกินจะพิมพ์
    out.update(_mc3("vr20", m["vr20"], 2))
    out.update(_mc3("zero_cross", m["zero_cross"], None))
    return out


def _fig_theory(t, with_weights):
    out = {f"factor_h{h}_pct": C.pct(t["share"][h], 1) for h in (1, 20, 250)}
    out.update({"chg250_sd_pct": C.pct(t["chg250_sd"], 1), "left_sd_day_pct": C.pct(t["left_sd"], 2)})
    if with_weights:
        out.update({f"w_{leg}": C.rd(t["w"][j], 3) for j, leg in enumerate(("b", "c", "d"))})
        out.update({f"left_{fac}": C.rd(t["left"][j], 3) for j, fac in enumerate(FACTORS)})
    return out


def _fig_construction(key, demo, mc, theo, crit5):
    w, left, share = demo["w"][0], demo["left"][0], demo["share"][0]
    adf = float(demo["adf"][0])
    d_left = 3 if key in ESTIMATED else 4                    # ค่าที่คิดจาก loading จริงเก็บครบทศนิยม
    out = {"w_b": C.rd(w[0], 3), "w_c": C.rd(w[1], 3), "w_d": C.rd(w[2], 3), "gross": C.rd(1.0 + np.abs(w).sum(), 3),
           "left_m": C.rd(left[0], d_left), "left_s": C.rd(left[1], d_left), "left_g": C.rd(left[2], d_left),
           "left_sd_day_pct": C.pct(demo["left_sd"][0], 2),
           "share_m_pct": C.pct(share[0], 1), "share_s_pct": C.pct(share[1], 1), "share_g_pct": C.pct(share[2], 1),
           "share_idio_pct": C.pct(share[3], 1), "share_factor_pct": C.pct(share[:3].sum(), 1),
           "corr_mkt": C.rd(demo["corr_mkt"][0], 2), "daily_sd_pct": C.pct(demo["daily_sd"][0], 2),
           "adf": C.rd(adf, 2), "adf_verdict": verdict(adf, crit5),
           "sd_first250_pct": C.pct(demo["sd250"][0], 1), "sd_all_pct": C.pct(demo["sd_all"][0], 1),
           "sd_ratio": C.rd(demo["sd_ratio"][0], 2), "range_pct": C.pct(demo["range"][0], 1)}
    if theo is not None:
        out["theory"] = _fig_theory(theo, key in RETURN_REG)
    sp = mc["share_pooled"]
    m = {"reject_pct": ipct(mc["reject"]), "reject_lags10_pct": ipct(mc["reject_alt"]),
         "adf_med": C.rd(np.median(mc["adf"]), 1), "corr_mkt_med": C.rd(np.median(mc["corr_mkt"]), 2),
         "chg250_sd_pct": C.pct(mc["chg250_sd"], 1),
         "share_m_pct": ipct(sp[0]), "share_s_pct": ipct(sp[1]), "share_g_pct": ipct(sp[2]),
         "share_idio_pct": ipct(sp[3]), "share_factor_pct": ipct(sp[:3].sum())}
    m.update(_mc3("sd_ratio", mc["sd_ratio"], 1))
    m.update({f"hz_h{h}_pct": ipct(v) for h, v in zip(HORIZONS, mc["hz_share"])})
    if key in ESTIMATED:
        dw = 1 if key == "beta_lvl" else 2                   # β จาก regression ระดับ (ไม่มีสายจูง) กระจายกว้างมาก
        for j, leg in enumerate(("b", "c", "d")):
            if key.startswith("three") or j == 0:
                m.update(_mc3(f"w_{leg}", mc["w"][:, j], dw))
        for j, fac in enumerate(FACTORS):
            m[f"left_{fac}_med"] = C.rd(np.median(mc["left"][:, j]), dw)
    out["mc"] = m
    return out


def _fig_walk(wk):
    def parts(d):
        return {"m": C.rd(d["parts"][0], 4), "s": C.rd(d["parts"][1], 4), "g": C.rd(d["parts"][2], 4),
                "idio": C.rd(d["idio"], 4), "total": C.rd(d["total"], 4)}

    def spread(d):
        o = parts(d)
        o.update({"factor": C.rd(d["factor"], 4), "hedge_ret": C.rd(d["hedge_ret"], 4),
                  "w_b": C.rd(d["w"][0], 3), "w_c": C.rd(d["w"][1], 3), "w_d": C.rd(d["w"][2], 3),
                  "leg_b": C.rd(d["legs"][0], 4), "leg_c": C.rd(d["legs"][1], 4), "leg_d": C.rd(d["legs"][2], 4),
                  "factor_share_pct": ipct(d["factor"] / d["total"])})
        return o

    out = {"day": {"m_pct": C.rd(wk["f"][0], 2), "s_pct": C.rd(wk["f"][1], 2), "g_pct": C.rd(wk["f"][2], 2)}}
    out.update({k: parts(wk["asset"][k]) for k in ("a", "b", "c", "d")})
    out.update({k: spread(wk[k]) for k in ("ab", "beta_mkt", "three")})
    out["equal"] = {k: C.rd(v, 4) for k, v in wk["equal"].items()}
    return out


def _about():
    return {
        "data": "ข้อมูลจำลองทั้งหมด สร้างจากตัวสุ่มที่ทำซ้ำได้ โลกตัวอย่างที่ใช้วาดกราฟเลือกด้วยกติกาในโค้ด ไม่ได้เลือกด้วยตา "
                "คือเอาโลกผู้สมัครที่สถิติสำคัญทุกตัวอยู่ใกล้ค่ากลางของ Monte Carlo ที่สุด "
                "(demo_max_dev_pct บอกว่าห่างจากเปอร์เซ็นไทล์ที่ 50 ไม่เกินกี่จุด) ข้อสรุปทั่วไปให้ดูจาก Monte Carlo",
        "slide2": f"จำลองรูปสไลด์ 2 จำนวน {SLIDE_N} แท่ง: คลื่นร่วมสามลูก (Market, Size, Growth) "
                  f"บวก Risk ที่เป็น noise ในระดับราคา sd {SLIDE_NOISE:g} หน่วย แบบข่าวถาวรใช้ตัวเลขสุ่มชุดเดียวกันแต่บวกสะสม "
                  f"Monte Carlo {WORLDS:,} โลก",
        "neutral": f"สองโลก {N_BARS:,} แท่ง ปัจจัยรายวัน Market 1.0% Size 0.5% Growth 0.6% loading เท่ากับ 1 ทุกตัว "
                   f"โลก T เรื่องเฉพาะตัวเป็น AR(1) half-life {HALF_LIFE:g} แท่ง σ {SIGMA_EQ * 100:g}% "
                   f"โลก P เป็น random walk ที่ผันผวนต่อวันเท่ากัน ({IDIO_CHANGE_SD * 100:.2f}%) Monte Carlo {WORLDS:,} โลก",
        "unequal": f"สินทรัพย์ A, B, C, D ที่ loading ไม่เท่ากัน เรื่องเฉพาะตัวเป็นข่าวชั่วคราวทุกตัว (แบบโลก T) "
                   f"ประมาณน้ำหนักจาก {N_TRAIN} แท่งแรก แล้ววัดผลใน {N_BARS:,} แท่งถัดไป Monte Carlo {WORLDS:,} โลก "
                   f"สเปรดวัดต่อ A 1 หน่วย ไม่มีต้นทุน ไม่มีการเทรด",
        "adf": f"ADF ใช้ lags 1 มีค่าคงที่ ค่าวิกฤตมาจากการจำลอง random walk {N_SIM_NULL:,} เส้นที่ความยาวเท่ากัน "
               f"ส่วนสัดส่วนที่ lags {ADF_LAGS_ALT} ใช้ {N_SIM_NULL_ALT:,} เส้น",
        "precision": f"ตัวเลข Monte Carlo ปัดตามความแม่นที่วัดได้ (รันซ้ำด้วย seed อื่นแล้วหลักสุดท้ายขยับราว ±1) "
                     f"สัดส่วนโลกที่ ADF ผ่านและส่วนแบ่งของปัจจัยเป็นจำนวนเต็ม % และสัดส่วนโลกคลาดมาตรฐานไม่เกิน {MC_SE_PCT} จุด "
                     f"จึงควรเขียนนำด้วยคำว่า “ราว” · ค่า theory คิดจากสูตรจึงไม่มีความคลาดจากการสุ่ม",

        "walk": "ตัวอย่างคิดมือหนึ่งวัน ตัวเลขตั้งขึ้นให้คิดง่าย ไม่ได้มาจากการสุ่ม",
        "shares": "ส่วนแบ่งความแปรปรวนรายวันแยกผลตอบแทนของสเปรดเป็นสามปัจจัยกับเรื่องเฉพาะตัว ซึ่งทำได้เพราะรู้เฉลยของข้อมูลจำลอง "
                  "ชั้นบนคือโลกตัวอย่าง mc คือรวมทุกโลก hz คือส่วนแบ่งของปัจจัยในการเปลี่ยนแปลง h แท่ง",
    }


def figures(res=None):
    res = res or run()
    sl, ne, un = res["slide2"], res["neutral"], res["unequal"]
    crit5 = un["crit5"]
    slide2 = {"n_bars": SLIDE_N, "noise_sd": C.rd(SLIDE_NOISE, 1), "adf_crit5": C.rd(sl["crit"][0.05], 2),
              "n_sim_null": N_SIM_NULL, "worlds": WORLDS, "mc_se_pct": MC_SE_PCT,
              "level": _fig_slide(sl["level"]), "perm": _fig_slide(sl["perm"]),
              "mc": {"level": _fig_slide_mc(sl["mc"]["level"]), "perm": _fig_slide_mc(sl["mc"]["perm"])}}
    slide2.update(_demo_info(sl, CAND_SLIDE))
    neutral = {"n_bars": N_BARS, "worlds": WORLDS, "mc_se_pct": MC_SE_PCT, "n_sim_null": N_SIM_NULL, "vr_q": VR_Q,
               "half_life_bars": C.rd(HALF_LIFE, 1), "sigma_eq_pct": C.pct(SIGMA_EQ, 1),
               "idio_change_sd_pct": C.pct(IDIO_CHANGE_SD, 2),
               "factor_sd_pct": {k: C.pct(v, 1) for k, v in zip(FACTORS, FACTOR_SD)},
               "adf_crit5": C.rd(ne["crit"][0.05], 2), "adf_crit1": C.rd(ne["crit"][0.01], 2),
               "t": _fig_neutral_demo(ne["demo"]["t"], ne["crit"][0.05]),
               "p": _fig_neutral_demo(ne["demo"]["p"], ne["crit"][0.05]),
               "mc": {"t": _fig_neutral_mc(ne["mc"]["t"]), "p": _fig_neutral_mc(ne["mc"]["p"])}}
    neutral.update(_demo_info(ne, CAND_NEUTRAL))
    onebeta = {k: {"beta": C.rd(v["beta"], 3), "left_m": C.rd(v["left"][0], 4), "left_s": C.rd(v["left"][1], 4),
                   "left_g": C.rd(v["left"][2], 4), "left_sd_day_pct": C.pct(v["left_sd"], 2)}
               for k, v in un["onebeta"].items() if k != "a_alone_sd"}
    onebeta["a_alone_sd_day_pct"] = C.pct(un["onebeta"]["a_alone_sd"], 2)
    tb = un["two_best"]
    unequal = {"n_train": N_TRAIN, "n_test": N_BARS, "worlds": WORLDS, "mc_se_pct": MC_SE_PCT, "adf_crit5": C.rd(crit5, 2),
               "adf_lags_alt": ADF_LAGS_ALT, "cond_bcd": C.rd(un["cond"], 1),
               "idio_change_sd_pct": C.pct(IDIO_CHANGE_SD, 2),
               "load": {a: dict(zip(FACTORS, (C.rd(x, 1) for x in LOAD[a]))) for a in ("a", "b", "c", "d")},
               "onebeta": onebeta,
               "two_best": {"w_b": C.rd(tb["w"][0], 3), "w_c": C.rd(tb["w"][1], 3),
                            "left_m": C.rd(tb["left"][0], 3), "left_s": C.rd(tb["left"][1], 3),
                            "left_g": C.rd(tb["left"][2], 3), "left_sd_day_pct": C.pct(tb["left_sd"], 2)}}
    unequal.update(_demo_info(un, CAND_UNEQUAL))
    for k in CONSTRUCTIONS:
        unequal[k] = _fig_construction(k, un["demo"][k], un["mc"][k], un["theory"].get(k), crit5)
    return {"about": _about(), "slide2": slide2, "neutral": neutral, "walk": _fig_walk(res["walk"]),
            "unequal": unequal}


# ─────────────────────────────── charts ───────────────────────────────
def _n(v, d=None):
    """ตัวเลขสำหรับคำบรรยายใต้รูป (เครื่องหมายลบแบบ U+2212)"""
    return V.minus(f"{v:,.{d}f}" if d is not None else f"{v:,}" if isinstance(v, int) else f"{v}")


def _chart_slide2(sl, fg):
    lv, f, m = sl["level"], fg["slide2"]["level"], fg["slide2"]["mc"]["level"]
    lim = V.auto_lim(lv["a"], lv["b"], n=4)                  # A กับ B ใช้สเกลเดียวกัน จะได้เห็นว่าเป็นคลื่นลูกเดียวกัน
    panels = [{"y": lv["a"], "title": "Asset A", "sub": "คลื่นร่วม + Risk(A)", "color": V.BLUE, "ylim": lim},
              {"y": lv["b"], "title": "Asset B", "sub": "คลื่นร่วม + Risk(B)", "color": V.AMBER, "ylim": lim},
              {"y": lv["spread"], "title": "Spread = A − B", "sub": "เหลือแค่ Risk(A) − Risk(B)",
               "color": V.GREEN, "zero": True}]
    cap = (f"ข้อมูลจำลอง {SLIDE_N} แท่ง · A กับ B ขี่คลื่นลูกเดียวกัน (correlation ของระดับราคา "
           f"{_n(f['corr_levels'])}) ส่วน A − B แกว่งรอบเส้นศูนย์ด้วย sd {_n(f['spread_sd'])} หน่วย "
           f"และข้ามเส้นศูนย์ {f['zero_cross']} ครั้ง (ค่ากลางของ {_n(WORLDS)} โลกจำลอง: {m['zero_cross_med']} ครั้ง) "
           f"· รูปออกมาสวยแบบนี้เพราะเรา<b>สุ่ม Risk เป็น noise ในระดับราคา</b> — ไม่ใช่เพราะ A − B ต้องเป็นแบบนี้เสมอ")
    return V.stacked_panels("sas-p1-slide2", panels,
                            "ราคาจำลองของ A และ B ที่เคลื่อนตามคลื่นร่วมลูกเดียวกัน และสเปรด A ลบ B ที่แกว่งรอบศูนย์",
                            cap, x=sl["t"], xticks=[0, 50, 100, 150, 200], xlabel="แท่งที่")


def _chart_slide2_perm(sl, fg):
    lv, pm = sl["level"], sl["perm"]
    f, fl, m = fg["slide2"]["perm"], fg["slide2"]["level"], fg["slide2"]["mc"]
    far = max(f["spread_min"], f["spread_max"], key=abs)
    lim = V.auto_lim(pm["a"], pm["b"], n=4)
    panels = [{"y": pm["a"], "title": "Asset A", "sub": "คลื่นร่วม + Risk(A) ที่สะสม", "color": V.BLUE, "ylim": lim},
              {"y": pm["b"], "title": "Asset B", "sub": "คลื่นร่วม + Risk(B) ที่สะสม", "color": V.AMBER, "ylim": lim},
              {"y": [pm["spread"], lv["spread"]], "title": "Spread = A − B", "color": [V.RED, V.GREEN],
               "names": ["Risk เป็นข่าวถาวร", "Risk แบบสไลด์ (รูปก่อนหน้า)"], "zero": True}]
    cap = (f"ข้อมูลจำลอง · ตัวเลขสุ่ม<b>ชุดเดียวกับรูปก่อนหน้าทุกตัว</b> เปลี่ยนบรรทัดเดียวคือเอา Risk ไปบวกสะสม (ข่าวที่ไม่หายไป) "
           f"· คลื่นร่วมยังถูกตัดทิ้งหมดเหมือนเดิม แต่ A − B ไหลไปไกลถึง {_n(far)} หน่วย และข้ามเส้นศูนย์ {f['zero_cross']} ครั้ง "
           f"(แบบสไลด์ {fl['zero_cross']} ครั้ง) ทั้งที่ขยับต่อวันน้อยกว่า (sd {_n(f['spread_change_sd'])} "
           f"เทียบกับ {_n(fl['spread_change_sd'])}) · ใน {_n(WORLDS)} โลกจำลอง ค่ากลางของการข้ามศูนย์คือ "
           f"{m['perm']['zero_cross_med']} ครั้ง เทียบกับ {m['level']['zero_cross_med']} ครั้ง และ ADF ผ่านเกณฑ์ "
           f"{m['perm']['reject_pct']}% ของโลก เทียบกับ {m['level']['reject_pct']}%")
    return V.stacked_panels("sas-p1-slide2-permanent", panels,
                            "รูปเดียวกับสไลด์ 2 แต่ Risk เป็นข่าวถาวร: A กับ B ค่อย ๆ แยกจากกัน และสเปรดไม่กลับมาที่ศูนย์",
                            cap, x=sl["t"], xticks=[0, 50, 100, 150, 200], xlabel="แท่งที่")


def _chart_neutral(ne, fg):
    t, p = ne["demo"]["t"], ne["demo"]["p"]
    ft, fp, f = fg["neutral"]["t"], fg["neutral"]["p"], fg["neutral"]
    price_lim = V.auto_lim(t["a"][0] * 100, t["b"][0] * 100, p["a"][0] * 100, p["b"][0] * 100, n=4)
    spread_lim = V.auto_lim(t["spread"][0] * 100, p["spread"][0] * 100, n=4)

    def pair(d, name, sub):
        return {"y": [d["a"][0] * 100, d["b"][0] * 100], "title": f"{name} · ราคา A และ B", "sub": sub,
                "color": [V.BLUE, V.AMBER], "names": ["A", "B"], "ylim": price_lim}

    def spread(d, name, fd, color):
        return {"y": d["spread"][0] * 100, "title": f"{name} · สเปรด A − B",
                "sub": f"corr กับตลาด {_n(fd['corr_spread_mkt'], 2)} · ADF {_n(fd['adf'], 2)} ({fd['adf_verdict']})",
                "color": color, "zero": True, "ylim": spread_lim}

    panels = [pair(t, "โลก T", "เรื่องเฉพาะตัวเป็นข่าวชั่วคราว"), spread(t, "โลก T", ft, V.GREEN),
              pair(p, "โลก P", "เรื่องเฉพาะตัวเป็นข่าวถาวร"), spread(p, "โลก P", fp, V.RED)]
    cap = (f"ข้อมูลจำลอง {_n(N_BARS)} แท่ง แกนตั้งเป็น % (log price × 100) กรอบสเปรดสองกรอบใช้สเกลเดียวกัน · "
           f"สองโลกใช้ปัจจัยร่วมเส้นเดียวกัน และเรื่องเฉพาะตัวผันผวนต่อวันเท่ากัน ({_n(f['idio_change_sd_pct'], 2)}%) "
           f"ผลตอบแทนรายวันของ A กับ B จึงสัมพันธ์กันพอ ๆ กัน ({_n(ft['corr_ab_returns'], 2)} และ {_n(fp['corr_ab_returns'], 2)}) "
           f"และสเปรดทั้งสองแทบไม่สัมพันธ์กับตลาด · แต่โลก T แกว่งในกรอบแคบ (sd {_n(ft['sd_all_pct'], 1)}%) "
           f"ส่วนโลก P ไหลออกไป (sd {_n(fp['sd_all_pct'], 1)}%, ADF ไม่ผ่านเกณฑ์ {_n(f['adf_crit5'], 2)}) · "
           f"ใน {_n(WORLDS)} โลกจำลอง ADF ผ่าน {f['mc']['t']['reject_pct']}% ของโลก T แต่เพียง "
           f"{f['mc']['p']['reject_pct']}% ของโลก P — <b>เป็นกลางต่อตลาด ไม่ได้แปลว่าจะกลับมา</b>")
    return V.stacked_panels("sas-p1-neutral-not-reverting", panels,
                            "สองโลกจำลองที่สเปรดเป็นกลางต่อตลาดทั้งคู่: โลก T สเปรดแกว่งรอบศูนย์ โลก P สเปรดไหลออกไปไม่กลับ",
                            cap, xlabel="แท่งที่ (วัน)", xticks=[0, 250, 500, 750, 1000])


def _chart_one_beta(un, fg):
    ob, f = un["onebeta"], fg["unequal"]["onebeta"]
    rows = (("b1", "β = 1\nA − B ตามสไลด์"), ("kill_m", "β = {b}\nตัด Market พอดี"),
            ("kill_s", "β = {b}\nตัด Size พอดี"), ("kill_g", "β = {b}\nตัด Growth พอดี"),
            ("best", "β = {b}\nปัจจัยเหลือน้อยที่สุด"), ("ols", "β = {b}\nOLS ผลตอบแทน (ข้อมูลไม่จำกัด)"))
    labels = [lab.format(b=_n(f[k]["beta"])) for k, lab in rows]
    values = [[float(x) for x in ob[k]["left"]] for k, _ in rows]
    cap = (f"คิดจาก loading จริงของ A ({LOAD['a'][0]}, {LOAD['a'][1]}, {LOAD['a'][2]}) และ B "
           f"({LOAD['b'][0]}, {LOAD['b'][1]}, {LOAD['b'][2]}) · ตัวเลขในช่อง = loading ที่ยังเหลือในสเปรด A − β·B "
           f"· β หนึ่งค่าทำให้เป็นศูนย์ได้ทีละ<b>หนึ่งปัจจัย</b> ปัจจัยอื่นยังอยู่ บางตัวแย่ลงด้วย "
           f"(ตัด Market แล้ว Size ขยับจาก {_n(f['b1']['left_s'], 2)} เป็น {_n(f['kill_m']['left_s'], 2)}) "
           f"· แม้ β ที่ดีที่สุด ({_n(f['best']['beta'])}) ปัจจัยที่เหลือก็ยังแกว่ง {_n(f['best']['left_sd_day_pct'], 2)}% ต่อวัน "
           f"(A − B เหลือ {_n(f['b1']['left_sd_day_pct'], 2)}% · A ตัวเดียว {_n(f['a_alone_sd_day_pct'], 2)}%) "
           f"· แถวล่างคือ β ที่ OLS ของผลตอบแทนรายวันเข้าหาเมื่อข้อมูลยาวไม่สิ้นสุด ({_n(f['ols']['beta'])})")
    return V.heat_table("sas-p1-one-beta", labels, ["Market", "Size", "Growth"], values,
                        "ตาราง loading ที่เหลือในสเปรด A ลบ เบต้าคูณ B สำหรับค่าเบต้าหกแบบ: แต่ละเบต้าทำให้เป็นศูนย์ได้ปัจจัยเดียว",
                        cap, scale="div", fmt="{:+.2f}", row_title="เลือก β แบบไหน", col_title="loading ที่เหลือ",
                        legend=False)


def _bar_label(key, f):
    if key == "beta_mkt":
        return f"A − {_n(f[key]['w_b'])}·B\nβ ที่ตัด Market พอดี"
    if key == "beta_ols":                                     # β ต่างกันไปทุกโลก → บอกค่ากลาง
        return f"A − β·B (β ≈ {_n(f[key]['mc']['w_b_med'], 2)})\nβ จาก OLS ผลตอบแทน"
    return {"ab": "A − B\nβ = 1", "two": "A − (B, C)\nตัด Market + Size พอดี",
            "three_est": "A − (B, C, D)\nน้ำหนักจาก regression",
            "three_true": "A − (B, C, D)\nน้ำหนักจาก loading จริง"}[key]


def _chart_leftover(un, fg):
    f = fg["unequal"]
    keys = ("ab", "beta_mkt", "beta_ols", "two", "three_est", "three_true")
    bars = [{"label": _bar_label(k, f), "values": [float(x) * 100 for x in un["mc"][k]["share_pooled"]]} for k in keys]
    cap = (f"ข้อมูลจำลอง {_n(WORLDS)} โลก ช่วงทดสอบโลกละ {_n(N_BARS)} แท่ง · แต่ละแท่งคือความแปรปรวนของ"
           f"<b>ผลตอบแทนรายวัน</b>ของสเปรด แบ่งตามที่มา · A − B ยังมีปัจจัยร่วมปนอยู่ {f['ab']['mc']['share_factor_pct']}% "
           f"· β จาก OLS ลดความผันผวนรายวัน แต่กลับเหลือปัจจัยมากขึ้นเป็น {f['beta_ols']['mc']['share_factor_pct']}% "
           f"· ตัวช่วยสองตัวยังเหลือ Growth {f['two']['mc']['share_g_pct']}% · ต้องใช้สามตัวด้วยน้ำหนักที่ถูกจึงเหลือ "
           f"{f['three_true']['mc']['share_factor_pct']}% · ส่วนสีที่ดูเล็กในรูปนี้คือส่วนที่สะสมข้ามวัน (ดูรูปส่วนแบ่งตามระยะถือ)")
    return V.stacked_bars("sas-p1-factor-leftover", bars, ["Market", "Size", "Growth", "เรื่องเฉพาะตัว"],
                          "ส่วนแบ่งความแปรปรวนของผลตอบแทนรายวันของสเปรดหกแบบ แยกเป็น Market Size Growth และเรื่องเฉพาะตัว",
                          cap, colors=[V.BLUE, V.AMBER, V.PURPLE, V.mix(V.MUTED, "#ffffff", 0.45)],
                          xlabel="ส่วนแบ่งของความแปรปรวนรายวันของสเปรด (รวมทุกโลก)")


def _chart_three_spreads(un, fg):
    f, d = fg["unequal"], un["demo"]
    rows = (("ab", "(i) A − B", V.RED), ("beta_ols", f"(ii) A − {_n(f['beta_ols']['w_b'], 2)}·B  (β จาก OLS)", V.AMBER),
            ("three_est", "(iii) A − (B, C, D) น้ำหนักจาก regression", V.PURPLE),
            ("three_true", "(iv) A − (B, C, D) น้ำหนักจริง", V.GREEN))
    panels = [{"y": d[k]["full"][0] * 100, "title": title, "color": color, "zero": True,
               "sub": f"ปัจจัยเหลือ {_n(f[k]['left_sd_day_pct'], 2)}%/วัน · sd ช่วงทดสอบ {_n(f[k]['sd_all_pct'], 1)}%"}
              for k, title, color in rows]
    n = N_TRAIN + N_BARS
    cap = (f"ข้อมูลจำลอง {_n(n)} แท่ง (โลกตัวอย่างหนึ่งโลก) แกนตั้งเป็น % วัดจากค่าเฉลี่ยของช่วง train ทุกกรอบใช้สเกลเดียวกัน · "
           f"เรื่องเฉพาะตัวของทั้งสี่สินทรัพย์เป็นข่าวชั่วคราวทั้งหมด สเปรดที่ตัดปัจจัยครบ (กรอบล่าง) จึงอยู่ในกรอบ "
           f"sd {_n(f['three_true']['sd_all_pct'], 1)}% · สเปรดที่ยังมีปัจจัยเหลือค่อย ๆ ไหลออกจากศูนย์ "
           f"(A − B: sd {_n(f['ab']['sd_all_pct'], 1)}%) · ใน {_n(WORLDS)} โลก การเปลี่ยนแปลง 250 แท่งของ A − B "
           f"มี sd {_n(f['ab']['mc']['chg250_sd_pct'], 1)}% เทียบกับ {_n(f['three_true']['mc']['chg250_sd_pct'], 1)}% "
           f"ของแบบน้ำหนักจริง — <b>ปัจจัยที่ตัดไม่หมด = random walk ที่ซ่อนอยู่ในสเปรด</b>")
    return V.stacked_panels("sas-p1-three-spreads", panels,
                            "ระดับของสเปรดสี่แบบบนสเกลเดียวกัน: ยิ่งเหลือปัจจัยร่วมมาก สเปรดยิ่งไหลออกจากศูนย์",
                            cap, share_y=True, xlabel="แท่งที่ (วัน)", xticks=list(range(0, n + 1, 250)),
                            xbands=[(0, N_TRAIN - 1, f"ช่วงประมาณน้ำหนัก ({N_TRAIN} แท่ง)")])


def _chart_horizon(un, fg):
    f, m = fg["unequal"], un["mc"]
    rows = (("beta_ols", "A − β·B (β จาก OLS)", V.AMBER), ("ab", "A − B", V.RED),
            ("three_est", "A − (B, C, D) น้ำหนักจาก regression", V.PURPLE),
            ("three_true", "A − (B, C, D) น้ำหนักจริง", V.GREEN))
    logh = [float(np.log10(h)) for h in HORIZONS]            # แกนนอนแบบ log: ระยะถือ 1 → 250 แท่ง
    series = [{"name": name, "y": [float(v) * 100 for v in m[k]["hz_share"]], "color": color} for k, name, color in rows]
    a = f["ab"]["mc"]
    cap = (f"ข้อมูลจำลอง Monte Carlo {_n(WORLDS)} โลก · ถามว่า “ถ้าถือสเปรดไว้ h แท่ง ความไม่แน่นอนของผลมาจากปัจจัยร่วมกี่ %” "
           f"(แกนนอนเป็นสเกล log) · A − B: จาก {a['hz_h1_pct']}% ที่ 1 แท่ง เป็น {a['hz_h20_pct']}% ที่ 20 แท่ง "
           f"และ {a['hz_h250_pct']}% ที่ 250 แท่ง · เรื่องเฉพาะตัวแกว่งแรงแต่วนกลับ ส่วนปัจจัยที่เหลือ"
           f"เล็กต่อวันแต่<b>สะสม</b> — ถือยิ่งนาน ยิ่งกลายเป็นการเดิมพันกับปัจจัยร่วม ไม่ใช่กับเรื่องเฉพาะตัว")
    return V.line_chart("sas-p1-horizon-share", logh, series,
                        "ส่วนแบ่งของปัจจัยร่วมในความแปรปรวนของสเปรดตามระยะถือ: สเปรดที่ตัดปัจจัยไม่หมดมีส่วนแบ่งนี้เพิ่มขึ้นเรื่อย ๆ",
                        cap, xlabel="ระยะถือ h (แท่ง · สเกล log)", ylabel="ส่วนแบ่งของปัจจัยร่วม (%)",
                        xticks=logh, xlabels=[str(h) for h in HORIZONS], xlim=(-0.08, logh[-1] + 0.08),
                        ylim=(0, 100), yfmt=lambda v: f"{v:.0f}%", markers=True)


def charts(res=None):
    res = res or run()
    fg = figures(res)
    return {
        "sas-p1-slide2": _chart_slide2(res["slide2"], fg),
        "sas-p1-slide2-permanent": _chart_slide2_perm(res["slide2"], fg),
        "sas-p1-neutral-not-reverting": _chart_neutral(res["neutral"], fg),
        "sas-p1-one-beta": _chart_one_beta(res["unequal"], fg),
        "sas-p1-factor-leftover": _chart_leftover(res["unequal"], fg),
        "sas-p1-three-spreads": _chart_three_spreads(res["unequal"], fg),
        "sas-p1-horizon-share": _chart_horizon(res["unequal"], fg),
    }


# ─────────────────────────────── สรุปเมื่อรันตรง ๆ ───────────────────────────────
def main():
    fg = figures()
    s2, ne, wk, un = fg["slide2"], fg["neutral"], fg["walk"], fg["unequal"]
    line = "─" * 78
    print("ห้องทดลองตอนที่ 1 — เดิมพันกับอะไร: ตัดตลาดทิ้ง แล้วเหลืออะไร  (ข้อมูลจำลองทั้งหมด)")
    print(f"โลกตัวอย่างเลือกด้วยกติกา: สถิติสำคัญใกล้ค่ากลางของ Monte Carlo ที่สุด · Monte Carlo {fg['neutral']['worlds']:,} โลก")
    print(line)
    print(f"1a  รูปของสไลด์ 2  ({s2['n_bars']} แท่ง · ADF ต้องต่ำกว่า {s2['adf_crit5']} จึงผ่าน · โลกตัวอย่าง seed "
          f"{s2['demo_offset']} ห่างค่ากลางไม่เกิน {s2['demo_max_dev_pct']} เปอร์เซ็นไทล์)")
    for key, name in (("level", "Risk เป็น noise ในระดับ (แบบสไลด์)"), ("perm", "Risk บวกสะสม (ข่าวถาวร)")):
        d, m = s2[key], s2["mc"][key]
        print(f"    {name}")
        print(f"        corr ของระดับราคา A,B {d['corr_levels']:.2f} · corr ของการเปลี่ยนแปลงรายวัน {d['corr_changes']:.2f}")
        print(f"        สเปรด: sd {d['spread_sd']:.2f} · ต่ำสุด {d['spread_min']} สูงสุด {d['spread_max']} · "
              f"ข้ามศูนย์ {d['zero_cross']} ครั้ง · ขยับต่อวัน sd {d['spread_change_sd']:.2f} · "
              f"ADF {d['adf']:.2f} ({d['adf_verdict']})")
        print(f"        Monte Carlo: ข้ามศูนย์ {m['zero_cross_med']} ครั้ง ({m['zero_cross_p5']} ถึง {m['zero_cross_p95']}) · "
              f"|สเปรด| สูงสุด {m['maxabs_med']} · ADF ผ่าน {m['reject_pct']}% ของโลก")
    print(line)
    print(f"1b  เป็นกลางต่อตลาด ≠ กลับสู่ค่าเฉลี่ย  ({ne['n_bars']:,} แท่ง · เรื่องเฉพาะตัวขยับ "
          f"{ne['idio_change_sd_pct']}% ต่อวันทั้งสองโลก · ADF ต้องต่ำกว่า {ne['adf_crit5']} · โลกตัวอย่าง seed "
          f"{ne['demo_offset']} ห่างค่ากลางไม่เกิน {ne['demo_max_dev_pct']})")
    for key, name in (("t", "โลก T (ข่าวชั่วคราว)"), ("p", "โลก P (ข่าวถาวร)   ")):
        d, m = ne[key], ne["mc"][key]
        print(f"    {name}  corr(ΔA,ΔB) {d['corr_ab_returns']:.2f} · corr(A,ตลาด) {d['corr_a_mkt']:.2f} · "
              f"corr(สเปรด,ตลาด) {d['corr_spread_mkt']:+.2f}")
        print(f"        ADF {d['adf']:.2f} ({d['adf_verdict']}) · sd 250 แท่งแรก {d['sd_first250_pct']}% → ทั้งช่วง "
              f"{d['sd_all_pct']}% · VR({ne['vr_q']}) {d['vr20']:.2f} · ช่วงกว้าง {d['range_pct']}% · ข้ามศูนย์ {d['zero_cross']} ครั้ง")
        print(f"        Monte Carlo: ADF ผ่าน {m['reject_pct']}% ของโลก · sd ทั้งช่วง/250 แท่งแรก "
              f"{m['sd_ratio_med']} ({m['sd_ratio_p5']} ถึง {m['sd_ratio_p95']}) · VR {m['vr20_med']:.2f} "
              f"({m['vr20_p5']:.2f} ถึง {m['vr20_p95']:.2f}) · ข้ามศูนย์ {m['zero_cross_med']} ครั้ง")
    print(line)
    d = wk["day"]
    print(f"ตัวอย่างคิดมือ: วันที่ Market {d['m_pct']:+}% · Size {d['s_pct']:+}% · Growth {d['g_pct']:+}%")
    for key, name in (("a", "A"), ("b", "B")):
        r = wk[key]
        print(f"    {name}: {r['m']:+} {r['s']:+} {r['g']:+} (ปัจจัย) {r['idio']:+} (เฉพาะตัว) = {r['total']:+}%")
    for key, name in (("ab", "A − B"), ("beta_mkt", f"A − {wk['beta_mkt']['w_b']}·B"), ("three", "A − (B, C, D)")):
        r = wk[key]
        print(f"    {name}: {r['m']:+} {r['s']:+} {r['g']:+} (ปัจจัย) {r['idio']:+} (เฉพาะตัว) = {r['total']:+}%"
              f"   → มาจากปัจจัยร่วม {r['factor_share_pct']}%")
    print(f"    ถ้า loading เท่ากันหมดแบบสไลด์: A {wk['equal']['a_total']:+}% · B {wk['equal']['b_total']:+}% · "
          f"A − B = {wk['equal']['spread']:+}% (เหลือแต่เรื่องเฉพาะตัว)")
    print(line)
    print(f"1c  loading ไม่เท่ากัน  (ประมาณน้ำหนักจาก {un['n_train']} แท่ง · วัดผล {un['n_test']:,} แท่ง · "
          f"Monte Carlo {un['worlds']:,} โลก · ADF ต้องต่ำกว่า {un['adf_crit5']} · โลกตัวอย่าง seed {un['demo_offset']} "
          f"ห่างค่ากลางไม่เกิน {un['demo_max_dev_pct']})")
    ob = un["onebeta"]
    print("    β ตัวเดียว ตัดได้ทีละปัจจัย (loading ที่เหลือ: Market, Size, Growth · ปัจจัยที่เหลือ %/วัน)")
    for key in ("b1", "kill_m", "kill_s", "kill_g", "best", "ols"):
        r = ob[key]
        print(f"        β = {r['beta']:<6} → {r['left_m']:+.3f} {r['left_s']:+.3f} {r['left_g']:+.3f}   {r['left_sd_day_pct']:.2f}")
    tb = un["two_best"]
    print(f"    ตัวช่วยสองตัว (B, C) ที่ดีที่สุด: w = ({tb['w_b']}, {tb['w_c']}) → เหลือ {tb['left_m']:+.3f} {tb['left_s']:+.3f} "
          f"{tb['left_g']:+.3f}   {tb['left_sd_day_pct']:.2f}% ต่อวัน (ยังไม่เป็นศูนย์)")
    names = {"ab": "A − B", "beta_mkt": "A − β·B (ตัด Market)", "beta_ols": "A − β·B (OLS ผลตอบแทน)",
             "beta_lvl": "A − β·B (OLS ระดับราคา)", "two": "A − (B,C)", "three_est": "A − (B,C,D) regression ผลตอบแทน",
             "three_lvl": "A − (B,C,D) regression ระดับ", "three_true": "A − (B,C,D) น้ำหนักจริง"}
    print("    สเปรดแต่ละแบบ: [โลกตัวอย่าง] น้ำหนัก (B, C, D) · ปัจจัยในความแปรปรวนรายวัน · corr กับตลาด · ADF · sd")
    print("                   [MC] ADF ผ่านกี่ % ของโลก (lags 1 / lags 10) · sd ของการเปลี่ยนแปลง 250 แท่ง · "
          "ส่วนแบ่งปัจจัย h = 1 → 250")
    for key in CONSTRUCTIONS:
        r, m = un[key], un[key]["mc"]
        print(f"      {names[key]}")
        print(f"          w = ({r['w_b']}, {r['w_c']}, {r['w_d']}) · ปัจจัย {r['share_factor_pct']}% · corr {r['corr_mkt']:+.2f} · "
              f"ADF {r['adf']:.2f} ({r['adf_verdict']}) · sd {r['sd_first250_pct']}% → {r['sd_all_pct']}%")
        print(f"          [MC] ผ่าน {m['reject_pct']}% / {m['reject_lags10_pct']}% · Δ250 sd {m['chg250_sd_pct']}% · "
              f"ปัจจัยที่ h=1 {m['hz_h1_pct']}% → h=250 {m['hz_h250_pct']}% · ปัจจัยรายวัน {m['share_factor_pct']}%")
        if "theory" in r:
            t = r["theory"]
            extra = (f" · น้ำหนักเมื่อข้อมูลไม่จำกัด ({t['w_b']}, {t['w_c']}, {t['w_d']})" if "w_b" in t else "")
            print(f"          [สูตร] ปัจจัยที่ h=1 {t['factor_h1_pct']}% → h=250 {t['factor_h250_pct']}% · "
                  f"Δ250 sd {t['chg250_sd_pct']}%{extra}")
        if key in ESTIMATED:
            legs = ("b", "c", "d") if key.startswith("three") else ("b",)
            print("          [MC] น้ำหนักที่ประมาณได้ ค่ากลาง (5–95%): " + " · ".join(
                f"{leg.upper()} {m[f'w_{leg}_med']} ({m[f'w_{leg}_p5']} ถึง {m[f'w_{leg}_p95']})" for leg in legs))
    print(line)
    print("กราฟ: " + " · ".join(sorted(charts())))


if __name__ == "__main__":
    main()
