# Report B — Example L0–L8 (+ hints/solutions) vs our chapters 9–15

Scope read in full: example lines 1636–2842 and 4235–4531; ours `sab-part9.txt` … `sab-part15.txt`.
"EX" = example book (line numbers given). "Ours" = chapter + heading + quote.
All example arithmetic I could re-derive was re-computed with a script (results in section 5.3).

## 0. Headline numbers (measured)

| Measure | Example L1–L8 | Ours ch 9–15 (teaching body, before the worksheet box) |
|---|---|---|
| Prose volume | 92.5k chars, 46 subsections | 74.1k chars, 45 `##` sections |
| Paragraph length | 232 paragraphs, mean 305 chars, median 297, max 549 | ~75 paragraphs+bullets per chapter, mean 108–117 chars, median 80–110, max 396 |
| Numbers printed | 15.6 per 1,000 chars | 28.3 per 1,000 chars (ch 12: 36.5, ch 13: 37.0) |
| Calculations actually shown (`= number` in running text/tables) | 164 → 1.77 per 1,000 chars | 53 → 0.72 per 1,000 chars (ch 9: 3, ch 10: 1, ch 13: 5, ch 14: 4) |
| Numbers printed per shown calculation | ≈ 9 | ≈ 40 |
| Equations with a plain-language reading line | 10 of 10 (`อ่านสมการ:`) | 4 `[[fm]]` formulas in 7 chapters; 20 `🚶 อ่านเป็นภาษาคน` lines |
| Real market data | 3 assets × 2,192 daily rows, one hand-checked row, one real position followed through 4 lessons | none; every number is `🔢 สมมติ` or `🎲 จำลอง`; real data only as a phone task (`📱 เลือกคู่จริงหนึ่งคู่ … จดราคาปิดรายวัน 20 วัน`, ch 9 ใบ 09) |
| Exercises | 16 (2 per lesson), each with 2 hints (32 hints, mean 198 chars) + a solution (mean 954 chars) | 21 (3 per chapter), no hints anywhere in the book (0 hits for "คำใบ้" in all `sab-*.txt`), answers mean 208 chars |
| Predict-before-reveal stops | informal, in prose (e.g. EX 2237) | 14 `🛑` boxes (2 per chapter) |
| Math symbols a reader must hold | ≥ 19 (x, e, a, h, q, z, μ, s, α, β, φ, e*, d, d̂, Δq, C, V, G, Π) | 4 (X, h, φ, Z) |

The single most important reading of this table: **ours is result-dense and derivation-sparse; the example is the reverse.** We print almost twice as many numbers per page but show the arithmetic behind less than half as often. A beginner can check almost every number in the example with a calculator; in ours they must trust most of them. Our short paragraphs hide this: they are short because steps are omitted, not because the idea is small.

---

## 1. Teaching techniques the example uses that make it easier than ours

### 1.1 The five-rung ladder: toy numbers → name → formula → reading line → real number → file check
Every quantitative idea is climbed in the same order. Instance, z-score (EX 2054–2103):
1. toy: "วันนี้ A=208 และ B=100 การหัก B สองหน่วยออกให้ส่วนต่าง 208−2×100=8 แต่ระดับอ้างอิงของส่วนต่างนี้เป็น 4 ส่วนที่สูงกว่าระดับอ้างอิงจึงเท่ากับ 8−4=4" (2054)
2. scale by hand: "ระยะจากค่าเฉลี่ยคือ −1, +2 และ −1 ยกกำลังสองแล้วเฉลี่ยได้ (1+4+1)/3=2 จากนั้นถอดรากที่สอง … ได้ประมาณ 1.414214" (2056)
3. a four-row table "question → calculation → name" (2060–2065)
4. symbols defined in a sentence, then the formula, then `อ่านสมการ:` (2067–2073)
5. the same four steps on the real row 2023-01-01: 1,200.34 → 94.315144 → 327.542054 → 0.576911 (2083–2092)
6. the same value located in two CSV columns (2096–2103).

Recurrence: all 10 displayed equations in L1–L8 follow rungs 1→4; six of them are then re-done on real numbers (P&L, h/a, x/e/z, q, cash/equity, α/β).
Ours by contrast teaches Z-score with one division by 1: "วันที่ 11 ได้ 2.2 ÷ 1 = 2.2" (ch 9, "ไม้บรรทัดจาก 20 วัน"). The "subtract the mean" and "divide by the scale" steps never happen with non-trivial numbers in the main text of chapters 9–15 (mean is always 0, SD always 1).

### 1.2 One running toy case reused across lessons
The "นิทาน" (A=208, B=100, h=2, a=4) produces P&L +4 (1712–1720), the reference line (1960), x/e/z (2054), "changing h on the chart" (2127), the forecast (2293) and the name-collision check (2344). "208" appears 14 times in L1–L8. The reader never has to learn a new set of toy numbers to learn a new idea.
Ours also has a running case (A 100 / B 50, 10 sets) and uses it well in ch 11–12, but ch 9's 20-day table, ch 10's simulated 200 pairs (in % log distance), ch 13's X=2 worlds and ch 15's backtest "ขาละ 1,000" each switch units or data set.

### 1.3 Every intermediate quantity gets its own table cell
OLS slope (1996–2001): columns "B ลบค่าเฉลี่ย 100 | A ลบค่าเฉลี่ย 204 | ผลคูณสองระยะ | ระยะ B คูณตัวเอง" with a "รวม" row, then a second table that tries slopes 1, 2, 3 and shows the squared-error totals 8 / 6 / 8 (2007–2011) so the reader sees why 2 wins. Same pattern: correlation (1908–1912), MSE (2371–2374), drawdown (2597–2602), block bootstrap (2700–2704), partial-fill ledger (2536–2543). Recurrence: 40 tables in L1–L8; roughly half are "show the working" tables.
Ours: most tables are result tables (e.g. ch 13 "กฎเดียวสามโลก", ch 10 threshold table, ch 15 "ไม้ที่ต้องมี") whose working is in a collapsed `🔎` or nowhere.

### 1.4 Symbol legend in words before each formula
"เครื่องหมาย t−1 ใช้ถอยวัน ไม่ได้สั่งเอาราคาลบหนึ่ง" (1894); "∑ อ่านว่า 'รวมทุกแถว' เช่น ในเศษคือรวม 3, 0 และ 1 ไม่ใช่ตัวเลขใหม่ที่จะต้องหา" (2015); "ขีดตั้งสองข้างหมายถึงขนาดโดยไม่สนเครื่องหมาย เช่น |−2.4| และ |+2.4| ต่างเท่ากับ 2.4" (1772); the hat on d (2302). Recurs before all 10 equations.

### 1.5 "What this number is NOT" immediately after each result
"คะแนน +0.866025 … ไม่ได้บอกว่าต้องถือ B จำนวน 0.866025 หน่วยต่อ A และไม่ได้หมายถึงโอกาสกำไร 86.6025%" (1930); "ผลจากราคาคือ +4 ตามการลดของ x ไม่ใช่กำไร +2.83 ตามการลดของ z" (2077); "ค่า |z|=2 ไม่ได้บอกว่ามีโอกาสกลับ 95%" (2079); "ลดความผิดพลาดลง … 20% ยังไม่ได้แปลว่ามีกำไร 20%" (2386). Recurs after essentially every new number: 24 hits in L1–L8 for nine fixed phrasings (ไม่ได้บอกว่า, ยังไม่ใช่, ไม่ได้พิสูจน์, ไม่ใช่กำไร, …). We do this too (🚶 lines, e.g. ch 9 "Z-score บอกว่าวันนี้ 'ไกลกว่าปกติกี่เท่า' แต่ไม่ได้บอกว่าต้องขาย"), about 3 per chapter.

### 1.6 How it uses real market data
- **Provenance before use**: file table (1654–1662), one-row anatomy "หน่วยราคาคือ USDT ต่อหนึ่งเหรียญ … ถ้าใช้ close สร้างสัญญาณ เราต้องรอให้วันนั้นจบก่อน" (1822), audit table "2192 | 0 / 0 | 0" (1842–1846), and an explicit statement of what the data does not contain: "ในตารางยังไม่มีราคา bid/ask หรือต้นทุนยืมสินทรัพย์" (1848).
- **One hand-check row**: the reader reproduces a single real date end to end (2083–2092) and is told which CSV column holds which quantity.
- **One real position as a through-line**: the 2024-05-15 signal (z = −2.009654) is sized in L4.1 (2151–2161), filled and booked in L4.4 (2250–2263), paused in L6.4 (2515–2522), reported in L7.3 (2629–2639), stress-tested in L7.4 (2663–2667), and re-derived in solutions LS7, LS8, LS11. The two dates appear 9 times in the file.
- **Toy and real are never mixed silently**: "ตัวเลขจริงใช้ h, a และสเกลจากช่วงฝึกจริงทั้งหมด ไม่ใช้ 2, 4 และรากที่สองของ 2 จากชุดสาธิต" (2092).
- **The real result is allowed to be bad**: forecast worse than the zero baseline in test (−4.7005%, 2396), one position open 594 days at −190.98 USDT (2633–2639). The lesson becomes "calculation right ≠ idea right" (1642, 1646).

