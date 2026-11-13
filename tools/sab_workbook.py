#!/usr/bin/env python3
"""สมุดงาน docs/sab-workbook.xlsx — 8 แท็บสูตรสด ของ "Stat Arb for Non Quant · เล่ม 1" (แผน 6.3)

แท็บ: วิเคราะห์คู่ · beta/ระยะแกว่ง · ต้นทุน · บัญชีสองขา · กันชน · บันได carry · funding หลายเส้นทาง · ตาราง φ
ช่องสีเหลือง = ช่องใส่เอง (ค่าตั้งต้นคือตัวอย่างของมินจาก docs/sab-figures.json) · ช่องอื่นเป็นสูตรล้วน

    python3 tools/sab_workbook.py            # เขียน docs/sab-workbook.xlsx
    python3 tools/sab_workbook.py --check    # สร้างใหม่ในโฟลเดอร์ชั่วคราว → soffice --headless แปลง xlsx → xlsx (คำนวณสูตร)
                                             # → อ่านด้วย openpyxl data_only=True → เทียบทุกเซลล์ที่มีคู่ Python/JSON (ต่างได้ ≤ 0.01)
                                             # และตรวจว่า docs/sab-workbook.xlsx ตรงกับที่สคริปต์สร้าง

ทุกเซลล์สูตรที่มี "คู่" ถูกบันทึกไว้ตอนสร้าง: คู่ JSON (ค่าที่บทพิมพ์ · ปัดตามจำนวนทศนิยมใน JSON ก่อนเทียบ)
หรือคู่ Python (คิดซ้ำด้วยตรรกะเดียวกันในสคริปต์นี้ · เทียบตรง)
"""

import json
import math
import os
import shutil
import statistics
import subprocess
import sys
import tempfile

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sab_book as B  # noqa: E402

FIG_PATH = os.path.join(B.DOCS, "sab-figures.json")
OUT = os.path.join(B.DOCS, "sab-workbook.xlsx")
TOL = 0.01

FILL_IN = PatternFill("solid", fgColor="FFF4C2")      # ช่องใส่เอง
FILL_HEAD = PatternFill("solid", fgColor="DBEAFE")    # หัวตาราง
FILL_KEY = PatternFill("solid", fgColor="EDE9FE")     # ผลสำคัญ
BOLD = Font(bold=True)
TITLE = Font(bold=True, size=14)
NOTE = Font(italic=True, color="555555", size=9)


def jget(fig, path):
    """อ่านค่าตาม path แบบ sab_book.get_path แต่รองรับคีย์ที่มีจุด (เช่น 'ต้นทุนไปกลับที่0.1')"""
    parts = path.split(".")

    def walk(cur, i):
        if i == len(parts):
            return True, cur
        for j in range(len(parts), i, -1):
            k = ".".join(parts[i:j])
            if isinstance(cur, dict) and k in cur:
                ok, v = walk(cur[k], j)
                if ok:
                    return ok, v
            elif isinstance(cur, list) and k.isdigit() and int(k) < len(cur):
                ok, v = walk(cur[int(k)], j)
                if ok:
                    return ok, v
        return False, None
    ok, v = walk(fig, 0)
    if not ok:
        raise KeyError(path)
    return v


def load_fig():
    with open(FIG_PATH, encoding="utf-8") as fh:
        return json.load(fh)


# ───────────────────────── ตัวช่วยสร้างแท็บ + บันทึกคู่ ─────────────────────────

class Sheet:
    def __init__(self, wb, checks, fig, title, heading, lines, widths=None):
        self.ws = wb.create_sheet(title)
        self.title, self.checks, self.fig = title, checks, fig
        self.ws["A1"] = heading
        self.ws["A1"].font = TITLE
        for i, ln in enumerate(lines):
            c = self.ws.cell(row=2 + i, column=1, value=ln)
            c.font = NOTE
        self.ws.sheet_view.showGridLines = True
        for col, w in (widths or {}).items():
            self.ws.column_dimensions[col].width = w

    def ref(self, cell, absolute=False):
        if absolute:
            col = "".join(ch for ch in cell if ch.isalpha())
            row = "".join(ch for ch in cell if ch.isdigit())
            cell = f"${col}${row}"
        return f"'{self.title}'!{cell}"

    def label(self, cell, text, bold=False, head=False):
        c = self.ws[cell]
        c.value = text
        if bold or head:
            c.font = BOLD
        if head:
            c.fill = FILL_HEAD
            c.alignment = Alignment(wrap_text=True, vertical="top")
        return c

    def inp(self, cell, value, fmt=None):
        c = self.ws[cell]
        c.value = value
        c.fill = FILL_IN
        if fmt:
            c.number_format = fmt
        return c

    def f(self, cell, formula, py=None, js=None, fmt="#,##0.00", key=False):
        """สูตร + คู่: py = ค่าที่ Python คิดซ้ำ · js = path ใน sab-figures.json"""
        c = self.ws[cell]
        c.value = formula
        if fmt:
            c.number_format = fmt
        if key:
            c.fill = FILL_KEY
            c.font = BOLD
        if py is not None:
            self.checks.append((self.title, cell, "py", py, None))
        if js is not None:
            self.checks.append((self.title, cell, "json", jget(self.fig, js), js))
        return c


def L(col_idx):
    return get_column_letter(col_idx)


# ───────────────────────── แท็บ 1: วิเคราะห์คู่ ─────────────────────────

PAIR_R0 = 27          # แถวข้อมูลแรก
PAIR_ROWS = 800       # รองรับข้อมูลยาวสุด 800 วัน


def pair_example(fig):
    """ตัวอย่างของมิน: คู่อันดับ 1 จากการค้น 200 คู่ (บท 10 · 🎲 seed 11) แปลงเป็นราคาสองเหรียญ
    X ของคู่นี้ = z ในบท (ค่ากลาง 0 · ระยะแกว่ง 1) · ราคา B เป็นคลื่นสมมติ 🔢 · A = 2 × B + X"""
    z = fig["ch10"]["กราฟ"]["อันดับ1"]
    out = []
    for i, x in enumerate(z):
        b = round(50 * (1 + 0.08 * math.sin(2 * math.pi * i / 97) + 0.05 * math.sin(2 * math.pi * i / 23)), 4)
        a = round(2 * b + x, 4)
        out.append((i + 1, a, b))
    return out


def pair_twin(rows, h, n, card):
    """Python คู่ของแท็บวิเคราะห์คู่ (ตรรกะเดียวกับสูตร)"""
    X = [a - h * b for _, a, b in rows]
    f = X[:n]
    m = sum(f) / len(f)
    sd = statistics.stdev(f)
    z = [(x - m) / sd for x in X]
    cross = sum(1 for i in range(1, n) if (z[i] > 0) != (z[i - 1] > 0))
    test = z[n:]
    inband = sum(1 for v in test if abs(v) <= 2) / len(test) * 100
    maxz = max(abs(v) for v in test)
    ra = [rows[i][1] / rows[i - 1][1] - 1 for i in range(1, len(rows))]
    rb = [rows[i][2] / rows[i - 1][2] - 1 for i in range(1, len(rows))]
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    corr = sum((x - ma) * (y - mb) for x, y in zip(ra, rb)) / math.sqrt(
        sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))
    same = sum(1 for x, y in zip(ra, rb) if x * y > 0) / len(ra) * 100
    xp, xc = X[:n - 1], X[1:n]
    mxp, mxc = sum(xp) / len(xp), sum(xc) / len(xc)
    phi = sum((p - mxp) * (c - mxc) for p, c in zip(xp, xc)) / sum((p - mxp) ** 2 for p in xp)
    hl = math.log(0.5) / math.log(phi) if 0 < phi < 1 else None
    # การ์ดบท 12 ในช่วงทดสอบ
    side, paused, ent_i, ent_x = 0, 0, None, None
    nets, reasons = [], []
    for i in range(len(X)):
        idx = i + 1
        if idx <= n:
            continue
        if side != 0:
            el = idx - ent_i
            liq = side * card["ชุด"] * (X[i] - ent_x) - card["ต้นทุนเข้า"] - card["ต้นทุนออก"]
            rec = z[i] <= card["ออก"] if side < 0 else z[i] >= -card["ออก"]
            r = "งบ" if liq <= card["งบ"] else "เป้า" if rec else "เวลา" if el >= card["ถือ"] else None
            if r:
                nets.append(liq)
                reasons.append(r)
                side = 0
                if r == "งบ":
                    paused = 1
        elif paused:
            pass
        elif z[i] >= card["เข้า"]:
            side, ent_i, ent_x = -1, idx, X[i]
        elif z[i] <= -card["เข้า"]:
            side, ent_i, ent_x = 1, idx, X[i]
    return {"mean": m, "sd": sd, "cross": cross, "inband": inband, "maxz": maxz, "corr": corr, "same": same,
            "phi": phi, "hl": hl, "count": len(nets), "sum": sum(nets), "wins": sum(1 for v in nets if v > 0),
            "worst": min(nets) if nets else None, "n_budget": reasons.count("งบ"),
            "n_target": reasons.count("เป้า"), "n_time": reasons.count("เวลา"), "paused": paused, "open": side}


