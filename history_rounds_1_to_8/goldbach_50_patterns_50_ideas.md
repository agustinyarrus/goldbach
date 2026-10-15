# Goldbach: 50 patrones + 50 ideas

Fuente: `goldbach_counts_to_10000000.csv` y `goldbach_nasa_plus_findings_to_10000000.json`.
Limite: 10,000,000. Filas pares analizadas: 4,999,999.

## 50 patrones medidos

1. No hay contraejemplos hasta 10,000,000; el barrido completo dio cero pares nulos.
2. El mínimo no trivial sigue clavado en 1112 con 16 pares.
3. El máximo global es 9699690 con 124,180 pares.
4. El campeón 9699690 es múltiplo de 2*3*5*7*11*13*17, un primorial casi perfecto para atraer canales.
5. La banda mod 30 más fuerte es 0 con media 44350.38.
6. La banda mod 30 más débil es 2 con media 16607.55.
7. Ser 0 mod 30 multiplica la media por 2.67 frente a la peor banda.
8. La banda mod 210 más fuerte es 0 con media 51743.00.
9. La banda mod 210 más débil es 62 con media 16132.32.
10. La autocorrelación muestreada más alta entre periodos probados aparece en periodo 420 con corr=0.9920.
11. El JSON previo confirma periodo 210 como dominante local: Strongest autocorrelation period=210 with corr=0.9814.
12. El espectro detectó periodo cercano a 6: Dominant residual period approx 6.00 number-units (FFT bin 2796203).
13. El piso por década sube: de 1 en [4,10) a 3963 en [1M,10M].
14. En [1.000,10.000) el piso es 16 y el punto más débil es 1112.
15. En [1M,10M] el piso ya es 3963 pares, muy lejos de cero.
16. La mediana por década pasa de 82 en miles a 23011 en millones.
17. Los récords son raros: solo 244 nuevos máximos entre casi cinco millones de pares evaluados.
18. El último récord antes del límite es 9699690 con 124,180 pares.
19. Los máximos top se concentran en residuo 0 mod 30; los 6 primeros máximos tienen ese residuo.
20. Los débiles no triviales se amontonan cerca de 1.000: 1112, 1004, 1006, 1016, 1022, 1028.
21. La densidad normalizada media g(n)*log(n)^2/n para n>=1000 es 1.1560.
22. La densidad normalizada muestreada tiene mediana 0.8422.
23. La densidad normalizada más baja entre n>=1000 aparece en 2672 con 0.6524.
24. La densidad normalizada más alta aparece en 9699690 con 3.3134.
25. La cuenta de factores pequeños correlaciona con pares en 0.4208.
26. Divisibilidad por 3 produce lift 2.00 en la media de pares.
27. Divisibilidad por 5 produce lift 1.33 en la media de pares.
28. Divisibilidad por 7 produce lift 1.20 en la media de pares.
29. Los múltiplos de 30 tienen lift 2.00.
30. Los múltiplos de 210 tienen lift 2.21.
31. Los múltiplos de 2310 tienen lift 2.41.
32. Los múltiplos de 30030 tienen lift 2.61.
33. Los múltiplos de 510510 tienen lift 2.81.
34. El mayor salto vecino cambia -95,592 pares entre 9699690 y 9699692.
35. El cambio absoluto vecino medio es 12869.20; la mediana muestreada es 9101.
36. El test de puentes en desiertos primos encontró gap máximo 154 en el par medio que suma 9304860.
37. Ese puente de desierto no es frágil: 9304860 tiene 72,877 pares.
38. Hardy-Littlewood queda sistemáticamente bajo en la muestra: HL median actual/expected=1.152 on 500 sampled evens.
39. El residuo dominante en pares mod 30 fue canal 13+17 según la heatmap previa.
40. El sesgo Chebyshev aparece pero es chico a 10M: Chebyshev sample bias 4k+3 / 4k+1 = 1.0010 across 11736139 pairs.
41. Los primos gemelos aparecen en una fracción grande de pares muestreados: Twin primes touched 33.16% of sampled pairs (4271972 prime appearances).
42. Los Sophie Germain participan menos pero no son marginales: Sophie Germain primes touched 16.15% of sampled pairs (1986453 prime appearances).
43. Los primos de Mersenne son prácticamente invisibles: Mersenne primes touched 0.00% of sampled pairs (444 prime appearances).
44. El centro de gravedad más desviado entre focos aparece en 1016.
45. El peor desierto de punto medio entre débiles solo tiene distancia 6.
46. El z-score caliente local máximo coincide con el campeón global: 9699690.
47. El filtro hostil todavía deja piso 3162 en supervivientes.
48. Los vecinos semiprimos suben la media: Semiprime-neighbor mean pairs: with=24210.84, without=22659.24.
49. El grafo de Goldbach muestra hubs de primos repetidos; top hub 50227.
50. Los clusters débiles iniciales son largos porque el percentil 10 todavía crece desde escalas bajas: 10th-percentile weakness threshold=5372.00; longest weak cluster length=148993.

