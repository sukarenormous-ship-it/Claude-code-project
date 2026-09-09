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
