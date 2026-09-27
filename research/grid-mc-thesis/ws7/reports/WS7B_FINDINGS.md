# WS7-B Findings — frozen candidates on BTCUSDT Spot 1m, 2018–2023 (Discovery)

**Engine:** `engine_1m.py` — independent cross-check implementation of handoff §11–§13, **not the frozen engine** (golden tests 11/11 in `test_engine.py`)
**Data:** canonical sha256 `9d854236…1676` under `DATA_POLICY_v1.0.md` (accepted) · 2024+ SEALED, not downloaded
**Candidates (no additions):** D0/k1 (Basic control), D0/k1.5, D3/k1 · α=0.5 · B=10,000 · N=40 · fee 0.10%/side · trade-through 1 tick · TP ≥ next minute
**Envelope (this runner's choice, pending the frozen addendum):** each window starts flat, U = first open, L = 0.4·U, fixed; open lots MTM at window end, never force-closed
**Reconciliation:** attribution residual ≤ 2e-16; equity − (cash + MTM) = 0 in every run

## 1. The envelope dominates everything

| year | BTC | D0/k1 return | lots open at end | reason |
|---|---|---|---|---|
| 2018 | −73% | −18.6% | 40/40 | fell below L; full inventory |
| 2019 | +94% | +1.1% | 0 | price above U almost all year → idle cash |
| 2020 | +302% | +16.3% | 0 | harvested March crash + recovery, then idle above U |
| 2021 | +60% | +0.1% | 0 | above U from the first days |
| 2022 | −64% | −27.7% | 40/40 | below L |
| 2023 | +156% | 0.0% | 0 | never traded |

A fixed envelope anchored at the window's opening price turns the grid into "cash in rising years, full inventory in falling years". **3 of the 6 years carry almost no information about geometry** (15 of 61 rolling windows have ≤ 50 TPs). Envelope policy — which AIGR leaves to the user — is the first-order driver; spacing and TP are second-order.

## 2. Challengers vs Basic

### Calendar years (Δ vs D0/k1, pp of B)

| challenger | years Δ return > 0 | years Δ realized CF > 0 | years Δ timing > 0 |
|---|---|---|---|
| D0/k1.5 | 2/6 | 2/6 | 2/6 |
| D3/k1 | 2/6 | 1/6 | 1/6 |

Differences are small (|Δ return| ≤ 1.3 pp for k1.5; ≤ 5.4 pp for D3).

### Active rolling 12-month windows (46 of 61, overlapping), median Δ vs D0/k1

| challenger | Δ return | Δ beta | Δ timing | Δ execution | Δ cost | % windows Δ return > 0 | % Δ timing > 0 | % Δ cost > 0 |
|---|---|---|---|---|---|---|---|---|
| D0/k1.5 | +0.52 | +0.05 | +0.00 | +0.13 | **+0.47** | 83% | 50% | **100%** |
| D3/k1 | +0.14 | **−0.67** | −0.09 | −0.23 | +0.24 | 52% | 48% | 78% |

**Reading**

1. **D0/k1.5:** its small, frequent advantage is **fee saving** — fewer round trips (≈ −35% TPs) cost less in 100% of active windows, while the timing term is a coin flip (50%). It is not a harvest/recross edge — consistent with WS7-A (no level-reversal structure beyond a random walk at 1–8%).
2. **D3/k1:** lower exposure (beta −0.67 pp) helps in falling years (2018 +2.4, 2022 +5.4 pp; MaxDD −1.7/−6.1 pp) and hurts in 2020 (−2.4 pp); timing 48% → **inventory/risk geometry, not harvest alpha** — confirms the WS5 synthetic conclusion on real data.
3. Realized CF alone would mislead: D0/k1.5 has higher CF in most windows only because it pays less fee per unit harvested; D3's wins come from holding less inventory.

## 3. Status against the AIGR hypothesis ledger (Discovery evidence, independent engine)

| hypothesis | WS7-B |
|---|---|
| Basic Grid sufficient | **consistent** — no challenger shows a timing advantage |
| D0/k1.5 harvest advantage | **not supported** — advantage = lower fees, timing ≈ 0 |
| D3 = inventory/risk geometry | **supported** on real data |
| grid-lattice/recross mechanism with economic magnitude in BTC | **not supported** (with WS7-A) |

## 4. Limitations

- Independent engine, not the frozen 56/56 engine — must be reconciled before any claim (see §5)
- Envelope rule is this runner's choice; the frozen addendum's rule may differ and would change the level of results (not necessarily the Δ between candidates)
- timing uses ex-post ē (biased upward under a martingale) — read Δ timing between candidates, not the level
- hurdle 0; 3 informative years; rolling windows overlap; one asset; Discovery data already inspected

## 5. Next

1. **Reconcile engines:** upload the synthetic A/B/C 1m files → reproduce the audited D0/k1 terminal numbers (A: equity 13,041.98; B: 15,751.49; C: 17,081.19) with `engine_1m.py`; then run the frozen engine on the real data and diff the ledgers
2. Replace the envelope rule with the frozen addendum's rule and rerun (21 s)
3. Pre-OOS packet: given the effect sizes (≤ ~1 pp/yr for k1.5, driven by fees), the sealed 2024+ period can only detect gross failure — declare this before opening it
