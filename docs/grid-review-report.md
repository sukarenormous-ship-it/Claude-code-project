# รายงานตรวจสอบโดยทีมผู้เชี่ยวชาญ — Grid Trading Mastery

> คณะรีวิว 5 มุมมอง: บรรณาธิการโครงสร้าง · เทรดเดอร์ผู้ปฏิบัติ · Risk Manager · Quant ตรวจสูตร · Senior Bot Developer
> โจทย์จากเจ้าของหนังสือ: *"อ่านทั้งเล่มแล้วรู้สึกว่ายังไม่โดน มันยังเอาไปใช้จริงไม่ได้"*
> อัปเดต: 2026-07-05 | สถานะไฟล์ที่ตรวจ: branch `claude/grid-trading-book-review-dve69o` (หลัง PR #11 + Phase 1 fixes)

---

## คำตัดสินรวม

**ทั้ง 5 คนเห็นตรงกัน: ความรู้สึก "ไม่โดน" ของคุณถูกต้อง และวินิจฉัยได้เป็น 3 ชั้นที่ซ้อนกัน**

| ชั้น | อาการ | ผู้พบ |
|---|---|---|
| **1. ประสบการณ์อ่าน** | หนังสือเป็น "แคตตาล็อกเครื่องมือ" ไม่ใช่ "การฝึกงานกับเทรดเดอร์" — อ่านจบไม่รู้ว่าพรุ่งนี้เช้าต้องทำอะไรเป็นอย่างแรก | บรรณาธิการ |
| **2. ช่องว่างปฏิบัติการ** | Monday-morning test **ไม่ผ่าน**: มี $10,000 + หนังสือเล่มนี้ → เปิด grid จริงไม่ได้ ติดตาย 3 จุด | เทรดเดอร์ |
| **3. ความถูกต้อง** | เลขผิด/ขัดแย้งกันเอง ~40 จุด, WCL คำนวณไม่ได้จริงสัก variant, โค้ด Part 9 ไม่มีวันวาง order | Risk + Quant + Dev |

ข่าวดี: **คณิตศาสตร์แกนกลางของเล่มแน่นจริง** (quant ตรวจซ้ำแล้วส่วนใหญ่ถูกต้อง — ดูรายการ "ตรวจแล้วถูก" ท้ายรายงาน) ปัญหาไม่ใช่ต้องเขียนใหม่ทั้งเล่ม แต่ต้อง (ก) เปลี่ยนสถาปัตยกรรมการเล่าเรื่อง (ข) เติมสะพานสู่โลกจริง (ค) กวาดล้าง errata

---

## ชั้นที่ 1 — ทำไม "ไม่โดน" (บรรณาธิการโครงสร้าง)

1. **หนังสือผิดสัญญา golden thread** — Part 0 ประกาศ "Running Example: BTC/USDT บน Bybit ตลอดเล่ม" แต่แต่ละ part เป็นคนละบัญชี: $15k (Part 2) → $25k (Part 4) → $200k (Part 5) → $10k (Part 6B) → $20k (Part 7) ไม่มี "เทรดเดอร์คนเดิม" ให้ตามแม้แต่คู่ part เดียว
2. **ไม่มี capstone** — ไม่มีบท "หนึ่งเทรดเดอร์ หนึ่งบัญชี 30 วัน เห็นทุกการตัดสินใจ" เล่มจบที่ dashboard + แบบฝึกหัด = จบแบบ "เครื่องมือครบแล้วนะ" ไม่ใช่ "คุณเพิ่งเห็นมันทำงานจริงครบวงจร" → **สาเหตุอันดับ 1 ของ "ไม่โดน"**
3. **Choice overload ไม่มี default path** — 5 วิธีตั้ง zone, 3 bloating patterns, 4 execution styles, 3 snowball types, 5 supplementary strategies โดยแทบไม่เคยบอก "ถ้าไม่รู้จะเลือกอะไร ใช้อันนี้"
4. **ลำดับเล่มขัดกับลำดับใช้งาน** — ผู้อ่านเจอ Bidirectional/Hedge/Bloating ก่อนจะรู้วิธีตั้ง zone (Part 3), เมื่อไหร่ควรเปิด (Part 4), ใช้เงินเท่าไหร่ (Part 5) — ตลกร้าย: `grid-index.html` เองแนะนำเส้นทาง 0→1A→5→3→9 ซึ่งไม่ใช่ลำดับเล่ม
5. **ทุก part จบด้วยแบบฝึกหัดแล้วตัดจบ** — ไม่มี "ตอนนี้คุณทำอะไรได้แล้ว / การตัดสินใจถัดไปคืออะไร"
6. ความซ้ำเจือจาง: Step Pyramid ×2 (1A.8, 2.6), Composite Score ×2 (3B.6, 7B.5), GARCH ×2 (3.6, 7.5), funding ×3 (1B.4, 1C.3, 7.2) — 3B กับ 7B แทบเป็นบทเดียวกัน

**Spine ใหม่ที่เสนอ:** 0 → 1A → *3 → 4 → 5* (เลื่อนขึ้น: zone→regime→sizing) → 2 (bloating+migration) → **จบ core ใน 5 parts** → variants (1B/1C/1D) → 3B+7B (รวม) → 6B+7+6+8 (คัด) → 9 → **Part 10 Capstone (ใหม่)**

## ชั้นที่ 2 — Monday-Morning Test (เทรดเดอร์)

เดินตามเล่มด้วย $10,000 บน Bybit ได้ ~60% แล้วติดตาย:

1. **ขั้นวัด indicator** — เล่มสั่งใช้ Hurst/ATR/Donchian/ADX ก่อนเปิด grid แต่ไม่บอกว่ามือใหม่เอาค่ามาจากไหนโดยไม่เขียน Python (Hurst ไม่มีบน exchange/TradingView UI)
2. **ขั้น sizing (ติดตาย)** — Kelly ของ Part 5 ต้องการ p, b จาก **backtest 6 เดือนของ grid ที่ยังไม่ได้สร้าง** — chicken-and-egg ไม่มี cold-start default และขัดกับปรัชญา Close System ของ Part 1A โดยไม่มีกรรมการ
3. **ขั้นวาง order (ติดตาย)** — ทั้งเล่มไม่เคยบอกวิธี "วาง grid บน Bybit จริงๆ" — ไม่พูดถึง **Bybit native Grid Bot เลยสักบรรทัด** (ทางที่คนทุน $10k ใช้จริง) ส่วนทาง API โค้ดมี bug (ชั้นที่ 3)

**Decision gaps 20 จุด (G1–G20)** — จุดที่เล่มพูด "ปรับตาม... / พิจารณา..." โดยไม่ให้ default ที่สำคัญที่สุด:
- G14: Kelly cold-start (เสนอ: ไม่มีข้อมูล → grid capital = 10% ของ net worth จนมี 500+ cycles)
- G20/B18: **Zone Waterfall ขัดแย้งเชิงคณิตศาสตร์กับ Close System** — C_floor $8,460 ต้องใช้เงินทั้งก้อนถึง L5 แต่ waterfall สั่งกันเงิน Floor 20% "ห้ามแตะ" → ทุนรวมจริงต้องเป็น C_floor/0.8 = $10,575 (แบบฝึกหัดในเล่มก็ผิดแบบเดียวกัน)
- G9: Part 3 §3.9 บอก upper zone "ใส่ SELL รอ" — spot ขาย BTC ที่ยังไม่มีไม่ได้
- G18: กฎ fee ขัดกันเอง — Part 0 "Step ≥ 2× fee" vs Part 3 "กำไร/รอบ > 3× fee"
- ตัวเลขข้าม part ไม่ coherent: ATR $3,000→$2,500→$2,800, daily return 0.55%→0.27% (แล้ว Part 6B เอา 0.27% ไปทบ 5 ปี), ทุนกระโดด $4,700→$8,460→$200k→$10k
- (รายการเต็ม G1–G20 อยู่ในผลรีวิวฉบับ raw — จะยกเข้า backlog ตอนแก้)

**สิ่งที่ขาดระดับ P0:** บท "วาง grid บน Bybit จริง" (native bot mapping หรือ API), Day-0 Setup Checklist ฉบับเดียวเรียง 1→7 พร้อม default ทุกตัว, exchange microstructure (lot size, tick size, min notional, maker/taker, partial fill), ops routine รายวัน/สัปดาห์ + incident playbook ฝั่งมนุษย์

## ชั้นที่ 3ก — Risk Framework (Risk Manager)

**Verdict: Buy-Only = ใช้ได้หลังแก้ | Bidirectional / Grid Hedge / Part 8 = ยังใช้จริงไม่ได้**

- **WCL คำนวณไม่ได้จริงสัก variant:** Buy-Only ให้คำตอบขัดกัน 2 ค่า ($200 ที่ floor vs $4,700 ที่ BTC→0) โดยไม่มีสูตร L(P) เชื่อม; Hedge ไม่มีสูตร liquidation price ทั้งเล่ม — และตัวอย่างในเล่มเอง (1C.6 แถว pump +$20k) **โดน liquidate ก่อนถึงฉากจบโดยเล่มไม่รู้ตัว** (short 0.05 BTC margin $1,000 หมดพอดีที่ +$20k)
- **DD monitor ต่อสายเข้าเซ็นเซอร์ที่วัดผิดตัว:** live bot ใช้ `get_wallet_balance("USDT")` อย่างเดียว → ซื้อ BTC ปกติถูกนับเป็น DD ปลอม (HALT ปลอม) ส่วนขาดทุน BTC จริงมองไม่เห็น — backtest กลับใช้ mark-to-market → live กับ backtest วัดคนละอย่าง
- **ไม่มี kill switch ชั้นสาม** — มีแค่ −4% warning / −8% halt แล้วถือ inventory ไปเรื่อยๆ (framework กลางกำหนด −12% kill + 72h แต่เล่ม grid ไม่มี)
- **7 positions ที่มีอยู่ได้โดยไม่มี exit rule** เช่น inventory ใต้ floor, BTC ที่ถูก assign จาก CSP, USDT depeg grid (ซึ่ง step 0.05% < fee 0.2% = **ขาดทุนทุกรอบ** แต่เล่มเรียกว่า "ปลอดภัย")
- Hurst pause threshold มี **4 ค่า**ในเล่ม: 0.58 / 0.60 / 0.65 / 0.58 — ผู้อ่านไม่รู้จะหยุดที่ไหน

## ชั้นที่ 3ข — Errata จากการคำนวณซ้ำ (Quant)

ตรวจ 9 ไฟล์ พบ **30 จุด** (คำนวณผิด / code-comment mismatch / ขัดแย้งข้ามบท) จุดกระทบสูงสุด:

| ไฟล์ | ผิด | ถูก |
|---|---|---|
| part0 §0.2 (สูตรหลักที่คนจะจำ) | "0.01 × $490k = $4,900" | Σ(98..90) = $470k → **$4,700** (และ 0.55%/วัน → 0.57%) |
| part1a §1A.9 | worst case "~$1,500" | cost $8,460 − 0.091×$90k = **~$270** (ผิด 5.5 เท่า) |
| part1a §1A.7 stress | loss คิดจาก entry $100k = $437.6 | ต้องใช้ avg cost $92.7k → **~$358** |
| part6 §6.4 pair grid | "Net gain = $45 − $30 = $15/รอบ" | ขาทั้งสอง**บวกกัน**ตามนิยาม spread → **≈$45** (ขัดกับ §6.7 ของเล่มเองที่บวกถูก) |
| part4 (3 จุด) | diagram H 0.60, กล่องอ้าง 0.45/0.55, ตาราง ADX 25–40 | โค้ดจริงใช้ 0.50/**0.58** และ ADX **40/50** — unify |
| part7b §7B.3 | ADX 28/35 ใน adaptive sizing | **40/50** (ญาติ A2 ที่หลุดรอด) |
| part5 §5.3 | "0.019 ≈ 0.02 round down" + "Σ=$940k" | ปัด**ขึ้น**เกิน Kelly budget; $940k ทำซ้ำไม่ได้จากอนุกรมใดๆ |
| part2 §2.5/2.7 | bell allocation กับตาราง inventory | โค้ดจริงให้ [$924,$2,414,$3,325,...]; ตาราง implied ราคาซื้อ $70k ต่ำกว่า zone ต่ำสุด |
| appendix | Soft Martingale r^i, เงื่อนไข "DD < −threshold" (นิยาม DD บวก) | r^(i−1); เงื่อนไข**ไม่มีวัน trigger** — กลับเครื่องหมาย |
| part5 §5.2 | SE ของ p ใช้ n=270 trades | ข้อมูลเป็นรายเดือน n=3 → SE จริง **±22%** ไม่ใช่ ±2.3% (Kelly ทั้งบทดูแม่นเกินจริง 10 เท่า) |

หน่วยที่สม่ำเสมอ ✓: √365 สำหรับ crypto vol (ต่างจาก √252 ใน CLAUDE.md — ควรมีกล่องอธิบาย), funding ×3/วัน ✓

## ชั้นที่ 3ค — Implementation (Dev)

**Part 9 = ~35% ของ bot ที่รอด 1 สัปดาห์บน mainnet และ 35% นั้นคือส่วนที่ง่ายที่สุด**

- **Loop หลักไม่ปิดวงจร:** `GridWatchdog` emit ได้แค่ CANCEL/REDUCE/INCREASE/MIGRATE แต่ `main.py` รอ action `PLACE_ORDERS` ที่ไม่มีใคร emit → **bot จะไม่มีวันวาง order แม้แต่ใบเดียว** และ market data ถูกดึงครั้งเดียวก่อน `while True` แล้วแช่แข็งตลอดกาล
- **Bybit signing ผิดวิธี:** v5 POST ต้อง sign raw JSON body แต่โค้ด sign sorted query-string → ทุก order โดน reject (retCode 10004); ไม่มี orderLinkId → retry = order ซ้ำ (หมายเหตุ: `python-part6.html` ในหนังสือ python มีโค้ดที่ถูก — เล่ม grid ไม่ได้ใช้)
- **ของที่ named-but-never-shown:** `data_feed.py`, `alerts.py`, `compute_atr/donchian`, `compute_bb_width`, `DrawdownMonitor` class, `strategies/` ทั้ง 5 ไฟล์, ตัวเขียน `state.json` (dashboard อ่านไฟล์ที่ไม่มีใครเขียน)
- Part 4+7B+9 เรียกกันด้วยชื่อ method/signature ที่ไม่ตรงกัน (`compute_hurst` vs `hurst_exponent`, `create_orders` ที่ไม่มี, `base_step` vs `step`) — "เหมือนเขียนโดย 3 คนที่ไม่เคยรัน integration test ร่วมกัน"
- Fill detection บน live = 0% (sleep 1 ชม.), state persistence = 0%, alerts = 0%, `kelly_fraction` ใน config เป็น dead parameter, `max_notional_per_level` ไม่ถูก enforce, resume logic ไม่มีโค้ด
- Rate limit อ้าง "600 req/นาที" — จริงคือ 600 req/**5 วินาที** (IP) + per-UID per-endpoint

---

## สิ่งที่ grid-v2-plan.md ยังไม่ครอบคลุม (ต้องแก้แผน)

แผนเดิมเน้นความถูกต้องเชิงเทคนิคของ 1B/1C/1D — รีวิวรอบนี้พบว่า **ต้องเพิ่มอีก 4 กลุ่มงานและจัดลำดับใหม่**:

1. **Reader Experience Pack (ใหม่ทั้งกลุ่ม):** Part 10 Capstone "30 วันแรก", running example บัญชีเดียวตลอดเล่ม, part-ending bridges, Default Path boxes, spine reorder (และย้าย Part 1D ไปหลัง regime+sizing ไม่ใช่ก่อน)
2. **Exchange Reality Pack (ใหม่ทั้งกลุ่ม):** บท Bybit native Grid Bot mapping, Day-0 Runbook "$10,000 → grid แรกใน 1 ชั่วโมง" พร้อม cold-start defaults (ตอบ G14), microstructure, ops routine + incident playbook ฝั่งมนุษย์
3. **Errata Batch (ขยาย Phase 1):** ~40 จุดจาก Risk + Quant (B1–B19, #1–#30) รวม 3 ปมโครงสร้าง: Zone Waterfall vs Close System, WCL สองค่า, DD equity definition
4. **Part 9 Rescue (ขยาย Phase 7):** ปิดวงจร main loop, แก้ signing, DataFeed + state.json writer + fill events, equity = USDT + BTC×mark — แผนเดิมมี module ใหม่แต่ไม่ได้ audit ว่าโค้ดที่*มีอยู่*พังตรงไหน

## Top 5 สิ่งที่ควรทำก่อน (สังเคราะห์จากทั้ง 5 คน)

1. **Errata batch** — แก้เลขผิด ~40 จุด + unify thresholds (Hurst 0.58, ADX 40/50, fee 3×, DD ladder) — งาน mechanical เริ่มได้ทันที ป้องกันผู้อ่านปัจจุบันเสียหาย
2. **แก้ DD/equity pipeline + เพิ่ม kill switch −12%** — ระบบเบรกทั้งเล่มต่อสายเข้าเซ็นเซอร์ที่วัดผิดตัว ทุก risk rule พึ่งเลขนี้
3. **Day-0 Runbook + Exchange Reality** — ปลดล็อก Monday-morning test = แก้ "เอาไปใช้จริงไม่ได้" ตรงที่สุด
4. **Part 10 Capstone "30 วันแรก" + ผูก running example บัญชีเดียว** — แก้ "ไม่โดน" ตรงที่สุด (เขียนได้โดยไม่ต้องรื้อไฟล์เดิม)
5. **Part 9 Rescue** — ปิดวงจร loop + signing + state ก่อนเพิ่ม module ใหม่ตามแผนเดิม

## รายการที่ยืนยันว่า "ถูกต้อง" (coverage ของการตรวจ)

การตรวจซ้ำครอบคลุม: สูตรกำไร/รอบ, break-even table n²/8−n/4 ทั้ง 6 ค่า, Close System capital + ตาราง r-multiplier + stress table part1a ทุกเซลล์, Donchian/Keltner/ATR ทั้งชุด part3, state machine 2-of-3 vote ตาราง 21 วัน part4, Kelly f* ทุกตัวอย่าง part5, pair sizing + z-score ส่วนใหญ่ part6, IV-adaptive + funding + iron condor part7, composite scores part7b — **ผ่านทั้งหมด** ยกเว้นจุดที่รายงานข้างบน; การแก้ Phase 1 ก่อนหน้า (H=0.52→$2,933, hurst score, ADX config part9, Short Loss Buffer §1B.3) ยืนยันว่าถูกต้องแล้ว — แต่พบว่า **Running Example 1B.7 ยังคิดแบบ margin-only อยู่** (ต้องตามแก้ให้จบ)