def tab_pair(wb, checks, fig):
    m = fig["บัญชีมิน"]
    card_js = m["การ์ด"]
    s = Sheet(wb, checks, fig, "วิเคราะห์คู่", "วิเคราะห์คู่ — วางราคาปิดสองเหรียญ แล้วอ่านเชือกด้วยตัวเลข (บท 9 · 10 · 12 · 13 · 18)",
              ["วิธีใช้: วางราคาปิดรายวันของเหรียญ A ในคอลัมน์ B และเหรียญ B ในคอลัมน์ C ตั้งแต่แถว %d (ยาวสุด %d วัน) · ช่องสีเหลือง = ใส่เอง" % (PAIR_R0, PAIR_ROWS),
               "ตัวอย่างที่ใส่ไว้: 🎲 คู่อันดับ 1 จากการค้น 200 คู่ในบท 10 (จำลอง · ไม่ใช่เหรียญจริง) — X ของคู่นี้คือ z ในบท · ราคา B เป็นคลื่นสมมติ 🔢 และ A = 2 × B + X",
               "X = A − h × B · ค่ากลางและระยะแกว่งปกติคิดจากช่วงเลือกเท่านั้น (ไม่แอบใช้ช่วงทดสอบ) · ไม้ตามการ์ดบท 12 เทรดเฉพาะช่วงทดสอบ · ผลไม้เป็นหน่วยของ X × จำนวนชุด ก่อนค่าถือ"],
              widths={"A": 30, "B": 14, "C": 14, "D": 8, "E": 12, "F": 12, "G": 10, "H": 8, "I": 8, "J": 9, "K": 10,
                      "L": 10, "M": 8, "N": 10, "O": 10, "P": 7, "Q": 7, "R": 7, "S": 10, "T": 12, "U": 7, "V": 8,
                      "W": 10, "X": 7, "Y": 10})
    ws = s.ws
    # ── ช่องตั้งค่า ──
    s.label("A6", "ตั้งค่า", head=True)
    s.label("B6", "ค่า", head=True)
    card = {"เข้า": card_js["เข้า"], "ออก": card_js["ออก"], "ถือ": card_js["ช่วงถือสูงสุด"], "งบ": card_js["งบขาดทุนสุทธิ"],
            "ต้นทุนเข้า": card_js["ต้นทุนเข้า"], "ต้นทุนออก": card_js["ต้นทุนออก"], "ชุด": m["คู่"]["ชุด"]}
    settings = [("h (จำนวน B ต่อ A 1 เหรียญ)", m["คู่"]["h"]), ("จำนวนวันช่วงเลือก", fig["ch10"]["ค้น"]["วันช่วงเลือก"]),
                ("การ์ด: เข้าเมื่อ |z| ≥", card["เข้า"]), ("การ์ด: ออกเมื่อ |z| ≤", card["ออก"]),
                ("การ์ด: ถือสูงสุด (ช่วง)", card["ถือ"]), ("การ์ด: งบขาดทุนสุทธิ", card["งบ"]),
                ("ต้นทุนเข้า", card["ต้นทุนเข้า"]), ("ต้นทุนออก", card["ต้นทุนออก"]), ("จำนวนชุด", card["ชุด"])]
    for i, (lab, v) in enumerate(settings):
        s.label(f"A{7 + i}", lab)
        s.inp(f"B{7 + i}", v)
    H, N, ENT, EXT, MAXB, BUD, CIN, COUT, SETS = (f"$B${7 + i}" for i in range(9))

    rows = pair_example(fig)
    tw = pair_twin(rows, m["คู่"]["h"], fig["ch10"]["ค้น"]["วันช่วงเลือก"], card)
    r0, r1 = PAIR_R0, PAIR_R0 + PAIR_ROWS - 1
    rng = lambda col: f"{col}${r0}:{col}${r1}"   # noqa: E731

    # ── สรุป ──
    s.label("D6", "ผลของช่วงเลือก / ทดสอบ", head=True)
    s.label("G6", "ค่า", head=True)
    s.label("I6", "ในบท 10 (คู่อันดับ 1)", head=True)
    summ = [
        ("ค่ากลางของ X (ช่วงเลือก)", f"=AVERAGE({rng('F')})", tw["mean"], None),
        ("ระยะแกว่งปกติของ X (ช่วงเลือก)", f"=STDEV({rng('F')})", tw["sd"], None),
        ("ครั้งข้ามค่ากลาง (ช่วงเลือก)", f"=SUM({rng('H')})", tw["cross"], "ch10.อันดับ1.ข้ามค่ากลาง"),
        ("% วันในกรอบ ±2 (ช่วงทดสอบ)", f"=AVERAGE({rng('I')})*100", tw["inband"], "ch10.อันดับ1.ในกรอบ"),
        ("ระยะไกลสุด |z| (ช่วงทดสอบ)", f"=MAX({rng('J')})", tw["maxz"], "ch10.อันดับ1.ระยะสูงสุด"),
        ("correlation ผลตอบแทนรายวัน", f"=CORREL({rng('K')},{rng('L')})", tw["corr"], None),
        ("% วันทิศเดียวกัน (ไม่ใช่ correlation)", f"=AVERAGE({rng('M')})*100", tw["same"], None),
        ("φ ของช่วงเลือก (X วันนี้เทียบเมื่อวาน)", f"=SLOPE({rng('O')},{rng('N')})", tw["phi"], None),
        ("ครึ่งชีวิต (วัน)", '=IF(AND(G14>0,G14<1),LN(0.5)/LN(G14),"ไม่มี")', tw["hl"], None),
        ("การ์ด: จำนวนไม้ที่ปิด", f"=COUNT({rng('Y')})", tw["count"], None),
        ("การ์ด: รวมสุทธิ", f"=SUM({rng('Y')})", tw["sum"], None),
        ("การ์ด: ไม้กำไร", f'=COUNTIF({rng("Y")},">0")', tw["wins"], None),
        ("การ์ด: ไม้แย่สุด", f'=IF(COUNT({rng("Y")})=0,"",MIN({rng("Y")}))', tw["worst"], None),
        ("ออกเพราะงบ", f'=COUNTIF({rng("T")},"ออก:งบ")', tw["n_budget"], None),
        ("ออกเพราะเป้า", f'=COUNTIF({rng("T")},"ออก:เป้า")', tw["n_target"], None),
        ("ออกเพราะเวลา", f'=COUNTIF({rng("T")},"ออก:เวลา")', tw["n_time"], None),
        ("โหมดพักตอนจบ (1 = พัก)", f"=MAX({rng('X')})", tw["paused"], None),
    ]
    for i, (lab, frm, py, js) in enumerate(summ):
        r = 7 + i
        s.label(f"D{r}", lab)
        s.f(f"G{r}", frm, py=py, js=js, fmt="0.00", key=js is not None)
        if js:
            ws[f"I{r}"] = jget(fig, js)
            ws[f"I{r}"].font = NOTE
    ws["I16"] = "ครึ่งชีวิตต้องใช้ φ < 1 · φ ใกล้ 1 เชื่อไม่ได้ (บท 13)"
    ws["I16"].font = NOTE

    # ── หัวตารางข้อมูล ──
    heads = ["วันที่", "ราคาปิด A", "ราคาปิด B", "ลำดับ", "X = A − hB", "X ช่วงเลือก", "z", "ข้าม", "ในกรอบ",
             "|z| ทดสอบ", "ผลตอบแทน A", "ผลตอบแทน B", "ทิศเดียวกัน", "X เมื่อวาน", "X วันนี้", "ถือ (ก่อน)",
             "พัก (ก่อน)", "ช่วงที่ถือ", "สุทธิถ้าออกตอนนี้", "เหตุการณ์", "ถือ (หลัง)", "วันเข้า", "X ตอนเข้า",
             "พัก (หลัง)", "สุทธิไม้ที่ปิด"]
    for j, hd in enumerate(heads):
        s.label(f"{L(j + 1)}{r0 - 1}", hd, head=True)
    for k in range(PAIR_ROWS):
        r = r0 + k
        p = r - 1
        if k < len(rows):
            day, a, b = rows[k]
            s.inp(f"A{r}", day)
            s.inp(f"B{r}", a, "0.0000")
            s.inp(f"C{r}", b, "0.0000")
        else:
            for col in "ABC":
                ws[f"{col}{r}"].fill = FILL_IN
        ws[f"D{r}"] = f'=IF(OR(B{r}="",C{r}=""),"",ROW()-{r0 - 1})'
        ws[f"E{r}"] = f'=IF(D{r}="","",B{r}-{H}*C{r})'
        ws[f"F{r}"] = f'=IF(D{r}="","",IF(D{r}<={N},E{r},""))'
        ws[f"G{r}"] = f'=IF(D{r}="","",(E{r}-$G$7)/$G$8)'
        ws[f"G{r}"].number_format = "0.00"
        if k == 0:
            ws[f"H{r}"] = '=""'
            ws[f"K{r}"] = '=""'
            ws[f"L{r}"] = '=""'
            ws[f"N{r}"] = '=""'
            ws[f"O{r}"] = '=""'
        else:
            ws[f"H{r}"] = f'=IF(D{r}="","",IF(D{r}<={N},IF((G{r}>0)<>(G{p}>0),1,0),""))'
            ws[f"K{r}"] = f'=IF(D{r}="","",B{r}/B{p}-1)'
            ws[f"L{r}"] = f'=IF(D{r}="","",C{r}/C{p}-1)'
            ws[f"N{r}"] = f'=IF(D{r}="","",IF(D{r}<={N},E{p},""))'
            ws[f"O{r}"] = f'=IF(D{r}="","",IF(D{r}<={N},E{r},""))'
        ws[f"I{r}"] = f'=IF(D{r}="","",IF(D{r}>{N},IF(ABS(G{r})<=2,1,0),""))'
        ws[f"J{r}"] = f'=IF(D{r}="","",IF(D{r}>{N},ABS(G{r}),""))'
        ws[f"M{r}"] = f'=IF(K{r}="","",IF(K{r}*L{r}>0,1,0))'
        for col in "KL":
            ws[f"{col}{r}"].number_format = "0.00%"
        # การ์ดบท 12 (เครื่องสถานะ: ถือ −1 = short X · 1 = long X)
        if k == 0:
            ws[f"P{r}"] = 0
            ws[f"Q{r}"] = 0
            prev_ent, prev_x = '""', '""'
        else:
            ws[f"P{r}"] = f'=IF(D{r}="","",U{p})'
            ws[f"Q{r}"] = f'=IF(D{r}="","",X{p})'
            prev_ent, prev_x = f"V{p}", f"W{p}"
        ws[f"R{r}"] = f'=IF(D{r}="","",IF(P{r}=0,"",D{r}-{prev_ent}))'
        ws[f"S{r}"] = f'=IF(D{r}="","",IF(P{r}=0,"",P{r}*{SETS}*(E{r}-{prev_x})-{CIN}-{COUT}))'
        ws[f"T{r}"] = (f'=IF(D{r}="","",IF(D{r}<={N},"",IF(P{r}<>0,IF(S{r}<={BUD},"ออก:งบ",'
                       f'IF(IF(P{r}<0,G{r}<={EXT},G{r}>=-{EXT}),"ออก:เป้า",IF(R{r}>={MAXB},"ออก:เวลา","ถือ"))),'
                       f'IF(Q{r}=1,"พัก",IF(G{r}>={ENT},"เข้า short",IF(G{r}<=-{ENT},"เข้า long","รอ"))))))')
        ws[f"U{r}"] = (f'=IF(D{r}="","",IF(LEFT(T{r},3)="ออก",0,IF(T{r}="เข้า short",-1,'
                       f'IF(T{r}="เข้า long",1,P{r}))))')
        ws[f"V{r}"] = f'=IF(D{r}="","",IF(OR(T{r}="เข้า short",T{r}="เข้า long"),D{r},{prev_ent}))'
        ws[f"W{r}"] = f'=IF(D{r}="","",IF(OR(T{r}="เข้า short",T{r}="เข้า long"),E{r},{prev_x}))'
        ws[f"X{r}"] = f'=IF(D{r}="","",IF(T{r}="ออก:งบ",1,Q{r}))'
        ws[f"Y{r}"] = f'=IF(D{r}="","",IF(LEFT(T{r},3)="ออก",S{r},""))'
        for col in "ESWY":
            ws[f"{col}{r}"].number_format = "0.00"
    ws.freeze_panes = f"D{r0}"
    return s


