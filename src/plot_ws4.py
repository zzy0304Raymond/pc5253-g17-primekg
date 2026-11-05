"""D's figures. Templates come from E; extra panels follow the same style.

Run from the repository root: python -m src.plot_ws4 primekg_5000_bfs_v1
"""
import argparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .common import NODE_LEVELS, ROOT
from .figure_templates import axes_grid, damage_axes, draw, heatmap, legend, render
from .plotting import BAND_ALPHA, NODE_COLORS, STYLE, save

FORMATS = ("png", "pdf", "svg")


def table(gid, name):
    return pd.read_csv(ROOT / "results" / "ws4" / f"{gid}__{name}.csv")


def export(fig, gid, name):
    save(fig, "act2", name, output_dir=ROOT / "figures" / "act2" / gid, formats=FORMATS)
    plt.close(fig)


def theory_vs_sim(gid):
    measured = pd.read_csv(ROOT / "results" / "ws3" / f"{gid}__retrieval.csv")
    measured = measured[measured.strategy == "edge_random"]
    curves = table(gid, "theory")
    curves = curves[(curves.strategy == "theory_bond") & curves.metric.isin(["R_L2_single", "R_L2_multi"])]
    export(render("fig_R_theory_vs_sim", pd.concat([measured, curves], ignore_index=True)), gid, "fig_R_theory_vs_sim")


def corr_penalty(gid):
    data = table(gid, "corr_penalty")
    export(render("fig_corr_penalty", data[data.metric == "corr_penalty"]), gid, "fig_corr_penalty")
    plt.rcParams.update({"font.size": 10})
    wide = data[data.frac_removed.isin([.05, .10])].pivot_table(
        index=["strategy", "frac_removed"], columns="metric", values="value")
    fig, axes = axes_grid(width=3.8, height=3.3)
    ax = axes[0, 0]
    labels, endpoint, path = [], [], []
    for strategy, name in (("node_degree", "Degree"), ("node_betweenness", "Betweenness")):
        for frac in (.05, .10):
            row = wide.loc[(strategy, frac)]
            labels.append(f"{name}\nf = {frac:.0%}")
            endpoint.append(100 * row.penalty_endpoint)
            path.append(100 * row.penalty_path)
    x = np.arange(len(labels))
    ax.bar(x, endpoint, width=.62, color=NODE_COLORS["disease"], edgecolor="white", linewidth=1.5,
           label="Lost endpoint (mostly hub diseases)")
    ax.bar(x, path, width=.62, bottom=endpoint, color=NODE_COLORS["gene/protein"], edgecolor="white",
           linewidth=1.5, label="Lost paths (hub proteins)")
    for i, (a, b) in enumerate(zip(endpoint, path)):
        ax.text(i, a / 2, f"{a:.1f}", ha="center", va="center", fontsize=9, color="#333333")
        ax.text(i, a + b / 2, f"{b:.1f}", ha="center", va="center", fontsize=9, color="#333333")
        ax.text(i, a + b + 1.2, f"{a + b:.1f}", ha="center", va="bottom", fontsize=9, color="#333333")
    ax.set_xticks(x, labels, fontsize=8)
    ax.set(ylabel="Theory − simulation (percentage points)", ylim=(0, 75))
    legend(fig, axes)
    export(fig, gid, "fig_corr_channels")


def phase_diagram(gid):
    """E's layout with the heatmap on f, matching the plan's shared x-axis rule."""
    scan = table(gid, "hop_scan_10seeds")
    curves = table(gid, "theory")
    curves = curves[(curves.strategy == "theory_bond") & curves.metric.isin(["R_L2", "R_Linf"])]
    data = pd.concat([scan[scan.metric != "ppi_gcc_frac"], curves], ignore_index=True)
    plt.close(render("fig_phase_diagram", data))  # applies the template's rcParams
    fig = plt.figure(figsize=(7.2, 3.4), layout="constrained")
    grid = fig.add_gridspec(2, 2, width_ratios=[1.3, 1])
    heat = fig.add_subplot(grid[:, 0])
    fig.colorbar(heatmap(heat, data), ax=heat, label="Success R", shrink=.8)
    for row, f in enumerate(table(gid, "hop_boundary").first_f):
        heat.plot(f, row, marker="o", ms=5, mfc="white", mec="#333333", mew=.8, ls="none",
                  label="R$_L$ 5 pp below L = ∞" if row == 0 else None)
    axes = [heat]
    for row, metric in enumerate(("R_L2", "R_Linf")):
        panel = fig.add_subplot(grid[row, 1])
        draw(panel, data, "edge_random", metric, style=STYLE[metric[2:]])
        draw(panel, data, "theory_bond", metric, style=STYLE["theory"])
        panel.set(xlabel="Fraction removed f", ylabel="Success R", title=STYLE[metric[2:]]["label"])
        axes.append(panel)
    legend(fig, axes)
    export(fig, gid, "fig_phase_diagram")


def giant_component(gid):
    scan = table(gid, "hop_scan_10seeds")
    curves = table(gid, "theory")
    fig, axes = axes_grid(width=4.6, height=3.4)
    ax = axes[0, 0]
    draw(ax, scan, "edge_random", "ppi_gcc_frac", style=dict(color="#707070", label="PPI giant component", marker="s"))
    draw(ax, scan, "edge_random", "R_Linf", style=STYLE["Linf"] | dict(color="#9472C4", label="R, L = ∞"))
    draw(ax, curves, "theory_bond", "ppi_gcc_frac", style=dict(STYLE["theory"], label="GF theory"))
    draw(ax, curves, "theory_bond", "R_Linf", style=dict(color="black", ls="--"))
    draw(ax, curves, "theory_bond", "R_attachment_bound",
         style=dict(color="#333333", ls=":", label="Both endpoints keep a terminal edge"))
    damage_axes(ax, "Fraction")
    ax.set_xlim(.5, 1.01)
    legend(fig, axes)
    export(fig, gid, "fig_ppi_giant")


def prediction_figures(gid):
    export(render("fig_prediction", table(gid, "prediction")), gid, "fig_prediction")


def equal_damage(gid):
    data = table(gid, "equal_damage")
    export(render("fig_equal_damage", data[data.frac_removed == .05]), gid, "fig_equal_damage")


def attack_overlay(gid):
    fig = render("fig_attack", table(gid, "attack_overlay"))
    save(fig, "act1", "fig_attack_theory", output_dir=ROOT / "figures" / "act1" / gid, formats=FORMATS)
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gids", nargs="*", default=["primekg_5000_bfs_v1"])
    for gid in parser.parse_args().gids:
        for step in (theory_vs_sim, corr_penalty, phase_diagram, giant_component,
                     prediction_figures, equal_damage, attack_overlay):
            step(gid)
        print("Saved WS4 figures for", gid)
