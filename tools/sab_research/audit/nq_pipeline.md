# บันทึกถอด "เครื่องมือและวิธีทำเดิม" ของเล่ม คิดแบบ Quant (nq) — เพื่อใช้ซ้ำกับเล่ม stat arb มือใหม่

> ขอบเขต: อ่านอย่างเดียว ไม่แก้ไฟล์ในคลัง · ทุกข้อในบันทึกนี้อ้างจากไฟล์/คำสั่งที่รันจริงใน `/home/user/Claude-code-project` (วันที่ตรวจ 2026-11-12)
> ข้อใดที่ "อนุมาน" จะเขียนกำกับว่า *อนุมาน* ชัด ๆ · ข้อเสนอแยกไว้ในหัวข้อสุดท้าย

---

## 0. ข้อเท็จจริงที่ต้องรู้ก่อนวางแผน (สรุปหัวข้อ)

1. **สกิล `knowledge-book` ไม่ได้บันทึกสายพาน nq เลย** — `SKILL.md` และ `references/*.md` ไม่มีคำว่า `nq` สักครั้ง สกิลอธิบายแนวทาง "การ์ด 9 องค์ประกอบ" ของเล่ม theory/pillars ส่วน "เครื่องมือเดิม" ของเล่ม คิดแบบ Quant อยู่ที่ `tools/nq_*.py` เท่านั้น
2. **เล่ม nq ไม่ใช้การ์ดเลย** — ใน `nq-part*.html` มี `class="card"` = 0, `📚 Papers` = 0, `✅ ใช้ได้เมื่อไร`/`❌ พังเมื่อไร` = 0, `★★★` = 0 · ใช้ "กายวิภาคของบท" อีกแบบ (ข้อ 2)
3. **เล่ม nq ถูกสร้างในอีก repo** (`options-data`) แล้วย้ายเข้ามาทีเดียวใน commit `6c61340` (2026-09-01) · ประวัติการเขียน/รีวิวรายบทของ nq และเอกสารแผนที่นิยาม W1–W11 / "กฎเหล็ก" **ไม่อยู่ใน repo นี้** (commit อ้างถึง `options-data/docs/next-phase-plan.md`)
4. **ข้อมูลดิบ `data/` ไม่มีในสภาพแวดล้อมนี้** — `nq_figures.py --check` จบด้วย "ไม่พบโฟลเดอร์ข้อมูล: …/../options-data/data" · สคริปต์ที่อ่านแค่ JSON (charts/check/qa/glossary/drills) ยังรันได้
5. **สายพานยังทำงานได้จริงในสภาพแวดล้อมนี้** (ทดสอบบนสำเนาใน scratchpad): `nq_qa.py` ผ่าน 20 ไฟล์ · `nq_check_figures.py` ผ่าน 17 ค่า · `nq_glossary.py`/`nq_drills.py`/`nq_charts.py` ให้ผลตรงกับไฟล์ที่ commit ไว้ byte-for-byte · `render-pdf.mjs` ออก PDF ได้ (nq-part5 = 10 หน้า A4, ฝังฟอนต์ Sarabun)
6. **prefix `statarb-` ถูกใช้แล้ว 2 ทาง** — บทเสริม 5 ไฟล์ในคลัง (`statarb-copula-practice` ฯลฯ) และซีรีส์ภายนอก `statarb-ch0..ch21` ที่ภาคผนวก A อ้างถึง (ไม่มีไฟล์ในคลังนี้) · เล่มใหม่ไม่ควรใช้ `statarb-`
7. **ต้นฉบับ Markdown ของเล่ม stat arb ไม่อยู่ใน repo นี้** — `git ls-files '*.md'` มีแค่ไฟล์สกิล 5 ไฟล์ + `docs/pdf/README.md` + แผน 2 ไฟล์

---

## 1. สายพานผลิตทีละขั้น พร้อมคำสั่งจริง

### 1.1 ภาพรวมการไหล

```
ข้อมูลดิบ (data/deribit|okx/YYYY/MM/YYYY-MM-DD.csv)
   │  python3 tools/nq_figures.py [--data-dir DIR | NQ_DATA_DIR=DIR]   ← ขั้น 1 ตัวเลข
   ▼
docs/nq-figures.json  ("ห้ามแก้ด้วยมือ")
   │  python3 tools/nq_new_part.py <slug> "<sub>" "<desc>" "<title suffix>" > skeleton.html   ← ขั้น 2 เปลือกบท
   │  (เขียนเนื้อบท แทน <!--BODY--> · วางตัวคั่น <!--CHART:key--><!--/CHART:key--> ตรงที่จะมีกราฟ)
   │  python3 tools/nq_charts.py          ← ขั้น 3 เติม SVG ระหว่างตัวคั่น (รันซ้ำได้)
   │  python3 tools/nq_check_figures.py   ← ขั้น 4 ตรวจเลข (W7)
   │  python3 tools/nq_qa.py              ← ขั้น 5 โครงสร้าง/กล่องบังคับ/ลิงก์/เพดานศัพท์ (W8 W9 W11)
   │  python3 tools/nq_glossary.py        ← ขั้น 6 ภาคผนวก B จากกล่อง 📖 ทุกบท
   │  python3 tools/nq_drills.py          ← ขั้น 6 ภาคผนวก D จากกล่อง ✍️ ทุกบท
   │  (ตรวจเรนเดอร์ Playwright 1000px / 420px — ทำแบบ ad hoc ไม่มีสคริปต์ใน repo)
   ▼
node .claude/skills/knowledge-book/scripts/render-pdf.mjs docs nq-index nq-part0 …   ← ขั้น 7 PDF
```

ลำดับที่ปลอดภัย (*อนุมาน* จากการพึ่งพากันของสคริปต์): figures → charts → check_figures → qa → glossary/drills → qa อีกรอบ (เพราะ qa สแกนภาคผนวกด้วย) → PDF

### 1.2 ตารางสคริปต์ทั้งหมด

| สคริปต์ | หน้าที่ | อ่าน | เขียน | พึ่ง data/? | พึ่งไลบรารี |
|---|---|---|---|---|---|
| `tools/nq_figures.py` | คำนวณตัวเลขทุกตัวของเล่ม · มี `--check` (เทียบกับไฟล์เดิม ไม่เขียน "ใช้ใน CI") | `data/deribit`, `data/okx` | `docs/nq-figures.json` (~27 KB, 21 คีย์บนสุด) | **ใช่** | stdlib ล้วน (`random`, `statistics`, `csv`) |
| `tools/nq_new_part.py` | สร้างเปลือกบทใหม่: คัด `<head>`+CSS และ Thai line-break script จาก `nq-part1.html` ใส่ cover + `<!--BODY-->` | `docs/nq-part1.html` | stdout | ไม่ | stdlib |
| `tools/nq_charts.py` | สร้าง inline SVG 9 แบบจาก JSON แล้วเขียนทับเฉพาะระหว่าง `<!--CHART:key-->…<!--/CHART:key-->` | `docs/nq-figures.json` + `docs/nq-*.html` | แก้ไฟล์ `nq-*.html` ในที่ | ไม่ | stdlib |
| `tools/nq_check_figures.py` | (1) ค่าบังคับ 17 ค่าต้องปรากฏในบท (2) เตือนเลข `\d+\.\d+%` ที่ไม่มีใน JSON | JSON + `nq-*.html` | stdout, exit 1 ถ้าพัง | ไม่ | stdlib |
| `tools/nq_qa.py` | tag balance + `<br>` ปลอม + มี Thai script + กล่องบังคับ (เฉพาะ `nq-part\d+`) + ลิงก์ `href="*.html"` มีจริง + ศัพท์ ≤ 12 | `docs/nq-*.html` | stdout, exit 1 | ไม่ | stdlib (`html.parser`) |
| `tools/nq_glossary.py` | ภาคผนวก B: ดึงกล่อง "📖 ศัพท์ใหม่ในตอนนี้" ทุกบท แยกชั้น 1 (3 คำต้องจำ) / ชั้น 2 (ที่เหลือ) | `nq-part*.html` | `docs/nq-appendix-glossary.html` (ตอนนี้ 53 คำ: 27/26) | ไม่ | stdlib |
| `tools/nq_drills.py` | ภาคผนวก D: ดึง `<ol>` ในกล่อง "✍️ ลองทำเอง" ทุกบท + เกณฑ์ "Monday-Morning Test" | `nq-part*.html` | `docs/nq-appendix-drills.html` (30 ข้อ/10 บท) | ไม่ | stdlib |
| `tools/copula_figures.py` | บทเสริม copula: fit Gaussian/t/Clayton/Gumbel + bootstrap + MI vs z | data/ | `docs/copula-figures.json` | ใช่ | **numpy + scipy** |
| `tools/blending_figures.py` | บทเสริมรวมสัญญาณ: ค้นหา 114 วิธีรวมตัวกรอง + 300 รอบป้ายสลับสุ่ม | data/ | `docs/blending-figures.json` | ใช่ | **numpy + scipy** |
| `tools/live_backtest_figures.py` | บทเสริม live vs backtest: สภาพคล่องทั้งกระดาน · ต้นทุนซ่อนจาก mid · กระทบยอด 1 ไม้ · งบ tracking error | data/ + `nq-figures.json` | `docs/live-backtest-figures.json` | ใช่ | stdlib |
| `tools/alpha_decay_figures.py` | บทเสริม edge เสื่อม: power calculation n=(zα+zβ)²p0(1−p0)/(p0−p1)² | — (สูตรล้วน) | `docs/alpha-decay-figures.json` | **ไม่** | stdlib |
| `tools/data_health.py` | เครื่องมืออิสระตรวจสุขภาพข้อมูล 4 เรื่อง · ถ้าไม่ระบุ `--data-dir` จะเขียน JSON ด้วย | data/ | `docs/data-quality-figures.json` | ใช่ | stdlib |
| `.claude/skills/knowledge-book/scripts/render-pdf.mjs` | HTML → PDF (A4, printBackground, รอ fonts + 400ms ให้ `<wbr>` นิ่ง) รับ `[dir] [names…]` | `docs/*.html` | `docs/pdf/<name>.pdf` | ไม่ | Playwright (global `/opt/node22/lib/node_modules/playwright`, Chromium ที่ `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`) |
| `docs/pdf/render-pdf.mjs` | รุ่นเก่า: **hardcode 14 ไฟล์** (index, notation, theory-*, pillars-*) | — | `docs/pdf/` | ไม่ | Playwright |
| `generate-pdf.js` (root) | รุ่นเก่าของ Payoff Mastery: header "Payoff Mastery — …" + เลขหน้า, PDF วางข้าง HTML | ไฟล์ที่ระบุ | `<file>.pdf` | ไม่ | Playwright |

