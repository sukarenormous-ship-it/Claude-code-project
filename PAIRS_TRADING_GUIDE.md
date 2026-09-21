# Pairs Trading ด้วย Kalman Filter — คู่มือทีม

> เอกสารสรุปการศึกษาและทดลอง statistical arbitrage / pairs trading
> ตั้งแต่งานวิจัยต้นทาง จนถึงเครื่องมือใช้งานจริง (`kalman_pairs.py`)
> ทดสอบบนข้อมูลจริง WTI–Brent (EIA spot, 2016–2024)

---

## 0. TL;DR (สำหรับคนรีบ)

- **Pairs trading** = หาสินทรัพย์ 2 ตัวที่มีความสัมพันธ์ระยะยาว (cointegration) แล้วเดิมพันว่าเมื่อราคาเบี่ยงออกจากกันชั่วคราว มันจะกลับมาบรรจบ (mean reversion)
- **Kalman filter** ช่วยประมาณ "hedge ratio (β)" ที่เปลี่ยนตามเวลา → จับจังหวะแม่นขึ้น
- ผลทดสอบ (walk-forward OOS): **Kalman Sharpe ~0.96 vs Static OLS ~0.64** → ยกระดับได้จริง **แต่ไม่ใช่ไม้กายสิทธิ์**
- **ใช้เมื่อ:** ต้นทุนต่ำ (<10 bps) + pair มีพลวัต / **ข้ามเมื่อ:** ต้นทุนสูง (รายย่อย ~30bps+) → static OLS พอ
- **edge ที่แท้จริงอยู่ที่ "เลือก pair/regime ที่ถูก + คุมต้นทุน + วินัย"** ไม่ใช่ความซับซ้อนของโมเดล

---

## 1. ที่มา (Background)

### 1.1 แนวคิดพื้นฐาน
Pairs trading เป็น statistical arbitrage รูปแบบหนึ่ง อาศัย **cointegration**: แม้ราคาสองตัวจะ non-stationary (เดินสุ่ม) แต่ผลต่างเชิงเส้นของมัน (spread) กลับ stationary และมีแนวโน้มกลับสู่ค่าเฉลี่ย

```
spread_t = price1_t − β · price2_t        (β = hedge ratio)
```

เปิดสถานะเมื่อ spread เบี่ยงมากพอ, ปิดเมื่อมันกลับเข้าค่าเฉลี่ย

### 1.2 งานวิจัยต้นทาง
Fanelli, Fontana & Rotondi (2026), *"A Hidden Markov Model for Statistical Arbitrage in International Crude Oil Futures Markets"* (arXiv:2309.00875)
- ใช้ Brent + WTI + Shanghai futures พร้อมกัน
- โมเดล spread เป็น **mean-reverting + regime-switching (Hidden Markov Model)** ประมาณค่าด้วย filter-based EM
- พบว่ากลยุทธ์ที่ "พยากรณ์" spread (model-based) ชนะกลยุทธ์ที่ดูแต่อดีต

### 1.3 รากฐานวิชาการ
| งาน | คุณูปการ |
|-----|----------|
| Gatev et al. (2006) | distance method — benchmark ของวงการ (~11%/ปี ในยุคบุกเบิก) |
| Vidyamurthy (2004) | วางแนว cointegration |
| Elliott et al. (2005) | model-based / Kalman — ต้นแบบของ "พยากรณ์ spread" |
| Do & Faff (2010, 2012) | **reality check** — กำไรลดลงเมื่อตลาดพัฒนา + หักต้นทุนแล้วเกือบไม่เหลือ |

---

## 2. วิธีการ (Methodology)

### 2.1 ส่วนประกอบ
1. **Kalman filter** ประมาณ β รายวันแบบ time-varying (online, causal)
2. **z-score** ของ spread จาก rolling window → สัญญาณเข้า/ออก
3. **กฎเทรด:** เปิดเมื่อ |z| > entry, ปิดเมื่อ z ข้าม 0
4. **Lock hedge ตอนเข้า:** ล็อก β และ notional ณ วันเปิด ไม่ re-hedge รายวัน
5. **ต้นทุน:** transaction cost (ต่อครั้ง) + cost of carry (ต่อวันที่ถือ)
6. **ประเมิน:** walk-forward out-of-sample เท่านั้น

