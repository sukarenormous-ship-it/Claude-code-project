# Grid Trading Mastery — Round 6 Readability/Clarity Audit

**Status:** สแกนแล้ว รอการอนุมัติแก้ไข
**ทีมตรวจสอบ:** 4 ทีมอิสระ เน้น "อ่านง่าย เข้าใจง่าย ชัดเจน" (ไม่ใช่ความถูกต้องของสูตร — ตรวจไปแล้ว 2 รอบ) — beginner-comprehension (5 sub-batch, จำลองผู้อ่านมือใหม่), structure/flow (5 sub-batch), language/prose clarity (5 sub-batch), pedagogical example clarity (5 sub-batch)

**สรุปภาพรวม:** พบปัญหาเยอะกว่าที่คาด เพราะเป็นการตรวจมิติใหม่ที่ยังไม่เคยตรวจมาก่อน รวม **~90 findings** ครอบคลุม 4 กลุ่ม โดยเฉพาะ **"ช่องว่างศัพท์เทคนิค"** (jargon gap) ที่ซ้ำๆ กันในหลายไฟล์ ถือเป็นปัญหาเชิงระบบที่ควรแก้ก่อน ตามด้วยปัญหาเชิงโครงสร้าง/prose ที่กระจายทั่วเล่ม

---

## 🔴 A. ช่องว่างศัพท์เทคนิค (Jargon Gaps) — ปัญหาเชิงระบบ กระทบทั้งเล่ม

**A1. Perpetual futures / short / margin / leverage / liquidation / notional — ไม่เคยอธิบายเลยตลอดทั้งเล่ม**
ใช้ตั้งแต่ Part 1B (Bidirectional Grid) ยัน Part 8 (Cross-Exchange Arb) — Part 1B, 1C, 6, 7, 8 ล้วนอาศัยศัพท์ชุดนี้เป็นรากฐาน มีแค่ 1 ประโยคสั้นๆ อธิบาย "margin" ใน Part 1B เท่านั้น "leverage 10×" ไม่เคยอธิบายว่าทำไม margin ถึงเป็น notional/leverage ไม่เคยพูดถึง liquidation risk ที่มาจาก leverage เลย
**เสนอแก้:** เพิ่มกล่อง "Futures 101" สั้นๆ (4-5 ประโยค) ก่อน Part 1B §1B.2/1B.3 — คำจำกัดความ perpetual, short, margin=notional/leverage, liquidation

**A2. Options vocabulary (PUT/CALL/strike/premium/assignment/ITM/OTM/wings) — ไม่เคยอธิบายใน Part 7 เลย**
Part 7 (§7.3-7.4) สอน CSP, Short Strangle, Iron Condor ผ่านตัวอย่างล้วนๆ ("SELL PUT → ถ้า BTC<strike→assign") โดยไม่เคยอธิบายกลไกพื้นฐาน อ้างอิงไปที่ `pm-part1.html`/`vol-part2.html` แต่ผู้อ่านที่อ่าน Grid เล่มเดียวจะไม่มี background นี้ Part 8 (Laddered CSP) สืบทอดปัญหานี้ต่อ + เพิ่ม "ITM" ที่ไม่เคยอธิบายเลย
**เสนอแก้:** เพิ่มกล่อง "Options 101" ก่อน §7.3 หรือทำให้การอ้างอิง PM Series เป็น "อ่านก่อน" ที่ชัดเจนกว่าปัจจุบัน

**A3. σ (sigma)/standard deviation/68-95% rule/z-score — ไม่เคยอธิบายตั้งแต่ Part 1A**
ใช้หนักตั้งแต่ §1A.4 ("Zone −2σ ถึง +2σ") ต่อเนื่องถึง Part 3B/6 โดยไม่เคยมีกล่องอธิบายแบบเดียวกับที่ Hurst ได้
**เสนอแก้:** เพิ่มกล่องนิยาม σ ก่อน §1A.4 คล้าย pattern ของกล่อง Hurst ใน Part 0

