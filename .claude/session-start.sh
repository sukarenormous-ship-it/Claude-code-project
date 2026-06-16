#!/bin/bash
# Session start hook — prints context summary for every new Claude Code session

BRANCH=$(git -C /home/user/Claude-code-project branch --show-current 2>/dev/null || echo "unknown")
UNCOMMITTED=$(git -C /home/user/Claude-code-project status --porcelain 2>/dev/null | wc -l | tr -d ' ')

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " Quant Trading Knowledge Base"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " Branch: $BRANCH"
if [ "$UNCOMMITTED" -gt "0" ]; then
  echo " Status: $UNCOMMITTED uncommitted file(s)"
else
  echo " Status: clean"
fi
echo ""
echo " 10 Books:"
echo "   grid · playground · arb · eye · math"
echo "   pm · python · statarb · vol · vp"
echo ""
echo " Production Skills:"
echo "   /build-book <prefix>         rebuild any book → PDF"
echo "   /review-book <prefix> [part] screenshot QA at A4 width"
echo "   /add-diagram <part> <type>   add MiniChart to HTML"
echo ""
echo " Trading Skills:"
echo "   /trading-plan <market>       full end-to-end plan"
echo "   /view-to-trade <belief>      5D belief → trade structure"
echo "   /regime-check <indicators>   classify R1–R7 + CRS score"
echo "   /game-filter <regime>        OS funnel → top 2–3 games"
echo "   /calc-wcl <game> <params>    WCL + Gate A/B check"
echo "   /size-position <method>      Martingale / Kelly / Bell"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
