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
