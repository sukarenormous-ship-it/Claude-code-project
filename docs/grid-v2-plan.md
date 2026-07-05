# Grid Trading Mastery V2.0 — แผนปรับปรุงฉบับรวม

> รวม 2 แหล่ง: (1) **Blueprint for Team V2.0** (เอกสารพิมพ์เขียวจากทีม) + (2) **paper arXiv:2506.11921** "Dynamic Grid Trading Strategy: From Zero Expectation to Market Outperformance" (Chen, Chen & Jang, NTU 2025)
> สถานะ: แผนงาน — ยังไม่ใช่เนื้อหาเล่ม | อัปเดต: 2026-07-05

---

## 1. สรุปสิ่งที่แต่ละแหล่งให้

**Blueprint V2.0** ให้กรอบ *operational*: ยกระดับ Part 1B (Bidirectional) และ 1C (Grid Hedge) จาก concept เป็น manual ที่คำนวณได้จริง, เพิ่ม Part 1D ใหม่ (Asymmetric Hybrid Grid), ผูก regime เข้ากับ short/hedge permission, backtest 3 ชั้น, และ production runbook — จุดยืนหลักคือ **"short ไม่มีเพดานขาดทุนทางทฤษฎี จึงต้อง sizing จาก loss budget ไม่ใช่จากความอยาก short"**

**Paper DGT** ให้กรอบ *theoretical + empirical* ที่เล่มเดิมยังไม่มี:

| ผลลัพธ์จาก paper | ความหมายต่อหนังสือ |
|---|---|
| **Zero-EV Theorem**: grid แบบมีขอบเขต (terminate เมื่อหลุด zone) ภายใต้ random walk 50-50 มี expected value = 0 — และ**ติดลบทันทีเมื่อรวม fee** | นี่คือรากฐานทฤษฎีของประโยค "grid ไม่ใช่เวทมนตร์" — alpha ของ grid มาจาก mean-reversion (H < 0.5) *เท่านั้น* ไม่ใช่จากโครงสร้าง grid เอง ต้องเขียนให้ชัดใน Part 0 และ Part 4 |
| **Break-even arbitrage count = n²/8 − n/4**: grid ที่มี n ช่องต้องเก็บรอบ arbitrage ให้ได้เกินจำนวนนี้ก่อนราคาหลุดขอบ จึงจะคุ้มความเสียหายจากการเดินทางเดียว | เป็น design rule ใหม่สำหรับเลือก N: ประเมิน (รอบ/วัน × วันที่คาดว่าอยู่ใน zone) เทียบ n²/8 − n/4 ก่อนตั้ง grid — เล่มเดิมมีสูตร "รอบ/วัน ≈ ATR/Step" อยู่แล้ว แค่เชื่อมเข้าด้วยกัน |
| **DGT reset policy**: เมื่อราคาหลุดขอบ **อย่า terminate** — reset grid ใหม่โดยใช้ราคาปัจจุบันเป็นศูนย์กลาง: หลุดขอบบน → เก็บทุนคืน + reinvest กับ grid ใหม่; หลุดขอบล่าง → ถือ crypto ไว้ + ใช้กำไร arbitrage สะสมเป็น principal ของ grid ใหม่ | ตอบคำถาม Scope ข้อ 5 ของ blueprint ("ราคาออกนอก zone จะ reset/migrate/hedge/pause อย่างไร") ด้วยวิธีที่มี backtest รองรับ — เข้า Part 2 (migration) และ state `TREND_UP_MIGRATION` ของ Part 1D |
| **Geometric grid** (step เป็นสัดส่วน ×(1+k) ไม่ใช่บวกคงที่) | เล่มเดิมใช้ arithmetic grid ($2k คงที่) เกือบทั้งเล่ม — ควรเพิ่ม geometric เป็นทางเลือกใน Part 3 พร้อมเกณฑ์เลือก (zone กว้าง/ราคาเคลื่อนเป็น % → geometric เหมาะกว่า) |
| **Fee-vs-grid-size**: step เล็กเกิน → fee กินกำไร; step ใหญ่เกิน + levels เยอะเกิน → เปิดใช้งานน้อย ถือ crypto น้อย IRR แย่ | ยืนยัน rule of thumb "Step ≥ 2× fee" ของเล่มเดิมด้วยหลักฐาน backtest 2021–2024 (BTC/ETH, 1-min data, fee 0.08%) |
| **ผล backtest DGT**: IRR สูงถึง 60–70%, ชนะ B&H ทั้ง IRR และ MDD บน BTC; บน ETH ชนะ MDD ชัด (ตลาดลง ~80% DGT จำกัด DD ~50%) | ใช้เป็น evidence อ้างอิงได้ แต่**ต้องใส่ caveat**: ช่วงทดสอบ 2021–2024 เป็นช่วง bull-heavy ซึ่งเอื้อ spot grid เป็นพิเศษ (paper ยอมรับเอง) และ MDD 50% ไม่ใช่ "drawdown น้อย" |

