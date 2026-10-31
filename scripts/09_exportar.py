"""HINE-22: base anonimizada y GeoJSON de escenarios para la entrega.

Uso: python scripts/09_exportar.py   (requiere 02_limpieza.py, 05_cartografia.py y 07_escenarios.py)
Resultado (outputs/entrega/):
  base_anonimizada.csv       conteos agregados por año x sección x sexo x grupo de edad (sin datos personales)
  escenarios_2027.csv        resultados por sección (escenarios A y B, semáforos)
  escenarios_2027.geojson    lo mismo con el polígono de cada sección
"""
from pathlib import Path

import config
import geopandas as gpd
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
PROC = config.PROC
ENTREGA = config.OUT / "entrega"


def main():
    ENTREGA.mkdir(parents=True, exist_ok=True)
    base = pd.read_csv(config.MAESTRA)
    assert {"anio", "seccion", "sexo", "grupo_edad"} <= set(base.columns) and "edad" not in base.columns
    base.to_csv(ENTREGA / "base_anonimizada.csv", index=False)

    esc = pd.read_csv(PROC / "escenarios_2027.csv")
    esc.to_csv(ENTREGA / "escenarios_2027.csv", index=False)
    geo = gpd.read_file(config.SECCIONES)[["seccion", "geometry"]]
    g = geo.merge(esc, on="seccion", how="inner")
    assert {"semaforo_A", "semaforo_B_medio", "part_jov_2027", "part_jov_B_medio"} <= set(g.columns)
    g.to_file(ENTREGA / "escenarios_2027.geojson", driver="GeoJSON")
    # Universo 2024 vs. cartografía (corte del SIGE): secciones con predicción sin polígono y polígonos sin predicción
    sin_poligono = esc[~esc.seccion.isin(geo.seccion)][["seccion", "semaforo_A", "prioridad", "ln_jov_2024"]]
    sin_poligono.to_csv(ENTREGA / "secciones_sin_poligono.csv", index=False)
    geo[~geo.seccion.isin(esc.seccion)][["seccion"]].to_csv(ENTREGA / "poligonos_sin_prediccion.csv", index=False)
    print(f"base_anonimizada.csv: {len(base):,} filas · escenarios: {len(esc)} secciones · geojson: {len(g)} polígonos")
    print(f"Sin polígono en la cartografía: {len(sin_poligono)} secciones ({(sin_poligono.semaforo_A == 'rojo').sum()} rojas) · "
          f"polígonos sin predicción: {(~geo.seccion.isin(esc.seccion)).sum()}")


if __name__ == "__main__":
    main()
