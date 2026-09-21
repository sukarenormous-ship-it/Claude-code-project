# Historical Price Fetcher

สคริปต์ Python สำหรับดึงราคาย้อนหลัง (OHLCV candles) จาก **Bybit** หรือ **Binance**
ผ่าน public API — ไม่ต้องใช้ API key และไม่ต้องติดตั้ง package เพิ่ม (ใช้ standard library ล้วน ๆ)

## วิธีใช้

```bash
# แท่งเทียนรายวัน BTCUSDT จาก Binance ย้อนหลัง 7 วัน (แสดงบนจอ)
python3 fetch_prices.py --exchange binance --symbol BTCUSDT --interval 1d --days 7

# แท่งเทียน 1 ชั่วโมง ETHUSDT จาก Bybit ช่วงวันที่กำหนด บันทึกเป็น CSV
python3 fetch_prices.py --exchange bybit --symbol ETHUSDT --interval 1h \
    --start 2024-01-01 --end 2024-06-30 --output eth_1h.csv

# Bybit USDT perpetual (futures) แทน spot
python3 fetch_prices.py --exchange bybit --category linear --symbol BTCUSDT \
    --interval 4h --days 30 --output btc_perp_4h.csv
```

## Options

| Option | คำอธิบาย |
|---|---|
| `--exchange` | `binance` หรือ `bybit` (จำเป็น) |
| `--symbol` | คู่เทรด เช่น `BTCUSDT`, `ETHUSDT` (จำเป็น) |
| `--interval` | `1m 3m 5m 15m 30m 1h 2h 4h 6h 12h 1d 1w` (ค่าเริ่มต้น `1d`) |
| `--start` / `--end` | ช่วงวันที่ UTC เช่น `2024-01-01` (ถ้าไม่ใส่ end = ตอนนี้) |
| `--days` | ทางลัด: ดึงย้อนหลัง N วัน (ค่าเริ่มต้น 30 วันถ้าไม่ระบุ start) |
| `--category` | เฉพาะ Bybit: `spot` (ค่าเริ่มต้น), `linear` (USDT perp), `inverse` |
| `--output` | path ไฟล์ CSV; ถ้าไม่ใส่จะแสดง preview บนจอ |

## Output CSV

```
timestamp,datetime_utc,open,high,low,close,volume
1704067200000,2024-01-01 00:00:00,42283.58,44184.0,42180.77,44179.55,27174.28
```

- `timestamp` = เวลาเปิดแท่งเทียน (milliseconds, UTC)
- ดึงข้อมูลได้ยาวเท่าไหร่ก็ได้ — สคริปต์แบ่งหน้า (paginate) อัตโนมัติครั้งละ 1,000 แท่ง
  พร้อมหน่วงเวลาเล็กน้อยเพื่อไม่ให้ชน rate limit และ retry อัตโนมัติเมื่อ network มีปัญหา

## ใช้ต่อกับ pandas

```python
import pandas as pd
df = pd.read_csv("eth_1h.csv", parse_dates=["datetime_utc"], index_col="datetime_utc")
df["close"].plot()
```
