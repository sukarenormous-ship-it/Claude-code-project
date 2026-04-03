// payoff.js - Pure math: payoff calculations for all option strategies
// No side effects, no DOM manipulation

const Payoff = (() => {
  // ============================================================
  // Single Position Payoff Functions (at expiry)
  // ============================================================

  function longCall(spot, strike, premium) {
    return Math.max(spot - strike, 0) - premium;
  }

  function shortCall(spot, strike, premium) {
    return -longCall(spot, strike, premium);
  }

  function longPut(spot, strike, premium) {
    return Math.max(strike - spot, 0) - premium;
  }

  function shortPut(spot, strike, premium) {
    return -longPut(spot, strike, premium);
  }

  function longStock(spot, entryPrice) {
    return spot - entryPrice;
  }

  function shortStock(spot, entryPrice) {
    return entryPrice - spot;
  }

  function bond(faceValue) {
    // Bond payoff is constant regardless of spot price
    return faceValue;
  }

  // ============================================================
  // Unified Leg Calculator
  // leg = { type: 'call'|'put'|'stock'|'bond', position: 'long'|'short',
  //         strike, premium, entryPrice, faceValue, quantity }
  // ============================================================

  function calculateLeg(leg, spot) {
    const qty = leg.quantity || 1;
    let payoff = 0;

    switch (leg.type) {
      case 'call':
        payoff = leg.position === 'long'
          ? longCall(spot, leg.strike, leg.premium)
          : shortCall(spot, leg.strike, leg.premium);
        break;
      case 'put':
        payoff = leg.position === 'long'
          ? longPut(spot, leg.strike, leg.premium)
          : shortPut(spot, leg.strike, leg.premium);
        break;
      case 'stock':
        payoff = leg.position === 'long'
          ? longStock(spot, leg.entryPrice || leg.strike || 100)
          : shortStock(spot, leg.entryPrice || leg.strike || 100);
        break;
      case 'bond':
        payoff = bond(leg.faceValue || leg.strike || 0);
        break;
      default:
        payoff = 0;
    }

    return payoff * qty;
  }

  // ============================================================
  // Strategy Calculator (sum of all legs)
  // ============================================================

  function calculateStrategy(legs, spot) {
    return legs.reduce((sum, leg) => sum + calculateLeg(leg, spot), 0);
  }

  // ============================================================
  // Data Generation
  // ============================================================

  function getPriceRange(legs, padding) {
    padding = padding || 0.5;
    const strikes = [];

    legs.forEach(leg => {
      if (leg.strike !== undefined) strikes.push(leg.strike);
      if (leg.entryPrice !== undefined) strikes.push(leg.entryPrice);
    });

    if (strikes.length === 0) return { min: 50, max: 150 };

    const minStrike = Math.min(...strikes);
    const maxStrike = Math.max(...strikes);
    const range = maxStrike - minStrike || minStrike * 0.5;

    return {
      min: Math.max(0, minStrike - range * padding),
      max: maxStrike + range * padding
    };
  }

  function generatePayoffData(legs, numPoints, customRange) {
    numPoints = numPoints || 200;
    const range = customRange || getPriceRange(legs);
    const step = (range.max - range.min) / (numPoints - 1);
    const labels = [];
    const data = [];
    const legData = legs.map(() => []);

    for (let i = 0; i < numPoints; i++) {
      const spot = range.min + step * i;
      labels.push(Math.round(spot * 100) / 100);
      data.push(Math.round(calculateStrategy(legs, spot) * 100) / 100);

      // Individual leg payoffs
      legs.forEach((leg, idx) => {
        legData[idx].push(Math.round(calculateLeg(leg, spot) * 100) / 100);
      });
    }

    return { labels, data, legData, range };
  }

  // ============================================================
  // Analytics: Break-even, Max Profit, Max Loss
  // ============================================================

  function findBreakevens(legs, range) {
    range = range || getPriceRange(legs);
    const points = 1000;
    const step = (range.max - range.min) / points;
    const breakevens = [];

    let prevPayoff = calculateStrategy(legs, range.min);

    for (let i = 1; i <= points; i++) {
      const spot = range.min + step * i;
      const payoff = calculateStrategy(legs, spot);

      // Sign change = crossing zero
      if ((prevPayoff < 0 && payoff >= 0) || (prevPayoff >= 0 && payoff < 0)) {
        // Linear interpolation for precision
        const ratio = Math.abs(prevPayoff) / (Math.abs(prevPayoff) + Math.abs(payoff));
        const breakeven = (spot - step) + step * ratio;
        breakevens.push(Math.round(breakeven * 100) / 100);
      }

      prevPayoff = payoff;
    }

    return breakevens;
  }

  function findMaxProfit(legs, range) {
    range = range || getPriceRange(legs, 1.0);
    const points = 1000;
    const step = (range.max - range.min) / points;
    let maxProfit = -Infinity;

    for (let i = 0; i <= points; i++) {
      const spot = range.min + step * i;
      const payoff = calculateStrategy(legs, spot);
      if (payoff > maxProfit) maxProfit = payoff;
    }

    // Check extreme right edge - if still increasing, unlimited
    const farRight = calculateStrategy(legs, range.max * 2);
    const nearRight = calculateStrategy(legs, range.max * 1.9);
    if (farRight > nearRight + 0.01 && farRight > maxProfit) {
      return { value: Infinity, label: 'ไม่จำกัด' };
    }

    return { value: Math.round(maxProfit * 100) / 100, label: maxProfit.toFixed(2) };
  }

  function findMaxLoss(legs, range) {
    range = range || getPriceRange(legs, 1.0);
    const points = 1000;
    const step = (range.max - range.min) / points;
    let maxLoss = Infinity;

    for (let i = 0; i <= points; i++) {
      const spot = range.min + step * i;
      const payoff = calculateStrategy(legs, spot);
      if (payoff < maxLoss) maxLoss = payoff;
    }

    // Check extreme edges for unlimited loss
    const farRight = calculateStrategy(legs, range.max * 2);
    const nearRight = calculateStrategy(legs, range.max * 1.9);
    const farLeft = calculateStrategy(legs, Math.max(0.01, range.min * 0.1));
    const nearLeft = calculateStrategy(legs, Math.max(0.01, range.min * 0.2));

    if ((farRight < nearRight - 0.01 && farRight < maxLoss) ||
        (farLeft < nearLeft - 0.01 && farLeft < maxLoss)) {
      return { value: -Infinity, label: 'ไม่จำกัด' };
    }

    return { value: Math.round(maxLoss * 100) / 100, label: maxLoss.toFixed(2) };
  }

  // ============================================================
  // Summary generator
  // ============================================================

  function getSummary(legs) {
    const range = getPriceRange(legs, 1.0);
    return {
      breakevens: findBreakevens(legs, range),
      maxProfit: findMaxProfit(legs, range),
      maxLoss: findMaxLoss(legs, range)
    };
  }

  // ============================================================
  // Predefined Strategy Builders
  // ============================================================

  function buildStrategy(name, params) {
    const p = params;
    const strategies = {
      longCall: [
        { type: 'call', position: 'long', strike: p.strike, premium: p.premium, quantity: 1 }
      ],
      shortCall: [
        { type: 'call', position: 'short', strike: p.strike, premium: p.premium, quantity: 1 }
      ],
      longPut: [
        { type: 'put', position: 'long', strike: p.strike, premium: p.premium, quantity: 1 }
      ],
      shortPut: [
        { type: 'put', position: 'short', strike: p.strike, premium: p.premium, quantity: 1 }
      ],
      bullCallSpread: [
        { type: 'call', position: 'long', strike: p.strike1, premium: p.premium1, quantity: 1 },
        { type: 'call', position: 'short', strike: p.strike2, premium: p.premium2, quantity: 1 }
      ],
      bearPutSpread: [
        { type: 'put', position: 'long', strike: p.strike2, premium: p.premium2, quantity: 1 },
        { type: 'put', position: 'short', strike: p.strike1, premium: p.premium1, quantity: 1 }
      ],
      longStraddle: [
        { type: 'call', position: 'long', strike: p.strike, premium: p.premiumCall, quantity: 1 },
        { type: 'put', position: 'long', strike: p.strike, premium: p.premiumPut, quantity: 1 }
      ],
      longStrangle: [
        { type: 'call', position: 'long', strike: p.strike2, premium: p.premiumCall, quantity: 1 },
        { type: 'put', position: 'long', strike: p.strike1, premium: p.premiumPut, quantity: 1 }
      ],
      ironCondor: [
        { type: 'put', position: 'long', strike: p.strike1, premium: p.premium1, quantity: 1 },
        { type: 'put', position: 'short', strike: p.strike2, premium: p.premium2, quantity: 1 },
        { type: 'call', position: 'short', strike: p.strike3, premium: p.premium3, quantity: 1 },
        { type: 'call', position: 'long', strike: p.strike4, premium: p.premium4, quantity: 1 }
      ],
      butterflySpread: [
        { type: 'call', position: 'long', strike: p.strike1, premium: p.premium1, quantity: 1 },
        { type: 'call', position: 'short', strike: p.strike2, premium: p.premium2, quantity: 2 },
        { type: 'call', position: 'long', strike: p.strike3, premium: p.premium3, quantity: 1 }
      ],
      ratioCallSpread: [
        { type: 'call', position: 'long', strike: p.strike1, premium: p.premium1, quantity: 1 },
        { type: 'call', position: 'short', strike: p.strike2, premium: p.premium2, quantity: p.ratio || 2 }
      ],
      backRatioCallSpread: [
        { type: 'call', position: 'short', strike: p.strike1, premium: p.premium1, quantity: 1 },
        { type: 'call', position: 'long', strike: p.strike2, premium: p.premium2, quantity: p.ratio || 2 }
      ],
      protectivePut: [
        { type: 'stock', position: 'long', entryPrice: p.stockPrice, quantity: 1 },
        { type: 'put', position: 'long', strike: p.strike, premium: p.premium, quantity: 1 }
      ],
      coveredCall: [
        { type: 'stock', position: 'long', entryPrice: p.stockPrice, quantity: 1 },
        { type: 'call', position: 'short', strike: p.strike, premium: p.premium, quantity: 1 }
      ],
      collar: [
        { type: 'stock', position: 'long', entryPrice: p.stockPrice, quantity: 1 },
        { type: 'put', position: 'long', strike: p.strike1, premium: p.premium1, quantity: 1 },
        { type: 'call', position: 'short', strike: p.strike2, premium: p.premium2, quantity: 1 }
      ],
      syntheticLongStock: [
        { type: 'call', position: 'long', strike: p.strike, premium: p.premiumCall, quantity: 1 },
        { type: 'put', position: 'short', strike: p.strike, premium: p.premiumPut, quantity: 1 }
      ],
      putCallParityLeft: [
        { type: 'call', position: 'long', strike: p.strike, premium: p.premiumCall, quantity: 1 },
        { type: 'bond', faceValue: p.strike, quantity: 1 }
      ],
      putCallParityRight: [
        { type: 'put', position: 'long', strike: p.strike, premium: p.premiumPut, quantity: 1 },
        { type: 'stock', position: 'long', entryPrice: p.stockPrice || p.strike, quantity: 1 }
      ]
    };

    return strategies[name] || [];
  }

  // ============================================================
  // Public API
  // ============================================================

  return {
    longCall,
    shortCall,
    longPut,
    shortPut,
    longStock,
    shortStock,
    bond,
    calculateLeg,
    calculateStrategy,
    generatePayoffData,
    getPriceRange,
    findBreakevens,
    findMaxProfit,
    findMaxLoss,
    getSummary,
    buildStrategy
  };
})();
