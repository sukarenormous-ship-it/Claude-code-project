# Grid Trading Mastery — Round 4 Audit: Content + Image Correctness

> ที่มา: คำสั่ง "แบ่งทีมผู้เชี่ยวชาญตรวจสอบเนื้อหา รูปภาพ ให้ถูกต้อง" — ส่ง 4 ทีมตรวจขนาน (สูตร/ตัวเลข, cross-reference/navigation, ภาพ/แผนภูมิ, ตรรกะการเทรด) ครอบคลุมทั้ง 18 ไฟล์ของเล่ม Grid Trading Mastery (`docs/grid-*.html`) ทีมสูตร/ตัวเลขแบ่งงานเป็น 5 batch ย่อยเพื่อครอบคลุมทุกไฟล์อย่างละเอียด (แทนที่จะ skim)
>
> **สถานะ: แก้ครบทั้ง 52/52 findings แล้ว** (commit แยกต่อไฟล์/กลุ่ม, ผ่าน render-check ทุกจุด) ยกเว้น M6 (Part 1B +23% claim) ที่ตรวจสอบซ้ำแล้วพบว่าตัวเลขเดิมถูกต้องอยู่แล้ว (false positive จากทีมตรวจ) จึงไม่ได้แก้ไข

## สรุปนับจำนวน

| ระดับ | จำนวน |
|---|---|
| 🔴 Critical | 9 |
| 🟡 Moderate | 24 |
| ⚪ Minor | 19 |
| **รวม** | **52** |

---

## 🔴 Critical (แก้ก่อน — กระทบการตัดสินใจเทรดจริงหรือทำให้เล่มขัดแย้งในตัวเองอย่างชัดเจน)

