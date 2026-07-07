# Grid Trading Mastery — Round 5 Audit Findings

**Status:** สแกนแล้ว รอการอนุมัติแก้ไข
**ทีมตรวจสอบ:** 4 ทีมอิสระ (formula/numeric — แยก 5 sub-batch ครอบคลุม 18 ไฟล์, cross-reference/navigation, visual/diagram rendering, trading-logic domain coherence — แยก 5 sub-batch เช่นกัน) ตรวจซ้ำทั้งเล่มหลัง Round 4 แก้ไป 52 findings แล้ว

**สรุปเร็ว:** cross-reference/navigation team ไม่พบปัญหาเลย (0 findings) — โครงสร้าง nav/TOC/cross-ref ยังสะอาดจาก Round 4 formula/domain-logic และ visual teams พบรวม **38 findings** (6 Critical, 16 Moderate, 3 Visual-Moderate, 13 Minor) หลายรายการถูกยืนยันซ้ำโดยทีมอิสระ 2-3 ทีมพร้อมกัน (ความมั่นใจสูง)

---

## 🔴 CRITICAL (6)

### C1. `grid-part7b.html` — `TrendAdaptiveExecution`/`CompositeScoreExecution` ไม่มี `__init__` → โค้ด crash
บรรทัดประมาณ 213-251, 306-344 ทั้งสองคลาสไม่ประกาศ `__init__` เลย แต่ `self.grid` ถูกอ้างอิงในเมธอดของมัน `UnifiedGridController.__init__` เรียก `self.STYLES[style](grid_framework)` แบบ positional-arg เดียวกันกับ 2 คลาสที่มี `__init__` (`MeanReversionExecution`, `VolumeAdaptiveExecution`) — ผลคือถ้าเลือก `style="trend_adaptive"` หรือ `style="composite"` โปรแกรมจะ **crash ทันทีด้วย `TypeError`** ก่อนถึง `run_cycle()` เสียอีก ทั้งที่ทั้ง 2 สไตล์นี้ถูกนำเสนอเป็น first-class option ตลอดทั้งบท (§7B.3, §7B.5, exercises)
**Fix:** เพิ่ม `def __init__(self, grid_framework): self.grid = grid_framework` ให้ทั้งสองคลาส

### C2. `grid-part4.html` — เรียกฟังก์ชันที่ไม่มีจริง (`compute_hurst`)
§4.7 `GridWatchdog.run_checks()` เรียก `compute_hurst(market_data["prices_30d"])` แต่ฟังก์ชันที่ประกาศจริงในไฟล์นี้ชื่อ `hurst_exponent()` (§4.1) — รันจริงจะได้ `NameError` ทันที (ยืนยันซ้ำ 2 ทีมอิสระ)
**Fix:** เปลี่ยนชื่อเรียกเป็น `hurst_exponent(market_data["prices_30d"])`
**หมายเหตุ:** พบ `compute_bb_width()` ถูกเรียกในบรรทัดเดียวกันแต่ก็ไม่มีนิยามในไฟล์นี้เช่นกัน — ยังไม่ยืนยัน 100% ว่าเป็น bug เพราะอาจนิยามอยู่ใน `vol-part2.html` (นอก scope เล่มนี้) ควรตรวจสอบเพิ่มก่อนแก้

### C3. `grid-part6.html` §6.5 — ตัวอย่าง Relative Value Score คำนวณผิดจากสูตรของตัวเอง
สูตร: `0.40×hurst_score + 0.30×z_score_score + 0.30×rsi_score` (ใช้ฟังก์ชันจาก Part 3B) หนังสือระบุ A=62, B=79, C=45 แต่คำนวณจริงจากสูตร (ยืนยันซ้ำอิสระ 2 ทีม ตัวเลขตรงกันเป๊ะ) ได้ **A=47.5, B=75.4, C=39.0** — ผิดทั้ง 3 ค่า (ต่างสูงสุด 14.5 แต้ม) แม้ลำดับ B>A>C และข้อสรุป "70% Pair Grid B / 30% BTC Spot A" จะยังถูกอยู่ก็ตาม
**Fix:** แก้ตัวเลขเป็น 47.5/75.4/39.0 หรือทบทวน weights ให้ตรงกับผลที่ตั้งใจ

