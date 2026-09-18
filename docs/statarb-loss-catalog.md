# แคตตาล็อกจุดขาดทุน Stat Arb — จากคณะผู้เชี่ยวชาญ 4 ด้าน

> ผลการรีวิวโดยทีมผู้เชี่ยวชาญ 4 เลนส์ (โต๊ะ futures · execution/microstructure · econometrician · retail ตัวจริง)
> ที่อ่านเล่ม Stat Arb ทั้ง 27 ไฟล์ + แผนขยาย แล้วขุด "จุดขาดทุนที่ผู้ใช้ยังนึกไม่ถึง"
> **นอกเหนือจาก 6 ข้อแรก** ที่วินิจฉัยไว้แล้วใน `statarb-expansion-plan.md` §0.1
>
> ระดับความร้ายแรง: 🔴 เจ๊งพอร์ตได้ · 🟠 กัดเงียบสะสมนาน · 🟡 เสียโอกาส
> ทุกข้อระบุ: กลไก → ทำไมมองไม่เห็น → วิธีป้องกัน → บทที่ต้องไปเขียน


## A. สเปกสัญญา & ความหยาบของ Hedge — delta เปลือยที่มองไม่เห็น

### A1. 🔴 Hedge ratio ข้ามสเปกสัญญา: หน่วย oz vs กรัม + การปัดเศษ = delta ทองเปลือยที่ฝังอยู่ในทุก spread
*เลนส์: โต๊ะ futures*

**กลไกที่เงินหาย:** CME GC = 100 troy oz, quote USD/oz; APEX gold = สัญญาหน่วยกรัม quote USD/กรัม (1 troy oz = 31.1035 g) ขั้นตอนที่เงินหาย: (1) ต้องแปลงหน่วยราคาก่อนสร้าง ε — ถ้าเอา USD/oz ลบ USD/g ตรง ๆ หรือแปลงผิด จะได้ spread ที่ไม่มีความหมายหรือ position ผิดขนาดเป็นสิบเท่า (31×) = เจ๊งได้ในเทรดเดียว (2) ต่อให้แปลงถูก จำนวนสัญญาต้องปัดเป็นจำนวนเต็ม — ratio ที่ต้องการคือ 31.1035:1 แต่เทรดได้จริง 31:1 → เหลือทองเปลือย ~0.33% ของ notional; ที่ size retail (เช่น MGC 10oz = 311g เทียบ 3 สัญญา 100g = 300g) mismatch พุ่งเป็น ~3.5% ของขา → ด้วย vol ทองวันละ ~1% ค่า noise รายวันจาก delta ตกค้างมีขนาดเท่า ๆ กับ edge ของ spread เอง — สัญญาณจม noise, PnL แกว่งตามทิศทองทั้งที่คิดว่า market-neutral (3) tick size/tick value สองตลาดไม่เท่ากัน → executable spread ขยับเป็นขั้นบันไดคนละสเกล band ที่คำนวณจากทฤษฎีละเอียดกว่าที่ตลาดให้จริง

**ทำไมนึกไม่ถึง:** Retail เห็นคำว่า 'gold futures' ทั้งคู่เลยคิดว่าเป็นของเดียวกัน ต่างแค่ราคา — ไม่เคยเปิด contract spec sheet เทียบ หน่วย/ขนาด/tick เพราะบน crypto ทุก venue ใช้ BTC ตัวเดียวกันหน่วยเดียวกัน สัญชาตญาณจาก crypto จึงพาพลาด

**ป้องกัน/ตรวจจับ:** ก่อนจับคู่ข้าม exchange ต้องทำ 'spec sheet เทียบสองคอลัมน์' เสมอ: contract size (แปลงเป็นกรัมทั้งคู่), quote unit, tick size/value, currency, settlement type แล้วคำนวณ hedge ratio เป็นกรัม-ต่อ-กรัม พร้อมตาราง 'residual delta ต่อการปัดเศษ ณ size ของคุณ' — กฎ: ถ้า residual delta × σ_gold รายวัน > 20% ของ expected edge ต่อเทรด → size นั้นเล็กเกินกว่าจะเทรดคู่นี้ (หรือต้อง hedge เศษด้วย MGC/micro)

**ตัวเลขให้เห็นภาพ:** 1 GC = 3,110.35 g → ต้องใช้ 31.1035 สัญญา 100g; ปัดเป็น 31 → เปลือย 10.35 g (~0.33% notional); ที่คู่ MGC↔3×100g เปลือย ~3.5% → noise รายวัน ~$11 ต่อขา $33k เทียบ edge ต่อเทรดหลักไม่กี่ดอลลาร์

**สถานะในเล่ม:** ทั้งเล่มไม่มีคำว่า troy/ounce/กรัม/contract spec เลย (grep ยืนยัน) — ch17 พูด calendar บน underlying เดียวกันตลอด, ch14 cross-venue เป็น crypto ที่หน่วยตรงกันโดยธรรมชาติ; แผน 17.10 พูด delivery spec ในมุม no-arb band แต่ไม่พูดเลขคณิตของ hedge ratio/ปัดเศษ/tick

**→ ไปอยู่ที่:** 17.10 (Cross-Exchange Same-Commodity) — เพิ่มหัวข้อย่อย 'Spec Sheet & Hedge Ratio Arithmetic' พร้อม worked example GC↔APEX เป็นกรัม

### A2. 🟠 Lot size ขั้นต่ำทำให้ β จริงหยาบกว่า β ที่คำนวณ → มี directional exposure แฝงที่ใหญ่กว่า ε
*เลนส์: retail ตัวจริง* · *ญาติกับ A1 — มุมบัญชีเล็ก*

**กลไกที่เงินหาย:** ch4 ให้ β ทศนิยม 4 ตำแหน่ง แต่ตลาดให้ถือได้เป็น step: futures = จำนวนเต็มสัญญา, MT5 = 0.01 lot, exchange มี min qty/min notional ทุนเล็กเปิดได้ 1–3 หน่วยต่อขา → β จริงที่ implement ได้อาจห่างจาก β ที่ประมาณ 10–40% ส่วนต่างนี้คือ position ทิศทางเปล่า ๆ ฝังอยู่ใน 'arb': variance ของ residual exposure = (β_real − β_est)² × σ²_B ซึ่งบนคู่ volatile กลืน σ_ε ได้ทั้งตัว — PnL รายวันแกว่งตามตลาด ไม่ใช่ตาม ε แล้ว backtest (ที่ใช้ β ต่อเนื่อง) กับบัญชีจริงจึงหน้าตาคนละเรื่อง

**ทำไมนึกไม่ถึง:** ทุกสูตรในเล่มปฏิบัติกับ size เป็น continuous; ปัญหานี้หายไปเมื่อทุนใหญ่ (step เล็กเทียบ position) จึงไม่มีตำราไหนเขียน — แต่ retail อยู่ตรง regime ที่ rounding error ใหญ่สุดพอดี

**ป้องกัน/ตรวจจับ:** ก่อนเทรดคู่ไหน คำนวณ 'β granularity check': หา β_real ที่ใกล้สุดจาก lot step ณ ขนาดทุนจริง แล้วเช็ค residual vol = |β_real−β_est|×σ_B เทียบ σ_ε — ถ้าเกิน ~30% ของ σ_ε คู่นี้เล่นไม่ได้ที่ทุนนี้ (ไม่ใช่ปรับสูตร แต่ต้องเพิ่มทุนหรือเปลี่ยนคู่ที่ β≈1); แสดงว่าคู่ β ใกล้ 1 และ contract size ใกล้กันคือมิตรแท้ของบัญชีเล็ก

**ตัวเลขให้เห็นภาพ:** GC (100 oz) hedge กับ APEX gold (สมมติ 10 oz หรือสเปกต่าง): 1 GC ต้องการอีกฝั่ง 10 สัญญา — ทุนไม่ถึงก็ต้องถือ 1:8 หรือ 1:12 → off-hedge 20%; BTC/ETH ที่ β=0.0444 บน 0.01-lot step ยิ่งหยาบ

**สถานะในเล่ม:** ch4 ประมาณ β, ch12 ให้ size เป็น $ ต่อเนื่อง — ไม่มีขั้น 'แปลงเป็นจำนวนสัญญา/lot จริงแล้วเช็คความเสียหายจากการปัด' เลย

**→ ไปอยู่ที่:** แทรกใน ch12 (§12.x 'จาก $ เป็น lot: Rounding Risk') + เช็คลิสต์ใน ch4b decision framework

### A3. 🟠 Partial Fill กับ Hedge Granularity — เศษ delta ที่เสียงดังกว่า spread
*เลนส์: execution/microstructure* · *ญาติกับ A1 — มุมระหว่าง execution*

**กลไกที่เงินหาย:** ขั้นที่ 1: ch14 ปฏิบัติกับ fill เป็น binary (fill/ไม่ fill) แต่ limit order จริงคืน partial: ขา A ได้ 60% ขา B ได้ 100% → hedge ratio จริงเพี้ยนจาก β ทันที ขั้นที่ 2: บน futures ปัญหาถาวรกว่า: สัญญาเป็นจำนวนเต็มและ contract size สอง venue ไม่เท่ากัน (GC = 100oz vs lot ของ APEX) — β ที่คำนวณได้ 2.83 สัญญา ต้องปัดเป็น 3 → เศษ 0.17 สัญญาเป็น directional exposure ถาวรที่ 'ติดมากับ' ทุก spread ขั้นที่ 3: บน spread ที่ σ วันละไม่กี่ tick เศษ delta นี้มี P&L variance ใหญ่กว่าตัว spread หลายเท่า — equity curve จึงถูกขับด้วยราคาทอง ไม่ใช่ด้วย ε ทั้งที่หน้าจอบอกว่า 'market neutral' ขั้นที่ 4: ถ้าไม่มี reconciliation เศษจาก partial fill สะสมข้ามหลาย trade (position drift) จนวันหนึ่งพบว่าถือ outright ก้อนโตโดยไม่มีสัญญาณอะไรรองรับ

**ทำไมนึกไม่ถึง:** Backtest คิดเป็น notional ต่อเนื่อง (เช่น $100k พอดีทั้งสองขา) โลกจริงเป็นจำนวนเต็มสัญญา; retail เช็ค 'มี position ครบสองขาไหม' แต่ไม่เคยเช็ค 'ratio ของสองขาตรง β แค่ไหน' และไม่เคยคำนวณว่า variance ของเศษ delta เทียบกับ variance ของ ε แล้วอันไหนใหญ่กว่า

**ป้องกัน/ตรวจจับ:** ก่อนเลือกคู่ ให้คำนวณ residual delta ต่ำสุดที่เป็นไปได้จาก granularity ของสัญญา แล้วเทียบ: ถ้า σ(residual delta P&L) > 0.5×σ(spread P&L) คู่นั้นเทรดไม่ได้ที่ size ตั้งใจ — ต้องเพิ่มจำนวนสัญญาให้เศษเล็กลงโดยสัดส่วน หรือเปลี่ยนเครื่องมือ; handle partial fill เป็น state จริงใน state machine ch11 (ไม่ใช่แค่ SUCCESS/FAIL): fill เกิน x% → top-up ขาสั้น, ต่ำกว่า → unwind ส่วนเกิน; reconciliation ทุก 30s ของ ch14 ต้องเทียบ ratio ไม่ใช่แค่ existence

**ตัวเลขให้เห็นภาพ:** ต้องการ hedge 2.83:3 → เศษ 0.17 สัญญา GC = 17oz ≈ $40k+ notional; ทอง σ วันละ 1% → noise ~$400/วัน ขณะที่ edge ของ calendar spread ที่ไล่จับคือ 1–2 tick = $10–20/สัญญา — noise ใหญ่กว่า edge ~20 เท่า

**สถานะในเล่ม:** ch14 flowchart มีคำว่า 'partial adjust' ลอย ๆ หนึ่งคำ ไม่มีกลไก; ch19 พูด partial fill แค่ในฐานะเหตุผลที่ maker เสี่ยง; ทั้งเล่มไม่มีเรื่อง integer contract rounding / contract size mismatch เลย — ตัวอย่างเล่มเป็น crypto perp ที่หั่น size ละเอียดได้ พอผู้อ่านย้ายไป CME/APEX ตามเล่มขยาย Phase 4 จะชนกำแพงนี้ทันที

**→ ไปอยู่ที่:** ch14 (เพิ่มหัวข้อ partial fill state + ratio reconciliation) และ 17.12/17.13 (integer granularity บน futures); state ใหม่ใน ch11


## B. Margin & กระแสเงินสด — ตัวฆ่าอันดับหนึ่งของ spread ที่ "คิดถูก"

### B1. 🔴 Margin สองไซโล: ข้าม exchange ไม่มี SPAN spread credit — ขาขาดทุนโดน margin call ทั้งที่ขากำไรอยู่อีกโบรก
*เลนส์: โต๊ะ futures*

**กลไกที่เงินหาย:** Calendar spread ใน exchange เดียวกัน clearinghouse ให้ spread margin credit (SPAN) — margin ของ GC calendar เหลือหลักร้อยดอลลาร์ เทียบ outright หลักหมื่น (ลด 80–95%) แต่ cross-exchange CME↔APEX คือสองบัญชี สองโบรกเกอร์ สอง clearinghouse: (1) ต้องวาง margin เต็มแบบ outright ทั้งสองขา → เงินทุนจมมากกว่าเทรดเดียวกันใน exchange เดียว 5–20 เท่า → return on margin ต่ำจนไม่คุ้มตั้งแต่ต้น (2) ร้ายแรงกว่านั้น: เมื่อ spread ถ่างออกชั่วคราว (ปกติของ mean reversion) ขาขาดทุนโดนหัก variation margin เป็นเงินสดที่โบรก A ทุกวัน ส่วนกำไรขาตรงข้ามเป็นเงินสดที่โบรก B — โอนข้ามโบรก/ข้ามประเทศใช้เวลา 1–3 วัน (retail ไทยโอนเข้า US/SG นานกว่านั้น) → เงินสดที่ A หมดก่อน spread converge → โบรกบังคับปิดขา A ที่จุดถ่างสุด เหลือขา B เปลือย = แปลง 'divergence ชั่วคราว' เป็นขาดทุนจริงถาวร ตรงตำรา LTCM แต่ในสเกล retail

**ทำไมนึกไม่ถึง:** บน crypto ขาทั้งสองมักอยู่ใน exchange เดียว (perp+spot บน Bybit) หรือ cross-margin ในบัญชีเดียว — retail ไม่เคยเจอโลกที่ hedge สมบูรณ์แต่เงินสดอยู่คนละกระเป๋าและโอนไม่ทัน; ตอน backtest ไม่มีใครจำลอง cash flow รายวันของ variation margin แยกบัญชี

**ป้องกัน/ตรวจจับ:** กฎขนาด position จาก 'ทุนรับ divergence' ไม่ใช่จาก margin ขั้นต่ำ: ต้องมีเงินสดสำรองในแต่ละบัญชี ≥ margin เริ่มต้น + (k×σ_spread ถึง historical max divergence)×notional ของขานั้นแบบ standalone; ตั้ง alert ที่ 50% ของ buffer; ถ้าเทรด calendar ใน exchange เดียวได้ (GC listed calendar) ให้ทำแบบนั้น — spread credit คือเหตุผลเชิงโครงสร้างที่ MM ต้นทุนต่ำกว่าเรา; cross-exchange ต้องคิด cost of capital ของ margin สองก้อนเข้า fair value ด้วย

