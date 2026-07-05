# QA Issue List — เล่ม Statistical Arbitrage (ทีมตรวจความถูกต้อง + ภาพประกอบ)

> สถานะ: **ตรวจเนื้อหาครบ 6/6 cluster** (85 issues) · ตรวจภาพ (visual ×5) ติด session limit — จะรันหลัง 16:30 UTC
> ระดับ: 🔴 ผู้อ่านเข้าใจผิดเป็นเงิน · 🟠 สับสน · 🟡 ความสวยงาม
> สถานะแก้: ✅ = แก้แล้วใน branch นี้

## แก้แล้ว (commit ก่อนหน้า + commit นี้)
- ✅ ch3 §3.6 σ_stat ไม่สอดคล้อง residual std (แก้ residual std → 0.000044)
- ✅ ch3 §3.10 ตาราง sensitivity คำนวณใหม่ตาม hourly-bar convention + เปลี่ยน attribution จาก "Kendall" → "regime/selection"
- ✅ ch3 §3.10 Kendall block: เน้น N = จำนวน bar + เพิ่มตัวอย่างเทียบ daily/hourly + ตัด ×24 เกิน
- ✅ ch2 โจทย์ 2.3: 4σ → 2.7σ
- ✅ กราฟ ch13-basis-pnl.svg สูง 6 เมตร (สาเหตุหน้าว่าง ~23 หน้าใน PDF) — แก้ generator double-scaling แล้ว regenerate
- ✅ docs/charts/ 75 ไฟล์หายทั้งโฟลเดอร์ (ภาพแตกทุกบท) — ดึงเข้ามาแล้ว


## Cluster: foundations (ch0–3) — 5 issues

### 🔴 foundations-1. statarb-ch3.html — §3.6 กล่อง running example 'ตัวอย่างจริง: Bybit↔Lighter BTC — Calibration ผล' (~ ✅
- **ประเภท**: ตัวเลขในตัวอย่างผิด
- **ปัญหา**: ค่า σ_stat ≈ 0.00080 ขัดกับ b และ residual std ที่ให้ไว้ในตัวอย่างเดียวกัน — ตามสูตรที่เล่มสอนเอง (โจทย์ 3.1 และ step 3 ของ §3.6: σ_stat = residual_std/√(1−b²) ซึ่ง 'ลู่เข้าหากัน' กับ std(ε−θ)) ค่าที่ได้คือ 0.00012/√(1−0.9985²) = 0.00012/0.05475 ≈ 0.00219 (0.22%) ไม่ใช่ 0.08% ต่างกัน ~2.7 เท่า ทำให้ Entry band (0.293%/−0.027%) และ Stop (0.373%/−0.107%) ที่คำนวณต่อจากนั้นแคบเกินจริงทั้งหมด
- **หลักฐาน**: `b = 0.9985,  a = 2.0×10⁻⁶ / Residual std = 0.00012 ... σ_stat ≈ 0.00080  (≈ 0.08%) ... Entry: ε > 0.293% หรือ ε < −0.027%`
- **วิธีแก้**: ทำตัวเลขให้สอดคล้องกัน: ถ้าจะคง σ_stat = 0.08% ให้แก้ Residual std เป็น ≈ 0.000044 (= 0.0008×√(1−0.9985²)) หรือถ้าคง Residual std = 0.00012 ให้แก้ σ_stat เป็น ≈ 0.22% แล้วคำนวณ entry/stop band ใหม่

### 🟠 foundations-2. statarb-ch3.html — §3.10 ตาราง Sensitivity Test (~บรรทัด 651–657) ✅
- **ประเภท**: ตัวเลขในตัวอย่างผิด
- **ปัญหา**: คอลัมน์ b̂ กับ κ ไม่สอดคล้องกันภายใต้ bar size คงที่ใด ๆ: Δt ที่ implied จากแต่ละแถวคือ 0.0140, 0.0156, 0.0170, 0.0171 วัน (≈20–25 นาที) — ไม่คงที่ และไม่ตรงกับ convention ของบท (รายชั่วโมง Δt=1/24 ตาม §3.5–3.6 และโจทย์ 3.1–3.2) ถ้าใช้ bar รายชั่วโมง b̂=0.856 ต้องให้ κ = −ln(0.856)×24 ≈ 3.7 ต่อวัน (half-life ≈ 4.5 ชม.) ไม่ใช่ 11.1 ต่อวัน / 1.5 ชม.
- **หลักฐาน**: `30 วัน | 0.856 | 11.1 | 1.5 ชม. ... 90 วัน | 0.968 | 1.9 | 8.7 ชม.`
- **วิธีแก้**: ระบุ bar size ของตัวอย่างให้ชัด แล้วคำนวณ κ/half-life ใหม่ให้สอดคล้องทุกแถว เช่นถ้า hourly bars: κ = 3.73, 2.21, 1.31, 0.78 ต่อวัน และ half-life = 4.5h, 7.5h, 12.7h, 21.3h ตามลำดับ (แนวโน้มของบทเรียนยังคงเดิม)

### 🔴 foundations-3. statarb-ch3.html — §3.10 Bias Correction block (~บรรทัด 672–682) และการเชื่อมโยงกับตาราง Sensitivit ✅
- **ประเภท**: ความรู้ผิด
- **ปัญหา**: ตัวอย่างการแก้ Kendall bias ใช้ 'N = 30 obs' โดย map เข้ากับแถว 'lookback 30 วัน' ของตาราง — แต่ lookback 30 วันของข้อมูล intraday (hourly bar ขึ้นไป) มี N ≥ 720 observations ซึ่ง Kendall bias = (1+3b)/N ≈ 0.005 เท่านั้น เล็กเกินกว่าจะอธิบาย b̂ ที่ตกจาก 0.968 เหลือ 0.856 ได้ การสอนแบบนี้ชวนให้ผู้อ่านแทน N ด้วย 'จำนวนวัน' แทน 'จำนวน bar' → b_corrected สูงเกินจริงมหาศาล และเข้าใจผิดว่าความไม่เสถียรของ half-life ระหว่าง lookback (รวมโจทย์ 3.5 ที่ N ต่อ window เป็นร้อย ๆ bar) เกิดจาก Kendall bias ทั้งที่เชิงตัวเลขเป็นไปไม่ได้ — สาเหตุจริงคือ regime/selection ตามสาเหตุที่ 2–3 ที่บทเองก็เขียนไว้
- **หลักฐาน**: `ตัวอย่าง: b̂ = 0.856, N = 30 obs → b_corrected = 0.856 + (1 + 3×0.856)/30 = 0.975 ... ← ดีกว่า 30-วัน estimate (1.5h) มาก`
- **วิธีแก้**: เน้นว่า N ในสูตร Kendall คือจำนวน bar/observation ไม่ใช่จำนวนวัน แล้วแยกตัวอย่าง: (ก) ตัวอย่าง Kendall bias ใช้ daily bars ที่ N=30 จริง หรือ (ข) ถ้าเป็น intraday lookback 30 วัน ระบุว่า Kendall bias เล็กมาก (~0.005) และความต่างของ half-life ในตาราง/โจทย์ 3.5 มาจาก regime selection ไม่ใช่ Kendall bias

### 🟠 foundations-4. statarb-ch3.html — §3.10 Bias Correction block (~บรรทัด 676) ✅
- **ประเภท**: สูตรผิด/พิมพ์ผิด
- **ปัญหา**: บรรทัดคำนวณ half-life ที่ corrected มีตัวคูณ ×24 เกินมา: −ln(2)/ln(0.975) = 27.4 คือ half-life ในหน่วย bar อยู่แล้ว (≈27 ชม. ถ้า bar รายชั่วโมง) — สูตรตามที่พิมพ์ (×24) ให้ค่า ≈ 658 ชม. ไม่ใช่ 27 ชม. ผู้อ่านที่กดเครื่องคิดเลขตามจะได้ค่าคนละโลกกับคำตอบที่พิมพ์
- **หลักฐาน**: `half-life (corrected) ≈ −ln(2)/ln(0.975) × 24h ≈ 27 ชม.`
- **วิธีแก้**: ตัด '× 24h' ออก: half-life (corrected) ≈ −ln(2)/ln(0.975) ≈ 27.4 bars ≈ 27 ชม. (สำหรับ hourly bars)

### 🟠 foundations-5. statarb-ch2.html — โจทย์ 2.3 เฉลย (~บรรทัด 313) ✅
- **ประเภท**: ตัวเลขในตัวอย่างผิด
- **ปัญหา**: เฉลยบอกว่า ε−θ = 0.004 'ห่างกัน 4× σ_stat โดยประมาณ' — แต่จากพารามิเตอร์ที่โจทย์ให้ (κ=2, σ=0.003) σ_stat = σ/√(2κ) = 0.003/√4 = 0.0015 ดังนั้น 0.004/0.0015 ≈ 2.7σ_stat ไม่ใช่ 4σ (ตัวเลข 4 ดูเหมือนเผลอหารด้วย σ_stat=0.001) ต่างกันเชิงการตีความมาก เพราะ 2.7σ = โซน entry ปกติ แต่ 4σ = โซน stop-loss/โมเดลพังตามเกณฑ์ของเล่มเอง
- **หลักฐาน**: `ขนาด: ใหญ่พอสมควร เพราะ ε − θ = 0.004 (ห่างกัน 4× σ_stat โดยประมาณ)`
- **วิธีแก้**: แก้เป็น 'ห่างกันประมาณ 2.7× σ_stat (σ_stat = 0.003/√(2×2) = 0.0015)'

**Null-hypothesis gaps (เข้าสเปก ch5 §5.0):**
- statarb-ch3.html โจทย์ 3.3 เฉลย: 'ตรวจสอบว่า ADF test ยังผ่านไหม — ถ้าไม่ผ่าน = ε ไม่ stationary แล้ว' — ใช้ภาษา ผ่าน/ไม่ผ่าน ก่อนถึงบทที่ 5 โดยยังไม่เคยบอกผู้อ่านว่า null ของ ADF คือ 'มี unit root (ไม่ stationary)' และ 'ผ่าน' หมายถึง reject null (p ต่ำ) — ผู้อ่านที่ชินกับ 'p ต่ำ = แย่' จะตีความกลับด้าน
- statarb-ch3.html §3.10 สาเหตุที่ 2: 'ถ้าทดสอบ 20 window บน random walk ล้วน ๆ คาดว่าจะพบอย่างน้อย 1 window ที่ดู stationary โดยบังเอิญที่ 5% significance' — อ้าง significance level และ false positive ของการทดสอบ stationarity โดยที่ในบทที่ 0–3 ยังไม่เคยนิยามว่า null hypothesis ของการทดสอบคืออะไร และ 5% วัดจากอะไร


## Cluster: stats (ch4–7) — 13 issues

### 🔴 stats-1. statarb-ch5.html — §5.2 Engle-Granger + §5.5 Running Example (ADF critical values) + caption ภาพ ch
- **ประเภท**: ความรู้ผิด
- **ปัญหา**: ขั้นที่ 2 ของ Engle-Granger ทดสอบ ADF บน residual ที่ 'ประมาณ β มาจากข้อมูล' — การใช้ critical values / p-value ของ ADF มาตรฐาน (−3.44/−2.86/−2.57) กับ residual แบบนี้ผิดตามตำรา เพราะการ estimate β ทำให้ distribution ของ test statistic เลื่อน ต้องใช้ Engle-Granger/MacKinnon cointegration critical values ซึ่ง negative กว่า (ประมาณ −3.90/−3.34/−3.04 สำหรับ 2 ตัวแปร + constant) ผลคือ test ที่เล่มสอน anti-conservative → ประกาศว่า cointegrated ทั้งที่จริงไม่ใช่ (false positive) และทั้ง pipeline §5.8 + rolling monitor §5.9 + ch4 (adfuller(epsilon)) ใช้ p-value ที่ optimistic เกินจริงทั้งหมด
- **หลักฐาน**: `"Critical values: 1%=−3.44, 5%=−2.86, 10%=−2.57" (Running Example §5.5) และ caption "ADF critical values: −3.44 (1%), −2.86 (5%), −2.57 (10%) — test stat ที่ต่ำกว่า critical value → reject H₀" ใช้ในบริบท ADF บน ε̂ จาก OLS`
- **วิธีแก้**: ระบุว่า step 2 ต้องใช้ cointegration (MacKinnon) critical values ไม่ใช่ค่า ADF มาตรฐาน — ใน Python ใช้ statsmodels.tsa.stattools.coint(log_A, log_B) ซึ่งให้ p-value ที่ถูกต้องแทน adfuller(residuals) และแก้ตัวเลข critical values ในตัวอย่าง/ภาพให้เป็นชุด Engle-Granger (−3.90/−3.34/−3.04)

### 🔴 stats-2. statarb-ch4.html — §4.7 Pseudo-code — beta_tls()
- **ประเภท**: สูตรผิด/พิมพ์ผิด
- **ปัญหา**: pseudo-code TLS คืนค่า 1/β ไม่ใช่ β: เมื่อ covariance matrix เรียง [r_A, r_B] (A ก่อน) eigenvector ของ eigenvalue เล็กสุดคือทิศ (1, −β) ดังนั้น -v[0]/v[1] = 1/β — ยืนยันด้วย simulation (β จริง 1.5, closed-form ได้ 1.505 แต่ pseudo-code ได้ 0.665 ≈ 1/1.5) สำหรับคู่ที่ β ห่างจาก 1 เช่น BTC/ETH (β≈1.18) จะได้ hedge ratio ผิดเป็น 0.85 → position ผิดสัดส่วน
- **หลักฐาน**: `C = cov_matrix([[r_A], [r_B]])  # 2×2 ... v = eigenvectors[:, argmin(eigenvalues)] ... return -v[0] / v[1]`
- **วิธีแก้**: return -v[1] / v[0] (เมื่อเรียง A ก่อน B) หรือสลับ order เป็น cov_matrix([[r_B],[r_A]]) แล้วคง -v[0]/v[1]

### 🔴 stats-3. statarb-ch5.html — §5.6 Running Example: BTC/ETH CFD บน MT5
- **ประเภท**: ตัวเลขในตัวอย่างผิด
- **ปัญหา**: สร้าง ε ด้วย β_raw = 0.0444 (slope จาก regression 'ราคาดิบ') คูณกับ 'log price' — ผิดสองชั้น: (1) 0.0444 เป็น raw-price slope ใช้กับ log price ไม่ได้ ch4 §4.6.1 และ Running Example ch4 เตือนเรื่องนี้ตรงๆ ว่า β_log ≈ 1.183 และ 'อย่าใช้ β_raw = 0.0444' (2) ทิศสลับ: raw regression คือ ETH = 0.0444·BTC แต่ตัวอย่างนี้เอา 0.0444 ไปคูณฝั่ง ETH (ε = log BTC − 0.0444·log ETH) — ε ที่ได้แทบเท่ากับ log(BTC) เดี่ยวๆ (non-stationary) ผู้อ่านที่ทำตามจะได้ spread ปลอม
- **หลักฐาน**: `β_OLS = 0.0444 (จาก scatter plot)\nε = log(P_BTC) − 0.0444 × log(P_ETH)`
- **วิธีแก้**: ใช้ให้สอดคล้อง ch4: ε = log(P_ETH) − 1.183 × log(P_BTC) (β_log = 1.183 จาก level regression บน log price)

### 🟠 stats-4. statarb-ch4.html — §4.2b กล่อง 'ความหมายของ β จาก OLS'
- **ประเภท**: ความรู้ผิด
- **ปัญหา**: บอกว่า log(P_B) เพิ่ม 1 หน่วย ≈ B ขยับ +1% — ผิด: log เพิ่ม 1 หน่วยคือราคา ×e (≈ +172%) ส่วน B ขยับ +1% คือ log เพิ่ม ≈ 0.01 หน่วย (ประโยคถัดไป 'B ขยับ 1% → A ขยับ β%' ถูกแล้ว — วงเล็บนี้แหละที่ทำให้ scale เพี้ยน 100 เท่า)
- **หลักฐาน**: `ตีความ: "ถ้า log(P_B) เพิ่มขึ้น 1 หน่วย (≈ B ขยับ +1%) ค่าเฉลี่ยของ log(P_A) ที่ OLS คาดไว้ จะเพิ่มขึ้น β หน่วย"`
- **วิธีแก้**: แก้เป็น "ถ้า log(P_B) เพิ่มขึ้น 0.01 หน่วย (≈ B ขยับ +1%) log(P_A) คาดว่าเพิ่ม 0.01·β หน่วย (≈ A ขยับ β%)"

### 🟠 stats-5. statarb-ch4.html — §4.4 กล่อง 'กับดัก Lookback Selection Bias ใน β' ข้อแรก
- **ประเภท**: อธิบายชวนเข้าใจผิด
- **ปัญหา**: อ้าง 'Kendall-style bias: OLS บน window สั้น underestimate β' — Kendall (1954) small-sample bias เป็นของ AR(1) coefficient φ ไม่ใช่ hedge ratio β; OLS slope ของ cross-regression ไม่ได้ bias ต่ำอย่างเป็นระบบเมื่อ window สั้น และ causal chain ก็ผิด: β ที่ต่ำเกินจริงจะทิ้ง market factor ไว้ใน ε ทำให้ ε ดู 'แย่ลง' ไม่ใช่เรียบขึ้น สิ่งที่เกิดจริงกับ window สั้นคือ in-sample overfit + φ̂ ของ ε bias ต่ำ (Kendall) → half-life ดูสั้นเกินจริง
- **หลักฐาน**: `"Kendall-style bias: OLS บน window สั้น (7 วัน) underestimate β → ε ดูเรียบและ mean-reverting กว่าความเป็นจริง → backtest ดีเกินจริง"`
- **วิธีแก้**: แก้เป็น: window สั้นทำให้ (1) β̂ noisy และ overfit spread ใน sample → ε ใน-sample ดู stationary เกินจริง (2) Kendall bias กด φ̂ ของ ε ต่ำ → half-life ประเมินสั้นเกินจริง — ไม่ใช่ 'β ถูก underestimate'

### 🟠 stats-6. statarb-ch7.html — §7.6 Running Example ตาราง Funding Rate War — แถว 'ช่วง Recovery' (และแถว 'วัน 2
- **ประเภท**: ตัวเลขในตัวอย่างผิด
- **ปัญหา**: แถว Recovery ขัดแย้งในตัวเอง: static z = 2.5 กับ static σ = 0.08% ⇒ ε = 0.20% ⇒ GARCH z = 0.20/0.11 = 1.8 (ไม่ถึง entry 2.0) แต่ตารางเขียน 2.3 (signal) — ข้อสรุปการเทรดกลับด้าน (จริงๆ ต้อง 'ยังไม่เข้า' ไม่ใช่ 'signal') แถววัน 2 ก็คลาดเล็กน้อย: 5.8×0.08/0.23 = 2.0 ไม่ใช่ 1.9
- **หลักฐาน**: `ช่วง Recovery | 0.10% | 0.08% | 2.5 (borderline) | 0.11% | 2.3 (signal)`
- **วิธีแก้**: ทำให้ ε แถวเดียวกันสอดคล้อง: ถ้า ε = 0.25% → static z = 3.1, GARCH z = 2.3 (signal) หรือถ้าคง static z = 2.5 → GARCH z = 1.8 (ไม่เข้า) — เลือกชุดเดียวแล้วแก้ทั้งแถว รวมถึงแถววัน 2 (1.9 → 2.0 หรือปรับ ε)

### 🟠 stats-7. statarb-ch4.html — §4.2 หัวข้อ 'สูตร TLS (Total Least Squares)' บรรทัด SVD
- **ประเภท**: สูตรผิด/พิมพ์ผิด
- **ปัญหา**: สูตร SVD/eigenvector เขียน β_TLS = v₁₂/v₂₂ โดยไม่มีเครื่องหมายลบ — ผลลัพธ์มาตรฐาน (Golub–Van Loan) คือ β_TLS = −v₁₂/v₂₂ เมื่อ data matrix เรียง [x, y] = [r_B, r_A]; ตามที่เขียน (ordering [r_A, r_B]) จะได้ −1/β ยิ่งผิด และยังขัดกับ pseudo-code §4.7 ของเล่มเองที่มีเครื่องหมายลบ
- **หลักฐาน**: `หรือใช้ SVD: β_TLS = v₁₂/v₂₂  (eigenvector ของ covariance matrix [r_A, r_B])`
- **วิธีแก้**: β_TLS = −v₁₂/v₂₂ โดย v คือ eigenvector ของ eigenvalue เล็กสุดของ covariance matrix เรียง [r_B, r_A] (B ก่อน) — ระบุ ordering ให้ตรงกับ pseudo-code §4.7 ที่แก้แล้ว

### 🟠 stats-8. statarb-ch5.html — §5.3 ตารางเลือก test — แถว '2 (pairs)'
- **ประเภท**: อธิบายชวนเข้าใจผิด
- **ปัญหา**: บอกว่า Engle-Granger กับ Johansen 'ผลเท่ากัน' สำหรับ 2 assets — ไม่จริง: EG เป็น regression-based (fix normalization, ผลขึ้นกับทิศ regression ตามที่ §5.2 ของบทเดียวกันเน้นเอง) ส่วน Johansen เป็น ML-based อาจให้ β และผล reject/accept ต่างกันได้ และขัดกับ ch4 โจทย์ 4.0 (ค) ที่แนะนำ 'ลอง Johansen test เพื่อหา β ที่ดีกว่า' เมื่อ EG fail — ถ้าผลเท่ากันจริงคำแนะนำนั้นไร้ความหมาย
- **หลักฐาน**: `2 (pairs) | Engle-Granger | ง่ายกว่า ผลเท่ากัน`
- **วิธีแก้**: แก้เป็น 'ง่ายกว่า — ผลมักใกล้เคียงกันสำหรับ 2 ขา แต่ไม่เหมือนกันเสมอ (Johansen อาจพบ cointegration ที่ EG พลาด และไม่ขึ้นกับทิศ regression)'

