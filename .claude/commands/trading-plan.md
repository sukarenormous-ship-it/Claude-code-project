# Trading Plan

Full end-to-end trading plan: market data → regime → game → structure → size → risk check.

**Usage:** `/trading-plan <market description>`

Examples:
- `/trading-plan BTC at 105000, Hurst=0.43 ADX=17 IVR=62 FR=0.04%`
- `/trading-plan BTC neutral sideways, IVR high 78, capital 500000`
- `/trading-plan ETH trending up strongly, want to express bullish view`

## Steps

The market description is: $ARGUMENTS

Work through each step in order. Show your reasoning at each step.

---

### STEP 1 — Regime Detection

Parse any indicator values from the input. Estimate missing values from the market description.

Classify R1–R7 using:
- **Hurst**: <0.45 = mean-rev | 0.45–0.55 = random | >0.55 = trending
- **ADX**: <20 = no trend | 20–25 = weak | >25 = strong
- **IVR**: <30 = low vol | 30–70 = normal | >70 = high vol
- **Funding Rate**: <−0.05% = bearish | ±0.05% = neutral | >0.05% = bullish

State: Primary regime + CRS score + any secondary regime.

---

### STEP 2 — Game Selection (OS Funnel)

Apply the 6-step funnel for the detected regime (reference game-filter skill for full game list):
1. Start: all 42 games
2. Filter by regime compatibility
3. Filter by category
4. Filter by instrument availability
5. CRS gate ≥ 60
6. Check for game conflicts with any hypothetical open positions

Output: Top 2–3 recommended games with brief rationale.

---

### STEP 3 — Trade Structure

For each recommended game:

**If options-based game** (Iron Condor, Calendar, Spread, etc.):
1. Apply the 5D belief framework:
   - Direction + magnitude?
   - Range boundaries?
   - Probability shape?
   - Vol view (IV Rank / Percentile)?
   - DTE preference?
2. Design payoff using slope decomposition
3. Name 2 equivalent constructions and score them

**If directional/trend game** (Trend Rider, TP2, etc.):
1. State entry price, stop loss, take profit
2. R:R ratio
3. Trailing stop logic if applicable

**If pairs/arb game** (PairGrid, FRMR, etc.):
1. Pair and hedge ratio β
2. Current z-score vs entry threshold
3. Cointegration status (p-value if known)

---

### STEP 4 — Position Sizing

For each trade:
1. Choose sizing method: Martingale / Kelly / Bell Curve (match game type)
2. Compute position size given capital (use 500,000 THB or USD if not specified)
3. Show zone allocation: Active × % of zone

---

### STEP 5 — Risk Check (CRS Sheet)

For each trade:
```
[A] Capital: ___  Zone: ___  Max DD (macro): ___
[B] WCL this game: ___
[C] Gate A = Capital × Zone% × MaxDD_micro% = ___
    WCL ≤ Gate A? → PASS / FAIL
[D] Gate B = Capital × MaxDD_macro% = ___
    Portfolio WCL ≤ Gate B? → PASS / FAIL
[E] If FAIL: resize q₀ → ___
```

---

### OUTPUT FORMAT

```
═══ TRADING PLAN ═══════════════════════════════════════
Asset:   {asset}  |  Price: {price}  |  Date: {date}
─────────────────────────────────────────────────────────
REGIME:  R{n} — {name}   CRS: {score}/100
Signals: H={hurst}  ADX={adx}  IVR={ivr}  FR={fr}
─────────────────────────────────────────────────────────
RECOMMENDED GAMES:

① {Game Name}  [{category}]
   Structure: {describe trade setup}
   Entry: {level}  Stop: {level}  TP: {level}
   Size:  {method} → {size}  ({USD/BTC value})
   WCL:   {value}  Gate A: {value}  → PASS ✓

② {Game Name}  [{category}]
   ...

MONITOR:
  ③ {Game}  —  CRS {score} (watch)
─────────────────────────────────────────────────────────
RISK SUMMARY:
  Portfolio WCL:  {total}
  Gate B:         {value}  → PASS ✓
  Active Zone:    {%} deployed
═════════════════════════════════════════════════════════
```
