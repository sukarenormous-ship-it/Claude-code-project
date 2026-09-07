#!/usr/bin/env python3
"""ตรวจสุขภาพข้อมูล option chain — สคริปต์ที่ผู้อ่านรันกับข้อมูลของตัวเองได้

ใช้กับบท "ข้อมูลที่ใช้ทดสอบเชื่อได้แค่ไหน" — ไม่ใช่แค่สคริปต์สร้างตัวเลขให้บทนี้
แต่ออกแบบให้เป็นเครื่องมืออิสระที่รันกับข้อมูล option chain รูปแบบเดียวกัน
(โฟลเดอร์ <venue>/<YYYY>/<MM>/<YYYY-MM-DD>.csv คอลัมน์ตาม schema ของคลังนี้) ที่ไหนก็ได้

ตรวจสี่เรื่อง: ① ความครบของวันที่ (มีวันที่ขาดหายไหม) ② ผู้รอดชีวิต (สัญญาวันแรกเหลือกี่ตัววันสุดท้าย)
③ สภาพคล่อง (ไม่มีปริมาณซื้อขาย/ไม่มีราคาเสนอซื้อ/mark อยู่นอกช่วง bid-ask)
④ ราคาข้ามตลาด (ถ้ามีมากกว่าหนึ่งตลาด ราคา underlying ต่างกันแค่ไหนในวันเดียวกัน)

ใช้กับข้อมูลของตัวเอง:
    python3 tools/data_health.py --data-dir /path/to/your/data
ใช้กับข้อมูลของคลังนี้ (เขียน docs/data-quality-figures.json ด้วย):
    python3 tools/data_health.py
"""

import csv
import datetime
import glob
import json
import os
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "data-quality-figures.json")
DATA_DIR = os.environ.get(
    "NQ_DATA_DIR",
    os.path.join(ROOT, "data") if os.path.isdir(os.path.join(ROOT, "data"))
    else os.path.join(ROOT, "..", "options-data", "data"),
)


def _venues(data_dir):
    return sorted(d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d)))


def _days(data_dir, venue):
    return sorted(os.path.basename(p)[:-4]
                  for p in glob.glob(os.path.join(data_dir, venue, "*", "*", "*.csv")))


def date_coverage(data_dir, venue):
    days = _days(data_dir, venue)
    if not days:
        return None
    d0 = datetime.date(*map(int, days[0].split("-")))
    d1 = datetime.date(*map(int, days[-1].split("-")))
    expected = {(d0 + datetime.timedelta(i)).isoformat() for i in range((d1 - d0).days + 1)}
    missing = sorted(expected - set(days))
    return {"วันแรก": days[0], "วันสุดท้าย": days[-1], "จำนวนวันที่มีไฟล์": len(days),
            "จำนวนวันที่ควรมี": len(expected), "วันที่ขาดหาย": missing, "จำนวนวันที่ขาดหาย": len(missing)}


def survivorship(data_dir, venue, underlying="BTC"):
    days = _days(data_dir, venue)
    if not days:
        return None

    def names(day):
        path = os.path.join(data_dir, venue, day[:4], day[5:7], day + ".csv")
        with open(path) as fh:
            return {r["instrument"] for r in csv.DictReader(fh) if r["underlying"] == underlying}

    first, last = names(days[0]), names(days[-1])
    stay = first & last
    return {"underlying": underlying, "วันแรก": days[0], "วันสุดท้าย": days[-1],
            "จำนวนวันแรก": len(first), "จำนวนวันสุดท้าย": len(last), "อยู่ครบทั้งสองวัน": len(stay),
            "สัดส่วนที่รอดเปอร์เซ็นต์": round(100 * len(stay) / len(first), 1) if first else None}


def liquidity(data_dir, venue, day):
    path = os.path.join(data_dir, venue, day[:4], day[5:7], day + ".csv")
    if not os.path.exists(path):
        return None
    total = zero_vol = no_bid = mark_outside = 0
    with open(path) as fh:
        for row in csv.DictReader(fh):
            total += 1
            try:
                bid, ask = float(row["bid"] or 0), float(row["ask"] or 0)
                mark, vol = float(row["mark_price"] or 0), float(row["volume_24h"] or 0)
            except (ValueError, KeyError):
                continue
            if vol == 0:
                zero_vol += 1
            if bid <= 0:
                no_bid += 1
            if bid > 0 and ask > 0 and (mark < bid or mark > ask):
                mark_outside += 1
    return {"วันที่": day, "สัญญาทั้งหมด": total,
            "ไม่มีปริมาณซื้อขาย24ชมเปอร์เซ็นต์": round(100 * zero_vol / total, 1) if total else None,
            "ไม่มีราคาเสนอซื้อเปอร์เซ็นต์": round(100 * no_bid / total, 1) if total else None,
            "markอยู่นอกช่วงbidask": mark_outside}


