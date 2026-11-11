import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np
import sas_core as C
import statarb_lab as LAB

# ใช้: python3 tools/sas_snippets/p8_power.py [ไฟล์.csv Y X]   (ไม่ใส่ไฟล์ = 1,500 แท่งแบบคู่ตัวอย่าง)
# คำถาม: ถ้าคู่ของคุณ "มีสายจูงจริง" ข้อมูลยาวเท่านี้จะเห็นมันไหม — สถานี 3 ใช้ครึ่งแรกเท่านั้น
n = 1500
if len(sys.argv) == 4:
    _, mat, _, _ = LAB.load_columns(sys.argv[1], [sys.argv[2], sys.argv[3]], "raw")
    n = len(mat)
half, worlds = n // 2, 300
null = C.mc_null_eg(half, 2, n_sim=20000, lags=1, g=C.rng(802))  # seed เดียวกับ statarb_lab
cut5 = np.quantile(null, 0.05)             # เส้นตัด 5% ของจำนวนแท่งนี้ (จำลองเอง)
g = C.rng(881)
print(f"ข้อมูล {n:,} แท่ง → ครึ่งแรก {half:,} แท่ง · เส้นตัด 5% = {cut5:.2f} · โลกละ {worlds} ครั้ง")
print("โลกจำลองที่มีสายจูงจริง (β 1.4 · σ ของ ε 3%) ต่างกันแค่ความเร็วของสายจูง")
print("half-life   ครึ่งแรกยาวกี่เท่าของ half-life   สถานี 3 ให้ผ่าน")
for hl in (5, 12, 30, 60, 120):
    passed = 0
    for _ in range(worlds):
        p = C.make_pair("good", n, g, half_life=hl)
        r = C.eg_test(p["y"][:half], p["x"][:half])
        passed += r["adf"] < cut5
    print(f"{hl:6d} แท่ง   {half / hl:22.0f} เท่า   {passed / worlds:13.0%}")
print("อ่านว่า: สายจูงจริงแต่ช้า ข้อมูลเท่านี้มองไม่เห็นบ่อย → สถานี 3 ไม่ผ่าน ≠ ไม่มีสายจูง")
print("ดูแถวที่ half-life ใกล้กับที่เหตุผลของคู่คุณคาดไว้ (ไม่ใช่เลขที่ประมาณจากข้อมูลที่สอบไม่ผ่าน)")
