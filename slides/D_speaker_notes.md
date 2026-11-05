# D · Slides 9–11

Target 3:00 in total, about 130 words per minute. Every number comes from `results/ws4/` for `primekg_5000_bfs_v1`.

## Slide 9 · One formula predicts two-hop retrieval

**Script:** Why do the curves on the last slides look the way they do? A two-hop query with m shared proteins has m routes. Each route needs two edges, so it survives with probability p squared. Routes through different proteins share no edge, so they fail independently. The query fails only if all m routes fail. Averaging over the query set gives one line: R equals one minus G of one minus p squared, where G is the generating function of path counts. There are no fitted parameters. The dashed lines match both query groups, and over five thousand fresh damage orders the difference is below 0.001. A logistic regression with degree features does no better at predicting which query fails.

**中文要点：** 把一个查询想成 m 根并联的“保险丝”，每根由两条边串联。串联存活 p²，并联全断 (1 − p²)^m，对查询集取平均就是 PGF。这和课上求 giant component 是同一个工具，但这里没有自洽方程，因为路径之间互不共享边。

## Slide 10 · Targeted attacks break independence

**Script:** That formula assumes damage ignores the graph. A targeted attack does not. This plot shows the gap between the random-removal formula and measured success under attack. Removing the top five percent of nodes by degree leaves 30 percent of queries working, while the formula predicts 88 percent. That is a penalty of 57 points. It has two channels. About 24 points come from lost endpoints, mostly hub diseases. About 34 come from lost paths, because query paths run through hubs: their median degree is 188, against 25 for all proteins. So path count is not effective redundancy. Twenty-two percent of multi-path queries lose every path. The giant component hides this: compared with random removal it falls 7 points, while retrieval falls 56.

**中文要点：** 公式假设破坏是“盲”的。攻击专挑 hub，而查询恰好挂在 hub 上，因为一个蛋白要同时连到药物和疾病，天然偏向高度节点。损失拆成两路：端点本身被删（多为 hub 疾病），以及端点还在但路径没了。

## Slide 11 · Longer horizons move the bottleneck

**Script:** Finally, the hop limit. We have two analytic limits. At L equals two, retrieval is local, and our formula applies. At L equals infinity, a query only needs both endpoints to reach the protein–protein giant component. Generating functions give that probability with no fit, and it stays within about six points of simulation. In between, each extra hop delays the damage at which the limit matters: about ten, fifty and eighty percent edge loss for two, three and four hops. We expected a sharp percolation collapse at L infinity, and we did not see one. The protein giant component is too robust: its threshold is near p equals 0.006. At every damage level, over 92 percent of L-infinity failures have lost a terminal link. So longer horizons move the bottleneck from shared proteins to the last link.

**中文要点：** 原先预期 L = ∞ 会在渗流阈值附近塌缩，数据不支持。PPI 骨架极其耐打（p_c ≈ 0.006），先断的是药物、疾病接入骨架的末端边。所以结论应说瓶颈转移，不要说出现了相变。

## Theory Q&A

**Why are the routes independent?**  
Two routes through different proteins use four different edges, and every node pair carries one relation (pairs_with_multiple_relations = 0). Removing a fixed number of edges adds only an O(1/E) correction.

**Why does the simulation sit a little above the dashed line at 30–50% damage?**  
Sampling. The seed SD is about 0.05 and the ten seeds are nested across damage levels, so one offset persists along a curve. The mean over 5,000 fresh orders is within 0.001 of the formula.

**Why is the per-query AUC only 0.72?**  
That is close to the ceiling. If the formula is true, failure is still random given m, and the expected AUC is 0.72 at 30% and 0.71 at 50% damage. Formula and regression both reach it.

**Why is there no phase transition at L = 2?**  
R is a polynomial in p on a finite query set, so it has no singularity. It depends on a few local edges, not on a collective variable.

**Why no sharp collapse at L = ∞?**  
The PPI network is hub-heavy, so p_c = ⟨k⟩/(⟨k²⟩ − ⟨k⟩) ≈ 0.006, or 0.0054 on the filtered full graph. Long before that, endpoints lose all their terminal edges: 31.5% of queries have a drug with at most three targets. PPI disconnection is the failure mode in under 8% of failures.

**GF assumes a configuration model. Why use it on a real graph?**  
Because the difference is informative. On stub-matched graphs with the same degrees, our code agrees with simulation to about 0.001. On the real PPI network it also tracks closely (largest gap 0.020). For the degree attack, theory sits above simulation by up to 0.11, so the real graph is more fragile. Our null-model test of the cause is planned for the report.

**Is the 24 + 34 split unique?**  
No. It is an exact identity with endpoints counted first: Δ = (φ² − E)·C_th + E·(C_th − C). Counting paths first would change the split but not the total.

**Why do slides 8 and 11 differ slightly?**  
Slide 8 uses seeds 0–2. Slide 11 uses all ten. Two-hop success at 50% is 40.3% on slide 8 and 43.3% on slides 6 and 11.

**Does the logistic regression beat theory under attack?**  
Yes, AUC 0.88 against 0.66 at 5% degree attack, in cross-validation over queries. Treat it as exploratory: the features include the degree that defines the attack.
