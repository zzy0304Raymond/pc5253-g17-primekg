"""Stream the pinned CSV, audit types, normalize semantics, deterministic BFS."""
import argparse
from collections import Counter, deque
import platform
import numpy as np
import pandas as pd
import networkx as nx
from .common import ROOT, RELATIONS, NODE_TYPES, graph_dir, write_json, sha256

def write_graph(gid,node_records,semantic_edges,metadata):
    out=graph_dir(gid)
    if (out/'manifest.json').exists(): raise FileExistsError(f'{gid} is frozen; use a new gid or explicit clean rebuild in another root')
    out.mkdir(parents=True,exist_ok=True)
    ids=sorted(node_records); mapping={x:i for i,x in enumerate(ids)}
    nodes=pd.DataFrame([(mapping[x],x,*node_records[x]) for x in ids],columns=['nid','x_index','node_type','node_name'])
    rows=sorted({(r,min(mapping[u],mapping[v]),max(mapping[u],mapping[v])) for r,u,v in semantic_edges})
    edges=pd.DataFrame([(i,u,v,r) for i,(r,u,v) in enumerate(rows)],columns=['eid','u','v','relation'])
    nodes.to_csv(out/'nodes.csv',index=False,lineterminator='\n'); edges.to_csv(out/'edges.csv',index=False,lineterminator='\n')
    write_json(out/'build_metadata.json',metadata)
    return nodes,edges

def build(raw,sizes=(2000,5000),prefix='primekg'):
    records={}; semantic=set(); audit=Counter(); cross=Counter(); name_conflicts=0
    cols=['relation','x_index','x_type','x_name','y_index','y_type','y_name']
    allowed={'drug_protein':sorted(['drug','gene/protein']), 'disease_protein':sorted(['disease','gene/protein']), 'protein_protein':['gene/protein','gene/protein']}
    for chunk in pd.read_csv(raw,usecols=cols,chunksize=200000,keep_default_na=False):
        audit['raw_rows']+=len(chunk)
        for row,count in chunk.groupby(['relation','x_type','y_type']).size().items(): cross['|'.join(row)]+=int(count)
        selected=chunk[chunk.relation.isin(RELATIONS) & chunk.x_type.isin(NODE_TYPES) & chunk.y_type.isin(NODE_TYPES)]
        audit['selected_rows']+=len(selected)
        for r,x,xt,xn,y,yt,yn in selected[cols].itertuples(index=False,name=None):
            if sorted([xt,yt])!=allowed[r]: raise ValueError(f'Invalid relation endpoints {r}: {xt},{yt}')
            for ident in (x,y):
                if not str(ident).lstrip('-').isdigit(): raise ValueError(f'Noninteger original ID {ident}')
            x,y=int(x),int(y)
            for ident,typ,name in [(x,xt,str(xn)),(y,yt,str(yn))]:
                if ident in records:
                    if records[ident][0]!=typ: raise ValueError(f'Type conflict at {ident}')
                    if records[ident][1]!=name:
                        name_conflicts+=1; records[ident]=(typ,min(records[ident][1],name))
                else: records[ident]=(typ,name)
            if x==y: audit['self_loop_rows']+=1; continue
            key=(r,min(x,y),max(x,y))
            if key in semantic: audit['duplicate_or_reverse_rows']+=1
            semantic.add(key)
        print(f'Read {audit["raw_rows"]:,} rows; {len(semantic):,} retained relations',flush=True)
    if not semantic: raise ValueError('No supported edges')
    g=nx.Graph(); g.add_nodes_from(sorted(records)); g.add_edges_from((u,v) for _,u,v in sorted(semantic))
    diseases=[x for x in records if records[x][0]=='disease']
    if not diseases: raise ValueError('No disease nodes')
    start=min(diseases,key=lambda x:(-g.degree(x),x))
    queue=deque([start]); seen={start}; visit=[]
    while queue and len(visit)<max(sizes):
        u=queue.popleft(); visit.append(u)
        for v in sorted(g[u]):
            if v not in seen: seen.add(v); queue.append(v)
    if len(visit)<max(sizes): raise ValueError(f'BFS component only {len(visit)} nodes; cannot satisfy sizes')
    audit.update({'candidate_nodes':len(records),'semantic_edges':len(semantic),'structural_edges':g.number_of_edges(),'name_conflict_occurrences':name_conflicts})
    metadata={'raw_sha256':sha256(raw),'raw_bytes':raw.stat().st_size,'source_url':'https://dataverse.harvard.edu/api/access/datafile/6180620',
        'audit':dict(audit),'raw_relation_type_counts':dict(sorted(cross.items())), 'bfs_start_x_index':start,
        'bfs_start_degree':g.degree(start),'python':platform.python_version(),'networkx':nx.__version__,
        'node_policy':'Endpoints of selected rows, including nodes made isolated by self-loop removal',
        'name_policy':'Lexicographic minimum if labels disagree; IDs and types unchanged'}
    full=f'{prefix}_full_v1'; write_graph(full,records,semantic,{**metadata,'sampling':'all filtered candidate nodes'})
    for size in sizes:
        keep=set(visit[:size]); gid=f'{prefix}_{size}_bfs_v1'
        write_graph(gid,{x:records[x] for x in keep},{e for e in semantic if e[1] in keep and e[2] in keep},
            {**metadata,'sampling':'deterministic BFS induced subgraph','bfs_visit_x_indices':visit[:size]})
        print('Built '+gid,flush=True)
    write_json(ROOT/'data'/'raw'/'processing_audit.json',metadata)

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--raw',type=__import__('pathlib').Path,default=ROOT/'data/raw/kg.csv'); p.add_argument('--sizes',type=int,nargs='+',default=[2000,5000]); a=p.parse_args()
    build(a.raw,tuple(a.sizes))

