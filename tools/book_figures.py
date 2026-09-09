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