`.gitignore` ใน `docs/pdf/` ตัด `*.pdf` ทิ้ง (PDF ไม่ถูก commit)

### 1.3 ผูกชื่อ "nq" ตายตัวตรงไหน และต้องทำอะไรเพื่อใช้กับเล่มใหม่

| สคริปต์ | จุดที่ผูก nq / ผูกเนื้อหาเล่มเดิม (อ้างบรรทัดในไฟล์) | ต้องทำอะไร |
|---|---|---|
| `nq_new_part.py` | `SOURCE = docs/nq-part1.html` · `<title>คิดแบบ Quant — {suffix}</title>` · `<h1>คิดแบบ Quant</h1>` · อาร์กิวเมนต์ `slug` ไม่ได้ใช้ · docstring บอก 3 อาร์กิวเมนต์ แต่โค้ดบังคับ 4 (`len(sys.argv) != 5`) | ทำพารามิเตอร์ `--source`, `--book-title` · แก้ docstring · ถ้าเล่มใหม่เพิ่ม CSS class ใหม่ ต้องมีบทต้นแบบของเล่มใหม่เป็น SOURCE (ไม่งั้นทุกบทได้ CSS ของ nq) |
| `nq_figures.py` | `OUT = docs/nq-figures.json` · `DATA_DIR`/`NQ_DATA_DIR` · `MIN_ACCOUNT` · ทุก study ผูก BTC/Deribit/OKX + วันที่ตายตัว (`2026-08-29`, `2026-09-25`, `2026-08-20`, `2026-07-31`, `2026-08-01`) · `SEED = 20260830` | **เขียนใหม่ทั้งไฟล์** สำหรับข้อมูลจำลอง (ไม่ต้องมี DATA_DIR) · คัดลอกเฉพาะ "โครง": dict ภาษาไทย, `_อ่านก่อน`, `--check`, `json.dump(ensure_ascii=False, indent=2)` + newline ท้ายไฟล์ |
| `nq_charts.py` | อ่าน `docs/nq-figures.json` · สแกนเฉพาะไฟล์ `startswith("nq-")` · `CHARTS` 9 ฟังก์ชันผูกคีย์ JSON ของ nq · id ใน `<defs>` ขึ้นต้น `nq` (`nqArea`, `nqPx`, `nqAr`, `nqCap`) · ข้อความ caption บางอันฝัง "56 วัน" ตายตัว | คงไว้: กลไก marker + `_wrap()` (`<svg class="fig" viewBox role="img" aria-label>` + `<div class="cap">`) + palette/ฟอนต์ · เปลี่ยน: prefix ไฟล์, ไฟล์ JSON, ฟังก์ชันกราฟใหม่ทั้งหมด, prefix id ใน defs (กัน id ชนเมื่อหลายกราฟอยู่หน้าเดียว) |
| `nq_check_figures.py` | `FIG = docs/nq-figures.json` · `REQUIRED` 17 lambda ผูก path JSON ของ nq (`btc`, `มิน`, `ต้นทุนจริง`, …) · สแกน `startswith("nq-")` · ชุด `allowed` ของเลขที่ยกเว้น | ทำ REQUIRED เป็นของเล่มใหม่ · prefix/JSON เป็นพารามิเตอร์ · **ข้อจำกัด**: ตรวจเฉพาะทศนิยมตามด้วย `%` — เลขจำนวนเต็ม, `1,067 ไม้`, ค่า 0.141 (ไม่มี %) ไม่ถูกตรวจ |
| `nq_qa.py` | `glob("nq-*.html")` · `is_chapter = r"nq-part\d+\.html$"` · `REQUIRED_BOXES` / `CHAPTER_BOXES` (ข้อความ emoji ตายตัว) · `TERM_CAP = 12` | prefix เป็นพารามิเตอร์ · ปรับรายการกล่องบังคับถ้าเล่มใหม่มีกล่องใหม่ · **ข้อจำกัด**: ตรวจแค่ "มีสตริงนี้ในไฟล์" (ไม่ตรวจลำดับ/จำนวน) · ตรวจลิงก์เฉพาะ `href` ไม่ตรวจ `<code>ชื่อไฟล์</code>` |
| `nq_glossary.py` | `glob("nq-part*.html")` · shell จาก `nq-part1.html` · title "คิดแบบ Quant — ภาคผนวก B" · ลิงก์ `nq-part{N}.html` · output `nq-appendix-glossary.html` · `TITLES` (ไม่ได้ใช้จริงในโค้ด) · regex พึ่ง markup เป๊ะ: `<strong>3 คำที่ต้องจำก่อน</strong></p>\s*<ul>` และ `<strong>ที่เหลือ</strong>` คั่นด้วย ` · ` และ ` = ` | คัดลอก+พารามิเตอร์ prefix/title/ชื่อภาคผนวก · **ต้องเขียนกล่อง 📖 ตาม markup เดียวกันเป๊ะ** ไม่งั้นดึงไม่ได้ |
| `nq_drills.py` | เหมือน glossary + `TITLES` ชื่อบท nq 10 บท (ใช้เป็น `<h2>`) + ข้อความ "Monday-Morning Test ฉบับ non-quant" 6 ข้อที่เขียนเฉพาะเล่ม nq · regex `✍️ ลองทำเอง[^<]*</div>\s*<ol>` | คัดลอก · ย้าย TITLES และเกณฑ์สำเร็จเป็น config ของเล่มใหม่ · กล่อง ✍️ ต้องเป็น `<ol>` ตรงหลัง `</div>` ของหัวกล่อง |
| `copula/blending/live_backtest/data_health` | `DATA_DIR`/`NQ_DATA_DIR` · คอลัมน์ CSV ของคลัง (underlying, underlying_price, bid, ask, strike, expiry, type, mark_price, volume_24h, instrument) · `live_backtest` อ่าน `nq-figures.json` | ใช้เป็น *ตัวอย่างวิธีคิด* ได้ (เช่น search-vs-shuffled-label ของ blending) แต่รันไม่ได้ที่นี่ (ไม่มี data/ และไม่มี scipy) |
| `alpha_decay_figures.py` | `TRADES_PER_WEEK = 2` คัดลอกมือจาก `MIN_ACCOUNT` (ไม่ได้ import) | เป็น **ต้นแบบที่ใกล้เล่มใหม่ที่สุด**: สคริปต์ตัวเลขที่ไม่พึ่งข้อมูลตลาด รันได้ทุกที่ |

### 1.4 ผลทดสอบสายพานในสภาพแวดล้อมนี้ (รันจริง ไม่แตะคลัง — ทำบนสำเนาใน scratchpad)

| คำสั่ง | ผล |
|---|---|
| `python3 tools/nq_qa.py` (ในคลังจริง อ่านอย่างเดียว) | `ตรวจ 20 ไฟล์ · ผ่านทุกข้อ ✓` |
| `python3 tools/nq_check_figures.py` (อ่านอย่างเดียว) | `ตรวจ 20 ไฟล์ · ตัวเลขบังคับ 17 ค่า · ตรงกับ nq-figures.json ทั้งหมด ✓` |
| `python3 tools/nq_figures.py --check` | `ไม่พบโฟลเดอร์ข้อมูล: …/../options-data/data` (ไม่มี data/) |
| `nq_glossary.py` / `nq_drills.py` / `nq_charts.py` บนสำเนา | ผลตรงกับไฟล์ใน repo ทุกไฟล์ (`cmp` SAME 10 ไฟล์) → สายพาน idempotent · หมายเหตุ: `nq_charts.py` พิมพ์ "ไม่มีไฟล์ไหนมีตัวคั่น <!--CHART:ชื่อ--> ให้เขียน" ทั้งที่มี marker — ข้อความนี้ออกเมื่อ "ไม่มีไฟล์ไหนเปลี่ยน" (`written == 0`) ชวนเข้าใจผิด |
| `nq_new_part.py part10 "…" "…" "Part 10: ทดสอบ"` | ได้เปลือก 6,200 bytes มี `<!--BODY-->` + Thai script |
| `node .claude/skills/knowledge-book/scripts/render-pdf.mjs <copy>/docs nq-part5` | `ok nq-part5` · 10 หน้า A4 · `pdffonts`: Sarabun ExtraBold/SemiBold/Regular ฝังครบ (โหลดจาก Google Fonts ผ่าน proxy ได้) |
| Python / ไลบรารี | Python 3.13.18 · numpy 2.5.3 มี · **scipy ไม่มี** · node `/opt/node22/bin/node` · Playwright ใช้ได้ · `pdftotext`/`pdffonts` มี |

