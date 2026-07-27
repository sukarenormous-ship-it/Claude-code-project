#!/usr/bin/env python3
"""รันบล็อกโค้ดแบบ 'ผู้อ่านไล่ตามทีละบล็อกในไฟล์เดียว' (cumulative namespace)
บันทึกผลว่าบล็อกไหนพัง ด้วย error อะไร
"""
import io
import json
import os
import pathlib
import re
import sys
import traceback
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = pathlib.Path(os.environ.get("SNIPPET_DIR", "/tmp/book-snippets"))
SNIP = HERE
meta = json.loads((SNIP / "_meta.json").read_text())

plt.show = lambda *a, **k: None          # ไม่ให้ block
plt.savefig_orig = plt.savefig
plt.savefig = lambda *a, **k: None

TARGET = sys.argv[1] if len(sys.argv) > 1 else None

results = []
files = sorted({r["file"] for r in meta})
if TARGET:
    files = [f for f in files if TARGET in f]

for fn in files:
    # .ad-code = ภาพประกอบสอน (คลาสเวอร์ชันย่อ/ชิ้นส่วน) — ห้ามปนลำดับหลัก
    # ไม่งั้นมันจะทับคลาสจริงที่นิยามไว้ใน .fm
    blocks = [
        r for r in meta
        if r["file"] == fn and r["kind"] == "fm" and r["python"]
    ]
    ns = {"__name__": "__main__"}
    for r in blocks:
        code = (SNIP / f"{r['stem']}.txt").read_text(encoding="utf-8")
        # บล็อกที่เป็น "เนื้อไฟล์" (เช่น test_strategy.py ที่ให้ pytest รัน)
        # ไม่ใช่โค้ดที่รันต่อกันในสคริปต์เดียว — ติดป้ายด้วยหัว  # ── ชื่อไฟล์.py ──
        if re.match(r"\s*#\s*──\s*\S+\.py\s*──", code):
            continue
        buf = io.StringIO()
        old = sys.stdout
        rec = dict(file=fn, line=r["line"], stem=r["stem"])
        try:
            with warnings.catch_warnings(record=True) as wlist:
                warnings.simplefilter("always")
                sys.stdout = buf
                compile(code, r["stem"], "exec")   # แยก SyntaxError ออกมาก่อน
                exec(code, ns)
            rec["status"] = "ok"
            rec["warns"] = sorted({
                f"{w.category.__name__}: {str(w.message)[:120]}" for w in wlist
            })
        except SyntaxError as e:
            rec["status"] = "SyntaxError"
            rec["err"] = f"{e.msg} (line {e.lineno})"
        except Exception as e:
            rec["status"] = type(e).__name__
            rec["err"] = str(e)[:300]
            rec["tb"] = traceback.format_exc(limit=3)[-600:]
        finally:
            sys.stdout = old
            rec["stdout"] = buf.getvalue()[:1500]
            plt.close("all")
        results.append(rec)

(HERE / "run_results.json").write_text(json.dumps(results, indent=1))

bad = [r for r in results if r["status"] != "ok"]
print(f"รัน {len(results)} บล็อก · ผ่าน {len(results)-len(bad)} · พัง {len(bad)}\n")
from collections import Counter
for k, n in Counter(r["status"] for r in bad).most_common():
    print(f"  {k:22s} {n}")
print()
for r in bad:
    print(f"❌ {r['file']}:{r['line']:5d}  {r['status']}: {r.get('err','')[:150]}")