### 🟠 stats-9. statarb-ch5.html — §5.5 Running Example Step 1 — การตีความ β = 1.0049
- **ประเภท**: อธิบายชวนเข้าใจผิด
- **ปัญหา**: เขียนว่า 'Bybit เคลื่อนไหว 0.49% มากกว่า Lighter ต่อการขยับ 1%' — อ่านตามตัวอักษรคือ Bybit ขยับ 1.49% ต่อ Lighter 1% (ผิด 100 เท่า) ค่าจริงคือ Bybit ขยับ 1.0049% คือมากกว่าเพียง 0.0049 percentage point (0.49% เชิงสัมพัทธ์ของขนาด move)
- **หลักฐาน**: `→ β > 1.0 แปลว่า Bybit เคลื่อนไหว 0.49% มากกว่า Lighter ต่อการขยับ 1% ของ Lighter`
- **วิธีแก้**: แก้เป็น 'Lighter ขยับ 1% → Bybit ขยับ 1.0049% (มากกว่า 0.0049 จุดเปอร์เซ็นต์ หรือ ~0.5% เชิงสัมพัทธ์)'

### 🟠 stats-10. statarb-ch6.html — §6.1 กล่อง 'ข้อปฏิบัติจริง — Rolling Window สำหรับ μ และ σ' และกล่อง 'Model Risk
- **ประเภท**: อธิบายชวนเข้าใจผิด
- **ปัญหา**: สองกล่องนี้เป็นเนื้อหา z-score (μ_ε, σ_ε, threshold ±2) หลุดมาอยู่กลางหัวข้อ Hurst exponent โดยบทนี้ยังไม่เคยนิยาม z-score (นิยามอยู่ ch10) — ผู้อ่านเจอสัญลักษณ์ที่ไม่เคยแนะนำและเนื้อหาไม่เชื่อมกับ H เลย สอดคล้องกับชื่อไฟล์ภาพในบทที่ยังเป็นของเดิม (ch6-zscore-signal.svg, ch6-zscore-dist.svg) ทั้งที่ caption พูดเรื่อง Hurst/R-S
- **หลักฐาน**: `"ให้ใช้ rolling window 30 วัน ... เพื่อให้ z-score ปรับตัวตาม regime ล่าสุด" อยู่ใต้หัวข้อ '6.1 H วัดอะไร — สามโหมดของ Time Series'`
- **วิธีแก้**: ย้ายสองกล่องนี้ไป ch10 (Z-score) หรือเขียนประโยคเชื่อมว่าเกี่ยวกับ H อย่างไร และเปลี่ยนชื่อไฟล์ภาพเป็น ch6-hurst-three-modes.svg / ch6-hurst-rs-loglog.svg ให้ตรงเนื้อหา

### 🟡 stats-11. statarb-ch6.html — §6.5 Pseudo-code hurst_rs() — comment เรื่อง Jensen's inequality
- **ประเภท**: อธิบายชวนเข้าใจผิด
- **ปัญหา**: comment ขัดแย้งในตัวเอง: 'bias H สูงขึ้น (overestimate mean-reversion)' — H สูงขึ้น = persistent/trending มากขึ้น = mean-reversion ดู 'น้อยลง' ไม่ใช่มากขึ้น (ยืนยันทิศด้วย simulation: log(mean) ให้ H สูงกว่า mean(log) เล็กน้อยจริง แต่ H สูง = underestimate mean-reversion)
- **หลักฐาน**: `# การใช้ log(mean()) จะ bias H สูงขึ้น (overestimate mean-reversion)`
- **วิธีแก้**: แก้วงเล็บเป็น '(ทำให้ดู persistent เกินจริง → underestimate mean-reversion)'

### 🟡 stats-12. statarb-ch7.html — โจทย์ 7.2
- **ประเภท**: ตัวเลขในตัวอย่างผิด
- **ปัญหา**: 0.48/0.14 = 3.43 (ปัดเป็น 3.4) ไม่ใช่ 3.5 — ไม่กระทบข้อสรุป แต่เป็นเลขคำนวณที่แสดงเป็นสมการตรงๆ
- **หลักฐาน**: `Naive z = 0.48/0.14 = 3.5`
- **วิธีแก้**: แก้เป็น Naive z = 0.48/0.14 ≈ 3.4

### 🟡 stats-13. statarb-ch4.html — ทุกจุดที่อ้าง <img src="charts/..."> (ch4: 8 ภาพ, ch5: 6, ch6: 2, ch7: 2)
- **ประเภท**: อื่นๆ
- **ปัญหา**: โฟลเดอร์ docs/charts/ ไม่มีอยู่ใน repo เลย — ภาพประกอบทั้ง 18 จุดใน ch4–ch7 (เช่น ch4-ols-vs-tls.svg, ch5-adf-critical.svg, ch6-zscore-signal.svg, ch7-entry-exit-zones.svg) เป็นลิงก์เสียทั้งหมด ผู้อ่านจะเห็นแค่ alt text จึงตรวจปัญหา label/ตัวหนังสือทับกันในภาพไม่ได้ด้วย
- **หลักฐาน**: `ls docs/charts/ → No such file or directory; แต่ ch4 อ้าง src="charts/ch4-ols-vs-tls.svg" ฯลฯ รวม 18 จุด`
- **วิธีแก้**: สร้าง/นำเข้าไฟล์ SVG ใน docs/charts/ ให้ครบตามรายชื่อที่อ้าง หรือเอา <img> ออกจนกว่าจะมีภาพจริง

**Null-hypothesis gaps (เข้าสเปก ch5 §5.0):**
- ch4 §4.2b-3/§4.2b-4: ใช้ p-value ของ β (model.pvalues[1] 'ต้องการ ≪ 0.05', ตาราง 'p < 0.05 → β มีนัยสำคัญ') เป็นจุดแรกๆ ของเล่มที่ผู้อ่านเจอ p-value โดยไม่เคยอธิบายว่านี่คือ t-test ของ slope ที่มี H0: β = 0 และ reject แปลว่าอะไร/ไม่แปลว่าอะไร (เช่น ไม่ได้แปลว่า cointegrated)
- ch4 §4.2b-4 ตาราง 'ADF / KPSS ... ADF p < 0.05, KPSS p > 0.05': ใช้สองเกณฑ์ทิศตรงข้ามกันโดยไม่อธิบาย ณ จุดใช้ว่า H0 ของ ADF = มี unit root (ต้องการ reject) ส่วน H0 ของ KPSS = stationary (ต้องการ fail to reject) — ADF H0 มาอธิบายใน ch5 และ KPSS H0 มาอธิบายครั้งแรกใน ch6 §6.3 เท่านั้น ผู้อ่านที่อ่านตามลำดับบทจะไม่เข้าใจว่าทำไม KPSS ต้องการ p สูง
- ch4 §4.6.2 Test 2 (factor regression): 'γ ≈ 0 (p-value > 0.05) → hedged ดี' — ไม่ระบุ H0: γ = 0 และใช้ fail-to-reject เป็นการยืนยันว่า γ = 0 จริง ซึ่งต้องมีบทเรียนว่า p > 0.05 ไม่ใช่หลักฐานว่า H0 จริง (ขึ้นกับ power/sample size)
- ch4 ข้อจำกัดที่ 6 (Gauss-Markov): แนะนำ Durbin-Watson ด้วย heuristic 'DW ≈ 2 = ดี' โดยไม่บอกว่า DW เป็น hypothesis test ที่มี H0: ไม่มี first-order autocorrelation ใน residual
- ch5 §5.2 กล่อง 'ปรับ Position Size ตาม p-value — ใช้ p-value เป็น confidence score': ตีความ p-value เป็นระดับความเชื่อมั่นว่า pair cointegrate จริง (P(H0 ผิด|data)) ซึ่งผิดนิยาม — p-value คือ P(เห็น statistic สุดขั้วเท่านี้ | H0 จริง) บทเรียน null hypothesis ควรอธิบายความต่างนี้ก่อนสอนใช้ p เป็น sizing input
- ch4 §4.4 'ลอง 5 window แล้วเลือกที่ดีที่สุด = ทำ 5 tests โดยไม่ปรับ p-value → false positive เพิ่ม 5×': อ้าง multiple testing / การปรับ p-value โดยเล่มไม่เคยอธิบายว่า false positive ภายใต้ H0 คืออะไร และการคูณ 5 มาจากไหน (family-wise error rate) — ควรผูกกับบทเรียน H0/p-value เดียวกัน


## Cluster: advanced-model (ch8–10, 15, 23) — 19 issues

### 🔴 advanced-model-1. statarb-ch23.html — §23.3 running example (บรรทัด ~168) และ pseudo-code §23.9
- **ประเภท**: ความรู้ผิด
- **ปัญหา**: อ้างว่า Ch.4 §4.2b ให้ 'log-price β ≈ 0.04–0.06' และให้เหตุผลว่า 'BTC ≈ 25× ETH → β ≈ 1/25 ≈ 0.04' พร้อมสั่งให้ใช้ค่านี้สร้าง spread ε = log(P_A) − β·log(P_B) — ผิดทั้งคณิตและขัดกับ Ch.4 เอง: การคูณราคาด้วย 25 ใน log-space เป็นการเลื่อน intercept ไม่ใช่ slope; Ch.4 ระบุชัดว่า β_log = 1.183 ส่วน 0.0444 คือ β_raw (slope บน raw price ที่ขึ้นกับ scale และ Ch.4 เตือนว่า 'หลอกตา') ถ้าผู้อ่านใช้ β=0.04 กับ log-price จะได้ ε ≈ log(P_BTC) เกือบล้วนๆ = position แทบไม่ hedge เลย
- **หลักฐาน**: `ch23: "log-price β ≈ 0.04–0.06 ... (BTC ≈ 25× ETH → β ≈ 1/25 ≈ 0.04) ... สำหรับ spread construction ε = log(P_A) − β·log(P_B) ให้ใช้ log-price β จาก Ch.4 เสมอ" — แต่ ch4 บรรทัด 384: "β_log = 1.183 ≠ β_raw = 0.0444"`
- **วิธีแก้**: แก้เป็น: log-price β ของ BTC/ETH จาก Ch.4 คือ ≈ 1.18 (ค่า 0.0444 คือ raw-price slope ที่ขึ้นกับ scale ห้ามใช้กับ log-spread) และตัดเหตุผล 1/25 ทิ้ง — อธิบายแทนว่า log-return β กับ log-price β ใกล้กัน (~1.0–1.2) เพราะ log ตัด scale ราคาออกแล้ว

### 🔴 advanced-model-2. statarb-ch10.html — §10.1 ตาราง z-score ranges (บรรทัด 78–90) และ SVG zscore-bands
- **ประเภท**: ความรู้ผิด
- **ปัญหา**: ทิศทางสัญญาณกลับข้างจากหลัก mean reversion ของทั้งเล่ม: ตารางบอก z > 2.0 = 'Strong long signal / Enter long ε' และ z ≤ −2.0 = 'Enter short ε (sell cheap leg, buy expensive leg)' — mean reversion ต้อง SHORT ε เมื่อ z > +2 (spread แพงเกิน) และ LONG ε เมื่อ z < −2 (ch23 โจทย์ 23.3 ยืนยัน: ε = +2.4σ → 'SHORT Y (Enter)') วงเล็บของแถว z>2 ('buy cheap leg, sell expensive leg') คือการ short ε ซึ่งขัดกับ label 'long ε' ของตัวเอง และวงเล็บของแถว z≤−2 ('sell cheap leg, buy expensive leg') เป็น trade สวน mean reversion ตรงๆ ถ้าผู้อ่านทำตาม label จะเทรดผิดข้างทุกไม้
- **หลักฐาน**: `"z > 2.0 | Strong long signal | Enter long ε (buy cheap leg, sell expensive leg)" และ "z ≤ −2.0 | Strong short signal | Enter short ε (sell cheap leg, buy expensive leg)"`
- **วิธีแก้**: z > +2.0 → Enter SHORT ε (sell expensive leg A, buy cheap leg B); z ≤ −2.0 → Enter LONG ε (buy cheap leg A, sell expensive leg B) และแก้แถว hold ให้สอดคล้อง (z บวก = ถือ short ε)

### 🔴 advanced-model-3. statarb-ch23.html — §23.9 Pipeline รวม และตาราง Cross-Reference §23.10
- **ประเภท**: อื่นๆ
- **ปัญหา**: Gap สำคัญตรงกับที่ผู้ใช้รายงานขาดทุน: pipeline §23.9 อัปเดต β ทุก bar และใช้ β_t สร้าง ε ทันที แต่ไม่มีคำเตือนเรื่อง rebalancing cost / deadband เลย (ไม่มี |Δβ| threshold ก่อนปรับ position, ไม่มี cost-vs-benefit check) ทั้งที่ ch15 §15.7 + โจทย์ 15.3 มีครบ ('อย่าปรับทุก tick เพราะ transaction cost กินกำไร', threshold |Δβ|>0.01) — และตาราง cross-reference §23.10 ลิสต์ ch3,4,5,10,12,18,22 แต่ไม่อ้างถึง ch15 แม้แต่บรรทัดเดียว ผู้อ่านที่เข้าบท advanced นี้โดยตรงจะปรับ position ตาม β ทุก bar แล้วโดน fee กิน
- **หลักฐาน**: `§23.9 มีเพียง Entry/Exit/Stop ("Entry: |z_t| ≥ t_{α/2}(ν) AND Kalman gain K_t < 0.3 ... Exit: |z_t| ≤ 0.5 ... Stop: |z_t| ≥ 3 × t_{α/2}(ν)") ไม่มีข้อความใดกล่าวถึง transaction cost/deadband ของการปรับ β; ตาราง §23.10 ไม่มีแถว ch15`
- **วิธีแก้**: เพิ่มขั้นที่ 6 ใน pipeline: rebalance hedge เฉพาะเมื่อ |β_t − β_last_traded| > threshold ที่ calibrate จาก fee (อ้าง ch15 §15.7 และโจทย์ 15.3) และเพิ่ม ch15 ในตาราง cross-reference พร้อมคำเตือนว่า Q ใหญ่เกิน → β วิ่งตาม noise → rebalance ถี่จน fee กินกำไร

### 🟠 advanced-model-4. statarb-ch23.html — §23.5 (ผลต่อ Trading Signals), §23.7 ตาราง critical values, §23.9 step 3–4
- **ประเภท**: ความรู้ผิด
- **ปัญหา**: Scale mismatch ระหว่าง z-score กับ t critical value: pipeline คำนวณ z_t = ε_t/σ_t โดย σ_t คือ rolling std (ทำให้ z มี variance ≈ 1) แล้วเทียบกับ t_{α/2}(ν) ซึ่งเป็น quantile ของ t ที่ยังไม่ standardize (variance = ν/(ν−2)) — ถ้า ε เป็น scaled-t(4) จริง quantile 97.5% ของ z หน่วย unit-variance คือ 2.776×√(2/4) = 1.963 ≈ 1.96 เท่า Normal เลย ไม่ใช่ 2.776 ดังนั้น 'α=5%' ที่อ้างไม่เป็นจริง (effective α ~1–2%) เช่นเดียวกับ §23.5 ที่อ้าง 'excess kurtosis = 6: P(|z| > 2.0) ≈ 8–12%' — คำนวณจริงสำหรับ standardized t(5): P(|z|>2) = 4.9% (10.2% คือค่าของ t ที่ไม่ standardize) โค้ด MLE fit ได้ scale ออกมาแล้วแต่โยนทิ้งไม่ใช้
- **หลักฐาน**: `"Estimate σ_t: คำนวณ rolling std ของ ε_t ... ได้ z_t = ε_t / σ_t" + "threshold = t_{α/2}(ν) แทน 1.96" และ "P(|z| > 2.0) ≈ 8–12% จริงๆ" (คำนวณยืนยัน: standardized t(5) ให้ 4.93%; t(4) unit-variance quantile 97.5% = 1.963)`
- **วิธีแก้**: ใช้ scale จาก t.fit: threshold บน ε คือ scale×t_{α/2}(ν) หรือเทียบ z กับ t_{α/2}(ν)×√((ν−2)/ν) — หรืออธิบายตรงๆ ว่า 2.78 เป็นการเลือก threshold แบบ conservative ไม่ใช่ 'α=5% ที่ถูกต้องทางสถิติ' และแก้ตัวเลข 8–12% เป็นค่า standardized (~5% ที่ 2σ; ต่างชัดที่ 3–4σ)

### 🟠 advanced-model-5. statarb-ch23.html — §23.9 pseudo-code entry condition และ 'คณิตที่พัง' (cap K_max = 0.3)
- **ประเภท**: สูตรผิด/พิมพ์ผิด
- **ปัญหา**: Guard 'K < 0.3' พังเมื่อ x_t (ETH log-return) ติดลบ: K = P_prior·x_t/S มีเครื่องหมายตาม x_t ดังนั้น bar ที่ ETH ลงจะได้ K < 0 → เงื่อนไข K < 0.3 ผ่านเสมอไม่ว่า β กำลัง update เร็วแค่ไหน guard นี้จึงใช้ไม่ได้ครึ่งหนึ่งของเวลา
- **หลักฐาน**: `"K = P_prior * x_t / S" ตามด้วย "if abs(z_t) >= threshold and K < 0.3" — ไม่มี abs()`
- **วิธีแก้**: ใช้ abs(K) < 0.3 หรือดีกว่านั้นใช้ K·x_t (สัดส่วน innovation ที่ถูกดูดเข้า estimate ซึ่งอยู่ใน [0,1) เสมอ) เป็นตัว guard

### 🟠 advanced-model-6. statarb-ch15.html — §15.3 'ความหมายของ Kalman Gain K_t'
- **ประเภท**: ความรู้ผิด
- **ปัญหา**: อ้างว่า 'K_t อยู่ระหว่าง 0 ถึง 1' — ไม่จริงสำหรับ model นี้ (observation H = r_B): K = P·r_B/(r_B²P + R) ติดลบเมื่อ r_B < 0 และเกิน 1 ได้เมื่อ P ใหญ่ (เช่น P=1, R=1e-3, r_B=0.03 → K ≈ 15.7) ปริมาณที่อยู่ใน [0,1) จริงคือ K·r_B ข้อความนี้ยังขัดกับ ch23 ที่ต้องเขียน qualifier '(สำหรับ log-return inputs ที่ x_t ≪ 1)'
- **หลักฐาน**: `"K_t อยู่ระหว่าง 0 ถึง 1 และบอกว่า 'เชื่อข้อมูลใหม่มากแค่ไหน'"`
- **วิธีแก้**: แก้เป็น: ปริมาณ K_t·r_{B,t} อยู่ใน [0,1) และเป็นตัววัดน้ำหนักที่ให้ observation ใหม่; ตัว K_t เองมีเครื่องหมายและ scale ตาม r_B

### 🟠 advanced-model-7. statarb-ch15.html — §15.2 ตารางพารามิเตอร์ แถว R (บรรทัด 131)
- **ประเภท**: ตัวเลขในตัวอย่างผิด
- **ปัญหา**: แปลง variance เป็น std ผิด 10 เท่า: R=0.01 → std = √0.01 = 0.1 = 10% (ไม่ใช่ 1%) และ R=0.001 → std = √0.001 ≈ 3.2% (ไม่ใช่ 0.3%) ทำให้ผู้อ่าน calibrate R ผิด 100 เท่าใน variance scale
- **หลักฐาน**: `"R=0.01 → return std ≈ 1%; R=0.001 → ≈ 0.3%"`
- **วิธีแก้**: R=1e-4 → std = 1%; R=1e-5 → std ≈ 0.32% (หรือแก้ตัวเลข std ของแถวเดิมเป็น 10% / 3.2%) ให้สอดคล้องกับช่วงแนะนำ R ≈ 1e-4–1e-3 สำหรับ hourly BTC

### 🟠 advanced-model-8. statarb-ch15.html — โจทย์ 15.1 คำตอบ (ประโยคสรุปท้าย)
- **ประเภท**: ความรู้ผิด
- **ปัญหา**: สรุปกลับทิศ: 'หลัง warmup K จะเพิ่มขึ้นตามข้อมูลสะสม' — Kalman filter ทำงานตรงข้าม: ช่วง warm-up (P สูง) K สูง แล้ว P ลดลงเมื่อข้อมูลสะสม → K ลดลงเข้าสู่ steady state ขัดกับ §15.3 ของบทเดียวกันที่เขียนถูก ('ระยะแรก (P สูง): K สูง ... เมื่อ P ลด: K ลด')
- **หลักฐาน**: `"β ปรับขึ้นเล็กมากเพราะ K เล็ก (P เล็ก = confident ใน prior) — หลัง warmup K จะเพิ่มขึ้นตามข้อมูลสะสม"`
- **วิธีแก้**: แก้เป็น: K เล็กเพราะโจทย์กำหนด P เริ่มต้นเล็ก (0.001) — ถ้าเริ่มด้วย P₀ = 1.0 ตาม warm-up ปกติ K ช่วงแรกจะใหญ่แล้วลดลงเมื่อ estimate นิ่ง

