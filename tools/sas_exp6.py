#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ห้องทดลองของตอนที่ 6 — "มากกว่าสองตัว: ตะกร้า พอร์ต และสมการทั่วไป" (สไลด์แผ่นที่ 5)

คำถามของตอนนี้: ถ้าเลิกเทรดแค่ "คู่เดียว" แล้วใช้สินทรัพย์มากกว่าสองตัว หรือทำเป็นพอร์ต จะช่วยไหม
ทุกการทดลองใช้ข้อมูลจำลองที่เรารู้เฉลย (รู้ว่าสายจูงมีจริงหรือไม่ และแข็งแค่ไหน)

การทดลอง (คีย์ชั้นบนสุดของ figures() อยู่ในวงเล็บ)
  6a (crit)       ยิ่งใส่ขาในสเปรดมาก เกณฑ์ผ่านของ Engle-Granger ยิ่งต้องติดลบมาก
                  ถ้ายังใช้เกณฑ์ของ 2 ขา จะ "ผ่านปลอม" บ่อยแค่ไหน                     N = 2…8, 500 แท่ง
  6b (fit_noise)  ถดถอย random walk บน random walk อีก N−1 เส้น (ไม่มีสายจูงเลย) แล้วถือน้ำหนักเดิมต่อ
                  → ในช่วงที่ fit ดูนิ่งขึ้นเรื่อย ๆ ตามจำนวนขา แต่นอกช่วง fit ไม่นิ่งเลย
  6c (universe)   จักรวาลหุ้นจำลอง 30 ตัว 3 กลุ่ม สี่แบบ ต่างกันที่ "ความแข็งของสายจูง" อย่างเดียว
                  (thick / medium / thin / none) เทียบสี่กลยุทธ์ด้วยโค้ดชุดเดียวกัน แบบเดินหน้าทั้งหมด
                    s1 คู่เดียว (คู่ที่ค่า EG ดีที่สุดในช่วงคัดเลือก)
                    s2 สิบคู่ที่ไม่ใช้หุ้นซ้ำกัน
                    s3 หุ้นทุกตัวเทียบตะกร้ากลุ่ม + ตะกร้าตลาด (ถดถอยผลตอบแทน 60 แท่ง แล้วดู s-score)
                    s4 ส่วนเหลือจาก PCA (eigenportfolio 5 ตัว จากเมทริกซ์สหสัมพันธ์ 250 แท่ง)
                  คีย์: universe.<จักรวาล>.<s1…s4>.<ตัววัด> · universe.<จักรวาล>.leftover_factor_pct
                        universe.<จักรวาล>.selection · universe.<จักรวาล>.breadth_link
  6d (breadth)    สูตรความกว้าง Sharpe_พอร์ต = S·√(M / (1 + (M−1)ρ)) และโอกาสขาดทุนทั้งปี
                  พร้อมการจำลองตรวจสูตร
  6f (johansen)   [รอบสอง] Johansen แบบเปิดฝา (numpy ล้วน) กับสินทรัพย์ 3 ตัวที่มีสายจูงจริงหนึ่งเส้น
                  ทำสองความยาวของช่วงประมาณ (train_1000, train_500): ค่าวิกฤตที่จำลองเอง · หาเจอบ่อยแค่ไหน ·
                  น้ำหนักแม่นแค่ไหนเทียบกับ OLS (ในโลกสองแบบ เพราะคำตอบขึ้นกับว่าสายจูงทำงานอย่างไร) ·
                  และเมื่อไม่มีสายจูงเลย การ "ค้นหาน้ำหนัก" ทำให้ผ่านปลอมในช่วง fit มากแค่ไหน
                  · johansen.demo = โลกตัวอย่างหนึ่งใบ

คีย์ของ figures() (ทุกค่าปัดแล้ว · หน่วยอยู่ในชื่อคีย์: _pct = % · _bars = แท่ง · _bps = bps)
  about.<การทดลอง>                      คำอธิบายสั้น ๆ ของการตั้งค่า (จำนวนแท่ง จำนวนโลก ต้นทุน ความแม่น)
  crit.legs_<N>.crit5 | crit1 | crit10 | false_pass_2leg_pct                          N = 2…8
  fit_noise.legs_<N>.sd_in_pct | rms_out_pct | out_over_in | hl_in_median_bars
                    | hl_under_30_pct | out_outside_2sd_pct                           N = 2, 4, 8, 15
  universe.<thick|medium|thin|none>.<s1|s2|s3|s4>.
        sharpe_mean | sharpe_mean_se | sharpe_median | sharpe_p5 | sharpe_p95   Sharpe หลังต้นทุน (lag 1)
        sharpe_gross_mean (c = 0) | sharpe_lag2_mean (ได้ราคาช้าหนึ่งแท่ง)
        loss_worlds_pct (โลกที่ผลรวมหลังต้นทุนติดลบ)
        max_dd_at_10vol_pct (drawdown เมื่อปรับให้ผันผวน 10%/ปีเท่ากัน — ใช้ตัวนี้เทียบข้ามกลยุทธ์)
        max_dd_mean_pct | ann_return_mean_pct | ann_vol_mean_pct (ดิบ ขึ้นกับทุนที่ใช้) | capital_used_mean_pct
        abs_corr_market_mean | turnover_per_year (เท่าของทุน) | cost_per_year_pct
  universe.abs_corr_noise_floor                                    |corr| ที่ได้จากความบังเอิญล้วน ๆ
  universe.<จักรวาล>.paired.<s2_minus_s1|s3_minus_s2|s4_minus_s2|s4_minus_s3>.
        sharpe_diff_mean | sharpe_diff_se | better_worlds_pct      เทียบสองกลยุทธ์ในโลกเดียวกัน (แม่นกว่า)
  universe.<จักรวาล>.leftover_factor_pct.pair | basket | pca     ปัจจัยร่วมที่ยังเหลือในสเปรด (จากเฉลย)
  universe.<จักรวาล>.selection.best_pair_passes_pct | chosen_passing_mean | all_candidates_pass_pct
  universe.<จักรวาล>.breadth_link.pair_sharpe_mean | pair_corr_mean | formula_sharpe | measured_sharpe
  breadth.sharpe.rho_<0|0_1|0_3>.m_<M> · breadth.loss_year_pct.… · breadth.ceiling.rho_0_1 | rho_0_3
  breadth.sim.rho_<…>.m_<M>.sharpe | loss_year_pct                 (การจำลองตรวจสูตร)
  johansen.demo.…  ·  johansen.train_<1000|500>.crit | null | power | power_corr .…
        power      = โลกที่แรงกระแทกของ ε ไม่เกี่ยวกับ X (กรณีที่ OLS ได้เปรียบที่สุด)
        power_corr = โลกที่แรงกระแทกของ ε สัมพันธ์ 0.6 กับแรงกระแทกของ X

ความแม่น: จำนวนทศนิยมถูกเลือกให้ตัวเลขหลักสุดท้ายแทบไม่ขยับเมื่อเปลี่ยนเลขสุ่ม (ตรวจโดยรันซ้ำด้วยเลขสุ่มชุดอื่น)
          รายละเอียดอยู่ใน about.*_precision

seed: ทุกตัวมาจาก C.rng(offset) — 600 (6a) · 610 (6b) · 611 (เกณฑ์ EG ของ 6c) · 612 (6d)
      620 (โลกทั้งหมดของ 6c ดึงต่อกันจากตัวสุ่มตัวเดียว — โลกที่ w ใช้เลขสุ่มชุดเดียวกันทั้งสี่จักรวาล
      ต่างกันแค่ขนาดของส่วนเฉพาะตัว) · 680–687 (6f)

วิธีรัน
    python3 tools/sas_exp6.py            # พิมพ์สรุปตัวเลขหลัก (ใช้เวลาราว 2–3 นาที)
ใช้จากโค้ดอื่น
    import sas_exp6 as E;  res = E.run();  E.figures(res);  E.charts(res)

ข้อควรรู้ก่อนอ่านตัวเลข
  • ไม่มีการมองอนาคต: ทุกการตัดสินใจตอนสิ้นแท่ง t ใช้ข้อมูลถึงแท่ง t · กำไรขาดทุนเริ่มนับที่แท่ง t+1
    (ตัวเลข lag 2 = ได้ราคาช้าไปอีกหนึ่งแท่ง รายงานคู่กันเสมอ)
  • z ของคู่ (s1, s2) วัดด้วย σ ที่ประมาณจากช่วง train 250 แท่ง ไม่ใช่ σ จริง
  • ต้นทุน c = 5 bps ต่อขาต่อเที่ยว คิดกับทุกขารวมทั้งตะกร้าที่ใช้กันความเสี่ยง
  • ผลตอบแทนคิดต่อ "ทุนทั้งพอร์ต" โดยเงินรวมทุกขา (gross) ไม่เกิน 1 เท่าของทุนเสมอ
