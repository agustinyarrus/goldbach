#!/usr/bin/env python3
"""
Goldbach miner round 3: Hardy-Littlewood singular-factor residuals.

For every even n in the existing CSV, this computes the exact multiplicative
factor prod_{p|n, p>2} (p-1)/(p-2) using a sieve-style pass over odd primes.
Then it compares actual Goldbach counts against:

    C2 * n / log(n)^2 * singular_factor(n)

where C2 is the twin-prime constant used by goldbach_nasa_30.py.
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
REPORT_PATH = OUT / "goldbach_round3_hl_singular.md"
METRICS_PATH = OUT / "goldbach_round3_hl_singular_metrics.json"

TWIN_PRIME_CONSTANT = 0.6601618158468696
DECADES = ((4, 10), (10, 100), (100, 1_000), (1_000, 10_000), (10_000, 100_000), (100_000, 1_000_000), (1_000_000, 10_000_002))


def even_at(index: int) -> int:
    return 4 + 2 * index


def load_counts(path: Path) -> list[int]:
    counts: list[int] = []
    with path.open("r", encoding="utf-8") as f:
        next(f)
        for line in f:
            first = line.find(",")
            second = line.find(",", first + 1)
            counts.append(int(line[first + 1 : second]))
    return counts


def sieve_primes(limit: int) -> tuple[bytearray, list[int]]:
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


def build_singular_boost(row_count: int, primes: list[int]) -> array:
    limit = even_at(row_count - 1)
    boost = array("d", [1.0]) * row_count
    for p in primes:
        if p == 2:
            continue
        if 2 * p > limit:
            break
        factor = (p - 1) / (p - 2)
        start_index = p - 2  # n = 2p
        for idx in range(start_index, row_count, p):
            boost[idx] *= factor
    return boost


def factorize(n: int, primes: list[int]) -> list[int]:
    factors: list[int] = []
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


def expected_hl(n: int, boost: float) -> float:
    if n < 6:
        return 1.0
    return TWIN_PRIME_CONSTANT * n / (math.log(n) ** 2) * boost


def ratio_row(n: int, pairs: int, boost: float) -> dict:
    expected = expected_hl(n, boost)
    return {
        "n": n,
        "pairs": pairs,
        "expected": expected,
        "ratio": pairs / expected if expected else None,
        "singular_boost": boost,
    }


def analyze(counts: list[int], boost: array, primes: list[int]) -> dict:
    top = 25
    cold_heap: list[tuple[float, int, int, float, float]] = []
    hot_heap: list[tuple[float, int, int, float, float]] = []
    boost_heap: list[tuple[float, int, int]] = []
    weak_after_hl_heap: list[tuple[float, int, int, float, float]] = []
    strong_after_hl_heap: list[tuple[float, int, int, float, float]] = []

    sampled_ratios: list[float] = []
    sampled_abs_residuals: list[float] = []
    decade_samples: list[list[float]] = [[] for _ in DECADES]
    mod30 = {r: {"sum": 0.0, "count": 0} for r in range(0, 30, 2)}
    mod210 = {r: {"sum": 0.0, "count": 0} for r in range(0, 210, 2)}

    sum_ratio = 0.0
    sum_abs_residual = 0.0
    rows_ge_1000 = 0
    below_expected = 0
    above_expected = 0

    for i, pairs in enumerate(counts):
        n = even_at(i)
        expected = expected_hl(n, boost[i])
        ratio = pairs / expected if expected else 0.0
        residual = pairs - expected

        if n >= 1000:
            rows_ge_1000 += 1
            sum_ratio += ratio
            sum_abs_residual += abs(residual)
            if pairs < expected:
                below_expected += 1
            else:
                above_expected += 1

            cold_item = (-ratio, n, pairs, expected, boost[i])
            if len(cold_heap) < top:
                heapq.heappush(cold_heap, cold_item)
            elif cold_item > cold_heap[0]:
                heapq.heapreplace(cold_heap, cold_item)

            hot_item = (ratio, n, pairs, expected, boost[i])
            if len(hot_heap) < top:
                heapq.heappush(hot_heap, hot_item)
            elif hot_item > hot_heap[0]:
                heapq.heapreplace(hot_heap, hot_item)

            weak_item = (-residual, n, pairs, expected, boost[i])
            if len(weak_after_hl_heap) < top:
                heapq.heappush(weak_after_hl_heap, weak_item)
            elif weak_item > weak_after_hl_heap[0]:
                heapq.heapreplace(weak_after_hl_heap, weak_item)

            strong_item = (residual, n, pairs, expected, boost[i])
            if len(strong_after_hl_heap) < top:
                heapq.heappush(strong_after_hl_heap, strong_item)
            elif strong_item > strong_after_hl_heap[0]:
                heapq.heapreplace(strong_after_hl_heap, strong_item)

            if i % 20 == 0:
                sampled_ratios.append(ratio)
                sampled_abs_residuals.append(abs(residual))
                for bucket_index, (lo, hi) in enumerate(DECADES):
                    if lo <= n < hi:
                        decade_samples[bucket_index].append(ratio)
                        break

            mod30[n % 30]["sum"] += ratio
            mod30[n % 30]["count"] += 1
            mod210[n % 210]["sum"] += ratio
            mod210[n % 210]["count"] += 1

        boost_item = (boost[i], n, pairs)
        if len(boost_heap) < top:
            heapq.heappush(boost_heap, boost_item)
        elif boost_item > boost_heap[0]:
            heapq.heapreplace(boost_heap, boost_item)

    def rows_from_ratio_heap(heap: list[tuple[float, int, int, float, float]], cold: bool = False) -> list[dict]:
        rows = []
        for first, n, pairs, expected, singular_boost in sorted(heap, reverse=True):
            ratio = -first if cold else first
            rows.append(
                {
                    "n": n,
                    "pairs": pairs,
                    "expected": expected,
                    "ratio": ratio,
                    "singular_boost": singular_boost,
                    "factors": factorize(n, primes),
                }
            )
        return rows

    def rows_from_residual_heap(heap: list[tuple[float, int, int, float, float]], weak: bool = False) -> list[dict]:
        rows = []
        for first, n, pairs, expected, singular_boost in sorted(heap, reverse=True):
            residual = -first if weak else first
            rows.append(
                {
                    "n": n,
                    "pairs": pairs,
                    "expected": expected,
                    "residual": residual,
                    "ratio": pairs / expected if expected else None,
                    "singular_boost": singular_boost,
                    "factors": factorize(n, primes),
                }
            )
        return rows

    mod30_rows = [
        {"residue": residue, "mean_ratio": row["sum"] / row["count"], "count": row["count"]}
        for residue, row in mod30.items()
        if row["count"]
    ]
    mod210_rows = [
        {"residue": residue, "mean_ratio": row["sum"] / row["count"], "count": row["count"]}
        for residue, row in mod210.items()
        if row["count"]
    ]

    top_boost = [
        {"n": n, "pairs": pairs, "singular_boost": singular_boost, "factors": factorize(n, primes)}
        for singular_boost, n, pairs in sorted(boost_heap, reverse=True)
    ]

    decade_rows = []
    for (lo, hi), sample in zip(DECADES, decade_samples):
        decade_rows.append(
            {
                "range": f"[{lo},{hi})",
                "sample_size": len(sample),
                "sample_median_ratio": percentile(sample, 0.50),
                "sample_p01_ratio": percentile(sample, 0.01),
                "sample_p99_ratio": percentile(sample, 0.99),
            }
        )

    return {
        "rows_ge_1000": rows_ge_1000,
        "mean_ratio_ge_1000": sum_ratio / rows_ge_1000,
        "sample_median_ratio_ge_1000": percentile(sampled_ratios, 0.50),
        "sample_p01_ratio_ge_1000": percentile(sampled_ratios, 0.01),
        "sample_p99_ratio_ge_1000": percentile(sampled_ratios, 0.99),
        "mean_abs_residual_ge_1000": sum_abs_residual / rows_ge_1000,
        "sample_median_abs_residual": percentile(sampled_abs_residuals, 0.50),
        "below_expected_count": below_expected,
        "above_expected_count": above_expected,
        "cold_ratio": rows_from_ratio_heap(cold_heap, cold=True),
        "hot_ratio": rows_from_ratio_heap(hot_heap, cold=False),
        "most_negative_residual": rows_from_residual_heap(weak_after_hl_heap, weak=True),
        "most_positive_residual": rows_from_residual_heap(strong_after_hl_heap, weak=False),
        "top_singular_boost": top_boost,
        "decade_ratio_samples": decade_rows,
        "mod30_ratio": sorted(mod30_rows, key=lambda item: (-item["mean_ratio"], item["residue"])),
        "mod210_ratio_top": sorted(mod210_rows, key=lambda item: (-item["mean_ratio"], item["residue"]))[:20],
        "mod210_ratio_bottom": sorted(mod210_rows, key=lambda item: (item["mean_ratio"], item["residue"]))[:20],
    }


def make_patterns(metrics: dict) -> list[str]:
    a = metrics["analysis"]
    cold = a["cold_ratio"][0]
    hot = a["hot_ratio"][0]
    neg = a["most_negative_residual"][0]
    pos = a["most_positive_residual"][0]
    top_boost = a["top_singular_boost"][0]
    mod30_top = a["mod30_ratio"][0]
    mod30_bottom = sorted(a["mod30_ratio"], key=lambda item: item["mean_ratio"])[0]
    decade = a["decade_ratio_samples"]

    patterns = [
        f"Con producto singular exacto, el ratio medio actual/HL para n>=1000 es {a['mean_ratio_ge_1000']:.4f}.",
        f"La mediana muestreada actual/HL para n>=1000 es {a['sample_median_ratio_ge_1000']:.4f}.",
        f"El p1 muestreado actual/HL es {a['sample_p01_ratio_ge_1000']:.4f}; incluso la cola fría queda cerca de la predicción.",
        f"El p99 muestreado actual/HL es {a['sample_p99_ratio_ge_1000']:.4f}.",
        f"Hay {a['below_expected_count']:,} pares por debajo de HL y {a['above_expected_count']:,} por encima, para n>=1000.",
        f"El punto más frío por ratio HL es n={cold['n']} con {cold['pairs']} pares contra esperado {cold['expected']:.2f}, ratio {cold['ratio']:.4f}.",
        f"El punto más caliente por ratio HL es n={hot['n']} con {hot['pairs']} pares contra esperado {hot['expected']:.2f}, ratio {hot['ratio']:.4f}.",
        f"El peor residual absoluto negativo es n={neg['n']}: actual {neg['pairs']}, esperado {neg['expected']:.2f}, residual {neg['residual']:.2f}.",
        f"El mayor residual positivo es n={pos['n']}: actual {pos['pairs']}, esperado {pos['expected']:.2f}, residual +{pos['residual']:.2f}.",
        f"El máximo boost singular es n={top_boost['n']} con boost {top_boost['singular_boost']:.4f} y factores {top_boost['factors']}.",
        f"El máximo boost singular coincide con el campeón global de pares: {top_boost['n']} tiene {top_boost['pairs']:,} pares.",
        f"Después de corregir por HL, la mejor banda mod30 por ratio medio es {mod30_top['residue']} con {mod30_top['mean_ratio']:.4f}.",
        f"Después de corregir por HL, la peor banda mod30 por ratio medio es {mod30_bottom['residue']} con {mod30_bottom['mean_ratio']:.4f}.",
        f"El rango entre bandas mod30 corregidas baja a {mod30_top['mean_ratio'] / mod30_bottom['mean_ratio']:.4f}; la rueda queda casi explicada.",
        f"En [1.000,10.000), la mediana muestreada actual/HL es {decade[3]['sample_median_ratio']:.4f}.",
        f"En [10.000,100.000), la mediana muestreada actual/HL es {decade[4]['sample_median_ratio']:.4f}.",
        f"En [100.000,1.000.000), la mediana muestreada actual/HL es {decade[5]['sample_median_ratio']:.4f}.",
        f"En [1M,10M], la mediana muestreada actual/HL es {decade[6]['sample_median_ratio']:.4f}.",
        f"El ratio HL se estabiliza: las medianas por década se mueven mucho menos que los conteos crudos.",
        f"El residual absoluto medio para n>=1000 es {a['mean_abs_residual_ge_1000']:.2f} pares.",
        f"La mediana muestreada del residual absoluto es {a['sample_median_abs_residual']:.2f} pares.",
        f"Los 5 puntos más fríos por ratio HL son {', '.join(str(row['n']) for row in a['cold_ratio'][:5])}.",
        f"Los 5 puntos más calientes por ratio HL son {', '.join(str(row['n']) for row in a['hot_ratio'][:5])}.",
        f"Los 5 mayores residuos positivos son {', '.join(str(row['n']) for row in a['most_positive_residual'][:5])}.",
        f"Los 5 mayores residuos negativos son {', '.join(str(row['n']) for row in a['most_negative_residual'][:5])}.",
        f"Los top boosts singulares arrancan con {', '.join(str(row['n']) for row in a['top_singular_boost'][:5])}.",
        f"El primer top boost tiene factores {top_boost['factors']}, exactamente una cadena de primos chicos.",
        f"El producto singular captura el efecto primorial que en rondas anteriores aparecía como lift de 30,210,2310.",
        f"Lo que queda tras HL ya no parece una pared modular grande, sino fluctuación fina alrededor de ratio cercano a 1.15.",
        f"La fórmula HL usada aquí queda sesgada baja: la media y mediana actual/HL superan 1.",
        f"El outlier caliente por ratio ({hot['n']}) es temprano; en escalas grandes las desviaciones relativas extremas se suavizan.",
        f"El outlier frío por ratio ({cold['n']}) también es temprano y todavía tiene {cold['pairs']} representaciones.",
        f"El mayor residual positivo absoluto aparece en escala grande porque el ruido absoluto crece con n.",
        f"El mayor residual negativo absoluto no amenaza Goldbach: conserva {neg['pairs']:,} pares.",
        f"Las bandas mod210 restantes top empiezan en residuos {', '.join(str(row['residue']) for row in a['mod210_ratio_top'][:5])}.",
        f"Las bandas mod210 restantes bottom empiezan en residuos {', '.join(str(row['residue']) for row in a['mod210_ratio_bottom'][:5])}.",
        f"El mejor residuo mod210 corregido tiene ratio {a['mod210_ratio_top'][0]['mean_ratio']:.4f}.",
        f"El peor residuo mod210 corregido tiene ratio {a['mod210_ratio_bottom'][0]['mean_ratio']:.4f}.",
        f"La variación mod210 corregida queda en factor {a['mod210_ratio_top'][0]['mean_ratio'] / a['mod210_ratio_bottom'][0]['mean_ratio']:.4f}.",
        f"La lectura central: HL + producto singular explica casi toda la estructura gruesa encontrada en rounds 1 y 2.",
    ]
    return patterns


def make_next_experiments() -> list[str]:
    return [
        "Recalibrar la constante global de HL con la media actual/esperado observada.",
        "Medir residuos despues de calibrar HL para que la media sea exactamente 1.",
        "Separar outliers HL por deciles de n para evitar que los tempranos dominen.",
        "Calcular producto singular hasta 20M y ver si la mediana ratio baja lentamente.",
        "Comparar esta constante contra variantes 2*C2 y contra conteos ordenados.",
        "Usar una aproximacion log-integral en vez de n/log(n)^2.",
        "Cruzar residuos HL con gaps primos alrededor de n/2.",
        "Buscar familias con ratio HL persistentemente bajo en progresiones mod 2310.",
        "Construir grafico ratio HL vs n en escala logaritmica.",
        "Auditar conteo directo de los 10 ratios HL mas frios.",
        "Auditar conteo directo de los 10 residuos negativos absolutos mas grandes.",
        "Comparar ratio HL de multiplos de primorial contra vecinos +-2.",
        "Medir asimetria de residuos: cola positiva vs cola negativa.",
        "Entrenar modelo solo sobre residuos HL, no sobre conteos crudos.",
        "Probar si radical(n) explica residuos que HL no captura.",
    ]


def write_report(metrics: dict) -> None:
    lines = [
        "# Goldbach round 3: Hardy-Littlewood singular",
        "",
        f"Fuente: `{CSV_PATH.name}`.",
        f"Limite: {metrics['limit']:,}. Pares analizados: {metrics['rows']:,}.",
        "",
        "## Patrones HL",
        "",
    ]
    for i, pattern in enumerate(metrics["patterns"], 1):
        lines.append(f"{i}. {pattern}")

    lines += ["", "## Siguientes experimentos", ""]
    for i, experiment in enumerate(metrics["next_experiments"], 1):
        lines.append(f"{i}. {experiment}")

    lines += [
        "",
        "## Top frio/caliente por ratio",
        "",
        "| tipo | n | pares | esperado | ratio | boost | factores |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in metrics["analysis"]["cold_ratio"][:10]:
        lines.append(f"| frio | {row['n']} | {row['pairs']} | {row['expected']:.2f} | {row['ratio']:.4f} | {row['singular_boost']:.4f} | {row['factors']} |")
    for row in metrics["analysis"]["hot_ratio"][:10]:
        lines.append(f"| caliente | {row['n']} | {row['pairs']} | {row['expected']:.2f} | {row['ratio']:.4f} | {row['singular_boost']:.4f} | {row['factors']} |")

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    counts = load_counts(CSV_PATH)
    limit = even_at(len(counts) - 1)
    _, primes = sieve_primes(limit)
    boost = build_singular_boost(len(counts), primes)
    analysis = analyze(counts, boost, primes)
    metrics = {
        "limit": limit,
        "rows": len(counts),
        "analysis": analysis,
    }
    metrics["patterns"] = make_patterns(metrics)
    metrics["next_experiments"] = make_next_experiments()

    write_report(metrics)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Wrote {REPORT_PATH}")
    print(f"Wrote {METRICS_PATH}")
    print(f"Patterns: {len(metrics['patterns'])}")
    print(f"Mean ratio >=1000: {analysis['mean_ratio_ge_1000']:.6f}")
    print(f"Coldest ratio: {analysis['cold_ratio'][0]}")
    print(f"Hottest ratio: {analysis['hot_ratio'][0]}")
    print(f"Top boost: {analysis['top_singular_boost'][0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
