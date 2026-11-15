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
    python3 tools/sab_check_figures.py --scope base1   # หน้าพื้นฐาน (แผน 14.5 · คีย์ตัวเลขอยู่ใต้ base.* จาก tools/sab_figures_ch/base.py)
    python3 tools/sab_check_figures.py --selftest      # ใส่ข้อผิดจงใจในบทหุ่น ต้องจับได้ครบ
    SAB_BOOK=sab2 python3 tools/sab_check_figures.py --strict   # เล่ม 2: เลขที่มาไม่ใช่บทนี้ (chNN / แบบฝึก.chNN / เล่ม 1) = ล้ม

เล่ม 2 (ที่มาเข้ม): เลขบนหน้า sab2-partN ต้องอยู่ใต้ chNN.* · แบบฝึก.chNN · เรื่อง.partN · ตัวเลขเล่ม 1 (docs/sab-figures.json
ผ่านเล่มก่อนหน้าในทะเบียน sab_book.BOOKS) หรือเป็นจำนวนนับ < 100 / ปี 1900–2100 / ALLOWED — นอกนั้นรายงานเป็น "⚠️ ที่มา
ไม่ใช่บทนี้" (เตือน · --strict ให้ล้ม) พร้อม path ที่เลขไปบังเอิญตรง · data-key ที่ชี้คีย์บทอื่นก็รายงาน
"""

import json
import os
import re
import sys
import tempfile
from decimal import Decimal, InvalidOperation

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sab_book as B  # noqa: E402  (เลือกเล่มด้วย SAB_BOOK หรือ --book · ค่าเริ่มต้น sab)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
FIG = B.FIG

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
    """อ่านค่าตาม path ที่คั่นด้วย "." — คีย์ที่มีจุดในตัว (เช่น "บันไดที่0.1", "0.80") หาได้ด้วยการลองคีย์ยาวสุดก่อน"""
    parts = path.split(".")

    def walk(cur, i):
        if i == len(parts):
            return True, cur
        for j in range(len(parts), i, -1):
            key = ".".join(parts[i:j])
            if isinstance(cur, dict) and key in cur:
                ok, v = walk(cur[key], j)
                if ok:
                    return True, v
            elif isinstance(cur, list) and key.isdigit() and int(key) < len(cur):
                ok, v = walk(cur[int(key)], j)
                if ok:
                    return True, v
        return False, None
    ok, v = walk(fig, 0)
    if not ok:
        raise KeyError(path)
    return v


def visible_text(html, skip_code=False):
    """ข้อความที่ผู้อ่านเห็น (ตัด script/style/comment และแท็ก)
    skip_code (เล่ม 2): ตัด <pre> ด้วย — โค้ดในบล็อก 💻 details.code ตรวจโดย sab_qa V9 (รันจริง · ผลต้องปรากฏในหน้า)"""
    body = re.sub(r"<!--.*?-->", " ", html, flags=re.S)
    if skip_code:
        body = re.sub(r"<pre\b.*?</pre>", " ", body, flags=re.S)
    body = re.sub(r"<(script|style)\b.*?</\1>", " ", body, flags=re.S)
    body = re.sub(r"<[^>]+>", " ", body)
    return body.replace("&nbsp;", " ").replace("&minus;", "−")


def page_numbers(html, skip_code=False):
    out = []
    for m in NUM_RE.finditer(visible_text(html, skip_code)):
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


def check_page(name, html, fig, known, skip_code=False, fig_name="sab-figures.json"):
    problems = []
    for raw, n in page_numbers(html, skip_code):
        if n not in known and n.lstrip("-") not in known and n not in ALLOWED:
            problems.append(f"{name}: เลขลอย {raw!s} ไม่มีใน {fig_name}")
    for m in DATA_KEY_RE.finditer(html):
        key, inner = m.group(2), re.sub(r"<[^>]+>", "", m.group(3)).strip()
        try:
            want = get_path(fig, key)
        except KeyError:
            problems.append(f"{name}: data-key {key!r} ไม่มีใน JSON")
            continue
        if inner and isinstance(want, str) and norm(want) is None:      # ค่าข้อความ (เช่น โหมด PAUSED) เทียบตรงตัว
            if inner != want:
                problems.append(f"{name}: data-key {key} พิมพ์ {inner!r} แต่ JSON = {want!r}")
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


YEARS = {str(y) for y in range(1900, 2101)}


def value_paths(o, path=""):
    """ค่าตัวเลข (normalize แล้ว · ไม่มีเครื่องหมาย) → path แรกที่พบใน JSON (ไว้บอกว่าเลขที่ "ข้ามบท" มาจากไหน)"""
    out = {}

    def walk(x, p):
        if isinstance(x, dict):
            for k, v in x.items():
                walk(v, f"{p}.{k}" if p else str(k))
        elif isinstance(x, list):
            for i, v in enumerate(x):
                walk(v, f"{p}.{i}")
        elif not (isinstance(x, bool) or x is None) and isinstance(x, (int, float, str)):
            n = norm(x)
            if n is not None:
                out.setdefault(n.lstrip("-"), p)
    walk(o, path)
    return out


def strict_sources(fig, part, prev_fig=None):
    """ชุดค่าที่หน้าบท part ของเล่ม 2 อ้างได้: chNN.* · แบบฝึก.chNN (_แบบฝึก ของปลั๊กอิน) · เรื่อง.partN · ตัวเลขเล่ม 1
    (sab_book.load_figures ของเล่มก่อน) — ไม่รวมบทอื่นของเล่ม 2 (เลขที่บังเอิญตรงกับบทอื่นไม่นับ)"""
    ch = f"ch{part:02d}"
    own = {"ch": fig.get(ch, {}), "drill": (fig.get("แบบฝึก") or {}).get(ch, []),
           "story": (fig.get("เรื่อง") or {}).get(f"part{part}", {})}
    allowed = known_values(own)
    if prev_fig is not None:
        allowed |= known_values(prev_fig)
    return allowed


def check_strict(name, html, fig, part, prev_fig=None, where=None):
    """เล่ม 2: เลขบนหน้าบท N ต้องมีที่มาใต้ chNN / แบบฝึก.chNN / เรื่อง.partN / เล่ม 1 หรืออยู่ในรายการยกเว้น
    (จำนวนนับ < 100 · ปี 1900–2100 · ALLOWED) · data-key ต้องชี้คีย์ของบทนี้ (หรือแบบฝึก/เรื่องของบทนี้)
    คืนรายการข้อสังเกต (ไม่ล้มเว้นแต่ --strict)"""
    allowed = strict_sources(fig, part, prev_fig)
    where = where if where is not None else value_paths(fig)
    ch = f"ch{part:02d}"
    out, seen = [], set()
    for raw, n in page_numbers(html, skip_code=True):
        a = n.lstrip("-")
        if n in allowed or a in allowed or n in ALLOWED or a in ALLOWED or a in YEARS or raw in seen:
            continue
        seen.add(raw)
        src = where.get(a)
        out.append(f"{name}: {raw} ไม่มีใต้ {ch} / แบบฝึก.{ch} / เล่ม 1" + (f" (ตรงกับ {src} โดยบังเอิญ?)" if src else ""))
    for m in DATA_KEY_RE.finditer(html):
        key = m.group(2)
        if not (key.startswith(ch + ".") or key.startswith(f"แบบฝึก.{ch}") or key.startswith(f"เรื่อง.part{part}.")):
            out.append(f"{name}: data-key {key} ชี้คีย์นอกบทนี้ ({ch})")
    return out


def run(fig_path, docs_dir, scope=None, quiet=False, prefix=None, strict=False):
    prefix = prefix or B.PREFIX
    if not os.path.exists(fig_path):
        print(f"ยังไม่มี {os.path.relpath(fig_path, ROOT)} — รัน tools/sab_figures.py" + (f" --book {prefix}" if prefix != "sab" else "") + " ก่อน")
        return 1, ["no-json"]
    with open(fig_path, encoding="utf-8") as fh:
        fig = json.load(fh)
    known = known_values(fig)
    names = sorted(n for n in os.listdir(docs_dir) if n.startswith(f"{prefix}-") and n.endswith(".html"))
    if scope:
        names = [n for n in names if n == f"{prefix}-{scope}.html"]
    problems = check_json(fig)
    fig_name = f"{prefix}-figures.json"
    notes = []
    prev = B.BOOKS.get(prefix, {}).get("prev") if prefix != "sab" else None
    prev_fig = None
    if prev:
        prev_path = os.path.join(os.path.dirname(fig_path), f"{prev}-figures.json")
        if os.path.exists(prev_path):
            with open(prev_path, encoding="utf-8") as fh:
                prev_fig = json.load(fh)
    where = value_paths(fig) if prefix != "sab" else None
    for name in names:
        with open(os.path.join(docs_dir, name), encoding="utf-8") as fh:
            html = fh.read()
        problems += check_page(name, html, fig, known, skip_code=prefix != "sab", fig_name=fig_name)
        m = re.fullmatch(rf"{prefix}-part(\d+)\.html", name)
        if prefix != "sab" and m:                      # เล่ม 2: ที่มาต้องเป็นบทนี้ (หรือเล่ม 1) ไม่ใช่ที่ไหนก็ได้ใน JSON
            notes += check_strict(name, html, fig, int(m.group(1)), prev_fig, where)
    if strict:
        problems += notes
        notes = []
    if not quiet:
        if problems:
            print("พบปัญหา", len(problems), "ข้อ")
            for p in problems:
                print("  -", p)
        if notes:
            print(f"⚠️ ที่มาไม่ใช่บทนี้ {len(notes)} ข้อ (เตือน · --strict ให้ล้ม · ตัวเลขต้องอยู่ใต้ chNN / แบบฝึก.chNN / เล่ม 1):")
            for p in notes:
                print("  -", p)
        if not problems:
            print(f"ตรวจ {len(names)} ไฟล์ · ค่าที่รู้จัก {len(known)} ค่า · ตรงกับ {fig_name} ทั้งหมด ✓"
                  + (f" · เตือนที่มา {len(notes)} ข้อ" if notes else ""))
    run.notes = notes
    return (1 if problems else 0), problems


def selftest():
    fig = {
        "บัญชีมิน": {"beta": {"A": 1.5, "B": 1.0, "A_stress": 1.7}},
        "ch04": {"ต้องโอน": 11220, "equity_เปลี่ยน": -200, "กันชน": {"125000": 13.0, "120000": 8.6}, "ทุน": 120000},
        "ch08": {"beta": {"A": 1.2}},                                   # ผิดจงใจ: beta A ไม่ตรงค่าตรึง
        "เรื่อง": {"part3": {"close": {"เงินสดอิสระ": 14700}}, "part4": {"open": {"เงินสดอิสระ": 14000}}},  # ผิดจงใจ
        "_ต้นฉบับ": {"x": "2846.00"},
        "base": {"b1": {"ซื้อ": 100000, "ขาย": 103000, "กำไร": 3000}},      # หน้าพื้นฐาน: คีย์ใต้ base.*
    }
    base_good = ('<p>ซื้อที่ 100,000 แล้วขายที่ 103,000</p><table><tr><td data-key="base.b1.กำไร">3,000</td></tr></table>')
    base_bad = '<p>ได้กำไร 3,500</p><td data-key="base.b1.กำไร">3,500</td><td data-key="base.b9.ไม่มี">1</td>'
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
        _, p_good = run(fp, d, quiet=True, prefix="sab")
        page_good = [p for p in p_good if p.startswith("sab-part4")]
        with open(os.path.join(d, "sab-part5.html"), "w", encoding="utf-8") as fh:
            fh.write(bad)
        _, p_all = run(fp, d, quiet=True, prefix="sab")
        with open(os.path.join(d, "sab-base1.html"), "w", encoding="utf-8") as fh:
            fh.write(base_good)
        _, p_base_good = run(fp, d, scope="base1", quiet=True, prefix="sab")
        with open(os.path.join(d, "sab-base2.html"), "w", encoding="utf-8") as fh:
            fh.write(base_bad)
        _, p_base_bad = run(fp, d, scope="base2", quiet=True, prefix="sab")
        # เล่ม 2: เลขในโค้ด <pre> ของ details.code ไม่นับเป็นเลขลอย · เลขในย่อหน้าธรรมดายังนับ · ไฟล์ sab-* ไม่ปนกับ sab2-*
        with open(os.path.join(d, "sab2-part1.html"), "w", encoding="utf-8") as fh:
            fh.write('<p>ต้องโอน 11,220</p><details class="code"><summary>💻 ทำด้วย Python</summary>'
                     '<pre>x = 98765.43\nprint(round(x, 1))\n# ผลที่ต้องได้: 98765.4</pre></details><p>อีก 4,321.5</p>')
        _, p_v2 = run(fp, d, quiet=True, prefix="sab2")
        # เล่ม 2 ที่มาเข้ม: 13.5 อยู่ใต้ ch04 เท่านั้น → หน้า sab2-part5 อ้างไม่ได้ · 2,846 ของเล่ม 1 อ้างได้ · ปี 2025 ได้
        fig2 = {"ch05": {"ผล": 7.25}, "ch04": {"อื่น": 13.5}, "ch03": {"ปี": 2025, "เล่ม1": 2846}, "แบบฝึก": {"ch05": [{"คำตอบ": 1.75}]}}
        with open(os.path.join(d, "sab2-figures.json"), "w", encoding="utf-8") as fh:
            json.dump(fig2, fh, ensure_ascii=False)
        with open(os.path.join(d, "sab2-part5.html"), "w", encoding="utf-8") as fh:
            fh.write('<p>ผล 7.25 · ข้อ 1.75 · ปี 2025 · เล่ม 1 2,846 · บังเอิญ 13.5</p><td data-key="ch04.อื่น">13.5</td>')
        code_s, p_s = run(os.path.join(d, "sab2-figures.json"), d, scope="part5", quiet=True, prefix="sab2")
        notes_s = run.notes
        code_x, p_x = run(os.path.join(d, "sab2-figures.json"), d, scope="part5", quiet=True, prefix="sab2", strict=True)
    ok = True
    if code_s != 0 or p_s or len(notes_s) != 2 or not any("13.5" in n and "ch04.อื่น" in n for n in notes_s) \
            or not any("data-key ch04.อื่น" in n for n in notes_s) or code_x != 1 or len(p_x) != 2:
        ok = False
        print("selftest ล้ม: เล่ม 2 ที่มาเข้ม →", code_s, p_s, notes_s, code_x, p_x)
    if [p for p in p_v2 if "98765" in p] or not any("4,321.5" in p for p in p_v2) or any(p.startswith("sab-") for p in p_v2):
        ok = False
        print("selftest ล้ม: เล่ม 2 (โค้ดใน <pre> / แยกไฟล์ตาม prefix) →", p_v2)
    if [p for p in p_base_good if p.startswith("sab-base1")] or any(not p.startswith("sab-base2") for p in p_base_bad
                                                                    if p.startswith("sab-")):
        ok = False
        print("selftest ล้ม: --scope base1 / base2 →", p_base_good, p_base_bad)
    for e in ("เลขลอย 3,500", "data-key base.b1.กำไร พิมพ์ '3,500'", "base.b9.ไม่มี"):
        if not any(e in p for p in p_base_bad):
            ok = False
            print(f"selftest ล้ม: หน้า base ไม่จับข้อผิดจงใจ {e!r}")
    if page_good:
        ok = False
        print("selftest ล้ม: บทที่ถูกต้องถูกฟ้องผิด →", page_good)
    for e in expect:
        if not any(e in p for p in p_all):
            ok = False
            print(f"selftest ล้ม: ไม่จับข้อผิดจงใจ {e!r}")
    print("selftest", "ผ่าน ✓ (จับข้อผิดจงใจครบ", len(expect), "ชนิด · บทถูกไม่ถูกฟ้อง · หน้า base: --scope base1 และคีย์ base.* ใช้ได้ · เล่ม 2: ข้ามเลขใน <pre> ของ 💻 · ที่มาเข้ม chNN/แบบฝึก/เล่ม 1/ปี · --strict)" if ok else "ไม่ผ่าน ✗")
    return 0 if ok else 1


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--selftest"]:
        sys.exit(selftest())
    scope = a[a.index("--scope") + 1] if "--scope" in a else None
    sys.exit(run(FIG, DOCS, scope, strict="--strict" in a)[0])