### 2.2 ทำไมต้อง "lock hedge ตอนเข้า"
Kalman อัปเดต β ทุกวัน — ถ้า re-hedge ตาม β ทุกวันจะเกิด turnover มหาศาล (ต้นทุนกินเรียบ)
**แก้:** ใช้ β ใหม่แค่ตอน *เปิดเทรดครั้งถัดไป* ไม่ใช่ระหว่างถือ

---

## 3. ผลการทดลอง (Findings)

ทดสอบบน WTI–Brent (EIA spot, 2016–2024, 2,225 วัน) — ทุกผลคิดต้นทุนแล้ว

### 3.1 ความจริงค่อยๆ เผยตัว (สำคัญที่สุด)
| วิธีประเมิน | ตัวเลข | สถานะ |
|-------------|--------|--------|
| In-sample เต็มก้อน | 34%/ปี | 🔴 หลอกตา |
| Single OOS split (70/30) | Sharpe 3.29 | 🟡 regime luck |
| **Walk-forward (12 หน้าต่าง)** | **Sharpe ~1.0, บวก 100%** | 🟢 ภาพจริง |
| Walk-forward (ตัด COVID) | Sharpe ~2.9, ~18%/ปี | ✅ regime ปกติ (ยัง optimistic) |

> **บทเรียน:** in-sample หลอกตาเสมอ — ตัวเลขที่เชื่อได้คือ walk-forward OOS

### 3.2 Kalman vs Static OLS
- Walk-forward: Kalman **ชนะ 10/12 หน้าต่าง**, Sharpe 0.96 vs 0.64
- → β ที่ปรับตามเวลามีคุณค่าจริง **แต่แลกด้วยจำนวนเทรดที่สูงกว่า ~2.5 เท่า**

### 3.3 Sensitivity ต่อต้นทุน (+ cost of carry)
| | ผล |
|--|-----|
| **Cost of carry** | กระทบน้อย (mean-reversion ถือสั้น) — แม้ 20%/ปี Sharpe ตกแค่ 1.03→0.82 |
| **Transaction cost** | กระทบมาก โดยเฉพาะกับ Kalman ที่เทรดถี่ |
| **จุดพลิก** | ที่ ~30 bps → return ของ Static แซง Kalman |

> **นัย:** ต้นทุนต่ำ (กองทุน 2-5bps) Kalman ชนะชัด / ต้นทุนสูง (รายย่อย 30bps+) old-school พอ

### 3.4 Half-life de-selection (ทดลองแล้ว — ไม่ช่วย pair นี้)
- WTI–Brent reverts เร็วมาก (half-life median ~3 วัน) **แม้ช่วง COVID**
- ใส่ filter de-selection → **ผลแย่ลง** (Sharpe 0.96→0.78) เพราะตัดเทรดที่ทำกำไร
- → de-selection เป็น insurance ที่มีค่า **เฉพาะกับ pair อ่อน/เสี่ยงตาย** ไม่ใช่ pair แข็ง

### 3.5 ข้อควรระวังเรื่องตัวเลข
หน้าต่าง COVID 2020 ทำกำไร ~287% — เป็น **P&L จริงจาก dislocation** แต่เป็น **tail event** ที่ครั้งหน้าอาจล้างพอร์ต (margin call, futures ติดลบ, เทรดไม่ได้) → **อย่านับเป็นรายได้ประจำ**

---

## 4. โค้ด (Reference: `kalman_pairs.py`)

ใช้แค่ `numpy` + `pandas` — โมดูลสมบูรณ์อยู่ในไฟล์ `kalman_pairs.py`

