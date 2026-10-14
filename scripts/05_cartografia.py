"""HINE-10: polígonos de las secciones de León a partir de la Base Geográfica Digital del INE.

Fuente: SIGE 8, https://cartografia.ine.mx/sige8/productosCartograficos/bases (Guanajuato, corte dic. 2025).
Uso: guardar bgd_11_Shapefile.zip en data/raw/cartografia/ y correr python scripts/05_cartografia.py
Resultado:
  data/processed/leon_secciones.geojson   un polígono por sección (WGS84)
  data/processed/leon_escuelas.geojson    preparatorias y universidades de León (para las brigadas de SE)
"""
import zipfile
from pathlib import Path

import config
import geopandas as gpd
import pandas as pd
import py7zr

RAIZ = Path(__file__).resolve().parent.parent
CARTO = config.CARTO
PROC = config.PROC
MUNICIPIO = config.MUNICIPIO
NIVEL_ESCUELA = {1: "Preescolar", 2: "Primaria", 3: "Secundaria", 4: "Preparatoria", 5: "Universidad", 6: "Especial/otra"}


def extraer():
    """Devuelve la carpeta con las capas del estado; la extrae de bgd_<clave>_Shapefile.zip si hace falta."""
    clave = f"{config.ENTIDAD:02d}"
    hechas = [p for p in (CARTO / "bgd").glob(f"{clave} *") if (p / "SECCION.shp").exists()]
    if hechas:
        return hechas[0]
    with zipfile.ZipFile(CARTO / f"bgd_{clave}_Shapefile.zip") as z:
        z.extractall(CARTO)
    siete = sorted(CARTO.glob(f"{clave} *.7z"))
    if not siete:
        raise SystemExit(f"No encontré '{clave} <ESTADO>.7z' dentro de bgd_{clave}_Shapefile.zip")
    with py7zr.SevenZipFile(siete[0]) as z:
        z.extractall(CARTO / "bgd")
    return extraer()


def main():
    capas = extraer()
    sec = gpd.read_file(capas / "SECCION.shp")
    sec = sec[sec.municipio == MUNICIPIO][["seccion", "distrito_f", "distrito_l", "tipo", "geometry"]]
    sec = sec.dissolve(by="seccion", as_index=False)  # por si una sección viene partida en varias piezas
    sec = sec.to_crs(4326)
    sec["geometry"] = sec.geometry.simplify(0.00005, preserve_topology=True)  # ~5 m, aligera el mapa

    m = pd.read_csv(config.MAESTRA)
    s24 = set(m.loc[m.anio == 2024, "seccion"])
    panel = set(m.loc[m.en_panel_2015_2024, "seccion"])
    carto = set(sec.seccion)
    cob24 = len(s24 & carto) / len(s24)
    print(f"Polígonos {config.NOMBRE}: {len(sec)} | secciones 2024 en datos: {len(s24)} | con polígono: {cob24:.1%}")
    print(f"Panel 2015-2024 con polígono: {len(panel & carto) / len(panel):.1%}")
    print(f"Sin polígono (2024): {sorted(s24 - carto)[:20]} | polígonos sin datos 2024: {sorted(carto - s24)[:20]}")
    assert cob24 >= 0.95, "menos del 95% de las secciones 2024 tienen polígono"

    tipos = m[m.anio == 2024].groupby("seccion").tipo_seccion.first()
    cruce = sec.set_index("seccion").tipo.to_frame().join(tipos, how="inner")
    print("Código 'tipo' de la cartografía vs tipo de sección del conteo censal:")
    print(pd.crosstab(cruce.tipo, cruce.tipo_seccion).to_string())

    PROC.mkdir(parents=True, exist_ok=True)
    sec.rename(columns={"distrito_f": "distrito_federal", "distrito_l": "distrito_local", "tipo": "tipo_carto"}) \
       .to_file(config.SECCIONES, driver="GeoJSON")

    esc = gpd.read_file(capas / "ESCUELA.shp").to_crs(4326)
    esc = gpd.sjoin(esc, sec[["seccion", "geometry"]], predicate="within").drop(columns="index_right")
    # La capa no trae catálogo de TIPO; nivel inferido a partir de los nombres de las escuelas
    esc["nivel"] = esc.TIPO.map(NIVEL_ESCUELA)
    esc = esc[esc.nivel.isin(["Preparatoria", "Universidad"])][["NOMBRE", "nivel", "seccion", "geometry"]]
    print(f"Preparatorias y universidades en {config.NOMBRE}: {esc.nivel.value_counts().to_dict()}")
    esc.to_file(config.ESCUELAS, driver="GeoJSON")


if __name__ == "__main__":
    main()
