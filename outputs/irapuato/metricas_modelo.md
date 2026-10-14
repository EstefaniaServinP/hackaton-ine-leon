# HINE-17 — Modelo de predicción de participación 2027

Validación temporal sobre elecciones intermedias: se entrena prediciendo 2015 (con 2009 y 2012) y se prueba prediciendo 2021 (con 2015 y 2018).
Secciones en entrenamiento: 222 · en prueba: 234.

| Modelo | MAE (puntos) |
|---|---|
| Línea base: igual que la elección anterior | 3.61 |
| Línea base: igual que la elección del mismo tipo | 4.96 |
| Línea base: promedio de ambas | 3.95 |
| Regresión lineal | 3.66 |
| Random forest | 4.03 |

**Elegido: Regresión lineal.**

Nivel de Irapuato supuesto para 2027 (participación capturada de la intermedia 2021): 39.7 % total, 28.9 % jóvenes 18-29.

Secciones con predicción: 262 · calidad: {'completa': 237, 'parcial': 25}.
Participación 2027 predicha — mediana 42.4 %, rango 21.0–73.5 %.
Jóvenes 2027 predicha — mediana 31.8 %.
