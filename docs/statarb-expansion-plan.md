# แผนปรับปรุงเล่ม Statistical Arbitrage — "ครบทุก ε ไม่จำกัดแค่ Log Price"

> พิมพ์เขียวสำหรับขยายเล่ม Stat Arb (`docs/statarb-ch0..24 + appendix A/B` บน branch
> `claude/continue-latest-commit-sxxwJ`) ให้ครอบคลุม **ทุกรูปแบบ F(·)** พร้อมสถานการณ์ใช้งานจริง
> ตามหลักเดิมของเล่ม: ε = F(A) − β·F(B) คือกระดูกสันหลัง — ทุกอย่างคือ synthetic process

---

## 0. โจทย์จากผู้ใช้ (เคาะแล้ว)

| หัวข้อ | ข้อสรุป |
|---|---|
| **ปัญหา** | เล่มปัจจุบันเจาะลึก **log price** เป็นหลัก (pipeline ch1–12 ทั้งสายใช้ log pairs) ส่วน F(·) แบบอื่นมีแบบกระจัดกระจาย/ผิว หรือไม่มีเลย |
| **เป้าหมาย** | อธิบาย **ทุก F(·) ให้ลึกเท่ากัน** — absolute price, basis, funding/yield, options/IV และเติมตัวที่ยังไม่มี |
| **Options** | หมายถึง **เอา options มาเป็นเครื่องมือทำ stat arb** (สร้าง ε บน IV/PCP/skew แล้วเทรด mean reversion ของมัน) — แกนคือ ch22 เดิม ขยายให้เต็ม ไม่ใช่แค่ overlay |
| **บทเดิมทั้งสาย** | pipeline ch1–12 ต้อง **generalize พ้น log price**: ตัวอย่าง/สูตร/โจทย์ให้สลับ F(·) หลายแบบ ไม่ใช่ log pairs อย่างเดียว |
| **กฎเหล็ก** | ทุก ε ต้องมี **"สถานการณ์ที่ได้ใช้"** — trigger เกิดเมื่อไร ตลาดแบบไหน เจอบ่อยแค่ไหน ใครอยู่อีกฝั่ง ไม่ใช่แค่สูตร |
| **สไตล์** | คงรูปแบบเดิมของเล่ม: แก่นของบทนี้ → กลไก → สูตร → Running Example ตัวเลขจริง → กับดัก → แบบฝึกหัด |

### 0.1 บทเรียนจากการเทรดจริงของผู้ใช้ (calendar arb ทองคำ — ขาดทุน) → ต้องตอบในเล่ม

ผู้ใช้เทรด calendar arb ทองคำ (ตลาด contango) + cross-exchange CME↔APEX แล้วขาดทุน/ไม่มี order ทั้งที่คนอื่นได้กำไร — วิเคราะห์แล้วเจอ pitfall 6 จุดที่เล่มปัจจุบัน**ยังไม่ได้สอน**:

1. **Full-carry market ไม่มี signal edge** — contango ของทอง = fair carry (rate + storage − convenience) ไม่ใช่ mispricing; คนที่กำไรคือคนต้นทุน carry ต่ำกว่า (funding ถูก, มี vault, เป็น MM) → เกมนี้คือ**เกมต้นทุน ไม่ใช่เกมสัญญาณ** — ระบบที่บอกว่า "ไม่คุ้ม" อาจถูกแล้ว
2. **ε ต้องเป็น deviation จาก fair carry ไม่ใช่ spread ดิบ** — ε_t = spread_t − fair_carry_t โดย r ใช้ rate curve จริง (spread ทองที่วิ่ง ส่วนใหญ่คือ rate expectation เปลี่ยน — ไม่ hedge ขา rate = เทรดดอกเบี้ยโดยไม่รู้ตัว)
3. **Cross-exchange metal เดียวกัน ≠ instrument เดียวกัน** — delivery คนละที่/สเปกต่าง → θ ≠ 0, no-arb band กว้างเท่าต้นทุนขนจริง, ในแบนด์**ไม่มีแรงดึงกลับ** (เคส EFP มี.ค. 2020)
4. **Legging kill edge** — เข้า/ออกทีละขา = จ่าย bid-ask 4 ครั้งบน spread ที่ σ ไม่กี่ tick; ต้องใช้ listed calendar spread instrument
5. **ถือใกล้ expiry = โดน delivery dynamics** ไม่ใช่เก็บ convergence
6. **Spread chart จาก last-trade สองขาที่ print คนละเวลา = spike ปลอม** — ต้องใช้ synchronized mid + เส้น executable spread; คำถาม line vs candlestick เป็นคำถามผิด — ปัญหาอยู่ที่ data ข้างใต้

→ กลายเป็น **Phase 4 ใหม่** (ch17 ยกเครื่อง + ch10b บทใหม่เรื่อง spread data/TF/charting) ด้านล่าง

### 0.2 แคตตาล็อกจุดขาดทุนเพิ่มอีก 31 ข้อ — จากคณะผู้เชี่ยวชาญ 4 เลนส์

ผู้ใช้บอก "ยังนึกจุดขาดทุนอื่นๆ ไม่ออก" → ส่งทีมผู้เชี่ยวชาญ 4 คน (โต๊ะ futures · execution/microstructure · econometrician · retail ตัวจริง) อ่านเล่มทั้ง 27 ไฟล์แล้วขุดเพิ่ม ได้ **31 ข้อ (~25 ประเด็นอิสระ)** — รายละเอียดเต็มทุกข้อ (กลไก/ทำไมนึกไม่ถึง/ป้องกัน/ตัวเลข/บทปลายทาง) อยู่ที่ **`statarb-loss-catalog.md`**

