# E speaker notes

Source: formal C-Retriever runs in results/ws5/final/primekg_5000_bfs_v1.
All gains use sixty test query IDs and ten damage seeds. Rankings see only the
140 training query IDs. The static task-aware definition is unchanged.

## Slide 1 · When AI forgets

Knowledge graphs connect facts that a retrieval task may need to combine.
We ask what happens when some of those connections disappear. Our experiments
compare how the graph fragments, which semantic queries still work, and how a
limited restoration budget can recover the lost function. We use one shared
PrimeKG graph and fixed damage orders throughout the group project.

## Slide 2 · Connectivity and retrieval

The upper route answers a two-hop drug–protein–disease query. Delete one edge
and that query fails, even though a longer route still connects the endpoints.
Restoring the upper edge repairs the two-hop query. If we allow an extra hop,
the lower route can also become useful. This small example shows why a
connectivity measure and a retrieval metric can respond differently to damage.

## Slide 12 · Restoration for two-hop queries

All policies start from matching damaged masks. At fifty-percent damage and a
twenty-percent restoration budget, relation-type selection gains 48.5 percentage
points, edge betweenness 42.0, static task-aware 24.8 and random selection 13.2.
Task-aware selection starts well at the smaller budget, but its positive-score
set contains only a few dozen edges. After selecting those edges, the static
rule spends most additional budget on randomly ordered zero-score candidates.

## Slide 13 · Restoration for three-hop queries

The same restored graphs give a different comparison when a query can use one
protein–protein interaction. At fifty-percent damage and twenty-percent budget,
the mean gains are 16.5 points for edge betweenness and 15.7 for relation-type
selection, followed by 12.3 for static task-aware and 8.3 for random restoration.
The first two means are close relative to their seed variation. These curves
describe the horizon and budget dependence without establishing significance.

## Slide 14 · Robustness depends on the task

The policy with the largest structural gain can differ from the policy with
the largest two-hop retrieval gain. We therefore need to specify the task and
the damage budget when discussing robustness. Our measurements concern a BFS
subgraph and selected positive queries. The query split may share entities.
D's theory pages still need integration before the complete group presentation
and the fourteen-minute rehearsal can be finalized.

## Q&A

- Why did static task-aware not win at every budget? Its positive-score candidates
  are exhausted before even the 5% budget. The remaining candidates include PPI
  edges in random tie order. Relation type keeps spending on endpoint relations.
- Are scores recomputed? No. They are fixed at the initial damaged state.
- Do paths with two missing edges get a score? No. One edge cannot complete them.
- Were test queries used for ranking? No. Only training IDs enter scoring.
- Is the split entity-disjoint? No. Query IDs may share drugs, diseases and proteins.
- Does betweenness significantly beat relation type at L=3? We report means and
  sample SD, without a significance claim.
- Is C integrated? Yes. All formal runs use C's Retriever. Across 640 states,
  metrics and per-query L2/L3 outputs matched the earlier independent evaluator.
- What happens at candidate exhaustion? The policy stops and records unspent
  budget. No shortage occurred at the reported budgets.
- Can all policies reconstruct the original graph? Complete candidate rankings
  can. Relation-type selection excludes PPI and cannot fully reconstruct it.

E's speaking allocation is about 3.5 minutes across opening and closing.
The scripts are prepared for rehearsal; actual timing remains to be measured.
