"""Reverse-addition union-find. Array index t always means t removals."""
import numpy as np
import pandas as pd
try:
    from .common import check_order,n_removed,RESULT_COLUMNS
except ImportError:  # Support B's `from percolation import ...` with src on PYTHONPATH.
    from common import check_order,n_removed,RESULT_COLUMNS

def _input(n_nodes,edges_uv,order,kind):
    if not isinstance(n_nodes,(int,np.integer)) or n_nodes<0: raise ValueError('invalid node count')
    uv=np.asarray(edges_uv)
    if uv.size==0: uv=np.empty((0,2),dtype=np.int64)
    if uv.ndim!=2 or uv.shape[1]!=2 or not np.issubdtype(uv.dtype,np.integer): raise ValueError('edges_uv must be an integer (E,2) array')
    uv=uv.astype(np.int64,copy=False)
    if len(uv) and (uv.min()<0 or uv.max()>=n_nodes or np.any(uv[:,0]==uv[:,1])): raise ValueError('invalid endpoints or self-loops')
    uv=np.sort(uv,axis=1)
    return uv,check_order(order,len(uv) if kind=='edge' else n_nodes)

class _UnionFind:
    def __init__(self,n): self.parent=list(range(n)); self.size=[1]*n
    def find(self,a):
        while self.parent[a]!=a:
            self.parent[a]=self.parent[self.parent[a]]; a=self.parent[a]
        return a
    def union(self,a,b):
        a,b=self.find(a),self.find(b)
        if a==b: return 0
        if self.size[a]<self.size[b]: a,b=b,a
        self.parent[b]=a; self.size[a]+=self.size[b]
        return self.size[a]

def _arrays(total,n):
    out={k:np.zeros(total+1,dtype=np.int64) for k in ['gcc_size','n_components','n_isolated','n_alive','n_semantic_edges','n_structural_edges']}
    out['n_original']=int(n)
    return out

def nz_edges(n_nodes,edges_uv,order):
    uv,order=_input(n_nodes,edges_uv,order,'edge'); m=len(uv)
    pairs, inverse=np.unique(uv,axis=0,return_inverse=True)
    count=np.zeros(len(pairs),np.int64); degree=np.zeros(n_nodes,np.int64); uf=_UnionFind(n_nodes)
    out=_arrays(m,n_nodes); comp=isolated=n_nodes; largest=int(n_nodes>0); structural=0
    out['n_alive'][:]=n_nodes
    out['gcc_size'][m]=largest; out['n_components'][m]=comp; out['n_isolated'][m]=isolated
    for t in range(m-1,-1,-1):
        eid=int(order[t]); pid=int(inverse[eid]); count[pid]+=1
        if count[pid]==1:
            a,b=map(int,uv[eid]); isolated-=int(degree[a]==0)+int(degree[b]==0)
            degree[a]+=1; degree[b]+=1; structural+=1
            merged=uf.union(a,b)
            if merged: comp-=1; largest=max(largest,merged)
        out['gcc_size'][t]=largest; out['n_components'][t]=comp; out['n_isolated'][t]=isolated
        out['n_semantic_edges'][t]=m-t; out['n_structural_edges'][t]=structural
    return out

def nz_nodes(n_nodes,edges_uv,order):
    uv,order=_input(n_nodes,edges_uv,order,'node')
    pairs,counts=np.unique(uv,axis=0,return_counts=True)
    adjacency=[[] for _ in range(n_nodes)]
    for (a,b),c in zip(pairs.tolist(),counts.tolist()): adjacency[a].append((b,c)); adjacency[b].append((a,c))
    uf=_UnionFind(n_nodes); alive=np.zeros(n_nodes,bool); degree=np.zeros(n_nodes,np.int64)
    out=_arrays(n_nodes,n_nodes); comp=isolated=largest=structural=semantic=0
    for t in range(n_nodes-1,-1,-1):
        a=int(order[t]); alive[a]=True; comp+=1; isolated+=1; largest=max(largest,1)
        for b,c in adjacency[a]:
            if not alive[b]: continue
            semantic+=c; structural+=1; isolated-=int(degree[a]==0)+int(degree[b]==0)
            degree[a]+=1; degree[b]+=1
            merged=uf.union(a,b)
            if merged: comp-=1; largest=max(largest,merged)
        out['gcc_size'][t]=largest; out['n_components'][t]=comp; out['n_isolated'][t]=isolated
        out['n_alive'][t]=n_nodes-t; out['n_semantic_edges'][t]=semantic; out['n_structural_edges'][t]=structural
    return out

def to_levels(nz_out,levels,total,gid,strategy,seed):
    if len(nz_out['gcc_size'])!=total+1: raise ValueError('total does not match removal trajectory')
    n=nz_out['n_original']; rows=[]
    for f in levels:
        t=n_removed(f,total); alive=int(nz_out['n_alive'][t]); se=int(nz_out['n_structural_edges'][t])
        metrics={'gcc_frac':nz_out['gcc_size'][t]/n if n else 0.,
            'n_components':nz_out['n_components'][t], 'isolated_frac':nz_out['n_isolated'][t]/n if n else 0.,
            'avg_degree':2*se/alive if alive else 0., 'n_alive':alive,
            'n_semantic_edges':nz_out['n_semantic_edges'][t],'n_structural_edges':se}
        for metric,value in metrics.items(): rows.append([gid,strategy,seed,float(f),t,metric,float(value)])
    return pd.DataFrame(rows,columns=RESULT_COLUMNS)

