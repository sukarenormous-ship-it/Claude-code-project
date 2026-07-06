# แผนนำงานวิจัยมาเสริม Grid Trading Mastery — "ขยายของเดิม ไม่ตัดแปะ"

> หลักการคัด: paper ต้องผ่านอย่างน้อย 1 ใน 3 เกณฑ์ — (ก) **ยกระดับ**แนวคิดที่เล่มมีอยู่แล้วจาก rule-of-thumb เป็นทฤษฎีที่ derive ได้ (ข) **เติมช่องว่าง**ที่ทีมรีวิวชี้ (ดู grid-review-report.md) (ค) **เชื่อม**สิ่งที่เล่มแยกเป็นชิ้นๆ ให้เป็นระบบเดียว — ถ้าแค่ "เนื้อหาใหม่ที่น่าสนใจ" แต่ไม่ต่อกับของเดิม = ตัดทิ้ง
> อัปเดต: 2026-07-05

---

## ภาพรวม: 5 คลัสเตอร์ + 2 ที่จงใจไม่เอา

| # | Paper / แหล่ง | ต่อยอดอะไรในเล่ม | ลงบทไหน |
|---|---|---|---|
| A1 | Avellaneda & Stoikov (2008) — HFT in a limit order book | inventory risk ที่เล่มรู้ว่าเป็นจุดตายแต่จัดการแบบ passive | Part 2 + 1B |
| A2 | Guéant–Lehalle–Fernandez-Tapia (GLFT) + hftbacktest "GLFT & Grid Trading" | สูตร step/skew แบบ closed-form ต่อจาก step ≈ k×ATR | Part 3 |
| B1 | Leung & Li (2015), arXiv:1411.5062 — Optimal Mean Reversion Trading with Transaction Costs & Stop-Loss | สูตร Step = Half-Life×ATR/2 และ z-band ±2 ที่เล่มใช้แบบ fixed | Part 3 + 6 |
| C1 | MDPI Mathematics 2024 — Anti-Persistent Hurst Anticipates Mean Reversion (crypto pairs) | Hurst framework ของ Part 4 → ใช้เป็น entry signal ราย spread | Part 4 + 6 |
| C2 | Multi-Scale DFA, Physica A 2025 | warning box "R/S มี bias ใช้ DFA" ที่เล่มมีอยู่แล้ว | Part 4 |
| D1 | He, Manela, Ross, von Wachter (2024) — Fundamentals of Perpetual Futures (arXiv:2212.06888) | funding table ของ 1B/1C ที่ลอยอยู่ไม่มีทฤษฎีรองรับ | Part 1C + 7 |
| D2 | Designing Funding Rates (arXiv:2506.08573) + Ackerer et al., Math Finance 2025 | สมมติฐาน "funding ×3/วัน" ที่ hardcode ทั้งเล่ม | Part 1C + appendix |
| E1 | Busseti, Ryu & Boyd (2016) — Risk-Constrained Kelly | "25% fractional Kelly โดยศรัทธา" + DD ladder ที่แยกกันอยู่ | Part 5 |
| F1 | DGT (arXiv:2506.11921) | ✅ อยู่ใน grid-v2-plan.md แล้ว (zero-EV + migration) | Part 0 (ทำแล้ว) + 1D |
| F2 | Volatility-Induced Growth (Dempster, Evstigneev & Schenk-Hoppé 2007) + Volatility Harvesting (arXiv:1508.05241) | **ทฤษฎีว่าทำไม DGT ถึงชนะ** — ต่อจาก zero-EV ของ Part 0 | Part 0 + 1D |
| F3 | GTSbot (Rundo et al. 2019, Applied Sciences) — FX HFT grid + trend filter | หลักฐาน peer-reviewed ว่า grid+filter ลด DD ได้จริง (สนับสนุนปรัชญา "Grid คือ Grid") | Part 1D + 3B/7B |
| F4 | Jia (2022, ICEMME) — Feasibility of BTC grid via backtesting | sensitivity ของ yield ต่อ (upper, lower, N_up, N_down, initial position) — เติมตารางที่ Part 3 ไม่มี | Part 3 |
| F5 | Infinity Grid mechanism (KuCoin/Pionex spec + kraken-infinity-grid OSS) | รูปธรรมของ TREND_UP_MIGRATION ที่มีใช้จริงบน exchange | Part 1D + Exchange Reality |
| ✗ | RL-based grid optimization (หลายฉบับ 2024–25) | **จงใจไม่เอา** — ดูเหตุผลท้ายเอกสาร | — |
| ✗ | ML price prediction / GNN regime | **จงใจไม่เอา** | — |

