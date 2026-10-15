# Checkpoint avances Goldbach - 2026-05-12

Workspace:

```text
C:\Users\ayarr\Trabajos\goldbach
```

Estado:

- No quedaron procesos `goldbach` activos al guardar este checkpoint.
- La salida principal esta en `goldbach_rtx_output`.
- No es un repo git inicializado, asi que el checkpoint queda como archivo Markdown local.

## Scripts importantes

- `goldbach_rtx_round7.py`
  - FFT GPU/CPU hasta limites medianos.
  - Integra metricas HL, progresiones, short intervals y Chen D_{1,2}.

- `goldbach_huge_random_probe.py`
  - Probe aleatorio de numeros enormes.
  - Usa Miller-Rabin CPU para buscar un `p` chico tal que `n-p` sea primo.
  - Sirve para 100+ digitos, pero no usa GPU.

- `goldbach_hostile_crt_probe.py`
  - Generador CRT hostil CPU.
  - Construye pares `n` donde muchos `n-p` quedan forzados compuestos por congruencias.

- `goldbach_gpu64_probe.py`
  - Nuevo probe CUDA real para `n <= 2^64 - 1`.
  - Kernel `search_goldbach64`: busca el primer `p`.
  - Kernel `count_goldbach64`: cuenta todas las representaciones con `p <= p-limit`.
  - Usa Miller-Rabin deterministico 64-bit dentro de la RTX.
  - En Windows no se pudo usar `unsigned __int128` en NVRTC, asi que el kernel usa multiplicacion modular exacta por suma/doblado.

## Resultados verificados

### FFT exhaustivo hasta 250M

Archivo:

```text
goldbach_rtx_output\goldbach_rtx_round7_to_250000000.json
```

Resumen:

- Limite: 250,000,000
- Ceros: 0
- Backend: CuPy RTX FFT
- Mayor cantidad de pares detectada: `n = 249,339,090`, `2,115,013` pares.

### Random enorme

Resultados previos:

- Cerca de `4e18`: todos encontrados.
- Rango `4e18..18e18`: 100,000 targets, todos encontrados.
- 100 digitos: 1,000 targets, todos encontrados por probable MR.
- Mayor `p` observado en esas tandas: alrededor de pocos miles.

### GPU64 first-p hostil

Archivo:

```text
goldbach_rtx_output\goldbach_gpu64_hostile_20260512_200650.json
```

Resumen:

- Rango: `4,000,070,000,000,000,000 .. 18,000,000,000,000,000,000`
- Targets hostiles: 277,425
- `p-limit`: 2,000,000
- Faltantes: 0
- Peor primer `p`: 2,557
- Target mas dificil por primer `p`:

```text
n = 14275199748903066098
p = 2557
q = 14275199748903063541
```

Validacion:

- 1000 resultados muestreados por CPU: 0 errores.
- RTX llego a 100% SM utilization.

### GPU64 count hostil - record frio actual

Archivo:

```text
goldbach_rtx_output\goldbach_gpu64_hostile_20260512_202518.json
```

Resumen:

- Targets hostiles: 19,909
- Pares candidato lanzados: 2,965,107,097
- `p-limit`: 2,000,000
- Faltantes: 0
- Hits totales contados: 89,054,672
- Minimo de representaciones chicas: 4,181
- Mediana de representaciones chicas: 4,468
- Maximo de representaciones chicas: 4,867
- Kernel seconds: 666.777

Record frio actual:

```text
n = 16895403018399398618
representaciones con p <= 2,000,000 = 4,181
min p = 709
max p = 1,998,991
```

Validacion CPU completa de los 3 mas frios:

```text
n=16895403018399398618 gpu_count=4181 cpu_count=4181 min=709 max=1998991 ok=True
n=13287039417395496878 gpu_count=4209 cpu_count=4209 min=19 max=1999099 ok=True
n=15292835252282100638 gpu_count=4213 cpu_count=4213 min=67 max=1999957 ok=True
```

### GPU64 count hostil - seed 20260518

Archivo:

```text
goldbach_rtx_output\goldbach_gpu64_hostile_20260512_210602.json
```

Resumen:

- Targets hostiles: 19,881
- Pares candidato lanzados: 2,960,936,973
- `p-limit`: 2,000,000
- Faltantes: 0
- Minimo de representaciones chicas: 4,192
- Mediana de representaciones chicas: 4,468
- Maximo de representaciones chicas: 4,873
- Kernel seconds: 670.876
- GPU observada: 100% SM utilization, ~75 C, ~80 W.

Coldest de esta semilla:

```text
n = 12911015774628404558
representaciones con p <= 2,000,000 = 4,192
min p = 79
max p = 1,999,957
```

Validacion CPU completa de los 3 mas frios:

```text
n=12911015774628404558 gpu_count=4192 cpu_count=4192 min=79 max=1999957 ok=True
n=11984477252592297578 gpu_count=4207 cpu_count=4207 min=19 max=1999957 ok=True
n=15993827859448792478 gpu_count=4207 cpu_count=4207 min=859 max=1999891 ok=True
```

## Lectura actual

- No hay indicio cercano a contraejemplo.
- Los targets CRT hostiles arriba del maximo verificado conocido siguen teniendo miles de representaciones chicas.
- La mejor estrategia actual no es buscar "sin par" directamente, sino rankear numeros frios por cantidad de representaciones hasta un `p-limit`, y luego ampliar esos pocos targets.
- El mejor generador por ahora es `--mode hostile --mod-count 11`.
- `mod-count 12/13` bloquea un poco mas, pero genera muchos menos targets distintos dentro del rango 64-bit.
- El modo hibrido con `--exact-prefix-count` sube el primer primo permitido, pero no produjo targets mas frios.

## Comandos para retomar

Repetir tanda count GPU con nuevo seed:

```powershell
E:\goldbach_big\.venv_gpu\Scripts\python.exe .\goldbach_gpu64_probe.py --task count --mode hostile --start 4000070000000000000 --stop 18000000000000000000 --count 20000 --p-limit 2000000 --mod-count 11 --prime-chunk 8192 --max-results-saved 5000 --seed 20260519
```

Monitorear GPU:

```powershell
nvidia-smi dmon -s pucm -c 180
```

Buscar el record frio global entre JSON GPU64:

```powershell
Get-ChildItem .\goldbach_rtx_output\goldbach_gpu64_hostile_*.json |
  ForEach-Object {
    $m = Get-Content $_.FullName -Raw | ConvertFrom-Json
    if ($m.task -eq 'count') {
      [pscustomobject]@{
        file=$_.Name
        targets=$m.target_count
        min_count=$m.min_small_p_count
        cold_n=$m.coldest_results[0].n
        min_p=$m.coldest_results[0].min_p
        max_p=$m.coldest_results[0].max_p
      }
    }
  } | Sort-Object min_count | Format-Table -AutoSize
```

Siguiente ataque recomendado:

1. Repetir 5-10 seeds con `--task count --p-limit 2000000`.
2. Guardar los 100 targets mas frios.
3. Recontar solo esos frios con `p-limit` mas alto, idealmente 10M o 20M.
4. Si aparece un target con muy baja densidad, auditarlo por CPU completo y luego ampliar ventana.
