import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np
import sas_core as C
# ใช้: python3 tools/sas_snippets/p7_leash_probe.py [ไฟล์.csv Y X]
#      (ราคาดิบ · ไม่ใส่ไฟล์ = คู่จำลอง good / break / fake)
# กติกาใกล้เคียง 7a: ไม้บรรทัด (α, β, μ, σ) จากครึ่งแรกเท่านั้น · ครึ่งหลัง |z| ≥ 2 = เปิดเหตุการณ์
# "กลับ" = z ถึง 0.5 ฝั่งเดิม · ข้อมูลหมดก่อนกลับ = "ไม่กลับ" · ไม้เดิมจบก่อนจึงเปิดใหม่ได้
def probe(y, x):
    n = len(y) // 2
    r = C.eg_test(y[:n], x[:n])
    cut = C.crit_values(C.mc_null_eg(r["n_obs"], r["n_vars"], lags=r["lags"]))[0.05]
    e = y - r["alpha"] - r["beta"][0] * x
    z = (e - e[:n].mean()) / e[:n].std()
    wait, worst, t = [], [], n
    while t < len(z):
        if abs(z[t]) < 2:
            t += 1; continue
        w = np.sign(z[t]) * z[t:]                    # มองฝั่งที่แตะ: ยิ่งมาก ยิ่งหลุดไกล
        hit = np.nonzero(w[1:] <= 0.5)[0]
        k = hit[0] + 1 if len(hit) else len(w) - 1   # แท่งที่กลับ (หรือแท่งสุดท้าย)
        wait.append(k if len(hit) else np.inf)
        worst.append(w[:k + 1].max())
        t += k + 1
    if not wait: return [r["adf"], cut, 0] + [np.nan] * 5
    wait = np.array(wait)
    return [r["adf"], cut, len(wait), 100 * np.mean(wait <= 30), np.median(wait),
            100 * np.mean(np.isinf(wait)), max(worst), np.sqrt(np.mean(z[n:] ** 2))]
if len(sys.argv) == 4:
    d = np.genfromtxt(sys.argv[1], delimiter=",", names=True)
    pairs = {"yours": (np.log(d[sys.argv[2]]), np.log(d[sys.argv[3]]))}
else:
    pairs = {k: tuple(C.demo_pair(k)[c] for c in "yx") for k in ("good", "break", "fake")}
rows = ["EG ครึ่งแรก (ติดลบกว่าเส้นตัด = ผ่าน)", "เส้นตัด 5% (จำลอง)", "เหตุการณ์ในครึ่งหลัง",
        "% กลับภายใน 30 แท่ง", "แท่งจนกลับ ค่ากลาง (inf = ไม่กลับเกินครึ่ง)",
        "% ไม่กลับจนข้อมูลหมด", "หลุดไกลสุด (หน่วย σ̂)", "ขนาด z ครึ่งหลัง (ไม้บรรทัดพอดี = 1)"]
res = {k: probe(*v) for k, v in pairs.items()}
print("  ".join(f"{k:>7}" for k in res) + "   ตัววัด")
for i, r in enumerate(rows):
    print("  ".join(f"{res[k][i]:7.1f}" for k in res) + f"   {r}")
