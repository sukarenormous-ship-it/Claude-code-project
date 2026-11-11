#!/usr/bin/env python3
"""ห้องทดลองของตอนที่ 3 — "Y − βX = ε: ประกอบสเปรดให้ถูก" (สไลด์ 4)

ทุกตัวเลขมาจากข้อมูลจำลองที่ "รู้เฉลย" (sas_core.demo_pair / make_pair) ไม่มีข้อมูลตลาดจริง
คู่ตัวอย่าง (good / drift / fake) ถูกเลือกให้เห็นอาการชัด — ข้อสรุปทั่วไปให้ดูค่าจาก Monte Carlo หลายร้อย–หลายพันโลกเสมอ

การทดลอง (คีย์ใน figures() ใช้ชื่อในวงเล็บ)
  3a (beta)     β สี่วิธีจากข้อมูลช่วงเดียวกัน: OLS ของ Y บน X · OLS ของ X บน Y แล้วกลับเศษส่วน · TLS · β จากผลตอบแทน
                ทั้งช่วง train (750 แท่งแรก) ทั้งช่วง (1,500) และครึ่งหลัง — คู่ good เทียบกับค่าจริง 1.4
                คู่ fake ใช้เป็นตัวเปรียบเทียบ: β ที่ "ไม่ยอมนิ่ง" ระหว่างช่วง/ระหว่างวิธี คืออาการของคู่ที่ไม่มีสายจูง
                + ผลของการลืม α (no_alpha) และของการถดถอยบนราคาดิบแทน log (price_levels)
  3b (eg)       Engle-Granger สองขั้นบนช่วง train · ค่าวิกฤตจำลองเอง 100,000 โลกที่ n = 750, 2 ขา, lags = 1
                p-value · และ "อัตราผ่านปลอม" ถ้าเอาเกณฑ์ 5% ของ ADF ธรรมดา (อนุกรมเดียว) มาใช้กับ ε̂
                + อัตราผ่านที่วัดจริงของโลก good / drift / fake เมื่อมีข้อมูล 250 / 500 / 750 / 1,500 แท่ง
                  (4,000 โลกต่อแบบ — ไม่เดาว่า drift ต้องตก หรือว่าคู่จริงต้องผ่าน)
  3c (ar1)      AR(1) ของ ε̂ ช่วง train → φ, κ, half-life, μ, σ เทียบกับค่าจริง (φ 0.944 · 12 แท่ง · 0 · 3%)
  3d (oos)      เอา α̂, β̂, μ̂, σ̂ ของช่วง train ไปวัด 750 แท่งหลังที่ไม่เคยเห็น: ค่าเฉลี่ยเลื่อนกี่ σ · sd โตกี่เท่า
                · ADF · สัดส่วนแท่งที่หลุด ±2σ — good เทียบ drift (และ fake)
  3e (rolling)  β ของ OLS จาก 250 แท่งล่าสุด (ไม่มองอนาคต): ช่วงที่มันแกว่งของ good / drift / fake
  (remedy)      ยาแก้ของคู่ drift: สเปรด β คงที่ (นอกตัวอย่าง) เทียบสเปรด walk-forward (ประมาณใหม่จาก 250 แท่งล่าสุด
                ทุก 21 แท่ง) — ADF และ half-life บน 750 แท่งหลังเหมือนกัน · ADF ของสเปรดที่ถูก refit เรื่อย ๆ
                เทียบกับตาราง ADF ธรรมดาไม่ได้ จึงจำลองเกณฑ์ของมันจากโลก fake 1,000 โลก (remedy.wf_null)
  3f (money)    แปล β̂ เป็นเงิน: ขา Y 100,000 บาท → ขา X กี่บาท กี่หุ้น · ε ขยับ 1σ = กี่บาท · ต้นทุนไปกลับกี่บาท
  3g (wrong)    ใช้ β = 1 (อัตราส่วนราคา) กับคู่ที่ β จริง 1.4: ส่วนที่รั่ว (β − 1)·X เป็น random walk
                → sd ของการเปลี่ยนแปลงข้าม h แท่งโตไม่หยุด · half-life ยืด · แต่ ADF ยังผ่านได้บ่อย (วัดจริง)
  3h (mc)       3,000 โลก good: การกระจายของ β̂ − β (สี่วิธี) และของ half-life ที่ประมาณได้ เมื่อมีข้อมูล 250 / 750 / 1,500 แท่ง
  Monte Carlo ของ 3a/3d/3e/ยาแก้/3g ใช้ 500 โลกต่อแบบของคู่ คิดทุกขั้นแบบเดียวกับคู่ตัวอย่าง (ทุกโลกถูกนับ ไม่คัดทิ้ง)

ข้อตกลงของตอนนี้
  • ไม่มีตัวเลขไหนมองอนาคต: α̂, β̂, μ̂, σ̂ มาจากช่วง train แล้วใช้กับช่วงหลัง · rolling β ใช้ 250 แท่งที่จบ ณ แท่งนั้น
    สเปรด walk-forward ใช้ C.walk_forward_pair (ประมาณจากข้อมูลก่อนหน้าเท่านั้น)
    β "ทั้งช่วง" (full) มีไว้เทียบว่า β นิ่งแค่ไหน ไม่ได้ถูกนำไปใช้ตัดสินใจ
  • ไม้บรรทัดของ z ในตอนนี้ = ค่าเฉลี่ยและ sd ตัวอย่างของ ε̂ ช่วง train (แบบเดียวกับตอนที่ 4)
    σ_eq จาก AR(1) รายงานไว้ข้างกัน (ต่างกันไม่ถึง 1% ในคู่ good)
  • ε เป็นผลต่างของ log price → คูณ 100 แล้วอ่านเป็น "ราว ๆ %" ได้ (คีย์ลงท้าย _pct)
  • ค่าวิกฤตที่พิมพ์ในบท (n = 750) จำลอง 100,000 โลก (คลาดราว ±0.01) · ค่าที่ใช้นับอัตราผ่านที่ n = 250, 500, 1,500
    จำลอง 20,000 โลก (±0.03 จึงเก็บทศนิยมเดียว)
  • ตัวเลข Monte Carlo ปัดหยาบตามความแม่นที่มีจริง (ตรวจแล้วด้วยการเปลี่ยน seed): อัตรา % เป็นจำนวนเต็ม พร้อม
    moe95_pct = ขอบความคลาด 95% กรณีแย่สุด · p-value จากการจำลองเป็นเลขนัยสำคัญตัวเดียว และเมื่อมีโลกที่ติดลบกว่า
    ไม่ถึง 10 โลก บอกได้แค่ "< ขอบบน" (p_text) · half-life จาก Monte Carlo ส่วนใหญ่เป็นจำนวนเต็ม
  • half-life มีความหมายก็ต่อเมื่อผ่านการทดสอบแล้วเท่านั้น (คู่ fake ก็ให้ half-life เป็นเลขได้)
  • ตัวกรอง Kalman สำหรับ β ที่เคลื่อน "ตั้งใจไม่ทำ" ในตอนนี้ — อยู่ในหนังสือเล่มเดิม (statarb-ch15, statarb-ch23)
    ที่นี่ใช้ rolling OLS ซึ่งเป็นวิธีที่ง่ายที่สุดที่ไม่มองอนาคต เพื่อให้เห็นแนวคิดก่อนเทคนิค

วิธีรัน
    python3 tools/sas_exp3.py          # พิมพ์สรุปตัวเลขสำคัญ (ราว 55 วินาที)
ใช้จากโค้ด
    import sas_exp3 as E
    res = E.run()              # คำนวณทั้งหมด (เก็บผลไว้ เรียกซ้ำไม่คิดใหม่)
    E.figures()["beta"]        # ตัวเลขที่ปัดแล้ว พร้อมลงในบท → data-f="p3.beta.good.train.ols"
    E.charts()                 # {"sas-p3-…": html}

คีย์ของ figures()  (หน่วยอยู่ท้ายชื่อคีย์: _pct, _bps, _bars, _sigma, _baht · ไม่มีหน่วย = ตัวเลขเปล่า)
    about.<common|beta|eg|ar1|oos|rolling|remedy|money|wrong|mc>     ข้อความบอกการตั้งค่าของแต่ละการทดลอง
    settings.*                       จำนวนแท่ง · train · หน้าต่าง · จำนวนโลก · ค่าจริงของคู่ good · ต้นทุน
    beta.<good|drift|fake>.<train|full|second>.*   alpha · ols · ols_rev · tls · ret · r2_pct · r2_ret_pct
    beta.<kind>.*                    gap_train_full · gap_levels_returns · gap_two_ols · true_start · true_mid · true_end
    beta.good.no_alpha.*             beta_origin · sd_ratio · mean_shift_sigma
    beta.good.price_levels.*         beta_shares · alpha_baht · r2_pct
    beta.mc.*                        worlds · moe95_pct · flag_cut (|β̂ train − β̂ ทั้งช่วง| ที่คู่ good เกินแค่ 5%)
    beta.mc.<good|drift|fake>.*      flag_pct · gap_train_full_p50/p5/p95 · gap_levels_returns_p50/p5/p95 (ค่าสัมบูรณ์)
    eg.crit.*                        n_obs · n_vars · lags · n_sim · c1 · c5 · c10 · null_median
    eg.plain_adf.*                   c1 · c5 · c10 · false_pass_pct · false_pass_times
    eg.crit_n250.c5 · eg.crit_n500.c5 · eg.crit_n1500.c5 (+ n_sim)
    eg.<good|drift|fake>.*           stat_train · p_train_pct · p_train_text · verdict_train
                                     stat_full · p_full_pct · p_full_text · verdict_full
    eg.mc.*                          worlds (= 4,000) · moe95_pct
    eg.mc.<good|drift|fake>.*        pass_n250_pct · pass_n500_pct · pass_n750_pct · pass_n1500_pct
    ar1.truth.* · ar1.<good|drift|fake>.*   phi · kappa_per_bar · kappa_per_year · half_life_bars · mu_pct
                                     sigma_eq_pct · sd_sample_pct       (good มี true_eps.* = fit บน ε จริงช่วงเดียวกัน)
    oos.<good|drift|fake>.*          shift_sigma · sd_ratio · adf · p_pct · p_text · verdict · half_life_bars
                                     beyond2_pct · max_abs_z · last_z
    oos.mc.*                         worlds · moe95_pct
    oos.mc.<kind>.*                  shift_abs_p50/p5/p95_sigma · sd_ratio_p50/p5/p95 · adf_pass_pct
                                     beyond2_p50_pct (good มี beyond2_p5/p95_pct ด้วย) · oos.beyond2_normal_pct
    rolling.<good|drift|fake>.*      min · max · range · sd · first · last
    rolling.mc.worlds · rolling.mc.<kind>.*   range_p50 · range_p5 · range_p95
    remedy.<good|drift|fake>.static.*   adf · p_pct · p_text · verdict · half_life_bars · sd_pct
    remedy.<good|drift|fake>.wf.*    adf · p_pct · p_text · verdict · half_life_bars · sd_pct · z_sd
    remedy.wf_null.*                 worlds · moe95_pct · c5 · c10 · plain_false_pass_pct · half_life_p50_bars
    remedy.mc.*                      worlds · moe95_pct
    remedy.mc.<kind>.*               static_pass_pct · wf_pass_plain_pct · wf_pass_pct
                                     static_hl_p50_bars · wf_hl_p50/p5/p95_bars
    money.*                          beta · sigma_pct · log_y · log_x · price_y_baht · price_x_baht · y_baht · x_baht
                                     gross_baht · shares_y · shares_x · y_actual_baht · x_actual_baht · beta_actual
                                     shares_x_per_share_y (+ _first, _min, _max) · pnl_1sigma_baht
                                     pnl_1sigma_y_only_baht · pnl_1sigma_x_only_baht · pnl_1sigma_gross_pct
                                     hedge_x_up_pct · hedge_y_up_pct · hedge_y_leg_baht · hedge_x_leg_baht · hedge_net_baht
                                     cost_bps · cost_roundtrip_baht · entry2_gross_baht · entry2_net_baht · lot100.*
    wrong.*                          beta_used · leak_coef · leak_sd_per_bar_pct
    wrong.<right|beta1>.*            adf_train · p_train_pct · p_train_text · verdict_train · half_life_bars
                                     sd_train_pct · chg_sd_h1_pct … chg_sd_h250_pct · growth_h250_over_h20
    wrong.beta1.*                    sd_ratio · adf_oos · p_oos_text · verdict_oos · oos_shift_sigma · oos_sd_ratio
    wrong.mc.*                       worlds · moe95_pct · adf_pass_train_pct · adf_pass_oos_pct · hl_p50/p5_bars
                                     hl_right_p50_bars · sd_ratio_p50/p5/p95 · chg_sd_<right|beta1>_h<h>_pct
                                     growth_right_p50 · growth_beta1_p50
    mc.<n250|n750|n1500>.<ols|ols_rev|tls|ret>.*   bias · p5 · p50 · p95 · width (= p95 − p5) · abs_p50   (ของ β̂ − 1.4)
    mc.<n…>.*                        worlds · hl_p5/p50/p95/mean_bars · hl_infinite_worlds · hl_below_true_pct · phi_p50
                                     sigma_eq_p5/p50/p95_pct
"""
import functools
import math

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

