# แผน — องก์ VI: Execution (ทยอยส่งไม้ใหญ่ให้ impact ต่ำสุด)

> ส่วนต่อยอดของหนังสือ "อ่านกระดาน" · อิงแผนแม่บท §8.4 · **แผนก่อน ยังไม่ลงมือ**

## 1. Positioning — เติมจิ๊กซอว์ที่เล่มหลักยังขาด
เล่มหลัก (Part 0–14) สอน **"อ่านกระดาน + เป็นผู้วาง quote (market making)"** แต่ยังไม่ตอบคำถามที่ใกล้ตัวรายย่อยมาก:
> **"ถ้าฉันมีไม้ใหญ่เทียบสภาพคล่อง (เช่นเหรียญ alt บาง ๆ) จะส่งยังไงให้ไม่ดันราคาตัวเองจนขาดทุน?"**

นี่คือ **ด้านกลับของ market making** = ฝั่ง taker ที่อยาก execute ให้ดีที่สุด · Capstone มี forward-reference ไป Almgren-Chriss อยู่แล้ว → องก์นี้คือ "อ่านต่อ" ที่เป็นรูปเป็นร่าง

**เชื่อมเล่มหลัก:** Part 2 (walk the book/slippage) · Part 7 (Kyle's λ = market impact) · Part 8 (VPIN จับจังหวะหลบ toxic) · Part 11 (latency/กับดัก backtest) · Capstone ขั้น 5 (เลือกวิธีเข้า)

## 2. รูปแบบ (เสนอ)
- **prefix:** `ob-ex-1/2/3.html` (เป็น "องก์ VI" ของซีรีส์เดิม ใช้ style/connectivity ชุดเดียวกัน)
- breadcrumb: active = **"ตัดสินใจเข้า-ออก"** (execution = วิธีเข้า/ออกจริง) — ลึกกว่าที่ Part 9–12 แตะ
- ใช้ running case เดิม ($5,000 long BTC) + ขยายเป็น **"ไม้ใหญ่บนเหรียญสภาพคล่องปานกลาง"** เพื่อให้ execution มีความหมาย
- หลัง 3 ตอนเสร็จ → อัปเดต Capstone "อ่านต่อ" ให้ชี้เข้าองก์นี้ + rebuild เล่มรวม

## 3. โครง 3 ตอน

**EX-1 · ปัญหา Execution & Implementation Shortfall** — อุปมา: เทน้ำลงแก้ว (เร็ว=กระเด็น / ช้า=ระเหย)
- ทำไมไม้เดียวแพง: market impact (ต่อจาก walk the book Part 2)
- **trade-off หัวใจ:** ส่งเร็ว → impact สูง · ส่งช้า → timing/price risk สูง
- นิยาม **Implementation Shortfall (IS)** = ราคาที่ได้จริง − arrival price (benchmark)
- แยก **temporary impact** (เด้งกลับ) vs **permanent impact** (ถาวร)
- สูตร: `IS = Σ(fill_i − P_arrival)·q_i + ต้นทุนคงเหลือ`
- ภาพ: เทน้ำ, IS decomposition (impact + timing), temporary vs permanent

**EX-2 · Almgren-Chriss & ตารางการทยอยส่ง** — อุปมา: ทยอยขายของในตลาดไม่ให้ราคาตก
- temporary impact ∝ อัตราเทรด, permanent impact ∝ ปริมาณสะสม
- **optimize trade schedule:** minimize E[cost] + λ·Var[cost] → ได้ trajectory
- **efficient frontier** (expected cost ↔ variance) + บทบาท risk aversion γ
- เทียบ **TWAP / VWAP / IS-optimal** — อันไหนเหมาะเมื่อไหร่
- สูตร AC: trajectory แบบ exponential decay, κ = √(λσ²/η)
- ภาพ: efficient frontier, trade schedule (front-loaded AC vs flat TWAP), เทียบ 3 กลยุทธ์

**EX-3 · ลงมือจริง (รายย่อยคริปโต)** — อุปมา: กระจกห้องลองเสื้อ (ภาคต่อจาก Part 11)
- slicing: แบ่ง parent → child orders; **TWAP / VWAP / POV (percentage of volume)**
- limit vs market สำหรับ child; ใช้สัญญาณกระดาน (OBI/OFI Part 5–7, VPIN Part 8) **จับจังหวะ child orders**
- กับดัก: front-run เงาตัวเอง, fee สะสม, latency, เหรียญบางยิ่ง impact สูง
- **ตารางความจริงรายย่อย:** ไม้เล็ก → market ก็พอ · ไม้ใหญ่/เหรียญบาง → ต้อง slice · HFT execution algo = เกินรายย่อย
- ภาพ: parent→child slicing, ใช้ OFI จับจังหวะ child, flowchart เลือกกลยุทธ์ตามขนาดไม้/สภาพคล่อง

## 4. Papers
- **Almgren & Chriss (2000)** *Optimal Execution of Portfolio Transactions* — แกน
- **Obizhaeva & Wang (2013)** — execution บน LOB จริง (supply/demand resiliency)
- **Bertsimas & Lo (1998)** — ต้นกำเนิด · **Guéant** *Financial Mathematics of Market Liquidity*
- cross-ref: **square-root impact law** (Bouchaud) จาก Part 7 · Cartea-Jaimungal-Penalva (book)

## 5. มาตรฐาน (เหมือนเล่มหลัก)
Sarabun · design tokens เดิม · กล่อง .bg/.br/.bb/.ba · .fm · inline SVG ≤500px (ฟอนต์ป้ายเลข ≥11px, ไม่ทับเส้น) · breadcrumb + recap/bridge + 🎯 running case + นโยบายศัพท์ §8 (term-of-art อังกฤษ + ไทยวงเล็บครั้งแรก: execution, implementation shortfall, market impact, TWAP/VWAP/POV, trade schedule)

## 6. Phasing
1. เขียน EX-1 → EX-2 → EX-3 (อาจให้ทีมผู้เชี่ยวชาญเขียน หรือผมเขียนเอง)
2. cross-review (เนื้อหา+ลื่น+ถูกต้อง) + viz pass
3. อัปเดต Capstone "อ่านต่อ" + master map (เพิ่มองก์ VI) + rebuild ob-book + zip
4. verify สูตร AC กับ paper ต้นฉบับก่อน finalize

## ⚠️ ความซื่อสัตย์รายย่อย (ต้องเน้น)
- รายย่อยส่วนใหญ่ไม้เล็ก → execution algo ไม่จำเป็น; มันสำคัญเฉพาะ **ไม้ใหญ่เทียบสภาพคล่อง / เหรียญ alt บาง**
- AC closed-form = กรอบคิด ไม่ใช่สูตรที่รายย่อยรันเป๊ะ; ของจริงใช้ TWAP/VWAP/POV + สัญญาณกระดาน
- HFT execution (smart order routing ข้าม venue ระดับ ms) = เกินสนามรายย่อย
