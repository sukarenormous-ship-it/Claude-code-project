#!/usr/bin/env python3
"""สร้างสารบัญในหน้า (per-file TOC) จาก <h2>/<h3> ที่มี id อยู่แล้ว

ทำไมต้อง generate ไม่เขียนมือ: เล่มนี้มี 36 บท · 151 หัวข้อย่อย ถ้าเขียนมือ
พอเพิ่มหัวข้อใหม่แล้วลืมอัปเดต สารบัญจะโกหกทันที — และไม่มีใครรู้

รันซ้ำได้ (idempotent) — แทนที่ของเดิมระหว่าง marker เสมอ
    python3 build-toc.py docs 'python-part*.html'
"""
import html
import pathlib
import re
import sys

DOCS = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "docs")
GLOB = sys.argv[2] if len(sys.argv) > 2 else "python-part*.html"

START, END = "<!-- TOC:START -->", "<!-- TOC:END -->"

# ⚠️ ต้องถอด tag ออกจากหัวข้อก่อนเอาไปใส่สารบัญ — หัวข้อหลายอันมี <code>
#    ข้างใน ถ้าปล่อยไว้จะได้ลิงก์ที่มี markup ซ้อนแล้วจัดหน้าเพี้ยน
TAG = re.compile(r"<[^>]+>")

CSS = """.toc{background:var(--g1);border-radius:8px;padding:4px 0;margin:16px 0}
.toc ol{margin:0;padding:0;list-style:none}
.toc>ol>li{padding:6px 16px}
.toc>ol>li+li{border-top:1px solid rgba(0,0,0,.06)}
.toc a{color:var(--ink);text-decoration:none}
.toc a:hover{color:var(--teal);text-decoration:underline}
.toc .ch{font-weight:700}
.toc .secs{margin-top:4px;font-size:.9em;line-height:1.9;color:#475569}
.toc .secs a{margin-right:2px}
.toc .secs .sep{color:#cbd5e1;margin:0 4px}"""


def strip(s: str) -> str:
    return html.unescape(TAG.sub("", s)).strip()


def build(text: str) -> str:
    """เดินหา h2 แล้วผูก h3 ที่ตามมาก่อน h2 ตัวถัดไปเข้ากับมัน"""
    heads = [
        (m.start(), m.group(1), m.group(2), strip(m.group(3)))
        for m in re.finditer(r'<(h2|h3) id="([^"]+)">(.*?)</\1>', text, re.S)
    ]
    chapters = []
    for _, lvl, hid, title in heads:
        if lvl == "h2":
            chapters.append({"id": hid, "title": title, "secs": []})
        elif chapters:
            chapters[-1]["secs"].append({"id": hid, "title": title})

    if not chapters:
        return ""

    rows = []
    for c in chapters:
        secs = ""
        if c["secs"]:
            links = [f'<a href="#{s["id"]}">{html.escape(s["title"])}</a>'
                     for s in c["secs"]]
            secs = ('\n<div class="secs">'
                    + '<span class="sep">·</span>'.join(links) + "</div>")
        rows.append(f'<li><a class="ch" href="#{c["id"]}">'
                    f'{html.escape(c["title"])}</a>{secs}</li>')

    n_sec = sum(len(c["secs"]) for c in chapters)
    # เปิดค้างไว้ — details ที่ปิดอยู่จะพิมพ์ลง PDF แค่บรรทัดเดียว
    # และ CSS บังคับเปิดตอน print ไม่ชนะ UA stylesheet ของ <details>
    return (f'{START}\n<details class="toc-wrap" open>\n'
            f'<summary>สารบัญ Part นี้ — {len(chapters)} บท · {n_sec} หัวข้อ</summary>\n'
            f'<div class="toc">\n<ol>\n' + "\n".join(rows)
            + f"\n</ol>\n</div>\n</details>\n{END}")


def inject(path: pathlib.Path) -> str:
    t = path.read_text(encoding="utf-8")
    toc = build(t)
    if not toc:
        return "ไม่มี h2 ที่มี id"

    if "\n.toc{" not in t:                      # ใส่ CSS ครั้งเดียว
        anchor = "details{margin:8px 0}"
        if anchor not in t:
            return "หา anchor ของ CSS ไม่เจอ"
        t = t.replace(anchor, anchor + "\n" + CSS, 1)

    if START in t:                              # แทนที่ของเดิม
        # ⚠️ ต้องส่ง replacement เป็น lambda — ถ้าส่ง string ตรง ๆ re.sub จะ
        #    ตีความ \ ใน HTML/ข้อความไทยเป็น escape แล้วโยน "bad escape"
        t = re.sub(re.escape(START) + r".*?" + re.escape(END),
                   lambda _: toc, t, flags=re.S)
        note = "อัปเดต"
    else:
        # วางต่อจากกล่อง "อ่าน Part นี้ยังไง" ถ้ามี · ไม่งั้นต่อจากปก
        m = re.search(r'<div class="bx bd">\s*\n<div class="bt">🧭[^<]*</div>.*?\n</div>\n',
                      t, re.S) or re.search(r'<div class="cover">.*?\n</div>\n', t, re.S)
        if not m:
            return "หาที่แทรกไม่เจอ"
        t = t[:m.end()] + "\n" + toc + "\n" + t[m.end():]
        note = "แทรกใหม่"

    path.write_text(t, encoding="utf-8")
    n_ch = toc.count('class="ch"')
    return f"{note} · {n_ch} บท"