# ───────────────────────── แท็บ 2: beta/ระยะแกว่ง ─────────────────────────

# 🔢 ตัวอย่างสอน: การขยับรายวัน (%) ของ BTC และเหรียญ A — วันที่ BTC ขยับแรง A ขยับราว 1.5 เท่า
BETA_MOVES = [(-4, -6), (1, 0.4), (2.5, 3.9), (-0.5, -1.1), (3, 4.4), (-2.2, -3.4), (0.8, 1.6), (-1, -0.7),
              (4, 6.1), (-3, -4.4), (0.3, -0.2), (1.5, 2.6), (-2.5, -3.8), (0.6, 0.2), (2.1, 3.1), (-1.2, -2.0)]


def beta_rows(fig):
    btc = fig["บัญชีมิน"]["BTC"]["spot"]
    a = fig["บัญชีมิน"]["คู่"]["A"]
    out = [(1, btc, a)]
    pb, pa = btc, a
    for i, (mb, ma) in enumerate(BETA_MOVES):
        pb = round(pb * (1 + mb / 100), 2)
        pa = round(pa * (1 + ma / 100), 4)
        out.append((i + 2, pb, pa))
    return out


def tab_beta(wb, checks, fig):
    m = fig["บัญชีมิน"]
    s = Sheet(wb, checks, fig, "beta และระยะแกว่ง", "beta / ระยะแกว่ง — นับ beta จากวันที่ BTC ขยับแรง แล้วคิด exposure (บท 8)",
              ["วิธีนับ: เลือกวันที่ BTC ขยับเกินเส้น (ค่าตั้งต้น 2%) → ผลรวมการขยับของเหรียญ (คิดเครื่องหมายตามทิศ BTC) ÷ ผลรวมขนาดการขยับของ BTC",
               "ตัวอย่างราคาที่ใส่ไว้เป็น 🔢 ตัวเลขสมมติเพื่อสอน (ไม่ใช่ราคาจริง) — วางราคาปิดของคุณทับได้ · ค่าแกว่งตามช่วงข้อมูลที่เลือก",
               "ส่วนล่าง: exposure ของคู่ A–B ในบท 8 (มูลค่า × beta) · ขา B ทำผ่าน perp ของ B"],
              widths={"A": 34, "B": 14, "C": 14, "D": 12, "E": 12, "F": 10, "G": 12, "H": 12, "I": 4, "J": 30,
                      "K": 12, "L": 12, "M": 12})
    ws = s.ws
    s.label("A6", "เส้นวันขยับแรง (%)")
    s.inp("B6", 2)
    rows = beta_rows(fig)
    r0 = 9
    r1 = r0 + 199
    for j, hd in enumerate(["วัน", "ราคาปิด BTC", "ราคาปิดเหรียญ", "BTC ขยับ %", "เหรียญขยับ %", "วันแรง?",
                            "ขยับตามทิศ BTC", "ขนาดขยับ BTC"]):
        s.label(f"{L(j + 1)}{r0 - 1}", hd, head=True)
    for k in range(200):
        r = r0 + k
        if k < len(rows):
            s.inp(f"A{r}", rows[k][0])
            s.inp(f"B{r}", rows[k][1], "#,##0.00")
            s.inp(f"C{r}", rows[k][2], "0.0000")
        else:
            for col in "ABC":
                ws[f"{col}{r}"].fill = FILL_IN
        if k == 0:
            ws[f"D{r}"] = '=""'
            ws[f"E{r}"] = '=""'
        else:
            ws[f"D{r}"] = f'=IF(OR(B{r}="",B{r - 1}=""),"",(B{r}/B{r - 1}-1)*100)'
            ws[f"E{r}"] = f'=IF(OR(C{r}="",C{r - 1}=""),"",(C{r}/C{r - 1}-1)*100)'
        ws[f"F{r}"] = f'=IF(D{r}="","",IF(ABS(D{r})>$B$6,1,0))'
        ws[f"G{r}"] = f'=IF(F{r}=1,E{r}*SIGN(D{r}),"")'
        ws[f"H{r}"] = f'=IF(F{r}=1,ABS(D{r}),"")'
        for col in "DEGH":
            ws[f"{col}{r}"].number_format = "0.00"
    # คู่ Python
    th = 2
    mv = [((rows[i][1] / rows[i - 1][1] - 1) * 100, (rows[i][2] / rows[i - 1][2] - 1) * 100) for i in range(1, len(rows))]
    big = [(b, a) for b, a in mv if abs(b) > th]
    beta_py = sum(a * (1 if b > 0 else -1) for b, a in big) / sum(abs(b) for b, a in big)
    sd_b = statistics.stdev([b for b, _ in mv])
    sd_a = statistics.stdev([a for _, a in mv])
    s.label("J6", "ผล", head=True)
    s.label("K6", "ค่า", head=True)
    res = [("จำนวนวันแรง", f"=SUM(F{r0}:F{r1})", len(big)),
           ("beta ของเหรียญเทียบ BTC", f"=SUM(G{r0}:G{r1})/SUM(H{r0}:H{r1})", beta_py),
           ("ระยะแกว่งปกติรายวัน BTC (%)", f"=STDEV(D{r0}:D{r1})", sd_b),
           ("ระยะแกว่งปกติรายวัน เหรียญ (%)", f"=STDEV(E{r0}:E{r1})", sd_a)]
    for i, (lab, frm, py) in enumerate(res):
        s.label(f"J{7 + i}", lab)
        s.f(f"K{7 + i}", frm, py=py, fmt="0.00", key=i == 1)

    # ── exposure ของคู่ (บท 8) ──
    s.label("J13", "exposure ของคู่ A–B (บท 8)", head=True)
    s.label("K13", "ค่า", head=True)
    exp_in = [("มูลค่าขา A", fig["ch08"]["ขาเดียว"]["A"]), ("beta A", m["beta"]["A"]), ("beta B", m["beta"]["B"]),
              ("ราคา B", m["คู่"]["B"]), ("BTC ขยับ (%)", fig["ch08"]["ขาเดียว"]["BTCลงเปอร์เซ็นต์"])]
    for i, (lab, v) in enumerate(exp_in):
        s.label(f"J{14 + i}", lab)
        s.inp(f"K{14 + i}", v)
    s.label("J20", "วิธี hedge", head=True)
    for col, hd in zip("KLM", ["จำนวนเท่ากัน", "มูลค่าเท่ากัน", "beta-neutral"]):
        s.label(f"{col}20", hd, head=True)
    s.label("J21", "จำนวน B ที่ short")
    s.label("J22", "มูลค่าขา B")
    s.label("J23", "มูลค่าสุทธิ")
    s.label("J24", "beta exposure")
    s.label("J25", "ผลเมื่อ BTC ขยับ")
    s.label("J26", "B ขยับเอง 1% (ขา short เสีย)")
    for col, key in zip("KLM", ["จำนวนเท่ากัน", "มูลค่าเท่ากัน", "betaneutral"]):
        js = f"ch08.สามวิธี.{key}"
        s.inp(f"{col}21", jget(fig, js + ".จำนวนB"))
        s.f(f"{col}22", f"={col}21*$K$17", js=js + ".มูลค่าB", fmt="#,##0")
        s.f(f"{col}23", f"=$K$14-{col}22", js=js + ".มูลค่าสุทธิ", fmt="#,##0")
        s.f(f"{col}24", f"=$K$14*$K$15-{col}22*$K$16", js=js + ".betaexposure", fmt="#,##0")
        s.f(f"{col}25", f"={col}24*$K$18/100", js=js + ".BTCลง4", fmt="#,##0.00", key=True)
        v = jget(fig, js + ".มูลค่าB")
        s.f(f"{col}26", f"=-{col}22*1/100", js=f"ch08.stress_B1%.ขา{v}", fmt="#,##0.00")
    # stress beta
    bs = fig["ch08"]["beta_stress"]
    s.label("J28", "beta เปลี่ยนตอนตลาดลงแรง", head=True)
    s.label("K28", "ค่า", head=True)
    s.label("J29", "มูลค่า hedge (beta-neutral เดิม)")
    s.inp("K29", bs["hedgeBTC"])
    s.label("J30", "beta A ใหม่")
    s.inp("K30", m["beta"]["A_stress"])
    s.label("J31", "BTC ขยับ (%)")
    s.inp("K31", -5)
    s.label("J32", "exposure ที่โผล่มา")
    s.f("K32", "=$K$14*K30-K29", js="ch08.beta_stress.exposure", fmt="#,##0")
    s.label("J33", "ผล")
    s.f("K33", "=K32*K31/100", js="ch08.beta_stress.BTC-5%", fmt="#,##0.00", key=True)
    # ปัด lot
    lot = fig["ch08"]["ปัดlot"]
    s.label("J35", "ปัด lot ขา hedge ด้วย BTC perp", head=True)
    s.label("K35", "ค่า", head=True)
    s.label("J36", "ราคา BTC")
    s.inp("K36", m["BTC"]["spot"])
    s.label("J37", "BTC ที่ต้องการ")
    s.f("K37", "=K29/K36", js="ch08.ปัดlot.ต้องการBTC", fmt="0.000")
    s.label("J38", "ปัดลง (BTC)")
    s.inp("K38", lot["ปัดลง"]["BTC"])
    s.label("J39", "exposure เหลือ")
    s.f("K39", "=K29-K38*K36", js="ch08.ปัดlot.ปัดลง.exposure", fmt="#,##0")
    s.label("J40", "ปัดขึ้น (BTC)")
    s.inp("K40", lot["ปัดขึ้น"]["BTC"])
    s.label("J41", "exposure เหลือ")
    s.f("K41", "=K29-K40*K36", js="ch08.ปัดlot.ปัดขึ้น.exposure", fmt="#,##0")
    ws.freeze_panes = f"A{r0}"
    return s