import sas_core as C
import sas_svg as V

# ───────────────────────────── ค่าตั้งต้นของตอนนี้ ─────────────────────────────
N = 1500                        # แท่งต่อโลก (≈ 6 ปี)
TRAIN = N // 2                  # 750 แท่งแรก: ประมาณ α̂, β̂, μ̂, σ̂
ROLL = 250                      # หน้าต่างของ rolling β และของ walk-forward (≈ 1 ปี)
REFIT = 21                      # walk-forward ประมาณใหม่ทุก 21 แท่ง (≈ 1 เดือน)
LAGS = 1                        # จำนวน lag ของ ADF (ค่าตายตัวของทั้งชุด)
# จำนวนโลกเลือกจาก "ความแม่นที่ต้องพิมพ์" (ตรวจแล้วด้วยการเปลี่ยน seed): ตัวเลขยิ่งต้องละเอียด ยิ่งต้องใช้โลกมาก
WORLDS = 500                    # Monte Carlo ของ 3a/3d/3e/ยาแก้/3g ต่อแบบของคู่ (อัตราผ่านคลาดได้ราว ±4 จุด)
MC_WORLDS = 3000                # 3h: โลก good สำหรับการกระจายของ β̂ และ half-life (คำนวณถูก จึงใช้โลกมาก)
WF_NULL_WORLDS = 1000           # โลก fake ที่ใช้หาเกณฑ์ ADF ของสเปรด walk-forward
NULL_SIM = 100_000              # โลกของค่าวิกฤตที่ "พิมพ์ในบท"
NULL_SIM_AUX = 20_000           # โลกของค่าวิกฤตที่ใช้นับอัตราผ่านเท่านั้น (n = 250, 500, 1,500)
MC_SIZES = (250, TRAIN, N)      # จำนวนแท่งที่ใช้ประมาณใน 3h
EG_WORLDS = 4000                # โลกต่อแบบของคู่ สำหรับ "อัตราผ่าน" ของ Engle-Granger (คลาดได้ราว ±1.5 จุด)
EG_SIZES = (250, 500, TRAIN, N)           # จำนวนแท่งที่ลองทดสอบ
KINDS = ("good", "drift", "fake")
H_LIST = (1, 5, 20, 60, 120, 250)        # ระยะห่าง (แท่ง) ของ "การเปลี่ยนแปลงข้าม h แท่ง" ใน 3g

# ค่าจริงของคู่ good (ค่าตั้งต้นของ C.make_pair)
BETA, ALPHA, HL, SIGMA, SIGMA_X = 1.4, 0.3, 12.0, 0.03, 0.015
BETA_END = 2.2                  # คู่ drift: β เลื่อนจาก 1.4 ไป 2.2
SIGMA_M, SIGMA_IDIO = 0.012, 0.008       # คู่ fake: ปัจจัยตลาดร่วม กับส่วนเฉพาะตัวของแต่ละขา
PHI = C.phi_from_half_life(HL)

COST = 0.0005                   # c = 5 bps ต่อขา ต่อเที่ยว
Y_BAHT = 100_000                # ขนาดขา Y ของตัวอย่างเงินบาทใน 3f
BIG = 1e12                      # ตัวแทนของ "ไม่สิ้นสุด" เวลาหาเปอร์เซ็นไทล์ของ half-life


# ───────────────────────────── เครื่องมือเล็ก ๆ ─────────────────────────────
def rolling_beta(y, x, window):
    """β ของ OLS (มีค่าคงที่) จาก `window` แท่งล่าสุดที่จบที่แท่ง t — ไม่ใช้ข้อมูลหลังแท่ง t"""
    xw, yw = sliding_window_view(x, window), sliding_window_view(y, window)
    xc = xw - xw.mean(axis=1, keepdims=True)
    yc = yw - yw.mean(axis=1, keepdims=True)
    out = np.full(len(y), np.nan)
    out[window - 1:] = (xc * yc).sum(axis=1) / (xc * xc).sum(axis=1)
    return out


def four_betas(y, x):
    """β สี่วิธีจากข้อมูลช่วงเดียวกัน (+ จุดตัดแกนของแต่ละเส้น ไว้วาดกราฟ)"""
    fit = C.ols(y, x)                           # Y = α + β·X
    rev = C.ols(x, y)                           # X = c + γ·Y  →  Y = −c/γ + (1/γ)·X
    a_tls, b_tls = C.tls_beta(y, x)
    ret = C.ols(np.diff(y), np.diff(x))         # ΔY = a + β·ΔX  (β จากผลตอบแทน)
    gamma = rev["coef"][1]
    return {"alpha": fit["coef"][0], "ols": fit["coef"][1], "r2": fit["r2"],
            "alpha_rev": -rev["coef"][0] / gamma, "ols_rev": 1.0 / gamma,
            "alpha_tls": a_tls, "tls": b_tls,
            "ret": ret["coef"][1], "r2_ret": ret["r2"]}


def fit_spread(y, x):
    """Engle-Granger (ถดถอย + ADF ของส่วนเหลือ) แล้ว fit AR(1) ให้ ε̂ — ทุกอย่างที่แผนเทรดต้องใช้"""
    r = C.eg_test(y, x, lags=LAGS)
    eps = r["resid"]
    f = C.fit_ar1(eps)
    return {"alpha": r["alpha"], "beta": r["beta"][0], "eg": r["adf"],
            "n_obs": r["n_obs"], "n_vars": r["n_vars"], "lags": r["lags"],
            "mu": eps.mean(), "sd": eps.std(ddof=1),            # ไม้บรรทัดของ z ในตอนนี้
            "phi": f["phi"], "half_life": f["half_life"], "mu_ar1": f["mu"], "sigma_eq": f["sigma_eq"]}


def segment_check(s, mu, sd):
    """วัดอนุกรมช่วงหนึ่งด้วยไม้บรรทัด (μ, σ) ที่ได้มาจากช่วงอื่น"""
    z = (s - mu) / sd
    return {"shift": z.mean(), "sd_ratio": s.std(ddof=1) / sd, "sd": s.std(ddof=1),
            "adf": C.adf_stat(s, lags=LAGS), "half_life": C.fit_ar1(s)["half_life"],
            "beyond2": np.mean(np.abs(z) > 2.0), "max_abs_z": np.abs(z).max(), "last_z": z[-1]}


def change_sd(s, hs=H_LIST):
    """sd ของการเปลี่ยนแปลงข้าม h แท่ง: อนุกรมที่ดึงกลับจะ "ตัน" แถว √2·σ ส่วน random walk โตตาม √h ไม่หยุด"""
    return [float(np.std(s[h:] - s[:-h], ddof=1)) for h in hs]


def wrong_beta_check(y, x):
    """สเปรดที่ใช้ β = 1 (log ของอัตราส่วนราคา) วัดแบบเดียวกับสเปรดที่ถูก: train 750 แท่ง แล้วดู 750 แท่งหลัง"""
    s = y - x
    mu, sd = s[:TRAIN].mean(), s[:TRAIN].std(ddof=1)
    return {"spread": s - mu, "sd": sd, "adf_train": C.adf_stat(s[:TRAIN], lags=LAGS),
            "half_life": C.fit_ar1(s[:TRAIN])["half_life"],
            "oos": segment_check(s[TRAIN:], mu, sd), "chg_sd": change_sd(s)}


def analyse_pair(d):
    """ทุกอย่างของคู่หนึ่งคู่: β สี่วิธี · EG + AR(1) · ε ทั้งเส้นด้วยค่าของช่วง train · นอกตัวอย่าง · rolling β
    · สเปรด walk-forward · และสเปรด β = 1"""
    y, x = d["y"], d["x"]
    tr = fit_spread(y[:TRAIN], x[:TRAIN])
    eps = y - tr["alpha"] - tr["beta"] * x                  # α̂, β̂ ของช่วง train ใช้กับทั้ง 1,500 แท่ง
    wf = C.walk_forward_pair(y, x, train=ROLL, refit=REFIT)
    return {"betas": {"train": four_betas(y[:TRAIN], x[:TRAIN]), "full": four_betas(y, x),
                      "second": four_betas(y[TRAIN:], x[TRAIN:])},
            "train": tr, "full": fit_spread(y, x), "eps": eps,
            "oos": segment_check(eps[TRAIN:], tr["mu"], tr["sd"]),
            "rolling": rolling_beta(y, x, ROLL),
            "wf_eps": wf["eps"], "wf_z_sd": wf["stats"]["z_sd"],
            "wf_oos": segment_check(wf["eps"][TRAIN:], 0.0, tr["sd"]),
            "chg_sd": change_sd(eps), "wrong": wrong_beta_check(y, x)}


def dist(a):
    """ค่ากลาง ช่วง 5–95% และค่าเฉลี่ยของตัวเลขข้ามโลกจำลอง (inf ถูกนับเป็น "มากที่สุด" ไม่ทำให้เปอร์เซ็นไทล์เพี้ยน)"""
    a = np.minimum(np.asarray(a, float), BIG)
    p5, p50, p95 = np.percentile(a, [5, 50, 95])
    return {"p5": float(p5), "p50": float(p50), "p95": float(p95), "mean": float(a.mean()),
            "sd": float(a.std(ddof=1))}


# ───────────────────────────── ค่าวิกฤตที่จำลองเอง ─────────────────────────────
def simulate_nulls():
    """การแจกแจงของค่าสถิติในโลกที่ "ไม่มีอะไรเลย" (random walk ล้วน) — เรียงจากน้อยไปมาก"""
    return {
        "eg": {TRAIN: C.mc_null_eg(TRAIN, 2, n_sim=NULL_SIM, lags=LAGS, g=C.rng(300)),
               250: C.mc_null_eg(250, 2, n_sim=NULL_SIM_AUX, lags=LAGS, g=C.rng(302)),
               N: C.mc_null_eg(N, 2, n_sim=NULL_SIM_AUX, lags=LAGS, g=C.rng(303)),
               500: C.mc_null_eg(500, 2, n_sim=NULL_SIM_AUX, lags=LAGS, g=C.rng(304))},
        "adf": C.mc_null_adf(TRAIN, n_sim=NULL_SIM, lags=LAGS, g=C.rng(301)),     # อนุกรมเดียว 750 แท่ง
    }


def walk_forward_null(worlds):
    """ADF และ half-life ของสเปรด walk-forward (750 แท่งหลัง) ในโลก fake ที่ไม่มีสายจูง
    การ refit α, β ทุก 21 แท่งดึงสเปรดกลับมาใกล้ศูนย์เองอยู่แล้ว จึงต้องมีเกณฑ์ของตัวเอง ใช้ตาราง ADF ธรรมดาไม่ได้"""
    g = C.rng(320)
    adf, hl = np.empty(worlds), np.empty(worlds)
    for i in range(worlds):
        d = C.make_pair("fake", N, g)
        e = C.walk_forward_pair(d["y"], d["x"], train=ROLL, refit=REFIT)["eps"][TRAIN:]
        adf[i], hl[i] = C.adf_stat(e, lags=LAGS), C.fit_ar1(e)["half_life"]
    return {"adf": np.sort(adf), "half_life": hl}


def eg_stats_by_length(kind, offset, worlds=EG_WORLDS):
    """ค่า Engle-Granger ของ `worlds` โลก เมื่อมีข้อมูลแค่ n แท่งแรก → {n: อาร์เรย์}
    ใช้ตอบสองคำถาม: ต้องมีข้อมูลยาวแค่ไหน การทดสอบถึงจะเห็นสายจูงที่มีอยู่จริง · และคู่ปลอมหลุดผ่านบ่อยแค่ไหน"""
    g = C.rng(offset)
    out = {n: np.empty(worlds) for n in EG_SIZES}
    for i in range(worlds):
        d = C.make_pair(kind, N, g)
        for n in EG_SIZES:
            out[n][i] = C.eg_test(d["y"][:n], d["x"][:n], lags=LAGS)["adf"]
    return out


# ───────────────────────────── Monte Carlo ─────────────────────────────
def estimator_row(d):
    """3h: β̂ สี่วิธี และ AR(1) ของ ε̂ เมื่อประมาณจาก n แท่งแรกของโลกเดียวกัน (n = 250 / 750 / 1,500)"""
    y, x = d["y"], d["x"]
    row = {}
    for n in MC_SIZES:
        b, s = four_betas(y[:n], x[:n]), fit_spread(y[:n], x[:n])
        for k in ("ols", "ols_rev", "tls", "ret"):
            row[f"{k}_{n}"] = b[k]
        row.update({f"hl_{n}": s["half_life"], f"phi_{n}": s["phi"], f"sig_{n}": s["sigma_eq"]})
    return row


