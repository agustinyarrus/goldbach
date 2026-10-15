# Goldbach RTX round 7

Limit: 100,000,000
Backend: cupy-rtx-fft
FFT seconds: 2.304
Zero count: 0

## Main Findings

- Weakest >=1000: 1112 with 16 pairs.
- Strongest: 96996900 with 931,792 pairs.
- Summatory pairs up to limit: 8,804,091,938,900.

## Short Interval Metrics

| threshold | good count | max gap | from | to | gap/(123 log^2 x) |
|---:|---:|---:|---:|---:|---:|
| 1 | 49999999 | 2 | 4 | 6 | 0.008461 |
| 20 | 49999624 | 24 | 300 | 324 | 0.005998 |
| 100 | 49996467 | 210 | 2310 | 2520 | 0.028462 |
| 1000 | 49933937 | 1680 | 39270 | 40950 | 0.122062 |
| 5000 | 49540863 | 4620 | 265650 | 270270 | 0.240778 |
| 10000 | 48959791 | 30030 | 570570 | 600600 | 1.389731 |
| 20000 | 47662797 | 54600 | 1291290 | 1345890 | 2.241962 |
| 50000 | 43263045 | 30030 | 3873870 | 3903900 | 1.060944 |
| 100000 | 35100872 | 180180 | 8378370 | 8558550 | 5.764497 |

## Progression Density

### mod 2310

Top/bottom density ratio: 3.5609

Top residues: 0 (2.7250), 1890 (2.4527), 840 (2.4527), 210 (2.4527), 1050 (2.4527), 630 (2.4527), 1260 (2.4525), 1680 (2.4525)

Bottom residues: 2042 (0.7653), 1322 (0.7654), 692 (0.7655), 992 (0.7655), 2162 (0.7655), 62 (0.7655), 398 (0.7655), 1742 (0.7655)

### mod 30030

Top/bottom density ratio: 3.8849

Top residues: 0 (2.9514), 9240 (2.7064), 2310 (2.7064), 6930 (2.7062), 23100 (2.7062), 11550 (2.7062), 20790 (2.7062), 27720 (2.7061)

Bottom residues: 13592 (0.7597), 29762 (0.7597), 14552 (0.7597), 9092 (0.7597), 17492 (0.7597), 6362 (0.7598), 20522 (0.7598), 25472 (0.7598)

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
| 1096 | 18 | True | 2 | 31.14 | 0.064220 |  | 0.0000 |
| 1142 | 18 | True | 6 | 32.82 | 0.182796 |  | 0.0000 |
| 96996900 | 931792 | False | 2 | 52.05 | 0.038426 |  | 0.0000 |
| 99279180 | 925874 | False | 2 | 53.61 | 0.037304 |  | 0.0000 |
| 99038940 | 907058 | False | 2 | 54.59 | 0.036634 |  | 0.0000 |
| 98138040 | 905226 | False | 2 | 54.21 | 0.036896 |  | 0.0000 |
| 99549450 | 899964 | False | 2 | 55.31 | 0.036162 |  | 0.0000 |
| 98528430 | 897668 | False | 2 | 54.88 | 0.036443 |  | 0.0000 |
| 99849750 | 896665 | False | 2 | 55.68 | 0.035921 |  | 0.0000 |
| 93933840 | 896141 | False | 2 | 52.41 | 0.038161 |  | 0.0000 |

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
