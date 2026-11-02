import argparse
import importlib
import time
import platform
import numpy as np
import pandas as pd
from .common import *
from .percolation import nz_edges,nz_nodes,to_levels

def run(gid,theory_module='src.ws1_theory_reference'):
    nodes,edges=load_nodes(gid),load_edges(gid); n=len(nodes); uv=edges[['u','v']].to_numpy()
    tables=[]; timings=[]; theory=importlib.import_module(theory_module)
    degree=pd.read_csv(graph_dir(gid)/'node_features.csv').degree.to_numpy(dtype=np.int64)
    for kind,levels,func in [('edge',EDGE_LEVELS,nz_edges),('node',NODE_LEVELS,nz_nodes)]:
        total=len(edges) if kind=='edge' else n
        for seed in SEEDS:
            start=time.perf_counter(); out=func(n,uv,load_order(gid,f'{kind}_random_s{seed}'))
            tables.append(to_levels(out,levels,total,gid,f'{kind}_random',seed))
            timings.append({'strategy':kind+'_random','seed':seed,'seconds':time.perf_counter()-start})
            print(f'{gid} {kind} s{seed}: {timings[-1]["seconds"]:.2f}s',flush=True)
        for f in levels:
            removed=n_removed(f,total); keep=1-removed/total if total else 1.
            val=(theory.gcc_bond if kind=='edge' else theory.gcc_site)(degree,keep)
            tables.append(pd.DataFrame([[gid,'theory_bond' if kind=='edge' else 'theory_site',-1,f,removed,'gcc_frac',val]],columns=RESULT_COLUMNS))
    outdir=ROOT/'results/ws1'; outdir.mkdir(parents=True,exist_ok=True)
    df=pd.concat(tables,ignore_index=True); df.to_csv(outdir/f'{gid}__random.csv',index=False,lineterminator='\n')
    write_json(outdir/f'{gid}__provenance.json',{'gid':gid,'manifest_sha256':sha256(graph_dir(gid)/'manifest.json'),
        'run_python':platform.python_version(),'requirements_lock_sha256':sha256(ROOT/'requirements-lock.txt') if (ROOT/'requirements-lock.txt').exists() else None,
        'theory_module':theory_module,'theory_source_sha256':sha256(theory.__file__),
        'percolation_source_sha256':sha256(Path(__file__).with_name('percolation.py')),
        'edge_levels':EDGE_LEVELS,'node_levels':NODE_LEVELS,'seeds':list(SEEDS),'timings':timings,
        'theory_note':'GF assumes uncorrelated locally tree-like infinite configuration model; evaluated at actual retained fraction. Fallback is A reference, not D-approved.'})
    return df

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('gid'); p.add_argument('--theory-module',default='src.ws1_theory_reference'); a=p.parse_args(); run(a.gid,a.theory_module)