**A4. สถิติ hypothesis-testing (ADF test, null hypothesis H₀, p-value, critical value, Johansen test, trace statistic) — โผล่ใน Part 6 แบบไม่มีฐาน**
ใช้เปรียบเทียบตัวเลข ("ADF stat < critical value → reject H₀") แบบกลไกล้วนๆ ไม่มีคำอธิบายภาษาง่ายๆ เลยว่าทำไม
**เสนอแก้:** เพิ่ม 1-2 ประโยคอธิบายแนวคิด H₀/p-value แบบภาษาชาวบ้านก่อน §6.2

**A5. EMA (Exponential Moving Average) — กลายเป็นกลไกหลักของ Zone Migration (Part 4 §4.6) โดยไม่เคยอธิบาย**
**A6. Beta (regression slope) — ใช้ตั้งแต่ต้น Part 6 แต่คำอธิบายเดียวที่มีอยู่ซ่อนอยู่ใน answer ของ Exercise 3 ท้ายบท** ควรย้ายขึ้นมาต้นบท
**A7. ADX — ไม่อธิบายนาน (Part 0→1C→1D→2) จนมาอธิบายใน Part 4** เป็นข่าวดีที่ในที่สุดก็อธิบาย แต่ถูกใช้เป็น real decision-input 4+ ครั้งก่อนหน้าโดยไม่มีคำอธิบาย
**A8. ATR, Sharpe ratio, "alpha", Drawdown (DD)** — ส่วนใหญ่ท้ายที่สุดก็อธิบาย (ATR ในPart 3, DD ใน Part 5) แต่ล่าช้ามาก โดย "alpha" ไม่เคยอธิบายเลยทั้งเล่ม แม้จะเป็นคำในกล่องปรัชญาหน้าแรกสุดของ index
**A9. TWAP, autocorrelation, VaR, GARCH parameters (ω,α,β), half-life** — ใช้แบบมีคำอธิบายบางส่วนเท่านั้น ไม่ครบ

**A10. Appendix glossary ไม่มี ADX, ATR, Donchian, GARCH, Sharpe, Sortino, Calmar** — ทั้งที่เป็นศัพท์ที่คนน่าจะลืมและมาเปิดหาบ่อยที่สุด

---

## 🟠 B. ปัญหาเชิงโครงสร้าง (Structure/Flow)

**B1. [Major] Part 0 §0.3 หัวข้อไม่ preview เนื้อหาที่สำคัญที่สุดของมันเอง** — ทฤษฎี Random Walk/Shannon's Demon (ที่ตัวเนื้อหาเองบอกว่า "เปลี่ยนวิธีคิดทั้งเล่ม") ถูกฝังใต้หัวข้อ "เทียบกับ Buy-Hold/DCA"

**B2. [Major] "Close System" ถูกนำเสนอเป็น "ประเภทของ grid" ใน Part 0 §0.5 แต่จริงๆ เป็นหลักการข้ามประเภท** — Part 1B §1B.6 ใช้ชื่อเดียวกันกับ Bidirectional grid ทำให้โมเดลความเข้าใจของผู้อ่านต้องปรับใหม่กลางเล่ม

**B3. [Major] Part 8 ไม่มี `<h2>` เลยทั้งไฟล์** — ใช้ `<h3>` ล้วน ผิด convention การนับเลขหัวข้อ "N.M" ที่ใช้ทั่วทั้งเล่ม ทำให้ TOC-based navigation มองไม่เห็น Part 8

**B4. [Moderate] Part 3 นำเสนอ 5 วิธี sizing (ATR/Donchian/Keltner/Bootstrap/GARCH) โดยไม่สรุปว่าควรใช้อันไหนจริง** — §3.4 อ้างตัวเองว่า "ดีที่สุด" แต่ §3.5/§3.6 แย้งโดยนัย และตัวอย่างจริงของเล่ม (§3.9) กลับใช้วิธีง่ายสุด

