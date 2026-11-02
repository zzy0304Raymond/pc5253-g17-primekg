"""One command after verified download. Frozen artifacts are checked, not regenerated."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.common import ROOT,graph_dir,write_json,sha256
from src.build_graph import build
from src.make_toy import make_toy
from src.make_queries import make_queries
from src.make_orders import make_orders
from src.validate_data import validate
from src.check_integration import check
from src.run_ws1 import run
from src.plot_ws1 import plot,comparison

def main():
    raw=ROOT/'data/raw/kg.csv'; source=json.loads((raw.parent/'source.json').read_text())
    if sha256(raw)!=source['sha256']: raise ValueError('raw source SHA256 mismatch')
    if not (graph_dir('toy_v1')/'manifest.json').exists():
        if not (graph_dir('toy_v1')/'nodes.csv').exists(): make_toy()
        validate('toy_v1',True)
    gids=['primekg_2000_bfs_v1','primekg_5000_bfs_v1','primekg_full_v1']
    if not all((graph_dir(g)/'nodes.csv').exists() for g in gids): build(raw)
    for gid in gids:
        out=graph_dir(gid)
        if not (out/'manifest.json').exists():
            if gid!='primekg_full_v1': make_queries(gid)
            else:
                write_json(out/'queries.json',[])
                write_json(out/'query_metadata.json',{'scope':'Structural full-graph comparison only; no functional benchmark defined',
                    'candidate_counts':{},'selected_counts':{},'sampling_seed':None,'split_seed':None})
            make_orders(gid); validate(gid,True)
        else: validate(gid)
        check(gid)
        run(gid); plot(gid)
    comparison(gids)
    print('A pipeline completed',flush=True)

if __name__=='__main__': main()
