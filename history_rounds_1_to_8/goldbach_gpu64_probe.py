#!/usr/bin/env python3
"""
GPU 64-bit Goldbach probe.

This probes even numbers below 2^64 by launching CUDA threads over
(target n, prime p) pairs. Each thread tests whether q=n-p is prime using a
deterministic Miller-Rabin basis for 64-bit integers. Modular multiplication is
implemented with exact add/double arithmetic because NVRTC on Windows does not
support unsigned __int128 device code.

It is not an exhaustive verifier for an interval. It is a high-throughput
searcher for random, boundary, and CRT-hostile targets.
"""

from __future__ import annotations

import argparse
import json
import random
import time
from collections import Counter
from pathlib import Path

import cupy as cp
import numpy as np

from goldbach_hostile_crt_probe import (
    MR_BASES_64,
    UINT64_MAX,
    bases_for,
    crt_pair,
    find_pair,
    greedy_cover,
    miller_rabin,
    n_in_range,
    sieve,
)


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "goldbach_rtx_output"
SENTINEL_U64 = np.uint64(UINT64_MAX)


CUDA_SRC = r'''
typedef unsigned long long ull;

__device__ __forceinline__ ull add_mod_u64(ull a, ull b, ull m) {
    // Exact (a+b) % m for a,b < m without relying on 128-bit arithmetic.
    return (a >= m - b) ? (a - (m - b)) : (a + b);
}

__device__ ull mul_mod_u64(ull a, ull b, ull m) {
    ull res = 0ULL;
    a %= m;
    while (b) {
        if (b & 1ULL) {
            res = add_mod_u64(res, a, m);
        }
        b >>= 1;
        if (b) {
            a = add_mod_u64(a, a, m);
        }
    }
    return res;
}

__device__ ull pow_mod_u64(ull a, ull d, ull m) {
    ull res = 1ULL;
    a %= m;
    while (d) {
        if (d & 1ULL) {
            res = mul_mod_u64(res, a, m);
        }
        d >>= 1;
        if (d) {
            a = mul_mod_u64(a, a, m);
        }
    }
    return res;
}

__device__ bool is_prime64(ull n) {
    const ull smalls[12] = {
        2ULL, 3ULL, 5ULL, 7ULL, 11ULL, 13ULL,
        17ULL, 19ULL, 23ULL, 29ULL, 31ULL, 37ULL
    };
    if (n < 2ULL) return false;
    #pragma unroll
    for (int i = 0; i < 12; ++i) {
        ull p = smalls[i];
        if (n % p == 0ULL) return n == p;
    }

    ull d = n - 1ULL;
    int s = 0;
    while ((d & 1ULL) == 0ULL) {
        d >>= 1;
        ++s;
    }

    const ull bases[7] = {
        2ULL, 325ULL, 9375ULL, 28178ULL,
        450775ULL, 9780504ULL, 1795265022ULL
    };
    #pragma unroll
    for (int i = 0; i < 7; ++i) {
        ull a = bases[i] % n;
        if (a == 0ULL || a == 1ULL) continue;
        ull x = pow_mod_u64(a, d, n);
        if (x == 1ULL || x == n - 1ULL) continue;
        bool witness_passed = false;
        for (int r = 1; r < s; ++r) {
            x = mul_mod_u64(x, x, n);
            if (x == n - 1ULL) {
                witness_passed = true;
                break;
            }
        }
        if (!witness_passed) return false;
    }
    return true;
}

extern "C" __global__ void search_goldbach64(
    const ull* __restrict__ targets,
    const ull* __restrict__ primes,
    ull* __restrict__ found_p,
    int target_count,
    int prime_count
) {
    ull total = (ull)target_count * (ull)prime_count;
    ull stride = (ull)blockDim.x * (ull)gridDim.x;
    ull tid = (ull)blockIdx.x * (ull)blockDim.x + (ull)threadIdx.x;

    for (ull pos = tid; pos < total; pos += stride) {
        int t = (int)(pos / (ull)prime_count);
        int j = (int)(pos - (ull)t * (ull)prime_count);
        ull p = primes[j];
        ull current = found_p[t];
        if (p >= current) continue;
        ull n = targets[t];
        if (p > (n >> 1)) continue;
        ull q = n - p;
        if (is_prime64(q)) {
            atomicMin(&found_p[t], p);
        }
    }
}

extern "C" __global__ void count_goldbach64(
    const ull* __restrict__ targets,
    const ull* __restrict__ primes,
    unsigned int* __restrict__ counts,
    ull* __restrict__ min_p,
    ull* __restrict__ max_p,
    int target_count,
    int prime_count
) {
    ull total = (ull)target_count * (ull)prime_count;
    ull stride = (ull)blockDim.x * (ull)gridDim.x;
    ull tid = (ull)blockIdx.x * (ull)blockDim.x + (ull)threadIdx.x;

    for (ull pos = tid; pos < total; pos += stride) {
        int t = (int)(pos / (ull)prime_count);
        int j = (int)(pos - (ull)t * (ull)prime_count);
        ull p = primes[j];
        ull n = targets[t];
        if (p > (n >> 1)) continue;
        ull q = n - p;
        if (is_prime64(q)) {
            atomicAdd(&counts[t], 1U);
            atomicMin(&min_p[t], p);
            atomicMax(&max_p[t], p);
        }
    }
}
'''


