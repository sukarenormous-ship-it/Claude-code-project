#!/usr/bin/env python3
"""ชุดข้อมูลกลางของ Stat Arb เล่ม 2 (docs/sab2-data/) — สร้างซ้ำ ตรวจ และโหลดตามช่วงแบ่ง (stdlib เท่านั้น)

ไฟล์ดิบใน docs/sab2-data/raw/ คือคำตอบของ API สาธารณะ เก็บตามที่ได้ ไม่แก้แม้แต่ไบต์เดียว
docs/sab2-data/manifest.json บอก URL · เวลาดึง (UTC) · ขนาด (ไบต์) · sha256 ของทุกไฟล์ดิบ

ผลลัพธ์ที่สร้างจากไฟล์ดิบ (ห้ามแก้ด้วยมือ):
  closes-daily.csv   ราคาปิดรายวัน UTC จาก Binance spot (คู่ USDT) หนึ่งคอลัมน์ต่อเหรียญ
  funding-8h.csv     Funding Rate รายรอบของ perp บน OKX (แบบยาว: เวลา · สัญญา · อัตรา)
ช่วงแบ่งตายตัวทั้งเล่มอยู่ใน splits.json (เขียนด้วยมือครั้งเดียว · สคริปต์ตรวจว่าต่อกันพอดีและครอบคลุมข้อมูล)

ขั้นตอนทำความสะอาด:
  1. แท่งรายวันของ Binance: ตัดแท่งที่ close time อยู่หลังเวลาดึง (ยังไม่ปิด) · ตรวจวันซ้ำ วันหาย
     (เวลาเปิดติดกันต้องห่าง 86,400,000 ms) · เวลาเปิดต้องเป็น 00:00 UTC · ราคาปิดต้อง > 0
     เหรียญที่ไม่ผ่านถูกตัดทั้งเหรียญ (ไม่เติมเลขเดา) และบันทึกเหตุผลในหัว CSV
  2. เก็บเฉพาะวัน START..END ที่ทุกเหรียญมีครบ
  3. ตรวจข้ามแหล่ง BTC และ ETH เทียบ Kraken (USD) วันเดียวกัน → ส่วนต่าง % (มัธยฐาน · มากสุด)
  4. Funding: ตรวจรอบซ้ำ · รอบที่ไม่ห่าง 8 ชม. · เวลาที่ไม่ใช่ 00/08/16 UTC · fundingRate ≠ realizedRate
     · รอบที่ยังไม่ถึงเวลาตอนดึง — รายงานในหัว CSV (เก็บทุกรอบที่ชำระแล้ว ไม่เติมรอบที่หาย)

    python3 tools/sab2_realdata.py            # เขียน CSV ใหม่จากไฟล์ดิบ
    python3 tools/sab2_realdata.py --check    # ไม่เขียน: ตรวจ sha256/ขนาดไฟล์ดิบ, splits, และว่า CSV ตรงกับที่สร้างใหม่ทุกไบต์
    python3 tools/sab2_realdata.py --fetch    # (ผู้ดูแลเท่านั้น) ดึงไฟล์ดิบชุดใหม่ + manifest — ตัวเลขทั้งเล่มจะเปลี่ยน

ใช้ในโค้ดของบท:
    from sab2_realdata import load_closes, load_funding
    dates, px = load_closes("formation")          # px["BTC"] = [ราคาปิด float ...] เรียงตาม dates
    rows = load_funding("formation", instrument="BTC-USDT-SWAP")
    load_closes("final_test")                     # ValueError — ช่วงทดสอบสุดท้ายล็อกไว้จนถึงบท 17
    load_closes("final_test", unlock_final=True)  # บท 17 เท่านั้น
"""

