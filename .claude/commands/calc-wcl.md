# Calculate WCL

Calculate Worst-Case Loss (WCL) for a position and check it against Gate A.

**Usage:** `/calc-wcl <game-type> <params>`

Examples:
- `/calc-wcl martingale q0=0.02 m=1.5 N=3 entry=100000 stop=90000`
- `/calc-wcl condor premium=1050 wings=5950 contracts=1`
- `/calc-wcl grid q=0.01 levels=5 entry=100000 stop=92000`
- `/calc-wcl pair size=0.5BTC entry_spread=0.25 stop_spread=0.40`

**Gate check:** `/calc-wcl martingale ... capital=500000 zone_pct=30 max_dd=5`

## Formulas (from The Playground — Part 1)

### Martingale / Soft Martingale
```
Position size at level k:   qₖ = q₀ × mᵏ
Total exposure (all N levels filled):
    Q_total = q₀ × (mᴺ − 1) / (m − 1)
Weighted avg entry:
    P_entry_avg = Σ(qₖ × Pₖ) / Q_total
WCL:
    WCL = Q_total × |P_entry_avg − P_stop|
```

### Simple Grid
```
Q_total = q × N_levels
P_entry_avg = average of all entry prices
WCL = Q_total × |P_entry_avg − P_stop|
```

### Options (Iron Condor / Calendar / Condor)
```
WCL = (Max loss per lot) × (number of lots)
Max loss Iron Condor = Wing_width − Net_premium_received
Max loss Calendar    = Net_debit_paid (if spread goes to zero)
```

### Pair Grid (spread trade)
```
WCL = Q_BTC × |spread_entry − spread_stop| × BTC_price
```

### Gate A Check
```
Gate A = Capital × Zone_allocation% × Max_DD%
Pass   : WCL ≤ Gate A
Fail   : WCL > Gate A  →  resize: q₀_new = q₀ × (Gate_A / WCL)
```

## Steps

The argument is: $ARGUMENTS

1. Parse the game type and parameters from the argument
2. Apply the correct formula above to compute WCL step-by-step (show each intermediate value)
3. If capital/zone_pct/max_dd are provided, compute Gate A and show Pass/Fail
4. If failing, compute the resize factor and new q₀ or lot size
5. Format output as:

```
═══ WCL Calculation ══════════════════════════════
Game:         {type}
──────────────────────────────────────────────────
{intermediate calculations, one per line}
──────────────────────────────────────────────────
WCL:          ${value:,.0f}

Gate A:       ${gate_a:,.0f}   (Capital ${cap} × {zone}% × {dd}%)
Result:       PASS ✓ / FAIL ✗
              [If fail: resize q₀ from X → Y]
══════════════════════════════════════════════════
```
