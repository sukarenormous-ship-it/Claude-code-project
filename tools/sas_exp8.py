#!/usr/bin/env python3
"""
ห้องทดลองตอนที่ 8 — "ลงมือทำ: คู่มือห้องทดลองกับข้อมูลของคุณเอง"

ตอนนี้ไม่มีทฤษฎีใหม่ มีแต่เครื่องมือ: tools/statarb_lab.py พาคู่ของคุณผ่านเจ็ดสถานีแล้วให้คำตัดสิน
ครึ่งแรกของข้อมูล = ช่วงศึกษา (สถานี 2–4, 6 และคำสั่ง scan ดูแค่ครึ่งนี้) · ครึ่งหลัง = ช่วงสอบ (สถานี 5, 7)
โมดูลนี้ทำสี่อย่างเพื่อให้เนื้อหาตอนที่ 8 มีหลักฐานรองรับ (ข้อมูลจำลองทั้งหมด)

  การทดลอง A — รันเครื่องมือจริงกับคู่ตัวอย่างสี่คู่ (ข้อมูลจำลองที่ "ถูกเลือก" ให้เห็นอาการชัด)
      เรียกฟังก์ชันของ statarb_lab ในกระบวนการเดียวกัน (ไม่ได้พิมพ์ผลเอง) แล้วเก็บข้อความที่พิมพ์
      ออกมาตรงตัวไว้ใต้ outputs.* — make-demo, check ×4, scan, basket และ check กับไฟล์ที่ตั้งใจทำให้
      "สกปรก" แบบไฟล์จริง (ค่าว่าง วันที่ซ้ำ ราคา 0 เรียงใหม่→เก่า และ split 2:1 ที่ไม่ได้ปรับราคา)

  การทดลอง B — เครื่องมือนี้เชื่อได้แค่ไหน (Monte Carlo)
      จำลองโลกห้าแบบ แบบละ N_WORLDS โลก (1,500 แท่ง): good / drift / break / fake ตามค่าตั้งต้นของ
      C.make_pair และ slow = สายจูงจริงแต่ช้ากว่า (half-life 30 แทน 12) ส่งเข้าเจ็ดสถานีชุดเดียวกัน
      แล้วนับว่าแต่ละสถานีและคำตัดสินรวมออกมาเป็น ✅ / ⚠️ / ❌ กี่เปอร์เซ็นต์ — คำตอบที่ซื่อสัตย์ของ
      "ผ่านครบเจ็ดสถานีแปลว่าอะไร" ต้องมาจากตรงนี้ ไม่ใช่จากคู่ตัวอย่างสี่คู่

  การทดลอง C — ทำไมสถานี 7 จึง backtest แค่ครึ่งหลัง (ความลำเอียงจากการคัดเลือก)
      จำลองคู่ที่ "ไม่มีสายจูง" N_SEL คู่ เก็บเฉพาะคู่ที่บังเอิญผ่านสถานี 3 (ราว 5%) แล้ว backtest
      แบบ walk-forward ทั้งในช่วงศึกษา (ช่วงที่ใช้คัด) และช่วงสอบ — ช่วงที่ใช้คัดดูมีกำไร ช่วงสอบไม่มี

  การทดลอง D — ตะกร้าที่ใส่ขาไม่เกี่ยว (Monte Carlo ของตัวอย่าง basket)
      คู่ good + random walk อิสระสองเส้น เทียบกับคู่ good ล้วน: ครึ่งแรกดูดีขึ้นไหม ครึ่งหลังแย่ลงไหม

ไม่มีการมองอนาคต: เครื่องมือประมาณ β, σ จากครึ่งแรก ไปวัดครึ่งหลัง และ backtest แบบ walk-forward
บนครึ่งหลัง (สถานะที่ตัดสินใจสิ้นแท่ง t รับผลตั้งแต่แท่ง t+1 · รายงาน lag 1 คู่กับ lag 2 เสมอ)

คีย์ของ figures()  (ทุกค่าปัดแล้ว · เปอร์เซ็นต์เป็นเลขอย่าง 12.3 · % จาก Monte Carlo ปัดเป็นจำนวนเต็ม)
  about.*                     คำอธิบายสั้นของแต่ละการทดลองและค่าที่ตั้งไว้
  settings.*                  n_bars, half_bars, exam_first_bar, exam_bars, train_bars, refit_bars, cost_bps,
                              round_trip_bps, entry, exit, sims, worlds, worlds_total
  thresholds.*                เกณฑ์ทุกตัวของ statarb_lab (ชื่อเดียวกับค่าคงที่ ตัวพิมพ์เล็ก) + แบบ _pct
  cutoff.*                    เส้นตัด 1/5/10% ของเครื่องมือ (20,000 โลก) เทียบกับอ้างอิง (100,000 โลก)
  demo.<kind>.*               verdict (pass/warn/fail), verdict_icon, verdict_line, status.s1…s7 (✅ ⚠️ ❌),
                              beta, beta_inv, beta_tls, beta_gap_pct, beta_second_half, beta_change_pct,
                              eg, eg_p_text, cut5, cut_noise, half_life_bars, sigma_pct,
                              crossings_per_year, train_per_half_life, shift_sigma, sd_ratio, eg_second_half,
                              eg_second_half_p_text, earn_bps, round_trip_bps, cost_ratio,
                              sharpe_lag1, sharpe_lag2, trades, hit_pct, hit_noise_pts, max_dd_pct,
                              ann_return_pct, avg_trade_bps, z_sd, exam_bars, exam_years, sharpe_margin,
                              sharpe_study, trades_study   (สถานี 7 = ช่วงสอบ · *_study = แถวเทียบของช่วงศึกษา)
  mc.worlds, mc.se_pts        จำนวนโลกต่อแบบ · ความคลาดมาตรฐานของ % ที่ 50% (จุด)
  mc.<kind>.*                 kind ∈ good, drift, break, fake, slow · pass_pct / warn_pct / fail_pct ·
                              s2…s7.{ok,warn,fail}_pct · sharpe_exam_{med,p05,p95} · sharpe_study_med ·
                              trades_{med,p05,p95}
  selection.*                 screened, selected, selected_pct, sharpe_study_{med,p05,p95},
                              sharpe_exam_{med,p05,p95}, study_would_pass_pct, s7_ok_pct, s7_fail_pct
  basket_mc.*                 worlds, eg_{pair,basket}_med, pass_{pair,basket}_pct, shift_{pair,basket}_med,
                              sd_ratio_{pair,basket}_med, ruler_bad_{pair,basket}_pct
  scan.*                      pairs, by_luck, passed_5pct, passed_strict, strict_p, cut5, best_pair, …
  basket.*                    n_assets, weights, eg, cut5, cut5_pair, half_life_bars, sigma_pct,
                              shift_sigma, sd_ratio (เทียบกับ demo.good ที่เป็นคู่ธรรมดา)
  messy.*                     rows_read, rows_used, dropped, jumps, verdict, status
  outputs.*                   ข้อความที่โปรแกรมพิมพ์ ตรงตัว: make_demo, check_good, check_drift, check_break,
                              check_fake, scan_demo, basket_demo, check_messy  (ใช้กับ <!--OUT:p8.outputs.…-->)

กราฟ: sas-p8-pipeline (แผนผังเจ็ดสถานี) · sas-p8-verdicts (คำตัดสินรวมต่อแบบของโลก) ·
      sas-p8-stations (สถานีไหนจับอาการไหน) · sas-p8-selection (backtest ช่วงที่ใช้คัด vs ช่วงสอบ)

รัน:  python3 tools/sas_exp8.py        (ราว 35 วินาที · seed ผ่าน C.rng(800–870) เท่านั้น รันซ้ำได้เลขเดิม)
"""
import contextlib
import csv
import functools
import io
import math
import os
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sas_core as C  # noqa: E402
import sas_svg as V  # noqa: E402
import statarb_lab as LAB  # noqa: E402

