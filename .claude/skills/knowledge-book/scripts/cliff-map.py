#!/usr/bin/env python3
"""แผนที่หน้าผา scaffolding: หาบล็อกโค้ดที่ 'ยาว/ยาก' แต่ไม่มีกล่องอธิบายติดอยู่

เกณฑ์ยาก = จำนวน construct ที่มือใหม่อ่านไม่ออกด้วยสายตา
"""
import html
import pathlib
import re
import sys
from collections import defaultdict

DOCS = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "docs")
TAG = re.compile(r"</?(?:span|br|div|a|strong|em|code|b|i|u|sub|sup)(?:\s[^>]*)?/?>", re.I)

# construct ที่ต้องอธิบาย (น้ำหนัก = ความยากสำหรับมือใหม่)
HARD = {
    r"\[[^\]]*\bfor\b[^\]]*\]": ("list comprehension", 3),
    r"\{[^}]*\bfor\b[^}]*\}": ("dict/set comprehension", 3),
    r"\blambda\b": ("lambda", 2),
    r"\.shift\(-?\d*\)": ("shift", 2),
    r"\.rolling\(": ("rolling", 2),
    r"\.cumsum\(|\.cumprod\(|\.cummax\(": ("cumulative", 2),
    r"\.diff\(\)": ("diff", 2),
    r"\.groupby\(": ("groupby", 3),
    r"\.apply\(": ("apply", 3),
    r"!=.*\.shift\(\)|\.shift\(\).*!=": ("การนับ trade ด้วย shift+cumsum", 4),
    r"\basync def\b": ("async def", 4),
    r"\bawait\b": ("await", 3),
    r"asyncio\.(gather|create_task|wait_for|Queue|Lock)": ("asyncio primitive", 4),
    r"\basync with\b|\basync for\b": ("async context/iter", 4),
    r"@(abstractmethod|property|classmethod|staticmethod|dataclass)": ("decorator", 3),
    r"super\(\)\.": ("super()", 3),
    r"\byield\b": ("generator", 3),
    r"\bcoint\(|adfuller\(|johansen": ("stat test", 3),
    r"RollingOLS|sm\.OLS": ("OLS", 2),
    r"minimize\(|linprog\(|LpProblem": ("optimizer", 3),
    r"np\.linalg\.|@ \w+|\.T\b": ("linear algebra", 3),
    r"\.loc\[|\.iloc\[": ("loc/iloc", 1),
    r"try:": ("exception handling", 2),
    r"\bself\.\w+\s*=": ("self assignment", 1),
}
HARD_C = [(re.compile(p), n, w) for p, (n, w) in HARD.items()]

# กล่องอธิบายที่นับว่า "มี scaffolding"
# ⚠️ ต้องนับกล่อง .bx ทุกสีด้วย — หนังสือใช้กล่องเตือน/กับดัก/สรุปเป็น
# scaffolding เหมือนกัน ถ้านับแค่ read-aloud/ai-decode จะรายงานว่า "ว่าง"
# ทั้งที่มีคำอธิบายดีอยู่แล้ว แล้วเราจะไปเติมกล่องซ้ำ
#
# ⚠️ เคยพลาดมาแล้ว: เขียน b[kabp] แบบระบุสี ทำให้กล่อง br (แดง = "bug ที่
# ซ่อนอยู่") · bg (เขียว = "แบบที่ถูก") · bd (เทา = สรุป) ไม่ถูกนับ
# → รายงานว่าบล็อกนั้นไม่มี scaffolding ทั้งที่อธิบายไว้ครบแล้ว
# ใช้ b\w+ ครอบทุกสีแทน แล้วไปตัดสินคุณภาพด้วยตาอีกที
SCAFF = re.compile(r'class="(read-aloud|ai-decode|ad-steps|bx b\w+)"')

rows = []
GLOB = sys.argv[2] if len(sys.argv) > 2 else "python-part*.html"
for path in sorted(DOCS.glob(GLOB)):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    for m in re.finditer(r'<div class="fm">(.*?)</div>', text, re.S):
        start = text[: m.start()].count("\n") + 1
        raw = m.group(1)
        code = html.unescape(TAG.sub("", raw))
        nlines = len([l for l in code.splitlines() if l.strip()])
        if nlines < 4:
            continue
        found = defaultdict(int)
        score = 0
        for rx, name, w in HARD_C:
            c = len(rx.findall(code))
            if c:
                found[name] += c
                score += w * min(c, 3)
        end = start + raw.count("\n")
        # มี scaffolding ก่อนถึง "บล็อกโค้ดถัดไป" หรือ "หัวข้อถัดไป" ไหม
        # (หน้าต่างตายตัวใช้ไม่ได้ เพราะ .output มักคั่นอยู่ระหว่างโค้ดกับคำอธิบาย)
        after = "\n".join(lines[end : end + 40])
        stop = re.search(r'<div class="fm">|<h[23][ >]', after)
        if stop:
            after = after[: stop.start()]

        # ⚠️ ต้องดู "ก่อนบล็อก" ด้วย — หนังสือใช้ทั้งสองแบบ:
        #   read-aloud วางไว้ก่อน (เตรียมสายตาก่อนเจอโค้ด)
        #   ai-decode วางไว้หลัง (แกะทีละบรรทัดหลังเห็นภาพรวม)
        # ถ้านับแค่ข้างหลัง บล็อกที่มี read-aloud นำหน้าจะถูกรายงานว่าว่าง
        #
        # ขอบเขตหน้าต่าง = นับถอยหลังจนชนของที่แปลว่า "คนละเรื่องแล้ว":
        # ท้ายบล็อกโค้ด/ผลลัพธ์ก่อนหน้า หรือหัวข้อก่อนหน้า — เอาอันที่ใกล้ที่สุด
        prefix = text[: m.start()]
        cut = 0
        for rx in (r'<div class="(?:fm|output)">', r"<h[23][ >]"):
            for mm in re.finditer(rx, prefix):
                if mm.start() > cut:
                    cut = mm.start()
        # ...แล้วตัดให้เหลือแค่ช่วงที่ "ติดกันจริง" (15 บรรทัดสุดท้าย) เพื่อไม่ให้
        # กล่องที่อธิบายบล็อกก่อนหน้าถูกนับมาเป็นของบล็อกนี้
        before = "\n".join(prefix[cut:].splitlines()[-15:])

        has = bool(SCAFF.search(after) or SCAFF.search(before))
        rows.append(
            dict(file=path.name, line=start, nlines=nlines, score=score,
                 has=has, why=", ".join(f"{k}×{v}" for k, v in
                                        sorted(found.items(), key=lambda x: -x[1])[:4]))
        )

print("═══ บล็อกที่ยาว/ยาก แต่ไม่มีกล่องอธิบายติดอยู่ (เรียงตามคะแนนความยาก) ═══\n")
per = defaultdict(list)
for r in rows:
    if not r["has"]:
        per[r["file"]].append(r)

for fn in sorted(per):
    tgt = sorted(per[fn], key=lambda r: -r["score"])
    tot = len([r for r in rows if r["file"] == fn])
    covered = len([r for r in rows if r["file"] == fn and r["has"]])
    print(f"── {fn}  (บล็อก≥4บรรทัด: {tot} · มี scaffolding แล้ว: {covered})")
    for r in tgt[:9]:
        print(f"   :{r['line']:<5} {r['nlines']:>3}บรรทัด  ยาก={r['score']:<3} {r['why']}")
    print()
