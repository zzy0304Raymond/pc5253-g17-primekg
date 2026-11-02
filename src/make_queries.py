"""Deterministic query sampling, using per-drug sparse inverted joins."""
import argparse
from collections import defaultdict,Counter
import numpy as np
from .common import load_nodes,load_edges,graph_dir,write_json

def query_candidates(nodes,edges):
    types=nodes.node_type.to_numpy(); targets=defaultdict(set); diseases=defaultdict(set)
    for u,v,r in edges[['u','v','relation']].itertuples(index=False,name=None):
        if r=='drug_protein':
            d,p=(u,v) if types[u]=='drug' else (v,u); targets[d].add(p)
        elif r=='disease_protein':
            s,p=(u,v) if types[u]=='disease' else (v,u); diseases[p].add(s)
    single=[]; multi=[]
    for d in sorted(targets):
        counts=Counter(s for protein in sorted(targets[d]) for s in sorted(diseases[protein]))
        for s,m in sorted(counts.items()): (single if m==1 else multi).append((d,s))
    return single,multi,targets,diseases

def make_queries(gid):
    out=graph_dir(gid)
    if (out/'manifest.json').exists(): raise FileExistsError(f'{gid} frozen')
    nodes,edges=load_nodes(gid),load_edges(gid)
    single,multi,targets,diseases=query_candidates(nodes,edges)
    chosen=[]
    for group,pairs in [('single',single),('multi',multi)]:
        idx=np.random.default_rng(42).permutation(len(pairs))[:100]
        chosen += [(pairs[i],group) for i in sorted(idx)]
    train=set(np.random.default_rng(42).permutation(len(chosen))[:round(.7*len(chosen))].tolist())
    queries=[]; xi=nodes.x_index.to_numpy()
    for i,((d,s),group) in enumerate(chosen):
        inter=sorted(p for p in targets[d] if s in diseases[p])
        queries.append(dict(query_id=i,drug_nid=int(d),disease_nid=int(s),drug_x_index=int(xi[d]),disease_x_index=int(xi[s]),
            relation_pattern=['drug_protein','disease_protein'],max_hops=2,redundancy_m=len(inter),group=group,
            intermediates=[int(p) for p in inter],split='train' if i in train else 'test'))
    write_json(out/'queries.json',queries)
    write_json(out/'query_metadata.json',{'candidate_counts':{'single':len(single),'multi':len(multi)},
        'selected_counts':dict(Counter(q['group'] for q in queries)),'sampling_seed':42,'split_seed':42,
        'sampling':'Separate default_rng(42) permutation per sorted group; chosen indices sorted; single then multi',
        'split':'default_rng(42).permutation(query_id)[:round(0.7*n)]',
        'unique_drugs':len({q['drug_nid'] for q in queries}),'unique_diseases':len({q['disease_nid'] for q in queries}),
        'm_distribution':dict(sorted(Counter(q['redundancy_m'] for q in queries).items()))})
    print(f'{gid}: candidates single={len(single):,}, multi={len(multi):,}; selected={len(queries)}',flush=True)
    return queries

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('gid'); make_queries(p.parse_args().gid)