ไฮไลต์ที่ร้ายแรงสุด (🔴 เจ๊งพอร์ตได้):
- **หน่วยสัญญา oz↔กรัม + การปัดเศษ** — GC = 100 troy oz (3,110.35 g) เทียบสัญญา 100 g → ratio จริง 31.1035:1 เทรดได้ 31:1 เหลือทองเปลือยที่ noise รายวันใหญ่เท่า edge
- **Margin สองไซโล ไม่มี SPAN spread credit** — cross-exchange ต้องวาง margin เต็มสองขา และตอน spread ถ่าง ขาขาดทุนโดนเรียกเงินสดที่โบรก A ทันที ส่วนกำไรค้างอยู่โบรก B (โอนข้ามประเทศ 1–3 วัน) → ถูกบังคับปิดที่จุดถ่างสุด = LTCM สเกล retail
- **Settlement mark คนละเวลา** — CME settle ตี 1 ครึ่งไทย, เอเชีย settle บ่าย → variation margin "ผี" เรียกเงินสดทั้งที่ spread ไม่ขยับ
- **FND/LTD คนละวัน + benchmark คนละตัว** — เทรด convergence ที่ไม่มีวันนัด converge จริง
- **Multiple testing** — scan หลายคู่แล้วเอาคู่ที่ผ่าน ADF = winner's curse; + grid-search z threshold ซ้ำอีกชั้น
- **Half-life ยาวกว่าอายุที่เหลือของสัญญา** + backtest บน continuous contract ที่ต่อเชื่อม = เทรด ε ที่ไม่มีอยู่จริง
- **ภาษีไม่ net ข้ามขา/jurisdiction** — กำไรขา A โดนเก็บเต็ม ขาดทุนขา B หักไม่ได้
- **จิตวิทยาตัดขาเดียว** — "เก็บกำไรขาที่บวก" = เปลี่ยน arb เป็น directional bet ตรงจุดแย่สุด

การกระจายลงบท: กลุ่ม margin/เวลา/สเปก → Phase 4 (17.10–17.13 ใหม่ + ch10b) · กลุ่มสถิติหลอก → ch4b + Phase 5 · กลุ่มบัญชีเล็ก → ch19/ch12 · จิตวิทยา → ch11/ch20 (ดูตารางท้าย catalog)

### 0.3 โจทย์เพิ่มรอบ 3 (ผู้ใช้อนุมัติแผนแล้ว + ขอเพิ่ม)

1. **Kalman churn (ประสบการณ์ตรงผู้ใช้)** — ใช้ Kalman แล้วขาดทุนเพราะปรับ position บ่อย: β วิ่งตาม noise (Q ใหญ่เกิน) → rebalance ถี่ → fee/slippage สะสมกิน edge — วิเคราะห์เต็ม + วิธีป้องกัน (deadband, แยกนาฬิกาความเชื่อ/นาฬิกา position, วัด turnover ของ β ตอน calibrate) อยู่ที่ `statarb-loss-catalog.md` §H1 → ลง ch15 + ตาราง cost ch19 (Phase 5)
2. **Null Hypothesis 101 (ผู้ใช้ขอ)** — เล่มใช้ ADF/p-value ตั้งแต่ ch5 โดยไม่เคยอธิบายว่า H₀ คืออะไร → เพิ่ม **ch5 §5.0 "Null Hypothesis คืออะไร — ก่อนอ่านค่า p ใดๆ"**: H₀/H₁ คืออะไร (ศาลตัดสิน "จำเลยบริสุทธิ์ไว้ก่อน"), p-value แปลว่าอะไร/ไม่ได้แปลว่าอะไร, H₀ ของ ADF คือ "มี unit root (ไม่ stationary)" ดังนั้น p ต่ำ = ปฏิเสธ H₀ = stationary (จุดที่คนอ่านกลับทางบ่อยที่สุด), Type I/II error ในบริบทเลือกคู่เทรด, power ของ test เมื่อ sample สั้น, โยงเข้า multiple testing (catalog E) — ทำใน **Phase 1** (มาก่อนเพราะทุกบทถัดไปอ้าง p-value)
3. **QA เนื้อหา + ภาพประกอบ (ผู้ใช้ขอ)** — ผู้ใช้พบ "บางภาพตัวหนังสือทับกราฟ อ่านไม่รู้เรื่อง" → เพิ่ม **Phase QA**: ทีม 11 คน (6 ตรวจความถูกต้องความรู้แบ่งตาม cluster + 5 ตรวจภาพด้วย screenshot จริงทั้ง 27 ไฟล์ ที่ 900px และ 390px) — หมายเหตุ: สาเหตุใหญ่ของ "ตัวหนังสือทับกัน" น่าจะคือบั๊ก `.fm` ใน Phase 0.5 ที่แก้แล้ว (ASCII diagram โดนยุบบรรทัด) — QA รอบนี้ยืนยัน + เก็บที่เหลือ

---

## 1. Audit — ตอนนี้แต่ละ F(·) อยู่ตรงไหน ลึกแค่ไหน

