#!/usr/bin/env python3
"""สร้างหน้าเครื่องมือกดเล่นของ "Stat Arb for Non Quant · เล่ม 1" (แผน 6.2) ด้วยเปลือกเดียวกับบท (sab_book.page)

    python3 tools/sab_tools_build.py           # เขียน docs/sab-tool-{carry,funding,reversion,fakepair}.html + docs/sab-tools.html
                                               # (หน้าเหล่านี้สร้างจากสคริปต์ทั้งหน้า เขียนทับได้) แล้วเติม DATA จาก sab-figures.json
    python3 tools/sab_tools_build.py --check   # เปิดทุกหน้าใน Chromium (Playwright · ตัดเครือข่าย) แล้วเทียบตัวเลขที่ JS คิด
                                               # กับ sab-figures.json: ทุก [data-twin] ตอนเปิด + สถานการณ์ที่กดเปลี่ยนค่า

ค่าตั้งต้นทุกตัวมาจาก <!--DATA:key--> (sab_charts.py เติม <script type="application/json"> นอก JS) · JS อ่านด้วย JSON.parse
เครื่องมือที่สุ่มใช้ Math.random ของเบราว์เซอร์ (ไม่ port random ของ Python) — หน้าบอกชัดว่าเป็นตัวอย่างใหม่ และวางค่าในบทจาก JSON ไว้ข้างกัน
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sab_book as B  # noqa: E402

FIG_PATH = os.path.join(B.DOCS, "sab-figures.json")
PAGES = ["sab-tool-carry.html", "sab-tool-funding.html", "sab-tool-reversion.html", "sab-tool-fakepair.html",
         "sab-tools.html"]


def sid(key):
    """id ของ <script type="application/json"> ที่ sab_charts.py สร้างจาก DATA:key"""
    return "data-" + re.sub(r"[^\w-]", "-", key)


def fill_data(html, fig):
    try:
        import sab_charts
        out, unknown = sab_charts.process(html, fig)
    except Exception:          # ปลั๊กอินกราฟของบทอื่นพังระหว่างเขียน → ใช้ตรรกะเดียวกันตรงนี้
        unknown = []

        def sub(m):
            try:
                data = B.get_path(fig, m.group(3))
            except KeyError:
                unknown.append(m.group(3))
                return m.group(0)
            js = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
            return f'{m.group(1)}<script type="application/json" id="{sid(m.group(3))}">{js}</script>{m.group(5)}'
        out = re.sub(r"(<!--(DATA):([^>]+?)-->)(.*?)(<!--/\2:\3-->)", sub, html, flags=re.S)
    if unknown:
        raise SystemExit(f"DATA ไม่รู้จัก: {unknown}")
    return out


def data_block(keys):
    return "\n".join(f"<!--DATA:{k}--><!--/DATA:{k}-->" for k in keys)


def ids_js(keys):
    """const BOOK = {...} — อ่าน JSON ทุกก้อนของหน้า"""
    items = ",".join(f"{json.dumps(k, ensure_ascii=False)}:J({json.dumps(sid(k))})" for k in keys)
    return f"const BOOK={{{items}}};"


# ───────────────────────── ส่วนกลางของหน้าเครื่องมือ ─────────────────────────

CSS = """<style>
.tool{border:2px solid var(--blue);border-radius:12px;padding:16px 18px;margin:20px 0;background:#fbfdff}
.tool h3{margin-top:.4em}
.ctrl{display:grid;grid-template-columns:1fr auto;gap:8px 14px;align-items:center;margin:12px 0}
.ctrl label{font-size:.95em;color:var(--g7)}
.ctrl input[type=number],.ctrl select{width:9.5em;font:inherit;padding:3px 8px;border:1px solid #cbd5e1;border-radius:6px;text-align:right;background:#fff}
.ctrl input[type=range]{width:100%;grid-column:1/-1}
.ctrl .val{font-weight:700;color:var(--g9);font-variant-numeric:tabular-nums;text-align:right}
.seg{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0}
.seg button,.btn{font:inherit;font-size:.95em;border:2px solid var(--blue);background:#fff;color:var(--blue);border-radius:8px;padding:4px 12px;cursor:pointer}
.seg button.on,.btn.pri{background:var(--blue);color:#fff}
.btn{margin:4px 6px 4px 0}
.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.v{font-weight:700;font-variant-numeric:tabular-nums}
.bk{display:block;font-size:.76em;color:#64748b;font-weight:400;white-space:nowrap}
.big{font-size:1.7em;font-weight:800;color:var(--g9);font-variant-numeric:tabular-nums}
.src{font-size:.86em;color:#64748b;margin:4px 0 14px}
.pos{color:var(--green)}.neg{color:var(--red)}.key{color:var(--purple)}
.chart{display:block;width:100%;height:auto;margin:10px 0;touch-action:none}
.kpi{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:12px 0}
.kpi>div{background:#fff;border:1px solid var(--g2);border-radius:8px;padding:8px 12px}
.kpi .lb{font-size:.85em;color:var(--g7)}
textarea.path{width:100%;font:inherit;font-variant-numeric:tabular-nums;border:1px solid #cbd5e1;border-radius:6px;padding:6px 8px}
@media(max-width:640px){.ctrl{grid-template-columns:1fr}.ctrl .val{text-align:left}.tool{padding:12px 12px}}
</style>"""

# ตัวช่วย JS ที่ทุกหน้าใช้ (ไม่มีไลบรารีภายนอก)
JS_COMMON = r"""
const $=id=>document.getElementById(id);
const J=id=>JSON.parse($(id).textContent);
function nf(v,d){if(v===null||v===undefined||typeof v!=='number'||!isFinite(v))return '—';
  const r=Math.round(Math.abs(v)*Math.pow(10,d)+1e-9)/Math.pow(10,d);
  const s=r.toLocaleString('en-US',{minimumFractionDigits:d,maximumFractionDigits:d});
  return (v<0&&r!==0?'−':'')+s;}
function decs(v){const t=String(v);return (t.indexOf('.')>=0&&t.indexOf('e')<0)?t.split('.')[1].length:0;}
function fj(v){return typeof v==='number'?nf(v,decs(v)):(v===null||v===undefined?'—':String(v));}
function jp(path){return path.split('/').reduce((o,k)=>(o===null||o===undefined)?undefined:o[k],BOOK);}
function num(id){const v=parseFloat(String($(id).value).replace(/,/g,''));return isFinite(v)?v:0;}
function setv(id,v){$(id).value=v;}
// ค่าในบทข้างตัวเลขสด: ทุก [data-twin] ได้ป้ายเทา "บท …" ต่อท้าย
function twins(){document.querySelectorAll('[data-twin]').forEach(el=>{
  let n=el.nextElementSibling; if(!n||!n.classList.contains('bk')){n=document.createElement('span');n.className='bk';el.after(n);}
  n.textContent='ในบท '+fj(jp(el.dataset.twin));});}
function put(id,v,d){const el=$(id);el.textContent=nf(v,d);el.classList.toggle('neg',v<0);}
const NS='http://www.w3.org/2000/svg';
function S(tag,a,txt){const e=document.createElementNS(NS,tag);for(const k in a)e.setAttribute(k,a[k]);if(txt!==undefined)e.textContent=txt;return e;}
function clear(svg){while(svg.firstChild)svg.removeChild(svg.firstChild);}
function T(svg,x,y,s,o){o=o||{};svg.appendChild(S('text',{x:x,y:y,'font-size':o.size||12,fill:o.fill||'#4b5563','text-anchor':o.anchor||'start','font-weight':o.weight||400,'font-family':'Sarabun,sans-serif'},s));}
const COL={green:'#16a34a',red:'#dc2626',purple:'#7c3aed',blue:'#2563eb',amber:'#d97706',grey:'#9ca3af',ink:'#374151',grid:'#e5e7eb'};
function gauss(){let u=0,v=0;while(u===0)u=Math.random();while(v===0)v=Math.random();return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v);}
"""

BACK = """<p style="text-align:center;margin-top:26px"><a href="sab-tools.html">← เครื่องมือทั้งหมดของเล่ม</a> ·
<a href="sab-workbook.xlsx">สมุดงาน xlsx</a></p>"""


def tool_page(fname, title, sub, desc, body, keys, js):
    html = B.page(title, sub, desc, CSS + "\n" + body + "\n" + BACK + "\n" + data_block(keys) +
                  "\n<script>\n" + JS_COMMON + ids_js(keys) + "\n" + js + "\n</script>")
    return fname, html


# ───────────────────────── 1. carry ─────────────────────────

CARRY_BODY = r"""
<div class="bx bb"><div class="bt">🎯 เครื่องมือนี้ตอบอะไร</div>
<p>ส่วนต่าง futures กับ spot บนจอดูเหมือนเงินที่รออยู่ แต่กว่าจะถึงมือต้องผ่านสี่ขั้น: หารด้วยทุนทั้งก้อน หักค่าธรรมเนียม หักค่าเสียโอกาส
แล้วยังต้องเหลือเงินสดพอรับวันที่ราคาวิ่งสวน เครื่องมือนี้ให้คุณเปลี่ยนตัวเลขเองแล้วดูว่าขั้นไหนกินมากที่สุด
ค่าตั้งต้นคือไม้แรกของมินในบท 4–6 (ตารางคิดที่ 1 BTC) และทุกตัวเลขสดมีป้ายเทา "ในบท" วางข้างกันให้เทียบ</p></div>

<div class="tool" id="t-ladder">
<h3>① บันไดสี่ขั้น: จาก % บนจอ ถึงส่วนเกินในมือ</h3>
<p class="whyline">🔩 ทำไมต้องมีเครื่องมือนี้: % บนจอคิดจากราคา spot ไม่ใช่จากทุนที่คุณต้องวางจริง และยังไม่หักอะไรเลย</p>
<div class="ctrl">
<label for="c-s">ราคา spot ตอนเปิด</label><input type="number" id="c-s" step="100">
<label for="c-f">ราคา futures ตอนเปิด</label><input type="number" id="c-f" step="100">
<label for="c-days">วันถึงหมดอายุ</label><input type="number" id="c-days" step="1" min="1">
<label for="c-cap">ทุนที่วางทั้งก้อน (spot + หลักประกัน + เงินสดอิสระ)</label><input type="number" id="c-cap" step="1000">
<label for="c-st">ราคาชำระวันหมดอายุ (ใช้คิดค่าธรรมเนียมขาย spot)</label><input type="number" id="c-st" step="100">
<label for="c-hur">hurdle ต่อปี (%) — ผลตอบแทนที่ได้แน่ ๆ ถ้าไม่ทำอะไร</label><input type="number" id="c-hur" step="0.5">
</div>
<p style="margin-bottom:4px">ค่าธรรมเนียมต่อข้าง</p>
<div class="seg" id="c-feeseg"></div>
<div class="tw"><table>
<tr><th>ขั้น</th><th>คิดอย่างไร</th><th class="num">% ต่อปี</th></tr>
<tr><td>① บนจอ</td><td>basis <span class="v" id="c-basis" data-twin="ch05/บันได/basis"></span> ÷ ราคา spot · ปรับเป็นทั้งปี</td><td class="num"><span class="v" id="c-r1" data-twin="ch05/บันได/บนจอ"></span></td></tr>
<tr><td>② ต่อทุน</td><td>basis ÷ ทุนทั้งก้อน (ไม่ใช่ราคา spot)</td><td class="num"><span class="v" id="c-r2" data-twin="ch05/บันได/ต่อทุน"></span></td></tr>
<tr><td>③ หลังค่าธรรมเนียม</td><td>หักค่าธรรมเนียมสามครั้ง (ซื้อ spot · short futures · ขาย spot วันหมดอายุ) รวม <span class="v" id="c-fee" data-twin="ch05/บันได/ค่าธรรมเนียม"></span> เหลือ <span class="v" id="c-net" data-twin="ch05/บันได/สุทธิ"></span></td><td class="num"><span class="v" id="c-r3" data-twin="ch05/บันได/หลังค่าธรรมเนียม"></span></td></tr>
<tr><td>④ ส่วนเกิน</td><td>หักค่าเสียโอกาสของทุนตลอดช่วง <span class="v" id="c-opp" data-twin="ch05/บันได/ค่าเสียโอกาส"></span> เหลือ <span class="v" id="c-exc" data-twin="ch05/บันได/ส่วนเกิน"></span></td><td class="num"><span class="v" id="c-r4" data-twin="ch05/บันได/ส่วนเกินเปอร์เซ็นต์"></span></td></tr>
</table></div>
<svg class="chart" id="c-ladsvg" viewBox="0 0 640 230" role="img" aria-label="บันไดสี่ขั้นของ carry"></svg>
<p class="src">🔢 ตัวเลขสมมติเพื่อสอน · สูตรเดียวกับแท็บ "บันได carry" ในสมุดงาน · ค่าธรรมเนียม futures ตอนชำระไม่มีในตัวอย่างนี้</p>
</div>

<div class="tool" id="t-hold">
<h3>② ปิดหรือถือวันที่ N</h3>
<p class="whyline">🔩 ทำไมต้องมีเครื่องมือนี้: ถ้า basis หดเร็ว เงินที่ยังเหลือให้เก็บอาจน้อยกว่าค่าเสียโอกาสของทุนที่ค้างอยู่</p>
<div class="ctrl">
<label for="h-n">วันที่ตัดสิน (นับจากวันเปิด)</label><input type="number" id="h-n" step="1" min="0">
<label for="h-s">ราคา spot วันนั้น</label><input type="number" id="h-s" step="100">
<label for="h-f">ราคา futures วันนั้น</label><input type="number" id="h-f" step="100">
<label for="h-hur">hurdle ต่อปี (%)</label><input type="number" id="h-hur" step="0.5">
</div>
<div class="tw"><table>
<tr><th>รายการ</th><th class="num">ค่า</th></tr>
<tr><td>basis ที่ยังเหลือให้เก็บ</td><td class="num"><span class="v" id="h-b" data-twin="ch06/วันที่30/basis"></span></td></tr>
<tr><td>ค่าธรรมเนียมที่ประหยัดได้ถ้าไม่ปิดตอนนี้ (ปิดสองขา)</td><td class="num"><span class="v" id="h-cf" data-twin="ch06/วันที่30/ค่าธรรมเนียมปิดตอนนี้"></span></td></tr>
<tr><td>ค่าธรรมเนียมขาย spot ถ้าถือถึงวันหมดอายุ</td><td class="num"><span class="v" id="h-hf" data-twin="ch06/วันที่30/ค่าธรรมเนียมspotถ้าถือ"></span></td></tr>
<tr><td><strong>ถือต่อได้เพิ่ม</strong></td><td class="num"><span class="v" id="h-extra" data-twin="ch06/วันที่30/ถือได้เพิ่ม"></span></td></tr>
<tr><td>ค่าเสียโอกาสของทุนในวันที่เหลือ <span id="h-rem"></span> วัน</td><td class="num"><span class="v" id="h-opp" data-twin="ch06/วันที่30/เสียโอกาส60วัน"></span></td></tr>
<tr><td><strong>ตัดสิน</strong></td><td class="num"><span class="v key" id="h-dec" data-twin="ch06/วันที่30/ตัดสินที่hurdle4"></span></td></tr>
<tr><td>hurdle ที่ทำให้ปิดกับถือเท่ากัน (% ต่อปี)</td><td class="num"><span class="v" id="h-sw" data-twin="ch06/วันที่30/จุดเปลี่ยนhurdle"></span></td></tr>
</table></div>
<p>ลองเปลี่ยน basis ของวันนั้นทีละขั้น (ราคา spot ตามค่าตั้งต้น · futures = spot + basis):</p>
<div class="tw"><table id="h-dist"><tr><th class="num">basis วันนั้น</th><th class="num">ถือต่อได้เพิ่ม</th><th class="num">ค่าเสียโอกาส</th><th>ตัดสิน</th></tr></table></div>
<p class="src">🔢 ตัวเลขสมมติเพื่อสอน · ใช้ทุน ค่าธรรมเนียม และวันถึงหมดอายุจากส่วน ①</p>
</div>

<div class="tool" id="t-pockets">
<h3>③ สองกระเป๋า และกันชนสะสม</h3>
<p class="whyline">🔩 ทำไมต้องมีเครื่องมือนี้: กำไรขา spot อยู่ในเหรียญ ใช้จ่ายหลักประกันขา futures ไม่ได้ — เงินสดอิสระคือกันชนเดียวที่มี</p>
<div class="ctrl">
<label for="p-m">หลักประกัน (% ของราคา futures ปัจจุบัน · กติกาสอน)</label><input type="number" id="p-m" step="1" min="1">
<label for="p-x">spot ขึ้นในวันเดียว (%)</label><span class="val" id="p-xv"></span>
<input type="range" id="p-x" min="0" max="30" step="0.5">
<label for="p-ba">basis หลังราคาขยับ</label><input type="number" id="p-ba" step="100">
</div>
<div class="seg"><button type="button" id="p-min">ทุนของมิน</button><button type="button" id="p-ton">ทุนของต้น</button></div>
<div class="kpi">
<div><div class="lb">เงินสดอิสระหลังเปิดไม้</div><span class="v" id="p-free" data-twin="ch03/เปิดไม้/เงินสดอิสระ"></span></div>
<div><div class="lb">กันชน: futures ขึ้นได้ในวันเดียว (%)</div><span class="v big" id="p-buf" data-twin="ch04/กันชน/125000"></span></div>
<div><div class="lb">กันชนเป็นเงิน</div><span class="v" id="p-bufm" data-twin="ch04/กันชนเงิน/125000"></span></div>
<div><div class="lb">ต้องโอนเติม</div><span class="v" id="p-top" data-twin="ch04/ต้องโอน"></span></div>
<div><div class="lb">ขาด</div><span class="v" id="p-short" data-twin="ch04/dist/1/ขาดที่ทุน125000"></span></div>
<div><div class="lb">เงินสดอิสระหลังโอน</div><span class="v" id="p-after" data-twin="ch04/เงินสดอิสระหลังโอน"></span></div>
<div><div class="lb">กันชนสะสม: วันถัดไปรับได้อีก (%)</div><span class="v" id="p-more" data-twin="ch04/หลังวันแรกรับได้อีก"></span></div>
<div><div class="lb">equity เปลี่ยน (สองขารวมกัน)</div><span class="v" id="p-eq" data-twin="ch04/equity_เปลี่ยน"></span></div>
</div>
<svg class="chart" id="p-svg" viewBox="0 0 640 250" role="img" aria-label="สองกระเป๋า: กำไรขา spot กับเงินสดที่ต้องโอนเติม"></svg>
<svg class="chart" id="p-line" viewBox="0 0 640 250" role="img" aria-label="เงินที่ต้องโอนเติมเทียบเงินสดอิสระเมื่อราคาขึ้นมากขึ้น"></svg>
<p class="src">🔢 ตัวเลขสมมติเพื่อสอน · ต้องโอนเติม = (1 + อัตราหลักประกัน) × (futures ใหม่ − futures เดิม) · ใช้ราคาและทุนจากส่วน ① · ชำระสิ้นวัน</p>
</div>

<div class="tool" id="t-crowd">
<h3>④ บันไดแย่ง: basis หดเมื่อคนแห่มาทำแบบเดียวกัน</h3>
<p class="whyline">🔩 ทำไมต้องมีเครื่องมือนี้: ส่วนเกินคือสิ่งที่คนอื่นแย่งได้ ค่าธรรมเนียมกับค่าเสียโอกาสไม่หดตาม</p>
<div class="tw"><table id="k-tbl"><tr><th class="num">basis</th><th class="num">① บนจอ</th><th class="num">③ หลังค่าธรรมเนียม</th><th class="num">④ ส่วนเกิน</th></tr></table></div>
<p>basis ต่ำสุดที่ยังเหลือส่วนเกินมากกว่าศูนย์ (ค่าอื่นตามส่วน ①): <span class="v key" id="k-zero"></span></p>
<svg class="chart" id="k-svg" viewBox="0 0 640 230" role="img" aria-label="ส่วนเกินเมื่อ basis หด"></svg>
<p class="src">🔢 ตัวเลขสมมติเพื่อสอน · futures = spot + basis · ใช้ทุน ค่าธรรมเนียม hurdle และวันจากส่วน ①</p>
</div>

<div class="bx ba"><div class="bt">💡 อ่านผลอย่างไร</div>
<ul>
<li>ถ้า ④ ติดลบ แปลว่าเอาเงินไปวางที่ได้ hurdle แน่ ๆ ดีกว่า แม้ ① จะดูสูง</li>
<li>ทุนมากขึ้นทำให้กันชนหนาขึ้น แต่ ② ③ ④ บางลง — สองกระเป๋ากับบันไดแลกกันเสมอ</li>
<li>เครื่องมือนี้ไม่ได้บอกกติกาของ exchange ใด ค่าธรรมเนียมและหลักประกันจริงต้องจดจากบัตรตลาดของคุณเอง 📱</li>
</ul></div>
<p>คู่กับเครื่องมือในคลัง: <a href="tool-carry-blowup.html">carry ค่าเงินกับหางที่ระเบิด</a> (เรื่องคนละแบบ — carry ของค่าเงินและความเสี่ยงหาง)</p>
"""

CARRY_JS = r"""
const M=BOOK['บัญชีมิน'], C4=BOOK.ch04;
const FEES=[['taker',M['ค่าธรรมเนียม'].taker],['maker',M['ค่าธรรมเนียม'].maker],['แบบมินใน nq',M['ค่าธรรมเนียม']['มินในnq']]];
let fee=M['ค่าธรรมเนียม'].taker;
setv('c-s',M.BTC.spot);setv('c-f',M.BTC.futures);setv('c-days',M.BTC['วันถึงหมดอายุ']);setv('c-cap',M['ทุนภาค1']['รวม']);
setv('c-st',M.BTC['ราคาชำระ']);setv('c-hur',M.hurdle);
setv('h-n',30);setv('h-s',BOOK.ch06['วันที่30'].spot);setv('h-f',BOOK.ch06['วันที่30'].futures);setv('h-hur',M.hurdle);
setv('p-m',M['กติกาหลักประกันเปอร์เซ็นต์']);setv('p-x',10);setv('p-ba',C4['คืนวันที่9'].futures-C4['คืนวันที่9'].spot);
const seg=$('c-feeseg');
FEES.forEach(([n,v],i)=>{const b=document.createElement('button');b.type='button';b.id='c-fee'+i;b.textContent=n+' '+fj(v)+'%';
  b.onclick=()=>{fee=v;[...seg.children].forEach(x=>x.classList.toggle('on',x===b));upd();};if(i===0)b.classList.add('on');seg.appendChild(b);});
function P(){return {s:num('c-s'),f:num('c-f'),days:num('c-days'),cap:num('c-cap'),st:num('c-st'),hur:num('c-hur'),fee:fee};}
function ladder(p,basis){const b=basis===undefined?p.f-p.s:basis, f0=p.s+b, k=365/p.days*100;
  const fees=p.fee/100*(p.s+f0+p.st), net=b-fees, opp=p.cap*p.hur/100*p.days/365;
  return {basis:b,r1:b/p.s*k,r2:b/p.cap*k,fees:fees,net:net,r3:net/p.cap*k,opp:opp,exc:net-opp,r4:(net-opp)/p.cap*k};}
function bars(svg,items,title){clear(svg);const W=640,H=+svg.getAttribute('viewBox').split(' ')[3],x0=150,x1=W-80;
  const mx=Math.max(1e-9,...items.map(d=>Math.abs(d[1])));const mn=Math.min(0,...items.map(d=>d[1]));
  const sc=v=>x0+(v-mn)/(mx-mn)*(x1-x0);const bh=Math.min(34,(H-50)/items.length-10);
  T(svg,10,18,title,{weight:700,fill:COL.ink});
  items.forEach((d,i)=>{const y=34+i*(bh+12);const a=sc(Math.min(0,d[1])),b=sc(Math.max(0,d[1]));
    svg.appendChild(S('rect',{x:a,y:y,width:Math.max(1,b-a),height:bh,rx:3,fill:d[2]}));
    T(svg,x0-8,y+bh/2+4,d[0],{anchor:'end',size:12.5});T(svg,b+6,y+bh/2+4,d[3]||nf(d[1],2),{size:12.5,weight:700,fill:d[2]});});
  svg.appendChild(S('line',{x1:sc(0),x2:sc(0),y1:28,y2:H-8,stroke:COL.grid}));}
function upd(){const p=P(),L=ladder(p);
  put('c-basis',L.basis,0);put('c-r1',L.r1,2);put('c-r2',L.r2,2);put('c-fee',L.fees,2);put('c-net',L.net,2);put('c-r3',L.r3,2);
  put('c-opp',L.opp,2);put('c-exc',L.exc,2);put('c-r4',L.r4,2);
  bars($('c-ladsvg'),[['① บนจอ',L.r1,COL.grey],['② ต่อทุน',L.r2,COL.blue],['③ หลังค่าธรรมเนียม',L.r3,COL.blue],
    ['④ ส่วนเกิน',L.r4,L.r4>=0?COL.green:COL.red]].map(d=>[d[0],d[1],d[2],nf(d[1],2)+'%']),'% ต่อปี แต่ละขั้น');
  // ② ปิดหรือถือ
  const n=num('h-n'),sN=num('h-s'),fN=num('h-f'),hh=num('h-hur');
  function hold(sN,fN,hh){const b=fN-sN,cf=p.fee/100*(sN+fN),hf=p.fee/100*sN,extra=b-hf+cf,rem=p.days-n,opp=p.cap*hh/100*rem/365;
    return {b:b,cf:cf,hf:hf,extra:extra,rem:rem,opp:opp,dec:opp>extra?'ปิด':'ถือ',sw:extra/(p.cap*rem/365)*100};}
  const H=hold(sN,fN,hh);
  put('h-b',H.b,0);put('h-cf',H.cf,2);put('h-hf',H.hf,2);put('h-extra',H.extra,2);$('h-rem').textContent=H.rem;put('h-opp',H.opp,2);
  $('h-dec').textContent=H.dec;put('h-sw',H.sw,2);
  const tb=$('h-dist');while(tb.rows.length>1)tb.deleteRow(1);
  BOOK.ch06.dist.forEach((d,i)=>{const r=tb.insertRow();const X=hold(sN,sN+d['basisวันที่30'],hh);
    r.innerHTML='<td class="num">'+nf(d['basisวันที่30'],0)+'</td><td class="num"><span class="v" data-twin="ch06/dist/'+i+'/ถือได้เพิ่ม">'+nf(X.extra,2)+
    '</span></td><td class="num"><span class="v" data-twin="ch06/dist/'+i+'/เสียโอกาส60วัน">'+nf(X.opp,2)+'</span></td><td><span class="v" data-twin="ch06/dist/'+i+'/ตัดสิน">'+X.dec+'</span></td>';});
  // ③ สองกระเป๋า
  const m=num('p-m')/100,x=num('p-x'),ba=num('p-ba');$('p-xv').textContent=nf(x,1)+'%';
  const free=p.cap-p.s-m*p.f,bufm=free/(1+m),buf=bufm/p.f*100,s1=p.s*(1+x/100),f1=s1+ba,top=(1+m)*(f1-p.f),
    short=Math.max(0,top-free),after=Math.max(0,free-top),more=after/(1+m)/f1*100,eq=(s1-p.s)-(f1-p.f);
  put('p-free',free,0);put('p-buf',buf,1);put('p-bufm',bufm,2);put('p-top',top,0);put('p-short',short,0);put('p-after',after,0);
  put('p-more',more,1);put('p-eq',eq,0);
  bars($('p-svg'),[['กำไรขา spot',s1-p.s,COL.green,'+'+nf(s1-p.s,0)+' (ติดอยู่ในเหรียญ)'],['เงินสดอิสระก่อน',free,COL.grey],
    ['ต้องโอนเติม',-top,COL.red,nf(-top,0)],['เงินสดหลังโอน',short>0?-short:after,short>0?COL.red:COL.green,short>0?'ขาด '+nf(short,0):nf(after,0)]],
    'คืนที่ spot ขึ้น '+nf(x,1)+'%: กำไรอยู่กระเป๋าหนึ่ง ใบเรียกเงินอยู่อีกกระเป๋า');
  // เส้นต้องโอนเติมเทียบเงินสดอิสระ
  const sv=$('p-line');clear(sv);const W=640,Hh=250,x0=60,x1=W-20,y0=Hh-34,y1=30,XM=30;
  const tops=[];for(let q=0;q<=XM;q+=0.5){const f=p.s*(1+q/100)+ba;tops.push([q,(1+m)*(f-p.f)]);}
  const ymax=Math.max(free*1.6,...tops.map(t=>t[1]))*1.05,ymin=Math.min(0,...tops.map(t=>t[1]));
  const X=q=>x0+q/XM*(x1-x0),Y=v=>y0-(v-ymin)/(ymax-ymin)*(y0-y1);
  T(sv,10,18,'ต้องโอนเติม (แดง) เทียบเงินสดอิสระ (เทา) เมื่อ spot ขึ้นในวันเดียว',{weight:700,fill:COL.ink});
  for(let q=0;q<=XM;q+=5){sv.appendChild(S('line',{x1:X(q),x2:X(q),y1:y1,y2:y0,stroke:COL.grid}));T(sv,X(q),y0+16,q+'%',{anchor:'middle',size:11});}
  sv.appendChild(S('line',{x1:x0,x2:x1,y1:Y(free),y2:Y(free),stroke:COL.grey,'stroke-width':3}));
  sv.appendChild(S('polyline',{points:tops.map(t=>X(t[0])+','+Y(t[1])).join(' '),fill:'none',stroke:COL.red,'stroke-width':3}));
  const qb=(free/(1+m)-ba+p.f)/p.s*100-100; // spot ขึ้นกี่ % แล้วเงินสดหมดพอดี
  if(qb>0&&qb<XM){sv.appendChild(S('circle',{cx:X(qb),cy:Y(free),r:6,fill:COL.purple}));T(sv,X(qb)+8,Y(free)-8,'เงินสดหมดที่ spot +'+nf(qb,1)+'%',{fill:COL.purple,weight:700});}
  sv.appendChild(S('line',{x1:X(x),x2:X(x),y1:y1,y2:y0,stroke:COL.ink,'stroke-dasharray':'4 4'}));
  T(sv,x0-6,Y(free)+4,nf(free,0),{anchor:'end',size:11});
  // ④ บันไดแย่ง
  const kt=$('k-tbl');while(kt.rows.length>1)kt.deleteRow(1);const ks=[];
  BOOK.ch05['บันไดแย่ง'].forEach((d,i)=>{const Lb=ladder(p,d.basis);ks.push([nf(d.basis,0),Lb.r4]);const r=kt.insertRow();
    r.innerHTML='<td class="num">'+nf(d.basis,0)+'</td><td class="num"><span class="v" data-twin="ch05/บันไดแย่ง/'+i+'/บนจอ">'+nf(Lb.r1,2)+
    '</span></td><td class="num"><span class="v" data-twin="ch05/บันไดแย่ง/'+i+'/หลังค่าธรรมเนียม">'+nf(Lb.r3,2)+
    '</span></td><td class="num"><span class="v '+(Lb.r4<0?'neg':'pos')+'" data-twin="ch05/บันไดแย่ง/'+i+'/ส่วนเกินเปอร์เซ็นต์">'+nf(Lb.r4,2)+'</span></td>';});
  const opp=p.cap*p.hur/100*p.days/365, bz=(p.fee/100*(2*p.s+p.st)+opp)/(1-p.fee/100);put('k-zero',bz,0);
  bars($('k-svg'),ks.map(d=>['basis '+d[0],d[1],d[1]>=0?COL.green:COL.red,nf(d[1],2)+'%']),'④ ส่วนเกิน (% ต่อปี) เมื่อ basis หด');
  twins();}
['c-s','c-f','c-days','c-cap','c-st','c-hur','h-n','h-s','h-f','h-hur','p-m','p-x','p-ba'].forEach(i=>$(i).addEventListener('input',upd));
$('p-min').onclick=()=>{setv('c-cap',M['ทุนภาค1']['รวม']);upd();};
$('p-ton').onclick=()=>{setv('c-cap',C4['ทุนของต้น']);upd();};
upd();
"""


# ───────────────────────── 2. funding ─────────────────────────

FUND_BODY = r"""
<div class="bx bb"><div class="bt">🎯 เครื่องมือนี้ตอบอะไร</div>
<p>perp ไม่มีวันหมดอายุ เงินที่ได้จึงไม่ล็อกไว้ล่วงหน้าแบบ basis — มันมาเป็นรอบ ๆ และเปลี่ยนทิศได้
มินถือ long spot คู่ short perp 30 วัน (90 รอบ · รอบละ 8 ชั่วโมงในตัวอย่างนี้) ที่ราคา mark ตรึงไว้
เลือกเส้นทาง funding แล้วดูว่าเงินที่ได้จริงต่างจาก % บนจอแค่ไหน กฎ "ติดลบ k รอบติดแล้วออก" ช่วยหรือทำร้าย
และค่าธรรมเนียม maker กับ taker ต่างกันเท่าไร</p></div>

<div class="tool">
<h3>เลือกเส้นทางและกติกา</h3>
<p class="whyline">🔩 ทำไมต้องมีเครื่องมือนี้: % บนจอคืออัตราตอนนี้คูณทั้งปี แต่เงินจริงคือผลรวมของทุกรอบที่คุณยังถืออยู่ หักค่าธรรมเนียมเปิดปิดสองขา</p>
<div class="seg" id="f-paths"></div>
<div class="ctrl">
<label for="f-k">กฎออก: ติดลบกี่รอบติดกันแล้วออก (0 = ไม่ใช้กฎ)</label><input type="number" id="f-k" min="0" max="20" step="1">
<label for="f-crowd">อัตราที่เหลือเมื่อถูกแย่ง (% ของเส้นทางเดิม)</label><span class="val" id="f-crowdv"></span>
<input type="range" id="f-crowd" min="10" max="100" step="5">
<label for="f-hur">hurdle ต่อปี (%)</label><input type="number" id="f-hur" step="0.5">
</div>
<div class="seg" id="f-feeseg"></div>
<div class="kpi">
<div><div class="lb">funding รวมทั้ง 90 รอบ</div><span class="v" id="f-tot"></span></div>
<div><div class="lb">ค่าธรรมเนียมเปิดปิดสองขา</div><span class="v" id="f-fees"></span></div>
<div><div class="lb">สุทธิถ้าถือครบ</div><span class="v big" id="f-net"></span></div>
<div><div class="lb">สุทธิตามกฎออก</div><span class="v big" id="f-rule"></span></div>
<div><div class="lb">กฎออกทำงานที่รอบ</div><span class="v key" id="f-exit"></span></div>
</div>
<svg class="chart" id="f-cum" viewBox="0 0 640 280" role="img" aria-label="funding สะสมของสี่เส้นทาง"></svg>
<p class="src">🔢 ตัวเลขสมมติเพื่อสอน · ดอลลาร์ต่อ 1 BTC ที่ราคา mark คงที่ · เส้นหนา = เส้นทางที่เลือก · จุดม่วง = รอบที่กฎออกทำงาน</p>
<h3>อัตรารายรอบ (แตะหรือลากบนกราฟเพื่อวาดเส้นทางของคุณเอง)</h3>
<svg class="chart" id="f-draw" viewBox="0 0 640 220" role="img" aria-label="อัตรา funding รายรอบ วาดเองได้"></svg>
<p class="src">🔢 อัตราต่อรอบ (%) · บวก = short perp ได้รับ · ลบ = short perp จ่าย · กดปุ่ม "วาดเอง" แล้วลากนิ้วบนกราฟ</p>
</div>

<div class="tool">
<h3>บันไดของเส้นทางที่เลือก (% ต่อปีของทุน)</h3>
<div class="tw"><table>
<tr><th>ขั้น</th><th>คิดอย่างไร</th><th class="num">% ต่อปี</th></tr>
<tr><td>① บนจอ</td><td>อัตรารอบแรก × 3 รอบต่อวัน · ปรับเป็นทั้งปี</td><td class="num"><span class="v" id="f-l1" data-twin="ch07/บันไดfunding/บนจอ"></span></td></tr>
<tr><td>② ต่อทุน</td><td>funding ที่ได้จริงทั้ง 30 วัน ÷ ทุนทั้งก้อน</td><td class="num"><span class="v" id="f-l2" data-twin="ch07/บันไดfunding/ต่อทุน"></span></td></tr>
<tr><td>③ หลังค่าธรรมเนียม</td><td>หักค่าธรรมเนียมเปิดปิดสองขา (ถือครบ ไม่ใช้กฎ)</td><td class="num"><span class="v" id="f-l3" data-twin="ch07/บันไดfunding/หลังค่าธรรมเนียม"></span></td></tr>
<tr><td>④ ส่วนเกิน</td><td>หักค่าเสียโอกาสของทุนตาม hurdle</td><td class="num"><span class="v" id="f-l4" data-twin="ch07/บันไดfunding/ส่วนเกินเปอร์เซ็นต์"></span></td></tr>
</table></div>
<p class="src">🔢 ตัวเลขสมมติเพื่อสอน · ค่าในบท (ป้ายเทา) คือเส้นทางราบ ค่าธรรมเนียม maker</p>
</div>

<div class="tool">
<h3>สี่เส้นทางพร้อมกัน (ใช้กฎ อัตราที่เหลือ และค่าธรรมเนียมจากด้านบน)</h3>
<div class="tw"><table id="f-all"><tr><th>เส้นทาง</th><th class="num">funding รวม</th><th class="num">สุทธิ maker</th><th class="num">สุทธิ taker</th><th class="num">ตามกฎ maker</th><th class="num">ตามกฎ taker</th></tr></table></div>
<p class="src">🔢 ตัวเลขสมมติเพื่อสอน · ป้ายเทาคือตารางในบท 7 (กฎ 3 รอบ · อัตราเต็ม)</p>
<h3>อัตราถูกแย่ง: เส้นทางราบเมื่ออัตราต่อรอบหดลง</h3>
<div class="tw"><table id="f-crowdtbl"><tr><th class="num">อัตราต่อรอบ (%)</th><th class="num">สุทธิ maker (% ต่อปี)</th><th class="num">สุทธิ taker (% ต่อปี)</th></tr></table></div>
<p class="src">🔢 ตัวเลขสมมติเพื่อสอน · ถือครบ 30 วัน ไม่ใช้กฎออก</p>
</div>

<div class="bx ba"><div class="bt">💡 อ่านผลอย่างไร</div>
<ul>
<li>เส้นทาง "กลับขั้ว" กฎออกช่วยไว้ แต่เส้นทาง "สลับ" กฎเดียวกันทำให้ออกเร็วเกินแล้วพลาดรอบบวกที่ตามมา — ไม่มีกฎที่ชนะทุกเส้นทาง</li>
<li>เมื่ออัตราถูกแย่งเหลือราวครึ่ง ค่าธรรมเนียม taker กินส่วนใหญ่ของสิ่งที่เหลือ</li>
<li>ตัวเลขรอบ funding เพดาน และกติกาจริงต่างกันทุก exchange — จดจากบัตรตลาดของคุณ 📱</li>
</ul></div>
"""

FUND_JS = r"""
const M=BOOK['บัญชีมิน'], C7=BOOK.ch07;
const MARK=M.BTC.spot, CAP=M['ทุนภาค1']['รวม'], DAYS=30, LEGS=4;
const NAMES=['ราบ','พุ่งแล้วแผ่ว','กลับขั้ว','สลับ'];
const BASE={};NAMES.forEach(n=>{let p=0;BASE[n]=C7['กราฟ'][n].map(c=>{const r=(c-p)/MARK;p=c;return Math.round(r*1e8)/1e8;});});
let cur='ราบ', mine=BASE['ราบ'].slice(), feeMode='maker';
setv('f-k',3);setv('f-crowd',100);setv('f-hur',M.hurdle);
const ps=$('f-paths');
NAMES.concat(['วาดเอง']).forEach(n=>{const b=document.createElement('button');b.type='button';b.textContent=n;b.dataset.p=n;
  b.onclick=()=>{if(n==='วาดเอง'&&cur!=='วาดเอง')mine=rates(cur,1).slice();cur=n;upd();};ps.appendChild(b);});
const fs=$('f-feeseg');
[['maker',M['ค่าธรรมเนียม'].maker],['taker',M['ค่าธรรมเนียม'].taker]].forEach(([n,v])=>{const b=document.createElement('button');b.type='button';
  b.textContent='ค่าธรรมเนียม '+n+' '+fj(v)+'%';b.dataset.f=n;b.onclick=()=>{feeMode=n;upd();};fs.appendChild(b);});
function feeTotal(mode){return M['ค่าธรรมเนียม'][mode]/100*LEGS*MARK;}
function rates(n,f){const r=n==='วาดเอง'?mine:BASE[n];return r.map(x=>x*f);}
function run(r,fee,k){let tot=0;r.forEach(x=>tot+=MARK*x);let neg=0,rc=0,held=true,exitAt=null;
  r.forEach((x,i)=>{if(held){rc+=MARK*x;neg=x<0?neg+1:0;if(k>0&&neg>=k){held=false;exitAt=i+1;}}});
  return {tot:tot,net:tot-fee,pct:(tot-fee)/CAP*365/DAYS*100,rule:rc,ruleNet:rc-fee,exitAt:exitAt};}
function upd(){const k=Math.max(0,Math.round(num('f-k'))),f=num('f-crowd')/100,hur=num('f-hur'),fee=feeTotal(feeMode);
  $('f-crowdv').textContent=nf(f*100,0)+'%';
  [...ps.children].forEach(b=>b.classList.toggle('on',b.dataset.p===cur));[...fs.children].forEach(b=>b.classList.toggle('on',b.dataset.f===feeMode));
  const r=rates(cur,f),R=run(r,fee,k);
  put('f-tot',R.tot,2);put('f-fees',fee,2);put('f-net',R.net,2);put('f-rule',R.ruleNet,2);$('f-exit').textContent=R.exitAt?('รอบที่ '+R.exitAt):'ไม่ออก (ถือครบ)';
  const Rm=run(r,feeTotal('maker'),0);
  put('f-l1',r[0]*3*365*100,2);put('f-l2',R.tot/CAP*365/DAYS*100,2);put('f-l3',Rm.pct,2);
  put('f-l4',(Rm.net-CAP*hur/100*DAYS/365)/CAP*365/DAYS*100,2);
  // ตารางสี่เส้นทาง
  const t=$('f-all');while(t.rows.length>1)t.deleteRow(1);
  NAMES.forEach(n=>{const rr=rates(n,f),a=run(rr,feeTotal('maker'),k),b=run(rr,feeTotal('taker'),k);const row=t.insertRow();
    const c=(v,key)=>'<td class="num"><span class="v'+(v<0?' neg':'')+'" data-twin="ch07/สี่เส้นทาง/'+n+'/'+key+'">'+nf(v,2)+'</span></td>';
    row.innerHTML='<td>'+n+'</td>'+c(a.tot,'fundingรวม')+c(a.net,'สุทธิmaker')+c(b.net,'สุทธิtaker')+c(a.ruleNet,'กฎmaker')+c(b.ruleNet,'กฎtaker');});
  const ct=$('f-crowdtbl');while(ct.rows.length>1)ct.deleteRow(1);
  C7['fundingถูกแย่ง'].forEach((d,i)=>{const sc=d['ต่อรอบเปอร์เซ็นต์']/100/BASE['ราบ'][0];const rr=BASE['ราบ'].map(x=>x*sc);
    const a=run(rr,feeTotal('maker'),0),b=run(rr,feeTotal('taker'),0);const row=ct.insertRow();
    row.innerHTML='<td class="num">'+fj(d['ต่อรอบเปอร์เซ็นต์'])+'</td><td class="num"><span class="v" data-twin="ch07/fundingถูกแย่ง/'+i+'/สุทธิmakerเปอร์เซ็นต์">'+nf(a.pct,2)+
      '</span></td><td class="num"><span class="v" data-twin="ch07/fundingถูกแย่ง/'+i+'/สุทธิtakerเปอร์เซ็นต์">'+nf(b.pct,2)+'</span></td>';});
  drawCum(f,k,R);drawRates(r);twins();}
function drawCum(f,k,R){const sv=$('f-cum');clear(sv);const W=640,H=280,x0=56,x1=W-16,y0=H-30,y1=28;
  const series={};NAMES.forEach(n=>{let c=0;series[n]=rates(n,f).map(x=>c+=MARK*x);});
  if(cur==='วาดเอง'){let c=0;series['วาดเอง']=rates('วาดเอง',f).map(x=>c+=MARK*x);}
  const all=[].concat(...Object.values(series));const ymax=Math.max(10,...all)*1.08,ymin=Math.min(0,...all)*1.08;
  const X=i=>x0+i/89*(x1-x0),Y=v=>y0-(v-ymin)/(ymax-ymin)*(y0-y1);
  T(sv,10,18,'funding สะสม (ดอลลาร์ต่อ 1 BTC)',{weight:700,fill:COL.ink});
  [0,30,60,89].forEach(i=>{sv.appendChild(S('line',{x1:X(i),x2:X(i),y1:y1,y2:y0,stroke:COL.grid}));T(sv,X(i),y0+16,'รอบ '+(i+1),{anchor:'middle',size:11});});
  sv.appendChild(S('line',{x1:x0,x2:x1,y1:Y(0),y2:Y(0),stroke:'#cbd5e1'}));T(sv,x0-6,Y(0)+4,'0',{anchor:'end',size:11});
  Object.keys(series).forEach(n=>{const on=n===cur;const pts=series[n].map((v,i)=>X(i)+','+Y(v)).join(' ');
    sv.appendChild(S('polyline',{points:pts,fill:'none',stroke:on?COL.blue:COL.grey,'stroke-width':on?3.2:1.4,opacity:on?1:.8}));
    const last=series[n][89];T(sv,x1-2,Y(last)-5,n+' '+nf(last,0),{anchor:'end',size:11,fill:on?COL.blue:'#6b7280',weight:on?700:400});});
  if(R.exitAt){const i=R.exitAt-1,v=series[cur][i];sv.appendChild(S('circle',{cx:X(i),cy:Y(v),r:6,fill:COL.purple}));
    T(sv,X(i)+8,Y(v)+18,'ออกรอบ '+R.exitAt,{fill:COL.purple,weight:700});}}
let dragging=false;
function drawRates(r){const sv=$('f-draw');clear(sv);const W=640,H=220,x0=56,x1=W-16,y0=H-26,y1=20,LIM=0.0004;
  const X=i=>x0+i/90*(x1-x0),Y=v=>(y0+y1)/2-v/LIM*(y0-y1)/2;
  sv.appendChild(S('rect',{x:x0,y:y1,width:x1-x0,height:y0-y1,fill:cur==='วาดเอง'?'#f5f3ff':'#fff',stroke:COL.grid}));
  [LIM,LIM/2,0,-LIM/2,-LIM].forEach(v=>{sv.appendChild(S('line',{x1:x0,x2:x1,y1:Y(v),y2:Y(v),stroke:v===0?'#94a3b8':COL.grid}));
    T(sv,x0-6,Y(v)+4,nf(v*100,2)+'%',{anchor:'end',size:10.5});});
  const bw=(x1-x0)/90;r.forEach((v,i)=>{const vv=Math.max(-LIM,Math.min(LIM,v));sv.appendChild(S('rect',{x:X(i)+0.5,y:Math.min(Y(vv),Y(0)),width:Math.max(1,bw-1),
    height:Math.abs(Y(vv)-Y(0)),fill:v>=0?COL.green:COL.red}));});
  T(sv,x1,14,cur==='วาดเอง'?'โหมดวาดเอง: ลากบนกราฟ':'กด "วาดเอง" เพื่อแก้เส้นทาง',{anchor:'end',size:11,fill:COL.purple});
  sv.onpointerdown=e=>{if(cur!=='วาดเอง')return;dragging=true;sv.setPointerCapture(e.pointerId);paint(e);};
  sv.onpointermove=e=>{if(dragging)paint(e);};sv.onpointerup=()=>{dragging=false;};
  function paint(e){const b=sv.getBoundingClientRect(),px=(e.clientX-b.left)/b.width*W,py=(e.clientY-b.top)/b.height*H;
    const i=Math.max(0,Math.min(89,Math.floor((px-x0)/bw)));let v=((y0+y1)/2-py)/((y0-y1)/2)*LIM;v=Math.max(-LIM,Math.min(LIM,v));
    mine[i]=Math.round(v/0.00005)*0.00005;upd();}}
['f-k','f-crowd','f-hur'].forEach(i=>$(i).addEventListener('input',upd));
upd();
"""


# ───────────────────────── 3. reversion ─────────────────────────

REV_BODY = r"""
<div class="bx bb"><div class="bt">🎯 เครื่องมือนี้ตอบอะไร</div>
<p>"กลับแน่" กับ "กลับทันก่อนเงินหมด" เป็นคนละคำถาม φ บอกว่าทุกช่วงระยะห่างจากค่ากลางเหลือกี่ส่วน
แรงสะบัดบอกว่าแต่ละช่วงถูกเขย่าแรงแค่ไหน ส่วนต้นทุนกับช่วงถือบอกว่ามีเวลาและเงินให้รอเท่าไร
เครื่องมือนี้มีห้าส่วน: ค่าคาดหมายของเส้นทางที่คาด · พัดเส้นทางสุ่ม · เวลาแตะเป้า · กฎเดียวสามโลก · stepper ของการ์ดกติกา</p></div>

<div class="tool">
<h3>ตั้งค่า</h3>
<div class="ctrl">
<label for="r-phi">φ (สัดส่วนระยะห่างที่เหลือต่อช่วง)</label><span class="val" id="r-phiv"></span>
<input type="range" id="r-phi" min="0.5" max="1.05" step="0.01">
<label for="r-sd">แรงสะบัดต่อช่วง (หน่วยเดียวกับ X)</label><span class="val" id="r-sdv"></span>
<input type="range" id="r-sd" min="0" max="1.5" step="0.05">
<label for="r-x0">X ตอนเข้า</label><input type="number" id="r-x0" step="0.1">
<label for="r-n">ถือกี่ช่วง</label><input type="number" id="r-n" step="1" min="1" max="60">
<label for="r-sets">จำนวนชุด</label><input type="number" id="r-sets" step="1" min="1">
<label for="r-cost">ต้นทุนไปกลับ</label><input type="number" id="r-cost" step="0.1" min="0">
</div>
</div>

<div class="tool">
<h3>① ค่าคาดหมายเมื่อถือครบ (เส้นทางที่คาด ไม่มีสัญญาณรบกวน)</h3>
<p class="whyline">🔩 ทำไมต้องมีเครื่องมือนี้: φ ใกล้ 1 ดูเหมือน "ยังกลับ" แต่ในช่วงถือสั้น ๆ ระยะที่หดได้แทบไม่พอจ่ายต้นทุน</p>
<div class="kpi">
<div><div class="lb">X เมื่อครบช่วงถือ</div><span class="v" id="r-end"></span></div>
<div><div class="lb">กำไรก่อนต้นทุน</div><span class="v" id="r-gross" data-twin="ch13/ตารางphi/0.80/กำไรก่อนต้นทุน"></span></div>
<div><div class="lb">ค่าคาดหมายสุทธิ</div><span class="v big" id="r-net" data-twin="ch13/ตารางphi/0.80/สุทธิ4ช่วง"></span></div>
<div><div class="lb">ครึ่งชีวิต (ช่วง)</div><span class="v" id="r-hl" data-twin="ch13/ตารางphi/0.80/ครึ่งชีวิต"></span></div>
</div>
<div class="tw"><table id="r-phitbl"><tr><th class="num">φ</th><th class="num">X หลัง 1 ช่วง</th><th class="num">X เมื่อครบ</th><th class="num">สุทธิ</th><th class="num">ครึ่งชีวิต</th></tr></table></div>
<p class="src">🔢 ตัวเลขสมมติเพื่อสอน · short ตะกร้าที่ X ตอนเข้า · กำไร = จำนวนชุด × ระยะที่หด · สูตรเดียวกับแท็บ "ตาราง φ" ในสมุดงาน · แรงสะบัดไม่เปลี่ยนค่าคาดหมายเมื่อถือครบโดยไม่มีกฎออก</p>
</div>

<div class="tool">
<h3>② พัดเส้นทาง</h3>
<p class="whyline">🔩 ทำไมต้องมีเครื่องมือนี้: ค่าคาดหมายเป็นเส้นเดียว แต่คุณจะได้เดินแค่เส้นเดียวในพัด และเส้นนั้นอาจขึ้นก่อนลง</p>
<button type="button" class="btn pri" id="r-fanbtn">สุ่มพัดใหม่</button>
<svg class="chart" id="r-fan" viewBox="0 0 640 280" role="img" aria-label="พัดเส้นทาง X ที่สุ่มด้วย φ และแรงสะบัดที่เลือก"></svg>
<p class="src">🎲 จำลองในเบราว์เซอร์ — ตัวอย่างใหม่ทุกครั้ง ไม่ใช่ชุดในบท · เส้นม่วง = เส้นทางที่คาด · เส้นเขียวประ = เป้าออก · เส้นแดงประ = ระยะที่ขาดทุนถึงงบ</p>
</div>

<div class="tool">
<h3>③ เวลาแตะเป้า: จาก X = 2 ถึง X ≤ 1</h3>
<p class="whyline">🔩 ทำไมต้องมีเครื่องมือนี้: ครึ่งชีวิตเป็นค่าของเส้นทางที่คาด เวลาจริงที่แตะเป้ากระจายกว้างกว่านั้นมาก</p>
<button type="button" class="btn pri" id="r-fpbtn">จำลองใหม่</button>
<div class="tw"><table id="r-fptbl"><tr><th>ค่า</th><th class="num">จำลองตอนนี้</th><th class="num">ในบท (ชุดตายตัว)</th></tr></table></div>
<p class="src">🎲 จำลอง <span id="r-fpn"></span> เส้นในเบราว์เซอร์ ตัวเลขสุ่มของเบราว์เซอร์ต่างจากชุดสุ่มตายตัวในบท ค่าจึงขยับเล็กน้อยทุกครั้ง · คอลัมน์ "ในบท" มีเฉพาะสามกรณีที่บท 13 คำนวณไว้</p>
</div>

<div class="tool">
<h3>④ กฎเดียวสามโลก (การ์ดบท 12 ที่ X = 2 · ออก 0.5 · งบ −15 · ครบ 3 ช่วง)</h3>
<p class="whyline">🔩 ทำไมต้องมีเครื่องมือนี้: การ์ดใบเดียวกันให้ผลต่างกันสุดขั้วตาม φ ที่คุณไม่รู้ค่าจริง</p>
<button type="button" class="btn pri" id="r-3wbtn">จำลองใหม่</button>
<div class="tw"><table id="r-3w"><tr><th class="num">φ</th><th class="num">ออกเพราะเป้า %</th><th class="num">ออกเพราะงบ %</th><th class="num">ออกเพราะเวลา %</th><th class="num">ไม้กำไร %</th><th class="num">ค่าคาดหมายต่อไม้</th></tr></table></div>
<p class="src">🎲 จำลองในเบราว์เซอร์ <span id="r-3wn"></span> ไม้ต่อโลก ที่แรงสะบัดตามที่ตั้ง · ป้ายเทา = ค่าในบท 13 (แรงสะบัด 0.5 · ชุดสุ่มตายตัว) · ก่อนค่าถือ</p>
</div>

<div class="tool">
<h3>⑤ stepper กฎเข้า–ถือ–ออก</h3>
<p class="whyline">🔩 ทำไมต้องมีเครื่องมือนี้: ลำดับ ขาดทุน → สัญญาณ → เวลา และโหมดพักหลังออกเพราะงบ ต้องเห็นทีละช่วงถึงจะเชื่อ</p>
<p style="margin-bottom:4px">เส้นทาง X (คั่นด้วยจุลภาค · ช่วงแรกคือก่อนเข้า)</p>
<textarea class="path" id="s-x" rows="2"></textarea>
<p style="margin:8px 0 4px">ราคา B แต่ละช่วง (เว้นว่าง = B นิ่ง · ราคา A = X + 2 × B)</p>
<textarea class="path" id="s-b" rows="2"></textarea>
<div class="seg" id="s-presets"></div>
<div><button type="button" class="btn" id="s-step">ก้าวต่อไป</button><button type="button" class="btn pri" id="s-all">รันทั้งเส้น</button>
<button type="button" class="btn" id="s-reset">เริ่มใหม่</button></div>
<div><label><input type="checkbox" id="s-ok"> ตรวจครบแล้ว (เงื่อนไขกลับมาตามใบพัก)</label> <button type="button" class="btn" id="s-resume">ขอกลับมา</button>
<span id="s-resmsg" class="v"></span></div>
<div class="tw"><table id="s-tbl"><tr><th class="num">ช่วง</th><th class="num">X</th><th>สถานะก่อน</th><th>เหตุการณ์</th><th class="num">ช่วงที่ถือ</th><th class="num">ขา A</th><th class="num">ขา B</th><th class="num">สุทธิถ้าออกตอนนี้</th><th>สถานะหลัง</th></tr></table></div>
<div class="kpi">
<div><div class="lb">สุทธิไม้ล่าสุดที่ปิด</div><span class="v big" id="s-last" data-twin="ch12/เส้นทาง/3/สุทธิ"></span></div>
<div><div class="lb">ไม้ที่ปิด</div><span class="v" id="s-closed" data-twin="ch14/ไม้ที่ปิด"></span></div>
<div><div class="lb">ช่วงที่ถูกพักบล็อก</div><span class="v" id="s-block" data-twin="ch14/บล็อก"></span></div>
<div><div class="lb">สถานะตอนจบ</div><span class="v key" id="s-state"></span></div>
</div>
<p class="src">🔢 ตัวเลขสมมติเพื่อสอน · ตะกร้า 10 ชุด (short X = short A 10 · long B 20) · ค่าตั้งต้นคือเส้นทางในบท 14 · ก่อนค่าถือ</p>
<h3>อัตราชนะที่ต้องได้</h3>
<div class="ctrl">
<label for="w-win">กำไรเฉลี่ยของไม้ชนะ</label><input type="number" id="w-win" step="1">
<label for="w-loss">ขาดทุนเฉลี่ยของไม้แพ้</label><input type="number" id="w-loss" step="1">
</div>
<p>ต้องชนะอย่างน้อย <span class="v big" id="w-need" data-twin="ch12/ต้องชนะทศนิยม"></span> % ของไม้ที่ออกแบบชนะหรือแพ้</p>
<div class="tw"><table id="w-mix"><tr><th>สัดส่วนตอนจบ (เป้า / เวลา / งบ)</th><th class="num">ค่าคาดหมายต่อไม้</th></tr></table></div>
<p class="src">🔢 ตัวเลขสมมติเพื่อสอน · ผลสามตอนจบจากบท 12</p>
</div>
"""

REV_JS = r"""
const M=BOOK['บัญชีมิน'], C12=BOOK.ch12, C13=BOOK.ch13, C14=BOOK.ch14, G=C13['กติกาตารางphi'], CARD=M['การ์ด'], SETS=M['คู่']['ชุด'], CST=CARD['ต้นทุนเข้า']+CARD['ต้นทุนออก'];
setv('r-phi',C13['ตารางphi']['0.80'].phi);setv('r-sd',0.5);setv('r-x0',G['เริ่ม']);setv('r-n',G['ช่วงถือ']);setv('r-sets',G['ชุด']);setv('r-cost',G['ต้นทุน']);
setv('s-x',C14['เส้นทาง'].join(', '));setv('s-b','');setv('w-win',C12['เส้นทาง']['1']['สุทธิ']);setv('w-loss',C12['เส้นทาง']['3']['สุทธิ']);
function R(){return {phi:num('r-phi'),sd:num('r-sd'),x0:num('r-x0'),n:Math.max(1,Math.round(num('r-n'))),sets:num('r-sets'),cost:num('r-cost')};}
function hl(phi){return (phi>0&&phi<1)?Math.log(0.5)/Math.log(phi):null;}
function expect(p,phi){const end=p.x0*Math.pow(phi,p.n),g=p.sets*(p.x0-end);return {end:end,g:g,net:g-p.cost,x1:p.x0*phi};}
function upd1(){const p=R();$('r-phiv').textContent=nf(p.phi,2);$('r-sdv').textContent=nf(p.sd,2);
  const e=expect(p,p.phi);put('r-end',e.end,2);put('r-gross',e.g,2);put('r-net',e.net,2);const h=hl(p.phi);$('r-hl').textContent=h===null?'ไม่มี':nf(h,2);
  const t=$('r-phitbl');while(t.rows.length>1)t.deleteRow(1);
  Object.keys(C13['ตารางphi']).forEach(k=>{const ph=C13['ตารางphi'][k].phi,E=expect(p,ph),H=hl(ph),row=t.insertRow();
    row.innerHTML='<td class="num">'+nf(ph,2)+'</td><td class="num">'+nf(E.x1,2)+'</td><td class="num">'+nf(E.end,2)+
    '</td><td class="num"><span class="v'+(E.net<0?' neg':'')+'" data-twin="ch13/ตารางphi/'+k+'/สุทธิ4ช่วง">'+nf(E.net,2)+'</span></td><td class="num">'+(H===null?'ไม่มี':nf(H,2))+'</td>';});
  twins();}
function fan(){const p=R(),sv=$('r-fan');clear(sv);const W=640,H=280,x0=44,x1=W-14,N=Math.max(12,Math.min(60,p.n*4)),y0=H-28,y1=24;
  const paths=[];for(let k=0;k<40;k++){let x=p.x0;const a=[x];for(let t=0;t<N;t++){x=p.phi*x+p.sd*gauss();a.push(x);}paths.push(a);}
  const all=[].concat(...paths);let ymax=Math.max(p.x0+1,...all),ymin=Math.min(-0.5,...all);ymax=Math.min(ymax,p.x0+6);ymin=Math.max(ymin,-6);
  const X=t=>x0+t/N*(x1-x0),Y=v=>y0-(Math.max(ymin,Math.min(ymax,v))-ymin)/(ymax-ymin)*(y0-y1);
  T(sv,10,16,'X ของตะกร้า '+N+' ช่วง · φ '+nf(p.phi,2)+' · แรงสะบัด '+nf(p.sd,2),{weight:700,fill:COL.ink});
  const stopX=p.x0+(Math.abs(CARD['งบขาดทุนสุทธิ'])-CARD['ต้นทุนเข้า']-CARD['ต้นทุนออก'])/p.sets;
  [[0,'#94a3b8','ค่ากลาง 0'],[CARD['ออก'],COL.green,'ออก '+fj(CARD['ออก'])],[stopX,COL.red,'งบ −15 ที่ X '+nf(stopX,1)]].forEach(([v,c,l])=>{
    sv.appendChild(S('line',{x1:x0,x2:x1,y1:Y(v),y2:Y(v),stroke:c,'stroke-dasharray':v===0?'':'5 4'}));T(sv,x1-2,Y(v)-4,l,{anchor:'end',size:11,fill:c});});
  paths.forEach(a=>sv.appendChild(S('polyline',{points:a.map((v,t)=>X(t)+','+Y(v)).join(' '),fill:'none',stroke:COL.grey,'stroke-width':1,opacity:.55})));
  const ex=[];for(let t=0;t<=N;t++)ex.push(p.x0*Math.pow(p.phi,t));
  sv.appendChild(S('polyline',{points:ex.map((v,t)=>X(t)+','+Y(v)).join(' '),fill:'none',stroke:COL.purple,'stroke-width':3}));
  [0,Math.round(N/2),N].forEach(t=>T(sv,X(t),y0+16,'ช่วง '+t,{anchor:'middle',size:11}));}
function firstPassage(phi,sd,M_){const MAX=phi>=1?1000:5000,ts=[];let up=0,inHalf=0;const h=hl(phi);
  for(let k=0;k<M_;k++){let x=2,t=0,touched=false;while(t<MAX){x=phi*x+sd*gauss();t++;if(x>=3)touched=true;if(x<=1)break;}ts.push(t);if(touched)up++;if(h!==null&&t<=h)inHalf++;}
  ts.sort((a,b)=>a-b);const n=ts.length,mean=ts.reduce((a,b)=>a+b,0)/n;
  return {med:ts[Math.floor(n/2)],mean:mean,p90:ts[Math.floor(0.9*n)],in4:ts.filter(t=>t<=4).length/n*100,up:up/n*100,half:h===null?null:inHalf/n*100,cap:ts.filter(t=>t>=MAX).length/n*100,MAX:MAX};}
function fp(){const p=R(),Mn=p.phi>=1?5000:20000;$('r-fpn').textContent=nf(Mn,0);const F=firstPassage(p.phi,p.sd,Mn);
  const bk=C13['แตะเป้า'].find(d=>Math.abs(d.phi-p.phi)<1e-9&&Math.abs(d['แรงสะบัด']-p.sd)<1e-9);
  const rows=[['มัธยฐานช่วงจนแตะ',nf(F.med,0),bk&&fj(bk['มัธยฐานช่วง'])],['เฉลี่ยช่วงจนแตะ',nf(F.mean,1),bk&&fj(bk['เฉลี่ยช่วง'])],
    ['90% แตะภายใน (ช่วง)',nf(F.p90,0),bk&&fj(bk['p90ช่วง'])],['จบใน 4 ช่วง (%)',nf(F.in4,1),bk&&fj(bk['จบใน4ช่วงเปอร์เซ็นต์'])],
    ['แตะก่อนครึ่งชีวิต (%)',F.half===null?'ไม่มีครึ่งชีวิต':nf(F.half,1),bk&&fj(bk['แตะก่อนครึ่งชีวิตเปอร์เซ็นต์'])],
    ['ขึ้นถึง 3 ก่อนแตะ (%)',nf(F.up,1),bk&&fj(bk['ขึ้นถึง3ก่อนเปอร์เซ็นต์'])]];
  if(F.cap>0)rows.push(['ไม่แตะเลยใน '+nf(F.MAX,0)+' ช่วง (%)',nf(F.cap,1),null]);
  const t=$('r-fptbl');while(t.rows.length>1)t.deleteRow(1);
  rows.forEach(r=>{const row=t.insertRow();row.innerHTML='<td>'+r[0]+'</td><td class="num v">'+r[1]+'</td><td class="num">'+(r[2]||'—')+'</td>';});}
function world(phi,sd,n){const st=2,res={'งบ':0,'เป้า':0,'เวลา':0};let tot=0,wins=0;
  for(let k=0;k<n;k++){let x=st;for(let t=1;t<=3;t++){x=phi*x+sd*gauss();const liq=SETS*(st-x)-CST;let r=null;
    if(liq<=CARD['งบขาดทุนสุทธิ'])r='งบ';else if(x<=CARD['ออก'])r='เป้า';else if(t>=3)r='เวลา';
    if(r){res[r]++;tot+=liq;if(liq>0)wins++;break;}}}
  return {t:res['เป้า']/n*100,b:res['งบ']/n*100,ti:res['เวลา']/n*100,w:wins/n*100,ev:tot/n};}
function w3(){const p=R(),n=20000;$('r-3wn').textContent=nf(n,0);const t=$('r-3w');while(t.rows.length>1)t.deleteRow(1);
  Object.keys(C13['กฎเดียวสามโลก']).forEach(k=>{const b=C13['กฎเดียวสามโลก'][k],W=world(+k,p.sd,n),row=t.insertRow();
    const c=(v,d,bv)=>'<td class="num"><span class="v">'+nf(v,d)+'</span><span class="bk">ในบท '+fj(bv)+'</span></td>';
    row.innerHTML='<td class="num">'+k+'</td>'+c(W.t,1,b['ออกเพราะเป้าเปอร์เซ็นต์'])+c(W.b,1,b['ออกเพราะงบเปอร์เซ็นต์'])+c(W.ti,1,b['ออกเพราะเวลาเปอร์เซ็นต์'])+
      c(W.w,1,b['ไม้กำไรเปอร์เซ็นต์'])+c(W.ev,2,b['ค่าคาดหมายต่อไม้ก่อนค่าถือ']);});}
// ── stepper: พอร์ตเครื่องสถานะการ์ดบท 12 (ลำดับ ขาดทุน → สัญญาณ → เวลา · ออกเพราะงบ → พัก) ──
const ST={none:'ว่าง',short:'ถือ short',long:'ถือ long'};
let pol,xs,bs,bar;
function parse(id){return $(id).value.split(/[,\s]+/).map(s=>s.replace('−','-')).filter(s=>s!=='').map(Number).filter(v=>isFinite(v));}
function state(){return pol.pos?(pol.pos.side<0?ST.short:ST.long)+(pol.paused?' (พักเปิดใหม่)':''):(pol.paused?'ว่าง · พัก':ST.none);}
function reset(){xs=parse('s-x');const b=parse('s-b');const b0=M['คู่'].B;bs=xs.map((_,i)=>b.length?(b[i]!==undefined?b[i]:b[b.length-1]):b0);
  pol={pos:null,paused:false,trades:[],blocked:0};bar=0;const t=$('s-tbl');while(t.rows.length>1)t.deleteRow(1);$('s-resmsg').textContent='';out();}
function step(){if(bar>=xs.length)return;const x=xs[bar],b=bs[bar],a=x+M['คู่'].h*b,before=state();let ev='',el='',la='',lb='',liq=null;
  if(pol.pos){const p=pol.pos;el=bar-p.bar;const qa=p.side*SETS,qb=-p.side*SETS*M['คู่'].h;
    la=qa*(a-p.a);lb=qb*(b-p.b);liq=la+lb-CARD['ต้นทุนเข้า']-CARD['ต้นทุนออก'];
    const rec=p.side<0?x<=CARD['ออก']:x>=-CARD['ออก'];
    const r=liq<=CARD['งบขาดทุนสุทธิ']?'งบ':rec?'เป้า':el>=CARD['ช่วงถือสูงสุด']?'เวลา':null;
    if(r){pol.trades.push({net:liq,r:r});pol.pos=null;if(r==='งบ')pol.paused=true;ev='ออก: '+r;}else ev='ถือ';}
  else if(pol.paused){ev='พัก (ไม่เปิดไม้ใหม่)';pol.blocked++;}
  else if(x>=CARD['เข้า']){pol.pos={side:-1,bar:bar,a:a,b:b};ev='เข้า short';}
  else if(x<=-CARD['เข้า']){pol.pos={side:1,bar:bar,a:a,b:b};ev='เข้า long';}
  else ev='รอ';
  const row=$('s-tbl').insertRow();const c=v=>'<td class="num'+(typeof v==='number'&&v<0?' neg':'')+'">'+(typeof v==='number'?nf(v,2):v)+'</td>';
  row.innerHTML='<td class="num">'+bar+'</td>'+c(x)+'<td>'+before+'</td><td><strong>'+ev+'</strong></td>'+(el===''?'<td></td>':'<td class="num">'+el+'</td>')+
    (la===''?'<td></td><td></td><td></td>':c(la)+c(lb)+c(liq))+'<td>'+state()+'</td>';bar++;out();}
function out(){const tr=pol.trades;$('s-last').textContent=tr.length?nf(tr[tr.length-1].net,0):'—';$('s-last').classList.toggle('neg',tr.length&&tr[tr.length-1].net<0);
  $('s-closed').textContent=tr.length;$('s-block').textContent=pol.blocked;$('s-state').textContent=state();twins();}
$('s-step').onclick=step;$('s-all').onclick=()=>{while(bar<xs.length)step();};$('s-reset').onclick=reset;
$('s-resume').onclick=()=>{let msg;if(!pol.paused)msg='ไม่ได้อยู่ในโหมดพัก';else if(pol.pos)msg='ต้องว่างก่อน';else if(!$('s-ok').checked)msg='ยังไม่ผ่านการตรวจ — กลับมาไม่ได้';
  else{pol.paused=false;msg='กลับมาแล้ว (ว่าง · เปิดไม้ใหม่ได้)';}$('s-resmsg').textContent=msg;out();};
const pr=$('s-presets');
[['บท 14',C14['เส้นทาง']]].concat(Object.keys(C12['เส้นทาง']).map(k=>['บท 12 เส้นทาง '+k,C12['เส้นทาง'][k].X])).forEach(([n,a])=>{
  const b=document.createElement('button');b.type='button';b.textContent=n;b.onclick=()=>{setv('s-x',a.join(', '));setv('s-b','');reset();while(bar<xs.length)step();};pr.appendChild(b);});
['s-x','s-b'].forEach(i=>$(i).addEventListener('change',reset));
function updw(){const w=num('w-win'),l=num('w-loss');put('w-need',Math.abs(l)/(w+Math.abs(l))*100,2);
  const o=BOOK['บัญชีมิน']&&C12['สัดส่วนตอนจบ'];const t=$('w-mix');while(t.rows.length>1)t.deleteRow(1);
  const outc=[C12['เส้นทาง']['1']['สุทธิ'],C12['เส้นทาง']['2']['สุทธิ'],C12['เส้นทาง']['3']['สุทธิ']];
  ['หลัก','เทียบ'].forEach(k=>{const mx=C12['สัดส่วนตอนจบ'][k]['สัดส่วน'];const ev=mx.reduce((s,v,i)=>s+v/100*outc[i],0);const row=t.insertRow();
    row.innerHTML='<td>'+mx.join(' / ')+'</td><td class="num"><span class="v'+(ev<0?' neg':'')+'" data-twin="ch12/สัดส่วนตอนจบ/'+k+'/ค่าคาดหมาย">'+nf(ev,2)+'</span></td>';});twins();}
['w-win','w-loss'].forEach(i=>$(i).addEventListener('input',updw));
['r-phi','r-sd','r-x0','r-n','r-sets','r-cost'].forEach(i=>$(i).addEventListener('input',()=>{upd1();fan();}));
['r-phi','r-sd'].forEach(i=>$(i).addEventListener('change',()=>{fp();w3();}));
$('r-fanbtn').onclick=fan;$('r-fpbtn').onclick=fp;$('r-3wbtn').onclick=w3;
upd1();fan();fp();w3();reset();while(bar<xs.length)step();updw();
"""


# ───────────────────────── 4. fakepair ─────────────────────────

FAKE_BODY = r"""
<div class="bx bb"><div class="bt">🎯 เครื่องมือนี้ตอบอะไร</div>
<p>ค้นคู่เหรียญจำนวนมากแล้วเลือกคู่ที่ "ข้ามค่ากลางบ่อยที่สุด" ในช่วงเลือก ฟังดูเหมือนหาคู่ที่ดีที่สุด
แต่ถ้าทุกคู่ไม่มีเชือกผูกเลย ผู้ชนะคือคู่ที่บังเอิญดูดีที่สุด แล้วช่วงทดสอบจะเปิดโปงมัน
เครื่องมือนี้สร้างคู่ไม่มีเชือก (สองราคาเดินตามปัจจัยร่วมแต่ไม่มีอะไรดึงส่วนต่างกลับ) กับคู่มีเชือก
จัดอันดับด้วยครั้งข้ามค่ากลาง แล้วให้คุณดูช่วงทดสอบเอง</p></div>

<div class="tool">
<h3>① ชุดในบท 10 (เปิดมาเห็นค่าตรงบท)</h3>
<p class="whyline">🔩 ทำไมต้องมีเครื่องมือนี้: อันดับหนึ่งจากการค้นคือผลของการค้น ไม่ใช่หลักฐานว่ามีเชือก</p>
<div class="kpi">
<div><div class="lb">คู่อันดับ 1: ครั้งข้ามค่ากลาง (ช่วงเลือก)</div><span class="v" id="b-cross" data-twin="ch10/อันดับ1/ข้ามค่ากลาง"></span></div>
<div><div class="lb">คู่อันดับ 1: % วันในกรอบ (ช่วงทดสอบ)</div><span class="v big" id="b-in" data-twin="ch10/อันดับ1/ในกรอบ"></span></div>
<div><div class="lb">คู่อันดับ 1: ระยะไกลสุด (ช่วงทดสอบ)</div><span class="v" id="b-max" data-twin="ch10/อันดับ1/ระยะสูงสุด"></span></div>
<div><div class="lb">คู่มีเชือกตัวแรก: ครั้งข้าม</div><span class="v" id="g-cross" data-twin="ch10/คู่จริงตัวแรก/ข้ามค่ากลาง"></span></div>
<div><div class="lb">คู่มีเชือกตัวแรก: % ในกรอบ</div><span class="v big" id="g-in" data-twin="ch10/คู่จริงตัวแรก/ในกรอบ"></span></div>
<div><div class="lb">คู่มีเชือกตัวแรก: ระยะไกลสุด</div><span class="v" id="g-max" data-twin="ch10/คู่จริงตัวแรก/ระยะสูงสุด"></span></div>
</div>
<svg class="chart" id="b-svg" viewBox="0 0 640 300" role="img" aria-label="z ของคู่อันดับ 1 ในบท 10 ช่วงเลือกและช่วงทดสอบ"></svg>
<p class="src">🎲 จำลอง (ชุดสุ่มตายตัวของบท 10 · ผลนิ่งเมื่อสุ่มใหม่ 30 ชุด) · ตัวเลขข้างบนคิดใหม่ในเบราว์เซอร์จากเส้นทางที่บทเก็บไว้ · ไม่ใช่เหรียญจริง</p>
<div class="tw"><table id="b-tbl"><tr><th>กลุ่ม (ชุดในบท)</th><th class="num">ครั้งข้ามเฉลี่ย</th><th class="num">% ในกรอบ ช่วงทดสอบ</th><th class="num">ระยะไกลสุดเฉลี่ย</th></tr></table></div>
<p class="src">🎲 จำลอง · ค้น 200 คู่ไม่มีเชือก × 500 วัน (ช่วงเลือก 250 วัน) · คู่มีเชือก 10 คู่ · มัธยฐานเมื่อสุ่มใหม่ 30 ชุด: 10 อันดับแรกอยู่ในกรอบ <span class="v" data-twin="seed_robustness/ch10/ในกรอบ/มัธยฐาน" id="b-med"></span></p>
</div>

<div class="tool">
<h3>② ค้นใหม่ด้วยตัวเลขสุ่มของคุณ</h3>
<div class="ctrl">
<label for="z-n">จำนวนคู่ไม่มีเชือกที่ค้น</label><input type="number" id="z-n" min="10" max="1000" step="10">
<label for="z-top">คัดอันดับต้น ๆ กี่คู่</label><input type="number" id="z-top" min="1" max="50" step="1">
<label for="z-gen">จำนวนคู่มีเชือกไว้เทียบ</label><input type="number" id="z-gen" min="1" max="100" step="1">
</div>
<div><label><input type="checkbox" id="z-leak"> กรอบรั่ว: คิดค่ากลางและระยะแกว่งจากทั้ง 500 วัน (แอบเห็นช่วงทดสอบ)</label></div>
<button type="button" class="btn pri" id="z-run">ค้นใหม่ (สุ่มชุดใหม่)</button>
<p class="src" id="z-note">ยังไม่ได้ค้น — กดปุ่มเพื่อสร้างชุดใหม่ ผลจะต่างจากชุดในบททุกครั้ง เพราะตัวเลขสุ่มของเบราว์เซอร์ไม่ใช่ชุดตายตัวของบท</p>
<div class="tw"><table id="z-tbl"><tr><th>กลุ่ม (ชุดใหม่)</th><th class="num">ครั้งข้ามเฉลี่ย</th><th class="num">% ในกรอบ ช่วงทดสอบ</th><th class="num">ระยะไกลสุดเฉลี่ย</th><th class="num">ในบท (% ในกรอบ)</th></tr></table></div>
<p class="src">🎲 จำลองในเบราว์เซอร์ — ตัวอย่างใหม่ ไม่ใช่ชุดในบท · ไม่มีเชือก: ปัจจัยร่วมเดินสุ่ม + ส่วนเฉพาะเดินสุ่มทั้งสองเหรียญ · มีเชือก: ส่วนต่างถูกดึงกลับทุกวัน</p>
<svg class="chart" id="z-svg" viewBox="0 0 640 300" role="img" aria-label="z ของคู่อันดับ 1 จากการค้นใหม่"></svg>
<p class="src">🎲 จำลองในเบราว์เซอร์ · ก่อนกดค้นใหม่ กราฟนี้แสดงคู่มีเชือกตัวแรกของบท 10 ไว้เทียบ</p>
</div>

<div class="tool">
<h3>③ ลองกี่ครั้ง ถึงเจอของบังเอิญ</h3>
<p>ถ้าแต่ละคู่มีโอกาส 5% ที่จะผ่านเกณฑ์โดยบังเอิญ การลองหลายคู่ทำให้โอกาสเจออย่างน้อยหนึ่งคู่ที่ "ผ่าน" สูงขึ้นเร็วมาก</p>
<div class="tw"><table id="t-tbl"><tr><th class="num">ลองกี่คู่</th><th class="num">โอกาสเจอคู่ผ่านโดยบังเอิญ (%)</th></tr></table></div>
<p class="src">🔢 ตัวเลขสมมติเพื่อสอน · โอกาส = 1 − 0.95 ยกกำลังจำนวนคู่ที่ลอง</p>
</div>

<div class="bx ba"><div class="bt">💡 อ่านผลอย่างไร</div>
<ul>
<li>คู่ที่ข้ามค่ากลางบ่อยที่สุดในช่วงเลือกมักอยู่ในกรอบช่วงทดสอบแย่กว่าคู่มีเชือกที่ไม่ได้ถูกคัด</li>
<li>เปิดสวิตช์กรอบรั่วแล้วคู่ไม่มีเชือกจะดูดีขึ้นทันที เพราะไม้บรรทัดถูกวัดจากอนาคตที่มันกำลังถูกทดสอบ</li>
<li>เครื่องมือนี้ตอบว่า "คัดแล้วหลอกได้แค่ไหน" ไม่ได้ตอบว่าคู่จริงของคุณมีเชือก — นั่นต้องใช้คำถาม "อะไรดึงสองราคากลับ" ในบท 9</li>
</ul></div>
<p>คู่กับเครื่องมือในคลัง: <a href="nq-tool-randomness.html">จริงหรือสุ่ม</a> · <a href="tool-deflated-sharpe.html">backtest กำลังโกหกไหม</a></p>
"""

FAKE_JS = r"""
const C10=BOOK.ch10, SR=BOOK.seed_robustness;
const ND=C10['ค้น']['วันทั้งหมด'], NF=C10['ค้น']['วันช่วงเลือก'];
setv('z-n',C10['ค้น']['คู่ที่ค้น']);setv('z-top',C10['ค้น']['คัด']);setv('z-gen',C10['ค้น']['คู่จริง']);
function zstats(sp,nf,leak){const f=leak?sp:sp.slice(0,nf);const m=f.reduce((a,b)=>a+b,0)/f.length;
  const sd=Math.sqrt(f.reduce((a,b)=>a+(b-m)*(b-m),0)/(f.length-1));const z=sp.map(x=>(x-m)/sd);
  let cross=0;for(let i=1;i<nf;i++)if((z[i]>0)!==(z[i-1]>0))cross++;const test=z.slice(nf);
  return {z:z,cross:cross,inband:test.filter(v=>Math.abs(v)<=2).length/test.length*100,maxz:Math.max(...test.map(Math.abs))};}
function rw(n,sd){let x=0;const o=new Array(n);for(let i=0;i<n;i++){x+=sd*gauss();o[i]=x;}return o;}
function ar1(n,phi,sd){let x=0;const o=new Array(n);for(let i=0;i<n;i++){x=phi*x+sd*gauss();o[i]=x;}return o;}
function pairH(){const c=rw(ND,0.03),u=rw(ND,0.01),v=rw(ND,0.01);return c.map((ci,i)=>(ci+u[i])-(ci+v[i]));}
function pairC(){const c=rw(ND,0.03),u=rw(ND,0.01),e=ar1(ND,0.9,0.03);return c.map((ci,i)=>{const a=ci+u[i];return a-(a+e[i]);});}
function zplot(svg,z,title,color){clear(svg);const W=640,H=300,x0=40,x1=W-12,y0=H-30,y1=26;
  const lim=Math.max(3,Math.ceil(Math.max(...z.map(Math.abs))));const X=i=>x0+i/(z.length-1)*(x1-x0),Y=v=>y0-(v+lim)/(2*lim)*(y0-y1);
  T(svg,10,16,title,{weight:700,fill:COL.ink});
  svg.appendChild(S('rect',{x:X(NF),y:y1,width:x1-X(NF),height:y0-y1,fill:'#f8fafc'}));
  [[2,COL.green],[-2,COL.green],[0,'#94a3b8']].forEach(([v,c])=>{svg.appendChild(S('line',{x1:x0,x2:x1,y1:Y(v),y2:Y(v),stroke:c,'stroke-dasharray':v?'5 4':''}));
    T(svg,x0-6,Y(v)+4,(v>0?'+':v<0?'−':'')+Math.abs(v),{anchor:'end',size:11});});
  svg.appendChild(S('line',{x1:X(NF),x2:X(NF),y1:y1,y2:y0,stroke:COL.ink}));
  T(svg,(x0+X(NF))/2,y0+18,'ช่วงเลือก '+NF+' วัน',{anchor:'middle',size:11.5});T(svg,(X(NF)+x1)/2,y0+18,'ช่วงทดสอบ',{anchor:'middle',size:11.5,weight:700});
  svg.appendChild(S('polyline',{points:z.slice(0,NF+1).map((v,i)=>X(i)+','+Y(v)).join(' '),fill:'none',stroke:COL.grey,'stroke-width':1.3}));
  svg.appendChild(S('polyline',{points:z.slice(NF).map((v,i)=>X(i+NF)+','+Y(v)).join(' '),fill:'none',stroke:color,'stroke-width':1.6}));
  let im=NF;for(let i=NF;i<z.length;i++)if(Math.abs(z[i])>Math.abs(z[im]))im=i;
  svg.appendChild(S('circle',{cx:X(im),cy:Y(z[im]),r:5,fill:COL.purple}));T(svg,X(im)+(im>z.length*0.8?-8:8),Y(z[im])+(z[im]<0?16:-8),'ไกลสุด '+nf(z[im],2),{fill:COL.purple,weight:700,anchor:im>z.length*0.8?'end':'start'});}
// ① ชุดในบท: คิดใหม่จากเส้นทางที่บทเก็บไว้
const bz=zstats(C10['กราฟ']['อันดับ1'],NF,false), gz=zstats(C10['กราฟ']['คู่จริง'],NF,false);
$('b-cross').textContent=nf(bz.cross,0);$('b-in').textContent=nf(bz.inband,1);$('b-max').textContent=nf(bz.maxz,2);
$('g-cross').textContent=nf(gz.cross,0);$('g-in').textContent=nf(gz.inband,1);$('g-max').textContent=nf(gz.maxz,2);
$('b-med').textContent=fj(SR.ch10['ในกรอบ']['มัธยฐาน']);
zplot($('b-svg'),bz.z,'คู่อันดับ 1 จาก 200 คู่ (ชุดในบท)',COL.red);
zplot($('z-svg'),gz.z,'คู่มีเชือกตัวแรก (ชุดในบท)',COL.blue);
const bt=$('b-tbl');[['ทั้ง 200 คู่','ทั้ง200คู่','ระยะสูงสุดเฉลี่ย'],['10 อันดับแรก','10อันดับแรก','ระยะสูงสุดเฉลี่ย'],['คู่มีเชือก 10 คู่','คู่จริง','ระยะสูงสุดเฉลี่ย']].forEach(([n,k,mk])=>{
  const d=C10[k],r=bt.insertRow();r.innerHTML='<td>'+n+'</td><td class="num">'+fj(d['ข้ามค่ากลาง'])+'</td><td class="num">'+fj(d['ในกรอบ'])+'</td><td class="num">'+fj(d[mk])+'</td>';});
// ③
const tt=$('t-tbl');Object.keys(C10['ลองหลายครั้ง']).forEach(n=>{const r=tt.insertRow();
  r.innerHTML='<td class="num">'+n+'</td><td class="num"><span class="v" data-twin="ch10/ลองหลายครั้ง/'+n+'">'+nf((1-Math.pow(0.95,+n))*100,1)+'</span></td>';});
// ②
function avg(a,k){return a.reduce((s,r)=>s+r[k],0)/a.length;}
function search(){const n=Math.max(10,Math.round(num('z-n'))),top=Math.max(1,Math.min(n,Math.round(num('z-top')))),gn=Math.max(1,Math.round(num('z-gen'))),leak=$('z-leak').checked;
  const H=[];for(let i=0;i<n;i++){const sp=pairH();const s=zstats(sp,NF,false);const L=leak?zstats(sp,NF,true):s;H.push({cross:s.cross,inband:L.inband,maxz:L.maxz,z:L.z});}
  const Gs=[];for(let i=0;i<gn;i++){const sp=pairC();const s=zstats(sp,NF,false);const L=leak?zstats(sp,NF,true):s;Gs.push({cross:s.cross,inband:L.inband,maxz:L.maxz,z:L.z});}
  const sorted=H.slice().sort((a,b)=>b.cross-a.cross),best=sorted.slice(0,top);
  const t=$('z-tbl');while(t.rows.length>1)t.deleteRow(1);
  const rows=[['ทั้ง '+n+' คู่ไม่มีเชือก',H,leak?C10['กรอบรั่ว']['ไม่มีเชือก']:C10['ทั้ง200คู่']['ในกรอบ']],['อันดับต้น '+top+' คู่',best,leak?null:C10['10อันดับแรก']['ในกรอบ']],
    ['คู่มีเชือก '+gn+' คู่',Gs,leak?C10['กรอบรั่ว']['มีเชือก']:C10['คู่จริง']['ในกรอบ']],['อันดับ 1',[sorted[0]],leak?null:C10['อันดับ1']['ในกรอบ']]];
  rows.forEach(([nm,a,bk])=>{const r=t.insertRow();r.innerHTML='<td>'+nm+'</td><td class="num">'+nf(avg(a,'cross'),1)+'</td><td class="num v">'+nf(avg(a,'inband'),1)+
    '</td><td class="num">'+nf(avg(a,'maxz'),2)+'</td><td class="num">'+(bk===null?'—':fj(bk))+'</td>';});
  const pass=H.filter(r=>r.inband>=85).length/H.length*100,cut=Gs.filter(r=>r.inband<85).length/Gs.length*100;
  $('z-note').textContent='ตัวอย่างใหม่ ไม่ใช่ชุดในบท'+(leak?' · กรอบรั่วเปิดอยู่':'')+' · เกณฑ์ "อยู่ในกรอบ ≥ 85%" ปล่อยคู่ไม่มีเชือกผ่าน '+nf(pass,1)+'% (ในบท '+
    fj(C10['เกณฑ์ในกรอบ85']['ปล่อยคู่ปลอม'])+'%) และตัดคู่มีเชือกทิ้ง '+nf(cut,0)+'% (ในบท '+fj(C10['เกณฑ์ในกรอบ85']['ตัดคู่จริง'])+'%)';
  zplot($('z-svg'),sorted[0].z,'คู่อันดับ 1 จาก '+n+' คู่ (ชุดใหม่'+(leak?' · กรอบรั่ว':'')+')',COL.red);}
$('z-run').onclick=search;
twins();
"""


# ───────────────────────── hub ─────────────────────────

def hub_body(fig):
    existing = [
        ("nq-tool-breakeven.html", "เส้นเสมอตัวของคุณ", "ต้องชนะกี่ % ถึงจะไม่ขาดทุน เมื่อจ่ายค่าผ่านทางทุกไม้", "1, 11"),
        ("nq-tool-ruin.html", "ขนาดไม้กับการอยู่รอด", "ใส่เท่าไรถึงยังอยู่ในเกมเมื่อเจอวันแย่ติดกัน", "4, 16"),
        ("nq-tool-samplesize.html", "ต้องเทรดกี่ไม้ถึงจะรู้", "ผลที่มีตอนนี้พิสูจน์อะไรได้แล้ว และต้องอีกกี่ไม้", "15"),
        ("nq-tool-randomness.html", "จริงหรือสุ่ม", "แยกกราฟตลาดจริงออกจากการโยนเหรียญได้จริงไหม", "10"),
        ("tool-deflated-sharpe.html", "backtest กำลังโกหกไหม",
         "ลองหลายแบบแล้วเลือกตัวที่ดีที่สุด ผลดีจะหดเหลือเท่าไร · Sharpe = ผลตอบแทนเฉลี่ยต่อความผันผวน (เล่มนี้ไม่สอน ใช้อ่านเครื่องมือนี้เท่านั้น)", "15"),
        ("tool-diversification.html", "กระจายความเสี่ยง", "ถือหลายคู่ช่วยได้แค่ไหนเมื่อคู่ขยับไปด้วยกัน", "8, 17"),
        ("tool-carry-blowup.html", "carry ที่ระเบิด", "carry ของค่าเงิน กำไรเล็กสม่ำเสมอกับหางที่ระเบิด (คนละเรื่องกับ basis)", "1, 4, 17"),
    ]
    for f, *_ in existing:
        if not os.path.exists(os.path.join(B.DOCS, f)):
            raise SystemExit(f"ไม่มีไฟล์ {f} ใน docs/ — เอาออกจากรายการ hub")
    rows_new = [
        ("sab-tool-carry.html", "บันได carry · ปิดหรือถือ · สองกระเป๋า",
         "จาก % บนจอถึงส่วนเกินในมือ · วันที่ N ควรปิดไหม · กันชนเงินสดเมื่อราคาวิ่งสวน · basis หดเมื่อคนแห่มา", "4, 5, 6"),
        ("sab-tool-funding.html", "funding หลายเส้นทาง",
         "สี่เส้นทาง + วาดเอง · กฎติดลบ k รอบแล้วออก · maker กับ taker · อัตราถูกแย่ง", "7"),
        ("sab-tool-reversion.html", "แรงดึงกลับ: กลับทันไหม",
         "φ แรงสะบัด ต้นทุน ช่วงถือ → ค่าคาดหมาย พัดเส้นทาง เวลาแตะเป้า กฎเดียวสามโลก · stepper การ์ดกติกา", "12, 13, 14"),
        ("sab-tool-fakepair.html", "คู่ปลอมจากการค้น",
         "ค้นหลายคู่ จัดอันดับด้วยครั้งข้าม ดูช่วงทดสอบ สุ่มชุดใหม่ สวิตช์กรอบรั่ว", "9, 10"),
    ]
    tr = lambda r: (f'<tr><td><a href="{r[0]}"><strong>{r[1]}</strong></a></td><td>{r[2]}</td>'  # noqa: E731
                    f'<td class="nw">บท {r[3]}</td></tr>')
    return f"""
<div class="bx bb"><div class="bt">🧭 วิธีใช้</div>
<p>ไม่มีบทใดต้องพึ่งเครื่องมือ — ทุกบทลงมือได้ด้วยตารางในบท ใบงาน และแท็บในสมุดงาน
เครื่องมือมีไว้ให้เปลี่ยนตัวเลขเองแล้วเห็นว่าอะไรขยับ ค่าตั้งต้นทุกหน้าคือตัวเลขของมินในบท และมีป้ายเทา "ในบท" วางข้างตัวเลขสดให้เทียบ</p>
<p>ถ้ามีเวลาสิบนาที เริ่มที่ <a href="sab-tool-carry.html">บันได carry</a> เพราะเป็นบันไดที่ทั้งเล่มใช้ซ้ำกับ funding และคู่เหรียญ</p></div>

<h2>เครื่องมือของเล่มนี้</h2>
<div class="tw"><table>
<tr><th>เครื่องมือ</th><th>ตอบคำถามอะไร</th><th class="nw">คู่กับ</th></tr>
{''.join(tr(r) for r in rows_new)}
</table></div>
<p class="src">🔢 ตัวเลขสมมติเพื่อสอน และ 🎲 จำลอง — ทุกหน้าบอกที่มาใต้ตารางและกราฟ · หน้าที่สุ่มบอกชัดว่าตัวเลขสุ่มของเบราว์เซอร์ต่างจากชุดตายตัวในบท</p>

<h2>สมุดงาน 8 แท็บ</h2>
<div class="bx bg"><div class="bt">📒 <a href="sab-workbook.xlsx">sab-workbook.xlsx</a></div>
<p>สูตรสดทุกช่อง ช่องสีเหลืองคือช่องที่ใส่เอง ค่าตั้งต้นคือตัวอย่างของมิน</p>
<ul>
<li><strong>วิเคราะห์คู่</strong> — วางราคาปิดสองเหรียญ → X · ค่ากลางและระยะแกว่งของช่วงเลือก · z · % วันในกรอบ · ครั้งข้าม · correlation · φ และครึ่งชีวิต · ไม้ตามการ์ดบท 12 (บท 9, 10, 12, 13, 18)</li>
<li><strong>beta และระยะแกว่ง</strong> — วันที่ BTC ขยับเกิน 2% → beta · exposure สามวิธี · beta เปลี่ยนตอนตลาดลงแรง · ปัด lot (บท 8)</li>
<li><strong>ต้นทุน</strong> — ต้นทุนไปกลับต่อขาและสองขา (บท 1)</li>
<li><strong>บัญชีสองขา</strong> — เงินสดอิสระ · มูลค่า spot · หลักประกัน · equity ทีละเหตุการณ์ (บท 3, 4)</li>
<li><strong>กันชน</strong> — futures ขึ้นได้กี่ % ก่อนเงินสดหมด · ตารางราคาขึ้น 5 / 10 / 15% (บท 4)</li>
<li><strong>บันได carry</strong> — บันไดสี่ขั้น · บันไดแย่ง · ปิดหรือถือวันที่ N (บท 5, 6)</li>
<li><strong>funding หลายเส้นทาง</strong> — 90 รอบ สี่เส้นทาง + ช่องของคุณ · กฎติดลบ k รอบ · maker/taker (บท 7)</li>
<li><strong>ตาราง φ</strong> — φ → ระยะที่เหลือและสุทธิ · ครึ่งชีวิต ↔ φ · หา φ ด้วยการนับมือ (บท 13)</li>
</ul></div>

<h2>เครื่องมือจากเล่มอื่นในคลังที่บทชี้ไป</h2>
<div class="tw"><table>
<tr><th>เครื่องมือ</th><th>ตอบคำถามอะไร</th><th class="nw">คู่กับ</th></tr>
{''.join(tr(r) for r in existing)}
</table></div>
<p class="src">📱 ตัวเลขในเครื่องมือของเล่มอื่นเป็นตัวอย่างของเล่มนั้น ใส่ค่าของคุณเองก่อนอ่านผล</p>
<p style="text-align:center;margin-top:26px"><a href="tools-index.html">เครื่องมือทั้งหมดในคลัง</a></p>
"""


def build():
    with open(FIG_PATH, encoding="utf-8") as fh:
        fig = json.load(fh)
    pages = [
        tool_page("sab-tool-carry.html", "ลองเอง: บันได carry", "ลองเอง: บันได carry · ปิดหรือถือ · สองกระเป๋า",
                  "เครื่องมือประกอบบท 4–6 · ค่าตั้งต้นคือไม้แรกของมิน", CARRY_BODY,
                  ["บัญชีมิน", "ch03", "ch04", "ch05", "ch06"], CARRY_JS),
        tool_page("sab-tool-funding.html", "ลองเอง: funding หลายเส้นทาง", "ลองเอง: funding หลายเส้นทาง",
                  "เครื่องมือประกอบบท 7 · long spot คู่ short perp 30 วัน", FUND_BODY, ["บัญชีมิน", "ch07"], FUND_JS),
        tool_page("sab-tool-reversion.html", "ลองเอง: แรงดึงกลับ", "ลองเอง: แรงดึงกลับ กลับทันไหม",
                  "เครื่องมือประกอบบท 12–14 · φ แรงสะบัด ต้นทุน ช่วงถือ และการ์ดกติกา", REV_BODY,
                  ["บัญชีมิน", "ch12", "ch13", "ch14"], REV_JS),
        tool_page("sab-tool-fakepair.html", "ลองเอง: คู่ปลอมจากการค้น", "ลองเอง: คู่ปลอมจากการค้น",
                  "เครื่องมือประกอบบท 9–10 · คู่ที่สวยที่สุดจากการค้นมักปลอม", FAKE_BODY,
                  ["ch10", "seed_robustness"], FAKE_JS),
    ]
    hub = B.page("เครื่องมือกดเล่น", "เครื่องมือกดเล่นและสมุดงาน",
                 "ไม่ใช่หน้าให้อ่าน แต่เป็นของให้กด — สี่เครื่องมือของเล่ม สมุดงาน 8 แท็บ และเครื่องมือในคลังที่บทชี้ไป",
                 CSS + hub_body(fig))
    pages.append(("sab-tools.html", hub))
    for fname, html in pages:
        html = fill_data(html, fig)
        with open(os.path.join(B.DOCS, fname), "w", encoding="utf-8") as fh:
            fh.write(html)
        print("เขียน", f"docs/{fname}", f"({len(html.encode()):,} ไบต์)")


# ───────────────────────── --check: เปิดใน Chromium แล้วเทียบกับ JSON ─────────────────────────

# สถานการณ์ที่กดเปลี่ยนค่าแล้วต้องได้ตัวเลขในบทอีกชุด: (หน้า, [การกระทำ], [(selector, path ใน JSON)])
SCENARIOS = [
    ("sab-tool-carry.html", [("click", "#c-fee2")],
     [("#c-fee", "ch05/บันไดที่0.1/ค่าธรรมเนียม"), ("#c-r3", "ch05/บันไดที่0.1/หลังค่าธรรมเนียม"),
      ("#c-r4", "ch05/บันไดที่0.1/ส่วนเกินเปอร์เซ็นต์")]),
    ("sab-tool-carry.html", [("fill", "#c-hur", "9")],
     [("#c-opp", "ch05/hurdle9/ค่าเสียโอกาส"), ("#c-r4", "ch05/hurdle9/ส่วนเกินเปอร์เซ็นต์")]),
    ("sab-tool-carry.html", [("click", "#p-ton")],
     [("#p-buf", "ch04/กันชน/120000"), ("#p-short", "ch04/ต้นขาด"), ("#p-free", "ch04/ต้นเงินสดอิสระ"),
      ("#c-r4", "ch05/ทุนกับกันชน/0/ส่วนเกินเปอร์เซ็นต์")]),
    ("sab-tool-carry.html", [("fill", "#c-cap", "150000")],
     [("#p-buf", "ch04/กันชน/150000"), ("#c-r3", "ch05/ทุนกับกันชน/2/หลังค่าธรรมเนียม")]),
    ("sab-tool-carry.html", [("fill", "#p-x", "15")], [("#p-top", "ch04/dist/2/ต้องโอน"), ("#p-short", "ch04/dist/2/ขาดที่ทุน125000")]),
    ("sab-tool-carry.html", [("fill", "#h-hur", "2")],
     [("#h-opp", "ch06/วันที่30/เสียโอกาสที่hurdle2"), ("#h-dec", "ch06/วันที่30/ตัดสินที่hurdle2")]),
    ("sab-tool-funding.html", [("click", "#f-feeseg button:nth-child(2)")],
     [("#f-net", "ch07/สี่เส้นทาง/ราบ/สุทธิtaker"), ("#f-rule", "ch07/สี่เส้นทาง/ราบ/กฎtaker")]),
    ("sab-tool-funding.html", [("click", "#f-paths button:nth-child(3)")],
     [("#f-tot", "ch07/สี่เส้นทาง/กลับขั้ว/fundingรวม"), ("#f-net", "ch07/สี่เส้นทาง/กลับขั้ว/สุทธิmaker"),
      ("#f-rule", "ch07/สี่เส้นทาง/กลับขั้ว/กฎmaker")]),
    ("sab-tool-funding.html", [("click", "#f-paths button:nth-child(4)")],
     [("#f-rule", "ch07/สี่เส้นทาง/สลับ/กฎmaker"), ("#f-net", "ch07/สี่เส้นทาง/สลับ/สุทธิmaker")]),
    ("sab-tool-funding.html", [("fill", "#f-crowd", "50")],
     [("#f-l3", "ch07/fundingถูกแย่ง/1/สุทธิmakerเปอร์เซ็นต์")]),
    ("sab-tool-reversion.html", [("fill", "#r-phi", "0.99")],
     [("#r-net", "ch13/ตารางphi/0.99/สุทธิ4ช่วง"), ("#r-gross", "ch13/ตารางphi/0.99/กำไรก่อนต้นทุน"),
      ("#r-hl", "ch13/ตารางphi/0.99/ครึ่งชีวิต")]),
    ("sab-tool-reversion.html", [("fill", "#r-phi", "1.02")], [("#r-net", "ch13/ตารางphi/1.02/สุทธิ4ช่วง")]),
    ("sab-tool-reversion.html", [("click", "#s-presets button:nth-child(2)")], [("#s-last", "ch12/เส้นทาง/1/สุทธิ")]),
    ("sab-tool-reversion.html", [("click", "#s-presets button:nth-child(3)")], [("#s-last", "ch12/เส้นทาง/2/สุทธิ")]),
    ("sab-tool-reversion.html", [("click", "#s-presets button:nth-child(5)")], [("#s-last", "ch12/เส้นทาง/4/สุทธิ")]),
    ("sab-tool-reversion.html", [("click", "#s-ok"), ("click", "#s-resume")], [("#s-state", "!ว่าง")]),
]

RUNNER = r"""
import { createRequire } from 'module';
import fs from 'fs';
const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require('/opt/node22/lib/node_modules/playwright/index.js')); }
const spec = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 420, height: 900 } });
await ctx.route('**/*', (r) => (r.request().url().startsWith('file:') ? r.continue() : r.abort()));
const out = [];
for (const job of spec) {
  const page = await ctx.newPage();
  const errs = [];
  page.on('pageerror', (e) => errs.push(e.message));
  await page.goto('file://' + job.file, { waitUntil: 'load' });
  await page.waitForTimeout(200);
  for (const a of job.actions) {
    if (a[0] === 'click') await page.click(a[1]);
    else await page.$eval(a[1], (e, v) => { e.value = v; e.dispatchEvent(new Event('input')); e.dispatchEvent(new Event('change')); }, a[2]);
    await page.waitForTimeout(80);
  }
  const twins = job.actions.length ? [] : await page.$$eval('[data-twin]', (els) => els.map((e) => [e.dataset.twin, e.textContent]));
  const reads = [];
  for (const [sel, path] of job.reads) reads.push([sel, path, await page.$eval(sel, (e) => e.textContent)]);
  out.push({ file: job.file, actions: job.actions, errs, twins, reads });
  await page.close();
}
await browser.close();
process.stdout.write(JSON.stringify(out));
"""


def jpath(fig, path):
    cur = fig
    for k in path.split("/"):
        if isinstance(cur, list):
            cur = cur[int(k)]
        else:
            cur = cur[k]
    return cur


def parse_num(text):
    t = text.strip().replace("−", "-").replace(",", "").replace("%", "")
    m = re.fullmatch(r"-?\d+(?:\.\d+)?", t)
    return (float(t), len(t.split(".")[1]) if "." in t else 0) if m else (None, None)


def same(text, want):
    if isinstance(want, str) or want is None:
        return text.strip() == str(want)
    v, d = parse_num(text)
    if v is None:
        return False
    return abs(v - float(want)) <= 0.5 * 10 ** (-d) + 1e-9


def check():
    with open(FIG_PATH, encoding="utf-8") as fh:
        fig = json.load(fh)
    spec = [{"file": os.path.join(B.DOCS, p), "actions": [], "reads": []} for p in PAGES[:4]]
    for page, actions, reads in SCENARIOS:
        spec.append({"file": os.path.join(B.DOCS, page), "actions": [list(a) for a in actions],
                     "reads": [list(r) for r in reads]})
    tmp = tempfile.mkdtemp(prefix="sab_tools_")
    try:
        sp, rn = os.path.join(tmp, "spec.json"), os.path.join(tmp, "run.mjs")
        with open(sp, "w", encoding="utf-8") as fh:
            json.dump(spec, fh, ensure_ascii=False)
        with open(rn, "w", encoding="utf-8") as fh:
            fh.write(RUNNER)
        r = subprocess.run(["node", rn, sp], capture_output=True, text=True, timeout=600)
        if r.returncode != 0:
            print(r.stderr)
            return 1
        res = json.loads(r.stdout)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    problems, n_twin, n_read = [], 0, 0
    for job in res:
        name = os.path.basename(job["file"])
        for e in job["errs"]:
            problems.append(f"{name}: page error {e}")
        for path, text in job["twins"]:
            n_twin += 1
            want = jpath(fig, path)
            if not same(text, want):
                problems.append(f"{name}: [data-twin={path}] แสดง {text!r} แต่ JSON = {want!r}")
        for sel, path, text in job["reads"]:
            n_read += 1
            if path.startswith("!"):
                ok = text.strip() == path[1:]
                want = path[1:]
            else:
                want = jpath(fig, path)
                ok = same(text, want)
            if not ok:
                problems.append(f"{name} หลัง {job['actions']}: {sel} แสดง {text!r} แต่ {path} = {want!r}")
    for p in problems:
        print("✗", p)
    print(f"ตอนเปิด: เทียบ {n_twin} ค่า [data-twin] · สถานการณ์กดเปลี่ยนค่า {len(SCENARIOS)} ชุด {n_read} ค่า")
    print("ผ่าน ✓" if not problems else f"ไม่ผ่าน ✗ ({len(problems)} ปัญหา)")
    return 0 if not problems else 1


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(check())
    build()