def random_even_in_range(rng: random.Random, start: int, stop: int) -> int:
    if start % 2:
        start += 1
    if stop % 2:
        stop -= 1
    return 2 * rng.randrange(start // 2, stop // 2 + 1)


def hybrid_cover(candidates: list[int], exact_count: int, greedy_mod_count: int) -> dict:
    uncovered = set(candidates)
    residue = 0
    modulus = 2
    congruences: list[dict] = []

    for p in candidates[:exact_count]:
        residue, modulus = crt_pair(residue, modulus, 0, p)
        blocked_now = {q for q in uncovered if q % p == 0}
        uncovered -= blocked_now
        congruences.append(
            {
                "modulus": p,
                "residue": 0,
                "blocked_now": len(blocked_now),
                "uncovered_after": len(uncovered),
                "kind": "exact_prefix",
            }
        )

    extra_moduli = candidates[exact_count : exact_count + greedy_mod_count]
    for m in extra_moduli:
        if modulus % m == 0:
            continue
        counts = Counter(p % m for p in uncovered)
        if not counts:
            break
        best_residue, _ = max(counts.items(), key=lambda item: (item[1], item[0] != 0))
        residue, modulus = crt_pair(residue, modulus, best_residue, m)
        blocked_now = {p for p in uncovered if p % m == best_residue}
        uncovered -= blocked_now
        congruences.append(
            {
                "modulus": m,
                "residue": best_residue,
                "blocked_now": len(blocked_now),
                "uncovered_after": len(uncovered),
                "kind": "greedy_cover",
            }
        )

    return {
        "residue": residue,
        "modulus": modulus,
        "congruences": congruences,
        "blocked_count": len(candidates) - len(uncovered),
        "candidate_count": len(candidates),
        "blocked_fraction": (len(candidates) - len(uncovered)) / len(candidates),
        "first_unblocked": min(uncovered) if uncovered else None,
        "uncovered_sample": sorted(uncovered)[:30],
        "exact_prefix_count": exact_count,
        "greedy_mod_count": greedy_mod_count,
    }


def build_targets(args: argparse.Namespace, rng: random.Random, primes: list[int]) -> tuple[list[int], dict]:
    meta: dict = {}
    if args.mode == "random":
        targets = [random_even_in_range(rng, args.start, args.stop) for _ in range(args.count)]
    elif args.mode == "boundary":
        base = args.start
        offsets = [0, 2, 4, 6, 8, 10, 12, 14, 30, 210, 2310, 30030, 510510, 9699690]
        targets = []
        for off in offsets[: args.count]:
            n = base + off
            targets.append(n if n % 2 == 0 else n + 1)
        while len(targets) < args.count:
            targets.append(random_even_in_range(rng, base, min(args.stop, base + args.span)))
    elif args.mode == "hostile":
        candidates = [p for p in primes if p >= 3]
        if args.exact_prefix_count:
            crt = hybrid_cover(candidates, args.exact_prefix_count, args.mod_count)
        else:
            crt = greedy_cover(candidates, [p for p in primes if p >= 3][: args.mod_count])
        crt["modulus_digits"] = len(str(crt["modulus"]))
        meta["crt"] = crt
        targets = []
        while len(targets) < args.count:
            n = n_in_range(crt["residue"], crt["modulus"], args.start, args.stop, rng)
            if n is None:
                raise SystemExit(
                    f"CRT modulus has no hit in range; reduce --mod-count. modulus_digits={crt['modulus_digits']}"
                )
            targets.append(n)
    else:
        raise ValueError(args.mode)

    unique = []
    seen = set()
    for n in targets:
        if n not in seen:
            if n > UINT64_MAX:
                raise SystemExit("This GPU64 probe only supports n <= 2^64-1.")
            unique.append(n)
            seen.add(n)
    return unique, meta


def validate_gpu_results(targets: list[int], found: list[int], primes: list[int], limit: int) -> list[dict]:
    rows = []
    prime_set = set(primes)
    for n, p in zip(targets[:limit], found[:limit]):
        if p == UINT64_MAX:
            rows.append({"n": n, "status": "no_gpu_pair", "p": None, "valid": False})
            continue
        q = n - p
        bases, proof = bases_for(q, random.Random(n ^ int(p)), 32)
        rows.append(
            {
                "n": n,
                "status": "found",
                "p": int(p),
                "q": int(q),
                "p_is_in_prime_list": int(p) in prime_set,
                "q_prime_cpu_check": miller_rabin(q, bases),
                "proof": proof,
            }
        )
    return rows


def write_report(path: Path, metrics: dict) -> None:
    lines = [
        "# GPU64 Goldbach probe",
        "",
        f"Mode: `{metrics['mode']}`",
        f"Targets: {metrics['target_count']:,}",
        f"Prime p-limit: {metrics['p_limit']:,}",
        f"Prime chunks: {metrics['prime_chunks']}",
        f"Kernel seconds: {metrics['kernel_seconds']:.3f}",
        f"Total candidate pairs launched: {metrics['candidate_pairs_launched']:,}",
        f"Task: `{metrics['task']}`",
        "",
        "## Results",
        "",
        f"- Found by GPU: {metrics['found_count']:,}",
        f"- Missing up to p-limit: {metrics['missing_count']:,}",
    ]
    if metrics["task"] == "count":
        lines += [
            f"- Min small-p representations: {metrics['min_small_p_count']}",
            f"- Median small-p representations: {metrics['median_small_p_count']}",
            f"- Max small-p representations: {metrics['max_small_p_count']}",
            "",
            "## Coldest GPU Results",
            "",
            "| n | small-p count | min p | max p |",
            "|---:|---:|---:|---:|",
        ]
        for row in metrics["coldest_results"][:40]:
            lines.append(f"| {row['n']} | {row['small_p_count']} | {row['min_p']} | {row['max_p']} |")
    else:
        lines += [
            f"- Smallest p found: {metrics['smallest_p_found']}",
            f"- Largest p found: {metrics['largest_p_found']}",
            f"- Median p found: {metrics['median_p_found']}",
            "",
            "## Hardest GPU Results",
            "",
            "| n | p | q |",
            "|---:|---:|---:|",
        ]
        for row in metrics["hardest_results"][:40]:
            lines.append(f"| {row['n']} | {row['p']} | {row['q']} |")
    if "crt" in metrics:
        lines += [
            "",
            "## CRT Hostility",
            "",
            f"- Blocked fraction: {metrics['crt']['blocked_fraction']:.4f}",
            f"- First unblocked p: {metrics['crt']['first_unblocked']}",
            f"- Modulus digits: {metrics['crt']['modulus_digits']}",
        ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def median_int(values: list[int]) -> int | None:
    if not values:
        return None
    values = sorted(values)
    return int(values[len(values) // 2])


def build_first_metrics(args, targets, primes, kernel, targets_gpu, prime_np, t0) -> dict:
    found_gpu = cp.full(len(targets), SENTINEL_U64, dtype=cp.uint64)
    prime_chunks = 0
    primes_launched = 0
    kernel_seconds = 0.0

    for offset in range(0, len(primes), args.prime_chunk):
        chunk_np = prime_np[offset : offset + args.prime_chunk]
        primes_gpu = cp.asarray(chunk_np)
        work_items = len(targets) * len(chunk_np)
        blocks = min(args.blocks, max(1, (work_items + args.threads - 1) // args.threads))
        start_event = cp.cuda.Event()
        end_event = cp.cuda.Event()
        start_event.record()
        kernel((blocks,), (args.threads,), (targets_gpu, primes_gpu, found_gpu, len(targets), len(chunk_np)))
        end_event.record()
        end_event.synchronize()
        elapsed = cp.cuda.get_elapsed_time(start_event, end_event) / 1000.0
        kernel_seconds += elapsed
        prime_chunks += 1
        primes_launched += len(chunk_np)
        found_now = int(cp.count_nonzero(found_gpu != SENTINEL_U64).get())
        print(
            f"chunk {prime_chunks}: primes {offset + 1:,}-{offset + len(chunk_np):,} "
            f"elapsed={elapsed:.3f}s found={found_now:,}/{len(targets):,}",
            flush=True,
        )
        del primes_gpu
        if found_now == len(targets):
            break

    found_arr = cp.asnumpy(found_gpu).astype(np.uint64)
    found_values = [int(p) for p in found_arr if int(p) != UINT64_MAX]
    result_rows = []
    for n, p in zip(targets, found_arr):
        p_int = int(p)
        result_rows.append(
            {
                "n": int(n),
                "p": None if p_int == UINT64_MAX else p_int,
                "q": None if p_int == UINT64_MAX else int(n - p_int),
            }
        )
    hardest = sorted((row for row in result_rows if row["p"] is not None), key=lambda row: (-row["p"], row["n"]))[:100]
    validation = validate_gpu_results(targets, [int(p) for p in found_arr], primes, args.validate)
    return {
        "task": "first",
        "prime_chunks": prime_chunks,
        "primes_launched": primes_launched,
        "candidate_pairs_launched": len(targets) * primes_launched,
        "kernel_seconds": kernel_seconds,
        "total_seconds": time.perf_counter() - t0,
        "found_count": len(found_values),
        "missing_count": len(targets) - len(found_values),
        "smallest_p_found": min(found_values) if found_values else None,
        "largest_p_found": max(found_values) if found_values else None,
        "median_p_found": median_int(found_values),
        "hardest_results": hardest,
        "validation": validation,
        "results_saved_count": min(len(result_rows), args.max_results_saved),
        "results_truncated": len(result_rows) > args.max_results_saved,
        "results": result_rows[: args.max_results_saved],
    }


def build_count_metrics(args, targets, primes, kernel, targets_gpu, prime_np, t0) -> dict:
    counts_gpu = cp.zeros(len(targets), dtype=cp.uint32)
    min_p_gpu = cp.full(len(targets), SENTINEL_U64, dtype=cp.uint64)
    max_p_gpu = cp.zeros(len(targets), dtype=cp.uint64)
    prime_chunks = 0
    primes_launched = 0
    kernel_seconds = 0.0

    for offset in range(0, len(primes), args.prime_chunk):
        chunk_np = prime_np[offset : offset + args.prime_chunk]
        primes_gpu = cp.asarray(chunk_np)
        work_items = len(targets) * len(chunk_np)
        blocks = min(args.blocks, max(1, (work_items + args.threads - 1) // args.threads))
        start_event = cp.cuda.Event()
        end_event = cp.cuda.Event()
        start_event.record()
        kernel(
            (blocks,),
            (args.threads,),
            (targets_gpu, primes_gpu, counts_gpu, min_p_gpu, max_p_gpu, len(targets), len(chunk_np)),
        )
        end_event.record()
        end_event.synchronize()
        elapsed = cp.cuda.get_elapsed_time(start_event, end_event) / 1000.0
        kernel_seconds += elapsed
        prime_chunks += 1
        primes_launched += len(chunk_np)
        total_hits = int(counts_gpu.sum().get())
        covered = int(cp.count_nonzero(counts_gpu).get())
        print(
            f"chunk {prime_chunks}: primes {offset + 1:,}-{offset + len(chunk_np):,} "
            f"elapsed={elapsed:.3f}s covered={covered:,}/{len(targets):,} hits={total_hits:,}",
            flush=True,
        )
        del primes_gpu

    counts = cp.asnumpy(counts_gpu).astype(np.uint32)
    min_p = cp.asnumpy(min_p_gpu).astype(np.uint64)
    max_p = cp.asnumpy(max_p_gpu).astype(np.uint64)
    count_values = [int(x) for x in counts]
    result_rows = []
    for n, c, lo, hi in zip(targets, counts, min_p, max_p):
        c_int = int(c)
        result_rows.append(
            {
                "n": int(n),
                "small_p_count": c_int,
                "min_p": None if c_int == 0 else int(lo),
                "max_p": None if c_int == 0 else int(hi),
            }
        )
    coldest = sorted(result_rows, key=lambda row: (row["small_p_count"], row["min_p"] or UINT64_MAX, row["n"]))[:100]
    return {
        "task": "count",
        "prime_chunks": prime_chunks,
        "primes_launched": primes_launched,
        "candidate_pairs_launched": len(targets) * primes_launched,
        "kernel_seconds": kernel_seconds,
        "total_seconds": time.perf_counter() - t0,
        "found_count": sum(1 for row in result_rows if row["small_p_count"] > 0),
        "missing_count": sum(1 for row in result_rows if row["small_p_count"] == 0),
        "min_small_p_count": min(count_values) if count_values else None,
        "median_small_p_count": median_int(count_values),
        "max_small_p_count": max(count_values) if count_values else None,
        "coldest_results": coldest,
        "validation": [],
        "results_saved_count": min(len(result_rows), args.max_results_saved),
        "results_truncated": len(result_rows) > args.max_results_saved,
        "results": result_rows[: args.max_results_saved],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Use CUDA to probe 64-bit Goldbach targets.")
    parser.add_argument("--task", choices=["first", "count"], default="first")
    parser.add_argument("--mode", choices=["random", "boundary", "hostile"], default="hostile")
    parser.add_argument("--start", type=int, default=4_000_070_000_000_000_000)
    parser.add_argument("--stop", type=int, default=18_000_000_000_000_000_000)
    parser.add_argument("--span", type=int, default=1_000_000_000_000_000_000)
    parser.add_argument("--count", type=int, default=20_000)
    parser.add_argument("--p-limit", type=int, default=2_000_000)
    parser.add_argument("--mod-count", type=int, default=13)
    parser.add_argument("--exact-prefix-count", type=int, default=0)
    parser.add_argument("--prime-chunk", type=int, default=8192)
    parser.add_argument("--threads", type=int, default=256)
    parser.add_argument("--blocks", type=int, default=65535)
    parser.add_argument("--seed", type=int, default=20260512)
    parser.add_argument("--validate", type=int, default=200)
    parser.add_argument("--max-results-saved", type=int, default=200_000)
    parser.add_argument("--out-dir", type=Path, default=OUT)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(args.seed)

    t0 = time.perf_counter()
    primes = sieve(args.p_limit)
    targets, extra = build_targets(args, rng, primes)
    prime_np = np.asarray(primes, dtype=np.uint64)
    target_np = np.asarray(targets, dtype=np.uint64)

    free_mem, total_mem = cp.cuda.runtime.memGetInfo()
    print(
        f"prepared targets={len(targets):,} primes={len(primes):,} "
        f"candidate_pairs={len(targets) * len(primes):,} gpu_free={free_mem // (1024**2)}MiB/{total_mem // (1024**2)}MiB",
        flush=True,
    )

    targets_gpu = cp.asarray(target_np)
    if args.task == "first":
        kernel = cp.RawKernel(CUDA_SRC, "search_goldbach64", options=("--std=c++11",))
        task_metrics = build_first_metrics(args, targets, primes, kernel, targets_gpu, prime_np, t0)
    else:
        kernel = cp.RawKernel(CUDA_SRC, "count_goldbach64", options=("--std=c++11",))
        task_metrics = build_count_metrics(args, targets, primes, kernel, targets_gpu, prime_np, t0)

    metrics = {
        "task": args.task,
        "mode": args.mode,
        "start": args.start,
        "stop": args.stop,
        "target_count": len(targets),
        "p_limit": args.p_limit,
        "prime_count": len(primes),
        "prime_chunk": args.prime_chunk,
        "threads": args.threads,
        "blocks": args.blocks,
        "seed": args.seed,
        **task_metrics,
        **extra,
    }

    stamp = time.strftime("%Y%m%d_%H%M%S")
    json_path = args.out_dir / f"goldbach_gpu64_{args.mode}_{stamp}.json"
    md_path = args.out_dir / f"goldbach_gpu64_{args.mode}_{stamp}.md"
    json_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    write_report(md_path, metrics)

    print(f"Wrote {json_path}", flush=True)
    print(f"Wrote {md_path}", flush=True)
    if args.task == "count":
        print(
            f"covered={metrics['found_count']:,}/{metrics['target_count']:,} missing={metrics['missing_count']:,} "
            f"min_count={metrics['min_small_p_count']} median_count={metrics['median_small_p_count']} "
            f"kernel={metrics['kernel_seconds']:.3f}s total={metrics['total_seconds']:.3f}s",
            flush=True,
        )
    else:
        print(
            f"found={metrics['found_count']:,}/{metrics['target_count']:,} missing={metrics['missing_count']:,} "
            f"largest_p={metrics['largest_p_found']} kernel={metrics['kernel_seconds']:.3f}s total={metrics['total_seconds']:.3f}s",
            flush=True,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
