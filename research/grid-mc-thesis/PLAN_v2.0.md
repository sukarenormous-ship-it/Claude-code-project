# Spot Grid Edge, Depth Structure & MC Risk — Research Plan v2.0

**วันที่:** 2026-09-24
**สถานะ:** แผนปรับจาก `HANDOFF_v1.0.md` — รอผู้วิจัยยืนยันค่าใน §11 ก่อนเริ่ม P0
**หลักการเปลี่ยน:** จาก *"MC ช่วยจัดสรรทุน grid ได้ดีกว่า Basic ไหม"*
เป็น **คำถาม 3 ชั้นที่มีประตู (gate) กั้น** — ทุกผลลัพธ์ที่เป็นไปได้จบเป็น thesis ที่ป้องกันได้

---

## 0. สรุปการเปลี่ยนแปลงจาก v1.0

| หมวด | v1.0 | v2.0 | เหตุผล |
|---|---|---|---|
| คำถามหลัก | Adaptive/MC allocation > Basic | RQ1 edge → RQ2 depth structure/allocation → RQ3 MC risk | ถ้า grid ไม่มี edge เหนือ beta การปรับ allocation ไม่มีความหมาย |
| บทบาท MC | estimator สำหรับ allocation | (1) null model ทดสอบ edge (2) risk engine สำหรับ joint tail/reserve | MC ที่ fit จากข้อมูลเดียวกันไม่เพิ่มข้อมูลด้าน alpha |
| Metric | หลายตัว ไม่มีตัวหลัก | ตัวหลัก 1 ตัวต่อ RQ + non-inferiority margins เป็นตัวเลข (§3) | ป้องกัน cherry-pick |
| Benchmark | Basic 3 แบบ | + Shadow-exposure, HODL-matched, DCA, Cash | แยก timing edge ออกจาก beta |
| `[L,U]` / `S0` | ไม่ระบุนโยบายข้ามปี | Epoch/re-center policy ตายตัว (§4.2) | BTC 3k→100k+ ทำให้ range คงที่ใช้ไม่ได้ |
| Fill | crossing ≠ fill (หลักการ) | trade-through ≥ 1 tick เป็นค่าหลัก, touch-fill เป็น sensitivity | maker limit: touch ≠ fill |
| สถิติ | paired comparison | block bootstrap + effective N + power/MDE + SPA + censoring-aware scoring | episode อิสระมีน้อย |
| Estimator กลาง | Empirical → MC | Empirical → **semi-parametric survival** → (MC เฉพาะ risk) | smoothing หางบางแบบโปร่งใส |
| Data split | walk-forward (ไม่ระบุช่วง) | Dev / Val / sealed Test ระบุวันที่ (§5) | กัน leakage |
| ขอบเขต | S0–S10, 8 arms | P0–P7; Governor ซับซ้อน, Adaptive TP, Regime, Orderflow → parking lot | thesis เดียวต้องจบได้ |
| สิ่งที่ **คงไว้** | — | Hard rules §2, crossing≠fill, event engine, golden tests, censoring, Capital Lock, TP floor, parameter governance, "MC proposes; risk disposes", falsification mindset | จุดแข็งของ v1.0 |

---

## 1. คำถามวิจัยและสมมติฐาน

### RQ1 — Edge: grid บน spot BTC/ETH มี edge เหนือ beta หรือไม่
- **H1₀:** ผลตอบแทนของ Basic Grid ไม่ต่างจากพอร์ตที่ถือ exposure เส้นทางเดียวกัน (Shadow) และไม่ต่างจาก grid บน surrogate paths ที่ไม่มี mean reversion
- **H1₁:** grid ได้ timing alpha > 0 จาก mean reversion ในสเกลระยะห่าง grid

### RQ2 — Structure: hit–recovery–capital-lock ต่างกันตาม depth อย่างคงที่หรือไม่ และใช้ประโยชน์ได้หรือไม่
- **H2a₀:** ความน่าจะเป็น/เวลา recovery ไม่ขึ้นกับ depth (หลังคุม vol) หรือไม่คงที่ข้าม block
- **H2b₀:** Empirical-C (tilt จาก Basic ด้วย shrinkage) ไม่ให้ ERLC ดีกว่า Basic ที่ดีที่สุด โดยไม่แย่ลงด้าน downside

