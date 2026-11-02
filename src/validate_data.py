"""Validate and freeze a graph. Semantic checks are independent of query generator."""
import argparse
from collections import Counter,defaultdict
import json
import platform
import numpy as np
import pandas as pd
import networkx as nx
from .common import *

def validate(gid,freeze=False):
    out=graph_dir(gid); nodes=load_nodes(gid); edges=load_edges(gid); queries=load_queries(gid)
    def require(ok,msg):
        if not ok: raise ValueError(gid+': '+msg)
    n,e=len(nodes),len(edges)
    require(nodes.x_index.is_unique and nodes.x_index.is_monotonic_increasing,'x_index not unique/sorted')
    require(set(nodes.node_type)<=set(NODE_TYPES),'unknown node type')
    require(set(edges.relation)<=set(RELATIONS),'unknown relation')
    uv=edges[['u','v']].to_numpy()
    require(not e or (uv.min()>=0 and uv.max()<n and np.all(uv[:,0]<uv[:,1])),'invalid endpoints')
    require(not edges.duplicated(['relation','u','v']).any(),'duplicate semantic edge')
    require(edges[['relation','u','v']].equals(edges.sort_values(['relation','u','v'])[['relation','u','v']].reset_index(drop=True)),'edge sort mismatch')
    types=nodes.node_type.to_numpy(); neighborhoods=defaultdict(set)
    expected={'drug_protein':sorted(['drug','gene/protein']),'disease_protein':sorted(['disease','gene/protein']),'protein_protein':['gene/protein']*2}
    for u,v,r in edges[['u','v','relation']].itertuples(index=False,name=None):
        require(sorted([types[u],types[v]])==expected[r],'relation endpoints mismatch')
        neighborhoods[(u,r)].add(v); neighborhoods[(v,r)].add(u)
    require([q['query_id'] for q in queries]==list(range(len(queries))),'query_id order')
    require(len({(q['drug_nid'],q['disease_nid']) for q in queries})==len(queries),'duplicate query')
    train=set(np.random.default_rng(42).permutation(len(queries))[:round(.7*len(queries))].tolist())
    for q in queries:
        d,s=q['drug_nid'],q['disease_nid']; require(0<=d<n and 0<=s<n,'query endpoint range')
        require(types[d]=='drug' and types[s]=='disease','query endpoint type')
        shared=sorted(neighborhoods[(d,'drug_protein')] & neighborhoods[(s,'disease_protein')])
        require(bool(shared) and shared==q['intermediates'] and len(shared)==q['redundancy_m'],'query path mismatch')
        require(q['group']==('single' if len(shared)==1 else 'multi'),'query group mismatch')
        require(q['drug_x_index']==int(nodes.x_index.iloc[d]) and q['disease_x_index']==int(nodes.x_index.iloc[s]),'original query ID mismatch')
        require(q['relation_pattern']==['drug_protein','disease_protein'] and q['max_hops']==2,'query pattern mismatch')
        require(q['split']==('train' if q['query_id'] in train else 'test'),'query split mismatch')
    for kind,total in [('edge',e),('node',n)]:
        for seed in SEEDS:
            order=load_order(gid,f'{kind}_random_s{seed}')
            require(np.array_equal(order,np.random.default_rng(seed).permutation(total)),'random order not reproducible')
            require(set(order[:n_removed(.1,total)])<=set(order[:n_removed(.2,total)]),'non-nested order')
    g=structural_graph(gid); protein_ids=nodes.loc[nodes.node_type=='gene/protein','nid'].tolist()
    ppi=nx.Graph(); ppi.add_nodes_from(protein_ids); ppi.add_edges_from(edges.loc[edges.relation=='protein_protein',['u','v']].itertuples(index=False,name=None))
    multiple=int((edges.groupby(['u','v']).size()>1).sum())
    degree=pd.DataFrame({'nid':nodes.nid,'x_index':nodes.x_index,'node_type':nodes.node_type,
        'degree':[g.degree(i) for i in range(n)], 'ppi_degree':[ppi.degree(i) if i in ppi else 0 for i in range(n)]})
    for rel in RELATIONS: degree['degree_'+rel]=[len(neighborhoods[(i,rel)]) for i in range(n)]
    groups=Counter(q['group'] for q in queries); split_counts=Counter(q['group']+'_'+q['split'] for q in queries)
    warnings=[]
    for group in ['single','multi']:
        if groups[group]<100: warnings.append(f'{group}: only {groups[group]} selected queries; no padding')
    if multiple: warnings.append('Multiple semantic relations per structural pair: verify downstream projection')
    top_d=Counter(q['disease_nid'] for q in queries).most_common(1)
    summary={'gid':gid,'n_nodes':n,'n_edges':e,'n_structural_edges':g.number_of_edges(),
        'node_type_counts':dict(Counter(nodes.node_type)),'relation_counts':dict(Counter(edges.relation)),
        'query_counts':dict(groups),'query_split_counts':dict(split_counts),'pairs_with_multiple_relations':multiple,
        'gcc_size':max(map(len,nx.connected_components(g)),default=0),'n_components':nx.number_connected_components(g),
        'n_isolated':nx.number_of_isolates(g),'n_proteins':len(ppi),'ppi_zero_degree_count':nx.number_of_isolates(ppi),
        'ppi_gcc_size':max(map(len,nx.connected_components(ppi)),default=0),
        'unique_query_drugs':len({q['drug_nid'] for q in queries}),'unique_query_diseases':len({q['disease_nid'] for q in queries}),
        'max_queries_per_disease':top_d[0][1] if top_d else 0,'warnings':warnings,
        'metrics':{'gcc_frac':'gcc_size/N_original','isolated_frac':'alive isolated/N_original','avg_degree':'2*alive_structural_edges/N_alive; 0 for empty graph','n_components':'alive nodes only'},
        'environment':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'networkx':nx.__version__}}
    if (out/'manifest.json').exists():
        manifest=json.loads((out/'manifest.json').read_text(encoding='utf-8'))
        for path,digest in manifest['sha256'].items(): require(sha256(out/path)==digest,'hash changed: '+path)
    elif freeze:
        degree.to_csv(out/'node_features.csv',index=False,lineterminator='\n')
        summary['build']=json.loads((out/'build_metadata.json').read_text(encoding='utf-8'))
        summary['queries']=json.loads((out/'query_metadata.json').read_text(encoding='utf-8'))
        files=[p for p in out.rglob('*') if p.is_file() and p.suffix in ('.csv','.json','.npy')]
        summary['sha256']={p.relative_to(out).as_posix():sha256(p) for p in sorted(files)}
        write_json(out/'manifest.json',summary)
    report=ROOT/'results'/'validation'/f'{gid}.json'; write_json(report,summary)
    print(f'{gid}: VALID; N={n}, semantic E={e}, queries={len(queries)}, warnings={warnings}',flush=True)
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('gid'); p.add_argument('--freeze',action='store_true'); a=p.parse_args(); validate(a.gid,a.freeze)
