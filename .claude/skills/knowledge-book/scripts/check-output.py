#!/usr/bin/env python3
"""เทียบ .output ที่หนังสือเขียนไว้ กับผลลัพธ์ที่โค้ดพิมพ์ออกมาจริง

ข้อบกพร่องคนละชั้นกับ "รันได้ไหม": โค้ดรันผ่านแต่ตัวเลขในหนังสือไม่ตรง
= ผู้อ่านรันตามแล้วได้ผลต่าง จะคิดว่าตัวเองทำพลาด
"""
import html
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).parent
SNIP = HERE / "snippets"
DOCS = pathlib.Path("/home/user/Claude-code-project/docs")
TAG = re.compile(r"</?(?:span|br|div|a|strong|em|code|b|i|u|sub|sup)(?:\s[^>]*)?/?>", re.I)




def norm(s: str) -> str:
    """ตัดช่องว่างท้ายบรรทัด + บรรทัดว่าง เพื่อเทียบเนื้อจริง"""
    return "\n".join(l.rstrip() for l in s.strip().splitlines() if l.strip())


def nums(s: str):
    return re.findall(r"-?\d+\.?\d*", s)


target = sys.argv[1] if len(sys.argv) > 1 else ""

# อ่านผลรันของ part ที่ระบุ (rr_<part>.json) — ถ้าไม่ระบุ ใช้ run_results.json
_rf = HERE / (f"rr_{target}.json" if target and (HERE / f"rr_{target}.json").exists()
              else "run_results.json")
results = {(r["file"], r["line"]): r for r in json.loads(_rf.read_text())}
rows = []
for path in sorted(DOCS.glob("python-part*.html")):
    if target and target not in path.name:
        continue
    text = path.read_text(encoding="utf-8")
    # หา .fm ที่ตามด้วย .output
    # ⚠️ ห้ามใช้ (.*?) เฉย ๆ — มันจะไล่ข้ามบล็อกไปหา .output ที่อยู่ไกล
    # ทำให้จับคู่โค้ดกับผลลัพธ์คนละก้อน · ต้องกันไม่ให้ข้าม </div>
    for m in re.finditer(
        r'<div class="fm">((?:(?!</div>).)*)</div>\s*'
        r'<div class="output">((?:(?!</div>).)*)</div>', text, re.S
    ):
        line = text[: m.start()].count("\n") + 1
        # บล็อกที่เป็นเนื้อไฟล์ (# ── ชื่อไฟล์.py ──) ไม่ได้ถูกรัน จึงไม่ต้องเทียบ
        if re.match(r"\s*<span[^>]*>?\s*#\s*──\s*\S+\.py",
                    html.unescape(m.group(1))[:120]) or \
           re.match(r"\s*#\s*──\s*\S+\.py",
                    html.unescape(TAG.sub("", m.group(1)))[:120]):
            continue
        doc = norm(html.unescape(TAG.sub("", m.group(2))))
        r = results.get((path.name, line))
        if r is None:
            rows.append((path.name, line, "ไม่ได้รัน", doc, ""))
            continue
        if r["status"] != "ok":
            rows.append((path.name, line, f"บล็อกพัง ({r['status']})", doc, ""))
            continue
        act = norm(r["stdout"])
        if "..." in doc or "…" in doc:
            continue          # หนังสือย่อด้วย ... โดยตั้งใจ (เกณฑ์เดียวกับ sync-output)
        if not act:
            rows.append((path.name, line, "ไม่พิมพ์อะไรเลย", doc, ""))
        elif act != doc:
            same = nums(act) == nums(doc)
            rows.append((path.name, line,
                         "ต่างแค่รูปแบบ" if same else "ตัวเลขไม่ตรง", doc, act))

print(f"พบจุดที่ต้องดู {len(rows)}\n")
for fn, line, why, doc, act in rows:
    print(f"{'='*70}\n{fn}:{line}  [{why}]")
    print("── หนังสือเขียน ──"); print(doc[:500])
    if act:
        print("── รันจริงได้ ──"); print(act[:500])
