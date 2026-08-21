# Layer 1 — Memory Layer (CLAUDE.md / Risk.md)

Layer 1 is the foundation. It is always loaded, always active. Every rule governing how you trade, how you manage risk, and how you behave during a session lives here. If a rule is not written here, it does not exist in your system.

**Two files, two jobs:**
- `CLAUDE.md` — your global memory. Core trading style, default workflow, session behavior, non-negotiable habits.
- `Risk.md` — your core risk rules. Max position size, max daily drawdown, stop-loss logic.
- `Risk.local.md` — private overrides for account-specific adjustments. **Never commit to version control.**

---

## CLAUDE.md Template

When the user asks you to build their CLAUDE.md, ask these questions first if not already answered:
1. What instrument(s) do you trade? (Stocks, futures, forex, crypto)
2. What timeframe is your primary setup? (1m, 5m, 15m, 1h, daily)
3. How would you describe your trading style? (Momentum, trend following, mean reversion, breakout)
4. What is your maximum daily loss in dollars?
5. What percentage of your account do you risk per trade?
6. What are your non-negotiable rules? (Things you know you break under pressure)

Then generate this structure:

```markdown
# CLAUDE.md — Trading System Rules

## trading.rules

### Entry Model
- I trade [STYLE] setups on [TIMEFRAME].
- My primary edge is [DESCRIBE SETUP IN ONE SENTENCE].
- I only take trades that satisfy ALL of the following:
  - [Condition 1 — e.g., price above VWAP]
  - [Condition 2 — e.g., volume confirmation on breakout]
  - [Condition 3 — e.g., risk:reward minimum 2:1]

### Confirmation Rules
- Before entering, I confirm: [LIST REQUIRED CONDITIONS]
- I do not enter on: [LIST NO-TRADE CONDITIONS — e.g., into a gap, during first 15min, pre-FOMC]

### No-Trade Conditions
- [Condition 1 — e.g., If I have taken 2 losses today, I stop trading]
- [Condition 2 — e.g., No trades during major news events]
- [Condition 3 — e.g., No trades if daily drawdown limit is reached]

---

## risk.rules

See Risk.md for all position sizing and drawdown rules.

Key constraints active at all times:
- Max risk per trade: [X]% of account
- Max daily loss: $[AMOUNT]
- Stop-loss: always defined before entry, never moved against me

---

## execution.workflow

### Pre-Trade Checklist
1. Run PreMarket.sh and read the briefing.
2. Load the relevant playbook for today's session.
3. Confirm I am within my daily drawdown limit before placing any trade.
4. Define entry, stop, and target before entering.

### Entry Trigger
- I enter [at the open of the candle after confirmation / at a specific price level / on a limit order].
- I never chase. If the entry trigger has passed, the trade is missed.

### Trade Management
- Initial stop: [defined by structure / ATR / fixed points]
- Scale-out: [e.g., take 50% at 1R, move stop to breakeven, let runner go]
- Hard stop: never removed, never widened

### Exit Plan
- Target 1: [description]
- Target 2: [description]
- If trade goes against me: exit at stop, no averaging down.

---

## session.behavior

### When I Trade
- I trade [TIME WINDOW, e.g., 9:30–11:30 AM ET and 2:00–3:30 PM ET].
- Outside these hours, I do not look for setups.

### When I Stop
- After [N] consecutive losses, I stop for the day.
- After hitting my daily drawdown limit, I close the platform.
- If I feel frustrated, I stop immediately and run EndOfDay.sh.

### Tilt Control
- Signs of tilt: [e.g., increasing size, revenge trading, ignoring stops]
- If I notice tilt: log the emotion in my journal and close the platform.

### Review Process
- After each session: run PostTrade.sh and log the fill.
- At end of day: run EndOfDay.sh and score my rule adherence.
- Weekly: review the last 20 trades with journal-analyzer subagent.
```

---

## Risk.md Template

```markdown
# Risk.md — Core Risk Rules

## Position Sizing
- Max risk per trade: [X]% of account (= $[AMOUNT] at current equity)
- Position size formula: Risk $ ÷ (Entry price − Stop price) = Shares/contracts
- Never override this formula regardless of conviction level.

## Daily Drawdown Limit
- Max daily loss: $[AMOUNT]
- When this limit is hit: stop trading immediately. No exceptions.
- No "one more trade to get it back."

## Stop-Loss Rules
- Every trade has a hard stop defined before entry.
- Stops are never moved against the position.
- If price reaches the stop, I exit at market. No waiting.

## Maximum Open Risk
- I do not hold more than [X] positions simultaneously.
- Total open risk across all positions cannot exceed [Y]% of account.

## Drawdown Recovery
- After hitting the daily limit: no trading for the rest of the day.
- If I have three consecutive losing days: reduce size by 50% for the next week.
- If equity drops [X]% from peak: stop trading, review system with journal-analyzer.
```

---

## Risk.local.md Template (Never Commit)

```markdown
# Risk.local.md — Private Account Overrides
# DO NOT COMMIT THIS FILE. It is listed in .gitignore.

## Account-Specific Settings
- Current account equity: $[AMOUNT]
- Broker: [NAME]
- Position size override: [if different from Risk.md formula for this account]

## Personal Overrides
- [Any personal adjustments that apply only to this account]
```

---

## Starter Prompts

**Build my CLAUDE.md:**
```
I trade [your style] on [timeframe]. My edge is [describe setup]. My max daily loss is
[amount] and I never risk more than [%] per trade. Write my complete CLAUDE.md including
trading.rules, risk.rules, execution.workflow, and session.behavior sections.
```

**Enforce my rules mid-session:**
```
Check my current position against Risk.md. Am I within my max position size and daily
drawdown limits? Flag any violations immediately.
```

**Session debrief:**
```
Review today's session against my CLAUDE.md rules. Which rules did I follow? Which did I
break? Give me three specific corrections for tomorrow.
```

**System health check:**
```
Review all five layers of my trading system. Identify any gaps, conflicts between rules,
or missing components.
```

**Session briefing:**
```
Run PreMarket.sh, load the relevant playbook for today, and give me a one-paragraph
briefing on what I should be looking for this session.
```
