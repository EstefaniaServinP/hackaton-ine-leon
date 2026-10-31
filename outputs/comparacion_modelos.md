# ¿Un modelo más complejo predice mejor?

Error promedio (puntos de posición) al estimar 2021 con datos hasta 2018. Menos es mejor.

|                                               |   León |   Irapuato |   Juárez |   Chihuahua |
|:----------------------------------------------|-------:|-----------:|---------:|------------:|
| Regla simple (igual que la elección anterior) |   3.06 |       3.61 |     3.44 |        3.75 |
| Ridge (regresión lineal regularizada)         |   2.87 |       3.6  |     3.86 |        3.65 |
| Regresión lineal                              |   2.86 |       3.66 |     3.84 |        3.68 |
| Random forest                                 |   3.35 |       4.03 |     3.81 |        3.74 |
| Gradient boosting                             |   3.35 |       4.13 |     4.09 |        3.65 |
| Red neuronal                                  |   3.45 |       3.76 |     4.07 |        4.15 |
| XGBoost (versión de scikit-learn)             |   3.55 |       4.34 |     4.05 |        3.57 |

|                           | León             | Irapuato                              | Juárez                                        | Chihuahua                             |
|:--------------------------|:-----------------|:--------------------------------------|:----------------------------------------------|:--------------------------------------|
| Secciones en la prueba    | 688              | 234                                   | 949                                           | 467                                   |
| Con escolaridad del Censo | sí               | sí                                    | no                                            | no                                    |
| Método elegido            | Regresión lineal | Ridge (regresión lineal regularizada) | Regla simple (igual que la elección anterior) | Ridge (regresión lineal regularizada) |

Lectura: ningún método gana en todos lados, y entre los mejores la diferencia es menor a medio punto. Los modelos complejos solo ganan una vez y por poco; con pocas elecciones por sección tienden a memorizar el ruido de una elección. Por eso 06_modelo.py elige, en cada municipio, entre cuatro candidatos simples (regla simple, regresión lineal, Ridge y random forest) el que menos se equivoca.