| F(·) | สูตร ε | บ้านปัจจุบัน | ความลึก | ช่องว่าง |
|---|---|---|---|---|
| **Log price** | log P_A − β·log P_B | ch1–12, 15, 16, 23 (pipeline เต็มสาย) | ●●●● | — (สมบูรณ์แล้ว ใช้เป็นแม่แบบ) |
| **Absolute/Raw price** | P_A − β·P_B | แค่ตาราง §1.6 + §4.6.1 | ● | **ไม่มีบทกลยุทธ์จริงเลย** — ทั้งที่เป็นตัวถูกของ stablecoin peg, PAXG↔XAU, dual-listed futures |
| **Ratio** | P_A / P_B | ไม่มี | ○ | ไม่มีเลย (ญาติของ log — ต้องอธิบายว่าเมื่อไรใช้ ratio ตรง ๆ) |
| **Basis (perp−spot)** | P_perp − P_spot | ch13 | ●●●● | ลึกแล้ว — ขาดเชื่อมไปตระกูล funding โดยตรง |
| **Calendar (futures)** | P_front − β·P_back | ch17 | ●●● | ขาด roll dynamics + delivery convergence trade |
| **Funding / Yield spread** | funding_A − funding_B | ไม่มี (ch13 พูดถึง funding ในฐานะกลไกของ basis เท่านั้น) | ○ | **ไม่มีเลย** — cross-venue funding arb, staking yield vs funding |
| **Swap (CFD)** | ch21 spot↔CFD | ch21 | ●●●● | niche แต่ครบแล้ว |
| **Options: PCP** | C − P − (S − K·e^(−rT)) | ch18 | ●●● | ขาด American/early-exercise เชิงลึก, fee band ทำให้ PCP กว้าง |
| **Options: IV surface** | IV_A − β·IV_B | ch22 (box, RR skew, cross-venue IV, VRP) | ●●● | ขาด **IV term structure ε**, **dispersion**, **sticky strike vs sticky delta**, PnL decomposition (vega/gamma/theta) ของ ε trade |
| **กรอบเลือก F(·)** | — | §1.6 (ตาราง) + §4.6.1 (raw vs log vs basis) | ●● | **ไม่มี decision framework เต็ม** — ผู้อ่านยังตอบไม่ได้ว่า "สถานการณ์นี้ใช้ ε ไหน" อย่างเป็นระบบ |

ตรวจแล้วด้วย grep ทั้งเล่ม: ไม่มีคำว่า stablecoin / USDC / dispersion / sticky / funding spread / ratio spread ปรากฏเลย

---

## 2. หลักออกแบบ: "Situation Card" — มาตรฐานบังคับของทุก ε

ทุก ε (ทั้งเก่า retrofit และใหม่) ต้องมีกล่อง **🎯 สถานการณ์ที่ได้ใช้** ตอบ 6 คำถาม:

1. **Trigger** — อะไรทำให้ ε เบี่ยง (sentiment รุนแรง / event / โครงสร้างตลาด / liquidity แตก)
2. **Regime** — ตลาดแบบไหนโอกาสโผล่บ่อย (euphoria → basis บวม · panic → PCP/box หลุด · sideways เงียบ → pairs ทำงานดี · event/earnings → IV เบี่ยง)
3. **ความถี่ + อายุ** — เจอกี่ครั้ง/เดือน อยู่ได้นานแค่ไหนก่อนโดนปิด (วินาที→latency, ชั่วโมง→basis, วัน-สัปดาห์→pairs)
4. **Edge vs Friction** — ขนาดเบี่ยงทั่วไปกี่ σ / กี่ % เทียบ fee+slippage+funding (โยง ch19)
5. **ใครอยู่อีกฝั่ง** — เพราะอะไรเขายอมให้เรากิน (forced flow, retail sentiment, inventory constraint, regulatory segmentation)
6. **สัญญาณ setup พัง** — อะไรบอกว่าความสัมพันธ์สลาย ไม่ใช่โอกาส (โยง ch24 case studies)

> เหตุผล: ผู้ใช้ระบุว่า "แต่ละอย่างมันต้องมีสถานการณ์ที่ได้ใช้" — สูตรที่ไม่รู้ว่าเมื่อไรได้ใช้ = ความรู้ที่เทรดไม่ได้

---

## 3. โครงงานเขียน — 5 Phase

### Phase 0 — รวมบ้านก่อน (โครงสร้าง repo)
ไฟล์เล่ม statarb อยู่บน branch `claude/continue-latest-commit-sxxwJ` แยกจากสายหลัก
→ ดึง `docs/statarb-*` เข้า branch ทำงานปัจจุบันก่อนแก้ เพื่อให้ diff/รีวิว/PDF rebuild อยู่ที่เดียว

### Phase 0.5 — Quick Win: แก้สูตรอ่านไม่ออกทั้งเล่มด้วย CSS บรรทัดเดียว
ผู้ใช้รายงาน "สูตรอ่านยากมาก เรียงไม่เป็นประโยค" — ทีม typography วินิจฉัย + ยืนยันแล้ว:
- **Root cause**: ทั้ง 27 ไฟล์เขียนสูตรใน `<div class="fm">` โดยพึ่ง plain newline + จัดคอลัมน์ด้วย space แต่ CSS `.fm` **ไม่มี `white-space` property** → browser ยุบทุกบรรทัดเป็นประโยคเดียว (สมการหลายตัวไหลติดกัน, limits ของ Σ ที่จัดไว้ใต้เครื่องหมายหลุดลอยไปท้ายประโยค)
- **Fix ทันที**: เติม `white-space:pre` เข้า rule `.fm` (rule เหมือนกันเป๊ะทุกไฟล์ → sed ครั้งเดียวจบ 27 ไฟล์) — ปลดล็อก **114 กล่องสูตร multi-line ใน 23 ไฟล์** ให้กลับมาเรียงบรรทัดตามที่ผู้เขียนตั้งใจ; มี `overflow-x:auto` อยู่แล้ว มือถือจึงแค่ scroll แนวนอนไม่ล้นจอ
- **เก็บตก**: 6 กล่องใน 3 ไฟล์ (ch17×2, ch18×2, ch23×2) มี newline หัว/ท้ายกล่องที่จะกลายเป็นบรรทัดว่างส่วนเกิน — ลบมือ; 47 บรรทัดยาว >78 ตัวอักษร ยอม scroll ไว้ก่อน ค่อยหักบรรทัดตอน Phase 5
- ทำทันทีหลัง Phase 0 แล้ว rebuild PDF หนึ่งรอบ → ผู้ใช้ได้เล่มที่อ่านสูตรออกโดยไม่ต้องรอเนื้อหาใหม่

