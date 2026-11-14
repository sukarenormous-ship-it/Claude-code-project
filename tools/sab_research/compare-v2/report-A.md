# Report A — Example "ภาคพื้นฐาน + ตอน A–C" vs our chapters 0, 1, 2, 3, 4, 8, 11

Scope read in full:
- Example `ea8791aa-Stat_Arb_Hands_On_Complete_v1_0.md` lines 55–1635 (ภาคพื้นฐาน, เริ่ม 1–4, 0.1–0.3, ตอน A, B, C), 4134–4234 (P0–P10), 4971–5106 (hints H_A–H_C, solutions S1–S11).
- Ours `sab-part{0,1,2,3,4,8,11}.txt` in full. For two fairness checks I also grepped ch 9, 13–16 and the appendices (noted where used).
- "EX L123" = example line number. "Ours ch3 §heading (txt L80)" = our chapter, heading, line in the `.txt`.
- No repo file was edited.

---

## 0. Measurements (so the rest is not guesswork)

Method: Python over the raw text; "visible chars" = characters excluding spaces and Thai combining marks (Thai has no word spaces, so chars is the honest unit). Body prose only (tables, headings, captions, code excluded).

| Measure | Example (L55–1635) | Ours (7 chapters) |
|---|---|---|
| Body prose, visible chars | 79,455 | 57,763 total, but only **39,427 is "teaching zone"** (first `##` to the `⚠️ ค่าเริ่มต้น` box) |
| Share of chapter that is teaching vs apparatus | n/a (linear text) | teaching 38–48% per chapter; **apparatus after it 42–52%** (cards, worksheets, exercises, glossary, links) |
| Avg paragraph (visible chars) | 171 overall; **131 in ภาคพื้นฐาน**; 197–221 in A–C | 74–103 per chapter (ours is shorter per item) |
| Distinct technical concepts taught (my hand count) | ≈ 35 | ≈ 60 |
| Explanation per concept | ≈ 2,270 chars | ≈ 650 chars (**≈ 3.5× less explanation per concept**) |
| New-term density, opening chapter | ภาคพื้นฐาน 1–5 (L55–370): **4 English terms** (long, short, entry price, exit price) + 2 Thai (สถานะ, ขา). Whole ภาคพื้นฐาน (29,952 chars): 12 distinct Latin words ≈ 1 new term / 2,500–3,000 chars | ch0 teaching zone (6,151 chars): 11 glossed English terms + ~6 unglossed (ขา, dated futures, perp, funding, stat arb, exchange) ≈ **1 new term / 360 chars (7–8× denser)** |
| Terms before the first worked number | 0 (first number at EX L67 is "ซื้อ B หนึ่งหน่วยที่ราคา 100 บาท"; the word *long* arrives at L81, after the result) | ch0: **6 terms in the first 1,462 chars** (exchange, Futures, Spot, วันหมดอายุ, Long, Short) before the first worked row at txt L51 — and that row already uses a fractional quantity and a signed-quantity formula |
| First formula | EX L466 (`x = A − 2B`), after ~410 lines; first signed-quantity formula EX L941, after ~880 lines | ch0 txt L59, three paragraphs after *long* is first defined |
| Display formulas preceded by a full numeric walk | 10 of 10 | 13 `[[fm]]`; 🚶 plain-language line precedes most (14 🚶 total), but the numeric walk precedes the formula in only about half (see §2) |
| "พักตรงนี้ได้" checkpoints | 5 (EX L104, 138, 213, 282, 354 — all inside พื้นฐาน 1–5, **none in A–C**) | 0 mid-chapter (we have "🎯 3 อย่างที่ต้องจำ" + "สรุป" only at chapter end) |
| "อ่านภาพ:" lines | 19 (19 of 19 figures) | 0 "how to read" lines; 12 `[[cap]]` captions that state assumptions, not reading order |
| "อ่านสมการ:" lines with numbers substituted | 10 (10 of 10 equations) | 0 as a fixed device |
| 🛑 predict-before-reveal boxes | 0 formatted (only "ลอง…" prompts in prose, 91 uses of ลอง) | 13 |
| Forward references "(บท N)" inside teaching zone | few, mostly "A.4 จะ…" | **30** (ch0: 9, ch1: 5, ch2: 6, ch3: 3, ch4: 1, ch8: 2, ch11: 4) |
| Tables / figures | 35 / 19 | 41 / 12 |
| Repetition marker "ก่อนต้นทุน" | 24× | — |

Worked numeric steps for the same concept (hand count):

| Concept | Example | Ours |
|---|---|---|
| P&L of a short | ≈ 8 steps over 58 lines (EX L156–213: borrow → sell 208 → cash in + obligation → price 210 → buy 210 → return → 208 − 210 = −2 → why "up" = loss → entry/exit table) | **1** table row: `short 0.1 BTC … −0.1 × 2,000 = −200` (ch0 txt L53) |
| Two-leg P&L = change in spread | ≈ 20 steps (พื้นฐาน 4, 5, 10; A.2: legs → total-cash check 410 − 406 → regroup `(208 − 200) − (206 − 202)` → Δ → signed qty → formula) | ≈ 8 (ch11: two-row table, 5-row equity table, `10 × (1 − 0)`); the regrouping step that *explains* the identity is never shown |
| Equity while holding a short | ≈ 16 steps (B.3–B.4: four fills each with fee; equity at t1, t2, t3; reconcile 3.589 − 1.412 = 2.177) | ≈ 6 (ch3: 3-row table, two methods), no fees in the ledger |
| Annualising a basis | 4-step table before first use (EX L1171–1176) | 1 sentence, **94 lines after the number is first used** (ch3 txt L25/L80 use 12.17%; derivation at L174) |

Arithmetic check: I recomputed every figure I could in both texts (example: ≈ 70 figures incl. OLS sums 140/70, squared errors 74/4/74, `284 − 280h + 70h² = 4 + 70(h−2)²`, ln(1.03)=0.0295588, r=11.9877%, F=101.9901, r=11.6368%, all cash/equity/fee lines, 3/823, P10/S10 ledger 1,159.840 → 1,004.361; ours: every table in the seven chapters incl. 0.99ⁿ row, binomial 60.5/30.6/7.6/1.4, 1.25% rescue, 13.0%/8.6% buffers, three-line beta table, all exercise answers). **No arithmetic error found in either book.** Non-arithmetic defects are listed in §5 (example) and §6 (ours).

---

## 1. Teaching techniques the example uses that make it easier than ours

**T1. One unit first → two units → two legs (number of moving parts grows by one each section).**
EX L65: "เริ่มจาก B เพียงหนึ่งหน่วย เพื่อให้เห็นการซื้อกับการขายชัดที่สุด". EX L112: "เราติดป้ายให้เป็น 'B หน่วยแรก' กับ 'B หน่วยที่สอง' เพื่อใช้ตามเงินของแต่ละหน่วย". Prices are 100/101/99/208/210 — every subtraction is mental.
Recurrence: the whole of พื้นฐาน 1–5 (L59–370); "หน่วยแรก" 9×; still unit-by-unit in the fee ledger at B.3 (EX L1308 "หน่วยแรกใช้เงิน 101 U หน่วยที่สองใช้อีก 101 U"). Ours opens with 100,000/103,000, a 0.1 BTC row, then 1 BTC, then says Min really trades 0.01 BTC (three sizes in one chapter).

**T2. Follow the cash before the formula; the formula is introduced as an abbreviation of something already done.**
EX L79: "สังเกตว่าเราไม่ได้เริ่มจากการท่องว่าจะนำราคาไหนลบราคาไหน เราตามเงินก่อนว่าเคยจ่ายอะไรไป และได้รับอะไรกลับมา". EX L462–466: two computations of x by hand, then "เมื่อเข้าใจการทำสองครั้งนี้แล้ว เราจึงย่อวิธีคำนวณเป็น **x = A − 2B**". Mini-headings name the move: "**ตามเงินจนจบก่อนใช้เครื่องหมาย**" (L915), "**ย่อการรับและจ่ายให้เป็นสูตรเดียว**" (L1331).
Recurrence: 10 of 10 display equations come after the numeric walk.

