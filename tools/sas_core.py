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
  • ผลตอบแทนคิดต่อ "เงินรวมสองขา" (gross = 1 + |β|) 1 หน่วย
  • ต้นทุน c = ต้นทุนเที่ยวเดียวต่อขา เป็นสัดส่วนของมูลค่าที่ซื้อขาย (เช่น 5 bps = 0.0005)
    เข้า 1 ครั้งเสีย c ต่อ gross · ครบรอบ (เข้า+ออก) เสีย 2c ต่อ gross

รันไฟล์นี้ตรง ๆ เพื่อทดสอบตัวเอง:
    python3 tools/sas_core.py
"""

import math

import numpy as np

SEED = 20261110
DAYS_PER_YEAR = 252


# ───────────────────────── ตัวสร้างข้อมูลจำลอง ─────────────────────────

def rng(offset=0):
    """ตัวสุ่มที่ทำซ้ำได้ — แต่ละการทดลองใช้ offset ของตัวเอง จะได้ไม่กระทบกัน"""
    return np.random.default_rng(SEED + int(offset))


def phi_from_half_life(half_life):
    """สัมประสิทธิ์ AR(1) ที่ให้ half-life ตามต้องการ (หน่วย = จำนวนแท่ง)"""
    return 0.5 ** (1.0 / float(half_life))


def half_life_from_phi(phi):
    """half-life (จำนวนแท่ง) จากสัมประสิทธิ์ AR(1) · ถ้า φ ไม่อยู่ใน (0,1) ถือว่าไม่ดึงกลับ"""
    if not (0.0 < phi < 1.0):
        return math.inf
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

    คืน dict: y, x, eps (ส่วนที่ดึงกลับจริง · fake ไม่มี = None), beta_path, kind"""
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
    """OLS ธรรมดา · คืน coef, se, t, resid, r2, s2 (ถ้า const=True ตัวแรกของ coef คือค่าคงที่)"""
    y = np.asarray(y, float)
    X = np.asarray(X, float)
    if X.ndim == 1:
        X = X[:, None]
    if const:
        X = np.column_stack([np.ones(len(y)), X])
    xtx = X.T @ X
    coef = np.linalg.solve(xtx, X.T @ y)
    resid = y - X @ coef
    dof = len(y) - X.shape[1]
    s2 = float(resid @ resid) / dof
    se = np.sqrt(np.diag(s2 * np.linalg.inv(xtx)))
    tss = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - float(resid @ resid) / tss if tss > 0 else 0.0
    return {"coef": coef, "se": se, "t": coef / se, "resid": resid, "r2": r2, "s2": s2}


def tls_beta(y, x):
    """Total least squares (orthogonal regression) ของ y บน x — ไม่ขึ้นกับว่าใครเป็นตัวตั้ง
    คืน (alpha, beta)"""
    y = np.asarray(y, float)
    x = np.asarray(x, float)
    cov = np.cov(x, y)
    sxx, syy, sxy = cov[0, 0], cov[1, 1], cov[0, 1]
    beta = (syy - sxx + math.sqrt((syy - sxx) ** 2 + 4.0 * sxy ** 2)) / (2.0 * sxy)
    return float(y.mean() - beta * x.mean()), float(beta)


# ───────────────────────── stationarity ─────────────────────────

def adf_stat(x, lags=1, const=True):
    """ADF: ค่า t ของ ρ ใน  Δx_t = a + ρ·x_{t−1} + Σ γ_i·Δx_{t−i} + e_t
    ρ ติดลบมาก = มีแรงดึงกลับ · ค่า t นี้ "ห้าม" เทียบกับตาราง normal/t ปกติ
    ต้องเทียบกับค่าวิกฤตของ Dickey-Fuller (ดู mc_null_adf / mc_null_eg)"""
    x = np.asarray(x, float)
    dx = np.diff(x)
    y = dx[lags:]
    cols = [x[lags:-1]]
    for i in range(1, lags + 1):
        cols.append(dx[lags - i:len(dx) - i])
    r = ols(y, np.column_stack(cols), const=const)
    return float(r["t"][1 if const else 0])


