import unittest
import numpy as np
import networkx as nx
from src.percolation import nz_edges,nz_nodes,to_levels
from src.common import n_removed

def direct(n,uv,edge_alive,node_alive):
    g=nx.Graph(); g.add_nodes_from(np.flatnonzero(node_alive).tolist())
    retained=[(int(a),int(b)) for (a,b),live in zip(uv,edge_alive) if live and node_alive[a] and node_alive[b]]
    g.add_edges_from(retained)
    return dict(gcc_size=max(map(len,nx.connected_components(g)),default=0),n_components=nx.number_connected_components(g),
        n_isolated=nx.number_of_isolates(g),n_alive=len(g),n_semantic_edges=len(retained),n_structural_edges=g.number_of_edges())

class PercolationTests(unittest.TestCase):
    def test_all_states_against_independent_networkx(self):
        rng=np.random.default_rng(314)
        for n in range(16):
            for trial in range(5):
                uv=np.asarray([(i,j) for i in range(n) for j in range(i+1,n) if rng.random()<.2],dtype=np.int64).reshape(-1,2)
                if trial%2 and len(uv): uv=np.concatenate([uv,uv[:2]]) # parallel semantic relations
                for kind in ['edge','node']:
                    order=rng.permutation(len(uv) if kind=='edge' else n)
                    got=(nz_edges if kind=='edge' else nz_nodes)(n,uv,order)
                    for t in range(len(order)+1):
                        ea=np.ones(len(uv),bool); na=np.ones(n,bool)
                        (ea if kind=='edge' else na)[order[:t]]=False
                        expected=direct(n,uv,ea,na)
                        for metric,value in expected.items(): self.assertEqual(got[metric][t],value,(n,trial,kind,t,metric))
    def test_validation(self):
        for bad in [np.array([0,0]),np.array([1]),np.array([.0]),np.array([-1])]:
            with self.assertRaises(ValueError): nz_edges(2,np.array([[0,1]]),bad)
        for f in [-.1,1.1,float('nan')]:
            with self.assertRaises(ValueError): n_removed(f,5)
        with self.assertRaises(ValueError): nz_nodes(2,[[0,0]],[0,1])
    def test_fixed_denominator(self):
        a=nz_nodes(3,[[0,1],[1,2]],[0,1,2]); df=to_levels(a,[0,1/3,1],3,'test','node_random',0)
        self.assertEqual(df[(df.frac_removed==1/3)&(df.metric=='gcc_frac')].value.iloc[0],2/3)

if __name__=='__main__': unittest.main()

