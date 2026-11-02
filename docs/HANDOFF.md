# A handoff to B–E

Before starting, run `python -m src.validate_data primekg_5000_bfs_v1`. The initial plan's shared files and function names are retained. Additional feature files and count arrays are documented in DATA_CONTRACT.md. This is a prepared handoff; no messages were sent to group members.

## B — centrality and node attacks

```python
from src.common import load_nodes, load_edges, structural_graph
from src.percolation import nz_nodes, to_levels
from src.common import NODE_LEVELS
gid = 'primekg_5000_bfs_v1'
nodes, edges = load_nodes(gid), load_edges(gid)
g = structural_graph(gid)  # includes isolates; nid insertion order fixed
order = sorted(g, key=lambda nid: (-g.degree(nid), nid))
out = nz_nodes(len(nodes), edges[['u', 'v']].to_numpy(), order)
table = to_levels(out, NODE_LEVELS, len(nodes), gid, 'node_degree', -1)
```

Compute centralities on the original graph once. Normalize returned edge keys before joining to eid. Supply node_degree.npy, node_betweenness.npy and edge_betweenness.npy under this gid's orders; add separate provenance. Do not overwrite random orders or the manifest. k=100 must fit graph size; record NetworkX version. Zero models must preserve type-specific degree and state whether queries are retained or regenerated.

## C — retrieval and L scan

Use `load_queries`, `edge_alive_mask` and `node_alive_mask`. `effective_edge_mask` combines endpoint and relation survival. `results/validation/{gid}__retrieval_reference.csv` contains independent reference rows at f=0,.3,.5,.9,1 for seed 0 and both random strategies. It is a validation fixture, not a replacement WS3 deliverable. Compare query_id, endpoint survival, s_alive and d_ppi against your Retriever. Compare finite distances explicitly. Use node_features only as original graph features, never as damaged degrees.

## D — theoretical inputs and predictions

The manifest contains exact node/edge/query counts, raw source hash and pairs_with_multiple_relations. `node_features.csv` contains all-node structural degree and type-labeled PPI degree; select gene/protein rows for the PPI distribution, including zero degrees. Queries contain m and intermediate protein IDs. D's train seeds 0–6/test seeds 7–9 do not reuse E's query split. The finite-size single-path bond baseline is M(M-1)/(E(E-1)); keep E and integer removals available.

A uses an isolated GF reference until D supplies theory.py. An analytic 3-regular identity test checks its nontrivial root. A's WS1 accepts --theory-module src.theory so D's implementation can be substituted without changing data or experiments. Cross-member validation is pending until D's actual module is available.

## E — restoration and slide integration

Use seed 0–9 damaged masks at f=.3/.5; copy masks for each strategy and budget. Select edges from training queries only and report test-query R. The independent reference CSV supports zero-budget checks; restoring all removed edges must recover original structure/paths. Query overlap at entity level is permitted by the agreed split and should not be described as entity-disjoint generalization.

A's figures are PNG+PDF in figures/act1/{gid}; principal gid is 5000. Theory is explicitly marked configuration-model reference. Use slides/A_speaker_notes.md and slides/A_slides_3_4.pptx for pages 3–4. E owns the final template and full deck. The WS1 plotter loads your plotting.setup() once provided.

## Items requiring team acknowledgement

1. Metric denominators and empty-graph definitions in DATA_CONTRACT.md (now implemented explicitly).
2. A's extra count metrics and feature file are additive; consumers should select metrics by name.
3. D's reference-vs-final theory status; fixed-cardinality versus independent-removal approximation.
4. E's relation-type candidate shortages and whether task-aware ranks are recomputed.
5. No result direction is enforced by data selection. Unexpected attack/theory trends remain valid findings after checks.

An explicit raw-data or query-validity failure blocks formal publication. Sampling concentration and model mismatch are reported limitations, not grounds for silently changing the standard graph.
