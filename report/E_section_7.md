# 7. Network-informed restoration

## 7.1 Shared damage states and repair budgets

We evaluated restoration on the main 5,000-node graph using C's `Retriever` and B's original edge-betweenness order. For each of ten random damage seeds, we removed the prescribed prefix of the shared edge order at deletion fractions 0.3 and 0.5. Every strategy and budget began from a fresh copy of that same damaged mask. Nodes remained present throughout these edge-only experiments.

Budgets allowed restoration of 0%, 5%, 10% or 20% of the actually removed edges, rounded using the shared Python-rounding convention. At the largest budget, the 30% and 50% damage states permitted restoration of 7,073 and 11,789 relations, respectively. Candidates were existing relations deleted by the simulation. Relation-type restoration stopped if eligible candidates were exhausted and reported its actual expenditure. No candidate shortage occurred at the tested budgets.

The query split contained 140 training and 60 test query IDs. Rankings used training queries only. We measured GCC fraction and success on the test queries at horizons L=2 and L=3. For each seed we subtracted its zero-budget baseline before aggregating the gain. Results report the mean and sample standard deviation across the ten damage seeds. The zero-budget baseline was identical across all four strategies.

## 7.2 Four restoration policies

**Random** shuffled all removed edges. **Edge betweenness** restored removed edges in B's fixed, original-graph ranking. **Relation type** randomly selected from deleted drug–protein and disease–protein relations, excluding protein–protein interactions. This control tests how much retrieval recovery comes from selecting the relevant relation categories.

**Static task-aware** scored removed edges using training queries that had no surviving two-hop path. A path contributed one point to its missing edge if its other edge survived. A path missing both relations contributed no point, and an already successful query contributed no score. An edge could accumulate points from several completable training paths. Scores were computed once per initial damaged state, with random tie breaking. Zero-score candidates remained in the ranking. All randomized rankings used the damage seed plus 100. Different budgets used prefixes of the same ranking.

## 7.3 Recovery depends on budget and query horizon

At 50% initial edge loss and a 20% repair budget, all four policies improved two-hop retrieval, but their mean gains differed:

| Policy | L=2 gain, percentage points | L=3 gain, percentage points |
|---|---:|---:|
| Random | 13.17 ± 2.77 | 8.33 ± 5.77 |
| Edge betweenness | 42.00 ± 3.99 | 16.50 ± 7.13 |
| Relation type | 48.50 ± 6.69 | 15.67 ± 7.34 |
| Static task-aware | 24.83 ± 6.31 | 12.33 ± 6.63 |

Relation-type restoration had the highest mean two-hop gain in this setting. Edge betweenness had the highest mean three-hop gain, exceeding relation type by 0.83 percentage points. This small difference is descriptive; we did not perform a significance test. The comparison also concerns gains relative to separate L-specific baselines, rather than a claim that the larger horizon has a lower final success rate.

The ranking changed with budget. At 30% damage and a 5% repair budget, static task-aware restoration had the highest mean L=2 gain at 12.67 points, compared with 11.00 for edge betweenness, 7.00 for relation type and 1.17 for random restoration. Increasing the budget to 20% gave gains of 15.50, 23.67, 27.50 and 6.00 points in the same policy order. A single budget therefore does not characterize a restoration policy's performance.

The structural outcome favored a different policy at 50% damage and 20% budget. Edge betweenness increased GCC fraction by 1.782 percentage points, compared with 0.584 for random, 0.610 for relation type and 0.670 for static task-aware restoration. The policy with the largest structural gain thus differed from the one with the largest two-hop retrieval gain in this experiment.

## 7.4 Interpreting the static score

The static score prioritized a small candidate set. Across the ten main-graph damage seeds, 31–46 removed edges had positive scores after 30% damage and 62–87 after 50% damage. Even the 5% budget exceeded these counts: positive-score candidates occupied less than 3% of that budget. Once these candidates were selected, additional budget was spent on randomly ordered zero-score edges. This follows directly from the implemented static rule and explains its early rise followed by slower additional gains.

The recovered relation mix provides complementary evidence. At 50% damage and 20% budget, protein–protein interactions constituted about 76.0% of static task-aware restorations and 68.1% of edge-betweenness restorations. Relation-type restoration assigned its entire expenditure to terminal relations. Two-hop paths require those terminal links, whereas a three-hop path can also use a protein–protein interaction. These differences help interpret the observed outcomes, although the composition analysis alone does not isolate a causal contribution from each edge category.

All results refer to the shared positive-query benchmark. Test query IDs can share entities with training queries, and uncertainty across damage seeds does not estimate variation across newly sampled tasks or graphs. The task-aware score was designed for two-hop training paths and was not retuned for L=3.

**Figures and source tables.** `fig_restoration` shows the two damage levels and query horizons; `fig_gain_per_edge` normalizes gains by actual restored edges; `fig_restoration_gcc` and `fig_restored_edge_types` provide structural and relation-type comparisons. Formal runs are in `results/ws5/final/{gid}`. `E_results_table.csv`, `E_static_score_diagnostics.csv` and `E_edge_type_composition.csv` contain the report's numerical evidence. All four policies have also been run on the 2,000-node development graph.
