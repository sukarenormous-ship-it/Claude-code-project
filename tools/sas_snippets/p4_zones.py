import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np
import sas_core as C

# ใช้: python3 tools/sas_snippets/p4_zones.py [ไฟล์.csv Y X]   (ราคาดิบ · ไม่ใส่ไฟล์ = คู่จำลอง good กับ fake)
# กราฟโซนแบบ "รู้แค่อดีต" · ใช้เฉพาะครึ่งแรก · α̂, β̂ จาก 250 แท่งแรก · เส้น P10/P50/P90 ของแท่ง t
# คิดจากแท่ง 0..t · นับเฉพาะแท่ง 250 ขึ้นไป ทุกอย่างที่นับจึงรู้แค่อดีต
def longest(mask):
    best = cur = 0
    for m in mask:
        cur = cur + 1 if m else 0
        best = max(best, cur)
    return best

def signs(y, x):
    n = len(y) // 2                                     # ครึ่งหลังเก็บไว้ทดสอบ ห้ามแตะ
    a, b = C.ols(y[:250], x[:250])["coef"]                # ไม้บรรทัดจากช่วงอุ่นเครื่อง
    e = y[:n] - a - b * x[:n]
    lo, mid, hi = np.array([np.percentile(e[:t + 1], [10, 50, 90]) for t in range(n)]).T
    s = slice(250, n)                                   # เชื่อเส้นหลังมีอดีตครบ 250 แท่ง
    e, lo, mid, hi = e[s], lo[s], mid[s], hi[s]
    side = np.sign(e - mid)
    return [len(e) / max(1, np.sum(side[1:] != side[:-1])), max(longest(side > 0), longest(side < 0)),
            max(longest(e > hi), longest(e < lo)), 100 * np.mean((e > hi) | (e < lo)),
            100 * np.mean(e <= e[-1])]

if len(sys.argv) == 4:
    d = np.genfromtxt(sys.argv[1], delimiter=",", names=True)
    pairs = {"ของคุณ": (np.log(d[sys.argv[2]]), np.log(d[sys.argv[3]]))}
else:
    pairs = {k: (C.demo_pair(k)["y"], C.demo_pair(k)["x"]) for k in ("good", "fake")}
rows = ["แท่งต่อการตัดเส้นกลางหนึ่งครั้ง", "แท่งที่ค้างฝั่งเดียวนานสุด", "แท่งที่อยู่นอกเส้น 10/90 นานสุด (ครั้งเดียว)",
        "% ของเวลานอกเส้น 10/90 (ยิ่งเกิน 20 มาก ยิ่งน่าสงสัย)",
        "% ของแท่ง 250..ล่าสุด ที่ต่ำกว่าจุดล่าสุด"]
res = {k: signs(*v) for k, v in pairs.items()}
print("  ".join(f"{k:>7}" for k in res) + "   สัญญาณ")
for i, r in enumerate(rows):
    print("  ".join(f"{res[k][i]:7.0f}" for k in res) + f"   {i + 1}. {r}")
