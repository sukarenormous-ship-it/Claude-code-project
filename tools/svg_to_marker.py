#!/usr/bin/env python3
"""แทนภาพ SVG เดิม (วาดมือ) ด้วย marker FIG เพื่อให้ tools/make_figures.py วาดใหม่จากข้อมูล
ใช้:  python3 tools/svg_to_marker.py docs/pm-part0.html 1:p0-payoff-vs-profit 2:p0-long-call ...
ดัชนีนับเฉพาะ SVG เดิม (ยาว ≥ 200 ตัวอักษร และไม่ใช่ภาพจาก generator) ตามลำดับในไฟล์ต้นฉบับ
"""
import re
import sys


def legacy_svgs(s):
    gen_spans = [(m.start(), m.end()) for m in re.finditer(r"<!-- FIG:[^:]+:BEGIN -->.*?<!-- FIG:[^:]+:END -->", s, re.S)]
    out = []
    for m in re.finditer(r"<svg\b.*?</svg>", s, re.S):
        if len(m.group(0)) < 200: continue
        if any(a <= m.start() < b for a, b in gen_spans): continue
        out.append(m)
    return out


def main():
    path = sys.argv[1]; pairs = [a.split(":", 1) for a in sys.argv[2:]]
    s = open(path, encoding="utf-8").read()
    svgs = legacy_svgs(s)
    for idx, name in sorted(((int(i), n) for i, n in pairs), reverse=True):
        m = svgs[idx - 1]
        s = s[:m.start()] + f"<!-- FIG:{name}:BEGIN -->\n<!-- FIG:{name}:END -->" + s[m.end():]
        print(f"  #{idx} → FIG:{name} (ลบ {len(m.group(0))} ตัวอักษร)")
    open(path, "w", encoding="utf-8").write(s)


if __name__ == "__main__":
    main()
