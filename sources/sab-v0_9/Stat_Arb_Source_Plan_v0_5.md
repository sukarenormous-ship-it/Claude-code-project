# รายละเอียดแผนต้นฉบับ Stat Arb ฉบับ 0.5

ข้อมูลส่วนนี้มีอยู่แล้วในต้นฉบับ JSON ของฉบับ 0.5 แต่ไม่ได้แสดงทั้งหมดในหนังสือ PDF จัดรวมเป็นไฟล์ประกอบเพื่อเก็บรายละเอียดการออกแบบ โดยยังไม่ได้เพิ่มเนื้อหาหรือทำวิจัยต่อ

## รายละเอียดกรณีศึกษา

### C1 Pairs trading และเส้นทางจาก research สู่ algorithm

#### design_axes

##### asset_selection

เหตุผลในการเลือกคู่และช่วงที่ใช้คัดเลือก

##### workflow

ข้อมูล การประมาณ hedge การสร้าง signal และเวลาใช้ข้อมูล

##### position_management

ขนาดรายขา การปรับ hedge และกฎเข้าออก

#### replication_note

Palomar และ QuantConnect เป็นคนละ implementation ต้องระบุขั้นตอนที่นำมาเปรียบเทียบ บันทึกเวอร์ชันและสิทธิการใช้ข้อมูลก่อนรัน

### C2 คู่ที่เคยทำงานแล้วผลเสื่อมลง

#### design_axes

##### asset_selection

Universe, liquidity และการเลือกคู่จากช่วงฝึก

##### workflow

Cointegration screening, backtest และ out-of-sample evaluation

##### position_management

การรวมคู่ที่เลือกและเงื่อนไขปรับ universe

#### replication_note

ตัวอย่างพึ่งพา QuantRocket/Moonshot และข้อมูลที่ผู้ใช้ต้องเข้าถึง การมี notebook สาธารณะยังต้องตรวจ dependencies และข้อมูล

### C3 Factor และ PCA residual statistical arbitrage

#### design_axes

##### asset_selection

Universe ที่ใช้ประมาณปัจจัยและสินทรัพย์ที่มีข้อมูลเพียงพอ

##### workflow

ประมาณ factor สร้าง residual process แล้วประเมิน mean reversion

##### position_management

แปลงสัญญาณเป็น holdings และรวมสถานะ hedge ที่ซ้ำกัน

#### replication_note

ArbitrageLab เป็น implementation ของผู้อื่น ต้องเทียบกฎและเครื่องหมายกับต้นฉบับ รวมทั้งตรวจว่า residual หมายถึงระดับหรือผลตอบแทน

### C4 Sparse mean-reverting portfolio selection

#### design_axes

##### asset_selection

กำหนด universe และจำนวนขาที่อนุญาต

##### workflow

เลือกตัวชี้วัด สร้างปัญหา optimization แล้วตรวจพฤติกรรมนอกช่วงสร้าง

##### position_management

คำนวณขนาดรายขา turnover และต้นทุนของตะกร้าที่เลือก

#### replication_note

จำนวนขาที่เหมาะสมต้องประเมินร่วมกับสภาพคล่อง ต้นทุน และความเสถียร ไม่ใช้จำนวนขาจากตัวอย่างเป็นค่าที่เหมาะกับตลาดของเราโดยอัตโนมัติ

### C5 Finding moving-band statistical arbitrages

#### design_axes

##### asset_selection

Universe และข้อจำกัดที่มีผลต่อสินทรัพย์ในตะกร้า

##### workflow

ค้นน้ำหนักด้วยปัญหา optimization แล้วสร้างกฎซื้อขาย

##### position_management

ถือและเลิกใช้ตะกร้าตามกติกา พร้อมติดตามความเบี่ยงเบนจากกรอบ

#### replication_note

ข้อมูลหุ้นที่ใช้ในงานเดิมมีข้อจำกัดการเข้าถึง และต้องตรวจ solver/dependencies ของโค้ด การเปลี่ยนเป็น Binance เป็น adaptation

### C6 A Markowitz approach to managing a dynamic basket of moving-band statistical arbitrages

#### design_axes

##### asset_selection

คัดตะกร้าที่มีอยู่ในเวลาตัดสินใจ

##### workflow

ประมาณผลตอบแทน ความเสี่ยง และต้นทุนตามนิยามของงาน

##### position_management

