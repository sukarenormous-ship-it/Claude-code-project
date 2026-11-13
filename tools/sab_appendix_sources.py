"""สร้างตารางในภาคผนวก (รันจากรากคลัง) — ย้ายจาก scratchpad ของผู้เขียนภาคผนวก ให้รันซ้ำได้เมื่อคัมภีร์/JSON เปลี่ยน"""
"""เติมตารางของ docs/sab-appendix-sources.html จาก docs/sab-figures.json และรายการอ้างอิงของต้นฉบับ
บล็อก: SEEDS · SEEDS3 · CLAIMS · ERRATA · REFS · OUTSIDE (ระหว่าง <!--X:begin--> และ <!--X:end-->)
รันซ้ำได้เมื่อ JSON เปลี่ยน (เช่น _claims ของบทใหม่) แล้วตามด้วย sab_charts.py --fill --scope appendix-sources"""
import json, re, sys, os, html
sys.path.insert(0, 'tools')
import sab_book as B
E = html.escape
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
fig = json.load(open('docs/sab-figures.json', encoding='utf-8'))
MD = os.path.join(os.environ.get('SAB_SOURCE_DIR', 'sources/sab-v0_9'), 'Stat_Arb_for_Non_Quant_Part_I_v0_9.md')
blocks = {}

# ── seed_robustness ──
NAMES = {
 'ch09': {'ในกรอบไม่มีเชือก': 'คู่ไม่มีเชือก: วันในกรอบ ±2 ช่วงทดสอบ (%)', 'ในกรอบมีเชือก': 'คู่มีเชือก: วันในกรอบ (%)',
          'คู่ที่เกิน3มีเชือก': 'คู่มีเชือกที่ช่วงทดสอบเกิน ±3 (%)', 'ทิศเดียวกันไม่มีเชือก': 'คู่ไม่มีเชือก: วันขยับทิศเดียวกัน (%)',
          'ทิศเดียวกันมีเชือก': 'คู่มีเชือก: วันขยับทิศเดียวกัน (%)',
          'corrไม่มีเชือก': 'correlation เฉลี่ย คู่ไม่มีเชือก', 'corrมีเชือก': 'correlation เฉลี่ย คู่มีเชือก', 'phiไม่มีเชือก': 'φ เฉลี่ย คู่ไม่มีเชือก'},
 'ch10': {'ระยะสูงสุดเฉลี่ย': '10 คู่ที่คัด: ระยะ z สูงสุดเฉลี่ยช่วงทดสอบ', 'ในกรอบ': '10 คู่ที่คัด: วันในกรอบ (%)',
          'ในกรอบคู่จริง': 'คู่มีเชือก: วันในกรอบ (%)', 'ระยะสูงสุดคู่จริง': 'คู่มีเชือก: ระยะ z สูงสุดเฉลี่ย',
          'ทั้ง200ในกรอบ': 'ทั้ง 200 คู่: วันในกรอบ (%)', 'ข้ามค่ากลาง10อันดับ': '10 อันดับแรก: ครั้งข้ามค่ากลางเฉลี่ย',
          'กรอบรั่วไม่มีเชือก': 'กรอบรั่ว: วันในกรอบของคู่ไม่มีเชือก (%)', 'เกณฑ์85ปล่อยคู่ปลอม': 'เกณฑ์ในกรอบ ≥ 85%: ปล่อยคู่ปลอม (%)',
          'เกณฑ์85ตัดคู่จริง': 'เกณฑ์ในกรอบ ≥ 85%: ตัดคู่จริง (%)'},
 'ch13': {'มัธยฐานแตะเป้า': 'φ 0.99: มัธยฐานช่วงจนแตะเป้า', 'แตะก่อนครึ่งชีวิต': 'φ 0.99: แตะเป้าก่อนครึ่งชีวิต (%)', 'ขึ้นถึง3ก่อน': 'φ 0.99: ขึ้นถึง 3 ก่อนแตะเป้า (%)'},
 'ch15': {'รวมสุทธิ': 'การ์ดบท 12 บนคู่อันดับ 1: รวมสุทธิ', 'จำนวนไม้': 'จำนวนไม้ก่อนหยุดเพราะงบ'},
 'ch17': {'ลึกสุด': 'drawdown ลึกสุด (100 ไม้)', 'นานสุดไม้': 'drawdown นานสุด (ไม้)', 'ผลรวม100ไม้': 'ผลรวม 100 ไม้'},
}
SEEDOF = {'ch09': 7, 'ch10': 11, 'ch13': 20261111, 'ch15': 11, 'ch17': 20261111}
rows, rows3 = [], []
sr = fig['seed_robustness']
for ch in ['ch09', 'ch10', 'ch13', 'ch15', 'ch17']:
    for k, v in sr[ch].items():
        if not (isinstance(v, dict) and 'มัธยฐาน' in v):
            continue
        cells = ''.join(f'<td data-key="seed_robustness.{ch}.{k}.{f}">{B.fmt(v[f])}</td>' for f in ('ตัวอย่าง', 'มัธยฐาน', 'ต่ำสุด', 'สูงสุด'))
        three = any(isinstance(v[f], float) and len(repr(abs(v[f])).split('.')[1]) > 2 for f in ('ตัวอย่าง', 'มัธยฐาน', 'ต่ำสุด', 'สูงสุด'))
        r = f'<tr><td class="nw"><a href="sab-part{int(ch[2:])}.html">บท {int(ch[2:])}</a></td><td>{E(NAMES[ch].get(k, k))}</td>{cells}</tr>'
        (rows3 if three else rows).append(r)
