"""
Shared matplotlib style for the Statistical Arbitrage book.
All chapter chart scripts import from here so the visual language stays consistent.

Palette mirrors the book's CSS :root variables (teal/navy theme).
Exports SVG into docs/charts/ for embedding via <img class="chart" src="charts/...svg">.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

# ----- paths -----
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHARTS_DIR = os.path.join(ROOT, "docs", "charts")
FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
os.makedirs(CHARTS_DIR, exist_ok=True)

# ----- register Thai font (Sarabun) so Thai labels render -----
for fn in ("Sarabun-Regular.ttf", "Sarabun-Bold.ttf"):
    fp = os.path.join(FONT_DIR, fn)
    if os.path.exists(fp):
        font_manager.fontManager.addfont(fp)

# ----- book palette (matches CSS :root) -----
TEAL   = "#0d9488"
NAVY   = "#1f2937"
INK    = "#111827"
RED    = "#dc2626"
GREEN  = "#16a34a"
BLUE   = "#2563eb"
AMBER  = "#d97706"
VIOLET = "#7c3aed"
GREY   = "#9ca3af"
GRID   = "#e5e7eb"
SOFT   = "#cbd5e1"

# soft fills for zones
RED_F   = "#fef2f2"
AMBER_F = "#fff7ed"
GREEN_F = "#f0fdf4"
TEAL_F  = "#f0fdfa"
BLUE_F  = "#eff6ff"

plt.rcParams.update({
    # Sarabun renders Thai; DejaVu Sans is fallback for Greek/math glyphs (σ θ κ ε τ ✓)
    "font.family": ["Sarabun", "DejaVu Sans"],
    "font.size": 11,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.titlecolor": NAVY,
    "axes.labelcolor": NAVY,
    "axes.edgecolor": SOFT,
    "axes.linewidth": 1.0,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.8,
    "axes.axisbelow": True,
    "xtick.color": GREY,
    "ytick.color": GREY,
    "xtick.labelcolor": NAVY,
    "ytick.labelcolor": NAVY,
    "legend.frameon": True,
    "legend.framealpha": 0.95,
    "legend.edgecolor": GRID,
    "legend.fontsize": 9.5,
    "figure.dpi": 110,
    "svg.fonttype": "none",   # keep text as text in SVG (selectable, small files)
})


def style_axes(ax):
    """Common axis polish: hide top/right spines."""
    ax.spines[["top", "right"]].set_visible(False)


def save(fig, name):
    """Save figure as SVG into docs/charts/. `name` without extension."""
    path = os.path.join(CHARTS_DIR, name + ".svg")
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print("saved", os.path.relpath(path, ROOT))
    return path