**ตัวเลขให้เห็นภาพ:** GC outright margin ~$10–13k/สัญญา vs GC calendar spread margin หลักร้อย; cross-exchange ต้องวางเต็มสองฝั่ง ~$15–20k+ ต่อคู่ — spread ถ่าง $5/oz = โดนเรียกเงินสด $500/GC ที่ฝั่งขาดทุนภายในคืนเดียว

**สถานะในเล่ม:** ทั้งเล่มไม่มี SPAN/cross-margin/variation margin เลย (grep ยืนยัน — คำว่า margin ที่เจอเป็น margin call เชิงทั่วไปใน ch13/21 และ capital lock-up หนึ่งบรรทัดใน ch16); ch19 นับ cost ครบทุกตัวยกเว้นต้นทุนและความเสี่ยงฝั่ง margin; แผนขยายไม่มีหัวข้อ margin เลย

**→ ไปอยู่ที่:** หัวข้อใหม่ 17.13 'Margin Mechanics: SPAN Credit vs สองไซโล' (Phase 4) + โยงเข้า ch12 (sizing) และ ch24 (LTCM = ตายด้วย cash flow ไม่ใช่ด้วย thesis ผิด)

### B2. 🔴 Variation Margin Asymmetry — spread converge แต่เงินสดหมดก่อน (ไม่มี margin offset ข้าม exchange)
*เลนส์: execution/microstructure* · *เรื่องเดียวกับ B1 — มุม execution*

**กลไกที่เงินหาย:** ขั้นที่ 1: calendar spread ภายใน CME ได้ spread margin credit (หลักร้อยดอลลาร์) แต่ cross-exchange CME↔APEX แต่ละ venue เห็นแค่ outright ขาเดียว → ต้องวาง initial margin เต็มสองฝั่ง ขั้นที่ 2: เมื่อ spread diverge (ก่อนจะ converge — ซึ่งเป็นเส้นทางปกติของ mean reversion trade) ขาขาดทุนโดน variation margin เรียกเป็น 'เงินสดจริงทุกวัน' ขณะที่กำไรฝั่งตรงข้ามเป็น unrealized อยู่อีก venue หนึ่ง — ถอน/โอนข้ามได้ช้าหลายชั่วโมงถึงข้ามวัน ติด cutoff, ติด weekend, ฝั่ง crypto venue ติด withdrawal processing ขั้นที่ 3: hedge สมบูรณ์แบบบนกระดาษจึงกลายเป็น liquidity mismatch จริง: ต้องมีเงินสดอิสระที่ venue ขาขาดทุน เท่ากับ path-maximum divergence ไม่ใช่เท่ากับ margin ณ วันเข้า ขั้นที่ 4: ถ้าเงินไม่พอ โบรกบังคับปิดขานั้น ณ จุด divergence สูงสุดพอดี → ขาดทุนฝั่งนั้นกลายเป็น realized + เหลือขาเดียว naked; spread ที่ converge ในอีกสามวันให้คนอื่นเก็บ — นี่คือกลไกที่ทำให้ 'คิดถูกแต่เจ๊ง' (บทเรียน Metallgesellschaft 1993 ขนาดย่อ)

**ทำไมนึกไม่ถึง:** Retail คิด risk เป็น 'ขาดทุนสุทธิของ spread' ซึ่งเล็ก เลย size ใหญ่ — ไม่เคยแยกว่า futures จ่าย loss เป็นเงินสดรายวันต่อขา ไม่ใช่ต่อ net position และไม่รู้ว่า margin offset เป็นสิทธิพิเศษภายใน clearinghouse เดียวกันเท่านั้น; ยิ่งไม่เคยคิดเรื่องความเร็วการโอนเงินระหว่าง venue เป็นส่วนหนึ่งของ risk model

**ป้องกัน/ตรวจจับ:** size จาก 'เงินสด ณ venue เดียว ต้องรับ k×σ ของ path divergence ได้' (ใช้ expected maximum ของ OU bridge ไม่ใช่แค่ระยะ entry→mean แบบ dd_limit ใน ch12); ตั้ง pre-funded buffer สองฝั่ง ≥ 3× initial margin ต่อขา; วัด transfer latency จริงระหว่าง venue แล้วถือเป็น parameter ของกลยุทธ์; กติกาเดียวจบ: ถ้า buffer ที่มีรองรับ divergence ได้ไม่ถึง 3σ อย่าเปิด — ไม่ใช่ลด size แต่คือไม่เปิด

**ตัวเลขให้เห็นภาพ:** GC 1 สัญญา: outright margin ~$10–12k vs calendar spread ภายใน CME ~$400–800; cross-exchange = จ่ายเต็มสองฝั่ง ~$20k+ ต่อ spread เดียว; ทองขยับ $50/oz วันเดียว = variation margin $5,000/สัญญา ต้องเป็นเงินสด ณ venue นั้นก่อนเช้าวันรุ่งขึ้น

**สถานะในเล่ม:** ch13/ch21 พูด margin call แบบขาเดียวโดน liquidate; ch12 dd_limit ประเมิน worst case แค่ระยะจาก entry_z กลับ θ (spread วิ่ง 'ออก' ไกลกว่า entry ได้ — LTCM ใน ch24 คือเคสนี้แต่เล่มไม่แปลงเป็นสูตร sizing); ทั้งเล่มไม่มีเรื่อง variation margin เป็น cash flow รายวัน, ไม่มี margin offset ข้าม venue, ไม่มี transfer latency; ch19 นับ funding cost แต่ไม่นับ 'ต้นทุนเงินสดจม 2 ฝั่ง'

**→ ไปอยู่ที่:** ch17 หัวข้อใหม่ 17.13 'Margin Mechanics ของ Cross-Exchange Spread' + retrofit สูตร sizing ใน ch12 (path-max divergence)

### B3. 🔴 Margin แยกกระเป๋า + กำไรอยู่ venue หนึ่ง ขาดทุนอยู่อีก venue: spread ยังดีอยู่แต่โดน liquidate ขาเดียว
*เลนส์: retail ตัวจริง* · *เรื่องเดียวกับ B1 — มุม retail*

**กลไกที่เงินหาย:** แต่ละ venue mark เฉพาะขาของตัวเอง: spread วิ่งสวน 2σ → ขา loss สะสม unrealized loss บน venue B จน margin ratio ชน stop-out ขณะที่กำไรฝั่ง venue A โอนมาช่วยไม่ทัน (crypto withdrawal 10–60 นาที + on-chain fee, MT5 broker ถอน 1–3 วันทำการ) → venue B บังคับปิดขา loss ตอน spread กว้างสุด เหลือขา A เป็น naked directional ตอนตลาดผันผวนสุด — สิ่งที่ 'ตลาด' ทำให้เราโดยไม่ต้องรอเราตัดสินใจผิดเอง จากนั้น spread revert กลับตามที่โมเดลทำนาย แต่เราไม่อยู่แล้ว

**ทำไมนึกไม่ถึง:** โมเดลคิดความเสี่ยงที่ระดับ ε (net exposure ต่ำ) แต่ liquidation engine ของแต่ละ venue เห็นแค่ขาโดด ๆ ที่ leverage สูง — 'ความเสี่ยงสุทธิต่ำ' ไม่มีอยู่จริงในสายตาของ risk engine ใด ๆ ที่เรากำลังใช้

**ป้องกัน/ตรวจจับ:** กฎ: leverage ต่อขา ≤ ที่ทนได้ถ้าขานั้นโดน adverse move = z_stop × σ_leg (ไม่ใช่ σ_ε!) โดยไม่ต้องเติมเงิน; ตั้ง rebalance protocol ล่วงหน้า (เงินสำรอง 30–50% นอกตลาดที่โอนได้ใน 1 ชั่วโมง, alert ที่ margin ratio 2 ขั้นก่อน stop-out); ซ้อม 'fire drill' โอนเงินข้าม venue จริงก่อนเปิด position แรก

**ตัวเลขให้เห็นภาพ:** ขาละ $10k leverage 10× บน Bybit: BTC ขยับสวน 5% = ใช้ margin ไปครึ่งหนึ่งของขานั้น ทั้งที่ ε ขยับแค่ 0.3%

**สถานะในเล่ม:** ch14 พูด leg risk เฉพาะตอน execution (เข้าไม่ครบสองขา); ch20 มี drawdown hierarchy แต่วัดที่ PnL รวม ไม่มีเรื่อง margin แยก venue / ความเร็วการโยกเงิน

**→ ไปอยู่ที่:** ขยาย ch20 (เพิ่ม §20.x 'Venue-Level Margin Risk') + โยงเข้า ch10b/ch17 ของ Phase 4

### B4. 🔴 Daily settlement mark คนละเวลา = variation margin ผี — โดนเรียกเงินสดทั้งที่ spread ไม่ขยับ
*เลนส์: โต๊ะ futures*

**กลไกที่เงินหาย:** Futures mark-to-market ทุกวันด้วย settlement price ของแต่ละ exchange — CME GC settle ~13:30 ET (ตี 1 ครึ่งเวลาไทย) ส่วน exchange เอเชีย settle ช่วงบ่ายเอเชีย ห่างกัน ~10+ ชั่วโมง ถ้าทองขยับ 1% ระหว่างสอง mark: ขาหนึ่งถูก mark ขาดทุน 1% ของ notional คืนนี้ → โดนหัก/เรียก variation margin เป็นเงินสดทันที ส่วนขากำไรจะถูก mark ชดเชยที่อีกตลาด 'คนละรอบเวลา' — เศรษฐศาสตร์ยัง hedge อยู่ครบ แต่กระแสเงินสดรายวันไม่ hedge เลย บัญชีที่เงินสดบางจะโดน margin call จากการเคลื่อนไหวที่ไม่ใช่ความเสี่ยงจริง แล้วถูกบังคับลด position ในจังหวะแย่สุด; บน MT5 CFD ก็มีเงาแบบเดียวกัน: swap/rollover ตัดคนละเวลากับ futures leg

**ทำไมนึกไม่ถึง:** Crypto perp mark แบบ real-time ต่อเนื่อง ไม่มี concept 'settlement รอบวันคนละเวลา'; retail ดู PnL รวมสองขาบนสเปรดชีตตัวเองแล้วเห็น flat จึงงงว่าทำไมโบรกเรียกเงิน — ไม่รู้ว่าโบรกแต่ละฝั่งเห็นแค่ขาของตัวเอง ณ mark ของตัวเอง

**ป้องกัน/ตรวจจับ:** จำลอง 'worst-case overnight cash call' ก่อนเข้า: notional ต่อขา × (σ ทองช่วงเวลาระหว่างสอง mark) × 2–3σ = เงินสดขั้นต่ำที่ต้องมีค้างในแต่ละบัญชี; อ่านเวลา settlement ของทั้งสองตลาดและรู้ว่าคืนไหน mark จะฉีก (event ระหว่างสอง mark); บันทึก PnL สองชุดแยกกัน: economic PnL (synchronized) vs margin PnL (ตาม mark ของโบรก) — ตัวหลังคือตัวที่ฆ่าคุณได้

**ตัวเลขให้เห็นภาพ:** ทองขยับ 1% ระหว่างสอง mark → cash call ~$3,300 ต่อ 1 GC ภายในคืนเดียว ทั้งที่ synchronized spread ขยับ 0

**สถานะในเล่ม:** ไม่มีเลยทั้งเล่ม — settlement ที่เจอใน ch13/ch9 คือ funding settlement ของ perp คนละเรื่อง; ch19 ไม่มี cost/risk มิติเวลา mark; แผนขยายไม่มี

**→ ไปอยู่ที่:** 17.13 (Margin Mechanics) ร่วมกับข้อ margin สองไซโล — เป็นเหตุผลว่าทำไม buffer ต้องคิดต่อบัญชีไม่ใช่ต่อพอร์ต

### B5. 🟡 ไม่มี margin offset ข้าม venue: ต้องวาง margin เต็มสองขา → ROC จริงเหลือครึ่งเดียวของ backtest
*เลนส์: retail ตัวจริง*

**กลไกที่เงินหาย:** spread margin credit มีเฉพาะเมื่อสองขาอยู่ใน clearing เดียวกัน (เช่น listed GC calendar บน CME margin ลดเหลือ ~10–20% ของ outright) แต่ CME↔APEX, Bybit↔Lighter, MT5 สองโบรกเกอร์ = คนละ clearing → วาง initial margin เต็มทั้งสองขา + ต้องกัน buffer เผื่อ mark-to-market วิ่งสวนแต่ละขาอีกขาละ 2–3 เท่าของ margin ผล: ทุนที่จมจริง ≈ 4–6 เท่าของที่ backtest คิด (backtest มักคิด return บน notional ขาเดียวหรือบน margin แบบ netted) กลยุทธ์ที่โชว์ 20%/ปี บนกระดาษ เหลือ 3–5% บนเงินสดจริง — ต่ำกว่าดอกเบี้ยไร้ความเสี่ยง

**ทำไมนึกไม่ถึง:** backtest ไม่มีคอลัมน์ margin — วัด PnL บน notional; retail รู้ตัวครั้งแรกตอนโอนเงินจริงแล้วพบว่าเปิด size ตามแผนไม่ได้ หรือเปิดได้แต่ leverage ต่อขาสูงเกินจนขาเดียวโดน liquidate ง่าย

**ป้องกัน/ตรวจจับ:** สอนสูตร ROC จริง = net edge ต่อรอบ × รอบ/ปี × notional / (IM_A + IM_B + buffer_A + buffer_B) พร้อมตารางเทียบ: same-clearing listed spread vs cross-venue; กติกาเลือกตลาด: ถ้า ε อยู่ข้าม clearing ต้องการ edge ต่อรอบอย่างน้อย 3–5 เท่าของ same-clearing ถึงคุ้มทุนที่จมเพิ่ม

**ตัวเลขให้เห็นภาพ:** GC listed calendar: margin ~$1,500/spread · CME↔APEX ขาเต็ม 2 ฝั่ง + buffer ≈ $25,000–35,000 สำหรับ exposure เท่ากัน — ทุนจมต่างกัน ~20 เท่า

**สถานะในเล่ม:** ทั้งเล่มไม่มีคำว่า margin offset/SPAN เลย; ch21 พูดถึง margin call แค่หนึ่งประโยคใน Model Risk box; ch12 คำนวณ size จาก capital ตรง ๆ เหมือน margin ไม่เคย binding

**→ ไปอยู่ที่:** ch19b (ส่วน capital efficiency) + retrofit กล่องเตือนใน ch14, ch17.12, ch21.7


## C. เวลา ปฏิทิน และนาฬิกาของตลาด

### C1. 🟠 Session hours ไม่ทับกัน: CME เปิด ~23 ชม. APEX เปิดเฉพาะช่วงเอเชีย — มีหน้าต่างเปลือยทุกวัน + mean reversion ปลอมใน backtest
*เลนส์: โต๊ะ futures*

