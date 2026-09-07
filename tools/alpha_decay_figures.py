#!/usr/bin/env python3
"""สร้าง docs/alpha-decay-figures.json — ตัวเลขของบท "edge เสื่อม — แยกจาก drawdown ปกติยังไง"

ใช้สูตรเดียวกับ nq-tool-samplesize.html (power calculation แบบ one-sample proportion test
ที่ประมาณ variance ด้วยค่าใต้ null p0 ทั้งสองพจน์ — เป็นค่าประมาณที่นิยมใช้เพราะเรียบง่ายกว่า
สูตรที่แยก variance ของ p1 ออกมาต่างหาก) ขยายจากกรณีพิเศษ p0=0.5 (ตรวจจับว่ามี edge ไหม)
ไปเป็นกรณีทั่วไป p0→p1 (ตรวจจับว่า edge เสื่อมไหม)

    n = (z_alpha + z_beta)² · p0(1-p0) / (p0-p1)²

z_alpha=2 (~97.5% ทาง), z_beta=1.2816 (90% power) — ค่าเดียวกับเครื่องมือ sample-size
ตรวจแล้วว่าที่ p0=0.5 สูตรนี้ลดรูปกลับไปเป็นสูตรของเครื่องมือเดิมพอดี

    python3 tools/alpha_decay_figures.py
"""

import json
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "alpha-decay-figures.json")
Z_ALPHA, Z_BETA = 2.0, 1.2816
TRADES_PER_WEEK = 2   # MIN_ACCOUNT["ไม้ต่อสัปดาห์"] ใน nq_figures.py — golden thread เดียวกัน


def required_n(p0, p1):
    return math.ceil(((Z_ALPHA + Z_BETA) ** 2) * p0 * (1 - p0) / ((p0 - p1) ** 2))


def to_time(n, trades_per_week=TRADES_PER_WEEK):
    weeks = n / trades_per_week
    return {"จำนวนไม้": n, "สัปดาห์": round(weeks, 1), "ปี": round(weeks / 52, 1)}


def build():
    # ตรวจว่าลดรูปกลับไปเป็นสูตรเดิมของ nq-tool-samplesize ได้จริงที่ p0=0.5
    check_p055 = required_n(0.5, 0.55)
    tool_formula_p055 = math.ceil(((Z_ALPHA + Z_BETA) ** 2) * 0.25 / (0.05 ** 2))

    pairs = [
        (0.55, 0.54), (0.55, 0.52), (0.55, 0.50), (0.55, 0.48),
        (0.60, 0.58), (0.60, 0.55), (0.60, 0.50),
    ]
    table = []
    for p0, p1 in pairs:
        n = required_n(p0, p1)
        table.append({
            "edgeเดิมเปอร์เซ็นต์": round(100 * p0, 1),
            "edgeหลังเสื่อมเปอร์เซ็นต์": round(100 * p1, 1),
            "ลดลงจุด": round(100 * (p0 - p1), 1),
            **to_time(n),
        })

    headline = required_n(0.55, 0.50)   # กรณีตั้งต้นของบท: edge 55% เสื่อมเหลือ 50%

    return {
        "_อ่านก่อน": "สร้างด้วย tools/alpha_decay_figures.py — ห้ามแก้ด้วยมือ",
        "สูตร": {
            "คำอธิบาย": "one-sample proportion test power calculation (variance ประมาณด้วย p0 ทั้งสองพจน์) ขยายจาก nq-tool-samplesize (กรณีพิเศษ p0=0.5)",
            "z_alpha": Z_ALPHA, "z_beta": Z_BETA,
            "ตรวจลดรูปที่p0เท่ากับ0.5": {"สูตรทั่วไป": check_p055, "สูตรเครื่องมือเดิม": tool_formula_p055,
                                          "ตรงกัน": check_p055 == tool_formula_p055},
        },
        "สมมติฐานจังหวะเทรดของมิน": {"ไม้ต่อสัปดาห์": TRADES_PER_WEEK, "ที่มา": "MIN_ACCOUNT ใน nq_figures.py (golden thread เดียวกันทั้งเล่ม)"},
        "กรณีตั้งต้นของบท": {"edgeเดิมเปอร์เซ็นต์": 55, "edgeหลังเสื่อมเปอร์เซ็นต์": 50, **to_time(headline)},
        "ตารางตรวจจับ": table,
    }


if __name__ == "__main__":
    with open(OUT, "w") as fh:
        json.dump(build(), fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("เขียน", os.path.relpath(OUT, ROOT))