---

## Cluster A — Grid คือ Market Making: ยกระดับ inventory risk เป็นกลไก active

**สิ่งที่เล่มมีอยู่:** เล่มรู้ดีว่า inventory คือจุดตาย (Part 0 กล่อง "เมื่อไหร่ Grid ล้มเหลว", Part 2 bloating ทั้งบท) แต่เครื่องมือทั้งหมดเป็น **passive**: รอ (Option A), ลด Q (Option B), hedge (Option C), halt — และทีมรีวิวพบว่าเกณฑ์เลือก Option ไม่มี (gap G5)

**สิ่งที่ paper เพิ่ม:** Avellaneda-Stoikov พิสูจน์ว่า market maker (ซึ่ง grid คือ subspecies หนึ่ง) ไม่ควรวาง quote สมมาตรรอบ mid price เมื่อถือ inventory — ต้องคำนวณ **reservation price** ที่เลื่อนหนีจาก inventory:

```
r(s,q,t) = s − q·γ·σ²·(T−t)        ← ราคา "กลาง" ที่แท้จริงเมื่อถือ q หน่วย
δ_bid + δ_ask = γσ²(T−t) + (2/γ)ln(1+γ/k)   ← ความกว้าง spread optimal
```

แปลเป็นภาษา grid: **ยิ่ง inventory หนัก center ของ grid ควรเลื่อนลง และฝั่ง buy ควรห่างขึ้น** — นี่คือคำตอบเชิงทฤษฎีของคำถามที่ Part 2 ตอบไม่จบ (เมื่อไหร่รอ/เมื่อไหร่ลด Q) และของ Step Pyramid ที่เล่มทำตามสัญชาตญาณอยู่แล้ว (เพิ่ม step เมื่อ H สูง = ลด fill โดยไม่รู้ตัวว่ากำลังทำ inventory skew แบบหยาบ)

**วิธีลง (ไม่ตัดแปะ):**
- Part 2 เพิ่ม section "2.x จาก Bloating สู่ Inventory Skew" — เริ่มจาก 3 Options เดิม แล้วแสดงว่าทั้งสามคือจุดพิเศษของสูตรเดียว: `bid_offset = base_step × (1 + λ·q/q_max)` (inventory-scaled) — ให้ q/q_max เป็น**เกณฑ์เลือก Option ที่หายไป**: q<30% → A, 30–70% → B (ผ่านสูตร), >70% → C
- Part 1B ใช้ reservation price อธิบายว่าทำไม short layer ต้องหด/ขยับเมื่อ long inventory โต — แทนที่กฎตายตัว "short ≤ 20% ของ long"
- ระดับความลึก: กล่องทฤษฎี + สูตรเดียว + ตัวอย่างตัวเลขจาก running example — **ไม่เอา HJB/stochastic control เข้าเล่ม** (อ้างอิงท้ายบทพอ)

**GLFT (A2):** เวอร์ชัน closed-form ที่ใช้กับ crypto ได้จริงและมี tutorial ที่ map เข้า grid trading ตรงตัว (hftbacktest) — calibrate order-arrival intensity A, k จาก trade data แล้วได้ half-spread optimal → ลง Part 3 เป็น "วิธีที่ 6" ของการตั้ง step: **step จาก fill intensity แทน ATR** พร้อมบอกชัดว่าเมื่อไหร่คุ้มที่จะใช้ (มี tick data + รัน calibration ได้) เมื่อไหร่ ATR rule พอ (มือใหม่) — เข้ากับหลัก Default Path ของรีวิวบรรณาธิการ

## Cluster B — Zone/Step/Stop จาก OU: ปิดวงจร Half-Life ที่เล่มเปิดไว้ครึ่งเดียว

**สิ่งที่เล่มมีอยู่:** สูตร `Step optimal = (Half-Life × ATR)/2` (Part 3 / CLAUDE.md), z-score ±2 เข้า ±4 หนี (Part 6, ยกจาก statarb book), และ "give-up point" ที่ทีม risk พบว่า**ไม่มี procedure จริง** (7 positions ไร้ exit rule)

