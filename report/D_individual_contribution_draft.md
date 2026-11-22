# Member D — Individual contribution draft

**Name:** ZHENG FANGWEN

**Project:** PC5253 Group 17, theory and prediction of knowledge-graph retrieval robustness (WS4)

My assigned workstream was the theory layer of the project: zero-parameter predictions for the structural and functional measurements, a test of where those predictions hold, and the prediction of retrieval failure. I also proposed the theory additions to the original project plan, including the hop-limit dimension and the zero-parameter retrieval formula.

For connectivity, `src/theory.py` implements the generating-function predictions for random edge removal, random node removal and degree attack, together with the Molloy–Reed threshold. I checked them on random graphs with the same degree sequence, where they agree with simulation to about 0.001, and against A's independent reference implementation, where they agree to 2×10⁻¹³. For retrieval, I derived the two-hop success formula R₂ = 1 − G_m(1 − p²). It treats each query as a series–parallel network of m independent routes. Over 5,000 fresh damage orders it agrees with simulation to within 0.001. I also derived the long-horizon limit, which describes attachment of the endpoints to the protein–protein giant component. This led to the finding that, for every query, the drug–disease minimum cut equals the smaller endpoint degree. As a result, longer horizons move the bottleneck to drug target links, and the percolation collapse we had expected does not appear.

For prediction (`src/prediction.py`, `src/run_ws4.py`), I showed that the formula reaches the chance-limited AUC ceiling for predicting which query fails. I measured and decomposed the correlation penalty under targeted attacks: 57–64 percentage points at a 5% attack, split into lost endpoints and lost paths through hubs. I also showed that the formula predicts E's restoration gains within one seed SD in all twelve cases. For the report stage I added a degree-preserving null-model test (`src/run_null_model.py`, with tests). It traces the extra structural fragility under degree attack to disassortative mixing and higher-order structure. I also added an uncertainty analysis that explains the width of the seed bands, the question we could not answer during the presentation.

I wrote report Sections 3 and 6, the abstract, the findings list in the introduction, the theory parts of Section 8, and the D entries in the reproducibility appendix. I also prepared slides 10–12 and their backup slides, and the theory Q&A notes.

AI assistance was used for coding and drafting. I checked the derivations and numerical results, and the claims in the report trace to files in `results/ws4/`.
