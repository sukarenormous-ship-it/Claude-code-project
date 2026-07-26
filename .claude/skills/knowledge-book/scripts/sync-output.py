#!/usr/bin/env python3
"""อัปเดตบล็อก .output ในไฟล์หนังสือ ให้ตรงกับผลลัพธ์ที่โค้ดพิมพ์จริง

ข้าม:
  - บล็อกที่หนังสือย่อด้วย ... (ตั้งใจย่อ ไม่ใช่ผิด)
  - บล็อกที่รันไม่ผ่าน / ไม่พิมพ์อะไร
"""
import html
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).parent
DOCS = pathlib.Path("/home/user/Claude-code-project/docs")
TAG = re.compile(r"</?(?:span|br|div|a|strong|em|code|b|i|u|sub|sup)(?:\s[^>]*)?/?>", re.I)

part = sys.argv[1]
apply_ = "--apply" in sys.argv
results = {r["line"]: r for r in json.loads((HERE / f"rr_{part}.json").read_text())}
path = DOCS / f"python-{part}.html"
text = path.read_text(encoding="utf-8")

PAIR = re.compile(
    r'(<div class="fm">((?:(?!</div>).)*)</div>\s*<div class="output">)'
    r'((?:(?!</div>).)*)(</div>)', re.S
)


def norm(s):
    return "\n".join(l.rstrip() for l in s.strip().splitlines() if l.strip())


changed, skipped = [], []
out_parts, pos = [], 0
for m in PAIR.finditer(text):
    line = text[: m.start()].count("\n") + 1
    doc_raw = m.group(3)
    doc = norm(html.unescape(TAG.sub("", doc_raw)))
    r = results.get(line)
    reason = None
    if r is None:
        reason = "ไม่ได้รัน"
    elif r["status"] != "ok":
        reason = f"บล็อกพัง {r['status']}"
    elif not norm(r["stdout"]):
        reason = "ไม่พิมพ์อะไร"
    elif "..." in doc or "…" in doc:
        reason = "หนังสือย่อด้วย ... (ข้าม)"
    if reason:
        skipped.append((line, reason))
        continue
    act = norm(r["stdout"])
    if act == doc:
        continue
    new = html.escape(act, quote=False)
    out_parts.append(text[pos: m.start(3)])
    out_parts.append(new)
    pos = m.end(3)
    changed.append((line, doc, act))

out_parts.append(text[pos:])
new_text = "".join(out_parts)

print(f"── {path.name} ──")
print(f"อัปเดต {len(changed)} บล็อก · ข้าม {len(skipped)}")
for line, reason in skipped:
    print(f"  ข้าม :{line} — {reason}")
for line, doc, act in changed:
    print(f"\n  :{line}")
    print("    เดิม: " + doc.splitlines()[0][:90])
    print("    ใหม่: " + act.splitlines()[0][:90])

if apply_ and changed:
    path.write_text(new_text, encoding="utf-8")
    print("\n✓ เขียนไฟล์แล้ว")
elif changed:
    print("\n(dry-run — ใส่ --apply เพื่อเขียนจริง)")
