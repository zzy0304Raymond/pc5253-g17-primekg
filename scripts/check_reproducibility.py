"""Rebuild in an isolated root under the current interpreter and compare scientific files."""
import os
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.common import ROOT,sha256,write_json

def main():
    root=ROOT/'.build/repro311'; root.mkdir(parents=True,exist_ok=True)
    env={**os.environ,'G17_ROOT':str(root)}
    subprocess.run([sys.executable,'-m','src.build_graph','--raw',str(ROOT/'data/raw/kg.csv')],env=env,check=True)
    gids=['primekg_2000_bfs_v1','primekg_5000_bfs_v1','primekg_full_v1']; checked=[]
    for gid in gids:
        if gid!='primekg_full_v1': subprocess.run([sys.executable,'-m','src.make_queries',gid],env=env,check=True)
        subprocess.run([sys.executable,'-m','src.make_orders',gid],env=env,check=True)
        paths=['nodes.csv','edges.csv']+(['queries.json'] if gid!='primekg_full_v1' else [])
        paths += [f'orders/{kind}_random_s{s}.npy' for kind in ['edge','node'] for s in range(10)]
        for rel in paths:
            a=sha256(ROOT/'data/processed'/gid/rel); b=sha256(root/'data/processed'/gid/rel)
            if a!=b: raise AssertionError(f'{gid}/{rel} not reproducible')
            checked.append(f'{gid}/{rel}')
    import pandas as pd
    small=pd.read_csv(ROOT/'data/processed/primekg_2000_bfs_v1/nodes.csv')
    large=pd.read_csv(ROOT/'data/processed/primekg_5000_bfs_v1/nodes.csv')
    if not set(small.x_index)<=set(large.x_index): raise AssertionError('prefix inclusion failed')
    import json
    a=json.loads((ROOT/'data/processed/primekg_2000_bfs_v1/build_metadata.json').read_text())['bfs_visit_x_indices']
    b=json.loads((ROOT/'data/processed/primekg_5000_bfs_v1/build_metadata.json').read_text())['bfs_visit_x_indices']
    if a!=b[:2000]: raise AssertionError('BFS prefix mismatch')
    write_json(ROOT/'results/validation/reproducibility.json',{'passed':True,'python':sys.version,'scientific_files_checked':checked,'bfs_prefix_verified':True,
        'note':'Rebuilt from same verified raw CSV in isolated root; bytewise SHA256 equality. Metadata may differ by environment.'})
    print(f'Reproducibility PASS: {len(checked)} files identical; BFS prefix verified',flush=True)

if __name__=='__main__': main()
