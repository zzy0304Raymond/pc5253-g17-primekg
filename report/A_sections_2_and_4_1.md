# A — Report sections for integration

These sections report completed experiments. Section numbering follows G17_Work_Plan.md. Figure numbers should be assigned by the report editor. The reference GF implementation is supplied by A pending comparison with D's final theory module.

## 2. Data and experimental protocol

### 2.1 Source and graph representation

We use the fixed PrimeKG `kg.csv` distributed as Harvard Dataverse file 6180620, associated with DOI 10.7910/DVN/IXA7BM [1]. The downloaded file contains 8,100,498 stored rows and occupies 981,751,236 bytes. Its MD5 matches the repository metadata (`aac8191d4fbc5bf09cdf8c3c78b4e75f`); the SHA-256 is recorded in the reproducibility appendix. Thus the analysis is tied to a specific dataset file rather than an unspecified current version of the repository.

The experimental network retains drug, disease and gene/protein entities and the drug_protein, disease_protein and protein_protein relations. Entity identity is determined by the original numerical node index, not by its display name. We collect nodes from both endpoint columns, check endpoint types against the relation, normalize the endpoint pair of every undirected relation, and remove duplicate or reverse storage records and self-loops. The raw filter selects 854,278 rows; 427,324 duplicate or reverse records are collapsed, leaving 426,954 semantic relations. No selected self-loop rows or conflicting entity names were observed. The filtered network contains 30,968 nodes. These counts describe the filtered network, not the complete unfiltered PrimeKG.

Two representations serve distinct measurements. The semantic representation retains each normalized relation label and is used for constrained retrieval. The structural representation is a simple undirected projection used for degree, connected components and percolation. We explicitly check whether any endpoint pair has multiple semantic relation types; the count is zero in all supplied graphs. Consequently, the structural and semantic edge counts coincide in this dataset. The implementation nevertheless retains the correct projection semantics if later datasets contain parallel relations.

### 2.2 Deterministic induced subgraphs

The standard graph is obtained by breadth-first traversal of the filtered network, starting from the disease with the highest structural degree. Ties and neighbor visits are ordered by numerical original ID. The selected start node has original index 32617 and degree 1,156. We retain the first 5,000 visited nodes and every eligible relation between them, producing an induced subgraph rather than the BFS tree. The first 2,000 nodes of the same traversal provide a smaller validation graph. Within each graph, nodes are sorted by original ID before assigning contiguous local IDs; edges are sorted by relation and endpoint pair. Local IDs are therefore graph-specific even where original entities overlap.

| Graph | Nodes | Relations | Drugs | Diseases | Proteins |
|---|---:|---:|---:|---:|---:|
| BFS validation | 2,000 | 32,468 | 3 | 46 | 1,951 |
| BFS standard | 5,000 | 117,891 | 74 | 283 | 4,643 |
| Filtered full graph | 30,968 | 426,954 | 6,282 | 5,593 | 19,093 |

The 5,000-node graph contains 90,187 protein–protein, 27,228 disease–protein and 476 drug–protein relations. Its mean degree differs by node type: approximately 44.82 for proteins, 96.21 for diseases and 6.43 for drugs. These distributions are shown as empirical degree CCDFs sampled at logarithmically spaced thresholds. A long tail in such a plot is descriptive evidence and does not by itself establish a power-law distribution.

The BFS sample is dominated by proteins and nearby high-connectivity structure. We therefore retain the filtered full graph for a direct robustness comparison. A connected BFS sample is not evidence that the full filtered network is connected: the latter has 23 components, with 30,921 of 30,968 nodes in its largest component.

### 2.3 Fixed functional benchmark