**จุดที่สองแหล่งเสริมกันพอดี:** paper พิสูจน์ว่า "อย่าหยุด grid เมื่อหลุดขอบล่าง — ถือ inventory ต่อ" ในเชิง EV แต่ paper *ไม่มี* risk management เลย (ไม่มี SL, ไม่มี hedge, MDD ยังลึก) ส่วน blueprint ให้ชั้น risk ครบแต่ยังไม่มีทฤษฎีรองรับว่าทำไม reset ดีกว่า terminate → **V2.0 = DGT reset logic + risk stack ของ blueprint**

---

## 2. Audit ที่ยืนยันกับไฟล์จริงแล้ว (P0 — แก้ก่อน)

| # | ปัญหา | ตำแหน่งจริงในไฟล์ | การแก้ |
|---|---|---|---|
| A1 | claim "**ทุกสถานการณ์กำไร** — เพราะ hedge ป้องกัน directional risk สมบูรณ์" | `docs/grid-part1c.html` บรรทัด ~247 | เขียนใหม่เป็น conditional claim ตาม blueprint Table 15 + เพิ่ม P&L attribution เต็มรูป (grid + spot unrealized + perp unrealized + funding − fees − slippage − rebalance − margin cost) |
| A2 | **ADX config ไม่ตรงกัน**: Part 4 ใช้ BTC-calibrated 40/50 แต่ config.yaml ใน Part 9 เป็น `adx_caution: 25, adx_off: 35` | `docs/grid-part9.html` บรรทัด ~382–383 vs `docs/grid-part4.html` | แก้ Part 9 config เป็น 40/50 ให้ตรง Part 4 (ทิศทางตาม blueprint: ใช้ 40/50 ทั้งเล่ม) + ตรวจ cheat sheet ใน appendix |
| A3 | Hurst score code/comment mismatch + ตัวอย่าง Step Pyramid H=0.52 | ต้อง audit ใน `grid-part2.html`, `grid-part4.html` (grep แรกยังไม่เจอ H=0.52 ใน part2 — ต้องไล่ด้วยมือ) | Formula Audit sprint สัปดาห์ 1 |
| A4 | Bidirectional capital คิดแค่ margin (optimistic เกิน) | `docs/grid-part1b.html` | เพิ่ม Short Loss Buffer + Fee/Funding/Slippage Reserve ใน Total Capital |
| A5 | แผนภาพ Part 0 ข้าม level + "Drawdown น้อย" ไม่มีเงื่อนไข | `docs/grid-part0.html`, `docs/charts/grid-part0-basics.svg` | ✅ **แก้แล้วใน PR #11** — เหลือเพิ่มโยง Zero-EV theorem (ดู Phase 1) |

---

## 3. แผนงานเป็น Phase (ปรับจาก 8 สัปดาห์ของ blueprint + สอด paper เข้าไป)

