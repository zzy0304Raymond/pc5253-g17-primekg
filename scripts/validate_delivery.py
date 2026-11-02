"""Final gates and machine-readable summary; no expected scientific trend imposed."""
import json
from pathlib import Path
import platform
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
from src.common import ROOT,graph_dir,sha256,write_json,EDGE_LEVELS,NODE_LEVELS,RESULT_COLUMNS
from src.validate_data import validate

gids=['primekg_2000_bfs_v1','primekg_5000_bfs_v1','primekg_full_v1']
summary=[]
for gid in gids:
    m=json.loads((graph_dir(gid)/'manifest.json').read_text(encoding='utf-8')); validate(gid)
    d=pd.read_csv(ROOT/'results/ws1'/f'{gid}__random.csv')
    assert list(d.columns)==RESULT_COLUMNS and len(d)==1846
    assert not d.duplicated(['strategy','seed','frac_removed','metric']).any()
    assert d.gid.eq(gid).all() and np.isfinite(d.value).all()
    for kind,levels in [('edge',EDGE_LEVELS),('node',NODE_LEVELS)]:
        for seed in range(10):
            a=d[(d.strategy==kind+'_random')&(d.seed==seed)&(d.metric=='gcc_frac')].sort_values('frac_removed')
            assert np.allclose(a.frac_removed,levels) and a.value.between(0,1).all()
            assert (np.diff(a.value)<=1e-12).all()
            assert abs(a.value.iloc[0]-m['gcc_size']/m['n_nodes'])<1e-12
    prov=json.loads((ROOT/'results/ws1'/f'{gid}__provenance.json').read_text())
    assert prov['manifest_sha256']==sha256(graph_dir(gid)/'manifest.json')
    assert prov['percolation_source_sha256']==sha256(ROOT/'src/percolation.py')
    assert prov['theory_source_sha256']==sha256(ROOT/'src/ws1_theory_reference.py')
    for f in ['fig_degree_dist','fig_S_random_edge','fig_S_random_node','fig_fragmentation']:
        for ext in ['png','pdf']: assert (ROOT/'figures/act1'/gid/f'{f}.{ext}').is_file()
    features=pd.read_csv(graph_dir(gid)/'node_features.csv')
    qmeta=json.loads((graph_dir(gid)/'query_metadata.json').read_text())
    lines=[f'# {gid}: data quality and scope','',f'- Nodes: {m["n_nodes"]:,}; semantic/structural edges: {m["n_edges"]:,}/{m["n_structural_edges"]:,}.',
        f'- Types: {m["node_type_counts"]}.',f'- Relations: {m["relation_counts"]}.',f'- Multiple-relation pairs: {m["pairs_with_multiple_relations"]}.',
        f'- Original GCC: {m["gcc_size"]:,}; components: {m["n_components"]}; isolates: {m["n_isolated"]}.',
        f'- Proteins with PPI degree zero: {m["ppi_zero_degree_count"]}; retain these proteins in C/D inputs.',
        f'- Query groups: {m["query_counts"]}; query split: {m["query_split_counts"]}.',
        f'- Unique selected drug/disease endpoints: {m["unique_query_drugs"]}/{m["unique_query_diseases"]}.',
        f'- Core data manifest SHA-256: `{sha256(graph_dir(gid)/"manifest.json")}`.',
        '- All selected queries have independently verified intact two-hop paths. Every random order is a complete seed-reproducible permutation.',
        '- Structural validation covers both removal modes at five fractions; independent PPI reference fixtures are supplied where queries exist.','']
    if gid.endswith('full_v1'): lines += ['## Scope limitation','','Structural comparison only. queries.json=[] is intentional; no retrieval benchmark is defined and R must not be reported as zero.']
    elif '2000' in gid: lines += ['## Important limitation','','Only three drugs occur in the prescribed BFS prefix. All 46 single and 66 multi queries are retained, so benchmark size is 112, not 200. Use for validation, not as an equivalent query sample to the standard graph.']
    else: lines += ['## Interpretation','','The 200 selected queries are balanced positive-path tasks, not a random sample of all possible drug–disease pairs. BFS composition differs materially from the filtered full graph; see sampling comparison.']
    (graph_dir(gid)/'data_quality.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    summary.append({'gid':gid,'nodes':m['n_nodes'],'edges':m['n_edges'],'queries':sum(m['query_counts'].values()),'results_rows':len(d),'mean_degree':float(features.degree.mean())})
assert json.loads((ROOT/'results/validation/reproducibility.json').read_text())['passed']
write_json(ROOT/'results/validation/delivery_summary.json',{'passed':True,'run_python':platform.python_version(),'graphs':summary,
    'formal_random_trajectories':60,'formal_result_rows':sum(x['results_rows'] for x in summary),
    'limitations':['D/E reference integration pending actual modules','2000 graph has 112 queries / 3 drugs','Full graph structural only',
        'Course submission, rehearsal and peer grading not performed'], 'raw_sha256':json.loads((ROOT/'data/raw/source.json').read_text())['sha256']})
print(json.dumps(summary,indent=2));print('FINAL SCIENTIFIC DELIVERY GATES PASS')
