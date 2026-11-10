#!/usr/bin/env python3
"""แกนคำนวณของห้องทดลอง "แกะสไลด์ Stat Arb" (docs/statarb-slides-*.html)

ทุกตัวเลขและทุกกราฟในชุดนี้มาจากฟังก์ชันในไฟล์นี้ + โมดูลทดลอง tools/sas_exp*.py
ตั้งใจใช้ numpy อย่างเดียว เพื่อให้ผู้อ่านรันตามได้โดยไม่ต้องติดตั้งอะไรเพิ่ม
และเพื่อให้ "เปิดฝาดูได้" ว่าการทดสอบแต่ละตัวทำอะไรจริง ๆ ไม่ใช่กล่องดำ

ข้อตกลงที่ใช้ทั้งชุด (สำคัญ — อ่านก่อนใช้)
  • ราคาทุกตัวเป็น log price · y, x คืออนุกรมของ log P
  • สเปรด ε_t = y_t − α − β·x_t   · "long สเปรด 1 หน่วย" = ซื้อ Y 1 บาท + ขาย X β บาท
  • pos[t] คือสถานะที่ "ตัดสินใจตอนสิ้นแท่ง t" ด้วยข้อมูลถึงแท่ง t เท่านั้น
    จึงเริ่มรับผลตอบแทนตั้งแต่แท่ง t+1 (lag=1) — ห้ามใช้ lag=0 ยกเว้นตั้งใจสาธิตบั๊ก
    lag=1 แปลว่า "ซื้อขายได้ที่ราคาปิดของแท่งที่ให้สัญญาณพอดี" (มองโลกแง่ดี แต่เป็นมาตรฐาน)
    lag=2 = ได้ราคาช้าไปหนึ่งแท่ง (เข้มกว่า) — ตัวเลขสำคัญควรรายงานทั้งสองแบบ
  • ผลตอบแทนคิดต่อ "เงินรวมสองขา" (gross = 1 + |β|) 1 หน่วย และใช้ผลต่างของ log price
    (Δy − β·Δx)/(1+|β|) แทนผลตอบแทนจริงของการถือหุ้น — เป็นค่าประมาณ: กฎที่ long กับ short
    พอ ๆ กัน ความคลาดหักล้างกันเกือบหมด (คู่ good จำลอง: เฉลี่ยไม่ถึง 1 bp ต่อปี แต่ละโลกคลาดได้ราว
    ±10 bps ต่อปี) แต่พอร์ตที่ถือข้างเดียวตลอดจะคลาดราว 1% ต่อปี
  • ต้นทุน c = ต้นทุนเที่ยวเดียวต่อขา เป็นสัดส่วนของมูลค่าที่ซื้อขาย (เช่น 5 bps = 0.0005)
    เข้า 1 ครั้งเสีย c ต่อ gross · ครบรอบ (เข้า+ออก) เสีย 2c ต่อ gross
    ข้อยกเว้นเดียว: ไม้ที่ "ยังเปิดค้าง" ตอนข้อมูลจบ ถูกตีมูลค่าที่ราคาปิดสุดท้าย ยังไม่ได้จ่ายค่าออก
    (ดู info["open_at_end"] ของ spread_pnl)
  • ข้อมูลเสีย (NaN/inf · แถวไม่พอ · ราคาค้างเป็นค่าคงที่) ไม่ถูกปล่อยผ่านเงียบ ๆ:
    ฟังก์ชันที่ "ประกอบสเปรด/ทำ backtest จากราคา" (ols, eg_test, spread_pnl, walk_forward_pair,
    portfolio_pnl) จะหยุดด้วย ValueError พร้อมข้อความบอกสาเหตุ
    ส่วน "สถิติของอนุกรมเส้นเดียว" (adf_stat, adf_stat_batch, fit_ar1, variance_ratio, p_value)
    คืน NaN = "คำนวณไม่ได้" — ไม่ใช่ตัวเลขที่ดูเหมือนคำตัดสิน

รันไฟล์นี้ตรง ๆ เพื่อทดสอบตัวเอง:
    python3 tools/sas_core.py
"""

import math

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

SEED = 20261110
DAYS_PER_YEAR = 252


def _check_finite(where, **named):
    """หยุดพร้อมข้อความชัด ๆ ถ้าข้อมูลมี NaN/inf — ดีกว่าปล่อยให้ผลลัพธ์กลายเป็น NaN หรือ 0 เงียบ ๆ"""
    for name, a in named.items():
        a = np.asarray(a, float)
        if not np.isfinite(a).all():
            bad = ~np.isfinite(a)
            first = tuple(int(i) for i in np.argwhere(bad)[0])
            first = first[0] if len(first) == 1 else first
            raise ValueError(f"{where}: {name} มี NaN/inf {int(bad.sum())} จุด (จุดแรกที่ตำแหน่ง {first}) "
                             "— ตัดแถวที่ขาดออกหรือเติมค่าก่อน")


# ───────────────────────── ตัวสร้างข้อมูลจำลอง ─────────────────────────

def rng(offset=0):
    """ตัวสุ่มที่ทำซ้ำได้ — แต่ละการทดลองใช้ offset ของตัวเอง จะได้ไม่กระทบกัน"""
    return np.random.default_rng(SEED + int(offset))


def phi_from_half_life(half_life):
    """สัมประสิทธิ์ AR(1) ที่ให้ half-life ตามต้องการ (หน่วย = จำนวนแท่ง)"""
    return 0.5 ** (1.0 / float(half_life))


def half_life_from_phi(phi):
    """half-life (จำนวนแท่ง) จากสัมประสิทธิ์ AR(1) = −ln2 / ln φ
      0 < φ < 1   ดึงกลับทีละน้อย → half-life เป็นจำนวนบวก (φ ใกล้ 1 = ช้า)
      −1 < φ ≤ 0  ดึงกลับ "ภายในแท่งเดียว" → 0.0  (white noise, bid-ask bounce ·
                  φ ติดลบ = เด้งเลยค่าเฉลี่ยไปอีกฝั่ง) — นี่คือการดึงกลับที่เร็วที่สุด ไม่ใช่ "ไม่ดึงกลับ"
      |φ| ≥ 1     ไม่ดึงกลับ (random walk หรือระเบิดออก) → inf
      φ เป็น NaN  → NaN (ประมาณไม่ได้)"""
    phi = float(phi)
    if math.isnan(phi):
        return math.nan
    if abs(phi) >= 1.0:
        return math.inf
    if phi <= 0.0:
        return 0.0
    return -math.log(2.0) / math.log(phi)


def random_walk(n, sigma, g, drift=0.0, x0=0.0):
    """random walk: x_t = x_{t−1} + drift + σ·e_t  (ไม่มีแรงดึงกลับ)"""
    return x0 + np.cumsum(drift + sigma * g.standard_normal(n))


def ar1(n, half_life, sigma_eq, g, mu=0.0):
    """AR(1) ดึงกลับสู่ μ: x_t − μ = φ·(x_{t−1} − μ) + e_t
    เริ่มจากการแจกแจงนิ่งของตัวเอง · sigma_eq = ส่วนเบี่ยงเบนมาตรฐานระยะยาวของ x"""
    phi = phi_from_half_life(half_life)
    sd_e = sigma_eq * math.sqrt(1.0 - phi * phi)
    e = sd_e * g.standard_normal(n)
    x = np.empty(n)
    x[0] = sigma_eq * g.standard_normal()
    for t in range(1, n):
        x[t] = phi * x[t - 1] + e[t]
    return mu + x


def ar1_batch(n_series, n, half_life, sigma_eq, g):
    """AR(1) หลายเส้นพร้อมกัน (n_series × n) — ใช้กับ Monte Carlo"""
    phi = phi_from_half_life(half_life)
    sd_e = sigma_eq * math.sqrt(1.0 - phi * phi)
    e = sd_e * g.standard_normal((n_series, n))
    x = np.empty((n_series, n))
    x[:, 0] = sigma_eq * g.standard_normal(n_series)
    for t in range(1, n):
        x[:, t] = phi * x[:, t - 1] + e[:, t]
    return x


def make_pair(kind, n, g, beta=1.4, alpha=0.3, half_life=12.0, sigma_eq=0.03, sigma_x=0.015,
              x0=4.0, beta_end=2.2, break_at=0.6, sigma_perm=0.012, sigma_m=0.012, sigma_idio=0.008):
    """สร้างคู่สินทรัพย์จำลอง (log price) ที่ "รู้เฉลย" ว่ามีสายจูงจริงหรือไม่ — สี่แบบ

      good  : มีสายจูงจริง   y = α + β·x + ε   โดย ε ดึงกลับ (AR(1) half-life, sigma_eq)
      drift : สายจูงยืด      Δy = β_t·Δx + Δε  โดย β_t ค่อย ๆ เลื่อนจาก beta → beta_end
      break : สายจูงขาด      เหมือน good จนถึงสัดส่วน break_at ของข้อมูล แล้ว ε ได้ส่วนที่ไม่กลับ
                             (random walk σ = sigma_perm ต่อแท่ง) เพิ่มเข้ามา
      fake  : ไม่มีสายจูงเลย  Δy = m + i_y , Δx = m + i_x (ผลตอบแทนสัมพันธ์กันสูงเพราะ m ร่วม
                             แต่ระยะห่างของราคาเป็น random walk)

    คืน dict: y, x, eps (ส่วนที่ดึงกลับจริง · fake ไม่มี = None), beta_path, kind

    ข้อควรรู้ก่อนเขียนการทดลอง (วัดจากการจำลองแล้ว)
      • drift: beta_path เป็น β ใน "โลกของผลตอบแทน" (Δy ต่อ Δx) — ห้ามนำไปคูณระดับราคาเพื่อสร้าง
        สเปรด: y − β_t·x ไม่นิ่ง มันไหลไปตาม −x0·(β_t − beta)
      • drift ผ่านการทดสอบ Engle-Granger แบบ β คงที่ "เกือบทุกครั้ง" (ราว 93% ที่ 1,500 แท่ง) และ break
        ผ่านได้ราวหนึ่งในสามเมื่อทดสอบทั้งช่วง (ช่วงก่อนขาดเหมือนคู่ good ทุกประการ จึงผ่านเกือบทุกครั้ง)
        — อย่าเขียนว่าสองแบบนี้ "สอบตก" ให้รายงานอัตราผ่านที่วัดได้จริงในการทดลองนั้น
      • fake: sigma_x ไม่ถูกใช้ · ความผันผวนต่อแท่งของ x และ y = √(sigma_m² + sigma_idio²)
        (ตัวสุ่ม n ตัวแรกถูกจั่วแล้วทิ้ง เพื่อให้ลำดับการสุ่มเหมือนกันทุกแบบ) · beta_path เป็น 1 ทั้งเส้น"""
    x_inc = sigma_x * g.standard_normal(n)
    x = x0 + np.cumsum(x_inc)
    beta_path = np.full(n, float(beta))
    if kind == "fake":
        m = sigma_m * g.standard_normal(n)
        x = x0 + np.cumsum(m + sigma_idio * g.standard_normal(n))
        y = (alpha + beta * x0) + np.cumsum(m + sigma_idio * g.standard_normal(n))
        return {"y": y, "x": x, "eps": None, "beta_path": np.ones(n), "kind": kind}
    eps = ar1(n, half_life, sigma_eq, g)
    if kind == "good":
        y = alpha + beta * x + eps
    elif kind == "drift":
        beta_path = np.linspace(beta, beta_end, n)
        y0 = alpha + beta * x0
        y = y0 + np.cumsum(beta_path * x_inc) + eps
    elif kind == "break":
        k = int(break_at * n)
        perm = np.zeros(n)
        perm[k:] = np.cumsum(sigma_perm * g.standard_normal(n - k))
        y = alpha + beta * x + eps + perm
        return {"y": y, "x": x, "eps": eps, "perm": perm, "break_index": k,
                "beta_path": beta_path, "kind": kind}
    else:
        raise ValueError(f"ไม่รู้จัก kind={kind!r}")
    return {"y": y, "x": x, "eps": eps, "beta_path": beta_path, "kind": kind}


