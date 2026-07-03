#!/usr/bin/env python3
"""Fetch historical OHLCV candles from Bybit or Binance public APIs.

No API key and no third-party packages required (standard library only).

Examples:
    # 1-hour candles for BTCUSDT from Binance, last 7 days, print to screen
    python3 fetch_prices.py --exchange binance --symbol BTCUSDT --interval 1h --days 7

    # Daily candles for ETHUSDT from Bybit spot, saved to CSV
    python3 fetch_prices.py --exchange bybit --symbol ETHUSDT --interval 1d \
        --start 2024-01-01 --end 2024-06-30 --output eth_daily.csv

    # Bybit USDT perpetual (futures) instead of spot
    python3 fetch_prices.py --exchange bybit --category linear --symbol BTCUSDT \
        --interval 4h --days 30 --output btc_perp_4h.csv
"""

import argparse
import csv
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

BINANCE_URL = "https://api.binance.com/api/v3/klines"
BYBIT_URL = "https://api.bybit.com/v5/market/kline"

# Intervals accepted on the command line, mapped to each exchange's format.
INTERVALS = {
    "1m":  {"binance": "1m",  "bybit": "1",   "ms": 60_000},
    "3m":  {"binance": "3m",  "bybit": "3",   "ms": 180_000},
    "5m":  {"binance": "5m",  "bybit": "5",   "ms": 300_000},
    "15m": {"binance": "15m", "bybit": "15",  "ms": 900_000},
    "30m": {"binance": "30m", "bybit": "30",  "ms": 1_800_000},
    "1h":  {"binance": "1h",  "bybit": "60",  "ms": 3_600_000},
    "2h":  {"binance": "2h",  "bybit": "120", "ms": 7_200_000},
    "4h":  {"binance": "4h",  "bybit": "240", "ms": 14_400_000},
    "6h":  {"binance": "6h",  "bybit": "360", "ms": 21_600_000},
    "12h": {"binance": "12h", "bybit": "720", "ms": 43_200_000},
    "1d":  {"binance": "1d",  "bybit": "D",   "ms": 86_400_000},
    "1w":  {"binance": "1w",  "bybit": "W",   "ms": 604_800_000},
}

MAX_CANDLES_PER_REQUEST = 1000  # both exchanges allow up to 1000