### Phase QA — ตรวจความถูกต้อง + ภาพประกอบทั้งเล่ม (⏳ กำลังรัน)
ทีม 11 คน: 6 content clusters (foundations / stats / advanced-model / execution / strategies / appendix — ตรวจสูตร, คำนวณตัวอย่างซ้ำ, ตรวจ claim ประวัติศาสตร์, หา null-hypothesis gaps) + 5 visual reviewers (screenshot ทุกไฟล์ที่ 900px+390px หา ตัวหนังสือทับกัน / KaTeX พัง / ล้นจอ) → ผลรวมเข้า issue list แล้วแก้เป็น commit แยกก่อนเริ่มเขียนเนื้อหาใหม่

### Phase 1 — บทกรอบใหม่: "ε Design — เลือก F(·) จากสถานการณ์" (`statarb-ch4b`) + Null Hypothesis 101
งานที่ 2 ของ Phase นี้ (ผู้ใช้ขอ): **ch5 §5.0 "Null Hypothesis คืออะไร"** — สเปกอยู่ที่ §0.3 ข้อ 2
บทแทรกหลัง ch4 (ตาม pattern `pm-part3a` ไม่ต้อง renumber ทั้งเล่ม) — ยกระดับ §1.6 + §4.6.1 เป็นบทเต็ม:
- **Decision tree 1 หน้า**: สินทรัพย์เดียวกันคนละ venue? → basis/log · เป้าหมายคือ carry ไม่ใช่ราคา? → funding/basis · คนละ asset คนละ scale? → log · หน่วยเดียว scale เท่ากัน? → absolute · มุมมองอยู่บน vol ไม่ใช่ราคา? → IV
- **ตารางแม่บท "สถานการณ์ → ε ที่ถูก"** (ทุกแถวลิงก์ไปบทของมัน): peg แตก→absolute · perp บวม→basis · funding ต่าง venue→funding spread · IV กระโดดขา front→term structure ฯลฯ
- **Regime map**: ε ไหน "มีของ" ในตลาดแบบไหน (สอดคล้อง Regime-Switching ch9)
- **กับดักข้ามประเภท**: unit mismatch, stationarity คนละความหมายต่อ F, β เปลี่ยนความหมายเมื่อเปลี่ยน F (ต่อยอด §4.6.1)
- แบบฝึกหัดรูปแบบ "ให้สถานการณ์ 8 ข้อ เลือก F(·) + ให้เหตุผล" (ขยายจากโจทย์ท้าย ch4 ที่มีเค้าอยู่แล้ว)

### Phase 2 — เติม F(·) ที่หายไป (2 บทใหม่)
**`statarb-ch13b` — Absolute Price & Ratio: เมื่อหน่วยเดียวกันแท้ ๆ**
- ทฤษฎี: เมื่อไร absolute ถูกกว่า log (สอง instrument อ้าง underlying เดียวกัน หน่วยเดียวกัน — ε มีความหมายเป็น $ ตรง ๆ) + ratio ε = P_A/P_B และความสัมพันธ์กับ log
- กลยุทธ์จริง 3 ตัว พร้อม Situation Card:
  1. **Stablecoin peg** (USDT/USDC, depeg event) — absolute ล้วน, mean = 1.0000 ที่รู้ล่วงหน้า (ไม่ต้อง estimate θ!) → จุดสอนพิเศษ: ε ที่มี anchor เชิงโครงสร้าง vs anchor เชิงสถิติ
  2. **Tokenized vs จริง** (PAXG ↔ XAUUSD) — เทียบให้เห็นว่า log ก็ได้/absolute ก็ได้ เมื่อไรต่างกันจริง
  3. **Dual-listed futures เดือนเดียวกัน** (BTC Jun futures บน 2 exchange) — absolute โดยธรรมชาติ
- กับดัก: peg ไม่ใช่ cointegration (depeg = jump ไม่ใช่ mean reversion — โยง ch8 jump-diffusion), liquidity หายตอน depeg จริง

**`statarb-ch13c` — Funding & Yield Spreads: เทรด "อัตรา" ไม่ใช่ "ราคา"**
- ε = funding_A − funding_B (Bybit↔Lighter cross-venue funding) — running example ต่อจากคู่หลักของเล่มเดิมได้ทันที
- Cash-and-carry ซ้อน yield: staking yield (stETH) vs funding — ε = (funding earned) − (staking yield forgone)
- โครงสร้าง: อัตราเป็น % ต่อช่วงเวลา → ต้อง normalize interval (8h vs 1h) ก่อนสร้าง ε — จุดที่คนพลาดบ่อยสุด
- Situation Card: funding spread บาน ตอน sentiment สุดขั้วข้างเดียว + venue เล็ก lag venue ใหญ่
- โยง ch13 (basis คือ integral ของ funding โดยประมาณ) — สองบทนี้เป็นพี่น้องกัน

### Phase 3 — Options เป็นเครื่องมือ Stat Arb เต็มตัว (ยืนยัน scope แล้ว: เทรด ε บน vol ไม่ใช่แค่ overlay)
**ขยาย `ch18` (PCP):**
- American vs European — เมื่อไร PCP เป็น inequality ไม่ใช่ equality, early exercise (crypto options ส่วนใหญ่ European แต่ dated futures + coin-settled มี quirk)
- **PCP band ในโลกจริง**: fee + spread ทำให้ violation ต้องเกิน band ก่อนเทรดได้ — คำนวณ band จริงของ Deribit
- Situation Card: PCP หลุดตอนไหน (expiry ใกล้ + panic, liquidity ขาข้าง put ตอน crash)

