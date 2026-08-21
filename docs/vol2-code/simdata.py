"""
Synthetic data generators for the Practical Quant: Stat Arb notebooks.

IMPORTANT — why simulated data, not real market data:
This sandboxed environment's network policy blocks financial data providers
(Yahoo Finance, Stooq, etc. all return 403 at the egress proxy). Rather than
fabricate or misrepresent real prices, every notebook in vol2-code/ uses
SIMULATED price series with a fully documented, known data-generating process
(DGP). This is disclosed in every notebook.

This is not just a workaround — for teaching estimation methods it is
arguably *better*: because the true beta / true cointegration residual /
true factor loadings are known by construction, we can measure each
estimator's bias and error against ground truth, which real market data
never gives you.

Reader who wants to re-run these against real prices: swap `load_prices()`
in each notebook for your own data loader (e.g. a broker API or a local
CSV) — the estimation code does not care where the prices came from.

All generators take an explicit `seed` and are otherwise pure functions of
their parameters, so results are exactly reproducible.
"""
import numpy as np
import pandas as pd


def simulate_cointegrated_pair(
    n=750,
    beta_true=1.3,
    beta_drift="const",       # "const" | "sine" | "randomwalk" | "meanrevert"
    beta_drift_scale=0.15,    # amplitude / step-scale of the drift
    beta_mr_theta=0.02,       # (meanrevert only) speed beta is pulled back to beta_true
    beta_mr_sigma=0.03,       # (meanrevert only) daily shock size to beta
    ou_theta=0.05,            # OU mean-reversion speed of the true spread
    ou_sigma=0.8,             # OU volatility of the true spread
    price_b_vol=0.9,          # daily vol of the random-walk driver (asset B), in price units
    price0_b=170.0,           # starting price of asset B (loosely PEP-scale)
    alpha=0.0,                # intercept
    obs_noise_a=0.15,         # observation (microstructure) noise std, asset A
    obs_noise_b=0.15,         # observation noise std, asset B
    seed=42,
):
    """
    Simulates two price series (A, B) that are genuinely cointegrated by
    construction:

        B_t          = random walk                      (the "driver")
        beta_t       = true, time-varying hedge ratio
        spread_t     = OU process                        (the tradeable residual)
        A_true_t     = alpha + beta_t * B_t + spread_t
        A_obs_t      = A_true_t + noise_a_t               (observed price, noisy)
        B_obs_t      = B_t     + noise_b_t                (observed price, noisy)

    Returns a DataFrame with columns:
        B_true, A_true, B_obs, A_obs, beta_true, spread_true
    """
    rng = np.random.default_rng(seed)

    # 1. driver asset B: random walk in price space
    b_steps = rng.normal(0, price_b_vol, n)
    B_true = price0_b + np.cumsum(b_steps)

    # 2. true time-varying beta path
    if beta_drift == "const":
        beta_t = np.full(n, beta_true)
    elif beta_drift == "sine":
        beta_t = beta_true + beta_drift_scale * np.sin(2 * np.pi * np.arange(n) / (n / 2))
    elif beta_drift == "randomwalk":
        steps = rng.normal(0, beta_drift_scale / np.sqrt(n), n)
        beta_t = beta_true + np.cumsum(steps)
    elif beta_drift == "meanrevert":
        # AR(1)/OU-style: beta has a "home" (beta_true) it is pulled back to
        beta_t = np.empty(n)
        beta_t[0] = beta_true
        for t in range(1, n):
            beta_t[t] = beta_t[t - 1] + beta_mr_theta * (beta_true - beta_t[t - 1]) + beta_mr_sigma * rng.normal()
    else:
        raise ValueError("unknown beta_drift")

    # 3. true spread: Ornstein-Uhlenbeck (mean-reverting), this IS the residual
    spread = np.zeros(n)
    for t in range(1, n):
        spread[t] = spread[t - 1] + ou_theta * (0 - spread[t - 1]) + ou_sigma * rng.normal()

    # 4. true price of A (noiseless)
    A_true = alpha + beta_t * B_true + spread

    # 5. observed (noisy) prices — this noise is what creates EIV in return-space
    A_obs = A_true + rng.normal(0, obs_noise_a, n)
    B_obs = B_true + rng.normal(0, obs_noise_b, n)

    idx = pd.RangeIndex(n, name="t")
    return pd.DataFrame({
        "B_true": B_true, "A_true": A_true,
        "B_obs": B_obs, "A_obs": A_obs,
        "beta_true": beta_t, "spread_true": spread,
    }, index=idx)


def simulate_factor_universe(
    n_assets=40,
    n_days=500,
    n_factors=2,
    factor_vol=(1.0, 0.5),      # daily vol of each common factor
    idio_ou_theta=0.06,         # mean-reversion speed of idiosyncratic residual
    idio_ou_sigma=(0.3, 0.9),   # range of idio residual vol across assets (uniform)
    loading_range=(0.4, 1.6),   # range of factor loadings across assets (uniform)
    seed=7,
):
    """
    Simulates a cross-sectional universe of `n_assets` return series driven by
    `n_factors` common factors plus an idiosyncratic OU residual per asset:

        r_i,t = sum_k( beta_i,k * F_k,t ) + eps_i,t
        eps_i,t follows an OU process (mean-reverting "idiosyncratic residual")

    This is the ground truth for Part III (residual/factor stat arb): the
    factor loadings and the idiosyncratic residual are both known exactly,
    so we can check whether PCA/regression recovers them and whether the
    s-score signal on the *true* residual would have been profitable in a
    zero-cost, frictionless sense (a sanity upper bound, not a claim about
    real trading — cost/friction is Part VIII's job, not this notebook's).

    Returns (returns_df, loadings_true, factors_df, idio_true_df)
    """
    rng = np.random.default_rng(seed)

    # common factors: independent random walks in return-space (iid returns)
    factors = np.column_stack([
        rng.normal(0, factor_vol[k % len(factor_vol)], n_days) for k in range(n_factors)
    ])
    factors_df = pd.DataFrame(factors, columns=[f"F{k+1}" for k in range(n_factors)])

    loadings = rng.uniform(loading_range[0], loading_range[1], size=(n_assets, n_factors))
    # random sign flips so not everything is a pure "long the factor" bet
    loadings *= rng.choice([-1, 1], size=(n_assets, n_factors), p=[0.25, 0.75])

    idio_sigmas = rng.uniform(idio_ou_sigma[0], idio_ou_sigma[1], n_assets)
    idio = np.zeros((n_days, n_assets))
    for i in range(n_assets):
        for t in range(1, n_days):
            idio[t, i] = idio[t - 1, i] + idio_ou_theta * (0 - idio[t - 1, i]) + idio_sigmas[i] * rng.normal()
    idio_df = pd.DataFrame(idio, columns=[f"A{i+1}" for i in range(n_assets)])

    common = factors_df.values @ loadings.T
    returns = pd.DataFrame(common, columns=idio_df.columns) + idio_df

    loadings_true = pd.DataFrame(loadings, index=idio_df.columns,
                                  columns=[f"F{k+1}" for k in range(n_factors)])
    return returns, loadings_true, factors_df, idio_df
