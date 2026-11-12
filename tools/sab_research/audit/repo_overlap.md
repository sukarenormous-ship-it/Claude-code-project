# แผนที่เนื้อหาซ้ำ: เล่ม stat arb สำหรับมือใหม่ (คริปโต) × คลัง `docs/`

> บันทึกของบรรณารักษ์ · key = `repo_overlap` · ตรวจเมื่อ 2026-11-12 · ไม่ได้แก้ไฟล์ใดในคลัง
> กฎของคลังที่ใช้ตัดสิน: **Write Once, Reference Everywhere** (ที่มา: `.claude/skills/knowledge-book/references/craft-standard.md` หัวข้อ "กฎความสอดคล้องข้ามเล่ม" ข้อ 1 และ `docs/quant-theory-volumes-plan.md` ตาราง §0 แถว "กฎเหล็ก")

---

## 0. ขอบเขต วิธีตรวจ และสัญลักษณ์ในบันทึกนี้

### 0.1 ไฟล์ที่เปิดอ่านจริง
- หน้ารวม/อ้างอิง: `docs/index.html`, `docs/notation.html`, `docs/nq-index.html`, `docs/nq-appendix-map.html`, `docs/nq-appendix-glossary.html`, `docs/nq-runbook.html`, `docs/tools-index.html`, `docs/nq-tools.html`
- บทเสริม stat arb ทั้ง 5: `docs/statarb-copula-practice.html`, `statarb-signal-blending.html`, `statarb-live-vs-backtest.html`, `statarb-alpha-decay.html`, `statarb-data-quality.html`
- arb: `arb-part1, 2a, 2b, 3, 4, 5, 7, 8, 9` (หัวข้อทั้งหมด + เนื้อเต็มของ part1 บท 1–2, part2a บท 6, part2b บท 7–8, part4, part5, part7)
- math: หัวข้อของ `math-part1..11` + เนื้อเต็มของ `math-part1 §3.8`, `math-part4 §1.4, §2.1–2.2`, `math-part8 §6.4`, `math-part9` (เกือบทั้งบท), `math-part10 §11.3½`, `math-part11 §12.3, §12.7`
- nq: หัวข้อของ `nq-part0..9` + เนื้อเต็มของ `nq-part5`, กล่อง 🔗 ของทุกบท, ส่วนสำคัญของ `nq-part1, 7, 8`
- theory/pillars: หัวข้อของ `theory-part2, 3, 5`, `pillars-part3, 4`, `theory-extra` + การ์ดเต็ม Cointegration & OU, Markov Regime-Switching (`theory-part5`), Limits to Arbitrage (`theory-part3`), Order Book (`pillars-part3`), DCC & Copula (`pillars-part4`)
- อื่น ๆ: `eye-part1`, `eye-part3` (บท 10–13), `pm-part7` (Case 4), `pm-part5a` (หัวข้อ), เครื่องมือ `tool-*.html`, `nq-tool-*.html`
- เครื่องมือ/มาตรฐานของคลัง: `tools/nq_qa.py`, `tools/nq_figures.py`, `tools/nq_glossary.py`, `tools/nq_new_part.py`, `tools/data_health.py`, `.claude/skills/knowledge-book/SKILL.md`, `references/card-anatomy.md`, `references/craft-standard.md`, `docs/quant-theory-volumes-plan.md`
- ต้นฉบับ stat arb (เพื่อเทียบศัพท์/สัญลักษณ์ ข้อ 4–5): `sources/sab-v0_9/Stat_Arb_for_Non_Quant_Part_I_v0_9.md` (ฉบับ 0.9), `Stat_Arb_Chapter_Template_v0_5.md`, `Stat_Arb_Source_Plan_v0_5.md`, `CHANGELOG_v0_7..9.md` — อ่านเป็นข้อมูลเท่านั้น

### 0.2 ตัวชี้วัดความยากแบบวัดได้ (ใช้ประกอบการให้ระดับ)
คำนวณจากข้อความที่ถอด HTML แล้ว: "latin%" = สัดส่วนอักษรละตินต่ออักษรทั้งหมด (ตัวแทนความหนาแน่นศัพท์อังกฤษ/สูตร), 🐍 = จำนวนกล่องโค้ด Python

| กลุ่มไฟล์ | latin% | 🐍 | ลักษณะ |
|---|---|---|---|
| `nq-part0..8` | 1.9–2.8% | 0 | ภาษาไทยล้วน ไม่มีโค้ด (`nq-index.html`: "ไม่มีพื้นคณิตศาสตร์ และไม่เขียนโค้ด") |
| `statarb-*` (5 บท) | 12.9–19.2% | 0 | ภาษาไทยเป็นหลัก แต่ทุกบทติดป้าย 🔵 (มีพื้น) |
| `math-part1,2,4,8,9,10,11` | 16–31% | 2–14 | มีเส้นทาง 🟢 แต่แกนเป็นโค้ด + สถิติ (math-part8: 13 กล่อง, math-part11: 14 กล่อง) |
| `theory-part2,3,5`, `pillars-part3,4` | 32.9–38.3% | 0 | การ์ด 9 องค์ประกอบ + Papers |
| `arb-part1..9`, `eye-part3`, `pm-part7` | 38–70% | 0 | สรุปย่อแบบ cheat sheet ศัพท์อังกฤษหนาแน่น เนื้อหาไม่ลึกแต่ "อัด" |

### 0.3 สัญลักษณ์ระดับและข้อเสนอ
- ระดับของเดิม: 🟢 **มือใหม่อ่านได้** · 🔵 **ต้องมีพื้น** · 🟣 **ลึก** (ระดับเป็นวิจารณญาณของผู้ตรวจ อิงตัวชี้วัด 0.2 + ป้ายเส้นทางอ่านที่ไฟล์ติดเอง)
- ข้อเสนอ: **🔗 อ้างอิง** (ใส่ในกล่อง "🔗 อยากลึกกว่านี้" ตามแบบ nq) · **✍️ เขียนใหม่ระดับมือใหม่** (คลังไม่มี หรือมีแต่ยากเกิน — เล่มใหม่เป็นบ้าน) · **✂️ ย่อแล้วชี้ไป** (สรุป 1–3 ย่อหน้าเท่าที่จำเป็น แล้วส่งต่อบ้านเดิม)

---

## 1. ตารางแผนที่: หัวข้อของเล่ม → บ้านในคลัง → ระดับ → ข้อเสนอ

### ภาค 1 (บท 0–5)

