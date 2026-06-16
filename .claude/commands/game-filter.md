# Game Filter

Run the OS (Operating System) 6-step funnel to find which of the 42 Playground games to play today.

**Usage:** `/game-filter <regime> [options]`

Examples:
- `/game-filter R1` — range regime, show all passing games
- `/game-filter R2 instrument=BTC capital=500000`
- `/game-filter R4 instrument=options zone=active`

## The 42 Games (from The Playground — Part 9)

| Category | Games |
|----------|-------|
| Grid / Range | G1 Simple Grid, G2 Soft Martingale Grid, G3 Anti-Martingale Grid, G4 Fibonacci Grid, G5 Asymmetric Grid, G6 Multi-Asset Grid |
| Trend | G7 Trend Rider, G8 Breakout Grid, G9 Pullback Grid, G10 Momentum Grid, G11 Trend + Grid Hybrid |
| Options Income | G12 Iron Condor, G13 Calendar Spread, G14 Strangle, G15 Butterfly, G16 Jade Lizard, G17 Covered Call, G18 Cash-Secured Put |
| Options Directional | G19 Debit Spread, G20 Long Call/Put, G21 Ratio Spread, G22 LEAPS |
| Volatility | G23 Long Straddle, G24 Short Straddle, G25 Vol Dispersion, G26 VIX Hedge |
| Stat Arb | G27 Pair Grid BTC/ETH, G28 Pair Grid BTC/SOL, G29 Cross-Exchange Arb, G30 Funding Rate Arb |
| Mean Reversion | G31 RSI Grid, G32 BB Grid, G33 VWAP Grid, G34 Overnight Mean Rev |
| Carry / Yield | G35 Funding Carry, G36 Basis Trade, G37 Covered Carry |
| Macro / Event | G38 Pre-FOMC Vol, G39 Earnings Straddle, G40 ETF Arb |
| Special | G41 Crisis Alpha, G42 Tail Risk Hedge |

## Regime → Game Mapping (from The Playground — Part 7)

| Regime | Condition | Best Games | Avoid |
|--------|-----------|-----------|-------|
| R1 Range | Hurst<0.45, ADX<20, IVR<30 | G1–G6, G12–G18, G31–G34 | G7–G11 |
| R2 Uptrend | Hurst>0.55, ADX>25, price>MA | G7–G11, G17, G19, G22, G36 | G12 short side |
| R3 Downtrend | Hurst>0.55, ADX>25, price<MA | G7–G11 short, G20 puts, G19 put spread | G17 |
| R4 High-Vol | IVR>75 | G12–G18 (sell vol), G35–G37 | G23, G24 buy |
| R5 Low-Vol | IVR<20 | G23, G24 (buy vol), G38–G39 | G12–G18 sell |
| R6 Crisis | VIX spike, Hurst mixed | G41, G42, reduce size all | most games |
| R7 Capitul. | Extreme down, IVR>90 | G41, G42, G20 puts | everything else |

## 6-Step OS Funnel

```
Step 1 — Universe:    All 42 games
Step 2 — Regime:      Filter by current R1–R7
Step 3 — Category:    Remove categories outside regime
Step 4 — Instrument:  Keep only games tradeable with available instruments
Step 5 — CRS Gate:    Composite Regime Score ≥ threshold (default 60)
Step 6 — Execute:     Max 2–3 active positions, size via /size-position
```

### CRS Score (0–100)
```
CRS = 0.30×Hurst_score + 0.25×ADX_score + 0.25×IVR_score + 0.20×Trend_score
Threshold: ≥ 60 to open, ≥ 40 to hold
```

## Steps

The argument is: $ARGUMENTS

1. Parse: regime (R1–R7) and optional filters (instrument, capital, zone)
2. Show Step 1 → 6 funnel, with count at each step
3. List passing games with brief rationale
4. Recommend top 2–3 games with sizing suggestion (call `/size-position` logic inline)
5. Flag any games that are marginal (CRS 50–60) as "Monitor"

Format:
```
═══ OS Funnel ════════════════════════════════════
Regime: {R}  |  {date}
Step 1  Universe        42 games
Step 2  Regime filter   → {N} games  (R{x} compatible)
Step 3  Category        → {N} games
Step 4  Instrument      → {N} games  (BTC/ETH options available)
Step 5  CRS Gate ≥60    → {N} games
─────────────────────────────────────────────────
ACTIVE (max 3):
  ① {GameName}  — CRS {score}  — size {suggestion}
  ② {GameName}  — CRS {score}  — size {suggestion}

MONITOR:
  {GameName}  — CRS {score}  — watch for entry
══════════════════════════════════════════════════
```
