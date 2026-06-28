# โค้ดคู่มือ — Pairs Trading Starter

โค้ดประกอบ **Arbitrage Part V: Statistical Arbitrage (บท 18–21)**
ออกแบบให้ **รายย่อยรันได้จริง** ด้วยข้อมูลฟรีและไลบรารีโอเพนซอร์ส

## ติดตั้ง

```bash
pip install -r requirements.txt
```

## รัน

```bash
python pairs_trading_starter.py KO PEP      # คู่ Coke vs Pepsi (ค่าเริ่มต้น)
python pairs_trading_starter.py XLE XOP      # ETF พลังงาน 2 ตัว
```

โปรแกรมจะทำตาม workflow ในหนังสือให้อัตโนมัติ:

| ขั้น | ฟังก์ชัน | เกณฑ์ผ่าน |
|---|---|---|
| 1. Cointegration | `coint()` | p-value < 0.05 |
| 2. Hedge ratio β | `hedge_ratio()` | — |
| 3. Half-life | `half_life()` | 5–30 วัน |
| 4. สัญญาณ Z-score | `zscore()` | entry ±2, exit ~0, stop ±4 |
| 5. Backtest (มีต้นทุน) | `backtest()` | Sharpe **หลังหักต้นทุน** > 1 (อย่าเชื่อ > 3) |

## ⚠️ ข้อจำกัด (อ่านก่อนใช้)

- ข้อมูล Yahoo Finance ฟรีมี **survivorship bias** และไม่มีข้อมูล borrow/short — backtest จะ **มองโลกในแง่ดีเกินจริง**
- โมเดล cost เป็นค่าประมาณ (`cost_bps`) — ต้นทุนจริงของรายย่อยรวม spread + slippage + ค่ายืมหุ้น (borrow) อาจสูงกว่า
- Backtest **ไม่ใช่** การพิสูจน์ว่ากำไรจริง — ต้อง **paper trade ก่อน** แล้วค่อย size เล็กด้วยเงินที่เสียได้
- โค้ดนี้เพื่อ **การศึกษา** ไม่ใช่คำแนะนำการลงทุน

อ่านพื้นฐานทฤษฎี + หลักฐานวิจัยได้ที่ `docs/arb-part5.html` (บท 18–21)
