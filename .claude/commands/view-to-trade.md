# View to Trade

Convert a market belief into a concrete trade structure using the 5-Dimensional Belief Framework (from the View→Payoff and Payoff Mastery books).

**Usage:** `/view-to-trade <belief description>`

Examples:
- `/view-to-trade "BTC will rise 20% in 30 days, confident 70%, no crash fear"`
- `/view-to-trade "BTC sideways in 90k–115k range, IV looks expensive at rank 72"`
- `/view-to-trade "ETH vol will drop, IV rank 80 vs RV only 45, 21 days"`
- `/view-to-trade "BTC/ETH spread stretched +2.1 sigma, expect reversion"`

## Steps

The belief is: $ARGUMENTS

---

### STEP 1 — Decode the 5 Dimensions

Extract or infer each dimension from the stated belief:

**Dimension 1 — Direction**
- What moves and by how much? (e.g., BTC +20%, ETH neutral, spread −2σ)
- Confidence level (0–100%)?
- Asymmetry: fear upside or downside more?

**Dimension 2 — Range / Boundaries**
- Is there a ceiling belief? → Short Call at K
- Is there a floor belief? → Long Put (or Short Put if collecting premium)
- Is there a corridor [K₁, K₂]? → Condor / Iron Condor
- No boundary → Long naked option

**Dimension 3 — Probability Shape**
- Uniform across range → Iron Condor (flat interior payoff)
- Peaked at center → Butterfly (max profit at midpoint)
- Fat tails → Add long wings to any structure
- Bimodal (binary move) → Wide Strangle

**Dimension 4 — Vol View**
```
IV Rank:       (IV − IV_min) / (IV_max − IV_min)
IV Percentile: days_with_IV_below_today / 252

Short vol: Rank > 75% AND Percentile > 80%
Long vol:  Rank < 25% AND clustering detected
```

**Dimension 5 — Time / Path**
- DTE preference (days to expiry)?
- Is path important (barrier, Asian, binary) or just final price?
- Theta decay speed: >30 DTE = slow; <7 DTE = Gamma acceleration zone

---

### STEP 2 — Design the Payoff

1. Describe the ideal P&L curve at expiry in words: "flat max profit between K₁ and K₂, limited loss outside"
2. Draw it verbally: profit zone, breakevens, max gain, max loss
3. Apply slope decomposition:
   ```
   At each price kink where slope changes:
     Δslope = +1 → Long option at that strike
     Δslope = −1 → Short option at that strike
   ```
4. List the required legs (Call or Put, Long or Short, at which strikes)

---

### STEP 3 — Enumerate Constructions

Using put-call parity, list all ways to build the same payoff shape:

For each construction, compute:
- Net credit or debit
- Capital at risk
- Max profit / Capital ratio
- IV skew advantage (is any long leg at lower IV than short leg?)
- Number of legs (fewer = less slippage)

Score and recommend the best construction.

**Common constructions:**
| Payoff Shape | Construction Options |
|-------------|---------------------|
| Neutral corridor | Iron Condor (calls+puts) / Short Strangle / Call Condor / Put Condor |
| Peaked at center | Iron Butterfly / Short Straddle + wings |
| Bull spread | Bull Call Spread (debit) / Bull Put Spread (credit) |
| Bear spread | Bear Put Spread (debit) / Bear Call Spread (credit) |
| Pure long vol | Long Straddle / Long Strangle |
| Pure short vol | Short Straddle / Short Strangle / Iron Condor |

---

### STEP 4 — Map to Playground Game

Which of the 42 games best matches this structure?

| If the structure is... | Likely game |
|------------------------|------------|
| Iron Condor | G17 (Iron Condor) |
| Short gamma, collect premium | G17 / G18 (VCP) |
| Bull spread | G19 (Directional Spread) |
| Pairs mean reversion | G21 (PairGrid) |
| Vol selling | G29 (VRS) |
| Crisis hedge | G27 (FlashCrash) / G42 (FRMR) |

Cross-check with regime: if detected regime ≠ this game's preferred regime → flag caution.

---

### STEP 5 — Quick Sizing & Risk

Apply basic sizing:
- Option premium: max 2–5% of Active Zone per trade
- Position size: Gate A check (WCL ≤ Capital × Zone% × MaxDD%)
- For pairs: Kelly-adjusted, full stat arb z-score confirmation needed

---

### OUTPUT FORMAT

```
═══ VIEW → TRADE ════════════════════════════════════════
Belief: {paraphrase of input}
─────────────────────────────────────────────────────────
5D ANALYSIS:
  Direction:  {asset} {direction} ~{magnitude}  ({confidence}% conf.)
  Range:      {corridor / bounded / unlimited}
  Prob Shape: {uniform / peaked / fat-tail / bimodal}
  Vol View:   {short/long/neutral}  IVR={rank}%
  Time:       {DTE} days  |  Path: {yes/no}
─────────────────────────────────────────────────────────
PAYOFF DESIGN:
  Max profit: {value} when {condition}
  Max loss:   {value} when {condition}
  Breakevens: {K_lower} / {K_upper}

LEGS:
  {Long/Short} {Call/Put} {Strike}  [slope change explanation]
  ...
─────────────────────────────────────────────────────────
CONSTRUCTIONS (ranked):
  ① {name}  — Credit: {$}  Cap at risk: {$}  Ratio: {%}  ← RECOMMENDED
  ② {name}  — Credit: {$}  Cap at risk: {$}  Ratio: {%}
─────────────────────────────────────────────────────────
PLAYGROUND GAME:  G{n} — {name}
REGIME CHECK:     {R} fits? {yes/no — explain}
SIZING HINT:      Premium ≤ {$} (2% of Active Zone)
                  WCL: {$} — Gate A {pass/fail}
═════════════════════════════════════════════════════════
```

If the belief describes a pairs/stat arb trade (spread mean reversion), use the stat arb framework instead of options:
- State spread ε, current z-score, entry direction
- Check half-life and ADF p-value if known
- Size via Kelly adjusted for pairs
