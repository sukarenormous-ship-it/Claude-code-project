# Layer 2 — Knowledge Layer (Playbooks / Skills)

Layer 2 is your setup library. Playbooks are loaded on-demand — Claude pulls in the relevant one based on what you are looking for in that session. Markets change in character constantly, but your playbook definitions should not. A breakout setup is a breakout setup. The precision lives in the file.

**Two types:**
- **Global playbooks** (`~/.claude/skills/`) — Reusable across every market you trade. Shared logic that applies regardless of instrument or environment.
- **Project playbooks** (`.claude/skills/`) — Built for one strategy or market environment only. Holds repo-specific edge, market-specific workflows.

---

## The Three Core Playbooks

### breakout.md — Momentum Continuation Setups

When the user asks you to write a breakout playbook, generate this structure customized to their instrument:

```markdown
# Breakout Playbook — [INSTRUMENT]

## What Is a Valid Breakout
A breakout is valid when:
- Price has consolidated for at least [N] bars/candles at a clear level.
- The level is defined by [prior high/low / VWAP / overnight range / key round number].
- The breakout candle closes [above/below] the level with [X]% of its body outside.

## Confirmation Rules (ALL must be true before entry)
- [ ] Volume on the breakout candle is [X]× the [N]-bar average volume.
- [ ] The candle is not a doji or indecision candle.
- [ ] No major news event is scheduled within [X] minutes.
- [ ] I am within my valid trading hours.
- [ ] Daily drawdown limit has not been reached.

## Entry Trigger
- Entry: [Open of the next candle after confirmation / Limit at retest of broken level].
- If price re-enters the broken level by more than [X] points/%, the setup is invalid.

## Stop Placement
- Stop: [Below the breakout candle low / Below the consolidation range / ATR-based].
- Hard stop: never moved against the position.
- Maximum stop distance: [X] points / [X]% — if setup requires a wider stop, skip it.

## Scaling Logic
- Scale 1: Take [X]% at [1R / first target level].
- Move stop to breakeven after Scale 1 is taken.
- Scale 2: Let the runner go to [2R / measured move target].

## Invalidation Conditions (Exit immediately if any occur)
- Price closes back inside the consolidation range.
- Volume drops to below-average on continuation candles.
- A reversal candle forms at the first target level.
- I have been in the trade for [N] bars with no progress.
```

---

### pullback.md — Trend Continuation Entries

```markdown
# Pullback Playbook — [INSTRUMENT]

## Trend Definition
A valid trend for pullback entries requires:
- Higher highs and higher lows on [TIMEFRAME] (for longs).
- Price is [above/below] the [20/50/200]-period moving average.
- The most recent swing has made a new high/low within the last [N] bars.

## Acceptable Pullback Depth
- Pullback is valid if price retraces between [30%] and [60%] of the prior swing.
- Deeper than [60%] of the prior swing: trend structure may be breaking. Skip.
- Shallower than [30%]: entry too aggressive, skip.

## Structure Needed to Confirm Continuation
- [ ] Pullback terminates at a defined level: [moving average / prior structure / Fibonacci level].
- [ ] A higher low forms on the pullback (for longs) — confirmed by a bullish reversal candle.
- [ ] Volume decreases on the pullback and expands on the reversal candle.

## Criteria That Invalidate the Setup
- Price takes out the prior swing low/high (trend structure broken).
- Volume expands on the pullback (suggests distribution, not consolidation).
- Price closes below/above the moving average during the pullback.

## Entry Trigger
- Entry: [On confirmation candle close / Limit at the pullback level].
- If price moves more than [X]% past the entry level before I enter, skip the trade.

## Stop Placement
- Stop: Below the pullback low (for longs), above the pullback high (for shorts).
- No more than [X] points from entry.

## Exit Plan
- Target: Prior swing high/low or next significant level.
- Trail: Once at 1R, move stop to breakeven. Trail by [ATR / swing lows].
```

---

### mean-reversion.md — Fade and Reversal Logic

```markdown
# Mean-Reversion Playbook — [INSTRUMENT]

## Extended Conditions (Required for a Fade Entry)
Price must show ALL of the following:
- Extended [X] standard deviations from the [N]-period moving average.
- [RSI / Stochastic] reading above [70] (for fade shorts) or below [30] (for fade longs).
- Price is [X]% above/below the prior day close OR overnight range extreme.
- No momentum catalyst (earnings, major news) driving the extension.

## Trigger for a Fade Entry
- Wait for a reversal candle: [bearish engulfing / shooting star / pin bar] for shorts.
- The reversal candle closes in the opposite direction of the extension.
- Volume does NOT need to be extreme — this is a fade, not a breakout.

## Hard Stop Placement
- Stop: [X] points beyond the reversal candle extreme.
- This is a hard stop. Mean-reversion trades can run far if wrong.
- If the stop is wider than [X] points, the trade does not meet the playbook criteria.

## Profit Target Logic
- Primary target: Return to the [mean / VWAP / prior day close / moving average].
- Do NOT try to ride it further — mean-reversion is not a trend trade.
- If the primary target is not reached within [N] bars, exit at market.

## Invalidation
- Price makes a new extreme in the direction of the extension (trend resuming).
- A catalyst appears that justifies the extension (news, data release).
- The reversal candle's high/low is taken out before target is reached.
```

---

## Starter Prompts

**Write a breakout playbook:**
```
Write a breakout.md playbook for [your instrument]. Include: valid breakout structure,
volume confirmation rules, entry trigger, initial stop placement, scaling logic, and the
conditions that invalidate the setup.
```

**Load and apply a playbook:**
```
Load pullback.md. Scan [instrument] on [timeframe] and identify any current setups that
match the pullback criteria. For each one, specify entry, stop, and target.
```

**Compare setup against playbook:**
```
I am looking at this chart: [describe or attach]. Score this setup against my breakout.md
criteria from 1 to 10 and tell me what is missing before I can take the trade.
```

**Build a custom playbook from your trading history:**
```
Review the last [N] trades in trades.log that I labeled as [setup type]. Extract the common
characteristics across the winners and write them into a new playbook called [name].md.
```