import datetime as dt
import hashlib
import json
import os
import statistics
import sys
import time
import urllib.request
from decimal import Decimal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "docs", "sab2-data")
RAW = os.path.join(DATA, "raw")
MANIFEST = os.path.join(DATA, "manifest.json")
CLOSES_CSV = os.path.join(DATA, "closes-daily.csv")
FUNDING_CSV = os.path.join(DATA, "funding-8h.csv")
SPLITS = os.path.join(DATA, "splits.json")

START, END = "2022-11-15", "2026-11-14"           # สี่ปีเต็ม ตรึงก่อนดึงข้อมูล
START_MS = 1668470400000                          # 2022-11-15 00:00 UTC
DAY_MS = 86_400_000
H8_MS = 8 * 3_600_000
COINS = ["BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "LTC", "LINK", "DOT"]
PERPS = ["BTC-USDT-SWAP", "ETH-USDT-SWAP", "SOL-USDT-SWAP"]
KRAKEN = {"BTC": ("XBTUSD", "XXBTZUSD"), "ETH": ("ETHUSD", "XETHZUSD")}
SPLIT_NAMES = ["formation", "validation", "final_test"]
UA = "sab2-realdata/1.0"                          # ไม่ส่งข้อมูลระบุตัวตนใด ๆ

BINANCE_URL = "https://data-api.binance.vision/api/v3/klines?symbol={sym}USDT&interval=1d&startTime={start}&limit=1000"
OKX_URL = "https://www.okx.com/api/v5/public/funding-rate-history?instId={inst}&limit=100"
KRAKEN_URL = "https://api.kraken.com/0/public/OHLC?pair={pair}&interval=1440"


# ---------- เครื่องมือเล็ก ----------

def utc(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc)


def day(ms):
    return utc(ms).strftime("%Y-%m-%d")


def stamp(ms):
    return utc(ms).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_stamp(s):
    return int(dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


def num(s):
    """สตริงทศนิยมจาก API → สตริงที่ตัดศูนย์ท้าย (ค่าเท่าเดิมทุกหลัก ไม่ปัด)"""
    d = Decimal(s)
    t = format(d, "f")
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    if Decimal(t) != d:
        raise SystemExit(f"แปลง {s} แล้วค่าเปลี่ยน")
    return t


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def raw_json(name):
    with open(os.path.join(RAW, name), encoding="utf-8") as fh:
        return json.load(fh)


def pages(man, prefix):
    """ไฟล์ดิบของชุดหนึ่ง เรียงตามเลขหน้า p1, p2, ..."""
    names = [n for n in man["files"] if n.startswith(prefix + "-p")]
    return sorted(names, key=lambda n: int(n[len(prefix) + 2:].split(".")[0]))


# ---------- ตรวจไฟล์ดิบ ----------

def load_manifest():
    with open(MANIFEST, encoding="utf-8") as fh:
        man = json.load(fh)
    for name, info in man["files"].items():
        path = os.path.join(RAW, name)
        if not os.path.exists(path):
            raise SystemExit(f"{name}: ไม่มีไฟล์ดิบ")
        with open(path, "rb") as fh:
            b = fh.read()
        if len(b) != info["bytes"]:
            raise SystemExit(f"{name}: ขนาด {len(b)} ไบต์ ไม่ตรง manifest {info['bytes']}")
        if sha256_bytes(b) != info["sha256"]:
            raise SystemExit(f"{name}: sha256 ไม่ตรง manifest — ไฟล์ดิบถูกแก้")
    extra = set(os.listdir(RAW)) - set(man["files"])
    if extra:
        raise SystemExit(f"ไฟล์ใน raw/ ที่ไม่อยู่ใน manifest: {sorted(extra)}")
    return man


# ---------- ราคาปิดรายวัน ----------

def binance_series(man, sym):
    names = pages(man, f"binance-{sym}USDT-1d")
    if not names:
        return None, {"reason": "ไม่มีไฟล์ดิบ"}
    rows, info = [], {"files": names, "urls": [man["files"][n]["url"] for n in names],
                      "fetched": man["files"][names[0]]["fetched_utc"]}
    expect_start = START_MS
    for n in names:
        url = man["files"][n]["url"]
        if url != BINANCE_URL.format(sym=sym, start=expect_start):
            raise SystemExit(f"{n}: URL ใน manifest ไม่ตรงกับลำดับหน้าที่คาด")
        part = raw_json(n)
        f_ms = parse_stamp(man["files"][n]["fetched_utc"])
        for r in part:
            rows.append((r, f_ms))
        if part:
            expect_start = part[-1][0] + DAY_MS
    opens = [r[0] for r, _ in rows]
    info["raw_rows"] = len(rows)
    info["duplicates"] = len(opens) - len(set(opens))
    info["gaps"] = [(day(a), day(b)) for a, b in zip(opens, opens[1:]) if b - a != DAY_MS]
    info["not_midnight"] = [stamp(o) for o in opens if o % DAY_MS]
    info["dropped_open"], info["nonpositive"] = [], []
    closes = {}
    for r, f_ms in rows:
        if r[6] > f_ms:
            info["dropped_open"].append((day(r[0]), stamp(r[6]), num(r[4])))
            continue
        c = num(r[4])
        if Decimal(c) <= 0:
            info["nonpositive"].append((day(r[0]), c))
        closes[day(r[0])] = c
    want = [day(START_MS + i * DAY_MS) for i in range(n_days())]
    info["missing_in_range"] = [d for d in want if d not in closes]
    problems = []
    if info["duplicates"]:
        problems.append(f"วันซ้ำ {info['duplicates']}")
    if info["gaps"]:
        problems.append(f"วันหาย {info['gaps'][:3]}")
    if info["not_midnight"]:
        problems.append(f"เวลาเปิดไม่ใช่ 00:00 UTC {info['not_midnight'][:3]}")
    if info["nonpositive"]:
        problems.append(f"ราคาปิด ≤ 0 {info['nonpositive'][:3]}")
    if info["missing_in_range"]:
        problems.append(f"ไม่มีข้อมูล {len(info['missing_in_range'])} วันในช่วง (แรกสุด {info['missing_in_range'][0]})")
    if problems:
        info["reason"] = " · ".join(problems)
        return None, info
    return closes, info


def n_days():
    return (dt.date.fromisoformat(END) - dt.date.fromisoformat(START)).days + 1


def kraken_closes(man, coin):
    pair, key = KRAKEN[coin]
    name = f"kraken-{pair}-1440.json"
    js = raw_json(name)
    if js.get("error"):
        raise SystemExit(f"{name}: {js['error']}")
    return name, man["files"][name], {day(r[0] * 1000): Decimal(r[4]) for r in js["result"][key]}


def build_closes(man):
    series, infos, dropped_coins = {}, {}, []
    for c in COINS:
        s, info = binance_series(man, c)
        infos[c] = info
        if s is None:
            dropped_coins.append((c, info["reason"]))
        else:
            series[c] = s
    kept = [c for c in COINS if c in series]
    days = [day(START_MS + i * DAY_MS) for i in range(n_days())]
    cross = {}
    for coin in KRAKEN:
        if coin not in series:
            continue
        name, finfo, k = kraken_closes(man, coin)
        both = [d for d in days if d in k]
        diffs = {d: abs(Decimal(series[coin][d]) - k[d]) / k[d] * 100 for d in both}
        worst = max(both, key=lambda d: diffs[d])
        cross[coin] = (finfo["url"], len(both), both[0], both[-1],
                       statistics.median(diffs.values()), diffs[worst], worst)
    L = [
        "# sab2-data · ชุดข้อมูลกลาง เล่ม 2 · ราคาปิดรายวัน (หน่วย USDT) จาก Binance spot",
        "# สร้างโดย tools/sab2_realdata.py จากไฟล์ดิบใน docs/sab2-data/raw/ — ห้ามแก้ด้วยมือ (รัน --check เพื่อตรวจ)",
        "# วัน: หนึ่งแถว = หนึ่งวันตามเวลา UTC (00:00:00 ถึง 23:59:59.999) · ราคาปิด = ราคาซื้อขายสุดท้ายของวันนั้น",
        "# ราคาเก็บตามสตริงของ API ตัดเฉพาะศูนย์ท้าย (ไม่ปัด) · ช่วงแบ่งของเล่มอยู่ใน splits.json",
        "# source: https://data-api.binance.vision/api/v3/klines?symbol=<COIN>USDT&interval=1d&startTime=<ms>&limit=1000 (แบ่งหน้า · URL ทุกหน้าอยู่ใน manifest.json)",
    ]
    for c in COINS:
        i = infos[c]
        if c not in series:
            L.append(f"# coin_{c}: ตัดออก — {i['reason']}")
            continue
        L.append(f"# coin_{c}: {c}USDT · ไฟล์ดิบ {len(i['files'])} หน้า · fetched_utc {i['fetched']} · raw_rows {i['raw_rows']}"
                 f" · ซ้ำ 0 · หาย 0 · เวลาเปิดไม่ใช่ 00:00 UTC 0 · ราคา ≤ 0 0")
        for d, ct, px in i["dropped_open"]:
            L.append(f"# dropped_{c}: {d} close_time {ct} หลังเวลาดึง = แท่งยังไม่ปิด (ราคาตอนดึง {px})")
    for coin, (url, n, a, b, med, mx, worst) in cross.items():
        L.append(f"# check_kraken_{coin}: {url} · {n} วัน ({a} .. {b}) · ส่วนต่างราคาปิด Binance(USDT) กับ Kraken(USD)"
                 f" มัธยฐาน {med:.4f}% · มากสุด {mx:.4f}% ({worst})")
    L.append(f"# range: {START} .. {END} · rows: {len(days)} · coins: {len(kept)}")
    L.append("date_utc," + ",".join(c.lower() for c in kept))
    for d in days:
        L.append(d + "," + ",".join(series[c][d] for c in kept))
    summary = {"coins": kept, "dropped": dropped_coins, "cross": cross, "rows": len(days),
               "unclosed": sum(len(infos[c]["dropped_open"]) for c in kept)}
    return "\n".join(L) + "\n", summary


# ---------- Funding ----------

def build_funding(man):
    L = [
        "# sab2-data · ชุดข้อมูลกลาง เล่ม 2 · Funding Rate รายรอบของสัญญา perpetual (USDT-margined) บน OKX",
        "# สร้างโดย tools/sab2_realdata.py จากไฟล์ดิบใน docs/sab2-data/raw/ — ห้ามแก้ด้วยมือ (รัน --check เพื่อตรวจ)",
        "# rate = fundingRate ของรอบนั้น เป็นสัดส่วน (0.0001 = 0.01% ต่อรอบ) · บวก = ฝั่ง long จ่ายฝั่ง short",
        "# timestamp_utc = เวลาชำระของรอบ · OKX เก็บประวัติย้อนหลังได้จำกัด: ข้อมูลเริ่มที่รอบแรกที่ API ยังตอบ",
        "# source: https://www.okx.com/api/v5/public/funding-rate-history?instId=<INST>&limit=100 (แบ่งหน้าด้วย after=<fundingTime เก่าสุด> · URL ทุกหน้าอยู่ใน manifest.json)",
    ]
    out, summary = [], {}
    for inst in PERPS:
        names = pages(man, f"okx-{inst}-funding")
        recs = []
        after = None
        for n in names:
            url = man["files"][n]["url"]
            want = OKX_URL.format(inst=inst) + (f"&after={after}" if after else "")
            if url != want:
                raise SystemExit(f"{n}: URL ใน manifest ไม่ตรงกับลำดับหน้าที่คาด")
            js = raw_json(n)
            if js.get("code") != "0":
                raise SystemExit(f"{n}: OKX ตอบ code {js.get('code')} {js.get('msg')}")
            f_ms = parse_stamp(man["files"][n]["fetched_utc"])
            for r in js["data"]:
                if r["instId"] != inst:
                    raise SystemExit(f"{n}: instId {r['instId']} ไม่ใช่ {inst}")
                recs.append((int(r["fundingTime"]), r["fundingRate"], r.get("realizedRate"), f_ms))
            if js["data"]:
                after = js["data"][-1]["fundingTime"]
        if not recs:
            raise SystemExit(f"{inst}: ไม่มีข้อมูล funding")
        fetched = man["files"][names[0]]["fetched_utc"]
        times = [t for t, *_ in recs]
        dup = len(times) - len(set(times))
        future = [stamp(t) for t, _, _, f in recs if t > f]
        uniq, after_end = {}, 0
        for t, rate, real, f in recs:
            if t <= f and day(t) > END:
                after_end += 1
            elif t <= f:
                uniq.setdefault(t, (rate, real))
        ts = sorted(uniq)
        steps = [(stamp(a), (b - a) / 3_600_000) for a, b in zip(ts, ts[1:]) if b - a != H8_MS]
        offgrid = [stamp(t) for t in ts if t % H8_MS]
        mismatch = [stamp(t) for t in ts if uniq[t][1] is not None and Decimal(uniq[t][0]) != Decimal(uniq[t][1])]
        rates = [Decimal(uniq[t][0]) for t in ts]
        s = {"rows": len(ts), "first": stamp(ts[0]), "last": stamp(ts[-1]), "duplicates": dup,
             "future": future, "steps": steps, "offgrid": offgrid, "mismatch": mismatch,
             "pages": len(names), "fetched": fetched, "after_end": after_end,
             "mean": sum(rates) / len(rates), "neg": sum(1 for r in rates if r < 0)}
        summary[inst] = s
        L.append(f"# inst_{inst}: ไฟล์ดิบ {len(names)} หน้า · fetched_utc {fetched} · {len(ts)} รอบ · {s['first']} .. {s['last']}"
                 f" · ซ้ำ {dup} · ห่างไม่เท่า 8 ชม. {len(steps)} · เวลาไม่ใช่ 00/08/16 UTC {len(offgrid)}"
                 f" · fundingRate≠realizedRate {len(mismatch)} · รอบที่ยังไม่ชำระตอนดึง (ตัด) {len(future)}"
                 f" · รอบหลัง {END} (ตัด ให้ตรงช่วงราคา) {after_end}")
        for a, h in steps:
            L.append(f"# gap_{inst}: หลัง {a} รอบถัดไปห่าง {h:g} ชม.")
        for t in ts:
            out.append((t, inst, num(uniq[t][0])))
    out.sort(key=lambda r: (r[0], PERPS.index(r[1])))
    L.append("timestamp_utc,instrument,rate")
    L += [f"{stamp(t)},{inst},{rate}" for t, inst, rate in out]
    return "\n".join(L) + "\n", summary


# ---------- ช่วงแบ่ง ----------

def read_splits():
    with open(SPLITS, encoding="utf-8") as fh:
        sp = json.load(fh)
    return sp


def check_splits():
    sp = read_splits()
    ranges = [sp["splits"][k] for k in SPLIT_NAMES]
    if ranges[0]["start"] != START or ranges[-1]["end"] != END:
        raise SystemExit("splits.json ไม่ครอบคลุม START..END พอดี")
    for a, b in zip(ranges, ranges[1:]):
        if (dt.date.fromisoformat(b["start"]) - dt.date.fromisoformat(a["end"])).days != 1:
            raise SystemExit("splits.json: ช่วงไม่ต่อกันพอดี (มีวันซ้อนหรือวันหาย)")
    out = []
    for k in SPLIT_NAMES:
        r = sp["splits"][k]
        n = (dt.date.fromisoformat(r["end"]) - dt.date.fromisoformat(r["start"])).days + 1
        if n != r["days"]:
            raise SystemExit(f"splits.json: {k} เขียน days {r['days']} แต่นับได้ {n}")
        out.append((k, r["start"], r["end"], n))
    return out


def _split_range(split, unlock_final):
    if split is not None and split not in SPLIT_NAMES:
        raise ValueError(f"split ต้องเป็นหนึ่งใน {SPLIT_NAMES} หรือ None (ทั้งหมด)")
    if split in (None, "final_test") and not unlock_final:
        raise ValueError("ช่วงทดสอบสุดท้าย (final_test) ล็อกไว้จนถึงบท 17 — "
                         "ใช้ 'formation' หรือ 'validation' หรือเรียกด้วย unlock_final=True ในบท 17 เท่านั้น")
    sp = read_splits()["splits"]
    if split is None:
        return sp["formation"]["start"], sp["final_test"]["end"]
    return sp[split]["start"], sp[split]["end"]


def _csv_rows(path):
    with open(path, encoding="utf-8") as fh:
        lines = [ln.rstrip("\n") for ln in fh if not ln.startswith("#")]
    return lines[0].split(","), [ln.split(",") for ln in lines[1:] if ln]


def load_closes(split, unlock_final=False, coins=None):
    """คืน (dates, {COIN: [ราคาปิด float ...]}) ของช่วงที่ขอ · split: 'formation' | 'validation' | 'final_test' | None
    'final_test' และ None (ทั้งหมด) ต้องส่ง unlock_final=True (บท 17)"""
    a, b = _split_range(split, unlock_final)
    head, rows = _csv_rows(CLOSES_CSV)
    names = [h.upper() for h in head[1:]]
    want = [c.upper() for c in coins] if coins else names
    bad = [c for c in want if c not in names]
    if bad:
        raise ValueError(f"ไม่มีเหรียญ {bad} ในชุดข้อมูล (มี {names})")
    idx = {c: names.index(c) + 1 for c in want}
    sel = [r for r in rows if a <= r[0] <= b]
    return [r[0] for r in sel], {c: [float(r[i]) for r in sel] for c, i in idx.items()}


def load_funding(split, unlock_final=False, instrument=None):
    """คืน [(timestamp_utc, instrument, rate float), ...] ของรอบที่ชำระในช่วงวันที่ขอ (ตามวัน UTC ของ timestamp)
    หมายเหตุ: OKX เก็บประวัติย้อนหลังได้จำกัด ช่วงที่ไม่มีข้อมูลจะได้รายการว่าง"""
    a, b = _split_range(split, unlock_final)
    _, rows = _csv_rows(FUNDING_CSV)
    if instrument is not None and instrument not in PERPS:
        raise ValueError(f"ไม่มีสัญญา {instrument} (มี {PERPS})")
    return [(t, i, float(r)) for t, i, r in rows
            if a <= t[:10] <= b and (instrument is None or i == instrument)]


# ---------- ดึงไฟล์ดิบ (ผู้ดูแล) ----------

def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        body = r.read()
    return body, dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch():
    """ดึงไฟล์ดิบชุดใหม่ทั้งหมด — ส่งแค่ URL สาธารณะกับ User-Agent ทั่วไป ไม่ส่งข้อมูลระบุตัวตน"""
    os.makedirs(RAW, exist_ok=True)
    for n in os.listdir(RAW):
        os.remove(os.path.join(RAW, n))
    files = {}

    def save(name, url):
        body, when = _get(url)
        with open(os.path.join(RAW, name), "wb") as fh:
            fh.write(body)
        files[name] = {"url": url, "fetched_utc": when, "bytes": len(body), "sha256": sha256_bytes(body)}
        time.sleep(0.25)
        return json.loads(body)

    for c in COINS:
        start, p = START_MS, 1
        while True:
            part = save(f"binance-{c}USDT-1d-p{p}.json", BINANCE_URL.format(sym=c, start=start))
            if len(part) < 1000:
                break
            start, p = part[-1][0] + DAY_MS, p + 1
    for inst in PERPS:
        after, p = None, 1
        while True:
            url = OKX_URL.format(inst=inst) + (f"&after={after}" if after else "")
            js = save(f"okx-{inst}-funding-p{p}.json", url)
            if not js.get("data"):
                break
            after, p = js["data"][-1]["fundingTime"], p + 1
    for coin, (pair, _) in KRAKEN.items():
        save(f"kraken-{pair}-1440.json", KRAKEN_URL.format(pair=pair))
    with open(MANIFEST, "w", encoding="utf-8") as fh:
        json.dump({"_อ่านก่อน": "ไฟล์ดิบใน raw/ เก็บตามที่ API ตอบ ไม่แก้ · bytes และ sha256 ใช้ตรวจใน tools/sab2_realdata.py --check",
                   "files": files}, fh, ensure_ascii=False, indent=1)
        fh.write("\n")


# ---------- main ----------

def build_all():
    man = load_manifest()
    closes, cs = build_closes(man)
    funding, fs = build_funding(man)
    return man, {CLOSES_CSV: closes, FUNDING_CSV: funding}, cs, fs


def report(man, cs, fs, splits):
    print(f"ไฟล์ดิบ {len(man['files'])} ไฟล์ · ขนาดและ sha256 ตรง manifest")
    print(f"ราคาปิด: {len(cs['coins'])} เหรียญ ({' '.join(cs['coins'])}) · {START} .. {END} · {cs['rows']} วัน"
          f" · ซ้ำ 0 · หาย 0 · ราคา ≤ 0 0 · เวลาไม่ใช่ 00:00 UTC 0 · แท่งยังไม่ปิดที่ตัด {cs['unclosed']}")
    for c, why in cs["dropped"]:
        print(f"  ตัดเหรียญ {c}: {why}")
    for coin, (url, n, a, b, med, mx, worst) in cs["cross"].items():
        print(f"  Kraken {coin}: {n} วัน ({a} .. {b}) · ส่วนต่าง มัธยฐาน {med:.4f}% · มากสุด {mx:.4f}% ({worst})")
    for inst, s in fs.items():
        print(f"funding {inst}: {s['rows']} รอบ · {s['first']} .. {s['last']} · ซ้ำ {s['duplicates']}"
              f" · ห่างไม่เท่า 8 ชม. {len(s['steps'])} · นอกเวลา 00/08/16 {len(s['offgrid'])}"
              f" · rate≠realized {len(s['mismatch'])} · ยังไม่ชำระ(ตัด) {len(s['future'])} · หลัง {END}(ตัด) {s['after_end']}"
              f" · เฉลี่ย {float(s['mean']) * 100:.4f}%/รอบ · ติดลบ {s['neg']} รอบ")
    for k, a, b, n in splits:
        print(f"split {k}: {a} .. {b} ({n} วัน)")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--fetch"]:
        fetch()
        args = []
    if args not in ([], ["--check"]):
        raise SystemExit("ใช้: python3 tools/sab2_realdata.py [--check | --fetch]")
    man, outputs, cs, fs = build_all()
    splits = check_splits()
    if args == ["--check"]:
        report(man, cs, fs, splits)
        bad = []
        for path, text in outputs.items():
            cur = open(path, encoding="utf-8").read() if os.path.exists(path) else None
            if cur != text:
                bad.append(os.path.relpath(path, ROOT))
        if bad:
            print(f"ไม่ตรงกับที่สร้างจากไฟล์ดิบ: {', '.join(bad)} — รัน python3 tools/sab2_realdata.py")
            sys.exit(1)
        print("✓ --check ผ่าน: sha256 ตรง · CSV ทั้งสองไฟล์ตรงกับที่สร้างใหม่ทุกไบต์ · splits ต่อกันพอดี")
        sys.exit(0)
    for path, text in outputs.items():
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"เขียน {os.path.relpath(path, ROOT)}")
    report(man, cs, fs, splits)
