# neur5 headline stats straight from the pseudopop arrays + csv (mirrors neur5 cells: load, stim_by_neur, decode, pooled, CCD, stim axis)
import sys, json, numpy as np, pandas as pd
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, permutation_test_score
from scipy.stats import pearsonr

root, out_json = sys.argv[1], sys.argv[2]
pseudopop_dir, conds, epoch = f'{root}/outputs/processed_data/pseudopop', ['C1', 'C2', 'C3'], 'stim'

all_beh_trials_df = pd.read_csv(f'{root}/data/psychopy/all_beh_trials_df.csv'); patients = sorted(all_beh_trials_df.loc[all_beh_trials_df['subj'] > 11, 'subj'].unique())
beh_trials_df = all_beh_trials_df.loc[all_beh_trials_df['subj'] == patients[0]].sort_values('trial_key').reset_index(drop=True)
beh_trials_df['condition'] = beh_trials_df['condition'].replace({'curv_comp': 'C1', 'flat_comp': 'C3', 'baseline': 'C2'})
meanFRs = np.load(f'{pseudopop_dir}/{epoch}/trial_mean_FRs.npy', allow_pickle=True)
meanFRs = meanFRs - np.load(f'{pseudopop_dir}/baseline/trial_mean_FRs.npy', allow_pickle=True).mean(axis=0, keepdims=True)

stim_by_neur, cond2stims, cond_decode_X, cond_decode_y = {}, {}, {}, {}
for cond in conds:
    cond_mask = (beh_trials_df['condition'] == cond).values
    df_tmp = pd.DataFrame(meanFRs[cond_mask]); df_tmp['true_stim'] = beh_trials_df.loc[cond_mask, 'true_stim'].round(2).values
    grouped = df_tmp.groupby('true_stim').mean(); stim_by_neur[cond], cond2stims[cond] = grouped.values, grouped.index.values
    cond_decode_X[cond] = meanFRs[cond_mask]; cond_decode_y[cond] = (beh_trials_df.loc[cond_mask, 'stim_boundary_aligned'] > 0).astype(int).values

stats_out = {}
clf = LogisticRegression(penalty=None, max_iter=1000); cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
for cond in conds:
    score, _, pval = permutation_test_score(clf, cond_decode_X[cond], cond_decode_y[cond], cv=cv, scoring='accuracy', n_permutations=1000, random_state=0, n_jobs=-1)
    stats_out[f'decode_{cond}'] = {'acc': round(score, 4), 'p': round(pval, 4)}
X_pooled = np.vstack([cond_decode_X[c] for c in conds]); y_pooled = np.concatenate([cond_decode_y[c] for c in conds])
score, _, pval = permutation_test_score(clf, X_pooled, y_pooled, cv=cv, scoring='accuracy', n_permutations=1000, random_state=0, n_jobs=-1)
stats_out['decode_pooled'] = {'acc': round(score, 4), 'p': round(pval, 4)}

ccd = np.zeros((3, 3))
for i, ctr in enumerate(conds):
    for j, cte in enumerate(conds):
        ccd[i, j] = LogisticRegression(penalty=None, max_iter=1000).fit(cond_decode_X[ctr], cond_decode_y[ctr]).score(cond_decode_X[cte], cond_decode_y[cte])
stats_out['ccd'] = np.round(ccd, 4).tolist(); stats_out['ccd_offdiag_mean'] = round(ccd[~np.eye(3, dtype=bool)].mean(), 4)

for cond in conds:
    stims, FRs = np.array(cond2stims[cond]), stim_by_neur[cond]
    pcs = PCA(n_components=5).fit_transform(FRs); corrs = [np.corrcoef(stims, pcs[:, k])[0, 1] for k in range(5)]
    best = int(np.argmax(np.abs(corrs))); r, p = pearsonr(stims, np.sign(corrs[best]) * pcs[:, best])
    stats_out[f'stim_axis_{cond}'] = {'best_pc': best + 1, 'r': round(r, 4), 'p': round(p, 4)}

json.dump(stats_out, open(out_json, 'w'), indent=1); print(json.dumps(stats_out, indent=1))