**สิ่งที่ paper เพิ่ม:** Leung & Li ตั้งโจทย์เดียวกับที่ grid เจอทุกวันเป็น optimal double stopping บน OU: เข้าเมื่อไหร่ ออกเมื่อไหร่ วาง stop-loss ตรงไหน **โดยคิด transaction cost** — ผลหลักที่ใช้ได้ทันที: entry region เป็น **ช่วงจำกัดที่อยู่เหนือ stop-loss เสมอ** (ไม่ใช่ "ยิ่งลึกยิ่งซื้อ" แบบ martingale intuition) และ optimal levels คำนวณได้จาก (θ, μ, σ) ของ OU ที่เล่ม fit เป็นอยู่แล้วผ่าน half-life

**วิธีลง:**
- Part 3: ต่อท้ายสูตร half-life step เดิมด้วย "จาก rule-of-thumb สู่ optimal band" — ตาราง lookup: fit OU 30 วัน → (κ, σ) → optimal entry/exit band + stop จากสูตร Leung-Li (ประเมินเชิงตัวเลข ใส่เป็นตาราง precomputed ให้ผู้อ่านไม่ต้องแก้ free-boundary เอง)
- Part 6 (Pair Grid): แทน z=±2/±4 คงที่ด้วย band ที่ขึ้นกับ κ ของคู่นั้น — คู่ที่ revert ช้า band ต้องกว้างขึ้น (ตอนนี้ทุกคู่ใช้เลขเดียวกันหมด)
- **Give-up point ได้นิยามจริงเสียที:** stop-loss placement ของ Leung-Li = จุดที่ "รอต่อ" มี expected value ต่ำกว่า "ตัดตอนนี้" — ตอบ finding ของ risk manager ตรงๆ ลง Part 1A (floor) + Part 5

## Cluster C — Regime: เปลี่ยน Hurst จาก filter เป็น signal + มาตรฐาน DFA

**สิ่งที่เล่มมีอยู่:** Part 4 ใช้ H เป็น regime gate (ON/CAUTION/OFF) + warning box แนะนำ DFA แทน R/S อยู่แล้ว (พร้อม `nolds.dfa`)

**สิ่งที่ paper เพิ่ม:**
- **C1 (MDPI 2024, crypto pairs):** local Hurst ต่ำ = spread จะ revert **เร็วกว่า** อย่างมีนัย — ยกระดับ H จาก "เปิด/ปิดเครื่อง" เป็น "ตัวจัดลำดับว่าคู่ไหน/ช่วงไหนน่าเข้าที่สุด" → Part 6 pair selection เพิ่มคอลัมน์ local-H ranking; Part 4 เพิ่มย่อหน้า "H ไม่ใช่แค่สวิตช์ — มันคือตัววัดความเร็ว mean reversion" ซึ่งเชื่อมกลับไปหา break-even count n²/8−n/4 ใน Part 0 (H ต่ำ → รอบ/วันมากขึ้น → ถึง break-even เร็วขึ้น) **ทำให้ Part 0–4–6 กลายเป็นเรื่องเดียวกัน**
- **C2 (Multi-scale DFA 2025):** ยืนยัน + ให้ spec ของ rolling-window DFA (window, scale range) → อัปเกรด warning box เดิมเป็น procedure สั้นๆ พร้อม default parameters — สอดคล้อง Phase 5 ของ v2-plan (regime integration)

## Cluster D — Perp/Funding: ให้ Part 1C มีฐานทฤษฎีก่อนสร้าง risk manual ทับ

**สิ่งที่เล่มมีอยู่:** ตาราง funding scenarios (1B.4, 1C.3, 7.2), hedge = spot + short perp — แต่ทีมรีวิวพบว่าไม่มีสูตร liquidation, ตัวอย่างในเล่มโดน liquidate โดยไม่รู้ตัว (B9), และ funding ×3/วัน ถูก hardcode

**สิ่งที่ paper เพิ่ม:**
- **D1 (Fundamentals of Perpetual Futures, 2024):** no-arbitrage relation ระหว่าง perp premium กับ funding — ให้ **ขอบเขตของ basis ที่ "ปกติ"** และเงื่อนไขที่ arbitrage force ดึงกลับ → Part 1C ได้เครื่องมือแยก "basis ปกติ" จาก "basis ผิดปกติที่ต้อง de-risk" (ตอนนี้ basis risk เป็นแค่คำเตือนลอยๆ) และ funding break-even ของ v2-plan Phase 3 ได้สมการอ้างอิงแทนตัวเลขนิ้วชี้ฟ้า
- **D2 (Designing Funding Rates 2025 + Perpetual Futures Pricing, Math Finance 2025):** จุดสำคัญเชิงปฏิบัติ — **spec ของ funding (คาบ, clamp, premium index) ต่างกันตาม exchange และเปลี่ยนได้** → แก้ hardcode "×3/วัน" ทั้งเล่มเป็น `funding_interval` ใน config + กล่องเตือน 1 กล่อง; รายละเอียด pricing ลง appendix เป็น further reading

