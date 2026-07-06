# แผน Build เล่ม 2 — "Practical Quant: Stat Arb ที่ใช้ได้จริง"

> เอกสารนี้คือ **พิมพ์เขียวลงมือ** ต่อยอดจากเล่ม 1 (`arb-part1..9.html`)
> โฟกัส: **real practice** — จาก estimate hedge ratio → tune → execute → survive cost → monitor regime → kill switch
> สไตล์/มาตรฐานยึดตาม `quant-theory-volumes-plan.md` §4.5–4.7 (การ์ด v4, style guide, กัน hallucinate)

---

## 0. สรุปงาน (Decisions)

| หัวข้อ | ข้อสรุป |
|---|---|
| **ทำอะไร** | เล่ม 2 ของสาย stat arb — *คู่มือลงมือ* ที่เล่ม 1 ไม่ได้ลงลึก (เล่ม 1 = ทฤษฎี/taxonomy/วิธีคิด) |
| **ทำไมแยกเล่ม** | เล่ม 1 ยาวเกิน + โหมดอ่านต่างกัน (เล่ม 1 = เข้าใจ · เล่ม 2 = รันได้จริง มีตัวเลข มีโค้ด) |
| **แกนเล่ม** | 2 แกน: (1) "บันได β" OLS → TLS/PCA → Rolling → **Kalman** → Adaptive/VECM · (2) **pairwise → factor/residual** (pair = rank-1, เทรด residual) |
| **กฎเหล็ก** | เขียนครั้งเดียวมีบ้านเดียว — เรื่องที่เล่ม 1 มีแล้วให้ *อ้างอิง* ไม่เขียนซ้ำ |
| **รูปแบบไฟล์** | HTML self-contained สไตล์เดิม (`practice-part0..9.html`, ~10 Part) **+** โฟลเดอร์ `docs/vol2-code/` (Jupyter/.py + toy dataset ที่รันได้จริง) |
| **การ์ดบท** | มาตรฐาน v4 เดิม **+ 2 กล่องใหม่**: 🐍 โค้ดจริง · 🧪 ผล backtest จริง |
| **กันพลาด** | ห้าม hallucinate paper/ตัวเลข; ตัวเลขผลลัพธ์ทุกตัวต้องมาจาก backtest ในโฟลเดอร์โค้ด ไม่ใช่ตัวเลขลอย |

---

## 1. Positioning — เล่ม 2 ต่างจากเล่ม 1 ยังไง

| | เล่ม 1 (`arb-part*`) | เล่ม 2 (`practice-part*`) |
|---|---|---|
| ถาม | "arb คืออะไร / มองหายังไง" | "ลงมือทำยังไงให้รอด cost + ไม่โดนสับขาหลอก" |
| แกน | taxonomy + epistemology | estimation → tuning → execution → monitoring |
| จบแล้ว | เข้าใจแนวคิด | รันโค้ดได้ มีตัวเลข ตัดสินใจเป็น |

**สิ่งที่เล่ม 1 มีแล้ว (ให้อ้างอิง ไม่เขียนซ้ำ):**
- `arb-part5` §18–21: Pairs, OU process, Kalman *concept*, Regime detection, Factor stat arb, ML, walk-forward, overfitting
- `arb-part7` §25–27: Execution, Risk management, Infrastructure
- `theory-part5`: Cointegration (Engle-Granger/Johansen), GARCH, backtest rigor (deflated Sharpe, purged CV)

**ช่องว่างที่ยังว่างสนิทในเล่ม 1 (ยืนยันด้วย grep):**
`TLS = 0 · Johansen = 0 · VECM = 0 · ADX = 0 · adaptive Kalman = 0 · optimal band = 0`
และ Kalman ใน §19.2 มีแค่ ~3 บรรทัด (concept ล้วน ไม่มี Q/R/โค้ด/tuning) → เล่ม 2 ลงตรงนี้พอดี

---

## 1.5 ปรัชญาเล่ม + แผนที่ Edge  → เป็น **Part 0** ของเล่ม

### §0 — "Kalman ไม่ใช่ edge" (บทเปิด, ตั้งความคาดหวังผู้อ่าน)
- estimator (OLS/TLS/Kalman) = **ท่อประปา ไม่ใช่ alpha**; ถ้าใครก็รันได้ = *table stakes* ไม่ใช่ edge (by definition)
- หลักฐาน: **Do & Faff (2010)** — กำไร pairs แบบคลาสสิก (Gatev 2006) เสื่อมลงเรื่อย ๆ โดน cost + crowding กิน; ใน US large-cap ที่ liquid สุด กลยุทธ์เบสิกแทบตาย
- ประโยคทอง (.pq): *"Kalman คือของฟรีที่ทุกคนมี — ความอยู่รอดของคุณอยู่ที่ 4 ชั้นที่เหลือ"*
- นี่คือสิ่งที่ทำให้เล่ม 2 ต่างจากคอร์สที่สอนแค่ "โค้ด Kalman"

### แผนที่ Edge — edge ย้ายไปไหน (สอนผู้อ่านให้รู้ว่าจะขุดที่ไหน)
> **กฎ meta:** อะไรตีพิมพ์แล้ว edge เฉพาะตัวมักหมด → อ่าน literature เพื่อเอา *ทิศทาง + วิธีการ* มาผลิต edge เอง ไม่ใช่ก๊อป alpha สำเร็จรูป · อ่านเพื่อรู้ว่า "อะไร crowded แล้ว (เลี่ยง)" กับ "อะไร arbitrage ยากเชิงโครงสร้าง (ทน)"

| ชั้น | edge อยู่ตรงไหน | crowded? | รายย่อยเล่นได้ | literature |
|---|---|---|---|---|
| **A. Selection / relationship** | สแกน universe ใหญ่หา relationship ที่คนอื่นมองไม่เห็น (edge อยู่ที่ *การค้นหา* ไม่ใช่การเทรด); copula / partial-cointegration / eigenportfolio จับ dependence ที่ linear-cointegration พลาด | กำลังร้อน | ✅ จุดแข็งรายย่อย (บ่อเล็ก) | graph clustering (2024), Clegg-Krauss partial coint (2018), Avellaneda-Lee (2010) |
| **B. Signal / feature** | residual เป็นแค่ feature เดียว; ดึง residual จาก factor model แล้วให้โมเดล non-linear หา pattern | **แออัดสุด + overfit ง่ายสุด** | ⚠️ ระวัง (ต้องวินัย backtest) | **Guijarro-Ordóñez, Pelger, Zanotti — "Deep Learning Statistical Arbitrage", Management Science (2024/25)**; Fischer-Krauss LSTM (2018); Krauss et al. GBT/RF (2017) |
| **C. Regime / risk / when-NOT-to-trade** | edge ที่เสื่อมช้าสุด เพราะเป็น *วินัย* ไม่ใช่สัญญาณให้ arbitrage; ตัดทันตอนคู่บ้านแตก | ต่ำ (คนมองข้ามเพราะ "น่าเบื่อ") | ✅✅ ทนสุด | §3C + López de Prado (2018) |
| **D. Structural / niche** | เล่นบ่อที่คู่แข่งบาง: illiquid, small-cap, non-US, crypto; capacity เล็กเกินกองใหญ่จะลง; กระจายหลายคู่แทนคู่เดียวลึก | ต่ำ–กลาง | ✅✅ edge เฉพาะรายย่อย | crypto pairs (2024–26), multi-pair portfolio |

