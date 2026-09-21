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
| `04_kalman_tuning.ipynb` | Part IV–V | Q/R plateau-vs-peak, innovation whiteness, MLE/EM, AR(1) vs random-walk β |
| `05_bands_and_costs.ipynb` | Part VI, VIII | full cost model (√-law impact), z vs cost-aware vs numerical-optimal band |
| `06_regime_killswitch.ipynb` | Part VII | structural break จำลอง, ชั้นเร็ว (disagreement) vs ชั้นช้า (coint re-test), stop-loss paradox |
| `07_full_backtest.ipynb` | Part IX | selection inflation (Monte Carlo), PBO (CSCV-lite), purged CV leakage demo |
| `build_nb0{1..7}.py` | — | สคริปต์ที่ "เขียน" ตัวโน้ตบุ๊ก (source of truth — แก้ตรงนี้ ไม่แก้ .ipynb JSON ตรง ๆ) |

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
- ระหว่างสร้างชุดนี้ เจอ **บั๊กจริง + ผลที่ไม่ตรงกับ "ตำรา"** หลายจุด ทุกจุดแก้แล้วและเก็บไว้เป็นบทเรียน
  ในตัวโน้ตบุ๊กเอง (ไม่ใช่แก้เงียบ ๆ) — เพราะการเห็นว่า "ทำไมผลไม่เป็นตามคาด" มีค่ากว่าตัวเลขที่สวยตามคาด:
  - **nb02**: (a) สูตร Hurst คูณ 2 ผิดที่ (random walk ได้ H≈0.95 แทน ~0.5) · (b) ใช้ `adfuller()` บน
    residual แทน `coint()` → false-positive พุ่งจาก ~12 เป็น ~44 (เกือบ 3 เท่า)
  - **nb04**: (a) innovation Ljung-Box reject ทั้ง Q ดี/แย่ (เพราะ sine ground truth ไม่ใช่ random walk)
    แต่ std(innovation) ยังแยกดี/แย่ได้ 17 เท่า · (b) AR(1) β แทบไม่ชนะ random-walk เลยแม้ ground truth
    มี "บ้าน" จริง — random-walk ที่จูน Q ดีก็เลียนแบบ mean-reversion ได้ในตัว
  - **nb06**: ชั้นเร็ว (disagreement) ยกธง 24 วัน *ก่อน* break จริง = false alarm จาก noise ไม่ใช่การจับล่วงหน้า
  - **nb07**: OLS purged-CV ไม่โชว์ leakage เลย (naive≈purged) เพราะ AR(1) มี coefficient เดียวทั่วอนุกรม —
    ต้องเปลี่ยนเป็น KNN + overlapping labels ถึงเห็น leakage ชัด (random R²=+0.22 vs purged R²=−0.13)
  - **nb04–07 build scripts**: escaping/quote bugs ในตัว generator script ที่จับได้ก่อน execute
