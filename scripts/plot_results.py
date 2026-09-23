"""Regenerate the README figure from the rounded manuscript table entries."""
from __future__ import annotations
import csv
from collections import defaultdict
from pathlib import Path
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parents[1]
with (root / 'docs/paper_results.csv').open() as handle:
    rows = list(csv.DictReader(handle))
groups = defaultdict(list)
for row in rows:
    groups[row['backbone']].append(row)
names = ['DLinear', 'OLS', 'PatchTST', 'iTransformer', 'FreTS']
baseline = [sum(float(r['baseline_mse']) for r in groups[n]) / len(groups[n]) for n in names]
steps = [sum(float(r['steps_mse']) for r in groups[n]) / len(groups[n]) for n in names]

plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
fig, ax = plt.subplots(figsize=(8.8, 3.8), layout='constrained')
x = range(len(names))
ax.bar([v-0.18 for v in x], baseline, width=0.35, color='#A9B5C8', label='Frozen backbone')
ax.bar([v+0.18 for v in x], steps, width=0.35, color='#326B9A', label='STEPS')
ax.set_xticks(list(x), names)
ax.set_ylabel('Mean full-horizon test MSE ↓')
ax.set_ylim(0, 0.44)
ax.grid(axis='y', alpha=0.15)
ax.set_axisbelow(True)
ax.legend(frameon=False, ncol=2, loc='upper right')
fig.savefig(root / 'assets/paper_results_summary.png', dpi=180)