### 1.7 Chart → holdings → account money (the chain we most need to study)
1. Holdings first, before any chart: per-leg table giving +2 and +2 (1714–1718).
2. Tie the spread to the holdings: "ส่วนต่างลดลง 4 ขณะที่สถานะ short A และ long B ได้ 4" (1720).
3. Three numbers from one price, three different questions: level 208 / x = 8 / e = 4 / z = 2.83 (2060–2065).
4. Which of them is money: +4 follows x, not z (2077).
5. Why x and not the ratio: same ratio path, P&L +10 or 0 depending on units held (2117).
6. Chart parameter change ≠ account change: h 2→3 moves the plotted value by −100 with no fill (2127).
7. Size: value of one base (1 ETH + h BTC = 7,439.31) → q = 950 / 7,439.31 (2153–2161), then re-check gross at the fill price against a 1,000 cap (2171).
8. Time: signal at close t → pending → fill at open t+1 → mark at close t+1 (2181–2187).
9. Cash: "ลบจำนวนที่เปลี่ยนคูณราคา" with signs, 1,000 + 209 − 202 − 0.411 = 1,006.589 (2203–2205).
10. Equity: cash + signed holdings at mark = 999.589, "ต่ำกว่าทุน 0.411 เท่าค่าธรรมเนียมที่เพิ่งจ่าย" (2215).
11. Reconcile two ways on real numbers: per-leg −7.778208 − 182.250676 − 0.95 = −190.978884 and equity 9,809.021116 − 10,000 = −190.978884 (2261–2263).
Ours covers steps 1, 2, 6, 9, 10, 11 well in ch 11 (and adds Mean/SD changes to step 6). It lacks steps 3–4 as an explicit table, does step 5 only in exercises, does step 7 as "1,000 ÷ 100", and step 8 as one worksheet row.

### 1.8 Know-time vs act-time tables
"จังหวะ | ข้อมูลที่พร้อม | สิ่งที่ทำได้" (2181–2187); the 31-December label example (1864, 2324) and its solution table with real residuals (4442–4446). Recurs in L2.2, L2.3, L4.2, L5.2, L6.1, Q9.

### 1.9 Classification tables that turn a vague word into cases
- inputs: read / estimated / chosen / assumed / known-after (1762–1768)
- "stop" has three meanings (2481–2488)
- which result number answers which question, and its usual misreading (2583–2591)
- symptom → check first → do not fix yet (2683–2690; 2412–2418)
- axis of the next experiment (2792–2798)
Six such tables in L1–L8.

### 1.10 The hint → solution ladder
Structure, constant for all 16 questions:
- **Hint 1 (`คำใบ้ขั้นแรก`)** points back to a specific worked row or asks one narrowing question, without the method. Q5: "กลับไปตารางสามแถวใน L3.2 แถวแรก B ห่างค่าเฉลี่ย −1 และ A ห่าง −3 ผลคูณจึงเป็น +3 … ทำแบบเดียวกันทุกแถวแล้วรวมก่อนหาร" (4265). Q6: "ณ สิ้นปี 2022 เรายังไม่รู้ราคาปี 2024–2025 … ค่า h ที่ได้จะพร้อมใช้งานในสิ้นปี 2022 ได้อย่างไร" (4269).
- **Hint 2 (`คำใบ้เพิ่มเติม`)** gives the method skeleton and names the trap. Q5: "คราวนี้ a ติดลบ จึงต้องระวังว่าการหัก a จะเพิ่มจำนวนที่เหลือ … คอลัมน์ spread … เก็บ e ที่หัก a แล้ว จึงอย่าหักซ้ำ" (4267). Q10: "การลดลง 0.002475 ในสัดส่วนจึงอยู่ประมาณ 0.2475% ไม่ใช่ 24.75%" (4295).
- **Solution** = heading phrased as the insight (e.g. "LS8 Q8 ตรวจผลของสถานะค้างด้วยบัญชีสองทาง"), a working table, a reasoning paragraph, and often **error diagnosis from the size of the miss**: "ถ้าคลาดเพียงเล็กน้อย ลองตรวจว่าใช้ h ที่ปัดเหลือสี่ตำแหน่งหรือไม่ ถ้าคลาดใกล้ขนาด a อาจหัก intercept ซ้ำหรือยังไม่ได้หัก หากเครื่องหมาย z กลับด้าน ให้ตรวจการกำหนด A กับ B" (4399).
- Open questions get a model answer plus why a weaker answer fails: "ส่วนประโยคว่า 'ใช้ OLS หา spread แล้วใส่ OU' บอกเพียงเครื่องมือ" (4343).
- A self-assessment scale tells the reader what using a hint means: "1 ทำตาม / 2 ใช้คำใบ้ / 3 ทำเอง / 4 ประยุกต์" (2820–2825).
Ours: one collapsed "แนวคำตอบ" per question, ~200 chars, answer and warning in the same breath, e.g. ch 12 ✍️ ข้อ 1: "10 × (2.4 − 0.3) − 1 = 20 · 10 × (2.4 − 4.6) − 1 = −23 · ต้องชนะ 23 ÷ (20 + 23) ≈ 53.49% ข้อระวัง: …". No intermediate rung, no "if you got X you probably did Y".

### 1.11 Lesson scaffolding
- deliverable per lesson (1679–1688) and "where to go back when stuck" (1690, 2827)
- each lesson ends with a two-sentence handoff naming the next question: 7 of 7 (1796, 1950, 2141, 2283, 2438, 2557, 2738)
- 14 of 46 subsection headings are questions; 9 are "ลอง…" tasks.
Ours has the `[[pq]]` hook at the end of each chapter (equivalent, and better written).

### 1.12 Baseline habit
Nothing is judged without a "do nothing" comparison: zero-change forecast (2386), fee = 0 run (2657), frozen rule vs sensitivity runs (1862, 2659). Ours has it once as a bullet: "ผู้สมัคร: คู่ไหน เพราะอะไร และฐานเทียบ 'ไม่เทรดเลย'" (ch 15, "กระดาษ → เล็ก → ปกติ").

---

## 2. Step order

### 2.1 Example concept sequence, L1–L8 (one line per step)
1. "ETH แพง" must become a testable question: expensive relative to what (1700)
2. two separate questions: does the gap predict; does holding pay after cost (1702–1704)
3. toy holdings and per-leg P&L: +2, +2 = +4 while the spread goes 8 → 4 (1712–1720)
4. names: long spread / short spread (1720)
5. scale: q bases, h B per A (1722)
6. P&L formula with in/out fill prices; plug the toy (1724–1732)
7. one-page hypothesis incl. "เหตุที่ต้องหยุดเชื่อ" and "สิ่งที่ยังไม่ได้ตรวจ" (1740–1750)
8. where each number comes from: read / estimated / chosen / assumed / after-the-fact (1760–1768)
9. fix the protocol numbers before analysis (1772)
10. research-ready ≠ tradable: spot prices do not give you a short (1806–1816)
11. what one data row means and when it is known (1822)
12. bar sanity checks (1824)
13. join on date, not on row index (1826)
14. audit result and what the data lacks (1842–1848)
15. split by time: train / validation / test, with permitted actions (1854–1862)
16. the boundary label problem; test is spent once seen (1864–1868)
17. proportional change → ratio → log return, 100 → 110 → 121 (1882–1902)
18. correlation by hand on 3 days (1904–1918)
19. what correlation does not say; candidate table; pick ETH/BTC (1930–1940)
20. reference line from the toy: A = 4 + 2B + e (1960–1976)
21. OLS by hand; why squares; trial slopes; intercept (1986–2013)
22. formula, code, pitfalls (2015–2039)
23. real h, a, residual SD; h as a coin count, not equal value (2041–2048)
24. x, e, z: three answers; SD by hand (2054–2065)
25. formula with train subscripts; what z is not (2067–2079)
26. one real row by hand; map to file columns (2083–2103)
27. why not the ratio (2115–2121)
28. changing h on the chart changes nothing in the account (2127–2131)
29. size: value of one base → q (2151–2161)
30. signs by direction; re-check gross at fill; lot-size caveat (2163–2173)
31. timeline: signal → pending → fill → mark → end of data (2179–2191)
32. cash with signed quantities; short proceeds carry a buy-back duty (2197–2213)
33. equity = cash + marked holdings; fee on gross traded value (2215–2229)
34. follow the real position; reconcile two ways (2235–2263)
35. what risk remains with two legs; gross cap ≠ max loss (2269–2273)
36. level today vs change tomorrow; toy half-rule forecast (2293–2314)
37. labels and leakage; fit α, β; real forecast for e = 1,000 (2322–2346)
38. read sign and size; forecast must beat cost (2352–2363)
39. MSE by hand; zero baseline; % improvement; real table (2369–2398)
40. if not supported: what to ask before changing anything (2410–2420)
41. φ = 1 + β, fixed point e*, half-life 108 days vs 594 days held (2422–2428)
42. same signal, different action depending on state (2448–2452)
43. state table; signals / ledger / marks files (2458–2473)
44. "stop" = pause new entries / request close / retire the model (2479–2488)
45. what the 30-day pause does to the real position (2500–2522)
46. legs filling at different times; cancel request vs acknowledgement (2528–2547)
47. keep the question fixed while reading the answer; no trades is a result (2567–2573)
48. which number answers what; % needs a stated base; drawdown by hand (2579–2608)
49. result table; start from the open position (2614–2643)
50. fee stress and entry-threshold sensitivity (2655–2669)
51. symptom table; block bootstrap by hand; real intervals (2681–2728)
52. decide: develop / pause / retire (2748–2752)
53. five-paragraph report with sample paragraphs (2758–2784)
54. choose the next experiment by axis; change one thing (2790–2812)
55. self-assessment levels; reproducible project folder (2818–2839)