### 1.5 prefix ใหม่ที่ไม่ชนของเดิม

prefix ที่มีอยู่ใน `docs/` ตอนนี้ (นับไฟล์): `arb`21 · `eye`11 · `math`20 · `nq`21 · `pillars`10 · `pm`27 · `statarb`5 · `theory`15 · `tool`5 · `tools`1 · `payoff`2 · `quant`2 · `case` `copula` `blending` `alpha` `live` `data` `index` `notation` `all` `everything` อย่างละ 1 · อ้างถึงแต่ไม่มีไฟล์: `ob-` `vol-` `vp-` `playground-` `python-` `practice-` `grid-` `statarb-ch*`

| ตัวเลือก | ชนไหม | หมายเหตุ |
|---|---|---|
| **`sab-`** (stat arb beginner) — แนะนำ | ไม่มีไฟล์/ลิงก์ใดขึ้นต้น `sab-` (ตรวจแล้ว) · `glob("sab-*.html")` ไม่กวาดไฟล์อื่น | สคริปต์ `tools/sab_*.py` · JSON `docs/sab-figures.json` · บท `sab-part0..N.html` · ภาคผนวก `sab-appendix-*.html` · เครื่องมือ `sab-tool-*.html` · หน้ารวม `sab-index.html` · runbook `sab-runbook.html` |
| `statarb-` | **ชน** — glob `statarb-*` จะกวาดบทเสริม 5 ไฟล์ และสับสนกับซีรีส์ภายนอก `statarb-ch*` | ไม่ควรใช้ |
| `sa-` | ไม่มีไฟล์ แต่สั้นเกินและมี `id="sa"` ใน JS ของ `tool-diversification.html` (ไม่ชนชื่อไฟล์จริง) | ใช้ได้แต่สื่อความน้อยกว่า |

---

## 2. "กายวิภาคของบท" ในเล่ม คิดแบบ Quant

### 2.1 ลำดับบล็อกจริง (จากการแยกโครงทั้ง 10 บท)

```
cover (.cover: h1 "คิดแบบ Quant" · .sub "Part N — <ชื่อ>: <คำโปรย>" · .desc คำสำคัญคั่น ·)
🧭 เส้นทางอ่าน  (.bx.bb style="font-size:.92em" — 🟢 มือใหม่ / 🔵 มีพื้นแล้ว)
H2 เปิดด้วยฉาก/ปริศนา (มักเป็นมินหน้าจอ หรือคำถามค้างจากบทก่อน = callback)
   .pq ประโยคทอง ภายใน section แรก
H2 × 3–5 เนื้อหา: ร้อยแก้วสั้น + ตาราง .tw + กราฟ (CHART) + กล่องประเด็น .bx.br/.bg + 🧮 + 🧠 .qv
   (บางบท: 📉 เคสพังจริง · [รอบสอง] · 💡 · 📊 หลักฐานจากคลังข้อมูล)
── ชุดปิดบท (ลำดับคงที่เกือบทุกบท) ──
⚠️ ค่าเริ่มต้น (.dft)
🎬 ฉากหน้าจอ (.scene)
🧭 นิสัยคิด (.bx.bp, <ol>)
🧮 ตัวเลขของมิน (.bx.ba)          ← Part 0/1 วางก่อน .dft · Part 2–3, 5–8 วางหลัง 🧭 · Part 4 ไม่มีกล่องนี้
✍️ ลองทำเอง (.bx.bg, <ol> 3 ข้อ)
🎯 3 อย่างที่ต้องจำจาก Part นี้ (.bx.bg, <ul> 3 ข้อ)
สรุป Part N (.bx.bb, <ul>)
.pq สะพาน (สีน้ำเงิน: style="border-left-color:var(--blue);background:var(--blue-bg)") — "คำถามที่ยังค้าง … · Part N+1 ตอบ"
🔗 อยากลึกกว่านี้ (.bx.ba, <ul> อ้าง <code>ไฟล์ในคลัง</code>)
📖 ศัพท์ใหม่ในตอนนี้ (.bx.bb — "3 คำที่ต้องจำก่อน" <ul> + "ที่เหลือ" คั่น ·)
Thai line-break <script> (ห้ามแก้)
```

บทปิดเล่ม (Part 9) ต่าง: ไม่มี "สรุป Part" · `.pq` ปิดเป็นสีเขียว · 🔗 เปลี่ยนเป็น "ไปต่อที่ไหน" · 📖 บอกว่า "Part นี้ไม่มีศัพท์ใหม่ … เปิดภาคผนวก B" · มี 💎 "คำถามที่เปลี่ยนไปตลอดทั้งเล่ม"

### 2.2 กล่องบังคับทุกชนิด — class + HTML จริง (ย่อจากไฟล์)

กล่องที่ `nq_qa.py` บังคับในบท (`nq-part\d+.html`): `🧭 เส้นทางอ่าน` · `class="pq"` · `📖 ศัพท์ใหม่ในตอนนี้` · `class="qv"` · `🎬 ฉากหน้าจอ` · `🧭 นิสัยคิด` · `⚠️ ค่าเริ่มต้น` · `🧮` · `✍️ ลองทำเอง` · `🎯 3 อย่าง` · `🔗`

**🧭 เส้นทางอ่าน** (`nq-part1.html`)
```html
<div class="bx bb" style="font-size:.92em"><div class="bt">🧭 เส้นทางอ่าน</div>
<p><strong>🟢 มือใหม่:</strong> อ่านทั้งหมด Part นี้ไม่มีสมการเลยแม้แต่ตัวเดียว · <strong>🔵 มีพื้นแล้ว:</strong> ตัวเลขทั้งหมดในบทนี้สร้างซ้ำได้ด้วย <code>tools/nq_figures.py</code> …</p></div>
```

**.pq ประโยคทอง** (ม่วง ค่าเริ่มต้น) และ **.pq สะพาน** (น้ำเงิน)
```html
<div class="pq">แพตเทิร์นที่คุณเห็นบนกราฟ ไม่ได้พิสูจน์ว่าตลาดมีความทรงจำ มันพิสูจน์แค่ว่าตลาดขยับ</div>
<div class="pq" style="border-left-color:var(--blue);background:var(--blue-bg)">ถ้าข้อมูลของเราเองจะไม่พอไปอีกสิบปี แล้วเราจะตัดสินใจอะไรได้บ้างวันนี้ · คำตอบเริ่มที่การเขียนความเชื่อออกมาให้มัน <em>ผิดได้</em> — สถานีที่ ① ใน Part 2</div>
```
(บทละ 2–3 `.pq`)

**🎬 ฉากหน้าจอ** — `.scene` (CSS เพิ่มของ nq: พื้นเทา `var(--g0)` กรอบ `var(--g2)`)
```html
<div class="scene"><div class="bt">🎬 ฉากหน้าจอ — มินเจอโพสต์ในกลุ่ม</div>
<p>เช้าวันเสาร์ มีคนโพสต์ในกลุ่มเทรด: <em>"ระบบผมชนะ 17 จาก 22 ไม้เดือนนี้ครับ ใครสนใจทักมา"</em> …</p>
<ol><li><strong>22 ไม้</strong> — อยู่ในโซนที่ต่อให้เก่งจริงก็พิสูจน์ไม่ได้ …</li> …</ol>
<p>มินไม่ได้ตัดสินว่าคนโพสต์โกหก … <strong>ตัวเลขชุดนี้แยกสองกรณีนั้นไม่ออก</strong> …</p></div>
```

**🧭 นิสัยคิด** — `.bx.bp` + `<ol>` (ลำดับคำถาม ไม่ใช่ลำดับเครื่องมือ)
```html
<div class="bx bp"><div class="bt">🧭 นิสัยคิด — สามคำถามต่อทุกตัวเลขที่มีคนยื่นมาให้</div>
<ol>
<li><strong>มาจากกี่ครั้ง</strong> — ตัวเลขที่ไม่มี n มาด้วย ยังไม่ใช่หลักฐาน เป็นแค่เรื่องเล่า</li>
<li><strong>ใครหายไป</strong> — …</li>
<li><strong>ถ้าเป็นดวงล้วน หน้าตาจะต่างจากนี้ยังไง</strong> — …</li>
</ol>
<p>คำถามข้อสามคือข้อที่ทรงพลังที่สุด และเป็นข้อที่แทบไม่มีใครถาม</p></div>
```

