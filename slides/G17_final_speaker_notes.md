# G17 final presentation: speaker notes

Pages 1–15 are the main presentation. Pages 16–18 are optional Q&A backups.

## Slide 1: When AI Forgets

Today we ask how losing relations changes both the connectivity of a knowledge graph and its ability to answer queries. We compare random failures, targeted attacks, retrieval theory and restoration on one shared PrimeKG benchmark.

## Slide 2: Connectivity and retrieval

The upper route answers a two-hop drug–protein–disease query. Delete one edge
and that query fails, even though a longer route still connects the endpoints.
Restoring the upper edge repairs the two-hop query. If we allow an extra hop,
the lower route can also become useful. This small example shows why a
connectivity measure and a retrieval metric can respond differently to damage.
Concept schematic, not an observed PrimeKG case.

## Slide 3: PrimeKG and the shared protocol

We use PrimeKG as a real example of a network whose structure and function can respond differently to damage. We retain drugs, diseases and proteins, together with three relation types. Our standard experiment uses a deterministic breadth-first sample of five thousand nodes and all eligible relations between those nodes.

The graph has about one hundred and eighteen thousand relations, but its composition is uneven: most nodes are proteins, while only seventy-four are drugs. The degree distributions also differ across entity types. We describe these distributions without assuming that they follow a power law.

For the later retrieval experiments, every query asks whether a drug and disease share a protein through the required relation types. We fix one hundred queries with a single path and one hundred with multiple paths. Everyone uses the same graph, queries and removal orders. This lets us compare structural and functional outcomes under exactly the same damage. Because BFS sampling changes the network, we also check the filtered full graph.

Source: slides/A_speaker_notes.md; data/processed/primekg_5000_bfs_v1.

## Slide 4: Random network failure

The structural question is: how much of the original network remains in one connected piece? We measure S as the largest surviving component divided by the original number of nodes.

Bond percolation removes relations while keeping the nodes. Site percolation removes nodes and all their incident relations. The denominator remains the original node count in both cases. The solid curves are the averages of ten random removal orders; the bounds show one standard deviation.

At fifty percent edge removal, about ninety-eight percent of the original nodes still belong to the largest component. At fifty percent node removal, the value is about forty-nine percent. That is close to all surviving nodes, so the lower curve partly reflects the nodes removed directly. Equal removal fractions do not imply equal numbers of lost relations.

The black dashed curves are generating-function predictions from the original degree distribution under a configuration-model approximation. They follow the main trends closely, although the extreme edge-removal region shows a larger discrepancy. Agreement here is an observation, not proof that the real network satisfies all model assumptions.

There is also a sampling limitation. In the filtered full graph, fifty percent edge removal leaves about eighty-six percent in the largest component, rather than ninety-eight percent. We therefore keep our claims specific to the graph being studied. The next question is what happens when the lost nodes are selected deliberately instead of randomly.

Source: slides/A_speaker_notes.md; results/ws1. The GF reference agrees with D's solver.

## Slide 5: Targeted failure and central nodes

Random failure treats every node equally. We now ask what happens when we deliberately remove the most central nodes first. We compute degree and betweenness on the intact graph, then keep those rankings fixed throughout the experiment.

Both attacks fragment the graph much faster than random removal. After removing half the nodes, the largest component contains about 49 percent of the original nodes under random failure, compared with 23 percent under degree attack and 21 percent under betweenness attack. These are fractions of the original graph, so directly deleted nodes also count as lost.

The composition chart shows that almost all of the top one percent are proteins or diseases. Removing those nodes also removes all their incident relations. The black dashed curve is the degree-based theoretical reference. Its difference from the real attack curve suggests that the degree distribution alone does not explain every detail; D will examine this later.

So far, we have measured whether nodes remain connected. C will now ask whether the damaged graph can still answer the same drug–disease queries.

Source: B's ws2 attack and hub-composition tables; D's ws4 attack overlay. Random curves use ten seeds; targeted rankings are fixed.