**B5. [Moderate, หลายจุด] ขาด bridge sentence ข้ามบทหลายจุด** — Part 3B→4 (Hurst สอนซ้ำไม่บอกทำไม), Part 5→2 (ใช้ "bottom-heavy" ไม่อ้างอิงกลับ), Part 6→6B (เปลี่ยนหัวข้อกะทันหันไม่บอก), Part 7→7B→8

**B6. [Moderate] Hurst threshold (0.45/0.48/0.50/0.52/0.55/0.58/0.6) กระจายทั่ว Part 0-1C โดยไม่มีตารางสรุปหรืออธิบายว่าทำไมต่างกัน** (อาจเป็น hysteresis ที่ตั้งใจ แต่ไม่บอกผู้อ่าน)

**B7. [Moderate] Part 4 §4.5 "Grid Reset" vs §4.6 "Zone Migration"** ทั้งคู่ใช้คำว่า "ย้าย/shift" แต่เป็นคนละกลไก (hard reset vs soft trailing) — ชื่อหัวข้อทำให้สับสน

**B8-B15 (Minor-Moderate, ดูรายละเอียดเพิ่มเติมได้จาก raw team reports):** exercise ยากง่ายไม่เรียงลำดับใน Part 2/9, §4.1's diagram โผล่ก่อนสอน ADX/BB, §6.2 คลุมเนื้อหาหนักเกินหัวข้อ "พื้นฐาน", ไม่มี signposting ว่า Part 6 กระโดดความซับซ้อนขึ้นแรง, Part 9's ชื่อ/index สัญญา "state machine/async/WebSocket" แต่ไม่เคยแสดงโค้ดจริง

---

## 🟡 C. ปัญหา Prose/ภาษา (เลือกเฉพาะที่สำคัญ — full list มีจำนวนมาก กระจายเกือบทุกไฟล์)

**C1. [Major] Part 0 §0.1 — ตารางตัวอย่างแรกสุดของเล่มใช้ notation "SELL/BUY" คลุมเครือไม่อธิบาย** ส่งผลกระทบเพราะเป็นตัวอย่างแรกที่ผู้อ่านเจอ

**C2. [Major] Part 6 — "อยู่เหนือจุดยอมแพ้เสมอ" อ่านแล้วดูเหมือนทิศทางกลับด้าน** (ควรหมายถึง "อยู่ก่อนถึง" ไม่ใช่ "เกิน")

**C3. [Major] Part 6B — "+55%" (รวม Grid+Wealth) ถูกเรียกว่า "Grid: +55%" ในตารางสรุป ขัดกับ "+39%" (grid อย่างเดียว) ที่บอกไว้ 4 บรรทัดก่อนหน้า** — สร้างความเข้าใจผิดได้ง่าย

**C4. [Major, ต้องแก้] Part 3 Exercise 4 — มีเศษข้อความ "→ 20 →" ที่ดูเหมือนหลงเหลือจากการแก้ไข Round 5 ของผมเอง** ("N = int(20,000/3,500) = int(5.71) → 20 → 5 levels") ต้องตรวจสอบและทำความสะอาด

**C5. [Major] Part 8 — Flash Crash Grid บรรยายขัดแย้งในตัวเอง**: ประโยคแรกบอก "วางล่วงหน้า" (placed in advance) แต่ Setup section บอกตรงข้าม "วางทันทีหลัง crash (ไม่ใช่ก่อน)"

**C6-C~40 [Moderate-Minor]:** รันออนหลายจุด (โดยเฉพาะ Part 1C's funding-rate analogy, Part 4/5/6 key-idea boxes), เศษ note ภายในหลุดเข้ามาในเนื้อหา (Part 9's "ดู Round 4 audit" **ต้องลบ — พบซ้ำจาก 2 ทีมอิสระ**), URL ไม่ตรงกับโค้ด (testnet.bybit.com vs api-testnet.bybit.com), typo เล็กๆ หลายจุด — ดูรายละเอียดทั้งหมดได้จาก raw team output

---

