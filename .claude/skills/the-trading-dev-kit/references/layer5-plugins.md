# Layer 5 — Distribution Layer (Plugins)

Layer 5 turns your trading system into something you can ship. A plugin bundles your skills, agents, hooks, and commands into a single deployable package. Build it once. Install it on any machine. Share it with your team in one click. Every member of the team runs the same version of the same system.

**Two core components:**
- `plugin.json` — the manifest. Your system blueprint: what strategies are included, what rules are active, what triggers fire, what version is running. Versioned, locked, no guesswork.
- The store URL — where teammates can discover, install, and update your plugin instantly.

---

## What You Can Ship

| Folder | Contents |
|--------|----------|
| `skills/` | Your playbooks. The actual edge: breakout, pullback, mean-reversion definitions. |
| `agents/` | Specialist subagents: market-researcher, risk-manager, journal-analyzer. |
| `hooks/` | Automation scripts: PreMarket, PostTrade, EndOfDay. All triggers, ready to install. |
| `commands/` | Action shortcuts: enter, scale, cut, hedge, close — standardized across the team. |

---

## plugin.json Manifest Template

```json
{
  "name": "my-trading-system",
  "version": "1.0.0",
  "description": "My rule-based trading system — [YOUR STYLE] on [INSTRUMENTS]",
  "author": "[YOUR NAME]",
  "homepage": "https://github.com/[USERNAME]/[REPO]",

  "skills": [
    {
      "name": "breakout",
      "path": "skills/breakout.md",
      "description": "Momentum continuation setups"
    },
    {
      "name": "pullback",
      "path": "skills/pullback.md",
      "description": "Trend continuation entries"
    },
    {
      "name": "mean-reversion",
      "path": "skills/mean-reversion.md",
      "description": "Fade and reversal logic"
    }
  ],

  "agents": [
    {
      "name": "market-researcher",
      "path": "agents/market-researcher.md",
      "description": "News, catalysts, and market structure analysis"
    },
    {
      "name": "risk-manager",
      "path": "agents/risk-manager.md",
      "description": "Position sizing and downside modeling"
    },
    {
      "name": "journal-analyzer",
      "path": "agents/journal-analyzer.md",
      "description": "Trade review and pattern detection"
    }
  ],

  "hooks": [
    {
      "name": "PreMarket",
      "path": "hooks/PreMarket.sh",
      "trigger": "session_start",
      "description": "Load market context before the session"
    },
    {
      "name": "PostTrade",
      "path": "hooks/PostTrade.sh",
      "trigger": "post_execution",
      "description": "Log fills after execution"
    },
    {
      "name": "EndOfDay",
      "path": "hooks/EndOfDay.sh",
      "trigger": "session_end",
      "description": "Save state before the close"
    }
  ],

  "commands": [
    {
      "name": "enter",
      "path": "commands/enter.md",
      "description": "Execute entry according to active playbook"
    },
    {
      "name": "scale",
      "path": "commands/scale.md",
      "description": "Scale out at target levels"
    },
    {
      "name": "cut",
      "path": "commands/cut.md",
      "description": "Exit position immediately at market"
    },
    {
      "name": "risk-check",
      "path": "commands/risk-check.md",
      "description": "Verify position against Risk.md before adding size"
    }
  ],

  "requires": {
    "claude_code_version": ">=1.0.0"
  }
}
```

---

## Repository Structure for Distribution

Your plugin lives in a GitHub repository with this layout:

```
my-trading-system/
├── plugin.json              ← Manifest (required)
├── README.md                ← Install instructions + quick start
├── CHANGELOG.md             ← Version history
│
├── skills/
│   ├── breakout.md
│   ├── pullback.md
│   └── mean-reversion.md
│
├── agents/
│   ├── market-researcher.md
│   ├── risk-manager.md
│   └── journal-analyzer.md
│
├── hooks/
│   ├── PreMarket.sh
│   ├── PostTrade.sh
│   └── EndOfDay.sh
│
├── commands/
│   ├── enter.md
│   ├── scale.md
│   ├── cut.md
│   └── risk-check.md
│
├── CLAUDE.md                ← Global rules (committed)
├── Risk.md                  ← Risk rules (committed)
└── .gitignore               ← Excludes Risk.local.md
```

---

## Audit Checklist Before Shipping

Run this before publishing any version. The audit catches issues that will break a teammate's session.

```
□ All skill files are present and have valid YAML frontmatter
□ All agent files are present and have clear role definitions
□ All hook scripts are executable (chmod +x hooks/*.sh)
□ All hook scripts reference files that exist in the repo (no broken paths)
□ plugin.json version is incremented from the previous release
□ Risk.md is present and contains real numbers (not placeholders)
□ Risk.local.md is listed in .gitignore and NOT committed
□ No agent prompt conflicts with CLAUDE.md rules
□ No command bypasses or overrides Risk.md limits
□ README.md install instructions are accurate for the current version
□ All playbooks have invalidation conditions defined
□ CHANGELOG.md is updated with what changed in this version
```

**Audit prompt for Claude:**
```
Review my plugin before I publish it. Check for: missing risk rules, hooks that reference
non-existent files, agent prompts that conflict with CLAUDE.md, and any commands that
could bypass Risk.md limits.
```

---

## Packaging and Publishing

**Step 1: Bundle**
```bash
# Ensure hooks are executable
chmod +x hooks/*.sh

# Verify all files referenced in plugin.json exist
cat plugin.json | python3 -c "
import json, sys, os
p = json.load(sys.stdin)
for section in ['skills', 'agents', 'hooks', 'commands']:
    for item in p.get(section, []):
        path = item['path']
        if not os.path.exists(path):
            print(f'MISSING: {path}')
        else:
            print(f'OK: {path}')
"
```

**Step 2: Commit and tag**
```bash
git add .
git commit -m "release: v[VERSION] — [brief description of changes]"
git tag v[VERSION]
git push origin main --tags
```

**Step 3: Create GitHub release**
```bash
gh release create v[VERSION] \
  --title "v[VERSION] — [description]" \
  --notes "See CHANGELOG.md for full details." \
  --latest
```

**Step 4: Install on another machine**
```bash
# Teammate installs via Claude Code
claude plugin install https://github.com/[USERNAME]/[REPO]
```

---

## Starter Prompts

**Build a plugin manifest:**
```
Create a plugin.json manifest for my trading system. Include: system name, version 1.0.0,
list of active strategies from my skills/ folder, list of agents in my agents/ folder,
hooks that fire automatically, and the commands available to the team.
```

**Package for team distribution:**
```
Bundle my current system for team distribution. Include skills/, agents/, hooks/, and
commands/. Write a README that explains how to install, what each component does, and
what the team needs to configure before their first session.
```

**Audit plugin before shipping:**
```
Review my plugin before I publish it. Check for: missing risk rules, hooks that reference
non-existent files, agent prompts that conflict with CLAUDE.md, and any commands that
could bypass Risk.md limits.
```

**Version bump:**
```
Bump the plugin version to [X.Y.Z], update CHANGELOG.md with [description of changes],
and prepare the release commit message.
```
