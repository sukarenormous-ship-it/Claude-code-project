# กราฟ & ภาพประกอบ — ให้ "สวย" โดยยังเป็น inline SVG ล้วน

หนังสือชุดนี้ใช้ **inline SVG วาดมือ** ทุกภาพ (108+ ชิ้น) — ห้ามเปลี่ยนไปใช้ chart library, `<canvas>`, หรือรูป raster เพราะจะพัง PDF export / offline / self-contained ทั้งหมด **ความสวยทำได้เต็มที่ภายใน SVG อยู่แล้ว** ไฟล์นี้คือวิธีทำ

> เดโมเทียบ before/after: `assets/chart-demo.html` (payoff long call) — เปิดดูก่อนลงมือ

## หลัก 7 ข้อ (ไล่ตามลำดับ — สีมาท้ายสุด)

1. **เลือกรูปแบบตามหน้าที่ของข้อมูล** — payoff/curve = เส้น+area; เทียบค่า = bar; สัดส่วน = เลขเด่น/แท่งเดียว ไม่ใช่ทุกอย่างต้องเป็นกราฟ
2. **สีตามความหมาย ไม่ใช่ตามลำดับ** — ใช้ palette เดิมของเล่ม: 🟢`--green`=กำไร/ดี · 🔴`--red`=ขาดทุน/พัง · 🔵`--blue`=เส้นหลัก/กลาง · 🟣`--purple`=จุดสำคัญ/insight · 🟡`--amber`=เตือน/หมายเหตุ
3. **grid & แกนถอยหลัง (recessive)** — grid `#e5e7eb` เส้นบาง, แกน `#cbd5e1`–`#9ca3af`; ข้อมูลต้องเด่นกว่าโครง
4. **มาร์กบาง ปลายมน** — เส้นหลัก `stroke-width:2.5–2.75` + `stroke-linecap/linejoin:round`; เส้นอ้างอิงบางกว่า+ประ (`stroke-dasharray:4 4`)
5. **เติม hover เฉพาะฉบับ HTML** (option) — PDF เห็นเป็นเฟรมนิ่ง จึงต้อง**สวยตั้งแต่สถานะนิ่ง**ก่อนเสมอ
6. **accessibility** — ≥2 ซีรีส์ต้องมี legend + ไม่พึ่งสีอย่างเดียว (ใช้เส้นทึบ/ประ หรือ label กำกับ); contrast พอ; ระวังโหมดมืด (ดูล่าง)
7. **render แล้วดูจริง** — screenshot ด้วย Playwright เช็ค label ชนกัน/ล้นกรอบ ก่อนถือว่าเสร็จ (validator เช็คสีได้ แต่ไม่เช็ค layout)

## เครื่องมือความสวย (เพิ่มเข้า SVG เดิมได้ทีละชิ้น)

วาง `<defs>` ครั้งเดียวต่อ SVG (หรือรวมไว้ต้นไฟล์แล้วอ้าง id ซ้ำ):

```html
<defs>
  <!-- area ไล่เฉดใต้เส้น: จางลงเข้าหา baseline -->
  <linearGradient id="gUp" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#16a34a" stop-opacity="0.34"/>
    <stop offset="1" stop-color="#16a34a" stop-opacity="0.03"/></linearGradient>
  <linearGradient id="gDn" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#dc2626" stop-opacity="0.04"/>
    <stop offset="1" stop-color="#dc2626" stop-opacity="0.28"/></linearGradient>
  <!-- เงานุ่มใต้เส้นหลัก (สีเดียวกับเส้น) -->
  <filter id="soft" x="-20%" y="-20%" width="140%" height="140%">
    <feDropShadow dx="0" dy="1.5" stdDeviation="1.6" flood-color="#2563eb" flood-opacity="0.28"/></filter>
</defs>
```

