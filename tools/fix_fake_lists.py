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
MARK = re.compile(r'^\s*(?:(•|✓|✗|◦|–)|(\d+)\.)\s+(.*)$', re.S)


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
        m = MARK.match(s)
        if m:
            sym, num, rest = m.groups()
            parsed.append(("num" if num else ("keep" if sym in "✓✗" else "bul"), sym, rest.strip()))
        else:
            parsed.append(("text", None, s))
    if not any(k in ("num", "bul", "keep") for k, _, _ in parsed):
        return None

    out, run, kind = [], [], None

    def flush_list():
        nonlocal run, kind
        if not run:
            return
        tag = "ol" if kind == "num" else "ul"
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