# ───────────────────────── แท็บ 3: ต้นทุน ─────────────────────────

def tab_cost(wb, checks, fig):
    m = fig["บัญชีมิน"]
    s = Sheet(wb, checks, fig, "ต้นทุน", "ต้นทุนไปกลับ — ซื้อแล้วขายคืนทันทีเสียเท่าไร (บท 1 · ใบ 01)",
              ["ค่าธรรมเนียม: taker %s%% · maker %s%% (ประกาศบรรทัดแรกทุกตาราง) · 🔢 ตัวเลขสมมติเพื่อสอน · ตารางคิดที่ 1 BTC" %
               (m["ค่าธรรมเนียม"]["taker"], m["ค่าธรรมเนียม"]["maker"]),
               "คอลัมน์ C = ค่าธรรมเนียมที่มินเคยจ่ายในเล่ม \"คิดแบบ Quant\" (ⓝ เทียบ)"],
              widths={"A": 40, "B": 18, "C": 22})
    ws = s.ws
    s.label("A5", "รายการ", head=True)
    s.label("B5", "taker (ค่าตั้งต้น)", head=True)
    s.label("C5", "ค่าธรรมเนียมแบบมินใน nq", head=True)
    labels = ["ราคาเสนอซื้อ (bid)", "ราคาเสนอขาย (ask)", "จำนวน BTC", "ค่าธรรมเนียมต่อข้าง (%)", "ราคากลาง (mid)",
              "ส่วนต่างราคาซื้อ-ขาย", "ส่วนต่างที่เสียไปกลับ", "ค่าธรรมเนียมไปกลับ", "รวมต่อขา", "% ของราคากลาง",
              "สองขา (spot + futures)", "basis บนจอ", "basis หลังต้นทุนสองขา"]
    for i, lab in enumerate(labels):
        s.label(f"A{6 + i}", lab)
    for col, fee, js in (("B", m["ค่าธรรมเนียม"]["taker"], "ch01.ต้นทุนไปกลับ"),
                         ("C", m["ค่าธรรมเนียม"]["มินในnq"], "ch01.ต้นทุนไปกลับที่0.1")):
        s.inp(f"{col}6", m["BTC"]["bid"], "#,##0")
        s.inp(f"{col}7", m["BTC"]["ask"], "#,##0")
        s.inp(f"{col}8", 1)
        s.inp(f"{col}9", fee, "0.00")
        both = col == "B"
        s.f(f"{col}10", f"=({col}6+{col}7)/2", js="ch01.ต้นทุนไปกลับ.mid" if both else None, fmt="#,##0")
        s.f(f"{col}11", f"={col}7-{col}6", js="ch01.ต้นทุนไปกลับ.ส่วนต่าง" if both else None, fmt="#,##0")
        s.f(f"{col}12", f"=-({col}7-{col}6)*{col}8", js="ch01.ต้นทุนไปกลับ.ส่วนต่างราคา" if both else None, fmt="#,##0")
        s.f(f"{col}13", f"=-{col}9/100*({col}6+{col}7)*{col}8", js=js + ".ค่าธรรมเนียม", fmt="#,##0")
        s.f(f"{col}14", f"={col}12+{col}13", js=js + ".รวม", fmt="#,##0", key=True)
        s.f(f"{col}15", f"=-{col}14/({col}10*{col}8)*100", js=js + ".เปอร์เซ็นต์", fmt="0.00")
        s.f(f"{col}16", f"=2*{col}14", js=js + ".สองขา", fmt="#,##0")
        s.inp(f"{col}17", m["BTC"]["basis"], "#,##0")
        s.f(f"{col}18", f"={col}17+{col}16", js=js + ".3000ลบสองขา", fmt="#,##0", key=True)
    return s


# ───────────────────────── แท็บ 4: บัญชีสองขา ─────────────────────────

def ledger_py(cap, s0, f0, m, s1, f1, st):
    rows = []
    free, spot, mar = cap, 0, 0
    rows.append((free, spot, mar, free + spot + mar))
    free, spot = cap - s0, s0
    rows.append((free, spot, mar, free + spot + mar))
    free, mar = free - m * f0, m * f0
    rows.append((free, spot, mar, free + spot + mar))
    spot, mar = s1, mar - (f1 - f0)
    rows.append((free, spot, mar, free + spot + mar))
    top = m * f1 - mar
    paid = min(top, free)
    free, mar = free - paid, mar + paid
    rows.append((free, spot, mar, free + spot + mar))
    spot, mar = st, mar - (st - f1)
    rows.append((free, spot, mar, free + spot + mar))
    return rows, top, max(0, top - (rows[3][0]))


def tab_ledger(wb, checks, fig):
    m = fig["บัญชีมิน"]
    s = Sheet(wb, checks, fig, "บัญชีสองขา", "สมุดบัญชีสองขา — เงินสดอิสระ · มูลค่า spot · หลักประกัน · equity (บท 3 · 4 · ใบ 03)",
              ["long spot 1 BTC + short futures 1 BTC · กติกาสอน: หลักประกัน = 10% ของราคา futures ปัจจุบัน ชำระสิ้นวัน · 🔢 ตัวเลขสมมติเพื่อสอน (แว่นขยาย ×100)",
               "คอลัมน์ B = ทุนของมิน · C = ทุนของต้น · ถ้าเงินสดอิสระไม่พอโอนเติม แถว 'ขาด' จะไม่เป็นศูนย์"],
              widths={"A": 34, "B": 16, "C": 16, "D": 4, "E": 30, "F": 16, "G": 16, "H": 16, "I": 16})
    ws = s.ws
    s.label("A5", "ค่าที่ใส่", head=True)
    s.label("B5", "มิน", head=True)
    s.label("C5", "ต้น", head=True)
    k4 = fig["ch04"]
    inputs = [("ทุน", m["ทุนภาค1"]["รวม"], k4["ทุนของต้น"]), ("ราคา spot ตอนเปิด", m["BTC"]["spot"], m["BTC"]["spot"]),
              ("ราคา futures ตอนเปิด", m["BTC"]["futures"], m["BTC"]["futures"]),
              ("หลักประกัน (% ของ futures)", m["กติกาหลักประกันเปอร์เซ็นต์"], m["กติกาหลักประกันเปอร์เซ็นต์"]),
              ("spot คืนวันที่ 9", k4["คืนวันที่9"]["spot"], k4["คืนวันที่9"]["spot"]),
              ("futures คืนวันที่ 9", k4["คืนวันที่9"]["futures"], k4["คืนวันที่9"]["futures"]),
              ("ราคาชำระวันหมดอายุ", m["BTC"]["ราคาชำระ"], m["BTC"]["ราคาชำระ"])]
    for i, (lab, a, b) in enumerate(inputs):
        s.label(f"A{6 + i}", lab)
        s.inp(f"B{6 + i}", a, "#,##0")
        s.inp(f"C{6 + i}", b, "#,##0")
    s.label("A14", "ผลคืนวันที่ 9", head=True)
    s.label("A15", "ขา futures ถูกหัก (variation margin)")
    s.label("A16", "หลักประกันที่ต้องมี")
    s.label("A17", "ต้องโอนเติม")
    s.label("A18", "ขาด (เงินสดอิสระไม่พอ)")
    for col, cap in (("B", m["ทุนภาค1"]["รวม"]), ("C", k4["ทุนของต้น"])):
        rows, top, short = ledger_py(cap, m["BTC"]["spot"], m["BTC"]["futures"], 0.1, 110000, 113200, 105000)
        mine = col == "B"
        s.f(f"{col}15", f"=-({col}11-{col}8)", js="ch04.variation_margin" if mine else None, py=-(113200 - 103000), fmt="#,##0")
        s.f(f"{col}16", f"={col}9/100*{col}11", js="ch04.หลักประกันที่ต้องมี" if mine else None, fmt="#,##0")
        s.f(f"{col}17", f"={col}16-({col}9/100*{col}8+{col}15)", js="ch04.ต้องโอน", fmt="#,##0", key=True)
        s.f(f"{col}18", f"=MAX(0,{col}17-({col}6-{col}7-{col}9/100*{col}8))", py=short,
            js=None if mine else "ch04.ต้นขาด", fmt="#,##0", key=True)
    # ── ตารางบัญชี ──
    events = ["เริ่ม", "ซื้อ spot", "short futures วางหลักประกัน", "ชำระคืนวันที่ 9", "หลังโอนเติม", "ชำระวันหมดอายุ"]
    for top_row, col, cap, js, nrows in ((21, "B", m["ทุนภาค1"]["รวม"], "ch04.ตารางบัญชี", 6),
                                          (30, "C", k4["ทุนของต้น"], "ch04.ตารางบัญชีต้น", 4)):
        who = "มิน" if col == "B" else "ต้น"
        s.label(f"E{top_row - 1}", f"สมุดบัญชีของ{who}", head=True)
        for j, hd in enumerate(["เงินสดอิสระ", "มูลค่า spot", "หลักประกัน", "equity"]):
            s.label(f"{L(6 + j)}{top_row - 1}", hd, head=True)
        rows, _, _ = ledger_py(cap, 100000, 103000, 0.1, 110000, 113200, 105000)
        c = col
        fr = {  # (free, spot, margin) ต่อแถว
            0: (f"={c}6", "=0", "=0"),
            1: (f"={c}6-{c}7", f"={c}7", "=0"),
            2: (f"={c}6-{c}7-{c}9/100*{c}8", f"={c}7", f"={c}9/100*{c}8"),
            3: (f"=F{top_row + 2}", f"={c}10", f"=H{top_row + 2}-({c}11-{c}8)"),
            4: (f"=F{top_row + 3}-MIN({c}17,F{top_row + 3})", f"={c}10", f"=H{top_row + 3}+MIN({c}17,F{top_row + 3})"),
            5: (f"=F{top_row + 4}", f"={c}12", f"=H{top_row + 4}-({c}12-{c}11)"),
        }
        for i in range(6):
            r = top_row + i
            s.label(f"E{r}", events[i])
            jsrow = f"{js}.{i}" if i < nrows else None
            vals = rows[i]
            for j, colx in enumerate("FGH"):
                key = ["เงินสดอิสระ", "มูลค่าspot", "หลักประกัน"][j]
                s.f(f"{colx}{r}", fr[i][j], py=vals[j], js=f"{jsrow}.{key}" if jsrow else None, fmt="#,##0")
            s.f(f"I{r}", f"=F{r}+G{r}+H{r}", py=vals[3], js=f"{jsrow}.equity" if jsrow else None, fmt="#,##0", key=True)
    # ── กรณี 2 (บท 3) ──
    c2 = fig["ch03"]["กรณี2"]
    s.label("A40", "กรณีสอง: วันหลังราคาเปลี่ยน (บท 3)", head=True)
    s.label("B40", "ค่า", head=True)
    for i, (lab, v) in enumerate([("spot ตอนเปิด", m["BTC"]["spot"]), ("futures ตอนเปิด", m["BTC"]["futures"]),
                                  ("spot วันนี้", c2["spot"]), ("futures วันนี้", c2["futures"])]):
        s.label(f"A{41 + i}", lab)
        s.inp(f"B{41 + i}", v, "#,##0")
    s.label("A45", "basis วันนี้")
    s.f("B45", "=B44-B43", js="ch03.กรณี2.basis", fmt="#,##0")
    s.label("A46", "ขา spot")
    s.f("B46", "=B43-B41", js="ch03.กรณี2.ขาspot", fmt="#,##0")
    s.label("A47", "ขา futures (short)")
    s.f("B47", "=B42-B44", js="ch03.กรณี2.ขาfutures", fmt="#,##0")
    s.label("A48", "รวมสองขา")
    s.f("B48", "=B46+B47", js="ch03.กรณี2.รวม", fmt="#,##0", key=True)
    return s


