# STEPS

**Test-time adaptation for multivariate time-series forecasting**

Research implementation accompanying *STEPS: A Temporal Smooth Error Propagation Solver on the Manifolds for Test-Time Adaptation in Time Series Forecasting*. This is a prepublication code release; no conference acceptance is claimed.

![STEPS method overview](assets/STEPS_method_overview.png)

STEPS revises a frozen backbone forecast after the first half of its horizon is observed. A local branch extends the observed prefix residual using a training-derived spectral prior. A global branch predicts smooth bias from mature historical residuals. The final suffix correction anchors to the local branch and adds the component of the global correction orthogonal to it.

## Results at a glance

The table compares STEPS with the forecasting TTA methods reported in the manuscript: TAFAS, PETSA, and the two COSA variants (COSA-F and COSA-P). It reports full-horizon test MSE averaged over the five backbones, six datasets, and four horizons for which all methods have entries (120 cells per method). Lower is better. These are means of the **rounded manuscript table entries**, not new measurements.

| Method | Mean test MSE ↓ | Change vs. frozen baseline |
|:--|--:|--:|
| Frozen backbone | 0.3690 | — |
| TAFAS | 0.3554 | −3.7% |
| PETSA | 0.3554 | −3.7% |
| COSA-F | 0.3086 | −16.4% |
| COSA-P | 0.3183 | −13.7% |
| STEPS | 0.2789 | −24.4% |

The line chart shows each method's mean MSE at each forecast horizon, averaging over the same five backbones and six datasets. These published comparison values are contextual references from the manuscript's supplied comparison table; their information and adaptation protocols may differ from STEPS, so the aggregate is descriptive rather than a matched-protocol claim. The comparison excludes MICN and TimeMixer because the manuscript does not report the other methods for those backbones. See the [full 120-cell method comparison](docs/paper_tta_comparison.csv), [complete STEPS/backbone paper table](docs/RESULTS.md), and [machine-readable STEPS transcription](docs/paper_results.csv).

![Mean test MSE by forecast horizon for STEPS and comparison methods](assets/paper_tta_comparison_by_horizon.png)

![Residual structure analysis from the manuscript](assets/residual_structure_evidence.png)

## Reproduce the adapter evaluation

This repository contains the **STEPS adapter, its fixed parameter search, the cache reader, and the evaluation protocol**. It contains no backbone weights, pretrained checkpoints, forecast caches, or raw datasets. You must supply frozen backbone predictions and the corresponding split series in the format below. This separation lets the adapter be evaluated without shipping model weights.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m steps.runner --cache-dir /path/to/frozen_cache \
  --backbones DLinear --datasets ETTh1 --horizons 96
```

Omit the backbone, dataset, and horizon filters to run all 144 cells. Per-cell JSON and `summary.json` are written to `results/final_method_grid/` unless `--output-dir` is given. The runner reuses existing results by default; pass `--overwrite` to rerun them.

For each cell, provide `train`, `val`, and `test` folders:

```text
frozen_cache/
  DLinear_ETTh1_H96_seed0_ep30_b256/
    train/{metadata.json,prediction.npy,series.npy}
    val/{metadata.json,prediction.npy,series.npy}
    test/{metadata.json,prediction.npy,series.npy}
```

`prediction.npy` has shape `(N, H, C)`. `series.npy` has shape `(N + lookback + H - 1 or longer, C)` and starts at the first input time point for that split. `metadata.json` must contain `{"lookback": <integer>}`. For origin `i`, the history is `series[i:i+lookback]` and the target is `series[i+lookback:i+lookback+H]`. Origins must be in chronological order, one time step apart. See [the full protocol](docs/PROTOCOL.md) and [fixed configuration](configs/final_grid.json).

## Repository layout

```text
steps/method.py       Final local and global correction operators
steps/cache.py        Frozen forecast cache reader
steps/runner.py       Validation selection and 144-cell evaluation
configs/              Fixed experiment parameters
docs/                 Protocol and manuscript result tables
assets/               Figures used in the manuscript
tests/                Synthetic protocol checks
```

## Citation

The accompanying manuscript is in preparation for conference submission. A bibliographic entry and preprint link will be added when public metadata is available; please cite the manuscript title above in the meantime.

## License

See [LICENSE](LICENSE).
