Stat Arb for Non Quant — Markdown ฉบับ 0.9

เปิด Stat_Arb_for_Non_Quant_Part_I_v0_9.md เพื่ออ่านเนื้อหาหลัก
ฉบับ 0.9 เขียนบท 6 และ 7 ทั้งบท ทำให้บท 0–10 (ภาค 1–2) อ่านต่อเนื่องได้ครบ
ดูรายการทั้งหมดใน CHANGELOG_v0_9.md (ฉบับก่อนหน้าอยู่ใน CHANGELOG_v0_6.md ถึง CHANGELOG_v0_8.md)
ไฟล์หลักรวมบท 0–10 ที่เขียนแล้ว แผนบท 0–20 กรณีศึกษา 14 ชุด และแหล่งอ้างอิง 48 รายการ
บท 11–20 ยังเป็นแผน บท 8 และ 10 เขียนแล้วบางส่วน

การเปิดพร้อมภาพ
1. แตก ZIP ทั้งชุด
2. เก็บโฟลเดอร์ figures และ code ไว้ข้างไฟล์ Markdown
3. เปิดด้วยโปรแกรมที่รองรับ Markdown และ LaTeX math
4. รูปใช้ relative paths จึงย้ายทั้งโฟลเดอร์ไปที่อื่นได้

สมการ inline ใช้ $...$ และ display ใช้ $$...$$; ตารางใช้ GitHub-flavored Markdown
ลิงก์สารบัญและอ้างอิงใช้ HTML anchors การรองรับขึ้นกับโปรแกรมที่เปิด

ไฟล์ประกอบ
- CHANGELOG_v0_6.md ถึง CHANGELOG_v0_9.md: รายการแก้ไข เนื้อหาที่เสริม และงานที่ยังค้าง
- Stat_Arb_Chapter_Template_v0_5.md: แม่แบบบท (ไม่เปลี่ยนจากฉบับ 0.5)
- Stat_Arb_Source_Plan_v0_5.md: รายละเอียดแผนต้นฉบับ (ไม่เปลี่ยนจากฉบับ 0.5)
- figures/: รูป 22 คู่ PNG/SVG; ฉบับ 0.9 เพิ่ม carry_ladder, funding_scenarios, corr_vs_coint และ selection_bias; รูปใหม่ 4 รูปคือ tail_risk, margin_cash, hedge_compare, first_passage
  และ mr_moving_mean ถูกวาดใหม่ให้ใช้สัญลักษณ์ X
- code/: สคริปต์สาธิตเดิม 5 ไฟล์พร้อมผล JSON, v06_enrichment_demo.py พร้อมผล JSON
  v06_figures.py สำหรับสร้างรูปของฉบับ 0.6 (ไฟล์นี้ต้องใช้ matplotlib) v07_primer_checks.py พร้อมผล JSON
  v09_ch06_ch07_demo.py พร้อมผล JSON และ v09_figures.py (ต้องใช้ matplotlib)

ตัวอย่างเป็นข้อมูลสมมติเพื่อตรวจแนวคิด หน่วย และบัญชี ไม่มีการส่งคำสั่งซื้อขาย
ตัวเลขใหม่ของฉบับ 0.6 ตรวจด้วย v06_enrichment_demo.py แล้ว; โค้ดภายนอกและผล paper ยังไม่ได้รันทำซ้ำ