# ───────────────────────── แท็บ 5: กันชน ─────────────────────────

def tab_buffer(wb, checks, fig):
    m = fig["บัญชีมิน"]
    k4 = fig["ch04"]
    s = Sheet(wb, checks, fig, "กันชน", "ใบกันชนเงินสด — futures ขึ้นได้กี่ % ในวันเดียวก่อนเงินสดอิสระหมด (บท 4 · ใบ 04)",
              ["ต้องโอนเติม = (1 + อัตราหลักประกัน) × (futures ใหม่ − futures เดิม) · กำไรขา spot ใช้จ่ายหลักประกันไม่ได้ (สองกระเป๋า) · 🔢 ตัวเลขสมมติเพื่อสอน",
               "ตารางล่าง: spot ขึ้น x% และ basis หลังขยับ 3,200 แบบคืนวันที่ 9 (สมมติฐานใน JSON _สมมติฐาน)"],
              widths={"A": 40, "B": 16, "C": 16, "D": 16})
    s.label("A5", "ค่าที่ใส่", head=True)
    caps = [m["ทุนภาค1"]["รวม"], k4["ทุนของต้น"], 150000]
    for col, cap in zip("BCD", caps):
        s.label(f"{col}5", f"ทุน {cap:,}", head=True)
        s.inp(f"{col}6", cap, "#,##0")
        s.inp(f"{col}7", m["BTC"]["spot"], "#,##0")
        s.inp(f"{col}8", m["BTC"]["futures"], "#,##0")
        s.inp(f"{col}9", m["กติกาหลักประกันเปอร์เซ็นต์"], "0")
    for i, lab in enumerate(["ทุน", "ราคา spot", "ราคา futures", "หลักประกัน (%)", "เงินสดอิสระหลังเปิดไม้",
                             "กันชนเป็นเงิน (futures ขึ้นได้กี่ดอลลาร์)", "กันชน (%)"]):
        s.label(f"A{6 + i}", lab)
    for col, cap in zip("BCD", caps):
        free = cap - 100000 - 10300
        bufm = free / 1.1
        s.f(f"{col}10", f"={col}6-{col}7-{col}9/100*{col}8", py=free, fmt="#,##0")
        s.f(f"{col}11", f"={col}10/(1+{col}9/100)", py=bufm,
            js=f"ch04.กันชนเงิน.{cap}" if str(cap) in k4["กันชนเงิน"] else None, fmt="#,##0.00")
        s.f(f"{col}12", f"={col}11/{col}8*100", py=bufm / 103000 * 100, js=f"ch04.กันชน.{cap}", fmt="0.0", key=True)
    s.label("A15", "spot ขึ้น (%)", head=True)
    s.label("B15", "futures ใหม่", head=True)
    s.label("C15", "ต้องโอนเติม", head=True)
    s.label("D15", "ขาด ที่ทุนคอลัมน์ B", head=True)
    s.label("E15", "ขาด ที่ทุนคอลัมน์ C", head=True)
    s.ws.column_dimensions["E"].width = 18
    s.label("A14", "basis หลังขยับ")
    s.inp("B14", k4["คืนวันที่9"]["futures"] - k4["คืนวันที่9"]["spot"], "#,##0")
    for i, d in enumerate(k4["dist"]):
        r = 16 + i
        s.inp(f"A{r}", d["spotขึ้นเปอร์เซ็นต์"])
        s.f(f"B{r}", f"=$B$7*(1+A{r}/100)+$B$14", js=f"ch04.dist.{i}.futures", fmt="#,##0")
        s.f(f"C{r}", f"=(1+$B$9/100)*(B{r}-$B$8)", js=f"ch04.dist.{i}.ต้องโอน", fmt="#,##0")
        s.f(f"D{r}", f"=MAX(0,C{r}-$B$10)", js=f"ch04.dist.{i}.ขาดที่ทุน125000", fmt="#,##0")
        s.f(f"E{r}", f"=MAX(0,C{r}-$C$10)", js=f"ch04.dist.{i}.ขาดที่ทุน120000", fmt="#,##0")
    s.label("A20", "กันชนสะสม: หลังโอนเติมวันแรก (แถว 10%) รับได้อีก (%)")
    s.f("B20", "=MAX(0,$B$10-C17)/(1+$B$9/100)/B17*100", js="ch04.หลังวันแรกรับได้อีก", fmt="0.0", key=True)
    s.label("A21", "เงินสดอิสระหลังโอนเติม")
    s.f("B21", "=MAX(0,$B$10-C17)", js="ch04.เงินสดอิสระหลังโอน", fmt="#,##0")
    return s


# ───────────────────────── แท็บ 6: บันได carry ─────────────────────────

def ladder_py(fee=0.05, basis=3000, cap=125000, hurdle=4, s0=100000, days=90, st=105000):
    f0 = s0 + basis
    fees = fee / 100 * (s0 + f0 + st)
    net = basis - fees
    opp = cap * hurdle / 100 * days / 365
    k = 365 / days * 100
    return {"basis": basis, "บนจอ": basis / s0 * k, "ต่อทุน": basis / cap * k, "ค่าธรรมเนียม": fees, "สุทธิ": net,
            "หลังค่าธรรมเนียม": net / cap * k, "ค่าเสียโอกาส": opp, "ส่วนเกิน": net - opp,
            "ส่วนเกินเปอร์เซ็นต์": (net - opp) / cap * k}


