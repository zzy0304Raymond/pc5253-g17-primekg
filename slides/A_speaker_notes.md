# A: slides 3–4, approximately three minutes

Use the 5000-node graph as the main result. The two-slide PPTX contains editable charts/table and source notes. E may adapt styling to the final shared template. The scripts below total roughly three minutes at a deliberate pace; actual rehearsal and timing are still needed.

## Slide 3 — PrimeKG and the shared experimental protocol (~75 seconds)

We use PrimeKG as a real example of a network whose structure and function can respond differently to damage. We retain drugs, diseases and proteins, together with three relation types. Our standard experiment uses a deterministic breadth-first sample of five thousand nodes and all eligible relations between those nodes.

The graph has about one hundred and eighteen thousand relations, but its composition is uneven: most nodes are proteins, while only seventy-four are drugs. The degree distributions also differ across entity types. We describe these distributions without assuming that they follow a power law.

For the later retrieval experiments, every query asks whether a drug and disease share a protein through the required relation types. We fix one hundred queries with a single path and one hundred with multiple paths. Everyone uses the same graph, queries and removal orders. This lets us compare structural and functional outcomes under exactly the same damage. Because BFS sampling changes the network, we also check the filtered full graph.

## Slide 4 — Random failure and the giant component (~105 seconds)

The structural question is: how much of the original network remains in one connected piece? We measure S as the largest surviving component divided by the original number of nodes.

Bond percolation removes relations while keeping the nodes. Site percolation removes nodes and all their incident relations. The denominator remains the original node count in both cases. The solid curves are the averages of ten random removal orders; the bounds show one standard deviation.

At fifty percent edge removal, about ninety-eight percent of the original nodes still belong to the largest component. At fifty percent node removal, the value is about forty-nine percent. That is close to all surviving nodes, so the lower curve partly reflects the nodes removed directly. Equal removal fractions do not imply equal numbers of lost relations.

The black dashed curves are generating-function predictions from the original degree distribution under a configuration-model approximation. They follow the main trends closely, although the extreme edge-removal region shows a larger discrepancy. Agreement here is an observation, not proof that the real network satisfies all model assumptions.

There is also a sampling limitation. In the filtered full graph, fifty percent edge removal leaves about eighty-six percent in the largest component, rather than ninety-eight percent. We therefore keep our claims specific to the graph being studied. The next question is what happens when the lost nodes are selected deliberately instead of randomly.

## Q&A preparation

- **Why use BFS?** It is the agreed deterministic protocol and keeps the main experiment computationally manageable. It is biased toward the selected connected neighborhood; the full-graph comparison quantifies a consequence of that choice.
- **Why does the small graph have fewer queries?** The prescribed prefix contains only three drugs. It supplies 46 single and 66 multi queries. We retained all valid queries rather than altering the protocol or padding duplicates.
- **Are the theoretical curves exact?** They are configuration-model references, evaluated at the actual retained fraction. Finite size, graph correlations and fixed-cardinality deletion limit exactness.
- **Why does deleting every edge leave GCC size one?** The nodes still exist as isolated vertices. For nonempty graphs S=1/N, whereas deleting every node gives S=0.
- **Is a drug–protein–disease path medical evidence of treatment?** It is a constrained association path, not proof of therapeutic efficacy.
- **Did you test the other members' code?** We supply independent structural and retrieval fixtures. Their actual implementations must be checked against those fixtures when available.

## Three handoff points for E

1. Standard graph: N=5,000, E=117,891, 200 fixed queries; all initially succeed.
2. At f=.5, bond S=.98218±.00128 and site S=.49252±.00345; use the original-N denominator.
3. Full-graph bond S=.85830 at f=.5, so sampling materially changes the apparent robustness.
