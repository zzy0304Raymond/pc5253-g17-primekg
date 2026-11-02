"""Reproduce the work plan's toy generator; common production query pipeline."""
import numpy as np
import networkx as nx
from .build_graph import write_graph
from .make_queries import make_queries
from .make_orders import make_orders

def make_toy():
    rng=np.random.default_rng(42); types=['drug']*60+['disease']*60+['gene/protein']*600
    records={i:(t,f'n{i}') for i,t in enumerate(types)}; semantic=set(); prots=np.arange(120,720)
    ppi=nx.barabasi_albert_graph(600,3,seed=42)
    for a,b in ppi.edges(): semantic.add(('protein_protein',min(a,b)+120,max(a,b)+120))
    w=np.array([ppi.degree(i) for i in range(600)],float); w/=w.sum()
    for ids,low,high,r in [(range(60),2,13,'drug_protein'),(range(60,120),5,26,'disease_protein')]:
        for d in ids:
            for p in rng.choice(prots,rng.integers(low,high),replace=False,p=w): semantic.add((r,d,int(p)))
    write_graph('toy_v1',records,semantic,{'source':'G17_Work_Plan Appendix A','seed':42,'synthetic':True})
    make_queries('toy_v1'); make_orders('toy_v1')

if __name__=='__main__': make_toy()

