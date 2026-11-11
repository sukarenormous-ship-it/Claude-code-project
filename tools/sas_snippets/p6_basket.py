import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np, sas_core as C, statarb_lab as LAB

# ใช้: python3 tools/sas_snippets/p6_basket.py [ไฟล์.csv Y A,B,C]
#     ราคาดิบ · ไม่ใส่ไฟล์ = ข้อมูลจำลอง
# คำถาม: ขาที่เพิ่มคุ้มค่าผ่านทางไหม — เทียบ Y กับขาแรกขาเดียว และ Y กับทุกขา
if len(sys.argv) == 4:  # ชื่อคอลัมน์มีจุดได้ เช่น PTT.BK · ทิ้งแถวที่ขาดค่า · เรียงตามวันที่ให้
    m = LAB.load_columns(sys.argv[1], [sys.argv[2]] + sys.argv[3].split(","), "raw")[1]
    y, legs = m[:, 0], m[:, 1:]
else:  # คู่ตัวอย่าง good (มีสายจูงจริง) + ขาเกิน 3 ขาที่ไม่ผูกกับ Y เลย
    p, g = C.demo_pair("good"), C.rng(691)
    y = p["y"]
    extra = [4 + np.cumsum(0.015 * g.standard_normal(len(y))) for _ in range(3)]
    legs = np.column_stack([p["x"]] + extra)
half = len(y) // 2
print(f"ประมาณน้ำหนักจาก {half} แท่งแรก แล้วถือน้ำหนักเดิมอีก {len(y) - half} แท่ง")
for k in sorted({1, legs.shape[1]}):
    r = C.eg_test(y[:half], legs[:half, :k])
    null = C.mc_null_eg(r["n_obs"], r["n_vars"], n_sim=20000, lags=r["lags"])
    cut = C.crit_values(null)[0.05]  # 20,000 รอบ แม่นราว ±0.03 จึงพิมพ์ทศนิยมเดียว
    spread = y - r["alpha"] - legs[:, :k] @ np.atleast_1d(r["beta"])
    a, b = spread[:half], spread[half:]
    swing_out = np.sqrt(np.mean((b - a.mean()) ** 2))
    print(f"\nN = {k + 1} ขา  ADF {r['adf']:.2f} · เกณฑ์ 5% ของ {k + 1} ขา {cut:.1f}"
          f" -> {'ผ่าน' if r['adf'] < cut else 'ไม่ผ่าน'}")
    print(f"  sd ในช่วง fit {a.std():.2%} · แกว่งนอกช่วง fit {swing_out:.2%}"
          f" · ค่าเฉลี่ยเลื่อน {(b.mean() - a.mean()) / a.std():+.1f}σ")
print("\nขาที่เพิ่มคุ้มเมื่อ: ผ่านเกณฑ์ของจำนวนขาใหม่ และแกว่งนอกช่วง fit แคบกว่าแบบขาน้อย")
