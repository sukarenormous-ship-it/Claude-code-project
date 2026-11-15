#!/usr/bin/env python3
"""กฎเพิ่มของเล่ม 2 (docs/sab2-book-plan.md หัวข้อ 5 และ 7) — sab_qa.py เรียกใช้เมื่อรันด้วย --book sab2

  V9  บล็อก 💻 details.code: ทุก <pre> ในบล็อกรันได้จริงและพิมพ์ค่าตรงกับบรรทัด "# ผลที่ต้องได้: …" ท้ายโค้ด
      (ตัวเลขตามลำดับ · จำนวนเท่ากัน · ค่าที่พิมพ์ปัดตามจำนวนทศนิยมที่เขียนในบรรทัดคาดหวังแล้วต้องเท่ากัน) ·
      ทุกค่าที่คาดหวังต้องปรากฏในเนื้อหน้านอก <pre> · ≤ 25 บรรทัดโค้ด (ไม่นับบรรทัดว่างและบรรทัดคาดหวัง) ·
      summary ขึ้นต้น "💻 ทำด้วย Python" · บทก่อน 17 ห้ามมี unlock_final ในโค้ด
      รัน: temp dir · PYTHONPATH=tools · timeout · ไม่มีเครือข่าย (unshare -n ถ้าเครื่องรองรับ + ปิด socket ในตัวรัน)
  V10 ทุกบทมีกล่อง .fails "พังเมื่อไร / บอกอะไรไม่ได้" อย่างน้อยหนึ่งกล่องบนเส้นทางหลัก (นอก details)
      หัว .bt มีทั้ง "พังเมื่อไร" และ "บอกอะไรไม่ได้" · ในกล่องมีตัวเลขอย่างน้อยหนึ่งตัว (เงื่อนไขพร้อมตัวเลข)
  V11 ปลั๊กอิน tools/sab2_figures_ch/*.py และ tools/sab2_charts_ch/*.py ยกเว้น ch17.py ห้ามแตะช่วงทดสอบสุดท้าย:
      ห้ามมี unlock_final (ยกเว้นเขียนตรงตัวว่า unlock_final=False) · ห้ามอ่านไฟล์ข้อมูลตรง (sab2-data · closes-daily ·
      funding-8h · splits.json) หรือเรียกตัวช่วยภายใน (_split_range · _csv_rows) ของ sab2_realdata

markup ที่ผู้เขียนต้องใช้
    <details class="code"><summary>💻 ทำด้วย Python</summary>
    <pre>import sab2_stats as S
    r = S.ols([1, 2, 3, 4], [2.1, 3.9, 6.2, 7.8])
    print(round(r["slope"], 2), round(r["intercept"], 2))
    # ผลที่ต้องได้: 1.94 · 0.15</pre>
    <p>…</p></details>

    <div class="fails"><div class="bt">⚠️ พังเมื่อไร / บอกอะไรไม่ได้</div>
    <ul><li><strong>พังเมื่อ</strong> ข้อมูลสั้นกว่า 60 วัน …</li><li><strong>บอกไม่ได้ว่า</strong> …</li></ul></div>

    python3 tools/sab2_qa.py              # = python3 tools/sab_qa.py --book sab2 (ตรวจทุกหน้า docs/sab2-*.html)
    python3 tools/sab2_qa.py --selftest   # ทดสอบกฎ V9–V11 ด้วยหน้าหุ่นและปลั๊กอินหุ่น
"""

import ast
import html as htmllib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
CODE_TIMEOUT = 60            # วินาทีต่อบล็อก
CODE_MAX_LINES = 25          # แผน sab2 หัวข้อ 5
FINAL_PART = 17              # บทเดียวที่เปิดช่วงทดสอบสุดท้ายได้
EXPECT_RE = re.compile(r"^\s*#\s*ผลที่ต้องได้\s*:\s*(.*?)\s*$")
NUM_RE = re.compile(r"(?<![A-Za-z_\d.])[-−+]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:[eE][-+]?\d+)?(?![\d])")
FORBIDDEN_TOKENS = ("sab2-data", "closes-daily", "funding-8h", "splits.json", "_split_range", "_csv_rows")