**กลไกที่เงินหาย:** สามช่องทางเสียเงิน: (1) หน้าต่างเปลือยรายวัน — ช่วงที่ APEX ปิดแต่ CME ยังเทรด (ซึ่งครอบคลุมช่วง London/NY ที่ทองขยับแรงสุดและข่าว FOMC/NFP ลงพอดี) ปรับหรือปิด position ได้ขาเดียว → คืนไหนมี event คุณถือ delta ทองเปลือยหลายชั่วโมงโดยไม่มีทางเลือก (2) κ ปลอม — spread series ที่มีขาหนึ่งแช่แข็งข้ามคืน พอ APEX เปิดใหม่ราคาขา APEX กระโดดไล่ตาม CME ทันที → บนกราฟดูเหมือน spread 'ถ่างแล้วดึงกลับเร็ว' fit OU ได้ half-life สั้นสวยงาม แต่ความจริงคือขา stale reprice ไม่ใช่แรงดึงกลับที่เทรดกินได้ — backtest บอกมี edge, live ไม่มี order หรือเข้าแล้วไม่ converge (3) σ กับ band ที่ประมาณจากข้อมูลคร่อมช่วงปิดตลาดจะบวม → threshold ผิดทั้งระบบ

**ทำไมนึกไม่ถึง:** Crypto เปิด 24/7 ทั้งจักรวาล — retail ที่โตจาก crypto ไม่มี concept 'ตลาดปิด' อยู่ใน pipeline เลย; และ pitfall ข้อ 6 เดิม (last-trade ไม่ sync) แก้ที่ระดับ tick แต่ปัญหานี้อยู่ระดับโครงสร้าง: ต่อให้ sync สมบูรณ์ ช่วงที่ venue หนึ่งปิด spread ที่เห็นก็ไม่มีอยู่จริงในเชิง executable

**ป้องกัน/ตรวจจับ:** สร้าง ε เฉพาะจากช่วงเวลาที่ทั้งสองตลาดเปิดพร้อมกัน (overlap window) เท่านั้น — fit κ/σ/half-life จาก overlap-only series แล้วเทียบกับ full series: ถ้า half-life ต่างกันมาก แปลว่า 'reversion' ส่วนใหญ่คือ stale repricing; ห้ามถือ cross-session position คร่อมคืนที่มี event ปฏิทิน macro; วัด % ของเวลาที่ปิดขาได้ทั้งคู่ — ถ้า overlap สั้นกว่า half-life ของ ε คู่นี้เทรดไม่ได้เชิงโครงสร้าง

**ตัวเลขให้เห็นภาพ:** GC เทรด ~23 ชม./วัน; ถ้า venue เอเชียเปิด ~7–9 ชม. → overlap จริงอาจไม่ถึง 1/3 ของวัน และช่วง 19:30–21:00 น. ไทย (ข่าว US) มักเทรดได้ขาเดียว

**สถานะในเล่ม:** ทั้งเล่มไม่มีคำว่า session/ชั่วโมงเปิดตลาดเลย (grep ยืนยัน) — เล่มเกิดจาก crypto 24/7; ch10b ในแผนพูด sync ระดับ quote/timestamp แต่ยังไม่พูด market-closed regime และ κ bias จาก gap reversion

**→ ไปอยู่ที่:** ch10b (Spread Data Engineering) — เพิ่มหัวข้อ 'Overlap Window & Gap Reversion Illusion' + Situation Card ใน 17.10

### C2. 🔴 ปฏิทินสัญญาไม่ตรงกัน: FND/LTD คนละวัน + settlement benchmark คนละตัว — เทรด convergence ที่ไม่มีวันนัด converge
*เลนส์: โต๊ะ futures*

**กลไกที่เงินหาย:** GC เป็น physical delivery: First Notice Day อยู่ปลายเดือนก่อนเดือน delivery และโบรก retail ส่วนใหญ่มีนโยบายบังคับปิด position ก่อน FND หลายวัน 'ทีละขา ตามปฏิทินของขานั้น' — ส่วนสัญญาฝั่งเอเชียเป็น cash-settled หมดอายุคนละวัน และ settle กับ benchmark ราคาคนละตัว ผลคือ: (1) หน้าต่างเทรดจริงสั้นกว่าที่คิดมาก — thesis 'ถือรอ converge ถึง expiry' เป็นไปไม่ได้เพราะต้องออกก่อน FND ซึ่งมาก่อน LTD เกือบเดือน (2) ไม่มีวันที่สัญญาทั้งสองถูกบังคับให้เท่ากัน — ขาหนึ่งหยุดเทรด/ถูกโบรกปิดก่อนอีกขาหลายวัน terminal spread จึงเป็นผลต่างของ fix สองตัวคนละวันคนละนิยาม = ตัวเลขสุ่ม ไม่ใช่ศูนย์ (3) อันตรายสุด: โบรกบังคับปิดขา CME อัตโนมัติวันหนึ่ง (มักด้วย market order ช่วง liquidity บาง) โดยขา APEX ยังค้าง → เหลือ position เปลือยโดยไม่รู้ตัวจนเช็คพอร์ต; นอกจากนี้เดือนที่ liquid ของสองตลาดไม่ตรงกัน (GC liquid เฉพาะ Feb/Apr/Jun/Aug/Oct/Dec ฝั่งเอเชียมักรายเดือน) → คู่ที่เทรดได้จริงมี maturity ห่างกัน 1 เดือน = แอบมี calendar leg ฝังอยู่ที่มี carry drift ~0.4%/เดือน ณ rate 5% ที่คุณไม่ได้ตั้งใจถือ

**ทำไมนึกไม่ถึง:** Pitfall เดิมข้อ 5 เตือนแค่ 'อย่าถือใกล้ expiry' — แต่จุดนี้ลึกกว่า: retail คิดว่า 'สัญญาเดือนเดียวกัน' คือ instrument คู่แฝดที่มีเส้นชัยเดียวกัน ไม่เคยเปิดปฏิทิน FND ของโบรกตัวเอง และไม่รู้ว่า cash settlement อ้าง benchmark อะไร; นโยบาย auto-liquidation ของโบรกอยู่ในเอกสารที่ไม่มีใครอ่าน

**ป้องกัน/ตรวจจับ:** ก่อนเข้า ทำ timeline หนึ่งบรรทัดต่อคู่: วันนี้ → [วันโบรกเริ่มบังคับปิดขา A] → [FND A] → [LTD A] → [expiry B] → benchmark ที่ B settle; วันแรกสุดในรายการนั้นคือ 'วันหมดอายุจริงของ trade' — half-life ของ ε ต้องสั้นกว่าระยะถึงวันนั้นอย่างน้อย 2–3 เท่า; ถ้าสอง benchmark สุดท้ายไม่ใช่ราคาเดียวกัน ให้ประเมิน basis risk ของ fix-vs-fix เป็นความเสี่ยงคงค้างที่ไม่มีวันหาย; ถ้าเดือน liquid ไม่ตรง ให้คิด carry ของ maturity gap เข้า fair value (ต่อยอด 17.9)

**ตัวเลขให้เห็นภาพ:** GC: FND ≈ วันทำการสุดท้ายของเดือนก่อน delivery month, LTD ≈ วันทำการที่ 3 จากท้ายของ delivery month — หน้าต่าง 'สะอาด' จบก่อน expiry ~4–5 สัปดาห์; maturity gap 1 เดือน ณ rate 5.25% = carry ฝัง ~0.44% ที่ drift ทางเดียว

**สถานะในเล่ม:** ทั้งเล่มไม่มี First Notice/notice เลย (grep ยืนยัน); ch17 มีแค่ practitioner note 'roll 5 วันก่อน expiry' และ delivery squeeze หนึ่งประโยค; แผน 17.11 พูด position limits + liquidity migration แต่ยังไม่มี FND/นโยบายโบรกบังคับปิดทีละขา/benchmark mismatch/liquid month cycle ไม่ตรง

**→ ไปอยู่ที่:** 17.11 (Roll & Expiry Mechanics) — ขยายเป็น 'ปฏิทินคู่' + ตาราง FND/LTD/broker policy; ส่วน maturity gap carry โยง 17.9

### C3. 🟠 Settlement Mark ≠ ราคาที่เทรดได้ — spread รายวันจากสอง venue ที่ settle คนละเวลา คนละวิธี
*เลนส์: execution/microstructure*

**กลไกที่เงินหาย:** ขั้นที่ 1: สร้าง daily spread series ของ CME↔APEX จาก 'ราคาปิด/settlement' ของแต่ละตลาด — แต่ CME GC settle จาก VWAP window ~13:29–13:30 ET ส่วน APEX settle ตามเวลาเอเชีย ห่างกันหลายชั่วโมง ขั้นที่ 2: ε รายวันที่ได้จึงมีการเคลื่อนของราคาหลายชั่วโมงฝังอยู่ข้างใน — วันนี้ขาหนึ่ง 'ค้าง' พรุ่งนี้ 'วิ่งตาม' = สร้าง mean reversion ปลอมและ σ ปลอมใน daily data (เวอร์ชัน slow-motion ของปัญหา async ที่ระดับ intraday) β, θ, band ที่ fit จาก series นี้ผิดตั้งแต่ต้นทาง ขั้นที่ 3: ฝั่ง P&L จริง — โบรกไม่ mark position ด้วย spread ที่เราเทรดได้ แต่ mark ทีละขาด้วย settlement ของ venue ตัวเอง; เดือนไกล ๆ ที่ไม่มี trade จะถูก settle ด้วย committee/model ขั้นที่ 4: บางวัน settlement สองฝั่ง snapshot คนละสภาวะตลาด → margin เรียกเพิ่ม/equity แกว่งแรง ทั้งที่ executable spread แทบไม่ขยับ — ขาดทุนบนกระดาษที่บังคับพฤติกรรมจริง (โดน call, ตัดใจปิด)

**ทำไมนึกไม่ถึง:** Retail เห็นตัวเลข daily close ใน chart แล้วเชื่อว่ามันคือ 'ราคา ณ สิ้นวันเดียวกัน' ของทั้งสองตลาด — ไม่รู้ว่า settlement คือกระบวนการเฉพาะของแต่ละ exchange (เวลา, VWAP window, committee) และไม่เคยรู้ว่า statement ที่โบรกส่งมา mark คนละราคากับที่ตัวเองคิด จนกระทั่งโดน margin call วันที่ 'spread ไม่ได้ขยับ'

**ป้องกัน/ตรวจจับ:** วิเคราะห์ cross-exchange spread ด้วย snapshot เวลาเดียวกันที่ทั้งสองตลาดเปิดและ liquid พร้อมกัน (เช่น London PM / ช่วง overlap) ไม่ใช้ settlement ของใครเลยในการ fit; แยกบัญชีสองชั้นเสมอ: 'ε ตาม mark ของโบรก' (ตัวที่ตัดสิน margin) กับ 'ε executable' (ตัวที่ตัดสิน trade) — ต้อง monitor ทั้งคู่; ก่อนถือ position ข้ามวัน ให้จำลอง margin call จาก scenario ที่ settlement สองฝั่ง snapshot ห่างกันในวันที่ตลาดขยับ 2%

**ตัวเลขให้เห็นภาพ:** CME settle 13:30 ET, ตลาดเอเชีย settle ห่าง ~10 ชม.; วันที่ทองขยับ 1.5% ระหว่างสอง window → daily ε กระโดด ~$35–50/oz โดยที่ executable spread จริงขยับไม่ถึง $5

**สถานะในเล่ม:** คำว่า settlement ในเล่มมีแต่ funding settlement ของ perp (ch13); daily settlement ของ futures, VWAP window, การ mark เดือน illiquid ด้วย committee — ไม่มีเลย; ch10b ในแผนพูดถึง async ที่ระดับ tick/last-trade แต่ยังไม่ครอบ 'async ที่ระดับ daily settlement' ซึ่งเป็นตัวหลอก backtest รายวันของคน retail ที่ใช้ EOD data

**→ ไปอยู่ที่:** ch10b (เพิ่มหัวข้อ daily data: settlement ไม่ใช่ close ไม่ใช่ executable) + ch17.11 Roll & Expiry (ฝั่ง margin mark)

### C4. 🟠 Funding-Clock Artifact ใน Cross-Venue Perp ε — สัญญาณที่แท้จริงคือนาฬิกา funding สอง venue เดินไม่ตรงกัน
*เลนส์: execution/microstructure*

**กลไกที่เงินหาย:** ขั้นที่ 1: Bybit เก็บ funding เป็น snapshot ทุก 8 ชม. (00/08/16 UTC) ขณะที่ venue อย่าง Lighter ใช้รอบถี่กว่า/กลไกต่างกัน ขั้นที่ 2: รอบ ๆ เวลา snapshot ราคา perp ของแต่ละ venue จะถูกดึงเข้า/ออกจาก index อย่างเป็นระบบ (คน position เพื่อรับ/หนี funding แล้ว unwind หลัง snapshot) → ε ของ perp-perp จึงมีคลื่น intraday ที่ 'ผูกกับนาฬิกา funding' ไม่ใช่กับ mispricing ขั้นที่ 3: z-score ที่ fit โดยไม่รู้เรื่องนี้จะ trigger entry ตรงคลื่นพวกนี้ซ้ำ ๆ — และการเข้าก่อน snapshot ฝั่งผิดหมายถึง 'เก็บ spike แต่จ่าย funding ก้อนที่เป็นต้นเหตุของ spike นั้นเอง' ภายในไม่กี่นาที ขั้นที่ 4: ซ้ำด้วยบัญชี: สูตร funding cost ใน ch19 (rate × periods) assume rate คงที่และ pro-rata — ของจริงคือ snapshot แบบ all-or-nothing ณ วินาทีเดียว: ถือ 7ชม.59นาทีแล้วปิดก่อน snapshot = ฟรี, ถือเกิน 1 นาที = จ่ายเต็มก้อน → ต้นทุนจริงต่อ trade กระโดดเป็นขั้นบันได ไม่ใช่เส้นเรียบแบบใน backtest

**ทำไมนึกไม่ถึง:** Retail มอง funding เป็น 'ค่าเช่ารายวันเฉลี่ย ๆ' ตามสูตรในหนังสือ ไม่รู้ว่ามันเป็น discrete event ที่บิดรูปราคารอบ ๆ ตัวมัน และไม่เคยเอา timestamp ของ funding สอง venue มาทาบบน ε chart ดูว่า 'สัญญาณ' ของตัวเองกระจุกอยู่รอบเวลาไหน

**ป้องกัน/ตรวจจับ:** ทาบ funding timestamps ของทั้งสอง venue ลงบน ε chart แล้วดู histogram ของ entry signals ตามเวลาในวัน — ถ้ากระจุกรอบ snapshot = กำลังเทรดนาฬิกา ไม่ใช่ mispricing; deseasonalize ε ด้วย time-of-day mean ก่อน fit OU หรืออย่างน้อย blackout entry ±15 นาทีรอบ snapshot; entry gate ต้องคำนวณ 'expected funding ถึง snapshot ถัดไป' เป็นตัวเลขจริง ณ ขณะนั้น (predicted rate × เวลาที่เหลือ) ไม่ใช่ค่าเฉลี่ยประวัติศาสตร์

**ตัวเลขให้เห็นภาพ:** funding 0.01%/8h บน $100k = $10/ก้อน; ε spike รอบ snapshot ~5–8bps แล้ว revert ใน 20–40 นาที — ระบบที่เข้าก่อน snapshot เก็บ 6bps แต่จ่าย funding 10bps + fee = ขาดทุนสุทธิทุกครั้งที่ 'สัญญาณสวยที่สุดของวัน' โผล่