KINDS = ("good", "drift", "break", "fake")            # คู่ตัวอย่างสี่คู่ (การทดลอง A)
MC_KINDS = KINDS + ("slow",)                          # การทดลอง B เพิ่มสายจูงที่ช้ากว่า
SLOW_HALF_LIFE = 30.0                                 # "slow" = คู่ good ทุกอย่าง ยกเว้น half-life 30 แท่ง
KIND_TH = {"good": "good — มีสายจูงจริง", "drift": "drift — สายจูงยืด (β เลื่อน)",
           "break": "break — สายจูงขาดที่ 60%", "fake": "fake — ไม่มีสายจูง",
           "slow": "slow — สายจูงจริงแต่ช้า (half-life 30)"}
N_BARS = 1500              # ความยาวของทุกโลกจำลอง (เท่ากับคู่ตัวอย่าง)
N_WORLDS = 300             # จำนวนโลกต่อแบบในการทดลอง B (% คลาดมาตรฐานได้ถึงราว ±3 จุด จึงปัดเป็นจำนวนเต็ม)
N_SEL = 3000               # คู่ "ไม่มีสายจูง" ที่ส่งเข้าสถานี 3 ในการทดลอง C (ผ่านมาราว 5%)
N_BASKET = 300             # จำนวนโลกของการทดลอง D
REF_SIMS = 100_000         # จำนวนโลกของเส้นตัด "อ้างอิง" ที่ใช้ตรวจเส้นตัดของเครื่องมือ
SEED_MC, SEED_SEL, SEED_BASKET, SEED_REF = 850, 860, 861, 870   # statarb_lab ใช้ 800 + จำนวนสินทรัพย์
BASKET_LEGS = "X_good,X_drift,X_fake"


# ───────────────────────── การทดลอง A: รันเครื่องมือจริง ─────────────────────────

def cli(*argv):
    """เรียก statarb_lab เหมือนพิมพ์คำสั่งเอง แล้วคืนข้อความที่มันพิมพ์ออกมา (ตรงตัว)"""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        LAB.main(list(argv))
    return buf.getvalue().rstrip("\n")


def write_messy(src, dst):
    """ไฟล์ "แบบที่เจอจริง": คู่ good คู่เดิม (ตั้งชื่อใหม่ AAA, BBB) ที่ใส่ความสกปรกห้าอย่าง
    ค่าว่าง · NA · ราคา 0 · วันที่ซ้ำ · split 2:1 ของ AAA ที่ไม่ได้ปรับราคาย้อนหลัง · และเรียงใหม่ → เก่า"""
    with open(src, newline="", encoding="utf-8") as fh:
        data = [r[:3] for r in list(csv.reader(fh))[1:]]
    data[120][1] = ""
    data[480][2] = "NA"
    data[610][1] = "0"
    for r in data[900:]:
        r[1] = f"{float(r[1]) / 2:.4f}"
    data.insert(300, list(data[299]))
    with open(dst, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["date", "AAA", "BBB"])
        w.writerows(data[::-1])


def stations_of(path, ycol, xcol):
    """ผลเจ็ดสถานีในรูปตัวเลข (ชุดเดียวกับที่ check พิมพ์) สำหรับเก็บลง figures"""
    _, mat, dates, rep = LAB.load_columns(path, [ycol, xcol], "raw")
    return LAB.run_stations(mat[:, 0], mat[:, 1], LAB.options(), rep, dates), rep


def scan_numbers(path):
    """ตัวเลขสรุปของ scan บนไฟล์ตัวอย่าง (คำนวณด้วยฟังก์ชันเดียวกับคำสั่ง)"""
    names, mat, _, _ = LAB.load_columns(path, None, "raw")
    h = len(mat) // 2
    found, _ = LAB.scan_pairs(names, mat[:h], LAB.DEFAULT_SIMS)
    strict = LAB.P_PASS / len(found)
    cv5 = C.crit_values(LAB.null_eg(h, 2, LAB.DEFAULT_SIMS))[0.05]
    return {"found": found, "strict": strict, "cv5": cv5, "h": h,
            "n5": sum(p < LAB.P_PASS for p, *_ in found), "n_strict": sum(p < strict for p, *_ in found)}


def basket_numbers(path):
    """ตัวเลขของตัวอย่างตะกร้า: Y_good เทียบกับขาจริงหนึ่งขา + ขาที่ไม่เกี่ยวสองขา"""
    names, mat, _, _ = LAB.load_columns(path, ["Y_good"] + BASKET_LEGS.split(","), "raw")
    return dict(LAB.basket_fit(mat, LAB.DEFAULT_SIMS), names=names)


def run_tool():
    """การทดลอง A ทั้งหมด: เขียนไฟล์ตัวอย่างลงโฟลเดอร์ชั่วคราว แล้วรันทุกคำสั่งกับมัน"""
    with tempfile.TemporaryDirectory() as tmp:
        demo, messy = os.path.join(tmp, "demo.csv"), os.path.join(tmp, "my_pair.csv")
        out = {"make_demo": cli("make-demo", demo)}
        for k in KINDS:
            out[f"check_{k}"] = cli("check", demo, "--y", f"Y_{k}", "--x", f"X_{k}")
        out["scan_demo"] = cli("scan", demo)
        out["basket_demo"] = cli("basket", demo, "--y", "Y_good", "--basket", BASKET_LEGS)
        write_messy(demo, messy)
        out["check_messy"] = cli("check", messy, "--y", "AAA", "--x", "BBB")
        return {"outputs": out, "demo": {k: stations_of(demo, f"Y_{k}", f"X_{k}")[0] for k in KINDS},
                "messy": stations_of(messy, "AAA", "BBB"), "scan": scan_numbers(demo),
                "basket": basket_numbers(demo)}


# ───────────────────────── การทดลอง B: เครื่องมือเชื่อได้แค่ไหน ─────────────────────────

def make_world(kind, g):
    """โลกจำลองหนึ่งโลก · slow = good ที่ half-life ยาวขึ้น (ทุกอย่างอื่นเท่าเดิม)"""
    if kind == "slow":
        return C.make_pair("good", N_BARS, g, half_life=SLOW_HALF_LIFE)
    return C.make_pair(kind, N_BARS, g)


def reliability():
    """ส่งโลกจำลองแบบละ N_WORLDS โลกเข้าเจ็ดสถานี → สถานะของทุกสถานี + คำตัดสินรวม + Sharpe/จำนวนไม้
    status[kind] เป็นอาร์เรย์ (โลก × 7) ของ 0 = ✅, 1 = ⚠️, 2 = ❌ · verdict[kind] เป็น 0/1/2 แบบเดียวกัน"""
    opt = LAB.options()
    level = {LAB.OK: 0, LAB.WARN: 1, LAB.FAIL: 2}
    code = {"pass": 0, "warn": 1, "fail": 2}
    res = {}
    for i, kind in enumerate(MC_KINDS):
        g = C.rng(SEED_MC + i)
        status = np.zeros((N_WORLDS, 7), dtype=int)
        verdict = np.zeros(N_WORLDS, dtype=int)
        exam, study, trades = np.zeros(N_WORLDS), np.zeros(N_WORLDS), np.zeros(N_WORLDS)
        for w in range(N_WORLDS):
            d = make_world(kind, g)
            st = LAB.run_stations(d["y"], d["x"], opt)
            status[w] = [level[s["status"]] for s in st]
            verdict[w] = code[LAB.verdict(st)[0]]
            m7 = st[6]["m"]
            exam[w], study[w], trades[w] = m7["sharpe2"], m7["sharpe_study"], m7["trades"]
        res[kind] = {"status": status, "verdict": verdict, "sharpe_exam": exam, "sharpe_study": study,
                     "trades": trades}
    return res