**ข้อสรุปเชิงกลยุทธ์ที่เล่มต้องสื่อ:** edge ที่ *ทน* สำหรับรายย่อย = **C + D** (วินัย + niche) ไม่ใช่ A/B (โมเดลที่ทุกคนแข่งกันอยู่) — DL/RL มี backtest สวยแต่ live อ่อนกว่ามากและ overfit หนัก → สอนเป็น "รู้ว่ามันมี + กับดักของมัน" ไม่ใช่ชวนไปแข่ง

### ไอเดียเสริม (นอก literature — flag ชัดว่าเป็นสมมติฐาน ต้อง backtest)
1. **Estimator-disagreement เป็น risk gate:** เมื่อ β จาก OLS/TLS/Kalman *ไม่ตรงกัน* = สัญญาณความสัมพันธ์กำลังสั่น → ใช้ divergence เป็น kill-switch (ถูก · ใหม่ · ทำง่าย)
2. **Fade the crowd:** ทุกคนเข้า z=2 → forced-unwind ที่ threshold มาตรฐานคาดเดาได้ → จับจังหวะต่างเล็กน้อย (second-order)
3. **Access เป็น alpha จริงในไทย/SEA:** broker ไหน · ยืมช็อตได้ไหม · ภาษี — บางที edge คือ *สิทธิ์เข้าถึง* ไม่ใช่โมเดล
4. **Horizon diversification:** คู่เดียวรันหลาย timeframe แล้วรวมสัญญาณ (คนละ horizon decorrelate กัน)

> ทั้ง 4 เป็น **สมมติฐาน** — ในเล่มต้องมาพร้อม backtest จริงในโฟลเดอร์โค้ด ไม่ใช่เคลมลอย ๆ

---

## 2. แกนกระดูกสันหลัง — "บันได β" (Hedge-Ratio Estimation Ladder)

ทั้งเล่มร้อยด้วยคำถามเดียว: *จะหา β ยังไง แล้วทำให้มัน "มีชีวิต" ยังไง*

### ขั้น 0 — OLS และ "ทำไมมันพัง"
- β = Cov(y,x)/Var(x); residual = spread
- **จุดพัง 1 — ไม่สมมาตร**: regress A~B ได้ β ≠ 1/(β จาก B~A)
- **จุดพัง 2 — Errors-in-Variables (EIV / attenuation bias)**: ขาขวา (x) ก็มี noise → β เอนเข้าหา 0 อย่างเป็นระบบ
- **ใช้ได้เมื่อไร**: pair เสถียรมาก / calibrate ครั้งเดียว in-sample / เป็น benchmark เทียบ
- ★ นี่คือคำตอบเชิงเทคนิคว่าทำไม "OLS ใช้ได้แค่บางสถานการณ์"
- Lit: attenuation bias (Frisch); Engle-Granger 2-step (OLS residual → ADF)

### ขั้น 1 — TLS / Deming / PCA hedge ratio
- minimize ระยะ *ตั้งฉาก* (ไม่ใช่แนวตั้ง) → แก้ EIV + สมมาตร
- = eigenvector ตัวแรกของ covariance 2 assets (โยง PCA/eigenportfolio)
- **ต้อง assume** อัตราส่วน noise variance 2 ขา (δ) — สอนวิธีเดา/ประมาณ
- Lit: Deming (1943); total least squares (Golub-Van Loan); Avellaneda-Lee (2010) ใช้ PCA เป็น hedge จริง

### ขั้น 2 — Rolling / Expanding OLS
- β เดินตามเวลาแบบง่ายสุด; สอน **window tradeoff** (สั้น = ไวแต่ jitter · ยาว = นิ่งแต่ช้า)
- กับดัก: step change, edge effect, **lookahead** ถ้า refit ไม่ระวัง
- เป็นสะพานสู่ state-space (Kalman = rolling ที่ "จำ" และ optimal)

### ขั้น 3 — Kalman Filter (หัวใจเล่ม)
- state-space: `β_t = β_{t-1} + w_t` (state = random walk), `y_t = β_t·x_t + v_t`
- **Q** (process noise) = "β เปลี่ยนเร็วแค่ไหน" · **R** (measurement noise) = "เชื่อราคาล่าสุดแค่ไหน"
- ★ **อัตราส่วน Q/R = ปุ่มเดียวที่สำคัญสุด** — tuning เป็นศิลปะ (Q/R สูง → ไว/ไหว; ต่ำ → นิ่ง/ช้า)
- worked example ทีละ step + โค้ดจริง (`pykalman` และเขียนมือ) + วิธีจูน Q/R
- ข้อดี lookahead: Kalman ใช้เฉพาะข้อมูลอดีต → ปลอดภัยกว่า rolling-refit
- Lit: Chan (2013) *Algorithmic Trading* (โค้ด Kalman pairs); Elliott et al. (2005, OU state-space)

### ขั้น 4 — เหนือ Kalman (ที่กองทุนใช้จริง)
- **Johansen / VECM** — cointegrate หลายขา (>2), หา cointegrating vector หลายชุด (เล่ม 1 ไม่มีเลย)
- **Adaptive Kalman** — Q/R ขยับเองตาม innovation (ดู §3B)
- **Markov-regime-switching Kalman** / particle filter / GP-regression β / online learning
- Lit: Johansen (1988/91); Montana-Triantafyllopoulos (flexible least squares)

### Part I — decisions ที่เคาะแล้ว (จากการถกกับ user)

**D1 · TLS = "รู้ / ใช้เป็น / รู้ว่าพังตอนไหน"** (ไม่ใช่เชียร์ให้ใช้เสมอ)
- ใช้เป็น: OLS ลด error แนวตั้ง · TLS/Deming ลดตั้งฉาก (δ=1 = orthogonal = noise 2 ขาเท่ากัน)
- พังตอนไหน: (1) δ ผิด → TLS แลก bias ด้วยสมมติฐานที่อาจผิด = แย่กว่า OLS · (2) ไวต่อ outlier
- ★ **aha:** EIV bias เกิดกับ **return regression** เท่านั้น — OLS บน cointegration (price I(1)) เป็น **super-consistent** (Stock 1987) EIV หายเชิง asymptotic
- กฎที่สอน: OLS บน price/coint = ดีอยู่แล้ว (refine ด้วย **FM-OLS/DOLS** เรื่อง finite-sample) · OLS บน return/hedge = EIV จริง → TLS/PCA/Kalman ช่วย

