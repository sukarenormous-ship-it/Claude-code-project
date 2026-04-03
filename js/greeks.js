// greeks.js - Black-Scholes pricing and Greeks calculations
// Used for: Section 5 (Greeks), Section 6 (Calendar/Diagonal), theoretical price curves

const Greeks = (() => {
  // ============================================================
  // Normal Distribution helpers
  // ============================================================

  // Cumulative normal distribution (Abramowitz & Stegun approximation)
  function normalCDF(x) {
    if (x < -10) return 0;
    if (x > 10) return 1;

    const a1 = 0.254829592;
    const a2 = -0.284496736;
    const a3 = 1.421413741;
    const a4 = -1.453152027;
    const a5 = 1.061405429;
    const p = 0.3275911;

    const sign = x < 0 ? -1 : 1;
    x = Math.abs(x);

    const t = 1.0 / (1.0 + p * x);
    const y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.exp(-x * x / 2);

    return 0.5 * (1.0 + sign * y);
  }

  // Normal probability density function
  function normalPDF(x) {
    return Math.exp(-0.5 * x * x) / Math.sqrt(2 * Math.PI);
  }

  // ============================================================
  // Black-Scholes d1 and d2
  // S = spot, K = strike, T = time to expiry (years), r = risk-free rate, sigma = volatility
  // ============================================================

  function d1(S, K, T, r, sigma) {
    T = Math.max(T, 0.0001); // Guard against T=0
    sigma = Math.max(sigma, 0.0001);
    return (Math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * Math.sqrt(T));
  }

  function d2(S, K, T, r, sigma) {
    return d1(S, K, T, r, sigma) - sigma * Math.sqrt(Math.max(T, 0.0001));
  }

  // ============================================================
  // Theoretical Option Price (Black-Scholes)
  // ============================================================

  function callPrice(S, K, T, r, sigma) {
    if (T <= 0.0001) return Math.max(S - K, 0); // At expiry = intrinsic
    const D1 = d1(S, K, T, r, sigma);
    const D2 = d2(S, K, T, r, sigma);
    return S * normalCDF(D1) - K * Math.exp(-r * T) * normalCDF(D2);
  }

  function putPrice(S, K, T, r, sigma) {
    if (T <= 0.0001) return Math.max(K - S, 0);
    const D1 = d1(S, K, T, r, sigma);
    const D2 = d2(S, K, T, r, sigma);
    return K * Math.exp(-r * T) * normalCDF(-D2) - S * normalCDF(-D1);
  }

  function theoreticalPrice(type, S, K, T, r, sigma) {
    return type === 'call' ? callPrice(S, K, T, r, sigma) : putPrice(S, K, T, r, sigma);
  }

  // ============================================================
  // Greeks
  // ============================================================

  // Delta: rate of change of option price w.r.t. underlying price
  function delta(type, S, K, T, r, sigma) {
    if (T <= 0.0001) {
      if (type === 'call') return S > K ? 1 : (S === K ? 0.5 : 0);
      return S < K ? -1 : (S === K ? -0.5 : 0);
    }
    const D1 = d1(S, K, T, r, sigma);
    return type === 'call' ? normalCDF(D1) : normalCDF(D1) - 1;
  }

  // Gamma: rate of change of delta w.r.t. underlying price
  function gamma(S, K, T, r, sigma) {
    if (T <= 0.0001) return 0;
    const D1 = d1(S, K, T, r, sigma);
    return normalPDF(D1) / (S * sigma * Math.sqrt(T));
  }

  // Theta: rate of change of option price w.r.t. time (per day)
  function theta(type, S, K, T, r, sigma) {
    if (T <= 0.0001) return 0;
    const D1 = d1(S, K, T, r, sigma);
    const D2 = d2(S, K, T, r, sigma);
    const sqrtT = Math.sqrt(T);

    const term1 = -(S * normalPDF(D1) * sigma) / (2 * sqrtT);

    if (type === 'call') {
      return (term1 - r * K * Math.exp(-r * T) * normalCDF(D2)) / 365;
    }
    return (term1 + r * K * Math.exp(-r * T) * normalCDF(-D2)) / 365;
  }

  // Vega: rate of change of option price w.r.t. volatility (per 1% change)
  function vega(S, K, T, r, sigma) {
    if (T <= 0.0001) return 0;
    const D1 = d1(S, K, T, r, sigma);
    return S * normalPDF(D1) * Math.sqrt(T) / 100;
  }

  // Rho: rate of change of option price w.r.t. interest rate
  function rho(type, S, K, T, r, sigma) {
    if (T <= 0.0001) return 0;
    const D2 = d2(S, K, T, r, sigma);
    if (type === 'call') {
      return K * T * Math.exp(-r * T) * normalCDF(D2) / 100;
    }
    return -K * T * Math.exp(-r * T) * normalCDF(-D2) / 100;
  }

  // ============================================================
  // P&L before expiry (theoretical value - cost)
  // ============================================================

  function theoreticalPnL(type, position, S, K, T, r, sigma, premium) {
    const price = theoreticalPrice(type, S, K, T, r, sigma);
    const pnl = position === 'long' ? price - premium : premium - price;
    return pnl;
  }

  // ============================================================
  // Data generators for charts
  // ============================================================

  function generatePnLCurve(type, position, K, premium, T, r, sigma, priceRange, numPoints) {
    numPoints = numPoints || 200;
    const step = (priceRange.max - priceRange.min) / (numPoints - 1);
    const labels = [];
    const data = [];

    for (let i = 0; i < numPoints; i++) {
      const S = priceRange.min + step * i;
      labels.push(Math.round(S * 100) / 100);
      data.push(Math.round(theoreticalPnL(type, position, S, K, T, r, sigma, premium) * 100) / 100);
    }

    return { labels, data };
  }

  function generateGreekCurve(greekFn, params, priceRange, numPoints) {
    numPoints = numPoints || 200;
    const step = (priceRange.max - priceRange.min) / (numPoints - 1);
    const labels = [];
    const data = [];

    for (let i = 0; i < numPoints; i++) {
      const S = priceRange.min + step * i;
      labels.push(Math.round(S * 100) / 100);
      const value = greekFn(S, params);
      data.push(Math.round(value * 10000) / 10000);
    }

    return { labels, data };
  }

  // Convenience: generate multiple time curves for a single option
  function generateTimeCurves(type, position, K, premium, r, sigma, priceRange, daysArray) {
    return daysArray.map(days => {
      const T = days / 365;
      const curve = generatePnLCurve(type, position, K, premium, T, r, sigma, priceRange);
      return { days, T, labels: curve.labels, data: curve.data };
    });
  }

  // ============================================================
  // Calendar Spread P&L
  // At evaluation date: short leg expired (intrinsic payoff), long leg = theoretical price
  // ============================================================

  function calendarSpreadPnL(S, K, T_long, r, sigma, premiumPaid) {
    // Short leg has expired: payoff = 0 (already settled)
    // Long leg still alive: value = theoretical price
    const longValue = callPrice(S, K, T_long, r, sigma);
    return longValue - premiumPaid;
  }

  // ============================================================
  // Default parameters
  // ============================================================

  const DEFAULTS = {
    r: 0.02,        // Risk-free rate 2%
    sigma: 0.25,    // Volatility 25%
    T: 30 / 365     // 30 days to expiry
  };

  // ============================================================
  // Public API
  // ============================================================

  return {
    normalCDF,
    normalPDF,
    d1,
    d2,
    callPrice,
    putPrice,
    theoreticalPrice,
    delta,
    gamma,
    theta,
    vega,
    rho,
    theoreticalPnL,
    generatePnLCurve,
    generateGreekCurve,
    generateTimeCurves,
    calendarSpreadPnL,
    DEFAULTS
  };
})();
