# HINE-16 — Intervención hipotética: "Brigada CAE–SE Joven"

Aprovecha la estructura de CAE y SE que el INE ya contrata para la elección intermedia 2027.
No requiere personal nuevo: se monta sobre recorridos y tiempos que ya existen.

## Dónde

Secciones en semáforo **rojo** (HINE-19) y las **50 secciones con mayor caída** (`top50_caida.csv`).

## Componentes

| # | Quién | Qué hace | A quién llega |
|---|---|---|---|
| 1 | **CAE** | Mientras recorre su ARE buscando domicilios para notificar, entrega **casa por casa** (no solo a los insaculados) un volante dirigido a jóvenes: dónde votar, por qué importa, y la invitación "si ves a un CAE, acércate a preguntar sin compromiso". | Todas las viviendas de las secciones rojas |
| 2 | **SE** (supervisa una ZORE, que agrupa varias ARE) | Brigadas en **preparatorias y universidades** cercanas a las secciones rojas durante los tiempos sin carga operativa. | Estudiantes de 18 a 24 |
| 3 | **CAE + SE** | **Simulacros abiertos**: los jóvenes interesados (volante, escuela o abordaje en calle) pueden asistir a los simulacros de casilla, que hoy tienen cupo porque no van todos los FMDC. | Jóvenes interesados |

## Supuestos operativos (experiencia de campo como CAE en León, Proceso Electoral Federal 2017-2018, elección presidencial)

- Un CAE atiende su ARE, de 1–2 secciones (ej.: un fraccionamiento con su privada + una sección de ~3 calles con casas y edificios), con **hasta ~300 personas por notificar** (cifra aproximada, de memoria).
- En un día recorre **~la mitad de una colonia**.
- **~1 de cada 4 viviendas abre** la puerta → 25 % de contacto cara a cara; el resto recibe solo el volante.
- Cada CAE realiza 2–3 simulacros en su ARE (Área de Responsabilidad Electoral); asisten pocos FMDC, por lo que hay cupo para jóvenes invitados.
- En los simulacros participa el CAE y, si no coincide con otro, el SE.

## Efectos supuestos (sobre la participación de jóvenes 18–29)

| Canal | Pesimista | Medio | Optimista | Base |
|---|---|---|---|---|
| Conversación cara a cara (25 % de viviendas) | +2.5 pts | +3.0 pts | +4.3 pts | Meta-análisis de experimentos de campo: ~2.5 pts (Green, McGrath y Aronow, 2013) y ~4.3 pts en contactados (Gerber, 51 experimentos) |
| Solo volante (75 % de viviendas) | 0 | +0.3 pts | +0.5 pts | La evidencia de volantes es débil, cercana a cero; se trata como bono pequeño |
| Brigada en escuelas (SE) | +0.5 pts | +1.0 pts | +2.0 pts | Sin evidencia experimental directa en México; supuesto conservador |
| Simulacro (sobre asistentes) | +5 pts | +10 pts | +15 pts | Supuesto; aplica a pocas personas (10–15 jóvenes por simulacro) |

Efecto combinado calculado (`scripts/07_escenarios.py`), promedio en las 223 secciones intervenidas:
**+1.4 pts (pesimista), +2.6 pts (medio), +4.4 pts (optimista)** en la participación de jóvenes.
Simulacros: ~25 asistentes por sección (2 simulacros × 10–15 jóvenes), con tope del 10 % de los jóvenes de la sección.

La literatura indica que el efecto del contacto es mayor en elecciones de **baja participación** (como una intermedia), lo que favorece a 2027.

## Lo que se reporta

- Escenario A (sin intervención) vs. B (con intervención) en pesimista / medio / optimista.
- Votos jóvenes adicionales, secciones que cambian de color y costo marginal (≈ volantes impresos; el personal ya está contratado).

## Fuentes

- Gerber, A. "Getting Out the Vote Is Tougher Than You Think", Stanford Social Innovation Review. https://ssir.org/articles/entry/getting_out_the_vote_is_tougher_than_you_think
- Green, D., McGrath, M. y Aronow, P. (2013). "Field Experiments and the Study of Voter Turnout", Journal of Elections, Public Opinion and Parties; citado en Political Science Research and Methods (2018), https://doi.org/10.1017/psrm.2018.39

## Nota

Invitar jóvenes a simulacros y las brigadas escolares de SE son **propuestas nuevas**: hoy los simulacros son solo para FMDC. Se presentan como recomendación al INE.

La experiencia de campo proviene de una elección **presidencial**; en una intermedia concurrente (2027, con elección local en Guanajuato) la carga operativa y la disponibilidad de tiempos pueden variar.
