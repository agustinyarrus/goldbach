# Goldbach round 2: patrones profundos

Fuente: `goldbach_counts_to_10000000.csv`.
Limite: 10,000,000. Pares analizados: 4,999,999.

## Patrones round 2

1. La mejor clase por densidad en rueda 2310 es residuo 0 con densidad media 2.7808.
2. La peor clase por densidad en rueda 2310 es residuo 2042 con densidad media 0.7788.
3. El cociente mejor/peor en rueda 2310 es 3.57.
4. Por pares crudos, la mejor clase 2310 es residuo 0 con media 56926.19.
5. Por pares crudos, la peor clase 2310 es residuo 2042 con media 15953.69.
6. La clase 2310 ganadora tiene su máximo en n=9699690 con 124,180 pares.
7. La clase 2310 perdedora toca mínimo en n=2042 con 30 pares.
8. Quitando el promedio de cada clase mod 210, el punto más frío es n=2672 con ratio 0.828.
9. Quitando el promedio de cada clase mod 210, el punto más caliente es n=5434 con ratio 1.497.
10. Quitando el promedio de cada clase mod 2310, el punto más frío es n=2672 con ratio 0.837.
11. Quitando el promedio de cada clase mod 2310, el punto más caliente es n=1612 con ratio 1.511.
12. La anomalía fría mod 2310 conserva 28 pares: sigue lejos de cero.
13. La anomalía caliente mod 2310 alcanza 35 pares.
14. En la década [1.000,10.000), los 12 más débiles van de 1112 a 1238 con conteos entre 16 y 18.
15. En [10.000,100.000), el mínimo sube a 92 y el p1 ya es 116.
16. En [100.000,1.000.000), el mínimo sube a 570 y el p1 ya es 720.
17. En [1M,10M], el mínimo sube a 3963 y el p1 ya es 4870.
18. El último n con <=20 pares es 1448.
19. El último n con <=50 pares es 4688.
20. El último n con <=100 pares es 11672.
21. El último n con <=500 pares es 85616.
22. El último n con <=1.000 pares es 195368.
23. El último n con <=5.000 pares es 1315298.
24. El último n con <=10.000 pares es 2947918.
25. El último n con <=20.000 pares es 6594752.
26. El umbral <=50.000 todavía aparece hasta 10000000.
27. El umbral <=100.000 todavía aparece hasta 10000000.
28. Hay 244 récords; la mayor sequía entre récords mide 390,390 números.
29. La mayor sequía de récords va de 8168160 a 8558550.
30. Los últimos récords terminan en 9699690 con 124,180 pares.
31. El mayor salto vecino hacia arriba es +94,672 entre 9699688 y 9699690.
32. El mayor salto vecino hacia abajo es -95,592 entre 9699690 y 9699692.
33. La mayor duplicación relativa vecina ocurre de 9699688 a 9699690 con ratio 4.21.
34. El modelo de boost por primos chicos correlaciona con densidad en 0.9990.
35. Se observaron 759 firmas de divisibilidad sobre los 10 primos chicos.
36. 286 firmas tienen al menos 100 ejemplos, suficiente para comparar medias.
37. La firma grande más fuerte usa primos [3, 5, 7, 11, 13] y densidad media 2.9801.
38. La firma grande más débil usa primos [] y densidad media 0.7681.
39. El punto más frío tras dividir por boost chico es n=12 con ratio 0.2573.
40. El punto más caliente tras dividir por boost chico es n=142 con ratio 1.3837.
41. Los múltiplos de 30 tienen lift 2.00 y su múltiplo más débil es 30.
42. Los múltiplos de 210 tienen lift 2.21 y su múltiplo más fuerte es 9699690.
43. Los múltiplos de 2310 tienen lift 2.41.
44. Los múltiplos de 30030 tienen lift 2.61.
45. Los múltiplos de 510510 tienen lift 2.81.
46. El único múltiplo de 9699690 dentro del límite es n=9699690 y coincide con el campeón global.
47. La peor banda mod30 es residuo 8, pero su caso caliente llega a 8406398 con 41,063 pares.
48. La mejor banda mod30 es residuo 0, pero su caso frío cae en 30 con solo 3 pares.
49. El patrón fuerte no es solo crecimiento: después de normalizar por log^2(n)/n, las clases modulares siguen separadas.
50. El patrón débil tampoco es solo modular: quedan outliers fríos dentro de su propia clase mod 2310.
51. La frontera empírica 'todo queda arriba de 1.000 pares' empieza después de n=195368.
52. La frontera empírica 'todo queda arriba de 5.000 pares' empieza después de n=1315298.
53. La década de millones tiene mediana 23011, casi 280.6 veces la mediana de la década de miles.
54. El p10 de millones es 9173, casi 247.9 veces el p10 de miles.
55. El máximo de [100.000,1.000.000) es 990990 con 15,594 pares.
56. El máximo de [1M,10M] es 9699690 con 124,180 pares.
57. Los outliers calientes mod 210 incluyen 5434, 1612, 1672, 2860, 1534.
58. Los outliers fríos mod 210 incluyen 2672, 1412, 2936, 9602, 1718.
59. Los outliers calientes mod 2310 incluyen 1612, 1534, 1108, 3562, 1054.
60. Los outliers fríos mod 2310 incluyen 2672, 1412, 2936, 9602, 1718.
61. Los vecinos del campeón global muestran pared: de 9699690 a 9699692 se pierden 95,592 pares.
62. El análisis round 2 refuerza una idea: Goldbach parece gobernado por crecimiento suave multiplicado por ruedas modulares y boosts de factores chicos.
63. La amenaza real para un contraejemplo no aparece en los grandes: los mínimos relativos grandes todavía tienen miles de representaciones.
64. 1112 sigue siendo más interesante como fósil modular temprano que como señal de una familia peligrosa.
65. Rueda 2310 mejora la lupa: separa subfamilias dentro de las mismas bandas mod 30/210.
66. Los récords favorecen números con muchos divisores chicos, pero los saltos vecinos prueban que ese boost se apaga de golpe al moverse dos unidades.

