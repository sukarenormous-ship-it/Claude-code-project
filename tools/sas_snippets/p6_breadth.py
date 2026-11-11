import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import math, numpy as np, sas_core as C, statarb_lab as LAB

# ใช้: python3 tools/sas_snippets/p6_breadth.py [pnl.csv ...]
#   แต่ละไฟล์: คอลัมน์ date (หรือ bar) + คอลัมน์ละหนึ่งสเปรด = กำไรขาดทุนรายวัน เป็นสัดส่วนของทุน
#   เช่นไฟล์จาก statarb_lab.py check ... --pnl-out · หลายไฟล์ = จับคู่กันตามวันที่ (ใช้เฉพาะวันที่มีครบ)
if len(sys.argv) >= 2:
    rows = {}                                # วันที่ (หรือเลขแท่ง) → {สเปรด: กำไรขาดทุน}
    for fn in sys.argv[1:]:
        head, body = LAB.read_table(fn)[:2]
        k = 0 if head[0].lower() == "bar" else LAB.find_date_column(head, body)
        for i, r in enumerate(body):
            day = rows.setdefault(r[k] if k is not None else str(i + 1), {})
            day.update({h: LAB.parse_number(r[j]) if j < len(r) else None
                        for j, h in enumerate(head) if j != k})
    cols = list(dict.fromkeys(c for v in rows.values() for c in v))   # Sharpe, ρ ไม่ขึ้นกับลำดับวัน
    pnl = np.array([[v.get(c) for c in cols] for v in rows.values()], dtype=float)  # ไม่มี = nan
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
