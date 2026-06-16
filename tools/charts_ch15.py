"""Charts for Ch.15 — Dynamic Hedging with Kalman Filter."""
import numpy as np
from book_style import (save, style_axes, TEAL, NAVY, RED, GREEN, AMBER, BLUE,
                        GREY, RED_F, GREEN_F, BLUE_F, TEAL_F, AMBER_F)
import matplotlib.pyplot as plt


def chart_kalman_beta():
    """Chart: Kalman Filter β vs Static OLS with regime changes."""
    rng = np.random.default_rng(42)
    n = 300
    t = np.arange(n)

    # True β: regime shifts at t=100 and t=200
    true_beta = np.where(t < 100, 0.90, np.where(t < 200, 1.05, 0.85))

    # Observed returns (B drives A via β + noise)
    r_B = rng.normal(0, 0.005, n)
    v = rng.normal(0, 0.003, n)
    r_A = true_beta * r_B + v

    # ---------- Kalman Filter ----------
    Q = 2e-4   # process noise — allows fast tracking
    R = 9e-6   # observation noise (≈ var of v above)
    beta_kf = np.empty(n)
    P_kf = np.empty(n)
    beta_kf[0] = 1.0
    P_kf[0] = 1.0
    for i in range(1, n):
        # Predict
        beta_pred = beta_kf[i - 1]
        P_pred = P_kf[i - 1] + Q
        # Update
        rb = r_B[i]
        innovation = r_A[i] - beta_pred * rb
        S = rb ** 2 * P_pred + R
        K = P_pred * rb / S if S > 1e-12 else 0.0
        beta_kf[i] = beta_pred + K * innovation
        P_kf[i] = (1 - K * rb) * P_pred

    # ±1σ Kalman uncertainty band
    sigma_kf = np.sqrt(P_kf)

    # ---------- Rolling OLS β (window = 60) ----------
    window = 60
    beta_ols = np.full(n, np.nan)
    for i in range(window, n):
        rb_w = r_B[i - window:i]
        ra_w = r_A[i - window:i]
        if rb_w.std() > 1e-10:
            beta_ols[i] = np.dot(rb_w, ra_w) / np.dot(rb_w, rb_w)

    # ---------- Plot ----------
    fig, ax = plt.subplots(figsize=(7.4, 3.8))
    fig.patch.set_facecolor(BLUE_F)
    ax.set_facecolor(BLUE_F)

    # Kalman ±1σ band
    ax.fill_between(t, beta_kf - sigma_kf, beta_kf + sigma_kf,
                    color=TEAL, alpha=0.25, label=None, zorder=1)

    # True β (faint reference)
    ax.plot(t, true_beta, color=NAVY, lw=1.0, ls="--", alpha=0.4,
            label="True β (reference)", zorder=2)

    # Static OLS
    ax.plot(t, beta_ols, color=GREY, lw=2.0, ls="--",
            label="Rolling OLS (60-step)", zorder=3)

    # Kalman β
    ax.plot(t, beta_kf, color=TEAL, lw=2.0,
            label="Kalman β_t", zorder=4)

    # Regime change vertical lines
    for tc, label_x in zip([100, 200], [100, 200]):
        ax.axvline(tc, color=RED, lw=1.5, ls="--", zorder=5)
        ax.text(tc + 2, ax.get_ylim()[0] if ax.get_ylim()[0] > 0 else 0.80,
                "regime\nchange", fontsize=7.5, color=RED, va="bottom")

    style_axes(ax)
    ax.set_xlabel("t (steps)")
    ax.set_ylabel("β")
    ax.set_title("Kalman Filter β — adapts to regime shifts vs OLS lag")
    ax.legend(fontsize=9, loc="upper right")
    ax.set_xlim(0, n - 1)

    # Annotate regime change labels properly after axis is set
    ylim = ax.get_ylim()
    for tc in [100, 200]:
        ax.text(tc + 3, ylim[0] + 0.01 * (ylim[1] - ylim[0]),
                "regime\nchange", fontsize=7.5, color=RED, va="bottom")

    save(fig, "ch15-kalman-beta")


if __name__ == "__main__":
    chart_kalman_beta()
