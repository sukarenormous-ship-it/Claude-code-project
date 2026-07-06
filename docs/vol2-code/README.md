# vol2-code — โค้ดรันได้จริงคู่กับ "Practical Quant: Stat Arb"

## ⚠️ เรื่องข้อมูล — ทำไมเป็น simulated ไม่ใช่ราคาจริง

สภาพแวดล้อมที่ใช้เขียน/รันโน้ตบุ๊กชุดนี้บล็อกการเชื่อมต่อไปยัง data provider ทางการเงินทุกเจ้า
(Yahoo Finance, Stooq — ทดสอบแล้วทั้งคู่ถูกนโยบาย network ปฏิเสธ) ทุกโน้ตบุ๊กจึงใช้
**ข้อมูลจำลอง (simulated) ที่มี data-generating process (DGP) ที่รู้และเปิดเผยชัดเจน** แทน
(ดู `simdata.py`)

นี่ไม่ใช่แค่ทางออกเมื่อจนตรอก — สำหรับ**ทดสอบ estimator** มันดีกว่าราคาจริงด้วยซ้ำ เพราะเรารู้
β จริง / spread จริง / factor loading จริง จึงวัด bias ของแต่ละวิธีได้ตรง ๆ ราคาตลาดจริงไม่เคยให้
ground truth แบบนี้

ถ้าอยากรันกับราคาจริง: แก้แค่ `simulate_cointegrated_pair()` / `simulate_factor_universe()`
ในแต่ละโน้ตบุ๊กให้ดึงราคาของคุณเอง (broker API, ไฟล์ CSV ในเครื่อง ฯลฯ) — โค้ดส่วน estimator
(OLS/TLS/Kalman/PCA/copula) ไม่สนใจที่มาของราคา

## ไฟล์

| ไฟล์ | คู่กับ | มีอะไร |
|---|---|---|
| `simdata.py` | — | ตัวสร้างข้อมูลจำลอง (DGP มี seed, reproduce ได้ 100%) |
| `01_beta_ladder.ipynb` | Part I | OLS(price) vs OLS(return) vs TLS vs Rolling vs Kalman — วัด bias/RMSE จริง |
| `02_cointegration_copula.ipynb` | Part II | Engle-Granger ที่ถูก vs ผิด, half-life, Hurst, multiple-testing simulation, Gaussian-copula MI |
| `03_factor_residual.ipynb` | Part III | PCA หัก factor, s-score cross-sectional, เช็ค residual สะอาด |
| `build_nb0{1,2,3}.py` | — | สคริปต์ที่ "เขียน" ตัวโน้ตบุ๊ก (source of truth — แก้ตรงนี้ ไม่แก้ .ipynb JSON ตรง ๆ) |

## รัน / แก้ไขซ้ำ

```bash
pip install -r requirements.txt

# แก้เนื้อหาแล้ว rebuild + execute ใหม่:
python3 build_nb01.py
python3 -c "
import nbformat
from nbclient import NotebookClient
nb = nbformat.read('01_beta_ladder.ipynb', as_version=4)
NotebookClient(nb, timeout=120, kernel_name='python3').execute()
nbformat.write(nb, '01_beta_ladder.ipynb')
"
```

(ถ้าไม่มี kernel ชื่อ `python3` ให้รันครั้งแรกด้วย `python3 -m ipykernel install --user --name python3`
หรือใช้ชื่อ kernel ที่มีอยู่ในเครื่องคุณแทน)

## ⚠️ ข้อจำกัดที่ต้องรู้ก่อนใช้ตัวเลขจากโน้ตบุ๊กเหล่านี้

- ตัวเลขทั้งหมด**ไม่มี transaction cost / capacity / borrow constraint** — เป็นการสาธิตกลไกทางสถิติ
  ล้วน ๆ ไม่ใช่ backtest กลยุทธ์พร้อมเทรดจริง (ส่วนนั้นอยู่ Part VI–IX)
- ตัวเลขที่ printed ในแต่ละ cell **ผูกกับ seed ที่ระบุไว้** — เปลี่ยน seed แล้วตัวเลขจะขยับ
  (แต่ข้อสรุปเชิงคุณภาพควรเสถียร — ถ้าไม่เสถียรคือสัญญาณว่ามีอะไรผิดปกติ ให้สงสัยไว้ก่อน)
- ระหว่างสร้างชุดนี้ เจอบั๊กจริง 2 จุดที่แก้แล้วและได้กลายเป็นบทเรียนในตัวโน้ตบุ๊กเอง:
  (1) สูตร Hurst exponent ที่คูณ 2 ผิดที่ (2) ใช้ `adfuller()` ตรง ๆ บน residual แทนที่จะใช้
  `coint()` ทำให้ false-positive rate เพี้ยนไปเกือบ 3 เท่า — ทั้งสองเรื่องนี้คือกับดักที่คนเขียนโค้ด
  Engle-Granger/Hurst มือใหม่เจอได้จริง ไม่ใช่แค่ในทฤษฎี
