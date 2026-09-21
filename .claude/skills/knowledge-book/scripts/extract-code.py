#!/usr/bin/env python3
"""สกัดบล็อกโค้ดจากไฟล์หนังสือ HTML -> ไฟล์ .py ต่อบล็อก + metadata"""
import html
import json
import os
import pathlib
import re
import sys

DOCS = pathlib.Path("/home/user/Claude-code-project/docs")
OUT = pathlib.Path(os.environ.get("SNIPPET_DIR", "/tmp/book-snippets"))

# ดึง div ที่เป็นโค้ด: class="fm" หรือ class="ad-code" หรือ class="output"
BLOCK = re.compile(
    r'<div class="(fm|ad-code|output)"[^>]*>(.*?)</div>', re.S
)
# ⚠️ ต้องลบเฉพาะ tag ที่รู้จัก — regex <[^>]+> จะกิน format spec ของ f-string
# เช่น {'x':<28} {y:>10.2f}  ตรงกลางดูเหมือน tag
TAG = re.compile(
    r"</?(?:span|br|div|a|strong|em|code|b|i|u|sub|sup)(?:\s[^>]*)?/?>",
    re.I,
)

THAI = re.compile(r"[฀-๿]")


def clean(raw: str) -> str:
    # <br> -> newline ก่อนลบ tag อื่น
    s = re.sub(r"<br\s*/?>", "\n", raw)
    s = TAG.sub("", s)
    return html.unescape(s)


def looks_python(t: str) -> bool:
    """แยกโค้ด Python ออกจากสูตรคณิต / prompt ภาษาไทย"""
    if not t.strip():
        return False
    py = (
        "import ", "def ", "print(", "return ", "self.", "for ", "if ",
        "np.", "pd.", "plt.", " = ", "=(", "class ", "assert ", "await ",
        "async ", "@", "lambda", ".append(", "try:",
    )
    score = sum(1 for k in py if k in t)
    # สูตรคณิตศาสตร์: สั้น + ไม่มี keyword
    return score >= 1


def main():
    OUT.mkdir(exist_ok=True)
    for f in OUT.glob("*"):
        f.unlink()
    meta = []
    for path in sorted(DOCS.glob("python-*.html")):
        text = path.read_text(encoding="utf-8")
        # หาเลขบรรทัดของแต่ละ match
        for i, m in enumerate(BLOCK.finditer(text)):
            kind, raw = m.group(1), m.group(2)
            line = text[: m.start()].count("\n") + 1
            code = clean(raw)
            rec = {
                "file": path.name,
                "line": line,
                "kind": kind,
                "idx": i,
                "chars": len(code),
                "thai": bool(THAI.search(code)),
                "python": looks_python(code),
            }
            stem = f"{path.stem}__L{line:05d}__{kind}"
            (OUT / f"{stem}.txt").write_text(code, encoding="utf-8")
            rec["stem"] = stem
            meta.append(rec)
    (OUT / "_meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")

    # สรุป
    from collections import Counter
    c = Counter((r["file"], r["kind"]) for r in meta)
    print(f"บล็อกทั้งหมด {len(meta)}")
    for (fn, kind), n in sorted(c.items()):
        print(f"  {fn:24s} {kind:9s} {n:3d}")
    py = [r for r in meta if r["kind"] in ("fm", "ad-code") and r["python"]]
    print(f"\nเข้าข่าย Python (fm/ad-code): {len(py)}")
    notpy = [r for r in meta if r["kind"] in ("fm", "ad-code") and not r["python"]]
    print(f"ไม่เข้าข่าย (สูตร/prompt/ข้อความ): {len(notpy)}")
    for r in notpy[:25]:
        print(f"   {r['file']}:{r['line']} ({r['chars']}ch)")


if __name__ == "__main__":
    main()
