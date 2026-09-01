#!/usr/bin/env python3
"""สร้าง docs/live-backtest-figures.json — ตัวเลขของบท "live กับ backtest ไม่ตรงกัน"

วัดสามอย่างที่ backtest ทั่วไปมองไม่เห็น จากข้อมูล option chain จริงในคลังนี้
  1. สภาพคล่องทั้งกระดาน (ไม่ใช่แค่ใกล้ ATM) — มีกี่สัญญาที่ backtest "เทรดได้" แต่จริง ๆ เทรดไม่ได้
  2. ต้นทุนซ่อนจากการสมมติ fill ที่ราคากลาง (mid) แทนราคาที่ต้องจ่ายจริง — ต่อยอดจาก
     nq-figures.json::ต้นทุนตามอายุ (Part 5) ซึ่งคำนวณส่วนต่าง bid-ask ไว้แล้ว ไม่คำนวณซ้ำ
  3. ตัวอย่างกระทบยอดหนึ่งไม้ — เทียบราคาที่ backtest มักสมมติ กับราคาที่ต้องจ่ายจริงในสัญญาเดียว

ต้องมี nq-figures.json อยู่แล้ว (รัน nq_figures.py ก่อนถ้ายังไม่มี)
    python3 tools/live_backtest_figures.py
"""

import csv
import datetime
import glob
import json
import os
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "live-backtest-figures.json")
NQ_FIGURES = os.path.join(ROOT, "docs", "nq-figures.json")
DATA_DIR = os.environ.get(
    "NQ_DATA_DIR",
    os.path.join(ROOT, "data") if os.path.isdir(os.path.join(ROOT, "data"))
    else os.path.join(ROOT, "..", "options-data", "data"),
)
DAY = "2026-08-29"
BAND = 0.05


def _board_liquidity(day):
    """สภาพคล่องทั้งกระดาน (ทุกสัญญา ทุก underlying) ไม่จำกัดแค่ใกล้ ATM"""
    out = {}
    for venue in ("deribit", "okx"):
        path = os.path.join(DATA_DIR, venue, day[:4], day[5:7], day + ".csv")
        if not os.path.exists(path):
            continue
        total = zero_vol = no_bid = mark_outside = 0
        with open(path) as fh:
            for row in csv.DictReader(fh):
                total += 1
                try:
                    bid = float(row["bid"] or 0)
                    ask = float(row["ask"] or 0)
                    mark = float(row["mark_price"] or 0)
                    vol = float(row["volume_24h"] or 0)
                except (ValueError, KeyError):
                    continue
                if vol == 0:
                    zero_vol += 1
                if bid <= 0:
                    no_bid += 1
                if bid > 0 and ask > 0 and (mark < bid or mark > ask):
                    mark_outside += 1
        out[venue] = {
            "สัญญาทั้งหมด": total,
            "ไม่มีปริมาณซื้อขาย24ชม": zero_vol,
            "ไม่มีปริมาณซื้อขาย24ชมเปอร์เซ็นต์": round(100 * zero_vol / total, 1),
            "ไม่มีราคาเสนอซื้อ": no_bid,
            "ไม่มีราคาเสนอซื้อเปอร์เซ็นต์": round(100 * no_bid / total, 1),
            "markอยู่นอกช่วงbidask": mark_outside,
        }
    return out


def _hidden_cost_from_mid(cost_by_age):
    """ต้นทุนซ่อนถ้า backtest สมมติ fill ที่ราคากลาง — ครึ่งหนึ่งของส่วนต่าง bid-ask ตามอายุ

    ไม่คำนวณ spread ใหม่ ใช้ตัวเลขที่มีอยู่แล้วใน nq-figures.json::ต้นทุนตามอายุ (Part 5)
    เพราะ half-spread คือระยะห่างจาก mid ไปยัง bid หรือ ask ฝั่งใดฝั่งหนึ่ง
    """
    out = {}
    for venue, v in cost_by_age.get("ตลาด", {}).items():
        out[venue] = {name: round(b["ส่วนต่างกลางเปอร์เซ็นต์"] / 2, 1)
                      for name, b in v.get("ตามอายุคงเหลือ", {}).items()}
    return out


