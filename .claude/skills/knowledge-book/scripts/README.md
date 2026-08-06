# สคริปต์ตรวจหนังสือ

## render-pdf.mjs — export HTML → PDF
```bash
node .claude/skills/knowledge-book/scripts/render-pdf.mjs docs
node .claude/skills/knowledge-book/scripts/render-pdf.mjs docs pillars-part1 theory-part2
```

## cliff-map.py — วัดความครอบคลุมของ scaffolding
หาบล็อกโค้ดที่ยาว/ยาก แต่ไม่มีกล่องอธิบาย (`.read-aloud` / `.ai-decode`) ติดอยู่
ใช้เป็นเกณฑ์ "R3 จบ" ใน `docs/python-book-improvement-plan.md` §8.9

```bash
python3 .claude/skills/knowledge-book/scripts/cliff-map.py docs
python3 .claude/skills/knowledge-book/scripts/cliff-map.py docs 'python-part*.html'
```

## extract-code.py + run-code-blocks.py — รันโค้ดในหนังสือจริง
เลนส์ตรวจที่สำคัญสุดของหนังสือสอนโค้ด: สกัดทุกบล็อก `<div class="fm">`
ออกมา**รันจริง** แบบ cumulative namespace ต่อไฟล์ (เลียนแบบผู้อ่านที่ไล่รันจากต้นบท)

```bash
export SNIPPET_DIR=/tmp/book-snippets
python3 .claude/skills/knowledge-book/scripts/extract-code.py
python3 .claude/skills/knowledge-book/scripts/run-code-blocks.py            # ทุกไฟล์
python3 .claude/skills/knowledge-book/scripts/run-code-blocks.py part2      # เจาะจง
```

ต้องมี: `numpy pandas matplotlib scipy statsmodels scikit-learn plotly pulp`

### ⚠️ กับดักที่เคยพลาดมาแล้ว — อ่านก่อนใช้
1. **ห้ามลบ HTML tag ด้วย regex `<[^>]+>`** — มันจะกิน format spec ของ f-string
   เพราะ `{'x':<28} {y:>10.2f}` ตรงกลางหน้าตาเหมือน tag → ทำให้โค้ดที่ถูกอยู่แล้ว
   ดูเหมือนพัง (`extract-code.py` ลบเฉพาะ tag ที่รู้จักแล้ว)
2. **`.ad-code` ห้ามปนลำดับรันหลัก** — เป็นภาพประกอบสอน (คลาสเวอร์ชันย่อ)
   จะไปทับคลาสจริงที่นิยามใน `.fm`
3. **false positive ที่ต้องคัดออกด้วยมือ** — ตัวอย่างที่ตั้งใจให้ผิด (มีป้าย ❌),
   บล็อกพรีวิวต้นบทที่อ้างของที่นิยามทีหลัง, `inspect.getsource` บนโค้ดที่ exec
4. **อ่าน HTML ต้นฉบับยืนยันทุก finding ก่อนแก้เสมอ** — ห้ามเชื่อ output ของสคริปต์

## check-output.py + sync-output.py — เทียบ/ซิงก์ผลลัพธ์ที่หนังสือเขียนไว้
ข้อบกพร่อง**คนละชั้น**กับ "รันได้ไหม": โค้ดรันผ่านแต่ตัวเลขในหนังสือไม่ตรง
= ผู้อ่านรันตามแล้วได้ผลต่าง จะคิดว่าตัวเองทำพลาด

```bash
python3 .../check-output.py part4          # ดูว่าตรงไหมบ้าง
python3 .../sync-output.py part4           # dry-run
python3 .../sync-output.py part4 --apply   # เขียนผลจริงลง .output
```
ต้องรัน `run-code-blocks.py <part>` ก่อน แล้ว copy `run_results.json` เป็น `rr_<part>.json`

⚠️ regex จับคู่ `.fm` กับ `.output` ต้องกันไม่ให้ข้าม `</div>` — ถ้าใช้ `(.*?)`
เฉย ๆ มันจะไล่ข้ามบล็อกไปหา `.output` ที่อยู่ไกล แล้วจับคู่โค้ดกับผลลัพธ์คนละก้อน

