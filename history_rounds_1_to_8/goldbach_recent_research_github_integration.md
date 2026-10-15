# Goldbach: investigacion reciente + GitHub + plan RTX

Fecha de integracion: 2026-05-12.

## Fuentes academicas recientes

1. Genheng Zhao, "The exceptional set of Goldbach problem and Linnik's constant", arXiv:2511.05631v2, 2026-01-23.
   Resultado util: mejora el enfoque de conjunto excepcional; prueba E(X)=O(X^(7/10)). Para nuestro laboratorio: medir pisos, colas frias y familias frias persistentes, no solo buscar ceros.
   URL: https://arxiv.org/abs/2511.05631

2. Andres Chirre y Markus Valas Hagen, "On Goldbach numbers in short intervals", arXiv:2512.23534, 2025-12-29.
   Resultado util: bajo RH, hay al menos un numero Goldbach en intervalos (x, x + 123 log^2 x]. Para nuestro laboratorio: medir intervalos cortos empiricos, pero con versiones robustas: no solo count > 0, tambien count sobre umbrales.
   URL: https://arxiv.org/abs/2512.23534

3. Mizuki Akeno, "Small gaps between Goldbach primes", arXiv:2508.02769v3, 2025-11-30.
   Resultado util: estudia gaps pequenos dentro del conjunto P cap (N-P). Para nuestro laboratorio: medir, para cada N, los gaps entre primos p que participan en pares Goldbach y comparar minimo/mediana/promedio.
   URL: https://arxiv.org/abs/2508.02769

4. Gautami Bhowmik, Anne-Maria Ernvall-Hytonen, Neea Palojarvi, "Explicit estimates for the Goldbach summatory function", arXiv:2411.00323v2, 2025-04-16.
   Resultado util: enfoque de funcion sumatoria, promedios y progresiones aritmeticas. Para nuestro laboratorio: agregar sumatorias acumuladas y residuales por progresion.
   URL: https://arxiv.org/abs/2411.00323

5. Thi Thu Nguyen, "Average orders of Goldbach Estimates in Arithmetic Progressions", arXiv:2407.18266v2, 2025-05-01.
   Resultado util: ordenes promedio de representaciones en progresiones aritmeticas. Para nuestro laboratorio: extender round 6 a modulos 30030 y a sumas acumuladas por clase.
   URL: https://arxiv.org/abs/2407.18266

6. Jared Duker Lichtman, "Primes in arithmetic progressions to large moduli, and Goldbach beyond the square-root barrier", arXiv:2309.08522, 2023-08-30.
   Resultado util: nuevo nivel de distribucion 66/107 y mejora fuerte en aplicaciones tipo Goldbach. Para nuestro laboratorio: buscar evidencia empirica de estabilidad en modulos grandes y comparar mod 2310/30030/510510.
   URL: https://arxiv.org/abs/2309.08522

7. Runbo Li, "Primes in arithmetic progressions to large moduli and refinements of Harman's sieve", arXiv:2602.20917v5, 2026-05-05.
   Resultado util: distribucion promedio de primos en progresiones con modulos mayores que sqrt(x). Para nuestro laboratorio: testear progresiones mas grandes y variacion por deciles.
   URL: https://arxiv.org/abs/2602.20917

8. Runbo Li, "On Chen's theorem, Goldbach's conjecture and almost prime twins II", Mathematical Reports 2026 / arXiv-related preprint.
   Resultado util: cuenta representaciones N = p + P2 con casi-primos, con constantes cercanas al 2 de Hardy-Littlewood. Para nuestro laboratorio: medir conteos Chen D_{1,2}(N) junto a conteos p+p.
   URL: https://runbolicarey.com/assets/downloads/On_Chen_s_theorem__Goldbach_s_conjecture_and_almost_prime_twins_II.pdf

9. Ameneh Farhadian, "Goldbach Conjecture: Violation Probability and Generalization to Prime-like Distributions", arXiv:2504.14353, 2025-04-19.
   Resultado util: enfoque probabilistico y conjuntos prime-like. Para nuestro laboratorio: crear stress tests con conjuntos prime-like perturbados y comparar resiliencia Goldbach.
   URL: https://arxiv.org/abs/2504.14353

10. Oleksandr V. Marchukov, Andrea Trombettoni, Giuseppe Mussardo, Maxim Olshanii, "Achieving quantum advantage in a search for violations of the Goldbach conjecture...", arXiv:2404.00517v5, 2025-09-28.
    Resultado util: formulacion como busqueda acelerada sobre conjuntos candidatos. Para nuestro laboratorio: GPU search por rangos y single-checks de numeros enormes.
    URL: https://arxiv.org/abs/2404.00517

## Repos GitHub revisados

1. isaac-6/goldbach-gpu
   URL: https://github.com/isaac-6/goldbach-gpu
   Licencia: MIT. Idea fuerte: verificacion segmentada GPU, bitsets, fallback CPU riguroso, single-check con Miller-Rabin/GMP. Esto si vale incorporarlo conceptualmente.

2. dataplayer12/goldbach-comet
   URL: https://github.com/dataplayer12/goldbach-comet
   Licencia: MIT. Idea util: biblioteca simple para funcion G(x) y visualizacion comet. Ya tenemos mas potencia, pero sirve como recordatorio de separar core de visualizacion.

3. mbarylsk/goldbach-partition
   URL: https://github.com/mbarylsk/goldbach-partition
   Licencia: GPL-3.0. Idea: benchmarking de confirmacion rapida. No conviene copiar codigo por licencia si queremos mantener scripts propios, pero si comparar metricas.

4. Ruqing1963/Goldbach-Bias-Analysis
   URL: https://github.com/Ruqing1963/Goldbach-Bias-Analysis
   Licencia: MIT. Idea util: medir sesgo sistematico Hardy-Littlewood y corregir drift de escala. Ya lo empezamos en rounds 3-6; round 7 lo formaliza a mayor escala.

5. michelyamagishi/Goldbach
   URL: https://github.com/michelyamagishi/Goldbach
   Licencia: no declarada. Idea: particiones minimas e identidades con pi(n)/pi_2(n). Sin licencia clara: no copiar, solo considerar experimento de "minimal partition".

6. Thelearner26/goldbach-conjecture
   URL: https://github.com/Thelearner26/goldbach-conjecture
   Licencia: no declarada. Idea general: verificacion + comet. No aporta arquitectura nueva frente a nuestro laboratorio.

## Ideas incorporadas al round 7 RTX

1. Backend RTX con CuPy FFT para contar G(n) mas alla de 10M.
2. Salidas grandes en E:\goldbach_big para no saturar C:.
3. No guardar CSV completo por defecto; guardar resumen JSON/Markdown y solo muestras.
4. Medir intervalos cortos tipo Chirre-Hagen: ventanas de longitud 123 log^2 x y variantes robustas por umbral.
5. Medir gaps entre Goldbach primes al estilo Akeno: minimo/medio de gaps entre p participantes.
6. Medir D_{1,2}(N): cantidad de p primo tal que N-p es primo o semiprimo, inspirado por Chen/Li.
7. Medir residuales Hardy-Littlewood calibrados por progresiones grandes.
8. Mantener auditoria directa de casos extremos.
9. Preparar extension segmentada futura inspirada en isaac-6/goldbach-gpu para rangos 1e12 sin guardar arrays completos.
10. Probar stress tests prime-like perturbados como linea probabilistica, no como prueba matematica.
