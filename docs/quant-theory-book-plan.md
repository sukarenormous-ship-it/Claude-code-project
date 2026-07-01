# แผนทำหนังสือ "ทฤษฎีของ Quant" — รวมเล่ม + เติมส่วนที่ขาด

> เอกสารนี้คือ *พิมพ์เขียว* สำหรับเปลี่ยนเนื้อหาเดิม 4 ซีรีส์ (math / arb / pm / eye)
> ให้กลายเป็น **หนังสือเล่มเดียวที่สอดคล้องกัน** แล้วระบุ **ช่องว่างทางทฤษฎี (gaps)**
> ที่ต้องเขียนเพิ่มเพื่อให้ครบ "ทฤษฎีของ quant" จริง ๆ

---

## 1. เริ่มจากความจริง: ตอนนี้เรามีอะไรอยู่แล้ว

ในโฟลเดอร์ `docs/` มีเนื้อหาอยู่แล้ว **4 ซีรีส์** (รวม ~30+ ไฟล์ HTML/PDF) ซึ่งแข็งแรงมากแต่ **เขียนแยกกัน เนื้อหาทับซ้อน และยังไม่ถูกร้อยเป็นเล่มเดียว**

| ซีรีส์ | ไฟล์ | แก่นเรื่อง | บทบาทในเล่มรวม |
|---|---|---|---|
| **Math for Options** (`math-part1..7`) | บท 1–16 + ภาคผนวก | พีชคณิต, สถิติ, ความน่าจะเป็น, distributions, แคลคูลัส, linear algebra, regression, optimization (LP/NLP), time series, stochastic processes + Itô, Black‑Scholes, Monte Carlo | **รากฐานคณิตศาสตร์** |
| **Payoff Mastery** (`pm-part0..8`) | บท 1–28 + Part 0/3a/4a/5a | Payoff chart, PCP, synthetics, spreads, butterfly/condor/calendar/ratio, reading engine, slope decomposition, BS pricing, Greeks จากกราฟ, Breeden‑Litzenberger, Kelly, dynamic payoff, จิตวิทยา | **การอ่าน/ประกอบ Payoff & structuring** |
| **Arbitrage** (`arb-part1..9`) | บท 1–33 | นิยาม arb, taxonomy L1–L5, search pipeline, PCP/box/vol arb, cash & carry, FX/triangular, ETF/ADR, pairs/mean‑reversion/factor stat‑arb/ML, merger arb, event‑driven, execution, risk, infra, case studies | **กลยุทธ์และภาคปฏิบัติ** |
| **The Eye of the Arbitrageur** (`eye-part1..5`) | บท 1–22 | มองโลกเป็น option, conditional payoff, replication, deconstruction/construction, cross‑market translation, hidden options, MEV, inventing new arb | **กรอบความคิด/สายตา (intuition)** |

**ข้อสังเกตสำคัญ 2 ข้อ:**

1. **เนื้อหาทับซ้อนสูง** — เช่น *Put‑Call Parity* ปรากฏใน math, pm, arb, eye; *Payoff Algebra* อยู่ใน arb, pm, eye; *Black‑Scholes* อยู่ทั้ง math และ pm; *Prediction Markets* อยู่ใน arb, pm, eye → ถ้ายกมารวมตรง ๆ จะอ่านวน ซ้ำ และขัดกันเอง
2. **ขอบเขตยังเอียงไปทาง Options + Arbitrage** — ซึ่งคือ "ครึ่งหนึ่ง" ของทฤษฎี quant เท่านั้น ส่วนเสาหลักอีกหลายต้น (portfolio theory, fixed income, microstructure, risk theory ฯลฯ) **ยังไม่มีเลยหรือมีแบบผิว ๆ** → นี่คือ "ส่วนที่ขาด" ที่ต้องเติม

---

## 2. หลักการวางแผน 4 ข้อ (ตอบโจทย์ "สอดคล้อง + เติมส่วนที่ขาด")

1. **One Spine, Not Four Series** — ยุบ 4 ซีรีส์เป็นโครงเดียว มีลำดับ prerequisite ชัด ไม่ใช่ 4 เล่มวางข้างกัน
2. **Write Once, Reference Everywhere** — แต่ละแนวคิดมี "บ้านหลังเดียว" (canonical chapter) ที่อื่นอ้างอิงแทนที่จะเขียนซ้ำ
3. **Theory → Pricing → Strategy → Practice** — ทุกหัวข้อไหลตามสายนี้ เพื่อให้ของเดิม (เน้น strategy/intuition) กับของใหม่ (เน้น theory) เชื่อมกันสนิท
4. **Fill the Pillars** — เติมเสาหลักที่ขาดให้หนังสือครอบคลุม "quant" ทั้งสนาม ไม่ใช่แค่ options trader

