"""Figures for the external validation with real indications (Section 6).

Run from the repository root: python -m src.plot_ws6
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .common import ROOT
from .plotting import BAND_ALPHA, STYLE, panel_label, save, setup

IN = ROOT / "results" / "ws6"
OUT = ROOT / "figures" / "act6"
HOPS = (("R2", "L = 2"), ("R3", "L = 3"), ("R4", "L = 4"), ("Rinf", "L = ∞"))
COLORS = {"R2": STYLE["L2"]["color"], "R3": STYLE["L3"]["color"], "R4": "#8c564b", "Rinf": "#7f7f7f"}
POS, NEG = "#3B8DB5", "#B0B7C3"


def horizon_bars(ax, summary, cm, title=True):
    ind = summary.set_index("set")
    x = np.arange(len(HOPS))
    p = [100 * ind.loc["indication", k] for k, _ in HOPS]
    q = [100 * ind.loc["decoy", k] for k, _ in HOPS]
    ax.bar(x - .19, p, width=.36, color=POS, label="Approved indications")
    ax.bar(x + .19, q, width=.36, color=NEG, label="Degree-preserving decoys")
    ball = pd.read_csv(ROOT / "results" / "ws8" / "ball_null.csv").set_index("set").loc["decoy"]
    c = {k: ball[f"{k}_ball"] for k, _ in HOPS[:3]}
    ax.plot(x[:3] + .19, [100 * c[k] for k, _ in HOPS[:3]], ls="none", marker="_", ms=14, mew=2,
            color="black", label="Chance model (decoys)")
    tops = [max(a, b, 100 * c[k]) if k in c else max(a, b) for (a, b, (k, _)) in zip(p, q, HOPS)]
    for i, (a, b) in enumerate(zip(p, q)):
        ax.text(i, tops[i] + 3, f"×{a / b:.2f}", ha="center", fontsize=8.5)
    ax.set_xticks(x, [name for _, name in HOPS])
    ax.set(ylabel="Pairs with a typed path (%)", ylim=(0, 145), xlabel="Hop limit")
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.legend(loc="upper left", fontsize=7.5, ncol=1, frameon=False)
    if title:
        ax.set_title("Intact graph: only short paths are specific", fontsize=10.5)


def main():
    setup()
    summary = pd.read_csv(IN / "indication_intact_summary.csv")
    cm = pd.read_csv(IN / "indication_config_model.csv")
    scan = pd.read_csv(IN / "indication_damage_scan.csv")
    theory = pd.read_csv(IN / "indication_two_hop_theory.csv")
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.7), layout="constrained")

    ax = axes[0]
    rnd = scan[scan.kind == "edge_random"].groupby("frac_removed")
    mean, sd = rnd.mean(numeric_only=True), rnd.std(numeric_only=True, ddof=1)
    f = mean.index.to_numpy()
    ax.plot(f, mean.S, color="#333333", marker="s", ms=3, label="Giant component S")
    for key, name in (("Rinf", "L = ∞"), ("R3", "L = 3"), ("R2", "L = 2")):
        ax.plot(f, mean[f"{key}_pos"], color=COLORS[key], marker="o", ms=3, label=f"Indications, {name}")
        ax.plot(f, mean[f"{key}_neg"], color=COLORS[key], ls=":", lw=1.3)
    ax.plot(theory.frac_removed, theory.R2_pos_theory, color="black", ls="--", lw=1.1, label="Eq. (6)")
    ax.plot(theory.frac_removed, theory.R2_neg_theory, color="black", ls="--", lw=1.1)
    ax.plot([], [], color="grey", ls=":", lw=1.3, label="Decoys (dotted)")
    ax.set(xlabel="Fraction of edges removed at random, f", ylabel="Fraction with a typed path", xlim=(0, .9), ylim=(0, 1.02))
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2, fontsize=7.5, frameon=False)
    ax.set_title("Blind damage on the full graph", fontsize=10.5)

    ax = axes[1]
    att = scan[scan.kind == "degree"].set_index("frac_removed")
    for key, name in HOPS:
        ax.plot(mean.index, 1000 * mean[f"{key}_info_bits"], color=COLORS[key], marker="o", ms=3, label=name)
        ax.fill_between(mean.index, 1000 * (mean[f"{key}_info_bits"] - sd[f"{key}_info_bits"]),
                        1000 * (mean[f"{key}_info_bits"] + sd[f"{key}_info_bits"]), color=COLORS[key], alpha=BAND_ALPHA, lw=0)
    th = pd.read_csv(ROOT / "results" / "ws7" / "information_theory.csv")
    ax.plot(th.frac_removed, 1000 * th.R2_info_bits, color="black", ls="--", lw=1.1, label="L = 2, Eq. (6)")
    ax.plot(th.frac_removed, 1000 * th.R3_info_bits, color="black", ls=":", lw=1.3, label="L = 3, path-count estimate")
    ax.set(xlabel="Fraction of edges removed at random, f", ylabel="Information per pair (millibits)", xlim=(0, .9))
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2, fontsize=7.5, frameon=False)
    ax.set_title("Evidence carried by a path", fontsize=10.5)
    for a, lab in zip(axes, "ab"):
        panel_label(a, lab)
    fig2, ax2 = plt.subplots(figsize=(5.6, 3.5), layout="constrained")
    for key, name in HOPS:
        ax2.plot(mean.index, 1000 * mean[f"{key}_info_bits"], color=COLORS[key], marker="o", ms=3.5, label=name)
        ax2.fill_between(mean.index, 1000 * (mean[f"{key}_info_bits"] - sd[f"{key}_info_bits"]),
                         1000 * (mean[f"{key}_info_bits"] + sd[f"{key}_info_bits"]), color=COLORS[key], alpha=BAND_ALPHA, lw=0)
    ax2.plot(th.frac_removed, 1000 * th.R2_info_bits, color="black", ls="--", lw=1.1, label="L = 2, Eq. (6)")
    ax2.plot(th.frac_removed, 1000 * th.R3_info_bits, color="black", ls=":", lw=1.3, label="L = 3, Eq. (13)")
    ax2.set(xlabel="Fraction of edges removed at random, f", ylabel="Information per pair (millibits)", xlim=(0, .9))
    ax2.legend(loc="upper right", fontsize=8.5, ncol=2)
    save(fig2, "act6", "fig_information", output_dir=OUT, formats=("png", "pdf"))
    plt.close(fig2)
    save(fig, "act6", "fig_indications", output_dir=OUT, formats=("png", "pdf"))
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.6), layout="constrained", gridspec_kw=dict(wspace=0.08))
    ax = axes[0]
    fx = att.index.to_numpy()
    for key, name in HOPS[:3]:
        ax.plot(fx, att[f"{key}_pos"], color=COLORS[key], marker="o", ms=3, label=f"Indications, {name}")
        ax.plot(fx, att[f"{key}_neg"], color=COLORS[key], ls=":", lw=1.3)
    ax.plot(fx, att.S, color="#333333", marker="s", ms=3, label="Giant component S")
    ax.plot([], [], color="grey", ls=":", lw=1.3, label="Decoys (dotted)")
    ax.set(xlabel="Fraction of nodes removed by degree", ylabel="Fraction with a typed path", ylim=(0, 1.02))
    ax.legend(loc="upper right", fontsize=8.5)
    ax.set_title("Degree attack on the full graph", fontsize=10.5)
    ax = axes[1]
    keep = fx <= .1001
    for key, name in HOPS[:3]:
        ax.plot(fx[keep], (att[f"{key}_pos"] / att[f"{key}_neg"])[keep], color=COLORS[key], marker="o", ms=3, label=name)
    prot = pd.read_csv(ROOT / "results" / "ws8" / "protein_only_attack.csv")
    prot = prot[prot.attack == "proteins only"]
    for key in ("R2", "R3"):
        ax.plot(prot.frac_nodes, prot[f"{key}_ratio"], color=COLORS[key], ls="--", marker="s", ms=3,
                label=f"{key[0]}{key[1:]} proteins only".replace("R2", "L = 2,").replace("R3", "L = 3,"))
    ax.set(xlabel="Fraction of nodes removed by degree", ylabel="Indication rate / decoy rate", ylim=(0, 11))
    ax.legend(loc="upper left", ncol=1, fontsize=8.5)
    ax.set_title("Removing hubs removes non-specific paths", fontsize=10.5)
    for a, lab in zip(axes, "ab"):
        panel_label(a, lab)
    save(fig, "act6", "fig_indications_attack", output_dir=OUT, formats=("png", "pdf"))
    plt.close(fig)
    print("Saved act6 figures")


if __name__ == "__main__":
    main()


def frontier():
    """Perspective figure: robustness against information as the hop limit (resolution) changes."""
    setup()
    scan = pd.read_csv(IN / "indication_damage_scan.csv")
    rnd = scan[scan.kind == "edge_random"].groupby("frac_removed").mean(numeric_only=True)
    keys = (("R2", "L = 2"), ("R3", "L = 3"), ("R4", "L = 4"), ("Rinf", "L = ∞"))
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(9.2, 3.6), layout="constrained", gridspec_kw=dict(width_ratios=[1.45, 1]))
    ex = pd.read_csv(ROOT / "results" / "ws8" / "excess_by_horizon.csv")
    for f, style in ((0.0, dict(color="#3B8DB5", marker="o", label="Intact graph")),
                     (0.5, dict(color="#D9822B", marker="s", label="Half of the edges removed"))):
        part = ex[np.isclose(ex.frac_removed, f)]
        bx.plot([2, 3, 4], part.r_excess - 1, ms=6, lw=1.5, **style)
        if f == 0.0:
            n = 6233
            summ = pd.read_csv(IN / "indication_intact_summary.csv").set_index("set")
            err = []
            for key in ("R2", "R3", "R4"):
                tp, fp = summ.loc["indication", key], summ.loc["decoy", key]
                dr_dtp = -1 / ((1 - tp) * np.log(1 - fp))
                dr_dfp = np.log(1 - tp) / ((1 - fp) * np.log(1 - fp) ** 2)
                err.append(np.sqrt(dr_dtp ** 2 * tp * (1 - tp) / n + dr_dfp ** 2 * fp * (1 - fp) / n))
            bx.errorbar([2, 3, 4], part.r_excess - 1, yerr=err, fmt="none", ecolor=style["color"], capsize=3, lw=1)
    bx.set(yscale="log", xlabel="Hop limit L", ylabel=r"Excess of real over chance paths, $r_L - 1$",
           xticks=[2, 3, 4], ylim=(0.03, 3))
    bx.legend(loc="upper right", fontsize=8.5)
    bx.set_title("Specific excess shrinks with each hop", fontsize=10.5)
    panel_label(bx, "b")
    for f, style in ((0.0, dict(color="#3B8DB5", marker="o", label="Intact graph")),
                     (0.5, dict(color="#D9822B", marker="s", label="Half of the edges removed"))):
        x = [rnd.loc[0.5, f"{k}_pos"] / rnd.loc[0.0, f"{k}_pos"] for k, _ in keys]
        y = [1000 * rnd.loc[f, f"{k}_info_bits"] for k, _ in keys]
        ax.plot(x, y, ms=6, lw=1.5, **style)
        if f == 0.0:
            for xi, yi, (_, name) in zip(x, y, keys):
                ax.annotate(name, (xi, yi), textcoords="offset points", xytext=(6, 5), fontsize=9)
    s = rnd.loc[0.5, "S"] / rnd.loc[0.0, "S"]
    ax.plot([s], [0], marker="D", color="#333333", ls="none", ms=6, label="Giant component (no pairwise information)")
    ax.set(xlabel="Robustness: reachable indications kept at f = 0.5",
           ylabel="Information (millibits per pair)", xlim=(0.3, 0.95), ylim=(-1.5, 33))
    ax.legend(loc="upper right", fontsize=8.5)
    ax.set_title("Robustness against information", fontsize=10.5)
    panel_label(ax, "a")
    save(fig, "act6", "fig_frontier", output_dir=OUT, formats=("png", "pdf"))
    plt.close(fig)
    print("Saved fig_frontier")