"""
import functools
import math
import time

import numpy as np

import sas_core as C
import sas_svg as V

# ───────────────────────── ค่าตั้งของจักรวาลจำลอง (6c) ─────────────────────────
COST = 0.0005                 # c = 5 bps ต่อขาต่อเที่ยว
N_BARS, BURN = 1750, 250      # 250 แท่งแรก = ช่วงคัดเลือก/อุ่นเครื่อง · ทดสอบ 1,500 แท่ง
N_STOCKS, N_SECTORS = 30, 3
N_WORLDS = 100                # จำนวนโลกต่อจักรวาล (ค่าเฉลี่ย Sharpe คลาดได้ราว ±0.03–0.05 → พิมพ์ทศนิยมหนึ่งตำแหน่ง)
REFIT = 21                    # ประมาณค่าใหม่ทุก 21 แท่ง (คู่ และ eigenportfolio)
WIN = 60                      # หน้าต่างถดถอยผลตอบแทนของ s3 / s4
S_OPEN, S_CLOSE = 1.25, 0.5   # เปิดเมื่อ |s| > 1.25 · ปิดเมื่อ |s| < 0.5
B_MAX = math.exp(-1.0 / 30)   # รับเฉพาะส่วนเหลือที่ AR(1) บอกว่าดึงกลับเร็วกว่า ~30 แท่ง (b < 0.967)
N_PCA, CORR_WIN = 5, 250
SHOCK_CORR = 0.6              # 6f: ความสัมพันธ์ของแรงกระแทก ε กับแรงกระแทกของ X ในโลกแบบที่สอง
SD_MARKET, SD_SECTOR, SD_STYLE = 0.010, 0.007, 0.005      # sd รายวันของปัจจัยร่วมสามชั้น

# ส่วนเฉพาะตัวของหุ้น u = ส่วนที่ดึงกลับ (OU) + ส่วนที่ไปแล้วไม่กลับ (random walk)
UNIVERSES = {
    "thick":  {"ou_sigma": (0.025, 0.045), "perm_sigma": 0.003},
    "medium": {"ou_sigma": (0.015, 0.030), "perm_sigma": 0.005},
    "thin":   {"ou_sigma": (0.010, 0.020), "perm_sigma": 0.008},
    "none":   {"ou_sigma": None,           "perm_sigma": 0.010},
}
UNIVERSE_TH = {"thick": "สายจูงแข็ง", "medium": "สายจูงปานกลาง", "thin": "สายจูงอ่อน", "none": "ไม่มีสายจูง"}
STRATEGIES = ("s1", "s2", "s3", "s4")
STRATEGY_TH = {"s1": "S1 คู่เดียว", "s2": "S2 สิบคู่", "s3": "S3 หุ้น − ตะกร้ากลุ่ม", "s4": "S4 ส่วนเหลือ PCA"}
STRATEGY_COLOR = {"s1": V.MUTED, "s2": V.BLUE, "s3": V.AMBER, "s4": V.PURPLE}


# ───────────────────────── ตัวช่วยเล็ก ๆ ─────────────────────────
def _windows(a, w):
    """หน้าต่างเลื่อนยาว w ตามแกนเวลา (แกน 0) · หน้าต่างที่ k จบที่แท่ง k + w − 1 · แกนของหน้าต่างอยู่ท้ายสุด"""
    return np.lib.stride_tricks.sliding_window_view(a, w, axis=0)


def _rolling_ols(yw, fw):
    """OLS ของทุกหน้าต่างพร้อมกัน · yw (nt, n, w) = ตัวแปรตาม n ตัว · fw (nt, p, w) = ตัวแปรอธิบาย
    (ใส่แถวของเลข 1 มาเองถ้าต้องการค่าคงที่) → coef (nt, p, n), resid (nt, n, w)"""
    ft = fw.transpose(0, 2, 1)
    coef = np.linalg.solve(fw @ ft, fw @ yw.transpose(0, 2, 1))
    return coef, yw - coef.transpose(0, 2, 1) @ fw


def _ar1_fit(x):
    """AR(1) ตามแกนสุดท้ายของหลายเส้นพร้อมกัน: x_{k+1} = a + b·x_k + e → (a, b, s2)
    ผลเท่ากับ C.fit_ar1 ทีละเส้น (s2 หารด้วย m − 2 · m = จำนวนคู่ (x_k, x_{k+1}))
    คิดจากผลรวมและผลรวมกำลังสองโดยตรง (อ่านข้อมูลสามรอบ) เพราะเรียกกับอาร์เรย์ 1,500 × 30 × 60 หลายครั้ง"""
    m = x.shape[-1] - 1
    s, sq = x.sum(axis=-1), np.einsum("...k,...k->...", x, x)
    first, last = x[..., 0], x[..., -1]
    m0, m1 = (s - last) / m, (s - first) / m                   # ค่าเฉลี่ยของ x_k และของ x_{k+1}
    sxx = sq - last * last - m * m0 * m0
    syy = sq - first * first - m * m1 * m1
    sxy = np.einsum("...k,...k->...", x[..., :-1], x[..., 1:]) - m * m0 * m1
    with np.errstate(divide="ignore", invalid="ignore"):
        b = sxy / sxx
    return m1 - b * m0, b, (syy - b * sxy) / (m - 2)


def _dist(values):
    v = np.asarray(values, float)
    return {"mean": float(v.mean()), "median": float(np.median(v)),
            "p5": float(np.percentile(v, 5)), "p95": float(np.percentile(v, 95))}


def _norm_cdf(x):
    return 0.5 * math.erfc(-x / math.sqrt(2.0))


# ═════════════════════════ 6a — ค่าวิกฤตตามจำนวนขา ═════════════════════════
def _nested_residuals(w):
    """ส่วนเหลือของการถดถอยเส้นแรกบนเส้นที่ 2…N (มีค่าคงที่) ของทุก N ในรอบเดียว
    w: (โลก, แท่ง, เส้น) → {N: (โลก, แท่ง)}
    เพิ่มขาทีละขาแบบ Gram-Schmidt: ตั้งฉากขาใหม่กับขาเก่าก่อน แล้วค่อยลบส่วนที่ขาใหม่อธิบายได้ออก
    ผลเท่ากับ C.resid_batch ทุกประการ (ตรวจใน exp_crit_vs_legs) แต่ไม่ต้องแก้สมการใหม่ทุก N"""
    x = w - w.mean(axis=1, keepdims=True)
    resid = x[:, :, 0].copy()
    basis, out = [], {}
    for k in range(1, x.shape[2]):
        q = x[:, :, k].copy()
        for p, pp in basis:
            q -= ((q * p).sum(axis=1) / pp)[:, None] * p
        qq = (q * q).sum(axis=1)
        basis.append((q, qq))
        resid = resid - ((resid * q).sum(axis=1) / qq)[:, None] * q
        out[k + 1] = resid
    return out


def exp_crit_vs_legs(n_obs=500, n_sim=100_000, legs=tuple(range(2, 9)), chunk=500):
    """จำลองโลกที่ "ไม่มีตัวไหนผูกกันเลย" (random walk อิสระ) แล้วทำ Engle-Granger กับ N = 2…8 ขา
    ใช้ random walk ชุดเดียวกันกับทุก N (เพิ่มขาทีละขา) จึงเทียบข้าม N ได้ตรง ๆ"""
    g = C.rng(600)
    stats = {n: np.empty(n_sim) for n in legs}
    for s in range(0, n_sim, chunk):
        m = min(chunk, n_sim - s)
        w = np.cumsum(g.standard_normal((m, n_obs, max(legs))), axis=1)
        resid = _nested_residuals(w)
        if s == 0:                              # ยืนยันกับแกนคำนวณกลางทุกครั้งที่รัน
            for n in (legs[0], legs[-1]):
                ref = C.resid_batch(w[:40, :, 0], w[:40, :, 1:n])
                assert np.allclose(resid[n][:40], ref, atol=1e-8), "ส่วนเหลือไม่ตรงกับ C.resid_batch"
        for n in legs:
            stats[n][s:s + m] = C.adf_stat_batch(resid[n], lags=1, const=False)
    two_leg_cut = float(np.quantile(stats[legs[0]], 0.05))
    rows = {}
    for n in legs:
        q01, q05, q10 = np.quantile(stats[n], [0.01, 0.05, 0.10])
        rows[n] = {"crit1": float(q01), "crit5": float(q05), "crit10": float(q10),
                   "false_pass_2leg": float(np.mean(stats[n] < two_leg_cut))}
    return {"n_obs": n_obs, "n_sim": n_sim, "lags": 1, "legs": list(legs), "rows": rows}


# ═════════════════════════ 6b — สัญญาณรบกวนจากการ fit ═════════════════════════
def exp_fit_noise(legs=(2, 4, 8, 15), n_fit=500, n_hold=500, worlds=3000, sigma=0.01):
    """random walk อิสระล้วน ๆ (ไม่มีสายจูง) · fit น้ำหนักจาก 500 แท่งแรก แล้วถือน้ำหนักเดิมอีก 500 แท่ง
    sd_in = sd ของสเปรดในช่วง fit · rms_out = ขนาดการแกว่งนอกช่วง fit วัดรอบเส้นกลางของช่วง fit (ศูนย์)
    คือระยะที่คนเทรดเห็นจริงเมื่อยังใช้ μ เดิม"""
    g = C.rng(610)
    w = np.cumsum(sigma * g.standard_normal((worlds, n_fit + n_hold, max(legs))), axis=1)
    rows = {}
    for n in legs:
        sd_in, rms_out, hl, outside = (np.empty(worlds) for _ in range(4))
        for i in range(worlds):
            y, x = w[i, :, 0], w[i, :, 1:n]
            coef = C.ols(y[:n_fit], x[:n_fit])["coef"]
            eps = y - coef[0] - x @ coef[1:]                 # ค่าเฉลี่ยในช่วง fit เป็นศูนย์อยู่แล้ว
            sd_in[i] = eps[:n_fit].std(ddof=1)
            rms_out[i] = math.sqrt(float(np.mean(eps[n_fit:] ** 2)))
            hl[i] = C.fit_ar1(eps[:n_fit])["half_life"]
            outside[i] = np.mean(np.abs(eps[n_fit:]) > 2.0 * sd_in[i])
        rows[n] = {"sd_in": float(np.median(sd_in)), "rms_out": float(np.median(rms_out)),
                   "out_over_in": float(np.median(rms_out / sd_in)),
                   "hl_in": float(np.median(hl)), "hl_under_30": float(np.mean(hl < 30)),
                   "outside_2sd": float(np.mean(outside))}
    return {"legs": list(legs), "n_fit": n_fit, "n_hold": n_hold, "worlds": worlds, "sigma": sigma, "rows": rows}


# ═════════════════════════ 6c — จักรวาลหุ้นจำลอง ═════════════════════════
def base_world(g):
    """เลขสุ่มของโลกหนึ่งใบ (ใช้ร่วมกันทั้งสี่จักรวาล): ปัจจัยร่วม · น้ำหนักต่อปัจจัย · เส้น OU ขนาด 1 · เส้นถาวรขนาด 1
    g = ตัวสุ่มที่ส่งต่อกันทีละโลก (โลกที่ w ได้เลขสุ่มชุดที่ w ของ C.rng(620) เสมอ)"""
    t, n, k = N_BARS, N_STOCKS, N_SECTORS
    sec = np.repeat(np.arange(k), n // k)
    market = SD_MARKET * g.standard_normal(t)
    sector = SD_SECTOR * g.standard_normal((t, k))
    style = SD_STYLE * g.standard_normal(t)
    b_m, b_s, b_v = g.uniform(0.6, 1.5, n), g.uniform(0.6, 1.4, n), 0.6 * g.standard_normal(n)
    half_life, where = g.uniform(6.0, 18.0, n), g.uniform(0.0, 1.0, n)
    phi = 0.5 ** (1.0 / half_life)
    shock = g.standard_normal((t, n))
    ou = np.empty((t, n))                       # AR(1) ที่ sd ระยะยาว = 1 เริ่มจากการแจกแจงนิ่งของตัวเอง
    ou[0] = shock[0]
    for i in range(1, t):
        ou[i] = phi * ou[i - 1] + np.sqrt(1.0 - phi * phi) * shock[i]
    perm = np.cumsum(g.standard_normal((t, n)), axis=0)
    factor_ret = market[:, None] * b_m + sector[:, sec] * b_s + style[:, None] * b_v
    # น้ำหนักต่อปัจจัย × sd ของปัจจัย (คอลัมน์: ตลาด, กลุ่ม 1…K, สไตล์) — ใช้คิด "ปัจจัยร่วมที่ยังเหลือ" จากเฉลย
    loadings = np.column_stack([b_m * SD_MARKET] + [b_s * (sec == j) * SD_SECTOR for j in range(k)]
                               + [b_v * SD_STYLE])
    return {"sec": sec, "market": market, "factor_level": np.cumsum(factor_ret, axis=0), "ou": ou, "perm": perm,
            "phi": phi, "where": where, "loadings": loadings}


def dress_world(base, kind):
    """ใส่ส่วนเฉพาะตัวตามชนิดจักรวาล → log ราคา ผลตอบแทน และเฉลยที่ต้องใช้วัดผล"""
    spec = UNIVERSES[kind]
    if spec["ou_sigma"] is None:
        ou_sigma = np.zeros(N_STOCKS)
    else:
        lo, hi = spec["ou_sigma"]
        ou_sigma = lo + (hi - lo) * base["where"]
    u = base["ou"] * ou_sigma + spec["perm_sigma"] * base["perm"]
    logp = base["factor_level"] + u
    return {"logp": logp, "r": np.diff(logp, axis=0, prepend=logp[:1]), "sec": base["sec"],
            "market": base["market"], "loadings": base["loadings"],
            # ความแปรปรวนรายแท่งของ Δu: ส่วน OU = 2σ²(1−φ) · ส่วนถาวร = σ_p²
            "idio_var": 2.0 * ou_sigma ** 2 * (1.0 - base["phi"]) + spec["perm_sigma"] ** 2}


def factor_share(v, world):
    """สัดส่วนความแปรปรวนของผลตอบแทนสเปรดที่ยังมาจากปัจจัยร่วม · v (…, N) = น้ำหนักของสเปรดบนหุ้นแต่ละตัว
    คิดจากเฉลยของโลกจำลอง (น้ำหนักต่อปัจจัยจริง) ไม่ได้ประมาณจากข้อมูล"""
    fac = ((v @ world["loadings"]) ** 2).sum(axis=-1)
    idio = (v * v) @ world["idio_var"]
    return fac / (fac + idio)


def score(book, market):
    """ตัววัดของกลยุทธ์หนึ่งในโลกหนึ่ง · book = ผลรายแท่งช่วงทดสอบ (net, gross, lag2, turnover, used)"""
    st = C.perf_stats(book["net"])
    corr = abs(float(np.corrcoef(book["net"], market)[0, 1])) if st["ann_vol"] > 0 else 0.0
    return {"sharpe": st["sharpe"], "sharpe_gross": C.perf_stats(book["gross"])["sharpe"],
            "sharpe_lag2": C.perf_stats(book["lag2"])["sharpe"], "total": st["total"],
            "max_dd": st["max_dd"], "ann_vol": st["ann_vol"], "ann_return": st["ann_return"],
            "dd_over_vol": st["max_dd"] / st["ann_vol"] if st["ann_vol"] > 0 else 0.0,
            "abs_corr_market": corr, "turnover_year": float(book["turnover"].mean()) * C.DAYS_PER_YEAR,
            "used": float(book["used"].mean())}


# ── s1, s2: คู่ ──
def pick_pairs(world, n_pairs):
    """คัดคู่จากช่วงคัดเลือก (250 แท่งแรก): ทุกคู่ในกลุ่มเดียวกัน เรียงตามค่า Engle-Granger
    แล้วหยิบจากดีที่สุดลงมาโดยไม่ใช้หุ้นซ้ำ → (รายการคู่, ค่า EG ของคู่ที่เลือก, ค่า EG ของทุกคู่)"""
    logp, sec = world["logp"][:BURN], world["sec"]
    i, j = np.triu_indices(N_STOCKS, 1)
    same = sec[i] == sec[j]
    i, j = i[same], j[same]
    resid = C.resid_batch(logp[:, i].T, logp[:, j].T[:, :, None])
    stat = C.adf_stat_batch(resid, lags=1, const=False)
    used, chosen = set(), []
    for k in np.argsort(stat):
        if i[k] in used or j[k] in used:
            continue
        chosen.append(k)
        used |= {i[k], j[k]}
        if len(chosen) == n_pairs:
            break
    return [(int(i[k]), int(j[k])) for k in chosen], stat[chosen], stat


def trade_pairs(world, pairs):
    """เดินหน้าทีละคู่ด้วย C.walk_forward_pair (train 250 · refit 21 · เข้า z = 2 · ออก z = 0)
    คืนผลรายแท่งของแต่ละคู่ (ต่อเงินรวมสองขาของคู่นั้น) และสัดส่วนปัจจัยร่วมที่ยังเหลือในสเปรด"""
    logp = world["logp"]
    books, leftover = [], []
    for i, j in pairs:
        y, x = logp[:, i], logp[:, j]
        wf = C.walk_forward_pair(y, x, train=BURN, refit=REFIT, entry=2.0, exit=0.0, cost_per_leg=COST)
        turn = np.abs(np.diff(wf["held"], prepend=0.0))
        beta = np.where(np.isfinite(wf["beta"]), wf["beta"], 0.0)
        lag2, _ = C.spread_pnl(y, x, beta, wf["pos"], cost_per_leg=COST, lag=2)
        books.append({"net": wf["pnl"][BURN:], "gross": (wf["pnl"] + COST * turn)[BURN:], "lag2": lag2[BURN:],
                      "turnover": turn[BURN:], "used": np.abs(wf["held"][BURN:])})
        b = beta[BURN::REFIT]
        v = np.zeros((len(b), N_STOCKS))
        v[:, i], v[:, j] = 1.0, -b
        leftover.append(float(factor_share(v, world).mean()))
    return books, float(np.mean(leftover))


def combine(books):
    """พอร์ตของหลายคู่ แบ่งทุนเท่ากันทุกคู่ (จึงใช้เงินรวมไม่เกิน 1 เท่าของทุน)"""
    return {k: np.mean([b[k] for b in books], axis=0) for k in books[0]}


# ── s3, s4: ส่วนเหลือเทียบตะกร้า ──
def s_score(resid):
    """s-score ของส่วนเหลือสะสม: X_k = ผลรวมส่วนเหลือถึงแท่ง k → fit AR(1) → s = (X_ล่าสุด − μ)/σ_eq
    ok = AR(1) บอกว่าดึงกลับเร็วพอ (0 < b < B_MAX) · ที่ ok เป็นเท็จให้ s = 0"""
    x = np.cumsum(resid, axis=-1)
    a, b, s2 = _ar1_fit(x)
    ok = (b > 0) & (b < B_MAX) & (s2 > 0)
    bb = np.where(ok, b, 0.5)
    s = (x[..., -1] - a / (1.0 - bb)) / np.sqrt(np.where(ok, s2, 1.0) / (1.0 - bb * bb))
    return np.where(ok, s, 0.0), ok


def hysteresis(s, ok):
    """กฎเปิด-ปิดของหุ้นทุกตัวพร้อมกัน (เดินทีละแท่ง): ว่างอยู่ + s < −1.25 → long ส่วนเหลือ · s > 1.25 → short
    ปิด long เมื่อ s > −0.5 · ปิด short เมื่อ s < 0.5 · หรือเมื่อส่วนเหลือเลิกดึงกลับ (ok เป็นเท็จ)
    คืน state (nt, n) ∈ {−1, 0, 1} และ entry (nt, n) = แท่งที่เปิดไม้ที่ถืออยู่"""
    nt, n = s.shape
    state, entry = np.zeros((nt, n)), np.zeros((nt, n), dtype=int)
    cur, ent = np.zeros(n), np.zeros(n, dtype=int)
    for t in range(nt):
        st, good = s[t], ok[t]
        close = ((cur > 0) & ((st > -S_CLOSE) | ~good)) | ((cur < 0) & ((st < S_CLOSE) | ~good))
        cur[close] = 0.0
        go_long = (cur == 0) & good & (st < -S_OPEN)
        go_short = (cur == 0) & good & (st > S_OPEN)
        cur[go_long], cur[go_short] = 1.0, -1.0
        ent[go_long | go_short] = t
        state[t], entry[t] = cur, ent
    return state, entry


def run_book(weights, returns):
    """น้ำหนักเป้าหมายรายแท่ง → ผลรายแท่งช่วงทดสอบ (หลังต้นทุน · ก่อนต้นทุน · lag 2)"""
    net, turn = C.portfolio_pnl(weights, returns, cost_per_leg=COST)
    lag2, _ = C.portfolio_pnl(weights, returns, cost_per_leg=COST, lag=2)
    return {"net": net[BURN:], "gross": (net + COST * turn)[BURN:], "lag2": lag2[BURN:],
            "turnover": turn[BURN:], "used": np.abs(weights).sum(axis=1)[BURN:]}


def basket_strategy(world):
    """s3: หุ้นแต่ละตัว − β_กลุ่ม·ตะกร้ากลุ่ม − β_ตลาด·ตะกร้าตลาด (ตะกร้า = ค่าเฉลี่ยน้ำหนักเท่ากัน)
    β มาจากการถดถอยผลตอบแทน 60 แท่งล่าสุด · เปิดไม้ด้วย β ของวันนั้นแล้วถือ hedge เดิมจนปิด
    แต่ละไม้ได้ทุน 1/N และย่อด้วยเงินรวมของตัวเอง (1 + |β_กลุ่ม| + |β_ตลาด|)"""
    r, sec = world["r"], world["sec"]
    t, n = r.shape
    etf_sec = np.stack([r[:, sec == k].mean(axis=1) for k in range(N_SECTORS)], axis=1)
    etf_mkt = r.mean(axis=1)
    first = BURN - WIN + 1                               # หน้าต่างแรกจบที่แท่ง BURN พอดี
    yw = _windows(r, WIN)[first:]
    coef, resid = np.empty((len(yw), 3, n)), np.empty((len(yw), n, WIN))
    for k in range(N_SECTORS):
        f = np.stack([np.ones(t), etf_sec[:, k], etf_mkt], axis=1)
        coef[:, :, sec == k], resid[:, sec == k] = _rolling_ols(yw[:, sec == k], _windows(f, WIN)[first:])
    state, entry = hysteresis(*s_score(resid))
    cols = np.arange(n)
    b_sec, b_mkt = coef[entry, 1, cols], coef[entry, 2, cols]
    unit = state / (n * (1.0 + np.abs(b_sec) + np.abs(b_mkt)))
    weights = np.zeros((t, n + N_SECTORS + 1))           # หุ้น N ตัว + ตะกร้ากลุ่ม K ใบ + ตะกร้าตลาด
    weights[BURN:, :n] = unit
    for k in range(N_SECTORS):
        weights[BURN:, n + k] = -(unit * b_sec)[:, sec == k].sum(axis=1)
    weights[BURN:, -1] = -(unit * b_mkt).sum(axis=1)
    book = run_book(weights, np.column_stack([r, etf_sec, etf_mkt]))
    # สเปรดของหุ้น i เขียนเป็นน้ำหนักบนหุ้นทั้ง N ตัว (ตะกร้า = 1/10 ของทุกตัวในกลุ่ม · 1/30 ของทุกตัว)
    same = (sec[:, None] == sec[None, :]) / (n // N_SECTORS)
    c = coef[::REFIT]
    legs = np.eye(n) - c[:, 1, :, None] * same - c[:, 2, :, None] / n
    return book, float(factor_share(legs, world).mean())


def eigenportfolios(ret, k):
    """eigenportfolio k ตัวแรกจากเมทริกซ์สหสัมพันธ์ของผลตอบแทน → น้ำหนัก (k, N) = เวกเตอร์ลักษณะ ÷ sd ของหุ้น
    คืนสัดส่วนความแปรปรวนที่ k ตัวแรกอธิบายได้ด้วย"""
    val, vec = np.linalg.eigh(np.corrcoef(ret, rowvar=False))
    top = vec[:, ::-1][:, :k]
    return (top / ret.std(axis=0, ddof=1)[:, None]).T, float(val[::-1][:k].sum() / val.sum())


def pca_strategy(world):
    """s4: ทุก 21 แท่ง หา eigenportfolio 5 ตัวจาก 250 แท่งล่าสุด · ถดถอยผลตอบแทนหุ้นบนผลตอบแทนของ
    eigenportfolio (60 แท่ง) → ส่วนเหลือ → s-score กฎเดียวกับ s3 · ขากันความเสี่ยงคือหุ้นตัวอื่นทั้งตะกร้า"""
    r = world["r"]
    t, n = r.shape
    first = BURN - WIN + 1
    yw = _windows(r, WIN)[first:]
    nt = len(yw)
    fw, q_now, explained = np.ones((nt, N_PCA + 1, WIN)), np.empty((nt, N_PCA, n)), []
    for t0 in range(BURN, t, REFIT):                     # ใช้ข้อมูลถึงแท่ง t0 เท่านั้น แล้วใช้ไปอีก 21 แท่ง
        t1 = min(t0 + REFIT, t)
        q, share = eigenportfolios(r[t0 - CORR_WIN + 1:t0 + 1], N_PCA)
        fw[t0 - BURN:t1 - BURN, 1:] = _windows(r[t0 - WIN + 1:t1] @ q.T, WIN)
        q_now[t0 - BURN:t1 - BURN] = q
        explained.append(share)
    coef, resid = _rolling_ols(yw, fw)
    state, entry = hysteresis(*s_score(resid))
    legs = np.eye(n) - coef[:, 1:, :].transpose(0, 2, 1) @ q_now      # (nt, N, N): สเปรดของหุ้น i บนหุ้นทุกตัว
    held = legs[entry, np.arange(n)]                                   # น้ำหนัก ณ วันเปิดไม้ ถือจนปิด
    unit = state / (n * np.abs(held).sum(axis=2))
    weights = np.zeros((t, n))
    weights[BURN:] = (unit[:, :, None] * held).sum(axis=1)
    return run_book(weights, r), float(factor_share(legs[::REFIT], world).mean()), float(np.mean(explained))


def exp_universe(n_worlds=N_WORLDS):
    """รันสี่กลยุทธ์ในสี่จักรวาล × n_worlds โลก · โลกที่ w ของทุกจักรวาลใช้เลขสุ่มชุดเดียวกัน"""
    eg_cut = float(np.quantile(C.mc_null_eg(BURN, 2, n_sim=100_000, g=C.rng(611)), 0.05))
    out = {kind: {"scores": {s: [] for s in STRATEGIES}, "pnl": {s: [] for s in STRATEGIES},
                  "leftover": {"pair": [], "basket": [], "pca": []}, "pca_explained": [],
                  "best_passes": [], "chosen_pass": [], "all_pass": [],
                  "pair_sharpe": [], "pair_corr": []} for kind in UNIVERSES}
    g = C.rng(620)
    for w in range(n_worlds):
        base = base_world(g)
        for kind in UNIVERSES:
            world, o = dress_world(base, kind), out[kind]
            market = world["market"][BURN:]
            pairs, eg_chosen, eg_all = pick_pairs(world, 10)
            pair_books, left_pair = trade_pairs(world, pairs)
            basket_book, left_basket = basket_strategy(world)
            pca_book, left_pca, explained = pca_strategy(world)
            books = {"s1": pair_books[0], "s2": combine(pair_books), "s3": basket_book, "s4": pca_book}
            for s in STRATEGIES:
                o["scores"][s].append(score(books[s], market))
                o["pnl"][s].append(books[s]["net"])
            o["leftover"]["pair"].append(left_pair)
            o["leftover"]["basket"].append(left_basket)
            o["leftover"]["pca"].append(left_pca)
            o["pca_explained"].append(explained)
            o["best_passes"].append(float(eg_chosen[0] < eg_cut))
            o["chosen_pass"].append(float(np.sum(eg_chosen < eg_cut)))
            o["all_pass"].append(float(np.mean(eg_all < eg_cut)))
            nets = np.array([b["net"] for b in pair_books])
            o["pair_sharpe"].append(float(np.mean([C.perf_stats(x)["sharpe"] for x in nets])))
            corr = np.corrcoef(nets)
            o["pair_corr"].append(float(corr[np.triu_indices(len(nets), 1)].mean()))
    for o in out.values():                               # รายการของ dict → dict ของอาร์เรย์
        o["scores"] = {s: {k: np.array([row[k] for row in rows]) for k in rows[0]}
                       for s, rows in o["scores"].items()}
        o["pnl"] = {s: np.array(v) for s, v in o["pnl"].items()}
    return {"n_worlds": n_worlds, "eg_cut": eg_cut, "kinds": out}


def typical_world(kind_result):
    """โลกที่ Sharpe ของทั้งสี่กลยุทธ์อยู่ใกล้ค่ากลางของจักรวาลนั้นที่สุด (ใช้วาดตัวอย่าง)"""
    dist = 0.0
    for s in STRATEGIES:
        sh = kind_result["scores"][s]["sharpe"]
        spread = np.percentile(sh, 95) - np.percentile(sh, 5)
        dist = dist + np.abs(sh - np.median(sh)) / (spread if spread > 0 else 1.0)
    return int(np.argmin(dist))


# ═════════════════════════ 6d — สูตรความกว้าง ═════════════════════════
def breadth_sharpe(s, m, rho):
    """Sharpe ของพอร์ตที่ถือสเปรด m ตัว แต่ละตัว Sharpe = s และสัมพันธ์กันเฉลี่ย rho (น้ำหนักเท่ากัน)"""
    return s * math.sqrt(m / (1.0 + (m - 1.0) * rho))


def exp_breadth(s=0.5, ms=(1, 2, 5, 10, 20, 50, 100), rhos=(0.0, 0.1, 0.3), years=4000):
    table = {rho: {m: breadth_sharpe(s, m, rho) for m in ms} for rho in rhos}
    # โอกาสที่ผลตอบแทนทั้งปีติดลบ เมื่อผลรายปีแจกแจงปกติ = Φ(−Sharpe)
    loss = {rho: {m: _norm_cdf(-table[rho][m]) for m in ms} for rho in rhos}
    g = C.rng(612)
    days = C.DAYS_PER_YEAR
    mu = s / math.sqrt(days)                              # ผลตอบแทนเฉลี่ยรายแท่งของสเปรดที่ sd รายแท่ง = 1
    sim = {}
    for m, rho in ((1, 0.0), (10, 0.0), (10, 0.1), (10, 0.3)):
        common = g.standard_normal((years * days, 1))
        own = g.standard_normal((years * days, m))
        port = (mu + math.sqrt(rho) * common + math.sqrt(1.0 - rho) * own).mean(axis=1)
        yearly = port.reshape(years, days).sum(axis=1)
        sim[(m, rho)] = {"sharpe": float(port.mean() / port.std(ddof=1) * math.sqrt(days)),
                         "loss_year": float(np.mean(yearly < 0))}
    return {"s": s, "ms": list(ms), "rhos": list(rhos), "sharpe": table, "loss_year": loss,
            "ceiling": {rho: s / math.sqrt(rho) for rho in rhos if rho > 0}, "sim": sim, "sim_years": years}


# ═════════════════════════ 6f — Johansen แบบเปิดฝา [รอบสอง] ═════════════════════════
def johansen(x):
    """Johansen (VAR ระดับ 1 ล่าช้า มีค่าคงที่ไม่จำกัด) · x: (…, แท่ง, p) log ราคา
    ขั้นตอน: R0 = ΔX ลบค่าเฉลี่ย · R1 = X_{t−1} ลบค่าเฉลี่ย · S_ij = R_i'R_j / T
            แก้ |λ·S11 − S10·S00⁻¹·S01| = 0 → λ_1 ≥ … ≥ λ_p และเวกเตอร์ (คอลัมน์ = น้ำหนักของสเปรด)
    คืน (λ, เวกเตอร์, trace) โดย trace[r] = −T·Σ_{i>r} ln(1 − λ_i) ใช้ทดสอบ "มีสายจูงไม่เกิน r เส้น" """
    x = np.asarray(x, float)
    d, lag = np.diff(x, axis=-2), x[..., :-1, :]
    r0 = d - d.mean(axis=-2, keepdims=True)
    r1 = lag - lag.mean(axis=-2, keepdims=True)
    n = r0.shape[-2]
    tr = lambda a: np.swapaxes(a, -1, -2)                 # noqa: E731
    s00, s11, s01 = tr(r0) @ r0 / n, tr(r1) @ r1 / n, tr(r0) @ r1 / n
    a = tr(s01) @ np.linalg.solve(s00, s01)               # S10·S00⁻¹·S01 (สมมาตร)
    ch = np.linalg.cholesky(s11)                          # S11 = L·L' → แปลงเป็นปัญหาค่าลักษณะสมมาตรธรรมดา
    lam, u = np.linalg.eigh(np.linalg.solve(ch, tr(np.linalg.solve(ch, a))))
    lam, u = lam[..., ::-1], u[..., ::-1]
    vec = np.linalg.solve(tr(ch), u)
    trace = -n * np.cumsum(np.log1p(-lam)[..., ::-1], axis=-1)[..., ::-1]
    return lam, vec, trace


def _ols_weights(y, x):
    """สัมประสิทธิ์ OLS (มีค่าคงที่) ของหลายโลกพร้อมกัน · y (โลก, แท่ง) · x (โลก, แท่ง, p) → (โลก, p)"""
    xd = x - x.mean(axis=1, keepdims=True)
    yd = y - y.mean(axis=1, keepdims=True)
    xt = xd.transpose(0, 2, 1)
    return np.linalg.solve(xt @ xd, xt @ yd[:, :, None])[:, :, 0]


def _coint_worlds(n_worlds, n, g, w1=0.8, w2=0.5, shock_corr=0.0):
    """โลกที่มีสายจูงจริงหนึ่งเส้น: Y = 0.2 + 0.8·X1 + 0.5·X2 + ε · ε ดึงกลับ (half-life 12, σ 3%)
    shock_corr = 0   : แรงกระแทกของ ε ไม่เกี่ยวกับ X เลย และมีแต่ Y ที่ถูกดึงกลับ — กรณีที่ OLS ได้เปรียบที่สุด
    shock_corr = 0.6 : แรงกระแทกของ ε สัมพันธ์ 0.6 กับแรงกระแทกรวมของ X1 + X2
                       (ข่าวที่ขยับ X ดัน Y เลยสายจูงไปด้วยชั่วคราว — ซึ่งพบบ่อยกว่าในข้อมูลจริง)"""
    dx = 0.015 * g.standard_normal((n_worlds, n, 2))
    x = np.cumsum(dx, axis=1) + 4.0
    if shock_corr == 0.0:
        eps = C.ar1_batch(n_worlds, n, 12.0, 0.03, g)
    else:
        phi = C.phi_from_half_life(12.0)
        common = (dx[:, :, 0] + dx[:, :, 1]) / (0.015 * math.sqrt(2.0))          # sd = 1
        own = g.standard_normal((n_worlds, n))
        shock = 0.03 * math.sqrt(1.0 - phi * phi) * (shock_corr * common + math.sqrt(1.0 - shock_corr ** 2) * own)
        eps = np.empty((n_worlds, n))
        eps[:, 0] = 0.03 * g.standard_normal(n_worlds)                            # เริ่มจากการแจกแจงนิ่ง
        for t in range(1, n):
            eps[:, t] = phi * eps[:, t - 1] + shock[:, t]
    y = 0.2 + w1 * x[:, :, 0] + w2 * x[:, :, 1] + eps
    return np.concatenate([y[:, :, None], x], axis=2), eps


def _null_study(n_train, n_test, worlds, offset, chunk=2000):
    """โลกที่ไม่มีสายจูงเลย (random walk อิสระ ไม่มี drift) → การแจกแจงของ trace และของ ADF ของสเปรดที่
    "ค้นหาน้ำหนักมาแล้ว" (Johansen / OLS) ทั้งในช่วงที่ใช้ประมาณและนอกช่วง → ค่าวิกฤต 5% และอัตราผ่านปลอม"""
    g = C.rng(offset)
    null = {k: np.empty(worlds) for k in ("trace0", "plain_in", "plain_out", "joh_in", "joh_out", "ols_in", "ols_out")}
    for s in range(0, worlds, chunk):
        sl = slice(s, s + chunk)
        w = np.cumsum(g.standard_normal((chunk, n_train + n_test, 3)), axis=1)
        _, vec, trace = johansen(w[:, :n_train])
        null["trace0"][sl] = trace[:, 0]
        null["plain_in"][sl] = C.adf_stat_batch(w[:, :n_train, 0])
        null["plain_out"][sl] = C.adf_stat_batch(w[:, n_train:, 0])
        joh = (w @ vec[:, :, :1])[:, :, 0]                # สเปรดของเวกเตอร์ตัวแรก (น้ำหนักจากช่วง train)
        b = _ols_weights(w[:, :n_train, 0], w[:, :n_train, 1:])
        ols = w[:, :, 0] - (w[:, :, 1:] @ b[:, :, None])[:, :, 0]
        for name, spread in (("joh", joh), ("ols", ols)):
            null[name + "_in"][sl] = C.adf_stat_batch(spread[:, :n_train])
            null[name + "_out"][sl] = C.adf_stat_batch(spread[:, n_train:])
    g = C.rng(offset + 1)                                 # ทดสอบ "ไม่เกิน 1 เส้น": เหลือทิศทางสุ่มอีก 2 ทิศ
    trace1 = np.concatenate([johansen(np.cumsum(g.standard_normal((chunk, n_train, 2)), axis=1))[2][:, 0]
                             for _ in range(0, worlds, chunk)])
    cut = {"trace0": float(np.quantile(null["trace0"], 0.95)), "trace1": float(np.quantile(trace1, 0.95)),
           "adf_plain_in": float(np.quantile(null["plain_in"], 0.05)),
           "adf_plain_out": float(np.quantile(null["plain_out"], 0.05)),
           "adf_joh_in": float(np.quantile(null["joh_in"], 0.05)),
           "adf_ols_in": float(np.quantile(null["ols_in"], 0.05))}
    passes = {k: float(np.mean(null[k] < cut["adf_plain_" + k.split("_")[1]]))
              for k in ("plain_in", "plain_out", "joh_in", "joh_out", "ols_in", "ols_out")}
    return {"cut": cut, "null_pass": passes, "trace0": null["trace0"], "trace1": trace1}


def _power_study(n_train, n_test, worlds, offset, cut, true_w, shock_corr=0.0):
    """โลกที่มีสายจูงจริง: Johansen เจอบ่อยแค่ไหน · น้ำหนักแม่นแค่ไหนเทียบกับ OLS · นอกช่วงยังนิ่งไหม
    (ค่าวิกฤตชุดเดียวกับโลกที่ไม่มีสายจูง — ใต้สมมติฐานว่าง การแจกแจงของทั้ง trace และ EG ไม่ขึ้นกับ
    ความสัมพันธ์ของแรงกระแทก)"""
    xs, eps = _coint_worlds(worlds, n_train + n_test, C.rng(offset), *true_w, shock_corr=shock_corr)
    lam, vec, trace = johansen(xs[:, :n_train])
    wts = {"joh": -vec[:, 1:, 0] / vec[:, :1, 0], "ols": _ols_weights(xs[:, :n_train, 0], xs[:, :n_train, 1:])}
    found = trace[:, 0] > cut["trace0"]
    out = {"reject_r0": float(np.mean(found)), "pick_r1": float(np.mean(found & (trace[:, 1] <= cut["trace1"])))}
    adf = {}
    for name, w in wts.items():
        spread = xs[:, :, 0] - (xs[:, :, 1:] @ w[:, :, None])[:, :, 0]
        adf[name + "_in"] = C.adf_stat_batch(spread[:, :n_train])
        adf[name + "_out"] = C.adf_stat_batch(spread[:, n_train:])
        out[name + "_w1"] = _dist(w[:, 0])
        out[name + "_w1_err"] = float(np.median(np.abs(w[:, 0] - true_w[0])))
        out[name + "_w2_err"] = float(np.median(np.abs(w[:, 1] - true_w[1])))
        out[name + "_out_pass"] = float(np.mean(adf[name + "_out"] < cut["adf_plain_out"]))
    # การทดสอบแบบ Engle-Granger (OLS แล้ว ADF) เทียบกับเกณฑ์ที่ถูกของมันเอง — ไว้เทียบกำลังกับ trace
    out["ols_adf_pass"] = float(np.mean(adf["ols_in"] < cut["adf_ols_in"]))
    return out, {"xs": xs, "eps": eps, "lam": lam, "vec": vec, "trace": trace, "wts": wts, "adf": adf}


def _typical_coint_world(raw, true_w):
    """โลกที่ค่า trace · ขนาดความคลาดของน้ำหนัก · ADF นอกช่วง อยู่ใกล้ค่ากลางของทุกโลกที่สุด"""
    w = raw["wts"]["joh"]
    feats = [raw["trace"][:, 0], np.abs(w[:, 0] - true_w[0]), np.abs(w[:, 1] - true_w[1]), raw["adf"]["joh_out"]]
    dist = sum(np.abs(f - np.median(f)) / (np.percentile(f, 95) - np.percentile(f, 5)) for f in feats)
    return int(np.argmin(dist))


def exp_johansen(n_test=500, null_worlds=20_000, power_worlds=2000):
    """สินทรัพย์ 3 ตัว สายจูงจริง 1 เส้น · ทำสองความยาวของช่วงประมาณ (1,000 และ 500 แท่ง) เพื่อดูว่า "กินข้อมูล" แค่ไหน"""
    true_w = (0.8, 0.5)
    out = {"n_test": n_test, "null_worlds": null_worlds, "power_worlds": power_worlds, "true_w": true_w,
           "shock_corr": SHOCK_CORR, "studies": {}}
    for n_train, offset in ((1000, 680), (500, 684)):
        study = _null_study(n_train, n_test, null_worlds, offset)
        study["power"], raw = _power_study(n_train, n_test, power_worlds, offset + 2, study["cut"], true_w)
        study["power_corr"], _ = _power_study(n_train, n_test, power_worlds, offset + 3, study["cut"], true_w,
                                              shock_corr=SHOCK_CORR)
        out["studies"][n_train] = study
        if n_train == 1000:                               # โลกตัวอย่าง: เลือกจากโลกที่มีสายจูงจริงของช่วงประมาณยาว
            k = _typical_coint_world(raw, true_w)
            x, v = raw["xs"][k], raw["vec"][k, :, 0] / raw["vec"][k, 0, 0]      # ปรับให้น้ำหนักของ Y = 1
            spread = x @ v
            spread = spread - spread[:n_train].mean()
            out["demo"] = {
                "n_train": n_train, "x": x, "eps": raw["eps"][k], "spread": spread, "lam": raw["lam"][k],
                "trace": raw["trace"][k], "joh_w": raw["wts"]["joh"][k], "ols_w": raw["wts"]["ols"][k],
                "p_r0": float(np.mean(study["trace0"] >= raw["trace"][k, 0])),
                "p_r1": float(np.mean(study["trace1"] >= raw["trace"][k, 1])),
                "adf_in": float(raw["adf"]["joh_in"][k]), "adf_out": float(raw["adf"]["joh_out"][k]),
                "hl_in": C.fit_ar1(spread[:n_train])["half_life"],
                "hl_out": C.fit_ar1(spread[n_train:])["half_life"]}
    return out


# ═════════════════════════ run / figures ═════════════════════════
@functools.lru_cache(maxsize=1)
def run():
    """คำนวณทุกการทดลองของตอนที่ 6 (ผลเหมือนเดิมทุกครั้งที่รัน)"""
    res, cpu = {}, {}
    for name, fn in (("crit", exp_crit_vs_legs), ("fit_noise", exp_fit_noise), ("universe", exp_universe),
                     ("breadth", exp_breadth), ("johansen", exp_johansen)):
        t0 = time.process_time()
        res[name] = fn()
        cpu[name] = time.process_time() - t0
    res["cpu_seconds"] = cpu
    return res


def _fig_crit(r):
    out = {"n_obs": r["n_obs"], "n_sim": r["n_sim"], "lags": r["lags"]}
    for n, row in r["rows"].items():
        out[f"legs_{n}"] = {"crit1": C.rd(row["crit1"], 2), "crit5": C.rd(row["crit5"], 2),
                            "crit10": C.rd(row["crit10"], 2),
                            "false_pass_2leg_pct": C.pct(row["false_pass_2leg"], 0)}
    return out


def _fig_fit_noise(r):
    out = {"worlds": r["worlds"], "n_fit_bars": r["n_fit"], "n_hold_bars": r["n_hold"],
           "sigma_daily_pct": C.pct(r["sigma"], 1)}
    for n, row in r["rows"].items():
        # 3,000 โลก: sd_in คลาด ±0.03 จุด · rms_out ±0.2 จุด (พิมพ์จำนวนเต็ม) · half-life ±1 แท่ง
        out[f"legs_{n}"] = {"sd_in_pct": C.pct(row["sd_in"], 1), "rms_out_pct": C.pct(row["rms_out"], 0),
                            "out_over_in": C.rd(row["out_over_in"], 1),
                            "hl_in_median_bars": C.rd(row["hl_in"], 0),
                            "hl_under_30_pct": C.pct(row["hl_under_30"], 0),
                            "out_outside_2sd_pct": C.pct(row["outside_2sd"], 0)}
    return out


def _fig_strategy(sc):
    # ความแม่นของ Monte Carlo กำหนดจำนวนทศนิยม: ค่าเฉลี่ย Sharpe ของ 100 โลกคลาดได้ราว ±0.03–0.05
    # (เก็บไว้ใน sharpe_mean_se) จึงพิมพ์ทศนิยมเดียว · สัดส่วนโลกที่ขาดทุนคลาดได้ราว ±4 จุด
    sh = _dist(sc["sharpe"])
    n = len(sc["sharpe"])
    return {"sharpe_mean": C.rd(sh["mean"], 1),
            "sharpe_mean_se": C.rd(np.std(sc["sharpe"], ddof=1) / math.sqrt(n), 2),
            "sharpe_median": C.rd(sh["median"], 1),
            "sharpe_p5": C.rd(sh["p5"], 1), "sharpe_p95": C.rd(sh["p95"], 1),
            "sharpe_gross_mean": C.rd(sc["sharpe_gross"].mean(), 1),
            "sharpe_lag2_mean": C.rd(sc["sharpe_lag2"].mean(), 1),
            "loss_worlds_pct": C.pct(np.mean(sc["total"] < 0), 0),
            "max_dd_mean_pct": C.pct(sc["max_dd"].mean(), 0),
            # drawdown เมื่อปรับทุกกลยุทธ์ให้ผันผวน 10% ต่อปีเท่ากัน — ใช้เทียบข้ามกลยุทธ์ (ใช้ทุนไม่เท่ากัน)
            "max_dd_at_10vol_pct": C.pct(0.10 * sc["dd_over_vol"].mean(), 0),
            "abs_corr_market_mean": C.rd(sc["abs_corr_market"].mean(), 2),
            "turnover_per_year": C.rd(sc["turnover_year"].mean(), 1),
            "cost_per_year_pct": C.pct(COST * sc["turnover_year"].mean(), 1),
            "ann_return_mean_pct": C.pct(sc["ann_return"].mean(), 1),
            "ann_vol_mean_pct": C.pct(sc["ann_vol"].mean(), 1),
            "capital_used_mean_pct": C.pct(sc["used"].mean(), 0)}


def _paired(scores, a, b):
    """ผลต่าง Sharpe หลังต้นทุนของกลยุทธ์ a − b ในโลกเดียวกัน: ค่าเฉลี่ย · ความคลาด · % ของโลกที่ a ดีกว่า"""
    d = scores[a]["sharpe"] - scores[b]["sharpe"]
    return {"sharpe_diff_mean": C.rd(d.mean(), 1), "sharpe_diff_se": C.rd(d.std(ddof=1) / math.sqrt(len(d)), 2),
            "better_worlds_pct": C.pct(np.mean(d > 0), 0)}


def _fig_universe(r):
    out = {"n_worlds": r["n_worlds"], "n_stocks": N_STOCKS, "n_sectors": N_SECTORS,
           "n_bars": N_BARS, "burn_in_bars": BURN, "test_bars": N_BARS - BURN, "cost_bps": C.bps(COST, 0),
           "candidate_pairs": N_SECTORS * math.comb(N_STOCKS // N_SECTORS, 2),
           "eg_crit5_formation": C.rd(r["eg_cut"], 2),
           # |corr| ของอนุกรมที่ไม่สัมพันธ์กับตลาดเลยก็ไม่เป็นศูนย์: ค่าเฉลี่ยของ |r| ≈ √(2 / (π·n)) ที่ n = 1,500 แท่ง
           "abs_corr_noise_floor": C.rd(math.sqrt(2.0 / (math.pi * (N_BARS - BURN))), 2)}
    for kind, o in r["kinds"].items():
        k = {s: _fig_strategy(o["scores"][s]) for s in STRATEGIES}
        k["leftover_factor_pct"] = {name: C.pct(np.mean(v), 0) for name, v in o["leftover"].items()}
        k["pca_explained_pct"] = C.pct(np.mean(o["pca_explained"]), 0)
        # เทียบกลยุทธ์ "โลกต่อโลก" (ทุกกลยุทธ์เทรดโลกชุดเดียวกัน) — แม่นกว่าเทียบค่าเฉลี่ยสองตัวที่ปัดแล้วมาก
        k["paired"] = {f"{a}_minus_{b}": _paired(o["scores"], a, b)
                       for a, b in (("s2", "s1"), ("s3", "s2"), ("s4", "s2"), ("s4", "s3"))}
        k["selection"] = {"best_pair_passes_pct": C.pct(np.mean(o["best_passes"]), 0),
                          "chosen_passing_mean": C.rd(np.mean(o["chosen_pass"]), 0),
                          "all_candidates_pass_pct": C.pct(np.mean(o["all_pass"]), 0)}
        s_bar, rho = float(np.mean(o["pair_sharpe"])), float(np.mean(o["pair_corr"]))
        k["breadth_link"] = {"pair_sharpe_mean": C.rd(s_bar, 1), "pair_corr_mean": C.rd(rho, 2),
                             "formula_sharpe": C.rd(breadth_sharpe(s_bar, 10, rho), 1),
                             "measured_sharpe": k["s2"]["sharpe_mean"]}
        spec = UNIVERSES[kind]
        k["spec"] = {"perm_sigma_pct": C.pct(spec["perm_sigma"], 1),
                     "ou_sigma_lo_pct": C.pct(spec["ou_sigma"][0], 1) if spec["ou_sigma"] else 0.0,
                     "ou_sigma_hi_pct": C.pct(spec["ou_sigma"][1], 1) if spec["ou_sigma"] else 0.0}
        out[kind] = k
    return out


def _rho_key(rho):
    return "rho_" + f"{rho:g}".replace(".", "_")


def _fig_breadth(r):
    out = {"single_sharpe": r["s"], "sim_years": r["sim_years"], "sharpe": {}, "loss_year_pct": {},
           "ceiling": {_rho_key(rho): C.rd(v, 2) for rho, v in r["ceiling"].items()}, "sim": {}}
    for rho in r["rhos"]:
        out["sharpe"][_rho_key(rho)] = {f"m_{m}": C.rd(r["sharpe"][rho][m], 2) for m in r["ms"]}
        out["loss_year_pct"][_rho_key(rho)] = {f"m_{m}": C.pct(r["loss_year"][rho][m], 1) for m in r["ms"]}
    for (m, rho), v in r["sim"].items():          # 4,000 ปี: Sharpe คลาด ±0.02 · โอกาสขาดทุนคลาด ±0.7 จุด
        out["sim"].setdefault(_rho_key(rho), {})[f"m_{m}"] = {"sharpe": C.rd(v["sharpe"], 1),
                                                             "loss_year_pct": C.pct(v["loss_year"], 0)}
    return out


def _fig_power(p):
    # 2,000 โลก: อัตราคลาดได้ราว ±1 จุด → จำนวนเต็ม · ค่าคลาดกลางของน้ำหนัก ±0.002 → ทศนิยมสองตำแหน่ง
    return {"reject_r0_pct": C.pct(p["reject_r0"], 0), "pick_r1_pct": C.pct(p["pick_r1"], 0),
            "ols_adf_pass_pct": C.pct(p["ols_adf_pass"], 0),
            "joh_w1_err_median": C.rd(p["joh_w1_err"], 2), "joh_w2_err_median": C.rd(p["joh_w2_err"], 2),
            "ols_w1_err_median": C.rd(p["ols_w1_err"], 2), "ols_w2_err_median": C.rd(p["ols_w2_err"], 2),
            "joh_w1_p5": C.rd(p["joh_w1"]["p5"], 1), "joh_w1_p95": C.rd(p["joh_w1"]["p95"], 1),
            "ols_w1_p5": C.rd(p["ols_w1"]["p5"], 1), "ols_w1_p95": C.rd(p["ols_w1"]["p95"], 1),
            "joh_out_pass_pct": C.pct(p["joh_out_pass"], 0), "ols_out_pass_pct": C.pct(p["ols_out_pass"], 0)}


def _fig_johansen(r):
    d = r["demo"]
    long = r["studies"][d["n_train"]]
    # ค่าวิกฤตจาก 20,000 โลก: trace คลาด ±0.2 → จำนวนเต็ม · ADF คลาด ±0.02 → ทศนิยมหนึ่งตำแหน่ง
    # ค่าของโลกตัวอย่างเป็นตัวเลขของโลกเดียว (ไม่มีความคลาดจากการสุ่ม) จึงพิมพ์ละเอียดกว่าได้
    out = {"n_test_bars": r["n_test"], "null_worlds": r["null_worlds"], "power_worlds": r["power_worlds"],
           "shock_corr": r["shock_corr"],
           "demo": {"n_train_bars": d["n_train"], "true_w1": r["true_w"][0], "true_w2": r["true_w"][1],
                    "joh_w1": C.rd(d["joh_w"][0], 3), "joh_w2": C.rd(d["joh_w"][1], 3),
                    "ols_w1": C.rd(d["ols_w"][0], 3), "ols_w2": C.rd(d["ols_w"][1], 3),
                    "eig1": C.rd(d["lam"][0], 4), "eig2": C.rd(d["lam"][1], 4), "eig3": C.rd(d["lam"][2], 4),
                    "trace_r0": C.rd(d["trace"][0], 1), "trace_r1": C.rd(d["trace"][1], 1),
                    "trace_r0_crit5": C.rd(long["cut"]["trace0"], 0), "trace_r1_crit5": C.rd(long["cut"]["trace1"], 0),
                    "p_r0_pct": C.pct(d["p_r0"], 1), "p_r1_pct": C.pct(d["p_r1"], 0),
                    "adf_in": C.rd(d["adf_in"], 2), "adf_out": C.rd(d["adf_out"], 2),
                    "adf_in_crit5": C.rd(long["cut"]["adf_joh_in"], 1),
                    "adf_out_crit5": C.rd(long["cut"]["adf_plain_out"], 1),
                    "hl_in_bars": C.rd(d["hl_in"], 1), "hl_out_bars": C.rd(d["hl_out"], 1)}}
    for n_train, st in r["studies"].items():
        cut, npass = st["cut"], st["null_pass"]
        out[f"train_{n_train}"] = {
            "crit": {"trace_r0_crit5": C.rd(cut["trace0"], 0), "trace_r1_crit5": C.rd(cut["trace1"], 0),
                     "adf_plain_crit5": C.rd(cut["adf_plain_in"], 1),
                     "adf_plain_out_crit5": C.rd(cut["adf_plain_out"], 1),
                     "adf_after_johansen_crit5": C.rd(cut["adf_joh_in"], 1),
                     "adf_after_ols_crit5": C.rd(cut["adf_ols_in"], 1)},
            "null": {"plain_in_pass_pct": C.pct(npass["plain_in"], 0),
                     "plain_out_pass_pct": C.pct(npass["plain_out"], 0),
                     "johansen_in_pass_pct": C.pct(npass["joh_in"], 0),
                     "johansen_out_pass_pct": C.pct(npass["joh_out"], 0),
                     "ols_in_pass_pct": C.pct(npass["ols_in"], 0), "ols_out_pass_pct": C.pct(npass["ols_out"], 0)},
            "power": _fig_power(st["power"]),
            "power_corr": _fig_power(st["power_corr"])}
    return out


def _about(res):
    u, cr, fn, jo = res["universe"], res["crit"], res["fit_noise"], res["johansen"]
    return {
        "crit": f"ข้อมูลจำลอง: random walk อิสระ {cr['legs'][-1]} เส้น ยาว {cr['n_obs']} แท่ง {cr['n_sim']:,} โลก · "
                "ถดถอยเส้นแรกบนเส้นที่เหลือ N−1 เส้น (มีค่าคงที่) แล้ววัด ADF ของส่วนเหลือ (lags = 1) · "
                "ค่าวิกฤตคลาดได้ราว ±0.01 (ตัวเลขหลักสุดท้ายอาจขยับหนึ่งหน่วยเมื่อเปลี่ยนเลขสุ่ม) · "
                "ใกล้ตาราง MacKinnon (lags = 0) ภายใน 0.05",
        "fit_noise": f"ข้อมูลจำลอง: random walk อิสระ ผันผวนวันละ 1% · fit น้ำหนักด้วย OLS จาก {fn['n_fit']} แท่งแรก "
                     f"แล้วถือน้ำหนักเดิมอีก {fn['n_hold']} แท่ง · {fn['worlds']:,} โลก · ตัวเลขคือค่ากลาง (median) ของทุกโลก · "
                     "sd_in = sd ของสเปรดในช่วง fit · rms_out = ขนาดการแกว่งนอกช่วง fit วัดรอบเส้นกลางเดิม "
                     "(ระยะที่คนเทรดเห็นเมื่อยังใช้ μ เดิม) · half-life คลาดได้ราว ±1 แท่ง",
        "universe": f"ข้อมูลจำลอง: หุ้น {N_STOCKS} ตัว {N_SECTORS} กลุ่ม กลุ่มละ {N_STOCKS // N_SECTORS} ตัว · "
                    f"{N_BARS:,} แท่ง ({BURN} แท่งแรกใช้คัดเลือก ทดสอบ {N_BARS - BURN:,} แท่ง) · "
                    f"{u['n_worlds']} โลกต่อจักรวาล (โลกเดียวกันทั้งสี่จักรวาล ต่างกันแค่ส่วนเฉพาะตัว) · "
                    "c = 5 bps ต่อขาต่อเที่ยว · เงินรวมทุกขาไม่เกิน 1 เท่าของทุน",
        "universe_precision": f"ความแม่นของ {u['n_worlds']} โลก: ค่าเฉลี่ย Sharpe คลาดได้ราว ±0.03–0.05 (ดู sharpe_mean_se) "
                              "จึงพิมพ์ทศนิยมเดียว · ช่วง 5–95% คลาดได้ราว ±0.1 · สัดส่วนโลกที่ขาดทุนคลาดได้ราว ±4 จุด "
                              "(ใช้คำว่า 'ราว') · จะบอกว่ากลยุทธ์ไหนดีกว่า ให้ใช้ paired.* (ผลต่างในโลกเดียวกัน "
                              "คลาดเพียงราว ±0.03–0.06) แทนการลบค่าเฉลี่ยที่ปัดแล้วสองตัว",
        "universe_compare": "เทียบข้ามกลยุทธ์ด้วย Sharpe และ max_dd_at_10vol_pct (drawdown เมื่อปรับทุกกลยุทธ์ให้ผันผวน "
                            "10% ต่อปีเท่ากัน) เท่านั้น — กลยุทธ์ใช้ทุนไม่เท่ากัน (capital_used_mean_pct: คู่ราว 45–60% · "
                            "S3/S4 ราว 15–25%) ผลตอบแทนต่อปีและ max_dd_mean_pct ดิบจึงเทียบกันตรง ๆ ไม่ได้ · "
                            f"|corr กับตลาด| ของอนุกรมที่ไม่สัมพันธ์กับตลาดเลยยังได้ราว {math.sqrt(2.0 / (math.pi * (N_BARS - BURN))):.2f} จากความบังเอิญล้วน ๆ "
                            "(abs_corr_noise_floor) — ค่าที่ใกล้ระดับนี้แปลว่า 'แยกจากศูนย์ไม่ออก'",
        "universe_returns": "ผลตอบแทนหุ้น = bM·ตลาด + bS·กลุ่ม + bV·สไตล์ + Δu · sd รายวันของปัจจัย 1.0% / 0.7% / 0.5% · "
                            "bM ~ U(0.6, 1.5) · bS ~ U(0.6, 1.4) · bV ~ N(0, 0.6²) · "
                            "u = ส่วนที่ดึงกลับ (half-life 6–18 แท่ง) + ส่วนที่ไปแล้วไม่กลับ (random walk)",
        "universe_kinds": "thick: σ ของส่วนดึงกลับ 2.5–4.5% + ส่วนถาวร 0.3%/วัน · medium: 1.5–3.0% + 0.5%/วัน · "
                          "thin: 1.0–2.0% + 0.8%/วัน · none: ไม่มีส่วนดึงกลับเลย ส่วนถาวร 1.0%/วัน",
        "s1_s2": f"คัดคู่จากทุกคู่ในกลุ่มเดียวกัน ({N_SECTORS * math.comb(N_STOCKS // N_SECTORS, 2)} คู่) ด้วยค่า Engle-Granger "
                 f"ของ {BURN} แท่งแรก · s1 = คู่ที่ดีที่สุด · s2 = สิบคู่แรกที่ไม่ใช้หุ้นซ้ำ แบ่งทุนเท่ากัน · "
                 f"เดินหน้า train {BURN} แท่ง ประมาณใหม่ทุก {REFIT} แท่ง · เข้า z = 2 ออก z = 0 "
                 "(z วัดด้วย σ ที่ประมาณจากช่วง train)",
        "s3": f"หุ้นทุกตัวเทียบตะกร้ากลุ่ม + ตะกร้าตลาด (น้ำหนักเท่ากัน) · ถดถอยผลตอบแทน {WIN} แท่งล่าสุด · "
              f"s-score ของส่วนเหลือสะสม · เปิดเมื่อ |s| > {S_OPEN} ปิดเมื่อ |s| < {S_CLOSE} · "
              "เทรดเฉพาะเมื่อ AR(1) ของส่วนเหลือบอกว่าดึงกลับเร็วกว่าราว 30 แท่ง (b < 0.967) · "
              "ถือ hedge ของวันเปิดไม้จนปิด · แต่ละไม้ได้ทุน 1/30",
        "s4": f"ทุก {REFIT} แท่ง หา eigenportfolio {N_PCA} ตัวจากเมทริกซ์สหสัมพันธ์ {CORR_WIN} แท่งล่าสุด · "
              f"ถดถอยผลตอบแทนหุ้นบน eigenportfolio ({WIN} แท่ง) · กฎ s-score เดียวกับ s3",
        "leftover": "สัดส่วนความแปรปรวนของผลตอบแทนสเปรดที่ยังมาจากปัจจัยร่วม (ตลาด กลุ่ม สไตล์) "
                    "คิดจากเฉลยของโลกจำลอง เฉลี่ยทุกสเปรด ทุกจุดที่ประมาณค่าใหม่ ทุกโลก",
        "breadth": "สูตร Sharpe_พอร์ต = S·√(M / (1 + (M−1)ρ)) ที่ S = 0.5 · โอกาสขาดทุนทั้งปี = Φ(−Sharpe) "
                   f"(สมมติผลรายปีแจกแจงปกติ) · ตรวจด้วยการจำลอง {res['breadth']['sim_years']:,} ปี",
        "johansen": f"[รอบสอง] ข้อมูลจำลอง: Y = 0.2 + 0.8·X1 + 0.5·X2 + ε (X เป็น random walk วันละ 1.5% · "
                    f"ε half-life 12 แท่ง σ 3%) · ประมาณน้ำหนักจาก 1,000 หรือ 500 แท่งแรก แล้วทดสอบอีก {jo['n_test']} แท่ง "
                    f"ด้วยน้ำหนักเดิม · ค่าวิกฤตทุกตัวจำลองเองจาก random walk อิสระที่ไม่มี drift {jo['null_worlds']:,} โลก "
                    f"(ผ่านขั้นตอนเดียวกันทุกประการ · ข้อมูลที่มี drift ชัดต้องจำลองค่าวิกฤตใหม่) · "
                    f"วัดซ้ำในโลกที่มีสายจูงจริง {jo['power_worlds']:,} โลก สองแบบ — power: แรงกระแทกของ ε ไม่เกี่ยวกับ X "
                    f"(กรณีที่ OLS ได้เปรียบที่สุด) · power_corr: แรงกระแทกของ ε สัมพันธ์ {jo['shock_corr']:g} กับแรงกระแทกรวม "
                    "ของ X1 + X2 · โลกตัวอย่าง (demo) มาจากแบบแรก ถูกเลือกให้ใกล้ค่ากลางของโลกเหล่านั้นที่สุด",
        "johansen_precision": "อัตราจาก 2,000 โลกคลาดได้ราว ±1 จุด (พิมพ์จำนวนเต็ม) · ค่าวิกฤต trace คลาด ±0.2 "
                              "(จำนวนเต็ม) · ค่าวิกฤต ADF คลาด ±0.02 (ทศนิยมหนึ่ง) · ตัวเลขของโลกตัวอย่างเป็นค่าของโลกเดียว",
    }


def figures(res=None):
    """ตัวเลขทุกตัวที่ตอนที่ 6 ใช้ (ปัดแล้ว พร้อมพิมพ์)"""
    res = res or run()
    return {"about": _about(res), "crit": _fig_crit(res["crit"]), "fit_noise": _fig_fit_noise(res["fit_noise"]),
            "universe": _fig_universe(res["universe"]), "breadth": _fig_breadth(res["breadth"]),
            "johansen": _fig_johansen(res["johansen"])}


# ═════════════════════════ กราฟ ═════════════════════════
def _chart_crit(res, fg):
    r = res["crit"]
    legs = r["legs"]
    c1, c5, c10 = ([r["rows"][n][k] for n in legs] for k in ("crit1", "crit5", "crit10"))
    fp = [100.0 * r["rows"][n]["false_pass_2leg"] for n in legs]
    fig = V.Fig("sas-p6-crit-vs-legs", 760, 330)
    p = fig.panel((1.5, 8.5), V.auto_lim(c1, c10), x=58, y=72, w=300, h=200)
    p.grid().yaxis(title="ค่า ADF ที่ต้องติดลบกว่านี้").xaxis(ticks=legs, title="จำนวนขาในสเปรด (N)")
    p.line(legs, c10, V.MUTED, dash="2 4").line(legs, c1, V.MUTED, dash="7 4").line(legs, c5, V.BLUE, hero=True)
    p.scatter(legs, c5, V.BLUE, r=3.5, opacity=1.0)
    p.title("เกณฑ์ผ่านของ Engle-Granger").legend([("5%", V.BLUE), ("1%", V.MUTED, "line", "7 4"),
                                                  ("10%", V.MUTED, "line", "2 4")])
    q = fig.panel((1.5, 8.5), (0, 100), x=440, y=72, w=232, h=200)
    q.grid().yaxis(title="% ของโลกที่ไม่มีสายจูง แต่ “ผ่าน”", fmt=lambda v: f"{v:.0f}")
    q.bars(legs, fp, V.RED, labels=True, fmt=lambda v: f"{v:.0f}%")
    q.hline(5, label="5% ที่ตั้งใจ", pos="out").xaxis(ticks=legs, title="จำนวนขาในสเปรด (N)")
    q.title("ถ้ายังใช้เกณฑ์ของ 2 ขา")
    f = fg["crit"]
    return fig.svg(
        "ซ้าย: ค่าวิกฤตของ Engle-Granger ติดลบมากขึ้นเมื่อจำนวนขาเพิ่มจาก 2 เป็น 8 ขวา: สัดส่วนผ่านปลอมเมื่อใช้เกณฑ์ของ 2 ขา",
        f"ข้อมูลจำลอง {r['n_sim']:,} โลกที่ไม่มีสายจูงเลย ({r['n_obs']} แท่ง) · เกณฑ์ 5% ขยับจาก "
        f"{V.num(f['legs_2']['crit5'], 2)} (2 ขา) ไปถึง {V.num(f['legs_8']['crit5'], 2)} (8 ขา) · "
        f"ถ้ายังใช้เกณฑ์ของ 2 ขากับสเปรด 8 ขา จะ “ผ่าน” ถึง {f['legs_8']['false_pass_2leg_pct']:.0f}% "
        "ทั้งที่ไม่มีอะไรผูกกันเลย")


def _chart_fit_noise(res, fg):
    r = res["fit_noise"]
    legs = r["legs"]
    f = fg["fit_noise"]
    # ป้ายบนแท่งใช้ค่าที่ปัดแล้วชุดเดียวกับในบท (sd ในช่วง fit ทศนิยมหนึ่ง · นอกช่วงจำนวนเต็ม)
    return V.grouped_bars(
        "sas-p6-fit-noise", [f"N = {n}" for n in legs], [
            {"name": "ช่วงที่ใช้ fit (500 แท่งแรก)", "values": [f[f"legs_{n}"]["sd_in_pct"] for n in legs],
             "color": V.BLUE},
            {"name": "นอกช่วง fit (ถือน้ำหนักเดิมอีก 500 แท่ง)",
             "values": [f[f"legs_{n}"]["rms_out_pct"] for n in legs], "color": V.RED}],
        "แท่งเทียบขนาดการแกว่งของสเปรดในช่วงที่ใช้ fit กับนอกช่วง fit เมื่อจำนวนขาเพิ่มจาก 2 เป็น 15",
        f"ข้อมูลจำลอง {r['worlds']:,} โลก · random walk อิสระล้วน ๆ <b>ไม่มีสายจูงเลย</b> · ยิ่งใส่ขามาก สเปรดในช่วง fit "
        f"ยิ่งดูแคบและดูดึงกลับเร็ว (N = 15: half-life ที่วัดได้ {f['legs_15']['hl_in_median_bars']} แท่ง) "
        f"แต่พอพ้นช่วง fit กลับแกว่งกว้างกว่าเดิม {V.num(f['legs_15']['out_over_in'], 1)} เท่า — "
        "ความนิ่งที่เห็นมาจากการ fit ไม่ได้มาจากสายจูง",
        ylabel="ขนาดการแกว่งของสเปรด (% · ค่ากลางของทุกโลก)", fmt=lambda v: V.num(v, 1 if v < 10 else 0))


def _chart_strategies(res, fg):
    rows = []
    for kind in UNIVERSES:
        for s in STRATEGIES:
            f = fg["universe"][kind][s]
            rows.append({"label": f"{UNIVERSE_TH[kind]} · {STRATEGY_TH[s]}", "mid": f["sharpe_mean"],
                         "lo": f["sharpe_p5"], "hi": f["sharpe_p95"], "color": STRATEGY_COLOR[s]})
    u = fg["universe"]
    return V.dot_interval(
        "sas-p6-strategies", rows,
        "Sharpe หลังต้นทุนของสี่กลยุทธ์ในจักรวาลจำลองสี่แบบ: ค่าเฉลี่ยและช่วง 5–95% ของทุกโลก",
        f"ข้อมูลจำลอง {u['n_worlds']} โลกต่อแถว · โค้ดชุดเดียวกันทุกแถว ต่างกันที่ความแข็งของสายจูงในข้อมูล · "
        f"สายจูงปานกลาง: คู่เดียวได้เฉลี่ย {V.num(u['medium']['s1']['sharpe_mean'], 1)} แต่ช่วงกว้างตั้งแต่ "
        f"{V.num(u['medium']['s1']['sharpe_p5'], 1)} ถึง {V.num(u['medium']['s1']['sharpe_p95'], 1)} · "
        f"สิบคู่ได้ {V.num(u['medium']['s2']['sharpe_mean'], 1)} และช่วงแคบลงมาก · "
        "แต่เมื่อไม่มีสายจูง ทุกกลยุทธ์อยู่แถวศูนย์หรือต่ำกว่า — ความกว้างขยายขอบที่มีอยู่ ไม่ได้สร้างขอบขึ้นมาเอง",
        xlabel="Sharpe ต่อปี (หลังหักต้นทุน c = 5 bps)", mid_name="ค่าเฉลี่ย", row_h=30, fmt=lambda v: V.num(v, 1))


def _chart_cost_drag(res, fg):
    u = fg["universe"]
    light = lambda c: V.mix(c, "#ffffff", 0.55)           # noqa: E731
    series = []
    for s in ("s2", "s3"):
        series.append({"name": f"{STRATEGY_TH[s]} · ก่อนต้นทุน", "color": light(STRATEGY_COLOR[s]),
                       "values": [u[k][s]["sharpe_gross_mean"] for k in UNIVERSES]})
        series.append({"name": f"{STRATEGY_TH[s]} · หลังต้นทุน", "color": STRATEGY_COLOR[s],
                       "values": [u[k][s]["sharpe_mean"] for k in UNIVERSES]})
    return V.grouped_bars(
        "sas-p6-cost-drag", [UNIVERSE_TH[k] for k in UNIVERSES], series,
        "Sharpe เฉลี่ยก่อนและหลังต้นทุนของพอร์ตสิบคู่กับพอร์ตหุ้นเทียบตะกร้า ในจักรวาลสี่แบบ",
        f"ข้อมูลจำลอง {u['n_worlds']} โลกต่อแท่ง · S3 หมุนเงิน {V.num(u['medium']['s3']['turnover_per_year'], 1)} "
        f"เท่าของทุนต่อปี (S2: {V.num(u['medium']['s2']['turnover_per_year'], 1)} เท่า) จึงจ่ายต้นทุนมากกว่าหลายเท่า · "
        f"สายจูงอ่อน: S3 ก่อนต้นทุน {V.num(u['thin']['s3']['sharpe_gross_mean'], 1)} เหลือ "
        f"{V.num(u['thin']['s3']['sharpe_mean'], 1)} หลังต้นทุน · ไม่มีสายจูง: ก่อนต้นทุน "
        f"{V.num(u['none']['s3']['sharpe_gross_mean'], 1)} หลังต้นทุน {V.num(u['none']['s3']['sharpe_mean'], 1)}",
        ylabel="Sharpe ต่อปี (ค่าเฉลี่ยของทุกโลก)", fmt=lambda v: V.num(v, 1))


def _chart_leakage(res, fg):
    lf = fg["universe"]["medium"]["leftover_factor_pct"]
    names = {"pair": "คู่ (Y − β·X)", "basket": "หุ้น − ตะกร้ากลุ่ม − ตะกร้าตลาด", "pca": "หุ้น − eigenportfolio 5 ตัว"}
    return V.stacked_bars(
        "sas-p6-leakage", [{"label": names[k], "values": [lf[k], 100.0 - lf[k]]} for k in ("pair", "basket", "pca")],
        ["ปัจจัยร่วมที่ยังเหลือ", "เฉพาะตัว (สิ่งที่ตั้งใจเดิมพัน)"],
        "สัดส่วนความแปรปรวนของผลตอบแทนสเปรดที่ยังมาจากปัจจัยร่วม เทียบสเปรดสามแบบ",
        f"ข้อมูลจำลอง จักรวาลสายจูงปานกลาง · คิดจากเฉลยของโลกจำลอง · สเปรดของคู่ยังมีปัจจัยร่วมเหลือ "
        f"{V.num(lf['pair'], 0)}% ของความแปรปรวน หุ้นเทียบตะกร้าเหลือ {V.num(lf['basket'], 0)}% "
        f"และส่วนเหลือ PCA เหลือ {V.num(lf['pca'], 0)}% — ขาที่มากขึ้นช่วยตัดสิ่งที่ไม่ได้ตั้งใจเดิมพันออกได้สะอาดกว่า",
        colors=[V.RED, "#94a3b8"])


def _chart_equity(res, fg):
    panels = []
    for kind in ("medium", "none"):
        o = res["universe"]["kinds"][kind]
        w = typical_world(o)
        curves = []
        for s in STRATEGIES:
            pnl, vol = o["pnl"][s][w], o["scores"][s]["ann_vol"][w]
            curves.append(100.0 * np.cumsum(pnl) * (0.10 / vol if vol > 0 else 0.0))
        panels.append({"y": curves, "names": [STRATEGY_TH[s] for s in STRATEGIES],
                       "color": [STRATEGY_COLOR[s] for s in STRATEGIES], "zero": True,
                       "title": f"จักรวาล “{UNIVERSE_TH[kind]}” — โลกตัวอย่างหนึ่งใบ"})
    return V.stacked_panels(
        "sas-p6-equity", panels,
        "ผลตอบแทนสะสมของสี่กลยุทธ์ในโลกตัวอย่าง: บนคือจักรวาลสายจูงปานกลาง ล่างคือจักรวาลที่ไม่มีสายจูง",
        "ข้อมูลจำลอง · โลกตัวอย่างถูก <b>เลือก</b> ให้ Sharpe ของทั้งสี่กลยุทธ์ใกล้ค่ากลางของจักรวาลนั้นที่สุด · "
        "ทุกเส้นถูกปรับขนาดหลังจบให้ผันผวน 10% ต่อปีเท่ากัน (เพื่อเทียบรูปร่างเท่านั้น) หน่วยเป็น % ของทุน หลังหักต้นทุน · "
        "บน: เส้นของพอร์ตหลายสเปรดเรียบกว่าคู่เดียวมาก · ล่าง: โค้ดเดียวกันทุกบรรทัด แต่ไม่มีสายจูงให้เก็บ",
        xlabel="แท่งที่ (วัน) นับจากเริ่มช่วงทดสอบ", panel_h=170)


def _chart_breadth(res, fg):
    r = res["breadth"]
    colors = (V.BLUE, V.AMBER, V.RED)
    f = fg["breadth"]
    sharpe = V.line_chart(
        "sas-p6-breadth", r["ms"],
        [{"name": f"ρ = {rho:g}", "y": [r["sharpe"][rho][m] for m in r["ms"]], "color": c}
         for rho, c in zip(r["rhos"], colors)],
        "Sharpe ของพอร์ตตามจำนวนสเปรด M สามระดับความสัมพันธ์ระหว่างสเปรด",
        f"สูตร S·√(M / (1 + (M−1)ρ)) ที่ S = 0.5 ต่อสเปรด · ถ้าสเปรดไม่สัมพันธ์กันเลย 100 ตัวให้ "
        f"{V.num(f['sharpe']['rho_0']['m_100'], 2)} · แต่ถ้า ρ = 0.3 ได้แค่ "
        f"{V.num(f['sharpe']['rho_0_3']['m_100'], 2)} และไม่มีวันเกิน {V.num(f['ceiling']['rho_0_3'], 2)} "
        "ไม่ว่าจะเพิ่มอีกกี่ตัว",
        xlabel="จำนวนสเปรดในพอร์ต (M)", ylabel="Sharpe ต่อปีของพอร์ต", categories=True, zero=True)
    loss = V.line_chart(
        "sas-p6-breadth-loss", r["ms"],
        [{"name": f"ρ = {rho:g}", "y": [100 * r["loss_year"][rho][m] for m in r["ms"]], "color": c}
         for rho, c in zip(r["rhos"], colors)],
        "โอกาสที่ผลตอบแทนทั้งปีติดลบ ตามจำนวนสเปรด M สามระดับความสัมพันธ์",
        f"โอกาสขาดทุนทั้งปี = Φ(−Sharpe) · สเปรดเดียว (Sharpe 0.5) ขาดทุนราว "
        f"{V.num(f['loss_year_pct']['rho_0']['m_1'], 0)}% ของปี · สิบสเปรดที่ ρ = 0.1 เหลือ "
        f"{V.num(f['loss_year_pct']['rho_0_1']['m_10'], 0)}% · แต่ที่ ρ = 0.3 ยังเหลือ "
        f"{V.num(f['loss_year_pct']['rho_0_3']['m_10'], 0)}%",
        xlabel="จำนวนสเปรดในพอร์ต (M)", ylabel="โอกาสขาดทุนทั้งปี (%)", categories=True, zero=True)
    return sharpe, loss


def _chart_johansen(res, fg):
    r = res["johansen"]
    d, f = r["demo"], fg["johansen"]["demo"]
    n_train = d["n_train"]
    return V.stacked_panels(
        "sas-p6-johansen", [
            {"y": [d["x"][:, 0], d["x"][:, 1], d["x"][:, 2]], "names": ["Y", "X1", "X2"],
             "title": "log ราคาของสินทรัพย์สามตัว"},
            {"y": [100 * d["eps"], 100 * d["spread"]], "names": ["ε จริง (เฉลย)", "สเปรดที่ Johansen หาได้"],
             "color": [V.MUTED, V.BLUE], "zero": True,
             "title": f"สเปรด (%) — น้ำหนักจาก {n_train:,} แท่งแรกเท่านั้น"}],
        "บน: log ราคาของสินทรัพย์สามตัว ล่าง: สเปรดที่ Johansen ประมาณได้เทียบกับ ε จริง ทั้งช่วงประมาณและช่วงทดสอบ",
        f"ข้อมูลจำลอง Y = 0.2 + 0.8·X1 + 0.5·X2 + ε · โลกตัวอย่างที่ <b>เลือก</b> ให้ใกล้ค่ากลาง · Johansen ได้น้ำหนัก "
        f"{V.num(f['joh_w1'], 2)} และ {V.num(f['joh_w2'], 2)} (เฉลย 0.8 และ 0.5) · ADF ของสเปรดในช่วงทดสอบที่ไม่ได้ใช้ประมาณ = "
        f"{V.num(f['adf_out'], 2)} (เกณฑ์ 5% ราว {V.num(f['adf_out_crit5'], 1)})",
        xlabel="แท่งที่ (วัน)", panel_h=140,
        xbands=[(0, n_train, "ช่วงที่ใช้ประมาณน้ำหนัก"),
                (n_train, len(d["spread"]) - 1, "ช่วงทดสอบ (น้ำหนักเดิม)", V.AMBER)])


def _chart_overfit(res, fg):
    j = fg["johansen"]
    f = j["train_1000"]["null"]
    return V.grouped_bars(
        "sas-p6-overfit", ["ไม่ค้นหาน้ำหนักเลย\n(เส้นเดียว)", "OLS 3 ขา", "Johansen 3 ขา"], [
            {"name": "ในช่วงที่ใช้ประมาณน้ำหนัก",
             "values": [f["plain_in_pass_pct"], f["ols_in_pass_pct"], f["johansen_in_pass_pct"]], "color": V.RED},
            {"name": "นอกช่วง (น้ำหนักเดิม)",
             "values": [f["plain_out_pass_pct"], f["ols_out_pass_pct"], f["johansen_out_pass_pct"]], "color": V.BLUE}],
        "สัดส่วนของโลกที่ไม่มีสายจูงแต่ผ่านเกณฑ์ ADF 5% แบบธรรมดา เทียบวิธีหาน้ำหนักสามแบบ ในช่วง fit และนอกช่วง fit",
        f"ข้อมูลจำลอง {j['null_worlds']:,} โลก · random walk อิสระ 3 เส้น <b>ไม่มีสายจูงเลย</b> · ถ้าเอาสเปรดที่ค้นหาน้ำหนักมาแล้ว"
        f"ไปเทียบกับเกณฑ์ ADF ธรรมดา: OLS ผ่านปลอม {V.num(f['ols_in_pass_pct'], 0)}% · Johansen ผ่านปลอม "
        f"{V.num(f['johansen_in_pass_pct'], 0)}% · นอกช่วง fit ทั้งคู่กลับมาแถว 5% เท่ากับการสุ่ม — "
        "ยิ่งวิธีค้นหาเก่ง ยิ่งต้องตรวจนอกช่วง fit",
        ylabel="% ของโลกที่ “ผ่าน” ทั้งที่ไม่มีสายจูง", fmt=lambda v: f"{v:.0f}%", hlines=[(5.0, "5% ที่ตั้งใจ")])


def charts(res=None):
    """กราฟของตอนที่ 6 — {ชื่อ: html}"""
    res = res or run()
    fg = figures(res)
    breadth, breadth_loss = _chart_breadth(res, fg)
    return {
        "sas-p6-crit-vs-legs": _chart_crit(res, fg),
        "sas-p6-fit-noise": _chart_fit_noise(res, fg),
        "sas-p6-strategies": _chart_strategies(res, fg),
        "sas-p6-cost-drag": _chart_cost_drag(res, fg),
        "sas-p6-leakage": _chart_leakage(res, fg),
        "sas-p6-equity": _chart_equity(res, fg),
        "sas-p6-breadth": breadth,
        "sas-p6-breadth-loss": breadth_loss,
        "sas-p6-johansen": _chart_johansen(res, fg),
        "sas-p6-overfit": _chart_overfit(res, fg),
    }


# ═════════════════════════ สรุปเมื่อรันตรง ๆ ═════════════════════════
def _print_summary(res):
    fg = figures(res)
    line = "─" * 78
    print("ห้องทดลองตอนที่ 6 — มากกว่าสองตัว (ข้อมูลจำลองทั้งหมด)")
    print(line)
    f = fg["crit"]
    print(f"6a  เกณฑ์ผ่าน Engle-Granger ตามจำนวนขา ({f['n_obs']} แท่ง · {f['n_sim']:,} โลกที่ไม่มีสายจูง)")
    print("    ขา   เกณฑ์ 5%   เกณฑ์ 1%   ผ่านปลอมถ้าใช้เกณฑ์ของ 2 ขา")
    for n in res["crit"]["legs"]:
        row = f[f"legs_{n}"]
        print(f"    {n:>2}   {row['crit5']:>7.2f}   {row['crit1']:>7.2f}   {row['false_pass_2leg_pct']:>5}%")
    print(line)
    f = fg["fit_noise"]
    print(f"6b  fit น้ำหนักบน random walk อิสระ ({f['worlds']:,} โลก · fit {f['n_fit_bars']} แท่ง ถือต่อ {f['n_hold_bars']} แท่ง)")
    print("    ขา   sd ในช่วง fit   แกว่งนอกช่วง   นอก÷ใน   half-life ที่วัดได้   นอกแถบ ±2sd")
    for n in res["fit_noise"]["legs"]:
        row = f[f"legs_{n}"]
        print(f"    {n:>2}   {row['sd_in_pct']:>10.1f}%   {row['rms_out_pct']:>10}%   {row['out_over_in']:>5.1f}x"
              f"   {row['hl_in_median_bars']:>10} แท่ง   {row['out_outside_2sd_pct']:>6}%")
    print(line)
    u = fg["universe"]
    print(f"6c  จักรวาลหุ้นจำลอง {u['n_stocks']} ตัว · {u['n_worlds']} โลกต่อจักรวาล · ทดสอบ {u['test_bars']:,} แท่ง · c = {u['cost_bps']} bps")
    print(f"    (Sharpe เฉลี่ยคลาดได้ราว ±SE ในวงเล็บเหลี่ยม · DD@10% = drawdown เมื่อปรับให้ผันผวน 10%/ปีเท่ากัน · "
          f"|corr| ระดับบังเอิญ ≈ {u['abs_corr_noise_floor']})")
    for kind in UNIVERSES:
        k = u[kind]
        print(f"  [{kind}] {UNIVERSE_TH[kind]}")
        print("        Sharpe หลังต้นทุน [±SE] (5–95%)  ก่อนต้นทุน  lag2  โลกที่ขาดทุน  DD@10%  |corr ตลาด|  หมุนเงิน/ปี  ใช้ทุน")
        for s in STRATEGIES:
            r = k[s]
            print(f"    {s}  {r['sharpe_mean']:>5.1f} [±{r['sharpe_mean_se']:.2f}] ({r['sharpe_p5']:>4.1f} ถึง {r['sharpe_p95']:>4.1f})"
                  f"   {r['sharpe_gross_mean']:>5.1f}  {r['sharpe_lag2_mean']:>5.1f}   {r['loss_worlds_pct']:>5}%   "
                  f"{r['max_dd_at_10vol_pct']:>4}%   {r['abs_corr_market_mean']:>6.2f}   {r['turnover_per_year']:>6.1f} เท่า"
                  f"   {r['capital_used_mean_pct']:>3}%")
        print("    เทียบในโลกเดียวกัน (ผลต่าง Sharpe ±SE · % ของโลกที่ตัวแรกดีกว่า): " + " · ".join(
            f"{name.replace('_minus_', '−')} {v['sharpe_diff_mean']:+.1f} ±{v['sharpe_diff_se']:.2f} ({v['better_worlds_pct']}%)"
            for name, v in k["paired"].items()))
        lf, sel, bl = k["leftover_factor_pct"], k["selection"], k["breadth_link"]
        print(f"    ปัจจัยร่วมที่ยังเหลือในสเปรด: คู่ {lf['pair']}% · ตะกร้า {lf['basket']}% · PCA {lf['pca']}%")
        print(f"    การคัดคู่: คู่ที่ดีที่สุดผ่าน EG 5% ใน {sel['best_pair_passes_pct']}% ของโลก · "
              f"ใน 10 คู่ที่เลือก ผ่านเฉลี่ย {sel['chosen_passing_mean']} คู่ · ทุกคู่ที่เป็นไปได้ผ่าน {sel['all_candidates_pass_pct']}%")
        print(f"    สูตรความกว้าง: Sharpe เฉลี่ยรายคู่ {bl['pair_sharpe_mean']} · ρ เฉลี่ย {bl['pair_corr_mean']} "
              f"→ สูตรบอก {bl['formula_sharpe']} · วัดได้ {bl['measured_sharpe']}")
    print(line)
    b = fg["breadth"]
    print("6d  สูตรความกว้าง (S = 0.5 ต่อสเปรด): Sharpe ของพอร์ต / โอกาสขาดทุนทั้งปี")
    print("    ρ      " + "".join(f"M={m:<9}" for m in res["breadth"]["ms"]))
    for rho in res["breadth"]["rhos"]:
        key = _rho_key(rho)
        print(f"    {rho:<5g}  " + "".join(
            f"{b['sharpe'][key][f'm_{m}']:.2f}/{b['loss_year_pct'][key][f'm_{m}']:>4.1f}%  " for m in res["breadth"]["ms"]))
    print(f"    เพดานเมื่อ M → ∞: ρ = 0.1 → {b['ceiling']['rho_0_1']} · ρ = 0.3 → {b['ceiling']['rho_0_3']}")
    sim = b["sim"]
    print(f"    จำลองตรวจสูตร ({b['sim_years']:,} ปี) M = 10: ρ = 0 → {sim['rho_0']['m_10']['sharpe']} · "
          f"ρ = 0.1 → {sim['rho_0_1']['m_10']['sharpe']} · ρ = 0.3 → {sim['rho_0_3']['m_10']['sharpe']}")
    print(line)
    j = fg["johansen"]
    d = j["demo"]
    print(f"6f  [รอบสอง] Johansen กับสินทรัพย์ 3 ตัว (สายจูงจริง 1 เส้น) · ทดสอบนอกช่วง {j['n_test_bars']} แท่ง")
    print(f"    โลกตัวอย่าง (ประมาณจาก {d['n_train_bars']:,} แท่ง) — น้ำหนัก (เฉลย 0.8, 0.5): "
          f"Johansen {d['joh_w1']}, {d['joh_w2']} · OLS {d['ols_w1']}, {d['ols_w2']}")
    print(f"      trace: ไม่มีสายจูงเลย? {d['trace_r0']} (เกณฑ์ 5% = {d['trace_r0_crit5']}) · "
          f"มีไม่เกิน 1 เส้น? {d['trace_r1']} (เกณฑ์ 5% = {d['trace_r1_crit5']})")
    print(f"      ADF ของสเปรด: ในช่วงประมาณ {d['adf_in']} (เกณฑ์ที่ถูกหลังค้นหา = {d['adf_in_crit5']}) · "
          f"นอกช่วง {d['adf_out']} (เกณฑ์ = {d['adf_out_crit5']})")
    for n_train in res["johansen"]["studies"]:
        st = j[f"train_{n_train}"]
        nu = st["null"]
        print(f"    ประมาณจาก {n_train:,} แท่ง (ค่าวิกฤต 5%: trace {st['crit']['trace_r0_crit5']} / {st['crit']['trace_r1_crit5']}"
              f" · ADF หลัง Johansen {st['crit']['adf_after_johansen_crit5']} · หลัง OLS {st['crit']['adf_after_ols_crit5']})")
        print(f"      โลกที่ไม่มีสายจูง ({j['null_worlds']:,} โลก) ผ่านเกณฑ์ ADF ธรรมดา: ไม่ค้นหา {nu['plain_in_pass_pct']}% · "
              f"Johansen ใน {nu['johansen_in_pass_pct']}% / นอก {nu['johansen_out_pass_pct']}% · "
              f"OLS ใน {nu['ols_in_pass_pct']}% / นอก {nu['ols_out_pass_pct']}%")
        for key, what in (("power", "แรงกระแทกของ ε อิสระจาก X"), ("power_corr", f"แรงกระแทกสัมพันธ์ {j['shock_corr']:g}")):
            pw = st[key]
            print(f"      โลกที่มีสายจูงจริง ({j['power_worlds']:,} โลก · {what}): trace เจอ {pw['reject_r0_pct']}% "
                  f"(เลือก 1 เส้นถูก {pw['pick_r1_pct']}%) · OLS+ADF เจอ {pw['ols_adf_pass_pct']}% · "
                  f"ค่าคลาดกลางของน้ำหนัก Johansen {pw['joh_w1_err_median']} / OLS {pw['ols_w1_err_median']} · "
                  f"ช่วง 5–95% ของน้ำหนักตัวแรก Johansen {pw['joh_w1_p5']}–{pw['joh_w1_p95']} / OLS {pw['ols_w1_p5']}–{pw['ols_w1_p95']}")
    print(line)
    cpu = res["cpu_seconds"]
    print("เวลา CPU (วินาที): " + " · ".join(f"{k} {v:.1f}" for k, v in cpu.items())
          + f" · รวม {sum(cpu.values()):.1f}")


if __name__ == "__main__":
    _print_summary(run())