**สถานะในเล่ม:** ch13 เตือน 'อย่าถือข้ามรอบ funding' เฉพาะบริบท basis (perp↔spot); ch19 ให้สูตร funding แบบเส้นตรงคงที่; ไม่มีที่ไหนพูดถึง (ก) ε ของ perp-perp มี seasonality ตามนาฬิกา funding ที่ไม่ตรงกันสอง venue (ข) ธรรมชาติ all-or-nothing ของ snapshot ที่ทำให้ timing เข้าออกห่างกัน 1 นาทีต่างกันทั้งก้อน; แผน ch13c พูด normalize interval สำหรับ funding-spread ε แต่ยังไม่ครอบผลกระทบต่อ price-spread ε

**→ ไปอยู่ที่:** ch13c (funding mechanics ข้าม venue) + ch10b (deseasonalize ε / signal-time histogram) + แก้สูตร funding ใน ch19 เป็นแบบ snapshot-aware


## D. Execution จริง — ระหว่างสัญญาณกับ fill

### D1. 🟠 Adverse Selection ของ Maker Order — rebate คือค่าจ้างให้โดน pick off
*เลนส์: execution/microstructure*

**กลไกที่เงินหาย:** ขั้นที่ 1: ระบบเห็นว่า taker fee แพง (ch19 คำนวณเอง: taker −17bps vs maker rebate +7bps) จึงเปลี่ยนไปวาง limit order ทั้งสองขา ขั้นที่ 2: quote ของเราค้างอยู่ในหนังสือ — คนที่ยอม cross มากิน quote เราคือคนที่รู้ว่า spread กำลังวิ่งต่อ (informed flow / คนเห็น venue อื่นขยับก่อน) ขั้นที่ 3: ผลคือ fill แบบมีเงื่อนไข — เทรดที่ ε กลับตัวเองโดยไม่แตะ quote เรา = ไม่ได้ fill (พลาดรอบที่กำไร) ส่วนเทรดที่ fill = ε ทะลุผ่านราคาเราไปต่อ (ได้ของตอนที่มันแพงที่สุด) ขั้นที่ 4: backtest ที่ assume 'ราคาแตะ = fill ที่ราคา limit' จึงเก็บกำไรทั้งสองแบบ แต่ของจริงเก็บได้เฉพาะแบบที่แย่ → P&L จริงต่ำกว่า backtest อย่างเป็นระบบ ทั้งที่ fee model ถูกทุกบรรทัด

**ทำไมนึกไม่ถึง:** Retail มองค่า fee เป็นตัวเลขคงที่ในตาราง — เห็น maker rebate ก็คิดว่า 'ประหยัด 24bps ฟรี' ไม่เคยคิดว่า fill probability มี correlation กับทิศทางของ ε (fill ไม่ใช่เหตุการณ์สุ่ม แต่เป็นสัญญาณร้ายในตัวมันเอง) เพราะไม่เคยนั่งฝั่ง market maker มาก่อน

**ป้องกัน/ตรวจจับ:** วัด markout จริง: log ทุก maker fill แล้วดู ε ที่ +5s/+30s/+5min หลัง fill — ถ้า ε เฉลี่ยวิ่งสวนต่อหลัง fill นั่นคือต้นทุน adverse selection ที่ต้องหักจาก rebate; แยกวัด fill ratio ของ quote ตอน ε กำลัง revert vs กำลัง diverge; ใน backtest ห้ามใช้ touch-fill — ต้องให้ราคา 'เทรดทะลุ' limit อย่างน้อย 1 tick จึงนับ fill และคิด adverse markout เป็น cost อีกบรรทัดใน edge waterfall ของ ch19

**ตัวเลขให้เห็นภาพ:** rebate ประหยัด 24bps/round-trip แต่ถ้า markout เฉลี่ยหลัง fill = −0.5 tick/ขา (~4bps) × 2 ขา × entry+exit ≈ −16bps + เทรดกำไรที่ไม่ถูก fill หายไป ~30–50% ของสัญญาณ → net แย่กว่า taker ในหลาย regime

**สถานะในเล่ม:** ch19 แบบฝึกหัดข้อ 2 สอนตรง ๆ ว่า 'เปลี่ยนเป็น maker ประหยัด 24bps' โดยเตือนแค่ 'อาจไม่ถูก fill' — ไม่พูดเลยว่า fill ที่ได้มาเป็น fill ที่ biased; ch14.5 แนะนำ 'limit aggressive ใกล้ mid' ก็ไม่เตือน; คำว่า adverse selection / pick off ไม่ปรากฏที่ไหนในเล่มเลย (grep แล้ว 'adverse' มีแต่ในความหมาย adverse move)

**→ ไปอยู่ที่:** ขยาย ch19 (เพิ่มบรรทัด adverse selection ใน edge waterfall + แก้แบบฝึกหัดข้อ 2) และ ch14.5 (order types); โยงเข้า ch10b เรื่อง executable spread

### D2. 🟠 Queue Position กับ Implied Liquidity บน Listed Spread Book — วางถูกเครื่องมือแต่ยังไม่ได้ของ
*เลนส์: execution/microstructure*

**กลไกที่เงินหาย:** ขั้นที่ 1: แก้ปัญหา legging ด้วย listed calendar spread order (ตามที่วินิจฉัยไว้) แล้ววาง limit ที่ best bid ของ spread book ขั้นที่ 2: GC calendar spread เทรดกันในกรอบไม่กี่ tick — order ที่มาก่อนเราต่อคิวยาว และ CME ยังมี implied orders ที่ engine สร้างจาก outright book มาแทรกสภาพคล่อง ขั้นที่ 3: ระดับราคาที่เราต่อคิว จะ fill ถึงตัวเราก็ต่อเมื่อ flow ขายกดทะลุทั้งคิว = spread กำลังจะลงต่อ (adverse selection ซ้อนอีกชั้นบน instrument ที่ σ เล็กมาก) ส่วนรอบที่ spread เด้งกลับจากระดับนั้น คนหัวคิวได้ของ เราไม่ได้ ขั้นที่ 4: backtest บน spread series ที่นับ 'ราคาแตะระดับ = fill' จะโชว์ trade count และกำไรสูงกว่าความจริงหลายเท่า เพราะบน instrument ที่วันหนึ่งขยับ 2–3 tick การอยู่ท้ายคิวหมายถึงแทบไม่เคยได้ fill ฝั่งที่กำไร

**ทำไมนึกไม่ถึง:** Retail คิดว่า 'ใช้ spread instrument แล้วจบ' — ไม่รู้ว่าใน book ที่ tick แคบและ volume บางเบา ตำแหน่งคิวคือ edge ทั้งหมด และไม่รู้ด้วยซ้ำว่า implied liquidity ที่เห็นบนจอไม่ใช่คิวที่ตัวเองจะได้ต่อ; แพลตฟอร์ม retail ไม่แสดง queue position เลย

**ป้องกัน/ตรวจจับ:** ประเมิน expected queue ก่อนวาง: ดู size ที่ระดับนั้น ÷ volume ต่อวันของ spread — ถ้าคิวยาวกว่า volume ครึ่งวัน อย่านับว่าจะได้ fill; ใน backtest ของ spread instrument ให้นับ fill เฉพาะเมื่อราคาเทรด 'ทะลุ' ระดับ (trade-through) ไม่ใช่แค่แตะ; ถ้าจำเป็นต้องได้ของจริง ให้จ่าย taker 1 tick บน spread book (ยังถูกกว่า legging 4 ขามาก) แล้วคิด tick นั้นเป็น cost ตรง ๆ ใน ch19

**ตัวเลขให้เห็นภาพ:** GC calendar spread ขยับวันละ 2–3 tick (tick = $10/สัญญา); backtest touch-fill ให้ 40 trades/เดือน กำไรเฉลี่ย 1.5 tick — ของจริงท้ายคิวได้ fill ~15% ของสัญญาณ และเกือบทั้งหมดเป็นฝั่ง trade-through ที่ขาดทุนทันที 1 tick

**สถานะในเล่ม:** เล่มไม่มีคำว่า queue / pro-rata / implied ในบริบท matching เลย; แผนขยาย 17.12 เขียนแค่ 'ใช้ listed spread order เท่านั้น' — หยุดตรงประตูทางเข้า ไม่ได้สอนว่าเข้าไปแล้วต้องยืนตรงไหนของคิวถึงจะได้ของ

**→ ไปอยู่ที่:** ต่อท้าย 17.12 ใหม่ (Execution: Listed Spread Order) เป็น 17.12.2 'อ่าน spread book: คิว, implied, และเมื่อไรควรยอมจ่าย tick'

### D3. 🟠 Signal-to-Fill Decay — backtest fill ที่ bar close แต่ ε สลายตัวด้วย κ ระหว่างรอ
*เลนส์: execution/microstructure*

**กลไกที่เงินหาย:** ขั้นที่ 1: backtest คำนวณ z ที่ bar close แล้ว fill ที่ราคา close ของ bar เดียวกัน (หรือ mid ณ วินาทีนั้น) ขั้นที่ 2: ของจริง — กว่าสัญญาณจะประมวลเสร็จ ส่ง order สองขา รอ fill (ch14: 120–500ms ถ้าเร็ว, หลายวินาที-นาทีถ้า retail รัน bot บน VPS + rate limit) ε ไม่ได้รอเรา: มันเป็น OU ที่กำลังถูกสปริงดึงกลับด้วยอัตรา e^(−κΔt) ขั้นที่ 3: ยิ่ง half-life สั้น (ซึ่งคือคู่ที่ระบบชอบเลือก เพราะ Sharpe สวย) สัดส่วนของ deviation ที่หายไประหว่าง signal→fill ยิ่งใหญ่ — คู่ half-life 45 นาที ดีเลย์แค่ 5 นาทีก็กิน 7% ของ gap, ดีเลย์ 1 bar 15 นาทีกิน 21% ขั้นที่ 4: ซ้ำด้วย selection bias ของ bar close: การที่ z ทะลุ threshold 'ณ close' แปลว่าจุด extreme จริงเกิดกลางบาร์และผ่านไปแล้ว — backtest ได้เข้าที่จุดที่โลกจริงไม่มีวันได้ → edge ทั้งก้อนใน backtest อาจเป็นแค่ artifact ของการ fill ย้อนเวลา

**ทำไมนึกไม่ถึง:** Retail เข้าใจ lookahead bias ระดับ parameter (เล่มสอนใน ch3 walk-forward) แต่ไม่เคยคิดว่า 'fill ที่ราคา close ของ bar สัญญาณ' ก็คือ lookahead อีกชนิด เพราะทุก backtest framework สำเร็จรูปทำแบบนี้เป็น default; และไม่มีใครบอกว่า decay ระหว่างรอ scale ตาม κ — ตัวเดียวกับที่ทำให้กลยุทธ์น่าเทรด

**ป้องกัน/ตรวจจับ:** กฎเหล็ก: fill ได้เร็วสุดที่ open ของ bar ถัดไป (หรือ mid ณ t_signal + latency จริงที่วัดได้) แล้วเทียบ equity curve สองแบบ — ส่วนต่างคือ 'latency tax' ของกลยุทธ์; คำนวณ decay ratio = 1 − e^(−κ·delay) ใส่เป็น cost อีกบรรทัดใน ch19; ตั้ง gate: ถ้า latency รวม > 10–15% ของ half-life ให้ถือว่าคู่นั้นเทรดไม่ได้ด้วย infra ปัจจุบัน (เข้มกว่าเกณฑ์หลวม 2× holding time ที่ ch14 พูดผ่าน ๆ)

**ตัวเลขให้เห็นภาพ:** half-life 45 นาที (ตัวอย่างจริงใน ch11), entry z=2.0, gross 15bps: ดีเลย์ 1 bar 15m → เหลือ 15×e^(−0.693×15/45) = 11.9bps; หายไป 3.1bps ยังไม่รวมการข้าม spread — เทียบ net edge ในตาราง ch19 ที่ −4.6bps อยู่แล้ว = จมลึกลงอีก

**สถานะในเล่ม:** ch3 §3.9 กัน lookahead ของ parameter เท่านั้น; ch14 มีประโยคเดียว 'latency > 2× holding time = ซื้อสูงขายต่ำ' ซึ่งหลวมเกินไปและไม่มีสูตร; ไม่มีที่ไหนในเล่มพูดถึง fill-at-signal-bar-close bias หรือ decay e^(−κΔt) ระหว่าง signal→fill

**→ ไปอยู่ที่:** ch10b (สถาปัตยกรรม 2 ชั้น — เพิ่มหัวข้อ 'latency tax และการ fill ใน backtest') + หมายเหตุใน ch3 §3.9


## E. โมเดล/สถิติหลอก — backtest บอกมี edge แต่ไม่มี

### E1. 🔴 สแกนหลายคู่ = Multiple Testing — คู่ที่ผ่าน ADF อาจเป็นแค่ผู้ชนะโดยบังเอิญ + Winner's Curse ของพารามิเตอร์
*เลนส์: econometrician*

**กลไกที่เงินหาย:** (1) รัน ADF ที่ p<0.05 กับคู่ที่เป็น random walk ล้วน 100 คู่ → คาดว่าจะ 'ผ่าน' ~5 คู่โดยบังเอิญ — ตรงกับ funnel ในเล่มที่บอกว่า 'กรอง 100 → 3–5 คู่' พอดี นั่นคือผลลัพธ์ที่ noise ล้วนก็สร้างได้ (2) พอเทรดคู่ปลอมเหล่านี้ spread คือ random walk → เดินหนีไม่กลับ → ขาดทุนแบบ divergence (3) ซ้ำร้าย แม้คู่ที่ cointegrate จริง คู่ที่ 'ถูกเลือก' คือคู่ที่ sample ช่วงนั้นดูดีเกินความจริงของมันเอง (post-selection bias) → κ, σ, ความถี่สัญญาณใน backtest สูงกว่าที่จะเจอ live เสมอ — regression to the mean ของ performance

**ทำไมนึกไม่ถึง:** ซอฟต์แวร์แสดง p-value ทีละคู่ retail จึงตีความ p=0.03 ว่า 'มั่นใจ 97%' โดยไม่รู้ว่าความหมายของ p เปลี่ยนไปทันทีที่สแกนหลายสิบคู่แล้วเลือกตัวที่ดีสุด ตำรา econometrics สอน single-pair inference — ไม่มีใครบอกว่า screening loop คือการทำ hypothesis test ซ้ำหลายสิบครั้ง

**ป้องกัน/ตรวจจับ:** (1) รายงาน expected false positives = N_pairs × α ทุกครั้งที่สแกน (2) ใช้ Benjamini-Hochberg FDR หรืออย่างหยาบ Bonferroni (α/N) เป็น gate (3) คู่ที่ผ่านต้อง confirm บนข้อมูลช่วงใหม่ที่ไม่เคยใช้สแกน (fresh holdout ต่อคู่ — คนละเรื่องกับ walk-forward ภายในคู่) (4) บังคับ economic prior: ตอบให้ได้ว่าทำไมสองตัวนี้ควรผูกกันเชิงโครงสร้าง (venue เดียวกัน/underlying เดียวกัน/flow เดียวกัน) — คู่ที่มีแต่สถิติไม่มีเหตุผลเชิงกลไก ให้ discount หนัก (5) หลังเลือกคู่แล้ว shrink คาดการณ์: ใช้ half-life/σ จากช่วง confirm ไม่ใช่ช่วง scan

**ตัวเลขให้เห็นภาพ:** สแกน 200 คู่ random walk ที่ α=0.05 → คาด ~10 คู่ 'ผ่าน ADF'; BH-FDR ที่ q=10% บน 200 คู่ ตัดเหลือเฉพาะ p เล็กจริง เช่น ต้อง p<0.0025 สำหรับตัวอันดับ 5

