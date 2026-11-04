# WS2 — Centrality and Targeted-Attack Analysis

## 1. Purpose

WS2 studies the structural vulnerability of the PrimeKG-derived knowledge graph.

The main questions are:

1. Which nodes are structurally important according to degree and betweenness centrality?
2. Is the graph more vulnerable to targeted removal of central nodes than to random node failure?
3. How much do degree-based and betweenness-based critical-node sets overlap?
4. What entity types (gene/protein, disease, drug) are represented among the most central nodes?
5. Which edges have high betweenness and may be useful for downstream restoration experiments?

The primary analysis graph is:

`primekg_5000_bfs_v1`

The smaller graph:

`primekg_2000_bfs_v1`

is retained as a development / validation graph for faster testing and comparison.

---

## 2. Main Scripts

### `src/centrality.py`

Computes:

- node degree ranking
- approximate node betweenness ranking
- approximate edge betweenness ranking

Ranking tie-breaking is deterministic:

- node rankings: decreasing centrality, then increasing `nid`
- edge ranking: decreasing centrality, then increasing `eid`

Approximate betweenness uses:

- `k = 100`
- `seed = 42`

Run on the primary graph:

    python -m src.centrality --gid primekg_5000_bfs_v1

Run on the development graph:

    python -m src.centrality --gid primekg_2000_bfs_v1

The default graph is `primekg_5000_bfs_v1`, so the following is also valid:

    python -m src.centrality

### `src/run_ws2.py`

Runs node-removal robustness experiments using the shared percolation implementation.

Strategies:

- random node failure
- degree-targeted attack
- betweenness-targeted attack

The random baseline averages the 10 pre-generated random orders:

`node_random_s0.npy` through `node_random_s9.npy`.

Run on the primary graph:

    python -m src.run_ws2 --gid primekg_5000_bfs_v1

The main robustness metric is:

`gcc_frac = GCC size / original number of nodes`

where GCC is the giant connected component.

### `src/analyze_ws2.py`

Computes:

- overall entity-type composition
- entity-type composition among the top 1%, 5%, and 10% degree nodes
- entity-type composition among the top 1%, 5%, and 10% betweenness nodes
- Jaccard overlap between degree and betweenness top-node sets

Run with:

    python -m src.analyze_ws2 --gid primekg_5000_bfs_v1

### `src/plot_ws2.py`

Generates the final WS2 figures.

Run with:

    python -m src.plot_ws2 --gid primekg_5000_bfs_v1

Figures include:

- random vs degree vs betweenness node-removal robustness
- degree-hub entity composition
- betweenness-hub entity composition

Figure filenames include the graph ID to avoid accidental overwriting between graph variants.

---

## 3. Reproduction Workflow

For the 5000-node primary graph:

    python -m src.centrality --gid primekg_5000_bfs_v1
    python -m src.run_ws2 --gid primekg_5000_bfs_v1
    python -m src.analyze_ws2 --gid primekg_5000_bfs_v1
    python -m src.plot_ws2 --gid primekg_5000_bfs_v1

For the 2000-node development / validation graph:

    python -m src.centrality --gid primekg_2000_bfs_v1
    python -m src.run_ws2 --gid primekg_2000_bfs_v1
    python -m src.analyze_ws2 --gid primekg_2000_bfs_v1
    python -m src.plot_ws2 --gid primekg_2000_bfs_v1

All four scripts default to `primekg_5000_bfs_v1` when `--gid` is omitted.

---

## 4. Centrality-Order Outputs

For each processed graph, centrality orders are stored under:

`data/processed/<gid>/orders/`

WS2 produces:

- `node_degree.npy`
- `node_betweenness.npy`
- `edge_betweenness.npy`

Each node order is a complete permutation of stable `nid` values.

The edge order is a complete permutation of stable `eid` values.

### Handoff to Restoration Experiments

The main WS2 → restoration handoff is:

`data/processed/primekg_5000_bfs_v1/orders/edge_betweenness.npy`

This provides the edge-betweenness ranking for downstream restoration strategies.

A corresponding development version is also available under:

`data/processed/primekg_2000_bfs_v1/orders/edge_betweenness.npy`

---

## 5. Primary Graph

For `primekg_5000_bfs_v1`:

- Nodes: 5,000
- Structural edges: 117,891

Overall entity composition:

| Entity type | Count | Fraction |
| --- | ---: | ---: |
| gene/protein | 4,643 | 92.86% |
| disease | 283 | 5.66% |
| drug | 74 | 1.48% |

Important high-centrality nodes include UBC, MYC, E2F1, FOS, and several disease nodes.

UBC ranks first by both degree and approximate node betweenness in the 5000-node graph.

Selected degree-ranking results include:

| Rank | Node | Type | Degree |
| ---: | --- | --- | ---: |
| 1 | UBC | gene/protein | 2,196 |
| 2 | MYC | gene/protein | 1,236 |
| 3 | hereditary breast ovarian cancer syndrome | disease | 1,156 |
| 4 | hereditary breast carcinoma | disease | 1,082 |

Selected approximate betweenness-ranking results include:

| Rank | Node | Type | Betweenness |
| ---: | --- | --- | ---: |
| 1 | UBC | gene/protein | 0.154636 |
| 2 | MYC | gene/protein | 0.088296 |
| 3 | E2F1 | gene/protein | 0.042709 |
| 4 | hereditary breast ovarian cancer syndrome | disease | 0.040530 |
| 5 | FOS | gene/protein | 0.032666 |

These results illustrate that high-degree hubs and high-betweenness bottlenecks overlap substantially but are not identical.

---

## 6. Targeted-Attack Results

The main result is that targeted removal of structurally central nodes fragments the graph substantially faster than random node failure.

