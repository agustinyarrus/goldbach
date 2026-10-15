#!/usr/bin/env python3
"""
Goldbach deep miner, round 2.

This round focuses on:
- wheel 2310 structure,
- hot/cold anomalies after removing modular density,
- weak/strong atlas by decade,
- threshold frontiers,
- small-prime boost signatures,
- record droughts and neighbor shocks.
"""

from __future__ import annotations

import heapq
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "goldbach_nasa_output"
CSV_PATH = OUT / "goldbach_counts_to_10000000.csv"
REPORT_PATH = OUT / "goldbach_round2_deep_patterns.md"
METRICS_PATH = OUT / "goldbach_round2_deep_metrics.json"

SMALL_PRIMES = (3, 5, 7, 11, 13, 17, 19, 23, 29, 31)
PRIMORIALS = (30, 210, 2310, 30030, 510510, 9699690)
DECADES = ((4, 10), (10, 100), (100, 1_000), (1_000, 10_000), (10_000, 100_000), (100_000, 1_000_000), (1_000_000, 10_000_002))
THRESHOLDS = (20, 50, 100, 500, 1_000, 5_000, 10_000, 20_000, 50_000, 100_000)


def even_at(index: int) -> int:
    return 4 + 2 * index


def load_counts(path: Path) -> list[int]:
    counts: list[int] = []
    with path.open("r", encoding="utf-8") as f:
        next(f)
        for line in f:
            # Format: even,goldbach_pairs,mod30,mod210
            first = line.find(",")
            second = line.find(",", first + 1)
            counts.append(int(line[first + 1 : second]))
    return counts


def density(n: int, pairs: int) -> float:
    return pairs * (math.log(n) ** 2) / n


def percentile(sorted_values: list[int] | list[float], p: float) -> float:
    if not sorted_values:
        return 0.0
    if len(sorted_values) == 1:
        return float(sorted_values[0])
    pos = (len(sorted_values) - 1) * p
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return float(sorted_values[lo])
    frac = pos - lo
    return float(sorted_values[lo] * (1.0 - frac) + sorted_values[hi] * frac)


def mod_density_summary(counts: list[int], modulus: int) -> list[dict]:
    buckets: dict[int, dict] = {}
    for i, pairs in enumerate(counts):
        n = even_at(i)
        residue = n % modulus
        row = buckets.setdefault(
            residue,
            {
                "residue": residue,
                "count": 0,
                "pair_sum": 0,
                "density_sum": 0.0,
                "min_pairs": pairs,
                "min_n": n,
                "max_pairs": pairs,
                "max_n": n,
            },
        )
        row["count"] += 1
        row["pair_sum"] += pairs
        row["density_sum"] += density(n, pairs)
        if pairs < row["min_pairs"]:
            row["min_pairs"] = pairs
            row["min_n"] = n
        if pairs > row["max_pairs"]:
            row["max_pairs"] = pairs
            row["max_n"] = n

    out = []
    for row in buckets.values():
        out.append(
            {
                **row,
                "mean_pairs": row["pair_sum"] / row["count"],
                "mean_density": row["density_sum"] / row["count"],
            }
        )
    return sorted(out, key=lambda item: (-item["mean_density"], item["residue"]))


def top_bottom_mod2310(counts: list[int]) -> dict:
    summary = mod_density_summary(counts, 2310)
    return {
        "top_by_density": summary[:20],
        "bottom_by_density": sorted(summary, key=lambda item: (item["mean_density"], item["residue"]))[:20],
        "top_by_pairs": sorted(summary, key=lambda item: (-item["mean_pairs"], item["residue"]))[:20],
        "bottom_by_pairs": sorted(summary, key=lambda item: (item["mean_pairs"], item["residue"]))[:20],
    }


