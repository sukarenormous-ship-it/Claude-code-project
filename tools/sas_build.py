#!/usr/bin/env python3
"""เครื่องมือ build ของชุด "แกะสไลด์ Stat Arb" (docs/statarb-slides-*.html)

ตัวเลข กราฟ และผลลัพธ์โปรแกรมทุกชิ้นในชุดนี้มาจากโค้ดในห้องทดลอง (tools/sas_exp1.py … sas_exp8.py)
คนเขียนบทวาง "ที่เสียบ" ไว้ในหน้า HTML แล้วให้สคริปต์นี้เติม จึงเป็นไปไม่ได้ที่ข้อความกับกราฟจะขัดกันเอง

    python3 tools/sas_build.py <คำสั่ง> [ไฟล์.html …] [--parts 1,3] [--strict] [--no-run]

คำสั่ง (ใส่หลายคำสั่งคั่นด้วยจุลภาคได้ เช่น  charts,fill,out,snippets,check)
    figures  เรียก figures() ของโมดูลทดลอง → docs/statarb-slides-figures.json  {"meta": …, "p1": …, …}
             ไม่ระบุไฟล์ = ทุกโมดูลที่มีอยู่ (เขียน JSON ใหม่ทั้งไฟล์)
             ระบุไฟล์ หรือ --parts 3,5 = คำนวณเฉพาะตอนนั้น แล้วรวมเข้ากับ JSON เดิม (ตอนอื่นไม่ถูกแตะ)
    charts   เติม <!--CHART:sas-p3-ชื่อ--> … <!--/CHART:sas-p3-ชื่อ--> ด้วย HTML จาก charts() ของ sas_exp3
    fill     เติม <span data-f="p3.beta.ols_train">…</span> ด้วยค่าจาก JSON
             int/float → คั่นหลักพัน ทศนิยมตามที่เก็บไว้ · str → ตามนั้น · "-" นำหน้า → "−" (U+2212)
             ใส่ data-abs = พิมพ์ค่าสัมบูรณ์ · path ชี้เข้าลิสต์ได้ (p4.pcts.3 หรือ p4.pcts[3])
    out      เติม <!--OUT:p8.demo.good--> … <!--/OUT:p8.demo.good--> ด้วย <pre class="out">ข้อความจาก JSON</pre>
    snippets เติม <!--CODE:p3_hedge_ratio--> … <!--/CODE:p3_hedge_ratio--> ด้วยซอร์สของ
             tools/sas_snippets/p3_hedge_ratio.py ใน <pre class="code"> และเติม <!--RUN:p3_hedge_ratio--> …
             ด้วย stdout ที่ได้จากการรันไฟล์เดียวกันนั้นจริง (python3 ไฟล์ · cwd = รากของ repo · ไม่มีอาร์กิวเมนต์)
             ใน <pre class="out"> — โค้ดที่พิมพ์ในบท จึงเป็นโค้ดตัวเดียวกับที่ให้ผลลัพธ์ที่พิมพ์อยู่ข้างใต้
    shell    อัปเดตเปลือกของหน้า (CSS สองบล็อกใน <head> + Thai line-break script) ให้ตรงกับที่
             tools/sas_new_part.py สร้างในตอนนี้ — เนื้อหาไม่ถูกแตะ (ใช้เมื่อ check บอกว่าเปลือกไม่ตรง)
    check    ตรวจหน้า: error = โครงสร้าง HTML · <br> ปลอมเป็นรายการ · ลิงก์ภายใน · data-f / CHART / OUT /
             CODE / RUN (ว่าง · ไม่มีเจ้าของ · ไม่ตรงกับต้นทาง) · id ซ้ำ · เปลือก (CSS + Thai line-break script)
             · <!--BODY--> ค้าง · กล่องบังคับ   |   warning (ไม่ทำให้ล้ม) = ตัวเลขที่ไม่ได้ติดป้าย data-f
             · ศัพท์ใหม่เกิน 12 · ข้อความไทยยาวเกิน ~420 ตัวอักษร · em-dash ซ้อนในประโยคเดียว
             · snippet ยาวเกิน 40 บรรทัด · RUN ที่ไม่มี CODE คู่กัน
             ลิงก์ไปหน้าในชุดเดียวกัน (statarb-slides-index / part1…8) ที่ยังไม่ถูกเขียน = warning เพราะหลายคนเขียน
             พร้อมกัน · --strict = นับเป็น error (ใช้ตอนรวมเล่มรอบสุดท้าย) · --draft = ไม่มีผลแล้ว (รับไว้เฉย ๆ)
             --no-run = ไม่รัน snippet ซ้ำเพื่อเทียบกับบล็อก RUN (ตรวจแค่ว่าไม่ว่าง)
                        ปกติ check รัน snippet ซ้ำแล้วเทียบกับที่พิมพ์ในหน้าทุกตัวอักษร
    all      figures → charts → fill → out → snippets → check   (shell ไม่อยู่ใน all)

ไฟล์: ไม่ระบุ = docs/statarb-slides-*.html ทั้งหมด · ระบุ = แตะเฉพาะไฟล์นั้น
ทุกคำสั่งรันซ้ำได้ (idempotent) และเขียนไฟล์เฉพาะเมื่อเนื้อหาเปลี่ยนจริง · มี error เมื่อไร exit code = 1
คนเขียนบทที่ทำงานพร้อมกันหลายคน: ระบุไฟล์ของตัวเองเสมอ และอย่ารัน figures / all แบบไม่ระบุตอน

ตัวแปรแวดล้อมสำหรับทดสอบเครื่องมือเท่านั้น:
    SAS_EXP_DIR (โฟลเดอร์ของ sas_exp*.py) · SAS_FIGURES (ไฟล์ JSON) · SAS_SNIPPET_DIR (โฟลเดอร์ของ snippet)
"""

import argparse
import glob
import html
import importlib
import json
import math
import os
import re
import subprocess
import sys
import traceback
from decimal import Decimal
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
TOOLS = os.path.join(ROOT, "tools")
EXP_DIR = os.environ.get("SAS_EXP_DIR") or TOOLS
FIG_PATH = os.environ.get("SAS_FIGURES") or os.path.join(DOCS, "statarb-slides-figures.json")
SNIPPET_DIR = os.environ.get("SAS_SNIPPET_DIR") or os.path.join(TOOLS, "sas_snippets")
REF_PAGE =os.path.join(DOCS, "statarb-data-quality.html")
PATTERN = "statarb-slides-*.html"
PARTS = range(1, 9)
MINUS = "\u2212"                   # เครื่องหมายลบจริง (ไม่ใช่ขีดกลาง)
VS16 = "\ufe0f"                    # ตัวเลือกรูปอีโมจิ — บางคนพิมพ์ติดมา บางคนไม่ ต้องเทียบแบบไม่สนใจ
TERM_CAP = 12
LONG_RUN = 420
MAX_NUM_WARN = 40
SNIPPET_TIMEOUT = 300              # วินาที ต่อหนึ่ง snippet
SNIPPET_MAX_LINES = 40

VOID = {"br", "hr", "img", "meta", "link", "input", "wbr", "source", "col",
        # แท็กใบของ SVG (เขียนแบบปิดในตัว หรือเปิด-ปิดคู่กันก็ได้) — แนวเดียวกับ tools/nq_qa.py
        "path", "rect", "line", "circle", "ellipse", "polygon", "polyline", "stop", "use",
        "fedropshadow", "fegaussianblur", "feoffset", "feflood", "fecomposite", "femergenode"}

