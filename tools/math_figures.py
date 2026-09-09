#!/usr/bin/env python3
"""คำนวณตัวเลขที่ปรากฏในชุดคณิตศาสตร์ (เล่ม 2) ใหม่จากอินพุตในหนังสือ แล้วตรวจว่าข้อความ
ในไฟล์ HTML ยังตรงกับค่าที่คำนวณได้

ครอบคลุม: 2·A §2.1 β/α · §2.2 multiple regression + multicollinearity · §1.3 wᵀΣw ·
2·B §4.2½ min-variance · 2·C §5.5 DR portfolio · 2·D §9.4 Kalman (มือ + จำลอง) ·
2·F §14.6 logistic (ตาราง sigmoid + fit + calibration)

ใช้:  python3 tools/math_figures.py          → พิมพ์ค่าและตรวจทุกไฟล์ (exit 1 ถ้าไม่ตรง)
      python3 tools/math_figures.py --print  → พิมพ์ค่าอย่างเดียว
ต้องมี numpy (pip install numpy) เพราะ 2·D/2·F ใช้สายสุ่มของ numpy.random.default_rng
"""
import math
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
CHECKS = []  # (file, label, expected substring)


def expect(file, label, text):
    CHECKS.append((file, label, text))


def ols(X, y):
    beta = np.linalg.solve(X.T @ X, X.T @ y)
    res = y - X @ beta
    n, k = X.shape
    s2 = res @ res / (n - k)
    se = np.sqrt(np.diag(s2 * np.linalg.inv(X.T @ X)))
    r2 = 1 - (res @ res) / ((y - y.mean()) @ (y - y.mean()))
    return beta, se, r2


# ── 2·A §2.1 simple regression (6 เดือน) ────────────────────────────────
mkt6 = np.array([3, -2, 5, -1, 2, -4]) / 100
stk6 = np.array([5, -4, 7, 0, 2, -7]) / 100
cov = np.cov(mkt6, stk6, ddof=1)[0, 1]
var = np.var(mkt6, ddof=1)
b21 = cov / var
a21 = stk6.mean() - b21 * mkt6.mean()
print(f"2·A §2.1  Cov={cov:.6f} Var={var:.6f} β={b21:.4f} α={a21:.5f}")
expect("math-part4.html", "§2.1 Cov", f"{cov:.6f}")
expect("math-part4.html", "§2.1 Var", f"{var:.6f}")
expect("math-part4.html", "§2.1 β", f"{b21:.2f}")
expect("math-part4.html", "§2.1 β polyfit", f"{b21:.4f}")

# ── 2·A §1.3 wᵀΣw ────────────────────────────────────────────────────────
w = np.array([0.5, 0.3, 0.2]); sd = np.array([0.20, 0.15, 0.30])
Corr = np.array([[1, .3, .2], [.3, 1, .5], [.2, .5, 1]])
sp = math.sqrt(w @ (np.outer(sd, sd) * Corr) @ w)
print(f"2·A §1.3  σ_p={sp*100:.2f}%  เฉลี่ยถ่วง={w@sd*100:.2f}%")
expect("math-part4.html", "§1.3 σ_p", f"{sp*100:.2f}%")
expect("math-part4.html", "§1.3 เฉลี่ยถ่วง", f"{w@sd*100:.2f}%")
s2p = 0.6**2 * 0.04 + 2 * 0.6 * 0.4 * 0.01 + 0.4**2 * 0.09
expect("math-part4.html", "§1.3 2 หุ้น", f"{math.sqrt(s2p)*100:.1f}%")

# ── 2·A §1.4 PCA — 2×2 ด้วยมือ และ 5 ช่วงอายุ ────────────────────────────
C2 = np.array([[1, .8], [.8, 1]]); l2, v2 = np.linalg.eigh(C2)
expect("math-part4.html", "§1.4 λ 2×2", f"λ₁ = {l2[1]:.1f}    λ₂ = {l2[0]:.1f}")
expect("math-part4.html", "§1.4 % 2×2", f"PC1 อธิบาย {l2[1]:.1f} / 2.0 = {l2[1]/2*100:.0f}%")
expect("math-part4.html", "§1.4 v₁ 2×2", f"[{abs(v2[0,1]):.2f}, {abs(v2[1,1]):.2f}]")
w1 = np.array([1, 1]) / np.sqrt(2); w2 = np.array([1, -1]) / np.sqrt(2)
expect("math-part4.html", "§1.4 wᵀΣw", f"= {w1 @ C2 @ w1:.1f} และ (1 + 1 − 2 × 0.8)/2 = {w2 @ C2 @ w2:.1f}")
C5p = np.array([[1, .95, .88, .80, .72], [.95, 1, .96, .90, .83], [.88, .96, 1, .97, .92],
                [.80, .90, .97, 1, .97], [.72, .83, .92, .97, 1]])
l5, v5 = np.linalg.eigh(C5p); pct5 = l5[::-1] / l5.sum() * 100; cum5 = np.cumsum(pct5)
print(f"2·A §1.4  2×2 λ={l2[::-1]} · 5×5 %={np.round(pct5,2)} PC1={np.round(v5[:,-1],2)} PC2={np.round(v5[:,-2],2)} PC3={np.round(v5[:,-3],2)}")
for i_ in range(5):
    expect("math-part4.html", f"§1.4 PC{i_+1} %", f"PC{i_+1}: {pct5[i_]:5.2f}%   (สะสม {cum5[i_]:5.2f}%)")
um1 = lambda v: f"{v:.2f}".replace("-", "−")
for k_, name_ in ((-1, "PC1"), (-2, "PC2"), (-3, "PC3")):
    expect("math-part4.html", f"§1.4 {name_} vector", f"{name_} = [" + ", ".join(um1(x) for x in v5[:, k_]) + "]")

