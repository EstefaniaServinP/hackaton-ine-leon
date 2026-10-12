# HINE-16 — Intervención hipotética: "Brigada CAE–SE Joven"

Aprovecha la estructura de CAE y SE que el INE ya contrata para la elección intermedia 2027.
No requiere personal nuevo: se monta sobre recorridos y tiempos que ya existen.

## Dónde

Secciones en semáforo **rojo** (HINE-19) y las **50 secciones con mayor caída** (`top50_caida.csv`).

## Componentes

| # | Quién | Qué hace | A quién llega |
|---|---|---|---|
| 1 | **CAE** | Mientras recorre su ARE buscando domicilios para notificar, entrega **casa por casa** (no solo a los insaculados) un volante cuyo **mensaje principal es invitar a los jóvenes a votar en 2027** (cuándo y dónde votar, y por qué su voto cuenta). Como formas de involucrarse y conocer el proceso, invita además a acercarse al CAE para resolver dudas ("si ves a un CAE, acércate a preguntar sin compromiso") y a asistir a un simulacro. Contenido institucional y neutral: sin colores, frases ni símbolos asociados a partidos o candidaturas. | Todas las viviendas de las secciones rojas |
| 2 | **SE** (supervisa una ZORE, que agrupa varias ARE) | Brigadas en **preparatorias y universidades** cercanas a las secciones rojas durante los tiempos sin carga operativa. | Estudiantes de 18 a 24 |
| 3 | **CAE + SE** | **Simulacros abiertos**: los jóvenes interesados (volante, escuela o abordaje en calle) pueden asistir a los simulacros de casilla, que hoy tienen cupo porque no van todos los FMDC. | Jóvenes interesados |

## Supuestos operativos (experiencia de campo como CAE en León, Proceso Electoral Federal 2017-2018, elección presidencial)

- Un CAE atiende su ARE, de 1–2 secciones (ej.: un fraccionamiento con su privada + una sección de ~3 calles con casas y edificios), con **hasta ~300 personas por notificar** (cifra aproximada, de memoria).
- En un día recorre **~la mitad de una colonia**.
- **~1 de cada 4 viviendas abre** la puerta → 25 % de contacto cara a cara; el resto recibe solo el volante.
  Es conservador frente al dato oficial: en la primera etapa de 2024 los CAE notificaron en la propia visita al 37.6 % de la ciudadanía visitada en el país; en Guanajuato no fue posible localizar al 21.6 % (INE, Informe sobre la primera etapa de integración de mesas directivas de casilla 2023-2024, pp. 71–73).
- Cada CAE realiza 2–3 simulacros en su ARE (Área de Responsabilidad Electoral); asisten pocos FMDC, por lo que hay cupo para jóvenes invitados. Los simulacros ocurren en la segunda etapa de capacitación, más cerca de la jornada (Guía CAE 2023-2024, p. 80).
- En los simulacros participa el CAE y, si no coincide con otro, el SE.

## Efectos supuestos (sobre la participación de jóvenes 18–29)

| Canal | Pesimista | Medio | Optimista | Base |
|---|---|---|---|---|
| Conversación cara a cara (25 % de viviendas) | +2.5 pts | +3.0 pts | +4.3 pts | ~2.5 pts (Green et al., 2013, como se citó en Townsley, 2025) y 4.3 pts en contactados (Gerber y Huber, 2016) |
| Solo volante (75 % de viviendas) | 0 | +0.3 pts | +0.5 pts | Envío postal no partidista: < 0.5 pts (Gerber y Huber, 2016); volantes partidistas sin efecto significativo (Green et al., 2013, como se citó en Townsley, 2025) |
| Brigada en escuelas (SE) | +0.5 pts | +1.0 pts | +2.0 pts | Sin evidencia experimental directa en México; supuesto conservador |
| Simulacro (sobre asistentes) | +5 pts | +10 pts | +15 pts | Supuesto; aplica a pocas personas (10–15 jóvenes por simulacro) |

