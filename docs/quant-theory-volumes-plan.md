# แผน Build เล่มใหม่ — 2 เล่ม เติมเต็มทฤษฎี Quant

> เอกสารนี้คือ **พิมพ์เขียวลงมือ** ต่อยอดจาก `quant-theory-book-plan.md`
> สรุปสิ่งที่ตกลงกันแล้ว + โครงต่อบทของเล่มใหม่ 2 เล่ม เพื่อให้เริ่มเขียนได้ทันที

---

## 0. สรุปงาน (Decisions ที่เคาะแล้ว)

| หัวข้อ | ข้อสรุป |
|---|---|
| **ทำอะไร** | สร้างเนื้อหา *ใหม่* เพื่อปิดช่องว่างทฤษฎี quant ที่เล่มเดิม (math/pm/arb/eye) ขาด |
| **แรงบันดาลใจ** | "5 Legendary Quant Theories" (Random Walk·Mean-Variance·CAPM·EMH·Options Pricing) + ผู้ใช้ขอเพิ่ม **Time Series** + ปิด gap ที่เหลือทั้งหมด |
| **แยกหรือรวม?** | **แยกเป็นเล่มใหม่** (ไม่ยัดเข้า 4 ซีรีส์เดิม) เพราะของใหม่ไม่มีบ้านเดิม + เล่มเดิมยังไม่รวมร่าง + เขียนเป็นโมดูลแล้วเสียบเข้า master spine ทีหลังปลอดภัยกว่า |
| **กี่เล่ม?** | **2 เล่ม** แบ่งตาม "โหมดอ่าน": เล่ม A = narrative (เรื่องเล่าตามไทม์ไลน์), เล่ม B = reference (อ้างอิงแยกสนาม) |
| **รูปแบบไฟล์** | HTML self-contained สไตล์เดียวกับของเดิม (Sarabun, กล่อง `.bx`, สูตร Unicode ใน `.fm`, SVG วาดมือ, `@media print`→PDF) วางใน `docs/` |
| **เทมเพลตบท** | Intuition → ทฤษฎี → สูตร → ตัวอย่างคำนวณ → **เชื่อมเล่มเดิม (cross-ref)** → กับดัก → กล่องสรุป |
| **กฎเหล็ก** | เขียนครั้งเดียวมีบ้านเดียว — เรื่องที่เล่มเดิมมีแล้ว ให้ *อ้างอิง* ไม่เขียนซ้ำ; ใช้ notation sheet กลางตาม `quant-theory-book-plan.md` |
| **รอบนี้ทำ** | **เล่ม A ก่อน** (ตรงกับรูป + เป็น gap ใหญ่สุดคือ Portfolio Theory), เล่ม B รอบถัดไป |

ความลึก: **สมดุล** เป็นค่าตั้งต้น (intuition หนัก + สูตรหลัก + ตัวอย่างคำนวณ; derivation สำคัญ ๆ เช่น Lagrangian ของ mean-variance / ที่มา BS ใส่ในกล่อง "เจาะลึก" ที่ข้ามได้) — *ยังรอผู้ใช้ยืนยัน*

---

## 1. เล่ม A — "ทฤษฎีตำนานของ Quant"  (`theory-part1..6.html`)

โหมด: เล่าเรื่องตามไทม์ไลน์ 5 ทฤษฎี → แต่ละทฤษฎีเป็น "ประตู" สู่หัวข้อ gap สมัยใหม่ที่มันให้กำเนิด

### Part I — ปฐมบท + Random Walk (1900) — `theory-part1.html`
- ไทม์ไลน์ 5 ทฤษฎี (1900→1973) + เล่มนี้จะพาไปไหน
- Bachelier, Brownian motion, random walk hypothesis: "ราคา = ความไม่แน่นอนที่มองเห็นได้"
- **ประตู → measure-theoretic probability**: σ-algebra, filtration, conditional expectation, **martingale** (กล่องเจาะลึก)
- เชื่อม: `math-part6` (stochastic+Itô), `eye` (มองโลกเป็นความไม่แน่นอน)
- ปิด gap: 🟡 measure/martingale

