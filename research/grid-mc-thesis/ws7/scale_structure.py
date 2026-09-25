#!/usr/bin/env python3
"""WS7-A market-process characterization: mean-reversion structure by grid scale.

Descriptive only — no strategy candidate, no parameter selection (AIGR §11-A).

Primary statistic — lattice reversal probability at log spacing δ:
  p_rev(δ) = P(next level-to-level step reverses the previous one)
  p_up_after_down(δ) = after a down-crossing (a buy), P(reach the next level up — the k=1 TP —
                       before the next level down). This is the empirical H(1) at spacing δ.
For a driftless martingale both are 0.5 (minus a small close-sampling bias, which the
surrogates share — so always read them against the surrogates, not against 0.5).

Economic context — "trailing envelope grid": a fully funded grid with equal capital per level
spanning `depth` below the running maximum U_t (lab: L = 0.4·U), N = floor(ln(1/(1-depth))/δ)
levels, exposure e_t = min(M_t − j_t, N)/N (j_t lattice cell of the close, M_t its running
max). Per δ (fractions of capital B, log-return approximation):
  * gross   G  = Σ e_{t−1} r_t
  * timing  TT = Σ (e_{t−1} − ē) r_t
  * sawtooth S = G − G_smooth, G_smooth using the continuous exposure min((M^x_t − x_t)/D, 1)
  * cycles (sells) per year and fee drag
These have low power for small-scale structure (large drawdowns dominate G); report them for
magnitude, decide structure with p_rev.

Every statistic is compared with surrogate paths that keep the vol path but carry no sign
dependence (see `surrogate`); z = (real − surrogate mean) / surrogate sd.

Why not raw cycle counts: lattice crossings are driven by quadratic variation at scale δ,
which the surrogates preserve by construction — counts barely move even with strong mean
reversion (see test_ws7.py). Counts are still reported for fee drag.

Also reports variance ratios VR(q) = Var(r_q) / (q · Var(r_1)) for real vs surrogates.

Limits: close-to-close path (sub-minute crossings ignored for real and surrogates alike);
frictionless fills at the close; unbounded upward trailing of U; gaps never filled (the
return across a gap stays in place and is never shuffled).

Usage:
  python3 scale_structure.py --data data/canonical --out results/ws7a
  python3 scale_structure.py --synthetic ou --out /tmp/check      # self-check fixture
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

SEALED_FROM_MS = int(dt.datetime(2024, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
MINUTE_MS = 60_000
DAY = 1440

DELTAS_PCT = (0.25, 0.5, 1.0, 2.0, 4.0, 8.0)
SURROGATES = ("signflip", "volshuffle", "iid")
VR_HORIZONS_MIN = (5, 15, 60, 240, DAY, 3 * DAY, 7 * DAY)


# ---------------------------------------------------------------- data

def load_canonical(data_dir: Path) -> tuple[np.ndarray, np.ndarray, str]:
    files = sorted(data_dir.glob("*.npz"))
    if not files:
        raise SystemExit(f"no canonical .npz files in {data_dir}")
    h = hashlib.sha256()
    ts, cs = [], []
    for f in files:
        h.update(f.read_bytes())
        z = np.load(f)
        ts.append(z["open_time_ms"])
        cs.append(z["close"])
    t = np.concatenate(ts)
    c = np.concatenate(cs)
    if np.any(t >= SEALED_FROM_MS):
        raise SystemExit("REFUSED: canonical data contains sealed OOS timestamps (>= 2024-01-01)")
    if np.any(np.diff(t) <= 0):
        raise SystemExit("canonical data not strictly increasing — rerun ingestion")
    return t, np.log(c), h.hexdigest()


def synthetic(kind: str, years: float = 2.0, seed: int = 7) -> tuple[np.ndarray, np.ndarray]:
    """Fixtures: 'rw' = random walk (no structure); 'ou' = RW + mean-reverting component."""
    rng = np.random.default_rng(seed)
    n = int(years * 365 * DAY)
    sigma = 0.0008  # ~ BTC-like 1m vol
    x = np.cumsum(rng.normal(0, sigma, n))
    if kind == "ou":
        # OU deviation around the RW with a ~6h half-life and ~2% stationary std
        theta = np.log(2) / 360
        s = 0.02 * np.sqrt(2 * theta)
        e = rng.normal(0, s, n)
        u = np.empty(n)
        u[0] = 0.0
        a = 1 - theta
        for i in range(1, n):
            u[i] = a * u[i - 1] + e[i]
        x = x + u
    elif kind != "rw":
        raise SystemExit(f"unknown synthetic kind {kind}")
    t = np.arange(n, dtype=np.int64) * MINUTE_MS
    keep = np.ones(n, bool)
    keep[rng.choice(n, 200, replace=False)] = False  # sprinkle gaps
    return t[keep], np.log(30000.0) + x[keep]


# ---------------------------------------------------------------- statistics

def grid_exposure(x: np.ndarray, delta: float, depth: float) -> tuple[np.ndarray, int]:
    """Lots held (0..N) by the trailing-envelope grid, and N."""
    n_levels = int(np.floor(np.log(1 / (1 - depth)) / delta))
    j = np.floor(x / delta).astype(np.int64)
    pos = np.minimum(np.maximum.accumulate(j) - j, n_levels)
    return pos, n_levels


def lattice_steps(x: np.ndarray, delta: float) -> np.ndarray:
    """Level-to-level steps (+1/−1) of the level-touch sequence at log spacing delta.

    A step is recorded when price reaches the level one above or one below the last level it
    touched; re-touching the same level is not a step (so bid/ask-style wobble around one
    level does not count as a reversal). Multi-level jumps expand to one step per level.
    """
    j = np.floor(x / delta).astype(np.int64)
    d = np.diff(j)
    nz = np.nonzero(d)[0]
    if nz.size == 0:
        return np.zeros(0, np.int64)
    c, dd = j[nz], d[nz]
    n = np.abs(dd)
    start = np.repeat(np.cumsum(n) - n, n)
    k = np.arange(n.sum()) - start
    up = np.repeat(dd > 0, n)
    cc = np.repeat(c, n)
    touched = np.where(up, cc + 1 + k, cc - k)
    keep = np.concatenate([[True], touched[1:] != touched[:-1]])
    steps = np.diff(touched[keep])
    assert np.all(np.abs(steps) == 1)
    return steps


def reversal_stats(x: np.ndarray, delta: float) -> dict:
    """p_rev = P(next level-to-level step reverses the previous one); 0.5 for a driftless martingale.

    p_up_after_down is the grid-relevant half: after a down-crossing (a buy), does price reach
    the next level up (the k=1 TP) before the next level down?
    """
    s = lattice_steps(x, delta)
    if s.size < 3:
        return {"steps": int(s.size), "p_rev": float("nan"), "p_up_after_down": float("nan")}
    prev, nxt = s[:-1], s[1:]
    down = prev < 0
    return {"steps": int(s.size), "p_rev": float((prev != nxt).mean()),
            "p_up_after_down": float((nxt[down] > 0).mean()) if down.any() else float("nan")}


def grid_stats(x: np.ndarray, delta: float, depth: float, fee: float) -> dict:
    pos, n = grid_exposure(x, delta, depth)
    e = pos[:-1] / n
    r = np.diff(x)
    dpos = np.diff(pos)
    sells = int(-dpos[dpos < 0].sum())
    trades = int(np.abs(dpos).sum())
    smooth = np.minimum((np.maximum.accumulate(x) - x) / np.log(1 / (1 - depth)), 1.0)[:-1]
    g = float(e @ r)
    return {"gross": g, "timing": g - float(e.mean() * r.sum()), "sawtooth": g - float(smooth @ r),
            "mean_exposure": float(e.mean()), "cycles": sells, "fees": fee * trades / n, "levels": n}


def surrogate(t: np.ndarray, x: np.ndarray, kind: str, rng) -> np.ndarray:
    """Null paths with no sign dependence and nothing pinned except the start.

    signflip   : r' = μ + |r − μ|·(±1)      exact |move| sequence (vol path), random signs
    volshuffle : r' = μ + σ_t · z_π(t)       z = (r − μ)/σ_t shuffled over the whole sample,
                                             σ_t = trailing 1-day RMS of (r − μ)
    iid        : r' = r_π(t)                 global shuffle (also destroys vol clustering)

    Returns across data gaps stay in place. Do NOT shuffle within fixed windows: that pins
    every window's endpoints, i.e. builds mean reversion to them into the null — a grid
    harvests exactly that, so the null would be biased in the grid's favour.
    """
    r = np.diff(x)
    ok = np.diff(t) == MINUTE_MS
    idx = np.where(ok)[0]
    mu = r[idx].mean()
    r2 = r.copy()
    if kind == "signflip":
        r2[idx] = mu + np.abs(r[idx] - mu) * rng.choice((-1.0, 1.0), idx.size)
    elif kind == "volshuffle":
        dev = r[idx] - mu
        c = np.concatenate([[0.0], np.cumsum(dev * dev)])
        k = np.arange(1, idx.size + 1)
        lo = np.maximum(k - DAY, 0)
        sig = np.sqrt((c[k] - c[lo]) / (k - lo))
        sig = np.concatenate([[sig[0]], sig[:-1]])  # trailing, excludes the current return
        sig[sig == 0] = dev.std()
        z = dev / sig
        r2[idx] = mu + sig * z[rng.permutation(idx.size)]
    elif kind == "iid":
        r2[idx] = r[idx][rng.permutation(idx.size)]
    else:
        raise ValueError(kind)
    return np.concatenate([[x[0]], x[0] + np.cumsum(r2)])


def variance_ratios(t: np.ndarray, x: np.ndarray, horizons) -> dict:
    m = ((t - t[0]) // MINUTE_MS).astype(np.int64)
    dense = np.full(m[-1] + 1, np.nan)
    dense[m] = x
    r1 = np.diff(dense)
    v1 = np.nanvar(r1)
    out = {}
    for q in horizons:
        rq = dense[q:] - dense[:-q]
        out[q] = float(np.nanvar(rq) / (q * v1))
    return out


def year_slices(t: np.ndarray):
    years = np.array([dt.datetime.fromtimestamp(s / 1000, tz=dt.timezone.utc).year for s in t[[0, -1]]])
    for y in range(years[0], years[1] + 1):
        lo = dt.datetime(y, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000
        hi = dt.datetime(y + 1, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000
        sel = np.where((t >= lo) & (t < hi))[0]
        if sel.size > DAY:
            yield str(y), slice(sel[0], sel[-1] + 1)


# ---------------------------------------------------------------- driver

STATS = ("gross", "timing", "sawtooth", "p_rev", "p_up_after_down")


def analyse(t, x, deltas, kinds, n_surr, fee, seed, depth=0.6):
    rng = np.random.default_rng(seed)
    segments = [("ALL", slice(0, len(t)))] + list(year_slices(t))
    years = {name: (t[s][-1] - t[s][0]) / MINUTE_MS / (365 * DAY) for name, s in segments}

    both = lambda xx, d: {**grid_stats(xx, d / 100, depth, fee), **reversal_stats(xx, d / 100)}
    real = {name: {d: both(x[s], d) for d in deltas} for name, s in segments}
    vr_real = variance_ratios(t, x, VR_HORIZONS_MIN)

    surr = {w: {name: {d: {k: [] for k in STATS} for d in deltas} for name, _ in segments} for w in kinds}
    vr_surr = {w: {q: [] for q in VR_HORIZONS_MIN} for w in kinds}
    for w in kinds:
        for _ in range(n_surr):
            xs = surrogate(t, x, w, rng)
            for name, s in segments:
                for d in deltas:
                    st = both(xs[s], d)
                    for k in STATS:
                        surr[w][name][d][k].append(st[k])
            for q, v in variance_ratios(t, xs, VR_HORIZONS_MIN).items():
                vr_surr[w][q].append(v)

    rows = []
    for name, _ in segments:
        yrs = years[name]
        for d in deltas:
            st = real[name][d]
            row = {"segment": name, "delta_pct": d, "levels": st["levels"], "mean_exposure": st["mean_exposure"],
                   "cycles_per_year": st["cycles"] / yrs, "fee_drag_pct_yr": 100 * st["fees"] / yrs}
            for k in ("gross", "timing", "sawtooth"):
                row[f"{k}_pct_yr"] = 100 * st[k] / yrs
            row.update(steps=st["steps"], p_rev=st["p_rev"], p_up_after_down=st["p_up_after_down"])
            row["net_timing_pct_yr"] = 100 * (st["timing"] - st["fees"]) / yrs
            for w in kinds:
                tag = w
                for k in STATS:
                    a = np.array(surr[w][name][d][k])
                    sd = a.std(ddof=1) if a.size > 1 else float("nan")
                    row[f"{tag}_{k}_z"] = float((st[k] - a.mean()) / sd) if sd > 0 else float("nan")
                    row[f"{tag}_{k}_pctile"] = float((a < st[k]).mean())
                    row[f"{tag}_{k}_mean"] = float(a.mean())
            rows.append(row)

    vr_rows = []
    for q in VR_HORIZONS_MIN:
        row = {"horizon_min": q, "vr_real": vr_real[q]}
        for w in kinds:
            a = np.array(vr_surr[w][q])
            tag = w
            row[f"{tag}_vr_surr_mean"] = float(a.mean())
            row[f"{tag}_vr_pctile"] = float((a < vr_real[q]).mean())
        vr_rows.append(row)
    return rows, vr_rows, years["ALL"]


def write_csv(path: Path, rows: list[dict]) -> None:
    import csv

    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def summary_md(rows, vr_rows, meta, kinds) -> str:
    w_main = kinds[0]
    hz = lambda q: f"{q}m" if q < 60 else (f"{q // 60}h" if q < DAY else f"{q // DAY}d")
    lines = [f"# WS7-A scale structure — {meta['source']}", "",
             f"- span: {meta['start']} → {meta['end']} ({meta['years']:.2f} y), points: {meta['n_points']:,}",
             f"- data sha256: `{meta['data_sha256']}`",
             f"- trailing envelope depth {meta['depth'] * 100:.0f}% below running max; fee/side "
             f"{meta['fee'] * 100:.3f}%; surrogates per kind {meta['n_surrogates']}; seed {meta['seed']}", "",
             "## Grid statistics, all data (% of B per year)", "",
             "| δ % | N | ē | cycles/yr | fee drag | gross | timing | net timing | sawtooth | " +
             " | ".join(f"z gross / timing / sawtooth ({w})" for w in kinds) + " |",
             "|---|---|---|---|---|---|---|---|---|" + "---|" * len(kinds)]
    for r in rows:
        if r["segment"] != "ALL":
            continue
        z = " | ".join(f"{r[f'{w}_gross_z']:+.1f} / {r[f'{w}_timing_z']:+.1f} / {r[f'{w}_sawtooth_z']:+.1f}"
                       for w in kinds)
        lines.append(f"| {r['delta_pct']} | {r['levels']} | {r['mean_exposure']:.2f} | {r['cycles_per_year']:.0f} | "
                     f"{r['fee_drag_pct_yr']:.2f} | {r['gross_pct_yr']:+.2f} | {r['timing_pct_yr']:+.2f} | "
                     f"{r['net_timing_pct_yr']:+.2f} | {r['sawtooth_pct_yr']:+.2f} | {z} |")
    lines += ["", "## Lattice reversal probability, all data (0.5 = martingale)", "",
              "| δ % | steps | p_rev | p(up after down) | " +
              " | ".join(f"z p_rev ({w}) / surr mean" for w in kinds) + " |",
              "|---|---|---|---|" + "---|" * len(kinds)]
    for r in rows:
        if r["segment"] != "ALL":
            continue
        z = " | ".join(f"{r[f'{w}_p_rev_z']:+.1f} / {r[f'{w}_p_rev_mean']:.4f}" for w in kinds)
        lines.append(f"| {r['delta_pct']} | {r['steps']:,} | {r['p_rev']:.4f} | {r['p_up_after_down']:.4f} | {z} |")
    lines += ["", f"## Stability by year — p_rev z vs {w_main} surrogates", "",
              "| year | " + " | ".join(f"δ {d}%" for d in meta["deltas"]) + " |",
              "|---|" + "---|" * len(meta["deltas"])]
    for y in sorted({r["segment"] for r in rows if r["segment"] != "ALL"}):
        lines.append(f"| {y} | " + " | ".join(f"{r[f'{w_main}_p_rev_z']:+.1f}" for r in rows if r["segment"] == y) + " |")
    lines += ["", "## Variance ratio", "", "| horizon | VR real | " +
              " | ".join(f"VR {w} (pctile)" for w in kinds) + " |",
              "|---|---|" + "---|" * len(kinds)]
    for r in vr_rows:
        cells = " | ".join(f"{r[f'{w}_vr_surr_mean']:.3f} ({r[f'{w}_vr_pctile']:.2f})" for w in kinds)
        lines.append(f"| {hz(r['horizon_min'])} | {r['vr_real']:.3f} | {cells} |")
    lines += ["", "Reading: p_rev z ≫ 0 at spacing δ → price reverses between adjacent levels more often than "
              "on sign-random paths with the same moves: the structure a grid at that spacing harvests. "
              "z = (real − surrogate mean) / surrogate sd. gross z ≫ 0 → the grid earns more on the real "
              "path than on paths with the same moves but random signs (harvestable mean reversion); sawtooth "
              "z ≫ 0 → the lattice at spacing δ adds harvest beyond the smooth envelope exposure. timing uses the "
              "ex-post mean exposure ē, which is biased upward even under a martingale (ē and Σr are negatively "
              "correlated) — compare it with surrogates, never with 0. Net timing subtracts fees only (no "
              "hurdle). Process statistic, not a backtest.", ""]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--data", type=Path, help="canonical .npz directory from ingest_binance.py")
    src.add_argument("--synthetic", choices=["rw", "ou"])
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--surrogates", type=int, default=50)
    ap.add_argument("--fee", type=float, default=0.001, help="fee per side (0.001 = 0.10%%)")
    ap.add_argument("--seed", type=int, default=20260925)
    ap.add_argument("--years", type=float, default=2.0, help="synthetic length")
    ap.add_argument("--depth", type=float, default=0.6, help="envelope depth below running max (lab: 0.6)")
    args = ap.parse_args(argv)

    if args.data:
        t, x, sha = load_canonical(args.data)
        source = str(args.data)
    else:
        t, x = synthetic(args.synthetic, args.years)
        sha, source = "synthetic", f"synthetic:{args.synthetic}"

    rows, vr_rows, years = analyse(t, x, DELTAS_PCT, SURROGATES, args.surrogates, args.fee, args.seed, args.depth)
    iso = lambda ms: dt.datetime.fromtimestamp(ms / 1000, tz=dt.timezone.utc).strftime("%Y-%m-%d")
    meta = {"source": source, "start": iso(t[0]), "end": iso(t[-1]), "years": years, "n_points": int(len(t)),
            "data_sha256": sha, "n_surrogates": args.surrogates, "fee": args.fee, "seed": args.seed, "depth": args.depth,
            "deltas": list(DELTAS_PCT), "surrogates": list(SURROGATES)}
    args.out.mkdir(parents=True, exist_ok=True)
    write_csv(args.out / "grid_scale.csv", rows)
    write_csv(args.out / "variance_ratio.csv", vr_rows)
    (args.out / "meta.json").write_text(json.dumps(meta, indent=2))
    md = summary_md(rows, vr_rows, meta, SURROGATES)
    (args.out / "summary.md").write_text(md)
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
