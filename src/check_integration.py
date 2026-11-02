"""Independent reference checks and portable downstream fixtures; no B-E implementation ownership."""
import argparse
import numpy as np
import pandas as pd
import networkx as nx
from .common import *
from .percolation import nz_edges,nz_nodes

def check(gid):
    nodes,edges,queries=load_nodes(gid),load_edges(gid),load_queries(gid); n=len(nodes); uv=edges[['u','v']].to_numpy()
    checked=[]; reference=[]; types=nodes.node_type.to_numpy()
    for kind,fn in [('edge',nz_edges),('node',nz_nodes)]:
        order=load_order(gid,f'{kind}_random_s0'); total=len(order); out=fn(n,uv,order)
        for f in [0,.3,.5,.9,1]:
            t=n_removed(f,total); ea=np.ones(len(edges),bool); na=np.ones(n,bool)
            (ea if kind=='edge' else na)[order[:t]]=False
            mask=effective_edge_mask(edges,ea,na); g=structural_graph(gid,ea,na)
            expect={'gcc_size':max(map(len,nx.connected_components(g)),default=0),'n_components':nx.number_connected_components(g),
                'n_isolated':nx.number_of_isolates(g),'n_alive':len(g),'n_structural_edges':g.number_of_edges(),'n_semantic_edges':int(mask.sum())}
            for metric,value in expect.items():
                if out[metric][t]!=value: raise AssertionError((gid,kind,f,metric,out[metric][t],value))
            checked.append({'strategy':kind+'_random','seed':0,'frac_removed':f,'n_removed':t,**expect})
            # Full semantic reference using NetworkX PPI BFS. Shared targets preserve zero-hop paths.
            ppi=nx.Graph(); ppi.add_nodes_from(nodes.loc[(nodes.node_type=='gene/protein')&na,'nid'].tolist())
            targets={}; dis={}
            for u,v,r in edges.loc[mask,['u','v','relation']].itertuples(index=False,name=None):
                if r=='protein_protein': ppi.add_edge(u,v)
                else:
                    ent,prot=(u,v) if types[u]!='gene/protein' else (v,u)
                    (targets if r=='drug_protein' else dis).setdefault(ent,set()).add(prot)
            cache={}
            for q in queries:
                d,s=q['drug_nid'],q['disease_nid']; a=targets.get(d,set()); b=dis.get(s,set())
                alive=bool(na[d] and na[s]); shared=len(a&b) if alive else 0; dist=float('inf')
                if alive and a and b:
                    if d not in cache: cache[d]=nx.multi_source_dijkstra_path_length(ppi,a,weight=None)
                    dist=min((cache[d].get(p,float('inf')) for p in b),default=float('inf'))
                if (dist==0)!=(shared>0): raise AssertionError('zero-hop inconsistency')
                if f==0 and shared!=q['redundancy_m']: raise AssertionError('baseline redundancy mismatch')
                reference.append({'gid':gid,'strategy':kind+'_random','seed':0,'frac_removed':f,'query_id':q['query_id'],
                    'drug_alive':bool(na[d]),'disease_alive':bool(na[s]),'s_alive':shared,'d_ppi':dist,
                    'R_L2':int(alive and shared>0),'R_L3':int(alive and np.isfinite(dist) and dist<=1),
                    'R_L4':int(alive and np.isfinite(dist) and dist<=2),'R_Linf':int(alive and np.isfinite(dist))})
            # E: copied zero-budget mask equals baseline; restore all deletions equals intact edges.
            if kind=='edge':
                restored=ea.copy(); restored[order[:t]]=True
                if not restored.all() or not np.array_equal(ea,effective_edge_mask(edges,ea)): raise AssertionError('restoration baseline mutation')
    outdir=ROOT/'results/validation'; outdir.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(checked).to_csv(outdir/f'{gid}__networkx_checks.csv',index=False)
    pd.DataFrame(reference).to_csv(outdir/f'{gid}__retrieval_reference.csv',index=False)
    write_json(outdir/f'{gid}__integration.json',{'passed':True,'structural_states':len(checked),'metrics_per_state':6,'queries_per_state':len(queries),
        'reference':'Independent NetworkX projection and PPI shortest paths. Not an execution of B/C/D/E modules.',
        'manifest_sha256':sha256(graph_dir(gid)/'manifest.json')})
    print(gid+': independent structural and retrieval checks PASS',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('gid'); check(p.parse_args().gid)