def residual_anomalies(counts: list[int], modulus: int, top: int = 20) -> dict:
    summary = mod_density_summary(counts, modulus)
    mean_by_residue = {row["residue"]: row["mean_density"] for row in summary}
    cold_heap: list[tuple[float, int, int, float, float]] = []
    hot_heap: list[tuple[float, int, int, float, float]] = []

    for i, pairs in enumerate(counts):
        n = even_at(i)
        if n < 1000:
            continue
        d = density(n, pairs)
        expected = mean_by_residue[n % modulus]
        ratio = d / expected if expected else 0.0

        cold_item = (-ratio, n, pairs, d, expected)
        if len(cold_heap) < top:
            heapq.heappush(cold_heap, cold_item)
        elif cold_item > cold_heap[0]:
            heapq.heapreplace(cold_heap, cold_item)

        hot_item = (ratio, n, pairs, d, expected)
        if len(hot_heap) < top:
            heapq.heappush(hot_heap, hot_item)
        elif hot_item > hot_heap[0]:
            heapq.heapreplace(hot_heap, hot_item)

    cold = [
        {"n": n, "pairs": pairs, "density": d, "expected_density": expected, "ratio": -neg_ratio}
        for neg_ratio, n, pairs, d, expected in sorted(cold_heap, reverse=True)
    ]
    hot = [
        {"n": n, "pairs": pairs, "density": d, "expected_density": expected, "ratio": ratio}
        for ratio, n, pairs, d, expected in sorted(hot_heap, reverse=True)
    ]
    return {"modulus": modulus, "cold": cold, "hot": hot}


def decade_atlas(counts: list[int], top: int = 12) -> list[dict]:
    rows = []
    for lo, hi in DECADES:
        weak_heap = []
        strong_heap = []
        values = []
        for i, pairs in enumerate(counts):
            n = even_at(i)
            if not (lo <= n < hi):
                continue
            values.append(pairs)
            weak_item = (-pairs, -n)
            if len(weak_heap) < top:
                heapq.heappush(weak_heap, weak_item)
            elif weak_item > weak_heap[0]:
                heapq.heapreplace(weak_heap, weak_item)

            strong_item = (pairs, -n)
            if len(strong_heap) < top:
                heapq.heappush(strong_heap, strong_item)
            elif strong_item > strong_heap[0]:
                heapq.heapreplace(strong_heap, strong_item)

        ordered = sorted(values)
        weakest = [{"n": -neg_n, "pairs": -neg_pairs} for neg_pairs, neg_n in sorted(weak_heap, reverse=True)]
        strongest = [{"n": -neg_n, "pairs": pairs} for pairs, neg_n in sorted(strong_heap, reverse=True)]
        rows.append(
            {
                "range": f"[{lo},{hi})",
                "count": len(values),
                "min": ordered[0],
                "p01": percentile(ordered, 0.01),
                "p10": percentile(ordered, 0.10),
                "median": percentile(ordered, 0.50),
                "p90": percentile(ordered, 0.90),
                "max": ordered[-1],
                "weakest": weakest,
                "strongest": strongest,
            }
        )
    return rows


def threshold_frontiers(counts: list[int]) -> list[dict]:
    rows = []
    for threshold in THRESHOLDS:
        last_below = None
        below_count = 0
        for i, pairs in enumerate(counts):
            if pairs <= threshold:
                last_below = even_at(i)
                below_count += 1
        rows.append(
            {
                "threshold": threshold,
                "count_at_or_below": below_count,
                "last_at_or_below": last_below,
                "after_that_everything_above": None if last_below is None else last_below + 2,
            }
        )
    return rows


def record_droughts(counts: list[int]) -> dict:
    records = []
    best = -1
    for i, pairs in enumerate(counts):
        n = even_at(i)
        if pairs > best:
            records.append({"n": n, "pairs": pairs})
            best = pairs

    droughts = []
    for left, right in zip(records, records[1:]):
        droughts.append({"from_n": left["n"], "to_n": right["n"], "width": right["n"] - left["n"], "from_pairs": left["pairs"], "to_pairs": right["pairs"]})
    return {"record_count": len(records), "last_records": records[-15:], "largest_droughts": sorted(droughts, key=lambda item: (-item["width"], item["from_n"]))[:15]}