def http_get_json(url: str, params: dict) -> object:
    """GET a URL with query params and parse the JSON response."""
    full_url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(full_url, headers={"User-Agent": "price-fetcher/1.0"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:  # network hiccup or rate limit: back off and retry
            if attempt == 4:
                raise
            wait = 2 ** attempt
            print(f"  request failed ({exc}), retrying in {wait}s...", file=sys.stderr)
            time.sleep(wait)


def fetch_binance(symbol: str, interval: str, start_ms: int, end_ms: int) -> list:
    """Fetch candles from Binance, paginating forward from start to end."""
    candles = []
    cursor = start_ms
    while cursor < end_ms:
        data = http_get_json(BINANCE_URL, {
            "symbol": symbol,
            "interval": INTERVALS[interval]["binance"],
            "startTime": cursor,
            "endTime": end_ms,
            "limit": MAX_CANDLES_PER_REQUEST,
        })
        if isinstance(data, dict):  # error payload, e.g. {"code":-1121,"msg":"Invalid symbol."}
            raise RuntimeError(f"Binance error: {data}")
        if not data:
            break
        for k in data:
            # kline format: [openTime, open, high, low, close, volume, closeTime, ...]
            candles.append({
                "timestamp": int(k[0]),
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "volume": float(k[5]),
            })
        last_open = int(data[-1][0])
        next_cursor = last_open + INTERVALS[interval]["ms"]
        if next_cursor <= cursor:
            break
        cursor = next_cursor
        print(f"  fetched {len(candles)} candles so far...", file=sys.stderr)
        time.sleep(0.15)  # stay well under rate limits
    return candles


def fetch_bybit(symbol: str, interval: str, start_ms: int, end_ms: int, category: str) -> list:
    """Fetch candles from Bybit v5, paginating forward from start to end."""
    candles = []
    cursor = start_ms
    while cursor < end_ms:
        data = http_get_json(BYBIT_URL, {
            "category": category,
            "symbol": symbol,
            "interval": INTERVALS[interval]["bybit"],
            "start": cursor,
            "end": end_ms,
            "limit": MAX_CANDLES_PER_REQUEST,
        })
        if data.get("retCode") != 0:
            raise RuntimeError(f"Bybit error: {data.get('retMsg')} (retCode={data.get('retCode')})")
        rows = data["result"]["list"]
        if not rows:
            break
        # Bybit returns newest-first: [startTime, open, high, low, close, volume, turnover]
        rows.sort(key=lambda r: int(r[0]))
        for r in rows:
            ts = int(r[0])
            if ts < cursor:  # guard against overlap between pages
                continue
            candles.append({
                "timestamp": ts,
                "open": float(r[1]),
                "high": float(r[2]),
                "low": float(r[3]),
                "close": float(r[4]),
                "volume": float(r[5]),
            })
        last_open = int(rows[-1][0])
        next_cursor = last_open + INTERVALS[interval]["ms"]
        if next_cursor <= cursor:
            break
        cursor = next_cursor
        print(f"  fetched {len(candles)} candles so far...", file=sys.stderr)
        time.sleep(0.15)
    return candles


def parse_date(value: str) -> datetime:
    """Accept YYYY-MM-DD or full ISO timestamps, interpreted as UTC."""
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    raise argparse.ArgumentTypeError(f"unrecognized date: {value!r} (use YYYY-MM-DD)")


def write_csv(candles: list, path: str) -> None:
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "datetime_utc", "open", "high", "low", "close", "volume"])
        for c in candles:
            dt = datetime.fromtimestamp(c["timestamp"] / 1000, tz=timezone.utc)
            writer.writerow([
                c["timestamp"],
                dt.strftime("%Y-%m-%d %H:%M:%S"),
                c["open"], c["high"], c["low"], c["close"], c["volume"],
            ])


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch historical OHLCV candles from Bybit or Binance.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--exchange", choices=["binance", "bybit"], required=True)
    parser.add_argument("--symbol", required=True, help="e.g. BTCUSDT, ETHUSDT")
    parser.add_argument("--interval", choices=sorted(INTERVALS), default="1d")
    parser.add_argument("--start", type=parse_date, help="start date (UTC), e.g. 2024-01-01")
    parser.add_argument("--end", type=parse_date, help="end date (UTC), defaults to now")
    parser.add_argument("--days", type=int,
                        help="shortcut: fetch the last N days (ignored if --start is given)")
    parser.add_argument("--category", choices=["spot", "linear", "inverse"], default="spot",
                        help="Bybit market type (spot, USDT perp, or inverse perp)")
    parser.add_argument("--output", help="write CSV to this path instead of printing a preview")
    args = parser.parse_args()

    end = args.end or datetime.now(timezone.utc)
    if args.start:
        start = args.start
    elif args.days:
        start = end - timedelta(days=args.days)
    else:
        start = end - timedelta(days=30)

    if start >= end:
        parser.error("--start must be before --end")

    start_ms = int(start.timestamp() * 1000)
    end_ms = int(end.timestamp() * 1000)

    print(f"Fetching {args.symbol} {args.interval} candles from {args.exchange} "
          f"({start:%Y-%m-%d %H:%M} -> {end:%Y-%m-%d %H:%M} UTC)...", file=sys.stderr)

    if args.exchange == "binance":
        candles = fetch_binance(args.symbol.upper(), args.interval, start_ms, end_ms)
    else:
        candles = fetch_bybit(args.symbol.upper(), args.interval, start_ms, end_ms, args.category)

    if not candles:
        print("No data returned. Check the symbol and date range.", file=sys.stderr)
        sys.exit(1)

    print(f"Got {len(candles)} candles.", file=sys.stderr)

    if args.output:
        write_csv(candles, args.output)
        print(f"Saved to {args.output}", file=sys.stderr)
    else:
        # print a small preview as a table
        print(f"{'datetime (UTC)':<20}{'open':>12}{'high':>12}{'low':>12}{'close':>12}{'volume':>16}")
        shown = candles if len(candles) <= 10 else candles[:5] + candles[-5:]
        for i, c in enumerate(shown):
            if len(candles) > 10 and i == 5:
                print(f"{'...':<20}")
            dt = datetime.fromtimestamp(c["timestamp"] / 1000, tz=timezone.utc)
            print(f"{dt:%Y-%m-%d %H:%M}    {c['open']:>12.4f}{c['high']:>12.4f}"
                  f"{c['low']:>12.4f}{c['close']:>12.4f}{c['volume']:>16.4f}")
        print("\n(use --output prices.csv to save the full dataset)")


if __name__ == "__main__":
    main()
