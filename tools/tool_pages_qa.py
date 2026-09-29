#!/usr/bin/env python3
"""ตรวจเครื่องมือโต้ตอบ docs/tool-*.html ในเบราว์เซอร์จริง เทียบกับสูตรเดียวกันที่เขียนด้วย Python

แต่ละหน้าคำนวณด้วย JavaScript ตอนเลื่อน slider ตัวตรวจนี้ทำสามอย่าง
  1. เปิดหน้าใน Chromium (Playwright) แล้วต้องไม่มี JS error
  2. ค่าตั้งต้นที่พิมพ์ไว้ใน HTML ต้องเท่ากับค่าที่ JS เขียนทับตอนโหลด (ไม่มีเลขค้าง)
  3. ตั้ง slider หลายชุด แล้วค่าที่หน้าแสดงต้องตรงกับโมเดล Python ด้านล่างทุกตัว

    python3 tools/tool_pages_qa.py

ต้องมี node + Playwright (ติดตั้งไว้แล้วในสภาพแวดล้อมนี้) · ถ้าไม่มีจะข้ามพร้อมคำเตือน ไม่นับเป็นข้อผิด
"""

import json
import math
import os
import shutil
import subprocess
import sys
import tempfile

from scipy.stats import norm

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
PW = os.environ.get("PLAYWRIGHT_JS", "/opt/node22/lib/node_modules/playwright/index.js")
EULER = 0.5772156649


def _pct(x, d):
    return ("+" if x >= 0 else "−") + f"{abs(x):.{d}f}%"


def _round(x):          # Math.round ของ JS (ปัดครึ่งขึ้น)
    return math.floor(x + 0.5)


def vol_drag(mu, sig, lev):
    mu, sig = mu / 100, sig / 100
    a, dr = lev * mu, (lev * sig) ** 2 / 2
    return {"oArith": _pct(a * 100, 1), "oDrag": f"−{dr * 100:.1f}%", "oGeo": _pct((a - dr) * 100, 1)}


def carry_blowup(carry, lev, deval, prob):
    prob /= 100
    good = carry * lev; bad = good - deval * lev; ev = (1 - prob) * good + prob * bad
    return {"oGood": _pct(good, 0), "oBad": _pct(bad, 0), "oEv": _pct(ev, 0),
            "oSurv": f"~{1 / prob:.0f} ปี", "oTen": f"{_round((1 - prob) ** 10 * 100)}%"}


def duration(dur, dy, cvx=None):
    if cvx is None:     # หน้าเว็บตั้ง convexity ≈ D² + D ให้เองจนกว่าผู้อ่านจะเลื่อน
        cvx = min(1000, _round((dur * dur + dur) / 10) * 10)
    d = dy / 1e4; a = -dur * d; f = a + 0.5 * cvx * d * d; baht = _round(f * 1e6)
    return {"oDur": _pct(a * 100, 1), "oFull": _pct(f * 100, 1), "oBaht": ("+" if baht >= 0 else "−") + f"{abs(baht):,}"}


def diversification(sa, sb, rho):
    base = 0.5 * sa + 0.5 * sb; port = math.sqrt(max(0, 0.25 * sa * sa + 0.25 * sb * sb + 0.5 * rho * sa * sb))
    return {"oBase": f"{base:.1f}%", "oPort": f"{port:.1f}%", "oBenefit": f"{(base - port) / base * 100:.0f}%"}


def deflated_sharpe(sr, years, n):
    e = 0 if n < 2 else (1 - EULER) * norm.ppf(1 - 1 / n) + EULER * norm.ppf(1 - 1 / (n * math.e))
    s0 = e / math.sqrt(years); se = math.sqrt((1 + sr * sr / 504) / years); r = sr - s0
    return {"oObs": f"{sr:.2f}", "oNoise": f"{s0:.2f}", "oReal": ("+" if r >= 0 else "−") + f"{abs(r):.2f}",
            "oDsr": f"{_round(norm.cdf(r / se) * 100)}%"}