# ตัวรัน: ปิด socket ก่อนรันโค้ดของบล็อก (กันเครือข่ายแม้เครื่องไม่มี unshare)
RUNNER = r'''import runpy, socket, sys
def _blocked(*a, **k):
    raise OSError("เครือข่ายถูกปิดในการตรวจบล็อก 💻 (sab2_qa V9)")
socket.socket = _blocked
socket.create_connection = _blocked
socket.getaddrinfo = _blocked
path = sys.argv[1]
sys.argv = [path]
runpy.run_path(path, run_name="__main__")
'''

_UNSHARE = None


def _unshare_prefix():
    """["unshare", "-n"] ถ้าเครื่องนี้สร้าง network namespace ได้ (ทดสอบครั้งเดียว) · ไม่ได้ = []"""
    global _UNSHARE
    if _UNSHARE is None:
        _UNSHARE = []
        exe = shutil.which("unshare")
        if exe:
            for pre in ([exe, "-n"], [exe, "-rn"]):
                try:
                    if subprocess.run(pre + ["true"], capture_output=True, timeout=10).returncode == 0:
                        _UNSHARE = pre
                        break
                except (OSError, subprocess.SubprocessError):
                    pass
    return _UNSHARE


# ───────────────────────── ตัวช่วย ─────────────────────────

def _dec(s):
    """'−1,234.50' → Decimal · None ถ้าไม่ใช่ตัวเลข"""
    s = s.strip().replace("−", "-").replace(",", "")
    try:
        return Decimal(s)
    except InvalidOperation:
        return None


def numbers(text):
    """ตัวเลขทุกตัวในข้อความ (ตามลำดับ) เป็นสตริงดิบ"""
    return [m.group(0) for m in NUM_RE.finditer(text)]


def _places(raw):
    """จำนวนทศนิยมที่เขียน (ไม่นับรูป e) · None = เขียนแบบ e → เทียบแบบสัมพัทธ์"""
    raw = raw.replace(",", "")
    if "e" in raw.lower():
        return None
    return len(raw.split(".")[1]) if "." in raw else 0


def same_value(printed, expected):
    """ค่าที่พิมพ์ปัดตามทศนิยมของค่าที่คาดหวังแล้วเท่ากัน (half-up) · รูป e เทียบสัมพัทธ์ 1e-9"""
    p, e = _dec(printed), _dec(expected)
    if p is None or e is None:
        return False
    k = _places(expected)
    if k is None:
        return abs(p - e) <= abs(e) * Decimal("1e-9")
    q = Decimal(1).scaleb(-k)
    return p.quantize(q, rounding=ROUND_HALF_UP) == e.quantize(q, rounding=ROUND_HALF_UP)


def _norm_num(raw):
    d = _dec(raw)
    if d is None:
        return None
    d = abs(d)
    return str(d.quantize(Decimal(1))) if d == d.to_integral() else format(d.normalize(), "f")


def page_numbers_outside_code(html):
    """ตัวเลขที่ผู้อ่านเห็นในหน้า นอก <pre> · script · style · comment (normalize · ไม่สนเครื่องหมาย)"""
    body = re.sub(r"<!--.*?-->", " ", html, flags=re.S)
    body = re.sub(r"<(script|style|pre)\b.*?</\1>", " ", body, flags=re.S)
    text = htmllib.unescape(re.sub(r"<[^>]+>", " ", body))
    return {n for n in (_norm_num(x) for x in numbers(text)) if n is not None}


