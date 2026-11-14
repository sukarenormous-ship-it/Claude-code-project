# Report D — Overall design and reader experience: example book vs ours

Scope: whole-book design, section template, density, navigation load, exercises.
Sources: example = `ea8791aa-Stat_Arb_Hands_On_Complete_v1_0.md` (5,522 lines; cited as **EX L###**); ours = text dumps in `compare/ours/` (cited as **file L###**, e.g. `part4 L55`), plus `docs/sab-book-plan.md` (cited as **plan L###**).
All numbers come from stdlib-Python scripts in `compare/scripts/` (`measure.py`, `measure2.py`, `exparts.py`, `exer.py`, `pace.py`, `ourdev.py`, `exdev.py`); they can be re-run with `python3 -I <script> <example.md> <ours dir>`.

Method limits, stated once: Thai is measured in non-space characters, not words. "English words" are Latin-letter tokens of 3+ letters (code blocks excluded). Our dumps are plain-text conversions, so paragraph/list detection is by line type. The example's 30 figures were not available; they are counted from image links and judged only by their captions and "อ่านภาพ" lines.

---

## 0. The verdict in one paragraph

The two books are built on opposite bets. The example bets on **slowness and one voice**: 299K characters of continuous "we do this together" prose, three labelled devices, zero emoji, a 36.6K-character foundation that introduces 13 English words. Ours bets on **story, compression and apparatus**: a strong character-driven plot and far richer trading reality (margin calls, who pays, crowding), but only 42% of each chapter is teaching narrative, 48% is end-matter boxes, and chapter 0 alone asks the reader to absorb 31 English words in its first 12,000 characters where the example has introduced 5. On matched concepts the example spends 5–13 times more characters than we do. For a true beginner the example is easier to follow; ours is more motivating and more useful once understood. The way to beat it is not to copy its length but to put its step granularity inside our story, and to pay for that by cutting our template roughly in half.

---

## 1. Reader journey

### 1.1 Example

**Assumed reader.** Nobody who has traded before is assumed. The first teaching sentence is "สมมติคุณกำลังดูสินทรัพย์ชื่อ B หน้าจอบอกว่าราคา 100 บาท ตัวเลขนี้เป็นราคาของ B หนึ่งหน่วย" (EX L61). The reader is assumed to be able to move to Python later: "ถ้าเริ่มอ่านบนโทรศัพท์ ใช้ PDF และคำนวณตัวอย่างสั้นบนกระดาษได้เลย เมื่อต้องการลองโค้ด ให้แตก ZIP ทั้งชุด" (EX L792), and from the Tools part onward to read Σ, an SDE (EX L3030) and a partial derivative (EX L3344).

**What they can do at the end.** Write a six-part research report that ends in "ทำต่อ พัก หรือเลิกใช้" (EX L5192–5199), re-run a real-data pair study on BTC/ETH/BNB daily data 2020–2025 (EX L1644), and place themselves on a four-step ladder "ทำตามตัวอย่าง → ใช้คำใบ้ → ทำโจทย์เดิมเอง → ประยุกต์กับโจทย์ใหม่" (EX L5207–5212). Success is explicitly not profit: "ไม่มีเงื่อนไขว่าต้องทำให้ผลกำไรเป็นบวกจึงจะเรียนรู้สำเร็จ" (EX L5214).

**Dependency chain.**
1. ภาคพื้นฐาน 1–22 (EX L55–723): buy then sell one unit → two units (price per unit vs quantity vs money) → short → two legs lose/win/offset → why two units of B → what to plot → costs → what if the gap does not close → 4 exercises with solutions.
2. Bridge + section 0 (EX L724–864): the question, the map of the book, evidence types, files, example conventions.
3. ตอน A (EX L865): why x = A − hB; profit = −Δx; reference level; fitting h and a by hand from six rows; out-of-sample; futures rate.
4. ตอน B (EX L1224): one full round trip in the account — size, signal vs fill, cash, holdings, equity, partial fill.
5. ตอน C (EX L1472): the same round with things going wrong — cost, look-ahead, divergence, open positions, h changes.
6. L0–L8 (EX L1636–2842): the same pipeline on real data: hypothesis → data → variable → size and account → forecast vs baseline → rules and pause → reading results → next experiment.
7. เครื่องมือ 1–6 and กรณี 01–09 (EX L2843–4133): reference material opened on demand.
8. Exercises P1–P10, Q1–Q16 (inside lessons), PX1–PX15, each with hints and solutions; glossary; project hand-off.

**How the reader knows where they are.** Only by section codes (พื้นฐาน 7, A.4, L6.5, T2.3, K05.2, PX11) and three tables: the part-by-question map (EX L755–761), "ชิ้นงานที่นำไปใช้ต่อ" per lesson (EX L1679–1688), and "คำถามที่กำลังติด → กลับไปอ่านในเล่มนี้" (EX L5224–5233). The teaching body contains 245 internal code references and no pointers to other books; outside sources are cited as [R#] to the reference list.

### 1.2 Ours

**Assumed reader.** "เล่มนี้เขียนให้คนที่ซื้อขายเหรียญบน exchange เป็นและคิดเลข + − × ÷ % ได้ แต่ไม่มีพื้นสถิติและไม่เขียนโค้ด" (index L17; plan L212). In practice chapter 0 also assumes the reader can take in spot, dated futures, perp, funding, settlement price, basis, long, short, hedging and stat arb in one sitting (the 📖 box of chapter 0 lists 11 terms, part0 L363–389).

**What they can do at the end.** Fill the 8-slot nature card for a strategy, keep a two-leg ledger, size a cash buffer, walk a yield "ladder" from screen rate to excess over hurdle, write a 6-line rule card, and issue a four-level verdict (ไม่รับ · กระดาษ · เล็ก · ปกติ) on their own and other people's ideas (part18 L118–130). Twenty worksheets (ใบ 00–18, 02b) are the take-away artefacts.

**Dependency chain.**
1. Part 1, บท 0–7: basis 3,000 and two legs (0) → costs and margin (1) → EV and who pays (2) → two-leg ledger (3) → margin call and cash buffer (4) → yield ladder and crowding (5) → close or hold (6) → perp funding (7).
2. Part 2, บท 8–14: hedge, beta, exposure (8) → correlation vs "rope", mean/SD/z, formation/test (9) → selection bias (10) → pair ledger (11) → rule card and break-even win rate (12) → reversion speed (13) → loss and pause mode (14).
3. Part 3, บท 15–18: loss attribution (15) → execution and capacity (16) → nature of stat arb (17) → transfer and verdict (18).
4. Appendices A–I, four interactive tools, an 8-tab workbook.

**How the reader knows where they are.** A 🧭 box at the top of every chapter with three colour-coded reading paths and a one-line "เรื่องที่ผ่านมา" (part4 L13–17); a dated scene (part4 L33 "วันที่ 9 · 23:40"); a running account table and a nature card with filled and pending slots at the end of every chapter (part4 L218–270); a TOC with a headline number per chapter (index L39–97); a symptom index (appendix-map L33–59). The chapters contain 442 "บท N" references (187 of them parenthetical forward/back pointers) and 76 named pointers to other books in the repo.

### 1.3 What the comparison shows

| | Example | Ours |
|---|---|---|
| First thing the reader is asked to understand | one unit bought at 100, sold at 101 (EX L61–77) | BTC spot 100,000 vs 90-day futures 103,000, long one leg and short the other (part0 L23–27) |
| Running example | one pair, A=208, B=100, h=2, reference 4, reused through A–C, L3, L5 and solutions ("208" occurs 158 times) | two: BTC 100,000/103,000 (Part 1) and X = A − 2B (Part 2), each with a ×100 or "real size" convention |
| Reader's role | co-calculator ("เรา" 29.4 per 10,000 chars) | observer of Min ("มิน" 15.1 per 10,000 chars; "เรา" 1.6) |
| Motivation | none beyond curiosity; no character, no stakes | strong: scene, question, cliffhanger in every chapter |
| Real data | yes, with an honest null result (position open 594 days, EX L2520) | none ("📡 ข้อมูลจริง ยังไม่มีในรุ่นนี้", index L161) |
| Needs code | yes for L1–L8 | no (workbook + tools) |

---

## 2. Section anatomy

### 2.1 The example's template

A `##` part has 3–7 `###` subsections (median 6 prose paragraphs, 1,516 characters each). The recurring moves:

1. **Opening move: link back, then one concrete situation.**
   "ภาคพื้นฐานพาเราเดินเงินของ B ทีละหน่วยแล้ว คราวนี้เราจะใช้ภาพเดิมตอบคำถามใหม่ว่า ถ้า A และ B ขยับไปด้วยกัน เราจะสร้างตัวเลขที่ช่วยมองเห็นส่วนที่ขยับต่างกันได้อย่างไร" (EX L871).
   "สมมติ z มากกว่า 2 ติดต่อกันสามวัน ถ้าโปรแกรมอ่านเพียงว่า “z มากกว่า 2 ให้ขาย” มันอาจขายเพิ่มทุกวัน ทั้งที่เราตั้งใจเปิดเพียงหนึ่งชุด" (EX L2448). Of the 30 part openings printed by `exends.py`, nearly all begin with "สมมติ…", "ลอง…" or a one-sentence recap of the previous part.

2. **New term: do the thing first, name it afterwards, then say the name adds nothing.**
   "การถือแบบ “ซื้อไว้ก่อน แล้วขายออกภายหลัง” นี้เรียกว่า **long** ถ้าเห็นข้อความว่า “long B หนึ่งหน่วย” ให้แปลเป็นภาพธรรมดาว่า เราซื้อ B หนึ่งหน่วยมาไว้ในมือ" (EX L81).
   "การมีคำว่า long, entry และ exit ไม่ได้เพิ่มเหตุการณ์ใหม่เข้ามา เป็นเพียงชื่อที่ใช้เรียกสิ่งที่เราเพิ่งทำ" (EX L102).

3. **Numbers: follow the money one sentence at a time, write the compact formula last, then check a second way.**
   "เมื่อเห็นเงินครบทั้งสองด้านแล้ว จึงเขียนการคำนวณสั้น ๆ ได้ว่า เงินรับกลับมา − เงินที่จ่ายไป =198−200=−2 บาท" (EX L130).
   "ลองตรวจด้วยเงินรวมอีกทาง เรารับเงินขาย A 208 และรับเงินขาย B 202 รวมรับ 410 ขณะที่จ่ายซื้อ B 200 และซื้อ A คืน 206 รวมจ่าย 406 จึงเหลือ 4" (EX L929).
   The stated principle: "สังเกตว่าเราไม่ได้เริ่มจากการท่องว่าจะนำราคาไหนลบราคาไหน เราตามเงินก่อน" (EX L79).

4. **Checkpoint ("พักตรงนี้ได้").** Full instance: "**พักตรงนี้ได้:** long B คือซื้อ B ไว้ก่อน ตอนเข้าจ่ายเงินซื้อ ตอนออกรับเงินขาย ตัวอย่างหนึ่งหน่วยนี้จ่าย 100 รับ 101 จึงได้ 1 บาทก่อนต้นทุน" (EX L104). Used 5 times, all before EX L356, then abandoned.

5. **Figure reading ("อ่านภาพ:").** Full instance: "อ่านภาพ: ตอนซื้อ เงิน 100 บาทออกไปและได้ B หนึ่งหน่วยมา ตอนขาย B หน่วยนั้น เงิน 101 บาทกลับมาและไม่มี B เหลืออยู่ จึงได้เงินเพิ่ม 1 บาทก่อนต้นทุน" (EX L75). 30 uses, one per figure.

6. **Equation reading ("อ่านสมการ:").** Full instance, after `x_t = P_A,t − h·P_B,t`: "อ่านสมการ: ให้นำราคา B ณ เวลาที่สนใจคูณจำนวน h ก่อน แล้วจึงลบออกจากราคา A ณ เวลาเดียวกัน วันนี้จึงเป็น 208 − 2 × 100 = 8 U ต่อชุด" (EX L895). 39 uses; every display formula is followed by one, with the running numbers substituted.

7. **Disambiguation tables.** "แยกตัวเลขสามชนิดนี้ให้ออก" — price per unit / quantity / total money (EX L140–150); "ตัวเลข | ได้มาอย่างไรในตัวอย่าง | ใช้ทำอะไร" (EX A.3). A self-check question is handed to the reader: "นี่คือราคาหนึ่งหน่วย หรือเงินของทุกหน่วยรวมกัน?" (EX L152).

8. **Predict before reveal** — given once as a reading instruction, not as a device: "ให้หยุดก่อนบรรทัดเฉลยแล้วลองคาดว่าผลจะเป็นอย่างไร … หากติด ให้ใช้คำใบ้ระดับแรกเพื่อหาจุดเริ่ม แล้วค่อยเปิดระดับที่สองหรือเฉลย" (EX L765).

9. **End of section: exercise pointer plus a bridge sentence.** "Q11 ใช้วันที่ของสถานะแรกเขียนเหตุการณ์ตั้งแต่ไม่มีสถานะ …" then "เมื่อระบุการกระทำตามสถานะครบแล้ว เราจึงอ่านผลทั้งช่วงได้โดยรู้ว่าเงินเปลี่ยนจากอะไร บทถัดไปจะรวมบัญชี คะแนนพยากรณ์ และภาระที่ยังค้าง" (EX L2553–2557). Tools and cases end with "ลองใช้ PX1 ทบทวน…" (EX L2943). There is no summary box and no vocabulary box.

10. **Exercise → two-level hint → reasoned solution** (quoted in section 5).

The whole device inventory is: section codes, bold run-in sub-headings (63), tables (112 in the teaching body), "อ่านภาพ" (30), "อ่านสมการ" (39), "พักตรงนี้ได้" (5), code blocks (25). No emoji, no boxes.

### 2.2 Our template

Plan L353–379 specifies 23 boxes per chapter. As built, a chapter runs in this order (chapter 4 as the instance): 🧭 เส้นทางอ่าน with three paths (part4 L13–17) → 🟠 catch-up box (L21–29) → 📓 scene with Min's four lines (L33–49) → chapter question (L51) → 5–7 sections whose headings carry the key number ("equity −200 แต่ต้องโอน 11,220", L53) → inside them 🛑 predict prompts (L100), 🚶 plain-language line before a formula (L120–122), 🔢 provenance tags, 🎬 road-not-taken scene (L106), 📊 n = 1 distribution box (L145), 🔎 folded deep-dive (L162) → 🏦 (L184) → ⚠️ defaults (L198) → 🧭 thinking habit (L204) → 🧮📒 Min's account (L218) → 🧬 nature card with 8 slots (L244–270) → 🛠 worksheet with 🔩 why, ✅ pass criteria, 📱 from-your-app (L274–312) → 🔁 if the market changes (L316) → ✍️ three exercises with folded answers (L326–348) → 🎯 three things to remember (L352) → สรุป (L362) → bridge question (L366) → 🔗 deeper links at three colour levels (L370–378) → 📖 new vocabulary (L382–404).

Measured consequence (`measure2.py`): across 19 chapters, front matter is 10% of characters, the teaching sections are **42%** (109,313 chars), and everything from the first end-matter box onward is **48%** (125,413 chars). In chapter 4 the teaching sections end at L180 of 405. This is by design: plan L360 budgets "เนื้อหา 900–1,100" words inside a main path of about 1,980–2,200 (plan L381).

### 2.3 Device-by-device judgement

| Device | Example | Ours | Better for a beginner, and why |
|---|---|---|---|
| Opening | recap + neutral "สมมติ…" situation | dated scene with stakes, a wrong instinct, and a question (part4 L35–51) | **Ours.** The margin-call night is a reason to care; the example never gives one. But our scene already uses 6–8 glossed terms before the first section (part4 L35–39: Margin Call, Futures, Margin, Equity, Free Cash). |
| Introducing a term | event first, name second, one term at a time (EX L81) | name first with Thai gloss in the sentence that also uses it: "Long (สถานะซื้อ/ถือซื้อ) คือได้เมื่อราคาขึ้น ส่วน Short (สถานะขาย/ขายชอร์ต) คือได้เมื่อราคาลง เหมือนขายไว้ก่อน…" (part0 L45) | **Example.** Ours defines long and short in one sentence; the example gives each its own subsection (EX L59–107, L156–216). |
| Working numbers | one operation per sentence, money trail, formula last, second check | several operations per sentence: "ขา spot ได้ 110,000 − 100,000 = +10,000 ส่วนขา short futures เสีย 113,200 − 103,000 = 10,200 รวมสองขาได้ −200 เท่ากับ basis ที่กว้างขึ้นจาก 3,000 เป็น 3,200 พอดี" (part4 L55) | **Example**, clearly. Ours is correct and elegant but each sentence is a finished result, not a step. See the pacing table in 3.3. |
| Predict-then-reveal | one global instruction (EX L765) | 37 inline 🛑 prompts, e.g. "ราคา BTC วันหมดอายุต้องเป็นเท่าไร มินถึงจะไม่ได้ 3,000?" (part0 L71) | **Ours.** Placed exactly where the surprise is. Keep. |
| Checkpoint | "พักตรงนี้ได้" ×5, then dropped | none mid-chapter; 🎯 + สรุป at the very end, after ~200 lines of apparatus | **Example's idea, done by neither.** A one-sentence recap after each section is missing in ours and inconsistent in theirs. |
| Figure reading | "อ่านภาพ:" says what moves and what to conclude | caption = provenance tag + dense facts: "🔢 ตัวเลขสมมติเพื่อสอน · แท่งไม่รวมเงิน 100,000 ที่ซื้อเหรียญ · equity = 100,000 + สามแท่ง · ราคาขึ้น 10% วันที่ 9 equity เปลี่ยนแค่ −200 แต่เงินย้ายกระเป๋า 11,220" (part4 L88) | **Example.** Ours tells the reader what is true, not how to look. |
| Equation reading | after the formula, with numbers | 🚶 before the formula in words (44 uses); numbers often inside the formula line (part12 L128) | **Tie; combine.** Words before (ours) plus numeric substitution after (theirs) is better than either. |
| Honesty about evidence | "สิ่งที่ยังตอบไม่ได้" table (EX L777–782) | 🔢/🎲/📱 tags on every table (106 + 20 + 25 uses), n = 1 boxes with 30 re-seeds (part9 L135–137) | **Ours** for rigour; but the tag is repeated so often it becomes noise. One table like the example's, once, would carry most of it. |
| End of section | exercise pointer + bridge | 14 boxes, then bridge | **Example.** The bridge question in ours is good (part4 L366) but arrives 185 lines after the teaching stops. |
| Summary | none | 🎯 three bullets + สรุป paragraph | **Ours**, but the two say the same thing twice (part4 L354–364). |
| Vocabulary | one glossary at the back (24 rows) | 📖 box per chapter (172 items) + three-tier glossary appendix | **Ours**, if capped. Mean 9.1 new items per chapter is too many. |
| Take-away artefact | per-lesson artefact table (EX L1679–1688), notebooks | 20 worksheets with Min's filled copy and pass criteria | **Ours** for a non-coder. |

---

## 3. Density and readability measurements

### 3.1 Whole teaching body (`measure.py`)

Example = EX L55–4133 (foundation through case 09). Ours = บท 0–18.

| Metric | Example | Ours |
|---|---:|---:|
| Characters, teaching body | 298,810 | 250,738 |
| of which teaching narrative (ours: sections only) | 298,810 | 109,313 |
| Units (## parts / chapters) | 30 | 19 |
| Characters per unit | 9,960 | 13,197 |
| Prose paragraphs | 1,090 | 1,087 |
| List items | 2 | 789 |
| Characters per prose paragraph, median (p90) | 252 (372) | 120 (245) |
| Prose paragraphs under 80 characters | 9% | 32% |
| Numbers per 1,000 characters | 19.3 | 28.3 |
| Prose paragraphs containing 3+ numbers | 46% | 42% |
| Text blocks (paragraph or list item) with 3+ numbers | 46% | 31% |
| Arithmetic steps written out (digit-operator-digit) per 1,000 chars | 2.52 | 2.02 |
| English word tokens per 1,000 characters | 9.0 | 17.3 |
| Distinct English words | 410 | 271 |
| Tables (per 10,000 chars) | 112 (3.7) | 115 (4.6) |
| Figures (per 10,000 chars) | 30 (1.0) | 34 (1.36) |
| Display formulas | 38 | 21 |
| Emoji types used | 0 | 36 |
| Labelled recurring devices | 3 | 22 box types (91 distinct box titles) |
| Whole book incl. appendices | 379,090 | 460,659 |

Reading the table: the two books have the same number of paragraphs, but the example's are twice as long and continuous, while ours is fragmented into short paragraphs and 789 bullets. Ours carries 47% more numbers per character and writes out fewer of the arithmetic steps, so each number arrives with less explanation. Ours has nearly twice the English-token density, largely because glossed terms are repeated (3.4 below).

### 3.2 How fast the vocabulary arrives

Cumulative distinct English words after N characters of teaching text:

| After N chars | Example | Ours |
|---:|---:|---:|
| 5,000 | 4 | 22 |
| 12,000 | 5 | 31 |
| 25,000 | 5 | 57 |
| 50,000 | 61 | 86 |
| 100,000 | 113 | 122 |
| 200,000 | 284 | 240 |

First unit head to head — example foundation (EX L55–723) vs our chapter 0:

| | Example foundation | Our chapter 0 |
|---|---:|---:|
| Characters | 36,182 | 12,983 |
| Prose paragraphs / list items | 253 / 2 | 60 / 52 |
| Distinct English words | 12 | 33 |
| Distinct English words per 1,000 chars | 0.33 | 2.54 |
| Tables / figures / formulas | 9 / 9 / 0 | 4 / 2 / 2 |

The example front-loads almost nothing and back-loads heavily (it ends with more distinct English words than we do). Ours front-loads: 17 newly glossed terms in chapter 0 and 16 more in chapter 1 (`measure2.py`: new glossed terms per chapter = 17, 16, 8, 9, 8, 5, 4, 4, 11, 11, 4, 4, 2, 3, 3, 4, 5, 4, 2).

### 3.3 Pacing on matched concepts (`pace.py`)

| Concept | Example chars (where) | Our chars (where) | Ratio |
|---|---:|---:|---:|
| Long and short of one asset | 5,820 (EX L59–107, 156–216) | 847 (part0 L43–61) | 6.9× |
| Two legs: P&L under different futures | 8,747 (EX L217–378) | 1,191 (part0 L63–98) | 7.3× |
| Cash, holdings, equity per fill | 7,944 (EX L1300–1419) | 1,498 (part3 L41–77) | 5.3× |
| Building the yardstick from data (h and reference / mean, SD, z) | 7,642 (EX L1009–1136) | 1,237 (part9 L75–97) | 6.2× |
| What z means | 4,388 (EX L2052–2112) | 332 (part9 L95–97) | 13.2× |
| Spread change → money with signed quantities | 4,492 (EX L909–966) | 2,611 (part11 L43–113) | 1.7× |

For the pair-trade pipeline as a whole: example foundation + A–C + L0–L8 = about 185,700 characters; our Part 2 teaching sections (บท 8–14) = 37,116 characters. The instance that best shows the gap is the standard deviation in our chapter 9, taught in one bullet: "2 ใน 3 ของ 20 วันคือราว 13 วัน เรียงระยะห่างจาก Mean (ไม่สนเครื่องหมาย) จากน้อยไปมาก ค่าที่ 13 คือ 0.9 ค่าที่ 14 คือ 1.1 เส้นแบ่งจึงอยู่ราว 1: แถบ ±1 มี 13 จาก 20 วัน (65%) ระยะจาก Mean ถึงขอบแถบนี้คือ 1 Standard Deviation" (part9 L89). The idea (count, do not compute) is better than the example's; the execution is one sentence where a beginner needs a page.

### 3.4 Our chapter composition and vocabulary load (`measure2.py`)

- Teaching sections per chapter: 4,701–6,558 characters. End matter per chapter: 5,552–7,331 characters. In 16 of 19 chapters the end matter is larger than the teaching sections (all except บท 0, 4 and 17).
- 124 distinct glossed English terms, 545 gloss occurrences. "Margin (หลักประกัน)" is glossed 16 times, "Short" 15, "Basis" 15, "Funding Rate" 14. Within chapter 4 alone there are 33 gloss occurrences for 19 terms. Plan L385 says "คำอังกฤษใส่วงเล็บครั้งแรกเท่านั้น"; the built chapters gloss in the catch-up box, the scene, the question, and the 📖 box.
- 📖 boxes list 172 items, 6–12 per chapter, mean 9.1. Plan L381 targets "ศัพท์ใหม่ 5–8 คำ".
- Chapter 0 contains 13 pointers to other chapters before the reader has finished the first one (e.g. part0 L148–156: บท 1, บท 4, บท 6, บท 5, บท 2, บท 2–4).

### 3.5 The example is not uniform (`exparts.py`)

| Part | Chars | Median para | Paras with 3+ numbers | New English words | Figures | Formulas |
|---|---:|---:|---:|---:|---:|---:|
| Foundation 1–22 | 36,607 | 133 | 33% | 13 | 9 | 0 |
| Bridge + 0.x | 9,703 | 259 | 19% | 48 | 0 | 0 |
| A–C | 54,544 | 239 | 55% | 54 | 10 | 10 |
| L0–L8 | 84,905 | 272 | 38% | 147 | 8 | 10 |
| Tools 1–6 | 63,979 | 334 | 61% | 102 | 2 | 13 |
| Cases 01–09 | 52,899 | 294 | 63% | 49 | 1 | 5 |

The gentle book is the first 100K characters. After that paragraphs grow to 300+ characters, figures nearly vanish (3 in 117K characters), and 147 new English words land in L0–L8.

---

## 4. Navigation and cognitive load in ours

### 4.1 Inventory of recurring boxes, labels and emoji (19 chapters; `ourdev.py`)

| Device | Count (chapters) | Verdict for a beginner |
|---|---|---|
| 🧭 เส้นทางอ่าน (three colour paths + "เรื่องที่ผ่านมา") | 19 (19) | **Overhead as built.** Keep the one-line recap; move the three paths to the index page. |
| 🟠 ย่อจากบทที่ข้าม | 6 (6) | **Overhead for the main reader**: a box of 4–5 compressed definitions at the top of the chapter (part12 L21–31) that only fast-path readers need. |
| 📓 สมุดของมิน scene + four lines | 19 (19) | **Helps.** The book's best asset. |
| Chapter question / bridge question | 37 (19) | **Helps.** |
| 🛑 หยุดคิด/ทายก่อน… | 37 (19), at least six label variants | **Helps.** Use one label. |
| 🚶 อ่านเป็นภาษาคนก่อน | 44 (19) | **Helps.** |
| 🔢 / 🎲 / 📱 provenance tags | 106 / 20 / 25 | **Helps once, noise after.** 106 repetitions of "ตัวเลขสมมติเพื่อสอน" (68 in full). |
| 🔎 ลงลึก [รอบสอง] folds | 25 folds (18 chapters) | **Neutral.** Collapsed, clearly optional. In บท 0–6 they sit inside the sections; from บท 7 on they sit at the very end of the chapter. |
| 🎬 ทางที่ไม่ได้เลือก | 10 (10) | **Helps** (counterfactual with a second character). |
| 👥 คนอีกฝั่ง | 8 (7) | **Helps**, but it is where คนเร่ง / คนรีบ / คนรู้ are coined (see 4.2). |
| 📊/🎲/🔢 "หนึ่งเส้นทาง (n = 1)" | 12 (12) | **Helps**; unique strength. Three different emoji for one device. |
| 🧠 มุมที่มองต่าง | 9 (9) | **Overhead**: restates the summary (part9 L172–174 vs L379). |
| ⚠️ ค่าเริ่มต้น | 19 (19) | **Overhead as a box.** "ค่าของเล่ม ไม่ใช่คำแนะนำ" appears 18 times. One line under the relevant table is enough. |
| 🧭 นิสัยคิด | 19 (19) | **Overhead.** 4–6 more questions per chapter, on top of "สี่คำถาม"; chapters 9 and 12 each add a different "หกคำถาม" (part9 L184, part12 L189). Same emoji as the reading-path box. |
| 🧮 📒 บัญชีมินท้ายบท | 19 (19) | **Mixed.** Useful when the account changed; in chapter 0 it reports "ยังไม่เปิด" (part0 L226–238). Two columns because of the ×100 convention. |
| 🧬 ธรรมชาติของกลยุทธ์ + 8-slot card | 19 (19); circled digits ①–⑧ 413 times | **Overhead per chapter, valuable per part.** The card is the book's organising idea but is shown half-empty 15 times. |
| 🛠 ใบงาน with 🔩 / ✅ / 📱 | 20 (19) | **Helps**, but the full sheet is printed in the chapter and again twice in appendix E (68K characters, blank and filled). |
| 🔁 ถ้าเปลี่ยนตลาด | 19 (19) | **Overhead**: duplicates the (ถ่ายโอน) exercise that follows (part4 L318 points to "✍️ ข้อ 3"). |
| ✍️ ลองทำเอง | 19 (19), 57 items | **Helps**; too few and no hints (section 5). |
| 🎯 3 อย่างที่ต้องจำ + สรุป | 19 + 19 | **Helps; merge.** |
| 🔗 อยากลึกกว่านี้ (🟢🔵🟣) | 19 (19), 76 external links | **Overhead** for a beginner; appendix A already has the same map (appendix-map L129). |
| 📖 ศัพท์ใหม่ | 19 (19), 172 items | **Helps if capped at about 5.** |
| 🏦, ⚖️, 👤, 📘, 🗂, 🔧 one-off boxes | 1–3 each | Overhead; each is a new visual signal to decode. |

Collisions that a beginner will trip on:
- **🧭** means both "reading path" and "thinking habit" (38 uses).
- **🟢 🔵** mean reader types in the 🧭 box (part0 L15) and depth levels of links in the 🔗 box (part0 L353–357).
- **①–⑧** have three meanings: nature-card slots, nq "stations", and the price rows of ใบ 00 (part0 L250–256). Our own appendix warns about the first two: "⚠️ วงกลมเลขในหน้านี้มีสองความหมาย" (appendix-map L21–23). Chapter 18's verdict paragraph is unreadable without the card memorised: "carry BTC → เล็ก เพราะ ① สัญญาบังคับบรรจบ และ ⑤ ส่วนเกิน 5.23% ยังเหลือหลัง hurdle แต่ ⑧ exchange ระงับถอน…" (part18 L122).
- **🔢 🎲** are provenance tags and also box-title emoji (part12 L169, part9 L135).

### 4.2 Book-specific coined words (occurrences, chapters)

| Word | Count | Verdict |
|---|---|---|
| เชือก | 261 (19) | **Keep.** The unifying image; introduced with care (part0 L102). |
| กันชน | 73 (16) | Keep; it is the glossary translation of Cash Buffer. |
| ในกรอบ / คู่ปลอม | 53 (9) / 27 (7) | Keep; plain Thai. |
| ค่าผ่านทาง | 48 (7) | Keep; intuitive for costs. |
| คนเร่ง / คนรีบ / คนรู้ | 44 / 38 / 37 | **Problem.** Three look-alike labels for three counterparties; เร่ง and รีบ are near-synonyms. |
| ไม้บรรทัด | 33 (5) | Marginal; means "mean + SD". |
| วันล็อก / ค่าดึง / โซ่ | 30 / 26 / 13 | **Overhead**: a second vocabulary for expiry / funding / dated futures, learned alongside the English and the Thai gloss. |
| รอบชดเชย | 26 (4) | Marginal; defined by formula (part2 L88). |
| บัตรตลาด / บัตรธรรมชาติ / บัตร 8 ช่อง | 19 / 10 / 4 | Three "cards". |
| มือที่แย่งเชือก | 18 (6) | Overhead; equals Crowding, which is also taught. |
| แถบผล | 14 (7) | Marginal. |
| n = 1 | 14 (13) | Keep the idea; say "ตัวอย่างเดียว". |
| มือหลุด, ใบแกน, ด่าน, กฎทอง, สองกระเป๋า, แว่นขยาย ×100, สี่คำถาม, สมุดห้าช่อง, ทางด่วน | 2–17 each | Mostly overhead; several are used once or twice. |
| nq | 72 (19) | **Overhead.** A beginner is told about another book in every chapter head. |
| ของมิน / สาธิต (two-scale convention) | 165 / 37 | **Overhead.** Part 1 tables are at 1 BTC while Min trades 0.01 BTC, so numbers appear twice (part4 L37 "11,220 … (ของมินจริงคือ 112.20)"). |

For a term like funding the reader of chapter 0 must hold: "funding", "Funding Rate", "อัตราค่าธรรมเนียมการถือสถานะ · สัญญา Perpetual", and "ค่าดึง" (part0 L106).

### 4.3 Against the example's device set

The example asks the reader to learn three labels ("อ่านภาพ", "อ่านสมการ", "พักตรงนี้ได้") and a code scheme. It coins almost no words: "ชุด", "ระดับอ้างอิง", "ความห่าง" are ordinary Thai. Ours asks for about 22 box types, 36 emoji, about 25 coined words, three reading paths, two number scales and an 8-slot card. Each of ours has a reason in the plan; together they cost a beginner more attention than the stat arb content does. The example's weakness is the mirror image: with no summaries, no boxes and no figures in its second half, it gives the eye nowhere to rest.

---

## 5. Exercises

### 5.1 The two systems (`exer.py`)

| | Example | Ours |
|---|---|---|
| Items | 4 (foundation) + 10 (P1–P10) + 16 (Q1–Q16, inside lessons) + 15 (PX1–PX15) = 45 | 57 = 3 per chapter (คำนวณ 19, ตัดสินใจ 19, ถ่ายโอน 19) |
| Where | Q at the end of each lesson; P and PX at the back | ✍️ box in each chapter; appendix D |
| Item length (median) | 406–498 chars, multi-part | 155 chars |
| Hints | two levels for P; one starter per PX; grouped for Q | none ("คำใบ้" occurs 0 times) |
| Solution length (median) | 535–716 chars, prose with reasons | 209 chars, arithmetic separated by "·" |
| Back-matter size | 66,727 chars | appendix D + answers repeat the chapter text |
| Condition-variation set | PX1–PX15, one per tool/case | the (ถ่ายโอน) item |
| Cumulative / capstone | P10 (new h = 3 from scratch), hand-off report, self-assessment ladder | ใบ 18 verdict sheet |
| Inline prediction prompts | none | 37 🛑 |

All 57 items of our appendix D are verbatim copies of the chapter ✍️ items (57 of 57 matched), and appendix "answers" repeats the folded answers. The appendix adds no practice.

### 5.2 One chain from the example, in full

Exercise: "กำหนดให้ h คงที่ และ x = A − hB หากถือ long A หนึ่งหน่วยกับ short B จำนวน h หน่วย กำไรจากราคาเท่ากับการเปลี่ยนของ x คราวนี้กลับจำนวนเป็น short A หนึ่งหน่วยกับ long B จำนวน h หน่วย จงหาว่ากำไรสัมพันธ์กับการเปลี่ยนของ x อย่างไร โดยเริ่มคำนวณจากแต่ละขา" (EX L4148).

Hint: "P1 หรือ A1 ระดับ 1 ลองคิดกำไรของขา short A และขา long B แยกกันก่อน ระดับ 2 นำ −ΔA + hΔB ไปเทียบกับ Δx แล้วแยกการคำนวณเมื่อราคาขยับออกจากการคาดว่าราคาจะขยับจริงหรือไม่" (EX L4977).

Solution (first of four paragraphs): "ใช้เหตุการณ์สั้นใน A.2 ตรวจเครื่องหมายได้ก่อน: short A ที่ 208 แล้วซื้อคืน 206 ได้ +2 และ long B สองหน่วยที่ 100 แล้วขาย 101 ได้อีก +2 รวมกำไรจากราคา +4 ส่วน x เปลี่ยนจาก 8 เป็น 4 หรือ Δx = −4 ดังนั้นกำไรของ short spread จึงเป็น −Δx = +4 ก่อนต้นทุน" (EX L5006), followed by a fresh counter-example the text never showed (ratio falls from 2.08 to 2.075 yet the position loses 1 U, EX L5012).

Solutions also diagnose the likely slip: "หากได้คำตอบราคารวม B เป็น 202 ลองย้อนดูว่าเผลอนำราคาใหม่มาบวกกับราคาเก่าหรือไม่" (EX L672), and the closing self-check routes errors back to sections: "เงินสดผิดมักตามกลับไปที่เครื่องหมายหรือ fill ค่าธรรมเนียมผิดให้ดูว่านับครบทุกขาทั้งเข้าออกหรือไม่" (EX L5103).

### 5.3 The same from ours

Exercise: "(คำนวณ) ถ้าเปิดชุดเดียวกันด้วยทุน 150,000 กติกาเดิม Free Cash หลังเปิดเท่าไร และราคา futures ขึ้นสะสมได้กี่ % ของ 103,000?" (part4 L328).
Answer: "150,000 − 100,000 − 10,300 = 39,700 · ÷ 1.1 = 36,091 · 36,091 ÷ 103,000 ≈ 35.0% กันชนหนากว่ามินเกือบสามเท่า แลกกับเงินอีก 25,000 ที่นอนเฉย" (part4 L332).

The answer is right and ends with an insight, but a reader who got 33% has no way to find where they went wrong.

### 5.4 Which design teaches better

- **Scaffolding: example.** Two-level hints let a stuck reader take one step without seeing the answer; ours is all-or-nothing.
- **Solutions: example.** Reasons, a second method, and wrong-answer diagnosis. Ours has the seed of this in decision items ("คำตอบที่ผิดคือ “equity ยังดีอยู่ ไม่เป็นไร”", part4 L340; "ยั่วใจ" appears 22 times across chapters) but not in calculation items.
- **Variation: example.** PX items change exactly one condition of a worked case and ask why the answer moves (EX L4538). Ours has one transfer item per chapter.
- **Typing and placement: ours.** The (คำนวณ / ตัดสินใจ / ถ่ายโอน) triad is a cleaner design than the example's mixed multi-part items, the answer is one click away in the chapter, and the example's back matter is ordered confusingly (exercises A–C → hints L → solutions L → PX → hints PX → solutions PX → hints A–C → solutions A–C, EX L4134–5000).
- **Prediction during reading: ours.** 37 inline prompts against one global instruction.
- **Practice on the reader's own data: ours for non-coders** (worksheets with "✅ เกณฑ์ผ่าน 3 ข้อ" and Min's filled copy), **example for coders** (guided notebooks with checks, EX L851–857).
- **Capstone: example.** A report skeleton, a worked report to critique (EX L5201), and a self-assessment ladder.

Overall the example's exercise system teaches better because it supports the reader between "stuck" and "answer". Ours has the better skeleton and the better in-text prompts but stops at three terse items per chapter.

---

## 6. Weaknesses of the example as a whole

1. **No story and no stakes.** Assets are "A" and "B", money is an invented unit "U" (EX L813), there is no person, no loss that hurts, no reason to turn the page. "เรา" appears 29 times per 10,000 characters but "we" never want anything.
2. **Length without relief.** 299K characters of teaching in 1,090 paragraphs with a median of 252 characters; no summary boxes, no per-section vocabulary, and the only checkpoint device stops at EX L355.
3. **A difficulty cliff.** The promise of the foundation (13 English words in 36K characters) is broken later: L0–L8 adds 147 new English words; Tools reach `dx = κ(μ − x)dt + σ dW` (EX L3030) and `∂C/∂v` (EX L3344); cases cover PCA, Kalman, copula-scored forecasts and delta-hedged options in 3–5 subsections each.
4. **Figures disappear.** 19 of 30 figures are in the foundation and A–C; Tools and Cases have 3 in 117K characters.
5. **Repetition of the same arithmetic and the same caveats.** "208" occurs 158 times; "fill" 188; "ยังไม่ได้" 71; "ก่อนต้นทุน" 38; "maker" 28 times in a book whose results "ไม่ใช่หลักฐาน maker execution" (EX L7). The caution is correct but is restated rather than taught once.
6. **A coder's book after page 60.** The real-data half needs Python, notebooks and a ZIP of files (EX L1650–1673); a non-coder can only read results.
7. **No margin, liquidation or leverage.** "ยังไม่จำลองเงินประกัน การถูกบังคับปิด หรือคิวจับคู่" (EX L841). For a crypto reader this is the first thing that hurts, and it is where our chapters 1, 3 and 4 are strongest. Funding and basis get one subsection (A.6) and one case.
8. **Exercises far from the text and oddly ordered** (see 5.4); Q items sit in the lessons (Q1 at EX L1792, Q16 at EX L2829) but their hints start at EX L4239 and their solutions at EX L4339, 1,400–2,700 lines away.
9. **A deflating real-data ending without interpretation for a beginner.** Validation has zero entries; the single test position is opened 2024-05-16 and still open at 2025-12-31 (EX L2515–2522). Honest, but the book offers no positive demonstration that the method ever works, and no discussion of why anyone would be paid.
10. **Terminology is not built for carry-over.** English terms appear lower-case and unglossed in running text ("long", "fill", "residual", "holdings"), with one 24-row glossary at the back. Our CLAUDE.md rule produces a better learning record, if applied once per chapter.
11. **Navigation by code only.** No progress markers, no reading-time estimates, no symptom index of the kind our appendix A has.

---

## 7. Recommendations

### P1 — structural, do these first

**P1.1 Add a slow foundation before the current chapter 0, inside Min's story.**
Yes, it is needed: the pacing table shows 7× compression on long/short and two-leg P&L, and 31 English words in the first 12,000 characters against 5. Specification:
- Three or four short units ("คืนก่อนวันที่ 1"), 3,000–4,000 characters each, about 12–15K in total (the example spends 36.6K; we should not).
- Unit a: buy 0.01 BTC, sell it; price per unit vs quantity vs money, with the three-number table of EX L140–148 rebuilt on BTC. Unit b: selling first and buying back, told through a futures position (our reader has no borrow desk; part0 L45 already notes "ในตลาด futures ทำได้เลยโดยไม่ต้องมีเหรียญ"). Unit c: two legs under four futures — both lose, both win, offset, one wins more (EX L217–378 is the model). Unit d: what a dated futures contract is and what expiry forces.
- At most 3 new terms per unit, no coined words until "เชือก" at the very end, no pointers to later chapters, one figure with an explicit reading per unit, 2 exercises with solutions per unit.
- Then current chapter 0 can keep its hook but lose perp, funding and inverse contracts (part0 L106–130), which belong in chapter 7.

**P1.2 Halve the chapter template; double the teaching.**
Target: teaching sections ≥ 65% of chapter characters (now 42%), end matter ≤ 20% (now 48%). Concretely:
- Keep in the chapter: one-line position strip, scene, chapter question, sections, 🛑, 🚶, 🎬, the n = 1 box, one merged summary, exercises, bridge, 📖.
- Merge: 🎯 + สรุป + 🧠 into one "สรุป 3 ข้อ".
- Move out behind one collapsed "แฟ้มของฉัน" block or to the appendices that already hold them: 🛠 worksheet (keep a 3-line teaser and link; appendix E has both versions), 🧮📒 account (show only when it changed), 🧬 card (show the full card only at บท 6, 7, 14, 17), 🔗 links (appendix A L129 already maps them), 🧭 นิสัยคิด (fold into the worksheet's pass criteria).
- Delete: 🔁 box (it duplicates the transfer exercise), ⚠️ box (one line under the table), 🟠 catch-up boxes and the three-path line in every chapter head (keep paths on the index only), 🔩 line.
- Spend the freed 5,000–6,000 characters per chapter on the sections, raising them from about 5,700 to about 10,000 characters, which matches the example's 9,960 per part.

**P1.3 Rewrite calculations at one operation per sentence, money first.**
Rules a reviewer can check: (a) no sentence with more than one "=" in the teaching sections; (b) every result is first reached by following cash and holdings, then compressed into a formula, then checked a second way (EX L929); (c) numbers per 1,000 characters in teaching sections ≤ 20 (now 28.3); (d) convert bullets that carry reasoning into prose (789 list items now). Priority chapters: 0, 3, 4, 9, 11, 12.

**P1.4 Split the overloaded chapters.**
Chapter 9 teaches correlation, simulation design, formation/test periods, the spread X, mean, SD by counting, z, a four-rung rope ladder and the counterparty in 5,659 characters (part9 L41–166). Split into "ไม้บรรทัด" (mean, SD, z on Min's 20 days, about 8K) and "เดินด้วยกัน ≠ มีเชือก" (correlation, simulation, formation/test). Chapter 0 splits per P1.1. Chapter 12 should move its second table and funding adjustment (part12 L91–103, L143) to a follow-on section.

**P1.5 Rebuild the exercise system as a ladder with hints.**
- Per chapter 5 items: (1) ทำตาม — same numbers, blanks to fill; (2) เปลี่ยนเลขหนึ่งตัว; (3) เปลี่ยนเงื่อนไขหนึ่งข้อ (PX style); (4) ตัดสินใจ; (5) ถ่ายโอน.
- Every calculation item gets a two-level hint (level 1: where to start; level 2: one intermediate number, as EX L4978 does) and a solution in sentences with one "ถ้าได้ … แปลว่าพลาดตรง …" line.
- Appendix D stops being a copy: make it the condition-variation set plus three cumulative reviews (after บท 7, 14, 18) that reuse earlier numbers.
- Add the four-step self-assessment ladder (EX L5207–5212) to appendix D and to ใบ 18.

### P2 — reduce load

**P2.1 Cap and stage vocabulary.** At most 5 new terms per chapter (now mean 9.1, max 12; chapter 0 has 17 new glosses). Gloss once per chapter at first use in the sections, never in the 🧭 line, catch-up box, scene and question as well (545 gloss occurrences for 124 terms). Introduce the event before the name, as EX L81 does.

**P2.2 One meaning per symbol; at most 8 emoji.** Fix the three collisions in 4.1: give the reading-path box and the thinking-habit box different marks or drop one; stop using 🟢🔵 for both reader type and link depth; reserve ①–⑧ for the nature card and renumber ใบ 00 rows with plain 1–4. In running text write the slot name, not the digit (part18 L122–128).

**P2.3 Prune coined words.** Keep เชือก, กันชน, ค่าผ่านทาง, คู่ปลอม, ในกรอบ. Replace วันล็อก / ค่าดึง / โซ่ / มือที่แย่งเชือก / ไม้บรรทัด with the glossary terms they shadow, or use them once as an image and then drop them. Rename คนเร่ง / คนรีบ / คนรู้ so the three do not look alike, and introduce them in one table. No more than one new coined word per chapter, and each must appear in 📖 with its standard equivalent.

**P2.4 One money scale.** Remove the "สาธิต 1 BTC / ของมิน ÷ 100" double bookkeeping (165 "ของมิน" mentions, two-column account tables). Use one size for the whole of Part 1 and say so once.

**P2.5 Make the book stand alone.** Remove "nq" from chapter heads and scenes (72 mentions); keep cross-book links in appendix A only.

**P2.6 Adopt and standardise three reading aids.** "อ่านภาพ:" after every figure (replace fact-list captions such as part4 L88); numeric substitution after every formula in addition to 🚶 before it; a one-sentence "พักตรงนี้ได้" after every section — the example dropped this after EX L355, so doing it consistently is a visible improvement over it.

**P2.7 Replace 106 provenance tags with one table.** Put an "evidence type → what it can tell → what it cannot" table (model: EX L777–782) in the index and in chapter 9; keep a small tag only on 🎲 simulation results.

### P3 — additions that make ours clearly better, not a copy

**P3.1 One real-data walk-through without code.** The example's real-data pipeline is its strongest claim to seriousness and ours has none (index L161). Use the 8-tab workbook to walk a real pair through formation/test with frozen rules, and report the result honestly even if it is null (EX L2515–2522 shows how). "Real data, no Python" is something the example cannot offer.

**P3.2 A written capstone.** Turn ใบ 18 into a six-row report skeleton (question, data, variables and rules, account, evaluation, conclusion; EX L5192–5199) with Min's completed report to critique, and state the example's success criterion in our words: not taking the trade is a valid result (we already say it, part18 L142).

**P3.3 An artefact map on the index.** A table "บท → ใบงาน → ใช้ต่อในบทไหน" modelled on EX L1679–1688. We already have the artefacts; the example only has the table.

**P3.4 Protect what the example lacks.** Do not dilute: the scene-question-cliffhanger frame; number-bearing headings; margin, liquidation and cash buffer (บท 1, 3, 4); "who pays" and crowding (บท 2, 5, 17); EV and break-even win rate (บท 2, 12, 18); the n = 1 boxes with re-seeded ranges; the symptom index; the interactive tools.

**P3.5 Do not import the example's faults.** No SDE or partial-derivative material in the main path; no back-of-book hint/solution maze (keep answers folded next to the question); no 300-character paragraphs without a table, figure or checkpoint every 1,500 characters; no anonymous A/B/U world.

### Proposed chapter template (replaces the 23-box sequence)

1. Position strip, one line: part · chapter n/N · "ต้องรู้จากบทก่อน: …" (3 items with their numbers).
2. Scene of Min (≤ 150 words) and the chapter question.
3. Three to five steps. Each step: situation → follow the money sentence by sentence → table → name the term → 🛑 predict → figure with "อ่านภาพ" → formula with 🚶 before and numbers after → "พักตรงนี้ได้".
4. One 🎬 or n = 1 box where the chapter has one.
5. สรุป 3 ข้อ.
6. ✍️ five graded items, each with folded hint(s) and folded solution.
7. Bridge question.
8. 📖 ≤ 5 terms.
9. One collapsed block "แฟ้มของฉัน": worksheet link, account line, card slot filled in this chapter, deeper reading.

---

## Appendix: reproducibility

- `scripts/measure.py` — table 3.1, 3.2 and first-unit comparison.
- `scripts/measure2.py` — chapter composition, gloss counts, coined-word counts, voice.
- `scripts/exparts.py` — example per-part profile and device positions.
- `scripts/exer.py` — exercise counts, lengths, duplication check.
- `scripts/pace.py` — matched-concept pacing.
- `scripts/ourdev.py`, `scripts/exdev.py` — box, label and emoji inventories.
- `scripts/exends.py`, `scripts/ourends.py` — opening and closing paragraphs of every part / chapter.
- `scripts/v.py` — character-limited line viewer used for the quoted passages.
