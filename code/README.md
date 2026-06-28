# โค้ดคู่มือ — Pairs Trading Starter

โค้ดประกอบ **Arbitrage Part V: Statistical Arbitrage (บท 18–21)**
ออกแบบให้ **รายย่อยรันได้จริง** ด้วยข้อมูลฟรีและไลบรารีโอเพนซอร์ส

> ⚠️ **เพื่อการศึกษา ไม่ใช่คำแนะนำการลงทุน** — backtest/ผลในอดีตไม่รับประกันอนาคต
> และการ short มีความเสี่ยงขาดทุนไม่จำกัด + margin call + ค่ายืมหุ้น (borrow) รายวัน

## รัน (ทางเลือกที่ง่ายที่สุด: ไม่ต้องลงอะไรในเครื่อง)

เปิด [Google Colab](https://colab.research.google.com) → สร้าง notebook ใหม่ →
เซลล์แรกพิมพ์ `!pip install yfinance statsmodels` → วางโค้ดจากไฟล์นี้แล้วกด Run

## รัน (ในเครื่องตัวเอง)

```bash
pip install -r requirements.txt
python pairs_trading_starter.py KO PEP      # คู่ Coke vs Pepsi (ค่าเริ่มต้น)
python pairs_trading_starter.py XLE XOP     # ETF พลังงาน 2 ตัว
```

## สิ่งที่โปรแกรมทำ (ตาม workflow ในหนังสือ)

ประเมินพารามิเตอร์บนช่วง **train** แล้ววัดผลบน **out-of-sample (OOS)** เพื่อกัน look-ahead:

| ขั้น | สิ่งที่ได้ | เกณฑ์ผ่าน |
|---|---|---|
| 1. Cointegration | p-value (train) | < 0.05 |
| 2. Hedge ratio β | จาก OLS (train) | — |
| 3. Half-life | (train) | **5–30 วัน** |
| 4. สัญญาณ Z-score | rolling | entry ±2, exit \|Z\|<0.5, stop ±4 |
| 5. Sharpe | in-sample เทียบ **OOS** | OOS > 1 (อย่าเชื่อ > 3); ถ้า IS ≫ OOS = overfit |
| 6. **สัญญาณวันนี้** | Long/Short/Exit/รอ | เอาไปจดใน paper-trade log ทุกวัน |

บรรทัด `[6] สัญญาณวันนี้` คือสิ่งที่ใช้ paper trade: รันทุกเย็นหลังตลาดปิด → จดสัญญาณลงชีต

## ⚠️ ข้อจำกัด (อ่านก่อนใช้)

- ข้อมูล Yahoo ฟรีมี **survivorship bias** (ไม่เห็นหุ้นที่ถูกถอด/เจ๊ง) → backtest ดูดีเกินจริง อย่าเชื่อตัวเลขเป๊ะๆ
- โมเดล cost เป็นค่าประมาณ (`cost_bps`, `borrow_bps_annual`) — ต้นทุนจริงของรายย่อยอาจสูงกว่า โดยเฉพาะค่ายืมหุ้นเล็ก
- การ split train/test แบบนี้เป็น walk-forward อย่างง่าย (ครั้งเดียว) — ของจริงควร re-estimate เป็นรอบๆ
- คู่ตัวอย่างเป็น **หุ้นสหรัฐ** — การ short ต้องใช้โบรกเกอร์ที่รองรับ margin/short หุ้นสหรัฐ (บัญชีไทย long-only ทำไม่ได้); ช่วง paper trade ไม่ต้องมีบัญชีก็ได้ แค่จดสัญญาณ
- Backtest **ไม่ใช่** การพิสูจน์กำไร — paper trade ≥ 2–3 เดือน (≥20–30 สัญญาณ) ก่อน แล้วค่อย size เล็ก ≤ 1–2%/คู่ ด้วยเงินที่เสียได้

อ่านพื้นฐานทฤษฎี + หลักฐานวิจัยได้ที่ `docs/arb-part5.html` (บท 18–21)