## 🟢 D. ปัญหา Pedagogical (ตัวอย่าง/แผนภาพ/แบบฝึกหัด)

**D1. [ต้องแก้ด่วน] Part 1C — placeholder ตัวอักษรจริง "$XX" หลงเหลืออยู่ใน diagram แรกสุดของบท** (ควรเป็นตัวเลขจริง)

**D2. [ต้องแก้ด่วน] Part 6B §6B.1/§6B.4 — Zone Upgrade diagram มี label อ่านไม่ออก (ทับกับเส้นขอบ) + มี 3 ชุดตัวเลขไม่ตรงกันสำหรับตัวอย่างเดียวกัน** ($85k-$115k ใน diagram, $80k-$120k ใน Option B, $87k-$113k ใน verification box) — เกี่ยวโยงกับ M10 fix ของ Round 5 ที่ผมแก้แค่ prose ไม่ได้แก้ diagram/Option B

**D3. [ต้องแก้] Part 5 — Kelly chart marker (V2 ที่แก้ไปแล้วใน Round 5) ยังคง render เป็นรูปสามเหลี่ยมทำให้เข้าใจผิดว่าเป็นเส้นกราฟที่สอง** ทั้งที่ caption บอกว่าเป็น "single point" — ต้องเปลี่ยนเป็น scatter/point marker แทน line-interpolation

**D4. [Moderate] Part 1D ไม่มี diagram เลยทั้งไฟล์** ทั้งที่มีระบบ 5-state ที่เหมาะกับ flowchart มาก

**D5. [Moderate] Part 7B ไม่มี "Running Example" section** (ทุก part อื่นในกลุ่มนี้มี) + ตัวเลข Sharpe/DD ในกล่องผลลัพธ์นำเสนอเป็นข้อเท็จจริงโดยไม่มี caveat "สมมติ/illustrative" เหมือนที่ไฟล์อื่นทำ

**D6. [Moderate] Part 8 ไม่มี callout box เตือนความเสี่ยงเลยทั้งไฟล์** — ความเสี่ยงสำคัญถูกฝังในคอมเมนต์โค้ดแทน

**D7-D15 [Minor-Moderate]:** ตัวเลขที่ไม่มีที่มา (Part 1C's Grid Cashflow column, Part 1D's $340 profit figure), Part 3B Exercise 1 ขาดข้อมูล BB Width ที่จำเป็น, Part 9's "state.json" ที่ dashboard อ่านแต่ไม่มีใครเขียน, ฯลฯ

---

## สรุปข้อเสนอแนะการแก้ไข

เนื่องจากรอบนี้เป็นการตรวจ **คุณภาพเชิงอัตวิสัย** (ไม่ใช่ถูก/ผิดชัดเจนแบบ Round 4-5) findings จำนวนมากเป็น "ควรปรับปรุง" ไม่ใช่ "บั๊ก" ขอเสนอแบ่งสเกลการแก้เป็น:

1. **ต้องแก้แน่นอน (สั้น เร็ว ผลกระทบสูง):** C4 (เศษข้อความของผมเอง), C5 (ขัดแย้งในตัวเอง), D1 (placeholder $XX), D2 (diagram เลขไม่ตรง 3 ชุด), D3 (chart marker), C3 (+55% label), C6 (ลบ "ดู Round 4 audit")
2. **ควรแก้ (jargon gaps สำคัญ):** A1 (futures 101), A2 (options 101), A3 (sigma), เพิ่ม A10 (appendix glossary)
3. **ควรพิจารณา (โครงสร้าง):** B1-B3 (Major structure issues)
4. **ถ้ามีเวลา:** ที่เหลือทั้งหมด (Moderate/Minor prose polish, bridge sentences, callout boxes)

รายละเอียดเต็มของทุก finding (รวมถึง quote และ suggested fix ที่ไม่ได้สรุปในเอกสารนี้) อยู่ใน conversation transcript ของ 20 sub-agent reports ที่ทีมตรวจสอบส่งมา
