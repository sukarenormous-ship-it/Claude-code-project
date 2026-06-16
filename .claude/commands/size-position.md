# Size Position

Calculate position size using Martingale, Kelly, or Bell Curve sizing — from The Playground framework.

**Usage:** `/size-position <method> <params>`

Examples:
- `/size-position martingale capital=500000 zone=30 q0=0.01 m=1.5 N=3 price=100000`
- `/size-position kelly capital=500000 zone=30 mu=0.08 r=0.02 sigma=0.25`
- `/size-position bell capital=500000 zone=30 levels=5 mid=100000 atr=3000`

## Methods & Formulas (from The Playground — Parts 0–1, 3)

### 1. Martingale Sizing
```
Level k size:    qₖ = q₀ × mᵏ           (k = 0, 1, 2, … N−1)
Total exposure:  Q_total = q₀ × (mᴺ − 1) / (m − 1)
Capital check:   Q_total × price ≤ Capital × Zone%   (must hold)

Parameters:
  q₀  = base lot size (e.g. 0.01 BTC)
  m   = multiplier (typical: 1.3–2.0)
  N   = number of levels (typical: 3–5)
```

### 2. Kelly Criterion Sizing
```
Kelly fraction:  f* = (μ − r) / σ²
Fractional Kelly: f_used = f* × kelly_fraction   (typical: 0.25–0.50)
Position size:   Q = Capital × Zone% × f_used / price

Parameters:
  μ   = expected return (annualized)
  r   = risk-free rate
  σ   = annualized volatility
  kelly_fraction = safety scaling (default 0.25)
```

### 3. Bell Curve (Gaussian) Zone Sizing
```
Size at level i:  Qᵢ ∝ exp(−(Pᵢ − μ)² / 2σ²)
Normalize so Σ Qᵢ = Q_total
Parameters:
  μ   = zone midpoint price
  σ   = ATR × spread_factor (controls how fast size tapers from midpoint)
  levels = number of grid levels
```

### Capital allocation reminder
```
Active Zone budget = Capital × Zone%
Max position value  ≤ Active Zone budget
WCL check: always run /calc-wcl after sizing
```

## Steps

The argument is: $ARGUMENTS

1. Parse the method and parameters
2. Show calculation step-by-step with each intermediate value labeled
3. For Martingale: show a table of all levels (k, qₖ, entry price, cumulative Q)
4. For Kelly: show f*, f_used, final position size in BTC and USD value
5. For Bell: show a table of all levels with weights and normalized sizes
6. Always end with:
   - Total exposure in BTC and USD
   - % of zone capital used
   - Reminder to verify with `/calc-wcl`

Format numbers: BTC to 4 decimal places, USD with thousands separator.
