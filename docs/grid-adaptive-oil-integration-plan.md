# แผนขัดเกลา + เพิ่มแนวคิด "Adaptive Grid น้ำมัน" เข้าหนังสือ Grid Trading Mastery

> สถานะ: **รอ user อนุมัติ** — ยังไม่มีการแก้ไฟล์หนังสือใดๆ
> ที่มา: โพสต์แชร์ไอเดียระบบ Adaptive Grid บน WTI (Linear Regression trend filter,
> ATR-adaptive step, delay refresh, overlap prevention, rolling basket TP, kill switch)
> ผลทดสอบที่เคลม: 2019–2026, fixed 0.3 lot, ทุน $2,000, PF 5, Sharpe 1.2, MaxDD −16%

---

## 1. ผลการประเมินต้นทาง (ทำแล้ว — สรุปไว้เป็นหลักฐานการตัดสินใจ)

| กลไกในโพสต์ | สถานะเทียบหนังสือ | การตัดสินใจ |
|---|---|---|
| 1. LR slope ของ EMA (normalized) เป็น trend filter | **ไม่มีในหนังสือ** — Hurst วัดนิสัย, ADX วัดแรงไร้ทิศ แต่ไม่มีตัววัด "ทิศ+แรง" ในค่าเดียว | ✅ เพิ่ม (Part 4) |
| 2. ATR-adaptive step | มีแล้ว — Part 3 `Step = k × ATR` | ❌ ไม่เพิ่ม (ซ้ำ) |
| 3. Delay refresh รอแท่งปิด | มีแล้ว — Part 3 §3.0 นาฬิกา 3 เรือน | ❌ ไม่เพิ่ม (ซ้ำ) |
| 4. Overlap prevention (ระยะห่างขั้นต่ำจากไม้เดิม) | **ไม่มีในหนังสือ** — Part 2 แก้บวมที่ sizing, ยังไม่มี guard เชิงระยะห่าง | ✅ เพิ่ม (Part 2) |
| 5. Rolling Global Basket TP (VWAP + k×ATR, Close All) | **ไม่มีในหนังสือ** — ตาราง TP §2.6.1 มี 4 policy ยังไม่มี basket | ✅ เพิ่ม (Part 2) |
| 6. Kill switch | มีแล้ว — Part 5 Drawdown Ladder / HALT | ❌ ไม่เพิ่ม (ซ้ำ) |
| ตัวเลข performance ที่เคลม | ตรวจแล้วมีปัญหา (0.3 lot WTI บน $2k ≈ $1 move = 15% ของพอร์ต; PF 5 คู่ Sharpe 1.2 คือลายเซ็น PF-inflation; "Expected Payoff 2.8 เท่า" ใช้หน่วยผิด; ไม่มี swap/rollover) | ✅ แปลงเป็นบทเรียน "วิธีอ่าน backtest คนอื่น" (Part 9) — **ไม่คัดลอกตัวเลขมาอ้างเป็นข้อเท็จจริง** |

## 2. หลักการขัดเกลา (ตาม voice guide เดิมของเล่ม)

- **ตัด hype ทิ้งทั้งหมด** — ไม่มี "มีดกำลังร่วง มึงอย่ารับ", ไม่มี emoji, ไม่มีเคลมตัวเลขที่ตรวจสอบไม่ได้
- **problem-first opening** ทุก section ใหม่ — เริ่มจากปัญหาที่ผู้อ่านเจอ ไม่ใช่จากชื่อเทคนิค
- **หนึ่งสูตรต่อหนึ่ง section** พร้อมนิยามตัวแปรครบ
- **ตัวเลขทุกตัวมาจาก running example ของเล่ม** (BTC, ทุน $100k, zone $85k–$118k) — ไม่ใช้ตัวเลขน้ำมันจากโพสต์
- **ทุกอย่างสอดคล้อง zero-EV theorem (Part 0 §0.4)** — เทคนิคใหม่ปรับ "รูปทรง" ของ P&L ไม่ได้เพิ่ม expected value
- ใช้เลข section แบบ x.y.1 (precedent: §2.6.1) เพื่อ**ไม่ต้อง renumber ไล่ทั้งไฟล์**

## 3. งานแก้ไขที่เสนอ (5 จุด, 4 ไฟล์)

### A. Part 4 — ใหม่ §4.2.1 "Normalized Slope — ตัววัดทิศทางที่ Hurst กับ ADX ไม่ให้"
แทรกหลัง §4.2 (ADX), id `s4-2-1` — ไม่กระทบเลข section อื่น