def world_row(d):
    """ตัวเลขของหนึ่งโลกจำลองสำหรับ 3a/3d/3e/ยาแก้/3g (dict ของสเกลาร์) — คิดแบบเดียวกับคู่ตัวอย่างทุกขั้น"""
    a = analyse_pair(d)
    row = {
        "ols_train": a["betas"]["train"]["ols"], "ols_full": a["betas"]["full"]["ols"],
        "ret_train": a["betas"]["train"]["ret"], "hl_train": a["train"]["half_life"],
        "shift_abs": abs(a["oos"]["shift"]), "sd_ratio": a["oos"]["sd_ratio"], "adf_oos": a["oos"]["adf"],
        "beyond2": a["oos"]["beyond2"], "hl_static": a["oos"]["half_life"],
        "rb_range": np.nanmax(a["rolling"]) - np.nanmin(a["rolling"]),
        "adf_wf": a["wf_oos"]["adf"], "hl_wf": a["wf_oos"]["half_life"],
        "bad_adf_train": a["wrong"]["adf_train"], "bad_adf_oos": a["wrong"]["oos"]["adf"],
        "bad_hl": a["wrong"]["half_life"], "bad_sd_ratio": a["wrong"]["sd"] / a["train"]["sd"],
    }
    for h, ok, bad in zip(H_LIST, a["chg_sd"], a["wrong"]["chg_sd"]):
        row[f"chg_ok_{h}"], row[f"chg_bad_{h}"] = ok, bad
    return row


def simulate_worlds(kind, offset, worlds=WORLDS, row=world_row):
    """`worlds` โลกของคู่แบบ `kind` → {ชื่อตัวเลข: อาร์เรย์ยาว worlds} (ทุกโลกถูกนับ ไม่มีการคัดทิ้ง)"""
    g = C.rng(offset)
    rows = [row(C.make_pair(kind, N, g)) for _ in range(worlds)]
    return {k: np.array([r[k] for r in rows], float) for k in rows[0]}


# ───────────────────────────── 3f เงินบาท ─────────────────────────────
def exp_money(d, fit):
    """แปล β̂ (หน่วยเงิน เพราะใช้ log price) เป็นบาทและจำนวนหุ้น ณ ราคาปิดของแท่งสุดท้าย"""
    y, x = d["y"], d["x"]
    # ใช้เลขที่ปัดแล้วตั้งแต่ต้น (β 3 ตำแหน่ง · σ 0.001% · ราคา 1 สตางค์) ผู้อ่านกดเครื่องคิดเลขตามได้ตรงทุกบรรทัด
    beta, sigma = round(fit["beta"], 3), round(fit["sd"], 5)
    py, px = round(math.exp(y[-1]), 2), round(math.exp(x[-1]), 2)
    x_baht = beta * Y_BAHT
    ratio = beta * np.exp(y - x)                         # หุ้น X ต่อหุ้น Y ที่ทำให้มูลค่าเป็น 1 : β ณ แต่ละแท่ง
    out = {"beta": beta, "sigma": sigma, "log_y": y[-1], "log_x": x[-1], "py": py, "px": px,
           "x_baht": x_baht, "gross": Y_BAHT + x_baht,
           "ratio_last": ratio[-1], "ratio_first": ratio[0], "ratio_min": ratio.min(), "ratio_max": ratio.max()}
    for name, lot in (("", 1), ("lot100_", 100)):         # ปัดเป็นหุ้นเต็ม / ปัดเป็นทีละ 100 หุ้น
        sy, sx = lot * round(Y_BAHT / py / lot), lot * round(x_baht / px / lot)
        out.update({f"{name}shares_y": sy, f"{name}shares_x": sx, f"{name}y_actual": sy * py,
                    f"{name}x_actual": sx * px, f"{name}beta_actual": sx * px / (sy * py)})
    ya, xa = out["y_actual"], out["x_actual"]
    # long สเปรด = ถือ Y +ya บาท และ X −xa บาท · ε สูงขึ้น 1σ ได้สองทาง: Y ขึ้นเอง หรือ X ลงเอง
    out["pnl_1s"] = Y_BAHT * sigma                               # แบบ log: มูลค่าขา Y × Δε
    out["pnl_1s_y_only"] = ya * (math.exp(sigma) - 1.0)           # X นิ่ง · Y ขึ้น σ (หน่วย log)
    out["pnl_1s_x_only"] = xa * (1.0 - math.exp(-sigma / beta))   # Y นิ่ง · X ลง σ/β
    # ตลาดพาทั้งคู่ขึ้นตามสัดส่วน β (ε แทบไม่ขยับ): X ขึ้น 1% · Y ขึ้น β% → สองขาหักล้างกัน
    up = 0.01
    out["hedge_y_up"] = beta * up
    out["hedge_y_leg"] = ya * out["hedge_y_up"]
    out["hedge_x_leg"] = -xa * up
    out["cost_roundtrip"] = 2.0 * COST * out["gross"]
    return out


# ───────────────────────────── รวมทุกการทดลอง ─────────────────────────────
@functools.lru_cache(maxsize=1)
def run():
    """คำนวณทุกการทดลองของตอนที่ 3 (ผลถูกเก็บไว้ เรียกซ้ำไม่คิดใหม่)"""
    pairs = {k: C.demo_pair(k) for k in KINDS}
    demo = {k: analyse_pair(pairs[k]) for k in KINDS}
    tr = demo["good"]["train"]
    assert (tr["n_obs"], tr["n_vars"], tr["lags"]) == (TRAIN, 2, LAGS)   # null ต้องจำลองด้วยค่าชุดเดียวกัน
    y, x = pairs["good"]["y"], pairs["good"]["x"]
    origin = C.ols(y[:TRAIN], x[:TRAIN], const=False)                    # ลืม α: บังคับเส้นผ่านจุดกำเนิด
    levels = C.ols(np.exp(y[:TRAIN]), np.exp(x[:TRAIN]))                 # ถดถอยบนราคาดิบ (บาท) แทน log
    return {
        "pairs": pairs, "demo": demo,
        "nulls": simulate_nulls(),
        "wf_null": walk_forward_null(WF_NULL_WORLDS),
        "mc": {k: simulate_worlds(k, 310 + i) for i, k in enumerate(KINDS)},
        "mc_est": simulate_worlds("good", 315, MC_WORLDS, estimator_row),
        "eg_pass": {k: eg_stats_by_length(k, 330 + i) for i, k in enumerate(KINDS)},
        "true_eps_fit": C.fit_ar1(pairs["good"]["eps"][:TRAIN]),
        "no_alpha": {"beta_origin": origin["coef"][0], "sd_ratio": origin["resid"].std(ddof=1) / tr["sd"],
                     "mean_shift_sigma": tr["alpha"] / tr["sd"]},       # ε = Y − β̂X เฉย ๆ จะมีค่าเฉลี่ย = α̂
        "price_levels": {"alpha": levels["coef"][0], "beta": levels["coef"][1], "r2": levels["r2"]},
        "money": exp_money(pairs["good"], tr),
    }


# ───────────────────────────── figures(): ตัวเลขที่ปัดแล้ว ─────────────────────────────
def _r(v, d=2):
    return C.rd(float(v), d)


def _num(v, d):
    """ปัด d ตำแหน่ง · d = 0 → int (ไฟล์ตัวเลขพิมพ์ int โดยไม่มี .0)"""
    return int(round(float(v))) if d == 0 else _r(v, d)


def _hl(v, d=1):
    """half-life สำหรับลงในบท: d ตำแหน่ง (d = 0 → จำนวนเต็ม) · ≥ 100 แท่ง → ปัดเป็นสิบ (ตัวเลขยาวขนาดนั้น
    มาจากสเปรดที่แทบไม่ดึงกลับ จึงสั่นมากตามโลกที่สุ่มได้) · ไม่ดึงกลับ (φ ≥ 1) → "∞" """
    v = float(v)
    if not math.isfinite(v) or v >= BIG / 10:
        return "∞"
    return int(10 * round(v / 10)) if v >= 100 else _num(v, d)


def _sig1(v):
    """เลขนัยสำคัญตัวเดียว อย่างน้อยทศนิยมหนึ่งตำแหน่ง (0.31 → 0.3 · 0.044 → 0.04 · 1.04 → 1.0)
    — สำหรับค่าที่กระจายกว้างจนหลักที่สองสั่นตาม seed"""
    v = float(v)
    return 0.0 if v == 0 else _r(v, max(1, -math.floor(math.log10(abs(v)))))


def _wide(v):
    """ค่าที่กระจายกว้างมากข้ามโลก (เช่นหาง 5–95% ของ |ค่าเฉลี่ยเลื่อน|): ≥ 2 → จำนวนเต็ม · < 2 → ทศนิยมเดียว"""
    return _num(v, 0 if abs(v) >= 2 else 1)


def _crit(null, q):
    return float(C.crit_values(null, qs=(q,))[q])


def _p(stat, null):
    """p-value จำลอง → (ตัวเลข %, ข้อความพร้อมหน่วย) ปัดตามความแม่นของจำนวนโลกที่จำลอง
    k = จำนวนโลก "ไม่มีอะไรเลย" ที่ได้ค่าติดลบเท่านี้หรือกว่า — k น้อย = p แทบไม่มีความแม่น
      k < 10      → บอกแค่ขอบบน "< 10/จำนวนโลก" (เช่น 100,000 โลก → "< 0.01%") · ตัวเลขเก็บขอบบนนั้น
      p < 10%     → เลขนัยสำคัญตัวเดียว (0.051% → 0.05%) · p ≥ 10% → จำนวนเต็ม"""
    n = len(null)
    p = float(C.p_value(stat, null))
    if math.isnan(p):                                            # ทดสอบไม่ได้ (ข้อมูลเสีย) — ไม่แต่งตัวเลข
        return "—", "—"
    if p * n < 10:
        bound = 1000.0 / n                                       # = 100 × 10/n  (หน่วย %)
        d = max(0, -math.floor(math.log10(bound)))
        return _num(bound, d), f"< {bound:.{d}f}%"
    pc = 100.0 * p
    d = 0 if pc >= 10 else max(0, -math.floor(math.log10(pc)))
    return _num(pc, d), f"{pc:.{d}f}%"


def _verdict(stat, crit5):
    return "ผ่าน" if stat < crit5 else "ไม่ผ่าน"


def _pass_pct(stats, crit5):
    """สัดส่วนโลกที่ผ่านเกณฑ์ เป็น % จำนวนเต็ม (ความคลาดของสัดส่วนจากหลักร้อย–พันโลกเกินทศนิยมอยู่แล้ว)"""
    return _num(100.0 * np.mean(np.asarray(stats) < crit5), 0)


def _moe(worlds):
    """ขอบความคลาด 95% ของ "อัตรา %" ที่นับจาก `worlds` โลก กรณีแย่สุด (อัตราจริง 50%) = 1.96·√(0.25/worlds)"""
    return _r(196.0 * math.sqrt(0.25 / worlds), 1)


def _spread3(prefix, dd, d=2, scale=1.0, suffix=""):
    """ค่ากลาง + ช่วง 5–95% ของ dist() → สามคีย์ชื่อ <prefix>_p50/p5/p95<suffix>"""
    return {f"{prefix}_{q}{suffix}": _num(scale * dd[q], d) for q in ("p50", "p5", "p95")}


def _fig_test(prefix, stat, null, suffix=""):
    pc, text = _p(stat, null)
    return {f"{prefix}{suffix}": _r(stat, 2), f"p{suffix}_pct": pc, f"p{suffix}_text": text,
            f"verdict{suffix}": _verdict(stat, _crit(null, 0.05))}


