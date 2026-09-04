#!/usr/bin/env python3
"""สร้าง "ดัชนีสัญลักษณ์ → อ่านครั้งแรกที่ไหน" จากบล็อก 📖 อ่านสูตรว่า ทั้งคลัง แล้วเขียนลง
docs/notation.html ระหว่าง marker <!-- SYMBOL-INDEX:BEGIN --> … <!-- SYMBOL-INDEX:END -->

ใช้:  python3 tools/symbol_index.py          → อัปเดต notation.html
      python3 tools/symbol_index.py --dry    → พิมพ์ตารางอย่างเดียว
รันใหม่ทุกครั้งที่เพิ่มบล็อก 📖 — idempotent
"""
import glob
import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")

# ลำดับการอ่านของคลัง — ไฟล์ที่มาก่อนคือ "ครั้งแรก"
ORDER = ["nq-part0", "nq-part1", "nq-part2", "nq-part3", "nq-part4", "nq-part5", "nq-part6", "nq-part7", "nq-part8", "nq-part9",
         "nq-appendix-indicators", "math-part1", "math-part2", "math-part3", "math-part6", "math-part7",
         "math-part4", "math-part5", "math-part8", "math-part9", "math-part10", "math-part11",
         "pm-part0", "pm-part1", "pm-part2", "pm-part3", "pm-part3a", "pm-part4", "pm-part4a", "pm-part5", "pm-part5a", "pm-part6", "pm-part7", "pm-part8",
         "theory-part1", "theory-part2", "theory-part3", "theory-part4", "theory-part5", "theory-part6", "theory-extra",
         "pillars-part1", "pillars-part2", "pillars-part3", "pillars-part4",
         "arb-part1", "arb-part2a", "arb-part2b", "arb-part3", "arb-part4", "arb-part5", "arb-part6", "arb-part7", "arb-part8", "arb-part9",
         "eye-part1", "eye-part2", "eye-part3", "eye-part4", "eye-part5", "statarb-copula-practice"]

LABEL = {"nq": "NQ", "math": "คณิต", "pm": "Payoff", "theory": "ทฤษฎี", "pillars": "เสา", "arb": "Arb", "eye": "ตา", "statarb": "statarb"}

# (สัญลักษณ์ที่แสดง, regex หาในข้อความบล็อก, คำอ่านสั้น)
SYMBOLS = [
    ("xₜ, x<sub>t−1</sub>", r"ตัวห้อย[^·]{0,40}(เวลา|วันนี้|เมื่อวาน)", "ตัวห้อยเวลา"),
    ("x̄", r"บาร์|ขีดบน", "ขีดบน = ค่าเฉลี่ย"),
    ("x̂, β̂", r"แฮต|หมวก", "หมวก = ค่าประมาณ"),
    ("Σ (ผลรวม)", r"ซิกมาใหญ่|ผลรวมของ", "ซิกมาใหญ่"),
    ("Σ (เมทริกซ์ covariance)", r"covariance matrix|เมทริกซ์[^·]{0,20}covariance", "Σ = ตาราง covariance"),
    ("σ, σ²", r"ซิกมา(?!ใหญ่)", "ซิกมา = SD · σ² = variance"),
    ("μ", r"มิว", "มิว = ค่าเฉลี่ย/drift"),
    ("β", r"เบต้า", "เบต้า = ความชัน/ความไว"),
    ("α", r"อัลฟา|α ตัวนี้", "อัลฟา (หลายความหมาย)"),
    ("ρ", r"โร\b|โร ", "โร = correlation"),
    ("λ", r"แลมบ์ดา", "แลมบ์ดา (หลายความหมาย)"),
    ("θ", r"ธีตา|ทีตา", "ธีตา (Theta / แรงดึงกลับ)"),
    ("φ", r"ฟี\b|ฟี ", "ฟี = สัดส่วนที่เหลือ (AR)"),
    ("ε", r"เอปไซลอน", "เอปไซลอน = ช็อก/residual"),
    ("Δ", r"เดลตา", "เดลตา = การเปลี่ยนแปลง / Greek"),
    ("∂", r"อนุพันธ์ย่อย|ดีโค้ง", "อนุพันธ์ย่อย"),
    ("d (dx, dt, dW)", r"การเปลี่ยนแปลงจิ๋ว|ดีดับเบิลยู", "การเปลี่ยนแปลงจิ๋ว"),
    ("∇", r"นาบลา|เกรเดียนต์", "เกรเดียนต์"),
    ("√", r"รูท|รากที่สอง", "รากที่สอง"),
    ("ln, e^x", r"ล็อกธรรมชาติ|เอ็กซ์โพเนนเชียล|อี ยกกำลัง", "ล็อกธรรมชาติ / e ยกกำลัง"),
    ("e^(−rT)", r"ตัวลดค่า", "ตัวลดค่า"),
    ("|x|", r"ค่าสัมบูรณ์", "ค่าสัมบูรณ์ = ทิ้งทิศ"),
    ("max / min", r"แม็กซ์|ค่ามากสุด|ค่าที่น้อยกว่า|min\(", "ตัวกรองด้านเดียว"),
    ("ᵀ", r"ทรานสโพส", "ทรานสโพส"),
    ("⁻¹", r"อินเวอร์ส", "อินเวอร์ส = หารด้วยเมทริกซ์"),
    ("E[·]", r"ค่าคาดหวัง|expected value", "ค่าคาดหวัง"),
    ("E[Y | X], P(A | B)", r"เมื่อรู้|given", "ขีดตั้ง = given"),
    ("Var, Cov", r"แวเรียนซ์|โคแวเรียนซ์", "แวเรียนซ์ / โคแวเรียนซ์"),
    ("N(d), N′(d)", r"เอ็นของดี|CDF", "CDF ของ normal"),
    ("≈", r"≈", "ประมาณ — มีสมมติฐาน"),
    ("t, SE, p", r"เอสอี|SE\(|t-stat|ที เท่ากับ", "ค่าประมาณ ÷ SE"),
    ("argmin / argmax", r"argmin|argmax|ที่ทำให้[^·]{0,15}(น้อย|สูง|ต่ำ)ที่สุด", "คืนตำแหน่ง ไม่ใช่ค่า"),
    ("f*, p*, x*", r"ดอกจัน|สตาร์", "ดอกจัน = ค่าที่ดีที่สุด / risk-neutral"),
]