### Phase 1 — Foundation & Claim Audit (blueprint สัปดาห์ 1 + paper §2)
- แก้ A1–A4 ทั้งหมด
- **Part 0 เพิ่ม section "ทำไม grid เปล่าๆ ไม่มี edge"**: Zero-EV theorem ฉบับอ่านง่าย (ไม่ต้องพิสูจน์ induction เต็ม — ยกผลลัพธ์ + intuition + อ้าง paper), ตาราง n²/8 − n/4 สำหรับ n = 4…20, และประโยคแกน: *"grid มีกำไรคาดหวังเป็นบวกก็ต่อเมื่อตลาด mean-revert จริง (H < 0.5) หรือคุณไม่ terminate เมื่อหลุดขอบ (DGT) — ไม่ใช่เพราะโครงสร้าง grid วิเศษ"*
- Assumption Box มาตรฐาน (template จาก blueprint Table 36) ติดทุกตัวอย่าง P&L — เริ่มจากตัวเลข "0.55%/วัน" ใน Part 0 ที่ต้องติดป้าย *mechanical illustration under assumptions*
- Deliverable: audit log ใน `docs/grid-appendix.html` (Formula Audit table ตาม blueprint Table 37)

### Phase 2 — Part 1B Bidirectional เป็น risk manual (blueprint สัปดาห์ 2)
- เพิ่ม 1B.10–1B.15 ตาม blueprint Table 7: Short Risk Budget (สูตร `Q_short_max = R_short / Σ(SL − Entry_j)` + ตัวอย่าง 44.6% จาก Table 10), Capital Stack, Stop Map (no-new-short ที่ zone top / soft stop +0.5 ATR / hard stop max(+1 ATR, ×1.05)), Funding break-even, Failure Mode Table, Order Lifecycle
- Design principle box: *"ห้ามเริ่มจาก 'อยาก short เท่าไหร่' — เริ่มจาก 'ยอมเสียจาก short side เท่าไหร่'"*

### Phase 3 — Part 1C Grid Hedge เขียน P&L ใหม่ (blueprint สัปดาห์ 3)
- Core rewrite: hedge ไม่ได้ลบ risk แต่**ย้าย** directional risk → execution/funding/basis/liquidation/rebalance risk
- เพิ่ม: Hedge Drift + rebalance triggers (Table 18), Funding Cost Ratio action rule (<25% ปกติ / 25–50% ลด / 50–100% เฉพาะ risk control / >100% pause), Basis risk, Liquidation Distance เกณฑ์ >25–30% conservative, Emergency Hedge Runbook (Table 21)

### Phase 4 — Part 1D ใหม่: Asymmetric Hybrid Grid + DGT Migration (blueprint สัปดาห์ 4 + paper §3)
- โครงตาม blueprint: Buy-only core 70–80% + Hedge reserve 15–25% + Capped short 0–10%, Ratio Policy ตาม regime (Table 24), 5 states (Table 25), Decision tree (Table 26)
- **เพิ่ม DGT-style migration เป็นกลไกของ state `TREND_UP_MIGRATION` และขาลงของ `BUY_ONLY_CORE`**:
  - หลุดขอบบน → เก็บทุน+กำไรคืน, ตั้ง grid ใหม่ center = ราคาปัจจุบัน (ตรง paper: "recover and reinvest")
  - หลุดขอบล่าง → ไม่ล้าง inventory (ตรง paper: ขายทิ้ง = ขัดหลัก buy-low), hedge ตาม Part 1C, ใช้ realized profit เป็น principal ของ grid ใหม่
  - ใส่ตารางเทียบ 3 ทางเลือกเมื่อหลุด zone: Terminate (EV=0, ไม่แนะนำ) / DGT reset (EV บวกใน backtest แต่ MDD ลึกถ้าไม่ hedge) / DGT reset + hedge (แนวทาง V2.0)
- Caveat box สำหรับผล paper: ช่วงทดสอบ bull-heavy, ETH MDD ยัง ~50%, ไม่มี risk layer — นี่คือเหตุผลที่ V2.0 ต้องประกบ DGT ด้วย risk stack

