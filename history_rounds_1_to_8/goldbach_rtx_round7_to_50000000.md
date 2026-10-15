# Goldbach RTX round 7

Limit: 50,000,000
Backend: cupy-rtx-fft
FFT seconds: 0.473
Zero count: 0

## Main Findings

- Weakest >=1000: 1112 with 16 pairs.
- Strongest: 48498450 with 505,193 pairs.
- Summatory pairs up to limit: 2,394,752,234,437.

## Short Interval Metrics

| threshold | good count | max gap | from | to | gap/(123 log^2 x) |
|---:|---:|---:|---:|---:|---:|
| 1 | 24999999 | 2 | 4 | 6 | 0.008461 |
| 20 | 24999624 | 24 | 300 | 324 | 0.005998 |
| 100 | 24996467 | 210 | 2310 | 2520 | 0.028462 |
| 1000 | 24933937 | 1680 | 39270 | 40950 | 0.122062 |
| 5000 | 24540863 | 4620 | 265650 | 270270 | 0.240778 |
| 10000 | 23959791 | 30030 | 570570 | 600600 | 1.389731 |
| 20000 | 22662797 | 54600 | 1291290 | 1345890 | 2.241962 |
| 50000 | 18263045 | 30030 | 3873870 | 3903900 | 1.060944 |
| 100000 | 10100872 | 180180 | 8378370 | 8558550 | 5.764497 |

## Progression Density

### mod 2310

Top/bottom density ratio: 3.5633

Top residues: 0 (2.7402), 1890 (2.4665), 210 (2.4665), 840 (2.4664), 1050 (2.4664), 630 (2.4663), 1470 (2.4662), 1680 (2.4662)

Bottom residues: 2042 (0.7690), 992 (0.7694), 1832 (0.7694), 1718 (0.7694), 1322 (0.7694), 1118 (0.7694), 362 (0.7694), 908 (0.7694)

### mod 30030

Top/bottom density ratio: 3.8877

Top residues: 0 (2.9673), 9240 (2.7217), 6930 (2.7216), 2310 (2.7215), 23100 (2.7213), 13860 (2.7213), 20790 (2.7213), 11550 (2.7212)

Bottom residues: 20522 (0.7632), 29762 (0.7633), 13592 (0.7633), 9602 (0.7634), 6662 (0.7634), 9092 (0.7635), 25472 (0.7635), 19388 (0.7635)

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
| 48498450 | 505193 | True | 2 | 48.00 | 0.041667 | 2427622 | 4.8053 |
| 49639590 | 502457 | True | 2 | 49.40 | 0.040488 | 2442462 | 4.8610 |
| 49519470 | 491705 | True | 2 | 50.35 | 0.039718 | 2414705 | 4.9109 |
| 49069020 | 491287 | True | 2 | 49.94 | 0.040049 | 2401168 | 4.8875 |
| 46966920 | 486549 | True | 2 | 48.27 | 0.041438 | 2344898 | 4.8194 |
| 47477430 | 485458 | True | 2 | 48.90 | 0.040900 | 2352012 | 4.8449 |
| 47987940 | 483704 | True | 2 | 49.60 | 0.040319 | 2360067 | 4.8792 |
| 49990710 | 483317 | True | 2 | 51.72 | 0.038673 | 2399769 | 4.9652 |
| 49008960 | 482709 | True | 2 | 50.76 | 0.039398 | 2380463 | 4.9315 |
| 49038990 | 480447 | True | 2 | 51.03 | 0.039189 | 2374193 | 4.9416 |
| 2672 | 28 | True | 6 | 48.11 | 0.124717 | 224 | 8.0000 |
| 9699690 | 124180 | True | 2 | 39.05 | 0.051210 | 563495 | 4.5377 |
| 10000000 | 38807 | True | 6 | 128.84 | 0.046568 | 275559 | 7.1008 |
| 25000000 | 85838 | True | 6 | 145.62 | 0.041202 | 624072 | 7.2703 |
| 50000000 | 158467 | True | 6 | 157.76 | 0.038032 | 1161165 | 7.3275 |
| 1000000 | 5402 | True | 6 | 92.56 | 0.064820 | 36389 | 6.7362 |
| 5900000 | 24838 | True | 6 | 118.77 | 0.050517 | 174510 | 7.0259 |
| 10800000 | 82933 | True | 2 | 65.11 | 0.030716 | 471348 | 5.6835 |
| 15700000 | 57754 | True | 6 | 135.92 | 0.044143 | 413512 | 7.1599 |
| 20600000 | 73330 | True | 6 | 140.46 | 0.042716 | 528122 | 7.2020 |
| 25500000 | 186786 | True | 2 | 68.26 | 0.029300 | 1058795 | 5.6685 |
| 30400000 | 108238 | True | 6 | 140.43 | 0.042725 | 771880 | 7.1313 |
| 35300000 | 116790 | True | 6 | 151.13 | 0.039702 | 851025 | 7.2868 |
| 40200000 | 265415 | True | 2 | 75.73 | 0.026409 | 1548801 | 5.8354 |
| 45100000 | 164755 | True | 6 | 136.87 | 0.043837 | 1156906 | 7.0220 |

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
