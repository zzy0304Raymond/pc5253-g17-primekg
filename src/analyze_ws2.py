"""WS2 hub composition and centrality-overlap analysis."""

import argparse
import numpy as np
import pandas as pd

from .common import ROOT, load_nodes, load_order


def jaccard(a, b):
    """Jaccard similarity between two sets."""
    a = set(a)
    b = set(b)
    return len(a & b) / len(a | b)


def composition(nodes, ranked_nids, top_n, ranking_name, top_frac):
    """Entity-type composition among the top-ranked nodes."""
    selected = nodes[nodes["nid"].isin(ranked_nids[:top_n])]

    counts = (
        selected["node_type"]
        .value_counts()
        .rename_axis("node_type")
        .reset_index(name="count")
    )

    counts["fraction"] = counts["count"] / top_n
    counts["ranking"] = ranking_name
    counts["top_fraction"] = top_frac
    counts["top_n"] = top_n

    return counts


def main():
    parser = argparse.ArgumentParser(
        description="Analyze WS2 centrality rankings and hub composition."
    )

    parser.add_argument(
        "--gid",
        default="primekg_5000_bfs_v1",
        help="Processed graph ID.",
    )

    args = parser.parse_args()
    gid = args.gid

    nodes = load_nodes(gid)

    degree_order = load_order(gid, "node_degree")
    betweenness_order = load_order(gid, "node_betweenness")

    n = len(nodes)

    out_dir = ROOT / "results" / gid
    out_dir.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------
    # Overall graph composition
    # ---------------------------------------------------------
    overall = (
        nodes["node_type"]
        .value_counts()
        .rename_axis("node_type")
        .reset_index(name="count")
    )
    overall["fraction"] = overall["count"] / n

    print("\nOverall graph composition")
    print(overall.to_string(index=False))

    # ---------------------------------------------------------
    # Top 1%, 5%, 10%
    # ---------------------------------------------------------
    fractions = [0.01, 0.05, 0.10]

    composition_results = []
    overlap_results = []

    for frac in fractions:
        top_n = int(round(frac * n))

        degree_top = degree_order[:top_n]
        bc_top = betweenness_order[:top_n]

        composition_results.append(
            composition(
                nodes,
                degree_order,
                top_n,
                "degree",
                frac,
            )
        )

        composition_results.append(
            composition(
                nodes,
                betweenness_order,
                top_n,
                "betweenness",
                frac,
            )
        )

        jac = jaccard(degree_top, bc_top)

        overlap_results.append(
            {
                "top_fraction": frac,
                "top_n": top_n,
                "intersection": len(
                    set(degree_top) & set(bc_top)
                ),
                "jaccard": jac,
            }
        )

    composition_df = pd.concat(
        composition_results,
        ignore_index=True,
    )

    overlap_df = pd.DataFrame(overlap_results)

    # ---------------------------------------------------------
    # Save
    # ---------------------------------------------------------
    overall.to_csv(
        out_dir / "ws2_overall_composition.csv",
        index=False,
    )

    composition_df.to_csv(
        out_dir / "ws2_hub_composition.csv",
        index=False,
    )

    overlap_df.to_csv(
        out_dir / "ws2_degree_betweenness_overlap.csv",
        index=False,
    )

    # ---------------------------------------------------------
    # Print useful summaries
    # ---------------------------------------------------------
    print("\nHub composition")
    print("-" * 70)

    for frac in fractions:
        print(f"\nTop {int(frac * 100)}%")

        subset = composition_df[
            composition_df["top_fraction"] == frac
        ]

        print(
            subset[
                ["ranking", "node_type", "count", "fraction"]
            ].to_string(index=False)
        )

    print("\nDegree vs Betweenness overlap")
    print("-" * 70)
    print(overlap_df.to_string(index=False))


if __name__ == "__main__":
    main()