"""G17 A–E templates. Rendering consumes measurements; it never simulates results.

See docs/FIGURE_TEMPLATES.md for exact CSV schemas and CLI examples.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from .plotting import STYLE, NODE_COLORS, HEATMAP, BAND_ALPHA, setup


CATALOG = {
    "fig_degree_dist": ("A", "Degree distribution", "nodes"),
    "fig_S_random_edge": ("A", "Random edge failure", "long"),
    "fig_S_random_node": ("A", "Random node failure", "long"),
    "fig_attack": ("B", "Targeted attacks", "long"),
    "fig_hub_composition": ("B", "Hub composition", "hubs"),
    "fig_S_vs_R": ("C", "Structure vs function", "long"),
    "fig_R_by_group": ("C", "Path redundancy", "long"),
    "fig_R_L_curves": ("C", "Retrieval horizon", "long"),
    "fig_R_L_heatmap": ("C", "Retrieval heatmap", "long"),
    "fig_R_theory_vs_sim": ("D", "Theory vs simulation", "long"),
    "fig_corr_penalty": ("D", "Correlation penalty", "long"),
    "fig_phase_diagram": ("D", "Task-scale phase diagram", "long"),
    "fig_prediction": ("D", "Prediction performance", "prediction"),
    "fig_restoration": ("E", "Restoration gain", "recovery"),
    "fig_gain_per_edge": ("E", "Gain per restored edge", "recovery"),
    "fig_fragmentation": ("A", "Network fragmentation", "long"),
    "fig_sampling_comparison": ("A", "Sampling comparison", "long"),
    "fig_rank_overlap": ("B", "Centrality rank overlap", "overlap"),
    "fig_equal_damage": ("D", "Equal damage comparison", "long"),
    "fig_query_schematic": ("E", "Connectivity vs retrieval", "schematic"),
}
RESTORE = tuple(k for k in STYLE if k.startswith("restore_"))
L_METRICS = ("R_L2", "R_L3", "R_L4", "R_Linf")


def required(data, columns):
    missing = set(columns) - set(data.columns)
    if missing:
        raise ValueError(f"Missing columns: {', '.join(sorted(missing))}")
    if data.empty:
        raise ValueError("Empty input table")
    if data[list(columns)].isna().any().any():
        raise ValueError("Required fields contain missing values")


def numeric(data, columns):
    required(data, columns)
    if not np.isfinite(data[list(columns)].to_numpy(dtype=float)).all():
        raise ValueError(f"Nonfinite values in {columns}")


def select(data, strategy, metric):
    result = data[(data.strategy == strategy) & (data.metric == metric)]
    if result.empty:
        raise ValueError(f"Missing series: strategy={strategy}, metric={metric}")
    return result


def draw(ax, data, strategy, metric, *, style=None, x="frac_removed"):
    frame = select(data, strategy, metric)
    numeric(frame, [x, "seed", "value"])
    if frame.duplicated([x, "seed"]).any():
        raise ValueError("Duplicate seed/x rows; select one gid, damage level and experiment first")
    if not np.equal(frame.seed, np.floor(frame.seed)).all() or (frame.seed < -1).any():
        raise ValueError("seed must be -1 (deterministic) or a nonnegative integer")
    deterministic = frame.seed.eq(-1)
    if deterministic.any() and not deterministic.all():
        raise ValueError("Cannot mix deterministic and repeated measurements in one series")
    if deterministic.all():
        agg = frame.sort_values(x)
        mean = agg.value.to_numpy()
        xx = agg[x].to_numpy()
    else:
        seeds = frame.groupby(x).seed.apply(lambda v: frozenset(v))
        if any(v != seeds.iloc[0] for v in seeds) or len(seeds.iloc[0]) < 2:
            raise ValueError("Each x needs the same set of at least two seeds for sample SD")
        agg = frame.groupby(x).value.agg(["mean", "std"])
        xx, mean = agg.index.to_numpy(), agg["mean"].to_numpy()
        color = (style or STYLE[strategy])["color"]
        ax.fill_between(xx, mean - agg["std"].to_numpy(), mean + agg["std"].to_numpy(),
                        color=color, alpha=BAND_ALPHA, linewidth=0)
    ax.plot(xx, mean, **dict(style or STYLE[strategy]))


def axes_grid(rows=1, cols=1, *, width=None, height=None):
    fig, axes = plt.subplots(rows, cols, squeeze=False,
                            figsize=(width or 3.5 * cols + 0.3, height or 2.7 * rows + 0.6),
                            layout="constrained")
    return fig, axes


def damage_axes(ax, ylabel):
    ax.set(xlabel="Fraction removed f", ylabel=ylabel, xlim=(-0.02, 1.02))
    ax.set_xticks([0, .2, .4, .6, .8, 1])


def legend(fig, axes):
    handles = {}
    for ax in np.asarray(axes).ravel():
        for handle, label in zip(*ax.get_legend_handles_labels()):
            handles.setdefault(label, handle)
    if handles:
        fig.legend(handles.values(), handles.keys(), loc="outside lower center",
                   ncol=min(2 if np.asarray(axes).size == 1 else 4, len(handles)),
                   fontsize=8, columnspacing=1.4)


def basic_curves(name, data):
    fig, axes = axes_grid()
    ax = axes[0, 0]
    if name in ("fig_S_random_edge", "fig_S_random_node"):
        kind = "edge" if name.endswith("edge") else "node"
        draw(ax, data, kind + "_random", "gcc_frac")
        draw(ax, data, "theory_bond" if kind == "edge" else "theory_site", "gcc_frac", style=STYLE["theory"])
        ylabel = "GCC fraction"
    elif name == "fig_attack":
        for strategy in ("node_random", "node_degree", "node_betweenness"):
            draw(ax, data, strategy, "gcc_frac")
        draw(ax, data, "theory_attack", "gcc_frac", style=STYLE["theory"])
        ylabel = "GCC fraction"
    elif name == "fig_S_vs_R":
        draw(ax, data, "edge_random", "gcc_frac", style=STYLE["gcc"])
        draw(ax, data, "edge_random", "R_L2", style=STYLE["L2"])
        ylabel = "GCC fraction / success R"
    elif name == "fig_R_by_group":
        for group in ("single", "multi"):
            draw(ax, data, "edge_random", "R_L2_" + group, style=STYLE[group])
        ylabel = "Retrieval success R"
    elif name == "fig_R_L_curves":
        for metric in L_METRICS:
            draw(ax, data, "edge_random", metric, style=STYLE[metric[2:]])
        ylabel = "Retrieval success R"
    elif name == "fig_corr_penalty":
        for strategy in ("node_degree", "node_betweenness"):
            draw(ax, data, strategy, "corr_penalty")
        ax.axhline(0, color="#AAAAAA", lw=.7, zorder=0)
        ylabel = "Theory − simulation Δ"
    damage_axes(ax, ylabel)
    legend(fig, axes)
    return fig


def degree_distribution(data):
    required(data, ["node_type", "degree"])
    numeric(data, ["degree"])
    if not set(data.node_type) <= set(NODE_COLORS) or (data.degree < 0).any():
        raise ValueError("Invalid node type or negative degree")
    if not np.equal(data.degree, np.floor(data.degree)).all():
        raise ValueError("Degree must be integer")
    fig, axes = axes_grid()
    ax = axes[0, 0]
    if data.degree.max() == 0:
        raise ValueError("Log degree plot requires a nonzero degree")
    thresholds = np.unique(np.geomspace(1, max(2, data.degree.max()), 60).astype(int))
    node_labels = {"drug": "Drug", "disease": "Disease", "gene/protein": "Protein"}
    for typ, color in NODE_COLORS.items():
        values = np.sort(data.loc[data.node_type == typ, "degree"].to_numpy())
        if not len(values):
            raise ValueError(f"Missing node type: {typ}")
        survival = (len(values) - np.searchsorted(values, thresholds)) / len(values)
        positive = survival > 0
        ax.loglog(thresholds[positive], survival[positive], color=color, marker=".",
                  markersize=3, label=f"{node_labels[typ]} (n={len(values):,})")
    ax.set(xlabel="Degree k", ylabel="P(K ≥ k)")
    legend(fig, axes)
    return fig


def hubs(data):
    required(data, ["strategy", "top_frac", "node_type", "fraction"])
    numeric(data, ["top_frac", "fraction"])
    if data.duplicated(["strategy", "top_frac", "node_type"]).any():
        raise ValueError("Duplicate hub composition cells")
    if not set(data.node_type) <= set(NODE_COLORS) or not data.fraction.between(0, 1).all():
        raise ValueError("Invalid node types or fractions")
    fig, axes = axes_grid(cols=2)
    for ax, strategy in zip(axes.ravel(), ("node_degree", "node_betweenness")):
        table = data[data.strategy == strategy].pivot(index="top_frac", columns="node_type", values="fraction")
        if set(table.columns) != set(NODE_COLORS) or table.isna().any().any() or not np.allclose(table.sum(axis=1), 1):
            raise ValueError("Each hub group needs all three types summing to 1")
        bottom = np.zeros(len(table))
        for typ, color in NODE_COLORS.items():
            ax.bar(range(len(table)), table[typ], bottom=bottom, width=.60, color=color, label=typ)
            bottom += table[typ].to_numpy()
        ax.set_xticks(range(len(table)), [f"{v:.0%}" for v in table.index])
        ax.set(xlabel="Top-ranked nodes", ylabel="Node-type fraction", ylim=(0, 1.02), title=STYLE[strategy]["label"])
    legend(fig, axes)
    return fig


def heatmap(ax, data, *, survival=False):
    cells = []
    seed_sets = []
    for metric in L_METRICS:
        frame = select(data, "edge_random", metric)
        if frame.duplicated(["seed", "frac_removed"]).any():
            raise ValueError("Duplicate heatmap seed/level")
        numeric(frame, ["value", "frac_removed", "seed"])
        seed_sets.extend(frame.groupby("frac_removed").seed.apply(lambda s: frozenset(s)).tolist())
        cells.append(frame.groupby("frac_removed").value.mean().rename(metric))
    if any(s != seed_sets[0] for s in seed_sets):
        raise ValueError("Heatmap cells must use identical seed sets")
    table = pd.concat(cells, axis=1).sort_index()
    if table.isna().any().any() or not np.all((table.to_numpy() >= 0) & (table.to_numpy() <= 1)):
        raise ValueError("Heatmap requires complete fractions in [0, 1]")
    xx = table.index.to_numpy()
    if not np.all((xx >= 0) & (xx <= 1)) or len(xx) < 2:
        raise ValueError("Heatmap requires at least two damage levels in [0,1]")
    if survival:
        xx = 1 - xx[::-1]
        table = table.iloc[::-1]
    # Preserve nonuniform f spacing; categories L are equally spaced, including infinity.
    edges = np.r_[max(0, xx[0] - (xx[1]-xx[0])/2), (xx[:-1]+xx[1:])/2,
                  min(1, xx[-1]+(xx[-1]-xx[-2])/2)]
    mesh = ax.pcolormesh(edges, np.arange(5)-.5, table.to_numpy().T,
                         cmap=HEATMAP, vmin=0, vmax=1, shading="flat", rasterized=True)
    ax.set_yticks(range(4), ["2", "3", "4", "∞"])
    ax.set(xlabel="Edge survival p" if survival else "Fraction removed f", ylabel="Maximum hops L")
    return mesh


def phase(data):
    fig = plt.figure(figsize=(7.2, 3.4), layout="constrained")
    grid = fig.add_gridspec(2, 2, width_ratios=[1.3, 1])
    ax = fig.add_subplot(grid[:, 0])
    mesh = heatmap(ax, data, survival=True)
    fig.colorbar(mesh, ax=ax, label="Success R", shrink=.8)
    axes = [ax]
    for row, metric in enumerate(("R_L2", "R_Linf")):
        other = fig.add_subplot(grid[row, 1])
        draw(other, data, "edge_random", metric, style=STYLE[metric[2:]])
        draw(other, data, "theory_bond", metric, style=STYLE["theory"])
        other.set(xlabel="Fraction removed f", ylabel="Success R", title=STYLE[metric[2:]]["label"])
        axes.append(other)
    legend(fig, axes)
    return fig


def theory_groups(data):
    fig, axes = axes_grid(cols=2)
    for ax, group in zip(axes.ravel(), ("single", "multi")):
        draw(ax, data, "edge_random", "R_L2_" + group, style=STYLE[group])
        draw(ax, data, "theory_bond", "R_L2_" + group, style=STYLE["theory"])
        damage_axes(ax, "Retrieval success R")
        ax.set_title(group.capitalize() + "-path queries")
    legend(fig, axes)
    return fig


def predictions(data):
    required(data, ["model", "damage_frac", "metric", "value"])
    numeric(data, ["value", "damage_frac"])
    if data.duplicated(["model", "damage_frac", "metric"]).any():
        raise ValueError("One held-out aggregate per model/damage/metric is required")
    fig, axes = axes_grid(cols=2)
    models = ("theory", "logistic")
    for ax, metric in zip(axes.ravel(), ("AUC", "Brier")):
        t = data[data.metric == metric].pivot(index="damage_frac", columns="model", values="value")
        if set(t.columns) != set(models) or t.isna().any().any() or not np.isfinite(t.to_numpy()).all():
            raise ValueError("Both models and complete held-out scores are required")
        if not np.all((t.to_numpy() >= 0) & (t.to_numpy() <= 1)):
            raise ValueError("AUC and Brier must lie in [0,1]")
        for i, (model, color) in enumerate(zip(models, ("#707070", "#9472C4"))):
            ax.bar(np.arange(len(t))+(i-.5)*.3, t[model], width=.28, color=color,
                   label="Theory" if model == "theory" else "Logistic regression")
        ax.set_xticks(range(len(t)), [f"{f:.0%}" for f in t.index])
        ax.set(xlabel="Initial edge removal", ylabel=metric,
               title=metric + (" ↑" if metric == "AUC" else " ↓"))
    legend(fig, axes)
    return fig


def recovery(name, data, strategies=RESTORE):
    required(data, ["damage_frac", "budget_frac", "n_restored", "strategy", "seed", "metric", "value"])
    numeric(data, ["damage_frac", "budget_frac", "n_restored", "seed", "value"])
    if (not data.budget_frac.between(0, 1).all() or (data.n_restored < 0).any()
            or not np.equal(data.n_restored, np.floor(data.n_restored)).all()):
        raise ValueError("Invalid restoration budgets/counts")
    if not np.allclose(data.damage_frac, data.frac_removed):
        raise ValueError("For recovery, frac_removed must be the initial damage_frac")
    query_rows = data.metric.isin(["R_L2", "R_L3"])
    if not data.loc[query_rows, "value"].between(0, 1).all():
        raise ValueError("Recovery input values are raw success fractions in [0,1], not precomputed gains")
    damages = sorted(data.damage_frac.unique())
    if damages != [.3, .5]:
        raise ValueError("Restoration requires both damage_frac=0.3 and 0.5")
    fig, axes = axes_grid(rows=2, cols=2, width=7.2, height=5.7)
    for row, damage in enumerate(damages):
        for col, metric in enumerate(("R_L2", "R_L3")):
            ax = axes[row, col]
            subset = data[(data.damage_frac == damage) & (data.metric == metric)]
            seed_sets = [frozenset(subset.loc[subset.strategy == s, "seed"]) for s in strategies]
            if any(s != seed_sets[0] for s in seed_sets):
                raise ValueError("Recovery strategies must use identical damage seeds")
            for strategy in strategies:
                frame = data[(data.damage_frac == damage) & (data.strategy == strategy) & (data.metric == metric)].copy()
                if frame.empty or frame.duplicated(["seed", "budget_frac"]).any():
                    raise ValueError("Missing or duplicated recovery observations")
                baseline = frame[frame.budget_frac == 0].set_index("seed").value
                if not set(frame.seed) <= set(baseline.index):
                    raise ValueError("Every seed requires a zero-budget baseline")
                if (frame.loc[frame.budget_frac == 0, "n_restored"] != 0).any():
                    raise ValueError("Zero budget must restore zero edges")
                frame["value"] = frame.value - frame.seed.map(baseline)
                if name == "fig_gain_per_edge":
                    frame = frame[frame.budget_frac > 0].copy()
                    if (frame.n_restored <= 0).any():
                        raise ValueError("Positive-budget efficiency requires n_restored > 0")
                    frame["value"] = frame.value / frame.n_restored * 1000
                else:
                    frame["value"] *= 100  # success fraction -> percentage points
                draw(ax, frame, strategy, metric, x="budget_frac")
            # Fair baseline: all strategies start at the same state for each seed.
            base = data[(data.damage_frac == damage) & (data.metric == metric) & (data.budget_frac == 0)]
            if (base.groupby("seed").value.nunique() != 1).any():
                raise ValueError("Strategies have different zero-budget baselines")
            ax.set(title=f"{damage:.0%} removed · L = {col+2}", xlabel="Removed edges restored")
            ax.set_ylabel("Gain per 1,000 edges" if name == "fig_gain_per_edge" else "Success gain (pp)")
            ax.set_xticks([0, .05, .10, .20], ["0%", "5%", "10%", "20%"])
    legend(fig, axes)
    return fig


def extras(name, data):
    if name == "fig_fragmentation":
        fig, axes = axes_grid(cols=3, width=10.5)
        for ax, metric, label in zip(axes.ravel(), ("n_components", "isolated_frac", "avg_degree"),
                                     ("Components", "Isolated fraction", "Mean degree")):
            for strategy in ("edge_random", "node_random"):
                draw(ax, data, strategy, metric)
            damage_axes(ax, label)
    elif name == "fig_sampling_comparison":
        fig, axes = axes_grid()
        for gid, color in zip(sorted(data.gid.unique()), ("#3B8DB5", "#9472C4", "#707070")):
            frame = data[data.gid == gid]
            labels = {"primekg_2000_bfs_v1": "2,000-node BFS", "primekg_5000_bfs_v1": "5,000-node BFS",
                      "primekg_full_v1": "Filtered full graph"}
            draw(axes[0, 0], frame, "edge_random", "gcc_frac", style=dict(color=color, label=labels.get(gid, gid), marker="o"))
        if data.gid.nunique() > 3:
            raise ValueError("Sampling comparison supports up to three graphs")
        damage_axes(axes[0, 0], "GCC fraction")
    elif name == "fig_rank_overlap":
        numeric(data, ["top_frac", "jaccard"])
        if data.top_frac.duplicated().any() or not data.jaccard.between(0, 1).all():
            raise ValueError("Invalid rank-overlap table")
        fig, axes = axes_grid()
        frame = data.sort_values("top_frac")
        axes[0, 0].plot(frame.top_frac*100, frame.jaccard, color="#9472C4", marker="o")
        axes[0, 0].set(xlabel="Top-ranked nodes (%)", ylabel="Jaccard overlap", ylim=(0, 1.03))
    else:  # same damage, different strategies; never pool distinct f values
        numeric(data, ["frac_removed"])
        levels = sorted(data.frac_removed.unique())
        if len(levels) != 1:
            raise ValueError("Equal-damage comparison requires exactly one frac_removed")
        fig, axes = axes_grid(cols=2)
        strategies = ("node_random", "node_degree", "node_betweenness")
        for ax, metric, label in zip(axes.ravel(), ("gcc_frac", "R_L2"), ("GCC fraction", "Success R")):
            for i, strategy in enumerate(strategies):
                frame = select(data, strategy, metric)
                if frame.seed.duplicated().any():
                    raise ValueError("Duplicate seed in equal-damage comparison")
                vals = frame.value.to_numpy()
                numeric(frame, ["value", "seed"])
                if (frame.seed == -1).all() and len(frame) == 1:
                    sd = 0
                elif (frame.seed >= 0).all() and len(frame) >= 2:
                    sd = vals.std(ddof=1)
                else:
                    raise ValueError("Use one deterministic row or at least two seed repeats")
                ax.bar(i, vals.mean(), color=STYLE[strategy]["color"], width=.55, yerr=sd)
            ax.set_xticks(range(3), ["Random", "Degree", "Betweenness"], fontsize=8)
            ax.set(ylabel=label, title=f"f = {levels[0]:.0%}")
    legend(fig, axes)
    return fig


def schematic():
    fig, axes = axes_grid(cols=3, width=9, height=2.7)
    xy = np.array([[0, .5], [1.05, .95], [.65, .15], [1.45, .15], [2.1, .5]])
    for ax, title, stage in zip(axes.ravel(), ("Intact", "Connected, query lost", "Query restored"), range(3)):
        for u, v in ((0, 1), (1, 4), (0, 2), (2, 3), (3, 4)):
            broken = (u, v) == (1, 4) and stage == 1
            repaired = (u, v) == (1, 4) and stage == 2
            ax.plot(xy[[u,v],0], xy[[u,v],1], color="#9472C4" if repaired else "#B5BDC7",
                    ls="--" if broken else "-", lw=2 if repaired else 1)
        for i, (x, y) in enumerate(xy):
            ax.scatter(x, y, s=230, color=NODE_COLORS["drug" if i == 0 else "disease" if i == 4 else "gene/protein"], zorder=3)
        ax.text(0, .30, "Drug", ha="center", fontsize=9)
        ax.text(2.1, .30, "Disease", ha="center", fontsize=9)
        ax.text(1.05, 1.15, "Protein", ha="center", fontsize=8)
        ax.text(1.05, -.04, "PPI", ha="center", fontsize=8)
        # The lower alternative includes a PPI step; semantic query requires L=2.
        ax.text(1, -.32, "L = 2 succeeds" if stage != 1 else "L = 2 fails", ha="center", fontsize=9)
        ax.set(xlim=(-.3, 2.3), ylim=(-.5, 1.25), title=title)
        ax.axis("off")
    return fig


def render(name, data=None, *, restoration_strategies=RESTORE):
    """Return a figure. Callers own saving and closing. No demo fallback."""
    if name not in CATALOG:
        raise ValueError(f"Unknown template: {name}")
    setup()
    plt.rcParams.update({"font.size": 10, "axes.titlesize": 10,
                         "xtick.labelsize": 8, "ytick.labelsize": 8,
                         "legend.fontsize": 8, "lines.markersize": 3.5})
    schema = CATALOG[name][2]
    if schema == "schematic":
        return schematic()
    if data is None:
        raise ValueError("An input table is required")
    if schema in ("long", "recovery"):
        required(data, ["gid", "strategy", "seed", "frac_removed", "metric", "value"])
        if name != "fig_sampling_comparison" and data.gid.nunique() != 1:
            raise ValueError("Select exactly one gid before rendering")
    if schema == "nodes":
        return degree_distribution(data)
    if schema == "hubs":
        return hubs(data)
    if schema == "prediction":
        return predictions(data)
    if schema == "recovery":
        if (not restoration_strategies or len(set(restoration_strategies)) != len(restoration_strategies)
                or not set(restoration_strategies) <= set(RESTORE)):
            raise ValueError("Choose unique known restoration strategies")
        return recovery(name, data, strategies=restoration_strategies)
    if name == "fig_R_L_heatmap":
        fig, axes = axes_grid()
        mesh = heatmap(axes[0, 0], data)
        fig.colorbar(mesh, ax=axes[0, 0], label="Success R")
        return fig
    if name == "fig_phase_diagram":
        return phase(data)
    if name == "fig_R_theory_vs_sim":
        return theory_groups(data)
    if name in ("fig_fragmentation", "fig_sampling_comparison", "fig_rank_overlap", "fig_equal_damage"):
        return extras(name, data)
    return basic_curves(name, data)
