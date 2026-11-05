# B · Slide 5: Targeted failure and central nodes

## Script

Random failure treats every node equally. We now ask what happens when we deliberately remove the most central nodes first. We compute degree and betweenness on the intact graph, and then keep those rankings fixed throughout the experiment.

Both targeted attacks fragment the graph much more severely than random removal. After removing half of the nodes, the largest connected component contains about 49 percent of the original graph under random failure, compared with only 23 percent under degree attack and 21 percent under betweenness attack. These are fractions of the original graph, so directly removed nodes also count as lost.

On the right, we look at who these central nodes are. Disease nodes make up only 5.66 percent of the full graph, but they account for 14 to 16 percent of the top one percent central nodes, so diseases are clearly over-represented. Degree and betweenness also identify substantially overlapping critical nodes: 41 of the top 50 nodes are shared, with a Jaccard similarity of 0.695. This helps explain why the two targeted-attack curves are so similar.

Finally, the black dashed curve is the degree-based theoretical reference. It captures the overall collapse pattern, but does not perfectly match the empirical degree attack. This suggests that degree distribution alone does not capture every structural detail of the real knowledge graph, which D will examine later.

So far, we have measured whether nodes remain connected. C will now ask whether the damaged graph can still answer the same drug–disease queries.

Source: B's WS2 attack and hub-composition results; D's WS4 attack overlay. Random curves use ten seeds; targeted rankings are fixed.

## Sources and delivery notes

- Main graph: `primekg_5000_bfs_v1`.
- Structural results: `results/primekg_5000_bfs_v1/ws2_attack_results_long.csv`.
- Hub composition: `results/primekg_5000_bfs_v1/ws2_hub_composition.csv`.
- Theory overlay: `figures/act1/primekg_5000_bfs_v1/fig_attack_theory.png` and `results/ws4/primekg_5000_bfs_v1__attack_overlay.csv`.
- Random curves: ten-seed mean and sample SD. Attack rankings are fixed, so no random-seed uncertainty band is claimed for them.
- About 190 words; rehearse at your own speaking pace.
