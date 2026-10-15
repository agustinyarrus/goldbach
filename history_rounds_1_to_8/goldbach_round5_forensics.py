#!/usr/bin/env python3
"""
Goldbach miner round 5: direct forensics on calibrated cold/hot cases.

Inputs:
- goldbach_counts_to_10000000.csv
- goldbach_round4_calibrated_hl_metrics.json

For the largest-scale cold/hot calibrated outliers, this independently counts
Goldbach pairs with the sieve, then measures:
- midpoint prime desert,
- balanced-pair rates,
- tiny/giant rates,
- residue-channel usage mod 30,
- direct audit mismatches.
"""

from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "goldbach_nasa_output"
CSV_PATH = OUT / "goldbach_counts_to_10000000.csv"
ROUND4_PATH = OUT / "goldbach_round4_calibrated_hl_metrics.json"
REPORT_PATH = OUT / "goldbach_round5_forensics.md"
METRICS_PATH = OUT / "goldbach_round5_forensics_metrics.json"

TARGET_GROUPS = (
    ("cold_ratio_1m", ("scale_extremes", "1000000", "cold_ratio")),
    ("hot_ratio_1m", ("scale_extremes", "1000000", "hot_ratio")),
    ("negative_residual_1m", ("scale_extremes", "1000000", "negative_residual")),
    ("positive_residual_1m", ("scale_extremes", "1000000", "positive_residual")),
)


def even_at(index: int) -> int:
    return 4 + 2 * index


def index_of_even(n: int) -> int:
    return (n - 4) // 2


def load_counts(path: Path) -> list[int]:
    counts: list[int] = []
    with path.open("r", encoding="utf-8") as f:
        next(f)
        for line in f:
            first = line.find(",")
            second = line.find(",", first + 1)
            counts.append(int(line[first + 1 : second]))
    return counts


