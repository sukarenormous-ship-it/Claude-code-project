---
name: the-trading-dev-kit
description: >
  The Trading Development Kit — a five-layer system for building a rule-based trading operation with Claude.
  Use this skill whenever the user mentions: setting up a trading system, writing CLAUDE.md for trading, building Risk.md,
  creating a playbook (breakout, pullback, mean-reversion), writing trade hooks (PreMarket, PostTrade, EndOfDay),
  setting up trading subagents (market researcher, risk manager, journal analyzer), packaging a trading plugin,
  scaffolding a trading kit, enforcing trading rules, session debrief, or anything about systematic/rule-based trading with Claude.
  Trigger even if the user says "trading system", "trade rules", "my playbook", "position sizing rules", "trade journal", or "trading CLAUDE.md".
---

# The Trading Development Kit

> Write your system once. Stop donating to the market.

A five-layer system that turns Claude into a consistent, rule-based trading co-pilot. Every layer has a clear job. Together they remove discretion from your process.

## The Five Layers

| Layer | Component | Job |
|-------|-----------|-----|
| L1 | CLAUDE.md / Risk.md | **Memory** — Rules, risk parameters, session behavior. Always loaded. |
| L2 | Playbooks / Skills | **Knowledge** — Setup library: breakout, pullback, mean-reversion. On-demand. |
| L3 | Hooks | **Guardrail** — Shell scripts that fire automatically around session events. |
| L4 | Subagents | **Delegation** — Specialist agents run in their own context and return one clean answer. |
| L5 | Plugins | **Distribution** — Bundle your entire system into a deployable package. |

---

## Which Layer Do You Need?

Read the user's request and identify the layer. Then read the matching reference file.

| User says... | Layer | Reference file |
|---|---|---|
| "Write my CLAUDE.md", "set my risk rules", "build my trading system", "session debrief", "rule violation" | **L1** | `references/layer1-memory.md` |
| "Write a breakout playbook", "load my pullback skill", "score this setup", "does this chart match my playbook" | **L2** | `references/layer2-knowledge.md` |
| "Set up PreMarket hook", "log my trade", "end of day review", "PostTrade script" | **L3** | `references/layer3-hooks.md` |
| "Deploy market researcher", "size this trade", "run risk manager", "analyze my journal" | **L4** | `references/layer4-subagents.md` |
| "Build a plugin", "package my system", "share with my team", "audit before shipping" | **L5** | `references/layer5-plugins.md` |

Once you identify the layer, **read the reference file in full** before responding. The reference files contain the templates, scripts, and worked examples — don't write from scratch without them.

---

## If the User Wants the Full System

When the user says something like "set up my full trading system" or "scaffold the trading dev kit", guide them through all five layers in order:

1. Start with L1 — ask for their trading style, risk tolerance, timeframe, max daily loss, and % per trade. Generate CLAUDE.md and Risk.md from their answers.
2. Ask which setups they trade (breakout, pullback, mean-reversion) → write the playbooks (L2).
3. Ask which instruments they trade and where they want logs stored → write the hook scripts (L3).
4. Confirm which subagents they need (market researcher / risk manager / journal analyzer) → write the agent definitions (L4).
5. Offer to bundle everything into a plugin.json for team distribution (L5).

Work through each layer one at a time. Confirm with the user before moving to the next.

---

## Core Principle

Rules over feelings. If it is not written, it does not exist in your system. Discretion loses. Systems win.

Every decision left to the moment is a decision made under pressure. This kit removes that pressure by making the decision before the pressure arrives.