**T3. Name after experience ("the word adds no new event").**
EX L81: "การถือแบบ 'ซื้อไว้ก่อน แล้วขายออกภายหลัง' นี้เรียกว่า **long**". EX L102: "การมีคำว่า long, entry และ exit ไม่ได้เพิ่มเหตุการณ์ใหม่เข้ามา เป็นเพียงชื่อที่ใช้เรียกสิ่งที่เราเพิ่งทำ".
Recurrence: every term in the portion that I checked (long, short, ขา L228, h L446, x L458, spread L899, residual L1094, signal/fill L1280, gross L1232, equity L1354, mark L1362, turnover L1482) — ≥ 12 times, always *after* the reader has computed the thing. Ours does the reverse in ch0–1 (term + gloss first, number after), and often several terms per sentence (§2).

**T4. Restate the term as a picture/action.**
EX L81: "ถ้าเห็นข้อความว่า 'long B หนึ่งหน่วย' ให้แปลเป็นภาพธรรมดาว่า เราซื้อ B หนึ่งหน่วยมาไว้ในมือ". EX L188: "ให้จำภาพว่าเราขาย A ไปหนึ่งหน่วย และยังมีภาระต้องหา A หนึ่งหน่วยกลับมาคืน". EX L170: "ลองวางของที่เกิดขึ้นไว้สองด้าน ด้านหนึ่งคือ **เงินที่รับมา 208 บาท** อีกด้านหนึ่งคือ **A หนึ่งหน่วยที่ยังต้องคืน**".
Recurrence: long, short, ขา, สถานะ, fill (L829), ACK (L1428), mark.

**T5. "พักตรงนี้ได้" checkpoint: one or two sentences that restate the section with its numbers and give permission to stop.**
EX L104: "**พักตรงนี้ได้:** long B คือซื้อ B ไว้ก่อน ตอนเข้าจ่ายเงินซื้อ ตอนออกรับเงินขาย ตัวอย่างหนึ่งหน่วยนี้จ่าย 100 รับ 101 จึงได้ 1 บาทก่อนต้นทุน".
Recurrence: 5× (L104, 138, 213, 282, 354), every 35–75 lines in พื้นฐาน 1–5. Then dropped (a weakness, §5).

**T6. "อ่านภาพ:" — every figure is followed by a sentence saying what to look at first and what number to take away.**
EX L1320: "อ่านภาพ: ไล่กล่องเงินสดทางซ้ายจากบนลงล่าง แล้วอ่านรายการทางขวาที่ทำให้เงินสดเปลี่ยน…". Recurrence 19/19. Same for tables in prose: "อ่านแถวสุดท้ายช้า ๆ" (L881), "อ่านตารางจาก t0 ก่อน" (L1276), "ลองอ่านตารางโดยตามคอลัมน์เงินสดลงมาเพียงคอลัมน์เดียวก่อน" (L1329).

**T7. "อ่านสมการ:" — every equation is re-read with the example's numbers plugged in, and each symbol is glossed where it appears.**
EX L945: "อ่านสมการ: กำไรจากราคา ΔΠ เท่ากับจำนวนที่ถือแต่ละขาคูณการเปลี่ยนราคาของขานั้นแล้วรวมกัน ในเหตุการณ์นี้เป็น (−1) × (−2) + 2 × (+1) = +4 U". EX L897 glosses P, the subscript and t; L935 Δ; L1064 Σ ("ทำให้ครบทุกแถว แล้วนำผลมาบวกกัน"). Recurrence 10/10.

**T8. Naming the three kinds of number, plus one portable self-question.**
EX L140–152: "**แยกตัวเลขสามชนิดนี้ให้ออก** … ตัวเลข 100 เป็นราคาของ B หนึ่งหน่วย ตัวเลข 2 เป็นจำนวน B ที่ซื้อ และตัวเลข 200 เป็นเงินรวม" and "ให้ถามกับตัวเลขที่กำลังดูเพียงข้อเดียวก่อนว่า 'นี่คือราคาหนึ่งหน่วย หรือเงินของทุกหน่วยรวมกัน?'".
Recurrence: L120, L134, L246 ("อย่าลืมว่า 99 บาทเป็นราคาต่อหนึ่งหน่วย"), L316, L1246 (size 408 vs spread 8). The same idea returns as "where does each number come from" (table EX L999–1005; exercise P3 L4162): observed / estimated from the past / chosen rule / assumed / known only later.

**T9. Double-entry cross-check after every result (per leg, then total cash in vs out).**
EX L274–276: "รวมรับ 406 บาท … รวมจ่าย 410 บาท … จึงขาดทุน 4 บาท ตรงกับการคิดแยกขาที่เสียขาละ 2 บาท". Recurrence: L302, L929, L1412–1414, L1447, L1553; the stem "ตรวจ" appears 58×. (Ours has this too in ch3/ch11 — "สองวิธีต้องตรงกัน" — but not in ch0, 1, 4, 8.)

**T10. Explicit scenario resets and "change one thing only".**
EX L290: "เหตุการณ์ต่อไปนี้เป็นทางเลือกแยกกัน ทุกครั้งเริ่มจากจุดเปิดเดียวกัน ไม่ได้นำการปิดครั้งหนึ่งไปต่อเป็นการเปิดของอีกครั้ง". EX L1478: "ตอน C จะเริ่มจากรอบเดิม แล้วเปลี่ยนเหตุการณ์ทีละเรื่อง". Recurrence ≈ 20 reset phrases; all of C.1–C.3 change exactly one input (fee only → exit timing only → path only) against the same 4-fill round.

**T11. Three outcomes from one opening (win / exactly offset / lose on both legs) before any claim about hedging.**
EX L217–328, table L308–312 and L504–508. The loss-on-both-legs case comes *first* (พื้นฐาน 4) with the lesson at L268: "การเห็นว่าชุดหนึ่งมีทั้งซื้อและขายยังไม่พอบอกว่าเงินจะปลอดภัย". Then L330: "ภาพนี้ไม่ได้บอกว่าเหตุการณ์ไหนจะเกิดขึ้นบ่อยกว่า".

**T12. Pre-empting the specific wrong reading, with its number.**
EX L278: at open "มีเงินเข้ามากกว่าออก 8 บาท … เงิน 8 บาทจึงยังเรียกเป็นกำไรของรอบนี้ไม่ได้". EX L1389: "เราอาจเผลอคิดว่าได้กำไร 6.589 U แล้ว". Solutions diagnose the likely wrong answer: EX L663 "หากได้คำตอบราคารวม B เป็น 202 ลองย้อนดูว่าเผลอนำราคาใหม่มาบวกกับราคาเก่าหรือไม่"; EX L5103 maps each kind of wrong answer to the section to re-read. Recurrence ≥ 8.

**T13. "If you are lost, go back to…" recovery instructions.**
EX L211: "หากยังสลับไม่คล่อง ให้กลับไปใช้คำว่า 'ได้เงินจากอะไร' และ 'จ่ายเงินเพื่ออะไร' ก่อนเสมอ". Also L343, L753, L925, and the routing paragraph L1622 ("หากติดที่การเลือกขาซื้อขาย ให้กลับไป… A.2 … เลือกจำนวนไม่ได้ ให้กลับ B.1 … เงินปลายทางไม่ตรง ให้ตามเงินทีละ fill ใน B.3"). "กลับไป" 27×.

**T14. Break the tool on purpose to show what it does not measure.**
EX L474: keep prices, change the multiplier to 3 → x becomes −92 "ทั้งที่ราคาสินทรัพย์ไม่ได้ขยับเลย". EX L566: B filled 1 of 2 → spread still falls 8 → 4 but the account earns 3, not 4. (Ours has the first — ch11 "X กระโดด 0 → 10" — and does it well.)

**T15. Bold run-in question headings every 3–6 paragraphs** (52 in the portion), e.g. "**ทำไมราคาขึ้นแล้วเราจึงขาดทุน**" (L190), "**มีความชันแล้ว เส้นต้องอยู่สูงเท่าไร**" (L1076). They chunk long sections into one-idea blocks.

**T16. Two-level hints before solutions; practice immediately after the first block.**
EX L4977: "P1 … ระดับ 1 ลองคิดกำไรของขา short A และขา long B แยกกันก่อน ระดับ 2 นำ −ΔA + hΔB ไปเทียบกับ Δx". 10 problems × 2 levels; four easy problems sit right at the end of ภาคพื้นฐาน (L638–670) with full solutions directly after (L672–716). P10 re-does the whole ledger with h = 3 as a transfer test.