### 2.2 Our concept sequence, chapters 9–15
Ch 9: (1) Correlation 0.90 → % of same-direction days · (2) simulation set-up: 200 pairs × 2 kinds × 500 days, common factor, 30 re-runs · (3) Formation / Test Period + three time rules · (4) pair spread X = A − 2B over 20 days · (5) Mean by summing · (6) SD as the band holding 2/3 of days · (7) 95% band, Z-score · (8) result: 0.90 pairs stay in band 59.7%, 0.72 pairs 91.8% · (9) n = 1 box · (10) rope ladder, who pays · (11) place A–B, write slot ⑥.
Ch 10: (12) screener ranks 200 pairs by mean crossings · (13) open the Test Period: 65.2%, −4.85 SD · (14) reveal: all 200 have no rope · (15) top-10 vs all vs real · (16) 30 re-runs · (17) 0.95ⁿ table, Data Snooping · (18) leaky ruler · (19) threshold trade-off table · (20) pair register.
Ch 11: (21) paper trade, per-leg P&L · (22) cash / Equity table · (23) perp margin caveat · (24) why 10 and 20, h, "one set" · (25) not Market-neutral · (26) profit = sets × ΔX, reverse position · (27) five-box card · (28) costs 4 + 3 + 5, funding, Break-even, per-capital vs per-gross return · (29) h / Mean / SD change the chart, not the money · (30) four reasons a spread returns while money falls.
Ch 12: (31) six-line rule card · (32) assumptions (B fixed, Mean 0, SD 1, one period = one look) · (33) three rehearsed paths · (34) line ≠ fill · (35) fourth path and precedence · (36) Break-even Win Rate · (37) Expected Value in two worlds · (38) funding on top · (39) คนรีบ vs คนรู้ · (40) 1% rule → 6 sets · (41) real trades, n = 1.
Ch 13: (42) coin-toss walk vs "80% remains" · (43) φ and Noise · (44) φ 0.80 vs 0.99 over 4 periods · (45) Half-life table · (46) mean path ≠ path, Time to Target · (47) same card in three worlds · (48) trade 3 under each world · (49) estimating φ by counting, evidence sheet.
Ch 14: (50) gap to 4.1, −21 · (51) Pause Mode vs holding state · (52) cost of pausing · (53) three look-alike causes, Regime Change symptoms · (54) several pairs on the same side · (55) Mean that follows · (56) three decisions, five options, resume conditions.
Ch 15: (57) result bridge 12 → 8 → 5 → 3 → 2 · (58) Forecast Error vs money paid · (59) top-down diagnosis, two-branch tree · (60) backtest of the fake pair with the card · (61) trades needed · (62) variants tried · (63) paper → small → normal, pre-registration.

### 2.3 Structural differences in order
- **We draw the spread before we explain what is held.** X = A − 2B appears in ch 9 (step 4); "why 2", "one set" and "X is the price of one set" arrive in ch 11 (step 24). The example fixes holdings and P&L first (steps 3–6), then builds the spread from them (steps 20–24). For two chapters our reader is measuring a quantity whose link to money has not been shown.
- **We never have a data step.** The example spends all of L2 (steps 10–19) before any subtraction. Ours goes from "the app shows 0.90" straight to a simulated universe.
- **h is given, never obtained.** "เพราะ B ราคาครึ่งหนึ่งของ A จึงใช้ B สองเหรียญต่อ A หนึ่งเหรียญ" (ch 11). The example's steps 20–23 have no counterpart in our main text (only a box in ch 8 where h = 1.6 "จากระดับราคา" is stated as an assumed value, with no calculation).
- **We have no "will it come back" test on data.** Ch 13 explains φ through worlds whose φ is known; the example's steps 36–41 estimate it from the data and compare with a baseline.
- **We are ahead on rules.** The example has no price stop, no time exit and no Expected Value; our steps 31–41 and 50–56 have no counterpart there.

### 2.4 Twenty passages in ours where a beginner loses the thread (S1–S20)

**S1 — ch 9, "ไม้บรรทัดจาก 20 วัน: Mean 0 · Standard Deviation 1"**
Quote: "จดราคาปิด 20 วันแล้วคิด Spread ของคู่ X = A − 2B (A หนึ่งเหรียญลบ B สองเหรียญ ขามูลค่าเท่ากันแบบบท 8)"
Cannot follow: why subtracting two B from one A is a quantity worth measuring. Ch 8 did choose "A 10 กับ short B 20 เหรียญ" as the equal-value hedge, but the step from that holding to the line X — one set = +1 A, −2 B, and a change in X is the money made per set — is only made in ch 11 ("X คือ 'ราคาของหนึ่งชุด'"). For two chapters X is a chart quantity with no stated link to the account.
Missing step: three lines before the table — "A 100, B 50; to have the same value on both sides you need 2 B per A; hold +1 A and −2 B and your money moves by exactly the change in A − 2B" with one numeric check (day 1 → day 2: 100.7 − 99.6 = +1.1, 2 × (49.9 − 49.6) = 0.6, X moves 0.4 → 0.9 = +0.5 = 1.1 − 0.6).

**S2 — ch 9, same section**
Quote: "Z-score … = ระยะห่างจาก Mean ÷ Standard Deviation วันที่ 11 ได้ 2.2 ÷ 1 = 2.2 … (Standard Deviation ของ A–B เท่ากับ 1 X จึงอ่านเป็น Z-score ได้ตรง แต่คู่อื่นต้องหาร)"
Cannot follow: with Mean 0 and SD 1 both steps of the Z-score are invisible, so from here to ch 15 the reader treats X and Z as the same thing (the card says "เข้า: X ≥ 2"). The first time they meet a real pair (Mean ≠ 0, SD ≠ 1) they have never done the calculation. The example does it twice with awkward numbers (8 → 4 → 2.83; 94.32 → 327.54 → 0.577).
Missing step: a second mini-row "คู่ C–D: Mean 3, SD 2, today X = 8 → distance 8 − 3 = 5 → 5 ÷ 2 = 2.5" in the main text, not only in ✍️ ข้อ 1.

**S3 — ch 9, "ทดลองกับคู่ที่รู้คำตอบ"**
Quote: "ชุดทดลองมีสองแบบ แบบละ 200 คู่ คู่ละ 500 วัน ปัจจัยร่วม (แรงที่ดันสองเหรียญพร้อมกัน) ขยับวันละราว 3% (ค่าที่ตั้งเอง) คู่ไม่มีเชือกคือคู่ที่ไม่มีอะไรดึงระยะห่างกลับ ส่วนคู่มีเชือก ระยะห่างจะถูกดึงกลับทุกวันแต่แกว่งแรงกว่า แล้วสุ่มใหม่ 30 ชุดด้วยกติกาเดิม เผื่อชุดแรกเป็นโชค"
Cannot follow: one 300-character paragraph introduces simulation, two pair types, a common factor, "pulled back every day", "swings harder" and re-sampling 30 times; the next paragraph adds Formation Period, Test Period and survivorship. Seven new ideas in ~790 characters, none with a number the reader can touch.
Missing step: a five-day hand-made miniature of each type (common shock + own shock; one column with "pull back 20% of the distance", one without) so "มีเชือก / ไม่มีเชือก" is a rule the reader has executed. Ch 13's coin-toss table is exactly this device — it arrives four chapters late.

**S4 — ch 9, "0.90 อยู่ในกรอบ 59.7% · 0.72 อยู่ 91.8%"**
Quote: "ถ้าตรึงไม้บรรทัดจาก Formation Period แล้ว Test Period จะมีกี่ % ของวันอยู่ในกรอบ ±2" … "(คู่จำลองวัดเป็น % ห่างของ A เทียบ B คู่ของมินวัดเป็น X = A − 2B ความคิดเดียวกัน หน่วยต่างกัน · ตัวอย่างนี้ไม่ได้หาจำนวนเหรียญต่อขา)"
Cannot follow: (a) "days in band in the Test Period" is the chapter's key measurement and is never computed by hand — Min's 20 days are Formation only; (b) the simulated spread is a log/percentage distance, Min's is a price difference, and the switch is a parenthesis.
Missing step: 10 further days for A–B (days 21–30) judged against the frozen ruler (Mean 0, SD 1): count how many are inside ±2 → "x จาก 10 วัน". And one sentence saying which spread definition the reader should use for their own pair and why (see 3.4).

