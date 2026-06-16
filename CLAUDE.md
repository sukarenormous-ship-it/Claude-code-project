# Quant Trading Knowledge Base

This repository contains 10 Thai-language quant trading books, PDF builders, and Claude Code skills for both book production and live trading decisions.

## The 10 Books

| Prefix | Title | Core Topic |
|--------|-------|-----------|
| `grid` | Grid Trading Mastery | Grid strategies, Kelly sizing, drawdown control |
| `playground` | The Playground | 42 trading games, R1–R7 regime OS, full risk framework |
| `math` | คณิตศาสตร์สำหรับ Options | Options math: Greeks, Black-Scholes, Monte Carlo |
| `vol` | Volatility Mastery | IV vs RV, vol risk premium, vol regime trading |
| `vp` | View → Payoff | 5D belief framework, strategy construction algorithm |
| `pm` | Payoff Mastery | Payoff design first, then construction selection |
| `statarb` | Statistical Arbitrage | Cointegration, spread, z-score, rolling monitor |
| `arb` | Arbitrage | Cash-and-carry, merger arb, funding rate arb |
| `eye` | ตาของ Arbitrageur | Options mindset: everything in life is an option |
| `python` | Python for Quant Traders | numpy/pandas/scipy/statsmodels patterns for trading |

## Skills

| Skill | Usage | Purpose |
|-------|-------|---------|
| `/build-book <prefix>` | `/build-book vol` | Rebuild any book to PDF + send |
| `/review-book <prefix> [part]` | `/review-book vol part3` | Screenshot visual QA at A4 width |
| `/add-diagram <part> <type> <desc>` | `/add-diagram vol-part3 bar "..."` | Add MiniChart to HTML part |
| `/regime-check <indicators>` | `/regime-check hurst=0.42 adx=16 ivr=25` | Classify R1–R7 + CRS score |
| `/game-filter <regime>` | `/game-filter R1 instrument=BTC` | Run 6-step OS funnel → top games |
| `/calc-wcl <game> <params>` | `/calc-wcl martingale q0=0.02 m=1.5 N=3` | WCL + Gate A/B check |
| `/size-position <method> <params>` | `/size-position kelly mu=0.08 sigma=0.25` | Martingale / Kelly / Bell sizing |
| `/trading-plan <market>` | `/trading-plan BTC neutral IVR=68` | Full end-to-end plan (all books) |
| `/view-to-trade <belief>` | `/view-to-trade "BTC bullish +20%"` | 5D belief → payoff → structure |

---

## The Unified Framework

All 10 books form one integrated decision system:

```
OBSERVE MARKET
    │
    ▼
SEE OPTIONS EVERYWHERE          ← eye
("If…Then…" = option; salary = bond; insurance = put)
    │
    ▼
FORM 5D BELIEF                  ← vp + pm
  1. Direction  (magnitude, confidence, asymmetry)
  2. Range      (corridor / bounded / unlimited)
  3. Prob Shape (uniform / peaked / fat-tail)
  4. Vol View   (IV > RV? sell; IV < RV? buy)
  5. Time/Path  (days to expiry, path-dep?)
    │
    ▼
DETECT REGIME                   ← grid + playground
  Hurst + ADX + IVR + Funding Rate → R1–R7
    │
    ▼
SELECT GAME (OS Funnel)         ← playground
  42 games → regime filter → instrument filter → CRS gate → 2–3 positions
    │
    ├── If directional trade ──→ PAYOFF DESIGN      ← pm + vp + math
    │                              slope decomp → enumerate → score constructions
    │
    └── If pairs/arb ─────────→ STATISTICAL EDGE    ← statarb + arb + python
                                   cointegration → z-score → entry/exit rules
    │
    ▼
SIZE THE POSITION               ← grid + playground
  Martingale / Kelly (25% fractional) / Bell Curve
    │
    ▼
RISK CHECK (CRS Sheet)          ← playground
  WCL → Gate A → Gate B → Portfolio stress → PASS or resize
    │
    ▼
EXECUTE + MONITOR (8-Step OS)
  Daily 3-check: stop triggered? regime changed? portfolio WCL in Gate B?
    │
    ▼
EXIT & RECYCLE
  TP hit: 80% → Active, 20% → Standby, 24h wait
  Stop hit: root cause analysis, 24h cooling
```

---

## Regime Framework (R1–R7)

**Four signal inputs:**

| Signal | Mean-Reverting | Random | Trending/High |
|--------|---------------|--------|---------------|
| **Hurst (H)** | < 0.45 | 0.45–0.55 | > 0.55 |
| **ADX** | < 20 (no trend) | 20–25 (weak) | > 25 (strong) |
| **IVR** | < 30 (low vol) | 30–70 (normal) | > 70 (high vol) |
| **Funding Rate** | < −0.05% (bearish) | ±0.05% (neutral) | > 0.05% (bullish) |

