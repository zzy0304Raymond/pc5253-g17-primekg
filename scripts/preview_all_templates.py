"""Explicit demo gallery; synthetic examples never enter production results.

python -m scripts.preview_all_templates --output-dir D:/path/to/gallery
"""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.common import ROOT
from src.figure_templates import CATALOG, RESTORE, render
from src.plotting import save


def demo_tables():
    # All values in this function are synthetic layout examples, not experiments.
    rows = []
    f = np.array([0, .05, .1, .2, .3, .4, .5, .6, .7, .8, .85, .9, .95, .97, .99])
    for strategy in ("edge_random", "node_random", "node_degree", "node_betweenness", "theory_bond", "theory_site", "theory_attack"):
        deterministic = strategy.startswith("theory") or strategy in ("node_degree", "node_betweenness")
        for seed in ([-1] if deterministic else range(10)):
            p = 1-f
            jitter = 1 if seed == -1 else 1 + .05*np.sin(seed*1.7)
            if strategy in ("edge_random", "theory_bond"):
                s = 1-(f**6)
            elif strategy in ("node_random", "theory_site"):
                s = p**1.1
            elif strategy in ("node_degree", "theory_attack"):
                s = p**4
            else:
                s = p**3
            s = np.clip(s*jitter, 0, 1)
            curves = {"gcc_frac": s, "isolated_frac": f*(1-f), "n_components": 5000*f*(1-f),
                      "avg_degree": 35*p, "R_L2_single": p**2,
                      "R_L2_multi": 1-(1-p*p)**3,
                      "R_L2": .5*p*p + .5*(1-(1-p*p)**3),
                      "R_L3": 1-f**2.5, "R_L4": 1-f**3.5, "R_Linf": 1-f**5}
            curves["corr_penalty"] = .15*np.sin(np.pi*f)*(1 if strategy == "node_degree" else .7)
            for metric, values in curves.items():
                values = values if deterministic else values*(1+.035*np.sin(seed*2+f*8)*f)
                for frac, value in zip(f, values):
                    rows.append(dict(gid="DEMO_ONLY", strategy=strategy, seed=seed,
                                     frac_removed=frac, n_removed=round(frac*5000), metric=metric, value=float(value)))
    long = pd.DataFrame(rows)
    # Bound success fractions; this applies only to deliberately synthetic examples.
    mask = long.metric.str.startswith("R_")
    long.loc[mask, "value"] = long.loc[mask, "value"].clip(0, 1)
    hubs = pd.DataFrame([dict(strategy=strategy, top_frac=top, node_type=typ, fraction=value)
                        for strategy in ("node_degree", "node_betweenness") for top in (.01,.05,.1)
                        for typ,value in zip(("drug","disease","gene/protein"),(.10+top,.15, .75-top))])
    prediction = pd.DataFrame([dict(model=model, damage_frac=damage, metric=metric, value=value)
                              for damage in (.3,.5) for metric in ("AUC","Brier")
                              for model,value in zip(("theory","logistic"), (.77,.81) if metric=="AUC" else (.19,.17))])
    recovery = []
    for damage in (.3,.5):
        for seed in range(10):
            for horizon in (2,3):
                baseline = .4 + (horizon-2)*.15 - (damage-.3)*.4 + .025*np.sin(seed)
                for i,strategy in enumerate(RESTORE):
                    for budget in (0,.05,.1,.2):
                        gain = (1+0.28*i)*(1-np.exp(-budget*5))*.22*(1+.10*np.sin(seed*1.3))
                        recovery.append(dict(gid="DEMO_ONLY", strategy=strategy, seed=seed, metric=f"R_L{horizon}",
                                             frac_removed=damage, damage_frac=damage, budget_frac=budget,
                                             n_restored=round(10000*damage*budget), value=baseline+gain))
    return long, hubs, prediction, pd.DataFrame(recovery)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    a = parser.parse_args()
    a.output_dir.mkdir(parents=True, exist_ok=True)
    examples = a.output_dir / "example_data"
    examples.mkdir(exist_ok=True)
    long, hub, prediction, recovery = demo_tables()
    real = pd.read_csv(ROOT / "results/ws1/primekg_5000_bfs_v1__random.csv")
    nodes = pd.read_csv(ROOT / "data/processed/primekg_5000_bfs_v1/node_features.csv")
    comparisons = pd.concat([pd.read_csv(ROOT / f"results/ws1/{gid}__random.csv") for gid in
                             ("primekg_2000_bfs_v1", "primekg_5000_bfs_v1", "primekg_full_v1")])
    overlap = pd.DataFrame({"top_frac": [.01,.05,.1], "jaccard": [.42,.55,.61]})
    tables = {"nodes": nodes, "hubs": hub, "prediction": prediction,
              "recovery": recovery, "overlap": overlap, "schematic": None}
    images = []
    manifest = []
    for name, (owner,title,schema) in CATALOG.items():
        data = tables.get(schema, long)
        source = "DEMO · synthetic values"
        if name in ("fig_degree_dist", "fig_S_random_edge", "fig_S_random_node", "fig_fragmentation"):
            data = nodes if schema == "nodes" else real
            source = "A · archived results"
        if name == "fig_sampling_comparison":
            data, source = comparisons, "A · archived results"
        if name == "fig_equal_damage":
            data = long[long.frac_removed == .3]
        if schema == "schematic":
            source = "Concept schematic"
        fig = render(name, data)
        # Every synthetic example is visibly marked, including its PDF and SVG.
        fig.suptitle(f"{owner} · {title}" + ("  |  DEMO" if source.startswith("DEMO") else ""),
                     fontsize=11, fontweight="normal")
        paths = save(fig, "templates", name, output_dir=a.output_dir / owner, formats=("png","pdf","svg"))
        plt.close(fig)
        images.append((paths[0], owner, title, source))
        if data is not None:
            exported = data.copy()
            exported["demo_only"] = source.startswith("DEMO")
            exported.to_csv(examples / f"{name}.csv", index=False, lineterminator="\n")
        manifest.append(dict(template=name, owner=owner, schema=schema, source=source,
                             n_rows=len(data) if data is not None else 0, outputs=[str(p) for p in paths]))
    # Contact sheet only: individual full-resolution figures are also delivered.
    fig, axes = plt.subplots(5,4,figsize=(16,15.5),layout="constrained")
    for ax, (path,owner,title,source) in zip(axes.ravel(),images):
        ax.imshow(plt.imread(path))
        ax.axis("off")
    fig.savefig(a.output_dir / "G17_all_templates_preview.png", dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    (a.output_dir / "gallery_manifest.json").write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
    print(f"Rendered {len(images)} templates and overview to {a.output_dir}")


if __name__ == "__main__":
    main()