| บท/หัวข้อ | บ้านที่มีอยู่ในคลัง (ไฟล์ · หัวข้อ) | ระดับของเดิม | ข้อเสนอ |
|---|---|---|---|
| **0.1 stat arb คืออะไร / ไม่ใช่ arb จริง** | `arb-part5` บทนำ ("หุ้น 2 ตัวที่เคลื่อนไหวด้วยกัน → แยกจากกัน → เข้าเทรด"); `arb-part2b` บท 7 (Pairs Trading = Lv.4 Structured, "อย่าเรียก Lv.3+ ว่า Arbitrage"); `theory-part3` การ์ด Limits to Arbitrage (stat-arb = "soft statistical edge — ไม่มีวันบรรจบ") | arb 🔵 (ย่อ) · theory 🔵/🟣 | ✍️ เขียนเองสั้น ๆ + 🔗 `theory-part3` (ทำไมไม่มีวันบรรจบ) และ `arb-part2b` บท 7 (สเปกตรัม Lv.1–5) |
| **0.2 long/short และกำไรขาดทุน** | `arb-part1 §2.1` Short Selling (แบบหุ้น: ยืม, borrow cost, recall, margin call); `math-part1 §1.5` "Short คือ Long กลับหัว" | arb 🔵 · math-part1 🟢/🔵 | ✍️ เขียนใหม่ — คลังสอน short แบบ "ยืมหุ้น" แต่ในคริปโต short ผ่าน perp/futures ไม่ต้องยืมของ; ยังไม่มีที่ใดใช้ "จำนวนถือมีเครื่องหมาย" · ✂️ ชี้ `arb-part1 §2.1` เฉพาะกรณี short spot ที่ต้องยืม |
| **0.3 spot / dated futures / perp** | `arb-part1 §2.2` ตาราง Instruments (Perp "จ่าย/รับ Funding Rate ทุก 8 ชั่วโมง"); `pm-part4` ตาราง (Long/Short perp = payoff เชิงเส้น); `math-part1 §3.8` ราคาล่วงหน้า | 🔵 (ย่อมาก) | ✍️ เขียนใหม่ (ไม่มีบ้านระดับมือใหม่) · ⚠️ ห้ามลิงก์ `arb-part1 §2.2` โดยไม่มีหมายเหตุว่ารอบ funding ไม่ได้ 8 ชม. เสมอ (ต้นฉบับข้อตกลงข้อ 6 ระวังเรื่องนี้แล้ว) |
| **0.4 หลักประกัน leverage และการถูกบังคับปิด** | `nq-part7` (เลเวอเรจคูณความผันผวน, ผลกลางติดลบ); `tool-carry-blowup` ("เพดานเลเวอเรจ < 1 / ขนาดการพัง"); `arb-part1 §2.1` (margin call หุ้น); `eye-part3` บท 12 (Liquidation cascade = barrier option); `pm-part7` Case 4 ("potential liquidation บน perp") | nq/tool 🟢 · eye 🔵 | ✍️ เขียนใหม่ — initial/maintenance/variation margin, liquidation, haircut, free cash **ไม่มีที่ใดสอน** · 🔗 `nq-part7` + `tool-carry-blowup` เป็นสัญชาตญาณเรื่องเลเวอเรจ |
| **0.5 order book, bid–ask, maker/taker** | `nq-part5` (ส่วนต่างราคาซื้อ-ขาย, คำสั่งซื้อทันที/คำสั่งตั้งรอ, ผู้ดูแลสภาพคล่อง; ตัวเลขจริง 22.5% vs 2.3%); `pillars-part3` การ์ด Order Book & Bid-Ask (★★ มี maker-taker rebate); `arb-part7 §25.2` ตาราง order types | nq 🟢 · pillars 🔵 · arb 🔵 | ✂️ ย่อแล้วชี้ `nq-part5` (ใช้ศัพท์ไทยชุดเดียวกัน) + 🔗 `pillars-part3` |
| **0.6 funding ของ perp** | `arb-part1 §2.2` (นิยาม + เครื่องหมาย: Perp > Spot → Long จ่าย Short รับ); `eye-part1` drill (funding −0.03%/8hr ใครรับ); `eye-part3` บท 11 Case A (−0.03%/8hr = −32.9%/ปี); `pm-part7` Case 4 "Funding Arb ที่ไม่ใช่ Arb" (0.05% × 3 × 365 = 54.75%); `arb-part2a §6` (ติดป้าย claim เรื่อง funding เป็น [Observed]/[Heuristic]) | 🔵 (เศษเสี้ยวกระจาย 5 ไฟล์) | ✍️ เขียนใหม่ (กระแสเงินสด เครื่องหมาย รอบ การลงบัญชีแยกจากกำไรราคา) · 🔗 `pm-part7` Case 4 เป็นกรณีเตือน · เครื่องหมายในต้นฉบับ 00.06 ตรงกับ `arb-part1` แล้ว |
| **1 แหล่งกำไร 4 กลไก** (สัญญา · พยากรณ์ · carry · ให้สภาพคล่อง ตามต้นฉบับ 01.02–01.05) | `arb-part2b` บท 7–8 (Lv.1–5 + ตาราง Locked Edge: Dated Futures Basis = ✅ [Exact], Funding carry = ❌ [Heuristic]); `nq-part5` "ใครอยู่อีกฝั่งของไม้นี้" (4 คำตอบ: ต้องการอย่างอื่น · ถูกบังคับ · ผู้ดูแลสภาพคล่อง · รู้มากกว่า); `theory-part3` EMH / Grossman-Stiglitz / Limits to Arb ("premium กับ crash คือกลไกเดียวกัน"); `eye-part3` บท 10 ("yield มาจากไหน?") | nq 🟢 · arb 🔵 · theory 🔵/🟣 | ✍️ เขียนเอง (กรอบ 4 กลไกไม่มีในคลัง) · 🔗 `nq-part5` + `theory-part3` + `arb-part2b` บท 7 — ต้องบอกว่าแกนต่างกัน: Lv.1–5 วัด "ความแน่นอน" ส่วน 4 กลไกบอก "กำไรมาจากไหน" |
| **2.1 basis และ implied carry** | `math-part1 §3.8` (F = S₀·e^{(r−q)T} + เหตุผล cash and carry, มี 🚶 + Python); `arb-part4 §15.1–15.5` (F = S × e^{(r−d)T}, Basis = F − S → 0 ที่หมดอายุ, Contango/Backwardation, ตัวอย่าง SET50) | math-part1 🟢/🔵 · arb 🔵 | ✍️ เขียนใหม่ — คำว่า "implied carry" และการ annualize basis **ไม่พบในคลัง** (grep "implied carry/implied repo" = 0) · 🔗 `math-part1 §3.8` สำหรับเหตุผล no-arbitrage |
| **2.2 OLS / hedge ratio** | `math-part4 §2.1` (β = Cov/Var, คำนวณมือ 6 จุด → 1.54); `math-part8 §6.4` (hedge ratio ต้องเป็น "ช่วง": n=6 → CI [1.118, 1.960] = ช่วงห่าง ฿840,000); `math-part9 §9.1` (regress สลับข้างได้ β ไม่ใช่ส่วนกลับ: 1.5068 vs 0.6500) | 🔵 (มีเส้นทาง 🟢) | ✂️ ย่อแล้วชี้ — สอนแค่ "เส้นที่ใกล้ทุกจุด" + "h เป็นค่าประมาณมีช่วง" แล้ว 🔗 `math-part4 §2.1`, `math-part8 §6.4` |
| **2.3 PCA** | `math-part4 §1.4` (PCA yield curve 91/7/1%, Python); `pillars-part1` (PCA + Kalman ของ yield curve); `arb-part5 §20.3` (PC1 ≈ market factor) | math 🔵 · pillars 🟣 · arb 🔵 | ✂️ ย่อ + 🔗 `math-part4 §1.4` · ✍️ ตัวอย่างคริปโต (PC1 ≈ ตลาดคริปโตรวม) ต้องเขียนเอง |
| **2.4 z-score ไม่มีหน่วย / ค่าเปลี่ยนโดยราคาไม่เปลี่ยน** | `math-part11 §12.7` "สัญญาณไร้หน่วย ปะทะ ต้นทุนที่มีหน่วย" (ตารางทดสอบ ×10: z-score/Sharpe ไม่เปลี่ยน, bps เปลี่ยน) | 🔵 (มีป้าย "🎯 เทรดจริงอยู่แล้ว: ข้ามไปอ่าน §12.7 ก่อน") | 🔗 `math-part11 §12.7` เป็น "อยากลึกกว่านี้" ของต้นฉบับ 02 ข้อ 1 |
| **2.5 รักษาลำดับเวลา / leakage** | `nq-part8` (มองอนาคต, หลุมพรางห้าอย่าง); `math-part11 §12.3–12.4` (k-fold สุ่มสลับใช้ไม่ได้, leakage 4 ทาง) | nq 🟢 · math 🔵 | ✂️ ชี้ `nq-part8` เป็นฐาน + 🔗 `math-part11` |
| **3.1 บัญชีสถานะ เงินสด equity mark-to-market reconciliation** | ไม่มีบ้าน — ใกล้สุดคือ `statarb-live-vs-backtest` ชั้นที่ 1 (กระทบยอดทีละ fill) และชั้นที่ 2 (วัด drawdown จากยอดเงินสกุลเดียวขณะถือหลายสกุล) | 🔵 | ✍️ **เขียนใหม่ — เล่มใหม่เป็นบ้านหลัก** |
| **3.2 กำไรจาก spread / เปลี่ยน hedge ratio** | `math-part9 §9.3` (มูลค่าต่อ 1 หน่วย spread ≈ ฿296, 21 เทรด = 84 fills); `math-part8 §6.4` | 🔵 | ✍️ เขียนใหม่ (การแปลง spread เป็นเงิน) + 🔗 `math-part9 §9.3` |
| **3.3 ต้นทุน** | `nq-part5` + `nq-tool-breakeven` (อัตราชนะขั้นต่ำ = 50% + ต้นทุน ÷ 2 ÷ กำไรเป้า); `arb-part1 §2.3` (Commission/Spread/Slippage/Borrow/Margin Interest/Funding); `math-part9 §9.3` (25 bps ต่อข้าง กำไร 113.7 → 51.5; จุดพลิก z=1 vs z=2 ที่ 28.7 bps); `math-part11 §12.6` (ต้นทุนต้องอยู่ใน CV) | nq 🟢 · arb 🔵 · math 🔵 | ✂️ ย่อแล้วชี้ `nq-part5` + `nq-tool-breakeven` · 🔗 `math-part9 §9.3` (ตารางจุดพลิก) |
| **3.4 margin และ funding ในบัญชี (variation margin, free cash, ชำระรายวัน)** | ไม่มี | — | ✍️ เขียนใหม่ (บ้านหลัก) |
| **4.1 dollar-neutral** | **ไม่พบนิยามในคลัง** (grep "dollar neutral/notional" ไม่เจอในบริบทนี้) | — | ✍️ เขียนใหม่ |
| **4.2 beta-neutral / market-neutral** | `arb-part5 §20.3` (Portfolio beta = 0); `theory-part2` การ์ด CAPM ("quant เห็น: β เป็นเครื่องมือ neutralize/attribution ไม่ใช่ตัวทำนาย"); `math-part9` ศัพท์ "Market neutral" | 🔵 | ✍️ เขียนใหม่บนตัวอย่างคริปโต + 🔗 `theory-part2` |
| **4.3 factor-neutral / ความเสี่ยงที่เหลือ** | `math-part4 §2.2` (Multiple regression → factor, hedge ทีละ factor); `theory-part2` การ์ด Factor Models ★★★; `arb-part5 §20.2–20.3`; "neutral ยังขาดทุน": `pillars-part1` (basis risk: "duration-neutral ≠ PnL"), `theory-part5` (pairs = short gamma), `tool-diversification` (ρ → 1) | math 🔵 · theory 🔵/🟣 · tool 🟢 | ✍️ เขียนใหม่ระดับมือใหม่ + 🔗 `theory-part2`, `math-part4 §2.2`, `tool-diversification` |
| **4.4 optimization ช่วยจัดพอร์ต** | `math-part5` (LP, Lagrange → Markowitz, QP); `theory-part2` mini-card "Portfolio Construction สมัยใหม่" | 🔵/🟣 | ✂️ ย่อแล้วชี้ `math-part5` |
| **5.1 replication / put-call parity** | `math-part1 §2.2` (PCP ★★★); `arb-part1 §3.2, §3.4`; `arb-part3` บท 11–12 (Conversion/Reversal/Box); `arb-part2a` บท 5 (Payoff Algebra); `math-part7 §11.5`; `nq-part6` (โครงสร้างจ่ายผล) | math-part1/nq 🟢 · arb 🔵 | ✂️ ย่อแล้วชี้ `math-part1 §2.2` + `arb-part3` |
| **5.2 volatility / เส้นอายุสัญญา** | `arb-part3` บท 13–14 (IV vs RV, gamma scalping, term structure); `math-part6` บท 8 (GARCH); `theory-part4` | 🔵/🟣 | ✂️ ชี้ไป (เล่มใหม่ไม่ต้องสอน vol) |
| **5.3 market making / inventory** | `pillars-part3` การ์ด Avellaneda-Stoikov (★★); `nq-part5` "ผู้ดูแลสภาพคล่อง" | pillars 🔵/🟣 · nq 🟢 | ✂️ ชี้ + ✍️ ย่อหน้าสั้นเรื่อง inventory risk |
| **5.4 prediction (พยากรณ์)** | `arb-part5 §21` (ML ย่อ); `theory-extra` การ์ด Momentum ★★★ | 🔵 | ✍️ เขียนเอง · ⚠️ คำว่า prediction ชนกับ "Prediction Markets" ใน `arb-part8` บท 30 และ "PM (Prediction)" ใน `arb-part1 §2.2` |
| **5.5 copula และ probability** | `statarb-copula-practice`; `pillars-part4` การ์ด DCC & Copula (★★); `pillars-part2` Gaussian Copula | 🔵 / 🟣 | ✂️ ชี้ไป (ดูบท 19) |

