#!/usr/bin/env python3
"""รายการสิ่งที่ต้องทำเพื่อย้ายบทเป็นแม่แบบ v2 (แผน 14.3) — รายงานอย่างเดียว ไม่เขียนไฟล์

รันกฎ V1–V8 ของ tools/sab_qa.py กับหน้าเดิมโดยไม่สนป้าย <body data-tpl="2"> แล้วพิมพ์เป็นรายการให้ผู้เขียนไล่ทำ:
ป้าย/กล่องที่เลิกใช้ที่ยังอยู่ · ตอน <h2> ที่ยังไม่มี .rest · กราฟที่ยังไม่มี .readfig · สูตรที่ยังไม่มี .readeq ·
จำนวนแบบฝึก/คำใบ้/เฉลย · ย่อหน้าที่มี "=" เกินสอง (พร้อมข้อความต้นย่อหน้า) · จำนวนศัพท์ใน 📖 · งบคำแบบ v2 (แผน 14.4)

    python3 tools/sab_migrate_v2.py part4      # หรือ: part 4
    python3 tools/sab_migrate_v2.py base1

[x] = ผ่านเกณฑ์ v2 แล้ว · [ ] = ยังต้องทำ · หลังย้ายเสร็จให้ตรวจจริงด้วย python3 tools/sab_qa.py --scope partN --final
งบคำนับด้วย node tools/sab_wordcount.mjs --as-v2 (ถ้ารัน node ไม่ได้ จะประมาณสัดส่วนจากจำนวนอักษรแทน)
"""

import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sab_qa as Q  # noqa: E402


def char_share(html):
    """ประมาณสัดส่วนเส้นทางหลักแบบ v2 จากจำนวนอักษร (ใช้เมื่อรัน node ไม่ได้)"""
    def size(h):
        return len(re.sub(r"\s+", "", Q.text_of(h)))
    page = Q.cut(html, Q.blocks(html, lambda t, a: Q.has_class(a, "cover")))
    off = Q.blocks(page, lambda t, a: t == "details" or Q.has_class(a, "sheet")
                   or (t == "table" and (Q.has_class(a, "ledger") or Q.has_class(a, "ncard"))))
    off += Q.box_spans(page, "📖")
    return size(Q.cut(page, off)), size(page)


def word_budget(slug, html):
    """บรรทัดรายงานงบคำแบบ v2 → (ผ่านไหม | None ถ้านับไม่ได้, [บรรทัด])"""
    tool = os.path.join(Q.ROOT, "tools", "sab_wordcount.mjs")
    try:
        r = subprocess.run(["node", tool, "--as-v2", slug], capture_output=True, text=True, timeout=180)
        lines = [ln for ln in r.stdout.splitlines() if ln.strip()]
        if r.returncode in (0, 1) and lines and lines[0].startswith(f"sab-{slug}.html:"):
            return r.returncode == 0, [lines[0].split(": ", 1)[1]] + lines[1:]
        why = (r.stderr.strip().splitlines() or ["ไม่มีผลลัพธ์"])[-1]
    except (OSError, subprocess.TimeoutExpired) as e:
        why = repr(e)
    main, page = char_share(html)
    pct = round(100 * main / page) if page else 0
    return None, [f"นับคำด้วย node ไม่ได้ ({why}) — ประมาณจากจำนวนอักษร: เส้นทางหลัก {pct}% ของหน้า (v2 ต้อง ≥ 65% ของคำ)"]


