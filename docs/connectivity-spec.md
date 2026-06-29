# Connectivity Spec — "อ่านกระดาน" (ทำให้เชื่อมทั้งเล่มแบบ ultrasmooth)

> สำหรับทุกทีมเขียน · **ใช้อุปกรณ์ชุดนี้เหมือนกันเป๊ะทุก Part** เพื่อให้เล่มร้อยเป็นเส้นเดียว
> คงโครงสร้าง/style block/SVG valid · render PNG เช็คว่าไม่มี overlap หลังเพิ่ม

---

## 1. Through-line (เส้นเรื่องเดียวทั้งเล่ม) — 4 ด่าน
- **A. อ่านกระดาน (พื้นฐาน)** → Part 0, 1, 2, (ภาคสถิติ)
- **B. รู้ใครกำลังกดดัน & เชื่อได้แค่ไหน** → Part 3, 4, 5, 6, 7, 8
- **C. ตัดสินใจเข้า-ออก / วาง quote** → Part 9, 10, 11, 12
- **D. ต่อยอด & คุมความเสี่ยง** → Part 13, 14, โบนัส
- **Capstone** รวมทุกด่านเป็น workflow เดียว

## 2. Breadcrumb "เราอยู่ตรงไหน" — วางใต้ cover ก่อนกล่องเป้าหมายทุก Part
HTML มาตรฐาน (ตัวที่ active = ครอบด้วย `<b style="color:var(--blue)">…</b>`):
```
<div style="text-align:center;font-size:.82em;color:var(--g7);margin:6px 0 18px">🧭 อ่านกระดาน › รู้ใครกดดัน &amp; เชื่อได้แค่ไหน › ตัดสินใจเข้า-ออก › ต่อยอด/คุมเสี่ยง</div>
```
- Part 1,2 → active ด่าน "อ่านกระดาน" · Part 3–8 → active "รู้ใครกดดัน…" · Part 9–12 → active "ตัดสินใจเข้า-ออก" · Part 13,14,โบนัส → active "ต่อยอด/คุมเสี่ยง"

## 3. Recap + Bridge — ต้น Part (หลัง breadcrumb) และท้าย Part
**ต้น Part** (กล่อง `.bb`):
```
<div class="bx bb"><div class="bt">🔗 ต่อจากตอนก่อน</div>
<p><strong>เพิ่งรู้มา:</strong> [แนวคิดหลักของ Part ก่อน 1 ประโยค] · <strong>ตอนนี้จะเติม:</strong> [แนวคิดของ Part นี้ 1 ประโยค ว่าต่อยอดยังไง]</p></div>
```
**ท้าย Part** (แทนบรรทัดลิงก์เดิม):
```
<p style="text-align:center;color:var(--g7);font-size:.9em"><strong>ส่งต่อ →</strong> [คำถาม/แนวคิดที่ Part ถัดไปจะตอบ]</p>
```

