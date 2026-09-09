# neur_analyses — run neur2–5 post-QC

Goal: QC is done, so run the pipeline end to end. Of the 4 26** patients, only 2605 is included for now (issues with 2601/2603/2604).

## steps

- [ ] neur2 for pt2605: sections 2–5 (section 1 / preQC already done). Needs `QC_pt2605.csv`; suffix `_notch600`. Output: `outputs/processed_data/202605/neurs_df.parquet`.
- [ ] check `all_beh_trials_df.csv` has 2605 trials before building the pseudopop.
- [ ] neur3: rebuild pseudopop arrays with 2605 added (`outputs/processed_data/pseudopop/{epoch}/...` + `all_neur_df.parquet`).
- [ ] neur4: encoding figs + Kruskal-Wallis. Figures skip if png exists — delete `outputs/figs/single_units/*` first to regenerate with 2605.
- [ ] neur5: population PCA / decoding / CCD. Headline stats via `markdowns/completed/neur5_headline_stats.py` to compare against `stats_fixed.json`.

## how to run

Headless, from `code/python`: `MPLBACKEND=Agg jupyter nbconvert --to notebook --execute --ExecutePreprocessor.kernel_name=nn_env <nb>.ipynb --output <scratch>/x.ipynb`, then copy back over the source.