_DEMO_OFFSET = {"good": 12, "drift": 13, "break": 14, "fake": 11}


def demo_pair(kind="good", n=1500):
    """คู่ตัวอย่างหลักของทั้งชุด (ทุกตอนใช้เส้นเดียวกัน) — 1,500 แท่ง ≈ 6 ปีของข้อมูลรายวัน
    seed ของแต่ละแบบ "ถูกเลือก" ให้เห็นอาการชัด (เป็นตัวอย่างประกอบ ไม่ใช่ค่าเฉลี่ย)
    ภาพ "ทั่วไป" ต้องดูจากผล Monte Carlo หลายร้อยโลกในแต่ละตอนเสมอ"""
    return make_pair(kind, n, rng(_DEMO_OFFSET[kind]))


# ───────────────────────── regression ─────────────────────────

def ols(y, X, const=True):
    """OLS ธรรมดา · คืน coef, se, t, resid, r2, s2 (ถ้า const=True ตัวแรกของ coef คือค่าคงที่)

    วิธีคิด: แก้สมการปกติ (X'X)·b = X'y — ถ้ามีค่าคงที่จะ "ลบค่าเฉลี่ยออกก่อน" แล้วค่อยแก้
    ผลทางคณิตศาสตร์เท่ากับสูตรตำราทุกประการ แต่ไม่เสียทศนิยมเมื่อระดับของข้อมูลสูงกว่าความผันผวนมาก
    r2: const=True วัดเทียบกับค่าเฉลี่ยของ y · const=False วัดเทียบกับศูนย์ (แบบ uncentred ตามธรรมเนียม
        ของการถดถอยที่ไม่มีค่าคงที่) จึงอยู่ใน [0, 1] ทั้งสองกรณี
    ข้อมูลใช้ไม่ได้ → หยุดด้วย ValueError ที่บอกสาเหตุ: แถวไม่พอ (ต้องมากกว่าจำนวนสัมประสิทธิ์) ·
    มี NaN/inf · ตัวแปรอธิบายเป็นค่าคงที่หรือซ้ำกัน (สมการแก้ไม่ได้ — เป็น np.linalg.LinAlgError
    ซึ่งนับเป็น ValueError ด้วย)"""
    y = np.asarray(y, float)
    X = np.asarray(X, float)
    if X.ndim == 1:
        X = X[:, None]
    n, p = X.shape
    k = p + (1 if const else 0)
    if len(y) != n:
        raise ValueError(f"ols: y มี {len(y)} แถว แต่ X มี {n} แถว")
    if n - k < 1:
        raise ValueError(f"ols: ข้อมูลไม่พอ — มี {n} แถว แต่ต้องประมาณ {k} ค่า (ต้องมีอย่างน้อย {k + 1} แถว)")
    _check_finite("ols", y=y, X=X)
    if const:
        xm, ym = X.mean(axis=0), float(y.mean())
        Xc, yc = X - xm, y - ym
    else:
        Xc, yc = X, y
    xtx = Xc.T @ Xc
    # ตัวแปรอธิบายที่ "ไม่ขยับเลย" เมื่อเทียบกับระดับของตัวเอง (sd/ระดับ < 1e-12) = ค่าคงที่ → แยกจาก α ไม่ได้
    if const and p and (np.diag(xtx) <= n * (1e-12 * xm) ** 2).any():
        raise np.linalg.LinAlgError("ols: ตัวแปรอธิบายเป็นค่าคงที่ (ราคาค้าง?) — แยกจากค่าคงที่ α ไม่ได้")
    dup = "ols: ตัวแปรอธิบายเป็นศูนย์ทั้งเส้นหรือซ้ำกัน (ตัวหนึ่งเขียนได้จากตัวอื่น) — สมการแก้ไม่ได้"
    if p >= 2:  # หลายตัวแปร: ถ้าตัวหนึ่งเขียนได้จากตัวอื่นเกือบเป๊ะ สัมประสิทธิ์จะเป็นเลขมั่ว → หยุดดีกว่า
        d = np.sqrt(np.diag(xtx))
        if (d == 0).any() or np.linalg.eigvalsh(xtx / np.outer(d, d))[0] < 1e-10:
            raise np.linalg.LinAlgError(dup)
    try:
        b = np.linalg.solve(xtx, Xc.T @ yc)
        xtx_inv = np.linalg.inv(xtx)
    except np.linalg.LinAlgError:
        raise np.linalg.LinAlgError(dup) from None
    resid = yc - Xc @ b
    rss = float(resid @ resid)
    s2 = rss / (n - k)
    var = s2 * np.diag(xtx_inv)
    if const:   # แปลงกลับ: α = ȳ − x̄·b · Var(α) = s²·(1/n + x̄'(X'X)⁻¹x̄)
        coef = np.concatenate([[ym - xm @ b], b])
        var = np.concatenate([[s2 * (1.0 / n + xm @ xtx_inv @ xm)], var])
    else:
        coef = b
    se = np.sqrt(var)
    tss = float(yc @ yc)
    r2 = 1.0 - rss / tss if tss > 0 else 0.0
    with np.errstate(divide="ignore", invalid="ignore"):
        t = coef / se
    return {"coef": coef, "se": se, "t": t, "resid": resid, "r2": r2, "s2": s2}


def tls_beta(y, x):
    """Total least squares (orthogonal regression) ของ y บน x · คืน (alpha, beta)
    สมมาตร: สลับ y กับ x แล้วได้เส้นเดิม (β กลายเป็น 1/β) ต่างจาก OLS ที่ได้สองคำตอบ
    แต่ไม่ใช่ "β ที่ถูกเสมอ":
      • ขึ้นกับหน่วย/สเกล — สมมติว่าสองขามี noise ขนาดเท่ากันในหน่วยเดียวกัน
        จึงใช้ได้เมื่อ y และ x เป็น log price ทั้งคู่เท่านั้น (คูณขาใดขาหนึ่งด้วย 100 แล้ว β เปลี่ยน)
      • ถ้า noise อยู่ที่ y ฝั่งเดียว (แบบคู่ good ของห้องทดลอง) OLS y~x คือตัวที่ไม่เอนเอียง
        ส่วน TLS จะเอนสูงเล็กน้อย — TLS อยู่ระหว่าง β ของ OLS สองทิศเสมอ
    กรณีสุดขอบ: y กับ x ไม่สัมพันธ์กันเลยและ x ผันผวนกว่า → β = 0 · ถ้า y ผันผวนกว่า (หรือ x คงที่)
    เส้นตั้งฉาก → β = inf, alpha = NaN · บอกทิศไม่ได้เลย → NaN"""
    y = np.asarray(y, float)
    x = np.asarray(x, float)
    cov = np.cov(x, y)
    sxx, syy, sxy = float(cov[0, 0]), float(cov[1, 1]), float(cov[0, 1])
    d = syy - sxx
    r = math.hypot(d, 2.0 * sxy)
    if sxy == 0.0:
        beta = 0.0 if d < 0 else (math.inf if d > 0 else math.nan)
    elif d >= 0:
        beta = (d + r) / (2.0 * sxy)
    else:               # สูตรเดียวกัน เขียนอีกรูปเพื่อไม่ให้ลบเลขใกล้กันจนเสียทศนิยม
        beta = 2.0 * sxy / (r - d)
    alpha = float(y.mean() - beta * x.mean()) if math.isfinite(beta) else math.nan
    return alpha, float(beta)


# ───────────────────────── stationarity ─────────────────────────

def adf_stat(x, lags=1, const=True):
    """ADF: ค่า t ของ ρ ใน  Δx_t = a + ρ·x_{t−1} + Σ γ_i·Δx_{t−i} + e_t
    ρ ติดลบมาก = มีแรงดึงกลับ · ค่า t นี้ "ห้าม" เทียบกับตาราง normal/t ปกติ
    ต้องเทียบกับค่าวิกฤตของ Dickey-Fuller (ดู mc_null_adf / mc_null_eg) ที่จำลองด้วย lags เดียวกัน

    lags = จำนวนพจน์ Δx ย้อนหลังที่ใส่เพื่อซับความสัมพันธ์ระยะสั้น · ค่าตั้งต้น 1 ตายตัว (ไม่มีการเลือกให้)
    พอสำหรับข้อมูลรายวันทั่วไป แต่ถ้าราคามี noise ของการเสนอซื้อขาย (แท่งสั้น, bid-ask bounce,
    ราคาค้าง) ต้องเพิ่ม lags (เช่น 4) ไม่เช่นนั้นการทดสอบจะ "ผ่าน" บ่อยเกินจริงมาก

    คำนวณไม่ได้ → NaN (ไม่ใช่ error): ข้อมูลสั้นเกินไป (เหลือ degree of freedom < 2) · มี NaN/inf ·
    อนุกรมคงที่หรือเป็นเส้นตรงเป๊ะ (Δx เท่ากันทุกแท่ง) · สมการแก้ไม่ได้"""
    x = np.asarray(x, float)
    lags = int(lags)
    if lags < 0:
        raise ValueError("adf_stat: lags ต้อง ≥ 0")
    k = 1 + lags + (1 if const else 0)
    if len(x) - 1 - lags - k < 2 or not np.isfinite(x).all():
        return math.nan
    dx = np.diff(x)
    if np.ptp(dx) == 0:         # ราคาค้าง (Δx = 0 ทุกแท่ง) หรือเส้นตรงเป๊ะ → ไม่มีอะไรให้ทดสอบ
        return math.nan
    y = dx[lags:]
    cols = [x[lags:-1]]
    for i in range(1, lags + 1):
        cols.append(dx[lags - i:len(dx) - i])
    try:
        r = ols(y, np.column_stack(cols), const=const)
    except ValueError:
        return math.nan
    t = float(r["t"][1 if const else 0])
    return t if math.isfinite(t) else math.nan