# (ชื่อที่แสดง, สิ่งที่ต้องเจอในหน้า) — ดู bible §6
BOXES = [
    ("🧭 เส้นทางอ่าน", "🧭 เส้นทางอ่าน"), ("ประโยคทอง .pq", re.compile(r'class="[^"]*\bpq\b')),
    ("🖼️ สไลด์บอกอะไร", "🖼️"), ("🔍 สิ่งที่สไลด์ไม่ได้บอก", "🔍"), ("🧪 ห้องทดลอง", "🧪"),
    ("🛠️ ทำเองกับข้อมูลของคุณ", "🛠️"), ("🎬 ฉากหน้าจอ", "🎬"), ("🧭 นิสัยคิด", "🧭 นิสัยคิด"),
    ("⚠️ ค่าเริ่มต้นที่แนะนำ", "⚠️ ค่าเริ่มต้น"), ("📉 เมื่อทฤษฎีพังจริง", "📉"), ("✍️ ลองทำเอง", "✍️ ลองทำเอง"),
    ("🎯 3 อย่างที่ต้องจำ", "🎯 3 อย่าง"), ("📚 Papers", "📚"), ("📖 อ่านต่อ", "📖 อ่านต่อ"),
    ("📖 ศัพท์ใหม่ในตอนนี้", "📖 ศัพท์ใหม่ในตอนนี้"),
]
NO_SLIDE_PARTS = {5, 8}            # ตอนที่ไม่มีสไลด์ต้นทาง → ไม่บังคับ 🖼️

CHART_NAME = re.compile(r"sas-p([1-8])-[a-z0-9][a-z0-9-]*")
SNIPPET_NAME = re.compile(r"p([1-8])_[a-z0-9][a-z0-9_]*")
SPAN_F =re.compile(r"<span\b(?=[^>]*\bdata-f\s*=)([^>]*)>(.*?)</span>", re.S)
ATTR_F = re.compile(r'\bdata-f\s*=\s*"([^"]*)"')
THAI = re.compile(r"[\u0E00-\u0E7F]")


# ───────────────────────── รายงานผล ─────────────────────────

class Log:
    """เก็บ error (✗) / warning (⚠) แล้วพิมพ์รวมตอนจบแต่ละคำสั่ง"""

    def __init__(self):
        self.errors = 0
        self.warnings = 0
        self._items = []

    def err(self, where, msg, line=None):
        self.errors += 1
        self._items.append(("✗", where, line, msg))

    def warn(self, where, msg, line=None):
        self.warnings += 1
        self._items.append(("⚠", where, line, msg))

    def flush(self):
        # error ก่อน warning · เรียงตามไฟล์และบรรทัด · รูปแบบ ไฟล์:บรรทัด: ข้อความ
        for mark, where, line, msg in sorted(self._items, key=lambda it: (it[0] != "✗", it[1], it[2] or 0)):
            print(f"  {mark} {where}" + (f":{line}" if line else "") + f": {msg}")
        self._items = []


def rel(path):
    try:
        r = os.path.relpath(path, ROOT)
    except ValueError:
        return path
    return path if r.startswith("..") else r


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def write_if_changed(path, new, old):
    if new == old:
        return False
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(new)
    return True


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def targets(paths):
    """ไฟล์ HTML ที่จะทำงานด้วย — ระบุมา = เฉพาะไฟล์นั้น · ไม่ระบุ = ทั้งชุดใน docs/"""
    if paths:
        missing = [p for p in paths if not os.path.isfile(p)]
        if missing:
            raise SystemExit("✗ ไม่พบไฟล์ (file not found): " + ", ".join(missing))
        return [os.path.abspath(p) for p in paths]
    return sorted(glob.glob(os.path.join(DOCS, PATTERN)))


def part_of(path):
    """'index' · หมายเลขตอน 1–8 · หรือ None ถ้าชื่อไฟล์ไม่ใช่หน้าของชุดนี้"""
    name = os.path.basename(path)
    if re.search(r"-index\.html$", name):
        return "index"
    m = re.search(r"-part([1-8])\.html$", name)
    return int(m.group(1)) if m else None


# ───────────────────────── figures.json ─────────────────────────

_FIG_CACHE = {}


def load_figures():
    """อ่าน figures.json (คืน None ถ้ายังไม่มีไฟล์)"""
    if not os.path.isfile(FIG_PATH):
        return None
    key = (os.path.getmtime(FIG_PATH), os.path.getsize(FIG_PATH))
    if _FIG_CACHE.get("key") != key:
        with open(FIG_PATH, encoding="utf-8") as fh:
            try:                                     # ถ้ามีคนกำลังรัน figures อยู่ รอให้เขียนจบก่อน (ไม่อ่านไฟล์ครึ่ง ๆ)
                import fcntl
                fcntl.flock(fh, fcntl.LOCK_SH)
            except (ImportError, OSError):
                pass
            raw = fh.read()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            raise SystemExit(f"✗ {rel(FIG_PATH)} อ่านเป็น JSON ไม่ได้ ({e}) — สร้างใหม่ด้วยคำสั่ง figures") from None
        if not isinstance(data, dict):
            raise SystemExit(f"✗ {rel(FIG_PATH)} ต้องเป็น object ที่ชั้นบนสุด — สร้างใหม่ด้วยคำสั่ง figures")
        _FIG_CACHE["key"], _FIG_CACHE["data"] = key, data
    return _FIG_CACHE["data"]


def resolve(fig, path):
    """ค่าที่ dot path ชี้ถึง · ดัชนีลิสต์เขียน a.3 หรือ a[3] · คีย์ที่มีจุดอยู่ข้างใน (เช่น "0.5") ก็หาเจอ
    หาไม่เจอ → LookupError พร้อมคำอธิบายว่าหลุดตรงไหนและมีคีย์อะไรให้เลือก"""
    segs = [s for s in re.sub(r"\[(-?\d+)\]", r".\1", path.strip()).split(".")]
    deepest = [0, fig]

    def walk(node, i):
        if i > deepest[0]:
            deepest[0], deepest[1] = i, node
        if i == len(segs):
            return node
        if isinstance(node, list):
            if re.fullmatch(r"-?\d+", segs[i]) and -len(node) <= int(segs[i]) < len(node):
                return walk(node[int(segs[i])], i + 1)
            raise LookupError
        if isinstance(node, dict):
            for j in range(i + 1, len(segs) + 1):
                key = ".".join(segs[i:j])
                if key in node:
                    try:
                        return walk(node[key], j)
                    except LookupError:
                        continue
        raise LookupError

    try:
        return walk(fig, 0)
    except LookupError:
        i, node = deepest
        at = ".".join(segs[:i]) or "(ราก)"
        if isinstance(node, dict):
            have = ", ".join(list(node)[:14]) + (" …" if len(node) > 14 else "")
            hint = f'ไม่มีคีย์ "{segs[i]}" ใต้ {at} — มี: {have}'
        elif isinstance(node, list):
            hint = f'{at} เป็นลิสต์ยาว {len(node)} — "{segs[i]}" ไม่ใช่ดัชนีที่ใช้ได้'
        else:
            hint = f"{at} เป็นค่าเดี่ยวแล้ว ลงลึกต่อไม่ได้"
        raise LookupError(hint) from None


