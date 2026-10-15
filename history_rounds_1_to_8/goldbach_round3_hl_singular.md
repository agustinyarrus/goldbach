# Goldbach round 3: Hardy-Littlewood singular

Fuente: `goldbach_counts_to_10000000.csv`.
Limite: 10,000,000. Pares analizados: 4,999,999.

## Patrones HL

1. Con producto singular exacto, el ratio medio actual/HL para n>=1000 es 1.1560.
2. La mediana muestreada actual/HL para n>=1000 es 1.1521.
3. El p1 muestreado actual/HL es 1.1393; incluso la cola fría queda cerca de la predicción.
4. El p99 muestreado actual/HL es 1.2173.
5. Hay 1 pares por debajo de HL y 4,999,500 por encima, para n>=1000.
6. El punto más frío por ratio HL es n=2672 con 28 pares contra esperado 28.50, ratio 0.9823.
7. El punto más caliente por ratio HL es n=1108 con 25 pares contra esperado 14.94, ratio 1.6736.
8. El peor residual absoluto negativo es n=2672: actual 28, esperado 28.50, residual -0.50.
9. El mayor residual positivo es n=9699690: actual 124180, esperado 108386.16, residual +15793.84.
10. El máximo boost singular es n=9699690 con boost 4.3807 y factores [2, 3, 5, 7, 11, 13, 17, 19].
11. El máximo boost singular coincide con el campeón global de pares: 9699690 tiene 124,180 pares.
12. Después de corregir por HL, la mejor banda mod30 por ratio medio es 16 con 1.1576.
13. Después de corregir por HL, la peor banda mod30 por ratio medio es 8 con 1.1534.
14. El rango entre bandas mod30 corregidas baja a 1.0036; la rueda queda casi explicada.
15. En [1.000,10.000), la mediana muestreada actual/HL es 1.2966.
16. En [10.000,100.000), la mediana muestreada actual/HL es 1.2274.
17. En [100.000,1.000.000), la mediana muestreada actual/HL es 1.1825.
18. En [1M,10M], la mediana muestreada actual/HL es 1.1510.
19. El ratio HL se estabiliza: las medianas por década se mueven mucho menos que los conteos crudos.
20. El residual absoluto medio para n>=1000 es 3086.34 pares.
21. La mediana muestreada del residual absoluto es 2641.38 pares.
22. Los 5 puntos más fríos por ratio HL son 2672, 1412, 2936, 9602, 1718.
23. Los 5 puntos más calientes por ratio HL son 1108, 1618, 2974, 1612, 1546.
24. Los 5 mayores residuos positivos son 9699690, 9999990, 9935310, 9669660, 9969960.
25. Los 5 mayores residuos negativos son 2672, 1412, 2936, 1718, 2642.
26. Los top boosts singulares arrancan con 9699690, 9189180, 8678670, 8168160, 7657650.
27. El primer top boost tiene factores [2, 3, 5, 7, 11, 13, 17, 19], exactamente una cadena de primos chicos.
28. El producto singular captura el efecto primorial que en rondas anteriores aparecía como lift de 30,210,2310.
29. Lo que queda tras HL ya no parece una pared modular grande, sino fluctuación fina alrededor de ratio cercano a 1.15.
30. La fórmula HL usada aquí queda sesgada baja: la media y mediana actual/HL superan 1.
31. El outlier caliente por ratio (1108) es temprano; en escalas grandes las desviaciones relativas extremas se suavizan.
32. El outlier frío por ratio (2672) también es temprano y todavía tiene 28 representaciones.
33. El mayor residual positivo absoluto aparece en escala grande porque el ruido absoluto crece con n.
34. El mayor residual negativo absoluto no amenaza Goldbach: conserva 28 pares.
35. Las bandas mod210 restantes top empiezan en residuos 46, 82, 94, 148, 118.
36. Las bandas mod210 restantes bottom empiezan en residuos 68, 152, 62, 188, 38.
37. El mejor residuo mod210 corregido tiene ratio 1.1582.
38. El peor residuo mod210 corregido tiene ratio 1.1522.
39. La variación mod210 corregida queda en factor 1.0052.
40. La lectura central: HL + producto singular explica casi toda la estructura gruesa encontrada en rounds 1 y 2.

## Siguientes experimentos

1. Recalibrar la constante global de HL con la media actual/esperado observada.
2. Medir residuos despues de calibrar HL para que la media sea exactamente 1.
3. Separar outliers HL por deciles de n para evitar que los tempranos dominen.
4. Calcular producto singular hasta 20M y ver si la mediana ratio baja lentamente.
5. Comparar esta constante contra variantes 2*C2 y contra conteos ordenados.
6. Usar una aproximacion log-integral en vez de n/log(n)^2.
7. Cruzar residuos HL con gaps primos alrededor de n/2.
8. Buscar familias con ratio HL persistentemente bajo en progresiones mod 2310.
9. Construir grafico ratio HL vs n en escala logaritmica.
10. Auditar conteo directo de los 10 ratios HL mas frios.
11. Auditar conteo directo de los 10 residuos negativos absolutos mas grandes.
12. Comparar ratio HL de multiplos de primorial contra vecinos +-2.
13. Medir asimetria de residuos: cola positiva vs cola negativa.
14. Entrenar modelo solo sobre residuos HL, no sobre conteos crudos.
15. Probar si radical(n) explica residuos que HL no captura.

## Top frio/caliente por ratio

| tipo | n | pares | esperado | ratio | boost | factores |
|---|---:|---:|---:|---:|---:|---|
| frio | 2672 | 28 | 28.50 | 0.9823 | 1.0061 | [2, 167] |
| frio | 1412 | 18 | 17.77 | 1.0129 | 1.0028 | [2, 353] |
| frio | 2936 | 31 | 30.48 | 1.0169 | 1.0027 | [2, 367] |
| frio | 9602 | 77 | 75.40 | 1.0212 | 1.0002 | [2, 4801] |
| frio | 1718 | 21 | 20.46 | 1.0262 | 1.0012 | [2, 859] |
| frio | 2642 | 29 | 28.11 | 1.0315 | 1.0008 | [2, 1321] |
| frio | 2252 | 26 | 24.99 | 1.0403 | 1.0018 | [2, 563] |
| frio | 4472 | 49 | 46.69 | 1.0494 | 1.1175 | [2, 13, 43] |
| frio | 1022 | 18 | 17.10 | 1.0527 | 1.2169 | [2, 7, 73] |
| frio | 4028 | 44 | 41.66 | 1.0561 | 1.0796 | [2, 19, 53] |
| caliente | 1108 | 25 | 14.94 | 1.6736 | 1.0036 | [2, 277] |
| caliente | 1618 | 32 | 19.59 | 1.6336 | 1.0012 | [2, 809] |
| caliente | 2974 | 49 | 30.72 | 1.5953 | 1.0007 | [2, 1487] |
| caliente | 1612 | 35 | 22.02 | 1.5895 | 1.1285 | [2, 13, 31] |
| caliente | 1546 | 30 | 18.95 | 1.5831 | 1.0013 | [2, 773] |
| caliente | 1744 | 33 | 20.86 | 1.5820 | 1.0093 | [2, 109] |
| caliente | 1282 | 26 | 16.55 | 1.5708 | 1.0016 | [2, 641] |
| caliente | 1264 | 26 | 16.57 | 1.5690 | 1.0130 | [2, 79] |
| caliente | 2164 | 38 | 24.27 | 1.5659 | 1.0019 | [2, 541] |
| caliente | 1024 | 22 | 14.07 | 1.5636 | 1.0000 | [2] |