Efecto combinado calculado (`scripts/07_escenarios.py`), promedio en las 229 secciones intervenidas:
**+1.4 pts (pesimista), +2.6 pts (medio), +4.4 pts (optimista)** en la participación de jóvenes.
Simulacros: ~25 asistentes por sección (2 simulacros × 10–15 jóvenes), con tope del 10 % de los jóvenes de la sección.

La literatura indica que el efecto del contacto es mayor en elecciones de **baja participación** (como una intermedia), lo que favorece a 2027.

## Lo que se reporta

- Escenario A (sin intervención) vs. B (con intervención) en pesimista / medio / optimista.
- Votos jóvenes adicionales, secciones que cambian de color y costo marginal (≈ volantes impresos; el personal ya está contratado).

## Fuentes (APA 7)

- Gerber, A. y Huber, G. A. (2016, 7 de marzo). Getting out the vote is tougher than you think. *Stanford Social Innovation Review*. https://ssir.org/articles/entry/getting_out_the_vote_is_tougher_than_you_think
- Townsley, J. (2025). Is it worth door-knocking? Evidence from a United Kingdom-based Get Out The Vote (GOTV) field experiment on the effect of party leaflets and canvass visits on voter turnout. *Political Science Research and Methods, 13*(1), 21–35. https://doi.org/10.1017/psrm.2018.39 (cita a Green, McGrath y Aronow, 2013, y a Bhatti et al., 2016, que estima 0.78 pts en Europa)

## Nota

Invitar jóvenes a simulacros y las brigadas escolares de SE son **propuestas nuevas**: hoy los simulacros son solo para FMDC. Se presentan como recomendación al INE.

La experiencia de campo proviene de una elección **presidencial**; en una intermedia concurrente (2027, con elección local en Guanajuato) la carga operativa y la disponibilidad de tiempos pueden variar.

## Momento del contacto (ajuste)

La primera visita de los CAE ocurre meses antes de la jornada y el efecto de un contacto se desvanece con el tiempo. Por eso el volante lleva un **código QR** para que la persona joven, si quiere, se suscriba a un recordatorio institucional (con su consentimiento), y se agrega un **segundo contacto en las últimas semanas antes de la elección**: recordatorios a quienes se suscribieron y difusión digital focalizada en las zonas de las secciones rojas. No se usan datos de contacto del padrón.

## Piloto con grupo de comparación (`scripts/12_piloto.py`, `outputs/piloto.md`)

Para saber cuánto funciona la brigada, proponemos aplicarla con un grupo de comparación elegido al azar:

- **Por sección:** 108 secciones rojas con brigada y 108 sin ella. Solo distingue efectos de ~2.6 pts o más (escenario medio).
- **Por persona:** dentro de las secciones rojas, el CAE entrega el volante en hogares elegidos al azar y registra la entrega; el INE compara de forma interna y anonimizada la participación de jóvenes de hogares con y sin volante usando los registros de marca de voto de los cuadernillos. Distingue efectos de ~0.8 pts, pero exige registrar cada hogar visitado, algo que hoy no se hace.
- **Con el talón (recomendado):** el CAE ya registra cada visita a la ciudadanía sorteada en el "Talón acuse de recibo de la carta-notificación" (INE, *Guía para la y el Capacitador-Asistente Electoral 2023-2024*, pp. 107–108). Se agrega una casilla "volante joven entregado" y el volante se entrega a la mitad de las personas sorteadas, elegidas al azar. El INE compara la participación de los jóvenes sorteados de cada grupo con su clave de elector. Con ~9,650 jóvenes por grupo distingue efectos de ~1.7 pts, por debajo de lo que reporta la literatura para personas contactadas (2.5 a 4.3).

## Diferencia con la carta-notificación

La carta-notificación que entregan los CAE ya invita a votar (experiencia propia del equipo), pero solo llega a la ciudadanía sorteada, el 13 % de la lista nominal (Guía CAE 2023-2024, p. 16), y no está dirigida a jóvenes. El volante de la Brigada llega a todas las viviendas de las secciones rojas y habla a los jóvenes.
