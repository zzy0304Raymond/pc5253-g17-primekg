"""Run the four fixed WS3 damage strategies and the edge-only hop scan."""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from .common import (
    EDGE_LEVELS, NODE_LEVELS, RESULT_COLUMNS, ROOT, SEEDS,
    graph_dir, load_order, load_queries, n_removed, sha256, write_json,
)
from .retrieval import Retriever

SCAN_SEEDS = (0, 1, 2)
DESIGNS = (
    ("edge_random", EDGE_LEVELS, SEEDS),
    ("node_random", NODE_LEVELS, SEEDS),
    ("node_degree", NODE_LEVELS, (-1,)),
    ("node_betweenness", NODE_LEVELS, (-1,)),
)


def run(gid):
    queries = load_queries(gid)
    groups = np.array([q["group"] for q in queries])
    if set(groups) != {"single", "multi"}:
        raise ValueError("WS3 requires nonempty single-path and multi-path query groups")
    redundancy = np.array([q["redundancy_m"] for q in queries])
    retriever = Retriever(gid)
    records, per_query, input_orders = [], {}, []
    outdir = ROOT / "results" / "ws3"

    for strategy, levels, seeds in DESIGNS:
        for seed in seeds:
            order_name = strategy if seed == -1 else f"{strategy}_s{seed}"
            order = load_order(gid, order_name)
            input_orders.append(order_name)
            scan = strategy == "edge_random" and seed in SCAN_SEEDS
            frames = []
            for fraction in levels:
                removed = n_removed(fraction, len(order))
                alive = np.ones(len(order), dtype=bool)
                alive[order[:removed]] = False
                masks = {"edge_alive" if strategy.startswith("edge_") else "node_alive": alive}
                frame = retriever.evaluate(queries, compute_dist=scan, **masks)
                success = frame.s_alive.to_numpy() > 0
                if fraction == 0 and (not success.all() or not np.array_equal(frame.s_alive, redundancy)):
                    raise AssertionError(f"Intact graph path counts disagree with queries for {gid}")
                metrics = {"R_L2": success.mean()}
                for group in ("single", "multi"):
                    metrics[f"R_L2_{group}"] = success[groups == group].mean()
                if scan:
                    distance = frame.d_ppi.to_numpy()
                    l3, l4, unlimited = distance <= 1, distance <= 2, np.isfinite(distance)
                    if not np.array_equal(distance == 0, success) or np.any(
                        (success & ~l3) | (l3 & ~l4) | (l4 & ~unlimited)
                    ):
                        raise AssertionError("Hop results contradict two-hop counts or monotonicity")
                    metrics.update(R_L3=l3.mean(), R_L4=l4.mean(), R_Linf=unlimited.mean())
                records.extend((gid, strategy, seed, fraction, removed, metric, value)
                               for metric, value in metrics.items())
                frame.insert(1, "frac_removed", fraction)
                frames.append(frame)
            per_query[f"{gid}__perquery__{strategy}__s{seed}.csv"] = pd.concat(frames, ignore_index=True)
            print(f"{gid}: {strategy}, seed {seed} complete", flush=True)

    summary = pd.DataFrame(records, columns=RESULT_COLUMNS)
    outdir.mkdir(parents=True, exist_ok=True)
    for filename, frame in per_query.items():
        frame.to_csv(outdir / filename, index=False, lineterminator="\n")
    summary.to_csv(outdir / f"{gid}__retrieval.csv", index=False, lineterminator="\n")
    random_edge = summary[summary.strategy == "edge_random"]
    checks = {}
    for group in ("single", "multi"):
        series = random_edge[random_edge.metric == f"R_L2_{group}"].groupby("n_removed").value.mean()
        p = 1 - series.index.to_numpy() / len(retriever.edges)
        predicted = (1 - (1 - p[:, None] ** 2) ** redundancy[groups == group]).mean(axis=1)
        errors = np.abs(series.to_numpy() - predicted)
        checks[group] = {
            "max_abs_error": float(errors.max()),
            "within_0_05": bool((errors <= .05).all()),
        }
    data = graph_dir(gid)
    inputs = ["nodes.csv", "edges.csv", "queries.json"]
    inputs.extend(f"orders/{name}.npy" for name in input_orders)
    write_json(outdir / f"{gid}__provenance.json", {
        "gid": gid,
        "n_queries": len(queries),
        "strategies": {strategy: {"seeds": list(seeds), "levels": levels}
                       for strategy, levels, seeds in DESIGNS},
        "hop_scan": {"strategy": "edge_random", "seeds": SCAN_SEEDS, "L": [2, 3, 4, "inf"]},
        "distance_encoding": {"blank": "not computed", "inf": "computed, no path"},
        "independent_edge_model_check": checks,
        "input_sha256": {name: sha256(data / name) for name in inputs},
        "source_sha256": {name: sha256(Path(__file__).with_name(name))
                          for name in ("retrieval.py", "run_ws3.py", "common.py")},
    })
    print(f"Saved {len(summary)} metric rows and {len(per_query)} per-query tables in {outdir}")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gid", nargs="?", default="primekg_5000_bfs_v1")
    run(parser.parse_args().gid)


if __name__ == "__main__":
    main()
