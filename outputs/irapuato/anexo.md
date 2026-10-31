# Anexo metodológico

## 1. Coeficientes del modelo final (variables estandarizadas)

Puntos de posición que cambia la predicción cuando la variable sube una desviación estándar.

|                                           |   Coeficiente |
|:------------------------------------------|--------------:|
| Posición en la elección anterior          |          5.49 |
| % de 60 y más en la lista                 |          1.85 |
| Años de escolaridad (Censo 2020)          |          1.81 |
| Tamaño de la lista (logaritmo)            |         -0.62 |
| Posición en la intermedia anterior        |          0.45 |
| % de jóvenes en la lista                  |          0.33 |
| % de mujeres en la lista                  |          0.25 |
| Brecha de jóvenes en la elección anterior |          0.15 |
| Crecimiento de la lista en 6 años         |          0.1  |

## 2. Umbral de cuadernillos sin capturar

| umbral        |   anios_descartados |   error_validacion |   rojas |   en_comun |
|:--------------|--------------------:|-------------------:|--------:|-----------:|
| 10%           |                 122 |               3.82 |     116 |        112 |
| 20%           |                 105 |               3.66 |     112 |        112 |
| 30%           |                  87 |               3.73 |     112 |        111 |
| Sin descartar |                   0 |               3.48 |     120 |        106 |

Años descartados = sección-año con NS por encima del umbral. El error de validación no es del todo comparable entre filas porque cambia qué secciones entran a la prueba.

## 3. Abstención aparente por padrón desactualizado

Inscritos por habitante en Irapuato (LN 2021 / población 2020): 0.75. Mediana por color: {'amarillo': 0.88, 'rojo': 0.75, 'verde': 0.9}. Secciones con más inscritos que habitantes: 18 (rojas: 1). Correlación con la participación juvenil esperada: 0.49.

| ausentes   |   rojas |
|:-----------|--------:|
| 5%         |      99 |
| 10%        |      85 |
| 20%        |      56 |

## 4. Costos

Impresión de 25,519 volantes: $25,519 a $51,038 pesos. Tiempo de CAE: unas 425 horas en total (1 minuto por visita).
