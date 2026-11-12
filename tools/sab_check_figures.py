#!/usr/bin/env python3
"""ตรวจว่าตัวเลขในบท docs/sab-*.html ตรงกับ docs/sab-figures.json (กฎเหล็ก W7: ห้ามมีเลขลอย)

ต่อยอดจาก nq_check_figures.py โดยแก้จุดอ่อนที่ผู้ตรวจเจอ
  - normalize ก่อนเทียบ: comma หลักพัน · เครื่องหมายลบ U+2212 · ศูนย์ท้ายทศนิยม
  - จับเลขลอยกว้างขึ้น: ทศนิยม · จำนวนเต็ม ≥ 3 หลัก · เลขมี comma · เลขมีเครื่องหมาย · เลขตามด้วย % หรือหน่วยเงิน
  - ชุดค่าที่รู้จักรวมค่าสตริง Decimal ของต้นฉบับ (ใต้ _ต้นฉบับ) ด้วย
  - `data-key="a.b.c"` ทุกตัวต้องมีใน JSON และค่าที่พิมพ์ในเซลล์ต้องตรงค่าใน JSON
  - บัญชีต่อเนื่อง: เรื่อง.partN.open ต้องเท่ากับ เรื่อง.partN-1.close ทุกคีย์ที่มีทั้งคู่
  - beta ของ A ทุกที่ใน JSON ต้องเท่าค่าตรึง บัญชีมิน.beta.A (stress แยกคีย์ A_stress)
เลขลอย = fatal (ตามต้นแบบ nq)

    python3 tools/sab_check_figures.py                 # ทุกไฟล์ docs/sab-*.html
    python3 tools/sab_check_figures.py --scope part4   # เฉพาะบท
    python3 tools/sab_check_figures.py --selftest      # ใส่ข้อผิดจงใจในบทหุ่น ต้องจับได้ครบ
"""

import json
import os
import re
import sys
import tempfile
from decimal import Decimal, InvalidOperation

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
FIG = os.path.join(DOCS, "sab-figures.json")

# ตัวเลขที่อธิบายได้เองในบท (ลำดับ · จำนวนนับเล็ก · ค่าคงที่ของการสอน) — เพิ่มเฉพาะเมื่อมีเหตุผล
ALLOWED = {str(i) for i in range(0, 100)} | {"100", "1000", "0.5", "0.1", "0.01"}

# ค่าที่ต้องปรากฏในบท (เติมทีละบทเมื่อเขียน): หน้า → [path ใน JSON]
# ตรวจเฉพาะหน้าที่มีไฟล์แล้ว · path ใช้ "." คั่น
REQUIRED = {
    # "sab-part4.html": ["ch04.ต้องโอน", "ch04.equity_เปลี่ยน", "ch04.กันชน.125000"],
}

NUM_RE = re.compile(
    r"(?<![\w.])"                       # ไม่ติดตัวอักษร/จุดด้านหน้า
    r"([+\-]?\d{1,3}(?:,\d{3})+(?:\.\d+)?|[+\-]?\d+(?:\.\d+)?)"
    r"(?![\w])"
    r"(\s*(?:%|บาท|ดอลลาร์|\$|USDT|เท่า))?"
)


def norm(s):
    """'−11,220.50' → '-11220.5' · คืน None ถ้าไม่ใช่ตัวเลข"""
    s = str(s).strip().replace("−", "-").replace("+", "")
    s = re.sub(r"(?<=\d),(?=\d{3})", "", s)
    try:
        d = Decimal(s)
    except InvalidOperation:
        return None
    if d == d.to_integral():
        return str(d.quantize(Decimal(1)))
    return format(d.normalize(), "f")


def known_values(fig):
    known = set()

    def walk(o):
        if isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
        elif isinstance(o, bool) or o is None:
            return
        elif isinstance(o, (int, float, str)):
            n = norm(o)
            if n is not None:
                known.add(n)
                known.add(n.lstrip("-"))
    walk(fig)
    return known


def get_path(fig, path):
    cur = fig
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        elif isinstance(cur, list) and part.isdigit() and int(part) < len(cur):
            cur = cur[int(part)]
        else:
            raise KeyError(path)
    return cur


