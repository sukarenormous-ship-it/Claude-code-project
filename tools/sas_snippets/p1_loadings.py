import sys, os, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import sas_core as C
# ใช้: python3 tools/sas_snippets/p1_loadings.py [ไฟล์.csv Y X ตลาด,ดัชนีอื่น] · ไม่ใส่ไฟล์ = ข้อมูลจำลอง
if len(sys.argv) == 5:  # CSV = ราคาปิดที่ปรับปันผลแล้ว
    d, names = np.genfromtxt(sys.argv[1], delimiter=",", names=True), sys.argv[4].split(",")
    miss = [c for c in sys.argv[2:4] + names if c not in d.dtype.names]
    if miss: sys.exit(f"ไม่พบคอลัมน์ {miss} · ในไฟล์มี {d.dtype.names}")
    P = np.log(np.column_stack([d[c] for c in sys.argv[2:4] + names]))
    R = np.diff(P[np.all(np.isfinite(P), axis=1)], axis=0)  # ผลตอบแทน (log)
    ry, rx, F = R[:, 0], R[:, 1], R[:, 2:]
else:  # เฉลย: Y = 1.3·Market + 0.4·Size · X = 0.8·Market + 1.0·Size · ไม่มีสายจูง
    g, n, names = C.rng(195), 1000, ["Market", "Size"]
    F = np.column_stack([g.normal(0, sd, n) for sd in (0.010, 0.005)])
    ry, rx = (F @ w + 0.008 * g.standard_normal(n) for w in ([1.3, 0.4], [0.8, 1.0]))
h = len(ry) // 2  # ประมาณทุกอย่างจากครึ่งแรก ตรวจกับครึ่งหลังที่ไม่ได้ใช้ประมาณ
for j in range(1, F.shape[1]):  # ดัชนีถัดไป: หักส่วนที่ดัชนีก่อนหน้าอธิบายได้ (สูตรจากครึ่งแรก)
    c = C.ols(F[:h, j], F[:h, :j])["coef"]
    F[:, j] -= c[0] + F[:, :j] @ c[1:]
by, bx = (C.ols(r[:h], F[:h])["coef"][1:] for r in (ry, rx))
beta = by[0] / bx[0]  # β ที่ทำให้ดัชนีแรกหายพอดี
fmt = lambda v: " ".join(f"{round(x, 2) + 0.0:+.2f}" for x in v)  # กัน -0.00
vr20 = lambda s: np.var(s[20:] - s[:-20]) / (20 * np.var(np.diff(s)))  # s = ระดับ · ใกล้ 1 = ไม่มีอะไรดึง
rw = np.percentile([vr20(np.cumsum(e)) for e in C.rng(196).standard_normal((1000, len(ry) - h))], [5, 95])
print(f"ครึ่งแรก {h:,} วัน · loading Y {fmt(by)} · X {fmt(bx)} · β {beta:.2f}")
print(f"ครึ่งหลัง {len(ry) - h:,} วัน · random walk ยาวเท่านี้ได้ VR20 {rw[0]:.2f}–{rw[1]:.2f} (5–95%)")
for lab, s in (("Y-X", ry - rx), (f"Y-{beta:.2f}X", ry - beta * rx)):
    f = C.ols(s[h:], F[h:])  # loading ที่สเปรดยังเหลือในครึ่งหลัง
    left = " · ".join(f"{nm} {fmt([b])} ±{2 * e:.2f}" for nm, b, e in zip(names, f["coef"][1:], f["se"][1:]))
    print(f"{lab:>9} ครึ่งหลังเหลือ {left} · VR20 {vr20(np.cumsum(s[h:])):.2f}")