---

## 3. โครงเล่มใหม่ (Unified Table of Contents)

แต่ละ Part ระบุว่า **[มีแล้ว]** (ดึงจากของเดิม), **[ผสาน]** (รวมหลายซีรีส์เข้าด้วยกัน), หรือ **[เขียนใหม่]** (gap ที่ขาด)

### Part 0 — สายตาของ Quant (Mindset)
มองโลกเป็น payoff/option, conditional payoff, replication, ทำไมถึงทรงพลัง
**[มีแล้ว]** ← eye 1–4, pm‑part0

### Part I — รากฐานคณิตศาสตร์
พีชคณิต, exp/log/ดอกเบี้ย/PV, สถิติ, ความน่าจะเป็น, distributions, แคลคูลัส, linear algebra, regression, optimization, time series เบื้องต้น, stochastic process + Itô, Monte Carlo
**[มีแล้ว]** ← math 1–16
**[เขียนใหม่ — เติม]** ความเข้มของ probability เชิง measure: σ‑algebra, expectation as integral, **martingale, filtration, conditional expectation** (จำเป็นต่อ pricing theory ที่เข้มขึ้น)

### Part II — Payoff & Structuring
Payoff chart, 2‑step slope, synthetics, spreads/straddle, butterfly/condor/calendar/ratio, reading engine, slope decomposition, reverse engineering, Payoff Algebra
**[มีแล้ว]** ← pm 1–16, eye 5–6

### Part III — ทฤษฎีการตั้งราคา (Pricing Theory) ⭐ *เติมเยอะ*
- **[มีแล้ว]** Black‑Scholes (เล่าเรื่อง), digital option, Greeks, Breeden‑Litzenberger ← pm‑part5a, math‑part7
- **[เขียนใหม่]** **Binomial / lattice** เต็มรูป (Cox‑Ross‑Rubinstein), convergence → BS
- **[เขียนใหม่]** **Risk‑neutral pricing อย่างเป็นทางการ**: measure Q, Girsanov, fundamental theorem of asset pricing
- **[เขียนใหม่]** **PDE approach**: Black‑Scholes PDE + **Feynman‑Kac** (เชื่อม PDE ↔ expectation)
- **[เขียนใหม่]** **American options** (early exercise, free boundary), **exotics** (barrier, Asian, lookback, digital ที่ลึกขึ้น)
- **[เขียนใหม่]** **Volatility modeling**: implied vol surface, **local vol (Dupire)**, **stochastic vol (Heston, SABR)**, **jump‑diffusion (Merton)**, skew/term‑structure แบบมีโมเดล

### Part IV — Arbitrage & Strategies
นิยาม/taxonomy L1–L5, search pipeline, PCP/box/synthetic arb, vol arb, cash & carry, FX/triangular, ETF/ADR, pairs/mean reversion/factor stat‑arb/ML, merger arb, event‑driven, hidden options, time‑structure arb, MEV
**[มีแล้ว]** ← arb 1–33, eye 7–13, 18–21

### Part V — Econometrics & Machine Learning ⭐ *เติมเยอะ*
- **[มีแล้ว]** time series & vol forecasting เบื้องต้น, ML ใน stat arb ← math‑part6, arb‑part5
- **[เขียนใหม่]** **GARCH family** (GARCH/EGARCH/GJR), **cointegration** (Engle‑Granger, **Johansen**), **VAR/VECM**, **regime‑switching (Markov)**
- **[เขียนใหม่]** **Bayesian methods** สำหรับ quant (shrinkage, hierarchical, MCMC เบื้องต้น)
- **[เขียนใหม่]** **ML ทำถูกวิธี (López de Prado)**: labeling (triple‑barrier), **purged/embargoed CV**, feature importance, **overfitting & deflated Sharpe**, backtest ที่เชื่อถือได้

### Part VI — Portfolio Theory & Asset Pricing ⭐ *เกือบไม่มีเลย — gap ใหญ่ที่สุด*
- **[เขียนใหม่]** **Mean‑Variance / Markowitz**, efficient frontier, two‑fund theorem
- **[เขียนใหม่]** **CAPM, APT**, security market line, beta
- **[เขียนใหม่]** **Factor models** (Fama‑French 3/5, Carhart momentum, q‑factor), risk premia, factor zoo & p‑hacking
- **[เขียนใหม่]** **Black‑Litterman**, **risk parity**, shrinkage covariance (Ledoit‑Wolf)
- **[ผสาน/ขยาย]** **Position sizing**: Kelly (มีแล้วใน pm‑part5a) → fractional Kelly, drawdown‑aware sizing