---

## 2. Step order

### 2a. Example's concept sequence (one line per step)

1. พื้นฐาน 1 — buy 1 at 100, sell at 101, +1; then the names long / entry / exit / สถานะ; unrealised vs sold.
2. พื้นฐาน 2 — buy 2 at 100, sell at 99, −2; three kinds of number (price per unit, quantity, total).
3. พื้นฐาน 3 — short 1 unit: borrow, sell 208, obligation, buy back 210, −2; why "price up" = loss; entry/exit for a short.
4. พื้นฐาน 4 — two legs (short 1 A, long 2 B); A up, B down → −2 −2 = −4; the word ขา; cross-check by total cash; opening cash +8 is not profit.
5. พื้นฐาน 5 — same opening, two other closings (+4, 0); three outcomes side by side; outcome ≠ probability; mark value vs realised cash.
6. พื้นฐาน 6 — "A up 4" in two worlds (B up 2 / B flat): the gap is unchanged vs wider → relative move.
7. พื้นฐาน 7 — why 2 units of B: A − 1B leaves +2, A − 2B cancels; name h; h is not the price ratio 2.08.
8. พื้นฐาน 8 — what to plot: compute the gap twice, then x = A − 2B; unit of x; changing the multiplier moves the graph, not the money.
9. พื้นฐาน 9 — seen / expected / held / result are four different things.
10. พื้นฐาน 10 — three futures of the gap (4 / 8 / 12) ↔ +4 / 0 / −4; P&L = gap at entry − gap at exit, derived from the legs.
11. พื้นฐาน 11 — add a cost of 1; time; partial fill (+3 not +4); "stop adding" ≠ close; stop-loss trigger ≠ closed.
12. พื้นฐาน 12 — if the gap does not come back: check the measurement, then the belief; OU is optional.
13. พื้นฐาน 13–22 — map of the book; 4 exercises with solutions; "write your own question".
14. เริ่ม 1–4, 0.1–0.3 — 4-row price table that motivates the question; roadmap; what each kind of evidence can/cannot show; example spec (cash 1,000, fee 0.1%).
15. A.1 — `x_t = P_A − hP_B` with reading guide.
16. A.2 — Δ; signed quantities (+2, −1); `ΔΠ = −Δx`; names short spread / long spread.
17. A.3 — spread 8 vs distance-from-reference 4 vs profit; entry threshold 6; "where each number comes from".
18. A.4 — h and intercept from six rows by hand (means, deviations, trial slopes 1/2/3 with squared errors, 140 ÷ 70, intercept 4, residual), then code.
19. A.5 — a line that fits the past still has to meet new data; changing the ruler ≠ changing the holdings.
20. A.6 — futures: ratio → ln → year fraction → implied rate; P&L = basis change; "r fell" ≠ profit.
21. B.1 — size of one set (gross 408), cap 500, floor → 1 set; gross (+) vs spread (−); not dollar-neutral.
22. B.2 — rule (enter x ≥ 6, exit x ≤ 4); timeline t0–t3; signal vs fill; saw 5, captured 3.
23. B.3 — cash ledger fill by fill with fees; `C_new`; Δq vs q; equity with mark prices.
24. B.4 — cash up but equity down; equity at t1/t2/t3; reconcile 3.589 → 2.177.
25. B.5 — partial fill, cancel request, fill before ACK; equity 994.7405.
26. B.6 — actual holdings ≠ plan → two options (complete or flatten).
27. C.1 — fee 0.5% → −1.115; break-even fee 0.36452%; doubling size does not fix it.
28. C.2 — timing error: using the signal price as fill price → 3.178 vs 2.177.
29. C.3 — spread widens to 12: mark P&L −5.411; an open position must be reported.
30. C.4–C.7 — do we need OU; closed vs open results in one table; changing h is a new experiment; bridge to real data.

### 2b. Our sequence over the same ground

- ch0: two prices on screen → four questions → **long + short + signed formula + ขา + Hedging in one table** → cash-and-carry three expiry outcomes → Settlement Price → Basis → rope metaphor → **perp + funding + Funding Rate** → (fold: linear/inverse) → stat arb / arbitrage → three gates → who Min is, ×100 → map.
- ch1: Order Book, bid, ask, Mid, Taker, Maker → round trip 120 → two legs 240 / maker 80 / 0.1% 440 → maker vs legging → Market Maker, Adverse Selection → Margin, Leverage → Liquidation (teaser) → "profit in one place, cash called in another" (teaser of ch4).
- ch2: Expected Value → 99% bot → chance of seeing no loss → Median vs Mean → four mechanisms table → who pays the 3,000 → Ton's one-leg funding.
- ch3: 217,700 puzzle → Position Value, Margin, Free Cash, Equity, Unrealized → case 1 (+1,000, two methods) → case 2 (−100) → P&L = basis at entry − basis now → Annualized Basis → Unrealized vs Realized → Daily Settlement → three denominators.
- ch4: margin-call night → two pockets → Ton liquidated → buffer = Free Cash ÷ 1.1 → cumulative → distribution of nights → Mark Price, Wick, IM/MM.
- ch8: dollar-neutral hedge loses 20 → Beta → counting beta → Exposure → two meanings of neutral → beta 1.5 → 1.7 → market / group / own → size of leg B 10/20/30.
- ch11: per-leg P&L + equity check → h, ชุด, X → sets × ΔX → costs 12 → −2 → denominators → h change makes X jump → Z-score → four causes.

Steps the example has that are **absent from our sequence** (in these chapters): its steps 1, 2, 3 (cash walk of long, of quantity, of short), 6–7 (why a multiplier at all), 9, 17, 18, 22, 25–26, 28. Steps where **ours is later than first use**: h (defined ch11, used since ch9), Annualized Basis (used ch3 L25/L80, derived L174), daily settlement of futures losses (used ch1 L144, taught ch3 L161), Margin/Liquidation (used ch0 L150, defined ch1 L110/L118, taught ch4).

### 2c. Twenty-three concrete passages in ours (skip / assumed-before-taught / several new things at once)

**1. ch0 §สองขา: ถือของเดียวกันคนละทิศ (txt L45).**
"Long (สถานะซื้อ/ถือซื้อ) คือได้เมื่อราคาขึ้น ส่วน Short (สถานะขาย/ขายชอร์ต) คือได้เมื่อราคาลง เหมือนขายไว้ก่อนที่ราคาวันนี้แล้วค่อยซื้อคืนทีหลัง ซึ่งในตลาด futures ทำได้เลยโดยไม่ต้องมีเหรียญ"
Problem: long, short, the mechanism of short, and a futures-specific fact — one sentence. Long/short are defined by outcome ("ได้เมื่อราคาขึ้น") not by action, so the reader cannot reconstruct *why*. Missing steps: buy 1 at 100 → sell at 101 → paid 100, received 101, +1; then sell first at 100 → must buy back → buy at 102 → received 100, paid 102, −2; then "this is called short" (EX L59–213).

**2. ch0 same section, first worked table (txt L49–59).**
"long 0.1 BTC | 100,000 | 102,000 | +0.1 × 2,000 | +200" and "สูตรเดียวใช้ได้ทั้งสองทิศ: จำนวนที่ถือแบบมีเครื่องหมาย × ราคาที่เปลี่ยน (long เป็นบวก short เป็นลบ)".
Problem: the first calculation in the book combines a fractional quantity, six-digit prices and a signed-quantity formula. Missing: one unit / small price first; "price per unit vs quantity vs total" (EX L140–152); the sign convention only after the reader has seen cash received vs cash paid (the example reaches signed quantities at L933–939 and spends a paragraph separating "minus = price fell" from "minus = we are short").

**3. ch0 same section (txt L61).**
"เครื่องมือแต่ละตัวในสถานะเรียกว่า ขา และการถือขาหนึ่งเพื่อหักล้างการขยับของอีกขาเรียกว่า Hedging (การป้องกันความเสี่ยง) แต่ถ้าได้แค่ศูนย์ก็ไม่มีใครทำ ตรงนี้เองที่ 3,000 เข้ามา"
Problem: สถานะ (never defined anywhere in ch0), ขา, Hedging in one sentence, then a jump from "long and short the *same* thing = 0" to "two *different* instruments". Missing: define สถานะ as "what the account holds or owes" (EX L98); say explicitly that the next example differs because the two legs were opened at *different prices*.

