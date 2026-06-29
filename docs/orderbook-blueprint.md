# แผนแม่บท — หนังสือ "อ่านกระดาน (Reading the Book)"
## Order Flow & Microstructure สำหรับรายย่อย

> เอกสารนี้คือ **แผนแม่บท (master blueprint)** ที่สังเคราะห์จากทีมผู้เชี่ยวชาญ 4 ด้าน
> ใช้เป็นพิมพ์เขียวก่อนลงมือเขียน HTML→PDF จริง (สไตล์เดียวกับซีรีส์ math/pm/arb/eye)

---

## 1. อัตลักษณ์ & ตำแหน่งของเล่ม

- **Prefix ไฟล์:** `ob-partN.html` → `ob-partN.pdf`
- **ภาษา:** ไทย | **ฟอนต์:** Sarabun | **รูปแบบ:** PDF-first (A4, สร้างด้วย `generate-pdf.js`)
- **ตลาดตัวอย่างหลัก:** คริปโต (Binance/Bybit — order book L2 + trade stream ฟรีผ่าน WebSocket/REST)
- **positioning:** เป็น "เลนส์ execution & microstructure" ของซีรีส์
  - `payoff/pm` → เทรด **อะไร** | `arb` → หา **โอกาส** | `math` → **เครื่องคิด** | `eye` → **mindset**
  - **เล่มนี้ → เทรด *ตรงไหน / เมื่อไหร่ / ต้นทุนจริงเท่าไหร่*** (จิ๊กซอว์ที่ซีรีส์ยังขาด)
- **คำวางตำแหน่ง:** order book = **เครื่องมือ 1 ชิ้น** ที่ให้ indicator ตระกูลใหม่ (ดู *แรงซื้อขายจริง* แทน *เงาราคา*) — แม่นระยะสั้น อายุสั้น ใช้คู่ risk management ไม่ใช่ระบบเบ็ดเสร็จ

---

## 2. มาตรฐานกลาง (ใช้ทุก Part เพื่อความต่อเนื่องของซีรีส์)

### 2.1 Design tokens (ตรงกับ math-part*.html)
- สี: `--green #16a34a` (bid/provide/ดี), `--red #dc2626` (ask/consume/เตือน), `--blue #2563eb` (คีย์/เชื่อมเล่ม), `--amber #d97706` (ข้อสังเกต) + เทา `--g0..g9`
- กล่อง: `.bg`(เขียว), `.br`(แดง=กับดัก), `.bb`(ฟ้า=คีย์/cross-ref), `.ba`(เหลือง=ข้อสังเกต/งานวิจัย) + หัวกล่อง `.bt`
- สูตร: `.fm` (Courier mono, พื้นเทา) | ตาราง: header ฟ้า + zebra
- Cover: `.cover` + `.sub` + `.desc`

### 2.2 ระบบภาพประกอบ (inline SVG, schematic วาดมือ, ≤500px)
- **เทมเพลตแม่ = "ภาพ 0.1 กระดาน LOB"** → bid เขียวซ้าย / ask แดงขวา / mid เส้นประกลาง / spread ลูกศรสองหัว
- ภาพอื่นที่ต่อยอดจากเทมเพลตแม่: 1.3, 2.1, 2.3, 3.2, 4.2, 5.1, 7.1, 9.1, 10.1, 12.1, 14.1
- โทนสีมาตรฐาน: bid/provide=เขียว, ask/consume/เตือน=แดง, คีย์=ฟ้า, ข้อสังเกต=เหลือง
- **แนะนำ:** วาดเทมเพลตแม่เป็น component กลางก่อน แล้ว reuse

### 2.3 โครงทุก Part (8 บล็อกตายตัว)
1. เป้าหมายการเรียนรู้ → 2. ฮุก/อุปมามือใหม่ → 3. เนื้อหาแกนเป็นชั้น (ง่าย→ลึก) →
4. สูตร `.fm` → 5. ภาพประกอบ 2–3 ภาพ → 6. กล่อง "งานวิจัยล่าสุด" →
7. เชื่อมโยงเล่มอื่น `.bb` → 8. กับดักมือใหม่ + แบบฝึก (ทำได้ด้วยข้อมูลคริปโตฟรี)

