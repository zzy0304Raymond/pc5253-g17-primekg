# C · Slides 6–8

## Slide 6 · Connectivity outlasts two-hop retrieval

**Figure:** `fig_S_vs_R`

- S measures how many original nodes remain in the largest component.
- R measures how many of the 200 original queries still have an allowed path.
- At 50% edge loss, the two metrics differ by 54.9 percentage points.

**Script:** We used the same deletion order for the structural and functional measurements. After random removal of half the edges, the largest connected component still contains 98.2 percent of the original nodes, averaged over ten seeds. Only 43.3 percent of the selected queries still have a two-hop path. Protein–protein edges can sustain the connected component, while a two-hop query needs one protein connected to both endpoints.

**Likely question:** Why are the curves so far apart?  
**Answer:** The largest component can be held together by protein–protein links. A two-hop query specifically needs two surviving terminal links incident to the same protein.

## Slide 7 · Queries with backup paths survive more often

**Figure:** `fig_R_by_group`

- Each group contains 100 queries.
- The groups use the intact graph's path counts.
- At 50% edge loss the success rates are 60.7% and 25.9%.

**Script:** We grouped queries by the number of shared proteins in the intact graph. Each group contains 100 queries. When half the edges are removed, 60.7 percent of queries with multiple paths still work, compared with 25.9 percent of single-path queries. A query can survive the loss of one shared protein route if both edges of another route remain.

**Likely question:** Is redundancy measured again after each deletion?  
**Answer:** We keep the original group labels fixed. Each damaged state tells us how many of the original routes remain.

## Slide 8 · One extra hop recovers many queries

**Figures:** `fig_R_L_curves` and `fig_R_L_heatmap`

- Every hop limit uses the same three damage seeds.
- One extra hop allows one protein–protein link.
- At 90% edge loss, four-hop and unlimited success are 28.7% and 37.0%.

**Script:** For this comparison, we use the same three damage seeds for every hop limit. At 50 percent edge removal, allowing one protein–protein step increases mean success from 40.3 to 84.5 percent. Four hops reach 89.5 percent. At more severe damage, the four-hop and unlimited curves separate. The heatmap shows how retrieval changes with both the deletion fraction and the allowed path length.

**Likely question:** Why is two-hop success 40.3% here and 43.3% on slide 6?  
**Answer:** The hop scan uses seeds 0–2 for every curve, while slide 6 uses all ten seeds. Both use the same frozen query set.
