// lessons.js - Comprehensive Thai Lesson Content for Payoff Chart Interactive App
// Each lesson defines content, chart configuration, and controls for the app controller

const LESSONS = [

  // ============================================================
  // Section 1: พื้นฐาน - อ่าน Payoff Chart ให้เป็น
  // ============================================================
  {
    id: '1.1',
    section: 1,
    sectionTitle: 'พื้นฐาน - อ่าน Payoff Chart ให้เป็น',
    title: 'Payoff Chart คืออะไร?',
    chartType: 'payoff',
    strategy: 'longCall',
    defaultParams: { strike: 100, premium: 5 },
    showLegs: false,
    legLabels: [],
    controls: [
      { type: 'range', key: 'strike', label: 'ราคาใช้สิทธิ์ (K)', min: 50, max: 200, step: 1, default: 100 },
      { type: 'range', key: 'premium', label: 'ค่า Premium', min: 1, max: 30, step: 0.5, default: 5 }
    ],
    content: `
      <p><strong>Payoff Chart</strong> คือกราฟที่แสดงกำไร/ขาดทุนของตำแหน่ง Options ณ วันหมดอายุ เป็นเครื่องมือสำคัญที่สุดสำหรับนักเทรด Options ทุกคน เพราะมันช่วยให้เห็นภาพรวมของสถานการณ์ทั้งหมดในรูปเดียว</p>

      <div class="highlight-box">
        <strong>แกน X (แนวนอน):</strong> ราคาสินทรัพย์อ้างอิง (Underlying Asset) ณ วันหมดอายุ - แสดงว่าถ้าราคาจบที่จุดต่างๆ เราจะได้กำไรหรือขาดทุนเท่าไหร่<br>
        <strong>แกน Y (แนวตั้ง):</strong> กำไร/ขาดทุน (Profit/Loss) - เหนือเส้นศูนย์คือกำไร ต่ำกว่าคือขาดทุน
      </div>

      <p>เส้นศูนย์ (Zero Line) คือเส้นแบ่งระหว่างกำไรและขาดทุน พื้นที่เหนือเส้นนี้คือโซนกำไร พื้นที่ใต้คือโซนขาดทุน จุดที่เส้นกราฟตัดกับเส้นศูนย์คือจุดคุ้มทุน (Break-even Point)</p>

      <p>ในตัวอย่างนี้ เราใช้ <strong>Long Call</strong> เป็นตัวอย่าง ลองเลื่อน slider ด้านขวาเพื่อดูว่าการเปลี่ยนค่า Strike Price และ Premium ส่งผลต่อรูปร่างของกราฟอย่างไร</p>

      <div class="key-insight">
        <strong>ทำไมต้องเข้าใจ Payoff Chart?</strong> เพราะก่อนจะเทรด Options คุณต้องรู้ว่าคุณจะได้หรือเสียเท่าไหร่ในแต่ละสถานการณ์ Payoff Chart คือ "แผนที่" ของการเทรดของคุณ
      </div>
    `
  },

  {
    id: '1.2',
    section: 1,
    sectionTitle: 'พื้นฐาน - อ่าน Payoff Chart ให้เป็น',
    title: 'องค์ประกอบสำคัญ',
    chartType: 'payoff',
    strategy: 'longCall',
    defaultParams: { strike: 100, premium: 5 },
    showLegs: false,
    legLabels: [],
    controls: [
      { type: 'range', key: 'strike', label: 'ราคาใช้สิทธิ์ (K)', min: 50, max: 200, step: 1, default: 100 },
      { type: 'range', key: 'premium', label: 'ค่า Premium', min: 1, max: 30, step: 0.5, default: 5 }
    ],
    content: `
      <p>Payoff Chart มีองค์ประกอบสำคัญหลายอย่างที่คุณต้องอ่านให้ออก มาดูทีละตัว:</p>

      <div class="highlight-box">
        <strong>Strike Price (ราคาใช้สิทธิ์):</strong> คือราคาที่คุณมีสิทธิ์ซื้อ (Call) หรือขาย (Put) สินทรัพย์อ้างอิง เป็นจุดที่กราฟ "หักศอก" เปลี่ยนทิศทาง ถ้าราคาสินทรัพย์อยู่เหนือ Strike (สำหรับ Call) = In the Money
      </div>

      <div class="highlight-box">
        <strong>Premium (ค่าพรีเมียม):</strong> คือราคาที่คุณจ่ายเพื่อซื้อ Option เปรียบเสมือน "ค่าประกัน" - เป็นต้นทุนที่จ่ายไปแล้วไม่ว่าจะเกิดอะไรขึ้น สังเกตว่ากราฟเริ่มต้นที่ -Premium เสมอ (สำหรับ Long position)
      </div>

      <div class="highlight-box">
        <strong>Break-even Point (จุดคุ้มทุน):</strong> จุดที่กำไร = 0 สำหรับ Long Call: Break-even = Strike + Premium เช่น Strike 100 + Premium 5 = ราคาต้องถึง 105 ถึงจะเริ่มมีกำไร
      </div>

      <div class="highlight-box">
        <strong>Intrinsic Value vs Time Value:</strong>
        <ul>
          <li><strong>Intrinsic Value (มูลค่าที่แท้จริง):</strong> ส่วนที่ Option อยู่ In the Money เช่น Call Strike 100, ราคาปัจจุบัน 110 → Intrinsic = 10</li>
          <li><strong>Time Value (มูลค่าเวลา):</strong> ส่วนที่เหลือ = Premium - Intrinsic Value คือ "ความหวัง" ที่ราคาจะเคลื่อนไหวก่อนหมดอายุ</li>
        </ul>
      </div>

      <p>ลองเลื่อน slider เพื่อสังเกตว่า Strike Price กำหนดจุดหักศอก ส่วน Premium กำหนดว่ากราฟอยู่ลึกแค่ไหนในโซนขาดทุน จุดคุ้มทุนจะเลื่อนตามค่าทั้งสอง</p>

      <div class="key-insight">
        <strong>จำไว้:</strong> Payoff Chart ณ วันหมดอายุนั้น Time Value = 0 เหลือแต่ Intrinsic Value เท่านั้น นี่คือเหตุผลที่กราฟเป็นเส้นตรงหักศอก ไม่ใช่เส้นโค้ง (เส้นโค้งจะเรียนในบทที่ 5)
      </div>
    `
  },


  // ============================================================
  // Section 2: Building Blocks - 4 ตำแหน่งพื้นฐาน
  // ============================================================
  {
    id: '2.1',
    section: 2,
    sectionTitle: 'Building Blocks - 4 ตำแหน่งพื้นฐาน',
    title: 'Long Call',
    chartType: 'payoff',
    strategy: 'longCall',
    defaultParams: { strike: 100, premium: 5 },
    showLegs: false,
    legLabels: [],
    controls: [
      { type: 'range', key: 'strike', label: 'ราคาใช้สิทธิ์ (K)', min: 50, max: 200, step: 1, default: 100 },
      { type: 'range', key: 'premium', label: 'ค่า Premium', min: 1, max: 30, step: 0.5, default: 5 }
    ],
    content: `
      <p><strong>Long Call = "สิทธิ์ซื้อ"</strong> — คุณจ่ายค่า Premium เพื่อได้สิทธิ์ซื้อสินทรัพย์อ้างอิงที่ราคา Strike Price ณ วันหมดอายุ</p>

      <p>กราฟมีรูปร่าง <strong>"หักศอกขึ้น"</strong> — ด้านซ้ายของ Strike เป็นเส้นแนวนอนที่ระดับ -Premium (ขาดทุนคงที่) พอผ่าน Strike กราฟเริ่มชันขึ้น 45 องศา ยิ่งราคาขึ้นไปเท่าไหร่ กำไรก็ยิ่งเพิ่มขึ้นไม่จำกัด</p>

      <div class="formula">
        Payoff = max(0, S - K) - Premium<br>
        เมื่อ S = ราคาสินทรัพย์ ณ วันหมดอายุ, K = Strike Price
      </div>

      <div class="highlight-box">
        <strong>ทำไมกราฟเป็นรูปร่างนี้?</strong>
        <ul>
          <li>ถ้า S &lt; K → Option หมดค่า คุณไม่ใช้สิทธิ์ เสียแค่ Premium ที่จ่ายไป</li>
          <li>ถ้า S = K → Option ยังไม่มีกำไร แต่เริ่ม "มีค่า"</li>
          <li>ถ้า S &gt; K → คุณใช้สิทธิ์ซื้อที่ K แล้วขายที่ S กำไร = (S - K) - Premium</li>
        </ul>
      </div>

      <ul>
        <li><strong>ขาดทุนสูงสุด (Max Loss):</strong> Premium ที่จ่ายไป — จำกัดและรู้ล่วงหน้า</li>
        <li><strong>กำไรสูงสุด (Max Profit):</strong> ไม่จำกัด — ราคาขึ้นเท่าไหร่ก็ได้กำไรเท่านั้น</li>
        <li><strong>จุดคุ้มทุน (Break-even):</strong> Strike + Premium</li>
      </ul>

      <div class="key-insight">
        <strong>Long Call เหมาะเมื่อ:</strong> คุณคิดว่าราคาจะ <strong>ขึ้นมาก</strong> และต้องการจำกัดความเสี่ยงไว้ที่ค่า Premium เปรียบเสมือนซื้อ "ตั๋วรถไฟ" — ถ้าราคาขึ้น คุณโดยสารไปด้วย ถ้าไม่ขึ้น คุณเสียแค่ค่าตั๋ว
      </div>
    `
  },

  {
    id: '2.2',
    section: 2,
    sectionTitle: 'Building Blocks - 4 ตำแหน่งพื้นฐาน',
    title: 'Short Call',
    chartType: 'payoff',
    strategy: 'shortCall',
    defaultParams: { strike: 100, premium: 5 },
    showLegs: false,
    legLabels: [],
    controls: [
      { type: 'range', key: 'strike', label: 'ราคาใช้สิทธิ์ (K)', min: 50, max: 200, step: 1, default: 100 },
      { type: 'range', key: 'premium', label: 'ค่า Premium', min: 1, max: 30, step: 0.5, default: 5 }
    ],
    content: `
      <p><strong>Short Call = "ด้านกลับของ Long Call"</strong> — คุณ <strong>ขาย</strong> สิทธิ์ซื้อให้คนอื่น แล้วรับค่า Premium เข้ากระเป๋า</p>

      <div class="key-insight">
        <strong>หลักการสำคัญที่สุด:</strong> Short = พลิก Long กลับหัว! ไม่ต้องจำรูปร่างใหม่ แค่เอา Long Call พลิกกลับด้าน (mirror ผ่านเส้นศูนย์) ก็ได้ Short Call ทันที หลักการนี้ใช้ได้กับทุก Option position
      </div>

      <p>กราฟมีรูปร่าง <strong>"หักศอกลงกลับด้าน"</strong> — ด้านซ้ายของ Strike เป็นเส้นแนวนอนที่ระดับ +Premium (กำไรคงที่) พอผ่าน Strike กราฟเริ่มดิ่งลง ยิ่งราคาขึ้นไปเท่าไหร่ ขาดทุนก็ยิ่งเพิ่มไม่จำกัด</p>

      <div class="formula">
        Payoff = Premium - max(0, S - K)<br>
        = -1 × Payoff ของ Long Call
      </div>

      <ul>
        <li><strong>ขาดทุนสูงสุด (Max Loss):</strong> ไม่จำกัด — นี่คือความเสี่ยงสูงสุดของ Short Call</li>
        <li><strong>กำไรสูงสุด (Max Profit):</strong> Premium ที่รับมา</li>
        <li><strong>จุดคุ้มทุน (Break-even):</strong> Strike + Premium (เหมือน Long Call แต่ทิศกลับกัน)</li>
      </ul>

      <div class="warning-box">
        <strong>ระวัง:</strong> Short Call มีความเสี่ยงไม่จำกัด เพราะราคาสินทรัพย์สามารถขึ้นไปได้ไม่มีขีดจำกัด แต่คุณผูกพันต้องขายที่ราคา Strike ส่วนต่างเท่าไหร่คุณต้องรับผิดชอบทั้งหมด
      </div>
    `
  },

  {
    id: '2.3',
    section: 2,
    sectionTitle: 'Building Blocks - 4 ตำแหน่งพื้นฐาน',
    title: 'Long Put',
    chartType: 'payoff',
    strategy: 'longPut',
    defaultParams: { strike: 100, premium: 5 },
    showLegs: false,
    legLabels: [],
    controls: [
      { type: 'range', key: 'strike', label: 'ราคาใช้สิทธิ์ (K)', min: 50, max: 200, step: 1, default: 100 },
      { type: 'range', key: 'premium', label: 'ค่า Premium', min: 1, max: 30, step: 0.5, default: 5 }
    ],
    content: `
      <p><strong>Long Put = "สิทธิ์ขาย"</strong> — คุณจ่ายค่า Premium เพื่อได้สิทธิ์ขายสินทรัพย์อ้างอิงที่ราคา Strike Price ณ วันหมดอายุ ใช้เมื่อคิดว่าราคาจะลง</p>

      <p>กราฟมีรูปร่าง <strong>"หักศอกซ้าย"</strong> — ด้านขวาของ Strike เป็นเส้นแนวนอนที่ระดับ -Premium (ขาดทุนคงที่) แต่ด้านซ้ายยิ่งราคาลง กราฟยิ่งชันขึ้น กำไรเพิ่มขึ้นเรื่อยๆ จนราคาถึง 0</p>

      <div class="formula">
        Payoff = max(0, K - S) - Premium<br>
        เมื่อ S = ราคาสินทรัพย์ ณ วันหมดอายุ, K = Strike Price
      </div>

      <div class="highlight-box">
        <strong>ทำไมกราฟเป็นรูปร่างนี้?</strong>
        <ul>
          <li>ถ้า S &gt; K → Option หมดค่า คุณไม่ใช้สิทธิ์ เสียแค่ Premium</li>
          <li>ถ้า S = K → Option ยังไม่มีกำไร เพิ่งเริ่มมีค่า</li>
          <li>ถ้า S &lt; K → คุณซื้อจากตลาดที่ราคา S แล้วใช้สิทธิ์ขายที่ K กำไร = (K - S) - Premium</li>
        </ul>
      </div>

      <ul>
        <li><strong>ขาดทุนสูงสุด (Max Loss):</strong> Premium ที่จ่ายไป</li>
        <li><strong>กำไรสูงสุด (Max Profit):</strong> Strike - Premium (เพราะราคาต่ำสุดคือ 0)</li>
        <li><strong>จุดคุ้มทุน (Break-even):</strong> Strike - Premium</li>
      </ul>

      <div class="key-insight">
        <strong>Long Put เหมาะเมื่อ:</strong> คุณคิดว่าราคาจะ <strong>ลงมาก</strong> หรือต้องการ <strong>ซื้อประกัน</strong> ให้กับหุ้นที่ถืออยู่ (Protective Put) เปรียบเสมือนซื้อประกันอัคคีภัย — จ่ายค่าเบี้ยไม่แพง แต่ถ้าไฟไหม้จริงได้ชดเชยเต็มที่
      </div>
    `
  },

  {
    id: '2.4',
    section: 2,
    sectionTitle: 'Building Blocks - 4 ตำแหน่งพื้นฐาน',
    title: 'Short Put',
    chartType: 'payoff',
    strategy: 'shortPut',
    defaultParams: { strike: 100, premium: 5 },
    showLegs: false,
    legLabels: [],
    controls: [
      { type: 'range', key: 'strike', label: 'ราคาใช้สิทธิ์ (K)', min: 50, max: 200, step: 1, default: 100 },
      { type: 'range', key: 'premium', label: 'ค่า Premium', min: 1, max: 30, step: 0.5, default: 5 }
    ],
    content: `
      <p><strong>Short Put = พลิก Long Put กลับหัว!</strong> — คุณ <strong>ขาย</strong> สิทธิ์ขายให้คนอื่น แล้วรับค่า Premium มา ใช้หลักการ "flip" เหมือนเดิม ไม่ต้องจำรูปร่างใหม่</p>

      <p>กราฟมีรูปร่าง "หักศอกขวา กลับด้าน" — ด้านขวาของ Strike เป็นเส้นแนวนอนที่ระดับ +Premium (กำไรคงที่) ด้านซ้ายยิ่งราคาลง กราฟยิ่งดิ่งลง ขาดทุนเพิ่มขึ้นเรื่อยๆ</p>

      <div class="formula">
        Payoff = Premium - max(0, K - S)<br>
        = -1 × Payoff ของ Long Put
      </div>

      <ul>
        <li><strong>ขาดทุนสูงสุด (Max Loss):</strong> Strike - Premium (ถ้าราคาลงไปเป็น 0)</li>
        <li><strong>กำไรสูงสุด (Max Profit):</strong> Premium ที่รับมา</li>
        <li><strong>จุดคุ้มทุน (Break-even):</strong> Strike - Premium</li>
      </ul>

      <div class="key-insight">
        <strong>หลักการ "Flip" ครบ 4 ตำแหน่ง:</strong> ตอนนี้คุณรู้จักครบทั้ง 4 ตำแหน่งพื้นฐานแล้ว — Long Call, Short Call, Long Put, Short Put จำแค่ 2 รูปทรง (Call shape + Put shape) แล้วใช้หลัก "พลิก" สำหรับ Short ไม่ต้องจำ 4 รูปแยกกัน!
      </div>

      <div class="highlight-box">
        <strong>Short Put เหมาะเมื่อ:</strong> คุณคิดว่าราคาจะ <strong>ไม่ลง</strong> หรือขึ้นเล็กน้อย และยินดีรับซื้อสินทรัพย์ที่ราคา Strike ถ้ามันลงมาจริง เปรียบเสมือนคุณเป็นบริษัทประกัน — รับเบี้ยประกันมา แต่ถ้าเกิดเหตุจริงต้องจ่ายชดเชย
      </div>
    `
  },


  {
    id: '2.5',
    section: 2,
    sectionTitle: 'Building Blocks - 4 ตำแหน่งพื้นฐาน',
    title: 'Put-Call Parity',
    chartType: 'comparison',
    strategy: null,
    defaultParams: { strike: 100, premiumCall: 8, premiumPut: 5, stockPrice: 100 },
    showLegs: false,
    legLabels: [],
    controls: [
      { type: 'range', key: 'strike', label: 'ราคาใช้สิทธิ์ (K)', min: 50, max: 200, step: 1, default: 100 },
      { type: 'range', key: 'premiumCall', label: 'Premium Call', min: 1, max: 30, step: 0.5, default: 8 },
      { type: 'range', key: 'premiumPut', label: 'Premium Put', min: 1, max: 30, step: 0.5, default: 5 }
    ],
    content: `
      <p><strong>Put-Call Parity</strong> คือความสัมพันธ์พื้นฐานที่สำคัญที่สุดในโลก Options เป็นสมการที่เชื่อมโยง Call, Put, หุ้น และพันธบัตรเข้าด้วยกัน</p>

      <div class="formula">
        C + PV(K) = P + S<br><br>
        เมื่อ C = ราคา Call, P = ราคา Put<br>
        PV(K) = มูลค่าปัจจุบันของ Strike Price<br>
        S = ราคาหุ้นปัจจุบัน
      </div>

      <p>สมการนี้บอกว่า: <strong>Long Call + เงินสด (= Strike)</strong> ให้ Payoff เหมือนกันกับ <strong>Long Put + หุ้น</strong> ทุกประการ ไม่ว่าราคาจะจบที่ไหน กราฟซ้อนทับกันพอดี!</p>

      <div class="highlight-box">
        <strong>ลองพิสูจน์ดู:</strong>
        <ul>
          <li><strong>กรณี S &gt; K:</strong> Long Call + เงินสด → ใช้สิทธิ์ซื้อที่ K ได้หุ้นมูลค่า S | Long Put + หุ้น → Put หมดค่า เหลือหุ้นมูลค่า S ✓ เท่ากัน!</li>
          <li><strong>กรณี S &lt; K:</strong> Long Call + เงินสด → Call หมดค่า เหลือเงินสด K | Long Put + หุ้น → ใช้สิทธิ์ขายหุ้นได้เงิน K ✓ เท่ากัน!</li>
        </ul>
      </div>

      <div class="key-insight">
        <strong>Call และ Put คือเหรียญเดียวกัน สองด้าน!</strong> ถ้าคุณรู้ราคาของอันหนึ่ง คุณสามารถคำนวณราคาของอีกอันได้ทันที นี่คือเหตุผลที่ตลาด Options มีความสอดคล้องกัน — ถ้าราคาไม่สอดคล้อง จะมี Arbitrage opportunity
      </div>

      <div class="warning-box">
        <strong>หมายเหตุ:</strong> Put-Call Parity ใช้ได้กับ European Options เท่านั้น (ใช้สิทธิ์ได้แค่วันหมดอายุ) สำหรับ American Options จะเป็น inequality แทน
      </div>
    `
  },

  {
    id: '2.6',
    section: 2,
    sectionTitle: 'Building Blocks - 4 ตำแหน่งพื้นฐาน',
    title: 'Synthetic Positions',
    chartType: 'comparison',
    strategy: null,
    defaultParams: { strike: 100, premiumCall: 8, premiumPut: 5 },
    showLegs: false,
    legLabels: [],
    controls: [
      { type: 'range', key: 'strike', label: 'ราคาใช้สิทธิ์ (K)', min: 50, max: 200, step: 1, default: 100 },
      { type: 'range', key: 'premiumCall', label: 'Premium Call', min: 1, max: 30, step: 0.5, default: 8 },
      { type: 'range', key: 'premiumPut', label: 'Premium Put', min: 1, max: 30, step: 0.5, default: 5 }
    ],
    content: `
      <p><strong>Synthetic Positions</strong> คือการ "สังเคราะห์" ตำแหน่งหนึ่งจากส่วนผสมของตำแหน่งอื่นๆ โดยอาศัยหลัก Put-Call Parity</p>

      <p>จาก C + PV(K) = P + S เราสามารถจัดรูปสมการใหม่ได้:</p>

      <div class="formula">
        Synthetic Long Stock = Long Call + Short Put (Strike เดียวกัน)<br>
        S = C - P + PV(K)<br><br>
        Synthetic Long Call = Long Stock + Long Put<br>
        C = S + P - PV(K)<br><br>
        Synthetic Long Put = Long Call + Short Stock<br>
        P = C - S + PV(K)
      </div>

      <p>ลองดูกราฟด้านขวา — เส้น Payoff ของ <strong>Long Call + Short Put</strong> (Strike เดียวกัน) ซ้อนทับกับเส้นหุ้นพอดี! นี่คือ Synthetic Long Stock</p>

      <div class="highlight-box">
        <strong>ทำไมต้องใช้ Synthetic?</strong>
        <ul>
          <li>ต้นทุนต่ำกว่า — ใช้เงินน้อยกว่าซื้อหุ้นจริง (leverage)</li>
          <li>ใช้เมื่อยืมหุ้นไม่ได้ — สร้าง Synthetic Short Stock แทนการ Short ขายจริง</li>
          <li>Arbitrage — ถ้าราคา Synthetic ≠ ราคาจริง มีโอกาสทำกำไรไร้ความเสี่ยง</li>
        </ul>
      </div>

      <div class="key-insight">
        <strong>ทุกตำแหน่งสามารถ "ผลิต" จากส่วนผสมอื่นได้!</strong> เหมือนทำอาหาร — ถ้าไม่มีวัตถุดิบ A คุณอาจใช้ B + C ทดแทนได้ นี่คือพลังของการเข้าใจ Put-Call Parity อย่างลึกซึ้ง
      </div>
    `
  },


  // ============================================================
  // Section 3: หลักการรวม
  // ============================================================
  {
    id: '3.1',
    section: 3,
    sectionTitle: 'หลักการรวม',
    title: 'หลักการบวก Payoff',
    chartType: 'payoff',
    strategy: 'bullCallSpread',
    defaultParams: { strike1: 95, premium1: 8, strike2: 110, premium2: 3 },
    showLegs: true,
    legLabels: ['Long Call K₁', 'Short Call K₂'],
    controls: [
      { type: 'range', key: 'strike1', label: 'Strike K₁ (Long Call)', min: 50, max: 200, step: 1, default: 95 },
      { type: 'range', key: 'premium1', label: 'Premium (Long Call)', min: 1, max: 30, step: 0.5, default: 8 },
      { type: 'range', key: 'strike2', label: 'Strike K₂ (Short Call)', min: 50, max: 200, step: 1, default: 110 },
      { type: 'range', key: 'premium2', label: 'Premium (Short Call)', min: 1, max: 30, step: 0.5, default: 3 }
    ],
    content: `
      <p><strong>นี่คือหลักการที่สำคัญที่สุดในบทเรียนทั้งหมด!</strong></p>

      <div class="key-insight">
        <strong>หลักการบวก Payoff:</strong> Payoff ของกลยุทธ์หลายขา = ผลรวมของ Payoff แต่ละขา ณ ทุกจุดราคา<br><br>
        คุณไม่ต้องจำรูปร่างกลยุทธ์ใดเลย — แค่เข้าใจหลักการนี้ คุณสามารถ <strong>สร้าง</strong> กลยุทธ์ใดก็ได้ด้วยตัวเอง!
      </div>

      <p>ดูกราฟด้านขวา — เส้นประ (dashed) คือ Payoff ของแต่ละขา: Long Call K₁ (สีฟ้า) และ Short Call K₂ (สีแดง) เส้นทึบ (solid) คือ Payoff รวม ซึ่งได้จากการ <strong>บวก</strong> ค่าของเส้นประสองเส้นที่ทุกจุดราคา</p>

      <div class="highlight-box">
        <strong>ลองทำตาม:</strong>
        <ol>
          <li>เลือกจุดราคาสักจุด เช่น S = 80</li>
          <li>อ่านค่า Payoff ของ Long Call K₁ ที่จุดนั้น (= -8)</li>
          <li>อ่านค่า Payoff ของ Short Call K₂ ที่จุดนั้น (= +3)</li>
          <li>บวกกัน: -8 + 3 = -5</li>
          <li>ตรวจสอบว่าเส้นทึบอยู่ที่ -5 จริงมั้ย? ✓</li>
        </ol>
      </div>

      <p>ลองทำซ้ำกับจุดราคาอื่นๆ แล้วคุณจะเห็นว่ามันใช้ได้ทุกจุด! นี่คือเหตุผลที่กลยุทธ์ Bull Call Spread มีรูปร่าง "บันได" — เป็นผลจากการรวมเส้น "หักศอกขึ้น" กับเส้น "หักศอกลง"</p>

      <div class="warning-box">
        <strong>สิ่งที่ต้องจำ:</strong> ไม่มีเวทมนตร์ใดในกลยุทธ์ Options ทุกอย่างคือ "การบวกเส้นตรง" ถ้าเข้าใจหลักการนี้ คุณจะไม่มีวันต้อง "ท่องจำ" รูปร่างกลยุทธ์อีกต่อไป
      </div>
    `
  },

  {
    id: '3.2',
    section: 3,
    sectionTitle: 'หลักการรวม',
    title: 'ห้องทดลอง: ลองผสมเอง',
    chartType: 'sandbox',
    strategy: null,
    defaultParams: {},
    showLegs: true,
    legLabels: [],
    controls: [],
    content: `
      <p><strong>ถึงเวลาลงมือทำเอง!</strong> ใช้ตัวสร้างขาด้านล่างเพื่อเพิ่ม Option legs 2-4 ขา แล้วดูผลลัพธ์ในกราฟ</p>

      <div class="highlight-box">
        <strong>วิธีใช้:</strong>
        <ul>
          <li>เลือก <strong>ประเภท</strong>: Call หรือ Put</li>
          <li>เลือก <strong>ทิศทาง</strong>: Long (ซื้อ) หรือ Short (ขาย)</li>
          <li>ตั้ง <strong>Strike Price</strong> และ <strong>Premium</strong></li>
          <li>กดเพิ่มขา แล้วดูกราฟเปลี่ยนแปลงทันที</li>
        </ul>
      </div>

      <p>เส้นประแต่ละสีคือแต่ละขา เส้นทึบคือ Payoff รวม สังเกตว่ารูปร่างต่างๆ เกิดจากการรวมของ Building Blocks ที่คุณเรียนมาในบทที่ 2</p>

      <div class="key-insight">
        <strong>ลองสร้างรูปร่างเหล่านี้ดู:</strong>
        <ul>
          <li>รูป V (กำไรเมื่อราคาเคลื่อนไหวมาก)</li>
          <li>รูป V กลับหัว (กำไรเมื่อราคานิ่ง)</li>
          <li>รูปบันไดขึ้น (กำไรจำกัด ขาดทุนจำกัด ทิศขาขึ้น)</li>
          <li>รูปเต็นท์แหลม (กำไรสูงสุดที่จุดเดียว)</li>
        </ul>
      </div>

      <p><strong>อย่าเพิ่งดูชื่อกลยุทธ์!</strong> จุดประสงค์ของห้องทดลองนี้คือให้คุณ "ค้นพบ" รูปร่างด้วยตัวเอง แล้วค่อยไปเรียนรู้ชื่อในบทถัดไป</p>
    `
  },

  {
    id: '3.3',
    section: 3,
    sectionTitle: 'หลักการรวม',
    title: 'Challenge: สร้างรูปร่างเป้าหมาย',
    chartType: 'sandbox',
    strategy: null,
    defaultParams: {},
    showLegs: true,
    legLabels: [],
    controls: [],
    content: `
      <p><strong>ทดสอบความเข้าใจ!</strong> ลองสร้าง Payoff ให้ตรงกับเป้าหมายที่กำหนด</p>

      <div class="highlight-box">
        <strong>Challenge 1:</strong> สร้าง Payoff ที่ "กำไรจำกัด ขาดทุนจำกัด" เมื่อราคาขึ้น<br>
        <em>คำใบ้: ใช้ Call 2 ตัว ต่าง Strike</em>
      </div>

      <div class="highlight-box">
        <strong>Challenge 2:</strong> สร้าง Payoff ที่ "กำไรเมื่อราคาอยู่นิ่ง" (ไม่เคลื่อนไหวมาก)<br>
        <em>คำใบ้: ถ้า Long = กำไรเมื่อเคลื่อนไหว แล้ว Short ล่ะ?</em>
      </div>

      <div class="highlight-box">
        <strong>Challenge 3:</strong> สร้าง Payoff ที่ "กำไรสูงสุดที่จุดราคาเดียว" (รูปเต็นท์)<br>
        <em>คำใบ้: ต้องใช้อย่างน้อย 3 ขา</em>
      </div>

      <div class="key-insight">
        <strong>ทำไมต้องฝึกแบบนี้?</strong> ในการเทรดจริง คุณมักเริ่มจาก "มุมมอง" แล้วค่อยหากลยุทธ์ที่ตรง — ไม่ใช่เริ่มจากชื่อกลยุทธ์แล้วค่อยหาจังหวะใช้ การฝึกสร้าง Payoff จากเป้าหมายจึงเป็นทักษะที่สำคัญกว่าการท่องชื่อ
      </div>
    `
  },


  // ============================================================
  // Section 4: Named Strategies - "พจนานุกรม" ที่ต้องรู้
  // ============================================================
  {
    id: '4.1',
    section: 4,
    sectionTitle: 'Named Strategies - "พจนานุกรม" ที่ต้องรู้',
    title: 'Bull Call Spread',
    chartType: 'payoff',
    strategy: 'bullCallSpread',
    defaultParams: { strike1: 95, premium1: 8, strike2: 110, premium2: 3 },
    showLegs: true,
    legLabels: ['Long Call K₁', 'Short Call K₂'],
    controls: [
      { type: 'range', key: 'strike1', label: 'Strike K₁ (Long Call)', min: 50, max: 200, step: 1, default: 95 },
      { type: 'range', key: 'premium1', label: 'Premium (Long Call)', min: 1, max: 30, step: 0.5, default: 8 },
      { type: 'range', key: 'strike2', label: 'Strike K₂ (Short Call)', min: 50, max: 200, step: 1, default: 110 },
      { type: 'range', key: 'premium2', label: 'Premium (Short Call)', min: 1, max: 30, step: 0.5, default: 3 }
    ],
    content: `
      <p><strong>Bull Call Spread</strong> = Long Call (Strike ต่ำ) + Short Call (Strike สูง) — "มุมมองขาขึ้นแบบจำกัดความเสี่ยง"</p>

      <div class="highlight-box">
        <strong>ลองสร้างเองก่อน!</strong> ถ้าคุณทำ Challenge ในบท 3.3 มาแล้ว คุณน่าจะเคยสร้างรูปร่างนี้ได้แล้ว — "กำไรจำกัด ขาดทุนจำกัด เมื่อราคาขึ้น" ก็คือ Bull Call Spread นั่นเอง!
      </div>

      <p>กราฟมีรูปร่าง <strong>"บันไดขึ้น"</strong>:</p>
      <ul>
        <li>ถ้า S &lt; K₁ → ทั้งสอง Call หมดค่า ขาดทุน = Net Premium จ่ายไป</li>
        <li>ถ้า K₁ &lt; S &lt; K₂ → Long Call มีค่า, Short Call ยังไม่มีค่า กำไรเพิ่มขึ้นตามราคา</li>
        <li>ถ้า S &gt; K₂ → ทั้งสอง Call มีค่า แต่หักลบกัน กำไรคงที่</li>
      </ul>

      <div class="formula">
        Net Premium = Premium₁ - Premium₂ (จ่ายสุทธิ)<br>
        Max Profit = (K₂ - K₁) - Net Premium<br>
        Max Loss = Net Premium<br>
        Break-even = K₁ + Net Premium
      </div>

      <div class="key-insight">
        <strong>เมื่อไหร่ใช้ Bull Call Spread แทน Long Call?</strong> เมื่อคุณคิดว่าราคาจะขึ้น <strong>แต่ไม่มาก</strong> — การขาย Call ที่ Strike สูงช่วยลดต้นทุน (Net Premium ต่ำกว่า Long Call เปล่าๆ) แลกกับการจำกัดกำไรสูงสุด
      </div>
    `
  },

  {
    id: '4.2',
    section: 4,
    sectionTitle: 'Named Strategies - "พจนานุกรม" ที่ต้องรู้',
    title: 'Bear Put Spread',
    chartType: 'payoff',
    strategy: 'bearPutSpread',
    defaultParams: { strike1: 90, premium1: 3, strike2: 105, premium2: 8 },
    showLegs: true,
    legLabels: ['Short Put K₁', 'Long Put K₂'],
    controls: [
      { type: 'range', key: 'strike1', label: 'Strike K₁ (Short Put)', min: 50, max: 200, step: 1, default: 90 },
      { type: 'range', key: 'premium1', label: 'Premium (Short Put)', min: 1, max: 30, step: 0.5, default: 3 },
      { type: 'range', key: 'strike2', label: 'Strike K₂ (Long Put)', min: 50, max: 200, step: 1, default: 105 },
      { type: 'range', key: 'premium2', label: 'Premium (Long Put)', min: 1, max: 30, step: 0.5, default: 8 }
    ],
    content: `
      <p><strong>Bear Put Spread</strong> = Long Put (Strike สูง) + Short Put (Strike ต่ำ) — "มุมมองขาลงแบบจำกัดความเสี่ยง"</p>

      <p>เป็นกลยุทธ์ "กระจกสะท้อน" ของ Bull Call Spread — ทุกอย่างกลับทิศ ใช้เมื่อคิดว่าราคาจะลงแบบไม่รุนแรง</p>

      <p>กราฟมีรูปร่าง <strong>"บันไดลง"</strong>:</p>
      <ul>
        <li>ถ้า S &gt; K₂ → ทั้งสอง Put หมดค่า ขาดทุน = Net Premium จ่ายไป</li>
        <li>ถ้า K₁ &lt; S &lt; K₂ → Long Put มีค่า, Short Put ยังไม่มีค่า กำไรเพิ่มขึ้นเมื่อราคาลง</li>
        <li>ถ้า S &lt; K₁ → ทั้งสอง Put มีค่า แต่หักลบกัน กำไรคงที่</li>
      </ul>

      <div class="formula">
        Net Premium = Premium₂ - Premium₁ (จ่ายสุทธิ)<br>
        Max Profit = (K₂ - K₁) - Net Premium<br>
        Max Loss = Net Premium<br>
        Break-even = K₂ - Net Premium
      </div>

      <div class="key-insight">
        <strong>สังเกต:</strong> Bull Call Spread และ Bear Put Spread มีโครงสร้างเหมือนกัน — ซื้อ Option ที่แพงกว่า + ขาย Option ที่ถูกกว่า (ต่าง Strike เดียวกัน) แค่ใช้ Call สำหรับขาขึ้น ใช้ Put สำหรับขาลง
      </div>
    `
  },

  {
    id: '4.3',
    section: 4,
    sectionTitle: 'Named Strategies - "พจนานุกรม" ที่ต้องรู้',
    title: 'Long Straddle',
    chartType: 'payoff',
    strategy: 'longStraddle',
    defaultParams: { strike: 100, premiumCall: 5, premiumPut: 5 },
    showLegs: true,
    legLabels: ['Long Call', 'Long Put'],
    controls: [
      { type: 'range', key: 'strike', label: 'ราคาใช้สิทธิ์ (K)', min: 50, max: 200, step: 1, default: 100 },
      { type: 'range', key: 'premiumCall', label: 'Premium Call', min: 1, max: 30, step: 0.5, default: 5 },
      { type: 'range', key: 'premiumPut', label: 'Premium Put', min: 1, max: 30, step: 0.5, default: 5 }
    ],
    content: `
      <p><strong>Long Straddle</strong> = Long Call + Long Put (Strike เดียวกัน) — "เดิมพันว่าราคาจะผันผวนมาก ไม่ว่าจะขึ้นหรือลง"</p>

      <p>กราฟมีรูปร่าง <strong>"V"</strong> คลาสสิก — จุดต่ำสุดอยู่ที่ Strike Price (ขาดทุนมากสุด = ค่า Premium สองตัวรวมกัน) ยิ่งราคาเคลื่อนไหวออกจาก Strike มากเท่าไหร่ ไม่ว่าจะทิศไหน ก็ยิ่งกำไร</p>

      <div class="formula">
        Payoff = max(0, S - K) + max(0, K - S) - PremiumCall - PremiumPut<br>
        Max Loss = PremiumCall + PremiumPut (ณ จุด S = K)<br>
        Break-even บน = K + PremiumCall + PremiumPut<br>
        Break-even ล่าง = K - PremiumCall - PremiumPut
      </div>

      <div class="highlight-box">
        <strong>ทำไมเป็นรูป V?</strong> ลองใช้หลักการบวก Payoff:
        <ul>
          <li>ด้านซ้ายของ Strike: Long Call = -PremiumCall (แบน), Long Put = เพิ่มขึ้น → รวม = เพิ่มขึ้น - PremiumCall</li>
          <li>ด้านขวาของ Strike: Long Call = เพิ่มขึ้น, Long Put = -PremiumPut (แบน) → รวม = เพิ่มขึ้น - PremiumPut</li>
          <li>ที่ Strike: ทั้งคู่ = 0 → รวม = -(PremiumCall + PremiumPut) = จุดต่ำสุด</li>
        </ul>
      </div>

      <div class="key-insight">
        <strong>Long Straddle เหมาะเมื่อ:</strong> คุณคาดว่าจะมีเหตุการณ์สำคัญ (ประกาศผลประกอบการ, ผลเลือกตั้ง, ฯลฯ) ที่จะทำให้ราคาเคลื่อนไหวมาก แต่ไม่รู้ว่าจะไปทางไหน <strong>ข้อเสีย:</strong> ต้องจ่าย Premium ทั้ง Call และ Put — ต้นทุนสูง ราคาต้องเคลื่อนไหวมากพอถึงจะคุ้มทุน
      </div>
    `
  },

  {
    id: '4.4',
    section: 4,
    sectionTitle: 'Named Strategies - "พจนานุกรม" ที่ต้องรู้',
    title: 'Long Strangle',
    chartType: 'payoff',
    strategy: 'longStrangle',
    defaultParams: { strike1: 90, strike2: 110, premiumCall: 3, premiumPut: 3 },
    showLegs: true,
    legLabels: ['Long Put K₁', 'Long Call K₂'],
    controls: [
      { type: 'range', key: 'strike1', label: 'Strike K₁ (Long Put)', min: 50, max: 200, step: 1, default: 90 },
      { type: 'range', key: 'strike2', label: 'Strike K₂ (Long Call)', min: 50, max: 200, step: 1, default: 110 },
      { type: 'range', key: 'premiumCall', label: 'Premium Call', min: 1, max: 30, step: 0.5, default: 3 },
      { type: 'range', key: 'premiumPut', label: 'Premium Put', min: 1, max: 30, step: 0.5, default: 3 }
    ],
    content: `
      <p><strong>Long Strangle</strong> = Long Put (Strike ต่ำ) + Long Call (Strike สูง) — เหมือน Straddle แต่ใช้ Strike ต่างกัน ถูกกว่า แต่ต้องการการเคลื่อนไหวมากกว่า</p>

      <p>กราฟมีรูปร่าง <strong>"V กว้าง"</strong> หรือ "U ก้นแบน" — มีโซนขาดทุนคงที่ระหว่าง Strike ทั้งสอง แล้วกำไรเพิ่มขึ้นเมื่อราคาออกนอก Strike</p>

      <div class="formula">
        Max Loss = PremiumCall + PremiumPut (เมื่อ K₁ ≤ S ≤ K₂)<br>
        Break-even บน = K₂ + PremiumCall + PremiumPut<br>
        Break-even ล่าง = K₁ - PremiumCall - PremiumPut
      </div>

      <div class="highlight-box">
        <strong>เปรียบเทียบ Straddle vs Strangle:</strong>
        <table style="width:100%; border-collapse: collapse;">
          <tr><th style="text-align:left; padding:4px; border-bottom:1px solid #ccc;"></th><th style="padding:4px; border-bottom:1px solid #ccc;">Straddle</th><th style="padding:4px; border-bottom:1px solid #ccc;">Strangle</th></tr>
          <tr><td style="padding:4px;">Strike</td><td style="padding:4px;">เดียวกัน</td><td style="padding:4px;">ต่างกัน (OTM ทั้งคู่)</td></tr>
          <tr><td style="padding:4px;">ต้นทุน</td><td style="padding:4px;">สูงกว่า</td><td style="padding:4px;">ต่ำกว่า</td></tr>
          <tr><td style="padding:4px;">ราคาต้องเคลื่อนไหว</td><td style="padding:4px;">น้อยกว่า</td><td style="padding:4px;">มากกว่า</td></tr>
          <tr><td style="padding:4px;">รูปร่าง</td><td style="padding:4px;">V แหลม</td><td style="padding:4px;">V กว้าง / U</td></tr>
        </table>
      </div>

      <div class="key-insight">
        <strong>เลือกอันไหนดี?</strong> Strangle ถูกกว่า (เพราะซื้อ OTM Options) แต่ต้องการ "เหตุการณ์ใหญ่" กว่าถึงจะคุ้มทุน ถ้ามั่นใจว่าจะมีความผันผวนสูงมาก ใช้ Straddle ถ้าอยากจ่ายน้อยและรับความเสี่ยงว่าราคาอาจไม่เคลื่อนไหวพอ ใช้ Strangle
      </div>
    `
  },


  {
    id: '4.5',
    section: 4,
    sectionTitle: 'Named Strategies - "พจนานุกรม" ที่ต้องรู้',
    title: 'Iron Condor',
    chartType: 'payoff',
    strategy: 'ironCondor',
    defaultParams: { strike1: 80, premium1: 1, strike2: 90, premium2: 3, strike3: 110, premium3: 3, strike4: 120, premium4: 1 },
    showLegs: true,
    legLabels: ['Long Put K₁', 'Short Put K₂', 'Short Call K₃', 'Long Call K₄'],
    controls: [
      { type: 'range', key: 'strike1', label: 'Strike K₁ (Long Put)', min: 50, max: 200, step: 1, default: 80 },
      { type: 'range', key: 'premium1', label: 'Premium K₁', min: 1, max: 30, step: 0.5, default: 1 },
      { type: 'range', key: 'strike2', label: 'Strike K₂ (Short Put)', min: 50, max: 200, step: 1, default: 90 },
      { type: 'range', key: 'premium2', label: 'Premium K₂', min: 1, max: 30, step: 0.5, default: 3 },
      { type: 'range', key: 'strike3', label: 'Strike K₃ (Short Call)', min: 50, max: 200, step: 1, default: 110 },
      { type: 'range', key: 'premium3', label: 'Premium K₃', min: 1, max: 30, step: 0.5, default: 3 },
      { type: 'range', key: 'strike4', label: 'Strike K₄ (Long Call)', min: 50, max: 200, step: 1, default: 120 },
      { type: 'range', key: 'premium4', label: 'Premium K₄', min: 1, max: 30, step: 0.5, default: 1 }
    ],
    content: `
      <p><strong>Iron Condor</strong> = 4 ขา — "เดิมพันว่าราคาจะนิ่ง อยู่ในกรอบ" เป็นกลยุทธ์ยอดนิยมสำหรับตลาด Sideway</p>

      <p>ประกอบด้วย 2 Spread ย่อย:</p>
      <ul>
        <li><strong>Bull Put Spread</strong> (ขาล่าง): Long Put K₁ + Short Put K₂</li>
        <li><strong>Bear Call Spread</strong> (ขาบน): Short Call K₃ + Long Call K₄</li>
      </ul>

      <p>กราฟมีรูปร่าง <strong>"ที่ราบสูงตรงกลาง ทิ้งดิ่งสองข้าง"</strong> — กำไรคงที่เมื่อราคาอยู่ระหว่าง K₂ ถึง K₃ ขาดทุนจำกัดเมื่อราคาออกนอกกรอบ</p>

      <div class="formula">
        Net Credit = (Premium₂ - Premium₁) + (Premium₃ - Premium₄)<br>
        Max Profit = Net Credit (เมื่อ K₂ ≤ S ≤ K₃)<br>
        Max Loss = (K₂ - K₁) - Net Credit หรือ (K₄ - K₃) - Net Credit<br>
        Break-even บน = K₃ + Net Credit<br>
        Break-even ล่าง = K₂ - Net Credit
      </div>

      <div class="highlight-box">
        <strong>ทำไมต้อง 4 ขา?</strong>
        <ul>
          <li>Short Put + Short Call = รับ Premium สูง แต่ความเสี่ยงไม่จำกัด (Short Strangle)</li>
          <li>Long Put (ข้างนอก) + Long Call (ข้างนอก) = "ปีก" ที่จำกัดความเสี่ยง</li>
          <li>รวมกันได้กลยุทธ์ที่ <strong>ทั้งกำไรและขาดทุนจำกัด</strong></li>
        </ul>
      </div>

      <div class="key-insight">
        <strong>Iron Condor เหมาะเมื่อ:</strong> คุณคิดว่าราคาจะไม่เคลื่อนไหวมาก (Low Volatility) และต้องการเก็บ Premium เป็นรายได้ประจำ เป็นกลยุทธ์ที่มีโอกาสชนะสูง (ราคาอยู่ในกรอบบ่อยกว่าออกนอกกรอบ) แต่เมื่อเสียจะเสียมากกว่ากำไรแต่ละครั้ง
      </div>
    `
  },

  {
    id: '4.6',
    section: 4,
    sectionTitle: 'Named Strategies - "พจนานุกรม" ที่ต้องรู้',
    title: 'Butterfly Spread',
    chartType: 'payoff',
    strategy: 'butterflySpread',
    defaultParams: { strike1: 90, premium1: 12, strike2: 100, premium2: 6, strike3: 110, premium3: 2 },
    showLegs: true,
    legLabels: ['Long Call K₁', 'Short 2x Call K₂', 'Long Call K₃'],
    controls: [
      { type: 'range', key: 'strike1', label: 'Strike K₁ (Long Call)', min: 50, max: 200, step: 1, default: 90 },
      { type: 'range', key: 'premium1', label: 'Premium K₁', min: 1, max: 30, step: 0.5, default: 12 },
      { type: 'range', key: 'strike2', label: 'Strike K₂ (Short 2x Call)', min: 50, max: 200, step: 1, default: 100 },
      { type: 'range', key: 'premium2', label: 'Premium K₂ (ต่อ contract)', min: 1, max: 30, step: 0.5, default: 6 },
      { type: 'range', key: 'strike3', label: 'Strike K₃ (Long Call)', min: 50, max: 200, step: 1, default: 110 },
      { type: 'range', key: 'premium3', label: 'Premium K₃', min: 1, max: 30, step: 0.5, default: 2 }
    ],
    content: `
      <p><strong>Butterfly Spread</strong> = Long 1 Call K₁ + Short 2 Call K₂ + Long 1 Call K₃ — "เดิมพันว่าราคาจะอยู่ตรงจุด K₂ พอดี"</p>

      <p>กราฟมีรูปร่าง <strong>"เต็นท์"</strong> หรือ "ผีเสื้อ" (จึงเป็นที่มาของชื่อ) — กำไรสูงสุดที่จุด K₂ พอดี แล้วค่อยๆ ลดลงทั้งสองด้าน จนขาดทุนคงที่เมื่อราคาออกนอก K₁ หรือ K₃</p>

      <div class="formula">
        Net Debit = Premium₁ - 2 × Premium₂ + Premium₃<br>
        Max Profit = (K₂ - K₁) - Net Debit (ณ จุด S = K₂)<br>
        Max Loss = Net Debit<br>
        Break-even บน = K₃ - Net Debit<br>
        Break-even ล่าง = K₁ + Net Debit
      </div>

      <div class="highlight-box">
        <strong>ทำไมเป็นรูปเต็นท์?</strong> ลองใช้หลักการบวก Payoff:
        <ul>
          <li>Long Call K₁ = หักศอกขึ้นที่ K₁ (ชัน +1)</li>
          <li>Short 2x Call K₂ = หักศอกลงที่ K₂ (ชัน -2)</li>
          <li>Long Call K₃ = หักศอกขึ้นที่ K₃ (ชัน +1)</li>
          <li>รวม: +1 - 2 + 1 = 0 ที่ปลายทั้งสองด้าน → กลับมาแบน!</li>
        </ul>
      </div>

      <div class="key-insight">
        <strong>Butterfly Spread เหมาะเมื่อ:</strong> คุณมั่นใจมากว่าราคาจะจบที่จุดใดจุดหนึ่ง (เช่น ใกล้ราคาปัจจุบัน) ต้นทุนต่ำมาก (Net Debit น้อย) แต่กำไรสูงสุดจะได้ก็ต่อเมื่อราคาจบที่ K₂ พอดี — เป็นกลยุทธ์ที่ต้องมีความแม่นยำสูง
      </div>
    `
  },


  // ============================================================
  // Section 5: Greeks
  // ============================================================
  {
    id: '5.1',
    section: 5,
    sectionTitle: 'Greeks',
    title: 'Payoff ก่อน vs หลังหมดอายุ',
    chartType: 'timeCurve',
    strategy: null,
    defaultParams: { strike: 100, premium: 5, type: 'call', position: 'long', sigma: 0.25 },
    showLegs: false,
    legLabels: [],
    controls: [
      { type: 'range', key: 'strike', label: 'ราคาใช้สิทธิ์ (K)', min: 50, max: 200, step: 1, default: 100 },
      { type: 'range', key: 'premium', label: 'ค่า Premium', min: 1, max: 30, step: 0.5, default: 5 },
      { type: 'range', key: 'daysToExpiry', label: 'วันถึงหมดอายุ', min: 1, max: 180, step: 1, default: 30 },
      { type: 'range', key: 'sigma', label: 'ความผันผวน (σ) %', min: 5, max: 80, step: 1, default: 25 }
    ],
    content: `
      <p>จนถึงตอนนี้ เราดูแต่ Payoff <strong>ณ วันหมดอายุ</strong> เท่านั้น — เส้นตรงหักศอก แต่ในความเป็นจริง Options มีมูลค่าก่อนหมดอายุด้วย และเส้น Payoff ก่อนหมดอายุจะเป็น <strong>เส้นโค้ง</strong> ไม่ใช่เส้นตรง!</p>

      <div class="highlight-box">
        <strong>เส้นโค้ง vs เส้นตรง:</strong>
        <ul>
          <li><strong>ณ วันหมดอายุ:</strong> เส้นตรงหักศอก (มีแค่ Intrinsic Value)</li>
          <li><strong>ก่อนหมดอายุ:</strong> เส้นโค้งมน (มี Intrinsic + Time Value)</li>
          <li>ยิ่งเหลือเวลามาก เส้นโค้งยิ่งอยู่สูงกว่าเส้นหมดอายุ (เพราะ Time Value สูง)</li>
        </ul>
      </div>

      <p>ลองเลื่อน slider <strong>"วันถึงหมดอายุ"</strong> — ดูว่าเส้นโค้งค่อยๆ แบนลงจนกลายเป็นเส้นตรงหักศอกเมื่อเวลาหมด นี่คือกระบวนการ <strong>Time Decay</strong> ที่เกิดขึ้นทุกวัน</p>

      <div class="key-insight">
        <strong>Black-Scholes Model:</strong> เส้นโค้งนี้คำนวณจากสูตร Black-Scholes — สูตรที่ปฏิวัติวงการการเงินโลก สูตรนี้รวม 5 ตัวแปร: ราคาสินทรัพย์, Strike, เวลา, ความผันผวน (Volatility), และอัตราดอกเบี้ย เราจะเรียนรู้ "ความไว" ต่อตัวแปรเหล่านี้ในบทถัดไป — นั่นคือ Greeks!
      </div>

      <div class="warning-box">
        <strong>สิ่งสำคัญ:</strong> เส้น Payoff ณ วันหมดอายุคือ "ปลายทาง" เท่านั้น ระหว่างทางก่อนหมดอายุ คุณสามารถขาย Option ได้ตลอดเวลา และราคาจะอยู่บนเส้นโค้ง ไม่ใช่เส้นตรง
      </div>
    `
  },

  {
    id: '5.2',
    section: 5,
    sectionTitle: 'Greeks',
    title: 'Delta (Δ)',
    chartType: 'greeks',
    strategy: null,
    defaultParams: { strike: 100, premium: 5, daysToExpiry: 30, sigma: 0.25 },
    showLegs: false,
    legLabels: [],
    controls: [
      { type: 'range', key: 'strike', label: 'ราคาใช้สิทธิ์ (K)', min: 50, max: 200, step: 1, default: 100 },
      { type: 'range', key: 'daysToExpiry', label: 'วันถึงหมดอายุ', min: 1, max: 180, step: 1, default: 30 },
      { type: 'range', key: 'sigma', label: 'ความผันผวน (σ) %', min: 5, max: 80, step: 1, default: 25 }
    ],
    content: `
      <p><strong>Delta (Δ)</strong> คือ "ความชัน" ของเส้น Payoff — วัดว่ามูลค่า Option เปลี่ยนไปเท่าไหร่ เมื่อราคาสินทรัพย์อ้างอิงเปลี่ยน ฿1</p>

      <div class="formula">
        Δ = ∂V / ∂S ≈ การเปลี่ยนแปลงของราคา Option / การเปลี่ยนแปลงของราคาสินทรัพย์
      </div>

      <div class="highlight-box">
        <strong>ค่า Delta ของแต่ละตำแหน่ง:</strong>
        <ul>
          <li><strong>Long Call:</strong> 0 ถึง +1 (เคลื่อนไหวไปทางเดียวกับสินทรัพย์)</li>
          <li><strong>Long Put:</strong> -1 ถึง 0 (เคลื่อนไหวสวนทางกับสินทรัพย์)</li>
          <li><strong>ATM Call ≈ +0.5:</strong> สินทรัพย์ขึ้น ฿1 → Call ขึ้นประมาณ ฿0.50</li>
          <li><strong>Deep ITM Call ≈ +1.0:</strong> เคลื่อนไหวเกือบเท่าหุ้นจริง</li>
          <li><strong>Deep OTM Call ≈ 0:</strong> แทบไม่ขยับ</li>
        </ul>
      </div>

      <p>กราฟด้านขวาแสดงทั้งเส้น Payoff (แกน Y ซ้าย) และเส้น Delta (แกน Y ขวา) พร้อมกัน สังเกตว่า Delta คือ "ความชัน" ของเส้น Payoff ณ แต่ละจุด</p>

      <div class="key-insight">
        <strong>Delta มีอีกความหมาย:</strong> Delta ≈ ความน่าจะเป็นที่ Option จะ In the Money ณ วันหมดอายุ เช่น Delta = 0.3 หมายความว่ามีโอกาสประมาณ 30% ที่ Option จะมีค่า ณ วันหมดอายุ (เป็นการประมาณเท่านั้น ไม่ใช่ค่าที่แน่นอน)
      </div>

      <p>ลองเลื่อน slider "วันถึงหมดอายุ" — ดูว่าเมื่อเวลาน้อยลง เส้น Delta จะ "ชันขึ้น" บริเวณ Strike (เปลี่ยนจาก 0 เป็น 1 อย่างรวดเร็ว) เพราะเมื่อใกล้หมดอายุ ตลาดมั่นใจมากขึ้นว่า Option จะ ITM หรือ OTM</p>
    `
  },

  {
    id: '5.3',
    section: 5,
    sectionTitle: 'Greeks',
    title: 'Gamma (Γ)',
    chartType: 'greeks',
    strategy: null,
    defaultParams: { strike: 100, premium: 5, daysToExpiry: 30, sigma: 0.25 },
    showLegs: false,
    legLabels: [],
    controls: [
      { type: 'range', key: 'strike', label: 'ราคาใช้สิทธิ์ (K)', min: 50, max: 200, step: 1, default: 100 },
      { type: 'range', key: 'daysToExpiry', label: 'วันถึงหมดอายุ', min: 1, max: 180, step: 1, default: 30 },
      { type: 'range', key: 'sigma', label: 'ความผันผวน (σ) %', min: 5, max: 80, step: 1, default: 25 }
    ],
    content: `
      <p><strong>Gamma (Γ)</strong> คือ "อัตราการเปลี่ยนแปลงของ Delta" — หรืออนุพันธ์อันดับสองของราคา Option ต่อราคาสินทรัพย์ พูดง่ายๆ คือ Gamma วัดว่า Delta เปลี่ยนเร็วแค่ไหน</p>

      <div class="formula">
        Γ = ∂Δ / ∂S = ∂²V / ∂S²
      </div>

      <p>Gamma สูงสุดเมื่อ Option อยู่ <strong>At the Money (ATM)</strong> และ <strong>ใกล้หมดอายุ</strong> — นี่คือจุดที่ Delta เปลี่ยนแปลงเร็วที่สุด</p>

      <div class="highlight-box">
        <strong>ทำไม Gamma สำคัญ?</strong>
        <ul>
          <li><strong>Gamma สูง = Delta ไม่เสถียร:</strong> ราคาขยับนิดเดียว Delta เปลี่ยนมาก → ยากต่อการ Hedge</li>
          <li><strong>Gamma ต่ำ = Delta เสถียร:</strong> ราคาขยับ Delta แทบไม่เปลี่ยน → Hedge ง่าย</li>
          <li><strong>Long Options = Long Gamma:</strong> ได้ประโยชน์จากการเคลื่อนไหวของราคา</li>
          <li><strong>Short Options = Short Gamma:</strong> เสียเปรียบจากการเคลื่อนไหวของราคา</li>
        </ul>
      </div>

      <div class="key-insight">
        <strong>Gamma Risk ใกล้หมดอายุ:</strong> เมื่อเหลือเวลาน้อย Gamma ของ ATM Options จะพุ่งสูงมาก — Delta อาจกระโดดจาก 0.1 เป็น 0.9 ภายในวันเดียว! นี่คือเหตุผลที่ Market Maker ต้องปรับ Hedge บ่อยมากในสัปดาห์สุดท้ายก่อนหมดอายุ
      </div>

      <p>ลองเลื่อน slider "วันถึงหมดอายุ" ไปที่ค่าน้อยๆ (1-5 วัน) แล้วดูว่ากราฟ Gamma แหลมขึ้นมากแค่ไหน!</p>
    `
  },

  {
    id: '5.4',
    section: 5,
    sectionTitle: 'Greeks',
    title: 'Theta (Θ)',
    chartType: 'greeks',
    strategy: null,
    defaultParams: { strike: 100, premium: 5, daysToExpiry: 30, sigma: 0.25 },
    showLegs: false,
    legLabels: [],
    controls: [
      { type: 'range', key: 'strike', label: 'ราคาใช้สิทธิ์ (K)', min: 50, max: 200, step: 1, default: 100 },
      { type: 'range', key: 'daysToExpiry', label: 'วันถึงหมดอายุ', min: 1, max: 180, step: 1, default: 30 },
      { type: 'range', key: 'sigma', label: 'ความผันผวน (σ) %', min: 5, max: 80, step: 1, default: 25 }
    ],
    content: `
      <p><strong>Theta (Θ)</strong> คือ "การสูญเสียมูลค่าจากเวลาต่อวัน" — นี่คือเหตุผลที่เส้นโค้งในบท 5.1 ค่อยๆ แบนลงจนกลายเป็นเส้นตรง Theta วัดว่าแต่ละวันที่ผ่านไป Option เสียมูลค่าไปเท่าไหร่</p>

      <div class="formula">
        Θ = ∂V / ∂t ≈ การเปลี่ยนแปลงของราคา Option ต่อวัน
      </div>

      <div class="highlight-box">
        <strong>คุณสมบัติของ Theta:</strong>
        <ul>
          <li>Theta มีค่า <strong>เป็นลบ</strong> สำหรับ Long Options เสมอ (มูลค่าลดลงทุกวัน)</li>
          <li>Theta มีค่า <strong>เป็นบวก</strong> สำหรับ Short Options (เวลาเป็นเพื่อนของคนขาย)</li>
          <li>ATM Options มี Theta <strong>สูงสุด</strong> (ค่าเวลามากสุด → เสียมากสุดต่อวัน)</li>
          <li>Theta <strong>เร่งตัว</strong> เมื่อใกล้หมดอายุ — 30 วันสุดท้ายเสียเวลาเร็วกว่า 30 วันแรก!</li>
        </ul>
      </div>

      <p>ลองเลื่อน slider "วันถึงหมดอายุ" ช้าๆ จาก 180 ลงมา — สังเกตว่า Theta (เส้นสีแดง) ยิ่งติดลบมากขึ้นเมื่อเหลือเวลาน้อย เหมือนน้ำแข็งละลาย ยิ่งใกล้ดวงอาทิตย์ยิ่งละลายเร็ว</p>

      <div class="key-insight">
        <strong>Theta vs Gamma — สมดุลธรรมชาติ:</strong> Long Options ได้ Gamma (ประโยชน์จากการเคลื่อนไหว) แต่เสีย Theta (เสียค่าเวลาทุกวัน) Short Options ตรงข้าม — นี่คือสมดุลพื้นฐานของ Options ไม่มีอะไรได้ฟรี!
      </div>

      <div class="warning-box">
        <strong>คำเตือนสำหรับผู้ถือ Long Options:</strong> อย่าถือ Long Options นานเกินไปโดยไม่มีเหตุผล Theta จะกัดกินมูลค่าของคุณทุกวัน โดยเฉพาะใน 30 วันสุดท้าย — ต้องมั่นใจว่าการเคลื่อนไหวที่คาดหวังจะชดเชย Theta ได้
      </div>
    `
  },

  {
    id: '5.5',
    section: 5,
    sectionTitle: 'Greeks',
    title: 'Vega (ν)',
    chartType: 'greeks',
    strategy: null,
    defaultParams: { strike: 100, premium: 5, daysToExpiry: 30, sigma: 0.25 },
    showLegs: false,
    legLabels: [],
    controls: [
      { type: 'range', key: 'strike', label: 'ราคาใช้สิทธิ์ (K)', min: 50, max: 200, step: 1, default: 100 },
      { type: 'range', key: 'daysToExpiry', label: 'วันถึงหมดอายุ', min: 1, max: 180, step: 1, default: 30 },
      { type: 'range', key: 'sigma', label: 'ความผันผวน (σ) %', min: 5, max: 80, step: 1, default: 25 }
    ],
    content: `
      <p><strong>Vega (ν)</strong> คือ "ความไวต่อความผันผวน" — วัดว่ามูลค่า Option เปลี่ยนไปเท่าไหร่เมื่อ Implied Volatility เปลี่ยน 1%</p>

      <div class="formula">
        ν = ∂V / ∂σ ≈ การเปลี่ยนแปลงของราคา Option ต่อ 1% ของ IV
      </div>

      <div class="highlight-box">
        <strong>คุณสมบัติของ Vega:</strong>
        <ul>
          <li>Vega มีค่า <strong>เป็นบวก</strong> สำหรับ Long Options (Vol ขึ้น = ราคา Option ขึ้น)</li>
          <li>Vega มีค่า <strong>เป็นลบ</strong> สำหรับ Short Options (Vol ขึ้น = เสียเปรียบ)</li>
          <li>ATM Options มี Vega <strong>สูงสุด</strong></li>
          <li>Vega <strong>ลดลง</strong> เมื่อใกล้หมดอายุ (เวลาน้อย = Vol มีผลน้อยลง)</li>
        </ul>
      </div>

      <p>ลองเลื่อน slider "ความผันผวน" แล้วดูว่าเส้นโค้ง Payoff เปลี่ยนอย่างไร — เมื่อ Vol สูง เส้นโค้งจะ "ป่อง" ออก (Time Value สูง) เมื่อ Vol ต่ำ เส้นโค้งจะ "แนบ" กับเส้นหมดอายุมากขึ้น</p>

      <div class="key-insight">
        <strong>ทำไม Vega สำคัญ?</strong> ในการเทรด Options จริง ราคาไม่ได้ขึ้นอยู่กับทิศทางเพียงอย่างเดียว — <strong>Implied Volatility</strong> (IV) เปลี่ยนแปลงตลอดเวลาและส่งผลต่อราคามาก ตัวอย่างเช่น คุณซื้อ Long Call ถูกทิศทาง (ราคาขึ้น) แต่ถ้า IV ลดลงพร้อมกัน คุณอาจไม่ได้กำไรเลย!
      </div>

      <div class="warning-box">
        <strong>IV Crush:</strong> หลังเหตุการณ์สำคัญ (เช่น ประกาศผลประกอบการ) IV มักลดลงอย่างรวดเร็ว — เรียกว่า "IV Crush" ทำให้ Long Options ทั้ง Call และ Put เสียมูลค่าทันที แม้ราคาจะเคลื่อนไหวไปในทิศที่ต้องการก็ตาม
      </div>
    `
  },


  // ============================================================
  // Section 6: Advanced Combinations
  // ============================================================
  {
    id: '6.1',
    section: 6,
    sectionTitle: 'Advanced Combinations',
    title: 'Ratio Spreads',
    chartType: 'payoff',
    strategy: 'ratioCallSpread',
    defaultParams: { strike1: 95, premium1: 8, strike2: 110, premium2: 3, ratio: 2 },
    showLegs: true,
    legLabels: ['Long 1x Call K₁', 'Short 2x Call K₂'],
    controls: [
      { type: 'range', key: 'strike1', label: 'Strike K₁ (Long Call)', min: 50, max: 200, step: 1, default: 95 },
      { type: 'range', key: 'premium1', label: 'Premium K₁', min: 1, max: 30, step: 0.5, default: 8 },
      { type: 'range', key: 'strike2', label: 'Strike K₂ (Short Call)', min: 50, max: 200, step: 1, default: 110 },
      { type: 'range', key: 'premium2', label: 'Premium K₂', min: 1, max: 30, step: 0.5, default: 3 },
      { type: 'range', key: 'ratio', label: 'Ratio (Short:Long)', min: 1, max: 4, step: 1, default: 2 }
    ],
    content: `
      <p><strong>Ratio Spread</strong> — "ถ้าจำนวน contracts ไม่เท่ากันล่ะ?" จนถึงตอนนี้ เราใช้ 1:1 ตลอด แต่ถ้าเปลี่ยนเป็น 1:2 หรือ 1:3 ล่ะ? รูปร่างจะเปลี่ยนไปอย่างมาก!</p>

      <p><strong>1x2 Ratio Call Spread</strong> = Long 1 Call K₁ + Short 2 Call K₂ ต่างจาก Bull Call Spread ตรงที่ขายมากกว่าซื้อ</p>

      <div class="formula">
        Net Premium = Premium₁ - (Ratio × Premium₂)<br>
        ถ้า Net Premium &lt; 0 → ได้เงินเข้ามา (Credit)<br>
        ถ้า Ratio ≥ 2 → มี "ขา" ที่ไม่ได้ Cover → ความเสี่ยงไม่จำกัด!
      </div>

      <div class="highlight-box">
        <strong>ลองเลื่อน Ratio slider!</strong> สังเกตการเปลี่ยนแปลง:
        <ul>
          <li><strong>Ratio 1:</strong> Bull Call Spread ปกติ — กำไรจำกัด ขาดทุนจำกัด</li>
          <li><strong>Ratio 2:</strong> กราฟเริ่ม "งอลง" ทางขวา — กำไรมีจุดสูงสุดแล้วเริ่มลด</li>
          <li><strong>Ratio 3+:</strong> กราฟดิ่งลงอย่างรวดเร็ว — ความเสี่ยงไม่จำกัดทางขวา!</li>
        </ul>
      </div>

      <div class="key-insight">
        <strong>จำนวน (Quantity) เป็นอีกตัวแปรหนึ่งที่เปลี่ยนรูปร่าง!</strong> นอกจาก Strike, Premium, Call/Put, Long/Short แล้ว Quantity ก็สำคัญ เพราะมันเปลี่ยน "ความชัน" ของแต่ละขา เมื่อชันไม่เท่ากัน ผลรวมก็เปลี่ยนไปอย่างมาก
      </div>

      <div class="warning-box">
        <strong>ระวัง:</strong> Ratio Spread ที่ Short มากกว่า Long จะมี "naked leg" — ส่วนที่ไม่ได้ hedge ทำให้ความเสี่ยงไม่จำกัด ต้องเข้าใจความเสี่ยงนี้ก่อนใช้งานจริง
      </div>
    `
  },

  {
    id: '6.2',
    section: 6,
    sectionTitle: 'Advanced Combinations',
    title: 'Back Ratio Spread',
    chartType: 'payoff',
    strategy: 'backRatioCallSpread',
    defaultParams: { strike1: 95, premium1: 8, strike2: 110, premium2: 3, ratio: 2 },
    showLegs: true,
    legLabels: ['Short 1x Call K₁', 'Long 2x Call K₂'],
    controls: [
      { type: 'range', key: 'strike1', label: 'Strike K₁ (Short Call)', min: 50, max: 200, step: 1, default: 95 },
      { type: 'range', key: 'premium1', label: 'Premium K₁', min: 1, max: 30, step: 0.5, default: 8 },
      { type: 'range', key: 'strike2', label: 'Strike K₂ (Long Call)', min: 50, max: 200, step: 1, default: 110 },
      { type: 'range', key: 'premium2', label: 'Premium K₂', min: 1, max: 30, step: 0.5, default: 3 },
      { type: 'range', key: 'ratio', label: 'Ratio (Long:Short)', min: 1, max: 4, step: 1, default: 2 }
    ],
    content: `
      <p><strong>Back Ratio Spread</strong> — พลิก Ratio กลับด้าน! ซื้อมากกว่าขาย กำไรไม่จำกัดกลับมา</p>

      <p><strong>1x2 Back Ratio Call Spread</strong> = Short 1 Call K₁ + Long 2 Call K₂ — ขาย Call ถูก 1 ตัว ซื้อ Call แพง 2 ตัว</p>

      <div class="formula">
        Net Premium = (Ratio × Premium₂) - Premium₁<br>
        ถ้า Net Premium &gt; 0 → ต้องจ่ายเงิน (Debit)<br>
        ถ้า Net Premium &lt; 0 → ได้เงินเข้ามา (Credit) — สถานการณ์ในฝัน!
      </div>

      <div class="highlight-box">
        <strong>รูปร่างของ Back Ratio:</strong>
        <ul>
          <li>ราคาอยู่ต่ำ → Short Call ไม่มีค่า, Long Call ก็ไม่มีค่า → ผลลัพธ์ ≈ Net Premium</li>
          <li>ราคาอยู่ระหว่าง K₁ กับ K₂ → Short Call เริ่มเสีย, Long Call ยังไม่มีค่า → โซนอันตราย!</li>
          <li>ราคาสูงมาก → Long Call 2 ตัวทำงาน สุทธิ "ชัน +1" → กำไรไม่จำกัด!</li>
        </ul>
      </div>

      <div class="key-insight">
        <strong>Back Ratio เหมาะเมื่อ:</strong> คุณคิดว่าราคาจะ "ระเบิด" ขึ้นไปไกลมาก หรือไม่ก็อยู่นิ่ง แต่จะเจ็บถ้าราคาขึ้นนิดเดียว (โซนระหว่าง K₁ กับ K₂) เป็นกลยุทธ์ที่น่าสนใจเมื่อ IV ต่ำและคาดว่าจะเพิ่มขึ้น
      </div>
    `
  },

  {
    id: '6.3',
    section: 6,
    sectionTitle: 'Advanced Combinations',
    title: 'Calendar Spread',
    chartType: 'timeCurve',
    strategy: null,
    defaultParams: { strike: 100, daysNear: 30, daysFar: 90, sigma: 0.25 },
    showLegs: false,
    legLabels: [],
    controls: [
      { type: 'range', key: 'strike', label: 'ราคาใช้สิทธิ์ (K)', min: 50, max: 200, step: 1, default: 100 },
      { type: 'range', key: 'daysNear', label: 'วันหมดอายุ (Near)', min: 1, max: 90, step: 1, default: 30 },
      { type: 'range', key: 'daysFar', label: 'วันหมดอายุ (Far)', min: 30, max: 365, step: 1, default: 90 },
      { type: 'range', key: 'sigma', label: 'ความผันผวน (σ) %', min: 5, max: 80, step: 1, default: 25 }
    ],
    content: `
      <p><strong>Calendar Spread</strong> (Time Spread) = Short Option ใกล้หมดอายุ + Long Option ไกลหมดอายุ (Strike เดียวกัน) — มิติใหม่: <strong>เวลา!</strong></p>

      <p>จนถึงตอนนี้ กลยุทธ์ทั้งหมดใช้วันหมดอายุเดียวกัน แต่ Calendar Spread ใช้วันหมดอายุต่างกัน ทำให้ต้องใช้ <strong>ราคาทฤษฎี (Black-Scholes)</strong> จากบท 5 ในการวิเคราะห์</p>

      <div class="highlight-box">
        <strong>หลักการทำงาน:</strong>
        <ul>
          <li>Short Near-Term: หมดอายุเร็ว → Theta สูง → สูญเสียค่าเวลาเร็ว (ดีสำหรับคนขาย)</li>
          <li>Long Far-Term: หมดอายุช้า → Theta ต่ำ → สูญเสียค่าเวลาช้า</li>
          <li>ผลรวม: คุณ "เก็บเกี่ยว" ส่วนต่างของ Theta → กำไรจากเวลาที่ผ่านไป</li>
        </ul>
      </div>

      <div class="formula">
        Payoff ≈ ราคาทฤษฎี Far-Term Option - Payoff Near-Term Option - Net Debit<br>
        กำไรสูงสุดเมื่อ S ≈ K ณ วันหมดอายุของ Near-Term
      </div>

      <div class="key-insight">
        <strong>Calendar Spread เดิมพันกับ Theta!</strong> กำไรสูงสุดเมื่อราคาอยู่ที่ Strike พอดี ณ วันหมดอายุของขา Near — เพราะ Near-Term หมดค่า ส่วน Far-Term ยังมี Time Value เหลืออยู่ เป็นกลยุทธ์ที่ต้องเข้าใจ Greeks (โดยเฉพาะ Theta) อย่างดี
      </div>
    `
  },

  {
    id: '6.4',
    section: 6,
    sectionTitle: 'Advanced Combinations',
    title: 'Diagonal Spread',
    chartType: 'timeCurve',
    strategy: null,
    defaultParams: { strike1: 95, strike2: 105, daysNear: 30, daysFar: 90, sigma: 0.25 },
    showLegs: false,
    legLabels: [],
    controls: [
      { type: 'range', key: 'strike1', label: 'Strike K₁ (Near)', min: 50, max: 200, step: 1, default: 95 },
      { type: 'range', key: 'strike2', label: 'Strike K₂ (Far)', min: 50, max: 200, step: 1, default: 105 },
      { type: 'range', key: 'daysNear', label: 'วันหมดอายุ (Near)', min: 1, max: 90, step: 1, default: 30 },
      { type: 'range', key: 'daysFar', label: 'วันหมดอายุ (Far)', min: 30, max: 365, step: 1, default: 90 },
      { type: 'range', key: 'sigma', label: 'ความผันผวน (σ) %', min: 5, max: 80, step: 1, default: 25 }
    ],
    content: `
      <p><strong>Diagonal Spread</strong> = Calendar Spread + ต่าง Strike — รวมมิติ <strong>ราคา</strong> และ <strong>เวลา</strong> เข้าด้วยกัน</p>

      <p>Short Near-Term Call K₁ + Long Far-Term Call K₂ โดย K₁ ≠ K₂ และวันหมดอายุต่างกัน ถ้ามองในตาราง Options Chain จะเห็นว่าตำแหน่งทั้งสองอยู่บน "เส้นทแยง" (Diagonal)</p>

      <div class="highlight-box">
        <strong>เปรียบเทียบ 3 ประเภท Spread:</strong>
        <ul>
          <li><strong>Vertical Spread:</strong> ต่าง Strike, หมดอายุเดียวกัน (เดิมพันทิศทาง)</li>
          <li><strong>Calendar Spread:</strong> Strike เดียวกัน, ต่างหมดอายุ (เดิมพันเวลา)</li>
          <li><strong>Diagonal Spread:</strong> ต่าง Strike + ต่างหมดอายุ (เดิมพันทั้งทิศทาง+เวลา)</li>
        </ul>
      </div>

      <p>Diagonal Spread ให้ความยืดหยุ่นมากที่สุด — คุณสามารถปรับ "ทิศเอียง" ของกำไรสูงสุดได้ ถ้า K₂ &gt; K₁ (Long Call ที่ Strike สูงกว่า) = เอียงขาขึ้น ถ้า K₂ &lt; K₁ = เอียงขาลง</p>

      <div class="key-insight">
        <strong>Diagonal Spread เหมาะเมื่อ:</strong> คุณมีมุมมองทั้งทิศทาง (ราคาจะขยับไปทางไหน) และเวลา (จะขยับเมื่อไหร่) ตัวอย่าง: คุณคิดว่าราคาจะค่อยๆ ขึ้นในอีก 2-3 เดือน → ใช้ Diagonal Call Spread ที่ Strike Long สูงกว่า Short
      </div>

      <div class="warning-box">
        <strong>ข้อควรระวัง:</strong> Diagonal Spread ซับซ้อนกว่า Vertical และ Calendar เพราะมีตัวแปรมากกว่า Greeks ทั้ง Delta, Theta, Vega ล้วนมีผล ต้องเข้าใจบทที่ 5 อย่างดีก่อนใช้งานจริง
      </div>
    `
  },


  // ============================================================
  // Section 7: ประยุกต์ใช้ - "คิดจาก Scenario"
  // ============================================================
  {
    id: '7.1',
    section: 7,
    sectionTitle: 'ประยุกต์ใช้ - "คิดจาก Scenario"',
    title: '"คิดว่าราคาจะขึ้น"',
    chartType: 'comparison',
    strategy: null,
    defaultParams: { strike: 100, premium: 5 },
    showLegs: false,
    legLabels: [],
    controls: [
      { type: 'range', key: 'strike', label: 'ราคาใช้สิทธิ์ (K)', min: 50, max: 200, step: 1, default: 100 },
      { type: 'range', key: 'premium', label: 'ค่า Premium', min: 1, max: 30, step: 0.5, default: 5 }
    ],
    content: `
      <p>ถ้าคุณคิดว่าราคาจะขึ้น มีหลายวิธีที่จะทำกำไร — แต่ละวิธีมี Trade-off ต่างกัน มาเปรียบเทียบ:</p>

      <div class="highlight-box">
        <table style="width:100%; border-collapse: collapse; font-size: 0.95em;">
          <tr style="border-bottom:2px solid #ccc;">
            <th style="text-align:left; padding:6px;">กลยุทธ์</th>
            <th style="padding:6px;">ต้นทุน</th>
            <th style="padding:6px;">Max Loss</th>
            <th style="padding:6px;">Max Profit</th>
            <th style="padding:6px;">Break-even</th>
          </tr>
          <tr style="border-bottom:1px solid #eee;">
            <td style="padding:6px;"><strong>Long Call</strong></td>
            <td style="padding:6px;">Premium</td>
            <td style="padding:6px;">Premium</td>
            <td style="padding:6px;">ไม่จำกัด</td>
            <td style="padding:6px;">K + Premium</td>
          </tr>
          <tr style="border-bottom:1px solid #eee;">
            <td style="padding:6px;"><strong>Bull Call Spread</strong></td>
            <td style="padding:6px;">Net Premium</td>
            <td style="padding:6px;">Net Premium</td>
            <td style="padding:6px;">K₂-K₁-Net</td>
            <td style="padding:6px;">K₁ + Net</td>
          </tr>
          <tr>
            <td style="padding:6px;"><strong>Long Stock</strong></td>
            <td style="padding:6px;">ราคาหุ้น</td>
            <td style="padding:6px;">ราคาหุ้น</td>
            <td style="padding:6px;">ไม่จำกัด</td>
            <td style="padding:6px;">ราคาซื้อ</td>
          </tr>
        </table>
      </div>

      <p>กราฟด้านขวาแสดง Payoff ของทั้ง 3 กลยุทธ์ซ้อนกัน ลองสังเกต:</p>
      <ul>
        <li><strong>Long Call:</strong> ต้นทุนต่ำ กำไรไม่จำกัด แต่ต้องถูกทิศ+ถูกเวลา (Theta กัดกิน)</li>
        <li><strong>Bull Call Spread:</strong> ต้นทุนต่ำสุด กำไร/ขาดทุนจำกัดทั้งคู่ เหมาะกับ "ขึ้นพอประมาณ"</li>
        <li><strong>Long Stock:</strong> ต้นทุนสูงสุด แต่ไม่มี Time Decay ถือได้นานเท่าที่ต้องการ</li>
      </ul>

      <div class="key-insight">
        <strong>ไม่มีกลยุทธ์ที่ "ดีที่สุด"</strong> — มีแต่กลยุทธ์ที่ <strong>"เหมาะที่สุด" กับมุมมองของคุณ</strong> ถามตัวเองว่า: ราคาจะขึ้นเท่าไหร่? ภายในเวลาเท่าไหร่? พร้อมเสียเท่าไหร่? คำตอบจะบอกว่าควรใช้กลยุทธ์ไหน
      </div>
    `
  },

  {
    id: '7.2',
    section: 7,
    sectionTitle: 'ประยุกต์ใช้ - "คิดจาก Scenario"',
    title: '"คิดว่าราคาจะนิ่ง"',
    chartType: 'comparison',
    strategy: null,
    defaultParams: { strike: 100, premium: 5 },
    showLegs: false,
    legLabels: [],
    controls: [
      { type: 'range', key: 'strike', label: 'ราคาใช้สิทธิ์ (K)', min: 50, max: 200, step: 1, default: 100 },
      { type: 'range', key: 'premium', label: 'ค่า Premium', min: 1, max: 30, step: 0.5, default: 5 }
    ],
    content: `
      <p>ตลาด Sideway — ราคาไม่ไปไหน ในโลกหุ้นทำอะไรไม่ได้ แต่ในโลก Options คุณสามารถทำกำไรจากความ "นิ่ง" ได้!</p>

      <div class="highlight-box">
        <table style="width:100%; border-collapse: collapse; font-size: 0.95em;">
          <tr style="border-bottom:2px solid #ccc;">
            <th style="text-align:left; padding:6px;">กลยุทธ์</th>
            <th style="padding:6px;">ความเสี่ยง</th>
            <th style="padding:6px;">Max Profit</th>
            <th style="padding:6px;">ช่วงกำไร</th>
          </tr>
          <tr style="border-bottom:1px solid #eee;">
            <td style="padding:6px;"><strong>Short Straddle</strong></td>
            <td style="padding:6px;">ไม่จำกัด!</td>
            <td style="padding:6px;">Premium ทั้งสอง</td>
            <td style="padding:6px;">แคบ</td>
          </tr>
          <tr style="border-bottom:1px solid #eee;">
            <td style="padding:6px;"><strong>Iron Condor</strong></td>
            <td style="padding:6px;">จำกัด</td>
            <td style="padding:6px;">Net Credit</td>
            <td style="padding:6px;">กว้างปานกลาง</td>
          </tr>
          <tr>
            <td style="padding:6px;"><strong>Butterfly</strong></td>
            <td style="padding:6px;">จำกัด (น้อยมาก)</td>
            <td style="padding:6px;">K₂-K₁-Debit</td>
            <td style="padding:6px;">แคบมาก</td>
          </tr>
        </table>
      </div>

      <ul>
        <li><strong>Short Straddle:</strong> กำไรสูงสุด แต่ความเสี่ยงไม่จำกัด — ต้องมี margin สูงและจัดการความเสี่ยงอย่างเข้มงวด</li>
        <li><strong>Iron Condor:</strong> ยอดนิยม! ความเสี่ยงจำกัด ช่วงกำไรกว้าง โอกาสชนะสูง แต่ Risk/Reward ratio ไม่ดี</li>
        <li><strong>Butterfly:</strong> ต้นทุนต่ำมาก กำไรสูงสุดสูง แต่ต้องแม่นยำมาก (ราคาต้องจบใกล้ K₂)</li>
      </ul>

      <div class="key-insight">
        <strong>กลยุทธ์ Neutral ทั้งหมดมีจุดร่วม:</strong> คือการ "ขาย Volatility" — คุณเดิมพันว่าความผันผวนจริง (Realized Vol) จะน้อยกว่าที่ตลาดคาด (Implied Vol) ถ้า IV สูงผิดปกติ กลยุทธ์เหล่านี้จะมีโอกาสสำเร็จสูงขึ้น
      </div>
    `
  },

  {
    id: '7.3',
    section: 7,
    sectionTitle: 'ประยุกต์ใช้ - "คิดจาก Scenario"',
    title: '"คิดว่าจะผันผวนแต่ไม่รู้ทิศทาง"',
    chartType: 'comparison',
    strategy: null,
    defaultParams: { strike: 100, premiumCall: 5, premiumPut: 5 },
    showLegs: false,
    legLabels: [],
    controls: [
      { type: 'range', key: 'strike', label: 'ราคาใช้สิทธิ์ (K)', min: 50, max: 200, step: 1, default: 100 },
      { type: 'range', key: 'premiumCall', label: 'Premium Call', min: 1, max: 30, step: 0.5, default: 5 },
      { type: 'range', key: 'premiumPut', label: 'Premium Put', min: 1, max: 30, step: 0.5, default: 5 }
    ],
    content: `
      <p>มีเหตุการณ์ใหญ่กำลังจะเกิดขึ้น (ประกาศผลประกอบการ, การเลือกตั้ง, รายงานเศรษฐกิจ) — คุณรู้ว่าราคาจะขยับแรง แต่ไม่รู้ว่าจะขึ้นหรือลง</p>

      <div class="highlight-box">
        <strong>Straddle vs Strangle — เลือกอันไหน?</strong>
        <table style="width:100%; border-collapse: collapse;">
          <tr style="border-bottom:2px solid #ccc;">
            <th style="text-align:left; padding:6px;">เกณฑ์</th>
            <th style="padding:6px;">Long Straddle</th>
            <th style="padding:6px;">Long Strangle</th>
          </tr>
          <tr style="border-bottom:1px solid #eee;">
            <td style="padding:6px;">ต้นทุน</td>
            <td style="padding:6px;">สูง (ATM ทั้งคู่)</td>
            <td style="padding:6px;">ต่ำ (OTM ทั้งคู่)</td>
          </tr>
          <tr style="border-bottom:1px solid #eee;">
            <td style="padding:6px;">ราคาต้องขยับ</td>
            <td style="padding:6px;">น้อยกว่า</td>
            <td style="padding:6px;">มากกว่า</td>
          </tr>
          <tr style="border-bottom:1px solid #eee;">
            <td style="padding:6px;">โอกาสกำไร</td>
            <td style="padding:6px;">สูงกว่า</td>
            <td style="padding:6px;">ต่ำกว่า</td>
          </tr>
          <tr>
            <td style="padding:6px;">กำไรต่อ 1 บาท</td>
            <td style="padding:6px;">ต่ำกว่า</td>
            <td style="padding:6px;">สูงกว่า (leverage ดี)</td>
          </tr>
        </table>
      </div>

      <p>ดูกราฟเปรียบเทียบ — Straddle (รูป V แหลม) ตัดเส้นศูนย์ใกล้กว่า Strangle (รูป V กว้าง) แต่ต้นทุน Straddle สูงกว่ามาก</p>

      <div class="key-insight">
        <strong>กฎง่ายๆ:</strong>
        <ul>
          <li>ถ้า IV ยังไม่สูงมาก + คาดว่าจะระเบิด → <strong>Straddle</strong> (ต้องการ margin of safety)</li>
          <li>ถ้า IV สูงอยู่แล้ว + ต้องการต้นทุนต่ำ → <strong>Strangle</strong> (ยอมรับว่าต้องเคลื่อนไหวมากกว่า)</li>
          <li>ถ้า IV สูงมาก → อย่าซื้อ Vol เลย! (อาจโดน IV Crush)</li>
        </ul>
      </div>

      <div class="warning-box">
        <strong>กับดัก IV Crush:</strong> ก่อนเหตุการณ์ IV มักสูงผิดปกติ (ตลาดรู้ว่าจะผันผวน) ทำให้ Option แพง หลังเหตุการณ์ IV มักลดลงอย่างรวดเร็ว แม้ราคาจะขยับ ถ้าขยับไม่มากพอ คุณอาจเสีย Vega มากกว่าได้ Delta
      </div>
    `
  },

  {
    id: '7.4',
    section: 7,
    sectionTitle: 'ประยุกต์ใช้ - "คิดจาก Scenario"',
    title: '"ต้องการ Hedge"',
    chartType: 'payoff',
    strategy: 'protectivePut',
    defaultParams: { strike: 100, premium: 5, stockPrice: 100 },
    showLegs: true,
    legLabels: ['Long Stock', 'Long Put'],
    controls: [
      { type: 'range', key: 'strike', label: 'ราคาใช้สิทธิ์ (K)', min: 50, max: 200, step: 1, default: 100 },
      { type: 'range', key: 'premium', label: 'ค่า Premium', min: 1, max: 30, step: 0.5, default: 5 },
      { type: 'range', key: 'stockPrice', label: 'ราคาหุ้นปัจจุบัน', min: 50, max: 200, step: 1, default: 100 }
    ],
    content: `
      <p><strong>Hedging = "เปลี่ยนรูปร่างของ Payoff"</strong> — คุณมีตำแหน่งอยู่แล้ว (เช่น ถือหุ้น) และต้องการป้องกันความเสี่ยง</p>

      <div class="highlight-box">
        <strong>3 กลยุทธ์ Hedge หลัก:</strong>
        <ul>
          <li><strong>Protective Put:</strong> ถือหุ้น + ซื้อ Put = "ประกันขาลง"
            <br>→ Payoff รวม = Long Call shape! (จำกัดขาดทุน กำไรไม่จำกัด)</li>
          <li><strong>Covered Call:</strong> ถือหุ้น + ขาย Call = "รายได้เสริม แลกกับการจำกัดกำไร"
            <br>→ Payoff รวม = Short Put shape! (รับ Premium แต่ยังเสี่ยงขาลง)</li>
          <li><strong>Collar:</strong> ถือหุ้น + ซื้อ Put + ขาย Call = "ครอบทั้งบนทั้งล่าง"
            <br>→ Payoff รวม = Bull Spread shape! (จำกัดทั้งกำไรและขาดทุน)</li>
        </ul>
      </div>

      <p>สังเกตว่าทุกกลยุทธ์ Hedge ไม่ได้ "ลบ" ความเสี่ยงออก — แค่ <strong>"เปลี่ยนรูปร่าง"</strong> ของ Payoff ให้เหมาะกับความต้องการ ยอมสละบางส่วน (ต้นทุน Premium หรือ Upside) เพื่อแลกกับความปลอดภัย</p>

      <div class="key-insight">
        <strong>Hedge คือการบวก Payoff!</strong> หลักการเดียวกับบท 3.1 — Protective Put = Long Stock + Long Put เอา Payoff ทั้งสองมาบวกกัน ก็ได้รูปร่าง Long Call นี่คือพลังของหลักการบวก Payoff — ใช้ได้กับทุกสถานการณ์
      </div>

      <div class="warning-box">
        <strong>Hedge มีต้นทุน!</strong> Protective Put ต้องจ่าย Premium (เหมือนเบี้ยประกัน) ถ้าราคาไม่ลง คุณเสียเงินฟรี Covered Call ไม่ต้องจ่ายเงิน แต่ต้องสละ Upside ถ้าราคาพุ่ง ไม่มี Hedge ที่ฟรี — ถ้ามีใครบอกว่ามี ให้ระวัง!
      </div>
    `
  },


  // ============================================================
  // Section 8: Full Sandbox
  // ============================================================
  {
    id: '8.1',
    section: 8,
    sectionTitle: 'Full Sandbox',
    title: 'ห้องทดลองขั้นสูง',
    chartType: 'sandbox',
    strategy: null,
    defaultParams: {},
    showLegs: true,
    legLabels: [],
    controls: [],
    content: `
      <p><strong>Full Sandbox</strong> — ห้องทดลองขั้นสูงที่คุณสามารถสร้างกลยุทธ์ใดก็ได้อย่างอิสระ</p>

      <div class="highlight-box">
        <strong>เครื่องมือที่มีให้:</strong>
        <ul>
          <li><strong>Leg Builder:</strong> เพิ่มขา Option ได้ไม่จำกัด (Call/Put, Long/Short, Strike, Premium, จำนวน)</li>
          <li><strong>Strategy Presets:</strong> โหลดกลยุทธ์สำเร็จรูปเป็นจุดเริ่มต้น แล้วปรับแต่งตามต้องการ</li>
          <li><strong>Show Legs:</strong> แสดง/ซ่อนเส้น Payoff ของแต่ละขา</li>
        </ul>
      </div>

      <div class="key-insight">
        <strong>แนวทางการทดลอง:</strong>
        <ul>
          <li>เริ่มจาก Strategy Preset แล้วลองเปลี่ยน Strike, Premium หรือเพิ่ม/ลดขา</li>
          <li>ลองสร้างกลยุทธ์ที่คุณเคยเห็นในข่าว/บทความ</li>
          <li>ลองปรับ Ratio ของขาต่างๆ ดูว่ารูปร่างเปลี่ยนอย่างไร</li>
          <li>ท้าทายตัวเอง: สร้าง Payoff ที่มีกำไรในช่วงราคาที่เฉพาะเจาะจง</li>
        </ul>
      </div>

      <div class="highlight-box">
        <strong>Challenge Mode:</strong> ระบบจะสุ่มรูปร่าง Payoff เป้าหมาย คุณต้องสร้างกลยุทธ์ที่ให้ Payoff ตรงกัน
        <ul>
          <li>ระดับง่าย: 2 ขา (Spreads พื้นฐาน)</li>
          <li>ระดับกลาง: 3-4 ขา (Butterfly, Condor)</li>
          <li>ระดับยาก: Ratio, มีขาซ้อน</li>
        </ul>
      </div>

      <p>จำไว้: <strong>ไม่มีคำตอบถูกผิด</strong> — มีแค่ Payoff ที่ตรงหรือไม่ตรงกับเป้าหมาย กลยุทธ์ที่ต่างกันอาจให้ Payoff เหมือนกันได้ (จำหลัก Synthetic Positions จากบท 2.6!)</p>
    `
  },

  // ============================================================
  // Section 9: สรุปและ Cheat Sheet
  // ============================================================
  {
    id: '9.1',
    section: 9,
    sectionTitle: 'สรุปและ Cheat Sheet',
    title: 'สรุปทุกกลยุทธ์',
    chartType: 'static',
    strategy: null,
    defaultParams: {},
    showLegs: false,
    legLabels: [],
    controls: [],
    content: `
      <p><strong>ตารางสรุปกลยุทธ์ทั้งหมด</strong> — ใช้เป็น Quick Reference</p>

      <div class="highlight-box">
        <table style="width:100%; border-collapse: collapse; font-size: 0.85em;">
          <tr style="border-bottom:2px solid #ccc; background:#f8f8f8;">
            <th style="text-align:left; padding:5px;">กลยุทธ์</th>
            <th style="padding:5px;">ส่วนประกอบ</th>
            <th style="padding:5px;">มุมมอง</th>
            <th style="padding:5px;">Max Loss</th>
            <th style="padding:5px;">Max Profit</th>
          </tr>
          <tr style="border-bottom:1px solid #eee;">
            <td style="padding:5px;">Long Call</td>
            <td style="padding:5px;">+1 Call</td>
            <td style="padding:5px;">ขาขึ้นแรง</td>
            <td style="padding:5px;">Premium</td>
            <td style="padding:5px;">ไม่จำกัด</td>
          </tr>
          <tr style="border-bottom:1px solid #eee;">
            <td style="padding:5px;">Long Put</td>
            <td style="padding:5px;">+1 Put</td>
            <td style="padding:5px;">ขาลงแรง</td>
            <td style="padding:5px;">Premium</td>
            <td style="padding:5px;">K - Premium</td>
          </tr>
          <tr style="border-bottom:1px solid #eee;">
            <td style="padding:5px;">Bull Call Spread</td>
            <td style="padding:5px;">+Call K₁, -Call K₂</td>
            <td style="padding:5px;">ขาขึ้นเล็กน้อย</td>
            <td style="padding:5px;">Net Debit</td>
            <td style="padding:5px;">(K₂-K₁)-Debit</td>
          </tr>
          <tr style="border-bottom:1px solid #eee;">
            <td style="padding:5px;">Bear Put Spread</td>
            <td style="padding:5px;">+Put K₂, -Put K₁</td>
            <td style="padding:5px;">ขาลงเล็กน้อย</td>
            <td style="padding:5px;">Net Debit</td>
            <td style="padding:5px;">(K₂-K₁)-Debit</td>
          </tr>
          <tr style="border-bottom:1px solid #eee;">
            <td style="padding:5px;">Long Straddle</td>
            <td style="padding:5px;">+Call K, +Put K</td>
            <td style="padding:5px;">ผันผวนมาก</td>
            <td style="padding:5px;">Premium ทั้งคู่</td>
            <td style="padding:5px;">ไม่จำกัด</td>
          </tr>
          <tr style="border-bottom:1px solid #eee;">
            <td style="padding:5px;">Long Strangle</td>
            <td style="padding:5px;">+Put K₁, +Call K₂</td>
            <td style="padding:5px;">ผันผวนมาก</td>
            <td style="padding:5px;">Premium ทั้งคู่</td>
            <td style="padding:5px;">ไม่จำกัด</td>
          </tr>
          <tr style="border-bottom:1px solid #eee;">
            <td style="padding:5px;">Iron Condor</td>
            <td style="padding:5px;">4 ขา</td>
            <td style="padding:5px;">Sideway</td>
            <td style="padding:5px;">Width - Credit</td>
            <td style="padding:5px;">Net Credit</td>
          </tr>
          <tr style="border-bottom:1px solid #eee;">
            <td style="padding:5px;">Butterfly</td>
            <td style="padding:5px;">+1,-2,+1 Call</td>
            <td style="padding:5px;">ราคาอยู่ที่จุด</td>
            <td style="padding:5px;">Net Debit</td>
            <td style="padding:5px;">(K₂-K₁)-Debit</td>
          </tr>
          <tr>
            <td style="padding:5px;">Protective Put</td>
            <td style="padding:5px;">Stock + Put</td>
            <td style="padding:5px;">Hedge ขาลง</td>
            <td style="padding:5px;">Premium+ส่วนต่าง</td>
            <td style="padding:5px;">ไม่จำกัด</td>
          </tr>
        </table>
      </div>

      <div class="key-insight">
        <strong>Flowchart: เลือกกลยุทธ์จากมุมมอง</strong>
        <ul>
          <li><strong>ราคาจะขึ้นมาก?</strong> → Long Call หรือ Back Ratio Call Spread</li>
          <li><strong>ราคาจะขึ้นเล็กน้อย?</strong> → Bull Call Spread หรือ Short Put</li>
          <li><strong>ราคาจะลงมาก?</strong> → Long Put</li>
          <li><strong>ราคาจะลงเล็กน้อย?</strong> → Bear Put Spread หรือ Short Call</li>
          <li><strong>ราคาจะผันผวนมาก?</strong> → Long Straddle หรือ Long Strangle</li>
          <li><strong>ราคาจะนิ่ง?</strong> → Iron Condor, Butterfly, หรือ Short Straddle</li>
          <li><strong>ต้องการ Hedge หุ้นที่ถืออยู่?</strong> → Protective Put หรือ Collar</li>
          <li><strong>ต้องการรายได้ประจำ?</strong> → Covered Call หรือ Iron Condor</li>
        </ul>
      </div>

      <div class="formula">
        หลักการ 3 ข้อที่สำคัญที่สุด:<br><br>
        1. Short = พลิก Long กลับหัว<br>
        2. Payoff รวม = ผลรวมของแต่ละขา (หลักการบวก)<br>
        3. ทุกตำแหน่งสร้างได้จากส่วนผสมอื่น (Put-Call Parity)
      </div>

      <div class="warning-box">
        <strong>คำเตือนสุดท้าย:</strong> Payoff Chart แสดงแค่กำไร/ขาดทุน ณ วันหมดอายุ ในการเทรดจริงยังมีปัจจัยอื่นที่สำคัญ: Liquidity (สภาพคล่อง), Bid-Ask Spread, Commissions, Assignment Risk, และ Early Exercise ต้องพิจารณาทุกปัจจัยก่อนตัดสินใจเทรด
      </div>

      <p><strong>ขอให้สนุกกับการเทรด Options และจำไว้ว่า:</strong> อย่าท่องจำ ให้เข้าใจหลักการ แล้วคุณจะสร้างกลยุทธ์ใดก็ได้ด้วยตัวเอง!</p>
    `
  }

];

// Export for use in app.js
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { LESSONS };
}