# ── 2·A §2.2 multiple regression ─────────────────────────────────────────
mkt = np.array([3, -2, 5, -1, 2, -4, 1, 3]) / 100
size = np.array([1, 2, -1, 0, 3, -2, 1, -1]) / 100
val = np.array([-1, 1, 2, 1, -2, 0, -1, 2]) / 100
stk = np.array([4.6, -1.0, 6.2, -0.6, 4.1, -6.3, 1.9, 2.3]) / 100
X = np.column_stack([np.ones(8), mkt, size, val])
beta, se, r2 = ols(X, stk)
b1s, a1s = np.polyfit(mkt, stk, 1)
r2s = 1 - ((stk - (a1s + b1s * mkt))**2).sum() / ((stk - stk.mean())**2).sum()
grow = -val + np.array([0.1, -0.1, 0, 0.1, -0.1, 0.1, 0, -0.1]) / 100
X2 = np.column_stack([X, grow])
beta2, se2, _ = ols(X2, stk)
XtX = (X * 100).T @ (X * 100)  # ในหนังสือแสดงหน่วย % (ยกเว้นคอลัมน์ 1)
XtX[0, 0] = 8; XtX[0, 1:] /= 100; XtX[1:, 0] /= 100
Xty = (X * 100).T @ (stk * 100); Xty[0] /= 100
print(f"2·A §2.2  β={np.round(beta,4)} (β₀={beta[0]*100:.3f}%) R²={r2:.4f} SE={np.round(se,3)} t={np.round(beta/se,2)}")
print(f"          simple β={b1s:.4f} α={a1s:.4f} R²={r2s:.4f} | +growth β={np.round(beta2,3)} SE={np.round(se2,2)} ρ(val,grow)={np.corrcoef(val,grow)[0,1]:.3f}")
print(f"          XᵀX diag={np.round(np.diag(XtX),1)} Xᵀy={np.round(Xty,1)}")
expect("math-part4.html", "§2.2 β₁", f"{beta[1]:.3f}")
expect("math-part4.html", "§2.2 β₂", f"{beta[2]:.3f}")
expect("math-part4.html", "§2.2 β₃", f"{beta[3]:.3f}")
expect("math-part4.html", "§2.2 β₀ (%)", f"{beta[0]*100:.3f}")
expect("math-part4.html", "§2.2 R²", f"{r2:.3f}")
expect("math-part4.html", "§2.2 t ตลาด", f"{beta[1]/se[1]:.1f}")
expect("math-part4.html", "§2.2 t ขนาด", f"{beta[2]/se[2]:.2f}")
expect("math-part4.html", "§2.2 β ตลาดเดี่ยว", f"{b1s:.3f}")
expect("math-part4.html", "§2.2 R² เดี่ยว", f"{r2s:.3f}")
expect("math-part4.html", "§2.2 β₃ หลังเติม", f"{beta2[3]:.3f}")
expect("math-part4.html", "§2.2 β₄ growth", f"{beta2[4]:.3f}")
expect("math-part4.html", "§2.2 SE₃ หลังเติม", f"{se2[3]:.2f}")
expect("math-part4.html", "§2.2 ρ(val,grow)", f"{np.corrcoef(val,grow)[0,1]:.3f}".replace("-", "−"))
expect("math-part4.html", "§2.2 numpy β", f"[{beta[0]:.4f} {beta[1]:.4f} {beta[2]:.4f} {beta[3]:.4f}]")
expect("math-part4.html", "§2.2 numpy R²", f"R² = {r2:.4f}")
um4 = lambda v, f: f"{v:{f}}".replace("-", "−")
expect("math-part4.html", "§2.2 x₄ series", "x₄ = [" + ", ".join(("+" if v > 0 else "") + um4(round(v, 1), ".1f") for v in grow * 100) + "]")
expect("math-part4.html", "§2.2 β₁ หลังเติม", f"β₁ (ตลาด) = {beta2[1]:.3f}")
expect("math-part4.html", "§2.2 β₂ หลังเติม", f"β₂ (ขนาด) = {beta2[2]:.3f}")
expect("math-part4.html", "§2.2 SE₄", f"SE = {se2[4]:.2f}")
C4 = np.corrcoef([mkt, size, val])
expect("math-part4.html", "§2.2 ρ ปัจจัย", f"ρ = {C4[0,1]:.2f} และ {C4[0,2]:.2f}")
expect("math-part4.html", "§2.2 ρ ขนาด-มูลค่า", um4(C4[1,2], ".2f"))
Xd = np.column_stack([np.ones(8), mkt, size]); bd, sed, r2d = ols(Xd, stk)
expect("math-part4.html", "§2.2 ✍️ β ตลาด", f"1.230 → {bd[1]:.3f}")
expect("math-part4.html", "§2.2 ✍️ β ขนาด", f"0.670 → {bd[2]:.3f}")
expect("math-part4.html", "§2.2 ✍️ R²", f"R² {r2:.4f} → {r2d:.4f} ลดแค่ {r2 - r2d:.4f}")

# ── 2·B §4.2½ min-variance 2 สินทรัพย์ ──────────────────────────────────
sA, sB, rho = .20, .10, .2
covAB = rho * sA * sB
wA = (sB**2 - covAB) / (sA**2 + sB**2 - 2 * covAB); wB = 1 - wA
ret = wA * .10 + wB * .06
var_p = wA**2 * sA**2 + wB**2 * sB**2 + 2 * wA * wB * covAB
print(f"2·B §4.2½ w_A={wA:.4f} ผลตอบแทน={ret*100:.2f}% σ={math.sqrt(var_p)*100:.2f}%")
expect("math-part5.html", "min-var w_A", f"{wA:.4f}")
expect("math-part5.html", "min-var ret", f"{ret*100:.2f}%")
expect("math-part5.html", "min-var σ", f"{math.sqrt(var_p)*100:.2f}%")

# ── 2·C §5.5 DR portfolio ────────────────────────────────────────────────
C5 = np.array([[1, .86, .42, -.05, -.30], [.86, 1, .38, -.02, -.26], [.42, .38, 1, .10, -.44],
               [-.05, -.02, .10, 1, .18], [-.30, -.26, -.44, .18, 1]])
sd5 = np.array([.30, .28, .20, .15, .05]); S5 = np.outer(sd5, sd5) * C5
iu = np.triu_indices(5, 1); rho_avg = C5[iu].mean()
out = []
for wts in ([.2] * 5, [.4, .4, .1, .05, .05]):
    wv = np.array(wts); spv = math.sqrt(wv @ S5 @ wv); out.append((spv, (wv @ sd5) / spv))
print(f"2·C §5.5  ρ เฉลี่ย={rho_avg:.3f} เท่ากัน σ={out[0][0]*100:.1f}% DR={out[0][1]:.2f} | เทค σ={out[1][0]*100:.1f}% DR={out[1][1]:.2f} สูงขึ้น {out[1][0]/out[0][0]*100-100:.0f}%")
expect("math-part8.html", "§5.5 ρ เฉลี่ย", f"{rho_avg:.3f}")
expect("math-part8.html", "§5.5 σ เท่ากัน", f"{out[0][0]*100:.1f}%")
expect("math-part8.html", "§5.5 σ เทค", f"{out[1][0]*100:.1f}%")
expect("math-part8.html", "§5.5 สูงขึ้น", f"สูงขึ้น {out[1][0]/out[0][0]*100-100:.0f}%")
expect("math-part8.html", "§5.5 DR เท่ากัน", f"DR = {out[0][1]:.2f}")
expect("math-part8.html", "§5.5 DR เทค", f"DR = {out[1][1]:.2f}")

# ── 2·D §9.4 Kalman: เดินเลขมือ ──────────────────────────────────────────
b, P, Q, R = 1.50, 0.01, 1e-4, 1.0
hand = []
for A, B in ((100, 152.0), (101, 151.0)):
    Pp = P + Q; K = Pp * A / (A * A * Pp + R); inn = B - b * A
    b = b + K * inn; P = (1 - K * A) * Pp; hand.append((Pp, K, K * A, inn, b, P))
print(f"2·D §9.4  วัน1 K={hand[0][1]:.6f} β̂={hand[0][4]:.6f} P={hand[0][5]:.7f} | วัน2 K={hand[1][1]:.6f} β̂={hand[1][4]:.6f} P={hand[1][5]:.7f} ±{math.sqrt(hand[1][5]):.4f}")
expect("math-part9.html", "Kalman K₁", f"{hand[0][1]:.6f}")
expect("math-part9.html", "Kalman β̂₁", f"{hand[0][4]:.6f}")
expect("math-part9.html", "Kalman K₂", f"{hand[1][1]:.6f}")
expect("math-part9.html", "Kalman β̂₂", f"{hand[1][4]:.6f}")
expect("math-part9.html", "Kalman ±√P₂", f"± {math.sqrt(hand[1][5]):.4f}")

# ── 2·D §9.4 Kalman: จำลองคู่ A/B ของ §9.1 ───────────────────────────────
rng = np.random.default_rng(0); n = 500
A = 100 + np.cumsum(rng.normal(0, 1, n)); Bs = 5.0 + 1.5 * A + rng.normal(0, 2, n)
b, P = 1.0, 1.0; Q, R = 1e-6, 4.0; bk = np.empty(n)
for t in range(n):
    Pp = P + Q; K = Pp * A[t] / (A[t]**2 * Pp + R); b += K * (Bs[t] - b * A[t]); P = (1 - K * A[t]) * Pp; bk[t] = b