**D2 · price (level) vs return — แยกให้ขาด พร้อมเหตุผล (มีกล่องเน้น)**
- price/cointegration → β ทำ combo stationary → ตอบ *"spread จะกลับไหม"* · ใช้ผิด = **spurious regression** (Granger-Newbold 1974)
- return/factor → β = exposure ณ ขณะนั้น → ตอบ *"neutral ต่อ factor ไหม"* · return co-move แต่ level ลอยห่างได้ (hedge return ≠ spread กลับ)
- stat arb ใช้ทั้งคู่คนละหน้าที่ → เหตุผลลึกว่าทำไม Part II (price) แยกจาก Part III (return/factor)

**D3 · Hedge unit — ลงลึก (3 ความ neutral ที่สับสน)**
- share-ratio (จาก coint, ทำให้ spread กลับ) vs dollar-neutral (คุม gross แต่ไม่การันตี residual) vs beta-neutral (Part III)
- ★ กับดัก: coint share-ratio มัก **ไม่** dollar-neutral และ **ไม่** market-beta-neutral → แบก hidden exposure (โยง "factor bet ปลอมตัว" Part III); บังคับ dollar-neutral = ทำลาย cointegration
- หลัก: เลือกก่อนว่าจะ neutral ต่ออะไร แล้วหน่วยตามมา (ปกติได้ไม่ครบ 3) → stat arb เลือก reversion ก่อน คุม factor แยก
- ลงลึกหน้าจอไทย: ปัด β·shares เป็นจำนวนเต็ม (rounding, ทุนน้อยเจ็บ) · **board lot 100 หุ้น** (β·100 อาจไม่ลงตัว) · Kalman อัปเดต β → rebalance → ค่าคอมฯ (โยง VI/VIII)
- Lit เพิ่ม: Stock (1987, super-consistency) · Phillips-Hansen (1990, FM-OLS) · Stock-Watson (1993, DOLS) · Granger-Newbold (1974, spurious regression)

### Part IV–V (Kalman) — decisions ที่เคาะแล้ว (จากการถกกับ user)

**K1 · จุดยืน Kalman (ซื่อสัตย์ ไม่เชียร์เกิน ไม่ปัดทิ้ง)**
- แยก: filter เอง **causal/ไม่ lookahead** (fix Q/R = ไม่มี bias) · overfit ทั้งหมดอยู่ที่ *การเลือก Q/R* ไม่ใช่กลไก
- คุณค่าจริง (Palomar): คุม drawdown, ไม่กระตุกเหมือน rolling-OLS · **แต่ edge ไม่ได้อยู่ที่ "ใช้ Kalman" (commodity) — อยู่ที่วินัยการจูน + รู้ว่าสมมติฐานพังตอนไหน**

**K2 · จะรู้ว่า overfit ยังไง — 4 diagnostic**
1. ★ **Q/R plateau vs peak** — sweep Q/R plot OOS: ที่ราบกว้าง = จริง · ยอดแหลม = ฟลุค (diagnostic ดี+ถูกสุด)
2. **Innovation whiteness (ไม่ใช้ PnL)** — innovation ต้อง white + variance = S_t; ถ้า autocorrelated/variance เพี้ยน = โมเดลผิด (NIS/whiteness, Bar-Shalom) → *ตัดสิน filter จาก innovation ไม่ใช่ PnL*
3. **IS vs OOS gap** + deflated Sharpe + walk-forward
4. **Q/R stability ข้าม sub-period**

**K3 · จูน Q/R ไม่หลอกตัวเอง — ลำดับวินัย (ดีสุด → fallback)**
1. ★ **ประมาณเชิงสถิติ ไม่ใช่ตาม PnL** — MLE/EM (`pykalman.em()`) จูนให้ *อธิบายข้อมูล* ไม่ใช่แม็กซ์ PnL · caveat: EM degenerate (R→0) ต้องใส่ bound
2. **ผูกเศรษฐกิจ** — R ≈ microstructure/bid-ask variance ของ spread · Q ↔ "β half-life ~X เดือน" · λ=Q/R ↔ effective window (เลือก lookback ด้วยความเชื่อ ไม่ใช่ backtest)
3. **train/lock/test** — fit→lock→OOS ไม่แตะ test · purged/embargoed CV · deflated Sharpe หักจำนวน config ที่ลอง
4. **เลือกที่ราบ ไม่เลือกยอด** + **ปุ่มเดียว** (fix R จูนแค่ Q หรือ λ ตัวเดียว)
- tutorial ทั่วไปทำกลับด้าน (grid-search PnL) = เหตุที่ผล live หด

**K4 · β random-walk vs mean-reverting**
- default = random walk (ง่าย = adaptive EWMA) แต่ฝัง assumption "β ไม่มีบ้าน" ซึ่งมักผิดกับคู่ cointegrate จริง
- ★ **"filter กิน alpha ตัวเอง":** β adapt เร็วไป → ดูดซับ mispricing เข้า β → spread ดู mean-zero ตลอด สัญญาณหาย (tension: adapt hedge vs อย่ากลืน deviation)
- variant (กล่องเจาะลึก): **AR(1) mean-reverting β** `β_t=μ+φ(β_{t-1}−μ)+w` — ยัง linear-Gaussian, เปลี่ยน transition matrix บรรทัดเดียว · limit Q→0 = β คงที่ = OLS
- จุดยืน (เหมือน TLS ใน Part I): สอน random-walk เป็น default → AR(1) = "รู้ไว้ ใช้เมื่อเชื่อว่า β นิ่งเชิงโครงสร้าง" · เลือกแบบไหน = ขึ้นกับเชื่อว่าความสัมพันธ์เป็นโครงสร้างหรือบังเอิญ (โยง Part 0/VII)
- ธีม: diagnostic ทั้งหมด (plateau/whiteness/MLE/deflated Sharpe) = **process edge ชั้น C** ไม่ใช่ตัว Kalman
- Lit เพิ่ม: Bar-Shalom (innovation consistency/NIS) · pykalman EM

### Part VII (Regime & kill-switch) — decisions ที่เคาะแล้ว (จากการถกกับ user)

**R1 · เปรียบเทียบทุกวิธีจับ regime (มีตารางเต็มในเล่ม)**
- ชั้นเร็ว (early-warning, false alarm สูง แต่ถูก/ไว): z-divergence · estimator-disagreement · Kalman NIS · ADX/RSI
- ชั้นช้า (ground truth, ช้าแต่แม่น): half-life (OU κ) · Hurst · rolling coint re-test (ADF/Johansen) · CUSUM
- retrospective/post-mortem: Chow (break รู้ตำแหน่ง) · Bai-Perron (หลาย break ไม่รู้ตำแหน่ง) · Bayesian changepoint
- ★ **สถาปัตยกรรม = 2 ชั้นลำดับ ไม่ใช่ vote เท่ากัน:** ชั้นเร็วยกธง → *ลดขนาดก่อน* → ชั้นช้ายืนยัน → *kill* · ไวจากชั้นเร็ว แม่นจากชั้นช้า

