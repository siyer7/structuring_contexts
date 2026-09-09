# Trial alignment fix (2026-09-03)

Tags: `pre-alignment-fix` (state before) → `alignment-fix` (state after). Old figures + stats archived in `outputs/archive/pre_alignment_fix/`.

## What was wrong

`data/psychopy/all_subjs.csv` rows within a subject were in no meaningful order — leftover of an unstable `sort_values(by=['subj'])` at the end of beh1. neur3 paired csv row *i* with neural trigger trial *i*, so nearly every trial carried the wrong condition / stimulus label.

Two orders matter, and neither was the csv order:

- **`trial_key`** — the design index (0–239), identical trial set across all subjects. Equals `sort_values(['blockN', 'trials.thisIndex'])`.
- **`trial_chronological_idx`** — the order actually played (0–239 per subject). Equals `sort_values(['run', 'blocks.thisN', 'trials.thisN'])`. NOT `blockN`: PsychoPy shuffled block presentation (pt12/18/22 played blocks 1,3,2,4,5,6; pt21 played 1,2,3,5,4,6) and trials within a block.

## Evidence

Per-trial behavioral RT (`submit_resp.rt`) vs neural-trigger RT (task started → response submitted), pairing trials in each candidate order:

| pairing order | median \|ΔRT\| | trials within 50 ms |
|---|---|---|
| csv order (old) | 357–476 ms | 7–11 % |
| `trial_chronological_idx` | 23–24 ms | 100 % (all 4 patients) |
| `trial_key` | 320–442 ms | 7–15 % |

The chronological sort also matches the PsychoPy clock (`baseline.started`) exactly within each run.

## What changed

- **beh1**: adds `trial_chronological_idx`; csv written sorted by `['subj', 'trial_key']` (stable). All other columns identical to before. Paths fixed `results/` → `data/`.
- **neur3**: per patient, sort by `trial_chronological_idx` → pair with triggers → reorder spikes/FRs/table by `trial_key` (shared trial axis; played order differs across patients) → assert every patient's `trial_key` + `true_stim` sequence identical → stack. `trial_tables.pkl` no longer written.
- **neur4 / neur5**: trial tables come from `all_subjs.csv` sorted by `trial_key` (rows of the pseudopop are in that order). neur5's cross-patient assert enabled.

## Results, before → after (stim epoch, 57 neurons)

| stat | before (scrambled) | after (aligned) |
|---|---|---|
| decode C1 / C2 / C3 | 76.3 % (p=.001) / 75.0 % (p=.001) / 62.5 % (p=.047) | 47.5 % (p=.73) / 46.3 % (p=.77) / 51.3 % (p=.47) |
| decode pooled | 55.8 % (p=.07) | 44.6 % (p=.93) |
| CCD off-diag mean | 46.3 % | 50.2 % |
| stim-axis r C1 / C2 / C3 | .64 (p=.01) / .48 / — | .22 (p=.44) / .36 (p=.11) / .24 (p=.40) |
| single-unit KW, FDR-sig | 0/171 (min raw p .0071) | 0/171 (min raw p .0020) |

Why the old numbers looked good: scrambled labels are session-time-biased, and session time is decodable from FRs (drift). Full stats: `outputs/archive/pre_alignment_fix/stats_baseline.json` vs `stats_fixed.json`.

## How to revert / compare

```bash
git diff pre-alignment-fix alignment-fix -- code/python      # code changes only
git checkout pre-alignment-fix                                 # whole repo (code, csv, parquets, npy) as it was
git checkout main                                              # back
```
Old figures: `outputs/archive/pre_alignment_fix/figs/`, `.../decoding/`.