head = '<tr><th>บท</th><th>ค่า</th><th>ตัวอย่างในเล่ม</th><th>มัธยฐาน</th><th>ต่ำสุด</th><th>สูงสุด</th></tr>'
blocks['SEEDS'] = '<div class="tw"><table>\n' + head + '\n' + '\n'.join(rows) + '\n</table></div>'
blocks['SEEDS3'] = '<div class="tw"><table>\n' + head + '\n' + '\n'.join(rows3) + '\n</table></div>'

# ── _claims ──
LV = {'สมมติฐาน': 'สมมติฐาน', 'มีแหล่ง': 'มีแหล่ง (ยังไม่เปิดตรวจ)', 'ตัวอย่างสอน': 'ตัวอย่างสอน'}
cr = []
for c in fig['_claims']:
    chs = ' · '.join(f'<a href="sab-part{n}.html">{n}</a>' for n in c['บท'])
    src = E(c['แหล่ง']) if c.get('แหล่ง') else '—'
    cr.append(f'<tr><td class="nw"><code>{E(c["id"])}</code></td><td>{E(c["ข้อความ"])}</td><td class="nw">{E(LV.get(c["ระดับหลักฐาน"], c["ระดับหลักฐาน"]))}</td><td>{src}</td><td class="nw">{chs}</td></tr>')
blocks['CLAIMS'] = ('<div class="tw"><table class="small">\n<tr><th>id</th><th>ข้อความ</th><th>ระดับหลักฐาน</th><th>แหล่ง</th><th>บท</th></tr>\n'
                    + '\n'.join(cr) + '\n</table></div>')


# ── _errata ──
er = []
for e in fig['_errata']:
    ch = re.match(r'ch(\d+)', e['คีย์'])
    chs = f'<a href="sab-part{int(ch.group(1))}.html">บท {int(ch.group(1))}</a>' if ch else '—'
    er.append(f'<tr><td>{e["ข้อ"]}</td><td class="nw">{chs}</td><td>{E(e["แก้"])}</td><td><code>{E(e["คีย์"])}</code></td></tr>')
blocks['ERRATA'] = ('<div class="tw"><table class="small">\n<tr><th>ข้อ</th><th>บท</th><th>เล่มนี้ใช้</th><th>คีย์ใน JSON</th></tr>\n'
                    + '\n'.join(er) + '\n</table></div>')