กำหนดขนาดตะกร้า รวม holdings และจัดการตะกร้าที่เริ่มหรือสิ้นสุด

#### replication_note

ต้องตรวจนิยามความเสี่ยงและ neutrality ในต้นฉบับก่อนเขียนตาม รวมถึงเงื่อนไขข้อมูล solver และค่าใช้จ่ายที่ใช้

### C7 Signal strength, decay และต้นทุนการปรับพอร์ต

#### design_axes

##### asset_selection

สินทรัพย์และข้อมูลที่ใช้สร้าง features

##### workflow

ประเมิน strength/decay แปลงเป็น forecast และเปรียบเทียบวิธีจัดพอร์ต

##### position_management

No-trade buffer หรือ optimization ภายใต้ต้นทุนและข้อจำกัด

#### replication_note

โค้ดเขียนด้วย R และมีจุดที่ต้องตรวจความตรงกันระหว่างคำอธิบายกับนิพจน์ การเป็น market-neutral ต้องตรวจจาก constraints และ holdings ของแต่ละตัวอย่าง

### C8 Implied carry Funding และ basis

#### design_axes

##### asset_selection

เลือก dated futures หรือ perpetual ให้ตรงกลไกและข้อมูลอ้างอิง

##### workflow

นิยามตัวแปรตามเวลา และตรวจกราฟกับบัญชีรายขา

##### position_management

ขนาด hedge หลักประกัน และนโยบายจัดการรายรับสะสม

#### replication_note

จะเขียนบัญชีและการทดลองจากสมมติฐานที่ระบุ พร้อมตรวจเอกสารสัญญาปัจจุบันก่อนใช้กติกา funding หรือหลักประกันจริง

### C9 Exact synthetic: call–put–cash ที่จำลองหุ้นตามเงื่อนไขสัญญา

#### design_axes

##### asset_selection

European call และ put ของ underlying เดียวกัน strike และ expiry เดียวกัน; ระบุ dividends และอัตราดอกเบี้ย

##### workflow

เขียน payoff รายขา รวม payoff แล้วเทียบ initial value และเงื่อนไข replication

##### position_management

กำหนดจำนวน option, multiplier และเงินสดให้ตรงกัน; แยก expiry settlement จากการปิดก่อนครบกำหนด

#### replication_note

ตัวอย่างให้มูลค่าเริ่มต้นและ payoff เท่ากัน จึงไม่ได้แสดง pricing arbitrage ที่มีกำไร; ไม่มี dividends ต้นทุนหรือ default และยังไม่ได้ทำซ้ำกลยุทธ์ภายนอกกับข้อมูลตลาด

### C10 Residual momentum: หัก factor แล้วทดสอบการไปต่อ

#### design_axes

##### asset_selection

หุ้นที่มีข้อมูลสำหรับ rolling factor regression และการจัดอันดับตามเดือน; ตรวจ universe และ survivorship

##### workflow

ประมาณ factor ด้วยข้อมูลย้อนหลัง สร้างคะแนน residual momentum โดยเว้นเดือนล่าสุด แล้วตรวจผลตอบแทนอนาคตตาม horizon

##### position_management

Long กลุ่มคะแนนสูง short กลุ่มต่ำและ rebalance ตามเวลา; การจัดอันดับ residual ไม่รับประกัน factor neutrality ของ holdings

#### replication_note

ต้องเข้าถึงข้อมูลและตรวจรายละเอียด formation/holding period ต้นทุน borrow และกฎออกของ implementation ที่เลือก; ผล paper ยังไม่ได้ทำซ้ำในชุดนี้

### C11 Forecast → portfolio: Cvxportfolio และ Deep Statistical Arbitrage

#### design_axes

##### asset_selection

กำหนดสินทรัพย์ ปัจจัย features และข้อมูลที่มีจริงในเวลานั้น; ตรวจสิทธิใช้ข้อมูลต้นฉบับ

##### workflow

Cvxportfolio รับ forecasts ไป optimize; DeepStatArb เรียนรู้จากลำดับ residual แล้ว map allocation กลับไปยัง underlying assets

##### position_management

Reoptimize หรือปรับ allocation ตามกฎและต้นทุน; ตรวจ neutrality ใน holdings รวม cash/financing และเพิ่ม operational exits ที่งานไม่ได้ให้

#### replication_note