def _fig_beta(res):
    out = {}
    for k in KINDS:
        a, path = res["demo"][k], res["pairs"][k]["beta_path"]
        o = {}
        for seg in ("train", "full", "second"):
            b = a["betas"][seg]
            o[seg] = {"alpha": _r(b["alpha"], 3), "ols": _r(b["ols"], 3), "ols_rev": _r(b["ols_rev"], 3),
                      "tls": _r(b["tls"], 3), "ret": _r(b["ret"], 3),
                      "r2_pct": C.pct(b["r2"], 1), "r2_ret_pct": C.pct(b["r2_ret"], 1)}
        tr, full = a["betas"]["train"], a["betas"]["full"]
        o.update({"gap_train_full": _r(abs(tr["ols"] - full["ols"]), 3),
                  "gap_levels_returns": _r(abs(tr["ols"] - tr["ret"]), 3),
                  "gap_two_ols": _r(tr["ols_rev"] - tr["ols"], 3)})
        if k != "fake":                                   # β จริง ณ ต้นข้อมูล · แท่งที่ 750 · ปลายข้อมูล
            o.update({"true_start": _r(path[0], 2), "true_mid": _r(path[TRAIN - 1], 2), "true_end": _r(path[-1], 2)})
        out[k] = o
    na, pl = res["no_alpha"], res["price_levels"]
    out["good"]["no_alpha"] = {"beta_origin": _r(na["beta_origin"], 3), "sd_ratio": _r(na["sd_ratio"], 2),
                               "mean_shift_sigma": _r(na["mean_shift_sigma"], 1)}
    out["good"]["price_levels"] = {"beta_shares": _r(pl["beta"], 2), "alpha_baht": _r(pl["alpha"], 1),
                                   "r2_pct": C.pct(pl["r2"], 1)}
    out["fake"]["ret_theory"] = _r(SIGMA_M ** 2 / (SIGMA_M ** 2 + SIGMA_IDIO ** 2), 3)
    # "β ไม่นิ่ง" ใช้เป็นสัญญาณเตือนได้แค่ไหน: ตั้งเกณฑ์ที่คู่ good เกินแค่ 5% ของโลก แล้วนับว่าคู่อื่นเกินกี่ %
    gap = {k: np.abs(res["mc"][k]["ols_train"] - res["mc"][k]["ols_full"]) for k in KINDS}
    cut = float(np.percentile(gap["good"], 95))
    out["mc"] = {"worlds": WORLDS, "moe95_pct": _moe(WORLDS), "flag_cut": _r(cut, 2)}
    for k in KINDS:
        m = res["mc"][k]
        # good: ทศนิยมสองตำแหน่ง · drift/fake กระจายกว้างจนหลักที่สองสั่นตาม seed → เลขนัยสำคัญตัวเดียว
        rnd = (lambda v: _r(v, 2)) if k == "good" else _sig1
        o = {"flag_pct": _pass_pct(-gap[k], -cut)}            # สัดส่วนโลกที่ |β̂ train − β̂ ทั้งช่วง| > เกณฑ์
        for name, vals in (("gap_train_full", gap[k]), ("gap_levels_returns", np.abs(m["ols_train"] - m["ret_train"]))):
            dd = dist(vals)
            o.update({f"{name}_{q}": rnd(dd[q]) for q in ("p50", "p5", "p95")})
        out["mc"][k] = o
    return out


def _fig_eg(res):
    eg, adf = res["nulls"]["eg"], res["nulls"]["adf"]
    c5_adf = _crit(adf, 0.05)
    false_pass = float(C.p_value(c5_adf, eg[TRAIN]))       # โลกที่ไม่มีอะไรเลย แต่ค่า EG ต่ำกว่าเกณฑ์ของ ADF ธรรมดา
    out = {
        "crit": {"n_obs": TRAIN, "n_vars": 2, "lags": LAGS, "n_sim": NULL_SIM,
                 "c1": _r(_crit(eg[TRAIN], 0.01)), "c5": _r(_crit(eg[TRAIN], 0.05)),
                 "c10": _r(_crit(eg[TRAIN], 0.10)), "null_median": _r(np.median(eg[TRAIN]))},
        "plain_adf": {"n_obs": TRAIN, "n_sim": NULL_SIM, "c1": _r(_crit(adf, 0.01)), "c5": _r(c5_adf),
                      "c10": _r(_crit(adf, 0.10)), "false_pass_pct": _num(100.0 * false_pass, 0),
                      "false_pass_times": _r(false_pass / 0.05, 1)},
        # 20,000 โลก → ±0.03 จึงเก็บทศนิยมเดียว (ใช้นับอัตราผ่านเท่านั้น ไม่ใช่ตารางค่าวิกฤตที่จะพิมพ์)
        "crit_n250": {"n_sim": NULL_SIM_AUX, "c5": _r(_crit(eg[250], 0.05), 1)},
        "crit_n500": {"n_sim": NULL_SIM_AUX, "c5": _r(_crit(eg[500], 0.05), 1)},
        "crit_n1500": {"n_sim": NULL_SIM_AUX, "c5": _r(_crit(eg[N], 0.05), 1)},
        "mc": {"worlds": EG_WORLDS, "moe95_pct": _moe(EG_WORLDS)},
    }
    for k in KINDS:
        a = res["demo"][k]
        o = _fig_test("stat", a["train"]["eg"], eg[TRAIN], "_train")
        o.update(_fig_test("stat", a["full"]["eg"], eg[N], "_full"))
        out[k] = o
        out["mc"][k] = {f"pass_n{n}_pct": _pass_pct(res["eg_pass"][k][n], _crit(eg[n], 0.05)) for n in EG_SIZES}
    return out


def _fig_ar1_one(phi, hl, mu, sigma_eq, sd=None):
    o = {"phi": _r(phi, 4), "kappa_per_bar": _r(-math.log(phi), 4) if 0 < phi < 1 else "—",
         "kappa_per_year": _r(-math.log(phi) * C.DAYS_PER_YEAR, 1) if 0 < phi < 1 else "—",
         "half_life_bars": _hl(hl), "mu_pct": C.pct(mu, 2),
         "sigma_eq_pct": C.pct(sigma_eq, 2) if math.isfinite(sigma_eq) else "∞"}
    if sd is not None:
        o["sd_sample_pct"] = C.pct(sd, 2)
    return o


def _fig_ar1(res):
    out = {"truth": _fig_ar1_one(PHI, HL, 0.0, SIGMA)}
    out["truth"]["half_life_bars"] = int(HL)                     # ค่าที่ตั้งเอง ไม่ใช่ค่าประมาณ
    for k in KINDS:
        t = res["demo"][k]["train"]
        out[k] = _fig_ar1_one(t["phi"], t["half_life"], t["mu_ar1"], t["sigma_eq"], t["sd"])
    f = res["true_eps_fit"]
    out["good"]["true_eps"] = _fig_ar1_one(f["phi"], f["half_life"], f["mu"], f["sigma_eq"],
                                           res["pairs"]["good"]["eps"][:TRAIN].std(ddof=1))
    return out


def _fig_segment(s, null):
    o = _fig_test("adf", s["adf"], null)
    o.update({"shift_sigma": _r(s["shift"], 2), "sd_ratio": _r(s["sd_ratio"], 2),
              "half_life_bars": _hl(s["half_life"]), "beyond2_pct": C.pct(s["beyond2"], 1),
              "max_abs_z": _r(s["max_abs_z"], 1), "last_z": _r(s["last_z"], 1)})
    return o


def _fig_oos(res):
    adf = res["nulls"]["adf"]
    c5 = _crit(adf, 0.05)
    out = {k: _fig_segment(res["demo"][k]["oos"], adf) for k in KINDS}
    out["beyond2_normal_pct"] = C.pct(math.erfc(2.0 / math.sqrt(2.0)), 1)    # ถ้า z เป็น normal มาตรฐาน
    out["mc"] = {"worlds": WORLDS, "moe95_pct": _moe(WORLDS)}
    for k in KINDS:
        m = res["mc"][k]
        o = {"adf_pass_pct": _pass_pct(m["adf_oos"], c5)}
        o.update({f"shift_abs_{q}_sigma": _wide(v) for q, v in dist(m["shift_abs"]).items() if q in ("p5", "p50", "p95")})
        o.update(_spread3("sd_ratio", dist(m["sd_ratio"]), 1))
        b2 = dist(m["beyond2"])
        o["beyond2_p50_pct"] = _num(100.0 * b2["p50"], 0)
        if k == "good":                     # หางของ drift/fake กว้างจนตัวเลขสั่นหลายจุดตาม seed — ใช้ค่ากลางพอ
            o.update({"beyond2_p5_pct": _num(100.0 * b2["p5"], 0), "beyond2_p95_pct": _num(100.0 * b2["p95"], 0)})
        out["mc"][k] = o
    return out


def _fig_rolling(res):
    out = {"mc": {"worlds": WORLDS}}
    for k in KINDS:
        rb = res["demo"][k]["rolling"][ROLL - 1:]
        out[k] = {"min": _r(rb.min()), "max": _r(rb.max()), "range": _r(rb.max() - rb.min()),
                  "sd": _r(rb.std(ddof=1), 3), "first": _r(rb[0]), "last": _r(rb[-1])}
        out["mc"][k] = _spread3("range", dist(res["mc"][k]["rb_range"]), 1)
    return out


def _fig_remedy(res):
    adf, wfn = res["nulls"]["adf"], res["wf_null"]
    c5_plain, c5_wf = _crit(adf, 0.05), _crit(wfn["adf"], 0.05)
    # half_life_p50_bars ของโลก fake = half-life ที่ "สูตรคายออกมา" ทั้งที่ไม่มีสายจูงเลย — ไว้เทียบกับ half-life
    # ของสเปรดที่สอบตก (ตัวเลขแบบนั้นไม่มีความหมาย)
    out = {"wf_null": {"worlds": WF_NULL_WORLDS, "moe95_pct": _moe(WF_NULL_WORLDS),
                       "c5": _r(c5_wf, 1), "c10": _r(_crit(wfn["adf"], 0.10), 1),
                       "plain_false_pass_pct": _pass_pct(wfn["adf"], c5_plain),
                       "half_life_p50_bars": _hl(dist(wfn["half_life"])["p50"], 0)},
           "mc": {"worlds": WORLDS, "moe95_pct": _moe(WORLDS)}}
    for k in KINDS:
        a = res["demo"][k]
        st = _fig_test("adf", a["oos"]["adf"], adf)
        st.update({"half_life_bars": _hl(a["oos"]["half_life"]), "sd_pct": C.pct(a["oos"]["sd"], 2)})
        wf = _fig_test("adf", a["wf_oos"]["adf"], wfn["adf"])       # เทียบกับเกณฑ์ของสเปรด walk-forward เอง
        wf.update({"half_life_bars": _hl(a["wf_oos"]["half_life"]), "sd_pct": C.pct(a["wf_oos"]["sd"], 2),
                   "z_sd": _r(a["wf_z_sd"], 2)})
        out[k] = {"static": st, "wf": wf}
        m = res["mc"][k]
        o = {"static_pass_pct": _pass_pct(m["adf_oos"], c5_plain),
             "wf_pass_plain_pct": _pass_pct(m["adf_wf"], c5_plain), "wf_pass_pct": _pass_pct(m["adf_wf"], c5_wf),
             "static_hl_p50_bars": _hl(dist(m["hl_static"])["p50"], 0)}
        o.update({f"wf_hl_{q}_bars": _hl(v, 0) for q, v in dist(m["hl_wf"]).items() if q in ("p5", "p50", "p95")})
        out["mc"][k] = o
    return out


def _fig_money(res):
    m = res["money"]
    baht = lambda v: int(round(v))
    return {
        "beta": _r(m["beta"], 3), "sigma_pct": C.pct(m["sigma"], 3),
        "log_y": _r(m["log_y"], 4), "log_x": _r(m["log_x"], 4),
        "price_y_baht": _r(m["py"], 2), "price_x_baht": _r(m["px"], 2),
        "y_baht": Y_BAHT, "x_baht": baht(m["x_baht"]), "gross_baht": baht(m["gross"]),
        "shares_y": int(m["shares_y"]), "shares_x": int(m["shares_x"]),
        "y_actual_baht": baht(m["y_actual"]), "x_actual_baht": baht(m["x_actual"]),
        "beta_actual": _r(m["beta_actual"], 4),
        "shares_x_per_share_y": _r(m["ratio_last"], 2), "shares_x_per_share_y_first": _r(m["ratio_first"], 2),
        "shares_x_per_share_y_min": _r(m["ratio_min"], 2), "shares_x_per_share_y_max": _r(m["ratio_max"], 2),
        "pnl_1sigma_baht": baht(m["pnl_1s"]), "pnl_1sigma_y_only_baht": baht(m["pnl_1s_y_only"]),
        "pnl_1sigma_x_only_baht": baht(m["pnl_1s_x_only"]),
        "pnl_1sigma_gross_pct": C.pct(m["sigma"] / (1.0 + m["beta"]), 2),
        "hedge_x_up_pct": 1.0, "hedge_y_up_pct": C.pct(m["hedge_y_up"], 3),
        "hedge_y_leg_baht": baht(m["hedge_y_leg"]), "hedge_x_leg_baht": baht(m["hedge_x_leg"]),
        "hedge_net_baht": baht(m["hedge_y_leg"]) + baht(m["hedge_x_leg"]),      # บวกจากเลขที่ปัดแล้ว ให้ตรงกับที่พิมพ์
        "cost_bps": C.bps(COST, 1), "cost_roundtrip_baht": baht(m["cost_roundtrip"]),
        "entry2_gross_baht": 2 * baht(m["pnl_1s"]),
        "entry2_net_baht": 2 * baht(m["pnl_1s"]) - baht(m["cost_roundtrip"]),
        "lot100": {"shares_y": int(m["lot100_shares_y"]), "shares_x": int(m["lot100_shares_x"]),
                   "y_actual_baht": baht(m["lot100_y_actual"]), "x_actual_baht": baht(m["lot100_x_actual"]),
                   "beta_actual": _r(m["lot100_beta_actual"], 4)},
    }


def _fig_chg(chg):
    o = {f"chg_sd_h{h}_pct": C.pct(v, 2) for h, v in zip(H_LIST, chg)}
    o["growth_h250_over_h20"] = _r(chg[H_LIST.index(250)] / chg[H_LIST.index(20)], 2)
    return o


