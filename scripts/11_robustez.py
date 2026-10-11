"""Robustez del semáforo y de los escenarios.

Uso: python scripts/11_robustez.py   (requiere 06_modelo.py y 07_escenarios.py)
Resultado: outputs/robustez.md

1. Error de la predicción juvenil: se repite el método completo para predecir a los jóvenes de 2021
   (modelo entrenado con 2015) y se mide el error contra lo observado.
2. Secciones rojas firmes vs. probables según ese margen de error.
3. Sensibilidad del semáforo a los cortes y al ajuste por caída.
4. Escenario "solo evidencia europea": conversación +0.78 pts (Bhatti et al., 2016, como se citó en
   Townsley, 2025) y cero para volante, escuelas y simulacros.
"""
import importlib.util
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


def error_juvenil():
    """Predice la participación juvenil de 2021 con el mismo método que para 2027."""
    m = pd.read_csv(PROC / "leon_maestra.csv")
    s, ciudad, ciudad_jov = modelo.tasas(m)
    tr = modelo.filas(s, 2015).dropna(subset=["y"])
    te = modelo.filas(s, 2021)
    mod = modelo.modelos()["Regresión lineal"].fit(tr[modelo.NUM + modelo.CAT], tr.y)
    pos = pd.Series(mod.predict(te[modelo.NUM + modelo.CAT]), index=te.index)
    # Igual que en 2027: nivel de la intermedia anterior (2015) + posición; brecha de la intermedia anterior
    part = ciudad[2015] + pos
    brecha = s.xs(2015).brecha_jov.reindex(te.index).fillna(ciudad_jov[2015] - ciudad[2015])
    pred = (part + brecha).clip(0, 100)
    real = s.xs(2021).part_jov.reindex(te.index)
    ok = real.notna() & pred.notna()
    err = (pred[ok] - real[ok])
    # Error relativo a la ciudad (lo que el semáforo compara): se quita el sesgo de nivel
    err_rel = err - err.mean()
    return {"n": int(ok.sum()), "sesgo_nivel": err.mean(), "mae": err.abs().mean(),
            "mae_rel": err_rel.abs().mean(), "q80": err_rel.abs().quantile(0.8)}


def main():
    e = pd.read_csv(PROC / "escenarios_2027.csv")
    ej = error_juvenil()
    q = ej["q80"]

    rojas = e[e.semaforo_A == "rojo"]
    firmes = int((rojas.part_jov_2027 + q < escen.CORTE_ROJO).sum())
    por_caida = int(((rojas.part_jov_2027 >= escen.CORTE_ROJO)).sum())
    probables = len(rojas) - firmes - por_caida

    sens = []
    for rojo, verde in [(27.5, 37.5), (30, 40), (32.5, 42.5)]:
        nivel = np.select([e.part_jov_2027 < rojo, e.part_jov_2027 < verde], [2, 1], 0)
        con = np.where(e.tend_intermedia.fillna(0) <= escen.CAIDA, np.minimum(nivel + 1, 2), nivel)
        sens.append({"cortes": f"{rojo} / {verde}", "rojas_con_ajuste": int((con == 2).sum()),
                     "rojas_sin_ajuste": int((nivel == 2).sum())})

    # Escenario solo evidencia europea en las mismas secciones intervenidas
    dj = np.where(e.intervenida, escen.CONTACTO * 0.78, 0.0)
    jov_eu = e.part_jov_2027 + dj
    sem_eu = escen.semaforo(jov_eu, e.tend_intermedia)
    votos_eu = int((dj / 100 * e.ln_jov_2024).sum())
    rojas_eu = int((sem_eu == "rojo").sum())

    md = ["# Robustez del semáforo y de los escenarios", "",
          "## 1. Error de la predicción juvenil (validación con 2021)", "",
          f"Secciones evaluadas: {ej['n']}. Sesgo de nivel (toda la ciudad): {ej['sesgo_nivel']:+.1f} pts. "
          f"Error absoluto medio: {ej['mae']:.1f} pts; quitando el sesgo de nivel: {ej['mae_rel']:.1f} pts. "
          f"El 80 % de las secciones queda a menos de **±{q:.1f} pts**.", "",
          "## 2. Secciones rojas firmes y probables", "",
          f"De {len(rojas)} secciones rojas: **{firmes} firmes** (siguen en rojo aun sumando +{q:.1f} pts), "
          f"{probables} probables (cerca del corte) y {por_caida} en rojo por el ajuste de caída.", "",
          "## 3. Sensibilidad del semáforo", "",
          pd.DataFrame(sens).to_markdown(index=False), "",
          "## 4. Escenario solo evidencia europea", "",
          f"Conversación +0.78 pts y cero en lo demás: **{votos_eu:,} votos jóvenes adicionales** y "
          f"{len(rojas) - rojas_eu} secciones salen del riesgo alto ({rojas_eu} rojas)."]
    (OUT / "robustez.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