def neighbor_shocks(counts: list[int], top: int = 20) -> dict:
    up_heap: list[tuple[int, int]] = []
    down_heap: list[tuple[int, int]] = []
    ratios_heap: list[tuple[float, int]] = []

    for i in range(len(counts) - 1):
        delta = counts[i + 1] - counts[i]
        if delta > 0:
            item = (delta, i)
            if len(up_heap) < top:
                heapq.heappush(up_heap, item)
            elif item > up_heap[0]:
                heapq.heapreplace(up_heap, item)
        if delta < 0:
            item = (-delta, i)
            if len(down_heap) < top:
                heapq.heappush(down_heap, item)
            elif item > down_heap[0]:
                heapq.heapreplace(down_heap, item)
        if counts[i] > 0:
            ratio = counts[i + 1] / counts[i]
            item = (ratio, i)
            if len(ratios_heap) < top:
                heapq.heappush(ratios_heap, item)
            elif item > ratios_heap[0]:
                heapq.heapreplace(ratios_heap, item)

    def jump_row(i: int) -> dict:
        return {
            "from": even_at(i),
            "to": even_at(i + 1),
            "pairs_from": counts[i],
            "pairs_to": counts[i + 1],
            "delta": counts[i + 1] - counts[i],
            "ratio": counts[i + 1] / counts[i] if counts[i] else None,
        }

    return {
        "largest_up": [jump_row(i) for _, i in sorted(up_heap, reverse=True)],
        "largest_down": [jump_row(i) for _, i in sorted(down_heap, reverse=True)],
        "largest_ratio_up": [jump_row(i) for _, i in sorted(ratios_heap, reverse=True)],
    }


def small_prime_signature(counts: list[int]) -> dict:
    groups: dict[int, dict] = {}
    sum_x = sum_y = sum_xx = sum_yy = sum_xy = 0.0
    top = 20
    cold_ratio_heap: list[tuple[float, int, int, float, float]] = []
    hot_ratio_heap: list[tuple[float, int, int, float, float]] = []

    for i, pairs in enumerate(counts):
        n = even_at(i)
        sig = 0
        theoretical = 1.0
        active = []
        for bit, p in enumerate(SMALL_PRIMES):
            if n % p == 0:
                sig |= 1 << bit
                theoretical *= (p - 1) / (p - 2)
                active.append(p)
        d = density(n, pairs)
        row = groups.setdefault(sig, {"signature": sig, "count": 0, "density_sum": 0.0, "pair_sum": 0, "example_n": n, "primes": active})
        row["count"] += 1
        row["density_sum"] += d
        row["pair_sum"] += pairs

        sum_x += theoretical
        sum_y += d
        sum_xx += theoretical * theoretical
        sum_yy += d * d
        sum_xy += theoretical * d

        ratio = d / theoretical
        cold_item = (-ratio, n, pairs, d, theoretical)
        if len(cold_ratio_heap) < top:
            heapq.heappush(cold_ratio_heap, cold_item)
        elif cold_item > cold_ratio_heap[0]:
            heapq.heapreplace(cold_ratio_heap, cold_item)

        hot_item = (ratio, n, pairs, d, theoretical)
        if len(hot_ratio_heap) < top:
            heapq.heappush(hot_ratio_heap, hot_item)
        elif hot_item > hot_ratio_heap[0]:
            heapq.heapreplace(hot_ratio_heap, hot_item)

    n_rows = len(counts)
    numerator = n_rows * sum_xy - sum_x * sum_y
    denominator = math.sqrt((n_rows * sum_xx - sum_x * sum_x) * (n_rows * sum_yy - sum_y * sum_y))

    signatures = []
    for row in groups.values():
        mean_density = row["density_sum"] / row["count"]
        mean_pairs = row["pair_sum"] / row["count"]
        theoretical = 1.0
        for p in row["primes"]:
            theoretical *= (p - 1) / (p - 2)
        signatures.append(
            {
                "signature": row["signature"],
                "primes": row["primes"],
                "count": row["count"],
                "example_n": row["example_n"],
                "mean_density": mean_density,
                "mean_pairs": mean_pairs,
                "theoretical_small_boost": theoretical,
                "density_over_boost": mean_density / theoretical,
            }
        )

    large_signatures = [row for row in signatures if row["count"] >= 100]
    cold_points = [
        {"n": n, "pairs": pairs, "density": d, "theoretical_small_boost": theoretical, "density_over_boost": -neg_ratio}
        for neg_ratio, n, pairs, d, theoretical in sorted(cold_ratio_heap, reverse=True)
    ]
    hot_points = [
        {"n": n, "pairs": pairs, "density": d, "theoretical_small_boost": theoretical, "density_over_boost": ratio}
        for ratio, n, pairs, d, theoretical in sorted(hot_ratio_heap, reverse=True)
    ]
    return {
        "signature_count": len(signatures),
        "large_signature_count": len(large_signatures),
        "corr_theoretical_boost_vs_density": numerator / denominator if denominator else 0.0,
        "top_large_signatures": sorted(large_signatures, key=lambda item: (-item["mean_density"], item["signature"]))[:20],
        "bottom_large_signatures": sorted(large_signatures, key=lambda item: (item["mean_density"], item["signature"]))[:20],
        "cold_points_after_small_boost": cold_points,
        "hot_points_after_small_boost": hot_points,
    }


