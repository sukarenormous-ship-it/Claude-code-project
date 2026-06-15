# Regime Check

Identify the current market regime (R1–R7) from indicator values and get game recommendations.

**Usage:** `/regime-check <indicators>`

Examples:
- `/regime-check hurst=0.42 adx=16 ivr=25 trend=flat`
- `/regime-check hurst=0.61 adx=34 ivr=42 trend=up price=105000 ma200=98000`
- `/regime-check ivr=88 adx=45 hurst=0.52` — high-vol scenario

## Regime Definitions (from The Playground — Part 7)

| Regime | Name | Hurst | ADX | IVR | Trend | Typical game set |
|--------|------|-------|-----|-----|-------|-----------------|
| R1 | Range / Sideways | < 0.45 | < 20 | 15–40 | Flat | Grid, Iron Condor, BB/RSI |
| R2 | Uptrend | > 0.55 | > 25 | 25–55 | Up | Trend Rider, Covered Call, LEAPS |
| R3 | Downtrend | > 0.55 | > 25 | 30–60 | Down | Short trend, Put spreads |
| R4 | High Volatility | 0.45–0.55 | > 35 | > 75 | Mixed | Sell vol (Condor, Strangle, Calendar) |
| R5 | Low Volatility | < 0.45 | < 15 | < 20 | Flat | Buy vol (Straddle, pre-event) |
| R6 | Crisis / Stress | Mixed | > 40 | > 80 | Down | Crisis Alpha, Tail hedge, reduce |
| R7 | Capitulation | < 0.45 | high | > 90 | Extreme down | Tail hedge only, wait |

## Indicator Descriptions

```
Hurst exponent (H):
  H < 0.45  → mean-reverting (range / choppy)
  H ≈ 0.50  → random walk
  H > 0.55  → trending (persistent)

ADX (Average Directional Index, BTC-calibrated):
  < 20  → no trend
  20–35 → developing trend
  > 35  → strong trend
  > 50  → extreme (caution — often near reversal)

IVR (IV Rank, 0–100):
  < 20  → historically low vol → buy vol opportunities
  20–50 → normal
  50–75 → elevated → options selling becoming attractive
  > 75  → high → premium selling favorable
  > 90  → extreme → crisis/event

Trend (from price vs MA200):
  up    = price > MA200 by > 2%
  down  = price < MA200 by > 2%
  flat  = within ±2%
```

## CRS (Composite Regime Score)

```
Hurst_score = map H to 0–100 for the detected regime direction
ADX_score   = map ADX to 0–100 for regime strength
IVR_score   = map IVR to 0–100 for the regime type
Trend_score = 100 if trend matches regime, 50 if neutral, 0 if counter

CRS = 0.30×Hurst_score + 0.25×ADX_score + 0.25×IVR_score + 0.20×Trend_score
```

## Steps

The argument is: $ARGUMENTS

1. Parse all provided indicator values (hurst, adx, ivr, trend, price, ma200)
2. Score each indicator against ALL 7 regime definitions
3. Identify the **primary regime** (highest match score) and **secondary** (second highest, if within 15 points)
4. Compute CRS for the primary regime
5. List the recommended games for the primary regime (reference game-filter for the full list)
6. Flag any conflicting signals

Format:
```
═══ Regime Check ═════════════════════════════════
Inputs:  Hurst={h}  ADX={adx}  IVR={ivr}  Trend={t}
─────────────────────────────────────────────────
PRIMARY:   R{n} — {name}    (match: {score}%)
Secondary: R{n} — {name}    (match: {score}%)
CRS Score: {crs}/100  →  {STRONG / MODERATE / WEAK}
─────────────────────────────────────────────────
Recommended games:
  ✓ {game list for primary regime}

Caution:
  ⚠ {any conflicting signals or borderline indicators}

Next step: /game-filter R{n} to run the full OS funnel
══════════════════════════════════════════════════
```
