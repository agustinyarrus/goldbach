# Goldbach round 4: HL calibrado

Fuente: `goldbach_counts_to_10000000.csv`.
Limite: 10,000,000. Pares analizados: 4,999,999.
Factor de calibracion HL: 1.155968.

## Patrones calibrados

1. El factor de calibración global de HL en n>=1000 es 1.155968.
2. Después de calibrar, un ratio 1.0 significa 'exactamente lo esperable para este rango finito'.
3. El punto más frío calibrado desde 1000 es n=2672 con ratio 0.8498.
4. El punto más caliente calibrado desde 1000 es n=1108 con ratio 1.4478.
5. Desde 10k, el punto más frío calibrado es n=13892 con ratio 0.9359.
6. Desde 100k, el punto más frío calibrado es n=144128 con ratio 0.9617.
7. Desde 1M, el punto más frío calibrado es n=6051632 con ratio 0.9747.
8. Desde 1M, ese punto frío todavía tiene 18,572 pares.
9. Desde 1M, el punto más caliente calibrado es n=1116182 con ratio 1.0443.
10. El peor residual calibrado negativo desde 1000 es n=9909270 con residual -1508.69.
11. El peor residual calibrado negativo desde 1M es n=9909270 con residual -1508.69.
12. Pero ese peor residual desde 1M conserva 92,630 representaciones.
13. El mayor residual calibrado positivo desde 1M es n=2292750 con +419.21.
14. Por bandas iguales, el primer decil tiene media calibrada 1.0277.
15. Por bandas iguales, el último decil tiene media calibrada 0.9902.
16. La mediana muestreada del último decil es 0.9905.
17. El p1 muestreado del último decil es 0.9836.
18. El p99 muestreado del último decil es 0.9974.
19. La mejor correlación de conteos entre lags probados es periodo 2310 con corr 0.9956.
20. La mejor correlación de ratio calibrado entre lags probados es periodo 210 con corr 0.8788.
21. El menor cambio logarítmico medio del ratio calibrado ocurre con periodo 2310.
22. El periodo 2310 deja cambio log medio 0.0041.
23. El mayor salto vecino hacia arriba va de 9699688 a 9699690: +94,672 pares.
24. En ese salto se ganan factores [3, 5, 7, 11, 13, 17, 19] y se pierden [29, 41809].
25. El mayor salto vecino hacia abajo va de 9699690 a 9699692: -95,592 pares.
26. En esa caída se pierden factores [3, 5, 7, 11, 13, 17, 19] y se ganan [109, 22247].
27. Alrededor de 9699690, el centro queda rank 1 por pares dentro de ±20.
28. En la ventana ±20 de 9699690, el máximo es 9699690 con 124,180 pares.
29. En la ventana ±20 de 9699690, el mínimo es 9699706 con 28,220 pares.
30. Alrededor de 1112, el centro queda rank 21 dentro de ±20.
31. En la ventana ±20 de 1112, el mínimo es 1112 con 16 pares.
32. En la ventana ±20 de 1112, el máximo es 1110 con 54 pares.
33. Alrededor de 2672, el centro queda rank 21 dentro de ±20.
34. 2672 es frío contra HL, pero en su ventana local el mínimo es 2672 con 28 pares.
35. Los top fríos calibrados desde 1M son 6051632, 8930354, 7913132, 9702212, 8547692.
36. Los top calientes calibrados desde 1M son 1116182, 1048700, 1020154, 1022014, 1260136.
37. Los peores residuos negativos calibrados desde 1M son 9909270, 9639630, 9969120, 9463860, 9975000.
38. Los mayores residuos positivos calibrados desde 1M son 2292750, 3266190, 1920660, 1494780, 2193870.
39. La rareza relativa extrema vive temprano; en los millones la rareza baja mucho en ratio.
40. La rareza absoluta extrema vive tarde; en los millones los residuales son grandes pero con miles de pares.
41. Los vecinos de records muestran que el boost singular es muy discontinuo: moverse +2 puede borrar muchos factores chicos.
42. La comparación por lags muestra que repetir clase modular ayuda, pero no congela el residuo fino.
43. La señal peligrosa para Goldbach tendría que ser ratio bajo y conteo bajo a la vez; en grandes no aparece.
44. El round 4 deja una hipótesis precisa: los mínimos grandes son fluctuaciones calibradas normales sobre una base que ya crece muy lejos de cero.

## Siguientes experimentos

1. Extender el análisis calibrado hasta 20M con solo métricas, sin CSV completo.
2. Recalibrar por decil y buscar outliers dentro de cada decil por separado.
3. Calcular gaps primos alrededor de n/2 para los fríos calibrados desde 1M.
4. Auditar ventanas ±200 alrededor de los top records y top fríos.
5. Medir cuántos factores chicos se pierden en cada salto vecino extremo.
6. Comparar ratios calibrados entre n, n+2310 y n+30030.
7. Construir una tabla de familias por firma exacta de factores chicos.
8. Probar un modelo de residuo fino con features de gaps primos locales.
9. Graficar bandas de percentiles calibrados por escala.
10. Buscar el mínimo de pairs/calibrated_expected por ventanas móviles.
11. Probar si los fríos desde 1M tienen n/2 dentro de un desierto primo.
12. Crear un dashboard HTML de atlas local para anchors.
13. Comparar conteo observado contra HL calibrado con constante por década.
14. Buscar progresiones donde el ratio calibrado cae de forma persistente.
15. Correr auditoría directa Miller-Rabin sobre los fríos grandes calibrados.

## Fríos por escala

| desde n | n | pares | ratio calibrado | residual calibrado | factores |
|---:|---:|---:|---:|---:|---|
| 1000 | 2672 | 28 | 0.8498 | -4.95 | [2, 167] |
| 10000 | 13892 | 115 | 0.9359 | -7.87 | [2, 23, 151] |
| 100000 | 144128 | 751 | 0.9617 | -29.90 | [2, 563] |
| 1000000 | 6051632 | 18572 | 0.9747 | -482.19 | [2, 179, 2113] |

## Estabilidad por lag

| periodo | corr conteos | corr ratio calibrado | cambio log medio | delta pares medio |
|---:|---:|---:|---:|---:|
| 30 | 0.9744 | 0.8736 | 0.0042 | 2667.57 |
| 210 | 0.9920 | 0.8788 | 0.0041 | 1470.94 |
| 420 | 0.9920 | 0.8763 | 0.0041 | 1470.54 |
| 2310 | 0.9956 | 0.8783 | 0.0041 | 1075.26 |
