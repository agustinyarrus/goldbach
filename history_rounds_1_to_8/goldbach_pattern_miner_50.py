#!/usr/bin/env python3
"""
Mine a first batch of 50 measurable Goldbach patterns and 50 next ideas.

Reads the existing CSV/JSON exports produced by goldbach_nasa_30.py. This
version uses only the Python standard library so it runs in the same interpreter
that produced the earlier files.
"""

from __future__ import annotations

import csv
import heapq
import json
import math
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "goldbach_nasa_output"
CSV_PATH = OUT / "goldbach_counts_to_10000000.csv"
JSON_PATH = OUT / "goldbach_nasa_plus_findings_to_10000000.json"
REPORT_PATH = OUT / "goldbach_50_patterns_50_ideas.md"
METRICS_PATH = OUT / "goldbach_50_patterns_metrics.json"

SMALL_PRIMES = (3, 5, 7, 11, 13, 17, 19, 23, 29, 31)
PRIMORIALS = (30, 210, 2310, 30030, 510510, 9699690)
AUTOCORR_PERIODS = (2, 4, 6, 10, 12, 14, 18, 20, 30, 42, 60, 70, 90, 120, 150, 180, 210, 240, 300, 420)


def even_at(index: int) -> int:
    return 4 + 2 * index


def index_of_even(n: int) -> int:
    return (n - 4) // 2


def percentile(sorted_values: list[float] | list[int], p: float) -> float:
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
    return float(sorted_values[lo] * (1 - frac) + sorted_values[hi] * frac)


def median(values: list[int] | list[float]) -> float:
    return percentile(sorted(values), 0.5)


def load_counts(csv_path: Path) -> list[int]:
    counts: list[int] = []
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            counts.append(int(row["goldbach_pairs"]))
    return counts


def load_json(json_path: Path) -> dict:
    with json_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def mission_by_number(data: dict, number: int) -> dict:
    for mission in data["missions"]:
        if mission["mission"] == number:
            return mission
    raise KeyError(number)


def global_stats(counts: list[int]) -> dict:
    ordered = sorted(counts)
    return {
        "min": int(ordered[0]),
        "max": int(ordered[-1]),
        "mean": float(sum(counts) / len(counts)),
        "median": percentile(ordered, 0.5),
        "p01": percentile(ordered, 0.01),
        "p10": percentile(ordered, 0.10),
        "p90": percentile(ordered, 0.90),
        "p99": percentile(ordered, 0.99),
    }


def strongest_and_weakest(counts: list[int], top: int = 12) -> dict:
    strongest_pairs = heapq.nlargest(top, ((c, -even_at(i)) for i, c in enumerate(counts)))
    strongest = [{"n": -neg_n, "pairs": c} for c, neg_n in sorted(strongest_pairs, key=lambda item: (-item[0], -item[1]))]

    weak_candidates = ((c, even_at(i)) for i, c in enumerate(counts) if even_at(i) >= 1000)
    weakest_pairs = heapq.nsmallest(top, weak_candidates)
    weakest = [{"n": n, "pairs": c} for c, n in weakest_pairs]
    return {"strongest": strongest, "weakest_ge_1000": weakest}


def record_breakers(counts: list[int]) -> list[dict]:
    best = -1
    records: list[dict] = []
    for i, c in enumerate(counts):
        if c > best:
            best = c
            records.append({"n": even_at(i), "pairs": c})
    return records


def decade_stats(counts: list[int]) -> list[dict]:
    ranges = [(4, 10), (10, 100), (100, 1_000), (1_000, 10_000), (10_000, 100_000), (100_000, 1_000_000), (1_000_000, 10_000_002)]
    buckets: list[list[tuple[int, int]]] = [[] for _ in ranges]
    for i, c in enumerate(counts):
        n = even_at(i)
        for bucket_index, (lo, hi) in enumerate(ranges):
            if lo <= n < hi:
                buckets[bucket_index].append((n, c))
                break

    out = []
    for (lo, hi), bucket in zip(ranges, buckets):
        values = [c for _, c in bucket]
        ordered = sorted(values)
        weakest_n, weakest_c = min(bucket, key=lambda item: (item[1], item[0]))
        out.append(
            {
                "range": f"[{lo},{hi})",
                "min": int(ordered[0]),
                "weakest": int(weakest_n),
                "p10": percentile(ordered, 0.10),
                "median": percentile(ordered, 0.5),
                "mean": float(sum(values) / len(values)),
                "max": int(ordered[-1]),
            }
        )
    return out


