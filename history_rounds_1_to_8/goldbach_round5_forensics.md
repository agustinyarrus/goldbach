# Goldbach round 5: forense frío/caliente

Targets únicos auditados: 80.
Auditoría directa limpia: True.

## Patrones forenses

1. Se auditaron 80 n únicos de los grupos fríos/calientes grandes.
2. Todas las auditorías directas contra el CSV dieron match.
3. El frío calibrado principal 6051632 tiene conteo directo 18,572.
4. El caliente calibrado principal 1116182 tiene conteo directo 4,587.
5. Los fríos por ratio >=1M tienen media 23695.95 pares.
6. Los calientes por ratio >=1M tienen media 4743.65 pares.
7. Los peores residuales negativos >=1M tienen media 97377.75 pares.
8. Los mayores residuales positivos >=1M tienen media 23396.65 pares.
9. El gap primo más ancho alrededor de n/2 aparece en n=8829152 con gap 54.
10. El frío principal 6051632 tiene gap alrededor del midpoint 26.
11. El caliente principal 1116182 tiene gap alrededor del midpoint 0.
12. Los fríos tienen gap medio midpoint 19.40; los calientes 15.20.
13. Los fríos tienen distancia media al primo central 5.25; los calientes 3.65.
14. Los fríos tienen tasa central 1% media 0.0092; los calientes 0.0096.
15. Los fríos tienen tasa central 5% media 0.0473; los calientes 0.0466.
16. Los fríos tienen tasa central 10% media 0.0952; los calientes 0.0938.
17. El caso más central dentro del 1% es n=1048700 con tasa 0.0117.
18. El caso menos central dentro del 10% es n=1020154 con tasa 0.0888.
19. Los fríos tienen tasa tiny-sqrt media 0.001412; los calientes 0.004016.
20. El caso con más peso tiny-sqrt es n=1020154 con tasa 0.005654.
21. Los fríos tienen tasa tiny-log media 0.1448; los calientes 0.1682.
22. El caso más dominado por un canal mod30 es n=1220266 con canal 17+29 al 0.6751.
23. El frío principal usa 3 canales mod30 activos.
24. El caliente principal usa 2 canales mod30 activos.
25. El canal dominante del frío principal es 13+19 con tasa 0.6658.
26. El canal dominante del caliente principal es 13+19 con tasa 0.6634.
27. No aparece una explicación única por desierto central: los fríos grandes no tienen necesariamente gaps midpoint extremos.
28. Tampoco aparece una explicación única por pares tiny-giant: las tasas tiny son pequeñas en todos los grupos grandes.
29. La diferencia frío/caliente grande parece venir más de fluctuación distribuida entre muchos canales que de un solo bloqueo local.
30. El conteo directo confirma que los outliers calibrados grandes siguen teniendo decenas de miles de representaciones.

## Agregados por grupo

| grupo | n | media pares | gap midpoint medio | central 1% | central 5% | tiny sqrt | canal dominante medio | audit |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| cold_ratio_1m | 20 | 23695.95 | 19.40 | 0.0092 | 0.0473 | 0.001412 | 0.6671 | True |
| hot_ratio_1m | 20 | 4743.65 | 15.20 | 0.0096 | 0.0466 | 0.004016 | 0.6588 | True |
| negative_residual_1m | 20 | 97377.75 | 18.60 | 0.0097 | 0.0479 | 0.001206 | 0.2510 | True |
| positive_residual_1m | 20 | 23396.65 | 18.90 | 0.0094 | 0.0473 | 0.002754 | 0.2605 | True |

## Top fríos >=1M

| n | pares | gap midpoint | central 1% | central 5% | tiny sqrt | canal top | canal rate |
|---:|---:|---:|---:|---:|---:|---|---:|
| 6051632 | 18572 | 26 | 0.0093 | 0.0471 | 0.002046 | 13+19 | 0.6658 |
| 8930354 | 25939 | 0 | 0.0096 | 0.0475 | 0.001465 | 1+13 | 0.6648 |
| 7913132 | 23382 | 20 | 0.0093 | 0.0495 | 0.001283 | 13+19 | 0.6674 |
| 9702212 | 30441 | 26 | 0.0093 | 0.0471 | 0.001018 | 13+19 | 0.6678 |
| 8547692 | 26813 | 18 | 0.0094 | 0.0487 | 0.001193 | 13+19 | 0.6669 |
| 6940562 | 21793 | 36 | 0.0091 | 0.0482 | 0.001422 | 13+19 | 0.6692 |
| 8829152 | 25709 | 54 | 0.0092 | 0.0468 | 0.001011 | 13+19 | 0.6697 |
| 9601828 | 27720 | 20 | 0.0091 | 0.0475 | 0.001010 | 11+17 | 0.6711 |
| 7928042 | 23416 | 0 | 0.0088 | 0.0458 | 0.001153 | 13+19 | 0.6655 |
| 8480798 | 24839 | 0 | 0.0091 | 0.0477 | 0.001087 | 1+7 | 0.6632 |