**⚠️ ค่าเริ่มต้น** — `.dft` (CSS เพิ่ม: พื้น `#ecfeff` กรอบ `2px solid #06b6d4` หัว `#0e7490`) · มักจบด้วย "ถ้ายังไม่รู้จะเริ่มยังไง/ข้อไหน …"
```html
<div class="dft"><div class="bt">⚠️ ค่าเริ่มต้น — จัดการต้นทุนยังไงตั้งแต่วันนี้</div>
<ul>
<li><strong>วัดค่าผ่านทางของตัวเองก่อนเทรดไม้ถัดไป</strong> — …</li>
<li><strong>หลีกเลี่ยงของที่ใกล้หมดอายุ ถ้าไม่มีเหตุผลเฉพาะเจาะจง</strong> — …</li>
<li><strong>ถ้ายังไม่รู้จะเริ่มยังไง</strong> ให้คำนวณต้นทุนต่อรอบของตัวเองหนึ่งตัวเลข แล้วเขียนแปะไว้ข้างจอ …</li>
</ul></div>
```

**🧮 ตัวเลข / worked example** — `.bx.ba` + `🚶 อ่านเป็นภาษาคนก่อน` + `.fm` เฉพาะสูตร
```html
<div class="bx ba"><div class="bt">🧮 ตัวเลขของมิน</div>
<ul>
<li>ทุน <strong>50,000 บาท</strong> · ค่าธรรมเนียม <strong>0.1% ต่อข้าง</strong> → เข้าและออกครบรอบ = <strong>0.2% ต่อรอบ</strong></li>
<li>อัตราชนะที่ต้องได้เพื่อ <em>แค่เสมอตัว</em> = <strong>55.0%</strong> ไม่ใช่ 50%</li>
</ul>
<p><strong>🚶 อ่านเป็นภาษาคนก่อน:</strong> ถ้ากำไรกับขาดทุนเท่ากัน การชนะครึ่งหนึ่งควรจะเสมอตัวพอดี แต่ทุกไม้ต้องจ่ายค่าผ่านทาง 0.2% ไปก่อน …</p>
<div class="fm">อัตราชนะเสมอตัว = 50% + (ต้นทุนต่อรอบ ÷ 2 ÷ กำไรเป้า) <br>
                = 50% + (0.2 ÷ 2 ÷ 2) = 50% + 5% = 55%</div></div>
```
(ทุกบทมี "🧮 ตัวเลขของมิน" ยกเว้น Part 4 ที่ใช้ 🧮 แบบอื่น · Part 9 ใช้ "🧮 สถานะหลังผ่านไป 19 วัน")

**✍️ ลองทำเอง** — `.bx.bg` + `<ol>` 3 ข้อทุกบท (ไม่มีเฉลย · ข้อสามของ Part 0 ถูก callback ใน Part 9)
```html
<div class="bx bg"><div class="bt">✍️ ลองทำเอง</div>
<ol>
<li>เปิดไม้ล่าสุดที่คุณเทรด แล้วเขียนความเชื่อตอนนั้นเป็นข้อความที่ <em>ผิดได้</em> หนึ่งประโยค — ถ้าเขียนไม่ได้ นั่นคือคำตอบของแบบฝึกหัดนี้</li>
<li>…</li>
<li>… จดวันที่ไว้ เราจะกลับมาดูข้อนี้อีกครั้งที่ Part 9</li>
</ol></div>
```

**🎯 3 อย่างที่ต้องจำ** — `.bx.bg` + `<ul>` 3 ข้อ หัวข้อหนาแล้วตามด้วย `—`
```html
<div class="bx bg"><div class="bt">🎯 3 อย่างที่ต้องจำจาก Part นี้</div>
<ul>
<li><strong>ถามฐานก่อนเสมอ</strong> — สัญญาณจะมีความหมายก็ต่อเมื่อมันดีกว่า "การไม่ทำอะไรเลย"</li>
<li><strong>ตัวเลขทุกตัวมาพร้อมขนาดตัวอย่าง</strong> — 54.5% จาก 11 ครั้ง กับ 54.5% จาก 1,100 ครั้ง เป็นคนละเรื่องกันโดยสิ้นเชิง</li>
<li><strong>อินดิเคเตอร์คือสถานีที่ 3</strong> — …</li>
</ul></div>
```

**🧠 มุมที่มองต่าง** — `.qv` · หัวในเล่มนี้คือ "🧠 มุมที่ quant มองต่าง" · `<br>` เดี่ยวคั่นคู่ (ข้อยกเว้นเดียวของกฎ `<br>`)
```html
<div class="qv"><div class="bt">🧠 มุมที่ quant มองต่าง</div>
<p><strong>คนทั่วไปเห็น:</strong> ตัวเลข 54.5% แล้วถามว่า "สรุปสัญญาณนี้ใช้ได้หรือไม่ได้"<br>
<strong>quant เห็น:</strong> ตัวเลข 54.5% พร้อมกับ n = 11 แล้วถามว่า "ข้อมูลเท่านี้ให้สิทธิ์ฉันพูดอะไรได้บ้าง" — …</p></div>
```
(บทเสริม copula ใช้ "🧠 มุมที่คนใช้จริงมองต่าง" / "คนใช้จริงเห็น")

**🔗 อยากลึกกว่านี้** — `.bx.ba` + `<ul>` + `<code>` (ไม่ใช่ลิงก์)
```html
<div class="bx ba"><div class="bt">🔗 อยากลึกกว่านี้</div>
<ul>
<li>ความน่าจะเป็นและการแจกแจงแบบเต็ม → <code>math-part2</code>, <code>math-part3</code></li>
<li>อยากรันการจำลองในบทนี้เอง → <code>tools/nq_figures.py</code> ในคลังนี้ ตัวเลขทุกตัวสร้างซ้ำได้</li>
</ul></div>
```

**📖 ศัพท์ใหม่ในตอนนี้** — `.bx.bb` · markup นี้คือ "สัญญา" กับ `nq_glossary.py` และ `nq_qa.py` (เปลี่ยนไม่ได้)
```html
<div class="bx bb"><div class="bt">📖 ศัพท์ใหม่ในตอนนี้</div>
<p><strong>3 คำที่ต้องจำก่อน</strong></p>
<ul>
<li><strong>ฐาน (base rate)</strong> = อัตราการเกิดตามปกติ เมื่อยังไม่ใส่เงื่อนไขอะไรเลย</li>
<li><strong>ขนาดตัวอย่าง (n)</strong> = …</li>
<li><strong>เส้นเสมอตัว</strong> = …</li>
</ul>
<p><strong>ที่เหลือ</strong> · <strong>ข้อความที่ผิดได้</strong> = … · <strong>ส่วนต่างราคาซื้อ-ขาย</strong> = … · <strong>สายการผลิต 8 สถานี</strong> = โครงของหนังสือเล่มนี้</p></div>
```
(regex ของ glossary ต้องการ `</div>` ปิดกล่องตามด้วย `<!--` หรือจบไฟล์ — กล่อง 📖 จึงต้องเป็นกล่องสุดท้ายก่อนคอมเมนต์ Thai script)

**กล่องเสริมที่ไม่บังคับ แต่ใช้จริง**
- `📉 ตอนนี้พังจริงแบบไหน — เคส…` (`.bx.ba` ใน Part 0, `.bx.br` ใน Part 3)
- `🔵 [รอบสอง] แล้วสูตร Kelly ล่ะ` (`.bx.bb` ใน Part 7 · reading path บอกว่า "กล่อง [รอบสอง] ท้ายบท")
- `💡 ทำไมเรื่องนี้ต้องอยู่ใน Part 0 …` (`.bx.bb`) · `📊 หลักฐานจากคลังข้อมูลของเราเอง` (`.bx.bb`) · `💎 …` (Part 8, 9)
- กล่องประเด็นสั้นหัวเป็นตัวเลข/ข้อสรุป เช่น `<div class="bx br"><div class="bt">รอบสอง: ชนะเฉลี่ย 10.0 จาก 20 ไม้</div>` — ใช้เป็น "beat" ของเรื่อง
- `.ad` (ข้อดี/ข้อเสีย 2 คอลัมน์) ใช้ครั้งเดียวใน Part 3
- `<abbr title="…">` tooltip ใช้น้อย (Part 0:1 · 1:3 · 4:1 · ที่เหลือ 0) — ศัพท์ใช้วิธี "ไทยในวงเล็บครั้งแรก" เป็นหลัก

**กราฟ** (ผลจาก `nq_charts.py._wrap`)
```html
<!--CHART:sample-size-->
<svg class="fig" viewBox="0 0 760 312" role="img" aria-label="กราฟแสดงว่าคนที่มี edge จริง 55% … ที่ 100 ไม้ได้แค่ 13.3% ที่ 1000 ไม้ได้ 88.1%">…</svg>
<div class="cap">จำลอง 20,000 รอบต่อจุด · เส้นน้ำเงินคือคนที่เก่งจริง เส้นแดงคือคนที่ไม่มีฝีมือเลย — …</div>
<!--/CHART:sample-size-->
```

### 2.3 CSS ที่ nq เพิ่มจาก `assets/template.html` (เทียบกฎต่อกฎ)

```css
.dft { background:#ecfeff;border:2px solid #06b6d4;border-radius:10px;padding:14px 20px;margin:18px 0 }
.dft .bt { color:#0e7490 }
.scene { background:var(--g0);border:1px solid var(--g2);border-radius:10px;padding:16px 20px;margin:18px 0 }
.scene .bt { color:var(--g9) }
.fig { display:block;margin:22px auto;width:100%;height:auto }
.cap { text-align:center;font-size:.87em;color:#64748b;margin:-12px 0 20px }
@media print { … .bx,table,.card,.ad,.qv,.dft,.scene{page-break-inside:avoid} … }
```
หน้าเครื่องมือเพิ่ม `.tool .ctrl .btn .out .big .row .guess` (slider + JS vanilla ฝังในหน้า)

