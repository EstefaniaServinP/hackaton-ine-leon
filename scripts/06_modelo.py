"""HINE-17: predicción de la participación 2027 (elección intermedia) por sección de León.

Uso: python scripts/06_modelo.py   (requiere data/processed/leon_maestra.csv)
Resultado:
  data/processed/prediccion_2027.csv
  outputs/metricas_modelo.md

Idea (ver notas en outputs/metricas_modelo.md):
  participación capturada = SV / (SV + NV); años con NS > 20 % de la LN se descartan para esa sección.
  posición = participación de la sección - participación de León ese año.
  El modelo predice la posición en la elección t a partir de:
    - la posición en la elección del mismo tipo anterior (t-6) y en la elección inmediata anterior (t-3),
    - la brecha de jóvenes y la composición de la lista nominal en t-3.
  Como 2027 es intermedia, se entrena solo con transiciones presidencial -> intermedia:
    validación temporal: entrenar con t = 2015 (2009, 2012) -> probar con t = 2021 (2015, 2018).
    final: entrenar con t = 2015 y 2021 -> predecir t = 2027 (2021, 2024).
  Participación 2027 = nivel de León 2027 (supuesto: igual que la intermedia 2021) + posición predicha.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

RAIZ = Path(__file__).resolve().parent.parent
PROC = RAIZ / "data" / "processed"
CENSO = pd.read_csv(PROC / "censo_secciones.csv").set_index("seccion")
OUT = RAIZ / "outputs"
ANIOS = [2009, 2012, 2015, 2018, 2021, 2024]
MAX_NS = 0.20
NUM = ["pos_mismo_tipo", "pos_anterior", "brecha_jov_anterior", "pct_jov", "pct_60", "pct_muj", "log_ln", "crec_ln",
       "escolaridad"]  # grado promedio de escolaridad, Censo 2020 por sección (scripts/13_censo.py)
CAT = ["tipo_seccion"]


def tasas(m, max_ns=MAX_NS):
    """Participación capturada por sección y año, total y de jóvenes, y su posición respecto a León."""
    m = m[m.anio.isin(ANIOS)]
    g = m.groupby(["anio", "seccion"])
    s = g[["LN", "SV", "NV", "NS"]].sum()
    j = m[m.grupo_amplio == "18-29"].groupby(["anio", "seccion"])[["LN", "SV", "NV"]].sum()
    s["part"] = 100 * s.SV / (s.SV + s.NV)
    s["part_jov"] = 100 * j.SV / (j.SV + j.NV)
    s.loc[s.NS / s.LN > max_ns, ["part", "part_jov"]] = np.nan
    s["pct_jov"] = 100 * j.LN / s.LN
    s["pct_60"] = 100 * m[m.grupo_amplio == "60+"].groupby(["anio", "seccion"]).LN.sum() / s.LN
    s["pct_muj"] = 100 * m[m.sexo == "Mujer"].groupby(["anio", "seccion"]).LN.sum() / s.LN
    s["tipo_seccion"] = g.tipo_seccion.first()
    valido = s[s.part.notna()]
    ciudad = valido.groupby("anio").apply(lambda x: 100 * x.SV.sum() / (x.SV.sum() + x.NV.sum()), include_groups=False)
    jv = m[m.grupo_amplio == "18-29"].join(s.part.isna().rename("excluir"), on=["anio", "seccion"])
    jv = jv[~jv.excluir].groupby("anio")[["SV", "NV"]].sum()
    ciudad_jov = 100 * jv.SV / (jv.SV + jv.NV)
    a = s.index.get_level_values("anio")
    s["pos"] = s.part - a.map(ciudad)
    s["brecha_jov"] = s.part_jov - s.part
    return s, ciudad, ciudad_jov


def filas(s, t):
    """Variables para predecir la posición en la elección t."""
    mismo, ant = t - 6, t - 3
    x = s.xs(ant)[["pos", "brecha_jov", "pct_jov", "pct_60", "pct_muj", "LN", "tipo_seccion"]].copy()
    x = x.rename(columns={"pos": "pos_anterior", "brecha_jov": "brecha_jov_anterior"})
    x["pos_mismo_tipo"] = s.xs(mismo).pos.reindex(x.index)
    x["crec_ln"] = x.LN / s.xs(mismo).LN.reindex(x.index) - 1
    x["log_ln"] = np.log(x.LN)
    x["escolaridad"] = CENSO.escolaridad.reindex(x.index)  # dato fijo de 2020; secciones posteriores quedan sin dato
    if t in s.index.get_level_values("anio"):
        x["y"] = s.xs(t).pos.reindex(x.index)
    return x


def modelos():
    prep_lin = ColumnTransformer([
        ("num", make_pipeline(SimpleImputer(strategy="median", add_indicator=True), StandardScaler()), NUM),
        ("cat", OneHotEncoder(handle_unknown="ignore"), CAT)])
    prep_rf = ColumnTransformer([("num", "passthrough", NUM), ("cat", OneHotEncoder(handle_unknown="ignore"), CAT)])
    return {
        "Regresión lineal": make_pipeline(prep_lin, LinearRegression()),
        "Random forest": make_pipeline(prep_rf, RandomForestRegressor(n_estimators=500, min_samples_leaf=5,
                                                                       random_state=42, n_jobs=-1)),
    }


def predecir(s, ciudad, ciudad_jov):
    """Valida, elige el modelo, lo reentrena y predice 2027. Devuelve (predicción, validación, modelo final)."""
    # --- Validación temporal: entrenar con la intermedia 2015, probar con la intermedia 2021 ---
    tr, te = filas(s, 2015).dropna(subset=["y"]), filas(s, 2021).dropna(subset=["y"])
    mismo = te.pos_mismo_tipo.fillna(te.pos_anterior).fillna(0)
    res = {"Línea base: igual que la elección anterior": mean_absolute_error(te.y, te.pos_anterior.fillna(0)),
           "Línea base: igual que la elección del mismo tipo": mean_absolute_error(te.y, mismo),
           "Línea base: promedio de ambas": mean_absolute_error(te.y, (mismo + te.pos_anterior.fillna(mismo)) / 2)}
    ajustados = {}
    for nombre, mod in modelos().items():
        mod.fit(tr[NUM + CAT], tr.y)
        res[nombre] = mean_absolute_error(te.y, mod.predict(te[NUM + CAT]))
        ajustados[nombre] = mod
    candidatos = {k: v for k, v in res.items() if k in ajustados}
    mejor = min(candidatos, key=candidatos.get)

    # --- Modelo final: entrenar con las intermedias 2015 y 2021, predecir 2027 ---
    todo = pd.concat([tr, te])
    final = modelos()[mejor].fit(todo[NUM + CAT], todo.y)
    x27 = filas(s, 2027)
    x27["pos_2027"] = final.predict(x27[NUM + CAT])
    nivel_2027 = ciudad[2021]
    nivel_jov_2027 = ciudad_jov[2021]
    p = pd.DataFrame(index=x27.index)
    p["part_2027"] = (nivel_2027 + x27.pos_2027).clip(0, 100)
    # Brecha de jóvenes: la de 2021 (intermedia) si existe; si no, la de 2024 ajustada por el cambio de la brecha de la ciudad
    ajuste = (nivel_jov_2027 - nivel_2027) - (ciudad_jov[2024] - ciudad[2024])
    brecha = (s.xs(2021).brecha_jov.reindex(p.index)
              .fillna(s.xs(2024).brecha_jov.reindex(p.index) + ajuste)
              .fillna(nivel_jov_2027 - nivel_2027))  # sin dato válido: brecha promedio de la ciudad
    p["part_jov_2027"] = (p.part_2027 + brecha).clip(0, 100)
    p["ln_2024"] = x27.LN
    p["ln_jov_2024"] = (x27.LN * x27.pct_jov / 100).round()
    p["pct_jov"] = x27.pct_jov
    p["tipo_seccion"] = x27.tipo_seccion
    hist = s.part.unstack("anio").reindex(p.index)
    for a in ANIOS:
        p[f"part_{a}"] = hist[a]
    p["anios_con_dato"] = hist[[2015, 2018, 2021, 2024]].notna().sum(axis=1)  # calidad sobre el panel 2015-2024
    p["calidad"] = np.select([p.anios_con_dato >= 3, p.anios_con_dato >= 1], ["completa", "parcial"], "sin historial")
    # Tendencia entre intermedias (para el semáforo): cambio de posición 2015 -> 2021
    p["tend_intermedia"] = (s.xs(2021).pos.reindex(p.index) - s.xs(2015).pos.reindex(p.index))
    p = p.round(2).reset_index()
    return p, {"res": res, "mejor": mejor, "tr": tr, "te": te}, final


def main():
    m = pd.read_csv(PROC / "leon_maestra.csv")
    s, ciudad, ciudad_jov = tasas(m)
    p, val, final = predecir(s, ciudad, ciudad_jov)
    res, mejor, tr, te = val["res"], val["mejor"], val["tr"], val["te"]
    nivel_2027, nivel_jov_2027 = ciudad[2021], ciudad_jov[2021]
    print("MAE validación (puntos de posición, prueba 2021):")
    for k, v in res.items():
        print(f"  {k}: {v:.2f}")
    print(f"Elegido: {mejor}")
    p.to_csv(PROC / "prediccion_2027.csv", index=False)

    imp = None
    if mejor == "Random forest":
        rf = final[-1]
        nombres = final[0].get_feature_names_out()
        imp = pd.Series(rf.feature_importances_, index=nombres).sort_values(ascending=False).round(3)

    lineas = ["# HINE-17 — Modelo de predicción de participación 2027", "",
              "Validación temporal sobre elecciones intermedias: se entrena prediciendo 2015 (con 2009 y 2012) y se prueba prediciendo 2021 (con 2015 y 2018).",
              f"Secciones en entrenamiento: {len(tr)} · en prueba: {len(te)}.", "",
              "| Modelo | MAE (puntos) |", "|---|---|"]
    lineas += [f"| {k} | {v:.2f} |" for k, v in res.items()]
    lineas += ["", f"**Elegido: {mejor}.**", "",
               f"Nivel de León supuesto para 2027 (participación capturada de la intermedia 2021): {nivel_2027:.1f} % "
               f"total, {nivel_jov_2027:.1f} % jóvenes 18-29.", "",
               f"Secciones con predicción: {len(p)} · calidad: {p.calidad.value_counts().to_dict()}.",
               f"Participación 2027 predicha — mediana {p.part_2027.median():.1f} %, rango {p.part_2027.min():.1f}–{p.part_2027.max():.1f} %.",
               f"Jóvenes 2027 predicha — mediana {p.part_jov_2027.median():.1f} %."]
    if imp is not None:
        lineas += ["", "Importancia de variables (random forest):", "", "| Variable | Importancia |", "|---|---|"]
        lineas += [f"| {k.split('__')[-1]} | {v} |" for k, v in imp.head(8).items()]
    (OUT / "metricas_modelo.md").write_text("\n".join(lineas) + "\n")
    print("\n".join(lineas[-14:]))


if __name__ == "__main__":
    main()