PAGES = {
    "tool-vol-drag.html": (vol_drag, [dict(mu=12, sig=25, lev=3), dict(mu=10, sig=20, lev=1), dict(mu=8, sig=40, lev=4), dict(mu=20, sig=10, lev=8)]),
    "tool-carry-blowup.html": (carry_blowup, [dict(carry=7, lev=5, deval=40, prob=5), dict(carry=8, lev=6, deval=25, prob=10), dict(carry=3, lev=2, deval=20, prob=1), dict(carry=15, lev=20, deval=60, prob=30)]),
    "tool-duration.html": (duration, [dict(dur=18, dy=200), dict(dur=7, dy=100), dict(dur=30, dy=-200), dict(dur=0.5, dy=25), dict(dur=18, dy=200, cvx=0)]),
    "tool-diversification.html": (diversification, [dict(sa=20, sb=20, rho=0.2), dict(sa=10, sb=40, rho=-0.5), dict(sa=30, sb=15, rho=1), dict(sa=50, sb=5, rho=0.6)]),
    "tool-deflated-sharpe.html": (deflated_sharpe, [dict(sr=1.2, years=3, n=50), dict(sr=1.5, years=2, n=100), dict(sr=3, years=2, n=100), dict(sr=0.5, years=1, n=1), dict(sr=5, years=20, n=1000)]),
}

HARNESS = r"""
import pw from '%s';
import fs from 'fs';
const spec = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const b = await pw.chromium.launch(); const p = await b.newPage(); const res = {};
for (const [file, t] of Object.entries(spec)) {
  const errs = []; p.removeAllListeners('pageerror'); p.on('pageerror', e => errs.push(String(e)));
  const url = 'file://' + t.path;
  await p.goto(url);
  const onload = await p.evaluate(ids => Object.fromEntries(ids.map(i => [i, document.getElementById(i).textContent])), t.outs);
  const cases = [];
  for (const c of t.cases) {
    await p.goto(url);
    await p.evaluate(c => { for (const [id, v] of Object.entries(c)) { const e = document.getElementById(id); e.value = v; e.dispatchEvent(new Event('input')); } }, c);
    cases.push(await p.evaluate(ids => Object.fromEntries(ids.map(i => [i, document.getElementById(i).textContent])), t.outs));
  }
  res[file] = { onload, cases, errs };
}
console.log(JSON.stringify(res)); await b.close();
"""


def main():
    import re
    if not shutil.which("node") or not os.path.exists(PW):
        print("⚠️  ไม่มี node/Playwright — ข้ามการตรวจเครื่องมือในเบราว์เซอร์")
        return 0
    spec = {}
    for f, (model, cases) in PAGES.items():
        spec[f] = dict(path=os.path.join(DOCS, f), outs=list(model(**cases[0])), cases=cases)
    with tempfile.TemporaryDirectory() as td:
        js, sp = os.path.join(td, "h.mjs"), os.path.join(td, "spec.json")
        open(js, "w").write(HARNESS % PW); json.dump(spec, open(sp, "w"))
        out = subprocess.run(["node", js, sp], capture_output=True, text=True, timeout=300)
    if out.returncode != 0:
        print("❌ harness ล้มเหลว:", out.stderr[-800:]); return 1
    res = json.loads(out.stdout.strip().splitlines()[-1])
    bad = n = 0
    for f, (model, cases) in PAGES.items():
        r = res[f]; raw = open(os.path.join(DOCS, f), encoding="utf-8").read()
        for e in r["errs"]:
            print(f"❌ {f}: JS error {e}"); bad += 1
        for k, v in r["onload"].items():
            m = re.search(rf'id="{k}">([^<]*)<', raw)
            if not m or m.group(1) != v:
                print(f"❌ {f}: ค่าตั้งต้นใน HTML ของ {k} = {m.group(1) if m else None!r} แต่ JS เขียน {v!r}"); bad += 1
        for c, got in zip(cases, r["cases"]):
            want = model(**c)
            for k, v in want.items():
                n += 1
                if got[k] != v:
                    print(f"❌ {f} {c}: {k} หน้าเว็บ {got[k]!r} ≠ Python {v!r}"); bad += 1
    print(f"ตรวจเครื่องมือ {len(PAGES)} หน้า · {sum(len(c) for _, c in PAGES.values())} ชุด slider · {n} ค่า · ไม่ตรง {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