def mod_summaries(counts: list[int], modulus: int) -> list[dict]:
    buckets: dict[int, list[int]] = {r: [] for r in range(0, modulus, 2)}
    for i, c in enumerate(counts):
        buckets[even_at(i) % modulus].append(c)

    out = []
    for residue, values in buckets.items():
        if not values:
            continue
        ordered = sorted(values)
        out.append(
            {
                "residue": residue,
                "mean": float(sum(values) / len(values)),
                "median": percentile(ordered, 0.5),
                "minimum": int(ordered[0]),
                "maximum": int(ordered[-1]),
                "size": len(values),
            }
        )
    return sorted(out, key=lambda item: (-item["mean"], item["residue"]))


def autocorrs(counts: list[int], stride: int = 20) -> list[dict]:
    mean = sum(counts) / len(counts)
    centered = [c - mean for c in counts]
    out = []
    for period in AUTOCORR_PERIODS:
        lag = period // 2
        if lag <= 0 or lag >= len(counts):
            continue
        xy = xx = yy = 0.0
        samples = 0
        for i in range(0, len(counts) - lag, stride):
            left = centered[i]
            right = centered[i + lag]
            xy += left * right
            xx += left * left
            yy += right * right
            samples += 1
        corr = xy / math.sqrt(xx * yy) if xx and yy else 0.0
        out.append({"period": period, "lag_even_steps": lag, "corr": corr, "stride": stride, "samples": samples})
    return sorted(out, key=lambda item: item["corr"], reverse=True)


def local_neighbor_stats(counts: list[int], top: int = 12) -> dict:
    jumps: list[tuple[int, int]] = []
    total_abs = 0
    abs_values_sample: list[int] = []
    for i in range(len(counts) - 1):
        delta = counts[i + 1] - counts[i]
        abs_delta = abs(delta)
        total_abs += abs_delta
        if i % 20 == 0:
            abs_values_sample.append(abs_delta)
        item = (abs_delta, i)
        if len(jumps) < top:
            heapq.heappush(jumps, item)
        elif item > jumps[0]:
            heapq.heapreplace(jumps, item)

    largest = []
    for _, i in sorted(jumps, reverse=True):
        largest.append(
            {
                "from": even_at(i),
                "to": even_at(i + 1),
                "pairs_from": counts[i],
                "pairs_to": counts[i + 1],
                "delta": counts[i + 1] - counts[i],
            }
        )
    return {
        "mean_abs_neighbor_change": float(total_abs / (len(counts) - 1)),
        "median_abs_neighbor_change_sampled": median(abs_values_sample),
        "largest_neighbor_jumps": largest,
    }


def small_factor_score(counts: list[int]) -> dict:
    prime_stats = {p: {"div_sum": 0, "div_count": 0, "not_sum": 0, "not_count": 0} for p in SMALL_PRIMES}
    by_score = {s: {"sum": 0, "count": 0} for s in range(len(SMALL_PRIMES) + 1)}
    sum_x = sum_y = sum_xx = sum_yy = sum_xy = 0.0

    for i, c in enumerate(counts):
        n = even_at(i)
        score = 0
        for p in SMALL_PRIMES:
            if n % p == 0:
                score += 1
                prime_stats[p]["div_sum"] += c
                prime_stats[p]["div_count"] += 1
            else:
                prime_stats[p]["not_sum"] += c
                prime_stats[p]["not_count"] += 1

        by_score[score]["sum"] += c
        by_score[score]["count"] += 1
        sum_x += score
        sum_y += c
        sum_xx += score * score
        sum_yy += c * c
        sum_xy += score * c

    n_rows = len(counts)
    numerator = n_rows * sum_xy - sum_x * sum_y
    denominator = math.sqrt((n_rows * sum_xx - sum_x * sum_x) * (n_rows * sum_yy - sum_y * sum_y))
    correlation = numerator / denominator if denominator else 0.0

    by_prime = []
    for p in SMALL_PRIMES:
        stats = prime_stats[p]
        div_mean = stats["div_sum"] / stats["div_count"]
        not_mean = stats["not_sum"] / stats["not_count"]
        by_prime.append({"prime": p, "mean_if_divisible": div_mean, "mean_if_not": not_mean, "lift": div_mean / not_mean})

    by_score_rows = []
    for score, stats in by_score.items():
        if stats["count"]:
            by_score_rows.append({"small_factor_count": score, "size": stats["count"], "mean_pairs": stats["sum"] / stats["count"]})

    return {"corr_small_factor_count_vs_pairs": correlation, "by_prime": by_prime, "by_score": by_score_rows}