# ───────────────────────── การทดลอง C: backtest บนช่วงที่ใช้คัดคู่ ─────────────────────────

def selection_bias():
    """คู่ที่ไม่มีสายจูง (fake) N_SEL คู่ → เก็บเฉพาะคู่ที่สถานี 3 ให้ ✅ (บังเอิญล้วน ๆ)
    แล้วดู Sharpe (lag 2) ของ walk-forward ในช่วงศึกษา (แท่ง 251–750 = ช่วงที่ใช้คัด) เทียบกับช่วงสอบ"""
    opt = LAB.options()
    g = C.rng(SEED_SEL)
    study, exam, s7 = [], [], []
    for _ in range(N_SEL):
        d = C.make_pair("fake", N_BARS, g)
        if LAB.station_leash(LAB.fit_first_half(d["y"], d["x"]), opt)["status"] != LAB.OK:
            continue
        st7 = LAB.station_backtest(d["y"], d["x"], opt)
        study.append(st7["m"]["sharpe_study"])
        exam.append(st7["m"]["sharpe2"])
        s7.append(st7["status"])
    return {"screened": N_SEL, "study": np.array(study), "exam": np.array(exam), "s7": np.array(s7),
            "study_years": (N_BARS // 2 - opt.train) / C.DAYS_PER_YEAR}


# ───────────────────────── การทดลอง D: ตะกร้าที่ใส่ขาไม่เกี่ยว ─────────────────────────

def basket_overfit():
    """คู่ good + random walk อิสระสองเส้น (ความผันผวนเท่า X) เทียบกับคู่ good ล้วน · น้ำหนักจากครึ่งแรก
    คืนอาร์เรย์ (โลก × 4): EG ครึ่งแรก, p-value (เส้นตัดของจำนวนสินทรัพย์นั้น), |เลื่อน| (σ), sd ครึ่งหลัง/ครึ่งแรก"""
    g = C.rng(SEED_BASKET)
    out = {"pair": [], "basket": []}
    for _ in range(N_BASKET):
        d = C.make_pair("good", N_BARS, g)
        junk = [C.random_walk(N_BARS, 0.015, g, x0=4.0) for _ in range(2)]
        for key, cols in (("pair", [d["y"], d["x"]]), ("basket", [d["y"], d["x"]] + junk)):
            b = LAB.basket_fit(np.column_stack(cols), LAB.DEFAULT_SIMS)
            out[key].append((b["eg"]["adf"], b["eg"]["p"], abs(b["shift"]), b["sd_ratio"]))
    return {k: np.array(v) for k, v in out.items()}


def reference_cutoff():
    """เส้นตัดของคู่ (750 แท่ง · lags 1) จากการจำลอง REF_SIMS โลก เทียบกับของเครื่องมือ (DEFAULT_SIMS โลก)
    ตอบคำถามว่า "±" ที่เครื่องมือพิมพ์ไว้ข้างเส้นตัดนั้นซื่อตรงไหม"""
    h = N_BARS // 2
    ref = C.crit_values(C.mc_null_eg(h, 2, n_sim=REF_SIMS, lags=LAB.EG_LAGS, g=C.rng(SEED_REF)))
    tool = LAB.null_eg(h, 2, LAB.DEFAULT_SIMS)
    return {"ref": ref, "tool": C.crit_values(tool), "noise": LAB.cutoff_noise(tool, 0.05)}


@functools.lru_cache(maxsize=1)
def run():
    """ทุกการคำนวณของตอนที่ 8 (จำไว้ใช้ซ้ำ: figures() กับ charts() ใช้ผลชุดเดียวกัน)"""
    res = run_tool()
    res["mc"] = reliability()
    res["selection"] = selection_bias()
    res["basket_mc"] = basket_overfit()
    res["cutoff"] = reference_cutoff()
    return res


# ───────────────────────── figures ─────────────────────────

def whole(v):
    """เลขที่เป็นจำนวนเต็มพอดีเก็บเป็น int (ตัวเติมตัวเลขจะพิมพ์ 10 ไม่ใช่ 10.0)"""
    return int(v) if float(v).is_integer() else v


def share(mask):
    """สัดส่วนของ True → เปอร์เซ็นต์จำนวนเต็ม (300 โลก: ทศนิยมแกว่งตามการสุ่ม จึงไม่เก็บ)"""
    return whole(C.pct(float(np.mean(mask)), 0))


def spread3(values, d=1):
    """ค่ากลางและช่วง 5–95% ของผลจากหลายโลก"""
    lo, med, hi = np.percentile(values, [5, 50, 95])
    return {"med": C.rd(med, d), "p05": C.rd(lo, d), "p95": C.rd(hi, d)}


def demo_figures(stations):
    """ตัวเลขของคู่ตัวอย่างหนึ่งคู่ ปัดแบบเดียวกับที่ check พิมพ์"""
    code, line, _ = LAB.verdict(stations)
    s2, s3, s4, s5, s6, s7 = (s["m"] for s in stations[1:])
    return {
        "verdict": code, "verdict_icon": line.split(" ")[0], "verdict_line": line,
        "status": {f"s{s['no']}": s["status"] for s in stations},
        "beta": C.rd(s2["beta"], 3), "beta_inv": C.rd(s2["beta_inv"], 3), "beta_tls": C.rd(s2["beta_tls"], 3),
        "beta_gap_pct": C.pct(s2["gap"], 1), "beta_second_half": C.rd(s2["beta2"], 3),
        "beta_change_pct": C.pct(s2["change"], 1),
        "eg": C.rd(s3["adf"], 2), "eg_p_text": LAB.fmt_p(s3["p"]),
        "cut5": C.rd(s3["cv5"], 2), "cut_noise": C.rd(s3["cv_noise"], 2),
        "half_life_bars": C.rd(s4["half_life"], 1), "sigma_pct": C.pct(s4["sigma"], 2),
        "crossings_per_year": int(round(s4["crossings"])), "train_per_half_life": C.rd(s4["train_per_hl"], 1),
        "shift_sigma": C.rd(s5["shift"], 2), "sd_ratio": C.rd(s5["sd_ratio"], 2),
        "eg_second_half": C.rd(s5["adf2"], 2), "eg_second_half_p_text": LAB.fmt_p(s5["p2"]),
        "earn_bps": int(round(s6["earn"] * 1e4)), "round_trip_bps": whole(C.bps(s6["cost"], 1)),
        "cost_ratio": C.rd(s6["ratio"], 1),
        "sharpe_lag1": C.rd(s7["sharpe1"], 2), "sharpe_lag2": C.rd(s7["sharpe2"], 2),
        "trades": int(s7["trades"]), "hit_pct": int(round(100 * s7["hit2"])),
        "hit_noise_pts": int(round(s7["hit_noise"])) if math.isfinite(s7["hit_noise"]) else None,
        "max_dd_pct": C.pct(s7["max_dd2"], 1), "ann_return_pct": C.pct(s7["ann_return2"], 2),
        "avg_trade_bps": int(round(s7["avg_trade2"] * 1e4)), "z_sd": C.rd(s7["z_sd"], 2),
        "exam_bars": int(s7["n_test"]), "exam_years": C.rd(s7["years"], 2), "sharpe_margin": C.rd(s7["margin"], 2),
        "sharpe_study": C.rd(s7["sharpe_study"], 2), "trades_study": int(s7["trades_study"]),
    }


def mc_figures(m):
    """สัดส่วนคำตัดสินและสถานะของแต่ละสถานี สำหรับโลกหนึ่งแบบ"""
    out = {"pass_pct": share(m["verdict"] == 0), "warn_pct": share(m["verdict"] == 1),
           "fail_pct": share(m["verdict"] == 2)}
    for j in range(1, 7):
        col = m["status"][:, j]
        out[f"s{j + 1}"] = {"ok_pct": share(col == 0), "warn_pct": share(col == 1), "fail_pct": share(col == 2)}
    out.update({f"sharpe_exam_{k}": v for k, v in spread3(m["sharpe_exam"]).items()})
    out["sharpe_study_med"] = C.rd(float(np.median(m["sharpe_study"])), 1)
    out.update({f"trades_{k}": int(round(v)) for k, v in spread3(m["trades"], 0).items()})
    return out


def selection_figures(sel):
    """การทดลอง C: คู่ fake ที่ผ่านสถานี 3 — Sharpe ช่วงที่ใช้คัด เทียบช่วงสอบ"""
    margin = LAB.SHARPE_Z / math.sqrt(sel["study_years"])
    out = {"screened": sel["screened"], "selected": len(sel["study"]),
           "selected_pct": C.pct(len(sel["study"]) / sel["screened"], 1),
           "study_would_pass_pct": share(sel["study"] - margin > 0),
           "s7_ok_pct": share(sel["s7"] == LAB.OK), "s7_fail_pct": share(sel["s7"] == LAB.FAIL)}
    out.update({f"sharpe_study_{k}": v for k, v in spread3(sel["study"]).items()})
    out.update({f"sharpe_exam_{k}": v for k, v in spread3(sel["exam"]).items()})
    return out


def basket_mc_figures(bm):
    """การทดลอง D: คู่ good ล้วน เทียบกับ ตะกร้า 4 สินทรัพย์ (คู่ good + ขาไม่เกี่ยว 2 ขา)"""
    out = {"worlds": N_BASKET}
    for key, a in bm.items():
        ruler_bad = (a[:, 2] > LAB.SHIFT_MAX_SIGMA) | (a[:, 3] > LAB.SD_RATIO_MAX) | (a[:, 3] < 1 / LAB.SD_RATIO_MAX)
        # ค่ากลางจาก 300 โลกแกว่งตามการสุ่มราว ±0.05 จึงเก็บทศนิยมตำแหน่งเดียว
        out.update({f"eg_{key}_med": C.rd(float(np.median(a[:, 0])), 1), f"pass_{key}_pct": share(a[:, 1] < LAB.P_PASS),
                    f"shift_{key}_med": C.rd(float(np.median(a[:, 2])), 1),
                    f"sd_ratio_{key}_med": C.rd(float(np.median(a[:, 3])), 1),
                    f"ruler_bad_{key}_pct": share(ruler_bad)})
    return out


def threshold_figures():
    """เกณฑ์ของ statarb_lab ตามที่ตั้งไว้ + แบบเปอร์เซ็นต์สำหรับพิมพ์ในเนื้อหา"""
    t = dict(LAB.thresholds())
    for k in ("flat_share_warn", "beta_gap_warn", "beta_change_warn", "p_pass", "p_warn"):
        t[k + "_pct"] = int(round(100 * t[k]))
    t["min_bars"] = 2 * LAB.MIN_HALF_BARS
    t["sd_ratio_min"] = C.rd(1.0 / LAB.SD_RATIO_MAX, 2)
    return {k: whole(v) for k, v in t.items()}


def figures(res=None):
    res = res or run()
    opt = LAB.options()
    sc, bk = res["scan"], res["basket"]
    messy, messy_rep = res["messy"]
    best = sc["found"][0]
    cut = res["cutoff"]
    se = 100 * math.sqrt(0.25 / N_WORLDS)
    h = N_BARS // 2
    return {
        "about": {
            "tool": "tools/statarb_lab.py — เครื่องมือเจ็ดสถานี ใช้ numpy อย่างเดียว เรียกได้ทั้งจากบรรทัดคำสั่งและจากโค้ด",
            "split": "ครึ่งแรกของข้อมูล = ช่วงศึกษา (ประมาณ β, σ และทดสอบสายจูง) · ครึ่งหลัง = ช่วงสอบ "
                     "(สถานี 5 วัดด้วยไม้บรรทัดของครึ่งแรก · สถานี 7 backtest เฉพาะครึ่งหลัง)",
            "demo": "การทดลอง A: รันเครื่องมือกับคู่ตัวอย่างจำลองสี่คู่ 1,500 แท่ง (ถูกเลือกให้เห็นอาการชัด) "
                    "ด้วยค่าตั้งต้น: ต้นทุน 5 bps ต่อขาต่อเที่ยว · entry 2 · exit 0 · train 250 แท่ง · "
                    f"เส้นตัดจาก {LAB.DEFAULT_SIMS:,} โลก",
            "mc": f"การทดลอง B: โลกจำลองแบบละ {N_WORLDS} โลก (1,500 แท่ง · β 1.4 · σ ของ ε 3% · half-life 12 "
                  f"ยกเว้น slow = {SLOW_HALF_LIFE:g}) ผ่านเจ็ดสถานีชุดเดียวกัน นับสัดส่วน ✅ / ⚠️ / ❌ · "
                  f"% คลาดมาตรฐานได้ถึงราว ±{se:.0f} จุด จึงปัดเป็นจำนวนเต็ม",
            "selection": f"การทดลอง C: คู่ fake (ไม่มีสายจูง) {N_SEL:,} คู่ เก็บเฉพาะคู่ที่สถานี 3 ให้ผ่าน "
                         "แล้วเทียบ Sharpe (lag 2) ของ walk-forward ในช่วงที่ใช้คัด (แท่ง 251–750) กับช่วงสอบ (751–1,500)",
            "basket_mc": f"การทดลอง D: {N_BASKET} โลก คู่ good ล้วน เทียบกับคู่ good + random walk อิสระ 2 เส้น "
                         "(4 สินทรัพย์ ทดสอบด้วยเส้นตัดของ 4 สินทรัพย์) · น้ำหนักจากครึ่งแรก วัดครึ่งหลัง",
            "scan": "scan ทดสอบทุกคู่ของ 8 คอลัมน์ในไฟล์ตัวอย่าง (28 คู่) ด้วยครึ่งแรก 750 แท่ง",
            "basket": "basket: Y_good เทียบกับ X_good (ขาจริง) + X_drift, X_fake (ขาที่ไม่เกี่ยว) = 4 สินทรัพย์",
            "messy": "ไฟล์สกปรกจำลอง: คู่ good ที่ใส่ค่าว่าง 2 ช่อง ราคา 0 หนึ่งช่อง วันที่ซ้ำ 1 แถว เรียงใหม่→เก่า "
                     "และ split 2:1 ของ AAA ที่ไม่ได้ปรับราคา",
            "cutoff": f"เส้นตัดและ p-value ในผลลัพธ์ของเครื่องมือมาจากการจำลอง {LAB.DEFAULT_SIMS:,} โลก "
                      f"cutoff.* เทียบกับเส้นตัดอ้างอิงจาก {REF_SIMS:,} โลก ที่ 750 แท่ง · 2 สินทรัพย์ · lags 1",
        },
        "settings": {"n_bars": N_BARS, "half_bars": h, "exam_first_bar": h + 1, "exam_bars": N_BARS - h,
                     "train_bars": opt.train, "refit_bars": LAB.REFIT_BARS, "cost_bps": whole(opt.cost_bps),
                     "round_trip_bps": whole(2 * opt.cost_bps), "entry": whole(opt.entry), "exit": whole(opt.exit),
                     "sims": opt.sims, "worlds": N_WORLDS, "worlds_total": N_WORLDS * len(MC_KINDS),
                     "slow_half_life_bars": whole(SLOW_HALF_LIFE)},
        "thresholds": threshold_figures(),
        "cutoff": {
            "tool_sims": LAB.DEFAULT_SIMS, "ref_sims": REF_SIMS, "bars": h,
            "tool_5pct": C.rd(cut["tool"][0.05], 2), "ref_5pct": C.rd(cut["ref"][0.05], 2),
            "tool_1pct": C.rd(cut["tool"][0.01], 2), "ref_1pct": C.rd(cut["ref"][0.01], 2),
            "tool_10pct": C.rd(cut["tool"][0.1], 2), "ref_10pct": C.rd(cut["ref"][0.1], 2),
            "gap_5pct": C.rd(abs(C.rd(cut["tool"][0.05], 2) - C.rd(cut["ref"][0.05], 2)), 2),
            "noise_5pct": C.rd(cut["noise"], 2),
        },
        "demo": {k: demo_figures(res["demo"][k]) for k in KINDS},
        "mc": dict({k: mc_figures(res["mc"][k]) for k in MC_KINDS}, worlds=N_WORLDS, se_pts=C.rd(se, 1)),
        "selection": selection_figures(res["selection"]),
        "basket_mc": basket_mc_figures(res["basket_mc"]),
        "scan": {
            "pairs": len(sc["found"]), "by_luck": C.rd(LAB.P_PASS * len(sc["found"]), 1),
            "passed_5pct": int(sc["n5"]), "passed_strict": int(sc["n_strict"]), "strict_p": C.rd(sc["strict"], 4),
            "cut5": C.rd(sc["cv5"], 2), "half_bars": int(sc["h"]),
            "best_pair": best[2], "best_eg": C.rd(best[1], 2),
            "cross_pairs": len(sc["found"]) - len(KINDS),
            "cross_passed_5pct": int(sum(p < LAB.P_PASS and nm.split(" ~ ")[0][2:] != nm.split(" ~ ")[1][2:]
                                         for p, _, nm, _, _ in sc["found"])),
        },
        "basket": {
            "n_assets": len(bk["names"]),
            "weights": {nm: C.rd(float(w), 3) for nm, w in zip(bk["names"][1:], bk["eg"]["beta"])},
            "eg": C.rd(bk["eg"]["adf"], 2), "eg_p_text": LAB.fmt_p(bk["eg"]["p"]),
            "cut5": C.rd(bk["eg"]["cv"][0.05], 2), "cut5_pair": C.rd(bk["pair_cv"][0.05], 2),
            "half_life_bars": C.rd(bk["half_life"], 1), "sigma_pct": C.pct(bk["sd1"], 2),
            "shift_sigma": C.rd(bk["shift"], 2), "sd_ratio": C.rd(bk["sd_ratio"], 2),
        },
        "messy": {
            "rows_read": int(messy_rep["rows_read"]), "rows_used": int(messy[0]["m"]["n"]),
            "dropped": int(messy[0]["m"]["dropped"]), "jumps": int(messy[0]["m"]["jumps"]),
            "verdict": LAB.verdict(messy)[0], "verdict_line": LAB.verdict(messy)[1],
            "status": {f"s{s['no']}": s["status"] for s in messy},
            "sharpe_lag2": C.rd(messy[6]["m"]["sharpe2"], 2), "avg_trade_bps": int(round(messy[6]["m"]["avg_trade2"] * 1e4)),
            "shift_sigma": C.rd(messy[4]["m"]["shift"], 1),
        },
        "outputs": dict(res["outputs"]),
    }


# ───────────────────────── กราฟ ─────────────────────────

GROUP = {"data": V.MUTED, "study": V.BLUE, "exam": V.AMBER}


def pipeline_boxes():
    """เนื้อหาของกล่องทั้งเจ็ด: (หมายเลข, ชื่อ, คำถามที่สถานีนั้นตอบ, เกณฑ์ ✅ สองบรรทัด, กลุ่มสี)
    เกณฑ์อ่านจากค่าคงที่ของ statarb_lab จึงตรงกับโปรแกรมเสมอ"""
    return [
        (1, "ข้อมูล", "วัตถุดิบสะอาดและพอไหม",
         (f"มีอย่างน้อย {2 * LAB.MIN_HALF_BARS} แท่ง", "ไม่มีแถวเสีย ไม่มีราคากระโดด"), "data"),
        (2, "β สามวิธี", "ถ่วงกันเท่าไร และนิ่งไหม",
         (f"สามวิธีห่างกัน ≤ {LAB.BETA_GAP_WARN:.0%}", f"สองครึ่งต่างกัน ≤ {LAB.BETA_CHANGE_WARN:.0%}"), "study"),
        (3, "สายจูง", "ε ถูกดึงกลับจริงไหม",
         (f"p-value จำลอง < {LAB.P_PASS:g}", "(เส้นตัดของจำนวนแท่งนี้)"), "study"),
        (4, "จังหวะ", "กลับเร็วและบ่อยแค่ไหน",
         (f"train ≥ {LAB.TRAIN_MIN_HALF_LIVES:g} เท่าของ half-life", f"ข้ามค่าเฉลี่ย ≥ {LAB.CROSSINGS_MIN_PER_YEAR:g} ครั้ง/ปี"),
         "study"),
        (5, "สองครึ่ง", "ไม้บรรทัดเดิมยังใช้ได้ไหม",
         (f"ค่าเฉลี่ยเลื่อน ≤ {LAB.SHIFT_MAX_SIGMA:g}σ", f"ความกว้าง {1 / LAB.SD_RATIO_MAX:.2f}–{LAB.SD_RATIO_MAX:g} เท่า"), "exam"),
        (6, "ต้นทุน", "หนึ่งรอบเหลือกำไรไหม",
         (f"ได้ ≥ {LAB.COST_RATIO_OK:g} เท่าของต้นทุน 2c", "(entry − exit)·σ/(1+|β|)"), "study"),
        (7, "เดินหน้า", "รอดในช่วงสอบไหม",
         (f"Sharpe lag 2 − {LAB.SHARPE_Z}/√ปี > 0", f"เทรดเฉพาะครึ่งหลัง · ≥ {LAB.MIN_TRADES} ไม้"), "exam"),
    ]


def arrow_line(x1, y1, x2, y2, head):
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{V.MUTED}" '
            f'stroke-width="1.6" marker-end="url(#{head})"/>')


def chart_pipeline():
    """แผนผังเจ็ดสถานี (กล่องกับลูกศร ไม่มีข้อมูล)"""
    fig = V.Fig("sas-p8-pipeline", w=760, h=394)
    bw, bh, gap, x0 = 170.0, 112.0, 20.0, 10.0
    row_y = (44.0, 206.0)
    head = fig.uid("arrow")
    fig.defs.append(f'<marker id="{head}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" '
                    f'orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{V.MUTED}"/></marker>')
    fig.title("เจ็ดสถานีของคำสั่ง check", sub="แต่ละกล่อง: คำถามที่สถานีนั้นตอบ และเกณฑ์ผ่าน")

    def corner(i):
        return x0 + (i % 4) * (bw + gap), row_y[i // 4]

    for i, (no, name, ask, rule, grp) in enumerate(pipeline_boxes()):
        x, y = corner(i)
        color = GROUP[grp]
        fig.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.0f}" height="{bh:.0f}" rx="9" '
                f'fill="{V.mix(color, "#ffffff", 0.91)}" stroke="{color}" stroke-width="1.3"/>',
                f'<circle cx="{x + 20:.1f}" cy="{y + 21:.1f}" r="11.5" fill="{color}"/>',
                V.text(x + 20, y + 25.5, str(no), size=13, color="#ffffff", anchor="middle", weight=700),
                V.text(x + 39, y + 26, name, size=13.5, color=V.DARK, weight=700),
                V.text(x + 12, y + 51, ask, size=12, color=V.INK),
                f'<line x1="{x + 12:.1f}" y1="{y + 62:.1f}" x2="{x + bw - 12:.1f}" y2="{y + 62:.1f}" '
                f'stroke="{V.mix(color, "#ffffff", 0.55)}" stroke-width="1"/>',
                V.text(x + 12, y + 80, rule[0], size=10.8, color=V.INK),
                V.text(x + 12, y + 97, rule[1], size=10.8, color=V.MUTED))
        if i % 4 != 3 and i != 6:                           # ลูกศรไปกล่องถัดไปในแถวเดียวกัน
            fig.add(arrow_line(x + bw + 2, y + bh / 2, x + bw + gap - 2, y + bh / 2, head))
    # ลูกศรหักมุมจากสถานี 4 ลงไปสถานี 5
    x4, y4 = corner(3)
    x5, y5 = corner(4)
    mid = (y4 + bh + y5) / 2
    fig.add(f'<path d="M{x4 + bw / 2:.1f},{y4 + bh + 2:.1f} V{mid:.1f} H{x5 + bw / 2:.1f} V{y5 - 3:.1f}" fill="none" '
            f'stroke="{V.MUTED}" stroke-width="1.6" marker-end="url(#{head})"/>',
            V.text((x4 + x5 + bw) / 2, mid - 7, "ไม้บรรทัด (α, β, σ) จากครึ่งแรก ถูกนำไปสอบกับครึ่งหลัง",
                   size=10.8, color=V.MUTED, anchor="middle", halo=True))
    # ลูกศรจากสถานี 7 ไปกล่องคำตัดสิน
    x7, y7 = corner(6)
    xv, yv = corner(7)
    fig.add(arrow_line(x7 + bw + 2, y7 + bh / 2, xv - 2, yv + bh / 2, head),
            f'<rect x="{xv:.1f}" y="{yv:.1f}" width="{bw:.0f}" height="{bh:.0f}" rx="9" fill="#ffffff" '
            f'stroke="{V.DARK}" stroke-width="1.6"/>',
            V.text(xv + 12, yv + 26, "คำตัดสิน", size=13.5, color=V.DARK, weight=700))
    for j, (color, label) in enumerate(((V.GREEN, "ผ่านครบ → ศึกษาต่อได้"), (V.AMBER, "มีข้อสังเกต → อ่านก่อนไปต่อ"),
                                        (V.RED, "ไม่ผ่าน → ดู “ลองอะไรต่อ”"))):
        yy = yv + 50 + 20 * j
        fig.add(f'<circle cx="{xv + 18:.1f}" cy="{yy - 4:.1f}" r="5" fill="{color}"/>',
                V.text(xv + 30, yy, label, size=11.2, color=V.INK))
    fig.legend([("ตรวจวัตถุดิบ", GROUP["data"], "rect"), ("วัดจากครึ่งแรก (ช่วงศึกษา)", GROUP["study"], "rect"),
                ("สอบกับครึ่งหลัง (ข้อมูลที่ช่วงศึกษายังไม่เคยเห็น)", GROUP["exam"], "rect")], 12, 352)
    fig.text(12, 378, "ไม่ผ่านที่สถานีไหน เครื่องมือจะบอกชื่อสถานีแรกที่ติด พร้อมคำแนะนำ “ลองอะไรต่อ” ของสถานีนั้น",
             size=11, color=V.MUTED)
    return fig.svg(
        "แผนผังเจ็ดสถานีของคำสั่ง check: ข้อมูล, β สามวิธี, สายจูง, จังหวะ, สองครึ่ง, ต้นทุน, เดินหน้า "
        "แล้วจบที่คำตัดสิน ผ่านครบ มีข้อสังเกต หรือไม่ผ่าน",
        "แผนผัง (ไม่ใช่ข้อมูล) · อ่านซ้ายไปขวาแล้วลงแถวล่าง · สถานี 2–4 และ 6 ดูเฉพาะ<b>ครึ่งแรก</b>ของข้อมูล "
        "ส่วนสถานี 5 กับ 7 คือการ<b>สอบกับครึ่งหลัง</b> (สถานี 7 backtest เฉพาะครึ่งหลัง เพราะช่วงที่ใช้ตัดสินว่ามีสายจูง "
        "มักจะดูดีเกินจริง) · ตัวเลขในกล่องคือเกณฑ์ที่ตั้งไว้ที่หัวไฟล์ <code>statarb_lab.py</code> แก้ได้ที่เดียว")