def _fig_wrong(res):
    a, adf, eg = res["demo"]["good"], res["nulls"]["adf"], res["nulls"]["eg"][TRAIN]
    w, tr, m = a["wrong"], a["train"], res["mc"]["good"]
    c5 = _crit(adf, 0.05)
    right = _fig_test("adf", tr["eg"], eg, "_train")              # β ถูกประมาณ → ต้องเทียบกับเกณฑ์ของ EG
    right.update({"half_life_bars": _hl(tr["half_life"]), "sd_train_pct": C.pct(tr["sd"], 2)})
    right.update(_fig_chg(a["chg_sd"]))
    bad = _fig_test("adf", w["adf_train"], adf, "_train")         # β = 1 ถูกกำหนดเอง → ใช้เกณฑ์ ADF ธรรมดาได้
    oos = _fig_test("adf", w["oos"]["adf"], adf, "_oos")
    bad.update({"adf_oos": oos["adf_oos"], "p_oos_text": oos["p_oos_text"], "verdict_oos": oos["verdict_oos"],
                "half_life_bars": _hl(w["half_life"]), "sd_train_pct": C.pct(w["sd"], 2),
                "sd_ratio": _r(w["sd"] / tr["sd"], 2), "oos_shift_sigma": _r(w["oos"]["shift"], 2),
                "oos_sd_ratio": _r(w["oos"]["sd_ratio"], 2)})
    bad.update(_fig_chg(w["chg_sd"]))
    mc = {"worlds": WORLDS, "moe95_pct": _moe(WORLDS), "adf_pass_train_pct": _pass_pct(m["bad_adf_train"], c5),
          "adf_pass_oos_pct": _pass_pct(m["bad_adf_oos"], c5),
          "hl_right_p50_bars": _hl(dist(m["hl_train"])["p50"], 0)}
    # สเปรด β = 1 มี random walk ซ่อนอยู่: half-life ของมันเป็นแค่ตัวเลขที่สูตรคาย หางบนจึงไร้ความหมาย เก็บแค่ p5/p50
    mc.update({f"hl_{q}_bars": _hl(v, 0) for q, v in dist(m["bad_hl"]).items() if q in ("p5", "p50")})
    mc.update(_spread3("sd_ratio", dist(m["bad_sd_ratio"]), 1))
    for h in H_LIST:
        mc[f"chg_sd_right_h{h}_pct"] = C.pct(np.median(m[f"chg_ok_{h}"]), 1)
        mc[f"chg_sd_beta1_h{h}_pct"] = C.pct(np.median(m[f"chg_bad_{h}"]), 1)
    mc["growth_right_p50"] = _r(np.median(m["chg_ok_250"] / m["chg_ok_20"]), 1)
    mc["growth_beta1_p50"] = _r(np.median(m["chg_bad_250"] / m["chg_bad_20"]), 1)
    return {"beta_used": 1.0, "leak_coef": _r(tr["beta"] - 1.0, 3),
            "leak_sd_per_bar_pct": C.pct((BETA - 1.0) * SIGMA_X, 2),
            "right": right, "beta1": bad, "mc": mc}


def _fig_mc(res):
    m = res["mc_est"]
    out = {}
    for n in MC_SIZES:
        o = {"worlds": MC_WORLDS, "n_bars": n}
        for k in ("ols", "ols_rev", "tls", "ret"):
            err = m[f"{k}_{n}"] - BETA
            dd = dist(err)
            o[k] = {"bias": _r(dd["mean"], 2), "p5": _r(dd["p5"], 2), "p50": _r(dd["p50"], 2),
                    "p95": _r(dd["p95"], 2), "width": _r(dd["p95"] - dd["p5"], 2),
                    "abs_p50": _r(np.median(np.abs(err)), 2)}
        hl = dist(m[f"hl_{n}"])
        # ค่ากลาง 1 ตำแหน่ง (ที่ 250 แท่งยังสั่นราว ±0.2 แท่งตาม seed แม้ 3,000 โลก) · หาง 5–95% เป็นจำนวนเต็ม
        o.update({"hl_p5_bars": _hl(hl["p5"], 0), "hl_p50_bars": _hl(hl["p50"]), "hl_p95_bars": _hl(hl["p95"], 0)})
        # ค่าเฉลี่ยมีความหมายเฉพาะเมื่อทุกโลกได้ half-life จำกัด (โลกเดียวที่ φ̂ ≥ 1 ทำให้ค่าเฉลี่ยเป็น ∞)
        o["hl_mean_bars"] = _hl(np.mean(m[f"hl_{n}"])) if np.all(np.isfinite(m[f"hl_{n}"])) else "∞"
        o["hl_infinite_worlds"] = int(np.sum(~np.isfinite(m[f"hl_{n}"])))
        o["hl_below_true_pct"] = _num(100.0 * np.mean(m[f"hl_{n}"] < HL), 0)
        o["phi_p50"] = _r(np.median(m[f"phi_{n}"]), 3)
        o.update(_spread3("sigma_eq", dist(m[f"sig_{n}"]), 1, scale=100.0, suffix="_pct"))
        out[f"n{n}"] = o
    return out


def _about():
    return {
        "common": f"ข้อมูลจำลองทั้งหมด · คู่ตัวอย่าง {N:,} แท่งรายวัน · ประมาณจาก {TRAIN} แท่งแรก (train) แล้วตรวจกับ "
                  f"{N - TRAIN} แท่งหลัง · Monte Carlo {WORLDS} โลกต่อแบบของคู่ (good / drift / fake) · 3h ใช้ {MC_WORLDS:,} โลก good · "
                  f"อัตราผ่านของ Engle-Granger ใช้ {EG_WORLDS:,} โลกต่อแบบ · ADF ใช้ lags = {LAGS} · "
                  f"ตัวเลข Monte Carlo ปัดหยาบตามความแม่น (อัตรา % เป็นจำนวนเต็ม คลาดได้ไม่เกิน ±moe95_pct จุด)",
        "beta": "β สี่วิธีจากข้อมูลช่วงเดียวกัน: OLS ของ Y บน X · OLS ของ X บน Y แล้วกลับเศษส่วน · TLS · OLS ของ ΔY บน ΔX "
                f"(β จากผลตอบแทน) · ค่าจริงของคู่ good: α = {ALPHA}, β = {BETA} · คู่ drift: β เลื่อนจาก {BETA} ไป {BETA_END} · "
                f"beta.mc.flag_cut = |β̂ train − β̂ ทั้งช่วง| ที่คู่ good เกินแค่ 5% ของโลก · flag_pct = % ของโลกที่เกินเกณฑ์นั้น",
        "eg": f"Engle-Granger บน {TRAIN} แท่งแรก · ค่าวิกฤตจำลองจาก random walk อิสระ 2 เส้น {NULL_SIM:,} โลก "
              f"(n = {TRAIN}, lags = {LAGS}; คลาดได้ราว ±0.01) · เกณฑ์ ADF ธรรมดา = อนุกรมเดียว มีค่าคงที่ {NULL_SIM:,} โลก · "
              f"เกณฑ์ที่ n = 250, 500 และ {N:,} ใช้ {NULL_SIM_AUX:,} โลก (ใช้นับอัตราผ่าน ไม่ใช่ตารางที่จะพิมพ์) · "
              f"อัตราผ่าน (eg.mc) นับจาก {EG_WORLDS:,} โลกต่อแบบของคู่ โดยใช้ n แท่งแรกของโลกเดียวกัน · "
              f"p-value: เมื่อมีโลกที่ติดลบกว่าไม่ถึง 10 โลก บอกได้แค่ \"น้อยกว่า\"",
        "ar1": f"fit AR(1) กับ ε̂ ของ {TRAIN} แท่งแรก · ค่าจริงของคู่ good: φ = {PHI:.4f} (half-life {HL:.0f} แท่ง), "
               f"μ = 0, σ = {100 * SIGMA:.0f}% · μ ของเราคือ θ ของหนังสือเล่มเดิม",
        "oos": f"α̂, β̂ และไม้บรรทัด (ค่าเฉลี่ย, sd ของ ε̂) มาจาก {TRAIN} แท่งแรก แล้ววัด {N - TRAIN} แท่งหลัง · "
               f"ADF ของช่วงหลังเทียบเกณฑ์ ADF ธรรมดา (β ไม่ได้ประมาณจากช่วงนี้)",
        "rolling": f"β ของ OLS จาก {ROLL} แท่งล่าสุดที่จบ ณ แท่งนั้น (ไม่มองอนาคต) · range = ค่าสูงสุด − ค่าต่ำสุดตลอดเส้น",
        "remedy": f"สเปรด β คงที่ (ค่าจาก {TRAIN} แท่งแรก) เทียบสเปรด walk-forward (α, β ประมาณใหม่จาก {ROLL} แท่งล่าสุด "
                  f"ทุก {REFIT} แท่ง) วัดบน {N - TRAIN} แท่งหลังเหมือนกัน · เกณฑ์ ADF ของสเปรด walk-forward จำลองจากโลก fake "
                  f"{WF_NULL_WORLDS:,} โลก (คลาดได้ราว ±0.05) · half-life ของสเปรดที่ไม่ผ่าน ADF เป็นแค่ตัวเลขที่สูตรคายออกมา "
                  f"(เทียบโลก fake ที่ไม่มีสายจูงเลย: mc.fake.static_hl_p50_bars ของสเปรด β คงที่ · "
                  f"wf_null.half_life_p50_bars ของสเปรด walk-forward)",
        "money": f"คู่ good · β̂ ของช่วง train · ราคาปิดแท่งสุดท้าย · ขา Y {Y_BAHT:,} บาท · σ = sd ของ ε̂ ช่วง train · "
                 f"ต้นทุน {C.bps(COST, 0)} bps ต่อขาต่อเที่ยว · lot100 = ปัดเป็นทีละ 100 หุ้น",
        "wrong": f"คู่ good (β จริง {BETA}) แต่ใช้ β = 1 คือ log ของอัตราส่วนราคา · train {TRAIN} แท่ง · "
                 f"chg_sd_h = sd ของการเปลี่ยนแปลงข้าม h แท่ง (ทั้ง {N:,} แท่ง) · Monte Carlo {WORLDS} โลก good",
        "mc": f"{MC_WORLDS:,} โลก good · ประมาณจาก 250 / {TRAIN} / {N:,} แท่งแรกของโลกเดียวกัน · β̂ − {BETA} ของสี่วิธี "
              f"และ half-life ของ ε̂ (ค่าจริง {HL:.0f} แท่ง) · ช่วงที่รายงาน = เปอร์เซ็นไทล์ 5–95 · width = p95 − p5 · "
              f"β̂ คลาดได้ราว ±0.01 · ค่ากลาง half-life ที่ 250 แท่งคลาดได้ราว ±0.2 แท่ง",
    }


def figures(res=None):
    """ตัวเลขทั้งหมดของตอนที่ 3 ปัดแล้วพร้อมลงในบท (dict ซ้อน คีย์ ASCII)"""
    res = res or run()
    return {
        "about": _about(),
        "settings": {"n_bars": N, "train_bars": TRAIN, "test_bars": N - TRAIN, "roll_window_bars": ROLL,
                     "refit_bars": REFIT, "lags": LAGS, "worlds": WORLDS, "mc_worlds": MC_WORLDS,
                     "eg_worlds": EG_WORLDS, "wf_null_worlds": WF_NULL_WORLDS,
                     "null_sim": NULL_SIM, "null_sim_aux": NULL_SIM_AUX,
                     "alpha_true": ALPHA, "beta_true": BETA, "beta_drift_end": BETA_END,
                     "hl_true_bars": int(HL), "phi_true": _r(PHI, 4), "sigma_true_pct": C.pct(SIGMA, 1),
                     "sigma_x_pct": C.pct(SIGMA_X, 1), "cost_bps": C.bps(COST, 1), "y_baht": Y_BAHT},
        "beta": _fig_beta(res),
        "eg": _fig_eg(res),
        "ar1": _fig_ar1(res),
        "oos": _fig_oos(res),
        "rolling": _fig_rolling(res),
        "remedy": _fig_remedy(res),
        "money": _fig_money(res),
        "wrong": _fig_wrong(res),
        "mc": _fig_mc(res),
    }


# ───────────────────────────── charts() ─────────────────────────────
def _n(v, d=2, sign=False):
    return V.num(float(v), d, sign=sign)


