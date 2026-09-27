#!/usr/bin/env python3
"""Golden cases for engine_1m.py. Run: python3 test_engine.py"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import engine_1m as eng  # noqa: E402
import ws7b_run as w7  # noqa: E402

D0 = eng.Config("D0/k1", (10, 10, 10, 10), k=1.0)


def bars(seq):
    """seq of (open, high, low, close)."""
    a = np.array(seq, float)
    return a[:, 0], a[:, 1], a[:, 2], a[:, 3]


def run(seq, cfg=D0, U=100.0):
    o, h, l, c = bars(seq)
    return eng.run(cfg, h, l, o, U), c


def test_levels_geometry():
    lv, d = eng.lab_levels((10, 10, 10, 10))
    assert len(lv) == 40 and np.isclose(lv[0], 98.5) and np.isclose(lv[-1], 40.0) and np.allclose(d, 1.5)
    lv3, d3 = eng.lab_levels((6, 8, 12, 14))
    assert len(lv3) == 40 and np.isclose(lv3[0], 97.5) and np.isclose(d3[-1], 15 / 14) and np.isclose(lv3[-1], 40.0)


def test_simple_buy_then_tp_next_minute():
    res, _ = run([(100, 100, 99.9, 100), (100, 100, 98.4, 98.6), (98.6, 100.02, 98.6, 100)])
    lots = [L for L in res.lots if L.level_id == 0]
    assert len(lots) == 1 and lots[0].entry_bar == 1 and lots[0].exit_bar == 2
    L = lots[0]
    assert np.isclose(L.proceeds - L.cost, L.qty * (100 * (1 - 0.001) - 98.5 * (1 + 0.001)))


def test_no_tp_in_entry_bar():
    res, _ = run([(100, 100, 99.9, 100), (100, 100.5, 98.4, 99), (99, 99.1, 98.9, 99)])
    L = [x for x in res.lots if x.level_id == 0][0]
    assert L.entry_bar == 1 and L.exit_bar == -1


def test_trade_through_required():
    res, _ = run([(100, 100, 99.9, 100), (100, 100, 98.5, 98.6)])
    assert not res.lots
    res, _ = run([(100, 100, 99.9, 100), (100, 100, 98.49, 98.6)])
    assert len(res.lots) == 1


def test_jump_through_multiple_levels():
    res, _ = run([(100, 100, 99.9, 100), (100, 100, 95.0, 95.2)])
    assert sorted(L.level for L in res.lots) == [95.5, 97.0, 98.5]


def test_rearm_and_repeat():
    seq = [(100, 100, 99.9, 100), (100, 100, 98.4, 98.6), (98.6, 100.1, 98.6, 100),
           (100, 100, 98.4, 98.6), (98.6, 100.1, 98.6, 100)]
    res, _ = run(seq)
    lots = [L for L in res.lots if L.level_id == 0]
    assert [(L.entry_bar, L.exit_bar) for L in lots] == [(1, 2), (3, 4)]


def test_level_above_start_needs_rearm():
    # start at 98.0: level 98.5 above → needs high >= 98.5 + 0.75 = 99.25 before it can buy
    seq = [(98, 98.2, 97.9, 98), (98, 98.6, 97.9, 98), (98, 99.3, 98, 99.2), (99.2, 99.2, 98.4, 98.6)]
    res, _ = run(seq)
    lots = [L for L in res.lots if L.level_id == 0]
    assert len(lots) == 1 and lots[0].entry_bar == 3


def test_accounting_identity_and_full_funding():
    rng = np.random.default_rng(3)
    x = 100 * np.exp(np.cumsum(rng.normal(0, 0.004, 20000)))
    o = np.concatenate([[100], x[:-1]])
    h = np.maximum(o, x) * (1 + np.abs(rng.normal(0, 0.001, x.size)))
    l = np.minimum(o, x) * (1 - np.abs(rng.normal(0, 0.001, x.size)))
    res = eng.run(D0, h, l, o, 100.0)
    led = eng.ledger_series(res, x)
    assert np.allclose(led["equity"], led["cash"] + led["qty"] * x)
    assert led["cash"].min() >= -1e-9
    for lv in range(40):  # at most one open lot per level at any time
        ls = [L for L in res.lots if L.level_id == lv]
        for a, b in zip(ls, ls[1:]):
            assert a.exit_bar >= 0 and b.entry_bar > a.exit_bar
    realized = sum(L.proceeds - L.cost for L in res.lots if L.exit_bar >= 0)
    open_cost = sum(L.cost for L in res.lots if L.exit_bar < 0)
    assert np.isclose(led["cash"][-1], 10_000 + realized - open_cost)


def test_terminal_inventory_not_closed():
    res, c = run([(100, 100, 99.9, 100), (100, 100, 90, 90.5)])
    led = eng.ledger_series(res, c)
    assert all(L.exit_bar < 0 for L in res.lots) and len(res.lots) == 6
    assert np.isclose(led["mtm"][-1], sum(L.qty for L in res.lots) * 90.5)


def test_deterministic():
    seq = [(100, 100, 99.9, 100), (100, 100, 95, 95.2), (95.2, 99, 95, 98.8), (98.8, 100.2, 97, 100)]
    a, _ = run(seq)
    b, _ = run(seq)
    assert [(L.level_id, L.entry_bar, L.exit_bar, L.qty) for L in a.lots] == \
           [(L.level_id, L.entry_bar, L.exit_bar, L.qty) for L in b.lots]


def test_attribution_reconciles():
    rng = np.random.default_rng(5)
    n = 60 * 24 * 20
    x = 100 * np.exp(np.cumsum(rng.normal(0, 0.001, n)))
    o = np.concatenate([[100], x[:-1]])
    h, l = np.maximum(o, x) * 1.0005, np.minimum(o, x) * 0.9995
    t = np.arange(n, dtype=np.int64) * 60_000
    res = eng.run(D0, h, l, o, 100.0)
    m = w7.metrics(res, t, x, 100.0, 0, int(t[-1]) + 60_000)
    assert abs(m["att_recon_residual"]) < 1e-12 and abs(m["residual_equity"]) < 1e-9
    assert np.isclose(m["fees"], sum(L.entry_fee + L.exit_fee for L in res.lots))


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    for n, f in tests:
        f()
        print(f"PASS {n}")
    print(f"{len(tests)}/{len(tests)} passed")
