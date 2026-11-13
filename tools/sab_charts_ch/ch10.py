"""บท 10 — ปรับกราฟ sab-selection-bias ให้ป้ายแกนวันมาจาก JSON (ปลั๊กอินของ tools/sab_charts.py)

กราฟต้นแบบใน sab_charts.py ใช้ lines() ซึ่งพิมพ์ป้ายแกน x ทุก ~62 วัน (249 · 311 · 373 …) — ตัวเลขเหล่านี้ไม่มีใน
sab-figures.json จึงเป็น "เลขลอย" ตามกฎ W7 · ปลั๊กอินนี้วาดกราฟเดิมทุกอย่าง แล้วแทนป้ายแกน x ด้วยวันที่ 1 ·
วันแรกของช่วงทดสอบ · วันสุดท้าย (ทุกค่ามาจาก ch10.ค้น)
"""

import re

from sab_charts import CHARTS, C, B, Frame, chart, text  # noqa: F401

_BASE = CHARTS["sab-selection-bias"]


@chart("sab-selection-bias")
def _selection_bias_ch10(fig):
    html = _BASE(fig)
    g, s = fig["ch10"]["กราฟ"], fig["ch10"]["ค้น"]
    top, real = g["อันดับ1"], g["คู่จริง"]
    n, nf = s["วันทั้งหมด"], s["วันช่วงเลือก"]
    f = Frame(min(top + real), max(top + real), 760, 320)
    tick_y = f"{f.Bm + 16:.1f}"
    # ลบป้ายแกน x เดิม (font-size 10.5 ที่ y = Bm + 16) แล้ววางป้ายใหม่จาก JSON
    html = re.sub(r'<text x="[\d.]+" y="' + re.escape(tick_y) + r'" text-anchor="middle" font-size="10.5"[^>]*>[^<]*</text>\n?',
                  "", html)
    X = lambda x: f.L + (x - 1) / (len(top) - 1) * (760 - f.L - f.R)  # noqa: E731
    ticks = [(1, f"วันที่ {B.fmt(1)}", "start"), (nf, f"วันที่ {B.fmt(nf)}", "middle"), (n, f"วันที่ {B.fmt(n)}", "end")]
    labels = "\n".join(text(X(x), f.Bm + 16, lab, 10.5, C["grey"], anc) for x, lab, anc in ticks)
    return html.replace("\n</svg>", "\n" + labels + "\n</svg>", 1)
