#!/usr/bin/env python3
"""แปลง "รายการปลอม" (<br> + • / ✓ / 1.) ให้เป็น <ul>/<ol> จริง

ทำไมต้องแก้: style guide หมวด B และกฎเหล็กของ skill เขียนไว้ว่า
"รายการใช้ <ul> จริง ห้าม <br> ปลอม (ตัวการทำบรรทัดไทยตัดกลางคำ)"
บนจอกว้างรายการปลอมดูปกติ แต่บนมือถือบรรทัดที่ตัดขึ้นบรรทัดใหม่จะ
ชิดซ้ายเท่ากับหัวข้อย่อย จนแยกไม่ออกว่าข้อไหนจบข้อไหนเริ่ม

การแปลง (รักษาถ้อยคำเดิมทุกตัวอักษร เปลี่ยนแค่โครงสร้าง):
    <p>นำ:<br> • ก<br> • ข<br><br> ท้าย</p>
  → <p>นำ:</p> <ul><li>ก</li><li>ข</li></ul> <p>ท้าย</p>
  • ถูกตัดทิ้ง (ใช้จุดของ <ul> แทน) · 1. 2. 3. → <ol> · ✓ ✗ คงไว้ในข้อความ
  (คลังใช้ <li>✓ … อยู่แล้วใน theory-part1/2/5)

ใช้:  python3 tools/fix_fake_lists.py            → ดูว่าจะแก้อะไร (ไม่เขียนไฟล์)
      python3 tools/fix_fake_lists.py --write    → เขียนจริง
      python3 tools/fix_fake_lists.py --write pm-part3a arb-part1
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")

P_BLOCK = re.compile(r'(<p(?![a-z])[^>]*>)((?:(?!</?p[ >]).)*?)(</p>)', re.S)
BR = re.compile(r'<br\s*/?>')
# เครื่องหมายอาจอยู่ข้างในแท็ก inline เช่น <strong>• Premium</strong> — ต้องข้ามแท็กนำก่อน
INLINE_OPEN = r'(?:<(?:strong|em|b|i|code|span|abbr|a)\b[^>]*>\s*)*'
# → นับเป็นเครื่องหมายหัวข้อ **เฉพาะเมื่ออยู่ต้นส่วนที่คั่นด้วย <br>** เท่านั้น
# (กลางประโยค → แปลว่า "นำไปสู่" ซึ่งเป็นการใช้ปกติ · regex นี้ผูกกับ ^ จึงไม่โดน)
MARK = re.compile(r'^\s*(' + INLINE_OPEN + r')\s*(?:(•|✓|✗|◦|–|→|⇒)|(\d+)\.)\s+(.*)$', re.S)
# รายการอีกแบบ: "หัวข้อ" เป็นตัวหนาแทนเครื่องหมาย — <strong>Step 1 — Observe:</strong> …
# ต้องมี ≥ MIN_LABEL ข้อ ถึงจะถือว่าเป็นรายการ (กันโครงสร้างสองบรรทัดที่ตั้งใจ เช่น
# "มือใหม่เห็น / quant เห็น" ในกล่อง 🧠)
LABEL = re.compile(r'^\s*<(strong|b)\b[^>]*>(?:(?!</\1>).)+</\1>\s*[:：]?', re.S)
MIN_LABEL = 3
MIN_ARROW = 2            # → ต้องมีอย่างน้อยสองข้อติดกัน ถึงจะนับเป็นรายการ
# บางรายการเป็น "ลูกโซ่" — คั่นแต่ละข้อด้วยลูกศรตัวเดียวโดด ๆ
# ลูกศรพวกนี้ไม่ใช่ข้อของรายการ และไม่ใช่ตัวจบรายการ แต่คือลำดับ → ใช้ <ol> แทน
CONNECTOR = re.compile(r'^\s*(?:<[^>]+>\s*)*[↓⇓→⇒]\s*(?:</[^>]+>\s*)*$')


def convert_block(open_tag, body):
    """คืน HTML ใหม่ หรือ None ถ้าบล็อกนี้ไม่ใช่รายการปลอม"""
    if not BR.search(body):
        return None
    segs = [s.strip() for s in BR.split(body)]
    parsed = []
    for s in segs:
        if not s:
            parsed.append(("gap", None, ""))
            continue
        if CONNECTOR.match(s):
            parsed.append(("chain", None, ""))
            continue
        m = MARK.match(s)
        if m:
            pre, sym, num, rest = m.groups()
            # → กำกวมกว่าเครื่องหมายอื่น — แยกชนิดไว้ก่อน แล้วค่อยกรองด้วยความยาวรัน
            kind = "num" if num else ("keep" if sym in "✓✗" else ("arr" if sym in "→⇒" else "bul"))
            # คืนแท็ก inline ที่นำหน้าเครื่องหมายกลับเข้าไป (เช่น <strong> ที่ครอบ "• Premium")
            parsed.append((kind, sym, (pre or "") + rest.strip()))
        else:
            parsed.append(("text", None, s))
    # → ที่โดดเดี่ยวไม่ใช่รายการ แต่เป็นการเชื่อมความในย่อหน้า — คืนให้เป็นข้อความ
    i = 0
    while i < len(parsed):
        if parsed[i][0] != "arr":
            i += 1
            continue
        j = i
        while j < len(parsed) and parsed[j][0] == "arr":
            j += 1
        if j - i >= MIN_ARROW:
            for k in range(i, j):
                parsed[k] = ("bul", parsed[k][1], parsed[k][2])
        else:
            for k in range(i, j):
                sym, t = parsed[k][1], parsed[k][2]
                parsed[k] = ("text", None, f"{sym} {t}")
        i = j

    if not any(k in ("num", "bul", "keep") for k, _, _ in parsed):
        # ไม่มีเครื่องหมาย — ลองแบบ "หัวข้อตัวหนา" แทน
        labelled = [i for i, (k, _, t) in enumerate(parsed)
                    if k == "text" and LABEL.match(t)]
        if len(labelled) < MIN_LABEL:
            return None
        for i in labelled:
            parsed[i] = ("bul", None, parsed[i][2])

    out, run, kind = [], [], None

    chained = [False]

    def flush_list():
        nonlocal run, kind
        if not run:
            return
        tag = "ol" if (kind == "num" or chained[0]) else "ul"
        chained[0] = False
        out.append(f"<{tag}>\n" + "\n".join(f"<li>{t}</li>" for t in run) + f"\n</{tag}>")
        run, kind = [], None

    def flush_text(buf):
        if buf:
            out.append(f"{open_tag}{'<br>'.join(buf)}</p>")

    buf = []
    for k, sym, t in parsed:
        if k in ("num", "bul", "keep"):
            item = f"{sym} {t}" if k == "keep" else t
            if kind and k != kind:
                flush_list()
            kind = k
            flush_text(buf); buf = []
            run.append(item)
        elif k == "chain":
            chained[0] = True          # ลูกศรคั่น — อยู่รายการเดียวกัน แค่เป็นลำดับ
        elif k == "gap":
            flush_list()
        else:
            flush_list()
            buf.append(t)
    flush_list()
    flush_text(buf)
    return "\n".join(out)


def process(path, write):
    src = open(path, encoding="utf-8").read()
    # ไม่แตะกล่องสูตร — <br> ที่นั่นคือการขึ้นบรรทัดของสูตร ไม่ใช่รายการ
    holes = [(m.start(), m.end()) for m in re.finditer(r'<div class="fm">.*?</div>', src, re.S)]

    def in_hole(i):
        return any(a <= i < b for a, b in holes)

    changes, out, last = 0, [], 0
    for m in P_BLOCK.finditer(src):
        if in_hole(m.start()):
            continue
        new = convert_block(m.group(1), m.group(2))
        if new is None:
            continue
        out.append(src[last:m.start()]); out.append(new); last = m.end()
        changes += 1
    if not changes:
        return 0
    out.append(src[last:])
    if write:
        open(path, "w", encoding="utf-8").write("".join(out))
    return changes


def main(argv):
    write = "--write" in argv
    names = [a for a in argv if a != "--write"]
    files = [os.path.join(DOCS, n if n.endswith(".html") else n + ".html") for n in names] \
        or sorted(glob.glob(os.path.join(DOCS, "*.html")))
    tot = 0
    for f in files:
        n = process(f, write)
        if n:
            print(f"{'✏️ ' if write else '   '}{os.path.basename(f):<34} {n} บล็อก")
            tot += n
    print(f"\n{'แก้' if write else 'จะแก้'} {tot} บล็อก ใน {len(files)} ไฟล์"
          + ("" if write else " · ใส่ --write เพื่อเขียนจริง"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