### 4.1 ฟังก์ชันหลัก
```python
kalman_beta(p1, p2, q=1e-4, r=1.0)        # ประมาณ hedge ratio β รายวัน
rolling_zscore(spread, win=60)            # z-score จาก rolling window
pairs_backtest(p1, p2, beta, z, entry,    # backtest (lock hedge + cost + carry)
               cost_bps, carry_annual, start)
perf(rets)                                # annualized return / Sharpe / max DD
walk_forward(p1, p2, ...)                 # OOS evaluator (เลือก param จาก train)
```

### 4.2 หัวใจของ Kalman filter
```python
def kalman_beta(p1, p2, q=1e-4, r=1.0):
    p1 = np.asarray(p1, float); p2 = np.asarray(p2, float); n = len(p1)
    x = np.array([1.0, 0.0])          # state = [beta, intercept]
    P = np.eye(2); Q = np.eye(2) * q
    beta = np.zeros(n)
    for t in range(n):
        H = np.array([p2[t], 1.0])
        P = P + Q                     # predict
        e = p1[t] - H @ x            # innovation
        S = H @ P @ H + r
        K = (P @ H) / S             # gain
        x = x + K * e               # update
        P = P - np.outer(K, H) @ P
        beta[t] = x[0]
    return beta
```

### 4.3 หัวใจของ backtest (lock hedge)
```python
if pos == 0 and abs(z[t]) > entry:        # เปิด
    pos = -1 if z[t] > 0 else 1
    beta_e = beta[t]                       # << LOCK β ตอนเข้า
    gross_e = abs(p1[t]) + abs(beta_e*p2[t])
    rets[t] -= cost
elif pos != 0:                            # ถืออยู่
    pnl = pos*((p1[t]-p1[t-1]) - beta_e*(p2[t]-p2[t-1]))
    rets[t] = pnl/gross_e - carry          # หารด้วย notional ที่ lock + carry รายวัน
    if (pos==-1 and z[t]<=0) or (pos==1 and z[t]>=0):
        pos = 0; rets[t] -= cost           # ปิดเมื่อ z ข้าม 0
```

---

## 5. วิธีใช้ (Usage)

```python
import pandas as pd
from kalman_pairs import kalman_beta, rolling_zscore, walk_forward, perf

# p1, p2 = ราคาสองขา เรียงเก่า->ใหม่ ความยาวเท่ากัน
p1 = df["WTI"].values
p2 = df["Brent"].values

# --- ตัวเลขที่เชื่อได้: walk-forward OOS ---
print("OOS Kalman:", perf(walk_forward(p1, p2, q=1e-4, use_kalman=True)))
print("OOS Static:", perf(walk_forward(p1, p2,          use_kalman=False)))

# --- สัญญาณวันนี้ (เทรดจริง) ---
beta = kalman_beta(p1, p2, q=1e-4)
z = rolling_zscore(p1 - beta*p2, win=60)
print(f"z={z[-1]:.2f}, beta={beta[-1]:.3f}")
# |z|>1.5 & ไม่มีสถานะ -> เปิด (z>0: short p1/long p2 ; z<0: ตรงข้าม)
# มีสถานะ + z ข้าม 0 -> ปิด
```

### ปุ่มปรับ
| พารามิเตอร์ | ค่าเริ่มต้น | ปรับเมื่อ |
|---|---|---|
| `q` (process noise) | 1e-4 | pair กลับช้า → 1e-5 (β นิ่งขึ้น, เทรดน้อยลง) |
| `win` (rolling z) | 60 | ตลาดเร็ว → สั้นลง |
| `entry` | 1.5 | ต้นทุนสูง → 2.0 (เทรดน้อยลง) |
| `cost_bps` | ใส่ของจริง | รายย่อยมัก 20-50+ |
| `carry_annual` | 0.04 | = financing + ค่ายืม short จริง |

---

## 6. เมื่อไหร่ควร/ไม่ควรใช้ Kalman

| ควรใช้ ✅ | ไม่ควรใช้ ❌ |
|-----------|-------------|
| ต้นทุนซื้อขายต่ำ (<10 bps) | ต้นทุนสูง (รายย่อย ~30bps+) → static OLS พอ |
| ความสัมพันธ์ของ pair เปลี่ยนตามเวลา | pair นิ่งมาก → β แทบไม่ขยับ |
| จูนเป็น (Q ต่ำ + lock hedge) | ยังไม่เชี่ยว → เริ่ม static ก่อน |

