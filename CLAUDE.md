# CLAUDE.md

แนวทางสำหรับ repo นี้ (Guidelines for this repository)

repo นี้ใช้สร้างหนังสือ/เอกสารการเรียนรู้ภาษาไทย เกี่ยวกับ quantitative finance
(การเงินเชิงปริมาณ) และ options trading (การเทรดออปชัน)

## กฎการใช้คำศัพท์ในหนังสือ (Terminology rule for books)

**เมื่อสร้างหรือแก้ไขหนังสือทุกเล่มใน repo นี้ ให้ทำตามกฎนี้เสมอ:**

หากพบ **technical term (คำศัพท์เทคนิค)** ให้ **ทับศัพท์** โดยคงคำภาษาอังกฤษ/คำเทคนิคไว้
แล้ว **วงเล็บคำแปลไทย** ต่อท้ายในการกล่าวถึงครั้งแรก

รูปแบบ (Format):

```
English technical term (คำแปลไทย)
```

ตัวอย่าง (Examples):

- Long Call (สถานะซื้อสิทธิ์ซื้อ)
- Compound Interest (ดอกเบี้ยทบต้น)
- Geometric Series (อนุกรมเรขาคณิต)
- Implied Volatility (ความผันผวนแฝง)
- Delta Hedging (การป้องกันความเสี่ยงด้วยเดลตา)

**เหตุผล (Why):** ผู้อ่านจะได้เรียนรู้คำศัพท์ภาษาอังกฤษและ technical term ไปพร้อมกัน
เพื่อให้เข้าใจและต่อยอดได้เมื่ออ่านหนังสือเล่มอื่น ๆ ที่ใช้คำศัพท์เดียวกัน

### รายละเอียดเพิ่มเติม (Details)

- **คงคำภาษาอังกฤษเป็นหลัก** สำหรับ technical term — อย่าแปลทิ้งจนเหลือแต่ภาษาไทย
  (keep the English term as the primary form; do not replace it entirely with Thai)
- ใส่คำแปลไทยในวงเล็บ **ครั้งแรกที่เอ่ยถึง** คำนั้นในแต่ละเล่ม/แต่ละ part หลังจากนั้น
  ใช้คำภาษาอังกฤษได้เลยโดยไม่ต้องวงเล็บซ้ำทุกครั้ง
- ใช้กับคำที่เป็นศัพท์เทคนิคจริง ๆ (เช่น ศัพท์การเงิน คณิตศาสตร์ สถิติ การเขียนโปรแกรม)
  ไม่จำเป็นต้องทับศัพท์คำทั่วไปในชีวิตประจำวัน
- สัญลักษณ์ทางคณิตศาสตร์ (เช่น S, K, σ) สามารถวงเล็บอธิบายความหมายไทยได้เช่นกัน
  เช่น `S (ราคาหุ้น)`, `σ (ความผันผวน)`

## ตารางศัพท์มาตรฐาน (Standard glossary)

**ใช้คำแปลไทยตามตารางนี้เสมอ** เพื่อให้ทุกเล่มแปลคำเดียวกันให้ตรงกัน (อย่าแปลคำเดิม
สลับไปมา เช่น Premium ต้องเป็น "ค่าพรีเมียม" เหมือนกันทุกเล่ม ไม่ใช่บางที่ "เบี้ยประกัน")

หากเจอ technical term ใหม่ที่ยังไม่มีในตาราง ให้ **เพิ่มลงตารางนี้** พร้อมคำแปลไทย
ที่เลือกใช้ เพื่อให้เล่มถัด ๆ ไปใช้ตรงกัน

### พื้นฐานออปชัน (Options basics)

