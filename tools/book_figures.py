#!/usr/bin/env python3
"""ตัวตรวจตัวเลขของเล่ม Payoff Mastery (pm-*), Arbitrage (arb-*) และ ตาของ Arbitrageur (eye-*)
คำนวณตัวอย่างตัวเลขใหม่จากอินพุตที่หนังสือให้ แล้วตรวจว่าข้อความในไฟล์ HTML ยังตรง

คู่กับ tools/math_figures.py (ชุดคณิตศาสตร์เล่ม 2 · Arb §1.5 · statarb · theory-extra) —
แยกไฟล์เพราะเล่มเหล่านี้เป็นเลขคณิตล้วน ไม่ต้องใช้ numpy

ใช้:  python3 tools/book_figures.py          → ตรวจ (exit 1 ถ้าไม่ตรง)
      python3 tools/book_figures.py --print  → พิมพ์ค่าอย่างเดียว
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
CHECKS = []  # (file, label, expected substring)


def expect(file, label, text):
    CHECKS.append((file, label, text))


def um(v, f=".2f"):
    """format แล้วแทนเครื่องหมายลบด้วย U+2212 ตามแบบหนังสือ"""
    return f"{v:{f}}".replace("-", "−")


def money(v, f=",.2f"):
    return um(v, f)


# ── บล็อกตรวจจะถูกเติมตามผลสำรวจ (pm · arb · eye) ─────────────────────────────
# ── Payoff Mastery (pm-part1…8) ─────────────────────────────────────────────────
def N(x):  # CDF ของ normal มาตรฐาน
    return 0.5*(1+math.erf(x/math.sqrt(2)))
def npdf(x):
    return math.exp(-x*x/2)/math.sqrt(2*math.pi)

K, P = 100, 5
expect("pm-part1.html", "LC/LP BE", f"LC BE={K+8}, MaxLoss=-8 | LP BE={K-8}, MaxLoss=-8")
pvk = 100*math.exp(-0.05*0.5)
expect("pm-part1.html", "PV(K) 6 เดือน", f"100 × e⁻⁰·⁰²⁵ = <strong>฿{pvk:.2f}</strong>")
expect("pm-part1.html", "PCP ซ้าย", f"8.50 + {pvk:.2f} = <strong>{8.50+pvk:.2f}</strong>")
expect("pm-part1.html", "PCP ขวา", f"5.80 + 100 = <strong>{105.80:.2f}</strong>")
expect("pm-part1.html", "PCP ต่าง", f"ต่าง = {8.50+pvk-105.80:.2f}")
expect("pm-part1.html", "phantom K ไม่ลด", f"C + K = 8.50 + 100 = {108.50:.2f}")
expect("pm-part1.html", "phantom ต่าง", f"ต่าง ฿{108.50-105.80:.2f}!")
expect("pm-part1.html", "phantom ส่วนเกิน", f"฿{100-pvk:.2f}")
expect("pm-part1.html", "arb จริง", f"Arb จริงมีแค่ ฿{8.50+pvk-105.80:.2f}")
pvk2 = 100*math.exp(-0.02)
expect("pm-part1.html", "PCP 2% 1 ปี", f"PV(K) = 100×e⁻⁰·⁰² = {pvk2:.2f}")
expect("pm-part1.html", "PCP 2% ทั้งสองข้าง", f"ซ้าย=12+{pvk2:.2f}={12+pvk2:.2f}, ขวา=7+100={107:.2f} → violation ฿{12+pvk2-107:.2f}")
expect("pm-part1.html", "conversion 120", f"หุ้น 120 + Put 0 − Call {120-100} = 100")
expect("pm-part1.html", "conversion 80", f"หุ้น 80 + Put {100-80} − Call 0 = 100")
box = 20*math.exp(-0.05*0.25)
expect("pm-part1.html", "box 90/110", f"(110-90) × e⁻⁰·⁰¹²⁵ = 20 × {math.exp(-0.05*0.25):.4f} = <strong>฿{box:.2f}</strong>")
expect("pm-part1.html", "box กำไร", f"กำไร ฿{box-18.50:.2f} risk-free!")
box2 = 10*math.exp(-0.03*0.5)
expect("pm-part1.html", "box 95/105", f"10 × e⁻⁰·⁰¹⁵ = 10 × {math.exp(-0.03*0.5):.4f} = ฿{box2:.2f}")
expect("pm-part1.html", "box 95/105 PV profit", f"PV profit ฿{box2-9.50:.2f}")
expect("pm-part1.html", "box 95/105 nominal", f"= 10 - 9.50 = ฿{10-9.50:.2f}")
expect("pm-part2.html", "BCS ปลายขวา", f"-5+(110-90)×1 = +{-5+20}")
expect("pm-part2.html", "covered call 120", f"120 − {120-100} = {min(120,100)}")
expect("pm-part2.html", "IC EV", f"EV = 0.7×2000 + 0.3×(-8000) = {0.7*2000:.0f}-{0.3*8000:.0f} = -฿{-(0.7*2000-0.3*8000):,.0f}")
expect("pm-part3.html", "butterfly peak", f"10 - 3 = <strong>฿{10-3}</strong>")
expect("pm-part3.html", "IC max loss", f"5 − 2 = {5-2}")
expect("pm-part3a.html", "bull spread debit", f"Long Call(90) ฿12 + Short Call(110) ฿4 → <strong>net debit ฿{12-4}</strong>")
p110 = 4 - 100 + 110*math.exp(-0.05*0.25); p90 = 12 - 100 + 90*math.exp(-0.05*0.25)
expect("pm-part3a.html", "bull spread credit (PCP)", f"Short Put(110) ฿{p110:.2f} + Long Put(90) ฿{p90:.2f} → <strong>net credit ฿{p110-p90:.2f}</strong>")
expect("pm-part3a.html", "debit+credit = PV(20)", f"8 + {p110-p90:.2f} = {8+p110-p90:.2f} = PV(K₂-K₁) = 20 × e⁻⁰·⁰¹²⁵")
expect("pm-part3a.html", "3× BCS max profit", f"3 × (110-100) - net premium = {3*10} - net")
expect("pm-part3a.html", "4× short put loss", f"ขาดทุน ฿{4*10} (ไม่ใช่ ฿10)")
expect("pm-part3a.html", "drill 4 max profit", f"3(20)-10={3*20-10}")
expect("pm-part3a.html", "deliberate flat ขวา", f"-5 + 2×(105-95) = -5+20 = +{-5+20}")
expect("pm-part3a.html", "deliberate ค่าที่ถูก", f"+15-10 = +{15-10}")
expect("pm-part4.html", "PM gap", f"→ gap {62-55}%")
p_ = [1/2.10, 1/3.30, 1/3.50]
expect("pm-part4.html", "overround", f"{p_[0]*100:.1f}% + {p_[1]*100:.1f}% + {p_[2]*100:.1f}% = {sum(p_)*100:.1f}% → overround {sum(p_)*100-100:.1f}%")
expect("pm-part4a.html", "staircase slope", f"slope = 1/5 = ${1/5:.2f} ต่อ $1")
expect("pm-part4a.html", "touch/close gap", f"Gap ${0.75-0.55:.2f}")
expect("pm-part5.html", "combined -17", f"Combined: -5 + (-2) + (-10) = <strong>{-5-2-10}</strong>")
# Black-Scholes S=100 K=100 r=5% σ=20% T=0.5
S0, K0, r0, sg, T0 = 100, 100, 0.05, 0.20, 0.5
d1 = (math.log(S0/K0) + (r0+sg*sg/2)*T0)/(sg*math.sqrt(T0)); d2 = d1 - sg*math.sqrt(T0)
disc = math.exp(-r0*T0)
C0 = S0*N(d1) - K0*disc*N(d2); P0 = C0 - S0 + K0*disc
expect("pm-part5a.html", "d₁", f"= <strong>{d1:.4f}</strong>")
expect("pm-part5a.html", "d₂", f"d₂ = {d1:.4f} - {sg*math.sqrt(T0):.4f} = <strong>{d2:.4f}</strong>")
expect("pm-part5a.html", "N(d₁)", f"N({d1:.4f}) ≈ <strong>{N(d1):.4f}</strong> (Delta)")
expect("pm-part5a.html", "N(d₂)", f"N({d2:.4f}) ≈ <strong>{N(d2):.4f}</strong> (P(ITM))")
expect("pm-part5a.html", "Call", f"= {S0*N(d1):.2f} - {K0*disc*N(d2):.2f}<br>\n&nbsp; = <strong>฿{C0:.2f}</strong>")
expect("pm-part5a.html", "Put ผ่าน PCP", f"P = {C0:.2f} - 100 + {K0*disc:.2f} = <strong>฿{P0:.2f}</strong>")
expect("pm-part5a.html", "digital", f"{disc:.4f} × {N(d2):.4f} = <strong>${disc*N(d2):.3f}</strong>")
expect("pm-part5a.html", "digital vs PM", f"{round(62-disc*N(d2)*100)}¢")
expect("pm-part5a.html", "Δ put", f"{N(d1)-1:.4f}")
g_ = npdf(d1)/(S0*sg*math.sqrt(T0))
expect("pm-part5a.html", "N′(d₁)", f"0.3989 × {math.exp(-d1*d1/2):.4f} = <strong>{npdf(d1):.4f}</strong>")
expect("pm-part5a.html", "Γ", f"{npdf(d1):.4f} / {S0*sg*math.sqrt(T0):.2f} = <strong>{g_:.4f}</strong>")
th1 = S0*npdf(d1)*sg/(2*math.sqrt(T0)); th2 = r0*K0*disc*N(d2)
expect("pm-part5a.html", "Θ สองพจน์", f"-({S0*npdf(d1)*sg:.3f})/({2*math.sqrt(T0):.4f}) - ({th2:.3f})")
expect("pm-part5a.html", "Θ รวม", f"= -{th1:.3f} - {th2:.3f} = <strong>-{th1+th2:.2f} ต่อปี</strong>")
expect("pm-part5a.html", "Θ ต่อวัน", f"-{th1+th2:.2f}/365 = <strong>-฿{(th1+th2)/365:.3f} ต่อวัน</strong>")
vega = S0*npdf(d1)*math.sqrt(T0)
expect("pm-part5a.html", "Vega", f"100 × {npdf(d1):.4f} × {math.sqrt(T0):.4f} = <strong>{vega:.2f}</strong>")
expect("pm-part5a.html", "Vega ต่อ 1%", f"{vega:.2f}/100 = <strong>฿{vega/100:.3f}</strong>")
expect("pm-part5a.html", "BCS EV", f"EV = 0.40×(-5) + 0.35×(0) + 0.25×(15) = -2 + 0 + {0.25*15:.2f} = <strong>+฿{0.40*-5+0.25*15:.2f}</strong>")
expect("pm-part5a.html", "Kelly b=2", f"(2×0.6 - 0.4) / 2 = (1.2-0.4)/2 = <strong>{(2*0.6-0.4)/2:.1f} = {(2*0.6-0.4)/2*100:.0f}%</strong>")
expect("pm-part6.html", "odds 1.80", f"1/1.80={1/1.80*100:.1f}% vs 60% → Options แพงกว่า {60-1/1.80*100:.1f}%")
expect("pm-part6.html", "delta+gamma", f"200 + (-50×5) = {200-50*5}")
expect("pm-part7.html", "IC slippage", f"2.00 - 4×0.05 = <strong>฿{2.00-0.20:.2f}</strong>")
expect("pm-part7.html", "IC slippage %", f"Slippage กิน {0.20/2.00*100:.0f}% ของ max profit")
expect("pm-part7.html", "butterfly slippage", f"4 legs × bid-ask ฿0.05 = ฿{4*0.05:.2f} → <strong>แค่ {0.20/10*100:.0f}% ของ max profit แต่เท่ากับ {0.20/1*100:.0f}% ของ max loss")
ev = 0.07*(10-0.20) + 0.93*(-1-0.20)
expect("pm-part7.html", "butterfly EV", f"0.07 × (10-0.20) + 0.93 × (-1-0.20) = {0.07*9.80:.3f} - {0.93*1.20:.3f} = <strong>{ev:.3f}</strong>")
expect("pm-part7.html", "PCP net edge", f"฿0.50 - ฿0.30 (spread) - ฿0.15 (borrow) = <strong>+฿{0.50-0.30-0.15:.2f}</strong>")
expect("pm-part7.html", "BCS 100/120", f"max profit = 20-7 = ฿{20-7}")
expect("pm-part7.html", "PM hedge net", f"$1 = ฿35 หักต้นทุน $0.25 = ฿{0.25*35:.2f} → เหลือ ฿{35-0.25*35:.2f} → <strong>แต่ loss จาก stock = ฿30 → net loss ฿{30-(35-0.25*35):.2f}")
expect("pm-part7.html", "PM hedge S=50", f"PM ยังได้แค่ ฿{35-8.75:.2f} (net loss ฿{50-(35-8.75):.2f})")
br = [0.20, 0.35, 0.30, 0.20]
expect("pm-part7.html", "brackets overround", f"sum ${sum(br):.2f} → <strong>overround {(sum(br)-1)*100:.0f}%</strong>")
expect("pm-part7.html", "brackets p", f"0.35/1.05 = <strong>{0.35/1.05*100:.1f}%</strong>")
pn = 0.35/1.05
expect("pm-part7.html", "brackets EV", f"EV = {pn:.3f} × ($1-$0.35) + {1-pn:.3f} × (-$0.35) = {pn*0.65:.3f} - {(1-pn)*0.35:.3f} = <strong>-${-(pn*0.65-(1-pn)*0.35):.3f}</strong>")
expect("pm-part7.html", "brackets return", f"$0.65 ({0.65/0.35*100:.0f}% return!)")
expect("pm-part7.html", "funding 0.05%", f"0.05% × 3 × 365 = <strong>{0.05*3*365:.2f}%/year!</strong>")
expect("pm-part8.html", "repair", f"฿2.50 × 2 = ฿{2.50*2:.0f}")
expect("pm-part8.html", "EV A", f"EV = 0.9×1 + 0.1×(-20) = <strong>{0.9*1-0.1*20:.2f}</strong>")
expect("pm-part8.html", "EV B", f"EV = 0.3×10 + 0.7×(-2) = <strong>+{0.3*10-0.7*2:.2f}</strong>")

# ── Arbitrage (arb-part1…8) ─────────────────────────────────────────────────────
expect("arb-part1.html", "ทอง A/B", f"<strong>กำไร ฿{30500-30000} ทันที")
expect("arb-part1.html", "Gross/Net", f"Gross ฿0.80 − ค่าใช้จ่าย ฿0.70 = Net ฿{0.80-0.70:.2f}")
expect("arb-part1.html", "BTC 4 ขา", f"(2,100,000 + 2,105,000) = ฿{round((2100000+2105000)*0.001):,} → กำไร ฿{5000-200-round((2100000+2105000)*0.001)}")
expect("arb-part1.html", "commission 4 ขา", f"Net=500−4(50)−4(80)=500−{4*50+4*80}= −฿{4*50+4*80-500} ขาดทุน!")
expect("arb-part1.html", "PV(K) 5% 1 ปี", f"100 × {math.exp(-0.05):.4f} = ฿{100*math.exp(-0.05):.2f}")
expect("arb-part1.html", "PCP 2% 1 ปี", f"PV(K) = 100×e⁻⁰·⁰² = {100*math.exp(-0.02):.2f} → ซ้าย=12+{100*math.exp(-0.02):.2f}={12+100*math.exp(-0.02):.2f} ขวา=7+100=107")
expect("arb-part1.html", "§1.5 541 วัน", f"ต้องถือราว {541} วันทำการ (สองปีเศษ)")  # 541 คำนวณใน math_figures.py (บล็อก Arb §1.5)
pvk = 100*math.exp(-0.05*0.5)
expect("arb-part3.html", "PV(K) 5% 6 เดือน", f"PV(K) = 100 × e⁻⁰·⁰²⁵ = ฿{pvk:.2f}")
expect("arb-part3.html", "PCP ซ้าย", f"C + PV(K) = 8.50 + {pvk:.2f} = <strong>฿{8.50+pvk:.2f}</strong>")
expect("arb-part3.html", "PCP ขวา", f"P + S = 5.80 + 100 = <strong>฿{5.80+100:.2f}</strong>")
expect("arb-part3.html", "PCP violation", f"Violation = {8.50+pvk:.2f} - {105.80:.2f} = <strong>฿{8.50+pvk-105.80:.2f}</strong>")
expect("arb-part3.html", "Conversion net", f"Net = 0.23 - 0.12 - 0.20 = -฿{-(0.23-0.12-0.20):.2f}")
box = 20*math.exp(-0.05*0.25)
expect("arb-part3.html", "box fair", f"PV(110-90) = 20 × e⁻⁰·⁰¹²⁵ = ฿{box:.2f}")
expect("arb-part3.html", "box price", f"Box Price = 12 + 6.50 = <strong>฿{12+6.50:.2f}</strong>")
expect("arb-part3.html", "box profit expiry", f"= 20 - 18.50 = <strong>฿{20-18.50:.2f} risk-free</strong>")
expect("arb-part3.html", "box profit PV", f"= {box:.2f} - 18.50 = ฿{box-18.50:.2f}")
box2 = 10*math.exp(-0.03*0.5)
expect("arb-part3.html", "box 95/105 fair", f"Fair={box2:.2f} → market 9.50 < fair → ซื้อ Box ได้ ฿10 at expiry → กำไร ฿{10-9.50:.2f} ณ วันหมดอายุ = ฿{box2-9.50:.2f} มูลค่าปัจจุบัน")
earn = 100000*0.12/365*30
expect("arb-part3.html", "Earn 12% 30 วัน", f"฿100,000 × 12% / 365 × 30 วัน = ฿{earn:,.0f} ต่อเดือน")
expect("arb-part3.html", "Earn net", f"฿{earn:,.0f} (หลังหัก withdrawal fee ฿2) = <strong>฿{earn-2:,.0f}")
k = (0.167*0.92-0.08)/0.167
expect("arb-part2b.html", "Kelly 0.44", f"= {0.167*0.92-0.08:.3f}/0.167 = <strong>{k:.2f} → ใช้ {k/2*100:.0f}% ของพอร์ต (Half-Kelly)")
k2 = (0.135-0.1)/0.15
expect("arb-part2b.html", "Kelly 0.233", f"f*=(0.135-0.1)/0.15 = {k2:.3f} → Half-Kelly = {k2/2*100:.1f}% ของพอร์ต")
expect("arb-part2b.html", "funding 110%", f"+0.1%/8hr (≈{0.1*3*365:.0f}%/ปี แบบไม่ทบต้น!)")
fair = 900*math.exp((0.02-0.025)*0.25)
expect("arb-part4.html", "SET50 fair", f"900 × {math.exp(-0.00125):.5f} = <strong>{fair:.2f}</strong>")
expect("arb-part4.html", "SET50 overpriced", f"905-{fair:.2f} = <strong>{905-fair:.2f} จุด</strong>")
expect("arb-part4.html", "SET50 ฿/สัญญา", f"= ฿{round(905-fair,2)*200:,.0f} ต่อสัญญา")  # หนังสือคูณจากตัวเลขที่ปัดแล้ว 6.12
fair2 = 920*math.exp((0.02-0.025)*0.25)
expect("arb-part4.html", "SET50 ลองคิด", f"Fair={fair2:.2f} → Actual 930 overpriced {930-fair2:.2f} จุด (฿{round((930-fair2)*200):,} ต่อสัญญา)")
tri = 1000*0.92*0.86*1.28
expect("arb-part4.html", "triangular", f"$1,000 → €{1000*0.92:.0f} → £{1000*0.92*0.86:.2f} → ${tri:,.2f}")
expect("arb-part4.html", "triangular profit", f"= <strong>${tri-1000:.2f}</strong>")
expect("arb-part4.html", "triangular product", f"0.92 × 0.86 × 1.28 = {0.92*0.86*1.28:.5f} ส่วนเกิน {(0.92*0.86*1.28-1)*100:.2f}%")
expect("arb-part6.html", "merger spread", f"Spread = 50 - 47.50 = ฿{50-47.50:.2f} ({2.50/50*100:.0f}% ของราคาดีล ฿50)")
expect("arb-part6.html", "merger ฐานเงินลงจริง", f"2.50/47.50 = {2.50/47.50*100:.2f}%")
expect("arb-part6.html", "merger downside", f"เสีย ฿{47.50-35:.2f} ({(47.50-35)/47.50*100:.1f}% ของราคาที่ซื้อ ฿47.50!)")
expect("arb-part6.html", "merger breakeven p", f"ต้องมั่นใจ >{12.50/15*100:.1f}% ว่า deal จะสำเร็จ</strong> (P > 12.50/15 = {12.50/15*100:.1f}%)")
expect("arb-part6.html", "RV 1.6%", f"1.6% × {math.sqrt(252):.2f} ≈ {1.6*math.sqrt(252):.1f}%")
expect("arb-part6.html", "RV 2%", f"2%×√252={2*math.sqrt(252):.1f}% → overpriced 50-{2*math.sqrt(252):.1f}={50-2*math.sqrt(252):.1f} vol points")
expect("arb-part6.html", "spread 4/80", f"Spread ฿4/฿80={4/80*100:.0f}% ใน 6 เดือน → annualized={4/80*100*2:.0f}%")
expect("arb-part7.html", "฿2,000/(14×4)", f"฿2,000/(14×4)=฿{2000/56:.1f}/ครั้งที่เช็ค")
expect("arb-part8.html", "PM Yes+No 1.02", f"0.62 + 0.40 = {0.62+0.40:.2f} ไม่มี arb · 0.62 + 0.36 = {0.62+0.36:.2f}")
expect("arb-part8.html", "PM กำไร $0.02", f"กำไร ${1-0.98:.2f} ต่อชุด")
expect("arb-part8.html", "cross-platform 93¢", f"55¢ + ซื้อ No ที่ Polymarket 38¢ = {55+38}¢ < $1 → <strong>guaranteed ${(100-93)/100:.2f} profit/contract")
expect("arb-part5.html", "half-life 6.9", f"θ = 0.1 ต่อวันให้ {math.log(2):.3f}/0.1 ≈ {math.log(2)/0.1:.1f} วัน")

# ── ตาของ Arbitrageur (eye-part1…5) ─────────────────────────────────────────────
expect("eye-part1.html", "ทอง A/B", f"ราคาต่างกัน ฿{30500-30000}")
expect("eye-part1.html", "BTC A/B", f"ส่วนต่าง = ${67800-67500}")
expect("eye-part1.html", "PM 0.62 → %", f"= $0.62</td><td><strong>{0.62*100:.0f}%")
expect("eye-part1.html", "odds 1.65", f"1/1.65</td><td><strong>{round(1/1.65*100):.0f}%")
expect("eye-part1.html", "touch vs close gap", f"Gap {62-45}%")
expect("eye-part1.html", "ETH gap", f"gap {52-45}%")
expect("eye-part1.html", "synthetic", f"กำไร ฿{100-95}")
expect("eye-part2.html", "structured note", f"ต้นทุนจริง = 97 + 5 = <strong>฿{97+5}")
expect("eye-part2.html", "note markup", f"คุณจ่ายแพงเกิน ฿{105-102}!")
expect("eye-part2.html", "DW margin", f"issuer กิน ฿{1.50-1.20:.2f} ({(1.50-1.20)/1.20*100:.0f}% ของราคาทฤษฎี ฿1.20!)")
expect("eye-part2.html", "call spread S=2800", f"{2800-2000} − {2800-2500} = {500}")
p_ = [1/2.10, 1/3.30, 1/3.50]
expect("eye-part2.html", "overround", f"{p_[0]*100:.1f}% + {p_[1]*100:.1f}% + {p_[2]*100:.1f}% = <strong>{sum(p_)*100:.1f}%")
expect("eye-part2.html", "overround excess", f"ส่วนเกิน {sum(p_)*100-100:.1f}%")
expect("eye-part2.html", "de-vig", f"({p_[0]*100:.1f} → {p_[0]/sum(p_)*100:.1f}%)")
expect("eye-part2.html", "Fed gap", f"Gap {74-62}%")
expect("eye-part2.html", "X vs Y", f"ส่วนต่าง ${500-400}")
expect("eye-part3.html", "layers", f"{7} − {4} − {1} = {7-4-1}")
expect("eye-part3.html", "Earn net", f"11% - 5% funding cost = {11-5}% delta-neutral yield")
expect("eye-part3.html", "Earn marginal", f"marginal {11-5-4}%")
expect("eye-part3.html", "funding/day", f"-0.03%/8hr = -{0.03*3:.2f}%/day = -{0.03*3*365:.2f}%/year")
expect("eye-part3.html", "funding read", f"เท่ากับ ลบ {0.03*3*365:.2f}% ต่อปี")
expect("eye-part3.html", "funding periods", f"{3*365:,} รอบ")
expect("eye-part5.html", "Lloyd's", f"{2026-1688} ปีต่อมา")  # อิงปี 2026 ที่หนังสือเขียน


# ── ภาพ payoff ที่ generator วาด (tools/make_figures.py) — ตรวจว่าตัวเลขในหัวภาพ/ป้าย ตรงกับ payoff_lib ──
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from payoff_lib import Leg, summary  # noqa: E402

def pm(v):
    return f"{v:+g}".replace("-", "−")

def payoff_checks(file, label, legs, texts, with_premium=True):
    """texts = รายการ f-string template ที่ใช้ตัวแปร sm (dict จาก summary) · ทุกข้อความต้องอยู่ในไฟล์"""
    sm = summary(legs, with_premium=with_premium)
    for t in texts:
        expect(file, label, t(sm))

LC = [Leg("call", 100, 1, 5)]; LP = [Leg("put", 100, 1, 5)]
payoff_checks("pm-part0.html", "long call", LC, [lambda sm: f"BE = 100 + 5 = {sm['breakevens'][0]:g}", lambda sm: f"ขาดทุนสูงสุด {pm(sm['max_loss'])}"])
payoff_checks("pm-part0.html", "put pair", LP, [lambda sm: f"BE ทั้งคู่ = 100 − 5 = {sm['breakevens'][0]:g}", lambda sm: f"ขาดทุนสูงสุด {pm(sm['max_loss'])}"])
payoff_checks("pm-part0.html", "bull call spread 90/110 net 5", [Leg("call", 100, 1, 0), Leg("call", 110, -1, 0)],
              [lambda sm: f"payoff สูงสุด {pm(sm['max_profit'])}"], with_premium=False)
payoff_checks("pm-part2.html", "BCS 90@8/110@3", [Leg("call", 90, 1, 8), Leg("call", 110, -1, 3)],
              [lambda sm: f"เบี้ยสุทธิ {sm['net_premium']:g}", lambda sm: f"BE {sm['breakevens'][0]:g}", lambda sm: f"กำไรสูงสุด {pm(sm['max_profit'])}",
               lambda sm: f"ขาดทุนสูงสุด {pm(sm['max_loss'])}", lambda sm: f"−5 + 20 = {pm(sm['max_profit'])}"])
payoff_checks("pm-part2.html", "straddle", [Leg("call", 100, 1, 5), Leg("put", 100, 1, 5)],
              [lambda sm: f"BE {sm['breakevens'][0]:g}", lambda sm: f"BE {sm['breakevens'][1]:g}", lambda sm: f"ขาดทุนสูงสุด {pm(sm['max_loss'])}"])
payoff_checks("pm-part2.html", "covered call", [Leg("stock", 100, 1, 0), Leg("call", 100, -1, 5)],
              [lambda sm: f"BE {sm['breakevens'][0]:g}", lambda sm: f"กำไรสูงสุด {pm(sm['max_profit'])}", lambda sm: f"ขาดทุนสูงสุด {pm(sm['max_loss'])} (ที่ S = 0)"])
payoff_checks("pm-part2.html", "collar", [Leg("stock", 100, 1, 0), Leg("put", 90, 1, 3), Leg("call", 110, -1, 3)],
              [lambda sm: f"กำไรสูงสุด {pm(sm['max_profit'])}", lambda sm: f"ขาดทุนสูงสุด {pm(sm['max_loss'])}"])
BF = [Leg("call", 90, 1, 12), Leg("call", 100, -2, 6), Leg("call", 110, 1, 3)]
for f in ("pm-part3.html", "pm-part3a.html"):
    payoff_checks(f, "butterfly 90/100/110", BF, [lambda sm: f"เบี้ยสุทธิ {sm['net_premium']:g}", lambda sm: f"10 − 3 = {pm(sm['max_profit'])}" if f == "pm-part3.html" else f"−3 + 10 = {pm(sm['max_profit'])}",
                                                 lambda sm: f"BE {sm['breakevens'][0]:g}", lambda sm: f"BE {sm['breakevens'][1]:g}", lambda sm: f"ขาดทุนสูงสุด {pm(sm['max_loss'])}"])
payoff_checks("pm-part3.html", "iron condor", [Leg("put", 90, 1, 1), Leg("put", 95, -1, 2), Leg("call", 105, -1, 2), Leg("call", 110, 1, 1)],
              [lambda sm: f"เบี้ยสุทธิที่รับ {-sm['net_premium']:g}", lambda sm: f"−(ความกว้าง 5 − เบี้ย 2) = {pm(sm['max_loss'])}", lambda sm: f"BE {sm['breakevens'][0]:g}", lambda sm: f"BE {sm['breakevens'][1]:g}"])
payoff_checks("pm-part3.html", "ratio 1x2", [Leg("call", 100, 1, 0), Leg("call", 110, -2, 0)],
              [lambda sm: f"payoff สูงสุด {pm(sm['max_profit'])}", lambda sm: f"ตัดศูนย์ {sm['breakevens'][-1]:g}"], with_premium=False)
payoff_checks("pm-part3a.html", "3x cap", [Leg("call", 100, 3, 0), Leg("call", 110, -3, 0)], [lambda sm: f"3 × 10 = {sm['max_profit']:g}"], with_premium=False)
payoff_checks("pm-part8.html", "DW cap", [Leg("call", 100, 1, 6), Leg("call", 120, -1, 0)],
              [lambda sm: f"BE {sm['breakevens'][0]:g}", lambda sm: f"กำไรสูงสุด {pm(sm['max_profit'])}", lambda sm: f"ขาดทุนสูงสุด {pm(sm['max_loss'])}"])



def main():
    if "--print" in sys.argv:
        return 0
    bad = 0
    cache = {}
    for f, label, text in CHECKS:
        path = os.path.join(DOCS, f)
        if path not in cache:
            cache[path] = open(path, encoding="utf-8").read()
        if text not in cache[path]:
            print(f"❌ {f} · {label}: ไม่พบ \"{text}\""); bad += 1
    print(f"\nตรวจ {len(CHECKS)} ค่าใน {len(cache)} ไฟล์ · ไม่ตรง {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