### Part VII — Fixed Income, Rates & Credit ⭐ *ไม่มีเลย — gap ใหญ่*
- **[เขียนใหม่]** yield curve, bootstrapping, **duration/convexity**, DV01
- **[เขียนใหม่]** term‑structure models: **Vasicek, CIR, Hull‑White, HJM, LMM** เบื้องต้น
- **[เขียนใหม่]** bond/swap/FRA pricing, swaption
- **[เขียนใหม่]** credit: hazard rate, **CDS pricing**, structural (Merton) vs reduced‑form default

### Part VIII — Market Microstructure & Execution ⭐ *มีภาคปฏิบัติ ขาดทฤษฎี*
- **[มีแล้ว]** execution reality, edge ตายตรง bid/ask, infrastructure ← arb‑part7, pm‑part7
- **[เขียนใหม่]** order book dynamics, **adverse selection (Glosten‑Milgrom, Kyle)**
- **[เขียนใหม่]** **market making (Avellaneda‑Stoikov)**, inventory risk
- **[เขียนใหม่]** **optimal execution (Almgren‑Chriss)**, market impact & transaction‑cost models

### Part IX — Risk Management & Performance ⭐ *มีพื้นฐาน ขาดทฤษฎี*
- **[มีแล้ว]** risk management เบื้องต้น, scenario/stress testing, feasibility, anti‑patterns ← arb‑part7, pm‑part5/7
- **[เขียนใหม่]** **VaR / CVaR (Expected Shortfall)**, coherent risk measures, factor risk decomposition
- **[เขียนใหม่]** performance metrics: Sharpe/Sortino/Information Ratio/Calmar, drawdown control
- **[เขียนใหม่]** **backtesting pitfalls**: lookahead, survivorship, multiple testing, **deflated/PBO** (เชื่อมกับ Part V)

### Part X — ตลาดมีประสิทธิภาพแค่ไหน & จิตวิทยา
EMH, anomalies, **limits to arbitrage (Shleifer‑Vishny)**, behavioral biases (Kahneman)
**[ผสาน]** ← pm‑part8 (จิตวิทยา) **[เขียนใหม่ — เติม]** EMH / limits to arbitrage เชิงทฤษฎี

### Part XI — Capstone: Drills, Cases & Decision Frameworks
workshop drills, case simulation, real cases, cheat sheets, missions
**[มีแล้ว]** ← pm‑part6, arb‑part8/9, eye‑part4

---

## 4. สรุป "ส่วนที่ขาด" (Gap Map) — เรียงตามความสำคัญ

| ลำดับ | ส่วนที่ขาด | สถานะปัจจุบัน | ทำไมต้องมี |
|---|---|---|---|
| 🔴 1 | **Portfolio Theory & Asset Pricing** (Part VI) | แทบไม่มี | เสาหลักของ quant ทั้งสาย buy‑side; ไม่มีแล้วเรียกว่า "ทฤษฎี quant" ไม่ได้ |
| 🔴 2 | **Fixed Income / Rates / Credit** (Part VII) | ไม่มีเลย | ตลาดใหญ่ที่สุดในโลก; เป็นบ้านเกิดของ quant ดั้งเดิม |
| 🔴 3 | **Pricing Theory ที่เข้ม** — measure Q, PDE/Feynman‑Kac, stochastic vol, exotics, American (Part III) | มีแค่ BS เล่าเรื่อง | ยกระดับจาก "ผู้ใช้สูตร" เป็น "ผู้เข้าใจสูตร" |
| 🟠 4 | **Microstructure theory** — Kyle, Almgren‑Chriss, Avellaneda‑Stoikov (Part VIII) | มีภาคปฏิบัติ | อธิบาย "ทำไม edge ตายตรง bid/ask" ด้วยโมเดล |
| 🟠 5 | **Econometrics/ML rigor** — GARCH, cointegration, deflated Sharpe (Part V) | ผิว ๆ | กันการหลอกตัวเองด้วย backtest ปลอม |
| 🟠 6 | **Risk theory** — VaR/CVaR, coherent measures, backtest pitfalls (Part IX) | พื้นฐาน | เปลี่ยน risk จาก checklist เป็นกรอบเชิงปริมาณ |
| 🟡 7 | **Measure‑theoretic probability** — martingale, filtration (Part I) | ขาด | prerequisite ของ #3 |
| 🟡 8 | **EMH / limits to arbitrage** เชิงทฤษฎี (Part X) | ขาด | กรอบอธิบายว่า "ทำไม arb ถึงมี/หายไป" |

