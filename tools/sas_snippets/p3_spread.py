import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np
import sas_core as C

# ใช้: python3 tools/sas_snippets/p3_spread.py [<ไฟล์.csv> <คอลัมน์ Y> <คอลัมน์ X>]
#      ไม่ใส่อะไร = คู่จำลอง good · ใส่ drift = คู่จำลองที่ β ค่อย ๆ เลื่อน
#      CSV: แถวแรกเป็นชื่อคอลัมน์ · หนึ่งแถวต่อวัน เรียงเก่า → ใหม่ · ราคาไม่มีจุลภาคคั่นหลักพัน
if len(sys.argv) == 4:                                   # 1) สองคอลัมน์ → log ราคา
    d = np.genfromtxt(sys.argv[1], delimiter=",", names=True)
    P = np.log(np.column_stack([d[c.replace(" ", "_")] for c in sys.argv[2:4]]))
    y, x = P[np.all(np.isfinite(P), axis=1)].T
else:
    p = C.demo_pair(sys.argv[1] if len(sys.argv) == 2 else "good")
    y, x = p["y"], p["x"]
k = len(y) // 2                                          # 2) train | test
r = C.eg_test(y[:k], x[:k])                              # 3) OLS (มี α) + ADF ของ ε̂
a, b, e = r["alpha"], float(r["beta"][0]), r["resid"]
null = C.mc_null_eg(r["n_obs"], r["n_vars"], n_sim=100_000, lags=r["lags"])
cut = C.crit_values(null)[0.05]                          # 4) เกณฑ์ของ n, ขา, lags เรา
print(f"train {k:,} แท่ง · α = {a:.3f} · β = {b:.3f} → ซื้อ Y 100 บาท คู่กับขาย X {100 * b:.0f} บาท")
ok = r["adf"] < cut
print(f"Engle-Granger {r['adf']:.2f} · เกณฑ์ 5% ที่จำลองเอง {cut:.2f} → "
      + ("ผ่าน" if ok else "ไม่ผ่าน: ตัวเลขบรรทัดถัดไปยังไม่มีความหมาย"))
f, sd = C.fit_ar1(e), e.std(ddof=1)                      # 5) สี่ตัวเลขของ ε
cross = int(np.sum(np.diff(np.sign(e - e.mean())) != 0))
print(f"μ {100 * f['mu']:+.2f}% · σ {100 * sd:.2f}% · half-life {f['half_life']:.1f} แท่ง "
      f"(φ {f['phi']:.4f}) · ข้ามเส้นกลาง {cross} ครั้งใน {k:,} แท่ง")
et = y[k:] - a - b * x[k:]                               # 6) test: ใช้ของ train เท่านั้น
z = (et - e.mean()) / sd
s, cut1 = C.adf_stat(et), C.crit_values(C.mc_null_adf(len(et), n_sim=100_000))[0.05]
print(f"test {len(et):,} แท่ง · ค่ากลางเลื่อน {z.mean():+.2f}σ̂ · sd ×{z.std(ddof=1):.2f} · "
      f"นอก ±2σ̂ {100 * np.mean(np.abs(z) > 2):.1f}% ของแท่ง")
print(f"ADF ของช่วง test {s:.2f} · เกณฑ์ ADF ธรรมดา {cut1:.2f} (β ไม่ได้มาจากช่วงนี้) → "
      + ("ผ่าน" if s < cut1 else "ไม่ผ่าน: β ของ train ใช้กับข้อมูลใหม่ไม่ได้"))
sa = np.concatenate([e, et])                             # ทั้งสองช่วง ด้วย α, β ของ train
g = np.std(sa[250:] - sa[:-250]) / np.std(sa[20:] - sa[:-20])
print(f"sd ของการเปลี่ยนแปลงข้าม 250 แท่ง ÷ ข้าม 20 แท่ง = {g:.2f} (ε นิ่ง ≈ 1 · โตต่อ = มีของที่ไม่กลับปน)")
