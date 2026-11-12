#!/usr/bin/env python3
"""เตรียมบทให้ persona มือใหม่ (gate P1) และตรวจคำตอบของ persona

แนวคำตอบ <details class="ans"> และ 🔎 <details class="deep"> อยู่ในไฟล์บทเดียวกัน — subagent ที่อ่าน HTML ดิบ
จะเห็นทันที จึงต้องลบออกก่อนส่งบท

    python3 tools/sab_persona_strip.py part4 > /tmp/persona/sab-part4.html      # บทที่ไม่มีเฉลยและ 🔎
    python3 tools/sab_persona_strip.py --grade part4 answers.json               # เทียบกับ แบบฝึก.ch04 ใน JSON
    python3 tools/sab_persona_strip.py --selftest

answers.json ที่ persona เขียน: {"1": "ข้อความคำตอบ", "2": "...", "3": "..."}
แบบฝึก.chNN ใน docs/sab-figures.json: รายการ 3 ข้อ · ข้อที่มีคีย์ "คำตอบ" (ตัวเลขหรือรายการตัวเลข) ตรวจด้วยสคริปต์
(ปัดค่าจริงตามจำนวนทศนิยมที่ผู้ตอบให้) · ข้อที่ไม่มี "คำตอบ" = ข้ออธิบาย/ถ่ายโอน ให้ผู้ตรวจเลนส์มือใหม่ให้คะแนน
P1 ผ่านเมื่อข้อถูก ≥ 2 จาก 3
"""

import json
import os
import re
import sys
import tempfile
from decimal import Decimal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
FIG = os.path.join(DOCS, "sab-figures.json")


def strip_details(html):
    """ลบ <details class="ans|deep"> ทั้งก้อน (นับชั้น details ซ้อน)"""
    out, i = [], 0
    pat = re.compile(r"<details\b[^>]*class=\"[^\"]*\b(ans|deep)\b[^\"]*\"[^>]*>", re.S)
    while True:
        m = pat.search(html, i)
        if not m:
            out.append(html[i:])
            break
        out.append(html[i:m.start()])
        depth, j = 1, m.end()
        for t in re.finditer(r"<(/?)details\b[^>]*>", html[m.end():]):
            depth += -1 if t.group(1) else 1
            if depth == 0:
                j = m.end() + t.end()
                break
        else:
            j = len(html)
        i = j
    return "".join(out)


def nums(text):
    t = str(text).replace("−", "-")
    t = re.sub(r"(?<=\d),(?=\d{3})", "", t)
    return [Decimal(x) for x in re.findall(r"-?\d+(?:\.\d+)?", t)]


def close(got, want):
    """ถูกเมื่อค่าที่ตอบเท่าค่าจริงที่ปัดเท่าจำนวนทศนิยมที่ผู้ตอบให้ (13.3 ↔ 13.34 ถูก · 11,200 ↔ 11,220 ผิด)"""
    places = max(0, -got.as_tuple().exponent)
    return want.quantize(Decimal(1).scaleb(-places)) == got


def grade(expected, answers):
    """คืน (ถูก, ตรวจด้วยสคริปต์ได้, รายละเอียด)"""
    right, auto, detail = 0, 0, []
    for i, item in enumerate(expected, 1):
        want = item.get("คำตอบ") if isinstance(item, dict) else None
        got = answers.get(str(i), "")
        if want is None:
            detail.append(f"ข้อ {i}: ข้ออธิบาย — ให้ผู้ตรวจเลนส์มือใหม่ให้คะแนน")
            continue
        auto += 1
        want = want if isinstance(want, list) else [want]
        have = nums(got)
        ok = all(any(close(h, Decimal(str(w))) or close(-h, Decimal(str(w))) for h in have) for w in want)
        right += ok
        detail.append(f"ข้อ {i}: {'ถูก' if ok else 'ผิด'} (ต้องมี {want} · ตอบ {got[:60]!r})")
    return right, auto, detail


def selftest():
    html = ('<p>บท</p><details class="deep"><summary>🔎</summary><p>σ</p><details><summary>ซ้อน</summary>x</details></details>'
            '<ol><li>ข้อ<details class="ans"><summary>แนวคำตอบ</summary>11,220</details></li></ol><p>ท้าย</p>')
    s = strip_details(html)
    ok = "σ" not in s and "11,220" not in s and "ท้าย" in s and "ข้อ" in s and "ซ้อน" not in s
    exp = [{"คำตอบ": 11220}, {"คำตอบ": [13.0, -200]}, {"โจทย์": "อธิบาย"}]
    r, a, _ = grade(exp, {"1": "ต้องโอน 11,220 ดอลลาร์", "2": "กันชน 13% แต่ equity −200", "3": "เพราะ..."})
    r2, _, _ = grade(exp, {"1": "11,200", "2": "13"})
    ok = ok and (r, a) == (2, 2) and r2 == 0
    with tempfile.TemporaryDirectory():
        pass
    print("selftest", "ผ่าน ✓ (ลบเฉลย/🔎 รวม details ซ้อน · ตรวจคำตอบตัวเลข comma/U+2212)" if ok else "ไม่ผ่าน ✗")
    return 0 if ok else 1


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--selftest"]:
        sys.exit(selftest())
    if len(a) == 3 and a[0] == "--grade":
        part, ans_path = a[1], a[2]
        n = int(re.fullmatch(r"part(\d+)", part).group(1))
        with open(FIG, encoding="utf-8") as fh:
            expected = json.load(fh).get("แบบฝึก", {}).get(f"ch{n:02d}") or []
        with open(ans_path, encoding="utf-8") as fh:
            answers = json.load(fh)
        r, auto, detail = grade(expected, answers)
        print("\n".join(detail))
        print(f"P1 บท {n}: ถูก {r}/{auto} ข้อที่ตรวจด้วยสคริปต์ (เกณฑ์รวม ≥ 2/3 รวมคะแนนข้ออธิบายจากผู้ตรวจ)")
        sys.exit(0)
    if len(a) == 1 and re.fullmatch(r"part\d+", a[0]):
        with open(os.path.join(DOCS, f"sab-{a[0]}.html"), encoding="utf-8") as fh:
            sys.stdout.write(strip_details(fh.read()))
        sys.exit(0)
    print(__doc__)
    sys.exit(1)