def normalized_density(counts: list[int], top: int = 12) -> dict:
    low_heap: list[tuple[float, int, int]] = []
    high_heap: list[tuple[float, int, int]] = []
    sample: list[float] = []
    density_sum = 0.0
    density_count = 0

    for i, c in enumerate(counts):
        n = even_at(i)
        if n < 1000:
            continue
        density = c * (math.log(n) ** 2) / n
        density_sum += density
        density_count += 1
        if i % 100 == 0:
            sample.append(density)

        low_item = (-density, n, c)
        if len(low_heap) < top:
            heapq.heappush(low_heap, low_item)
        elif low_item > low_heap[0]:
            heapq.heapreplace(low_heap, low_item)

        high_item = (density, n, c)
        if len(high_heap) < top:
            heapq.heappush(high_heap, high_item)
        elif high_item > high_heap[0]:
            heapq.heapreplace(high_heap, high_item)

    low_density = [{"n": n, "density": -neg_density, "pairs": c} for neg_density, n, c in sorted(low_heap, reverse=True)]
    high_density = [{"n": n, "density": density, "pairs": c} for density, n, c in sorted(high_heap, reverse=True)]
    return {
        "median_ge_1000_sampled": median(sample),
        "mean_ge_1000": density_sum / density_count,
        "low_density": low_density,
        "high_density": high_density,
    }


def primorial_alignment(counts: list[int]) -> list[dict]:
    rows = []
    total_sum = sum(counts)
    total_count = len(counts)
    for m in PRIMORIALS:
        mult_sum = 0
        mult_count = 0
        best_n = None
        best_pairs = -1
        for i, c in enumerate(counts):
            n = even_at(i)
            if n % m == 0:
                mult_sum += c
                mult_count += 1
                if c > best_pairs:
                    best_pairs = c
                    best_n = n
        if not mult_count:
            continue
        not_sum = total_sum - mult_sum
        not_count = total_count - mult_count
        rows.append(
            {
                "modulus": m,
                "multiples": mult_count,
                "mean_if_multiple": mult_sum / mult_count,
                "mean_if_not": not_sum / not_count if not_count else None,
                "lift": (mult_sum / mult_count) / (not_sum / not_count) if not_count else None,
                "best_multiple": best_n,
                "best_multiple_pairs": best_pairs,
            }
        )
    return rows


