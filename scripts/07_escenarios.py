"""HINE-18 y HINE-19: semáforo de riesgo 2027 y escenarios sin y con intervención.

Uso: python scripts/07_escenarios.py   (requiere 04_territorial.py, 06_modelo.py y 13_censo.py)
Resultado:
  data/processed/escenarios_2027.csv   una fila por sección: semáforo, escenarios y prioridad
  outputs/resumen_escenarios.md       tablas para el reporte
  outputs/cifras_clave.json           cifras que deben coincidir en reporte y presentación

Semáforo: solo la participación juvenil predicha para 2027 (rojo < 30 %, amarillo 30-40 %, verde >= 40 %).
La caída 2015->2021 ya entra al modelo; aquí solo marca prioridad (no cambia el color).

Intervención "Brigada CAE-SE Joven", versión acotada a lo que no agrega recorridos:
  - Dónde: todas las secciones rojas (criterio público y automático, sin datos partidistas).
  - Qué: durante la visita que el CAE ya hace a cada persona sorteada, deja en ese hogar un volante
    neutral que invita a los jóvenes a votar. El sorteo cubre el 13 % de la lista nominal
    (INE, Guía CAE 2023-2024, p. 16); en Guanajuato no se localizó al 21.6 % (INE, informe primera etapa
    2023-2024, p. 73). Hogares alcanzados ~ 13 % x 78.4 % de la LN, con tope en las viviendas habitadas (Censo 2020).
  - Efecto por joven que vive en un hogar alcanzado (puntos), con base en material impreso no partidista:
      pesimista 0.2 · medio 0.5 · optimista 1.0
    (Gerber y Huber, 2016: envío no partidista < 0.5; Bhatti et al., 2016, como se citó en Townsley, 2025:
    0.78 por contacto en Europa). No se supone conversación con el joven.
  - Brigadas escolares y simulacros abiertos: complementos no cuantificados.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
PROC = RAIZ / "data" / "processed"
OUT = RAIZ / "outputs"

CORTE_ROJO, CORTE_VERDE, CAIDA = 30, 40, -3
NIVELES = ["verde", "amarillo", "rojo"]
SORTEO = 0.13
LOCALIZABLE = 1 - 0.2157  # en Guanajuato no se localizó al 21.57 % de la ciudadanía visitada (INE, informe 1a etapa 2023-2024, p. 73)
EFECTO = {"pesimista": 0.2, "medio": 0.5, "optimista": 1.0}  # puntos por joven en hogar alcanzado


def semaforo(part_jov, tend=None):
    """Color por participación juvenil predicha. `tend` se acepta por compatibilidad y no se usa."""
    nivel = np.select([part_jov < CORTE_ROJO, part_jov < CORTE_VERDE], [2, 1], 0)
    return pd.Series(np.array(NIVELES)[nivel], index=part_jov.index)


def main():
    p = pd.read_csv(PROC / "prediccion_2027.csv").set_index("seccion")
    censo = pd.read_csv(PROC / "censo_secciones.csv").set_index("seccion")
    top50 = set(pd.read_csv(OUT / "top50_caida.csv").seccion)

    p["semaforo_A"] = semaforo(p.part_jov_2027)
    p["viene_cayendo"] = p.tend_intermedia.fillna(0) <= CAIDA
    p["top50"] = p.index.isin(top50)
    p["intervenida"] = p.semaforo_A == "rojo"
    # Prioridad dentro del rojo: 1 = top 50 de caída, 2 = viene cayendo, 3 = resto
    p["prioridad"] = np.where(~p.intervenida, 0, np.where(p.top50, 1, np.where(p.viene_cayendo, 2, 3)))

    # Alcance: hogares de personas sorteadas / viviendas habitadas (sin censo: mediana de las rojas)
    viv = censo.viviendas.reindex(p.index)
    hogares = SORTEO * LOCALIZABLE * p.ln_2024
    alcance = (hogares / viv).clip(upper=1)
    alcance = alcance.fillna(alcance[p.intervenida].median())
    p["alcance_hogares"] = alcance.round(3)
    p["volantes"] = np.where(p.intervenida, hogares.round(), 0)

    filas = []
    for nombre, ef in EFECTO.items():
        dj = np.where(p.intervenida, alcance * ef, 0.0)  # puntos sobre todos los jóvenes de la sección
        p[f"part_jov_B_{nombre}"] = (p.part_jov_2027 + dj).clip(upper=100).round(2)
        p[f"part_B_{nombre}"] = (p.part_2027 + dj * p.pct_jov / 100).round(2)
        p[f"votos_extra_{nombre}"] = (dj / 100 * p.ln_jov_2024).round(1)
        p[f"semaforo_B_{nombre}"] = semaforo(p[f"part_jov_B_{nombre}"])
        votos = float(p[f"votos_extra_{nombre}"].sum())
        filas.append({
            "escenario": nombre,
            "efecto_por_joven_alcanzado_pts": ef,
            "efecto_medio_seccion_pts": round(float(dj[p.intervenida.values].mean()), 2),
            "votos_jovenes_extra": int(round(votos)),
            "rojas_B": int((p[f"semaforo_B_{nombre}"] == "rojo").sum()),
            "salen_de_rojo": int(((p.semaforo_A == "rojo") & (p[f"semaforo_B_{nombre}"] != "rojo")).sum()),
            "pesos_por_voto_por_peso_de_volante": round(float(p.volantes.sum()) / votos, 0) if votos else None,
        })
    p.reset_index().to_csv(PROC / "escenarios_2027.csv", index=False)

    r = pd.DataFrame(filas)
    iv = p[p.intervenida]
    conteo = pd.DataFrame({"A (sin intervención)": p.semaforo_A.value_counts()}
                          | {f"B {k}": p[f"semaforo_B_{k}"].value_counts() for k in EFECTO}).reindex(NIVELES[::-1]).fillna(0).astype(int)
    ln, lnj = p.ln_2024, p.ln_jov_2024
    total = {k: float((p[c] * ln).sum() / ln.sum()) for k, c in [("A", "part_2027")] + [(k, f"part_B_{k}") for k in EFECTO]}
    jov = {k: float((p[c] * lnj).sum() / lnj.sum()) for k, c in [("A", "part_jov_2027")] + [(k, f"part_jov_B_{k}") for k in EFECTO]}
    jov_alcanzados = float((iv.alcance_hogares * iv.ln_jov_2024).sum())

    cifras = {
        "rojas": int((p.semaforo_A == "rojo").sum()), "amarillas": int((p.semaforo_A == "amarillo").sum()),
        "verdes": int((p.semaforo_A == "verde").sum()),
        "jovenes_en_rojas": int(iv.ln_jov_2024.sum()),
        "pct_jovenes_en_rojas": round(100 * iv.ln_jov_2024.sum() / lnj.sum()),
        "pct_secciones_rojas": round(100 * len(iv) / len(p)),
        "rojas_top50": int(iv.top50.sum()), "rojas_cayendo": int(iv.viene_cayendo.sum()),
        "rojas_rurales_mixtas": int(iv.tipo_seccion.isin(["R", "M"]).sum()),
        "volantes": int(iv.volantes.sum()), "jovenes_alcanzados": int(round(jov_alcanzados)),
        "alcance_medio_hogares_pct": round(100 * iv.alcance_hogares.mean()),
        "votos": {f["escenario"]: f["votos_jovenes_extra"] for f in filas},
        "salen_de_rojo": {f["escenario"]: f["salen_de_rojo"] for f in filas},
        "pesos_por_voto": {f["escenario"]: f["pesos_por_voto_por_peso_de_volante"] for f in filas},
        "participacion_total": {k: round(v, 1) for k, v in total.items()},
        "participacion_jovenes": {k: round(v, 1) for k, v in jov.items()},
    }
    (OUT / "cifras_clave.json").write_text(json.dumps(cifras, ensure_ascii=False, indent=1))

    md = ["# HINE-18 / HINE-19 — Semáforo 2027 y escenarios", "",
          f"Secciones intervenidas: {len(iv)} (todas las rojas). Volantes: {cifras['volantes']:,} (uno por hogar de "
          f"persona sorteada). Jóvenes que viven en hogares alcanzados: ~{cifras['jovenes_alcanzados']:,} "
          f"(alcance medio {cifras['alcance_medio_hogares_pct']} % de los hogares de cada sección roja).", "",
          "## Semáforo (número de secciones)", "", conteo.to_markdown(), "",
          "## Resultado por escenario", "", r.to_markdown(index=False), "",
          "## Participación de León 2027 (ponderada por lista nominal)", "",
          pd.DataFrame({"Total %": total, "Jóvenes 18-29 %": jov}).round(2).to_markdown(), "",
          "Semáforo: rojo < 30 %, amarillo 30–40 %, verde ≥ 40 % de participación juvenil predicha (sin ajuste por caída). "
          "Prioridad dentro del rojo: top 50 de caída, luego las que vienen cayendo, luego el resto."]
    (OUT / "resumen_escenarios.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
