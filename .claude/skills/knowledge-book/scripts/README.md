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