def _chart_scatter(res):
    d, b = res["pairs"]["good"], res["demo"]["good"]["betas"]["train"]
    cap = (f"ข้อมูลจำลอง (คู่ good) · จุด = log ราคาของ Y กับ X ใน {TRAIN} แท่งแรก (หยิบมา 300 จุด) · "
           f"เส้น = OLS ของ Y บน X ได้ α̂ = {_n(b['alpha'], 3)}, β̂ = {_n(b['ols'], 3)} "
           f"(ค่าจริง α = {ALPHA}, β = {BETA}) · สิ่งที่ต้องดู: ระยะในแนวดิ่งจากจุดถึงเส้นคือ ε ของวันนั้น — "
           f"R² {_n(100 * b['r2'], 1)}% บอกว่าจุดเกาะเส้นแน่น แต่ยังไม่ได้บอกว่า ε กลับมาหาเส้นหรือเปล่า")
    return V.scatter_chart(
        "sas-p3-scatter", d["x"][:TRAIN], d["y"][:TRAIN],
        "จุดกระจายของ log ราคา Y เทียบ X ของคู่ good พร้อมเส้นถดถอย OLS", cap,
        xlabel="X (log ราคา)", ylabel="Y (log ราคา)", max_points=300,
        lines=[{"a": b["alpha"], "b": b["ols"], "name": f"เส้น OLS: Y = {_n(b['alpha'], 2)} + {_n(b['ols'], 2)}·X",
                "color": V.RED}])


def _chart_scatter_fake(res):
    d, a = res["pairs"]["fake"], res["demo"]["fake"]
    b, g = a["betas"]["train"], res["demo"]["good"]["betas"]["train"]
    cap = (f"ข้อมูลจำลอง (คู่ fake — ไม่มีสายจูง) · {TRAIN} แท่งแรก · ถดถอย Y บน X ได้ β̂ = {_n(b['ols'])} แต่ถดถอย X บน Y "
           f"แล้วกลับเศษส่วนได้ {_n(b['ols_rev'])} — เส้นเดียวกันควรได้เลขเดียวกัน แต่ OLS ให้สองคำตอบ "
           f"(TLS อยู่ตรงกลาง: {_n(b['tls'])}) · ยิ่งจุดกระจายหลวม สองเส้นยิ่งถ่างออก: คู่ good ที่ R² "
           f"{_n(100 * g['r2'], 1)}% ต่างกันแค่ {_n(g['ols'], 3)} กับ {_n(g['ols_rev'], 3)} · "
           f"และ R² {_n(100 * b['r2'], 1)}% ของคู่นี้ไม่ได้แปลว่ามีสายจูง — Engle-Granger ได้ "
           f"{_n(a['train']['eg'])} ไม่ผ่านเกณฑ์")
    return V.scatter_chart(
        "sas-p3-scatter-fake", d["x"][:TRAIN], d["y"][:TRAIN],
        "จุดกระจายของคู่ fake พร้อมเส้นถดถอยสามแบบที่ให้ความชันต่างกัน", cap,
        xlabel="X (log ราคา)", ylabel="Y (log ราคา)", max_points=300,
        lines=[{"a": b["alpha"], "b": b["ols"], "name": f"OLS: Y บน X (β̂ = {_n(b['ols'])})", "color": V.RED},
               {"a": b["alpha_rev"], "b": b["ols_rev"], "name": f"OLS: X บน Y กลับเศษส่วน ({_n(b['ols_rev'])})",
                "color": V.AMBER},
               {"a": b["alpha_tls"], "b": b["tls"], "name": f"TLS ({_n(b['tls'])})", "color": V.PURPLE,
                "dash": "6 4"}])


def _density(a, lo, hi, bins):
    h, edges = np.histogram(a, bins=bins, range=(lo, hi), density=True)
    return 0.5 * (edges[:-1] + edges[1:]), h * np.mean((a >= lo) & (a <= hi))


def _chart_eg_null(res):
    eg, adf = res["nulls"]["eg"][TRAIN], res["nulls"]["adf"]
    c_eg, c_adf = _crit(eg, 0.05), _crit(adf, 0.05)
    false_pass = figures(res)["eg"]["plain_adf"]["false_pass_pct"]
    stat = res["demo"]["good"]["train"]["eg"]
    fake = res["demo"]["fake"]["train"]["eg"]
    lo, hi, bins = -6.0, 1.5, 75
    xs, d_adf = _density(adf, lo, hi, bins)
    _, d_eg = _density(eg, lo, hi, bins)
    cap = (f"ข้อมูลจำลอง · การแจกแจงของค่าทดสอบในโลกที่ \"ไม่มีอะไรเลย\" {NULL_SIM:,} โลก (n = {TRAIN}) · "
           f"เส้นของ Engle-Granger อยู่ซ้ายกว่าเส้นของ ADF ธรรมดา เพราะ OLS เลือก β ที่ทำให้ ε̂ ดูนิ่งที่สุดไว้ก่อนแล้ว "
           f"เกณฑ์ 5% จึงต้องเข้มขึ้นจาก {_n(c_adf)} เป็น {_n(c_eg)} · ถ้าใช้เกณฑ์ของ ADF ธรรมดากับ ε̂ "
           f"คู่ที่ไม่มีสายจูงจะผ่านถึง {false_pass}% แทนที่จะเป็น 5% (แถบชมพู = โซนที่ ADF ธรรมดาบอก \"ผ่าน\" "
           f"แต่ Engle-Granger บอก \"ไม่ผ่าน\") · คู่ good ได้ {_n(stat)} (ผ่านขาด) คู่ fake ได้ {_n(fake)} (ไม่ผ่าน)")
    return V.line_chart(
        "sas-p3-eg-null", xs,
        [{"name": "ADF ธรรมดา (อนุกรมเดียว)", "y": d_adf, "color": V.MUTED},
         {"name": "Engle-Granger (ε̂ จากการถดถอย 2 ขา)", "y": d_eg, "color": V.BLUE, "hero": True}],
        "การแจกแจงของค่าทดสอบ ADF ธรรมดาเทียบกับ Engle-Granger ในโลกที่ไม่มีสายจูง พร้อมเกณฑ์ 5% ของแต่ละแบบ", cap,
        xlabel="ค่าทดสอบ (ยิ่งติดลบ = ยิ่งดูเหมือนมีแรงดึงกลับ)", ylabel="ความหนาแน่น", markers=False,
        xlim=(lo, hi), zero=True,
        vlines=[(c_eg, "", V.BLUE), (c_adf, "")],
        xbands=[(c_eg, c_adf, "", V.RED)],
        # สองเกณฑ์ห่างกันแค่ราว 0.5 หน่วย ป้ายเหนือกรอบจะทับกัน จึงวางป้ายซ้อนกันในที่ว่างทางซ้ายแทน
        callouts=[(c_eg, 0.5, f"เกณฑ์ 5% ของ Engle-Granger {_n(c_eg)}", -40, 0, V.BLUE),
                  (c_adf, 0.38, f"เกณฑ์ 5% ของ ADF ธรรมดา {_n(c_adf)}", -86, 0, V.MUTED),
                  (stat, 0.0, f"คู่ good {_n(stat)}", 30, -46, V.GREEN),
                  (fake, float(np.interp(fake, xs, d_eg)), f"คู่ fake {_n(fake)}", 46, -18, V.RED)])


def _chart_eg_power(res):
    f = figures(res)["eg"]["mc"]
    colors = {"good": V.BLUE, "drift": V.AMBER, "fake": V.RED}
    names = {"good": "good (สายจูงจริง)", "drift": "drift (สายจูงจริง แต่ β เลื่อน)", "fake": "fake (ไม่มีสายจูง)"}
    cap = (f"ข้อมูลจำลอง · {EG_WORLDS:,} โลกต่อแบบ (แต่ละตัวเลขคลาดได้ไม่เกิน ±{_n(f['moe95_pct'], 1)} จุด) · "
           f"สัดส่วนของโลกที่ผ่าน Engle-Granger ที่ระดับ 5% เมื่อมีข้อมูลยาวต่างกัน · "
           f"คู่ที่มีสายจูงจริง (half-life {HL:.0f} แท่ง) มีข้อมูลหนึ่งปีผ่านแค่ {f['good']['pass_n250_pct']}% — "
           f"\"ไม่ผ่าน\" ตอนข้อมูลสั้นจึงไม่ได้แปลว่าไม่มีสายจูง · สองปี {f['good']['pass_n500_pct']}% · "
           f"สามปีเกือบทุกโลก ({f['good']['pass_n750_pct']}%) · คู่ fake ผ่านราว 5% ทุกความยาวตามที่ตั้งเกณฑ์ไว้ · "
           f"คู่ drift ก็ผ่านเป็นส่วนใหญ่ ({f['drift']['pass_n750_pct']}% ที่ {TRAIN} แท่ง): "
           f"การทดสอบนี้ไม่ได้ตรวจว่า β นิ่ง")
    return V.grouped_bars(
        "sas-p3-eg-power", [f"{n:,} แท่ง\n(≈ {n / C.DAYS_PER_YEAR:.0f} ปี)" for n in EG_SIZES],
        [{"name": names[k], "values": [f[k][f"pass_n{n}_pct"] for n in EG_SIZES], "color": colors[k]} for k in KINDS],
        "อัตราผ่านการทดสอบ Engle-Granger ของคู่ good drift และ fake เมื่อมีข้อมูล 250 ถึง 1,500 แท่ง", cap,
        ylabel="ผ่านเกณฑ์ 5% (% ของโลก)", xlabel="ความยาวข้อมูลที่ใช้ทดสอบ", fmt=lambda v: _n(v, 0), ylim=(0, 112),
        hlines=[(5.0, "5% ที่ตั้งใจให้คู่ปลอมผ่าน")])


def _chart_spread_good(res):
    a, fo = res["demo"]["good"], figures(res)["oos"]
    tr, o = a["train"], fo["good"]
    s = 100.0 * tr["sd"]
    cap = (f"ข้อมูลจำลอง (คู่ good) · ε = Y − α̂ − β̂·X โดย α̂, β̂ และเส้น μ̂, ±1σ̂, ±2σ̂ มาจาก {TRAIN} แท่งแรกเท่านั้น "
           f"(σ̂ = {_n(s)}% ค่าจริง {100 * SIGMA:.0f}%) · half-life ที่ประมาณได้ {_n(tr['half_life'], 1)} แท่ง "
           f"(ค่าจริง {HL:.0f}): ออกไปไกลแค่ไหนก็กลับเข้าหา μ̂ ภายในไม่กี่สัปดาห์ · ครึ่งหลังที่ไม่เคยเห็น ไม้บรรทัดเดิมยังใช้ได้ "
           f"(ค่าเฉลี่ยเลื่อน {_n(o['shift_sigma'], 2, True)}σ̂, sd เป็น {_n(o['sd_ratio'])} เท่า) แต่ไม่เป๊ะ: "
           f"แท่งที่หลุด ±2σ̂ มี {_n(o['beyond2_pct'], 1)}% เทียบ {_n(fo['beyond2_normal_pct'], 1)}% ถ้า z เป็น normal "
           f"เพราะ σ̂ จากช่วง train มักต่ำกว่าของจริง (ใน {fo['mc']['worlds']} โลก ค่ากลาง "
           f"{fo['mc']['good']['beyond2_p50_pct']}%)")
    return V.line_chart(
        "sas-p3-spread-good", None, [{"name": "ε", "y": 100.0 * a["eps"], "color": V.DARK, "width": 1.3}],
        "สเปรด ε ของคู่ good ตลอด 1,500 แท่ง พร้อมเส้นค่าเฉลี่ยและแถบหนึ่งและสองซิกมาจากช่วง train", cap,
        xlabel="แท่งที่ (วัน)", ylabel="ε (log × 100 ≈ %)", markers=False,
        hlines=[(2 * s, f"+2σ̂ = {_n(2 * s, 1, True)}", V.RED), (s, "+1σ̂"), (0.0, "μ̂ = 0"), (-s, f"{V.MINUS}1σ̂"),
                (-2 * s, f"{V.MINUS}2σ̂ = {_n(-2 * s, 1)}", V.RED)],
        xbands=[(0, TRAIN, f"train: {TRAIN} แท่งแรก (ประมาณ α̂, β̂, μ̂, σ̂)", V.BLUE),
                (TRAIN, N - 1, "นอกตัวอย่าง: ไม่เคยเห็น", V.MUTED)])