**ขยาย `ch22` (IV Stat Arb) — เพิ่ม 4 หัวข้อ:**
1. **IV Term Structure ε** — front IV − β·back IV (ต่อยอด 18.4 ที่แตะไว้ ให้เป็น strategy เต็ม พร้อม event calendar: ก่อน/หลัง FOMC, ETF decision)
2. **Dispersion เบื้องต้น** — BTC index IV vs basket IV ของ majors (โครงสร้างเดียวกับ multi-leg ch16 แต่บน vol) — ระบุชัดว่าเป็น L2 topic + ข้อจำกัดข้อมูล alt IV
3. **Sticky Strike vs Sticky Delta** — ทำไม RR_25Δ ε (22.3) ที่ดู mean-revert อาจเป็นภาพลวงจาก smile dynamics — นี่คือ "กับดักเชิงโครงสร้าง" ของ vol stat arb
4. **PnL Decomposition ของ ε trade บน options**: vega (ที่ตั้งใจกิน) vs gamma/theta (ที่ติดมา) vs delta residual — ต่อยอดกล่อง delta hedge 18.6 + vega-equivalent sizing 22.7 ให้เป็นระบบบัญชีเต็ม
- Situation Cards ทุกตัว: IV เบี่ยงตาม event cycle ชัดกว่า price pairs → ความถี่คาดการณ์ได้มากกว่า แต่ friction สูงกว่ามาก (โยง 22.6)

### Phase 4 — Calendar Arb ภาคปฏิบัติ: ทำไมขาดทุนทั้งที่ "ทำถูกสูตร" (ยกเครื่อง ch17 + บทใหม่ ch10b)

> Phase นี้เกิดจากบทเรียนจริงของผู้ใช้ (§0.1) — สำคัญสุดในเชิงปฏิบัติ เพราะตอบคำถาม "ทำตามหนังสือแล้วทำไมยังเจ็บ"

**ยกเครื่อง `ch17` (Commodity Basis/Calendar) — เพิ่ม 5 หัวข้อ:**
1. **17.8 Full-Carry Markets: เกมต้นทุน ไม่ใช่เกมสัญญาณ** — ทำไม calendar ทองคำแทบไม่มี signal edge; ตาราง "ต้นทุน carry ของคุณ vs ของ bank/MM"; วิธีเช็คก่อนเข้าตลาดว่า market นี้ full-carry หรือมี structural deviation (เทียบ: ทอง=full carry · น้ำมัน=seasonal+storage constraint · ก๊าซ=พีคจัด → มี ε ให้เล่นจริง); บทสรุปที่ต้องกล้าพูด: **"ไม่มี order = ระบบทำงานถูก"**
2. **17.9 Carry-Adjusted ε** — ε_t = spread_t − fair_carry_t(r_curve) ทีละขั้น พร้อมตัวอย่างทองคำจริง; แยก component: rate move vs storage vs แท้จริง mispricing; เตือน: ไม่ hedge rate = เทรดดอกเบี้ยแฝง
3. **17.10 Cross-Exchange Same-Commodity (CME↔APEX/SHFE)** — location basis, delivery spec, θ ≠ 0, no-arb band = ต้นทุนขนจริง; ในแบนด์ไม่มี mean reversion บังคับ → ต้อง estimate θ, band จากข้อมูล ห้าม assume 0; เคส EFP gold blowout มี.ค. 2020
4. **17.11 Roll & Expiry Mechanics** — ทำไมห้ามถือใกล้ expiry (delivery dynamics, position limits, liquidity migration); โซนเวลาที่ spread "สะอาด" vs "สกปรก"
5. **17.12 Execution: Listed Spread Order เท่านั้น** — legging = จ่าย bid-ask 4 ครั้ง; คำนวณให้ดูว่า friction ของ legging กิน edge หมดยังไง; spread instrument บน CME (GC calendar) ใช้ยังไง

**บทใหม่ `ch10b` — Spread Data Engineering: TF, Executable Spread และ Chart ที่ไม่โกหก** (แทรกหลัง ch10 Z-score):
- **เลือก Timeframe จาก half-life ไม่ใช่จากความรู้สึก** — fit κ (OU, ch3) → TF สัญญาณ ≈ half-life/10–20; ตาราง: half-life ชั่วโมง→TF 5m · วัน→H4 · สัปดาห์→Daily
- **สถาปัตยกรรม 2 ชั้น**: ชั้นสัญญาณ (TF จาก half-life, gate ด้วย deviation > friction band + k·σ) + ชั้น execution (TF เล็ก หา timing หลัง gate เปิดเท่านั้น) → แก้ dilemma "TF เล็ก false เยอะ / TF ใหญ่พลาด spike" เชิงโครงสร้าง: TF เล็กไม่มีสิทธิ์สั่งเทรด
- **Spike ปลอมจาก data ไม่ sync** — spread จาก last-trade สองขาที่ print คนละเวลา (ขา illiquid ราคาค้าง) = spike ที่เทรดไม่ได้; ต้องสร้างจาก synchronized mid quotes
- **Executable Spread สองเส้น** — enter_long_spread = ask_A − bid_B, enter_short = bid_A − ask_B; สัญญาณจริง = เส้น executable ทะลุ band ไม่ใช่ mid ทะลุ
- **Line vs Candlestick: คำถามที่ใช่กว่า** — candle ของ spread ต้อง aggregate จาก spread series ที่ sync แล้วเท่านั้น (ห้าม high_A − low_B — คนละ timestamp); ถ้า data ยัง async candle จะโกหกสวยกว่า line; สิ่งที่ต้องมีจริงบน chart: mid spread + executable both sides + friction band + fair-carry line
- Situation Card + แบบฝึกหัด: ให้ dataset ที่มี spike ปลอม 3 จุด จริง 1 จุด → หาให้เจอว่าอันไหนเทรดได้

