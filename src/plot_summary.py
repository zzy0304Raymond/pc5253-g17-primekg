"""One-figure summary of the report (Figure 1).

(a) Random edge removal: the giant component S and retrieval R_L for L = 2, 3, inf,
    with the zero-parameter predictions of Section 3 (dashed).
(b) 5% node removal: structural and functional loss under blind and targeted damage,
    with the blind-damage formula.

Run from the repository root: python -m src.plot_summary primekg_5000_bfs_v1
"""
import argparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .common import ROOT
from .plotting import BAND_ALPHA, STYLE, panel_label, save, setup


def mean_sd(frame, strategy, metric):
    part = frame[(frame.strategy == strategy) & (frame.metric == metric)]
    g = part.groupby("frac_removed").value
    return g.mean(), g.std(ddof=1)


def main(gid):
    setup()
    ws1 = pd.read_csv(ROOT / "results" / "ws1" / f"{gid}__random.csv")
    hop = pd.read_csv(ROOT / "results" / "ws4" / f"{gid}__hop_scan_10seeds.csv")
    theory = pd.read_csv(ROOT / "results" / "ws4" / f"{gid}__theory.csv")
    theory = theory[theory.strategy == "theory_bond"]
    damage = pd.read_csv(ROOT / "results" / "ws4" / f"{gid}__equal_damage.csv")
    damage = damage[np.isclose(damage.frac_removed, .05)]
    penalty = pd.read_csv(ROOT / "results" / "ws4" / f"{gid}__corr_penalty.csv")
    formula = penalty[(penalty.strategy == "node_degree") & np.isclose(penalty.frac_removed, .05)
                      & (penalty.metric == "R_L2_formula")].value.iloc[0]

    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.9), layout="constrained",
                             gridspec_kw=dict(width_ratios=[1.35, 1]))
    ax = axes[0]
    fresh = pd.read_csv(ROOT / "results" / "ws4" / f"{gid}__hop_fresh_orders.csv")
    fresh = pd.concat([pd.DataFrame([{c: (1.0 if c.endswith("_mean") else 0.0) for c in fresh.columns} | {"frac_removed": 0.0}]),
                       fresh], ignore_index=True)
    mean, sd = mean_sd(ws1, "edge_random", "gcc_frac")
    style = dict(color="#333333", marker="s", label="Giant component S")
    ax.fill_between(mean.index, mean - sd, mean + sd, color=style["color"], alpha=BAND_ALPHA, linewidth=0)
    ax.plot(mean.index, mean.to_numpy(), ms=3.5, **style)
    line = theory[theory.metric == "gcc_frac"].sort_values("frac_removed")
    ax.plot(line.frac_removed, line.value, color="black", ls="--", lw=1.2)
    for key, th, style in (("R_Linf", "R_Linf", dict(STYLE["Linf"], color="#7f7f7f", label="Retrieval, unlimited hops")),
                           ("R_L3", None, dict(STYLE["L3"], label="Retrieval, L = 3")),
                           ("R_L2", "R_L2", dict(STYLE["L2"], label="Retrieval, L = 2"))):
        x = fresh.frac_removed.to_numpy()
        m = fresh[f"{key}_mean"].to_numpy()
        s = fresh[f"{key}_se"].to_numpy() * np.sqrt(600)
        ax.fill_between(x, m - s, m + s, color=style["color"], alpha=BAND_ALPHA, linewidth=0)
        ax.plot(x, m, ms=3.5, **style)
        if th:
            line = theory[theory.metric == th].sort_values("frac_removed")
            ax.plot(line.frac_removed, line.value, color="black", ls="--", lw=1.2)
    ax.plot([], [], color="black", ls="--", lw=1.2, label="Zero-parameter theory")
    ax.annotate("", xy=(.5, .414), xytext=(.5, .982),
                arrowprops=dict(arrowstyle="<->", color="#d62728", lw=1.3))
    ax.text(.515, .64, "S − R₂ = 57 points\nat f = 0.5", color="#d62728", fontsize=9, va="center",
            bbox=dict(fc="white", ec="none", alpha=0.85, pad=1))
    ax.set(xlabel="Fraction of edges removed at random, f", ylabel="Fraction surviving", xlim=(0, 1), ylim=(0, 1.03))
    ax.legend(loc="lower left", fontsize=8.5)
    ax.set_title("Blind damage: connectivity stays, short answers go", fontsize=11)

    ax = axes[1]
    names = [("node_random", "Random\nremoval"), ("node_degree", "Degree\nattack"), ("node_betweenness", "Betweenness\nattack")]
    x = np.arange(len(names))
    s_loss = [100 * (1 - damage[(damage.strategy == s) & (damage.metric == "gcc_frac")].value.mean()) for s, _ in names]
    r_loss = [100 * (1 - damage[(damage.strategy == s) & (damage.metric == "R_L2")].value.mean()) for s, _ in names]
    ax.bar(x - .19, s_loss, width=.36, color="#9DA8BA", label="Lost connectivity (1 − S)")
    ax.bar(x + .19, r_loss, width=.36, color="#3B8DB5", label="Lost two-hop answers (1 − R₂)")
    ax.axhline(100 * (1 - formula), color="black", ls="--", lw=1.2, label="Blind-damage formula for 1 − R₂")
    for i, (a, b) in enumerate(zip(s_loss, r_loss)):
        ax.text(i - .19, a + 1.5, f"{a:.0f}", ha="center", fontsize=9)
        ax.text(i + .19, b + 1.5, f"{b:.0f}", ha="center", fontsize=9)
    ax.set_xticks(x, [n for _, n in names], fontsize=9)
    ax.set(ylabel="Percent lost (5% of nodes removed)", ylim=(0, 100))
    ax.legend(loc="upper left", fontsize=8.5)
    ax.set_title("Aimed damage: routes run through hubs", fontsize=11)
    panel_label(axes[0], "a")
    panel_label(axes[1], "b")
    save(fig, "act0", "fig_summary", output_dir=ROOT / "figures" / "act0", formats=("png", "pdf"))
    plt.close(fig)
    print("Saved fig_summary")