---

## 5. กฎความสอดคล้อง (Consistency Rules) — ทำให้ "ร้อยเป็นเล่มเดียว" จริง

1. **Single numbering** — เลขบทเดียวทั้งเล่ม (Ch.1–N) แทนที่จะ reset ทุกซีรีส์
2. **Notation sheet** — ตารางสัญลักษณ์กลาง 1 หน้า: `S, K, r, q, σ, τ, Φ(·)`, ฯลฯ ใช้เหมือนกันทั้งเล่ม (ตอนนี้แต่ละซีรีส์เขียนคนละแบบ)
3. **Canonical home + cross‑ref** — กำหนดว่าแต่ละหัวข้อทับซ้อนอยู่บ้านไหน:
   - *Put‑Call Parity* → บ้านหลักที่ Part II, ที่อื่นอ้างอิง
   - *Payoff Algebra* → Part II
   - *Black‑Scholes (เล่าเรื่อง)* → Part II, *(เชิงทฤษฎี)* → Part III
   - *Prediction Markets* → Part IV (จุดเดียว)
4. **Prerequisite graph** — ทุกบทระบุ "ต้องอ่านบทไหนก่อน" ทำเป็นแผนภาพหน้าแรก
5. **Difficulty tier** — ติดป้าย L1 (intuition) / L2 (working) / L3 (theory) ทุกบท ให้ผู้อ่านเลือกเส้นทางได้
6. **Template เดียว** — ทุกบทมีโครงเดียวกัน: *Intuition → Theory → Formula → Worked example → Drills → Pitfalls → Cheat box*
7. **De‑dup pass** — รอบหนึ่งไล่ลบเนื้อหาซ้ำข้ามซีรีส์ แทนด้วย cross‑reference

---

## 6. Roadmap การลงมือ (แนะนำลำดับ)

**Phase 1 — รวมเล่ม (ไม่เขียนเนื้อหาใหม่):** ทำ master TOC, notation sheet, prerequisite graph, de‑dup, แปลง 4 ซีรีส์ให้เลขบท/เทมเพลตเดียวกัน → ได้ "เล่ม v1" ที่สอดคล้องจากของเดิมล้วน ๆ

**Phase 2 — เติม gap แดง (เสาหลักที่หาย):** เขียน Part VI (Portfolio), Part VII (Fixed Income), เสริม Part III (Pricing theory) — นี่คือสิ่งที่ทำให้กลายเป็น "ทฤษฎี quant" จริง

**Phase 3 — เติม gap ส้ม/เหลือง:** Part VIII (microstructure), Part V (econometrics/ML rigor), Part IX (risk theory), เสริม Part I (measure), Part X (EMH)

**Phase 4 — เก็บงาน:** Capstone ใหม่ที่ดึงข้ามทุก Part, ตรวจ cross‑ref, index ศัพท์, ออกเป็น PDF เล่มเดียว

**เกณฑ์ "เล่มเสร็จ":** ผู้อ่านที่เริ่มจาก Part 0 เดินจนจบได้โดยไม่ต้องไปหาแหล่งอื่นเพื่อเข้าใจเสาหลักทั้ง 8 ต้นของ quant (math, payoff, pricing, strategy/arb, econometrics/ML, portfolio, fixed income, microstructure/risk)

---

## 7. ของเดิม → Part ในเล่มใหม่ (mapping อ้างอิงเร็ว)

```
eye-part1..4            → Part 0
math-part1..7           → Part I  (+ เติม measure)
pm-part0..3a, eye-5..6  → Part II
pm-part5a, math-part7   → Part III (+ เขียนใหม่เยอะ)
arb-part1..9, eye-7..21 → Part IV
math-part6, arb-part5   → Part V  (+ เขียนใหม่)
(ไม่มี)                  → Part VI  ✦ ใหม่ทั้งหมด
(ไม่มี)                  → Part VII ✦ ใหม่ทั้งหมด
arb-part7, pm-part7     → Part VIII (+ ทฤษฎีใหม่)
arb-part7, pm-part5/7   → Part IX  (+ ทฤษฎีใหม่)
pm-part8                → Part X   (+ EMH ใหม่)
pm-part6, arb-part8/9   → Part XI
```