**Regime profiles:**

| Regime | Condition | Top Games | Max Size | Close |
|--------|-----------|-----------|----------|-------|
| **R1** Range | H<0.48, ADX<20, IVR<50 | G1 Grid, G17 Iron Condor, G21 PairGrid | 100% | — |
| **R2** Trend Up | H>0.52, ADX>25, FR>0.02% | G6 TP2, G25 FrontLoad, G37 VCG | 100% | G1, G17 |
| **R3** Trend Down | H>0.52, ADX>25, FR<−0.02% | G20 RiskRev, G38 PutLadder, G42 FRMR | 50% | G1, G15, G2 |
| **R4** High-Vol | IVR>70, 5d_move>10% | G3 AntiFrag, G27 FlashCrash, G29 VRS | 25% | G2, G17, G41 |
| **R5** Transition | Ambiguous signals | G29 VRS, G30 Graduation | 50% | most |
| **R6** Euphoria | FR>0.10%, IVR<40, Sentiment>80 | G16 CovCall, G38 Hedge, G42 FRMR | 30% | G6, G32 |
| **R7** Capitulation | FR<−0.08%, IVR>80 | G27 Deploy, G15 CSP, G39 CCT | 30% | — |

**Game conflicts (cannot run simultaneously):**
- G2 Soft Martingale ⚔ G3 Anti-Fragile
- G17 Iron Condor ⚔ G29 VRS (opposite gamma)
- G22 Basis Trade ⚔ G42 FRMR
- G32 Halving Carry ⚔ G37 VCG

---

## Risk Management

### Zone Waterfall
```
Total Capital (C₀)
├─ Active Zone  (50%) → deployed as live orders
├─ Standby Zone (30%) → yield/lending or staged reserve
└─ Floor Zone   (20%) → emergency reserve; NEVER touch
```
After each game closes: rebalance waterfall. If Active < 50% → pull from Standby.

### WCL & Gates
```
Martingale:  Q_total = q₀ × (mᴺ − 1)/(m − 1)
             WCL     = Q_total × |P_entry_avg − P_stop|

Gate A (game-level):  Capital × Zone% × MaxDD_micro%   → PASS if WCL ≤ Gate A
Gate B (portfolio):   Capital × MaxDD_macro%            → PASS if portfolio WCL ≤ Gate B
```
If Gate A fail → resize: `q₀_new = q₀ × (Gate A / WCL)`

### Drawdown Ladder
```
DD = −5%  → WARNING: review positions
DD = −8%  → HALT: no new games
DD = −12% → KILL SWITCH: close all, 72h cooling
Resume: DD > −4% AND H < 0.55 AND 24h cooling
```

### Position Sizing
```
Martingale   qₖ = q₀ × mᵏ  (k = 0…N−1)
Kelly        f* = (p×b − q)/b ; use f_safe = 0.25 × f*
             Q = Capital × Zone% × f_safe / price
Bell Curve   Qᵢ ∝ exp(−(Pᵢ − μ)² / 2σ²); σ = ATR × factor; normalize Σ Qᵢ = Q_total
```

---

## Options Framework

### 5-Dimensional Belief (vp book)
1. **Direction** — "[Asset] will move [±X%] with [Y%] confidence, fearing [up/down] more"
2. **Range** — corridor [K₁,K₂] / bounded one side / unlimited
3. **Probability Shape** — uniform → condor; peaked → butterfly; fat-tail → add wings
4. **Vol View** — IV > RV (sell vol); IV < RV (buy vol); confirm with Rank + Percentile
5. **Time/Path** — DTE, path-dependent or not, Theta decay speed

### Strategy Construction (pm + vp)
```
Step 1: Imagine P&L curve at expiry (don't name strategy yet)
Step 2: Decompose — at each slope kink: Δslope +1 = Long leg, Δslope −1 = Short leg
Step 3: Enumerate — same shape via put-call parity → multiple constructions
Step 4: Score — credit/debit, IV skew advantage, capital efficiency, simplicity
```

### Vol Decision Rules
```
Short vol: IV Rank > 75% AND IV Percentile > 80% AND RV declining
           → Iron Condor / Short Strangle / Calendar sell
Long vol:  IV Rank < 25% AND vol clustering detected AND RV accelerating
           → Long Straddle / Long Strangle / Calendar buy
```

### Strategy Quick-Select
| Belief | Strategy | Greeks |
|--------|----------|--------|
| Neutral, range-bound | Iron Condor | Theta+, Vega−, Delta≈0 |
| Mildly bullish | Bull Call Spread | Delta+, Theta−, Vega+ |
| Strongly bullish | Long Call | Delta+, Gamma+, Vega+ |
| Vol will drop | Short Strangle | Theta+, Vega−, Delta≈0 |
| Vol will rise | Long Straddle | Gamma+, Vega+, Theta− |
| Binary event | Strangle | Vega+, Gamma+ |

