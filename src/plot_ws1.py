"""English WS1 figures, using E's plotting module when supplied."""
import argparse
import importlib
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .common import ROOT,graph_dir,load_nodes

def setup():
    try: e=importlib.import_module('src.plotting')
    except ModuleNotFoundError as exc:
        if exc.name!='src.plotting': raise
        e=None
    if e: e.setup()
    else: plt.rcParams.update({'font.size':12,'figure.figsize':(6,4),'savefig.dpi':300,'axes.spines.top':False,'axes.spines.right':False})

def save(fig,name,folder):
    folder.mkdir(parents=True,exist_ok=True)
    for ext in ('png','pdf'): fig.savefig(folder/f'{name}.{ext}',bbox_inches='tight')
    plt.close(fig)

def plot(gid):
    setup(); folder=ROOT/'figures/act1'/gid
    df=pd.read_csv(ROOT/'results/ws1'/f'{gid}__random.csv')
    for kind,color,th in [('edge','#1f77b4','theory_bond'),('node','#2ca02c','theory_site')]:
        data=df[(df.strategy==kind+'_random')&(df.metric=='gcc_frac')]
        agg=data.groupby('frac_removed').value.agg(['mean','std']).reset_index()
        theory=df[(df.strategy==th)&(df.metric=='gcc_frac')]
        fig,ax=plt.subplots(); x=agg.frac_removed.to_numpy(); y=agg['mean'].to_numpy(); sd=agg['std'].to_numpy()
        ax.plot(x,y,'o-',color=color,label=f'Random {kind} removal')
        ax.fill_between(x,np.maximum(0,y-sd),np.minimum(1,y+sd),color=color,alpha=.2,label='Mean ± 1 SD (10 seeds)')
        ax.plot(theory.frac_removed,theory.value,'k--',label='Configuration-model GF')
        ax.set(xlabel='Fraction removed f',ylabel='Largest component / original N',ylim=(-.02,1.05),xlim=(0,1))
        ax.legend(fontsize=9,loc='lower left'); ax.grid(alpha=.15); fig.tight_layout()
        save(fig,f'fig_S_random_{kind}',folder)
    features=pd.read_csv(graph_dir(gid)/'node_features.csv')
    fig,ax=plt.subplots()
    # Empirical survival probabilities sampled at logarithmically spaced degree thresholds.
    thresholds=np.unique(np.geomspace(1,max(2,features.degree.max()),60).astype(int))
    for typ,color in [('drug','#1f77b4'),('disease','#ff7f0e'),('gene/protein','#2ca02c')]:
        d=features.loc[features.node_type==typ,'degree'].to_numpy()
        if not len(d): continue
        ccdf=np.array([(d>=k).mean() for k in thresholds]); keep=ccdf>0
        ax.loglog(thresholds[keep],ccdf[keep],'.-',color=color,label=f'{typ} (n={len(d):,})')
    ax.set(xlabel='Degree k',ylabel='P(K ≥ k)'); ax.legend(fontsize=9); ax.grid(alpha=.15); fig.tight_layout()
    save(fig,'fig_degree_dist',folder)
    fig,axes=plt.subplots(1,3,figsize=(13,3.8))
    for ax,metric,label in zip(axes,['n_components','isolated_frac','avg_degree'],['Connected components','Isolated / original N','Mean degree of surviving nodes']):
        for kind,color in [('edge','#1f77b4'),('node','#2ca02c')]:
            a=df[(df.strategy==kind+'_random')&(df.metric==metric)].groupby('frac_removed').value.agg(['mean','std'])
            ax.plot(a.index,a['mean'],color=color,label=kind+' removal'); ax.fill_between(a.index,a['mean']-a['std'],a['mean']+a['std'],color=color,alpha=.18)
        ax.set(xlabel='Fraction removed f',ylabel=label); ax.grid(alpha=.15)
    axes[0].legend(fontsize=9); fig.tight_layout(); save(fig,'fig_fragmentation',folder)

def comparison(gids):
    setup(); fig,axes=plt.subplots(1,2,figsize=(12,4)); colors=['#1f77b4','#ff7f0e','#2ca02c']
    for gid,color in zip(gids,colors):
        features=pd.read_csv(graph_dir(gid)/'node_features.csv'); d=np.sort(features.degree.to_numpy()); k=np.unique(np.geomspace(1,max(2,d.max()),60).astype(int))
        ccdf=(len(d)-np.searchsorted(d,k))/len(d); mask=ccdf>0; label=f'N={len(d):,}'
        axes[0].loglog(k[mask],ccdf[mask],'.-',color=color,label=label)
        df=pd.read_csv(ROOT/'results/ws1'/f'{gid}__random.csv'); a=df[(df.strategy=='edge_random')&(df.metric=='gcc_frac')].groupby('frac_removed').value.agg(['mean','std'])
        axes[1].plot(a.index,a['mean'],color=color,label=label); axes[1].fill_between(a.index,a['mean']-a['std'],a['mean']+a['std'],color=color,alpha=.15)
    axes[0].set(xlabel='Degree k',ylabel='P(K ≥ k)'); axes[1].set(xlabel='Fraction removed f',ylabel='Largest component / original N')
    for ax in axes: ax.legend(); ax.grid(alpha=.15)
    fig.tight_layout(); save(fig,'fig_sampling_comparison',ROOT/'figures/act1')

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('gids',nargs='+'); p.add_argument('--compare',action='store_true'); a=p.parse_args()
    for gid in a.gids: plot(gid)
    if a.compare: comparison(a.gids)
