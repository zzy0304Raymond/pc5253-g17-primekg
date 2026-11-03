"""Shared G17 figure style. Call setup() before creating figures."""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

from .common import ROOT


# Existing experiment colors follow Work Plan appendix C.
STYLE = {
    "edge_random": dict(color="#1f77b4", label="Random edge removal", marker="o"),
    "node_random": dict(color="#2ca02c", label="Random node removal", marker="s"),
    "node_degree": dict(color="#d62728", label="Degree attack", marker="^"),
    "node_betweenness": dict(color="#ff7f0e", label="Betweenness attack", marker="D"),
    "theory": dict(color="black", ls="--", label="Theory"),
    "restore_random": dict(color="#707070", label="Random", marker="o"),
    "restore_edge_betweenness": dict(color="#3B8DB5", label="Edge betweenness", marker="s"),
    "restore_relation_type": dict(color="#E3AE53", label="Relation type", marker="^"),
    "restore_task_aware": dict(color="#9472C4", label="Task-aware", marker="D"),
    "gcc": dict(color="#707070", label="GCC", marker="s"),
    "single": dict(color="#3B8DB5", label="Single", marker="o"),
    "multi": dict(color="#9472C4", label="Multi", marker="s"),
    "L2": dict(color="#3B8DB5", label="L = 2", marker="o"),
    "L3": dict(color="#E3AE53", label="L = 3", marker="s"),
    "L4": dict(color="#9472C4", label="L = 4", marker="^"),
    "Linf": dict(color="#707070", label="L = ∞", marker="D"),
}

NODE_COLORS = {"drug": "#3B8DB5", "disease": "#D97B7B", "gene/protein": "#9DA8BA"}
HEATMAP = LinearSegmentedColormap.from_list("g17_blue", ["#F6F8FB", "#B9D8E7", "#22658C"])
BAND_ALPHA = 0.16


def setup():
    """Apply the shared style; individual figures may choose their own size."""
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "DejaVu Sans"],
        "font.size": 12,
        "figure.figsize": (6, 4),
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "savefig.dpi": 300,
        "pdf.fonttype": 42,
        "svg.fonttype": "none",
        "text.color": "#333333",
        "axes.labelcolor": "#333333",
        "axes.edgecolor": "#858585",
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.titlesize": 12,
        "axes.titleweight": "normal",
        "axes.titlepad": 12,
        "axes.labelpad": 8,
        "axes.grid": False,
        "xtick.color": "#555555",
        "ytick.color": "#555555",
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.size": 3.5,
        "ytick.major.size": 3.5,
        "lines.linewidth": 1.8,
        "lines.markersize": 4,
        "lines.markeredgewidth": 0.6,
        "legend.frameon": False,
        "legend.fontsize": 10,
        "legend.handlelength": 2.4,
        "legend.labelspacing": 0.6,
        "errorbar.capsize": 2,
    })


def mean_sd(ax, x, mean, sd, strategy):
    """Draw precomputed mean ± sample SD, without clipping or interpolation.

    Callers compute SD across independent seeds (ddof=1), not queries or
    pooled damage levels. Deterministic results use ax.plot instead.
    """
    x, mean, sd = [np.asarray(v, dtype=float) for v in (x, mean, sd)]
    if x.ndim != 1 or mean.shape != x.shape or sd.shape != x.shape or not len(x):
        raise ValueError("x, mean and sd must be nonempty 1D arrays of equal length")
    if not all(np.isfinite(v).all() for v in (x, mean, sd)):
        raise ValueError("x, mean and sd must be finite; at least two seeds are needed for SD")
    if np.any(np.diff(x) <= 0) or np.any(sd < 0):
        raise ValueError("x must increase strictly and sd must be nonnegative")
    style = STYLE[strategy]
    ax.fill_between(x, mean - sd, mean + sd, color=style["color"],
                    alpha=BAND_ALPHA, linewidth=0)
    return ax.plot(x, mean, **style)[0]


def panel_label(ax, label):
    """Place a lowercase panel letter outside the top-left of an axes."""
    return ax.text(-0.13, 1.07, label, transform=ax.transAxes,
                   fontsize=14, fontweight="bold", va="bottom", ha="left")


def save(fig, act, name, *, output_dir=None, formats=("png", "pdf")):
    """Export relative to the repository, regardless of shell working directory.

    output_dir overrides the destination for previews. Does not close fig.
    SVG is available through formats=("png", "pdf", "svg").
    """
    folder = Path(output_dir) if output_dir is not None else ROOT / "figures" / act
    folder.mkdir(parents=True, exist_ok=True)
    paths = []
    for ext in formats:
        path = folder / f"{name}.{ext}"
        fig.savefig(path, bbox_inches="tight", pad_inches=0.12)
        paths.append(path)
    return paths
