import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np
import sas_core as C
import statarb_lab as LAB

# ใช้: python3 tools/sas_snippets/p2_eye.py [ไฟล์.csv Y X]
# ไม่ใส่ไฟล์ = คู่ตัวอย่างจำลอง · ทุกเส้นเทียบกับ "ฝาแฝดไร้สายจูง" (random walk ยาวเท่ากัน)
def eye(s):                                   # s: แถวละหนึ่งเส้น
    s = np.atleast_2d(s)
    n = s.shape[1]
    a, b = s[:, :n // 2], s[:, n // 2:]
    pooled = np.sqrt((a.var(1, ddof=1) + b.var(1, ddof=1)) / 2)
    gap = abs(a.mean(1) - b.mean(1)) / pooled                 # ข้อ 1 ตัดครึ่ง
    d = s - s.mean(1, keepdims=True)
    cross = (np.diff(np.sign(d), axis=1) != 0).sum(1)         # ข้อ 2 ข้ามเส้นกลาง
    first = np.ptp(s[:, :n // 4], axis=1) / np.ptp(s, axis=1) # ข้อ 3 ช่วงหยุดโตไหม
    return gap, cross, first

if len(sys.argv) == 4:
    _, m, _, _ = LAB.load_columns(sys.argv[1], sys.argv[2:4], "raw")
    series = {"log Y": m[:, 0], "log X": m[:, 1], "Y - X": m[:, 0] - m[:, 1]}
else:   # fake = ไม่มีสายจูง (มีแต่ปัจจัยตลาดร่วม) · eps ของ good = มีสายจูง
    f, e = C.demo_pair("fake"), C.demo_pair("good")["eps"]
    series = {"fake log Y": f["y"], "fake log X": f["x"],
              "fake Y - X": f["y"] - f["x"], "good eps": e}
n = len(next(iter(series.values())))
twin = eye(np.cumsum(C.rng(297).standard_normal((2000, n)), axis=1))
print(f"{n:,} แท่ง · ฝาแฝด = random walk ยาวเท่ากัน 2,000 เส้น (ข้อมูลจำลอง)")
print("               gap(sd)  crossings  first 1/4 range")
med = [np.median(v) for v in twin]
print(f"twin median  {med[0]:8.2f} {med[1]:9.0f} {med[2]:12.0%}")
for name, s in series.items():
    g, c, r = (v[0] for v in eye(s))
    print(f"{name:12s} {g:8.2f} {c:9d} {r:12.0%}")
print("gap = ค่าเฉลี่ยสองครึ่งห่างกันกี่ sd · crossings = ข้ามค่าเฉลี่ยกี่ครั้ง")
print("first 1/4 range = ช่วงสูง-ต่ำของหนึ่งในสี่แรก เทียบกับทั้งเส้น")
print("ธงแดง (ข้อใดข้อหนึ่ง): gap > 1 · ข้ามไม่มากกว่าฝาแฝดชัดเจน · ช่วงแรกแคบกว่าฝาแฝด")
print("ธงแดง = สงสัย ไม่ใช่ทิ้ง · สายจูงช้าอาจข้ามแค่ราวสองเท่าของฝาแฝด → ไปต่อที่ ADF")