### RQ3 — MC risk: MC ประมาณ joint tail ของพอร์ต grid ได้ดีกว่า empirical หรือไม่ และ reserve จาก MC มีค่าเชิงเศรษฐกิจหรือไม่
- **H3₀:** quantile ของ K_max / peak CL / drawdown จาก MC ไม่ calibrated ดีกว่า empirical quantile และ reserve จาก MC ไม่ลด breach โดยไม่เสีย ERLC เกิน tolerance

ลำดับบังคับ: RQ1 → RQ2 → RQ3 (RQ3 ทำได้แม้ RQ2 ล้ม ดู §8)

---

## 2. Hard contract (คงจาก v1.0)

Spot only · buy-only entry · fully funded · ไม่มี leverage/borrow/martingale/เติมทุน · MC/โมเดลขยาย `[L,U]` ไม่ได้ ลด structural reserve ไม่ได้ ลบ inventory ไม่ได้ · inventory คงอยู่ข้าม replan และ mark-to-market · นอก `[L,U]` หยุด entry ใหม่ exit เดิมทำต่อ · TP ≥ TP_floor เสมอ · invariant ล้ม = backtest invalid

---

## 3. Pre-registration: metric และเกณฑ์ (ล็อกใน P0)

### 3.1 นิยาม
- `C_locked(t)` = มูลค่าต้นทุนของ inventory ที่ถืออยู่ ณ t
- `LCT = ∫ C_locked(t) dt` (capital-time, หน่วย USDT·ปี)
- `NetPnL` = realized + unrealized (MTM ณ สิ้นช่วง) หลังค่าธรรมเนียม/slippage/rounding
- `r_h` = hurdle rate ต่อปี (ค่าเริ่มต้นเสนอ 4%, sensitivity 0% / 6%)
- เงินสดว่างได้ `r_h` ทุก arm เท่ากัน (ยุติธรรมกับ benchmark)

### 3.2 Metric หลัก (หนึ่งตัวต่อ RQ)
| RQ | Primary metric | นิยาม |
|---|---|---|
| RQ1 | **Timing Alpha (TA)** | `Return(Grid) − Return(Shadow)` ต่อปี โดย Shadow ถือ exposure (สัดส่วน BTC ต่อ equity) เท่ากับ grid ณ บาร์ก่อนหน้า (lag 1 บาร์ 1h) ซื้อขายที่ราคาปิดบวกต้นทุน taker |
| RQ2 | **ΔERLC** (paired) | `ERLC = (NetPnL − r_h·LCT) / LCT`; เทียบ Empirical-C − Basic ที่ดีที่สุด บน path/block เดียวกัน |
| RQ3 | **Quantile loss + breach economics** | pinball loss ของ Q90/Q95 ของ K_max, peak CL, 30d drawdown ต่อ episode; และ `#reserve breach` ที่ ERLC ไม่แย่ลงเกิน margin |

### 3.3 Secondary (รายงานเสมอ ไม่ใช้ตัดสินหลัก)
MaxDD, CVaR95 ของผลตอบแทน 30 วัน, CLI, inventory age Q90, terminal inventory, time-under-water, จำนวน fill, return เทียบ HODL-matched/DCA/Cash

### 3.4 Non-inferiority margins (ค่าเสนอ — ยืนยันใน P0)
| Metric | Margin ที่ยอมให้แย่ลงได้ |
|---|---|
| MaxDD | +2.0 จุดเปอร์เซ็นต์ (absolute) |
| CVaR95 (30d) | +10% relative |
| CLI | +10% relative |
| Inventory age Q90 | +15% relative |
| Terminal inventory (% ของ B) | +5 จุดเปอร์เซ็นต์ |

Adaptive arm "ชนะ" = primary ดีกว่าอย่างมีนัยสำคัญ **และ** ผ่าน margin ทุกตัว

### 3.5 กฎการตัดสิน
- Primary test หนึ่งตัวต่อ gate, one-sided, α = 0.05
- Secondary: รายงานพร้อม Holm correction, ไม่ใช้เป็นเหตุผลให้ GO
- ห้ามเปลี่ยน metric/margin หลังเห็นผลของ gate นั้น — ถ้าจำเป็นต้องเปลี่ยน ให้เขียน deviation log พร้อมเหตุผลและรายงานทั้งสองแบบ
- Pre-registration file ถูก commit และบันทึก SHA-256 ก่อนรัน P3

---

## 4. Structural design (ไม่ optimize ตาม PnL)