def redundancy(gid):
    """Figure 2: the three redundancy distributions behind S, R_inf and R_2."""
    import json
    setup()
    degree = pd.read_csv(ROOT / "data" / "processed" / gid / "node_features.csv").degree.to_numpy()
    lam = pd.read_csv(ROOT / "results" / "ws4" / f"{gid}__mincut_per_query.csv").edge_connectivity.to_numpy()
    queries = json.loads((ROOT / "data" / "processed" / gid / "queries.json").read_text())
    m = np.array([q["redundancy_m"] for q in queries])
    fig, ax = plt.subplots(figsize=(5.6, 3.7), layout="constrained")
    for values, color, name in ((degree, "#333333", "Node degree k, for S"),
                                (lam, "#7f7f7f", "Min cut λ, for R∞"),
                                (m, "#3B8DB5", "Shared proteins m, for R₂")):
        x = np.unique(values)
        ccdf = np.array([(values >= v).mean() for v in x])
        x = np.r_[x, x[-1] * 1.0001]
        ccdf = np.r_[ccdf, 0.0]
        ax.step(x, ccdf, where="post", color=color, lw=1.8,
                label=f"{name}:  P(=1) = {(values == 1).mean():.1%}")
    ax.set_xscale("log")
    ax.set(xlabel="Redundancy x (number of independent units)", ylabel="Fraction with redundancy ≥ x",
           ylim=(0, 1.05), xlim=(.9, 3000))
    ax.legend(loc="upper right", fontsize=8.5)
    save(fig, "act0", "fig_redundancy", output_dir=ROOT / "figures" / "act0", formats=("png", "pdf"))
    plt.close(fig)


def r2_by_group(gid="primekg_5000_bfs_v1"):
    """Long-run two-hop success by query group against the exact formula."""
    setup()
    data = pd.read_csv(ROOT / "results" / "ws4" / f"{gid}__R2_long_run_by_group.csv")
    theory = pd.read_csv(ROOT / "results" / "ws4" / f"{gid}__theory.csv")
    theory = theory[theory.strategy == "theory_bond"]
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.5), layout="constrained", sharey=True)
    for ax, group, title in ((axes[0], "single", "Single-path queries (m = 1)"),
                             (axes[1], "multi", "Multi-path queries (m ≥ 2)")):
        part = data[data.group == group].sort_values("frac_removed")
        x = np.r_[0, part.frac_removed]
        mean = np.r_[1, part["mean"]]
        sd = np.r_[0, part.sd_one_state]
        style = STYLE[group]
        ax.fill_between(x, mean - sd, mean + sd, color=style["color"], alpha=BAND_ALPHA, linewidth=0,
                        label="One damage state (±1 SD)")
        ax.plot(x, mean, color=style["color"], marker=style["marker"], ms=3.5, label="Mean of 5,000 damage orders")
        line = theory[theory.metric == f"R_L2_{group}"].sort_values("frac_removed")
        ax.plot(line.frac_removed, line.value, color="black", ls="--", lw=1.2, label=r"Exact formula $1 - G_m(1 - p^2)$")
        ax.set(title=title, xlabel="Fraction of edges removed f", xlim=(0, 1), ylim=(0, 1.02))
    axes[0].set_ylabel("Two-hop success R₂")
    axes[1].legend(loc="upper right", fontsize=8.5)
    save(fig, "act2", "fig_R2_long_run", output_dir=ROOT / "figures" / "act2" / gid, formats=("png", "pdf"))
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gids", nargs="*", default=["primekg_5000_bfs_v1"])
    for gid in parser.parse_args().gids:
        main(gid)
        redundancy(gid)
        r2_by_group(gid)