เป็นคนละวิธีและตัวอย่าง ไม่ใช่กลยุทธ์เดียวที่เราทำซ้ำ; ตัวอย่าง Cvxportfolio ปรับ hyperparameters และรายงานผลบนช่วงเดียวกัน ส่วนข้อมูล DeepStatArb มีข้อจำกัด; ต้นทุนในงานเป็นสมมติฐาน ไม่ใช่ราคาตลาดปัจจุบัน และยังไม่มีผลยืนยัน OOS จากเรา

### C12 Delta-hedged options: GAMMA methodology และ QuantLib simulation

#### design_axes

##### asset_selection

เลือก option และเครื่องมือ hedge ให้ตรง expiry, multiplier และ model; GAMMA กับ QuantLib ใช้โครงสร้างคนละแบบ

##### workflow

อ่าน methodology ของ GAMMA และจำลอง discrete delta hedging ใน QuantLib โดยติดตาม option, underlying และ cash account

##### position_management

GAMMA ปรับ delta รายวันและถือ straddle ถึงครบกำหนด; QuantLib ตัวอย่างขาย European call ภายใต้ constant-vol Black–Scholes และ hedge เป็นช่วง

#### replication_note

เป็นสองกรณีแยกกัน: methodology ของดัชนีกับตัวอย่างจำลองโมเดล ไม่ใช่ผล backtest ตลาดจริงจากเรา; ตัวอย่าง QuantLib ไม่มี execution-cost model และสมการ delta ในบทเป็น algebra เพื่ออธิบายกลไก

### C13 Optimal stopping ภายใต้ OU: objective ต้นทุน และ stop-loss

#### design_axes

##### asset_selection

ใช้ candidate ที่มีเหตุผลและข้อมูลรองรับสมมติฐาน OU ตาม horizon; การ fit ผ่านยังไม่ใช่หลักฐานกำไรหลังต้นทุน

##### workflow

เปรียบเทียบปัญหา stopping ของ Leung–Li กับ Lipton–López de Prado และตรวจนิยามเวลา ต้นทุน และขอบเขตที่แต่ละงานแก้

##### position_management

แยก model-optimal entry/liquidation จาก risk limit และ operational stop; gap และ fill จริงอาจทำให้ขาดทุนเกิน threshold

#### replication_note

ArbitrageLab เป็น implementation ของบุคคลอื่น ไม่ใช่ author code; ยังไม่ยืนยัน heat-potentials code ของ Lipton–López de Prado และยังไม่ได้ทำซ้ำตัวเลข paper หรือ market-data backtest

### C14 Copula signal: conditional CDF และการ audit กฎเข้า–ออก

#### design_axes

##### asset_selection

เลือกคู่และช่วงประมาณ marginal distributions กับ copula โดยไม่ใช้ข้อมูลอนาคต; ตรวจข้อมูลปลายหางและ ECDF endpoints

##### workflow

สำหรับ continuous copula ใช้ ∂C(u,v)/∂v = P(U≤u | V=v); ค่านี้ไม่ใช่ P(กำไรสุทธิในอนาคต>0)

##### position_management

แยก entry tails จาก normal/loss/time exits; ตรวจหน่วย regression coefficient กับ order quantities และสถานะของคำสั่งจริง

#### replication_note

ตัวอย่างตั้งสมมติฐาน mean reversion; snippet ที่ตรวจไม่มี neutral-region flat exit หรือ loss stop ให้ยกตามอัตโนมัติ และต้องตรวจการใช้ coefficient จาก log-return regression เป็นจำนวนหุ้น; อย่านำ exit ของส่วน cointegration มาอ้างว่าเป็นกฎของ copula

## ข้อกำหนดแม่แบบเพิ่มเติม

### 3. ภาพรวมของแนวคิด

#### mechanism_checks

##### payoff

รายขาจ่ายอะไร ณ เวลาใด และความเท่ากันเป็นตามสัญญาหรือเป็นสมมติฐาน

##### forecast

พยากรณ์อะไร ใช้ข้อมูลที่รู้เมื่อไร horizon เท่าไร และเป้าหมายอนาคตวัดอย่างไร

##### hedge

ลด exposure ใดด้วยจำนวนที่ถือจริง และความเสี่ยงใดยังเหลือ

##### construction

แปลง feature หรือแบบจำลองเป็น weights, units และเงินสดอย่างไร ภายใต้ข้อจำกัดใด