ols_b = np.polyfit(A, Bs, 1)[0]; ols_noint = (A @ Bs) / (A @ A)
print(f"          จำลอง: β̂[0]={bk[0]:.4f} β̂[499]={bk[-1]:.4f} OLS={ols_b:.4f} OLS ไม่มี α={ols_noint:.4f}")
expect("math-part9.html", "OLS β §9.1", f"{ols_b:.4f}")
expect("math-part9.html", "Kalman β̂ สุดท้าย", f"{bk[-1]:.4f}")
expect("math-part9.html", "OLS ไม่มี α", f"{ols_noint:.4f}")

# ── 2·F §14.6 logistic ───────────────────────────────────────────────────
b0, b1 = -0.2, 0.8
print("2·F §14.6 ตาราง sigmoid:", end=" ")
for x in (0, 1, 2, -1):
    z = b0 + b1 * x; p = 1 / (1 + math.exp(-z)); print(f"x={x}: P={p:.4f}", end=" ")
    expect("math-part11.html", f"sigmoid x={x}", f"{p:.4f}")
print(f"| odds ratio e^0.8={math.exp(0.8):.4f}")
expect("math-part11.html", "odds ratio", f"{math.exp(0.8):.4f}")


def fit_logit(Xf, y, C=1.0, iters=50):
    """sklearn objective: ½‖β‖² + C·logloss, intercept ไม่ถูกปรับ (Newton)"""
    Xa = np.column_stack([np.ones(len(y)), Xf]); k = Xa.shape[1]
    theta = np.zeros(k); reg = np.eye(k); reg[0, 0] = 0
    for _ in range(iters):
        p = 1 / (1 + np.exp(-Xa @ theta))
        g = C * Xa.T @ (p - y) + reg @ theta
        H = C * (Xa.T * (p * (1 - p))) @ Xa + reg
        theta -= np.linalg.solve(H, g)
    return theta


rng = np.random.default_rng(7); n = 400
Xl = rng.normal(0, 1, (n, 2)); noise = rng.normal(0, 1, n)
yl = (0.8 * Xl[:, 0] - 0.5 * Xl[:, 1] + noise > 0).astype(int)
th = fit_logit(Xl, yl)
pin = 1 / (1 + np.exp(-(th[0] + Xl @ th[1:])))
rg = np.random.default_rng(77); X2l = rg.normal(0, 1, (2000, 2))
y2 = (0.8 * X2l[:, 0] - 0.5 * X2l[:, 1] + rg.normal(0, 1, 2000) > 0).astype(int)
p2 = 1 / (1 + np.exp(-(th[0] + X2l @ th[1:])))
print(f"          fit: coef={np.round(th[1:],3)} intercept={th[0]:.2f} acc in={((pin>0.5)==yl).mean():.3f} out={((p2>0.5)==y2).mean():.3f} สัดส่วนขึ้น={yl.mean():.4f}")
expect("math-part11.html", "logit coef₁", f"{th[1]:.3f}")
expect("math-part11.html", "logit coef₂", f"{th[2]:.3f}")
expect("math-part11.html", "logit acc in", f"{((pin>0.5)==yl).mean():.2f}")
expect("math-part11.html", "logit acc out", f"{((p2>0.5)==y2).mean():.3f}")
edges = [0, .2, .4, .6, .8, 1.01]
for lo, hi in zip(edges[:-1], edges[1:]):
    m = (p2 >= lo) & (p2 < hi)
    print(f"          [{lo:.1f},{hi:.1f}) n={m.sum()} ทำนาย {p2[m].mean():.3f} เกิดจริง {y2[m].mean():.3f}")
    expect("math-part11.html", f"calibration [{lo:.1f},{hi:.1f})", f"n={m.sum():4d}  ทำนายเฉลี่ย {p2[m].mean():.3f}  เกิดจริง {y2[m].mean():.3f}")

# ── 2·F §13.5 Bayes: Beta-Binomial (สูตรตรงสำหรับ a, b จำนวนเต็ม) ─────────
from math import comb


def beta_cdf_int(x, a, b):
    """I_x(a,b) = P(Binomial(a+b−1, x) ≥ a) สำหรับ a, b จำนวนเต็ม"""
    n_ = a + b - 1
    return sum(comb(n_, k) * x**k * (1 - x)**(n_ - k) for k in range(a, n_ + 1))


def beta_q(pr, a, b):
    lo, hi = 0.0, 1.0
    for _ in range(60):
        m = (lo + hi) / 2
        if beta_cdf_int(m, a, b) < pr: lo = m
        else: hi = m
    return (lo + hi) / 2


print("2·F §13.5 Beta-Binomial:", end=" ")
for a, b in ((59, 43), (69, 51), (581, 421), (591, 429), (168, 132)):
    mean = a / (a + b); lo, hi = beta_q(.025, a, b), beta_q(.975, a, b); pgt = 1 - beta_cdf_int(.55, a, b)
    print(f"Beta({a},{b}) mean={mean:.3f} [{lo:.3f}, {hi:.3f}] P>0.55={pgt:.3f}", end=" | ")
    expect("math-part11.html", f"Beta({a},{b}) mean", f"{mean:.3f}")
    if (a, b) != (168, 132):   # กล่อง ❌ รายงานแค่ค่าเฉลี่ยกับ P ไม่มีช่วง
        expect("math-part11.html", f"Beta({a},{b}) CrI", f"[{lo:.3f}, {hi:.3f}]")
    expect("math-part11.html", f"Beta({a},{b}) P>0.55", f"{pgt:.3f}")
print()
# ✍️: flat prior, 58% ต่อเนื่อง — กี่ไม้จึง P(p>0.55) ≥ 0.95
for n_ in (700, 750):
    k_ = round(0.58 * n_); pgt = 1 - beta_cdf_int(.55, 1 + k_, 1 + n_ - k_)
    print(f"          n={n_} k={k_} P>0.55={pgt:.4f}")
expect("math-part11.html", "✍️ 750 ไม้", f"{1 - beta_cdf_int(.55, 436, 316):.3f}")

# ── 2·D §9.5 VECM บนคู่ A/B ของ §9.1 ──────────────────────────────────────
rng = np.random.default_rng(0); n = 500
A = 100 + np.cumsum(rng.normal(0, 1, n)); Bs = 5.0 + 1.5 * A + rng.normal(0, 2, n)
bta, alp = np.polyfit(A, Bs, 1); spr = Bs - (alp + bta * A)
dA, dB = np.diff(A), np.diff(Bs)
Xv = np.column_stack([np.ones(n - 2), spr[1:-1], dA[:-1], dB[:-1]])


def ols_t(Xm, y):
    bb = np.linalg.lstsq(Xm, y, rcond=None)[0]; rr = y - Xm @ bb
    s2_ = rr @ rr / (len(y) - Xm.shape[1]); se_ = np.sqrt(np.diag(s2_ * np.linalg.inv(Xm.T @ Xm)))
    return bb, bb / se_