def _chart_rolling_beta(res):
    dm, f = res["demo"], figures(res)["rolling"]
    path = res["pairs"]["drift"]["beta_path"]
    cap = (f"ข้อมูลจำลอง · β ของ OLS จาก {ROLL} แท่งล่าสุด (สองกรอบใช้สเกลเดียวกัน) · คู่ good ที่ β จริงคงที่ {BETA} "
           f"ก็ยังแกว่ง {_n(f['good']['min'])}–{_n(f['good']['max'])} เพราะ {ROLL} แท่งมีข้อมูลน้อย — นั่นคือ noise ไม่ใช่ข่าว · "
           f"คู่ drift: rolling β̂ ไต่จาก {_n(f['drift']['first'])} ตอนต้น → {_n(f['drift']['last'])} ตอนท้าย ขณะที่ β จริงเลื่อน {BETA} → {BETA_END} แต่ตามหลัง"
           f"ราวครึ่งหน้าต่าง และแกว่งขึ้นลงระหว่างทางจนแยกจาก noise ได้ยากถ้าดูช่วงสั้น ๆ · "
           f"คู่ fake เหวี่ยง {_n(f['fake']['min'])} ถึง {_n(f['fake']['max'])} และกลับเครื่องหมาย · "
           f"เทียบ {f['mc']['worlds']} โลก: ช่วงแกว่ง (สูงสุด − ต่ำสุด) ค่ากลาง good {_n(f['mc']['good']['range_p50'], 1)} · "
           f"drift {_n(f['mc']['drift']['range_p50'], 1)} · fake {_n(f['mc']['fake']['range_p50'], 1)}")
    return V.stacked_panels(
        "sas-p3-rolling-beta",
        [{"y": [dm["good"]["rolling"], dm["drift"]["rolling"], path],
          "names": ["คู่ good", "คู่ drift", "β จริงของคู่ drift"], "color": [V.BLUE, V.AMBER, V.MUTED],
          "title": "มีสายจูง: good (β จริงคงที่) กับ drift (β จริงเลื่อน)",
          "hlines": [(BETA, f"β จริงของ good = {BETA}")]},
         {"y": dm["fake"]["rolling"], "color": V.RED, "title": "ไม่มีสายจูง: คู่ fake", "zero": True}],
        "rolling beta หน้าต่าง 250 แท่งของคู่ good คู่ drift และคู่ fake", cap,
        xlabel="แท่งที่ (วัน)", share_y=True, panel_h=150)


def _chart_spread_drift(res):
    a, f = res["demo"]["drift"], figures(res)["remedy"]
    s = 100.0 * a["train"]["sd"]
    st, wf, mc = f["drift"]["static"], f["drift"]["wf"], f["mc"]["drift"]
    cap = (f"ข้อมูลจำลอง (คู่ drift) · แกนตั้ง = ε × 100 (≈ %) · บน: β̂ คงที่จาก {TRAIN} แท่งแรก — พอพ้นช่วง train "
           f"สเปรดค่อย ๆ ไหลขึ้น จนอยู่นอกแถบ ±2σ̂ ของ train {_n(figures(res)['oos']['drift']['beyond2_pct'], 1)}% ของแท่ง "
           f"(ครึ่งหลัง: ADF {_n(st['adf'])} {st['verdict']}, sd {_n(st['sd_pct'])}% · สูตรยังคาย half-life ออกมาได้ "
           f"{st['half_life_bars']} แท่ง แต่ตัวเลขนี้ไม่มีความหมายเมื่อสอบตก — สเปรดแบบเดียวกันของคู่ที่ไม่มีสายจูงเลย"
           f"ก็ได้ค่ากลาง {f['mc']['fake']['static_hl_p50_bars']} แท่ง) · ล่าง: ประมาณ α, β ใหม่จาก {ROLL} แท่งล่าสุดทุก {REFIT} แท่ง — "
           f"สเปรดกลับมาแกว่งรอบศูนย์ (ADF {_n(wf['adf'])} {wf['verdict']} เมื่อเทียบเกณฑ์ของสเปรดแบบนี้เอง "
           f"{_n(f['wf_null']['c5'], 1)}, half-life {wf['half_life_bars']} แท่ง, sd {_n(wf['sd_pct'])}%) · "
           f"ใน {f['mc']['worlds']} โลก drift: β คงที่ผ่าน {mc['static_pass_pct']}% · walk-forward ผ่าน {mc['wf_pass_pct']}% · "
           f"สายจูงยังอยู่ แค่ความยาวเปลี่ยน: ไม้บรรทัดต้องขยับตาม")
    return V.stacked_panels(
        "sas-p3-spread-drift",
        [{"y": 100.0 * a["eps"], "color": V.RED, "title": f"สเปรด β คงที่ (β̂ = {_n(a['train']['beta'])} จากช่วง train)",
          "hlines": [(2 * s, "+2σ̂ ของ train"), (-2 * s, f"{V.MINUS}2σ̂ ของ train")]},
         {"y": 100.0 * a["wf_eps"], "color": V.BLUE,
          "title": f"สเปรด walk-forward (β จาก {ROLL} แท่งล่าสุด ปรับทุก {REFIT} แท่ง)", "zero": True}],
        "สเปรดของคู่ drift แบบ beta คงที่เทียบกับแบบ walk-forward", cap,
        xlabel="แท่งที่ (วัน)", share_y=True, panel_h=140,
        xbands=[(0, TRAIN, f"{TRAIN} แท่งแรก = train ของ β คงที่ · ตัวเลขเทียบกันวัดหลังจากนี้", V.BLUE)])


def _chart_wrong_beta(res):
    d, a, f = res["pairs"]["good"], res["demo"]["good"], figures(res)["wrong"]
    leak = (a["train"]["beta"] - 1.0) * (d["x"] - d["x"][:TRAIN].mean())
    b1, mc = f["beta1"], f["mc"]
    cap = (f"ข้อมูลจำลอง (คู่ good, β จริง {BETA}) · แกนตั้ง = log × 100 (≈ %) · บน: ε จาก β̂ = {_n(a['train']['beta'])} "
           f"แกว่งแคบรอบศูนย์ · ล่าง: ใช้ β = 1 (อัตราส่วนราคา) — สเปรดเท่ากับ ε ตัวเดิมบวกส่วนที่รั่ว (β − 1)·X "
           f"ซึ่งเป็น random walk เส้นแดงจึงเดินตามเส้นเทา · ช่วง train: sd โตเป็น {_n(b1['sd_ratio'])} เท่า, half-life ยืดจาก "
           f"{f['right']['half_life_bars']} เป็น {b1['half_life_bars']} แท่ง · การเปลี่ยนแปลงข้าม {H_LIST[-1]} แท่งมี sd "
           f"{_n(b1['chg_sd_h250_pct'])}% เทียบ {_n(f['right']['chg_sd_h250_pct'])}% เมื่อ β ถูก · ที่ต้องระวัง: "
           f"ADF ของสเปรดผิดตัวนี้ได้ {_n(b1['adf_train'])} ({b1['verdict_train']}) และใน {mc['worlds']} โลกผ่านถึง "
           f"{mc['adf_pass_train_pct']}% — ผ่านการทดสอบไม่ได้แปลว่า β ถูก")
    return V.stacked_panels(
        "sas-p3-wrong-beta",
        [{"y": 100.0 * a["eps"], "color": V.BLUE, "title": f"β ถูก: ε = Y − α̂ − {_n(a['train']['beta'])}·X", "zero": True},
         {"y": [100.0 * a["wrong"]["spread"], 100.0 * leak], "color": [V.RED, V.MUTED],
          "names": ["Y − X (β = 1)", "ส่วนที่รั่ว (β̂ − 1)·X"], "title": "β ผิด: ใช้อัตราส่วนราคา", "zero": True}],
        "สเปรดของคู่ good เมื่อใช้ beta ที่ถูก เทียบกับเมื่อใช้ beta เท่ากับหนึ่ง พร้อมส่วนที่รั่ว", cap,
        xlabel="แท่งที่ (วัน)", share_y=True, panel_h=140,
        xbands=[(0, TRAIN, f"train: {TRAIN} แท่งแรก", V.BLUE)])


def _chart_mc_beta(res):
    f = figures(res)["mc"]
    names = (("ols", "OLS: Y บน X", V.BLUE), ("ols_rev", "OLS: X บน Y กลับเศษส่วน", V.AMBER),
             ("tls", "TLS", V.PURPLE), ("ret", "β จากผลตอบแทน", V.GREEN))
    rows = [{"label": f"{n:,} แท่ง\n{name}", "mid": f[f"n{n}"][k]["p50"], "lo": f[f"n{n}"][k]["p5"],
             "hi": f[f"n{n}"][k]["p95"], "color": color}
            for n in (250, TRAIN) for k, name, color in names]
    a, b = f["n250"], f[f"n{TRAIN}"]
    cap = (f"ข้อมูลจำลอง · {a['worlds']:,} โลก good (β จริง {BETA} ทุกโลก) · จุด = ค่ากลางของ β̂ − β, เส้น = ช่วง 5–95% · "
           f"OLS ของ Y บน X ไม่เอนเอียง แต่ข้อมูลหนึ่งปีให้ β̂ คลาดได้ตั้งแต่ {_n(a['ols']['p5'], 2, True)} ถึง "
           f"{_n(a['ols']['p95'], 2, True)} (กว้าง {_n(a['ols']['width'])} → {_n(b['ols']['width'])} เมื่อมี {TRAIN} แท่ง) · "
           f"กลับข้างถดถอยแล้วเอนเอียงขึ้น (ค่ากลาง {_n(a['ols_rev']['p50'], 2, True)} ที่ 250 แท่ง) TLS อยู่ระหว่างกลาง · "
           f"β จากผลตอบแทนแคบกว่าในห้องทดลองนี้ ({_n(a['ret']['width'])} → {_n(b['ret']['width'])}) เพราะ ε ที่กลับตัวช้า"
           f"ทำให้ระดับราคามี noise ก้อนใหญ่ — แต่มันวัดการขยับตามกันรายวัน ไม่ได้พิสูจน์สายจูง "
           f"(คู่ fake ก็ให้ β จากผลตอบแทนที่นิ่ง)")
    return V.dot_interval(
        "sas-p3-mc-beta", rows,
        "ความคลาดเคลื่อนของ beta ที่ประมาณได้จากสี่วิธี เมื่อใช้ข้อมูล 250 และ 750 แท่ง", cap,
        zero=True, xlabel="β̂ − β จริง", fmt=lambda v: _n(v, 2, True), row_h=40)


def _chart_mc_hl(res):
    f = figures(res)["mc"]
    rows = [{"label": f"ใช้ข้อมูล {n:,} แท่ง", "mid": f[f"n{n}"]["hl_p50_bars"], "lo": f[f"n{n}"]["hl_p5_bars"],
             "hi": f[f"n{n}"]["hl_p95_bars"], "color": V.BLUE} for n in MC_SIZES]
    a = f["n250"]
    cap = (f"ข้อมูลจำลอง · {a['worlds']:,} โลก good ที่ half-life จริง {HL:.0f} แท่งทุกโลก · half-life ที่ประมาณจาก ε̂ "
           f"เอนเอียงต่ำ (ค่ากลาง {_n(a['hl_p50_bars'], 1)} แท่งเมื่อมี 250 แท่ง · {a['hl_below_true_pct']}% ของโลก"
           f"ได้ต่ำกว่าค่าจริง) และกว้าง: 5–95% = {a['hl_p5_bars']}–{a['hl_p95_bars']} แท่ง · "
           f"ใช้เป็นแผนได้ในระดับ \"ราวสองสัปดาห์\" ไม่ใช่ \"{_n(res['demo']['good']['train']['half_life'], 1)} แท่งเป๊ะ\"")
    return V.dot_interval(
        "sas-p3-mc-hl", rows,
        f"half-life ที่ประมาณได้เมื่อใช้ข้อมูล 250 750 และ 1,500 แท่ง เทียบกับค่าจริง {HL:.0f} แท่ง", cap,
        zero=False, xlabel="half-life ที่ประมาณได้ (แท่ง)",
        fmt=lambda v: _n(v, 0 if float(v).is_integer() else 1),       # หางเก็บเป็นจำนวนเต็ม · ค่ากลาง 1 ตำแหน่ง
        vlines=[(HL, f"ค่าจริง {HL:.0f} แท่ง", V.GREEN)])


def charts(res=None):
    """กราฟทั้งหมดของตอนที่ 3 → {ชื่อ: html}"""
    res = res or run()
    return {
        "sas-p3-scatter": _chart_scatter(res),
        "sas-p3-scatter-fake": _chart_scatter_fake(res),
        "sas-p3-eg-null": _chart_eg_null(res),
        "sas-p3-eg-power": _chart_eg_power(res),
        "sas-p3-spread-good": _chart_spread_good(res),
        "sas-p3-rolling-beta": _chart_rolling_beta(res),
        "sas-p3-spread-drift": _chart_spread_drift(res),
        "sas-p3-wrong-beta": _chart_wrong_beta(res),
        "sas-p3-mc-beta": _chart_mc_beta(res),
        "sas-p3-mc-hl": _chart_mc_hl(res),
    }