def fmt_value(v, absolute=False):
    """จัดรูปค่าจาก JSON ให้เป็นข้อความที่ปรากฏในบท (กติกาเดียวกันทั้ง fill และ check)"""
    if isinstance(v, bool) or v is None or isinstance(v, (dict, list)):
        kind = "null" if v is None else type(v).__name__
        raise TypeError(f"ค่าเป็น {kind} — data-f ต้องชี้ไปที่ตัวเลขหรือข้อความเดี่ยว")
    if isinstance(v, int):
        s = f"{abs(v) if absolute else v:,}"
    elif isinstance(v, float):
        if not math.isfinite(v):
            raise TypeError("ค่าเป็น NaN/inf")
        x = abs(v) if (absolute or v == 0) else v
        s = repr(x)                              # ทศนิยมตามที่เก็บไว้ (12.0 → "12.0" · อยากได้ "12" ให้เก็บเป็น int)
        if "e" in s or "E" in s:
            s = format(Decimal(s), "f")
        whole, dot, frac = s.lstrip("-").partition(".")
        s = ("-" if s.startswith("-") else "") + f"{int(whole):,}" + dot + frac    # คั่นหลักพันเหมือน int
    else:
        s = html.escape(str(v), quote=False)
        if absolute:
            s = s.lstrip("-" + MINUS)
    return MINUS + s[1:] if s.startswith("-") else s


def json_problems(obj, path, errs, warns):
    """ตรวจว่าเป็นค่า JSON แท้ ไม่มี NaN/inf · เตือนค่าที่ดูเหมือนยังไม่ได้ปัด"""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if not isinstance(k, str):
                errs.append(f"{path}: คีย์ {k!r} ไม่ใช่ข้อความ (key must be str)")
                continue
            if not re.fullmatch(r"[A-Za-z0-9_]+", k):
                warns.append(f"{path}.{k}: คีย์ควรเป็น ASCII snake_case")
            json_problems(v, f"{path}.{k}", errs, warns)
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            json_problems(v, f"{path}.{i}", errs, warns)
    elif obj is None:
        warns.append(f"{path}: เป็น null (C.rd คืน None เมื่อค่าไม่ finite) — data-f จะใช้ค่านี้ไม่ได้")
    elif type(obj) in (bool, int, str) or isinstance(obj, str):
        pass
    elif isinstance(obj, float):
        if not math.isfinite(obj):
            errs.append(f"{path}: {obj!r} (NaN/inf) เก็บลง JSON ไม่ได้")
        elif len(repr(float(obj)).split("e")[0].partition(".")[2]) > 6:
            warns.append(f"{path}: {float(obj)!r} ดูเหมือนยังไม่ได้ปัด (ใช้ C.rd / C.pct / C.bps)")
    else:
        t = type(obj)
        errs.append(f"{path}: ชนิด {t.__module__}.{t.__name__} ไม่ใช่ค่า JSON "
                    "(แปลงด้วย C.rd(), int(), float(), .tolist() ก่อน)")


# ───────────────────────── โมดูลทดลอง ─────────────────────────

_MODS, _CHARTS, _CHART_WARNED = {}, {}, set()


def exp_path(n):
    return os.path.join(EXP_DIR, f"sas_exp{n}.py")


def load_exp(n):
    if n not in _MODS:
        for d in (TOOLS, EXP_DIR):
            if d not in sys.path:
                sys.path.insert(0, d)
        _MODS[n] = importlib.import_module(f"sas_exp{n}")
    return _MODS[n]


def charts_of(n):
    """{ชื่อกราฟ: html} ของตอน n (รัน charts() ครั้งเดียวต่อการเรียกสคริปต์)"""
    if n not in _CHARTS:
        out = load_exp(n).charts()
        if not isinstance(out, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in out.items()):
            raise TypeError(f"sas_exp{n}.charts() ต้องคืน dict ของ {{ชื่อ: html}}")
        _CHARTS[n] = out
    return _CHARTS[n]


def chart_warnings(n):
    """ข้อสังเกตเกี่ยวกับผลของ sas_exp<n>.charts() (รายงานครั้งเดียวต่อการเรียกสคริปต์)
    ชื่อผิดรูป = วางในหน้าไม่ได้ · id ที่ไม่ขึ้นต้นด้วยชื่อกราฟ = เสี่ยงชนกับกราฟอื่นในหน้าเดียวกัน"""
    if n in _CHART_WARNED or n not in _CHARTS:
        return []
    _CHART_WARNED.add(n)
    out = []
    for name, svg in _CHARTS[n].items():
        m = CHART_NAME.fullmatch(name)
        if not m or int(m.group(1)) != n:
            out.append(f'charts(): ชื่อ "{name}" ไม่อยู่ในรูป sas-p{n}-<slug> — วางในหน้าไม่ได้')
        stray = [i for i in re.findall(r'\sid="([^"]+)"', svg) if not i.startswith(name + "-")]
        if stray:
            out.append(f'charts(): กราฟ "{name}" มี id ที่ไม่ขึ้นต้นด้วยชื่อกราฟ ({", ".join(stray[:3])}) '
                       "— ใช้ชื่อกราฟเป็น cid ของตัวสร้าง ไม่งั้น id อาจชนกับกราฟอื่นในหน้าเดียวกัน")
    return out


def chart_problem(name):
    """None ถ้าชื่อกราฟนี้มีเจ้าของจริง · ไม่งั้นคืนข้อความอธิบาย (ไม่รันการทดลองถ้าไม่จำเป็น)"""
    m = CHART_NAME.fullmatch(name)
    if not m:
        return "ชื่อกราฟต้องเป็นรูป sas-p<1-8>-<slug ตัวเล็ก/ตัวเลข/ขีด>"
    n = int(m.group(1))
    if not os.path.isfile(exp_path(n)):
        return f"ยังไม่มีโมดูล {rel(exp_path(n))}"
    if n not in _CHARTS and name in read(exp_path(n)):
        return None                                  # เจอชื่อในซอร์สของโมดูล — ถือว่ามี (ไม่ต้องรัน)
    try:
        have = charts_of(n)
    except Exception as e:                           # noqa: BLE001 — รายงานแล้วไปต่อ
        return f"เรียก sas_exp{n}.charts() ไม่สำเร็จ: {type(e).__name__}: {e}"
    if name in have:
        return None
    return f"sas_exp{n}.charts() ไม่มีชื่อนี้ — ที่มี: " + (", ".join(sorted(have)) or "(ว่าง)")


# ───────────────────────── ที่เสียบ <!--KIND:name--> ─────────────────────────

def find_blocks(text, kind):
    """คู่ <!--KIND:name--> … <!--/KIND:name--> → ([(name, เริ่มเนื้อใน, จบเนื้อใน, บรรทัด)], [(บรรทัด, ปัญหา)])"""
    blocks, errs, cur = [], [], None
    for m in re.finditer(r"<!--(/?)" + kind + r":(.*?)-->", text, re.S):
        name, ln = m.group(2).strip(), line_of(text, m.start())
        if not m.group(1):
            if cur:
                errs.append((cur[2], f"<!--{kind}:{cur[0]}--> ไม่มีตัวปิด <!--/{kind}:{cur[0]}-->"))
            cur = (name, m.end(), ln)
        elif cur and cur[0] == name:
            blocks.append((name, cur[1], m.start(), cur[2]))
            cur = None
        else:
            errs.append((ln, f"<!--/{kind}:{name}--> ไม่มีตัวเปิดที่ชื่อตรงกัน"))
    if cur:
        errs.append((cur[2], f"<!--{kind}:{cur[0]}--> ไม่มีตัวปิด <!--/{kind}:{cur[0]}-->"))
    return blocks, errs


def splice(text, edits):
    """แทนที่ช่วง [(start, end, ข้อความใหม่)] โดยไล่จากท้ายไฟล์ (ตำแหน่งข้างหน้าไม่เลื่อน)"""
    for a, b, new in sorted(edits, reverse=True):
        text = text[:a] + new + text[b:]
    return text


