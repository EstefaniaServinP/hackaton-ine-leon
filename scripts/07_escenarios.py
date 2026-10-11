"""HINE-18 y HINE-19: escenarios 2027 sin y con intervención, y semáforo de riesgo.

Uso: python scripts/07_escenarios.py   (requiere 04_territorial.py y 06_modelo.py)
Resultado:
  data/processed/escenarios_2027.csv   una fila por sección con escenario A, B (pesimista/medio/optimista) y semáforos
  outputs/resumen_escenarios.md       tablas para el reporte

Semáforo (riesgo de abstención juvenil, sobre la participación predicha de jóvenes 18-29 en 2027):
  rojo < 30 %, amarillo 30-40 %, verde >= 40 %.
  Si la sección cayó 3 puntos o más respecto a León entre las intermedias 2015 y 2021, sube un nivel.

Intervención "Brigada CAE-SE Joven" (outputs/intervencion.md): se aplica a las secciones rojas del
escenario A y a las 50 secciones con mayor caída (outputs/top50_caida.csv).
"""
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
PROC = RAIZ / "data" / "processed"
OUT = RAIZ / "outputs"

CORTE_ROJO, CORTE_VERDE, CAIDA = 30, 40, -3
NIVELES = ["verde", "amarillo", "rojo"]
CONTACTO = 0.25           # 1 de cada 4 viviendas abre la puerta (experiencia CAE)
ASISTENTES_SIMULACRO = 25  # ~2 simulacros por sección x 10-15 jóvenes
MAX_ASISTENCIA = 0.10      # tope: no más del 10 % de los jóvenes de la sección
# Efecto en puntos sobre la participación de jóvenes; simulacro sobre asistentes
SUPUESTOS = {
    "pesimista": {"conversacion": 2.5, "volante": 0.0, "escuela": 0.5, "simulacro": 5},
    "medio": {"conversacion": 3.0, "volante": 0.3, "escuela": 1.0, "simulacro": 10},
    "optimista": {"conversacion": 4.3, "volante": 0.5, "escuela": 2.0, "simulacro": 15},
}


def semaforo(part_jov, tend):
    nivel = np.select([part_jov < CORTE_ROJO, part_jov < CORTE_VERDE], [2, 1], 0)
    nivel = np.where(tend.fillna(0) <= CAIDA, np.minimum(nivel + 1, 2), nivel)
    return pd.Series(np.array(NIVELES)[nivel], index=part_jov.index)


def efecto_jovenes(sup, ln_jov):
    """Puntos de participación juvenil que suma la intervención en una sección."""
    casa = CONTACTO * sup["conversacion"] + (1 - CONTACTO) * sup["volante"]
    asistentes = np.minimum(ASISTENTES_SIMULACRO, MAX_ASISTENCIA * ln_jov)
    simulacro = asistentes * sup["simulacro"] / ln_jov.clip(lower=1)
    return casa + sup["escuela"] + simulacro


def main():
    p = pd.read_csv(PROC / "prediccion_2027.csv").set_index("seccion")
    top50 = set(pd.read_csv(OUT / "top50_caida.csv").seccion)

    p["semaforo_A"] = semaforo(p.part_jov_2027, p.tend_intermedia)
    p["intervenida"] = (p.semaforo_A == "rojo") | p.index.isin(top50)

    filas = []
    for nombre, sup in SUPUESTOS.items():
        dj = np.where(p.intervenida, efecto_jovenes(sup, p.ln_jov_2024), 0.0)
        p[f"part_jov_B_{nombre}"] = (p.part_jov_2027 + dj).clip(upper=100).round(2)
        p[f"part_B_{nombre}"] = (p.part_2027 + dj * p.pct_jov / 100).round(2)
        p[f"votos_extra_{nombre}"] = (dj / 100 * p.ln_jov_2024).round(1)
        p[f"semaforo_B_{nombre}"] = semaforo(p[f"part_jov_B_{nombre}"], p.tend_intermedia)
        cambio = p[p.intervenida]
        filas.append({
            "escenario": nombre,
            "efecto_jov_medio_pts": round(float(np.mean(dj[p.intervenida.values])), 2),
            "votos_jovenes_extra": int(p[f"votos_extra_{nombre}"].sum()),
            "rojas_A": int((p.semaforo_A == "rojo").sum()),
            "rojas_B": int((p[f"semaforo_B_{nombre}"] == "rojo").sum()),
            "salen_de_rojo": int(((cambio.semaforo_A == "rojo") & (cambio[f"semaforo_B_{nombre}"] != "rojo")).sum()),
        })
    p.reset_index().to_csv(PROC / "escenarios_2027.csv", index=False)

    r = pd.DataFrame(filas)
    conteo = pd.DataFrame({"A (sin intervención)": p.semaforo_A.value_counts()}
                          | {f"B {k}": p[f"semaforo_B_{k}"].value_counts() for k in SUPUESTOS}).reindex(NIVELES[::-1]).fillna(0).astype(int)
    ln = p.ln_2024
    total = pd.Series({"A (sin intervención)": (p.part_2027 * ln).sum() / ln.sum()}
                      | {f"B {k}": (p[f"part_B_{k}"] * ln).sum() / ln.sum() for k in SUPUESTOS}).round(2)
    lnj = p.ln_jov_2024
    jov = pd.Series({"A (sin intervención)": (p.part_jov_2027 * lnj).sum() / lnj.sum()}
                    | {f"B {k}": (p[f"part_jov_B_{k}"] * lnj).sum() / lnj.sum() for k in SUPUESTOS}).round(2)

    md = ["# HINE-18 / HINE-19 — Escenarios 2027 y semáforo de riesgo", "",
          f"Secciones intervenidas: {int(p.intervenida.sum())} (rojas en A ∪ top 50 de caída), "
          f"con {int(p.loc[p.intervenida, 'ln_jov_2024'].sum()):,} jóvenes en lista nominal (2024).", "",
          "## Semáforo (número de secciones)", "", conteo.to_markdown(), "",
          "## Resultado por escenario", "", r.to_markdown(index=False), "",
          "## Participación de León 2027 (ponderada por lista nominal)", "",
          pd.DataFrame({"Total %": total, "Jóvenes 18-29 %": jov}).to_markdown(), "",
          "Umbrales: rojo < 30 %, amarillo 30–40 %, verde ≥ 40 % de participación juvenil predicha; "
          "sube un nivel si la sección cayó ≥ 3 puntos respecto a León entre 2015 y 2021."]
    (OUT / "resumen_escenarios.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
