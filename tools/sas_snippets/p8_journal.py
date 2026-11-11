import sys, os, argparse
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import sas_core as C
import statarb_lab as LAB

# ใช้: python3 tools/sas_snippets/p8_journal.py [ไฟล์.csv Y X [journal.csv]] [--cost-bps 8 ...]
# ทำอะไร: รันเจ็ดสถานีด้วยกฎชุดเดียวกับ check แล้วพิมพ์ "หนึ่งบรรทัดของสมุดวิจัย" (ใส่ชื่อสมุด = ต่อท้ายให้)
ap = argparse.ArgumentParser()
ap.add_argument("files", nargs="*")
for k, v in [("--cost-bps", LAB.DEFAULT_COST_BPS), ("--train", LAB.DEFAULT_TRAIN),
             ("--entry", LAB.DEFAULT_ENTRY), ("--exit", LAB.DEFAULT_EXIT)]:
    ap.add_argument(k, type=float, default=v)
ap.add_argument("--prices", default="raw", choices=["raw", "log"])
a = ap.parse_args()
if len(a.files) >= 3:
    names, mat, dates, rep = LAB.load_columns(a.files[0], a.files[1:3], a.prices)
    y, x, pair = mat[:, 0], mat[:, 1], f"{names[0]}~{names[1]}"
else:  # คู่ตัวอย่าง good (ข้อมูลจำลอง)
    d = C.demo_pair("good")
    y, x, rep, dates, pair = d["y"], d["x"], None, None, "Y_good~X_good"
book = a.files[3] if len(a.files) == 4 else None
new = book is not None and not os.path.exists(book)
n_try = 1 + (sum(1 for _ in open(book, encoding="utf-8")) - 1 if book and not new else 0)
st = LAB.run_stations(y, x, LAB.options(a.cost_bps, a.train, a.entry, a.exit), rep, dates)
m = {k: v for s in st for k, v in s["m"].items()}
def f(key, fmt):                         # สถานีที่ไม่ได้รัน (หยุดที่สถานี 1) → เว้นว่าง
    return format(m[key], fmt) if key in m else ""
p = m.get("p")
p_txt = "" if p is None else "<0.001" if p < 0.001 else f"{p:.{2 if p >= 0.1 else 3}f}"
cols = ["try", "pair", "bars", "cost_bps", "entry", "exit", "train", "beta", "eg", "p", "half_life",
        "shift", "width", "cost_ratio", "sharpe_exam", "trades", "stations", "verdict", "why"]
row = [str(n_try), pair, str(len(y)), f"{a.cost_bps:g}", f"{a.entry:g}", f"{a.exit:g}", f"{a.train:g}",
       f("beta", ".3f"), f("adf", ".2f"), p_txt, f("half_life", ".1f"), f("shift", "+.2f"),
       f("sd_ratio", ".2f"), f("ratio", ".1f"), f("sharpe2", ".2f"), f("trades", "d"),
       "".join(s["status"] for s in st), LAB.verdict(st)[0], "(เขียนเอง)"]
if book:                                 # ต่อท้ายสมุด (ไฟล์ใหม่ = เขียนหัวคอลัมน์ให้ก่อน)
    with open(book, "a", encoding="utf-8") as fh:
        fh.write((",".join(cols) + "\n" if new else "") + ",".join(row) + "\n")
print(",".join(cols))
print(",".join(row))
