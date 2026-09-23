"""Evaluate the frozen final STEPS grid from user-supplied forecast caches."""
from __future__ import annotations
import json, time
from pathlib import Path
import numpy as np
from . import method as ge
from . import method as fs
from . import method as loc
from .cache import load

DATASETS = ("ETTh1", "ETTh2", "ETTm1", "ETTm2", "exchange_rate", "weather")
BACKBONES = ("DLinear", "OLS", "PatchTST", "iTransformer", "FreTS", "TimeMixer")
HORIZONS = (96, 192, 336, 720)
BETAS = np.linspace(-0.5, 1.5, 41)
FRETS_RELEASE_SEEDS = {"ETTh1": 1, "ETTh2": 2, "ETTm1": 2, "ETTm2": 0,
                       "exchange_rate": 0, "weather": 2}
TRAINING = {
    "DLinear": (30, 256),
    "OLS": (30, 256),
    "PatchTST": (30, 256),
    "iTransformer": (30, 256),
    "FreTS": (30, 256),
}

def training_config(backbone, dataset, horizon):
    if backbone == "FreTS" and horizon == 720:
        return (FRETS_RELEASE_SEEDS[dataset], 30, 64)
    if backbone == "TimeMixer":
        # Match the official long-term forecasting recipes: 10 epochs for
        # the four ETT datasets and 20 for Exchange/Weather.
        epochs, batch = (10, 128) if dataset.startswith("ETT") else (20, 128)
        return (0, epochs, batch)
    epochs, batch = TRAINING[backbone]
    return (0, epochs, batch)

def metric(p, y, c, prefix):
    e=np.asarray(p,np.float64)+np.asarray(c,np.float64)-np.asarray(y,np.float64)
    return {"mse":float(np.mean(e*e)),"mae":float(np.mean(np.abs(e))),"suffix_mse":float(np.mean(e[:,prefix:]**2))}

def orth(g,l,prefix,beta):
    # remove the projection of Global onto the Local suffix direction
    out=np.zeros_like(g,dtype=np.float64); gs=np.asarray(g[:,prefix:],np.float64); ls=np.asarray(l[:,prefix:],np.float64)
    den=np.sum(ls*ls,axis=(1,2),keepdims=True)+1e-8
    innov=gs-np.sum(gs*ls,axis=(1,2),keepdims=True)/den*ls
    out[:,prefix:]=ls+beta*innov
    return out

def global_model(train, val, h):
    ptr,xtr,ytr,_=train; pv,xv,yv,_=val
    rrtr=ge.residual_records(ptr,ytr); rrval=ge.residual_records(pv,yv)
    btr,ltr=ge.causal_multiscale(rrtr,np.empty((0,ptr.shape[-1],4)),h)
    bval,lval=ge.causal_multiscale(rrval,rrtr,h)
    ftr=ge.make_features(ge.current_features(ptr,xtr),btr,ltr,"MSRegime-LR")
    fval=ge.make_features(ge.current_features(pv,xv),bval,lval,"MSRegime-LR")
    target=np.asarray(ge.dct(ytr-ptr,axis=1,norm='ortho').transpose(0,2,1))
    stats=ge.fit_stats(ftr,target); candidates=[]
    for rank in [r for r in ge.RANKS if r<=h]:
      for ridge in ge.RIDGES:
        model=ge.solve(stats,ridge,rank); corr=ge.correction(model,fval,h)
        e=np.asarray(pv)+corr-yv; candidates.append((float(np.mean(e*e)),model))
    return min(candidates,key=lambda x:x[0])[1]

def run(ds, backbone, h, cache_dir, output_dir):
    seed,epochs,batch_size=training_config(backbone,ds,h)
    t0=time.perf_counter(); data={s:load(cache_dir, ds,h,s,backbone,seed,epochs,batch_size) for s in ('train','val','test')}
    tr,va,te=data['train'],data['val'],data['test']; prefix=h//2
    prior=loc.empirical_prior(np.asarray(tr[2])-np.asarray(tr[0]),modes=64)
    # fixed final Local setting: 64 modes, noise=10, half-prefix
    gain=loc.empirical_gain(prior,prefix,10.0)
    vl=fs.local_correction(va[0],va[2],prefix,gain,prior['scale']); tl=fs.local_correction(te[0],te[2],prefix,gain,prior['scale'])
    model=global_model(tr,va,h)
    # causal Global correction from mature residual histories
    def gc(split, carry):
      p,x,y,_=split; rr=ge.residual_records(p,y); bank,length=ge.causal_multiscale(rr,carry,h)
      feat=ge.make_features(ge.current_features(p,x),bank,length,'MSRegime-LR'); return ge.correction(model,feat,h),rr
    vg,rrv=gc(va,ge.residual_records(tr[0],tr[2])); tg,_=gc(te,np.concatenate([ge.residual_records(tr[0],tr[2]),rrv]))
    trials=[]
    cut=int(.6*len(va[0]))
    for beta in BETAS:
      c=orth(vg,vl,prefix,beta); trials.append((float(np.mean((va[0][:cut]+c[:cut]-va[2][:cut])**2)),float(beta)))
    beta=min(trials)[1]; pred=orth(tg,tl,prefix,beta)
    out={"dataset":ds,"backbone":backbone,"horizon":h,"training_seed":seed,"training_epochs":epochs,"training_batch_size":batch_size,
         "prefix":prefix,"beta":beta,"local_noise":10.0,
         "validation_mse":min(trials)[0],"test":metric(te[0],te[2],pred,prefix),"baseline":metric(te[0],te[2],np.zeros_like(te[0]),prefix),"seconds":time.perf_counter()-t0}
    path=output_dir; path.mkdir(parents=True,exist_ok=True)
    (path/f'{backbone}_{ds}_H{h}.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out),flush=True); return out

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate the fixed STEPS final grid from frozen forecast caches")
    parser.add_argument("--cache-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("results/final_method_grid"))
    parser.add_argument("--backbones", nargs="+", choices=BACKBONES, default=BACKBONES)
    parser.add_argument("--datasets", nargs="+", choices=DATASETS, default=DATASETS)
    parser.add_argument("--horizons", nargs="+", type=int, choices=HORIZONS, default=HORIZONS)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for backbone in args.backbones:
        for dataset in args.datasets:
            for horizon in args.horizons:
                path = args.output_dir / f"{backbone}_{dataset}_H{horizon}.json"
                if path.exists() and not args.overwrite:
                    records.append(json.loads(path.read_text()))
                else:
                    records.append(run(dataset, backbone, horizon, args.cache_dir, args.output_dir))
    (args.output_dir / "summary.json").write_text(json.dumps(records, indent=2) + "\n")


if __name__ == "__main__":
    main()
