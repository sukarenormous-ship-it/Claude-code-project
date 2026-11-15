#!/usr/bin/env python3
"""สถิติของเล่ม 2 แบบ stdlib ล้วน (Stat Arb for Non Quant · เล่ม 2 · แผน docs/sab2-book-plan.md หัวข้อ 7)
Statistics for volume 2, standard library only — used by tools/sab2_figures_ch/*.py and by the 💻 blocks in the pages.

ทุกฟังก์ชันรับ list ของ float และคืน float / list / dict ธรรมดา (ไม่มี numpy) · ชื่อคีย์เป็นภาษาอังกฤษให้โค้ดในหน้าอ่านง่าย
Every function takes plain lists and returns plain floats / lists / dicts.

    python3 tools/sab2_stats.py --selftest     # เทียบ numpy (1e-9) · ค่าวิกฤต ADF ที่ตีพิมพ์ · การจำลองที่รู้คำตอบ

หมวด (sections): ค่าพื้นฐาน · การถดถอย · AR(1)/OU/half-life · ADF (+ p-value แบบจำลอง adf_pvalue_sim) · Engle–Granger · หน้าต่างเลื่อน · Kalman 1 มิติ ·
PCA (Jacobi) · พอร์ต · Kelly · walk-forward
"""

import math
import random
import statistics
import sys

# ═══════════════════════════ ค่าพื้นฐาน (basics) ═══════════════════════════


def mean(xs):
    """ค่าเฉลี่ย · arithmetic mean"""
    return math.fsum(xs) / len(xs)


def var(xs, ddof=1):
    """ความแปรปรวน (ตัวหาร n − ddof) · variance with n − ddof denominator"""
    m = mean(xs)
    return math.fsum((x - m) ** 2 for x in xs) / (len(xs) - ddof)


def sd(xs, ddof=1):
    """ส่วนเบี่ยงเบนมาตรฐาน · standard deviation"""
    return math.sqrt(var(xs, ddof))


def cov(xs, ys, ddof=1):
    """ความแปรปรวนร่วม · covariance"""
    mx, my = mean(xs), mean(ys)
    return math.fsum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (len(xs) - ddof)


def corr(xs, ys):
    """สหสัมพันธ์เพียร์สัน · Pearson correlation"""
    mx, my = mean(xs), mean(ys)
    sxy = math.fsum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = math.fsum((x - mx) ** 2 for x in xs)
    syy = math.fsum((y - my) ** 2 for y in ys)
    return sxy / math.sqrt(sxx * syy)


def diff(xs):
    """ผลต่างวันต่อวัน x[t] − x[t−1] (ยาว n − 1) · first differences"""
    return [b - a for a, b in zip(xs, xs[1:])]


def logs(xs):
    """log ธรรมชาติของราคา · natural log of prices"""
    return [math.log(x) for x in xs]


def zscore(xs, m=None, s=None):
    """ระยะห่างจากค่าเฉลี่ยเป็นจำนวน SD (ใส่ m, s จากช่วงเลือกได้) · z-scores, optionally with a fixed ruler"""
    m = mean(xs) if m is None else m
    s = sd(xs) if s is None else s
    return [(x - m) / s for x in xs]


def norm_cdf(z):
    """CDF ของการแจกแจงปกติมาตรฐาน · standard normal CDF"""
    return 0.5 * math.erfc(-z / math.sqrt(2.0))


def norm_ppf(p):
    """ค่าผกผันของ CDF ปกติ · inverse standard normal CDF"""
    return statistics.NormalDist().inv_cdf(p)


# ═══════════════════════════ การถดถอย (regression) ═══════════════════════════


def ols(x, y):
    """ถดถอย y = a + b·x แบบกำลังสองน้อยสุด · simple OLS with intercept
    คืน slope · intercept · residuals · fitted · r2 · sigma (SE ของ residual) · se_slope · se_intercept · t_slope · n"""
    n = len(x)
    if n != len(y) or n < 3:
        raise ValueError("ols ต้องมี x, y ยาวเท่ากันอย่างน้อย 3 จุด")
    mx, my = mean(x), mean(y)
    sxx = math.fsum((u - mx) ** 2 for u in x)
    sxy = math.fsum((u - mx) * (v - my) for u, v in zip(x, y))
    b = sxy / sxx
    a = my - b * mx
    fitted = [a + b * u for u in x]
    resid = [v - f for v, f in zip(y, fitted)]
    sse = math.fsum(r * r for r in resid)
    sst = math.fsum((v - my) ** 2 for v in y)
    s2 = sse / (n - 2)
    se_b = math.sqrt(s2 / sxx)
    se_a = math.sqrt(s2 * (1.0 / n + mx * mx / sxx))
    return {"slope": b, "intercept": a, "residuals": resid, "fitted": fitted,
            "r2": 1.0 - sse / sst if sst > 0 else float("nan"), "sigma": math.sqrt(s2),
            "se_slope": se_b, "se_intercept": se_a, "t_slope": b / se_b if se_b > 0 else float("inf"), "n": n}


def ols_origin(x, y):
    """ถดถอยผ่านจุดกำเนิด y = b·x (ไม่มีค่าคงที่) · regression through the origin"""
    sxx = math.fsum(u * u for u in x)
    b = math.fsum(u * v for u, v in zip(x, y)) / sxx
    resid = [v - b * u for u, v in zip(x, y)]
    s2 = math.fsum(r * r for r in resid) / (len(x) - 1)
    return {"slope": b, "residuals": resid, "se_slope": math.sqrt(s2 / sxx), "sigma": math.sqrt(s2)}