bB, tB = ols_t(Xv, dB[1:]); bA, tA = ols_t(Xv, dA[1:])
ident = bB[1] - bta * bA[1]; phi_v = 1 + ident; hl = -math.log(2) / math.log(abs(phi_v))
X2v = np.column_stack([np.ones(n - 1), spr[:-1]]); b2, t2 = ols_t(X2v, dB); a2, ta2 = ols_t(X2v, dA)
um = lambda v, f: f"{v:{f}}".replace("-", "−")
print(f"2·D §9.5  γ_B={um(bB[1],'.4f')} t={um(tB[1],'.2f')} γ_A={bA[1]:+.4f} t={tA[1]:+.2f} identity={um(ident,'.4f')} φ={phi_v:.4f} HL={hl:.2f} | ECM γ_B={um(b2[1],'.4f')} t={um(t2[1],'.2f')} γ_A={a2[1]:+.4f} identity={um(b2[1]-bta*a2[1],'.4f')}")
expect("math-part9.html", "VECM γ_B", um(bB[1], '.4f'))
expect("math-part9.html", "VECM t γ_B", um(tB[1], '.2f'))
expect("math-part9.html", "VECM γ_A", f"+{bA[1]:.4f}")
expect("math-part9.html", "VECM t γ_A", f"+{tA[1]:.2f}")
expect("math-part9.html", "VECM identity", um(ident, '.4f'))
expect("math-part9.html", "VECM half-life", f"{hl:.2f} วัน")
expect("math-part9.html", "ECM γ_B", um(b2[1], '.4f'))
expect("math-part9.html", "ECM t", um(t2[1], '.2f'))
expect("math-part9.html", "ECM identity", um(b2[1] - bta * a2[1], '.4f'))
# SE ของ φ̂ สองตัว (ใช้ในกล่อง ✅ อ่านผลลัพธ์ — "0.15 กับ 0.20 วัน อยู่ในช่วงคลาดเคลื่อนของกันและกัน")
bS_, tS_ = ols_t(Xv, np.diff(spr)[1:]); se_phi_vecm = bS_[1] / tS_[1]
b1_, t1_ = ols_t(X2v, np.diff(spr)); se_phi_ar1 = b1_[1] / t1_[1]
print(f"          SE(φ̂) VECM={se_phi_vecm:.3f} AR(1)={se_phi_ar1:.3f} · Δφ̂={abs(bS_[1]-b1_[1]):.3f}")
expect("math-part9.html", "SE φ̂ VECM/AR1", f"SE ของมันคือ {se_phi_vecm:.3f} (VECM) กับ {se_phi_ar1:.3f} (AR(1))")
expect("math-part9.html", "Δφ̂", f"ต่างกัน {abs(bS_[1]-b1_[1]):.3f} ขณะที่")
# ✍️ 2·D §9.5 — ตัวจำลองที่ A ปรับตัวจริง (สุ่ม u ทั้งชุดก่อน แล้ว e · s[0]=0 · A[0]=100)
rng = np.random.default_rng(0)
u_ = rng.normal(0, 2, n); e_ = rng.normal(0, 1, n)
s_ = np.zeros(n); A_ = np.zeros(n); A_[0] = 100
for t_ in range(1, n):
    s_[t_] = 0.7 * s_[t_ - 1] + u_[t_]; A_[t_] = A_[t_ - 1] + 0.1 * s_[t_ - 1] + e_[t_]
B_ = 5 + 1.5 * A_ + s_
bt_, al_ = np.polyfit(A_, B_, 1); sp_ = B_ - (al_ + bt_ * A_); dA_, dB_ = np.diff(A_), np.diff(B_)
Xw = np.column_stack([np.ones(n - 2), sp_[1:-1], dA_[:-1], dB_[:-1]])
wB, wtB = ols_t(Xw, dB_[1:]); wA, wtA = ols_t(Xw, dA_[1:]); wid = wB[1] - bt_ * wA[1]
print(f"          ✍️ β̂={bt_:.4f} γ_B={um(wB[1],'.4f')} t={um(wtB[1],'.2f')} γ_A=+{wA[1]:.4f} t=+{wtA[1]:.2f} identity={um(wid,'.4f')} φ̂={1+wid:.3f} HL={-math.log(2)/math.log(1+wid):.2f}")
expect("math-part9.html", "✍️ β̂", f"β̂ = {bt_:.4f}")
expect("math-part9.html", "✍️ γ_B", f"<strong>{um(wB[1],'.4f')}</strong> (t = {um(wtB[1],'.2f')})")
expect("math-part9.html", "✍️ γ_A", f"<strong>+{wA[1]:.4f}</strong> (t = +{wtA[1]:.2f})")
expect("math-part9.html", "✍️ identity", f"<strong>{um(wid,'.4f')}</strong> = φ − 1")
expect("math-part9.html", "✍️ φ̂/HL", f"φ̂ = {1+wid:.3f} → ครึ่งชีวิต {-math.log(2)/math.log(1+wid):.2f} วัน")
# 2·F §13.5 — เอกลักษณ์ Beta ↔ Binomial ที่ยกเป็นตัวอย่างในกล่อง 🧮
p_id = sum(math.comb(101, j) * 0.55 ** j * 0.45 ** (101 - j) for j in range(0, 59))
expect("math-part11.html", "Beta↔Binomial ตัวอย่าง", f"P(Binomial(101, 0.55) ≤ 58) = {p_id:.3f}")


# ── Arb เล่ม 1 §1.5 บันไดสามขั้น — σ_ε/√N และ P(v(T)<0) = Φ(−(μ/σ)√T) ────────
Phi_ = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))
for N_ in (1, 2, 10, 100, 1000):
    v_ = 30 / math.sqrt(N_)
    expect("arb-part1.html", f"§1.5 σ_ε/√N N={N_}", f"<td>{v_:.1f}%</td>" if N_ in (1, 100) else f"<td>{v_:.2f}%</td>")
for T_ in (1, 20, 100, 252, 400, 1000):
    expect("arb-part1.html", f"§1.5 P(v<0) T={T_}", f"<td>{100 * Phi_(-0.1 * math.sqrt(T_)):.2f}%</td>")
expect("arb-part1.html", "§1.5 ไตรมาส", f"63 วัน โอกาสไตรมาสติดลบ {100 * Phi_(-0.1 * math.sqrt(63)):.1f}%")
expect("arb-part1.html", "§1.5 Sharpe ต่อปี", f"ต่อปี ≈ {0.1 * math.sqrt(252):.2f}")
expect("arb-part1.html", "§1.5 pairs กระจาย", f"กระจายได้แค่ {100 * (1 - 1 / math.sqrt(2)):.0f}%")
print(f"Arb §1.5  σ/√N: " + " ".join(f"{30/math.sqrt(n):.2f}" for n in (1,2,10,100,1000)) + " · P(v<0): " + " ".join(f"{100*Phi_(-0.1*math.sqrt(t)):.2f}" for t in (1,20,100,252,400,1000)))


# ── 2·D §9.1 ครึ่งชีวิต ≠ เวลาปิดไม้ — first passage ของ OU (φ ของ §8.4½) ─────────
rng_fp = np.random.default_rng(1); phi_fp = 0.9048; hl_fp = -math.log(2) / math.log(phi_fp)
n_fp = 200_000; x_fp = np.full(n_fp, 2.0); t_fp = np.zeros(n_fp); alive = np.ones(n_fp, bool)
sig_fp = math.sqrt(1 - phi_fp ** 2)  # ให้ SD นิ่งของ spread = 1 → เข้าที่ 2 SD
for k_ in range(1, 5001):
    x_fp = phi_fp * x_fp + sig_fp * rng_fp.standard_normal(n_fp)
    hit = alive & (x_fp <= 0); t_fp[hit] = k_; alive &= ~hit
    if not alive.any():
        break