---

## 7. กฎเหล็ก & ข้อควรระวัง

### กฎเหล็ก (เจ็บมาแล้ว)
1. **อย่าตั้ง Q สูง** — β กระตุก + สัญญาณตาย (ไม่ได้ไวขึ้น)
2. **อย่า re-hedge β รายวัน** — turnover พุ่ง 6 เท่า (โค้ด lock ให้แล้ว)
3. **อย่าใช้ z จาก Kalman innovation ตรงๆ** ถ้า intercept ลอย — spread กลายเป็น noise
4. **ดู walk-forward เท่านั้น** — อย่าตัดสินจาก in-sample
5. **อย่าเพิ่ม filter ฟุ่มเฟือย** บน pair แข็ง

### ความเสี่ยงที่โมเดลไม่บอก
- **ไม่ใช่ arbitrage จริง** — spread อาจไม่กลับ (structural break) → ติดสถานะขาดทุนยาว
- **Tail risk** — ช่วงวิกฤตอาจล้างพอร์ต (margin call, gap, สภาพคล่องหาย)
- **Crowding** — กลยุทธ์ยอดนิยมพังพร้อมกันได้ (เช่น Quant Quake ส.ค. 2007)
- **Spot ≠ futures** — ผลทดสอบใช้ spot; ของจริงมี roll cost + execution
- **Alpha decay** — edge หดเมื่อตลาดพัฒนา/มีคนทำมากขึ้น

---

## 8. ขั้นตอนก่อนใช้เงินจริง (Checklist)
- [ ] เลือก pair ที่มีเหตุผลเศรษฐกิจรองรับ (ไม่ใช่ data-mining)
- [ ] ทดสอบ cointegration และ walk-forward หลายหน้าต่าง
- [ ] ใส่ `cost_bps` + `carry_annual` **ของคุณจริง** (conservative)
- [ ] ตรวจว่าเข้าถึงตลาดได้จริง (เช่น Shanghai INE เข้ายากสำหรับต่างชาติ)
- [ ] Paper trade อย่างน้อย 3–6 เดือน
- [ ] ตั้ง stop-loss / เวลาถือสูงสุด + จำกัดขนาดต่อคู่
- [ ] เริ่มเงินจริงเล็กๆ ก่อน

---

## 9. ไฟล์ในโปรเจกต์
| ไฟล์ | เนื้อหา |
|------|---------|
| `kalman_pairs.py` | ⭐ โมดูลใช้งานจริง (template) |
| `kalman_q_demo.py` | สาธิตผลของการตั้งค่า Q (สูง vs ต่ำ) |
| `wti_brent_kalman.py` | backtest พื้นฐาน Kalman vs static |
| `wti_brent_oos.py` | train/test 70/30 split |
| `wti_brent_walkforward.py` | walk-forward หลายหน้าต่าง |
| `wti_brent_cost.py` | sensitivity ต่อ cost + cost of carry |
| `wti_brent_normfix.py` | แก้ normalization (entry-locked notional) |
| `wti_brent_halflife.py` | half-life de-selection filter |

---

## 10. อ้างอิง
- Fanelli, Fontana & Rotondi (2026), *A Hidden Markov Model for Statistical Arbitrage in International Crude Oil Futures Markets*, arXiv:2309.00875
- Gatev, Goetzmann & Rouwenhorst (2006), *Pairs Trading*, RFS
- Vidyamurthy (2004), *Pairs Trading: Quantitative Methods and Analysis*
- Elliott, Van der Hoek & Malcolm (2005), *Pairs Trading*, Quantitative Finance
- Do & Faff (2010, 2012), reality-check studies
- *A Survey of Statistical Arbitrage Pairs Trading Strategies* (Warsaw WNE WP 19/2025)

> **ข้อจำกัดความรับผิด:** เอกสารนี้เพื่อการศึกษา ไม่ใช่คำแนะนำการลงทุน — pairs trading มีความเสี่ยงขาดทุนจริง
