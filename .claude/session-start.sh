#!/bin/bash
# Session start hook — prints context for Claude at the beginning of each session

BRANCH=$(git -C /home/user/Claude-code-project branch --show-current 2>/dev/null || echo "unknown")
UNCOMMITTED=$(git -C /home/user/Claude-code-project status --porcelain 2>/dev/null | wc -l | tr -d ' ')

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Quant Trading Knowledge Base"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Branch : $BRANCH"
if [ "$UNCOMMITTED" -gt "0" ]; then
  echo "  ⚠  $UNCOMMITTED uncommitted file(s)"
fi
echo ""
echo "  Books  : grid | playground | arb | eye | math"
echo "           pm   | python     | statarb | vol | vp"
echo ""
echo "  Book skills:"
echo "    /build-book <prefix>            — rebuild PDF"
echo "    /review-book <prefix> [part]    — visual QA"
echo "    /add-diagram <part> <type> <desc>"
echo ""
echo "  Trading skills:"
echo "    /trading-plan  <market>         — full end-to-end plan"
echo "    /view-to-trade <belief>         — belief → payoff → trade"
echo "    /regime-check  hurst=X adx=Y ivr=Z"
echo "    /game-filter   R1               — OS funnel → top games"
echo "    /calc-wcl      <game> <params>  — WCL + Gate check"
echo "    /size-position <method> <params>"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
