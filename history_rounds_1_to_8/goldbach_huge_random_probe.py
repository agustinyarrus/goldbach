#!/usr/bin/env python3
"""
Huge random Goldbach probe.

This does not exhaustively verify a range. It samples very large even numbers
and tries to find a Goldbach partition using small prime p and Miller-Rabin for
n-p. For n < 2^64 the primality test is deterministic with known bases. For
larger n it is a strong probable-prime test and results are labelled probable.

The goal is to find "suspicious" numbers with no small-prime partition up to a
chosen p-limit. Those are not counterexamples, but they are good targets for
deeper search.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "goldbach_rtx_output"
UINT64_MAX = (1 << 64) - 1
MR_BASES_64 = (2, 325, 9375, 28178, 450775, 9780504, 1795265022)
SMALL_TRIAL_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


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


def miller_rabin(n: int, bases: list[int] | tuple[int, ...]) -> bool:
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


def primality_bases(n: int, rng: random.Random, rounds: int) -> tuple[list[int] | tuple[int, ...], str]:
    if n <= UINT64_MAX:
        return MR_BASES_64, "deterministic_u64"
    bases = list(SMALL_TRIAL_PRIMES)
    while len(bases) < rounds:
        bases.append(rng.randrange(2, n - 2))
    return bases, f"probable_mr_{rounds}_bases"


def find_goldbach_pair(n: int, primes: list[int], rng: random.Random, rounds: int) -> dict:
    if n < 4 or n % 2:
        raise ValueError("n must be even and >= 4")
    checks = 0
    for p in primes:
        if p > n // 2:
            break
        q = n - p
        bases, proof = primality_bases(q, rng, rounds)
        checks += 1
        if miller_rabin(q, bases):
            return {
                "n": n,
                "status": "found",
                "p": p,
                "q": q,
                "p_checks": checks,
                "proof_level": proof,
                "q_digits": len(str(q)),
            }
    return {
        "n": n,
        "status": "suspicious_no_pair_with_p_limit",
        "p_limit": primes[-1],
        "p_checks": checks,
        "proof_level": "none",
        "q_digits": len(str(n)),
    }


def random_even_in_range(rng: random.Random, start: int, stop: int) -> int:
    if start % 2:
        start += 1
    if stop % 2:
        stop -= 1
    return 2 * rng.randrange(start // 2, stop // 2 + 1)


def random_even_digits(rng: random.Random, digits: int) -> int:
    lo = 10 ** (digits - 1)
    hi = 10**digits - 1
    return random_even_in_range(rng, lo, hi)


def build_targets(args: argparse.Namespace, rng: random.Random) -> list[int]:
    targets: list[int] = []
    if args.mode == "range":
        for _ in range(args.count):
            targets.append(random_even_in_range(rng, args.start, args.stop))
    elif args.mode == "digits":
        for _ in range(args.count):
            targets.append(random_even_digits(rng, args.digits))
    elif args.mode == "boundary":
        base = args.start if args.start else 4_000_000_000_000_000_000
        offsets = [0, 2, 4, 6, 8, 10, 12, 14, 30, 210, 2310, 30030, 510510, 9699690]
        for off in offsets:
            n = base + off
            if n % 2:
                n += 1
            targets.append(n)
        for _ in range(max(0, args.count - len(targets))):
            targets.append(random_even_in_range(rng, base, base + args.span))
    else:
        raise ValueError(args.mode)

    seen = set()
    unique = []
    for n in targets:
        if n not in seen:
            unique.append(n)
            seen.add(n)
    return unique


def write_report(path: Path, metrics: dict) -> None:
    lines = [
        "# Huge random Goldbach probe",
        "",
        f"Mode: `{metrics['mode']}`",
        f"Targets: {metrics['target_count']}",
        f"Prime p-limit: {metrics['p_limit']:,}",
        f"Found: {metrics['found_count']}",
        f"Suspicious: {metrics['suspicious_count']}",
        f"Seconds: {metrics['seconds']:.3f}",
        "",
        "## Summary",
        "",
        f"- Smallest p found: {metrics['smallest_p_found']}",
        f"- Largest p found: {metrics['largest_p_found']}",
        f"- Median p checks: {metrics['median_p_checks']}",
        f"- Max p checks: {metrics['max_p_checks']}",
        "",
        "## Suspicious",
        "",
    ]
    suspicious = [row for row in metrics["results"] if row["status"] != "found"]
    if not suspicious:
        lines.append("No suspicious targets in this batch.")
    else:
        for row in suspicious:
            lines.append(f"- n={row['n']} no pair found up to p={row['p_limit']:,} after {row['p_checks']:,} checks.")

    lines += [
        "",
        "## First results",
        "",
        "| n | status | p | q digits | p checks | proof |",
        "|---:|---|---:|---:|---:|---|",
    ]
    for row in metrics["results"][:80]:
        lines.append(
            f"| {row['n']} | {row['status']} | {row.get('p', '')} | "
            f"{row.get('q_digits', '')} | {row['p_checks']} | {row['proof_level']} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def median(values: list[int]) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    mid = len(values) // 2
    if len(values) % 2:
        return float(values[mid])
    return (values[mid - 1] + values[mid]) / 2


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe huge random even numbers for Goldbach partitions.")
    parser.add_argument("--mode", choices=["range", "digits", "boundary"], default="boundary")
    parser.add_argument("--start", type=int, default=4_000_000_000_000_000_000)
    parser.add_argument("--stop", type=int, default=18_000_000_000_000_000_000)
    parser.add_argument("--span", type=int, default=1_000_000_000_000_000_000)
    parser.add_argument("--digits", type=int, default=100)
    parser.add_argument("--count", type=int, default=1000)
    parser.add_argument("--p-limit", type=int, default=2_000_000)
    parser.add_argument("--mr-rounds", type=int, default=24)
    parser.add_argument("--seed", type=int, default=1742)
    parser.add_argument("--out-dir", type=Path, default=OUT)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(args.seed)

    t0 = time.perf_counter()
    primes = sieve(args.p_limit)
    targets = build_targets(args, rng)
    results = [find_goldbach_pair(n, primes, rng, args.mr_rounds) for n in targets]
    seconds = time.perf_counter() - t0

    found = [row for row in results if row["status"] == "found"]
    p_values = [row["p"] for row in found]
    check_values = [row["p_checks"] for row in results]
    metrics = {
        "mode": args.mode,
        "start": args.start,
        "stop": args.stop,
        "span": args.span,
        "digits": args.digits,
        "target_count": len(targets),
        "p_limit": args.p_limit,
        "prime_count": len(primes),
        "mr_rounds": args.mr_rounds,
        "seed": args.seed,
        "seconds": seconds,
        "found_count": len(found),
        "suspicious_count": len(results) - len(found),
        "smallest_p_found": min(p_values) if p_values else None,
        "largest_p_found": max(p_values) if p_values else None,
        "median_p_checks": median(check_values),
        "max_p_checks": max(check_values) if check_values else 0,
        "results": results,
    }

    stamp = time.strftime("%Y%m%d_%H%M%S")
    json_path = args.out_dir / f"goldbach_huge_probe_{args.mode}_{stamp}.json"
    md_path = args.out_dir / f"goldbach_huge_probe_{args.mode}_{stamp}.md"
    json_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    write_report(md_path, metrics)

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(f"targets={len(targets)} found={len(found)} suspicious={len(results)-len(found)}")
    print(f"largest_p={metrics['largest_p_found']} median_checks={metrics['median_p_checks']} max_checks={metrics['max_p_checks']}")
    print(f"seconds={seconds:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