**S5 — ch 10, "38 ครั้งที่ดูเหมือนเชือก" / "เปิด Test Period"**
Quote: "นับว่า Spread ของคู่ข้าม Mean กี่ครั้ง คู่อันดับ 1 ข้าม 38 ครั้ง" … "Spread ลงไปถึง −4.85 Standard Deviation หรือราคาเหรียญแรกเทียบเหรียญที่สองห่างจาก Mean ราว 16–17%"
Cannot follow: what counts as a crossing (the score the whole chapter is about) is never shown on numbers; the conversion −4.85 SD → 16–17% is explained only in 🔎 with e^(−0.1803).
Missing step: count crossings on the ch 9 table (it has 3 sign changes in 20 days: day 4→5, 8→9, 13→14 — I checked) so "38 in 250 days" has a scale; and one line "1 SD ของคู่นี้ ≈ 3.7% จึง 4.85 SD ≈ 17%".

**S6 — ch 10, "ตัวเลขล้วน ๆ กันคู่ปลอมไม่อยู่"**
Quote: "เกณฑ์ 85% ปล่อยคู่ปลอมผ่าน 30.5% (สุ่มใหม่ 30 ชุดได้ 22–34%) สูงกว่าโอกาส 5% ที่สมมติไว้ข้างบนมาก และตัดคู่จริงทิ้ง 13% ถ้าดันเกณฑ์เป็น 95% คู่ปลอมก็ยังผ่าน 22.5% แต่คู่จริงถูกตัด 65% เพราะคู่ปลอมบางคู่โชคดีทั้งสองช่วง"
Cannot follow: seven numbers and two kinds of error in one sentence; and the table itself is puzzling — raising the bar from 85% to 90% lowers fake passes only from 30.5% to 29.5%. The reason (fake pairs are either far outside or luckily inside; few sit in between) is not given. Also this section uses the ch 9 data set (59.7%) while the rest of the chapter uses another (57.1%), flagged only by "ชุดเดียวกับบท 9".
Missing step: read the table as counts first ("จาก 200 คู่ปลอม ผ่าน 61 คู่ · จาก 200 คู่จริง ตกรอบ 26 คู่"), then one sentence on why the fake-pass column barely moves.

**S7 — ch 11, "ขา A +20 ขา B −10 รวม +10"**
Quote: "ในแอปจริงขา perp ไม่มีเงินขายเข้ามาเลย ต้องวาง Margin (หลักประกัน) แทนตามบท 4 ซึ่งทุนที่ซื้อ A หมดแล้วไม่เหลือให้ (บท 16) เงินสดจึงต่างจากตารางนี้ แต่กำไรจากราคาเท่ากัน"
Cannot follow: the cash table just learned is declared unlike the reader's app, the capital is said to be fully used, and the answer is five chapters away. A reader who opens their exchange will not find "เงินสด 1,000 · มูลค่า B −1,000".
Missing step: a second three-row table "แบบ perp": cash after buying A = 0, margin posted for B = (say) 200 from a separate buffer, unrealised P&L on B = −10 → same Equity change +10. Two tables side by side, same bottom line.

**S8 — ch 11, "+10 กลายเป็น −2 เมื่อค่าผ่านทางรวม 12"**
Quote: "ค่าผ่านทางในกระดาษ: เข้า 4 ระหว่างถือ 3 ออก 5 รวม 12" and "เงินสดเดินแบบนี้: จ่าย 4 เหลือ 996 จ่ายอีก 3 เหลือ 993 (Equity 1,003) แล้วปิดรับ 10 จ่าย 5 จบที่ 998"
Cannot follow: where 4, 3 and 5 come from (no rate × value), why exit costs more than entry, and why holding costs 3 when the next paragraph says the short leg *receives* 0.1 per round. The cash walk compresses four events into one sentence. The example derives each fee: "|−1|×209×0.001=0.209 ขา B ใช้ |+2|×101×0.001=0.202" (EX 2229).
Missing step: "เข้า: 0.2% × 2,000 = 4" (or whatever rate is intended) per leg, and the cash walk as four table rows appended to the existing Equity table.

**S9 — ch 11 → ch 12 → ch 15, cost basis changes without comment**
Quotes: ch 11 "เข้า 4 ระหว่างถือ 3 ออก 5 รวม 12" (10 sets); ch 12 card "ต้นทุน: เข้า 0.4 + ออก 0.6 = 1 ต่อไม้" (the same 10 sets); ch 15 "หักค่าธรรมเนียม 2 จาก Taker Order (คำสั่งซื้อขายทันที) สี่ครั้ง" plus 3 for entry prices.
Cannot follow: the same position costs 9 to trade in one chapter, 1 in the next and 5 in the third. Ch 11's lesson is "cost 12 eats +10"; ch 12's Break-even Win Rate of 57% rests on cost 1. With ch 11's costs the three endings would be +8 / −6 / −29.
Missing step: one fee rate fixed for chapters 11–15 (as the example fixes 0.1% and then stress-tests 0 / 0.1 / 0.5%, EX 2663–2667), or an explicit sentence in ch 12 saying why the card assumes a cheaper venue, with the 57% recomputed at the ch 11 cost as a contrast.