### Phase 5 — Regime + Risk Integration (blueprint สัปดาห์ 5)
- Short/Hedge Permission Matrix (Table 29) เข้า Part 4, Capital Stack ใหม่ (Table 30) เข้า Part 5, config.yaml v2 (Table 28)
- เชื่อม Zero-EV: regime detection คือกลไกที่ทำให้เรา "อยู่ใน zone ที่ EV บวก" — H < 0.5 = เงื่อนไขที่ทำให้ arbitrage count ทะลุ n²/8 − n/4 ได้จริง

### Phase 6 — Backtest & Evidence Pack (blueprint สัปดาห์ 6 + paper methodology)
- 3 fill layers (naive/conservative/event-like) — ผลหลักในเล่มใช้ conservative เท่านั้น
- 8 stress scenarios (Table 32)
- **Replicate DGT**: ใช้ methodology ของ paper (1-min data, geometric grid, fee 0.08%) เป็น baseline เทียบ Asymmetric Hybrid — ได้ทั้ง validation และ chart ประกอบ Part 1D (paper มี source code บน GitHub ให้เทียบ)

### Phase 7 — Part 9 Implementation (blueprint สัปดาห์ 7)
- โมดูลใหม่ตาม Table 33–34: `risk/` (short_risk, hedge_risk, liquidation, funding_monitor), `execution/` (order_manager, hedge_manager, position_reconciler, emergency_runbook), `backtest/` (3 fill engines + stress), `reports/` (pnl_attribution, assumption_box, audit_log)
- เพิ่ม `GridMigrator` class (ไม่อยู่ใน blueprint — มาจาก paper): `detect_boundary_break`, `recover_capital`, `recenter_grid`, `carry_inventory_down` — ผูกกับ state machine
- Production checklist (Table 35)

### Phase 8 — Editorial + Final QA (blueprint สัปดาห์ 8)
- Reader tools: strategy selector, capital/ratio calculators, checklists, answer key
- Red team: claim discipline ทุกบท, ตัวเลข running example generate จาก notebook เดียวกัน
- Definition of Done: ใช้ 14 ข้อของ blueprint §10.2 + เพิ่ม 3 ข้อ:
  - [ ] Part 0 มี Zero-EV theorem + break-even arbitrage table
  - [ ] Part 1D มี DGT migration rules ครบ 2 ทิศ (ขึ้น/ลง) พร้อม caveat box
  - [ ] Backtest replicate DGT baseline แล้วเทียบ Hybrid บน conservative fill

---

## 4. ลำดับที่แนะนำให้เริ่มทันที

1. **Phase 1 (A1, A2, A4)** — แก้ claim อันตรายและ config mismatch ก่อน เพราะกระทบผู้อ่านปัจจุบัน (A5 อยู่ใน PR #11 แล้ว)
2. **Phase 4 โครง Part 1D** — เป็นบทแกนของ V2.0 และปลดล็อกการเขียน Phase 2/3 ให้ชี้กลับมาที่ Hybrid ได้
3. Phase 2 → 3 → 5 → 6 → 7 → 8 ตามลำดับ

## 5. ความเสี่ยง/ข้อควรระวังของแผน

- **อย่านำเสนอ DGT เป็น "ทางแก้ Zero-EV" แบบไม่มีเงื่อนไข** — DGT ที่หลุดขอบล่างคือการแปลง grid เป็น B&H บางส่วน ซึ่งย้าย risk ไปที่ inventory ไม่ได้ลบทิ้ง (สอดคล้อง inventory-risk box ที่เพิ่งแก้ใน PR #11)
- ผล IRR 60–70% ของ paper ห้ามยกขึ้นปกหรือ headline — เป็นผลของ bull period; ใส่ได้เฉพาะใน context พร้อม assumption box
- Geometric grid ทำให้สูตร Close System capital ใน Part 1A เปลี่ยน (Σ ราคาเป็น geometric series) — ถ้าเพิ่มใน Part 3 ต้อง audit สูตรที่เกี่ยวข้องทุกจุด ไม่ให้เกิด mismatch แบบ ADX ซ้ำ
