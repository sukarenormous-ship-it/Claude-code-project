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
