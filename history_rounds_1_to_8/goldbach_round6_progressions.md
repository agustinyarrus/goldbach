# Goldbach round 6: progresiones mod 2310 calibradas

Fuente: `goldbach_counts_to_10000000.csv`.
Limite: 10,000,000. Factor calibracion: 1.155968.

## Patrones de progresiones

1. Se analizaron 1155 progresiones pares modulo 2310.
2. El residuo con mayor ratio calibrado medio es 2218 con 1.003042.
3. El residuo con menor ratio calibrado medio es 2042 con 0.995456.
4. El rango medio top/bottom tras HL calibrado es solo 1.007620.
5. La familia persistentemente más caliente es residuo 724: su peor banda todavía promedia 0.992737.
6. La familia persistentemente más fría es residuo 1328: su mejor banda solo promedia 1.013568.
7. El residuo más inestable por bandas es 982 con span 0.046594.
8. El residuo que menos se enfría del primer al último decil es 1748 con drift -0.024405.
9. El residuo que más se enfría del primer al último decil es 982 con drift -0.046594.
10. En el último decil, el residuo más caliente es 724 con media 0.992737.
11. En el último decil, el residuo más frío es 62 con media 0.987672.
12. El mejor residuo medio 2218 tiene mínimo individual en n=9967558 con ratio 0.981447.
13. El peor residuo medio 2042 tiene máximo individual en n=2042 con ratio 1.117237.
14. La familia fría persistente 1328 tiene mínimo individual en n=5948 con ratio 0.914584.
15. La familia caliente persistente 724 tiene máximo individual en n=3034 con ratio 1.263259.
16. Después de HL calibrado, las familias mod 2310 sobreviven pero con amplitud pequeña.
17. Esto confirma que la rueda 2310 ya estaba casi absorbida por el producto singular.
18. Las progresiones persistentes son mejores objetivos para teoría que los outliers sueltos.
19. Aun la peor familia persistente está muy cerca de ratio 1: no aparece una progresión peligrosa.
20. La variación por escala dentro de un mismo residuo es comparable a la variación entre residuos.
21. Los top 5 residuos medios calientes son 2218, 1198, 568, 256, 712.
22. Los top 5 residuos medios fríos son 2042, 2252, 908, 1118, 362.
23. Los top 5 persistentes calientes son 724, 1384, 754, 568, 2044.
24. Los top 5 persistentes fríos son 1328, 1748, 1118, 2252, 2012.
25. Los top 5 más inestables son 982, 1282, 292, 1192, 1702.
26. La hipótesis ahora se afina: el residuo fino restante parece una oscilación de baja amplitud alrededor de HL calibrado.

## Top/bottom por media calibrada

| tipo | residuo | media | min ratio | min n | max ratio | max n | span bandas |
|---|---:|---:|---:|---:|---:|---:|---:|
| hot | 2218 | 1.003042 | 0.981447 | 9967558 | 1.185234 | 4528 | 0.042844 |
| hot | 1198 | 1.002722 | 0.982373 | 6166588 | 1.316828 | 1198 | 0.040947 |
| hot | 568 | 1.002710 | 0.983131 | 8956438 | 1.154586 | 2878 | 0.037242 |
| hot | 256 | 1.002647 | 0.982304 | 9967906 | 1.163485 | 2566 | 0.042332 |
| hot | 712 | 1.002607 | 0.981392 | 9386242 | 1.168784 | 3022 | 0.043206 |
| hot | 1516 | 1.002567 | 0.980989 | 7892476 | 1.211430 | 3826 | 0.043690 |
| hot | 736 | 1.002492 | 0.980504 | 9099826 | 1.217199 | 3046 | 0.042959 |
| hot | 1774 | 1.002482 | 0.980971 | 9565174 | 1.163271 | 6394 | 0.043685 |
| hot | 244 | 1.002468 | 0.981877 | 9321094 | 1.293774 | 2554 | 0.040715 |
| hot | 1822 | 1.002426 | 0.982092 | 8666632 | 1.186159 | 4132 | 0.042690 |
| cold | 2042 | 0.995456 | 0.977810 | 8396582 | 1.117237 | 2042 | 0.029021 |
| cold | 2252 | 0.995638 | 0.899958 | 2252 | 1.144824 | 6872 | 0.025211 |
| cold | 908 | 0.996037 | 0.949228 | 5528 | 1.085306 | 60968 | 0.027521 |
| cold | 1118 | 0.996089 | 0.946257 | 8048 | 1.136889 | 1118 | 0.025450 |
| cold | 362 | 0.996253 | 0.849805 | 2672 | 1.110572 | 21152 | 0.027532 |
| cold | 2162 | 0.996253 | 0.907780 | 4472 | 1.134655 | 2162 | 0.028894 |
| cold | 1328 | 0.996286 | 0.914584 | 5948 | 1.108996 | 1328 | 0.025102 |
| cold | 1832 | 0.996301 | 0.977324 | 530822 | 1.083830 | 101162 | 0.026898 |
| cold | 1448 | 0.996309 | 0.916421 | 6068 | 1.157137 | 3758 | 0.028909 |
| cold | 488 | 0.996317 | 0.976316 | 42068 | 1.149703 | 2798 | 0.029482 |

## Persistentes

| tipo | residuo | media | peor/mejor banda | primer decil | ultimo decil | drift |
|---|---:|---:|---:|---:|---:|---:|
| hot | 724 | 1.002075 | 0.992737 | 1.031174 | 0.992737 | -0.038437 |
| hot | 1384 | 1.000524 | 0.992402 | 1.028527 | 0.992402 | -0.036125 |
| hot | 754 | 1.001652 | 0.992303 | 1.032202 | 0.992303 | -0.039900 |
| hot | 568 | 1.002710 | 0.992176 | 1.029418 | 0.992176 | -0.037242 |
| hot | 2044 | 1.001213 | 0.991992 | 1.030692 | 0.991992 | -0.038700 |
| hot | 424 | 1.001388 | 0.991958 | 1.032729 | 0.991958 | -0.040771 |
| hot | 304 | 1.001933 | 0.991924 | 1.033896 | 0.991924 | -0.041972 |
| hot | 1198 | 1.002722 | 0.991854 | 1.032801 | 0.991854 | -0.040947 |
| hot | 394 | 1.001208 | 0.991851 | 1.029280 | 0.991851 | -0.037430 |
| hot | 64 | 1.001213 | 0.991822 | 1.032824 | 0.991822 | -0.041002 |
| cold | 1328 | 0.996286 | 1.013568 | 1.013568 | 0.988466 | -0.025102 |
| cold | 1748 | 0.996384 | 1.013805 | 1.013805 | 0.989401 | -0.024405 |
| cold | 1118 | 0.996089 | 1.014016 | 1.014016 | 0.988566 | -0.025450 |
| cold | 2252 | 0.995638 | 1.014583 | 1.014583 | 0.989372 | -0.025211 |
| cold | 2012 | 0.997176 | 1.015501 | 1.015501 | 0.988970 | -0.026531 |
| cold | 1382 | 0.997144 | 1.015746 | 1.015746 | 0.988165 | -0.027581 |
| cold | 1238 | 0.996472 | 1.015822 | 1.015822 | 0.989604 | -0.026218 |
| cold | 1832 | 0.996301 | 1.015875 | 1.015875 | 0.988977 | -0.026898 |
| cold | 458 | 0.997061 | 1.015942 | 1.015942 | 0.988682 | -0.027260 |
| cold | 1592 | 0.996734 | 1.016168 | 1.016168 | 0.989101 | -0.027067 |