### ภาค 2 (บท 6–10)

| บท/หัวข้อ | บ้านที่มีอยู่ในคลัง | ระดับของเดิม | ข้อเสนอ |
|---|---|---|---|
| **6 cash-and-carry, basis, funding** | `arb-part4` บท 15 (หุ้น/SET50); `math-part1 §3.8`; `arb-part2b §8.1` (basis = locked, funding = ไม่ locked); `arb-part4 §17.3` (Cross-Exchange Funding, Earn + Hedge: 11% − 5% ≈ 6%); `eye-part3` บท 11 Case A และบท 13 Case A (New Listing Gap: spot มาก่อน perp); `pm-part7` Case 4; `theory-part3` (Treasury basis blowup มี.ค. 2020, funding/haircut); `tool-carry-blowup` (carry FX + เลเวอเรจ) | 🔵 (เศษเสี้ยว 7 ไฟล์ ไม่มีบทไหนต่อครบ) | ✍️ **เขียนใหม่ — บ้านหลักของ crypto basis & funding** (ผลตอบแทนต่อทุนรวม margin, hurdle rate, ปิดก่อนหมดอายุ, settlement price — ไม่มีในคลัง) · 🔗 `math-part1 §3.8`, `pm-part7` Case 4, `theory-part3`, `arb-part2b §8.1` |
| **7.1 correlation vs cointegration** | `math-part9 §9.1` (คนเมาจูงหมา, Engle-Granger 3 ขั้น, coint() vs adfuller(): เจอคู่ปลอม 15.5% vs 5.0%); `theory-part5` การ์ด Cointegration & OU (⚠️ correlation ≠ cointegration, Johansen); `arb-part5 §18.1` (ตาราง + ตัวอย่าง "BTC กับ ETH: correlated แต่ ratio เปลี่ยนเรื่อยๆ") | math 🔵/🟣 · theory 🔵 · arb 🔵 | ✂️ ย่อสัญชาตญาณแล้ว 🔗 `math-part9 §9.1` (บ้านลึกที่สุด) — **ไม่เขียนกลไกการทดสอบซ้ำ** |
| **7.2 formation / test period** | `math-part11 §12.1–12.3` (walk-forward); `nq-part8` | math 🔵 · nq 🟢 | ✍️ เขียน protocol + "ทะเบียนคู่" ระดับมือใหม่ + 🔗 |
| **7.3 selection bias / pair-mining** | `nq-part8` (ค้นหา 828 ชุด เสกผลงานปลอม 4.77 จุด); `math-part9 §9.3` (หุ้น 500 ตัว = 124,750 คู่ → ~6,200 คู่ปลอมที่ 5%, ~19,000 ถ้าใช้ adfuller); `theory-part5` (pair-mining); `tool-deflated-sharpe`; `statarb-signal-blending` (งบ DoF) | nq/tool 🟢 · math/theory 🔵 | ✂️ ชี้ `nq-part8` เป็นฐาน (ผู้อ่านเล่มเดียวกัน) + 🔗 `math-part9 §9.3` |
| **7.4 ข้อมูล BTC/ETH จริงในคลัง** | `statarb-copula-practice` (56 วัน: Pearson 0.852, Kendall τ 0.692) | 🔵 | 🔗 ใช้เป็นตัวอย่างจริง (ระบุว่าข้อมูลสั้น) |
| **8 กฎเข้า–ถือ–ออก** | `arb-part5 §18.2` (เข้า \|z\|>2, ออก z≈0, stop \|z\|>4); `math-part9 §9.2` (เกณฑ์เดียวกัน + "ใบรายงานผลที่ซื่อสัตย์" + ตาราง z=1 vs z=2 ตามต้นทุน); `theory-part5` (\|z\|≥2); `math-part11 §12.7`; `nq-part7` (เพดาน 1%/ไม้, −20% หยุดทบทวน); `nq-part2` (เส้นตาย, กรอบเวลา 5 วันทำการ); `nq-runbook` | nq 🟢 · math 🔵 · arb 🔵 | ✂️ ชี้ `math-part9 §9.2` + `nq-part7` · ✍️ เขียน time stop, loss budget, ลำดับเหตุการณ์ (ไม่มีในคลัง) |
| **9 mean reversion / OU / half-life** | `math-part9 §8.4` AR(1) และ §8.4½ OU (ตารางแปล φ = e^{−θΔt}; ครึ่งชีวิตที่วัดจาก 250 วันต่ำไป 14% และช่วง 3.62–8.97 วัน = Kendall bias); `theory-part5` การ์ด (φ = 0.95 → 13.5 วัน); `arb-part5 §19.1` ("ยางยืด", half-life 5 vs 60 วัน); `math-part6 §10.3`, `math-part7 §12.5`; `notation.html` §7 | math 🔵/🟣 · theory 🔵 · arb 🔵 | ✂️ ย่อด้วยภาพ "หนังยาง" ที่คลังใช้แล้ว + 🔗 `math-part9 §8.4½` · ✍️ half-life ≠ เวลาแตะเป้า (first-passage) และ conditional mean — **ไม่มีในคลัง** |
| **10 regime change / พักระบบ** | `theory-part5` การ์ด Markov Regime-Switching (filtered ≠ smoothed); `arb-part5 §19.3` ("ถ้าตลาดเปลี่ยน → หยุดเทรด pairs"); `statarb-alpha-decay` ("ลดขนาดตามสัดส่วนความไม่แน่ใจ", ตั้งกฎลด/เพิ่มกลับไว้ล่วงหน้า, 55%→50% ต้อง 1,067 ไม้); `statarb-signal-blending` (gating ด้วย regime); `nq-part7`, `nq-runbook` (−20% หยุดทบทวน); `arb-part7 §26.3`, `arb-part9` (kill switch); `theory-part3` AMH | nq 🟢 · statarb/theory 🔵 | ✍️ เขียนใหม่ (โปรโตคอล pause/resume + จัดการ inventory ระหว่างพัก — ไม่มีในคลัง) · 🔗 `statarb-alpha-decay`, `theory-part5` |

### ภาค 3–5 (แผนบท 11–20)

