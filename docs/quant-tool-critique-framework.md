# Quant Tool Critique & Research Framework

## Team Handoff --- English Working Specification

**Status:** Framework v1.0 (user's original) + v1.1 notes from the "คิดแบบ Quant" appendix E review (see bottom)\
**Purpose:** A shared framework for studying, critiquing, implementing,
and validating quantitative indicators, statistical models, features,
and trading strategies.

> ใช้ร่วมกับ `docs/nq-appendix-indicators.html` (ภาคผนวก E) — ภาคผนวกคือ Gate 1 ของกรอบนี้ทั้งชิ้น
> และหัวข้อ "จากการ์ดสู่งานวิจัย — สี่ประตู" ท้ายภาคผนวกแมปเนื้อหาในคลังเข้ากับ Gate 2–4

## 1. Core Principle

A quantitative tool should never be treated as a trading rule merely
because it produces a number.

**Market Reality → Data → Representation → Feature/Model → Forecast →
Signal → Position → Execution → PnL**

Every arrow introduces assumptions. Every transformation preserves some
information and discards some information.

Keep four distinctions explicit:

-   **Measurement ≠ Prediction**
-   **Prediction ≠ Signal**
-   **Signal ≠ Position**
-   **Statistical Edge ≠ Economic Edge**

The central question is not *"Does this tool work?"* It is:

> **Under what market state, horizon, information set, assumptions, and
> trading costs does this representation add stable, incremental,
> economically usable information?**

------------------------------------------------------------------------

## 2. The Eight-Question Framework

**WHY → WHAT → HOW → LOSE → ASSUME → PREDICT → SURVIVE → PAY**

For every stage use four modes: **intuition → technical meaning →
counterexample → quant consequence**.

### WHY --- What problem was the tool designed to solve?

Ask what phenomenon or latent quantity it was intended to measure before
asking how to trade it. Record origin, original market/timeframe,
intended use, and the source of conventional parameters. A legacy
convention is not a law of nature. Classify cutoffs as mathematical,
statistical, empirically calibrated, conventional, or heuristic.

Examples: RSI measures smoothed directional gain/loss imbalance; ATR
measures recent movement magnitude; regression estimates a conditional
linear relationship; PCA extracts dominant variance directions;
cointegration seeks a stable long-run combination of non-stationary
series.

### WHAT --- What information can it see?

Document the information set available at decision time and, equally
importantly, what is invisible. RSI based on closes does not directly
observe the intrabar path. A BTC--ETH regression does not automatically
know funding, OI, liquidity, or omitted factors.

> **A model cannot directly recover information it never receives.**

### HOW --- How is information transformed?

Decompose the entire pipeline rather than memorizing the final formula.

RSI:
`Price → Change → Gain/Loss → Wilder smoothing → Ratio → bounded nonlinear transform`.

OLS:
`X,Y → linear projection → residuals → squared loss → coefficients`.

Inspect differencing, logs, ratios, ranks, smoothing, weighting,
normalization, clipping, nonlinear transforms, loss functions, rolling
windows, and recursive updating. A formula encodes decisions about which
observations and errors matter more.

### LOSE --- What information is destroyed?

Every feature is lossy compression.

> **Feature = information retained + information discarded**

RSI retains directional imbalance but loses much of absolute volatility,
path, jump timing, volume, and factor attribution. A regression slope
hides nonlinear, tail, and regime-specific structure. PCA preserves
high-variance directions, not necessarily predictive information.

**Mandatory counterexample:** construct two materially different
data-generating states that produce the same output.

> **Same output ≠ same underlying state.**

### ASSUME --- What must be approximately true?

Do not merely list assumptions. Ask: *If this assumption fails, which
interpretation or inference becomes unreliable?*

For regression consider conditional-mean specification, exogeneity,
autocorrelation, heteroskedasticity, heavy tails, jumps,
non-stationarity, structural breaks, time-varying coefficients, and
omitted factors.

Memory is also an assumption: SMA uses a finite rectangular kernel; EMA
exponential decay; Wilder slower exponential decay; rolling OLS a hard
window; EWLS exponential weights; Kalman an evolving latent state.

> **Nominal parameter ≠ effective memory.**

Recursive features also require initialization and warm-up. Warm-up is
not effective lookback.

> **Same current value ≠ same historical path.**

------------------------------------------------------------------------

### PREDICT --- Why should today's measurement contain future information?

This is where measurement becomes a research hypothesis. Specify an
explicit predictor, target, and horizon: `X_t ?→ Y_(t+h)`.

Competing hypotheses are mandatory. RSI \< 30 may imply mean reversion
or downside continuation. A large residual may be temporary dislocation,
new information, or model misspecification.

Study the conditional distribution, not only the mean: median, hit rate,
quantiles, tail losses, MAE, MFE, time to convergence, and
holding-period distribution.

Evaluate **incremental** information: a feature may predict in isolation
yet add nothing after existing features are known.

### SURVIVE --- Is the relationship robust?

Seek relationships that are difficult to destroy, not parameters that
maximize historical performance.

Test across time, assets, regimes, volatility states, parameter choices,
model specifications, cost assumptions, outlier treatments, and training
windows. Use chronological OOS, walk-forward evaluation, leakage audits,
purging/embargo when labels overlap, structural-break diagnostics,
multiple-testing control, and parameter-sensitivity surfaces.

> **Stable parameter region \> isolated best parameter**

Also test conditional effects such as `E[Y | X, Regime]`; pooling
regimes can erase a genuine effect or reverse its sign.

### PAY --- Can it be monetized?

A statistically real effect can still be economically useless.

`Net Edge = Gross Edge - Fees - Spread - Slippage - Funding - Market Impact - Other Frictions`

Include turnover, liquidity, capacity, latency, leverage, margin, short
constraints, drawdown, tail risk, and convergence time.

> **Best statistical signal ≠ best implementable signal.**

> **Eventually correct ≠ tradably correct.**

------------------------------------------------------------------------

## 3. Cross-Cutting Concepts

### Measurement → Forecast → Signal → Position

Keep these separate in both reasoning and code.

-   **Measurement:** e.g. RSI = 25; residual = -2σ.
-   **Forecast:** expected future target conditional on current
    information.
-   **Signal:** a decision-oriented transformation such as a rank or
    risk-adjusted forecast.
-   **Position:** allocation after volatility, covariance, liquidity,
    and risk constraints.

### Feature Quality Is Not Alpha Quality

A feature can be stationary, normalized, high-entropy, and robust to
outliers while having zero predictive value. White noise is the
canonical counterexample.

> **Statistically well behaved ≠ predictive ≠ tradable.**

### Entropy vs Predictive Information

High marginal entropy means a feature varies; it does not mean the
variation predicts the target. Ask whether the feature reduces
uncertainty about the target and whether it adds information beyond
existing features.

### Stationarity and Concept Drift

Distinguish mean shift, variance shift, distribution shift, structural
break, and predictive-relationship shift. The last is especially
important: the mapping from feature to future target can change even if
the feature distribution appears stable.

Rolling z-scoring does not guarantee stationarity. Differencing can
improve stationarity while destroying long-run information. Transform
data to serve the research question, not merely to obtain a favorable
statistical test.

### Effective Information

**Number of rows ≠ number of independent information units.**
Autocorrelation, smoothing, overlapping labels, and common factors
reduce effective information.

------------------------------------------------------------------------

## 4. Regression Extension

### Simple Regression

`Y = alpha + beta X + epsilon`

For simple OLS with an intercept:

`beta = Cov(X,Y) / Var(X) = Corr(X,Y) × sigma_Y / sigma_X`

Beta therefore combines co-movement and relative scale. The same beta
can arise from different underlying relationships.

A residual is **deviation from the fitted model**. It is not
automatically mispricing, alpha, or mean reversion. R² is in-sample fit
quality, not prediction accuracy. Contemporaneous explanation
(`Y_t ~ X_t`) is not forecasting (`Y_(t+1) ~ X_t`).

### Multiple Regression

`Y = beta_0 + beta_1 X_1 + ... + beta_k X_k + epsilon`

A coefficient is conditional on the other included regressors.
Additional issues include multicollinearity, omitted-variable bias,
coefficient instability, interactions, dimensionality, regularization,
and incremental OOS value.

Too few variables can omit important structure; too many can create
variance and overfitting. Ridge/Lasso trade bias for variance/complexity
control; they do not establish causality.

### Time-Series Regression and Cointegration

Unrelated non-stationary series can produce high R² and apparently
significant coefficients: spurious regression. Differencing/log returns
often improves stationarity but removes long-run level information.

Cointegration is the special case where individually non-stationary
series have a stationary linear combination. It is evidence of a
long-run statistical constraint, not proof of a profitable trade.
Adjustment speed, half-life, beta stability, structural breaks, costs,
and economic mechanism still require validation.

ADF/KPSS are diagnostics, not trading signals. `ADF p < 0.05` does not
mean "95% probability the spread will revert."

------------------------------------------------------------------------

## 5. Crypto Statistical-Arbitrage Application

Crypto assets share strong common-factor structure. Pairwise
relationships should therefore not automatically be interpreted as
independent relative-value relationships.

Baseline factor model:

`r_(i,t) = alpha_i + beta_i F_t + epsilon_(i,t)`

`F_t` may be BTC return, a broad crypto index, PCA factors, or a
multi-factor representation.

Residualization changes the question from *"How much did the coin
move?"* to *"How much did it move relative to what the chosen common
factors explain?"* Residuals are model-relative, not pure idiosyncratic
truth.

Candidate hypotheses include residual reversal, residual momentum,
funding crowding, OI shock, liquidity shock, and volatility/regime
interactions.

Preferred architecture:

**Raw Data → Returns → Common-Factor Estimation → Residualization →
Residual Characterization → Competing Alpha Hypotheses → OOS Validation
→ Portfolio Construction → Execution/Cost Model**

Do not begin by scanning every pair and selecting the smallest p-value.
This invites common-factor contamination, multiple testing, and
selection bias.

------------------------------------------------------------------------

## 6. Standard Team Research Template

For every new indicator, feature, model, or paper, produce:

### A. Origin & Intent

Origin; problem addressed; original market/timeframe/context; source of
conventional parameters.

### B. Mathematical Anatomy

Inputs; full transformation pipeline; weighting/memory;
initialization/warm-up; normalization/scale; objective/loss.

### C. Information Audit

Information retained; information discarded; blind spots; path
dependence; at least one same-output/different-state counterexample.

### D. Assumption Audit

Structural, statistical, and time-series assumptions; expected failure
mode when each assumption breaks.

### E. Predictive Hypothesis

Explicit target and horizon; mechanism; null hypothesis; competing
hypothesis.

### F. Empirical Characterization

Conditional distributions; mean/median/quantiles; hit rate; MAE/MFE;
signal decay; regime conditioning; incremental information.

### G. Robustness

Chronological OOS; walk-forward; leakage audit; multiple-testing
control; parameter plateau; asset/regime/timeframe stability; structural
breaks.

### H. Economic Validation

Fees; spread; slippage; funding; turnover; latency; capacity; liquidity;
leverage/margin; tail risk; covariance; net PnL.

------------------------------------------------------------------------

## 7. Acceptance Gates

1.  **Meaning:** We understand what the tool measures and what it cannot
    see.
2.  **Statistical Quality:** Its assumptions, dependence, instability,
    and distributional behavior are characterized well enough for the
    intended use.
3.  **Predictive Quality:** It adds stable, incremental OOS information
    about a clearly defined future target.
4.  **Economic Quality:** The information can be converted into a
    portfolio that survives realistic costs, execution constraints, and
    path risk.

**Failure at an earlier gate should stop downstream optimization.**

------------------------------------------------------------------------

## 8. Team Rules

1.  Never equate an indicator value with a trade.
2.  Never equate a residual with mispricing without evidence.
3.  Never equate statistical significance with economic significance.
4.  Never optimize a threshold before defining the hypothesis.
5.  Never use full-sample information in a live-compatible historical
    feature.
6.  Never judge robustness from a single best parameter.
7.  Never treat more rows as automatically more independent information.
8.  Never assume normalization guarantees stationarity.
9.  Never delete outliers before deciding whether they are errors or
    real events.
10. Never call a feature useful merely because it is mathematically
    sophisticated.
11. Prefer simple transparent baselines before dynamic/high-dimensional
    models.
12. Document what every transformation keeps, loses, and assumes.
13. Use competing hypotheses rather than confirmation-only research.
14. Evaluate conditional distributions, not only mean return.
15. A research result is not a strategy until portfolio construction,
    execution, and costs are modeled.

## 9. Compact Review Card

-   **WHY:** What phenomenon is it intended to measure, and why might it
    matter?
-   **WHAT:** What information enters, and what is invisible?
-   **HOW:** How are inputs transformed, weighted, normalized, and
    optimized?
-   **LOSE:** What information is compressed away? Can different states
    produce the same output?
-   **ASSUME:** What must be approximately true for the
    interpretation/inference to hold?
-   **PREDICT:** Why should it inform a precisely defined future target
    and horizon? What is the competing hypothesis?
-   **SURVIVE:** Does it persist OOS, across regimes/assets, and across
    a stable parameter region without leakage/data snooping?
-   **PAY:** After realistic costs, execution, portfolio constraints,
    and path risk, is the edge economically usable?

## Closing Principle

> **Do not ask whether a quantitative tool "works." Ask what it
> measures, what it forgets, what it assumes, what it predicts, where
> that relationship survives, and whether the surviving information can
> actually be monetized.**

------------------------------------------------------------------------

## v1.1 notes — from applying the framework to ภาคผนวก E (2026-09)

Three additions the appendix work suggested; none change the eight questions, they sharpen them.

1.  **NULL — an explicit step between ASSUME and PREDICT.**
    *"Under pure randomness (a symmetric random walk with the asset's own
    volatility), what does this output look like, and how often does the
    cutoff fire?"* This is the single most productive device in the
    appendix: RSI outside 30/70 fires 11.4 % of days, Bollinger ±2σ 11.8 %,
    a 20-day breakout 12.9 % (Sparre Andersen, exact), |t| > 2 on a
    20-day price regression 71.7 %, and R² of a regression on EMA12 has a
    median of 0.88 — all with zero information present. Every "it works"
    claim must be quoted against this base rate, not against zero. The
    framework mentions the null hypothesis inside PREDICT; it deserves its
    own gate because it can be computed *before* any predictive study, from
    the formula alone.