| English term | คำแปลไทย (วงเล็บครั้งแรก) |
|---|---|
| Call (Option) | สิทธิ์ซื้อ |
| Put (Option) | สิทธิ์ขาย |
| Long | สถานะซื้อ/ถือซื้อ |
| Short | สถานะขาย/ขายชอร์ต |
| Strike Price (K) | ราคาใช้สิทธิ์ |
| Premium | ค่าพรีเมียม (ราคาออปชัน) |
| Expiration / Expiry | วันหมดอายุ |
| Exercise | การใช้สิทธิ์ |
| Assignment | การถูกใช้สิทธิ์ |
| Payoff | ผลตอบแทน ณ วันหมดอายุ |
| Intrinsic Value | มูลค่าที่แท้จริง |
| Time Value | มูลค่าตามเวลา |
| Underlying (Asset) | สินทรัพย์อ้างอิง |
| Moneyness | สถานะราคาเทียบจุดใช้สิทธิ์ |
| In-the-money (ITM) | ราคาอยู่ในเงิน (มีมูลค่าใช้สิทธิ์) |
| At-the-money (ATM) | ราคาเท่าจุดใช้สิทธิ์ |
| Out-of-the-money (OTM) | ราคาอยู่นอกเงิน (ยังไม่มีมูลค่าใช้สิทธิ์) |
| European Options | ออปชันแบบยุโรป (ใช้สิทธิ์ได้เฉพาะวันหมดอายุ) |
| American Options | ออปชันแบบอเมริกัน (ใช้สิทธิ์ได้ทุกวันก่อนหมดอายุ) |
| Settlement | การชำระราคา |
| Break-even (Point) | จุดคุ้มทุน |

### กรีก (Greeks)

| English term | คำแปลไทย (วงเล็บครั้งแรก) |
|---|---|
| Delta | เดลตา (ความไวต่อราคาสินทรัพย์อ้างอิง) |
| Gamma | แกมมา (อัตราการเปลี่ยนของเดลตา) |
| Theta | ทีตา (ค่าเสื่อมตามเวลา) |
| Vega | เวกา (ความไวต่อความผันผวน) |
| Rho | โร (ความไวต่ออัตราดอกเบี้ย) |

### ความผันผวน (Volatility)

| English term | คำแปลไทย (วงเล็บครั้งแรก) |
|---|---|
| Volatility (σ) | ความผันผวน |
| Implied Volatility (IV) | ความผันผวนแฝง |
| Historical / Realized Volatility (HV/RV) | ความผันผวนในอดีต/ที่เกิดขึ้นจริง |
| Volatility Skew / Smile | ความเบ้/รอยยิ้มของความผันผวน |

### กลยุทธ์ (Strategies)

| English term | คำแปลไทย (วงเล็บครั้งแรก) |
|---|---|
| Spread | สเปรด (กลยุทธ์หลายขา) |
| Bull Call Spread | สเปรดซื้อแบบกระทิง |
| Bear Put Spread | สเปรดขายแบบหมี |
| Straddle | สแตรดเดิล (ซื้อ Call+Put ที่ Strike เดียวกัน) |
| Strangle | สแตรงเกิล (ซื้อ Call+Put คนละ Strike) |
| Butterfly | บัตเตอร์ฟลาย |
| Iron Condor | ไอรอนคอนดอร์ |
| Calendar Spread | สเปรดต่างเดือนหมดอายุ |
| Diagonal Spread | สเปรดทแยง |
| Ratio Spread | สเปรดอัตราส่วน |
| Conversion | คอนเวอร์ชัน (กลยุทธ์ล็อกกำไรจากพุต-คอล) |
| Reversal | รีเวอร์ซัล (คอนเวอร์ชันแบบกลับด้าน) |
| Bull Put Spread | สเปรดพุตแบบกระทิง |
| Bear Call Spread | สเปรดคอลแบบหมี |
| Synthetic (Position) | สถานะสังเคราะห์ |
| Synthetic Forward | ฟอร์เวิร์ดสังเคราะห์ |
| Covered Call | คอฟเวอร์คอล |
| Protective Put | พุตป้องกันความเสี่ยง |
| Collar | คอลลาร์ (ปลอกคอ) |
| Roll | การเลื่อน/ต่ออายุสถานะ |