print(f"2·D §9.1  first passage 2SD→0: HL={hl_fp:.2f} median={np.median(t_fp):.0f} mean={t_fp.mean():.1f} p90={np.percentile(t_fp,90):.0f} p95={np.percentile(t_fp,95):.0f} ≤HL={100*(t_fp<=hl_fp).mean():.0f}%")
expect("math-part9.html", "first passage HL", f"ครึ่งชีวิต {hl_fp:.2f} วัน")
expect("math-part9.html", "first passage median", f"มัธยฐาน <strong>{np.median(t_fp):.0f} วัน</strong> ค่าเฉลี่ย {t_fp.mean():.1f} วัน")
expect("math-part9.html", "first passage p90/p95", f"1 ใน 10 ไม้นานเกิน {np.percentile(t_fp,90):.0f} วัน · 1 ใน 20 เกิน {np.percentile(t_fp,95):.0f} วัน")
expect("math-part9.html", "first passage ≤HL", f"มีแค่ {100*(t_fp<=hl_fp).mean():.0f}% ที่ปิดภายในหนึ่งครึ่งชีวิต")


# ── 2·A §1.6 Factor or Noise — MP edges · parallel analysis ปอกทีละชั้น · ความนิ่ง ──────
p6 = 5
def eig_corr6(Xm):
    return np.linalg.eigvalsh(np.corrcoef(Xm.T))[::-1]
def vec_corr6(Xm):
    return np.linalg.eigh(np.corrcoef(Xm.T))[1][:, ::-1]
def noise_p95(pp, nn, sims=1000, seed=1):
    r_ = np.random.default_rng(seed)
    arr = np.array([eig_corr6(r_.standard_normal((nn, pp)))[0] for _ in range(sims)])
    return np.percentile(arr, 95), np.median(arr), arr.max()
def peel(lam, nn):
    out, used = [], 0.0
    for k in range(len(lam) - 1):
        dims = len(lam) - k
        base = (len(lam) - used) / dims * noise_p95(dims, nn)[0]
        out.append((lam[k], base, lam[k] > base))
        if lam[k] <= base:
            break
        used += lam[k]
    return out
lp6 = (1 + math.sqrt(p6 / 250)) ** 2; lm6 = (1 - math.sqrt(p6 / 250)) ** 2
expect("math-part4.html", "§1.6 λ₊", f"(1 + 0.1414)² = {lp6:.3f}")
expect("math-part4.html", "§1.6 λ₋", f"λ₋ = {lm6:.3f}")
rng6 = np.random.default_rng(0); noise6 = rng6.standard_normal((250, p6)); ln = eig_corr6(noise6); wn6 = vec_corr6(noise6)
expect("math-part4.html", "§1.6 noise eig", "<td>" + "</td><td>".join(f"{v:.3f}" for v in ln) + "</td>")
expect("math-part4.html", "§1.6 noise %", f"<strong>{ln[0]/5*100:.1f}%</strong></td><td><strong>{ln[1]/5*100:.1f}%</strong>")
expect("math-part4.html", "§1.6 noise cum", f"{np.cumsum(ln)[1]/5*100:.1f}%</td><td>{np.cumsum(ln)[2]/5*100:.1f}%</td><td>{np.cumsum(ln)[3]/5*100:.1f}%")
sgn = 1 if wn6[0, 1] > 0 else -1
expect("math-part4.html", "§1.6 noise PC2", "[" + ", ".join(f"{sgn*x:.2f}".replace("-", "−") for x in wn6[:, 1]) + "]")
q95, qmed, qmax = noise_p95(5, 250)
expect("math-part4.html", "§1.6 PA p95", f"เปอร์เซ็นไทล์ 95 = <strong>{q95:.3f}</strong> (ค่ากลาง {qmed:.3f} · ใหญ่สุดที่เจอใน 1,000 ชุด {qmax:.2f})")
pl = peel(ln, 250)
expect("math-part4.html", "§1.6 noise peel", f"ฐานของ λ₂ = {(5-ln[0])/4:.3f} × {noise_p95(4,250)[0]:.3f} = <strong>{pl[1][1]:.3f}</strong>")
r7 = np.random.default_rng(7); fp = sum(eig_corr6(r7.standard_normal((250, p6)))[0] > q95 for _ in range(2000)) / 2000
expect("math-part4.html", "§1.6 false positive", f"ผ่านข้อแรก {fp*100:.2f}%")
def make6(nn, seed=2):
    r_ = np.random.default_rng(seed); f1 = r_.standard_normal(nn); f2 = r_.standard_normal(nn)
    return np.outer(f1, np.full(p6, .8)) + np.outer(f2, .2 * np.array([-2, -1, 0, 1, 2.])) + r_.standard_normal((nn, p6))
for nn in (250, 2500):
    Xs = make6(nn); ls = eig_corr6(Xs); ps = peel(ls, nn); ws = vec_corr6(Xs)
    cells = " · ".join(f"{l:.3f} · {b:.3f} {'✓' if ok else '✗'}" for l, b, ok in ps)
    expect("math-part4.html", f"§1.6 struct n={nn}", "<td>" + "</td><td>".join(f"{l:.3f} · {b:.3f} {'✓' if ok else '✗'}" for l, b, ok in ps) + "</td>")
    sg = 1 if ws[0, 1] < 0 else -1
    expect("math-part4.html", f"§1.6 struct PC2 n={nn}", "[" + ", ".join(f"{sg*x:.2f}".replace("-", "−").replace("−0.00", "0.00") for x in ws[:, 1]) + "]")
    expect("math-part4.html", f"§1.6 MP-adj n={nn}", f"{(5-ls[0])/4*(1+math.sqrt(4/nn))**2:.3f}")
    print(f"2·A §1.6  n={nn} eig={np.round(ls,3)} peel={[(round(l,3),round(b,3),bool(o)) for l,b,o in ps]}")
def hcos(Xm, k):
    h = len(Xm) // 2
    return abs(vec_corr6(Xm[:h])[:, k] @ vec_corr6(Xm[h:])[:, k])
X25 = make6(2500); X2 = make6(250)
expect("math-part4.html", "§1.6 cos noise", f"<td>{hcos(noise6,0):.3f}</td><td>{hcos(noise6,1):.3f}</td>")
expect("math-part4.html", "§1.6 cos struct250", f"<td>{hcos(X2,1):.3f}</td>")
expect("math-part4.html", "§1.6 cos struct2500", f"<td>{hcos(X25,0):.3f}</td><td>{hcos(X25,1):.3f}</td><td>{hcos(X25,2):.3f}</td>")
r3 = np.random.default_rng(3); a3 = r3.standard_normal((20000, 5)); b3 = r3.standard_normal((20000, 5))
c3 = np.abs((a3 * b3).sum(1)) / np.linalg.norm(a3, axis=1) / np.linalg.norm(b3, axis=1)
expect("math-part4.html", "§1.6 cos random", f"ค่ากลาง {np.median(c3):.3f} และเปอร์เซ็นไทล์ 95 อยู่ที่ {np.percentile(c3,95):.3f}")
ls250 = eig_corr6(make6(250)); ls2500 = eig_corr6(make6(2500))
expect("math-part4.html", "§1.6 MP prefactor 250", f"{(5-ls250[0])/4:.3f} × {(1+math.sqrt(4/250))**2:.3f} = {(5-ls250[0])/4*(1+math.sqrt(4/250))**2:.3f}")
expect("math-part4.html", "§1.6 MP prefactor 2500", f"{(5-ls2500[0])/4:.3f} × {(1+math.sqrt(4/2500))**2:.3f} = {(5-ls2500[0])/4*(1+math.sqrt(4/2500))**2:.3f}")
expect("math-part4.html", "§1.6 cos struct250 PC1", f"<td>{hcos(X2,0):.3f}</td><td>{hcos(X2,1):.3f}</td>")
expect("math-part4.html", "§1.6 cos noise PC3", f"<td>{hcos(noise6,0):.3f}</td><td>{hcos(noise6,1):.3f}</td><td>{hcos(noise6,2):.3f}</td>")
det = 0
for sd_ in range(300):
    lv = eig_corr6(make6(250, seed=100 + sd_)); pl_ = peel(lv, 250); det += len(pl_) >= 2 and pl_[1][2]
