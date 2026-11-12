#!/usr/bin/env python3
"""แยกต้นฉบับ v0.9 เป็นชิ้นวัตถุดิบต่อหัวข้อ และตรวจว่าทุกหัวข้อมีปลายทางในเล่มใหม่ (S1a/S1b)

ปลายทางมาจากตารางแปลงในแผน (docs/sab-book-plan.md หัวข้อ 8.1 + ตารางแรกของ 8.2)
แปลงเป็น tools/sab_srcmap.json ด้วย --build-map (สร้างใหม่ได้เสมอเมื่อแผนเปลี่ยน)

    python3 tools/sab_extract.py --build-map                   # แผน → tools/sab_srcmap.json
    python3 tools/sab_extract.py [ต้นฉบับ.md] --report map       # S1a: ทุกหัวข้อมีปลายทาง (เฟส 1 · ไม่ต้องมีบท)
    python3 tools/sab_extract.py --report tags --scope part4    # S1b: หัวข้อที่ปลายทาง "บท 4" มีป้าย <!--src:xx.xx--> ในบท
    python3 tools/sab_extract.py --dump 03.09                   # พิมพ์ชิ้นวัตถุดิบของหัวข้อ (ไว้เขียนบท)

ต้นฉบับ: อาร์กิวเมนต์แรกที่ลงท้าย .md หรือ $SAB_SOURCE_DIR/Part_I_v0_9_errata.md (สำเนาแก้ errata) ถ้ามี
ไม่เช่นนั้น $SAB_SOURCE_DIR/Stat_Arb_for_Non_Quant_Part_I_v0_9.md · SAB_SOURCE_DIR ตั้งต้น = sources/sab-v0_9
stdlib ล้วน (ในเครื่องไม่มีไลบรารี markdown)
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAN = os.path.join(ROOT, "docs", "sab-book-plan.md")
SRCMAP = os.path.join(ROOT, "tools", "sab_srcmap.json")
SOURCE_DIR = os.path.join(ROOT, os.environ.get("SAB_SOURCE_DIR", "sources/sab-v0_9"))
SEC_RE = re.compile(r"\b(\d{2})\.(\d{2})\b")

# หัวข้อระดับ ## นอกบท 0–10 ที่ชื่อในตารางแผนไม่ใช่ substring ของหัวข้อจริง → คำค้นในคอลัมน์แรกของตาราง
ALIASES = {
    "แผนหนังสือและเป้าหมายการเรียน": "แผนหนังสือและเป้าหมาย",
    "แผนภาค 1": "แผนภาค 1–2",
    "แผนภาค 2": "แผนภาค 1–2",
    "แผนภาค 3": "แผนบท 13",
    "แผนภาค 4": "แผนบท 14",
    "แผนภาค 5": "แผนบท 19–20",
    "กรณีศึกษาที่ใช้เป็นแกนของเล่ม": "C8 implied carry",
    "แหล่งอ้างอิงและทางอ่านต่อ": "แหล่งอ้างอิง",
    "สารบัญ": "สารบัญ",
    "เล่มนี้เขียนให้ใคร": "เขียนให้ใคร",
}


def source_path(args):
    for a in args:
        if a.endswith(".md"):
            return a
    errata = os.path.join(SOURCE_DIR, "Part_I_v0_9_errata.md")
    if os.path.exists(errata):
        return errata
    return os.path.join(SOURCE_DIR, "Stat_Arb_for_Non_Quant_Part_I_v0_9.md")


def sections(md_path):
    """[(id, หัวข้อ, บรรทัดเริ่ม, ข้อความ)] · id = 'NN.MM' สำหรับ ### หรือ 'top:<หัวข้อ>' สำหรับ ## ที่ไม่ใช่บท"""
    with open(md_path, encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    out, cur = [], None
    for i, line in enumerate(lines, 1):
        m3 = re.match(r"###\s+(\d{2}\.\d{2})\s+(.*)", line)
        m2 = re.match(r"##\s+(.*)", line) if not line.startswith("###") else None
        if m3 or m2:
            if cur:
                out.append(cur)
            if m3:
                cur = [m3.group(1), m3.group(2).strip(), i, []]
            elif re.match(r"บท \d+", m2.group(1)):
                cur = None          # หัวบท: เนื้อหาอยู่ในหัวข้อย่อย
                continue
            else:
                cur = ["top:" + m2.group(1).strip(), m2.group(1).strip(), i, []]
            continue
        if cur:
            cur[3].append(line)
    if cur:
        out.append(cur)
    return [(a, b, c, "\n".join(d).strip()) for a, b, c, d in out]


def plan_rows():
    with open(PLAN, encoding="utf-8") as fh:
        text = fh.read()
    s81 = text[text.index("### 8.1"):text.index("### 8.2")]
    s82 = text[text.index("### 8.2"):text.index("## 9.")]
    s82 = s82.split("| รูป v0.9")[0]          # ตารางแรกของ 8.2 เท่านั้น (ตารางรูปแยก)
    rows = []
    for block in (s81, s82):
        for line in block.split("\n"):
            if not line.startswith("|") or line.startswith("|---") or line.startswith("| v0.9"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 3:
                rows.append({"v09": cells[0], "หัวข้อ": cells[1] if len(cells) > 3 else "",
                             "ปลายทาง": cells[2] if len(cells) > 3 else cells[1],
                             "การจัดการ": cells[3] if len(cells) > 3 else (cells[2] if len(cells) > 2 else "")})
    return rows


def expand(cell):
    """'01.09–01.10' → ['01.09','01.10'] · '02.01–02.02' · '05.03, 05.04' · คืน [] ถ้าไม่ใช่เลขหัวข้อ"""
    ids = set()
    for a, b in re.findall(r"(\d{2}\.\d{2})\s*[–-]\s*(\d{2}\.\d{2})", cell):
        ch, s, e = a[:2], int(a[3:]), int(b[3:])
        if b[:2] == ch:
            ids |= {f"{ch}.{k:02d}" for k in range(s, e + 1)}
    ids |= {f"{x}.{y}" for x, y in SEC_RE.findall(cell)}
    return sorted(ids)


def parse_dest(dest):
    d = {"บท": sorted({int(x) for x in re.findall(r"บท\s*(\d+)", dest)} |
                     {int(x) for grp in re.findall(r"บท\s*((?:\d+\s*[,/]\s*)+\d+)", dest)
                      for x in re.findall(r"\d+", grp)}),
         "ภาคผนวก": sorted(set(re.findall(r"(?:ภผ\.|ภาคผนวก\s*)([A-I])", dest)) |
                         ({"D"} if re.search(r"(?<![A-Za-z])D(?![A-Za-z])", dest) else set())),
         "เล่ม2": "เล่ม 2" in dest, "ตัด": dest.startswith("ตัด") or "ตัดจากหน้าผู้อ่าน" in dest or "ไม่เข้าหน้าผู้อ่าน" in dest,
         "ไฟล์": re.findall(r"`([^`]+)`", dest)}
    for grp in re.findall(r"ภาค\s*([123])", dest):
        d.setdefault("ภาค", []).append(int(grp))
    return d


def build_map(md_path):
    rows = plan_rows()
    secs = sections(md_path)
    out, unmatched = {}, []
    for sid, title, line, _ in secs:
        hit = None
        if not sid.startswith("top:"):
            hit = next((r for r in rows if sid in expand(r["v09"])), None)
        else:
            name = sid[4:]
            keys = [v for k, v in ALIASES.items() if name.startswith(k)] + [name[:14]]
            for k in keys:
                hit = next((r for r in rows if k in r["v09"]), None)
                if hit:
                    break
        if hit:
            out[sid] = {"หัวข้อ": title, "บรรทัด": line, "ปลายทาง": hit["ปลายทาง"],
                        "การจัดการ": hit["การจัดการ"], **parse_dest(hit["ปลายทาง"])}
        else:
            unmatched.append(sid)
    with open(SRCMAP, "w", encoding="utf-8") as fh:
        json.dump({"_อ่านก่อน": "สร้างโดย tools/sab_extract.py --build-map จาก docs/sab-book-plan.md หัวข้อ 8.1/8.2 · ห้ามแก้มือ",
                   "หัวข้อ": out}, fh, ensure_ascii=False, indent=1)
    print(f"เขียน tools/sab_srcmap.json · จับคู่ {len(out)}/{len(secs)} หัวข้อ")
    for u in unmatched:
        print("  - ยังไม่มีปลายทาง:", u)
    return 0 if not unmatched else 1


def load_map():
    if not os.path.exists(SRCMAP):
        sys.exit("ยังไม่มี tools/sab_srcmap.json — รัน --build-map ก่อน")
    with open(SRCMAP, encoding="utf-8") as fh:
        return json.load(fh)["หัวข้อ"]


def report_map(md_path):
    m = load_map()
    secs = sections(md_path)
    missing = [s for s, *_ in secs if s not in m]
    nodest = [s for s, v in m.items() if not (v["บท"] or v["ภาคผนวก"] or v["เล่ม2"] or v["ตัด"] or v["ไฟล์"] or v.get("ภาค"))]
    print(f"S1a: {len(secs) - len(missing)}/{len(secs)} หัวข้อมีแถวในตารางแปลง"
          f" ({100 * (len(secs) - len(missing)) / max(1, len(secs)):.0f}%)")
    for s in missing:
        print("  - ไม่มีแถว:", s)
    for s in nodest:
        print("  - แถวไม่ระบุปลายทางที่ตรวจได้:", s, "→", m[s]["ปลายทาง"][:60])
    return 0 if not missing and not nodest else 1


def report_tags(scope):
    n = int(re.fullmatch(r"part(\d+)", scope).group(1))
    page = os.path.join(ROOT, "docs", f"sab-{scope}.html")
    if not os.path.exists(page):
        print(f"ยังไม่มี docs/sab-{scope}.html")
        return 1
    with open(page, encoding="utf-8") as fh:
        tags = set(re.findall(r"<!--src:([^>]+?)-->", fh.read()))
    tags = {t.strip() for x in tags for t in x.split(",")}
    want = sorted(s for s, v in load_map().items() if n in v["บท"])
    miss = [s for s in want if s not in tags]
    print(f"S1b บท {n}: ป้าย {len(want) - len(miss)}/{len(want)}")
    for s in miss:
        print("  - ไม่มีป้าย <!--src:" + s + "-->")
    return 0 if not miss else 1


def dump(sid, md_path):
    for s, title, line, body in sections(md_path):
        if s == sid:
            print(f"## {s} {title}  (บรรทัด {line})\n\n{body}")
            return 0
    print("ไม่พบหัวข้อ", sid)
    return 1


if __name__ == "__main__":
    a = sys.argv[1:]
    md = source_path(a)
    if "--build-map" in a:
        sys.exit(build_map(md))
    if "--dump" in a:
        sys.exit(dump(a[a.index("--dump") + 1], md))
    if "--report" in a:
        kind = a[a.index("--report") + 1]
        if kind == "map":
            sys.exit(report_map(md))
        if kind == "tags" and "--scope" in a:
            sys.exit(report_tags(a[a.index("--scope") + 1]))
    print(__doc__)
    sys.exit(1)