def cross_venue_price_diff(data_dir, venues, underlying="BTC"):
    if len(venues) < 2:
        return None
    per_venue = {}
    for v in venues:
        prices = {}
        for path in sorted(glob.glob(os.path.join(data_dir, v, "*", "*", "*.csv"))):
            day = os.path.basename(path)[:-4]
            vals = []
            with open(path) as fh:
                for row in csv.DictReader(fh):
                    if row.get("underlying") == underlying and row.get("underlying_price"):
                        vals.append(float(row["underlying_price"]))
            if vals:
                prices[day] = statistics.median(vals)
        per_venue[v] = prices

    a, b = venues[0], venues[1]
    common = sorted(set(per_venue[a]) & set(per_venue[b]))
    if not common:
        return None
    diffs = [100 * abs(per_venue[a][d] - per_venue[b][d]) / per_venue[a][d] for d in common]
    return {"underlying": underlying, "ตลาดที่เทียบ": [a, b], "จำนวนวันร่วม": len(common),
            "ส่วนต่างกลางเปอร์เซ็นต์": round(statistics.median(diffs), 3),
            "ส่วนต่างมากสุดเปอร์เซ็นต์": round(max(diffs), 3)}


def run_report(data_dir):
    venues = _venues(data_dir)
    report = {"ตลาดที่พบ": venues, "ความครบของวันที่": {}, "ผู้รอดชีวิต": {}, "สภาพคล่องวันล่าสุด": {}}
    latest_by_venue = {}
    for v in venues:
        report["ความครบของวันที่"][v] = date_coverage(data_dir, v)
        report["ผู้รอดชีวิต"][v] = survivorship(data_dir, v)
        days = _days(data_dir, v)
        if days:
            latest_by_venue[v] = days[-1]
            report["สภาพคล่องวันล่าสุด"][v] = liquidity(data_dir, v, days[-1])
    report["ราคาข้ามตลาด"] = cross_venue_price_diff(data_dir, venues) if len(venues) >= 2 else None
    return report


def print_human(report):
    print("=== รายงานสุขภาพข้อมูล ===")
    print("ตลาดที่พบ:", ", ".join(report["ตลาดที่พบ"]) or "(ไม่มี)")
    for v, cov in report["ความครบของวันที่"].items():
        if not cov:
            continue
        status = "ครบ" if cov["จำนวนวันที่ขาดหาย"] == 0 else f"ขาด {cov['จำนวนวันที่ขาดหาย']} วัน: {cov['วันที่ขาดหาย']}"
        print(f"\n[{v}] {cov['วันแรก']} ถึง {cov['วันสุดท้าย']} — "
              f"{cov['จำนวนวันที่มีไฟล์']}/{cov['จำนวนวันที่ควรมี']} วัน ({status})")
        surv = report["ผู้รอดชีวิต"].get(v)
        if surv and surv["สัดส่วนที่รอดเปอร์เซ็นต์"] is not None:
            print(f"  ผู้รอดชีวิต ({surv['underlying']}): {surv['สัดส่วนที่รอดเปอร์เซ็นต์']}% "
                  f"({surv['อยู่ครบทั้งสองวัน']}/{surv['จำนวนวันแรก']})")
        liq = report["สภาพคล่องวันล่าสุด"].get(v)
        if liq:
            print(f"  สภาพคล่อง ({liq['วันที่']}): ไม่มีปริมาณซื้อขาย {liq['ไม่มีปริมาณซื้อขาย24ชมเปอร์เซ็นต์']}% · "
                  f"ไม่มีราคาเสนอซื้อ {liq['ไม่มีราคาเสนอซื้อเปอร์เซ็นต์']}% · "
                  f"mark นอกช่วง bid-ask {liq['markอยู่นอกช่วงbidask']} สัญญา")
    if report.get("ราคาข้ามตลาด"):
        cv = report["ราคาข้ามตลาด"]
        print(f"\nราคาข้ามตลาด ({' vs '.join(cv['ตลาดที่เทียบ'])}, {cv['underlying']}): "
              f"ต่างกันกลาง {cv['ส่วนต่างกลางเปอร์เซ็นต์']}% · มากสุด {cv['ส่วนต่างมากสุดเปอร์เซ็นต์']}% "
              f"({cv['จำนวนวันร่วม']} วันที่มีข้อมูลทั้งสองตลาด)")


if __name__ == "__main__":
    _args = sys.argv[1:]
    _custom_dir = "--data-dir" in _args
    if _custom_dir:
        DATA_DIR = _args[_args.index("--data-dir") + 1]
    if not os.path.isdir(DATA_DIR):
        sys.exit(f"ไม่พบโฟลเดอร์ข้อมูล: {DATA_DIR}\n"
                 f"ระบุตำแหน่งด้วย --data-dir <path> หรือตัวแปรแวดล้อม NQ_DATA_DIR")
    rep = run_report(DATA_DIR)
    print_human(rep)
    if not _custom_dir:
        with open(OUT, "w") as fh:
            json.dump({"_อ่านก่อน": "สร้างด้วย tools/data_health.py — ห้ามแก้ด้วยมือ", **rep},
                       fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        print("\nเขียน", os.path.relpath(OUT, ROOT))