def overlapping(edits):
    """True ถ้ามีช่วงแทนที่สองช่วงซ้อนกัน (เช่น วาง CODE ไว้ในบล็อก RUN) — splice จะทำไฟล์พัง"""
    spans = sorted((a, b) for a, b, _ in edits)
    return any(b0 > a1 for (_, b0), (a1, _) in zip(spans, spans[1:]))


def out_html(value):
    return '\n<pre class="out">' + html.escape(str(value).rstrip("\n"), quote=False) + "</pre>\n"


# ───────────────────────── snippet (CODE / RUN) ─────────────────────────

_RUNS = {}


def snippet_path(name):
    return os.path.join(SNIPPET_DIR, name + ".py")


def snippet_problem(name):
    """None ถ้ามีไฟล์ snippet ชื่อนี้ · ไม่งั้นคืนข้อความอธิบาย"""
    if not SNIPPET_NAME.fullmatch(name):
        return ("ชื่อ snippet ต้องเป็นรูป p<1-8>_<slug ตัวเล็ก/ตัวเลข/ขีดล่าง> "
                "(= ชื่อไฟล์ใน tools/sas_snippets/ ไม่มี .py)")
    if not os.path.isfile(snippet_path(name)):
        have = sorted(f[:-3] for f in os.listdir(SNIPPET_DIR) if f.endswith(".py")) if os.path.isdir(SNIPPET_DIR) else []
        return f"ไม่พบไฟล์ {rel(snippet_path(name))} — ที่มี: " + (", ".join(have) or "(ยังไม่มีสักไฟล์)")
    return None


def code_html(name):
    """ซอร์สของ snippet ทั้งไฟล์ ตามตัวอักษร ใน <pre class="code">"""
    return '\n<pre class="code">' + html.escape(read(snippet_path(name)).rstrip("\n"), quote=False) + "</pre>\n"


def run_snippet(name):
    """รันไฟล์ snippet แบบที่ผู้อ่านจะรัน (python3 ไฟล์ · cwd = รากของ repo · ไม่มีอาร์กิวเมนต์)
    ครั้งเดียวต่อการเรียกสคริปต์ → (stdout, ปัญหา หรือ None, คำเตือน หรือ None)"""
    if name not in _RUNS:
        env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONHASHSEED="0", PYTHONDONTWRITEBYTECODE="1")
        try:
            r = subprocess.run([sys.executable, snippet_path(name)], cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                               capture_output=True, encoding="utf-8", errors="replace", timeout=SNIPPET_TIMEOUT)
        except subprocess.TimeoutExpired:
            _RUNS[name] = (None, f"รันเกิน {SNIPPET_TIMEOUT} วินาทีแล้วยังไม่จบ", None)
        except OSError as e:
            _RUNS[name] = (None, f"เริ่มรันไม่ได้: {e}", None)
        else:
            err = r.stderr.strip()
            problem = warn = None
            if r.returncode != 0:
                problem = f"รันแล้วล้ม (exit code {r.returncode}):\n" + "\n".join(err.splitlines()[-8:])
            elif not r.stdout.strip():
                problem = "รันแล้วไม่พิมพ์อะไรออก stdout เลย — บล็อก RUN ต้องมีผลลัพธ์ให้แสดง"
            elif err:
                warn = "รันผ่าน แต่พิมพ์ข้อความออก stderr ด้วย (ผู้อ่านจะเห็นเหมือนกัน): " + err.splitlines()[-1][:160]
            _RUNS[name] = (r.stdout, problem, warn)
    return _RUNS[name]


# ───────────────────────── คำสั่ง: figures ─────────────────────────

def cmd_figures(paths, parts, log):
    if parts:
        wanted, partial = sorted(set(parts)), True
    elif paths:
        wanted = sorted({p for p in map(part_of, paths) if isinstance(p, int)})
        partial = True
        if not wanted:
            print("  ไฟล์ที่ระบุไม่มีโมดูลทดลองเป็นของตัวเอง (หน้า index) — ใช้ figures.json เดิม")
            return
    else:
        wanted, partial = list(PARTS), False
    skipped = [n for n in wanted if not os.path.isfile(exp_path(n))]
    if skipped and partial:                          # ขอตอนนี้มาโดยเจาะจง แต่ไม่มีโมดูล = ผิดพลาด ไม่ใช่ "ข้าม"
        for n in skipped:
            log.err(f"sas_exp{n}.py", f"ไม่พบโมดูลทดลองของตอน {n} ({rel(exp_path(n))})")
    elif skipped:
        print("  ข้าม (ยังไม่มีไฟล์ / skipped): " + ", ".join(f"sas_exp{n}.py" for n in skipped))
    new = {}
    for n in wanted:
        if n in skipped:
            continue
        try:
            data = load_exp(n).figures()
        except Exception:                            # noqa: BLE001 — ต้องล้มให้เห็นชัด
            log.err(f"sas_exp{n}.figures()", "ล้มระหว่างรัน:\n" + traceback.format_exc().rstrip())
            continue
        errs, warns = [], []
        if not isinstance(data, dict):
            errs.append(f"p{n}: figures() ต้องคืน dict (ได้ {type(data).__name__})")
        else:
            json_problems(data, f"p{n}", errs, warns)
        for e in errs:
            log.err(f"sas_exp{n}.figures()", e)
        for w in warns[:15]:
            log.warn(f"sas_exp{n}.figures()", w)
        if len(warns) > 15:
            log.warn(f"sas_exp{n}.figures()", f"… และอีก {len(warns) - 15} คำเตือนแบบเดียวกัน")
        if not errs:
            new[f"p{n}"] = json.loads(json.dumps(data, ensure_ascii=False, allow_nan=False))
            print(f"  p{n}: {sum(1 for _ in _leaves(new[f'p{n}'])):,} ค่า จาก sas_exp{n}.py")
    if log.errors:
        log.flush()
        print(f"  ✗ ไม่เขียน {rel(FIG_PATH)} เพราะมี error ข้างบน (ไฟล์เดิมไม่ถูกแตะ)")
        return
    if not new:
        print("  ไม่มีผลจากโมดูลทดลองตัวไหนเลย — ไม่แตะ figures.json")
        return
    try:
        import fcntl
    except ImportError:                              # ไม่ใช่ POSIX — เขียนแบบไม่ล็อก
        fcntl = None
    os.makedirs(os.path.dirname(FIG_PATH), exist_ok=True)
    fd = os.open(FIG_PATH, os.O_RDWR | os.O_CREAT, 0o644)
    with os.fdopen(fd, "r+", encoding="utf-8") as fh:
        if fcntl:                                    # กันสองคนรัน figures พร้อมกันแล้วเขียนทับกัน
            fcntl.flock(fh, fcntl.LOCK_EX)
        old = fh.read()
        try:
            cur = json.loads(old) if (old.strip() and partial) else {}
            if not isinstance(cur, dict):
                raise ValueError("ชั้นบนสุดไม่ใช่ object")
        except ValueError as e:                      # รวมกับไฟล์เดิมไม่ได้ — อย่าเขียนทับของคนอื่นเงียบ ๆ
            log.err(rel(FIG_PATH), f"ไฟล์เดิมอ่านเป็น JSON ไม่ได้ ({e}) — รัน figures แบบไม่ระบุตอนเพื่อสร้างใหม่ทั้งไฟล์")
            return
        merged = {k: v for k, v in cur.items() if k != "meta"}
        merged.update(new)
        keys = sorted(merged, key=lambda k: (not re.fullmatch(r"p\d+", k), int(k[1:]) if k[1:].isdigit() else 0, k))
        meta = {"series": "แกะสไลด์ Stat Arb", "generator": "python3 tools/sas_build.py figures",
                "parts": keys,
                "note": "ทุกค่าปัดแล้วตามที่ปรากฏในบท · ห้ามแก้ด้วยมือ · สร้างใหม่ด้วยคำสั่ง generator"}
        try:
            for d in (TOOLS, EXP_DIR):
                if d not in sys.path:
                    sys.path.insert(0, d)
            meta["seed"] = int(importlib.import_module("sas_core").SEED)
        except Exception:                            # noqa: BLE001 — seed เป็นข้อมูลประกอบเท่านั้น
            pass
        text = json.dumps({"meta": meta, **{k: merged[k] for k in keys}}, ensure_ascii=False, indent=1,
                          allow_nan=False) + "\n"
        if text != old:
            fh.seek(0)
            fh.truncate()
            fh.write(text)
            print(f"  เขียน {rel(FIG_PATH)} ({len(keys)} ตอน: {', '.join(keys)})")
        else:
            print(f"  {rel(FIG_PATH)} ไม่เปลี่ยน")
    _FIG_CACHE.clear()


