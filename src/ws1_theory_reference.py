"""A's explicit fallback until D supplies theory.py; configuration-model GF."""
import numpy as np
from scipy.optimize import brentq

def gcc(degrees,keep,mode='bond'):
    degrees=np.asarray(degrees)
    if mode not in ('bond','site') or not 0<=keep<=1: raise ValueError('invalid mode/keep')
    if degrees.ndim!=1 or not np.issubdtype(degrees.dtype,np.integer) or np.any(degrees<0): raise ValueError('degrees must be nonnegative integers')
    if not len(degrees) or degrees.sum()==0 or keep==0: return 0.
    pk=np.bincount(degrees)/len(degrees); ks=np.arange(len(pk)); mean=float(np.dot(ks,pk))
    excess=float(np.dot(ks*(ks-1),pk)/mean)
    if keep*excess<=1: return 0.
    weights=ks[2:]*pk[2:]/mean; powers=ks[2:]-1
    def h(u):
        if u==1: return excess
        if u==0: return float(weights.sum())
        return float(np.dot(weights,np.expm1(powers*np.log(u))/np.expm1(np.log(u))))
    u=0. if keep*h(0)>=1 else brentq(lambda x:keep*h(x)-1,0,1,xtol=1e-13)
    s=1-float(np.dot(pk,u**ks))
    return max(0.,s*(keep if mode=='site' else 1.))

def gcc_bond(degrees,p): return gcc(degrees,p,'bond')
def gcc_site(degrees,phi): return gcc(degrees,phi,'site')