def visible_text(html):
    """ข้อความที่ผู้อ่านเห็น (ตัด script/style/comment และแท็ก)"""
    body = re.sub(r"<!--.*?-->", " ", html, flags=re.S)
    body = re.sub(r"<(script|style)\b.*?</\1>", " ", body, flags=re.S)
    body = re.sub(r"<[^>]+>", " ", body)
    return body.replace("&nbsp;", " ").replace("&minus;", "−")


def page_numbers(html):
    out = []
    for m in NUM_RE.finditer(visible_text(html)):
        raw, unit = m.group(1), (m.group(2) or "").strip()
        n = norm(raw)
        if n is None:
            continue
        a = n.lstrip("-")
        flagged = ("." in a) or ("," in raw) or len(a.split(".")[0]) >= 3 or raw[0] in "+-−" or unit
        if flagged:
            out.append((raw + (unit and " " + unit), n))
    return out


DATA_KEY_RE = re.compile(r'<(\w+)[^>]*\bdata-key="([^"]+)"[^>]*>(.*?)</\1>', re.S)


def check_page(name, html, fig, known):
    problems = []
    for raw, n in page_numbers(html):
        if n not in known and n.lstrip("-") not in known and n not in ALLOWED:
            problems.append(f"{name}: เลขลอย {raw!s} ไม่มีใน sab-figures.json")
    for m in DATA_KEY_RE.finditer(html):
        key, inner = m.group(2), re.sub(r"<[^>]+>", "", m.group(3)).strip()
        try:
            want = get_path(fig, key)
        except KeyError:
            problems.append(f"{name}: data-key {key!r} ไม่มีใน JSON")
            continue
        if inner:
            got = norm(re.sub(r"[%\s]|บาท|ดอลลาร์|\$", "", inner))
            if got is None or norm(want) is None or got.lstrip("-") != norm(want).lstrip("-") \
                    or (got.startswith("-") != norm(want).startswith("-") and not inner.startswith("(")):
                problems.append(f"{name}: data-key {key} พิมพ์ {inner!r} แต่ JSON = {want!r}")
    for path in REQUIRED.get(name, []):
        try:
            want = norm(get_path(fig, path))
        except KeyError:
            problems.append(f"{name}: REQUIRED {path} ไม่มีใน JSON")
            continue
        if want not in {n for _, n in page_numbers(html)} | {n.lstrip("-") for _, n in page_numbers(html)}:
            problems.append(f"{name}: ไม่พบค่าบังคับ {path} = {want}")
    return problems


def check_json(fig):
    problems = []
    story = fig.get("เรื่อง", {}) or {}
    for k, v in story.items():
        m = re.fullmatch(r"part(\d+)", k)
        if not m or not isinstance(v, dict):
            continue
        prev = story.get(f"part{int(m.group(1)) - 1}")
        if not prev:
            continue
        op, cl = v.get("open") or {}, prev.get("close") or {}
        for key in set(op) & set(cl):
            if op[key] is not None and cl[key] is not None and op[key] != cl[key]:
                problems.append(f"เรื่อง.{k}.open.{key} = {op[key]} ≠ close บทก่อน = {cl[key]}")
    fixed = (fig.get("บัญชีมิน", {}).get("beta") or {}).get("A")
    if fixed is not None:
        def walk(o, path):
            if isinstance(o, dict):
                for kk, vv in o.items():
                    if kk == "beta" and isinstance(vv, dict) and "A" in vv and vv["A"] != fixed:
                        problems.append(f"{path}.beta.A = {vv['A']} ≠ ค่าตรึง {fixed}")
                    walk(vv, f"{path}.{kk}" if path else kk)
        walk(fig, "")
    return problems