def _fill_example(day):
    """เลือกสัญญาใกล้ ATM หนึ่งตัวจาก deribit มาเป็นตัวอย่างกระทบยอด"""
    path = os.path.join(DATA_DIR, "deribit", day[:4], day[5:7], day + ".csv")
    best = None
    with open(path) as fh:
        for row in csv.DictReader(fh):
            if row["underlying"] != "BTC" or row["type"] != "call":
                continue
            try:
                bid, ask = float(row["bid"] or 0), float(row["ask"] or 0)
                spot, strike = float(row["underlying_price"]), float(row["strike"])
                ey, em, ed = map(int, row["expiry"].split("-"))
            except (ValueError, KeyError):
                continue
            if bid <= 0 or ask <= 0:
                continue
            dte = (datetime.date(ey, em, ed) - datetime.date(*map(int, day.split("-")))).days
            if not (5 <= dte <= 45) or abs(strike / spot - 1) > 0.05:
                continue
            cand = {"สัญญา": row["instrument"], "dte": dte,
                    "bidดอลลาร์": round(bid * spot), "askดอลลาร์": round(ask * spot),
                    "midดอลลาร์": round((bid + ask) / 2 * spot)}
            if best is None or abs(cand["dte"] - 21) < abs(best["dte"] - 21):
                best = cand
    if not best:
        return None
    contracts = 1
    backtest_cost = best["midดอลลาร์"] * contracts
    live_buy_cost = best["askดอลลาร์"] * contracts
    live_sell_proceeds = best["bidดอลลาร์"] * contracts
    return {
        **best,
        "วันที่": day,
        "สมมติซื้อกี่สัญญา": contracts,
        "backtestสมมติจ่ายดอลลาร์": backtest_cost,
        "ซื้อจริงต้องจ่ายดอลลาร์": live_buy_cost,
        "ถ้าขายคืนทันทีได้ดอลลาร์": live_sell_proceeds,
        "ส่วนต่างซื้อแล้วขายคืนทันทีดอลลาร์": live_buy_cost - live_sell_proceeds,
        "ส่วนต่างซื้อแล้วขายคืนทันทีเปอร์เซ็นต์": round(100 * (live_buy_cost - live_sell_proceeds) / backtest_cost, 1),
    }


def _tracking_error_budget(day, band=BAND):
    """การกระจายของ (ask-mid)/mid บนสัญญาใกล้ ATM ทั้งหมดในวันนั้น — ใช้ตั้งเพดาน tracking error"""
    path = os.path.join(DATA_DIR, "deribit", day[:4], day[5:7], day + ".csv")
    gaps = []
    with open(path) as fh:
        for row in csv.DictReader(fh):
            if row["underlying"] != "BTC":
                continue
            try:
                bid, ask = float(row["bid"] or 0), float(row["ask"] or 0)
                spot, strike = float(row["underlying_price"]), float(row["strike"])
            except (ValueError, KeyError):
                continue
            if bid <= 0 or ask <= 0 or abs(strike / spot - 1) > band:
                continue
            mid = (bid + ask) / 2
            gaps.append(100 * (ask - mid) / mid)
    gaps.sort()
    n = len(gaps)
    pct = lambda q: round(gaps[min(n - 1, int(q * n))], 1)
    return {"จำนวนสัญญา": n, "p25": pct(.25), "p50": pct(.50), "p75": pct(.75), "p90": pct(.90), "p99": pct(.99)}


def build():
    with open(NQ_FIGURES) as fh:
        nq = json.load(fh)
    cost_by_age = nq.get("ต้นทุนตามอายุ", {})

    return {
        "_อ่านก่อน": "สร้างด้วย tools/live_backtest_figures.py — ห้ามแก้ด้วยมือ · ใช้ nq-figures.json::ต้นทุนตามอายุ ร่วมด้วย ไม่คำนวณ spread ซ้ำ",
        "ข้อมูล": {"วันที่ตรวจ": DAY, "ตลาด": ["deribit", "okx"]},
        "สภาพคล่องทั้งกระดาน": _board_liquidity(DAY),
        "ต้นทุนซ่อนจากใช้midpriceเปอร์เซ็นต์": _hidden_cost_from_mid(cost_by_age),
        "ตัวอย่างกระทบยอดหนึ่งไม้": _fill_example(DAY),
        "งบtrackingError": _tracking_error_budget(DAY),
    }


if __name__ == "__main__":
    _args = sys.argv[1:]
    if "--data-dir" in _args:
        _i = _args.index("--data-dir")
        DATA_DIR = _args[_i + 1]
    if not os.path.isdir(DATA_DIR):
        sys.exit(f"ไม่พบโฟลเดอร์ข้อมูล: {DATA_DIR}\n"
                 f"ระบุตำแหน่งด้วย --data-dir <path> หรือตัวแปรแวดล้อม NQ_DATA_DIR "
                 f"(ต้องมี deribit/ และ okx/ อยู่ข้างใน)")
    if not os.path.exists(NQ_FIGURES):
        sys.exit(f"ไม่พบ {NQ_FIGURES} — รัน tools/nq_figures.py ก่อน")
    with open(OUT, "w") as fh:
        json.dump(build(), fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("เขียน", os.path.relpath(OUT, ROOT))