**สถานะในเล่ม:** ch3 §3.10 พูด selection bias ของ 'window' ภายในคู่เดียว (สาเหตุที่ 2) แต่ไม่แตะการสแกนข้ามคู่ ch5 §5.8 มี funnel '100 → 3–5 คู่' และเตือน in-sample/OOS แต่ไม่มีการปรับ α ตามจำนวนคู่ ไม่มีคำว่า Bonferroni/FDR ทั้งเล่ม (grep ยืนยัน) และไม่มีแนวคิด winner's curse หลังการคัดเลือกเลย

**→ ไปอยู่ที่:** ch5 เพิ่ม §5.10 'Multiple Testing & Winner's Curse ใน Pair Scan' ต่อท้าย pipeline §5.8–5.9 (เข้า Phase 5 generalize ch1–12)

### E2. 🟠 Grid-search หา entry/exit z ที่ดีที่สุด = Multiple Testing บนพารามิเตอร์ — Sharpe ที่เห็นต้องถูก deflate
*เลนส์: econometrician*

**กลไกที่เงินหาย:** (1) ลอง entry z ∈ {1.5, 2, 2.5} × exit ∈ {0, 0.5, 1} × window ∈ {30, 60, 90} × TF 2 แบบ = 54 configs (2) ต่อให้กลยุทธ์ไม่มี edge เลย ค่า max ของ Sharpe จาก 54 การจับฉลากจะสูงตาม √(2·ln N) — บนข้อมูล 1 ปี best-of-54 โชว์ Sharpe 1.5–2 ได้จาก noise ล้วน (3) กับดักซ้อน: ทดสอบ config ที่เลือกบน OOS หนึ่งช่วง แล้วพอผลไม่ดีก็กลับไป 'ปรับนิดหน่อย' แล้วทดสอบ OOS เดิมซ้ำ — ทำไม่กี่รอบ OOS ช่วงนั้นก็กลายเป็น in-sample ของกระบวนการ (4) live จึงได้ Sharpe ใกล้ศูนย์ลบ friction — ขาดทุนแบบเรื้อรังโดยที่ backtest ทุกเวอร์ชันดูดี

**ทำไมนึกไม่ถึง:** Retail มองการจูน parameter เป็น 'engineering' ไม่ใช่ 'การทดสอบสมมติฐานซ้ำ' และไม่มีความรู้สึกว่า OOS ที่ถูก reuse หมดความศักดิ์สิทธิ์ — เครื่องมือ optimize ของ platform (MT5 optimizer!) ยิ่งสนับสนุนพฤติกรรมนี้โดยตรง

**ป้องกัน/ตรวจจับ:** (1) นับ N_configs ที่เคยลองทั้งหมด (รวมที่ลองแล้วทิ้ง) แล้วใช้ Deflated Sharpe Ratio / เทียบ max-of-N ของ noise เป็น benchmark ขั้นต่ำ (2) เลือกพารามิเตอร์ด้วย nested walk-forward (จูนใน train, ประเมินใน validation, รายงานผลจาก test ที่แตะครั้งเดียว) (3) กัน final holdout ไว้แตะได้ครั้งเดียวในชีวิตของกลยุทธ์ (4) ชอบพารามิเตอร์ที่มาจากทฤษฎี (เช่น entry จาก OU band §3.4 + friction §19) มากกว่าจาก search — ยิ่ง search space เล็ก ยิ่งเชื่อผลได้

**ตัวเลขให้เห็นภาพ:** 54 configs บน noise ล้วน ข้อมูล 252 วัน: E[max Sharpe] ≈ √(2·ln 54 / 1 ปี) ≈ 2.8 → เกณฑ์ 'Sharpe > 2' ที่คนใช้คัดกลยุทธ์ ผ่านได้สบายด้วยความว่างเปล่า

**สถานะในเล่ม:** ch7 มีกล่อง practitioner หนึ่งย่อหน้าบอกให้ 'maximize Sharpe บน test window แล้ว validate out-of-sample' — ซึ่งอ่านแล้วชวนทำ grid search โดยไม่รู้โทษของมันด้วยซ้ำ ทั้งเล่มไม่มีแนวคิด deflated Sharpe, ไม่มีการนับจำนวน trials, ไม่มีคำเตือนเรื่อง OOS reuse (ch3 §3.9 walk-forward ครอบคลุมเฉพาะ OU parameters ไม่ใช่ strategy hyperparameters)

**→ ไปอยู่ที่:** บทใหม่สั้นหรือหัวข้อใหญ่ 'Backtest Validation' — เหมาะแทรกเป็น ch3.11 หรือรวมใน Phase 5 (ยังไม่มีที่ไหนในแผนรองรับ — เป็นช่องว่างของแผนด้วย)

### E3. 🔴 Half-life ยาวกว่าอายุที่เหลือของสัญญา + backtest บน continuous contract ที่ต่อเชื่อม = เทรด ε ที่ไม่มีอยู่จริง
*เลนส์: econometrician*

**กลไกที่เงินหาย:** (1) fit OU บน spread ของ futures จาก continuous series ย้อนหลัง 2 ปี ได้ half-life 25 วัน (2) แต่ front contract จริงเหลืออายุ 18 วัน → โอกาสเห็น convergence ก่อนถูกบังคับออก/roll ต่ำมาก — trade นี้ 'ถูกสูตร' แต่เป็นไปไม่ได้เชิงเวลาตั้งแต่ก่อนเข้า (3) ตอน roll ต้องปิดที่ spread ณ ตอนนั้น (realize ขาดทุนถ้ายังไม่กลับ) แล้วเปิดคู่เดือนใหม่ที่เป็น 'อีก instrument' มี fair value ต่างกัน (4) ยิ่งกว่านั้น continuous series ที่ back-adjust/ต่อเชื่อมสร้าง jump ปลอมตรงรอย roll — mean reversion ที่ ADF เห็นบน series ต่อเชื่อม ส่วนหนึ่งคือ artifact ของการ splice ไม่ใช่แรงดึงที่เทรดได้บนสัญญาจริงตัวใดตัวหนึ่ง

**ทำไมนึกไม่ถึง:** Platform (TradingView/MT5) เสิร์ฟ continuous contract เป็น default — retail ไม่รู้ด้วยซ้ำว่า series ที่ fit OU ไม่ใช่ instrument ที่ตัวเองถือ และไม่มีเครื่องมือไหนเตือนว่า half-life ที่ประเมินได้ ยาวกว่านาฬิกาที่สัญญาเหลืออยู่

**ป้องกัน/ตรวจจับ:** (1) กติกาบังคับ: เทรด calendar/futures spread ได้เฉพาะเมื่อ time_to_forced_exit ≥ 3× half-life (นับถึงวันที่ต้องออกก่อน delivery dynamics ไม่ใช่วัน expiry) (2) fit OU บนข้อมูลของ contract pair จริงเป็นราย generation (Jun–Aug ปีก่อน ๆ) ไม่ใช่ continuous series (3) ถ้าจำเป็นต้องใช้ continuous ให้ตัด bar คร่อมวัน roll ทิ้งก่อน fit (4) ใน backtest ต้อง simulate การ roll พร้อม cost จริง ไม่ใช่ปล่อยให้ position ข้าม roll ราวกับเป็นตัวเดียวกัน

**ตัวเลขให้เห็นภาพ:** Half-life 25 วัน, เหลือเวลาเทรดจริง 18 วัน → คาดหวังเห็นการหดแค่ ~39% ของระยะทาง (1−0.5^(18/25)) ก่อนโดนบังคับ realize

**สถานะในเล่ม:** ch17 ทั้งบทไม่พูดถึง roll/expiry เลย (มีแค่หนึ่งบรรทัดใน 'ความเสี่ยง' §17.4) แผน 17.11 ครอบคลุม delivery dynamics และ liquidity migration (ตรงกับ pitfall ข้อ 5 ที่วินิจฉัยแล้ว) แต่ยังไม่มีทั้งสองประเด็นสถิติ: feasibility check ระหว่าง half-life กับอายุสัญญาที่เหลือ และ artifact จากการต่อเชื่อม continuous series ใน backtest

**→ ไปอยู่ที่:** Phase 4: เพิ่มเข้า ch17.11 (Roll & Expiry) หนึ่งหัวข้อย่อย 'นาฬิกาสัญญา vs นาฬิกา OU' + เข้า ch10b ส่วน data engineering เรื่อง splicing artifact

### E4. 🟠 Lookahead ในขา rate/funding ของ carry-adjusted ε — backtest ใช้อัตราที่ ณ เวลานั้นยังไม่รู้
*เลนส์: econometrician*

**กลไกที่เงินหาย:** (1) พอยกระดับเป็น ε = spread − fair_carry ตามแผน ต้องมี rate series เข้ามาในสูตร — จุดนี้คือประตู lookahead ใหม่ (2) รูปแบบพลาด: ใช้ SOFR/settlement ที่ประกาศย้อนหลัง (รู้จริง T+1) มาคำนวณ fair carry ของวันเดียวกัน, ใช้ rate curve วันนี้ตีราคา fair carry ย้อนหลังทั้งประวัติ (fair line เรียบผิดจริง → ε ดู mean-revert สวยเกิน), ฝั่ง crypto ใช้ realized funding ของรอบ 8 ชม. มาตัดสินใจ ณ ต้นรอบ ทั้งที่ตอนนั้นมีแค่ predicted rate (3) ผล: ε ใน backtest แกว่งแคบและกลับตัวไวกว่า ε ที่คำนวณได้จริง ณ เวลาเทรด → threshold, half-life, Sharpe เว่อร์หมด — live แล้ว band ที่คิดว่าแน่นกลับไม่แน่น

**ทำไมนึกไม่ถึง:** ทุกคนระวัง lookahead ที่ 'ราคา' แต่ไม่มีใครมองว่า rate ก็เป็น time series ที่มี publication lag และ revision — ยิ่ง data vendor เสิร์ฟ rate เป็นคอลัมน์เดียวจัด align ให้แล้ว ยิ่งมองไม่เห็นว่า ณ bar นั้นตลาดยังไม่รู้ค่านั้น

**ป้องกัน/ตรวจจับ:** (1) กฎ point-in-time: ทุก input ใน fair_carry_t ต้องเป็นค่าที่ตลาดรู้แล้ว ณ t (SOFR ใช้ค่าเมื่อวาน, funding ใช้ predicted rate ไม่ใช่ realized) (2) เก็บ snapshot rate curve เป็นรายวัน (as-of database) แทน series เดียวย้อนหลัง (3) sanity test: รัน backtest สองรอบ — rate แบบ point-in-time vs แบบ ex-post — ถ้า Sharpe ต่างกันมาก แปลว่า edge อยู่ที่ lookahead ไม่ใช่ mispricing (4) ระบุใน ε definition เสมอว่าใช้ rate ตัวไหน ณ lag เท่าไร

**ตัวเลขให้เห็นภาพ:** Funding arb backtest ที่ใช้ realized rate แทน predicted ณ ต้นรอบ มักเปลี่ยนจากกำไรเป็นเสมอตัว เพราะรอบที่ funding พลิกเครื่องหมายคือรอบที่ทำกำไรปลอมทั้งหมด

**สถานะในเล่ม:** ch17 §17.3 ใช้ r=5.25% ค่าเดียวคงที่ทั้งตัวอย่าง — ไม่มีมิติเวลาเลย แผน 17.9 สั่งให้ใช้ 'rate curve จริง' (แก้ pitfall ข้อ 2 ที่วินิจฉัยแล้ว — การสร้าง ε ให้ถูก) แต่ยังไม่มีใครเตือนเรื่อง backtest hygiene ของขา rate: publication lag, as-of snapshot, predicted vs realized funding — ch13 ก็ใช้ funding แบบรู้ค่าแล้วตลอด

**→ ไปอยู่ที่:** Phase 4: หัวข้อย่อยใน ch17.9 'Point-in-Time Rates' + กล่องเตือนใน ch13/แผน ch13c (funding spreads)

### E5. 🟠 Mean reversion ปลอมจาก microstructure — bid-ask bounce ทำ κ เฟ้อ และ Epps effect ทำ β เพี้ยน แม้ data จะ sync แล้ว
*เลนส์: econometrician*

**กลไกที่เงินหาย:** (1) ต่อให้แก้ปัญหา timestamp ไม่ sync แล้ว (pitfall ข้อ 6 เดิม) ราคา last-trade ยังเด้งสลับ bid/ask — Roll model: สร้าง autocovariance ลบ = −s²/4 ในราคาที่ไม่มี mean reversion จริงเลย (2) AR(1) บน spread ที่สร้างจากราคาแบบนี้จึงได้ b̂ ต่ำปลอม → κ เฟ้อ → half-life ระดับ 'นาที' ที่หน้าจอ — แต่ 'ระยะกลับตัว' ที่เห็นคือครึ่งหนึ่งของ bid-ask spread ที่คุณต้องจ่ายเพื่อเข้าออกพอดี = เก็บ edge เท่า spread แต่จ่าย cost เท่า spread ทุกไม้ (3) ซ้อนด้วย Epps effect: ที่ TF ละเอียด correlation/β ระหว่างสอง instrument ถูกกดต่ำลงเพราะ trade ไม่พร้อมกัน → β ที่ fit บน 1m ต่างจาก β จริงเชิงโครงสร้าง → hedge ไม่สมดุล เกิด residual drift ที่ไม่ใช่สัญญาณ

**ทำไมนึกไม่ถึง:** สายตาแยกไม่ออกระหว่าง mean reversion จริงกับ bounce — ทั้งคู่ดูเป็น oscillation รอบค่ากลางเหมือนกันเป๊ะ และ half-life สั้น ๆ ดูเป็นข่าวดี ('กลับไว!') ทั้งที่ half-life ≈ 1–3 bar คือลายเซ็นคลาสสิกของ noise ไม่ใช่ alpha

**ป้องกัน/ตรวจจับ:** (1) red flag อัตโนมัติ: half-life ≤ 3 bar ของ TF ที่ใช้ → สงสัย microstructure ก่อน alpha เสมอ (2) fit OU จาก mid-quote ไม่ใช่ last-trade แล้วเทียบ half-life สองแบบ — ถ้าต่างกันมาก = bounce (3) เช็ค expected gross ต่อไม้ ≥ 2–3× executable spread cost ไม่ใช่แค่ > 0 (4) ประเมิน β จาก TF หยาบกว่า (H1/H4) แล้วนำมาใช้กับ execution TF — ห้าม fit β บน TF ที่จะยิง order (5) ทดสอบ signal ด้วย executable price (ตาม ch10b) ถ้า edge หายเมื่อเปลี่ยนจาก mid เป็น executable = ไม่เคยมี edge

**ตัวเลขให้เห็นภาพ:** Bid-ask spread s=4 ticks → last-trade series แสดง 'reversion' amplitude ~2 ticks ทุกไม้ ขณะ round-trip cost = 4+ ticks → แพ้ทุกไม้แบบคงเส้นคงวา; Epps: ρ ที่ 1m อาจ 0.5 ทั้งที่ 1h เป็น 0.95