**S10 — ch 12, "การ์ด 6 บรรทัด"**
Quote: "ก่อนเข้าให้ถามว่าผลที่คาดหักต้นทุนและส่วนเผื่อแล้วยังบวกไหม เช่น คาดได้ 6 ต้นทุน 3 เผื่อพลาด 1 เหลือ 2 จึงเปิด เส้นเข้าอยู่ที่ 2 เพราะกลับถึง 0.5 จะได้ 10 × 1.5 = 15 เทียบต้นทุน 1 เส้นออกอยู่ที่ 0.5 เพราะเก็บส่วนใหญ่แล้ว ส่วนงบ −15 ตรงกับ X ราว 3.5 ซึ่งไกลพอที่ถ้าถึง เชือกอาจขาดแล้ว"
Cannot follow: "6, 3, 1" belong to no example in the book (the same paragraph's own numbers are 15 and 1); "งบ −15 ตรงกับ X ราว 3.5" is the result of solving 10 × (2.1 − X) − 1 = −15, using an entry of 2.1 that has not been introduced yet (the card line says 2).
Missing step: use the card's own numbers for the pre-entry check (15 − 1 − margin), and show "−15 = 10 × (2.1 − X) − 1 → X = 3.5" after the paths table, where 2.1 exists.

**S11 — ch 12, same section**
Quote: "ตะกร้า X = A − 2B โดย B = 50 ทุกจุด A จึงเท่ากับ 100 + X ส่วนไม้บรรทัดมี Mean 0 และ Standard Deviation 1 X จึงอ่านเป็น Z-score (ค่ามาตรฐาน) ได้ตรง และ 'ช่วง' คือการเปิดดู X วันละครั้ง"
Cannot follow: four simplifying assumptions and a new word in one sentence. "ตะกร้า" is not in the chapter glossary and ch 11 called the same thing "ชุด"; "short X" in the card line above has not been defined yet (ch 11 called it "สถานะกลับด้าน"). Because B is frozen, every path in ch 12–14 is a one-leg trade: "ขา B = long 20 ที่ 50 นิ่ง (ได้เสีย 0)". The two-leg bookkeeping learned in ch 11 is not exercised again.
Missing step: split into a four-row "ข้อสมมติของบทนี้" box; keep one word (ชุด); and let B move in at least one path (e.g. path 2) so the ledger shows two non-zero legs.

**S12 — ch 12, "+16 กับ −21: ต้องชนะเกิน 57%"**
Quote: "กลับกัน ชนะ 65% แต่ไม้ชนะได้ 1 ไม้แพ้เสีย 3 และต้นทุน 0.1 Expected Value ก็ยังเป็น −0.5 ต่อครั้ง เพราะต้องชนะถึง 77.5% (บท 18)"
Cannot follow: a second example with four new numbers and two results in one sentence, with the explanation deferred six chapters. −0.5 = 0.65 × 1 − 0.35 × 3 − 0.1 and 77.5% = 3.1 ÷ 4 are both left to the reader.
Missing step: either cut it (the 37-trade argument just above is already complete) or give it two lines of arithmetic.

**S13 — ch 13, "เหลือ 80% หรือ 99% ต่อช่วง"**
Quote: "คู่ φ 0.80 ลดจาก 2 เหลือ 0.82 สุทธิ +10.81 ส่วนคู่ φ 0.99 ลดไม่ถึง 0.1 ได้ไม่ถึง 1 สุทธิ −0.21"
Cannot follow: the reader who multiplies gets 10 × (2 − 0.82) − 1 = 10.80 and 10 × (2 − 1.92) − 1 = −0.20; the printed 10.81 and −0.21 come from unrounded 0.8192 and 1.9212. The calculation is not written out (ch 13 has 5 shown calculations in 11.4k chars; only ch 9 with 3 and ch 10 with 1 show fewer).
Missing step: write the line "10 × (2 − 0.8192) − 1 = 10.81" once, and show 0.8192 in the table (or round the result to 10.8).

**S14 — ch 13, "Half-life 69 ช่วง แต่ครึ่งหนึ่งแตะ 1 ใน 12 ช่วง" and "กฎเดียวสามโลก"**
Quote: "เมื่อเทียบกับ Standard Deviation (ส่วนเบี่ยงเบนมาตรฐาน) ของแต่ละโลก 2 คือ Z-score (ค่ามาตรฐาน) 12.0, 2.4 และ 0.56 ในโลกเชือกย้วย X = 2 จึงไม่ใช่จุดสุดโต่ง"
Cannot follow: where each world's SD comes from (it is noise ÷ √(1 − φ²): 0.167, 0.833, 3.54 — never stated); and the consequence — ch 12 told the reader the ruler is "Mean 0 และ Standard Deviation 1", but none of the three worlds has SD 1. So "การ์ดเดียวกันในสามโลก" enters at Z = 2.4 in one world and Z = 0.56 in another; the comparison mixes "weaker rope" with "entry that is no longer extreme". A beginner will read +8.70 / −0.48 / −0.99 as the pure effect of φ.
Missing step: a row "SD ของ X ในโลกนี้" in both tables with one sentence on why a slack rope also means a wider normal range; and say explicitly that a card written as "X ≥ 2" silently assumes the ruler still holds.

**S15 — ch 12 ↔ ch 13 ↔ ch 15, the three-ending worlds are never reconciled with the simulated worlds**
Quotes: ch 12 "ถ้า 60 ไม้ถึงเส้นออกได้ 960 อีก 25 ไม้ครบเวลาได้ 50 และ 15 ไม้ชนงบ −315"; ch 13 table "ออกเพราะถึงเป้า (%) 26.4 · ออกเพราะชนงบ (%) 0.1 · ออกเพราะครบเวลา (%) 73.4"; ch 15 "ไม้ที่ต้องมี" built on 60/25/15.
Cannot follow: the "main world" of ch 12 (60% reach the exit line) appears in no simulated world of ch 13 (best case 26.4%), yet ch 15 returns to 60/25/15 to compute "15 ไม้". The reader cannot tell which picture is the realistic one.
Missing step: one bridging sentence in ch 13 ("ch 12's three endings were a simplification; with noise, time exits pay a range of amounts, which is why 73.4% time exits still average +8.70") and, in ch 15, the trades-needed figure for the ch 13 worlds as well.

**S16 — ch 13, "ไม้ 3: โลก 0.80 คาด +2.08 · โลก 0.99 คาด −7.44"**
Quote: "นับช่วงจาก 2 จนแตะ 1 ใน 20 เส้นของภาพ ได้ Median 9 ซึ่งในตาราง Half-life อยู่ระหว่าง φ 0.90 กับ 0.95 คือราว 0.93 ทั้งที่ค่าจริงคือ 0.99 เพราะสิ่งที่นับคือ Time to Target ซึ่งสั้นกว่า Half-life การนับจึงมักเข้าข้างเรา และใช้ได้ทางเดียว คือถ้าค่าที่นับยังช้ากว่าเวลาที่ยอมถือ ของจริงก็ช้ากว่านั้นอีก"
Cannot follow: method, result, bias and the one-sided decision rule in a single 360-character sentence; the Median of a list with six censored entries is not worked (it is (7 + 11) ÷ 2 = 9 from the sheet's list); and the section two headings earlier just said Half-life ≠ Time to Target, so the reader is asked to use a tool immediately after being told it measures the wrong thing. Also "อีก 2 ช่วงเส้นค่าเฉลี่ยจาก 2.8 จะอยู่ราว 1.79 และครบเวลาได้ราว +2.08" skips 2.8 × 0.8 × 0.8 = 1.79 and 10 × (2.1 − 1.79) − 1 = 2.08.
Missing step: four numbered steps (list → sort → middle → look up), then a separate two-line box "why this flatters us and how to use it anyway". Better: add a direct estimate from Min's own 20 days (see 3.6).

**S17 — ch 11 / ch 12 / ch 15, three numbering systems with the same glyphs**
Quotes: ch 11 "การ์ด 5 กล่อง … ① สัญญาณ | ② กฎ | ③ จำนวนเป้าหมาย | ④ ได้จริง (สถานะ) | ⑤ Equity" followed ten lines later by "กรอบนี้เติมช่อง ④ และ ⑤ ของบัตร" (the 8-slot nature card, where ④ = รูปร่าง, ⑤ = ทุน); ch 12 sheet "ค่าที่ plot ① ความสัมพันธ์ … ⑥ อะไรหักล้าง"; ch 15 sheet "① ค่าที่คาดไว้ … ⑤ หลังค่าถือ".
Cannot follow: "ช่อง ④" means three different things inside chapters 11–15.
Missing step: letters or words for the local lists (ก–จ, or named boxes), keep ①–⑧ for the nature card only.

**S18 — ch 15, "15 ไม้ หรือ 17,299 ไม้"**
Quote: "กำไรเฉลี่ยต่อไม้ต้องห่างศูนย์อย่างน้อยสองเท่าของระยะที่ค่าเฉลี่ยแกว่งเองจากโชค (มั่นใจราว 95%) ยิ่งมีไม้มาก ค่าเฉลี่ยยิ่งแกว่งน้อย คือถ้าไม้มากขึ้นสี่เท่า ค่าเฉลี่ยจะแกว่งเหลือครึ่ง" and the column "Standard Deviation (ส่วนเบี่ยงเบนมาตรฐาน) ของผลต่อไม้ 13.13"
Cannot follow: (a) SD was taught in ch 9 as "the band holding about 2/3 of the days"; here it is the SD of a three-outcome result (+16 / +2 / −21) where that picture does not apply, and 13.13 is derived only in 🔎; (b) "how much the average wobbles" is asserted, not shown — no row says "with 4 trades the average wobbles ±6.6, with 16 trades ±3.3, with 64 trades ±1.6; you need the wobble × 2 to be below 6.95".
Missing step: that three-row ladder in the main text; the reader then sees 15 appear between 4 and 16 instead of receiving it.

**S19 — ch 14, "3.8 แรงกว่าตอนเข้า แต่การ์ดสั่งพัก"**
Quote: table "FLAT ไม่ถือ | OPENING กำลังเข้า | OPEN ถือครบ | CLOSING กำลังปิด" × "ACTIVE | PAUSED"
Cannot follow: six new labels at once, two of which (OPENING, CLOSING) describe partially filled orders — a situation the book has not yet shown (Legging Risk is ch 16). The example reaches its state table (EX 2460–2469) after a full lesson on signal → pending → fill.
Missing step: introduce only FLAT / OPEN × ACTIVE / PAUSED here (what Min actually needs tonight), add the two transitional states in ch 16 where partial fills happen.

**S20 — ch 15, "กระดาษ → เล็ก → ปกติ"**
Quote: "กันหลอกตัวเองด้วยประกาศก่อนทดสอบ 6 ขั้น ที่เขียนก่อนเห็นผล … โจทย์: กลไก เวลาถือ ต้นทุน ทุน · ผู้สมัคร: คู่ไหน เพราะอะไร และฐานเทียบ 'ไม่เทรดเลย' …" then "เขียนประกาศก่อนทดสอบให้ A–B ใหม่"
Cannot follow: six headings, no filled-in example; Min's version is said to exist but is not shown. The example prints its hypothesis sheet filled in (EX 1742–1750) and later a model report paragraph (EX 2780–2782).
Missing step: Min's six lines for A–B with actual values (the numbers all exist already in ch 9–14).

---

## 3. Content the example has that ours lacks

For each: what it is (EX lines), why a beginner needs it, where it fits in ours.

### 3.1 Reading a data file before using it (EX 1822–1848, Q3–Q4, LS3–LS4)
What: meaning of one row (unit, open/close, when known), bar sanity checks, duplicate/missing dates, joining two assets on date not row number, and what to do with a missing day ("การเติมแถวให้ครบไม่ได้สร้างราคาซื้อขายในวันที่หายไปจริง", 1948).
Why: our reader is told to "จดราคาปิดรายวัน 20 วันจากกราฟในแอป" (ch 9 ใบ 09). Two apps closing at different hours, or one skipped day, produce a fake spread jump — the very "signal" the reader will then trade.
Where: ch 9, immediately before the 20-day table, as a 6-line box "ก่อนลบราคากัน: 4 ข้อตรวจ" (same closing time for both coins · same date on each row · no gap · unit). Add one deliberately broken row to the ใบ 09 exercise.

### 3.2 When a number is known vs when you can act on it (EX 2181–2187, 1864, 2324, LS9)
What: signal at the close of day t, fill at the next price, mark after that; a label that crosses the Formation/Test boundary belongs to the Test Period.
Why: ours has it as one worksheet row ("ตอนเปิดดูแต่ละช่วง · กดได้ที่ราคาถัดไป", ch 12 ใบ 12) and one sentence ("เข้าได้ 2.1 ไม่ใช่ 2.0 เพราะตอนเปิดดู X ข้ามเส้นไปแล้ว"). These two say slightly different things (fill at the observed price vs at the next price). Look-ahead is the most common way a beginner's backtest lies.
Where: ch 12, a three-row timeline table under "ซ้อมสามเส้นทาง" (เห็น X → ส่งคำสั่ง → ได้ราคา), and one line in ch 15's pre-registration list.

### 3.3 Hedge ratio from data, by hand (EX 1986–2048)
What: slope from a 3-row table, why squared errors, trial slopes 1/2/3, intercept, then the real h = 0.0666 read as "BTC per ETH", plus "ตัวเลขนี้เป็นสัดส่วนจำนวนเหรียญ ไม่ได้บังคับให้มูลค่า USDT ของสองขาเท่ากัน" (2048).
Why: ours sets h from the price ratio and never says there is another way. For Min's own 20 days the least-squares slope is 2.53, not 2 (I computed it from the ใบ 09 table) — so the first reader who tries a spreadsheet SLOPE will get a different spread and not know why. Our own ch 11 section on "h เปลี่ยน → X เปลี่ยน" needs a source for the new h (1.8) to be believable.
Where: ch 11, after "10 ชุด × X ขยับ 1 = +10": a short "h มาได้สองทาง" box — equal value (2.0) vs fitted from 20 days (≈ 2.5) — each with what it keeps constant, and the rule "choose before entry, do not switch mid-trade". Full hand calculation can live in a `🔎`.

### 3.4 Choosing what to plot: price difference vs ratio vs log (EX 1882–1902, 2115–2121)
What: why proportional changes need a ratio/log (100→110→121; ln 1.10 + ln 1.10 = ln 1.21), and why a ratio chart does not tell you money for fixed coin counts (A 100→110, B 50→60: +10 with 2 B, 0 with 1 B).
Why: ours uses three spread definitions — X = A − 2B (ch 9, 11–14), "% ห่างของ A เทียบ B" (simulations, ch 9–10), Z-score with "ขาละ 1,000" (ch 15 backtest) — joined by "ความคิดเดียวกัน หน่วยต่างกัน". The ratio trap is only in exercises (ch 9 ✍️ ข้อ 3, ch 11 ✍️ ข้อ 3). A reader whose app only draws A/B needs this in the main text.
Where: ch 11, in "X กระโดด 0 → 10 แต่เงินไม่ขยับ" or right after the leg table: a three-row table "เส้นที่วาด | ของที่ต้องถือให้เงินเดินตามเส้น" (A − hB ↔ fixed coins · A/B or log ↔ equal value, re-balanced). Move the ch 9 ratio exercise's content up into text.

### 3.5 Correlation computed on something the reader can see (EX 1904–1918)
What: correlation from deviations on 3 days.
Why: ours treats Correlation as a black box ("เครื่องคิด … สเปรดชีตใช้สูตร CORREL") and replaces it with a conversion table. That is a defensible choice for non-quants, but there is a consistency risk: the scene says the app shows 0.90, while CORREL on the 20 rows of ใบ 09 gives 0.77 on daily changes and 0.66 on price levels (computed), and the sheet's own count gives 89.5% same-direction days, which the conversion table maps to ≈ 0.95 (50% + arcsin(r) ÷ π).
Where: ch 9 — keep the black box, but add one sentence on what CORREL is fed (daily % changes, not prices) and either align the ใบ 09 data with 0.90 or state that the app used a longer window. Low priority to add the hand calculation.

### 3.6 "Will it come back" tested on data against a do-nothing baseline (EX 2293–2428)
What: today's level vs tomorrow's change; regress change on level; β → φ = 1 + β; half-life from data (108 days); compare forecast error with "no change" on unseen data; observe that half-life 108 ≠ 594 days actually held.
Why: ours teaches φ only through worlds where φ is given, and the only estimation method is counting time-to-target, which the same chapter calls biased. There is no "does knowing X today beat guessing 'no change'?" check.
Where: ch 13, replacing part of the counting method. A hand version exists in our own data: for the ch 9 20-day X, Σ(X today × X tomorrow) ÷ Σ(X today²) = 0.74 (computed), i.e. "ทุกวันเหลือราว 74%" → Half-life ≈ 2.3 days, close to the φ 0.80 world. That one calculation ties ch 9's table to ch 13's φ, uses only multiply/add/divide, and can be followed by the existing warning that 20 points flatter φ (our 🔎 already has the bias figure).

### 3.7 Sizing with a cap that is re-checked at the fill (EX 2151–2173)
What: value of one unit of the pair → number of units for a target gross → re-check at the fill price → cancel if above the cap; "gross cap is not a maximum loss" (2173, 2271).
Why: ours sizes by "ทุน 1,000 ÷ ราคา A 100" (gross = 2× capital) and later by the 1% rule (6 sets). The step "what if prices moved between deciding and filling" is absent, and non-round prices never occur (A 100, B 50).
Where: ch 12 "งบ −15 กับกฎ 1% ของมิน" — add a non-round example in ✍️ (e.g. A 3.27, B 0.412) so the reader divides once with awkward numbers and rounds to Lot Size.

### 3.8 Reading a result table: which number answers which question (EX 2583–2608, 2629–2643)
What: marked P&L vs closed-round-trip P&L vs unrealised; % with an explicit base (−1.91% of capital vs −20.10% of entry gross); Drawdown computed step by step (1,000 → 1,100 → 990 → 1,050 gives 10%); "start reading from what is still open"; gross exposure drifting from 950 to 1,124 while holding.
Why: ours has the result *bridge* (better, see 4) but no result *table* for a run of trades. Drawdown does not appear in ch 9–15 at all (first use ch 17). Ch 15's backtest shows two trades and a total; the 30-re-run box gives Median and range but not what a reader's own trade log should be summarised into.
Where: ch 15, after "เงินก็หลอกได้": a 6-row "อ่านสมุดไม้" table for Min's three real trades + one open paper trade (closed P&L −3 · open P&L · carry +2.1 · worst trade −21 · peak-to-trough: +18 → −3 = 21 · trades 3 of 15 needed). All numbers already exist in ch 12–14.

### 3.9 Stress tests with one knob (EX 2655–2669)
What: same positions, fee 0 / 0.1% / 0.5%; entry 1.5 / 2.0 / 2.5 with the main rule kept; "ถ้าก่อนค่าธรรมเนียมก็ขาดทุน การหาบัญชีที่ fee ถูกลงอย่างเดียวจะยังไม่แก้ปัญหานั้น" (2657).
Why: ours has the cost variant as an exercise (ch 12 ✍️ ข้อ 3: +14 / 0 / −23, 62.16%) and a warning against tuning (ch 10 🔁, ch 15). A small "same card, three costs" table makes the S9 inconsistency above into a feature.
Where: ch 12, after "+16 กับ −21": 3-row table cost 1 / 3 / 9 → endings, Break-even Win Rate, EV at 60/25/15.

### 3.10 Deciding the next experiment (EX 2790–2812, Q14–Q15, LS14)
What: a table by axis (asset selection / workflow / position management / contract structure / forecast) → "problem it would fix → what must be re-checked"; rule "change one thing, keep the rest, write the pass/fail criterion first"; a worked example (pause-at-30-days vs close-at-30-days with re-entry held equal, 2810).
Why: ours has the five-option menu (ch 14) and "แก้ทีละชั้น" (ch 15), but not a worked "next experiment" for A–B. The reader finishes ch 15 knowing they must pause and collect 15 trades, not what to change if the diagnosis says "กิ่งแรก".
Where: ch 15, end of "ไล่จากชั้นบนลงล่าง": a 5-row table "ชั้นที่เงินหาย → สิ่งเดียวที่จะเปลี่ยน → สิ่งที่ต้องคงไว้ → จะรู้ได้อย่างไรว่าไม่ช่วย".

### 3.11 A written conclusion that does not exceed the evidence (EX 2758–2784, Q13, LS13)
What: five-paragraph report skeleton with sample sentences; "ไม่เปลี่ยนเหตุผลย้อนหลัง" (2768).
Why: ours has the excellent one-sentence "ข้อสรุปแคบ" (ch 14, ch 15) but no slot for data used, rule, result with base, what is still open, assumptions.
Where: ใบ 15 — add five labelled lines; Min's filled version in the text.

### 3.12 Classifying every number by origin (EX 1760–1768, Q2, LS2)
What: read from the market / estimated / chosen / assumed / known only afterwards.
Why: our chapters mark this typographically (🔢, 🎲, "ค่าเริ่มต้นของมิน — ค่าของเล่ม ไม่ใช่คำแนะนำ") but never ask the reader to sort their own card. Sorting "h = 2, เข้า 2, งบ −15, ต้นทุน 1, φ, +16" would expose that φ and the 60/25/15 mix are assumptions.
Where: ch 12 ใบ 12, one extra column "มาจากไหน".

### 3.13 Legs filled at different moments, with order states (EX 2528–2547)
Out of my chapters (ours: ch 16). Noted only because ch 14's state table already uses OPENING/CLOSING (see S19).

### 3.14 Hints, long-form solutions and error diagnosis (EX 4235–4528)
See 1.10. Our 57-exercise appendix has answers but no hint rung.
Where: every ✍️ box in ch 9–15: split "แนวคำตอบ" into `คำใบ้ 1` (points to the table to reuse) → `คำใบ้ 2` (first line of the calculation) → `เฉลย` (full working + "ถ้าได้ … แปลว่า …").

---

## 4. Content and devices ours has that the example lacks

1. **Ground truth by simulation.** Ch 9: pairs with and without a rope, known in advance; result "ไม่มีเชือก | 0.9 | 85.7 | 59.7" vs "มีเชือก | 0.72 | 75.6 | 91.8". The example selects its pair by highest return correlation among three (EX 1880, 1934–1940) — precisely the habit our ch 9 dismantles — and can only add a caveat (1930).
2. **Selection bias made numeric.** Ch 10: top of 200 rope-less pairs crosses the mean 38 times; "การคัดยกครั้งข้ามได้ 18.8 ครั้ง … แต่ยกวันในกรอบ Test Period ได้แค่ 3.1 จุด"; the 0.95ⁿ table; false-pass vs false-cut table; the pair register that records failures. The example mentions the issue in two sentences (1940, 2659).
3. **"n = 1" boxes.** Every simulated or lived result is followed by its distribution over 30 re-runs (ch 9, 10, 12, 13, 14, 15), including the admission that the book's own example was the luckiest of 30 (ch 10: "ในเล่ม 4.82 ซึ่งเบาที่สุดใน 30 ชุด"). The example has one path of one pair and a bootstrap on forecast scores only.
4. **A complete rule card.** Ch 12: entry, signal exit, time exit, loss budget, cost, precedence; four rehearsed paths; "งบจึงเป็นจุดที่การ์ดสั่งออก ไม่ใช่เพดานที่เงินหยุดลด" (−15 → −21). The example has no price stop and no time exit; its only "stop" is a pause that leaves a position open 594 days (EX 2500, 2520).
5. **Break-even Win Rate and Expected Value.** "ใน 37 ไม้ชนะ 21 ไม้ได้ 336 แพ้ 16 ไม้เสีย 336" (ch 12) is a better derivation than a formula. The example never computes an expected value or a required win rate.
6. **Sizing from a loss rule.** "เสียชุดละ 2.1 จึงถือได้ 6 ชุด เสีย 12.6 หรือ 0.88%" (ch 12, ch 14), and the honest "ตรงนี้เขาผิด". The example sizes by target gross only.
7. **Speed of reversion vs holding time.** Ch 13: φ table, Half-life table, "Half-life ≠ Time to Target", 44.8% reach the far edge first, the same card in three worlds. The example gives one half-life number and one sentence.
8. **Pause Mode with its price.** Ch 14: right to open vs what is held; "+13 ที่พลาด กับ −21 ที่ไม่ต้องเสียซ้ำ"; asymmetric error ("เสียโอกาสที่กลับมาได้" vs "เสียเงินที่ไม่กลับมา"); resume conditions that exclude the signal. The example distinguishes the meanings of "stop" (2481–2488) but attaches no numbers.
9. **Result bridge.** Ch 15: 12 → 8 → 5 → 3 → 2, separating Forecast Error (nobody received it) from entry price, fee and carry. The example separates only price from fee (2655–2669).
10. **How many trades are needed.** Ch 15: 15 / 32 / 87 / 17,299. The example says "one trade is not enough" without a number.
11. **Who pays.** คนรีบ / คนรู้, the rope ladder, slot ② of the card. The example mentions "เหตุผลเศรษฐศาสตร์" twice (1932, 2794) and never develops it.
12. **Crypto reality of the short leg.** Short via Perpetual Futures, funding as a separate ledger line with sign (ch 11–15). The example simulates a spot short and lists funding/borrow as "not included" 11 times.
13. **Not Market-neutral, quantified.** beta exposure +500, −20 when BTC −4% (ch 11–14). The example warns (2591) without a number.
14. **Chart changes without money, three ways.** h, Mean, SD (ch 11) and "Mean เลื่อนตาม" (ch 14). The example covers h only (2127).
15. **Form.** `🛑` predict-first boxes (14), `🚶` plain-language lines (20), Min's four notebook lines and running ledger, "ทางที่ไม่ได้เลือก" scenes, "3 อย่างที่ต้องจำ", per-chapter glossary, worksheets with pass criteria and a phone task, "ถ้าเปลี่ยนตลาด", three exercise types (คำนวณ / ตัดสินใจ / ถ่ายโอน), paragraphs a third the length of the example's, four symbols instead of nineteen, consistent English-term (Thai gloss) style.

Worth expanding: 1, 3, 4, 8 and 9 are the things a reader cannot get from the example at any price; they deserve the extra worked steps listed in section 6 more than any new topic does.

---

## 5. Weaknesses of the example we should not copy

### 5.1 The real-data experiment barely happens
- Validation: 0 entries. Test: 1 entry, 0 closed round trips (EX 2631–2632). The reader never sees a completed real trade, a win, or a win rate.
- The sensitivity test is empty: "เกณฑ์เข้า 1.5, 2 และ 2.5 ใน validation ต่างไม่เกิดการเข้า" (2669).
- The "signal at close, fill at next open" lesson cannot be seen in 24/7 crypto bars: signal-day close ETH 3,032.55 / BTC 66,206.50, next-day open ETH 3,032.55 / BTC 66,206.51 (2253–2254); gross at fill 950.000085 vs target 950 (2256). Q7 asks "อธิบายว่าทำไมมูลค่าทั้งสองครั้งจึงอาจไม่เท่ากัน" for a difference of 0.000085 USDT.
- The forecast lesson teaches MSE on a signal that is essentially noise: +0.32% in train, +0.25% validation, −4.70% test (2394–2396).
Take the method (hand-check row, through-line position), not the experiment. If we add real data, choose a window with several completed round trips, including a losing one.

### 5.2 Design choices that contradict its own findings
- Pair picked by the highest return correlation of three survivors (1880, 1940); h then fitted on price levels of two trending assets. The fit is unstable by its own solution: train h = 0.0666, a = −233; full sample h = 0.0288, a = +804 (4405). Cointegration is never tested (2768).
- Half-life 108 days against a 30-day "pause" that closes nothing, no time exit, no loss limit (2428, 2500). The 594-day stuck position is a consequence of the rule set, presented as a finding.
- One-day forecast vs multi-day holding rule, acknowledged as different experiments (1704) but both kept.

### 5.3 Arithmetic
I recomputed: toy P&L (+4; fees 0.823 → +2.177), correlation 0.866025, ln 1.10 = 0.095310, OLS slope 2 / intercept 4 and the 8 / 6 / 8 trial table, SD 1.414214, z 2.828427, the real row (1,106.024856 → 94.315144 → 327.542054 → 0.576911), sizing (7,439.310326 → 0.1277000096 ETH, 0.0084998200 BTC), cash 10,174.536757, leg P&L −7.778208 / −182.250676, equity 9,809.021116, 594 and 30 days, 2,192 / 1,096 / 365 / 731 rows, half-life 108.40, e* 63.253, the three MSE percentages, −1.9098% and −20.1030%, the drawdown table, bootstrap block means, the partial-fill ledger (1,125; equity 1,000), the half-leg scenario (9,893.446418; −99.572174), LS9 differences and 1,091 pairs. **No arithmetic errors found.**
Small blemishes: 1,000 × β + α prints −5.970926 where the shown rounded terms give −5.970925 (2346, explained as full precision); the result table mixes sign conventions for drawdown ("-0.0000%" vs "5.4675%", 2637).

### 5.4 Notation and naming load
- ≥ 19 symbols in L1–L5. A whole paragraph is needed to separate h from β from "beta", and a from α (2342).
- The book's x is A − hB but the file column named x stores e; a table (2096–2101) and three later reminders (2103, 4267, 4397) exist only to repair this.
- Up to ten significant digits ("0.1277000096", "0.000692820323"); "เต็มความละเอียด" warnings recur.
- English working words without a Thai gloss, against our terminology rule: fill 71×, mark 19×, inventory 11×, maker 11×, baseline 7×, label 7×, plus gate, holdings, pending, split, protocol.

### 5.5 Length, rhythm, repetition
- 232 paragraphs of near-identical size (mean 305, median 297 chars), four or five per subsection, no summary, no key-points box, no per-lesson glossary, no character or story. It is even, not paced.
- "ยังไม่" occurs 104 times in L1–L8; the maker/borrow caveat 11 times; −190.98 six times; 594 five times.
- L7.5's block bootstrap takes seven long paragraphs (2692–2718) to reach "the interval straddles zero".
- Hints for the open questions (Q1, Q13–Q16) restate the question; there is nothing to check an answer against.

### 5.6 Audience mismatch
Eight code blocks, a ZIP of notebooks, JSON protocol files, hashes. Our reader has a phone and a spreadsheet. Anything we borrow must be doable in ใบ worksheets.

---

## 6. Prioritised change list for our chapters 9–15

Space: all seven chapters are 16.0–16.9k characters, so additions need cuts. Reclaimable without loss: the cumulative "บัตรใบ 3" table repeats rows already filled — 1,351 chars in ch 13, 1,260 in ch 14, 1,645 in ch 15 (8–10% of each chapter). Show only the rows filled in this chapter plus a link to the full card. That alone pays for most P1 items below.

### Cross-chapter
- **P1 — Show the working.** Target at least one written calculation for every number the argument rests on. Current count of shown calculations: ch 9: 3, ch 10: 1, ch 11: 19, ch 12: 11, ch 13: 5, ch 14: 4, ch 15: 10. Ch 11 is the model; bring 9, 10, 13 and 14 to that level.
- **P1 — One cost basis for ch 11–15.** Today: 12 (ch 11), 1 (ch 12–14), 2 + 3 (ch 15) for the same 10 sets. Pick a rate, derive each cost as rate × value once, keep it; put alternatives in a stress table (3.9).
- **P1 — Hint rung in every ✍️.** `คำใบ้ 1` → `คำใบ้ 2` → `เฉลย` with "ถ้าได้ … แปลว่า …" (1.10). 21 questions in these chapters.
- **P2 — One real pair, one real row, one real trade.** A short "ลองกับของจริง" strand: in ch 9 a real 20-day table with source, closing time and date; in ch 11 one real row turned into holdings and money; in ch 15 the real trade log read with the result table. Mark it visibly different from 🔢/🎲. Choose data with several closed trades (5.1).
- **P2 — Reserve ①–⑧ for the nature card.** Rename the five-box card (ch 11), the plot checklist (ch 12 sheet) and the bridge layers (ch 15 sheet) (S17).
- **P2 — One name per thing.** ชุด (not ตะกร้า); define "short X / long X" in ch 11 where "สถานะกลับด้าน" is introduced and use one of them afterwards.
- **P3 — Reader sorts their own card by origin** (read / fitted / chosen / assumed), one column in ใบ 12 (3.12).

### Chapter 9
- **P1** Before the 20-day table, add the three-line bridge from holdings to X with one numeric check (S1). Reorder: "what one set is" (5 lines borrowed from ch 11) → table → Mean → SD → Z.
- **P1** Add a second Z-score example with Mean ≠ 0 and SD ≠ 1 in the main text; say out loud that the book's pair was built with Mean 0 and SD 1 so that X reads as Z, and that the reader's pair will not be.
- **P1** Add days 21–30 for A–B and count days inside the frozen ±2 band by hand, so "อยู่ในกรอบ Test Period" is done once before the 59.7% / 91.8% table.
- **P1** Slow "ทดลองกับคู่ที่รู้คำตอบ": a 5-day hand miniature of a rope pair and a rope-less pair before "200 คู่"; move the three time rules to after the reader has seen why a Test Period is needed (after the result table); drop the survivorship clause here (it is ch 10's topic).
- **P2** "ก่อนลบราคากัน" data box (3.1) and a broken row in ใบ 09.
- **P2** State which spread to draw for a real pair and why the simulation uses % distance (3.4); one sentence, plus a pointer to ch 11.
- **P2** Reconcile the 0.90 label with ใบ 09 (CORREL on the sheet gives 0.77 on daily changes; 89.5% same-direction days maps to ≈ 0.95) or say the app used a longer window; say what CORREL is fed.
- **P3** Cut from the main text: the perp remark in the rope-ladder caption; the second 🔎 (φ 0.976, Half-life of pairs that do not revert) belongs in ch 13, where φ is defined.

### Chapter 10
- **P1** Count mean crossings on the ch 9 table (3 in 20 days) before "38 ครั้ง"; give the per-day rate for both (3 ÷ 20 vs 38 ÷ 250) so the reader sees the score.
- **P1** Rewrite the paragraph under the threshold table as counts out of 200, one error type per sentence, and explain why the fake-pass column hardly moves between 85% and 95% (S6).
- **P2** Say in one line that this chapter uses two simulated sets (its own 200 rope-less pairs: 57.1%; ch 9's 200 + 200: 59.7% / 91.8%) and why.
- **P2** Give the −4.85 SD → 16–17% conversion one visible line.
- **P2** Show the pair register with one more ordinary failed row (not only the rank-1 pair), so "จดคู่ที่ไม่ผ่าน" is modelled.
- **P3** "กรอบรั่ว" is a strong result squeezed into four lines; give it the two numbers as a small table (97.2 / 95.3 vs 59.7 / 91.8).

### Chapter 11
- **P1** Derive the costs: rate × value for entry and exit, per leg; make "ระหว่างถือ" consistent in sign with the funding paragraph (either the short leg pays in this example or the 3 is something else). Turn the cash walk into table rows (S8).
- **P1** Add the "แบบ perp" twin of the Equity table with a margin line and where the margin money comes from; do not defer it to ch 16 (S7).
- **P1** New short section "h มาได้สองทาง" (equal value 2.0 vs fitted ≈ 2.5 on the ch 9 table) and what each choice means for what you hold (3.3). This also gives the "h เป็น 1.8" update a cause.
- **P2** Bring the ratio trap from ✍️ ข้อ 3 into the text as a 3-row "เส้นที่วาด ↔ ของที่ต้องถือ" table (3.4).
- **P2** Add the four-question table for one price pair: ราคา A · X · ระยะจาก Mean · Z-score — "ตัวไหนคือเงิน" (EX 2060–2065 device).
- **P3** The beta-exposure paragraph interrupts the h explanation mid-flow; move it after "กำไรจากราคา = จำนวนชุด × การเปลี่ยนของ X".

### Chapter 12
- **P1** Fix the cost (see cross-chapter) and add the "same card, three costs" table (3.9).
- **P1** Split the assumptions sentence into a four-row box; replace "คาดได้ 6 ต้นทุน 3 เผื่อพลาด 1" with the card's own numbers; move "งบ −15 ตรงกับ X ราว 3.5" after the paths table and show the one-line solve (S10, S11).
- **P1** Let B move in at least one rehearsed path so the ledger has two live legs; otherwise ch 12–14 quietly become one-leg trades.
- **P2** Three-row timeline (เห็น → ส่ง → ได้ราคา) and make the text and ใบ 12 agree on whether the fill is at the observed price or the next one (3.2).
- **P2** Cut or expand the "ชนะ 65% … 77.5% (บท 18)" sentence (S12).
- **P2** Label 60/25/15 and 45/20/35 as assumed mixes at first mention and promise the measured mixes of ch 13.
- **P3** Non-round sizing exercise with Lot Size (3.7).

### Chapter 13
- **P1** Write out the net results (10.81, −0.21, +2.08, −7.44) as calculations with the unrounded inputs visible (S13, S16).
- **P1** Add the "SD ของ X ในโลกนี้" row to both simulation tables and one sentence on the consequence for a card written in X; or re-run "กฎเดียวสามโลก" entering at Z = 2 in each world and show both versions (S14).
- **P1** Add the hand estimate of φ from the ch 9 table (≈ 0.74 → Half-life ≈ 2.3 days) as the primary method; keep counting as the cross-check; break the counting paragraph into numbered steps and work the Median (S16, 3.6).
- **P2** Bridge to ch 12: why 26.4 / 73.4 / 0.1 is not 60 / 25 / 15 and still earns +8.70 (S15).
- **P2** Add a do-nothing comparison: "ถ้าทายว่าพรุ่งนี้ X เท่าเดิม ผิดเท่าไร เทียบกับทายว่าเหลือ 80%" on five rows of the ch 9 table.
- **P3** The "⚖️ สองคำที่ฟังคล้ายกัน" box and the perp/basis transfer bullets can shrink; the chapter introduces 7 terms already.

### Chapter 14
- **P1** Reduce the state table to FLAT / OPEN × ACTIVE / PAUSED here; move OPENING / CLOSING to ch 16 (S19).
- **P2** Show the 62% (21 ÷ 34) derivation as "ชนะได้ 13 แพ้เสีย 21 → ใน 34 ไม้ต้องชนะ 21", the same 37-trade device as ch 12.
- **P2** Add the three meanings of "หยุด" as a three-row table with what happens to holdings, cash and open orders in each (EX 2481–2488 device, with our numbers: พัก = holdings unchanged, carry keeps running; ปิด = pay exit cost 0.6; คัดออก = register entry).
- **P2** After the five-option menu, add a worked "next experiment" for A–B: one change, what stays fixed, what result would mean it did not help (3.10).
- **P3** The multi-pair paragraph (−60) is a new topic in three lines; either give it a small table or leave it to ch 17.

### Chapter 15
- **P1** Add the wobble ladder (4 / 16 / 64 trades) in the main text before the trades-needed table, and one sentence on what SD means for a three-outcome result (S18).
- **P1** Print Min's six-line pre-registration for A–B filled in (S20).
- **P2** Add the "อ่านสมุดไม้" result table for Min's three trades, including peak-to-trough (+18 → −3) as a first, unnamed Drawdown (3.8).
- **P2** Add the five-line conclusion template to ใบ 15 with Min's filled version (3.11).
- **P2** The bridge counts entry price only; add the exit price layer or say why it is zero, so "ทุกชั้นรวมได้ตัวเลขในบัญชี" holds for a reader's real trade.
- **P2** Trades-needed for the ch 13 worlds as well as the ch 12 mixes (S15).
- **P3** Remove Sharpe Ratio from the chapter glossary unless it is used in the text (it appears only in a 🔗 line).

### What not to import
Python/notebook workflow; price-level OLS on two trending coins as the default hedge ratio; correlation as the pair selector; a baseline with no loss limit; the symbol set; ten-digit numbers; block bootstrap; unglossed English working vocabulary.
