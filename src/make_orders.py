import argparse
import numpy as np
from .common import graph_dir,load_nodes,load_edges,SEEDS

def make_orders(gid):
    out=graph_dir(gid)
    if (out/'manifest.json').exists(): raise FileExistsError(f'{gid} frozen')
    (out/'orders').mkdir(exist_ok=True)
    for kind,total in [('edge',len(load_edges(gid))),('node',len(load_nodes(gid)))]:
        for seed in SEEDS: np.save(out/'orders'/f'{kind}_random_s{seed}.npy',np.random.default_rng(seed).permutation(total))

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('gid'); make_orders(p.parse_args().gid)
