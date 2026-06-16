"""Charts for Ch.6 — Z-score & Entry Signal."""
import numpy as np
from book_style import (save, style_axes, TEAL, NAVY, RED, GREEN, AMBER, BLUE,
                        GREY, RED_F, AMBER_F, GREEN_F, TEAL_F, BLUE_F)
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy.stats import norm


def ou_path(n, kappa, theta, sigma, x0, seed):
    rng = np.random.default_rng(seed)
    x = np.empty(n)
    x[0] = x0
    for t in range(1, n):
        x[t] = x[t - 1] + kappa * (theta - x[t - 1]) + sigma * rng.standard_normal()
    return x


# ============================================================
# Chart 1 — Z-score signal (2 panels: spread + z-score)
# ============================================================
def chart_zscore_signal():
    n = 200
    kappa, theta, sigma = 0.06, 0.0, 1.0
    sd = sigma / np.sqrt(2 * kappa)          # stationary std ≈ 2.89
    x = ou_path(n, kappa, theta, sigma, x0=0.0, seed=7)
    t = np.arange(n)

    # rolling z-score: (x - rolling_mean) / rolling_std, window=30
    win = 30
    roll_mean = np.full(n, np.nan)
    roll_std  = np.full(n, np.nan)
    for i in range(win - 1, n):
        chunk = x[i - win + 1 : i + 1]
        roll_mean[i] = chunk.mean()
        roll_std[i]  = chunk.std(ddof=1)

    z = (x - roll_mean) / roll_std           # shape (n,), nan for first win-1 pts

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.5, 4.0), sharex=True)

    # ----- Top panel: spread ε -----
    ax1.axhline(0,      color=TEAL,  lw=1.4, ls="--", alpha=0.7)
    ax1.axhline( 2*sd,  color=AMBER, lw=1.0, ls=":",  alpha=0.8, label="±2σ")
    ax1.axhline(-2*sd,  color=AMBER, lw=1.0, ls=":",  alpha=0.8)
    ax1.fill_between(t,  2*sd,  3.5*sd, color=AMBER_F, alpha=0.5)
    ax1.fill_between(t, -3.5*sd, -2*sd, color=AMBER_F, alpha=0.5)
    ax1.plot(t, x, color=NAVY, lw=1.6, label="ε (spread)")
    ax1.set_ylabel("ε (spread)")
    ax1.set_title("Spread ε และ Z-score — Entry Signal")
    ax1.legend(loc="upper right", fontsize=8.5)
    ax1.set_xlim(0, n - 1)
    style_axes(ax1)

    # ----- Bottom panel: z-score, colour-coded -----
    valid = ~np.isnan(z)
    tv = t[valid]
    zv = z[valid]

    # Segment into colour bands
    red_mask   = np.abs(zv) > 2
    green_mask = np.abs(zv) < 1
    navy_mask  = ~red_mask & ~green_mask

    # Reference lines
    ax2.axhline(0,    color=TEAL,  lw=1.2, ls="--", alpha=0.7)
    ax2.axhline( 2,   color=AMBER, lw=1.1, ls=":",  alpha=0.9, label="±2 (Entry)")
    ax2.axhline(-2,   color=AMBER, lw=1.1, ls=":",  alpha=0.9)
    ax2.axhline( 3,   color=RED,   lw=1.0, ls=":",  alpha=0.8, label="±3 (Stop)")
    ax2.axhline(-3,   color=RED,   lw=1.0, ls=":",  alpha=0.8)

    # Draw coloured z-score line segment by segment
    def draw_segments(ax, tv, zv, mask, color, lw=1.8):
        """Draw line only where mask is True, breaking on False segments."""
        seg_t, seg_z = [], []
        for i in range(len(tv)):
            if mask[i]:
                seg_t.append(tv[i])
                seg_z.append(zv[i])
            else:
                if seg_t:
                    ax.plot(seg_t, seg_z, color=color, lw=lw, solid_capstyle="round")
                    seg_t, seg_z = [], []
        if seg_t:
            ax.plot(seg_t, seg_z, color=color, lw=lw, solid_capstyle="round")

    draw_segments(ax2, tv, zv, navy_mask,  NAVY,  lw=1.8)
    draw_segments(ax2, tv, zv, green_mask, GREEN, lw=2.0)
    draw_segments(ax2, tv, zv, red_mask,   RED,   lw=2.0)

    # Legend handles
    legend_handles = [
        Line2D([0], [0], color=RED,   lw=2, label="|z|>2 (Entry zone)"),
        Line2D([0], [0], color=GREEN, lw=2, label="|z|<1 (Exit zone)"),
        Line2D([0], [0], color=NAVY,  lw=2, label="1≤|z|≤2 (Hold)"),
        Line2D([0], [0], color=AMBER, lw=1, ls=":", label="±2 (Entry)"),
        Line2D([0], [0], color=RED,   lw=1, ls=":", label="±3 (Stop)"),
    ]
    ax2.legend(handles=legend_handles, loc="upper right", fontsize=8, ncol=2)
    ax2.set_ylabel("z-score")
    ax2.set_xlabel("เวลา t (bars)")
    ax2.set_xlim(0, n - 1)
    ax2.set_ylim(-5, 5)
    style_axes(ax2)

    fig.tight_layout(h_pad=0.5)
    save(fig, "ch6-zscore-signal")


