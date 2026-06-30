# แผน — เติมทฤษฎีระดับตำรา (Textbook Theory) แบบแทรกในบทเดิม

> ส่วนต่อยอดของ "อ่านกระดาน" · สังเคราะห์จาก gap analysis 2 ทีม (ตำราทฤษฎี O'Hara/Foucault/Hasbrouck + ตำรา quant/LOB Bouchaud/Cartea/Guéant/Harris) · **scope ที่อนุมัติ: Top 7 inline boxes, ไม่เพิ่มบทใหม่**

## หลักการ
- แทรกเป็นกล่อง "📚 ทฤษฎีเบื้องหลัง (จากตำรา)" ในบทที่ทฤษฎีนั้นถูกใช้อยู่แล้ว — ผูกกลับ ไม่ใช่ก้อนลอย
- term-of-art อังกฤษ + ไทยวงเล็บครั้งแรก (นโยบาย §8) · มาตรฐาน style เดิม
- แต่ละกล่องต้องจบด้วย "ใช้ทำอะไรกับเล่มนี้" (เชื่อมกลับ Part ที่เกี่ยวข้อง)

## Standard textbooks (canon, ยืนยันแล้ว)
- O'Hara (1995) Market Microstructure Theory · Harris (2003) Trading and Exchanges · Hasbrouck (2007) Empirical Market Microstructure · Foucault-Pagano-Röell (2013) Market Liquidity · Bouchaud-Bonart-Donier-Gould (2018) Trades, Quotes and Prices · Cartea-Jaimungal-Penalva (2015) Algorithmic & HF Trading · Guéant (2016) Financial Mathematics of Market Liquidity

## 7 กล่องที่จะเติม (ทั้งสองทีมจัดอันดับ)

1. **Part 9 — Resting limit order = short option** (Copeland-Galai 1983; Glosten 1994; Bouchaud ch.17–18)
   - แก่น: วาง limit = เขียน free option ให้ฝั่งที่รู้มากกว่า; ฟิลตอนตลาดวิ่งผ่าน = ฟิลตอนเราผิดพอดี ("you get the trades you don't want")
   - EV(MM) = spread capture − adverse-selection cost − inventory cost
   - เชื่อม: เหตุผลที่ grid (Part 12) / A-S (Part 10) เจ๊งตอนเทรนด์

2. **Part 3 — Roll (1984) model: efficient price + bid-ask bounce**
   - แก่น: P_obs = m_t (random walk) + bounce; Spread = 2√(−Cov(Δp_t, Δp_{t−1}))
   - เป็น "พ่อแม่" ของ 3-way decomposition ที่ตามมา; วาง box เปิด Part 3

3. **ภาคสถิติ — microstructure noise / volatility signature plot**
   - แก่น: sample ถี่เกิน → realized variance พองเพราะ bounce ครอบงำ; σ ที่วัดได้ ≠ σ ของ efficient price
   - เชื่อม: σ ผิด → A-S (Part 10) / grid spacing (Part 12) / backtest (Part 11) เพี้ยน

4. **Part 9 (หรือ Part 3) — make/take fee + queue-position economics** (Harris; Bouchaud priority/tick)
   - แก่น: EV(limit) = P(fill)·(½spread + rebate) − P(adverse fill)·adverse cost − queue-wait cost; priority คือสินทรัพย์
   - เชื่อม: PnL ของ grid/MM (Part 9–12), post-only/rebate (Part 11)

5. **Part 7 — propagator / transient impact + order-flow long memory** (Bouchaud ch.10–14; Lillo-Farmer)
   - แก่น: impact เป็น transient (kernel สลายตัว); signed flow เป็น long-memory เพราะ order splitting; สองอย่างสมดุลให้ราคา ~martingale
   - เชื่อม: กลไกใต้ √-law (Part 7) + เตือนว่า CVD/OFI persistence ส่วนหนึ่งคือ splitting ไม่ใช่ informed (Part 6)

6. **Part 14 (หรือ 13) — Hasbrouck (1995) Information Share + Gonzalo-Granger**
   - แก่น: หลาย venue แชร์ efficient price ร่วม (cointegration) → IS = สัดส่วน variance ของ efficient-price innovation ที่แต่ละ venue สร้าง = ใครนำ price discovery
   - เชื่อม: ฐานวัด lead-lag ของ cross-exchange arb (Part 14) / stat-arb (Part 13): perp นำ spot ไหม?

7. **Part 7 (หรือสถิติ) — Amihud (2002) ILLIQ**
   - แก่น: ILLIQ = mean(|return| / dollar volume) = price move ต่อดอลลาร์ที่เทรด = Kyle's λ ฉบับข้อมูลรายวัน
   - เชื่อม: คัด/จัดอันดับสภาพคล่องเหรียญด้วย OHLCV รายวัน (ไม่ต้องมี L2 feed) — เครื่องมือ universe-selection

## Phasing
1. เขียน 7 กล่อง (ผม=หัวหน้าทีมเขียนเองเพื่อความแม่นคณิต)
2. regen PDF + spot-check overlap ทุกไฟล์ที่แตะ
3. อัปเดต references ในแผนแม่บท (orderbook-blueprint.md §6) เพิ่มตำรา 7 เล่ม + เปเปอร์ใหม่
4. rebuild ob-book + zip · commit/push

## ความซื่อสัตย์
- ทฤษฎีพวกนี้คือ "ทำไมมันเป็นแบบนั้น" — รายย่อยใช้เป็นกรอบคิด/เครื่องมือคัดกรอง ไม่ใช่สูตรรันเรียลไทม์
- Hasbrouck IS / propagator = งานระดับ research; เราให้สัญชาตญาณ + สูตรแก่น ไม่ลงลึก estimation เต็มรูป