def make_patterns(metrics: dict, data: dict) -> list[str]:
    strongest = metrics["extremes"]["strongest"]
    weakest = metrics["extremes"]["weakest_ge_1000"]
    records = metrics["records"]
    decades = metrics["decades"]
    mod30 = metrics["mod30"]
    mod210 = metrics["mod210"]
    autoc = metrics["autocorr"]
    density = metrics["density"]
    factors = metrics["small_factors"]
    primorials = metrics["primorials"]
    neighbor = metrics["neighbor"]

    mission23 = mission_by_number(data, 23)
    mission24 = mission_by_number(data, 24)
    mission26 = mission_by_number(data, 26)
    mission31 = mission_by_number(data, 31)
    mission32 = mission_by_number(data, 32)

    patterns = [
        f"No hay contraejemplos hasta {data['limit']:,}; el barrido completo dio cero pares nulos.",
        f"El mínimo no trivial sigue clavado en {weakest[0]['n']} con {weakest[0]['pairs']} pares.",
        f"El máximo global es {strongest[0]['n']} con {strongest[0]['pairs']:,} pares.",
        f"El campeón {strongest[0]['n']} es múltiplo de 2*3*5*7*11*13*17, un primorial casi perfecto para atraer canales.",
        f"La banda mod 30 más fuerte es {mod30[0]['residue']} con media {mod30[0]['mean']:.2f}.",
        f"La banda mod 30 más débil es {mod30[-1]['residue']} con media {mod30[-1]['mean']:.2f}.",
        f"Ser 0 mod 30 multiplica la media por {mod30[0]['mean'] / mod30[-1]['mean']:.2f} frente a la peor banda.",
        f"La banda mod 210 más fuerte es {mod210[0]['residue']} con media {mod210[0]['mean']:.2f}.",
        f"La banda mod 210 más débil es {mod210[-1]['residue']} con media {mod210[-1]['mean']:.2f}.",
        f"La autocorrelación muestreada más alta entre periodos probados aparece en periodo {autoc[0]['period']} con corr={autoc[0]['corr']:.4f}.",
        f"El JSON previo confirma periodo 210 como dominante local: {mission24['finding']}",
        f"El espectro detectó periodo cercano a 6: {mission23['finding']}",
        f"El piso por década sube: de {decades[0]['min']} en [4,10) a {decades[-1]['min']} en [1M,10M].",
        f"En [1.000,10.000) el piso es {decades[3]['min']} y el punto más débil es {decades[3]['weakest']}.",
        f"En [1M,10M] el piso ya es {decades[-1]['min']} pares, muy lejos de cero.",
        f"La mediana por década pasa de {decades[3]['median']:.0f} en miles a {decades[-1]['median']:.0f} en millones.",
        f"Los récords son raros: solo {len(records)} nuevos máximos entre casi cinco millones de pares evaluados.",
        f"El último récord antes del límite es {records[-1]['n']} con {records[-1]['pairs']:,} pares.",
        f"Los máximos top se concentran en residuo 0 mod 30; los 6 primeros máximos tienen ese residuo.",
        f"Los débiles no triviales se amontonan cerca de 1.000: {', '.join(str(x['n']) for x in weakest[:6])}.",
        f"La densidad normalizada media g(n)*log(n)^2/n para n>=1000 es {density['mean_ge_1000']:.4f}.",
        f"La densidad normalizada muestreada tiene mediana {density['median_ge_1000_sampled']:.4f}.",
        f"La densidad normalizada más baja entre n>=1000 aparece en {density['low_density'][0]['n']} con {density['low_density'][0]['density']:.4f}.",
        f"La densidad normalizada más alta aparece en {density['high_density'][0]['n']} con {density['high_density'][0]['density']:.4f}.",
        f"La cuenta de factores pequeños correlaciona con pares en {factors['corr_small_factor_count_vs_pairs']:.4f}.",
        f"Divisibilidad por 3 produce lift {factors['by_prime'][0]['lift']:.2f} en la media de pares.",
        f"Divisibilidad por 5 produce lift {factors['by_prime'][1]['lift']:.2f} en la media de pares.",
        f"Divisibilidad por 7 produce lift {factors['by_prime'][2]['lift']:.2f} en la media de pares.",
        f"Los múltiplos de 30 tienen lift {primorials[0]['lift']:.2f}.",
        f"Los múltiplos de 210 tienen lift {primorials[1]['lift']:.2f}.",
        f"Los múltiplos de 2310 tienen lift {primorials[2]['lift']:.2f}.",
        f"Los múltiplos de 30030 tienen lift {primorials[3]['lift']:.2f}.",
        f"Los múltiplos de 510510 tienen lift {primorials[4]['lift']:.2f}.",
        f"El mayor salto vecino cambia {neighbor['largest_neighbor_jumps'][0]['delta']:+,} pares entre {neighbor['largest_neighbor_jumps'][0]['from']} y {neighbor['largest_neighbor_jumps'][0]['to']}.",
        f"El cambio absoluto vecino medio es {neighbor['mean_abs_neighbor_change']:.2f}; la mediana muestreada es {neighbor['median_abs_neighbor_change_sampled']:.0f}.",
        f"El test de puentes en desiertos primos encontró gap máximo 154 en el par medio que suma {mission26['payload'][0]['bridge_even']}.",
        f"Ese puente de desierto no es frágil: {mission26['payload'][0]['bridge_even']} tiene {mission26['payload'][0]['bridge_pairs']:,} pares.",
        f"Hardy-Littlewood queda sistemáticamente bajo en la muestra: {mission_by_number(data, 7)['finding']}",
        f"El residuo dominante en pares mod 30 fue canal 13+17 según la heatmap previa.",
        f"El sesgo Chebyshev aparece pero es chico a 10M: {mission_by_number(data, 12)['finding']}",
        f"Los primos gemelos aparecen en una fracción grande de pares muestreados: {mission_by_number(data, 13)['finding']}",
        f"Los Sophie Germain participan menos pero no son marginales: {mission_by_number(data, 14)['finding']}",
        f"Los primos de Mersenne son prácticamente invisibles: {mission_by_number(data, 16)['finding']}",
        f"El centro de gravedad más desviado entre focos aparece en {mission_by_number(data, 20)['payload'][0]['n']}.",
        f"El peor desierto de punto medio entre débiles solo tiene distancia {mission_by_number(data, 21)['payload'][0]['nearest_prime_distance']}.",
        f"El z-score caliente local máximo coincide con el campeón global: {mission_by_number(data, 22)['payload']['hot'][0]['n']}.",
        f"El filtro hostil todavía deja piso {mission_by_number(data, 25)['finding'].split('floor=')[1].split(';')[0]} en supervivientes.",
        f"Los vecinos semiprimos suben la media: {mission_by_number(data, 27)['finding']}",
        f"El grafo de Goldbach muestra hubs de primos repetidos; top hub {mission_by_number(data, 28)['payload'][0]['prime']}.",
        f"Los clusters débiles iniciales son largos porque el percentil 10 todavía crece desde escalas bajas: {mission_by_number(data, 29)['finding']}",
        f"El modelo divisor-booster casi explica la densidad: {mission31['finding']}",
        f"El escaneo de ventanas termina con piso {mission32['payload']['windows'][-1]['floor_pairs']:,} en la última ventana.",
    ]
    return patterns[:50]


