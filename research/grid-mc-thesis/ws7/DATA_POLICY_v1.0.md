# WS7 Data Policy v1.0 — exchange-event anomalies

**สถานะ:** ACCEPTED โดยผู้วิจัย (2026-09-27) · ใช้กับ BTCUSDT Spot 1m 2018-01 → 2023-12 (Discovery)
**เหตุผล:** QC ของทั้งสอง pipeline (ผู้วิจัย `btc_discovery/RUN_STATUS.json` = FAIL และ `ingest_binance.py` รอบแรก)
พบ anomaly ชุดเดียวกัน 1,214 แถว; `SOURCE_DATA_SPEC_TH.md` กำหนดว่าต้องมี "separately accepted data policy" ก่อน Stage 1

## Cross-validation ของแหล่งข้อมูล

- ZIP ทั้ง 72 ไฟล์ใน bundle ของผู้วิจัย **ตรงกันทุกไบต์** กับที่ `ingest_binance.py` ดาวน์โหลดเอง; checksum ตรงกับไฟล์ `.CHECKSUM` ที่ Binance เผยแพร่ทุกไฟล์
- จำนวน anomaly ตรงกัน: 1,214 (off-grid open 1,201 รวม 1 แถวที่มีทั้งสองปัญหา · close_time ≠ open+59999 จำนวน 13)
- ไม่มีข้อมูล 2024+ ใน bundle และไม่มีการดาวน์โหลด 2024+

## นโยบาย: Keep, flag and snap

| ชนิด | จำนวน | การจัดการ |
|---|---|---|
| `offset_snapped` — แท่งหลัง restart 2018-02-09 09:59 → 2018-02-10 05:59 UTC บน offset +14.789 s, spacing 60 s | 1,201 | ปัด `open_time` ลงเป็นนาที (timing error < 1 แท่ง), **ไม่แก้ราคา/volume** |
| `partial_bar` — แท่งสุดท้ายก่อน exchange หยุด, open ตรงนาที, close_time สั้น | 12 | เก็บตามเดิม |
| `close_time_anomaly` — close_time ผิดรูปแบบ (2020-12) | 1 | เก็บตามเดิม |

- ทุกแถวอยู่ใน `anomaly_manifest.csv`; เดือนที่มี anomaly = CONDITIONAL
- ห้าม forward-fill; นาทีที่หาย (8,065) อยู่ใน `gap_manifest.csv`; engine ไม่สร้าง crossing ภายในช่วงที่หาย
- กรณีใดไม่เข้ารูปแบบข้างบน = FAIL (ต้องมีนโยบายใหม่)
- Canonical dataset sha256: `9d854236c9bf9a4fbfc698c11d3a52142e0040c49bbfded7e54e2281fc681676`

## ผลต่อ gate

ด้วยนโยบายนี้ ingestion = 72 เดือน, PASS 48 / CONDITIONAL 24 / FAIL 0 → admitted สำหรับ Stage 1 (WS7-B)
การเปลี่ยนนโยบายภายหลังต้องออกเวอร์ชันใหม่และรันผลที่ได้รับผลกระทบใหม่ทั้งหมด