### 🟠 advanced-model-9. statarb-ch15.html — §15.8 Running Example — β Drift
- **ประเภท**: ตัวเลขในตัวอย่างผิด
- **ปัญหา**: เส้นทาง β 0.98 → 1.05 ใน 5 จุด (2 ชั่วโมง) เป็นไปไม่ได้ด้วยพารามิเตอร์ที่ให้ (P=0.001, Q/R ตาม default บท = 1e-5/1e-3, returns ~0.1–0.2%): โจทย์ 15.1 ของบทเดียวกันแสดงว่า 1 update ด้วยค่า scale เดียวกันขยับ β เพียง ~3.6e-7 — ต่อให้อัปเดตทุกนาที gain K ≈ P·r_B/R ~ 1e-3 ก็ขยับ β ได้ ~1e-7 ต่อ step ไม่มีทางถึง 0.07 ใน 2 ชม. ทำให้ผู้อ่านเข้าใจความเร็ว tracking ของ Kalman ผิดหลาย order of magnitude
- **หลักฐาน**: `"เริ่มต้น: beta = 0.98, P = 0.001 ... t=0.5h: ... beta ≈ 0.995 ... t=2.0h: ... beta ≈ 1.05 ✓"`
- **วิธีแก้**: ใช้ P เริ่มต้น/Q ที่ใหญ่ขึ้นมาก (เช่น P=0.5, Q=1e-3) พร้อมระบุไว้ในตัวอย่าง หรือปรับ timeline เป็นหลายวัน/ระบุจำนวน update ต่อจุดให้ตัวเลข consistent กับโจทย์ 15.1

### 🟠 advanced-model-10. statarb-ch9.html — §9.7 Running Example — Normal Regime
- **ประเภท**: ตัวเลขในตัวอย่างผิด
- **ปัญหา**: σ = 0.002 → ±2σ = ±0.004 → บน BTC $65,000 คือ ±$260 ไม่ใช่ ±$130 ($130 คือ 1σ)
- **หลักฐาน**: `"σ ของ spread ≈ 0.002 → entry ที่ ±2σ ≈ ±$130 บน $65,000 BTC"`
- **วิธีแก้**: แก้เป็น ±2σ ≈ ±$260 (หรือเปลี่ยนเป็น ±1σ ≈ ±$130 ถ้าตั้งใจ)

### 🟠 advanced-model-11. statarb-ch9.html — §9.5 ตาราง action vs §9.7 code output vs §9.8 ตาราง 3-Regime
- **ประเภท**: อธิบายชวนเข้าใจผิด
- **ปัญหา**: เกณฑ์ขัดกันเองภายในบทโดยไม่มีคำอธิบาย: (1) §9.5 สั่งปิด position ทั้งหมดเมื่อ P(Broken) > 0.20 แต่ §9.8 ใช้ hard stop ที่ P(Broken) > 0.5 และกล่อง 'บนโต๊ะจริง' ใช้ 0.4; (2) ตัวอย่าง §9.7 ให้ P(Normal)=0.42 แล้วบอก 'ลด size 75%' ทั้งที่กฎ §9.5 (p_normal < 0.50 → else branch) สั่งหยุดเทรด/ปิด position; (3) §9.5 ให้เทรด 25% ที่โซน 0.50–0.70 แต่ §9.8 ให้ 50% ที่ 0.3 < P(Normal) < 0.7 — ผู้อ่านไม่รู้จะใช้ชุดไหน
- **หลักฐาน**: `§9.5: "any any >0.20 → ปิด position ทั้งหมด (Broken)" vs §9.8: "P(S=Broken) > 0.5 → Hard stop" vs §9.7 output: "P(Normal)=0.42, P(Stressed)=0.51, P(Broken)=0.07 → ลด size 75%"`
- **วิธีแก้**: เลือกชุดเกณฑ์เดียวเป็น canonical (เช่นของ §9.8) แล้วให้ §9.5/§9.7 อ้างชุดเดียวกัน หรือใส่หมายเหตุชัดๆ ว่าตัวเลขต่างกันเพราะ context ใด

### 🟠 advanced-model-12. statarb-ch8.html — §8.7 Running Example vs โจทย์ 8.3 คำตอบ
- **ประเภท**: อธิบายชวนเข้าใจผิด
- **ปัญหา**: ทิศทางเศรษฐศาสตร์ของ funding rate ขัดแย้งกันเอง: §8.7 บอก Bybit ขึ้น funding เป็น 0.09%/8h 'เพื่อดึง short position' แล้ว 'Bybit perp premium เพิ่มขึ้นทันทีจาก $10 → $80' — แต่ funding บวกสูง = long จ่าย short → short ไหลเข้า/long ปิด → แรงขาย perp → premium ควรหดลง ไม่ใช่พุ่ง 8 เท่า และคำตอบโจทย์ 8.3 ในบทเดียวกันก็บอกตรงข้ามว่า 'jump จาก funding rate war อาจกดดัน Bybit premium ซึ่งเป็น favorable' สำหรับ Short Bybit — สอง section เล่าเหตุการณ์เดียวกันคนละทิศ
- **หลักฐาน**: `§8.7: "ปรับ funding rate เป็น 0.09% ... เพื่อดึง short position ... Bybit perp premium เพิ่มขึ้นทันทีจาก $10 → $80" vs โจทย์ 8.3: "jump จาก funding rate war อาจกดดัน Bybit premium ซึ่งเป็น favorable"`
- **วิธีแก้**: เลือกกลไกเดียวให้ consistent: ถ้า premium สูงเป็นเหตุ (จน funding ตามขึ้น) ให้เล่าว่า premium spike มาก่อนแล้ว funding ปรับตาม; ถ้า funding ขึ้นเป็นเหตุ ให้ premium หด/ติดลบ และแก้ทิศใน 8.7 หรือ 8.3 ให้ตรงกัน

### 🟠 advanced-model-13. statarb-ch10.html — Exercise 10.1 คำตอบ ข้อ (c)–(d)
- **ประเภท**: ตัวเลขในตัวอย่างผิด
- **ปัญหา**: ข้อ (b) หา MAD = 0.01% ถูกต้อง แต่ข้อ (c) กลับใช้ 0.02 คูณ: 'σ_robust: 0.02 × 1.4826 = 0.02965%' — ค่าที่ถูกคือ 0.01 × 1.4826 = 0.01483% (ข้อ (d) ได้ 0 เหมือนเดิมโดยบังเอิญเพราะเศษเป็นศูนย์)
- **หลักฐาน**: `"(b) ... MAD = 0.01%" ตามด้วย "(c) σ_robust: 0.02 × 1.4826 = 0.02965%"`
- **วิธีแก้**: แก้ (c) เป็น σ_robust = 0.01 × 1.4826 = 0.01483% และ (d) ตัวหารเป็น 0.01483

### 🟠 advanced-model-14. statarb-ch10.html — §10.3 กล่อง Result
- **ประเภท**: ตัวเลขในตัวอย่างผิด
- **ปัญหา**: อ้างว่า 'outlier moves the median by exactly 0 in this example' — ไม่จริง: median ของชุด clean = (0.10+0.11)/2 = 0.105% ส่วนชุดที่มี outlier = 0.11% → median เลื่อน +0.005% (n คู่ median คือค่าเฉลี่ยคู่กลาง ไม่ใช่ 'middle value' เดี่ยว) ข้อสรุปเรื่อง robustness ยังถูก แต่คำว่า 'exactly 0' ผิด
- **หลักฐาน**: `"The outlier moves the median by exactly 0 in this example (median is the middle value of a sorted list)"`
- **วิธีแก้**: แก้เป็น: outlier เลื่อน median เพียง +0.005% (0.105 → 0.11) เทียบกับ mean ที่เลื่อน +0.07% — เล็กกว่า ~14 เท่า

### 🟠 advanced-model-15. statarb-ch10.html — §10.5 ตารางเปรียบเทียบ แถว Efficiency
- **ประเภท**: ความรู้ผิด
- **ปัญหา**: 'Robust Z (MAD) ~64% efficient under Normality' — 64% คือ asymptotic efficiency ของ median (location) เทียบ mean (2/π ≈ 63.7%) ส่วน MAD ในฐานะ scale estimator มี efficiency เทียบ SD เพียง ~37% (Huber) — ตารางระบุคอลัมน์เป็น (MAD) จึงให้ตัวเลขผิดตัว
- **หลักฐาน**: `"Efficiency (clean data) | 100% efficient under Normality | ~64% efficient under Normality" ในคอลัมน์ Robust Z (MAD)`
- **วิธีแก้**: แยกระบุ: median มี efficiency ~64% (location), MAD ~37% (scale) ภายใต้ Normal — ราคาที่จ่ายเพื่อ robustness

### 🟠 advanced-model-16. statarb-ch10.html — Running Example ตาราง + ย่อหน้า Decision
- **ประเภท**: อธิบายชวนเข้าใจผิด
- **ปัญหา**: ย่อหน้า Decision เรียก standard z=3.2 ที่ ε=0.32% ว่า 'false alarm ... driven by inflated σ from the spike' — กลับทิศ: σ ที่ inflate ทำให้ z เล็กลง (จาก 14.7 เหลือ 3.2) ไม่ใช่สร้าง alarm ปลอม และ robust z ของ bar เดียวกัน = 14.7 ยิ่ง confirm สัญญาณแรงกว่า — ถ้า ε=0.32% เป็นสัญญาณจริง มันไม่ใช่ false alarm; ถ้าเป็น glitch robust z ยิ่งหลอกหนักกว่า คำอธิบายจึงขัดแย้งกับตารางของตัวเอง
- **หลักฐาน**: `"The standard z produced a false alarm at ε=0.32% (z=3.2 suggesting strong signal, but driven by inflated σ from the spike)" ขณะที่ตารางแถวเดียวกันให้ Robust z = 14.7`
- **วิธีแก้**: เขียนใหม่ให้ตรง: σ ที่ inflate กด z ลง (14.7 → 3.2) ทำให้ standard z 'พลาด/ลดทอน' สัญญาณ — จุดขายของ robust z คือกู้สัญญาณที่ถูกกดคืนมา ไม่ใช่กรอง false alarm ในกรณีนี้

### 🟠 advanced-model-17. statarb-ch23.html — โจทย์ 23.3 คำตอบ (ค)
- **ประเภท**: อธิบายชวนเข้าใจผิด
- **ปัญหา**: อ้างว่า '42% ของ signal ที่ Normal เห็น (โซน 1.96–2.78) จะไม่ถูกนับ' — 42% คือเปอร์เซ็นต์ที่ threshold สูงขึ้น (2.776/1.96 − 1) ไม่ใช่สัดส่วนของสัญญาณ: ภายใต้ Normal สัดส่วน |z|>1.96 ที่ตกในโซน 1.96–2.78 คือ ~89% ภายใต้ t(4) ที่ไม่ standardize ~58% — ไม่มีกรณีไหนเป็น 42%
- **หลักฐาน**: `"สำคัญคือ 42% ของ signal ที่ Normal เห็น (โซน 1.96–2.78) จะไม่ถูกนับใน t-distribution"`
- **วิธีแก้**: แก้เป็น 'threshold เข้มขึ้น 42%' และถ้าจะพูดถึงสัดส่วนสัญญาณ ให้คำนวณจริง (สัญญาณ Normal ส่วนใหญ่ ~60–90% ตก zone นี้ ขึ้นกับ distribution จริง)

### 🟠 advanced-model-18. statarb-ch8.html — ทุก <img class="chart"> ใน 5 บทของชุดนี้ (ch8: fat-tail-hist, jump-detection; ch
- **ประเภท**: ภาพ:label หาย/ผิด
- **ปัญหา**: โฟลเดอร์ docs/charts/ ไม่มีอยู่ในโปรเจกต์ → รูปประกอบทุกรูปใน ch8/ch9/ch10/ch15/ch23 (รวม 13 ไฟล์ .svg ที่ถูกอ้าง) เป็นรูปแตก ผู้อ่านเห็นแค่ caption ลอยๆ (ch9/ch10 มี SVG สำรองแต่ถูกซ่อนด้วย display:none จึงไม่ช่วย)
- **หลักฐาน**: `<img class="chart" src="charts/ch8-fat-tail-hist.svg"> ฯลฯ แต่ `ls docs/charts/` → 'No such file or directory'`
- **วิธีแก้**: สร้าง/รวมโฟลเดอร์ charts พร้อมไฟล์ svg ตามชื่อที่อ้าง หรือเปลี่ยนมาใช้ inline SVG ที่มีอยู่แล้ว (เอา display:none ออกใน ch9/ch10)

### 🟡 advanced-model-19. statarb-ch10.html — caption ใต้รูป ch10-zscore-bands (บรรทัด 141)
- **ประเภท**: อธิบายชวนเข้าใจผิด
- **ปัญหา**: Caption ขัดกับตาราง §10.1 และกับ SVG สำรองของตัวเอง: caption ว่า stop-loss ที่ |z|>3 และ entry zone 2<|z|<3 แต่ตารางใช้ stop-loss 3.5 และ entry |z|>2.0 (ไม่มีเพดาน 3) ส่วน SVG วาด band ที่ ±1/±2 พร้อม label '1<z≤2' เป็น amber; caption ยังพูดถึง 'green triangles' ที่ในรูปเป็นวงกลม
- **หลักฐาน**: `caption: "RED zone = |z|>3 (stop-loss), AMBER zone = 2<|z|<3 (entry)" vs ตาราง: "|z| > 3.5 | Stop-loss zone"`
- **วิธีแก้**: ทำ caption/ตาราง/รูปให้ใช้เกณฑ์เดียวกัน (entry |z|>2, stop 3.5)

**Null-hypothesis gaps (เข้าสเปก ch5 §5.0):**
- ch8 §8.5: อ้าง 'threshold=4.0 เทียบเท่ากับ p-value < 0.001' ของ Lee-Mykland test โดยทั้งบทไม่เคยระบุ null hypothesis (H0 = ไม่มี jump ที่เวลา t; increment มาจาก pure diffusion ที่ locally Normal) — ผู้อ่านไม่รู้ว่า p-value นี้วัดความน่าจะเป็นของอะไรภายใต้สมมติฐานไหน
- ch23 §23.10 (และ prerequisite §5.6 ที่ถูกอ้าง): กฎ 'Shapiro-Wilk: ถ้า p ≥ 0.05 ใช้ Normal; ถ้า p < 0.05 ใช้ t-distribution' ถูกใช้ใน ch23 โดยไม่บอกว่า H0 ของ Shapiro-Wilk คือ 'residuals เป็น Normal' — และไม่เตือนว่า p ≥ 0.05 ไม่ได้พิสูจน์ความเป็น Normal (แค่ไม่มีหลักฐานพอปฏิเสธ โดยเฉพาะเมื่อ sample เล็ก/test power ต่ำ)
- ch23 §23.7–23.8: ใช้ภาษา hypothesis testing เต็มรูป ('two-tailed α=5%', '95% confidence', 'significant') กับ entry threshold โดยไม่เคยระบุ null ที่แฝงอยู่ (H0 = ε อยู่ที่ mean ของมัน / ไม่มี dislocation ให้เทรด) — ผู้อ่านที่ไม่รู้ H0 จะตีความ α=5% ว่าเป็น 'โอกาสขาดทุน 5%' ซึ่งผิดความหมาย


## Cluster: execution (ch11–14, 16) — 17 issues

### 🟠 execution-1. statarb-ch12.html — §12.4 กล่องแดง 'ตัวอย่าง: Max Drawdown เป็น Binding Constraint'
- **ประเภท**: ความรู้ผิด
- **ปัญหา**: อธิบายทิศทางกลับด้าน: บอกว่า drawdown limit เป็น binding เมื่อ entry_z ต่ำ แต่จากสูตร size_DD = max_loss/(entry_z·σ) ค่า entry_z ต่ำจะทำให้ dd_limit ใหญ่ขึ้น (binding น้อยลง) — entry_z สูงต่างหากที่ทำให้ dd_limit เล็กลงและ binding; ขัดกับหมายเหตุใน §12.5 ของบทเดียวกันที่บอกว่า 'ยิ่ง entry ที่ z สูง position ยิ่งต้องเล็กลง'
- **หลักฐาน**: `สถานการณ์นี้เกิดขึ้นเมื่อ entry_z ต่ำ (เช่น z = 2.0 ต่ำกว่า z = 3.5) หรือ σ_spread สูง`
- **วิธีแก้**: แก้เป็น 'เกิดขึ้นเมื่อ entry_z สูง หรือ σ_spread สูง' (หรือถ้าตั้งใจสื่อว่า Kelly ใหญ่กว่า dd_limit เพราะ dd_limit เล็ก ให้ยกตัวอย่าง z สูง เช่น z=3.5 แทน)

### 🟠 execution-2. statarb-ch12.html — §12.5 กล่อง 'หมายเหตุเกี่ยวกับ sigma ใน dd_limit'
- **ประเภท**: อธิบายชวนเข้าใจผิด
- **ปัญหา**: อธิบาย worst-case ผิดทิศ: การที่ spread 'เคลื่อนจาก entry_z กลับไปที่ค่ากลาง' คือทิศทางที่ position ทำกำไร (เรา trade mean reversion) — adverse move ที่ทำให้ขาดทุนคือ spread วิ่งออกห่างจากค่ากลางเพิ่มอีก entry_z·σ (เช่น z จาก 2 ไป 4) ตัวสูตรใช้ได้แต่เหตุผลที่ให้ไว้กลับด้าน
- **หลักฐาน**: `มาจากสมมติว่า worst-case adverse move คือ spread เคลื่อนจาก z ณ จุดเข้า (entry_z) กลับไปที่ค่ากลาง`
- **วิธีแก้**: แก้เป็น: สมมติ worst-case คือ spread วิ่งสวน position ออกห่างจากค่ากลางเพิ่มอีกระยะ entry_z·σ (เช่น z เพิ่มจาก entry_z เป็น 2×entry_z) ก่อนถูก stop

### 🟠 execution-3. statarb-ch12.html — §12.7 โจทย์ 12.1 Step 5 และโจทย์ 12.2 (คำตอบ)
- **ประเภท**: ตัวเลขในตัวอย่างผิด
- **ปัญหา**: คำตอบแบบฝึกหัดคำนวณ raw_size โดยไม่คูณ ¼-Kelly (fractional_kelly=0.25) ทั้งที่ pseudo-code §12.5 (Step 5) และ running example §12.6 คูณ 0.25 เสมอ และ key-idea บอก 'ให้ใช้ ¼-Kelly เสมอ' — raw_size ในเฉลยจึงใหญ่เกิน 4 เท่าเทียบกับวิธีที่สอนไว้ (12.1: ควรเป็น $175,781 ไม่ใช่ $703,125; 12.2 Pair A: $3.51M ไม่ใช่ $14.06M, Pair B: $226k ไม่ใช่ $905k) — คำตอบสุดท้ายบังเอิญไม่เปลี่ยนเพราะ dd_limit binding
- **หลักฐาน**: `Step 5: raw_size = 50,000 × 30.0 × 0.625 × 0.75 = $703,125`
- **วิธีแก้**: ใส่ตัวคูณ 0.25 ในทุกเฉลย: raw_size = 50,000 × (0.25 × 30.0) × 0.625 × 0.75 = $175,781 (และปรับตัวเลข Pair A/B กับข้อความ 'สูงกว่า 18 เท่า' ตาม)

### 🟠 execution-4. statarb-ch11.html — §11.6 'การคำนวณ Grid Levels' — ตัวอย่าง θ=0.001, σ_stat=0.003
- **ประเภท**: ตัวเลขในตัวอย่างผิด
- **ปัญหา**: Strong buy ที่ z < −2 ต้องเป็น ε < θ − 2σ = 0.001 − 0.006 = −0.005 ไม่ใช่ −0.004 (ε=−0.004 คือ z≈−1.67) — และขัดกับ running example ในหน้าเดียวกันที่เขียนถูกว่า 'BUY+++ ที่ z < −2 (ε < −0.005)'
- **หลักฐาน**: `Strong buy: ε &lt; −0.004 (z &lt; −2)`
- **วิธีแก้**: แก้เป็น 'Strong buy: ε < 0.001 − 2×0.003 = −0.005 (z < −2)'

### 🟠 execution-5. statarb-ch11.html — §11.6 pseudo-code OUGrid.is_cointegration_healthy เทียบกับตาราง/กล่องความเสี่ยงใ
- **ประเภท**: อื่นๆ
- **ปัญหา**: Threshold ปิด grid ไม่ตรงกันในบทเดียวกัน: ข้อความบอกปิด grid เมื่อ 'ADF p-value > 0.1' (ทั้งในตารางแถว Hard Stop และกล่องความเสี่ยง) แต่โค้ดถือว่า healthy เฉพาะ adf_pvalue < 0.05 → โค้ดจะสั่ง CLOSE_ALL_GRID ตั้งแต่ p ≥ 0.05
- **หลักฐาน**: `return adf_pvalue &lt; 0.05 and regime_probs['broken'] &lt; 0.5  (แต่ข้อความ: 'ถ้า ADF p-value &gt; 0.1 หรือ regime = Broken → ปิด grid ทั้งหมดทันที')`
- **วิธีแก้**: เลือกค่าเดียว (เช่น ใช้ p<0.05 = healthy ทั้งข้อความและโค้ด หรืออธิบายว่าใช้ 0.05 สำหรับ entry gate และ 0.1 สำหรับ hard stop แล้วให้โค้ดสะท้อนตามนั้น)

### 🟠 execution-6. statarb-ch11.html — §11.6 pseudo-code OUGrid.get_grid_action
- **ประเภท**: อื่นๆ
- **ปัญหา**: โค้ด trigger BUY/SELL ตั้งแต่ |z| > 0.5 และคืนค่า 'BUY_LEVEL_0' (level = int(abs(z)) = 0 เมื่อ 0.5<|z|<1) ขัดกับนิยาม grid ในข้อความที่ระบุ levels ที่ θ ± k·σ สำหรับ k = 1, 2, 3 และตัวอย่างที่ให้ Buy เริ่มที่ z < −1
- **หลักฐาน**: `if z &lt; -0.5:  # below θ → buy (long spread)
            return f"BUY_LEVEL_{level}"`
- **วิธีแก้**: เปลี่ยนเงื่อนไขเป็น |z| ≥ 1 (level = int(abs(z)) ≥ 1) ให้สอดคล้องกับ grid levels k=1,2,3 หรืออธิบายในข้อความว่า level 0 เริ่มที่ ±0.5σ

