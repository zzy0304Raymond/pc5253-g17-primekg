# E restoration implementation plan

Scope: finish E-owned restoration code, experiment runner, tests, local reference
evaluation, plots and integration instructions in the existing D-drive checkout.
Keep A-D modules untouched. No dataset audits or frozen-data changes.

Decisions:
- Static task-aware scores per damage state; random tie breaking with damage seed + 100.
- Relation-type candidates never include PPI edges. When exhausted, leave budget
  unspent and record requested/actual restoration counts and shortfall.
- Formal default requires C's src.retrieval and B's original edge ranking.
- An explicitly selected E-owned L2/L3 reference evaluator supports local checks;
  it never silently substitutes for C and is labelled in every result.
- No data, experiment completion or result direction is fabricated.

Steps:
1. [x] Implement four ranking functions and pure mask restoration.
2. [x] Verify ranking, training-only scoring, nested budgets and immutable inputs
   against small independent graph cases.
3. [x] Implement a runner with fixed A deletion orders, test-query evaluation,
   actual budget accounting, edge-type counts, provenance and saved rankings.
4. [x] Implement an independent edge-only reference scorer for E's local verification.
5. [x] Run toy and available real-graph strategies explicitly in reference mode;
   render labelled preliminary figures and document B/C handoff requirements.
6. [x] Deliver E code, available results, figure previews and a 14-slide working deck.

Pending member integration: B's edge ranking, C's Retriever, then the final
four-policy experiment and complete group presentation rehearsal.