### 4.1 ค่าพื้นฐาน (ค่าเสนอ)
| พารามิเตอร์ | ค่าเสนอ | Sensitivity |
|---|---|---|
| `B` | 10,000 USDT | 1,000 / 100,000 (ผล rounding/min-notional) |
| Structural reserve `R` | 10% ของ B | 0% / 20% |
| `N` slots | 40 | 20 / 80 |
| Spacing | Arithmetic (A0) และ Log (A1) — ทั้งคู่เป็น benchmark | — |
| TP | fixed, = max(TP_floor, 1 spacing) | 0.5× / 2× spacing |
| Fees | 0.10% maker ต่อข้าง (Binance spot VIP0) | 0.075% / 0.15% |
| Slippage (maker fill) | 0 + trade-through rule | touch-fill (optimistic) |
| Re-arm `r_rearm` | 0.5 spacing | 0.25 / 1.0 spacing |

### 4.2 นโยบาย range และ anchor (ปิดช่องโหว่ใหญ่ของ v1.0)
- **Anchor `S0`** = ราคา ณ เวลาที่สร้าง/re-center grid; depth ของ level `d = 1 − g/S0`
- **Envelope:** `[L,U] = [S0·(1 − w_down), S0·(1 + w_up)]` ค่าเสนอ `w_down = 60%`, `w_up = 10%`; sensitivity `w_down` 40% / 75%
- **Re-center ขึ้นเท่านั้น:** เมื่อราคา ≥ U ต่อเนื่อง ≥ 24 ชม. → สร้าง grid ใหม่ที่ anchor ใหม่ด้วย **free cash เท่านั้น**; position เดิมยังถือ TP เดิม (ไม่มีการขาย/ซื้อเพื่อ rebalance)
- **ไม่ re-center ลง:** ใต้ L = หยุด entry, ถือ inventory, รอ exit (ป้องกัน averaging down นอกกรอบ)
- นโยบายนี้เป็น structural policy — ใช้เหมือนกันทุก arm และห้ามปรับตามผล

### 4.3 Execution
- Engine: `MarketData → Crossing → Eligibility → Fill → Position → Exit → Ledger` (จาก v1.0)
- **Fill หลัก:** limit buy ที่ g ถือว่า fill เมื่อ `low_1m ≤ g − 1 tick`; limit sell ที่ TP fill เมื่อ `high_1m ≥ TP + 1 tick`
- **Intrabar ambiguity:** entry และ TP อยู่ในแท่ง 1m เดียวกัน → นับ entry อย่างเดียว TP เร็วสุดแท่งถัดไป
- Golden tests 18 ข้อของ v1.0 + เพิ่ม: (19) trade-through vs touch, (20) re-center เฉพาะ free cash, (21) Shadow portfolio lag-1 ไม่มี lookahead, (22) hurdle accrual บนเงินสดว่าง

---

## 5. ข้อมูลและการแบ่งช่วง

- **Venue หลัก:** Binance spot `BTCUSDT`, `ETHUSDT` 1m จาก data.binance.vision (มี checksum → provenance) เริ่ม 2017-08
- **Cross-check venue:** Bybit spot ช่วงที่ทับกัน (เช็กความต่างของ path/fill เท่านั้น)
- **Research clock:** 1h (aggregate จาก 1m แหล่งเดียวกัน); execution: 1m
- Manifest/DQ ตาม M0 ของ v1.0

| ช่วง | วันที่ | ใช้ทำ | เหตุการณ์สำคัญ |
|---|---|---|---|
| **Dev** | 2017-08 → 2021-12 | สำรวจ, fit estimator, เลือก config | 2018 bear, มี.ค. 2020 crash, 2021 run + พ.ค. 2021 crash |
| **Val** | 2022-01 → 2023-12 | ตัดสิน G3/G4 (ใช้ครั้งเดียวต่อ gate) | LUNA/FTX, bear ที่ฟื้นช้า |
| **Test (sealed)** | 2024-01 → เดือนสุดท้ายที่ครบ ณ วันที่ล็อก | P7 เท่านั้น รันครั้งเดียว | — |

- **Contamination log:** บันทึกว่าช่วงใดเคยถูกดูในงานก่อน (เช่น 6-mode experiment บน perp 4h) ถ้า Test เคยถูกดู ให้ระบุเป็น "partially contaminated" ในรายงาน
- **Robustness (ไม่ใช้เลือก config):** leave-one-cycle-out บน Dev+Val

---

## 6. ลำดับงานและประตู