| บท | บ้านที่มีอยู่ในคลัง | ระดับของเดิม | ข้อเสนอ |
|---|---|---|---|
| **11 factor residual (reversal/momentum)** | `theory-part5` (Avellaneda-Lee residual OU — 1 บรรทัดใน "ใช้ได้เมื่อไร" และ 📚); `arb-part5 §20`; `theory-part2` Factor Models; `math-part4 §2.2`; `theory-extra` Momentum ★★★ | 🔵/🟣 | ✍️ เขียนใหม่ระดับมือใหม่ + 🔗 |
| **12 ตะกร้า (กี่ขา)** | `theory-part5` (Johansen หลายตัว — กล่าวถึง); `arb-part5 §20.1` (จาก pairs สู่ portfolio); `math-part4 §1.3` (wᵀΣw); `arb-part4 §17.1–17.2` (ETF/index basket) | 🔵 | ✍️ เขียนใหม่ (cointegration หลายตัวแปรไม่มีบ้านเต็มในคลัง) |
| **13 จัดเงินระหว่างหลายตะกร้า** | `math-part10 §11.2–11.5` (Kelly, half-Kelly, **§11.3½ Kelly ที่สัมพันธ์กัน: ρ=0.6 → เดิมพันเกิน 3.4 เท่า**, drawdown, stress test); `pm-part5a` Kelly; `theory-extra` การ์ด Kelly; `arb-part2b §7.1`; `nq-part7` + `nq-tool-ruin`; `tool-diversification`; `pillars-part4` VaR/ES | nq/tool 🟢 · math 🔵 · pillars 🔵/🟣 | ✂️ ย่อ + 🔗 `math-part10 §11.3½` (ตรงประเด็นหลายตะกร้าที่สุด) และ `nq-part7` · ✍️ การจัดเงินเมื่อแต่ละตะกร้าใช้ margin ต่างกัน · ⚠️ Kelly มี 4 บ้านในคลัง ต้องเลือกลิงก์เดียวเป็นหลัก |
| **14 อ่าน paper และ code** | `pillars-part5` (ประโยคเดียว "อ่าน paper ต้นฉบับ"); กล่อง 📚 Papers ในการ์ด theory/pillars (เป็นรายการ ไม่ใช่วิธีอ่าน); `arb-part2a §6.1` (4 ระดับความแน่ใจของ claim) | — | ✍️ **ช่องว่างจริง** — เล่มใหม่เป็นบ้าน |
| **15 ทดสอบกับข้อมูลที่ไม่เคยเห็น** | `math-part11` บท 12–13 (walk-forward, leakage, multiple testing, block bootstrap); `theory-part5` การ์ด Deflated Sharpe; `nq-part8`; `tool-deflated-sharpe`; `statarb-data-quality` (หกโรคข้อมูล + 4 ปัญหาเฉพาะคริปโต); `statarb-signal-blending` | nq/tool 🟢 · math 🔵/🟣 · statarb 🔵 | ✂️ ย่อแล้วชี้ — บ้านแน่นที่สุดในคลังแล้ว |
| **16 จากกราฟสู่คำสั่ง (execution)** | `pillars-part3` (√-law impact, Almgren-Chriss); `arb-part7` บท 25 (ตาราง Limit/Market/IOC/FOK); `arb-part1 §1.4` และ `arb-part7 §26.1` (execution risk "ขา 1 ได้ ขา 2 ไม่ได้"); `nq-part5`; `statarb-live-vs-backtest` (กระทบยอดทีละ fill, งบ tracking error, shadow trading) | nq 🟢 · arb/statarb 🔵 · pillars 🔵/🟣 | ✂️ ชี้ไป + ✍️ legging, partial fill, reject, timeout และผลต่อบัญชี (ไม่มีในคลัง) |
| **17 อ่าน backtest ที่ขาดทุน** | `math-part9 §9.2` ("ชนะ 21/21 ไม้ + drawdown 0 = หลักฐานว่าข้อมูลผิด"); `statarb-live-vs-backtest`; `statarb-alpha-decay`; `statarb-data-quality`; `nq-part9` (85% ของกำไรทั้งเดือนมาจาก 2 วัน); `nq-part8` | 🟢/🔵 | ✍️ เขียน "อ่าน backtest ขาดทุนให้เป็นคำถามวิจัย" (ต้นฉบับ 01.08 มีแล้ว คลังไม่มี) + 🔗 สาย statarb |
| **18 หลายสัญญาณ + ปรับพอร์ตให้คุ้มต้นทุน** | `statarb-signal-blending` (voting/weighting/gating, งบ DoF, meta-labelling — **บ้านหลัก**); `math-part11 §14` (Ridge/Lasso), §12.6 (ต้นทุนใน CV) | 🔵 | ✂️ ชี้ `statarb-signal-blending` · ✍️ ส่วน rebalance/turnover ให้คุ้มต้นทุน |
| **19 ความสัมพันธ์ไม่เชิงเส้น + copula** | `statarb-copula-practice` (บ้านเชิงปฏิบัติ: 4 บทบาท, สัญญาณสองตัวสัมพันธ์กันแค่ 0.141); `pillars-part4` การ์ด DCC & Copula; `pillars-part2` Gaussian copula (Li 2000 → 2008) | 🔵 / 🟣 | ✂️ ชี้ไป · ✍️ ต้องเขียนบทนำระดับมือใหม่เอง เพราะ `statarb-copula-practice` บอกให้อ่าน **practice-part2 §2.1–2.4 ก่อน ซึ่งไม่มีในคลังนี้** |
| **20 baseline → ML** | `arb-part5 §21` (Feature, Walk-Forward, overfitting — ย่อมาก); `math-part11` (CV, bootstrap, Ridge/Lasso); `statarb-signal-blending` (meta-labelling); `theory-extra` (Deep Hedging — concept card) | 🔵 | ✍️ เขียนใหม่ระดับมือใหม่ + 🔗 `math-part11` |

### 1.1 บ้านที่ "แข่งกันเอง" ในคลัง — เล่มใหม่ต้องเลือกลิงก์หลักให้ชัด
| แนวคิด | บ้านที่ซ้ำกัน | เสนอให้ลิงก์หลักเป็น | เหตุผล |
|---|---|---|---|
| Cointegration/pairs | `arb-part5 §18` · `theory-part5` การ์ด · `math-part9` บท 9 | `math-part9` บท 9 (ลึก+ตัวเลขตรวจได้) ; `theory-part5` เป็นภาพรวม | `arb-part5` เป็น cheat sheet ไม่มี 🚶 |
| OU / half-life | `arb-part5 §19.1` · `theory-part5` · `math-part9 §8.4½` · `notation.html` §7 | `math-part9 §8.4½` | มี Kendall bias + ช่วงความเชื่อมั่น |
| Kelly | `arb-part2b §7.1` · `pm-part5a` · `math-part10 §11.2–11.3½` · `theory-extra` | `math-part10 §11.3½` | ตอบโจทย์หลายตะกร้า (ความสัมพันธ์ระหว่างกลยุทธ์) · หมายเหตุ: `nq-part7` 🔗 ชี้ `pm-part5a` |
| Backtest overfitting | `theory-part5` Deflated Sharpe · `math-part11 §12.5` · `nq-part8` · `tool-deflated-sharpe` | `nq-part8` (ฐานมือใหม่) → `tool-deflated-sharpe` → `theory-part5` | ไล่ระดับความยาก |

---

## 2. ช่องว่างจริงของคลัง — เล่ม stat arb ควรเป็นบ้าน

ตรวจด้วยการค้นคำสำคัญทั้งคลัง (`grep` บนข้อความที่ถอดจาก HTML ทั้ง 99 ไฟล์ใน `docs/`) และอ่านบ้านที่ใกล้ที่สุด:

1. **กลไกตลาดคริปโตระดับมือใหม่** — spot/dated futures/perp, initial/maintenance/variation margin, liquidation, haircut, settlement price, notional vs หลักประกัน. คลังมีแค่ตาราง 1 ตารางใน `arb-part1 §2.2` และเคสกระจายใน `eye-part3`, `pm-part7` (ทั้งหมดระดับ 🔵 ย่อ) · `nq-*` ไม่แตะ futures/perp เลย
2. **funding เป็นกระแสเงินสด** — เครื่องหมาย, รอบที่ต่างกันตาม exchange, การลงบัญชีแยกจากกำไรราคา. คลังเขียน "ทุก 8 ชั่วโมง" เป็นข้อเท็จจริงตายตัวใน `arb-part1 §2.2` (และใช้ /8hr ใน `eye-part1`, `eye-part3`, `pm-part7`)
3. **บัญชีสถานะและการกระทบยอด** — signed holdings, cash, equity, mark-to-market, realized/unrealized, return denominator, gross/net exposure. ไม่มีไฟล์ใดสอน (ใกล้สุด `statarb-live-vs-backtest` ซึ่งสมมติว่าผู้อ่านมีระบบรันอยู่แล้ว)
4. **basis เป็นเงิน vs เป็นอัตรา, implied carry, annualize, ผลตอบแทนต่อทุนรวม margin, hurdle rate, ปิดก่อนหมดอายุ** — `math-part1 §3.8` ให้สูตร F แต่ไม่กลับด้านเป็นอัตรา; คำว่า implied carry ไม่ปรากฏ
5. **dollar-neutral** ไม่มีนิยาม; beta- vs factor-neutral ไม่เคยถูกเทียบบนตัวอย่างเดียวกัน; "neutral แต่ยังขาดทุน" มีแค่ในบริบทบอนด์ (`pillars-part1`)
6. **โปรโตคอลเลือกคู่ formation/test + ทะเบียนคู่** ระดับมือใหม่ (คลังมีหลักการใน `math-part11`, `nq-part8` แต่ไม่มีขั้นตอนสำหรับคู่)
7. **half-life ≠ เวลาที่เส้นทางแตะเป้า (first-passage)**, conditional mean — ไม่มีในคลัง (`theory-part5` ยังเขียนว่า "ต้องถือไหวอย่างน้อยหลาย half-life")
8. **กฎเข้า–ถือ–ออกครบชุด**: time stop, loss budget, ลำดับเหตุการณ์เมื่อหลายกฎชนกัน, **pause/resume และการจัดการ inventory/คำสั่งค้างระหว่างพัก** — คลังมีแค่ "หยุดเทรด" (`arb-part5 §19.3`), "−20% หยุดทบทวน" (`nq-runbook`), "ลดขนาดตามความไม่แน่ใจ" (`statarb-alpha-decay`)
9. **legging / partial fill / reject / timeout** และผลต่อบัญชี — คลังมีแค่แถว "Execution: ขา 1 ได้ ขา 2 ไม่ได้" (`arb-part1 §1.4`, `arb-part7 §26.1`)
10. **วิธีอ่าน paper และ code** + ระดับหลักฐาน — ไม่มี (มีแค่รายการ 📚 Papers)
11. **อ่าน backtest ที่ขาดทุนให้เป็นคำถามวิจัย** — ไม่มี (มีแต่ backtest ที่ "ดีเกินจริง" ใน `math-part9 §9.2`)
12. **factor residual และตะกร้าในคริปโต** ระดับมือใหม่, cointegration หลายตัวแปร — มีแค่การกล่าวถึง (`theory-part5`)
13. **baseline → ML** ระดับมือใหม่ — `arb-part5 §21` ย่อเกินไป
14. **ศัพท์ไทยของเรื่องข้างบน** — `nq-appendix-glossary.html` (53 คำ) ไม่มี basis, funding, margin, liquidation, hedge ratio, cointegration, half-life เลย

