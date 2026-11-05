# D · Slides 9–11

Target 3:00 in total, about 130 words per minute. Every number comes from `results/ws4/` for `primekg_5000_bfs_v1`.

## Slide 9 · One formula predicts two-hop retrieval

**Script:** Why do the curves on the last slides look the way they do? A two-hop query with m shared proteins has m routes. Each route needs two edges, so it survives with probability p squared. Routes through different proteins share no edge, so they fail independently. The query fails only if all m routes fail. Averaging over the query set gives one line: R equals one minus G of one minus p squared, where G is the generating function of path counts. There are no fitted parameters. The dashed lines match both query groups, and over five thousand fresh damage orders the difference is below 0.001. A logistic regression with degree features does no better at predicting which query fails.

**中文要点：** 把一个查询想成 m 根并联的“保险丝”，每根由两条边串联。串联存活 p²，并联全断 (1 − p²)^m，对查询集取平均就是 PGF。这和课上求 giant component 是同一个工具，但这里没有自洽方程，因为路径之间互不共享边。

## Slide 10 · Targeted attacks break independence

**Script:** That formula assumes damage ignores the graph. A targeted attack does not. This plot shows the gap between the random-removal formula and measured success under attack. Removing the top five percent of nodes by degree leaves 30 percent of queries working, while the formula predicts 88 percent. That is a penalty of 57 points. It has two channels. About 17 points come from lost endpoints, mostly hub diseases. About 40 come from lost paths, because query paths run through hubs: the median path protein has degree 188, against 25 for all proteins. So path count is not effective redundancy: 53 percent of multi-path queries fail. The giant component hides this: compared with random removal it falls 7 points, while retrieval falls 56.

**中文要点：** 公式假设破坏是“盲”的。攻击专挑 hub，而查询恰好挂在 hub 上，因为一个蛋白要同时连到药物和疾病，天然偏向高度节点。R 可以写成“端点存活 × 路径存活”，所以损失分成两路，17 和 40 是两种拆分顺序的平均。

## Slide 11 · Longer horizons move the bottleneck

**Script:** Finally, the hop limit. We have two analytic limits. At L equals two, retrieval is local, and our formula applies. At L equals infinity, a query only needs both endpoints to reach the protein–protein giant component. Generating functions give that probability with no fit, and it matches the mean over 600 fresh damage orders to within 0.01. In between, each extra hop delays the damage at which the limit matters: about ten, fifty and eighty-five percent edge loss for two, three and four hops. We expected a sharp percolation collapse at L infinity, and we did not see one. The protein giant component still holds 75 percent of proteins at 90 percent edge loss. Up to that point, over 90 percent of L-infinity failures are drugs that have lost every target. So on this benchmark, longer horizons move the bottleneck from shared proteins to the drug's own target links.

**中文要点：** 原先预期 L = ∞ 会在渗流阈值附近塌缩，数据不支持。PPI 骨架极其耐打，先断的主要是药物到靶点的那几条边，因为查询里的药物靶点很少。所以结论应说这个查询集上瓶颈转移，不要说出现了相变；0.006 只是 Molloy–Reed 估计，我们没有测到阈值本身。

## Theory Q&A

**Why are the routes independent?**  
Two routes through different proteins use four different edges, and every node pair carries one relation (pairs_with_multiple_relations = 0). Removing a fixed number of edges adds only an O(1/E) correction.

**Why does the simulation sit a little above the dashed line at 30–50% damage?**  
Sampling. The seed SD is about 0.05 and the ten seeds are nested across damage levels, so one offset persists along a curve. The mean over 5,000 fresh orders is within 0.001 of the formula.

**Why is the per-query AUC only 0.72?**  
That is close to the ceiling. If the formula is true, failure is still random given m, and the expected AUC is 0.72 at 30% and 0.71 at 50% damage. Formula and regression both reach it.

**Why is there no phase transition at L = 2?**  
Each query depends on a fixed handful of edges, so R(p) stays the same smooth function as the graph grows. A giant component depends on an unbounded number of edges, which is why it can become singular as N → ∞.

**Why no sharp collapse at L = ∞?**  
The PPI network is hub-heavy. The Molloy–Reed estimate is p_c = ⟨k⟩/(⟨k²⟩ − ⟨k⟩) ≈ 0.006, or 0.0054 on the filtered full graph. Our scan stops at p = 0.01, so we did not measure the threshold itself. Drug links fail long before that: at p = 0.01 only 8% of queries keep a terminal link at both ends, whatever the PPI network does.

**Is the drug bottleneck a sampling artefact?**  
It is specific to this benchmark, so we do not generalise it. The BFS graph keeps 78% of its drugs' target links, yet the median query drug has 2 targets in both the BFS graph and the full graph. Also, 31.5% of queries use a drug with at most three targets.

**GF assumes a configuration model. Why use it on a real graph?**  
Because the difference is informative. On stub-matched graphs with the same degrees, our code agrees with simulation to about 0.001. On the real PPI network the gap stays within 0.009 up to f = 0.97 and reaches 0.020 at f = 0.99. For the degree attack, theory sits up to 0.11 above simulation below f ≈ 0.58, so the real graph is more fragile there; above that a small remnant survives where theory gives zero. Our null-model test of the cause is planned for the report.

**How unique is the 17 + 40 split?**  
R is a product of an endpoint factor and a path factor, so a sequential split depends on which factor changes first. We average both orders: Δ = (φ² − E)(C_th + C)/2 + (C_th − C)(φ² + E)/2. At 5% degree attack, endpoints give 11–24 points and paths 34–46, depending on order.

**Why do slides 8 and 11 differ slightly?**  
Slide 8 uses seeds 0–2, and the heatmap on slide 11 uses all ten. Damage-order noise is visible at this size: L = 3 at 50% loss is 84.5% with three seeds, 81.9% with ten, and 79.2% over 600 fresh orders.

**Does the logistic regression beat theory under attack?**  
Yes. At a 5% degree attack the AUC is 0.88 against 0.66 in cross-validation over queries, and 0.83 when folds are split by drug. Treat it as exploratory: the features include the degree that defines the attack.