### 🟠 execution-7. statarb-ch13.html — §13.7 Running Example — บรรทัดสุดท้ายของ block คำนวณ Net P&L
- **ประเภท**: ตัวเลขในตัวอย่างผิด
- **ปัญหา**: Annualized return คำนวณผิด: +0.37% ต่อ trade ที่ความถี่ ~1 trade/วัน ให้ annualized ≈ 0.37% × 365 ≈ 135% (แบบ simple ตามวิธีเดียวกับที่เฉลยโจทย์ 13.2 ใช้: 0.51%/วัน → 'Annualized ~186%') ไม่ใช่ ~20%
- **หลักฐาน**: `= +$369  →  +0.37% บน $100,000 ใน 16 ชั่วโมง
  ≈ Annualized ~20% (ถ้า trade frequency ≈ 1 trade/วัน)`
- **วิธีแก้**: แก้เป็น ≈ Annualized ~135% (0.37% × 365) หรือถ้าตั้งใจให้ conservative (คิด win rate/วันที่ไม่มี signal) ต้องระบุสมมติฐานที่ทำให้เหลือ ~20%

### 🟠 execution-8. statarb-ch13.html — §13.5 Cost Breakdown Table (แถว Taker fee)
- **ประเภท**: ความรู้ผิด
- **ปัญหา**: ใช้ taker fee 0.055% 'per leg' กับทั้งสองขา ทั้งที่ trade คือ Short perp + Long SPOT — 0.055% คืออัตรา taker ของ Bybit derivatives เท่านั้น ส่วน Bybit spot base fee คือ 0.1% (maker/taker) ทำให้ค่า fee ของขา spot ต่ำกว่าจริงประมาณเท่าตัว; นอกจากนี้ 'ลดเหลือ −0.01% (maker)' ก็ไม่ตรงกับ Bybit perp maker 0.02% (non-VIP)
- **หลักฐาน**: `Taker fee (entry) | 0.055% per leg | −0.11% รวมสองขา | ใช้ limit order ลดเหลือ −0.01% (maker)`
- **วิธีแก้**: แยกอัตราตามตลาด: perp leg taker 0.055%/maker 0.02%, spot leg 0.1% (base tier) และอัปเดตยอดรวม round-trip กับ breakeven ตาม

### 🟠 execution-9. statarb-ch14.html — §14.7 Running Example — block 'Timeline (simultaneous)'
- **ประเภท**: ตัวเลขในตัวอย่างผิด
- **ปัญหา**: ค่า ε คำนวณซ้ำไม่ได้ตามสูตรที่พิมพ์: log(65023.5) − 1.003 × log(64998.2) = 11.08250 − 11.11536 ≈ −0.03286 (−3.29%) ไม่ใช่ 0.0389% — ค่า 0.0389% ได้เฉพาะเมื่อ β=1 (log(65023.5)−log(64998.2)=0.000389) หรือเมื่อหัก mean θ ของ ε ออกแล้ว แต่สูตรตามที่เขียนไม่มีการหัก θ
- **หลักฐาน**: `(ε = log(65023.5) - 1.003 * log(64998.2) = 0.0389%)`
- **วิธีแก้**: ใช้ β=1.0 ในตัวอย่าง (ε = log(65023.5) − log(64998.2) = 0.0389%) หรือเขียนเป็น ε − θ = 0.0389% พร้อมระบุค่า θ ที่ทำให้ตัวเลขลงตัว

### 🟠 execution-10. statarb-ch12.html — §12.1 key-idea (⚠️ Full Kelly อันตราย) เทียบ §12.7 'บนโต๊ะจริง' ข้อ 1
- **ประเภท**: อื่นๆ
- **ปัญหา**: คำแนะนำ fractional Kelly ขัดกันเองในบทเดียว: ต้นบทสั่ง 'ให้ใช้ ¼-Kelly เสมอ' (และ pseudo-code ใช้ 0.25) แต่กล่อง production แนะนำ 'ใช้ Half-Kelly (f = f*/2) เป็น default'
- **หลักฐาน**: `สำหรับ stat arb ให้ใช้ ¼-Kelly เสมอ (f_actual = f* × 0.25) ... vs ... ใช้ Half-Kelly (f = f*/2) เป็น default`
- **วิธีแก้**: เลือกมาตรฐานเดียว (เช่น ¼-Kelly ตาม pseudo-code) หรืออธิบายชัดว่าเมื่อไรใช้ ½ เมื่อไรใช้ ¼

### 🟠 execution-11. statarb-ch11.html — ทุก <img class="chart" src="charts/..."> ใน ch11–ch16 (เช่น ch11 §11.2, §11.5, §
- **ประเภท**: อื่นๆ
- **ปัญหา**: โฟลเดอร์ docs/charts/ ไม่มีอยู่ในโปรเจกต์ (ไม่มีไฟล์ .svg ใดๆ) ทำให้รูป chart หลักทุกรูปในทั้ง 5 บทเป็น broken image ขณะที่ SVG สำรองที่ถูกต้องถูกซ่อนไว้ใน <div style="display:none"> จึงไม่แสดงอะไรเลย
- **หลักฐาน**: `<img class="chart" src="charts/ch11-state-machine.svg" ...> (ls: cannot access '/home/user/Claude-code-project/docs/charts/': No such file or directory)`
- **วิธีแก้**: สร้าง/เพิ่มไฟล์ใน docs/charts/ หรือเอา display:none ออกจาก div ที่ครอบ SVG fallback (หรือใช้ <object> พร้อม fallback จริง)

### 🟠 execution-12. statarb-ch12.html — §12.6 caption ใต้ chart 'Sensitivity Analysis: ผลของ Half-life ที่ต่างกัน'
- **ประเภท**: ภาพ:label หาย/ผิด
- **ปัญหา**: Caption อ้าง 'AMBER vertical = min useful HL=7d, BLUE = typical pair HL=30d' แต่กราฟ (และทั้งบท) ใช้ half-life หน่วยชั่วโมง แกน x = 1–20h, target=5h และในรูปมีเพียงเส้น GREEN target=5h กับเส้น RED dd_limit — หน่วยวัน (7d/30d) ไม่เกี่ยวกับเนื้อหาบทนี้เลย (น่าจะ copy มาจากบริบท equity pairs รายวัน)
- **หลักฐาน**: `AMBER vertical = min useful HL=7d, BLUE = typical pair HL=30d`
- **วิธีแก้**: แก้ caption ให้ตรงรูป เช่น 'GREEN vertical = target half-life 5h, RED dashed = dd_limit $66.7k'

### 🟡 execution-13. statarb-ch13.html — §13.7 caption ใต้หัวข้อ 'P&L ของ Basis Trades'
- **ประเภท**: ภาพ:label หาย/ผิด
- **ปัญหา**: Caption บรรยาย histogram ของ P&L (green bars = wins, red bars = losses, cumulative line, win rate 70%) แต่รูปที่มี (ทั้งชื่อไฟล์ ch13-basis-pnl.svg และ SVG fallback) เป็น z-score path ของ basis พร้อมจุด ENTRY z=+4.1 / EXIT z≈0 และเส้น funding F1/F2 — ไม่มี bar chart ใดๆ
- **หลักฐาน**: `P&L per trade: green bars = wins (+0.10%–+0.20%), red bars = losses (−0.07%–−0.09%). Teal dashed = cumulative P&L. Win rate 70%`
- **วิธีแก้**: เปลี่ยน caption ให้ตรงรูปจริง (basis z-score timeline พร้อม entry/exit/funding marks) หรือเปลี่ยนรูปเป็น P&L distribution ตาม caption

### 🟡 execution-14. statarb-ch14.html — §14.2 caption ใต้รูป leg risk และ §14.3 caption ใต้ execution flowchart
- **ประเภท**: ภาพ:label หาย/ผิด
- **ปัญหา**: สอง caption ไม่ตรงรูป: (1) รูป leg risk วาง CASE A/CASE B เป็นบน-ล่าง แต่ caption บอก 'ซ้าย:...|ขวา:...'; (2) caption flowchart บอก 'Submit Leg A (maker) → Leg B (taker)' (sequential) แต่ diagram และคำแนะนำหลักของบท (§14.4) ใช้ 'Place Order A + Order B พร้อมกัน' (simultaneous)
- **หลักฐาน**: `ซ้าย: execution สำเร็จ ... | ขวา: Leg B fail ... / Execution flowchart: Submit Leg A (maker) → Leg B (taker)`
- **วิธีแก้**: แก้เป็น 'บน/ล่าง' และแก้ caption flowchart ให้ตรง diagram (ส่งสอง order พร้อมกัน + timeout 500ms ต่อ leg) หรือระบุว่า maker-first เป็นทางเลือกใน 'บนโต๊ะจริง'

### 🟡 execution-15. statarb-ch14.html — §14.8 โจทย์ 14.2
- **ประเภท**: ตัวเลขในตัวอย่างผิด
- **ปัญหา**: ใช้ 'Bybit taker fee = 0.05%' ขณะที่ ch13 (Cost Breakdown) และ ch19 (ตาราง friction) ใช้ 0.055% ตลอดทั้งเล่ม — ตัวเลขไม่สอดคล้องข้ามบท (ผลต่างเล็ก: fee ควรเป็น $220 ไม่ใช่ $200, รวม $1,143 ไม่ใช่ $1,123)
- **หลักฐาน**: `Bybit taker fee = 0.05% ... Fee สองรอบ (buy + sell): $200,000 × 0.05% × 2 = $200`
- **วิธีแก้**: ใช้ 0.055% ให้ตรงกับบทอื่น: fee = $220, รวมขาดทุน ≈ $1,143

### 🟡 execution-16. statarb-ch16.html — §16.4 caption ใต้ pie chart
- **ประเภท**: ภาพ:label หาย/ผิด
- **ปัญหา**: Caption อ้างว่า BTC spread ได้ weight มากสุดเพราะ 'Sharpe สูงสุดและ risk ต่ำสุด' แต่ตาราง Running Example §16.8 ระบุ BTC Bybit↔Lighter มี σ 12%/ปี ซึ่งไม่ใช่ต่ำสุด (BTC Perp Basis ต่ำสุดที่ 8%)
- **หลักฐาน**: `BTC spread ได้ weight มากสุดเพราะ Sharpe สูงสุดและ risk ต่ำสุด (เทียบตาราง: BTC Bybit↔Lighter σ 12% vs BTC Perp Basis σ 8%)`
- **วิธีแก้**: แก้เป็น 'เพราะ Sharpe สูงสุด' (ตัด 'และ risk ต่ำสุด' ออก)

### 🟡 execution-17. statarb-ch16.html — §16.6 pseudo-code portfolio_allocate (min_weight) เทียบ §16.8 กล่อง 'ข้อปฏิบัติจ
- **ประเภท**: อื่นๆ
- **ปัญหา**: ความหมายของ minimum weight ขัดกัน: โค้ดใช้ min_weight=0.05 เป็น threshold เพื่อ 'ตัด weight ที่ต่ำกว่าให้เป็น 0' แต่กล่องข้อปฏิบัติจริงบอกตั้ง minimum weight 10% 'ไม่ให้ weight เป็น 0 เพราะจะทำให้ portfolio ไม่ diversified' — semantics ตรงข้ามกัน (drop-to-zero vs floor-at-10%)
- **หลักฐาน**: `weights = [w if w >= min_weight else 0.0 for w in weights] ... vs ... ตั้ง minimum weight 10% ต่อ spread (ไม่ให้ weight เป็น 0 ...)`
- **วิธีแก้**: เลือก semantics เดียว: ถ้าต้องการ floor ให้โค้ด clip ขึ้นเป็น min_weight (แล้ว renormalize) หรือแก้ข้อความ production ให้อธิบายว่า weight ต่ำกว่า threshold จะถูกตัดทิ้ง


## Cluster: strategies (ch17–22, 24) — 19 issues

### 🟠 strategies-1. statarb-ch17.html — key-idea บนสุด + cover + §17.1 vs §17.3/§17.4
- **ประเภท**: อธิบายชวนเข้าใจผิด
- **ปัญหา**: นิยาม calendar spread ขัดแย้งกันในบทเดียว: key-idea เขียน 'Calendar Spread = F(near) − F(far)' และ §17.1 คำนวณ Front − Back = −$2.50 แต่ §17.3 ประกาศว่า 'เรานิยาม calendar spread = Back-month − Front-month เสมอ' และ §17.4/§17.7 ใช้ Back − Front ผู้อ่านจะสับสนเรื่องเครื่องหมายของ spread และทิศทาง trade
- **หลักฐาน**: `key-idea: 'Calendar Spread = F(near) - F(far)' | §17.1: 'Calendar spread = Front − Back = $80.00 − $82.50 = −$2.50' | §17.3: 'เรานิยาม calendar spread = Back-month − Front-month เสมอ'`
- **วิธีแก้**: เลือก convention เดียว (Back − Front ตาม §17.3) แล้วแก้ key-idea เป็น F(far) − F(near), แก้ตัวอย่าง §17.1 และคำบรรยาย cover ให้ตรงกัน

### 🟠 strategies-2. statarb-ch18.html — §18.1 ตาราง derivation ของ Put-Call Parity
- **ประเภท**: ความรู้ผิด
- **ปัญหา**: ตารางพิสูจน์ PCP ให้ payoff ที่ไม่เท่ากันระหว่าง Portfolio A และ B ทั้งที่ข้อความสรุปว่า 'เนื่องจาก payoff เท่ากัน': (1) Portfolio A รวม 'Invest (F−K)e^{−rT}' ทำให้ payoff = max(F_T−K,0)+(F−K) ขณะที่ B = max(F_T−K,0) — ต่างกัน (F−K) ทุกกรณี (2) payoff ของ forward struck at K เมื่อ F_T ≤ K ถูกเขียนเป็น 0 ทั้งที่จริงคือ F_T−K (ติดลบ) รวมกับ put แล้วต้องได้ 0 ไม่ใช่ K−F_T
- **หลักฐาน**: `แถว A: 'Buy C, Invest (F−K)e^{−rT}' payoff เมื่อ F_T>K = '(F_T − K) + (F−K)' | แถว B: payoff เมื่อ F_T ≤ K = '0 + (K − F_T)' | ตามด้วย 'เนื่องจาก payoff เท่ากัน ราคาต้องเท่ากัน'`
- **วิธีแก้**: แก้เป็น Portfolio A = Long Call อย่างเดียว, Portfolio B = Long Put + Long Forward struck at K (มูลค่าปัจจุบัน (F−K)e^{−rT}) แล้วแสดง payoff: A = max(F_T−K,0), B = max(K−F_T,0)+(F_T−K) = max(F_T−K,0) เท่ากันทั้งสองกรณี → C = P + (F−K)e^{−rT}

### 🔴 strategies-3. statarb-ch19.html — §19.2 ตาราง Fee Structure + แบบฝึกหัดข้อ 2
- **ประเภท**: ความรู้ผิด
- **ปัญหา**: ระบุ Bybit Perp maker fee = −0.025% (rebate) ซึ่งเป็น fee schedule เก่า (ก่อนปี 2021) — ปัจจุบัน Bybit derivatives non-VIP คิด maker +0.02% / taker 0.055% (ตัว taker 0.055% ในตารางตรงกับ schedule ปัจจุบัน แสดงว่า maker ควรเป็น 0.02%) และ ch21 §21.6 ของเล่มเดียวกันก็เขียนว่า maker Bybit 'ลดเหลือ 0.02%' — ขัดแย้งข้ามบท ผลคือข้อ 2 ที่สรุปว่า round trip 2 makers ได้ rebate −0.07% (จาก +17bps → −7bps) ผิดทั้งหมด กลยุทธ์ที่ดูมี edge เพราะ rebate จะขาดทุนจริง (ต่าง 0.045%/side) ค่า Lighter (−0.010%/+0.030%) ก็ควร verify — Lighter โฆษณา zero fee สำหรับ standard account
- **หลักฐาน**: `'Bybit Perp | −0.025% (rebate) | +0.055%' และ 'Round trip cost (2 makers) ... rebate: −0.07% (receive)' vs statarb-ch21.html §21.6: 'Maker option ... ✅ ลดเหลือ 0.02%'`
- **วิธีแก้**: แก้ maker Bybit เป็น +0.02% (ไม่มี rebate สำหรับ non-VIP), คำนวณ round trip 2 makers ใหม่เป็นต้นทุนบวก และแก้คำตอบข้อ 2 (ประหยัดจาก taker→maker = 0.035%/side ต่อขา Bybit ไม่ใช่ 0.08%) พร้อม verify fee ของ Lighter

### 🟠 strategies-4. statarb-ch19.html — §19.2 กล่อง 'Maker vs Taker Strategy'
- **ประเภท**: ตัวเลขในตัวอย่างผิด
- **ปัญหา**: บอกว่าใช้ maker ทั้งคู่ 'ลด cost จาก −0.17% เป็น −0.03% ต่อ round trip' แต่ตามตารางเดียวกัน maker ทั้งคู่ = (−0.025 + −0.010) × 2 = −0.07% (ตารางเองก็เขียน 'rebate: −0.07% (receive)') ไม่ใช่ −0.03%
- **หลักฐาน**: `'ลด cost จาก −0.17% เป็น −0.03% ต่อ round trip' vs แถวตาราง 'Round trip cost (2 makers) ... rebate: −0.07% (receive)'`
- **วิธีแก้**: แก้ −0.03% เป็น −0.07% (หรือถ้าแก้ fee Bybit เป็น +0.02% ตาม issue ก่อนหน้า ให้คำนวณใหม่ทั้งชุด)

### 🟠 strategies-5. statarb-ch19.html — §19.9 ตาราง Running Example แถว Slippage
- **ประเภท**: ตัวเลขในตัวอย่างผิด
- **ปัญหา**: แถว Slippage ระบุ −0.3 bps สำหรับ '$100k on $500M ADV' แต่ §19.4 ของบทเดียวกันคำนวณด้วย input ชุดเดียวกันเป๊ะ (σ=2%, size=$100k, ADV=$500M) ได้ 0.02×√(100,000/500,000,000) = 0.028% = 2.8 bps (และ pseudo-code §19.8 ยังคูณ 2 สำหรับ entry+exit = 5.7bps) ถ้าใช้ 2.8bps net edge จะเป็น −7.1bps ไม่ใช่ −4.6bps
- **หลักฐาน**: `§19.4: 'Slippage = 0.02 × sqrt(100,000/500,000,000) = 0.02 × 0.014 = 0.00028 = 0.028%' vs §19.9: 'Slippage ($100k on $500M ADV) ... −0.3 bps'`
- **วิธีแก้**: แก้แถว Slippage เป็น −2.8 bps (หรือ −5.7 bps ถ้านับ round trip ตาม pseudo-code) และปรับ Net Edge / ข้อสรุป breakeven ให้สอดคล้อง

### 🟠 strategies-6. statarb-ch19.html — §19.9 แถว Gross spread vs สูตร breakeven (และ key-idea/pseudo-code)
- **ประเภท**: อธิบายชวนเข้าใจผิด
- **ปัญหา**: Gross ในตารางใช้ z_entry×σ = 2.0×7.5 = 15bps (นัยว่า capture ทั้งหมดถึง z=0) แต่ breakeven ในหน้าเดียวกันใช้ตัวหาร (z_entry − z_exit) = 1.5 ซึ่งนัยว่า exit ที่ z=0.5 — ถ้า exit ที่ z=0.5 จริง gross ที่ capture ได้คือ (2.0−0.5)×7.5 = 11.25bps ไม่ใช่ 15bps ทำให้ net edge ดูดีกว่าจริง 3.75bps (pseudo-code compute_edge ก็ใช้ spread_at_entry เต็มเป็น gross เช่นกัน)
- **หลักฐาน**: `'Gross spread at entry (z=2.0, σ=7.5bps) | 2.0 × 7.5bps | +15.0 bps' vs 'Break-even σ: total cost 19.6bps / (2.0 − 0.5) = 13.1bps'`
- **วิธีแก้**: ใช้ gross = (z_entry − z_exit) × σ ให้สอดคล้องกับ breakeven ทั้งในตาราง §19.9 และ compute_edge() หรือระบุชัดว่า assume exit ที่ z=0

### 🔴 strategies-7. statarb-ch21.html — §21.2 key-idea 'สูตรการคำนวณ Swap Amount'
- **ประเภท**: สูตรผิด/พิมพ์ผิด
- **ปัญหา**: สูตร Swap = Lots × Contract size × Swap points/10 ให้ผลผิด 10 เท่าเมื่อเทียบกับตัวอย่างของบทเอง: XAUUSD 1 lot (100 oz), swap −1.20 points → สูตรนี้ได้ 1×100×(1.20/10) = $12/day แต่ running example และโจทย์ 21.1 คำนวณถูกต้องได้ $1.20/day สูตรมาตรฐานคือ Lots × Contract_size × Swap_points × point_size (point XAUUSD = 0.01 → 1×100×1.20×0.01 = $1.20) ตัวหาร /10 ไม่มีที่มา
- **หลักฐาน**: `'$$\text{Swap} = \text{Lots} \times \text{Contract size} \times \frac{\text{Swap points}}{10}$$' vs running example: 'Swap per day = 1 lot × 1.20 × $1.00 = $1.20/day'`
- **วิธีแก้**: แก้สูตรเป็น Swap = Lots × Contract_size × Swap_points × Point_size (หรือ Lots × Swap_points × point_value ตามที่ตัวอย่างใช้จริง)