**4. ch0 §3,000 ที่ไม่สนว่าราคาจะไปไหน (txt L65–92).**
"สมมติมินซื้อ spot 1 BTC ที่ 100,000 และ short futures 1 BTC ที่ 103,000 แล้วถือจนสัญญาหมดอายุ" → 🛑 → table row "60,000 | −40,000 | +43,000 | +3,000" → only afterwards (L92): "ที่เท่ากันทุกแถวเพราะในวันหมดอายุ สัญญา futures จบด้วย Settlement Price (ราคาชำระ) ซึ่งอิงราคา spot ของวันนั้น".
Problem: to get +43,000 the reader must already know that the futures closes at the spot price on expiry; that fact comes after the table and after the 🛑 question. Missing step, before the table: "on the last day the contract is settled at that day's spot price, so the short is 'bought back' at the same price the coin is worth"; then walk one row in cash words (coin bought 100,000, now worth 60,000: −40,000; contract sold at 103,000, closed at 60,000: +43,000).

**5. ch0 §เชือกที่ผูกสองราคา (txt L104–114).**
"หน้าจอของมินยังมีอีกชนิดคือ Perpetual Futures (สัญญาล่วงหน้าแบบไม่มีวันหมดอายุ) เรียกสั้น ๆ ว่า perp … สิ่งที่ดึงราคา perp ให้อยู่ใกล้ spot คือค่าดึงชื่อ funding ซึ่งจ่ายตาม Funding Rate (…) ฉบับเต็มอยู่บท 7" + three bullets (who pays, sign flips, every 8 h) + "100,000 × 0.01% = 10".
Problem: seven new ideas in ~10 lines, in chapter 0, for a product not used until ch7; it lands right after Basis, which the reader has known for six lines. Then a fold adds Linear/Inverse/Stablecoin. Missing step: none — this is an ordering problem; it should move.

