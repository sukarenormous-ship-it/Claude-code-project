#!/usr/bin/env python3
"""WS7-B Discovery: frozen candidates on real BTCUSDT 1m, independent engine (engine_1m.py).

Candidates (handoff §11-B, no additions): D0/k1 (Basic control), D0/k1.5, D3/k1; α=0.5, fee 0.10%/side,
B=10,000, N=40, equal capital per level.

Envelope for real data (this runner's pre-declared choice — replace with the frozen addendum's
rule when available): each window starts flat with fresh capital B, U = first open of the
window, L = 0.4·U (lab [40,100] scaled), fixed for the window; no re-anchoring; open lots are
marked to market at the window end, never force-closed.
  * primary:    6 calendar-year windows 2018 … 2023
  * robustness: 12-month windows starting every month (overlapping; descriptive only)

Attribution on the hourly derivative (sums of hourly simple returns, hurdle 0):
  ΣR_net = ē·Σr  (beta)  + Σ(e_{t−1}−ē)·r  (timing)  + [ΣR_gross − Σe_{t−1}·r]  (execution)
         + [ΣR_net − ΣR_gross]  (cost)
where e = inventory MTM / equity at the previous hour end and R_gross adds fees back.

Usage: python3 ws7b_run.py --data data/canonical --out results/ws7b
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import engine_1m as eng  # noqa: E402

SEALED_FROM_MS = int(dt.datetime(2024, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
HOUR_MS = 3_600_000
CANDIDATES = (
    eng.Config("D0/k1", (10, 10, 10, 10), k=1.0),
    eng.Config("D0/k1.5", (10, 10, 10, 10), k=1.5),
    eng.Config("D3/k1", (6, 8, 12, 14), k=1.0),
)


def load(data_dir: Path) -> tuple[dict, str]:
    files = sorted(data_dir.glob("*.npz"))
    h = hashlib.sha256()
    parts = {k: [] for k in ("open_time_ms", "open", "high", "low", "close")}
    for f in files:
        h.update(f.read_bytes())
        z = np.load(f)
        for k in parts:
            parts[k].append(z[k])
    d = {k: np.concatenate(v) for k, v in parts.items()}
    if np.any(d["open_time_ms"] >= SEALED_FROM_MS):
        raise SystemExit("REFUSED: sealed OOS timestamps present")
    if np.any(np.diff(d["open_time_ms"]) <= 0):
        raise SystemExit("canonical data not strictly increasing")
    return d, h.hexdigest()


def utc(ms: int) -> dt.datetime:
    return dt.datetime.fromtimestamp(ms / 1000, tz=dt.timezone.utc)


def ms(y: int, m: int) -> int:
    return int(dt.datetime(y, m, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)


def windows(t: np.ndarray, mode: str):
    if mode == "year":
        for y in range(2018, 2024):
            yield str(y), ms(y, 1), ms(y + 1, 1)
    else:
        for y in range(2018, 2024):
            for m in range(1, 13):
                a = ms(y, m)
                y2, m2 = (y + 1, m)
                b = ms(y2, m2)
                if b <= SEALED_FROM_MS:
                    yield f"{y}-{m:02d}+12m", a, b


def attribution(t, close, open0, led, capital) -> dict:
    hour = t // HOUR_MS
    ends = np.flatnonzero(np.diff(np.concatenate([hour, [hour[-1] + 1]])) != 0)
    eq = np.concatenate([[capital], led["equity"][ends]])
    eqg = np.concatenate([[capital], led["equity"][ends] + led["fees_cum"][ends]])
    px = np.concatenate([[open0], close[ends]])
    e_prev = np.concatenate([[0.0], (led["mtm"][ends] / led["equity"][ends])])[:-1]
    r = px[1:] / px[:-1] - 1
    R = eq[1:] / eq[:-1] - 1
    Rg = eqg[1:] / eqg[:-1] - 1
    ebar = float(e_prev.mean())
    beta = ebar * r.sum()
    timing = float(((e_prev - ebar) * r).sum())
    shadow = float((e_prev * r).sum())
    out = {"sumR_net": float(R.sum()), "mean_exposure": ebar, "beta": float(beta), "timing": timing,
           "execution": float(Rg.sum() - shadow), "cost": float(R.sum() - Rg.sum()),
           "hodl_ebar": float(beta), "asset_sum_r": float(r.sum())}
    out["recon_residual"] = out["sumR_net"] - (out["beta"] + out["timing"] + out["execution"] + out["cost"])
    peak = np.maximum.accumulate(eq)
    out["max_dd"] = float(((peak - eq) / peak).max())
    return out


def metrics(res: eng.Result, t, close, open0, a_ms, b_ms) -> dict:
    cfg = res.cfg
    led = eng.ledger_series(res, close)
    lots = res.lots
    closed = [L for L in lots if L.exit_bar >= 0]
    open_ = [L for L in lots if L.exit_bar < 0]
    yrs = (b_ms - a_ms) / (365.25 * 86_400_000)
    end_ms = b_ms
    realized = sum(L.proceeds - L.cost for L in closed)
    fees = sum(L.entry_fee + L.exit_fee for L in lots)
    ttp_h = np.array([(t[L.exit_bar] - t[L.entry_bar]) / HOUR_MS for L in closed])
    hold_y = np.array([((t[L.exit_bar] if L.exit_bar >= 0 else end_ms) - t[L.entry_bar]) / (365.25 * 86_400_000)
                       for L in lots])
    obs7 = [L for L in lots if end_ms - t[L.entry_bar] >= 7 * 86_400_000]
    tp_times = sorted(t[L.exit_bar] for L in closed)
    marks = [a_ms] + tp_times + [end_ms]
    drought_d = max(np.diff(marks)) / 86_400_000 if len(marks) > 1 else (end_ms - a_ms) / 86_400_000
    months = {}
    for L in closed:
        k = utc(int(t[L.exit_bar])).strftime("%Y-%m")
        months[k] = months.get(k, 0.0) + (L.proceeds - L.cost)
    all_months = []
    y, m = utc(a_ms).year, utc(a_ms).month
    while ms(y, m) < b_ms:
        all_months.append(months.get(f"{y}-{m:02d}", 0.0))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    equity_T = float(led["equity"][-1])
    att = attribution(t, close, open0, led, cfg.capital)
    assert np.all(led["cash"] >= -1e-6), "full-funding invariant violated"
    return {
        "return_pct": 100 * (equity_T / cfg.capital - 1),
        "realized_cf": realized, "tp_count": len(closed),
        "net_per_tp": realized / len(closed) if closed else float("nan"),
        "fees": fees, "fee_drag_pct": 100 * fees / cfg.capital,
        "ttp_median_h": float(np.median(ttp_h)) if closed else float("nan"),
        "p_tp_24h": float(np.mean([(L.exit_bar >= 0 and t[L.exit_bar] - t[L.entry_bar] <= 86_400_000) for L in obs7])) if obs7 else float("nan"),
        "p_tp_7d": float(np.mean([(L.exit_bar >= 0 and t[L.exit_bar] - t[L.entry_bar] <= 7 * 86_400_000) for L in obs7])) if obs7 else float("nan"),
        "drought_days": float(drought_d),
        "median_month_cf": float(np.median(all_months)), "pct_pos_months": 100 * float(np.mean(np.array(all_months) > 0)),
        "lct_usdt_y": float(sum(L.cost * h for L, h in zip(lots, hold_y))),
        "inv_age_q90_d": float(np.quantile(hold_y, 0.9) * 365.25) if lots else float("nan"),
        "open_lots": len(open_), "open_cost": float(sum(L.cost for L in open_)),
        "open_mtm": float(led["mtm"][-1]), "cash_T": float(led["cash"][-1]), "equity_T": equity_T,
        "committed_max": float(led["cost_basis"].max()),
        "residual_equity": float(led["equity"][-1] - (led["cash"][-1] + led["mtm"][-1])),
        **{f"att_{k}": v for k, v in att.items()},
        "years": yrs,
    }


def run_all(d, mode):
    t = d["open_time_ms"]
    rows = []
    for name, a, b in windows(t, mode):
        sel = np.flatnonzero((t >= a) & (t < b))
        if sel.size < 1000:
            continue
        s = slice(sel[0], sel[-1] + 1)
        tt, o, h, l, c = t[s], d["open"][s], d["high"][s], d["low"][s], d["close"][s]
        U = float(o[0])
        for cfg in CANDIDATES:
            res = eng.run(cfg, h, l, o, U)
            m = metrics(res, tt, c, U, a, b)
            rows.append({"window": name, "candidate": cfg.name, "U": U, "L": 0.4 * U,
                         "start_px": U, "end_px": float(c[-1]), **m})
    return rows


def write_csv(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def fmt(v, p=1):
    return f"{v:+.{p}f}" if isinstance(v, float) else str(v)


def summary(year_rows, roll_rows, meta) -> str:
    L = [f"# WS7-B Discovery — frozen candidates on BTCUSDT 1m (independent engine)", "",
         f"- data sha256 `{meta['data_sha256']}` · data policy v1.0 · engine `engine_1m.py` (cross-check, not frozen)",
         "- B=10,000 · N=40 · α=0.5 · fee 0.10%/side · trade-through 1 tick · TP ≥ next minute",
         "- envelope per window: U = first open, L = 0.4·U, fixed; fresh capital; open lots MTM at window end", ""]
    L += ["## Calendar-year windows", "",
          "| year | BTC Δ% | cand | return % | realized CF | TP | net $/TP | fees | ē | beta % | timing % | exec % | cost % | MaxDD % | open lots | drought d |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in year_rows:
        L.append(f"| {r['window']} | {100 * (r['end_px'] / r['start_px'] - 1):+.0f} | {r['candidate']} | "
                 f"{r['return_pct']:+.1f} | {r['realized_cf']:,.0f} | {r['tp_count']} | {r['net_per_tp']:.2f} | "
                 f"{r['fees']:,.0f} | {r['att_mean_exposure']:.2f} | {100 * r['att_beta']:+.1f} | "
                 f"{100 * r['att_timing']:+.1f} | {100 * r['att_execution']:+.1f} | {100 * r['att_cost']:+.1f} | "
                 f"{100 * r['att_max_dd']:.1f} | {r['open_lots']} | {r['drought_days']:.0f} |")
    L += ["", "## Challenger − Basic (D0/k1), calendar years", "",
          "| year | challenger | Δ return pp | Δ realized CF | Δ TP | Δ ē | Δ beta pp | Δ timing pp | Δ exec pp | Δ cost pp | Δ MaxDD pp |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    by = {(r["window"], r["candidate"]): r for r in year_rows}
    signs = {}
    for (w, c), r in by.items():
        if c == "D0/k1":
            continue
        b = by[(w, "D0/k1")]
        dd = {k: r[k] - b[k] for k in ("return_pct", "realized_cf", "tp_count", "att_mean_exposure", "att_beta",
                                      "att_timing", "att_execution", "att_cost", "att_max_dd")}
        signs.setdefault(c, []).append(dd)
        L.append(f"| {w} | {c} | {dd['return_pct']:+.1f} | {dd['realized_cf']:+,.0f} | {dd['tp_count']:+d} | "
                 f"{dd['att_mean_exposure']:+.2f} | {100 * dd['att_beta']:+.1f} | {100 * dd['att_timing']:+.1f} | "
                 f"{100 * dd['att_execution']:+.1f} | {100 * dd['att_cost']:+.1f} | {100 * dd['att_max_dd']:+.1f} |")
    L += ["", "### Sign consistency across the 6 years (count of years with Δ > 0)", "",
          "| challenger | return | realized CF | timing | beta |", "|---|---|---|---|---|"]
    for c, lst in signs.items():
        cnt = lambda k: sum(x[k] > 0 for x in lst)
        L.append(f"| {c} | {cnt('return_pct')}/6 | {cnt('realized_cf')}/6 | {cnt('att_timing')}/6 | {cnt('att_beta')}/6 |")
    L += ["", "## Rolling 12-month windows (monthly starts, overlapping — descriptive)", "",
          "| challenger | n | median Δ return pp | % windows Δ return > 0 | median Δ realized CF | % Δ CF > 0 | median Δ timing pp | % Δ timing > 0 |",
          "|---|---|---|---|---|---|---|---|"]
    rb = {(r["window"], r["candidate"]): r for r in roll_rows}
    for c in ("D0/k1.5", "D3/k1"):
        ds = [(rb[(w, c)], rb[(w, "D0/k1")]) for (w, cc) in rb if cc == c]
        dr = np.array([a["return_pct"] - b["return_pct"] for a, b in ds])
        dc = np.array([a["realized_cf"] - b["realized_cf"] for a, b in ds])
        dtm = np.array([a["att_timing"] - b["att_timing"] for a, b in ds])
        L.append(f"| {c} | {len(ds)} | {np.median(dr):+.1f} | {100 * np.mean(dr > 0):.0f}% | {np.median(dc):+,.0f} | "
                 f"{100 * np.mean(dc > 0):.0f}% | {100 * np.median(dtm):+.2f} | {100 * np.mean(dtm > 0):.0f}% |")
    L += ["", "Attribution is on sums of hourly simple returns (not compounded), hurdle 0; "
          "rows reconcile to ΣR_net by construction (max |residual| reported in meta.json). "
          "Rolling windows overlap and are not independent. Discovery data — characterize/falsify only.", ""]
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    d, sha = load(args.data)
    year_rows = run_all(d, "year")
    roll_rows = run_all(d, "roll")
    args.out.mkdir(parents=True, exist_ok=True)
    write_csv(args.out / "runs_year.csv", year_rows)
    write_csv(args.out / "runs_rolling12m.csv", roll_rows)
    all_rows = year_rows + roll_rows
    meta = {"data_sha256": sha, "candidates": [c.__dict__ for c in CANDIDATES],
            "max_abs_recon_residual": max(abs(r["att_recon_residual"]) for r in all_rows),
            "max_abs_equity_residual": max(abs(r["residual_equity"]) for r in all_rows),
            "engine_sha256": hashlib.sha256(Path(eng.__file__).read_bytes()).hexdigest()}
    (args.out / "meta.json").write_text(json.dumps(meta, indent=2))
    md = summary(year_rows, roll_rows, meta)
    (args.out / "summary.md").write_text(md)
    print(md)
    print(json.dumps({k: meta[k] for k in ("max_abs_recon_residual", "max_abs_equity_residual")}))


if __name__ == "__main__":
    main()