def pct_of(mask):
    return float(np.mean(mask)) * 100


def chart_verdicts(res):
    """คำตัดสินรวมของเครื่องมือ ต่อแบบของโลก (การทดลอง B)"""
    mc = res["mc"]
    bars = [{"label": KIND_TH[k].replace(" — ", "\n"),
             "values": [pct_of(mc[k]["verdict"] == c) for c in (0, 1, 2)]} for k in MC_KINDS]
    good_pass, slow_pass = pct_of(mc["good"]["verdict"] == 0), pct_of(mc["slow"]["verdict"] == 0)
    slow_fail = pct_of(mc["slow"]["verdict"] == 2)
    fake_fail, break_fail = pct_of(mc["fake"]["verdict"] == 2), pct_of(mc["break"]["verdict"] == 2)
    good_fail = pct_of(mc["good"]["verdict"] == 2)
    return V.stacked_bars(
        "sas-p8-verdicts", bars, ["ผ่านครบ 7 สถานี", "ผ่านแบบมีข้อสังเกต", "ไม่ผ่าน"],
        f"แท่งซ้อนแนวนอนห้าแท่ง แสดงสัดส่วนคำตัดสินของเครื่องมือในโลกจำลองแบบละ {N_WORLDS} โลก: "
        f"โลก good ผ่านครบ {good_pass:.0f}% โลก fake ไม่ผ่าน {fake_fail:.0f}% โลก slow ผ่านครบ {slow_pass:.0f}%",
        f"ข้อมูลจำลอง · แบบละ {N_WORLDS} โลก โลกละ 1,500 แท่ง ผ่านเจ็ดสถานีด้วยค่าตั้งต้น (ตัวเลขคลาดได้ราว ±3 จุด) · "
        f"สายจูงจริงแบบเร็ว (good) ผ่านครบ <b>{good_pass:.0f}%</b> และไม่ผ่านเลย {good_fail:.0f}% · "
        f"ไม่มีสายจูง (fake) ถูกจับได้ <b>{fake_fail:.0f}%</b> · สายจูงขาด (break) ถูกจับได้ {break_fail:.0f}% · "
        "drift เกือบทั้งหมดได้ “มีข้อสังเกต” ตรงกับเฉลย (สายจูงยังอยู่ แต่ β ต้องประมาณใหม่เป็นรอบ ๆ) · "
        f"แถวล่างสุดสำคัญ: สายจูง<b>จริง</b>ที่ช้าลง (half-life 30) ผ่านครบแค่ {slow_pass:.0f}% และไม่ผ่านถึง "
        f"{slow_fail:.0f}% — ไม่ผ่านจึงแปลว่า “ข้อมูลชุดนี้ยืนยันไม่ได้” ไม่ใช่ “พิสูจน์แล้วว่าไม่มีสายจูง”",
        colors=[V.GREEN, V.AMBER, V.RED], xlabel="สัดส่วนของโลกจำลอง")