def adf_stat_batch(x, lags=1, const=True, chunk=2000):
    """ADF ของหลายเส้นพร้อมกัน (n_series × n) — ผลเท่ากับเรียก adf_stat ทีละเส้น"""
    x = np.asarray(x, float)
    out = np.empty(x.shape[0])
    for s in range(0, x.shape[0], chunk):
        xs = x[s:s + chunk]
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
        coef = np.linalg.solve(xtx, xty[..., None])[..., 0]
        resid = y - np.einsum("smi,si->sm", X, coef)
        s2 = (resid ** 2).sum(axis=1) / (y.shape[1] - X.shape[2])
        j = 1 if const else 0
        se = np.sqrt(s2 * np.linalg.inv(xtx)[:, j, j])
        out[s:s + chunk] = coef[:, j] / se
    return out


def resid_batch(y, X):
    """ส่วนเหลือของ OLS (มีค่าคงที่) ของหลายระบบพร้อมกัน
    y: (S, n) · X: (S, n, p) → resid (S, n)"""
    y = np.asarray(y, float)
    X = np.asarray(X, float)
    X1 = np.concatenate([np.ones(X.shape[:2] + (1,)), X], axis=2)
    xtx = np.einsum("smi,smj->sij", X1, X1)
    xty = np.einsum("smi,sm->si", X1, y)
    coef = np.linalg.solve(xtx, xty[..., None])[..., 0]
    return y - np.einsum("smi,si->sm", X1, coef)


def mc_null_adf(n_obs, n_sim=20000, lags=1, g=None, const=True):
    """การแจกแจงของค่า ADF เมื่อ "ความจริงคือ random walk" (ไม่มีแรงดึงกลับ)
    ใช้หาค่าวิกฤตเอง แทนการเปิดตาราง · คืนอาร์เรย์เรียงจากน้อยไปมาก"""
    g = g or rng(9001)
    x = np.cumsum(g.standard_normal((n_sim, n_obs)), axis=1)
    return np.sort(adf_stat_batch(x, lags=lags, const=const))


def mc_null_eg(n_obs, n_vars=2, n_sim=20000, lags=1, g=None, chunk=2000):
    """การแจกแจงของค่า Engle-Granger เมื่อ "ไม่มีตัวไหนผูกกันเลย"
    จำลอง random walk อิสระ n_vars เส้น · ถดถอยเส้นแรกบนเส้นที่เหลือ (มีค่าคงที่)
    แล้ววัด ADF (ไม่มีค่าคงที่) ของส่วนเหลือ · ยิ่ง n_vars มาก ค่าวิกฤตยิ่งติดลบมาก"""
    g = g or rng(9002 + n_vars)
    out = np.empty(n_sim)
    for s in range(0, n_sim, chunk):
        m = min(chunk, n_sim - s)
        w = np.cumsum(g.standard_normal((m, n_obs, n_vars)), axis=1)
        res = resid_batch(w[:, :, 0], w[:, :, 1:])
        out[s:s + m] = adf_stat_batch(res, lags=lags, const=False)
    return np.sort(out)


def crit_values(null_sorted, qs=(0.01, 0.05, 0.10)):
    """ค่าวิกฤตจากการแจกแจงใต้สมมติฐานว่าง — "ต้องติดลบกว่านี้ถึงจะเรียกว่าผ่าน" """
    return {q: float(np.quantile(null_sorted, q)) for q in qs}


def p_value(stat, null_sorted):
    """p-value แบบจำลอง: สัดส่วนของโลกที่ "ไม่มีอะไรเลย" ที่ให้ค่าติดลบได้เท่านี้หรือกว่า"""
    return float(np.searchsorted(null_sorted, stat, side="right")) / len(null_sorted)


