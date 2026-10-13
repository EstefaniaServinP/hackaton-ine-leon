"""Variables sociodemográficas del Censo 2020 por sección electoral (INEGI, Estadísticas Censales a
Escalas Geoelectorales 2020), descargadas del Mapa Digital de México para Guanajuato, una por archivo.

Uso: python scripts/13_censo.py
Entrada: data/raw/censo/{poblacion,escolaridad,viviendas,internet,pea,migracion,pob_12a14}.xlsx
Resultado: data/processed/censo_secciones.csv
"""
import warnings
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
CENSO = RAIZ / "data" / "raw" / "censo"
INDICADORES = {
    "poblacion": "Población total",
    "escolaridad": "Grado promedio de escolaridad",
    "viviendas": "Viviendas particulares habitadas",
    "internet": "Viviendas particulares habitadas que disponen de internet",
    "pea": "Población de 12 años y más económicamente activa",
    "migracion": "Población nacida en otra entidad",
    "pob_12a14": "Población de 12 a 14 años",  # en junio de 2027 tendrán unos 18 a 21: votan por primera vez
}


def leer(nombre):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # el archivo del INEGI no trae estilos por defecto
        d = pd.read_excel(CENSO / f"{nombre}.xlsx", dtype=str)
    d = d[d["Clave Geográfica"].fillna("").str.fullmatch(r"\d{8}")]  # 11 + distrito federal + sección
    return pd.Series(pd.to_numeric(d.Valor, errors="coerce").values, index=d.Nombre.astype(int), name=nombre)


def main():
    c = pd.concat([leer(n) for n in INDICADORES], axis=1)
    c.index.name = "seccion"
    assert not c.index.duplicated().any()
    c["pct_internet"] = (100 * c.internet / c.viviendas).clip(upper=100)  # 4 secciones > 100 % por redondeo
    c["pct_pea"] = 100 * c.pea / c.poblacion
    c["pct_migracion"] = 100 * c.migracion / c.poblacion
    c.round(2).to_csv(RAIZ / "data" / "processed" / "censo_secciones.csv")
    print(f"{len(c):,} secciones de Guanajuato -> data/processed/censo_secciones.csv")
    print(c[["escolaridad", "pct_internet", "pct_pea", "pct_migracion"]].describe().round(1).to_string())


if __name__ == "__main__":
    main()