### 1) area fill ใต้เส้น (ผลเยอะสุด)
ปิด polygon ระหว่างเส้นข้อมูลกับ baseline แล้วเติม gradient:
```html
<path d="M60,180 L60,210 L244,210 L306,180 Z" fill="url(#gDn)"/>   <!-- โซนขาดทุน -->
<path d="M306,180 L490,90 L490,180 Z"          fill="url(#gUp)"/>   <!-- โซนกำไร -->
```

### 2) เส้นหลัก = hero (เด่น + เงา + ปลายมน)
```html
<path d="M60,210 L244,210 L490,90" fill="none" stroke="#2563eb"
      stroke-width="2.75" stroke-linecap="round" stroke-linejoin="round" filter="url(#soft)"/>
```

### 3) callout ชี้จุดสำคัญ (แทน label ลอย)
```html
<!-- จุดคุ้มทุน: วงกลมกลวง + ป้ายโค้งชี้ -->
<circle cx="306" cy="180" r="4.5" fill="#fff" stroke="#7c3aed" stroke-width="2.5"/>
<path d="M306,180 C330,150 346,150 360,150" fill="none" stroke="#7c3aed" stroke-width="1"/>
<text x="364" y="153" font-size="9.5" fill="#7c3aed" font-weight="700">จุดคุ้มทุน 110</text>
<!-- ค่าสำคัญ: เส้นประดิ่ง + จุด + ป้าย -->
<line x1="150" y1="210" x2="150" y2="232" stroke="#dc2626" stroke-width="1" stroke-dasharray="2 2"/>
<circle cx="150" cy="210" r="3" fill="#dc2626"/>
<text x="150" y="246" text-anchor="middle" font-size="9.5" fill="#dc2626" font-weight="600">ขาดทุนสูงสุด = ฿10</text>
```

### 4) grid ถอยหลัง
```html
<g stroke="#e5e7eb" stroke-width="1">
  <line x1="60" y1="120" x2="490" y2="120"/><line x1="60" y1="150" x2="490" y2="150"/></g>
```

## Convention ที่ต้องคุมให้ตรงทั้งเล่ม

- **viewBox + responsive:** `<svg viewBox="0 0 520 300" ...>` + CSS `svg{width:100%}` หรือ `style="width:100%;max-width:520px;display:block;margin:20px auto"` — อย่า hardcode `width`/`height` px
- **ฟอนต์ label:** `font-family="Sarabun"` (มีในหน้าอยู่แล้ว) ขนาด 9–13; หัวกราฟ `font-weight:700`
- **ตัวเลข/label สวมสี "หมึก" ไม่ใช่สีซีรีส์** — ข้อความทั่วไปใช้ `#374151/#6b7280`; ให้ "มาร์กสี" ข้าง ๆ เป็นตัวบอก identity แทน (ยกเว้น label ที่จงใจสื่อความหมาย เช่น "กำไร" สีเขียว)
- **ห้ามกราฟ 2 แกน y** (dual-axis) — ถ้าหน่วยต่างกันให้แยกเป็น 2 กราฟ
- **1 กราฟ = 1 ประเด็น** — ให้ callout ชี้ "สิ่งที่อยากให้เห็น" ตรงกับข้อความในการ์ด

## PDF & โหมดมืด

- **PDF:** `feDropShadow`/gradient/opacity render ผ่าน Playwright + `printBackground:true` ได้ครบ — ตรวจด้วย `scripts/render-pdf.mjs` เสมอหลังแก้ภาพ
- **โหมดมืด:** หนังสือพื้นขาวคงที่ (ไม่มี dark mode) จึงไม่ต้องทำ dark variant ของ SVG; แต่ถ้าอนาคตทำ ให้เลือกสเต็ปสีใหม่เทียบ surface มืด **อย่า invert อัตโนมัติ**
- ถ้าต้องการเช็คสีชุดใหม่ว่า colorblind-safe/contrast ผ่านไหม ใช้ validator ของ dataviz skill: `node scripts/validate_palette.js "<hex,...>" --mode light`