# ============================================================
# Chart 2 — Z-score distribution vs Normal(0,1)
# ============================================================
def chart_zscore_distribution():
    # Simulate a longer OU path to collect ~1000 z-scores
    n_long = 1500
    win = 30
    kappa, sigma = 0.06, 1.0
    x = ou_path(n_long, kappa, 0.0, sigma, x0=0.0, seed=42)

    roll_mean = np.array([x[max(0, i - win + 1): i + 1].mean() for i in range(n_long)])
    roll_std  = np.array([x[max(0, i - win + 1): i + 1].std(ddof=1) if i >= win - 1 else np.nan
                          for i in range(n_long)])

    z_all = (x - roll_mean) / roll_std
    z_clean = z_all[~np.isnan(z_all) & np.isfinite(z_all)]
    # Keep first 1000 valid observations
    z_clean = z_clean[:1000]

    fig, ax = plt.subplots(figsize=(6.8, 3.6))

    # Histogram
    counts, edges, patches = ax.hist(z_clean, bins=40, density=True,
                                     color=TEAL, alpha=0.65, edgecolor="white",
                                     linewidth=0.5, label="z-score distribution (n=1000)")

    # Shade tails (|z| > 2)
    for patch, left, right in zip(patches, edges[:-1], edges[1:]):
        if abs((left + right) / 2) > 2:
            patch.set_facecolor(RED)
            patch.set_alpha(0.55)

    # Normal(0,1) PDF overlay
    xs = np.linspace(-5, 5, 400)
    ax.plot(xs, norm.pdf(xs), color=NAVY, lw=2.2, label="Normal(0,1) PDF")

    # ±2σ vertical lines
    for v, lbl in [(2, "+2σ"), (-2, "−2σ")]:
        ax.axvline(v, color=AMBER, lw=1.5, ls="--", alpha=0.9)
        ax.text(v, ax.get_ylim()[1] * 0.02 if v > 0 else ax.get_ylim()[1] * 0.02,
                lbl, ha="center", va="bottom", fontsize=9, color=AMBER, fontweight="bold")

    ax.set_xlabel("z-score")
    ax.set_ylabel("Density")
    ax.set_title("Distribution of Z-scores from OU Simulation vs Normal(0,1)")
    ax.legend(loc="upper right", fontsize=9)
    ax.set_xlim(-5, 5)

    # Annotate tails
    tail_frac = np.mean(np.abs(z_clean) > 2)
    ax.text(3.2, 0.05, f"Tail > |2|\n{tail_frac*100:.1f}%", ha="center",
            fontsize=8.5, color=RED, fontweight="bold")

    style_axes(ax)
    save(fig, "ch6-zscore-dist")


if __name__ == "__main__":
    chart_zscore_signal()
    chart_zscore_distribution()
