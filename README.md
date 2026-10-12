# Mapa de Alerta de Abstención en León

Proyecto para el Hackathon INE 2026 **"Hackea la participación: Datos que construyen democracia"**,
**Reto 2: Predicción y escenarios de riesgo de abstención**.

Estima la participación de 2027 (elección intermedia) en cada sección electoral de León, Guanajuato,
la clasifica en un semáforo de riesgo de abstención juvenil y simula una intervención con la
estructura existente de CAE y SE del INE ("Brigada CAE–SE Joven").

## Datos

- **Conteos Censales de Participación Ciudadana 2009–2024**, INE (datos abiertos):
  https://ine.mx/transparencia/datos-abiertos/visualizacion-datos/conteos-censales-participacion/
- **Base Geográfica Digital**, Guanajuato, SIGE 8, INE (corte diciembre 2025):
  https://cartografia.ine.mx/sige8/productosCartograficos/bases

- **Estadísticas Censales a Escalas Geoelectorales 2020**, INEGI: escolaridad, viviendas, internet, PEA y migración por sección.

Solo se usa información agregada por sección, sexo y edad; no hay datos personales.

## Cómo reproducir

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
# poblacion, escolaridad, viviendas, internet, pea y migracion como .xlsx en data/raw/censo/
.venv/bin/python scripts/13_censo.py         # variables del Censo 2020 por sección
.venv/bin/python scripts/06_modelo.py        # modelo de predicción 2027 y validación
.venv/bin/python scripts/07_escenarios.py    # escenarios sin/con intervención y semáforo
.venv/bin/python scripts/08_mapa.py          # mapa interactivo
.venv/bin/python scripts/09_exportar.py      # archivos de entrega
.venv/bin/python scripts/10_figura_mapa.py   # mapa estático para el reporte
.venv/bin/python scripts/11_robustez.py      # margen de error, sensibilidad y escenario europeo
.venv/bin/python scripts/12_piloto.py        # efecto mínimo detectable del piloto con grupo de comparación
```

## Resultados principales

| Archivo | Contenido |
|---|---|
| `outputs/mapa_escenarios.html` | Mapa interactivo: semáforo por sección, selector de escenario, top 50, escuelas |
| `outputs/fig_edad_leon.png`, `outputs/fig_edad_quinquenal.png` | Participación por edad 2009–2024 |
| `outputs/fig_tiposec.png` | León vs. resto del estado y por tipo de sección |
| `outputs/metricas_modelo.md` | Validación del modelo |
| `outputs/resumen_escenarios.md` | Semáforo y resultados de la intervención |
| `outputs/intervencion.md` | Diseño y supuestos de la intervención |
| `outputs/recomendaciones.md` | Acciones por nivel de riesgo y por distrito |
| `outputs/piloto.md` | Diseño del piloto con grupo de comparación |
| `outputs/robustez.md` | Margen de error, secciones rojas firmes, sensibilidad y escenario con evidencia europea |
| `outputs/notas_secciones.md`, `outputs/notas_caida.md` | Decisiones metodológicas |
| `outputs/entrega/` | Base anonimizada y escenarios (CSV y GeoJSON) |

## Uso de IA

Se utilizaron herramientas de asistencia de IA (Claude) para apoyo en programación y redacción;
el diseño del análisis, la validación de resultados y las recomendaciones son de autoría del equipo.
