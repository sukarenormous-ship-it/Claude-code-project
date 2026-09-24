# Basic-Anchored Monte Carlo Capital Grid

## Complete Research & Implementation Handoff v1.0

**Date:** 2026-09-23\
**Status:** Architecture, red-team, Study 0, and M0--M2 specification
complete.\
**Next:** BTC/ETH Spot data → M0 → M1 → M2 → GO / CONDITIONAL GO /
STOP.\
**Freeze:** do not add Regime, Orderflow, ML/RL, or dynamic sizing
before M0--M2 review.

## 1. Thesis

Build a **spot, buy-only, fully-funded bounded grid**. MC is not
primarily a price predictor.

> With finite capital inside a deliberately wide funded price range, can
> capital be allocated more productively than a strong Basic Grid
> without materially worsening downside, inventory burden, or capital
> lock?

MC is a candidate estimator only. If rolling empirical estimates are as
good or better, remove MC.

## 2. Core contract

Define `B` total capital, `R` structural reserve, `N` slots, hard range
`[L,U]`, deployable capital `B_D=B-R`, and V1 equal slot capital
`b=B_D/N`.

Hard rules: - Spot only; no leverage, borrowing, martingale, or silent
capital injection. - MC cannot expand `[L,U]`, create capital, erase
inventory, or reduce structural reserve. - Inventory persists through
replans and remains mark-to-market. - Outside `[L,U]`: stop new entries;
continue existing exits.

`[L,U]` is the **Structural Survival Envelope**.

Mechanical survival is not economic survival. Main risks are
**Drawdown + Inventory Risk + Capital Lock**. Crypto rapid moves mainly
create **rapid inventory conversion**.

**Grid Crossing != Fill.**

## 3. Basic Grid = Baseline + Prior + Fallback

Let `G0=G_Basic`. Adaptive allocation proposes `G_A=G0+DeltaG`.

Weak evidence → `DeltaG→0` → return toward Basic.

Strong Basic comparators: 1. Arithmetic spacing. 2. Log/percentage
spacing. 3. Predefined Basic + MA entry gate.

Desired behavior: - useful information: Adaptive \> Basic; - weak/wrong
information: Adaptive must not be materially worse than Basic beyond
predefined economic tolerances.

Evaluate Net Equity, MaxDD, tail loss, CapitalLock×Time, inventory age,
terminal inventory, and time-under-water---not return alone.

## 4. Direction is not the core target

Grid economics are mainly **Downward Excursion → Recovery**. The hostile
process is **persistent non-recovering downside**, not simply "Bear".

Directional/regime information may later be a risk feature, but is not
required in V1.

------------------------------------------------------------------------

# Study 0 --- Real Crypto Path Anatomy

## 5. Scope and data

Start BTC Spot and ETH Spot separately.

Preferred: - 1h research/planning clock; - 1m or reliable 5m
event/execution reconstruction; - UTC; - provenance/checksum/coverage
manifest.

Study 0 asks: 1. Do recoverable grid opportunities exist after
executable costs? 2. Are hit--recovery--capital-lock economics
heterogeneous by entry depth? 3. Is the structure stable over time? 4.
Is Basic allocation inefficient? 5. Is rolling empirical estimation
sufficient? 6. Does MC add information?

Manifest fields:

``` text
dataset_id, venue, market_type, symbol, base_asset, quote_asset,
timeframe, start_time_utc, end_time_utc, row_count, expected_rows,
missing_rows, duplicate_rows, source, download_time, checksum,
price_tick, qty_step, min_notional, fee_assumption_id
```

Canonical OHLCV:

``` text
venue, market_type, symbol, timeframe, timestamp_open, timestamp_close,
open, high, low, close, volume, source, data_quality_flag
```

Do not blindly remove extreme observations; distinguish bad data from
real tails.

## 6. M0 --- Data Integrity

Audit timestamp ordering, duplicates, missing intervals, OHLC
consistency, positive prices, nonnegative volume, source
discontinuities, and cross-timeframe reconciliation.

For 1h aggregated from 1m: first open, max high, min low, last close
must reconcile.

Dataset status: `PASS / CONDITIONAL / FAIL`. M1 cannot use FAIL data.

**M0 DoD:** manifest complete; reproducible DQ audit; missing/duplicates
audited; timeframe reconciliation; extreme events verified; input hashes
recorded.

