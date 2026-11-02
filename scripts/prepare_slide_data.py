import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
from src.common import ROOT,graph_dir,write_json
gid='primekg_5000_bfs_v1'
m=json.loads((graph_dir(gid)/'manifest.json').read_text())
d=pd.read_csv(graph_dir(gid)/'node_features.csv'); results=pd.read_csv(ROOT/'results/ws1'/f'{gid}__random.csv')
degree=[]
for typ,color in [('drug','#1f77b4'),('disease','#ff7f0e'),('gene/protein','#2ca02c')]:
    a=d.loc[d.node_type==typ,'degree'].to_numpy(); k=np.unique(np.geomspace(1,a.max(),35).astype(int)); p=np.array([(a>=v).mean() for v in k]); mask=p>0
    degree.append({'name':typ,'x':np.log10(k[mask]).tolist(),'y':np.log10(p[mask]).tolist(),'color':color})
curves={}
for kind,th in [('edge','theory_bond'),('node','theory_site')]:
    a=results[(results.strategy==kind+'_random')&(results.metric=='gcc_frac')].groupby('frac_removed').value.agg(['mean','std'])
    t=results[(results.strategy==th)&(results.metric=='gcc_frac')].sort_values('frac_removed')
    curves[kind]={'x':a.index.tolist(),'mean':a['mean'].tolist(),'std':a['std'].tolist(),'theory':t.value.tolist()}
write_json(ROOT/'slides/chart_data.json',{'gid':gid,'counts':m['node_type_counts'],'edges':m['n_edges'],'degree':degree,'curves':curves})