### 2.4 ⚠️ รายการที่ต้อง verify ก่อนตีพิมพ์
- ตัวเลข **R² ~65%** ของ OBI → ขึ้นกับตลาด/timeframe (ใส่กล่อง `.ba` กำกับ)
- **continuation ~84%** เมื่อคิวหมดด้วย market order (Lu-Abergel 2018) → ตรวจกับ paper ต้นฉบับ
- โครงสร้าง **fee/rebate** Binance/Bybit → เปลี่ยนตามโปรโมชัน ให้ผู้อ่านเช็คหน้า fee schedule
- นิยาม **OFI** ใช้เวอร์ชัน event-based ที่ best level (Cont-Kukanov-Stoikov)

**สถานะ polish pass (รอบล่าสุด):**
- ✅ สูตร Avellaneda-Stoikov (reservation price + optimal spread) และ arXiv IDs ทั้งหมด — verified ตรงต้นฉบับ
- ✅ ตัวเลขที่ดู "เหมือนผลวิจัย" เปลี่ยนเป็นเชิงคุณภาพ/กำกับว่าสาธิต: ภาพ 7.3 (R²) → "ต่ำกว่า/สูงกว่า", ภาพ 13.3 (เมทริกซ์ γ) → กำกับ "ตัวเลขสาธิต"
- ✅ R²~65% / continuation~84% มีกล่อง `.ba` กำกับ "ขึ้นกับ calibration/ตลาด" ทุกจุด
- ⏳ คงเหลือ: **fee/rebate** ให้ผู้อ่านเช็ค fee schedule จริง (เลี่ยงระบุเลขตายตัวโดยเจตนา)

---

## 3. สารบัญแม่บท (5 องก์ · 15 ตอน)