def tab_ladder(wb, checks, fig):
    m = fig["บัญชีมิน"]
    s = Sheet(wb, checks, fig, "บันได carry", "บันได carry — จาก % บนจอ ถึงส่วนเกินที่เหลือในมือ (บท 5 · 6 · ใบ 05)",
              ["ค่าธรรมเนียม: taker %s%% · maker %s%% · คิดสามครั้ง: ซื้อ spot · short futures · ขาย spot วันหมดอายุ (futures ชำระเองไม่เสีย) · 🔢 ตัวเลขสมมติเพื่อสอน" %
               (m["ค่าธรรมเนียม"]["taker"], m["ค่าธรรมเนียม"]["maker"]),
               "hurdle = ผลตอบแทนที่คุณได้แน่ ๆ ถ้าไม่ทำอะไร (ค่าเสียโอกาสของเรา ไม่ใช่ตัวเลข crowding)"],
              widths={"A": 40, "B": 16, "C": 16, "D": 16, "E": 4, "F": 34, "G": 14, "H": 14})
    s.label("A5", "ค่าที่ใส่", head=True)
    cols = [("B", "มิน", 0.05, 4, "ch05.บันได"), ("C", "ค่าธรรมเนียม 0.1%", 0.1, 4, "ch05.บันไดที่0.1"),
            ("D", "hurdle 9%", 0.05, 9, "ch05.hurdle9")]
    labels = ["ราคา spot", "ราคา futures", "วันถึงหมดอายุ", "ทุน", "ค่าธรรมเนียมต่อข้าง (%)", "hurdle ต่อปี (%)",
              "ราคาชำระวันหมดอายุ", "basis", "① บนจอ (% ต่อปีของราคา spot)", "② ต่อทุน (% ต่อปี)", "ค่าธรรมเนียมรวม",
              "สุทธิหลังค่าธรรมเนียม", "③ หลังค่าธรรมเนียม (% ต่อปี)", "ค่าเสียโอกาส", "ส่วนเกิน", "④ ส่วนเกิน (% ต่อปี)"]
    for i, lab in enumerate(labels):
        s.label(f"A{6 + i}", lab)
    for col, name, fee, hur, js in cols:
        s.label(f"{col}5", name, head=True)
        s.inp(f"{col}6", m["BTC"]["spot"], "#,##0")
        s.inp(f"{col}7", m["BTC"]["futures"], "#,##0")
        s.inp(f"{col}8", m["BTC"]["วันถึงหมดอายุ"])
        s.inp(f"{col}9", m["ทุนภาค1"]["รวม"], "#,##0")
        s.inp(f"{col}10", fee if fee != 0.05 else m["ค่าธรรมเนียม"]["taker"], "0.00")
        s.inp(f"{col}11", hur if hur != 4 else m["hurdle"], "0.00")
        s.inp(f"{col}12", m["BTC"]["ราคาชำระ"], "#,##0")
        c = col
        s.f(f"{c}13", f"={c}7-{c}6", js=js + ".basis", fmt="#,##0")
        s.f(f"{c}14", f"={c}13/{c}6*365/{c}8*100", js=js + ".บนจอ", fmt="0.00", key=True)
        s.f(f"{c}15", f"={c}13/{c}9*365/{c}8*100", js=js + ".ต่อทุน", fmt="0.00", key=True)
        s.f(f"{c}16", f"={c}10/100*({c}6+{c}7+{c}12)", js=js + ".ค่าธรรมเนียม", fmt="#,##0.00")
        s.f(f"{c}17", f"={c}13-{c}16", js=js + ".สุทธิ", fmt="#,##0.00")
        s.f(f"{c}18", f"={c}17/{c}9*365/{c}8*100", js=js + ".หลังค่าธรรมเนียม", fmt="0.00", key=True)
        s.f(f"{c}19", f"={c}9*{c}11/100*{c}8/365", js=js + ".ค่าเสียโอกาส", fmt="#,##0.00")
        s.f(f"{c}20", f"={c}17-{c}19", js=js + ".ส่วนเกิน", fmt="#,##0.00")
        s.f(f"{c}21", f"={c}20/{c}9*365/{c}8*100", js=js + ".ส่วนเกินเปอร์เซ็นต์", fmt="0.00", key=True)
    # บันไดแย่ง
    s.label("F5", "บันไดแย่ง: basis หดเมื่อคนแห่มา (ใช้ค่าคอลัมน์ B)", head=True)
    s.label("F6", "basis", head=True)
    s.label("G6", "① บนจอ", head=True)
    s.label("H6", "③ หลังค่าธรรมเนียม", head=True)
    s.label("I6", "④ ส่วนเกิน", head=True)
    s.ws.column_dimensions["I"].width = 14
    for i, row in enumerate(fig["ch05"]["บันไดแย่ง"]):
        r = 7 + i
        s.inp(f"F{r}", row["basis"], "#,##0")
        k = "365/$B$8*100"
        net = f"(F{r}-$B$10/100*($B$6+($B$6+F{r})+$B$12))"
        s.f(f"G{r}", f"=F{r}/$B$6*{k}", js=f"ch05.บันไดแย่ง.{i}.บนจอ", fmt="0.00")
        s.f(f"H{r}", f"={net}/$B$9*{k}", js=f"ch05.บันไดแย่ง.{i}.หลังค่าธรรมเนียม", fmt="0.00")
        s.f(f"I{r}", f"=({net}-$B$19)/$B$9*{k}", js=f"ch05.บันไดแย่ง.{i}.ส่วนเกินเปอร์เซ็นต์", fmt="0.00")
    # ทุนกับส่วนเกิน
    s.label("F15", "ทุนมากขึ้น = กันชนหนาขึ้น แต่ส่วนเกินบางลง", head=True)
    s.label("F16", "ทุน", head=True)
    s.label("G16", "③ หลังค่าธรรมเนียม", head=True)
    s.label("H16", "④ ส่วนเกิน", head=True)
    for i, row in enumerate(fig["ch05"]["ทุนกับกันชน"]):
        r = 17 + i
        s.inp(f"F{r}", row["ทุน"], "#,##0")
        s.f(f"G{r}", f"=$B$17/F{r}*365/$B$8*100", js=f"ch05.ทุนกับกันชน.{i}.หลังค่าธรรมเนียม", fmt="0.00")
        s.f(f"H{r}", f"=($B$17-F{r}*$B$11/100*$B$8/365)/F{r}*365/$B$8*100",
            js=f"ch05.ทุนกับกันชน.{i}.ส่วนเกินเปอร์เซ็นต์", fmt="0.00")
    # ปิดหรือถือวันที่ N (บท 6)
    d30 = fig["ch06"]["วันที่30"]
    s.label("A24", "ปิดหรือถือวันที่ N (บท 6 · ใช้ทุน/ค่าธรรมเนียม/วันของคอลัมน์ B)", head=True)
    s.label("B24", "hurdle หลัก", head=True)
    s.label("C24", "hurdle ทางเลือก", head=True)
    lab2 = ["วันที่ตัดสิน", "spot วันนั้น", "futures วันนั้น", "hurdle ต่อปี (%)", "basis ที่เหลือ", "ค่าธรรมเนียมถ้าปิดตอนนี้",
            "ค่าธรรมเนียม spot ถ้าถือถึงวันหมดอายุ", "ถือต่อได้เพิ่ม", "วันที่เหลือ", "ค่าเสียโอกาสของวันที่เหลือ", "ตัดสิน",
            "จุดเปลี่ยน hurdle (%)"]
    for i, lab in enumerate(lab2):
        s.label(f"A{25 + i}", lab)
    for col, hur, jsopp, jsdec in (("B", m["hurdle"], "ch06.วันที่30.เสียโอกาส60วัน", "ch06.วันที่30.ตัดสินที่hurdle4"),
                                   ("C", d30["hurdleทางเลือก"], "ch06.วันที่30.เสียโอกาสที่hurdle2", "ch06.วันที่30.ตัดสินที่hurdle2")):
        c = col
        s.inp(f"{c}25", 30)
        s.inp(f"{c}26", d30["spot"], "#,##0")
        s.inp(f"{c}27", d30["futures"], "#,##0")
        s.inp(f"{c}28", hur, "0.00")
        main = c == "B"
        s.f(f"{c}29", f"={c}27-{c}26", js="ch06.วันที่30.basis", fmt="#,##0")
        s.f(f"{c}30", f"=$B$10/100*({c}26+{c}27)", js="ch06.วันที่30.ค่าธรรมเนียมปิดตอนนี้", fmt="#,##0.00")
        s.f(f"{c}31", f"=$B$10/100*{c}26", js="ch06.วันที่30.ค่าธรรมเนียมspotถ้าถือ", fmt="#,##0.00")
        s.f(f"{c}32", f"={c}29-{c}31+{c}30", js="ch06.วันที่30.ถือได้เพิ่ม", fmt="#,##0.00", key=True)
        s.f(f"{c}33", f"=$B$8-{c}25", py=60, fmt="0")
        s.f(f"{c}34", f"=$B$9*{c}28/100*{c}33/365", js=jsopp, fmt="#,##0.00", key=True)
        s.f(f"{c}35", f'=IF({c}34>{c}32,"ปิด","ถือ")', js=jsdec, fmt=None, key=True)
        s.f(f"{c}36", f"={c}32/($B$9*{c}33/365)*100", js="ch06.วันที่30.จุดเปลี่ยนhurdle" if main else None,
            py=None if main else d30["จุดเปลี่ยนhurdle"], fmt="0.00")
    return s


# ───────────────────────── แท็บ 7: funding หลายเส้นทาง ─────────────────────────

def funding_rates(fig):
    """อัตราต่อรอบ (%) ของสี่เส้นทาง ถอดจากกราฟสะสมใน JSON (ดอลลาร์ต่อ 1 BTC ที่ราคา mark)"""
    mark = fig["บัญชีมิน"]["BTC"]["spot"]
    out = {}
    for name, cum in fig["ch07"]["กราฟ"].items():
        prev, rates = 0.0, []
        for c in cum:
            rates.append(round((c - prev) / mark * 100, 6))
            prev = c
        out[name] = rates
    return out


def funding_py(rates, mark, cap, days, fee_total, k):
    tot = sum(r / 100 * mark for r in rates)
    neg, rc, held = 0, 0.0, True
    for r in rates:
        if held:
            rc += mark * r / 100
            neg = neg + 1 if r < 0 else 0
            if k > 0 and neg >= k:
                held = False
    return {"tot": tot, "net": tot - fee_total, "pct": (tot - fee_total) / cap * 365 / days * 100,
            "rule": rc, "rule_net": rc - fee_total, "exited": not held}