## Slide 6: Structural and functional robustness

**Figure:** `fig_S_vs_R`

- S measures how many original nodes remain in the largest component.
- R measures how many of the 200 original queries still have an allowed path.
- At 50% edge loss, the two metrics differ by 54.9 percentage points.

**Script:** We used the same deletion order for the structural and functional measurements. After random removal of half the edges, the largest connected component still contains 98.2 percent of the original nodes, averaged over ten seeds. Only 43.3 percent of the selected queries still have a two-hop path. Protein–protein edges can sustain the connected component, while a two-hop query needs one protein connected to both endpoints.

**Likely question:** Why are the curves so far apart?
**Answer:** The largest component can be held together by protein–protein links. A two-hop query specifically needs two surviving terminal links incident to the same protein.
Source: results/ws1 and results/ws3 matching edge damage states.

## Slide 7: Path redundancy and retrieval

**Figure:** `fig_R_by_group`

- Each group contains 100 queries.
- The groups use the intact graph's path counts.
- At 50% edge loss the success rates are 60.7% and 25.9%.

**Script:** We grouped queries by the number of shared proteins in the intact graph. Each group contains 100 queries. When half the edges are removed, 60.7 percent of queries with multiple paths still work, compared with 25.9 percent of single-path queries. A query can survive the loss of one shared protein route if both edges of another route remain.

**Likely question:** Is redundancy measured again after each deletion?
**Answer:** We keep the original group labels fixed. Each damaged state tells us how many of the original routes remain.
Source: results/ws3/primekg_5000_bfs_v1__retrieval.csv.

## Slide 8: The retrieval horizon

**Figures:** `fig_R_L_curves` and `fig_R_L_heatmap`

- Every hop limit uses the same three damage seeds.
- One extra hop allows one protein–protein link.
- At 90% edge loss, four-hop and unlimited success are 28.7% and 37.0%.

**Script:** For this comparison, we use the same three damage seeds for every hop limit. At 50 percent edge removal, allowing one protein–protein step increases mean success from 40.3 to 84.5 percent. Four hops reach 89.5 percent. At more severe damage, the four-hop and unlimited curves separate. The heatmap shows how retrieval changes with both the deletion fraction and the allowed path length.

**Likely question:** Why is two-hop success 40.3% here and 43.3% on slide 6?
**Answer:** The hop scan uses seeds 0–2 for every curve, while slide 6 uses all ten seeds. Both use the same frozen query set.
All displayed horizons use damage seeds 0–2.

## Slide 9: One formula predicts two-hop retrieval

Why do the curves on the last slides look the way they do? A two-hop query with m shared proteins has m routes. Each route needs two edges, so it survives with probability p squared. Routes through different proteins share no edge, so they fail independently. The query fails only if all m routes fail. Averaging over the query set gives one line: R equals one minus G of one minus p squared, where G is the generating function of path counts. There are no fitted parameters. The dashed lines match both query groups, and over five thousand fresh damage orders the difference is below 0.001. A logistic regression with degree features does no better at predicting which query fails.

Source: results/ws4/primekg_5000_bfs_v1__theory.csv, __monte_carlo_check.csv, __prediction.csv.

## Slide 10: Targeted attacks break independence

That formula assumes damage ignores the graph. A targeted attack does not. This plot shows the gap between the random-removal formula and measured success under attack. Removing the top five percent of nodes by degree leaves 30 percent of queries working, while the formula predicts 88 percent. That is a penalty of 57 points. It has two channels. About 17 points come from lost endpoints, mostly hub diseases. About 40 come from lost paths, because query paths run through hubs: the median path protein has degree 188, against 25 for all proteins. So path count is not effective redundancy: 53 percent of multi-path queries fail. The giant component hides this: compared with random removal it falls 7 points, while retrieval falls 56.

Source: results/ws4/primekg_5000_bfs_v1__corr_penalty.csv, __provenance.json, __equal_damage_summary.csv. The split averages both orders of the two factors. 188 is per query path; the median over the 133 unique proteins is 106.

