# Mapa de Alerta de Abstención en León

Autores: **Estefania Portillo Balderas** y **Mauricio Caudillo Puente**.

Proyecto para el Hackathon INE 2026 **"Hackea la participación: Datos que construyen democracia"**,
**Reto 2: Predicción y escenarios de riesgo de abstención**.

Clasifica el riesgo de abstención juvenil de 2027 (elección intermedia) en cada sección electoral de León, Guanajuato,
con un semáforo, y propone dos acciones con lo que el INE
ya tiene: un volante en la visita que el CAE ya hace y módulos de credencial cerca de las escuelas, con un
recordatorio por SMS solo para quien lo acepte.

## Datos

- **Conteos Censales de Participación Ciudadana 2009–2024**, INE (datos abiertos):
  https://ine.mx/transparencia/datos-abiertos/visualizacion-datos/conteos-censales-participacion/
- **Base Geográfica Digital**, Guanajuato, SIGE 8, INE (corte diciembre 2025):
  https://cartografia.ine.mx/sige8/productosCartograficos/bases

- **Estadísticas Censales a Escalas Geoelectorales 2020**, INEGI: escolaridad, viviendas, internet, PEA y migración por sección.

Solo se usa información agregada por sección, sexo y edad; no hay datos personales.

## Cómo reproducir

Después de instalar (las dos primeras líneas), todo se corre con `.venv/bin/python scripts/00_todo.py`. Paso por paso:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

.venv/bin/python scripts/01_descarga.py      # descarga los 6 años del INE y extrae Guanajuato
.venv/bin/python scripts/02_limpieza.py      # tabla maestra de León (valida contra totales del INE)
.venv/bin/python scripts/03_graficas_edad.py # participación por edad y sexo 2009–2024
.venv/bin/python scripts/04_territorial.py   # León vs. Guanajuato, tipo de sección y top 50 de caída
# Descargar bgd_11_Shapefile.zip del SIGE 8 en data/raw/cartografia/ antes del siguiente paso
.venv/bin/python scripts/05_cartografia.py   # polígonos de secciones y escuelas
# Descargar del Mapa Digital de México (INEGI, capa Geoelectorales, Guanajuato, nivel Secciones) los indicadores
# poblacion, escolaridad, viviendas, internet, pea, migracion y pob_12a14 (Población de 12 a 14 años) como .xlsx en data/raw/censo/
.venv/bin/python scripts/13_censo.py         # variables del Censo 2020 por sección
.venv/bin/python scripts/06_modelo.py        # modelo de predicción 2027 y validación
.venv/bin/python scripts/07_escenarios.py    # escenarios sin/con intervención y semáforo
.venv/bin/python scripts/08_mapa.py          # mapa interactivo
.venv/bin/python scripts/09_exportar.py      # archivos de entrega
.venv/bin/python scripts/10_figura_mapa.py   # mapa estático para el reporte
.venv/bin/python scripts/11_robustez.py      # margen de error, tasa de acierto y sensibilidad
.venv/bin/python scripts/12_piloto.py        # efecto mínimo detectable del piloto con grupo de comparación
.venv/bin/python scripts/14_fichas.py        # una ficha por sección de prioridad 1 (anexo)
.venv/bin/python scripts/15_anexo.py         # coeficientes, umbral de cuadernillos, padrón desactualizado y costos
```

## Usarlo en otro municipio

El análisis no está amarrado a León. Todo se configura en [scripts/config.py](scripts/config.py) y se corre con un solo comando:

```bash
# 1. Ver las claves de los municipios del estado (Guanajuato = 11)
.venv/bin/python scripts/00_todo.py --entidad 11 --listar

# 2. Correr todo para ese municipio
.venv/bin/python scripts/00_todo.py --entidad 11 --municipio 17 --nombre Irapuato
```

Los resultados quedan en `outputs/<nombre>/` (semáforo, mapa, fichas, piloto, robustez) y no tocan los de León.

**Prueba con Irapuato** (mismo estado, sin descargar nada más): ver [outputs/irapuato/](outputs/irapuato/).
109 de 262 secciones en riesgo alto, con el 60 % de los jóvenes; tasa de acierto de 82 % (al azar, 42 %).
Ahí el modelo empata con la regla simple (error de 3.66 contra 3.61 puntos): el orden del semáforo se sostiene,
pero la ventaja del modelo que vimos en León no se repite en todos lados.

**Para un municipio de otro estado** hay que descargar a mano dos cosas antes de correrlo:

| Qué | Dónde se descarga | Dónde se guarda |
|---|---|---|
| Base Geográfica Digital del estado | SIGE 8 del INE: https://cartografia.ine.mx/sige8/productosCartograficos/bases | `data/raw/cartografia/bgd_<clave>_Shapefile.zip` |
| 7 indicadores del Censo 2020 por sección | Mapa Digital de México, capa Geoelectorales, nivel Secciones | `data/raw/censo/<clave>/` con los mismos nombres que en `data/raw/censo/` |

Los Conteos Censales de todos los estados los descarga solo `01_descarga.py`. El porcentaje de ciudadanía que no se
pudo localizar (para estimar los volantes) se toma automáticamente del informe del INE para cada estado.
Los cortes del semáforo (30 % y 40 %) son los mismos en todos lados: un municipio donde los jóvenes votan menos,
como Irapuato, tendrá más secciones en rojo.

## Resultados principales

| Archivo | Contenido |
|---|---|
| `outputs/mapa_escenarios.html` | Mapa interactivo: semáforo por sección, selector de escenario, top 50, escuelas |
| `outputs/fig_edad_leon.png`, `outputs/fig_edad_quinquenal.png` | Participación por edad 2009–2024 |
| `outputs/fig_tiposec.png` | León vs. resto del estado y por tipo de sección |
| `outputs/metricas_modelo.md` | Validación del modelo |
| `outputs/resumen_escenarios.md` | Semáforo y resultados de la intervención |
| `outputs/intervencion.md` | Las dos acciones (volante y credencial con SMS voluntario), supuestos, costos, neutralidad y pilotos |
| `outputs/recomendaciones.md` | Acciones por nivel de riesgo y por distrito |
| `outputs/piloto.md` | Piloto con grupo de comparación: efecto mínimo detectable y escala necesaria |
| `outputs/fichas_prioridad1.pdf` | Ficha de una página por sección de prioridad 1 |
| `outputs/anexo.md` | Coeficientes del modelo, prueba del umbral de cuadernillos, abstención aparente por padrón desactualizado y costos |
| `outputs/cifras_clave.json` | Cifras que deben coincidir en el reporte y la presentación |
| `outputs/robustez.md` | Margen de error, secciones rojas firmes, sensibilidad y escenario con evidencia europea |
| `outputs/notas_secciones.md`, `outputs/notas_caida.md` | Decisiones metodológicas |
| `outputs/entrega/` | Base anonimizada y escenarios (CSV y GeoJSON) |

## Uso de IA

Se utilizaron herramientas de asistencia de IA (Claude) para apoyo en programación y redacción;
el diseño del análisis, la validación de resultados y las recomendaciones son de autoría del equipo.

## Derechos

Todos los derechos reservados; ver [LICENSE](LICENSE). Los derechos patrimoniales se ceden al INE conforme a la carta de cesión del concurso.
