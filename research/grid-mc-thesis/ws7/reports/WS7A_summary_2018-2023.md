# WS7-A scale structure — data/canonical

- span: 2018-01-01 → 2023-12-31 (6.00 y), points: 3,146,975
- data sha256: `9d854236c9bf9a4fbfc698c11d3a52142e0040c49bbfded7e54e2281fc681676`
- trailing envelope depth 60% below running max; fee/side 0.100%; surrogates per kind 50; seed 20260925

## Grid statistics, all data (% of B per year)

| δ % | N | ē | cycles/yr | fee drag | gross | timing | net timing | sawtooth | z gross / timing / sawtooth (signflip) | z gross / timing / sawtooth (volshuffle) | z gross / timing / sawtooth (iid) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.25 | 366 | 0.71 | 17080 | 9.34 | +9.51 | -3.86 | -13.20 | -13.21 | +0.6 / +0.1 / -0.4 | +0.5 / +0.4 / +0.2 | +0.3 / +0.0 / -0.2 |
| 0.5 | 183 | 0.71 | 5358 | 5.86 | +12.49 | -0.87 | -6.73 | -10.23 | +0.6 / +0.1 / -0.6 | +0.4 / +0.4 / +0.1 | +0.2 / -0.1 / -0.6 |
| 1.0 | 91 | 0.71 | 1559 | 3.44 | +15.00 | +1.61 | -1.83 | -7.73 | +0.5 / +0.1 / -1.0 | +0.3 / +0.3 / -0.2 | +0.1 / -0.1 / -1.5 |
| 2.0 | 45 | 0.71 | 434 | 1.94 | +17.17 | +3.78 | +1.85 | -5.56 | +0.5 / +0.1 / -1.5 | +0.3 / +0.2 / -0.7 | +0.1 / -0.1 / -3.0 |
| 4.0 | 22 | 0.71 | 113 | 1.04 | +18.68 | +5.37 | +4.34 | -4.05 | +0.5 / +0.1 / -2.1 | +0.3 / +0.2 / -1.3 | +0.1 / -0.1 / -4.3 |
| 8.0 | 11 | 0.69 | 29 | 0.54 | +19.62 | +6.58 | +6.04 | -3.11 | +0.5 / +0.1 / -1.7 | +0.2 / +0.2 / -1.2 | +0.1 / -0.1 / -1.9 |

## Lattice reversal probability, all data (0.5 = martingale)

| δ % | steps | p_rev | p(up after down) | z p_rev (signflip) / surr mean | z p_rev (volshuffle) / surr mean | z p_rev (iid) / surr mean |
|---|---|---|---|---|---|---|
| 0.25 | 272,454 | 0.3695 | 0.3701 | +18.6 / 0.3531 | +26.7 / 0.3442 | +22.0 / 0.3495 |
| 0.5 | 85,993 | 0.4119 | 0.4130 | +7.1 / 0.4009 | +12.4 / 0.3926 | +7.5 / 0.4008 |
| 1.0 | 25,415 | 0.4372 | 0.4392 | +0.3 / 0.4366 | +3.0 / 0.4289 | -0.6 / 0.4390 |
| 2.0 | 7,199 | 0.4600 | 0.4637 | -0.1 / 0.4606 | +0.6 / 0.4562 | -0.9 / 0.4654 |
| 4.0 | 1,924 | 0.4805 | 0.4879 | +0.4 / 0.4766 | +0.8 / 0.4717 | -0.1 / 0.4812 |
| 8.0 | 510 | 0.4951 | 0.5081 | +0.4 / 0.4874 | +0.6 / 0.4848 | +0.2 / 0.4917 |

## Stability by year — p_rev z vs signflip surrogates

| year | δ 0.25% | δ 0.5% | δ 1.0% | δ 2.0% | δ 4.0% | δ 8.0% |
|---|---|---|---|---|---|---|
| 2018 | +15.7 | +5.6 | +1.2 | +1.2 | -0.4 | +0.7 |
| 2019 | +9.1 | +4.3 | -0.2 | -1.4 | -0.5 | -0.7 |
| 2020 | +9.2 | -0.4 | -0.5 | -0.5 | -0.5 | +0.8 |
| 2021 | +6.8 | +4.6 | +0.1 | +0.0 | +1.1 | +0.0 |
| 2022 | +1.4 | +0.2 | -0.4 | -0.5 | +1.0 | +1.0 |
| 2023 | +3.1 | +0.5 | -1.0 | +0.1 | +0.8 | -1.4 |

## Variance ratio

| horizon | VR real | VR signflip (pctile) | VR volshuffle (pctile) | VR iid (pctile) |
|---|---|---|---|---|
| 5m | 0.965 | 1.001 (0.00) | 1.000 (0.00) | 1.000 (0.00) |
| 15m | 0.918 | 1.002 (0.00) | 0.999 (0.00) | 1.000 (0.00) |
| 1h | 0.877 | 1.004 (0.00) | 0.998 (0.00) | 0.999 (0.00) |
| 4h | 0.813 | 1.006 (0.00) | 0.995 (0.00) | 0.998 (0.00) |
| 1d | 0.822 | 1.006 (0.00) | 0.988 (0.00) | 0.993 (0.00) |
| 3d | 0.790 | 0.997 (0.00) | 0.987 (0.00) | 0.992 (0.00) |
| 7d | 0.827 | 0.999 (0.08) | 0.990 (0.06) | 0.987 (0.00) |

Reading: p_rev z ≫ 0 at spacing δ → price reverses between adjacent levels more often than on sign-random paths with the same moves: the structure a grid at that spacing harvests. z = (real − surrogate mean) / surrogate sd. gross z ≫ 0 → the grid earns more on the real path than on paths with the same moves but random signs (harvestable mean reversion); sawtooth z ≫ 0 → the lattice at spacing δ adds harvest beyond the smooth envelope exposure. timing uses the ex-post mean exposure ē, which is biased upward even under a martingale (ē and Σr are negatively correlated) — compare it with surrogates, never with 0. Net timing subtracts fees only (no hurdle). Process statistic, not a backtest.
