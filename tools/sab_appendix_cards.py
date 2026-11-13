"""สร้างตารางในภาคผนวก (รันจากรากคลัง) — ย้ายจาก scratchpad ของผู้เขียนภาคผนวก ให้รันซ้ำได้เมื่อคัมภีร์/JSON เปลี่ยน"""
"""สร้างตารางบัตรสี่ใบของ docs/sab-appendix-card.html จาก tools/sab_bible.json คีย์ บัตร
เขียนทับระหว่าง <!--CARDS:begin--> และ <!--CARDS:end--> · รันซ้ำได้เมื่อคัมภีร์เปลี่ยน แล้วตามด้วย
python3 tools/sab_charts.py --fill --scope appendix-card"""
import json, sys, html, re, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import sab_book as B
fig = json.load(open('docs/sab-figures.json', encoding='utf-8'))
bible = json.load(open('tools/sab_bible.json', encoding='utf-8'))['บัตร']
order = sorted([k for k in bible if not k.startswith('_')], key=lambda k: int(k.split()[0]))
SLOTS = "①②③④⑤⑥⑦⑧"
NAMES = ["กำไรจากอะไร", "ใครจ่าย / เมื่อไรเป็นคนรู้", "ถืออะไรจริง", "รูปร่าง (แถบผล)", "ทุน / กันชน",
         "ต้องเป็นจริง / เลิกเชื่อ", "ตายอย่างไร", "อุบัติเหตุหน้างาน"]
# บัตรใบ 4 (ร่าง · แผน 5.3): เล่มสอนแค่ตัวอย่างขาเดียวของบท 1 — ช่องที่เล่มไม่สอนเป็นเทา
CARD4 = {
    "①": [(1, "ch01.ได้ขาเดียว.ได้สองฝั่ง", "ให้สภาพคล่อง: ได้สองฝั่งรอบละ 0.2 (ส่วนต่างราคาซื้อ-ขาย)")],
    "②": [(1, None, "คนที่กดซื้อขายทันที (สมมติฐาน) · เป็นคนรู้เมื่อราคาวิ่งทางเดียว")],
    "④": [(1, "ch01.ได้ขาเดียว.ได้ขาเดียว", "ได้เล็กบ่อย · ได้ขาเดียวตอนราคาลงเสีย −0.4")],
}
def entry(ch, key, txt):
    t = html.escape(txt)
    if key:
        v = B.fmt(B.get_path(fig, key))
        for cand in (v, v.lstrip('−')):
            if cand in t:
                t = t.replace(cand, f'<span data-key="{key}">{cand}</span>', 1)
                break
        else:
            t += f': <span data-key="{key}">{v}</span>'
    return f'<div>{t} <span class="ch">บท {ch}</span></div>'
rows = ['<tr><th>ช่อง</th>' + ''.join(f'<th>ใบ {k.split()[0]} · {html.escape(" ".join(k.split()[1:]))}</th>' for k in order)
        + '<th>ใบ 4 · ให้สภาพคล่อง (ร่าง)</th></tr>']
for i, s in enumerate(SLOTS):
    tds = [f'<td data-label="{i+1}" class="slot">{s} {NAMES[i]}</td>']
    for k in order:
        ent = bible[k].get(s, [])
        tds.append(f'<td data-label="{i+1}">' + ''.join(entry(*e) for e in ent) + '</td>' if ent
                   else f'<td data-label="{i+1}" class="na">—</td>')
    ent = CARD4.get(s)
    tds.append(f'<td data-label="{i+1}">' + ''.join(entry(*e) for e in ent) + '</td>' if ent
               else f'<td data-label="{i+1}" class="na">เล่ม 2</td>')
    rows.append('<tr>' + ''.join(tds) + '</tr>')
table = '<div class="tw"><table class="ncard c4">\n' + '\n'.join(rows) + '\n</table></div>'
path = 'docs/sab-appendix-card.html'
src = open(path, encoding='utf-8').read()
new = re.sub(r'(<!--CARDS:begin-->).*?(<!--CARDS:end-->)', lambda m: m.group(1) + '\n' + table + '\n' + m.group(2), src, flags=re.S)
if new == src and '<!--CARDS:begin-->' not in src:
    sys.exit('ไม่พบ marker CARDS')
open(path, 'w', encoding='utf-8').write(new)
print('เขียนบัตร', len(order) + 1, 'ใบ')