def solve(A, b):
    """แก้ระบบ A·x = b ด้วยการกำจัดแบบเกาส์ (pivot บางส่วน) · Gaussian elimination with partial pivoting"""
    n = len(A)
    M = [list(map(float, row)) + [float(v)] for row, v in zip(A, b)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        if abs(M[p][c]) < 1e-300:
            raise ValueError("เมทริกซ์เอกฐาน (singular)")
        M[c], M[p] = M[p], M[c]
        for r in range(n):
            if r != c:
                f = M[r][c] / M[c][c]
                M[r] = [u - f * w for u, w in zip(M[r], M[c])]
    return [M[i][n] / M[i][i] for i in range(n)]


def inverse(A):
    """เมทริกซ์ผกผัน (Gauss–Jordan) · matrix inverse"""
    n = len(A)
    cols = [solve(A, [1.0 if i == j else 0.0 for i in range(n)]) for j in range(n)]
    return [[cols[j][i] for j in range(n)] for i in range(n)]


def ols_multi(columns, y, const=True):
    """ถดถอยหลายตัวแปร y = c + Σ b_j·x_j (columns = list ของคอลัมน์) · multiple OLS via normal equations
    คืน coef (ค่าคงที่ก่อนถ้า const) · se · t · residuals · r2 · sigma · n · k"""
    n = len(y)
    X = [[1.0] * n] if const else []
    X += [list(map(float, c)) for c in columns]
    k = len(X)
    XtX = [[math.fsum(a * b for a, b in zip(X[i], X[j])) for j in range(k)] for i in range(k)]
    Xty = [math.fsum(a * b for a, b in zip(X[i], y)) for i in range(k)]
    inv = inverse(XtX)
    coef = [math.fsum(inv[i][j] * Xty[j] for j in range(k)) for i in range(k)]
    fitted = [math.fsum(coef[j] * X[j][t] for j in range(k)) for t in range(n)]
    resid = [v - f for v, f in zip(y, fitted)]
    sse = math.fsum(r * r for r in resid)
    my = mean(y)
    sst = math.fsum((v - my) ** 2 for v in y)
    s2 = sse / (n - k)
    se = [math.sqrt(s2 * inv[i][i]) for i in range(k)]
    return {"coef": coef, "se": se, "t": [c / s for c, s in zip(coef, se)], "residuals": resid,
            "r2": 1.0 - sse / sst if const and sst > 0 else float("nan"), "sigma": math.sqrt(s2), "n": n, "k": k}


# ═══════════════════════════ AR(1) · OU · half-life ═══════════════════════════


def ar1(xs, const=True):
    """ประมาณ φ ของ x[t] = c + φ·x[t−1] + e (ถดถอยวันนี้บนเมื่อวาน) · AR(1) by OLS
    คืน phi · c · se_phi · sigma (SD ของ e) · residuals · mean (c / (1 − φ)) · n (จำนวนคู่ที่ใช้)"""
    x0, x1 = xs[:-1], xs[1:]
    if const:
        r = ols(x0, x1)
        phi, c, se = r["slope"], r["intercept"], r["se_slope"]
    else:
        r = ols_origin(x0, x1)
        phi, c, se = r["slope"], 0.0, r["se_slope"]
    return {"phi": phi, "c": c, "se_phi": se, "sigma": r["sigma"], "residuals": r["residuals"],
            "mean": c / (1.0 - phi) if phi != 1 else float("nan"), "n": len(x1)}


def half_life(phi):
    """ครึ่งชีวิต (ช่วง) ของระยะห่าง: φ^h = 1/2 → h = ln 2 / −ln φ · half-life; inf ถ้า φ ≥ 1 · nan ถ้า φ ≤ 0"""
    if phi >= 1:
        return float("inf")
    if phi <= 0:
        return float("nan")
    return math.log(2.0) / -math.log(phi)


def half_life_ci(phi, se_phi, level=0.95):
    """ช่วงความเชื่อมั่นโดยประมาณของ half-life: แปลงปลายช่วง φ ± z·SE ผ่าน half_life (ฟังก์ชันเพิ่มตาม φ)
    approximate CI by mapping the normal CI of φ through half_life (monotone); ปลายบน = inf เมื่อ φ + z·SE ≥ 1"""
    z = norm_ppf(0.5 + level / 2.0)
    lo, hi = phi - z * se_phi, phi + z * se_phi
    return {"half_life": half_life(phi), "lo": half_life(lo) if lo > 0 else 0.0, "hi": half_life(hi),
            "phi_lo": lo, "phi_hi": hi, "z": z}


def ou_from_ar1(phi, c, sigma_eps, dt=1.0):
    """พารามิเตอร์ OU dX = θ(μ − X)dt + σ dW จาก AR(1) ที่ระยะห่างเวลา dt · OU parameters from an AR(1) fit
    θ = −ln φ / dt · μ = c / (1 − φ) · σ = σ_e·√(2θ / (1 − φ²)) · SD นิ่ง = σ_e / √(1 − φ²) · half-life = ln 2 / θ"""
    if not 0 < phi < 1:
        raise ValueError("OU ต้องการ 0 < φ < 1")
    theta = -math.log(phi) / dt
    return {"theta": theta, "mu": c / (1.0 - phi), "sigma": sigma_eps * math.sqrt(2.0 * theta / (1.0 - phi * phi)),
            "sd_stationary": sigma_eps / math.sqrt(1.0 - phi * phi), "half_life": math.log(2.0) / theta}


# ═══════════════════════════ ADF ═══════════════════════════
# MacKinnon (2010) "Critical Values for Cointegration Tests", Queen's Economics Dept. WP 1227, ตาราง case "c" (มีค่าคงที่):
#   ค่าวิกฤต = β∞ + β1/T + β2/T² + β3/T³ · N = จำนวนตัวแปรในสมการ (1 = ADF ธรรมดา · 2 = Engle–Granger สองขา)
MACKINNON_2010_C = {
    1: {"1%": (-3.43035, -6.5393, -16.786, -79.433), "5%": (-2.86154, -2.8903, -4.234, -40.040),
        "10%": (-2.56677, -1.5384, -2.809, 0.0)},
    2: {"1%": (-3.89644, -10.9519, -33.527, 0.0), "5%": (-3.33613, -6.1101, -6.823, 0.0),
        "10%": (-3.04445, -4.2412, -2.720, 0.0)},
}
# MacKinnon (1994) "Approximate asymptotic distribution functions for unit-root and cointegration tests", JBES 12:
#   p ≈ Φ(Σ γ_i τ^i) · ใช้ชุด small-p เมื่อ τ ≤ τ* และชุด large-p เมื่อ τ > τ* · นอก [τ_min, τ_max] = 0 หรือ 1 (case "c")
MACKINNON_1994_C = {
    1: {"min": -18.83, "max": 2.74, "star": -1.61, "small": (2.1659, 1.4412, 0.038269),
        "large": (1.7339, 0.93202, -0.12745, -0.010368)},
    2: {"min": -18.86, "max": 0.92, "star": -2.62, "small": (2.92, 1.5012, 0.039796),
        "large": (2.1945, 0.64695, -0.29198, -0.042377)},
}


def adf_crit(nobs, n_vars=1):
    """ค่าวิกฤต ADF แบบมีค่าคงที่ที่ขนาดตัวอย่าง nobs (MacKinnon 2010) · ADF critical values {"1%","5%","10%"}"""
    t = float(nobs)
    return {k: b[0] + b[1] / t + b[2] / t ** 2 + b[3] / t ** 3 for k, b in MACKINNON_2010_C[n_vars].items()}


def adf_pvalue(stat, n_vars=1):
    """p-value โดยประมาณของสถิติ ADF/EG (MacKinnon 1994 · เชิงเส้นกำกับ) · approximate asymptotic p-value"""
    c = MACKINNON_1994_C[n_vars]
    if stat > c["max"]:
        return 1.0
    if stat < c["min"]:
        return 0.0
    g = c["small"] if stat <= c["star"] else c["large"]
    return norm_cdf(sum(gi * stat ** i for i, gi in enumerate(g)))


def adf(xs, lags=0, const=True, n_vars=1):
    """ทดสอบ Augmented Dickey–Fuller: Δx[t] = α + γ·x[t−1] + Σ β_i·Δx[t−i] + e · สถิติ = γ / SE(γ)
    ADF test with constant (const=False: ไม่มีค่าคงที่ ใช้กับ residual ใน Engle–Granger) และจำนวน lag คงที่
    คืน stat · pvalue · crit · gamma · phi (= 1 + γ) · nobs · lags · reject5 (ปฏิเสธ "ไม่มีเชือก" ที่ 5%)"""
    dx = diff(xs)
    y = dx[lags:]
    level = xs[lags:-1]
    cols = [level] + [dx[lags - i:len(dx) - i] for i in range(1, lags + 1)]
    r = ols_multi(cols, y, const=const)
    j = 1 if const else 0
    stat = r["coef"][j] / r["se"][j]
    nobs = len(y)
    crit = adf_crit(nobs, n_vars)
    return {"stat": stat, "pvalue": adf_pvalue(stat, n_vars), "crit": crit, "gamma": r["coef"][j],
            "phi": 1.0 + r["coef"][j], "nobs": nobs, "lags": lags, "reject5": stat < crit["5%"]}


_NULL_CACHE = {}


def _rw_world(seed, n, n_vars=1):
    """โลกเดินสุ่มมาตรฐาน (ก้าว N(0, 1)) ยาว n · n_vars = 2 → คู่เดินสุ่มอิสระ (y, x) สำหรับ Engle–Granger"""
    rng = random.Random(seed)
    walks = []
    for _ in range(n_vars):
        v, w = 0.0, []
        for _ in range(n):
            v += rng.gauss(0.0, 1.0)
            w.append(v)
        walks.append(w)
    return walks[0] if n_vars == 1 else tuple(walks)


def adf_null(n, worlds=10000, seed=1, lags=0, n_vars=1, world=None):
    """ค่าสถิติ ADF (n_vars = 1 · มีค่าคงที่) หรือ Engle–Granger (n_vars = 2) ของโลกเดินสุ่ม worlds โลก ยาว n เท่าข้อมูล
    เรียงจากน้อยไปมาก · โลกที่ i ใช้ seed + i (i = 0 … worlds − 1) · world(seed, n) → ซีรีส์ (หรือคู่ (y, x) ถ้า n_vars = 2)
    แทนโลกมาตรฐานได้ (เช่น lambda s, n: sab2_sim.random_walk_pair(seed=s, n=n)["X"]) · จำผลไว้ในกระบวนการ
    null distribution of the ADF / EG statistic by simulation (small samples, where the asymptotic table is off)"""
    key = (n, worlds, seed, lags, n_vars, world)
    if key not in _NULL_CACHE:
        gen = world or (lambda s, m: _rw_world(s, m, n_vars))
        out = []
        for i in range(worlds):
            w = gen(seed + i, n)
            out.append(engle_granger(w[0], w[1], lags)["stat"] if n_vars == 2 else adf(w, lags=lags)["stat"])
        _NULL_CACHE[key] = sorted(out)
    return _NULL_CACHE[key]


def adf_pvalue_sim(stat, n, worlds=10000, seed=1, lags=0, n_vars=1, world=None):
    """p-value แบบจำลองของค่าสถิติ ADF/EG ที่ข้อมูลยาว n (จำนวนจุดของซีรีส์ ไม่ใช่จำนวนแถวการเปลี่ยน):
    สัดส่วนโลกเดินสุ่มที่ได้ค่าสถิติ ≤ stat · คืน pvalue · below (จำนวนโลก) · worlds · crit ({"1%","5%","10%"} =
    ค่าที่ลำดับ int(p·worlds) จากล่าง) · asymptotic (adf_pvalue ของ MacKinnon เทียบ) · simulated small-sample p-value"""
    null = adf_null(n, worlds, seed, lags, n_vars, world)
    below = sum(1 for v in null if v <= stat)
    crit = {k: null[max(0, int(p * worlds) - 1)] for k, p in (("1%", 0.01), ("5%", 0.05), ("10%", 0.10))}
    return {"pvalue": below / worlds, "below": below, "worlds": worlds, "n": n, "crit": crit,
            "asymptotic": adf_pvalue(stat, n_vars)}


def engle_granger(y, x, lags=0):
    """Engle–Granger สองขั้น: (1) ถดถอย y = a + h·x หา h และ residual (2) ADF บน residual (ไม่มีค่าคงที่ ·
    ค่าวิกฤตแบบ N = 2 ของ MacKinnon) · two-step cointegration test, same convention as statsmodels.coint
    คืน h · intercept · residuals · stat · pvalue · crit · reject5 · adf (ผลขั้น 2 ทั้งชุด)"""
    step1 = ols(x, y)
    a = adf(step1["residuals"], lags=lags, const=False, n_vars=2)
    return {"h": step1["slope"], "intercept": step1["intercept"], "residuals": step1["residuals"],
            "stat": a["stat"], "pvalue": a["pvalue"], "crit": a["crit"], "reject5": a["reject5"], "adf": a}


# ═══════════════════════════ หน้าต่างเลื่อน (rolling) ═══════════════════════════


def rolling(xs, window, fn):
    """ใช้ fn กับหน้าต่างยาว window ที่จบที่วัน t (วันแรก ๆ ที่ข้อมูลไม่พอ = None) · generic rolling apply"""
    return [None if t + 1 < window else fn(xs[t + 1 - window:t + 1]) for t in range(len(xs))]


def rolling_mean(xs, window):
    """ค่าเฉลี่ยเคลื่อนที่ (ใช้ข้อมูลถึงวัน t เท่านั้น) · trailing rolling mean"""
    return rolling(xs, window, mean)


def rolling_sd(xs, window, ddof=1):
    """SD เคลื่อนที่ · trailing rolling standard deviation"""
    return rolling(xs, window, lambda w: sd(w, ddof))


def rolling_ols(x, y, window):
    """ถดถอย y บน x ในหน้าต่างเลื่อน → [{"slope","intercept","sigma"} | None] · trailing rolling regression"""
    out = []
    for t in range(len(x)):
        if t + 1 < window:
            out.append(None)
            continue
        r = ols(x[t + 1 - window:t + 1], y[t + 1 - window:t + 1])
        out.append({"slope": r["slope"], "intercept": r["intercept"], "sigma": r["sigma"]})
    return out


# ═══════════════════════════ Kalman 1 มิติ ═══════════════════════════


def kalman_hedge(x, y, q, r, beta0=0.0, p0=1.0):
    """Kalman 1 มิติสำหรับ hedge ratio ที่เปลี่ยนตามเวลา · 1-D Kalman filter for a time-varying hedge ratio
    สถานะ β[t] = β[t−1] + w (ความแปรปรวน q) · สังเกต y[t] = β[t]·x[t] + v (ความแปรปรวน r)
    ทุกวัน: ทาย β → เห็น y → ใหม่ = เดิม + K × (เห็น − ทาย) โดย K = P·x / (P·x² + r)
    คืน beta (หลังเห็นวัน t) · beta_prior (ก่อนเห็น = ใช้เทรดวัน t ได้) · gain · P · innovation · S (ความแปรปรวนของ innovation)"""
    beta, P = float(beta0), float(p0)
    out = {"beta": [], "beta_prior": [], "gain": [], "P": [], "innovation": [], "S": []}
    for xt, yt in zip(x, y):
        P = P + q                       # ทาย: β คงเดิม ความไม่แน่ใจเพิ่ม q
        e = yt - beta * xt              # เห็น − ทาย
        S = P * xt * xt + r
        K = P * xt / S
        out["beta_prior"].append(beta)
        beta = beta + K * e
        P = (1.0 - K * xt) * P
        for k, v in (("beta", beta), ("gain", K), ("P", P), ("innovation", e), ("S", S)):
            out[k].append(v)
    return out


# ═══════════════════════════ PCA (Jacobi) ═══════════════════════════


def cov_matrix(columns, ddof=1):
    """เมทริกซ์ความแปรปรวนร่วมของหลายคอลัมน์ · covariance matrix (columns = list ของ series)"""
    k = len(columns)
    return [[cov(columns[i], columns[j], ddof) for j in range(k)] for i in range(k)]


def jacobi_eigen(A, tol=1e-15, max_sweeps=100):
    """ค่าลักษณะเฉพาะและเวกเตอร์ของเมทริกซ์สมมาตร (วิธีหมุน Jacobi · เหมาะกับ ≤ 10×10) · symmetric eigen-decomposition
    คืน (values เรียงมากไปน้อย, vectors = list ของเวกเตอร์ · ส่วนประกอบที่ค่าสัมบูรณ์มากสุดเป็นบวก)"""
    n = len(A)
    a = [list(map(float, row)) for row in A]
    if any(abs(a[i][j] - a[j][i]) > 1e-12 * (1 + abs(a[i][j])) for i in range(n) for j in range(n)):
        raise ValueError("jacobi_eigen ต้องการเมทริกซ์สมมาตร")
    v = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    scale = max((abs(a[i][j]) for i in range(n) for j in range(n)), default=0.0) or 1.0
    for _ in range(max_sweeps):
        off = math.sqrt(math.fsum(a[i][j] ** 2 for i in range(n) for j in range(n) if i != j))
        if off <= tol * scale:
            break
        for p in range(n - 1):
            for q in range(p + 1, n):
                if abs(a[p][q]) <= 1e-300:
                    continue
                theta = (a[q][q] - a[p][p]) / (2.0 * a[p][q])
                t = (1.0 if theta >= 0 else -1.0) / (abs(theta) + math.sqrt(theta * theta + 1.0))
                c = 1.0 / math.sqrt(t * t + 1.0)
                s = t * c
                for k in range(n):              # A ← Jᵀ A J (คอลัมน์ แล้วแถว)
                    akp, akq = a[k][p], a[k][q]
                    a[k][p], a[k][q] = c * akp - s * akq, s * akp + c * akq
                for k in range(n):
                    apk, aqk = a[p][k], a[q][k]
                    a[p][k], a[q][k] = c * apk - s * aqk, s * apk + c * aqk
                for k in range(n):
                    vkp, vkq = v[k][p], v[k][q]
                    v[k][p], v[k][q] = c * vkp - s * vkq, s * vkp + c * vkq
    pairs = []
    for j in range(n):
        vec = [v[i][j] for i in range(n)]
        big = max(range(n), key=lambda i: abs(vec[i]))
        if vec[big] < 0:
            vec = [-u for u in vec]
        pairs.append((a[j][j], vec))
    pairs.sort(key=lambda t: -t[0])
    return [p[0] for p in pairs], [p[1] for p in pairs]


def pca(columns, standardize=False):
    """PCA ของหลายคอลัมน์ (เช่นผลตอบแทนรายวันของเหรียญ) · principal components via Jacobi
    standardize=True ใช้เมทริกซ์สหสัมพันธ์ · คืน values · vectors (loadings) · explained (สัดส่วน) · scores · cov"""
    cols = [list(c) for c in columns]
    if standardize:
        cols = [zscore(c) for c in cols]
    C = cov_matrix(cols)
    vals, vecs = jacobi_eigen(C)
    tot = math.fsum(vals)
    ms = [mean(c) for c in cols]
    n = len(cols[0])
    scores = [[math.fsum(vec[i] * (cols[i][t] - ms[i]) for i in range(len(cols))) for t in range(n)] for vec in vecs]
    return {"values": vals, "vectors": vecs, "explained": [x / tot for x in vals], "scores": scores, "cov": C}


# ═══════════════════════════ พอร์ต (portfolio) ═══════════════════════════


def portfolio_variance(weights, covm):
    """ความแปรปรวนของพอร์ต wᵀ Σ w · portfolio variance"""
    k = len(weights)
    return math.fsum(weights[i] * covm[i][j] * weights[j] for i in range(k) for j in range(k))


def portfolio_sd(weights, covm):
    """SD ของพอร์ต · portfolio standard deviation"""
    return math.sqrt(portfolio_variance(weights, covm))


# ═══════════════════════════ Kelly ═══════════════════════════


def kelly_growth(f, outcomes):
    """อัตราโตเฉลี่ยต่อรอบ Σ p·ln(1 + f·r) · expected log growth for fraction f (outcomes = [(p, r)])"""
    return math.fsum(p * math.log1p(f * r) for p, r in outcomes)


def kelly_discrete(outcomes, tol=1e-13):
    """สัดส่วน Kelly ของเหตุการณ์ไม่ต่อเนื่อง: f ที่ทำให้ Σ p·ln(1 + f·r) สูงสุด (หาด้วยการแบ่งครึ่งบนอนุพันธ์)
    simple Kelly for discrete outcomes [(prob, return per 1 unit staked)] · ห้ามยืม: 0 ≤ f < f_max (ไม่ให้ 1 + f·r ≤ 0)
    คืน f · growth · f_max · ค่าคาดหวัง (ถ้า ≤ 0 → f = 0)"""
    if abs(math.fsum(p for p, _ in outcomes) - 1.0) > 1e-9:
        raise ValueError("ความน่าจะเป็นต้องรวมได้ 1")
    ev = math.fsum(p * r for p, r in outcomes)
    worst = min(r for _, r in outcomes)
    f_max = -1.0 / worst if worst < 0 else float("inf")
    if ev <= 0:
        return {"f": 0.0, "growth": 0.0, "f_max": f_max, "ev": ev}
    d = lambda f: math.fsum(p * r / (1.0 + f * r) for p, r in outcomes)  # noqa: E731
    lo = 0.0
    hi = f_max * (1 - 1e-12) if f_max != float("inf") else 1.0
    if f_max == float("inf"):
        while d(hi) > 0:
            hi *= 2.0
            if hi > 1e12:
                raise ValueError("Kelly ไม่มีขอบบน (ไม่มีผลลบ)")
    while hi - lo > tol * max(1.0, hi):
        mid = (lo + hi) / 2.0
        if d(mid) > 0:
            lo = mid
        else:
            hi = mid
    f = (lo + hi) / 2.0
    return {"f": f, "growth": kelly_growth(f, outcomes), "f_max": f_max, "ev": ev}


# ═══════════════════════════ walk-forward ═══════════════════════════


def walk_forward(n, train, test, step=None, anchored=False):
    """แบ่งข้อมูลยาว n เป็นหน้าต่าง (ช่วงเลือก → ช่วงทดสอบ) เดินหน้าทีละ step (ค่าเริ่มต้น = test)
    walk-forward splitter · anchored=True: ช่วงเลือกเริ่มที่ 0 เสมอ (ยาวขึ้นเรื่อย ๆ)
    คืน [((train_start, train_end), (test_start, test_end))] แบบ half-open [start, end) · ช่วงทดสอบไม่ทับกันเมื่อ step ≥ test"""
    step = step or test
    if min(train, test, step) <= 0:
        raise ValueError("train, test, step ต้องเป็นบวก")
    out, s = [], 0
    while s + train + test <= n:
        out.append(((0 if anchored else s, s + train), (s + train, s + train + test)))
        s += step
    return out


# ═══════════════════════════ selftest ═══════════════════════════


def _close(a, b, tol, rel=True):
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(_close(u, v, tol, rel) for u, v in zip(a, b))
    scale = max(1.0, abs(b)) if rel else 1.0
    return abs(a - b) <= tol * scale


def selftest():
    import numpy as np
    ok, n_checks = True, 0

    def check(label, cond, detail=""):
        nonlocal ok, n_checks
        n_checks += 1
        if not cond:
            ok = False
            print(f"  ✗ {label} {detail}")

    rng = random.Random(20261115)
    T = 1e-9

    # ── 1) เทียบ numpy (1e-9) ──
    x = [rng.gauss(10, 2) for _ in range(200)]
    y = [3.0 + 1.7 * u + rng.gauss(0, 1.5) for u in x]
    X, Y = np.array(x), np.array(y)
    check("mean/var/sd/cov/corr", _close([mean(x), var(x), sd(x), cov(x, y), corr(x, y)],
                                         [X.mean(), X.var(ddof=1), X.std(ddof=1), np.cov(X, Y)[0, 1],
                                          np.corrcoef(X, Y)[0, 1]], T))
    r = ols(x, y)
    A = np.column_stack([np.ones_like(X), X])
    beta, *_ = np.linalg.lstsq(A, Y, rcond=None)
    res = Y - A @ beta
    s2 = res @ res / (len(Y) - 2)
    se = np.sqrt(np.diag(s2 * np.linalg.inv(A.T @ A)))
    r2 = 1 - (res @ res) / ((Y - Y.mean()) @ (Y - Y.mean()))
    check("ols slope/intercept/se/r2", _close([r["slope"], r["intercept"], r["se_slope"], r["se_intercept"], r["r2"]],
                                              [beta[1], beta[0], se[1], se[0], r2], T))
    check("ols residuals", _close(r["residuals"], list(res), T))
    z1 = [rng.gauss(0, 1) for _ in range(150)]
    z2 = [rng.gauss(0, 1) + 0.5 * a for a in z1]
    yy = [1 + 2 * a - 3 * b + rng.gauss(0, 0.3) for a, b in zip(z1, z2)]
    m = ols_multi([z1, z2], yy)
    A2 = np.column_stack([np.ones(150), z1, z2])
    b2, *_ = np.linalg.lstsq(A2, np.array(yy), rcond=None)
    e2 = np.array(yy) - A2 @ b2
    se2 = np.sqrt(np.diag(e2 @ e2 / (150 - 3) * np.linalg.inv(A2.T @ A2)))
    check("ols_multi coef/se", _close(m["coef"] + m["se"], list(b2) + list(se2), T))
    o = ols_origin(x, y)
    check("ols_origin", _close(o["slope"], float(X @ Y / (X @ X)), T))
    ar = [0.0]
    for _ in range(300):
        ar.append(0.8 * ar[-1] + rng.gauss(0, 1))
    f = ar1(ar)
    bb, *_ = np.linalg.lstsq(np.column_stack([np.ones(300), ar[:-1]]), np.array(ar[1:]), rcond=None)
    check("ar1 phi/c", _close([f["phi"], f["c"]], [bb[1], bb[0]], T))
    # ADF lag 0 และ lag 2 เทียบการถดถอยเดียวกันใน numpy
    for lags in (0, 2):
        a = adf(ar, lags=lags)
        dx = np.diff(ar)
        cols = [np.ones(len(dx) - lags), np.array(ar[lags:-1])] + [dx[lags - i:len(dx) - i] for i in range(1, lags + 1)]
        A3 = np.column_stack(cols)
        yv = dx[lags:]
        b3, *_ = np.linalg.lstsq(A3, yv, rcond=None)
        e3 = yv - A3 @ b3
        se3 = np.sqrt(np.diag(e3 @ e3 / (len(yv) - A3.shape[1]) * np.linalg.inv(A3.T @ A3)))
        check(f"adf lag {lags} stat", _close(a["stat"], b3[1] / se3[1], T), f"{a['stat']} vs {b3[1] / se3[1]}")
    check("rolling mean/sd", _close([v for v in rolling_mean(x, 20) if v is not None],
                                    list(np.convolve(X, np.ones(20) / 20, mode="valid")), T)
          and _close(rolling_sd(x, 20)[-1], float(X[-20:].std(ddof=1)), T))
    ro = rolling_ols(x, y, 50)
    check("rolling_ols", ro[48] is None and _close(ro[-1]["slope"], float(np.polyfit(X[-50:], Y[-50:], 1)[0]), T))
    # PCA: เทียบ numpy.linalg.eigh (ค่า · เวกเตอร์ถึงเครื่องหมาย) ขนาด 3, 6, 10
    for k in (3, 6, 10):
        cols = [[rng.gauss(0, 1) for _ in range(120)] for _ in range(k)]
        for i in range(1, k):
            cols[i] = [u + 0.6 * w for u, w in zip(cols[i], cols[i - 1])]
        C = np.cov(np.array(cols))
        w_np, v_np = np.linalg.eigh(C)
        w_np, v_np = w_np[::-1], v_np[:, ::-1]
        vals, vecs = jacobi_eigen(cov_matrix(cols))
        vec_ok = all(min(np.abs(np.array(vecs[j]) - v_np[:, j]).max(), np.abs(np.array(vecs[j]) + v_np[:, j]).max()) < 1e-9
                     for j in range(k))
        check(f"jacobi {k}×{k} values/vectors", _close(vals, list(w_np), T) and vec_ok)
    p = pca(cols[:3])
    check("pca explained sums to 1", _close(math.fsum(p["explained"]), 1.0, T))
    wts = [0.5, -0.3, 0.8]
    C3 = cov_matrix(cols[:3])
    check("portfolio_variance", _close(portfolio_variance(wts, C3), float(np.array(wts) @ np.array(C3) @ np.array(wts)), T))

    # ── 2) ค่าอ้างอิงที่ตีพิมพ์ ──
    cinf = adf_crit(10 ** 12)
    check("MacKinnon 2010 asymptotic c (N=1)", _close([cinf["1%"], cinf["5%"], cinf["10%"]], [-3.43035, -2.86154, -2.56677], 1e-6))
    # Fuller (1976) / Hamilton (1994) ตาราง B.6 case 2: τ_μ ที่ T = 25, 50, 100, 250, 500 (ค่าทศนิยม 2 ตำแหน่ง)
    fuller = {25: (-3.75, -3.00, -2.63), 50: (-3.58, -2.93, -2.60), 100: (-3.51, -2.89, -2.58),
              250: (-3.46, -2.88, -2.57), 500: (-3.44, -2.87, -2.57)}
    worst = max(abs(adf_crit(t)[k] - v) for t, vs in fuller.items() for k, v in zip(("1%", "5%", "10%"), vs))
    check("ค่าวิกฤต ADF เทียบตาราง Fuller (≤ 0.03)", worst <= 0.03, f"ต่างสุด {worst:.4f}")
    eg = adf_crit(10 ** 12, n_vars=2)
    check("MacKinnon 2010 EG N=2 asymptotic", _close([eg["1%"], eg["5%"], eg["10%"]], [-3.89644, -3.33613, -3.04445], 1e-6))
    pv = [adf_pvalue(cinf[k]) for k in ("1%", "5%", "10%")] + [adf_pvalue(eg[k], 2) for k in ("1%", "5%", "10%")]
    check("p-value ที่ค่าวิกฤตเชิงเส้นกำกับ ≈ 1% · 5% · 10% (±0.003)",
          _close(pv, [0.01, 0.05, 0.10, 0.01, 0.05, 0.10], 0.003, rel=False), f"{[round(v, 4) for v in pv]}")
    check("p-value ต่อเนื่องที่ τ*", abs(adf_pvalue(-1.61 - 1e-9) - adf_pvalue(-1.61 + 1e-9)) < 0.002
          and abs(adf_pvalue(-2.62 - 1e-9, 2) - adf_pvalue(-2.62 + 1e-9, 2)) < 0.002)
    check("p-value ขอบ", adf_pvalue(-30) == 0.0 and adf_pvalue(5) == 1.0)

    # ── 3) การจำลองที่รู้คำตอบ ──
    def ar_path(g, n, phi, s=1.0):
        v = g.gauss(0, s / math.sqrt(1 - phi * phi)) if phi < 1 else 0.0
        out = [v]
        for _ in range(n - 1):
            v = phi * v + g.gauss(0, s)
            out.append(v)
        return out
    g = random.Random(7)
    big = ar1(ar_path(g, 20000, 0.95))
    check("ar1 ข้อมูลยาว: φ 0.95 (±0.006)", abs(big["phi"] - 0.95) < 0.006, f"{big['phi']:.4f}")
    rej_rw = sum(adf(ar_path(g, 250, 1.0))["reject5"] for _ in range(600)) / 600
    check("ADF ขนาดการทดสอบ: random walk ปฏิเสธ ≈ 5% (2.5%–8%)", 0.025 <= rej_rw <= 0.08, f"{rej_rw:.3f}")
    rej_rw2 = sum(adf(ar_path(g, 250, 1.0), lags=2)["reject5"] for _ in range(400)) / 400
    check("ADF lag 2 ขนาดการทดสอบ ≈ 5% (2%–9%)", 0.02 <= rej_rw2 <= 0.09, f"{rej_rw2:.3f}")
    pw = sum(adf(ar_path(g, 250, 0.9))["reject5"] for _ in range(200)) / 200
    check("ADF อำนาจ: φ 0.9 n 250 ปฏิเสธ ≥ 80%", pw >= 0.8, f"{pw:.3f}")
    eg_null = 0
    for _ in range(300):
        xa, xb = ar_path(g, 250, 1.0), ar_path(g, 250, 1.0)
        eg_null += engle_granger(xa, xb)["reject5"]
    check("Engle–Granger: สองขาเดินสุ่มอิสระ ปฏิเสธ ≈ 5% (2%–9%)", 0.02 <= eg_null / 300 <= 0.09, f"{eg_null / 300:.3f}")
    xb = ar_path(g, 500, 1.0)
    sp = ar_path(g, 500, 0.85, 0.5)
    ya = [2.0 + 1.5 * u + e for u, e in zip(xb, sp)]
    e = engle_granger(ya, xb)
    check("Engle–Granger: มีเชือก φ 0.85 → ปฏิเสธ · h ≈ 1.5", e["reject5"] and abs(e["h"] - 1.5) < 0.05, f"h={e['h']:.3f}")
    cover, reps = 0, 400
    for _ in range(reps):
        fr = ar1(ar_path(g, 250, 0.9))
        ci = half_life_ci(fr["phi"], fr["se_phi"])
        cover += ci["phi_lo"] <= 0.9 <= ci["phi_hi"]
    check("ช่วง half-life (ผ่าน φ ± 1.96 SE) ครอบค่าจริง 88%–98%", 0.88 <= cover / reps <= 0.98, f"{cover / reps:.3f}")
    check("half_life(0.5) = 1 · (0.9) = 6.58 · (1) = inf", _close(half_life(0.5), 1.0, T)
          and abs(half_life(0.9) - 6.5788) < 1e-4 and half_life(1.0) == float("inf"))
    ou = ou_from_ar1(0.9, 0.2, 0.5)
    check("OU จาก AR(1): μ = 2 · half-life ตรง · SD นิ่ง", _close([ou["mu"], ou["half_life"], ou["sd_stationary"]],
                                                                [2.0, half_life(0.9), 0.5 / math.sqrt(0.19)], T))
    # Kalman: q = 0 → คือกำลังสองน้อยสุดแบบเวียน (สูตรปิด) · q > 0 ตาม h ที่ไหลได้ดีกว่า h คงที่
    xs = [g.uniform(1, 3) for _ in range(300)]
    ys = [1.3 * u + g.gauss(0, 0.2) for u in xs]
    kf = kalman_hedge(xs, ys, q=0.0, r=0.04, beta0=0.5, p0=10.0)
    exact = (0.5 * 0.04 / 10.0 + math.fsum(u * v for u, v in zip(xs, ys))) / (0.04 / 10.0 + math.fsum(u * u for u in xs))
    check("Kalman q=0 = least squares แบบเวียน (1e-9)", _close(kf["beta"][-1], exact, T))
    hs = [1.0 + 0.5 * t / 499 for t in range(500)]
    xs = [g.uniform(1, 3) for _ in range(500)]
    ys = [h * u + g.gauss(0, 0.1) for h, u in zip(hs, xs)]
    kf = kalman_hedge(xs, ys, q=1e-4, r=0.01, beta0=1.0, p0=1.0)
    hst = ols_origin(xs, ys)["slope"]
    rm_k = math.sqrt(mean([(b - h) ** 2 for b, h in zip(kf["beta"][50:], hs[50:])]))
    rm_s = math.sqrt(mean([(hst - h) ** 2 for h in hs[50:]]))
    check("Kalman ตาม h ที่ไหล 1.0→1.5 ดีกว่า h คงที่", rm_k < 0.5 * rm_s, f"{rm_k:.4f} vs {rm_s:.4f}")
    # Kelly
    k1 = kelly_discrete([(0.6, 1.0), (0.4, -1.0)])
    k2 = kelly_discrete([(0.55, 2.0), (0.45, -1.0)])
    check("Kelly สองผล: f = p − q/b", _close([k1["f"], k2["f"]], [0.2, 0.55 - 0.45 / 2.0], 1e-9))
    k3 = kelly_discrete([(0.5, 0.3), (0.3, -0.1), (0.2, -0.5)])
    gr = [kelly_growth(k3["f"] + dlt, [(0.5, 0.3), (0.3, -0.1), (0.2, -0.5)]) for dlt in (-1e-4, 0, 1e-4)]
    check("Kelly สามผล: จุดสูงสุดของอัตราโต", gr[1] >= gr[0] and gr[1] >= gr[2] and k3["f"] > 0)
    check("Kelly ค่าคาดหวังลบ → 0", kelly_discrete([(0.4, 1.0), (0.6, -1.0)])["f"] == 0.0)
    # walk-forward
    wf = walk_forward(100, 40, 20)
    check("walk_forward หน้าต่างเลื่อน", wf == [((0, 40), (40, 60)), ((20, 60), (60, 80)), ((40, 80), (80, 100))])
    wa = walk_forward(100, 40, 20, anchored=True)
    check("walk_forward anchored", [w[0] for w in wa] == [(0, 40), (0, 60), (0, 80)]
          and all(tr[1] == te[0] for tr, te in wa))
    # p-value แบบจำลอง: ข้อมูลยาว → ใกล้ MacKinnon 1994 (เชิงเส้นกำกับ) · ข้อมูลสั้น → เส้น 5% ต่ำกว่าตาราง asymptotic
    for st in (-3.43, -2.86, -2.3, -1.6):
        ps = adf_pvalue_sim(st, 500, worlds=2000, seed=7)
        check(f"ADF p แบบจำลอง 500 จุด ≈ MacKinnon ที่ {st} (±0.02)", abs(ps["pvalue"] - adf_pvalue(st)) <= 0.02,
              f"{ps['pvalue']:.4f} vs {adf_pvalue(st):.4f}")
    pe = adf_pvalue_sim(-3.34, 500, worlds=1000, seed=7, n_vars=2)
    check("EG p แบบจำลอง 500 จุด ≈ MacKinnon N=2 ที่ −3.34 (±0.025)", abs(pe["pvalue"] - adf_pvalue(-3.34, 2)) <= 0.025,
          f"{pe['pvalue']:.4f} vs {adf_pvalue(-3.34, 2):.4f}")
    sm = adf_pvalue_sim(-2.86, 11, worlds=4000, seed=1)
    check("ADF 11 จุด: เส้น 5% แบบจำลองใกล้ MacKinnon 2010 ที่ 10 แถว (±0.2) และต่ำกว่า −2.86 · p > asymptotic",
          abs(sm["crit"]["5%"] - adf_crit(10)["5%"]) <= 0.2 and sm["crit"]["5%"] < -2.86 and sm["pvalue"] > sm["asymptotic"],
          f"{sm['crit']['5%']:.3f} vs {adf_crit(10)['5%']:.3f}")
    check("adf_pvalue_sim: seed เดิมผลเดิม · world แทนได้", adf_pvalue_sim(-2.0, 30, 300, seed=3)["below"] ==
          adf_pvalue_sim(-2.0, 30, 300, seed=3, world=lambda s_, m: _rw_world(s_, m))["below"])
    print("selftest", f"ผ่าน ✓ ({n_checks} ข้อ · เทียบ numpy ≤ 1e-9 สัมพัทธ์ · ค่าวิกฤต MacKinnon 2010 / ตาราง Fuller ≤ 0.03 · "
          "p-value MacKinnon 1994 ±0.003 · p-value แบบจำลอง (adf_pvalue_sim) ≈ MacKinnon ที่ 500 จุด · จำลองที่รู้คำตอบ: ขนาด/อำนาจ ADF · EG · ช่วง half-life · Kalman · Kelly)"
          if ok else "ไม่ผ่าน ✗")
    return 0 if ok else 1


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        sys.exit(selftest())
    print(__doc__)
    sys.exit(2)