### Phase 5 — Generalize Pipeline + Retrofit + ปิดเล่ม
- **Generalize pipeline ch1–12 พ้น log price**: ทุกบทแกน (OU ch3, β ch4, cointegration ch5, stationarity ch6, GARCH ch7, z-score ch10, entry/exit ch11, sizing ch12) เพิ่มตัวอย่าง/โจทย์ที่ใช้ F(·) อื่นอย่างน้อย 1 จุดต่อบท (basis, absolute, funding, IV) + หมายเหตุ "สูตรนี้เปลี่ยนยังไงเมื่อ F เปลี่ยน" (เช่น z-score บน basis ใช้ σ เป็น $ ไม่ใช่ % · half-life ของ funding spread สั้นกว่า log pairs มาก)
- **Editorial rewrite กล่องสูตรตาม Formula Style Guide (§6)**: ~114 กล่อง เรียงตามความหนัก — ch4 (18 กล่อง) → ch22 (10) → ch5 (9) → ch3 (8) → ch9/ch15 (7) → ที่เหลือ 1–6 กล่อง/ไฟล์
- **กระจายจุดขาดทุนจาก `statarb-loss-catalog.md`** ลงบทตามตารางท้าย catalog (กลุ่ม E ลง ch4b/ch5/ch6/ch10 · กลุ่ม F ลง ch19/ch12 · กลุ่ม G ลง ch11/ch20)
- ใส่ **Situation Card ย้อนหลัง** ให้กลยุทธ์เดิมทุกบท: ch13 (basis), ch14 (cross-venue), ch17 (calendar), ch21 (CFD) — ให้ทั้งเล่มพูดภาษาเดียวกัน
- **ch0 (เริ่มต้นที่นี่)**: อัปเดต reading map ให้มีแถว "คุณสนใจ ε แบบไหน → อ่านบทไหน"
- **Appendix A (Formula Playbook)**: เพิ่มสูตรทุก ε ใหม่ + ตาราง decision tree ย่อ
- **Appendix B (Glossary)**: ศัพท์ใหม่ (dispersion, sticky strike/delta, funding spread, peg, term structure)
- **ch24 (Case Studies)**: เพิ่ม 2 เคส — depeg (UST/USDC มี.ค. 2023) และ vol event ที่ term structure กลับหัว
- Rebuild PDF ทั้งเล่ม + ตรวจแบบเดียวกับรอบก่อน (text-diff + heading check + visual spot-check)

---

## 4. สรุปขนาดงาน

| Phase | ชิ้นงาน | สถานะ | ประมาณหน้า PDF ใหม่ |
|---|---|---|---|
| 0 | ย้ายไฟล์ 27 ไฟล์ + `docs/vendor` (KaTeX/Sarabun) เข้า branch หลัก | ✅ commit `70911c1` | — |
| 0.5 | **Quick win**: `white-space:pre` × 27 ไฟล์ + ลบ newline เกิน 6 กล่อง | ✅ commit `70911c1` — ยืนยันด้วย screenshot กล่อง OLS ch4 | — (แก้ 114 กล่องสูตรทันที) |
| QA | ทีม 11 คน ตรวจความถูกต้องความรู้ + ภาพประกอบทุกไฟล์ → แก้ตาม issue list | ⏳ กำลังรัน | — |
| 1 | ch4b กรอบเลือก F(·) + **ch5 §5.0 Null Hypothesis 101** | ✅ เขียนแล้ว + ตรวจ render แล้ว | ~15–20 |
| 2 | ch13b (absolute/ratio) + ch13c (funding/yield) | ✅ เขียนแล้ว + ตรวจ render แล้ว | ~25–30 |
| 3 | Options stat arb: ขยาย ch18 + ch22 (4 หัวข้อใหม่) | รอ | ~25–30 |
| 4 | Calendar arb ภาคปฏิบัติ: ch17 ยกเครื่อง (17.8–17.13 รวม margin mechanics) + ch10b ใหม่ | ✅ เขียนแล้ว + ตรวจ render แล้ว | ~30–35 |
| 5 | Generalize ch1–12 + Kalman churn ลง ch15/ch19 + editorial rewrite สูตร ~114 กล่อง + กระจาย loss catalog + Situation Cards + rebuild PDF | รอ | ~25–30 |
| | **รวม** | | **~125–145 หน้า** (เล่มโต ~406 → ~540+) |

ลำดับ: **0 ✅ → 0.5 ✅ → QA ⏳ → (แก้ผล QA) → 1 → 4 → 2 → 3 → 5**
- Phase 1 ก่อนบทใหม่ทุกบท (ทุกบทอ้าง decision tree กลาง + null hypothesis เป็นรากของทุก test ที่ตามมา)
- **ดัน Phase 4 ขึ้นก่อน 2–3** เพราะตอบปัญหาที่ผู้ใช้เจ็บจริงอยู่ตอนนี้ (calendar arb ขาดทุน + TF + charting)
แต่ละ Phase = commit แยก + รีวิวก่อนไปต่อ (ตาม convention เดิมของ repo)

---

## 5. สถานะคำถามเปิด

**เคาะแล้ว (จากผู้ใช้ รอบ 2):**
- ✅ Options = เอา options มาทำ stat arb (เทรด ε บน vol/PCP/skew) — ch22 เป็นแกน ขยายเต็ม
- ✅ บทเดิม pipeline ต้อง generalize พ้น log price → Phase 5
- ✅ เพิ่มโจทย์ calendar arb ภาคปฏิบัติ (ทองคำ contango, CME↔APEX, TF, spread charting) → Phase 4 ใหม่ + ดันลำดับขึ้นก่อน