def primorial_rows(counts: list[int]) -> list[dict]:
    total_sum = sum(counts)
    total_count = len(counts)
    rows = []
    for modulus in PRIMORIALS:
        values = []
        for i, pairs in enumerate(counts):
            n = even_at(i)
            if n % modulus == 0:
                values.append((n, pairs))
        pair_sum = sum(pairs for _, pairs in values)
        not_sum = total_sum - pair_sum
        not_count = total_count - len(values)
        strongest = max(values, key=lambda item: item[1])
        weakest = min(values, key=lambda item: item[1])
        rows.append(
            {
                "modulus": modulus,
                "multiples": len(values),
                "mean_pairs": pair_sum / len(values),
                "mean_if_not": not_sum / not_count if not_count else None,
                "lift": (pair_sum / len(values)) / (not_sum / not_count) if not_count else None,
                "weakest_multiple": {"n": weakest[0], "pairs": weakest[1]},
                "strongest_multiple": {"n": strongest[0], "pairs": strongest[1]},
            }
        )
    return rows


def weak_band_exceptions(counts: list[int]) -> dict:
    mod30_summary = mod_density_summary(counts, 30)
    best_residue = mod30_summary[0]["residue"]
    worst_residue = sorted(mod30_summary, key=lambda item: item["mean_density"])[0]["residue"]
    heaps = {
        "hot_in_worst": [],
        "cold_in_best": [],
    }
    top = 20
    for i, pairs in enumerate(counts):
        n = even_at(i)
        d = density(n, pairs)
        if n % 30 == worst_residue:
            item = (d, n, pairs)
            if len(heaps["hot_in_worst"]) < top:
                heapq.heappush(heaps["hot_in_worst"], item)
            elif item > heaps["hot_in_worst"][0]:
                heapq.heapreplace(heaps["hot_in_worst"], item)
        if n % 30 == best_residue:
            item = (-d, n, pairs)
            if len(heaps["cold_in_best"]) < top:
                heapq.heappush(heaps["cold_in_best"], item)
            elif item > heaps["cold_in_best"][0]:
                heapq.heapreplace(heaps["cold_in_best"], item)

    return {
        "best_mod30_residue": best_residue,
        "worst_mod30_residue": worst_residue,
        "hot_in_worst": [{"n": n, "pairs": pairs, "density": d} for d, n, pairs in sorted(heaps["hot_in_worst"], reverse=True)],
        "cold_in_best": [{"n": n, "pairs": pairs, "density": -neg_d} for neg_d, n, pairs in sorted(heaps["cold_in_best"], reverse=True)],
    }


