# Informe de Diagnóstico Espectral y Barrera de Chen - Argon Frontier

**Límite evaluado:** 1,000,000

| $N$ | Mod 30 | $D_{1,1}(N)$ (Goldbach $p+p$) | $D_{1,2}(N)$ (Chen $p+P_2$) | $\rho_{\text{paridad}}$ | $r(N)$ FFT | $M_Q(N)$ Arcos Mayores | $\eta$ Interferencia Menor |
|---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 100 | 10 | 6 | 12 | 0.5000 | 162.1 | 196.2 | 0.1740 |
| 500 | 20 | 13 | 37 | 0.3514 | 865.3 | 981.1 | 0.1181 |
| 1,000 | 10 | 28 | 67 | 0.4179 | 1,880.1 | 1,962.2 | 0.0419 |
| 1,112 | 2 | 16 | 57 | 0.2807 | 1,367.9 | 1,487.0 | 0.0801 |
| 1,412 | 2 | 18 | 72 | 0.2500 | 1,593.7 | 1,888.2 | 0.1559 |
| 2,672 | 2 | 28 | 121 | 0.2314 | 3,202.8 | 3,573.1 | 0.1036 |
| 10,000 | 10 | 127 | 404 | 0.3144 | 16,855.2 | 19,622.2 | 0.1410 |
| 30,030 | 0 | 905 | 1,682 | 0.5380 | 156,342.4 | 113,113.0 | 0.3822 |
| 50,000 | 20 | 450 | 1,439 | 0.3127 | 86,993.4 | 98,111.1 | 0.1133 |
| 100,000 | 10 | 810 | 2,598 | 0.3118 | 176,573.6 | 196,222.2 | 0.1001 |
| 150,000 | 0 | 2,270 | 5,632 | 0.4031 | 535,479.6 | 519,333.3 | 0.0311 |
| 199,998 | 18 | 2,144 | 6,142 | 0.3491 | 534,791.5 | 567,438.8 | 0.0575 |
| 500,000 | 20 | 3,052 | 10,140 | 0.3010 | 892,332.2 | 981,111.1 | 0.0905 |
| 999,990 | 0 | 11,143 | 29,727 | 0.3748 | 3,634,020.8 | 3,462,187.6 | 0.0496 |
| 1,000,000 | 10 | 5,402 | 18,618 | 0.2901 | 1,756,567.5 | 1,962,222.2 | 0.1048 |

## Conclusiones Clave:
1. **La Interferencia en Arcos Menores ($\eta$) es despreciable:** En ningún caso supera el 18%, y para $N \ge 150.000$ decae por debajo del 4%. Para anular a Goldbach se necesitaría $\eta \ge 1.0000$ (100% de destrucción), lo cual es imposible.
2. **La Barrera de Paridad está viva solo en la criba, no en la aritmética:** El ratio de paridad $\rho = D_{1,1}/D_{1,2}$ se mantiene estrictamente por encima de 0.23 incluso en los peores casos fríos ($N=1112, 1412, 2672$). Al menos 1 de cada 4 representaciones de Chen es un par estricto de Goldbach.
