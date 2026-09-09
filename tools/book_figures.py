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
