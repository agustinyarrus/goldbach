#!/usr/bin/env python3
"""
Hostile CRT Goldbach probe.

Constructs even numbers n such that n-p is forced composite for many small
prime candidates p. This is not an exhaustive verifier; it is an adversarial
candidate generator for finding unusually hard Goldbach instances.

Two blocking modes:
1. greedy-cover: choose one residue per small modulus to cover many candidate
   primes p <= p-limit.
2. exact-prefix: force n-p composite for the first K odd prime candidates.

The greedy mode is practical in 64-bit ranges. The exact-prefix mode is best
for huge-digit stress tests.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "goldbach_rtx_output"
UINT64_MAX = (1 << 64) - 1
MR_BASES_64 = (2, 325, 9375, 28178, 450775, 9780504, 1795265022)
SMALL_TRIAL_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
_WORKER_PRIMES: list[int] = []
_WORKER_CANDIDATES: list[int] = []
_WORKER_CONGRUENCES: list[dict] = []
_WORKER_ROUNDS = 32
_WORKER_SEED = 0


def sieve(limit: int) -> list[int]:
    flags = bytearray(b"\x01") * (limit + 1)
    flags[0] = 0
    if limit >= 1:
        flags[1] = 0
    root = math.isqrt(limit)
    for p in range(2, root + 1):
        if flags[p]:
            start = p * p
            flags[start : limit + 1 : p] = b"\x00" * (((limit - start) // p) + 1)
    return [n for n in range(2, limit + 1) if flags[n]]


def crt_pair(a1: int, m1: int, a2: int, m2: int) -> tuple[int, int]:
    inv = pow(m1, -1, m2)
    t = ((a2 - a1) * inv) % m2
    modulus = m1 * m2
    return (a1 + m1 * t) % modulus, modulus


def miller_rabin(n: int, bases) -> bool:
    if n < 2:
        return False
    for p in SMALL_TRIAL_PRIMES:
        if n % p == 0:
            return n == p
    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2
    for a in bases:
        a %= n
        if a in (0, 1):
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True


def bases_for(n: int, rng: random.Random, rounds: int):
    if n <= UINT64_MAX:
        return MR_BASES_64, "deterministic_u64"
    bases = list(SMALL_TRIAL_PRIMES)
    while len(bases) < rounds:
        bases.append(rng.randrange(2, n - 2))
    return bases, f"probable_mr_{rounds}_bases"


def find_pair(n: int, primes: list[int], rng: random.Random, rounds: int) -> dict:
    checks = 0
    for p in primes:
        if p > n // 2:
            break
        q = n - p
        bases, proof = bases_for(q, rng, rounds)
        checks += 1
        if miller_rabin(q, bases):
            return {"status": "found", "p": p, "q": q, "p_checks": checks, "proof_level": proof, "q_digits": len(str(q))}
    return {"status": "suspicious_no_pair_with_p_limit", "p": None, "p_checks": checks, "proof_level": "none", "q_digits": len(str(n))}


def init_worker(primes: list[int], candidates: list[int], congruences: list[dict], rounds: int, seed: int) -> None:
    global _WORKER_PRIMES, _WORKER_CANDIDATES, _WORKER_CONGRUENCES, _WORKER_ROUNDS, _WORKER_SEED
    _WORKER_PRIMES = primes
    _WORKER_CANDIDATES = candidates
    _WORKER_CONGRUENCES = congruences
    _WORKER_ROUNDS = rounds
    _WORKER_SEED = seed


def probe_target_worker(n: int) -> dict:
    rng = random.Random((_WORKER_SEED << 32) ^ (n & ((1 << 64) - 1)))
    row = find_pair(n, _WORKER_PRIMES, rng, _WORKER_ROUNDS)
    row["n"] = n
    row["n_digits"] = len(str(n))
    row["blocking_validation"] = validate_blocking(n, _WORKER_CANDIDATES, _WORKER_CONGRUENCES, sample_limit=2000)
    return row


def greedy_cover(candidates: list[int], moduli: list[int]) -> dict:
    uncovered = set(candidates)
    congruences: list[dict] = []
    residue = 0
    modulus = 2

    for m in moduli:
        counts = Counter(p % m for p in uncovered)
        if not counts:
            break
        # Avoid residue 0 unless it is genuinely best; nonzero residues usually
        # cover ordinary primes better for small moduli.
        best_residue, best_hits = max(counts.items(), key=lambda item: (item[1], item[0] != 0))
        residue, modulus = crt_pair(residue, modulus, best_residue, m)
        blocked_now = {p for p in uncovered if p % m == best_residue}
        uncovered -= blocked_now
        congruences.append({"modulus": m, "residue": best_residue, "blocked_now": len(blocked_now), "uncovered_after": len(uncovered)})

    return {
        "residue": residue,
        "modulus": modulus,
        "congruences": congruences,
        "blocked_count": len(candidates) - len(uncovered),
        "candidate_count": len(candidates),
        "blocked_fraction": (len(candidates) - len(uncovered)) / len(candidates),
        "first_unblocked": min(uncovered) if uncovered else None,
        "uncovered_sample": sorted(uncovered)[:30],
    }


def exact_prefix(candidates: list[int], blockers: list[int], block_count: int) -> dict:
    residue = 0
    modulus = 2
    congruences = []
    used = []
    for p, m in zip(candidates[:block_count], blockers):
        residue, modulus = crt_pair(residue, modulus, p % m, m)
        congruences.append({"candidate_p": p, "modulus": m, "residue": p % m})
        used.append(p)
    return {
        "residue": residue,
        "modulus": modulus,
        "congruences": congruences,
        "blocked_count": len(used),
        "candidate_count": len(candidates),
        "blocked_fraction": len(used) / len(candidates),
        "first_unblocked": candidates[block_count] if block_count < len(candidates) else None,
        "uncovered_sample": candidates[block_count : block_count + 30],
    }


def n_in_range(residue: int, modulus: int, start: int, stop: int, rng: random.Random) -> int | None:
    if start % 2:
        start += 1
    if stop % 2:
        stop -= 1
    k_min = (start - residue + modulus - 1) // modulus
    k_max = (stop - residue) // modulus
    if k_min > k_max:
        return None
    k = rng.randrange(k_min, k_max + 1)
    n = residue + k * modulus
    return n if n % 2 == 0 else n + modulus


def n_with_digits(residue: int, modulus: int, digits: int, rng: random.Random) -> int:
    lo = 10 ** (digits - 1)
    hi = 10**digits - 1
    if lo % 2:
        lo += 1
    if hi % 2:
        hi -= 1
    k_min = (lo - residue + modulus - 1) // modulus
    k_max = (hi - residue) // modulus
    if k_min > k_max:
        # If modulus is already larger than the digit interval, jump to a larger
        # number with the required residue rather than failing.
        k_min = max(1, (lo - residue + modulus - 1) // modulus)
        k_max = k_min + 10_000
    k = rng.randrange(k_min, k_max + 1)
    return residue + k * modulus


def validate_blocking(n: int, candidates: list[int], congruences: list[dict], sample_limit: int = 2000) -> dict:
    blocked = 0
    false_blocks = 0
    for p in candidates[:sample_limit]:
        expected = False
        for row in congruences:
            m = row["modulus"]
            r = row["residue"]
            if p % m == r:
                expected = True
                break
        if expected:
            blocked += 1
            if (n - p) <= 1 or (n - p) % m != 0:
                false_blocks += 1
    return {"sample_checked": min(sample_limit, len(candidates)), "blocked_in_sample": blocked, "false_blocks": false_blocks}


def median(values: list[int]) -> float:
    values = sorted(values)
    if not values:
        return 0.0
    mid = len(values) // 2
    if len(values) % 2:
        return float(values[mid])
    return (values[mid - 1] + values[mid]) / 2


def write_report(path: Path, metrics: dict) -> None:
    lines = [
        "# Hostile CRT Goldbach probe",
        "",
        f"Mode: `{metrics['mode']}`",
        f"Constructor: `{metrics['constructor']}`",
        f"Targets: {metrics['target_count']}",
        f"p-limit: {metrics['p_limit']:,}",
        f"CRT modulus digits: {metrics['crt']['modulus_digits']}",
        f"Blocked fraction up to p-limit: {metrics['crt']['blocked_fraction']:.4f}",
        f"First unblocked candidate: {metrics['crt']['first_unblocked']}",
        "",
        "## Results",
        "",
        f"- Found: {metrics['found_count']}",
        f"- Suspicious: {metrics['suspicious_count']}",
        f"- Largest p found: {metrics['largest_p_found']}",
        f"- Median p checks: {metrics['median_p_checks']}",
        f"- Max p checks: {metrics['max_p_checks']}",
        f"- Seconds: {metrics['seconds']:.3f}",
        "",
        "## Congruences",
        "",
        "| modulus | residue | blocked now | uncovered after |",
        "|---:|---:|---:|---:|",
    ]
    for row in metrics["crt"]["congruences"][:80]:
        lines.append(
            f"| {row['modulus']} | {row['residue']} | {row.get('blocked_now', '')} | {row.get('uncovered_after', '')} |"
        )
    lines += [
        "",
        "## Top Hard Results",
        "",
        "| n digits | n | status | p | p checks | proof |",
        "|---:|---:|---|---:|---:|---|",
    ]
    for row in metrics["hardest_results"][:40]:
        lines.append(f"| {row['n_digits']} | {row['n']} | {row['status']} | {row.get('p')} | {row['p_checks']} | {row['proof_level']} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate hostile CRT Goldbach targets.")
    parser.add_argument("--constructor", choices=["greedy-cover", "exact-prefix"], default="greedy-cover")
    parser.add_argument("--mode", choices=["range", "digits"], default="range")
    parser.add_argument("--start", type=int, default=4_000_000_000_000_000_000)
    parser.add_argument("--stop", type=int, default=18_000_000_000_000_000_000)
    parser.add_argument("--digits", type=int, default=200)
    parser.add_argument("--count", type=int, default=1000)
    parser.add_argument("--p-limit", type=int, default=2_000_000)
    parser.add_argument("--mod-count", type=int, default=15)
    parser.add_argument("--exact-block-count", type=int, default=100)
    parser.add_argument("--mr-rounds", type=int, default=32)
    parser.add_argument("--seed", type=int, default=271828)
    parser.add_argument("--workers", type=int, default=1, help="Parallel worker processes. Use 0 for all logical CPUs.")
    parser.add_argument("--chunksize", type=int, default=128, help="Targets per process-pool chunk.")
    parser.add_argument("--progress-every", type=int, default=50_000, help="Print progress every N finished targets. Use 0 to disable.")
    parser.add_argument("--out-dir", type=Path, default=OUT)
    args = parser.parse_args()
    if args.workers == 0:
        args.workers = os.cpu_count() or 1

    args.out_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(args.seed)
    t0 = time.perf_counter()

    primes = sieve(args.p_limit)
    candidates = [p for p in primes if p >= 3]
    blocker_moduli = [p for p in primes if p >= 3][: args.mod_count]

    if args.constructor == "greedy-cover":
        crt = greedy_cover(candidates, blocker_moduli)
    else:
        blockers = [p for p in primes if p >= 3 and p not in set(candidates[: args.exact_block_count])]
        # If there are not enough disjoint blockers early, use later primes.
        if len(blockers) < args.exact_block_count:
            blockers = [p for p in primes if p >= 3][args.exact_block_count : args.exact_block_count * 3]
        crt = exact_prefix(candidates, blockers, args.exact_block_count)

    residue = crt["residue"]
    modulus = crt["modulus"]
    crt["modulus_digits"] = len(str(modulus))
    crt["residue_digits"] = len(str(residue))

    targets = []
    misses = 0
    for _ in range(args.count):
        if args.mode == "range":
            n = n_in_range(residue, modulus, args.start, args.stop, rng)
            if n is None:
                misses += 1
                break
        else:
            n = n_with_digits(residue, modulus, args.digits, rng)
        targets.append(n)

    print(
        f"prepared targets={len(targets)} constructor={args.constructor} mode={args.mode} "
        f"workers={args.workers} modulus_digits={crt['modulus_digits']}",
        flush=True,
    )

    if args.workers > 1 and targets:
        with ProcessPoolExecutor(
            max_workers=args.workers,
            initializer=init_worker,
            initargs=(primes, candidates, crt["congruences"], args.mr_rounds, args.seed),
        ) as pool:
            results = []
            for idx, row in enumerate(pool.map(probe_target_worker, targets, chunksize=args.chunksize), start=1):
                results.append(row)
                if args.progress_every and idx % args.progress_every == 0:
                    print(f"progress {idx}/{len(targets)}", flush=True)
    else:
        init_worker(primes, candidates, crt["congruences"], args.mr_rounds, args.seed)
        results = []
        for idx, n in enumerate(targets, start=1):
            results.append(probe_target_worker(n))
            if args.progress_every and idx % args.progress_every == 0:
                print(f"progress {idx}/{len(targets)}", flush=True)

    found = [row for row in results if row["status"] == "found"]
    p_values = [row["p"] for row in found]
    check_values = [row["p_checks"] for row in results]
    hardest = sorted(results, key=lambda row: (-row["p_checks"], row["n"]))[:100]

    metrics = {
        "mode": args.mode,
        "constructor": args.constructor,
        "start": args.start,
        "stop": args.stop,
        "digits": args.digits,
        "target_count": len(targets),
        "range_misses": misses,
        "p_limit": args.p_limit,
        "prime_count": len(primes),
        "mod_count": args.mod_count,
        "exact_block_count": args.exact_block_count,
        "workers": args.workers,
        "chunksize": args.chunksize,
        "progress_every": args.progress_every,
        "seed": args.seed,
        "crt": crt,
        "seconds": time.perf_counter() - t0,
        "found_count": len(found),
        "suspicious_count": len(results) - len(found),
        "largest_p_found": max(p_values) if p_values else None,
        "smallest_p_found": min(p_values) if p_values else None,
        "median_p_checks": median(check_values),
        "max_p_checks": max(check_values) if check_values else 0,
        "hardest_results": hardest,
        "results": results,
    }

    stamp = time.strftime("%Y%m%d_%H%M%S")
    json_path = args.out_dir / f"goldbach_hostile_crt_{args.constructor}_{args.mode}_{stamp}.json"
    md_path = args.out_dir / f"goldbach_hostile_crt_{args.constructor}_{args.mode}_{stamp}.md"
    json_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    write_report(md_path, metrics)

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(f"targets={len(targets)} found={len(found)} suspicious={len(results)-len(found)}")
    print(f"workers={args.workers} chunksize={args.chunksize}")
    print(f"blocked_fraction={crt['blocked_fraction']:.4f} first_unblocked={crt['first_unblocked']} modulus_digits={crt['modulus_digits']}")
    print(f"largest_p={metrics['largest_p_found']} median_checks={metrics['median_p_checks']} max_checks={metrics['max_p_checks']}")
    print(f"seconds={metrics['seconds']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