**R2 · kill-switch + re-entry (evidence-backed)**
- ★ **stop-loss paradox ของ mean reversion:** stop แบบ "spread ห่าง = ตัด" ขัดในตัว (ห่าง = จุดเข้าดีขึ้น) → **stop ต้องผูกกับ "ความสัมพันธ์พัง" (R1) ไม่ใช่ "spread ห่าง"**
- แยก exit 2 ชนิด: convergence-exit → re-enter ได้ทันที (Gatev หลาย round-trip) · structural-break-exit → **ห้าม re-enter บน β/spread เดิม**
- re-entry rule: คู่ break → **quarantine** → รับกลับเมื่อ (1) coint re-test ผ่าน window ใหม่ + (2) half-life ปกติ + (3) disagreement คลี่คลาย = *รอ re-qualify ไม่ใช่รอเวลา*
- ตั้ง stop ร่วมกับ entry/exit (ไม่มั่ว): **Leung-Li (2015)** — entry region อยู่เหนือ stop เสมอ, stop สูง → take-profit ต่ำ
- Evidence/Lit: Leung-Li (2015, stop-loss exit) · Gatev et al (2006, re-form/multi-roundtrip) · Zhu/Yale (wait-one-day cooldown) · Lin-McCrae-Gulati (2006, minimum-profit bound) · Brown-Durbin-Evans (1975, CUSUM) · Bai-Perron (1998/2003) · Adams-MacKay (2007, BOCPD)

**R3 · estimator-disagreement gate (ไอเดีย user — วางเป็น early-warning ชั้นเร็ว)**
- คำนวณ β_OLS/TLS/Kalman บน rolling → dispersion (max−min)/mean เกิน baseline = ยกธง (ลดขนาด/รอยืนยัน)
- caveat: บางส่วนมาจาก Kalman lag → calibrate baseline regime ปกติก่อน · **สมมติฐาน ต้อง backtest** (โยง Part I+IV+VII)

**หมายเหตุ Part VI (Bands):** เคาะไปมากตอนถก §3 แล้ว (z/s-score vs cost-aware/ATR vs optimal OU threshold; band คงที่ vs adaptive) → สรุป decision ตอนเขียนได้เลย

---

## 2.5 Part II ลงรายละเอียด — Correlation & Cointegration ที่ใช้จริง + Copula รายย่อย

> ธีมหลักของ Part นี้ (ตอบโจทย์ user ตรง ๆ): **"ทุกคนมีเครื่องมือ · library · AI เหมือนกัน บนสินทรัพย์ชุดเดียวกัน — แล้วเราต่างตรงไหน"**
> เล่ม 1 §18.1 พูด correlation vs cointegration เชิงมโนทัศน์แล้ว → ที่นี่ *ไม่เขียนซ้ำ* แต่ลง **funnel จริง + ค่า cut-off + วิธี differentiate**

### 2.5.1 The Screening Funnel — ค่า cut-off ที่ใช้กันจริง (จาก paper)

| ขั้นกรอง | ค่าที่ใช้กันจริง | ทำไม / กับดัก |
|---|---|---|
| 1. Correlation prescreen | ρ(log-returns) **> 0.8** | S&P500: มีแค่ ~872 คู่ที่ > 0.8 · เป็นแค่ตัวกรองหยาบ **ไม่ใช่ข้อพิสูจน์ tradability** |
| 2. Engle-Granger ADF | **p < 0.05** (เข้ม: < 0.01) | ทดสอบว่า residual stationary · แต่ single test บน 500 คู่ = false positive เพียบ (ดู 2.5.3) |
| 3. Hurst exponent | **H < 0.5** (ยิ่งต่ำยิ่ง mean-revert) | ยืนยันซ้ำว่า revert จริง ไม่ใช่ ADF บังเอิญผ่าน |
| 4. Half-life (OU) | ใช้ได้ราว **~1–30 วัน** | สั้นไป = churn ค่าคอมฯ · ยาวไป = ทุนถูกล็อก + คู่มีเวลาพัง (empirical เห็น 0.33–70 วัน) |
| 5. Johansen (≥2 ขา) | trace / max-eigen > critical | สำหรับ basket >2 ตัว (เล่ม 1 ไม่มี) |

> สอนเป็น **decision funnel** ไม่ใช่ท่องค่า: ทุกคู่ต้องผ่าน *หลายด่านพร้อมกัน* (ADF **และ** Hurst **และ** half-life สมเหตุผล) — ผ่านด่านเดียวไม่พอ

### 2.5.2 "ทุกคนใช้เหมือนกัน แล้วต่างตรงไหน" — 5 จุด differentiation (แกนของ Part)
1. **Universe** — สแกนที่คนอื่นไม่สแกน (small-cap/ไทย/SEA/crypto) → funnel เดิม แต่บ่อใหม่
2. **Validation เข้มกว่า** — out-of-sample re-test cointegration (ไม่ใช่ fit ครั้งเดียวจบ); รวมหลาย test กัน false positive
3. **Parameter regime** — จูน half-life band / cut-off ให้เข้ากับ *cost ของตัวเอง* ไม่ใช่ลอกค่า paper
4. **When-NOT-to-trade** — coint p-value ลอย/half-life พุ่ง = ถอย (โยง §3C kill-switch)
5. **วิธี dependence ที่ต่างจากฝูง** — ใช้ **copula** จับความสัมพันธ์/จังหวะที่ linear-cointegration ของฝูงพลาด (2.5.4)

### 2.5.3 กับดักตัวจริง (ต้องมีกล่อง 📉 ทุกอัน)
- **In-sample cointegrate → out-sample พัง** (กับดักอันดับ 1)
- **Multiple testing**: สแกน 500 คู่ที่ α=0.05 = คาดหวัง ~เจอ false ~25 คู่ "ผ่าน" ทั้งที่มั่ว → ต้อง Bonferroni/FDR หรือ deflated Sharpe
- **Look-ahead ใน selection**: เลือกคู่จากทั้ง sample แล้ว backtest บน sample เดิม = โกงตัวเอง
- **Regime dependence**: คู่ที่ coint ในตลาดขาขึ้น อาจพังในวิกฤต

### 2.5.4 Copula สำหรับรายย่อย — ชั้น A ที่ฝูงยังไม่แน่น
**ทำไมรายย่อยควรสน:** copula แยก *marginal* (พฤติกรรมแต่ละตัว) ออกจาก *dependence* (โครงสร้างความเชื่อมโยง) → จับ **non-linear + tail dependence** ที่ correlation/cointegration เชิงเส้นพลาด; ใช้ได้แม้ hedge ratio เชิงเส้นพัง; ไม่ต้องบังคับให้ spread เป็น linear-stationary