## 7. Event definition and re-arm

For reference `S0` and depth `d`, level `g=S0*(1-d)`.

Downward cross = price moves from above g to at/below g. Crossing is not
automatically a fill.

Event schema:

``` text
event_id, symbol, reference_time, reference_price, depth_pct, grid_price,
cross_time, cross_price, order_live_before_cross, fill_status, fill_time,
fill_price, fill_assumption, rearm_required_price, tp_floor, data_quality_flag
```

State machine:
`ARMED → TRIGGERED → FOLLOWING → RECOVERED/CENSORED → WAIT_REARM → ARMED`

New opportunity requires price above `g*(1+r_rearm)` and a new downward
crossing.

Report dense eligible observations for description and
de-overlapped/re-armed episodes for uncertainty inference.

## 8. Recovery / first passage

After fill `P_e`, target return q gives `P_TP=P_e*(1+q)`.

`tau` = first time after entry that price reaches TP.

If not reached before observation ends: **right-censored**. Do not
delete it, set tau=horizon, or call permanent failure.

Predefined horizons: `6h, 12h, 24h, 72h, 7d, 30d`, plus longer follow-up
where available.

Recovery surface: `R(d,q,h)=P(TP_q reached within h | entry at depth d)`

Also estimate the full time-to-TP survival curve.

## 9. MFE / MAE / Capital Lock

Measure MFE and MAE only until exit or observation horizon.
`MAE_before_TP` is critical. Report MAE conditional on TP and no-TP
separately.

`CL_j = Capital_j * HoldingTime_j`

`CL_total = sum(CL_j)`

`CLI = CL_total/(B*T)`

Capital Lock is a primary economic metric.

## 10. Drawdown / rapid-move anatomy

Drawdown fields:

``` text
episode_id, peak_time, peak_price, trough_time, trough_price, depth_pct,
time_to_bottom, recovery_time, total_underwater_time, recovered,
right_censored, max_1h_drop, max_4h_drop, max_24h_drop
```

Study crash→fast recovery, slow recovery, stagnation, and continuation
separately.

Crossing velocity: `V_G = number of grid levels crossed / time`

Rapid-move fields:

``` text
event_id, start_time, end_time, return_1m, return_5m, return_1h,
levels_crossed, crossing_velocity, rebound_1h, rebound_6h,
rebound_24h, rebound_72h
```

These later inform structural reserve and stress tests.

## 11. Empirical Capital Landscape B_E

For each depth d and TP q retain a vector: - P(Hit) - P(TP\<=24h \|
Hit) - P(TP\<=72h \| Hit) - median and Q90 recovery time - median and
Q95 MAE - Capital Lock - Net PnL - sample support n - uncertainty
interval - censoring/DQ status

Do **not** collapse M2 into an arbitrary scalar score.

Low support → `InsufficientEvidence`, not forced 0%/100%.

Construct landscapes by predefined time blocks/rolling windows; do not
immediately pool all years. BTC and ETH remain separate experiments.

Possible outcomes: - flat → Basic likely sufficient; - structured +
stable → Empirical-C promising; - structured + time-varying → rolling
estimator/MC may help; - unstable/noisy OOS → return to Basic.

------------------------------------------------------------------------

# Execution & Accounting Contract

## 12. TP economic floor

Hard constraint: **TP\* \>= TP_floor**.

Floor includes buy fee, sell fee, spread, slippage, tick/quantity
rounding, and minimum required net profit, based on actual fill.

No feasible profitable TP → **No Trade**.

No adaptive model can override this.

Adaptive TP is tested only after geometry passes; use
MFE/first-passage/recovery information. ATR/realized volatility remain
comparators/features.

## 13. Event-driven engine

Required sequence:
`MarketData → Crossing → Eligibility → Fill → Position → Exit → Ledger`

Forbidden shortcuts: - `Low<Grid => Buy@Grid` - `High>TP => Profit`
without ordering/execution logic.

Separate pre-positioned limit orders from reactive
`Cross→Decision→Submit→Fill`.

Execution modes: - E1 conservative bar execution when only OHLC
exists; - E2 fine-resolution 1m/5m reconstruction for ambiguous coarse
bars.

E2 preferred where data permits.

## 14. Cost engine and invariants

Costs live outside strategy logic and return fee, spread cost, slippage,
rounding loss, and net execution price.