> หมายเหตุด้านข้อมูล: คลังนี้ไม่มีข้อมูลดิบในตัว — `tools/nq_figures.py` และ `tools/data_health.py` มองหา `data/` หรือ `../options-data/data` ซึ่งไม่มีอยู่ (`ls data` → ไม่พบ); ข้อมูลที่บรรยายไว้ใน `nq-index.html` คือ "สแนปช็อต option chain ของ Deribit และ OKX รายวัน 57 วัน" — **ไม่มีประวัติ funding หรือราคา futures/perp แยก** เล่มใหม่ที่ต้องการตัวอย่าง basis/funding จริงต้องหาแหล่งข้อมูลใหม่ หรือคงตัวเลขสมมติตามข้อตกลงข้อ 1 ของต้นฉบับ

---

## 3. สไตล์ 2 แบบในคลัง — แบบไหนเหมาะกับเล่มใหม่

### 3.1 สองแบบที่มีอยู่
| | การ์ดทฤษฎี 9 องค์ประกอบ (`theory-*`, `pillars-*`) | บทเล่าเรื่อง + กล่องบังคับ (`nq-*`) |
|---|---|---|
| นิยาม | Thesis → ❓ทำไมต้องรู้ → 🔧ใช้ทำอะไร → ✅ใช้ได้ → ❌พัง → ⚖️ข้อดี/เสีย → 🧠มุมต่าง → 📍ปัจจุบัน → 📚Papers (+ 🚶, 🧮, ✍️, 🎯 สำหรับ ★★★) — `references/card-anatomy.md` | เรื่องต่อเนื่องของ "มิน" + กล่องที่ `tools/nq_qa.py` บังคับทุกบท: 🧭 เส้นทางอ่าน · ประโยคทอง `.pq` · 📖 ศัพท์ใหม่ (เพดาน 12 คำ, `TERM_CAP = 12`) · 🧠 มุมที่มองต่าง · 🎬 ฉากหน้าจอ · 🧭 นิสัยคิด · ⚠️ ค่าเริ่มต้น · 🧮 · ✍️ ลองทำเอง · 🎯 3 อย่างที่ต้องจำ · 🔗 อยากลึกกว่านี้ |
| หน่วยเนื้อหา | 1 การ์ด = 1 ทฤษฎี | 1 บท = 1 สถานีของกระบวนการ |
| ผู้อ่านเป้าหมาย | หลายระดับในหน้าเดียว: แบนเนอร์ของ `theory-part5`/`pillars-part3` บอกมือใหม่ให้อ่านเฉพาะ 🎯 + 🚶 + 🧮 + 🎯3 (ข้ามกล่องสูตรและ ❌ เชิงลึก) | ระดับเดียว: "ไม่มีพื้นคณิตศาสตร์ และไม่เขียนโค้ด" (`nq-index.html`) |
| ศัพท์อังกฤษ | latin 32.9–38.3% | latin 1.9–2.8% |

### 3.2 ข้อเสนอ: ใช้แบบ **บทเล่าเรื่อง + กล่องบังคับ (nq)** เป็นแกน — เหตุผลพร้อมหลักฐาน
1. **ผู้อ่านตรงกัน** — ต้นฉบับประกาศว่า "เส้นทางหลักของทุกบทใช้เพียงบวก ลบ คูณ หาร เปอร์เซ็นต์ และการอ่านกราฟ" และ "ไม่จำเป็นต้องเขียนโค้ดเป็น" (ต้นฉบับ ส่วน positioning) = โปรไฟล์ผู้อ่านของ `nq-index.html` เป๊ะ
2. **เนื้อหาเป็น "กระบวนการตัดสินใจ" ไม่ใช่ "ทฤษฎีตำนาน"** — ต้นฉบับบอกว่า "เล่มนี้สอนการตัดสินใจ: จะถืออะไร เท่าไร เมื่อไร และเงินในบัญชีเปลี่ยนอย่างไร" ช่อง 📍ปัจจุบัน/📚Papers/⚖️ ของการ์ดไม่มีที่ให้ "บัญชีเงินสด" หรือ "กฎ pause/resume" ส่วนกล่อง ⚠️ ค่าเริ่มต้น / 🧭 นิสัยคิด / 🎬 ฉากหน้าจอ ของ nq รองรับตรง ๆ
3. **คลังเองยอมรับว่าการ์ดไม่เหมาะกับการอ่านรอบแรก** — `index.html` ติดป้ายฉบับเล่าเรื่องว่า "แนะนำให้เริ่มที่นี่" และ "เหมาะกับการอ่านรวดเดียวให้เข้าใจภาพรวม ก่อนจะย้อนมาอ่านฉบับการ์ด"; การ์ดเองต้องมีแบนเนอร์บอกมือใหม่ให้ข้ามบางกล่อง
4. **บทเสริม stat arb ทั้ง 5 บทเลือกเสียง nq ไปแล้ว** — ใช้ตัวละครมิน (🎬 "ฉากของมิน" ใน `statarb-signal-blending`, `statarb-alpha-decay`), ใช้ ⚠️ ค่าเริ่มต้น (4/5 บท), ลิงก์กลับ `nq-index.html`/`nq-appendix-map.html` ทุกบท — เล่มใหม่ที่ใช้แบบเดียวกันจะเชื่อมได้ไร้รอยต่อ
5. **กล่องบังคับตรวจได้ด้วยเครื่อง** — `tools/nq_qa.py` ตรวจโครงสร้าง HTML, กล่องบังคับ, ลิงก์ภายในต้องมีไฟล์จริง (W8), เพดานศัพท์ (W9) และผ่านทุกข้อในตอนตรวจ ("ตรวจ 20 ไฟล์ · ผ่านทุกข้อ ✓") — เป็นโครงสร้างพื้นฐานที่ยกไปใช้กับเล่มใหม่ได้ทันที
6. **มาตรฐาน v4 ของคลังย้ายองค์ประกอบ "learning design" (🎬 ฉากหน้าจอ, 🧭 นิสัยคิด, heuristic ระดับโต๊ะ) ไปอยู่ใน nq แล้ว** — ดู `craft-standard.md` หัวข้อ "🎓 Learning design" เทียบกับ `CHAPTER_BOXES` ใน `nq_qa.py`

### 3.3 จุดที่ควรยืมจากแบบการ์ด/ต้นฉบับ (ไม่ใช่ทิ้งทั้งหมด)
- แยก **❌ พังเมื่อไร (เทคนิค)** ออกจาก **ข้อเสีย (trade-off)** ตามกฎเหล็กข้อ 1 ของ `card-anatomy.md` — ใช้ในกล่องท้ายบทกลยุทธ์ (บท 6–7, 11–12)
- **🚶 อ่านเป็นภาษาคนก่อน** เหนือทุกสูตร (บังคับทั้งสองแบบ)
- ป้าย **"ลงลึก"** ของต้นฉบับ ≈ ป้าย **[รอบสอง]** / "เจาะลึก (ข้ามได้)" ใน `craft-standard.md` และ `card-anatomy.md` — ใช้ชื่อเดียวกับคลังเพื่อความสม่ำเสมอ

### 3.4 การแปลงแม่แบบต้นฉบับ → กล่องของ nq
| แม่แบบต้นฉบับ (`Stat_Arb_Chapter_Template_v0_5.md`) | กล่องในคลัง |
|---|---|
| คำถามเปิดบท | 🎬 ฉากหน้าจอ / ย่อหน้าเปิดแบบปริศนา (`craft-standard.md` "เปิด section ด้วยปริศนา") |
| เมื่ออ่านจบ ผู้อ่านควร… / พื้นฐานที่ควรรู้ | 🧭 เส้นทางอ่าน (+ ลิงก์ prerequisite) |
| ข้อกำหนดของกลยุทธ์และระบบ (ตาราง) | ⚠️ ค่าเริ่มต้น + ตารางแบบ `nq-runbook.html` |
| กรณีศึกษาและข้อจำกัด | 🧠 มุมที่มองต่าง + กล่องเคส "เมื่อทฤษฎีพังจริง" |
| แบบฝึกหัดและเฉลย | ✍️ ลองทำเอง (มี "ดูเฉลย" แบบ `math-part9 §9.3`) |
| ทบทวนหนึ่งหน้า | 🎯 3 อย่างที่ต้องจำ + สรุป ✓ + 📖 ศัพท์ใหม่ (≤12 คำ) |
| แหล่งอ่านต่อ | 🔗 อยากลึกกว่านี้ (ในคลัง) แยกจาก 📚 (แหล่งภายนอก) |