Selected GCC fractions for the 5000-node primary graph are:

| Fraction removed | Random | Degree | Betweenness |
| ---: | ---: | ---: | ---: |
| 0.00 | 1.0000 | 1.0000 | 1.0000 |
| 0.01 | 0.9899 | 0.9590 | 0.9500 |
| 0.05 | 0.9494 | 0.8830 | 0.8856 |
| 0.10 | 0.8986 | 0.8162 | 0.8148 |
| 0.20 | 0.7973 | 0.6898 | 0.6858 |
| 0.50 | 0.4925 | 0.2320 | 0.2058 |

Here,

`S(f) = GCC size after removal / original number of nodes`.

For example, after removing 20% of nodes:

- random failure retains a GCC containing about 79.73% of the original nodes;
- degree-targeted attack retains about 68.98%;
- betweenness-targeted attack retains about 68.58%.

After removing 50% of nodes:

- random failure: `S(f) = 0.4925`
- degree attack: `S(f) = 0.2320`
- betweenness attack: `S(f) = 0.2058`

Therefore, the sampled PrimeKG graph is considerably more vulnerable to targeted attacks on structurally central nodes than to random node failures.

Degree and betweenness attacks show similar robustness trajectories on the 5000-node graph. Neither centrality strategy uniformly dominates the other at every removal fraction.

---

## 7. Degree vs Betweenness Overlap

Top-ranked degree and betweenness nodes overlap substantially:

| Centrality cutoff | Top N | Intersection | Jaccard |
| ---: | ---: | ---: | ---: |
| 1% | 50 | 41 | 0.6949 |
| 5% | 250 | 198 | 0.6556 |
| 10% | 500 | 387 | 0.6313 |

The Jaccard similarity is:

`J(A,B) = |A ∩ B| / |A ∪ B|`

For the top 1%, 41 of the 50 highest-ranked degree nodes also appear among the 50 highest-ranked betweenness nodes.

This substantial overlap helps explain why degree-targeted and betweenness-targeted attack curves are similar.

---

## 8. Hub Entity Composition

The overall 5000-node graph is dominated by gene/protein nodes:

- gene/protein: 92.86%
- disease: 5.66%
- drug: 1.48%

However, disease nodes are disproportionately represented among highly central nodes.

For the top 1% degree nodes:

- gene/protein: 84%
- disease: 16%
- drug: 0%

For the top 1% betweenness nodes:

- gene/protein: 86%
- disease: 14%
- drug: 0%

Relative to the overall disease fraction of 5.66%, this corresponds to approximately:

- `16 / 5.66 ≈ 2.83x` enrichment among top-1% degree nodes;
- `14 / 5.66 ≈ 2.47x` enrichment among top-1% betweenness nodes.

Drug nodes are rare among the most central nodes.

These observations should be interpreted for the sampled PrimeKG subgraph rather than assumed to hold universally for the full PrimeKG.

---

## 9. Result Files

Primary 5000-node outputs are stored in:

`results/primekg_5000_bfs_v1/`

including:

- `ws2_attack_results_long.csv`
- `ws2_gcc_comparison.csv`
- `ws2_overall_composition.csv`
- `ws2_hub_composition.csv`
- `ws2_degree_betweenness_overlap.csv`

The long-format attack result file retains the shared percolation metrics across strategies and removal levels.

Development / validation attack results are retained under:

`results/primekg_2000_bfs_v1/`

including:

- `ws2_attack_results_long.csv`
- `ws2_gcc_comparison.csv`

The 2000-node graph is intended mainly for faster development, validation, and comparison. Final project conclusions should primarily use the 5000-node results.

---

## 10. Figures

Primary presentation figures are stored under `figures/`:

- `ws2_attack_curves_primekg_5000_bfs_v1.png`
- `ws2_attack_curves_primekg_5000_bfs_v1.pdf`
- `ws2_degree_hub_composition_primekg_5000_bfs_v1.png`
- `ws2_betweenness_hub_composition_primekg_5000_bfs_v1.png`

The attack-curve figure is the main WS2 presentation figure.

It shows that the random-failure curve remains substantially above the two targeted-attack curves, while degree and betweenness attacks produce similar trajectories.

---

## 11. Tests

WS2-specific tests are located in:

`tests/test_ws2.py`

They cover:

- acceptance of valid attack-order permutations;
- rejection of duplicate IDs;
- deterministic degree-ranking logic;
- Jaccard calculation.

Run all repository tests with:

    python -m unittest discover -s tests -v

Current status:

`21 tests passed`

This includes the existing repository tests together with the newly added WS2 tests.

---

## 12. Main Interpretation

The WS2 analysis supports three main conclusions.

### 1. Targeted structural failures are substantially more damaging than random failures

Removing nodes with high degree or high betweenness causes the giant connected component to shrink substantially faster than random node removal.

This indicates that the PrimeKG-derived graph has heterogeneous structural importance: a relatively small subset of nodes contributes disproportionately to global connectivity.

### 2. Degree hubs and betweenness bottlenecks overlap substantially

Degree and betweenness centrality measure different structural properties:

- degree identifies nodes with many direct connections;
- betweenness identifies nodes lying on many shortest paths.

However, their top-ranked node sets overlap strongly in this graph.

This helps explain why the two targeted-attack strategies produce similar robustness trajectories.

### 3. Disease nodes are enriched among structurally central nodes

Disease nodes constitute only 5.66% of the sampled graph but account for 14–16% of the top 1% central nodes.

This suggests that disease entities occupy disproportionately important structural positions in the sampled PrimeKG graph.

Overall, these results motivate protecting structurally important nodes and edges when maintaining a knowledge graph used for downstream retrieval or AI tasks, and they provide centrality-based rankings that can be used by downstream restoration experiments.