import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np
import sas_core as C
import statarb_lab as LAB

# ใช้: python3 tools/sas_snippets/p5_placebo.py [ไฟล์.csv Y X [จำนวนชุด]]   (ไม่ใส่ = คู่ good)
# ยาหลอก: สุ่มหยิบ "วัน" ของผลตอบแทนมาเรียงใหม่ (หยิบแล้วใส่คืน) Y กับ X ย้ายวันไปด้วยกัน
# → correlation เท่าเดิม แต่สายจูงหายไป · ท่อ backtest ที่ซื่อสัตย์ต้องได้ราว 0
# ← แทน honest ด้วยฟังก์ชัน backtest ของคุณ: รับ y, x (log ราคา) คืน Sharpe ต่อปี
def honest(y, x, c=0.0005):          # walk-forward: ใช้ข้อมูลถึงแท่งก่อนหน้าเท่านั้น
    return C.walk_forward_pair(y, x, cost_per_leg=c)["stats"]["sharpe"]

def peeking(y, x, c=0.0005):         # ท่อที่ผิด: β, μ, σ จากข้อมูลทั้งเส้น (มองอนาคต)
    r = C.eg_test(y, x)
    pos = C.band_positions((r["resid"] - r["resid"].mean()) / r["resid"].std())
    pnl, _ = C.spread_pnl(y, x, np.full(len(y), r["beta"][0]), pos, cost_per_leg=c)
    return C.perf_stats(pnl[250:])["sharpe"]

a, p = sys.argv[1:], C.demo_pair("good")
y, x, n = p["y"], p["x"], int(a[3]) if len(a) > 3 else 40
if a:   # แถวที่ราคาขาดขาใดขาหนึ่งถูกตัดทิ้ง · เรียงตามวันที่ให้
    y, x = LAB.load_columns(a[0], a[1:3], "raw")[1].T
g, dy, dx = C.rng(581), np.diff(y), np.diff(x)
fake = []
for _ in range(n):
    k = g.integers(0, len(dy), len(dy))  # ใส่คืน: ถ้าแค่สลับลำดับ ปลายสองข้างจะถูกตรึงไว้
    yp, xp = y[0] + np.r_[0, np.cumsum(dy[k])], x[0] + np.r_[0, np.cumsum(dx[k])]
    fake.append((honest(yp, xp), peeking(yp, xp)))
fake = np.array(fake)
print(f"คู่ที่ทดสอบ (ไม่สุ่ม): Sharpe walk-forward {honest(y, x):+.2f}")
print(f"ยาหลอก {n} ชุด (ไม่มีสายจูง):")
for j, name in enumerate(("ท่อ walk-forward", "ท่อ β, μ, σ ทั้งเส้น (ผิด)")):
    s = fake[:, j]
    print(f"  ค่ากลาง {np.median(s):+.2f} · เส้น 95% {np.quantile(s, 0.95):+.2f}"
          f" · กำไร {np.mean(s > 0):4.0%} ของชุด  <- {name}")
