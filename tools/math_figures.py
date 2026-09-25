#!/usr/bin/env python3
"""คำนวณตัวเลขที่ปรากฏในชุดคณิตศาสตร์ (เล่ม 2) ใหม่จากอินพุตในหนังสือ แล้วตรวจว่าข้อความ
ในไฟล์ HTML ยังตรงกับค่าที่คำนวณได้

ครอบคลุม: 2·A §2.1 β/α · §2.2 multiple regression + multicollinearity · §1.3 wᵀΣw ·
2·B §4.2½ min-variance · 2·C §5.5 DR portfolio · 2·D §9.4 Kalman (มือ + จำลอง) ·
2·F §14.6 logistic (ตาราง sigmoid + fit + calibration) · 2·A §1.4 PCA · §1.6 Factor or Noise ·
§1.7 PC→พอร์ต · 2·D §9.1½ β หลายตัว · §9.2½ distance · §9.3½ first passage/threshold ·
§9.5½ Johansen · Arb §1.5 σ/√N และ P(v<0)

ใช้:  python3 tools/math_figures.py          → พิมพ์ค่าและตรวจทุกไฟล์ (exit 1 ถ้าไม่ตรง)
      python3 tools/math_figures.py --print  → พิมพ์ค่าอย่างเดียว
ต้องมี numpy (pip install numpy) เพราะ 2·D/2·F ใช้สายสุ่มของ numpy.random.default_rng
บล็อก 2·D §9.5½ (Johansen) ต้องมี statsmodels ด้วย — ถ้าไม่มีจะข้ามพร้อมเตือน ไม่ล้ม
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


CODE_CHECKS = []  # (file, หัวกล่องโค้ด) — รันโค้ดในบทจริง แล้วเทียบผลรันกับบรรทัด <span class="o"> ทั้งสองทาง


def expect_code(file, hdr):
    """โค้ด 🐍 ในบทต้องรันได้ และผลที่บทแสดงต้องเป็นผลที่โค้ดพิมพ์จริง
    · ทุกบรรทัดที่โค้ดพิมพ์ต้องอยู่ในบรรทัดผลลัพธ์ของบท
    · ทุกบรรทัดผลลัพธ์ในบท (ตัดคำอธิบายหลัง ← ออก) ต้องเป็นบรรทัดที่โค้ดพิมพ์จริง"""
    CODE_CHECKS.append((file, hdr))


def _code_block(file, hdr):
    import html as _h, re as _r
    src = open(os.path.join(DOCS, file), encoding="utf-8").read()
    for m in _r.finditer(r'<div class="code"><div class="hdr">(.*?)</div><pre>(.*?)</pre>', src, _r.S):
        if hdr in m.group(1):
            body = m.group(2)
            shown = [_h.unescape(_r.sub(r"<[^>]+>", "", t)) for t in _r.findall(r'<span class="o">(.*?)</span>', body, _r.S)]
            code = _h.unescape(_r.sub(r"<[^>]+>", "", _r.sub(r'<span class="o">.*?</span>', "", body, flags=_r.S)))
            return code, shown
    return None, None


def _discover_code_blocks():
    """ทุกกล่อง 🐍 ในคลังที่แสดงผลลัพธ์ (<span class="o">) ถูกตรวจอัตโนมัติ ไม่ต้องลงทะเบียนเอง"""
    import glob as _g, re as _r
    seen = set(CODE_CHECKS)
    for path in sorted(_g.glob(os.path.join(DOCS, "*.html"))):
        src = open(path, encoding="utf-8").read()
        for m in _r.finditer(r'<div class="code"><div class="hdr">(.*?)</div><pre>(.*?)</pre>', src, _r.S):
            if '<span class="o">' in m.group(2):
                key = (os.path.basename(path), m.group(1))
                if not any(f == key[0] and h in key[1] for f, h in seen):
                    CODE_CHECKS.append(key); seen.add(key)


def _run_code_checks():
    import subprocess as _sp, tempfile as _tf
    bad = 0; skipped = []
    env = dict(os.environ, MPLBACKEND="Agg")
    for file, hdr in CODE_CHECKS:
        code, shown = _code_block(file, hdr)
        if code is None:
            print(f"❌ {file} · ไม่พบกล่องโค้ด \"{hdr}\""); bad += 1; continue
        with _tf.TemporaryDirectory() as tmp:          # โค้ดบางกล่อง savefig — อย่าให้ไฟล์หลุดลงคลัง
            run = _sp.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=300, cwd=tmp, env=env)
        err = run.stderr.strip().splitlines()[-1] if run.stderr.strip() else str(run.returncode)
        if run.returncode and err.startswith("ModuleNotFoundError"):
            skipped.append((file, hdr, err.split("'")[1] if "'" in err else err)); continue
        if run.returncode:
            print(f"❌ {file} · โค้ด \"{hdr}\" รันไม่ผ่าน: {err}"); bad += 1; continue
        printed = [ln.strip() for ln in run.stdout.splitlines() if ln.strip()]
        shown_core = [t.lstrip("#").split("←")[0].strip() for t in shown]
        shown_core = [t for t in shown_core if t]
        for ln in printed:
            if not any(ln == t or t.startswith(ln) for t in shown_core):
                print(f"❌ {file} · โค้ด \"{hdr}\" พิมพ์ \"{ln}\" แต่บทไม่ได้แสดงบรรทัดนี้"); bad += 1
        for t in shown_core:
            if t not in printed:
                print(f"❌ {file} · โค้ด \"{hdr}\" บทแสดง \"{t}\" แต่โค้ดไม่ได้พิมพ์บรรทัดนี้"); bad += 1
    if skipped:
        pk = sorted({m for _, _, m in skipped})
        print(f"⚠️  ข้ามโค้ด {len(skipped)} กล่องเพราะเครื่องนี้ไม่มีแพ็กเกจ {', '.join(pk)} (pip install {' '.join(pk)} แล้วรันใหม่)")
    return bad


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

# ── 2·A §2.1 ❌ จุดเดียวคุมทั้งเส้น — เดือนที่ 7 · rolling 60 วันที่ jump เข้า/ออกหน้าต่าง ─────
def _beta(x, y):
    return np.cov(x, y, ddof=1)[0, 1] / np.var(x, ddof=1)
m7 = np.append(mkt6, -0.06); s7 = np.append(stk6, -0.20)
b7 = _beta(m7, s7)
r2_7 = 1 - ((s7 - np.polyval(np.polyfit(m7, s7, 1), m7)) ** 2).sum() / ((s7 - s7.mean()) ** 2).sum()
print(f"2·A §2.1❌ β7={b7:.4f} R²={r2_7:.3f} hedge ฿{b7*1e6:,.0f} vs ฿{b21*1e6:,.0f} ต่าง ฿{(b7-b21)*1e6:,.0f}")
expect("math-part4.html", "§2.1❌ β7", f"β = <b>{b7:.2f}</b>")
expect("math-part4.html", "§2.1❌ R²", f"R² = {r2_7:.2f}")
expect("math-part4.html", "§2.1❌ hedge", f"฿{b7*1e6/1e6:.2f}M แทน ฿{b21*1e6/1e6:.2f}M")
expect("math-part4.html", "§2.1❌ ต่าง", f"ต่างกัน ฿{round((b7-b21)*1e6, -3):,.0f}")
_rng = np.random.default_rng(11); _T, _W, _J = 250, 60, 120
_m = _rng.normal(0, 0.01, _T); _s = 1.2 * _m + _rng.normal(0, 0.008, _T)
_m[_J], _s[_J] = -0.07, -0.20
_rb = np.array([_beta(_m[i - _W + 1:i + 1], _s[i - _W + 1:i + 1]) for i in range(_W - 1, _T)])
_idx = np.arange(_W - 1, _T)
rb_before, rb_jump, rb_last, rb_after = _rb[_idx == _J - 1][0], _rb[_idx == _J][0], _rb[_idx == _J + _W - 1][0], _rb[_idx == _J + _W][0]
rb_loo = _beta(_m[_J - _W + 1:_J], _s[_J - _W + 1:_J])
print(f"2·A §2.1❌ rolling: ก่อน {rb_before:.2f} · วัน jump {rb_jump:.2f} · วันที่ 60 {rb_last:.2f} · วันที่ 61 {rb_after:.2f} · ตัดวัน jump {rb_loo:.2f}")
expect("math-part4.html", "§2.1❌ rolling ก่อน", f"β วันที่ 119 = {rb_before:.2f}")
expect("math-part4.html", "§2.1❌ rolling jump", f"β วันที่ 120 = {rb_jump:.2f}")
expect("math-part4.html", "§2.1❌ rolling last", f"β วันที่ 179 = {rb_last:.2f}")
expect("math-part4.html", "§2.1❌ rolling after", f"β วันที่ 180 = {rb_after:.2f}")
expect("math-part4.html", "§2.1❌ rolling loo", f"ตัดวันที่ 120 ทิ้งได้ {rb_loo:.2f}")
expect("math-part4.html", "§2.1❌ rolling prose", f"จาก {rb_before:.2f} เป็น {rb_jump:.2f}")

# ── 2·C §5.2 Robust regression — Theil-Sen · Huber บน Anscombe ชุด 3, β 7 เดือน, rolling ─────
from scipy.stats import theilslopes  # noqa: E402
import statsmodels.api as sm  # noqa: E402
_xa = np.array([10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5], float)
_y3 = np.array([7.46, 6.77, 12.74, 7.11, 7.81, 8.84, 6.08, 5.39, 8.15, 6.42, 5.73])
def _huber(x, y):
    rr = sm.RLM(y, sm.add_constant(x), M=sm.robust.norms.HuberT()).fit(); return rr.params[1], rr.weights
b_a_ols = np.polyfit(_xa, _y3, 1)[0]; b_a_cut = np.polyfit(_xa[_y3 < 12], _y3[_y3 < 12], 1)[0]
b_a_ts = theilslopes(_y3, _xa)[0]; b_a_h, w_a = _huber(_xa, _y3)
print(f"2·C §5.2 robust: OLS {b_a_ols:.3f} ตัด {b_a_cut:.3f} TS {b_a_ts:.3f} Huber {b_a_h:.3f} w_outlier {w_a[2]:.3f}")
expect("math-part8.html", "§5.2 robust Anscombe", f"OLS = <strong>{b_a_ols:.3f}</strong> · ตัด outlier ด้วยมือ = {b_a_cut:.3f} · Theil-Sen = <strong>{b_a_ts:.3f}</strong> · Huber = <strong>{b_a_h:.3f}</strong>")
expect("math-part8.html", "§5.2 robust code", f"# OLS {b_a_ols:.3f} · Theil-Sen {b_a_ts:.3f} · Huber {b_a_h:.3f}")
assert w_a[2] < 0.01 and np.all(w_a[np.arange(11) != 2] > 0.99), w_a
expect("math-part8.html", "§5.2 คู่", f"11 จุดได้ {11*10//2} คู่")
b7_ts = theilslopes(s7, m7)[0]; b7_h, _ = _huber(m7, s7)
print(f"2·C §5.2 robust 7 เดือน: OLS {b7:.2f} TS {b7_ts:.2f} Huber {b7_h:.2f}")
_sl7 = [(s7[6] - s7[i]) / (m7[6] - m7[i]) for i in range(6)]; _w7 = _huber(m7, s7)[1][6]
expect("math-part8.html", "§5.2 คู่เดือน 7", f"จุดเดียวอยู่ใน {6} จาก {21} คู่ ({6/21*100:.0f}% ของคู่")
expect("math-part8.html", "§5.2 min slope เดือน 7", f"ให้ความชันตั้งแต่ {min(_sl7):.2f} ขึ้นไป")
expect("math-part8.html", "§5.2 Huber w เดือน 7", f"น้ำหนักเดือนที่ 7 เหลือ {_w7:.2f}")
expect("math-part8.html", "§5.2 robust 7 เดือน", f"OLS = <strong>{b7:.2f}</strong> · Theil-Sen = <strong>{b7_ts:.2f}</strong> · Huber = <strong>{b7_h:.2f}</strong> · 6 เดือนแรกล้วน = {b21:.2f}")
_w0, _w1 = slice(_J - _W, _J), slice(_J - _W + 1, _J + 1)
rb_ts0, rb_ts1 = theilslopes(_s[_w0], _m[_w0])[0], theilslopes(_s[_w1], _m[_w1])[0]
rb_h0, rb_h1 = _huber(_m[_w0], _s[_w0])[0], _huber(_m[_w1], _s[_w1])[0]
print(f"2·C §5.2 robust rolling: OLS {rb_before:.2f}→{rb_jump:.2f} TS {rb_ts0:.2f}→{rb_ts1:.2f} Huber {rb_h0:.2f}→{rb_h1:.2f}")
expect("math-part8.html", "§5.2 robust rolling", f"OLS กระโดด {rb_before:.2f} → <strong>{rb_jump:.2f}</strong> · Theil-Sen {rb_ts0:.2f} → <strong>{rb_ts1:.2f}</strong> · Huber {rb_h0:.2f} → <strong>{rb_h1:.2f}</strong>")
expect("math-part8.html", "§5.2 ลิงก์ 2·A", f"β ที่กระโดดจาก {rb_before:.2f} เป็น {rb_jump:.2f}")

# ── 2·A §1.4½ OLS vs PCA — ความชันสามแบบจากข้อมูลชุดเดียว (ภาพวาดโดย tools/make_figures.py) ──
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_figures import ols_pca_data  # noqa: E402
_x, _y, b_ols_f, b_pca_f, b_rev_f = ols_pca_data()
print(f"2·A §1.4½ OLS={b_ols_f:.4f} PC1={b_pca_f:.4f} OLS สลับ={b_rev_f:.4f}")
expect("math-part4.html", "§1.4½ OLS", f"OLS (Y บน X) = <b>{b_ols_f:.2f}</b>")
expect("math-part4.html", "§1.4½ PC1", f"PC1 (TLS) = <b>{b_pca_f:.2f}</b>")
expect("math-part4.html", "§1.4½ OLS สลับ", f"OLS สลับข้าง (X บน Y แล้วกลับ) = <b>{b_rev_f:.2f}</b>")
expect("math-part4.html", "§1.4½ ภาพ OLS", f"ความชัน = {b_ols_f:.2f}")
expect("math-part4.html", "§1.4½ ภาพ PC1", f"ความชัน = {b_pca_f:.2f}")
expect("math-part4.html", "§1.4½ ลำดับ", f"({b_ols_f:.2f} &lt; {b_pca_f:.2f} &lt; {b_rev_f:.2f})")
expect("math-part4.html", "§1.4½ bullet", f"OLS คือคำตอบ ({b_ols_f:.2f}) · PC1 ({b_pca_f:.2f}) ตอบคำถามอื่น")
expect("math-part4.html", "§1.4½ สลับ", f"ในภาพนี้ {b_ols_f:.2f} กับ {b_rev_f:.2f} ห่างกัน")
assert b_ols_f < b_pca_f < b_rev_f

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
expect("math-part9.html", "SE φ̂ VECM/AR1 · กล่องเมื่อไรไม่จำเป็น",
       f"SE ของ φ̂ จาก VECM คือ {se_phi_vecm:.3f} ส่วนจาก AR(1) คือ {se_phi_ar1:.3f}")
expect("math-part9.html", "SE กว้างกว่ากี่ %",
       f"กว้างกว่าราว {round((se_phi_vecm / se_phi_ar1 - 1) * 100 / 10) * 10:.0f}%")
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
_np95_cache = {}
def noise_p95(pp, nn, sims=1000, seed=1):
    key = (pp, nn, sims, seed)
    if key not in _np95_cache:  # ผลเดิมทุกครั้ง (seed คงที่) — cache ไว้เพราะ peel() ถูกเรียกหลายร้อยรอบ
        r_ = np.random.default_rng(seed)
        arr = np.array([eig_corr6(r_.standard_normal((nn, pp)))[0] for _ in range(sims)])
        _np95_cache[key] = (np.percentile(arr, 95), np.median(arr), arr.max())
    return _np95_cache[key]
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
expect("math-part4.html", "§1.7 SD ports", f"SD ของพอร์ต w คือ {(R5 @ w5).std(ddof=1):.3f}% ต่อวัน")
expect("math-part4.html", "§1.7 SD w̃", f"SD {(R5 @ wn5).std(ddof=1):.3f}% = {(R5 @ w5).std(ddof=1):.3f}/{w5.sum():.3f}")
expect("math-part4.html", "§1.7 corr F1 f1", f"สัมพันธ์กับปัจจัย Level ที่ใช้สร้างข้อมูล {np.corrcoef(R5 @ w5, g1)[0,1]:.3f}")
expect("math-part4.html", "§1.7 self weight", f"{w5[0]:.3f}/{w5.sum():.3f} = {w5[0]/w5.sum()*100:.0f}%")
# case A: LOO residual of stock 1
sgA, lA, VA, FA = _ports(R5[:, 1:]); XA = np.column_stack([np.ones(n7), FA]); bA = np.linalg.lstsq(XA, R5[:, 0], rcond=None)[0]; epsA = R5[:, 0] - XA @ bA; XcA = np.cumsum(epsA)
aA, phA, tA = _ar1s(XcA)
expect("math-part4.html", "§1.7 β LOO", f"β = [{bA[1]:.3f}, {um7(bA[2])}]")
expect("math-part4.html", "§1.7 resid SD", f"SD {epsA.std():.3f}%")
expect("math-part4.html", "§1.7 φ̂ A", f"φ̂ = {phA:.4f}   t ของ (φ̂ − 1) = {um7(tA, '.2f')}")
expect("math-part4.html", "§1.7 HL A", f"\"{math.log(2)/-math.log(phA):.0f} วัน\"")
expect("math-part4.html", "§1.7 Xc range", f"เดินไปถึง {XcA.min():.0f} และ +{XcA.max():.0f}".replace("-", "−"))
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
            return len(hls), np.median(fin), np.percentile(fin, 25), np.percentile(fin, 75), (hls < 30 * math.log(2)).mean()
        for W_ in (60, 250):
            nA, mA, q1A, q3A, shA = _win(epsA50, W_); nB, mB, q1B, q3B, shB = _win(epsb, W_)
            print(f"2·A §1.7  W={W_}: noise windows={nA} HL median={mA:.1f} p25={q1A:.1f} p75={q3A:.1f} pass={shA:.2f} | OU median={mB:.1f} p25={q1B:.1f} p75={q3B:.1f} pass={shB:.2f}")
            if W_ == 60:
                expect("math-part4.html", "§1.7 win60 noise", f"<td><strong>{mA:.1f} วัน</strong></td><td>{q1A:.1f}–{q3A:.1f}</td><td><strong>{shA*100:.0f}%</strong></td>")
                expect("math-part4.html", "§1.7 win60 OU", f"<td>{mB:.1f} วัน</td><td>{q1B:.1f}–{q3B:.1f}</td><td>{shB*100:.0f}%</td>")
                expect("math-part4.html", "§1.7 win60 count", f"หน้าต่าง 60 วัน {nA} หน้าต่าง")
            else:
                expect("math-part4.html", "§1.7 win250", f"ครึ่งชีวิตค่ากลาง <strong>{mA:.0f} วัน</strong> และผ่านเกณฑ์ &lt; 20.8 วันแค่ <strong>{int(round(shA*nA))} ใน {nA}</strong> หน้าต่าง ส่วน OU จริงให้ค่ากลาง {mB:.1f} วัน ผ่าน {int(round(shB*nB))} ใน {nB}")
                expect("math-part4.html", "§1.7 win250 pct", f"(80% → {shA*100:.0f}% กับ 95% → {shB*100:.0f}%)")
print("2·A §1.7  case B:", [(p_, round(ph, 4), round(t_, 2), round(h, 1), round(c_, 2)) for p_, ph, t_, h, c_ in rowsB])


# ── 2·D §9.5½ Johansen บนตะกร้า 3 ตัว (ต้องมี statsmodels) ────────────────────────
try:
    from statsmodels.tsa.vector_ar.vecm import coint_johansen
    from statsmodels.tsa.stattools import coint as _coint
    rj = np.random.default_rng(4); nj = 500
    Aj = 100 + np.cumsum(rj.normal(0, 1, nj)); Bj = 80 + np.cumsum(rj.normal(0, 1.2, nj))
    uj = rj.normal(0, 1, nj); sj = np.zeros(nj)
    for t_ in range(1, nj): sj[t_] = 0.8 * sj[t_ - 1] + uj[t_]
    Cj = 10 + 0.5 * Aj + 0.8 * Bj + sj; Yj = np.column_stack([Aj, Bj, Cj])
    umj = lambda v, f=".2f": f"{v:{f}}".replace("-", "−")
    for i_, j_, nm in [(0, 1, "A กับ B"), (0, 2, "A กับ C"), (1, 2, "B กับ C")]:
        tj, pj, _ = _coint(Yj[:, i_], Yj[:, j_])
        expect("math-part9.html", f"§9.5½ EG {nm}", f"<td class=\"nw\">{nm}</td><td>{umj(tj)}</td><td>{pj:.3f}</td>")
    jo = coint_johansen(Yj, det_order=0, k_ar_diff=0)
    for r_ in range(3):
        cell = f"<td>{jo.eig[r_]:.4f}</td><td>" + ("<strong>" if r_ < 2 else "") + f"{jo.lr1[r_]:.2f}" + ("</strong>" if r_ < 2 else "") + f"</td><td>{jo.cvt[r_,1]:.2f}</td>"
        expect("math-part9.html", f"§9.5½ trace r≤{r_}", cell)
    bj = jo.evec[:, 0] / -jo.evec[2, 0]
    expect("math-part9.html", "§9.5½ β", f"<strong>[{bj[0]:.3f}, {bj[1]:.3f}, −1]</strong>")
    spj = Yj @ bj; xj = spj[:-1] - spj.mean(); yj = spj[1:] - spj.mean(); phj = (xj @ yj) / (xj @ xj)
    expect("math-part9.html", "§9.5½ spread HL", f"φ = {phj:.4f} → ครึ่งชีวิต <strong>{-math.log(2)/math.log(phj):.2f} วัน</strong> (จริง {-math.log(2)/math.log(0.8):.2f})")
    bo = np.linalg.lstsq(np.column_stack([np.ones(nj), Aj, Bj]), Cj, rcond=None)[0]
    expect("math-part9.html", "§9.5½ OLS", f"(regress C บน A, B): [{bo[1]:.3f}, {bo[2]:.3f}]")
    jo1 = coint_johansen(Yj, det_order=0, k_ar_diff=1)
    expect("math-part9.html", "§9.5½ lag1", f"ใช้ lag 1 ได้ trace {jo1.lr1[0]:.2f} / {jo1.lr1[1]:.2f} / {jo1.lr1[2]:.2f}")
    Dj = 50 + np.cumsum(rj.normal(0, 1, nj)); jo4 = coint_johansen(np.column_stack([Aj, Bj, Cj, Dj]), 0, 0)
    expect("math-part9.html", "§9.5½ ratio", f"(อัตราส่วน trace ต่อค่าวิกฤตลดจาก {jo.lr1[1]/jo.cvt[1,1]:.2f} เหลือ {jo4.lr1[1]/jo4.cvt[1,1]:.2f})")
    expect("math-part9.html", "§9.5½ 4 vars", "trace = [" + ", ".join(f"{v:.2f}" for v in jo4.lr1) + "] เทียบ [" + ", ".join(f"{v:.2f}" for v in jo4.cvt[:, 1]) + "]")
    print(f"2·D §9.5½ eig={np.round(jo.eig,4)} trace={np.round(jo.lr1,2)} β={np.round(bj,3)} HL={-math.log(2)/math.log(phj):.2f} · 4 vars trace={np.round(jo4.lr1,2)}")
except ImportError:
    print("⚠️  statsmodels ไม่ได้ติดตั้ง — ข้ามบล็อก §9.5½ (pip install statsmodels)")


# ── statarb-ledger: บัญชีหนึ่งไม้ pairs (เลขคณิตล้วน) ────────────────────────────
fee_ = 0.0005; borrow_ = 0.0002; days_ = 5
B_in, B_q = 150.20, 100; A_in1, A_q1, A_in2, A_q2 = 96.80, 100, 96.95, 51; B_out, A_out = 147.90, 96.40
notB = B_q * B_in; notA = A_q1 * A_in1 + A_q2 * A_in2
fees_in = fee_ * B_q * B_in + fee_ * A_q1 * A_in1 + fee_ * A_q2 * A_in2
pnlB = (B_in - B_out) * B_q; pnlA = (A_out - A_in1) * A_q1 + (A_out - A_in2) * A_q2
fees_out = round(fee_ * B_q * B_out, 2) + round(fee_ * (A_q1 + A_q2) * A_out, 2); borrow_c = borrow_ * notB * days_  # ปัดทีละบรรทัดเหมือนในหน้า
net_ = pnlB + pnlA - fees_in - fees_out - borrow_c
sp_in = B_in - 1.51 * A_in1; sp_out = B_out - 1.51 * A_out; naive = 100 * (sp_in - sp_out)
expect("statarb-ledger.html", "ledger ขา B", f"= +{pnlB:.2f}")
expect("statarb-ledger.html", "ledger ขา A", f"= −{-(A_out - A_in1) * A_q1:.2f} − {-(A_out - A_in2) * A_q2:.2f} = −{-pnlA:.2f}")
expect("statarb-ledger.html", "ledger gross", f"= +{pnlB + pnlA:.2f}")
expect("statarb-ledger.html", "ledger fees", f"{fee_*B_q*B_in:.2f} + {fee_*A_q1*A_in1:.2f} + {fee_*A_q2*A_in2:.2f} = {fees_in:.2f} &nbsp;·&nbsp; ออก {fee_*B_q*B_out:.2f} + {fee_*(A_q1+A_q2)*A_out:.2f} = {fees_out:.2f} &nbsp;·&nbsp; ค่ายืม {borrow_c:.2f}")
expect("statarb-ledger.html", "ledger net", f"= +{net_:.2f}")
expect("statarb-ledger.html", "ledger spread", f"= <strong>{sp_in:.3f}</strong> · วันออก = 147.90 − 1.51 × 96.40 = <strong>{sp_out:.3f}</strong> · backtest บอกว่ากำไร = 100 × ({sp_in:.3f} − {sp_out:.3f}) = <strong>{naive:.2f}</strong>")
expect("statarb-ledger.html", "ledger partial", f"<td>−{A_q2*(A_in2-A_in1):.2f}</td><td>{A_q2*(A_in2-A_in1)/naive*100:.1f}%</td>")
expect("statarb-ledger.html", "ledger fees share", f"(14.82 + {fees_out:.2f})</td><td>−{fees_in+fees_out:.2f}</td><td>{(fees_in+fees_out)/naive*100:.1f}%</td>")
expect("statarb-ledger.html", "ledger borrow share", f"<td>−{borrow_c:.2f}</td><td>{borrow_c/naive*100:.1f}%</td>")
expect("statarb-ledger.html", "ledger gap total", f"<strong>−{naive-net_:.2f}</strong></td><td><strong>{(naive-net_)/naive*100:.1f}%</strong>")
expect("statarb-ledger.html", "ledger exposure gap", f"net short {notB - A_q1*A_in1:,.0f}")
expect("statarb-ledger.html", "ledger gross notional", f"<td>{notB+notA:,.2f}</td><td><strong>{net_/(notB+notA)*100:.3f}%</strong>")
expect("statarb-ledger.html", "ledger on B", f"<td>{notB:,.2f}</td><td>{net_/notB*100:.2f}%</td>")
expect("statarb-ledger.html", "ledger on margin", f"<td>{0.25*(notB+notA):,.2f}</td><td><strong>{net_/(0.25*(notB+notA))*100:.2f}%</strong>")
expect("statarb-ledger.html", "ledger borrow % of net", f"{borrow_c/net_*100:.1f}% ของกำไรสุทธิ")
expect("statarb-ledger.html", "ledger pct_change", f"ให้ \"ผลตอบแทน\" {(0.05-0.40)/0.40*100:.0f}% แล้ว {(-0.30-0.05)/0.05*100:.0f}%".replace("-", "−"))
print(f"ledger    gross={pnlB+pnlA:.2f} net={net_:.2f} naive={naive:.2f} gap={naive-net_:.2f} ({(naive-net_)/naive*100:.1f}%)")


# ── theory-extra: การ์ด Decision & Dependence (เลขคณิตล้วน) ──────────────────────────
for rho_ in (0.3, 0.8):
    mi_ = -0.5 * math.log(1 - rho_ ** 2)
    expect("theory-extra.html", f"MI ρ={rho_}", f"<strong>{mi_:.3f} nats</strong> ({mi_/math.log(2):.3f} bits)")
Hy = -(1/3 * math.log2(1/3) + 2/3 * math.log2(2/3))
expect("theory-extra.html", "H(Y) X²", f"= <strong>{Hy:.3f} bits</strong>")
expect("theory-extra.html", "MI ratio", f"ข้อมูลที่ได้เพิ่ม {(-0.5*math.log(1-0.64))/(-0.5*math.log(1-0.09)):.0f} เท่า")
pred_ = 0.2 * 0.7 + 0.8 * 0.1; lc_ = math.exp(-0.5 * 9); ls_ = math.exp(-0.5) / 3; post_ = pred_ * ls_ / (pred_ * ls_ + (1 - pred_) * lc_)
expect("theory-extra.html", "HMM predict", f"0.2 × 0.7 + 0.8 × 0.1 = <strong>{pred_:.2f}</strong>")
expect("theory-extra.html", "HMM lik", f"= {lc_:.4f} · ภายใต้ปั่นป่วน ∝ e^{{−½(3/3)²}}/3 = {ls_:.4f}")
expect("theory-extra.html", "HMM post", f"= <strong>{post_:.3f}</strong>")
expect("theory-extra.html", "HMM LR", f"อัตราส่วน likelihood {ls_/lc_:.0f} เท่า")
expect("theory-extra.html", "stop 50%", f"= <strong>{0.5*105+0.5*97-0.3:.1f}</strong>")
expect("theory-extra.html", "stop 40%", f"= <strong>{0.4*105+0.6*97-0.3:.1f}</strong>")
p_star = (100 + 0.3 - 97) / (105 - 97)
expect("theory-extra.html", "stop p*", f"เส้นแบ่งอยู่ที่โอกาสราว {p_star*100:.0f}%")
expect("theory-extra.html", "MI bias", f"81/(500 × 0.693) ≈ <strong>{81/(2*250*math.log(2)):.2f} bits</strong>")
expect("theory-extra.html", "pinball", f"(10 − 8) × 0.9 = {2*0.9:.1f} · ทำนาย 12 → (10 − 12) × (0.9 − 1) = {(-2)*(0.9-1):.1f}")
print(f"theory-extra MI={-0.5*math.log(1-0.09):.4f}/{-0.5*math.log(1-0.64):.4f} H(Y)={Hy:.3f} HMM pred={pred_:.2f} post={post_:.3f} LR={ls_/lc_:.1f} p*={p_star:.3f}")

# ── Arb เล่ม 1 §2.3 ค่าใช้จ่าย — ตัวเลขในกล่อง "กฎทอง" ต้องตรงกับภาพน้ำตก ────────────────
import make_figures as _mf  # noqa: E402

_steps, _net, _cost = _mf.cost_waterfall_data()
print(f"Arb §2.3   gross={_steps[0][1]:.2f} ค่าใช้จ่ายรวม={_cost:.2f} net={_net:+.2f}")
expect("arb-part1.html", "§2.3 กฎทอง", f"Arb ที่ดูเหมือนกำไร ฿{_steps[0][1]:.2f} อาจขาดทุนจริง ฿{abs(_net):.2f} หลังหักค่าใช้จ่าย")


# ── เล่ม 1 Part IV §11.3 Black-Scholes — ภาพกายวิภาคต้องใช้เลขชุดเดียวกับตัวอย่างในบท ──────
_d1, _d2, _Nd1, _Nd2, _disc, _t1, _t2, _C = _mf.bs_anatomy_data()
print(f"เล่ม1 §11.3 d1={_d1:.3f} d2={_d2:.3f} N(d1)={_Nd1:.4f} N(d2)={_Nd2:.4f} C={_C:.3f}")
expect("math-part7.html", "§11.3 d₁", f"d₁ = (0 + 0.08125) / 0.25 = <b>{_d1:.3f}</b>")
expect("math-part7.html", "§11.3 d₂", f"d₂ = d₁ − σ√T = {_d1:.3f} − 0.25 = <b>{_d2:.3f}</b>")
expect("math-part7.html", "§11.3 N(d₁)", f"N(d₁) = N({_d1:.3f}) ≈ <b>{_Nd1:.4f}</b>")
expect("math-part7.html", "§11.3 N(d₂)", f"N(d₂) = N({_d2:.3f}) ≈ <b>{_Nd2:.4f}</b>")
expect("math-part7.html", "§11.3 C ขั้นลบ", f"= {_t1:.2f} − {_t2:.2f}\n")
expect("math-part7.html", "§11.3 C ละเอียด", f"(ค่าละเอียด = {_C:.3f})")

# ── ตาของ Arbitrageur ถอด structured note — ภาพกับข้อความต้องได้ตัวเลขเดียวกัน ─────────────
_eln_cost, _eln_markup = _mf.eln_data()
print(f"eye ELN   ต้นทุนจริง={_eln_cost:.0f} จ่ายเกิน={_eln_markup:.0f}")
expect("eye-part2.html", "ELN ต้นทุนจริง", f"ต้นทุนจริง = 97 + 5 = ฿{_eln_cost:.0f}")
expect("eye-part2.html", "ELN markup", f"คุณจ่ายแพงเกิน ฿{_eln_markup:.0f}!")



# ── statarb-ic-lab — ทุกตัวเลขในบทผูกกับ docs/ic-figures.json (สร้างด้วย tools/ic_figures.py) ──
_IC = _mf._load("ic-figures.json")
_F = "statarb-ic-lab.html"


def _neg(x):
    """−0.116 แบบที่เขียนในบท (ลบเป็นเครื่องหมายลบจริง ไม่ใช่ hyphen)"""
    return f"{x:+.3f}".replace("-", "−")


_ic_d = _IC["ข้อมูล"]
expect(_F, "ช่วงข้อมูล", f"({_ic_d['ตั้งแต่']} ถึง {_ic_d['ถึง']} · {_ic_d['จำนวนวัน']} วัน)")

for _r in _IC["สัญญาณ"]:
    _h1 = _r["ทุกhorizon"]["1 วัน"]
    _lab = _r["สัญญาณ"]
    expect(_F, f"ตาราง §3 · {_lab} IC", f'{_neg(_r["IC1วัน"])}</td><td class="nw">{_r["จำนวนวัน"]}</td>')
    expect(_F, f"ตาราง §3 · {_lab} SE/ฐาน",
           f'<td class="nw">{_h1["SEโดยประมาณ"]:.3f}</td><td class="nw">±{_r["ฐานสุ่ม"]["absที่95"]:.3f}</td>')

_sel = _IC["ผลของการเลือกตัวที่ดีที่สุด"]
expect(_F, "§4 ฐานเฉลี่ยของตัวที่ดีที่สุด", f"max|IC| เฉลี่ย <strong>{_sel['maxABSเฉลี่ยจากความสุ่ม']:.3f}</strong>")
expect(_F, "§4 ฐานที่ 95 ของตัวที่ดีที่สุด", f"และถึง <strong>{_sel['maxABSที่95จากความสุ่ม']:.3f}</strong> ได้ใน 5% ของรอบ")
expect(_F, "§4 ค่าจริงกับเปอร์เซ็นไทล์",
       f"<strong>{_sel['ของจริง']:.3f}</strong> — อยู่ที่เปอร์เซ็นไทล์ <strong>{_sel['เปอร์เซ็นไทล์ของของจริง']:.1f}</strong>")
expect(_F, "§4 สัดส่วนรอบสุ่มที่สูงกว่า", f"(ราว {100 - _sel['เปอร์เซ็นไทล์ของของจริง']:.0f}% ของรอบสุ่มให้ค่าสูงกว่าเรา)")

_C = _IC["สหสัมพันธ์ระหว่างสัญญาณ"]
_hi, _lo = _C["สูงสุด"], _C["ต่ำสุด"]
_ma, _least = _C["ค่าเฉลี่ยสัมบูรณ์ต่อสัญญาณ"], _C["ตัวที่ซ้ำกับตัวอื่นน้อยที่สุด"]
expect(_F, "§4 คู่ที่ซ้ำกันที่สุด",
       f"{_hi['คู่'][0]} กับ {_hi['คู่'][1]} ที่ <strong>{_hi['สหสัมพันธ์อันดับ']:.2f}</strong>")
expect(_F, "§4 คู่ที่ต่างกันที่สุด",
       f"({_lo['คู่'][0]} กับ {_lo['คู่'][1]}) ก็ยังได้ {_lo['สหสัมพันธ์อันดับ']:.2f}")
expect(_F, "§7 ตัวที่ซ้ำน้อยสุดไม่ติดกับดัก",
       f'<strong>"{_least}"</strong>')
expect(_F, "§7 IC ที่ 10 วันของตัวนั้น",
       f'(IC {next(r["ทุกhorizon"]["10 วัน"]["IC"] for r in _IC["สัญญาณ"] if r["สัญญาณ"] == _least):+.4f} — ยังอยู่ในฐาน)')
expect(_F, "§7 ค่าเฉลี่ยสหสัมพันธ์",
       f"(เฉลี่ย {_ma[_least]:.2f} เทียบกับ {max(_ma.values()):.2f} ของตัวที่ซ้ำมากที่สุด)")

_P = _IC["โอกาสที่การทดสอบจะจับได้"]
expect(_F, "§3 power ที่ IC 0.25",
       f"IC จริงเท่ากับ 0.25 การทดสอบนี้มีโอกาสจับได้เพียง {_P['โอกาสจับได้']['IC จริง = 0.25']:.0f}%")
expect(_F, "§3 power ที่ IC 0.20 และ 0.40",
       f"ที่ IC จริง 0.20 เหลือ {_P['โอกาสจับได้']['IC จริง = 0.2']:.0f}% และที่ 0.40 ก็ยังได้แค่ {_P['โอกาสจับได้']['IC จริง = 0.4']:.0f}%")
expect(_F, "§8 power ในสรุปสามข้อ",
       f"ที่ {_P['จำนวนวันที่ใช้']} วัน ต่อให้ IC จริงเป็น 0.25 การทดสอบก็จับได้แค่ {_P['โอกาสจับได้']['IC จริง = 0.25']:.0f}%")
expect(_F, "§5 ค่า z ที่ใช้", f"z<sub>α</sub> = {_P['zที่ใช้ตัด']} · z<sub>β</sub> = 1.2816")

_samp = _IC["ขนาดตัวอย่างที่ต้องใช้"]
_best = _IC["สัญญาณที่ดีที่สุด"]
_YR = _IC["กฎพื้นฐานของการจัดการเชิงรุก"]["ของสัญญาณที่ดีที่สุด"]["วันต่อปีของสินทรัพย์เดียว"]
_need = next(v for k, v in _samp.items() if "ที่วัดได้" in k)
for _k, _v in _samp.items():
    if "ที่วัดได้" in _k:
        continue
    _icv = float(_k.split("= ")[1])
    expect(_F, f"ตาราง §5 · IC {_icv}", f'<td class="nw">{_icv:.2f}</td><td class="nw">{_v:,}</td><td class="nw">{_v/_YR:.1f}</td>')
expect(_F, "ตาราง §5 · IC ที่วัดได้",
       f'<strong>{abs(_best["IC"]):.4f}</strong> (ที่วัดได้)</td><td class="nw"><strong>{_need:,}</strong></td><td class="nw">{_need/_YR:.1f}</td>')
expect(_F, "ตาราง §5 · ระยะห่างจากที่ต้องใช้",
       f'<strong>{_best["จำนวนวัน"]} วัน</strong> — ห่างจากที่ต้องใช้ราว <strong>{_need/_best["จำนวนวัน"]:.0f} เท่า</strong>')

_T = _IC["กลุ่มสามส่วนของสัญญาณที่ดีที่สุด"]
for _g in _T["กลุ่ม"]:
    expect(_F, f"ตาราง §6 · กลุ่ม{_g['กลุ่ม']}",
           f'<td class="nw">{_g["จำนวนวัน"]}</td><td class="nw">{_g["ผลตอบแทนเฉลี่ยเปอร์เซ็นต์"]:+.3f}%</td>'
           f'<td class="nw">{_g["มัธยฐานเปอร์เซ็นต์"]:+.3f}%</td>'.replace("-", "−"))
expect(_F, "ตาราง §6 · ส่วนต่าง",
       f'<strong>{_T["ส่วนต่างสูงสุดลบต่ำสุดเปอร์เซ็นต์"]:+.3f}%</strong></td><td class="nw">{_T["ส่วนต่างมัธยฐานเปอร์เซ็นต์"]:+.3f}%</td>'.replace("-", "−"))
expect(_F, "ตาราง §6 · กำไรขั้นต้น",
       f'<td class="nw"><strong>+{_T["กำไรขั้นต้นตามทิศที่ถูกเปอร์เซ็นต์"]:.3f}%</strong></td>')
expect(_F, "ตาราง §6 · หักต้นทุน",
       f'หักต้นทุนไป-กลับ {_T["ต้นทุนไปกลับเปอร์เซ็นต์"]}%</td><td class="nw">—</td>'
       + f'<td class="nw"><strong>+{_T["เหลือหลังต้นทุนเปอร์เซ็นต์"]:.3f}%</strong>')
expect(_F, "§6 ทิศที่ต้องเทรด", f'<em>{_T["ทิศที่ต้องเทรด"]}</em>')
expect(_F, "§6 ค่าเฉลี่ยกับมัธยฐานของกลุ่มต่ำสุด",
       f'({_T["กลุ่ม"][0]["ผลตอบแทนเฉลี่ยเปอร์เซ็นต์"]:+.3f}% กับ {_T["กลุ่ม"][0]["มัธยฐานเปอร์เซ็นต์"]:+.3f}% ในกลุ่มต่ำสุด)')
expect(_F, "§6 กำไรขั้นต้นในกล่องเตือน",
       f'<strong>+{_T["กำไรขั้นต้นตามทิศที่ถูกเปอร์เซ็นต์"]:.3f}% ต่อวัน</strong>')

_h10 = [r["ทุกhorizon"]["10 วัน"] for r in _IC["สัญญาณ"]]
_out10 = [x for x in _h10 if x["นอกฐาน"]]
_THAI_N = {4: "สี่", 5: "ห้า", 6: "หก", 7: "เจ็ด"}
expect(_F, "§7 จำนวนที่หลุดฐานที่ 10 วัน",
       f"{_THAI_N[len(_out10)]}ใน{_THAI_N[len(_h10)]}สัญญาณหลุดออกนอกแถบฐานพร้อมกัน")
expect(_F, "§7 ช่วง IC ที่ 10 วัน",
       f"มี IC ระหว่าง {max(x['IC'] for x in _out10):.2f} ถึง {min(x['IC'] for x in _out10):.2f}".replace("-", "−"))
expect(_F, "§7 ช่วงจำนวนวันที่ 10 วัน",
       f"ที่นับได้ {min(x['จำนวนวัน'] for x in _h10)}–{max(x['จำนวนวัน'] for x in _h10)} วัน")
expect(_F, "§7 จำนวนตัวอย่างอิสระ",
       f"<strong>{min(x['จำนวนวันอิสระโดยประมาณ'] for x in _h10)}–{max(x['จำนวนวันอิสระโดยประมาณ'] for x in _h10)}</strong>")
expect(_F, "§7 การซ้อนทับ", "ซ้อนทับกัน 9 ใน 10 วัน")
_px = _mf._load("nq-figures.json")["ราคารายวัน"]
expect(_F, "§7 ราคาจริงต้นช่วงทะยาน", f"{float(_px['2026-08-17']):,.0f} วันที่ 17 ส.ค.")
expect(_F, "§7 ราคาจริงปลายช่วงทะยาน", f"{float(_px['2026-08-27']):,.0f} วันที่ 27 ส.ค.")
expect(_F, "§7 ขนาดการทะยาน",
       f"<strong>+{(float(_px['2026-08-27'])/float(_px['2026-08-17'])-1)*100:.0f}% ใน 10 วัน</strong>")

_law = _IC["กฎพื้นฐานของการจัดการเชิงรุก"]
for _k, _v in _law["จำนวนเดิมพันอิสระที่ต้องใช้ต่อปี"].items():
    _icv = float(_k.split("= ")[1])
    expect(_F, f"ตาราง §8 · IC {_icv}", f'<td class="nw">{_icv:.2f}</td><td class="nw">{_v}</td>')
_lb = _law["ของสัญญาณที่ดีที่สุด"]
expect(_F, "ตาราง §8 · IC ที่วัดได้",
       f'<strong>{_lb["IC"]:.4f}</strong> (ที่วัดได้)</td><td class="nw"><strong>{_lb["เดิมพันอิสระที่ต้องใช้ต่อปี"]}</strong></td>')
expect(_F, "§8 หน้าต่างสัญญาณ", f'<strong>{_lb["หน้าต่างของสัญญาณ(วัน)"]} วัน</strong> — วันติดกันใช้ข้อมูลร่วมกัน '
                                 f'{_lb["หน้าต่างของสัญญาณ(วัน)"] - 1} ใน {_lb["หน้าต่างของสัญญาณ(วัน)"]} วัน')
expect(_F, "§8 เดิมพันอิสระที่มีจริง",
       f'{_lb["วันต่อปีของสินทรัพย์เดียว"]} ÷ {_lb["หน้าต่างของสัญญาณ(วัน)"]} ≈ '
       f'<strong>{_lb["เดิมพันอิสระที่มีจริงต่อปีต่อสินทรัพย์"]} ครั้งต่อปี</strong>')
expect(_F, "§8 จำนวนสินทรัพย์ที่ต้องใช้ (แสดงการหาร)",
       f'{_lb["เดิมพันอิสระที่ต้องใช้ต่อปี"]} ÷ {_lb["เดิมพันอิสระที่มีจริงต่อปีต่อสินทรัพย์"]} = '
       f'{_lb["เดิมพันอิสระที่ต้องใช้ต่อปี"] / _lb["เดิมพันอิสระที่มีจริงต่อปีต่อสินทรัพย์"]:.1f} ปัดขึ้นเป็นสินทรัพย์ราว\n'
       f'<strong>{_lb["จำนวนสินทรัพย์ที่ต้องใช้"]} ตัว</strong>')
expect(_F, "§8 คริปโตกี่เหรียญ",
       f'คริปโต{_lb["จำนวนสินทรัพย์ที่ต้องใช้"]}เหรียญที่ขยับตาม BTC พร้อมกันหมด')
expect(_F, "§3 จำนวนรอบจำลอง", f"ทำซ้ำ {_IC['วิธีวัด']['จำนวนรอบจำลองฐาน']:,} รอบ")


# ── statarb-neutrality — ทุกตัวเลขผูกกับ docs/neutrality-figures.json ──
_NT = _mf._load("neutrality-figures.json")
_FN = "statarb-neutrality.html"
_L = {r["ขั้น"]: r for r in _NT["ขั้นบันไดความเป็นกลาง"]}
_TL = {r["ขั้น"]: r for r in _NT["หางซ้าย"]["ผลของแต่ละขั้น"]}
_naive, _dol = "ไม่ทำอะไรเลย", "ขั้น 1 · dollar-neutral"
_bet, _fac = "ขั้น 2 · beta-neutral", "ขั้น 3 · factor-neutral"

expect(_FN, "ข้อมูล · จำนวนวัน",
       f"(= ผลตอบแทน {_NT['ข้อมูล']['จำนวนวันผลตอบแทน']} วัน) ชุดเดียวกับทุกบทในคลัง")
expect(_FN, "ข้อมูล · จำนวนเหรียญ", f"เหรียญสมมติ {len(_NT['ข้อมูล']['เบต้าจริง'])} ตัว")

# §1 ฉากของมิน ต้องตรงกับวันแย่ที่สุดจริงของพอร์ตที่ไม่ทำอะไร
_bmin, _bmax = min(_NT["ข้อมูล"]["เบต้าจริง"]), max(_NT["ข้อมูล"]["เบต้าจริง"])
_mkt1 = _TL[_naive]["ผลตอบแทนตลาดวันนั้นเปอร์เซ็นต์"]
expect(_FN, "§1 ตลาดขึ้นเท่าไรวันนั้น", f"BTC วิ่งขึ้น {_mkt1:.2f}%")
expect(_FN, "§1 เลขคณิตของฉาก",
       f"({_bmax} − {_bmin}) × {_mkt1:.2f}% = <strong>{(_bmax - _bmin) * _mkt1:.1f}%</strong>")
expect(_FN, "§4 วันเดียวกัน dollar-neutral เสียเท่าไร", "พอร์ต dollar-neutral เสียแค่ −0.908%")

# §2–§4 บันได exposure
expect(_FN, "§2 exposure ตลาด ลดลง",
       f"ลดจาก {_L[_naive]['exposureตลาดสัมบูรณ์เฉลี่ย']:.3f} เหลือ {_L[_dol]['exposureตลาดสัมบูรณ์เฉลี่ย']:.3f}")
expect(_FN, "§2 exposure ปัจจัยสอง ไม่ขยับ",
       f"({_L[_naive]['exposureปัจจัยสองสัมบูรณ์เฉลี่ย']:.3f} → {_L[_dol]['exposureปัจจัยสองสัมบูรณ์เฉลี่ย']:.3f})")
expect(_FN, "§2 ตัวอย่าง β สุดขั้ว",
       f"ซื้อเหรียญที่ β = {min(_NT['ข้อมูล']['เบต้าจริง'])} ด้วยเงิน 100 แล้วชอร์ตเหรียญที่ β = {max(_NT['ข้อมูล']['เบต้าจริง'])}")
_spanb = max(_NT['ข้อมูล']['เบต้าจริง']) - min(_NT['ข้อมูล']['เบต้าจริง'])
expect(_FN, "§2 ผลของ β ต่าง",
       f"({max(_NT['ข้อมูล']['เบต้าจริง'])} − {min(_NT['ข้อมูล']['เบต้าจริง'])}) × 1% = <strong>{_spanb:.1f}%</strong>")
expect(_FN, "§3 exposure ตลาด ขั้นสอง",
       f"ลดจาก {_L[_dol]['exposureตลาดสัมบูรณ์เฉลี่ย']:.3f} เหลือ <strong>{_L[_bet]['exposureตลาดสัมบูรณ์เฉลี่ย']:.3f}</strong>")
expect(_FN, "§3 ปัจจัยสองยังไม่ขยับ",
       f"({_L[_dol]['exposureปัจจัยสองสัมบูรณ์เฉลี่ย']:.3f} → {_L[_bet]['exposureปัจจัยสองสัมบูรณ์เฉลี่ย']:.3f})")
expect(_FN, "§4 exposure ปัจจัยสอง ขั้นสาม",
       f"ลดจาก {_L[_bet]['exposureปัจจัยสองสัมบูรณ์เฉลี่ย']:.3f} เหลือ <strong>{_L[_fac]['exposureปัจจัยสองสัมบูรณ์เฉลี่ย']:.3f}</strong>")

_n_assets = len(_NT["ข้อมูล"]["เบต้าจริง"])
expect(_FN, "§4 มิติที่เหลือ",
       f"เหลือ {_n_assets} − 2 − 1 = <strong>{_n_assets - 3} มิติจาก {_n_assets}</strong>")
expect(_FN, "§4 กำไรขั้นต้นลดลงตามขั้น",
       f"{_L[_dol]['กำไรรวมเปอร์เซ็นต์']:.1f}% ที่ขั้น 1 → {_L[_bet]['กำไรรวมเปอร์เซ็นต์']:.1f}% ที่ขั้น 2")
expect(_FN, "§4 แถว naive หักล้างความสัมพันธ์",
       f"กลับได้แค่ {_L[_naive]['กำไรรวมเปอร์เซ็นต์']:.2f}%")
expect(_FN, "§4 กำไรที่มาจากตลาดของ naive",
       f"<strong>{_L[_naive]['กำไรที่มาจากตลาดเปอร์เซ็นต์']:+.2f}%</strong>".replace("-", "−"))
expect(_FN, "§4 กำไรที่มาจากตลาดของ dollar",
       f"<strong>{_L[_dol]['กำไรที่มาจากตลาดเปอร์เซ็นต์']:+.2f}%</strong>".replace("-", "−"))
expect(_FN, "§4 จำนวนวันที่เดินพอร์ต", f"ในช่วง {_L[_fac]['จำนวนวัน']} วันนี้")

# §4 หางซ้าย
_k5 = "ค่าสัมบูรณ์เฉลี่ยของกำไร5วันที่ตลาดขยับแรงสุด"
expect(_FN, "§4 แกว่งวันตลาดเหวี่ยง ก่อน", f"แกว่งเฉลี่ย <strong>±{_TL[_naive][_k5]:.2f}%</strong>")
expect(_FN, "§4 แกว่งวันตลาดเหวี่ยง หลัง", f"แกว่งแค่ <strong>±{_TL[_fac][_k5]:.2f}%</strong>")
expect(_FN, "§4 วันแย่สุดของ dollar-neutral",
       f"วันแย่ที่สุดเสีย {_TL[_dol]['วันแย่ที่สุดเปอร์เซ็นต์']:.3f}% ในวันที่ตลาดแทบไม่ขยับเลย "
       f"({_TL[_dol]['ผลตอบแทนตลาดวันนั้นเปอร์เซ็นต์']:.3f}%)".replace("-", "−"))
expect(_FN, "§4 ขาดทุนสะสมสูงสุดแย่ลง",
       f"<strong>{_TL[_fac]['ขาดทุนสะสมสูงสุดเปอร์เซ็นต์']:.3f}%</strong> ซึ่ง <em>แย่กว่า</em> ขั้นที่ 1 "
       f"ที่ {_TL[_dol]['ขาดทุนสะสมสูงสุดเปอร์เซ็นต์']:.3f}%".replace("-", "−"))

# §5 ความผิดพลาดของ β
_B = _NT["ความผิดพลาดของเบต้า"]; _R = _NT["exposureที่เหลือจริง"]
_w2 = max(_B["รายเหรียญ"], key=lambda r: r["ความคลาดเคลื่อนสัมบูรณ์เฉลี่ย"])
expect(_FN, "§5 หน้าต่างประมาณ", f"OLS หน้าต่าง {_B['หน้าต่างที่ใช้ประมาณ']} วัน")
expect(_FN, "§5 ความคลาดเคลื่อน",
       f"<strong>คลาดเคลื่อนเฉลี่ย {_B['ความคลาดเคลื่อนสัมบูรณ์เฉลี่ยทั้งแผง']:.3f} "
       f"และเคยพลาดถึง {_B['ความคลาดเคลื่อนสัมบูรณ์สูงสุด']:.3f}</strong>")
expect(_FN, "§5 เหรียญที่แย่ที่สุด · β จริง", f"β จริงคือ <strong>{_w2['เบต้าจริง']:.3f}</strong>")
expect(_FN, "§5 เหรียญที่แย่ที่สุด · ช่วง",
       f"<strong>{_w2['เบต้าประมาณต่ำสุด']:.3f} ถึง {_w2['เบต้าประมาณสูงสุด']:.3f}</strong>")
expect(_FN, "§5 เหรียญที่แย่ที่สุด · เฉลี่ย", f"เฉลี่ยได้แค่ <strong>{_w2['เบต้าประมาณเฉลี่ย']:.3f}</strong>")
expect(_FN, "§5 exposure ที่เหลือ (ประมาณ)", f"exposure ที่เหลือจริง <strong>{_R['exposureเหลือเมื่อใช้เบต้าประมาณ']:.3f}</strong>")
expect(_FN, "§5 exposure ที่เหลือ (β จริง)", f"exposure ที่เหลือจริง <strong>{_R['exposureเหลือถ้ารู้เบต้าจริง']:.3f}</strong> พอดีเป๊ะ")

# §6 turnover
_T = _NT["turnoverControl"]; _F0 = _T["สัญญาณเร็ว"]["ไม่คุมเลย"]; _S0 = _T["สัญญาณช้า"]["ไม่คุมเลย"]
_FB, _SB = _T["สัญญาณเร็ว"]["ดีที่สุด"], _T["สัญญาณช้า"]["ดีที่สุด"]
_D = _NT["ความเร็วที่alphaเสื่อม"]
expect(_FN, "§6 turnover ของสัญญาณเร็ว",
       f"<strong>เปลี่ยนมือเฉลี่ย {_F0['turnoverเฉลี่ยต่อวัน']:.2f} เท่าของพอร์ตต่อวัน</strong>")
expect(_FN, "§6 ต้นทุนกินเท่าไร",
       f"ที่ต้นทุนไป-กลับ {_NT['ข้อมูล']['ต้นทุนไปกลับbps']} bps กินไป <strong>{_F0['ต้นทุนรวมเปอร์เซ็นต์']:.2f}%</strong>")
expect(_FN, "§6 กำไรขั้นต้นที่ถูกกิน", f"จากกำไรขั้นต้น {_F0['กำไรรวมเปอร์เซ็นต์']:.2f}%")
# IC ต้องมาคู่ SE เสมอ — ตารางในบทแสดง IC ± 2SE และ t ทุกช่อง
for _h in ("1 วัน", "2 วัน", "3 วัน", "5 วัน"):
    for _nm in ("สัญญาณเร็ว", "สัญญาณช้า"):
        _x = _D[_nm][_h]
        expect(_FN, f"ตาราง §6 · {_nm} {_h}",
               f'<td class="nw">{_x["IC"]:+.3f} ± {2 * _x["SE"]:.3f}</td>'.replace("-", "−"))
expect(_FN, "§6 t สูงสุดของสัญญาณเร็ว",
       f'ค่าที่สูงที่สุดของมันคือ t = {_D["สัญญาณเร็ว"]["1 วัน"]["tstat"]:+.2f}')
expect(_FN, "§6 สัญญาณช้าหลุดฐานที่ไหน",
       f'(t = {_D["สัญญาณช้า"]["2 วัน"]["tstat"]:+.2f} · {_D["สัญญาณช้า"]["3 วัน"]["tstat"]:+.2f} · '
       f'{_D["สัญญาณช้า"]["5 วัน"]["tstat"]:+.2f})')
expect(_FN, "§6 IC สองตัวแยกกันไม่ออก",
       f'เพราะ {_D["สัญญาณเร็ว"]["1 วัน"]["IC"]:.3f} กับ {_D["สัญญาณช้า"]["1 วัน"]["IC"]:.3f}')
# ตารางเทียบต้องมีจำนวนวัน และตัวเลขต่อวัน (ยอดรวมเทียบกันตรง ๆ ไม่ได้)
for _lab, _g in (("เร็ว", _F0), ("ช้า", _S0)):
    expect(_FN, f"ตาราง §6 · {_lab} จำนวนวัน", f'<td class="nw">{_g["จำนวนวัน"]}</td>')
    expect(_FN, f"ตาราง §6 · {_lab} กำไรขั้นต้นต่อวัน", f'{_g["กำไรขั้นต้นต่อวันเปอร์เซ็นต์"]:.4f}%')
    expect(_FN, f"ตาราง §6 · {_lab} กำไรสุทธิต่อวัน", f'{_g["กำไรสุทธิต่อวันเปอร์เซ็นต์"]:.4f}%')
expect(_FN, "§6 ส่วนต่างจำนวนวัน", f'เริ่มเดินช้ากว่า {_F0["จำนวนวัน"] - _S0["จำนวนวัน"]} วัน')
expect(_FN, "ตาราง §6 · กำไรสุทธิที่ λ ดีที่สุด (เร็ว)",
       f'{_FB["กำไรสุทธิเปอร์เซ็นต์"]:.3f}% (λ = {_FB["ความเร็วปรับพอร์ต"]:g})')
expect(_FN, "ตาราง §6 · กำไรสุทธิที่ λ ดีที่สุด (ช้า)",
       f'{_SB["กำไรสุทธิเปอร์เซ็นต์"]:.3f}% (λ = {_SB["ความเร็วปรับพอร์ต"]:g})')
expect(_FN, "§6 เท่าตัวของ turnover",
       f"turnover สูงกว่า <strong>{_F0['turnoverเฉลี่ยต่อวัน']/_S0['turnoverเฉลี่ยต่อวัน']:.1f} เท่า</strong>")
expect(_FN, "§6 เท่าตัวของต้นทุนต่อวัน",
       f"จ่ายค่าธรรมเนียมต่อวันมากกว่า <strong>{_F0['ต้นทุนต่อวันเปอร์เซ็นต์']/_S0['ต้นทุนต่อวันเปอร์เซ็นต์']:.1f} เท่า</strong>")
# การรั่วของความเป็นกลางเมื่อไม่ฉายซ้ำ — ตัวเลขนี้บทยกมาเป็นหลักฐาน
_GF = _T["สัญญาณเร็ว"]["ที่ลอง"]
expect(_FN, "§6 ช่วง exposure หลังฉายซ้ำ",
       f'อยู่ราว\n{min(g["exposureตลาดสัมบูรณ์เฉลี่ย"] for g in _GF):.3f}–'
       f'{max(g["exposureตลาดสัมบูรณ์เฉลี่ย"] for g in _GF):.3f} ตลอดทุกค่า λ')
expect(_FN, "§6 เดินเลขต้นทุน",
       f'{_F0["turnoverเฉลี่ยต่อวัน"]:.3f} × {_NT["ข้อมูล"]["ต้นทุนไปกลับbps"]/2/100:g}% × '
       f'{_F0["จำนวนวัน"]} วัน ≈ {_F0["ต้นทุนรวมเปอร์เซ็นต์"]:.2f}%')
expect(_FN, "§6 λ ที่แย่ของสัญญาณช้า",
       f"สัญญาณช้าที่ λ = {max(g['ความเร็วปรับพอร์ต'] for g in _T['สัญญาณช้า']['ที่ลอง'] if g['กำไรสุทธิเปอร์เซ็นต์'] < 0):g}")
expect(_FN, "§6 จำนวน λ ที่ลอง",
       f"ที่ {_F0['จำนวนวัน']} วันกับ {len(_T['สัญญาณเร็ว']['ที่ลอง'])} ค่า λ")
expect(_FN, "§6 ระยะห่างที่เล็กเกินเชื่อ",
       f"ระยะห่างระหว่าง {_FB['กำไรสุทธิเปอร์เซ็นต์']:.3f}% กับ {_F0['กำไรสุทธิเปอร์เซ็นต์']:.3f}%")

# §7 สรุป
expect(_FN, "§7 β ผิดเฉลี่ยในสรุป",
       f"β ที่ผิดเฉลี่ย {_B['ความคลาดเคลื่อนสัมบูรณ์เฉลี่ยทั้งแผง']:.2f} ทำให้พอร์ตที่ \"beta-neutral\" "
       f"เหลือ exposure {_R['exposureเหลือเมื่อใช้เบต้าประมาณ']:.2f}")


# ── 2·E (math-part10) §10.1 SE(Sharpe) · §10.2 Sortino/ความเบ้ · §11.1–11.3 Kelly · §11.4 drawdown ──
_M10 = "math-part10.html"
for _nm in ("m10-sml", "m10-kelly", "m10-drawdown"):
    _mf.FIGS[(_M10, _nm)]()          # เรียก generator ของภาพเพื่อให้ NUMS มีค่าที่มันคำนวณจริง

# §10.1 ช่วงความเชื่อมั่นของ Sharpe (Lo 2002) — SE ≈ √((1 + S²/504)/T)
def _se_sharpe(S, T):
    return math.sqrt((1 + S * S / 504) / T)
_ci = {(S, T): (S - 1.96 * _se_sharpe(S, T), S + 1.96 * _se_sharpe(S, T)) for S in (1.0, 2.0) for T in (3, 10)}
print("2·E §10.1  ช่วง 95% ของ Sharpe: " + " · ".join(
    f"S={S} T={T}ปี [{lo:.2f}, {hi:.2f}]" for (S, T), (lo, hi) in _ci.items()))
for _S, _T in ((1.0, 3), (1.0, 10), (2.0, 3), (2.0, 10)):
    _lo, _hi = _ci[(_S, _T)]
    expect(_M10, f"§10.1 ช่วง 95% S={_S} T={_T}ปี", f"[{_lo:.2f}, {_hi:.2f}]".replace("-", "−"))

# §10.2 Sharpe เท่ากันแต่ความเบ้ต่างกัน — โค้ดในบท (seed 5 · 1000 วัน)
def _sortino_data():
    """ตรงกับโค้ดในบท: seed 5 · n=1000 · sd=0.012 · mu=0.0008 · B เบ้ซ้าย 90/10"""
    rng = np.random.default_rng(5)
    n, sd, mu = 1000, 0.012, 0.0008
    A = rng.normal(0, 1, n); A = (A - A.mean()) / A.std()
    B = np.where(rng.random(n) < 0.90, rng.normal(0.45, 0.35, n), rng.normal(-4.0, 1.2, n))
    B = (B - B.mean()) / B.std()
    return A * sd + mu, B * sd + mu


def _ratios(x, rf=0.02):
    ann = x.mean() * 252
    total_sd = x.std() * np.sqrt(252)
    down_sd = np.sqrt(np.mean(np.minimum(x, 0.0) ** 2)) * np.sqrt(252)
    return ann, (ann - rf) / total_sd, (ann - rf) / down_sd


_A, _B = _sortino_data()
_annA, _shA, _soA = _ratios(_A); _annB, _shB, _soB = _ratios(_B)
_wrong = lambda x: (x.mean() * 252 - 0.02) / (x[x < 0].std() * np.sqrt(252))
_wrA, _wrB = _wrong(_A), _wrong(_B)
_fl = np.where(np.random.default_rng(1).random(1000) < 0.5, 0.01, -0.01)
_fl_so = (_fl.mean() * 252 - 0.02) / (np.sqrt(np.mean(np.minimum(_fl, 0) ** 2)) * np.sqrt(252))
print(f"2·E §10.2  A: {_annA:.1%} Sharpe {_shA:.2f} Sortino {_soA:.2f} แย่สุด {_A.min():.1%} · "
      f"B: {_annB:.1%} Sharpe {_shB:.2f} Sortino {_soB:.2f} แย่สุด {_B.min():.1%} · "
      f"สูตรผิด {_wrA:.2f}/{_wrB:.2f} (ต่าง {_wrA/_wrB:.1f} เท่า) · สูตรถูกต่าง {_soA/_soB:.2f} เท่า · stop ตายตัว {_fl_so:.2f}")
expect(_M10, "§10.2 A ผลลัพธ์", f"A สมมาตร: ผลตอบแทน {_annA:.1%} | Sharpe {_shA:.2f} | Sortino {_soA:.2f} | แย่สุด {_A.min():.1%}")
expect(_M10, "§10.2 B ผลลัพธ์", f"B เบ้ซ้าย: ผลตอบแทน {_annB:.1%} | Sharpe {_shB:.2f} | Sortino {_soB:.2f} | แย่สุด {_B.min():.1%}")
expect(_M10, "§10.2 สูตรผิด", f"A = {_wrA:.2f} | B = {_wrB:.2f}")
expect(_M10, "§10.2 อัตราส่วนสูตรถูก", f"{_soA:.2f} vs {_soB:.2f} (ต่าง {_soA/_soB:.2f} เท่า)")
expect(_M10, "§10.2 อัตราส่วนสูตรผิด", f"สูตรผิดให้ {_wrA:.2f} vs {_wrB:.2f} (ต่าง {_wrA/_wrB:.1f} เท่า)")
expect(_M10, "§10.2 Sortino ของ stop ตายตัว", f"สูตรถูกให้ <strong>{_fl_so:.2f}</strong>")

# §10.3–10.4 CAPM/alpha — ตัวเดียวกับภาพ m10-sml
_sml = _mf.NUMS["m10-sml"]
print(f"2·E §10.4  CAPM ที่ β=1.5: {_sml['capm']:.1%} · alpha {_sml['alpha']:+.1%}")
expect(_M10, "§10.4 alpha จากภาพ", f"alpha = {_sml['alpha']*100:+.1f}%")

# §11.1–11.2 Kelly — เส้นโค้ง g(f) และการจำลอง 10,000 เส้นทาง (seed 42 · 200 งวด)
_k = _mf.NUMS["m10-kelly"]
print(f"2·E §11.1  Kelly f* = {_k['fstar']:.0%} · g สูงสุด {_k['gmax']*100:.3f}%/งวด · "
      f"ตัดศูนย์ที่ {_k['f0']*100:.2f}% = {_k['f0']/_k['fstar']:.2f}×Kelly")
expect(_M10, "§11.2 จุดตัดศูนย์", f"<strong>{_k['f0']*100:.2f}% = {_k['f0']/_k['fstar']:.2f}×Kelly</strong>")


def _kelly_paths(p=0.55, N=10_000, T=200, fracs=(0.02, 0.05, 0.10, 0.25, 0.40)):
    """ตรงกับโค้ดในบท: seed 42 · กริดแพ้ชนะสุ่มล่วงหน้าชุดเดียว ใช้ซ้ำทุกขนาดเดิมพัน"""
    rng = np.random.default_rng(42)
    wins = rng.random((N, T)) < p
    out = {}
    for frac in fracs:
        w = np.ones(N)
        for t in range(T):
            w *= np.where(wins[:, t], 1 + frac, 1 - frac)
        out[frac] = w
    return out


_paths = _kelly_paths()
_med = {f: float(np.median(w)) for f, w in _paths.items()}
_half = {f: float((w < 0.5).mean()) for f, w in _paths.items()}
print("2·E §11.2  " + " · ".join(f"f={f:.0%} มัธยฐาน {_med[f]:.2f} จบต่ำกว่าครึ่งทุน {_half[f]:.1%}" for f in _paths))
for _f in (0.02, 0.05, 0.10, 0.25, 0.40):
    expect(_M10, f"§11.2 ผลจำลอง f={_f:.0%}",
           f"เดิมพัน {_f:>3.0%}: มัธยฐาน {_med[_f]:6.2f} เท่า | จบต่ำกว่าครึ่งทุน {_half[_f]:.1%}")
# ตารางเปิดบท (ค่าชุดเดียวกัน คนละรูปแบบ)
for _f, _cell in ((0.02, f"{_med[0.02]:.2f} เท่า"), (0.05, f"{_med[0.05]:.2f} เท่า"),
                  (0.10, f"<strong>{_med[0.10]:.2f} เท่า</strong> ← สูงสุด"),
                  (0.25, f"<strong>{_med[0.25]:.2f} เท่า</strong> ← ขาดทุน!"),
                  (0.40, f"<strong>{_med[0.40]:.4f} เท่า</strong> ← แทบไม่เหลือ")):
    expect(_M10, f"§เปิดเรื่อง ตารางมัธยฐาน f={_f:.0%}", _cell)
expect(_M10, "§เปิดเรื่อง ตารางโอกาสเจ็บ f=40%", f"<strong>{_half[0.40]:.1%}</strong></td></tr>")
# ค่าเฉลี่ยตามทฤษฎีที่ f = 40% กับสัดส่วนที่เหลือไม่ถึง 1% ของทุน
_mean40 = (0.55 * 1.4 + 0.45 * 0.6) ** 200
_ruin40 = float((_paths[0.40] < 0.01).mean())
print(f"2·E §11.2  ที่ f=40%: ค่าเฉลี่ยตามทฤษฎี {_mean40:,.0f} เท่า · เหลือไม่ถึง 1% ของทุน {_ruin40:.0%} · "
      f"ค่าเฉลี่ยที่จำลองได้จริง {_paths[0.40].mean():.0f} เท่า")
expect(_M10, "§11.2 ค่าเฉลี่ยตามทฤษฎีที่ f=40%", f"<strong>{_mean40:,.0f} เท่า</strong>")
expect(_M10, "§11.2 เหลือไม่ถึง 1% ของทุน", f"<strong>{_ruin40:.0%} เหลือเงินไม่ถึง 1% ของที่เริ่มมา</strong>")

# §11.3 half-Kelly เทียบ Kelly เต็ม — ตัวเลข "ต่างกัน" ในตาราง
print(f"2·E §11.3  Kelly เต็มโตกว่า half {_med[0.10]/_med[0.05]-1:.0%} · เสี่ยงกว่า {_half[0.10]/_half[0.05]:.0f} เท่า")
expect(_M10, "§11.3 Kelly ดีกว่ากี่ %", f"Kelly ดีกว่า {_med[0.10]/_med[0.05]-1:.0%}")
expect(_M10, "§11.3 Kelly เสี่ยงกว่ากี่เท่า", f"Kelly เสี่ยงกว่า {_half[0.10]/_half[0.05]:.0f} เท่า")
expect(_M10, "§11.3 มองจากฝั่ง Kelly เต็ม",
       f"ยอมเสียกำไรไป <strong>{1-_med[0.05]/_med[0.10]:.0%}</strong> ({_med[0.10]:.2f} → {_med[0.05]:.2f} เท่า)")
expect(_M10, "§11.3 สองฐานคือคู่เดียวกัน",
       f"(ขึ้นจาก {_med[0.05]:.2f} คิด {_med[0.10]/_med[0.05]-1:.0%} · ลงจาก {_med[0.10]:.2f} คิด {1-_med[0.05]/_med[0.10]:.0%})")

# §11.4 drawdown — โค้ดในบท (seed 17 · 1000 วัน) ตัวเดียวกับภาพ m10-drawdown
_dd = _mf.NUMS["m10-drawdown"]
_total, _mdd, _shd = _dd["total"], _dd["mdd"], _dd["sharpe"]
_t2b, _rec = _dd["top_to_bottom"], _dd["recov"]
print(f"2·E §11.4  กำไรรวม {_total:+.0%} · Sharpe {_shd:.2f} · MDD {_mdd:.1%} · "
      f"ยอด→ก้น {_t2b} วัน · ก้น→เท่าทุน {_rec} วัน · รวม {_t2b+_rec} วัน · ต้องกำไร {1/(1+_mdd)-1:.0%}")
expect(_M10, "§11.4 กำไรรวม", f"<strong>กำไรรวม {_total:+.0%}</strong>")
expect(_M10, "§11.4 Sharpe", f"(Sharpe {_shd:.2f} ถือว่าดี)")
expect(_M10, "§11.4 MDD", f"<strong>Max Drawdown = {_mdd:.1%}</strong>".replace("-", "−"))
expect(_M10, "§11.4 ยอดถึงก้น", f"<strong>ใช้เวลา {_t2b} วันจากยอดถึงก้น</strong>")
expect(_M10, "§11.4 ก้นถึงเท่าทุน", f"<strong>อีก {_rec} วันกว่าจะกลับเท่าทุนเดิม</strong>")
expect(_M10, "§11.4 รวมวันที่เจ็บ", f"รวม <strong>{_t2b+_rec} วัน</strong>")
expect(_M10, "§11.4 ต้องกำไรเท่าไรถึงกลับเท่าทุน", f"ต้องทำกำไร <strong>{1/(1+_mdd)-1:.0%}</strong> เพื่อกลับจากหลุม {_mdd:.1%}".replace("-", "−"))
expect(_M10, "§11.4 ผลรันในโค้ด MDD", f"Max Drawdown   = {_mdd:.1%}")
expect(_M10, "§11.4 ผลรันในโค้ด ระยะเวลา", f"ยอด→ก้น {_t2b} วัน · ก้น→เท่าทุน {_rec} วัน · รวม {_t2b+_rec} วัน")


# §11.3 กฎ "ครึ่ง Kelly ได้ 75%" — g(k·f*)/g(f*) = 2k − k² และกฎ drawdown ของ fractional Kelly
def _g(f, p=0.55, b=1.0):
    return p * math.log(1 + b * f) + (1 - p) * math.log(1 - f)
_gstar = _g(_k["fstar"])
_krows = [0.25, 0.5, 1.0, 1.5, 2.0]
print("2·E §11.3  " + " · ".join(f"k={kk}: สูตร {2*kk-kk*kk:.4f} จริง {_g(kk*_k['fstar'])/_gstar:.4f}" for kk in _krows))
for _kk in _krows:
    expect(_M10, f"§11.3 ตาราง 2k−k² ที่ k={_kk}", f"<td class=\"nw\">{2*_kk-_kk*_kk:.4f}</td>".replace("-", "−")
           if _kk not in (0.5, 1.0) else f"{2*_kk-_kk*_kk:.4f}")
    expect(_M10, f"§11.3 ตารางเกมเหรียญจริงที่ k={_kk}",
           f"{_g(_kk*_k['fstar'])/_gstar:.4f}".replace("-", "−"))
expect(_M10, "§11.3 half-Kelly ได้ 75%", f"2(0.5) − 0.5² = {2*0.5-0.25:.2f}")

# ความน่าจะเป็นที่เงินจะ "เคยแตะ" x เท่าของทุน — ทฤษฎีเวลาไม่จำกัด เทียบกับกริดจำลอง 200 งวด
def _touch_prob(frac, p=0.55, N=10_000, T=200):
    rng = np.random.default_rng(42)
    wins = rng.random((N, T)) < p
    w = np.ones(N); lo = np.ones(N)
    for t in range(T):
        w *= np.where(wins[:, t], 1 + frac, 1 - frac); lo = np.minimum(lo, w)
    return float((lo < 0.5).mean())
_touch = {kk: _touch_prob(kk * _k["fstar"]) for kk in (0.5, 1.0)}
_theory = {kk: 0.5 ** (2 / kk - 1) for kk in (0.5, 1.0)}
print(f"2·E §11.3  เคยแตะครึ่งทุน: Kelly เต็ม {_touch[1.0]:.1%} (ทฤษฎี {_theory[1.0]:.0%}) · "
      f"half-Kelly {_touch[0.5]:.1%} (ทฤษฎี {_theory[0.5]:.1%}) · อัตราส่วนจำลอง {_touch[1.0]/_touch[0.5]:.1f} เท่า")
expect(_M10, "§11.3 ทฤษฎี Kelly เต็มแตะครึ่งทุน", f"0.5^1 = {_theory[1.0]:.0%}")
expect(_M10, "§11.3 ทฤษฎี half-Kelly แตะครึ่งทุน", f"0.5^3 = {_theory[0.5]:.1%}")
expect(_M10, "§11.3 จำลอง Kelly เต็มแตะครึ่งทุน", f"เคยแตะครึ่งทุน <strong>{_touch[1.0]:.1%}</strong>")
expect(_M10, "§11.3 จำลอง half-Kelly แตะครึ่งทุน", f"เคยแตะครึ่งทุน <strong>{_touch[0.5]:.1%}</strong>")
expect(_M10, "§11.3 อัตราส่วนความเสี่ยงจากการจำลอง",
       f"การจำลองได้ {_touch[1.0]/_touch[0.5]:.1f} เท่า ({_touch[1.0]*100:.1f} ต่อ {_touch[0.5]*100:.1f})")
expect(_M10, "§11.3 อัตราส่วนความเสี่ยงตามสูตร",
       f"สูตรบอกเสี่ยงต่างกัน {_theory[1.0]/_theory[0.5]:.0f} เท่า ({_theory[1.0]*100:.0f} ต่อ {_theory[0.5]*100:.1f})")


# §11.2 ค่าเฉลี่ยที่ f = 40% ประมาณจากข้อมูลไม่ได้ — มัธยฐานนิ่ง ค่าเฉลี่ยกระโดดตาม seed
def _f40(seed, p=0.55, N=10_000, T=200, frac=0.40):
    rng = np.random.default_rng(seed)
    wins = rng.random((N, T)) < p
    w = np.ones(N)
    for t in range(T):
        w *= np.where(wins[:, t], 1 + frac, 1 - frac)
    return float(w.mean()), float(np.median(w))
_seeds = [42, 1, 2, 3, 7]
_mm = [_f40(sd) for sd in _seeds]
print("2·E §11.2  f=40% คนละ seed: ค่าเฉลี่ย " + " · ".join(f"{m:,.0f}" for m, _ in _mm)
      + " | มัธยฐาน " + " · ".join(f"{md:.4f}" for _, md in _mm))
assert len({f"{md:.4f}" for _, md in _mm}) == 1, "มัธยฐานควรเท่ากันทั้งห้า seed"
expect(_M10, "§11.2 ค่าเฉลี่ยที่จำลองได้จริง",
       f"ค่าเฉลี่ยที่วัดได้จาก 10,000 เส้นทางจริงคือ {_mm[0][0]:,.0f} เท่า ไม่ใช่ {_mean40:,.0f}</strong>")
expect(_M10, "§11.2 ค่าเฉลี่ยห้า seed", "<strong>" + " · ".join(f"{m:,.0f}" for m, _ in _mm) + "</strong>")
expect(_M10, "§11.2 มัธยฐานนิ่งทั้งห้า seed", f"<strong>มัธยฐานได้ {_mm[0][1]:.4f} เท่ากันทั้งห้าครั้ง</strong>")

# §11.2 สูตร Kelly ทั่วไป f* = p/a − q/b — เทรดที่มี stop
def _kelly_gen(p, a, b):
    return p / a - (1 - p) / b
_p, _b = 0.45, 0.10
_ev = _p * _b - (1 - _p) * 0.05
_f_a5, _f_a8 = _kelly_gen(_p, 0.05, _b), _kelly_gen(_p, 0.08, _b)
print(f"2·E §11.2  สูตรทั่วไป: ตรวจกับเหรียญ {_kelly_gen(0.55, 1.0, 1.0):.2f} · "
      f"EV {_ev:+.2%} · a=5% → f*={_f_a5:.3f} · a=8% → f*={_f_a8:.3f} · หดลง {_f_a5/_f_a8:.0f} เท่า")
expect(_M10, "§11.2 ทั่วไป ตรวจกับเกมเหรียญ", f"0.55 ÷ 1 − 0.45 ÷ 1 = {_kelly_gen(0.55, 1.0, 1.0):.2f}")
expect(_M10, "§11.2 ทั่วไป ค่าคาดหวังต่อหน่วยสถานะ",
       f"0.45 × 10% − 0.55 × 5% = <strong>{_ev:+.2%}</strong>")
expect(_M10, "§11.2 ทั่วไป f* ที่ stop 5%", f"f* = 0.45 ÷ 0.05 − 0.55 ÷ 0.10 = 9 − 5.5 = <b>{_f_a5:.1f}</b>")
expect(_M10, "§11.2 ทั่วไป f* ที่ขาดทุนจริง 8%", f"f* = 0.45 ÷ 0.08 − 0.55 ÷ 0.10 = 5.625 − 5.5 = <b>{_f_a8:.3f}</b>")
expect(_M10, "§11.2 ทั่วไป หดกี่เท่า", f"ลดลง <strong>{_f_a5/_f_a8:.0f} เท่า</strong>")
expect(_M10, "§11.2 ทั่วไป notional 350%", f"ถือมูลค่า {_f_a5*100:.0f}% ของพอร์ต")
expect(_M10, "§11.2 ทั่วไป เหลือกี่ %", f"เหลือ {_f_a8*100:.1f}% ของพอร์ต")


# §11.4 ตารางความอสมมาตร — ขาดทุน DD แล้วต้องกำไร 1/(1+DD) − 1 ถึงเท่าทุน
_recov = {d: 1 / (1 - d) - 1 for d in (0.10, 0.20, 0.30, 0.50, 0.70, 0.90)}
print("2·E §11.4  ต้องกำไรเพื่อเท่าทุน: " + " · ".join(f"{d:.0%}→{r:.0%}" for d, r in _recov.items()))
for _d, _r in _recov.items():
    _cell = f"<strong>{_r:.0%}</strong>" if _d >= 0.50 else f"{_r:.0%}"
    expect(_M10, f"§11.4 ตารางเท่าทุนที่ขาดทุน {_d:.0%}", f"<td>{_d:.0%}</td><td class=\"nw\">{_cell}</td>")


# §11.3½ Kelly หลายสถานะ f = Σ⁻¹(μ − r_f) — 5 กลยุทธ์เหมือนกัน μ − r_f = 10% · σ = 20%
_n5, _ex5, _sd5 = 5, 0.10, 0.20
def _kelly_multi(rho, n=_n5, ex=_ex5, sd=_sd5):
    C = np.full((n, n), rho); np.fill_diagonal(C, 1.0)
    S = C * sd * sd
    return np.linalg.solve(S, np.full(n, ex)), S
def _growth(f, S, ex=_ex5):
    """อัตราเติบโตส่วนเกินเหนือ r_f แบบต่อเนื่อง g = fᵀ(μ − r_f) − fᵀΣf/2"""
    return float(f.sum() * ex - f @ S @ f / 2)
_naive5 = _n5 * _ex5 / _sd5 ** 2
_ktot = {r: float(_kelly_multi(r)[0].sum()) for r in (0.0, 0.3, 0.6, 0.9)}
print("2·E §11.3½ " + " · ".join(f"ρ={r}: ถูก {v:.2f} เกิน {_naive5/v:.1f} เท่า" for r, v in _ktot.items()))
expect(_M10, "§11.3½ Kelly เดี่ยวรวม", f"ถ้าใส่ครบ 5 ตัวก็ได้ <strong>{_naive5:.1f} เท่า</strong>")
for _r in (0.3, 0.6, 0.9):
    expect(_M10, f"§11.3½ ค่าที่ถูกที่ ρ={_r}", f"<strong>{_ktot[_r]:.2f} เท่า</strong></td><td class=\"nw\"><strong>{_naive5/_ktot[_r]:.1f} เท่า</strong>")
# 📉 คนที่ size ถูกที่ ρ = 0.3 เมื่อ ρ กระโดดเป็น 0.9
_k_shift = _ktot[0.3] / _ktot[0.9]
_f03, _ = _kelly_multi(0.3); _f09, _S09 = _kelly_multi(0.9)
_g_right, _g_stale = _growth(_f09, _S09), _growth(_f03, _S09)
print(f"2·E §11.3½ 📉 k = {_k_shift:.2f} · 2k−k² = {2*_k_shift-_k_shift**2:.2f} · "
      f"g ถูก {_g_right:+.1%} · g ค้าง {_g_stale:+.1%} · อัตราส่วน {_g_stale/_g_right:.2f} · ¼–½ → {_k_shift/4:.2f}–{_k_shift/2:.2f}")
assert abs(_g_stale / _g_right - (2 * _k_shift - _k_shift ** 2)) < 1e-9, "สองวิธีต้องได้ค่าเดียวกัน"
expect(_M10, "§11.3½📉 k หลัง ρ กระโดด", f"{_ktot[0.3]:.2f} ÷ {_ktot[0.9]:.2f} = <strong>{_k_shift:.2f} เท่าของ Kelly</strong>")
expect(_M10, "§11.3½📉 2k−k²", f"2k − k² = 2({_k_shift:.2f}) − {_k_shift:.2f}² = {2*_k_shift-_k_shift**2:.2f}".replace("-0", "−0"))
expect(_M10, "§11.3½📉 g ที่ถูก", f"size ตาม Kelly ของ ρ = 0.9   →  {_g_right:+.1%}")
expect(_M10, "§11.3½📉 g ที่ค้าง", f"size ตาม Kelly ของ ρ = 0.3   →  {_g_stale:+.1%}".replace("-", "−"))
expect(_M10, "§11.3½📉 หลังคูณ ¼–½", f"k = {_k_shift:.2f} เหลือ {_k_shift/4:.2f}–{_k_shift/2:.2f}")

# §11.2 📍 vol targeting = Kelly ที่ Sharpe คงที่: σ_พอร์ต = f*·σ = Sharpe
_SR = 0.5
expect(_M10, "§11.2📍 vol ของ Kelly เต็ม", f"กลยุทธ์ Sharpe {_SR} จึงมี Kelly เต็มที่พอร์ตเหวี่ยง {_SR:.0%} ต่อปี และ half-Kelly ที่ {_SR/2:.0%}")
expect(_M10, "§11.2📍 เป้า vol 10–15%", f"เป้า vol ไว้ 10–15% ก็เท่ากับเดิมพัน {0.10/_SR:.1f}–{0.15/_SR:.1f} เท่าของ Kelly")


# ── เล่ม 1 Part III (math-part3) — Greeks ของ Call ชุดเดียวกับ Part V §11.3 · ภาพ Gamma · Delta-Gamma ──
_M3 = "math-part3.html"
from scipy.stats import norm as _nrm  # noqa: E402


def _bs_all(S=100.0, K=100.0, r=0.05, sg=0.25, T=1.0):
    d1 = (math.log(S / K) + (r + sg * sg / 2) * T) / (sg * math.sqrt(T)); d2 = d1 - sg * math.sqrt(T)
    C = S * _nrm.cdf(d1) - K * math.exp(-r * T) * _nrm.cdf(d2)
    return dict(C=C, d1=d1, delta=_nrm.cdf(d1), delta_put=_nrm.cdf(d1) - 1,
                gamma=_nrm.pdf(d1) / (S * sg * math.sqrt(T)),
                theta_yr=-(S * _nrm.pdf(d1) * sg) / (2 * math.sqrt(T)) - r * K * math.exp(-r * T) * _nrm.cdf(d2),
                vega_pt=S * _nrm.pdf(d1) * math.sqrt(T) / 100, rho_pct=K * T * math.exp(-r * T) * _nrm.cdf(d2) / 100)


_g3 = _bs_all()
_th_day = _g3["theta_yr"] / 365
print(f"เล่ม1 III  C={_g3['C']:.3f} Δ={_g3['delta']:.4f} Δput={_g3['delta_put']:.3f} Γ={_g3['gamma']:.4f} "
      f"Θ/วัน={_th_day:.4f} ν/จุด={_g3['vega_pt']:.3f} ρ/1%={_g3['rho_pct']:.3f}")
expect(_M3, "§7.6 V Δ Γ ในข้อความ", f"V = {_g3['C']:.3f}, Δ = {_g3['delta']:.3f}, Γ = {_g3['gamma']:.4f}")
expect(_M3, "§7.3 Put Delta", f"Δ ≈ {_g3['delta_put']:.3f}".replace("-", "−"))
expect(_M3, "§7.3 ρ เทียบ Vega", f"มี ρ ≈ {_g3['rho_pct']:.2f} ต่อดอกเบี้ย +1% มากกว่า Vega {_g3['vega_pt']:.2f} ต่อ vol +1 จุด")
# hook: วันเดียวกันกับ Call อายุ 1 ปี — หุ้น +1 · เวลา 1 วัน · σ −4 จุด
_hook_long = _g3["delta"] * 1 + 0.5 * _g3["gamma"] * 1 - (-_th_day) - _g3["vega_pt"] * 4
_hook_demo = 0.5 - 0.08 - 0.12 * 4
print(f"เล่ม1 III  hook: demo {_hook_demo:+.2f} · Call 1 ปี {_hook_long:+.3f} · หนักกว่า {_hook_long/_hook_demo:.0f} เท่า")
expect(_M3, "§7.3 hook Greeks ของ Call 1 ปี",
       f"(Δ {_g3['delta']:.3f} · Γ {_g3['gamma']:.4f} · Θ {_th_day:.4f}/วัน · ν {_g3['vega_pt']:.3f}/จุด)".replace("-", "−"))
expect(_M3, "§7.3 hook ผลของ Call 1 ปี",
       f"{_g3['delta']:.3f} + ½×{_g3['gamma']:.4f} − {-_th_day:.4f} − {_g3['vega_pt']:.3f}×4 ≈ <strong>{_hook_long:.2f}</strong>".replace("-0.9", "−0.9"))
expect(_M3, "§7.3 hook หนักกว่ากี่เท่า", f"ขาดทุนหนักกว่าราว {_hook_long/_hook_demo:.0f} เท่า")

# ภาพ 7.4 — Gamma สูงสุดจริงที่ S* = K·e^(−(r+1.5σ²)T) ไม่ใช่ที่ K
for _nm in ("m3-call-curve-gamma",):
    _mf.FIGS[(_M3, _nm)]()
_cg = _mf.NUMS["m3-call-curve-gamma"]
_Ss = 100 * math.exp(-(0.05 + 1.5 * 0.20 ** 2) * 0.5)
assert abs(_cg["s_peak"] - _Ss) < 1e-9
_grid = np.linspace(60, 140, 8001)
_gg = _nrm.pdf((np.log(_grid / 100) + (0.05 + 0.02) * 0.5) / (0.2 * math.sqrt(0.5))) / (_grid * 0.2 * math.sqrt(0.5))
assert abs(_grid[_gg.argmax()] - _Ss) < 0.02, "จุดสูงสุดเชิงตัวเลขต้องตรงกับสูตร S*"
print(f"เล่ม1 III  ภาพ 7.4: Γ ที่ K = {_cg['gamma']:.4f} · สูงสุดที่ S* = {_Ss:.2f} ได้ {_cg['gamma_peak']:.4f}")

# §7.6 ตาราง Delta-Gamma เทียบราคาจริง — ผลรันของโค้ดในบท
for _dS in (1, 5, 10, 20, -10, -20):
    _tr = _bs_all(S=100 + _dS)["C"] - _g3["C"]
    _do = _g3["delta"] * _dS; _dg = _do + 0.5 * _g3["gamma"] * _dS ** 2
    expect(_M3, f"§7.6 ผลรัน dS={_dS:+d}", f"{_dS:+4d} | {_tr:+8.3f}     | {_do:+8.3f}       | {_dg:+8.3f}".lstrip())
_e20 = (_g3["delta"] * 20 + 0.5 * _g3["gamma"] * 400) - (_bs_all(S=120)["C"] - _g3["C"])
_d20 = (_bs_all(S=120)["C"] - _g3["C"]) - _g3["delta"] * 20
print(f"เล่ม1 III  +20: Delta พลาด {_d20:.2f} · Delta+Gamma พลาด {_e20:.2f}")
expect(_M3, "§7.6 Delta พลาดที่ +20", f"Delta พลาด {_d20:.1f} · Gamma เหลือพลาด {_e20:.1f}")


# ── เล่ม 1 Part IV (math-part6) — GARCH · EWMA · IV (bisection/Newton) · binomial tree ──────
_M6 = "math-part6.html"
for _h in ("พยากรณ์เส้นทาง σ หลังเกิดช็อก", "IV ด้วย 2 วิธี", "Binomial tree (CRR)"):
    expect_code(_M6, _h)
for _h in ("Delta-Gamma approx เทียบราคาจริง",):
    expect_code(_M3, _h)
for _h in ("Sharpe · Sortino", "จำลอง 10,000 เส้นทาง", "คำนวณ Max Drawdown", "stress test พอร์ต 3 สินทรัพย์"):
    expect_code(_M10, _h)

# §8.4 GARCH ω = 0.00002 · α = 0.10 · β = 0.85
_w, _a, _b = 0.00002, 0.10, 0.85
_vinf = _w / (1 - _a - _b)
_v_shock = _w + _a * 0.03 ** 2 + _b * 0.0004
_v_calm = _w + _a * 0.0 + _b * 0.0004
_hl = math.log(0.5) / math.log(_a + _b)
print(f"เล่ม1 IV  GARCH σ∞={math.sqrt(_vinf):.2%}/วัน ({math.sqrt(_vinf*252):.1%}/ปี) · หลังช็อก {math.sqrt(_v_shock):.2%} · "
      f"วันนิ่ง {math.sqrt(_v_calm):.2%} · half-life {_hl:.1f} วัน (ที่ 0.99: {math.log(.5)/math.log(.99):.0f})")
expect(_M6, "§8.4 σ²∞", f"σ²∞ = 0.00002/(1−0.95) = {_vinf:.4f}")
expect(_M6, "§8.4 σ หลังช็อก", f"= {_v_shock:.5f} → σ = <strong>{math.sqrt(_v_shock):.2%}/วัน</strong>")
expect(_M6, "§8.4 ลองทำ วันนิ่ง", f"= {_v_calm:.5f} → σ = √{_v_calm:.5f} = <strong>{math.sqrt(_v_calm):.1%}/วัน</strong>")
expect(_M6, "§8.4 half-life", f"ln 0.5 / ln 0.95 ≈ {_hl:.1f} วัน")
expect(_M6, "§8.5 half-life", f"ส่วนที่ σ² เกินระดับปกติหดเหลือครึ่งทุกราว <strong>{_hl:.1f} วัน</strong>")
expect(_M6, "§8.5 half-life ที่ 0.99", f"ที่ 0.99 ต้องรอราว {math.log(.5)/math.log(.99):.0f} วัน")
expect(_M6, "§8.4 σ∞ รายปี", f"σ∞ = 2%/วัน × √252 ≈ <strong>{math.sqrt(_vinf*252):.1%}/ปี</strong>")
# โค้ดพยากรณ์ต้องตรงกับสูตรปิด E[σ²ₜ₊ₕ] = σ²∞ + (α+β)^(h−1)(σ²ₜ₊₁ − σ²∞)
_v = 0.0009; _v1 = _w + (_a + _b) * _v
for _k in range(1, 8):
    _v = _w + (_a + _b) * _v
    assert abs(_v - (_vinf + (_a + _b) ** (_k - 1) * (_v1 - _vinf))) < 1e-15
# §8.3 EWMA λ = 0.94
expect(_M6, "§8.3 EWMA half-life และหน้าต่าง",
       f"ln 0.5 / ln 0.94 ≈ {math.log(.5)/math.log(.94):.0f} วัน · เทียบเท่าหน้าต่าง 1/(1−λ) ≈ {1/(1-0.94):.0f} วัน")

# §9 IV — Call S = K = 100 · r = 5% · T = 1 ปี · σ* = 25%
_C6 = _bs_all()["C"]
for _m, _px in ((0.505, "21.98"), (0.2575, "12.62"), (0.13375, "8.00"), (0.195625, "10.29")):
    _got = _bs_all(sg=_m)["C"]
    assert f"{_got:.2f}" == _px, (_m, _got)
    expect(_M6, f"§9.3 bisection BS({_m})", f'<td class="nw">{_got:.2f}</td>')
from scipy.optimize import brentq as _brentq  # noqa: E402
_iv15 = _brentq(lambda v: _bs_all(sg=v)["C"] - 15.0, 0.01, 2.0)
expect(_M6, "§9.3 ลองทำ IV ที่ราคา 15", f"เฉลย: IV ≈ {_iv15:.1%}")
_bs0 = math.sqrt(2 * math.pi / 1.0) * _C6 / 100
print(f"เล่ม1 IV  C={_C6:.3f} · IV(15)={_iv15:.2%} · Brenner–Subrahmanyam σ₀={_bs0:.1%} · bisection ~{math.log2(0.99/1e-4):.1f} รอบ")
expect(_M6, "§9.3 ค่าเริ่ม Brenner–Subrahmanyam", f"√(2π) × {_C6:.3f}/100 ≈ <strong>{_bs0:.1%}</strong>")
_nw = _mf.NUMS.get("m6-newton") or (_mf.FIGS[(_M6, "m6-newton")](), _mf.NUMS["m6-newton"])[1]
assert abs(_nw["price"] - _C6) < 1e-9, "ภาพ Newton ต้องใช้ Call ชุดเดียวกับโค้ดในบท"
# §10.1 tree
expect(_M6, "§10.1 ลำดับราคา tree", "(14.6 → 11.2 → 12.8 → 12.1)")



# ── เล่ม 1 Part II (math-part2) — สถิติ ความน่าจะเป็น การแจกแจง ──────────────────────────────
_M2 = "math-part2.html"
expect_code(_M2, "N(d) จาก erf")


def _bach_call(S0, K, sd):
    """ค่าของ Call = payoff เฉลี่ยเมื่อราคาปลายทาง ~ Normal(S0, sd) ไม่คิดดอกเบี้ย"""
    d = (S0 - K) / sd
    return (S0 - K) * _nrm.cdf(d) + sd * _nrm.pdf(d)


_cA, _cB = _bach_call(100, 120, 5), _bach_call(100, 120, 20)
_atm = _bach_call(100, 100, 20) / _bach_call(100, 100, 5)
print(f"เล่ม1 II  hook: Call K120 A ฿{_cA:.6f} B ฿{_cB:.3f} ต่างกัน {_cB/_cA:,.0f} เท่า · ATM {_atm:.4f} เท่า")
assert _cA < 0.01 and _cB / _cA > 40_000 and abs(_atm - 4) < 1e-12
expect(_M2, "hook ค่า Call B", f"มีค่าราว <strong>฿{_cB:.2f}</strong>")
expect(_M2, "hook ATM 4 เท่า", f"ของ B ก็ยังแพงกว่า <strong>{_atm:.0f} เท่าพอดี</strong>")
_tb = _mf.NUMS.get("m2-two-bells-strike") or (_mf.FIGS[(_M2, "m2-two-bells-strike")](), _mf.NUMS["m2-two-bells-strike"])[1]

# §4.3 σ หุ้นนิ่ง vs หุ้นเหวี่ยง — หาร n ตามสูตรในกล่อง และหาร n − 1
_ra, _rb = np.array([1, -1, 2, -2]), np.array([10, -8, 12, -14])
expect(_M2, "§4.3 σ A", f"<strong>{_ra.std():.2f}%</strong>")
expect(_M2, "§4.3 σ B", f"<strong>{_rb.std():.1f}%</strong>")
expect(_M2, "§4.3 ddof=1", f"จะได้ {_ra.std(ddof=1):.2f}% กับ {_rb.std(ddof=1):.2f}%")

# §6.3 ตาราง N(d)
for _d, _txt in ((-2.0, "−2.0"), (-1.0, "−1.0"), (0.0, "0.0"), (1.0, "+1.0"), (2.0, "+2.0")):
    expect(_M2, f"§6.3 N({_d})", f"<tr><td>{_txt}</td><td>{_nrm.cdf(_d):.3f}</td>")
expect(_M2, "§6.3 ตารางละเอียด",
       "<td><strong>N(d)</strong></td>" + "".join(f"<td>{_nrm.cdf(x):.3f}</td>".replace(">0.", ">.") for x in (0, .05, .1, .15, .2, .25, .3, .35, .4, .45, .5)))
expect(_M2, "§6.3 N(0.325)", f"ค่าเป๊ะจาก erf = {_nrm.cdf(0.325):.4f}")
_d1b = (math.log(1) + (0.05 + 0.25 ** 2 / 2)) / 0.25
assert abs(_d1b - 0.325) < 1e-12 and abs(_d1b - 0.25 - 0.075) < 1e-12, "d₁, d₂ ต้องมาจาก S = K = 100 · r = 5% · σ = 25% · T = 1"

# §6.4 Lognormal (E[S] = 100) · §6.6 หางหนา
_ln = _mf.NUMS.get("m2-normal-vs-lognormal") or (_mf.FIGS[(_M2, "m2-normal-vs-lognormal")](), _mf.NUMS["m2-normal-vs-lognormal"])[1]
expect(_M2, "§6.4 มัธยฐาน", f"มัธยฐาน = 100·e^(−0.02) = {_ln['median']:.1f}")
expect(_M2, "§6.4 ยอด", f"ยอด = 100·e^(−0.06) = {_ln['mode']:.1f}")
from scipy import stats as _st  # noqa: E402
_ft = _mf.NUMS.get("m2-fat-tails") or (_mf.FIGS[(_M2, "m2-fat-tails")](), _mf.NUMS["m2-fat-tails"])[1]
_exact = 2 * _st.t(3).sf(3 * math.sqrt(3))
assert abs(_ft["tail_t"] - _exact) < 1e-12, "หางในภาพต้องเท่าหางจริงของ t (ν = 3) ไม่ใช่ผลรวมบนกริดที่ถูกตัด"
print(f"เล่ม1 II  หางเกิน 3σ: Normal {_ft['tail_n']:.3%} · t(3) {_ft['tail_t']:.3%} · {_ft['tail_t']/_ft['tail_n']:.1f} เท่า")

# capstone — หุ้น ฿100 σ = 20%/ปี
_sm = 0.20 * math.sqrt(1 / 12)
expect(_M2, "capstone σ เดือน", f"σ เดือน = 20% × √(1/12) ≈ {_sm:.1%}")
expect(_M2, "capstone ±1σ เดือน", f"<strong>฿{100-100*_sm:.1f}–฿{100+100*_sm:.1f}</strong>")
expect(_M2, "capstone ±2σ เดือน", f"≈ ±฿{2*100*_sm:.1f} → <strong>฿{100-200*_sm:.1f}–฿{100+200*_sm:.1f}</strong>")
_med2 = 100 * math.exp(-0.02)
_p2 = _nrm.cdf((math.log(1.2) + 0.02) / 0.2) - _nrm.cdf((math.log(0.8) + 0.02) / 0.2)
expect(_M2, "capstone lognormal",
       f"มัธยฐานคือ ฿{_med2:.2f} ช่วง ±1σ คือ ฿{_med2*math.exp(-0.2):.1f}–฿{_med2*math.exp(0.2):.1f} และโอกาสจบใน ฿80–฿120 ได้ {_p2:.1%}")
expect(_M2, "capstone √(1/12) √(1/52)", f"√(1/12) ≈ {math.sqrt(1/12):.2f} · 1 สัปดาห์ ≈ √(1/52) ≈ {math.sqrt(1/52):.2f}")
# Bayes
expect(_M2, "§5.3 Bayes", f"0.90×0.60 / 0.70 = 0.54 / 0.70 ≈ <strong>{0.54/0.70:.0%}</strong>")



# ── เสาหลัก Part IV (pillars-part4) — VaR · ES · coherence · EVT · copula ─────────────────────
_P4 = "pillars-part4.html"
from scipy.stats import t as _tdist, binom as _binom, multivariate_normal as _mvn  # noqa: E402
_ve = _mf.NUMS.get("var-es-tail") or (_mf.FIGS[(_P4, "var-es-tail")](), _mf.NUMS["var-es-tail"])[1]
_z99 = _nrm.ppf(0.99); _es99 = _nrm.pdf(_z99) / 0.01
assert abs(_ve["z99"] - _z99) < 1e-12 and abs(_ve["es_mult"] - _es99) < 1e-12, "ภาพกับเนื้อต้องใช้ z ตัวเดียวกัน"
expect(_P4, "VaR ตัวอย่าง", f"→ VaR = {_z99:.3f} × 2% × $100M = <strong>${_z99*2:.2f}M</strong>")
expect(_P4, "VaR 95%", f"z = {_nrm.ppf(.95):.3f} &lt; {_z99:.3f} → VaR เล็กลง (${_nrm.ppf(.95)*2:.2f}M)")
expect(_P4, "ES fm", f"ES₉₉ = {_es99:.3f}σ &nbsp;(จาก z₉₉ = {_z99:.3f} · เทียบ VaR₉₉ = {_z99:.3f}σ)")
expect(_P4, "ES ตัวอย่าง", f"ES₉₉ = {_es99:.3f} × 2% × $100M = <strong>${_es99*2:.2f}M</strong>")
expect(_P4, "ES ส่วนต่าง", f"ส่วนต่าง ${(_es99-_z99)*2:.2f}M")


def _t4(a, sc=1 / math.sqrt(2)):
    """t (ν = 4) ปรับให้ variance = 1 · คืน VaR และ ES หางซ้ายในหน่วย σ"""
    q = _tdist(4).ppf(1 - a)
    return -q * sc, (4 + q * q) / 3 * _tdist(4).pdf(q) / (1 - a) * sc


_v99, _e99 = _t4(0.99); _v95, _ = _t4(0.95); _v999, _ = _t4(0.999); _v975, _e975 = _t4(0.975)
print(f"เสา IV  normal VaR99 {_z99:.3f}σ ES99 {_es99:.3f}σ · t4 VaR95 {_v95:.3f} VaR99 {_v99:.3f} VaR99.9 {_v999:.3f} ES99 {_e99:.3f} ES97.5 {_e975:.3f}")
expect(_P4, "t4 เทียบ normal ที่ 99%", f"ที่ 99% normal ให้ {_z99:.3f}σ แต่หางหนาให้ {_v99:.3f}σ")
expect(_P4, "t4 เทียบ normal ที่ 99.9%", f"ห่างกันเป็น {_nrm.ppf(.999):.2f}σ กับ {_v999:.2f}σ")
expect(_P4, "t4 เทียบ normal ที่ 95%", f"(normal {_nrm.ppf(.95):.3f}σ มากกว่า {_v95:.3f}σ)")
expect(_P4, "t4 VaR ES ส่วนต่าง", f"VaR₉₉ = {_v99*2:.2f}% · ES₉₉ = {_e99*2:.2f}% · ส่วนต่าง <strong>${(_e99-_v99)*2:.2f}M</strong>")
expect(_P4, "ES/VaR normal t4", f"normal ที่ 99% ได้ {_es99/_z99:.2f}")
expect(_P4, "ES/VaR t4", f"t (ν = 4) ได้ {_e99/_v99:.2f}")
expect(_P4, "ทำไม 97.5%", f"ES₉₇.₅ = {_nrm.pdf(_nrm.ppf(.975))/.025:.3f}σ แทบเท่ากับ VaR₉₉ = {_z99:.3f}σ")
expect(_P4, "ทำไม 97.5% หางหนา", f"ES₉₇.₅ = {_e975:.3f}σ เทียบ VaR₉₉ = {_v99:.3f}σ")
# traffic light
_pg, _pr = _binom.cdf(4, 250, .01), 1 - _binom.cdf(9, 250, .01)
expect(_P4, "traffic light เขียว", f"ตกอยู่ในโซนนี้ {_pg:.0%} ของเวลา")
expect(_P4, "traffic light แดง", f"จะเข้าโซนนี้แค่ {_pr:.2%} ของเวลา")
# Viniar
_p25 = _nrm.cdf(-25)
assert 1e134 < 1 / (_p25 * 252) < 1e136
expect(_P4, "Viniar", f"มีโอกาส {_p25*1e138:.1f} × 10⁻¹³⁸ ต่อวัน")
# พันธบัตรสองตัว — VaR ละเมิด ES ไม่ละเมิด
_pd = 0.04; _pair = {0: (1 - _pd) ** 2, 100: 2 * _pd * (1 - _pd), 200: _pd ** 2}


def _es95(dist):
    left, acc = 0.05, 0.0
    for loss in sorted(dist, reverse=True):
        take = min(dist[loss], left); acc += take * loss; left -= take
    return acc / 0.05


_es1, _es2 = _es95({0: 1 - _pd, 100: _pd}), _es95(_pair)
expect(_P4, "พันธบัตร ES ตัวเดียว", f"ตัวเดียว ES₉₅ = <strong>${_es1:.0f}</strong>")
expect(_P4, "พันธบัตร ES คู่", f"รวม 2 ตัว ES₉₅ = <strong>${_es2:.1f}</strong> ซึ่งน้อยกว่า ${_es1:.0f} + ${_es1:.0f} = ${2*_es1:.0f}")
# EVT
expect(_P4, "POT จำนวนวันเกิน", f"จะมีราว {1250*_nrm.cdf(-1.5):.0f} วันจาก 1,250 วัน")
_pt = _tdist(4).cdf(-_nrm.ppf(.999) * math.sqrt(2))
expect(_P4, "EVT หางจริง 6 เท่า", f"จะเกิดจริง {_pt:.1%} หรือ <strong>{_pt/0.001:.0f} เท่า</strong>")
expect(_P4, "EVT ขนาด VaR", f"ต่างกัน {_v999/_nrm.ppf(.999):.1f} เท่า: {_nrm.ppf(.999):.2f}σ เทียบ {_v999:.2f}σ")
# copula
_C7 = [[1, .7], [.7, 1]]
_cond = [_mvn(cov=_C7).cdf([_nrm.ppf(u)] * 2) / u for u in (.05, .01, .001)]
_lam = 2 * _tdist(5).cdf(-math.sqrt(5 * 0.3 / 1.7))
expect(_P4, "Gaussian copula ลู่ช้า", "ได้ " + " · ".join(f"{c:.2f}" for c in _cond) + " ที่หาง 5% · 1% · 0.1%")
expect(_P4, "t-copula λ", f"ρ เดียวกันค้างอยู่ที่ {_lam:.2f}")
expect(_P4, "DCC σ พอร์ต ปกติ", f"= <strong>{math.sqrt(1.3/2):.2f}</strong> เท่าของ σ แต่ละตัว")
expect(_P4, "DCC σ พอร์ต วิกฤต", f"σ พอร์ต = <strong>{math.sqrt(1.85/2):.2f}</strong> เท่า")
expect(_P4, "DCC VaR เพิ่ม", f"เพิ่มขึ้น <strong>{math.sqrt(1.85/1.3)-1:.0%}</strong>")



# ── Payoff Chart Study Guide — ตัวเลขในเนื้อ/ตาราง เทียบกับ payoff_lib ตัวเดียวกับที่วาดภาพ ────────
_SG = "payoff-chart-study-guide.html"
import payoff_lib as _pl  # noqa: E402
_L = _pl.Leg


def _pnl(legs, S):
    return sum(l.qty * ((max(S - l.K, 0) if l.kind == "call" else max(l.K - S, 0) if l.kind == "put" else (S - l.K)) - l.premium)
               for l in legs)


# บทที่ 3 ตาราง Bull Call Spread · Long Call 100 ราคา 8 + Short Call 110 ราคา 3
_bcs = [_L("call", 100, 1, 8), _L("call", 110, -1, 3)]
for _S in (90, 95, 100, 105, 110, 115, 120):
    _a, _b = _pnl(_bcs[:1], _S), _pnl(_bcs[1:], _S)
    _fmt = lambda v: f"{v:+.0f}" if v else "0"
    _cell_a = f"{_a:.0f}" if _a < 0 else f"+{_a:.0f}"
    _cell_b = f"{_b:.0f}" if _b < 0 else f"+{_b:.0f}"
    _tot = _a + _b
    _cell_t = f"<strong>{_tot:.0f}</strong>" if _tot <= 0 else f"<strong>+{_tot:.0f}</strong>"
    if _tot == 0:
        _cell_t = "<strong>0</strong> (BE!)"
    expect(_SG, f"บทที่ 3 BCS ที่ S={_S}", f"<tr><td>{_S}</td><td>{_cell_a}</td><td>{_cell_b}</td><td>{_cell_t}</td></tr>")
assert _pl.summary(_bcs)["breakevens"] == [105.0]

# กฎ slope สองขั้น (s₀ จาก Put/หุ้น · ±1 ทุก Strike) ต้องตรงกับ segments() ของ engine ทุกกลยุทธ์
def _slope_rule(legs):
    s0 = sum(-l.qty for l in legs if l.kind == "put") + sum(l.qty for l in legs if l.kind == "stock")
    out, cur = [s0], s0
    for K in sorted({l.K for l in legs if l.kind in ("call", "put")}):
        cur += sum(l.qty for l in legs if l.kind in ("call", "put") and l.K == K); out.append(cur)
    return out


for _nm, _legs in {"straddle": [_L("call", 100, 1, 5), _L("put", 100, 1, 5)],
                   "bear put": [_L("put", 110, 1, 8), _L("put", 90, -1, 3)],
                   "iron condor": [_L("put", 90, 1, 1), _L("put", 95, -1, 2), _L("call", 105, -1, 2), _L("call", 110, 1, 1)],
                   "butterfly": [_L("call", 90, 1, 12), _L("call", 100, -2, 6), _L("call", 110, 1, 3)],
                   "protective put": [_L("stock", 100, 1, 0), _L("put", 90, 1, 3)],
                   "collar": [_L("stock", 100, 1, 0), _L("put", 90, 1, 3), _L("call", 110, -1, 3)]}.items():
    _eng = [round(seg[2], 9) for seg in _pl.segments(_legs, 0, 250)]
    assert _slope_rule(_legs) == _eng, (_nm, _slope_rule(_legs), _eng)
print("SG  กฎ slope สองขั้นตรงกับ engine ทั้ง 6 กลยุทธ์")
expect(_SG, "straddle slope", "s₀ = −1 · ผ่าน 100 ได้ +2 (ทั้งสองขา) → slope ขวา = +1")

# Protective put · Short straddle
_pp = _pl.summary([_L("stock", 100, 1, 0), _L("put", 90, 1, 3)])
expect(_SG, "protective put ขาดทุนสูงสุด", f"Put K = 90 ราคา 3 → เสียได้ไม่เกิน {-_pp['max_loss']:.0f})")
_ss = [_L("call", 100, -1, 5), _L("put", 100, -1, 5)]
expect(_SG, "short straddle ขาลง", f"K = 100 เบี้ยรวม 10 เสียได้ถึง {-_pnl(_ss, 0):.0f}")
# Parity example + Put ยุโรปลึก ITM ต่ำกว่า intrinsic
_c6 = _bs_all(S=100, K=100, r=0.05, sg=0.20, T=0.5)["C"]; _pv6 = 100 * math.exp(-0.025)
expect(_SG, "parity PV(K)", f"PV(K) = 100·e<sup>−0.025</sup> = {_pv6:.2f}")
expect(_SG, "parity Put", f"ถ้า Call ราคา {_c6:.2f} Put ต้องราคา {_c6:.2f} + {_pv6:.2f} − 100 = <strong>{_c6+_pv6-100:.2f}</strong>")
_dp = _bs_all(S=60, K=100, r=0.05, sg=0.20, T=1.0); _put60 = _dp["C"] - 60 + 100 * math.exp(-0.05)
assert _put60 < 40
expect(_SG, "Put ยุโรปลึก ITM", f"ราคา {_put60:.2f} ต่ำกว่า intrinsic 40")



# ── เสาหลัก Part I (pillars-part1) — bootstrapping · duration · carry+roll · swap/FRA/swaption ───
_P1 = "pillars-part1.html"


def _bond(c, y, n, k=1):
    """บอนด์คูปอง c ต่อปี yield y จ่าย k งวด/ปี อายุ n ปี → ราคา, Macaulay, modified, convexity (ปี²)"""
    t = np.arange(1, n * k + 1) / k
    cf = np.full(len(t), 100 * c / k); cf[-1] += 100
    pv = cf / (1 + y / k) ** (t * k); P = pv.sum()
    mac = (t * pv).sum() / P
    conv = (cf * t * (t + 1 / k) / (1 + y / k) ** (t * k + 2)).sum() / P
    return P, mac, mac / (1 + y / k), conv


_DF1 = 1 / 1.04; _DF2 = (100 - 5 * _DF1) / 105
_z2 = _DF2 ** -0.5 - 1; _f12 = _DF1 / _DF2 - 1; _swp = (1 - _DF2) / (_DF1 + _DF2)
print(f"เสา I  DF1={_DF1:.5f} DF2={_DF2:.5f} z2={_z2:.3%} f12={_f12:.2%} swap={_swp:.2%}")
expect(_P1, "bootstrap DF1", f"DF(1) = 1/1.04 = <strong>{_DF1:.5f}</strong>")
expect(_P1, "bootstrap DF2", f"DF(2) = (100 − 5 × {_DF1:.5f})/105 = <strong>{_DF2:.5f}</strong>")
expect(_P1, "bootstrap z2", f"z₂ = DF(2)<sup>−1/2</sup> − 1 = <strong>{_z2:.3%}</strong>")
expect(_P1, "bootstrap f12", f"f(1,2) = DF(1)/DF(2) − 1 = <strong>{_f12:.2%}</strong>")
expect(_P1, "par swap", f"(1 − {_DF2:.5f})/({_DF1:.5f} + {_DF2:.5f}) = <strong>{_swp:.2%}</strong>")
expect(_P1, "FRA", f"FRA 1→2 ปี = {_f12:.2%}")
# duration 30 ปี par 4% annual
_P30, _mac30, _mod30, _c30 = _bond(0.04, 0.04, 30)
_ex30 = _bond(0.04, 0.05, 30)[0] / _P30 - 1
print(f"เสา I  30y par: mod {_mod30:.2f} C {_c30:.0f} อันดับหนึ่ง {-_mod30:.1%} +conv {-_mod30*.01+.5*_c30*1e-4:.1%} จริง {_ex30:.1%} · ที่ 3% {_bond(.04,.03,30)[2]:.1f} ที่ 5% {_bond(.04,.05,30)[2]:.1f}")
expect(_P1, "30y mod duration", f"มี modified duration {_mod30:.1f} → ดอกเบี้ยขึ้น 1%: ΔP/P ≈ −{_mod30:.1f} × 1%")
expect(_P1, "30y convexity", f"พอใส่ convexity (C = {_c30:.0f}) ได้ {(-_mod30*.01+.5*_c30*1e-4)*100:.1f}%".replace("-", "−"))
expect(_P1, "30y exact", f"ลดลง <strong>{-_ex30:.1%}</strong>")
expect(_P1, "30y duration ขึ้นกับ yield", f"ที่ 3% เป็น {_bond(.04,.03,30)[2]:.1f} ที่ 5% เป็น {_bond(.04,.05,30)[2]:.1f}")
_z30 = (1.04 / 1.05) ** 30 - 1
expect(_P1, "30y zero", f"modified = 30/1.04 = {30/1.04:.1f} → อันดับหนึ่ง −{30/1.04:.1f}% ราคาจริงลด {-_z30:.1%}")
# carry + roll: 5y yield 4% → ปีหน้าเป็น 4y ที่ 3.8%
_P4r = _bond(0.04, 0.038, 4)[0]; _mod4 = _bond(0.04, 0.04, 4)[2]; _mac4 = _bond(0.04, 0.04, 4)[1]
_roll = _P4r / 100 - 1
print(f"เสา I  roll: ราคา {_P4r:.2f} roll {_roll:.2%} · mod {_mod4:.2f} mac {_mac4:.2f} · รวม {0.01+_roll:.2%}")
expect(_P1, "carry roll ราคา", f"ที่ yield 3.8% ราคา {_P4r:.2f} ตรงกันพอดี")
expect(_P1, "carry roll", f"0.2% × modified duration {_mod4:.2f} = <strong>roll-down ≈ +{0.002*_mod4:.2%}</strong>")
expect(_P1, "carry roll read", f"0.2% × {_mod4:.2f} ≈ {0.002*_mod4:.2%} · duration ในสูตรนี้คือ <em>modified</em> duration (Macaulay {_mac4:.2f}")
expect(_P1, "carry+roll รวม", f"1.0% + {_roll:.2%} = <strong>~{0.01+_roll:.2%}</strong>")
# Vasicek / CIR · swaption
expect(_P1, "half-life", f"half-life = ln 2 / 0.5 ≈ {math.log(2)/0.5:.2f} ปี")
expect(_P1, "Feller", f"σ ≤ √(2ab) = {math.sqrt(2*0.5*0.04):.2f}")
_A = sum(1.04 ** -t for t in range(2, 7))
expect(_P1, "swaption annuity", f"(A = {_A:.2f})")
expect(_P1, "swaption Bachelier", f"= <strong>{_A*0.01/math.sqrt(2*math.pi):.2%} ของ notional</strong>")
# ภาพ PCA
_pc = _mf.NUMS.get("yc-loadings") or (_mf.FIGS[(_P1, "yc-loadings")](), _mf.NUMS["yc-loadings"])[1]
print("เสา I  yc-loadings NUMS:", {k: round(v, 4) for k, v in _pc.items()})



# ── เสาหลัก Part II (pillars-part2) — hazard · CDS · Merton · one-factor copula ───────────────
_P2 = "pillars-part2.html"
from scipy.integrate import quad as _quad  # noqa: E402
_sv = _mf.NUMS.get("survival-curve") or (_mf.FIGS[(_P2, "survival-curve")](), _mf.NUMS["survival-curve"])[1]
_lam2 = 0.02 / 0.6
assert abs(_sv["lam"] - _lam2) < 1e-12
expect(_P2, "λ จาก 200 bp", f"λ ≈ spread / (1 − R) = 2.0% / 0.6 ≈ <strong>{_lam2:.1%}/ปี</strong>")
expect(_P2, "PD 1 ปี", f"1 − e<sup>−λ</sup> = {1-math.exp(-_lam2):.2%}")
expect(_P2, "PD ที่ λ สูง", f"(ที่ λ = {0.1/0.6:.1%} จะได้ {1-math.exp(-0.1/0.6):.1%})")
expect(_P2, "รอด 5 ปี", f"โอกาสรอด 5 ปี = e<sup>−5λ</sup> ≈ {_sv['s5']:.0%}")
expect(_P2, "Lehman λ", f"spread 200 bp เดิมจะ imply λ แค่ {0.02/(1-0.08625):.2%}")
# credit triangle ตรงเป๊ะเมื่อ λ แบน + เบี้ยต่อเนื่อง ไม่ว่า r, T
for _r in (0.0, 0.05):
    for _T in (1, 10):
        _pl_ = _quad(lambda t: math.exp(-(_r + _lam2) * t), 0, _T)[0]
        _pr_ = 0.6 * _quad(lambda t: _lam2 * math.exp(-(_r + _lam2) * t), 0, _T)[0]
        assert abs(_pr_ / _pl_ - 0.02) < 1e-12, "triangle ต้องตรงเป๊ะเมื่อ λ แบน"


def _par_noacc(s, R=0.4, r=0.03, T=5, dt=0.25):
    lam = s / (1 - R); ts = [dt * i for i in range(1, int(T / dt) + 1)]
    prem = sum(dt * math.exp(-(r + lam) * t) for t in ts)
    prot = (1 - R) * sum(math.exp(-r * t) * (math.exp(-lam * (t - dt)) - math.exp(-lam * t)) for t in ts)
    return prot / prem


_pn = {s: _par_noacc(s) * 1e4 for s in (0.02, 0.05, 0.10)}
expect(_P2, "par spread ไม่นับ accrual",
       f"ที่ λ มาจาก 200 bp ได้ par spread {_pn[0.02]:.2f} bp · 500 bp ได้ {_pn[0.05]:.2f} · 1,000 bp ได้ {_pn[0.10]:,.2f}")
# Merton
_V, _D, _s, _mu = 100, 70, 0.20, 0.08
_DD = (math.log(_V / _D) + (_mu - _s ** 2 / 2)) / _s
_d2q = (math.log(_V / _D) + (0.03 - _s ** 2 / 2)) / _s
print(f"เสา II  DD={_DD:.3f} PD={_nrm.cdf(-_DD):.2%} · d2Q={_d2q:.2f} PDQ={_nrm.cdf(-_d2q):.2%}")
expect(_P2, "Merton DD", f"= [{math.log(_V/_D):.3f} + {_mu-_s**2/2:.2f}] / 0.20 ≈ <strong>{_DD:.2f}</strong>")
expect(_P2, "Merton PD", f"→ PD = N(−{_DD:.2f}) ≈ <strong>{_nrm.cdf(-_DD):.2%}</strong>")
expect(_P2, "Merton PD Q", f"PD<sub>Q</sub> = N(−{_d2q:.2f}) = <strong>{_nrm.cdf(-_d2q):.2%}</strong> เทียบ PD<sub>P</sub> {_nrm.cdf(-_DD):.2%}")


def _merton_spread(T, V=100, D=70, s=0.20, r=0.03):
    d1 = (math.log(V / D) + (r + s * s / 2) * T) / (s * math.sqrt(T)); d2 = d1 - s * math.sqrt(T)
    debt = D * math.exp(-r * T) * _nrm.cdf(d2) + V * _nrm.cdf(-d1)
    return (-math.log(debt / D) / T - r) * 1e4


expect(_P2, "Merton spread สั้น", f"ได้ spread 1 ปีแค่ {_merton_spread(1):.1f} bp และ 3 เดือนแค่ {_merton_spread(0.25):.2f} bp")
# one-factor Gaussian: 100 ชื่อ PD 2% senior รับเมื่อเจ๊ง > 10
from scipy.stats import binom as _bn  # noqa: E402


def _pool(rho, n=100, p=0.02):
    if rho == 0:
        return _bn.pmf(np.arange(n + 1), n, p)
    k = _nrm.ppf(p); xs = np.linspace(-8, 8, 4001); w = _nrm.pdf(xs); w /= w.sum()
    P = np.zeros(n + 1)
    for x, wt in zip(xs, w):
        P += wt * _bn.pmf(np.arange(n + 1), n, _nrm.cdf((k - math.sqrt(rho) * x) / math.sqrt(1 - rho)))
    return P


_k = np.arange(101); _res = {}
for _rho in (0.0, 0.3, 0.5, 0.9):
    _P = _pool(_rho); _res[_rho] = (_P[11:].sum(), (np.maximum(_k - 10, 0) * _P).sum(), (np.minimum(_k, 3) * _P).sum() / 3)
print("เสา II  tranche: " + " · ".join(f"ρ={r}: P(>10)={v[0]:.2%} EL={v[1]:.2f} eq={v[2]:.0%}" for r, v in _res.items()))
expect(_P2, "tranche ρ=0", f"= {_res[0.0][0]:.4%} · loss ที่ senior คาดว่าจะรับ ≈ 0 ชื่อ")
expect(_P2, "tranche ρ=0.3", f"ρ = 0.3: โอกาส {_res[0.3][0]:.2%} · loss คาดหวัง {_res[0.3][1]:.2f} ชื่อ")
expect(_P2, "tranche ρ=0.9", f"ρ = 0.9 (เกาะกลุ่ม): โอกาส {_res[0.9][0]:.2%} · loss คาดหวัง <strong>{_res[0.9][1]:.2f} ชื่อ</strong>")
expect(_P2, "tranche ρ=0.5 ไม่ monotone", f"ที่ ρ = 0.5 ได้ {_res[0.5][0]:.2%} สูงกว่าที่ 0.9")
assert _res[0.5][0] > _res[0.9][0] and _res[0.3][1] < _res[0.5][1] < _res[0.9][1]
expect(_P2, "equity tranche", f"ลดจาก {_res[0.0][2]:.0%} ที่ ρ = 0 เหลือ {_res[0.3][2]:.0%} ที่ ρ = 0.3 และ {_res[0.9][2]:.0%} ที่ ρ = 0.9")



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
    _discover_code_blocks()
    code_bad = _run_code_checks()
    bad += code_bad
    print(f"\nตรวจ {len(CHECKS)} ค่าใน {len(cache)} ไฟล์ · โค้ดในบท {len(CODE_CHECKS)} กล่อง (รันจริง) · ไม่ตรง {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