### Part II — Mean-Variance (1952) + CAPM/APT (1964) — `theory-part2.html`  ⭐ gap ใหญ่สุด
- Mean-variance: E(Rₚ)=Σwᵢe(Rᵢ), σₚ²=w'Σw, efficient frontier, two-fund theorem
- **เจาะลึก**: Lagrangian หา min σₚ² s.t. Σwᵢ=1, e(Rₚ)=μ*
- CAPM: SML, β, e[Rᵢ]=R_f+βᵢ(e[Rₘ]−R_f); APT
- **ขยายเติม gap**: factor models (Fama-French 3/5, Carhart momentum), Black-Litterman, risk parity, shrinkage covariance (Ledoit-Wolf), position sizing (Kelly → fractional)
- เชื่อม: `math-part4` (linear algebra), `math-part5` (optimization), `pm-part5a` (Kelly)
- ปิด gap: 🔴 **Portfolio Theory & Asset Pricing**

### Part III — Efficient Markets (1970) — `theory-part3.html`
- EMH 3 รูปแบบ (weak / semi-strong / strong) + joint hypothesis problem
- **limits to arbitrage** (Shleifer-Vishny), noise traders, ทำไม arb มีอยู่และทำไมมันหาย
- anomalies & factor zoo, p-hacking / multiple testing (โยงไป Part V)
- เชื่อม: `arb-part1` (นิยาม arb), `eye` (information edge)
- ปิด gap: 🟡 EMH / limits to arbitrage

### Part IV — Options Pricing / Black-Scholes (1973) — `theory-part4.html`  ⭐
- Risk-neutral pricing: replication + no-arbitrage → measure Q, **Girsanov** (กล่องเจาะลึก), fundamental theorem of asset pricing
- ที่มา BS: **BS PDE + Feynman-Kac** (เชื่อม PDE ↔ expectation); binomial → BS convergence
- Greeks (อ้างอิง `pm-part5a`, ไม่เขียนซ้ำ — เติมเฉพาะมุมทฤษฎี)
- ส่วนขยาย: American/exotics, vol surface, smile/skew, local vol (Dupire), stochastic vol (Heston/SABR), jump-diffusion (Merton)
- เชื่อม: `pm-part5a`, `math-part7` (BS+MC), `arb-part3` (vol arb)
- ปิด gap: 🔴 **Pricing theory เชิงลึก**

### Part V — Time Series (ผู้ใช้ขอเพิ่ม) — `theory-part5.html`  ⭐
- Stationarity, white noise, random walk vs AR(1) (โยงกลับ Part I)
- ACF/PACF → AR / MA / ARMA / ARIMA (วิธีเลือก order)
- **GARCH family** (vol clustering) → โยง vol forecasting
- **Cointegration** (Engle-Granger, Johansen) + VECM → pairs/stat-arb
- Regime-switching (Markov)
- **Backtest ที่เชื่อถือได้**: lookahead/survivorship bias, multiple testing, **deflated Sharpe**, purged/embargoed CV (López de Prado)
- เชื่อม: `math-part6` (time series+vol), `arb-part5` (pairs/mean-reversion/stat-arb/ML)
- ปิด gap: 🟠 Time series + ML rigor

### Part VI — สังเคราะห์ A + Cheat Sheet — `theory-part6.html`
- 5 ทฤษฎี + time series ร้อยกันเป็นภาพเดียว (แผนภาพความสัมพันธ์)
- map เข้า master spine (Part 0–XI) ของ `quant-theory-book-plan.md`
- Cheat sheet: สูตรหลัก + เมื่อไรใช้อะไร

---

## 2. เล่ม B — "เสาที่เหลือของ Quant (Engineering)"  (`pillars-part1..5.html`)

โหมด: คู่มืออ้างอิงแยกสนาม — 3 เสาที่ 5 รีลไม่พูดถึงแต่ quant ต้องมี *(ทำรอบถัดไป)*

### Part I — Fixed Income & Rates — `pillars-part1.html`
yield curve, bootstrapping, duration/convexity, DV01; term-structure models (Vasicek, CIR, Hull-White, HJM, LMM เบื้องต้น); bond/swap/FRA/swaption pricing
→ ปิด gap: 🔴 **Fixed Income / Rates**