**เลือก family ตาม "คู่นี้เชื่อมกันตอนไหน" (tail dependence):**
| Copula | Tail | ใช้เมื่อ |
|---|---|---|
| Gaussian / Frank | ไม่มี | เชื่อมกันปกติ ไม่มี tail พิเศษ |
| Student-t | 2 หาง สมมาตร | เชื่อมแรงทั้งตอนขึ้น/ลง (คู่ในเซกเตอร์เดียว) |
| Clayton | หางล่าง | เชื่อมแรงตอน **ตลาดตก** (crash together) |
| Gumbel / Joe | หางบน | เชื่อมแรงตอน **ตลาดขึ้น** |

**Signal = Mispricing Index (MI):** fit copula → conditional probability `P(U≤u|V=v)` → **MI = P(cond) − 0.5** → สะสม MI ข้าม threshold = เข้า/ออก (ต่างจาก z-score ของ spread ที่ใช้ในสาย cointegration)

**เครื่องมือรายย่อย (ฟรี/มาตรฐาน — ทำได้จริงไม่ต้อง infra แพง):**
- `arbitragelab` (Hudson & Thames) — มี **Mispricing Index Copula Strategy** สำเร็จรูป
- `copulas` / `copulae` / `statsmodels` — fit copula เอง
- QuantConnect tutorial "Pairs Trading: Copula vs Cointegration" — โค้ดรันได้ฟรี

**กับดัก copula (ต้องเตือน):** ต้อง fit *marginal* ให้ดีก่อน (empirical CDF/ECDF); เลือก family มั่ว = overfit; tail-dependence estimate ไม่นิ่งบนข้อมูลน้อย; **ต้อง out-of-sample เสมอ**

**Lit:** Rad, Low & Faff (2016, เปรียบเทียบ distance/cointegration/copula) · Xie, Wu et al. (2016, MI method ต้นฉบับ) · Stübinger, Mangold & Krauss (2018, vine copula หลายตัว)

### 2.5.5 ขีดจำกัดของโลก pairwise → สะพานสู่ Part III
- correlation/cointegration/copula ทั้งหมด = มอง *ทีละคู่* แต่สินทรัพย์ co-move เพราะแชร์ **common factor** ไม่ใช่ "ความสัมพันธ์วิเศษเฉพาะคู่"
- นั่งสแกนหาคู่สวย ๆ ไม่ใช่ edge (AI เขียน scan ให้ใครก็ได้ บน asset ชุดเดียวกัน)
- → ปิด Part II ด้วยคำถามที่พาไป Part III: *"ถ้า co-movement มาจาก factor ร่วม ทำไมต้องเลือกคู่ทีละคู่ — ทำไมไม่หัก factor แล้วเทรดสิ่งที่เหลือทั้งกระดาน?"*

---

## 2.6 Part III ลงรายละเอียด — ★ Residual / Factor Stat Arb (Part เอกใหม่)

> **จุดยืน:** pairwise คือ *จุดเริ่ม* · factor/residual คือ *ที่ที่โตขึ้นไป* — Part นี้คือหัวใจใหม่ของเล่มตามที่ user ต้องการ

### 2.6.1 Thesis — pair = กรณีพิเศษ rank-1
- assets co-move เพราะ **shared factor loading** (market/sector/style); "spread" จริง ๆ = **idiosyncratic residual** หลังหัก common factor
- การเลือกคู่มือ = สร้าง factor-neutral portfolio 2 ตัวแบบหยาบ; **PCA/eigenportfolio (Avellaneda-Lee 2010)** ทำเป็นระบบทั้ง universe → เลิกเลือกคู่ ไปเทรด mean-reversion ของ residual ข้ามทั้งกระดาน

### 2.6.2 หัก common factor 3 วิธี (ง่าย → ซับซ้อน; รายย่อยเริ่มข้อ 1 ได้ทันที)
1. **Sector/market ETF hedge** — regress asset บน sector ETF แล้วเทรด residual (ง่ายสุด ทำได้วันนี้)
2. **Statistical factors via PCA / eigenportfolio** (Avellaneda-Lee) — ไม่ต้องตั้งชื่อ factor ปล่อยให้ข้อมูลหาเอง
3. **Fundamental factors** (Fama-French/sector dummies) — โยง `theory-part2` (factor models) เล่ม A แทนเขียนซ้ำทฤษฎี

### 2.6.3 The s-score (Avellaneda-Lee) — แทน "เลือกคู่ + z-score"
- โมเดล idiosyncratic residual เป็น OU → standardize เป็น **s-score** → เข้า/ออกตาม s-score
- position = f(s-score) ข้ามทุกชื่อ → **ไม่มีการ "เลือกคู่" เลย** (ตอบ user: cut-off ไม่จำเป็น — ใช้ soft ranking ทั้ง universe แทน binary select)

### 2.6.4 Cross-sectional mean reversion
- rank residual ทั้ง universe → long ก้นตาราง / short หัวตาราง · factor-neutral by construction · **หลาย bet เล็ก ๆ** แทนคู่เดียวลึก (โยง edge map ชั้น A/D)

### 2.6.5 ★ ประเด็นทอง — common factor = "ความเสี่ยง" ไม่ใช่แค่คำอธิบาย
- ไม่ neutralize factor ให้ดี → "pair/residual" ของคุณคือ **factor bet ปลอมตัว** (แอบ long/short sector/market) = เหตุผลจริงที่ pairs ไร้เดียงสาระเบิดตอนวิกฤต
- **เข้าใจ common factor ไม่ได้ให้ edge — แต่กัน "edge ปลอม"**; วิธีเช็ค: regress residual กลับบน factor → loading ควร ≈ 0
- ประโยคทอง (.pq): *"เลิกถามว่าคู่ไหนสวย — ถามว่า residual อะไรที่เหลือหลังหักสิ่งที่ทุกคนถืออยู่แล้ว และใครยังไม่ได้หักมัน"*

### 2.6.6 ชั้น DL/ML residual (สอนให้รู้ + กับดัก ไม่ใช่ชวนแข่ง)
- **Guijarro-Ordóñez, Pelger, Zanotti** "Deep Learning Statistical Arbitrage": factor (PCA/IPCA) → arbitrage residual → CNN/transformer signal
- ซื่อสัตย์: crowded + overfit หนัก + retail สู้ compute ไม่ได้ → สอนเป็น "รู้ว่ามี + กับดัก" ไม่ใช่พระเอก

