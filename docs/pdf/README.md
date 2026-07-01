# PDF export — "ทฤษฎีของ Quant"

ไฟล์ PDF ของหนังสือทั้งสองเล่ม (เล่ม A + B) ทุกบท + หน้า index/notation/การ์ดเสริม

## สร้าง/อัปเดต PDF ใหม่

```bash
node docs/pdf/render-pdf.mjs
```

จะ render ทุกไฟล์ HTML ในโฟลเดอร์ `docs/` เป็น PDF (A4, พื้นหลังสี, ตัดคำไทยเหมือนในเบราว์เซอร์) มาไว้ที่ `docs/pdf/<ชื่อบท>.pdf`

ต้องมี Playwright + Chromium (ในสภาพแวดล้อมนี้ติดตั้งไว้แล้ว)

## รายการไฟล์ (14 บท)

| ไฟล์ | เนื้อหา |
|---|---|
| `index.pdf` | หน้าสารบัญรวม |
| `notation.pdf` | Notation Master Sheet |
| `theory-part1..6.pdf` | เล่ม A — ทฤษฎีตำนานของ Quant |
| `theory-extra.pdf` | การ์ดเสริม (Kelly, Momentum, Black-Litterman, Heston, SABR, Rough Vol/Deep Hedging) |
| `pillars-part1..5.pdf` | เล่ม B — เสาที่เหลือของ Quant |

## หมายเหตุ

ไฟล์ `.pdf` ถูก **gitignore** ไว้ (เป็น artifact ที่สร้างใหม่ได้ + ฟอนต์ Sarabun ฝังในทุกไฟล์ทำให้ขนาดรวมใหญ่ ~20 MB) — ถ้าต้องการเก็บ PDF เข้า git จริง ๆ ให้ลบบรรทัดใน `docs/pdf/.gitignore` ออก