def eg_test(y, X, lags=1):
    """Engle-Granger สองขั้น: (1) ถดถอย y บน X (มีค่าคงที่) (2) ADF บนส่วนเหลือ
    คืน alpha, beta (อาร์เรย์), resid, adf, r2 · adf ต้องเทียบกับ mc_null_eg เท่านั้น"""
    r = ols(y, X, const=True)
    return {
        "alpha": float(r["coef"][0]),
        "beta": np.asarray(r["coef"][1:], float),
        "resid": r["resid"],
        "adf": adf_stat(r["resid"], lags=lags, const=False),
        "r2": r["r2"],
    }


def fit_ar1(x):
    """ประมาณ AR(1): x_t = c + φ·x_{t−1} + e_t → φ, μ, σ_eq, half-life
    หมายเหตุ: φ ที่ประมาณจากข้อมูลจำกัดเอนเอียงต่ำ จึงมักได้ half-life สั้นกว่าจริง"""
    x = np.asarray(x, float)
    r = ols(x[1:], x[:-1], const=True)
    c, phi = float(r["coef"][0]), float(r["coef"][1])
    sd_e = math.sqrt(r["s2"])
    if 0.0 < phi < 1.0:
        mu = c / (1.0 - phi)
        sigma_eq = sd_e / math.sqrt(1.0 - phi * phi)
    else:
        mu, sigma_eq = float(np.mean(x)), math.inf
    return {"c": c, "phi": phi, "sd_e": sd_e, "mu": mu, "sigma_eq": sigma_eq,
            "half_life": half_life_from_phi(phi), "t_phi_minus_1": (phi - 1.0) / float(r["se"][1])}


def variance_ratio(x, q):
    """Var(x_{t+q} − x_t) / (q · Var(x_{t+1} − x_t))
    ≈ 1 = random walk · < 1 = ดึงกลับ · > 1 = วิ่งเป็นเทรนด์"""
    x = np.asarray(x, float)
    d1 = np.diff(x)
    dq = x[q:] - x[:-q]
    return float(dq.var(ddof=1) / (q * d1.var(ddof=1)))


# ───────────────────────── z-score (ไม่มองอนาคต) ─────────────────────────

def rolling_mean_std(s, window):
    """ค่าเฉลี่ยและ sd ของ `window` แท่งล่าสุด "รวมแท่ง t" · t < window−1 ให้ NaN"""
    s = np.asarray(s, float)
    n = len(s)
    mean = np.full(n, np.nan)
    std = np.full(n, np.nan)
    if n < window:
        return mean, std
    c1 = np.concatenate([[0.0], np.cumsum(s)])
    c2 = np.concatenate([[0.0], np.cumsum(s * s)])
    m = (c1[window:] - c1[:-window]) / window
    v = (c2[window:] - c2[:-window]) / window - m * m
    v = np.maximum(v, 0.0) * window / (window - 1)
    mean[window - 1:] = m
    std[window - 1:] = np.sqrt(v)
    return mean, std


def zscore_rolling(s, window):
    """z ของแท่ง t เทียบกับหน้าต่าง `window` แท่งล่าสุด (รวมแท่ง t) — ใช้ข้อมูลอดีตเท่านั้น"""
    mean, std = rolling_mean_std(s, window)
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
      z เป็น NaN → ว่าง"""
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
    lag=1 (ถูก): สถานะของแท่ง t รับผลของแท่ง t+1
    lag=2 (เข้มกว่า): ส่งคำสั่งช้าไปหนึ่งแท่ง
    lag=0 (บั๊ก): ให้สถานะที่ตัดสินใจจากราคาปิดแท่ง t รับผลของแท่ง t เอง
    คืน (pnl, info) โดย info มี held, turnover, n_trades"""
    y = np.asarray(y, float)
    x = np.asarray(x, float)
    n = len(y)
    b = np.broadcast_to(np.asarray(beta, float), (n,)).copy()
    pos = np.asarray(pos, float)
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
    return pnl, {"held": held, "turnover": turnover, "n_trades": count_trades(held)}


def count_trades(held):
    """จำนวนครั้งที่ "เปิดสถานะใหม่" (จากว่างหรือจากฝั่งตรงข้าม)"""
    held = np.asarray(held, float)
    prev = np.concatenate([[0.0], held[:-1]])
    return int(np.sum((held != 0) & (held != prev)))