### 2.6.7 retail edge ในโลก factor (ต้องซื่อสัตย์)
- factor-residual ก็ crowded ในตลาด liquid (Avellaneda-Lee เองโชว์ Sharpe เสื่อมหลัง ~2002) → **ไม่มี edge ใน *วิธี selection* ใด ๆ เหลือแล้ว** (pairs/coint/copula/PCA/DL)
- edge จริงย้ายไป: **บ่อที่ factor ยัง under-modeled** (Thai/SEA/crypto — แค่หัก sector ETF ก็อาจพอ) · **cost/capacity/access** (ชั้น D) · **วินัย+regime** (ชั้น C)

**Lit:** Avellaneda & Lee (2010, PCA residual s-score) · Guijarro-Ordóñez, Pelger, Zanotti (factor + DL residual) · โยง `theory-part2` (factor models/PCA) เล่ม A

---

## 3. 3 เทคนิค practitioner (จาก user) — ทีมรีวิว + ปรับให้ตรงตำรา

> พูดตรง: ทั้ง 3 ไอเดียมี "core ที่ถูก" แต่ต้องรีเฟรมให้ตรงกับสิ่งที่ literature เรียกจริง เพื่อไม่ให้ตกหลุมที่มองไม่เห็น

### A. ATR band → จริง ๆ คือ "cost-aware band"
- **core ถูก**: band ควรกว้างพอให้ spread ที่ถ่างออก "คุ้ม cost + เหลือ edge"
- **ต้องแก้ 2 จุด**:
  1. คิด ATR/True Range บน **spread series** (ไม่ใช่ราคาดิบของขาใดขาหนึ่ง)
  2. เป้าหมายจริงคือ band ≥ **round-trip cost + edge** → มีทฤษฎี **optimal threshold จาก OU + cost** (Leung-Li 2015) รองรับ ไม่ต้องเดาเอา
- **เทียบให้เห็น**: z-score band (±kσ) vs ATR band vs optimal OU band — สอนว่าเลือกอันไหนเมื่อไร
- ⚠️ ธงกัน over-claim: ตัวเลข "เทรดลด 60–80% / กำไรสุทธิสูงขึ้น" = **ต้องพิสูจน์ด้วย backtest ของคุณเอง** ขึ้นกับ pair/cost/vol ไม่ใช่ค่าคงที่สากล → ใส่เป็น 🧪 กล่องผลจริงจากโฟลเดอร์โค้ด

### B. vol-adaptive R → จริง ๆ คือ "adaptive / robust Kalman"
- **core ถูก 100%**: แท่งสะบัดผิดปกติ → อย่ารีบขยับ β ไล่ราคาขยะ
- **ชื่อทางการ + วิธีถูกหลัก**:
  - **innovation-based R + Mahalanobis gating**: ถ้า `residual/√S` เกิน threshold → inflate R ชั่วคราว (robust/Huber Kalman)
  - หรือใส่ **EWMA/GARCH ของ measurement-vol** เข้า R
- ⚠️ ต้องมี **decay กลับ** ไม่งั้น filter "ตาบอดถาวร" (R ค้างสูง = ไม่เรียนรู้อีกเลย)
- ⚠️ อย่าปรับ Q และ R มั่วพร้อมกันจนระบบ unidentifiable

### C. ADX/RSI regime filter → เก็บเป็น proxy ได้ แต่ไม่ใช่ ground truth
- **พูดตรง**: ADX/RSI ออกแบบมาจับ *เทรนด์ของราคา* แต่ spread ที่ cointegrate ถูกออกแบบให้ *mean-revert* อยู่แล้ว → เอา trend indicator มาจับ "คู่บ้านแตก" เป็น **proxy หยาบที่ต้อง validate** ไม่ใช่กฎศักดิ์สิทธิ์
- **สิ่งที่แข็งกว่า (literature ใช้จริงเป็น regime/kill-switch)**:
  - **half-life monitoring** — OU κ ลอย → half-life พุ่ง = mean reversion กำลังตาย
  - **Hurst exponent** — >0.5 = trending (mean reversion หาย)
  - **rolling cointegration re-test** — ADF/Johansen p-value ลอยขึ้น = ความสัมพันธ์เสื่อม
  - **structural break tests** — CUSUM / Chow / Bai-Perron
- **แผนใช้จริง**: ADX = cheap real-time proxy **คู่กับ** half-life/coint-retest เป็นตัวตัดสิน (ground truth) → kill switch เมื่อ 2 ตัวเห็นตรงกัน
- Lit: Bai-Perron (1998/2003); Hurst/Lo (1991)

---

## 4. บทข้ามสาย (practitioner reality — ที่รายย่อยตายเพราะมองข้าม)

- **Cost & capacity**: spread ต้องชนะ cost; √-law market impact; **borrow cost / ยืมช็อตได้จริงไหม**; financing/carry
- **Backtest ที่ไม่โกหก** (อ้าง `theory-part5`, เติมมุมลงมือ): purged/embargoed CV, deflated Sharpe, PBO; กับดัก "in-sample cointegrate → out-sample พัง"; survivorship-free universe
- **Risk & kill-switch**: DD ต่อ pair, pairs สัมพันธ์กันเอง (ไม่ diversify จริง), leg/gap/halt risk, size ตาม "ทน SD ได้กี่ตัว" ไม่ใช่ความมั่นใจ
- **Data reality**: corporate action, split/dividend adjust, stale print, bid-ask, timezone

---

## 5. โครงบท (เสนอ ~10 Part) — `practice-part0..9.html`

**Arc ของเล่ม:** framing → *pairwise* (จุดเริ่ม) → *factor/residual* (ที่โตขึ้นไป) → adaptive → trading → proving

| Part | ชื่อ | แกน |
|---|---|---|
| 0 | **Kalman ไม่ใช่ edge + แผนที่ Edge** | ตั้งความคาดหวัง: estimator = ท่อประปา; edge จริงอยู่ชั้น A–D (เน้น C+D สำหรับรายย่อย) |
| I | **บันได β — hedge ratio (pairwise)** | ทำไม OLS พัง → EIV → TLS/PCA → rolling |
| II | **Correlation & Cointegration ที่ใช้จริง** | funnel + cut-off จริง, differentiation 5 จุด, multiple-testing, **copula/MI** + *ขีดจำกัดของโลก pairwise* → สะพานสู่ Part III |
| **III** | **★ Residual / Factor Stat Arb** *(เอกใหม่)* | **pair = rank-1 special case; หัก common factor → เทรด residual; s-score (Avellaneda-Lee); cross-sectional; factor = ความเสี่ยง; DL residual (Pelger) + กับดัก; retail edge = บ่อที่ factor under-modeled** |
| IV | **Kalman ลงมือ** | state-space, จูน Q/R — dynamic **hedge ratio และ factor loadings**; worked example + โค้ด |
| V | **Adaptive & Robust Kalman** | vol-adaptive R ที่ถูกหลัก, innovation gating, regime-switching |
| VI | **Signals & Bands** | z-score / s-score vs cost-aware/ATR band, optimal threshold (OU) |
| VII | **Regime & Structural Break** | half-life monitor, Hurst, coint re-test, ADX proxy, kill switch |
| VIII | **Cost · Execution · Capacity · Borrow** | โลกจริงของรายย่อย |
| IX | **Backtest ไม่โกหก + Risk + Case study เต็ม** | paper → live + Cheat sheet "เลือก estimator/แนวทางยังไง" |