**วิธีลง:** ไม่เพิ่มบทใหม่ — เสริม 1C.3 (พื้นฐาน funding) ด้วยครึ่งหน้า "ทำไม funding ถึงมีอยู่" + ขอบเขต basis, แล้วชี้ลูกศรไปที่ hedge runbook ที่ v2-plan Phase 3 จะสร้าง

## Cluster E — Sizing: จาก "0.25× โดยศรัทธา" เป็น "fraction ที่ derive จาก DD constraint"

**สิ่งที่เล่มมีอยู่:** Kelly + f_safe = 0.25×f* (Part 5) และ DD ladder −5/−8/−12 — **สองระบบนี้ไม่เชื่อมกัน** และ quant พบว่า SE ของ p ในเล่มต่ำกว่าจริง ~10 เท่า (B5: ±2.3% ที่จริง ±22%) ทำให้ Kelly ดูแม่นเกินจริง

**สิ่งที่ paper เพิ่ม:** Busseti-Ryu-Boyd ตั้ง Kelly เป็น optimization ที่มี **drawdown constraint เป็นเงื่อนไขตรงๆ**: max growth s.t. P(W_min < α) ≤ β — แปลว่าเลือก fraction จากคำถาม "ยอมให้ P(DD เกิน 8%) ไม่เกินกี่ %" ซึ่งคือภาษาเดียวกับ DD ladder ที่เล่มมีอยู่แล้วเป๊ะ

**วิธีลง:**
- Part 5 เพิ่ม section "5.x ทำไม 0.25 — และเมื่อไหร่ไม่ใช่ 0.25": (1) แก้ B5 ให้ SE ถูกต้อง (2) แสดงว่า estimation error ขนาดนั้น + DD constraint −8% → fraction ที่ derive ได้ตกราว 0.2–0.3× สำหรับพารามิเตอร์ทั่วไปของ grid — **ยืนยันกฎเดิมของเล่มด้วยเหตุผล** แทนที่จะเปลี่ยนกฎ (3) ตาราง fraction ตาม (SE ของ p, DD budget) ให้ปรับเองได้
- นี่คือตัวอย่างที่ดีที่สุดของ "ขยายของเดิม": ตัวเลข 25% ไม่เปลี่ยน แต่เปลี่ยนสถานะจาก dogma เป็น derivation

## Cluster F — Dynamic Grid: จาก reset ที่ "ได้ผลใน backtest" สู่ทฤษฎีว่าทำไมมันควรได้ผล

**สิ่งที่เล่มมี/แผนมีอยู่:** Part 0 มี zero-EV theorem แล้ว (bounded grid + random walk → EV=0), v2-plan Phase 4 มี Part 1D ที่จะใส่ DGT migration (หลุดขอบบน → เก็บทุน+ตั้ง grid ใหม่; หลุดขอบล่าง → ถือ inventory + ใช้กำไรเป็น principal ใหม่), และ Part 4 มี zone migration พูดถึงบางส่วน — แต่ทั้งหมดยังยืนอยู่บนหลักฐาน backtest ของ paper เดียว (DGT, ช่วง bull 2021–24)

**สิ่งที่ paper ชุดนี้เพิ่ม (แต่ละตัวอุดคนละรู):**