**6. ch0 §ไม่ต้องเดาทิศ ยังไม่ใช่เงินฟรี (txt L150).**
"ราคาพุ่งเมื่อไร exchange ขอเงินเพิ่มให้ขา short ทันที แม้สองขารวมกันยังได้ 3,000 แต่ถ้าไม่มีเงินเติมก็ถูกปิดทิ้ง เหลือขาเดียว (บท 4)"
Problem: assumes margin, margin call and liquidation; nothing so far says a futures position is held on a deposit. Missing sentence: "futures ไม่ต้องจ่ายเต็ม วางเงินค้ำไว้ก้อนหนึ่ง ถ้าขาดทุน เงินค้ำถูกหัก" before the gate list. (ch0's teaching zone has 9 forward references.)

**7. ch1 §ราคาไม่ขยับ แต่ยอดลด 120 (txt L41–55).**
"หน้า Order Book (กระดานคำสั่ง) … bid คือราคาสูงสุดที่มีคนรอซื้อ (99,990) ส่วน ask คือราคาต่ำสุดที่มีคนรอขาย (100,010) และตรงกลางคือ Mid Price (ราคากลาง) 100,000 …" / "คำสั่งแบบนี้ชื่อ Taker Order (…) ส่วนอีกแบบคือ Maker Order (…)" → table "ค่าธรรมเนียม taker 0.05% ตอนซื้อ 50 + ตอนขาย 50 | −100".
Problem: six terms in two paragraphs before the first number; then the fee appears as "50" with no multiplication. 0.05% of 100,010 is 50.005 — the rounding is silent, and percent → decimal is never shown anywhere in ch1. Missing: the four cash lines (pay 100,010; fee 100,010 × 0.05 ÷ 100 ≈ 50; receive 99,990; fee ≈ 50). The example does exactly this on 100 U first: "ถ้าซื้อของมูลค่า 100 U ค่าธรรมเนียมคือ 100 × 0.001 = 0.1 U จึงจ่ายเงินจริง 100.1 U" (EX L831).

**8. ch1 §สองขาเสีย 240 · basis 3,000 เหลือ 2,760 (txt L63–75).**
One paragraph re-defines Spot and Short, names Cash-and-Carry, computes "2 × 120 = 240", "3,000 จะเหลือ 2,760", and adds "(บท 5 คิดอีกแบบเมื่อถือจนวันหมดอายุ)". The table then gives "maker 0.02% (ถ้าได้ครบ) −80" and "0.1% ต่อข้าง −440".
Problem: −80 and −440 cannot be reproduced from the text (−80 = 4 fills × 20 with the spread counted as zero; −440 = 2 × (20 + 200)). The reader also has not been shown the four fills of a two-leg round trip. Missing: a four-fill table (buy spot, sell futures, sell spot, buy futures back) with spread and fee per fill — the structure of EX L1322–1327.

**9. ch1 §Margin 1,000 ถือ 10,000 and §กำไรอยู่ที่หนึ่ง เงินถูกเรียกอีกที่ (txt L110–154).**
"…เรียกว่า Margin และขนาดสถานะ ÷ Margin คือ Leverage (…)" → "สถานะจะโดน Liquidation (การถูกบังคับปิดสถานะ) ก่อนถึงจุดนั้น เมื่อ Margin ต่ำกว่าขั้นต่ำ (บท 4)" → "ขา short futures −10,000 ถูกหักจาก Margin 10,300 เหลือ 300" → "Margin 300 ต่ำกว่า 10% ของราคาใหม่มาก exchange จะเรียกให้เติมเงิน".
Problem: Margin, Leverage, Liquidation, daily cash settlement of the loss, the 10% maintenance rule and the margin call are all used within 45 lines; settlement is only taught in ch3 (L161) and the rule in ch4. The same story is then told properly, with different numbers (10,200 / 100 / 11,220), in ch4. Missing step if it stays: "ขาดทุนของ futures ถูกหักเป็นเงินสดออกจากเงินค้ำทุกสิ้นวัน".

**10. ch2 §สี่กลไก: เงินเข้ามาทางไหน (txt L124–138).**
Table row: "Carry (ผลตอบแทนจากการถือ) | short perp รับ funding · ถือ spot คู่ไว้หักล้างราคา | รายรับต่อเนื่องพอ | ฝั่ง long perp | ได้ทีละนิด เสียก้อนใหญ่นาน ๆ ครั้ง".
Problem: one 4 × 5 table introduces Prediction, Carry, Liquidity and re-glosses Settlement Price, Maker Order, Bid-Ask Spread, Taker Order. Three of the four mechanisms have had no worked number yet (pairs → ch9+, carry → ch7, liquidity provision → never in these chapters). A beginner can only read it as a list of names. Missing: one already-seen number per row (3,000 locked; 10 per funding round from ch0; 0.2 per unit from ch1's two-sided maker example) or reveal rows as chapters arrive.

**11. ch2 §ชนะ 99% แต่เฉลี่ยเสียรอบละ 0.21 (txt L67–102).**
"โอกาสไม่แพ้หนึ่งรอบคือ 0.99 ไม่แพ้สองรอบติดคือ 0.99 × 0.99 ไล่คูณไปเรื่อย ๆ ก็ได้ตารางนี้" → "90.4% | 81.8% | 60.5% | 36.6% | 8.1%" → later box: "หน้าจอแสดง | +50 | −71 | −192" with "โอกาส | 60.5% | 30.6% | 7.6% | 1.4%".
Problem: no intermediate product is shown (0.9801, 0.9703…), −71 is not shown as 49 − 120, and 30.6% / 7.6% are binomial probabilities with no method at all. Missing: two products written out, "49 รอบชนะ − 120 = −71", and a plain statement that the second probability row is machine-computed.
Related slip: txt L108 says "20 ไม้สมมติของบอทแบบเดียวกัน" but that sample has Win Rate 95% (L118) while the bot was defined as 99% — a beginner will stop here.

**12. ch3 scene + §เหลือ 60 วัน: ได้ +1,000 ทั้งที่ 12.17% ไม่ขยับ (txt L25, L80, L174).**
Scene: "ใต้ป้ายเล็ก ๆ 'basis ต่อปี 12.17%' ซึ่งคือ Annualized Basis (อัตรา basis ต่อปี)". L80: "เมื่ออัตราต่อปีเท่าเดิมแต่วันเหลือน้อยลง basis จึงหดเหลือ 2,000 และราคา futures เป็น 102,000".
Problem: the reader cannot check "2,000" because how 12.17% is built is only given at L174 ("3,000 ÷ 100,000 = 3% ใน 90 วัน แล้วคูณ 365 ÷ 90"), 94 lines later, in a different section. Missing, before case 1: 3,000 ÷ 100,000 = 3% per 90 days → × 365 ÷ 90 = 12.17% per year → backwards: 12.17% × 60 ÷ 365 = 2% → 2,000. (The example does a 4-row step table before first use, EX L1171–1176.)

**13. ch3 §บวกหน้าจอได้ 217,700 (txt L45–76).**
"ตอน short futures มินไม่ได้รับเงิน 103,000 และไม่ได้จ่าย 103,000 เพราะตัวเลขนั้นคือ Position Value (ขนาดสัญญา) ส่วนเงินที่จ่ายจริงคือ Margin (หลักประกัน) หรือเงินค้ำสัญญา 10% ของราคา futures" → table headed Free Cash / มูลค่า spot / บัญชี Margin / equity → four definitions (incl. Unrealized PnL) → formula.
Problem: five accounting terms in ~15 lines, and the central surprise ("selling brings in no cash") is asserted, not contrasted with the ordinary idea of selling. The book has never shown the plain short where cash comes in and an obligation remains; that model first appears in ch11 (L71, "short B 20 ที่ 50 | 1,000 | 1,000 | −1,000") and is retracted eight lines later. Missing: a two-column contrast "ยืมมาขาย: เงินเข้า + ภาระคืน" vs "futures: ไม่มีเงินเข้า วางเงินค้ำ กำไรขาดทุนวิ่งเข้าออกเงินค้ำ", each with the equity sum (EX L1354: "1,006.589 + 202 − 209 = 999.589").

**14. ch3 §BTC ขึ้น 20,000 แต่สองขารวมเสีย 100 (txt L118–122).**
"ดูคอลัมน์ basis คู่กับคอลัมน์กำไร ทุกแถวกำไรเท่ากับ 3,000 ลบ basis ตอนนี้" → `กำไรจากราคา = basis ตอนเข้า − basis ตอนนี้`.
Problem: the identity is offered as a pattern spotted in four rows; the regrouping that explains it is not shown here (ch0's `[[fm]]` did it only for the expiry case). Missing one line with case-2 numbers: (120,000 − 100,000) + (103,000 − 123,100) = (103,000 − 100,000) − (123,100 − 120,000) = 3,000 − 3,100. The example does this regrouping twice (EX L929, L1194).

**15. ch4 §ต้นมี Free Cash 9,700 — the rescue (txt L116).**
"ขาย spot และปิด futures พร้อมกัน แค่ราว 1.25% ของสถานะ ก็ได้เงินสดจากเหรียญ และ Margin ที่ต้องมีก็ลดลง รวมกันพอปิดส่วนที่ขาด"
Problem: 1.25% is correct (1,520 ÷ (110,000 + 11,320)) but underived; a beginner cannot see why selling 1.25% covers a 1,520 shortfall. Missing: sell 0.0125 BTC → +1,375 cash; required margin falls 0.0125 × 11,320 = 141.5; total ≈ 1,516.5.

**16. ch4 §กันชน and §Mark Price (txt L120–122, L178–194).**
The 1.1 multiplier is built well in words, but its validity condition ("ใช้ได้เฉพาะเมื่อบัญชี Margin พอดีขั้นต่ำก่อนราคาขยับ") sits inside a fold (L170). Then one paragraph introduces Mark Price, continuous evaluation and Maintenance Margin; the next Wick; the next box Initial Margin and Haircut — five terms, zero numbers: "…สั่ง Liquidation ได้ทันทีที่ Margin ต่ำกว่า Maintenance Margin (ระดับรักษาหลักประกัน) ซึ่งเป็นขั้นต่ำก่อนถูกปิด".
Missing: one worked line (e.g. initial 10% = 10,300, maintenance 5% = 5,150 → closed when the account falls below 5,150) or move the block to the fold.
Also missing as a first step in the chapter: a *small* night (futures +1,000 → margin 10,300 − 1,000 = 9,300; required 10,400; top up 1,100 = 1.1 × 1,000) before the 10,200 night.

**17. ch8 §นับ beta จากวันที่ BTC ขยับแรง (txt L59–68).**
"จดการขยับของ BTC เป็นบวกทุกวัน ส่วน A จดบวกถ้าไปทางเดียวกับ BTC จดลบถ้าสวนทาง" … "BTC 3 + 2.5 + 2.2 + 5 + 3.3 + 4 = 20 · A 4 + 4.5 + 2 + 8.5 + 5 + 6 = 30 · 30 ÷ 20 = 1.5".
Problem: the eight days exist only in the chart; the text never shows which two days were dropped, there is no day where A goes against BTC (so rule 2 is never exercised), and "sum ÷ sum" (rather than averaging daily ratios, which the caption says range 0.91–1.8) is unexplained. Missing: an 8-row table with a "นับ / ไม่นับ" column and one opposite-direction day.

**18. ch8 §Exposure +500 (txt L72–90).**
One section: beta exposure formula; a five-column table; "Dollar-neutral (เป็นกลางต่อมูลค่า) คือ Net Exposure (มูลค่าสุทธิ) เป็นศูนย์ ส่วนแถวสองเป็น Market-neutral (เป็นกลางต่อตลาด)"; Gross Exposure; Margin; then "1,500 คือ 1.5 ล็อต … Lot Size (ขนาดสั่งขั้นต่ำ) … Funding Rate (…) 0.01% ต่อรอบจะรับหรือจ่าย 0.15 ต่อรอบ … เดือนละ 90 รอบ = 13.5".
Problem: eight terms in five paragraphs; the lot-size and funding digressions arrive before the reader has absorbed "two meanings of neutral". Missing: a split (exposure → two neutrals → practical frictions as a separate box).

**19. ch8 §แยกเป็นสามบรรทัด: ตลาด · กลุ่ม · เฉพาะเหรียญ (txt L108–122).**
"🔢 สถานการณ์ที่ให้มา: BTC −3% · กระแสกลุ่ม −4% (A และ B ขยับเพิ่มคนละ −4%) · A ขยับเอง +1% · B ขยับเอง −1%" → table "ตลาด (BTC) | 0 | −15 / กลุ่ม | −40 | 0 / เฉพาะเหรียญ | 10 | 20".
Problem: a new coin B (price 50, beta 1.0), four simultaneous moves and six results with no arithmetic. To get "−15" the reader must compute 1,000 × 1.5 × (−3%) = −45 for A and +30 for the short B, unaided; to get "20", +10 (A) and +10 (short B gains when B falls 1%). Missing: a per-leg table (A leg / hedge leg / sum) for each of the three lines.

**20. ch11 §ขา A +20 ขา B −10 รวม +10 (txt L45, L61–79).**
"ขา B เป็น Short (…) ซึ่งเขาทำผ่าน perp ของ B (…) เพราะยืมเหรียญมาขายไม่ได้เสมอ จำนวนที่ซื้อเขียนเป็นบวก ที่ short เป็นลบ" → equity table where short B makes cash go 0 → 1,000 and "มูลค่า B −1,000" → then "ส่วนเงิน 1,000 จากการ short ไม่ใช่เงินใหม่ … และในแอปจริงขา perp ไม่มีเงินขายเข้ามาเลย ต้องวาง Margin (หลักประกัน) แทน … เงินสดจึงต่างจากตารางนี้".
Problem: the table uses a borrow-and-sell cash model the book has never taught, with a negative "value" column, and the next paragraph says the real account does not look like the table. Two accounting models in ten lines. Missing: either the short walk of passage 1 earlier in the book, or one sentence here: "−1,000 คือภาระซื้อ B คืน 20 เหรียญ ตีราคาวันนี้".

**21. ch11 §10 ชุด × X ขยับ 1 = +10 (txt L83–89).**
"เพราะ B ราคาครึ่งหนึ่งของ A จึงใช้ B สองเหรียญต่อ A หนึ่งเหรียญ … ตัวเลข 'จำนวน B ต่อ A หนึ่งหน่วย' ชื่อ Hedge Ratio (อัตราส่วนการป้องกันความเสี่ยง) เขียนสั้นว่า h … คือเลข 2 ใน X = A − 2B ที่วาดมาตั้งแต่บท 9" → next paragraph: Market-neutral, Beta, Exposure 500 → next: "หนึ่งชุด".
Problem: (a) h is defined two chapters after X = A − 2B is first used (ch9 txt L77 introduces it in a parenthesis: "A หนึ่งเหรียญลบ B สองเหรียญ ขามูลค่าเท่ากันแบบบท 8"); (b) the only reason given for "2" is the price ratio — exactly the reading the example warns against (EX L448, L903: "เลข 2 จึงไม่ได้มาจากการนำ 208 หาร 100"); (c) the reader is never shown *why subtracting a multiple of B is useful at all*. Missing: the example's three-row comparison (A alone / A − B / A − 2B when A moves 2 for each 1 of B; EX L875–879) adapted to A 100 / B 50.

**22. ch11 §+10 กลายเป็น −2 (txt L116–127).**
"ค่าผ่านทางในกระดาษ: เข้า 4 ระหว่างถือ 3 ออก 5 รวม 12" (caption: "ไม่ใช่อัตราค่าธรรมเนียมของตลาดใด").
Problem: the lesson "a correct trade can still lose" rests on three unexplained lump sums. They do not follow from the book's own rates: four fills of ≈ 1,000 at ch1's taker 0.05% are ≈ 2.0 in fees, so 12 is roughly six times the book's own toll, and exit (5) > entry (4) has no reason. Missing: per-fill cost lines using ch1's rates plus an explicit "filled at a worse price than seen" line; then choose example prices where the result is still negative.

**23. ch11 §X กระโดด 0 → 10 แต่เงินไม่ขยับ — Z-score paragraph (txt L147).**
"ถ้า X อยู่ที่ 5 โดย Mean (ค่าเฉลี่ย) เป็น 0 และ Standard Deviation (ส่วนเบี่ยงเบนมาตรฐาน) เป็น 1 จะได้ Z-score = 5 แต่พอคำนวณ Standard Deviation ใหม่เป็น 2.5 แล้ว Z-score จะเหลือ 5 ÷ 2.5 = 2".
Problem: three statistics terms dropped into an accounting chapter in one paragraph; it depends on ch9. It is correct and useful, but it is a second idea stacked on the h-change idea before the first has a checkpoint.

---

## 3. Content the example has that ours lacks (in these chapters)

| # | Content (example ref) | Why a beginner needs it | Where it fits in ours |
|---|---|---|---|
| 1 | Cash walk of a long, one unit, then two units (EX L59–152) | Everything later is "quantity × price change"; without the cash picture the sign rule is memorised, not understood | ch0, new first section before "สองขา" |
| 2 | Cash walk of a short: sell first, obligation, buy back; "money came in first but it is not profit" (EX L156–213) | Our reader meets short as "ได้เมื่อราคาลง" and is re-told that definition in ch1 L63, ch2 L124, ch3 L43, ch8 L47, ch11 L45 — five re-glosses of a concept that was never walked through | ch0 same new section; reused by ch3 contrast panel and ch11 equity table |
| 3 | Three kinds of number + the self-question (EX L140–152) | Our ×100 magnifier, 0.1 / 1 / 0.01 BTC sizes and "ขนาดสัญญา vs เงิน" (ch3) are all instances of this confusion | ch0 right after the first walk; recall in ch3 §217,700 |
| 4 | Entry/exit words tied to the action on each side (tables EX L93–96, L204–207, L339–342) | We use ราคาเปิด / ตอนเข้า / ตอนออก / ปิด without ever saying that "exit" of a short is a *buy* | ch0 (4-cell table) |
| 5 | Both legs lose at once; exact offset; both win — from one opening (EX L217–328) | ch0 shows only the perfect lock (+3,000 three times), so "two legs = safe" is planted; ch8 has to undo it | ch8 opening (A −6% while BTC +2% → −60 − 20 = −80) and one line in ch0's "ยังไม่ใช่เงินฟรี" |
| 6 | Why a multiplier: A − B still moves, A − 2B does not; h is not the price ratio (EX L427–448, L869–903) | Without it X = A − 2B is a formula from nowhere | ch9 at first use of X (other reviewer's chapter) and ch11 §10 ชุด |
| 7 | Getting h and the reference level from data by hand (EX L1009–1112) | Ours never derives h in the main text (only equal value; appendix-deep has the covariance formula) | Only the gentle half is worth taking: "try h = 1, 2, 3 and see which leaves the least wobble" as an optional box in ch11; not the Σ algebra (§5) |
| 8 | Spread value vs distance from reference vs profit; "where each number comes from" table (EX L969–1005) | Stops "X = 8 so I made 8" and separates observed / estimated / chosen / assumed / known-later | ch11 next to the 5-box card (txt L104–112) |
| 9 | Signal price vs fill price on a timeline; saw 5, captured 3 (EX L1265–1294); the look-ahead bug 3.178 vs 2.177 (EX L1512–1527) | In our ch11 the paper trade fills exactly at the seen price; the only hint is one clause in an answer ("สองขาได้ราคาไม่พร้อมกัน X ตอนเข้าจริงอาจไม่ใช่ 0", txt L337). (ch15 has a −3 slippage example, outside this portion.) | ch11, as the first cost line between "+10" and "−2" |
| 10 | Fill-by-fill cash ledger *with fees*, and the moment "cash is above start but equity is below" (EX L1300–1404) | Our ch3 ledger has no fees ("equity เท่าเดิมทุกแถว" is true only because fees are omitted); ch11 uses lump sums | ch3 (one fee row at open) and ch11 (replace lump sums) |
| 11 | Partial fill + cancel + fill-before-confirmation; plan vs actual holdings → two options (EX L1420–1468) | Our ch11 box ④ "ได้จริง" has one sentence ("ถ้าได้ B แค่บางส่วน X บนจอยังขยับ แต่เงินไม่ขยับตาม"); ch1 has a one-leg example on a different price scale; the full treatment is in ch16 | ch11 mini-example for box ④ (A +10, B only −10: +20 − 5 = +15 ≠ 10 × ΔX) |
| 12 | Break-even fee rate from turnover; "doubling the size doubles the loss" (EX L1482–1508) | Our ch1 gives cost as a share of profit (8%) and ch11 a break-even per set (1.2); "turnover" — fees are paid on all four fills of the full value — is implicit | ch1 worksheet ใบ 01 (one row) and ch11 |
| 13 | Size (gross, with +) vs spread (with −): "หากเอา 8 มาเป็นขนาดหนึ่งชุด เราจะเข้าใจผิดว่าชุดนี้เล็กมาก" (EX L1246) | In ch11 X = 0 or 1 while the position is 2,000 | ch11 §10 ชุด, one sentence |
| 14 | Two-level hints; wrong-answer diagnosis; self-assessment (EX L4977–4996, L663, L5101–5103) | Our answers open straight to the full solution; a stuck reader has no intermediate rung | every ✍️ block |
| 15 | "พักตรงนี้ได้", "อ่านภาพ:", "อ่านสมการ:" as fixed devices | see §1 | every chapter |
| 16 | "Stop adding ≠ closing; trigger ≠ closed" (EX L570–586) | Liquidation price vs price actually received is the same idea | ch4 one line (ours treats the general point in ch14) |

Not lacking (the example has it, ours has an equal or better version): two-method reconciliation (ch3, ch11); ruler change vs money (ch11); basis P&L vs annualised rate incl. the identical S100/F103 → S120/F123.1 scenario (ch3 — ours is simpler because it uses simple annualisation and folds the ln version away); ratio vs spread (ch9/ch11 exercises).

---

## 4. Content and devices ours has that the example lacks (keep / expand)

1. **A real market and real screens.** BTC spot / dated futures / perp, app labels ("🏦 คำในบท ↔ ป้ายในแอป", ch3 txt L143–159), "📱 จดจากแอป" tasks, exchange-rule caveats. The example is abstract A/B in "U", with a borrow-and-sell short and an explicit exclusion: "ยังไม่จำลองเงินประกัน การถูกบังคับปิด หรือคิวจับคู่" (EX L841).
2. **Margin, liquidation and cash management (all of ch4; ch1 leverage table).** "สองกระเป๋า", buffer = Free Cash ÷ 1.1, the cumulative-buffer trap ("13.0% เป็นการขึ้นสะสม … ไม่ใช่ 'ต่อวัน'"), Ton's liquidation with equity down only 200, Mark Price/Wick. Nothing comparable in the example portion. This is our strongest material; expand, don't trim.
3. **Trading costs as actually paid:** bid/ask, taker vs maker, round trip, legging risk, who is on the other side (ch1). The example has a flat % fee only.
4. **Why the money exists and who pays:** four recurring questions, "คนเร่ง", four mechanisms, the golden-rule hypothesis (ch2). The example never asks who is on the other side.
5. **Expected value and distribution thinking:** 99%-win bot with EV −0.21, chance of seeing no loss in n rounds, รอบชดเชย, Median vs Mean, the "📊 n = 1" boxes (ch2, ch4 txt L145–159). The example only says outcomes ≠ probabilities.
6. **Hedging theory for beginners (ch8):** beta by counting, exposure in money, dollar- vs market-neutral, beta 1.5 → 1.7 stress, market / group / own decomposition, "a bigger hedge leg imports its own news" (10/20/30 coins; Ton wins one night, loses the next). The example has one sentence (EX L1257).
7. **Return denominators** (3.0% / 2.4% / 1.48% in ch3; capital vs gross in ch11).
8. **Three ways a chart moves without money moving** (h, Mean, SD → Z-score; ch11 txt L151–159). The example has only the h case.
9. **Story and characters.** Min's notebook with the same four lines every night; foils Ton (leverage, one leg) and Jo (99% bot); "🎬 ทางที่ไม่ได้เลือก". Gives motive for each chapter; the example has no narrative and no reason to care until L735.
10. **Metaphor system:** rope / chain with a lock / fingers on the rope / toll / two pockets — consistent across chapters.
11. **🛑 predict-before-reveal boxes** (13 in seven chapters) as a formatted device; "🧠 มุมที่มองต่าง" contrast boxes.
12. **Exercises typed as คำนวณ / ตัดสินใจ / ถ่ายโอน**, each answer naming "คำตอบที่ยั่วใจแต่ผิด" and "ข้อระวังของคนทำจริง"; inline folds instead of answers 800 lines away.
13. **Worksheets with pass criteria** (ใบ 00–11, "ของฉัน" column, "บวกกลับได้" checks), running "📒 บัญชีมินท้ายบท", the 8-slot strategy card, "🔁 ถ้าเปลี่ยนตลาด".
14. **Reading lanes and folds** (🟢 🔵 🟠; "🔎 ลงลึก" always ends "ไม่มีอะไรหลังจากนี้พึ่งกล่องนี้"); per-chapter glossary split into "3 คำที่ต้องจำก่อน / ที่เหลือ".
15. **Lighter maths and shorter paragraphs:** simple annualisation instead of ln/exp, no Σ, no code; average item 74–103 chars vs 171.

---

## 5. Weaknesses of the example we should not copy

1. **Repetition.** "ก่อนต้นทุน" 24×; "ยังไม่" 93×. The same +4 / 0 / −4 trade is computed in พื้นฐาน 4, 5, 10, 11, exercise 2, A.2 and again in S1; the number 206 appears 26×. Entry/exit is explained three times (L85–102, L198–211, L334–352).
2. **Length for the yield.** ภาคพื้นฐาน spends ≈ 30,000 visible chars (680 lines) on ≈ 10 concepts with no story, no instrument and no stakes. The first motivating question about a real decision appears at L735.
3. **Devices are not sustained.** "พักตรงนี้ได้" appears 5× in L104–354 and never again — none in A.4 (OLS) or B.3 (ledger), where a rest is most needed.
4. **Difficulty cliff.** After 680 lines of one-unit arithmetic, A.4 uses Σ notation, squared errors and completing the square ("284 − 280h + 70h² … จัดรูปเป็น 4 + 70 × (h − 2)²", EX L1108–1112); A.6 uses ln/exp with 6–7 significant digits (0.0295588, 11.9877%, 101.9901). Five Python blocks (zip, abs, floor, float vs Decimal) sit in the foundation.
5. **Parallel number sets that the author must keep apart.** 208/100 → 206/101 (+4) vs fills 209/101 → 208/102 (+3) vs the 4-row intro table (200/98, 202/99, 204/100, 208/100) vs the 6-row formation table (90/185 … 100/204). The warning is issued three times (EX L815, L961, L1265). A.1 uses "คู่ราคาจากบทเปิด" 202/99, which is not in the six rows that A.4 then calls "ชุดฝึกสมมติอีกชุดหนึ่ง".
6. **Symbols and words reused.** A and B are assets, then label two paths in A.6 (author's warning at EX L1196); q = number of sets vs q_A, q_B (L1244); "gross" = position size in B.1 and gross profit in C.1 (warning at L1506); "spread" two meanings (L905); currency renamed from บาท to U mid-book (L813).
7. **Used before derived.** Reference level 4 and threshold 6 are used in A.3 before A.4 derives them; the coincidence "4 the level vs 4 the distance" needs its own disclaimer paragraph (L979).
8. **Unrealistic account model for our audience.** Full sale proceeds land in cash (1,208.791), no margin, no borrow cost, no bid-ask. Copying the ledger literally would contradict our ch3–4. Take the *structure* (one row per fill, fee per row, equity after each row), not the model.
9. **False precision.** 0.36452%, 1,158.2405, 994.7405, 0.0505; a 0.5-unit fill right after insisting on whole sets.
10. **File/Notebook/ZIP housekeeping in the teaching flow** (L790–861).
11. **No summaries, no glossary in flow, exercises ~800 lines from their hints** (L4134 vs L4971).
12. **Arithmetic:** none wrong (see §0). Two soft spots only: the claim that the best line for any slope passes through the means is asserted, not shown (L1034); A.4 fits price levels on six points (the author flags the limits in A.5).

---

## 6. Prioritised change list

### Cross-cutting (apply to all seven chapters)

- **P1 — Term budget.** No sentence introduces two new terms; no `##` section introduces more than three; the term is named after its first number (T3). Current worst sections: ch0 L45–61, ch0 L104–114, ch1 L41–43, ch3 L45–76, ch8 L72–90.
- **P1 — "พักตรงนี้ได้" after every `##` section** (1–2 sentences restating the section with its numbers). Sustain it through the hard sections, unlike the example.
- **P1 — First number of each new idea is single-unit / small**, then scale to Min's size. Fix one quantity per chapter (ch0 currently uses 0.1 BTC, 1 BTC and 0.01 BTC).
- **P2 — After every `[[fm]]`, an "อ่านสมการ" line with the chapter's numbers substituted; in every `[[cap]]`, an "อ่านภาพ" clause saying where to look first.**
- **P2 — Two-level hint fold before each answer fold**, and one "ถ้าได้ … แปลว่า …" wrong-answer diagnosis per exercise.
- **P2 — Scenario labels:** every multi-row table says "ต่อเนื่องกัน" or "แยกกัน เริ่มจากจุดเดียวกัน" (ch3 does at L104; ch4's main table is sequential but its distribution table is separate; ch8 mixes).
- **P2 — Double check in every chapter** (per leg vs total cash), not only ch3/ch11.
- **P3 — Make room.** 42–52% of each chapter is apparatus. The 8-slot card is reprinted in full in ch2, 3, 4, 8, 11; show only the slots that changed. Move "🔁 ถ้าเปลี่ยนตลาด" to the appendix map.
- **Do not import:** Python, Σ/OLS algebra, ln/exp in the main flow, the "U" currency, four-decimal figures, multiple parallel number sets, disclaimer repetition.

### Chapter 0

- **P1 Add** a first section before "สองขา" (≈ 25–30 lines): buy 1 at 100, sell at 101 (+1, cash out/in); buy 2 at 100, sell at 99 (−2) with the price / quantity / total table; sell first at 100, buy back at 102 (−2) with "เงินเข้ามาก่อน แต่ยังมีภาระซื้อคืน"; a 4-cell entry/exit table; then "BTC ราคา 100,000 ก็คิดแบบเดียวกัน". Only then the signed-quantity formula, presented as shorthand.
- **P1 Reorder** §3,000: state convergence at expiry first (move txt L92 above the table), walk the 60,000 row in cash words, then the table, then the 🛑.
- **P1 Cut/move** perp + funding + Funding Rate (txt L106–114), its chart panel and the linear/inverse fold to ch7; leave one sentence. Removes ~7 terms from the opening chapter.
- **P2 Slow down** txt L61: define สถานะ and ขา separately; say why the second example differs from the first (legs opened at different prices).
- **P2 Add** one sentence before the three gates that futures are held on a deposit (so gate 2 is readable), and one non-lock outcome ("ถ้าปิดก่อนวันหมดอายุตอน basis เป็น 3,200 จะได้ −200") so the chapter does not teach "always +3,000".
- **P2 Move** "👤 มินคือใคร / ×100" above the first table, or drop the 0.1 BTC row and use 1 BTC throughout.
- **P3** Add the total-cash cross-check to the exercise answer (in 300 … out …).

### Chapter 1

- **P1 Replace** the first table with a four-line cash walk (pay 100,010; fee 100,010 × 0.05 ÷ 100 ≈ 50; receive 99,990; fee ≈ 50), showing percent → decimal once and stating the rounding.
- **P1 Add** a four-fill table for the two-leg round trip (buy spot, sell futures, sell spot, buy futures back) → 240; derive −80 and −440 in the same table.
- **P1 Slow down** txt L41–43: bid/ask with numbers first; Taker in the next paragraph; Maker only in its own section; Mid Price after the table.
- **P2 Move** §กำไรอยู่ที่หนึ่ง เงินถูกเรียกอีกที่ (txt L138–154) to ch4 (it depends on daily settlement taught in ch3 and duplicates ch4 with different numbers); leave a two-line teaser.
- **P2 Add** the turnover view: fees are charged on ≈ 400,000 of traded value to earn 3,000; minimum basis that covers 240; "เปิดสองเท่า ค่าผ่านทางก็สองเท่า".
- **P2 Rescale** the legging example (99.9 / 100.1 / 99.5) to the chapter's prices (99,990 / 100,010).
- **P3 Fold** Market Maker / Adverse Selection.

### Chapter 2

- **P1 Show the arithmetic** in §ชนะ 99%: 0.99 × 0.99 = 0.9801, × 0.99 = 0.9703 …; "49 − 120 = −71"; mark the 30.6 / 7.6 / 1.4 row as machine-computed.
- **P1 Slow down** the four-mechanism table: reveal mechanisms one at a time, each with a number already met (3,000; 10 per round; 0.2 per unit), or show two rows now and add rows in ch7 and ch9.
- **P2 Fix** "บอทแบบเดียวกัน" (99%) vs the 20-trade sample (95%).
- **P2 Trim** the scene (txt L23–25): six glossed terms in two sentences.
- **P3** Consider marking ch2 as readable after ch4: it interrupts cost (ch1) → ledger (ch3) → cash (ch4), which is the example's uninterrupted order.

### Chapter 3

- **P1 Reorder:** teach annualising (3% per 90 days → × 365 ÷ 90 → 12.17%; and back: × 60 ÷ 365 → 2% → 2,000) before §เหลือ 60 วัน, as a 4-step table.
- **P1 Add** a contrast panel in §217,700: "ขายแบบยืมมาขาย: เงินเข้า + ภาระคืน" vs "short futures: ไม่มีเงินเข้า วางเงินค้ำ", each with its equity sum. Depends on the new ch0 section.
- **P1 Add** the regrouping line under the 4-row table (passage 14) so the basis rule is derived, not observed.
- **P2 Add** fees to the ledger once (two rows at open) so the reader sees equity start below capital by exactly the fees; then say later tables omit them.
- **P2 Slow down** txt L45–76: introduce Free Cash / บัญชี Margin with the table, Equity after it, Unrealized PnL only in case 1 where it first has a value.
- **P3 Fix** the card row "② ใครจ่าย · บทนี้: 12.17% ต่อปีบนจอ" (not a "who pays" fact) and the gloss "Position Value (ขนาดสัญญา)" (CLAUDE.md glossary: มูลค่าสถานะ).

### Chapter 4

- **P1 Add** a small first night before the 10% night: futures +1,000 → 10,300 − 1,000 = 9,300; required 10,400; top up 1,100 = 1.1 × 1,000. The multiplier is then already familiar when 11,220 appears.
- **P1 Show or cut** the 1.25% rescue (passage 15).
- **P2 Lift** the validity condition of ÷ 1.1 out of the fold into one sentence.
- **P2 Slow down** §Mark Price: one worked line for initial vs maintenance margin, or move the block into the fold; add "ราคาที่ถูกปิดจริงอาจแย่กว่าราคาที่ทำให้ถูกเรียก".
- **P3 Keep and expand** the two-pockets chart, Ton's path, the cumulative-buffer trap and the n = 1 table — nothing in the example competes.

### Chapter 8

- **P1 Add** an 8-row beta table (with dropped days and one opposite-direction day) and one sentence on why sum ÷ sum.
- **P1 Add** per-leg arithmetic to the three-line table (passage 19).
- **P1 Split** §Exposure +500 into exposure → two meanings of neutral → a separate "หน้างาน" box for lot size and funding.
- **P2 Add** a both-legs-lose night (A −6%, BTC +2%: −60 − 20 = −80) next to the scene.
- **P2 Start** the scene arithmetic from one coin (A 100 → 94) before "6% ของ 1,000".
- **P3 Keep** the 10 / 20 / 30 comparison and Ton's reversal.

### Chapter 11

- **P1 Build h and X** before §10 ชุด: A alone / A − B / A − 2B when A moves 2 per 1 of B; say that "B is half the price" is the equal-value choice, one of several (pointer to the ch8 fold). Coordinate with ch9, where X first appears.
- **P1 Replace** costs 4 / 3 / 5 with per-fill lines at ch1's rates plus a seen-price vs fill-price line (signal vs fill), with fees inside the cash column; adjust prices so the lesson (right direction, net loss) still holds with traceable numbers.
- **P1 Resolve** the two cash models in the equity table: either label it "แบบยืมมาขาย เพื่อเห็นภาระซื้อคืน" and explain −1,000 as the obligation, or rebuild it on the margin model of ch3–4.
- **P2 Add** a partial-fill mini-example for box ④ and the "size 2,000 vs X = 1" sentence.
- **P2 Add** the "where each number comes from" table beside the 5-box card.
- **P3 Move** the Z-score paragraph to ch9/ch12 or a fold; add an optional box "ลอง h = 1, 2, 3" (no formulas).

---

## 7. Eight most important findings

1. Ours carries ≈ 60 concepts in ≈ 39,400 chars of actual teaching; the example carries ≈ 35 in ≈ 79,500. Explanation per concept is ≈ 3.5× thinner in ours, and only 38–48% of each of our chapters is teaching.
2. New-term density in our opening chapter is 7–8× the example's: 6 terms before the first worked number, and that number already uses a fractional quantity and a signed formula. The example uses 4 English terms in its first 315 lines.
3. Ours never walks the cash of a long or a short. Short is defined by outcome and then re-glossed in five later chapters; the borrow-and-sell picture first appears, unexplained, in a ch11 table.
4. Four concepts are used before they are taught: Annualized Basis (ch3, 94 lines early), h (two chapters early), daily settlement and the margin rule (ch1 uses what ch3–4 teach), margin/liquidation (ch0).
5. Several of our tables give results with no reproducible arithmetic: ch1 −80/−440, ch2 30.6%/−71, ch4 1.25%, ch8 three-line table and beta sums, ch11 costs 4/3/5 (which do not follow from the book's own fee rates).
6. The example's cheap, repeatable devices are what we lack: "พักตรงนี้ได้" (5), "อ่านภาพ" (19/19), "อ่านสมการ" (10/10), name-after-number, scenario resets, two-level hints. We have 0 of the first three as fixed devices.
7. Our real advantages are substantive and absent from the example: margin/liquidation/cash buffer, bid-ask and maker/taker, who pays, EV and distributions, beta/exposure, return denominators, a story, 🛑 boxes, worksheets. None should be cut to make room.
8. Do not copy the example's length and repetition, its abandoned checkpoints, the OLS/ln/Python cliff, its four parallel number sets, or its cash-in short model. Its arithmetic is clean (≈ 70 figures rechecked, none wrong); so is ours.
