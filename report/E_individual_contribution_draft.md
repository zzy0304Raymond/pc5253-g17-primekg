# Member E contribution draft

**Project:** PC5253 Group 17, PrimeKG structural and functional robustness.

Member E's work covers limited-budget restoration, the shared figure system and
the assembly of the group presentation. The implementation provides four repair
rankings and a pure restoration function that preserves the original damaged
mask. The policies compare random selection, original edge betweenness,
relation-type selection and a static training-query score. Budget accounting
records actual restored edges and any unspent allowance.

The experiment runner uses A's fixed damage orders and B's edge-betweenness
ranking. C's retrieval interface evaluates the test query IDs. Before C's module
was available, an E-owned edge-only evaluator provided independent L2/L3 checks.
Its results were later compared with C's output for all four restoration policies
on the 2,000- and 5,000-node graphs. All reported metrics and per-query indicators
matched in 640 strategy/budget states.

The main-graph restoration experiment shows a dependence on both budget and
query horizon. At 50% edge loss and 20% budget, relation-type restoration had the
largest mean two-hop retrieval gain, while edge betweenness had the largest mean
GCC gain. Static task-aware selection performed better at the smaller budget in
one main-graph comparison, but its gain grew more slowly after the small set of
positive-score candidates was exhausted. These are observations on the supplied
query split, without a claim of entity-disjoint generalization.

E also supplied shared matplotlib styles and twenty figure templates, a uniform
CSV-to-figure entry point, PNG/PDF/SVG outputs, tests for numerical aggregation
and restoration, English speaking notes, and report Sections 1 and 7. The group
deck incorporates A, B and C's available measurements and E's formal restoration
figures, with D's unsubmitted theory pages explicitly marked.

This is a factual contribution draft for the student's review. Personal identity,
course-specific declarations, reflection and any required contribution form
remain for the student to complete. It is not a completed peer-grading submission.
