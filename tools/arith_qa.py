#!/usr/bin/env python3
"""ตรวจเลขคณิตที่เขียนในข้อความ — คำนวณซ้ำแล้วเทียบกับที่พิมพ์ไว้

ทำไมต้องมี: คลังนี้มีเครื่องมือทวนตัวเลขที่ "สร้างจากข้อมูล" อยู่แล้ว
(math_figures · book_figures · nq_check_figures) แต่ **เลขคณิตที่เดินมือในข้อความ**
ไม่เคยมีใครตรวจ · บทที่ตัวเลขหนาแน่นที่สุดอย่าง math-part10 (551 ตัวเลข)
ไม่มี expect() แม้แต่ตัวเดียว

ตรวจอะไร: ลูกโซ่ความเท่ากัน  A = B = C  ต้องให้ค่าตรงกันทุกท่อนที่คำนวณได้
    "0.50×4 + ½×0.05×16 = 2.0 + 0.4 = +2.4"   → ตรวจทั้งสามท่อน
ลำดับความสำคัญ: × ÷ ก่อน + − · เปอร์เซ็นต์อ่านเป็นหน่วยเดียวกันทั้งสมการ
(ธรรมเนียมการเขียนของคลังนี้ เช่น "2% + 1.5 × 7% = 12.5%")

ข้ามอะไร:
  - สูตรใน .fm · โค้ด · SVG
  - "ชื่อ" ที่หน้าตาเหมือนการหาร เขียนติดกันไม่เว้นวรรค เช่น RSI 70/30 · 60/40 portfolio
  - สมการที่มีสัญลักษณ์เกินกว่าที่ตัวตรวจอ่านได้ (√ ² ³ ^ ½ e π …) — ถ้าอ่านไม่ครบ
    แล้วยังตรวจ จะคว้าแค่ตัวเลขท้ายสมการมาเทียบ กลายเป็นเตือนผิดทุกครั้ง

ใช้:  python3 tools/arith_qa.py            → ทั้งคลัง
      python3 tools/arith_qa.py math-part10
"""
import glob
import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")

NUM = r'[−–-]?\$?\d[\d,]*(?:\.\d+)?%?'
OP = r'[×*÷/+−]'
TERM = rf'{NUM}(?:\s*{OP}\s*{NUM})*'
CHAIN = re.compile(rf'({TERM}(?:\s*=\s*{TERM}){{1,4}})')
TOL = 0.015
# สัญลักษณ์ที่ตัวตรวจอ่านไม่ได้ — เจอในบริบทเมื่อไร ข้ามสมการนั้นทั้งอัน
UNSUPPORTED = set("√²³⁴⁵ⁿ^½¼¾πΣ∏∫…⁻⁰¹⁶⁷⁸⁹ᐟ")
# ถ้าตัวอักษรก่อนหน้าเป็นตัวดำเนินการหรือวงเล็บเปิด แปลว่า regex ไปเริ่มจับกลางสมการ
# (เช่น "(1.8 − 0.6) × 3.24% = 3.9%" จะจับได้แค่ "3.24% = 3.9%") — ต้องข้าม
MID_EXPR = set("×*÷/+−-()^√·")


def _val(tok):
    t = tok.replace(",", "").replace("−", "-").replace("–", "-").replace("$", "").strip()
    if t.endswith("%"):
        t = t[:-1]
    try:
        return float(t)
    except ValueError:
        return None


def evaluate(expr):
    toks = re.findall(rf'{NUM}|{OP}', expr)
    nums, ops = [], []
    for t in toks:
        if re.fullmatch(OP, t):
            ops.append(t)
        else:
            v = _val(t)
            if v is None:
                return None
            nums.append(v)
    if len(nums) != len(ops) + 1:
        return None
    i = 0
    while i < len(ops):
        if ops[i] in "×*÷/":
            a, b = nums[i], nums[i + 1]
            if ops[i] in "÷/" and b == 0:
                return None
            nums[i:i + 2] = [a * b if ops[i] in "×*" else a / b]
            ops.pop(i)
        else:
            i += 1
    r = nums[0]
    for i, o in enumerate(ops):
        r = r + nums[i + 1] if o == "+" else r - nums[i + 1]
    return r


