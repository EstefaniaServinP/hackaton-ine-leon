# Intervención: Brigada CAE–SE Joven (versión acotada)

Diseñada para no agregar recorridos al CAE, no recolectar datos personales y poder medirse.
Cifras generadas por `scripts/07_escenarios.py` y `scripts/12_piloto.py`; ver `outputs/cifras_clave.json`.

## Dónde: criterio público y automático

Todas las secciones en **riesgo alto** del semáforo (participación juvenil predicha para 2027 menor a 30 %):
**172 secciones** de León, con 131,922 jóvenes de 18 a 29 años en la lista nominal de 2024.

El criterio usa solo datos de participación (Conteos Censales del INE) y del Censo 2020. **No usa resultados
electorales ni datos partidistas**, se aplica igual a todas las secciones que lo cumplen y la lista puede
publicarse antes de iniciar. Así se evita que la selección de lugares favorezca a alguna opción política.

## Qué hace cada figura

| Componente | Quién | Qué hace | ¿Se cuantifica? |
|---|---|---|---|
| **Volante joven** | CAE | En la visita que **ya hace** al hogar de cada persona sorteada (INE, Guía CAE 2023-2024, pp. 107–108), deja un volante neutral que invita a los jóvenes del hogar a votar en 2027 y a conocer el proceso (acercarse al CAE o a un simulacro). Incluye un QR a "Ubica tu casilla" del INE; **no recolecta datos**. Sin colores, frases ni símbolos asociados a partidos o candidaturas. | Sí |
| Brigadas escolares | SE | Pláticas en preparatorias y universidades cercanas, **si los planteles lo autorizan y la carga operativa de 2027 lo permite**. 70 secciones rojas tienen una a 1 km o menos. | No (sin evidencia) |
| Simulacros abiertos | CAE y SE | Invitar a jóvenes interesados a los simulacros, que ocurren en la segunda etapa de capacitación, más cerca de la jornada (Guía CAE, p. 80), **sin afectar su propósito de capacitar a los FMDC**. | No (sin evidencia) |
| Recordatorio final | INE | Difusión institucional en las últimas semanas, general y sin datos personales. | No |

**Diferencia con la carta-notificación:** la carta ya invita a votar (experiencia propia del equipo), pero
está dirigida a la persona sorteada, no a los jóvenes del hogar.

## Alcance

- El sorteo cubre el 13 % de la lista nominal (Guía CAE, p. 16), pero en Guanajuato no se pudo localizar al
  21.6 % de la ciudadanía visitada (INE, informe de la primera etapa 2023-2024, p. 73): unos **42,200 volantes**,
  uno por hogar localizado.
- En promedio se alcanza al **29 %** de los hogares de cada sección roja (hogares localizados entre viviendas
  habitadas del Censo 2020), es decir, a unos **36,200 jóvenes** que viven en esos hogares.
- **No se supone conversación con el joven:** quien abre la puerta casi nunca es él. El efecto se modela
  como el de un material impreso que llega al hogar.

## Efecto supuesto por joven que vive en un hogar alcanzado

| Escenario | Puntos | Base |
|---|---|---|
| Pesimista | 0.2 | Efecto europeo de contacto, 0.78 pts (Bhatti et al., 2016, como se citó en Townsley, 2025), aplicado a una cuarta parte |
| Medio | 0.5 | Envío impreso no partidista: menos de 0.5 pts (Gerber y Huber, 2016) |
| Optimista | 1.0 | Doble del anterior; techo prudente |

## Resultado

| Escenario | Votos jóvenes extra | Secciones que salen del rojo | Pesos por voto por cada peso que cueste un volante |
|---|---|---|---|
| Pesimista | ~70 | 0 | ~590 |
| Medio | ~180 | 3 | ~230 |
| Optimista | ~360 | 5 | ~120 |

**Lectura honesta:** el efecto directo es pequeño. El valor de la propuesta es (1) el semáforo para priorizar,
(2) una acción de costo casi nulo que no agrega recorridos y (3) un piloto que mide si funciona.

## Piloto: la misma intervención, a la mitad de los hogares

El volante se deja solo en la mitad de los hogares visitados, elegidos al azar (por ejemplo, por el último
dígito del código de barras del talón), y el CAE marca una casilla nueva en el talón: "volante joven entregado".
Después, el INE compara de forma interna y anonimizada la participación de los jóvenes de los hogares con y
sin volante con los registros de marca de voto. Supuesto: el INE puede ubicar a los jóvenes de cada hogar por
el domicilio del padrón.

- En León detectaría efectos de **1.5 puntos** o más; los esperados son de 0.2 a 1.0.
- Para detectar 0.5 puntos hacen falta ~341 mil jóvenes, **unas 9 veces las secciones rojas de León**: el piloto
  debe hacerse en varios municipios o a nivel estatal. El código genera el semáforo para cualquier municipio.

## Supuestos y límites operativos

- Agregar una casilla al talón y el volante requiere ajustar documentos de la Estrategia de Capacitación y
  Asistencia Electoral 2026-2027, aprobada el 31 de agosto de 2026; lo realista es probarlo en el siguiente
  proceso o como prueba acotada.
- El CAE ya llena el talón; dejar el volante agrega segundos por visita, no recorridos.
- Ubicar a los jóvenes de cada hogar y usar los registros de marca de voto para evaluar requiere revisión
  jurídica del INE en materia de datos personales.
- La experiencia de campo del equipo es de una elección presidencial (2018).
