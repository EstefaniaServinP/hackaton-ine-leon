"""¿Un modelo más complejo predice mejor? Comparación de 7 métodos en varios municipios con el mismo examen.

Uso: python scripts/16_comparar_modelos.py   (usa los Conteos Censales ya descargados; corre 02_limpieza.py
     para cada municipio que no tenga su tabla maestra)
Resultado: outputs/comparacion_modelos.md y la clave "comparacion_modelos" en outputs/cifras_clave.json

Examen: con datos hasta 2018, cada método estima la posición de cada sección en la intermedia de 2021 (entrenado con
la intermedia de 2015, igual que 06_modelo.py). Se reporta el error absoluto medio en puntos.
Para los municipios sin el Censo descargado, el modelo corre sin la escolaridad.
"""
import json
import os
import subprocess
import sys
import warnings
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
MUNICIPIOS = [(11, 20, "León"), (11, 17, "Irapuato"), (8, 37, "Juárez"), (8, 19, "Chihuahua")]


def evaluar():
    """Errores de los 7 métodos para el municipio de config.py (se llama en un proceso aparte por municipio)."""
    import importlib.util
    import numpy as np
    import pandas as pd
    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import GradientBoostingRegressor, HistGradientBoostingRegressor
    from sklearn.impute import SimpleImputer
    from sklearn.metrics import mean_absolute_error
    from sklearn.neural_network import MLPRegressor
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    warnings.simplefilter("ignore")
    import config
    spec = importlib.util.spec_from_file_location("modelo", SCRIPTS / "06_modelo.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)

    s, _, _ = m.tasas(pd.read_csv(config.MAESTRA))
    tr, te = m.filas(s, 2015).dropna(subset=["y"]), m.filas(s, 2021).dropna(subset=["y"])
    prep = lambda: ColumnTransformer([  # noqa: E731
        ("num", make_pipeline(SimpleImputer(strategy="median", add_indicator=True), StandardScaler()), m.NUM),
        ("cat", OneHotEncoder(handle_unknown="ignore"), m.CAT)])
    metodos = dict(m.modelos())
    metodos["Gradient boosting"] = make_pipeline(prep(), GradientBoostingRegressor(
        n_estimators=300, max_depth=2, learning_rate=0.05, subsample=0.8, random_state=42))
    metodos["XGBoost (versión de scikit-learn)"] = make_pipeline(prep(), HistGradientBoostingRegressor(
        max_depth=3, learning_rate=0.05, max_iter=300, random_state=42))
    metodos["Red neuronal"] = make_pipeline(prep(), MLPRegressor(
        hidden_layer_sizes=(32, 16), alpha=1.0, max_iter=3000, early_stopping=True, random_state=42))
    errores = {}
    for nombre, mod in metodos.items():
        mod.fit(tr[m.NUM + m.CAT], tr.y)
        errores[nombre] = round(float(mean_absolute_error(te.y, mod.predict(te[m.NUM + m.CAT]))), 2)
    return {"municipio": config.NOMBRE, "secciones_prueba": len(te), "filas_entrenamiento": len(tr),
            "con_censo": bool(m.CENSO.escolaridad.notna().any()), "errores": errores,
            "elegido": m.elegir(s)[0]}


def main():
    if os.environ.get("SOLO_EVALUAR"):
        print(json.dumps(evaluar(), ensure_ascii=False))
        return
    sys.path.insert(0, str(SCRIPTS))
    filas = []
    for ent, mun, nombre in MUNICIPIOS:
        env = {**os.environ, "ENTIDAD": str(ent), "MUNICIPIO": str(mun), "NOMBRE": nombre}
        maestra = subprocess.run([sys.executable, "-c", "import config; print(config.MAESTRA)"], cwd=SCRIPTS,
                                 env=env, capture_output=True, text=True, check=True).stdout.strip()
        if not Path(maestra).exists():
            subprocess.run([sys.executable, str(SCRIPTS / "01_descarga.py")], env=env, check=True)
            subprocess.run([sys.executable, str(SCRIPTS / "02_limpieza.py")], env=env, check=True)
        r = subprocess.run([sys.executable, str(SCRIPTS / "16_comparar_modelos.py")], env={**env, "SOLO_EVALUAR": "1"},
                           capture_output=True, text=True, check=True)
        filas.append(json.loads(r.stdout.strip().splitlines()[-1]))
        print(f"{nombre}: listo", flush=True)

    import pandas as pd
    import config  # León, para guardar en outputs/
    t = pd.DataFrame({f["municipio"]: f["errores"] for f in filas})
    t = t.loc[t.mean(axis=1).sort_values().index]
    pie = pd.DataFrame({f["municipio"]: {"Secciones en la prueba": f["secciones_prueba"],
                                          "Con escolaridad del Censo": "sí" if f["con_censo"] else "no",
                                          "Método elegido": f["elegido"]} for f in filas})
    md = ["# ¿Un modelo más complejo predice mejor?", "",
          "Error promedio (puntos de posición) al estimar 2021 con datos hasta 2018. Menos es mejor.", "",
          t.to_markdown(), "", pie.to_markdown(), "",
          "Lectura: ningún método gana en todos lados, y entre los mejores la diferencia es menor a medio punto. "
          "Los modelos complejos solo ganan una vez y por poco; con pocas elecciones por sección tienden a memorizar el "
          "ruido de una elección. Por eso 06_modelo.py elige, en cada municipio, entre cuatro candidatos simples "
          "(regla simple, regresión lineal, Ridge y random forest) el que menos se equivoca."]
    (config.OUT / "comparacion_modelos.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))
    ruta = config.OUT / "cifras_clave.json"
    cifras = json.loads(ruta.read_text())
    cifras["comparacion_modelos"] = filas
    ruta.write_text(json.dumps(cifras, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
