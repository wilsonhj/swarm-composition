| detector | L0 AUROC / R@5% | L1 AUROC / R@5% | L2 AUROC / R@5% | L3 AUROC / R@5% | L4 AUROC / R@5% |
|---|---|---|---|---|---|
| rules(incident signatures) | 1.00±0.00 / 1.00 | 1.00±0.00 / 1.00 | 0.50±0.00 / 0.00 | 0.50±0.00 / 0.00 | 0.50±0.00 / 0.00 |
| isolation_forest | 0.93±0.01 / 0.42 | 0.95±0.01 / 0.60 | 0.90±0.02 / 0.35 | 0.78±0.04 / 0.02 | 0.67±0.03 / 0.22 |
| reciprocity_graph | 0.98±0.03 / 0.90 | 0.98±0.03 / 0.90 | 0.97±0.04 / 0.80 | 0.95±0.02 / 0.47 | 0.52±0.02 / 0.15 |
| supervised(train L0) | 1.00±0.00 / 1.00 | 1.00±0.00 / 1.00 | 0.99±0.02 / 0.87 | 0.94±0.02 / 0.20 | 0.55±0.06 / 0.00 |
| supervised(leave-level-out) | 1.00±0.00 / 1.00 | 1.00±0.00 / 1.00 | 1.00±0.00 / 1.00 | 1.00±0.00 / 1.00 | 0.24±0.08 / 0.13 |

| level | covert bytes delivered / hour (mean) |
|---|---|
| L0 | 2470 |
| L1 | 6565 |
| L2 | 12848 |
| L3 | 1138 |
| L4 | 729 |

Top supervised(train L0) importances: mkcol_unfilled=0.43, name_nonstd=0.17, peer_fresh_read=0.15, rate_per_h=0.13, name_entropy=0.06, n_mutual=0.05