### การกำหนดราคาและคณิตศาสตร์ (Pricing & math)

| English term | คำแปลไทย (วงเล็บครั้งแรก) |
|---|---|
| Black-Scholes (Model) | แบบจำลองแบล็ก-โชลส์ |
| Put-Call Parity | ความเท่าเทียมระหว่างพุตและคอล |
| Discount Factor | ตัวคิดลด |
| Present Value (PV) | มูลค่าปัจจุบัน |
| Future Value (FV) | มูลค่าอนาคต |
| Compound Interest | ดอกเบี้ยทบต้น |
| Geometric Series | อนุกรมเรขาคณิต |
| Normal Distribution | การแจกแจงปกติ |
| Standard Deviation | ส่วนเบี่ยงเบนมาตรฐาน |
| Variance | ความแปรปรวน |
| Mean | ค่าเฉลี่ย |
| Correlation | สหสัมพันธ์ |
| Covariance | ความแปรปรวนร่วม |
| Regression | การถดถอย |
| Brownian Motion | การเคลื่อนที่แบบบราวน์ |
| Geometric Brownian Motion (GBM) | การเคลื่อนที่บราวน์เชิงเรขาคณิต |
| Cumulative Distribution Function (CDF) | ฟังก์ชันการแจกแจงสะสม |
| Expected Value (EV) | มูลค่าคาดหวัง |
| Prediction | การคาดการณ์ราคา |

### การเก็งกำไร ความเสี่ยง และการเทรด (Arbitrage, risk & trading)

| English term | คำแปลไทย (วงเล็บครั้งแรก) |
|---|---|
| Arbitrage | การเก็งกำไรส่วนต่างราคา (อาร์บิทราจ) |
| Liquidity | สภาพคล่อง |
| Bid-Ask Spread | ส่วนต่างราคาเสนอซื้อ-เสนอขาย |
| Slippage | ส่วนต่างราคาที่คลาดเคลื่อน |
| Commission | ค่านายหน้า |
| Leverage | การใช้เลเวอเรจ (อัตราทด) |
| Short Selling | การขายชอร์ต (ยืมมาขาย) |
| Dividend | เงินปันผล |
| Counterparty | คู่สัญญา |
| Execution Risk | ความเสี่ยงด้านการส่งคำสั่ง |
| Model Risk | ความเสี่ยงของแบบจำลอง |
| Cointegration | โคอินทิเกรชัน (ความสัมพันธ์ระยะยาว) |
| Mean Reversion | การกลับเข้าสู่ค่าเฉลี่ย |
| Overfitting | การฟิตเกินพอดี |
| Hedging | การป้องกันความเสี่ยง |
| Delta Hedging | การป้องกันความเสี่ยงด้วยเดลตา |
| Delta-neutral | สถานะเป็นกลางต่อทิศทางราคา |
| Funding Rate | อัตราค่าธรรมเนียมการถือสถานะ (สัญญา Perpetual) |
| Ex-dividend (ex-div / XD) | วันขึ้นเครื่องหมายไม่ได้รับสิทธิเงินปันผล |

### ตลาดทำนายผล DeFi และตราสารโครงสร้าง (Prediction markets, DeFi & structured products)

| English term | คำแปลไทย (วงเล็บครั้งแรก) |
|---|---|
| Prediction Market (PM) | ตลาดทำนายผล |
| Digital / Binary Option | ออปชันดิจิทัล (จ่ายคงที่) |
| Impermanent Loss (IL) | การขาดทุนชั่วคราว |
| Maximal Extractable Value (MEV) | มูลค่าสูงสุดที่สกัดได้ |
| Flash Loan | สินเชื่อแฟลช (กู้-คืนในธุรกรรมเดียว) |
| Knock-out / Barrier | ระดับน็อกเอาต์ / กำแพงราคา |
| Equity-Linked Note (ELN) | ตราสารหนี้อิงหุ้น |
| Overround | ส่วนเกินผลรวมความน่าจะเป็น |
| Resolution / Settle | การตัดสินผล/ชำระ |

