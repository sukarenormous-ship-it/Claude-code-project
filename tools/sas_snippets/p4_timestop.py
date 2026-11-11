import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np
import sas_core as C
import statarb_lab as LAB

# ใช้: python3 tools/sas_snippets/p4_timestop.py [ไฟล์.csv Y X [c_bps entry]]  (ไม่ใส่ไฟล์ = คู่จำลอง break · 5 bps · entry 1.5)
# สถานี 4: เปิดครึ่งหลังครั้งเดียว · time stop จาก half-life ของครึ่งแรก · ตรวจสายจูงซ้ำทุก 21 แท่ง
if len(sys.argv) >= 4:
    y, x = LAB.load_columns(sys.argv[1], sys.argv[2:4], "raw")[1].T   # log ราคา เรียงเก่า → ใหม่
else:
    p = C.demo_pair("break"); y, x = p["y"], p["x"]
c = (float(sys.argv[4]) if len(sys.argv) >= 5 else 5.0) / 1e4
E = float(sys.argv[5]) if len(sys.argv) >= 6 else 1.5
n, W = len(y) // 2, 250
hl = C.fit_ar1(C.eg_test(y[:n], x[:n])["resid"])["half_life"]      # half-life จากครึ่งแรกเท่านั้น
ys, xs = y[n - W:], x[n - W:]          # 250 แท่งท้ายครึ่งแรกใช้อุ่นเครื่อง · นับผลเฉพาะครึ่งหลัง
print(f"half-life ครึ่งแรก {hl:.1f} แท่ง · entry {E} · ต้นทุน {c * 1e4:.0f} bps ต่อขา · นับผล {len(y) - n} แท่ง")
print(" stop       H  lag  ต่อปี  Sharpe  DD ลึกสุด  ไม้")
for name, H in (("none", None), ("3xHL", round(3 * hl)), ("4xHL", round(4 * hl))):
    for lag in (1, 2):
        s = C.walk_forward_pair(ys, xs, train=W, refit=21, entry=E, exit=0.0, max_hold=H,
                                cost_per_leg=c, lag=lag)["stats"]
        print(f" {name:<6}{H or '-':>4}{lag:5d}{s['ann_return']:7.1%}{s['sharpe']:8.2f}"
              f"{s['max_dd']:10.1%}{s['n_trades']:5d}")

# structural stop ตั้งต้น: Engle-Granger บน 250 แท่งล่าสุด ทุก 21 แท่ง · ไม่ผ่านที่ 10% สองรอบติด = ปิดและพักคู่
cut = np.percentile(C.mc_null_eg(W, 2, n_sim=100_000, lags=1, g=C.rng(450)), 10)
fails, streak, first = 0, 0, None
for t in range(n + 21, len(y) + 1, 21):
    bad = C.eg_test(y[t - W:t], x[t - W:t])["adf"] > cut
    fails, streak = fails + bad, (streak + 1 if bad else 0)
    if streak == 2 and first is None:
        first = t - 1
checks = len(range(n + 21, len(y) + 1, 21))
print(f"\nตรวจสายจูงซ้ำ {checks} ครั้ง (เกณฑ์ 10% = {cut:.2f}) · ไม่ผ่าน {fails} ครั้ง · "
      + (f"ไม่ผ่านสองรอบติดครั้งแรกที่แท่ง {first}" if first else "ไม่เคยไม่ผ่านสองรอบติด"))