### C4. `grid-part2.html` + `grid-part9.html` — สูตร top_heavy/bottom_heavy สลับกัน (2 จุด)
- **`grid-part2.html`** §2.5 `allocate_grid_capital()`: `top_heavy` ใช้ `weights=[1/(n-i)]` (เพิ่มตาม i) และ `bottom_heavy` ใช้ `weights=[1/(i+1)]` (ลดตาม i) — ตามธรรมเนียมของเล่ม (i=0 = level ใกล้ราคาปัจจุบันที่สุด, i มากขึ้น = ลึกลงไปถึง zone_low) ทำให้ `top_heavy` ถ่วงน้ำหนักไปที่ i สูง (= ล่าง) และ `bottom_heavy` ถ่วงน้ำหนักไปที่ i ต่ำ (= บน) — **สลับความหมายกับชื่อฟังก์ชันเอง**
- **`grid-part9.html`** §9.2 `allocate_by_weight()`: `bottom_heavy` ใช้ `weights=[1/(i+1)]` เดียวกัน → น้ำหนักมากสุดอยู่ใกล้ราคาปัจจุบัน ขัดกับนิยามของ `grid-appendix.html` เอง ("บวมล่าง: inventory สะสมมากในโซนราคาต่ำ")
**Fix:** สลับสูตรทั้งสองไฟล์ให้ตรงกับชื่อ/นิยาม เช่น `bottom_heavy = [1/(n-i)]`, `top_heavy = [1/(i+1)]`

### C5. `grid-appendix.html` §A — สูตร Kelly cheat-sheet ใช้ f* เต็มแทน fractional Kelly
Quote: `Capital deployed = f* × total_capital` (ใช้ f* ดิบ ไม่ใช่ fractional Kelly ที่นิยามไว้บรรทัดก่อนหน้า) ขัดกับ Part 9's ตัวอย่างจริง (kelly_fraction≈0.19 = 0.25×f*, ไม่ใช่ f*=0.754 เต็มๆ) และสูตรของ CLAUDE.md เอง ถ้าทำตามตรงๆ จะ deploy ทุนจริง ~75% ของ net worth แทนที่จะเป็น ~19% ตามที่ตั้งใจ — **over-leverage ประมาณ 4 เท่า**
**Fix:** แก้เป็น `Capital deployed = f_safe × total_capital` (โดย f_safe = 0.25×f*)

### C6. `grid-part9.html` — Cheat Sheet เครื่องหมายอสมการ HALT กลับด้าน
บรรทัด 594: `DD ≥ −8% → HALT` — ตามที่เขียน เงื่อนไขนี้จะเป็นจริงเกือบตลอดเวลาการทำงานปกติ (DD=0%, −1%, −7.9% ล้วน ≥ −8%) แต่จะเป็นเท็จพอดีตอนที่แย่ลงกว่า −8% ขัดกับ `config.yaml`'s `dd_halt_threshold: -0.08` และ Exercise 2 ในไฟล์เดียวกัน (บรรทัด 623) ที่ใช้ `<` ถูกต้อง ("DD=−9% < halt_threshold(−8%) → HALT") ยืนยันตรวจ source แล้วพบจริง
**Fix:** แก้เป็น `DD ≤ −8% → HALT`

---

## 🟡 MODERATE (16)

