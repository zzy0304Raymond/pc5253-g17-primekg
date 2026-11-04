"""Centrality rankings for WS2 targeted-attack experiments."""

import argparse

from pathlib import Path

import networkx as nx
import numpy as np

try:
    from .common import (
        check_order,
        graph_dir,
        load_edges,
        load_nodes,
        structural_graph,
    )
except ImportError:
    from common import (
        check_order,
        graph_dir,
        load_edges,
        load_nodes,
        structural_graph,
    )


def degree_order(gid):
    """
    Rank all nodes by decreasing degree.
    Ties are broken by increasing nid.
    """
    g = structural_graph(gid)
    nodes = load_nodes(gid)

    degree = dict(g.degree())

    order = np.array(
        sorted(
            nodes.nid.astype(int),
            key=lambda nid: (-degree[int(nid)], int(nid)),
        ),
        dtype=np.int64,
    )

    return check_order(order, len(nodes)), degree


def node_betweenness_order(gid, k=100, seed=42):
    """
    Rank nodes by decreasing betweenness centrality.

    If k is None, exact betweenness is calculated.
    Otherwise, k sampled source nodes are used for approximation.
    """
    g = structural_graph(gid)
    nodes = load_nodes(gid)

    if k is None or k >= g.number_of_nodes():
        scores = nx.betweenness_centrality(
            g,
            normalized=True,
        )
    else:
        scores = nx.betweenness_centrality(
            g,
            k=k,
            normalized=True,
            seed=seed,
        )

    order = np.array(
        sorted(
            nodes.nid.astype(int),
            key=lambda nid: (-scores[int(nid)], int(nid)),
        ),
        dtype=np.int64,
    )

    return check_order(order, len(nodes)), scores


def edge_betweenness_order(gid, k=100, seed=42):
    """
    Rank edges by decreasing approximate edge betweenness.

    NetworkX returns scores keyed by (u, v), but the shared project
    contract requires a permutation of stable eid values.
    """
    g = structural_graph(gid)
    edges = load_edges(gid)

    # NetworkX edge_betweenness_centrality does not provide the same
    # k-sampling interface as node betweenness in our installed version.
    # We therefore use edge_betweenness_centrality_subset with sampled
    # source nodes and all graph nodes as targets.
    rng = np.random.default_rng(seed)
    all_nodes = np.array(sorted(g.nodes()), dtype=np.int64)

    if k is None or k >= len(all_nodes):
        scores = nx.edge_betweenness_centrality(
            g,
            normalized=True,
        )
    else:
        sources = rng.choice(all_nodes, size=k, replace=False).tolist()
        scores = nx.edge_betweenness_centrality_subset(
            g,
            sources=sources,
            targets=all_nodes.tolist(),
            normalized=True,
        )

    # Structural graph is undirected, so (u,v) and (v,u) are identical.
    def score_for_edge(u, v):
        return scores.get((int(u), int(v)), scores.get((int(v), int(u)), 0.0))

    edge_scores = {
        int(row.eid): score_for_edge(row.u, row.v)
        for row in edges.itertuples(index=False)
    }

    order = np.array(
        sorted(
            edges.eid.astype(int),
            key=lambda eid: (-edge_scores[int(eid)], int(eid)),
        ),
        dtype=np.int64,
    )

    return check_order(order, len(edges)), edge_scores


def save_order(gid, name, order):
    """Save a validated node/edge attack order into the graph's orders folder."""
    if not name.startswith(("node_", "edge_")):
        raise ValueError("order name must start with node_ or edge_")

    total = len(load_nodes(gid)) if name.startswith("node_") else len(load_edges(gid))
    order = check_order(order, total)

    path = graph_dir(gid) / "orders" / f"{name}.npy"
    path.parent.mkdir(parents=True, exist_ok=True)
    np.save(path, order, allow_pickle=False)
    return path


def print_top_nodes(gid, order, scores, top_n=10, score_name="score"):
    """Print the highest-ranked nodes together with biomedical metadata."""
    nodes = load_nodes(gid).set_index("nid")

    print(f"\nTop {top_n} nodes by {score_name}")
    print("-" * 90)
    print(f"{'rank':<6}{'nid':<8}{score_name:<18}{'node_type':<18}node_name")

    for rank, nid in enumerate(order[:top_n], start=1):
        nid = int(nid)
        row = nodes.loc[nid]
        print(
            f"{rank:<6}{nid:<8}{scores[nid]:<18.6f}"
            f"{row['node_type']:<18}{row['node_name']}"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Compute WS2 centrality rankings."
    )

    parser.add_argument(
        "--gid",
        default="primekg_5000_bfs_v1",
        help="Processed graph ID.",
    )

    args = parser.parse_args()
    gid = args.gid

    print(f"Loading {gid} ...")
    g = structural_graph(gid)
    print(
        f"Graph loaded: {g.number_of_nodes()} nodes, "
        f"{g.number_of_edges()} structural edges."
    )

    # 1. Degree ranking
    degree_rank, degree_scores = degree_order(gid)
    print_top_nodes(
        gid,
        degree_rank,
        degree_scores,
        top_n=10,
        score_name="degree",
    )

    path = save_order(gid, "node_degree", degree_rank)
    print(f"\nSaved degree order to: {path}")

    # 2. Approximate node betweenness ranking
    print("\nComputing approximate node betweenness (k=100, seed=42) ...")
    node_bc_rank, node_bc_scores = node_betweenness_order(
        gid,
        k=100,
        seed=42,
    )

    print_top_nodes(
        gid,
        node_bc_rank,
        node_bc_scores,
        top_n=10,
        score_name="betweenness",
    )

    path = save_order(gid, "node_betweenness", node_bc_rank)
    print(f"\nSaved node betweenness order to: {path}")

    # 3. Approximate edge betweenness ranking
    print("\nComputing approximate edge betweenness (k=100, seed=42) ...")
    edge_bc_rank, edge_bc_scores = edge_betweenness_order(
        gid,
        k=100,
        seed=42,
    )

    path = save_order(gid, "edge_betweenness", edge_bc_rank)
    print(f"\nSaved edge betweenness order to: {path}")

    print("\nTop 10 edges by approximate edge betweenness")
    print("-" * 75)

    edges = load_edges(gid).set_index("eid")
    nodes = load_nodes(gid).set_index("nid")

    for rank, eid in enumerate(edge_bc_rank[:10], start=1):
        eid = int(eid)
        edge = edges.loc[eid]
        u = int(edge["u"])
        v = int(edge["v"])

        print(
            f"{rank:>2}. eid={eid:<6} "
            f"BC={edge_bc_scores[eid]:.6f} | "
            f"{nodes.loc[u, 'node_name']} -- "
            f"{nodes.loc[v, 'node_name']} "
            f"[{edge['relation']}]"
        )


if __name__ == "__main__":
    main()