##### execution

ส่งคำสั่งเมื่อไร ใช้ราคาใด ใครเป็นผู้ยืนยัน fill และมีต้นทุนหรือ fill uncertainty อะไร

### 6. จากโมเดลสู่การตัดสินใจ

#### exit_checks

##### normal

เงื่อนไขปิดตามกลไก สัญญาณ forecast หรือครบ horizon; ไม่บังคับทุกวิธีให้รอ z กลับศูนย์

##### loss

วัด mark-to-liquidation P&L ด้วยราคาและต้นทุนที่ระบุ; threshold เป็น trigger ไม่ใช่การรับประกันผลขาดทุนสูงสุด

##### time

กำหนดอายุสถานะและเวลาเริ่มนับ โดยแยกเวลา signal, order และ fill

##### model

หลักฐานหรือ data/model check ใดทำให้หยุดเปิดใหม่ ลดสถานะ หรือปิด

##### capital

ข้อจำกัดทุน หลักประกัน borrow และ liquidity ใดทำให้ลดหรือเลิกถือ

##### execution

จัดการ reject, stale quotes, pending orders, partial fills และ leg imbalance อย่างไร

#### pause_resume

##### pause

บันทึกสาเหตุและสถานะพักให้คงอยู่ข้ามรอบสัญญาณ; การพักเปิดใหม่ไม่ยกเลิกการติดตามความเสี่ยงของสถานะค้าง

##### resume

ระบุผู้หรือกฎที่อนุญาตให้กลับมา เงื่อนไขตรวจที่ต้องผ่าน และตรวจ flat/pending orders ตามนโยบาย; resume ไม่ใช่คำสั่งซื้อขายอัตโนมัติ

#### fill_reconciliation

คำนวณ holdings จาก fills ที่ยืนยัน รวม open orders, cash, fees และ liabilities; order submitted หรือ cancel requested ยังไม่ใช่ fill หรือ cancel ที่สำเร็จ

### 7. กรณีศึกษาและทางเลือกเมื่อสมมติฐานไม่ผ่าน

#### evidence_levels

- อ่านแหล่งต้นฉบับ
- ตรวจ implementation ที่ระบุและบันทึกขอบเขต
- รันตัวอย่างพร้อม environment และผลตรวจ
- ทำซ้ำผลที่ระบุพร้อมข้อมูล สมมติฐาน และความแตกต่างจากต้นฉบับ

## ลำดับพัฒนาหนังสือ

### stage

1

### title

โครงหนังสือและแม่แบบ

### deliverable

สารบัญพร้อมเป้าหมายรายบท ทะเบียนกรณีศึกษา และแม่แบบจากไฟล์เดิม

### review

ตรวจความต่อเนื่องของพื้นฐาน บทหลัก และกรณีศึกษา รวมถึงฟอนต์และการจัดหน้าที่ใช้อ้างอิง

### stage

2

### title

บทนำร่อง

### deliverable

บท 3 ที่มีคำอธิบาย ภาพ ตัวเลข สมการ pseudocode แบบฝึกหัด เฉลย และหน้าทบทวน

### review

ตรวจเลขและบัญชี แยกสัญญาณจาก holdings ตรวจลำดับเวลา และอ่านหน้าที่เรนเดอร์จริงทุกหน้า

### stage

3

### title

ภาคพื้นฐานและระบบคู่สินทรัพย์

### deliverable

ฉบับ 0.5 มีบท 1–4 เต็ม บทเสริม 4B และ 7A พร้อม C1–C14; ขั้นถัดไปเขียนบท 5–8 ให้เป็นระบบคู่สินทรัพย์ที่ตรวจตามได้ครบ

### review

ตรวจกลไก ตัวแปร เวลา holdings ทุน ต้นทุน และกฎเข้า–ออก; ตัวอย่างสมมติตรวจเลขแล้ว แต่โค้ดภายนอกยังต้องแยก environment/data/run และผลทำซ้ำ

### stage

4

### title

ตะกร้า พอร์ต และวิธีวิจัย

### deliverable

บท 9–16 พร้อม C2–C6 และ C10–C14 ตามเนื้อหา พร้อมบันทึกสถานะการอ่าน ตรวจโค้ด และทำซ้ำ

### review

ตรวจ objective, constraints, neutrality, การรวมสถานะ และการแบ่งข้อมูลตามเวลา