**สถานะในเล่ม:** คำว่า microstructure โผล่ครั้งเดียวทั้งเล่ม (กล่อง ch7 'holding < 2 bar อาจเป็น microstructure noise' — หนึ่งวลี ไม่มีกลไก) แผน ch10b ครอบ async spike + executable spread แล้ว (ตรง pitfall ข้อ 6 เดิม) แต่ยังไม่มี bounce→κ เฟ้อ (เกิดแม้ sync สมบูรณ์) และไม่มี Epps effect ต่อ β ทั้งในเล่มและในแผน

**→ ไปอยู่ที่:** Phase 4: เพิ่มเข้า ch10b อีกหนึ่งหัวข้อ 'Mean Reversion ปลอมจาก Microstructure' (ต่อจากส่วน executable spread) + โยงกลับ ch3 Kendall bias ว่าเป็น bias คนละตัวที่เสริมกัน

### E6. 🟠 Half-life ปลอมจาก Bid-Ask Bounce และ Bar ที่เลือก — วัดสปริงที่ไม่มีอยู่จริง
*เลนส์: execution/microstructure* · *ญาติกับ E6 — มุมการเลือก bar/TF*

**กลไกที่เงินหาย:** ขั้นที่ 1: สร้าง spread series จาก trade price (หรือ 1m close) แล้ว fit OU ขั้นที่ 2: trade price เด้งไปมาระหว่าง bid กับ ask (bounce) — สลับ buy/sell ทีก็ 'กลับ' ทั้ง tick โดยราคากลางไม่ขยับเลย; บน TF เล็ก bounce นี้คือ negative autocorrelation แรง → AR(1) ให้ b ต่ำ → κ สูง → half-life สั้นสวยงาม ทั้งที่ mean reversion นั้นคือความกว้างของ bid-ask เอง ซึ่งเป็นสิ่งเดียวที่เราเก็บกินไม่ได้ (เพราะต้องจ่ายมันเพื่อเข้า-ออก) ขั้นที่ 3: ขา illiquid (APEX / Lighter ช่วงเงียบ) ซ้ำหนักกว่า: last price ค้าง พอ print ใหม่ก็ 'วิ่งกลับ' หา leg อีกฝั่ง — staleness แปลงร่างเป็น mean reversion ในสถิติ ขั้นที่ 4: ทุกอย่าง downstream พังหมด: TF ที่ ch10b บอกให้เลือกจาก half-life ก็เลือกผิด, threshold z ก็ calibrate บน σ ที่เป็น noise, sizing ch12 ก็ scale ผิด — ระบบทั้งระบบสร้างขึ้นบนสปริงที่ไม่มีจริง แล้วจ่าย friction เต็มราคาทุกเทรด

**ทำไมนึกไม่ถึง:** ไม่มีเครื่องมือ retail ตัวไหนแยก 'mean reversion ของ value' ออกจาก 'mean reversion ของ noise' ให้ดู — ยิ่ง TF เล็ก half-life ยิ่งสั้น ยิ่งดูน่าเทรด retail เลยตีความว่า 'เจอคู่เทพ' ทั้งที่กำลังวัดความกว้าง spread ของโบรกตัวเอง; ส่วน bias ฝั่งตรงข้าม (bar ใหญ่ทำ half-life ยาวเกิน — วัดอะไรที่ละเอียดกว่า bar ไม่ได้) ก็ไม่มีใครเตือน

**ป้องกัน/ตรวจจับ:** fit OU บน synchronized mid เท่านั้น ห้ามใช้ trade/last price; ทำ robustness ladder: ประเมิน half-life บน 3–4 TF (1m/5m/15m/1h) — ถ้า half-life 'จริง' มันต้อง converge ข้าม TF, ถ้ามันสั้นลงเรื่อย ๆ เมื่อ TF เล็กลง = bounce/staleness; เช็คว่า half-life ที่ได้ > 5–10 bar ของ TF ที่ใช้ fit (ต่อยอดประโยคเดียวใน ch7); เทียบ σ_stat ที่ fit ได้กับ (half bid-ask A + half bid-ask B) — ถ้าใกล้กัน สปริงนั้นคือ bid-ask ไม่ใช่ alpha

**ตัวเลขให้เห็นภาพ:** spread mid นิ่ง แต่ trade price เด้ง bid↔ask กว้าง 2 tick: AR(1) บน 1m ให้ half-life ~3 นาที, บน mid ให้ half-life 4 ชั่วโมง — ต่างกัน 80 เท่า; ระบบที่เทรดตาม 3 นาทีจ่าย round-trip friction ~20bps เพื่อไล่จับ noise ที่มีขนาด 2 tick

**สถานะในเล่ม:** ch3 สอน Kendall bias (window สั้น → half-life สั้นเกิน) ซึ่งเป็น bias คนละตัว — ของ statistical sample ไม่ใช่ของ data ข้างใต้; ch7 มีประโยคเดียว 'holding < 2 bar อาจเป็น microstructure noise' ไม่มีกลไก ไม่มีวิธีตรวจ; แผน ch10b บอกให้เลือก TF จาก half-life โดย assume ว่า half-life ที่วัดมาถูก — ช่องโหว่คือขั้นก่อนหน้านั้น

**→ ไปอยู่ที่:** ch10b หัวข้อใหม่ 'Half-life ที่เชื่อได้: mid vs trade, bounce, และ convergence test ข้าม TF' (ต้องมาก่อนหัวข้อเลือก TF) + cross-ref ใน ch3.6 Calibration

### E7. 🟠 Survivorship Bias ในจักรวาลที่สแกน — backtest บนเหรียญ/สัญญาที่ยังรอดถึงวันนี้
*เลนส์: econometrician*

**กลไกที่เงินหาย:** (1) retail ดึงรายชื่อ symbol ปัจจุบันจาก Bybit/broker แล้ว backtest ย้อนหลัง 1–2 ปี (2) เหรียญที่ delist, สัญญาที่หยุดเทรด, คู่ที่ spread ระเบิดจน liquidity หาย — หายไปจากจักรวาลก่อนถึงมือเรา และเคสเหล่านั้นคือกรณี 'cointegration แตก' ที่แรงที่สุดพอดี (3) ผล: อัตราการรอดของความสัมพันธ์และ tail loss ของกลยุทธ์ pairs ถูกประเมินต่ำอย่างเป็นระบบ — backtest เห็นแต่คู่ที่จบสวย (4) live แล้วเจอ base rate จริงของการ delist/แตกคู่ ซึ่งมักมาพร้อม gap ขาลงของขา alt ที่ short hedge ไม่ทัน

**ทำไมนึกไม่ถึง:** API ของ exchange เสิร์ฟเฉพาะ symbol ที่ active — ข้อมูลของผู้ตายต้องไปขุดเอง retail ไม่รู้ด้วยซ้ำว่ามีอะไรหายไปจากรายการ เพราะสิ่งที่มองไม่เห็นย่อมไม่ถูกนับ

**ป้องกัน/ตรวจจับ:** (1) เก็บ snapshot รายชื่อ symbol เป็นระยะ (point-in-time universe) แล้ว backtest บนจักรวาล ณ เวลานั้น (2) ถ้าไม่มีข้อมูลผู้ตาย ให้บวก haircut กับผล backtest ของคู่ที่มีขา alt/เหรียญเล็ก และ cap sizing ตาม delist risk (3) นับ base rate: กี่ % ของ symbol เมื่อ 2 ปีก่อนที่วันนี้ไม่อยู่แล้ว — ใช้เป็น prior ของ P(คู่แตก)/ปี (4) กติกา: คู่ที่ขาหนึ่งอยู่นอก top-N ตาม volume ต้องมี exit plan สำหรับ delist announcement

**ตัวเลขให้เห็นภาพ:** ถ้า 15% ของ perp listings หายไปใน 2 ปี และคู่แตกเฉลี่ยเสียหาย 5–15% ต่อครั้ง → expected loss ที่ backtest มองไม่เห็น ~0.4–1%/ปี/คู่ ยังไม่รวม gap ตอนประกาศ delist

**สถานะในเล่ม:** ไม่มีคำว่า survivorship ที่ใดในเล่ม (grep ยืนยัน) ch5 pipeline เริ่มจาก 'คู่ทั้งหมดที่มี' โดย assume ว่าจักรวาลคงที่ ch24 พูด model แตกระดับ fund แต่ไม่แตะ bias ระดับ data universe ของ backtest แผนขยายก็ไม่มีหัวข้อนี้

**→ ไปอยู่ที่:** ch5 (แทรกในกล่องเตือนของ §5.8 pipeline) + ch24 เพิ่มบทเรียนสั้นเรื่อง universe bias — ทำได้ใน Phase 5

### E8. 🟠 ภาษี Stop-loss บน OU — stop 3σ แบบระยะราคา เผาผลกำไรของกลยุทธ์ mean reversion ที่มี edge จริง
*เลนส์: econometrician*

**กลไกที่เงินหาย:** (1) เล่มสอน state machine ที่ stop เมื่อ |z| ≥ 3 — แต่สำหรับ OU จริง เข้าที่ 2σ มีความน่าจะเป็นราว 15–25% (ขึ้นกับ κ เทียบ σ) ที่จะแตะ 3σ ก่อนกลับ θ — ไม่ใช่เหตุการณ์หายาก (2) จุด 3σ คือจุดที่ expected return ของ position สูงสุดพอดี (แรงดึงกลับแปรผันตามระยะจาก θ) — stop แบบระยะจึงขายตรงจุดที่ควรถูกที่สุด แล้ว ณ 3σ กระบวนการ mean-revert มักลากกลับเข้ามาใน band ทำให้ re-entry ก็เสียจังหวะซ้ำ (3) ทุกครั้งที่ stop โดน เสีย ~1σ+ + friction — เกิดบ่อยพอที่จะกิน edge ต่อไม้ (~0.5–1.5σ gross) จนกลยุทธ์ที่มี alpha จริงกลาย EV ลบ (4) เหตุผลที่ต้องมี stop คือ regime break — แต่ 'ระยะราคา 3σ' เป็น proxy ที่แย่ของ regime break: มัน trigger กับ excursion ปกติของ OU มากกว่า break จริง

**ทำไมนึกไม่ถึง:** 'ต้องมี stop-loss' เป็น dogma จากโลก trend/directional ที่ PnL เป็น martingale — retail ยกมาใช้กับ mean reversion โดยไม่รู้ว่าโครงสร้างกลับด้าน: สำหรับ OU ยิ่งลบยิ่ง expected return สูง การตัดขาดทุนด้วยระยะจึงตัด 'ตรงข้าม' กับ information และไม่มีใครคำนวณความถี่ที่ OU ปกติจะแตะ stop เอง

**ป้องกัน/ตรวจจับ:** (1) คำนวณ P(แตะ 3σ ก่อนกลับ θ | เข้า 2σ) จากพารามิเตอร์ OU ของคู่ แล้วคูณเป็น 'ภาษี stop ต่อไม้' ใส่ใน edge calculation ของ ch19 — ถ้า edge หลังภาษีติดลบ แปลว่า band/stop ออกแบบผิด (2) แยก stop สองชนิด: structural stop (ADF fail ใน rolling window, θ shift ตรวจด้วย ch9 regime filter, funding structure เปลี่ยน) = ออกทันที vs price stop = ตั้งไกลพอ (≥4σ) ให้ trigger จาก break จริงไม่ใช่ excursion ปกติ (3) ใช้ time-stop ควบ (จากข้อ first-passage) เพราะ 'ช้าเกิน' เป็นหลักฐานของ break ที่ดีกว่า 'ไกลเกิน' (4) backtest ต้องรายงาน % ของ trade ที่จบด้วย stop — ถ้าเกิน ~10% ระบบกำลังจ่ายภาษีนี้หนัก

**ตัวเลขให้เห็นภาพ:** OU เข้า 2σ: ถ้า P(แตะ 3σ ก่อน θ) = 20%, ค่าเสียต่อครั้ง 1.2σ → ภาษี stop = 0.24σ/ไม้ เทียบ expected gross 0.8σ = กิน 30% ของ edge ก่อนคิด fee

**สถานะในเล่ม:** ch11 state machine ใช้ STOP ที่ |z|≥3 เป็นกฎตายตัว, โจทย์ 3.3 ก็ใช้ 'stop-loss triggered ที่ 3σ' — ทั้งเล่มไม่เคยคำนวณความน่าจะเป็นที่ OU ปกติจะแตะ stop เอง ไม่มีแนวคิด stop-loss tax ใน edge budget ของ ch19 และไม่มีการแยก structural stop vs price stop (ch9 มีเครื่องมือ regime filter อยู่แล้วแต่ไม่ถูกเชื่อมมาทำหน้าที่นี้)

**→ ไปอยู่ที่:** ch11 เพิ่มหัวข้อ 'เศรษฐศาสตร์ของ Stop บน Mean Reversion' + หนึ่งแถวใหม่ใน edge waterfall ของ ch19 — เข้า Phase 5 retrofit ได้

### E9. 🟠 Cointegration จริงแต่เทรดไม่คุ้ม — Edge ต่อหน่วยเวลา แพ้ Carry ต่อหน่วยเวลา + หางขวาของเวลากลับตัว
*เลนส์: econometrician*

**กลไกที่เงินหาย:** (1) คู่ cointegrate จริง half-life 14 วัน entry ที่ 2σ คาดกำไร gross ~1.5σ (2) แต่ระหว่างถือ จ่าย carry ทุกวัน: funding perp 2 ขา (Bybit 3 รอบ/วัน), swap MT5 ทุกคืน, opportunity cost ของ margin futures (3) เวลากลับตัวจริงไม่ใช่ half-life: first-passage time ของ OU จาก 2σ กลับ θ มี median ต่ำแต่ mean สูงกว่าและหางขวาอ้วน — สัดส่วนไม่น้อยของ trade ถือเกิน 2–3 half-life (4) ผล: trade ที่ 'ชนะ' ตามสถิติ spread กลับ θ จริง แต่ net PnL ติดลบเพราะ carry สะสมกินหมด — ระบบดูถูกต้องทุกอย่าง ยกเว้นบรรทัดสุดท้าย

**ทำไมนึกไม่ถึง:** Retail มอง edge เป็น 'ระยะทาง σ' ไม่ใช่ 'อัตราต่อเวลา' และเข้าใจผิดว่า half-life = เวลาถือโดยเฉลี่ย (จริง ๆ คือเวลาที่ระยะทางหด 50% — เวลาถึง θ จริงยาวกว่าและกระจายกว้างมาก) ส่วน carry ไม่โผล่บน spread chart จึงไม่อยู่ในสายตา

**ป้องกัน/ตรวจจับ:** (1) เพิ่ม metric บังคับก่อนเข้า: edge_rate = expected_gross / E[holding_time] เทียบ carry_rate = (funding+swap+margin cost)/วัน — ถ้า edge_rate < 2× carry_rate ห้ามเทรด (2) ตาราง first-passage: P(ยังไม่กลับ θ หลัง 1, 2, 3 half-life) และ carry สะสม ณ จุดนั้น (3) time-stop ที่ตั้งจาก first-passage quantile (เช่น ออกที่ P75 ของเวลากลับตัว) ไม่ใช่ถือรอ convergence ไม่จำกัด (4) กติกา: half-life × carry_ต่อวัน ต้อง < 1/3 ของ expected gross

**ตัวเลขให้เห็นภาพ:** Half-life 14 วัน, gross คาด 0.9%, funding+swap 2 ขา 0.05%/วัน → ถือถึง P75 ของเวลากลับตัว (~30 วัน) จ่าย carry 1.5% → net −0.6% ทั้งที่ spread กลับ θ จริง

