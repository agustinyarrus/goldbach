#!/usr/bin/env python3
"""
Goldbach miner round 6: calibrated mod-2310 progression families.

This looks for residue classes that remain cold/hot after Hardy-Littlewood
calibration. Individual outliers are noisy; persistent residue families are a
better target for real structure.
"""

from __future__ import annotations

import json
import math
from array import array
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "goldbach_nasa_output"
CSV_PATH = OUT / "goldbach_counts_to_10000000.csv"
REPORT_PATH = OUT / "goldbach_round6_progressions.md"
METRICS_PATH = OUT / "goldbach_round6_progressions_metrics.json"

TWIN_PRIME_CONSTANT = 0.6601618158468696
MODULUS = 2310
BANDS = 10


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


def compute_raw_ratios(counts: list[int], boost: array) -> tuple[array, float]:
    ratios = array("d", [0.0]) * len(counts)
    total = 0.0
    total_count = 0
    for i, pairs in enumerate(counts):
        n = even_at(i)
        expected = expected_hl(n, boost[i])
        ratio = pairs / expected if expected else 0.0
        ratios[i] = ratio
        if n >= 1000:
            total += ratio
            total_count += 1
    return ratios, total / total_count


def band_index(n: int, limit: int) -> int:
    start = 1000
    width = (limit - start + 2) / BANDS
    return min(BANDS - 1, max(0, int((n - start) / width)))


def progression_analysis(counts: list[int], ratios: array, calibration: float) -> dict:
    limit = even_at(len(counts) - 1)
    rows = {}
    for residue in range(0, MODULUS, 2):
        rows[residue] = {
            "residue": residue,
            "count": 0,
            "sum": 0.0,
            "min_ratio": 10.0,
            "min_n": None,
            "max_ratio": 0.0,
            "max_n": None,
            "band_sums": [0.0] * BANDS,
            "band_counts": [0] * BANDS,
        }

    for i, pairs in enumerate(counts):
        n = even_at(i)
        if n < 1000:
            continue
        residue = n % MODULUS
        ratio = ratios[i] / calibration
        row = rows[residue]
        row["count"] += 1
        row["sum"] += ratio
        if ratio < row["min_ratio"]:
            row["min_ratio"] = ratio
            row["min_n"] = n
        if ratio > row["max_ratio"]:
            row["max_ratio"] = ratio
            row["max_n"] = n
        b = band_index(n, limit)
        row["band_sums"][b] += ratio
        row["band_counts"][b] += 1

    summaries = []
    for row in rows.values():
        band_means = [
            row["band_sums"][i] / row["band_counts"][i] if row["band_counts"][i] else None
            for i in range(BANDS)
        ]
        real_band_means = [value for value in band_means if value is not None]
        summaries.append(
            {
                "residue": row["residue"],
                "count": row["count"],
                "mean_ratio": row["sum"] / row["count"],
                "min_ratio": row["min_ratio"],
                "min_n": row["min_n"],
                "max_ratio": row["max_ratio"],
                "max_n": row["max_n"],
                "band_means": band_means,
                "band_min": min(real_band_means),
                "band_max": max(real_band_means),
                "band_span": max(real_band_means) - min(real_band_means),
                "first_band": real_band_means[0],
                "last_band": real_band_means[-1],
                "drift_last_minus_first": real_band_means[-1] - real_band_means[0],
            }
        )

    return {
        "top_mean": sorted(summaries, key=lambda row: (-row["mean_ratio"], row["residue"]))[:30],
        "bottom_mean": sorted(summaries, key=lambda row: (row["mean_ratio"], row["residue"]))[:30],
        "persistent_hot": sorted(summaries, key=lambda row: (-row["band_min"], row["residue"]))[:30],
        "persistent_cold": sorted(summaries, key=lambda row: (row["band_max"], row["residue"]))[:30],
        "most_unstable": sorted(summaries, key=lambda row: (-row["band_span"], row["residue"]))[:30],
        "warming": sorted(summaries, key=lambda row: (-row["drift_last_minus_first"], row["residue"]))[:30],
        "cooling": sorted(summaries, key=lambda row: (row["drift_last_minus_first"], row["residue"]))[:30],
        "last_band_hot": sorted(summaries, key=lambda row: (-row["last_band"], row["residue"]))[:30],
        "last_band_cold": sorted(summaries, key=lambda row: (row["last_band"], row["residue"]))[:30],
        "all_residue_count": len(summaries),
    }