def blocks(path):
    src = open(path, encoding="utf-8").read()
    out = []
    for m in re.finditer(r'<p class="read">.*?</p>', src, re.S):
        before = src[:m.start()]
        anc = re.findall(r'<h[23][^>]*id="([^"]+)"', before)
        text = re.sub(r"<[^>]+>", " ", m.group(0))
        out.append((anc[-1] if anc else "", html.unescape(text)))
    return out


def main():
    files = [os.path.join(DOCS, f + ".html") for f in ORDER if os.path.exists(os.path.join(DOCS, f + ".html"))]
    data = {f: blocks(f) for f in files}
    rows = []
    for sym, pat, gloss in SYMBOLS:
        rx = re.compile(pat)
        hits = []
        for f in files:
            for anc, text in data[f]:
                if rx.search(text):
                    hits.append((os.path.basename(f)[:-5], anc))
                    break
        if not hits:
            continue
        first = hits[0]
        others = hits[1:5]
        def link(h):
            name, anc = h
            lab = LABEL.get(name.split("-")[0], name)
            short = name.replace("-part", " ").replace("nq-appendix-indicators", "NQ App E")
            return f'<a href="{name}.html{"#" + anc if anc else ""}">{html.escape(short)}</a>'
        rows.append(f"<tr><td class=\"sym\">{sym}</td><td class=\"nw\">{html.escape(gloss)}</td><td>{link(first)}</td><td>{' · '.join(link(h) for h in others)}{' · …' if len(hits) > 5 else ''} <span class=\"lgd\">({len(hits)} เล่ม)</span></td></tr>")
    table = ("<!-- SYMBOL-INDEX:BEGIN -->\n<h3 id=\"symindex\">ดัชนีสัญลักษณ์ — อ่านครั้งแรกที่ไหน</h3>\n"
             "<p>สร้างอัตโนมัติจากบล็อก \"📖 อ่านสูตรว่า\" ทั้งคลัง (<code>tools/symbol_index.py</code>) · คอลัมน์ \"ครั้งแรก\" คือบทแรกตามลำดับอ่านที่สอนอ่านสัญลักษณ์นั้น ส่วนคอลัมน์ถัดไปคือบทอื่นที่อ่านซ้ำในบริบทใหม่</p>\n"
             "<div class=\"tw\"><table>\n<tr><th class=\"nw\">สัญลักษณ์</th><th class=\"nw\">อ่านว่า</th><th class=\"nw\">อ่านครั้งแรก</th><th>เจออีกที่</th></tr>\n"
             + "\n".join(rows) + "\n</table></div>\n<!-- SYMBOL-INDEX:END -->")
    if "--dry" in sys.argv:
        print(table)
        return 0
    p = os.path.join(DOCS, "notation.html")
    s = open(p, encoding="utf-8").read()
    if "<!-- SYMBOL-INDEX:BEGIN -->" in s:
        s = re.sub(r"<!-- SYMBOL-INDEX:BEGIN -->.*?<!-- SYMBOL-INDEX:END -->", lambda m: table, s, flags=re.S)
    else:
        key = '<h2>1. พื้นฐาน / กระบวนการสุ่ม'
        assert key in s
        s = s.replace(key, table + "\n\n" + key, 1)
    open(p, "w", encoding="utf-8").write(s)
    print(f"ดัชนี {len(rows)} สัญลักษณ์ เขียนลง notation.html แล้ว")
    return 0


if __name__ == "__main__":
    sys.exit(main())
