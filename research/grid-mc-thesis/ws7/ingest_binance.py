#!/usr/bin/env python3
"""WS7 ingestion gate — Binance Spot BTCUSDT 1m monthly archives (Discovery only).

Pipeline (AIGR Master Handoff §10):
  official monthly ZIP → checksum verification → ZIP/CSV integrity → schema validation
  → timestamp monotonicity → duplicate detection → expected-minute coverage
  → gap manifest → OHLC consistency → canonical Discovery dataset

Hard rules:
  * Months >= SEALED_FROM (2024-01) are refused — never downloaded, read or written.
  * Missing minutes are NEVER forward-filled; they are listed in the gap manifest.
  * Checksum mismatch, conflicting duplicates or invalid OHLC → month FAIL (not written).

Usage:
  # download from data.binance.vision (needs network access to that host)
  python3 ingest_binance.py --start 2018-01 --end 2023-12 --out data/

  # or use archives you downloaded yourself (ZIP + .CHECKSUM side by side)
  python3 ingest_binance.py --start 2018-01 --end 2023-12 --out data/ --source-dir ~/Downloads/btc1m
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

import numpy as np

SYMBOL = "BTCUSDT"
INTERVAL = "1m"
BASE_URL = "https://data.binance.vision/data/spot/monthly/klines"
SEALED_FROM = (2024, 1)
MINUTE_MS = 60_000
N_COLS = 12  # open_time, o, h, l, c, v, close_time, quote_vol, trades, taker_base, taker_quote, ignore


class SealedPeriodError(SystemExit):
    pass


def parse_month(s: str) -> tuple[int, int]:
    y, m = s.split("-")
    return int(y), int(m)


def assert_not_sealed(year: int, month: int) -> None:
    if (year, month) >= SEALED_FROM:
        raise SealedPeriodError(
            f"REFUSED: {year:04d}-{month:02d} is inside the sealed OOS period "
            f"(>= {SEALED_FROM[0]:04d}-{SEALED_FROM[1]:02d}). Open only after the pre-OOS packet is hashed."
        )


def month_range(start: str, end: str):
    y, m = parse_month(start)
    ye, me = parse_month(end)
    while (y, m) <= (ye, me):
        assert_not_sealed(y, m)
        yield y, m
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def month_bounds_ms(y: int, m: int) -> tuple[int, int]:
    start = dt.datetime(y, m, 1, tzinfo=dt.timezone.utc)
    end = dt.datetime(y + (m == 12), 1 if m == 12 else m + 1, 1, tzinfo=dt.timezone.utc)
    return int(start.timestamp() * 1000), int(end.timestamp() * 1000)


def archive_name(y: int, m: int) -> str:
    return f"{SYMBOL}-{INTERVAL}-{y:04d}-{m:02d}.zip"


def archive_url(y: int, m: int) -> str:
    return f"{BASE_URL}/{SYMBOL}/{INTERVAL}/{archive_name(y, m)}"


def fetch(url: str, retries: int = 4) -> bytes:
    delay = 2
    last = None
    for _ in range(retries + 1):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001 — report and retry network errors
            last = e
            import time

            time.sleep(delay)
            delay *= 2
    raise RuntimeError(f"download failed: {url}: {last}")


def get_archive(y: int, m: int, source_dir: Path | None, raw_dir: Path) -> tuple[bytes, str, str]:
    """Return (zip_bytes, published_sha256, source_url_or_path). Keeps a raw copy."""
    name = archive_name(y, m)
    if source_dir is not None:
        zb = (source_dir / name).read_bytes()
        ck = (source_dir / f"{name}.CHECKSUM").read_text()
        src = str(source_dir / name)
    else:
        url = archive_url(y, m)
        zb = fetch(url)
        ck = fetch(url + ".CHECKSUM").decode()
        src = url
    raw_dir.mkdir(parents=True, exist_ok=True)
    (raw_dir / name).write_bytes(zb)
    (raw_dir / f"{name}.CHECKSUM").write_text(ck)
    published = ck.strip().split()[0].lower()
    return zb, published, src


def to_ms(t: np.ndarray) -> np.ndarray:
    # Binance switched spot archives to microseconds from 2025-01; guard anyway.
    return np.where(t > 10**14, t // 1000, t)


def validate_month(y: int, m: int, zb: bytes, published: str) -> tuple[dict, dict | None, list]:
    rec: dict = {"archive_month": f"{y:04d}-{m:02d}", "published_checksum": published}
    calc = hashlib.sha256(zb).hexdigest()
    rec["calculated_checksum"] = calc
    problems: list[str] = []
    fail = False
    gaps: list = []

    if calc != published:
        rec.update(status="FAIL", problems="checksum mismatch")
        return rec, None, gaps

    try:
        zf = zipfile.ZipFile(io.BytesIO(zb))
        bad = zf.testzip()
        if bad is not None:
            raise zipfile.BadZipFile(f"corrupt member {bad}")
        members = [n for n in zf.namelist() if n.endswith(".csv")]
        if len(members) != 1:
            raise zipfile.BadZipFile(f"expected 1 csv, found {members}")
        text = zf.read(members[0]).decode()
    except Exception as e:  # noqa: BLE001
        rec.update(status="FAIL", problems=f"zip/csv integrity: {e}")
        return rec, None, gaps

    rows = list(csv.reader(io.StringIO(text)))
    if rows and not rows[0][0].strip().isdigit():
        rows = rows[1:]  # optional header
    if any(len(r) != N_COLS for r in rows):
        rec.update(status="FAIL", problems="schema: wrong column count")
        return rec, None, gaps
    try:
        arr = np.array([[float(x) for x in r[:6]] + [float(r[6])] for r in rows], dtype=np.float64)
    except ValueError as e:
        rec.update(status="FAIL", problems=f"schema: non-numeric field ({e})")
        return rec, None, gaps

    t = to_ms(arr[:, 0].astype(np.int64))
    tclose = to_ms(arr[:, 6].astype(np.int64))
    o, h, l, c, v = (arr[:, i] for i in range(1, 6))
    lo_ms, hi_ms = month_bounds_ms(y, m)
    rec["row_count"] = int(len(t))

    if np.any((t < lo_ms) | (t >= hi_ms)):
        problems.append("rows outside archive month")
        fail = True
    if np.any(t % MINUTE_MS != 0) or np.any(tclose != t + MINUTE_MS - 1):
        problems.append("timestamp alignment")
        fail = True

    if np.any(np.diff(t) < 0):
        problems.append("non-monotonic timestamps (sorted)")
        order = np.argsort(t, kind="stable")
        t, o, h, l, c, v = (x[order] for x in (t, o, h, l, c, v))

    dup_mask = np.concatenate([[False], np.diff(t) == 0])
    n_dup = int(dup_mask.sum())
    rec["duplicates"] = n_dup
    if n_dup:
        idx = np.where(dup_mask)[0]
        same = all(
            (o[i], h[i], l[i], c[i], v[i]) == (o[i - 1], h[i - 1], l[i - 1], c[i - 1], v[i - 1]) for i in idx
        )
        if not same:
            problems.append("conflicting duplicates")
            fail = True
        else:
            problems.append("identical duplicates dropped")
        keep = ~dup_mask
        t, o, h, l, c, v = (x[keep] for x in (t, o, h, l, c, v))

    bad_ohlc = (l <= 0) | (h < l) | (h < np.maximum(o, c)) | (l > np.minimum(o, c)) | (v < 0)
    rec["ohlc_violations"] = int(bad_ohlc.sum())
    rec["ohlc_status"] = "OK" if not bad_ohlc.any() else "VIOLATION"
    if bad_ohlc.any():
        problems.append("OHLC inconsistency")
        fail = True

    expected = (hi_ms - lo_ms) // MINUTE_MS
    rec["expected_minutes"] = int(expected)
    rec["missing_minutes"] = int(expected - len(t))
    grid = np.concatenate([[lo_ms - MINUTE_MS], t, [hi_ms]])
    step = np.diff(grid)
    for i in np.where(step > MINUTE_MS)[0]:
        g0 = int(grid[i] + MINUTE_MS)
        g1 = int(grid[i + 1] - MINUTE_MS)
        gaps.append((rec["archive_month"], iso(g0), iso(g1), (g1 - g0) // MINUTE_MS + 1))
    rec["gap_count"] = len(gaps)
    rec["first_timestamp"] = iso(int(t[0])) if len(t) else ""
    rec["last_timestamp"] = iso(int(t[-1])) if len(t) else ""
    rec["schema_status"] = "OK"

    if fail:
        rec["status"] = "FAIL"
    elif rec["missing_minutes"] or n_dup or problems:
        rec["status"] = "CONDITIONAL"
    else:
        rec["status"] = "PASS"
    rec["problems"] = "; ".join(problems)
    data = None if fail else {"open_time_ms": t, "open": o, "high": h, "low": l, "close": c, "volume": v}
    return rec, data, gaps


def iso(ms: int) -> str:
    return dt.datetime.fromtimestamp(ms / 1000, tz=dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--start", default="2018-01")
    ap.add_argument("--end", default="2023-12")
    ap.add_argument("--out", type=Path, default=Path("data"))
    ap.add_argument("--source-dir", type=Path, default=None, help="use pre-downloaded ZIP + .CHECKSUM files")
    args = ap.parse_args(argv)

    months = list(month_range(args.start, args.end))  # raises before any I/O if sealed
    out = args.out
    canon = out / "canonical"
    canon.mkdir(parents=True, exist_ok=True)
    manifest, gaps_all = [], []
    acquired = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for y, m in months:
        name = archive_name(y, m)
        try:
            zb, published, src = get_archive(y, m, args.source_dir, out / "raw")
        except Exception as e:  # noqa: BLE001
            manifest.append({"filename": name, "archive_month": f"{y:04d}-{m:02d}", "status": "FAIL",
                             "problems": f"acquisition: {e}", "acquisition_date": acquired})
            print(f"{name}: FAIL acquisition ({e})", file=sys.stderr)
            continue
        rec, data, gaps = validate_month(y, m, zb, published)
        rec.update(filename=name, source=src, acquisition_date=acquired)
        manifest.append(rec)
        gaps_all.extend(gaps)
        if data is not None:
            np.savez_compressed(canon / f"{SYMBOL}-{INTERVAL}-{y:04d}-{m:02d}.npz", **data)
        print(f"{name}: {rec['status']} rows={rec.get('row_count')} missing={rec.get('missing_minutes')} "
              f"{rec.get('problems', '')}")

    fields = ["filename", "source", "archive_month", "published_checksum", "calculated_checksum",
              "acquisition_date", "row_count", "expected_minutes", "missing_minutes", "gap_count", "duplicates",
              "first_timestamp", "last_timestamp", "schema_status", "ohlc_status", "ohlc_violations", "status",
              "problems"]
    with open(out / "provenance_manifest.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(manifest)
    with open(out / "gap_manifest.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["archive_month", "gap_start_utc", "gap_end_utc", "missing_minutes"])
        w.writerows(gaps_all)

    counts = {s: sum(r.get("status") == s for r in manifest) for s in ("PASS", "CONDITIONAL", "FAIL")}
    summary = {"symbol": SYMBOL, "interval": INTERVAL, "start": args.start, "end": args.end,
               "months": len(months), **counts,
               "missing_minutes_total": int(sum(r.get("missing_minutes", 0) or 0 for r in manifest)),
               "sealed_from": f"{SEALED_FROM[0]:04d}-{SEALED_FROM[1]:02d}"}
    (out / "ingest_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    return 0 if counts["FAIL"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