**M1.** `grid-part1a.html` §1A.7 — stress-test ใช้ baseline ผิด: `0.01094×($100k−$60k)=−$437.6` ที่ถูกต้องคือ cost basis($1,014) − market value($656.4) = **−$357.6** (สูงเกินจริง ~22%) ขัดกับวิธีคำนวณที่ถูกต้องในไฟล์เดียวกัน (§1A.2, §1A.9) — ยืนยันซ้ำ 3 ทีมอิสระ ตัวเลขตรงกันเป๊ะ

**M2.** `grid-part1a.html` §1A.7 — ช่วง r∈[1.1,1.5] ที่ประกาศไว้ขัดกับตารางที่ระบุ r=1.6 เป็น "Aggressive Soft" (ไม่มีคำเตือน) ซึ่งขัดกับกล่องเตือนถัดไปที่บอกว่า r>1.5 เสี่ยงมาก — ยืนยันซ้ำ 2 ทีม

**M3.** `grid-part1b.html` — ตัวเลข "+6%" ไม่ตรงกับ margin จริงที่คำนวณ 2 บรรทัดก่อนหน้า ($4,700→$5,230 ที่ 10× leverage = +11.3% ไม่ใช่ +6%) ตัวเลข 6% ตรงกับ scenario 20× leverage ที่ถูกปฏิเสธไปแล้วในย่อหน้าเดียวกัน — ยืนยันซ้ำ 2 ทีม

**M4.** `grid-part1c.html` §1C.4 — กฎ adaptive hedge ลด hedge ratio (เพิ่ม net-long) ทันทีที่ H>0.50 โดยไม่เช็คทิศทาง (Hurst วัด trendiness ไม่ใช่ทิศทาง) ขัดกับ Exercise 4 ในไฟล์เดียวกันที่ต้องใช้ H+ADX ยืนยัน downtrend ร่วมกัน

**M5.** `grid-part0.html` — กราฟ equity curve (Grid +18% / Buy&Hold +35% / DCA +22%) ขัดกับ caption "total return ใกล้เคียงกัน" — Buy&Hold เกือบเป็น 2 เท่าของ Grid

**M6.** `grid-part3.html` §3.7 — แถว "High Vol" ระบุ N=16-22 levels แต่คำนวณจาก Zone/Step ของแถวเองได้ ≈13.3-13.9 (ตรงกับแถว Normal Vol แทน ดูเหมือน copy-paste error) ขัดกับ docstring ของ `vol_regime_step()` ที่ตั้งใจให้ N≈16-22 ทุก regime

**M7.** `grid-part3b.html` + `grid-part4.html` — BB squeeze (width<2%) ให้คะแนน 100/100 ว่า "ideal" สำหรับ deploy grid แต่หลักการ TA มาตรฐานมองว่า squeeze เป็นสัญญาณเตือนก่อน volatility expansion/breakout (ตรงข้ามกับการยืนยัน mean-reversion) ขัดกับตรรกะ Hurst/ADX ของเล่มเองที่มอง trend เป็นศัตรูของ grid

**M8.** `grid-part5.html` §5.3 vs Exercise 2 — §5.3 ปัดขึ้น Q ที่คำนวณจาก Kelly (0.019→0.02, เกิน budget 5%) ในขณะที่ Exercise 2 ปัดลง "เพื่อความปลอดภัย" สำหรับการคำนวณแบบเดียวกัน — วิธีคิดขัดกันเอง โดย §5.3 คือฉบับที่ละเมิด risk budget ของตัวเอง

**M9.** `grid-part5.html` Exercise 4 — อ้างว่า "H=0.62 → Part4 สั่ง GRID OFF ไปแล้ว" จาก Hurst อย่างเดียว แต่โค้ด Part 4 ต้องมี 2-of-3 สัญญาณเห็นตรงกัน สัญญาณ Hurst เดี่ยวรับประกันได้แค่ CAUTION ไม่ใช่ GRID_OFF

