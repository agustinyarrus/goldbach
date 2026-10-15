# Goldbach RTX round 7

Limit: 20,000,000
Backend: cupy-rtx-fft
FFT seconds: 1.607
Zero count: 0

## Main Findings

- Weakest >=1000: 1112 with 16 pairs.
- Strongest: 19399380 with 226,758 pairs.
- Summatory pairs up to limit: 430,837,804,125.

## Short Interval Metrics

| threshold | good count | max gap | from | to | gap/(123 log^2 x) |
|---:|---:|---:|---:|---:|---:|
| 1 | 9999999 | 2 | 4 | 6 | 0.008461 |
| 20 | 9999624 | 24 | 300 | 324 | 0.005998 |
| 100 | 9996467 | 210 | 2310 | 2520 | 0.028462 |
| 1000 | 9933937 | 1680 | 39270 | 40950 | 0.122062 |
| 5000 | 9540863 | 4620 | 265650 | 270270 | 0.240778 |
| 10000 | 8959791 | 30030 | 570570 | 600600 | 1.389731 |
| 20000 | 7662797 | 54600 | 1291290 | 1345890 | 2.241962 |
| 50000 | 3263045 | 30030 | 3873870 | 3903900 | 1.060944 |
| 100000 | 583661 | 180180 | 8378370 | 8558550 | 5.764497 |

## Progression Density

### mod 2310

Top/bottom density ratio: 3.5671

Top residues: 0 (2.7623), 210 (2.4868), 1050 (2.4867), 630 (2.4866), 1890 (2.4866), 840 (2.4865), 1680 (2.4862), 1470 (2.4862)

Bottom residues: 2042 (0.7744), 1118 (0.7748), 2252 (0.7748), 362 (0.7748), 1448 (0.7749), 908 (0.7749), 1832 (0.7749), 2162 (0.7749)

### mod 30030

Top/bottom density ratio: 3.8914

Top residues: 0 (2.9899), 9240 (2.7443), 6930 (2.7439), 2310 (2.7434), 16170 (2.7434), 11550 (2.7434), 18480 (2.7433), 27720 (2.7433)

Bottom residues: 9092 (0.7683), 29762 (0.7684), 20522 (0.7684), 6662 (0.7684), 13592 (0.7684), 9602 (0.7684), 25472 (0.7685), 6362 (0.7686)

## Direct Profiles

| n | pairs | audit | min gap | avg gap | min/avg | Chen D12 | D12/pairs |
|---:|---:|---|---:|---:|---:|---:|---:|
| 1112 | 16 | True | 6 | 35.68 | 0.168174 | 115 | 7.1875 |
| 1004 | 18 | True | 6 | 28.29 | 0.212121 | 99 | 5.5000 |
| 1006 | 18 | True | 6 | 28.24 | 0.212500 | 107 | 5.9444 |
| 1016 | 18 | True | 4 | 28.86 | 0.138614 | 102 | 5.6667 |
| 1022 | 18 | True | 6 | 29.03 | 0.206693 | 115 | 6.3889 |
| 1028 | 18 | True | 6 | 28.97 | 0.207101 | 102 | 5.6667 |
| 1052 | 18 | True | 6 | 29.89 | 0.200765 | 107 | 5.9444 |
| 1088 | 18 | True | 6 | 30.00 | 0.200000 | 110 | 6.1111 |
| 1096 | 18 | True | 2 | 31.14 | 0.064220 | 115 | 6.3889 |
| 1142 | 18 | True | 6 | 32.82 | 0.182796 | 118 | 6.5556 |
| 19399380 | 226758 | True | 2 | 42.78 | 0.046756 | 1055868 | 4.6564 |
| 19909890 | 219217 | True | 2 | 45.41 | 0.044042 | 1050246 | 4.7909 |
| 19969950 | 217608 | True | 2 | 45.89 | 0.043587 | 1048645 | 4.8190 |
| 18888870 | 215303 | True | 2 | 43.87 | 0.045594 | 1014779 | 4.7133 |
| 19999980 | 211905 | True | 2 | 47.19 | 0.042381 | 1034157 | 4.8803 |
| 19870620 | 209671 | True | 2 | 47.39 | 0.042207 | 1025308 | 4.8901 |
| 19339320 | 209605 | True | 2 | 46.13 | 0.043353 | 1013298 | 4.8343 |
| 19549530 | 209389 | True | 2 | 46.68 | 0.042843 | 1015928 | 4.8519 |
| 19699680 | 208637 | True | 2 | 47.21 | 0.042364 | 1018691 | 4.8826 |
| 19939920 | 208246 | True | 2 | 47.88 | 0.041775 | 1023335 | 4.9141 |
| 2672 | 28 | True | 6 | 48.11 | 0.124717 | 224 | 8.0000 |
| 9699690 | 124180 | True | 2 | 39.05 | 0.051210 | 563495 | 4.5377 |
| 10000000 | 38807 | True | 6 | 128.84 | 0.046568 | 275559 | 7.1008 |
| 20000000 | 70730 | True | 6 | 141.38 | 0.042438 | 511222 | 7.2278 |

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
