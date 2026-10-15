# Conversación Goldbach - 2026-05-12

## Resumen

Se leyó `goldbach_journey.md`, que documentaba una exploración previa de la Conjetura Fuerte de Goldbach, y luego se creó un laboratorio computacional más avanzado: `goldbach_nasa_30.py`.

El script fue iterado varias veces: se agregaron misiones de análisis, auditoría exacta, FFT, comparación Hardy-Littlewood, análisis modular, sesgo de Chebyshev, primos especiales, clusters débiles, filtros hostiles y una auditoría independiente con Miller-Rabin. Más tarde se instaló NumPy y se activó FFT nativa para acelerar el barrido, manteniendo fallback puro Python.

## Archivos creados o modificados

- `C:\Users\aguyar\Assabloy\Desktop\goldbach_nasa_30.py`
- `C:\Users\aguyar\Assabloy\Desktop\goldbach_nasa_output\goldbach_counts_to_10000000.csv`
- `C:\Users\aguyar\Assabloy\Desktop\goldbach_nasa_output\goldbach_nasa_plus_findings_to_10000000.json`

## Resultado computacional principal

Se ejecutó el laboratorio hasta:

```text
10.000.000
```

Resultado:

```text
No se encontró ningún contraejemplo de Goldbach hasta 10.000.000.
```

Datos destacados:

- Eslabón débil serio: `1112`, con `16` pares de primos.
- Número más fuerte encontrado en la corrida de 10M: `9.699.690`, con `124.180` pares.
- La corrida grande tardó aproximadamente `622s`.

## Intuición discutida

Se planteó que si la cantidad de representaciones Goldbach crece aproximadamente como:

```text
N / (log N)^2
```

entonces parece cada vez menos probable que exista un número par grande con cero representaciones. La idea resumida fue:

```text
La marea sube más rápido de lo que los pozos pueden bajar.
```

Esto no prueba formalmente la conjetura, pero coincide con la intuición matemática estándar y con la evidencia computacional.

## Análisis especial de 1112

Se investigó por qué `1112` tiene justo `16` representaciones.

Factorización:

```text
1112 = 2^3 × 139
```

Residuo clave:

```text
1112 ≡ 2 mod 30
```

Como los primos grandes solo pueden caer en los residuos:

```text
1, 7, 11, 13, 17, 19, 23, 29 mod 30
```

para sumar `2 mod 30` quedan muy pocos canales:

```text
1 + 1
13 + 19
3 + 29
```

De `101` primos posibles `p ≤ 556`, el filtro módulo 30 mata `66` y deja solo `35` candidatos. Luego los filtros de divisibilidad por primos chicos terminan dejando exactamente `16`.

Pares Goldbach de `1112`:

```text
3 + 1109
19 + 1093
43 + 1069
61 + 1051
73 + 1039
79 + 1033
103 + 1009
193 + 919
229 + 883
283 + 829
373 + 739
379 + 733
421 + 691
439 + 673
499 + 613
541 + 571
```

Hardy-Littlewood predice aproximadamente:

```text
15.03 pares
```

y el conteo real fue:

```text
16 pares
```

Conclusión del patrón:

```text
1112 cae en una banda modular pobre, no recibe boost fuerte de factores chicos como 3 o 5, y los filtros por primos pequeños dejan solo 16 supervivientes.
```

Hasta `10.000.000`, `1112` siguió siendo el único número par `n ≥ 1000` con `≤ 16` representaciones.