- ปัญหานำ: state machine 3 สัญญาณ (Hurst/ADX/BB) บอกได้ว่า "trend แรง" แต่ไม่บอกว่าขึ้นหรือลง — GRID ON ขณะราคากำลังดิ่งแรงคือการรับมีด
- สูตร (หนึ่งเดียวของ section):
  `slope_norm = slope(LinReg(EMA, lookback)) / ATR`
  — slope หน่วยเป็น $/แท่ง หารด้วย ATR ($/แท่ง) → ค่าไร้หน่วย เทียบข้ามเหรียญ/ข้าม timeframe ได้
- ตีความ: `slope_norm < −threshold` → **veto ฝั่งซื้อชั่วคราว** (หยุดกางกริด Long ใหม่) แม้ state machine จะยัง GRID ON — วางเป็น *optional directional overlay* ไม่ใช่ vote ที่ 4 (ไม่แตะ logic 2-of-3 ใน §4.4 ที่เพิ่ง audit ผ่าน 3 รอบ)
- โค้ด Python สั้น (`np.polyfit` บนค่า EMA ย้อนหลัง) + เชื่อมว่า LinReg คือเครื่องมือเดียวกับที่ Part 6 ใช้หา hedge ratio (OLS) — ผู้อ่านเห็นว่าเป็นความรู้ recycle ไม่ใช่ของใหม่
- ตาราง threshold แนะนำ (BTC-calibrated ให้สอดคล้อง §4.2): เช่น slope_norm < −0.15 = veto, −0.15…+0.15 = neutral, > +0.15 = trend ขึ้น (พิจารณา Zone Migration §4.6)
- แบบฝึกหัดใหม่ 1 ข้อ ใน §4.9: คำนวณ slope_norm จากค่า EMA 5 ค่าที่กำหนดให้ + ATR แล้วตัดสิน veto/ไม่ veto

### B. Part 2 §2.6.1 — เพิ่มแถวที่ 5 ในตาราง TP Policy: "Basket TP (รวบทุกไม้)"
- กลไก: `P_basket_TP = Σ(Q_i × P_i)/ΣQ_i + k × ATR` — TP เดียวจากต้นทุนเฉลี่ยถ่วงน้ำหนัก ปิดทุกไม้พร้อมกัน แล้วเริ่มกริดรอบใหม่
- เหมาะกับ: โหมดกู้สถานการณ์หลังสะสมไม้ลึก (ไม่ใช่ default) — เฉพาะสินทรัพย์ mean-revert
- Trade-off ในตาราง: ออกจากดอยได้โดยไม่ต้องรอราคากลับไปไม้แรก แลกกับ cashflow รายรอบหายไป + risk ย้ายไปกองใน floating DD
- ตัวอย่างเลขสั้นจาก running example: ถือ 3 ไม้ที่ $100k / $98k / $96k (Q เท่ากัน) → VWAP = $98k → TP = $98k + 0.5×ATR($3k) = **$99.5k** — ปิดรวบได้ทั้งที่ราคายังต่ำกว่าไม้แรก $500
- **กล่องเตือนใหม่** (คู่กับกล่อง Partial TP เดิม): Basket TP + fixed lot = ลูกผสม down-averaging → PF ที่ backtest โชว์จะสูงเวอร์โดยโครงสร้าง (ขาดทุนซ่อนใน floating DD ไม่เข้าสถิติ) — ลิงก์ไปหมายเหตุ PF ใน Appendix และเช็คลิสต์ Part 9 (ข้อ D ด้านล่าง)

### C. Part 2 — ใหม่ §2.5.1 "Overlap Guard — ระยะห่างขั้นต่ำกันไม้กระจุก"
แทรกหลัง §2.5 (Dynamic Sizing), id `s2-5-1`

- ปัญหานำ: หลัง Zone Migration/Reset (Part 4 §4.5–4.6) ไม้เก่ายังค้าง — กริดชุดใหม่อาจวาง level ทับโซนไม้เดิม → exposure กระจุก
- กติกา: ก่อนวาง order ใหม่ ถ้า `|P_new − P_nearest_open| < m × ATR` (m ≈ 0.5–1.0) → skip level นั้น
- ชี้ว่าใน grid ปกติที่ step ผูก ATR อยู่แล้ว ปัญหานี้แทบไม่เกิด — มันเกิดตอน**ย้าย zone ทั้งกริดโดยมี inventory ค้าง** ซึ่งเป็นจุดที่หนังสือเดิมยังไม่มี guard
- สั้น (~ครึ่งหน้าจอ) ไม่มีแบบฝึกหัดเพิ่ม