Invariants: - Cash \>= 0. - Qty sold \<= Qty owned. - Equity = Cash +
Inventory market value. - Inventory persists through replans. - Slot
ownership explicit.

Invariant failure = **Backtest Invalid**.

Position ledger: planned/actual entry, qty/notional, TP, actual exit,
fees/slippage, net PnL, holding time, MAE/MFE, status.

Portfolio ledger: cash, inventory value, equity, positions/slots,
capital locked, reserve, realized/unrealized PnL, drawdown.

## 15. M1 --- Golden tests

Must pass 100%: 1. simple buy→TP; 2. buy→no recovery; 3. buy→deep
MAE→TP; 4. jump through multiple grids; 5. re-arm; 6. repeated
oscillation; 7. dataset-end censoring; 8. intrabar ambiguity; 9. gross
TP but net loss after costs; 10. inventory persistence; 11. insufficient
cash; 12. reserve binding; 13. duplicate-event protection; 14.
pre-positioned vs reactive fill; 15. partial fill/exit if supported; 16.
fee currency handling if relevant; 17. tick/quantity rounding; 18. same
input+config → same output.

**M1 DoD:** all pass; ledger reconciles; crossing/fill separated;
re-arm/censoring correct; ambiguity handled; TP floor enforced;
deterministic reproducibility.

## 16. M2 --- Path Anatomy

M2 is descriptive: **no optimizer and no MC**.

-   M2-A Downside Excursion
-   M2-B Recovery
-   M2-C Path Risk (MFE/MAE/MAE-before-TP)
-   M2-D Capital Lock
-   M2-E Crash/Rapid Move

Predeclared outputs: 1. Recovery Probability Surface 2. Recovery
Survival Curves 3. Q90 Capital-Lock Surface 4. Q95 MAE Surface 5.
Drawdown Depth × Recovery Duration 6. Rapid Crossing / Jump Distribution
7. Sample-Support Surface

**M2 DoD:** BTC/ETH reports, uncertainty/censoring, MAE/MFE, capital
lock, rapid moves, drawdowns, temporal stability, support map; no
optimizer/MC.

Decision: **GO / CONDITIONAL GO / STOP**.

------------------------------------------------------------------------

# Adaptive Research Ladder

## 17. Strong Basic benchmark

After M2: - B0 Arithmetic Basic - B1 Log Basic - B2 Basic + predefined
MA gate

MA gate: `Price < MA => skip new entry`. When price returns above MA, do
not batch-buy skipped crossings; only future re-armed crossings are
eligible.

All comparators share capital, range, slots, TP, costs, execution,
re-arm, and accounting when geometry is tested.

## 18. Rolling Empirical estimator / Empirical-C

Before MC: `B_Emp,t = f(history available through t)`

Freeze before future outcomes.

If heterogeneity is useful: `G_E = G_Basic + DeltaG_E`

Prefer region-level allocation over exact noisy point optimization.

Constraints: - downside gate; - structural stress gate; - distance
penalty from Basic; - concentration/minimum-spacing; - uncertainty
shrinkage.

Insufficient evidence → `G_E=G_Basic`.

## 19. MC admission

MC estimates decision-relevant distributions, not exact prices: -
P(Hit) - P(Recovery\|Hit) - recovery-time distribution - MFE/MAE -
Capital Lock - tail excursion

MC must beat or complement Rolling Empirical on: - calibration; -
discrimination; - distribution/quantile calibration; - seed/model
stability; - economic relevance.

No added decision value → **Reject MC** and continue with Empirical-C.

If MC is used, split `MC_train` and unseen `MC_validation` before
optimization. Historical walk-forward/OOS remains mandatory.

## 20. Allocator C

`G_C = G_Basic + DeltaG`

Evaluate the **whole portfolio**, not independent top-scoring levels.

Paired comparison on identical paths:
`Delta_j = Outcome(G_C,path_j) - Outcome(G_Basic,path_j)`

Penalize distance from Basic; larger tilts require stronger evidence.
Enforce minimum spacing and concentration constraints.

## 21. Downside & stress gates

Predefine tolerances for: - MaxDD - tail loss - Capital Lock - inventory
age - terminal inventory - net equity

Do not retrospectively call periods where adaptive wins "good regime".

Independent structural stress families: - rapid move through multiple
grids; - sharp drop; - drop + continuation; - crash + prolonged
stagnation; - crash + rebound; - repeated shocks.

