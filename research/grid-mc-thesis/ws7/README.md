# WS7 — BTCUSDT 1m Discovery tools

เครื่องมือสำหรับ WS7 ของ AIGR (Discovery 2018–2023 เท่านั้น — 2024+ **SEALED**)

| ไฟล์ | หน้าที่ |
|---|---|
| `ingest_binance.py` | ingestion gate ตาม handoff §10: ZIP ทางการ → checksum → integrity → schema → monotonic → duplicates → coverage → gap manifest → OHLC → canonical `.npz` + provenance manifest |
| `scale_structure.py` | WS7-A: โครงสร้าง mean reversion ตามสเกล spacing δ (0.25–8%, log) เทียบ surrogate |
| `test_ws7.py` | fixture ออฟไลน์ 13 ข้อ (`python3 test_ws7.py`) |

ต้องการ Python 3.10+ และ `numpy`

## ขั้นตอน

```bash
pip install numpy
python3 test_ws7.py                                   # ต้องผ่าน 13/13

# 1) ingestion — ต้องเข้าถึง data.binance.vision ได้
python3 ingest_binance.py --start 2018-01 --end 2023-12 --out data/
#    หรือถ้าดาวน์โหลด ZIP + .CHECKSUM เองไว้ในโฟลเดอร์เดียว:
python3 ingest_binance.py --start 2018-01 --end 2023-12 --out data/ --source-dir /path/to/zips

# 2) WS7-A scale structure (~6 นาทีที่ 50 surrogates/ชนิด)
python3 scale_structure.py --data data/canonical --out results/ws7a
```

ผลลัพธ์: `data/provenance_manifest.csv`, `data/gap_manifest.csv`, `data/ingest_summary.json`,
`results/ws7a/summary.md`, `grid_scale.csv`, `variance_ratio.csv`, `meta.json` (มี sha256 ของข้อมูล)

## กติกาที่โค้ดบังคับ

- เดือน ≥ 2024-01 ถูกปฏิเสธก่อนมี I/O ใดๆ; `scale_structure.py` ปฏิเสธ canonical data ที่มี timestamp ≥ 2024-01-01
- ไม่ forward-fill: นาทีที่หายอยู่ใน gap manifest; return ข้าม gap ไม่ถูกสลับใน surrogate
- checksum ไม่ตรง / duplicate ที่ค่าขัดกัน / OHLC ผิด → เดือนนั้น FAIL และไม่ถูกเขียนเป็น canonical

## วิธีอ่านผล WS7-A

- **ตัวตัดสินโครงสร้าง = `p_rev` z-score** ความน่าจะเป็นที่ step ระหว่าง level ถัดไปกลับทิศ
  (`p_up_after_down` = H(1) เชิงประจักษ์ที่ spacing δ) เทียบ surrogate ที่มี |การเคลื่อนไหว| เท่าเดิมแต่เครื่องหมายสุ่ม
  z ≫ 0 ที่ δ ใด = ราคาแกว่งกลับระหว่าง level ที่ spacing นั้นมากกว่า random walk
- `gross / timing / sawtooth` = ขนาดเชิงเศรษฐกิจของ trailing-envelope grid (ลึก 60% ใต้ running max แบบ lab)
  มี power ต่ำสำหรับโครงสร้างสเกลเล็ก เพราะ drawdown ใหญ่ครอบงำ — ใช้ดูขนาด ไม่ใช้ตัดสิน
- `timing` ใช้ ē แบบ ex-post ซึ่ง bias ขึ้นแม้ภายใต้ martingale → เทียบกับ surrogate เท่านั้น ห้ามเทียบกับ 0
- เป็น process statistic (close-to-close, frictionless) **ไม่ใช่ backtest** และไม่ใช้เลือกพารามิเตอร์

## ข้อค้นพบเชิงวิธีการระหว่างสร้าง (ยืนยันด้วย fixture)

1. **จำนวน cycle/crossing ไม่ใช่ตัววัด mean reversion** — ถูกกำหนดโดย quadratic variation ที่สเกล δ
   ซึ่ง surrogate คงไว้; บน fixture OU (half-life 6h, std 2%) ratio จริง/surrogate ≈ 0.99
2. **ห้ามสลับ returns ภายใน window คงที่** — ตรึงราคาต้น/ท้ายทุก window = ใส่ mean reversion เข้าไปใน null
   ซึ่ง grid เก็บเกี่ยวได้พอดี → null เข้าข้าง grid
3. **"recross" ต้องนับแบบ level-to-level** — ถ้านับการข้าม level เดิมซ้ำ p_rev ≈ 0.83–0.98 แม้เป็น random walk
