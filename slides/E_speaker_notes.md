# E speaker notes — working version

These notes describe the implemented methods and explicitly local results.
Replace the local-evaluator qualification after B/C integration; do not remove
it while presenting the current three-strategy figures.

## Slides 1–2: opening, about 1 minute total

We study what happens when a knowledge graph loses some of its relations.
Our question is whether a network that remains connected can still answer the
semantic queries we care about. In the example, a two-hop drug–protein–disease
path breaks, while a longer protein route keeps the graph connected. Allowing
that extra step changes which relations matter. We compare structural failure,
retrieval reliability and the limited-budget restoration of existing relations.

## Slide 12: two-hop restoration, about 1 minute

We begin with the same damaged graph for every policy. The budget is a fraction
of the deleted edges, and the task-aware ranking only sees training queries.
The figure reports gains on sixty held-out query IDs across ten damage seeds.
At fifty-percent damage and twenty-percent budget, relation-type restoration
gains 48.5 percentage points, compared with 13.2 for random and 24.8 for static
task-aware restoration. These are independent local checks; B and C integration
is still pending.

## Slide 13: three-hop restoration, about 55 seconds

With a three-hop limit, a path can include a protein–protein relation. We use the
same damaged states and the same rankings to evaluate this larger task horizon.
At fifty-percent damage and twenty-percent budget, the mean gains are 8.3,
15.7 and 12.3 percentage points for random, relation-type and static task-aware
restoration. The differences between policies and their dependence on budget
should be described from the curves rather than a predetermined ranking.

## Slide 14: closing, about 35 seconds

The scientific question combines a network, a semantic task and a damage budget.
Global connectivity and bounded retrieval inspect different properties. Our
restoration comparison shows why a type-matched control matters when explaining
an apparent task-aware advantage. The final four-policy comparison awaits B's
edge ranking and C's evaluator. Conclusions also need to retain the BFS sampling
scope, the selected positive queries and entity overlap between the query splits.

## Methods paragraph for later report integration

For each graph, we generated damaged states by deleting the prescribed prefix
of A's fixed random edge order at deletion fractions 0.3 and 0.5 for seeds 0–9.
Each policy started from a fresh copy of the same damaged mask. Restoration
budgets were 0, 0.05, 0.10 and 0.20 of the actual deleted-edge count, rounded
using the shared protocol. The static task-aware score counted two-hop paths
that a single missing edge could complete among currently unsuccessful training
queries. Ties were randomized with the damage seed plus 100. We evaluated the
GCC fraction and test-query success at L=2 and L=3, then subtracted each seed's
zero-budget baseline before aggregating gains as mean ± sample SD. The current
local runs use E's independent edge-only evaluator and exclude edge-betweenness
restoration until B's ranking is supplied.

## Likely questions

- Why can relation type beat task-aware? The static score prioritizes immediately
  completable training paths, then randomly orders zero-score candidates,
  including PPI edges. Relation-type restoration continues spending on the two
  endpoint relation types. Compare the edge-type composition and full curves.
- Is the score recomputed? No. It is fixed for each original damaged state.
- Does a two-edge break get a score? No. One restored edge cannot complete it.
- Did you use test queries to choose edges? No. Test query IDs only enter evaluation.
- Is this entity-disjoint generalization? No. Query IDs are split; entities may overlap.
- Does restoring every candidate recover the graph? It does for full rankings.
  Relation-type candidates intentionally exclude PPI edges, so that policy can
  exhaust its candidate set before the entire graph is restored.
- Do the current plots compare all four policies? No. Three policies have real
  local runs. The edge-betweenness implementation is tested but awaits B's ranking.
