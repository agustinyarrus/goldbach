#!/usr/bin/env python3
"""
Goldbach NASA-30+ Lab

This does not prove the Goldbach conjecture globally. It attacks it like a
computational lab: full counterexample sweep up to a limit, exact audits for
suspicious values, independent primality witnesses, wild analysis missions,
and evidence exports.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable

try:
    import numpy as np
except ImportError:
    np = None


TWIN_PRIME_CONSTANT = 0.6601618158468696
MILLER_RABIN_BASES_64 = (2, 325, 9375, 28178, 450775, 9780504, 1795265022)
SMALL_PRIME_WITNESSES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


@dataclass
class MissionResult:
    mission: int
    title: str
    finding: str
    payload: object


@dataclass
class Context:
    limit: int
    export_dir: Path
    top: int
    sample_size: int
    is_prime: bytearray
    is_prime_ext: bytearray
    primes: list[int]
    counts: list[int]
    evens: list[int]
    sample_evens: list[int]
    focus_evens: list[int]
    twin_flags: bytearray
    sophie_flags: bytearray
    safe_flags: bytearray
    mersenne_flags: bytearray
    pair_cache: dict[int, list[tuple[int, int]]] = field(default_factory=dict)
    factor_cache: dict[int, list[int]] = field(default_factory=dict)
    semiprime_cache: dict[int, bool] = field(default_factory=dict)

    def pairs(self, n: int) -> list[tuple[int, int]]:
        if n not in self.pair_cache:
            out: list[tuple[int, int]] = []
            half = n // 2
            for p in self.primes:
                if p > half:
                    break
                if self.is_prime[n - p]:
                    out.append((p, n - p))
            self.pair_cache[n] = out
        return self.pair_cache[n]


def sieve(n: int) -> tuple[bytearray, list[int]]:
    flags = bytearray(b"\x01") * (n + 1)
    if n >= 0:
        flags[0] = 0
    if n >= 1:
        flags[1] = 0
    root = math.isqrt(n)
    for p in range(2, root + 1):
        if flags[p]:
            start = p * p
            flags[start : n + 1 : p] = b"\x00" * (((n - start) // p) + 1)
    primes = [i for i in range(2, n + 1) if flags[i]]
    return flags, primes


def is_prime_witness(n: int) -> bool:
    if n < 2:
        return False
    for p in SMALL_PRIME_WITNESSES:
        if n % p == 0:
            return n == p

    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2

    for a in MILLER_RABIN_BASES_64:
        if a % n == 0:
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


def fft(values: list[complex], invert: bool = False) -> None:
    n = len(values)
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j ^= bit
        if i < j:
            values[i], values[j] = values[j], values[i]

    length = 2
    while length <= n:
        angle = 2.0 * math.pi / length * (1 if invert else -1)
        wlen = complex(math.cos(angle), math.sin(angle))
        half = length // 2
        for i in range(0, n, length):
            w = 1 + 0j
            for k in range(i, i + half):
                u = values[k]
                v = values[k + half] * w
                values[k] = u + v
                values[k + half] = u - v
                w *= wlen
        length <<= 1

    if invert:
        inv_n = 1.0 / n
        for i in range(n):
            values[i] *= inv_n


def goldbach_counts_by_fft(limit: int, is_prime: bytearray, primes: list[int]) -> list[int]:
    size = 1
    while size <= 2 * limit:
        size <<= 1

    if np is not None:
        signal = np.zeros(size, dtype=np.float64)
        signal[np.array(primes, dtype=np.int64)] = 1.0
        spectrum = np.fft.rfft(signal)
        convolution = np.fft.irfft(spectrum * spectrum, n=size)
        ordered = np.rint(convolution[: limit + 1]).astype(np.int64)

        counts = [0] * (limit + 1)
        for n in range(4, limit + 1, 2):
            diagonal = 1 if is_prime[n // 2] else 0
            counts[n] = int((ordered[n] + diagonal) // 2)
        return counts

    spectrum = [0j] * size
    for p in primes:
        spectrum[p] = 1 + 0j
    fft(spectrum, invert=False)
    for i in range(size):
        spectrum[i] *= spectrum[i]
    fft(spectrum, invert=True)

    counts = [0] * (limit + 1)
    for n in range(4, limit + 1, 2):
        ordered = int(round(spectrum[n].real))
        diagonal = 1 if is_prime[n // 2] else 0
        counts[n] = (ordered + diagonal) // 2
    return counts


def choose_sample(evens: list[int], sample_size: int) -> list[int]:
    if len(evens) <= sample_size:
        return evens[:]
    if sample_size <= 1:
        return [evens[0]]
    step = (len(evens) - 1) / (sample_size - 1)
    sampled = {evens[int(round(i * step))] for i in range(sample_size)}
    return sorted(sampled)


def build_special_prime_flags(limit: int, is_prime_ext: bytearray) -> tuple[bytearray, bytearray, bytearray, bytearray]:
    twin = bytearray(limit + 1)
    sophie = bytearray(limit + 1)
    safe = bytearray(limit + 1)
    mersenne = bytearray(limit + 1)
    ext_limit = len(is_prime_ext) - 1

    for p in range(2, limit + 1):
        if not is_prime_ext[p]:
            continue
        if (p >= 2 and p + 2 <= ext_limit and is_prime_ext[p + 2]) or (p >= 4 and is_prime_ext[p - 2]):
            twin[p] = 1
        if 2 * p + 1 <= ext_limit and is_prime_ext[2 * p + 1]:
            sophie[p] = 1
        if p > 2 and is_prime_ext[(p - 1) // 2]:
            safe[p] = 1
        if (p + 1) & p == 0:
            mersenne[p] = 1
    return twin, sophie, safe, mersenne


def choose_focus_evens(evens: list[int], counts: list[int], sample: list[int], top: int) -> list[int]:
    threshold = 1000 if evens and evens[-1] >= 1000 else 4
    candidates = [n for n in evens if n >= threshold]
    weak = sorted(candidates, key=lambda n: (counts[n], n))[: top * 4]
    strong = sorted(evens, key=lambda n: (-counts[n], n))[: top * 3]

    records: list[int] = []
    best = -1
    for n in evens:
        if counts[n] > best:
            records.append(n)
            best = counts[n]

    focus = set(weak + strong + records[-top * 2 :] + sample[: min(100, len(sample))])
    return sorted(focus)


def unique_prime_factors(ctx: Context, n: int) -> list[int]:
    if n in ctx.factor_cache:
        return ctx.factor_cache[n]
    original = n
    factors: list[int] = []
    for p in ctx.primes:
        if p * p > n:
            break
        if n % p == 0:
            factors.append(p)
            while n % p == 0:
                n //= p
    if n > 1:
        factors.append(n)
    ctx.factor_cache[original] = factors
    return factors


def hardy_littlewood_expected(ctx: Context, n: int) -> float:
    if n < 6:
        return float(max(1, ctx.counts[n]))
    expected = TWIN_PRIME_CONSTANT * n / (math.log(n) ** 2)
    for p in unique_prime_factors(ctx, n):
        if p > 2:
            expected *= (p - 1) / (p - 2)
    return expected


def direct_count(ctx: Context, n: int) -> int:
    return len(ctx.pairs(n))


def direct_count_by_witness(n: int) -> int:
    if n < 4 or n % 2 == 1:
        return 0
    total = 1 if is_prime_witness(n - 2) else 0
    for p in range(3, n // 2 + 1, 2):
        if is_prime_witness(p) and is_prime_witness(n - p):
            total += 1
    return total


def avg(values: Iterable[float]) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    data = sorted(values)
    pos = (len(data) - 1) * p
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return float(data[lo])
    return float(data[lo] + (data[hi] - data[lo]) * (pos - lo))


def pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 2:
        return 0.0
    mean_x = avg(xs)
    mean_y = avg(ys)
    dx = [x - mean_x for x in xs]
    dy = [y - mean_y for y in ys]
    denom = math.sqrt(sum(x * x for x in dx) * sum(y * y for y in dy))
    if denom == 0.0:
        return 0.0
    return sum(x * y for x, y in zip(dx, dy)) / denom


def shannon_entropy(counter: Counter) -> float:
    total = sum(counter.values())
    if total == 0:
        return 0.0
    entropy = 0.0
    for count in counter.values():
        p = count / total
        entropy -= p * math.log2(p)
    return entropy


def nearest_prime_distance(ctx: Context, x: int) -> int | None:
    for d in range(0, max(x, ctx.limit - x) + 1):
        left = x - d
        right = x + d
        if left >= 2 and ctx.is_prime[left]:
            return d
        if right <= ctx.limit and ctx.is_prime[right]:
            return d
    return None


def is_semiprime(ctx: Context, n: int) -> bool:
    if n in ctx.semiprime_cache:
        return ctx.semiprime_cache[n]
    if n < 4:
        ctx.semiprime_cache[n] = False
        return False
    tmp = n
    factors = 0
    for p in ctx.primes:
        if p * p > tmp:
            break
        while tmp % p == 0:
            factors += 1
            tmp //= p
            if factors > 2:
                ctx.semiprime_cache[n] = False
                return False
    if tmp > 1:
        factors += 1
    ctx.semiprime_cache[n] = factors == 2
    return ctx.semiprime_cache[n]


def nontrivial_evens(ctx: Context, values: Iterable[int], floor: int = 1000) -> list[int]:
    threshold = floor if ctx.limit >= floor else 4
    filtered = [n for n in values if n >= threshold]
    return filtered if filtered else list(values)


def mission_01_counterexample_sweep(ctx: Context) -> MissionResult:
    zeros = [n for n in ctx.evens if ctx.counts[n] == 0]
    weakest = min(ctx.evens, key=lambda n: (ctx.counts[n], n))
    serious = nontrivial_evens(ctx, ctx.evens)
    weakest_serious = min(serious, key=lambda n: (ctx.counts[n], n))
    strongest = max(ctx.evens, key=lambda n: (ctx.counts[n], -n))
    if zeros:
        finding = f"RED ALERT: {len(zeros)} candidate counterexamples found; first={zeros[0]}."
    else:
        finding = (
            f"No counterexamples up to {ctx.limit}; weakest={weakest} with {ctx.counts[weakest]} pairs; "
            f"weakest>=1000={weakest_serious} with {ctx.counts[weakest_serious]}."
        )
    return MissionResult(
        1,
        "Full counterexample radar",
        finding,
        {
            "zero_count": len(zeros),
            "first_zeros": zeros[: ctx.top],
            "weakest": {"n": weakest, "pairs": ctx.counts[weakest]},
            "weakest_nontrivial": {"n": weakest_serious, "pairs": ctx.counts[weakest_serious]},
            "strongest": {"n": strongest, "pairs": ctx.counts[strongest]},
        },
    )


def mission_02_exact_audit(ctx: Context) -> MissionResult:
    weak = sorted(nontrivial_evens(ctx, ctx.evens), key=lambda n: (ctx.counts[n], n))[: ctx.top]
    strong = sorted(ctx.evens, key=lambda n: (-ctx.counts[n], n))[: ctx.top]
    targets = sorted(set([4] + weak + strong + ctx.focus_evens[: ctx.top]))
    mismatches = []
    audits = []
    for n in targets:
        exact = direct_count(ctx, n)
        audits.append({"n": n, "fft": ctx.counts[n], "exact": exact})
        if exact != ctx.counts[n]:
            mismatches.append({"n": n, "fft": ctx.counts[n], "exact": exact})
    finding = (
        f"Exact audit clean on {len(targets)} suspicious evens."
        if not mismatches
        else f"FFT mismatch on {len(mismatches)} values; trust exact payload."
    )
    return MissionResult(2, "Forensic exact-count audit", finding, {"mismatches": mismatches, "audits": audits})


def mission_03_weakest_links(ctx: Context) -> MissionResult:
    threshold = 1000 if ctx.limit >= 1000 else 4
    candidates = [n for n in ctx.evens if n >= threshold]
    weakest = sorted(candidates, key=lambda n: (ctx.counts[n], n))[: ctx.top]
    payload = [{"n": n, "pairs": ctx.counts[n], "mod30": n % 30, "mod210": n % 210} for n in weakest]
    finding = f"Weakest above {threshold}: {weakest[0]} with {ctx.counts[weakest[0]]} pairs."
    return MissionResult(3, "Weak-link hunter", finding, payload)


def mission_04_strongest_links(ctx: Context) -> MissionResult:
    strongest = sorted(ctx.evens, key=lambda n: (-ctx.counts[n], n))[: ctx.top]
    payload = [{"n": n, "pairs": ctx.counts[n], "mod30": n % 30, "mod210": n % 210} for n in strongest]
    finding = f"Strongest signal: {strongest[0]} with {ctx.counts[strongest[0]]} pairs."
    return MissionResult(4, "Supernova hunter", finding, payload)


def mission_05_record_breakers(ctx: Context) -> MissionResult:
    records = []
    best = -1
    for n in ctx.evens:
        if ctx.counts[n] > best:
            best = ctx.counts[n]
            records.append({"n": n, "pairs": best})
    finding = f"{len(records)} record-breakers found; last record {records[-1]['n']} -> {records[-1]['pairs']} pairs."
    return MissionResult(5, "Record-breaker timeline", finding, {"last_records": records[-ctx.top :], "record_count": len(records)})


def mission_06_scale_buckets(ctx: Context) -> MissionResult:
    edges = [4]
    p = 10
    while p < ctx.limit:
        edges.append(p)
        p *= 10
    edges.append(ctx.limit + 2)
    edges = sorted(set(edges))

    buckets = []
    for lo, hi in zip(edges, edges[1:]):
        vals = [ctx.counts[n] for n in ctx.evens if lo <= n < hi]
        if vals:
            buckets.append(
                {
                    "range": f"[{lo},{hi})",
                    "min": min(vals),
                    "median": statistics.median(vals),
                    "mean": avg(vals),
                    "max": max(vals),
                }
            )
    finding = f"Scale floor rises from {buckets[0]['min']} to {buckets[-1]['min']} across buckets."
    return MissionResult(6, "Scale-pressure chamber", finding, buckets)


def mission_07_hardy_littlewood(ctx: Context) -> MissionResult:
    ratios = []
    for n in ctx.sample_evens:
        expected = hardy_littlewood_expected(ctx, n)
        ratios.append((ctx.counts[n] / expected if expected else 0.0, n, expected))
    ratio_values = [r[0] for r in ratios]
    low = sorted(ratios, key=lambda x: x[0])[: ctx.top]
    high = sorted(ratios, key=lambda x: -x[0])[: ctx.top]
    finding = f"HL median actual/expected={statistics.median(ratio_values):.3f} on {len(ratios)} sampled evens."
    return MissionResult(
        7,
        "Hardy-Littlewood lie detector",
        finding,
        {
            "median_ratio": statistics.median(ratio_values),
            "mean_ratio": avg(ratio_values),
            "lowest": [{"n": n, "ratio": r, "expected": e, "actual": ctx.counts[n]} for r, n, e in low],
            "highest": [{"n": n, "ratio": r, "expected": e, "actual": ctx.counts[n]} for r, n, e in high],
        },
    )


def mission_08_hl_outlier_lab(ctx: Context) -> MissionResult:
    scored = []
    for n in nontrivial_evens(ctx, ctx.sample_evens):
        expected = hardy_littlewood_expected(ctx, n)
        residual = ctx.counts[n] - expected
        scored.append((residual, n, expected))
    cold = sorted(scored, key=lambda x: x[0])[: ctx.top]
    hot = sorted(scored, key=lambda x: -x[0])[: ctx.top]
    finding = f"Coldest sampled residual: {cold[0][1]} ({cold[0][0]:+.2f}); hottest: {hot[0][1]} ({hot[0][0]:+.2f})."
    return MissionResult(
        8,
        "Asymptotic anomaly trap",
        finding,
        {
            "cold": [{"n": n, "residual": r, "expected": e, "actual": ctx.counts[n]} for r, n, e in cold],
            "hot": [{"n": n, "residual": r, "expected": e, "actual": ctx.counts[n]} for r, n, e in hot],
        },
    )


def mission_09_mod30(ctx: Context) -> MissionResult:
    groups: dict[int, list[int]] = defaultdict(list)
    for n in ctx.evens:
        groups[n % 30].append(ctx.counts[n])
    rows = [
        {"mod30": r, "mean": avg(vals), "median": statistics.median(vals), "min": min(vals), "max": max(vals), "n": len(vals)}
        for r, vals in sorted(groups.items())
    ]
    ranked = sorted(rows, key=lambda x: x["mean"], reverse=True)
    finding = f"Best mod30 band={ranked[0]['mod30']} mean={ranked[0]['mean']:.2f}; weakest={ranked[-1]['mod30']} mean={ranked[-1]['mean']:.2f}."
    return MissionResult(9, "Modulo-30 gravity well", finding, {"ranking": ranked})


def mission_10_mod210(ctx: Context) -> MissionResult:
    groups: dict[int, list[int]] = defaultdict(list)
    for n in ctx.evens:
        groups[n % 210].append(ctx.counts[n])
    rows = [{"mod210": r, "mean": avg(vals), "min": min(vals), "max": max(vals), "n": len(vals)} for r, vals in groups.items()]
    ranked = sorted(rows, key=lambda x: x["mean"], reverse=True)
    finding = f"Wheel-210 top band={ranked[0]['mod210']} mean={ranked[0]['mean']:.2f}; bottom={ranked[-1]['mod210']} mean={ranked[-1]['mean']:.2f}."
    return MissionResult(10, "Modulo-210 alien wheel", finding, {"top": ranked[: ctx.top], "bottom": ranked[-ctx.top :]})


def mission_11_residue_heatmap(ctx: Context) -> MissionResult:
    heat = Counter()
    targets = sorted(set(ctx.sample_evens[: min(300, len(ctx.sample_evens))] + ctx.focus_evens))
    total_pairs = 0
    for n in targets:
        for p, q in ctx.pairs(n):
            a, b = sorted((p % 30, q % 30))
            heat[f"{a}+{b}"] += 1
            total_pairs += 1
    top = [{"residue_pair": k, "hits": v} for k, v in heat.most_common(ctx.top)]
    finding = f"Residue heatmap scanned {total_pairs} pairs; dominant channel={top[0]['residue_pair']}."
    return MissionResult(11, "Residue-pair heatmap", finding, {"top_channels": top, "target_evens": len(targets)})


def mission_12_chebyshev(ctx: Context) -> MissionResult:
    appearances = Counter()
    pair_total = 0
    for n in ctx.sample_evens:
        for p, q in ctx.pairs(n):
            pair_total += 1
            for x in (p, q):
                if x > 2:
                    appearances[x % 4] += 1
    mod1 = appearances[1]
    mod3 = appearances[3]
    ratio = mod3 / mod1 if mod1 else float("inf")
    finding = f"Chebyshev sample bias 4k+3 / 4k+1 = {ratio:.4f} across {pair_total} pairs."
    return MissionResult(12, "Chebyshev bias amplifier", finding, {"appearances": dict(appearances), "ratio_3_over_1": ratio})


def special_prime_mission(ctx: Context, number: int, title: str, flags: bytearray, label: str) -> MissionResult:
    hit_pairs = 0
    appearances = 0
    total_pairs = 0
    for n in ctx.sample_evens:
        for p, q in ctx.pairs(n):
            total_pairs += 1
            p_hit = bool(flags[p])
            q_hit = bool(flags[q])
            if p_hit or q_hit:
                hit_pairs += 1
            appearances += int(p_hit) + int(q_hit)
    rate = hit_pairs / total_pairs if total_pairs else 0.0
    finding = f"{label} touched {rate:.2%} of sampled pairs ({appearances} prime appearances)."
    return MissionResult(number, title, finding, {"hit_pair_rate": rate, "appearances": appearances, "sampled_pairs": total_pairs})


def mission_13_twin(ctx: Context) -> MissionResult:
    return special_prime_mission(ctx, 13, "Twin-prime fuel injector", ctx.twin_flags, "Twin primes")


def mission_14_sophie(ctx: Context) -> MissionResult:
    return special_prime_mission(ctx, 14, "Sophie-Germain reactor", ctx.sophie_flags, "Sophie Germain primes")


def mission_15_safe(ctx: Context) -> MissionResult:
    return special_prime_mission(ctx, 15, "Safe-prime shield test", ctx.safe_flags, "Safe primes")


def mission_16_mersenne(ctx: Context) -> MissionResult:
    return special_prime_mission(ctx, 16, "Mersenne needle detector", ctx.mersenne_flags, "Mersenne primes")


def mission_17_balanced_core(ctx: Context) -> MissionResult:
    rows = []
    for n in nontrivial_evens(ctx, ctx.focus_evens):
        pairs = ctx.pairs(n)
        if not pairs:
            continue
        best_gap = min(abs(q - p) for p, q in pairs)
        band = max(2.0, 0.05 * n)
        balanced = sum(1 for p, q in pairs if abs(q - p) <= band)
        rows.append({"n": n, "pairs": len(pairs), "best_gap": best_gap, "balanced_rate": balanced / len(pairs)})
    high = sorted(rows, key=lambda r: (-r["balanced_rate"], r["best_gap"]))[: ctx.top]
    low = sorted(rows, key=lambda r: (r["balanced_rate"], -r["best_gap"]))[: ctx.top]
    finding = f"Most balanced focus even={high[0]['n']} rate={high[0]['balanced_rate']:.2%}; hardest={low[0]['n']}."
    return MissionResult(17, "Central-balance collider", finding, {"most_balanced": high, "least_balanced": low})


def mission_18_lopsided_tail(ctx: Context) -> MissionResult:
    rows = []
    for n in nontrivial_evens(ctx, ctx.focus_evens):
        pairs = ctx.pairs(n)
        if not pairs:
            continue
        root = math.isqrt(n)
        extreme = sum(1 for p, q in pairs if p <= root or (q - p) >= 0.90 * n)
        max_gap = max(q - p for p, q in pairs)
        rows.append({"n": n, "pairs": len(pairs), "max_gap": max_gap, "lopsided_rate": extreme / len(pairs)})
    ranked = sorted(rows, key=lambda r: (-r["lopsided_rate"], -r["max_gap"]))[: ctx.top]
    finding = f"Most lopsided focus even={ranked[0]['n']} rate={ranked[0]['lopsided_rate']:.2%}."
    return MissionResult(18, "Tiny-giant pair detector", finding, ranked)


def mission_19_entropy(ctx: Context) -> MissionResult:
    rows = []
    for n in nontrivial_evens(ctx, ctx.focus_evens):
        pairs = ctx.pairs(n)
        if not pairs:
            continue
        residues = Counter(p % 30 for p, _ in pairs)
        entropy = shannon_entropy(residues)
        rows.append({"n": n, "pairs": len(pairs), "entropy_bits": entropy, "normalized": entropy / math.log2(30)})
    low = sorted(rows, key=lambda r: r["entropy_bits"])[: ctx.top]
    high = sorted(rows, key=lambda r: -r["entropy_bits"])[: ctx.top]
    finding = f"Residue entropy ranges {low[0]['entropy_bits']:.3f}..{high[0]['entropy_bits']:.3f} bits in focus set."
    return MissionResult(19, "Residue entropy chamber", finding, {"lowest": low, "highest": high})


def mission_20_center_gravity(ctx: Context) -> MissionResult:
    rows = []
    for n in nontrivial_evens(ctx, ctx.focus_evens):
        pairs = ctx.pairs(n)
        if not pairs:
            continue
        mean_lower = avg(p for p, _ in pairs)
        drift = 0.25 - (mean_lower / n)
        rows.append({"n": n, "pairs": len(pairs), "mean_lower_prime": mean_lower, "drift_from_uniform_quarter": drift})
    ranked = sorted(rows, key=lambda r: -abs(r["drift_from_uniform_quarter"]))[: ctx.top]
    finding = f"Max center-of-gravity drift in focus set: {ranked[0]['n']} drift={ranked[0]['drift_from_uniform_quarter']:.4f}."
    return MissionResult(20, "Center-of-gravity drift", finding, ranked)


def mission_21_midpoint_desert(ctx: Context) -> MissionResult:
    weak = sorted(nontrivial_evens(ctx, ctx.evens), key=lambda n: (ctx.counts[n], n))[: ctx.top * 3]
    rows = []
    for n in weak:
        d = nearest_prime_distance(ctx, n // 2)
        rows.append({"n": n, "pairs": ctx.counts[n], "midpoint": n // 2, "nearest_prime_distance": d})
    ranked = sorted(rows, key=lambda r: (-(r["nearest_prime_distance"] or 0), r["pairs"]))[: ctx.top]
    finding = f"Worst midpoint desert among weak evens: n={ranked[0]['n']} distance={ranked[0]['nearest_prime_distance']}."
    return MissionResult(21, "Midpoint prime-desert sonar", finding, ranked)


def mission_22_local_volatility(ctx: Context) -> MissionResult:
    values = [ctx.counts[n] for n in ctx.evens]
    window = min(25, max(5, len(values) // 20))
    threshold = 1000 if ctx.limit >= 1000 else 4
    scored = []
    for i, value in enumerate(values):
        n = ctx.evens[i]
        if n < threshold:
            continue
        lo = max(0, i - window)
        hi = min(len(values), i + window + 1)
        neighbors = values[lo:i] + values[i + 1 : hi]
        if len(neighbors) < 5:
            continue
        sd = statistics.pstdev(neighbors)
        if sd == 0:
            continue
        z = (value - avg(neighbors)) / sd
        scored.append((z, n, value))
    cold = sorted(scored, key=lambda x: x[0])[: ctx.top]
    hot = sorted(scored, key=lambda x: -x[0])[: ctx.top]
    finding = f"Local volatility found coldest z={cold[0][0]:.2f} at {cold[0][1]}, hottest z={hot[0][0]:.2f} at {hot[0][1]}."
    return MissionResult(
        22,
        "Local volatility seismograph",
        finding,
        {
            "cold": [{"n": n, "z": z, "pairs": v} for z, n, v in cold],
            "hot": [{"n": n, "z": z, "pairs": v} for z, n, v in hot],
        },
    )


def mission_23_spectral(ctx: Context) -> MissionResult:
    raw = [float(ctx.counts[n]) for n in ctx.evens]
    m = len(raw)
    if m < 8:
        return MissionResult(23, "Spectral comet scanner", "Not enough data for spectral scan.", {})
    slope = (raw[-1] - raw[0]) / max(1, m - 1)
    residual = [raw[i] - (raw[0] + slope * i) for i in range(m)]
    size = 1
    while size < m:
        size <<= 1
    data = [complex(x, 0.0) for x in residual] + [0j] * (size - m)
    fft(data, invert=False)
    amps = []
    for k in range(1, size // 2):
        period_numbers = (size / k) * 2.0
        if 4.0 <= period_numbers <= min(5000.0, float(ctx.limit)):
            amp = abs(data[k])
            amps.append((amp, k, period_numbers))
    if not amps:
        return MissionResult(23, "Spectral comet scanner", "No usable mid-frequency spectral bins.", {})
    top = sorted(amps, key=lambda x: -x[0])[: ctx.top]
    finding = f"Dominant residual period approx {top[0][2]:.2f} number-units (FFT bin {top[0][1]})."
    return MissionResult(
        23,
        "Spectral comet scanner",
        finding,
        [{"bin": k, "amplitude": amp, "period_in_numbers": period} for amp, k, period in top],
    )


def mission_24_autocorrelation(ctx: Context) -> MissionResult:
    raw = [float(ctx.counts[n]) for n in ctx.evens]
    m = len(raw)
    if m < 20:
        return MissionResult(24, "Autocorrelation wormhole", "Not enough data for autocorrelation.", {})
    slope = (raw[-1] - raw[0]) / max(1, m - 1)
    x = [raw[i] - (raw[0] + slope * i) for i in range(m)]
    mean = avg(x)
    x = [v - mean for v in x]
    denominator = sum(v * v for v in x)
    rows = []
    for lag in range(1, min(120, m // 2) + 1):
        numerator = sum(x[i] * x[i - lag] for i in range(lag, m))
        corr = numerator / denominator if denominator else 0.0
        rows.append({"lag_even_steps": lag, "period_in_numbers": 2 * lag, "corr": corr})
    ranked = sorted(rows, key=lambda r: -r["corr"])[: ctx.top]
    finding = f"Strongest autocorrelation period={ranked[0]['period_in_numbers']} with corr={ranked[0]['corr']:.4f}."
    return MissionResult(24, "Autocorrelation wormhole", finding, ranked)


def mission_25_stress_filter(ctx: Context) -> MissionResult:
    floor = max(11, math.isqrt(ctx.limit))
    hostile_flags = [ctx.twin_flags, ctx.sophie_flags, ctx.safe_flags, ctx.mersenne_flags]
    rows = []
    raw_targets = nontrivial_evens(ctx, ctx.focus_evens + ctx.sample_evens[: min(300, len(ctx.sample_evens))])
    possible_targets = [n for n in raw_targets if n >= 2 * floor + 4]
    targets = sorted(set(possible_targets if possible_targets else raw_targets))
    for n in targets:
        pairs = ctx.pairs(n)
        if not pairs:
            rows.append({"n": n, "pairs": 0, "survivors": 0, "survival_rate": 0.0})
            continue
        survivors = 0
        for p, q in pairs:
            banned = p < floor or q < floor or any(flag[p] or flag[q] for flag in hostile_flags)
            if not banned:
                survivors += 1
        rows.append({"n": n, "pairs": len(pairs), "survivors": survivors, "survival_rate": survivors / len(pairs)})
    ranked = sorted(rows, key=lambda r: (r["survival_rate"], r["survivors"], r["pairs"]))[: ctx.top]
    finding = f"Hostile filter floor={floor}; hardest survivor case n={ranked[0]['n']} survivors={ranked[0]['survivors']}."
    return MissionResult(25, "Anti-Goldbach stress filter", finding, ranked)


def mission_26_prime_gap_bridges(ctx: Context) -> MissionResult:
    gaps = []
    for a, b in zip(ctx.primes, ctx.primes[1:]):
        if b > ctx.limit:
            break
        bridge = a + b
        if bridge <= ctx.limit and bridge % 2 == 0:
            gaps.append({"left_prime": a, "right_prime": b, "gap": b - a, "bridge_even": bridge, "bridge_pairs": ctx.counts[bridge]})
    ranked = sorted(gaps, key=lambda r: (-r["gap"], r["bridge_pairs"]))[: ctx.top]
    finding = f"Largest prime desert bridge gap={ranked[0]['gap']} at even {ranked[0]['bridge_even']}."
    return MissionResult(26, "Prime-desert bridge test", finding, ranked)


def mission_27_semiprime_neighbors(ctx: Context) -> MissionResult:
    with_neighbor = []
    without_neighbor = []
    for n in ctx.sample_evens:
        target = with_neighbor if (is_semiprime(ctx, n - 1) or is_semiprime(ctx, n + 1)) else without_neighbor
        target.append(ctx.counts[n])
    mean_with = avg(with_neighbor)
    mean_without = avg(without_neighbor)
    finding = f"Semiprime-neighbor mean pairs: with={mean_with:.2f}, without={mean_without:.2f}."
    return MissionResult(
        27,
        "Semiprime neighbor resonance",
        finding,
        {
            "with_semiprime_neighbor": {"n": len(with_neighbor), "mean_pairs": mean_with},
            "without_semiprime_neighbor": {"n": len(without_neighbor), "mean_pairs": mean_without},
        },
    )


def mission_28_graph_hubs(ctx: Context) -> MissionResult:
    occurrences = Counter()
    total_pairs = 0
    targets = ctx.sample_evens[: min(500, len(ctx.sample_evens))]
    for n in targets:
        for p, q in ctx.pairs(n):
            occurrences[p] += 1
            occurrences[q] += 1
            total_pairs += 1
    hubs = [{"prime": p, "appearances": c} for p, c in occurrences.most_common(ctx.top)]
    finding = f"Goldbach graph sampled {total_pairs} edges; top hub prime={hubs[0]['prime']}."
    return MissionResult(28, "Goldbach graph hub radar", finding, hubs)


def mission_29_weakness_clusters(ctx: Context) -> MissionResult:
    values = [ctx.counts[n] for n in ctx.evens]
    threshold = percentile([float(v) for v in values], 0.10)
    runs = []
    current = []
    for n in ctx.evens:
        if ctx.counts[n] <= threshold:
            current.append(n)
        elif current:
            runs.append(current)
            current = []
    if current:
        runs.append(current)
    rows = [
        {
            "start": run[0],
            "end": run[-1],
            "length_evens": len(run),
            "min_pairs": min(ctx.counts[n] for n in run),
            "mean_pairs": avg(ctx.counts[n] for n in run),
        }
        for run in runs
    ]
    ranked = sorted(rows, key=lambda r: (-r["length_evens"], r["mean_pairs"]))[: ctx.top]
    finding = f"10th-percentile weakness threshold={threshold:.2f}; longest weak cluster length={ranked[0]['length_evens']}."
    return MissionResult(29, "Weakness-cluster telescope", finding, ranked)


def mission_30_independent_witness(ctx: Context) -> MissionResult:
    weak = sorted(nontrivial_evens(ctx, ctx.evens), key=lambda n: (ctx.counts[n], n))[: ctx.top]
    strong = sorted(ctx.evens, key=lambda n: (-ctx.counts[n], n))[: max(2, ctx.top // 2)]
    targets = sorted(set(weak + strong + ctx.focus_evens[: max(2, ctx.top // 2)]))
    mismatches = []
    audits = []
    for n in targets:
        witness = direct_count_by_witness(n)
        audits.append({"n": n, "fft_count": ctx.counts[n], "miller_rabin_count": witness})
        if witness != ctx.counts[n]:
            mismatches.append({"n": n, "fft_count": ctx.counts[n], "miller_rabin_count": witness})
    finding = (
        f"Independent Miller-Rabin audit clean on {len(targets)} high-risk evens."
        if not mismatches
        else f"Independent witness mismatch on {len(mismatches)} evens; investigate immediately."
    )
    return MissionResult(30, "Independent witness tribunal", finding, {"mismatches": mismatches, "audits": audits})


def mission_31_factor_boost(ctx: Context) -> MissionResult:
    rows = []
    xs = []
    ys = []
    for n in nontrivial_evens(ctx, ctx.sample_evens):
        booster = 1.0
        odd_factors = []
        for p in unique_prime_factors(ctx, n):
            if p > 2:
                booster *= (p - 1) / (p - 2)
                odd_factors.append(p)
        normalized_density = ctx.counts[n] * (math.log(n) ** 2) / max(1.0, TWIN_PRIME_CONSTANT * n)
        xs.append(booster)
        ys.append(normalized_density)
        rows.append(
            {
                "n": n,
                "pairs": ctx.counts[n],
                "odd_prime_factors": odd_factors,
                "booster": booster,
                "normalized_density": normalized_density,
            }
        )
    corr = pearson(xs, ys)
    top_boosters = sorted(rows, key=lambda r: (-r["booster"], -r["pairs"]))[: ctx.top]
    weakest_after_boost = sorted(rows, key=lambda r: (r["normalized_density"] / r["booster"], r["pairs"]))[: ctx.top]
    finding = f"Divisor booster correlation={corr:.3f}; strongest booster n={top_boosters[0]['n']} x{top_boosters[0]['booster']:.2f}."
    return MissionResult(
        31,
        "Divisor-booster gravity model",
        finding,
        {"correlation": corr, "top_boosters": top_boosters, "weak_after_boost": weakest_after_boost},
    )


def mission_32_window_floor(ctx: Context) -> MissionResult:
    evens = nontrivial_evens(ctx, ctx.evens)
    window_count = min(40, max(4, len(evens) // 500))
    window_size = max(1, len(evens) // window_count)
    rows = []
    for start in range(0, len(evens), window_size):
        window = evens[start : start + window_size]
        if not window:
            continue
        weakest = min(window, key=lambda n: (ctx.counts[n], n))
        strongest = max(window, key=lambda n: (ctx.counts[n], -n))
        rows.append(
            {
                "start": window[0],
                "end": window[-1],
                "weakest": weakest,
                "floor_pairs": ctx.counts[weakest],
                "strongest": strongest,
                "ceiling_pairs": ctx.counts[strongest],
                "mean_pairs": avg(ctx.counts[n] for n in window),
            }
        )
    dips = sorted(rows, key=lambda r: (r["floor_pairs"], -r["end"]))[: ctx.top]
    finding = f"Window floor scan: final floor={rows[-1]['floor_pairs']} pairs; worst nonlocal dip at {dips[0]['weakest']}."
    return MissionResult(32, "Sliding-floor pressure scan", finding, {"windows": rows, "worst_dips": dips})


def mission_30_exports(ctx: Context, previous: list[MissionResult]) -> MissionResult:
    ctx.export_dir.mkdir(parents=True, exist_ok=True)
    counts_path = ctx.export_dir / f"goldbach_counts_to_{ctx.limit}.csv"
    findings_path = ctx.export_dir / f"goldbach_nasa_plus_findings_to_{ctx.limit}.json"

    with counts_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["even", "goldbach_pairs", "mod30", "mod210"])
        writer.writeheader()
        for n in ctx.evens:
            writer.writerow({"even": n, "goldbach_pairs": ctx.counts[n], "mod30": n % 30, "mod210": n % 210})

    findings = [
        {"mission": r.mission, "title": r.title, "finding": r.finding, "payload": r.payload}
        for r in previous
    ]
    with findings_path.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "limit": ctx.limit,
                "sample_size": len(ctx.sample_evens),
                "focus_size": len(ctx.focus_evens),
                "missions": findings,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    mission_number = len(previous) + 1
    finding = f"Evidence exported: {counts_path.name} and {findings_path.name}."
    return MissionResult(mission_number, "Evidence package exporter", finding, {"counts_csv": str(counts_path), "findings_json": str(findings_path)})


MISSION_FUNCTIONS: list[Callable[[Context], MissionResult]] = [
    mission_01_counterexample_sweep,
    mission_02_exact_audit,
    mission_03_weakest_links,
    mission_04_strongest_links,
    mission_05_record_breakers,
    mission_06_scale_buckets,
    mission_07_hardy_littlewood,
    mission_08_hl_outlier_lab,
    mission_09_mod30,
    mission_10_mod210,
    mission_11_residue_heatmap,
    mission_12_chebyshev,
    mission_13_twin,
    mission_14_sophie,
    mission_15_safe,
    mission_16_mersenne,
    mission_17_balanced_core,
    mission_18_lopsided_tail,
    mission_19_entropy,
    mission_20_center_gravity,
    mission_21_midpoint_desert,
    mission_22_local_volatility,
    mission_23_spectral,
    mission_24_autocorrelation,
    mission_25_stress_filter,
    mission_26_prime_gap_bridges,
    mission_27_semiprime_neighbors,
    mission_28_graph_hubs,
    mission_29_weakness_clusters,
    mission_30_independent_witness,
    mission_31_factor_boost,
    mission_32_window_floor,
]


def build_context(limit: int, export_dir: Path, top: int, sample_size: int) -> Context:
    ext_limit = max(limit, 2 * limit + 1)
    is_prime_ext, primes_ext = sieve(ext_limit)
    is_prime = is_prime_ext[: limit + 1]
    primes = [p for p in primes_ext if p <= limit]
    counts = goldbach_counts_by_fft(limit, is_prime, primes)
    evens = list(range(4, limit + 1, 2))
    sample_evens = choose_sample(evens, sample_size)
    twin, sophie, safe, mersenne = build_special_prime_flags(limit, is_prime_ext)
    focus_evens = choose_focus_evens(evens, counts, sample_evens, top)
    return Context(
        limit=limit,
        export_dir=export_dir,
        top=top,
        sample_size=sample_size,
        is_prime=is_prime,
        is_prime_ext=is_prime_ext,
        primes=primes,
        counts=counts,
        evens=evens,
        sample_evens=sample_evens,
        focus_evens=focus_evens,
        twin_flags=twin,
        sophie_flags=sophie,
        safe_flags=safe,
        mersenne_flags=mersenne,
    )


def print_banner(limit: int) -> None:
    print("=" * 78)
    print("GOLDBACH NASA-30+ LAB")
    print("=" * 78)
    print(f"Mission: attack strong Goldbach computationally up to {limit:,}")
    print("Warning: finite computation can find counterexamples, not prove infinity.")
    print("=" * 78)


def fft_engine_name() -> str:
    return "NumPy native FFT" if np is not None else "pure Python FFT"


def main() -> int:
    parser = argparse.ArgumentParser(description="NASA-style Goldbach analysis lab.")
    parser.add_argument("--limit", type=int, default=200_000, help="Even search limit, inclusive.")
    parser.add_argument("--top", type=int, default=12, help="How many ranked findings to keep per mission.")
    parser.add_argument("--sample-size", type=int, default=1_500, help="Sample size for pair-level missions.")
    parser.add_argument(
        "--export-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "goldbach_nasa_output",
        help="Directory for CSV/JSON evidence exports.",
    )
    args = parser.parse_args()

    if args.limit < 4:
        raise SystemExit("--limit must be at least 4")
    if args.limit % 2 == 1:
        args.limit -= 1
    if args.top < 1:
        raise SystemExit("--top must be at least 1")
    if args.sample_size < 1:
        raise SystemExit("--sample-size must be at least 1")

    start = time.perf_counter()
    print_banner(args.limit)
    print(f"[BOOT] Building prime radar and FFT Goldbach convolution ({fft_engine_name()})...")
    ctx = build_context(args.limit, args.export_dir, args.top, args.sample_size)
    print(
        f"[BOOT] primes={len(ctx.primes):,}, evens={len(ctx.evens):,}, "
        f"sample={len(ctx.sample_evens):,}, focus={len(ctx.focus_evens):,}"
    )

    results: list[MissionResult] = []
    for fn in MISSION_FUNCTIONS:
        result = fn(ctx)
        results.append(result)
        print(f"[{result.mission:02d}] {result.title}: {result.finding}")

    export_result = mission_30_exports(ctx, results)
    results.append(export_result)
    print(f"[{export_result.mission:02d}] {export_result.title}: {export_result.finding}")

    elapsed = time.perf_counter() - start
    zeros = [n for n in ctx.evens if ctx.counts[n] == 0]
    print("=" * 78)
    if zeros:
        print(f"RED ALERT: possible counterexample candidates: {zeros[: args.top]}")
        print("Run again with higher audit or independent code before believing it.")
    else:
        print(f"RESULT: no Goldbach counterexample found up to {ctx.limit:,}.")
    print(f"Runtime: {elapsed:.2f}s")
    print(f"Exports: {export_result.payload['counts_csv']}")
    print(f"         {export_result.payload['findings_json']}")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