**M10.** `grid-part6b.html` §6B.4 vs §6B.8 — ตัวอย่าง zone-upgrade ($10,000, N=10, Q=0.001 BTC) ผิดสูตร `Grid_cap=N×Q×P_avg` ของเล่มเองถึง 10 เท่า (ควรเป็น Q=0.01 ถ้า N=10 หรือ N≈100 ถ้า Q=0.001) และ §6B.8 ใช้ตัวเลข capital/Q/price ชุดเดียวกันแต่กลับสื่อว่า N≈100 ขัดกับ §6B.4

**M11.** `grid-part6b.html` §6B.6 — ตัวเลข "+92.5%/ปี" ไม่ตรงกับสูตร 0.27%/day × reinvest 70% ที่ระบุไว้ (คำนวณจริงได้ ≈+99%) ตารางถูกระบุชัดว่าเป็น illustrative/ไม่ใช่แผนจริงอยู่แล้ว จึงความรุนแรงต่ำ

**M12.** `grid-part7.html` §7.3 — โค้ด `csp_vs_limit_order()` มี dead branch: ตัวแปร `csp_effective_cost`/`csp_income` ถูกคำนวณตาม `expiry_price` แต่ `return` กลับ hardcode ค่าเดิมเสมอ ไม่ว่า `expiry_price` จะเป็นอะไร — พารามิเตอร์นี้ไม่มีผลต่อผลลัพธ์เลย ขัดกับ docstring ของฟังก์ชัน

**M13.** `grid-part7.html` §7.4 — max loss รวมของ Iron Condor คำนวณผิด: ระบุ ~$6,720 (ก็อปมาจาก max loss ของ call-spread เดี่ยวๆ) ที่ถูกต้องคือ max(put width $6,000, call width $7,000) − net credit รวม $730 = **$6,270**

**M14.** `grid-part7b.html` — `VolumeAdaptiveExecution.avg_volume` หารด้วย 20 คงที่ไม่ว่า `volume_history[-20:]` จะมีกี่ตัว (ถ้าน้อยกว่า 20 จะได้ค่าเฉลี่ยต่ำเกินจริง) และถ้า `volume_history` ว่างเปล่า จะได้ `avg_volume=0` → เรียก `get_size_multiplier()` ครั้งถัดไปจะ **ZeroDivisionError**

**M15.** `grid-part3b.html` — `order_accumulation_plan()` ใช้ boundary `>` (75/55/35) ในขณะที่ `resolve_composite_action()` (ที่ประกาศเป็น "single source of truth") ใช้ `>=` — ที่ score=75/55/35 พอดี ทั้งสองฟังก์ชันให้ผลลัพธ์ deploy % ต่างกัน

**M16.** `grid-part4.html` §4.3 — ตัวอย่าง BB_width=8% เป๊ะ ถูกระบุว่าทริกเกอร์ "GRID OFF" แต่โค้ดจริง (`bb_width > 0.08`) ที่ 0.08 พอดีจะตกไปอยู่ใน CAUTION ไม่ใช่ OFF

---

## 🖼️ VISUAL — MODERATE (3)

**V1.** `grid-part3b.html` #chartComposite — หัวกราฟยาวเกิน canvas ตัวอักษรหลุดขอบทั้งซ้าย-ขวา ("C" แรกกับ "o)" ท้ายหายไป) และ data label ตัวแรกถูกบังบางส่วนโดย legend box

**V2.** `grid-part5.html` #chartKelly — จุด marker "Fractional Kelly (25%×f*=15%)" ถูก plot ที่ตำแหน่ง x=20% (ไม่ใช่ 15% ตามป้ายกำกับ) และค่า y ก็ไม่ตรงกับเส้นกราฟ Expected Growth Rate ที่ตำแหน่งนั้น

**V3.** `grid-part7.html` #chartIVRegime — บาร์ "High IV" (ค่า 18) ถูกตัดขอบบนของกราฟเพราะ `mini-charts.js`'s nice-axis rounding ปัดขึ้นแค่ระดับ 15 ไม่รองรับค่าจริง 18 — data label ของบาร์นี้หายไปด้วย (bug ระดับ library ที่อาจเกิดซ้ำที่กราฟอื่นถ้าค่าสูงสุดไม่ตรง gridline)

