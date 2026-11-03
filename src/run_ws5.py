"""E's reproducible edge-restoration experiment, with explicit evaluator selection."""
import argparse
import importlib
from pathlib import Path
import time

import numpy as np
import pandas as pd

from .common import (ROOT, graph_dir, load_nodes, load_edges, load_queries,
                     load_order, n_removed, write_json, sha256)
from .restoration import (restore, rank_random, rank_edge_betweenness,
                          rank_relation_type, rank_task_aware, training_path_eids)
from .restoration_evaluation import EdgeRestorationReference, evaluate_c, gcc_fraction

STRATEGIES = ("random", "edge_betweenness", "relation_type", "task_aware")


def run(gid, output_dir, *, evaluator="c", strategies=STRATEGIES,
        seeds=tuple(range(10)), damages=(.3, .5), budgets=(0, .05, .1, .2)):
    if not strategies or len(set(strategies)) != len(strategies) or not set(strategies) <= set(STRATEGIES):
        raise ValueError("Choose unique known strategies")
    if not seeds or len(set(seeds)) != len(seeds) or any(s < 0 or s > 9 for s in seeds):
        raise ValueError("Damage seeds must be a unique nonempty subset of 0..9")
    if not budgets or 0 not in budgets or list(budgets) != sorted(set(budgets)):
        raise ValueError("Budgets must increase strictly and include zero")
    for f in (*damages, *budgets):
        n_removed(f, 1)
    nodes, edges, queries = load_nodes(gid), load_edges(gid), load_queries(gid)
    train = [q for q in queries if q["split"] == "train"]
    test = [q for q in queries if q["split"] == "test"]
    if not train or not test:
        raise ValueError("Nonempty training and test query sets are required")
    # All required member inputs are checked before creating an output directory.
    edge_order = load_order(gid, "edge_betweenness") if "edge_betweenness" in strategies else None
    if evaluator == "c":
        try:
            module = importlib.import_module("src.retrieval")
        except ModuleNotFoundError as exc:
            if exc.name != "src.retrieval":
                raise
            raise RuntimeError("C's src/retrieval.py is required for evaluator=c; no evaluator was substituted") from exc
        retriever = module.Retriever(gid)
        evaluate = lambda mask: evaluate_c(retriever, test, mask)
    elif evaluator == "reference":
        ref = EdgeRestorationReference(nodes, edges)
        evaluate = lambda mask: ref.evaluate(test, mask)
    else:
        raise ValueError("Evaluator must be c or reference")
    orders = {s: load_order(gid, f"edge_random_s{s}") for s in seeds}
    paths = training_path_eids(edges, train)
    out = Path(output_dir)
    if out.exists() and any(out.iterdir()):
        raise FileExistsError(f"Output directory is not empty: {out}; choose a new run directory")
    out.mkdir(parents=True, exist_ok=True)
    (out / "rankings").mkdir()
    metadata = dict(gid=gid, status="running", evaluator=evaluator,
                    result_scope="local independent check" if evaluator == "reference" else "C Retriever integration",
                    strategies=list(strategies), seeds=list(seeds), damages=list(damages), budgets=list(budgets),
                    n_nodes=len(nodes), n_edges=len(edges), n_train=len(train), n_test=len(test),
                    train_query_ids=[q["query_id"] for q in train], test_query_ids=[q["query_id"] for q in test],
                    task_aware="static pre-restoration completable-path counts; failed training queries only",
                    candidate_shortage="relation_type stops when eligible edges are exhausted; never fills with PPI",
                    tie_seed="damage seed + 100 for all randomized ranking functions",
                    budget_denominator="actual edges removed by A's fixed order prefix",
                    query_scope="test split only; entity overlap between train/test is permitted",
                    missing_strategies=sorted(set(STRATEGIES)-set(strategies)),
                    software=dict(numpy=np.__version__, pandas=pd.__version__),
                    source_sha256={p: sha256(ROOT / p) for p in
                                   ("src/restoration.py", "src/run_ws5.py", "src/restoration_evaluation.py")})
    if evaluator == "c":
        metadata["source_sha256"]["src/retrieval.py"] = sha256(Path(module.__file__))
    write_json(out / "provenance.json", metadata)
    started = time.perf_counter()
    rows, perquery, types = [], [], []
    try:
        for damage in damages:
            for seed in seeds:
                removed = orders[seed][:n_removed(damage, len(edges))]
                damaged = np.ones(len(edges), dtype=bool)
                damaged[removed] = False
                ranks = {}
                for strategy in strategies:
                    if strategy == "random":
                        ranks[strategy] = rank_random(removed, seed+100)
                    elif strategy == "edge_betweenness":
                        ranks[strategy] = rank_edge_betweenness(removed, edge_order)
                    elif strategy == "relation_type":
                        ranks[strategy] = rank_relation_type(removed, edges, seed+100)
                    else:
                        ranks[strategy] = rank_task_aware(removed, damaged, paths, seed+100)
                np.savez_compressed(out / "rankings" / f"f{damage:g}__s{seed}.npz", **ranks)
                baseline_queries = evaluate(damaged)
                baseline_gcc = gcc_fraction(len(nodes), edges, damaged)
                for strategy, ranking in ranks.items():
                    for budget in budgets:
                        alive = restore(damaged, ranking, budget)
                        restored = np.flatnonzero(alive & ~damaged)
                        requested = n_removed(budget, len(removed))
                        result = baseline_queries.copy() if budget == 0 else evaluate(alive)
                        gcc = baseline_gcc if budget == 0 else gcc_fraction(len(nodes), edges, alive)
                        if len(restored) > requested or (damaged & ~alive).any():
                            raise AssertionError("Restoration altered surviving edges or exceeded budget")
                        context = dict(gid=gid, strategy="restore_"+strategy, seed=seed, frac_removed=damage,
                                       n_removed=len(removed), damage_frac=damage, budget_frac=budget,
                                       requested_n_restored=requested, n_restored=len(restored),
                                       budget_shortfall=requested-len(restored),
                                       actual_budget_frac=len(restored)/len(removed) if len(removed) else 0,
                                       evaluator=evaluator, n_test_queries=len(test))
                        for metric, value in (("gcc_frac", gcc), ("R_L2", result.success_L2.mean()),
                                              ("R_L3", result.success_L3.mean())):
                            rows.append(dict(**context, metric=metric, value=float(value)))
                        perquery.extend(dict(**context, **row) for row in result.to_dict("records"))
                        counts = edges.iloc[restored].relation.value_counts()
                        for relation in ("drug_protein", "disease_protein", "protein_protein"):
                            types.append(dict(**context, relation=relation, count=int(counts.get(relation, 0))))
                print(f"{gid}: f={damage:g}, seed={seed}, strategies={','.join(strategies)}", flush=True)
        table = pd.DataFrame(rows)
        table.to_csv(out / f"{gid}__restoration.csv", index=False, lineterminator="\n")
        pd.DataFrame(perquery).to_csv(out / f"{gid}__test_perquery.csv", index=False, lineterminator="\n")
        pd.DataFrame(types).to_csv(out / f"{gid}__restored_edge_types.csv", index=False, lineterminator="\n")
        keys = ["gid", "strategy", "seed", "damage_frac", "metric"]
        base = table[table.budget_frac == 0][keys+["value"]].rename(columns={"value": "baseline"})
        gains = table.merge(base, on=keys, validate="many_to_one")
        gains["gain"] = gains.value-gains.baseline
        gains["gain_per_1000_edges"] = np.where(gains.n_restored > 0,
                                               1000*gains.gain/gains.n_restored.replace(0, np.nan), np.nan)
        gains.to_csv(out / f"{gid}__paired_gains.csv", index=False, lineterminator="\n")
        summary = gains.groupby(["gid", "strategy", "damage_frac", "budget_frac", "metric"]).agg(
            gain_mean=("gain", "mean"), gain_sd=("gain", "std"), n_seeds=("seed", "nunique"),
            restored_min=("n_restored", "min"), restored_max=("n_restored", "max"),
            shortfall_seeds=("budget_shortfall", lambda x: int((x>0).sum())))
        summary.to_csv(out / f"{gid}__summary.csv", lineterminator="\n")
        metadata.update(status="complete", elapsed_seconds=time.perf_counter()-started,
                        n_states=len(table)//3, n_metric_rows=len(table), n_perquery_rows=len(perquery))
    except Exception as exc:
        metadata.update(status="failed", error=str(exc), elapsed_seconds=time.perf_counter()-started)
        raise
    finally:
        write_json(out / "provenance.json", metadata)
    return table


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("gid")
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--evaluator", choices=("c", "reference"), default="c")
    p.add_argument("--strategies", nargs="+", choices=STRATEGIES, default=list(STRATEGIES))
    p.add_argument("--seeds", nargs="+", type=int, default=list(range(10)))
    args = p.parse_args()
    run(args.gid, args.output_dir, evaluator=args.evaluator, strategies=args.strategies, seeds=args.seeds)


if __name__ == "__main__":
    main()