### 🟠 strategies-8. statarb-ch21.html — §21.2 ตาราง positive swap แถว USOIL
- **ประเภท**: ความรู้ผิด
- **ปัญหา**: ระบุว่า Short USOIL ได้รับ swap บวก 'ใน backwardation' เพราะ 'Futures curve downward sloping' — กลับด้าน: ใน backwardation ราคา futures ต่ำกว่า spot และ roll yield เป็นบวกสำหรับฝั่ง long (นิยามของ positive carry/convenience yield) ฝั่ง short จะได้ swap/roll credit ใน contango ไม่ใช่ backwardation
- **หลักฐาน**: `'USOIL | Short (backwardation) | Futures curve downward sloping | +$1.0–3.0'`
- **วิธีแก้**: แก้เป็น Short ได้ swap บวกใน contango (curve ลาดขึ้น) หรือ Long ได้ swap บวกใน backwardation

### 🟠 strategies-9. statarb-ch21.html — ตัวอย่างที่ 1 (XAUUSD Gold Swap Harvest) แถว 'Swap received'
- **ประเภท**: ความรู้ผิด
- **ปัญหา**: ป้ายกำกับ swap income ของ short XAUUSD ว่ามาจาก '(backwardation)' — ทองคำแทบไม่เคยอยู่ใน backwardation (ch17 ของเล่มเดียวกันระบุ Gold 'มักเป็น Contango เสมอ') และ §21.2 ของบทนี้เองอธิบายถูกแล้วว่า short gold ได้ swap เพราะ 'Gold yield < USD yield' (interest rate carry ใน contango)
- **หลักฐาน**: `'Swap received (short CFD) | $1.20/day per lot (backwardation)' vs §21.2: 'XAUUSD (Gold CFD) | Short | Gold yield < USD yield → short receives rate' และ ch17: 'มักเป็น Contango เสมอ'`
- **วิธีแก้**: เปลี่ยน '(backwardation)' เป็น '(rate carry / contango)' หรือลบวงเล็บออก

### 🟠 strategies-10. statarb-ch21.html — §21.4 กล่อง 'EURUSD ↔ GBPUSD = Synthetic EURGBP' + ตัวอย่างที่ 3
- **ประเภท**: ความรู้ผิด
- **ปัญหา**: ตรรกะ USD exposure กลับด้านและขัดแย้งกันเอง: (1) §21.4 บอก 'β = 1.15 → Long $100k EURUSD + Short $115k GBPUSD → USD ≈ 0' แต่ USD จริง = −$100k + $115k = +$15k (ตารางในตัวอย่างที่ 3 เองก็เขียนถูกว่า 'Net USD ≈ +$15k (residual ~13%)') (2) ข้อระวังท้ายตัวอย่างที่ 3 บอก 'ถ้าใช้ equal notional จะมี residual USD exposure' — กลับด้าน: equal USD notional ทำให้ USD หักล้างพอดี ส่วน β-weighted notional ต่างหากที่สร้าง residual USD
- **หลักฐาน**: `'ตัวอย่าง: β = 1.15 → Long $100k EURUSD + Short $115k GBPUSD → USD ≈ 0' vs 'Net exposure | Long ~€74k / Short ~£55k / Net USD ≈ +$15k (residual ~13%)' และ 'ถ้าใช้ equal notional จะมี residual USD exposure'`
- **วิธีแก้**: แก้เป็น: equal USD notional → USD หักล้างเป็นศูนย์ (synthetic EURGBP เต็มรูป); การถ่วง notional ตาม β=1.15 สร้าง residual USD +$15k ที่ต้องยอมรับหรือ hedge เพิ่ม — เลือกอธิบาย trade-off ระหว่าง β-hedge กับ USD-neutral ให้ถูกทิศ

### 🟠 strategies-11. statarb-ch21.html — ตัวอย่างที่ 3 บรรทัดแรก (เหตุผลที่ β = 1.15)
- **ประเภท**: ความรู้ผิด
- **ปัญหา**: อธิบายว่า β ≠ 1 'เพราะ GBPUSD มี pip value ต่างกัน (GBPUSD pip มีค่าสูงกว่า)' — ผิด: pip value ต่อ lot ของ EURUSD และ GBPUSD เท่ากัน ($10/pip/standard lot เพราะ quote currency เป็น USD ทั้งคู่) β มาจาก OLS regression ของ log price (สัดส่วน covariance/variance) ไม่เกี่ยวกับ pip value
- **หลักฐาน**: `'β = 1.15 — ไม่ใช่ 1.0 เพราะ GBPUSD มี pip value ต่างกัน (GBPUSD pip มีค่าสูงกว่า)'`
- **วิธีแก้**: แก้เหตุผลเป็น: β มาจาก OLS บน log prices สะท้อน relative volatility/co-movement ของสองคู่เงิน ไม่ใช่ pip value

### 🔴 strategies-12. statarb-ch21.html — ตัวอย่างที่ 2 (BTC/ETH CFD) และ §21.5 running example — ค่า β = 0.0444
- **ประเภท**: ความรู้ผิด
- **ปัญหา**: β = 0.0444 เป็นค่าจาก regression บนราคาดิบ (ETH≈$3,000 / BTC≈$67,500 ≈ 0.044) แต่ framework ของบทและ EA code ใน §21.7 ใช้ log prices (MathLog(price_a) − g_beta × MathLog(price_b)) ซึ่ง β ใน log space ของคู่ BTC/ETH ต้องอยู่แถว ~1 (ρ=0.9745 ที่อ้างไว้ยิ่งยืนยัน) ถ้าผู้อ่านนำ β=0.0444 ไปใช้กับ log prices ตามโค้ด ε จะเหลือแค่ log ของขาเดียวโดยแทบไม่ hedge → กลายเป็น directional position เต็มตัว
- **หลักฐาน**: `'β = 0.0444, ρ = 0.9745, AR(1) = 0.9602, Half-life = 17h' + โค้ด: 'return MathLog(price_a) - g_beta * MathLog(price_b);'`
- **วิธีแก้**: ระบุให้ชัดว่า β=0.0444 มาจากราคาดิบ (price-level) และถ้าใช้ log-price framework ต้อง re-fit β ใหม่ (จะได้ค่า ~1.x) หรือเปลี่ยนตัวเลขตัวอย่างเป็น β ใน log space ให้สอดคล้องกับโค้ด

### 🟡 strategies-13. statarb-ch21.html — ตัวอย่างที่ 1 บรรทัดสรุป 'รวม alpha ≈ 0.54%'
- **ประเภท**: ตัวเลขในตัวอย่างผิด
- **ปัญหา**: คำนวณ mean-reversion alpha ไว้เอง = (0.60% − 0.33%) × 1.5 = 40 bps และ swap income = $6/lot ต่อ trade (≈0.3bp บน notional $200k) แต่บรรทัดสรุปกลับบอก 'รวม alpha ≈ 0.54% + swap เสริม' — 0.54% ไม่ตรงกับ 0.40% ที่คำนวณได้ (0.54 ดูเหมือนคูณด้วย 2.0 แทน 1.5)
- **หลักฐาน**: `'(0.60% − 0.33%) × 1.5 = 40 bps จาก mean reversion ... → รวม alpha ≈ 0.54% + swap เสริม'`
- **วิธีแก้**: แก้เป็น 'รวม alpha ≈ 0.40% + swap เสริม' หรือแสดงที่มาของ 0.54% ให้ชัด

### 🟡 strategies-14. statarb-ch21.html — §21.6 key-idea Breakeven σ Formula
- **ประเภท**: สูตรผิด/พิมพ์ผิด
- **ปัญหา**: เขียน total_friction = bid-ask + commission + max(0, swap_net) แต่ประโยคถัดไปและ pseudo-code (รวมตัวอย่างคอมเมนต์ −0.001) บอกให้หัก swap income ออกจาก friction — max(0, swap_net) จะตัด swap income ทิ้ง ขัดกับโค้ด total_friction = bid_ask + commission + swap_net (บวกค่าติดลบ = หักออก)
- **หลักฐาน**: `'total_friction = bid-ask + commission + max(0, swap_net) — ถ้า swap เป็น income ให้หักออกจาก friction' vs โค้ด: 'total_friction = bid_ask_pct + commission_pct + swap_net_pct ... swap_income=−10bps ... = 0.005 = 50 bps'`
- **วิธีแก้**: ตัด max(0,·) ออก — ใช้ total_friction = bid-ask + commission + swap_net (โดย swap_net ติดลบเมื่อเป็น income) ให้ตรงกับโค้ดและตัวอย่าง

### 🟡 strategies-15. statarb-ch21.html — ตัวอย่างที่ 2 แถว 'σ_stat empirical'
- **ประเภท**: ตัวเลขในตัวอย่างผิด
- **ปัญหา**: ในเซลล์เดียวกันใช้ตัวเลขขัดกัน: 'σ_stat empirical ≈ 170 bps (200 bps >> 53 bps ✅)' — 170 หรือ 200? (โจทย์ 21.3 ใช้ 2.0% = 200bps ส่วน §21.6 กล่อง BTC/ETH ใช้ 150–200bps)
- **หลักฐาน**: `'σ_stat empirical | ≈ 170 bps (200 bps >> 53 bps ✅)'`
- **วิธีแก้**: เลือกค่าเดียว เช่น '≈ 170–200 bps (>> 53 bps ✅)'

### 🟠 strategies-16. statarb-ch22.html — §22.7 กล่อง Vega-Neutral Sizing + ฟังก์ชัน vega_neutral_size
- **ประเภท**: สูตรผิด/พิมพ์ผิด
- **ปัญหา**: เงื่อนไข vega-neutral กลับด้าน: สำหรับ ε_IV = IV_A − β·IV_B ต้องให้ total Vega ขา B = β × total Vega ขา A (P&L ∝ ΔIV_A − β·ΔIV_B) ด้วยตัวเลขในตัวอย่าง (Vega_BTC=200, Vega_ETH=50, β=1.05) จำนวน ETH ที่ถูกต้องคือ β×200/50 = 4.2 lots แต่หนังสือตั้งเงื่อนไข 'Vega_A ≈ β_IV·Vega_B' แล้วได้ 200/(50×1.05) = 3.81 lots (หารด้วย β แทนที่จะคูณ) นอกจากนี้โค้ดยัง assign ratio ให้ lots_a ทั้งที่ตัวอย่างใช้ค่าเดียวกันเป็นจำนวน lots ของขา B — label สลับขา
- **หลักฐาน**: `'Target: Vega_A ≈ β_IV · Vega_B ... ETH: 200/(50×1.05) ≈ 3.81 lots' และโค้ด 'ratio = vega_a / (vega_b * beta_iv) ... "lots_a": lots_a * kelly_fraction' (lots_b=1)`
- **วิธีแก้**: แก้เงื่อนไขเป็น Vega_B(total) = β_IV × Vega_A(total) → lots_B = β_IV × Vega_A / Vega_B = 4.2 lots และแก้โค้ดให้ ratio ไปอยู่ขา B (lots_b = beta_iv*vega_a/vega_b เมื่อ lots_a=1)

### 🟡 strategies-17. statarb-ch22.html — §22.3 key-idea หมายเหตุ convention ของ Risk Reversal
- **ประเภท**: อธิบายชวนเข้าใจผิด
- **ปัญหา**: หมายเหตุอ้างว่า 'ตลาด FX ใช้ convention ตรงข้าม (RR = IV_call − IV_put ...)' แต่สูตรที่ยกมานั้นเหมือนกับนิยามของบทเองทุกตัวอักษร (RR_25Δ = σ_call − σ_put) — ไม่ได้ตรงข้าม อันที่จริง FX ก็ quote RR = call − put เช่นเดียวกัน (สิ่งที่ต่างคือ equity skew บางสำนัก quote เป็น put − call) ทำให้ผู้อ่านสับสนว่าเครื่องหมายไหนเป็นของใคร
- **หลักฐาน**: `นิยาม: 'RR_25Δ = σ_call(Δ=+0.25) − σ_put(Δ=−0.25)' vs หมายเหตุ: 'ตลาด FX ใช้ convention ตรงข้าม (RR = IV_call − IV_put > 0 เมื่อ call แพงกว่า)'`
- **วิธีแก้**: ลบหรือแก้หมายเหตุ: FX ใช้ convention เดียวกัน (call − put) เพียงแต่ใน FX ค่ามักสลับบวก/ลบตามคู่เงิน ส่วน equity/crypto มักติดลบเพราะ put skew

### 🟠 strategies-18. statarb-ch22.html — §22.4 กล่อง 'ทำไม Deribit IV > Bybit IV เรื้อรัง'
- **ประเภท**: อธิบายชวนเข้าใจผิด
- **ปัญหา**: เหตุผลในกล่องขัดแย้งกับข้อสรุปของตัวเอง: 'Bybit ... market makers demand higher premium เพราะ uncertainty สูงกว่า → IV underpriced relative to Deribit' — ถ้า MM เรียก premium สูงขึ้น ราคา option และ IV ของ Bybit ต้องสูงขึ้น ไม่ใช่ต่ำลง และ bullet แรก 'Deribit ... vol sellers มากกว่า' ก็ควรกด IV ของ Deribit ให้ต่ำ ไม่ใช่สูงเรื้อรัง — ตรรกะทั้งกล่องไม่ support ข้อสรุป θ_IV > 0
- **หลักฐาน**: `'Bybit = newer options market → market makers demand higher premium เพราะ uncertainty สูงกว่า → IV underpriced relative to Deribit'`
- **วิธีแก้**: เขียนเหตุผลใหม่ให้สอดคล้อง เช่น ความลึกของ order book/ตำแหน่ง mid ที่ต่างกัน, structural demand ของ hedger บน Deribit หรือระบุตรงๆ ว่าเป็น empirical observation ที่ต้องวัดจริง — ไม่ใช่คำอธิบายเชิง MM premium ที่ให้ผลกลับทิศ

### 🟡 strategies-19. statarb-ch24.html — §24.1 caption ของ chart LTCM NAV
- **ประเภท**: ตัวเลขในตัวอย่างผิด
- **ปัญหา**: caption บอก 'indexed Jan 1997 = 100 — จาก peak ≈ 210 ในต้นปี 1998' — เป็นไปไม่ได้: ตารางในหน้าเดียวกันระบุผลตอบแทนปี 1997 = +17% ดังนั้นฐาน Jan 1997 = 100 จะขึ้นไปได้เพียง ~117–125 ในต้นปี 1998 (peak ≈ 400 ใช้ได้เมื่อ index จากจุดตั้งกองทุน 1994 = 100 ตามกราฟคลาสสิก $1 → $4.11 → $0.33) สัดส่วน 210→17 (−92%) ถูกต้อง แต่ฐานปีผิด
- **หลักฐาน**: `'LTCM NAV (indexed Jan 1997 = 100) — จาก peak ≈ 210 ในต้นปี 1998 ลงสู่ 17' vs ตาราง 'ผลตอบแทน 1994–1997: +20%, +43%, +41%, +17%'`
- **วิธีแก้**: เปลี่ยนเป็น indexed มี.ค. 1994 = 100 → peak ≈ 400 → เหลือ ≈ 33 หรือคง Jan 1997 = 100 แล้วใช้ peak ≈ 120 → เหลือ ≈ 10


## Cluster: appendix (formulas + glossary) — 12 issues

### 🔴 appendix-1. statarb-appendix-formulas.html — A.7 สูตรที่ 27 'Net Edge' (บรรทัด ~346)
- **ประเภท**: สูตรผิด/พิมพ์ผิด
- **ปัญหา**: สูตร Net Edge ในภาคผนวก ตัด exchange fee (2×taker fee round-trip) ทิ้งทั้งก้อน แล้วไปคูณ 2 ที่ bid-ask แทน — ขัดกับ ch19 ที่นิยาม Net Edge = gross − (2f_taker + bid-ask + slippage + funding + legging) และในตัวอย่างจริงของ ch19 taker fee คือต้นทุนก้อนใหญ่ที่สุด (17bps จาก total 19.6bps) ผู้อ่านที่ใช้สูตรจากภาคผนวกจะประเมิน net edge สูงเกินจริงราว 0.17% ต่อ round trip และเทรดคู่ที่จริงๆ ขาดทุน (ตัวอย่าง ch19: gross 15bps, net จริง −4.6bps แต่สูตรภาคผนวกให้ค่าบวก)
- **หลักฐาน**: `ภาคผนวก: Edge_net = Edge_gross − 2·(bid-ask) − funding cost − slippage "(คูณ 2 สำหรับ round-trip bid-ask)" — เทียบกับ ch19 บรรทัด 75: Net Edge = σ_ε(gross) − [2f_taker + bid-ask + slippage + funding] และตาราง §19.2: "Round trip cost (2 takers) = (0.0`
- **วิธีแก้**: แก้เป็น Edge_net = Edge_gross − 2·f_taker − bid-ask − slippage − funding (− legging buffer) ให้ตรงกับ ch19 และอธิบายว่า ×2 คือ fee ทั้งสองขา/round-trip

### 🔴 appendix-2. statarb-appendix-formulas.html — A.2 สูตรที่ 7 'ADF Test Statistic' (บรรทัด ~146–147) — critical values
- **ประเภท**: ความรู้ผิด
- **ปัญหา**: สูตรนี้อยู่ในหมวด Cointegration และอ้าง บท 5 §5.2 (Engle-Granger step 2 = ADF บน residuals จาก regression ที่ประมาณ β̂ มาแล้ว) แต่ให้ critical values ของ Dickey-Fuller ธรรมดา (−2.93/−2.89/−2.87 ที่ 5%) — เมื่อทดสอบ residuals ที่ OLS เลือก β̂ ให้ variance ต่ำสุดแล้ว distribution จะเลื่อน ต้องใช้ Engle-Granger/Phillips-Ouliaris critical values (≈ −3.34 ที่ 5% สำหรับ 2 ตัวแปรมี constant; MacKinnon 1991) การใช้ −2.89 เป็นเกณฑ์ทำให้ reject H₀ ง่ายเกินไป → รับคู่ปลอมว่า cointegrated → เข้าเทรด spread ที่ไม่ mean-revert จริง
- **หลักฐาน**: `"Critical values (5%): n=50 → −2.93, n=100 → −2.89, n=500 → −2.87" ใต้หัวข้อ A.2 Cointegration & Hedge Ratio พร้อม ref "→ บท 5 §5.2" (ซึ่งคือ Engle-Granger 2-Step Test)`
- **วิธีแก้**: ระบุว่าถ้าทดสอบ residuals จาก cointegrating regression (EG step 2) ต้องใช้ Engle-Granger critical values (5% ≈ −3.34 สำหรับ 2 assets) หรือใช้ฟังก์ชัน coint() ไม่ใช่ตาราง ADF ธรรมดา — ตาราง DF ธรรมดาใช้ได้เฉพาะ series ที่ไม่ได้ประมาณ β มาก่อน

### 🟠 appendix-3. statarb-appendix-formulas.html — A.2 สูตรที่ 7 'ADF Test Statistic' (บรรทัด ~146) — ตัวสถิติ
- **ประเภท**: สูตรผิด/พิมพ์ผิด
- **ปัญหา**: เขียน t_ADF = φ̂/se(φ̂) โดยที่ภาคผนวกเดียวกัน (สูตรที่ 2) นิยาม φ = AR(1) lag coefficient (ค่าราวๆ 0.9–1.0) — t ของ φ̂ ตรงๆ คือการทดสอบ φ=0 ไม่ใช่ unit root test ค่าที่ได้จะเป็นบวกก้อนใหญ่และไม่มีวันต่ำกว่า critical value ติดลบ สถิติ ADF ที่ถูกคือ δ̂/se(δ̂) จาก regression Δε_t = α + δε_{t-1} + Σγ_kΔε_{t-k} (δ = φ−1) ตามที่ ch5 เขียนไว้เอง
- **หลักฐาน**: `ภาคผนวก: t_ADF = φ̂/se(φ̂), reject H₀ if t_ADF < critical value — เทียบ ch5 (บรรทัด 73–74): Δε_t = α + δε_{t-1} + Σγ_kΔε_{t-k} + η_t, H₀: δ = 0`
- **วิธีแก้**: แก้เป็น t_ADF = δ̂/se(δ̂) โดย δ คือสัมประสิทธิ์ของ ε_{t-1} ใน regression ของ Δε_t (δ = φ − 1) ให้ตรง notation ch5

### 🟠 appendix-4. statarb-appendix-formulas.html — A.2 สูตรที่ 5 'OLS Hedge Ratio' (บรรทัด ~130–131)
- **ประเภท**: อธิบายชวนเข้าใจผิด
- **ปัญหา**: ให้ β = Cov(P_A, P_B)/Var(P_B) โดยนิยาม P_A, P_B เป็น 'ราคา' (ราคาดิบ) — ขัดกับหลักของเล่มที่ ch4 ประกาศชัดว่า canonical β สำหรับ ε = log P_A − β log P_B คือ slope ของ log-price regression และ ch4 ยังลิสต์ 'ใช้ราคาดิบแทน log price' เป็นข้อผิดพลาดที่พบบ่อย (β ขึ้นกับ scale ราคา) ทั้งยังขัดกับสูตรที่ 6 ในการ์ดถัดไปที่กำชับ 'ใช้ log prices ตลอด (ไม่ใช่ raw prices)'
- **หลักฐาน**: `ภาคผนวก: β = Cov(P_A, P_B)/Var(P_B) "P_A, P_B = ราคา asset A และ B" — เทียบ ch4 บรรทัด 215/452: "β = Cov(log P_A, log P_B) / Var(log P_B)" และบรรทัด 945: "ใช้ราคาดิบแทน log price / basis — β กลายเป็นตัวเลขที่ขึ้นกับ scale"`
- **วิธีแก้**: แก้เป็น β = Cov(log P_A, log P_B)/Var(log P_B) และระบุว่าเป็น level regression บน log price

