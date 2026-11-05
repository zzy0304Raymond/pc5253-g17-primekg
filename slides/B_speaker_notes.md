# B · Slide 5: Targeted failure and central nodes

## Script

Random failure treats every node equally. We now ask what happens when we deliberately remove the most central nodes first. We compute degree and betweenness on the intact graph, then keep those rankings fixed throughout the experiment.

Both attacks fragment the graph much faster than random removal. After removing half the nodes, the largest component contains about 49 percent of the original nodes under random failure, compared with 23 percent under degree attack and 21 percent under betweenness attack. These are fractions of the original graph, so directly deleted nodes also count as lost.

The composition chart shows that almost all of the top one percent are proteins or diseases. Removing those nodes also removes all their incident relations. The black dashed curve is the degree-based theoretical reference. Its difference from the real attack curve suggests that the degree distribution alone does not explain every detail; D will examine this later.

So far, we have measured whether nodes remain connected. C will now ask whether the damaged graph can still answer the same drug–disease queries.

## Sources and delivery notes

- Main graph: `primekg_5000_bfs_v1`.
- Structural results: `results/primekg_5000_bfs_v1/ws2_attack_results_long.csv`.
- Hub composition: `results/primekg_5000_bfs_v1/ws2_hub_composition.csv`.
- Theory overlay: `figures/act1/primekg_5000_bfs_v1/fig_attack_theory.png` and `results/ws4/primekg_5000_bfs_v1__attack_overlay.csv`.
- Random curves: ten-seed mean and sample SD. Attack rankings are fixed, so no random-seed uncertainty band is claimed for them.
- About 190 words; rehearse at your own speaking pace.