Stress magnitudes come from Study 0 + risk policy and are frozen before
comparison.

**MC proposes; risk constraints dispose.**

## 22. Tail Reserve

Let K = additional slots potentially hit before recovery.

Model reserve may use a predefined quantile of K, but:
`R_t = max(R_structural, R_model)`

The model can never reduce reserve below structural floor.

## 23. Entry Governor

At a valid crossing compare: - A0 = keep cash - A1 = buy

Evaluate incremental economic value, tail risk, and Capital Lock from
current portfolio state.

BUY only if: - TP economically viable; - incremental value passes; -
downside gate passes; - cash after buy \>= required reserve.

Otherwise **SKIP**.

**No backlog:** skipped crossings are not batch-bought later. Re-arm and
a new valid crossing are required.

## 24. Uncertainty Governor

Adaptive intensity `w` lies in \[0,1\]:
`G_t = G_Basic + w_t * DeltaG_raw`

Increase w only with adequate sample support, calibration, stability,
and train-validation consistency. Weak evidence → w→0 → Basic.

Applies to Empirical-C and MC-C.

## 25. Adaptive TP

Only after geometry/governor/reserve pass.

Search TP only above economic floor using MFE, recovery, and
first-passage distributions.

Compare fixed TP vs adaptive TP while holding geometry constant.

Success = improved **net capital productivity**, not merely more TP
hits.

------------------------------------------------------------------------

# Model-Risk Firewall / Red-Team

## 26. Structural risks

1.  Crossing ≠ fill, especially rapid moves.
2.  Wide range prevents liquidation, not long capital immobilization.
3.  Probability estimates create false precision; report uncertainty.
4.  Deep grids have low support; require minimum evidence.
5.  Optimizers can overfit MC noise; train/validation split required.
6.  Downside cannot be judged only by MC; independent stress set
    required.
7.  Model tail reserve can be too low; structural reserve is hard floor.
8.  Adaptive TP can confound geometry; test sequentially.
9.  "Good/bad regime" cannot be defined from adaptive performance after
    the fact.
10. Basic comparator must be strong and share identical
    execution/accounting assumptions.

## 27. Falsification criteria

Reject the relevant module if: - adaptive allocation does not improve
capital productivity after costs; - gains require materially worse
downside; - results disappear under modest lookback/block/seed
sensitivity; - Basic+MA matches/beats the complex governor; - MC
calibration is no better than Rolling Empirical; - better MC forecasts
do not produce better allocation; - Governor only reduces DD by
suppressing activity beyond tolerance; - Adaptive TP increases hits but
not net capital productivity.

A negative result is valid research.

------------------------------------------------------------------------

# Parameter Governance

## 28. Parameter classes

### Structural / policy

`B`, `[L,U]`, `N`, structural reserve, TP floor/minimum net profit,
downside tolerances, reserve confidence level, hard stress policy.

Do **not** optimize these for backtest PnL.

### Model / sensitivity

Empirical/MC lookback, block length, simulation horizon, path count,
candidate resolution.

Choose from economic/data rationale and sensitivity---not best PnL.

### Estimated

Landscape, model tail reserve, grid tilt, uncertainty weight, later
adaptive TP.

### Execution

Re-arm, replan cadence, fill/cost assumptions.

Predefine or sensitivity-test; never silently tune on final results.

## 29. Timescale separation

-   slow estimator/MC → geometry;
-   faster Entry Governor → deployment;
-   later very-fast Orderflow → execution timing.

Fast polling must not repeatedly move structural grid geometry.

------------------------------------------------------------------------

# Research Sequence

## 30. Final ladder

**S0** Crypto Path Anatomy\
**S1** Empirical-B\
**S2** Strong Basic Benchmark\
**S3** Rolling Empirical Forecast\
**S4** MC Admission\
**S5** Basic-Anchored C\
**S6** Entry Governor\
**S7** Tail Reserve\
**S8** Adaptive TP\
**S9** Conditional/Regime MC only if evidence supports it\
**S10** Orderflow execution only after structural edge passes

