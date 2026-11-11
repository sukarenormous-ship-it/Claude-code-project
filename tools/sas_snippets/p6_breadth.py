import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import math, numpy as np, sas_core as C

# ใช้: python3 tools/sas_snippets/p6_breadth.py [pnl.csv]
#   pnl.csv: ทุกคอลัมน์ (ยกเว้น date) = กำไรขาดทุนรายวันของสเปรดหนึ่งตัว เป็นสัดส่วนของทุน
if len(sys.argv) == 2:
    d = np.genfromtxt(sys.argv[1], delimiter=",", names=True, deletechars="")
    pnl = np.column_stack([d[c] for c in d.dtype.names if c.lower() != "date"])
else:  # ข้อมูลจำลอง: 10 สเปรด 1,500 วัน · Sharpe จริง 0.5 · ρ = 0.1
    g, n, m, rho = C.rng(692), 1500, 10, 0.1
    shock = math.sqrt(rho) * g.standard_normal((n, 1)) + math.sqrt(1 - rho) * g.standard_normal((n, m))
    pnl = 0.01 * (shock + 0.5 / math.sqrt(252))
ok = ~np.isnan(pnl).any(axis=1)          # ใช้เฉพาะวันที่ทุกสเปรดมีข้อมูล
pnl = pnl[ok]
sharpe = lambda r: r.mean() / r.std() * math.sqrt(252)
loss_year = lambda s: 0.5 * math.erfc(s / math.sqrt(2))   # Φ(−Sharpe)
m, years = pnl.shape[1], len(pnl) / 252
s_bar = float(np.mean([sharpe(pnl[:, i]) for i in range(m)]))
corr = np.corrcoef(pnl.T)
rho_bar = (corr.sum() - m) / (m * (m - 1))
formula = s_bar * math.sqrt(m / (1 + (m - 1) * rho_bar))
print(f"สเปรด {m} ตัว · ข้อมูล {years:.1f} ปี (ตัดวันที่ข้อมูลไม่ครบ {(~ok).sum()} วัน)")
print(f"Sharpe เฉลี่ยรายตัว {s_bar:.2f} · สหสัมพันธ์เฉลี่ยระหว่างสเปรด {rho_bar:.2f}")
print(f"สูตร (สมมติทุกตัวผันผวนเท่ากัน) {formula:.2f}"
      f" · พอร์ตของคุณตามน้ำหนักเงินจริง {sharpe(pnl.sum(axis=1)):.2f}")
if rho_bar > 0:
    print(f"เพดานต่อให้เพิ่มสเปรดไม่สิ้นสุด: {s_bar / math.sqrt(rho_bar):.2f}")
print(f"โอกาสขาดทุนทั้งปี: สเปรดเดียว {loss_year(s_bar):.0%} · ทั้งพอร์ต {loss_year(formula):.0%}")
print(f"ระวัง: Sharpe ที่วัดจาก {years:.1f} ปี คลาดได้ราว ±{1 / math.sqrt(years):.2f} (≈ 1/√ปี)")
