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
| **กฎเหล็ก** | ทุก ε ต้องมี **"สถานการณ์ที่ได้ใช้"** — trigger เกิดเมื่อไร ตลาดแบบไหน เจอบ่อยแค่ไหน ใครอยู่อีกฝั่ง ไม่ใช่แค่สูตร |
| **สไตล์** | คงรูปแบบเดิมของเล่ม: แก่นของบทนี้ → กลไก → สูตร → Running Example ตัวเลขจริง → กับดัก → แบบฝึกหัด |

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

### Phase 1 — บทกรอบใหม่: "ε Design — เลือก F(·) จากสถานการณ์" (`statarb-ch4b`)
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

### Phase 3 — ขยาย Options ให้เต็มตัว
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

### Phase 4 — Retrofit + ปิดเล่ม
- ใส่ **Situation Card ย้อนหลัง** ให้กลยุทธ์เดิมทุกบท: ch13 (basis), ch14 (cross-venue), ch17 (calendar), ch21 (CFD) — ให้ทั้งเล่มพูดภาษาเดียวกัน
- **ch17 เพิ่ม**: roll dynamics + delivery convergence (ช่องว่างเดียวของบทนั้น)
- **ch0 (เริ่มต้นที่นี่)**: อัปเดต reading map ให้มีแถว "คุณสนใจ ε แบบไหน → อ่านบทไหน"
- **Appendix A (Formula Playbook)**: เพิ่มสูตรทุก ε ใหม่ + ตาราง decision tree ย่อ
- **Appendix B (Glossary)**: ศัพท์ใหม่ (dispersion, sticky strike/delta, funding spread, peg, term structure)
- **ch24 (Case Studies)**: เพิ่ม 2 เคส — depeg (UST/USDC มี.ค. 2023) และ vol event ที่ term structure กลับหัว
- Rebuild PDF ทั้งเล่ม + ตรวจแบบเดียวกับรอบก่อน (text-diff + heading check + visual spot-check)

---

## 4. สรุปขนาดงาน

| Phase | ชิ้นงาน | ประมาณหน้า PDF ใหม่ |
|---|---|---|
| 0 | ย้ายไฟล์เข้า branch หลัก | — |
| 1 | ch4b กรอบเลือก F(·) | ~12–15 |
| 2 | ch13b (absolute/ratio) + ch13c (funding/yield) | ~25–30 |
| 3 | ขยาย ch18 + ch22 (4 หัวข้อใหม่) | ~25–30 |
| 4 | Situation Cards retrofit + ch17/ch0/appendix/ch24 + rebuild PDF | ~15–20 |
| | **รวม** | **~80–95 หน้า** (เล่มโต ~406 → ~490) |

ลำดับแนะนำ: **0 → 1 → 2 → 3 → 4** (Phase 1 ต้องมาก่อน 2–3 เพราะบทใหม่ทุกบทจะอ้าง decision tree กลาง)
แต่ละ Phase = commit แยก + รีวิวก่อนไปต่อ (ตาม convention เดิมของ repo)

---

## 5. คำถามเปิด (รอเคาะก่อนเริ่มเขียน)

1. **Dispersion เอาลึกแค่ไหน?** — ต้องใช้ข้อมูล IV ของ alt ซึ่งบางตลาดไม่มี ถ้าข้อมูลไม่ถึงแนะนำสอนเป็น framework + ตัวอย่างจำลอง (ไม่ใช่ strategy พร้อมใช้)
2. **Stablecoin peg** — โฟกัส USDT/USDC บน spot exchange หรือรวม on-chain (Curve pool) ด้วย? แนะนำ: spot exchange ก่อน (สอดคล้อง scope Bybit/Lighter ของเล่ม)
3. **หมายเลขบท** — ใช้ ch4b/ch13b/ch13c (แทรก ไม่ renumber) ตาม pattern `pm-part3a` เดิม — โอเคไหม?
4. **Equity index dispersion / bond futures** — อยู่นอก scope crypto+MT5 ของเล่ม เสนอ *ไม่รวม* รอบนี้ (กันเล่มบวม)
