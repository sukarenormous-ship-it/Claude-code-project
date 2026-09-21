# Layer 3 — Guardrail Layer (Hooks)

Hooks are deterministic. They do not ask for permission and they do not rely on memory. They are shell scripts that fire automatically around session events. The guardrail layer exists because discipline that depends on willpower will eventually fail. Discipline that is automated never does.

**How hooks fire:** Event fires → Matcher checks → Command runs. There is no manual step in between.

Hook scripts live in `.claude/hooks/` (project-level) or `~/.claude/hooks/` (global).

---

## PreMarket.sh — Load Market Context Before the Session

Runs before the session opens. Loads market context, reads overnight structure, and sets bias, key levels, and risk frame for the day. Every session starts with the same information base.

```bash
#!/bin/bash
# PreMarket.sh — Run before every trading session
# Usage: bash PreMarket.sh [INSTRUMENT]
# Output: pre-market briefing to stdout and pre-market.log

INSTRUMENT="${1:-SPY}"
DATE=$(date +%Y-%m-%d)
LOG_FILE="./logs/pre-market.log"
mkdir -p ./logs

echo "=== PRE-MARKET BRIEFING: $DATE ===" | tee -a "$LOG_FILE"
echo "Instrument: $INSTRUMENT" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 1. Overnight range
echo "--- OVERNIGHT RANGE ---" | tee -a "$LOG_FILE"
echo "Fetch overnight high and low for $INSTRUMENT." | tee -a "$LOG_FILE"
echo "Overnight High: [FETCH FROM DATA SOURCE]" | tee -a "$LOG_FILE"
echo "Overnight Low:  [FETCH FROM DATA SOURCE]" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 2. Market regime (trend or range)
echo "--- MARKET REGIME ---" | tee -a "$LOG_FILE"
echo "Is $INSTRUMENT trending or ranging on the daily timeframe?" | tee -a "$LOG_FILE"
echo "Regime: [TREND / RANGE / TRANSITION]" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 3. Key levels
echo "--- KEY LEVELS ---" | tee -a "$LOG_FILE"
echo "Prior day high:  [LEVEL]" | tee -a "$LOG_FILE"
echo "Prior day low:   [LEVEL]" | tee -a "$LOG_FILE"
echo "VWAP yesterday:  [LEVEL]" | tee -a "$LOG_FILE"
echo "Key support:     [LEVEL]" | tee -a "$LOG_FILE"
echo "Key resistance:  [LEVEL]" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 4. Session bias
echo "--- SESSION BIAS ---" | tee -a "$LOG_FILE"
echo "Bias: [LONG / SHORT / NEUTRAL]" | tee -a "$LOG_FILE"
echo "Reason: [ONE SENTENCE]" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 5. Scheduled events
echo "--- SCHEDULED EVENTS ---" | tee -a "$LOG_FILE"
echo "Check economic calendar for events in the next 4 hours." | tee -a "$LOG_FILE"
echo "Events: [LIST OR 'NONE']" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 6. Risk frame
echo "--- RISK FRAME ---" | tee -a "$LOG_FILE"
echo "Daily drawdown limit: \$[FROM RISK.MD]" | tee -a "$LOG_FILE"
echo "Max risk per trade:   [X]% of account" | tee -a "$LOG_FILE"
echo "Account equity today: \$[CURRENT EQUITY]" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo "=== BRIEFING COMPLETE. READY TO TRADE. ===" | tee -a "$LOG_FILE"
```

**Claude Code hook configuration** (add to `.claude/settings.json`):
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "session_start",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/PreMarket.sh"
          }
        ]
      }
    ]
  }
}
```

---

## PostTrade.sh — Log Fills After Execution

Runs after every execution. Logs the fill, saves trade metadata, and captures what changed in the position. Nothing falls through the cracks because nothing depends on you remembering to do it.

```bash
#!/bin/bash
# PostTrade.sh — Run immediately after every trade execution
# Usage: bash PostTrade.sh
# Appends to trades.log

LOG_FILE="./logs/trades.log"
mkdir -p ./logs

# Gather trade details interactively (or pass as args)
echo "=== POST-TRADE LOG ===" 
read -p "Date/Time (YYYY-MM-DD HH:MM): " DATETIME
read -p "Instrument: " INSTRUMENT
read -p "Direction (LONG/SHORT): " DIRECTION
read -p "Setup type (breakout/pullback/mean-reversion): " SETUP_TYPE
read -p "Entry price: " ENTRY
read -p "Stop price: " STOP
read -p "Target price: " TARGET
read -p "Size (shares/contracts): " SIZE
read -p "Fill price (actual): " FILL
read -p "Risk $ on this trade: " RISK_DOLLARS
read -p "Notes (optional): " NOTES