def chart_stations(res):
    """สถานีไหนจับอาการไหน: % ของโลกที่สถานีนั้น "ไม่ให้ ✅" (⚠️ หรือ ❌)"""
    mc = res["mc"]
    cols = ["2\nβ", "3\nสายจูง", "4\nจังหวะ", "5\nสองครึ่ง", "6\nต้นทุน", "7\nเดินหน้า"]
    values = [[pct_of(mc[k]["status"][:, j] != 0) for j in range(1, 7)] for k in MC_KINDS]
    s5_break = pct_of(mc["break"]["status"][:, 4] == 2)
    s7_break = pct_of(mc["break"]["status"][:, 6] != 0)
    s7_good = pct_of(mc["good"]["status"][:, 6] != 0)
    s3_slow = pct_of(mc["slow"]["status"][:, 2] != 0)
    return V.heat_table(
        "sas-p8-stations", [KIND_TH[k].replace(" — ", "\n") for k in MC_KINDS], cols, values,
        "ตารางสี: แถวคือแบบของโลกจำลอง คอลัมน์คือสถานี 2 ถึง 7 ค่าในช่องคือเปอร์เซ็นต์ของโลกที่สถานีนั้นไม่ให้ผ่านสะอาด",
        f"ข้อมูลจำลอง · แบบละ {N_WORLDS} โลก · ตัวเลข = % ของโลกที่สถานีนั้น<b>ไม่ให้ผ่านสะอาด</b> (เตือนหรือไม่ผ่าน) · "
        "แต่ละอาการมีสถานีของมัน: fake ติดที่สถานี 3 · drift ติดที่สถานี 2 และ 5 · "
        f"break ติดที่สถานี 5 (ไม่ผ่าน {s5_break:.0f}%) และสถานี 7 ({s7_break:.0f}%) · "
        f"ราคาของความรอบคอบ: สถานี 7 เตือนโลก good ด้วย {s7_good:.0f}% (สามปีของช่วงสอบยังแยกจากโชคไม่ได้เสมอ) "
        f"และสถานี 3 ไม่ให้ผ่าน {s3_slow:.0f}% ของสายจูงจริงที่ช้า · "
        "สถานี 4 และ 6 ของโลก fake เตือนตามสถานี 3 (ตัวเลขของมันเชื่อไม่ได้เมื่อไม่มีสายจูง)",
        scale="seq", fmt="{:.0f}%", row_title="แบบของโลก", col_title="สถานี", lo=0, hi=100, color=V.RED)