Core experimental arms:

  Arm   Geometry           Entry control   Reserve                   TP
  ----- ------------------ --------------- ------------------------- ----------
  A0    Arithmetic Basic   none            structural                fixed
  A1    Log Basic          none            structural                fixed
  A2    predefined Basic   MA              structural                fixed
  B0    Empirical-C        none            structural                fixed
  B1    MC-C               none            structural                fixed
  C0    best validated C   Governor        structural                fixed
  C1    best validated C   Governor        structural + model tail   fixed
  D0    best validated C   Governor        tail reserve              adaptive

"Best validated" means selected only through the predefined
development/validation protocol, never final-test PnL.

## 31. Complexity budget

Each module must prove a specific incremental value: - Empirical-C →
allocation value - MC → forecast/calibration value - Governor →
deployment/risk value - Tail Reserve → crash robustness - Adaptive TP →
exit/capital-turnover value - Regime → conditional-distribution value -
Orderflow → execution-timing value

No demonstrated value → remove module.

------------------------------------------------------------------------

# Software Boundary

## 32. Suggested modules

``` text
market_data/
event_engine/
execution/
ledger/

landscape/
    empirical_estimator
    mc_estimator
    uncertainty

allocation/
    basic
    constrained_tilt
    shrinkage

runtime/
    governor
    reserve

exit/
    tp_floor
    fixed_tp
    adaptive_tp

validation/
    golden_cases
    calibration
    stress
    walk_forward
```

Critical interface:

`LandscapeEstimator -> Landscape + Uncertainty -> Allocator`

MC is a plugin, not the foundation.

## 33. Milestones

**M0 Data integrity** → BTC/ETH data + manifest + DQ.\
**M1 Event correctness** → golden cases 100%.\
**M2 Market anatomy** → empirical surfaces.\
**M3 Basic benchmark** → Arithmetic/Log/MA.\
**M4 Empirical-C** → test adaptive allocation without MC.\
**M5 MC admission** → MC must beat/complement empirical estimator.\
**M6 MC-C** → incremental allocation value.\
**M7 Governor + Tail Reserve**.\
**M8 Adaptive TP**.\
**M9 Final untouched confirmation**.\
Only then open Regime/Orderflow parking lot.

------------------------------------------------------------------------

# Current Evidence / Data Gate

## 34. What is already known

Prior repository work inspected the Grid-bot snapshot and existing
MC/grid/TP/orderflow/replay code. Existing research established useful
software scaffolding and highlighted execution/accounting gaps.

The earlier 6-mode experiment used Binance USD-M perpetual 4h prices
treated as a cash account, without historical orderflow. It is **not**
the target Bybit/spot 1h/1m Study-0 dataset and must not be presented as
proof of the new thesis.

Earlier MC-Recovery work also demonstrated that high recovery of many
lots can coexist with severe portfolio drawdown. Therefore recovery rate
alone is not a sufficient success metric.

The previously inspected repository snapshot did not expose the required
long BTC/ETH Spot OHLCV + fine-resolution data for Study 0. Do not
manufacture M2 results from an unsuitable proxy.

## 35. Immediate next work

1.  Acquire/import BTC and ETH Spot historical 1m (or reliable 5m) data
    with provenance.
2.  Generate/verify 1h research bars from the same source where
    possible.
3.  Run M0 data-quality audit.
4.  Implement event engine and golden synthetic cases.
5.  Pass M1 at 100%.
6.  Run M2 Path Anatomy.
7.  Build `B_E`.
8.  Review GO / CONDITIONAL GO / STOP **before** implementing optimizer
    or MC.
9.  If GO, build strong Basic benchmark and Rolling Empirical estimator.
10. Only then run MC Admission.

------------------------------------------------------------------------

# Final Strategy Hypothesis

> In spot crypto using fully-funded capital inside a deliberately wide
> funded price envelope, hit--recovery--capital-lock economics may
> differ systematically across price/depth regions. A robust Basic Grid
> should serve as the prior and fallback. Capital should be tilted away
> from Basic only when empirical or Monte Carlo evidence supports
> improved capital productivity without materially worse downside. Monte
> Carlo is admitted only if it improves decision-relevant distribution
> estimates over simpler rolling empirical methods. Structural safety,
> reserve floors, TP economic floors, accounting invariants, and
> deterministic stress tests always override adaptive-model preferences.

**Operational philosophy:**\
**Wide funded range = survival. Basic = robust prior. Empirical/MC
landscape = information. C = allocation. Governor/reserve = deployment
control. TP floor = economic validity. MC proposes; risk constraints
dispose.**
