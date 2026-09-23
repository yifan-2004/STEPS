# Paper results

Full-horizon test MSE, copied from the manuscript main tables. Lower is better. The complete set of 144 backbone/dataset/horizon entries is also in [`paper_results.csv`](paper_results.csv).

| Backbone | Baseline mean | STEPS mean | Relative change |
|:--|--:|--:|--:|
| DLinear | 0.3716 | 0.2794 | -24.8% |
| OLS | 0.3661 | 0.2753 | -24.8% |
| PatchTST | 0.3677 | 0.2809 | -23.6% |
| iTransformer | 0.3762 | 0.2833 | -24.7% |
| FreTS | 0.3634 | 0.2758 | -24.1% |
| TimeMixer | — | 0.2831 | — |

Means are unweighted arithmetic means of the 24 dataset–horizon cells for each backbone; the relative change uses the ratio of those means. These summaries are derived from the rounded values printed in the manuscript, so they should not be treated as higher-precision measurements. The manuscript has no TimeMixer baseline values in its comparison table, so no baseline mean or relative change is shown.

## Full paper tables

### iTransformer

| Dataset | H=96 | H=192 | H=336 | H=720 |
|:--|--:|--:|--:|--:|
| ETTh1 | .3928 (.4507) | .4487 (.5078) | .4955 (.5658) | .5836 (.7038) |
| ETTh2 | .1978 (.2577) | .2368 (.3161) | .2730 (.3545) | .3119 (.4276) |
| ETTm1 | .3384 (.3823) | .3615 (.4423) | .4187 (.5093) | .4873 (.6065) |
| ETTm2 | .1342 (.1647) | .1663 (.2209) | .2041 (.2727) | .2466 (.3451) |
| Exchange | .0471 (.0882) | .0890 (.1811) | .1608 (.3428) | .4116 (.8540) |
| Weather | .1355 (.1755) | .1746 (.2232) | .2098 (.2800) | .2734 (.3571) |

### PatchTST

| Dataset | H=96 | H=192 | H=336 | H=720 |
|:--|--:|--:|--:|--:|
| ETTh1 | .3812 (.4312) | .4358 (.4955) | .4848 (.5559) | .5810 (.7117) |
| ETTh2 | .1933 (.2362) | .2236 (.2826) | .2501 (.3199) | .3005 (.4264) |
| ETTm1 | .3498 (.4024) | .3670 (.4512) | .4130 (.5081) | .4712 (.5629) |
| ETTm2 | .1299 (.1584) | .1583 (.2059) | .1897 (.2458) | .2434 (.3268) |
| Exchange | .0429 (.0867) | .0858 (.1877) | .1517 (.3389) | .4372 (.8648) |
| Weather | .1523 (.1742) | .1907 (.2195) | .2212 (.2766) | .2862 (.3544) |

### DLinear

| Dataset | H=96 | H=192 | H=336 | H=720 |
|:--|--:|--:|--:|--:|
| ETTh1 | .4054 (.4695) | .4588 (.5213) | .4991 (.5659) | .5812 (.7117) |
| ETTh2 | .1845 (.2323) | .2225 (.2862) | .2554 (.3252) | .2978 (.4087) |
| ETTm1 | .3293 (.3715) | .3564 (.4438) | .4137 (.5183) | .4848 (.5929) |
| ETTm2 | .1322 (.1598) | .1546 (.1930) | .1835 (.2324) | .2285 (.3062) |
| Exchange | .0475 (.0913) | .0892 (.1827) | .1559 (.3277) | .3939 (.8873) |
| Weather | .1491 (.1954) | .1876 (.2403) | .2171 (.2918) | .2765 (.3643) |

### OLS

| Dataset | H=96 | H=192 | H=336 | H=720 |
|:--|--:|--:|--:|--:|
| ETTh1 | .3902 (.4511) | .4432 (.5046) | .4843 (.5510) | .5688 (.6997) |
| ETTh2 | .1836 (.2306) | .2207 (.2839) | .2552 (.3258) | .2960 (.4162) |
| ETTm1 | .3287 (.3710) | .3562 (.4439) | .4133 (.5182) | .4844 (.5922) |
| ETTm2 | .1325 (.1602) | .1547 (.1936) | .1837 (.2331) | .2279 (.3066) |
| Exchange | .0431 (.0814) | .0835 (.1727) | .1483 (.3226) | .3799 (.8366) |
| Weather | .1489 (.1957) | .1874 (.2404) | .2170 (.2921) | .2763 (.3644) |

### FreTS

| Dataset | H=96 | H=192 | H=336 | H=720 |
|:--|--:|--:|--:|--:|
| ETTh1 | .3976 (.4462) | .4445 (.5022) | .4888 (.5544) | .5857 (.7182) |
| ETTh2 | .1913 (.2384) | .2271 (.2866) | .2608 (.3317) | .3004 (.4119) |
| ETTm1 | .3295 (.3675) | .3542 (.4325) | .4091 (.5005) | .4707 (.5704) |
| ETTm2 | .1313 (.1581) | .1553 (.1923) | .1842 (.2320) | .2275 (.3012) |
| Exchange | .0434 (.0828) | .0838 (.1734) | .1489 (.3240) | .3747 (.8368) |
| Weather | .1436 (.1856) | .1815 (.2310) | .2139 (.2843) | .2708 (.3599) |

### TimeMixer

| Dataset | H=96 | H=192 | H=336 | H=720 |
|:--|--:|--:|--:|--:|
| ETTh1 | .3928 (-) | .4487 (-) | .4921 (-) | .5783 (-) |
| ETTh2 | .1871 (-) | .2253 (-) | .2586 (-) | .3000 (-) |
| ETTm1 | .3452 (-) | .3656 (-) | .4162 (-) | .4777 (-) |
| ETTm2 | .1289 (-) | .1525 (-) | .1811 (-) | .2270 (-) |
| Exchange | .0436 (-) | .0853 (-) | .1518 (-) | .4001 (-) |
| Weather | .1333 (-) | .1686 (-) | .2015 (-) | .4328 (-) |

Each cell is **STEPS (frozen backbone)**. This transcription contains only the manuscript’s Baseline and Ours columns; other comparisons remain in the paper.