**สถานะในเล่ม:** ch12 §12.2 มี half-life scaling สำหรับ sizing และ ch19 มี funding cost แยกเป็นรายการ แต่ไม่มีที่ไหนเอาสองอย่างมาหารกันเป็น 'edge ต่อหน่วยเวลา vs carry ต่อหน่วยเวลา' และทั้งเล่มไม่มี first-passage time distribution — ทุกตัวอย่างใช้ half-life แทนเวลาถือแบบเงียบ ๆ (เช่น โจทย์ 3.2 'Holding time เฉลี่ย ≈ τ₁/₂')

**→ ไปอยู่ที่:** ch19 เพิ่มหัวข้อ 'Cost of Time' (โยง ch12) หรือแทรกใน Phase 5 retrofit — เหมาะเป็น §19.7b ต่อจาก Break-even Analysis


## F. เศรษฐศาสตร์ของบัญชีเล็ก — edge เป็น % ผ่าน แต่เป็น $ ไม่ผ่าน

### F1. 🟠 ทุนขั้นต่ำของเกม: edge เป็น % ผ่าน แต่เป็น $ ไม่พอจ่าย fee ขั้นต่ำต่อรอบ
*เลนส์: retail ตัวจริง*

**กลไกที่เงินหาย:** ch19 คิด edge เป็น bps เทียบ friction เป็น bps — ผ่านทั้งคู่ แต่บัญชีเล็กเจอ 'พื้นค่าธรรมเนียมแบบ absolute' ที่ไม่ scale ลง: futures คิด fee ต่อสัญญา (CME GC ~$2.5–5/side/contract, broker+exchange+NFA รวม ~$10–20 ต่อ round-turn 2 ขา), MT5 ECN คิด $3–7/lot, บาง exchange มี minimum fee ต่อ order ขั้นตอน: (1) edge ต่อรอบของ calendar/cross-venue spread = 1–3 tick, (2) tick value คูณจำนวนสัญญาที่ทุนเล็กเปิดได้ (1 สัญญา) = $10–30, (3) fee ขั้นต่ำ+slippage = $10–20 → net ≈ 0 หรือติดลบ ทั้งที่สูตร % บอกว่า 'มี edge' เกมนี้มี break-even capital ที่คำนวณได้ แต่เล่มไม่เคยให้สูตร

**ทำไมนึกไม่ถึง:** ตำรา (รวมเล่มนี้) เขียนทุกอย่างเป็น % ของ notional — retail ที่ทุน $2k–10k ไม่เคยเห็นว่า cost floor เป็น $ คงที่ต่อรอบ ไม่ใช่ % Running example ch12 ใช้ capital $100,000 ซึ่งไม่ใช่โลกของผู้อ่านเป้าหมาย

**ป้องกัน/ตรวจจับ:** เพิ่มสมการ 'minimum viable capital': ทุนขั้นต่ำ ≈ (fixed fee ต่อรอบ × safety 3) / (expected edge ต่อรอบเป็นเศษส่วนของ notional) แล้วตารางจริง: Bybit taker 5.5bps×4 ขา, CME GC spread 1 lot, MT5 $/lot — ให้ผู้อ่านเช็คก่อนเปิดบัญชีว่าตลาดไหน 'ทุนเขาถึง' ตลาดไหนต้องข้ามไปก่อน

**ตัวเลขให้เห็นภาพ:** edge 10bps บน position $1,000 = $1 ต่อรอบ แต่ Bybit taker 0.055%×4 legs = $2.2 → net −$1.2 ทุกรอบที่ 'ชนะ'

**สถานะในเล่ม:** ch19 มี Edge Waterfall แต่ทุก component เป็น % ต่อ trade — ไม่มี fee floor แบบ absolute, ไม่มีสูตรทุนขั้นต่ำ; ch12 sizing เริ่มจาก capital ใหญ่เสมอ

**→ ไปอยู่ที่:** บทใหม่ ch19b 'เศรษฐศาสตร์ของบัญชีเล็ก' (แทรกหลัง ch19) — หรือ §19.11

### F2. 🟠 ค่าธรรมเนียม futures เป็นดอลลาร์คงที่ต่อสัญญา ไม่ใช่ % ของ notional — บน micro contract ค่าคอมรอบเดียว = 1–2 เท่าของ σ รายวันของ spread
*เลนส์: โต๊ะ futures*

**กลไกที่เงินหาย:** โครงสร้าง cost ของ ch19 ทั้งบทคิดเป็น % (bps) แบบ crypto — แต่ futures เก็บ fee คงที่ต่อสัญญา (exchange fee + NFA + คอมโบรก ≈ $2.5–4/ข้าง สำหรับ GC, ~$1–1.5/ข้าง สำหรับ MGC) จุดตาย: calendar/cross-exchange spread ของทองมี σ รายวันเล็กมากเป็น 'ดอลลาร์ต่อสัญญา' — spread ระดับ 2 เดือนขยับตาม rate เป็นหลัก σ รายวัน ~$0.2–0.4/oz → GC = $20–40/วัน/สัญญา, MGC = $2–4/วัน/สัญญา; เทรดหนึ่งรอบ = 4 executions → ค่าคอม GC ~$10–16 = 0.3–0.8 σ_daily ยังพอไหวถ้าถือหลายวัน แต่ MGC ~$4–6 = 1–2 เท่าของ σ รายวัน — แปลว่าต่อให้สัญญาณถูก 100% edge ที่ 2σ ก็แค่พอจ่ายค่าคอม; retail ที่ 'เริ่มจาก micro เพื่อฝึก' กำลังเทรดเกมที่คณิตศาสตร์แพ้ตั้งแต่ก่อนกดปุ่ม และไม่เห็นเพราะคิด cost เป็น % ของ notional (ซึ่งดูจิ๋ว ~0.001%)

**ทำไมนึกไม่ถึง:** สมองที่ฝึกจาก crypto คิด fee เป็น % เสมอ — 0.03% ฟังดูถูกกว่า Bybit ด้วยซ้ำ แต่ % ของ notional ไม่ใช่หน่วยที่ถูกต้องสำหรับ spread trade: หน่วยที่ถูกคือ 'fee ต่อรอบ ÷ σ ของ ε' และตัวเลขนี้บน micro แย่กว่า crypto taker หลายเท่า; ยิ่ง contract เล็ก fee ต่อสัญญาไม่ได้ scale ลงตาม → micro ถูก penalize เชิงโครงสร้าง

**ป้องกัน/ตรวจจับ:** ก่อนเลือก instrument คำนวณ ratio เดียว: total fee round-trip (รวม 4 ขา หรือ 2 ขาถ้าใช้ listed spread) ÷ σ_daily ของ ε เป็น $ — ต้อง < 0.3 ถึงจะมีเกมให้เล่น; ตารางเทียบ GC vs MGC vs listed calendar spread (listed spread = 2 fills ไม่ใช่ 4 + bid-ask 1 tick); ข้อสรุปที่ต้องกล้าเขียน: ที่ size ต่ำกว่า ~1 GC เกม calendar ทองไม่มีอยู่จริงสำหรับ retail — ไม่ใช่เพราะฝีมือ แต่เพราะเลขหาร

**ตัวเลขให้เห็นภาพ:** MGC calendar: σ_daily ~$2–4/สัญญา, ค่าคอมรอบละ ~$4–6 (4 ขา) → fee/σ ≈ 1.5–2.0; GC ผ่าน listed spread: fee ~$6–8 + 1 tick bid-ask $10 vs σ_daily $20–40 → fee/σ ≈ 0.4–0.9 — ยังต้องถือหลายวันถึงคุ้ม

**สถานะในเล่ม:** ch19 ทั้งบทเป็น % bps ของ crypto perp — ไม่มี fee แบบ $ คงที่ต่อสัญญา, ไม่มีการเทียบ fee กับ σ ของ spread เป็นดอลลาร์, ไม่มี micro vs full-size; แผน 17.12 พูด legging vs listed spread (pitfall 4 เดิม) แต่ไม่พูดโครงสร้าง fee คงที่และผลต่อการเลือกขนาดสัญญา

**→ ไปอยู่ที่:** ขยาย ch19 เพิ่มหัวข้อ 'Futures Fee Math: $ ต่อสัญญา vs σ ของ ε' + ตารางใน 17.12

### F3. 🟠 ต้นทุนคงที่รายเดือน (VPS/data/API) คือ hurdle rate ที่บัญชีเล็กข้ามไม่ผ่าน
*เลนส์: retail ตัวจริง*

**กลไกที่เงินหาย:** ระบบตามเล่มนี้ต้องมี: VPS ใกล้ venue 1–2 ตัว ($10–40/เดือน/ตัว), CME real-time market data สำหรับ non-professional (~$3–15/exchange/เดือนผ่านโบรกเกอร์ แต่ต้องมีบัญชี active), historical data สำหรับ walk-forward, charting/monitoring รวม $50–150/เดือน = $600–1,800/ปี — เป็น cost ที่จ่ายทุกเดือนไม่ว่าจะมี trade หรือไม่ ตลาด full-carry ที่ระบบบอกว่า 'ไม่มี order' (ซึ่งถูกแล้ว ตาม pitfall เดิม) จึงเจ็บซ้ำสอง: จ่าย overhead เต็มแต่รอบเทรดเป็นศูนย์ บนทุน $5k overhead $1,200/ปี = ต้องทำ 24%/ปี แค่เพื่อเท่าทุน — ก่อนคิด edge ใด ๆ

**ทำไมนึกไม่ถึง:** ch19 นิยาม cost = ต่อ trade ทั้งหมด (fee, spread, slippage, funding, legging) — ไม่มีบรรทัด fixed cost เพราะสำหรับ prop desk มันเป็น rounding error แต่สำหรับ retail มันคือ item ใหญ่สุดในงบ

**ป้องกัน/ตรวจจับ:** เพิ่มบรรทัดที่ 6 ใน Edge Waterfall: annualized fixed cost / capital แล้วให้สูตร break-even: ทุนขั้นต่ำที่ overhead เหลือ <2% ต่อปี; เทคนิคลด: เริ่มจาก venue ที่ data ฟรี (Bybit/Lighter WebSocket ฟรี), เลื่อน CME ไปจนพอร์ตถึงขั้น, รวม infra หลายกลยุทธ์บน VPS เดียว

**ตัวเลขให้เห็นภาพ:** ทุน $5,000 + overhead $100/เดือน → hurdle 24%/ปี · ทุน $50,000 → hurdle 2.4%/ปี — เกมเดียวกัน คนละความเป็นไปได้

**สถานะในเล่ม:** ไม่มีที่ไหนในเล่มพูดถึง fixed cost เลย (grep: ไม่มี VPS/data feed/subscription)

**→ ไปอยู่ที่:** ch19b (ส่วน fixed cost + break-even capital) — คู่กับข้อทุนขั้นต่ำ

### F4. 🟡 Opportunity cost ของ half-life ยาว: ทุนจมสัปดาห์ละรอบ ทำ annualized แพ้ funding rate ที่นอนรับเฉย ๆ
*เลนส์: retail ตัวจริง*

**กลไกที่เงินหาย:** edge ต่อรอบดูสวย (เช่น 40bps) แต่ตัวหารคือเวลา: τ½ 5 วัน + รอ setup → 15–25 รอบ/ปี/คู่ → 6–10%/ปี บนทุนที่ล็อกเต็ม (สองขา+buffer ตามข้อ margin) ขณะที่ benchmark ของ retail crypto มีอยู่จริงและ passive กว่ามาก: cash-and-carry รับ funding เฉลี่ย 8–15%/ปี หรือ T-bill 4–5% กลยุทธ์ที่ 'กำไร' จึงยังแพ้ทางเลือกที่ง่ายกว่า — และแพ้แบบมองไม่เห็นเพราะไม่เคยเทียบ ยิ่งไปกว่านั้น ทุนที่จมใน trade ที่ยืด 3×τ½ คือทุนที่เปิดโอกาสใหม่ไม่ได้ทั้งที่ z ตัวใหม่สวยกว่ากำลังวิ่งผ่านหน้า

**ทำไมนึกไม่ถึง:** ตำราวัดต่อ trade (win rate, edge per cycle) ไม่วัดต่อ 'ดอลลาร์-ปี'; retail ไม่ตั้ง hurdle rate เพราะไม่มีใครบังคับ — prop desk มี cost of capital ชัดเจน จึงไม่พลาดข้อนี้

**ป้องกัน/ตรวจจับ:** ทุกกลยุทธ์ต้องมีบรรทัด annualized return on locked capital = edge_net × (365/avg_holding_days × utilization) / capital_locked แล้วเทียบ 3 benchmark: funding carry, T-bill, ไม่ทำอะไร; กติกา: ถ้าไม่ชนะ carry passive อย่างน้อย 1.5 เท่า ไม่คุ้มความซับซ้อน+tail risk ที่แบกเพิ่ม; time-stop ที่ 3×τ½ ยังช่วยปลดทุนจมมาใช้กับ setup ใหม่

**ตัวเลขให้เห็นภาพ:** edge 40bps × 18 รอบ/ปี = 7.2% บน notional → หาร capital lock 2.5 เท่า = 2.9% จริง < T-bill

**สถานะในเล่ม:** ch19 จบที่ net edge ต่อ trade, ch20 จบที่ risk limit — ไม่มีการ annualize หรือเทียบ benchmark ที่ไหนในเล่ม

**→ ไปอยู่ที่:** ch19b (ส่วน 'Annualize ก่อนตกหลุมรัก') + Situation Card ทุกกลยุทธ์ควรมีช่องความถี่×edge ต่อปี (สอดคล้องข้อ 3 ของ Situation Card ในแผน)

### F5. 🟠 สกุลเงินและกระเป๋า margin: ขา offshore ทำให้ PnL/margin เป็น USD บนทุน THB — และคู่ที่ quote คนละสกุล (SHFE/TFEX) คือเทรด FX แฝงทั้งตัว
*เลนส์: โต๊ะ futures*

**กลไกที่เงินหาย:** สองชั้น: (1) ชั้นที่โดนแน่ ๆ — ทุนเป็น THB แต่ margin/variation margin/PnL ของทั้ง CME และ APEX เป็น USD: ทุกครั้งที่โดน cash call ต้องแปลง THB→USD ที่ retail FX spread + ค่าโอนระหว่างประเทศ และ equity ของพอร์ตแกว่งตาม USDTHB (~4–6%/ปี vol) ซึ่งใหญ่กว่า edge สะสมทั้งปีของ spread ทองได้สบาย ๆ — กำไร spread ทั้งไตรมาสหายได้ในสัปดาห์เดียวที่บาทแข็ง (2) ชั้นที่พลาดแบบไม่รู้ตัว — ถ้าขยายไปคู่ที่ quote คนละสกุล (SHFE gold = CNY/กรัม, TFEX Gold = อิง THB) spread ดิบ = ทอง + FX + import premium ปน; ส่วนที่ 'ดู mean-revert สวย ๆ' อาจเป็น USDCNH/USDTHB ล้วน ๆ — คุณกลายเป็น FX trader ที่ไม่มี view เรื่อง FX และไม่ได้ hedge ขานั้น

**ทำไมนึกไม่ถึง:** Crypto ทุกอย่าง denominate เป็น USD(T) หมด — ไม่มีประสบการณ์เรื่อง base currency ของบัญชี; และเมื่อกราฟ spread ข้ามสกุลถูก plot ใน currency เดียว (โบรกแปลงให้อัตโนมัติ) องค์ประกอบ FX ถูกซ่อนอยู่ในเส้นเดียวกัน มองด้วยตาแยกไม่ออก