ทุกบท: การ์ด v4 เดิม + 🐍 โค้ดจริง + 🧪 ผล backtest จริง + 📖 review/ตำรา + cross-ref เล่ม 1

---

## 6. วรรณกรรมอ้างอิง (ของจริง — ยืนยันแล้ว ห้ามเพิ่มที่ไม่แน่ใจ)

**Survey/ตำรา (backbone):**
- Krauss (2017) "Statistical Arbitrage Pairs Trading Strategies: Review and Outlook" — *survey หลักที่ user ต้องการ*
- Vidyamurthy (2004) *Pairs Trading: Quantitative Methods and Analysis*
- Chan, Ernest (2013) *Algorithmic Trading* — โค้ด Kalman pairs
- López de Prado (2018) *Advances in Financial Machine Learning* — backtest rigor

**Papers ต้นฉบับ:**
- Engle & Granger (1987) cointegration · Johansen (1988, 1991) VECM
- Gatev, Goetzmann, Rouwenhorst (2006) pairs performance
- Elliott, van der Hoek, Malcolm (2005) pairs/OU state-space
- Avellaneda & Lee (2010) statistical arbitrage US equities (PCA)
- Leung & Li (2015) optimal mean-reversion trading (thresholds)
- Do & Faff (2010, 2012) pairs profitability + costs
- Deming (1943) / total least squares · Bai & Perron (1998, 2003) structural breaks

**★ สมัยใหม่ + Kalman ที่ "รายย่อยทำตามได้จริง" (ยืนยันแล้ว ก.ค. 2026):**
- **Palomar, D.P. (2025)** *Portfolio Optimization: Theory and Application*, Cambridge Univ. Press — §15.6 "Kalman Filtering for Pairs Trading" (อ่านฟรีที่ bookdown.org). ⭐ อ้างอิงหลักของ Part IV–V: state-space หา time-varying hedge ratio + mean, แสดงว่า Kalman คุม drawdown ได้จริง (rolling-LS ไม่คุม), วลีในเล่ม: *"Kalman filtering is a must in pairs trading"*
- **Primbs, J.A. & Yamada, Y. (2018)** "Pairs trading under transaction costs using model predictive control", *Quantitative Finance* 18(6):885–895 — MPC + proportional cost + gross-exposure constraint บน OU spread (ใช้ใน Part VI/VIII)
- **Mudchanatongsuk, S., Primbs, J.A. & Wong, W. (2008)** "Optimal pairs trading: a stochastic control approach", *Proc. American Control Conf. 2008* — log-spread เป็น OU, แก้ผ่าน HJB (รากฐานของสาย stochastic-control cost)
- **Tenyakov, A. & Mamon, R. (2017)** "A computing platform for pairs-trading online implementation via a blended Kalman–HMM filtering approach", *Journal of Big Data* 4:46 — Kalman + HMM regime, พารามิเตอร์ self-updating แบบ online (อ้างใน Part IV adaptive/regime-switching Kalman)

**★ "Edge ย้ายไปไหน" — ML/DL + selection (สำหรับ Part 0 · ยืนยันแล้ว ก.ค. 2026):**
- **Sun, Y. (2025)** "A survey of statistical arbitrage pair trading with machine learning, deep learning, and reinforcement learning methods", *Univ. of Warsaw WP 2025-22* — **survey ที่ user ขอ** สำหรับ "edge ย้ายไปไหน"
- **Guijarro-Ordóñez, J., Pelger, M. & Zanotti, G.** "Deep Learning Statistical Arbitrage", *Management Science* (accepted 2024) — CNN/transformer บน residual ของ factor model = งาน top-journal ตัวแทน "ชั้น B"
- **Fischer, T. & Krauss, C. (2018)** LSTM stat arb S&P 500, *EJOR*; **Krauss, Do & Huck (2017)** DNN/GBT/RF stat arb S&P 500, *EJOR* — คลาสสิก ML stat arb
- **Clegg, M. & Krauss, C. (2018)** "Pairs trading with partial cointegration", *Quantitative Finance* — แยกส่วน mean-revert ออกจาก random-walk (ชั้น A selection)
- multi-pair graph clustering (arXiv 2024) · crypto pairs DL/DRL (2024–26) — ตัวแทนชั้น A/D (อ้างเป็นทิศทาง ไม่ใช่ alpha สำเร็จรูป)

**สอน "ลงมือทำ" ระดับรายย่อย (tutorial/code — ไม่ใช่ paper แต่ reproduce ได้):**
- QuantStart — "Dynamic Hedge Ratio Between ETF Pairs Using the Kalman Filter" + "Kalman Filter-Based Pairs Trading in QSTrader"
- QuantInsti blog — "Kalman Filter in Python: Tutorial and Strategies" (อัปเดต 2024, ข้อมูลตัวอย่างจริง)
- Palomar MAFS5310 lecture slides (HKUST) — pairs trading + Kalman
- GitHub repos: robust-Kalman + HMM pairs (เช่น EwanKW, git-kevinxuhuili) — โครงโค้ดตั้งต้นที่ปรับใช้ได้

> **⚠️ หมายเหตุการยืนยัน (สำคัญ):** เปเปอร์ชื่อ *"Pairs Trading Under Transaction Costs" โดย Mudchanivuth, S. & Sharp, J. A.* — **ยืนยันการมีอยู่ไม่ได้** จากการค้น (ก.ค. 2026) สันนิษฐานว่าเป็นการจำสลับของ 2 งานจริง: ชื่อเรื่องตรงกับ **Primbs & Yamada (2018)** ส่วนนามสกุล "Mudchana-" ตรงกับ **Mudchanatongsuk et al. (2008)** — ทั้งคู่ยืนยันแล้วและใส่ไว้ด้านบน หากผู้ใช้มี DOI/ลิงก์ของฉบับ Mudchanivuth-Sharp จริง ค่อยเพิ่มภายหลัง (ตามกฎ: ไม่แน่ใจ = ไม่ใส่)

> กฎ: อ้างเฉพาะที่มีจริง; ตอนเขียนแต่ละ Part ให้ยืนยันปี/ผู้แต่งอีกครั้ง ไม่มั่นใจให้ตัด

---

## 7. โฟลเดอร์โค้ด `docs/vol2-code/`