2.  **MECHANISM as part of Gate 3, not a template field.** "Why should this
    edge exist, and who is on the other side?" (Grossman–Stiglitz; see
    `theory-part3`). A statistically surviving relationship with no
    mechanism is a candidate for data snooping until proven otherwise.

3.  **SENSOR check inside WHAT.** "Does the historical feature and the live
    feature measure the same thing, with the same data?" (close-only vs
    OHLC, snapshot vs tick, test-mode vs live-mode). The appendix hit this
    accidentally: with close-only data +DI ≡ RSI exactly, and ATR is
    systematically too small, so stops set from it are too tight.

Mapping to the book ("คิดแบบ Quant"): WHY/WHAT/HOW/LOSE/ASSUME/NULL = ภาคผนวก E
(Gate 1); Gate 2 = Part 1 & 4 and the autocorrelation card; Gate 3 = Part 2 & 8,
`statarb-signal-blending`, `theory-part5`; Gate 4 = Part 5 & 7,
`statarb-live-vs-backtest`, `nq-tool-breakeven`.

### Where each section already lives in the library (Write Once — reference, don't duplicate)

| Framework section | Canonical home in `docs/` |
|---|---|
| §1 pipeline & four distinctions | `nq-index` (8 stations), `nq-part3` (measurement), `nq-part5` (cost), `nq-part7` (position) |
| §2 WHY/HOW/LOSE/ASSUME + NULL | `nq-appendix-indicators` (9 cards, every number reproducible from `indicator-figures.json`) |
| §2 WHAT (information set, sensor) | `nq-part3` station ③, `statarb-data-quality` |
| §2 PREDICT (target, horizon, competing hypotheses, mechanism) | `nq-part2`, `theory-part3` (Grossman–Stiglitz), `statarb-signal-blending` (incremental information) |
| §2 SURVIVE (OOS, walk-forward, multiple testing) | `nq-part8`, `theory-part5` (deflated Sharpe), `math-part11` (purged CV, block bootstrap), `statarb-alpha-decay` |
| §2 PAY | `nq-part5`, `nq-part7`, `pillars-part3` (impact, Almgren–Chriss), `statarb-live-vs-backtest`, `nq-tool-breakeven` |
| §3 effective information / stationarity | `nq-part1` (sample size), `math-part9` ch.8, autocorrelation card in appendix E (SE = 1/√n, 400 days) |
| §4 simple & multiple regression | `math-part8` ch.6 (SE, p-value, robust, VIF, overfitting), `math-part4` (β, PCA worked) |
| §4 spurious regression & cointegration | `math-part9` ch.8–9 (Engle–Granger, OU half-life), appendix E card 5 (71.7 % spurious |t|>2; Nelson–Kang 1984) |
| §5 factor structure / residualization | `math-part4` (PCA), `arb-part5` (pairs, factor stat-arb), `statarb-copula-practice` (tail dependence) |
| §5 execution & cost model | `pillars-part3`, `arb-part7`, `statarb-live-vs-backtest` |
| §5 monitoring after go-live | `statarb-alpha-decay`, `statarb-live-vs-backtest` |
| §6 template A–D | appendix E card anatomy (📜 🔧 🔍 👁 🗑 ✂️ ❌) |
| §6 template E–H | outside the "คิดแบบ Quant" book by design — see the rows above |
| §7 gates, §8 rules, §9 review card | Thai rendering: `quant-tool-critique-framework.html` |