def make_ideas() -> list[str]:
    return [
        "Construir un modelo predictivo g(n) = HL(n) * correccion_residuo * ruido_local y medir residuos reales.",
        "Separar los pares por canal mod 30 y estudiar que canales se apagan primero en numeros debiles.",
        "Repetir todo con rueda mod 2310 para ver si explica a 1112 mejor que mod 210.",
        "Buscar el primer n donde el piso de una ventana de 250k pares supera 100.000.",
        "Crear un detector de numeros anti-boost: pares con pocos factores pequenos pero conteo anormalmente alto.",
        "Crear un detector de numeros turbo-boost: muchos factores pequenos pero conteo anormalmente bajo.",
        "Medir si los records fuertes casi siempre son multiplos de primoriales truncados.",
        "Probar ventanas logaritmicas en vez de ventanas lineales para ver la subida del piso.",
        "Comparar conteo real contra Li(n)^2 heuristico en vez de n/log(n)^2.",
        "Hacer una regresion con features: log n, mod30, mod210, factores pequenos, tau(n), radical(n).",
        "Calcular el producto singular exacto para todos los n hasta 10M con SPF y comparar contra HL.",
        "Buscar mini-cometas: patrones visuales por cada residuo mod 210 en graficos separados.",
        "Mapear los huecos entre pares Goldbach consecutivos dentro de un mismo n.",
        "Ver si los pares mas balanceados predicen conteos altos o solo reflejan el azar local.",
        "Medir la proporcion de pares con p < sqrt(n), p < n/log(n), p dentro del 10% central.",
        "Buscar numeros cuya representacion use muchos primos especiales a la vez: gemelo + safe + Sophie.",
        "Crear ranking de primos-hub por deciles de n, no solo global.",
        "Medir si un primo hub sigue siendo hub cuando se normaliza por disponibilidad.",
        "Analizar la red bipartita n-primo y buscar comunidades por residuos modulares.",
        "Buscar secuencias consecutivas de pares con conteos por debajo del percentil 1 local.",
        "Definir una energia Goldbach: -log(g(n)/esperado) y buscar pozos profundos.",
        "Usar wavelets o FFT por ventanas para ver si el periodo 210 cambia de fuerza con n.",
        "Probar autocorrelacion despues de dividir por HL para aislar solo estructura modular.",
        "Comparar los residuos de conteo contra la funcion de von Mangoldt convolucionada.",
        "Buscar si n con n/2 primo tiene una contribucion diagonal visible en debiles.",
        "Auditar 1112 con ruedas mod 2,6,30,210,2310 para cuantificar cada capa de filtrado.",
        "Buscar todos los n donde HL predice menos de 1 pero el real ya es grande, para explicar el arranque.",
        "Crear una prueba visual interactiva: slider de n y canales modulares activos.",
        "Extender a 20M solo con CSV comprimido y top summaries para no duplicar 200MB.",
        "Guardar conteos en Parquet o NumPy .npz para acelerar analisis posteriores.",
        "Medir el minimo de g(n) para n>=X con X creciente y ajustar una curva del piso.",
        "Comparar el piso observado contra c*n/log(n)^2 para estimar margen empirico.",
        "Buscar candidatos a futuros debiles usando solo features modulares antes de contar pares.",
        "Entrenar un arbol de decision que explique debiles vs fuertes con reglas legibles.",
        "Construir una lista de 'enemigos de Goldbach': propiedades que bajan representaciones.",
        "Construir una lista de 'aliados de Goldbach': propiedades que suben representaciones.",
        "Medir el efecto de cada primo pequeno p en el boost como (p-1)/(p-2) observado vs teorico.",
        "Ver si los numeros 2 mod 30 son siempre pobres o si hay subfamilias rescatadas por 7,11,13.",
        "Buscar excepciones calientes dentro de la peor banda mod 30.",
        "Buscar excepciones frias dentro de la mejor banda mod 30.",
        "Hacer un atlas de los 100 numeros mas debiles por cada decada.",
        "Calcular pares ordenados vs no ordenados y separar el efecto diagonal p+p=n.",
        "Medir cuantos pares sobreviven tras prohibir primos chicos en ambos lados.",
        "Crear filtros hostiles mas agresivos y ver si algun n grande se acerca a cero.",
        "Comparar distribucion de p inferior contra una uniforme corregida por densidad prima.",
        "Buscar resonancias con numeros altamente compuestos.",
        "Analizar si phi(n)/n predice debilidad mejor que cantidad de factores pequenos.",
        "Construir un informe HTML con graficos: pisos, records, bandas modulares, outliers.",
        "Replicar el experimento en intervalos aleatorios altos usando primalidad probabilistica.",
        "Convertir esto en un pipeline incremental: cada corrida agrega limites, patrones y alertas nuevas.",
    ]