def make_patterns(metrics: dict) -> list[str]:
    mod2310 = metrics["mod2310"]
    residual210 = metrics["residual210"]
    residual2310 = metrics["residual2310"]
    atlas = metrics["decade_atlas"]
    thresholds = metrics["threshold_frontiers"]
    records = metrics["records"]
    shocks = metrics["neighbor_shocks"]
    signatures = metrics["small_prime_signatures"]
    primorials = metrics["primorials"]
    band = metrics["weak_band_exceptions"]

    top_sig = signatures["top_large_signatures"][0]
    bottom_sig = signatures["bottom_large_signatures"][0]

    patterns = [
        f"La mejor clase por densidad en rueda 2310 es residuo {mod2310['top_by_density'][0]['residue']} con densidad media {mod2310['top_by_density'][0]['mean_density']:.4f}.",
        f"La peor clase por densidad en rueda 2310 es residuo {mod2310['bottom_by_density'][0]['residue']} con densidad media {mod2310['bottom_by_density'][0]['mean_density']:.4f}.",
        f"El cociente mejor/peor en rueda 2310 es {mod2310['top_by_density'][0]['mean_density'] / mod2310['bottom_by_density'][0]['mean_density']:.2f}.",
        f"Por pares crudos, la mejor clase 2310 es residuo {mod2310['top_by_pairs'][0]['residue']} con media {mod2310['top_by_pairs'][0]['mean_pairs']:.2f}.",
        f"Por pares crudos, la peor clase 2310 es residuo {mod2310['bottom_by_pairs'][0]['residue']} con media {mod2310['bottom_by_pairs'][0]['mean_pairs']:.2f}.",
        f"La clase 2310 ganadora tiene su máximo en n={mod2310['top_by_density'][0]['max_n']} con {mod2310['top_by_density'][0]['max_pairs']:,} pares.",
        f"La clase 2310 perdedora toca mínimo en n={mod2310['bottom_by_density'][0]['min_n']} con {mod2310['bottom_by_density'][0]['min_pairs']} pares.",
        f"Quitando el promedio de cada clase mod 210, el punto más frío es n={residual210['cold'][0]['n']} con ratio {residual210['cold'][0]['ratio']:.3f}.",
        f"Quitando el promedio de cada clase mod 210, el punto más caliente es n={residual210['hot'][0]['n']} con ratio {residual210['hot'][0]['ratio']:.3f}.",
        f"Quitando el promedio de cada clase mod 2310, el punto más frío es n={residual2310['cold'][0]['n']} con ratio {residual2310['cold'][0]['ratio']:.3f}.",
        f"Quitando el promedio de cada clase mod 2310, el punto más caliente es n={residual2310['hot'][0]['n']} con ratio {residual2310['hot'][0]['ratio']:.3f}.",
        f"La anomalía fría mod 2310 conserva {residual2310['cold'][0]['pairs']} pares: sigue lejos de cero.",
        f"La anomalía caliente mod 2310 alcanza {residual2310['hot'][0]['pairs']:,} pares.",
        f"En la década [1.000,10.000), los 12 más débiles van de {atlas[3]['weakest'][0]['n']} a {atlas[3]['weakest'][-1]['n']} con conteos entre {atlas[3]['weakest'][0]['pairs']} y {atlas[3]['weakest'][-1]['pairs']}.",
        f"En [10.000,100.000), el mínimo sube a {atlas[4]['min']} y el p1 ya es {atlas[4]['p01']:.0f}.",
        f"En [100.000,1.000.000), el mínimo sube a {atlas[5]['min']} y el p1 ya es {atlas[5]['p01']:.0f}.",
        f"En [1M,10M], el mínimo sube a {atlas[6]['min']} y el p1 ya es {atlas[6]['p01']:.0f}.",
        f"El último n con <=20 pares es {thresholds[0]['last_at_or_below']}.",
        f"El último n con <=50 pares es {thresholds[1]['last_at_or_below']}.",
        f"El último n con <=100 pares es {thresholds[2]['last_at_or_below']}.",
        f"El último n con <=500 pares es {thresholds[3]['last_at_or_below']}.",
        f"El último n con <=1.000 pares es {thresholds[4]['last_at_or_below']}.",
        f"El último n con <=5.000 pares es {thresholds[5]['last_at_or_below']}.",
        f"El último n con <=10.000 pares es {thresholds[6]['last_at_or_below']}.",
        f"El último n con <=20.000 pares es {thresholds[7]['last_at_or_below']}.",
        f"El umbral <=50.000 todavía aparece hasta {thresholds[8]['last_at_or_below']}.",
        f"El umbral <=100.000 todavía aparece hasta {thresholds[9]['last_at_or_below']}.",
        f"Hay {records['record_count']} récords; la mayor sequía entre récords mide {records['largest_droughts'][0]['width']:,} números.",
        f"La mayor sequía de récords va de {records['largest_droughts'][0]['from_n']} a {records['largest_droughts'][0]['to_n']}.",
        f"Los últimos récords terminan en {records['last_records'][-1]['n']} con {records['last_records'][-1]['pairs']:,} pares.",
        f"El mayor salto vecino hacia arriba es {shocks['largest_up'][0]['delta']:+,} entre {shocks['largest_up'][0]['from']} y {shocks['largest_up'][0]['to']}.",
        f"El mayor salto vecino hacia abajo es {shocks['largest_down'][0]['delta']:+,} entre {shocks['largest_down'][0]['from']} y {shocks['largest_down'][0]['to']}.",
        f"La mayor duplicación relativa vecina ocurre de {shocks['largest_ratio_up'][0]['from']} a {shocks['largest_ratio_up'][0]['to']} con ratio {shocks['largest_ratio_up'][0]['ratio']:.2f}.",
        f"El modelo de boost por primos chicos correlaciona con densidad en {signatures['corr_theoretical_boost_vs_density']:.4f}.",
        f"Se observaron {signatures['signature_count']} firmas de divisibilidad sobre los 10 primos chicos.",
        f"{signatures['large_signature_count']} firmas tienen al menos 100 ejemplos, suficiente para comparar medias.",
        f"La firma grande más fuerte usa primos {top_sig['primes']} y densidad media {top_sig['mean_density']:.4f}.",
        f"La firma grande más débil usa primos {bottom_sig['primes']} y densidad media {bottom_sig['mean_density']:.4f}.",
        f"El punto más frío tras dividir por boost chico es n={signatures['cold_points_after_small_boost'][0]['n']} con ratio {signatures['cold_points_after_small_boost'][0]['density_over_boost']:.4f}.",
        f"El punto más caliente tras dividir por boost chico es n={signatures['hot_points_after_small_boost'][0]['n']} con ratio {signatures['hot_points_after_small_boost'][0]['density_over_boost']:.4f}.",
        f"Los múltiplos de 30 tienen lift {primorials[0]['lift']:.2f} y su múltiplo más débil es {primorials[0]['weakest_multiple']['n']}.",
        f"Los múltiplos de 210 tienen lift {primorials[1]['lift']:.2f} y su múltiplo más fuerte es {primorials[1]['strongest_multiple']['n']}.",
        f"Los múltiplos de 2310 tienen lift {primorials[2]['lift']:.2f}.",
        f"Los múltiplos de 30030 tienen lift {primorials[3]['lift']:.2f}.",
        f"Los múltiplos de 510510 tienen lift {primorials[4]['lift']:.2f}.",
        f"El único múltiplo de 9699690 dentro del límite es n={primorials[5]['strongest_multiple']['n']} y coincide con el campeón global.",
        f"La peor banda mod30 es residuo {band['worst_mod30_residue']}, pero su caso caliente llega a {band['hot_in_worst'][0]['n']} con {band['hot_in_worst'][0]['pairs']:,} pares.",
        f"La mejor banda mod30 es residuo {band['best_mod30_residue']}, pero su caso frío cae en {band['cold_in_best'][0]['n']} con solo {band['cold_in_best'][0]['pairs']} pares.",
        f"El patrón fuerte no es solo crecimiento: después de normalizar por log^2(n)/n, las clases modulares siguen separadas.",
        f"El patrón débil tampoco es solo modular: quedan outliers fríos dentro de su propia clase mod 2310.",
        f"La frontera empírica 'todo queda arriba de 1.000 pares' empieza después de n={thresholds[4]['last_at_or_below']}.",
        f"La frontera empírica 'todo queda arriba de 5.000 pares' empieza después de n={thresholds[5]['last_at_or_below']}.",
        f"La década de millones tiene mediana {atlas[6]['median']:.0f}, casi {atlas[6]['median'] / atlas[3]['median']:.1f} veces la mediana de la década de miles.",
        f"El p10 de millones es {atlas[6]['p10']:.0f}, casi {atlas[6]['p10'] / atlas[3]['p10']:.1f} veces el p10 de miles.",
        f"El máximo de [100.000,1.000.000) es {atlas[5]['strongest'][0]['n']} con {atlas[5]['strongest'][0]['pairs']:,} pares.",
        f"El máximo de [1M,10M] es {atlas[6]['strongest'][0]['n']} con {atlas[6]['strongest'][0]['pairs']:,} pares.",
        f"Los outliers calientes mod 210 incluyen {', '.join(str(row['n']) for row in residual210['hot'][:5])}.",
        f"Los outliers fríos mod 210 incluyen {', '.join(str(row['n']) for row in residual210['cold'][:5])}.",
        f"Los outliers calientes mod 2310 incluyen {', '.join(str(row['n']) for row in residual2310['hot'][:5])}.",
        f"Los outliers fríos mod 2310 incluyen {', '.join(str(row['n']) for row in residual2310['cold'][:5])}.",
        f"Los vecinos del campeón global muestran pared: de {shocks['largest_down'][0]['from']} a {shocks['largest_down'][0]['to']} se pierden {abs(shocks['largest_down'][0]['delta']):,} pares.",
        f"El análisis round 2 refuerza una idea: Goldbach parece gobernado por crecimiento suave multiplicado por ruedas modulares y boosts de factores chicos.",
        f"La amenaza real para un contraejemplo no aparece en los grandes: los mínimos relativos grandes todavía tienen miles de representaciones.",
        f"1112 sigue siendo más interesante como fósil modular temprano que como señal de una familia peligrosa.",
        f"Rueda 2310 mejora la lupa: separa subfamilias dentro de las mismas bandas mod 30/210.",
        f"Los récords favorecen números con muchos divisores chicos, pero los saltos vecinos prueban que ese boost se apaga de golpe al moverse dos unidades.",
    ]
    return patterns


