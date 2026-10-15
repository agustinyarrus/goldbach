#!/usr/bin/env python3
"""
Goldbach RTX round 7.

Large-scale GPU/CPU hybrid lab inspired by recent papers and useful GitHub
projects. It avoids full CSV exports by default and writes compact JSON/Markdown
summaries.

Recommended runner:
    E:\\goldbach_big\\.venv_gpu\\Scripts\\python.exe goldbach_rtx_round7.py --limit 50000000
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_OUT = ROOT / "goldbach_rtx_output"
TWIN_PRIME_CONSTANT = 0.6601618158468696

PAPER_SOURCES = [
    {
        "key": "Zhao_2026_exceptional_set",
        "title": "The exceptional set of Goldbach problem and Linnik's constant",
        "url": "https://arxiv.org/abs/2511.05631",
        "lab_hook": "Track cold tails, floors, and persistent residue families rather than only zero counts.",
    },
    {
        "key": "Chirre_Hagen_2025_short_intervals",
        "title": "On Goldbach numbers in short intervals",
        "url": "https://arxiv.org/abs/2512.23534",
        "lab_hook": "Measure empirical short intervals for Goldbach-rich thresholds.",
    },
    {
        "key": "Akeno_2025_small_gaps",
        "title": "Small gaps between Goldbach primes",
        "url": "https://arxiv.org/abs/2508.02769",
        "lab_hook": "Measure gaps inside P cap (N-P) for selected N.",
    },
    {
        "key": "Bhowmik_ErnvallHytonen_Palojarvi_2025_summatory",
        "title": "Explicit estimates for the Goldbach summatory function",
        "url": "https://arxiv.org/abs/2411.00323",
        "lab_hook": "Export summatory and progression averages, not only pointwise counts.",
    },
    {
        "key": "Nguyen_2025_AP_average_orders",
        "title": "Average orders of Goldbach Estimates in Arithmetic Progressions",
        "url": "https://arxiv.org/abs/2407.18266",
        "lab_hook": "Compare arithmetic progression averages at mod 2310 and 30030.",
    },
    {
        "key": "Lichtman_2023_square_root_barrier",
        "title": "Primes in arithmetic progressions to large moduli, and Goldbach beyond the square-root barrier",
        "url": "https://arxiv.org/abs/2309.08522",
        "lab_hook": "Stress larger moduli and residue stability.",
    },
    {
        "key": "Runbo_Li_2026_Harman",
        "title": "Primes in arithmetic progressions to large moduli and refinements of Harman's sieve",
        "url": "https://arxiv.org/abs/2602.20917",
        "lab_hook": "Use large-modulus progression diagnostics.",
    },
    {
        "key": "Runbo_Li_2026_Chen",
        "title": "On Chen's theorem, Goldbach's conjecture and almost prime twins II",
        "url": "https://runbolicarey.com/assets/downloads/On_Chen_s_theorem__Goldbach_s_conjecture_and_almost_prime_twins_II.pdf",
        "lab_hook": "Measure D_{1,2}(N): prime plus prime-or-semiprime representations.",
    },
    {
        "key": "Farhadian_2025_prime_like",
        "title": "Goldbach Conjecture: Violation Probability and Generalization to Prime-like Distributions",
        "url": "https://arxiv.org/abs/2504.14353",
        "lab_hook": "Future stress tests with prime-like perturbed sets.",
    },
    {
        "key": "Marchukov_Trombettoni_Mussardo_Olshanii_2025_quantum_search",
        "title": "Achieving quantum advantage in a search for violations of the Goldbach conjecture",
        "url": "https://arxiv.org/abs/2404.00517",
        "lab_hook": "Treat high-scale checks as search problems.",
    },
]

GITHUB_SOURCES = [
    {
        "repo": "isaac-6/goldbach-gpu",
        "url": "https://github.com/isaac-6/goldbach-gpu",
        "license": "MIT",
        "idea_used": "Segmented GPU verification with rigorous fallback as the design target for future range mode.",
    },
    {
        "repo": "dataplayer12/goldbach-comet",
        "url": "https://github.com/dataplayer12/goldbach-comet",
        "license": "MIT",
        "idea_used": "Keep G(n) computation and comet/visual summaries separable.",
    },
    {
        "repo": "Ruqing1963/Goldbach-Bias-Analysis",
        "url": "https://github.com/Ruqing1963/Goldbach-Bias-Analysis",
        "license": "MIT",
        "idea_used": "Bias/drift correction for Hardy-Littlewood residuals.",
    },
]


def import_numpy():
    import numpy as np

    return np


def try_import_cupy():
    try:
        import cupy as cp

        count = cp.cuda.runtime.getDeviceCount()
        if count < 1:
            return None, "CuPy installed but no CUDA device was visible"
        return cp, None
    except Exception as exc:  # pragma: no cover - environment dependent
        return None, repr(exc)


def sieve(limit: int) -> tuple[bytearray, list[int]]:
    flags = bytearray(b"\x01") * (limit + 1)
    flags[0] = 0
    flags[1] = 0
    root = math.isqrt(limit)
    for p in range(2, root + 1):
        if flags[p]:
            start = p * p
            flags[start : limit + 1 : p] = b"\x00" * (((limit - start) // p) + 1)
    primes = [i for i in range(2, limit + 1) if flags[i]]
    return flags, primes


def fft_size_for(limit: int) -> int:
    size = 1
    while size <= 2 * limit:
        size <<= 1
    return size


def counts_by_gpu_fft(limit: int, is_prime: bytearray, primes: list[int], cp: Any, np: Any, even_chunk: int) -> tuple[Any, dict]:
    size = fft_size_for(limit)
    t0 = time.perf_counter()
    signal = cp.zeros(size, dtype=cp.float32)
    prime_idx = cp.asarray(np.asarray(primes, dtype=np.int64))
    signal[prime_idx] = 1.0
    spectrum = cp.fft.rfft(signal)
    spectrum *= spectrum
    convolution = cp.fft.irfft(spectrum, n=size)
    prime_gpu = cp.asarray(np.frombuffer(is_prime, dtype=np.uint8))
    n_evens = limit // 2 - 1
    counts_even = np.empty(n_evens, dtype=np.int32)
    for offset in range(0, n_evens, even_chunk):
        end = min(n_evens, offset + even_chunk)
        evens = 4 + 2 * cp.arange(offset, end, dtype=cp.int64)
        ordered = cp.rint(convolution[evens]).astype(cp.int64)
        diagonal = prime_gpu[evens // 2].astype(cp.int64)
        counts_even[offset:end] = cp.asnumpy(((ordered + diagonal) // 2).astype(cp.int32))
        del evens, ordered, diagonal
    cp.cuda.Stream.null.synchronize()
    free_mem, total_mem = cp.cuda.runtime.memGetInfo()
    del signal, prime_idx, spectrum, convolution, prime_gpu
    cp.get_default_memory_pool().free_all_blocks()
    return counts_even, {
        "backend": "cupy-rtx-fft",
        "fft_size": size,
        "seconds": time.perf_counter() - t0,
        "even_chunk": even_chunk,
        "gpu_mem_free_after": int(free_mem),
        "gpu_mem_total": int(total_mem),
    }


def counts_by_numpy_fft(limit: int, is_prime: bytearray, primes: list[int], np: Any) -> tuple[Any, dict]:
    size = fft_size_for(limit)
    t0 = time.perf_counter()
    signal = np.zeros(size, dtype=np.float32)
    signal[np.asarray(primes, dtype=np.int64)] = 1.0
    spectrum = np.fft.rfft(signal)
    spectrum *= spectrum
    convolution = np.fft.irfft(spectrum, n=size)
    evens = np.arange(4, limit + 1, 2, dtype=np.int64)
    ordered = np.rint(convolution[evens]).astype(np.int64)
    prime_np = np.frombuffer(is_prime, dtype=np.uint8)
    diagonal = prime_np[evens // 2].astype(np.int64)
    counts_even = ((ordered + diagonal) // 2).astype(np.int32)
    return counts_even, {"backend": "numpy-cpu-fft", "fft_size": size, "seconds": time.perf_counter() - t0}


def n_for_index(idx: int) -> int:
    return 4 + 2 * idx


def index_for_n(n: int) -> int:
    return (n - 4) // 2


def count_for_n(counts_even: Any, n: int) -> int:
    return int(counts_even[index_for_n(n)])


def extremes(counts_even: Any, np: Any, lower: int = 1000, top: int = 20) -> dict:
    evens = 4 + 2 * np.arange(counts_even.size, dtype=np.int64)
    mask = evens >= lower
    sub_counts = counts_even[mask]
    sub_evens = evens[mask]
    weak_idx = np.lexsort((sub_evens, sub_counts))[:top]
    strong_idx = np.lexsort((sub_evens, -sub_counts))[:top]
    return {
        "weakest": [{"n": int(sub_evens[i]), "pairs": int(sub_counts[i])} for i in weak_idx],
        "strongest": [{"n": int(sub_evens[i]), "pairs": int(sub_counts[i])} for i in strong_idx],
        "zero_count": int((counts_even == 0).sum()),
    }


def short_interval_metrics(counts_even: Any, np: Any, thresholds: list[int]) -> list[dict]:
    evens = 4 + 2 * np.arange(counts_even.size, dtype=np.int64)
    rows = []
    for threshold in thresholds:
        good = counts_even >= threshold
        good_evens = evens[good]
        if good_evens.size < 2:
            rows.append({"threshold": threshold, "good_count": int(good_evens.size), "max_gap": None})
            continue
        gaps = np.diff(good_evens)
        max_i = int(np.argmax(gaps))
        start = int(good_evens[max_i])
        max_gap = int(gaps[max_i])
        bound = 123.0 * (math.log(max(start, 3)) ** 2)
        rows.append(
            {
                "threshold": threshold,
                "good_count": int(good_evens.size),
                "first_good": int(good_evens[0]),
                "last_good": int(good_evens[-1]),
                "max_gap": max_gap,
                "max_gap_from": start,
                "max_gap_to": int(good_evens[max_i + 1]),
                "chirre_hagen_123log2_at_from": bound,
                "max_gap_over_123log2": max_gap / bound,
            }
        )
    return rows


def progression_density(counts_even: Any, np: Any, modulus: int, top: int = 15) -> dict:
    evens = 4 + 2 * np.arange(counts_even.size, dtype=np.int64)
    density = counts_even.astype(np.float64) * (np.log(evens.astype(np.float64)) ** 2) / evens
    residues = evens % modulus
    sums = np.bincount(residues, weights=density, minlength=modulus)
    nums = np.bincount(residues, minlength=modulus)
    means = np.divide(sums, nums, out=np.zeros_like(sums), where=nums > 0)
    active = np.where(nums > 0)[0]
    top_res = active[np.argsort(-means[active])[:top]]
    bottom_res = active[np.argsort(means[active])[:top]]
    return {
        "modulus": modulus,
        "active_residues": int(active.size),
        "top_density": [{"residue": int(r), "mean_density": float(means[r]), "count": int(nums[r])} for r in top_res],
        "bottom_density": [{"residue": int(r), "mean_density": float(means[r]), "count": int(nums[r])} for r in bottom_res],
        "top_bottom_ratio": float(means[top_res[0]] / means[bottom_res[0]]) if means[bottom_res[0]] else None,
    }


def build_prime_or_semiprime(max_n: int, is_prime: bytearray, primes: list[int]) -> bytearray:
    flags = bytearray(is_prime[: max_n + 1])
    root = math.isqrt(max_n)
    for i, p in enumerate(primes):
        if p > root:
            break
        for q in primes[i:]:
            value = p * q
            if value > max_n:
                break
            flags[value] = 1
    return flags


def goldbach_prime_gap_profile(n: int, is_prime: bytearray, primes: list[int]) -> dict:
    half = n // 2
    participants: list[int] = []
    lower_pairs: list[tuple[int, int]] = []
    for p in primes:
        if p > half:
            break
        q = n - p
        if is_prime[q]:
            lower_pairs.append((p, q))
            participants.append(p)
            if q != p:
                participants.append(q)
    participants.sort()
    gaps = [b - a for a, b in zip(participants, participants[1:])]
    min_gap = min(gaps) if gaps else None
    avg_gap = (sum(gaps) / len(gaps)) if gaps else None
    return {
        "n": n,
        "pair_count_direct": len(lower_pairs),
        "participant_count": len(participants),
        "goldbach_prime_min_gap": min_gap,
        "goldbach_prime_avg_gap": avg_gap,
        "min_over_avg_gap": (min_gap / avg_gap) if min_gap is not None and avg_gap else None,
        "first_pair": lower_pairs[0] if lower_pairs else None,
        "most_balanced_pair": lower_pairs[-1] if lower_pairs else None,
    }


def chen_d12_count(n: int, is_prime: bytearray, prime_or_semiprime: bytearray, primes: list[int]) -> int:
    total = 0
    for p in primes:
        if p >= n:
            break
        if prime_or_semiprime[n - p]:
            total += 1
    return total


def direct_profiles(targets: list[int], counts_even: Any, is_prime: bytearray, primes: list[int], include_chen: bool) -> list[dict]:
    prime_or_semiprime = build_prime_or_semiprime(max(targets), is_prime, primes) if include_chen and targets else None
    rows = []
    for n in targets:
        profile = goldbach_prime_gap_profile(n, is_prime, primes)
        csv_count = count_for_n(counts_even, n)
        profile["count_from_fft"] = csv_count
        profile["audit_match"] = profile["pair_count_direct"] == csv_count
        if prime_or_semiprime is not None:
            d12 = chen_d12_count(n, is_prime, prime_or_semiprime, primes)
            profile["chen_D_1_2"] = d12
            profile["chen_over_goldbach_pairs"] = d12 / csv_count if csv_count else None
        rows.append(profile)
    return rows


def choose_targets(ext: dict, limit: int, max_profiles: int) -> list[int]:
    targets: list[int] = []
    for row in ext["weakest"][:10]:
        if row["n"] >= 1000:
            targets.append(row["n"])
    for row in ext["strongest"][:10]:
        targets.append(row["n"])
    for n in [1112, 2672, 9699690, 10_000_000, limit // 4 * 2, limit // 2 * 2, limit - (limit % 2)]:
        if 4 <= n <= limit:
            targets.append(n)
    # Add high-scale evenly spaced samples.
    step = max(2, (limit - 1_000_000) // 10)
    for n in range(1_000_000, limit + 1, step):
        if n % 2:
            n += 1
        if n <= limit:
            targets.append(n)
    unique: list[int] = []
    seen = set()
    for n in targets:
        if n % 2 == 0 and 4 <= n <= limit and n not in seen:
            unique.append(n)
            seen.add(n)
        if len(unique) >= max_profiles:
            break
    return unique


def summatory_metrics(counts_even: Any, np: Any) -> dict:
    total = int(counts_even.astype(np.int64).sum())
    evens = 4 + 2 * np.arange(counts_even.size, dtype=np.int64)
    checkpoints = []
    running = counts_even.astype(np.int64).cumsum()
    for q in [0.1, 0.25, 0.5, 0.75, 1.0]:
        idx = min(counts_even.size - 1, max(0, int(round((counts_even.size - 1) * q))))
        checkpoints.append({"n": int(evens[idx]), "summatory_pairs": int(running[idx])})
    return {"total_pairs_summatory": total, "checkpoints": checkpoints}


def save_npz(out_dir: Path, limit: int, counts_even: Any, np: Any) -> str:
    path = out_dir / f"goldbach_counts_even_to_{limit}.npz"
    evens_start_step = np.asarray([4, 2, limit], dtype=np.int64)
    np.savez_compressed(path, evens_start_step=evens_start_step, counts_even=counts_even.astype(np.int32))
    return str(path)


def write_report(path: Path, metrics: dict) -> None:
    lines = [
        "# Goldbach RTX round 7",
        "",
        f"Limit: {metrics['limit']:,}",
        f"Backend: {metrics['fft']['backend']}",
        f"FFT seconds: {metrics['fft']['seconds']:.3f}",
        f"Zero count: {metrics['extremes']['zero_count']}",
        "",
        "## Main Findings",
        "",
        f"- Weakest >=1000: {metrics['extremes']['weakest'][0]['n']} with {metrics['extremes']['weakest'][0]['pairs']} pairs.",
        f"- Strongest: {metrics['extremes']['strongest'][0]['n']} with {metrics['extremes']['strongest'][0]['pairs']:,} pairs.",
        f"- Summatory pairs up to limit: {metrics['summatory']['total_pairs_summatory']:,}.",
        "",
        "## Short Interval Metrics",
        "",
        "| threshold | good count | max gap | from | to | gap/(123 log^2 x) |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for row in metrics["short_intervals"]:
        ratio = row.get("max_gap_over_123log2")
        lines.append(
            f"| {row['threshold']} | {row['good_count']} | {row.get('max_gap')} | "
            f"{row.get('max_gap_from')} | {row.get('max_gap_to')} | {ratio:.6f} |"
            if ratio is not None
            else f"| {row['threshold']} | {row['good_count']} |  |  |  |  |"
        )
    lines += ["", "## Progression Density", ""]
    for prog in metrics["progressions"]:
        lines += [
            f"### mod {prog['modulus']}",
            "",
            f"Top/bottom density ratio: {prog['top_bottom_ratio']:.4f}",
            "",
            "Top residues: "
            + ", ".join(f"{r['residue']} ({r['mean_density']:.4f})" for r in prog["top_density"][:8]),
            "",
            "Bottom residues: "
            + ", ".join(f"{r['residue']} ({r['mean_density']:.4f})" for r in prog["bottom_density"][:8]),
            "",
        ]
    lines += [
        "## Direct Profiles",
        "",
        "| n | pairs | audit | min gap | avg gap | min/avg | Chen D12 | D12/pairs |",
        "|---:|---:|---|---:|---:|---:|---:|---:|",
    ]
    for row in metrics["direct_profiles"]:
        lines.append(
            f"| {row['n']} | {row['count_from_fft']} | {row['audit_match']} | "
            f"{row['goldbach_prime_min_gap']} | {row['goldbach_prime_avg_gap']:.2f} | "
            f"{row['min_over_avg_gap']:.6f} | {row.get('chen_D_1_2', '')} | "
            f"{row.get('chen_over_goldbach_pairs', 0):.4f} |"
        )
    lines += [
        "",
        "## Sources Integrated",
        "",
    ]
    for source in PAPER_SOURCES:
        lines.append(f"- {source['title']}: {source['url']}")
    lines += ["", "## GitHub Ideas Integrated", ""]
    for source in GITHUB_SOURCES:
        lines.append(f"- {source['repo']} ({source['license']}): {source['idea_used']} {source['url']}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="RTX-scale Goldbach round 7.")
    parser.add_argument("--limit", type=int, default=50_000_000)
    parser.add_argument("--backend", choices=["auto", "gpu", "cpu"], default="auto")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--max-profiles", type=int, default=36)
    parser.add_argument("--gpu-even-chunk", type=int, default=5_000_000)
    parser.add_argument("--no-chen", action="store_true")
    parser.add_argument("--save-counts", action="store_true")
    args = parser.parse_args()

    if args.limit < 10_000:
        raise SystemExit("--limit must be at least 10000")
    if args.limit % 2:
        args.limit -= 1
    args.out_dir.mkdir(parents=True, exist_ok=True)

    np = import_numpy()
    cp = None
    cupy_error = None
    if args.backend in {"auto", "gpu"}:
        cp, cupy_error = try_import_cupy()
        if args.backend == "gpu" and cp is None:
            raise SystemExit(f"GPU backend requested but unavailable: {cupy_error}")

    start = time.perf_counter()
    is_prime, primes = sieve(args.limit)
    sieve_seconds = time.perf_counter() - start

    if cp is not None:
        try:
            counts_even, fft_meta = counts_by_gpu_fft(args.limit, is_prime, primes, cp, np, args.gpu_even_chunk)
        except Exception as exc:
            if args.backend == "gpu":
                raise
            cupy_error = repr(exc)
            counts_even, fft_meta = counts_by_numpy_fft(args.limit, is_prime, primes, np)
            fft_meta["gpu_fallback_error"] = cupy_error
    else:
        counts_even, fft_meta = counts_by_numpy_fft(args.limit, is_prime, primes, np)
        if cupy_error:
            fft_meta["gpu_unavailable"] = cupy_error

    ext = extremes(counts_even, np)
    targets = choose_targets(ext, args.limit, args.max_profiles)
    metrics = {
        "limit": args.limit,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "system": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "sieve": {"prime_count": len(primes), "seconds": sieve_seconds},
        "fft": fft_meta,
        "extremes": ext,
        "short_intervals": short_interval_metrics(counts_even, np, [1, 20, 100, 1_000, 5_000, 10_000, 20_000, 50_000, 100_000]),
        "progressions": [progression_density(counts_even, np, 2310), progression_density(counts_even, np, 30030)],
        "summatory": summatory_metrics(counts_even, np),
        "targets": targets,
        "direct_profiles": direct_profiles(targets, counts_even, is_prime, primes, include_chen=not args.no_chen),
        "paper_sources": PAPER_SOURCES,
        "github_sources": GITHUB_SOURCES,
        "total_seconds": None,
    }
    if args.save_counts:
        metrics["counts_npz"] = save_npz(args.out_dir, args.limit, counts_even, np)
    metrics["total_seconds"] = time.perf_counter() - start

    json_path = args.out_dir / f"goldbach_rtx_round7_to_{args.limit}.json"
    md_path = args.out_dir / f"goldbach_rtx_round7_to_{args.limit}.md"
    json_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    write_report(md_path, metrics)

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(f"backend={metrics['fft']['backend']} limit={args.limit:,} zeros={ext['zero_count']}")
    print(f"weakest={ext['weakest'][0]} strongest={ext['strongest'][0]}")
    print(f"sieve={sieve_seconds:.2f}s fft={fft_meta['seconds']:.2f}s total={metrics['total_seconds']:.2f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
