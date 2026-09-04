---
name: knowledge-book
description: >-
  Write or extend the Thai self-contained HTML "knowledge book" chapters used in
  this repo (docs/*.html — e.g. the "ทฤษฎีของ Quant" volumes: theory-part*, pillars-part*,
  math/pm/arb/eye series). Use whenever the user asks to สร้าง/เขียน/ต่อ/ปรับปรุง หนังสือ,
  บท, Part, การ์ดทฤษฎี, เอกสารสอน, or a chapter/lesson document; or to review one to the
  book's craft standard, or export chapters to PDF. Encodes the card anatomy, Thai
  typography rules, v4 craft standard, expert-panel review loop, and PDF pipeline that
  evolved across past chats in this project.
---

# Knowledge Book — วิธีทำ "หนังสือ" ของโปรเจกต์นี้

โปรเจกต์นี้สะสมวิธีทำหนังสือสอนแบบ **HTML self-contained ภาษาไทย** ที่ผ่านการรีวิวหลายรอบจนได้มาตรฐาน "งานฝีมือ v4" สกิลนี้คือวิธีทำนั้น เพื่อให้บทใหม่/หนังสือเล่มใหม่ออกมาคุณภาพเดียวกันตั้งแต่ร่างแรก

หนังสือที่มีอยู่ (`docs/`): เล่ม A `theory-part1..6` + เล่ม B `pillars-part1..5` (ทฤษฎีของ Quant), และซีรีส์เดิม `math-` `pm-` `arb-` `eye-`, หน้ารวม `index.html` + `notation.html`

## ทำอะไรได้บ้าง (เลือกตามที่ผู้ใช้ขอ)

| ผู้ใช้ขอ | ทำอะไร |
|---|---|
| เขียนบท/Part ใหม่ | คัดลอก `assets/template.html` → เขียนตามการ์ด 9 องค์ประกอบ → รีวิว → commit |
| ต่อ/แก้บทเดิม | อ่านไฟล์เดิม, คงสไตล์เป๊ะ, แก้ตามที่ขอ, รักษากฎ typography |
| รีวิวให้ได้มาตรฐาน | รันคณะผู้เชี่ยวชาญตาม `references/craft-standard.md` |
| ออก PDF | รัน `scripts/render-pdf.mjs` |

## ขั้นตอนเขียนบทใหม่

1. **ดูของเดิมก่อน** — อ่านไฟล์ `docs/*.html` ที่ใกล้เคียงหัวข้อ (โดยเฉพาะ `pillars-part1.html` = ต้นแบบ v4) เพื่อจับ voice/ความหนาแน่นจริง และเช็คว่าหัวข้อนี้มี "บ้าน" อยู่แล้วไหม (Write Once — ถ้ามีให้ *อ้างอิง* ไม่เขียนซ้ำ)
2. **เริ่มจาก `assets/template.html`** — มี CSS, palette, reading-path banner, โครงการ์ด และ Thai line-break script ครบ (คัดลอกไป `docs/<ชื่อบท>.html` ทำงานต่อ — **อย่าเขียน CSS/script ใหม่เอง**)
3. **เขียนแต่ละการ์ด = 1 แนวคิด** ตามลำดับ 9 องค์ประกอบใน `references/card-anatomy.md`
   - Thesis → ❓ทำไมต้องรู้ → 🔧ใช้ทำอะไร → ✅ใช้ได้เมื่อไร → ❌พังเมื่อไร → ⚖️ข้อดี/ข้อเสีย → 🧠มุมที่มองต่าง → 📍ปัจจุบัน → 📚Papers
   - การ์ด ★★★ เพิ่ม: 🚶อ่านเป็นภาษาคนก่อน (เหนือสูตร) + 🧮worked example + 🎯3 อย่างที่ต้องจำ
4. **ยึด Style Guide** (`references/style-guide.md`) — โดยเฉพาะ: รายการใช้ `<ul>` จริงห้าม `<br>` ปลอม, `.fm` เก็บเฉพาะสูตร, เว้นวรรครอบคำอังกฤษ
   - **กราฟ/ภาพประกอบ:** ทำเป็น inline SVG เสมอ (ห้าม chart library/canvas/รูป raster) ตาม `references/visual-guide.md` — area gradient, เส้นหลักมีเงา+ปลายมน, grid ถอยหลัง, callout ชี้จุดสำคัญ, สีตามความหมาย (เขียว=กำไร แดง=ขาดทุน ม่วง=จุดสำคัญ)
5. **ปิดตอน** — สรุป ✓ + `.pq` cliffhanger เชื่อม Part ถัดไป + 📖อ่านต่อ + 📖ศัพท์ใหม่ในตอนนี้
6. **รีวิว** ตาม `references/craft-standard.md` แล้วแก้ให้ครบ
6½. **รัน QA ก่อน commit ทุกครั้ง** — `python3 tools/lib_qa.py` (ทั้งคลัง) หรือ `python3 tools/lib_qa.py <ชื่อบท>` · ตรวจ tag balance, บล็อก "📖 อ่านสูตรว่า", ลิงก์/anchor ภายในทุกตัว, banner 🧭, script ตัดคำ · ต้องได้ "ข้อผิดพลาด 0" · หนังสือ "คิดแบบ Quant" รันเพิ่ม `python3 tools/nq_qa.py` และ `python3 tools/nq_check_figures.py` · ชุดคณิตศาสตร์เล่ม 2 รัน `python3 tools/math_figures.py` (คำนวณตัวเลขทุกตัวอย่างใหม่แล้วเทียบกับข้อความ — ต้อง "ไม่ตรง 0") · หลังเพิ่ม/แก้บล็อก 📖 รัน `python3 tools/symbol_index.py` เพื่ออัปเดตดัชนีสัญลักษณ์ใน notation หมวด 0
7. **commit แยกต่อ Part** (`docs: <เล่ม> Part N — ร่างก่อนรีวิว` → `... ผ่านรีวิว N คน — แก้ครบ`) แล้ว push

## กฎที่พลาดไม่ได้ (สรุปจากบทเรียนจริง)

- **สัญชาตญาณมาก่อนสูตรเสมอ** — ทุกกล่องสูตรมี "🚶 อ่านเป็นภาษาคนก่อน" นำ
- **"พังเมื่อไร" (เทคนิค) ≠ "ข้อเสีย" (trade-off)** — ห้ามซ้ำกัน
- **ห้าม hallucinate** paper/เกร็ด/ตัวเลข — ไม่มั่นใจให้ตัด
- **Write Once, Reference Everywhere** — ใช้ notation กลาง, cross-ref ไฟล์เดิมแทนเขียนซ้ำ
- **โครงสร้าง HTML จริง** — `<ul>/<ol>/<p>` ไม่ใช่ `<br>` ปลอม (ตัวการทำบรรทัดไทยตัดกลางคำ)
- **อย่าแตะ Thai line-break `<script>`** ท้ายไฟล์ — คัดจาก template ตามเดิม

## ออก PDF

```bash
node .claude/skills/knowledge-book/scripts/render-pdf.mjs docs          # ทุกไฟล์ใน docs/
node .claude/skills/knowledge-book/scripts/render-pdf.mjs docs pillars-part1 theory-part2   # เจาะจง
```
ผลออกที่ `docs/pdf/<ชื่อ>.pdf` (A4, พื้นหลังสี, ตัดคำไทยเหมือนเบราว์เซอร์) — ต้องมี Playwright + Chromium (ติดตั้งไว้แล้วในสภาพแวดล้อมนี้ อย่ารัน `playwright install`)

## ไฟล์ในสกิลนี้

- `assets/template.html` — โครง HTML + CSS + การ์ดตัวอย่าง + line-break script (จุดเริ่มของทุกบท)
- `assets/chart-demo.html` — เดโม before/after ของกราฟ (payoff long call) ให้ดูก่อนทำภาพ
- `references/card-anatomy.md` — การ์ด 9 องค์ประกอบ + mini-card + ป้ายกำกับ + density
- `references/style-guide.md` — typography ไทย + โครงสร้าง HTML + การเขียน + palette
- `references/visual-guide.md` — กราฟ/ภาพประกอบ inline SVG ให้สวย (gradient/เงา/callout/grid) + snippet พร้อมใช้
- `references/craft-standard.md` — มาตรฐาน v4 + กระบวนการรีวิวคณะผู้เชี่ยวชาญ + consistency rules
- `scripts/render-pdf.mjs` — export HTML → PDF ด้วย Playwright