### หมายเหตุการใช้ check-output.py
- ต้องมี `rr_<part>.json` (คัดลอกจาก `run_results.json` หลังรัน `run-code-blocks.py <part>`)
  ถ้าไม่มีจะ fallback ไป `run_results.json` ซึ่ง**อาจเป็นผลของ part อื่นที่ค้างอยู่**
  แล้วรายงานว่า "ไม่ได้รัน" ทั้งไฟล์ — เจอมาแล้ว
- บล็อกที่หนังสือย่อด้วย `...` จะถูกข้าม (เกณฑ์เดียวกับ sync-output)

### บล็อกที่เป็น "เนื้อไฟล์" (ไม่ถูกรัน)
บางบล็อกไม่ใช่โค้ดที่รันต่อกันในสคริปต์เดียว แต่เป็น**เนื้อของไฟล์แยก**
(เช่น `test_strategy.py` ที่ให้ pytest รัน) · ติดป้ายด้วยหัวบรรทัดแรก:

```
# ── test_strategy.py ──
```

ทั้ง `run-code-blocks.py` และ `check-output.py` จะข้ามบล็อกแบบนี้
เพราะรันในลำดับเดียวกับบล็อกอื่นไม่ได้ (import ข้ามไฟล์, ต้องมี pytest เรียก)

### ⚠️ rr_<part>.json ค้างได้ง่ายมาก
ถ้าแก้ไฟล์ HTML แล้ว **เลขบรรทัดของทุกบล็อกจะขยับ** — ต้อง `extract` + `run`
ใหม่ก่อน `check` เสมอ ไม่งั้นจะรายงานว่า "ไม่ได้รัน" เป็นสิบจุดโดยไม่มีอะไรผิดจริง

### ⚠️ KaTeX ทำ Chromium crash บางหน้า (มี workaround ในสคริปต์แล้ว)
`python-part0` และ `python-part5` ทำให้ Chromium ในสภาพแวดล้อมนี้ crash
("Target crashed") ตอน layout ของ KaTeX HTML output

สิ่งที่พิสูจน์แล้ว (อย่าเสียเวลาไล่ซ้ำ):
- บล็อก **KaTeX CSS** อย่างเดียว → หาย · บล็อก **KaTeX JS** อย่างเดียว → หาย
  ⇒ ต้องมีทั้ง DOM และ CSS ถึงจะพัง
- **ทุกสูตรในหน้านั้นพังหมด** แม้สูตรง่ายที่สุด (`$$t = \text{Sharpe}\times\sqrt{T}$$`)
  เมื่อใช้ `<head>` จริงของหนังสือ ⇒ ไม่ใช่สูตรใดสูตรหนึ่งผิด
- ฟอนต์ `.woff2` ทุกไฟล์สมบูรณ์ (magic bytes `wOF2` ครบ 20 ไฟล์)
- ลองแล้วไม่ช่วย: `--no-sandbox`, `--disable-dev-shm-usage`,
  `--disable-features=FontationsFontBackend`, `--disable-gpu`,
  `--use-gl=swiftshader`, ทั้ง `chromium` และ `chromium_headless_shell`
- ไม่ใช่สคริปต์ตัดคำไทย (ลบออกแล้วยังพัง)

**workaround ที่ใช้อยู่:** ถ้าหน้าไหน crash สคริปต์จะลองใหม่โดยบล็อก
KaTeX CSS + auto-render แล้วเรียก `katex.renderToString(..., {output:'mathml'})`
เอง — Chromium เรนเดอร์ MathML ได้เองโดยไม่ต้องใช้ CSS ของ KaTeX