### Stat arb และคริปโต (Statistical arbitrage & crypto) — ใช้ในเล่ม "Stat Arb for Non Quant" (`docs/sab-*`)

คำที่มีในหมวดก่อนหน้าแล้วใช้ตามนั้น (Mean Reversion · Standard Deviation · Correlation · Expected Value · Bid-Ask Spread · Leverage · Hedging · Funding Rate · Cointegration · Arbitrage · Settlement · Break-even · Liquidity · Slippage · Counterparty · Overfitting · Mean · Median ใช้ตามตารางนี้)

| English term | คำแปลไทย (วงเล็บครั้งแรก) |
|---|---|
| Statistical Arbitrage (Stat Arb) | การเก็งกำไรเชิงสถิติ |
| Spot | ตลาดซื้อขายทันที |
| Futures (Dated Futures) | สัญญาซื้อขายล่วงหน้า (มีวันหมดอายุ) |
| Perpetual Futures (Perp) | สัญญาล่วงหน้าแบบไม่มีวันหมดอายุ |
| Basis | ส่วนต่างราคา futures กับ spot |
| Annualized Basis | อัตรา basis ต่อปี |
| Cash-and-Carry | ซื้อ spot คู่กับขาย futures เพื่อเก็บ basis |
| Carry | ผลตอบแทนจากการถือ |
| Settlement Price | ราคาชำระ |
| Maker Order | คำสั่งตั้งรอ |
| Taker Order | คำสั่งซื้อขายทันที |
| Round Trip | การเปิดแล้วปิดหนึ่งครั้ง (ไปกลับ) |
| Margin (Collateral) | หลักประกัน |
| Liquidation | การถูกบังคับปิดสถานะ |
| Mark Price | ราคาที่ exchange ใช้คิดหลักประกัน |
| Wick | ไส้เทียน (ราคาพุ่งชั่วขณะ) |
| Auto-Deleveraging (ADL) | การลดสถานะอัตโนมัติ |
| Insurance Fund | กองทุนประกันของ exchange |
| Isolated / Cross Margin | หลักประกันแยก / หลักประกันรวม |
| Haircut | ส่วนลดมูลค่าหลักประกัน |
| Equity | มูลค่าบัญชีรวม |
| Free Cash | เงินสดอิสระ |
| Cash Buffer | กันชนเงินสด |
| Hurdle Rate | ผลตอบแทนขั้นต่ำของทุน |
| Opportunity Cost | ค่าเสียโอกาส |
| Exposure | ความเสี่ยงสุทธิต่อตลาด |
| Beta (β) | ค่าเบต้า (ความไวต่อตลาด) |
| Gross Exposure | มูลค่าสองขารวมกัน |
| Net Exposure | มูลค่าสุทธิ |
| Dollar-neutral / Market-neutral | เป็นกลางต่อมูลค่า / เป็นกลางต่อตลาด |
| Hedge Ratio (h) | อัตราส่วนการป้องกันความเสี่ยง |
| Pair Spread (X) | ส่วนต่างของคู่ (เขียน "Spread ของคู่") |
| Z-score | ค่ามาตรฐาน (ระยะห่างเป็นจำนวนส่วนเบี่ยงเบนมาตรฐาน) |
| Formation Period / Test Period | ช่วงเลือก / ช่วงทดสอบ |
| Random Walk | การเดินสุ่ม |
| Half-life | ครึ่งชีวิต (เวลาที่ระยะห่างหดเหลือครึ่ง) |
| Persistence (φ) | อัตราคงเหลือต่อช่วง |
| Time to Target | เวลาแตะเป้า |
| Selection Bias | ความเอนเอียงจากการคัดเลือก |
| Data Snooping (Multiple Testing) | โชคจากการลองหลายครั้ง |
| Win Rate | อัตราชนะ |
| Break-even Win Rate | อัตราชนะที่ต้องได้ |
| Drawdown | การลดลงจากจุดสูงสุด |
| Capacity | ขนาดที่กลยุทธ์รับได้ |
| Crowding | การแห่ทำกลยุทธ์เดียวกัน |
| Crowded Unwind | การแห่ปิดสถานะพร้อมกัน |
| Regime Change | การเปลี่ยนสภาพตลาด |
| Order Book | กระดานคำสั่ง |
| Fill | การได้ราคาตามคำสั่ง |
| Partial Fill | การได้ราคาไม่ครบ |
| Legging Risk | ความเสี่ยงได้ขาเดียว |
| Netting | การหักกลบคำสั่ง |
| No-trade Buffer | กันชนไม่เทรด |
| Lot Size | ขนาดสั่งขั้นต่ำ |
| Backtest | การทดสอบย้อนหลัง |
| Paper Trading | การเทรดกระดาษ |
| Sharpe Ratio | อัตราส่วนชาร์ป |
| Stablecoin | เหรียญคงมูลค่า |
| Depeg | การหลุดหมุด |
| Pause Mode | โหมดพัก |
| Grid Bot | บอทกริด (ซื้อขายเป็นขั้นบันได) |
| Median | มัธยฐาน |
| Mid Price | ราคากลาง |
| Market Maker | ผู้ดูแลสภาพคล่อง |
| Adverse Selection | การคัดเลือกที่ไม่พึงประสงค์ |
| Rebate | เงินคืนค่าธรรมเนียม |
| Linear Contract | สัญญาแบบเชิงเส้น |
| Inverse Contract | สัญญาแบบผกผัน |
| Position Value | มูลค่าสถานะ |
| Unrealized PnL | กำไรค้าง (ยังไม่ปิดสถานะ) |
| Realized PnL | กำไรรับรู้ |
| Daily Settlement | การชำระสิ้นวัน |
| Variation Margin | เงินโอนตามกำไรขาดทุนรายวัน |
| Initial Margin | หลักประกันเริ่มต้น |
| Maintenance Margin | ระดับรักษาหลักประกัน |
| Margin Call | การเรียกหลักประกัน |
| Premium Index | ส่วนพรีเมียม (ส่วนหนึ่งของสูตร funding) |
| Interest Rate Component | ส่วนดอกเบี้ย (ส่วนหนึ่งของสูตร funding) |
| Stop-loss | เส้นตัดขาดทุน |
| Sunk Cost | ต้นทุนที่จ่ายแล้ว |
| Factor Model | โมเดลปัจจัย |
| Rebalance | การปรับสัดส่วน (ปรับ hedge) |
| Survivorship Bias | อคติผู้รอด |
| Regression to the Mean | ถอยสู่ค่าเฉลี่ย (คนละเรื่องกับ Mean Reversion) |
| Noise | แรงสะบัด |
| Strategy Specification | ข้อกำหนดกลยุทธ์ |
| Forecast Error | คาดพลาด |
| Post-only | ตั้งรอเท่านั้น |
| IOC (Immediate-or-Cancel) | ได้เท่าไรเอาเท่านั้น |
| Reduce-only | ลดสถานะเท่านั้น |
| Inventory | ของค้าง |
| Counterparty Risk | ความเสี่ยงคู่สัญญา |
| Prediction (ชื่อกลไกในช่อง ①) | การคาดการณ์ราคา — ในเล่มนี้คือ Mean Reversion ของคู่ |

คำสอนเฉพาะเล่มที่ไม่ใช่ศัพท์เทคนิค ใช้ไทยได้เลย: เชือก (ภาพเปรียบ) · คนเร่ง / คนรีบ / คนรู้ · มือที่แย่งเชือก (ภาพของ Crowding) · บัตรธรรมชาติ · แถบผล · รอบชดเชย · กฎทอง · ไม้บรรทัด · สองกระเป๋า