Queries ask whether a drug and disease share at least one protein through the required drug_protein and disease_protein relations. The redundancy m is the number of distinct intermediate proteins. We enumerate valid pairs in the intact graph, separate m=1 from m≥2, sort pairs by original IDs, and sample up to 100 queries from each group using seed 42. The standard graph has 3,175 single-path and 1,264 multi-path candidates and supplies exactly 100 queries from each group. The selected queries involve 39 drugs and 127 diseases, with no disease appearing in more than four selected queries. The multi-path group's redundancy ranges from 2 to 17.

The small graph supplies only 46 single-path and 66 multi-path queries, all of which are retained. Its three drugs make it useful for correctness checks but limit its representativeness as a functional benchmark. No queries or relations are duplicated to fill the target size. The full graph is released for structural comparison only; its empty query file is explicitly marked as an undefined functional benchmark, not a zero-success experiment.

Queries retain both original and local endpoint IDs, the complete intermediate-protein list and the relation pattern. For restoration, a seed-42 permutation of query IDs determines a 70% training / 30% test split. The standard benchmark has 140 training and 60 test queries. This split is over queries and permits shared entities; it is distinct from WS4's training/testing split over failure seeds. The benchmark is conditioned on intact-graph success and deliberately balances redundancy groups. Its aggregate retrieval rate must not be interpreted as a prevalence estimate over all drug–disease pairs. A semantic association path also does not establish a therapeutic effect.

### 2.4 Damage states and measurement

For random edge and node failure, seeds 0–9 generate permutations of the original semantic edge or node IDs. At fraction f, the first round(f × total) entries are removed, making damage states nested within a seed. Node removal also removes all incident relations. All downstream workstreams can reconstruct exactly the same states from these files. Edge-removal fractions extend to 0.99 and node-removal fractions to 0.90 according to the shared plan.

Structural robustness is S(f)=|C_max(f)|/N0, where N0 is the original node count. The denominator stays fixed for node removal. Component and isolated-node counts include only surviving nodes; the isolated fraction uses N0, whereas average degree is twice the number of surviving structural edges divided by surviving nodes. The empty surviving graph is assigned zero for these metrics. Results include actual surviving node and relation counts so that losses caused by different strategies can be compared transparently. Random results are summarized by the mean and sample standard deviation across ten seeds.

## 4.1 Structural robustness under random failure

### Simulation and theoretical reference

We compute all removal states by reversing each fixed removal order and adding edges or nodes with a union-find structure, following the reverse-addition approach of Newman–Ziff [2]. Each returned array is indexed by the number removed. For semantic duplicates on one endpoint pair, connectivity changes only when the first surviving relation is added. This implementation yields largest-component size, component count and isolated-node count, together with surviving structural and semantic edge counts.

We compare the curves with a generating-function prediction based on the original empirical structural degree distribution. With g0(z)=Σk p_k z^k and g1(z)=g0′(z)/g0′(1), the reference solves u=1−q+qg1(u), using the nontrivial solution where it exists. Bond robustness is 1−g0(u), while site robustness is q[1−g0(u)]. Here q is the actual retained fraction after integer rounding. These equations describe a configuration-model approximation; they are not an exact identity for a finite, typed biological network. The fixed-count deletion simulation also differs from independent Bernoulli retention at finite size.

### Standard-graph results

The 5,000-node graph is initially connected. Under random edge removal, most nodes remain in its largest component even after substantial relation loss. At f=0.50, mean S is 0.98218 with sample SD 0.00128. At f=0.90, it is 0.81540 ± 0.00366, and at f=0.99 it falls to 0.11222 ± 0.01592. Thus the largest component remains large over much of the sampled damage range but loses most original nodes at extreme edge removal.

| Removal | f | Mean S | Sample SD | GF reference |
|---|---:|---:|---:|---:|
| Edge | 0.50 | 0.98218 | 0.00128 | 0.98213 |
| Edge | 0.90 | 0.81540 | 0.00366 | 0.81431 |
| Edge | 0.99 | 0.11222 | 0.01592 | 0.12578 |
| Node | 0.50 | 0.49252 | 0.00345 | 0.49106 |
| Node | 0.90 | 0.08474 | 0.00351 | 0.08143 |