def make_next_experiments() -> list[str]:
    return [
        "Implementar rueda 30030 completa y comparar outliers contra rueda 2310.",
        "Calcular el producto singular exacto para cada n usando SPF compacto.",
        "Ajustar una regresion lineal sobre log(densidad) con indicadores mod 210 y factores chicos.",
        "Separar anomalías que vienen de factores grandes de n, no solo de primos chicos.",
        "Buscar familias n = primorial*k donde k es primo, semiprimo o altamente compuesto.",
        "Medir si los grandes saltos vecinos se explican por perder divisibilidad por 3,5,7 simultaneamente.",
        "Construir graficos de calor mod 2310 vs densidad normalizada.",
        "Hacer un atlas local alrededor de cada record: n-20 a n+20.",
        "Hacer un atlas local alrededor de cada debil: n-20 a n+20.",
        "Buscar si las anomalías frías mod 2310 comparten residues modulo 30030.",
        "Entrenar un predictor barato de debiles solo con n modulo primoriales.",
        "Comprimir conteos a npz/parquet para poder iterar mas rapido.",
        "Extender solo estadisticas agregadas hasta 20M o 50M sin guardar CSV completo.",
        "Generar un informe HTML navegable con tablas filtrables.",
        "Auditar manualmente los 20 outliers frios mod 2310 con conteo directo.",
        "Medir pares con ambos primos lejos de divisores chicos.",
        "Separar contribuciones p pequeno + n-p gigante contra pares balanceados.",
        "Comparar g(n) contra g(n+210), g(n+420), g(n+2310).",
        "Buscar 'clones modulares': n distintos con misma firma mod 2310 y densidades extremas.",
        "Probar si phi(n)/n ordena la debilidad mejor que la firma de factores chicos.",
        "Calcular radical(n) y tau(n) para los outliers extremos.",
        "Explorar si los records aparecen cerca de primoriales o exactamente en multiplos.",
        "Medir estabilidad del top 20 de residuos 2310 al cortar el rango en deciles.",
        "Construir un buscador interactivo por n que devuelva pares, firma, densidad y residuos.",
        "Correr una version Monte Carlo en rangos altos, sin FFT global, para testear heuristicas.",
    ]