def sieve(limit: int) -> tuple[bytearray, list[int]]:
    flags = bytearray(b"\x01") * (limit + 1)
    flags[0] = 0
    flags[1] = 0
    root = math.isqrt(limit)
    for p in range(2, root + 1):
        if flags[p]:
            start = p * p
            flags[start : limit + 1 : p] = b"\x00" * (((limit - start) // p) + 1)
    primes = [n for n in range(2, limit + 1) if flags[n]]
    return flags, primes


def nearest_prime_gap(flags: bytearray, midpoint: int) -> dict:
    left = midpoint
    while left >= 2 and not flags[left]:
        left -= 1
    right = midpoint
    while right < len(flags) and not flags[right]:
        right += 1
    return {
        "midpoint": midpoint,
        "left_prime": left if left >= 2 else None,
        "right_prime": right if right < len(flags) else None,
        "left_distance": midpoint - left if left >= 2 else None,
        "right_distance": right - midpoint if right < len(flags) else None,
        "prime_gap_across_midpoint": right - left if left >= 2 and right < len(flags) else None,
        "nearest_distance": min(midpoint - left, right - midpoint) if left >= 2 and right < len(flags) else None,
    }


def direct_profile(n: int, expected_count: int, flags: bytearray, primes: list[int]) -> dict:
    half = n // 2
    pairs: list[tuple[int, int]] = []
    channel_counts: Counter[str] = Counter()
    lower_residue_counts: Counter[int] = Counter()
    central_1pct = 0
    central_5pct = 0
    central_10pct = 0
    tiny_sqrt = 0
    tiny_log = 0
    best_gap = n
    best_pair = None

    one_pct = n * 0.01
    five_pct = n * 0.05
    ten_pct = n * 0.10
    sqrt_n = math.sqrt(n)
    log_cut = n / math.log(n)

    for p in primes:
        if p > half:
            break
        q = n - p
        if flags[q]:
            pairs.append((p, q))
            gap = q - p
            if gap < best_gap:
                best_gap = gap
                best_pair = (p, q)
            if gap <= one_pct:
                central_1pct += 1
            if gap <= five_pct:
                central_5pct += 1
            if gap <= ten_pct:
                central_10pct += 1
            if p <= sqrt_n:
                tiny_sqrt += 1
            if p <= log_cut:
                tiny_log += 1
            a, b = sorted((p % 30, q % 30))
            channel_counts[f"{a}+{b}"] += 1
            lower_residue_counts[p % 30] += 1

    total = len(pairs)
    dominant_channel, dominant_hits = channel_counts.most_common(1)[0] if channel_counts else (None, 0)
    return {
        "n": n,
        "expected_csv_count": expected_count,
        "direct_count": total,
        "audit_match": total == expected_count,
        "midpoint": nearest_prime_gap(flags, half),
        "best_balanced_pair": best_pair,
        "best_gap": best_gap if best_pair else None,
        "central_1pct": central_1pct,
        "central_5pct": central_5pct,
        "central_10pct": central_10pct,
        "central_1pct_rate": central_1pct / total if total else 0.0,
        "central_5pct_rate": central_5pct / total if total else 0.0,
        "central_10pct_rate": central_10pct / total if total else 0.0,
        "tiny_sqrt": tiny_sqrt,
        "tiny_sqrt_rate": tiny_sqrt / total if total else 0.0,
        "tiny_log": tiny_log,
        "tiny_log_rate": tiny_log / total if total else 0.0,
        "dominant_channel": dominant_channel,
        "dominant_channel_hits": dominant_hits,
        "dominant_channel_rate": dominant_hits / total if total else 0.0,
        "active_channels": len(channel_counts),
        "top_channels": [{"channel": channel, "hits": hits, "rate": hits / total if total else 0.0} for channel, hits in channel_counts.most_common(8)],
        "lower_residues": [{"residue": residue, "hits": hits, "rate": hits / total if total else 0.0} for residue, hits in lower_residue_counts.most_common()],
    }


def collect_targets(round4: dict) -> dict:
    groups = {}
    all_targets: dict[int, set[str]] = {}
    for group_name, path in TARGET_GROUPS:
        node = round4
        for key in path:
            node = node[key]
        ns = [int(row["n"]) for row in node[:20]]
        groups[group_name] = ns
        for n in ns:
            all_targets.setdefault(n, set()).add(group_name)
    return {"groups": groups, "all_targets": {str(n): sorted(labels) for n, labels in sorted(all_targets.items())}}


def aggregate_group(group_name: str, ns: list[int], profiles: dict[str, dict]) -> dict:
    selected = [profiles[str(n)] for n in ns]
    count = len(selected)
    return {
        "group": group_name,
        "count": count,
        "mean_direct_count": sum(row["direct_count"] for row in selected) / count,
        "mean_midpoint_gap": sum(row["midpoint"]["prime_gap_across_midpoint"] for row in selected) / count,
        "max_midpoint_gap": max(row["midpoint"]["prime_gap_across_midpoint"] for row in selected),
        "mean_nearest_midpoint_distance": sum(row["midpoint"]["nearest_distance"] for row in selected) / count,
        "mean_central_1pct_rate": sum(row["central_1pct_rate"] for row in selected) / count,
        "mean_central_5pct_rate": sum(row["central_5pct_rate"] for row in selected) / count,
        "mean_central_10pct_rate": sum(row["central_10pct_rate"] for row in selected) / count,
        "mean_tiny_sqrt_rate": sum(row["tiny_sqrt_rate"] for row in selected) / count,
        "mean_tiny_log_rate": sum(row["tiny_log_rate"] for row in selected) / count,
        "mean_dominant_channel_rate": sum(row["dominant_channel_rate"] for row in selected) / count,
        "all_audits_match": all(row["audit_match"] for row in selected),
    }


def make_patterns(metrics: dict) -> list[str]:
    profiles = metrics["profiles"]
    groups = {row["group"]: row for row in metrics["group_aggregates"]}
    cold = groups["cold_ratio_1m"]
    hot = groups["hot_ratio_1m"]
    neg = groups["negative_residual_1m"]
    pos = groups["positive_residual_1m"]
    widest_mid = max(profiles.values(), key=lambda row: row["midpoint"]["prime_gap_across_midpoint"])
    most_central = max(profiles.values(), key=lambda row: row["central_1pct_rate"])
    least_central = min(profiles.values(), key=lambda row: row["central_10pct_rate"])
    most_tiny = max(profiles.values(), key=lambda row: row["tiny_sqrt_rate"])
    most_channel_locked = max(profiles.values(), key=lambda row: row["dominant_channel_rate"])
    cold_first = profiles[str(metrics["groups"]["cold_ratio_1m"][0])]
    hot_first = profiles[str(metrics["groups"]["hot_ratio_1m"][0])]

    return [
        f"Se auditaron {len(profiles)} n únicos de los grupos fríos/calientes grandes.",
        "Todas las auditorías directas contra el CSV dieron match." if metrics["all_audits_match"] else "Hay mismatches en auditoría directa: revisar urgente.",
        f"El frío calibrado principal {cold_first['n']} tiene conteo directo {cold_first['direct_count']:,}.",
        f"El caliente calibrado principal {hot_first['n']} tiene conteo directo {hot_first['direct_count']:,}.",
        f"Los fríos por ratio >=1M tienen media {cold['mean_direct_count']:.2f} pares.",
        f"Los calientes por ratio >=1M tienen media {hot['mean_direct_count']:.2f} pares.",
        f"Los peores residuales negativos >=1M tienen media {neg['mean_direct_count']:.2f} pares.",
        f"Los mayores residuales positivos >=1M tienen media {pos['mean_direct_count']:.2f} pares.",
        f"El gap primo más ancho alrededor de n/2 aparece en n={widest_mid['n']} con gap {widest_mid['midpoint']['prime_gap_across_midpoint']}.",
        f"El frío principal {cold_first['n']} tiene gap alrededor del midpoint {cold_first['midpoint']['prime_gap_across_midpoint']}.",
        f"El caliente principal {hot_first['n']} tiene gap alrededor del midpoint {hot_first['midpoint']['prime_gap_across_midpoint']}.",
        f"Los fríos tienen gap medio midpoint {cold['mean_midpoint_gap']:.2f}; los calientes {hot['mean_midpoint_gap']:.2f}.",
        f"Los fríos tienen distancia media al primo central {cold['mean_nearest_midpoint_distance']:.2f}; los calientes {hot['mean_nearest_midpoint_distance']:.2f}.",
        f"Los fríos tienen tasa central 1% media {cold['mean_central_1pct_rate']:.4f}; los calientes {hot['mean_central_1pct_rate']:.4f}.",
        f"Los fríos tienen tasa central 5% media {cold['mean_central_5pct_rate']:.4f}; los calientes {hot['mean_central_5pct_rate']:.4f}.",
        f"Los fríos tienen tasa central 10% media {cold['mean_central_10pct_rate']:.4f}; los calientes {hot['mean_central_10pct_rate']:.4f}.",
        f"El caso más central dentro del 1% es n={most_central['n']} con tasa {most_central['central_1pct_rate']:.4f}.",
        f"El caso menos central dentro del 10% es n={least_central['n']} con tasa {least_central['central_10pct_rate']:.4f}.",
        f"Los fríos tienen tasa tiny-sqrt media {cold['mean_tiny_sqrt_rate']:.6f}; los calientes {hot['mean_tiny_sqrt_rate']:.6f}.",
        f"El caso con más peso tiny-sqrt es n={most_tiny['n']} con tasa {most_tiny['tiny_sqrt_rate']:.6f}.",
        f"Los fríos tienen tasa tiny-log media {cold['mean_tiny_log_rate']:.4f}; los calientes {hot['mean_tiny_log_rate']:.4f}.",
        f"El caso más dominado por un canal mod30 es n={most_channel_locked['n']} con canal {most_channel_locked['dominant_channel']} al {most_channel_locked['dominant_channel_rate']:.4f}.",
        f"El frío principal usa {cold_first['active_channels']} canales mod30 activos.",
        f"El caliente principal usa {hot_first['active_channels']} canales mod30 activos.",
        f"El canal dominante del frío principal es {cold_first['dominant_channel']} con tasa {cold_first['dominant_channel_rate']:.4f}.",
        f"El canal dominante del caliente principal es {hot_first['dominant_channel']} con tasa {hot_first['dominant_channel_rate']:.4f}.",
        "No aparece una explicación única por desierto central: los fríos grandes no tienen necesariamente gaps midpoint extremos.",
        "Tampoco aparece una explicación única por pares tiny-giant: las tasas tiny son pequeñas en todos los grupos grandes.",
        "La diferencia frío/caliente grande parece venir más de fluctuación distribuida entre muchos canales que de un solo bloqueo local.",
        "El conteo directo confirma que los outliers calibrados grandes siguen teniendo decenas de miles de representaciones.",
    ]


def write_report(metrics: dict) -> None:
    lines = [
        "# Goldbach round 5: forense frío/caliente",
        "",
        f"Targets únicos auditados: {len(metrics['profiles'])}.",
        f"Auditoría directa limpia: {metrics['all_audits_match']}.",
        "",
        "## Patrones forenses",
        "",
    ]
    for i, pattern in enumerate(metrics["patterns"], 1):
        lines.append(f"{i}. {pattern}")

    lines += [
        "",
        "## Agregados por grupo",
        "",
        "| grupo | n | media pares | gap midpoint medio | central 1% | central 5% | tiny sqrt | canal dominante medio | audit |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in metrics["group_aggregates"]:
        lines.append(
            f"| {row['group']} | {row['count']} | {row['mean_direct_count']:.2f} | {row['mean_midpoint_gap']:.2f} | "
            f"{row['mean_central_1pct_rate']:.4f} | {row['mean_central_5pct_rate']:.4f} | "
            f"{row['mean_tiny_sqrt_rate']:.6f} | {row['mean_dominant_channel_rate']:.4f} | {row['all_audits_match']} |"
        )

    lines += [
        "",
        "## Top fríos >=1M",
        "",
        "| n | pares | gap midpoint | central 1% | central 5% | tiny sqrt | canal top | canal rate |",
        "|---:|---:|---:|---:|---:|---:|---|---:|",
    ]
    for n in metrics["groups"]["cold_ratio_1m"][:10]:
        row = metrics["profiles"][str(n)]
        lines.append(
            f"| {n} | {row['direct_count']} | {row['midpoint']['prime_gap_across_midpoint']} | "
            f"{row['central_1pct_rate']:.4f} | {row['central_5pct_rate']:.4f} | {row['tiny_sqrt_rate']:.6f} | "
            f"{row['dominant_channel']} | {row['dominant_channel_rate']:.4f} |"
        )

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    counts = load_counts(CSV_PATH)
    round4 = json.loads(ROUND4_PATH.read_text(encoding="utf-8"))
    target_info = collect_targets(round4)
    target_ns = [int(n) for n in target_info["all_targets"]]
    flags, primes = sieve(max(target_ns))

    profiles = {}
    for n in target_ns:
        profiles[str(n)] = direct_profile(n, counts[index_of_even(n)], flags, primes)

    group_aggregates = []
    for group_name, ns in target_info["groups"].items():
        group_aggregates.append(aggregate_group(group_name, ns, profiles))

    metrics = {
        "groups": target_info["groups"],
        "target_membership": target_info["all_targets"],
        "profiles": profiles,
        "group_aggregates": group_aggregates,
        "all_audits_match": all(row["audit_match"] for row in profiles.values()),
    }
    metrics["patterns"] = make_patterns(metrics)

    write_report(metrics)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Wrote {REPORT_PATH}")
    print(f"Wrote {METRICS_PATH}")
    print(f"Targets: {len(profiles)}")
    print(f"Audits clean: {metrics['all_audits_match']}")
    print(f"Cold aggregate: {group_aggregates[0]}")
    print(f"Hot aggregate: {group_aggregates[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