---

## Statistical Arbitrage Framework

### Spread Construction
```
ε_t = log(P_A,t) − β × log(P_B,t)
β = OLS slope on log prices (recalibrate weekly)
```

### Pair Selection Pipeline
```
Level 1 — GATE (must pass):
  ρ ≥ 0.70  AND  ADF p < 0.05

Level 2 — TUNE:
  Shapiro-Wilk: p ≥ 0.05 → standard z; else → robust z (MAD)
  Half-life: τ = −ln(2)/ln(φ); ideal 2h–2 weeks

Level 3 — CONFIRM:
  Hurst H < 0.5 (mean-reverting, not trending)
```

### Entry / Exit / Stop
```
z_t = (ε_t − μ) / σ_stat

Entry:  z > +2 → Short spread (short A, long β×B)
        z < −2 → Long spread  (long A, short β×B)
Exit:   |z| < 0.5 → Close position
Stop:   |z| > 4  OR  p-value > 0.10 → Emergency exit
```

### Rolling Monitor (Traffic Light)
```
🟢 p < 0.05   → Full position
🟡 p 0.05–0.08 → Reduce 50%
🟠 p 0.08–0.10 → Reduce 80%, no new entries
🔴 p > 0.10   → Close ALL immediately
Watch the TREND of p, not just the level.
```

### Arbitrage Types (arb book)
- **Cash-and-carry**: Spot < Futures → buy spot, short futures
- **Stat arb**: Cointegrated pairs, z-score entry/exit
- **Funding rate arb**: Perpetual funding harvest (Spot + Short Perp)
- **Cross-exchange basis**: Spot on exchange A, futures on B
- **IV surface arb**: Options implied vol mispricings

---

## Key Formulas

| Formula | Expression | Notes |
|---------|-----------|-------|
| Grid profit/cycle | Q × Step − Fees | × cycles/day = daily P&L |
| Kelly f* | (p×b − q)/b | Use 25% fractional only |
| Q per level | Grid_cap / (N × P_avg) | Capital ÷ (levels × price) |
| WCL (martingale) | Q_total × \|P_avg − P_stop\| | Full exposure × stop distance |
| Gate A | Capital × Zone% × MaxDD% | Game risk budget |
| Step optimal | (Half-Life_days × ATR) / 2 | Grid step from mean-reversion speed |
| Zone width (GARCH) | 2 × σ_GARCH × √T | 95% coverage of price range |
| Spread ε | log(P_A) − β × log(P_B) | Recalibrate β weekly |
| Z-score | (ε − μ) / σ_stat | Entry ±2, emergency stop ±4 |
| Half-life | −ln(2) / ln(φ) | φ = AR(1) of spread |
| Vol annualize | σ_daily × √252 | 1% daily ≈ 16% annual |
| IV Rank | (IV − IV_min) / (IV_max − IV_min) | > 75% = expensive vol |
| Kelly Q size | Capital × Zone% × f_safe / price | f_safe = 0.25 × f* |

---

## Book Reference Map

| Question | Book | Key Chapter |
|----------|------|-------------|
| "What's the optimal grid step?" | grid | Part 0, Part 5 |
| "What regime am I in?" | playground | Part 7 |
| "Which game to play now?" | playground | Part 9 (8-step OS) |
| "How do I test for cointegration?" | statarb | Ch.5 |
| "How do I price this option?" | math | Part 3–4 (Black-Scholes) |
| "How do I size this trade?" | playground | Part 1, Part 3 |
| "What payoff shape do I want?" | vp | Part 3–4 (slope algorithm) |
| "Same payoff, which construction?" | pm | Part 0–2 |
| "When to sell vs buy vol?" | vol | Part 3–4 |
| "What arb opportunities exist?" | arb | Part 1, Part 5 |
| "Is this really an option?" | eye | Part 1 (If…Then… mindset) |
| "How to code this?" | python | Part 1–4 |

---

## PDF Builder Reference

```bash
python build_pdf.py                  # Grid Trading Mastery → pdf/Grid-Trading-Mastery.pdf
python build_pdf_playground.py       # The Playground       → pdf/The-Playground.pdf
python build_pdf_generic.py <prefix> # All other books      → pdf/{prefix}-BOOK.pdf

# All other prefixes: arb, eye, math, pm, python, statarb, vol, vp
```

## Git

- Branch: `claude/continue-latest-commit-sxxwJ`
- After pushing: always create a draft PR if one doesn't exist
- Push: `git push -u origin claude/continue-latest-commit-sxxwJ`
