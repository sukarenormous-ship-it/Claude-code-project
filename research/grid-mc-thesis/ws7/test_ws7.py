#!/usr/bin/env python3
"""Offline fixtures for the WS7 tools. Run: python3 test_ws7.py  (or pytest test_ws7.py)"""
from __future__ import annotations

import csv
import hashlib
import io
import sys
import tempfile
import zipfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import ingest_binance as ing  # noqa: E402
import scale_structure as ss  # noqa: E402


def fake_month(y, m, drop=(), dup=None, conflict=False, bad_ohlc=False, header=False):
    lo, hi = ing.month_bounds_ms(y, m)
    rows = []
    p = 10000.0
    for k, t in enumerate(range(lo, hi, ing.MINUTE_MS)):
        if k in drop:
            continue
        o, c = p, p * (1 + 0.0005 * np.sin(k))
        h, l = max(o, c) * 1.0002, min(o, c) * 0.9998
        if bad_ohlc and k == 5:
            h = l * 0.5
        rows.append([t, o, h, l, c, 1.5, t + ing.MINUTE_MS - 1, 1.0, 3, 0.5, 0.5, 0])
        p = c
    if dup is not None:
        r = list(rows[dup])
        if conflict:
            r[4] = r[4] * 1.01
            r[2] = max(r[2], r[4])
        rows.insert(dup + 1, r)
    buf = io.StringIO()
    w = csv.writer(buf)
    if header:
        w.writerow(["open_time", "open", "high", "low", "close", "volume", "close_time", "qv", "n", "tb", "tq", "i"])
    w.writerows(rows)
    zb = io.BytesIO()
    with zipfile.ZipFile(zb, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(f"BTCUSDT-1m-{y:04d}-{m:02d}.csv", buf.getvalue())
    data = zb.getvalue()
    return data, hashlib.sha256(data).hexdigest()


def test_pass_month():
    zb, ck = fake_month(2018, 2)
    rec, data, gaps = ing.validate_month(2018, 2, zb, ck)
    assert rec["status"] == "PASS", rec
    assert rec["missing_minutes"] == 0 and not gaps and len(data["close"]) == 28 * 1440


def test_header_tolerated():
    zb, ck = fake_month(2018, 2, header=True)
    assert ing.validate_month(2018, 2, zb, ck)[0]["status"] == "PASS"


def test_checksum_mismatch_fails():
    zb, _ = fake_month(2018, 2)
    rec, data, _ = ing.validate_month(2018, 2, zb, "0" * 64)
    assert rec["status"] == "FAIL" and data is None


def test_gap_manifest_no_forward_fill():
    zb, ck = fake_month(2018, 2, drop=range(100, 110))
    rec, data, gaps = ing.validate_month(2018, 2, zb, ck)
    assert rec["status"] == "CONDITIONAL" and rec["missing_minutes"] == 10
    assert len(gaps) == 1 and gaps[0][3] == 10
    assert len(data["close"]) == 28 * 1440 - 10  # nothing filled


def test_identical_duplicate_dropped():
    zb, ck = fake_month(2018, 2, dup=50)
    rec, data, _ = ing.validate_month(2018, 2, zb, ck)
    assert rec["status"] == "CONDITIONAL" and rec["duplicates"] == 1 and len(data["close"]) == 28 * 1440


def test_conflicting_duplicate_fails():
    zb, ck = fake_month(2018, 2, dup=50, conflict=True)
    assert ing.validate_month(2018, 2, zb, ck)[0]["status"] == "FAIL"


def test_bad_ohlc_fails():
    zb, ck = fake_month(2018, 2, bad_ohlc=True)
    assert ing.validate_month(2018, 2, zb, ck)[0]["status"] == "FAIL"


def test_sealed_period_refused():
    for start, end in [("2023-12", "2024-01"), ("2024-03", "2024-03")]:
        try:
            list(ing.month_range(start, end))
        except SystemExit as e:
            assert "REFUSED" in str(e)
        else:
            raise AssertionError("sealed month was not refused")


def test_ingest_end_to_end_from_source_dir():
    with tempfile.TemporaryDirectory() as d:
        src, out = Path(d, "src"), Path(d, "out")
        src.mkdir()
        for m in (1, 2):
            zb, ck = fake_month(2019, m, drop=[7] if m == 2 else ())
            name = ing.archive_name(2019, m)
            (src / name).write_bytes(zb)
            (src / f"{name}.CHECKSUM").write_text(f"{ck}  {name}\n")
        assert ing.main(["--start", "2019-01", "--end", "2019-02", "--out", str(out), "--source-dir", str(src)]) == 0
        assert len(list((out / "canonical").glob("*.npz"))) == 2
        man = list(csv.DictReader(open(out / "provenance_manifest.csv")))
        assert [r["status"] for r in man] == ["PASS", "CONDITIONAL"]
        t, x, _ = ss.load_canonical(out / "canonical")
        assert np.all(np.diff(t) > 0) and len(t) == (31 + 28) * 1440 - 1


def test_grid_exposure_known_paths():
    d = 0.01
    # down 3 cells, back up 3 → buys 3, sells 3, ends flat
    pos, n = ss.grid_exposure(np.array([0.5, -0.5, -1.5, -2.5, -1.5, -0.5, 0.5]) * d, d, 0.6)
    assert n == 91 and list(pos) == [0, 1, 2, 3, 2, 1, 0]
    # pure rise → never holds anything (envelope trails up)
    assert ss.grid_exposure(np.array([0.5, 1.5, 2.5, 3.5]) * d, d, 0.6)[0].max() == 0
    # multi-level gap down then back → 3 lots, all sold
    assert list(ss.grid_exposure(np.array([0.5, -2.5, 0.5]) * d, d, 0.6)[0]) == [0, 3, 0]
    # below L: capped at N, no extra buys; 60% envelope with δ=20% → N=4
    pos, n = ss.grid_exposure(np.log(np.array([1.0, 0.5, 0.2, 0.1, 0.2])), 0.2, 0.6)
    assert n == 4 and pos.max() == 4
    st = ss.grid_stats(np.array([0.5, -0.5, -1.5, -2.5, -1.5, -0.5, 0.5]) * d, d, 0.6, 0.001)
    assert st["cycles"] == 3 and np.isclose(st["fees"], 0.001 * 6 / 91)
    assert st["gross"] > 0  # bought on the way down, sold on the way up


def test_surrogates_keep_vol_path_and_gaps():
    rng = np.random.default_rng(1)
    t, x = ss.synthetic("rw", years=0.1, seed=3)
    r = np.diff(x)
    gap = np.diff(t) != ss.MINUTE_MS
    mu = r[~gap].mean()
    for kind in ss.SURROGATES:
        xs = ss.surrogate(t, x, kind, rng)
        rs = np.diff(xs)
        assert xs.shape == x.shape and xs[0] == x[0]
        assert np.allclose(r[gap], rs[gap]), kind           # gap returns untouched
        assert not np.allclose(r, rs), kind
        assert np.isclose(rs[~gap].mean(), mu, atol=5e-6), kind
    xs = ss.surrogate(t, x, "signflip", rng)
    assert np.allclose(np.abs(np.diff(xs)[~gap] - mu), np.abs(r[~gap] - mu))  # exact |move| sequence


def test_lattice_steps_ignore_wobble():
    d = 0.01
    # wobble across one level many times → no level-to-level step
    assert ss.lattice_steps(np.array([0.1, -0.1, 0.1, -0.1, 0.1]) * d, d).size == 0
    # down two levels, up one → steps [-1, +1] after the first touched level
    st = ss.lattice_steps(np.array([0.5, -0.2, -1.2, -0.1, 0.2]) * d, d)
    assert list(st) == [-1, 1], st
    # jump through three levels at once expands to three −1 steps
    assert list(ss.lattice_steps(np.array([0.5, -2.5]) * d, d)) == [-1, -1]  # touches 0,-1,-2


def test_structure_detected_only_when_present():
    """Mechanism fixture: RW → p_rev z ≈ 0; OU (6h half-life, 2% std) → p_rev z ≫ 0 at 1% spacing.

    Grid PnL z-scores are reported too but have little power here: a 60%-deep envelope's PnL is
    dominated by large drawdowns, which swamp a 2% oscillation (documented, not asserted).
    """
    kw = dict(deltas=(1.0,), kinds=("signflip", "volshuffle"), n_surr=12, fee=0.001, seed=11)
    for kind in ("rw", "ou"):
        t, x = ss.synthetic(kind, years=0.5, seed=5)
        rows, vr, _ = ss.analyse(t, x, **kw)
        r = next(r for r in rows if r["segment"] == "ALL")
        for sk in kw["kinds"]:
            z = r[f"{sk}_p_rev_z"]
            assert (z > 2.5) if kind == "ou" else (abs(z) < 2.5), (kind, sk, z)
        vr_1d = next(v for v in vr if v["horizon_min"] == ss.DAY)["vr_real"]
        assert (vr_1d < 0.8) == (kind == "ou"), (kind, vr_1d)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    for n, f in tests:
        f()
        print(f"PASS {n}")
    print(f"{len(tests)}/{len(tests)} passed")