def adf_stat_batch(x, lags=1, const=True, chunk=2000):
    """ADF ของหลายเส้นพร้อมกัน (n_series × n) — ผลเท่ากับเรียก adf_stat ทีละเส้น
    เส้นที่คำนวณไม่ได้ (คงที่หรือเส้นตรงเป๊ะ · มี NaN · สมการแก้ไม่ได้) ได้ NaN เฉพาะเส้นนั้น
    ไม่ทำให้ทั้งชุดล้ม"""
    x = np.asarray(x, float)
    lags = int(lags)
    if lags < 0:
        raise ValueError("adf_stat_batch: lags ต้อง ≥ 0")
    out = np.full(x.shape[0], np.nan)
    k = 1 + lags + (1 if const else 0)
    if x.shape[1] - 1 - lags - k < 2:
        return out
    for s in range(0, x.shape[0], chunk):
        xs = x[s:s + chunk]
        flat = np.ptp(np.diff(xs, axis=1), axis=1) == 0     # ราคาค้างหรือเส้นตรงเป๊ะ → NaN เหมือน adf_stat
        if const:   # ลบระดับของแต่ละเส้นออกก่อน: ค่า t ไม่เปลี่ยน (ค่าคงที่ a ซับไว้) แต่แม่นขึ้นเมื่อระดับสูง
            xs = xs - xs.mean(axis=1, keepdims=True)
        dx = np.diff(xs, axis=1)
        y = dx[:, lags:]
        cols = [xs[:, lags:-1]]
        for i in range(1, lags + 1):
            cols.append(dx[:, lags - i:dx.shape[1] - i])
        if const:
            cols = [np.ones_like(y)] + cols
        X = np.stack(cols, axis=2)
        xtx = np.einsum("smi,smj->sij", X, X)
        xty = np.einsum("smi,sm->si", X, y)
        try:
            coef = np.linalg.solve(xtx, xty[..., None])[..., 0]
            xtx_inv = np.linalg.inv(xtx)
        except np.linalg.LinAlgError:
            # มีบางเส้นในชุดนี้ที่สมการแก้ไม่ได้ → คิดทีละเส้นแทน (ช้ากว่า แต่เส้นที่เสียได้ NaN เส้นอื่นได้ค่าปกติ)
            out[s:s + chunk] = [adf_stat(row, lags=lags, const=const) for row in x[s:s + chunk]]
            continue
        resid = y - np.einsum("smi,si->sm", X, coef)
        s2 = (resid ** 2).sum(axis=1) / (y.shape[1] - X.shape[2])
        j = 1 if const else 0
        with np.errstate(divide="ignore", invalid="ignore"):
            stat = coef[:, j] / np.sqrt(s2 * xtx_inv[:, j, j])
        stat[flat | ~np.isfinite(stat)] = np.nan
        out[s:s + chunk] = stat
    return out


def resid_batch(y, X):
    """ส่วนเหลือของ OLS (มีค่าคงที่) ของหลายระบบพร้อมกัน
    y: (S, n) · X: (S, n, p) → resid (S, n)
    ระบบที่มีตัวแปรอธิบายเป็นค่าคงที่ (ราคาค้าง) หรือมี NaN ได้ส่วนเหลือเป็น NaN เฉพาะระบบนั้น
    (adf_stat_batch จะให้ NaN ต่อ) · ตัวแปรอธิบายซ้ำกันจนสมการแก้ไม่ได้ → LinAlgError"""
    y = np.asarray(y, float)
    X = np.asarray(X, float)
    stale = (np.ptp(X, axis=1) == 0).any(axis=1)
    # ลบค่าเฉลี่ยของแต่ละระบบออกก่อน: ส่วนเหลือเท่าเดิม (มีค่าคงที่อยู่แล้ว) แต่แม่นขึ้นเมื่อระดับสูง
    y = y - y.mean(axis=1, keepdims=True)
    X = X - X.mean(axis=1, keepdims=True)
    X1 = np.concatenate([np.ones(X.shape[:2] + (1,)), X], axis=2)
    xtx = np.einsum("smi,smj->sij", X1, X1)
    xty = np.einsum("smi,sm->si", X1, y)
    xtx[stale] = np.eye(X1.shape[2])            # ระบบที่ราคาค้าง: ใส่สมการหลอกให้แก้ผ่าน แล้วทับผลด้วย NaN ข้างล่าง
    try:
        coef = np.linalg.solve(xtx, xty[..., None])[..., 0]
    except np.linalg.LinAlgError:
        raise np.linalg.LinAlgError("resid_batch: บางระบบมีตัวแปรอธิบายซ้ำกัน — สมการแก้ไม่ได้") from None
    resid = y - np.einsum("smi,si->sm", X1, coef)
    resid[stale] = np.nan
    return resid


def mc_null_adf(n_obs, n_sim=20000, lags=1, g=None, const=True):
    """การแจกแจงของค่า ADF เมื่อ "ความจริงคือ random walk" (ไม่มีแรงดึงกลับ)
    ใช้หาค่าวิกฤตเอง แทนการเปิดตาราง · คืนอาร์เรย์เรียงจากน้อยไปมาก
    ค่าวิกฤตขึ้นกับ n_obs, lags และ const — ต้องจำลองด้วยค่าเดียวกับที่ใช้คำนวณสถิติตัวจริงเสมอ
    ความแม่น: ค่าวิกฤต 5% จาก 20,000 โลกคลาดได้ราว ±0.03 (1%: ±0.04) — เลขที่จะพิมพ์ลงในบท
    ควรใช้ n_sim ≥ 100,000"""
    g = g or rng(9001)
    x = np.cumsum(g.standard_normal((n_sim, n_obs)), axis=1)
    return np.sort(adf_stat_batch(x, lags=lags, const=const))


def mc_null_eg(n_obs, n_vars=2, n_sim=20000, lags=1, g=None, chunk=2000):
    """การแจกแจงของค่า Engle-Granger เมื่อ "ไม่มีตัวไหนผูกกันเลย"
    จำลอง random walk อิสระ n_vars เส้น · ถดถอยเส้นแรกบนเส้นที่เหลือ (มีค่าคงที่)
    แล้ววัด ADF (ไม่มีค่าคงที่) ของส่วนเหลือ · ยิ่ง n_vars มาก ค่าวิกฤตยิ่งติดลบมาก

    ค่าวิกฤตขึ้นกับ n_obs, n_vars และ lags — ต้องจำลองด้วยค่าเดียวกับที่ใช้คำนวณสถิติตัวจริง
    (eg_test คืน n_obs, n_vars, lags มาให้ส่งต่อตรง ๆ) · ตาราง MacKinnon ในตำราคิดที่ lags=0
    จึงต่างจากค่าที่จำลองด้วย lags=1 ได้เล็กน้อยเมื่อ n=250 (ราว 0.02–0.05 ยิ่ง n_vars มากยิ่งต่าง)
    และต่างมากขึ้นเมื่อ lags มากขึ้น — เป็นความต่างจริง ไม่ใช่ความคลาดจากการสุ่ม
    ความแม่น: ค่าวิกฤต 5% จาก 20,000 โลกคลาดได้ราว ±0.03 (1%: ±0.04) — เลขที่จะพิมพ์ลงในบท
    ควรใช้ n_sim ≥ 100,000"""
    g = g or rng(9002 + n_vars)
    out = np.empty(n_sim)
    for s in range(0, n_sim, chunk):
        m = min(chunk, n_sim - s)
        w = np.cumsum(g.standard_normal((m, n_obs, n_vars)), axis=1)
        res = resid_batch(w[:, :, 0], w[:, :, 1:])
        out[s:s + m] = adf_stat_batch(res, lags=lags, const=False)
    return np.sort(out)


def crit_values(null_sorted, qs=(0.01, 0.05, 0.10)):
    """ค่าวิกฤตจากการแจกแจงใต้สมมติฐานว่าง — "ต้องติดลบกว่านี้ถึงจะเรียกว่าผ่าน"
    (เป็นค่าจากการสุ่ม: ดูความแม่นใน mc_null_adf / mc_null_eg)"""
    return {q: float(np.quantile(null_sorted, q)) for q in qs}


def p_value(stat, null_sorted):
    """p-value แบบจำลอง: สัดส่วนของโลกที่ "ไม่มีอะไรเลย" ที่ให้ค่าติดลบได้เท่านี้หรือกว่า
    ได้ 0.0 แปลว่า "น้อยกว่า 1/จำนวนโลกที่จำลอง" ไม่ใช่ศูนย์จริง ๆ · stat เป็น NaN → NaN
    (อาร์เรย์ null ไม่จำเป็นต้องเรียงมาก่อน)"""
    if math.isnan(float(stat)):
        return math.nan
    null = np.asarray(null_sorted, float)
    return float(np.count_nonzero(null <= stat)) / len(null)


def eg_test(y, X, lags=1):
    """Engle-Granger สองขั้น: (1) ถดถอย y บน X (มีค่าคงที่) (2) ADF บนส่วนเหลือ
    คืน alpha, beta (อาร์เรย์), resid, adf, r2 และ n_obs, n_vars, lags
    adf ต้องเทียบกับ mc_null_eg ที่จำลองด้วยค่าชุดเดียวกันเท่านั้น:
        r = eg_test(y, x);  null = mc_null_eg(r["n_obs"], r["n_vars"], lags=r["lags"])
    (ค่าวิกฤตเปลี่ยนตามจำนวนแท่ง จำนวนสินทรัพย์ และ lags — ใช้ null ผิดชุด = ระดับนัยสำคัญผิด)
    adf เป็น NaN เมื่อทดสอบไม่ได้: ข้อมูลสั้นเกินไป หรือ y เขียนได้จาก X เป๊ะ (r2 = 1 เช่น ส่งสินทรัพย์
    เดียวกันมาสองคอลัมน์ — ส่วนเหลือเป็นแค่เศษปัดเลข ไม่ใช่สเปรด)"""
    r = ols(y, X, const=True)
    perfect = r["r2"] >= 1.0
    return {
        "alpha": float(r["coef"][0]),
        "beta": np.asarray(r["coef"][1:], float),
        "resid": r["resid"],
        "adf": math.nan if perfect else adf_stat(r["resid"], lags=lags, const=False),
        "r2": r["r2"],
        "n_obs": int(len(r["resid"])),
        "n_vars": int(len(r["coef"])),      # y หนึ่งตัว + จำนวนตัวแปรใน X
        "lags": int(lags),
    }