ข้อขัดกันที่ต้องตัดสิน: แม่แบบต้นฉบับกำหนดกระดาษ Letter และภาพ PNG จาก matplotlib (`figures/`, `code/v06_figures.py`) แต่ `.claude/skills/knowledge-book/SKILL.md` กำหนด "inline SVG เสมอ (ห้าม chart library/canvas/รูป raster)" และ nq วาดกราฟจาก JSON ด้วย `tools/nq_charts.py`

---

## 4. "Quant for Non-Quant / เล่มเดิม" ในคลังนี้คือชุดไหน

### 4.1 ข้อเท็จจริงที่ตรวจได้
- ต้นฉบับอ้าง "Quant for Non-Quant" ด้วย **เลขภาคโรมัน I ถึง XVIII** และหัวข้อย่อยแบบ "III.01" เช่น ภาค II (covariance/correlation, z-score, conditional expectation, distribution/CDF), ภาค III (regression, beta; III.01 = price/simple/log return), ภาค IV (systematic vs idiosyncratic), ภาค V (AR(1)/stationarity), ภาค VI (cointegration), ภาค VII (multivariate cointegration), ภาค VIII (factor), ภาค IX (PCA), ภาค XIV (research validity), ภาค XV (portfolio engineering), ภาค XVI (execution), ภาค XVIII (ไม่ระบุหัวข้อ; อ้างคู่กับ XVI ในแผนบท 6)
- ต้นฉบับบอกว่า "เล่มเดิมสอนเครื่องมือ เช่น สถิติ regression และ cointegration" และแม่แบบ "ใช้รูปแบบจาก Quant for Non-Quant ฉบับปรับปรุงครั้งที่ 11 … กระดาษ Letter"
- **ต้นฉบับยังไม่เคยตรวจการอ้างนี้กับไฟล์จริง**: `CHANGELOG_v0_7.md` และ `CHANGELOG_v0_8.md` ข้อค้าง "ตรวจการอ้างกับเล่มเดิมเมื่อได้ไฟล์", `CHANGELOG_v0_9.md` ยังค้าง "ตรวจการอ้างกับเล่มเดิม"
- ในคลัง **ไม่มีชุดไฟล์ใดมี 18 ภาคเลขโรมัน**: `nq-*` มี Part 0–9 (เลขอารบิก); `math-*` มี 11 ไฟล์ จัดเป็น "เล่ม 1 Part I–V" + "เล่ม 2 · A–F"; ไม่มีไฟล์ชื่อ "Quant for Non-Quant" (grep "non-quant" พบแค่ "Monday-Morning Test ฉบับ non-quant" ใน `nq-appendix-drills.html`)
- **`nq-*` ไม่ตรงโปรไฟล์ "สอน regression/cointegration"** — `nq-index.html` ระบุว่าไม่มีคณิตศาสตร์ ไม่มีโค้ด; ทั้งเล่มไม่มีคำว่า cointegration/regression เป็นหัวข้อ
- คำว่า "เล่มเดิม" ในภาษาของคลังนี้ **หมายถึง math/pm/arb/eye** — `docs/quant-theory-volumes-plan.md` §0 ("ช่องว่างทฤษฎี quant ที่เล่มเดิม (math/pm/arb/eye) ขาด") และกล่อง "🔗 เชื่อมเล่มเดิม" ใน `theory-part1, 2, 5`

### 4.2 ข้อสรุป: **ไม่แน่ใจ — น่าจะเป็นเอกสารภายนอกที่ไม่อยู่ในคลังนี้**
เนื้อหาที่ต้นฉบับอ้างถึง "ตรงกับ `math-*` มากที่สุด" แต่โครงเลขภาคไม่ตรงชุดใดเลย ส่วน `nq-*` ใกล้ด้านผู้อ่าน (non-quant) แต่ไม่สอนเครื่องมือที่ต้นฉบับอ้าง → ควรถามผู้ใช้ว่ามีไฟล์ Quant for Non-Quant หรือไม่ และจะนำเข้าคลังหรือไม่

### 4.3 ตารางแปลงการอ้าง "ภาค X ของเล่มเดิม" → ไฟล์ในคลังที่ใกล้ที่สุด
| ต้นฉบับอ้าง | หัวข้อที่ต้นฉบับระบุ | ทวนแนวคิด (ระดับ 🟢) | ทวนเครื่องมือ (ระดับ 🔵) |
|---|---|---|---|
| ภาค I–II | payoff, cash flow, expected value | `nq-part6` (กราฟจ่ายผล) | `math-part1` บทที่ 1, `math-part2 §5.4` |
| ภาค II | covariance/correlation, z-score, conditional expectation, distribution/CDF, uncertainty | `nq-part1` (ความน่าจะเป็นแบบมีเงื่อนไข, ความสุ่ม), `nq-part4` | `math-part2 §4.5`, `§5.3`, `§6.2–6.3` |
| III.01 | price, simple vs log return | `nq-part4` (ค่าเฉลี่ยสองแบบ) | `math-part1 §3.6` |
| ภาค III | regression, beta | — | `math-part4 §2.1`, `math-part8` บทที่ 6 |
| ภาค IV | systematic vs idiosyncratic | — | `theory-part2` (CAPM, Factor Models), `math-part10 §10.3–10.4` |
| ภาค V | AR(1), stationarity, dynamics | — | `math-part9` บทที่ 8 |
| ภาค VI | cointegration | — | `math-part9` บทที่ 9, `theory-part5` |
| ภาค VII | multivariate cointegration | — | ไม่มีบ้านเต็ม (`theory-part5` กล่าวถึง Johansen) |
| ภาค VIII | factor | — | `theory-part2` Factor Models, `math-part4 §2.2` |
| ภาค IX | PCA | — | `math-part4 §1.4` |
| ภาค XIV | research validity | `nq-part8` | `math-part11`, `theory-part5` (Deflated Sharpe) |
| ภาค XV | portfolio engineering | `nq-part7` | `theory-part2` (Portfolio Construction), `math-part5`, `math-part10` |
| ภาค XVI | execution | `nq-part5` | `pillars-part3`, `arb-part7` |
| ภาค XVIII | (ไม่ระบุ) | ไม่ทราบ | ไม่ทราบ |

### 4.4 ลิงก์ข้ามเล่มควรชี้อย่างไร
1. **เลิกใช้คำว่า "เล่มเดิม"** ในเล่มใหม่ เพราะชนกับความหมายของคลัง (math/pm/arb/eye) — เรียกชื่อไฟล์/ชื่อเล่มตรง ๆ เช่น "คิดแบบ Quant Part 8" หรือ "คณิตศาสตร์สำหรับ Options เล่ม 2 · D §9.1"
2. แทน "ภาค X ของเล่มเดิม" ด้วย **ลิงก์สองชั้น**: "ทวนแนวคิด" → `nq-part*` (🟢) และ "ทวนเครื่องมือ" → `math-*`/`theory-*` (🔵) ตามตาราง 4.3
3. ลิงก์ต้องเป็น `href` ไปไฟล์ที่มีอยู่จริงเท่านั้น (กฎ W8 ใน `nq_qa.py`); สิ่งที่ไม่มีในคลังให้เขียนเป็นข้อความธรรมดาแบบที่ nq ทำกับ `statarb-ch*`, `ob-part*`
4. ถ้าภายหลังนำ Quant for Non-Quant เข้าคลัง ให้ใช้ prefix ใหม่ที่ไม่ชนกับ `nq-` (ซึ่งเป็นของ "คิดแบบ Quant" แล้ว)

### 4.5 ระวังชื่อชนกับ "statarb-ch*" ที่ nq อ้างถึง
`nq-part2` (statarb-ch4b "ε Design + Null Hypothesis 101"), `nq-part3` (statarb-ch6 "regime detection, Hurst"), `nq-part7` (statarb-ch12 "การกำหนดขนาดไม้ในพอร์ตหลายตัว"), `nq-part8` (statarb-ch21 "วิธีทดสอบที่เชื่อถือได้"), `nq-appendix-map.html` (statarb-ch0 ในเส้นทาง "🔵 สายเขียนโค้ด") อ้างถึงซีรีส์ "Statistical Arbitrage" ที่**ไม่มีในคลัง** โดยอ้างเลขบทตั้งแต่ ch0 ถึง ch21 และ ch4b — เลขบทไม่ตรงแผน 21 บท (0–20) ของต้นฉบับ (เช่น regime = ch6 vs บท 10; sizing = ch12 vs บท 13) และอยู่ในสาย "เขียนโค้ด" ขณะที่ต้นฉบับไม่ต้องเขียนโค้ด → **น่าจะเป็นคนละเล่ม (ไม่แน่ใจ)** · เล่มใหม่ไม่ควรใช้ชื่อไฟล์ `statarb-chN` เพื่อไม่ให้ข้อความอ้างใน nq ชี้ผิดเล่ม

---

## 5. ศัพท์/สัญลักษณ์กลางที่เล่มใหม่ต้องใช้ให้ตรง และจุดที่ต้นฉบับต่างจากคลัง

