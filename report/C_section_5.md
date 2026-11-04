# 5. Functional robustness and query horizon

## 5.1 Retrieval under controlled damage

We evaluated the same 200 drug–disease pairs on every damaged version of the 5,000-node PrimeKG subgraph. All pairs had at least one two-hop path before removal. A two-hop query succeeds if one protein retains both its drug and disease links. For longer paths, the query may traverse protein–protein interactions between the two terminal proteins. If either endpoint is deleted, the query fails and remains in the denominator. We used the frozen random edge and node orders for ten seeds and the fixed degree and betweenness node orders. We scanned hop limits of 2, 3, 4 and unlimited using the same three random edge orders at all limits.

## 5.2 Connectivity and retrieval separate

With 50% of the edges removed at random, the largest connected component retained 98.2% of the original nodes, averaged across ten seeds. Two-hop retrieval succeeded for 43.3% of the queries on those same damage states, a gap of 54.9 percentage points. Protein–protein links contribute to global connectivity. A two-hop query instead depends on surviving drug–protein and disease–protein relations incident to a common protein.

Node deletion also removes potential query endpoints. At 50% node removal, the two-hop success rate was 15.55% under random removal, 0% under degree-targeted removal, and 0.5% under betweenness-targeted removal. The targeted values each describe a single fixed deletion order.

## 5.3 Backup paths and hop limits

At 50% random edge removal, queries with multiple original paths retained a 60.7% success rate, compared with 25.9% for queries with one path. Under independent edge retention with probability p, each two-hop path survives with probability p². For a query with m distinct shared proteins, the predicted probability of retaining at least one path is 1 − (1 − p²)^m. Our fixed-count sampling uses this model as a benchmark. Across the main graph's tested fractions, the largest absolute group-mean deviations from the benchmark were 2.10 percentage points for single-path queries and 3.25 points for multiple-path queries. The 2,000-node development graph had a 9.05-point maximum deviation for the single-path group, even though all independently checked per-query results matched.

For the matched three-seed hop scan, 50% edge removal gave mean success rates of 40.3%, 84.5%, 89.5%, and 89.5% at limits of 2, 3, 4, and unlimited hops. At 90% removal the corresponding values were 2.0%, 10.0%, 28.7%, and 37.0%. Longer protein chains can therefore preserve access to some queries after short paths have disappeared. The curves describe a finite BFS-sampled graph and a fixed benchmark of initially retrievable pairs. They measure the availability of association paths in the graph. Shaded intervals in the curves show sample standard deviation across removal seeds.

**Figures.** `fig_S_vs_R` compares the structural and functional fractions. `fig_R_by_group` compares the two redundancy groups. `fig_R_L_curves` and `fig_R_L_heatmap` show the matched hop scan.

**Reproduction.** The summary and per-query tables in `results/ws3` record the graph, damage strategy, seed and fraction. The provenance file records the exact input and code digests. A's structural values are in `results/ws1`.