### 2.4 ขนาด/ความหนาแน่นจริงต่อบท

| บท | คำไทย (Intl.Segmenter, ไม่นับ SVG) | ขนาดไฟล์ (bytes) | กล่อง | ตาราง | SVG | CHART marker | ศัพท์ใหม่ | ✍️ |
|---|---|---|---|---|---|---|---|---|
| Part 0 | 2,656 | 27,095 | 19 | 2 | 2 (วาดมือ) | 0 | 6 | 3 |
| Part 1 | 2,768 | 29,679 | 19 | 1 | 2 | 2 | 7 | 3 |
| Part 2 | 2,393 | 21,632 | 19 | 4 | 1 (วาดมือ) | 0 | 5 | 3 |
| Part 3 | 2,718 | 25,743 | 19 | 3 | 1 | 1 | 6 | 3 |
| Part 4 | 2,206 | 22,811 | 17 | 2 | 1 | 1 | 6 | 3 |
| Part 5 | 2,211 | 23,103 | 19 | 2 | 1 | 1 | 6 | 3 |
| Part 6 | 2,061 | 21,369 | 19 | 2 | 1 | 1 | 6 | 3 |
| Part 7 | 2,437 | 24,357 | 18 | 3 | 1 | 1 | 5 | 3 |
| Part 8 | 2,291 | 21,152 | 17 | 1 | 1 | 1 | 6 | 3 |
| Part 9 | 2,179 | 21,687 | 18 | 2 | 1 | 1 | 0 | 3 |

สรุป: **~2,000–2,800 คำไทยต่อบท** (ราว 7,000–9,500 อักษรไทย) · **ไฟล์ 21–30 KB** (CSS ~4.5 KB) · **17–19 กล่อง** · **1–2 กราฟ** · **5–7 ศัพท์ใหม่** (เพดานในสคริปต์ 12 — ใช้จริงต่ำกว่าครึ่ง) · ✍️ **3 ข้อทุกบท** · 🚶 0–2 ครั้ง · `.fm` 0–2 กล่อง (Part 1 ประกาศว่า "ไม่มีสมการเลย") · PDF ≈ 10 หน้า A4 (วัดจาก Part 5) · หน้ารวม ~756 คำ · runbook ~676 คำ
เทียบบทเสริม statarb: 1,327–2,562 คำ · 8–16 กล่อง · 1 กราฟ

### 2.5 ความต่างจากมาตรฐานในสกิล (สำคัญต่อการวางแผน)

| สกิล `knowledge-book` (theory/pillars) | เล่ม nq |
|---|---|
| หน่วย = การ์ด `.card` 9 องค์ประกอบ (Thesis/❓/🔧/✅/❌/⚖️/🧠/📍/📚) + ป้าย ★ / `.yr` | ไม่มีการ์ด · หน่วย = section ที่เปิดด้วยฉาก/ปริศนา แล้วปิดบทด้วยชุดกล่อง "ใช้เป็น" |
| 📚 Papers + 📖 อ่านต่อ | ไม่มี · แทนด้วย 🔗 อยากลึกกว่านี้ (ชี้เล่มในคลัง) |
| ไม่มีกฎตัวเลขจากไฟล์กลาง | ตัวเลขทุกตัวจาก `nq-figures.json` + ตัวตรวจ |
| ไม่มี `.dft` `.scene` | `.dft` `.scene` เป็นกล่องบังคับ |
| กฎร่วมที่ยังใช้: Thai line-break script · `<ul>/<ol>` ไม่ใช่ `<br>` ปลอม · `.fm` เฉพาะสูตร · 🚶 ก่อนสูตร · reading path · `.pq` · 🧠 `.qv` · 📖 ศัพท์ใหม่ + "3 คำต้องจำก่อน" · ห้าม hallucinate | เหมือนกัน |

บทเสริม statarb 5 บท **ไม่ได้ทำตามกายวิภาค nq ครบ**: ไม่มี 📖 ศัพท์ใหม่ / ✍️ / 🎯 / 🔗 เลยทั้ง 5 บท · มี `.dft` 4/5 · `.scene` "🎬 ฉากของมิน" 2/5 (alpha-decay, blending) · `nq_qa.py` ไม่สแกนไฟล์ `statarb-*` · ใช้ "📚 อ่านต่อ" อ้าง paper จริง (เช่น Sklar 1959, Xie et al. 2016, Rad-Low-Faff 2016) + ลิงก์บทถัดไป

---

## 3. อุปกรณ์เล่าเรื่องของเล่ม และสิ่งที่ย้ายมาเล่ม stat arb ได้

| อุปกรณ์ | ในเล่ม nq (ข้อเท็จจริง) | ใช้กับเล่มใหม่ได้ตรง ๆ | ต้องคิดใหม่ |
|---|---|---|---|
| **มิน (golden thread)** | พนักงานประจำ เทรดหลังเลิกงาน · `MIN_ACCOUNT` = ทุน 50,000 บาท · ค่าธรรมเนียม 0.1%/ข้าง (0.2%/รอบ) · ระบบเดิม EMA 12/26 + RSI 30/70 · 2 ไม้/สัปดาห์ (104 ไม้/ปี → 9.6 ปีถึง 1,000 ไม้) · "ตัวเลขสมมติที่ประกาศตรง ๆ ว่าสมมติ — ห้ามเปลี่ยนกลางเล่ม" · มีในทุกบท (นับคำ "มิน" 6–34 ครั้ง/บท) · Part 9 = 30 วันของมินเดินครบสาย · บทเสริม alpha-decay และ blending ใช้ "🎬 ฉากของมิน" และผูก 2 ไม้/สัปดาห์ต่อ | กลไก "บัญชีเดียว ตัวเลขชุดเดียวทั้งเล่ม" ประกาศใน JSON · ฉากหน้าจอของตัวละคร · callback แบบฝึกหัดข้ามบท | ตัวละครเดิมหรือใหม่ (มินเทรดทิศทางคริปโต · stat arb ต้องถือสองขา) · บัญชีต้องมีพารามิเตอร์ใหม่ (ต้นทุนสองขา, ยืม/ชอร์ต, ทุนต่อคู่) |
| **สายการผลิต 8 สถานี (metaphor เดียว)** | ① ข้อความ ② ฐาน ③ การวัด ④ การกระจาย ⑤ ต้นทุน ⑥ โครงสร้าง ⑦ ขนาด ⑧ บันทึก · แผนภาพ SVG ใน index+Part 0 (อินดิเคเตอร์อยู่สถานี ③ เท่านั้น) · บท = สถานี · Part 9 เดินครบ · runbook = 8 คำถาม · ภาคผนวก A จัดตามสถานี · บทเสริม statarb ถูกวางใต้สถานี ②/⑦/⑧ ในภาคผนวก A | หลัก "metaphor เดียวทั้งเล่ม" (craft-standard) · โครง "ถ้าข้ามไปจะเจ็บแบบไหน" | metaphor ของเล่มใหม่: ต่อยอด 8 สถานีกับ stat arb หรือใช้ metaphor ใหม่ (ดูข้อเสนอ) |
| **ตัวเลขเด่นประจำบท** | ตาราง "ตัวเลขเด่นในบท" ใน `nq-index.html` บทละ 1 ประโยค เช่น "เหรียญสุ่มสร้าง 'ขึ้น 3 วันติด' ได้ 11.0 ครั้ง เท่าตลาดจริงพอดี" · "การค้นหา 828 ชุดเสกผลงานปลอมได้ 4.77 จุด" · "85% ของกำไรทั้งเดือนมาจาก 2 วันใน 30 วัน" · ทุกเลขมาจาก JSON | ตรง ๆ (ทุกบทต้องมี "เลขหมัดเด็ด" ที่ตรวจย้อนได้) | ข้อมูลจำลองต้องบอกในบทว่าเป็นการจำลอง |
| **ภาคผนวก A แผนที่เข้าคลัง** | ตาราง "ติดที่สถานีไหน อ่านอะไรต่อ" + เส้นทางสี่แบบ (🟢 อ่านกราฟ / 🔵 เขียนโค้ด / 🟣 ทฤษฎี / 🟠 ลงมือ) + ตารางเครื่องมือ + คำเตือน "อย่าอ่านทุกเล่ม" · เขียนมือ · อ้างไฟล์ด้วย `<code>` เป็นส่วนใหญ่ | โครงตรง ๆ | ไฟล์ที่ชี้ไปต้อง "เปิดได้จริง" (ข้อ 4/W8) |
| **ภาคผนวก B ศัพท์** | สร้างด้วย `nq_glossary.py` · 2 ชั้น · ลิงก์กลับบท | สคริปต์ (หลัง generalize) | — |
| **ภาคผนวก C การ์ดเดียวจบ** (`nq-runbook.html`) | 8 คำถามก่อนกดคำสั่ง (คอลัมน์ "ถ้าตอบไม่ได้") · สมุดหกบรรทัดต่อไม้ (ช่องว่างให้กรอก) · ตารางค่าเริ่มต้นทั้งเล่ม (อ้าง Part ต้นทาง) · สัญญาณอันตราย 5 ข้อ · ประโยคเดียว · พิมพ์ได้ ~6 หน้า A4 · เขียนมือ | โครงตรง ๆ | เนื้อหาเฉพาะ stat arb |
| **ภาคผนวก D แบบฝึกหัด** | `nq_drills.py` · 30 ข้อ · ไม่มีเฉลย · เกณฑ์ "Monday-Morning Test" 6 ชิ้น | สคริปต์ | เกณฑ์สำเร็จของเล่มใหม่ |
| **เครื่องมือกดเล่น** | 4 หน้า `nq-tool-*.html` (จริงหรือสุ่ม · ต้องเทรดกี่ไม้ · เส้นเสมอตัว · ขนาดไม้กับการอยู่รอด) + หน้ารวม `nq-tools.html` · JS vanilla ในหน้า · `nq-tool-randomness` ฝัง array ผลตอบแทนรายวันจริง `const REAL = [...]` · ใช้ `Math.random` (ไม่ seed — เป็น interactive) · ทุกตัวขึ้นทะเบียนใน `tools-index.html` (เลข 06–09) | รูปแบบหน้า (`.tool .ctrl` slider + `.out` + `.big`) · ลิงก์คู่บท | เครื่องมือใหม่สำหรับ stat arb |
| **🎬/🧭/⚠️ ชุดปิดบท** | ทุกบท | ตรง ๆ | — |
| **ความถ่อมตัว/ขอบเขตข้อสรุป** | ทุกบทบอก "สรุปอะไรได้/ไม่ได้" (เช่น "ข้อมูล 57 วันคือน้อยมาก และเป็นช่วงตลาดขาขึ้น") · Part 9 "สามสิบวันนี้พิสูจน์อะไรไม่ได้เลย" | ตรง ๆ | — |
| **กล่อง "ตัวเลขในเล่มนี้มาจากไหน"** (`nq-index.html`) | ประกาศ JSON กลาง · seed คงที่ · charts จากไฟล์เดียวกัน · ตัวตรวจ · ข้อจำกัด | ตรง ๆ | ข้อความต้องเปลี่ยนจาก "ข้อมูลจริง" เป็น "ข้อมูลจำลอง seed คงที่" ให้ตรงความจริง |