def trade_pnls(held, pnl):
    """ผลตอบแทนรวมของแต่ละไม้ (ตั้งแต่เปิดจนปิด) — ใช้นับอัตราชนะและกำไรเฉลี่ยต่อไม้
    ต้นทุนตอนปิดสถานะตกอยู่ในแท่งถัดไป จึงรวมแท่งที่ปิดเข้าไปในไม้นั้นด้วย"""
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
                    out.append(acc)
                    acc = pnl[t]
            else:
                acc = pnl[t]
            cur = held[t]
        elif cur != 0:
            acc += pnl[t]
    if cur != 0:
        out.append(acc)
    return np.array(out)


def perf_stats(pnl, held=None):
    """สรุปผล: ผลตอบแทนต่อปี · ความผันผวนต่อปี · Sharpe · drawdown ลึกสุด (คิดแบบบวกสะสม ไม่ทบต้น)"""
    pnl = np.asarray(pnl, float)
    mean, sd = float(pnl.mean()), float(pnl.std(ddof=1)) if len(pnl) > 1 else 0.0
    eq = np.cumsum(pnl)
    peak = np.maximum.accumulate(np.concatenate([[0.0], eq]))[1:]
    out = {
        "ann_return": mean * DAYS_PER_YEAR,
        "ann_vol": sd * math.sqrt(DAYS_PER_YEAR),
        "sharpe": (mean / sd) * math.sqrt(DAYS_PER_YEAR) if sd > 0 else 0.0,
        "total": float(eq[-1]) if len(eq) else 0.0,
        "max_dd": float(np.max(peak - eq)) if len(eq) else 0.0,
    }
    if held is not None:
        tp = trade_pnls(held, pnl)
        out["n_trades"] = int(len(tp))
        out["hit_rate"] = float(np.mean(tp > 0)) if len(tp) else 0.0
        out["avg_trade"] = float(tp.mean()) if len(tp) else 0.0
        out["time_in_market"] = float(np.mean(np.asarray(held) != 0))
    return out


def walk_forward_pair(y, x, train=250, refit=21, entry=2.0, exit=0.0, stop=None,
                      max_hold=None, cost_per_leg=0.0, lag=1):
    """backtest คู่แบบเดินหน้า (walk-forward) — ไม่มีพารามิเตอร์ตัวไหนเห็นอนาคต
    ทุก `refit` แท่ง: ประมาณ α, β (OLS) และ μ, σ ของ ε จาก `train` แท่งล่าสุดที่จบ ณ แท่งก่อนหน้า
    แล้วใช้ค่าชุดนั้นคำนวณ z ของ `refit` แท่งถัดไป
    คืน dict: pnl, held, z, beta (อนุกรม), eps (สเปรดตามพารามิเตอร์ ณ ขณะนั้น), stats"""
    y = np.asarray(y, float)
    x = np.asarray(x, float)
    n = len(y)
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
    return {"pnl": pnl, "held": info["held"], "z": z, "beta": beta, "eps": eps,
            "stats": perf_stats(pnl[train:], info["held"][train:])}


def portfolio_pnl(weights, returns, cost_per_leg=0.0, lag=1):
    """ผลตอบแทนรายแท่งของพอร์ตหลายสินทรัพย์
    weights[t, i] = น้ำหนัก (สัดส่วนของทุน มีเครื่องหมาย) ที่ตัดสินใจตอนสิ้นแท่ง t
    returns[t, i] = ผลตอบแทนของสินทรัพย์ i ในแท่ง t
    น้ำหนักของแท่ง t รับผลของแท่ง t+lag · ต้นทุน = c × ผลรวม |น้ำหนักที่เปลี่ยน|
    คืน (pnl, turnover)"""
    w = np.asarray(weights, float)
    r = np.asarray(returns, float)
    held = np.zeros_like(w)
    if lag > 0:
        held[lag:] = w[:-lag]
    else:
        held = w.copy()
    turnover = np.abs(np.diff(held, axis=0, prepend=np.zeros((1, w.shape[1])))).sum(axis=1)
    return (held * r).sum(axis=1) - cost_per_leg * turnover, turnover


