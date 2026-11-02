# Member A — Individual contribution draft

This factual draft covers work implemented in this workspace. Add the required personal identification and any course-specific reflection format before submission. Do not claim attendance, group decisions or review activities that have not occurred.

My assigned responsibility was the shared data foundation and WS1 random network failure. The work produced a reproducible pipeline from the fixed PrimeKG source to deterministic standard graphs, fixed semantic queries and nested random failure states. Source checksums, graph-local node/edge IDs and frozen file manifests allow the other workstreams to use identical experiments.

The data audit identified an important difference between the two agreed graph sizes. The 2,000-node BFS graph contains only three drugs and supports 112 queries, whereas the 5,000-node graph supports the intended 200-query benchmark. The implementation preserves these actual counts and documents the implications for retrieval, prediction and restoration. It also supplies original-degree and PPI-degree features, including isolated proteins, for downstream theory and retrieval.

For WS1, reverse-addition union-find algorithms compute largest components, component counts and isolated nodes under both edge and node failure. The implementation is validated against direct NetworkX calculations on all removal states of small graphs and on selected states of the real graphs. It handles repeated semantic edges on one structural pair and distinguishes deleted nodes from surviving isolates.

The experimental deliverables include ten-seed random edge and node curves on the 2,000-node, 5,000-node and filtered full graphs, GF reference curves, degree distributions and fragmentation plots. At 50% edge removal the standard BFS graph retains approximately 98.2% of original nodes in its largest component, compared with 85.8% in the filtered full graph. This result motivated an explicit sampling limitation in the report.

To support the team, the package includes a data contract, per-member handoff instructions and independent per-query reference fixtures for future retrieval and restoration integration. The final computations were checked under Python 3.11.9, and a fresh reconstruction matched 68 scientific data files byte-for-byte. A two-slide editable presentation and report sections on the data protocol and random failure were prepared.

AI coding and drafting assistance was used for this workspace. The member should personally verify the scientific interpretation, understand the implementation, and follow the course's applicable disclosure rules. Actual group integration, rehearsals, peer grading and final institutional submission are separate activities and are not claimed as completed here.