def report(slug):
    name = f"sab-{slug}.html"
    n, b = Q.part_no(name), Q.base_no(name)
    path = os.path.join(Q.DOCS, name)
    if (n is None and b is None) or not os.path.exists(path):
        print(f"ไม่พบหน้าสอน docs/{name} (ใช้ partN หรือ baseN)")
        return 2
    kind, num = ("part", n) if n is not None else ("base", b)
    with open(path, encoding="utf-8") as fh:
        html = fh.read()
    S = Q.audit_v2(html, kind, num)["stats"]
    todo = 0

    def item(ok, text, details=()):
        nonlocal todo
        todo += 0 if ok else 1
        print(f"[{'x' if ok else ' '}] {text}")
        for d in details:
            print(f"      - {d}")

    print(f"รายการย้าย docs/{name} → แม่แบบ v2 (แผน 14.3 · รายงานอย่างเดียว ไม่เขียนไฟล์)")
    item(Q.is_v2(html), 'ป้ายแม่แบบ <body data-tpl="2">' + ("" if Q.is_v2(html) else " — ยังเป็น v1 (ใส่เมื่อย้ายเสร็จ ตัวตรวจจะสลับไปใช้กฎ v2)"))

    sheets = len(Q.blocks(html, lambda t, a: t == "div" and Q.has_class(a, "sheet")))
    miss = list(S["ขาด"])
    if kind == "part" and S["แฟ้ม"] != 1:
        miss.append(f"details.file 📁 แฟ้มของบทนี้ (พบ {S['แฟ้ม']} · ต้องมีหนึ่งบล็อก)")
    if kind == "part" and S["ใบงานในแฟ้ม"] < 1:
        miss.append(f".sheet ใน details.file (ตอนนี้มีใบงาน {sheets} ใบ อยู่นอกแฟ้ม)")
    item(not miss, "V1 โครงบังคับ" + (" ครบ" if not miss else f" — ยังขาด {len(miss)} อย่าง"), miss)

    item(not S["เลิกใช้"], "V8 ป้าย/คำที่เลิกใช้" + (" ไม่เหลือ" if not S["เลิกใช้"] else f" ยังอยู่ {len(S['เลิกใช้'])} อย่าง: "
                                                    + " · ".join(S["เลิกใช้"])))
    item(S["ตอน"] > 0 and not S["ตอนไม่มีrest"],
         f"V2 ตอนสอน <h2> {S['ตอน']} ตอน · ยังไม่มี .rest \"พักตรงนี้ได้\" {len(S['ตอนไม่มีrest'])} ตอน",
         [f"บรรทัด {ln}: {t}" for ln, t in S["ตอนไม่มีrest"]])
    item(not S["กราฟไม่มีreadfig"], f"V3 กราฟ .figw {S['กราฟ']} รูป · ยังไม่มี .readfig \"อ่านภาพ:\" {len(S['กราฟไม่มีreadfig'])} รูป",
         [f"บรรทัด {ln}: {t}" for ln, t in S["กราฟไม่มีreadfig"]])
    item(not S["สูตรไม่มีreadeq"], f"V4 สูตร .fm นอกบล็อกพับ {S['สูตร']} สูตร · ยังไม่มี .readeq \"อ่านสมการ:\" {len(S['สูตรไม่มีreadeq'])} สูตร",
         [f"บรรทัด {ln}: {t}" for ln, t in S["สูตรไม่มีreadeq"]])
    ex = S["แบบฝึก"]
    item(ex["ข้อ"] >= ex["ต้อง"] and not ex["ไม่มีเฉลย"] and ex["มีคำใบ้"] >= ex["ต้องมีคำใบ้"],
         f"V5 ✍️ แบบฝึก {ex['ข้อ']} ข้อ (ต้อง ≥ {ex['ต้อง']}) · มี details.hint {ex['มีคำใบ้']} ข้อ (ต้อง ≥ {ex['ต้องมีคำใบ้']}) · "
         + ("มี details.ans ครบทุกข้อ" if not ex["ไม่มีเฉลย"] else "ข้อที่ไม่มี details.ans: " + ", ".join(map(str, ex["ไม่มีเฉลย"]))))
    item(not S["ย่อหน้าเกิน="], f"V6 ย่อหน้าบรรยายที่มี \"=\" เกิน {Q.EQ_MAX} ตัว: {len(S['ย่อหน้าเกิน='])} ย่อหน้า"
         + (" (แตกเป็นหลายประโยค หรือย้ายลงตารางที่มีคอลัมน์ \"คิดอย่างไร\")" if S["ย่อหน้าเกิน="] else ""),
         [f"บรรทัด {ln} ({k} ตัว): {q}" for ln, k, q in S["ย่อหน้าเกิน="]])
    over = S["ศัพท์"] - S["เพดานศัพท์"]
    item(over <= 0, f"V7 📖 ศัพท์ใหม่ {S['ศัพท์']} คำ (เพดาน {S['เพดานศัพท์']})" + (f" — ต้องลด/ย้าย {over} คำ" if over > 0 else ""))
    ok, lines = word_budget(slug, html)
    item(bool(ok), "งบคำแบบ v2 (แผน 14.4): " + lines[0], [ln.strip(" -") for ln in lines[1:]])
    print(f"สรุป: ยังต้องทำ {todo} หัวข้อ จาก 10 · กฎเดิมที่ยังใช้กับหน้า v2 (W11–W16 · W18–W23 · W25 · D1) ดูจาก sab_qa.py หลังใส่ป้าย")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    slug = "".join(a) if len(a) == 2 and a[1].isdigit() else (a[0] if len(a) == 1 else "")
    if not re.fullmatch(r"(part|base)\d+", slug):
        print(__doc__)
        sys.exit(2)
    sys.exit(report(slug))