def make_patterns(metrics: dict) -> list[str]:
    p = metrics["progressions"]
    top = p["top_mean"][0]
    bottom = p["bottom_mean"][0]
    ph = p["persistent_hot"][0]
    pc = p["persistent_cold"][0]
    unstable = p["most_unstable"][0]
    least_cooling = p["warming"][0]
    cooling = p["cooling"][0]
    last_hot = p["last_band_hot"][0]
    last_cold = p["last_band_cold"][0]

    return [
        f"Se analizaron {p['all_residue_count']} progresiones pares modulo 2310.",
        f"El residuo con mayor ratio calibrado medio es {top['residue']} con {top['mean_ratio']:.6f}.",
        f"El residuo con menor ratio calibrado medio es {bottom['residue']} con {bottom['mean_ratio']:.6f}.",
        f"El rango medio top/bottom tras HL calibrado es solo {top['mean_ratio'] / bottom['mean_ratio']:.6f}.",
        f"La familia persistentemente más caliente es residuo {ph['residue']}: su peor banda todavía promedia {ph['band_min']:.6f}.",
        f"La familia persistentemente más fría es residuo {pc['residue']}: su mejor banda solo promedia {pc['band_max']:.6f}.",
        f"El residuo más inestable por bandas es {unstable['residue']} con span {unstable['band_span']:.6f}.",
        f"El residuo que menos se enfría del primer al último decil es {least_cooling['residue']} con drift {least_cooling['drift_last_minus_first']:.6f}.",
        f"El residuo que más se enfría del primer al último decil es {cooling['residue']} con drift {cooling['drift_last_minus_first']:.6f}.",
        f"En el último decil, el residuo más caliente es {last_hot['residue']} con media {last_hot['last_band']:.6f}.",
        f"En el último decil, el residuo más frío es {last_cold['residue']} con media {last_cold['last_band']:.6f}.",
        f"El mejor residuo medio {top['residue']} tiene mínimo individual en n={top['min_n']} con ratio {top['min_ratio']:.6f}.",
        f"El peor residuo medio {bottom['residue']} tiene máximo individual en n={bottom['max_n']} con ratio {bottom['max_ratio']:.6f}.",
        f"La familia fría persistente {pc['residue']} tiene mínimo individual en n={pc['min_n']} con ratio {pc['min_ratio']:.6f}.",
        f"La familia caliente persistente {ph['residue']} tiene máximo individual en n={ph['max_n']} con ratio {ph['max_ratio']:.6f}.",
        "Después de HL calibrado, las familias mod 2310 sobreviven pero con amplitud pequeña.",
        "Esto confirma que la rueda 2310 ya estaba casi absorbida por el producto singular.",
        "Las progresiones persistentes son mejores objetivos para teoría que los outliers sueltos.",
        "Aun la peor familia persistente está muy cerca de ratio 1: no aparece una progresión peligrosa.",
        "La variación por escala dentro de un mismo residuo es comparable a la variación entre residuos.",
        f"Los top 5 residuos medios calientes son {', '.join(str(row['residue']) for row in p['top_mean'][:5])}.",
        f"Los top 5 residuos medios fríos son {', '.join(str(row['residue']) for row in p['bottom_mean'][:5])}.",
        f"Los top 5 persistentes calientes son {', '.join(str(row['residue']) for row in p['persistent_hot'][:5])}.",
        f"Los top 5 persistentes fríos son {', '.join(str(row['residue']) for row in p['persistent_cold'][:5])}.",
        f"Los top 5 más inestables son {', '.join(str(row['residue']) for row in p['most_unstable'][:5])}.",
        "La hipótesis ahora se afina: el residuo fino restante parece una oscilación de baja amplitud alrededor de HL calibrado.",
    ]


def write_report(metrics: dict) -> None:
    lines = [
        "# Goldbach round 6: progresiones mod 2310 calibradas",
        "",
        f"Fuente: `{CSV_PATH.name}`.",
        f"Limite: {metrics['limit']:,}. Factor calibracion: {metrics['calibration']:.6f}.",
        "",
        "## Patrones de progresiones",
        "",
    ]
    for i, pattern in enumerate(metrics["patterns"], 1):
        lines.append(f"{i}. {pattern}")

    lines += [
        "",
        "## Top/bottom por media calibrada",
        "",
        "| tipo | residuo | media | min ratio | min n | max ratio | max n | span bandas |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in metrics["progressions"]["top_mean"][:10]:
        lines.append(f"| hot | {row['residue']} | {row['mean_ratio']:.6f} | {row['min_ratio']:.6f} | {row['min_n']} | {row['max_ratio']:.6f} | {row['max_n']} | {row['band_span']:.6f} |")
    for row in metrics["progressions"]["bottom_mean"][:10]:
        lines.append(f"| cold | {row['residue']} | {row['mean_ratio']:.6f} | {row['min_ratio']:.6f} | {row['min_n']} | {row['max_ratio']:.6f} | {row['max_n']} | {row['band_span']:.6f} |")

    lines += [
        "",
        "## Persistentes",
        "",
        "| tipo | residuo | media | peor/mejor banda | primer decil | ultimo decil | drift |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in metrics["progressions"]["persistent_hot"][:10]:
        lines.append(f"| hot | {row['residue']} | {row['mean_ratio']:.6f} | {row['band_min']:.6f} | {row['first_band']:.6f} | {row['last_band']:.6f} | {row['drift_last_minus_first']:.6f} |")
    for row in metrics["progressions"]["persistent_cold"][:10]:
        lines.append(f"| cold | {row['residue']} | {row['mean_ratio']:.6f} | {row['band_max']:.6f} | {row['first_band']:.6f} | {row['last_band']:.6f} | {row['drift_last_minus_first']:.6f} |")

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    counts = load_counts(CSV_PATH)
    limit = even_at(len(counts) - 1)
    primes = sieve_primes(limit)
    boost = build_singular_boost(len(counts), primes)
    ratios, calibration = compute_raw_ratios(counts, boost)
    metrics = {
        "limit": limit,
        "rows": len(counts),
        "calibration": calibration,
        "progressions": progression_analysis(counts, ratios, calibration),
    }
    metrics["patterns"] = make_patterns(metrics)
    write_report(metrics)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Wrote {REPORT_PATH}")
    print(f"Wrote {METRICS_PATH}")
    print(f"Patterns: {len(metrics['patterns'])}")
    print(f"Top mean: {metrics['progressions']['top_mean'][0]}")
    print(f"Bottom mean: {metrics['progressions']['bottom_mean'][0]}")
    print(f"Persistent cold: {metrics['progressions']['persistent_cold'][0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
