#!/usr/bin/env python3
"""
Goldbach miner round 4: calibrated Hardy-Littlewood residuals.

Round 3 showed that HL + the singular product explains the modular structure,
but the formula has a finite-range global bias. This round calibrates that bias
away and then asks what remains:

- cold/hot points by scale,
- residuals after calibration,
- stability under n -> n + 30/210/420/2310,
- neighbor shock explanations,
- local atlases around weak and record values.
"""

from __future__ import annotations

import heapq
import json
import math
from array import array
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "goldbach_nasa_output"
CSV_PATH = OUT / "goldbach_counts_to_10000000.csv"
REPORT_PATH = OUT / "goldbach_round4_calibrated_hl.md"
METRICS_PATH = OUT / "goldbach_round4_calibrated_hl_metrics.json"

TWIN_PRIME_CONSTANT = 0.6601618158468696
LOWER_BOUNDS = (1_000, 10_000, 100_000, 1_000_000)
LAGS = (30, 210, 420, 2310)
ANCHORS = (1112, 2672, 9699690, 9189180, 8678670, 8168160, 7657650, 990990, 510510, 2310)


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


def sieve_primes(limit: int) -> list[int]:
    flags = bytearray(b"\x01") * (limit + 1)
    flags[0] = 0
    flags[1] = 0
    root = math.isqrt(limit)
    for p in range(2, root + 1):
        if flags[p]:
            start = p * p
            flags[start : limit + 1 : p] = b"\x00" * (((limit - start) // p) + 1)
    return [n for n in range(2, limit + 1) if flags[n]]


def build_singular_boost(row_count: int, primes: list[int]) -> array:
    limit = even_at(row_count - 1)
    boost = array("d", [1.0]) * row_count
    for p in primes:
        if p == 2:
            continue
        if 2 * p > limit:
            break
        factor = (p - 1) / (p - 2)
        for idx in range(p - 2, row_count, p):
            boost[idx] *= factor
    return boost


def expected_hl(n: int, boost: float) -> float:
    if n < 6:
        return 1.0
    return TWIN_PRIME_CONSTANT * n / (math.log(n) ** 2) * boost


def factorize(n: int, primes: list[int]) -> list[int]:
    factors = []
    rest = n
    for p in primes:
        if p * p > rest:
            break
        if rest % p == 0:
            factors.append(p)
            while rest % p == 0:
                rest //= p
    if rest > 1:
        factors.append(rest)
    return factors


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    pos = (len(ordered) - 1) * p
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return ordered[lo]
    frac = pos - lo
    return ordered[lo] * (1.0 - frac) + ordered[hi] * frac


def compute_ratios(counts: list[int], boost: array) -> tuple[array, array, float]:
    raw_ratios = array("d", [0.0]) * len(counts)
    expected_values = array("d", [0.0]) * len(counts)
    total = 0.0
    total_count = 0
    for i, pairs in enumerate(counts):
        n = even_at(i)
        expected = expected_hl(n, boost[i])
        ratio = pairs / expected if expected else 0.0
        expected_values[i] = expected
        raw_ratios[i] = ratio
        if n >= 1000:
            total += ratio
            total_count += 1
    return raw_ratios, expected_values, total / total_count


def row_for_index(i: int, counts: list[int], ratios: array, expected: array, boost: array, calibration: float, primes: list[int]) -> dict:
    n = even_at(i)
    calibrated_expected = expected[i] * calibration
    return {
        "n": n,
        "pairs": counts[i],
        "raw_ratio": ratios[i],
        "calibrated_ratio": ratios[i] / calibration,
        "expected": expected[i],
        "calibrated_expected": calibrated_expected,
        "calibrated_residual": counts[i] - calibrated_expected,
        "singular_boost": boost[i],
        "factors": factorize(n, primes),
    }


def scale_extremes(counts: list[int], ratios: array, expected: array, boost: array, calibration: float, primes: list[int]) -> dict:
    top = 20
    heaps = {}
    for lower in LOWER_BOUNDS:
        heaps[lower] = {
            "cold_ratio": [],
            "hot_ratio": [],
            "negative_residual": [],
            "positive_residual": [],
        }

    for i, pairs in enumerate(counts):
        n = even_at(i)
        calibrated_ratio = ratios[i] / calibration
        calibrated_residual = pairs - expected[i] * calibration
        for lower in LOWER_BOUNDS:
            if n < lower:
                continue
            bucket = heaps[lower]
            cold_item = (-calibrated_ratio, i)
            if len(bucket["cold_ratio"]) < top:
                heapq.heappush(bucket["cold_ratio"], cold_item)
            elif cold_item > bucket["cold_ratio"][0]:
                heapq.heapreplace(bucket["cold_ratio"], cold_item)

            hot_item = (calibrated_ratio, i)
            if len(bucket["hot_ratio"]) < top:
                heapq.heappush(bucket["hot_ratio"], hot_item)
            elif hot_item > bucket["hot_ratio"][0]:
                heapq.heapreplace(bucket["hot_ratio"], hot_item)

            neg_item = (-calibrated_residual, i)
            if len(bucket["negative_residual"]) < top:
                heapq.heappush(bucket["negative_residual"], neg_item)
            elif neg_item > bucket["negative_residual"][0]:
                heapq.heapreplace(bucket["negative_residual"], neg_item)

            pos_item = (calibrated_residual, i)
            if len(bucket["positive_residual"]) < top:
                heapq.heappush(bucket["positive_residual"], pos_item)
            elif pos_item > bucket["positive_residual"][0]:
                heapq.heapreplace(bucket["positive_residual"], pos_item)

    out = {}
    for lower, bucket in heaps.items():
        out[str(lower)] = {
            "cold_ratio": [row_for_index(i, counts, ratios, expected, boost, calibration, primes) for _, i in sorted(bucket["cold_ratio"], reverse=True)],
            "hot_ratio": [row_for_index(i, counts, ratios, expected, boost, calibration, primes) for _, i in sorted(bucket["hot_ratio"], reverse=True)],
            "negative_residual": [row_for_index(i, counts, ratios, expected, boost, calibration, primes) for _, i in sorted(bucket["negative_residual"], reverse=True)],
            "positive_residual": [row_for_index(i, counts, ratios, expected, boost, calibration, primes) for _, i in sorted(bucket["positive_residual"], reverse=True)],
        }
    return out


def scale_bands(counts: list[int], ratios: array, expected: array, calibration: float) -> list[dict]:
    lower = 1000
    upper = even_at(len(counts) - 1)
    width = (upper - lower + 2) / 10
    bands = []
    for band in range(10):
        lo = int(lower + band * width)
        hi = int(lower + (band + 1) * width)
        if lo % 2:
            lo += 1
        if hi % 2:
            hi += 1
        bands.append({"band": band + 1, "lo": lo, "hi": hi, "count": 0, "ratio_sum": 0.0, "cal_residual_sum": 0.0, "samples": []})

    for i, pairs in enumerate(counts):
        n = even_at(i)
        if n < lower:
            continue
        band_index = min(9, int((n - lower) / width))
        row = bands[band_index]
        cal_ratio = ratios[i] / calibration
        row["count"] += 1
        row["ratio_sum"] += cal_ratio
        row["cal_residual_sum"] += pairs - expected[i] * calibration
        if i % 50 == 0:
            row["samples"].append(cal_ratio)

    out = []
    for row in bands:
        out.append(
            {
                "band": row["band"],
                "range": f"[{row['lo']},{row['hi']})",
                "count": row["count"],
                "mean_calibrated_ratio": row["ratio_sum"] / row["count"],
                "mean_calibrated_residual": row["cal_residual_sum"] / row["count"],
                "sample_p01": percentile(row["samples"], 0.01),
                "sample_median": percentile(row["samples"], 0.50),
                "sample_p99": percentile(row["samples"], 0.99),
            }
        )
    return out


def lag_stability(counts: list[int], ratios: array, calibration: float) -> list[dict]:
    rows = []
    start = index_of_even(1000)
    for period in LAGS:
        lag = period // 2
        n_samples = 0
        sum_abs_log = 0.0
        sum_abs_count_delta = 0.0
        sx = sy = sxx = syy = sxy = 0.0
        rx = ry = rxx = ryy = rxy = 0.0
        for i in range(start, len(counts) - lag, 20):
            x = counts[i]
            y = counts[i + lag]
            crx = ratios[i] / calibration
            cry = ratios[i + lag] / calibration
            n_samples += 1
            sum_abs_log += abs(math.log(cry / crx))
            sum_abs_count_delta += abs(y - x)
            sx += x
            sy += y
            sxx += x * x
            syy += y * y
            sxy += x * y
            rx += crx
            ry += cry
            rxx += crx * crx
            ryy += cry * cry
            rxy += crx * cry
        count_corr_den = math.sqrt((n_samples * sxx - sx * sx) * (n_samples * syy - sy * sy))
        ratio_corr_den = math.sqrt((n_samples * rxx - rx * rx) * (n_samples * ryy - ry * ry))
        rows.append(
            {
                "period": period,
                "lag_even_steps": lag,
                "samples": n_samples,
                "mean_abs_log_calibrated_ratio_change": sum_abs_log / n_samples,
                "mean_abs_count_delta": sum_abs_count_delta / n_samples,
                "count_corr": (n_samples * sxy - sx * sy) / count_corr_den if count_corr_den else 0.0,
                "calibrated_ratio_corr": (n_samples * rxy - rx * ry) / ratio_corr_den if ratio_corr_den else 0.0,
            }
        )
    return rows


def neighbor_shocks(counts: list[int], ratios: array, expected: array, boost: array, calibration: float, primes: list[int]) -> dict:
    top = 20
    up_heap: list[tuple[int, int]] = []
    down_heap: list[tuple[int, int]] = []
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

    def shock_row(i: int) -> dict:
        left = row_for_index(i, counts, ratios, expected, boost, calibration, primes)
        right = row_for_index(i + 1, counts, ratios, expected, boost, calibration, primes)
        left_set = set(left["factors"])
        right_set = set(right["factors"])
        return {
            "from": left,
            "to": right,
            "delta_pairs": right["pairs"] - left["pairs"],
            "ratio_pairs": right["pairs"] / left["pairs"] if left["pairs"] else None,
            "lost_factors": sorted(left_set - right_set),
            "gained_factors": sorted(right_set - left_set),
        }

    return {
        "largest_up": [shock_row(i) for _, i in sorted(up_heap, reverse=True)],
        "largest_down": [shock_row(i) for _, i in sorted(down_heap, reverse=True)],
    }


def local_atlas(counts: list[int], ratios: array, expected: array, boost: array, calibration: float, primes: list[int]) -> list[dict]:
    rows = []
    limit = even_at(len(counts) - 1)
    for anchor in ANCHORS:
        if anchor < 4 or anchor > limit or anchor % 2:
            continue
        entries = []
        for n in range(max(4, anchor - 20), min(limit, anchor + 20) + 1, 2):
            i = index_of_even(n)
            entries.append(row_for_index(i, counts, ratios, expected, boost, calibration, primes))
        center = row_for_index(index_of_even(anchor), counts, ratios, expected, boost, calibration, primes)
        strongest = max(entries, key=lambda row: row["pairs"])
        weakest = min(entries, key=lambda row: row["pairs"])
        rows.append(
            {
                "anchor": anchor,
                "center": center,
                "window_min": weakest,
                "window_max": strongest,
                "center_rank_by_pairs": 1 + sum(1 for row in entries if row["pairs"] > center["pairs"]),
                "entries": entries,
            }
        )
    return rows


def make_patterns(metrics: dict) -> list[str]:
    calibration = metrics["calibration"]
    extremes = metrics["scale_extremes"]
    bands = metrics["scale_bands"]
    lags = metrics["lag_stability"]
    shocks = metrics["neighbor_shocks"]
    atlas = metrics["local_atlas"]

    e1k = extremes["1000"]
    e10k = extremes["10000"]
    e100k = extremes["100000"]
    e1m = extremes["1000000"]
    best_lag_count = max(lags, key=lambda row: row["count_corr"])
    best_lag_ratio = max(lags, key=lambda row: row["calibrated_ratio_corr"])
    smallest_lag_drift = min(lags, key=lambda row: row["mean_abs_log_calibrated_ratio_change"])
    largest_up = shocks["largest_up"][0]
    largest_down = shocks["largest_down"][0]
    anchor_9699690 = next(row for row in atlas if row["anchor"] == 9699690)
    anchor_1112 = next(row for row in atlas if row["anchor"] == 1112)
    anchor_2672 = next(row for row in atlas if row["anchor"] == 2672)

    return [
        f"El factor de calibración global de HL en n>=1000 es {calibration:.6f}.",
        "Después de calibrar, un ratio 1.0 significa 'exactamente lo esperable para este rango finito'.",
        f"El punto más frío calibrado desde 1000 es n={e1k['cold_ratio'][0]['n']} con ratio {e1k['cold_ratio'][0]['calibrated_ratio']:.4f}.",
        f"El punto más caliente calibrado desde 1000 es n={e1k['hot_ratio'][0]['n']} con ratio {e1k['hot_ratio'][0]['calibrated_ratio']:.4f}.",
        f"Desde 10k, el punto más frío calibrado es n={e10k['cold_ratio'][0]['n']} con ratio {e10k['cold_ratio'][0]['calibrated_ratio']:.4f}.",
        f"Desde 100k, el punto más frío calibrado es n={e100k['cold_ratio'][0]['n']} con ratio {e100k['cold_ratio'][0]['calibrated_ratio']:.4f}.",
        f"Desde 1M, el punto más frío calibrado es n={e1m['cold_ratio'][0]['n']} con ratio {e1m['cold_ratio'][0]['calibrated_ratio']:.4f}.",
        f"Desde 1M, ese punto frío todavía tiene {e1m['cold_ratio'][0]['pairs']:,} pares.",
        f"Desde 1M, el punto más caliente calibrado es n={e1m['hot_ratio'][0]['n']} con ratio {e1m['hot_ratio'][0]['calibrated_ratio']:.4f}.",
        f"El peor residual calibrado negativo desde 1000 es n={e1k['negative_residual'][0]['n']} con residual {e1k['negative_residual'][0]['calibrated_residual']:.2f}.",
        f"El peor residual calibrado negativo desde 1M es n={e1m['negative_residual'][0]['n']} con residual {e1m['negative_residual'][0]['calibrated_residual']:.2f}.",
        f"Pero ese peor residual desde 1M conserva {e1m['negative_residual'][0]['pairs']:,} representaciones.",
        f"El mayor residual calibrado positivo desde 1M es n={e1m['positive_residual'][0]['n']} con +{e1m['positive_residual'][0]['calibrated_residual']:.2f}.",
        f"Por bandas iguales, el primer decil tiene media calibrada {bands[0]['mean_calibrated_ratio']:.4f}.",
        f"Por bandas iguales, el último decil tiene media calibrada {bands[-1]['mean_calibrated_ratio']:.4f}.",
        f"La mediana muestreada del último decil es {bands[-1]['sample_median']:.4f}.",
        f"El p1 muestreado del último decil es {bands[-1]['sample_p01']:.4f}.",
        f"El p99 muestreado del último decil es {bands[-1]['sample_p99']:.4f}.",
        f"La mejor correlación de conteos entre lags probados es periodo {best_lag_count['period']} con corr {best_lag_count['count_corr']:.4f}.",
        f"La mejor correlación de ratio calibrado entre lags probados es periodo {best_lag_ratio['period']} con corr {best_lag_ratio['calibrated_ratio_corr']:.4f}.",
        f"El menor cambio logarítmico medio del ratio calibrado ocurre con periodo {smallest_lag_drift['period']}.",
        f"El periodo 2310 deja cambio log medio {next(row for row in lags if row['period'] == 2310)['mean_abs_log_calibrated_ratio_change']:.4f}.",
        f"El mayor salto vecino hacia arriba va de {largest_up['from']['n']} a {largest_up['to']['n']}: {largest_up['delta_pairs']:+,} pares.",
        f"En ese salto se ganan factores {largest_up['gained_factors']} y se pierden {largest_up['lost_factors']}.",
        f"El mayor salto vecino hacia abajo va de {largest_down['from']['n']} a {largest_down['to']['n']}: {largest_down['delta_pairs']:+,} pares.",
        f"En esa caída se pierden factores {largest_down['lost_factors']} y se ganan {largest_down['gained_factors']}.",
        f"Alrededor de 9699690, el centro queda rank {anchor_9699690['center_rank_by_pairs']} por pares dentro de ±20.",
        f"En la ventana ±20 de 9699690, el máximo es {anchor_9699690['window_max']['n']} con {anchor_9699690['window_max']['pairs']:,} pares.",
        f"En la ventana ±20 de 9699690, el mínimo es {anchor_9699690['window_min']['n']} con {anchor_9699690['window_min']['pairs']:,} pares.",
        f"Alrededor de 1112, el centro queda rank {anchor_1112['center_rank_by_pairs']} dentro de ±20.",
        f"En la ventana ±20 de 1112, el mínimo es {anchor_1112['window_min']['n']} con {anchor_1112['window_min']['pairs']} pares.",
        f"En la ventana ±20 de 1112, el máximo es {anchor_1112['window_max']['n']} con {anchor_1112['window_max']['pairs']} pares.",
        f"Alrededor de 2672, el centro queda rank {anchor_2672['center_rank_by_pairs']} dentro de ±20.",
        f"2672 es frío contra HL, pero en su ventana local el mínimo es {anchor_2672['window_min']['n']} con {anchor_2672['window_min']['pairs']} pares.",
        f"Los top fríos calibrados desde 1M son {', '.join(str(row['n']) for row in e1m['cold_ratio'][:5])}.",
        f"Los top calientes calibrados desde 1M son {', '.join(str(row['n']) for row in e1m['hot_ratio'][:5])}.",
        f"Los peores residuos negativos calibrados desde 1M son {', '.join(str(row['n']) for row in e1m['negative_residual'][:5])}.",
        f"Los mayores residuos positivos calibrados desde 1M son {', '.join(str(row['n']) for row in e1m['positive_residual'][:5])}.",
        "La rareza relativa extrema vive temprano; en los millones la rareza baja mucho en ratio.",
        "La rareza absoluta extrema vive tarde; en los millones los residuales son grandes pero con miles de pares.",
        "Los vecinos de records muestran que el boost singular es muy discontinuo: moverse +2 puede borrar muchos factores chicos.",
        "La comparación por lags muestra que repetir clase modular ayuda, pero no congela el residuo fino.",
        "La señal peligrosa para Goldbach tendría que ser ratio bajo y conteo bajo a la vez; en grandes no aparece.",
        "El round 4 deja una hipótesis precisa: los mínimos grandes son fluctuaciones calibradas normales sobre una base que ya crece muy lejos de cero.",
    ]


def make_next_experiments() -> list[str]:
    return [
        "Extender el análisis calibrado hasta 20M con solo métricas, sin CSV completo.",
        "Recalibrar por decil y buscar outliers dentro de cada decil por separado.",
        "Calcular gaps primos alrededor de n/2 para los fríos calibrados desde 1M.",
        "Auditar ventanas ±200 alrededor de los top records y top fríos.",
        "Medir cuántos factores chicos se pierden en cada salto vecino extremo.",
        "Comparar ratios calibrados entre n, n+2310 y n+30030.",
        "Construir una tabla de familias por firma exacta de factores chicos.",
        "Probar un modelo de residuo fino con features de gaps primos locales.",
        "Graficar bandas de percentiles calibrados por escala.",
        "Buscar el mínimo de pairs/calibrated_expected por ventanas móviles.",
        "Probar si los fríos desde 1M tienen n/2 dentro de un desierto primo.",
        "Crear un dashboard HTML de atlas local para anchors.",
        "Comparar conteo observado contra HL calibrado con constante por década.",
        "Buscar progresiones donde el ratio calibrado cae de forma persistente.",
        "Correr auditoría directa Miller-Rabin sobre los fríos grandes calibrados.",
    ]


def write_report(metrics: dict) -> None:
    lines = [
        "# Goldbach round 4: HL calibrado",
        "",
        f"Fuente: `{CSV_PATH.name}`.",
        f"Limite: {metrics['limit']:,}. Pares analizados: {metrics['rows']:,}.",
        f"Factor de calibracion HL: {metrics['calibration']:.6f}.",
        "",
        "## Patrones calibrados",
        "",
    ]
    for i, pattern in enumerate(metrics["patterns"], 1):
        lines.append(f"{i}. {pattern}")

    lines += ["", "## Siguientes experimentos", ""]
    for i, experiment in enumerate(metrics["next_experiments"], 1):
        lines.append(f"{i}. {experiment}")

    lines += [
        "",
        "## Fríos por escala",
        "",
        "| desde n | n | pares | ratio calibrado | residual calibrado | factores |",
        "|---:|---:|---:|---:|---:|---|",
    ]
    for lower in LOWER_BOUNDS:
        row = metrics["scale_extremes"][str(lower)]["cold_ratio"][0]
        lines.append(f"| {lower} | {row['n']} | {row['pairs']} | {row['calibrated_ratio']:.4f} | {row['calibrated_residual']:.2f} | {row['factors']} |")

    lines += ["", "## Estabilidad por lag", "", "| periodo | corr conteos | corr ratio calibrado | cambio log medio | delta pares medio |", "|---:|---:|---:|---:|---:|"]
    for row in metrics["lag_stability"]:
        lines.append(f"| {row['period']} | {row['count_corr']:.4f} | {row['calibrated_ratio_corr']:.4f} | {row['mean_abs_log_calibrated_ratio_change']:.4f} | {row['mean_abs_count_delta']:.2f} |")

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    counts = load_counts(CSV_PATH)
    limit = even_at(len(counts) - 1)
    primes = sieve_primes(limit)
    boost = build_singular_boost(len(counts), primes)
    ratios, expected, calibration = compute_ratios(counts, boost)
    metrics = {
        "limit": limit,
        "rows": len(counts),
        "calibration": calibration,
        "scale_extremes": scale_extremes(counts, ratios, expected, boost, calibration, primes),
        "scale_bands": scale_bands(counts, ratios, expected, calibration),
        "lag_stability": lag_stability(counts, ratios, calibration),
        "neighbor_shocks": neighbor_shocks(counts, ratios, expected, boost, calibration, primes),
        "local_atlas": local_atlas(counts, ratios, expected, boost, calibration, primes),
    }
    metrics["patterns"] = make_patterns(metrics)
    metrics["next_experiments"] = make_next_experiments()

    write_report(metrics)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Wrote {REPORT_PATH}")
    print(f"Wrote {METRICS_PATH}")
    print(f"Patterns: {len(metrics['patterns'])}")
    print(f"Next experiments: {len(metrics['next_experiments'])}")
    print(f"Calibration: {calibration:.6f}")
    print(f"Coldest >=1M: {metrics['scale_extremes']['1000000']['cold_ratio'][0]}")
    print(f"Lag 2310: {next(row for row in metrics['lag_stability'] if row['period'] == 2310)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