จุดที่ต้องระวังในทาง MathML:
1. ต้องแปลง **ทั้ง `$$...$$` และ `\(...\)`** — ถ้าทำแค่ `$$` inline จะโผล่เป็น LaTeX ดิบ
2. ต้องลบ `<wbr>` (จากสคริปต์ตัดคำไทย) **เฉพาะ element ที่มีสูตร** ก่อน
   ไม่งั้นสูตรที่มีภาษาไทยข้างใน เช่น `\text{น้ำหนัก}` จะจับไม่ติด ·
   **อย่าลบทั้งหน้า** เพราะการตัดคำไทยจะหายไปทั้งเล่ม

## mocks/ — รันโค้ด Part VI (async/network) แบบ offline
Part VI เรียก `websockets` / `aiohttp` / `requests` จึงรันในสภาพแวดล้อมนี้ไม่ได้
`mocks/sitecustomize.py` ติดตั้ง mock ของทั้งสามตัวเข้า `sys.modules` โดยคืน
ข้อความรูปแบบเดียวกับ Binance/Bybit จริง แล้ว**ปิด stream หลังส่ง 3 ข้อความ**
เพื่อไม่ให้ลูป `while True` ค้าง

```bash
export SNIPPET_DIR=/tmp/book-snippets
PYTHONPATH=.claude/skills/knowledge-book/scripts/mocks \
  python3 .claude/skills/knowledge-book/scripts/run-code-blocks.py part6
```

`run-code-blocks.py` มี timeout 20 วินาทีต่อบล็อก (SIGALRM) กันลูปไม่รู้จบ

⚠️ **บล็อก entry point ที่รันค้างคือพฤติกรรมที่ถูกต้อง** — บล็อกสุดท้ายของ
Part VI จบด้วย `if __name__ == "__main__": asyncio.run(system.run())` ซึ่งเป็น
ระบบ live ที่รอ kill switch จึงรันไม่จบโดยตั้งใจ · TimeoutError ตรงนั้นไม่ใช่บั๊ก

⚠️ **อย่า sync output ของ Part VI** — ตัวเลขขึ้นกับ network/timing/mock
ถ้า sync จะเท่ากับเอาเลขของ mock ไปฝังในหนังสือ แล้วสื่อว่าผู้อ่านต้องได้เท่ากัน
ใช้ mock เพื่อตรวจว่า **โค้ดรันได้** เท่านั้น ไม่ใช่ตรวจว่าผลตรง

## ⚠️ กับดักตอน "ตรวจการแสดงผล" — อย่านับบรรทัดจากข้อความที่ถอด tag แล้ว

หนังสือในโปรเจกต์นี้ขึ้นบรรทัดใน `.fm` **สองวิธีที่ต่างกัน** และทั้งคู่ถูกต้อง:

| กลุ่มไฟล์ | วิธีขึ้นบรรทัด | ต้องมี `white-space:pre` ไหม |
|-----------|----------------|------------------------------|
| `python-*` · `math-*` | newline จริงในไฟล์ | **ต้องมี** |
| `pm-*` `arb-*` `eye-*` `theory-*` `pillars-*` | `<br>` | ไม่ต้อง |

**เคยพลาดมาแล้ว:** สคริปต์ที่ลบ HTML tag (รวม `<br>`) แล้วนับความยาวบรรทัด จะเห็น
เนื้อหา 4 บรรทัดที่คั่นด้วย `<br>` เป็น "บรรทัดเดียวยาว 162 ตัวอักษร" → รายงานว่า
35 ไฟล์พัง ทั้งที่**ไม่พังสักไฟล์** · เกือบแก้ CSS ทับของที่ถูกอยู่แล้ว

**วิธีตรวจที่ถูก** — ดูว่าไฟล์นั้นใช้กลไกไหนก่อน แล้วค่อยตัดสิน:
```python
ws = "white-space" in re.search(r'\.fm\{[^}]*\}', t).group(0)
has_br = bool(re.search(r'<br\s*/?>', block))
# พังจริงก็ต่อเมื่อ: มี newline จริงในบล็อก · ไม่มี <br> · และ .fm ไม่มี white-space
```

