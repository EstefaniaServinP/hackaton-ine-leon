"""Robustez del semáforo y del modelo.

Uso: python scripts/11_robustez.py   (requiere 06_modelo.py y 07_escenarios.py)
Resultado: outputs/robustez.md y claves "robustez" en outputs/cifras_clave.json

1. Validación con intervalo de confianza: error del modelo contra la mejor regla simple en 2021, con
   remuestreo (bootstrap) de secciones.
2. Error de la predicción juvenil: se repite el método completo para predecir a los jóvenes de 2021
   (nivel de la ciudad incluido), y se reporta el error real y el error relativo a la ciudad.
3. Secciones rojas firmes: siguen en rojo aunque la predicción suba el margen de error.
4. Sensibilidad del semáforo a los cortes y al nivel de León en 2027 (±3 puntos).
"""
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
PROC = RAIZ / "data" / "processed"
OUT = RAIZ / "outputs"


def cargar(nombre):
    spec = importlib.util.spec_from_file_location(nombre, RAIZ / "scripts" / f"{nombre}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


modelo = cargar("06_modelo")
escen = cargar("07_escenarios")


def validacion_con_intervalo(s, repeticiones=2000, semilla=7):
    tr = modelo.filas(s, 2015).dropna(subset=["y"])
    te = modelo.filas(s, 2021).dropna(subset=["y"])
    mod = modelo.modelos()["Regresión lineal"].fit(tr[modelo.NUM + modelo.CAT], tr.y)
    e_mod = np.abs(mod.predict(te[modelo.NUM + modelo.CAT]) - te.y.values)
    e_base = np.abs(te.pos_anterior.fillna(0).values - te.y.values)
    rng = np.random.default_rng(semilla)
    dif = [(e_base[i] - e_mod[i]).mean() for i in (rng.integers(0, len(te), len(te)) for _ in range(repeticiones))]
    return {"mae_modelo": e_mod.mean(), "mae_regla": e_base.mean(), "mejora": e_base.mean() - e_mod.mean(),
            "ic_bajo": float(np.percentile(dif, 2.5)), "ic_alto": float(np.percentile(dif, 97.5)), "n": len(te)}


def error_juvenil(s, ciudad, ciudad_jov):
    tr = modelo.filas(s, 2015).dropna(subset=["y"])
    te = modelo.filas(s, 2021)
    mod = modelo.modelos()["Regresión lineal"].fit(tr[modelo.NUM + modelo.CAT], tr.y)
    pos = pd.Series(mod.predict(te[modelo.NUM + modelo.CAT]), index=te.index)
    part = ciudad[2015] + pos  # igual que en 2027: nivel de la intermedia anterior
    brecha = s.xs(2015).brecha_jov.reindex(te.index).fillna(ciudad_jov[2015] - ciudad[2015])
    pred = (part + brecha).clip(0, 100)
    real = s.xs(2021).part_jov.reindex(te.index)
    ok = real.notna() & pred.notna()
    err = pred[ok] - real[ok]
    rel = err - err.mean()
    return {"n": int(ok.sum()), "sesgo": float(err.mean()), "mae_real": float(err.abs().mean()),
            "mae_rel": float(rel.abs().mean()), "q80_real": float(err.abs().quantile(0.8)),
            "q80_rel": float(rel.abs().quantile(0.8))}


def main():
    s, ciudad, ciudad_jov = modelo.tasas(pd.read_csv(PROC / "leon_maestra.csv"))
    v = validacion_con_intervalo(s)
    ej = error_juvenil(s, ciudad, ciudad_jov)
    e = pd.read_csv(PROC / "escenarios_2027.csv")
    rojas = e[e.semaforo_A == "rojo"]
    firmes = int((rojas.part_jov_2027 + ej["q80_rel"] < escen.CORTE_ROJO).sum())

    sens = []
    for rojo, verde in [(27.5, 37.5), (30, 40), (32.5, 42.5)]:
        sens.append({"prueba": f"Cortes {rojo} % / {verde} %",
                     "rojas": int((e.part_jov_2027 < rojo).sum())})
    for delta in [-3, 3]:
        sens.append({"prueba": f"Nivel de León en 2027 {delta:+d} puntos",
                     "rojas": int((e.part_jov_2027 + delta < escen.CORTE_ROJO).sum())})

    md = ["# Robustez del semáforo y del modelo", "",
          "## 1. Validación con intervalo de confianza (prueba 2021, " f"{v['n']} secciones)", "",
          f"Error del modelo {v['mae_modelo']:.2f} pts contra {v['mae_regla']:.2f} de la mejor regla simple: mejora de "
          f"{v['mejora']:.2f} pts (IC 95 % por remuestreo: {v['ic_bajo']:.2f} a {v['ic_alto']:.2f}).", "",
          "## 2. Error de la predicción juvenil (validación con 2021)", "",
          f"Sesgo de nivel de toda la ciudad: {ej['sesgo']:+.1f} pts. Error absoluto medio real: {ej['mae_real']:.1f} pts "
          f"(relativo a la ciudad: {ej['mae_rel']:.1f}). El 80 % de las secciones queda a menos de ±{ej['q80_real']:.1f} pts "
          f"en términos reales y ±{ej['q80_rel']:.1f} pts relativo a la ciudad.", "",
          "## 3. Secciones rojas firmes", "",
          f"De {len(rojas)} secciones rojas, **{firmes}** siguen en rojo aunque su predicción suba {ej['q80_rel']:.1f} pts.", "",
          "## 4. Sensibilidad del semáforo", "", pd.DataFrame(sens).to_markdown(index=False)]
    (OUT / "robustez.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))

    ruta = OUT / "cifras_clave.json"
    cifras = json.loads(ruta.read_text())
    cifras["robustez"] = {"mae_modelo": round(v["mae_modelo"], 2), "mae_regla": round(v["mae_regla"], 2),
                          "ic_mejora": [round(v["ic_bajo"], 2), round(v["ic_alto"], 2)],
                          "error_real_q80": round(ej["q80_real"], 1), "error_rel_q80": round(ej["q80_rel"], 1),
                          "rojas_firmes": firmes, "rojas_rango": [min(x["rojas"] for x in sens), max(x["rojas"] for x in sens)],
                          "sensibilidad": {x["prueba"]: x["rojas"] for x in sens}}
    ruta.write_text(json.dumps(cifras, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