def run(fig_path, docs_dir, scope=None, quiet=False):
    if not os.path.exists(fig_path):
        print(f"ยังไม่มี {os.path.relpath(fig_path, ROOT)} — รัน tools/sab_figures.py ก่อน")
        return 1, ["no-json"]
    with open(fig_path, encoding="utf-8") as fh:
        fig = json.load(fh)
    known = known_values(fig)
    names = sorted(n for n in os.listdir(docs_dir) if n.startswith("sab-") and n.endswith(".html"))
    if scope:
        names = [n for n in names if n == f"sab-{scope}.html"]
    problems = check_json(fig)
    for name in names:
        with open(os.path.join(docs_dir, name), encoding="utf-8") as fh:
            problems += check_page(name, fh.read(), fig, known)
    if not quiet:
        if problems:
            print("พบปัญหา", len(problems), "ข้อ")
            for p in problems:
                print("  -", p)
        else:
            print(f"ตรวจ {len(names)} ไฟล์ · ค่าที่รู้จัก {len(known)} ค่า · ตรงกับ sab-figures.json ทั้งหมด ✓")
    return (1 if problems else 0), problems


def selftest():
    fig = {
        "บัญชีมิน": {"beta": {"A": 1.5, "B": 1.0, "A_stress": 1.7}},
        "ch04": {"ต้องโอน": 11220, "equity_เปลี่ยน": -200, "กันชน": {"125000": 13.0, "120000": 8.6}, "ทุน": 120000},
        "ch08": {"beta": {"A": 1.2}},                                   # ผิดจงใจ: beta A ไม่ตรงค่าตรึง
        "เรื่อง": {"part3": {"close": {"เงินสดอิสระ": 14700}}, "part4": {"open": {"เงินสดอิสระ": 14000}}},  # ผิดจงใจ
        "_ต้นฉบับ": {"x": "2846.00"},
    }
    good = ('<p>ต้องโอน <strong>11,220</strong> ดอลลาร์ · equity เปลี่ยน <strong>−200</strong> · '
            'กันชน 13.0% ที่ทุน 120,000 · ค่าธรรมเนียมรวม 2,846 · บทที่ 4 วันที่ 30</p>'
            '<table class="ledger" data-part="4"><tr><td data-key="ch04.ต้องโอน">11,220</td>'
            '<td data-key="ch04.กันชน.120000">8.6%</td></tr></table>'
            '<script>var x = 98765.43;</script><!-- 55555 -->')
    bad = ('<p>กำไร 12.34% ต่อปี และ 7,777 ดอลลาร์</p>'                 # เลขลอยสองตัว
           '<td data-key="ch04.ต้องโอน">11,200</td>'                    # พิมพ์ไม่ตรง JSON
           '<td data-key="ch99.ไม่มี">5</td>')                          # key ไม่มี
    expect = ["12.34", "7,777", "พิมพ์ '11,200'", "ch99.ไม่มี", "beta.A = 1.2", "เงินสดอิสระ"]
    with tempfile.TemporaryDirectory() as d:
        fp = os.path.join(d, "sab-figures.json")
        with open(fp, "w", encoding="utf-8") as fh:
            json.dump(fig, fh, ensure_ascii=False)
        with open(os.path.join(d, "sab-part4.html"), "w", encoding="utf-8") as fh:
            fh.write(good)
        _, p_good = run(fp, d, quiet=True)
        page_good = [p for p in p_good if p.startswith("sab-part4")]
        with open(os.path.join(d, "sab-part5.html"), "w", encoding="utf-8") as fh:
            fh.write(bad)
        _, p_all = run(fp, d, quiet=True)
    ok = True
    if page_good:
        ok = False
        print("selftest ล้ม: บทที่ถูกต้องถูกฟ้องผิด →", page_good)
    for e in expect:
        if not any(e in p for p in p_all):
            ok = False
            print(f"selftest ล้ม: ไม่จับข้อผิดจงใจ {e!r}")
    print("selftest", "ผ่าน ✓ (จับข้อผิดจงใจครบ", len(expect), "ชนิด · บทถูกไม่ถูกฟ้อง)" if ok else "ไม่ผ่าน ✗")
    return 0 if ok else 1


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--selftest"]:
        sys.exit(selftest())
    scope = a[a.index("--scope") + 1] if "--scope" in a else None
    sys.exit(run(FIG, DOCS, scope)[0])
