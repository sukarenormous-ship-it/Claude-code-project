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
| Synthetic (Position) | สถานะสังเคราะห์ |
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
