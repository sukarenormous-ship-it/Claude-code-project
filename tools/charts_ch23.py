"""Charts for Ch.23 — Kalman Filter & t-Distribution."""
import numpy as np
from scipy import stats
from book_style import (save, style_axes, TEAL, NAVY, RED, GREEN, AMBER, BLUE,
                        GREY, RED_F, GREEN_F, BLUE_F, TEAL_F, AMBER_F)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


# ============================================================
# Chart 1 — Static vs Rolling vs Kalman beta_t comparison
# ============================================================
def chart_kalman_beta_compare():
    rng = np.random.default_rng(42)
    n = 200
    t = np.arange(n)

    # Simulate a "true" beta that has a regime change mid-way
    true_beta = np.ones(n) * 1.10
    # Regime change around step 80–130: beta drifts up to ~1.25 then back
    for i in range(n):
        if 80 <= i < 130:
            true_beta[i] = 1.10 + 0.15 * np.sin(np.pi * (i - 80) / 50)
        else:
            true_beta[i] = 1.10

    # Static beta (flat)
    static_beta = np.ones(n) * 1.10

    # Rolling beta (lagged, uses 30-bar window)
    window = 30
    rolling_beta = np.ones(n) * 1.10
    for i in range(window, n):
        # rolling OLS approximated by lagged true_beta mean
        rolling_beta[i] = true_beta[max(0, i - window):i].mean() + rng.normal(0, 0.005)

    # Kalman beta (adaptive)
    Q, R = 1e-5, 0.001
    beta_hat = 1.10
    P = 0.01
    kalman_beta = np.empty(n)
    rng2 = np.random.default_rng(7)
    for i in range(n):
        x_t = 0.03 + rng2.normal(0, 0.005)
        y_t = true_beta[i] * x_t + rng2.normal(0, 0.005)
        # Predict
        P_prior = P + Q
        # Update
        innovation = y_t - beta_hat * x_t
        S = x_t**2 * P_prior + R
        K = P_prior * x_t / S
        beta_hat = beta_hat + K * innovation
        P = (1 - K * x_t) * P_prior
        kalman_beta[i] = beta_hat

    fig, ax = plt.subplots(figsize=(7.4, 3.8))

    ax.plot(t, static_beta, color=GREY, lw=2, ls="--", label="Static OLS (ไม่เปลี่ยน)")
    ax.plot(t, rolling_beta, color=AMBER, lw=2, label="Rolling 30-bar (lag สูง)")
    ax.plot(t, kalman_beta, color=TEAL, lw=2.5, label="Kalman (adaptive)")

    # Annotate regime change
    ax.axvspan(80, 130, alpha=0.08, color=BLUE, label="Regime change (alt season)")
    ax.annotate("Alt season\nregime change", xy=(105, kalman_beta[105]),
                xytext=(115, 1.22), fontsize=8.5, color=BLUE,
                arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.0))

    ax.set_xlabel("เวลา (วัน)")
    ax.set_ylabel("β_t (hedge ratio)")
    ax.set_title("Static vs Rolling vs Kalman β_t — BTC/ETH")
    ax.set_ylim(1.03, 1.30)
    ax.legend(fontsize=9, loc="upper right")
    style_axes(ax)
    save(fig, "ch23-kalman-beta-compare")


