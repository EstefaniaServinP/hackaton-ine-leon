"""HINE-9: tabla maestra de León (MPIOCVE = 20), 2009-2024.

Uso: python scripts/02_limpieza.py   (requiere haber corrido 01_descarga.py)
Resultado: data/processed/leon_maestra.csv
  Una fila por año x sección x sexo x grupo quinquenal de edad, con LN, SV, NV, NS.
"""
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
RAW = RAIZ / "data" / "raw"
SALIDA = RAIZ / "data" / "processed" / "leon_maestra.csv"

ANIOS = [2009, 2012, 2015, 2018, 2021, 2024]
INTERMEDIAS = {2009, 2015, 2021}
LEON = 20
PANEL = [2015, 2018, 2021, 2024]  # periodo para el modelo por sección (ver outputs/notas_secciones.md)

CORTES = [18, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 200]
ETIQUETAS = ["18-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49", "50-54",
             "55-59", "60-64", "65-69", "70-74", "75-79", "80-84", "85+"]
SEXO = {0: "Hombre", 1: "Mujer", 2: "No binario"}
CONTEOS = ["LN", "SV", "NV", "NS"]


def cargar():
    cols = ["AELEC", "MPIOCVE", "SECCION", "TIPOSEC", "DEF", "DEL", "SEXO", "EDAD"] + CONTEOS
    d = pd.concat(pd.read_csv(RAW / f"gto_{a}.csv", encoding="utf-8-sig", usecols=cols,
                              dtype={"DEF": str, "DEL": str}) for a in ANIOS)
    d = d[d.MPIOCVE == LEON].drop(columns="MPIOCVE")
    # En 2009 y 2012 algunas secciones (ya inexistentes en el marco 2023) traen el distrito en blanco
    for c in ["DEF", "DEL"]:
        d[c] = pd.to_numeric(d[c].str.strip(), errors="coerce").astype("Int64")
    return d


def limpiar(d):
    d = d.rename(columns={"AELEC": "anio", "SECCION": "seccion", "TIPOSEC": "tipo_seccion",
                          "DEF": "distrito_federal", "DEL": "distrito_local", "SEXO": "sexo", "EDAD": "edad"})
    d["sexo"] = d.sexo.map(SEXO)
    d["grupo_edad"] = pd.cut(d.edad, CORTES, right=False, labels=ETIQUETAS)
    d = (d.groupby(["anio", "seccion", "tipo_seccion", "distrito_federal", "distrito_local", "sexo", "grupo_edad"],
                   observed=True, dropna=False)[CONTEOS].sum().reset_index())
    d["grupo_amplio"] = pd.cut(d.grupo_edad.cat.codes, [-1, 2, 8, 99], labels=["18-29", "30-59", "60+"])
    d["tipo_eleccion"] = d.anio.map(lambda a: "Intermedia" if a in INTERMEDIAS else "Presidencial")
    en_todos = set.intersection(*(set(d.loc[d.anio == a, "seccion"]) for a in PANEL))
    d["en_panel_2015_2024"] = d.seccion.isin(en_todos)
    return d


def tasa(g):
    return round(100 * g.SV.sum() / g.LN.sum(), 1)


def validar(d):
    clave = ["anio", "seccion", "sexo", "grupo_edad"]
    assert not d.duplicated(clave).any(), "hay filas duplicadas"
    assert not ((d.LN == 0) & (d.SV > 0)).any(), "hay filas con LN = 0 y votos"
    assert (d.SV + d.NV + d.NS == d.LN).all(), "SV + NV + NS no suma LN"
    assert d.grupo_edad.notna().all(), "hay edades fuera de rango"
    d24 = d[d.anio == 2024]
    assert d24.seccion.nunique() == 777, d24.seccion.nunique()
    assert tasa(d24) == 58.0, tasa(d24)
    assert tasa(d24[d24.grupo_amplio == "18-29"]) == 47.9
    assert tasa(d24[d24.grupo_amplio == "60+"]) == 73.0


def main():
    d = limpiar(cargar())
    validar(d)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    d.to_csv(SALIDA, index=False)
    print(f"{len(d):,} filas -> {SALIDA.relative_to(RAIZ)}")
    print(d.groupby("anio").apply(tasa, include_groups=False).rename("participacion_%").to_string())
    print(f"Secciones en panel 2015-2024: {d.loc[d.en_panel_2015_2024, 'seccion'].nunique()}")


if __name__ == "__main__":
    main()