def _leaves(obj):
    if isinstance(obj, dict):
        for v in obj.values():
            yield from _leaves(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _leaves(v)
    else:
        yield obj


# ───────────────────────── คำสั่ง: charts / fill / out ─────────────────────────

def cmd_charts(files, log):
    for path in files:
        text = read(path)
        blocks, errs = find_blocks(text, "CHART")
        for ln, e in errs:
            log.err(rel(path), e, ln)
        edits = []
        for name, a, b, ln in blocks:
            m = CHART_NAME.fullmatch(name)
            if not m:
                log.err(rel(path), f'CHART "{name}": ชื่อกราฟต้องเป็นรูป sas-p<1-8>-<slug>', ln)
                continue
            n = int(m.group(1))
            if not os.path.isfile(exp_path(n)):
                log.err(rel(path), f'CHART "{name}": ยังไม่มีโมดูล {rel(exp_path(n))}', ln)
                continue
            try:
                have = charts_of(n)
            except Exception:                        # noqa: BLE001
                log.err(rel(path), f'CHART "{name}": sas_exp{n}.charts() ล้ม:\n' + traceback.format_exc().rstrip(), ln)
                continue
            for w in chart_warnings(n):
                log.warn(rel(exp_path(n)), w)
            if name not in have:
                log.err(rel(path), f'CHART "{name}" ไม่มีใน sas_exp{n}.charts() — ที่มี: '
                        + (", ".join(sorted(have)) or "(ว่าง)"), ln)
                continue
            edits.append((a, b, "\n" + have[name].strip("\n") + "\n"))
        if write_if_changed(path, splice(text, edits), text):
            print(f"  อัปเดตกราฟ {len(edits)} ชิ้นใน {rel(path)}")


def _need_figures(path, log, what):
    fig = load_figures()
    if fig is None:
        log.err(rel(path), f"มี {what} แต่ยังไม่มี {rel(FIG_PATH)} — รัน figures ก่อน")
    return fig


def cmd_fill(files, log):
    for path in files:
        text = read(path)
        spans = list(SPAN_F.finditer(text))
        if not spans:
            continue
        fig = _need_figures(path, log, "data-f")
        if fig is None:
            continue
        edits = []
        for m in spans:
            ln = line_of(text, m.start())
            f = ATTR_F.search(m.group(1))
            if not f:
                log.err(rel(path), 'data-f ต้องเขียนแบบ data-f="dot.path" (ใช้อัญประกาศคู่)', ln)
                continue
            if "<" in m.group(2):
                log.err(rel(path), f'data-f="{f.group(1)}": ใน <span> ต้องมีแต่ข้อความ ห้ามมีแท็กซ้อน', ln)
                continue
            try:
                new = fmt_value(resolve(fig, f.group(1)), bool(re.search(r"\bdata-abs\b", m.group(1))))
            except (LookupError, TypeError) as e:
                log.err(rel(path), f'data-f="{f.group(1)}": {e}', ln)
                continue
            edits.append((m.start(2), m.end(2), new))
        if write_if_changed(path, splice(text, edits), text):
            print(f"  เติมตัวเลขใน {rel(path)} ({len(edits)} จุด)")


def cmd_out(files, log):
    for path in files:
        text = read(path)
        blocks, errs = find_blocks(text, "OUT")
        for ln, e in errs:
            log.err(rel(path), e, ln)
        if not blocks:
            continue
        fig = _need_figures(path, log, "<!--OUT:…-->")
        if fig is None:
            continue
        edits = []
        for name, a, b, ln in blocks:
            try:
                v = resolve(fig, name)
            except LookupError as e:
                log.err(rel(path), f'OUT "{name}": {e}', ln)
                continue
            if not isinstance(v, str):
                log.err(rel(path), f'OUT "{name}": ค่าต้องเป็นข้อความ (ได้ {type(v).__name__})', ln)
                continue
            edits.append((a, b, out_html(v)))
        if write_if_changed(path, splice(text, edits), text):
            print(f"  เติมผลลัพธ์โปรแกรม {len(edits)} ชิ้นใน {rel(path)}")


def cmd_snippets(files, log):
    for path in files:
        text = read(path)
        edits, counts = [], {"CODE": 0, "RUN": 0}
        for kind in ("CODE", "RUN"):
            blocks, errs = find_blocks(text, kind)
            for ln, e in errs:
                log.err(rel(path), e, ln)
            for name, a, b, ln in blocks:
                problem = snippet_problem(name)
                if problem:
                    log.err(rel(path), f'{kind} "{name}": {problem}', ln)
                    continue
                if kind == "CODE":
                    edits.append((a, b, code_html(name)))
                else:
                    stdout, problem, warn = run_snippet(name)
                    if problem:
                        log.err(rel(path), f'RUN "{name}": {rel(snippet_path(name))} {problem}', ln)
                        continue
                    if warn:
                        log.warn(rel(path), f'RUN "{name}": {warn}', ln)
                    edits.append((a, b, out_html(stdout)))
                counts[kind] += 1
        if overlapping(edits):
            log.err(rel(path), "บล็อก CODE / RUN ซ้อนกันอยู่ — วางให้เป็นบล็อกแยกกัน (ไฟล์ไม่ถูกแก้)")
            continue
        if write_if_changed(path, splice(text, edits), text):
            print(f"  เติม snippet ใน {rel(path)} (โค้ด {counts['CODE']} · ผลลัพธ์ {counts['RUN']})")


def cmd_shell(files, log):
    """เปลือกของหน้า = CSS สองบล็อกใน <head> + Thai line-break script · เนื้อหาระหว่างนั้นไม่ถูกแตะ"""
    css, script = ref_styles(), ref_script()
    if css is None or script is None:
        log.err(rel(REF_PAGE), "อ่านเปลือกต้นแบบไม่ได้ (ต้องมี <style> หนึ่งบล็อกใน <head> และ Thai line-break script)")
        return
    for path in files:
        text = read(path)
        cut = text.find("<body>")
        styles = list(re.finditer(r"<style>.*?</style>", text[:max(cut, 0)], re.S))
        scripts = [m for m in re.finditer(r"<script>.*?</script>", text, re.S) if "data-thwbr" in m.group(0)]
        if cut < 0 or len(styles) < 2 or len(scripts) != 1:
            log.err(rel(path), "เปลือกผิดรูป (ต้องมี <style> สองบล็อกใน <head> และ Thai line-break script หนึ่งบล็อก) "
                               "— สร้างเปลือกใหม่ด้วย tools/sas_new_part.py แล้วย้ายเนื้อหามา")
            continue
        edits = [(styles[0].start(), styles[0].end(), css[0]), (styles[1].start(), styles[1].end(), css[1]),
                 (scripts[0].start(), scripts[0].end(), script)]
        if write_if_changed(path, splice(text, edits), text):
            print(f"  อัปเดตเปลือกของ {rel(path)}")


# ───────────────────────── คำสั่ง: check ─────────────────────────

class Balance(HTMLParser):
    """แท็กเปิด-ปิดต้องสมดุล (แนวเดียวกับ tools/nq_qa.py · แท็กปิดในตัวใช้ได้เฉพาะใน <svg>)"""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.errors, self.svg = [], [], 0

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        self.svg += tag == "svg"
        self.stack.append((tag, self.getpos()[0]))

    def handle_startendtag(self, tag, attrs):
        if tag not in VOID and not self.svg:
            self.errors.append((self.getpos()[0], f"<{tag}/> ปิดในตัวไม่ได้ใน HTML — ใช้ <{tag}></{tag}>"))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        ln = self.getpos()[0]
        depth = next((i for i in range(len(self.stack) - 1, -1, -1) if self.stack[i][0] == tag), None)
        if depth is None:
            self.errors.append((ln, f"</{tag}> ปิดเกินมา (ไม่มีตัวเปิด)"))
            return
        for t, opened in self.stack[depth + 1:]:
            self.errors.append((opened, f"<{t}> เปิดแล้วไม่ได้ปิด (เจอ </{tag}> ที่บรรทัด {ln} ก่อน)"))
        self.svg -= sum(1 for t, _ in self.stack[depth:] if t == "svg")
        del self.stack[depth:]


class Prose(HTMLParser):
    """ดึง "ข้อความที่ผู้อ่านเห็น" ออกมา โดยข้ามส่วนที่ไม่ใช่ร้อยแก้ว
    (script · style · pre · code · svg · หัวตาราง · .fm · span[data-f] · ในบล็อก CHART/OUT)"""

    SKIP = {"script", "style", "pre", "code", "svg", "th", "title"}
    BLOCK = {"p", "li", "td", "th", "div", "h1", "h2", "h3", "h4", "dt", "dd", "summary", "details",
             "ul", "ol", "table", "tr", "blockquote", "pre", "body", "br"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.skip, self.marker = [], 0, 0
        self.runs, self.blocks = [], []          # (บรรทัด, ข้อความระหว่างแท็ก) · (บรรทัด, ข้อความทั้งบล็อก)
        self._buf, self._line = [], None

    def _flush(self):
        if self._buf:
            self.blocks.append((self._line, " ".join("".join(self._buf).split())))
        self._buf, self._line = [], None

    def handle_starttag(self, tag, attrs):
        if tag in self.BLOCK:
            self._flush()
        if tag in VOID:
            return
        a = dict(attrs)
        skip = (tag in self.SKIP or (tag == "span" and "data-f" in a)
                or "fm" in (a.get("class") or "").split())
        self.stack.append((tag, skip))
        self.skip += skip

    def handle_startendtag(self, tag, attrs):
        if tag in self.BLOCK:
            self._flush()

    def handle_endtag(self, tag):
        if tag in self.BLOCK:
            self._flush()
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                self.skip -= sum(s for _, s in self.stack[i:])
                del self.stack[i:]
                break

    def handle_comment(self, data):
        d = data.strip()
        if re.match(r"(CHART|OUT|CODE|RUN):", d):
            self.marker += 1
        elif re.match(r"/(CHART|OUT|CODE|RUN):", d):
            self.marker = max(0, self.marker - 1)

    def handle_data(self, data):
        if self.skip or self.marker or not data.strip():
            return
        ln = self.getpos()[0]
        self.runs.append((ln, data))
        if self._line is None:
            self._line = ln
        self._buf.append(data)

    def close(self):
        super().close()
        self._flush()


_REF = {}


def ref_script():
    """บล็อก <script> ตัดคำไทยต้นฉบับ (จาก docs/statarb-data-quality.html) — ทุกหน้าต้องมีเหมือนกันเป๊ะ"""
    if "s" not in _REF:
        found = [s for s in re.findall(r"<script>.*?</script>", read(REF_PAGE), re.S) if "data-thwbr" in s]
        _REF["s"] = found[-1] if found else None
    return _REF["s"]


def ref_styles():
    """(บล็อก <style> ของทั้งคลัง จากหน้าต้นแบบ, บล็อก <style> ของชุดนี้ จาก tools/sas_new_part.py)
    = สองบล็อกแรกใน <head> ที่ทุกหน้าของชุดต้องมีเหมือนกันเป๊ะ · None ถ้าอ่านต้นแบบไม่ได้"""
    if "css" not in _REF:
        _REF["css"] = None
        try:
            src = read(REF_PAGE)
            lib = re.findall(r"<style>.*?</style>", src[:max(src.find("<body>"), 0)], re.S)
            if TOOLS not in sys.path:
                sys.path.insert(0, TOOLS)
            if len(lib) == 1:
                _REF["css"] = (lib[0], importlib.import_module("sas_new_part").SERIES_CSS)
        except (OSError, ImportError, AttributeError):
            pass
    return _REF["css"]


def _snip(s, a, b, pad=28):
    lo, hi = max(0, a - pad), min(len(s), b + pad)
    return ("…" if lo else "") + " ".join(s[lo:hi].split()) + ("…" if hi < len(s) else "")


def _glossary_count(text):
    """จำนวนคำในกล่อง "📖 ศัพท์ใหม่ในตอนนี้" (นับ <li> · ไม่มีก็นับ <dt> · แถวตาราง · หรือ <strong>)"""
    i = text.find("📖 ศัพท์ใหม่ในตอนนี้")
    if i < 0:
        return None
    start = text.find("</div>", i)
    if start < 0:
        return None
    depth, pos = 1, start + 6
    for m in re.finditer(r"<(/?)div\b", text[pos:]):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            box = text[pos:pos + m.start()]
            break
    else:
        box = text[pos:]
    for pat in (r"<li\b", r"<dt\b"):
        n = len(re.findall(pat, box))
        if n:
            return n
    n = len(re.findall(r"<tr\b", box))
    if n > 1:
        return n - 1
    terms = re.findall(r"<strong>(.*?)</strong>", box, re.S)
    return len([t for t in terms if not t.strip().startswith(("3 คำ", "ที่เหลือ"))])


def check_file(path, log, strict=False, run=True):
    name = rel(path)
    text = read(path)
    part = part_of(path)
    if "<!--BODY-->" in text:
        log.err(name, "ยังมี <!--BODY--> ของเปลือกค้างอยู่ — แทนที่ด้วยเนื้อหา", line_of(text, text.index("<!--BODY-->")))

    # 1) โครงสร้าง HTML สมดุล
    bal = Balance()
    bal.feed(text)
    bal.close()
    for ln, e in bal.errors:
        log.err(name, e, ln)
    for tag, ln in bal.stack:
        log.err(name, f"<{tag}> เปิดแล้วไม่ได้ปิด", ln)

    body = re.sub(r"<(script|style)\b.*?</\1>", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)

    # 2) <br> ปลอมจำลองรายการ
    for m in re.finditer(r"<br\s*/?>\s*(?:•|▪|·\s|[-–]\s|\d+[.)]\s)", body):
        log.err(name, "<br> จำลองรายการ — ใช้ <ul>/<ol><li> จริง", line_of(body, m.start()))

    # 3) ลิงก์ภายในต้องมีไฟล์จริงใน docs/
    seen = set()
    for m in re.finditer(r'href="([^"#:?]+\.html)(?:[#?][^"]*)?"', body):
        href = m.group(1)
        if href in seen:
            continue
        seen.add(href)
        if not os.path.isfile(os.path.normpath(os.path.join(DOCS, href))):
            sibling = re.fullmatch(r"statarb-slides-(index|part[1-8])\.html", href)
            msg = f'ลิงก์ไป "{href}" ซึ่งไม่มีไฟล์ใน docs/'
            if sibling and not strict:
                log.warn(name, msg + " (หน้าในชุดเดียวกันที่ยังไม่ถูกเขียน — เป็น error เมื่อรันด้วย --strict)",
                         line_of(body, m.start()))
            else:
                log.err(name, msg + (" — หน้าในชุดเดียวกันที่ยังไม่ถูกเขียน (--strict)" if sibling
                                     else " — บทของหนังสือเล่มเก่าให้เขียนเป็น <code>ชื่อบท</code> ไม่ใช่ลิงก์"),
                        line_of(body, m.start()))

    # 4) data-f ต้องชี้ค่าจริง และข้อความต้องตรงกับ JSON
    for m in re.finditer(r"<(?!span\b)(\w+)\b[^>]*\bdata-f\s*=", body):
        log.err(name, f"data-f ใช้ได้กับ <span> เท่านั้น (เจอบน <{m.group(1)}>)", line_of(body, m.start()))
    spans = list(SPAN_F.finditer(body))
    outs, out_errs = find_blocks(body, "OUT")
    fig = load_figures()
    if (spans or outs) and fig is None:
        log.err(name, f"มี data-f / OUT แต่ยังไม่มี {rel(FIG_PATH)} — รัน figures ก่อน")
    elif fig is not None:
        for m in spans:
            ln = line_of(body, m.start())
            f = ATTR_F.search(m.group(1))
            if not f:
                log.err(name, 'data-f ต้องเขียนแบบ data-f="dot.path" (ใช้อัญประกาศคู่)', ln)
                continue
            try:
                want = fmt_value(resolve(fig, f.group(1)), bool(re.search(r"\bdata-abs\b", m.group(1))))
            except (LookupError, TypeError) as e:
                log.err(name, f'data-f="{f.group(1)}": {e}', ln)
                continue
            if m.group(2) != want:
                log.err(name, f'data-f="{f.group(1)}": ในหน้าเขียน "{_snip(m.group(2), 0, 40, 0)}" '
                              f'แต่ JSON = "{want}" — รัน fill', ln)

    # 5) ที่เสียบ CHART / OUT ต้องมีเจ้าของและถูกเติมแล้ว
    charts, chart_errs = find_blocks(body, "CHART")
    for ln, e in chart_errs + out_errs:
        log.err(name, e, ln)
    placed = {}
    for cname, a, b, ln in charts:
        problem = chart_problem(cname)
        if problem:
            log.err(name, f'CHART "{cname}": {problem}', ln)
        elif "<svg" not in body[a:b]:
            log.err(name, f'CHART "{cname}" ยังว่าง — รัน charts', ln)
        if cname in placed:
            log.err(name, f'CHART "{cname}" ถูกวางซ้ำ (ครั้งแรกบรรทัด {placed[cname]}) — id ใน <defs> จะชนกัน '
                          "ถ้าต้องการกราฟเดิมอีกที่ ให้สร้างอีกชื่อใน charts()", ln)
        placed.setdefault(cname, ln)
    if fig is not None:
        for oname, a, b, ln in outs:
            try:
                v = resolve(fig, oname)
            except LookupError as e:
                log.err(name, f'OUT "{oname}": {e}', ln)
                continue
            if not isinstance(v, str):
                log.err(name, f'OUT "{oname}": ค่าใน JSON ต้องเป็นข้อความ (ได้ {type(v).__name__})', ln)
            elif not body[a:b].strip():
                log.err(name, f'OUT "{oname}" ยังว่าง — รัน out', ln)
            elif body[a:b] != out_html(v):
                log.err(name, f'OUT "{oname}" ไม่ตรงกับ JSON (ของเก่า หรือถูกแก้ด้วยมือ) — รัน out', ln)

    # 5b) snippet: CODE ต้องตรงกับไฟล์ทุกตัวอักษร · RUN ต้องตรงกับ stdout ที่รันได้ตอนนี้
    code_names, run_blocks = set(), []
    for kind in ("CODE", "RUN"):
        blocks, errs = find_blocks(body, kind)
        for ln, e in errs:
            log.err(name, e, ln)
        for sname, a, b, ln in blocks:
            problem = snippet_problem(sname)
            if problem:
                log.err(name, f'{kind} "{sname}": {problem}', ln)
            elif not body[a:b].strip():
                log.err(name, f'{kind} "{sname}" ยังว่าง — รัน snippets', ln)
            elif kind == "CODE":
                code_names.add(sname)
                if body[a:b] != code_html(sname):
                    log.err(name, f'CODE "{sname}" ไม่ตรงกับ {rel(snippet_path(sname))} '
                                  "(ไฟล์ถูกแก้หลังเติม หรือบล็อกถูกแก้ด้วยมือ) — รัน snippets", ln)
                n_lines = read(snippet_path(sname)).rstrip("\n").count("\n") + 1
                if n_lines > SNIPPET_MAX_LINES:
                    log.warn(name, f'CODE "{sname}": โค้ดยาว {n_lines} บรรทัด เกิน {SNIPPET_MAX_LINES} — ตัดให้สั้นลง', ln)
            else:
                run_blocks.append((sname, ln))
                if not run:
                    continue
                stdout, problem, warn = run_snippet(sname)
                if problem:
                    log.err(name, f'RUN "{sname}": {rel(snippet_path(sname))} {problem}', ln)
                elif body[a:b] != out_html(stdout):
                    log.err(name, f'RUN "{sname}" ไม่ตรงกับผลที่รันได้ตอนนี้ (ของเก่า หรือถูกแก้ด้วยมือ) — รัน snippets '
                                  "· ถ้ารันสองครั้งได้ไม่เท่ากัน snippet ต้องตรึง seed", ln)
                elif warn:
                    log.warn(name, f'RUN "{sname}": {warn}', ln)
    for sname, ln in run_blocks:
        if sname not in code_names:
            log.warn(name, f'RUN "{sname}" ไม่มี CODE "{sname}" ในหน้าเดียวกัน — ผู้อ่านจะไม่เห็นโค้ดที่ให้ผลลัพธ์นี้', ln)

    # 6) id ซ้ำในหน้าเดียว
    ids = {}
    for m in re.finditer(r'\sid\s*=\s*"([^"]+)"', body):
        ids.setdefault(m.group(1), []).append(line_of(body, m.start()))
    for i, lines in ids.items():
        if len(lines) > 1:
            log.err(name, f'id="{i}" ซ้ำ {len(lines)} ครั้ง (บรรทัด {", ".join(map(str, lines[:6]))})', lines[1])

    # 7) Thai line-break script ต้องมี และเหมือนต้นฉบับ
    ref = ref_script()
    mine = [s for s in re.findall(r"<script>.*?</script>", text, re.S) if "data-thwbr" in s]
    if ref is None:
        log.err(name, f"หาสคริปต์ต้นฉบับใน {rel(REF_PAGE)} ไม่เจอ — ตรวจ Thai line-break script ไม่ได้")
    elif not mine:
        log.err(name, "ไม่มี Thai line-break script ก่อน </body> (สร้างเปลือกด้วย tools/sas_new_part.py)")
    elif mine[-1] != ref or len(mine) > 1:
        log.err(name, f"Thai line-break script ถูกแก้หรือมีซ้ำ — ต้องเหมือนใน {rel(REF_PAGE)} ทุกตัวอักษร "
                      "(รัน shell เพื่อคืนของเดิม)")

    # 7b) CSS ของเปลือก: สองบล็อกแรกใน <head> ต้องเป็นของคลัง + ของชุด ตามที่ sas_new_part.py สร้าง (ห้ามแก้มือ)
    css = ref_styles()
    cut = text.find("<body>")
    if css is None:
        log.err(name, f"อ่าน CSS ต้นแบบไม่ได้ ({rel(REF_PAGE)} / tools/sas_new_part.py) — ตรวจเปลือกไม่ได้")
    elif cut < 0:
        log.err(name, "ไม่พบ <body> — สร้างเปลือกด้วย tools/sas_new_part.py")
    elif re.findall(r"<style>.*?</style>", text[:cut], re.S)[:2] != list(css):
        log.err(name, "CSS ใน <head> ไม่ตรงกับเปลือกมาตรฐาน (บล็อกแรก = ของทั้งคลัง · บล็อกสอง = ของชุดนี้) — "
                      "ห้ามแก้ CSS ของคลาสที่มีอยู่ด้วยมือ · รัน shell เพื่อคืน/อัปเดตเปลือก")

    # 8) กล่องบังคับ
    flat = text.replace(VS16, "")
    if part == "index":
        if "🧭" not in flat:
            log.err(name, "หน้า index ต้องมีกล่อง 🧭")
    elif isinstance(part, int):
        for label, needle in BOXES:
            if label.startswith("🖼") and part in NO_SLIDE_PARTS:
                continue
            ok = needle.search(flat) if hasattr(needle, "search") else needle.replace(VS16, "") in flat
            if not ok:
                log.err(name, f"ขาดกล่องบังคับ: {label}")

    # ── warning (ไม่ทำให้ล้ม) ──
    prose = Prose()
    prose.feed(text)
    prose.close()
    hits = []
    for ln, run in prose.runs:
        for m in re.finditer(r"(?<![\w.,])\d[\d,]*\.\d+\s?%?|(?<![\w.,])\d[\d,]*\s?%", run):
            hits.append((ln, m.group(0).strip(), _snip(run, m.start(), m.end())))
    for ln, num, ctx in hits[:MAX_NUM_WARN]:
        log.warn(name, f'ตัวเลข "{num}" ไม่อยู่ใน data-f — ถ้ามาจากห้องทดลองต้องติดป้าย: {ctx}', ln)
    if len(hits) > MAX_NUM_WARN:
        log.warn(name, f"… และตัวเลขที่ไม่ได้ติดป้ายอีก {len(hits) - MAX_NUM_WARN} จุด")
    n_terms = _glossary_count(text)
    if n_terms is not None and n_terms > TERM_CAP:
        log.warn(name, f"กล่องศัพท์ใหม่มี {n_terms} คำ เกินเพดาน {TERM_CAP}")
    for ln, run in prose.runs:
        flat_run = " ".join(run.split())
        if len(flat_run) > LONG_RUN and THAI.search(flat_run):
            log.warn(name, f"ข้อความไทยยาว {len(flat_run)} ตัวอักษรไม่มีแท็กคั่น — แบ่งย่อหน้าหรือทำเป็นรายการ: "
                           f"{flat_run[:60]}…", ln)
    for ln, block in prose.blocks:
        pos = [m.start() for m in re.finditer("—", block)]
        for a, b in zip(pos, pos[1:]):
            if b - a <= 150 and not re.search(r"[.!?]\s", block[a:b]):
                log.warn(name, f"em-dash สองตัวในประโยคเดียว: {_snip(block, a, b + 1, 18)}", ln)
                break


def cmd_check(files, log, strict=False, run=True):
    for path in files:
        check_file(path, log, strict, run)


# ───────────────────────── main ─────────────────────────

ORDER = ["figures", "charts", "fill", "out", "snippets", "check"]      # ลำดับของ all
COMMANDS = ORDER + ["shell"]


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):          # ข้อความมีภาษาไทยและ ✗ ⚠ — อย่าให้ล้มเพราะ locale ของเครื่อง
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="build tool ของชุดแกะสไลด์ Stat Arb",
                                 epilog="รายละเอียด: ดู docstring ต้นไฟล์ tools/sas_build.py")
    ap.add_argument("command", help=" | ".join(COMMANDS) + " | all (คั่นหลายคำสั่งด้วย ,)")
    ap.add_argument("files", nargs="*", help="ไฟล์ HTML (ไม่ระบุ = docs/statarb-slides-*.html)")
    ap.add_argument("--parts", help="เฉพาะ figures: หมายเลขตอนคั่นด้วย , เช่น 3,5")
    ap.add_argument("--strict", action="store_true",
                    help="เฉพาะ check: ลิงก์ไปหน้าในชุดเดียวกันที่ยังไม่ถูกเขียน = error (ปกติ = warning)")
    ap.add_argument("--draft", action="store_true", help="ไม่มีผลแล้ว (พฤติกรรมนี้เป็นค่าเริ่มต้น) — รับไว้เพื่อความเข้ากันได้")
    ap.add_argument("--no-run", action="store_true", help="เฉพาะ check: ไม่รัน snippet ซ้ำเพื่อเทียบกับบล็อก RUN")
    args = ap.parse_args(argv)

    cmds = []
    for c in args.command.split(","):
        c = c.strip()
        if c == "all":
            cmds += ORDER
        elif c in COMMANDS:
            cmds.append(c)
        else:
            ap.error(f"ไม่รู้จักคำสั่ง {c!r} — ใช้ได้: {', '.join(COMMANDS)}, all")
    parts = None
    if args.parts:
        try:
            parts = [int(p) for p in args.parts.split(",") if p.strip()]
        except ValueError:
            ap.error("--parts ต้องเป็นตัวเลข 1–8 คั่นด้วย ,")
        if any(p not in PARTS for p in parts):
            ap.error("--parts ต้องอยู่ในช่วง 1–8")

    files = targets(args.files)
    total_err = total_warn = 0
    for c in cmds:
        print(f"── {c} ──")
        log = Log()
        if c == "figures":
            cmd_figures(args.files, parts, log)
        elif not files:
            print(f"  ไม่พบไฟล์ docs/{PATTERN} — ยังไม่มีอะไรให้ทำ (no files)")
        elif c == "charts":
            cmd_charts(files, log)
        elif c == "fill":
            cmd_fill(files, log)
        elif c == "out":
            cmd_out(files, log)
        elif c == "snippets":
            cmd_snippets(files, log)
        elif c == "shell":
            cmd_shell(files, log)
        elif c == "check":
            cmd_check(files, log, args.strict, not args.no_run)
        log.flush()
        if c == "check" and files:
            verdict = "ผ่าน ✓" if not log.errors else "ไม่ผ่าน"
            print(f"  ตรวจ {len(files)} ไฟล์ · error {log.errors} · warning {log.warnings} · {verdict}")
        elif log.errors:
            print(f"  ✗ {c}: error {log.errors}")
        total_err += log.errors
        total_warn += log.warnings
        if c == "figures" and log.errors:
            break                                    # ไม่มีตัวเลขที่เชื่อได้ ขั้นถัดไปไม่มีความหมาย
    if total_err:
        print(f"✗ จบด้วย error {total_err} จุด (exit 1)")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