### stage

5

### title

บทต่อยอดและรวมเล่ม

### deliverable

บท 17–20 ขยาย C8 และ C10–C14 หลังมี baseline พร้อมภาคผนวก ดัชนีตามปัญหา และไฟล์ประกอบ

### review

ตรวจการอ้างข้ามบท ความตรงกันของ code กับคำอธิบาย แหล่งอ้างอิง และคุณภาพ Word/PDF ทั้งชุด

## ข้อกำหนดบทนำร่อง

### chapter_number

3

### why_first

บทนี้เชื่อมโมเดลกับเงินจริงและตรวจความเข้าใจด้วยตัวเลขได้ จึงใช้ประเมินพร้อมกันได้ทั้งภาษา ความลึก สมการ ภาพ ตาราง และรูปแบบการทบทวน

### example_scope

ตัวอย่างสมมติของสินทรัพย์เชิงเส้นที่กำหนดราคา จำนวนหน่วย และเงินสดชัดเจน; การคิดหลักประกัน short และอนุพันธ์จริงจะขยายเมื่อเข้าสู่สัญญาที่เลือกศึกษา

### acceptance

- ผู้อ่านคำนวณ P&L ของแต่ละขาและรวมกลับเป็นการเปลี่ยน equity ได้
- ผู้อ่านอธิบายได้ว่าการเปลี่ยนค่าของโมเดลยังไม่ใช่กำไรจากราคา
- ผู้อ่านตามกระแสเงินของการปรับสถานะได้โดยไม่สร้างกำไรจากการซื้อขายเอง
- ผู้อ่านแยกต้นทุนที่บันทึกแล้วออกจากต้นทุนที่จะหักเพิ่มได้
- ผู้อ่านระบุได้ว่าสัญญาณเกิดเมื่อไรและจำนวนใดเป็นสถานะที่ถือจริงในแต่ละช่วง
- ผู้อ่านแก้โจทย์เปลี่ยนตัวเลขและเงื่อนไข พร้อมบอกสิ่งที่ยังต้องทดสอบก่อนเชื่อว่ามี edge

## แผนภาคผนวก

### title

พจนานุกรมและตารางสัญลักษณ์

### purpose

ค้นศัพท์ไทย–อังกฤษ ความหมาย และหน่วยได้รวดเร็ว

### title

พื้นฐานก่อนใช้

### purpose

ทวนคณิตศาสตร์เฉพาะที่ต้องใช้ พร้อมรหัสภาคและหัวข้อในเล่มเดิม

### title

แบบฟอร์มแกะ paper และ code

### purpose

บันทึกคำถาม สมมติฐาน ข้อมูล กฎ สิ่งที่เปลี่ยน และสถานะการตรวจอย่างสม่ำเสมอ

### title

วิธีรันไฟล์ประกอบ

### purpose

ระบุข้อมูล เวอร์ชัน dependencies ขั้นตอนรัน และผลที่ควรได้สำหรับตัวอย่างที่เผยแพร่พร้อมเล่ม

### title

ดัชนีตามปัญหา

### purpose

เริ่มค้นจากอาการ เช่น spread กลับแต่พอร์ตขาดทุน หรือเพิ่มขาแล้วต้นทุนสูง ก่อนเลือกบทที่อ่านต่อ

### title

เฉลยและเหตุผล

### purpose

ตรวจทั้งคำตอบ ขั้นตอนคิด หน่วย และกรณีที่คำตอบเปลี่ยนเมื่อสมมติฐานเปลี่ยน

## แหล่งอ่านต่อเพิ่มเติม

### chapter

18

### title

ArbitrageLab และกลุ่ม copula

### url

https://github.com/hudson-and-thames/arbitragelab

### note

เชื่อม C14; ระบุก่อนว่าจะตรวจ marginal, conditional CDF, entry/exit หรือ holdings ส่วนใด และแยก implementation จากงานต้นฉบับ

### chapter

20

### title

Deep Learning Statistical Arbitrage

### url

https://arxiv.org/abs/2106.04028

### code_url

https://github.com/gregzanotti/dlsa-public

### note

เชื่อม C11; ใช้แยก representation, forecast/allocation และ underlying holdings แล้วตรวจประโยชน์เพิ่มจาก baseline; ข้อมูลต้นฉบับมีข้อจำกัด และยังไม่ได้รัน author code ในชุดนี้