**ป้องกัน/ตรวจจับ:** แยก ε เป็นสามส่วนเสมอเมื่อสองขา quote คนละสกุล: ε_total = ε_gold + ε_FX + premium_structural แล้วถามว่าตั้งใจเทรดตัวไหน — ถ้าตอบ ε_gold ต้อง hedge FX ขาโต้ (futures/forward USDTHB, USDCNH) และคิดค่า hedge เข้า cost; สำหรับ margin currency: ถือ USD buffer ก้อนเดียวพอสำหรับ worst-case cash call แทนการแปลงรายครั้ง และวัดผลงานพอร์ตเป็นสกุลเดียวคงที่; กฎเช็คเร็ว: regress spread กับ FX rate — ถ้า R² สูง คุณกำลังเทรด FX ไม่ใช่ทอง

**ตัวเลขให้เห็นภาพ:** USDTHB vol ~5%/ปี บน margin $20k ที่จมไว้ = swing ~35,000 บาท/ปี — เทียบ edge เป้าหมายของ calendar arb ที่อาจไม่ถึง 3–5% ต่อปีบนทุนเดียวกัน

**สถานะในเล่ม:** ทั้งเล่มอยู่ในจักรวาล USD-only — ไม่มีมิติ base currency ของบัญชี, FX บน margin, หรือ multi-currency spread เลย; ch21 (CFD) ใกล้สุดแต่ก็เป็น USD ทั้งคู่; แผนขยายกล่าวถึง SHFE ใน 17.10 แต่ยังไม่ระบุประเด็นสกุลเงิน

**→ ไปอยู่ที่:** 17.10 — หัวข้อย่อย 'Currency Decomposition ของ Cross-Border Spread' + กล่องเตือนเรื่อง margin currency ใน 17.13

### F6. 🔴 ภาษีไม่ net ข้ามขา/ข้าม jurisdiction: กำไรขา A โดนเก็บเต็ม ขาดทุนขา B หักไม่ได้ → เทรดที่ชนะกลายเป็นขาดทุนหลังภาษี
*เลนส์: retail ตัวจริง*

**กลไกที่เงินหาย:** spread trade ที่กำไรสุทธิ +$200 มักประกอบจาก ขา A +$1,000 / ขา B −$800 ปัญหาคือกฎภาษีมอง 'รายธุรกรรม/รายประเภทสินทรัพย์' ไม่ได้มอง ε: (ก) ไทย — กำไร crypto เป็นเงินได้พึงประเมิน แต่การหักกลบขาดทุนทำได้เฉพาะธุรกรรมบน exchange ที่ได้รับอนุญาตจาก ก.ล.ต. ไทย — Bybit/Lighter ไม่ใช่ → ปีที่ gross win 500k / gross loss 450k อาจโดนประเมินบนฝั่งกำไรโดยหักฝั่งขาดทุนไม่ได้ (ข) เงินได้จากต่างประเทศ (CME ผ่านโบรกนอก, MT5 offshore) ตามแนวปฏิบัติตั้งแต่ปี 2567 นำเข้าเมื่อไรเสียภาษีเมื่อนั้น ไม่ว่าจะเกิดปีไหน — การถอนกำไรกลับมาใช้จึงมี tax event ติดมาด้วย (ค) ข้ามประเภทสินทรัพย์ (กำไร futures / ขาดทุน CFD) ยิ่งไม่มีช่องให้ net

**ทำไมนึกไม่ถึง:** backtest ไม่มีคอลัมน์ภาษี และ arb ดูเหมือน 'กำไรเล็ก ๆ เรื่อย ๆ' จนลืมว่า gross สองฝั่งใหญ่กว่ากำไรสุทธิ 5–10 เท่า — ฐานภาษีที่แท้จริงอาจคือ gross ไม่ใช่ net; รู้ตัวอีกทีตอนยื่นภาษีปีถัดไป ซึ่งเงินถูกใช้ไปแล้ว

**ป้องกัน/ตรวจจับ:** (1) ก่อนเลือก venue ให้ถามว่า 'ขาดทุนขานี้ หักกลบกับกำไรขาไหนได้บ้างตามกฎหมายไทย' — ให้ตารางสถานะ: exchange ไทยที่ได้ใบอนุญาต (net ได้) vs offshore (เสี่ยง gross) vs futures ต่างประเทศ (เงินได้ต่างประเทศ) (2) กันเงิน 15–35% ของ gross winning leg ไว้เป็น tax reserve ไม่ใช่ % ของ net (3) จังหวะ remit เงินกลับไทยคือ decision variable — วางแผนก่อน ไม่ใช่โอนตามอารมณ์ (4) เก็บ statement ทุก venue รายเดือน — ภาระพิสูจน์อยู่ฝั่งเรา

**ตัวเลขให้เห็นภาพ:** ปีที่ net +50k แต่ gross win 500k: ถ้าหักกลบไม่ได้และโดน marginal rate 20% → ภาษี 100k = ขาดทุนจริง −50k

**สถานะในเล่ม:** ทั้งเล่มไม่มีคำว่าภาษี/tax/withholding แม้แต่ครั้งเดียว (ยืนยันด้วย grep) ทั้งที่กลุ่มเป้าหมายคือคนไทยเทรด 3 jurisdiction

**→ ไปอยู่ที่:** ch19b (ส่วนสุดท้าย 'ภาษีของนัก spread ไทย') หรือ Appendix ใหม่ — พร้อม disclaimer ให้ปรึกษาผู้เชี่ยวชาญเพราะกฎเปลี่ยน


## G. จิตวิทยา — มือทำลายสิ่งที่โมเดลสร้าง

### G1. 🔴 จิตวิทยาตัดขาเดียว: 'เก็บกำไรขาที่บวก' = เปลี่ยน arb เป็น directional bet ตรงจุดที่แย่ที่สุด
*เลนส์: retail ตัวจริง*

**กลไกที่เงินหาย:** UI ของแต่ละ venue โชว์ PnL แยกขา: 'ขา A +$650 / ขา B −$800' สมองมองเห็นสองเทรด ไม่ใช่หนึ่ง spread → ตอน spread วิ่งสวนนานกว่า half-life ที่คำนวณ (ซึ่งเกิดเป็นปกติ — half-life คือค่ากลาง ไม่ใช่เพดาน) แรงกระตุ้นคือ 'ล็อกกำไรขาบวกก่อน เดี๋ยวขาลบเด้งค่อยปิด' ผล: เหลือขาเดียว = short/long เปล่า ๆ ด้วยเหตุผลที่ไม่เคยมีในระบบ และสถิติของจุดนี้โหดร้าย: spread ที่ยืด 2.5–3σ คือจุดที่ expected reversion แรงสุด — ตัดขา ณ จุดนี้คือขายจุดที่ควรถือที่สุด แล้วพอ revert จริง ขาที่เหลือขาดทุนซ้ำอีกรอบ (โดนทั้งสองทาง)

**ทำไมนึกไม่ถึง:** ตำรา quant ถือว่า position คือ vector หนึ่งตัว — ไม่มีบทไหนยอมรับว่ามนุษย์เห็น PnL เป็นรายขาและ loss aversion ทำงานรายขา; คนที่ยังไม่เคยถือ spread ติดลบ 3 สัปดาห์จะไม่เชื่อว่าตัวเองจะทำ จนกระทั่งทำ

**ป้องกัน/ตรวจจับ:** (1) กติกาเหล็กเขียนไว้ก่อนเข้า: spread เข้าเป็นคู่ ออกเป็นคู่ — การปิดขาเดียวทำได้กรณีเดียวคือ emergency hedge ตาม playbook ch20 (venue ล่ม) (2) สร้าง dashboard ที่โชว์เฉพาะ ε, z, spread PnL รวม — ซ่อน PnL รายขา (3) ตั้ง time-stop จาก half-life (เช่น 3×τ½ ไม่ revert → ปิดทั้งคู่พร้อมกัน) เพื่อให้ 'ทางออกตอนทรมาน' มีอยู่แล้วในระบบ ไม่ต้องด้นสด

**ตัวเลขให้เห็นภาพ:** ถือ spread −2.8σ มา 12 วัน (τ½=4 วัน): ปิดขากำไร → คืนเดียว spread revert 1.5σ ขาที่เหลือ −$1,900 ทั้งที่ถือครบสองขาจะ +$400

**สถานะในเล่ม:** ch11 state machine ไม่มี state/transition ใดพูดถึงการปิดขาเดียวโดยสมัครใจ; ch20 มี black swan table แต่ไม่มีจิตวิทยา operator เลยทั้งเล่ม

**→ ไปอยู่ที่:** ขยาย ch11 (กล่องแดง 'Leg-Cut Temptation') + section ใหม่ใน ch20 'Operator Psychology & Playbook'

---

## สรุปการกระจายลงบท (สำหรับ Phase การเขียน)

รวม 31 ข้อ (หลังรวมมุมซ้ำ ~25 ประเด็นอิสระ) — เมื่อรวมกับ 6 ข้อเดิมใน §0.1 = **แคตตาล็อกจุดขาดทุน 30+ ข้อ**

**✅ กระจายลงบทครบทั้งหมดแล้ว (Phase 5 ส่วนขยาย)** — ตารางนี้อัปเดตเป็นจุดที่เขียนจริง (ต่างจากคอลัมน์ "→ ไปอยู่ที่" เดิมของแต่ละข้อที่เป็นแผนก่อนเขียน):

| กลุ่ม | จำนวน | สถานะ | บทที่เขียนจริง |
|---|---|---|---|
| A สเปก/hedge granularity | 3 | ✅ | A1: ch17 §17.10 · A2: ch12 (β granularity) + ch4b checklist · A3: ch14 §14.8 |
| B margin/กระแสเงินสด | 5 | ✅ | B1/B2: ch17 §17.13 + ch12 (path-max divergence) · B3: ch20 §20.9 · B4: ch17 §17.13 · B5: ch19 §19.13 |
| C เวลา/ปฏิทิน/นาฬิกา | 4 | ✅ | C1: ch10b §10B.6 · C2: ch17 §17.11 · C3: ch10b §10B.7 · C4: ch13c §13C.4 |
| D execution | 3 | ✅ | D1: ch19 §19.10 + ch14 · D2: ch17 §17.12.2 · D3: ch10b §10B.9 |
| E โมเดล/สถิติหลอก | 9 | ✅ | E1: ch5 §5.10 · E2: ch5 §5.11 · E3: ch17 §17.11 + ch10b §10B.10 · E4: ch17 §17.9 · E5/E6: ch10b §10B.8 · E7: ch5 §5.8 + ch24 · E8: ch3 fix + ch11 §11.7 + ch19 §19.12 · E9: ch19 §19.11 |
| F เศรษฐศาสตร์บัญชีเล็ก | 6 | ✅ | F1-F4/F6: ch19b (บทใหม่) · F5: ch17 §17.10 |
| G จิตวิทยา | 1 | ✅ | ch11 §11.8 + ch20 §20.10 |
| H (รอบผู้ใช้) | 1 | ✅ | H1: ch15 §15.8 |

---

## H. รายงานเพิ่มจากผู้ใช้ (รอบ 3)

### H1. 🟠 Kalman filter ปรับ β บ่อย → rebalance บ่อย → ค่าธรรมเนียมกิน edge หมด (churn)
*เลนส์: ประสบการณ์ตรงของผู้ใช้ — วิเคราะห์เพิ่มโดยทีม*

**กลไกที่เงินหาย:** Kalman filter อัปเดต β ทุก observation ตามสัดส่วน Q/R — ถ้า Q (process noise) ตั้งใหญ่ β จะ "วิ่งตาม noise" ทุกแท่ง และทุกครั้งที่ β เปลี่ยน ระบบต้อง rebalance ขา hedge = ส่งคำสั่งจริงขนาด |Δβ|×notional ซึ่งจ่าย fee+slippage ทุกรอบ; edge ของ stat arb ต่อเทรดบางมาก (หลัก bps) แต่ churn จาก rebalance รายวัน/รายชั่วโมงสะสมเป็น % ต่อเดือน → กลยุทธ์ที่ direction ถูกก็ยังขาดทุนสุทธิ นอกจากนี้ β ที่แกว่งเร็วทำให้ ε นิ่งเกินจริง (residual เล็กลงเพราะโมเดล "ตามใจ" ข้อมูล) → z-score ไม่ค่อยถึง threshold → เทรดน้อยลงแต่ rebalance ไม่หยุด = จ่ายต้นทุนโดยไม่มีรายได้

**ทำไมนึกไม่ถึง:** ตำรา (รวมถึง ch15 เดิม) สอน Kalman ในมุม "ดีกว่า rolling OLS เพราะ adapt เร็ว" โดยไม่พูดต้นทุนของการ adapt; backtest ส่วนใหญ่คิด fee เฉพาะตอน entry/exit ของ spread trade แต่ลืมคิด fee ของ**การ rebalance hedge ระหว่างถือ** ซึ่งใน Kalman เกิดถี่กว่าหลายเท่า

**ป้องกัน/ตรวจจับ:** (1) **Deadband/hysteresis**: rebalance เฉพาะเมื่อ |β_now − β_position| > δ โดยตั้ง δ จากต้นทุน: rebalance คุ้มเมื่อ (ความเสี่ยงจาก hedge เพี้ยน) > (ค่า fee ของการปรับ) (2) **ลด Q หรือตรึง Q/R จาก walk-forward** ไม่ใช่ค่า default — วัด turnover ของ β (Σ|Δβ|) เป็น metric ตอน calibrate ไม่ใช่ดูแค่ fit (3) **แยกนาฬิกา**: อัปเดต *ความเชื่อ* เรื่อง β ได้ทุกแท่ง แต่ *ปรับ position* ตามรอบเวลาที่หยาบกว่า (เช่น วันละครั้ง) หรือเมื่อทะลุ deadband เท่านั้น (4) เพิ่มบรรทัดใน backtest: นับ "จำนวนครั้ง rebalance × ค่าเฉลี่ย cost ต่อครั้ง" แยกจาก entry/exit cost — ถ้าเกิน 30% ของ gross edge ให้ถือว่า config นั้นใช้ไม่ได้ (5) เทียบ baseline: rolling OLS + recalibrate รายสัปดาห์ ชนะ Kalman หลังหักต้นทุนบ่อยกว่าที่คิด

**ตัวเลขให้เห็นภาพ:** notional ขา B = $50,000, β แกว่งวันละ ~0.02 จาก noise → rebalance วันละ $1,000, taker fee 0.055% = $0.55/วัน ≈ $17/เดือน ต่อคู่ — ถ้า expected edge ของคู่ ≈ $40/เดือน churn กินไปเกือบครึ่งโดยยังไม่รวม slippage

**สถานะในเล่ม:** ch15 (Kalman dynamic hedging) สอนกลไกครบแต่ (รอทีม QA ยืนยัน) ไม่มีหัวข้อ rebalancing cost/deadband; ch19 นับ cost ของ entry/exit แต่ไม่มีหมวด rebalance cost

**→ ไปอยู่ที่:** ch15 เพิ่มหัวข้อ "ราคาของการ Adapt: Q, Turnover ของ β และ Deadband" (Phase 5) + แถวใหม่ในตาราง cost ของ ch19 + Situation Card ของ ch15