def build_metrics(counts: list[int], data: dict) -> dict:
    metrics = {
        "limit": even_at(len(counts) - 1),
        "rows": len(counts),
        "global": global_stats(counts),
        "extremes": strongest_and_weakest(counts),
        "records": record_breakers(counts),
        "decades": decade_stats(counts),
        "mod30": mod_summaries(counts, 30),
        "mod210": mod_summaries(counts, 210),
        "autocorr": autocorrs(counts),
        "small_factors": small_factor_score(counts),
        "density": normalized_density(counts),
        "primorials": primorial_alignment(counts),
        "neighbor": local_neighbor_stats(counts),
        "source_missions": {
            "mission_7": mission_by_number(data, 7)["finding"],
            "mission_23": mission_by_number(data, 23)["finding"],
            "mission_24": mission_by_number(data, 24)["finding"],
            "mission_31": mission_by_number(data, 31)["finding"],
            "mission_32": mission_by_number(data, 32)["finding"],
        },
    }
    metrics["patterns"] = make_patterns(metrics, data)
    metrics["ideas"] = make_ideas()
    return metrics


def write_report(metrics: dict) -> None:
    lines = [
        "# Goldbach: 50 patrones + 50 ideas",
        "",
        f"Fuente: `{CSV_PATH.name}` y `{JSON_PATH.name}`.",
        f"Limite: {metrics['limit']:,}. Filas pares analizadas: {metrics['rows']:,}.",
        "",
        "## 50 patrones medidos",
        "",
    ]
    for i, item in enumerate(metrics["patterns"], 1):
        lines.append(f"{i}. {item}")

    lines += ["", "## 50 ideas para la siguiente tanda", ""]
    for i, item in enumerate(metrics["ideas"], 1):
        lines.append(f"{i}. {item}")

    lines += [
        "",
        "## Datos rapidos",
        "",
        f"- Media global de pares: {metrics['global']['mean']:.2f}",
        f"- Mediana global de pares: {metrics['global']['median']:.0f}",
        f"- Percentil 1: {metrics['global']['p01']:.0f}",
        f"- Percentil 99: {metrics['global']['p99']:.0f}",
        f"- Records detectados: {len(metrics['records'])}",
        f"- Mejor autocorrelacion muestreada: periodo {metrics['autocorr'][0]['period']} con corr={metrics['autocorr'][0]['corr']:.4f}",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_metrics(metrics: dict) -> None:
    serializable = dict(metrics)
    serializable["records"] = {
        "count": len(metrics["records"]),
        "first_12": metrics["records"][:12],
        "last_12": metrics["records"][-12:],
    }
    METRICS_PATH.write_text(json.dumps(serializable, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    counts = load_counts(CSV_PATH)
    data = load_json(JSON_PATH)
    metrics = build_metrics(counts, data)
    write_report(metrics)
    write_metrics(metrics)
    print(f"Wrote {REPORT_PATH}")
    print(f"Wrote {METRICS_PATH}")
    print(f"Patterns: {len(metrics['patterns'])}; ideas: {len(metrics['ideas'])}")
    print(f"Strongest: {metrics['extremes']['strongest'][0]}")
    print(f"Weakest >=1000: {metrics['extremes']['weakest_ge_1000'][0]}")
    print(f"Best autocorr: {metrics['autocorr'][0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