print(f"2·A §1.6  detection of weak factor at n=250 over 300 seeds: {det/300:.2f}")
rng6b = np.random.default_rng(0); n25 = rng6b.standard_normal((2500, p6)); l25 = eig_corr6(n25)
expect("math-part4.html", "§1.6 ✍️ eig", "<strong>" + ", ".join(f"{v:.3f}" for v in l25) + "</strong>")
expect("math-part4.html", "§1.6 ✍️ ฐาน", f"ลงมาที่ <strong>{noise_p95(5,2500)[0]:.3f}</strong>")
expect("math-part4.html", "§1.6 ✍️ λ₊", f"(1 + √(5/2500))² = {(1+math.sqrt(5/2500))**2:.3f}")
print(f"2·A §1.6  noise eig={np.round(ln,3)} PA95={q95:.3f} fp={fp:.4f} cos noise={hcos(noise6,0):.3f}/{hcos(noise6,1):.3f} cos struct2500={hcos(X25,0):.3f}/{hcos(X25,1):.3f}/{hcos(X25,2):.3f} ✍️={np.round(l25,3)}")


# ── 2·D §9.1½ ตระกูล β · §9.2½ distance · §9.3½ first passage + threshold ──────────────
def _make_ex95(seed=0, n=500):
    r_ = np.random.default_rng(seed); u_ = r_.normal(0, 2, n); e_ = r_.normal(0, 1, n)
    s_ = np.zeros(n); A_ = np.zeros(n); A_[0] = 100
    for t_ in range(1, n):
        s_[t_] = 0.7 * s_[t_ - 1] + u_[t_]; A_[t_] = A_[t_ - 1] + 0.1 * s_[t_ - 1] + e_[t_]
    return A_, 5 + 1.5 * A_ + s_
def _hl(sp):
    x_ = sp[:-1] - sp.mean(); y_ = sp[1:] - sp.mean(); ph = (x_ @ y_) / (x_ @ x_)
    return ph, -math.log(2) / math.log(ph)
def _tls(x_, y_):
    Cv = np.cov(np.vstack([x_, y_])); v_ = np.linalg.eigh(Cv)[1][:, -1]; return v_[1] / v_[0]
Ah, Bh = _make_ex95()
b_ols = np.polyfit(Ah, Bh, 1)[0]; b_rev = 1 / np.polyfit(Bh, Ah, 1)[0]; b_tls = _tls(Ah, Bh)
grid_b = np.linspace(1.3, 1.7, 4001); phis_b = np.array([_hl(Bh - b_ * Ah)[0] for b_ in grid_b]); b_min = grid_b[phis_b.argmin()]
rows_b = [("OLS", b_ols), ("rev", b_rev), ("TLS", b_tls), ("minHL", b_min), ("true", 1.5)]
for nm, b_ in rows_b:
    expect("math-part9.html", f"§9.1½ β {nm}", f"<td>{b_:.4f}</td><td>{_hl(Bh - b_ * Ah)[1]:.2f} วัน" if nm != "true" else f"<td>1.5</td><td>{_hl(Bh - 1.5 * Ah)[1]:.2f} วัน")
sp_o = Bh - np.polyval(np.polyfit(Ah, Bh, 1), Ah); expect("math-part9.html", "§9.1½ SD spread OLS", f"<td>{sp_o.std():.3f}</td>")
expect("math-part9.html", "§9.1½ SD spread TLS", f"<td>{(Bh - Bh.mean() - b_tls * (Ah - Ah.mean())).std():.3f}</td>")
expect("math-part9.html", "§9.1½ SD spread true", f"<td>{(Bh - 1.5 * Ah).std():.3f}</td>")
expect("math-part9.html", "§9.1½ A range", f"ช่วง {Ah.min():.0f}–{Ah.max():.0f}")
# noisy 60-day windows
r11 = np.random.default_rng(11); n60 = 60
A60 = 100 + np.cumsum(r11.normal(0, 1, n60)); B60 = 5 + 1.5 * A60 + r11.normal(0, 1, n60)
Ao = A60 + r11.normal(0, 3, n60); Bo = B60 + r11.normal(0, 3, n60)
expect("math-part9.html", "§9.1½ noisy OLS", f"<td>{np.polyfit(Ao, Bo, 1)[0]:.3f}</td>")
expect("math-part9.html", "§9.1½ noisy rev", f"<td>{1/np.polyfit(Bo, Ao, 1)[0]:.3f}</td>")
expect("math-part9.html", "§9.1½ noisy TLS", f"<td>{_tls(Ao, Bo):.3f}</td>")
expect("math-part9.html", "§9.1½ clean OLS", f"<td>{np.polyfit(A60, B60, 1)[0]:.3f}</td>")
expect("math-part9.html", "§9.1½ attenuation", f"9/(9 + 9) = {A60.var()/(A60.var()+9):.3f}")
r12 = np.random.default_rng(12); ols_l, rev_l, tls_l = [], [], []
for _ in range(2000):
    A_ = 100 + np.cumsum(r12.normal(0, 1, n60)); B_ = 5 + 1.5 * A_ + r12.normal(0, 1, n60)
    Ao_ = A_ + r12.normal(0, 3, n60); Bo_ = B_ + r12.normal(0, 3, n60)
    ols_l.append(np.polyfit(Ao_, Bo_, 1)[0]); rev_l.append(1 / np.polyfit(Bo_, Ao_, 1)[0]); tls_l.append(_tls(Ao_, Bo_))
expect("math-part9.html", "§9.1½ median OLS", f"<td><strong>{np.median(ols_l):.3f}</strong></td>")
expect("math-part9.html", "§9.1½ median rev", f"<td><strong>{np.median(rev_l):.3f}</strong></td>")
expect("math-part9.html", "§9.1½ median TLS", f"<td><strong>{np.median(tls_l):.3f}</strong></td>")
# units
dAh, dBh = np.diff(Ah), np.diff(Bh)
b_dl = np.polyfit(dAh, dBh, 1)[0]; b_rt = np.polyfit(dAh / Ah[:-1], dBh / Bh[:-1], 1)[0]; b_lg = np.polyfit(np.log(Ah), np.log(Bh), 1)[0]
expect("math-part9.html", "§9.1½ β Δ", f"<td>{b_dl:.4f}</td>")
expect("math-part9.html", "§9.1½ β return", f"<td>{b_rt:.4f}</td>")
expect("math-part9.html", "§9.1½ β log", f"<td>{b_lg:.4f}</td>")
expect("math-part9.html", "§9.1½ units return", f"{b_rt:.4f} × P_B/P_A = <strong>{b_rt*Bh[-1]/Ah[-1]:.2f}</strong>")
expect("math-part9.html", "§9.1½ units log", f"{b_lg:.4f} × P_B/P_A = {b_lg*Bh[-1]/Ah[-1]:.2f}")
print(f"2·D §9.1½ β OLS={b_ols:.4f} rev={b_rev:.4f} TLS={b_tls:.4f} minHL={b_min:.4f} · noisy medians {np.median(ols_l):.3f}/{np.median(rev_l):.3f}/{np.median(tls_l):.3f} · β Δ={b_dl:.4f} ret={b_rt:.4f} log={b_lg:.4f}")
# distance
ssd_ab = ((Ah / Ah[0] - Bh / Bh[0]) ** 2).sum(); r5 = np.random.default_rng(5)
Cw = 100 + np.cumsum(r5.normal(0, 1, 500)); Dw = 155 + np.cumsum(r5.normal(0, 2, 500)); ssd_un = ((Cw / Cw[0] - Dw / Dw[0]) ** 2).sum()
expect("math-part9.html", "§9.2½ SSD pair", f"SSD = <strong>{ssd_ab:.3f}</strong>")
expect("math-part9.html", "§9.2½ SSD unrelated", f"SSD = <strong>{ssd_un:.3f}</strong> — ต่างกัน {ssd_un/ssd_ab:.0f} เท่า")
# first passage φ=0.7
phi7 = 0.7; se7 = math.sqrt(1 - phi7 ** 2); r1 = np.random.default_rng(1); M7 = 200_000
y7 = np.full(M7, 2.0); t7 = np.zeros(M7); al7 = np.ones(M7, bool)
for k_ in range(1, 3000):
    y7 = phi7 * y7 + se7 * r1.standard_normal(M7); hit = al7 & (y7 <= 0); t7[hit] = k_; al7 &= ~hit
    if not al7.any():
        break
