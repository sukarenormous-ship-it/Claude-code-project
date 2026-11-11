import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np
import sas_core as C
import statarb_lab as LAB

# ใช้: python3 tools/sas_snippets/p2_adf_hand.py [ไฟล์.csv Y X]
# ไม่ใส่ไฟล์ = คู่ตัวอย่างจำลอง · ADF แบบเปิดฝา (lags 0 มีค่าคงที่):
# ถดถอย "การเปลี่ยนแปลงวันนี้" บน "ระดับเมื่อวาน"
def adf0(s):                     # s: แถวละหนึ่งเส้น → ความชัน γ, se, t
    s = np.atleast_2d(s)
    dx = np.diff(s, axis=1)
    lv = s[:, :-1] - s[:, :-1].mean(1, keepdims=True)
    dx = dx - dx.mean(1, keepdims=True)
    sxx = (lv * lv).sum(1)
    rho = (lv * dx).sum(1) / sxx
    resid = dx - rho[:, None] * lv
    se = np.sqrt((resid ** 2).sum(1) / (dx.shape[1] - 2) / sxx)
    return rho, se, rho / se

if len(sys.argv) == 4:
    _, m, _, _ = LAB.load_columns(sys.argv[1], sys.argv[2:4], "raw")
    series = {"log Y": m[:, 0], "log X": m[:, 1], "Y - X": m[:, 0] - m[:, 1]}
else:   # fake = ไม่มีสายจูง (มีแต่ปัจจัยตลาดร่วม) · eps ของ good = มีสายจูง
    f, e = C.demo_pair("fake"), C.demo_pair("good")["eps"]
    series = {"fake log Y": f["y"], "fake log X": f["x"],
              "fake Y - X": f["y"] - f["x"], "good eps": e}
n, g = len(next(iter(series.values()))), C.rng(298)
walks = (np.cumsum(g.standard_normal((2000, n)), axis=1) for _ in range(50))
null = np.concatenate([adf0(w)[2] for w in walks])   # ไม้บรรทัด: t ของ random walk
cut = np.quantile(null, 0.05)
print(f"{n:,} แท่ง · เส้นตัด 5% จาก random walk {null.size:,} เส้นยาวเท่ากัน = {cut:.2f}")
print(f"ตาราง normal (-1.645): random walk แท้ 'ผ่าน' {np.mean(null < -1.645):.0%} แทน 5%")
print("             slope rho        se        t   ผลและ half-life")
for name, s in series.items():
    rho, se, t = (v[0] for v in adf0(s))
    hl = C.half_life_from_phi(1 + rho)
    ok = f"ผ่าน · half-life {hl:.1f} แท่ง" if t < cut else "ไม่ผ่าน · ไม่อ่าน half-life"
    print(f"{name:10s} {rho:11.4f} {se:9.4f} {t:8.2f}   {ok}")
print("lags 0 = ด่านคัดกรองคร่าว ๆ · ไม่ผ่าน ≠ ไม่นิ่ง · Y - X ใช้ β = 1 ตายตัว (β ที่ถูก: ตอนที่ 3)")
