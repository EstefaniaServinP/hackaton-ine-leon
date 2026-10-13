# Anexo metodológico

## 1. Coeficientes del modelo final (variables estandarizadas)

Puntos de posición que cambia la predicción cuando la variable sube una desviación estándar.

|                                           |   Coeficiente |
|:------------------------------------------|--------------:|
| Posición en la elección anterior          |          4.73 |
| Años de escolaridad (Censo 2020)          |          2.1  |
| Posición en la intermedia anterior        |          2.03 |
| % de 60 y más en la lista                 |          1.33 |
| Crecimiento de la lista en 6 años         |         -0.4  |
| Tamaño de la lista (logaritmo)            |         -0.32 |
| % de jóvenes en la lista                  |          0.12 |
| Brecha de jóvenes en la elección anterior |          0.06 |
| % de mujeres en la lista                  |         -0.02 |

## 2. Umbral de cuadernillos sin capturar

| umbral        |   anios_descartados |   error_validacion |   rojas |   en_comun |
|:--------------|--------------------:|-------------------:|--------:|-----------:|
| 10%           |                 230 |               2.95 |     172 |        169 |
| 20%           |                 180 |               2.86 |     172 |        172 |
| 30%           |                 158 |               2.79 |     173 |        169 |
| Sin descartar |                   0 |               2.35 |     178 |        161 |

Años descartados = sección-año con NS por encima del umbral. El error de validación no es del todo comparable entre filas porque cambia qué secciones entran a la prueba.

## 3. Abstención aparente por padrón desactualizado

Inscritos por habitante en León (LN 2021 / población 2020): 0.7. Mediana por color: {'amarillo': 0.85, 'rojo': 0.66, 'verde': 0.88}. Secciones con más inscritos que habitantes: 93 (rojas: 2). Correlación con la participación juvenil esperada: 0.33.

| ausentes   |   rojas |
|:-----------|--------:|
| 5%         |     139 |
| 10%        |     102 |
| 20%        |      56 |

## 4. Costos

Impresión de 42,200 volantes: $42,200 a $84,400 pesos. Tiempo de CAE: unas 703 horas en total (1 minuto por visita).