# ============================================================
# Chart 2 — Kalman Predict-Update cycle diagram
# ============================================================
def chart_predict_update():
    fig, ax = plt.subplots(figsize=(7.4, 4.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.set_facecolor("#f9fafb")
    fig.patch.set_facecolor("#f9fafb")

    ax.set_title("Kalman Filter — Predict-Update Cycle", fontsize=13,
                 fontweight="bold", color=NAVY, pad=14)

    # PREDICT box
    predict_box = FancyBboxPatch((0.4, 2.5), 3.8, 2.8,
                                  boxstyle="round,pad=0.15",
                                  linewidth=2, edgecolor=BLUE,
                                  facecolor=BLUE_F)
    ax.add_patch(predict_box)
    ax.text(2.3, 5.05, "① PREDICT (prior)", ha="center", va="center",
            fontsize=11, fontweight="bold", color=BLUE)
    ax.text(0.7, 4.55, r"$\hat{\beta}_{t|t-1} = \hat{\beta}_{t-1}$", ha="left",
            va="center", fontsize=10, color=NAVY)
    ax.text(0.7, 4.10, "(β คาดว่าไม่เปลี่ยน)", ha="left", va="center",
            fontsize=8.5, color=GREY)
    ax.text(0.7, 3.65, r"$P_{t|t-1} = P_{t-1} + Q$", ha="left", va="center",
            fontsize=10, color=NAVY)
    ax.text(0.7, 3.20, "(uncertainty เพิ่มขึ้น)", ha="left", va="center",
            fontsize=8.5, color=GREY)
    ax.text(0.7, 2.75, "Q = process noise variance", ha="left", va="center",
            fontsize=8.5, color=GREY)

    # UPDATE box
    update_box = FancyBboxPatch((5.4, 1.5), 4.2, 3.8,
                                 boxstyle="round,pad=0.15",
                                 linewidth=2, edgecolor=GREEN,
                                 facecolor=GREEN_F)
    ax.add_patch(update_box)
    ax.text(7.5, 5.05, "② UPDATE (posterior)", ha="center", va="center",
            fontsize=11, fontweight="bold", color=GREEN)
    ax.text(5.6, 4.60, r"Innovation: $\nu_t = y_t - \hat{\beta}_{t|t-1} x_t$",
            ha="left", va="center", fontsize=9, color=NAVY)
    ax.text(5.6, 4.15, r"Kalman gain: $K_t = \frac{P_{t|t-1} x_t}{x_t^2 P_{t|t-1}+R}$",
            ha="left", va="center", fontsize=9, color=NAVY)
    ax.text(5.6, 3.65, r"Update β: $\hat{\beta}_t = \hat{\beta}_{t|t-1} + K_t \nu_t$",
            ha="left", va="center", fontsize=9, color=NAVY)
    ax.text(5.6, 3.15, r"Update P: $P_t = (1 - K_t x_t) P_{t|t-1}$",
            ha="left", va="center", fontsize=9, color=NAVY)
    ax.text(5.6, 2.65, "R = observation noise variance", ha="left", va="center",
            fontsize=8.5, color=GREY)
    ax.text(5.6, 2.20, r"$K_t \in [0,1]$: ถ่วงน้ำหนัก obs vs model",
            ha="left", va="center", fontsize=8.5, color=GREY)
    ax.text(5.6, 1.75, r"$K_t \to 1$: เชื่อ obs | $K_t \to 0$: เชื่อ model",
            ha="left", va="center", fontsize=8.5, color=GREY)

    # Arrow Predict → Update
    ax.annotate("", xy=(5.35, 3.9), xytext=(4.25, 3.9),
                arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.8))

    # Feedback arrow Update → Predict (loop)
    ax.annotate("", xy=(2.3, 2.45), xytext=(7.5, 1.45),
                arrowprops=dict(arrowstyle="-|>", color=TEAL, lw=1.5,
                                connectionstyle="arc3,rad=-0.35",
                                linestyle="dashed"))
    ax.text(4.8, 0.85, "loop ต่อไปทุก time step →", ha="center", va="center",
            fontsize=9, color=GREY, style="italic")

    style_axes(ax)
    save(fig, "ch23-predict-update")


# ============================================================
# Chart 3 — Kalman beta_t for BTC/ETH (200 hours)
# ============================================================
def chart_kalman_btceth():
    rng = np.random.default_rng(17)
    n = 200
    t = np.arange(n)
    ols_beta = 1.10

    # Simulate Kalman beta path with alt-season regime event around t=80–140
    Q, R = 1e-5, 0.001
    beta_hat = 1.10
    P = 0.01

    # True dynamic beta
    true_beta = np.ones(n) * 1.10
    for i in range(n):
        if 80 <= i < 140:
            true_beta[i] = 1.10 + 0.12 * np.sin(np.pi * (i - 80) / 60)

    kalman_beta = np.empty(n)
    for i in range(n):
        x_t = 0.03 + rng.normal(0, 0.004)
        y_t = true_beta[i] * x_t + rng.normal(0, 0.005)
        P_prior = P + Q
        innovation = y_t - beta_hat * x_t
        S = x_t**2 * P_prior + R
        K = P_prior * x_t / S
        beta_hat = beta_hat + K * innovation
        P = (1 - K * x_t) * P_prior
        kalman_beta[i] = beta_hat

    fig, ax = plt.subplots(figsize=(7.4, 3.6))

    ax.axhline(ols_beta, color=GREY, lw=1.5, ls="--", label="β_OLS = 1.10 (คงที่)")
    ax.plot(t, kalman_beta, color=TEAL, lw=2.5, label="β_Kalman (dynamic)")

    # Annotate alt-season event
    peak_idx = kalman_beta[80:140].argmax() + 80
    ax.annotate("Alt season event", xy=(peak_idx, kalman_beta[peak_idx]),
                xytext=(peak_idx - 25, kalman_beta[peak_idx] + 0.02),
                fontsize=8.5, color=BLUE,
                arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.0),
                bbox=dict(boxstyle="round,pad=0.2", facecolor=BLUE_F,
                          edgecolor=BLUE, lw=0.8))

    ax.set_xlabel("เวลา (ชั่วโมง)")
    ax.set_ylabel("β_t")
    ax.set_title("Kalman β_t — BTC/ETH (ตัวอย่าง 200 ชั่วโมง)")
    ax.legend(fontsize=9)
    style_axes(ax)
    save(fig, "ch23-kalman-btceth")