# Calculate R:R
RISK_POINTS=$(echo "$ENTRY - $STOP" | bc 2>/dev/null || echo "[calc manually]")
TARGET_POINTS=$(echo "$TARGET - $ENTRY" | bc 2>/dev/null || echo "[calc manually]")

# Write to log
echo "---" >> "$LOG_FILE"
echo "datetime: $DATETIME" >> "$LOG_FILE"
echo "instrument: $INSTRUMENT" >> "$LOG_FILE"
echo "direction: $DIRECTION" >> "$LOG_FILE"
echo "setup_type: $SETUP_TYPE" >> "$LOG_FILE"
echo "entry: $ENTRY" >> "$LOG_FILE"
echo "fill: $FILL" >> "$LOG_FILE"
echo "stop: $STOP" >> "$LOG_FILE"
echo "target: $TARGET" >> "$LOG_FILE"
echo "size: $SIZE" >> "$LOG_FILE"
echo "risk_dollars: $RISK_DOLLARS" >> "$LOG_FILE"
echo "notes: $NOTES" >> "$LOG_FILE"
echo "status: OPEN" >> "$LOG_FILE"

echo "Trade logged to $LOG_FILE"
```

---

## EndOfDay.sh — Save State Before the Close

Runs before the close. Saves full session state, captures P&L data, and prepares the journal entry for review. The day is closed cleanly every time.

```bash
#!/bin/bash
# EndOfDay.sh — Run at the end of every trading session
# Saves session summary and prepares journal entry

DATE=$(date +%Y-%m-%d)
SUMMARY_FILE="./logs/sessions/session-$DATE.md"
TRADES_LOG="./logs/trades.log"
mkdir -p ./logs/sessions

echo "=== END OF DAY: $DATE ===" 

read -p "Total trades today: " TOTAL_TRADES
read -p "Winning trades: " WINS
read -p "Losing trades: " LOSSES
read -p "Total P&L today (\$): " TOTAL_PNL
read -p "Largest win (\$): " LARGEST_WIN
read -p "Largest loss (\$): " LARGEST_LOSS
read -p "Daily drawdown limit reached? (yes/no): " LIMIT_HIT
read -p "Rules followed (1-10 score): " RULES_SCORE
read -p "Which rules did I break? (or 'none'): " RULES_BROKEN
read -p "What would I do differently? " IMPROVEMENTS

cat > "$SUMMARY_FILE" << EOF
# Session Summary — $DATE

## Performance
- Total trades: $TOTAL_TRADES
- Wins: $WINS | Losses: $LOSSES
- Win rate: $(echo "scale=0; $WINS * 100 / $TOTAL_TRADES" | bc 2>/dev/null || echo "[calc manually]")%
- Total P&L: \$$TOTAL_PNL
- Largest win: \$$LARGEST_WIN
- Largest loss: \$$LARGEST_LOSS
- Daily limit hit: $LIMIT_HIT

## Rule Adherence
- Score: $RULES_SCORE / 10
- Rules broken: $RULES_BROKEN
- Improvements for tomorrow: $IMPROVEMENTS

## Trades Log Reference
See: $TRADES_LOG
EOF

echo "Session summary saved to $SUMMARY_FILE"
echo "=== SESSION CLOSED ==="
```

---

## Starter Prompts

**Write my PreMarket hook:**
```
Write a PreMarket.sh hook that: fetches overnight high and low for [instrument],
identifies the current market regime (trend or range), sets a bias for the session, and
outputs a structured pre-market briefing I can read in under 60 seconds.
```

**PostTrade logging:**
```
Write a PostTrade.sh hook that logs: instrument, direction, entry price, stop price,
size, fill time, and the setup type from my playbook. Save each entry to trades.log with a
timestamp.
```

**End of day review:**
```
Run EndOfDay.sh. Summarize my session: total trades, win rate, largest win, largest loss,
and whether I followed my CLAUDE.md rules. Flag any rule violations with specific examples.
```

**Configure hooks in Claude Code:**
```
Set up hooks in my .claude/settings.json so that PreMarket.sh runs at the start of each
trading session and PostTrade.sh runs after I confirm a trade execution.
```