**ยังรอเคาะ:**
1. **Dispersion เอาลึกแค่ไหน?** — ต้องใช้ข้อมูล IV ของ alt ซึ่งบางตลาดไม่มี ถ้าข้อมูลไม่ถึงแนะนำสอนเป็น framework + ตัวอย่างจำลอง (ไม่ใช่ strategy พร้อมใช้)
2. **Stablecoin peg** — โฟกัส USDT/USDC บน spot exchange หรือรวม on-chain (Curve pool) ด้วย? แนะนำ: spot exchange ก่อน (สอดคล้อง scope Bybit/Lighter ของเล่ม)
3. **หมายเลขบท** — ใช้ ch4b/ch10b/ch13b/ch13c (แทรก ไม่ renumber) ตาม pattern `pm-part3a` เดิม — โอเคไหม?
4. **Equity index dispersion / bond futures** — อยู่นอก scope crypto+MT5 ของเล่ม เสนอ *ไม่รวม* รอบนี้ (กันเล่มบวม) — แต่ commodity futures (ทองคำ CME/APEX) เข้า scope แล้วผ่าน Phase 4

---

## 6. Formula Style Guide — มาตรฐานการเขียนสูตร (บังคับใช้ทุกกล่อง .fm ต่อจากนี้)

ที่มา: ผู้ใช้รายงาน "สูตรอ่านยากมาก เรียงไม่เป็นประโยค" — นอกจาก CSS fix (Phase 0.5) แล้ว ต้องมีมาตรฐาน*การเขียน*ให้สูตรอ่านเป็นประโยคได้จริง จากทีมบรรณาธิการ:

1. หนึ่งสมการต่อหนึ่งบรรทัด — ห้ามมีเครื่องหมาย = ของสองสมการต่างเรื่องอยู่บรรทัดเดียวกัน; ขั้น derivation ที่ต่อจากบรรทัดบนให้ขึ้นบรรทัดใหม่นำด้วย → หรือ = เยื้องให้ตรงคอลัมน์กัน
2. ทุกกล่อง .fm ต้องมีบรรทัด 🚶 'อ่านเป็นภาษาคนก่อน' เป็น <p> เหนือกล่อง (ตาม v4 §4.7): หนึ่งประโยคไทยธรรมดา บอกว่าสูตรกำลังพูดอะไร ใช้สัญลักษณ์คณิตศาสตร์ได้ไม่เกิน 1 ตัวในประโยคนั้น
3. นิยามตัวแปรก่อนใช้เสมอ: สัญลักษณ์ที่โผล่ครั้งแรกในบทต้องมี bullet list (ul ปกติ นอกกล่อง .fm) รูปแบบ 'สัญลักษณ์ — ความหมายภาษาคน' ก่อนกล่องสูตรแรกที่ใช้มัน ห้ามนิยามตัวแปรผ่าน ← ในกล่อง
4. Σ พร้อม limits เขียน inline บนบรรทัดเดียวกันเสมอ: Σ(t=1..N) — ห้ามวาง t=1 เป็นบรรทัดที่สองใต้ Σ ด้วย space alignment (เปราะต่อการแก้ไขและ font metrics); ถ้า limits ชัดจากบริบทให้เขียนแค่ Σ แล้วระบุช่วงใน bullet นิยาม
5. ความยาวสูตรสูงสุด 60 ตัวอักษรต่อบรรทัด (รวม annotation) — เกินให้หักบรรทัดที่เครื่องหมาย = + − โดยขึ้นบรรทัดใหม่ด้วย operator นำหน้า; ยกเว้น code block ที่เกิน 60 ได้แต่ต้องไม่เกิน 90 (ยอม scroll บนมือถือ)
6. Thai prose ห้ามอยู่ใน .fm monospace — คำอธิบายภาษาไทยยาวกว่า 30 ตัวอักษรต้องออกไปเป็น <p> ก่อน/หลังกล่อง; ใน .fm อนุญาตไทยเฉพาะ annotation สั้นหลัง ← เท่านั้น
7. ลูกศร ← ใช้ annotate 'บรรทัดนี้คืออะไร/มาจากขั้นไหน' เท่านั้น สูงสุด 1 อันต่อบรรทัด ยาวไม่เกิน 30 ตัวอักษร และจัด ← ให้อยู่คอลัมน์เดียวกันทั้งกล่อง (นี่คือเหตุผลที่ CSS ต้องเป็น white-space:pre)
8. หนึ่งกล่อง = หนึ่งความคิด: .fm ไม่เกิน 8 บรรทัดสูตร (ไม่นับบรรทัดว่าง) — derivation ยาวให้หั่นเป็นหลายกล่อง คั่นด้วย <p> อธิบายว่า 'ทำไมขั้นต่อไปถึงทำแบบนั้น' เพื่อให้อ่านเป็นประโยคต่อเนื่อง
9. บรรทัดว่างในกล่องใช้คั่น 'กลุ่มตรรกะ' (นิยาม / objective / ผลลัพธ์) ครั้งละ 1 บรรทัดเท่านั้น ห้ามว่างติดกัน 2 บรรทัด และห้ามมี newline ทันทีหลัง <div class="fm"> หรือก่อน </div>
10. สูตรผลลัพธ์ที่ต้องจำ (เช่น β̂ = Cov(x,y)/Var(x)) แยกกล่องของตัวเอง บรรทัดเดียว พร้อม annotation ← 'สูตรที่ต้องจำ' — ไม่ฝังไว้กลาง derivation
11. Unicode ที่บังคับใช้: ใช้ · แทน * เสมอ, x² แทน x^2 เมื่อ exponent เป็นเลขหลักเดียว (², ³, √ มีใน Courier New), exponent ซับซ้อนใช้ ^( ), ค่าเฉลี่ยใช้ x̄ ȳ, ตัวประมาณใส่หมวก β̂ α̂, ห้ามใช้ subscript Unicode แบบ ₜ₌₁ (font fallback ไม่เสถียร) — ตัวห้อยเขียน _t ตามที่เล่มใช้อยู่แล้ว
12. ปิดท้ายทุก derivation สำคัญด้วย <p> 'แปลกลับเป็นคำพูด' ที่เชื่อมสูตรกลับสู่ความหมายเชิงเทรด (เช่น β̂ = 'B ขยับ 1% แล้ว A โดยเฉลี่ยขยับกี่ %') — สูตรที่แปลกลับไม่ได้คือสูตรที่ยังไม่ควรอยู่ในเล่ม