### 5.1 สัญลักษณ์กลางของคลัง (`notation.html`) ที่เกี่ยวกับเล่มนี้
| สัญลักษณ์ | ความหมายในคลัง | ที่มา |
|---|---|---|
| θ (OU) | แรงดึงกลับของ Ornstein-Uhlenbeck · half-life = ln2/θ | `notation.html` §7 และตาราง "ชนกัน" (θ ของ OU vs Theta; Heston ใช้ κ เป็นแรงดึงกลับ "สลับบทบาทกับ OU!") · `arb-part5 §19.1`, `math-part9 §8.4½`, `theory-part5` |
| φ | AR(1) coefficient (\|φ\|<1 นิ่ง; φ=1 unit root) | `notation.html` §7 |
| z-score | (spread − μ)/σ | `notation.html` §7 |
| β | beta = Cov(Rᵢ,R_m)/Var(R_m) — และในทางปฏิบัติใช้เป็น hedge ratio | `notation.html` §2; `math-part4 §2.1`, `math-part9 §9.1`, `arb-part5 §18`, `theory-part5` |
| ρ, Σ, w | correlation, covariance matrix, weights | `notation.html` §2 |
| spread | ask − bid | `notation.html` §5 |
| f* | Kelly: (μ−r)/σ² หรือ p − q/b | `notation.html` §2 |
| DSR | Deflated Sharpe Ratio | `notation.html` §7 |
| T | เวลาถึงหมดอายุ | `math-part1 §3.8`, `arb-part4 §15.1` |
| F, S₀, q | ราคาล่วงหน้า, ราคา spot, อัตราปันผล (F = S₀·e^{(r−q)T}) | `math-part1 §3.8` (ไม่อยู่ใน notation.html) |

**ช่องโหว่ของ `notation.html` เอง**: ไม่มี F, basis, funding rate, hedge ratio (แยกจาก β), จำนวนถือ, implied carry; และตาราง "สัญลักษณ์ที่ชนกัน" **ไม่มีแถว spread** ทั้งที่ §5 ใช้ spread = ask − bid และ §7 ใช้ spread ในความหมายส่วนต่างของคู่

### 5.2 จุดที่ต้นฉบับ (ตาราง "สัญลักษณ์ที่ใช้ทั้งเล่ม") ต่างจากคลัง
| เรื่อง | ต้นฉบับ | คลัง | ข้อเสนอ |
|---|---|---|---|
| ความเร็วปรับกลับของ OU | **κ** ($\phi=e^{-\kappa\Delta}$) | **θ** (`notation.html` §7; φ = e^{−θΔt} ใน `math-part9 §8.4½`) | เปลี่ยนเป็น θ ให้ตรงคลัง หรือคง κ แต่ใส่หมายเหตุแปลทุกครั้ง (คลังเตือนการสลับ κ/θ ไว้แล้ว) |
| Hedge ratio | **h** (หน่วย B ต่อ 1 หน่วย A; spread X = P_A − hP_B) | **β** (`math-part9`: B − β·A; `arb-part5`: A − β×B; `theory-part5`: Y − β·X) | คง h ได้ (แยกจาก β ตลาด ชัดกว่า) แต่ต้องเขียนหมายเหตุเชื่อม "ในคลัง (math-part9, arb-part5) ใช้ β" และระบุทิศ regress ทุกครั้ง (คลังเองใช้ทิศไม่ตรงกัน) |
| q | จำนวนที่ถือ (มีเครื่องหมาย) | อัตราปันผล (`math-part1 §3.8`) · q = 1 − p ใน Kelly (`arb-part2b §7.1`, `notation.html`) · Q = ขนาดคำสั่ง (`notation.html` §5) | ใส่ในตารางชนกันของเล่มใหม่ |
| d | มูลค่าสถานะ q·P | อัตราปันผล (`arb-part4 §15.1`) | ใส่ในตารางชนกัน |
| K | ฐานทุน | strike (`notation.html` §3) — ต้นฉบับ 05.03 ก็ใช้ strike 100 | เสี่ยงสับสนใน บท 5 — ควรเปลี่ยนสัญลักษณ์ฐานทุน |
| C, V | เงินสด, equity | ราคา call, Vega (`notation.html` §3) | ต้นฉบับเตือน C_T แล้ว แต่ยังไม่เตือน V = Vega |
| b | monetary basis F − S | b = odds ใน Kelly (`arb-part2b §7.1`, `notation.html` f* = p − q/b) | ใส่ในตารางชนกัน · นิยาม basis = F − S ตรงกับ `arb-part4 §15.3` แล้ว |
| γ | ความไวต่อ factor G | risk-aversion ใน Avellaneda-Stoikov (`notation.html` ตารางชนกัน) | ต้นฉบับเตือนเรื่อง gamma ของ options แล้ว ควรเพิ่ม Avellaneda-Stoikov |
| เวลาถึงหมดอายุ | τ | T (`math-part1`, `arb-part4`) | เลือกให้ตรงคลัง (T) หรือหมายเหตุ |
| ราคา | P_i (S, F เฉพาะ spot/futures) | S_t = ราคาสินทรัพย์ (`notation.html` §1) | รับได้ (ต้นฉบับใช้ S เฉพาะ spot ซึ่งตรง `math-part1 §3.8`) |
| ผลตอบแทน | R_i = simple return | `math-part9 §8.1`: "หนังสือทั้งเล่มทำงานกับ log return" | ระบุชัดเมื่อชี้ไป math-part9 |
| รอบ funding | "เปลี่ยนได้และต่างกันในแต่ละที่" (ข้อตกลงข้อ 6) | "ทุก 8 ชั่วโมง" (`arb-part1 §2.2`), /8hr (`eye-part1`, `eye-part3`, `pm-part7`) | ต้นฉบับถูกกว่า — ลิงก์ไปไฟล์เหล่านั้นต้องมีหมายเหตุ |
| ระดับความเชื่อ | หลักฐาน 4 ระดับ: อ่านวิธี/ตรวจโค้ด/รันตัวอย่าง/ทำซ้ำผล (ข้อตกลงข้อ 5) | 4 ระดับความแน่ใจของ claim: [Exact Identity]/[Contract-specific]/[Observed]/[Heuristic] (`arb-part2a §6.1`) | คนละแกน — ตั้งชื่อให้ต่างกันชัด และอธิบายว่าใช้ร่วมกันได้ |
| เกณฑ์ตายตัว | "ไม่มีค่า p, half-life, z-score … ค่าเดียวที่อนุญาตให้ซื้อขาย" (ต้นฉบับบท 9) | กฎตายตัว: \|z\|>2 เข้า / ≈0 ออก / \|z\|>4 stop (`arb-part5`, `math-part9`); "half-life เกิน 60 วัน อย่าเทรด" (`math-part9` 🎯) | เล่มใหม่ต้องบอกว่าเลขในคลังเป็น "ค่าเริ่มต้นของอีกเล่ม" ไม่ใช่กฎ เพื่อไม่ให้ขัดกันเงียบ ๆ |

### 5.3 ศัพท์ไทยที่ชนกัน/ต้องตรึง
- **"spread"** มีสองความหมายในคลัง: ส่วนต่างราคาซื้อ-ขาย (`nq-part5`, `nq-appendix-glossary.html`, `pillars-part3`) กับส่วนต่างของคู่ = residual (`math-part9` เตือนตรง ๆ ว่า "ไม่ใช่สเปรด bid-ask"). ต้นฉบับใช้ทั้งสองแบบ (glossary: "Spread = ค่าผสม P_A − hP_B" และ "Bid, ask และ mid") → เสนอ: ใช้ "ส่วนต่างราคาซื้อ-ขาย" ตาม nq สำหรับ bid-ask และ "spread ของคู่" (หรือ X) สำหรับคู่ ห้ามใช้คำว่า spread เดี่ยว ๆ
- **"ถอยสู่ค่าเฉลี่ย"** ใน `nq-part1` และ glossary ชั้น 1 = regression to the mean (เรื่องดวงในผลงาน) **ไม่ใช่** mean reversion ของ spread → เล่มใหม่ต้องใช้คำอื่น เช่น "แรงดึงกลับ" (`math-part9`, `notation.html`) หรือ "ดึงกลับหาค่าเฉลี่ย" (`theory-part5`) และเขียนกล่องแยกสองแนวคิด
- **"prediction"** (พยากรณ์ ในต้นฉบับ 05.07) ชนกับ "Prediction Markets"/"PM" (`arb-part8` บท 30, `arb-part1 §2.2`) และ "PM" ยังเป็นชื่อซีรีส์ Payoff Mastery (`pm-*`)
- **maker/taker** ต้นฉบับใช้อังกฤษ; nq ใช้ "คำสั่งตั้งรอ / คำสั่งซื้อทันที" และ "ผู้ดูแลสภาพคล่อง" (`nq-appendix-glossary.html` ชั้น 2) → ใช้คู่กัน: "คำสั่งตั้งรอ (maker)"
- **ครึ่งชีวิต** (`math-part9`) vs **half-life** (`arb-part5`, `theory-part5`, ต้นฉบับ) → แนะนำ "ครึ่งชีวิต (half-life)" ครั้งแรก

### 5.4 ศัพท์จาก glossary ของ nq ที่ผู้อ่านเล่มใหม่ "รู้แล้ว" และควรใช้คำเดิม
ฐาน (base rate) · ขนาดตัวอย่าง (n) · เส้นเสมอตัว · ความสุ่ม · อคติผู้รอดชีวิต · ส่วนเบี่ยงเบนมาตรฐาน · หางอ้วน · ถูกความผันผวนกิน · ส่วนต่างราคาซื้อ-ขาย · สภาพคล่อง · ใครอยู่อีกฝั่ง · เพดานความเสียหายต่อไม้ · การย่อจากจุดสูงสุด · สุ่มคืนกลับ · ค่าปรับจากการค้นหา · จดก่อนเทรด · มองอนาคต · จูนจนสวย · ทดสอบหลายครั้ง · เลเวอเรจ · ผลกลาง (ทั้งหมดจาก `nq-appendix-glossary.html`)