## 4. ⭐ Running case เดียวตลอดเล่ม
**กรณีศึกษา:** *"คุณมีเงิน $5,000 อยากเข้า long BTC/USDT ให้ได้ราคาดีที่สุด ไม่โดน adverse selection แล้วบริหารจนปิดสถานะ"*
แต่ละ Part เพิ่มกล่อง `.bg` สั้น หัวข้อ **"🎯 กับเคสของเรา"** บอกว่าแนวคิดในตอนนี้ช่วยตัดสินใจอะไรในเคสนี้ (1–2 ประโยค) ตาม one-liner นี้:
- **Part 1:** limit ที่เราวางจะไปอยู่ "ท้ายคิว" — เสี่ยงไม่ได้ fill ถ้าราคาวิ่งหนี
- **Part 2:** ถ้าใช้ market buy $5,000 จะ walk the book กี่ชั้น เสีย slippage เท่าไร
- **Part 3:** spread กว้างช่วงไหน (ข่าว/ดึก) → เลี่ยงเข้าไม้ตอนนั้น
- **Part 4:** "กำแพง bid" ใต้ราคาที่เห็น เชื่อเป็นแนวรับได้ไหม หรือเป็น spoof
- **Part 5:** OBI ตอนนี้หนุนการเข้า long ไหม (แต่ระวัง static)
- **Part 6:** เพิ่งมี market buy ก้อนใหญ่ → ควรไล่ตาม หรือรอ revert
- **Part 7:** ไม้ $5,000 ของเราจะดันราคา (impact, λ) แค่ไหน
- **Part 8:** ถ้า VPIN พุ่ง (flow เป็นพิษ) → ชะลอการเข้า
- **Part 9–11:** ถ้าเปลี่ยนเป็น "วาง limit เป็น MM" แทน taker — ได้ rebate แต่รับ inventory risk
- **Part 12:** ใช้ grid ทยอยเข้าแทนไม้เดียว เอียงตาม OBI
- **Part 13:** ใช้ OFI ของ BTC เป็นสัญญาณจังหวะเข้า
- **Part 14:** เทียบราคาข้าม exchange ก่อนเข้า + คิด effective price จริง
- **โบนัส:** ML ทำนายจังหวะเข้าได้ไหม (และทำไมยังไม่ใช่จุดเริ่ม)

## 5. เนื้อหาที่ต้องเติม (จากแผน §8) — เป็น "ตัวเชื่อม" ไม่ใช่บทแยก
- **§8.2 การแปลผล:** Part 3/4 เพิ่มตาราง "เห็นแบบนี้ = อาจหมายถึง" (spread กว้างขึ้น/คิวหาย) · **Part 4 เพิ่มกล่อง+ภาพ "อ่านพฤติกรรม Market Maker ถอน quote"** (ถอน 2 ฝั่ง=หลบเสี่ยง/ก่อนข่าว · ฝั่งเดียว=เอียงมุมมอง · ต่างจาก spoof)
- **§8.5 stylized facts:** Part 6 เพิ่มหมายเหตุ "sign autocorrelation (order flow ติดกันเป็นชุด → โยง Hawkes)" · Part 8 "volatility clustering" · Part 3 "intraday U-shape (spread/vol รูปตัว U ตลอดวัน)"
- **§8.4 เป็น cross-ref สนับสนุน (กล่อง `.ba` เท่านั้น ไม่ใช่บทใหม่):** Part 7 → square-root impact law (impact ∝ √volume, เสริม Kyle) · Part 8 → Detecting Toxic Flow (Cartea 2023, benign vs toxic สมัยใหม่) · Part 10/11 → Almgren-Chriss (optimal execution) + Guéant (2017) · โบนัส → Briola 2024/25 "microstructural guide" (forecasting ≠ สัญญาณจริง)
- **§8.1 นิยาม microstructure:** Part 0 (หัวหน้าทีมทำเอง)

## 6. Paper audit
ทุก paper ในเนื้อหลักต้องตอบได้ว่า **"ช่วยผู้อ่านตัดสินใจอะไรในเคส running case"** — ถ้าตอบไม่ได้ ให้ย้ายเป็น cross-ref/ภาคผนวก ไม่ยัดในเนื้อ

## 7. Capstone (หัวหน้าทีมทำเอง)
บทปิด **"อ่านกระดานจริง 1 รอบ"** = decision workflow รวมทุก Part กับ running case ($5,000 long BTC) ตั้งแต่เปิดจอ → ประเมิน → เข้า/ออก → คุมเสี่ยง · ทุกองก์ลิงก์ไป capstone ได้

---

## สิ่งที่หัวหน้าทีม (ผม) ทำเอง — ไม่ต้องแตะ
- **Part 0:** นิยาม microstructure + **master concept map (you-are-here ภาพใหญ่)** + breadcrumb/recap (เป็นต้นแบบ)
- **ภาคสถิติ:** breadcrumb + recap
- **บท Capstone** + master map
