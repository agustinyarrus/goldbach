# Round 8 - GPU64 CRT hostile search

Date: 2026-05-12

## What changed

- Added `goldbach_gpu64_probe.py`.
- Added CUDA kernel `search_goldbach64` for first Goldbach pair below 2^64.
- Added CUDA kernel `count_goldbach64` for counting all representations with prime `p <= p-limit`.
- Added CRT-hostile target generation in GPU mode.
- Added compact JSON saving to avoid filling C:.

## Key runs

### First-p hostile search, 4.00007e18 to 18e18

Command profile:

```powershell
E:\goldbach_big\.venv_gpu\Scripts\python.exe .\goldbach_gpu64_probe.py --mode hostile --start 4000070000000000000 --stop 18000000000000000000 --count 300000 --p-limit 2000000 --mod-count 11 --prime-chunk 8192 --validate 1000 --max-results-saved 5000
```

Output:

- File: `goldbach_gpu64_hostile_20260512_200650.json`
- Targets: 277,425
- CRT blocked fraction: 0.8045
- Missing up to p <= 2,000,000: 0
- Largest first p found: 2,557
- Kernel seconds: 64.118
- GPU telemetry: RTX reached 100% SM utilization.
- CPU validation: 1000/1000 sampled GPU results valid.

Hardest first-p target:

```text
n = 14275199748903066098
p = 2557
q = 14275199748903063541
```

### Full count hostile search, 4.00007e18 to 18e18

Command profile:

```powershell
E:\goldbach_big\.venv_gpu\Scripts\python.exe .\goldbach_gpu64_probe.py --task count --mode hostile --start 4000070000000000000 --stop 18000000000000000000 --count 20000 --p-limit 2000000 --mod-count 11 --prime-chunk 8192 --max-results-saved 5000 --seed 20260517
```

Output:

- File: `goldbach_gpu64_hostile_20260512_202518.json`
- Targets: 19,909
- Prime chunks: 19
- Candidate pairs launched: 2,965,107,097
- Missing up to p <= 2,000,000: 0
- Total small-p hits counted: 89,054,672
- Minimum small-p representations: 4,181
- Median small-p representations: 4,468
- Maximum small-p representations: 4,867
- Kernel seconds: 666.777
- GPU telemetry: RTX stayed at 100% SM utilization through the heavy chunks.

Coldest counted target:

```text
n = 16895403018399398618
representations with p <= 2,000,000 = 4,181
min p = 709
max p = 1,998,991
```

CPU full validation of the three coldest targets:

```text
n=16895403018399398618 gpu_count=4181 cpu_count=4181 min=709 max=1998991 ok=True
n=13287039417395496878 gpu_count=4209 cpu_count=4209 min=19 max=1999099 ok=True
n=15292835252282100638 gpu_count=4213 cpu_count=4213 min=67 max=1999957 ok=True
```

## Pattern notes

- Random huge probes around 4e18..18e18 found a pair extremely early, usually p below a few thousand.
- CRT greedy with `mod-count=11` is the best current adversarial generator for this machine/range balance.
- Greedy `mod-count=12` and `mod-count=13` block slightly more residues but produce far fewer distinct targets in the 64-bit range.
- Hybrid exact-prefix blocking raises the first unblocked prime but did not produce colder numbers than greedy; blocking many first primes alone is not enough.
- The current coldest signal is not "no pair"; it is lower small-p representation count. Even the coldest target found had 4,181 representations below p <= 2,000,000.

## Next good attacks

1. Repeat `--task count --mod-count 11` with new seeds and collect the global minimum count.
2. Run a two-stage pipeline: count many targets with p <= 2,000,000, then re-count the coldest 100 with p <= 10,000,000.
3. Add a GPU kernel that tests only selected cold targets with larger p windows.
4. Build segmented exhaustive verification below 2^64 only for windows selected by CRT/cold-count ranking.

## Follow-up seed 20260518

Command profile:

```powershell
E:\goldbach_big\.venv_gpu\Scripts\python.exe .\goldbach_gpu64_probe.py --task count --mode hostile --start 4000070000000000000 --stop 18000000000000000000 --count 20000 --p-limit 2000000 --mod-count 11 --prime-chunk 8192 --max-results-saved 5000 --seed 20260518
```

Output:

- File: `goldbach_gpu64_hostile_20260512_210602.json`
- Targets: 19,881
- Candidate pairs launched: 2,960,936,973
- Missing up to p <= 2,000,000: 0
- Minimum small-p representations: 4,192
- Median small-p representations: 4,468
- Maximum small-p representations: 4,873
- Kernel seconds: 670.876
- GPU telemetry while running: 100% SM utilization, about 75 C, about 80 W.

Coldest target in this seed:

```text
n = 12911015774628404558
representations with p <= 2,000,000 = 4,192
min p = 79
max p = 1,999,957
```

CPU validation of the three coldest targets:

```text
n=12911015774628404558 gpu_count=4192 cpu_count=4192 min=79 max=1999957 ok=True
n=11984477252592297578 gpu_count=4207 cpu_count=4207 min=19 max=1999957 ok=True
n=15993827859448792478 gpu_count=4207 cpu_count=4207 min=859 max=1999891 ok=True
```

Current cold-count record remains the previous seed:

```text
n = 16895403018399398618
representations with p <= 2,000,000 = 4,181
```