def chart_selection(res):
    """การทดลอง C: Sharpe ของ walk-forward ในช่วงที่ใช้คัด เทียบกับช่วงสอบ (ค่ากลางและช่วง 5–95%)"""
    sel, mc = res["selection"], res["mc"]

    def row(label, values, color):
        lo, mid, hi = np.percentile(values, [5, 50, 95])
        return {"label": label, "mid": float(mid), "lo": float(lo), "hi": float(hi), "color": color}

    n_sel = len(sel["study"])
    rows = [row(f"fake ที่บังเอิญผ่านสถานี 3\nช่วงศึกษา (ช่วงที่ใช้คัด)", sel["study"], V.RED),
            row("fake ที่บังเอิญผ่านสถานี 3\nช่วงสอบ", sel["exam"], V.MUTED),
            row("good — ช่วงศึกษา", mc["good"]["sharpe_study"], V.BLUE),
            row("good — ช่วงสอบ", mc["good"]["sharpe_exam"], V.BLUE),
            row("break — ช่วงศึกษา", mc["break"]["sharpe_study"], V.AMBER),
            row("break — ช่วงสอบ", mc["break"]["sharpe_exam"], V.AMBER)]
    med_study, med_exam = float(np.median(sel["study"])), float(np.median(sel["exam"]))
    return V.dot_interval(
        "sas-p8-selection", rows,
        "จุดและเส้นช่วง แสดง Sharpe lag 2 ของ backtest แบบเดินหน้า ในช่วงศึกษากับช่วงสอบ ของคู่ที่ไม่มีสายจูงแต่ผ่านสถานี 3 "
        f"ค่ากลาง {med_study:.1f} กับ {med_exam:.1f} เทียบกับโลก good และ break",
        f"ข้อมูลจำลอง · คู่ไม่มีสายจูง {N_SEL:,} คู่ ผ่านสถานี 3 มาได้ {n_sel} คู่ (บังเอิญล้วน ๆ) · "
        f"backtest ของคู่พวกนี้ในช่วงที่ใช้คัดได้ Sharpe ค่ากลาง <b>{med_study:.1f}</b> แต่ช่วงสอบเหลือ "
        f"<b>{med_exam:.1f}</b> — กำไรช่วงแรกเป็นเงาของการคัดเลือก ไม่ใช่สายจูง · คู่ good ได้พอ ๆ กันทั้งสองช่วง "
        f"ส่วน break ดีเฉพาะช่วงก่อนขาด · จึงตัดสินสถานี 7 จากช่วงสอบเท่านั้น (โลก good / break แบบละ {N_WORLDS} โลก)",
        zero=True, xlabel="Sharpe ต่อปี (lag 2 หลังหักต้นทุน 5 bps ต่อขาต่อเที่ยว)",
        fmt=lambda v: f"{v:.1f}")


