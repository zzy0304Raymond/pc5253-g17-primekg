"""Shared contract. All IDs are local to gid; no mutable global data caches."""
from pathlib import Path
import hashlib
import json
import math
import os
import numpy as np
import pandas as pd

ROOT = Path(os.environ.get('G17_ROOT', Path(__file__).resolve().parents[1])).resolve()
EDGE_LEVELS = [0, .05, .10, .20, .30, .40, .50, .60, .70, .80, .85, .90, .95, .97, .99]
NODE_LEVELS = [0, .05, .10, .20, .30, .40, .50, .60, .70, .80, .90]
SEEDS = range(10)
RELATIONS = ('drug_protein', 'disease_protein', 'protein_protein')
NODE_TYPES = ('drug', 'disease', 'gene/protein')
RESULT_COLUMNS = ['gid','strategy','seed','frac_removed','n_removed','metric','value']

def graph_dir(gid):
    if not isinstance(gid,str) or not gid or Path(gid).name != gid or gid in ('.','..') or '/' in gid or '\\' in gid:
        raise ValueError('gid must be a single directory name')
    return ROOT / 'data' / 'processed' / gid

def load_nodes(gid):
    df = pd.read_csv(graph_dir(gid)/'nodes.csv', keep_default_na=False)
    if not np.array_equal(df.nid, np.arange(len(df))): raise ValueError('nodes not in nid order')
    return df

def load_edges(gid):
    df = pd.read_csv(graph_dir(gid)/'edges.csv', keep_default_na=False)
    if not np.array_equal(df.eid, np.arange(len(df))): raise ValueError('edges not in eid order')
    return df

def load_queries(gid):
    return json.loads((graph_dir(gid)/'queries.json').read_text(encoding='utf-8'))

def check_order(order, total):
    a=np.asarray(order)
    if a.ndim != 1 or not np.issubdtype(a.dtype,np.integer) or len(a)!=total or not np.array_equal(np.sort(a),np.arange(total)):
        raise ValueError(f'order must be a permutation of 0..{total-1}')
    return a.astype(np.int64,copy=False)

def load_order(gid,name):
    if Path(name).name != name or '/' in name or '\\' in name: raise ValueError('invalid order name')
    if not name.startswith(('edge_','node_')): raise ValueError('order must start edge_ or node_')
    a=np.load(graph_dir(gid)/'orders'/f'{name}.npy',allow_pickle=False)
    total=len(load_edges(gid)) if name.startswith('edge_') else len(load_nodes(gid))
    return check_order(a,total).copy()

def n_removed(frac,total):
    if not math.isfinite(frac) or not 0<=frac<=1: raise ValueError('frac must be finite and in [0,1]')
    if not isinstance(total,(int,np.integer)) or total<0: raise ValueError('total must be a nonnegative integer')
    return int(round(float(frac)*int(total)))

def _mask(gid,name,frac,kind):
    if not name.startswith(kind+'_'): raise ValueError(f'expected {kind} order')
    order=load_order(gid,name); mask=np.ones(len(order),dtype=bool)
    mask[order[:n_removed(frac,len(order))]]=False
    return mask

def edge_alive_mask(gid,order_name,frac): return _mask(gid,order_name,frac,'edge')
def node_alive_mask(gid,order_name,frac): return _mask(gid,order_name,frac,'node')

def effective_edge_mask(edges,edge_alive=None,node_alive=None):
    alive=np.ones(len(edges),bool) if edge_alive is None else np.asarray(edge_alive,dtype=bool).copy()
    if alive.shape != (len(edges),): raise ValueError('edge mask shape mismatch')
    if node_alive is not None:
        nodes=np.asarray(node_alive,dtype=bool)
        if nodes.ndim!=1 or (len(edges) and edges[['u','v']].to_numpy().max()>=len(nodes)): raise ValueError('node mask shape mismatch')
        alive &= nodes[edges.u.to_numpy()] & nodes[edges.v.to_numpy()]
    return alive

def structural_graph(gid,edge_alive=None,node_alive=None):
    import networkx as nx
    nodes=load_nodes(gid); edges=load_edges(gid)
    na=np.ones(len(nodes),bool) if node_alive is None else np.asarray(node_alive,dtype=bool)
    if na.shape!=(len(nodes),): raise ValueError('node mask shape mismatch')
    g=nx.Graph(); g.add_nodes_from(nodes.nid.to_numpy()[na].tolist())
    g.add_edges_from(edges.loc[effective_edge_mask(edges,edge_alive,na),['u','v']].itertuples(index=False,name=None))
    return g

def sha256(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''): h.update(b)
    return h.hexdigest()

def write_json(path,value):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    tmp.replace(path)