---

## 4. กฎเหล็ก / จุดอ่อน ที่โค้ดและ commit อ้างถึง (รวบรวมเท่าที่พบ — ไม่เติมเอง)

| รหัส/ชื่อ | ถ้อยคำในแหล่ง | แหล่ง | บังคับใช้ด้วย |
|---|---|---|---|
| **กฎเหล็กข้อ 5 ของแผน** | "ห้ามพิมพ์ตัวเลขลอย ๆ ลงในบท ทุกตัวเลขต้องมาจากไฟล์นี้ และไฟล์นี้ต้องคำนวณจากข้อมูลจริงใน data/ ได้ซ้ำเสมอ" | `tools/nq_figures.py` บรรทัด 4–5 | `nq-figures.json` + `--check` + `nq_check_figures.py` |
| **W7** | "เล่มเดิมเจอตัวเลขขัดกันเอง 40-50 จุด เพราะพิมพ์เลขด้วยมือคนละที่" · กราฟกับข้อความ "ขัดกันเอง" | `tools/nq_check_figures.py` บรรทัด 4 · `tools/nq_charts.py` บรรทัด 4–5 | `nq_check_figures.py` (17 ค่าบังคับ + เตือนเลข % แปลกปลอม) · `nq_charts.py` (กราฟวาดจาก JSON) |
| **W8** | "ลิงก์ภายในทุกอันชี้ไปไฟล์ที่มีอยู่จริง (ห้ามอ้างถึงสิ่งที่เปิดดูไม่ได้)" | `tools/nq_qa.py` บรรทัด 7 | ตรวจเฉพาะ `href="…html"` — **ไม่ตรวจ `<code>` อ้างอิง** (ดูข้อ 8) |
| **W9** | "จำนวนศัพท์ใหม่ต่อบทไม่เกินเพดาน (กันหน้าผา)" | `tools/nq_qa.py` บรรทัด 8 | `TERM_CAP = 12` |
| **W11** | "โครงสร้าง HTML สมดุล และไม่มี `<br>` ปลอมจำลองรายการ" | `tools/nq_qa.py` บรรทัด 5 | parser tag balance + regex `<br>\s*(•|·\s|\d+\.\s)` |
| กล่องบังคับตามมาตรฐานงานฝีมือ | "กล่องบังคับตามมาตรฐานงานฝีมือครบทุกบท" (ข้อ 2 ใน docstring ไม่มีรหัส W) | `tools/nq_qa.py` บรรทัด 6 | `REQUIRED_BOXES` + `CHAPTER_BOXES` |
| ห้ามแก้ Thai line-break script ด้วยมือ | "ห้ามแก้ Thai line-break script ด้วยมือตามกฎ style guide" | `tools/nq_new_part.py` บรรทัด 5–6 · `references/style-guide.md` A | คัดลอกจาก `nq-part1.html` · `nq_qa` ตรวจ `data-thwbr` |
| ภาคผนวกต้องสร้างจากบท | "ภาคผนวกศัพท์ที่คัดลอกมาด้วยมือจะเพี้ยนจากบททันทีที่มีการแก้บทใด ๆ" | `tools/nq_glossary.py` · `tools/nq_drills.py` | สคริปต์ |
| seed คงที่ + ตรวจข้ามเมล็ด | "ทุกฟังก์ชันตรึงเมล็ดสุ่มไว้ … (ตรวจแล้วว่าค่าที่รายงานนิ่งข้ามเมล็ด ไม่ใช่ผลของเมล็ดใดเมล็ดหนึ่ง)" | `tools/nq_figures.py` บรรทัด 127–130 | `SEED = 20260830` (+ offset ต่อ study) |
| ผลจากไม้น้อย = ภาพประกอบกลไก | "ผลที่ได้มาจากไม้เพียงไม่กี่ไม้ จึงใช้เป็น *ภาพประกอบกลไก* ไม่ใช่หลักฐานทางสถิติ" + คีย์ `"เตือน"` ใน JSON | `_indicator_study` | ถ้อยคำในบท |
| ชุดจำลองที่ "หลอก" vs ชุดที่ใช้ตัดสินใจ | "ทำสองชุดโดยตั้งใจ ก) ใช้ผลตอบแทนจริงทั้งดุ้น … ชุดที่ *หลอก* ข) ตัดค่าเฉลี่ยออก … ความต่างของสองชุดนี้คือบทเรียนหลักของบท" | `_survival_study` | ออกแบบ study |
| กฎเหล็กของแผนเล่มก่อน | "เขียนครั้งเดียวมีบ้านเดียว — เรื่องที่เล่มเดิมมีแล้ว ให้ *อ้างอิง* ไม่เขียนซ้ำ" | `docs/quant-theory-volumes-plan.md` บรรทัด 18 | ไม่มีสคริปต์ |
| กฎเหล็ก 3 ข้อของการ์ด | พังเมื่อไร ≠ ข้อเสีย · สัญชาตญาณก่อนสูตร · ห้าม hallucinate | `references/card-anatomy.md` | ไม่มีสคริปต์ |
| output ตรงกับโค้ด | "ทำให้บรรทัดผลลัพธ์ตรงกับที่โค้ดพิมพ์จริงทั้งเล่ม" (PR #28) · "รันโค้ดทุกบล็อกซ้ำหลังแก้ = พิมพ์ตรงตามคอมเมนต์" | commit `2a18ad7`, `5663b42` | ตรวจมือ/subagent |
| re-verify ก่อนแก้ตามรีวิว | "Every finding below was re-verified numerically before being acted on." | commit `71f8d1a`, `9737f5e`, `2a69c4e` | กระบวนการ |

**สิ่งที่ไม่มีใน repo นี้:** นิยามของ W1–W6, W10 และกฎเหล็กข้ออื่นนอกจากข้อ 5 · เอกสารแผนเล่ม nq · ไฟล์ `options-data/docs/next-phase-plan.md` (ถูกอ้างใน commit `6c61340`, `cf012a8`, `e950da2`, `6b254b9`, `552a59e`)

---

## 5. กระบวนการรีวิว และการใช้ subagent ที่อนุมานได้จากประวัติ

### 5.1 เล่ม nq เอง
- เขียนและรีวิวใน repo `options-data` — ประวัติรายบทไม่อยู่ที่นี่ · ใน repo นี้มีแค่ commit ย้าย `6c61340` ที่บันทึกการตรวจ: "nq_qa.py และ nq_check_figures.py ผ่านทั้ง 20 ไฟล์ · ไม่มีลิงก์เสีย · เรนเดอร์ผ่านทั้ง 21 ไฟล์ที่ 1000px และ 420px ไม่มี error · สคริปต์สร้างตัวเลขใหม่ให้ผลตรงกับต้นฉบับใน options-data 100%"
- PR รวม: `20b58ab` (2026-09-07) "เพิ่มหนังสือ 'คิดแบบ Quant' + สายเสริม stat arb 5 บท (#31)"

### 5.2 บทเสริม stat arb 5 บท (งาน A–E ของ next-phase-plan)
แต่ละ commit = 1 บท + 1 สคริปต์ตัวเลข + 1 JSON + แถวใหม่ใน `nq-appendix-map.html` + ลิงก์ "อ่านต่อ" จากบทก่อนหน้า + บรรทัดตรวจซ้ำกันเป๊ะ: "ตรวจ HTML tag balance, ลิงก์ภายในทั้งหมด, เรนเดอร์ผ่าน Playwright ที่ 1000px/420px ไม่มี error ไม่มี overflow" · ไม่มีการกล่าวถึงคณะผู้เชี่ยวชาญใน commit เหล่านี้ · ข้อความ commit ยาว อธิบาย "ตอบคำถามอะไร + ตัวเลขหลัก + สคริปต์ + เชื่อมที่ไหน + ตรวจอะไร + ต่อจากงานไหน"

### 5.3 เล่มก่อนหน้า (รูปแบบรีวิวที่เจ้าของคุ้น)

| commit | คณะ/เลนส์ |
|---|---|
| `eeb686b` → `38781c0` (2026-07-01) | "ทีมผู้เชี่ยวชาญ 3 ด้านตรวจ" (eeb686b, Intl.Segmenter + `<wbr>`) → ผู้เชี่ยวชาญ typography จับว่า `overflow-wrap:break-word` คือตัวตัดคำไทยกลางคำ (38781c0) |
| `9d04192` | "คณะปรุง 3 ด้าน (narrative/quant-soul/learning design)" → กำเนิดมาตรฐาน v4 (🎬/🧭/heuristic/💎) |
| `6a402a4` / `9ea9dc8` | "ผ่านรีวิวผู้เชี่ยวชาญ 3 คน / 2 คน — แก้ครบ" (คู่กับ "ร่างก่อนรีวิว" `5f84437`, `f6aea5d`) |
| `5663b42` (2026-07-07) | 4 เลนส์: quant-math · options practitioner · learning design · Python code |
| `2586a51` | 4 เลนส์ whole-book "safe to merge (math 0 error · citation 0 hallucination …)" |
| `8cb5b45` | "Ran a 5-agent expert review panel (technical accuracy + narrative craft)" — ตรวจข้ามกับฉบับ v4 ที่ fact-check แล้ว |
| `9737f5e` | "Three independent reviewers (math / practitioner / learning design / code)" |
| `71f8d1a` → `9360e4e` → `2a69c4e` | 3 เลนส์สำหรับเล่ม 2·F: "Two of three review lenses returned (the statistics lens hit the session limit twice)" → เก็บ learning-design + code-quality → "The third review lens finally ran" · PR `8678699` "(ผ่านรีวิว 3 เลนส์)" |
| `69b24ae` | refactor `<br>` ปลอม 31 กล่อง "แก้โดย 3 agent ขนาน" + ยืนยัน byte-for-byte |
| เมษายน 2026 (`34ab429`, `04298af`, `bf726bd`) | "5-team proofreading" · "ruthless reviewers" (Goldman 30yr + Citadel + JoF reviewer) |

เลนส์ใน `references/craft-standard.md`: เนื้อหาเชิงลึก · วิชาการ (citation) · คนใช้จริง · บรรณาธิการการสอน · ภาษา/typography/i18n — "spawn เป็น subagent หรือสวมบทเอง ทีละเลนส์"

**pattern ที่อนุมานได้:**
- คณะ 3–5 เลนส์ รันเป็น subagent ขนาน (มีกรณีชน session limit แล้วรันเลนส์ที่เหลือภายหลัง)
- ทุกข้อที่รีวิวจับได้ ถูก "re-verify numerically" ก่อนแก้ และบันทึกตัวเลขก่อน/หลังใน commit
- ตรวจกลไก (tag balance, ลิงก์, contrast, render 0 page error, overflow ที่ 1000/420px, โค้ดพิมพ์ตรง output) แยกจากรีวิวเนื้อหา
- commit แยก: ร่าง → apply review (ต่อเลนส์หรือรวม) → PR merge ระบุจำนวนเลนส์
- ท้าย commit มี `Co-Authored-By: Claude …` + `Claude-Session: …`

---

## 6. ข้อจำกัดของสภาพแวดล้อม และผลต่อเล่มใหม่

| ข้อจำกัด | ผล | ผลต่อเล่ม stat arb ที่ใช้ข้อมูลจำลอง seed คงที่ |
|---|---|---|
| ไม่มี `data/` และ `../options-data/data` | `nq_figures.py`, `copula/blending/live_backtest_figures.py`, `data_health.py` รันไม่ได้ · `nq-figures.json` สร้างใหม่ไม่ได้ (แต่อ่านได้) | **ไม่กระทบ** ถ้าสคริปต์ตัวเลขของเล่มใหม่สร้างข้อมูลเอง (แบบ `alpha_decay_figures.py`) · ข้อดีกว่า nq: สร้างซ้ำได้ทุกที่ ไม่ต้องมี repo ข้อมูล |
| scipy ไม่มี · numpy 2.5.3 มี · Python 3.13.18 | สคริปต์ที่ใช้ `scipy.stats/optimize` รันไม่ได้ (ยังไม่ได้ทดสอบว่า pip ติดตั้งผ่าน proxy ได้หรือไม่) | ADF/cointegration/OU fit ต้องเขียนด้วย numpy หรือ stdlib · ถ้าจำเป็นต้องใช้ scipy/statsmodels ต้องตรวจการติดตั้งก่อน |
| seed กับเวอร์ชันไลบรารี | nq ใช้ `random.seed(SEED + offset)` ของ stdlib | ถ้าต้นฉบับ Markdown พิมพ์ตัวเลขจากการจำลองด้วย seed หนึ่ง ต้องยืนยันว่ารันที่นี่ได้ตัวเลขเดียวกันก่อน (*ข้อเสนอ*: ทำเป็นด่านแรกของแผน) และตามธรรมเนียม nq ควร "ตรวจว่าค่านิ่งข้ามเมล็ด" |
| ความจริงของข้อความ | หน้ารวม nq เขียนว่า "ตัวเลขทุกตัวมาจากข้อมูลจริง" | เล่มใหม่ต้องเขียนว่า "ข้อมูลจำลอง" ทุกที่ที่เกี่ยว ห้ามยกถ้อยคำ "ข้อมูลจริง" ของ nq มาตรง ๆ |
| ไฟล์ภายนอกที่อ้างถึง | 23 ชื่อใน `<code>` ไม่มีไฟล์ในคลัง (ข้อ 8) · commit `6c61340` บอกว่า repo "กระจายเป็น 19 branch" · local มีแค่ 2 branch (`claude/charming-wright-1xtlip`, `claude/payoff-chart-lesson-KchZQ`) | ถ้าเล่มใหม่จะอ้างซีรีส์ `statarb-ch*` / `practice-*` ต้องตัดสินใจว่าเป็น "ข้อความอ้างอิง" หรือย้ายไฟล์เข้ามา |
| Playwright / PDF / ฟอนต์ | ใช้ได้ (ทดสอบแล้ว) · Sarabun โหลดจาก Google Fonts ผ่าน proxy | ขั้น PDF ใช้ได้ทันที |
| render check 1000px/420px | ไม่มีสคริปต์ใน repo (ทำ ad hoc ทุกครั้ง) | ควรเขียนสคริปต์ตรวจ overflow/page error ของเล่มใหม่ (*ข้อเสนอ*) |

---

## 7. จุดเชื่อมเล่มใหม่เข้าคลัง

| ไฟล์ | รูปแบบเดิมที่ nq ใช้ | สิ่งที่ต้องทำกับเล่มใหม่ |
|---|---|---|
| `docs/index.html` (บรรทัด ~36–42) | `<h2>📘 เล่มใหม่ในโปรเจกต์นี้: คิดแบบ Quant</h2>` + `.bx.bg` อธิบาย "ประตูหน้า" + ลิงก์ `nq-index.html` | เพิ่มการ์ดแบบเดียวกันใต้ nq (ระบุว่าเป็นเล่มต่อจาก nq / สาย stat arb) |
| `docs/nq-appendix-map.html` | แถว "(ต่อ)" ใต้สถานี ②/⑦/⑧ ชี้ `statarb-*.html` ด้วย `<a href>` + ป้าย "(บทเสริมสาย stat arb)" · เส้นทางสี่แบบ · ตารางเครื่องมือ | เพิ่มแถว/เส้นทางชี้ `sab-index.html` (และพิจารณาว่าบทเสริม 5 บทอยู่ตรงไหนในเล่มใหม่) |
| `docs/nq-index.html` | ตารางภาคผนวก + กล่อง "ตัวเลขในเล่มนี้มาจากไหน" | (ถ้าต้องการ) เพิ่มแถว "อ่านต่อ: เล่ม stat arb" |
| `docs/nq-part9.html` / `.pq` ปิดเล่ม | "แผนที่อยู่ในภาคผนวก" | (ถ้าต้องการ) สะพานไปเล่มใหม่ |
| `docs/tools-index.html` | การ์ด `<a class="tool" href=…><span class="n">06</span><div class="theory">คิดแบบ QUANT · …</div><div class="t">…</div><div class="d">…</div><div class="rule">กฎที่ได้: …</div></a>` เลข 01–09 | ถ้ามีเครื่องมือใหม่ เพิ่มเลข 10+ รูปแบบเดียวกัน |
| `docs/nq-tools.html` | กล่อง "🔗 เครื่องมือจากเล่มอื่นในคลัง" | เพิ่มชื่อเครื่องมือใหม่ |
| บทเสริม `statarb-*.html` | ลิงก์ "📚 อ่านต่อ" เป็นสายต่อกัน copula → blending → live → decay → data-quality · ท้ายหน้ามีลิงก์ `nq-index.html` · `nq-appendix-map.html` | ลิงก์ไขว้กับบทของเล่มใหม่ที่ตรงหัวข้อ (Write Once — อ้างอิงแทนเขียนซ้ำ) |
| `docs/pdf/README.md` + `docs/pdf/render-pdf.mjs` | ล้าสมัย (14 ไฟล์ theory/pillars) | ใช้ `render-pdf.mjs` ของสกิลแบบระบุชื่อไฟล์ หรืออัปเดต README |
| `.claude/skills/knowledge-book/SKILL.md` | ไม่กล่าวถึง nq/สายพานตัวเลข | (ถ้าต้องการ) บันทึกสายพานที่ generalize แล้วลงสกิล เพื่อเล่มต่อไป |

---

## 8. ความไม่สอดคล้อง/บั๊กเล็กที่พบระหว่างตรวจ (ข้อเท็จจริง ไม่ได้แก้)

1. `nq_new_part.py`: docstring ตัวอย่างมี 3 อาร์กิวเมนต์ แต่โค้ดต้องการ 4 · `slug` ไม่ถูกใช้
2. `nq_charts.py`: ข้อความ "ไม่มีไฟล์ไหนมีตัวคั่น <!--CHART:ชื่อ--> ให้เขียน" ออกเมื่อไม่มีไฟล์ไหน *เปลี่ยน* (ไม่ใช่ไม่มี marker)
3. `nq_glossary.py`: dict `TITLES` ประกาศแต่ไม่ได้ใช้
4. `nq-part9.html` 🔗 เขียนว่า "ภาคผนวก D — แบบฝึกหัดทั้งเล่ม พร้อมแนวคำตอบ" แต่ `nq-appendix-drills.html` (จาก `nq_drills.py`) บอกว่า "แบบฝึกหัดในเล่มนี้ไม่มี 'เฉลย'" · และ 🔗 ของ Part 9 ไม่มี `href` ไปภาคผนวกเลย
5. W8 ผ่านเพราะตรวจแค่ `href` — มี 23 ชื่อใน `<code>` ที่ไม่มีไฟล์ในคลัง: `grid-part0` `ob-part0` `ob-part2` `ob-part6` `ob-part14` `playground-part0/5/7` `practice-part0/2/7/9` `python-part0` `statarb-ch0/ch4b/ch6/ch12/ch21` `vol-part1/8` `vp-drills` `vp-part1/7` (กระจายใน nq-part0,2,3,4,5,6,7,8, appendix-map, statarb-copula-practice) · commit `6c61340` ยอมรับข้อจำกัดนี้สำหรับ `practice-part2`
6. ตัวคั่น CHART ในบทเสริม (`decay-detection`, `data-quality-survivorship`, `live-liquidity`, `blending-search`) ไม่มีสคริปต์ใดลงทะเบียน → SVG ระหว่างตัวคั่นเป็นของที่วางมือ · `statarb-copula-practice.html` ไม่มีตัวคั่นเลย
7. ไม่มีตัวตรวจเลขของบทเสริม — ตรวจคร่าว ๆ (ทศนิยมในหน้า vs JSON ของบท): copula 3/44 ไม่อยู่ใน JSON (`0.2`, `2.3`, `2.4` — น่าจะเป็นเลขหัวข้อ §), blending 1/11 (`4.77` มาจาก nq Part 8), alpha-decay 1/8 (`1.5`), live/data-quality 0 → วินัยตัวเลขรักษาด้วยมือ
8. `alpha_decay_figures.py` คัดลอก `TRADES_PER_WEEK = 2` จาก `MIN_ACCOUNT` ด้วยมือ (golden thread ผูกด้วยคอมเมนต์ ไม่ใช่ import)
9. `docs/pdf/render-pdf.mjs` + `README.md` ล้าสมัย (14 ไฟล์) ต่างจากรุ่นในสกิลที่รับชื่อไฟล์

---

## 9. ข้อเสนอสำหรับแผนเล่มใหม่ (แยกจากข้อเท็จจริงข้างบน)

1. **prefix `sab-`** สำหรับทุกไฟล์ (`sab-part*.html`, `sab-figures.json`, `tools/sab_*.py`) — ไม่ชนของเดิม และไม่ใช้ `statarb-`
2. **generalize ด้วยการคัดลอกเป็น `tools/sab_*.py`** (ไม่แก้ `nq_*.py` เพื่อไม่ให้เล่ม nq เสี่ยงพัง) โดยแยกค่าผูกเล่มไว้ส่วนหัวไฟล์ (`PREFIX`, `BOOK_TITLE`, `FIG_JSON`, `SOURCE_SHELL`, `TITLES`, `REQUIRED`, เกณฑ์สำเร็จ) · แก้บั๊กเล็กในข้อ 8.1–8.3 ในฉบับคัดลอก
3. **`tools/sab_figures.py` เป็นการจำลองล้วน** ตามแบบ `alpha_decay_figures.py` + โครง `--check` ของ `nq_figures.py` · ประกาศ SEED เดียวในไฟล์ (+offset ต่อ study) · ใช้ stdlib/numpy เท่านั้น (ไม่มี scipy) · ตรวจ "ค่านิ่งข้ามเมล็ด" สำหรับเลขหมัดเด็ดทุกตัว
4. **ด่านแรกของแผน: กระทบยอดต้นฉบับ Markdown** — ทุกตัวเลขในต้นฉบับต้องมีที่มาใน `sab-figures.json` (หรือถูกตัด) ก่อนเริ่มเขียน HTML · ตามธรรมเนียม PR #28 "บรรทัดผลลัพธ์ตรงกับที่โค้ดพิมพ์จริง"
5. **ขยายตัวตรวจให้ปิดช่องที่ nq มี**: ตรวจ `<code>ชื่อไฟล์</code>` ด้วย (W8 จริง) · ตรวจเลขที่ไม่มี `%` (เช่น ค่า z, half-life, จำนวนไม้) · ตรวจลำดับชุดปิดบท · ลงทะเบียนกราฟทุกอันใน `sab_charts.py` (ไม่มี SVG วาดมือที่มีตัวเลข)
6. **คงกายวิภาคบทของ nq ทั้งชุด** (🧭 เส้นทางอ่าน → ฉากเปิด → `.pq` → เนื้อหา 3–5 H2 → ⚠️ → 🎬 → 🧭 → 🧮 → ✍️ 3 ข้อ → 🎯 3 ข้อ → สรุป → `.pq` สะพาน → 🔗 → 📖) · ความยาวเป้า ~2,000–2,800 คำไทย/บท · 1–2 กราฟ/บท · ศัพท์ใหม่ 5–7 คำ (เพดาน 12)
7. **ตัวละคร**: ตัดสินใจระหว่าง "มินเรียนต่อ" (บทเสริม 2 บทใช้มินแล้ว ต่อเนื่องจาก nq) กับตัวละครใหม่ · ถ้าใช้มิน ให้ขยาย `MIN_ACCOUNT` เป็นบัญชี stat arb ที่ประกาศครั้งเดียวใน JSON
8. **metaphor**: พิจารณาต่อยอด 8 สถานี (เช่น ① สมมติฐานของคู่ ② ฐาน = คู่สุ่มก็ "ผ่าน" ได้บ่อยแค่ไหน ③ การวัด z/hedge ratio ④ หางของสเปรด ⑤ ต้นทุนสองขา ⑥ โครงสร้างเข้า-ออก ⑦ ขนาด ⑧ บันทึก/ตรวจเสื่อม) เพื่อให้ภาคผนวก A ของ nq ชี้มาได้ตรงสถานี — หรือ metaphor ใหม่หนึ่งเดียวทั้งเล่ม
9. **ภาคผนวก**: ใช้ครบ 4 ชิ้นแบบ nq (A แผนที่ · B ศัพท์ [สคริปต์] · C การ์ดเดียวจบ · D แบบฝึกหัด [สคริปต์]) · แก้ข้อขัดแย้ง "มี/ไม่มีเฉลย" ตั้งแต่แผน
10. **เครื่องมือกดเล่น 2–4 ตัว** ในรูปแบบหน้า `nq-tool-*` และลงทะเบียน `tools-index.html` เลข 10+ (*ตัวอย่างหัวข้อ*: คู่สุ่มดู cointegrated บ่อยแค่ไหน · เส้นเสมอตัวสองขา · half-life กับเวลาถือ)
11. **รีวิว**: คณะ 4–5 เลนส์เป็น subagent ขนาน (สถิติ/econometrics · practitioner stat arb · learning design มือใหม่ · ภาษา/typography · ตรวจโค้ด-ตัวเลข) + re-verify ตัวเลขก่อนแก้ทุกข้อ + ตรวจกลไก (qa/check/render 1000/420px/PDF) แยกต่างหาก · commit "ร่างก่อนรีวิว" → "ผ่านรีวิว N เลนส์ — แก้ครบ"
12. **เชื่อมคลัง**: `docs/index.html` (การ์ดเล่มใหม่) · `nq-appendix-map.html` (แถว/เส้นทาง) · `tools-index.html` · ลิงก์ไขว้กับบทเสริม `statarb-*` · ทำทั้งหมดในขั้นสุดท้ายหลัง qa ผ่าน