def tab_funding(wb, checks, fig):
    m = fig["บัญชีมิน"]
    k7 = fig["ch07"]
    s = Sheet(wb, checks, fig, "funding หลายเส้นทาง", "funding หลายเส้นทาง — 30 วัน 90 รอบ · กฎ \"ติดลบ k รอบติดแล้วออก\" (บท 7 · ใบ 07)",
              ["ค่าธรรมเนียม: taker %s%% · maker %s%% · เปิดและปิดสองขา = 4 ครั้ง · funding รอบละ %s ชั่วโมงในตัวอย่างนี้ · 🔢 ตัวเลขสมมติเพื่อสอน" %
               (m["ค่าธรรมเนียม"]["taker"], m["ค่าธรรมเนียม"]["maker"], m["funding"]["ชั่วโมงต่อรอบในตัวอย่าง"]),
               "short perp รับ funding เมื่ออัตราเป็นบวก · คอลัมน์ 'ของฉัน' ว่างไว้ให้จดอัตราจริงรายรอบ 📱 · ช่องว่างนับเป็น 0"],
              widths={"A": 36, "B": 13, "C": 13, "D": 13, "E": 13, "F": 13})
    ws = s.ws
    rates = funding_rates(fig)
    names = ["ราบ", "พุ่งแล้วแผ่ว", "กลับขั้ว", "สลับ"]
    s.label("A5", "ค่าที่ใส่", head=True)
    s.label("B5", "ค่า", head=True)
    ins = [("ราคา mark (ตรึงตลอด 30 วัน)", m["BTC"]["spot"]), ("ทุน", m["ทุนภาค1"]["รวม"]), ("จำนวนวัน", 30),
           ("ค่าธรรมเนียม maker (%)", m["ค่าธรรมเนียม"]["maker"]), ("ค่าธรรมเนียม taker (%)", m["ค่าธรรมเนียม"]["taker"]),
           ("จำนวนครั้งที่เสียค่าธรรมเนียม", 4), ("กฎออก: ติดลบกี่รอบติด (0 = ไม่ใช้กฎ)", 3), ("hurdle ต่อปี (%)", m["hurdle"]),
           ("ชั่วโมงต่อรอบ (ในตัวอย่างนี้)", m["funding"]["ชั่วโมงต่อรอบในตัวอย่าง"])]
    for i, (lab, v) in enumerate(ins):
        s.label(f"A{6 + i}", lab)
        s.inp(f"B{6 + i}", v)
    MARK, CAP, DAYS, FM, FT, LEGS, K, HUR, HRS = (f"$B${6 + i}" for i in range(9))
    s.label("A16", "ค่าธรรมเนียมเปิดปิดรวม maker")
    s.f("B16", f"={FM}/100*{LEGS}*{MARK}", js="ch07.ค่าธรรมเนียมเปิดปิด.maker", fmt="#,##0")
    s.label("A17", "ค่าธรรมเนียมเปิดปิดรวม taker")
    s.f("B17", f"={FT}/100*{LEGS}*{MARK}", js="ch07.ค่าธรรมเนียมเปิดปิด.taker", fmt="#,##0")

    r0, n = 42, 90
    r1 = r0 + n - 1
    paths = names + ["ของฉัน"]
    s.label(f"A{r0 - 1}", "รอบ", head=True)
    for j, nm in enumerate(paths):
        s.label(f"{L(2 + j)}{r0 - 1}", f"{nm} (% ต่อรอบ)", head=True)
    # คอลัมน์ช่วย: H.. (ต่อเส้นทาง 3 คอลัมน์: ถือก่อน · ติดลบสะสม · funding ตามกฎ)
    helper0 = 8
    for j, nm in enumerate(paths):
        base = helper0 + 3 * j
        for t, hd in enumerate(["ยังถือ", "ติดลบติดกัน", "funding ตามกฎ"]):
            s.label(f"{L(base + t)}{r0 - 1}", f"{nm}: {hd}", head=True)
            ws.column_dimensions[L(base + t)].width = 11
    for i in range(n):
        r = r0 + i
        ws[f"A{r}"] = i + 1
        for j, nm in enumerate(paths):
            col = L(2 + j)
            if nm in rates:
                s.inp(f"{col}{r}", rates[nm][i], "0.0000")
            else:
                ws[f"{col}{r}"].fill = FILL_IN
            base = helper0 + 3 * j
            hc, nc, fc = L(base), L(base + 1), L(base + 2)
            if i == 0:
                ws[f"{hc}{r}"] = 1
                prev_n = 0
            else:
                ws[f"{hc}{r}"] = f"=IF(AND({hc}{r - 1}=1,OR({K}=0,{nc}{r - 1}<{K})),1,0)"
                prev_n = f"{nc}{r - 1}"
            ws[f"{nc}{r}"] = f"=IF({hc}{r}=1,IF(N({col}{r})<0,{prev_n}+1,0),{prev_n})"
            ws[f"{fc}{r}"] = f"=IF({hc}{r}=1,N({col}{r})/100*{MARK},0)"
            ws[f"{fc}{r}"].number_format = "0.00"
    # ── สรุปต่อเส้นทาง ──
    s.label("A20", "ผลต่อเส้นทาง", head=True)
    for j, nm in enumerate(paths):
        s.label(f"{L(2 + j)}20", nm, head=True)
    rows_lab = ["funding รวม 90 รอบ", "สุทธิ maker", "สุทธิ maker (% ต่อปี)", "funding ตามกฎ", "สุทธิตามกฎ maker",
                "ออกตามกฎ? (1 = ออก)", "สุทธิ taker", "สุทธิ taker (% ต่อปี)", "สุทธิตามกฎ taker",
                "① บนจอ (% ต่อปี ของอัตรารอบแรก)", "② ต่อทุน (% ต่อปี)", "③ หลังค่าธรรมเนียม maker (% ต่อปี)",
                "④ ส่วนเกินหลัง hurdle (% ต่อปี)"]
    for i, lab in enumerate(rows_lab):
        s.label(f"A{21 + i}", lab)
    mark, cap, days = m["BTC"]["spot"], m["ทุนภาค1"]["รวม"], 30
    for j, nm in enumerate(paths):
        col = L(2 + j)
        rr = f"{col}{r0}:{col}{r1}"
        base = helper0 + 3 * j
        hc, fc = L(base), L(base + 2)
        js = f"ch07.สี่เส้นทาง.{nm}" if nm in rates else None
        rt = rates.get(nm, [0.0] * n)
        pm = funding_py(rt, mark, cap, days, 80, 3)
        pt = funding_py(rt, mark, cap, days, 200, 3)
        g = lambda key: (js + "." + key) if js else None  # noqa: E731
        s.f(f"{col}21", f"=SUM({rr})/100*{MARK}", py=pm["tot"], js=g("fundingรวม"), fmt="#,##0.00")
        s.f(f"{col}22", f"={col}21-$B$16", py=pm["net"], js=g("สุทธิmaker"), fmt="#,##0.00", key=True)
        s.f(f"{col}23", f"={col}22/{CAP}*365/{DAYS}*100", py=pm["pct"], js=g("สุทธิmakerเปอร์เซ็นต์"), fmt="0.00")
        s.f(f"{col}24", f"=SUM({fc}{r0}:{fc}{r1})", py=pm["rule"], js=g("fundingตามกฎ"), fmt="#,##0.00")
        s.f(f"{col}25", f"={col}24-$B$16", py=pm["rule_net"], js=g("กฎmaker"), fmt="#,##0.00", key=True)
        s.f(f"{col}26", f"=IF(OR(MIN({hc}{r0}:{hc}{r1})=0,AND({K}>0,{L(base + 1)}{r1}>={K})),1,0)",
            py=1 if pm["exited"] else 0, fmt="0")
        s.f(f"{col}27", f"={col}21-$B$17", py=pt["net"], js=g("สุทธิtaker"), fmt="#,##0.00")
        s.f(f"{col}28", f"={col}27/{CAP}*365/{DAYS}*100", py=pt["pct"], js=g("สุทธิtakerเปอร์เซ็นต์"), fmt="0.00")
        s.f(f"{col}29", f"={col}24-$B$17", py=pt["rule_net"], js=g("กฎtaker"), fmt="#,##0.00")
        flat = nm == "ราบ"
        r_first = rt[0]
        s.f(f"{col}30", f"=N({col}{r0})*24/{HRS}*365", py=r_first * 3 * 365,
            js="ch07.บันไดfunding.บนจอ" if flat else None, fmt="0.00")
        s.f(f"{col}31", f"={col}21/{CAP}*365/{DAYS}*100", py=pm["tot"] / cap * 365 / days * 100,
            js="ch07.บันไดfunding.ต่อทุน" if flat else None, fmt="0.00")
        s.f(f"{col}32", f"={col}23", py=pm["pct"], js="ch07.บันไดfunding.หลังค่าธรรมเนียม" if flat else None, fmt="0.00")
        exc = (pm["net"] - cap * 0.04 * days / 365) / cap * 365 / days * 100
        s.f(f"{col}33", f"=({col}22-{CAP}*{HUR}/100*{DAYS}/365)/{CAP}*365/{DAYS}*100", py=exc,
            js="ch07.บันไดfunding.ส่วนเกินเปอร์เซ็นต์" if flat else None, fmt="0.00", key=flat)
    # อัตราถูกแย่ง (เส้นทางราบที่อัตราต่ำลง)
    s.label("A35", "อัตราถูกแย่ง: เส้นทางราบที่อัตราต่อรอบ (%)", head=True)
    s.label("B35", "taker (% ต่อปี)", head=True)
    s.label("C35", "maker (% ต่อปี)", head=True)
    for i, row in enumerate(k7["fundingถูกแย่ง"]):
        r = 36 + i
        s.inp(f"A{r}", row["ต่อรอบเปอร์เซ็นต์"], "0.000")
        s.f(f"B{r}", f"=(A{r}/100*{MARK}*90-$B$17)/{CAP}*365/{DAYS}*100", js=f"ch07.fundingถูกแย่ง.{i}.สุทธิtakerเปอร์เซ็นต์", fmt="0.00")
        s.f(f"C{r}", f"=(A{r}/100*{MARK}*90-$B$16)/{CAP}*365/{DAYS}*100", js=f"ch07.fundingถูกแย่ง.{i}.สุทธิmakerเปอร์เซ็นต์", fmt="0.00")
    ws.freeze_panes = f"B{r0}"
    return s


# ───────────────────────── แท็บ 8: ตาราง φ ─────────────────────────