# ───────────────────────────── สรุปเมื่อรันตรง ๆ ─────────────────────────────
def _print_summary(f):
    s, b, eg, ar, oos = f["settings"], f["beta"], f["eg"], f["ar1"], f["oos"]
    rb, rem, mo, wr, mc = f["rolling"], f["remedy"], f["money"], f["wrong"], f["mc"]
    line = lambda t: print("\n" + t + "\n" + "─" * 78)
    print(f"ห้องทดลองตอนที่ 3 — Y − βX = ε  (ข้อมูลจำลอง · {s['n_bars']:,} แท่ง · train {s['train_bars']} แท่งแรก · "
          f"Monte Carlo {s['worlds']} โลก)")

    line("3a  β สี่วิธี (ค่าจริงของคู่ good = 1.4)")
    print(f"{'คู่':<7s}{'ช่วง':<8s}{'OLS Y~X':>9s}{'OLS X~Y':>9s}{'TLS':>8s}{'ผลตอบแทน':>10s}{'R² %':>7s}")
    for k in KINDS:
        for seg in ("train", "full", "second"):
            r = b[k][seg]
            print(f"{k:<7s}{seg:<8s}{r['ols']:>9.3f}{r['ols_rev']:>9.3f}{r['tls']:>8.3f}{r['ret']:>10.3f}{r['r2_pct']:>7.1f}")
    print(f"  |β̂ train − β̂ ทั้งช่วง|: good {b['good']['gap_train_full']} · drift {b['drift']['gap_train_full']} · "
          f"fake {b['fake']['gap_train_full']}   (ค่ากลาง {b['mc']['worlds']} โลก: {b['mc']['good']['gap_train_full_p50']} · "
          f"{b['mc']['drift']['gap_train_full_p50']} · {b['mc']['fake']['gap_train_full_p50']})")
    print(f"  ใช้เป็นสัญญาณเตือน: เกณฑ์ {b['mc']['flag_cut']} (คู่ good เกินแค่ 5%) → drift เกิน "
          f"{b['mc']['drift']['flag_pct']}% · fake เกิน {b['mc']['fake']['flag_pct']}% ของโลก")
    print(f"  |β̂ ระดับราคา − β̂ ผลตอบแทน|: good {b['good']['gap_levels_returns']} · fake {b['fake']['gap_levels_returns']}"
          f"   (ค่ากลาง: {b['mc']['good']['gap_levels_returns_p50']} · {b['mc']['fake']['gap_levels_returns_p50']})")
    na, pl = b["good"]["no_alpha"], b["good"]["price_levels"]
    print(f"  ลืม α: บังคับผ่านจุดกำเนิดได้ β = {na['beta_origin']} (sd ของ ε เป็น {na['sd_ratio']} เท่า) · "
          f"ใช้ β̂ เดิมแต่ไม่ลบ α̂ → ε อยู่ห่างศูนย์ {na['mean_shift_sigma']}σ ตลอด")
    print(f"  ถดถอยบนราคาดิบ: β = {pl['beta_shares']} หุ้น X ต่อหุ้น Y (หน่วยหุ้น ไม่ใช่หน่วยเงิน)")

    line("3b  Engle-Granger บนช่วง train")
    c, pa = eg["crit"], eg["plain_adf"]
    print(f"  เกณฑ์ EG ({c['n_sim']:,} โลก, n = {c['n_obs']}, 2 ขา): 1% {c['c1']} · 5% {c['c5']} · 10% {c['c10']}")
    print(f"  เกณฑ์ ADF ธรรมดา: 1% {pa['c1']} · 5% {pa['c5']} · 10% {pa['c10']}  → ใช้ผิดกับ ε̂ จะผ่านปลอม "
          f"{pa['false_pass_pct']}% ({pa['false_pass_times']} เท่าของ 5%)")
    for k in KINDS:
        e = eg[k]
        print(f"  {k:<6s} train: {e['stat_train']:>6.2f} (p {e['p_train_text']}) {e['verdict_train']:<8s} "
              f"ทั้งช่วง: {e['stat_full']:>6.2f} (p {e['p_full_text']}) {e['verdict_full']}")
    print(f"  อัตราผ่านเกณฑ์ 5% ใน {eg['mc']['worlds']:,} โลก (±{eg['mc']['moe95_pct']} จุด) เมื่อมีข้อมูล "
          + " / ".join(f"{n:,}" for n in EG_SIZES) + " แท่ง:")
    for k in KINDS:
        print(f"    {k:<6s} " + " / ".join(f"{eg['mc'][k][f'pass_n{n}_pct']:>4d}%" for n in EG_SIZES))

    line("3c  AR(1) ของ ε̂ ช่วง train")
    print(f"  {'':<10s}{'φ':>8s}{'half-life':>11s}{'μ %':>8s}{'σ_eq %':>8s}{'sd %':>7s}")
    t = ar["truth"]
    print(f"  {'ค่าจริง':<10s}{t['phi']:>8}{t['half_life_bars']:>11}{t['mu_pct']:>8}{t['sigma_eq_pct']:>8}{'':>7s}")
    for k in KINDS:
        r = ar[k]
        print(f"  {k:<10s}{r['phi']:>8}{r['half_life_bars']:>11}{r['mu_pct']:>8}{r['sigma_eq_pct']:>8}{r['sd_sample_pct']:>7}")
    te = ar["good"]["true_eps"]
    print(f"  (ε จริงของคู่ good ช่วงเดียวกัน: φ {te['phi']} · half-life {te['half_life_bars']} · sd {te['sd_sample_pct']}%)")

    line("3d  นอกตัวอย่าง: 750 แท่งหลัง วัดด้วยไม้บรรทัดของช่วง train")
    for k in KINDS:
        o, m = oos[k], oos["mc"][k]
        print(f"  {k:<6s} ค่าเฉลี่ยเลื่อน {o['shift_sigma']:+.2f}σ · sd ×{o['sd_ratio']} · ADF {o['adf']} (p {o['p_text']}) "
              f"{o['verdict']} · นอก ±2σ {o['beyond2_pct']}% · |z| สูงสุด {o['max_abs_z']}")
        print(f"         {oos['mc']['worlds']} โลก: |เลื่อน| {m['shift_abs_p50_sigma']}σ ({m['shift_abs_p5_sigma']}–"
              f"{m['shift_abs_p95_sigma']}) · sd ×{m['sd_ratio_p50']} ({m['sd_ratio_p5']}–{m['sd_ratio_p95']}) · "
              f"ADF ผ่าน {m['adf_pass_pct']}%")

    line(f"3e  rolling β ({s['roll_window_bars']} แท่ง)")
    for k in KINDS:
        r, m = rb[k], rb["mc"][k]
        print(f"  {k:<6s} {r['min']} ถึง {r['max']} (ช่วง {r['range']}) · เริ่ม {r['first']} จบ {r['last']}   "
              f"{rb['mc']['worlds']} โลก: ช่วง {m['range_p50']} ({m['range_p5']}–{m['range_p95']})")

    line("ยาแก้ของ drift: สเปรด β คงที่ vs walk-forward (750 แท่งหลัง)")
    wn = rem["wf_null"]
    print(f"  เกณฑ์ 5% ของ ADF สเปรด walk-forward (โลก fake {wn['worlds']:,} โลก): {wn['c5']} · ถ้าใช้เกณฑ์ ADF ธรรมดา "
          f"โลก fake ผ่านปลอม {wn['plain_false_pass_pct']}%")
    for k in KINDS:
        st, wf, m = rem[k]["static"], rem[k]["wf"], rem["mc"][k]
        print(f"  {k:<6s} คงที่: ADF {st['adf']} {st['verdict']} · HL {st['half_life_bars']} · sd {st['sd_pct']}%   "
              f"walk-forward: ADF {wf['adf']} {wf['verdict']} · HL {wf['half_life_bars']} · sd {wf['sd_pct']}%")
        print(f"         {rem['mc']['worlds']} โลก: คงที่ผ่าน {m['static_pass_pct']}% (HL กลาง {m['static_hl_p50_bars']}) · "
              f"walk-forward ผ่าน {m['wf_pass_pct']}% (HL กลาง {m['wf_hl_p50_bars']}, {m['wf_hl_p5_bars']}–{m['wf_hl_p95_bars']})")

    line("3f  β เป็นเงินบาท (คู่ good · ราคาปิดแท่งสุดท้าย)")
    print(f"  log Y {mo['log_y']} → {mo['price_y_baht']} บาท · log X {mo['log_x']} → {mo['price_x_baht']} บาท · β̂ = {mo['beta']}")
    print(f"  long สเปรด: ซื้อ Y {mo['y_baht']:,} บาท = {mo['shares_y']:,} หุ้น · ขาย X {mo['x_baht']:,} บาท = "
          f"{mo['shares_x']:,} หุ้น · เงินรวมสองขา {mo['gross_baht']:,} บาท")
    print(f"  หลังปัดหุ้น: Y {mo['y_actual_baht']:,} · X {mo['x_actual_baht']:,} บาท → β ที่ได้จริง {mo['beta_actual']} · "
          f"{mo['shares_x_per_share_y']} หุ้น X ต่อหุ้น Y (ต้นข้อมูลเคยเป็น {mo['shares_x_per_share_y_first']})")
    print(f"  ε ขึ้น 1σ ({mo['sigma_pct']}%): ได้ราว {mo['pnl_1sigma_baht']:,} บาท (Y ขึ้นเอง {mo['pnl_1sigma_y_only_baht']:,} · "
          f"X ลงเอง {mo['pnl_1sigma_x_only_baht']:,}) = {mo['pnl_1sigma_gross_pct']}% ของเงินรวม")
    print(f"  ตลาดพาขึ้นทั้งคู่ ε แทบไม่ขยับ (X +1%, Y +{mo['hedge_y_up_pct']}%): ขา Y {mo['hedge_y_leg_baht']:+,} · ขา X "
          f"{mo['hedge_x_leg_baht']:+,} → สุทธิ {mo['hedge_net_baht']:+,} บาท")
    print(f"  ต้นทุนไปกลับ ({mo['cost_bps']} bps ต่อขา): {mo['cost_roundtrip_baht']:,} บาท · เข้าที่ 2σ ออกที่ μ: "
          f"{mo['entry2_gross_baht']:,} → สุทธิ {mo['entry2_net_baht']:,} บาท")
    lot = mo["lot100"]
    print(f"  ถ้าต้องซื้อทีละ 100 หุ้น: Y {lot['shares_y']:,} · X {lot['shares_x']:,} หุ้น → β ที่ได้จริง {lot['beta_actual']}")

    line("3g  β ผิด: ใช้ β = 1 กับคู่ที่ β จริง 1.4")
    r, w, m = wr["right"], wr["beta1"], wr["mc"]
    print(f"  β ถูก : ADF {r['adf_train']} {r['verdict_train']} · HL {r['half_life_bars']} · sd {r['sd_train_pct']}%")
    print(f"  β = 1 : ADF {w['adf_train']} (p {w['p_train_text']}) {w['verdict_train']} · HL {w['half_life_bars']} · "
          f"sd {w['sd_train_pct']}% (×{w['sd_ratio']}) · ครึ่งหลัง ADF {w['adf_oos']} {w['verdict_oos']}")
    print("  sd ของการเปลี่ยนแปลงข้าม h แท่ง (%):  h = " + "  ".join(f"{h:>5d}" for h in H_LIST))
    print("     β ถูก                              " + "  ".join(f"{r[f'chg_sd_h{h}_pct']:>5.1f}" for h in H_LIST))
    print("     β = 1                              " + "  ".join(f"{w[f'chg_sd_h{h}_pct']:>5.1f}" for h in H_LIST))
    print(f"     ค่ากลาง {m['worlds']} โลก · β ถูก            " + "  ".join(f"{m[f'chg_sd_right_h{h}_pct']:>5.1f}" for h in H_LIST))
    print(f"     ค่ากลาง {m['worlds']} โลก · β = 1            " + "  ".join(f"{m[f'chg_sd_beta1_h{h}_pct']:>5.1f}" for h in H_LIST))
    print(f"  {m['worlds']} โลก: สเปรด β = 1 ผ่าน ADF 5% ในช่วง train {m['adf_pass_train_pct']}% · ครึ่งหลัง "
          f"{m['adf_pass_oos_pct']}% · HL กลาง {m['hl_p50_bars']} (p5 {m['hl_p5_bars']}) เทียบ "
          f"{m['hl_right_p50_bars']} · sd ×{m['sd_ratio_p50']} ({m['sd_ratio_p5']}–{m['sd_ratio_p95']})")

    line(f"3h  ประมาณได้แม่นแค่ไหน ({s['mc_worlds']:,} โลก good)")
    print(f"  {'แท่ง':<7s}{'วิธี':<10s}{'เอนเอียง':>9s}{'5%':>8s}{'กลาง':>8s}{'95%':>8s}")
    for n in MC_SIZES:
        for k in ("ols", "ols_rev", "tls", "ret"):
            r = mc[f"n{n}"][k]
            print(f"  {n:<7d}{k:<10s}{r['bias']:>+9.2f}{r['p5']:>+8.2f}{r['p50']:>+8.2f}{r['p95']:>+8.2f}")
    for n in MC_SIZES:
        r = mc[f"n{n}"]
        print(f"  half-life จาก {n:>5,} แท่ง: กลาง {r['hl_p50_bars']} ({r['hl_p5_bars']}–{r['hl_p95_bars']}) · "
              f"ต่ำกว่าค่าจริง {r['hl_below_true_pct']}% ของโลก · σ_eq กลาง {r['sigma_eq_p50_pct']}% "
              f"({r['sigma_eq_p5_pct']}–{r['sigma_eq_p95_pct']})")


if __name__ == "__main__":
    _print_summary(figures())