### เทมเพลตตัวอย่าง — กล่อง OLS จาก ch4 (จุดที่ผู้ใช้ถ่ายรูปมา) เขียนใหม่ตามกฎ

```html
<!-- ═══ BEFORE (ch4 บรรทัด 193–211 — render แล้วยุบเป็นบรรทัดเดียว, t=1 ลอยหลุด) ═══
<p>เขียนปัญหาเป็นสมการ:</p>
<div class="fm">ให้ y_t = log(P_A,t)   และ   x_t = log(P_B,t)

ε_t = y_t − α − β·x_t          ← residual คือสิ่งที่เราสร้าง

objective: minimize  S(α, β) = Σ ε_t² = Σ (y_t − α − β·x_t)²
                              t=1        t=1</div>

<p>หา minimum โดยหา partial derivative เทียบเท่า 0:</p>
<div class="fm">∂S/∂α = −2·Σ(y_t − α − β·x_t) = 0   →   Σy_t = N·α + β·Σx_t
∂S/∂β = −2·Σ x_t·(y_t − α − β·x_t) = 0 →   Σx_t·y_t = α·Σx_t + β·Σx_t²

แก้ระบบสมการ (Normal Equations):

  β = [N·Σ(x_t·y_t) − Σx_t·Σy_t] / [N·Σx_t² − (Σx_t)²]
    = Cov(x, y) / Var(x)                ← รูปกระทัดรัด (x = log P_B)

  α = ȳ − β·x̄                          ← α เป็นตัวปรับระดับ</div>
═══ END BEFORE ═══ -->

<!-- ═══ AFTER — ตามกฎ: 🚶 ก่อนสูตร / นิยาม bullet ก่อนใช้ / 1 สมการ 1 บรรทัด / Σ(t=1..N) inline / ไทยยาวออกนอกกล่อง / ← ≤30 ตัวอักษรคอลัมน์ตรง / กล่องผลลัพธ์แยก / ปิดด้วยแปลกลับเป็นคำพูด ═══ -->

<p>🚶 <em>อ่านเป็นภาษาคนก่อน: เรากำลังเลือกเส้นตรงหนึ่งเส้น ที่ทำให้ "ส่วนที่ A ขยับเกินกว่าที่ B อธิบายได้" แกว่งรอบศูนย์แคบที่สุด</em></p>

<p><strong>ตัวแปรที่ใช้ในกล่องนี้:</strong></p>
<ul>
<li><code>y_t</code> — log ราคาขา A ที่แท่ง t: y_t = log(P_A,t)</li>
<li><code>x_t</code> — log ราคาขา B ที่แท่ง t: x_t = log(P_B,t)</li>
<li><code>α, β</code> — สองค่าคงที่ที่เราต้องหา: ระดับของเส้น และ hedge ratio</li>
<li><code>ε_t</code> — residual: ส่วนของ y_t ที่เส้นอธิบายไม่ได้ — นี่คือของที่เราเทรด</li>
<li><code>N</code> — จำนวนแท่งข้อมูลทั้งหมด (t = 1..N)</li>
</ul>

<p>เขียนปัญหาเป็นสมการ — สมการละบรรทัด:</p>

<div class="fm">ε_t = y_t − α − β·x_t                  ← นิยาม residual

minimize S(α,β) = Σ(t=1..N) ε_t²       ← S เล็ก = ε แกว่งแคบ</div>

<p>S เป็นผิวโค้งรูปชาม (convex) จุดต่ำสุดคือจุดเดียวที่ความชันเป็นศูนย์ทั้งสองทิศ — จึงตั้ง partial derivative เทียบ α และเทียบ β ให้เท่ากับ 0 ทีละตัว:</p>

<div class="fm">∂S/∂α = 0:  −2·Σ(y_t − α − β·x_t) = 0
            → Σy_t = N·α + β·Σx_t      ← normal eq. ข้อ 1

∂S/∂β = 0:  −2·Σ x_t·(y_t − α − β·x_t) = 0
            → Σ(x_t·y_t) = α·Σx_t + β·Σx_t²
                                       ← normal eq. ข้อ 2</div>

<p>ได้สองสมการ สองตัวไม่ทราบค่า (α, β) — แก้ระบบตรงๆ แล้วจัดรูปด้วยนิยามของ Cov และ Var ได้คำตอบปิดรูป:</p>

<div class="fm">β̂ = Cov(x, y) / Var(x)                ← สูตรที่ต้องจำ

α̂ = ȳ − β̂·x̄                           ← เส้นผ่านจุด (x̄, ȳ)</div>

<p><strong>แปลกลับเป็นคำพูด:</strong> β̂ ตอบคำถาม "B ขยับ 1% แล้ว A โดยเฉลี่ยขยับกี่ %" ส่วน α̂ แค่เลื่อนเส้นให้ผ่านจุดกึ่งกลางของข้อมูล — ตัวที่มีความหมายต่อการเทรดมีสองตัวคือ β̂ (hedge ratio ที่ใช้ size ขา B) และ ε_t (สัญญาณ mean reversion ที่เราเฝ้ารอ)</p>
```

กล่องนี้คือเทมเพลตอ้างอิงของ Phase 5 (editorial rewrite ~114 กล่อง เรียงตามความหนัก: ch4 → ch22 → ch5 → ch3 → ch9/ch15 → ที่เหลือ)