# ============================================================
# Chart 4 — Frequency Distribution: Normal vs Crypto Residuals (fat tails)
# ============================================================
def chart_fat_tails_hist():
    rng = np.random.default_rng(42)
    n = 5000

    # Simulate fat-tailed crypto residuals using t-distribution (nu=4)
    crypto_eps = stats.t.rvs(df=4, size=n, random_state=42)
    crypto_eps = crypto_eps / crypto_eps.std()   # standardize to σ=1

    x = np.linspace(-5.5, 5.5, 400)
    normal_pdf = stats.norm.pdf(x)
    tdist_pdf = stats.t.pdf(x, df=4)
    # scale t-pdf to have same σ=1 appearance
    tdist_pdf_scaled = stats.t.pdf(x * np.sqrt(2), df=4) * np.sqrt(2)

    fig, ax = plt.subplots(figsize=(7.4, 3.8))

    # histogram of crypto residuals
    ax.hist(crypto_eps, bins=80, density=True, color=TEAL, alpha=0.55,
            edgecolor="white", lw=0.3, label="Crypto ε (fat tails)")

    # Normal PDF overlay
    ax.plot(x, normal_pdf, color=GREY, lw=2.5, ls="--", label="Normal distribution")

    # Shade tail regions to highlight difference
    tail_mask_r = x > 2.0
    tail_mask_l = x < -2.0
    ax.fill_between(x[tail_mask_r], normal_pdf[tail_mask_r], alpha=0.20, color=RED)
    ax.fill_between(x[tail_mask_l], normal_pdf[tail_mask_l], alpha=0.20, color=RED)

    ax.annotate("Fat tails\n(crypto > Normal 5×)", xy=(3.8, 0.012),
                xytext=(4.0, 0.06), fontsize=8.5, color=RED,
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.0))
    ax.annotate("", xy=(-3.8, 0.012),
                xytext=(-4.5, 0.06),
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.0))

    ax.set_xlabel("ε / σ (standard deviations)")
    ax.set_ylabel("Probability density")
    ax.set_title("Frequency Distribution — Normal vs Crypto Residuals")
    ax.set_xlim(-5.5, 5.5)
    ax.set_ylim(0, 0.48)
    ax.legend(fontsize=9.5)
    style_axes(ax)
    save(fig, "ch23-fat-tails-hist")


# ============================================================
# Chart 5 — PDF comparison: Normal vs t(nu=10) vs t(nu=4)
# ============================================================
def chart_tdist_pdf():
    x = np.linspace(-5, 5, 500)
    normal_pdf = stats.norm.pdf(x)
    t10_pdf = stats.t.pdf(x, df=10)
    t4_pdf = stats.t.pdf(x, df=4)

    fig, ax = plt.subplots(figsize=(7.4, 3.8))

    ax.plot(x, normal_pdf, color=GREY, lw=2, label=r"Normal ($\nu \to \infty$)")
    ax.plot(x, t10_pdf, color=BLUE, lw=2, label=r"t($\nu$=10) — ใกล้ Normal")
    ax.plot(x, t4_pdf, color=TEAL, lw=2.5, label=r"t($\nu$=4) — fat tails ชัดเจน")

    # Mark critical values
    cv_normal = 1.96
    cv_t4 = stats.t.ppf(0.975, df=4)  # ~2.776
    ax.axvline(cv_normal, color=RED, lw=1.2, ls=":", alpha=0.7)
    ax.axvline(-cv_normal, color=RED, lw=1.2, ls=":", alpha=0.7)
    ax.axvline(cv_t4, color=RED, lw=1.8, ls="--", alpha=0.9)
    ax.axvline(-cv_t4, color=RED, lw=1.8, ls="--", alpha=0.9)

    ax.text(cv_normal + 0.05, 0.36, "z=1.96", fontsize=8, color=RED, rotation=90)
    ax.text(cv_t4 + 0.05, 0.30, f"t={cv_t4:.2f}", fontsize=8, color=RED, rotation=90)

    # Shade fat tail area between normal critical value and t(4) critical value
    mask = (x > cv_normal) & (x < cv_t4 + 0.5)
    ax.fill_between(x[mask], t4_pdf[mask], normal_pdf[mask],
                    alpha=0.25, color=RED, label="Extra fat tail area")

    ax.set_xlabel("x")
    ax.set_ylabel("Probability density")
    ax.set_title(r"PDF เปรียบเทียบ: Normal vs t($\nu$=10) vs t($\nu$=4)")
    ax.set_xlim(-5, 5)
    ax.set_ylim(0, 0.43)
    ax.legend(fontsize=9, loc="upper right")
    style_axes(ax)
    save(fig, "ch23-tdist-pdf")