**⚠️ Pivot ที่เคาะแล้ว (สำคัญ):** แผนเดิมตั้งใจใช้ราคาจริง (US ETF ผ่าน yfinance/stooq) — แต่สภาพแวดล้อมที่ build จริงบล็อกการเชื่อมต่อ data provider การเงินทุกเจ้า (ทดสอบแล้ว: Yahoo Finance + Stooq ถูกนโยบาย network ปฏิเสธทั้งคู่) จึงเปลี่ยนมาใช้ **ข้อมูลจำลอง (simulated) ที่มี DGP รู้ค่าและเปิดเผยชัดเจน** (`simdata.py`) แทน — ข้อดีที่ไม่คาดคิด: รู้ β/spread/factor loading จริง จึงวัด bias ของแต่ละ estimator ได้ตรง ๆ (ราคาจริงไม่ให้ ground truth แบบนี้) รายละเอียดเหตุผล + วิธีสลับกลับไปใช้ราคาจริงอยู่ใน `vol2-code/README.md`

**สถานะจริง ณ ตอนนี้ (Phase 1 — เสร็จและ execute แล้วทุกไฟล์):**
- `simdata.py` — ตัวสร้างข้อมูลจำลอง (seed คงที่, reproduce ได้ 100%)
- `01_beta_ladder.ipynb` ✅ — OLS(price) vs OLS(return) vs TLS vs Rolling vs Kalman; วัด bias/RMSE จริง (Part I)
- `02_cointegration_copula.ipynb` ✅ — Engle-Granger (`coint()` ที่ถูก vs `adfuller`-on-residual ที่ผิด), half-life, Hurst, multiple-testing simulation, Gaussian-copula MI (Part II)
- `03_factor_residual.ipynb` ✅ — PCA หัก factor + s-score cross-sectional + เช็ค residual สะอาด (Part III)
- `build_nb0{1,2,3}.py` — สคริปต์ source-of-truth ที่ generate แต่ละ .ipynb (แก้ตรงนี้ ไม่แก้ .ipynb JSON ตรง ๆ)
- `*.png` — กราฟที่ execute ออกมาจริง (embed อยู่ใน notebook ด้วย, แยกไฟล์ไว้เผื่อใช้ประกอบเนื้อหา HTML ทีหลัง)
- `requirements.txt` — numpy, pandas, scipy, statsmodels, matplotlib, scikit-learn (PCA), pykalman + nbformat/nbclient/ipykernel (สำหรับรัน). **ไม่ใช้ arbitragelab** (หนักเกินความจำเป็นสำหรับสาธิต — เขียน Gaussian copula เองแทน; `arbitragelab` แนะนำไว้เป็น optional สำหรับคนอยากไปต่อ Clayton/Gumbel/Student-t)
- `README.md` — เหตุผล data pivot + วิธีรัน/แก้ไขซ้ำ + ข้อจำกัดที่ต้องรู้ก่อนใช้ตัวเลข

**บั๊กจริงที่เจอระหว่างสร้าง + วิธีแก้ (คุ้มบันทึกไว้ กันคนอื่นเจอซ้ำ):**
1. สูตร Hurst exponent เดิมคูณ slope ด้วย 2 ผิดที่ (fit บน `std` ไม่ใช่ `variance` — ไม่ต้องคูณ 2) ทำให้ random walk ได้ H≈0.95–1.0 แทนที่จะเป็น ~0.5
2. ใช้ `adfuller()` ตรง ๆ บน OLS residual (วิธีที่ tutorial ทั่วไปสอน) แทนที่จะใช้ `statsmodels.tsa.stattools.coint()` — ทำให้ false-positive rate ในซิมูเลชัน multiple-testing (n=300, α=0.05) พุ่งจาก ~12 (ถูกต้อง ใกล้ค่าคาดหวัง 15) เป็น ~44 (เกือบ 3 เท่า) เพราะ residual ที่ fit แล้วดูนิ่งเกินจริงเสมอ (ต้องใช้ critical value ของ Engle-Granger/MacKinnon ไม่ใช่ ADF ทั่วไป) — ทั้งสองเรื่องนี้ถูกเก็บไว้เป็นบทเรียนในตัวโน้ตบุ๊กเอง ไม่ใช่แค่แก้เงียบ ๆ

**ยังไม่ทำ (รอ Phase 2–3):**
- `04_kalman_tuning.ipynb` — grid Q/R + MLE/EM + adaptive/robust variant (Part IV–V)
- `05_bands_and_costs.ipynb` — z/s-score vs ATR vs optimal band + net PnL หลัง cost (Part VI)
- `06_regime_killswitch.ipynb` — half-life/Hurst/coint-retest/ADX + kill switch + estimator-disagreement gate (Part VII)
- `07_full_backtest.ipynb` — ประกอบร่าง + purged CV + deflated Sharpe (Part IX)

> ตัวเลขในกล่อง 🧪 ทุกตัวต้อง reproduce ได้จาก notebook เหล่านี้ — Part I–III ยังไม่ได้ฝัง 🧪 box อ้างตัวเลขเฉพาะจาก 01–03 ลง HTML (เนื้อหาปัจจุบันอ้างอิง literature stats เป็นหลัก) เป็นงานเสริมที่ทำได้ใน Phase 4 ถ้าต้องการ

---

## 8. ลำดับงาน (Build Order)

- **Phase 0** — ✅ แผนนี้ (commit + draft PR)
- **Phase 1** — ✅ **เสร็จสมบูรณ์**: narrative + notebook ครบทั้งคู่
  - ✅ Part 0 (edge framing) · ✅ Part I (บันได β) · ✅ Part II (coint/copula) · ✅ Part III (residual/factor)
  - ✅ notebook 01–03 เขียน + execute จริงแล้ว (ดู §7 — pivot ไปใช้ simulated data เพราะ network policy บล็อก data provider)
- **Phase 2** — Part IV–VII (Kalman + Adaptive + Bands + Regime) + notebook 04–06
- **Phase 3** — Part VIII–IX (Cost/Execution + Backtest/Risk/Case) + notebook 07
- **Phase 4** — index/cross-ref เชื่อมเล่ม 1 + generate PDF (ใช้ `generate-pdf.js` เดิม)

แต่ละ Phase: commit แยก + ผ่านรีวิวทีมผู้เชี่ยวชาญ (เหมือนเล่ม 1) ก่อนไป Phase ถัดไป

---

## 9. Convention ที่ต้องคุมให้ตรง

- **Notation**: `β, S, σ, w, Σ, z, κ (mean-reversion speed), θ (long-run mean)` ให้ตรงเล่ม 1 + `theory-part5`
- **Cross-ref**: ลิงก์ `arb-part5/7`, `theory-part5` แทนเขียนซ้ำเสมอ
- **Difficulty tier**: L1/L2/L3 ทุกบท; กล่อง "เจาะลึก (ข้ามได้)" สำหรับ derivation Kalman/Johansen
- **Style guide**: ยึด `quant-theory-volumes-plan.md` §4.6 (line-break ไทย, `<ul>`/`<p>` ไม่ใช่ `<br>`, `.fm` เฉพาะสูตร)
