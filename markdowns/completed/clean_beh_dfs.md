# Clean beh_dfs plan (started 2026-09-04; items 1-4 EXECUTED 2026-09-04, item 5 EXECUTED 2026-09-05)

Running plan for cleaning up the behavioral dataframes / beh1–beh2 pipeline. Items accumulate here; execute all together once the list is settled.

## Executed 2026-09-04

Items 1-3 applied. Master csv is now `data/psychopy/all_beh_trials_df.csv` (name per beh1 markdown); old `all_subjs*.csv` all moved to `data/psychopy/arch/`. Readers updated: beh2, neur3, neur4, neur5, quick_viz. Verified: new csv identical to old modulo renames (157 shared cols equal; valence_stim/boundary/resp byte-identical; valence_direction redefined -- old col was v2's native valence sign, NaN for patients, unused downstream). Additions: `eligibility` (patients only), `valence_numeric` (rew=1/pen=0, replaces v2's valence-sign col under unambiguous name). beh1's markdown notes deleted per their own instruction. beh2 review still pending (its markdown mentions thresh-naming: true_thresh, stim/resp_thresh_aligned).

## Items

### 1. Merge patient eligibility into all_subjs.csv (beh1)

Source: `data/patient_documentation.csv` (uploaded 2026-09-04) — per-patient records with cols `subj, sess_type, notes, num_neurons, implantation date, expt date, age, sex, handedness, seizure location`. The `notes` col holds data eligibility: `LFP only` / `behavior only` / `neuronal`.

- In beh1_preproc_v2, cleaning section: after `df_subjs` is finalized, before `to_csv('all_subjs.csv')` — load patient_documentation, keep `subj` + `notes`, rename `notes` → `eligibility`, left-merge onto `df_subjs` on `subj`.
- Rename is also required to avoid collision: trial-level psychopy data already has a `notes` column.
- ID format differs: patient_documentation uses `202509`, beh csvs use `9` → convert with `subj - 202500` before merging.
- Verify: every subj non-null `eligibility`; row count unchanged (240/subj).
- Then quick_viz: read `all_subjs.csv`, `subjs_df` cols → `subjID, sess_type, eligibility`.

Open question: merge only `eligibility`, or also other patient_documentation cols (age, sex, num_neurons, …)?

### 2. Retire stale csvs; all_subjs.csv becomes beh1's only output

- Move `data/psychopy/all_subjs_clean.csv` (stale, Mar 23; written only by arch notebooks) and `all_subjs_v2.csv` (stale, May 4; only referenced as a read in arch/beh_valence) → `data/psychopy/arch/`. Point remaining readers (quick_viz) at `all_subjs.csv`.
- Drop the `all_subjs_v1.csv` write in beh1 (nothing reads it; raw files are on disk and beh1 reruns fast) and move the existing file to arch too. `all_subjs.csv` is then the single beh1 output.

### 3. beh1 markdown-driven restructure (renames + reorder)

Per the new "Logic flow" markdown (2026-09-04). No logic changes — renames + cell reordering only.

Renames (downstream-safety grep-verified across `code/python/`):

- `direction` → `shape_direction`; `true_div` → `true_thresh`. Old section creates them for df_v1 under the new names. v2 raw files already carry them under old names → one rename line for df_v2 under the (currently empty) New section. Rename-cols cell still maps `true_thresh` → `true_boundary`, so beh2 untouched. No reader of all_subjs.csv uses `direction` (neur6/utils.py hits are substrings; task_design/simulation1 use design csvs).
- `valence_flipped` → `valence_direction` (±1; 1 = curv=pen & flat=rew). Replaces BOTH current cols: cell 6's session-level ±1 and cell 14's trial-level boolean (current True == new −1). v1: create per-trial from shape/valence, assert sess A/C == 1, B/D == −1. v2 files already have it with matching polarity (verified). Flips become `np.where(valence_direction == -1, -x, x)`. Harmonizes with task_design_v2/simulation1 naming.

Reorder combined section to markdown order: rename cols → rename subjects → target_resp/true_resp (type-cast first) → valence flips → boundary-aligned + ranks → sanity checks (error trials, timings, outcomes + save).

- Rename-cols cell: drop true_resp/target_resp from display (not yet created) and drop its no-op mapping entries.
- Alignment-fix logic untouched: `trial_chronological_idx` + final sort `['subj','trial_key']` (neur3 depends on it).

Verify: rerun beh1 headless; diff new vs current all_subjs.csv under old→new name map (values identical, names only). Readers (beh2, neur3, neur4, neur5) use none of the renamed names. Then delete the two "delete this note" sub-bullets from the markdown.

Open: final csv name stays `true_boundary` (thresh is intermediate only) unless user says otherwise.

### 4. Rename beh_df-family vars -> beh_trials_df (EXECUTED, commit 0e2c544)

`all_beh_df` -> `all_beh_trials_df`, `pt_beh_df(s)` -> `pt_beh_trials_df(s)`, `cond_beh_df` -> `cond_beh_trials_df`, bare `beh_df` -> `beh_trials_df`, across neur3/4/5 + neur_utils.py. NOT renamed: simulation1's `beh_df` (design-csv family), beh2's markdown mention (beh2 review).

### 5. beh2 review: context + thresh naming, beh2 rebuilt per its markdown (EXECUTED 2026-09-05)

- csv (beh1): `condition` -> `context` with values `C1/C2/C3` (was psychopy's `curv_comp/baseline/flat_comp`); `true_boundary/target_boundary/valence_boundary` -> `true_thresh/target_thresh/valence_thresh`; `stim/resp_boundary_aligned` -> `stim/resp_thresh_aligned`. Verified new csv == old under the name map (values identical; 680 trials per context; C1/C2/C3 <-> -.2/0/.2).
- Readers: neur4 (`conds = ['C1','C2','C3']`, parallel `cntxts` list dropped, derived neuron x context table uses `context`), neur5 (private remap dropped, `stim_thresh_aligned`), sim1/sim2 (labels `C1/C2/C3`; design-csv lineage keeps its `condition` column; `outputs/simulations/inference_df.csv` labels remapped in place, sim1 NOT rerun since it trains 30 nets). task_design_v2 untouched: psychopy reads `curv_comp/...`.
- beh2 rebuilt to its Logic-flow markdown: quick viz (one row per patient x context) -> classification (per-context violin of per-patient accuracies + mean ± SEM; 1x3 <thresh/>thresh violins) -> stim vs resp (1x4 distributions + weights violin; 1x2 original / thresh-aligned). Dropped: raw/aligned toggle plot, between-context MSE + paired t-test, poster savefigs, `subj > 2` pilot filter (pilots no longer in csv). All 9 patients; invalid/incomplete trials kept (user decision: that is what accuracy measures). Violins everywhere for across-patient summaries (user asked for one choice for all plots).
- Reruns: beh1, beh2, neur4, neur5, sim2 headless. neur4 wrote new `pt2512`-style pngs under `outputs/figs/single_units/`; the pre-rename `pt12`-style pngs there are stale duplicates (not deleted).

## Execution order (once list is settled)

1. Edit beh1_preproc_v2 → rerun headless → regenerate `all_subjs.csv`.
2. Edit beh2 / quick_viz readers as needed.
3. Verify checks per item; commit together.
