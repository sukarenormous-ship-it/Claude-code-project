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
| **แกนเล่ม** | "บันได β" (Hedge-Ratio Estimation Ladder): OLS → TLS/PCA → Rolling → **Kalman** → Adaptive/VECM |
| **กฎเหล็ก** | เขียนครั้งเดียวมีบ้านเดียว — เรื่องที่เล่ม 1 มีแล้วให้ *อ้างอิง* ไม่เขียนซ้ำ |
| **รูปแบบไฟล์** | HTML self-contained สไตล์เดิม (`practice-part1..8.html`) **+** โฟลเดอร์ `docs/vol2-code/` (Jupyter/.py + toy dataset ที่รันได้จริง) |
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

## 5. โครงบท (เสนอ ~8 Part) — `practice-part1..8.html`

| Part | ชื่อ | แกน |
|---|---|---|
| 0 | **Kalman ไม่ใช่ edge + แผนที่ Edge** | ตั้งความคาดหวัง: estimator = ท่อประปา; edge จริงอยู่ชั้น A–D (เน้น C+D สำหรับรายย่อย) |
| I | **บันได β (1)** | ทำไม OLS พัง → EIV → TLS/PCA |
| II | **Cointegration ใช้จริง** | Engle-Granger, Johansen/VECM, OU half-life, re-testing |
| III | **Kalman ลงมือ** | state-space, จูน Q/R, worked example + โค้ด |
| IV | **Adaptive & Robust Kalman** | vol-adaptive R ที่ถูกหลัก, innovation gating, regime-switching |
| V | **Signals & Bands** | z-score vs cost-aware/ATR band, optimal threshold (OU) |
| VI | **Regime & Structural Break** | half-life monitor, Hurst, coint re-test, ADX proxy, kill switch |
| VII | **Cost · Execution · Capacity · Borrow** | โลกจริงของรายย่อย |
| VIII | **Backtest ไม่โกหก + Risk + Case study เต็ม** | paper → live + Cheat sheet "เลือก estimator ยังไง" |

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
- **Palomar, D.P. (2025)** *Portfolio Optimization: Theory and Application*, Cambridge Univ. Press — §15.6 "Kalman Filtering for Pairs Trading" (อ่านฟรีที่ bookdown.org). ⭐ อ้างอิงหลักของ Part III–IV: state-space หา time-varying hedge ratio + mean, แสดงว่า Kalman คุม drawdown ได้จริง (rolling-LS ไม่คุม), วลีในเล่ม: *"Kalman filtering is a must in pairs trading"*
- **Primbs, J.A. & Yamada, Y. (2018)** "Pairs trading under transaction costs using model predictive control", *Quantitative Finance* 18(6):885–895 — MPC + proportional cost + gross-exposure constraint บน OU spread (ใช้ใน Part V/VII)
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

- `data/` — toy dataset (คู่หุ้น/ETF ตัวอย่าง, ปรับ corporate action แล้ว) เล็กพอ commit ได้
- `01_beta_ladder.ipynb` — OLS vs TLS vs Rolling vs Kalman บนคู่เดียวกัน เทียบ β path
- `02_cointegration.ipynb` — Engle-Granger + Johansen + half-life
- `03_kalman_tuning.ipynb` — grid Q/R + adaptive/robust variant
- `04_bands_and_costs.ipynb` — z vs ATR vs optimal band + net PnL หลัง cost
- `05_regime_killswitch.ipynb` — half-life/Hurst/coint-retest/ADX + kill switch
- `06_full_backtest.ipynb` — ประกอบร่าง + purged CV + deflated Sharpe
- `requirements.txt` — numpy, pandas, statsmodels, pykalman, matplotlib (ไลบรารีมาตรฐาน ไม่ต้อง infra แพง)

> ตัวเลขในกล่อง 🧪 ทุกตัวต้อง reproduce ได้จาก notebook เหล่านี้

---

## 8. ลำดับงาน (Build Order)

- **Phase 0** — ✅ แผนนี้ (commit + draft PR)
- **Phase 1** — Part I–III (บันได β + Cointegration + Kalman) = 3 บทแกนหลัก + notebook 01–03
- **Phase 2** — Part IV–VI (Adaptive Kalman + Bands + Regime) + notebook 04–05
- **Phase 3** — Part VII–VIII (Cost/Execution + Backtest/Risk/Case) + notebook 06
- **Phase 4** — index/cross-ref เชื่อมเล่ม 1 + generate PDF (ใช้ `generate-pdf.js` เดิม)

แต่ละ Phase: commit แยก + ผ่านรีวิวทีมผู้เชี่ยวชาญ (เหมือนเล่ม 1) ก่อนไป Phase ถัดไป

---

## 9. Convention ที่ต้องคุมให้ตรง

- **Notation**: `β, S, σ, w, Σ, z, κ (mean-reversion speed), θ (long-run mean)` ให้ตรงเล่ม 1 + `theory-part5`
- **Cross-ref**: ลิงก์ `arb-part5/7`, `theory-part5` แทนเขียนซ้ำเสมอ
- **Difficulty tier**: L1/L2/L3 ทุกบท; กล่อง "เจาะลึก (ข้ามได้)" สำหรับ derivation Kalman/Johansen
- **Style guide**: ยึด `quant-theory-volumes-plan.md` §4.6 (line-break ไทย, `<ul>`/`<p>` ไม่ใช่ `<br>`, `.fm` เฉพาะสูตร)