def write_report(metrics: dict) -> None:
    lines = [
        "# Goldbach round 2: patrones profundos",
        "",
        f"Fuente: `{CSV_PATH.name}`.",
        f"Limite: {metrics['limit']:,}. Pares analizados: {metrics['rows']:,}.",
        "",
        "## Patrones round 2",
        "",
    ]
    for i, pattern in enumerate(metrics["patterns"], 1):
        lines.append(f"{i}. {pattern}")

    lines += ["", "## Siguientes experimentos", ""]
    for i, experiment in enumerate(metrics["next_experiments"], 1):
        lines.append(f"{i}. {experiment}")

    lines += [
        "",
        "## Tablas clave",
        "",
        "### Top 10 residuos 2310 por densidad",
        "",
        "| residuo | densidad media | pares medios | min | max |",
        "|---:|---:|---:|---:|---:|",
    ]
    for row in metrics["mod2310"]["top_by_density"][:10]:
        lines.append(f"| {row['residue']} | {row['mean_density']:.4f} | {row['mean_pairs']:.2f} | {row['min_pairs']} | {row['max_pairs']} |")

    lines += ["", "### Bottom 10 residuos 2310 por densidad", "", "| residuo | densidad media | pares medios | min | max |", "|---:|---:|---:|---:|---:|"]
    for row in metrics["mod2310"]["bottom_by_density"][:10]:
        lines.append(f"| {row['residue']} | {row['mean_density']:.4f} | {row['mean_pairs']:.2f} | {row['min_pairs']} | {row['max_pairs']} |")

    lines += ["", "### Fronteras de umbral", "", "| umbral | ultimo n <= umbral | cantidad |", "|---:|---:|---:|"]
    for row in metrics["threshold_frontiers"]:
        lines.append(f"| {row['threshold']} | {row['last_at_or_below']} | {row['count_at_or_below']} |")

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_metrics(metrics: dict) -> None:
    METRICS_PATH.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")