### Part II — Credit — `pillars-part2.html`
hazard rate, **CDS pricing**, structural (Merton) vs reduced-form default models
→ ปิด gap: 🔴 Credit

### Part III — Market Microstructure — `pillars-part3.html`
order book dynamics, adverse selection (**Glosten-Milgrom, Kyle**), market making (**Avellaneda-Stoikov**) + inventory risk, optimal execution (**Almgren-Chriss**), market impact / TCA
→ เชื่อม: `arb-part7`, `pm-part7` (execution reality) · ปิด gap: 🟠 Microstructure

### Part IV — Risk Management Theory — `pillars-part4.html`
**VaR / CVaR (Expected Shortfall)**, coherent risk measures, factor risk decomposition, stress testing; performance metrics (Sharpe/Sortino/Information Ratio/Calmar), drawdown control; backtest pitfalls (โยง เล่ม A Part V)
→ เชื่อม: `arb-part7`, `pm-part5/7` · ปิด gap: 🟠 Risk theory

### Part V — สังเคราะห์ B + แผนที่ "เติมเต็มครบแล้ว" — `pillars-part5.html`
รวม 3 เสา + ตารางยืนยันว่า gap แดง/ส้ม/เหลือง *ทั้งหมด* จาก `quant-theory-book-plan.md` ถูกปิดครบ

---

## 3. ตารางปิด Gap (ยืนยันว่าครบ)

| Gap (จากแผนเดิม) | ปิดที่ |
|---|---|
| 🔴 Portfolio Theory & Asset Pricing | เล่ม A · Part II |
| 🔴 Fixed Income / Rates / Credit | เล่ม B · Part I–II |
| 🔴 Pricing theory เชิงลึก | เล่ม A · Part IV |
| 🟠 Microstructure theory | เล่ม B · Part III |
| 🟠 Econometrics / ML rigor | เล่ม A · Part V |
| 🟠 Risk theory | เล่ม B · Part IV |
| 🟡 Measure-theoretic probability | เล่ม A · Part I |
| 🟡 EMH / limits to arbitrage | เล่ม A · Part III |
| (เพิ่มตามคำขอ) Time Series | เล่ม A · Part V |

➡️ ครบทุก gap

---

## 4. ลำดับงาน (Build Order)

**Phase A1** — ✅ เสร็จ: เล่ม A Part I–II (Random Walk, Portfolio/CAPM) ผ่านรีวิวทีม
**Phase A2** — ✅ เสร็จ: เล่ม A Part III–VI (EMH, Pricing, Time Series, สังเคราะห์) ผ่านรีวิวทีม
→ **เล่ม A "ทฤษฎีตำนานของ Quant" ครบ 6 ตอน** (`theory-part1..6.html`) ทุกตอนผ่านคณะผู้เชี่ยวชาญ 3–4 คน
**Phase B**  — ⏳ ถัดไป: เล่ม B Part I–V (Fixed Income/Credit, Microstructure, Risk, สังเคราะห์) — `pillars-part1..5.html`
**Phase F**  — อัปเดต `quant-theory-book-plan.md` ให้ map เล่ม A/B เข้า master spine + (ถ้าต้องการ) ทำหน้า index รวม + generate PDF