# ============================================================
# Chart 6 — Pipeline: Kalman + t-distribution (5 steps)
# ============================================================
def chart_pipeline():
    fig, ax = plt.subplots(figsize=(7.4, 3.5))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 5)
    ax.axis("off")
    ax.set_facecolor("#f9fafb")
    fig.patch.set_facecolor("#f9fafb")

    ax.set_title("Pipeline: Kalman + t-distribution (5 steps)", fontsize=12,
                 fontweight="bold", color=NAVY, pad=10)

    # Box definitions: (x_left, y_bottom, width, height, face, edge, label_title, lines)
    boxes = [
        (0.1, 2.2, 2.2, 1.8, BLUE_F, BLUE,
         "① Init",
         ["OLS β₀, Q, R", "MLE ν (training)"]),
        (2.6, 2.2, 2.4, 1.8, TEAL_F, TEAL,
         "② Kalman",
         ["β_t (dynamic)", "ε_t = y_t − β_t·x_t"]),
        (5.3, 2.2, 2.2, 1.8, AMBER_F, AMBER,
         "③ σ_t",
         ["rolling std(ε)", "z_t = ε_t/σ_t"]),
        (7.8, 2.2, 2.4, 1.8, "#f5f3ff", "#7c3aed",
         "④ t-threshold",
         [r"t_{α/2}(ν) แทน 1.96", "ν จาก MLE"]),
        (10.5, 2.2, 3.3, 1.8, GREEN_F, GREEN,
         "⑤ Signal",
         ["|z_t| ≥ t_{α/2} → Entry", "|z_t| ≤ 0.5 → Exit"]),
    ]

    for (xl, yb, w, h, fc, ec, title, lines) in boxes:
        box = FancyBboxPatch((xl, yb), w, h, boxstyle="round,pad=0.1",
                              linewidth=1.5, edgecolor=ec, facecolor=fc)
        ax.add_patch(box)
        ax.text(xl + w/2, yb + h - 0.3, title, ha="center", va="center",
                fontsize=8.5, fontweight="bold", color=ec)
        for i, line in enumerate(lines):
            ax.text(xl + w/2, yb + h - 0.75 - i*0.5, line,
                    ha="center", va="center", fontsize=7.5, color=NAVY)

    # Arrows between boxes
    arrow_pairs = [
        (2.30, 3.1, 2.55, 3.1),
        (5.00, 3.1, 5.25, 3.1),
        (7.50, 3.1, 7.75, 3.1),
        (10.20, 3.1, 10.45, 3.1),
    ]
    for (x1, y1, x2, y2) in arrow_pairs:
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.5))

    # Feedback arrow from step 2 back to step 1
    ax.annotate("", xy=(1.2, 2.15), xytext=(3.8, 2.15),
                arrowprops=dict(arrowstyle="-|>", color=TEAL, lw=1.3,
                                connectionstyle="arc3,rad=0.4",
                                linestyle="dashed"))
    ax.text(2.5, 1.4, "β_{t+1} ← β_t", ha="center", va="center",
            fontsize=8, color=TEAL)

    # Guard box
    guard_box = FancyBboxPatch((2.5, 0.2), 5.2, 0.85, boxstyle="round,pad=0.08",
                                linewidth=1.2, edgecolor=RED, facecolor=RED_F)
    ax.add_patch(guard_box)
    ax.text(5.1, 0.72, "Guard: Skip entry ถ้า K_t > 0.3 (β กำลัง update เร็ว)",
            ha="center", va="center", fontsize=7.5, fontweight="bold", color=RED)
    ax.text(5.1, 0.42, "ป้องกัน trade ระหว่าง regime transition",
            ha="center", va="center", fontsize=7, color=GREY)

    style_axes(ax)
    save(fig, "ch23-pipeline")


if __name__ == "__main__":
    chart_kalman_beta_compare()
    chart_predict_update()
    chart_kalman_btceth()
    chart_fat_tails_hist()
    chart_tdist_pdf()
    chart_pipeline()
    print("All ch23 charts saved.")
