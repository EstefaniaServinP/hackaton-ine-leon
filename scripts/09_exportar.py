"""HINE-22: base anonimizada y GeoJSON de escenarios para la entrega.

Uso: python scripts/09_exportar.py   (requiere 02_limpieza.py, 05_cartografia.py y 07_escenarios.py)
Resultado (outputs/entrega/):
  base_anonimizada.csv       conteos agregados por año x sección x sexo x grupo de edad (sin datos personales)
  escenarios_2027.csv        resultados por sección (escenarios A y B, semáforos)
  escenarios_2027.geojson    lo mismo con el polígono de cada sección
"""
from pathlib import Path

import geopandas as gpd
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
PROC = RAIZ / "data" / "processed"
ENTREGA = RAIZ / "outputs" / "entrega"


def main():
    ENTREGA.mkdir(parents=True, exist_ok=True)
    base = pd.read_csv(PROC / "leon_maestra.csv")
    assert {"anio", "seccion", "sexo", "grupo_edad"} <= set(base.columns) and "edad" not in base.columns
    base.to_csv(ENTREGA / "base_anonimizada.csv", index=False)

    esc = pd.read_csv(PROC / "escenarios_2027.csv")
    esc.to_csv(ENTREGA / "escenarios_2027.csv", index=False)
    geo = gpd.read_file(PROC / "leon_secciones.geojson")[["seccion", "geometry"]]
    g = geo.merge(esc, on="seccion", how="inner")
    assert {"semaforo_A", "semaforo_B_medio", "part_jov_2027", "part_jov_B_medio"} <= set(g.columns)
    g.to_file(ENTREGA / "escenarios_2027.geojson", driver="GeoJSON")
    print(f"base_anonimizada.csv: {len(base):,} filas · escenarios: {len(esc)} secciones · geojson: {len(g)} polígonos")


if __name__ == "__main__":
    main()