expect("math-part9.html", "§9.3½ FP φ0.7", f"<td class=\"nw\">{-math.log(2)/math.log(phi7):.2f} วัน</td><td><strong>{np.median(t7):.0f} วัน</strong></td><td>{t7.mean():.1f} วัน</td><td>{np.percentile(t7,90):.0f} วัน</td><td>{np.percentile(t7,95):.0f} วัน</td>")
expect("math-part9.html", "§9.3½ ≤HL φ0.7", f"แถว 1.94 วัน ที่ก้าวรายวันหยาบกว่าครึ่งชีวิต: แค่ {100*(t7 <= -math.log(2)/math.log(phi7)).mean():.1f}%")
r12b = np.random.default_rng(12); varA_l = []
for _ in range(2000):
    A_ = 100 + np.cumsum(r12b.normal(0, 1, n60)); r12b.normal(0, 1, n60); r12b.normal(0, 3, n60); r12b.normal(0, 3, n60); varA_l.append(A_.var())
mvA = np.median(varA_l)
expect("math-part9.html", "§9.1½ median Var(A)", f"Var(A)/(Var(A) + 9) ≈ {mvA/(mvA+9):.2f} เมื่อ Var(A) ค่ากลางของหน้าต่าง 60 วันอยู่ราว {mvA:.0f}")
expect("math-part9.html", "§9.3½ FP φ0.9048", f"<td><strong>{np.median(t_fp):.0f} วัน</strong></td><td>{t_fp.mean():.1f} วัน</td><td>{np.percentile(t_fp,90):.0f} วัน</td><td>{np.percentile(t_fp,95):.0f} วัน</td>")
# threshold economics (2M days)
r21 = np.random.default_rng(21); N21 = 2_000_000; xs21 = np.empty(N21); v_ = 0.0
for i_ in range(N21):
    v_ = phi7 * v_ + se7 * r21.standard_normal(); xs21[i_] = v_
def _cyc(z_):
    pos = 0; entry = 0.0; gross = 0.0; trades = 0
    for v_ in xs21:
        if pos == 0:
            if v_ >= z_: pos = -1; entry = v_; trades += 1
            elif v_ <= -z_: pos = 1; entry = v_; trades += 1
        elif (pos == -1 and v_ <= 0) or (pos == 1 and v_ >= 0):
            gross += (entry - v_) if pos == -1 else (v_ - entry); pos = 0
    return trades, gross
zs = (0.5, 1.0, 1.5, 2.0, 2.5, 3.0); cyc = {z_: _cyc(z_) for z_ in zs}
um9 = lambda v: f"{v:.1f}".replace("-", "−")
for c_ in (0, 0.5, 1.0, 1.5, 2.0):
    nets = [(cyc[z_][1] - c_ * cyc[z_][0]) / N21 * 1000 for z_ in zs]; best = zs[int(np.argmax(nets))]
    cells = "".join(f"<td>{'<strong>' if z_ == best else ''}{um9(nv)}{'</strong>' if z_ == best else ''}</td>" for z_, nv in zip(zs, nets))
    expect("math-part9.html", f"§9.3½ threshold c={c_}", cells + f'<td class="nw">{best}</td>')
expect("math-part9.html", "§9.3½ trades/1000d", "จำนวนรอบต่อ 1,000 วัน: " + " · ".join(f"{cyc[z_][0]/N21*1000:.1f}" + (" (z = 0.5)" if z_ == 0.5 else (" (z = 3)" if z_ == 3.0 else "")) for z_ in zs))
expect("math-part9.html", "§9.3½ per-trade", "กำไรต่อรอบ " + " · ".join(f"{cyc[z_][1]/cyc[z_][0]:.2f}" for z_ in zs) + " SD")
print(f"2·D §9.3½ FP φ0.7 median={np.median(t7):.0f} mean={t7.mean():.1f} p90={np.percentile(t7,90):.0f} p95={np.percentile(t7,95):.0f} · threshold best z by c: " + " ".join(f"c={c_}:{zs[int(np.argmax([(cyc[z_][1]-c_*cyc[z_][0]) for z_ in zs]))]}" for c_ in (0,0.5,1.0,1.5,2.0)))


# ── 2·A §1.7 score ≠ return ≠ P&L · residual สะสม · หน้าต่าง 60 วัน ─────────────────
def _ar1s(x_):
    xm = x_[:-1]; ym = x_[1:]; A_ = np.column_stack([np.ones(len(xm)), xm]); c_ = np.linalg.lstsq(A_, ym, rcond=None)[0]; e_ = ym - A_ @ c_
    s2_ = e_ @ e_ / (len(ym) - 2); seb = math.sqrt(s2_ * np.linalg.inv(A_.T @ A_)[1, 1]); return c_[0], c_[1], (c_[1] - 1) / seb
def _ports(Rm, k=2):
    sg = Rm.std(0, ddof=1); Cm = np.corrcoef(Rm.T); l_, V_ = np.linalg.eigh(Cm); l_ = l_[::-1]; V_ = V_[:, ::-1]
    F_ = [Rm @ ((V_[:, j] * np.sign(V_[:, j].sum() if j == 0 else V_[-1, j])) / sg) for j in range(k)]
    return sg, l_, V_, np.column_stack(F_)
n7 = 2500
def _data(p_, seed=2):
    r_ = np.random.default_rng(seed); g1 = r_.standard_normal(n7); g2 = r_.standard_normal(n7); En = r_.standard_normal((n7, p_))
    L2_ = .2 * np.array([-2, -1, 0, 1, 2.]) if p_ == 5 else np.linspace(-.4, .4, p_)
    return g1, g2, L2_, np.outer(g1, np.full(p_, .8)) + np.outer(g2, L2_) + En