### 🟠 appendix-5. statarb-appendix-formulas.html — A.5 สูตรที่ 18 'Max Drawdown' (บรรทัด ~258)
- **ประเภท**: สูตรผิด/พิมพ์ผิด
- **ปัญหา**: MDD = max_{0≤s≤t}(NAV_s − NAV_t) มี max เพียงชั้นเดียวบน s โดย t ลอยอยู่ — นี่คือนิยามของ 'drawdown ณ เวลา t' (current drawdown) ไม่ใช่ maximum drawdown ของทั้งช่วง ต้องมี max ครอบ t อีกชั้น นอกจากนี้รูปนี้เป็นหน่วยเงิน ขณะ glossary (ภาคผนวก B) นิยาม DD เป็นเปอร์เซ็นต์ของ peak
- **หลักฐาน**: `$$\text{MDD} = \max_{0 \le s \le t} \left(\text{NAV}_s - \text{NAV}_t\right)$$`
- **วิธีแก้**: แก้เป็น MDD = max_{t} [ max_{s≤t} NAV_s − NAV_t ] (หรือรูปเปอร์เซ็นต์ max_t (max_{s≤t}NAV_s − NAV_t)/max_{s≤t}NAV_s ให้สอดคล้อง glossary)

### 🟠 appendix-6. statarb-appendix-formulas.html — A.6 สูตรที่ 23 'Observation Equation' (บรรทัด ~306–307)
- **ประเภท**: อธิบายชวนเข้าใจผิด
- **ปัญหา**: นิยามตัวแปรใน observation equation ว่า y_t = 'ราคา asset A', x_t = 'ราคา asset B' และตัดค่า intercept α ทิ้ง — แต่ ch15 (ที่สูตรอ้างถึง) รัน Kalman บน returns: r_{A,t} = α + β_t·r_{B,t} + v_t ผู้อ่านที่ implement ตามภาคผนวก (ราคา level, ไม่มี α) จะได้โมเดลคนละตัวและ β_t ต่างจากบทหลัก (ch4 ยังย้ำว่า β จาก price-level กับ return regression เป็นคนละค่า)
- **หลักฐาน**: `ภาคผนวก: y_t = β_t x_t + v_t "y_t = ราคา asset A, x_t = ราคา asset B" — เทียบ ch15 บรรทัด 74: r_{A,t} = α + β_t r_{B,t} + v_t (observation) และ pseudo-code ใช้ r_A, r_B`
- **วิธีแก้**: เปลี่ยนคำอธิบายเป็น y_t = return ของ asset A (r_A), x_t = return ของ asset B (r_B) ตาม ch15 (และใส่ α หรือหมายเหตุว่า ch15 มี intercept)

### 🟠 appendix-7. statarb-appendix-formulas.html — หลายสูตร — ตัวชี้อ้างอิงบท/หัวข้อ (เช่นบรรทัด 252, 260, 268, 276, 196, 236)
- **ประเภท**: อื่นๆ
- **ปัญหา**: ตัวชี้ '→ บท X §Y' ผิดอย่างเป็นระบบอย่างน้อย 12 จุดจาก 34 สูตร ทำให้ Quick Reference ใช้ตามหาที่มาไม่ได้: สูตร 2 อ้าง 'บท 3 §3.2' (AR(1) จริงอยู่ §3.5–3.6), สูตร 12 อ้าง 'บท 3 §3.3' (สูตร E[T_exit] ไม่มีอยู่ในบท 3 หรือบทใดในเล่ม), สูตร 16 อ้าง 'บท 12 §12.7' (§12.7 คือแบบฝึกหัด และค่า L_max=4–6 ไม่ปรากฏที่ไหนในเล่ม), สูตร 17 อ้าง 'บท 16 §16.1' (ch16 คือ Multi-leg Portfolios ไม่มีสูตร Sharpe·√252), สูตร 18 อ้าง 'บท 16 §16.2, บท 20 §20.3' (§16.2=Covariance Matrix, §20.3=VaR/CVaR — MDD อยู่ §20.2), สูตร 19 อ้าง 'บท 16 §16.3' (คำว่า Calmar ไม่ปรากฏในบทใดของเล่มเลย), สูตร 20 อ้าง '§20.1' (VaR อยู่ §20.3), สูตร 22–24 อ้าง §15.1/§15.2 (state-space อยู่ §15.2, gain/update อยู่ §15.3), สูตร 25 อ้าง 'บท 23 §23.1' (Kalman อยู่ §23.2–23.3), สูตร 28 อ้าง '§19.3' (break-even อยู่ §19.7), สูตร 32 อ้าง 'บท 22 §22.2' (§22.2=Box Spread; IV pair อยู่ §22.1/22.4), สูตร 5 อ้าง '§4.1' (OLS อยู่ §4.2)
- **หลักฐาน**: `เช่น สูตร 19: "Calmar = Annualized Return/MDD ... → บท 16 §16.3" แต่ grep 'Calmar' ทั้ง statarb-ch0–24 ไม่พบเลย และ ch16 §16.3 คือ 'Mean-Variance Allocation'; สูตร 16: "L_max = 4–6 for crypto stat arb → บท 12 §12.7" แต่ ch12 §12.7 คือ 'แบบฝึกหัด' และ`
- **วิธีแก้**: ตรวจแก้ ref ทุกสูตรให้ตรงหัวข้อจริง; สำหรับสูตรที่ไม่มีในบทหลัก (E[T_exit], Calmar, Gross Leverage Cap 4–6, Sharpe·√252) ให้ระบุว่าเป็น 'เพิ่มเติมเฉพาะภาคผนวก' หรือเพิ่มเนื้อหาในบทหลัก

### 🟡 appendix-8. statarb-appendix-formulas.html — A.4 สูตรที่ 15 (บรรทัด ~225–228)
- **ประเภท**: อื่นๆ
- **ปัญหา**: ชื่อการ์ด 'Notional from Half-life' แต่สูตร N = Risk budget/(σ_ε·z_entry) คือ Max-Drawdown Position Limit จาก ch12 §12.4 — ไม่มี half-life อยู่ในสูตรเลย (half-life scaling เป็นคนละสูตรใน §12.2) ชื่อชวนให้เข้าใจผิดว่า sizing นี้ขึ้นกับความเร็ว mean-reversion
- **หลักฐาน**: `"15. Notional from Half-life — N = Risk budget/(σ_ε · z_entry)" เทียบ ch12 §12.4: size_DD = max_loss/(z_entry·σ_ε)`
- **วิธีแก้**: เปลี่ยนชื่อเป็น 'Position Size จาก Risk Budget / Max-Drawdown Constraint'

### 🟠 appendix-9. statarb-appendix-glossary.html — หมวด B–C รายการ 'Beta (β)' (บรรทัด ~150)
- **ประเภท**: ความรู้ผิด
- **ปัญหา**: คำนิยามกลับทิศ: บอกว่า β แสดงว่า 'asset B เคลื่อนไหวกี่หน่วยเมื่อ asset A เคลื่อนหนึ่งหน่วย' — แต่ β = Cov(P_A,P_B)/Var(P_B) คือ slope ของ regression A บน B ความหมายที่ถูกคือ A เคลื่อนกี่หน่วยเมื่อ B เคลื่อนหนึ่งหน่วย (= จำนวนหน่วย B ที่ต้องถือ hedge ต่อ A หนึ่งหน่วย ตามที่รายการ 'Hedge Ratio' ในไฟล์เดียวกันเขียนถูกแล้ว) ผู้อ่านที่ตีความตามนี้จะกลับด้าน hedge
- **หลักฐาน**: `"สัมประสิทธิ์ hedge ratio ที่แสดงว่า asset B เคลื่อนไหวกี่หน่วยเมื่อ asset A เคลื่อนหนึ่งหน่วย" ทั้งที่สูตรคือ β = Cov(P_A,P_B)/Var(P_B)`
- **วิธีแก้**: แก้เป็น 'asset A เคลื่อนไหวกี่หน่วยเมื่อ asset B เคลื่อนหนึ่งหน่วย (จำนวนหน่วยของ B ที่ต้องถือเพื่อ hedge A หนึ่งหน่วย)'

### 🟠 appendix-10. statarb-appendix-glossary.html — หมวด G–H รายการ 'Funding Rate' (บรรทัด ~256–257)
- **ประเภท**: อธิบายชวนเข้าใจผิด
- **ปัญหา**: ระบุเป็นข้อเท็จจริงทั่วไปว่า funding ชำระ 'ทุก 8 ชั่วโมง' และ annualize ด้วย r×3×365 — แต่เล่มนี้เทรดสอง venue หลักคือ Bybit (8h) และ Lighter ซึ่ง ch13 ระบุเองว่าจ่าย 'ทุก 1 ชั่วโมง' สูตร ×3×365 ใช้ได้เฉพาะรอบ 8h; ผู้อ่านที่ประเมิน funding cost ฝั่ง Lighter ด้วยสูตรนี้จะคลาดเคลื่อน
- **หลักฐาน**: `glossary: "ชำระระหว่าง long และ short ใน perpetual futures contract ทุก 8 ชั่วโมง ... Annualized funding ≈ r × 3 × 365" — เทียบ ch13 บรรทัด 86: "ทุก 8 ชั่วโมง (Bybit) หรือทุก 1 ชั่วโมง (Lighter)"`
- **วิธีแก้**: แก้เป็น 'ตามรอบเวลาที่ exchange กำหนด (Bybit ทุก 8 ชม., Lighter ทุก 1 ชม.)' และเขียนสูตร annualize ทั่วไป ≈ r × (จำนวนรอบต่อวัน) × 365

### 🟡 appendix-11. statarb-appendix-glossary.html — รายการ Cointegration (บรรทัด ~177), Spread (~495), Beta (~151), Hedge Ratio (~27
- **ประเภท**: อธิบายชวนเข้าใจผิด
- **ปัญหา**: สมการในสี่รายการนี้ใช้ราคาดิบ (ε = P_A,t − βP_B,t; β = Cov(P_A,P_B)/Var(P_B)) ขณะที่ทั้งเล่ม (ch3–ch5) และ Formula Playbook ยึด log price เป็นมาตรฐาน (ε = log P_A − β log P_B) และ ch4 เตือนว่าราคาดิบให้ β ที่ขึ้นกับ scale — ท้าย glossary ยังอ้างว่า 'ใช้ notation เดียวกับ Formula Playbook' ซึ่งไม่จริงในจุดนี้
- **หลักฐาน**: `"ε_t = P_{A,t} − β P_{B,t} ∼ I(0)" และ "ε_t = P_{A,t} − β P_{B,t} − α" เทียบ ch3 notation table: "ε = log(P_A) − β·log(P_B)" และ Playbook สูตร 6: "ใช้ log prices ตลอด (ไม่ใช่ raw prices)"`
- **วิธีแก้**: เปลี่ยน P เป็น log P ในสมการทั้งสี่รายการ (หรือเพิ่มหมายเหตุว่ารูปทั่วไป — ในเล่มนี้ใช้ log price)

### 🟡 appendix-12. statarb-appendix-glossary.html — หมวด T–V รายการ 'Vega' (บรรทัด ~554–555)
- **ประเภท**: อธิบายชวนเข้าใจผิด
- **ปัญหา**: คำนิยามบอกว่า vega คือการเปลี่ยนของ option price 'ต่อการเปลี่ยนแปลง 1 percentage point ของ IV' แต่สูตรที่ให้ V = ∂C/∂σ = Sφ(d1)√T เป็น vega ต่อการเปลี่ยน σ 1 หน่วยเต็ม (= 100 percentage points) — ถ้าใช้ตามนิยาม 1pp ต้องหารด้วย 100 ตัวเลขที่คำนวณจะคลาดกัน 100 เท่า
- **หลักฐาน**: `"อัตราการเปลี่ยนแปลงของ option price ต่อการเปลี่ยนแปลง 1 percentage point ของ implied volatility" คู่กับสูตร "𝒱 = ∂C/∂σ = Sφ(d_1)√T"`
- **วิธีแก้**: ระบุว่า Sφ(d1)√T คือ vega ต่อ 1.00 ของ σ และ vega ต่อ 1 vol point = Sφ(d1)√T/100 (หรือแก้นิยามเป็น 'ต่อหน่วยของ σ')


---
รวม 85 issues + null-hypothesis gaps 11 จุด
ลำดับการแก้: 🔴 ทั้งหมดก่อน (ทีละข้อ verify ก่อนแก้) → 🟠 → 🟡 · ตามด้วย visual QA หลัง 16:30 UTC

---

# ส่วนที่ 2: ผลตรวจภาพประกอบ + การ render (visual QA ครบ 5/5 ชุด — 81 issues)

## แก้แล้วทันที (เชิงระบบ — commit นี้)
- ✅ `.pseudo` (กล่องโค้ด) ขาด `white-space:pre` แบบเดียวกับ `.fm` — โค้ดยุบเป็นย่อหน้าเดียวใน 6 ไฟล์ (ch6/ch7/ch10/ch22 ฯลฯ) → เติมแล้ว
- ✅ **มือถือ 390px ล้นจอทั้งเล่ม** (สูตร KaTeX display + ตารางกว้าง ถูก "ตัดทิ้ง" ไม่มี scroll — ~30 จุดใน 20+ ไฟล์) → inject `@media(max-width:640px){.katex-display, table → overflow-x:auto}` ครบ 27 ไฟล์ — ยืนยันแล้ว scrollWidth 616→390
- ✅ กราฟ ch13-basis-pnl สูง 6 เมตร (หน้าว่าง ~23 หน้า) — แก้ generator + regenerate (commit ก่อนหน้า)

## คงเหลือ (แก้เป็นรายภาพใน Phase ถัดไป)


### Visual ชุด 1 (ch6–11) — 19 issues