### P0 — Pre-registration (1–2 สัปดาห์)
ยืนยันค่าใน §3–§5 และ §11 → เขียน `PREREG.md` → commit + SHA-256
**DoD:** ไฟล์ล็อกแล้ว; ยังไม่มีผล backtest ใดๆ บน Val/Test

### P1 — Data integrity / M0 (≈2 สัปดาห์)
ตาม M0 ของ v1.0 (manifest, DQ audit, reconcile 1m→1h, extreme events)
**Gate G0:** BTC และ ETH ≥ 6 ปีสถานะ PASS/CONDITIONAL
ล้ม → ลดขอบเขตเป็น 1h + E1 execution และระบุข้อจำกัด

### P2 — Engine / M1 (3–4 สัปดาห์)
Event engine + ledger + cost engine + benchmarks (Shadow, HODL-matched, DCA, Cash) + golden tests 22 ข้อ
**Gate:** golden 100%, deterministic, ledger reconcile

### P3 — RQ1 Edge test (≈3 สัปดาห์) — ใช้ Dev เท่านั้น
1. รัน A0/A1 Basic → TA, ERLC, secondaries; แยก PnL = grid-realized + inventory MTM
2. **Surrogate test** (ดู §7.1) — 1,000 เส้นต่อ family
3. Variance ratio / autocorrelation ของ returns ที่ horizon 1h–7d (diagnostic)
4. **Power/MDE:** block bootstrap ของ ERLC(Basic) → MDE ของ ΔERLC ที่ α=0.05, power=0.8 → บันทึกลง deviation-free log ก่อนเข้า P5

**Gate G1 (ต่อสินทรัพย์):** TA > 0 (block-bootstrap p < 0.05) **และ** ERLC บนเส้นจริงอยู่เหนือ percentile 90 ของ surrogate S-B
- ผ่านทั้ง BTC/ETH หรือตัวใดตัวหนึ่ง → P4 กับตัวที่ผ่าน
- ล้มทั้งคู่ → **Outcome A** (§8): ยืนยันบน Val → ข้ามไป P6 (optional) และ P7

### P4 — RQ2a Path anatomy + survival (3–4 สัปดาห์) — Dev
- Surfaces ตาม M2 v1.0: recovery probability, survival curves, Q90 CL, Q95 MAE, drawdown depth × duration, jump distribution, sample-support map
- **Effective N:** นับ drawdown episode อิสระ (de-overlapped) ต่อ depth bin; bin ที่ < 8 episode = InsufficientEvidence
- **Survival model:** Weibull AFT และ Cox, covariates = depth, realized vol (lagged), time-block; censoring ถูกต้อง
- **K distribution:** จำนวน slot ที่ถูก fill ต่อ drawdown episode และ peak CL ต่อ episode (joint risk)

**Gate G2:** depth effect มีนัยสำคัญ (LR test p < 0.01) **และ** ทิศทาง/ลำดับคงที่ใน ≥ 3 จาก 4 time block **และ** spread ERLC ระหว่าง depth region ดีสุด–แย่สุด > 2 × TP_floor ต่อรอบ
- ผ่าน → P5
- ล้ม → **Outcome B** → ข้าม P5 ไป P6

### P5 — RQ2b Allocation (≈4 สัปดาห์) — fit บน Dev, ตัดสินบน Val
- Arms: A0 Arithmetic, A1 Log, A2 Basic + MA gate (MA ค่าเดียวที่ประกาศล่วงหน้าใน P0 เช่น MA 200 บาร์บน 1h), **B0 Empirical-C**, **B0s Survival-C** (ใช้ survival model แทน empirical bins)
- Tilt: `G = G_Basic + w·ΔG`, `w ∈ [0,1]` จาก uncertainty shrinkage; region-level (4–6 region) ไม่ใช่ราย level; min spacing + concentration cap
- Candidate set จำกัด ≤ 12 config ประกาศใน P0
- ทดสอบ: paired stationary block bootstrap (block ≥ 30 วัน) ของ ΔERLC บน Val + **Hansen SPA** ข้าม candidate set + non-inferiority ทุก margin

**Gate G3:** best adaptive vs best Basic: ΔERLC > 0 (SPA p < 0.05) และผ่าน margin ทุกตัว และ ΔERLC ≥ MDE จาก P3
- ผ่าน → config นี้เป็นผู้เข้าชิงใน P7
- ล้ม → **Outcome C** (Basic เพียงพอ)

