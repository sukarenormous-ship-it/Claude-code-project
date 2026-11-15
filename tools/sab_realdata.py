#!/usr/bin/env python3
"""สร้าง docs/sab-data/btc-eth-daily.csv จากไฟล์ดิบใน docs/sab-data/raw/ (ภาคผนวก K · ข้อมูลจริง 📡)

ไฟล์ดิบเป็นคำตอบของ API สาธารณะ เก็บไว้ไม่แก้แม้แต่ไบต์เดียว · docs/sab-data/raw/manifest.json บอกว่าแต่ละไฟล์ดึงจาก URL ไหน
เมื่อไร (UTC) และ sha256 ของไฟล์ (กันการแก้ด้วยมือ)

ขั้นตอนทำความสะอาด (ทุกขั้นเขียนไว้ในหัว CSV ให้ผู้อ่านตรวจได้):
  1. อ่านแท่งรายวันของ Binance spot (BTCUSDT · ETHUSDT) — หนึ่งแท่งคือหนึ่งวัน UTC 00:00:00 ถึง 23:59:59.999
  2. ตัดแท่งที่เวลาปิด (close time) อยู่หลังเวลาดึงข้อมูล = แท่งที่ยังไม่ปิด ราคา "ปิด" ของมันยังเปลี่ยนได้
  3. ตรวจวันซ้ำและวันหาย (เวลาเปิดของแท่งติดกันต้องห่าง 86,400,000 มิลลิวินาทีพอดี) · พบ = หยุด ไม่เติมเลขเดา
  4. จับคู่สองเหรียญด้วยวันที่ (ไม่ใช่ลำดับแถว) แล้วเก็บเฉพาะช่วง START..END
  5. ตรวจข้ามแหล่ง: ราคาปิด Binance (USDT) เทียบ Kraken (USD) วันเดียวกัน → ส่วนต่างเป็น % (มัธยฐาน · มากสุด)
ราคาเก็บเป็นทศนิยมสองตำแหน่งตามขั้นราคาของ exchange (0.01) — ถ้าปัดแล้วไม่เท่าค่าดิบ = หยุด

    python3 tools/sab_realdata.py            # เขียน CSV ใหม่จากไฟล์ดิบ
    python3 tools/sab_realdata.py --check    # ไม่เขียน: ตรวจ sha256 ของไฟล์ดิบ และว่า CSV ที่มีอยู่ตรงกับที่สร้างใหม่ทุกไบต์
    python3 tools/sab_realdata.py --fetch    # (ผู้ดูแลเท่านั้น) ดึงไฟล์ดิบชุดใหม่ + เขียน manifest — ตัวเลขในภาคผนวก K จะเปลี่ยน
"""

import datetime as dt
import hashlib
import json
import os
import statistics
import sys
import urllib.request
from decimal import Decimal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "docs", "sab-data")
RAW = os.path.join(DATA, "raw")
CSV = os.path.join(DATA, "btc-eth-daily.csv")
MANIFEST = os.path.join(RAW, "manifest.json")

START, END = "2025-01-01", "2026-11-14"          # ช่วงของภาคผนวก K (ตรึงก่อนดึงข้อมูล)
START_MS = 1735689600000                         # 2025-01-01 00:00 UTC
DAY_MS = 86_400_000
SOURCES = {
    "A": ("BTC", "binance-BTCUSDT-1d.json",
          f"https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1d&startTime={START_MS}&limit=1000"),
    "B": ("ETH", "binance-ETHUSDT-1d.json",
          f"https://data-api.binance.vision/api/v3/klines?symbol=ETHUSDT&interval=1d&startTime={START_MS}&limit=1000"),
}
CROSS = {
    "A": ("kraken-XBTUSD-1440.json", "XXBTZUSD", "https://api.kraken.com/0/public/OHLC?pair=XBTUSD&interval=1440"),
    "B": ("kraken-ETHUSD-1440.json", "XETHZUSD", "https://api.kraken.com/0/public/OHLC?pair=ETHUSD&interval=1440"),
}


