import numpy as np, pandas as pd, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
S='/tmp/claude-1000/-home-nuttidalab-Documents-structuring-contexts/209c61e2-8bb9-4a44-b711-466fcb517e63/scratchpad'
pp='../../outputs/processed_data/pseudopop'
beh=pd.read_csv('../../data/psychopy/all_beh_trials_df.csv'); beh=beh[beh.subj==12].sort_values('trial_key').reset_index(drop=True)
FR=np.load(f'{pp}/stim/trial_mean_FRs.npy',allow_pickle=True)   # (240, 57) all neurons
conds=['curv_comp','baseline','flat_comp']; thr=dict(zip(conds,[-.2,0,.2])); edges=np.linspace(-.4,.4,11)
rng=np.random.default_rng(0)
cmap=plt.cm.RdBu_r.copy(); cmap.set_bad('black')

def bucket_means(Z, stims, mask):
    bins=pd.cut(stims[mask], bins=edges)
    return np.array([Z[mask][bins==c].mean(axis=0) if (bins==c).any() else np.full(Z.shape[1],np.nan) for c in bins.categories]).T

fig,axs=plt.subplots(3,4,figsize=(20,14)); plt.suptitle('All 57 neurons, z-scored within context. Cols: as-is | shuffled stim labels | split-half (sort on odd trials, show even) | split-half shuffled',y=1.0)
for i,cond in enumerate(conds):
    ids=beh.index[beh.condition==cond].values; stims=beh.loc[ids,'true_stim'].values
    X=FR[ids]; Z=(X-X.mean(0))/X.std(0)
    stims_shuf=rng.permutation(stims)
    allmask=np.ones(len(ids),bool); odd=np.arange(len(ids))%2==1; even=~odd
    panels=[('as-is: sort by peak (all trials), show all', bucket_means(Z,stims,allmask), bucket_means(Z,stims,allmask)),
            ('SHUFFLED stim labels, same sort', bucket_means(Z,stims_shuf,allmask), bucket_means(Z,stims_shuf,allmask)),
            ('split-half: sort on odd trials, show even', bucket_means(Z,stims,odd), bucket_means(Z,stims,even)),
            ('split-half, SHUFFLED labels', bucket_means(Z,stims_shuf,odd), bucket_means(Z,stims_shuf,even))]
    for j,(title,sort_heat,show_heat) in enumerate(panels):
        order=np.argsort(np.nanargmax(sort_heat,axis=1)); heat=show_heat[order]
        a=np.nanmax(np.abs(heat)); im=axs[i,j].imshow(heat,aspect='auto',cmap=cmap,vmin=-a,vmax=a,extent=[edges[0],edges[-1],heat.shape[0],0])
        axs[i,j].axvline(thr[cond],color='k',ls='--'); axs[i,j].set(title=f'{cond}\n{title}',xlabel='stim',ylabel='neuron (sorted)')
plt.tight_layout(); plt.savefig(f'{S}/heatmap_check.png',dpi=80)

# quantitative: per neuron x context, class effect = mean z(above boundary) - mean z(below); compare to shuffle null
print('per-neuron class effect |d| (mean z above - below boundary), real vs label-shuffled null (1000 shuffles), all 57 neurons:')
for cond in conds:
    ids=beh.index[beh.condition==cond].values; stims=beh.loc[ids,'true_stim'].values; y=stims>thr[cond]
    X=FR[ids]; Z=(X-X.mean(0))/X.std(0)
    d=Z[y].mean(0)-Z[~y].mean(0)
    null=np.array([ (lambda yp: Z[yp].mean(0)-Z[~yp].mean(0))(rng.permutation(y)) for _ in range(1000)])
    print(f'  {cond:10s}: real mean|d|={np.abs(d).mean():.3f}, null mean|d|={np.abs(null).mean():.3f} (95th pct of null means {np.percentile(np.abs(null).mean(1),95):.3f}); '
          f'neurons with |d| > null 97.5th pct: {(np.abs(d) > np.percentile(np.abs(null),97.5,axis=0)).sum()}/57 (expect ~1.4 by chance); max |d|={np.abs(d).max():.2f}')