แต่ละ Phase: commit แยก + push เข้า branch `claude/quant-theory-book-plan-s0qs7u` (PR #5 อัปเดตอัตโนมัติ)

## 4.5 มาตรฐานเนื้อหา v2 — จากคณะผู้เชี่ยวชาญ 4 คน (บังคับใช้ทุก Part)

หลังให้ผู้เชี่ยวชาญ 4 เลนส์ (pricing/stochastic · asset-pricing academic · buy-side practitioner · บรรณาธิการการสอน) รีวิว Part I ได้มาตรฐานที่ต้องยึดทั้งเล่ม:

**A. การ์ดทฤษฎี = 9 องค์ประกอบ** (เดิม 6):
Thesis → **❓ ทำไมต้องรู้จัก** (ถ้าไม่รู้จะพลาด/ต่อยอดอะไรไม่ได้ — ทำไม*ผู้อ่าน*ต้องเสียเวลากับมัน, กล่อง `.why` เส้นประ) → ใช้ทำอะไร → ใช้ได้เมื่อไร → พังเมื่อไร → **⚖️ ข้อดี/ข้อเสีย** (2 คอลัมน์) → **🧠 มุมที่ quant มองต่าง** (สีม่วง, รูปแบบ "คนทั่วไปเห็น X / quant เห็น Y", 1–2 ประโยค) → ปัจจุบันใช้จริง → Papers
- ★★ ใช้ **mini-card** ได้: Thesis + ทำไมต้องรู้ + พังเมื่อไร + มุม quant + Paper (ย่อแบบ *ตั้งใจ* ไม่ใช่ตกหล่น)
- "พังเมื่อไร" = failure mode เชิงเทคนิค; "ข้อดี/ข้อเสีย" = trade-off เชิงปฏิบัติ — ห้ามซ้ำกัน

**B. เล่าเรื่องให้คนรัก quant**: วาง hook (เรื่องจริง) ก่อนตารางหนัก ๆ, มี pull-quote, ปิดแต่ละตอนด้วย cliffhanger เชื่อม Part ถัดไป — ใช้ metaphor เดียว ("เลโก้")

**C. ระบบศัพท์**: เก็บอังกฤษ + ไทยในวงเล็บครั้งแรก + `<abbr title>` tooltip + กล่อง "ศัพท์ใหม่ในตอนนี้" ท้าย Part

**D. ความถูกต้องที่ต้องระวัง (บทเรียนจาก Part I)**:
- √time ใช้กับ σ·dW เท่านั้น (drift โตเชิงเส้น); แยก arithmetic vs **geometric BM** (BS/√252 ใช้ GBM); ใส่ vol drag −σ²/2
- martingale ⊋ random walk; Grossman-Stiglitz อธิบายว่าทำไม edge มี
- citation แม่นปี/ผู้แต่ง: "Harrison-Kreps (1979) & Harrison-Pliska (1981)" แยกกัน; CVaR เครดิต Rockafellar-Uriasev (2000) ด้วย; **GARCH = Engle 1982 ไม่ใช่ยุค ML**
- Part II ต้องมี: mean-variance Lagrangian + estimation error (error-maximizer), CAPM assumptions + Roll's critique + เหตุที่ β พังจริง, joint-hypothesis, FF เป็น "การปะ CAPM"
- ห้าม hallucinate paper — ไม่แน่ใจให้ตัดออก

**E. ทฤษฎีที่เพิ่มเข้าแผนที่** (จาก practitioner): GARCH, Cointegration/Engle-Granger+OU, SDF (Hansen-Jagannathan), Markov regime-switching (Hamilton 1989), market-impact/√-law/capacity, Avellaneda-Lee stat arb — และกลุ่ม "เครื่องมือเชิงเวลา" เป็นแกนของ Part V

**F. เรตติ้งปรับ**: M-M ★→★★ · ICAPM ★→★★ · Coherent Risk/CVaR ★★→★★★ · GARCH/Cointegration/Grossman-Stiglitz = ★★★

## 4.6 Style Guide (typography + การเขียน) — จากทีมบรรณาธิการ/ภาษา (บังคับใช้ทุกไฟล์)

หลังผู้ใช้รายงานปัญหา "ประโยคขึ้นบรรทัดใหม่กลางคำ อ่านไม่ได้ใจความ" ทีมภาษา+i18n+book editor ตรวจแล้วสรุปมาตรฐาน:

**A. Line-break ภาษาไทย (เทคนิค — มีในทุกไฟล์แล้ว):**
- CSS body: `word-break:normal;word-break:auto-phrase;overflow-wrap:break-word;line-break:loose;text-wrap:pretty;hanging-punctuation:allow-end`
- ฝัง `<script>` (Intl.Segmenter('th') → ฉีด `<wbr>` ที่ขอบเขตคำไทย) ก่อน `</body>` — ข้าม `.fm`/code/script, ใช้ `<wbr>` (copy สะอาด) ไม่ใช่ U+200B, idempotent
- mobile: `.fm{font-size:.82em}` ลด horizontal scroll สูตร

**B. โครงสร้าง HTML (สำคัญสุดต่อการอ่าน):**
- รายการ (bullet/เลข ≥2 ข้อ) → ใช้ `<ul>/<ol><li>` เสมอ **ห้าม** จำลองด้วย `•`+`<br>`
- ร้อยแก้วหลายย่อหน้าในกล่อง → `<p>` หลายอัน ไม่ใช่ `<br><br>`
- `<br>` เดี่ยวสงวนไว้เฉพาะ: คู่ "คนทั่วไปเห็น/quant เห็น" ใน `.qv`, และคู่บรรทัดสูตรใน `.fm`
- `.fm` เก็บ**เฉพาะสูตร**; คำอธิบายไทยยาว ๆ ย้ายออกมาเป็น `<p>/<ul>` (ไทยใน monospace อ่านยาก)

**C. การเขียน:**
- ประโยค ≤ ~2 บรรทัดจอ; ถ้าต้องมี (1)(2)(3) ในประโยคเดียว = สัญญาณให้เป็น `<ul>`; em-dash `—` ≤1 ตัว/ประโยค; `.qv` ฝั่ง "quant เห็น" ≤ ~2 ประโยค
- เว้นวรรครอบคำอังกฤษ/ตัวเลขที่แทรกในไทยเสมอ; ตัวคั่น inline มาตรฐาน = ` · `
- ศัพท์เทคนิคคงอังกฤษ; ครั้งแรกต่อ Part ใส่ไทยในวงเล็บ **หรือ** `<abbr title>` (อย่างใดอย่างหนึ่ง)

**D. จังหวะ/ความหนาแน่น:**
- กล่องสีติดกัน ≤4 ต่อการ์ด (เกินนั้นยุบเนื้อรองเป็นร้อยแก้ว) เพื่อคง visual hierarchy
- ทุก Part เนื้อหา: ≥1 `.pq` คั่น section + ≥1 กล่องเคส 📉 "เมื่อทฤษฎีพังจริง" + ปิดด้วยกล่องสรุป ✓ + `.pq` สะพานสู่ Part ถัดไป
- ทุก Part ปิดด้วยกล่อง "📖 ศัพท์ใหม่ในตอนนี้" (บทปิดเล่มใช้ quick index แทนได้)

## 4.6 มาตรฐานเนื้อหา v3 — Papers/Review + ตัวอย่างการใช้งาน (ผู้ใช้ขอ)

เพิ่ม 2 องค์ประกอบ (ใช้ทุก Part ต่อจากนี้ + retrofit เล่ม A):
- **📖 อ่านต่อ (review / ตำรา):** กล่องท้าย Part รวม survey papers + handbook มาตรฐาน (แยกจาก "📚 Papers" ที่เป็นต้นฉบับของทฤษฎี) — ช่วยผู้อ่านขุดต่อและรองรับส่วนที่อัปเดต (เช่น SOFR, rough vol)
- **🧮 ตัวอย่างการใช้งาน (worked example):** กล่องตัวเลขจริงในการ์ด ★★★ ที่ช่วยได้มากสุด (เช่น carry+roll = 1.76%, duration → −17%) — ทำให้ทฤษฎี "จับต้องได้" ไม่ใช่แค่สูตร
- ห้าม hallucinate: อ้างเฉพาะตำรา/paper ที่มีจริง; ถ้าไม่มั่นใจให้ตัด

## 5. Convention ที่ต้องคุมให้ตรงกัน
- **Notation**: `S, K, r, q, σ, T, Φ(·), w, Σ, β, R_f, R_m` ใช้เหมือนกันทั้ง 2 เล่มและตรงกับแผนเดิม
- **เลขบท**: ภายในแต่ละเล่มเรียงต่อเนื่อง; ใส่ป้าย gap ที่ปิดทุกบท
- **Cross-ref**: ลิงก์/อ้างอิงไฟล์เดิมแทนการเขียนซ้ำเสมอ
- **Difficulty tier**: ติด L1/L2/L3 ทุกบท; กล่อง "เจาะลึก (ข้ามได้)" สำหรับ derivation
