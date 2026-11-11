import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np
import sas_core as C
import statarb_lab as LAB

# ใช้: python3 tools/sas_snippets/p4_breakeven.py [ไฟล์.csv Y X [c_bps]]  (ไม่ใส่ไฟล์ = คู่จำลอง good · c = 5 bps)
# คำถาม: ต้นทุนของคุณบังคับให้แถบกว้างอย่างน้อยเท่าไร — คิดจากครึ่งแรกเท่านั้น ก่อนแตะช่วงทดสอบ
if len(sys.argv) >= 4:
    y, x = LAB.load_columns(sys.argv[1], sys.argv[2:4], "raw")[1].T   # log ราคา เรียงเก่า → ใหม่
else:
    p = C.demo_pair("good"); y, x = p["y"], p["x"]
c = (float(sys.argv[4]) if len(sys.argv) == 5 else 5.0) / 1e4    # ต้นทุนต่อขาต่อเที่ยว
n = len(y) // 2
a, b = C.ols(y[:n], x[:n])["coef"]
e = y[:n] - a - b * x[:n]
sd, hl = e.std(), C.fit_ar1(e)["half_life"]
need = 2 * c * (1 + abs(b)) / sd
print(f"β̂ {b:.3f} · σ̂ {sd:.2%} · half-life {hl:.1f} แท่ง · ต้นทุน {c * 1e4:.0f} bps ต่อขา (ครบรอบ {2 * c:.2%})")
print(f"แถบคุ้มทุน: entry − exit ต้องเกิน 2c(1+β)/σ = {need:.2f} σ  (ยังไม่มีกำไรเลย แค่เสมอตัว)")
print(f"time stop ≈ 3–4 × half-life ≈ {3 * hl:.0f}–{4 * hl:.0f} แท่ง (half-life ที่ประมาณได้มักสั้นกว่าจริง)\n")
print(" entry  สูตร/ไม้  จริง/ไม้  สุทธิ/ไม้  ไม้/ปี  สุทธิ/ปี")
z = C.zscore_fixed(e, e.mean(), sd)
for entry in (0.5, 1.0, 1.5, 2.0, 2.5):
    pos = C.band_positions(z, entry=entry, exit=0.0)
    pnl, info = C.spread_pnl(y[:n], x[:n], b, pos, cost_per_leg=c)
    tr = C.trade_pnls(info["held"], pnl, cost_per_leg=c)
    gross = tr.mean() + 2 * c if len(tr) else np.nan
    per_year = len(tr) / (n / 252)
    print(f"{entry:6.1f} {entry * sd / (1 + abs(b)):8.2%} {gross:9.2%} {gross - 2 * c:9.2%}"
          f" {per_year:7.1f} {np.sum(pnl) / (n / 252):9.2%}")
print("\nทุกค่าคิดในช่วงเดียวกับที่ใช้วัด σ̂ (ในตัวอย่าง) จึงมองโลกแง่ดี — ใช้เลือกแถบ ไม่ใช่คาดกำไร")