---

## ⚪ MINOR (13)

- **N1.** `grid-part1a.html` Exercise 1 — floor ที่ระบุ $85k เข้าไม่ถึงด้วย step $2k จากราคาเข้า $100k จริงๆ ไปหยุดที่ $86k โดยไม่บอกช่องว่างนี้
- **N2.** `grid-part1a.html` §1A.9 — ตัวเลข "avg profit $30" ไม่ตรงตารางจริง (เฉลี่ยจริง $36.4) ไม่มีคำอธิบาย weighting
- **N3.** `grid-part1b.html` §1B.8 — `BidirectionalGrid.__init__` รับ `leverage_short` เป็นพารามิเตอร์แต่ไม่ถูกใช้ที่ไหนเลยในคลาส
- **N4.** `grid-part2.html` Exercise 1 — H ที่เพิ่มขึ้นถูกกำกับ "(trending down)" ราวกับ H บอกทิศทางได้ (การสับสนเดียวกับ M4 แต่เบากว่า)
- **N5.** `grid-part3.html` §3.2 — คอมเมนต์บอก "buffer 10%" แต่โค้ดใช้ ×1.05/×0.95 (5% ต่อข้าง) ทุกจุดอื่นในไฟล์เขียนถูกว่า 5%
- **N6.** `grid-part3.html` — N-levels rounding ไม่สอดคล้อง: §3.4 ใช้ floor (int()) แต่ Exercise 4 ปัดขึ้น
- **N7.** `grid-part3b.html` — RSI "extreme" threshold ใช้ 30/70 ใน composite scoring แต่ใช้ 35/65 ใน entry-timing box
- **N8.** `grid-part4.html` — narrative Day18 บอกว่า "รอ Hurst hysteresis exit" แต่การเปลี่ยนสถานะจริงที่ Day21 มาจาก ADX/BB โหวตชนะ Hurst ไม่ใช่ Hurst ข้าม threshold เอง
- **N9.** `grid-part6.html` §6.7 — ตัวอย่าง TP-hit P&L ไม่ได้ simulate การ monitor ต่อเนื่อง ทำให้ผลลัพธ์เป็น best-case เกินจริง (ถูกระบุ caveat ไว้แล้วว่าเป็น best-case)
- **N10.** `grid-part7b.html` §7B.4 — อ้างว่า "03:00-06:00 UTC = Asia night" ซึ่งกลับด้าน (ช่วงนี้คือเวลากลางวันธุรกิจของเอเชีย) ข้อสรุปเรื่อง US-liquidity ต่ำยังถูกอยู่ แค่เหตุผลผิด
- **N11.** `grid-part7.html` — คอมเมนต์ Thai ยาวใน code block ล้นขอบกล่องสีเทาเล็กน้อย (cosmetic เท่านั้น)
- **N12.** `grid-appendix.html` vs `grid-part9.html` — sign convention ของ drawdown ต่างกัน (บวก vs ลบ) ในแต่ละไฟล์ยังถูกต้องในตัวเอง แต่ข้ามไฟล์อาจสับสน (เกี่ยวโยงกับ C6)
- **N13.** `grid-part6.html` §6.2 — สูตร half-life รูปแบบต่างจาก convention ที่ระบุไว้ (τ = −ln(2)/ln(φ)) — ความเชื่อมั่นต่ำ อาจเป็น parameterization ที่ถูกต้องแบบอื่น ไม่ยืนยันว่าผิด

---

## Files with zero confirmed findings
`grid-index.html`, `grid-part1d.html`, `grid-part8.html` (domain-logic), plus visual-clean on `grid-part1c/1d/2/3/4/6/6b/7b/8/9/appendix/part0/1a/1b/index`.