**และไม่ว่าสคริปต์จะบอกอะไร ให้เปิดดูภาพจริงก่อนแก้เสมอ** — Playwright ถ่ายรูป
element เดียวก็พอ (หน้าที่มี KaTeX ต้อง `route.abort()` ทั้ง `katex.min.css` และ
`auto-render*` ก่อน ไม่งั้น Chromium crash — เหตุผลเดียวกับใน `render-pdf.mjs`)

## ป้ายกำกับบล็อกที่ไม่ต้องรัน (`run-code-blocks.py`)

| หัวบล็อก | ความหมาย | ใช้เมื่อ |
|----------|----------|----------|
| `# ── ชื่อไฟล์.py ──` | เนื้อไฟล์ ไม่ใช่โค้ดที่รันต่อกัน | ไฟล์ที่ให้ `pytest` รัน · module ที่ import ทีหลัง |
| `# ── ตัวอย่างประกอบ ──` | โค้ดที่ "ยกมาชี้ให้ดู" | ตัวอย่างที่มี `...` · โค้ดผิดที่ยกมาเทียบ · fragment ที่อ้างตัวแปรนอกบริบท |

⚠️ **ห้ามใช้ `ตัวอย่างประกอบ` เพื่อปิดเสียงบล็อกที่รันไม่ผ่าน** — ป้ายนี้มีไว้บอกว่า
"บล็อกนี้ไม่เคยตั้งใจให้รัน" ถ้าเอาไปแปะบนโค้ดที่ควรรันได้แต่พัง คุณจะทำลาย
เลนส์ตรวจที่สำคัญที่สุดของหนังสือเล่มนี้ทิ้งไปเอง

## build-toc.py — สร้างสารบัญ (per-Part + เต็มเล่ม)

```bash
python3 .claude/skills/knowledge-book/scripts/build-toc.py docs 'python-part*.html'
```

generate จาก `<h2>/<h3>` ที่มี `id` อยู่แล้ว · รันซ้ำได้ (แทนที่ระหว่าง marker
`<!-- TOC:START/END -->` และ `<!-- BOOKTOC:START/END -->`) · **รันใหม่ทุกครั้งที่เพิ่ม/แก้หัวข้อ**

ทำไมต้อง generate: 36 บท · 151 หัวข้อ — เขียนมือแล้วลืมอัปเดตเมื่อไร สารบัญจะโกหก
โดยไม่มีใครรู้ · ครั้งแรกที่รันก็เจอทันทีว่าหัวข้อ 24.1 ยังเขียนตัวเลขเก่าอยู่

⚠️ **`<details>` ต้องใส่ `open`** — ถ้าปิดอยู่จะพิมพ์ลง PDF แค่บรรทัดเดียว และ
`@media print{...display:block!important}` **เอาชนะ UA stylesheet ของ `<details>` ไม่ได้**

⚠️ **`re.sub` ที่ replacement เป็น HTML/ข้อความไทย ต้องส่ง `lambda _: text`** —
ส่ง string ตรง ๆ จะโดนตีความ `\` เป็น escape แล้วโยน `bad escape`

## ⚠️ กับดักที่เจอซ้ำ — regex ที่ครอบหลาย entry

ตอนแก้ back-reference ใน `python-appendix.html` เขียน

```python
re.sub(r'<div class="gloss-term">(.*?)</div>.*?<div class="gloss-ref">(.*?)</div>', ...)
```

`.*?` ตรงกลาง**ข้าม `</div>` ไปจับ ref ของ entry ถัดไป** → ตั้งใจแก้ 14 คำ
แต่ไปเขียนทับ 24 คำ รวมถึงคำที่ชี้ถูกอยู่แล้ว (Mean · Correlation · Hedge Ratio)

**วิธีที่ถูก:** ตัดเป็น entry ก่อนด้วย `re.sub(r'<div class="gloss-entry">.*?\n</div>', fn, ...)`
แล้วค่อยแก้ *ภายใน* แต่ละ entry · เป็นกับดักเดียวกับที่ `check-output.py` เจอ
(จับคู่ `.fm` กับ `.output` ข้ามบล็อก) — **ทุกครั้งที่ regex ต้องเดินข้ามหลายก้อน
ให้แยกก้อนก่อนเสมอ**