Under random node removal, S declines almost proportionally to the surviving fraction over much of the range. At f=0.50, S≈0.49252 means about 98.5% of surviving nodes belong to the largest component. A lower node-removal curve than edge-removal curve does not by itself show greater fragmentation at equal damage cost: deleted nodes directly reduce the numerator and remove multiple incident edges. The fixed N0 denominator and additional surviving-edge counts make this distinction explicit.

The GF reference tracks the main curves closely, with a more noticeable bond difference at extreme removal. This is a quantitative observation for this graph and these sample sizes, not proof that the network satisfies configuration-model assumptions. We do not assign a unique structural cause to the residual without further controls. The finite graph and discrete damage grid also do not support an exact universal critical threshold from curve shape alone.

### Sampling sensitivity and full-graph comparison

The filtered full graph gives a materially different bond curve. At f=0.50, mean S≈0.85830, compared with 0.98218 in the 5,000-node BFS graph, a difference of approximately 0.124. At f=0.90, the corresponding values are 0.55382 and 0.81540. These comparisons use the same damage definition and ten seeds, but the graphs have different compositions and permutation realizations; they are not paired measurements of identical physical failures.

The full-graph result shows that the BFS subgraph overstates retention of original nodes in the largest component for these damage levels. Protein-rich sampling, degree changes and the removal of peripheral parts of the full network are plausible contributors, but this experiment alone does not isolate their separate effects. We therefore present the 5,000-node curves as results for the agreed standard subgraph and use the full graph to constrain claims about PrimeKG more broadly.

### Validation and connection to subsequent workstreams

The union-find implementation was compared with independent NetworkX calculations at every deletion state on 80 small random graphs, including empty graphs and repeated semantic endpoint pairs. For each real graph, independent checks at f=0, 0.3, 0.5, 0.9 and 1 cover both edge and node deletion and six structural counts. The GF solver passes the analytic 3-regular configuration-model identity. Separately, a clean Python 3.11.9 rebuild reproduces all 68 core scientific graph/query/order files byte-for-byte, including the shared BFS prefix.

For downstream retrieval and restoration, reference fixtures contain endpoint survival, surviving two-hop path counts and PPI distances at the same seed-0 damage states. They are computed independently with NetworkX and can be used to validate C's retriever and E's zero-budget baseline. Formal integration with the other members' actual modules remains separate from these reference checks. This foundation allows the subsequent sections to ask whether a structurally large component still supports the fixed semantic tasks, and whether attacks or restoration alter that relationship.

### Figure files for the report editor

- `figures/act1/primekg_5000_bfs_v1/fig_degree_dist.pdf`: empirical type-specific degree CCDF.
- `figures/act1/primekg_5000_bfs_v1/fig_S_random_edge.pdf`: bond simulation and GF reference.
- `figures/act1/primekg_5000_bfs_v1/fig_S_random_node.pdf`: site simulation and GF reference.
- `figures/act1/primekg_5000_bfs_v1/fig_fragmentation.pdf`: components, isolates and mean degree.
- `figures/act1/fig_sampling_comparison.pdf`: BFS sizes and filtered full graph.

### References

1. Chandak, P., Huang, K. & Zitnik, M. (2023). Building a knowledge graph to enable precision medicine. Scientific Data 10, 67. Dataset: https://doi.org/10.7910/DVN/IXA7BM ; repository: https://github.com/mims-harvard/PrimeKG .
2. Newman, M. E. J. & Ziff, R. M. (2000). Efficient Monte Carlo algorithm and high-precision results for percolation. Physical Review Letters 85, 4104.
3. Callaway, D. S., Newman, M. E. J., Strogatz, S. H. & Watts, D. J. (2000). Network robustness and fragility: Percolation on random graphs. Physical Review Letters 85, 5468.
