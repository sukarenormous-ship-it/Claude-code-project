#!/usr/bin/env python3
"""Independent AIGR 1m event engine (cross-check implementation, NOT the frozen engine).

Implements handoff §11–§13 from the text:
  per-level state machine  ARMED → FILLED/INVENTORY → TP → CASH → REARM_WAIT → ARMED
  * fully funded, equal capital per level: each level owns cash b = B/N, so levels are
    independent and the full-funding invariant holds by construction
  * buy: resting limit at the level; fills in the first bar after arming whose
    low <= level − tick (trade-through); fill price = level
  * TP: resting limit at level + k·Δ_local; fills no earlier than the minute after entry, when
    high >= TP + tick; fill price = TP
  * re-arm (ρ = α·Δ_local): a TP fill at or above level + ρ proves re-arm; the next buy is
    allowed from the following bar (one transition per level per bar, conservative)
  * a level above the first price starts in REARM_WAIT: armed after a bar with high >= level + ρ
  * below L no further levels exist; nothing is force-closed; open lots are marked to market
  * fees on both sides, charged in quote; qty rounded down to the lot step; min notional check
  * missing minutes are never filled: bars are processed in time order; a limit order resting
    through a gap fills at its limit price in the first bar after the gap that trades through it

Geometry is given in lab units on [40, 100] (handoff §5) and scaled by U/100.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

LAB_L, LAB_U = 40.0, 100.0
ZONE_WIDTH = 15.0  # four 15-unit depth zones in [40, 100]


@dataclass(frozen=True)
class Config:
    name: str
    zones: tuple[int, ...]          # levels per zone, shallow → deep (D0=(10,10,10,10))
    k: float = 1.0                  # TP multiplier  τ = k·Δ_local
    alpha: float = 0.5              # re-arm multiplier  ρ = α·Δ_local
    capital: float = 10_000.0
    fee: float = 0.001              # per side
    tick: float = 0.01              # BTCUSDT price tick
    qty_step: float = 1e-6          # BTC lot step
    min_notional: float = 10.0


def lab_levels(zones: tuple[int, ...]) -> tuple[np.ndarray, np.ndarray]:
    """Lab-unit levels and their local spacing, top (shallow) to bottom."""
    lv, dl = [], []
    for z, n in enumerate(zones):
        top = LAB_U - ZONE_WIDTH * z
        d = ZONE_WIDTH / n
        for i in range(1, n + 1):
            lv.append(top - d * i)
            dl.append(d)
    return np.array(lv), np.array(dl)


@dataclass
class Lot:
    level_id: int
    zone: int
    level: float
    entry_bar: int
    qty: float
    cost: float          # quote paid incl. fee
    entry_fee: float
    tp: float
    exit_bar: int = -1
    proceeds: float = 0.0
    exit_fee: float = 0.0


@dataclass
class Result:
    cfg: Config
    levels: np.ndarray
    spacing: np.ndarray
    lots: list[Lot] = field(default_factory=list)


def _first_at_or_after(idx: np.ndarray, t: int) -> int:
    j = np.searchsorted(idx, t)
    return int(idx[j]) if j < idx.size else -1


def run(cfg: Config, high: np.ndarray, low: np.ndarray, open_: np.ndarray, U: float) -> Result:
    lab_lv, lab_d = lab_levels(cfg.zones)
    scale = U / LAB_U
    levels = np.round(lab_lv * scale, 2)
    spacing = lab_d * scale
    n_levels = len(levels)
    b = cfg.capital / n_levels
    res = Result(cfg, levels, spacing)
    zone_of = np.repeat(np.arange(len(cfg.zones)), cfg.zones)
    first_price = float(open_[0])

    for i, (lv, d) in enumerate(zip(levels, spacing)):
        rho = cfg.alpha * d
        tp = round(lv + cfg.k * d, 2)
        buy_idx = np.flatnonzero(low <= lv - cfg.tick)
        tp_idx = np.flatnonzero(high >= tp + cfg.tick)
        if first_price > lv:
            armed_from = 0
        else:
            ra = _first_at_or_after(np.flatnonzero(high >= lv + rho), 0)
            armed_from = -1 if ra < 0 else ra + 1
        notional = b / (1 + cfg.fee)
        qty = np.floor(notional / lv / cfg.qty_step) * cfg.qty_step
        if qty * lv < cfg.min_notional:
            continue
        while armed_from >= 0:
            e = _first_at_or_after(buy_idx, armed_from)
            if e < 0:
                break
            entry_fee = qty * lv * cfg.fee
            lot = Lot(i, int(zone_of[i]), float(lv), e, float(qty), qty * lv + entry_fee, entry_fee, float(tp))
            res.lots.append(lot)
            s = _first_at_or_after(tp_idx, e + 1)
            if s < 0:
                break
            lot.exit_bar = s
            lot.exit_fee = qty * tp * cfg.fee
            lot.proceeds = qty * tp - lot.exit_fee
            assert tp >= lv + rho - 1e-9, "k < alpha needs an explicit re-arm wait"
            armed_from = s + 1
    return res


def ledger_series(res: Result, close: np.ndarray) -> dict:
    """Per-bar cash, inventory qty, inventory MTM and equity (end of bar)."""
    n = close.size
    b = res.cfg.capital
    dcash = np.zeros(n + 1)
    dqty = np.zeros(n + 1)
    dcost = np.zeros(n + 1)
    dfee = np.zeros(n + 1)
    for L in res.lots:
        dcash[L.entry_bar] -= L.cost
        dqty[L.entry_bar] += L.qty
        dcost[L.entry_bar] += L.cost
        dfee[L.entry_bar] += L.entry_fee
        if L.exit_bar >= 0:
            dcash[L.exit_bar] += L.proceeds
            dqty[L.exit_bar] -= L.qty
            dcost[L.exit_bar] -= L.cost
            dfee[L.exit_bar] += L.exit_fee
    cash = b + np.cumsum(dcash[:n])
    qty = np.cumsum(dqty[:n])
    qty[np.abs(qty) < 1e-12] = 0.0
    mtm = qty * close
    return {"cash": cash, "qty": qty, "mtm": mtm, "equity": cash + mtm,
            "cost_basis": np.cumsum(dcost[:n]), "fees_cum": np.cumsum(dfee[:n])}