# ── R1–R48 ──
md = open(MD, encoding='utf-8').read()
refsec = md[md.index('## แหล่งอ้างอิงและทางอ่านต่อ'):md.index('## ไฟล์ประกอบ Markdown')]
refs = re.findall(r'\*\*\[R(\d+)\]\*\*\s*(.+?)\n\s*\n<(https?://[^>]+)>', refsec)
assert len(refs) == 48, len(refs)
CASE = {1: 'C1', 3: 'C1', 4: 'C2', 5: 'C3', 11: 'C3 · C4', 6: 'C4', 7: 'C5', 8: 'C6', 9: 'C7', 20: 'C8', 10: 'C8', 30: 'C9',
        31: 'C10', 32: 'C10', 33: 'C11', 34: 'C11', 35: 'C11', 38: 'C12', 46: 'C12', 41: 'C13', 42: 'C13', 43: 'C13', 36: 'C14', 37: 'C14'}
WEB_V06 = {7, 9, 38}
NOT_CITED = {6, 9, 11}
IN_BOOK = {20: '<a href="sab-part5.html#deep-continuous">บท 5 🔎</a> (ข้ออ้าง <code>ch05-cme-basiswatch</code>)',
           23: '<a href="sab-part3.html#deep-settle">บท 3 🔎</a> (กลไกทั่วไป ไม่เอ่ยชื่อแหล่งในเนื้อ)'}
rr, nums = [], {}
for n, txt, url in refs:
    n = int(n)
    txt = txt.strip().rstrip('.')
    status = 'ฉบับ 0.6 เปิดตรวจจากเว็บได้' + (' (แก้ชื่อเอกสารแล้ว)' if n == 38 else '') + ' · รุ่นนี้ไม่ได้เปิดซ้ำ' if n in WEB_V06 else 'ยังไม่ได้เปิดตรวจจากเว็บ'
    cited = 'ไม่ถูกอ้างในต้นฉบับ' if n in NOT_CITED else ''
    use = IN_BOOK.get(n, '—')
    rr.append(f'<tr><td class="nw" id="r{n}">R{n}</td><td><a href="{E(url)}" rel="noopener">{E(txt)}</a></td><td class="nw">{CASE.get(n, "—")}</td>'
              f'<td>{status}{" · " + cited if cited else ""}</td><td>{use}</td></tr>')
    toks = re.findall(r'(?<![\w.])\d+(?:\.\d+)?', txt)
    toks = [t for t in toks if (('.' in t) or len(t) >= 3)]
    if toks:
        nums[f'R{n}'] = toks
blocks['REFS'] = ('<div class="tw"><table class="small">\n<tr><th>R</th><th>แหล่ง (ตามต้นฉบับ)</th><th>กรณี</th><th>สถานะการตรวจ</th><th>ใช้ในเล่มนี้</th></tr>\n'
                  + '\n'.join(rr) + '\n</table></div>')
refurls = {u.rstrip('/') for _, _, u in refs}
cases = md[md.index('## กรณีศึกษาที่ใช้เป็นแกนของเล่ม'):md.index('### แบบบันทึกที่ใช้กับทุกกรณี')]
out = []
for cm in re.finditer(r'### (C\d+) ([^\n]+)\n(.*?)(?=\n### |\Z)', cases, re.S):
    links = [u for u in re.findall(r'\]\((https?://[^)]+)\)', cm.group(3)) if u.rstrip('/') not in refurls]
    if links:
        lk = ' · '.join(f'<a href="{E(u)}" rel="noopener">{E(re.match(r"https?://([^/]+)", u).group(1))}</a>' for u in links)
        out.append(f'<li><strong>{cm.group(1)}</strong> {E(cm.group(2).strip())} — {lk}</li>')
blocks['OUTSIDE'] = '<ul class="small">\n' + '\n'.join(out) + '\n</ul>'

if '--nums' in sys.argv:
    print(json.dumps(nums, ensure_ascii=False))
    sys.exit()
path = 'docs/sab-appendix-sources.html'
src = open(path, encoding='utf-8').read()
for k, v in blocks.items():
    pat = re.compile(r'(<!--%s:begin-->).*?(<!--%s:end-->)' % (k, k), re.S)
    if not pat.search(src):
        print('ไม่มี marker', k); continue
    src = pat.sub(lambda m: m.group(1) + ('\n' + v + '\n' if '\n' in v or len(v) > 10 else v) + m.group(2), src)
open(path, 'w', encoding='utf-8').write(src)
print('เติม', ', '.join(blocks))
