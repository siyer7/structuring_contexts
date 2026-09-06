# Neural preprocessing prompt (started 2026-09-05)

Reusable checklist for every new neuronal patient download: raw -> per-channel mats -> notch600 -> OSort. Paste the "Prompt" block to Claude, fill in the patient IDs; Claude runs the steps, verifies each, and appends to the run log at the bottom.

## Prompt

> New neuronal patient(s) downloaded: `<IDs>`. Uploads are in `<base-dir folders>`. Run `notes/neur_preproc.md` steps 0-6 for them; verify each step; append to the run log; commit code edits (data is gitignored).

## Per-patient knobs (the only lines that change)

- `code/matlab/NSX2Mat_formatted.m` (true Blackrock `.ns6`) or `code/matlab/NSX2Mat_fromDI.m` (openNSx export saved as `.mat`): `subj = '<ID>'`
- `code/python/neur1_preproc.ipynb`: `patient = <4-digit ID>`; run headless from `code/python/` with the `NN_env` kernel
- `code/matlab/sorting.m`: `subj = '<ID>'`; alignment stays align-min (`filesAlignMax = []; filesAlignMin = filesToProcess`), threshold 5, `rawFileVersion = 5`

## Steps

0. **Folders.** `data/<ID>/{raw,records,osort_mat}` like existing patients. Uploads -> `raw/` (channel maps / electrode files -> `records/`). Remove the upload folder from the base dir. Verify: base dir clean; `raw/` holds the recording files.
1. **What kind of raw file is it?** `head -c 16 <file>`: `BRSMPGRP` (.ns6) / `BREVENTS` (.nev) = true Blackrock -> step 2a. `MATLAB 7.3 MAT-file` = openNSx export saved as .mat (DI's 202604/202605 uploads) -> rename `*_DI.ns6 -> *_DI_ns6.mat`, `*_DI.nev -> *_DI_nev.mat` so the extension is honest, then step 2b.
2. **Size check.** Expect 32 ch @ 30 kHz; duration ~= blocks/6 x ~28-33 min per `data/patient_documentation.csv`. Duration from file size: n_samples = (size - header) / bytes_per_sample, where spec 3.0 `Hub1-*.ns6` (2025-18 on) store ONE sample per 13-byte packet -> 77 bytes/sample (~0.139 GB/min), while spec 2.3 (202512) is 64 bytes/sample (~0.115 GB/min). For .mat exports read `NSX.MetaTags.DataDurationSec`. After step 2a/b the truth is `numel(data)` in any BL*.mat. Flag anything off.
   - 2a. `NSX2Mat_formatted.m` (openNSx per channel, uV) -> `osort_mat/nsx2mat/BL<chanID>.mat` x32, v7.3, ~200 MB each for a full session (~8 min).
   - 2b. `NSX2Mat_fromDI.m` (split `NSX.Data`, x MaxAnalog/MaxDigi = 0.25 uV/bit) -> identical outputs.
   - Verify: 32 files, IDs 193-224 (97-128 for 202512), size proportional to duration.
3. **Stale outputs.** Delete any `figs_max/`, `sorted_mats_max/`, `figs_notch/` etc. from earlier experiments before re-sorting (202603 had `_max` from a 5-channel re-sort).
4. **neur1_preproc** -> `osort_mat/nsx2mat_notch600/BL<chanID>.mat` x32 (v5, `data` 1xT double = 8 bytes/sample, notch 60..600 Hz Q=60). ~4 min per full session.
   - Verify: 32 files, each ~8 x n_samples bytes.
5. **sorting.m** -> `sorted_mats_notch600/5/A<chanID>_sorted_new.mat` x32 + `figs_notch600/5/` (>= 8 pngs/channel: 4 RAW, PCAALL, WAVES, CL_ALL, CL_*). ~20 min per full session.
   - Verify: 32 sorted mats; every channel has figs.
6. **Log + commit.** Append run log row(s) below; commit script/notebook edits.

## Gotchas

- Uploads named `.ns6`/`.nev` are not necessarily Blackrock files: DI's 2026 exports were MATLAB `.mat` (openNSx 7.4.6.2 output, 32 selected channels). openNSx cannot read them -> `NSX2Mat_fromDI.m`. Ask for true raw files when possible.
- neur1_preproc used to parse the patient from the path with `split('2025')` -> broke for 2026 IDs; now globs one patient's `nsx2mat/` directly (fixed 2026-09-05).
- sorting.m had a leftover 5-channel `chans_to_resort` filter and `pathRaw = nsx2mat/` (not notch600) until 2026-09-05; both fixed. Alignment: 2025 sorted_mats used align-min; 202603's `_max` folders were a one-off align-max experiment (deleted).
- 202601 raw is only 8.0 min (14.38M samples) for "4/6 blocks" (expected ~19-22 min) -> check with recording notes.
- Headless nbconvert must pin `--ExecutePreprocessor.kernel_name=nn_env`: NN_env has no nbconvert, so `jupyter nbconvert` falls through to base miniconda's, whose default `python3` kernel lacks neo/h5py.
- Downstream (not part of this prompt): neur2 reads `sorted_mats/5/` (no `_notch600` suffix); neur3 globs `raw/*.nev` via BlackrockIO, which a `.mat` export breaks.

## Run log

| date | patient | raw kind | duration | blocks (csv) | nsx2mat | notch600 | sorted | notes |
|---|---|---|---|---|---|---|---|---|
| 2026-09-05 | 202601 | true .ns6 (spec 3.0) | 8.0 min | 4/6 | 32 (NSX2Mat_formatted, 2 min) | 32 (2 min) | 32 mats / 273 figs; 62 clusters on 30 ch; 50.7k spikes (14 min) | duration ~1.5 blocks, not 4 -> check recording notes |
| 2026-09-05 | 202603 | true .ns6 (spec 3.0) | 33.0 min | ? | 32 (pre-existing, 2026-07-30) | 32 (5 min) | 32 / 266 figs; 57 clusters on 32 ch; 144.7k spikes (26 min) | deleted stale figs_max/, sorted_mats_max/ |
| 2026-09-05 | 202604 | openNSx export .mat (DI) | 16.2 min | 3/6 | 32 (NSX2Mat_fromDI, 3 min) | 32 (3 min) | 32 / 240 figs; 44 clusters on 21 ch; 34.0k spikes (14 min) | raw renamed *_DI_ns6.mat / *_DI_nev.mat |
| 2026-09-05 | 202605 | openNSx export .mat (DI) | 32.2 min | ? | 32 (NSX2Mat_fromDI, 6 min) | 32 (6 min) | 32 / 348 figs; 112 clusters on 30 ch; 82.6k spikes (26 min) | raw renamed as above |

Sorting times above are with 3-4 MATLAB instances running concurrently (~1 min/channel); alone ~40 s/channel. Reference durations of the 2025 patients from their sample counts: 202512 27.2, 202518 27.8, 202521 ~29.6 (est), 202522 28.1 min.

Headless run recipe (2026-09-05): MATLAB `cd code/matlab && matlab -batch "run('<script>.m')"` after setting `subj`; neur1 `cd code/python && jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 --ExecutePreprocessor.kernel_name=nn_env neur1_preproc.ipynb`. The `Error in startup (line 11)` MATLAB prints at start is `~/startup.m` cd-ing to a missing dir; harmless.