def _is_name(part):
    """'70/30' ที่เขียนติดกันคือชื่อเกณฑ์ ไม่ใช่การหาร — คลังนี้เขียนการหารแบบเว้นวรรค"""
    return bool(re.fullmatch(r'\d+/\d+', part.strip()))


def text_of(path):
    s = open(path, encoding="utf-8").read()
    s = re.sub(r'<(script|style|svg).*?</\1>', " ", s, flags=re.S)
    s = re.sub(r'<div class="fm">.*?</div>', " ", s, flags=re.S)   # สูตรสัญลักษณ์ ไม่ใช่เลขคณิต
    s = re.sub(r'<code\b.*?</code>', " ", s, flags=re.S)
    # เลขยกกำลังเขียนเป็น <sup> — ถ้าถอดแท็กเฉย ๆ มันจะกลายเป็นตัวเลขธรรมดา
    # ทำให้ "e<sup>−0.05</sup>" อ่านเป็น "e −0.05" แล้วตัวตรวจไปจับ −0.05 มาคิด
    s = re.sub(r'<sup\b[^>]*>.*?</sup>', "^", s, flags=re.S)
    return html.unescape(re.sub(r'<[^>]+>', " ", s))


def check(path):
    bad, t = [], text_of(path)
    for m in CHAIN.finditer(t):
        parts = [p.strip() for p in m.group(1).split("=")]
        if len(parts) < 2 or any(_is_name(p) for p in parts):
            continue
        # ดูบริบทรอบ ๆ ด้วย เพราะสัญลักษณ์ที่อ่านไม่ได้มักอยู่นอกช่วงที่ regex จับได้
        window = t[max(0, m.start() - 45):m.end() + 8]
        if UNSUPPORTED & set(window):
            continue
        before = t[:m.start()].rstrip()
        if before and before[-1] in MID_EXPR:
            continue
        # ฝั่งซ้ายสุดต้องเป็น "สมการ" จริง (มีตัวดำเนินการ) · ถ้าเป็นตัวเลขเปล่า
        # แปลว่าไปจับป้ายกำกับหรือการกำหนดค่ามา เช่น VaR99 = … · S = 0 = … · Δs@100 = −1
        if not re.search(OP, parts[0]):
            continue
        vals = [(p, evaluate(p)) for p in parts]
        vals = [(p, v) for p, v in vals if v is not None]
        if len(vals) < 2:
            continue
        ref = vals[0][1]
        for p, v in vals[1:]:
            # 0.3333 กับ 33.3% คือค่าเดียวกัน คนละหน่วย — คลังนี้สลับใช้ตามบริบท
            same = (abs(v - ref) <= max(abs(ref) * TOL, 5e-3)
                    or abs(v - ref * 100) <= max(abs(ref * 100) * TOL, 5e-3)
                    or abs(v * 100 - ref) <= max(abs(ref) * TOL, 5e-3))
            if not same:
                ctx = re.sub(r'\s+', " ", t[max(0, m.start() - 60):m.end() + 40])
                bad.append((m.group(1).strip(), vals[0][0], ref, p, v, ctx))
                break
    return bad


def main(argv):
    files = [os.path.join(DOCS, a if a.endswith(".html") else a + ".html") for a in argv] \
        or sorted(glob.glob(os.path.join(DOCS, "*.html")))
    tot = 0
    for f in files:
        bad = check(f)
        if not bad:
            continue
        print(f"\n❌ {os.path.basename(f)} — {len(bad)} จุด")
        for chain, p0, v0, p1, v1, ctx in bad[:10]:
            print(f"   {chain}")
            print(f"      '{p0}' = {v0:,.6g}  แต่  '{p1}' = {v1:,.6g}")
            print(f"      …{ctx}…")
        tot += len(bad)
    print(f"\nตรวจ {len(files)} ไฟล์ · เลขคณิตในข้อความที่ไม่ตรง {tot} จุด")
    return 1 if tot else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
