# Evaluation protocol

This document describes the released final adapter grid and its cache contract. The [implementation](../steps/runner.py) is the executable source of truth.

## Scope and ordering

The grid has six frozen backbones (`DLinear`, `OLS`, `PatchTST`, `iTransformer`, `FreTS`, `TimeMixer`), six datasets (`ETTh1`, `ETTh2`, `ETTm1`, `ETTm2`, `exchange_rate`, `weather`), and four forecast horizons (`96`, `192`, `336`, `720`). Each split contains consecutive, chronologically ordered origins at unit stride. Backbone training is separate from this repository; the required seed, epoch, and batch-size identifiers used to resolve each cache folder are recorded in `steps/runner.py` and `configs/final_grid.json`.

For each origin, `prediction.npy` is the frozen backbone output. `series.npy` yields the input history and the ground-truth forecast window via sliding windows. Arrays must be in the same normalization and channel order used by the backbone. The cache reader never loads checkpoint files.

## Available information at a revision

The observed prefix is `a = H/2`. The local correction reads the current forecast and only the first `a` ground-truth values. It changes the suffix and leaves the prefix forecast as-is. The global correction uses the current forecast and input history plus residual records from earlier, fully mature forecast windows. A residual record from origin `j` is eligible for origin `i` only after all `H` labels in `j`'s horizon are available (`j + H <= i` under the origin convention in the code). Current unobserved suffix labels must not affect any correction.

Within a split, chronological records are carried forward. Training records are available to validation; training and validation records are available to test. Dataset split boundaries and the generation of frozen forecasts are the responsibility of the supplied cache.

## Fixed STEPS settings

- Local: empirical training residual covariance in the first 64 orthonormal DCT modes, white residual term, observation-noise multiplier `10.0`.
- Global: four low-frequency modes per mature residual record; history widths `[4, 12, 24, 48, 96, 192, 336, 720, 1080]`; `MSRegime-LR` features; output DCT rank in `[8, 16, 32, 64]`; ridge in `[0.001, 0.01, 0.1, 1, 10, 100]`.
- Fusion: the local suffix correction plus `beta` times the global suffix innovation orthogonal to the local correction. `beta` is selected from 41 evenly spaced values in `[-0.5, 1.5]`.

The global rank and ridge minimize full-horizon validation MSE. The fusion coefficient minimizes full-horizon MSE on the first 60% of validation origins. The chosen settings are then applied once to test. The JSON output reports full-horizon MSE/MAE and suffix MSE; the paper tables use the full-horizon MSE.

## Cache name convention

`{backbone}_{dataset}_H{horizon}_seed{seed}_ep{epochs}_b{batch_size}/{split}/` where `split` is `train`, `val`, or `test`. Default seed `0`, 30 epochs and batch 256 apply to DLinear, OLS, PatchTST, iTransformer, and FreTS except FreTS at H=720. FreTS H=720 uses 30 epochs, batch 64, and dataset-specific seeds: ETTh1=1, ETTh2=2, ETTm1=2, ETTm2=0, exchange_rate=0, weather=2. TimeMixer uses seed 0, batch 128, and 10 epochs for ETT or 20 for exchange_rate/weather. These are cache identifiers reflecting the final local protocol; changing them requires regenerating the corresponding frozen forecasts.

## Interpretation of paper results

`docs/RESULTS.md` transcribes the manuscript's Baseline and Ours columns for all backbones. `docs/paper_tta_comparison.csv` separately transcribes the 120 cells for which the manuscript reports Baseline, TAFAS, PETSA, COSA-F, COSA-P, and STEPS together (five backbones, six datasets, four horizons). The published comparison methods are contextual references and may use a different adaptation or information protocol. MICN and TimeMixer are excluded from that cross-method file because comparison values are not reported for them. The README summary and plot are descriptive averages of rounded paper entries, not new measurements. To compare a new run, use the generated per-cell JSON rather than relying on rounded paper numbers.