## Siguientes experimentos

1. Implementar rueda 30030 completa y comparar outliers contra rueda 2310.
2. Calcular el producto singular exacto para cada n usando SPF compacto.
3. Ajustar una regresion lineal sobre log(densidad) con indicadores mod 210 y factores chicos.
4. Separar anomalías que vienen de factores grandes de n, no solo de primos chicos.
5. Buscar familias n = primorial*k donde k es primo, semiprimo o altamente compuesto.
6. Medir si los grandes saltos vecinos se explican por perder divisibilidad por 3,5,7 simultaneamente.
7. Construir graficos de calor mod 2310 vs densidad normalizada.
8. Hacer un atlas local alrededor de cada record: n-20 a n+20.
9. Hacer un atlas local alrededor de cada debil: n-20 a n+20.
10. Buscar si las anomalías frías mod 2310 comparten residues modulo 30030.
11. Entrenar un predictor barato de debiles solo con n modulo primoriales.
12. Comprimir conteos a npz/parquet para poder iterar mas rapido.
13. Extender solo estadisticas agregadas hasta 20M o 50M sin guardar CSV completo.
14. Generar un informe HTML navegable con tablas filtrables.
15. Auditar manualmente los 20 outliers frios mod 2310 con conteo directo.
16. Medir pares con ambos primos lejos de divisores chicos.
17. Separar contribuciones p pequeno + n-p gigante contra pares balanceados.
18. Comparar g(n) contra g(n+210), g(n+420), g(n+2310).
19. Buscar 'clones modulares': n distintos con misma firma mod 2310 y densidades extremas.
20. Probar si phi(n)/n ordena la debilidad mejor que la firma de factores chicos.
21. Calcular radical(n) y tau(n) para los outliers extremos.
22. Explorar si los records aparecen cerca de primoriales o exactamente en multiplos.
23. Medir estabilidad del top 20 de residuos 2310 al cortar el rango en deciles.
24. Construir un buscador interactivo por n que devuelva pares, firma, densidad y residuos.
25. Correr una version Monte Carlo en rangos altos, sin FFT global, para testear heuristicas.

## Tablas clave

### Top 10 residuos 2310 por densidad

| residuo | densidad media | pares medios | min | max |
|---:|---:|---:|---:|---:|
| 0 | 2.7808 | 56926.19 | 114 | 124180 |
| 1050 | 2.5039 | 51236.92 | 57 | 108521 |
| 630 | 2.5038 | 51228.99 | 41 | 108678 |
| 210 | 2.5037 | 51224.37 | 19 | 106853 |
| 1890 | 2.5036 | 51241.31 | 91 | 109424 |
| 840 | 2.5034 | 51217.80 | 51 | 108699 |
| 420 | 2.5030 | 51211.48 | 30 | 107346 |
| 1470 | 2.5029 | 51225.65 | 73 | 107953 |
| 2100 | 2.5029 | 51224.35 | 97 | 108327 |
| 1260 | 2.5028 | 51216.38 | 68 | 110742 |

### Bottom 10 residuos 2310 por densidad

| residuo | densidad media | pares medios | min | max |
|---:|---:|---:|---:|---:|
| 2042 | 0.7788 | 15953.69 | 30 | 33922 |
| 2252 | 0.7789 | 15966.97 | 26 | 33367 |
| 908 | 0.7792 | 15964.37 | 15 | 35010 |
| 1118 | 0.7792 | 15965.80 | 22 | 33846 |
| 362 | 0.7794 | 15963.67 | 8 | 34264 |
| 1832 | 0.7794 | 15969.75 | 25 | 33458 |
| 2162 | 0.7794 | 15967.54 | 34 | 33080 |
| 1328 | 0.7794 | 15971.57 | 22 | 33904 |
| 488 | 0.7794 | 15966.37 | 9 | 34191 |
| 1448 | 0.7794 | 15966.18 | 20 | 33420 |

### Fronteras de umbral

| umbral | ultimo n <= umbral | cantidad |
|---:|---:|---:|
| 20 | 1448 | 401 |
| 50 | 4688 | 1419 |
| 100 | 11672 | 3572 |
| 500 | 85616 | 28068 |
| 1000 | 195368 | 66140 |
| 5000 | 1315298 | 459229 |
| 10000 | 2947918 | 1040353 |
| 20000 | 6594752 | 2337327 |
| 50000 | 10000000 | 4569818 |
| 100000 | 10000000 | 4999568 |
