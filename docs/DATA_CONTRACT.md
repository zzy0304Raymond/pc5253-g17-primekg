# Shared data and metric contract

## IDs and relations

`nodes.csv`: nid, x_index, node_type, node_name. nid is contiguous, sorted by integer original x_index. It is LOCAL TO gid. Join graphs by x_index, never by nid. Types: drug, disease, gene/protein.

`edges.csv`: eid,u,v,relation. u<v; sorted by relation,u,v; eid contiguous. One row is one normalized undirected semantic association. Opposite storage directions and duplicates are collapsed; no self-loops. Labels: drug_protein, disease_protein, protein_protein. Structural edges are unique endpoint pairs; a pair survives while any of its semantic edges survives.

`queries.json`: exact keys in the work plan, including original/local IDs, sorted intermediates, redundancy_m, group, split. Separate seed-42 sampling of sorted single and multi groups, up to 100 each. query_id starts at 0; single first, then multi. No padding. E's train/test split is over query IDs; D's seed 0–6/7–9 split is a separate experiment.

`orders/edge_random_s0..9.npy`, `node_random_s0..9.npy`: complete int64 permutations. Delete the first round(f*total) elements, using Python rounding (ties to even). Keep all nodes in edge removal; remove nodes and incident relations in node removal. Never regenerate independent states at each f.

`node_features.csv` is an additive convenience file: original and local IDs, node_type, simple structural degree, PPI degree, and per-relation degree. PPI zero-degree proteins remain included; ppi_degree=0 on drug/disease is not evidence that they belong in the PPI network.

## Function interface

The seven common.py functions and nz_edges/nz_nodes/to_levels signatures match the plan. Loaders return fresh data. Order loads use allow_pickle=False and check complete permutations. Mutating a returned mask does not change the dataset or subsequent calls.

Newman–Ziff output arrays have length E+1 or N+1, indexed by NUMBER REMOVED. Required keys: gcc_size, n_components, n_isolated. Additive keys: n_alive, n_semantic_edges, n_structural_edges; n_original is a scalar. All counts concern surviving nodes only. The reverse-addition implementation handles repeated endpoint pairs without prematurely dropping structural connectivity.

## Metrics: implemented completion of underspecified details

These definitions are documented for team review; they do not change the plan's required function names or result columns.

- gcc_frac = GCC size / original N; includes removed nodes in denominator.
- isolated_frac = surviving isolated nodes / original N.
- n_components = connected components of surviving nodes.
- avg_degree = 2 * surviving simple structural edges / surviving nodes, defined as 0 for an empty surviving graph.
- n_alive, n_semantic_edges, n_structural_edges are additional long-table metric rows. Consumers should filter the metric they need, not assume a fixed row count.
- Empty surviving graph: GCC, components, isolates, mean degree all 0. Nonempty edgeless graph: GCC=1, components=isolates=N_alive.
- Simulation uncertainty is sample SD across seeds 0–9 (ddof=1), not uncertainty across dependent queries.
- Theory uses actual keep=1-n_removed/total. Independent Bernoulli formula and fixed-cardinality deletion are distinct finite-graph ensembles.

## Version safety

manifest.json freezes A's CSV/JSON/random-order SHA-256 values and source fingerprint. It excludes itself and later B-produced orders. B should provide a separate centrality provenance file referencing the parent manifest digest, software, k, seed and order-file hashes. Core data changes require new version and rerunning all dependent calculations.

Raw source provenance is retained in build_metadata.json. A partial download never becomes kg.csv without official checksum verification. Data generation refuses to alter frozen graphs.

## Retrieval and restoration details

Node removal invalidates drug/disease endpoints. Intermediate paths must use relation labels, not arbitrary graph paths. PPI includes every surviving protein, even if isolated. L=∞ success requires finite distance; never evaluate inf<=inf as success. At zero damage s_alive must equal redundancy_m for the selected benchmark.

All restoration strategies start from copies of the SAME damaged edge mask. Only original removed eids can be restored. Budget denominator is actual removed edges, not total original edges. E must specify candidate-shortage handling for relation_type and fixed-vs-recomputed task-aware scores. These decisions belong to E and are not silently imposed by A.

Full graph queries are an intentionally empty list with explicit structural-only scope; it must not be passed to functional experiments and reported as R=0. New zero-model graphs need a declared query policy: fixed original tasks or resampled tasks, with different scientific interpretations.