ค่าเริ่มต้นของ nq ที่ไม่ควรขัด (`nq-runbook.html`): เพดานความเสียหายต่อไม้ 1% ของทุน · เพดานรวมทั้งพอร์ต −20% แล้วหยุดทบทวน · ใช้คำสั่งตั้งรอเมื่อทำได้ · ค่าธรรมเนียมตัวอย่างของมิน 0.1% ต่อข้าง (`tools/nq_figures.py` `MIN_ACCOUNT`)

ข้อสังเกตคุณภาพ: `nq-appendix-glossary.html` มีคำซ้ำข้ามชั้น ("ส่วนต่างราคาซื้อ-ขาย" อยู่ทั้งชั้น 1 [Part 5] และชั้น 2 [Part 0]; "การตัดสินใจ ≠ ผลลัพธ์" อยู่ทั้งชั้น 1 [Part 8] และชั้น 2 [Part 2]) — ถ้าเล่มใหม่ยกตัวสร้าง glossary (`tools/nq_glossary.py`) ไปใช้ ควรเพิ่มการกันซ้ำ

---

## 6. ข้อเสนอการเชื่อมเล่มใหม่เข้าคลัง

### 6.1 ตำแหน่งและชื่อไฟล์
- เป็น **เล่มแยก** แบบเดียวกับ `nq-*` (ไม่ยัดเข้า arb/math) ตามหลักใน `quant-theory-volumes-plan.md` §0 ("ของใหม่ไม่มีบ้านเดิม → แยกเป็นเล่มใหม่")
- ใช้ prefix ใหม่ที่ไม่ชนกับ `nq-`, `statarb-ch*` (อ้างในบท nq แล้ว) และ `statarb-*` (บทเสริม 5 บท) — เช่น `sa-part0.html … sa-part20.html` + `sa-index.html` (ชื่อจริงให้ผู้ใช้ตัดสิน)
- สร้างไฟล์จากเปลือกเดียวกันด้วยแนวคิดของ `tools/nq_new_part.py` (CSS, palette, reading-path banner, Thai line-break script ชุดเดียว; ห้ามแก้ script ตัดคำด้วยมือ)

### 6.2 ฮับและทางเข้า
1. `index.html` — เพิ่มการ์ดเล่มใหม่ถัดจากกล่อง "📘 เล่มใหม่ในโปรเจกต์นี้: คิดแบบ Quant" (ปัจจุบัน index.html **ไม่ลิงก์บทเสริม statarb ทั้ง 5 เลย**)
2. `nq-index.html` — เพิ่ม "อ่านต่อ" ไปเล่มใหม่ (ปัจจุบันไม่มีลิงก์ statarb)
3. `nq-appendix-map.html` — บทเสริม statarb ทั้ง 5 **เข้าถึงได้จากหน้านี้หน้าเดียว**; เพิ่มแถวชี้เล่มใหม่ตามสถานี: ⑤ ต้นทุน → บท 3, 16 · ⑦ ขนาด → บท 0.4, 13 · ⑧ บันทึก → บท 15, 17 · ② ฐาน → บท 7
4. `sa-index.html` ของเล่มใหม่ควรเป็น **บ้านกลางของบทเสริม statarb ทั้ง 5** โดยผูกเข้าบท: บท 10 ↔ `statarb-alpha-decay` · บท 15 ↔ `statarb-data-quality` · บท 16–17 ↔ `statarb-live-vs-backtest` · บท 18 ↔ `statarb-signal-blending` · บท 19 ↔ `statarb-copula-practice`
5. บทเสริม statarb ทั้ง 5 ติดป้าย 🔵 และ `statarb-copula-practice` อ้าง `practice-part2` ที่ไม่มีในคลัง → เล่มใหม่บท 19 ควรเขียนบทนำ copula ระดับ 🟢 เพื่ออุดรูนี้ และให้ `statarb-copula-practice` ชี้กลับมาที่บทนั้นแทน (ถ้าผู้ใช้อนุมัติให้แก้บทเสริม)

### 6.3 กติกาอ้างอิง (ใช้ในกล่อง 🔗 อยากลึกกว่านี้)
- ทุกหัวข้อที่ตาราง 1 ให้ ✂️/🔗 ใช้ลิงก์หลักตามตาราง 1.1 — หนึ่งแนวคิดหนึ่งลิงก์หลัก ไม่ลิงก์ครบทุกบ้าน
- ไล่ระดับ: 🟢 nq/tool → 🔵 math/statarb → 🟣 theory/pillars (เหมือน "เส้นทางสี่แบบ" ใน `nq-appendix-map.html`)
- ลิงก์ไป `arb-part1 §2.2`, `eye-part3` บท 11, `pm-part7` Case 4 ต้องมีหมายเหตุเรื่องรอบ funding ไม่ตายตัว
- ลิงก์ไป `math-part9` ต้องหมายเหตุ: ใช้ β แทน h, θ แทน κ, log return แทน simple return

### 6.4 สัญลักษณ์และศัพท์
- เสนอให้ `notation.html` เพิ่มหมวด "8. Stat arb / ตลาดคริปโต": F, S, basis (b), implied carry (r^impl), T/τ, hedge ratio (h vs β), จำนวนถือ (q), spread ของคู่ (X), funding rate, θ vs κ — และเพิ่มแถว **spread** ในตาราง "ชนกัน"
- ตั้ง glossary ของเล่มใหม่แบบสร้างด้วยสคริปต์ (แนว `tools/nq_glossary.py`) จากกล่อง 📖 ศัพท์ใหม่ ≤12 คำ/บท และกันคำซ้ำ

### 6.5 QA และตัวเลข
- ขยาย `tools/nq_qa.py` (glob ปัจจุบัน = `nq-*.html` เท่านั้น — บทเสริม statarb ไม่ถูกตรวจ และตอนนี้ขาดกล่อง 📖 ศัพท์ใหม่ / ✍️ / 🎯 / 🔗 ทุกบท) หรือสร้างตัวตรวจคู่ขนานสำหรับเล่มใหม่
- ตัวเลขทุกตัวมาจากไฟล์เดียว (แนว `tools/nq_figures.py` → `docs/nq-figures.json` + `tools/nq_check_figures.py`) ตาม "กฎเหล็กข้อ 5: ห้ามพิมพ์ตัวเลขลอย ๆ" — โค้ดใน `code/` ของต้นฉบับ (standard library) แปลงเป็นสคริปต์ figures ได้
- แยกป้าย "ตัวเลขสมมติเพื่อสอน" (ข้อตกลงข้อ 1 ของต้นฉบับ) ออกจาก "ตัวเลขจากข้อมูลจริงในคลัง" (แนว nq) ให้ชัดทุกกล่อง
- กราฟเป็น inline SVG ตาม `SKILL.md` (แปลงภาพ PNG ในโฟลเดอร์ `figures/` ของต้นฉบับ)

### 6.6 เครื่องมือกดเล่น
- **ใช้ของเดิม (🔗)**: `nq-tool-breakeven` (บท 3), `nq-tool-samplesize` (บท 15, 17), `nq-tool-ruin` (บท 13), `tool-deflated-sharpe` (บท 7, 15), `tool-diversification` (บท 4, 13), `tool-carry-blowup` (บท 0.4, 6)
- **ช่องว่างที่ควรเป็นเครื่องมือของเล่มใหม่** (ยังไม่มีในคลัง): ตัวแปลง basis/funding → อัตราต่อปีและผลตอบแทนต่อทุนรวม margin · ระยะถึงราคา liquidation · half-life vs เวลาแตะเป้า (first-passage) · ตัวจำลองคู่ปลอมจากการค้นหาหลายคู่

### 6.7 ตัวละครและบัญชีตัวอย่าง
- บทเสริม statarb ใช้ "มิน" อยู่แล้ว และ `tools/nq_figures.py` ตรึงบัญชีมิน (ทุน 50,000 บาท, ค่าธรรมเนียม 0.1%/ข้าง, 2 ไม้/สัปดาห์) พร้อมกฎ "ทุกบทต้องใช้ชุดนี้ ห้ามเปลี่ยนกลางเล่ม" → ทางเลือก: (ก) ใช้มินต่อพร้อมบัญชี stat arb ใหม่ที่ประกาศชัด หรือ (ข) ตัวละครใหม่ — ตัดสินก่อนเขียน เพราะต้นฉบับใช้สินทรัพย์สมมติ A/B + BTC เป็นกรณีต่อเนื่อง

### 6.8 สิ่งที่ต้องถามผู้ใช้ก่อนลงมือ
1. Quant for Non-Quant มีไฟล์หรือไม่ / จะนำเข้าคลังไหม (กระทบตาราง 4.3 ทั้งหมด)
2. ซีรีส์ `statarb-ch*` ที่ nq อ้างถึงคือต้นฉบับนี้หรือคนละเล่ม
3. ยอมให้แก้บทเสริม statarb ทั้ง 5 และหน้ารวม (index, nq-index, nq-appendix-map, notation) เพื่อผูกเล่มใหม่หรือไม่
4. ใช้ κ หรือ θ, h หรือ β เป็นมาตรฐานของเล่มใหม่