## 50 ideas para la siguiente tanda

1. Construir un modelo predictivo g(n) = HL(n) * correccion_residuo * ruido_local y medir residuos reales.
2. Separar los pares por canal mod 30 y estudiar que canales se apagan primero en numeros debiles.
3. Repetir todo con rueda mod 2310 para ver si explica a 1112 mejor que mod 210.
4. Buscar el primer n donde el piso de una ventana de 250k pares supera 100.000.
5. Crear un detector de numeros anti-boost: pares con pocos factores pequenos pero conteo anormalmente alto.
6. Crear un detector de numeros turbo-boost: muchos factores pequenos pero conteo anormalmente bajo.
7. Medir si los records fuertes casi siempre son multiplos de primoriales truncados.
8. Probar ventanas logaritmicas en vez de ventanas lineales para ver la subida del piso.
9. Comparar conteo real contra Li(n)^2 heuristico en vez de n/log(n)^2.
10. Hacer una regresion con features: log n, mod30, mod210, factores pequenos, tau(n), radical(n).
11. Calcular el producto singular exacto para todos los n hasta 10M con SPF y comparar contra HL.
12. Buscar mini-cometas: patrones visuales por cada residuo mod 210 en graficos separados.
13. Mapear los huecos entre pares Goldbach consecutivos dentro de un mismo n.
14. Ver si los pares mas balanceados predicen conteos altos o solo reflejan el azar local.
15. Medir la proporcion de pares con p < sqrt(n), p < n/log(n), p dentro del 10% central.
16. Buscar numeros cuya representacion use muchos primos especiales a la vez: gemelo + safe + Sophie.
17. Crear ranking de primos-hub por deciles de n, no solo global.
18. Medir si un primo hub sigue siendo hub cuando se normaliza por disponibilidad.
19. Analizar la red bipartita n-primo y buscar comunidades por residuos modulares.
20. Buscar secuencias consecutivas de pares con conteos por debajo del percentil 1 local.
21. Definir una energia Goldbach: -log(g(n)/esperado) y buscar pozos profundos.
22. Usar wavelets o FFT por ventanas para ver si el periodo 210 cambia de fuerza con n.
23. Probar autocorrelacion despues de dividir por HL para aislar solo estructura modular.
24. Comparar los residuos de conteo contra la funcion de von Mangoldt convolucionada.
25. Buscar si n con n/2 primo tiene una contribucion diagonal visible en debiles.
26. Auditar 1112 con ruedas mod 2,6,30,210,2310 para cuantificar cada capa de filtrado.
27. Buscar todos los n donde HL predice menos de 1 pero el real ya es grande, para explicar el arranque.
28. Crear una prueba visual interactiva: slider de n y canales modulares activos.
29. Extender a 20M solo con CSV comprimido y top summaries para no duplicar 200MB.
30. Guardar conteos en Parquet o NumPy .npz para acelerar analisis posteriores.
31. Medir el minimo de g(n) para n>=X con X creciente y ajustar una curva del piso.
32. Comparar el piso observado contra c*n/log(n)^2 para estimar margen empirico.
33. Buscar candidatos a futuros debiles usando solo features modulares antes de contar pares.
34. Entrenar un arbol de decision que explique debiles vs fuertes con reglas legibles.
35. Construir una lista de 'enemigos de Goldbach': propiedades que bajan representaciones.
36. Construir una lista de 'aliados de Goldbach': propiedades que suben representaciones.
37. Medir el efecto de cada primo pequeno p en el boost como (p-1)/(p-2) observado vs teorico.
38. Ver si los numeros 2 mod 30 son siempre pobres o si hay subfamilias rescatadas por 7,11,13.
39. Buscar excepciones calientes dentro de la peor banda mod 30.
40. Buscar excepciones frias dentro de la mejor banda mod 30.
41. Hacer un atlas de los 100 numeros mas debiles por cada decada.
42. Calcular pares ordenados vs no ordenados y separar el efecto diagonal p+p=n.
43. Medir cuantos pares sobreviven tras prohibir primos chicos en ambos lados.
44. Crear filtros hostiles mas agresivos y ver si algun n grande se acerca a cero.
45. Comparar distribucion de p inferior contra una uniforme corregida por densidad prima.
46. Buscar resonancias con numeros altamente compuestos.
47. Analizar si phi(n)/n predice debilidad mejor que cantidad de factores pequenos.
48. Construir un informe HTML con graficos: pisos, records, bandas modulares, outliers.
49. Replicar el experimento en intervalos aleatorios altos usando primalidad probabilistica.
50. Convertir esto en un pipeline incremental: cada corrida agrega limites, patrones y alertas nuevas.

## Datos rapidos

- Media global de pares: 23653.76
- Mediana global de pares: 21196
- Percentil 1: 798
- Percentil 99: 72127
- Records detectados: 244
- Mejor autocorrelacion muestreada: periodo 420 con corr=0.9920