def fit_ar1(x):
    """ประมาณ AR(1): x_t = c + φ·x_{t−1} + e_t → φ, μ, σ_eq, half-life
      |φ| < 1 (รวม φ ≤ 0 เช่น white noise): นิ่ง → μ = c/(1−φ), σ_eq = sd_e/√(1−φ²)
      |φ| ≥ 1: ไม่นิ่ง → σ_eq = inf, half-life = inf (μ คืนเป็นค่าเฉลี่ยตัวอย่าง)
      ประมาณไม่ได้ (สั้นเกินไป · มี NaN/inf · อนุกรมคงที่) → ทุกค่าเป็น NaN

    ข้อควรระวังเวลาอ่านผล (วัดจากการจำลองแล้ว)
      • φ ที่ประมาณจากข้อมูลจำกัดเอนเอียงต่ำ จึงมักได้ half-life สั้นกว่าจริง
      • random walk แท้ ๆ ก็ให้ half-life เป็นเลขจำกัดเกือบทุกครั้ง (ราว 96% · ค่ากลางราว 0.15 × จำนวนแท่ง)
        — ตัวเลข half-life มีความหมายหลังผ่านการทดสอบ ADF/Engle-Granger แล้วเท่านั้น
      • σ_eq ก็เอนเอียงต่ำ: ราว −9% เมื่อมี 250 แท่ง และราว −14% เมื่อประมาณจากส่วนเหลือของ
        Engle-Granger 250 แท่ง (half-life จริง 12) → z ที่วัดด้วย σ นี้จะดูใหญ่เกินจริงนอกตัวอย่าง"""
    x = np.asarray(x, float)
    try:
        r = ols(x[1:], x[:-1], const=True)
    except ValueError:      # "ประมาณไม่ได้" ต้องไม่ถูกอ่านว่า "ไม่ดึงกลับ"
        return dict.fromkeys(("c", "phi", "sd_e", "mu", "sigma_eq", "half_life", "t_phi_minus_1"), math.nan)
    c, phi = float(r["coef"][0]), float(r["coef"][1])
    sd_e = math.sqrt(r["s2"])
    if abs(phi) < 1.0:
        mu = c / (1.0 - phi)
        sigma_eq = sd_e / math.sqrt(1.0 - phi * phi)
    else:
        mu, sigma_eq = float(np.mean(x)), math.inf
    se_phi = float(r["se"][1])
    return {"c": c, "phi": phi, "sd_e": sd_e, "mu": mu, "sigma_eq": sigma_eq,
            "half_life": half_life_from_phi(phi),
            "t_phi_minus_1": (phi - 1.0) / se_phi if se_phi > 0 else math.nan}


def variance_ratio(x, q):
    """Var(x_{t+q} − x_t) / (q · Var(x_{t+1} − x_t))   — สูตรไม่เอนเอียงของ Lo-MacKinlay (1988)
    ≈ 1 = random walk · < 1 = ดึงกลับ · > 1 = วิ่งเป็นเทรนด์
    ห้ามตัดสินด้วยตาเทียบกับ 1: random walk แท้ ๆ ก็ให้ค่าแกว่งกว้าง (ช่วง 5–95% ราว 0.76–1.28
    เมื่อ n = 1000, q = 20 และกว้างถึงราว 0.3–2.3 เมื่อ n = 250, q = 60) — ต้องเทียบกับแถบที่ได้จาก
    การจำลอง random walk ที่ n และ q เดียวกัน
    q ต้องเป็นจำนวนเต็ม ≥ 1 · ถ้าข้อมูลสั้นเกินไปสำหรับ q นี้ (q ≥ จำนวนแท่ง − 1) หรืออนุกรมคงที่ → NaN"""
    x = np.asarray(x, float)
    q = int(q)
    if q < 1:
        raise ValueError("variance_ratio: q ต้องเป็นจำนวนเต็ม ≥ 1")
    d1 = np.diff(x)
    T = len(d1)
    if q >= T:
        return math.nan
    mu = d1.mean()                              # ค่าเฉลี่ยต่อแท่ง (drift) — หักออกจากผลต่าง q แท่งด้วย q·mu
    var1 = float(d1.var(ddof=1))
    if not var1 > 0:
        return math.nan
    dq = x[q:] - x[:-q]
    m = q * (T - q + 1) * (1.0 - q / T)         # ตัวหารที่ชดเชยการใช้ช่วงซ้อนทับกัน
    return float(((dq - q * mu) ** 2).sum() / m / var1)


# ───────────────────────── z-score (ไม่มองอนาคต) ─────────────────────────