def code_blocks(html):
    """[(บรรทัด, summary, [โค้ดของแต่ละ <pre>])] ของทุก <details class="code">"""
    out = []
    for m in re.finditer(r"<details\b([^>]*)>", html):
        if "code" not in (re.search(r'class="([^"]*)"', m.group(1)) or [None, ""])[1].split():
            continue
        depth, end = 1, len(html)
        for t in re.finditer(r"<(/?)details\b[^>]*>", html[m.end():]):
            depth += -1 if t.group(1) else 1
            if depth == 0:
                end = m.end() + t.start()
                break
        inner = html[m.end():end]
        sm = re.search(r"<summary\b[^>]*>(.*?)</summary>", inner, re.S)
        summary = htmllib.unescape(re.sub(r"<[^>]+>", "", sm.group(1))).strip() if sm else ""
        pres = [htmllib.unescape(re.sub(r"<[^>]+>", "", p)) for p in re.findall(r"<pre\b[^>]*>(.*?)</pre>", inner, re.S)]
        out.append((html.count("\n", 0, m.start()) + 1, summary, pres))
    return out


def run_code(code, timeout=CODE_TIMEOUT):
    """รันโค้ดใน temp dir · PYTHONPATH=tools · ไม่มีเครือข่าย → (returncode, stdout, stderr)"""
    with tempfile.TemporaryDirectory(prefix="sab2code-") as d:
        with open(os.path.join(d, "block.py"), "w", encoding="utf-8") as fh:
            fh.write(code)
        with open(os.path.join(d, "_runner.py"), "w", encoding="utf-8") as fh:
            fh.write(RUNNER)
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": d, "PYTHONPATH": TOOLS,
               "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8",
               "LANG": "C.UTF-8", "MPLBACKEND": "Agg", "TMPDIR": d}
        cmd = _unshare_prefix() + [sys.executable, "_runner.py", "block.py"]
        try:
            r = subprocess.run(cmd, cwd=d, env=env, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return None, "", f"เกินเวลา {timeout} วินาที"
        return r.returncode, r.stdout, r.stderr


# ───────────────────────── กฎ ─────────────────────────

def check_code(name, html, part=None):
    """V9 — คืนรายการปัญหา (ขึ้นต้นด้วยชื่อไฟล์)"""
    P = []
    seen = None
    for line, summary, pres in code_blocks(html):
        where = f"{name}: V9 บล็อก 💻 บรรทัด {line}"
        if not re.sub(r"\s+", "", summary.replace("️", "")).startswith("💻ทำด้วยPython"):
            P.append(f'{where}: summary ต้องขึ้นต้นด้วย "💻 ทำด้วย Python" (พบ {summary[:30]!r})')
        if not pres:
            P.append(f"{where}: ไม่มี <pre> ที่เป็นโค้ด")
        for i, code in enumerate(pres, 1):
            tag = f"{where}" + (f" (<pre> ที่ {i})" if len(pres) > 1 else "")
            lines = [x for x in code.strip("\n").split("\n")]
            nonblank = [x for x in lines if x.strip()]
            em = EXPECT_RE.match(nonblank[-1]) if nonblank else None
            if not em:
                P.append(f'{tag}: บรรทัดสุดท้ายต้องเป็น "# ผลที่ต้องได้: ค่า · ค่า"')
                continue
            if len(nonblank) - 1 > CODE_MAX_LINES:
                P.append(f"{tag}: โค้ด {len(nonblank) - 1} บรรทัด (เพดาน {CODE_MAX_LINES})")
            if part != FINAL_PART and re.search(r"unlock_final", code):
                P.append(f"{tag}: ใช้ unlock_final ก่อนบท {FINAL_PART} (ช่วงทดสอบสุดท้ายล็อกไว้)")
                continue
            want = numbers(em.group(1))
            if not want:
                P.append(f"{tag}: บรรทัดผลที่ต้องได้ไม่มีตัวเลข")
                continue
            rc, out, err = run_code(code)
            if rc != 0:
                last = (err.strip().splitlines() or ["?"])[-1]
                P.append(f"{tag}: รันไม่ผ่าน ({'timeout' if rc is None else f'exit {rc}'}) — {last[:160]}")
                continue
            got = numbers(out)
            if len(got) != len(want) or not all(same_value(g, w) for g, w in zip(got, want)):
                P.append(f"{tag}: พิมพ์ {' · '.join(got) or '(ไม่มีตัวเลข)'} แต่บรรทัดคาดหวัง {' · '.join(want)}")
                continue
            if seen is None:
                seen = page_numbers_outside_code(html)
            missing = [w for w in want if _norm_num(w) not in seen]
            if missing:
                P.append(f"{tag}: ค่า {' · '.join(missing)} ไม่ปรากฏในเนื้อหน้า (นอกโค้ด)")
    return P


def check_fails(name, html, blocks, has_class, text_of):
    """V10 — ใช้ตัวช่วยของ sab_qa (blocks · has_class · text_of) เพื่อให้ตัดสิน "นอก details" แบบเดียวกับกฎอื่น"""
    P = []
    det = blocks(html, lambda t, a: t == "details")
    boxes = [b for b in blocks(html, lambda t, a: has_class(a, "fails"))
             if not any(s < b[0] < e for s, e, _ in det)]
    if not boxes:
        return [f'{name}: V10 ไม่มีกล่อง .fails "พังเมื่อไร / บอกอะไรไม่ได้" บนเส้นทางหลัก (อย่างน้อยหนึ่งกล่องต่อบท)']
    for s, e, _ in boxes:
        seg = html[s:e]
        bt = re.search(r'<div class="bt">(.*?)</div>', seg, re.S)
        head = re.sub(r"\s+", "", text_of(bt.group(1))) if bt else ""
        line = html.count("\n", 0, s) + 1
        if "พังเมื่อไร" not in head or "บอกอะไรไม่ได้" not in head:
            P.append(f'{name}: V10 กล่อง .fails บรรทัด {line}: หัว .bt ต้องมี "พังเมื่อไร / บอกอะไรไม่ได้"')
        if not re.search(r"\d", text_of(seg[bt.end():] if bt else seg)):
            P.append(f"{name}: V10 กล่อง .fails บรรทัด {line}: ต้องมีเงื่อนไขพร้อมตัวเลขอย่างน้อยหนึ่งตัว")
    return P


def _plugin_problems(path):
    rel = os.path.relpath(path, ROOT)
    with open(path, encoding="utf-8") as fh:
        src = fh.read()
    try:
        tree = ast.parse(src, filename=path)
    except SyntaxError as e:
        return [f"{rel}: V11 อ่านไม่ได้ (SyntaxError บรรทัด {e.lineno})"]
    ok_kw = set()                                   # ตำแหน่งของ unlock_final=False ที่ยอมได้
    P = []
    for node in ast.walk(tree):
        if isinstance(node, ast.keyword) and node.arg == "unlock_final":
            if isinstance(node.value, ast.Constant) and node.value.value is False:
                ok_kw.add(node.value.lineno)
            else:
                P.append(f"{rel}: V11 เรียกด้วย unlock_final (บรรทัด {node.value.lineno}) — เปิดช่วงทดสอบสุดท้ายได้เฉพาะ ch17.py")
        elif isinstance(node, ast.keyword) and node.arg is None:   # **kwargs อาจซ่อน unlock_final
            P.append(f"{rel}: V11 ส่ง **kwargs (บรรทัด {node.value.lineno}) — เขียนอาร์กิวเมนต์ตรงตัวเพื่อให้ตรวจช่วงข้อมูลได้")
    for i, text in enumerate(src.split("\n"), 1):
        code = text.split("#", 1)[0]
        if "unlock_final" in code and i not in ok_kw and not any(f"บรรทัด {i})" in p for p in P):
            P.append(f"{rel}: V11 มีคำว่า unlock_final (บรรทัด {i}) — เปิดช่วงทดสอบสุดท้ายได้เฉพาะ ch17.py")
        for tok in FORBIDDEN_TOKENS:
            if tok in code:
                P.append(f"{rel}: V11 อ้าง {tok!r} (บรรทัด {i}) — อ่านข้อมูลผ่าน sab2_realdata.load_closes/load_funding เท่านั้น")
    return P


def check_plugins(folders=None):
    """V11 — ปลั๊กอินทุกไฟล์ยกเว้น ch17.py"""
    folders = folders or [os.path.join(TOOLS, "sab2_figures_ch"), os.path.join(TOOLS, "sab2_charts_ch")]
    P = []
    for folder in folders:
        if not os.path.isdir(folder):
            continue
        for fn in sorted(os.listdir(folder)):
            if fn.endswith(".py") and fn != f"ch{FINAL_PART}.py":
                P += _plugin_problems(os.path.join(folder, fn))
    return P


# ───────────────────────── selftest ─────────────────────────

def _code(body, summary="💻 ทำด้วย Python"):
    return f'<details class="code"><summary>{summary}</summary>\n<pre>{body}</pre>\n<p>อธิบาย</p></details>\n'


def selftest():
    sys.path.insert(0, TOOLS)
    import sab_qa as Q   # ตัวช่วย blocks / has_class / text_of
    ok, msgs = True, []

    def expect(label, probs, want):
        nonlocal ok
        hit = [p for p in probs if want in p] if want else probs
        if (want and not hit) or (not want and probs):
            ok = False
            msgs.append(f"selftest ล้ม: {label} → {probs}")

    page_txt = "<p>ความชัน 1.94 และจุดตัด 0.15 · φ ประมาณ 0.9</p>"
    good = _code("import sab2_stats as S\n"
                 "r = S.ols([1, 2, 3, 4], [2.1, 3.9, 6.2, 7.8])\n"
                 "print(round(r[&quot;slope&quot;], 2), round(r[&quot;intercept&quot;], 2))\n"
                 "# ผลที่ต้องได้: 1.94 · 0.15")
    expect("บล็อกถูก (import sab2_stats · &quot; ถูกถอด)", check_code("t.html", page_txt + good, part=1), None)
    rounding = _code("print(0.94999 + 0.95)\nprint(1 &lt; 2)\n# ผลที่ต้องได้: 1.9")   # 1.89999 → 1.9 · True ไม่ใช่ตัวเลข
    expect("ปัดตามทศนิยมที่เขียน · &lt; ถูกถอด", check_code("t.html", "<p>1.9</p>" + rounding, part=1), None)
    cases = [
        ("ค่าไม่ตรง", _code("print(1.95)\n# ผลที่ต้องได้: 1.94"), "แต่บรรทัดคาดหวัง 1.94"),
        ("จำนวนค่าไม่ตรง", _code("print(1.94, 2)\n# ผลที่ต้องได้: 1.94"), "แต่บรรทัดคาดหวัง"),
        ("ไม่มีบรรทัดคาดหวัง", _code("print(1.94)"), "บรรทัดสุดท้ายต้องเป็น"),
        ("รันพัง", _code("raise ValueError('x')\n# ผลที่ต้องได้: 1.94"), "รันไม่ผ่าน (exit 1)"),
        ("ค่าไม่อยู่ในหน้า", _code("print(7.77)\n# ผลที่ต้องได้: 7.77"), "ไม่ปรากฏในเนื้อหน้า"),
        ("summary ผิด", _code("print(1.94)\n# ผลที่ต้องได้: 1.94", summary="โค้ด"), "summary ต้องขึ้นต้น"),
        ("ยาวเกิน", _code("x = 1\n" * 26 + "print(1.94)\n# ผลที่ต้องได้: 1.94"), "บรรทัด (เพดาน 25)"),
        ("เครือข่ายถูกปิด", _code("import socket\nsocket.create_connection(('example.com', 80))\nprint(1.94)\n"
                                  "# ผลที่ต้องได้: 1.94"), "รันไม่ผ่าน"),
        ("timeout", None, "timeout"),
        ("unlock_final ก่อนบท 17", _code("import sab2_realdata as R\nR.load_closes('final_test', unlock_final=True)\n"
                                        "print(1.94)\n# ผลที่ต้องได้: 1.94"), "ใช้ unlock_final ก่อนบท 17"),
    ]
    for label, block, want in cases:
        if block is None:                                  # timeout: เรียก run_code ตรงด้วยเวลาสั้น
            rc, _, err = run_code("while True: pass", timeout=2)
            if rc is not None:
                ok = False
                msgs.append(f"selftest ล้ม: timeout → rc={rc} {err}")
            continue
        expect(label, check_code("t.html", page_txt + block, part=3), want)
    # V10
    F = lambda h: check_fails("t.html", h, Q.blocks, Q.has_class, Q.text_of)  # noqa: E731
    fails_ok = ('<div class="fails"><div class="bt">⚠️ พังเมื่อไร / บอกอะไรไม่ได้</div>'
                '<ul><li>ข้อมูลสั้นกว่า 60 วัน</li></ul></div>')
    expect(".fails ถูก", F(fails_ok), None)
    expect("ไม่มี .fails", F("<p>x</p>"), "V10 ไม่มีกล่อง")
    expect(".fails อยู่ใน details", F(f"<details class=\"deep\"><summary>x</summary>{fails_ok}</details>"), "V10 ไม่มีกล่อง")
    expect(".fails หัวผิด", F('<div class="fails"><div class="bt">ข้อเสีย</div><p>สั้นกว่า 60 วัน</p></div>'), "หัว .bt")
    expect(".fails ไม่มีตัวเลข", F('<div class="fails"><div class="bt">พังเมื่อไร / บอกอะไรไม่ได้</div><p>ข้อมูลสั้น</p></div>'),
           "พร้อมตัวเลข")
    # V11
    with tempfile.TemporaryDirectory() as d:
        def plug(fn, src):
            with open(os.path.join(d, fn), "w", encoding="utf-8") as fh:
                fh.write(src)
        plug("ch03.py", "import sab2_realdata as R\ndef extend(data, D, q):\n"
                        "    R.load_closes('formation', unlock_final=False)\n    return {}\n")
        plug("ch17.py", "import sab2_realdata as R\ndef extend(data, D, q):\n"
                        "    R.load_closes('final_test', unlock_final=True)\n    return {}\n")
        expect("ปลั๊กอินถูก (False ได้ · ch17 เปิดได้)", check_plugins([d]), None)
        plug("ch05.py", "import sab2_realdata as R\nFLAG = True\ndef extend(data, D, q):\n"
                        "    R.load_closes('final_test', unlock_final=FLAG)\n    return {}\n")
        plug("ch06.py", "import sab2_realdata as R\ndef extend(data, D, q):\n"
                        "    kw = {'unlock_final': True}\n    R.load_closes('final_test', **kw)\n    return {}\n")
        plug("ch07.py", "import csv\ndef extend(data, D, q):\n"
                        "    open('docs/sab2-data/closes-daily.csv')\n    return {}\n")
        probs = check_plugins([d])

        def of(fn):
            return [p for p in probs if p.split(":", 1)[0].endswith(fn)]
        expect("ch05 unlock_final=ตัวแปร", of("ch05.py"), "เรียกด้วย unlock_final")
        expect("ch06 **kwargs", of("ch06.py"), "**kwargs")
        expect("ch07 อ่านไฟล์ตรง", of("ch07.py"), "'sab2-data'")
        expect("ch03/ch17 ไม่ถูกฟ้อง", of("ch03.py") + of("ch17.py"), None)
    for m in msgs:
        print(m)
    net = "unshare -n + ปิด socket" if _unshare_prefix() else "ปิด socket (เครื่องนี้ไม่มี unshare -n)"
    print("selftest V9–V11", f"ผ่าน ✓ (💻 รันจริง · ปัดตามทศนิยม · จับค่าไม่ตรง/จำนวนไม่ตรง/ไม่มีบรรทัดคาดหวัง/รันพัง/timeout/"
          f"ค่าไม่อยู่ในหน้า/summary/ยาวเกิน/unlock_final · เครือข่าย: {net} · .fails 4 กรณี · ปลั๊กอิน 5 กรณี)"
          if ok else "ไม่ผ่าน ✗")
    return 0 if ok else 1


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        sys.exit(selftest())
    os.environ["SAB_BOOK"] = "sab2"
    sys.path.insert(0, TOOLS)
    import runpy
    sys.argv = [os.path.join(TOOLS, "sab_qa.py")] + sys.argv[1:]
    runpy.run_path(sys.argv[0], run_name="__main__")
