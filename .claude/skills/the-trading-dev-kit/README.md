# the-trading-dev-kit

A Claude Code skill that scaffolds a five-layer, rule-based trading system
(memory/rules, playbooks, hooks, subagents, plugin packaging).

Vendored verbatim (MIT licensed) from
[nutdnuy/the-trading-dev-kit](https://github.com/nutdnuy/the-trading-dev-kit)
into this repo's skill folder so it's available whenever this project is
opened in Claude Code.

## Use

Just talk to Claude about building a trading system — e.g. "set up my full
trading system", "build my CLAUDE.md for trading", "write a breakout
playbook", "set up PreMarket hook". `SKILL.md` routes the request to the
right `references/layer*.md` file automatically.

Running the skill generates real files outside this folder — a trading
`CLAUDE.md`/`Risk.md` at the repo root (or wherever you point it),
`.claude/agents/` subagent definitions, `.claude/hooks/` scripts, and trade
logs. Keep any private/live-account data (`Risk.local.md`, `logs/`,
`trades.log`) out of version control — see the root `.gitignore`.

## Source

- Upstream: https://github.com/nutdnuy/the-trading-dev-kit
- License: MIT