def utc(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc)


def day(ms):
    return utc(ms).strftime("%Y-%m-%d")


def sha256(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def price(s):
    d = Decimal(s)
    p = d.quantize(Decimal("0.01"))
    if p != d:
        raise SystemExit(f"ราคา {s} มีทศนิยมเกินขั้นราคา 0.01 — ไม่ปัดเงียบ ๆ")
    return p


def load_manifest():
    with open(MANIFEST, encoding="utf-8") as fh:
        return json.load(fh)


def binance(name, fetched_ms):
    """คืน ({วันที่: ราคาปิด}, จำนวนแถวดิบ, [แท่งที่ตัดเพราะยังไม่ปิด])"""
    with open(os.path.join(RAW, name), encoding="utf-8") as fh:
        rows = json.load(fh)
    opens = [r[0] for r in rows]
    if len(set(opens)) != len(opens):
        raise SystemExit(f"{name}: มีวันซ้ำ")
    gaps = [(day(a), day(b)) for a, b in zip(opens, opens[1:]) if b - a != DAY_MS]
    if gaps:
        raise SystemExit(f"{name}: วันหาย {gaps} — ไม่เติมเลขเดา")
    closes, dropped = {}, []
    for r in rows:
        if r[6] > fetched_ms:                     # close time หลังเวลาดึง = แท่งยังไม่ปิด
            dropped.append((day(r[0]), utc(r[6]).strftime("%Y-%m-%dT%H:%M:%SZ"), str(price(r[4]))))
            continue
        closes[day(r[0])] = price(r[4])
    return closes, len(rows), dropped


def kraken(name, key):
    with open(os.path.join(RAW, name), encoding="utf-8") as fh:
        js = json.load(fh)
    if js.get("error"):
        raise SystemExit(f"{name}: {js['error']}")
    return {day(r[0] * 1000): Decimal(r[4]) for r in js["result"][key]}


def build():
    man = load_manifest()
    fetched = {k: v["fetched_utc"] for k, v in man["files"].items()}
    for name, info in man["files"].items():
        got = sha256(os.path.join(RAW, name))
        if got != info["sha256"]:
            raise SystemExit(f"{name}: sha256 ไม่ตรง manifest — ไฟล์ดิบถูกแก้")
    series, meta = {}, {}
    for leg, (sym, name, url) in SOURCES.items():
        if man["files"][name]["url"] != url:
            raise SystemExit(f"{name}: URL ใน manifest ไม่ตรงกับที่สคริปต์คาด")
        f_ms = int(dt.datetime.strptime(fetched[name], "%Y-%m-%dT%H:%M:%SZ")
                   .replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
        closes, n_raw, dropped = binance(name, f_ms)
        series[leg] = closes
        meta[leg] = (sym, url, fetched[name], n_raw, dropped)
    days = sorted(d for d in set(series["A"]) & set(series["B"]) if START <= d <= END)
    only = sorted((set(series["A"]) ^ set(series["B"])) & {d for d in set(series["A"]) | set(series["B"]) if START <= d <= END})
    if only:
        raise SystemExit(f"วันที่มีเหรียญเดียว {only}")
    want = (dt.date.fromisoformat(END) - dt.date.fromisoformat(START)).days + 1
    if len(days) != want:
        raise SystemExit(f"ได้ {len(days)} วัน แต่ช่วง {START}..{END} มี {want} วัน")
    cross = {}
    for leg, (name, key, url) in CROSS.items():
        k = kraken(name, key)
        diffs = [abs(series[leg][d] - k[d]) / k[d] * 100 for d in days if d in k]
        cross[leg] = (len(diffs), statistics.median(diffs), max(diffs),
                      max((d for d in days if d in k), key=lambda d: abs(series[leg][d] - k[d]) / k[d]))
    lines = [
        "# sab-data · ภาคผนวก K · ข้อมูลจริง 📡 ราคาปิดรายวันของ BTC และ ETH (หน่วย USDT) จาก Binance spot",
        "# สร้างโดย tools/sab_realdata.py จากไฟล์ดิบใน docs/sab-data/raw/ — ห้ามแก้ด้วยมือ (รัน --check เพื่อตรวจ)",
        "# วัน: หนึ่งแถว = หนึ่งวันตามเวลา UTC (00:00:00 ถึง 23:59:59.999) · ราคาปิด = ราคาซื้อขายสุดท้ายของวันนั้น",
    ]
    for leg in "AB":
        sym, url, f_utc, n_raw, dropped = meta[leg]
        lines.append(f"# source_{leg}: {sym} {url}")
        lines.append(f"# fetched_{leg}_utc: {f_utc}")
        lines.append(f"# raw_rows_{leg}: {n_raw}")
        for d, ct, c in dropped:
            lines.append(f"# dropped_{leg}: {d} close_time {ct} หลังเวลาดึง = แท่งยังไม่ปิด (ราคาตอนดึง {c})")
    lines.append("# check_gaps: 0 · check_duplicates: 0 (เวลาเปิดแท่งติดกันห่าง 86400000 ms ทุกคู่)")
    lines.append(f"# range: {START} .. {END} · rows: {len(days)}")
    for leg in "AB":
        n, med, mx, dmx = cross[leg]
        name, key, url = CROSS[leg]
        lines.append(f"# check_kraken_{leg}: {url} · {n} วัน · ส่วนต่างราคาปิด มัธยฐาน {med:.4f}% · มากสุด {mx:.4f}% ({dmx})")
    lines.append("date_utc,btc_close,eth_close")
    lines += [f"{d},{series['A'][d]},{series['B'][d]}" for d in days]
    return "\n".join(lines) + "\n"


def fetch():
    """ดึงไฟล์ดิบชุดใหม่ (ผู้ดูแล) — ไม่ส่งข้อมูลระบุตัวตนใด ๆ"""
    os.makedirs(RAW, exist_ok=True)
    files = {}
    jobs = [(name, url) for _, name, url in SOURCES.values()] + [(name, url) for name, _, url in CROSS.values()]
    for name, url in jobs:
        req = urllib.request.Request(url, headers={"User-Agent": "sab-realdata/1.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            body = r.read()
        when = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with open(os.path.join(RAW, name), "wb") as fh:
            fh.write(body)
        files[name] = {"url": url, "fetched_utc": when, "sha256": hashlib.sha256(body).hexdigest()}
    with open(MANIFEST, "w", encoding="utf-8") as fh:
        json.dump({"_อ่านก่อน": "ไฟล์ดิบเก็บตามที่ API ตอบ ไม่แก้ · sha256 ใช้ตรวจใน tools/sab_realdata.py --check",
                   "files": files}, fh, ensure_ascii=False, indent=1)
        fh.write("\n")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--fetch"]:
        fetch()
        a = []
    text = build()
    if a == ["--check"]:
        cur = open(CSV, encoding="utf-8").read() if os.path.exists(CSV) else None
        if cur != text:
            print("CSV ไม่ตรงกับที่สร้างจากไฟล์ดิบ — รัน python3 tools/sab_realdata.py")
            sys.exit(1)
        print(f"ไฟล์ดิบ sha256 ตรง manifest · {os.path.relpath(CSV, ROOT)} ตรงกับที่สร้างใหม่ทุกไบต์ ✓")
        sys.exit(0)
    with open(CSV, "w", encoding="utf-8") as fh:
        fh.write(text)
    rows = [ln for ln in text.splitlines() if ln and not ln.startswith("#")][1:]
    print(f"เขียน {os.path.relpath(CSV, ROOT)} · {len(rows)} แถวข้อมูล")