| องก์ | Part | ชื่อ | คำถามนำ |
|---|---|---|---|
| **I. รากฐาน** | 0 | กระดานคืออะไร | "ราคา" จริง ๆ มาจากไหน |
| | 1 | กายวิภาคของคิว | ทำไม "อยู่ต้นคิว" มีค่า |
| | 2 | 3 เหตุการณ์ที่ขยับกระดาน | อะไรทำให้กระดานเปลี่ยน |
| **II. Spread & ความน่าเชื่อถือ** | 3 | Bid-Ask Spread แยกส่วน | ทำไมช่องว่างสองฝั่งกว้างเท่านี้ |
| | 4 | กระดานเชื่อถือได้แค่ไหน/นานแค่ไหน | เชื่อสิ่งที่เห็นได้แค่ไหน |
| **III. อ่าน Flow** | 5 | Order Book Imbalance (OBI) | ฝั่งไหนหนัก (ภาพนิ่ง) |
| | 6 | ทำไม Market Order สำคัญ | ใครมีข้อมูล |
| | 7 | Order Flow Imbalance & Price Impact | flow ดันราคายังไง (Kyle's λ) |
| | 8 | VPIN / ความเป็นพิษของ flow | flow อันตรายแค่ไหน |
| **IV. Market Making** | 9 | MM-1 พื้นฐาน + inventory + fee | กินสปรดยังไง |
| | 10 | MM-2 Optimal (Avellaneda-Stoikov→RL) | วาง quote ตรงไหนถึง optimal |
| | 11 | MM-3 ลงมือจริงคริปโต + กับดัก backtest | จาก quote สู่ระบบรันได้ |
| **V. Advanced** | 12 | Grid Trading กับกระดาน | ยกระดับ grid ด้วยกระดาน |
| | 13 | Statistical Arbitrage ด้วย OFI | ทำนายราคาด้วย flow |
| | 14 | Cross-Exchange / Latency / Triangular Arb | arb จริงทำได้แค่ไหน |
| | โบนัส | เครื่องจักรอ่านกระดาน (DeepLOB/Transformers) | ปลายทาง ML |
| **ภาคเครื่องมือ** | สถิติ | ทบทวนสถิติพื้นฐานสำหรับ Order Flow (mean/median/mode, variance/SD, z-score, t-score, normal & t-dist) | อ่านก่อน Part 5–11 ถ้าสถิติไม่แน่น |

**เส้นเรื่องหลัก:** ราคาสองฝั่ง → คิว → เหตุการณ์ → spread → ความน่าเชื่อถือ → **static (OBI) → flow (OFI) → toxicity (VPIN)** → market making → ประยุกต์ (grid/arb) → ML

---

## 4. แผนผังอ้างอิงข้ามเล่ม

```
math (regression/PCA/log) ──► Part 7 (Kyle's λ=OLS slope, multi-level OFI=PCA), 13 (log-OFI), โบนัส (softmax)
ob (execution timing) ──────► pm/payoff (เข้า-ออกให้ได้ราคาดี, คิด P&L/inventory)
ob (adverse selection) ─────► eye (อ่าน flow = ใครมีข้อมูล)
ob (effective price/depth) ─► arb (ต้นทุนจริงของ arb = สะพานเชื่อม Part 14)
```

---

## 5. บลูพรินต์รายตอน (สรุปจากทีมผู้เชี่ยวชาญ)

### องก์ I — รากฐาน (Part 0–4)

**Part 0 · กระดานคืออะไร** — อุปมา: ร้านทอง 2 ป้ายราคา
- แกน: bid/ask/spread/mid, order-driven vs quote-driven, "ไม่มีราคาเดียว"
- สูตร: `Spread=Ask−Bid`, `Mid=(Ask+Bid)/2`, `Spread(bps)=Spread/Mid×10000`
- ภาพ: 0.1 กระดาน LOB (เทมเพลตแม่), 0.2 ร้านทอง, 0.3 order-driven vs quote-driven
- กับดัก: เอา last price คิดกำไรแล้วลืม spread | แบบฝึก: คำนวณ spread(bps) BTC vs เหรียญเล็ก

**Part 1 · กายวิภาคของคิว** — อุปมา: คิวซื้อ iPhone
- แกน: คิวในหนึ่งราคา, price-time priority (FIFO), tick/depth, queue value (ต้นคิว=ได้ fill ก่อน)
- สูตร: `Queue=Σปริมาณที่ราคา P`, `Depth(N)`, P(fill) ขึ้นกับ volume>Q_ahead
- ภาพ: 1.1 คิว zoom-in, 1.2 priority decision tree, 1.3 depth profile 5 ชั้น
- กับดัก: เชื่อว่า limit=ชัวร์ (ลืม queue risk) | แบบฝึก: จับ `@depth` ดูคิวขยับ 10 วินาที

**Part 2 · 3 เหตุการณ์** — อุปมา: เติม/เอาออก/หยิบของชั้นซูเปอร์
- แกน: Limit(provide)/Cancel/Market(consume), maker vs taker, walk the book/slippage, event flow
- สูตร: `AvgFill=Σ(p·q)/Σq`, `Slippage=AvgFill−BestAsk`
- ภาพ: 2.1 ก่อน/หลัง 3 เหตุการณ์, 2.2 maker vs taker, 2.3 walk the book
- กับดัก: market order บนเหรียญบาง→ดันราคาตัวเอง | แบบฝึก: คำนวณ slippage market buy $5000

> **กล่องสรุป `.bb` — Maker / Taker / Market Order: ใช้อันไหนเมื่อไหร่** (หัวใจของ Part 2)
>
> | มิติ | Limit (Maker) | Market Order (Taker) |
> |---|---|---|
> | ทำอะไร | วางคำสั่งรอที่ราคาที่เลือก | สั่งซื้อ/ขายทันทีที่ราคาดีสุดที่มี |
> | บทบาทสภาพคล่อง | **ให้ (provide)** เติมของเข้ากระดาน | **กิน (consume)** หยิบของออก |
> | ค่าธรรมเนียม | maker fee ต่ำ / บางที่ได้ **rebate** | taker fee สูงกว่า + จ่าย **spread** |
> | ความเร็ว/ความแน่นอน | อาจไม่ได้ fill (queue risk) | fill ทันที (แต่เสี่ยง slippage) |
> | ความเสี่ยงหลัก | **adverse selection** (โดนคนรู้ข้อมูลกิน) | **slippage / walk the book** |
> | เหมาะเมื่อ | ไม่รีบ, อยากได้ราคาดี, เป็น MM/grid | รีบ, ต้องการความแน่นอน, ปิดด่วน/hedge |
> | "มีข้อมูล" ไหม | สัญญาณอ่อน (ตั้งรอ ยกเลิกฟรี) | **informative** (ยอมจ่ายเพื่อได้ทันที → Part 6) |
>
> *หมายเหตุ:* **Cancel** เป็นเหตุการณ์ที่สาม (ถอน limit ออก = ลดสภาพคล่อง ไม่มีเงินเปลี่ยนมือ) — ไม่ใช่ maker/taker แต่เป็นส่วนของ event flow ที่ขยับกระดาน
> *post-only* (Part 11) = limit order ที่ยกเลิกอัตโนมัติถ้าจะกลายเป็น taker → การันตีเป็น maker เสมอ

**Part 3 · Spread แยกส่วน** — อุปมา: ร้านแลกเงินสนามบิน
- แกน: 3 ก้อนต้นทุน (order processing + inventory + **adverse selection**), ปัจจัยกว้าง/แคบ (tick, volatility, volume, การแข่งขัน MM, เวลา/ข่าว)
- สูตร: `Spread=Processing+Inventory+AdverseSelection`, `EffSpread=2×|P_trade−Mid|`
- ภาพ: 3.1 stacked bar 3 ก้อน, 3.2 spread กว้าง/แคบ 2 สถานการณ์, 3.3 informed vs noise trader
- กับดัก: เทรดเหรียญเล็กช่วงตลาดเงียบ | แบบฝึก: plot spread(bps) ราย 24 ชม. เทียบเวลาข่าว US

**Part 4 · ความน่าเชื่อถือ** — อุปมา: ผิวน้ำทะเล (คลื่นจริง vs ฟองลวง)
- แกน 4 มิติ: signal horizon (อายุวินาที), depth-at-touch vs deep, **spoofing/fleeting liquidity**, resiliency/refill
- สูตร: `OBI=(BidVol−AskVol)/(BidVol+AskVol)`, ธงเตือน spoof (ก้อนใหญ่+ห่าง best+cancel เมื่อราคาใกล้)
- ภาพ: 4.1 signal horizon (แกน log), 4.2 spoof 3 เฟรม, 4.3 resiliency timeline
- กับดัก: เชื่อ "กำแพง" เป็นแนวรับจริง (spoof) | แบบฝึก: จับออเดอร์ก้อนใหญ่ที่หายก่อนราคาแตะ

### องก์ II–III — Order Flow (Part 5–8)
**เส้นเรื่อง: static(OBI) → flow(OFI) → toxicity(VPIN)**

**Part 5 · OBI** — อุปมา: นับหัวคนชักเย่อ (ยืนอยู่ ≠ ลงมือ)
- แกน: OBI best/multi-level, R²~65% (กำกับว่าขึ้นกับตลาด), **OBI=ภาพนิ่ง ไม่ใช่ flow**, spoof หลอกได้
- **= "Volume Imbalance" ในศัพท์เทรดเดอร์** (queue imbalance ทางวิชาการ) → มี paper รองรับตรง: **Gould & Bonart (2015)** ทำนายทิศ mid-price ถัดไปได้ดี โดยเฉพาะ large-tick
- สูตร: `OBI=(V_bid−V_ask)/(V_bid+V_ask)` (สเกล −1..+1, กลาง=0), OBI_N depth-weighted
  - *เวอร์ชันสเกล 0..1:* `Imbalance=V_bid/(V_bid+V_ask)` (กลาง=0.5) → แปลงกัน `OBI=2×Imbalance−1`; **เลือกใช้อันเดียวให้ทั้งเล่มสม่ำเสมอ**
- ภาพ: 5.1 เชือกชักเย่อ, 5.2 OBI ทับ mid (มี false signal จาก cancel), 5.3 spoof wall 3 เฟรม
- กับดัก: OBI≠ทิศนาทีถัดไป (แค่วินาที) | แบบฝึก: คำนวณ OBI best vs 5 ชั้นจาก REST depth

**Part 6 · ทำไม Market Order สำคัญ** — อุปมา: ใครยอมจ่ายแพงเพื่อได้เดี๋ยวนี้ มักรู้อะไร
- แกน: market>cancel (informativeness), **adverse selection**, **non-Markovian** (คิวหมดเพราะ M→follow ~84% / เพราะ C→revert)
- **Delta (Δ) & Cumulative Delta (CVD)** — เครื่องมือวัดได้จริงของ "แรง market order": Δ = Buy vol − Sell vol (ของที่เทรดไปแล้ว, aggressor), CVD = running sum ของ Δ → trend แรงซื้อ/ขายสะสม
- สูตร: `Δ=BuyVol−SellVol`, `CVD_t=Σ Δ`, signed volume classification, `กำไร limit = ครึ่ง spread − E[adverse move|fill]`
- ภาพ: 6.1 สามเหตุการณ์ใครมีข้อมูล, **6.2 คิวหมด M vs C → follow/revert (ภาพหัวใจ)**, 6.3 adverse selection 2 ช่อง, 6.4 Δ/CVD แท่งเขียว-แดง + เส้น CVD สะสม
- กับดัก: เห็น best หมดคิวแล้วเดาทิศทันที (ต้องดูสาเหตุ); **CVD divergence ≠ กลับตัวเสมอ** (ระวัง absorption); aggressor ต้องจำแนกถูก (ใช้ flag `m` ของ Binance) | แบบฝึก: ติดป้าย buy/sell 200 trade เทียบทิศ mid + plot CVD

> **กล่อง `.bb` — Binance-ready Orderflow Toolkit (ผูกศัพท์เทรดเดอร์ ↔ ศัพท์วิชาการ ↔ paper)**
>
> | ศัพท์เทรดเดอร์ | ศัพท์วิชาการ | วัดอะไร | Paper รองรับ |
> |---|---|---|---|
> | **Delta (Δ)** | Trade imbalance / signed volume | flow ที่เทรดไปแล้ว (taker) | Lee & Ready (1991); Chordia-Subrahmanyam (2004) |
> | **Cumulative Delta (CVD)** | Cumulative signed order flow | trend แรงซื้อ/ขายสะสม | Chordia-Roll-Subrahmanyam (2002) |
> | **Volume Imbalance** | Queue / order-book imbalance | state ของ depth ที่ตั้งรอ | Gould & Bonart (2015) |
>
> **Nuance จากงานวิจัย (ใส่ `.ba`):** (1) **OFI > Trade Imbalance** — Δ/CVD ใช้ได้ดี แต่ OFI (Part 7) รวม cancel/limit ด้วย จึงมีข้อมูลมากกว่า → ชี้ทางอัปเกรด; (2) พลังทำนาย **เสื่อมตามเวลา** → ตอกย้ำ signal horizon สั้น (Part 4)

**Part 7 · OFI & Price Impact** — อุปมา: OBI=ภาพนิ่ง / OFI=วิดีโอการเปลี่ยน
- แกน: **OBI(state) vs OFI(flow)** (ตารางเทียบ), OFI event-based, Kyle's λ=OLS slope, **multi-level OFI (Cont 2023, PCA)**, stationarize
- สูตร: OFI ที่ best (3 กรณีราคาขึ้น/เท่า/ลง), `ΔP=λ·OFI+ε`, integrated OFI=PCA, `OFI_norm=OFI/DepthBar`
- ภาพ: 7.1 OBI vs OFI, **7.2 scatter ΔP vs OFI + เส้น regression=λ (ภาพสำคัญ)**, 7.3 bar R² best vs multi-level
- เชื่อม math: λ=Cov(ΔP,OFI)/Var(OFI), R², PCA | แบบฝึก: regress ΔP~OFI vs ΔP~OBI ดู R²

**Part 8 · VPIN** — อุปมา: นาฬิกาเดินตามปริมาณ ไม่ใช่เวลา
- แกน: **volume clock**, bulk volume classification, toxicity=adverse selection รวม, เตือน crash (+ ข้อโต้แย้ง calibration)
- สูตร: 1 bucket=ปริมาณ V คงที่, `V_buy=V·Z(ΔP/σ)`, `VPIN=(1/nV)Σ|V_buy−V_sell|`
- ภาพ: 8.1 clock time vs volume clock, 8.2 volume buckets กลไก, 8.3 VPIN เตือนก่อน crash
- กับดัก: ใช้ VPIN เป็นปุ่มทำนาย crash / ใช้เวลานาฬิกาคำนวณ | แบบฝึก: VPIN rolling จาก aggTrade 1 ชม.

### องก์ IV — Market Making (Part 9–11)

**Part 9 · MM-1 พื้นฐาน** — อุปมา: ร้านแลกเงินสนามบิน (inventory risk = ลิ้นชักเต็ม)
- แกน: กินสปรด, maker vs taker + **rebate คริปโต**, inventory risk, สัญชาตญาณ skew
- สูตร: `PnL_spread=(ask−bid)+rebate`, `bid_skew=mid−δ/2−k·q` / `ask_skew=mid+δ/2−k·q`, `PnL_inv=q·Δp`
- ภาพ: 9.1 กลไกกินสปรด, 9.2 inventory สะสมเมื่อ flow ไม่สมดุล, 9.3 skew quote (เชื่อม Part 10)
- กับดัก: คิดว่าสปรดกว้าง=ปลอดภัย (จริง=จัดการ inventory) | แบบฝึก: จำลอง fill 7 bid/3 ask หา inventory+PnL

**Part 10 · MM-2 Optimal** — อุปมา: ราคายุติธรรมในใจพ่อค้าขายร่ม (ขยับตามสต็อก)
- แกน: **reservation price**, optimal spread ถ่วง inventory/σ/(T−t), adverse selection (naive ตาย), value function, **→ ยุค RL**
- สูตร: **`r=s−q·γ·σ²·(T−t)`**, `δ_total=γσ²(T−t)+(2/γ)ln(1+γ/κ)`, `bid=r−δ/2 ask=r+δ/2`, RL: `max E[Σ(PnL−λq²)]`
- ภาพ: 10.1 reservation price ถูกดึงจาก mid, **10.2 P&L optimal vs naive (เด่น)**, 10.3 timeline Ho-Stoll→A-S→Guéant→RL
- เชื่อม math (HJB/optimize), pm (risk-adjusted payoff) | แบบฝึก: โค้ดคำนวณ r+quote, ทดลอง q=+10 vs −10

**Part 11 · MM-3 ลงมือจริง** — อุปมา: backtest = กระจกห้องลองเสื้อ (สวยเกินจริง)
- แกน: MM loop, WebSocket L2+trade, microprice, inventory limit+kill switch, **กับดัก backtest 3 ข้อ** (fill assumption/latency/market impact)
- สูตร: `microprice=(p_bid·V_ask+p_ask·V_bid)/(V_bid+V_ask)`, `PnL_net` (หัก fee/taker), `AFR=adverse fills/total`
- ภาพ: 11.1 MM loop diagram, **11.2 backtest สวย vs ความจริง (เด่น)**, 11.3 บันได backtest→paper→live
- กับดัก: เชื่อ backtest กราฟสวยแล้วเทเงินจริง | แบบฝึก: หา "fill assumption อันตราย" ใน pseudo-code + จำลอง latency

### องก์ V — Advanced (Part 12–14 + โบนัส)

**Part 12 · Grid Trading** — อุปมา: ตาข่ายจับปลาหลายชั้น (น้ำหลาก=กริดแตก)
- แกน: grid=MM กฎตายตัว, **เอียง grid ด้วย OBI/OFI**, **VPIN หยุด grid กันแตก**, spacing ไดนามิก
- สูตร: `Δ_grid=max(c1·spread̄, c2·σ·√τ)`, `P_center'=P_mid+α·OBI·Δ_grid`, VPIN>θ→ระงับไม้ทวนเทรนด์
- ภาพ: 12.1 grid ladder, 12.2 เอียง grid ตาม imbalance, 12.3 VPIN หยุด grid
- กับดัก: กริดเด้งบ่อยแต่กำไร<fee×2 / เทรนด์เดียวล้างพอร์ต | แบบฝึก: จำลอง grid วัน sideway vs trending หัก fee

**Part 13 · Stat-Arb ด้วย OFI** — อุปมา: แรงดันน้ำในท่อ (มาก่อนระดับน้ำ) / ท่อต่อกัน=cross-asset
- แกน: mean reversion, OFI predictor, **log-OFI/stationarize**, **cross-impact→cross-asset** (BTC→ETH)
- สูตร: `ofi=sign·log(1+|OFI|)/D`, `Δp_i=β·ofi_i+Σγ_ij·ofi_j+ε`, เข้าเมื่อ |Δp̂|>cost
- ภาพ: 13.1 OFI นำหน้าราคา, 13.2 stationarize ก่อน/หลัง, 13.3 cross-asset เมทริกซ์ γ
- กับดัก: OFI ดิบ→regression spurious / edge ต่อไม้เล็กมาก | แบบฝึก: regress Δp(ETH)~ofi(ETH)+ofi(BTC)

**Part 14 · Cross-Exchange/Latency/Triangular Arb** — อุปมา: ซื้อทุเรียนตลาด A ขายตลาด B (ค่ารถ+เวลาขน)
- แกน: 3 ชนิด arb, **depth ข้าม venue (effective price)**, ต้นทุนครบวงจร, **ตารางความจริงรายย่อย**
- สูตร: `Π_net=(P_sell,B−P_buy,A)−fee−w_withdraw−slip`, `P_eff(Q)=Σp_k·q_k/Q`, triangular `R>1`
- ภาพ: 14.1 cross-exchange 2 venue+หัก fee, 14.2 effective price ไต่เล่ม, 14.3 triangular+ตารางความจริง
- **ตารางความจริงรายย่อย:** latency ❌(HFT) / cross-exchange spot ⚠️ / triangular ⚠️ / **OFI stat-arb ✅ เหมาะสุด**
- กับดัก: spread บนจอ≠กำไร / latency arb อย่าลอง | แบบฝึก: P_eff 2 exchange หัก fee นับช่วง Π_net>0

**Part โบนัส · เครื่องจักรอ่านกระดาน** — อุปมา: สายตาฝึกดูล้านครั้ง / ยอดภูเขา ไม่ใช่ค่ายฐาน
- แกน: DeepLOB (CNN+LSTM), Transformer (TLOB/LiT), **"feature ดี > โมเดลลึก"**, **ML=ปลายทางไม่ใช่จุดเริ่ม**
- สูตร: `X∈R^{T×4L}`, label mid-move 3 class, `min CrossEntropy(softmax(f(X)),y)`
- ภาพ: B.1 pipeline LOB→CNN→LSTM→prediction, B.2 feature>depth bar, B.3 ยอดภูเขา
- กับดัก: ทุ่ม architecture แทน feature/ข้อมูล / ไม่กัน overfit | แบบฝึก: logistic regression + feature OFI vs เดาตาม sign(OFI)

---

## 6. แหล่งอ้างอิง (timeline 1985–2025)

- **รากฐาน:** Glosten-Milgrom (1985), Kyle (1985), Ho-Stoll (1981), Stoll (spread components)
- **Trade/Queue imbalance (Delta/CVD/Volume Imbalance):** Lee & Ready (1991, trade classification), Chordia-Roll-Subrahmanyam (2002), Chordia-Subrahmanyam (2004, order imbalance→returns), **Gould & Bonart (2015, queue imbalance one-tick-ahead predictor, arXiv 1512.03492)**
- **OFI/impact:** Cont-Kukanov-Stoikov (2014), **Cont-Cucuringu-Zhang (2023) cross-impact multi-level OFI**, Generalized OFI (arXiv 2112.02947), HF Stat-Arb Stationarized OFI
- **Toxicity:** Easley-López de Prado-O'Hara (2012, VPIN), Nowcasting Bitcoin crash with order imbalance
- **Queue/non-Markovian:** Lu-Abergel (2018), Queue-Reactive Hawkes (arXiv 1901.08938), Importance of Order Sizes (arXiv 2405.18594)
- **Market Making:** Avellaneda-Stoikov (2008), Guéant-Lehalle-Fernandez-Tapia (2013), MM under Weakly Consistent LOB (arXiv 1903.07222), Dynamic Modeling LOB/HJB (MDPI 2025)
- **RL MM:** Market Making with Deep RL from LOB (arXiv 2305.15821), Gašperov-Kostanjčar (Hawkes), Resolving Latency & Inventory Risk (arXiv 2505.12465), RL on Non-Stationary LOB (arXiv 2509.12456)
- **ML/Crypto:** DeepLOB (arXiv 1808.03668), TLOB (arXiv 2502.15757), LiT (Frontiers), Exploring Microstructural Dynamics in Crypto LOBs (arXiv 2506.05764)

---

## 7. ลำดับการสร้าง (Phasing)

1. **เฟส 1 (รากฐาน):** Part 0–2 + วาดเทมเพลตแม่ SVG (พิสูจน์ว่าเข้าชุดซีรีส์เป๊ะ)
2. **เฟส 2 (Spread+Flow):** Part 3–8
3. **เฟส 3 (Market Making):** Part 9–11
4. **เฟส 4 (Advanced+ML):** Part 12–14 + โบนัส
5. รวม `ob-all.zip` + อัปเดต index/บันเดิล

> หมายเหตุ: ก่อนตีพิมพ์ ตรวจรายการใน §2.4 (ตัวเลข R²/continuation, fee schedule)

---

## 8. รายการรอเพิ่ม (Pending — รวบเพิ่มทีเดียวภายหลัง)

> ยังไม่ลงมือ · บันทึกไว้เพื่อทำเป็น batch เดียว แล้ว regen เล่มรวมทีเดียว

### 8.1 นิยาม "Market Microstructure" (ใส่ Part 0)
- **สถานะปัจจุบัน:** คำนี้อยู่บนปกทุกตอน + เอ่ยใน Part 3 (spread 3 ก้อน) และ Part โบนัส (ภูเขา "ค่ายฐาน") แต่ **ยังไม่เคยนิยามศัพท์ให้มือใหม่**
- **จะเพิ่ม:** กล่อง `.bb` ใน Part 0 — "market microstructure = วิชาที่ศึกษา *กลไกการเกิดราคา/การซื้อขายระดับจุลภาค* (ราคาเกิดจากการจับคู่คำสั่ง) ต่างจาก macro/ปัจจัยพื้นฐาน · ทั้งเล่มนี้คือ microstructure ฉบับปฏิบัติสำหรับรายย่อย" + อ้างราก Glosten-Milgrom / Kyle / O'Hara

### 8.2 ชั้น "การแปลผล (Interpretation)" — อ่านพฤติกรรมจากกระดาน
รวมการตีความสัญญาณให้เป็นชั้นเดียวที่ชัดขึ้น (ปัจจุบันกระจายใน Part 1/2/3/4/6 ยังไม่รวมศูนย์):
- **bid-ask spread เปลี่ยน** (กว้างขึ้น/แคบลง) → แปลว่าอะไร (ต่อยอด Part 3/4 — ทำตาราง "เห็นแบบนี้ = อาจหมายถึง")
- **ลำดับคิว order ขยับ** (คิวสั้นลง / หายทั้งชั้น / เติมกลับเร็ว-ช้า) → แปลผล (ต่อยอด Part 1 queue + Part 4 resiliency)
- **⭐ MM ถอน bid/ask (pull quotes)** → สัญญาณอะไร:
  - ถอน **สองฝั่ง** = MM หลบความเสี่ยง / ก่อนข่าว / flow เป็นพิษ (โยง VPIN Part 8) → spread กว้าง สภาพคล่องหด
  - ถอน **ฝั่งเดียว** = เอียงมุมมอง/สะสม inventory ฝั่งนั้น (โยง skew Part 9–10)
  - ต่างจาก **spoof** (ตั้งกำแพงหลอกแล้วถอนก่อนโดนแตะ — Part 4)
  - เชื่อม Part 2 (cancel = ถอนสภาพคล่อง) + Part 6 (คิวหมดเพราะ cancel → มัก revert)
- **ตำแหน่งที่จะวาง:** กล่อง/หัวข้อใหม่ "อ่านพฤติกรรม Market Maker" — เหมาะใน **Part 4** (ความน่าเชื่อถือ) หรือ **Part 9** (MM) + ภาพ schematic "MM ถอน quote 2 ฝั่ง vs ฝั่งเดียว vs spoof"

### 8.3 หมายเหตุการ implement
- ทำ 8.1 + 8.2 พร้อมกัน → regen Part 0/4/9 (+ส่วนที่แตะ) → rebuild `ob-book.pdf` + `ob-all.zip` → cross-review รอบสั้น (legibility + ความถูกต้องของการตีความ) ก่อน commit