### D. Part 9 §9.4 — กล่องใหม่ "เช็คลิสต์อ่านผล backtest ที่คนแชร์กัน"
ต่อท้ายกล่องข้อจำกัด backtest engine เดิม — แปลงบทวิจารณ์โพสต์ต้นทางเป็นบทเรียนทั่วไป (ไม่ระบุที่มา ไม่โจมตีใคร):

1. **Sanity check ขนาด lot เทียบทุน** — ตัวอย่างทั่วไป: 0.3 lot WTI (300 barrels) บนทุน $2,000 → ราคาขยับ $1 = ±$300 = 15% ของพอร์ต; MaxDD −16% จึงแปลว่าระบบแทบไม่เคยถือไม้สวนเกิน $1
2. **PF สูง + Sharpe ปานกลาง = ลายเซ็น basket/close system** — ขาดทุน realize น้อยครั้งเพราะซ่อนใน floating DD; ดู Sharpe/Calmar แทน
3. **หน่วยของ metric** — Expected Payoff เป็นเงินต่อเทรด ไม่ใช่ "เท่า"; ใครใช้หน่วยผิดคืออ่านรายงานตัวเองไม่แตก
4. **ต้นทุนที่มักหายไป** — swap/rollover (สำคัญมากใน commodity CFD), contango, ค่า spread ช่วงข่าว
5. **คุณภาพข้อมูลช่วง event** — เช่น ราคาน้ำมันติดลบ เม.ย. 2020 ที่ data broker ส่วนใหญ่ clip ทิ้ง → backtest "รอดวิกฤต" ช่วงนั้นเชื่อไม่ได้

### E. Appendix — เพิ่ม 3 แถว Glossary + อัปเดต Cross-Book Index
- Glossary: **Linear Regression / Slope** (เส้นตรงที่ fit ข้อมูลดีที่สุด; slope = ความชัน), **VWAP ต้นทุนเฉลี่ย** (ต้นทุนเฉลี่ยถ่วงด้วยขนาดไม้), **Basket TP** (TP รวมทุกไม้จาก VWAP — ดู §2.6.1)
- Cross-Book Index: แถว OLS Regression เดิมเพิ่มโยง Part 4 §4.2.1 (LinReg ใช้ทั้ง hedge ratio และ slope filter)

## 4. สิ่งที่ตั้งใจ **ไม่ทำ** (และเหตุผล)

- ❌ ไม่ wire slope filter เข้า `UnifiedGridController` ใน Part 9 — reference implementation เพิ่งผ่าน audit 3 รอบ การเพิ่ม optional overlay เข้า code path หลักเสี่ยง regression เกินประโยชน์; ใน §4.2.1 จะระบุชัดว่า "เป็น overlay เสริม ต่อเองได้ที่จุด X" พร้อมชี้ตำแหน่ง
- ❌ ไม่เพิ่มบท/กรณีศึกษาน้ำมันแยก — เล่มนี้ผูก running example BTC ตลอด การเปิดสินทรัพย์ที่สองกลางเล่มเพิ่ม cognitive load เกินคุณค่า (บทเรียนน้ำมันถูกกลั่นเข้าเช็คลิสต์ข้อ D แทน)
- ❌ ไม่อ้างตัวเลข PF 5 / Sharpe 1.2 จากโพสต์เป็นข้อเท็จจริงใดๆ ในเนื้อหา

## 5. ขั้นตอนหลังอนุมัติ

1. เขียน 5 จุดตามลำดับ B → C → A → D → E (Part 2 ก่อนเพราะ §4.2.1 จะอ้างถึง Basket TP)
2. Consistency sweep: grep หา cross-reference ที่ควรโยงมา section ใหม่ (เช่น Part 1D Infinity Grid, Part 4 §4.5–4.6, Appendix PF note) + อัปเดต TOC ใน grid-index.html ถ้า list ถึงระดับ section
3. Render check ทุกไฟล์ที่แก้ผ่าน headless Chromium (ตาราง 5 แถวใน §2.6.1 อาจกว้าง — เช็ค overflow)
4. แบบฝึกหัดใหม่ 2 ข้อ (Part 4 slope_norm, Part 2 basket TP) — คำนวณมือยืนยันเฉลยก่อนใส่
5. Rebuild PDF ทั้งเล่ม + commit + push + อัปเดต PR #11

**ประมาณขนาดงาน**: เนื้อหาใหม่รวม ~3–4 หน้า PDF, แก้ 4 ไฟล์ HTML + PDF rebuild
