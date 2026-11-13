"""บท 0 — ผังแนวคิด "โซ่ที่มีวันล็อก" (dated futures) + "เชือกไม่มีวันล็อก" (perp)

ภาพแนวคิด ไม่มีตัวเลข (ผังครบ 4 ชนิดอยู่บท 9) · `sab-converge` ของบทนี้อยู่ใน tools/sab_charts.py แล้ว
"""

import math

from sab_charts import chart, wrap, text, C

INK, MUTED = C["ink"], C["muted"]
SPOT, FUT = C["blue"], C["amber"]


def _poly(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def _wiggle(x, a=9.0):
    return a * math.sin(x / 41.0) + a * 0.55 * math.sin(x / 15.0 + 1.3)


def _chain(x, y_top, y_bot):
    """ข้อโซ่แนวตั้งระหว่างสองเส้น (วงรีสลับแนว)"""
    out, n = [], max(2, int((y_bot - y_top) / 13))
    step = (y_bot - y_top) / n
    for i in range(n):
        cy = y_top + step * (i + 0.5)
        if i % 2 == 0:
            out.append(f'<ellipse cx="{x:.1f}" cy="{cy:.1f}" rx="3.6" ry="{step * 0.62:.1f}" fill="none" '
                       f'stroke="{MUTED}" stroke-width="2"/>')
        else:
            out.append(f'<ellipse cx="{x:.1f}" cy="{cy:.1f}" rx="2" ry="{step * 0.5:.1f}" fill="{MUTED}"/>')
    return out


def _lock(x, y):
    col = C["purple"]
    return [f'<path d="M{x - 6:.1f},{y - 4:.1f} v-6 a6,6 0 0 1 12,0 v6" fill="none" stroke="{col}" stroke-width="2.4"/>',
            f'<rect x="{x - 9:.1f}" y="{y - 5:.1f}" width="18" height="14" rx="3" fill="{col}"/>',
            f'<circle cx="{x:.1f}" cy="{y + 1.5:.1f}" r="2" fill="#fff"/>']


def _line(pts, col, dash=False):
    d = ' stroke-dasharray="5 4"' if dash else ""
    return (f'<polyline points="{_poly(pts)}" fill="none" stroke="{col}" stroke-width="2.6" '
            f'stroke-linecap="round" stroke-linejoin="round"{d}/>')


@chart("sab-rope-types0")
def _rope_types0(fig):  # noqa: ARG001 — ภาพแนวคิด ไม่อ่านตัวเลข
    W, H = 760, 500
    p = [f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fff"/>']

    # ── แผงบน: โซ่ที่มีวันล็อก ──
    x0, xl, xe = 74, 600, 700
    base = 222
    p.append(f'<rect x="8" y="8" width="{W - 16}" height="236" rx="10" fill="#fafafa" stroke="{C["grid"]}"/>')
    p.append(text(24, 36, "โซ่ที่มีวันล็อก · dated futures", 14, INK, weight=700))
    p.append(text(24, 56, "สัญญาบังคับให้ราคา futures กับราคา spot มาเจอกันในวันหมดอายุ", 12, MUTED))

    def top_pair(x):
        t = min(1.0, (x - x0) / (xl - x0))
        mid = 150 + _wiggle(x) * (1 - 0.35 * t)
        gap = 74 * (1 - t)
        return mid - gap / 2, mid + gap / 2          # (futures, spot) — ค่า y บนจอ

    xs = [x0 + i * 4 for i in range(int((xl - x0) / 4) + 1)]
    fut = [(x, top_pair(x)[0]) for x in xs]
    spot = [(x, top_pair(x)[1]) for x in xs]
    for t in (0.22, 0.47, 0.72):
        x = x0 + t * (xl - x0)
        a, b = top_pair(x)
        p += _chain(x, a + 3, b - 3)
    p.append(_line(fut, FUT))
    p.append(_line(spot, SPOT))
    # หลังวันล็อก: สัญญาจบ เหลือ spot เส้นเดียว (จาง)
    after = [(x, 150 + _wiggle(x) * 0.65) for x in range(xl, xe + 1, 4)]
    p.append(f'<polyline points="{_poly(after)}" fill="none" stroke="{SPOT}" stroke-width="2" stroke-opacity=".35" '
             f'stroke-dasharray="4 4"/>')
    fy0, sy0 = top_pair(x0)
    p.append(text(x0, fy0 - 12, "ราคา futures", 12, FUT, weight=700))
    p.append(text(x0, sy0 + 22, "ราคา spot", 12, SPOT, weight=700))
    xc = x0 + 0.22 * (xl - x0)
    a, b = top_pair(xc)
    p.append(text(xc + 12, (a + b) / 2 + 4, "ระยะที่เชือกยืด = basis", 11.5, INK, weight=600))
    ly = top_pair(xl)[0]
    p += _lock(xl, ly - 16)
    p.append(f'<circle cx="{xl}" cy="{ly:.1f}" r="5" fill="#fff" stroke="{C["purple"]}" stroke-width="2.4"/>')
    p.append(text(xl - 14, ly - 34, "วันล็อก: สองราคาต้องเท่ากัน", 12, C["purple"], "end", 700))
    # แกนเวลา
    p.append(f'<line x1="{x0}" y1="{base}" x2="{xe}" y2="{base}" stroke="{C["axis"]}" stroke-width="1.5"/>')
    for x, lab in ((x0, "วันเปิด"), (xl, "วันหมดอายุ")):
        p.append(f'<line x1="{x}" y1="{base - 5}" x2="{x}" y2="{base + 5}" stroke="{C["grey"]}" stroke-width="1.5"/>')
        p.append(text(x, base + 18, lab, 11, MUTED, "middle"))
    p.append(text(xe - 2, base - 8, "สัญญาจบ", 11, C["grey"], "end"))

    # ── แผงล่าง: เชือกไม่มีวันล็อก ──
    top = 256
    base2 = top + 196
    p.append(f'<rect x="8" y="{top}" width="{W - 16}" height="236" rx="10" fill="#fafafa" stroke="{C["grid"]}"/>')
    p.append(text(24, top + 28, "เชือกไม่มีวันล็อก · perp", 14, INK, weight=700))
    p.append(text(24, top + 48, "ไม่มีวันหมดอายุ จึงไม่มีวันที่สัญญาบังคับให้เจอกัน · มีค่าดึง (funding) จ่ายกันทุกรอบ", 12, MUTED))
    xe2 = 720
    mid0 = top + 118

    def bot_pair(x):
        mid = mid0 + _wiggle(x + 90)
        gap = 13 * math.sin((x - x0) / 62.0) + 3
        return mid - gap, mid + gap * 0.15            # (perp, spot)

    xs2 = [x0 + i * 4 for i in range(int((xe2 - 20 - x0) / 4) + 1)]
    p.append(_line([(x, bot_pair(x)[0]) for x in xs2], FUT))
    p.append(_line([(x, bot_pair(x)[1]) for x in xs2], SPOT))
    py0, sy0 = bot_pair(x0)
    p.append(text(x0, py0 - 26, "ราคา perp", 12, FUT, weight=700))
    p.append(text(x0, sy0 + 30, "ราคา spot", 12, SPOT, weight=700))
    # รอบ funding: เหรียญค่าดึงบนแกนเวลา · เครื่องหมายตามว่า perp อยู่เหนือหรือใต้ spot
    p.append(f'<line x1="{x0}" y1="{base2}" x2="{xe2}" y2="{base2}" stroke="{C["axis"]}" stroke-width="1.5"/>')
    p.append(f'<path d="M{xe2},{base2} l-9,-5 v10 z" fill="{C["grey"]}"/>')
    p.append(text(xe2 - 4, base2 - 10, "ไม่มีวันจบ", 11, C["grey"], "end"))
    for k in range(9):
        x = x0 + 40 + k * 66
        if x > xe2 - 40:
            break
        pf, ps = bot_pair(x)
        plus = pf < ps                                  # y เล็ก = ราคาสูง → perp แพงกว่า spot
        p.append(f'<line x1="{x:.1f}" y1="{base2 - 4}" x2="{x:.1f}" y2="{base2 + 4}" stroke="{C["grey"]}" stroke-width="1.5"/>')
        p.append(text(x, base2 + 17, "รอบ", 10, C["grey"], "middle"))
        p.append(f'<line x1="{x:.1f}" y1="{max(pf, ps) + 8:.1f}" x2="{x:.1f}" y2="{base2 - 22:.1f}" '
                 f'stroke="{C["axis"]}" stroke-dasharray="2 3"/>')
        p.append(f'<circle cx="{x:.1f}" cy="{base2 - 14}" r="9" fill="#fff" stroke="{INK}" stroke-width="1.6"/>')
        p.append(text(x, base2 - 9.5, "+" if plus else "−", 13, INK, "middle", 700))
    p.append(text(24, H - 12, "เหรียญ + : ฝั่ง long จ่ายฝั่ง short     เหรียญ − : ฝั่ง short จ่ายฝั่ง long", 11.5, INK))

    alt = ("ผังสองแผง แผงบนเป็นเส้นราคา futures กับ spot ผูกด้วยโซ่ที่สั้นลงเรื่อย ๆ จนสองเส้นมาเจอกันที่แม่กุญแจวันหมดอายุ "
           "แผงล่างเป็นเส้นราคา perp กับ spot ที่เดินคู่กันไปไม่มีวันจบ มีเหรียญค่าดึงเครื่องหมายบวกหรือลบทุกรอบ")
    cap = ("โซ่ของ dated futures สั้นลงจนล็อกในวันหมดอายุ · เชือกของ perp ไม่มีวันล็อก "
           "มีแต่ค่าดึงที่จ่ายทุกรอบ และฝั่งที่จ่ายสลับกันได้")
    return wrap(W, H, alt, p, cap, "แนวคิด")
