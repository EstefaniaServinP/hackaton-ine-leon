"""HINE-10: polígonos de las secciones de León a partir de la Base Geográfica Digital del INE.

Fuente: SIGE 8, https://cartografia.ine.mx/sige8/productosCartograficos/bases (Guanajuato, corte dic. 2025).
Uso: guardar bgd_11_Shapefile.zip en data/raw/cartografia/ y correr python scripts/05_cartografia.py
Resultado:
  data/processed/leon_secciones.geojson   un polígono por sección (WGS84)
  data/processed/leon_escuelas.geojson    preparatorias y universidades de León (para las brigadas de SE)
"""
import zipfile
from pathlib import Path

import geopandas as gpd
import pandas as pd
import py7zr

RAIZ = Path(__file__).resolve().parent.parent
CARTO = RAIZ / "data" / "raw" / "cartografia"
PROC = RAIZ / "data" / "processed"
CAPAS = CARTO / "bgd" / "11 GUANAJUATO"
LEON = 20
NIVEL_ESCUELA = {1: "Preescolar", 2: "Primaria", 3: "Secundaria", 4: "Preparatoria", 5: "Universidad", 6: "Especial/otra"}


def extraer():
    if (CAPAS / "SECCION.shp").exists():
        return
    with zipfile.ZipFile(CARTO / "bgd_11_Shapefile.zip") as z:
        z.extractall(CARTO)
    with py7zr.SevenZipFile(CARTO / "11 GUANAJUATO.7z") as z:
        z.extractall(CARTO / "bgd")


def main():
    extraer()
    sec = gpd.read_file(CAPAS / "SECCION.shp")
    sec = sec[sec.municipio == LEON][["seccion", "distrito_f", "distrito_l", "tipo", "geometry"]]
    sec = sec.dissolve(by="seccion", as_index=False)  # por si una sección viene partida en varias piezas
    sec = sec.to_crs(4326)
    sec["geometry"] = sec.geometry.simplify(0.00005, preserve_topology=True)  # ~5 m, aligera el mapa

    m = pd.read_csv(PROC / "leon_maestra.csv")
    s24 = set(m.loc[m.anio == 2024, "seccion"])
    panel = set(m.loc[m.en_panel_2015_2024, "seccion"])
    carto = set(sec.seccion)
    cob24 = len(s24 & carto) / len(s24)
    print(f"Polígonos León: {len(sec)} | secciones 2024 en datos: {len(s24)} | con polígono: {cob24:.1%}")
    print(f"Panel 2015-2024 con polígono: {len(panel & carto) / len(panel):.1%}")
    print(f"Sin polígono (2024): {sorted(s24 - carto)[:20]} | polígonos sin datos 2024: {sorted(carto - s24)[:20]}")
    assert cob24 >= 0.95, "menos del 95% de las secciones 2024 tienen polígono"

    tipos = m[m.anio == 2024].groupby("seccion").tipo_seccion.first()
    cruce = sec.set_index("seccion").tipo.to_frame().join(tipos, how="inner")
    print("Código 'tipo' de la cartografía vs tipo de sección del conteo censal:")
    print(pd.crosstab(cruce.tipo, cruce.tipo_seccion).to_string())

    PROC.mkdir(parents=True, exist_ok=True)
    sec.rename(columns={"distrito_f": "distrito_federal", "distrito_l": "distrito_local", "tipo": "tipo_carto"}) \
       .to_file(PROC / "leon_secciones.geojson", driver="GeoJSON")

    esc = gpd.read_file(CAPAS / "ESCUELA.shp").to_crs(4326)
    esc = gpd.sjoin(esc, sec[["seccion", "geometry"]], predicate="within").drop(columns="index_right")
    # La capa no trae catálogo de TIPO; nivel inferido a partir de los nombres de las escuelas
    esc["nivel"] = esc.TIPO.map(NIVEL_ESCUELA)
    esc = esc[esc.nivel.isin(["Preparatoria", "Universidad"])][["NOMBRE", "nivel", "seccion", "geometry"]]
    print(f"Preparatorias y universidades en León: {esc.nivel.value_counts().to_dict()}")
    esc.to_file(PROC / "leon_escuelas.geojson", driver="GeoJSON")


if __name__ == "__main__":
    main()
