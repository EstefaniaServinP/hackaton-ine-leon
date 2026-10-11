# HINE-17 — Modelo de predicción de participación 2027

Validación temporal sobre elecciones intermedias: se entrena prediciendo 2015 (con 2009 y 2012) y se prueba prediciendo 2021 (con 2015 y 2018).
Secciones en entrenamiento: 564 · en prueba: 688.

| Modelo | MAE (puntos) |
|---|---|
| Línea base: igual que la elección anterior | 3.06 |
| Línea base: igual que la elección del mismo tipo | 4.30 |
| Línea base: promedio de ambas | 3.21 |
| Regresión lineal | 2.92 |
| Random forest | 3.39 |

**Elegido: Regresión lineal.**

Nivel de León supuesto para 2027 (participación capturada de la intermedia 2021): 45.4 % total, 34.5 % jóvenes 18-29.

Secciones con predicción: 777 · calidad: {'completa': 689, 'parcial': 85, 'sin historial': 3}.
Participación 2027 predicha — mediana 49.7 %, rango 13.6–78.7 %.
Jóvenes 2027 predicha — mediana 37.8 %.