def rolling_mean_std(s, window):
    """ค่าเฉลี่ยและ sd (ddof=1) ของ `window` แท่งล่าสุด "รวมแท่ง t" · t < window−1 ให้ NaN
    คิดทีละหน้าต่างตรง ๆ จึงแม่นแม้ระดับราคาสูง · NaN หรือราคาผิดหนึ่งจุดกระทบเฉพาะหน้าต่างที่มีจุดนั้น
    (window แท่ง) แล้วกลับมาปกติเอง · window = 1 → sd เป็น NaN ทั้งเส้น (หา sd จากจุดเดียวไม่ได้)"""
    s = np.asarray(s, float)
    window = int(window)
    if window < 1:
        raise ValueError("rolling_mean_std: window ต้อง ≥ 1")
    n = len(s)
    mean = np.full(n, np.nan)
    std = np.full(n, np.nan)
    if n < window:
        return mean, std
    w = sliding_window_view(s, window)          # w[i] = s[i : i+window] (เป็นมุมมอง ไม่คัดลอกข้อมูล)
    step = max(1, 4_000_000 // window)          # ทำทีละก้อน กันหน่วยความจำบวมเมื่อข้อมูลยาวมาก
    for i in range(0, len(w), step):
        blk = w[i:i + step]
        j = window - 1 + i
        mean[j:j + len(blk)] = blk.mean(axis=1)
        if window > 1:
            std[j:j + len(blk)] = blk.std(axis=1, ddof=1)
    return mean, std


def zscore_rolling(s, window, include_current=True):
    """z ของแท่ง t เทียบกับค่าเฉลี่ย/sd ของหน้าต่างเลื่อน — ไม่ใช้ข้อมูลหลังแท่ง t
      include_current=True  (ค่าตั้งต้น): หน้าต่าง `window` แท่งที่จบที่แท่ง t (รวมแท่ง t เอง)
      include_current=False : หน้าต่าง `window` แท่งที่จบที่แท่ง t−1 (แท่ง t ไม่อยู่ในไม้บรรทัดของตัวเอง)

    ข้อจำกัดของแบบรวมแท่ง t: เพราะแท่ง t ดึงค่าเฉลี่ยและ sd เข้าหาตัวเอง |z| จึงมีเพดานทางคณิตศาสตร์
    |z| ≤ (window−1)/√window  (window 5 → 1.79 · 6 → 2.04 · 12 → 3.18) — หน้าต่างสั้นกว่าราว 10 แท่ง
    แทบไม่มีทางถึง ±2 เลย: "หน้าต่างสั้นแล้วไม่มีไม้" จึงเป็นผลของเพดานนี้ ไม่ใช่ของตลาด
    ถ้าจะทดลองหน้าต่างสั้น ให้ใช้ include_current=False หรือรายงานเพดานคู่กับผล"""
    mean, std = rolling_mean_std(s, window)
    if not include_current:
        mean = np.concatenate([[np.nan], mean[:-1]])
        std = np.concatenate([[np.nan], std[:-1]])
    with np.errstate(invalid="ignore", divide="ignore"):
        z = (np.asarray(s, float) - mean) / std
    z[~np.isfinite(z)] = np.nan
    return z


def zscore_fixed(s, mu, sd):
    """z เทียบกับ μ, σ ที่กำหนดตายตัว (เช่น ประมาณจากช่วง train แล้วใช้กับช่วง test)"""
    return (np.asarray(s, float) - mu) / sd


# ───────────────────────── กฎเข้า-ออก ─────────────────────────

def band_positions(z, entry=2.0, exit=0.0, stop=None, max_hold=None):
    """กฎแถบ: คืน pos[t] ∈ {−1, 0, +1} ที่ตัดสินใจตอนสิ้นแท่ง t
      ว่างอยู่ + z ≤ −entry → long สเปรด (+1)   · ว่างอยู่ + z ≥ +entry → short สเปรด (−1)
      ถือ long  ออกเมื่อ z ≥ −exit               · ถือ short ออกเมื่อ z ≤ +exit
      (exit=0 = ออกที่ค่าเฉลี่ย · exit=0.5 = ออกก่อนถึงค่าเฉลี่ย · exit=−entry = รอถึงแถบฝั่งตรงข้าม)
      stop:  ออกเมื่อ |z| ≥ stop แล้วพักจนกว่า |z| < entry จึงเข้าใหม่ได้
      max_hold: ออกเมื่อถือครบจำนวนแท่งนี้ แล้วพักจนกว่า |z| < entry เช่นกัน
      z เป็น NaN → ว่าง

    รายละเอียดที่โค้ดทำจริง (ควรรู้ก่อนอ่านผล)
      • ไม่เปิดสถานะใหม่บนแท่งที่ |z| ≥ stop — แต่ถ้าตอนนั้น "ว่างอยู่แล้ว" จะไม่ถูกสั่งพัก
        จึงเข้าได้ทันทีที่ z ถอยกลับมาอยู่ระหว่าง entry กับ stop (ต่างจากสถานะที่โดน stop ซึ่งต้องพัก)
      • z เป็น NaN ล้างทุกอย่าง รวมทั้งการพักหลัง stop
      • ออกตามปกติแล้วแท่งเดียวกันเข้าฝั่งตรงข้ามได้เลย → exit=−entry คือ "กลับข้างทันที"
        (อยู่ในตลาดเกือบตลอดเวลา)
      • exit = entry แปลว่าถือเฉพาะตอนที่ z อยู่นอกแถบ
    ค่าที่ไม่มีความหมายจะหยุดด้วย ValueError: exit > entry (ออกแล้วเข้าใหม่ทุกแท่ง max_hold ไม่ทำงาน)
    และ stop ≤ entry (ไม่มีวันได้เปิดสถานะ)"""
    if exit > entry:
        raise ValueError(f"band_positions: exit ({exit}) ต้องไม่เกิน entry ({entry})")
    if stop is not None and stop <= entry:
        raise ValueError(f"band_positions: stop ({stop}) ต้องมากกว่า entry ({entry}) ไม่เช่นนั้นจะไม่มีไม้เลย")
    z = np.asarray(z, float)
    pos = np.zeros(len(z))
    cur, held, locked = 0, 0, False
    for t in range(len(z)):
        zt = z[t]
        if not np.isfinite(zt):
            cur, held, locked = 0, 0, False
            pos[t] = 0
            continue
        if locked and abs(zt) < entry:
            locked = False
        if cur != 0:
            held += 1
            done = (cur == 1 and zt >= -exit) or (cur == -1 and zt <= exit)
            cut = (stop is not None and abs(zt) >= stop) or (max_hold is not None and held >= max_hold)
            if done:
                cur, held = 0, 0
            elif cut:
                cur, held, locked = 0, 0, True
        if cur == 0 and not locked:
            if zt <= -entry and not (stop is not None and abs(zt) >= stop):
                cur, held = 1, 0
            elif zt >= entry and not (stop is not None and abs(zt) >= stop):
                cur, held = -1, 0
        pos[t] = cur
    return pos


# ───────────────────────── backtest ─────────────────────────

def spread_pnl(y, x, beta, pos, cost_per_leg=0.0, lag=1):
    """ผลตอบแทนรายแท่งของการเทรดสเปรด ต่อเงินรวมสองขา 1 หน่วย
    y, x = log price · beta = ค่าเดียวหรืออนุกรม (ค่าที่รู้ตอนสิ้นแท่ง t)
    pos[t] = สถานะที่ตัดสินใจตอนสิ้นแท่ง t
    lag=1 (มาตรฐาน): สถานะของแท่ง t รับผลของแท่ง t+1 — เท่ากับสมมติว่าซื้อขายได้ที่ราคาปิดของ
                     แท่งที่ให้สัญญาณพอดี (มองโลกแง่ดีเล็กน้อย)
    lag=2 (เข้มกว่า): ได้ราคาช้าไปหนึ่งแท่ง — ควรรายงานคู่กับ lag=1 เมื่ออ้าง Sharpe
    lag=0 (บั๊ก): ให้สถานะที่ตัดสินใจจากราคาปิดแท่ง t รับผลของแท่ง t เอง
    คืน (pnl, info) โดย info มี held, turnover, n_trades, open_at_end

    ต้นทุน = c × |สถานะที่เปลี่ยน| ลงบัญชีในแท่งแรกที่สถานะใหม่มีผล · กลับข้าง = 2c ในแท่งเดียว
    ถ้า beta เปลี่ยนระหว่างถือ (เช่น จาก walk-forward) สัดส่วนสองขาถูกปรับตาม beta ใหม่ "ฟรี"
    (ไม่คิดค่าปรับสัดส่วน) · ไม้ที่ยังเปิดอยู่ ณ แท่งสุดท้ายถูกตีมูลค่าที่ราคาปิดสุดท้ายและยังไม่จ่ายค่าออก
    → info["open_at_end"] = True และไม้นั้นถูกนับใน n_trades ทั้งที่ยังไม่จบ
    y, x, beta, pos มี NaN/inf หรือ lag < 0 → ValueError"""
    y = np.asarray(y, float)
    x = np.asarray(x, float)
    n = len(y)
    b = np.broadcast_to(np.asarray(beta, float), (n,)).copy()
    pos = np.asarray(pos, float)
    lag = int(lag)
    if lag < 0:
        raise ValueError("spread_pnl: lag ต้อง ≥ 0 (lag ติดลบ = ใช้สถานะจากอนาคต)")
    _check_finite("spread_pnl", y=y, x=x, beta=b, pos=pos)
    dy = np.diff(y, prepend=y[0])
    dx = np.diff(x, prepend=x[0])
    held = np.zeros(n)
    b_held = b.copy()
    if lag > 0:
        held[lag:] = pos[:-lag]
        b_held[lag:] = b[:-lag]
    else:
        held = pos.copy()
    gross = held * (dy - b_held * dx) / (1.0 + np.abs(b_held))
    turnover = np.abs(np.diff(held, prepend=0.0))
    pnl = gross - cost_per_leg * turnover
    return pnl, {"held": held, "turnover": turnover, "n_trades": count_trades(held),
                 "open_at_end": bool(n and held[-1] != 0)}


def count_trades(held):
    """จำนวนครั้งที่ "เปิดสถานะใหม่" (จากว่างหรือจากฝั่งตรงข้าม)"""
    held = np.asarray(held, float)
    prev = np.concatenate([[0.0], held[:-1]])
    return int(np.sum((held != 0) & (held != prev)))


def trade_pnls(held, pnl, cost_per_leg=0.0):
    """ผลตอบแทนรวมของแต่ละไม้ (ตั้งแต่เปิดจนปิด) — ใช้นับอัตราชนะและกำไรเฉลี่ยต่อไม้
    ต้นทุนตอนปิดสถานะตกอยู่ในแท่งถัดไป จึงรวมแท่งที่ปิดเข้าไปในไม้นั้นด้วย
    กรณี "กลับข้างทันที" (+1 → −1 โดยไม่มีแท่งว่าง): ต้นทุน 2c ของแท่งนั้นเป็นค่าปิดไม้เก่า c + ค่าเปิด
    ไม้ใหม่ c · ถ้าส่ง cost_per_leg = c มาด้วย ค่าปิดจะถูกคืนให้ไม้เก่า (แต่ละไม้จ่าย 2c ของตัวเอง)
    ถ้าไม่ส่ง (ค่าตั้งต้น 0) ทั้ง 2c จะไปอยู่กับไม้ใหม่ — ผลรวมทุกไม้เท่ากันทั้งสองแบบ
    ไม้ที่ยังเปิดค้างตอนข้อมูลจบถูกนับเป็นไม้สุดท้ายด้วย (ยังไม่ได้จ่ายค่าออก)"""
    held = np.asarray(held, float)
    pnl = np.asarray(pnl, float)
    out, acc, cur = [], 0.0, 0.0
    for t in range(len(held)):
        if held[t] != cur:
            if cur != 0:
                if held[t] == 0:
                    acc += pnl[t]
                    out.append(acc)
                    acc = 0.0
                else:
                    close_cost = cost_per_leg * abs(cur)
                    out.append(acc - close_cost)
                    acc = pnl[t] + close_cost
            else:
                acc = pnl[t]
            cur = held[t]
        elif cur != 0:
            acc += pnl[t]
    if cur != 0:
        out.append(acc)
    return np.array(out)


def perf_stats(pnl, held=None, cost_per_leg=0.0):
    """สรุปผล: ผลตอบแทนต่อปี · ความผันผวนต่อปี · Sharpe · drawdown ลึกสุด (คิดแบบบวกสะสม ไม่ทบต้น)
    ถ้าส่ง held มาด้วย จะได้ n_trades, hit_rate (ไม้ที่กำไร > 0 · ไม้ที่ได้ 0 พอดีนับเป็นไม่ชนะ),
    avg_trade, time_in_market, open_at_end (ไม้สุดท้ายยังไม่ปิด) · cost_per_leg ใช้แบ่งต้นทุนของแท่งที่
    กลับข้างให้ถูกไม้ (ดู trade_pnls)
    pnl มี NaN → Sharpe เป็น NaN ("ไม่รู้" ไม่ใช่ 0) · ไม่มีแท่งเลย → ทุกค่าเป็น 0"""
    pnl = np.asarray(pnl, float)
    n = len(pnl)
    mean = float(pnl.mean()) if n else 0.0
    sd = float(pnl.std(ddof=1)) if n > 1 else 0.0
    if math.isnan(mean) or math.isnan(sd):
        sharpe = math.nan
    else:
        sharpe = (mean / sd) * math.sqrt(DAYS_PER_YEAR) if sd > 0 else 0.0
    eq = np.cumsum(pnl)
    peak = np.maximum.accumulate(np.concatenate([[0.0], eq]))[1:]
    out = {
        "ann_return": mean * DAYS_PER_YEAR,
        "ann_vol": sd * math.sqrt(DAYS_PER_YEAR),
        "sharpe": sharpe,
        "total": float(eq[-1]) if n else 0.0,
        "max_dd": float(np.max(peak - eq)) if n else 0.0,
    }
    if held is not None:
        held = np.asarray(held, float)
        tp = trade_pnls(held, pnl, cost_per_leg=cost_per_leg)
        out["n_trades"] = int(len(tp))
        out["hit_rate"] = float(np.mean(tp > 0)) if len(tp) else 0.0
        out["avg_trade"] = float(tp.mean()) if len(tp) else 0.0
        out["time_in_market"] = float(np.mean(held != 0)) if len(held) else 0.0
        out["open_at_end"] = bool(len(held) and held[-1] != 0)
    return out


def walk_forward_pair(y, x, train=250, refit=21, entry=2.0, exit=0.0, stop=None,
                      max_hold=None, cost_per_leg=0.0, lag=1):
    """backtest คู่แบบเดินหน้า (walk-forward) — ไม่มีพารามิเตอร์ตัวไหนเห็นอนาคต
    ทุก `refit` แท่ง: ประมาณ α, β (OLS) และ μ, σ ของ ε จาก `train` แท่งล่าสุดที่จบ ณ แท่งก่อนหน้า
    แล้วใช้ค่าชุดนั้นคำนวณ z ของ `refit` แท่งถัดไป
    คืน dict: pnl, held, pos, z, beta (อนุกรม), eps (สเปรดตามพารามิเตอร์ ณ ขณะนั้น), stats
      pos[t] = สถานะที่ตัดสินใจตอนสิ้นแท่ง t (อยู่บนแกนเวลาเดียวกับ z) · held[t] = pos[t−lag]
      stats = perf_stats ของช่วงหลัง train + z_sd (sd ของ z ที่เกิดขึ้นจริงในช่วงทดสอบ)

    สิ่งที่ต้องรู้เวลาอ่านผล (วัดจากการจำลองแล้ว)
      • z ที่นี่ "ไม่ใช่" หน่วยของ σ จริง: σ ที่ประมาณจากหน้าต่าง train ต่ำกว่าสิ่งที่จะเกิดถัดไป
        และเส้นกลางที่ประมาณได้ก็เยื้องจากของจริง → นอกตัวอย่าง sd ของ z ≈ 1.25 เมื่อ train=250
        (1.85 เมื่อ train=60 · 1.13 เมื่อ train=500) ไม่ใช่ 1 · "entry=2" จึงเป็น "2 เท่าของ σ ที่ประมาณจาก
        หน้าต่าง" ซึ่งเท่ากับราว 1.5 σ จริง — อย่าเทียบเกณฑ์ของ walk-forward กับสูตรที่คิดจาก σ จริง
        ตรง ๆ (ดู stats["z_sd"])
      • eps และ z "กระโดด" ทุกครั้งที่ประมาณใหม่ (α, β, μ, σ ชุดใหม่) — กำไรขาดทุนคิดจากราคาจริง
        จึงไม่มีกำไรปลอมจากการกระโดดนี้
      • สถานะที่ถือค้างข้ามรอบประมาณใหม่ถูกปรับสัดส่วนตาม β ใหม่โดยไม่คิดต้นทุน — ต้นทุนที่หายไป
        น้อยมาก (ไม่ถึง 4 bps ต่อปีในคู่ตัวอย่างทั้งสี่) แต่ "นโยบาย" นี้มีผลบนเส้นทางเดียว: คู่ break ตัวอย่าง
        ผลรวมกลับเครื่องหมายเมื่อเทียบกับการตรึง β ตั้งแต่เข้า ขณะที่ค่าเฉลี่ยหลายร้อยโลกเท่ากัน
        → ข้อสรุปทั่วไปให้ดูค่าเฉลี่ยจาก Monte Carlo ไม่ใช่เครื่องหมายของผลรวมบนคู่ตัวอย่างคู่เดียว
    y, x มี NaN/inf หรือข้อมูลไม่ยาวกว่า train → ValueError (ไม่มีช่วงทดสอบ)"""
    y = np.asarray(y, float)
    x = np.asarray(x, float)
    n = len(y)
    if len(x) != n:
        raise ValueError(f"walk_forward_pair: y มี {n} แท่ง แต่ x มี {len(x)} แท่ง")
    _check_finite("walk_forward_pair", y=y, x=x)
    if n <= train:
        raise ValueError(f"walk_forward_pair: มีข้อมูล {n} แท่ง แต่ train = {train} — ต้องยาวกว่า train "
                         "จึงจะเหลือช่วงทดสอบ")
    z = np.full(n, np.nan)
    beta = np.full(n, np.nan)
    eps = np.full(n, np.nan)
    for start in range(train, n, refit):
        sl = slice(start - train, start)
        r = ols(y[sl], x[sl], const=True)
        a, b = float(r["coef"][0]), float(r["coef"][1])
        mu, sd = float(r["resid"].mean()), float(r["resid"].std(ddof=1))
        blk = slice(start, min(start + refit, n))
        e = y[blk] - a - b * x[blk]
        eps[blk] = e
        beta[blk] = b
        z[blk] = (e - mu) / sd if sd > 0 else np.nan
    pos = band_positions(z, entry=entry, exit=exit, stop=stop, max_hold=max_hold)
    b_use = np.where(np.isfinite(beta), beta, 0.0)
    pnl, info = spread_pnl(y, x, b_use, pos, cost_per_leg=cost_per_leg, lag=lag)
    pnl[:train] = 0.0
    stats = perf_stats(pnl[train:], info["held"][train:], cost_per_leg=cost_per_leg)
    z_test = z[train:][np.isfinite(z[train:])]
    stats["z_sd"] = float(z_test.std()) if len(z_test) > 1 else math.nan
    return {"pnl": pnl, "held": info["held"], "pos": pos, "z": z, "beta": beta, "eps": eps,
            "stats": stats}


def portfolio_pnl(weights, returns, cost_per_leg=0.0, lag=1):
    """ผลตอบแทนรายแท่งของพอร์ตหลายสินทรัพย์
    weights[t, i] = น้ำหนัก (สัดส่วนของทุน มีเครื่องหมาย) ที่ตัดสินใจตอนสิ้นแท่ง t
    returns[t, i] = ผลตอบแทนของสินทรัพย์ i ในแท่ง t
    น้ำหนักของแท่ง t รับผลของแท่ง t+lag · ต้นทุน = c × ผลรวม |น้ำหนักที่เปลี่ยน|
    คืน (pnl, turnover) · ส่งอาร์เรย์มิติเดียวได้ (= สินทรัพย์ตัวเดียว)

    turnover วัดจาก "น้ำหนักเป้าหมาย" ที่เปลี่ยนเท่านั้น: การซื้อขายเพื่อดึงน้ำหนักกลับเมื่อราคาไหล
    และการล้างพอร์ตตอนข้อมูลจบ "ไม่ถูกคิดต้นทุน" — พอร์ตที่น้ำหนักเปลี่ยนช้าจะดูถูกกว่าจริงเล็กน้อย
    weights/returns มี NaN/inf (เช่น สินทรัพย์ที่ยังไม่เข้าตลาด — ให้เติม 0) หรือ lag < 0 → ValueError"""
    w = np.asarray(weights, float)
    r = np.asarray(returns, float)
    if w.ndim == 1:
        w = w[:, None]
    if r.ndim == 1:
        r = r[:, None]
    lag = int(lag)
    if lag < 0:
        raise ValueError("portfolio_pnl: lag ต้อง ≥ 0 (lag ติดลบ = ใช้น้ำหนักจากอนาคต)")
    _check_finite("portfolio_pnl", weights=w, returns=r)
    held = np.zeros_like(w)
    if lag > 0:
        held[lag:] = w[:-lag]
    else:
        held = w.copy()
    turnover = np.abs(np.diff(held, axis=0, prepend=np.zeros((1, w.shape[1])))).sum(axis=1)
    return (held * r).sum(axis=1) - cost_per_leg * turnover, turnover


# ───────────────────────── ตัวช่วยปัดเลขสำหรับ figures.json ─────────────────────────

def rd(v, d=2):
    """ปัดทศนิยมเพื่อเก็บลง figures.json — ค่าที่เก็บคือค่าที่จะปรากฏในบทตรงตัว
    NaN/inf → None · ไม่คืน "−0.0" (ค่าติดลบที่ปัดแล้วเป็นศูนย์จะได้ 0.0)
    ข้อจำกัด: เป็นเลขทศนิยมธรรมดา จึงไม่เก็บศูนย์ท้าย (3.10 → 3.1) และเลขที่ลงท้ายครึ่งพอดีถูกปัดตาม
    ค่าฐานสองจริง (1.005 → 1.0 · 2.5 → 2) — ถ้าต้องการจำนวนทศนิยมตายตัวให้จัดรูปตอนพิมพ์"""
    v = float(v)
    if not math.isfinite(v):
        return None
    out = round(v, d) + 0.0
    return int(out) if d == 0 else out


def pct(v, d=1):
    """สัดส่วน → เปอร์เซ็นต์ที่ปัดแล้ว (0.0312 → 3.1)"""
    return rd(100.0 * float(v), d)


def bps(v, d=1):
    """สัดส่วน → basis point ที่ปัดแล้ว (0.0005 → 5.0)"""
    return rd(10000.0 * float(v), d)


# ───────────────────────── ทดสอบตัวเอง ─────────────────────────

def _raises(fn, exc=ValueError):
    """True ถ้าเรียก fn แล้วเกิด error ชนิดที่คาดไว้"""
    try:
        fn()
    except exc:
        return True
    return False


def _all_nan(d):
    return all(isinstance(v, float) and math.isnan(v) for v in d.values())


def _test_estimators(y, x):
    """half-life / AR(1) · variance ratio · TLS · OLS · p-value · rd"""
    nan = math.nan

    # φ ≤ 0 คือดึงกลับเร็วที่สุด (ไม่ใช่ inf) · |φ| ≥ 1 = inf · NaN = NaN
    assert half_life_from_phi(0.0) == 0.0 and half_life_from_phi(-0.3) == 0.0
    assert half_life_from_phi(1.0) == math.inf and half_life_from_phi(1.2) == math.inf
    assert half_life_from_phi(-1.0) == math.inf and math.isnan(half_life_from_phi(nan))
    assert abs(half_life_from_phi(phi_from_half_life(12.0)) - 12.0) < 1e-9
    # white noise (sd 0.5): ต้องได้ σ_eq ≈ 0.5 ทุกโลก ไม่ใช่ inf ในครึ่งหนึ่งของโลก
    fits = [fit_ar1(row) for row in 0.5 * rng(21).standard_normal((300, 200))]
    assert all(math.isfinite(f["sigma_eq"]) and math.isfinite(f["half_life"]) for f in fits)
    assert min(f["phi"] for f in fits) < 0 < max(f["phi"] for f in fits)
    assert abs(float(np.median([f["sigma_eq"] for f in fits])) - 0.5) < 0.02
    # AR(1) ที่ φ = −0.5: นิ่ง · σ_eq จริง = 1/√0.75 = 1.1547
    e = rng(22).standard_normal(5000)
    osc = np.zeros(5000)
    for t in range(1, 5000):
        osc[t] = -0.5 * osc[t - 1] + e[t]
    f = fit_ar1(osc)
    assert abs(f["phi"] + 0.5) < 0.05 and abs(f["sigma_eq"] - 1.1547) < 0.05 and f["half_life"] == 0.0
    # ระเบิดออก (φ > 1) → inf · ประมาณไม่ได้ (คงที่ / มี NaN / สั้นเกิน) → NaN ทุกค่า ไม่ใช่ inf
    f = fit_ar1(1.05 ** np.arange(60))
    assert f["phi"] > 1 and f["sigma_eq"] == math.inf and f["half_life"] == math.inf
    bad = osc.copy()
    bad[50] = nan
    assert _all_nan(fit_ar1(np.full(100, 3.3))) and _all_nan(fit_ar1(bad)) and _all_nan(fit_ar1(osc[:3]))

    # variance ratio แบบไม่เอนเอียง: random walk ต้องเฉลี่ย ≈ 1 แม้ q ใหญ่เทียบกับ n (สูตรเดิมได้ ~0.72)
    w = np.cumsum(rng(23).standard_normal((400, 250)), axis=1)
    vr_rw = float(np.mean([variance_ratio(row, 60) for row in w]))
    assert 0.9 < vr_rw < 1.1, vr_rw
    assert abs(variance_ratio(w[0], 1) - 1.0) < 1e-12
    vr_mr = float(np.median([variance_ratio(row, 20) for row in ar1_batch(200, 1000, 8.0, 0.03, rng(24))]))
    assert 0.4 < vr_mr < 0.6, vr_mr
    assert math.isnan(variance_ratio(w[0][:10], 9)) and math.isnan(variance_ratio(np.ones(50), 5))
    assert _raises(lambda: variance_ratio(w[0], 0))

    # TLS: สลับ y, x ได้ β กลับเศษส่วน · อยู่ระหว่าง OLS สองทิศ · กรณีสุดขอบไม่คืน NaN มั่ว ๆ
    a1, b1 = tls_beta(y, x)
    a2, b2 = tls_beta(x, y)
    b_yx = float(ols(y, x)["coef"][1])
    b_xy = 1.0 / float(ols(x, y)["coef"][1])
    assert abs(b1 * b2 - 1.0) < 1e-9 and b_yx < b1 < b_xy, (b_yx, b1, b_xy)
    assert tls_beta([-0.5, -0.5, 0.5, 0.5], [-1.0, 1.0, -1.0, 1.0]) == (0.0, 0.0)
    assert tls_beta([-1.0, 1.0, -1.0, 1.0], [-0.5, -0.5, 0.5, 0.5])[1] == math.inf
    assert tls_beta(np.arange(5.0), np.ones(5))[1] == math.inf

    # OLS: ข้อมูลใช้ไม่ได้ต้องหยุดพร้อมข้อความ ไม่ใช่คืนเลขมั่ว
    assert _raises(lambda: ols([1.0, 2.0], [1.0, 3.0]))                 # 2 แถว 2 สัมประสิทธิ์
    assert _raises(lambda: ols(bad[:100], osc[:100]))                   # NaN
    assert _raises(lambda: ols(y, np.full(len(y), 3.3)))                # ตัวแปรอธิบายคงที่
    assert _raises(lambda: ols(y, np.column_stack([x, x])))             # ตัวแปรอธิบายซ้ำกัน
    assert _raises(lambda: ols(y, x[:-1]))                              # ความยาวไม่เท่ากัน
    # ค่าคงที่และ se ของค่าคงที่ต้องตรงกับสูตรตำราแบบไม่ลบค่าเฉลี่ย
    r = ols(y, x)
    X1 = np.column_stack([np.ones(len(y)), x])
    xtx = X1.T @ X1
    coef = np.linalg.solve(xtx, X1.T @ y)
    se = np.sqrt(r["s2"] * np.diag(np.linalg.inv(xtx)))
    assert np.allclose(r["coef"], coef, rtol=1e-8) and np.allclose(r["se"], se, rtol=1e-6)
    # เลื่อนระดับราคา (เช่น +10 ล้าน) ต้องไม่เปลี่ยน β และค่า ADF
    r0, r1 = eg_test(y, x), eg_test(y + 1e7, x + 1e7)
    assert abs(r0["beta"][0] - r1["beta"][0]) < 1e-6 and abs(r0["adf"] - r1["adf"]) < 1e-3, (r0["adf"], r1["adf"])
    rb = resid_batch((y + 1e7)[None, :], (x + 1e7)[None, :, None])[0]
    assert np.allclose(rb, r0["resid"], atol=1e-7)
    # r2 ของการถดถอยไม่มีค่าคงที่ = แบบ uncentred อยู่ใน [0, 1] เสมอ
    r_nc = ols(y, x, const=False)
    assert 0.0 <= r_nc["r2"] <= 1.0
    assert abs(r_nc["r2"] - (1.0 - float(r_nc["resid"] @ r_nc["resid"]) / float(y @ y))) < 1e-12
    # eg_test บอกค่าที่ต้องใช้จำลอง null ชุดที่ตรงกัน
    assert (r0["n_obs"], r0["n_vars"], r0["lags"]) == (len(y), 2, 1)
    assert math.isnan(eg_test(y[:3], x[:3])["adf"])
    assert math.isnan(eg_test(2.0 + x, x)["adf"])                       # y = x + ค่าคงที่: ไม่มีสเปรดให้ทดสอบ

    # p-value: NaN → NaN · ไม่ต้องเรียงมาก่อน · ตรงกับ quantile
    null = np.sort(rng(25).standard_normal(4000))
    assert math.isnan(p_value(nan, null)) and p_value(-99.0, null) == 0.0 and p_value(99.0, null) == 1.0
    q05 = float(np.quantile(null, 0.05))
    assert abs(p_value(q05, null) - 0.05) < 1e-3
    assert p_value(q05, rng(26).permutation(null)) == p_value(q05, null)

    # rd: ไม่มี "−0.0" · NaN/inf → None
    assert str(rd(-0.0004, 2)) == "0.0" and str(rd(-0.4, 0)) == "0" and rd(1.234, 2) == 1.23
    assert rd(nan) is None and rd(math.inf) is None and pct(0.0312) == 3.1 and bps(0.0005) == 5.0


def _test_adf(g):
    """adf_stat กับ adf_stat_batch ต้องให้ค่าเดียวกัน และรับมือข้อมูลเสียได้เหมือนกัน"""
    w = np.cumsum(g.standard_normal((7, 300)), axis=1)
    w[1] += 1e5                                         # ระดับสูง ๆ ก็ต้องตรงกัน
    w[2] = ar1(300, 8.0, 1.0, g)
    for const in (True, False):
        for lags in (0, 1, 2):
            one = np.array([adf_stat(w[i], lags=lags, const=const) for i in range(len(w))])
            for chunk in (2000, 3):                     # chunk=3 → ตรวจรอยต่อระหว่างก้อนด้วย
                diff = np.max(np.abs(one - adf_stat_batch(w, lags=lags, const=const, chunk=chunk)))
                assert diff < 1e-10, (const, lags, chunk, diff)
    # ลำดับของพจน์ย้อนหลังถูกต้อง: เทียบกับการสร้างตารางถดถอยทีละแถว (lags=2, มีค่าคงที่)
    xs = w[0]
    dx = np.diff(xs)
    rows = [[xs[t - 1], dx[t - 2], dx[t - 3]] for t in range(3, len(xs))]
    ref = ols(dx[2:], np.array(rows), const=True)["t"][1]
    assert abs(adf_stat(xs, lags=2) - ref) < 1e-9
    # สั้นเกินไป / คงที่ / มี NaN → NaN (ไม่ใช่เลขมั่วหรือ error) และไม่ลามไปเส้นอื่นในชุด
    for n_short in (2, 3, 4, 5, 6):
        assert math.isnan(adf_stat(xs[:n_short], lags=1)), n_short
    assert math.isfinite(adf_stat(xs[:7], lags=1))
    assert math.isnan(adf_stat(np.full(100, 3.3))) and math.isnan(adf_stat(np.arange(100.0)))
    assert np.isnan(adf_stat_batch(w[:, :6])).all()
    wb = w.copy()
    wb[3] = 3.3                                         # ราคาค้าง
    wb[4, 100] = np.nan                                 # ข้อมูลขาด
    wb[5] = np.arange(300.0)                            # เส้นตรงเป๊ะ (Δx คงที่)
    for const in (True, False):
        for lags in (0, 1):
            got = adf_stat_batch(wb, lags=lags, const=const)
            one = np.array([adf_stat(wb[i], lags=lags, const=const) for i in range(len(wb))])
            assert np.isnan(got[[3, 4, 5]]).all() and np.isnan(one[[3, 4, 5]]).all(), (const, lags, got)
            assert np.allclose(got, one, rtol=0, atol=1e-10, equal_nan=True), (const, lags, got, one)
            assert np.isfinite(got[[0, 1, 2, 6]]).all()
    # resid_batch: ระบบที่ตัวแปรอธิบายคงที่ได้ NaN เฉพาะระบบนั้น · ระบบอื่นต้องเท่ากับ ols ทีละระบบ
    Xb = np.stack([w[1], np.full(300, 3.3), w[6]])[:, :, None]
    rb = resid_batch(w[[0, 2, 0]], Xb)
    assert np.isnan(rb[1]).all() and np.isnan(adf_stat_batch(rb, const=False)[1])
    assert np.allclose(rb[0], ols(w[0], w[1])["resid"], atol=1e-9) and np.allclose(rb[2], ols(w[0], w[6])["resid"], atol=1e-9)
    assert _raises(lambda: resid_batch(w[:2], np.stack([w[2], w[2]], axis=1)[None].repeat(2, axis=0)))


def _test_rolling(eps):
    """ค่าเฉลี่ย/sd เลื่อน และ z-score: ถูกต้อง ทนข้อมูลเสีย ไม่มองอนาคต"""
    def brute(s, w):
        m = np.full(len(s), np.nan)
        sd = np.full(len(s), np.nan)
        for t in range(w - 1, len(s)):
            m[t], sd[t] = s[t - w + 1:t + 1].mean(), s[t - w + 1:t + 1].std(ddof=1)
        return m, sd

    s = eps[:600]
    for w in (2, 5, 60):
        m, sd = rolling_mean_std(s, w)
        bm, bs = brute(s, w)
        assert np.allclose(m, bm, rtol=0, atol=1e-12, equal_nan=True)
        assert np.allclose(sd, bs, rtol=1e-10, atol=0, equal_nan=True)
        assert np.isnan(m[:w - 1]).all() and np.isfinite(m[w - 1:]).all()
    # ระดับสูงมาก (1e6) เทียบกับ sd 0.01: สูตรผลรวมสะสมแบบเดิมพังที่นี่
    hi = 1e6 + 0.01 * rng(31).standard_normal(600)
    assert np.nanmax(np.abs(rolling_mean_std(hi, 60)[1] / brute(hi, 60)[1] - 1.0)) < 1e-9
    # NaN หนึ่งจุด หรือราคาผิดหนึ่งจุด กระทบเฉพาะหน้าต่างที่มีจุดนั้น แล้วกลับมาปกติ
    for bad_value in (np.nan, 1e7):
        sb = s.copy()
        sb[300] = bad_value
        mb, sdb = rolling_mean_std(sb, 60)
        m, sd = rolling_mean_std(s, 60)
        assert np.array_equal(sdb[360:], sd[360:]) and np.array_equal(mb[:300], m[:300], equal_nan=True)
        assert np.allclose(sdb[360:], brute(sb, 60)[1][360:], rtol=1e-12, atol=0)
    assert int(np.isfinite(zscore_rolling(np.where(np.arange(600) == 300, np.nan, s), 60)).sum()) == 600 - 59 - 60
    m1, sd1 = rolling_mean_std(s, 1)
    assert np.array_equal(m1, s) and np.isnan(sd1).all() and _raises(lambda: rolling_mean_std(s, 0))
    assert np.isnan(rolling_mean_std(s[:5], 60)[0]).all()
    # เพดาน |z| ≤ (w−1)/√w เมื่อแท่ง t อยู่ในหน้าต่างของตัวเอง · ไม่มีเพดานเมื่อใช้หน้าต่างที่จบที่ t−1
    for w in (3, 5, 6):
        assert np.nanmax(np.abs(zscore_rolling(eps, w))) <= (w - 1) / math.sqrt(w) + 1e-9
    z_in, z_out = zscore_rolling(eps, 5), zscore_rolling(eps, 5, include_current=False)
    assert np.nanmax(np.abs(z_in)) < 2.0 < np.nanmax(np.abs(z_out))
    m5, sd5 = brute(eps, 5)
    assert np.isnan(z_out[:5]).all() and np.allclose(z_out[5:], (eps[5:] - m5[4:-1]) / sd5[4:-1], atol=1e-9)
    # ไม่มองอนาคต: เปลี่ยนข้อมูลหลังแท่ง t แล้ว z ถึงแท่ง t ต้องเท่าเดิมทุกบิต
    for inc in (True, False):
        z_full = zscore_rolling(eps, 60, include_current=inc)
        for t in (59, 60, 100, 500):
            other = eps.copy()
            other[t + 1:] = 5.0 + rng(32).standard_normal(len(eps) - t - 1)
            assert np.array_equal(zscore_rolling(other, 60, include_current=inc)[:t + 1], z_full[:t + 1],
                                  equal_nan=True)


def _test_backtest(y, x, eps):
    """กฎแถบ · บัญชีกำไรขาดทุน · ต้นทุน · สรุปผล"""
    # กฎแถบ: ค่าที่ไม่มีความหมายต้องถูกปฏิเสธ · พฤติกรรมที่เขียนไว้ใน docstring ต้องเป็นจริง
    assert _raises(lambda: band_positions([0.0, 2.5], entry=2.0, stop=2.0))
    assert _raises(lambda: band_positions([0.0, 2.5], entry=2.0, exit=2.5))
    assert band_positions([0, 5, 3.5, 3, 0], stop=4).tolist() == [0, 0, -1, -1, 0]         # ว่างอยู่: ไม่ถูกพัก
    assert band_positions([0, 2.5, 5, 3.5, 3, 0], stop=4).tolist() == [0, -1, 0, 0, 0, 0]  # โดน stop: ต้องพัก
    assert band_positions([0, 2.5, 5, np.nan, 3, 0], stop=4).tolist() == [0, -1, 0, 0, -1, 0]  # NaN ล้างการพัก
    assert band_positions([0, 2.5, -2.5, 2.5], exit=-2.0).tolist() == [0, -1, 1, -1]       # กลับข้างในแท่งเดียว
    assert band_positions([0, -2.5, -2.2, -1.9, 0], entry=2.0, exit=2.0).tolist() == [0, 1, 1, 0, 0]
    assert band_positions([0, -2.5, -2.4, -2.3, -2.2, 0], max_hold=2).tolist() == [0, 1, 1, 0, 0, 0]

    z = zscore_fixed(eps, 0.0, 0.03)
    pos = band_positions(z, entry=1.5, exit=0.0)
    good, info = spread_pnl(y, x, 1.4, pos, lag=1)
    bug, _ = spread_pnl(y, x, 1.4, pos, lag=0)
    # ไม่มีต้นทุน + สเปรดดึงกลับจริง → ต้องกำไร · lag=0 (บั๊ก) ต้องแย่กว่า lag=1
    assert good.sum() > 0 and bug.sum() < good.sum(), (good.sum(), bug.sum())
    # ต้นทุนครบรอบ = 2c ต่อ gross ต่อไม้: turnover ต้องเท่ากับ 2 × จำนวนไม้ (ลบ 1 ถ้าไม้สุดท้ายยังไม่ปิด)
    c = 0.001
    costly, info2 = spread_pnl(y, x, 1.4, pos, cost_per_leg=c, lag=1)
    legs = 2 * info2["n_trades"] - (1 if info2["open_at_end"] else 0)
    assert info2["turnover"].sum() == legs and info2["n_trades"] > 5
    assert abs((good.sum() - costly.sum()) - c * legs) < 1e-12
    tp = trade_pnls(info["held"], good)
    assert abs(tp.sum() - good.sum()) < 1e-9 and len(tp) == info["n_trades"]
    # ไม้ที่ยังเปิดค้างตอนข้อมูลจบ: จ่ายแค่ค่าเข้า c และต้องถูกรายงานว่า open_at_end
    yy = np.array([0.0, 0.0, 0.01, 0.02, 0.03])
    p_open, i_open = spread_pnl(yy, np.zeros(5), 1.0, np.array([0.0, 1, 1, 1, 1]), cost_per_leg=c)
    p_shut, i_shut = spread_pnl(yy, np.zeros(5), 1.0, np.array([0.0, 1, 1, 0, 0]), cost_per_leg=c)
    assert i_open["open_at_end"] and i_open["turnover"].sum() == 1 and i_open["n_trades"] == 1
    assert not i_shut["open_at_end"] and i_shut["turnover"].sum() == 2
    assert perf_stats(p_open, i_open["held"])["open_at_end"] is True
    # ข้อมูลเสียหรือ lag ติดลบต้องหยุด ไม่ใช่คืน NaN/ผลเงียบ ๆ
    y_bad = yy.copy()
    y_bad[2] = np.nan
    assert _raises(lambda: spread_pnl(y_bad, np.zeros(5), 1.0, np.zeros(5)))
    assert _raises(lambda: spread_pnl(yy, np.zeros(5), 1.0, np.zeros(5), lag=-1))
    assert _raises(lambda: portfolio_pnl(np.ones((5, 2)), np.full((5, 2), np.nan)))
    assert _raises(lambda: portfolio_pnl(np.ones((5, 2)), np.zeros((5, 2)), lag=-1))

    # กลับข้างทันที: ถ้าบอก c แต่ละไม้ต้องจ่าย 2c ของตัวเอง · ไม่บอก c ผลรวมก็ยังเท่าเดิม
    held = np.array([0.0, 0, 1, 1, -1, -1, 0])
    gross = np.array([0.0, 0, 0.01, 0.02, 0.015, 0.015, 0])
    net = gross - c * np.abs(np.diff(held, prepend=0.0))
    assert np.allclose(trade_pnls(held, net, cost_per_leg=c), [0.028, 0.028])
    assert np.allclose(trade_pnls(held, net), [0.029, 0.027])
    assert abs(trade_pnls(held, net, cost_per_leg=c).sum() - net.sum()) < 1e-15

    # perf_stats: มี NaN → Sharpe เป็น NaN (ไม่ใช่ 0) · ไม่มีแท่งเลย → 0 ทุกค่าและไม่มี NaN
    assert math.isnan(perf_stats(np.array([0.01, np.nan, 0.02]))["sharpe"])
    empty = perf_stats(np.array([]), np.array([]))
    assert all(v == 0 for v in empty.values()), empty
    ps = perf_stats(np.array([0.01, -0.02, 0.03, 0.0]))
    assert abs(ps["sharpe"] - 0.005 / np.std([0.01, -0.02, 0.03, 0.0], ddof=1) * math.sqrt(252)) < 1e-12
    assert abs(ps["max_dd"] - 0.02) < 1e-15 and abs(ps["total"] - 0.02) < 1e-15

    # portfolio_pnl: น้ำหนักที่เทียบเท่ากับสเปรดต้องให้ผลเท่ากับ spread_pnl · รับอาร์เรย์มิติเดียวได้
    wts = np.column_stack([pos / 2.4, -1.4 * pos / 2.4])
    rets = np.column_stack([np.diff(y, prepend=y[0]), np.diff(x, prepend=x[0])])
    pp, to = portfolio_pnl(wts, rets, cost_per_leg=c)
    assert np.allclose(pp, costly, atol=1e-12) and np.allclose(to, info2["turnover"], atol=1e-12)
    p1, t1 = portfolio_pnl(np.array([0.0, 1, 1]), np.array([0.01, 0.02, 0.03]))
    assert np.allclose(p1, [0, 0, 0.03]) and np.allclose(t1, [0, 0, 1])


def _test_walk_forward(y, x):
    """walk-forward: ผลที่คืน · ข้อมูลเสีย · และการทดสอบสำคัญที่สุด — ห้ามมองอนาคต"""
    wf = walk_forward_pair(y, x, train=250, refit=21, entry=1.5, exit=0.0)
    assert wf["stats"]["total"] > 0
    assert np.isnan(wf["z"][:250]).all() and np.isfinite(wf["z"][250:]).all() and not wf["pnl"][:250].any()
    assert np.array_equal(wf["held"][1:], wf["pos"][:-1]) and wf["held"][0] == 0
    assert 1.0 < wf["stats"]["z_sd"] < 2.0, wf["stats"]["z_sd"]      # ไม่ใช่ 1: σ ในตัวอย่างต่ำกว่าของจริง
    assert isinstance(wf["stats"]["open_at_end"], bool)
    y_bad = y.copy()
    y_bad[700] = np.nan
    assert _raises(lambda: walk_forward_pair(y_bad, x))               # ราคาขาดหนึ่งจุดต้องหยุดพร้อมข้อความ
    assert _raises(lambda: walk_forward_pair(y[:250], x[:250]))       # ไม่มีช่วงทดสอบ

    # เปลี่ยนข้อมูลตั้งแต่แท่ง t0 เป็นต้นไป → ทุกอย่างก่อน t0 ต้องเท่าเดิมทุกบิต
    # (z, β, ε, สถานะที่ตัดสินใจ, กำไรขาดทุน) และสถานะที่ถือต้องเท่าเดิมถึงแท่ง t0+lag−1
    g = rng(41)
    n = len(y)
    for kw in (dict(train=250, refit=21, entry=1.5, lag=1, cost_per_leg=0.0005),
               dict(train=100, refit=1, entry=2.0, exit=0.5, stop=3.5, max_hold=40, lag=2),
               dict(train=120, refit=50, entry=1.0, exit=-1.0, lag=1)):
        base = walk_forward_pair(y, x, **kw)
        tr, rf, lag = kw["train"], kw["refit"], kw["lag"]
        for t0 in (tr, tr + 1, tr + rf - 1, tr + rf, tr + rf + 1, tr + 7 * rf, 777, n - 1):
            y2, x2 = y.copy(), x.copy()
            y2[t0:] += 0.5 + np.cumsum(0.05 * g.standard_normal(n - t0))
            x2[t0:] -= 0.5 + np.cumsum(0.05 * g.standard_normal(n - t0))
            alt = walk_forward_pair(y2, x2, **kw)
            for key in ("z", "beta", "eps", "pos", "pnl"):
                assert np.array_equal(alt[key][:t0], base[key][:t0], equal_nan=True), (kw, t0, key)
            assert np.array_equal(alt["held"][:t0 + lag], base["held"][:t0 + lag]), (kw, t0, "held")
            assert not np.array_equal(alt["z"][t0:], base["z"][t0:])  # การทดสอบนี้ "เห็น" การเปลี่ยนจริง
    return wf


def _selftest():
    g = rng(1)
    n = 1500
    x = random_walk(n, 0.015, g, x0=4.0)
    eps = ar1(n, 12.0, 0.03, g)
    y = 0.3 + 1.4 * x + eps

    r = eg_test(y, x)
    fit = fit_ar1(r["resid"])
    assert abs(r["beta"][0] - 1.4) < 0.05, r["beta"]
    assert 6 < fit["half_life"] < 20, fit["half_life"]

    # batch ต้องให้ผลเท่ากับทีละเส้น (const True/False × lags 0–2) และทนเส้นเสียได้
    _test_adf(g)

    # ค่าวิกฤตที่จำลองเองต้องใกล้ค่าตำรา (−2.86 สำหรับ ADF มีค่าคงที่ · −3.34 สำหรับ EG สองตัวแปร)
    c_adf = crit_values(mc_null_adf(500, n_sim=8000, g=rng(2)))[0.05]
    c_eg = crit_values(mc_null_eg(500, 2, n_sim=8000, g=rng(3)))[0.05]
    assert -3.0 < c_adf < -2.75, c_adf
    assert -3.5 < c_eg < -3.2, c_eg

    _test_estimators(y, x)
    _test_rolling(eps)
    _test_backtest(y, x, eps)
    wf = _test_walk_forward(y, x)

    # คู่ตัวอย่างหลักต้องทำซ้ำได้ทุกครั้ง (ทุกตอนของชุดใช้เส้นเดียวกัน)
    assert np.array_equal(demo_pair("good")["y"], demo_pair("good")["y"]) and len(demo_pair("fake")["x"]) == 1500

    print("sas_core selftest ผ่าน")
    print(f"  β̂ = {r['beta'][0]:.3f} (จริง 1.4) · EG-ADF = {r['adf']:.2f} · half-life ≈ {fit['half_life']:.1f} แท่ง (จริง 12)")
    print(f"  ค่าวิกฤต 5% จากการจำลอง: ADF = {c_adf:.2f} (ตำรา −2.86) · EG สองตัวแปร = {c_eg:.2f} (ตำรา −3.34)")
    print(f"  walk-forward ไม่คิดต้นทุน: Sharpe = {wf['stats']['sharpe']:.2f} · {wf['stats']['n_trades']} ไม้"
          f" · sd ของ z นอกตัวอย่าง = {wf['stats']['z_sd']:.2f}")


if __name__ == "__main__":
    _selftest()