g1, g2, L2_5, R5 = _data(5)
sg5, l5_, V5_, F5 = _ports(R5); v1_ = V5_[:, 0] * np.sign(V5_[:, 0].sum()); Z5 = (R5 - R5.mean(0)) / sg5; sc1 = Z5 @ v1_; w5 = v1_ / sg5; wn5 = w5 / w5.sum()
expect("math-part4.html", "§1.7 σ", "σ ของห้าหุ้น = [" + ", ".join(f"{x:.3f}" for x in sg5) + "]")
expect("math-part4.html", "§1.7 v₁", "v₁ = [" + ", ".join(f"{x:.3f}" for x in v1_) + "]")
um7 = lambda v, f=".3f": f"{v:{f}}".replace("-", "−")
expect("math-part4.html", "§1.7 r day0", "<td>" + "</td><td>".join(um7(x) for x in R5[0]) + "</td>")
expect("math-part4.html", "§1.7 z day0", "<td>" + "</td><td>".join(um7(x) for x in Z5[0]) + "</td>")
expect("math-part4.html", "§1.7 score day0", f"score₁ = Σ v·z = {sc1[0]:.3f}")
expect("math-part4.html", "§1.7 w", "<td>" + "</td><td>".join(f"{x:.3f}" for x in w5) + "</td>")
expect("math-part4.html", "§1.7 Σw", f"Σw = <strong>{w5.sum():.3f}</strong>")
expect("math-part4.html", "§1.7 F₁ day0", f"<strong>{w5 @ R5[0]:.3f}%</strong> ต่อทุน")
expect("math-part4.html", "§1.7 w̃", "<td>" + "</td><td>".join(f"{x:.3f}" for x in wn5) + "</td>")
expect("math-part4.html", "§1.7 P&L", f"return <strong>{wn5 @ R5[0]:.3f}%</strong> · ฿1M → <strong>P&amp;L ฿{wn5 @ R5[0] / 100 * 1e6:,.0f}</strong>")
expect("math-part4.html", "§1.7 Var score", f"Var(score₁) ตลอด 2,500 วัน = {sc1.var(ddof=1):.3f}")
expect("math-part4.html", "§1.7 SD ports", f"{(R5 @ w5).std(ddof=1):.3f}% ต่อวัน (w) หรือ {(R5 @ wn5).std(ddof=1):.3f}% (w̃)")
expect("math-part4.html", "§1.7 corr F1 f1", f"สัมพันธ์กับปัจจัย Level ที่ใช้สร้างข้อมูล {np.corrcoef(R5 @ w5, g1)[0,1]:.3f}")
expect("math-part4.html", "§1.7 self weight", f"{w5[0]:.3f}/{w5.sum():.3f} = {w5[0]/w5.sum()*100:.0f}%")
# case A: LOO residual of stock 1
sgA, lA, VA, FA = _ports(R5[:, 1:]); XA = np.column_stack([np.ones(n7), FA]); bA = np.linalg.lstsq(XA, R5[:, 0], rcond=None)[0]; epsA = R5[:, 0] - XA @ bA; XcA = np.cumsum(epsA)
aA, phA, tA = _ar1s(XcA)
expect("math-part4.html", "§1.7 β LOO", f"β = [{bA[1]:.3f}, {um7(bA[2])}]")
expect("math-part4.html", "§1.7 resid SD", f"SD {epsA.std():.3f}%")
expect("math-part4.html", "§1.7 φ̂ A", f"φ̂ = {phA:.4f}   t ของ (φ̂ − 1) = {um7(tA, '.2f')}")
expect("math-part4.html", "§1.7 HL A", f"\"{math.log(2)/-math.log(phA):.0f} วัน\"")
print(f"2·A §1.7  score0={sc1[0]:.3f} F1={w5@R5[0]:.3f}% P&L={wn5@R5[0]/100*1e6:,.0f} · caseA φ={phA:.4f} t={tA:.2f} HL={math.log(2)/-math.log(phA):.0f} Xc range {XcA.min():.1f}..{XcA.max():.1f}")
# case B at p=5 and p=50
def _ou(seed=3, phi_=.9, sd_=1.0):
    r_ = np.random.default_rng(seed); X_ = np.zeros(n7); et = r_.standard_normal(n7) * math.sqrt(1 - phi_ ** 2) * sd_
    for t_ in range(1, n7): X_[t_] = phi_ * X_[t_ - 1] + et[t_]
    return X_
Xou = _ou(); rowsB = []
for p_ in (5, 50):
    g1p, g2p, L2p, Rp = _data(p_); Rb = Rp.copy(); Rb[:, 0] = .8 * g1p + L2p[0] * g2p + np.diff(np.concatenate([[0], Xou]))
    _, _, _, Fb = _ports(Rb[:, 1:]); Xb = np.column_stack([np.ones(n7), Fb]); bb_ = np.linalg.lstsq(Xb, Rb[:, 0], rcond=None)[0]; epsb = Rb[:, 0] - Xb @ bb_; Xcb = np.cumsum(epsb)
    ab, phb, tb = _ar1s(Xcb); hlb = math.log(2) / -math.log(phb); cb = np.corrcoef(Xcb, Xou)[0, 1]
    expect("math-part4.html", f"§1.7 case B p={p_}", f"<td>{phb:.4f}</td><td>{um7(tb, '.2f')}</td><td>{hlb:.1f} วัน</td><td>{cb:.2f}</td>" if p_ == 50 else f"<td>{phb:.4f}</td><td>{um7(tb, '.2f')}</td><td>{hlb:.0f} วัน</td><td>{cb:.2f}</td>")
    rowsB.append((p_, phb, tb, hlb, cb))
    if p_ == 50:
        epsA50 = None
        _, _, _, Fa = _ports(Rp[:, 1:]); Xa = np.column_stack([np.ones(n7), Fa]); ba_ = np.linalg.lstsq(Xa, Rp[:, 0], rcond=None)[0]; epsA50 = Rp[:, 0] - Xa @ ba_
        def _win(eps_, W):
            hls = []
            for st in range(0, n7 - W, W):
                a_, ph_, _t = _ar1s(np.cumsum(eps_[st:st + W]))
                hls.append(math.log(2) / -math.log(ph_) if 0 < ph_ < 1 else float("inf"))
            hls = np.array(hls); fin = hls[np.isfinite(hls)]
            return len(hls), np.median(fin), np.percentile(fin, 25), np.percentile(fin, 75), (hls < 30).mean()
        for W_ in (60, 250):
            nA, mA, q1A, q3A, shA = _win(epsA50, W_); nB, mB, q1B, q3B, shB = _win(epsb, W_)
            print(f"2·A §1.7  W={W_}: noise windows={nA} HL median={mA:.1f} p25={q1A:.1f} p75={q3A:.1f} pass={shA:.2f} | OU median={mB:.1f} p25={q1B:.1f} p75={q3B:.1f} pass={shB:.2f}")
            if W_ == 60:
                expect("math-part4.html", "§1.7 win60 noise", f"<td><strong>{mA:.1f} วัน</strong></td><td>{q1A:.1f}–{q3A:.1f}</td><td><strong>{shA*100:.0f}%</strong></td>")
                expect("math-part4.html", "§1.7 win60 OU", f"<td>{mB:.1f} วัน</td><td>{q1B:.1f}–{q3B:.1f}</td><td>{shB*100:.0f}%</td>")
                expect("math-part4.html", "§1.7 win60 count", f"หน้าต่าง 60 วัน {nA} หน้าต่าง")
            else:
                expect("math-part4.html", "§1.7 win250", f"ครึ่งชีวิตค่ากลาง <strong>{mA:.0f} วัน</strong> และผ่านเกณฑ์ &lt; 30 วันแค่ <strong>{int(round(shA*nA))} ใน {nA}</strong> หน้าต่าง ส่วน OU จริงยังให้ค่ากลาง {mB:.1f} วัน ผ่าน {int(round(shB*nB))} ใน {nB}")
print("2·A §1.7  case B:", [(p_, round(ph, 4), round(t_, 2), round(h, 1), round(c_, 2)) for p_, ph, t_, h, c_ in rowsB])


def main():
    if "--print" in sys.argv:
        return 0
    bad = 0
    cache = {}
    for f, label, text in CHECKS:
        path = os.path.join(DOCS, f)
        if path not in cache:
            cache[path] = open(path, encoding="utf-8").read()
        if text not in cache[path]:
            print(f"❌ {f} · {label}: ไม่พบ \"{text}\""); bad += 1
    print(f"\nตรวจ {len(CHECKS)} ค่าใน {len(cache)} ไฟล์ · ไม่ตรง {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
