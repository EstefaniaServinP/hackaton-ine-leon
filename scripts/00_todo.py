"""Corre todo el análisis, en orden, para León o para cualquier otro municipio.

Uso:
  python scripts/00_todo.py                                            # León, Guanajuato (por defecto)
  python scripts/00_todo.py --entidad 11 --listar                      # claves de los municipios del estado
  python scripts/00_todo.py --entidad 11 --municipio 17 --nombre Irapuato

Antes, para un estado distinto de Guanajuato, hay que descargar a mano dos cosas (ver README):
  - data/raw/cartografia/bgd_<clave>_Shapefile.zip   (Base Geográfica Digital del INE, SIGE 8)
  - data/raw/censo/<clave>/*.xlsx                   (los 7 indicadores del Censo 2020 por sección)
Los Conteos Censales los descarga 01_descarga.py.
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
PASOS = ["01_descarga", "02_limpieza", "03_graficas_edad", "04_territorial", "05_cartografia", "13_censo",
         "06_modelo", "07_escenarios", "08_mapa", "09_exportar", "10_figura_mapa", "11_robustez", "12_piloto",
         "14_fichas", "15_anexo"]


def listar(entidad):
    """Municipios del estado con su clave del INE, a partir de la cartografía y de los Conteos Censales 2024."""
    os.environ["ENTIDAD"] = str(entidad)
    sys.path.insert(0, str(SCRIPTS))
    import config
    import pandas as pd
    d = pd.read_csv(config.csv_estado(2024), encoding="utf-8-sig", usecols=["MPIOCVE", "SECCION", "LN"])
    t = d.groupby("MPIOCVE").agg(secciones=("SECCION", "nunique"), lista_nominal=("LN", "sum"))
    capas = [p for p in (config.CARTO / "bgd").glob(f"{entidad:02d} *") if (p / "MUNICIPIO.shp").exists()]
    if capas:
        import geopandas as gpd
        nombres = gpd.read_file(capas[0] / "MUNICIPIO.shp", ignore_geometry=True).set_index("municipio").nombre
        t.insert(0, "nombre", nombres.reindex(t.index))
    print(t.sort_values("lista_nominal", ascending=False).to_string())


def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--entidad", type=int, default=11, help="clave del estado, 1 a 32 (Guanajuato = 11)")
    a.add_argument("--municipio", type=int, default=20, help="clave de municipio del INE (León = 20)")
    a.add_argument("--nombre", default="León", help="nombre del municipio, para títulos y carpetas")
    a.add_argument("--listar", action="store_true", help="solo muestra las claves de los municipios del estado")
    a.add_argument("--desde", default=PASOS[0], help="empezar en este paso (por ejemplo 06_modelo)")
    args = a.parse_args()
    if args.listar:
        return listar(args.entidad)
    if (args.entidad, args.municipio) != (11, 20) and args.nombre == "León":
        a.error("indica --nombre del municipio")
    env = {**os.environ, "ENTIDAD": str(args.entidad), "MUNICIPIO": str(args.municipio), "NOMBRE": args.nombre}
    pasos = PASOS + (["16_comparar_modelos"] if (args.entidad, args.municipio) == (11, 20) else [])
    for paso in pasos[pasos.index(args.desde):]:
        print(f"\n=== {paso} ({args.nombre}) ===", flush=True)
        subprocess.run([sys.executable, str(SCRIPTS / f"{paso}.py")], env=env, check=True)


if __name__ == "__main__":
    main()