for p in sorted(DOCS.glob(GLOB)):
    print(f"{p.name:26s} {inject(p)}")


# ─────────────────── สารบัญเต็มเล่มในหน้า index ───────────────────
# การ์ดในหน้า index ทั้งใบเป็น <a> อยู่แล้ว จึงซ้อนลิงก์ชื่อบทเข้าไปไม่ได้
# → ทำเป็นสารบัญเต็มเล่มต่อท้ายแทน (generate เหมือนกัน จะได้ไม่ล้าสมัย)
INDEX = DOCS / "python-for-quant-traders.html"
I_START, I_END = "<!-- BOOKTOC:START -->", "<!-- BOOKTOC:END -->"

PART_LABEL = {
    "python-part0.html": "Part 0 · พื้นฐานที่ต้องมีก่อน",
    "python-part1.html": "Part I · Python สำหรับ Quant",
    "python-part2.html": "Part II · คณิตศาสตร์และสถิติด้วยโค้ด",
    "python-part3.html": "Part III · OOP",
    "python-part4.html": "Part IV · Backtesting",
    "python-part5.html": "Part V · AI-Assisted Coding",
    "python-part6.html": "Part VI · Async & Live Trading",
}

if INDEX.exists() and GLOB.startswith("python-part"):
    blocks, n_ch, n_sec = [], 0, 0
    for name, label in PART_LABEL.items():
        f = DOCS / name
        if not f.exists():
            continue
        txt = f.read_text(encoding="utf-8")
        # ตัดสารบัญในหน้าออกก่อน ไม่งั้นจะไปจับหัวข้อซ้ำจากในนั้น
        txt = re.sub(re.escape(START) + r".*?" + re.escape(END), "", txt, flags=re.S)
        rows = []
        for m in re.finditer(r'<(h2|h3) id="([^"]+)">(.*?)</\1>', txt, re.S):
            lvl, hid, title = m.group(1), m.group(2), strip(m.group(3))
            if lvl == "h2":
                n_ch += 1
                rows.append(f'<li><a class="ch" href="{name}#{hid}">'
                            f'{html.escape(title)}</a></li>')
            else:
                n_sec += 1
        blocks.append(f'<div class="bt-part">{html.escape(label)}</div>\n'
                      f'<ol class="bt-ch">\n' + "\n".join(rows) + "\n</ol>")

    body = (f'{I_START}\n<h2>🗂️ สารบัญเต็มเล่ม — {n_ch} บท</h2>\n'
            f'<p style="margin-top:-6px;color:#64748b;font-size:.93em">'
            f'คลิกบทไหนก็กระโดดไปหน้านั้นได้ทันที · '
            f'ในแต่ละ Part มีสารบัญหัวข้อย่อยอีก {n_sec} หัวข้ออยู่บนสุดของหน้า</p>\n'
            f'<div class="booktoc">\n' + "\n".join(blocks)
            + f"\n</div>\n{I_END}")

    t = INDEX.read_text(encoding="utf-8")
    if "\n.booktoc{" not in t:
        css = """.booktoc{background:var(--g1);border-radius:10px;padding:14px 20px;margin:14px 0}
.bt-part{font-weight:700;color:var(--teal);margin:12px 0 4px;font-size:.95em}
.bt-part:first-child{margin-top:0}
ol.bt-ch{margin:0 0 4px;padding-left:20px;line-height:1.85}
ol.bt-ch li{font-size:.94em}
ol.bt-ch a{color:var(--ink);text-decoration:none}
ol.bt-ch a:hover{color:var(--teal);text-decoration:underline}"""
        anchor = "</style>"
        t = t.replace(anchor, css + "\n" + anchor, 1)

    if I_START in t:
        t = re.sub(re.escape(I_START) + r".*?" + re.escape(I_END),
                   lambda _: body, t, flags=re.S)
        note = "อัปเดต"
    else:
        anchor = '<h2>📎 เครื่องมือประกอบ</h2>'
        if anchor not in t:
            raise SystemExit("หาที่แทรกสารบัญเต็มเล่มไม่เจอ")
        t = t.replace(anchor, body + "\n\n" + anchor, 1)
        note = "แทรกใหม่"

    INDEX.write_text(t, encoding="utf-8")
    print(f"\n{INDEX.name:26s} {note} · สารบัญเต็มเล่ม {n_ch} บท")
