# Anexo metodológico

## 1. Coeficientes del modelo final (variables estandarizadas)

Puntos de posición que cambia la predicción cuando la variable sube una desviación estándar.

|                                           |   Coeficiente |
|:------------------------------------------|--------------:|
| Posición en la elección anterior          |          5.74 |
| % de 60 y más en la lista                 |          1.92 |
| Años de escolaridad (Censo 2020)          |          1.82 |
| Tamaño de la lista (logaritmo)            |         -0.65 |
| % de jóvenes en la lista                  |          0.46 |
| Posición en la intermedia anterior        |          0.3  |
| % de mujeres en la lista                  |          0.22 |
| Crecimiento de la lista en 6 años         |          0.12 |
| Brecha de jóvenes en la elección anterior |          0.12 |

## 2. Umbral de cuadernillos sin capturar

| umbral        |   anios_descartados |   error_validacion |   rojas |   en_comun |
|:--------------|--------------------:|-------------------:|--------:|-----------:|
| 10%           |                 122 |               3.82 |     117 |        109 |
| 20%           |                 105 |               3.66 |     109 |        109 |
| 30%           |                  87 |               3.73 |     113 |        108 |
| Sin descartar |                   0 |               3.48 |     107 |        105 |

Años descartados = sección-año con NS por encima del umbral. El error de validación no es del todo comparable entre filas porque cambia qué secciones entran a la prueba.

## 3. Abstención aparente por padrón desactualizado

Inscritos por habitante en Irapuato (LN 2021 / población 2020): 0.75. Mediana por color: {'amarillo': 0.88, 'rojo': 0.75, 'verde': 0.9}. Secciones con más inscritos que habitantes: 18 (rojas: 1). Correlación con la participación juvenil esperada: 0.49.

| ausentes   |   rojas |
|:-----------|--------:|
| 5%         |     100 |
| 10%        |      86 |
| 20%        |      56 |

## 4. Costos

Impresión de 26,222 volantes: $26,222 a $52,444 pesos. Tiempo de CAE: unas 437 horas en total (1 minuto por visita).
