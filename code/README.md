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

| ขั้น | สิ่งที่ได้ | การตีความ |
|---|---|---|
| 1. Cointegration | p-value (train) จาก `coint()` | reject (<0.05) = หลักฐานแข็ง; ไม่ reject = ยัง**อ้าง**ไม่ได้ (ไม่ใช่ "ไม่มีแน่นอน") |
| 2. Hedge ratio β | จาก OLS (train) | — |
| 3. Half-life | (train) | **5–30 วัน** |
| 4. KPSS cross-check | null กลับด้าน (null=stationary) | p ≥ 0.05 = ไม่ขัด ✓; ADF/EG reject + KPSS ไม่ขัด = หลักฐานสองทาง |
| 4b. **ด่านหน่วยเงิน** | σ floor + edge filter | กันสัญญาณปลอมช่วงตลาดนิ่ง — z ถึงเกณฑ์แต่ระยะห่างสั้นเกินคุ้มค่าธรรมเนียม |
| 5. Sharpe | in-sample เทียบ **OOS** | OOS > 1 (อย่าเชื่อ > 3); ถ้า IS ≫ OOS = overfit |
| 6. **สัญญาณวันนี้** | Long/Short/Exit/รอ | เอาไปจดใน paper-trade log ทุกวัน |
| 7. **Evidence Tier** | 🔴 Reject / 🟡 Watchlist / 🔵 Research / 🟢 Trade candidate | verdict รวมทุกชั้น — ไม่ใช้ p-value เป็นสวิตช์ตัวเดียว |

บรรทัด `[6] สัญญาณวันนี้` คือสิ่งที่ใช้ paper trade: รันทุกเย็นหลังตลาดปิด → จดสัญญาณลงชีต

### ด่านหน่วยเงิน (`cost_bps`, `edge_k`) — แก้ปัญหา "3σ ที่ไม่มี headroom"

ช่วงที่ตลาดนิ่ง spread แคบ ค่า σ จะยุบตาม ทำให้ราคาขยับนิดเดียวก็แตะ 2–3σ — z-score เป็นค่า**ไม่มีหน่วย**
จึงมองไม่เห็นว่าระยะทางจริงสั้นเกินกว่าจะคุ้มค่าธรรมเนียม (Bollinger squeeze) โค้ดกันไว้ 2 ชั้น:

1. **σ floor** = 2 × ต้นทุนไป-กลับ → z ไม่พองเองตอน σ ยุบ
2. **edge filter** = `|spread − mean| ≥ 3 × ต้นทุนไป-กลับ` → ไม่เปิดสถานะใหม่ถ้าไม่คุ้ม (แต่ยังปิดสถานะเดิมได้)

บรรทัด `[4b]` จะรายงานว่าบล็อกสัญญาณที่ไม่คุ้มไปกี่วัน — ถ้าตัวเลขนี้สูงมาก แปลว่าคู่นี้ผันผวนน้อยเกินกว่าจะเทรดคุ้มต้นทุนของคุณ

> เชิงเทคนิค: ใช้ `coint()` เท่านั้นสำหรับ cointegration — ห้ามรัน `adfuller()` บน residual เอง
> เพราะ residual จาก OLS ต้องใช้ Engle–Granger/MacKinnon critical values (ติดลบมากกว่าปกติ)

## ⚠️ ข้อจำกัด (อ่านก่อนใช้)

- ข้อมูล Yahoo ฟรีมี **survivorship bias** (ไม่เห็นหุ้นที่ถูกถอด/เจ๊ง) → backtest ดูดีเกินจริง อย่าเชื่อตัวเลขเป๊ะๆ
- โมเดล cost เป็นค่าประมาณ (`cost_bps`, `borrow_bps_annual`) — ต้นทุนจริงของรายย่อยอาจสูงกว่า โดยเฉพาะค่ายืมหุ้นเล็ก
- การ split train/test แบบนี้เป็น walk-forward อย่างง่าย (ครั้งเดียว) — ของจริงควร re-estimate เป็นรอบๆ
- คู่ตัวอย่างเป็น **หุ้นสหรัฐ** — การ short ต้องใช้โบรกเกอร์ที่รองรับ margin/short หุ้นสหรัฐ (บัญชีไทย long-only ทำไม่ได้); ช่วง paper trade ไม่ต้องมีบัญชีก็ได้ แค่จดสัญญาณ
- Backtest **ไม่ใช่** การพิสูจน์กำไร — paper trade ≥ 2–3 เดือน (≥20–30 สัญญาณ) ก่อน แล้วค่อย size เล็ก ≤ 1–2%/คู่ ด้วยเงินที่เสียได้

อ่านพื้นฐานทฤษฎี + หลักฐานวิจัยได้ที่ `docs/arb-part5.html` (บท 18–21)