def charts(res=None):
    res = res or run()
    return {
        "sas-p8-pipeline": chart_pipeline(),
        "sas-p8-verdicts": chart_verdicts(res),
        "sas-p8-stations": chart_stations(res),
        "sas-p8-selection": chart_selection(res),
    }


# ───────────────────────── สรุปเมื่อรันตรง ๆ ─────────────────────────

def main():
    f = figures()
    s, t = f["settings"], f["thresholds"]
    print("ตอนที่ 8 — ห้องทดลองเจ็ดสถานี (tools/statarb_lab.py) · ข้อมูลจำลองทั้งหมด")
    print(f"ค่าตั้งต้น: ต้นทุน {s['cost_bps']} bps ต่อขาต่อเที่ยว · entry {s['entry']} · exit {s['exit']} · "
          f"train {s['train_bars']} แท่ง · ประมาณใหม่ทุก {s['refit_bars']} แท่ง · จำลอง {s['sims']:,} โลกหาเส้นตัด")
    print(f"ครึ่งแรก (แท่ง 1–{s['half_bars']:,}) = ช่วงศึกษา · ครึ่งหลัง (แท่ง {s['exam_first_bar']:,}–{s['n_bars']:,}) = ช่วงสอบ "
          "· สถานี 7 backtest เฉพาะช่วงสอบ")
    print(f"เกณฑ์หลัก: β สามวิธีห่างกัน ≤ {t['beta_gap_warn_pct']}% · β สองครึ่งต่างกัน ≤ {t['beta_change_warn_pct']}% · "
          f"p < {t['p_pass']} · train ≥ {t['train_min_half_lives']} เท่าของ half-life · เลื่อน ≤ {t['shift_max_sigma']}σ · "
          f"กว้าง ≤ {t['sd_ratio_max']} เท่า · กำไรต่อรอบ ≥ {t['cost_ratio_ok']} เท่าของ 2c · "
          f"Sharpe lag 2 − {t['sharpe_z']}/√ปี > 0 และ ≥ {t['min_trades']} ไม้")
    c = f["cutoff"]
    print(f"เส้นตัด 5% ที่ {c['bars']} แท่ง: เครื่องมือ ({c['tool_sims']:,} โลก) {c['tool_5pct']} · อ้างอิง "
          f"({c['ref_sims']:,} โลก) {c['ref_5pct']} · ต่างกัน {c['gap_5pct']} (เครื่องมือบอกเองว่าคลาดได้ราว ±{c['noise_5pct']})")
    print()
    print("การทดลอง A — คู่ตัวอย่างสี่คู่ (ถูกเลือกให้เห็นอาการชัด)")
    print("  คู่     สถานี 1-7        β      EG      p     HL   เลื่อน   กว้าง   สอบ lag1/lag2  ไม้ | ศึกษา   คำตัดสิน")
    for k in KINDS:
        d = f["demo"][k]
        icons = " ".join(d["status"][f"s{i}"] for i in range(1, 8))
        print(f"  {k:<6s} {icons}  {d['beta']:6.3f}  {d['eg']:6.2f}  {d['eg_p_text']:>7s}  {d['half_life_bars']:5.1f}  "
              f"{d['shift_sigma']:+5.2f}σ  {d['sd_ratio']:5.2f}   {d['sharpe_lag1']:5.2f} / {d['sharpe_lag2']:5.2f}  "
              f"{d['trades']:3d} | {d['sharpe_study']:5.2f}   {d['verdict_line']}")
    sc, bk, ms = f["scan"], f["basket"], f["messy"]
    print(f"  scan: ทดสอบ {sc['pairs']} คู่ด้วยครึ่งแรก {sc['half_bars']} แท่ง · คาดว่าผ่านด้วยโชค {sc['by_luck']} คู่ · "
          f"ผ่าน 5% จริง {sc['passed_5pct']} คู่ (เป็นคู่ไขว้ที่ไม่เกี่ยวกัน {sc['cross_passed_5pct']} จาก {sc['cross_pairs']}) · "
          f"ผ่านเกณฑ์เข้ม p < {sc['strict_p']}: {sc['passed_strict']} คู่")
    print(f"  basket ({bk['n_assets']} สินทรัพย์): EG {bk['eg']} เทียบเส้นตัด 5% {bk['cut5']} (ของคู่ธรรมดา {bk['cut5_pair']}) · "
          f"half-life {bk['half_life_bars']} แท่ง · σ {bk['sigma_pct']}% · ครึ่งหลัง ε เลื่อน {bk['shift_sigma']:+}σ "
          f"กว้าง {bk['sd_ratio']} เท่า (คู่ธรรมดา: {f['demo']['good']['shift_sigma']:+}σ · {f['demo']['good']['sd_ratio']} เท่า)")
    print(f"  ไฟล์สกปรก: อ่าน {ms['rows_read']:,} แถว ใช้ได้ {ms['rows_used']:,} ทิ้ง {ms['dropped']} · ราคากระโดด {ms['jumps']} จุด "
          f"· Sharpe ช่วงสอบ {ms['sharpe_lag2']} (+{ms['avg_trade_bps']} bps ต่อไม้) → {ms['verdict_line']}")
    print()
    print(f"การทดลอง B — เครื่องมือเชื่อได้แค่ไหน (แบบละ {f['mc']['worlds']} โลก · 1,500 แท่ง · % คลาดได้ราว ±{f['mc']['se_pts']} จุด)")
    print("  แบบ     ผ่านครบ มีข้อสังเกต ไม่ผ่าน |  % ที่สถานีไม่ให้ ✅ (2  3  4  5  6  7) |  "
          "Sharpe ช่วงสอบ: กลาง (5–95%) · ช่วงศึกษา   ไม้ช่วงสอบ")
    for k in MC_KINDS:
        m = f["mc"][k]
        flagged = " ".join(f"{100 - m[f's{j}']['ok_pct']:3d}" for j in range(2, 8))
        print(f"  {k:<6s}  {m['pass_pct']:5d}%  {m['warn_pct']:5d}%   {m['fail_pct']:5d}%  |  {flagged}  |  "
              f"{m['sharpe_exam_med']:4.1f} ({m['sharpe_exam_p05']:4.1f} ถึง {m['sharpe_exam_p95']:4.1f}) · "
              f"{m['sharpe_study_med']:4.1f}      {m['trades_med']} ({m['trades_p05']}–{m['trades_p95']})")
    se = f["selection"]
    print()
    print(f"การทดลอง C — คู่ไม่มีสายจูง {se['screened']:,} คู่ ผ่านสถานี 3 มาได้ {se['selected']} คู่ ({se['selected_pct']}%)")
    print(f"  Sharpe lag 2 ช่วงที่ใช้คัด: {se['sharpe_study_med']} ({se['sharpe_study_p05']} ถึง {se['sharpe_study_p95']}) · "
          f"ช่วงสอบ: {se['sharpe_exam_med']} ({se['sharpe_exam_p05']} ถึง {se['sharpe_exam_p95']})")
    print(f"  ถ้าตัดสินจากช่วงที่ใช้คัด ผ่านเกณฑ์ Sharpe {se['study_would_pass_pct']}% · สถานี 7 (ช่วงสอบ) ให้ ✅ "
          f"{se['s7_ok_pct']}% และ ❌ {se['s7_fail_pct']}%")
    bm = f["basket_mc"]
    print()
    print(f"การทดลอง D — คู่ good ล้วน เทียบกับ + ขาไม่เกี่ยว 2 ขา ({bm['worlds']} โลก · ค่ากลาง)")
    print(f"  EG ครึ่งแรก {bm['eg_pair_med']} → {bm['eg_basket_med']} · ผ่านเส้นตัดของตัวเอง {bm['pass_pair_pct']}% → "
          f"{bm['pass_basket_pct']}% · |เลื่อน| ครึ่งหลัง {bm['shift_pair_med']}σ → {bm['shift_basket_med']}σ · "
          f"กว้าง {bm['sd_ratio_pair_med']} → {bm['sd_ratio_basket_med']} เท่า · ไม้บรรทัดเพี้ยน "
          f"{bm['ruler_bad_pair_pct']}% → {bm['ruler_bad_basket_pct']}%")
    print()
    print("ผลลัพธ์ของโปรแกรม (เก็บตรงตัวใต้ outputs.*): " + ", ".join(f"{k} {len(v.splitlines())} บรรทัด"
                                                            for k, v in f["outputs"].items()))
    print("กราฟ: " + ", ".join(charts()))


if __name__ == "__main__":
    main()
