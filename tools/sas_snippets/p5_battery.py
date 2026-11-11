import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np
import sas_core as C

# ใช้: python3 tools/sas_snippets/p5_battery.py [ไฟล์.csv Y X [c_bps] [p_max]]
# ไม่ใส่ไฟล์ = คู่ตัวอย่าง good กับ fake · ครึ่งแรก = train ครึ่งหลัง = test
a = sys.argv[1:]
c, p_max = (float(a[3]) if len(a) > 3 else 5) / 1e4, float(a[4]) if len(a) > 4 else 0.05
def battery(y, x):
    h = len(y) // 2
    r = C.eg_test(y[:h], x[:h])
    p = C.p_value(r["adf"], C.mc_null_eg(r["n_obs"], r["n_vars"], lags=r["lags"], g=C.rng(580)))
    e1, b1 = r["resid"], float(r["beta"][0])
    e2 = y[h:] - r["alpha"] - b1 * x[h:]               # ครึ่งหลัง ด้วย α, β ของครึ่งแรก
    sh, b2 = (e2.mean() - e1.mean()) / e1.std(ddof=1), float(C.ols(y[h:], x[h:])["coef"][1])
    h1, h2 = C.fit_ar1(e1)["half_life"], C.fit_ar1(e2)["half_life"]
    g, n1, n2 = (C.walk_forward_pair(y, x, cost_per_leg=k, lag=l)
                 for k, l in ((0, 1), (c, 1), (c, 2)))
    paid = g["pnl"].sum() - n1["pnl"].sum()            # ต้นทุนที่จ่ายไปทั้งหมด
    q = g["pnl"].sum() / paid if paid > 0 else 0.0     # = c ที่เท่าทุน ÷ c ที่ใช้
    s1, s2 = n1["stats"]["sharpe"], n2["stats"]["sharpe"]
    return [(f"{p:.3f}" if p >= 0.001 else "<0.001", "1 สายจูง: EG p ของครึ่งแรก", p <= p_max),
            (f"{sh:+.2f}", "2 ค่ากลางครึ่งหลังเลื่อนไม่ถึง 1 σ", abs(sh) < 1),
            (f"{b1:.2f} -> {b2:.2f}", "3 β ครึ่งหลังต่างไม่ถึง 15%", abs(b2 / b1 - 1) < 0.15),
            (f"{h1:.1f} -> {h2:.1f}", "4 half-life 2–60 ไม่ยืดเกิน 3 เท่า", 2 <= h1 <= 60 and h2 <= 3 * h1),
            (f"{q:.1f}", "5 กำไรขั้นต้น ÷ ต้นทุนที่จ่าย ≥ 3", q >= 3),
            (f"{s1:.2f} -> {s2:.2f}", "6 Sharpe lag 2 ≥ ครึ่งของ lag 1", s1 > 0 and s2 >= s1 / 2)]
pairs = {k: (C.demo_pair(k)["y"], C.demo_pair(k)["x"]) for k in ("good", "fake")}
if a:   # หัวคอลัมน์ห้ามมีเว้นวรรค · แถวที่ราคาขาดขาใดขาหนึ่งถูกตัดทิ้ง
    d = np.genfromtxt(a[0], delimiter=",", names=True, deletechars="")
    y, x = np.log(d[a[1]]), np.log(d[a[2]])
    ok = np.isfinite(y) & np.isfinite(x)
    pairs = {f"{a[1]}~{a[2]} (ตัด {np.sum(~ok)} แถว)": (y[ok], x[ok])}
for name, (y, x) in pairs.items():
    res = battery(y, x)
    print(f"คู่ {name}: ผ่าน {sum(ok for *_, ok in res)} จาก 6 ข้อ"
          f" (c = {c * 1e4:g} bps ต่อขา · เกณฑ์ EG p ≤ {p_max})")
    print("\n".join(f"  {v:>14}  {t}  -> {'ผ่าน' if ok else 'ไม่ผ่าน'}" for v, t, ok in res))