def tab_phi(wb, checks, fig):
    k13 = fig["ch13"]
    g = k13["กติกาตารางphi"]
    s = Sheet(wb, checks, fig, "ตาราง φ", "ตาราง φ — ทุกช่วงเหลือระยะห่างกี่ส่วน แล้วถือ 4 ช่วงได้เท่าไร (บท 13 · ใบ 13)",
              ["φ = สัดส่วนของระยะห่างที่เหลือหลังผ่านไปหนึ่งช่วง (ไม่มีสัญญาณรบกวน = เส้นทางที่คาด) · ครึ่งชีวิต = จำนวนช่วงจนระยะเหลือครึ่ง (มีเฉพาะ φ < 1)",
               "🔢 ตัวเลขสมมติเพื่อสอน · คอลัมน์ F 'ของฉัน' ใส่ φ ที่คุณประมาณได้ (เช่นจากแท็บวิเคราะห์คู่)"],
              widths={"A": 38, "B": 13, "C": 13, "D": 13, "E": 13, "F": 13, "G": 4, "H": 18, "I": 14, "J": 4, "K": 18, "L": 14})
    s.label("A5", "กติกา", head=True)
    s.label("B5", "ค่า", head=True)
    for i, (lab, v) in enumerate([("ระยะเริ่ม (X ตอนเข้า)", g["เริ่ม"]), ("ถือกี่ช่วง", g["ช่วงถือ"]),
                                  ("จำนวนชุด", g["ชุด"]), ("ต้นทุนไปกลับ", g["ต้นทุน"])]):
        s.label(f"A{6 + i}", lab)
        s.inp(f"B{6 + i}", v)
    keys = ["0.80", "0.99", "1.00", "1.02"]
    s.label("A11", "φ", head=True)
    for j, kk in enumerate(keys + ["ของฉัน"]):
        col = L(2 + j)
        s.label(f"{col}11", kk, head=True)
        if kk == "ของฉัน":
            s.inp(f"{col}12", 0.9, "0.00")
        else:
            s.inp(f"{col}12", k13["ตารางphi"][kk]["phi"], "0.00")
    s.label("A12", "φ ที่ใช้")
    for t in range(5):
        s.label(f"A{13 + t}", f"ระยะหลัง {t} ช่วง")
    s.label("A18", "ระยะเมื่อครบช่วงถือ")
    s.label("A19", "กำไรก่อนต้นทุน")
    s.label("A20", "สุทธิหลังต้นทุน")
    s.label("A21", "ครึ่งชีวิต (ช่วง)")
    for j, kk in enumerate(keys + ["ของฉัน"]):
        col = L(2 + j)
        phi = 0.9 if kk == "ของฉัน" else k13["ตารางphi"][kk]["phi"]
        js = None if kk == "ของฉัน" else f"ch13.ตารางphi.{kk}"
        for t in range(5):
            s.f(f"{col}{13 + t}", f"=$B$6*{col}$12^{t}", py=2 * phi ** t, js=f"{js}.ระดับ.{t}" if js else None, fmt="0.0000")
        end = 2 * phi ** 4
        s.f(f"{col}18", f"=$B$6*{col}12^$B$7", py=end, fmt="0.0000")
        s.f(f"{col}19", f"=$B$8*($B$6-{col}18)", py=10 * (2 - end), js=f"{js}.กำไรก่อนต้นทุน" if js else None, fmt="0.00")
        s.f(f"{col}20", f"={col}19-$B$9", py=10 * (2 - end) - 1, js=f"{js}.สุทธิ4ช่วง" if js else None, fmt="0.00", key=True)
        hl = math.log(0.5) / math.log(phi) if 0 < phi < 1 else "ไม่มี"
        s.f(f"{col}21", f'=IF(AND({col}12>0,{col}12<1),LN(0.5)/LN({col}12),"ไม่มี")', py=hl,
            js=(f"{js}.ครึ่งชีวิต" if js and isinstance(hl, float) else None), fmt="0.00")
    # ครึ่งชีวิต → φ
    s.label("H5", "ครึ่งชีวิต → φ", head=True)
    s.label("I5", "φ", head=True)
    for i, row in enumerate(k13["ครึ่งชีวิตเป็นphi"]):
        r = 6 + i
        s.inp(f"H{r}", row["ครึ่งชีวิต"])
        s.f(f"I{r}", f"=0.5^(1/H{r})", js=f"ch13.ครึ่งชีวิตเป็นphi.{i}.phi", fmt="0.000")
    # φ → ครึ่งชีวิต
    s.label("K5", "φ → ครึ่งชีวิต", head=True)
    s.label("L5", "ครึ่งชีวิต", head=True)
    for i, row in enumerate(k13["phiเป็นครึ่งชีวิต"]):
        r = 6 + i
        s.inp(f"K{r}", row["phi"], "0.000")
        s.f(f"L{r}", f"=LN(0.5)/LN(K{r})", js=f"ch13.phiเป็นครึ่งชีวิต.{i}.ครึ่งชีวิต", fmt="0.0")
    # นับมือ: เวลาจาก ≥ 2 ถึง ≤ 1
    s.label("A24", "หา φ ด้วยการนับมือ (ใบ 13)", head=True)
    s.label("B24", "ค่า", head=True)
    s.label("A25", "จดจำนวนวันจาก X ≥ 2 จนถึง X ≤ 1 ทีละครั้ง ลงช่องสีเหลือง B30 ลงไป (จดได้ 30 ครั้ง)")
    s.label("A26", "มัธยฐานของวันที่นับได้")
    s.f("B26", '=IF(COUNT(B30:B59)=0,"",MEDIAN(B30:B59))', fmt="0.0")
    s.label("A27", "φ โดยประมาณ (ระยะลดครึ่งในเวลามัธยฐาน)")
    s.f("B27", '=IF(B26="","",0.5^(1/B26))', fmt="0.00")
    s.label("A28", "เทียบ: φ จากแท็บวิเคราะห์คู่ (ช่วงเลือก)")
    s.f("B28", "='วิเคราะห์คู่'!G14", fmt="0.00")
    s.label("A29", "คำเตือน: สัญญาณรบกวนทำให้แตะ 1 เร็วกว่าครึ่งชีวิตจริง — φ จากการนับมือมักต่ำเกินจริง (บท 13)")
    s.ws["A29"].font = NOTE
    for r in range(30, 60):
        s.ws[f"B{r}"].fill = FILL_IN
    return s


# ───────────────────────── ประกอบ + ตรวจ ─────────────────────────

def build(path):
    fig = load_fig()
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    checks = []
    tab_pair(wb, checks, fig)
    tab_beta(wb, checks, fig)
    tab_cost(wb, checks, fig)
    tab_ledger(wb, checks, fig)
    tab_buffer(wb, checks, fig)
    tab_ladder(wb, checks, fig)
    tab_funding(wb, checks, fig)
    tab_phi(wb, checks, fig)
    wb.properties.title = f"{B.BOOK} · เล่ม 1 — สมุดงาน"
    wb.properties.creator = "tools/sab_workbook.py"
    # เวลาคงที่ → ไฟล์ซ้ำได้ (ไม่เปลี่ยนทุกครั้งที่รัน)
    import datetime
    fixed = datetime.datetime(2026, 1, 1)
    wb.properties.created = fixed
    wb.properties.modified = fixed
    wb.save(path)
    return checks


def _decimals(v):
    if isinstance(v, int):
        return 0
    t = repr(float(v))
    return len(t.split(".")[1]) if "." in t and "e" not in t else 2


def compare(got, kind, want):
    if isinstance(want, str) or isinstance(got, str):
        return str(got) == str(want)
    if got is None:
        return False
    if kind == "json":
        return abs(round(got, _decimals(want)) - want) <= TOL + 1e-9
    return abs(got - want) <= TOL


def recalc(src, tmpdir):
    outdir = os.path.join(tmpdir, "out")
    os.makedirs(outdir, exist_ok=True)
    env = dict(os.environ, HOME=tmpdir)   # โปรไฟล์ LibreOffice แยก ไม่ชนกับ soffice ตัวอื่น
    r = subprocess.run(["soffice", "--headless", "--norestore", "--convert-to", "xlsx", "--outdir", outdir, src],
                       capture_output=True, text=True, timeout=300, env=env)
    out = os.path.join(outdir, os.path.basename(src))
    if not os.path.exists(out):
        raise SystemExit(f"soffice แปลงไม่สำเร็จ: {r.stdout} {r.stderr}")
    return openpyxl.load_workbook(out, data_only=True)


def check():
    tmp = tempfile.mkdtemp(prefix="sab_wb_")
    try:
        fresh = os.path.join(tmp, "sab-workbook.xlsx")
        checks = build(fresh)
        problems = []
        # ไฟล์ใน docs ต้องเป็นผลล่าสุดของสคริปต์ (เทียบสูตร/ค่าทุกเซลล์)
        if not os.path.exists(OUT):
            problems.append(f"ยังไม่มี {os.path.relpath(OUT, B.ROOT)} — รัน python3 tools/sab_workbook.py")
        else:
            a, b = openpyxl.load_workbook(OUT), openpyxl.load_workbook(fresh)
            if a.sheetnames != b.sheetnames:
                problems.append(f"แท็บใน docs ไม่ตรง: {a.sheetnames} ≠ {b.sheetnames}")
            else:
                for name in a.sheetnames:
                    va = {c.coordinate: c.value for row in a[name].iter_rows() for c in row if c.value is not None}
                    vb = {c.coordinate: c.value for row in b[name].iter_rows() for c in row if c.value is not None}
                    if va != vb:
                        diff = sorted(set(va.items()) ^ set(vb.items()))[:3]
                        problems.append(f"docs/sab-workbook.xlsx แท็บ {name} ไม่ตรงกับสคริปต์ (รันใหม่) เช่น {diff}")
        wb = recalc(OUT if os.path.exists(OUT) else fresh, tmp)
        n_json = n_py = 0
        for sheet, cell, kind, want, js in checks:
            got = wb[sheet][cell].value
            if not compare(got, kind, want):
                problems.append(f"{sheet}!{cell}: ได้ {got!r} แต่{'JSON ' + js if kind == 'json' else 'Python'} = {want!r}")
            if kind == "json":
                n_json += 1
            else:
                n_py += 1
        # สูตรต้องไม่มี error ทุกเซลล์
        errs = []
        for ws in wb:
            for row in ws.iter_rows():
                for c in row:
                    v = c.value
                    if isinstance(v, str) and (v.startswith("Err:") or (v.startswith("#") and any(
                            x in v.upper() for x in ("DIV", "VALUE", "REF", "NAME", "N/A", "NUM", "NULL")))):
                        errs.append(f"{ws.title}!{c.coordinate}={c.value}")
        problems += [f"เซลล์ error: {e}" for e in errs[:20]]
        for p in problems:
            print("✗", p)
        tabs = ", ".join(wb.sheetnames)
        print(f"แท็บ {len(wb.sheetnames)}: {tabs}")
        print(f"เทียบ {n_json} เซลล์กับ JSON · {n_py} เซลล์กับ Python คู่ · error {len(errs)} เซลล์")
        print("ผ่าน ✓" if not problems else f"ไม่ผ่าน ✗ ({len(problems)} ปัญหา)")
        return 0 if not problems else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    if "--check" in sys.argv:
        sys.exit(check())
    checks = build(OUT)
    print(f"เขียน {os.path.relpath(OUT, B.ROOT)} · 8 แท็บ · เซลล์ที่มีคู่ตรวจ {len(checks)} เซลล์ (ตรวจด้วย --check)")


if __name__ == "__main__":
    main()