# ───────────────────────── ตัวช่วยปัดเลขสำหรับ figures.json ─────────────────────────

def rd(v, d=2):
    """ปัดทศนิยมเพื่อเก็บลง figures.json — ค่าที่เก็บคือค่าที่จะปรากฏในบทตรงตัว"""
    v = float(v)
    if not math.isfinite(v):
        return None
    out = round(v, d)
    return int(out) if d == 0 else out


def pct(v, d=1):
    """สัดส่วน → เปอร์เซ็นต์ที่ปัดแล้ว (0.0312 → 3.1)"""
    return rd(100.0 * float(v), d)


def bps(v, d=1):
    """สัดส่วน → basis point ที่ปัดแล้ว (0.0005 → 5.0)"""
    return rd(10000.0 * float(v), d)


# ───────────────────────── ทดสอบตัวเอง ─────────────────────────

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

    # batch ต้องให้ผลเท่ากับทีละเส้น
    w = np.cumsum(g.standard_normal((5, 300)), axis=1)
    one = np.array([adf_stat(w[i]) for i in range(5)])
    assert np.allclose(one, adf_stat_batch(w)), (one, adf_stat_batch(w))
    one0 = np.array([adf_stat(w[i], const=False) for i in range(5)])
    assert np.allclose(one0, adf_stat_batch(w, const=False))

    # ค่าวิกฤตที่จำลองเองต้องใกล้ค่าตำรา (−2.86 สำหรับ ADF มีค่าคงที่ · −3.34 สำหรับ EG สองตัวแปร)
    c_adf = crit_values(mc_null_adf(500, n_sim=8000, g=rng(2)))[0.05]
    c_eg = crit_values(mc_null_eg(500, 2, n_sim=8000, g=rng(3)))[0.05]
    assert -3.0 < c_adf < -2.75, c_adf
    assert -3.5 < c_eg < -3.2, c_eg

    # backtest: ไม่มีต้นทุน + สเปรดดึงกลับจริง → ต้องกำไร · lag=0 (บั๊ก) ต้องแย่กว่า lag=1
    z = zscore_fixed(eps, 0.0, 0.03)
    pos = band_positions(z, entry=1.5, exit=0.0)
    good, info = spread_pnl(y, x, 1.4, pos, lag=1)
    bug, _ = spread_pnl(y, x, 1.4, pos, lag=0)
    assert good.sum() > 0 and bug.sum() < good.sum(), (good.sum(), bug.sum())
    # ต้นทุนครบรอบ = 2c ต่อ gross ต่อไม้
    costly, info2 = spread_pnl(y, x, 1.4, pos, cost_per_leg=0.001, lag=1)
    assert abs((good.sum() - costly.sum()) - 0.001 * info2["turnover"].sum()) < 1e-12
    tp = trade_pnls(info["held"], good)
    assert abs(tp.sum() - good.sum()) < 1e-9 and len(tp) == info["n_trades"]

    wf = walk_forward_pair(y, x, train=250, refit=21, entry=1.5, exit=0.0)
    assert wf["stats"]["total"] > 0

    print("sas_core selftest ผ่าน")
    print(f"  β̂ = {r['beta'][0]:.3f} (จริง 1.4) · EG-ADF = {r['adf']:.2f} · half-life ≈ {fit['half_life']:.1f} แท่ง (จริง 12)")
    print(f"  ค่าวิกฤต 5% จากการจำลอง: ADF = {c_adf:.2f} (ตำรา −2.86) · EG สองตัวแปร = {c_eg:.2f} (ตำรา −3.34)")
    print(f"  walk-forward ไม่คิดต้นทุน: Sharpe = {wf['stats']['sharpe']:.2f} · {wf['stats']['n_trades']} ไม้")


if __name__ == "__main__":
    _selftest()