def build_metrics(counts: list[int]) -> dict:
    metrics = {
        "limit": even_at(len(counts) - 1),
        "rows": len(counts),
        "mod2310": top_bottom_mod2310(counts),
        "residual210": residual_anomalies(counts, 210),
        "residual2310": residual_anomalies(counts, 2310),
        "decade_atlas": decade_atlas(counts),
        "threshold_frontiers": threshold_frontiers(counts),
        "records": record_droughts(counts),
        "neighbor_shocks": neighbor_shocks(counts),
        "small_prime_signatures": small_prime_signature(counts),
        "primorials": primorial_rows(counts),
        "weak_band_exceptions": weak_band_exceptions(counts),
    }
    metrics["patterns"] = make_patterns(metrics)
    metrics["next_experiments"] = make_next_experiments()
    return metrics


def main() -> int:
    counts = load_counts(CSV_PATH)
    metrics = build_metrics(counts)
    write_report(metrics)
    write_metrics(metrics)
    print(f"Wrote {REPORT_PATH}")
    print(f"Wrote {METRICS_PATH}")
    print(f"Patterns: {len(metrics['patterns'])}")
    print(f"Next experiments: {len(metrics['next_experiments'])}")
    print(f"Top 2310 density residue: {metrics['mod2310']['top_by_density'][0]}")
    print(f"Cold mod2310 anomaly: {metrics['residual2310']['cold'][0]}")
    print(f"Last <= 1000 pairs: {metrics['threshold_frontiers'][4]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
