# Goldbach RTX round 7

Limit: 150,000,000
Backend: cupy-rtx-fft
FFT seconds: 6.056
Zero count: 0

## Main Findings

- Weakest >=1000: 1112 with 16 pairs.
- Strongest: 145495350 with 1,335,187 pairs.
- Summatory pairs up to limit: 18,885,914,138,855.

## Short Interval Metrics

| threshold | good count | max gap | from | to | gap/(123 log^2 x) |
|---:|---:|---:|---:|---:|---:|
| 1 | 74999999 | 2 | 4 | 6 | 0.008461 |
| 20 | 74999624 | 24 | 300 | 324 | 0.005998 |
| 100 | 74996467 | 210 | 2310 | 2520 | 0.028462 |
| 1000 | 74933937 | 1680 | 39270 | 40950 | 0.122062 |
| 5000 | 74540863 | 4620 | 265650 | 270270 | 0.240778 |
| 10000 | 73959791 | 30030 | 570570 | 600600 | 1.389731 |
| 20000 | 72662797 | 54600 | 1291290 | 1345890 | 2.241962 |
| 50000 | 68263045 | 30030 | 3873870 | 3903900 | 1.060944 |
| 100000 | 60100872 | 180180 | 8378370 | 8558550 | 5.764497 |

## Progression Density

### mod 2310

Top/bottom density ratio: 3.5599

Top residues: 0 (2.7167), 840 (2.4453), 1890 (2.4453), 630 (2.4452), 1050 (2.4452), 210 (2.4452), 1260 (2.4451), 1680 (2.4450)

Bottom residues: 2042 (0.7632), 1322 (0.7633), 692 (0.7633), 398 (0.7633), 2162 (0.7633), 1742 (0.7634), 992 (0.7634), 908 (0.7634)

### mod 30030

Top/bottom density ratio: 3.8840

Top residues: 0 (2.9427), 2310 (2.6981), 23100 (2.6980), 9240 (2.6980), 6930 (2.6980), 20790 (2.6980), 25410 (2.6979), 18480 (2.6979)

Bottom residues: 14552 (0.7576), 29762 (0.7577), 9092 (0.7577), 13592 (0.7577), 6362 (0.7577), 17492 (0.7577), 3632 (0.7578), 15182 (0.7578)

## Direct Profiles

| n | pairs | audit | min gap | avg gap | min/avg | Chen D12 | D12/pairs |
|---:|---:|---|---:|---:|---:|---:|---:|
| 1112 | 16 | True | 6 | 35.68 | 0.168174 |  | 0.0000 |
| 1004 | 18 | True | 6 | 28.29 | 0.212121 |  | 0.0000 |
| 1006 | 18 | True | 6 | 28.24 | 0.212500 |  | 0.0000 |
| 1016 | 18 | True | 4 | 28.86 | 0.138614 |  | 0.0000 |
| 1022 | 18 | True | 6 | 29.03 | 0.206693 |  | 0.0000 |
| 1028 | 18 | True | 6 | 28.97 | 0.207101 |  | 0.0000 |
| 1052 | 18 | True | 6 | 29.89 | 0.200765 |  | 0.0000 |
| 1088 | 18 | True | 6 | 30.00 | 0.200000 |  | 0.0000 |

## Sources Integrated

- The exceptional set of Goldbach problem and Linnik's constant: https://arxiv.org/abs/2511.05631
- On Goldbach numbers in short intervals: https://arxiv.org/abs/2512.23534
- Small gaps between Goldbach primes: https://arxiv.org/abs/2508.02769
- Explicit estimates for the Goldbach summatory function: https://arxiv.org/abs/2411.00323
- Average orders of Goldbach Estimates in Arithmetic Progressions: https://arxiv.org/abs/2407.18266
- Primes in arithmetic progressions to large moduli, and Goldbach beyond the square-root barrier: https://arxiv.org/abs/2309.08522
- Primes in arithmetic progressions to large moduli and refinements of Harman's sieve: https://arxiv.org/abs/2602.20917
- On Chen's theorem, Goldbach's conjecture and almost prime twins II: https://runbolicarey.com/assets/downloads/On_Chen_s_theorem__Goldbach_s_conjecture_and_almost_prime_twins_II.pdf
- Goldbach Conjecture: Violation Probability and Generalization to Prime-like Distributions: https://arxiv.org/abs/2504.14353
- Achieving quantum advantage in a search for violations of the Goldbach conjecture: https://arxiv.org/abs/2404.00517

## GitHub Ideas Integrated

- isaac-6/goldbach-gpu (MIT): Segmented GPU verification with rigorous fallback as the design target for future range mode. https://github.com/isaac-6/goldbach-gpu
- dataplayer12/goldbach-comet (MIT): Keep G(n) computation and comet/visual summaries separable. https://github.com/dataplayer12/goldbach-comet
- Ruqing1963/Goldbach-Bias-Analysis (MIT): Bias/drift correction for Hardy-Littlewood residuals. https://github.com/Ruqing1963/Goldbach-Bias-Analysis