### P6 — RQ3 MC as risk engine (≈4 สัปดาห์) — fit บน Dev, ตัดสินบน Val
- Model classes (ล็อกใน P0): **M-G** GBM (null) · **M-GJ** GARCH(1,1)-t + jumps · **M-SB** stationary bootstrap (block เฉลี่ย 7 และ 30 วัน)
- Parameter uncertainty: resample พารามิเตอร์จาก bootstrap/posterior ต่อเส้น
- Targets ต่อ episode/window: K_max, peak CL, 30d drawdown, time-under-water
- **Empirical comparator:** rolling empirical quantile + survival-model quantile
- **Calibration:** coverage ของ Q90/Q95 บน Val (rolling 90d windows), pinball loss, PIT histogram
- **Economic test:** reserve rule `R_t = max(R_structural, R_model)` — เทียบ structural-only / empirical-reserve / MC-reserve บน Val: #breach, MaxDD, ERLC

**Gate G4:** MC coverage คลาดไม่เกิน ±5 จุดเปอร์เซ็นต์ และ pinball loss ≤ empirical **และ** MC-reserve ลด breach หรือ MaxDD โดย ERLC ไม่แย่เกิน margin
- ผ่าน → MC-reserve เข้าชิงใน P7
- ล้ม → **Reject MC** → **Outcome D** (ใช้ empirical reserve) — ยังเป็นผลที่รายงานได้
- **ข้อจำกัดที่ต้องเขียน:** Val มี episode ใหญ่น้อย → coverage test มี power ต่ำ; รายงาน pooled BTC+ETH แยกจากรายตัว

### P7 — Final confirmation (≈1 สัปดาห์)
รัน config ที่ชนะจากแต่ละ gate (และ A1 Log Basic เสมอ) บน Test **ครั้งเดียว** → รายงานทุกผล ไม่ว่าดีหรือแย่
ห้ามแก้ config หลังเห็นผล Test

### Parking lot (ไม่ทำใน thesis นี้)
Entry Governor แบบ incremental-value, Adaptive TP, Regime/conditional MC, Orderflow, dynamic sizing, หลายสินทรัพย์

---

## 7. รายละเอียดวิธีการ

### 7.1 Surrogate families (P3)
| Family | วิธี | คงไว้ | ทำลาย |
|---|---|---|---|
| **S-A** | สลับ 1h log-returns แบบ iid | ราคาเริ่ม/จบ, distribution ของ returns | vol clustering, autocorrelation |
| **S-B** (หลัก) | ปรับ returns ด้วย conditional vol (GARCH ที่ fit บน Dev) → สลับ standardized residuals → คูณ vol path เดิมกลับ | ราคาเริ่ม/จบโดยประมาณ, vol path, fat tails | sign autocorrelation / mean reversion |
| **S-C** | IAAFT phase randomization | amplitude distribution + linear autocorrelation spectrum | nonlinear dependence |

การตีความ: ชนะ S-B แต่ไม่ชนะ S-C → edge เป็น linear autocorrelation (อธิบายได้ด้วย OU) · ชนะทั้งคู่ → มีโครงสร้าง nonlinear เพิ่ม

### 7.2 สถิติ
- Bootstrap: stationary block bootstrap, block เฉลี่ย ≥ 30 วัน (≥ recovery horizon ยาวสุดที่ใช้ตัดสิน), 5,000 resamples
- Effective N รายงานคู่กับ n ทุกตาราง
- Censoring-aware scoring: IPCW-Brier, Harrell's C สำหรับ survival/recovery models
- Multiple testing: SPA สำหรับ candidate set; Holm สำหรับ secondary
- Analytic baseline: first-passage probability/เวลาของ GBM และ OU (สูตรปิด) เทียบกับ empirical และ MC

### 7.3 Software (ต่อยอดโครง v1.0)
```text
market_data/  event_engine/  execution/  ledger/
benchmarks/        shadow, hodl_matched, dca, cash
surrogates/        iid, vol_residual_shuffle, iaaft
landscape/         empirical, survival, mc_estimator, uncertainty
allocation/        basic, constrained_tilt, shrinkage
risk/              reserve, k_distribution
validation/        golden_cases, block_bootstrap, spa, calibration, walk_forward
prereg/            PREREG.md, hashes, deviation_log.md
```

---

## 8. แผนที่ผลลัพธ์ → thesis ที่ได้