### C1. Part 9 `main.py` เรียกฟังก์ชันผิดตัว — DD Halt และ Execution Style เป็น dead code
**ไฟล์:** `grid-part9.html` (บรรทัด ~404-407, 442-468), เทียบกับ `grid-part4.html` (§4.7) และ `grid-part7b.html` (§7B.7)
เล่มสร้าง "main loop" ไว้ 2 ตัวที่ทำหน้าที่ต่างกัน: `GridWatchdog.run_checks()` (เช็ก regime เท่านั้น) กับ `UnifiedGridController.run_cycle()` (เช็ก DD Halt ก่อน แล้วค่อยเรียก execution style ที่เลือกไว้) แต่ `main.py` เรียก `watchdog.run_checks(...)` — ไม่เคยเรียก `controller.run_cycle()` เลย แปลว่า Drawdown Monitor (Part 5's central risk control) และ Execution Style ทั้ง 4 แบบ (จุดขายหลักของ Part 7B) **ไม่ถูกใช้งานจริงในโค้ด reference ของเล่ม** นอกจากนี้ `run_cycle()` เรียก `self.grid.create_orders(...)` ซึ่งไม่มีเมธอดนี้อยู่ใน `GridFramework` เลย (มีแค่ `create_buy_levels`)
**ผลกระทบ:** เทรดเดอร์ที่ copy โค้ดนี้ไปรันจริงจะได้ bot ที่ track `portfolio_history` แต่ไม่เคยหยุดเมื่อ drawdown ลึก — วิ่งผ่าน −8% ไปเรื่อยๆ ได้

### C2. State Machine 2-of-3 vote มี edge case ที่ปล่อยให้ FULL DEPLOY ตอนสัญญาณเร็วที่สุดกำลังเตือนอันตราย
**ไฟล์:** `grid-part4.html` (`GridStateMachine.evaluate`, บรรทัด ~339-361)
ถ้า Hurst=ON, ADX=ON (2 ตัวช้า ยังไม่ทัน), แต่ BB width=OFF (ตัวไวสุด สปайค์แล้ว) → นับ ON=2, OFF=1, CAUTION=0 → โค้ดตกไปที่ `GRID_ON` (full deploy) เหมือนไม่มีอะไรเกิดขึ้น เคส 1-1-1 มีการจัดการให้ตกไป CAUTION แต่เคส 2-ON/1-OFF ไม่มี — เท่ากับ neutralize สัญญาณเร็วสุดที่ตั้งใจออกแบบมาจับ breakout ตั้งแต่ต้น

### C3. Part 1A §1A.9 Running Example: unrealized loss ผิดไป 5.5 เท่า
**ไฟล์:** `grid-part1a.html` (§1A.9, "Max Drawdown (worst case)")
ระบุ "unrealized ~$1,500" แต่คำนวณจากตารางเดียวกัน (0.091 BTC × $90k floor = $8,190, capital $8,460 − $8,190) ได้ **$270** ไม่ใช่ $1,500 — เป็นตัวเลขความเสี่ยงในตัวอย่าง running example หลักของทั้งเล่ม

### C4. Part 1C §1C.6: Perp margin ขัดกับตารางP&L ของตัวเอง และขัดกับ §1C.3
**ไฟล์:** `grid-part1c.html` (§1C.6)
ระบุ margin $1,000 (10× ของ notional $10k) แต่ทุกแถวใน P&L table สอดคล้องกับ notional $5,000 เท่านั้น (ตรงกับ spot inventory 0.05 BTC ที่ตั้งไว้ใน §1C.2) → margin ที่ถูกต้องคือ $500 ไม่ใช่ $1,000 ทำให้ total capital ที่ระบุ ($5,700) ขัดกับ §1C.3 ที่คำนวณ scenario เดียวกันได้ $5,200

### C5. Part 3B §3B.9 (flagship running example) และ §3B.6 — Composite Score คำนวณผิดจากสูตรของตัวเอง ยืนยันซ้ำจาก 2 ทีมอิสระ
**ไฟล์:** `grid-part3b.html` (§3B.6, §3B.9) — **ยืนยันซ้ำโดยทั้งทีมสูตร/ตัวเลข และทีมภาพ/แผนภูมิ (ตรวจ chart data คนละมุมแต่เจอบั๊กเดียวกัน)**
- §3B.9: BB score ที่ถูกต้องจากฟังก์ชัน `bb_score_for_grid` ในไฟล์เดียวกันคือ ~62.16 ไม่ใช่ 78 ที่ระบุ → Composite ที่แท้จริง ≈73.35 (**PARTIAL_DEPLOY**) ไม่ใช่ 79.4 ที่อ้าง (**FULL_DEPLOY**) — เล่มแนะนำให้ทุ่มทุน 100% ทั้งที่สูตรตัวเองบอกว่าควรแค่ 60%
- §3B.6: Hurst=0.46 ควรได้ score 65 (ไม่ใช่ 85) ตามฟังก์ชันเดียวกัน → composite ที่แท้จริง 72.0 (PARTIAL_DEPLOY) ไม่ใช่ 76.0 ที่อ้าง (FULL_DEPLOY)
- ทีมภาพยืนยันจากมุมกราฟ: bar chart แสดง BB score=88 (เป็นไปไม่ได้ทางคณิตศาสตร์จาก input ที่ให้), Volume score=82 ทั้งที่ฟังก์ชันให้ 40 (สัญญาณกลับด้าน — ฟังก์ชันตีความ volume ต่ำแบบนี้ว่าเป็นความเสี่ยง ไม่ใช่จุดแข็ง)

### C6. Part 6B §6B.4 Option B: zone width ผิดไป 3 เท่า
**ไฟล์:** `grid-part6b.html` (§6B.4)
ระบุขยาย zone จาก $90k–$110k (width $20k) เป็น $80k–$120k (width $40k) แล้วเรียกว่า "+33% wider" — ที่จริงคือ **+100% wider** (กว้างขึ้น 2 เท่า ไม่ใช่ 1.33 เท่า)

### C7. Part 6B §6B.7 ตาราง projection ระยะยาว: คอลัมน์ BTC ไม่ reconcile กับคอลัมน์ Capital ทุกแถว
**ไฟล์:** `grid-part6b.html` (§6B.7)
Footnote ระบุ split 70% compound / 30% DCA BTC แต่ทุกแถวในตาราง (ปีที่ 1-5) ตัวเลข BTC ที่ระบุสูงกว่าที่ implied จาก Capital column ตามสัดส่วน 70/30 ประมาณ 30-40% ทุกแถว — เป็น pattern เดียวกันซ้ำๆ ไม่ใช่ rounding เดี่ยวๆ (เทียบกับตัวอย่างเล็กใน §6B.8 ที่ reconcile ถูกต้อง ยืนยันว่านี่คือบั๊กเฉพาะตารางนี้)

### C8. Part 9 §9.8 Dashboard: โค้ดตัวอย่างไม่ escape HTML → ทำลาย background/สีตัวอักษรทั้งหน้า
**ไฟล์:** `grid-part9.html` (§9.8, บรรทัด ~516-529)
โค้ดตัวอย่าง Flask dashboard เขียน raw `<body style="background:#0f172a;color:#e2e8f0">...</body>` แบบไม่ escape → browser parse เป็น markup จริง แล้วรวม attribute เข้ากับ `<body>` จริงของทั้งหน้า ยืนยันด้วยการ sample สีพื้นหลังทั่วทั้งเอกสาร (0-13900px) ได้ `#0f172a` (navy เข้ม) **ตลอดทั้งไฟล์ ตั้งแต่หน้าปก** — หัวข้อทั้ง 8 section (เช่น §9.1-§9.8) กลายเป็นตัวอักษรมองไม่เห็นเพราะสีตัวอักษร (`--g9:#111827`) ออกแบบมาสำหรับพื้นขาว นอกจากนี้ยังมี element หลอน (script tag, canvas, div) ที่ไม่ตั้งใจแสดงผลจริงบนหน้าเพจ

---

## 🟡 Moderate

| # | ไฟล์ | ปัญหา |
|---|---|---|
| M1 | `grid-index.html` | Part 3 TOC ไม่พูดถึง GARCH เลย ทั้งที่เป็น topic หลักที่ 2 chapter อื่นอ้างอิงมา |
| M2 | `grid-part4.html` | Hysteresis dead-band อธิบายเป็น "solution" ใน §4.4 แต่ไม่เคยใส่กลับเข้า `GridStateMachine` class ที่ Part 9 import จริง |
| M3 | `grid-part6.html` | Pair Grid running example: Day 8 บอกว่ายังไม่ถึง TP (-1σ) ทั้งที่ spread จริง (-0.5σ) ผ่าน TP ไปแล้วตามกฎที่เพิ่งสอน |
| M4 | `grid-part9.html` | `GridFramework.from_market_data()` รับ `kelly_fraction` แต่ไม่เคยใช้ในฟังก์ชัน — Kelly sizing เป็นแค่ comment ไม่ enforce จริง |
| M5 | `grid-part1a.html` §1A.10 Ex.1 | นับ $86k ซ้ำ สรุปควรได้ $7,280 ไม่ใช่ $7,420 |
| M6 | `grid-part1b.html` §1B.3 | อ้าง "+23%" แต่คำนวณจากเลข margin ที่แก้แล้วได้ 11.3%; เลข 6% มาจากเลข 20x leverage ที่บอกเองว่าไม่ควรใช้ |
| M7 | `grid-part3b.html` §3B.4 | vol_ratio=1.5 พอดีขอบเขต ฟังก์ชัน `<1.5` เข้มงวด → score ควรเป็น 45 ไม่ใช่ 70 |
| M8 | `grid-part3.html` §3.9 | ปัด $117,600 ควรได้ $118,000 ไม่ใช่ $117,000 → กระทบ zone_width/N/Q ต่อเนื่อง |
| M9 | `grid-part3.html` §3.7 | ตาราง Step/ATR ratio ไม่ตรงกับ step_factor ที่ escalate (0.35/0.50/0.60/0.70) ในฟังก์ชันติดกัน |
| M10 | `grid-part3.html` §3.0 vs Ex.5 | §3.0 อ้าง "เล็กกว่าหลายสิบเท่า" แต่ Ex.5 คำนวณเองได้ ~4.9 เท่า — ขัดกันในไฟล์เดียว |
| M11 | `grid-part2.html` §2.7 | Bottom-Heavy row implied avg entry $70k ขัดกับแถวอื่น ($90k) และเกินขอบเขตราคาที่ตั้งไว้ (BTC ลงแค่ $85k) |
| M12 | `grid-part2.html` Ex.3 | หัก fee ไม่สม่ำเสมอระหว่าง Bell Curve กับ Equal Weight baseline → "ดีกว่า 33%" ที่จริงควรเป็น ~47% |
| M13 | `grid-part6.html` §6.6 | ตาราง allocation กลับด้านกับสูตร correlation→allocation ของตัวเอง (correlation สูงสุดได้ allocation สูงสุด ทั้งที่หลักการบอกตรงข้าม) |
| M14 | `grid-part5.html` Ex.4 | ระบุ multiplier 0.4 ผิดช่วง Hurst (บอกว่าอยู่ที่ 0.55-0.58 ทั้งที่กฎในไฟล์เดียวกันให้ 0.7 ที่ช่วงนี้ และ 0.4 ที่ H>0.58) |
| M15 | `grid-part4.html` | avg buy price คำนวณผิด ($16k ควรเป็น $17k) → unrealized P&L $640 ควรเป็น $680 |
| M16 | `grid-part5.html` | "round down" ระบุผิดทิศ (0.019→0.02 คือ round up) + avg price ไม่ตรงกัน ($94k ขัดกับ $100k ที่ระบุ) |
| M17 | `grid-part6.html` | Spread σ ใน running example (Day 8, Day 10) คำนวณจาก input จริงได้ค่าไม่ตรงกับที่ระบุ (ข้อสรุปเชิงคุณภาพยังถูกอยู่) |
| M18 | `grid-part6b.html` §6B.2 | (1.0027)^365 = 2.6756 ไม่ใช่ 2.66 → capital $2,676 ไม่ใช่ $2,660 |
| M19 | `grid-part6b.html` §6B.3 vs §6B.8 | $100/วัน บน $10k (1%/วัน) ขัดกับอัตรามาตรฐาน 0.27%/วัน ที่ใช้กับทุนเดียวกันที่อื่น |
| M20 | `grid-part6b.html` §6B.6 vs §6B.7 | $100/วัน บน $20k ขัดกับ §6B.7 ที่ระบุ 0.27%/วัน ($54/วัน) สำหรับทุนตั้งต้นเดียวกัน — ได้ 2 ตัวเลขปลายปีคนละค่า |
| M21 | `grid-part7.html` §7.4 | Iron Condor ย้าย strike ออกไปไกลขึ้นแต่ premium เท่าเดิม (ควรลดลงเพราะ OTM มากขึ้น) |
| M22 | `grid-part8.html` | Flash Crash trigger ระบุ 3 แบบไม่ตรงกัน (prose 15%/1h/5x, code 15%/2h/3x, quiz 10%/1h) — **ยืนยันซ้ำโดยทีมตรรกะการเทรดด้วย** |
| M23 | `grid-part8.html` | Laddered CSP: assignment logic ขัดกับ strike ที่ให้ (Level 1 ที่ $98k ควรถูก assign ที่ BTC=$95k ไม่ใช่ "expire worthless") |
| M24 | `grid-part9.html` | Phase 2 success criteria "DD ≤ −8%" เครื่องหมายกลับด้าน (ควรเป็น DD ≥ −8% ตาม sign convention ของไฟล์เอง) |

---

## ⚪ Minor

| # | ไฟล์ | ปัญหา |
|---|---|---|
| N1 | `grid-index.html` | Part 2 TOC ไม่พูดถึง §2.6.1 (TP policy) |
| N2 | `grid-index.html` | Part 7 TOC ไม่พูดถึง §7.4/§7.5 |
| N3 | `grid-part8.html` | ไม่มี id anchor ที่ section heading เลย (ไม่ break อะไรตอนนี้ แต่ไม่สอดคล้องกับไฟล์อื่น) |
| N4 | `grid-part1a.html` §1A.9 | Label "Max Drawdown (worst case)" ที่จุดแตะ floor ไม่ตรงกับหลักการ Close System ที่ไม่มี stop-loss จริง (ความเสี่ยงจริงไม่จำกัด disclose ไว้ที่อื่นแล้ว) |
| N5 | `grid-part1a.html` Ex.5 | 1.2^8 ปัดควรได้ 0.021 ไม่ใช่ 0.022 |
| N6 | `grid-part1c.html` §1C.6 | Return % ไม่ตรงกับ range จริงของตาราง หรือทุนที่ระบุ ($6,000 เป็นเลขที่ 3 ที่ไม่มีที่มา) |
| N7 | `grid-part1d.html` §1D.2 | "$20,000/$100,000 ≈19%" ควรเป็น 20% พอดี |
| N8 | `grid-part2.html` §2.5 | Array ตัวอย่างก่อน normalize รวมได้ $11,000 ไม่ใช่ $10,000 |
| N9 | `grid-part3.html` §3.3.1 | Python round-half-to-even ให้ $1,200 ไม่ใช่ $1,300 ตามที่แสดง |
| N10 | `grid-part3.html` ตาราง 3.4 | N=21.56 ควร truncate เป็น 21 ไม่ใช่ 22 |
| N11 | `grid-part3.html` Ex.1 | $1,600 ปัดไปทาง $1,500 ชัดเจน ไม่ใช่ "$1,500 หรือ $2,000" |
| N12 | `grid-part5.html` | Kelly f* 0.75444 ควรปัดเป็น 0.754 ไม่ใช่ 0.755 |
| N13 | `grid-part4.html` | Hysteresis exit threshold: §4.4 บอก H<0.47, Ex.4 answer บอก H<0.48 |
| N14 | `grid-part5.html` | SE aside "±3%" ควรเป็น ≈±2% ตาม p=0.83, n=270 ที่ระบุ |
| N15 | `grid-part5.html` | Sensitivity claim "±30-40%" ไม่ตรงกับค่า b ใดๆ ที่ใช้ในไฟล์ (confidence ต่ำ อาจต้องดูเพิ่ม) |
| N16 | `grid-part8.html` | $6,000×1.2%=$72 ไม่ใช่ $73.5 ตามที่พิมพ์ |
| N17 | `grid-part8.html` | "$450 ต่อ 0.01 BTC ≈0.47%" — เปอร์เซ็นต์ตรงกับ 1 BTC ไม่ใช่ 0.01 BTC |
| N18 | `grid-part9.html` | Cheat sheet "round to $100" ไม่ครอบคลุม fee-floor branch ของสูตร step |
| N19 | `grid-part1a.html` (visual) | Soft Martingale bar chart แสดง Level 4 = 2.8 แต่ตัวอย่างละเอียดกว่าด้านล่างให้ 2.7 (ระดับ rounding) |

---

## จุดที่ตรวจแล้วไม่มีปัญหา (ครบทุกไฟล์)
ทุก anchor link ข้ามไฟล์ resolve ถูกต้อง, nav footer prev/next สอดคล้องกันทั้ง 18 ไฟล์, ไฟล์ที่ไม่ถูกกล่าวถึงข้างบนไม่มี finding ที่ยืนยันได้ (SVG diagram แก้บั๊กเดิมของ Part 0 ยังถูกต้อง, ตาราง/สูตรส่วนใหญ่ของ Part 1B/1C/4/5/6/7/7B/9 recompute ตรงตามที่พิมพ์)