- **F2 — Volatility-Induced Financial Growth / Volatility Harvesting:** นี่คือ "อีกครึ่งหนึ่ง" ของทฤษฎีที่ Part 0 เล่าไปแล้วครึ่งเดียว: bounded grid ที่ terminate มี EV=0 ก็จริง แต่วรรณกรรมสาย rebalancing (Shannon's demon, constant-mix) พิสูจน์ว่า **กลยุทธ์ที่ rebalance ไม่หยุดและไม่ terminate สกัด growth เชิงบวกจาก volatility ล้วนๆ ได้** (rebalancing premium ∝ σ²) แม้ราคาไม่มี drift — ภายใต้เงื่อนไข: ราคา stationary/ไม่ดิ่งทางเดียว, ต้อง rebalance ได้เรื่อยๆ, fee ไม่กิน premium หมด
  **นี่คือคำอธิบายที่สง่างามว่าทำไม DGT ชนะ**: การ "ไม่ terminate + ถือ inventory + ตั้ง grid ใหม่" ทำให้ grid เลิกเป็น bounded bet แล้วกลายเป็น volatility harvester ประเภทเดียวกับ constant-mix — และเงื่อนไขที่ premium หาย (ตลาดดิ่งทางเดียว, σ ต่ำ, fee สูง) ก็คือ failure modes ของ DGT พอดี → ลง Part 0 เป็นครึ่งหลังของ section ทฤษฎี ("EV ของ grid = 0, แต่ EV ของ *การไม่เลิกเล่น* > 0 เพราะอะไร") และลง Part 1D เป็นกรอบวิเคราะห์ว่าเมื่อไหร่ migration ควรทำ/ไม่ควรทำ
- **F3 — GTSbot (peer-reviewed, FX):** grid + trend filter + adaptive sizing บน FX HFT ที่รายงานผล "กำไรพร้อม drawdown ลดลง" — เป็นหลักฐานอิสระ (คนละตลาด คนละทีม) ว่าแนวทาง "grid เป็น framework + indicator เป็น executor" ของ Part 7B ยืนอยู่บนขาที่มีคนตรวจสอบแล้ว ไม่ใช่ความเชื่อของเล่มเอง → อ้างใน Part 1D + 7B เป็น evidence box ไม่ต้องเล่าเนื้อใน
- **F4 — Jia 2022 (BTC feasibility):** วิเคราะห์ sensitivity ของ yield ต่อพารามิเตอร์ grid ทีละตัว (ขอบบน, ขอบล่าง, จำนวนช่องบน, จำนวนช่องล่าง, ราคาเริ่ม) — คือข้อมูลที่ Part 3 ควรมีเป็นตาราง "พารามิเตอร์ไหนกระทบกำไรแรงสุด" แต่ไม่มี → แปลงเป็นตาราง sensitivity 1 ตาราง + ผูกกับ Day-0 Runbook (พารามิเตอร์ไหนต้องเป๊ะ พารามิเตอร์ไหนหยาบได้)
- **F5 — Infinity Grid (กลไกที่ exchange ใช้จริง):** geometric grid ไร้ขอบบน + รักษามูลค่า position คงที่ขณะราคาขึ้น = **implementation จริงของ TREND_UP_MIGRATION** ที่ Part 1D จะสอน — มีทั้ง spec บน KuCoin/Pionex และ open-source (kraken-infinity-grid) ให้เทียบ logic → ลง Part 1D (เทียบ DGT reset แบบ discrete vs infinity grid แบบ continuous — สองวิธีแก้ปัญหาเดียวกัน) + บท Exchange Reality ที่ทีมรีวิวสั่งเพิ่ม

**ผลรวมของ Cluster F ต่อ Part 1D:** บทนี้จะเปลี่ยนจาก "วิธีของ paper เดียว" เป็นสเปกตรัม: Terminate (EV=0) → DGT discrete reset (backtest ชนะ, ทฤษฎี = volatility harvesting) → Infinity continuous (ใช้บน exchange ได้เลย) → พร้อม trend filter จาก GTSbot เป็นเบรก — ทุกตัวถูก stress ด้วยเงื่อนไขจาก F2 ว่า premium หายเมื่อไหร่

---

## สิ่งที่จงใจไม่เอา (และทำไม)

1. **RL-based grid parameter optimization / DQN strategy selection (2024–25 หลายฉบับ):** ขัดปรัชญาแกนของเล่ม ("Grid คือ Grid — enhancement ไม่เพิ่ม total P&L อย่างมีนัย, indicator ที่ดีกว่า coin flip ถึงจะมีค่า") ผู้อ่าน reproduce ไม่ได้ ตรวจ overfitting ไม่ได้ และแทนที่ความเข้าใจด้วย black box — ถ้าจะกล่าวถึง ให้เป็น 1 ย่อหน้าใน Part 7 "ทำไมเล่มนี้ไม่สอน RL" ซึ่งตัวมันเองก็เป็นการสอนที่ดี
2. **ML price prediction / GNN regime models:** เหตุผลเดียวกัน + ฐานข้อมูล/compute เกินผู้อ่านเป้าหมาย — regime stack ของเล่ม (Hurst+ADX+BBW) ครอบคลุมพอและตรวจสอบได้

## ลำดับการทำ (ผูกกับ v2-plan + review report)

| ลำดับ | งาน | ผูกกับ | ขนาดงาน |
|---|---|---|---|
| 1 | **E1** Kelly-DD derivation + แก้ B5 | review B5 + Phase 1 errata | เล็ก (section เดียว ตัวเลขต้อง verify ด้วย notebook) |
| 2 | **A1** Inventory skew ลง Part 2/1B (+ เกณฑ์เลือก Option A/B/C) | review G5 + v2-plan Phase 2 | กลาง |
| 3 | **D1+D2** Perp no-arbitrage + funding config ลง 1C | v2-plan Phase 3 (ทำพร้อมกัน) | เล็ก-กลาง |
| 4 | **B1** OU optimal bands ลง Part 3/6 + give-up point | review "positions ไร้ exit" + Phase 5 | กลาง (ต้องทำตาราง precomputed) |
| 5 | **C1+C2** Hurst-as-signal + DFA procedure ลง Part 4/6 | Phase 5 | เล็ก |
| 6 | **A2** GLFT step calibration ลง Part 3 (advanced, optional path) | Phase 6 (ใช้ backtest ยืนยัน) | กลาง |
| 7 | **F2** Volatility harvesting ลง Part 0 (ครึ่งหลังของทฤษฎี) | ต่อจาก zero-EV ที่ทำแล้ว | เล็ก |
| 8 | **F2–F5** ชุด Dynamic Grid ลง Part 1D | v2-plan Phase 4 (เขียน 1D รอบเดียวจบ) | กลาง-ใหญ่ |
| 9 | **F4** Sensitivity table ลง Part 3 + Day-0 Runbook | review P0 (Day-0) | เล็ก |

**กติกาสำหรับทุกชิ้น (กัน "ตัดแปะ"):**
- ทุก section ใหม่ต้องเริ่มจากย่อหน้า "สิ่งที่เราสอนไปแล้วใน §X.Y" แล้วแสดงว่า paper *ต่อ* จากตรงนั้นอย่างไร
- สูตรใหม่ทุกตัวต้อง demo ด้วย **running example บัญชีเดียวกับเล่ม** (ตาม review P0.2) ไม่ใช่ตัวอย่างของ paper
- อ้างอิงท้ายบท (author, year, arXiv id) — เนื้อหาในบทเล่าด้วยภาษาของเล่ม
- ทฤษฎีหนัก (HJB, free boundary, no-arbitrage proofs) อยู่ appendix หรือ further reading เท่านั้น

## เอกสารอ้างอิงหลัก

- Avellaneda, M. & Stoikov, S. (2008). High-frequency trading in a limit order book. *Quantitative Finance* 8(3)
- Guéant, O., Lehalle, C-A., Fernandez-Tapia, J. (2013). Dealing with the inventory risk. arXiv:1105.3115 + hftbacktest GLFT-grid tutorial
- Leung, T. & Li, X. (2015). Optimal Mean Reversion Trading with Transaction Costs and Stop-Loss Exit. arXiv:1411.5062
- Anti-Persistent Hurst … Cryptocurrencies. *Mathematics* (MDPI) 12(18):2911, 2024
- Bui, Schinckus, Al-Jaifi (2025). Long-Range Correlations in Crypto: Multi-Scale DFA. *Physica A*
- He, Manela, Ross, von Wachter (2024). Fundamentals of Perpetual Futures. arXiv:2212.06888
- Ackerer, Hugonnier, Jermann (2025). Perpetual Futures Pricing. *Mathematical Finance*
- Kim & Park (2025). Designing Funding Rates for Perpetual Futures. arXiv:2506.08573
- Busseti, Ryu, Boyd (2016). Risk-Constrained Kelly Gambling. *J. Investing*
- Chen, Chen, Jang (2025). Dynamic Grid Trading. arXiv:2506.11921 ✅ (อยู่ในแผนแล้ว)
- Dempster, Evstigneev, Schenk-Hoppé (2007). Volatility-Induced Financial Growth. *Quantitative Finance* 7(2) + Volatility Harvesting: Extracting Return from Randomness. arXiv:1508.05241
- Rundo, Trenta, di Stallo, Battiato (2019). Grid Trading System Robot (GTSbot). *Applied Sciences* 9(9):1796
- Jia, R. (2022). The Feasibility of Grid Trading Approach for Bitcoin Based on Backtesting. *ICEMME 2022* (EAI)
- Infinity Grid: KuCoin/Pionex product specs + btschwertfeger/kraken-infinity-grid (open source)