| Outcome | เงื่อนไข | Contribution | บทที่เต็ม |
|---|---|---|---|
| **A** | G1 ล้ม | "ทดสอบอย่างเข้มงวดแล้ว spot grid บน BTC/ETH ไม่มี timing edge เหนือ beta" — พร้อม surrogate evidence | 1–4, 7, 8 (+6 ถ้าทำ) |
| **B** | G1 ผ่าน, G2 ล้ม | "grid มี edge แต่ไม่มีโครงสร้างตาม depth ที่คงที่ — Basic เพียงพอ" + MC risk | 1–5a, 6–8 |
| **C** | G2 ผ่าน, G3 ล้ม | "มีโครงสร้างแต่ใช้ประโยชน์ไม่ได้หลังต้นทุน/uncertainty" | ครบ |
| **D** | G4 ล้ม | "MC ไม่ดีกว่า empirical ในการประมาณ joint tail" (รวมกับ A/B/C ได้) | บท 6 เป็นผลลบ |
| **Full GO** | G1–G4 ผ่าน + P7 ยืนยัน | Basic-anchored allocation + MC reserve มีค่าเชิงเศรษฐกิจ | ครบ |

### โครงเล่ม thesis
1. บทนำ & คำถามวิจัย
2. ทบทวนวรรณกรรม: grid trading, optimal mean-reversion trading (OU; Bertram 2010, Leung & Li 2015), market making & inventory risk (Avellaneda & Stoikov 2008), survival analysis, bootstrap/MC สำหรับอนุกรมเวลา
3. ข้อมูล, engine, การบัญชี, golden tests
4. RQ1 Edge & surrogate test
5. RQ2 Path anatomy, survival model, allocation
6. RQ3 MC risk engine & reserve
7. Final holdout confirmation
8. อภิปราย, ข้อจำกัด (survivorship: BTC/ETH คือสินทรัพย์ที่รอด; episode น้อย; venue เดียว), งานต่อยอด

---

## 9. Kill criteria สรุป

| จุด | เงื่อนไขหยุด/เปลี่ยนทาง |
|---|---|
| P1 | ข้อมูลที่เชื่อถือได้ < 6 ปี → ลดขอบเขต |
| P3 | MDE > 2× ΔERLC ที่สมเหตุสมผล (เช่น > 3%/ปีของ LCT) → ตัด P5 ทิ้ง ไม่ต้องทดสอบสิ่งที่ตรวจจับไม่ได้ |
| G1 | ล้ม → Outcome A |
| G2 | ล้ม → Outcome B |
| G3 | ล้ม → Outcome C |
| G4 | ล้ม → Reject MC |
| ทุกจุด | invariant ล้ม / พบ lookahead → หยุด แก้ engine รันใหม่ตั้งแต่ P2 |

---

## 10. Timeline (ประมาณการ)

| Phase | สัปดาห์ | สะสม |
|---|---|---|
| P0 | 1–2 | 2 |
| P1 | 2 | 4 |
| P2 | 3–4 | 8 |
| P3 | 3 | 11 |
| P4 | 3–4 | 15 |
| P5 | 4 | 19 |
| P6 | 4 | 23 |
| P7 | 1 | 24 |
| เขียนเล่ม | 6–8 | ≈ 31 |

Outcome A/B จบเร็วกว่านี้ 6–10 สัปดาห์

---

## 11. สิ่งที่ผู้วิจัยต้องตัดสินใจก่อน P0

1. Venue หลัก: Binance spot (แนะนำ — ข้อมูลยาวและมี checksum) หรือ Bybit
2. ขนาดทุน `B` และ `N` (กระทบ min-notional/rounding)
3. นโยบาย envelope: `w_down`, `w_up`, เงื่อนไข re-center
4. Non-inferiority margins (§3.4) และ hurdle rate
5. ความยาว MA ของ A2 และ candidate set ของ P5 (≤ 12)
6. ช่วงวันที่ Dev/Val/Test และรายการช่วงที่เคยดูมาแล้ว (contamination log)
7. กำหนดส่ง thesis → ใช้ปรับขอบเขต P5/P6

---

**ปรัชญาการทำงาน (ปรับจาก v1.0):**
**พิสูจน์ edge ก่อนปรับ allocation. Basic = prior และ fallback. Empirical/survival = ข้อมูล. MC = null model และ risk engine. Reserve floor, TP floor, invariants และ pre-registration อยู่เหนือทุกโมเดล. ทุกผลลัพธ์ — รวมผลลบ — ต้องจบเป็นข้อสรุปที่ป้องกันได้.**