- 🟠 **statarb-ch6.html** [ภาพ:label หาย/ผิด]: ภาพกับคำบรรยายไม่ตรงกัน: เนื้อหาบอกว่า 'ด้านล่างแสดง time series สังเคราะห์สามแบบ' และ caption ว่าเป็นภาพ mean-reverting (H≈0.3) / random walk (H≈0.5) / trending (H≈0.7) แต่ภาพที่ฝังจริงคือ ch6-zscore-signal.svg ซึ่งเป็น → *แก้: สร้าง/ฝังภาพ time series 3 แบบ (H≈0.3/0.5/0.7) ตามที่ข้อความสัญญา หรือแก้ข้อความนำ+caption ให้บรรยายภาพ spread/z-score ที่มีอยู่จริง*
- 🟠 **statarb-ch6.html** [ภาพ:label หาย/ผิด]: ภาพกับคำบรรยายไม่ตรงกัน: caption บอกว่าเป็น 'R/S log-log plot: แกน x = log(n), แกน y = log(R/S) — slope คือ H; ตัวอย่างแสดง H ≈ 0.35' (ต่อจากขั้นตอน R/S algorithm พอดี) แต่ภาพที่ฝังจริงคือ histogram 'Distribution Z-score → *แก้: สร้างภาพ R/S log-log plot จริง (จุด log(n) vs log(R/S) พร้อมเส้น fit slope≈0.35) หรือย้าย/แก้ caption ให้ตรงกับ histogram ที่มี*
- 🟠 **statarb-ch8.html** [ภาพ:label หาย/ผิด]: caption บรรยายภาพสองแผง ('บน: ε_t ... | ล่าง: Lee-Mykland statistic |L_t| — เมื่อทะลุ threshold 4.0') และบอกว่า jump ถูกมาร์คด้วย '▲ สีแดง' แต่ SVG จริงมีแผงเดียว ไม่มีกราฟ |L_t| เลย และ jump event ใช้วงกลมแดง (legend: ' → *แก้: แก้ caption ให้ตรงกับภาพแผงเดียว (จุดวงกลมแดง = jump event) หรือ regenerate SVG เป็นสองแผงตามที่ caption ว่า*
- 🟠 **statarb-ch11.html** [ภาพ:label หาย/ผิด]: แผนภาพ state machine พังทั้งภาพ: (1) ลูกศร transition ระหว่างกล่อง state หลุดตำแหน่ง — เห็นเป็นหัวลูกศรลอยเดี่ยวๆ แถวบนของภาพ (ดำ/น้ำเงิน/เขียว/teal) ไม่เชื่อมกล่องใดเลย ส่วนระหว่างกล่อง NO_TRADE→WATCH→PAPER_GO→MANUAL_GO → *แก้: regenerate แผนภาพใหม่ให้ลูกศรเชื่อมกล่องจริง ย้าย label เงื่อนไขไปอยู่บนลูกศร (ไม่ทับกล่อง) และขยาย margin ของ figure ไม่ให้เส้นโค้ง invalidation ถูกต*
- 🟠 **statarb-ch6.html** [อื่นๆ] ✅(แก้เชิงระบบแล้ว): โค้ด pseudo-code ใน .pseudo block เสีย line break ทั้งหมด — HTML ต้นฉบับมีขึ้นบรรทัด/indent ถูกต้อง แต่ CSS class .pseudo (บรรทัด 51) ไม่มี white-space:pre ทำให้ browser ยุบ newline เป็น space โค้ด hurst_rs() และ hurst_b → *แก้: เพิ่ม white-space:pre (หรือ pre-wrap) ใน CSS .pseudo ของไฟล์*
- 🟠 **statarb-ch7.html** [อื่นๆ] ✅(แก้เชิงระบบแล้ว): เช่นเดียวกับ ch6: .pseudo ไม่มี white-space:pre ทำให้โค้ด garch_update()/garch_zscore()/should_use_garch() ยุบเป็นย่อหน้าเดียว อ่านโครงสร้าง if/for ไม่ออก → *แก้: เพิ่ม white-space:pre ใน CSS .pseudo ของไฟล์*
- 🟠 **statarb-ch10.html** [อื่นๆ] ✅(แก้เชิงระบบแล้ว): เช่นเดียวกับ ch6/ch7: .pseudo ไม่มี white-space:pre โค้ด compute_zscore()/rolling_zscore()/robust_zscore()/choose_signal() ยุบเป็นย่อหน้าเดียว → *แก้: เพิ่ม white-space:pre ใน CSS .pseudo ของไฟล์*
- 🟡 **statarb-ch8.html** [ภาพ:ตัวหนังสือทับกัน]: ใน histogram Fat Tail vs Normal: (1) ชื่อแกน x 'Standard Deviations from Mean (σ)' พิมพ์ทับ tick label '0' พอดี (อยู่พิกัดเดียวกัน) เห็นเป็นตัวเลข 0 ซ้อนกลางคำ 'Deviations' (2) legend 'Spread Returns (actual)' และ 'Norma → *แก้: เลื่อนชื่อแกน x ลงต่ำกว่าแถว tick (เช่น y=252) และย้าย legend ออกนอกบริเวณยอด histogram (เช่น มุมขวาบนเหนือแท่งเตี้ย)*
- 🟡 **statarb-ch6.html** [ภาพ:ตัวหนังสือทับกัน]: แบบเดียวกับ ch8: ชื่อแกน x 'Z-score' (x=340,y=228) พิมพ์ทับ tick label '0' (x=346,y=225) — ใน render เห็นเลข 0 ซ้อนบนคำ Z-score อ่านทั้งคู่ไม่ชัด → *แก้: เลื่อนชื่อแกน 'Z-score' ลง (y≈242) ให้พ้นแถว tick labels*
- 🟡 **statarb-ch7.html** [ภาพ:label หาย/ผิด]: label โซนด้านขวาของกราฟถูกตัดที่ขอบ SVG: 'ENTRY +2' และ 'ENTRY −2' เห็นแค่ 'ENTRY +'/'ENTRY −' เพราะ text เริ่มที่ x=715 ใน viewBox กว้าง 760 (ข้อความยาว ~50px เกินขอบ) ผู้อ่านไม่รู้ว่าเส้น entry คือระดับ ±2 → *แก้: ขยาย viewBox เป็นกว้าง ~790 หรือเลื่อน label เข้ามา (x=700, text-anchor=end ที่ x=755)*
- 🟡 **statarb-ch9.html** [ภาพ:ตัวหนังสือทับกัน]: เส้นประเขียว (Broken→Normal) พาดผ่านกลางตัวเลขความน่าจะเป็น '0.40' และ '0.20' พอดี (เส้นขีดฆ่าตัวเลข) และตัวเลข '0.05'/'0.01' ที่ลอยอยู่ล่างกลางไม่ชิดเส้นโค้งใด ทำให้จับคู่ label กับลูกศรยาก → *แก้: เลื่อน label 0.40/0.20 ลงใต้เส้นประ ~10px และย้าย 0.05/0.01 ให้ชิดเส้นโค้งของตัวเอง*
- 🟡 **statarb-ch11.html** [ภาพ:ตัวหนังสือทับกัน]: label ระดับ grid (+3σ, +2σ, +1σ, θ, 1σ, 2σ, 3σ) ที่ขอบซ้ายในพื้นที่กราฟ พิมพ์ทับ/ชนกับตัวเลข tick ของแกน y — เช่น '1σ' ซ้อนกับ '−0.005' และ '2σ' ซ้อนกับ '−0.010' อ่านเป็น '−0.0051σ', '−0.0102σ' → *แก้: ย้าย label σ เข้าไปในพื้นที่กราฟ (ขวาของแกน ~15px) หรือวางที่ขอบขวาของกราฟแทน*
- 🟠 **statarb-ch6.html** [render:ล้นจอ/ตัดขอบ] ✅(แก้เชิงระบบแล้ว): ที่ viewport 390px เอกสารล้นแนวนอน (scrollWidth 616px): (1) สูตร KaTeX display 'log(R/S)=H·log(n)+C ⟹ H = slope ของ log-log plot' ล้นขอบขวา เห็นแค่ถึง '⟹' (KaTeX display ไม่มี overflow-x:auto — มีแต่ .fm/.pseudo) (2) ตาร → *แก้: เพิ่ม CSS .katex-display{overflow-x:auto;overflow-y:hidden} และห่อตารางด้วย container ที่ overflow-x:auto (หรือใส่ table{display:block;overflow-x:auto*
- 🟠 **statarb-ch7.html** [render:ล้นจอ/ตัดขอบ] ✅(แก้เชิงระบบแล้ว): ที่ 390px เอกสารล้นแนวนอน (scrollWidth 544px): สูตร GARCH 'σ_t² = ... z_t = (ε_t−θ)/σ_t' ล้นขอบขวา — เศษส่วน z_t ถูกตัดครึ่ง; ตารางเปรียบเทียบ Static vs GARCH z-score (ช่วงเวลา/Spread σ/Static σ/Static z/GARCH σ_t/GARCH  → *แก้: เพิ่ม .katex-display{overflow-x:auto} และห่อตารางใน container overflow-x:auto*
- 🟠 **statarb-ch8.html** [render:ล้นจอ/ตัดขอบ] ✅(แก้เชิงระบบแล้ว): ที่ 390px สูตรหลักของบท 'dε = κ(θ−ε) dt + σ dW + J dN' (ทั้งในกล่องแก่นของบทและกล่อง JUMP-DIFFUSION OU) กว้าง ~460px เกินจอ แต่หน้าไม่ล้น (scrollWidth=390) แปลว่าส่วนท้ายสูตรถูก clip ทิ้ง — เทอม jump 'J dN' ซึ่งเป็นหัวใจ → *แก้: เพิ่ม .katex-display{overflow-x:auto} (หรือลดขนาดฟอนต์ KaTeX ในจอแคบ) ให้เลื่อนดูสูตรเต็มได้*
- 🟠 **statarb-ch9.html** [render:ล้นจอ/ตัดขอบ] ✅(แก้เชิงระบบแล้ว): ที่ 390px เอกสารล้นแนวนอน (scrollWidth 594px): สูตร 'dε = κ(θ−ε)dt + σ(s_t)dW  s_t ∈ {Normal, Stressed, Broken}' ถูกตัดที่ '{N…'; ตาราง OU parameters ต่อ regime ถูกตัด — คอลัมน์ 'Half-life' และ 'กลยุทธ์' (เทรดเต็ม size / → *แก้: เพิ่ม .katex-display{overflow-x:auto} และ wrapper overflow-x:auto ให้ตาราง*
- 🟠 **statarb-ch10.html** [render:ล้นจอ/ตัดขอบ] ✅(แก้เชิงระบบแล้ว): ที่ 390px เอกสารล้นแนวนอน (scrollWidth 527px): สูตร robust z-score 'z_t = (ε_t − median(ε)) / (1.4826·MAD)' ล้นขอบขวาของกล่อง KEY IDEA — ตัวส่วน 1.4826·MAD และตัวเศษถูกตัดกลางคำ; ตาราง Window W (4h/24h/72h/168h) ล้นจอไม่ → *แก้: เพิ่ม .katex-display{overflow-x:auto} และ wrapper overflow-x:auto ให้ตาราง*
- 🟠 **statarb-ch11.html** [render:ล้นจอ/ตัดขอบ] ✅(แก้เชิงระบบแล้ว): ที่ 390px เอกสารล้นแนวนอนมากที่สุดในกลุ่ม (scrollWidth 711px): สูตรหัวบท 'z_t > 2.0 ⇒ WATCH → PAPER_GO → MANUAL_GO  |z_t| < 0.5 ⇒ EXIT' เห็นแค่ถึง 'PAPER_GO →'; ตาราง Transition Conditions ถูกตัด — คอลัมน์ 'Action ที่ทำ' → *แก้: เพิ่ม .katex-display{overflow-x:auto} และ wrapper overflow-x:auto ให้ตารางทั้งสอง*
- 🟡 **statarb-ch9.html** [ภาพ:label หาย/ผิด]: caption ท้ายภาพบอกว่า 'z-score panel แสดงเกณฑ์แต่ละ zone' แต่ภาพ timeline มีแผงเดียว (spread ε พร้อมแถบสี regime และเส้น ±2σ) ไม่มี z-score panel แยก → *แก้: ตัดวลี 'z-score panel แสดงเกณฑ์แต่ละ zone' หรือเปลี่ยนเป็น 'เส้นประ ±2σ แสดงเกณฑ์ของ zone'*

### Visual ชุด 2 (ch0–5) — 10 issues

- 🟠 **statarb-ch2.html** [ภาพ:ตัวหนังสือทับกัน]: label กำกับจุดข้อมูล 't=1: std=1' และ 't=2: std≈1.41' วางทับเส้นโค้ง Brownian Motion (สีเขียว teal) พอดี — เส้นกราฟขีดพาดผ่านกลางตัวหนังสือ ทำให้อ่านยาก ตรงกับที่ผู้ใช้รายงานว่า 'ตัวหนังสือทับกราฟ' → *แก้: ใน ch2-sqrt-growth.svg เลื่อน label ทั้งสองขึ้นเหนือเส้น (ลดค่า y ราว 8-10px) หรือใส่ rect พื้นขาวหลังตัวหนังสือแบบเดียวกับ 't=4: std=2' ที่ไม่ทับเส้น*
- 🟠 **statarb-ch5.html** [ภาพ:ตัวหนังสือทับกัน]: label สีแดง '−1.90 (fail) ✗' วางทับซ้อนกับข้อความ 'Fail to Reject Zone — Non-Stationary (ε drift ✗)' บนบรรทัดเดียวกัน (y ต่างกันแค่ 4px) ตัวหนังสือสองชุดซ้อนกันอ่านไม่ออก → *แก้: เลื่อน '−1.90 (fail) ✗' ลงมาที่ y≈188 หรือเลื่อนข้อความ zone ลงล่างของแถบ ให้สองข้อความไม่อยู่บรรทัดเดียวกัน*
- 🟠 **statarb-ch5.html** [ภาพ:label หาย/ผิด]: ป้าย '−3.44 (1%)', '−2.86 (5%)', '−2.57 (10%)' ด้านขวาถูกตัดที่ขอบ SVG เห็นเป็น '−3.44 (19', '−2.86 (59', '−2.57 (10' — เปอร์เซ็นต์อ่านผิดได้ (1% กลายเป็นเหมือน 19) → *แก้: เปลี่ยนเป็น text-anchor="end" x="676" หรือขยาย viewBox กว้างเป็น ~715 หรือย้าย label เข้าด้านในกรอบ*
- 🟡 **statarb-ch5.html** [ภาพ:label หาย/ผิด]: ป้ายแกน y 'E[Crossings]' ถูกตัดที่ขอบซ้ายของ SVG เห็นเป็น 'rossings]' / 'Crossings]' เพราะ text-anchor=end ที่ x=42 แต่ข้อความกว้างกว่า 42px จึงเริ่มนอก viewBox → *แก้: เปลี่ยนเป็น text-anchor="start" x="8" หรือย่อ font/ใช้คำสั้นลง หรือหมุน -90° วางแนวตั้งข้างแกน*
- 🟠 **statarb-ch2.html** [render:ล้นจอ/ตัดขอบ] ✅(แก้เชิงระบบแล้ว): ที่จอมือถือ 390px สมการ Itô's Lemma (katex-display) ล้นกล่องและล้น viewport — เห็นแค่ df = (∂f/∂t + μ∂f/∂X + ½σ²∂²f/∂X²) dt ส่วนท้าย '+ σ(∂f/∂X)dW' ถูกตัดหาย และทำให้ทั้งหน้าเลื่อนแนวนอนได้ (scrollWidth 506 > 390) โดยไม่ → *แก้: เพิ่ม CSS .katex-display{overflow-x:auto;overflow-y:hidden} (ทำทุกบท) หรือแตกสมการเป็นสองบรรทัดด้วย aligned*
- 🟠 **statarb-ch4.html** [render:ล้นจอ/ตัดขอบ] ✅(แก้เชิงระบบแล้ว): ที่ 390px สมการ β̂_OLS = Cov/Var = ∑(r_A−r̄_A)(r_B−r̄_B)/∑(r_B−r̄_B)² ล้นขอบขวา — พจน์ ∑ ตัวหลังถูกตัด (เห็นแค่ '∑(r_B − r̄') ผู้อ่านมือถือไม่เห็นตัวส่วนครบ และทำให้หน้าเลื่อนแนวนอน (scrollWidth 528) → *แก้: เพิ่ม .katex-display{overflow-x:auto} หรือย่อ font-size สมการบนมือถือ / แตกเป็นสองขั้น*
- 🟠 **statarb-ch3.html** [render:ล้นจอ/ตัดขอบ] ✅(แก้เชิงระบบแล้ว): ที่ 390px ตารางกว้างเกิน viewport โดยไม่มี scroll container: ตาราง §3.8 คอลัมน์ 'คำนวณจาก' ถูกตัด (σ_t² = ω + α·ε²_{t-1}... อ่านไม่จบ) และคอลัมน์ 'ใช้ใน' หายทั้งคอลัมน์; ตาราง §3.9 คอลัมน์ 'เลือกเมื่อ' หายทั้งคอลัมน์ — เ → *แก้: ครอบ <table> ด้วย <div style="overflow-x:auto"> หรือเพิ่ม CSS @media (max-width:480px){table{display:block;overflow-x:auto}}*
- 🟠 **statarb-ch4.html** [render:ล้นจอ/ตัดขอบ] ✅(แก้เชิงระบบแล้ว): ตาราง 8 ตัวล้นขอบขวาที่ 390px โดยไม่มี scroll ภายใน — หนักสุดคือตาราง Gauss-Markov (ข้อจำกัดที่ 6) คอลัมน์ 'ผลกระทบ + วิธีตรวจ' หายทั้งคอลัมน์ (เนื้อหาวิธีแก้ Durbin-Watson/Newey-West มองไม่เห็นเลย), ตารางตัวอย่างคำนวณ O → *แก้: ครอบตารางทั้งหมดด้วย div overflow-x:auto หรือ CSS media query ให้ table เลื่อนแนวนอนได้ในตัวเอง*
- 🟠 **statarb-ch5.html** [render:ล้นจอ/ตัดขอบ] ✅(แก้เชิงระบบแล้ว): ตาราง 4 ตัวล้นขอบขวาที่ 390px ไม่มี scroll: ตาราง 3 ขั้นตอน คอลัมน์ 'ถ้าไม่ผ่าน / ต่ำกว่าเกณฑ์' ถูกตัดเกือบหมด (เห็นแค่ 'ข้า… p >… 0.1…'), ตาราง Rolling vs Expanding คอลัมน์ 'เลือกเมื่อ' หายทั้งคอลัมน์ → *แก้: ครอบตารางด้วย div overflow-x:auto เช่นเดียวกับ ch3/ch4*
- 🟡 **statarb-ch1.html** [อื่นๆ]: ภาพ SVG แบบหลาย panel เรียงข้างกันถูกย่อตามความกว้างจอมือถือ 390px ทำให้ตัวหนังสือในกราฟ (ชื่อแกน, legend, ค่าบนแกน) เล็กระดับ ~3-4px อ่านไม่ออกเลยบนมือถือ (ไม่ทับกัน แต่เล็กเกินอ่าน) → *แก้: เพิ่ม media query ให้ .chart แสดง min-width (เช่น min-width:640px) ภายใน container overflow-x:auto เพื่อให้เลื่อนดูได้แทนการบีบทั้งภาพ*

### Visual ชุด 3 (ch12–17) — 20 issues

- 🟠 **statarb-ch12.html** [ภาพ:ตัวหนังสือทับกัน]: label ของเส้นแนวตั้งสองเส้น (amber "½f* ≈ 5%" กับ red "f* = 10%") ถูกวาดทับกันที่มุมซ้ายบนของกราฟ อ่านรวมกันเป็น "½f*≟f5%10%" อ่านไม่รู้เรื่อง → *แก้: แยกตำแหน่ง annotation ของแต่ละเส้น เช่น วาง "½f*=5%" ชิดซ้ายของเส้น amber และ "f*=10%" ชิดขวาของเส้น red หรือวางคนละระดับความสูง*
- 🟠 **statarb-ch14.html** [ภาพ:ตัวหนังสือทับกัน]: label "YES" (กล่องขาวเล็ก) ถูกวาดทับข้อความ "Trade Complete" โดยตรง (อ่านเป็น "Trade Comp[YES]lete") และอีกจุดหนึ่ง "YES" วางทับขอบบน/ข้อความของกล่อง "Submit Leg B (taker)" → *แก้: ย้าย label YES ไปวางบนเส้น/ลูกศรระหว่าง diamond กับกล่องถัดไป ไม่ใช่ทับตัวกล่อง*
- 🟠 **statarb-ch14.html** [ภาพ:label หาย/ผิด]: ลูกศร flow ไม่เชื่อมกล่องตามตรรกะ: ลูกศรแนวตั้งทั้งหมดลอยอยู่คอลัมน์ขวา ต่อเนื่องเป็นสาย Signal→Cancel all→Leg B partial? ซึ่งผิดตรรกะ ("Cancel all (timeout)" เป็น terminal ไม่ควรมีลูกศรไหลลงต่อไปยัง "Leg B partial?") ส่ → *แก้: จัด routing ลูกศรให้ถูกต้อง: diamond →YES→ กล่องถัดไปในคอลัมน์กลาง, ลูกศร NO ไปกล่องขวาเท่านั้น และลดความสูง canvas ของ SVG ให้พอดีเนื้อหา*
- 🟡 **statarb-ch14.html** [ภาพ:ตัวหนังสือทับกัน]: เครื่องหมายกากบาทสีชมพูขนาดใหญ่ถูกวาดทับข้อความ "Exchange B (Lighter)" ในกล่องขวา (ทั้งที่มี ✗ เล็กต่อท้ายข้อความอยู่แล้ว) ทำให้ตัวอักษรถูกขีดคาด → *แก้: เอา X ใหญ่ที่ทับข้อความออก หรือย้ายไปมุมของกล่อง/ทำเป็นพื้นหลังจางกว่านี้*
- 🟡 **statarb-ch15.html** [ภาพ:ตัวหนังสือทับกัน]: label "regime change" สีแดงถูกวาดซ้ำ 2 ตำแหน่งต่อเส้นแนวตั้งแต่ละเส้น (ที่ β≈0.9 และที่ β≈0.05) โดยชุดที่อยู่กลางกราฟทับเส้น Kalman β_t, เส้น Rolling OLS และ CI band พอดี → *แก้: เหลือ label เดียวต่อเส้น วางที่ระดับ y ต่ำ (ใกล้แกน x) ที่ไม่มีเส้นข้อมูลผ่าน*
- 🟡 **statarb-ch17.html** [ภาพ:ตัวหนังสือทับกัน]: panel ซ้าย: เส้น Futures F(T) สีดำพาดทับคำ "Contango:" ของ annotation สีแดง; panel ขวา: เส้น F(T) สีเขียวพาดผ่านข้อความ "convenience yield → F<S" ซึ่งเป็นสีเขียวเดียวกับเส้น ทำให้อ่านยาก → *แก้: ย้าย annotation ทั้งสองไปพื้นที่ว่าง (เช่น ใต้เส้นซ้ายล่าง / เหนือเส้นขวาบน) หรือใส่กล่องพื้นหลังขาวให้ข้อความ*
- 🟡 **statarb-ch17.html** [ภาพ:ตัวหนังสือทับกัน]: กล่อง legend ของ panel บนวางทับข้อมูลช่วง t≈105–150: เส้น basis ที่ขึ้นไปแตะ ~1.5–2.2 และ entry marker (สามเหลี่ยมเขียว) บริเวณนั้นถูกกล่อง legend บังบางส่วน → *แก้: ย้าย legend ออกนอก plot area (เหนือกราฟ) หรือวางมุมล่างซ้าย/ทำ ncol=4 แถวเดียวเหนือ title*
- 🟡 **statarb-ch16.html** [ภาพ:ตัวหนังสือทับกัน]: กล่อง legend "Spread" วางทับขอบขวาของวงกลม pie (ทับรอยต่อชิ้นส้ม 20% กับชิ้น teal 30%) ที่ viewport 900px → *แก้: ย้าย legend ออกด้านขวาของ pie (เพิ่ม bbox_to_anchor ออกนอกแกน) หรือย่อ pie ให้เล็กลง*
- 🟠 **statarb-ch16.html** [ตัวเลขในตัวอย่างผิด]: ตัวเลข correlation ในภาพ heatmap (0.45, 0.22, 0.18) ไม่ตรงกับตัวอย่างตัวเลขใน code block ที่อยู่ติดกันเหนือภาพ (0.42, 0.15, 0.08) และไม่ตรงกับข้อความ §16.7 ที่อ้างว่า "BTC spread กับ ETH spread correlate 0.42" — ผู้อ่านจ → *แก้: แก้ heatmap SVG ให้ใช้ 0.42/0.15/0.08 เท่ากับตัวอย่างในข้อความ (หรือแก้ข้อความให้ตรงภาพ ทางใดทางหนึ่ง)*
- 🟠 **statarb-ch15.html** [render:ล้นจอ/ตัดขอบ] ✅(แก้เชิงระบบแล้ว): ที่ viewport 390px สูตร KaTeX display ล้นขวาโดยไม่มี scroll ภายใน (วัดได้ right=812px บน viewport 390px — หนักสุดในหกบท): สมการ observation "r_A,t = α + β_t r_B,t + v_t (observation)" หายไปทั้งท่อน ผู้อ่านมือถือไม่เห็นคร → *แก้: เพิ่ม CSS `.katex-display{overflow-x:auto;overflow-y:hidden}` (CSS ปัจจุบันมี overflow-x:auto เฉพาะ .fm)*
- 🟠 **statarb-ch12.html** [render:ล้นจอ/ตัดขอบ] ✅(แก้เชิงระบบแล้ว): ที่ 390px สูตร display ล้นขวาถูกตัดโดยไม่มี scroll ภายในกล่อง (right=667px): ท่อน "b=avg win/avg loss, q=1−p" ของสูตร Kelly หาย, สูตร size_adjusted ขาดวงเล็บปิด/τ_actual, สูตร δ_jump ขาดท้าย e^{−λJ²/σ²} และทำทั้งหน้า scr → *แก้: เพิ่ม CSS `.katex-display{overflow-x:auto;overflow-y:hidden}`*
- 🟠 **statarb-ch13.html** [render:ล้นจอ/ตัดขอบ] ✅(แก้เชิงระบบแล้ว): ที่ 390px สูตร Basis_t = P_perp,t − P_spot,t + เงื่อนไข Entry ล้นขวาถูกตัด (right=700px) — ท่อน "Entry: |Basis_t − Basis_fair| > kσ_basis" มองไม่เห็นบนมือถือ และทำทั้งหน้า scroll แนวนอน (186px) → *แก้: เพิ่ม CSS `.katex-display{overflow-x:auto;overflow-y:hidden}`*
- 🟠 **statarb-ch14.html** [render:ล้นจอ/ตัดขอบ] ✅(แก้เชิงระบบแล้ว): ที่ 390px สูตร Net P&L ล้นขวาถูกตัด (right=644px) — ท่อน "− fees_A − fees_B − slippage" ถูกตัดหลัง "fees_A" มองไม่เห็นบนมือถือ → *แก้: เพิ่ม CSS `.katex-display{overflow-x:auto;overflow-y:hidden}`*
- 🟠 **statarb-ch16.html** [render:ล้นจอ/ตัดขอบ] ✅(แก้เชิงระบบแล้ว): ที่ 390px สูตร w* = argmin ... ล้นขวาถูกตัด (right=614px) — เงื่อนไข "1^⊤w = 1, w ≥ 0" ถูกตัดหลัง μ_min มองไม่เห็นบนมือถือ → *แก้: เพิ่ม CSS `.katex-display{overflow-x:auto;overflow-y:hidden}`*
- 🟠 **statarb-ch17.html** [render:ล้นจอ/ตัดขอบ] ✅(แก้เชิงระบบแล้ว): ที่ 390px สูตรล้นขวาถูกตัดโดยไม่มี scroll: สูตรแก่นของบทตัดที่ "Calendar Sp..." (right=695px) และสูตร Calendar Spread Fair ตัดหลัง "= F(T_back) −" (right=821px) — ครึ่งขวาของสมการรวมทั้ง F_front·(e^{(r+u−q)ΔT} − 1) หายทั → *แก้: เพิ่ม CSS `.katex-display{overflow-x:auto;overflow-y:hidden}`*
- 🟠 **statarb-ch12.html** [render:ล้นจอ/ตัดขอบ] ✅(แก้เชิงระบบแล้ว): ที่ 390px ตารางกว้าง 444px ล้นจอโดยไม่มี scroll wrapper — คอลัมน์ "ผลกระทบ" ถูกตัดครึ่ง เนื้อหา ("ไม่ลด (fast mean reversion — ดี)" ฯลฯ) อ่านไม่ได้ (HTML ใช้ <table> เปล่าๆ ไม่มี div overflow-x:auto ครอบ) → *แก้: ครอบตารางด้วย <div style="overflow-x:auto"> หรือเพิ่ม CSS ให้ตารางกว้างเกินจอ scroll ได้*
- 🟠 **statarb-ch14.html** [render:ล้นจอ/ตัดขอบ] ✅(แก้เชิงระบบแล้ว): ที่ 390px ตารางกว้าง 493px ล้นจอโดยไม่มี scroll — คอลัมน์ "Complexity" หลุดออกนอกจอทั้งคอลัมน์ (ค่า กลาง/ต่ำ/สูง มองไม่เห็น) และคอลัมน์ Latency ถูกตัดบางส่วน → *แก้: ครอบตารางด้วย <div style="overflow-x:auto">*
- 🟠 **statarb-ch15.html** [render:ล้นจอ/ตัดขอบ] ✅(แก้เชิงระบบแล้ว): ที่ 390px ตารางล้นจอ (right=467px) โดยไม่มี scroll — คอลัมน์ที่ 5 "ผลเมื่อเพิ่ม" (β ตอบสนองเร็วขึ้นแต่ noisy / Kalman gain ลด / warm-up สั้นลง) หายไปทั้งคอลัมน์บนมือถือ → *แก้: ครอบตารางด้วย <div style="overflow-x:auto">*
- 🟠 **statarb-ch16.html** [render:ล้นจอ/ตัดขอบ] ✅(แก้เชิงระบบแล้ว): ที่ 390px ตาราง Running Example ล้นจอ (right=475px) — คอลัมน์ "σ ต่อปี" (12%/15%/8%/10%) หายทั้งคอลัมน์ และ "Expected Sharpe" ถูกตัดหัวตาราง; ตาราง §16.3 ล้นเล็กน้อย (right=405px) ตัดขอบคอลัมน์ "Risk ที่แท้จริงที่ต่างกัน → *แก้: ครอบตารางทั้งสองด้วย <div style="overflow-x:auto">*
- 🟡 **statarb-ch17.html** [render:ล้นจอ/ตัดขอบ] ✅(แก้เชิงระบบแล้ว): ที่ 390px ตารางล้นจอเล็กน้อย (right=404px) โดยไม่มี scroll — ขอบขวาคอลัมน์ "BTC Futures" ถูกตัด (เช่นค่า "ขึ้นกับ funding rate" แถวสุดท้ายชนขอบจอ) → *แก้: ครอบตารางด้วย <div style="overflow-x:auto">*

### Visual ชุด 4 (ch18–22) — 15 issues

- 🟠 **statarb-ch22.html** [อื่นๆ] ✅(แก้เชิงระบบแล้ว): กล่อง pseudo-code ทั้งบล็อกเสีย newline — โค้ดทั้งฟังก์ชัน get_atm_iv จนถึง exit signal ไหลติดกันเป็นย่อหน้าเดียวแบบ wrap อ่านเป็นโค้ดไม่ได้เลย (เห็นจริงใน screenshot statarb-ch22_w900_05.jpg ล่างสุด และ statarb-ch22_w39 → *แก้: เพิ่ม white-space:pre ในกฎ .pseudo ของ statarb-ch22.html (บรรทัด 52) หรือแปลงบล็อกเป็น <br>/&nbsp; แบบบทอื่น*
- 🟠 **statarb-ch21.html** [ภาพ:ตัวหนังสือทับกัน]: กล่อง legend ของ panel ล่าง (ε, θ=0, ±2σ, Entry, Exit) วางทับพื้นที่ข้อมูลช่วง t≈145–200 ชม. — จุด Entry สีแดงช่วง t≈158–170 ทับ/คร่อมขอบบนของ legend, สามเหลี่ยม Exit สีเขียวหลายจุดและเส้น ε กับเส้น θ=0 ลอดหลัง legend ทำ → *แก้: ย้าย legend ออกนอก plot area (เช่น ใต้กราฟ) หรือเลื่อนไปมุมล่างขวา/ซ้ายที่ไม่มีข้อมูล และใส่พื้นหลังทึบ*
- 🟠 **statarb-ch19.html** [ตัวเลขในตัวอย่างผิด]: caption บอก gross spread 0.20% และ net edge 0.09% แต่ตัวรูป (charts/ch19-edge-waterfall.svg) แสดง Gross Spread = +0.30% และ NET EDGE = +0.11% (0.30 − 0.10 − 0.04 − 0.03 − 0.02 = 0.11) ตัวเลขใน caption ไม่ตรงกับภาพทั้งสอง → *แก้: แก้ caption เป็น "...จาก gross spread ของ 0.30% — เหลือ net edge เพียง 0.11%"*
- 🟠 **statarb-ch21.html** [ภาพ:label หาย/ผิด]: caption ไม่ตรงกับรูป: รูปคือ charts/ch21-walkforward.svg (กราฟ "Walk-Forward Calibration — Prevent Overfitting" แสดง Realized Sharpe กับแถบ Train/Val.) แต่ caption บรรยาย architecture ว่า "Signal Engine เชื่อมต่อทั้ง 2 b → *แก้: เปลี่ยน caption ให้บรรยายกราฟ walk-forward (หรือใส่รูป architecture สองโบรกเกอร์ตามที่ caption ตั้งใจ แล้วย้ายกราฟ walk-forward ไป §21.5)*
- 🟠 **statarb-ch22.html** [ภาพ:label หาย/ผิด]: caption อ้างว่ามีสอง panel ("ซ้าย: ... | ขวา: RR_25Δ mean-reverts รอบ −8% spike ลงถึง −16%...") แต่รูป charts/ch22-vol-smile.svg มี panel เดียว (vol smile) ไม่มีกราฟ RR_25Δ เลย และตัวเลขใน caption (25Δ put IV=58% > 25Δ c → *แก้: ตัดส่วน "ขวา: ..." ออกหรือเพิ่ม panel RR_25Δ ในรูป และแก้ตัวเลข IV ใน caption ให้ตรงกับเส้น Normal ในภาพ*
- 🟠 **statarb-ch22.html** [ภาพ:label หาย/ผิด]: caption ไม่ตรงกับรูป: รูปคือ charts/ch22-rr-zscore.svg (กราฟ 2 panel: RR_25Δ time series + z-score พร้อมจุด Entry) แต่ caption บรรยาย pipeline cross-venue ว่า "Pipeline รับ IV feed จากทั้ง Deribit และ Bybit → คำนวณ ε_xve → *แก้: เปลี่ยน caption ให้บรรยายกราฟ RR_25Δ/z-score (เช่น "RR_25Δ spike เกิน ±2σ → entry, กลับสู่ θ_RR → exit") หรือใส่รูป pipeline ตามที่ caption ตั้งใจ*
- 🟠 **statarb-ch20.html** [ภาพ:label หาย/ผิด]: caption บอกว่า "เมื่อแตะ level 4 (-15%) ระบบหยุด" แต่ในรูป charts/ch20-drawdown-path.svg เส้นลึกสุดคือ "Emergency stop (−12%)" ไม่มีเส้น −15% ในภาพ และระดับในภาพ (−3/−5/−8/−12%) ก็เป็นคนละชุดกับ hierarchy Level 1–4 (per- → *แก้: แก้ caption เป็น −12% (Emergency stop) หรือแก้เส้น/legend ในรูปให้ตรงกับ Level 1–4 ของ §20.2*
- 🟠 **statarb-ch18.html** [render:ล้นจอ/ตัดขอบ] ✅(แก้เชิงระบบแล้ว): สูตร KaTeX display ล้นขอบขวาที่ 390px โดยไม่มี scroll container ของตัวเอง (.katex-display ไม่มี overflow-x:auto) ทำให้ทั้ง body เกิด horizontal scroll (document.scrollWidth = 626px ที่ viewport 390px) — ผู้อ่านมือถือเห็น → *แก้: เพิ่ม CSS .katex-display{overflow-x:auto;overflow-y:hidden} (ใช้ได้กับทั้ง 5 ไฟล์ ch18–ch22)*
- 🟠 **statarb-ch19.html** [render:ล้นจอ/ตัดขอบ] ✅(แก้เชิงระบบแล้ว): ที่ 390px สูตร Net Edge (underbrace) กว้าง 595px ล้นจอโดยไม่มี scroll container และตาราง §19.2 คอลัมน์ "หมายเหตุ" ถูกตัด ("(0.055+0.030)×2 = 0.17%" / "rebate: −0.07%" เห็นครึ่งเดียว) ทำให้ body scroll แนวนอนทั้งหน้า (scr → *แก้: เพิ่ม .katex-display{overflow-x:auto} และครอบตารางด้วย wrapper overflow-x:auto (หรือ table{display:block;overflow-x:auto})*
- 🟠 **statarb-ch20.html** [render:ล้นจอ/ตัดขอบ] ✅(แก้เชิงระบบแล้ว): ที่ 390px สูตร "Halt if: DD < −8% or VaR95 > 2% or ρavg > 0.7" ถูกตัดหลัง "VaR95 >" (กว้างจริง 581px), ตาราง Black Swan คอลัมน์ Recovery ถูกตัดเกือบหมด (เห็นแค่ "Wa/Cl/Re/No...") และตาราง 20.8 คอลัมน์ "เงื่อนไข Alert" หล → *แก้: เพิ่ม .katex-display{overflow-x:auto} และ wrapper overflow-x:auto ให้ตาราง*
- 🟠 **statarb-ch21.html** [render:ล้นจอ/ตัดขอบ] ✅(แก้เชิงระบบแล้ว): ที่ 390px สูตรเปิดบท ε_t = log P_CFD,t − log P_spot,t − θ ถูกตัดก่อนส่วน Entry: |ε_t| > 2σ_ε, สูตร Swap = Lots × Contract size × (Swap points/10) ถูกตัดกลางเศษส่วน, ตารางตัวอย่าง swap (บรรทัด 125) คอลัมน์ "ตัวอย่าง swap/ → *แก้: เพิ่ม .katex-display{overflow-x:auto} และ wrapper overflow-x:auto ให้ตาราง*
- 🟠 **statarb-ch22.html** [render:ล้นจอ/ตัดขอบ] ✅(แก้เชิงระบบแล้ว): ที่ 390px สูตรเปิดบท ε_IV = IV_BTC − IV_ETH − θ_IV ถูกตัดก่อนส่วน RR_25Δ = σ_call,25Δ − σ_put,25Δ, สูตรนิยาม RR_25Δ ใน §22.3 ถูกตัดที่ "σ_put(Δ...", และตาราง Data Sources คอลัมน์ Free/Paid หลุดจอทั้งคอลัมน์ + คอลัมน์ Sou → *แก้: เพิ่ม .katex-display{overflow-x:auto} และ wrapper overflow-x:auto ให้ตาราง*
- 🟡 **statarb-ch18.html** [ภาพ:label หาย/ผิด]: ข้อความ legend ยาวเกินขอบขวาของ SVG canvas และถูกตัด: "7-day expiry (higher, skewed)" เห็นเป็น "...skewe" และ "30-day expiry (lower, flatter)" วงเล็บปิดถูกตัด — legend เริ่มที่ x=366pt แต่ viewBox กว้างเพียง 494pt ข้อควา → *แก้: ย่อข้อความ legend หรือขยับ legend ไปทางซ้าย/ลดขนาด font หรือขยาย viewBox ให้พอ*
- 🟡 **statarb-ch19.html** [ภาพ:label หาย/ผิด]: annotation สีเขียว "Net Edge = 0.11%" ถูกตัดที่ขอบขวาของ SVG — เครื่องหมาย % หลุดขอบ เห็นเป็น "Net Edge = 0.11" (text เริ่ม x=408pt ยาว ~80pt ชน viewBox กว้าง 488.75pt) และหางลูกศรจาก label ชี้ทะลุผ่านตัวเลข "+0.11%" บนแ → *แก้: ขยับ label ไปทางซ้ายหรือใช้ text-anchor:end อิงขอบแท่ง เพื่อให้ % ไม่ถูกตัด*
- 🟡 **statarb-ch21.html** [ภาพ:ตัวหนังสือทับกัน]: กล่อง legend (Train/Validate/Realized Sharpe/Acceptable) วางทับ label แถบ "Val." ที่ x≈220 (เห็นเฉพาะตัว "V" ที่โผล่พ้นขอบ legend) และ label "Train"/"Val." ชุดขวาสุด (~day 250–310) จมอยู่หลังกล่อง legend ที่พื้นหลังกึ่งโ → *แก้: ย้าย legend ออกนอก plot area หรือใส่พื้นหลังทึบและเลื่อน label Train/Val. แถวบนหลบตำแหน่ง legend*

### Visual ชุด 5 (ch23–24+appendix) — 17 issues

- 🟠 **statarb-ch23.html** [render:ล้นจอ/ตัดขอบ] ✅(แก้เชิงระบบแล้ว): ที่ viewport 390px (mobile) สูตร KaTeX display กว้าง 461px แต่กล่องกว้าง 278px และไม่มี overflow-x:auto — ข้อความ 'ไม่ใช่ z_{α/2}=1.96' หลุดออกนอกจอ ทำให้ทั้งหน้าเกิด horizontal scroll (document scrollWidth = 517px) → *แก้: ใส่ overflow-x:auto ให้ .katex-display (หรือ wrapper ของสูตร) ที่จอแคบ หรือย่อสูตรเป็นสองบรรทัดบน mobile*
- 🟠 **statarb-ch24.html** [render:ล้นจอ/ตัดขอบ] ✅(แก้เชิงระบบแล้ว): ที่ 390px สูตร KaTeX display อย่างน้อย 9 จุดกว้างเกิน viewport โดยไม่มี scroll container ของตัวเอง (Model risk กว้าง 600px, Cascade risk 598px, Slippage 669px, σ_p² 454px บน container ~278–330px) — ทำให้สูตรถูกตัด/ต้องลา → *แก้: ใส่ overflow-x:auto ให้ .katex-display บน mobile; สูตร Model risk ที่มี underbrace 3 ก้อนควรมีเวอร์ชันย่อ/ขึ้นบรรทัดใหม่สำหรับจอแคบ*
- 🟠 **statarb-appendix-formulas.html** [render:ล้นจอ/ตัดขอบ]: แม้ที่ desktop 900px การ์ดคอลัมน์ขวาของ section A.4 ยื่นเกินขอบจอ (right edge = 950px) เพราะสูตรข้อ 16 'GE = Σ|w_i| ≤ L_max (L_max = 4–6 for crypto stat arb)' ยาวจนดัน grid column ให้กว้างเกิน — ข้อความ '…for crypto stat → *แก้: ใช้ grid-template-columns: repeat(2, minmax(0,1fr)) และใส่ overflow-x:auto ใน .fm/.katex-display ของการ์ด เพื่อไม่ให้สูตรยาวดันคอลัมน์*
- 🟠 **statarb-appendix-formulas.html** [render:ล้นจอ/ตัดขอบ] ✅(แก้เชิงระบบแล้ว): ที่ 390px การ์ดสูตรทุกใบกว้าง ~463px (right edge = 493px) เกิน viewport ~100px โดยไม่มี scroll ของตัวเอง — คำอธิบายท้ายการ์ดและสูตรหลายข้อถูกตัดที่ขอบขวา (เช่น ข้อ 2 เห็นแค่ κ = −ln φ/Δt, ส่วน θ = α/(1−φ) หลุดจอ) ผู้อ่าน → *แก้: การ์ด .fc ต้องเป็น width:100%/minmax(0,1fr) ไม่ fix ความกว้าง และให้สูตรใน .fm มี overflow-x:auto*
- 🟡 **statarb-ch23.html** [ภาพ:ตัวหนังสือทับกัน]: เส้นประ loop (จาก Output ย้อนกลับไป State) ลากทับข้อความสีเขียวใต้กล่อง UPDATE 'K_t → 1: เชื่อข้อมูลใหม่ | K_t → 0: เชื่อ model เดิม' — ครึ่งขวาของข้อความถูกเส้นตัดจนอ่านไม่ออก → *แก้: ย้ายข้อความขึ้น/ลงให้พ้นเส้น loop หรือปรับ path ของเส้นประให้อ้อมข้อความ (หรือใส่พื้นหลังขาวใต้ text)*
- 🟡 **statarb-ch23.html** [ภาพ:ตัวหนังสือทับกัน]: label 'altcoin season' (ส้ม) กับ 'β_t peak ~1.28' (เขียว) วางซ้อนชิดกันจนตัวอักษรชนกัน และ label เขียวยังทับเส้น CI ประและยอดเส้นโค้ง β_t ที่จุด peak — ที่ขนาดแสดงจริงในหน้า (~730px) สองบรรทัดนี้กลืนเป็นก้อนเดียวอ่านยาก → *แก้: แยกตำแหน่ง label สองตัว (เช่น altcoin season ไว้บนแถบพื้นส้ม, β_t peak ชี้ด้วยเส้น leader ออกด้านข้าง) และยกให้พ้นเส้น CI*
- 🟡 **statarb-ch23.html** [ภาพ:label หาย/ผิด]: label เขียนว่า 'β_t peak ~1.28' แต่เส้นโค้งที่วาดขึ้นไปสูงกว่า gridline 1.3 ชัดเจน (อ่านจากแกน ≈1.32) และ caption ใต้รูปบอก 'log-return scale: β ≈ 1.0–1.2' ขณะที่กราฟ peak เกิน 1.3 — ตัวเลข label/caption ไม่ตรงกับสิ่งที่ → *แก้: ปรับข้อมูลเส้นให้ peak ≈1.28 จริง หรือแก้ label/caption เป็นค่าที่วาดจริง (เช่น ~1.32 และช่วง 1.0–1.35)*
- 🟠 **statarb-ch23.html** [ความรู้ผิด]: เส้นแดง t(ν=4) ถูกวาดสูงกว่า Normal ทั้งที่กลางโค้ง (peak) และที่หาง — เป็นไปไม่ได้สำหรับ density ที่ integrate เป็น 1: t-distribution หางหนากว่าแต่ peak ต้องต่ำกว่า Normal (0.375 vs 0.399) ภาพนี้สอนผิดว่า t 'สูงกว่าทุกจ → *แก้: วาดใหม่ให้ t(ν=4) มี peak ต่ำกว่า Normal และตัดกันช่วง |t|≈1.5–2 ก่อนสูงกว่าที่หาง*
- 🟡 **statarb-ch23.html** [ภาพ:label หาย/ผิด]: เส้นประแดงที่ label ว่า 't=2.78 (ν=4)' ถูกวางที่ตำแหน่ง ±3.0 บนแกน (ตรง tick ±3 พอดี) ไม่ใช่ ±2.78 — ผู้อ่านเทียบตำแหน่งกับแกนจะได้ค่าผิด → *แก้: เลื่อนเส้นประแดงมาที่ตำแหน่ง 2.78 จริงบนแกน (ระหว่าง +2 กับ +3 ค่อนไปทาง +3)*
- 🟡 **statarb-ch23.html** [ตัวเลขในตัวอย่างผิด]: ในกล่องเขียนว่า 'e.g. 2.74 (ν=4)' แต่ค่า two-tailed 5% ของ ν=4 คือ 2.776 (ตาราง §23.7 และข้อความอื่นในบทใช้ 2.78) — ค่า 2.74 เป็นของ ν≈4.2–4.3 ตามตัวอย่าง MLE ไม่ใช่ ν=4 → *แก้: แก้เป็น 'e.g. 2.78 (ν=4)' หรือ '2.74 (ν=4.3)'*
- 🟡 **statarb-ch23.html** [ภาพ:ตัวหนังสือทับกัน]: label สีส้ม '↑ lag ≈30h' วางทับเส้นโค้งส้ม (Rolling) ตรงยอดพอดี — เส้นพาดผ่านตัวอักษร ทำให้อ่านยากโดยเฉพาะที่ขนาดจริงในหน้า → *แก้: ย้าย label ขึ้นเหนือยอดโค้งหรือใส่ leader line ชี้ลงมา*
- 🟡 **statarb-ch23.html** [อื่นๆ]: ลำดับแถวเรียง ν = 30, 10, 6, 4, 5, 3 — แถว ν=4 ถูกวางก่อน ν=5 ผิดลำดับ (ค่าตัวเลขทุกช่องถูกต้อง: ν=4→2.776, ν=5→2.571) ทำให้ลำดับจากน้อยไปมากสะดุด → *แก้: สลับแถวเป็น 30, 10, 6, 5, 4, 3 (คง highlight ที่ ν=4 ได้)*
- 🟡 **statarb-ch24.html** [ภาพ:ตัวหนังสือทับกัน]: เส้นประส้ม 'Managed liquidation' ลากพาดผ่านกลางข้อความแดง '−44% in Aug alone' (บรรทัดล่างของ label 'NAV ≈ 17 (Oct 1998)') ทำให้ข้อความถูกขีดทับ → *แก้: ยก label ขึ้นเหนือเส้น หรือเลื่อนข้อความไปใต้เส้นประ พร้อมพื้นหลังขาว*
- 🟡 **statarb-ch24.html** [ภาพ:ตัวหนังสือทับกัน]: เส้นโค้งส้มลากทับข้อความ label 'Crowding builds / 2 years silently' ทั้งสองบรรทัด (เส้นตัดผ่านคำว่า 'Crowding' และ '2 years') ทำให้อ่านยาก → *แก้: ย้าย label ไปด้านขวาล่างของโค้ง (พื้นที่ว่างใต้เส้น) หรือใส่พื้นหลัง*
- 🟡 **statarb-ch24.html** [ภาพ:label หาย/ผิด]: label แกน x ด้านขวาถูกตัดที่ขอบ SVG เห็นเป็น 't (d' แทนที่จะเป็น 't (days)' → *แก้: ขยาย viewBox/ขยับ label แกน x เข้ามาด้านใน หรือย่อเป็น 't'*
- 🟠 **statarb-ch24.html** [ภาพ:label หาย/ผิด]: เส้นประแดงพร้อม label 'Hurricane Katrina Sep 2005' ถูกวางที่ตำแหน่ง ~ก.พ. 2006 บนแกนเวลา (อยู่หลัง tick Jan'06 ชัดเจน) และยอด spike ของราคาก็วาดไว้ต้นปี 2006 — ตำแหน่งไม่ตรงกับ label Sep 2005 (อีกทั้ง Katrina จริงคือ Aug → *แก้: เลื่อนเส้นประ+spike ไปช่วง Q3–Q4 2005 ให้ตรง label (และแก้เป็น Aug 2005) พร้อมย้ายข้อความให้พ้นเส้นโค้ง*
- 🟡 **statarb-ch24.html** [ภาพ:ตัวหนังสือทับกัน]: เส้นประแดงแนวตั้ง (Amaranth Sep 2006) ลากทะลุกลางข้อความ label แดง '−$6.6B / in 1 week / ≈ −68% AUM' ทุกบรรทัด ทำให้ตัวเลขสำคัญอ่านยาก → *แก้: ขยับ label ไปด้านขวาของเส้นประ หรือใส่กล่องพื้นขาวรอบข้อความ*

รวม visual 81 issues — ยอดรวมทั้งเล่ม (เนื้อหา 85 + ภาพ 81) = 166 issues