## Slide 11: Longer horizons move the bottleneck

Finally, the hop limit. We have two analytic limits. At L equals two, retrieval is local, and our formula applies. At L equals infinity, a query only needs both endpoints to reach the protein–protein giant component. Generating functions give that probability with no fit, and it matches the mean over 600 fresh damage orders to within 0.01. In between, each extra hop delays the damage at which the limit matters: about ten, fifty and eighty-five percent edge loss for two, three and four hops. We expected a sharp percolation collapse at L infinity, and we did not see one. The protein giant component still holds 75 percent of proteins at 90 percent edge loss. Up to that point, over 90 percent of L-infinity failures are drugs that have lost every target. So on this benchmark, longer horizons move the bottleneck from shared proteins to the drug's own target links.

Source: results/ws4/primekg_5000_bfs_v1__hop_scan_10seeds.csv, __theory.csv, __hop_boundary.csv, __hop_fresh_orders.csv. The heatmap uses all ten seeds; slide 8 uses seeds 0–2. The 5 pp marker is a display choice, not a phase boundary. p_c is an estimate: the scan stops at p = 0.01.

## Slide 12: Restoration for two-hop queries

All policies start from matching damaged masks. At fifty-percent damage and a
twenty-percent restoration budget, relation-type selection gains 48.5 percentage
points, edge betweenness 42.0, static task-aware 24.8 and random selection 13.2.
Task-aware selection starts well at the smaller budget, but its positive-score
set contains only a few dozen edges. After selecting those edges, the static
rule spends most additional budget on randomly ordered zero-score candidates.
Source: results/ws5/final/primekg_5000_bfs_v1 and report/E_static_score_diagnostics.csv. Formal C Retriever; B edge ranking included.

## Slide 13: Restoration for three-hop queries

The same restored graphs give a different comparison when a query can use one
protein–protein interaction. At fifty-percent damage and twenty-percent budget,
the mean gains are 16.5 points for edge betweenness and 15.7 for relation-type
selection, followed by 12.3 for static task-aware and 8.3 for random restoration.
The first two means are close relative to their seed variation. These curves
describe the horizon and budget dependence without establishing significance.
Source: results/ws5/final/primekg_5000_bfs_v1. The displayed gains are paired within seed and shaded by sample SD. No significance claim.

## Slide 14: Robustness depends on the task

The policy with the largest structural gain can differ from the policy with
the largest two-hop retrieval gain. We therefore need to specify the task and
the damage budget when discussing robustness. Our measurements concern a BFS
subgraph and selected positive queries. The query split may share entities.
E report Sections 1 and 7. The full fourteen-minute rehearsal has not been measured.

## Slide 15: Thank you

Thank you for listening. We welcome your questions.

## Slide 16: Backup: predicting which query fails

Under random damage the formula sits at the AUC ceiling of about 0.72, so degree features add nothing. Under attack, degree features help a great deal, but they include the quantity that defines the attack, so this is exploratory. Source: results/ws4/primekg_5000_bfs_v1__prediction_detail.csv.

## Slide 17: Backup: how the theory was checked

The configuration-model check tests the code; the other rows test the assumptions. The attack check excludes f = 0.6, where the theory is at its threshold and the finite graph gives 0.025. The PPI gap reaches 0.020 at f = 0.99. Source: results/ws4/primekg_5000_bfs_v1__configuration_model_check.csv and __monte_carlo_check.csv.

## Slide 18: Backup: equal damage, different outcomes

At the same five-percent node loss, both targeted attacks reduce the largest component and retrieval more than random removal. The effect is much larger for retrieval: degree attack adds about seven percentage points of structural loss, but about fifty-six points of retrieval loss. Beyond ten-percent damage, the two attacks differ by at most two of the two hundred queries, so we do not rank them.

Source: results/ws4/primekg_5000_bfs_v1__equal_damage.csv and __equal_damage_summary.csv.
