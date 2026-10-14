"""Anexo metodológico: coeficientes del modelo, sensibilidad al umbral de cuadernillos sin capturar,
abstención aparente por padrón desactualizado y costos.

Uso: python scripts/15_anexo.py   (requiere 06_modelo.py, 07_escenarios.py, 11_robustez.py y 13_censo.py)
Resultado: outputs/anexo.md y claves "anexo" en outputs/cifras_clave.json

1. Coeficientes estandarizados de la regresión lineal final (entrenada con 2015 y 2021).
2. Umbral de cuadernillos sin capturar (NS / LN): se repite todo el modelo con 10 %, 20 %, 30 % y sin descartar,
   y se compara el error de validación y las secciones rojas con las del umbral base (20 %).
3. Abstención aparente: el INE no localizó al 21.6 % de la ciudadanía sorteada en Guanajuato; la razón principal
   en el país fue el cambio de domicilio (45.6 %) y la segunda, residir en el extranjero (12.2 %)
   (INE, informe primera etapa 2023-2024, pp. 73-74). Esas personas siguen en la lista nominal y cuentan como
   "no votó". Se mide:
     a) inscritos por habitante: lista nominal 2021 / población total del Censo 2020, por color del semáforo;
     b) cuántas secciones siguen rojas si una parte de sus jóvenes inscritos ya no vive ahí.
4. Costos: rubros y supuestos explícitos.
"""
import importlib.util
import json
from pathlib import Path

import config
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
PROC = config.PROC
OUT = config.OUT


def cargar(nombre):
    spec = importlib.util.spec_from_file_location(nombre, RAIZ / "scripts" / f"{nombre}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


modelo = cargar("06_modelo")
escen = cargar("07_escenarios")

NOMBRES = {"pos_mismo_tipo": "Posición en la intermedia anterior", "pos_anterior": "Posición en la elección anterior",
           "brecha_jov_anterior": "Brecha de jóvenes en la elección anterior", "pct_jov": "% de jóvenes en la lista",
           "pct_60": "% de 60 y más en la lista", "pct_muj": "% de mujeres en la lista",
           "log_ln": "Tamaño de la lista (logaritmo)", "crec_ln": "Crecimiento de la lista en 6 años",
           "escolaridad": "Años de escolaridad (Censo 2020)"}
AUSENTES = [0.05, 0.10, 0.20]  # parte de los jóvenes inscritos que ya no vive en la sección
COSTO_VOLANTE = (1.0, 2.0)  # pesos por volante impreso (supuesto)
MIN_EXTRA = 1  # minutos extra por visita para entregar el volante y marcar el talón (supuesto)


def coeficientes(final):
    nombres = final[0].get_feature_names_out()
    c = pd.Series(final[-1].coef_, index=[x.split("__")[-1] for x in nombres])
    c = c[[k for k in NOMBRES]].rename(NOMBRES)
    return c.reindex(c.abs().sort_values(ascending=False).index)


def umbral_ns(m, base):
    rojas_base = set(base[base.part_jov_2027 < escen.CORTE_ROJO].seccion)
    sin_dato = int(modelo.tasas(m, max_ns=1.0)[0].part.isna().sum())  # faltan por otras causas (sin votos capturados)
    filas = []
    for u in [0.10, 0.20, 0.30, 1.0]:
        s, ciudad, ciudad_jov = modelo.tasas(m, max_ns=u)
        p, val, _ = modelo.predecir(s, ciudad, ciudad_jov)
        rojas = set(p[p.part_jov_2027 < escen.CORTE_ROJO].seccion)
        filas.append({"umbral": "Sin descartar" if u == 1.0 else f"{u:.0%}",
                      "anios_descartados": int(s.part.isna().sum()) - sin_dato,
                      "error_validacion": round(val["res"]["Regresión lineal"], 2),
                      "rojas": len(rojas), "en_comun": len(rojas & rojas_base)})
    return pd.DataFrame(filas)


def padron(m, e):
    censo = pd.read_csv(PROC / "censo_secciones.csv").set_index("seccion")
    ln21 = m[m.anio == 2021].groupby("seccion").LN.sum()
    e = e.set_index("seccion")
    e["inscritos_por_habitante"] = (ln21 / censo.poblacion).reindex(e.index)
    por_color = e.groupby("semaforo_A").inscritos_por_habitante.median().round(2).to_dict()
    mas_que_habitantes = e[e.inscritos_por_habitante > 1]
    ausentes = []
    for x in AUSENTES:
        # Si una parte x de los jóvenes inscritos ya no vive ahí, la participación de los que sí viven es part / (1 - x)
        ajustada = (e.part_jov_2027 / (1 - x)).clip(upper=100)
        ausentes.append({"ausentes": f"{x:.0%}", "rojas": int((ajustada < escen.CORTE_ROJO).sum())})
    return {"razon_leon": round(float(ln21.reindex(e.index).sum() / censo.poblacion.reindex(e.index).sum()), 2),
            "mediana_por_color": por_color, "mas_inscritos_que_habitantes": len(mas_que_habitantes),
            "de_esas_rojas": int((mas_que_habitantes.semaforo_A == "rojo").sum()),
            "corr_part_jov": round(float(e.inscritos_por_habitante.corr(e.part_jov_2027)), 2),
            "ausentes": ausentes}


def main():
    m = pd.read_csv(config.MAESTRA)
    e = pd.read_csv(PROC / "escenarios_2027.csv")
    cifras = json.loads((OUT / "cifras_clave.json").read_text())

    s, ciudad, ciudad_jov = modelo.tasas(m)
    _, val, final = modelo.predecir(s, ciudad, ciudad_jov)
    coef = coeficientes(final)
    ns = umbral_ns(m, e)
    pad = padron(m, e)
    volantes = cifras["volantes"]
    costo = {"impresion": [round(volantes * c) for c in COSTO_VOLANTE],
             "horas_cae": round(volantes * MIN_EXTRA / 60)}

    md = ["# Anexo metodológico", "",
          "## 1. Coeficientes del modelo final (variables estandarizadas)", "",
          "Puntos de posición que cambia la predicción cuando la variable sube una desviación estándar.", "",
          coef.round(2).rename("Coeficiente").to_markdown(), "",
          "## 2. Umbral de cuadernillos sin capturar", "", ns.to_markdown(index=False), "",
          "Años descartados = sección-año con NS por encima del umbral. El error de validación no es del todo comparable "
          "entre filas porque cambia qué secciones entran a la prueba.", "",
          "## 3. Abstención aparente por padrón desactualizado", "",
          f"Inscritos por habitante en {config.NOMBRE} (LN 2021 / población 2020): {pad['razon_leon']}. Mediana por color: "
          f"{pad['mediana_por_color']}. Secciones con más inscritos que habitantes: {pad['mas_inscritos_que_habitantes']} "
          f"(rojas: {pad['de_esas_rojas']}). Correlación con la participación juvenil esperada: {pad['corr_part_jov']}.", "",
          pd.DataFrame(pad["ausentes"]).to_markdown(index=False), "",
          "## 4. Costos", "",
          f"Impresión de {volantes:,} volantes: ${costo['impresion'][0]:,} a ${costo['impresion'][1]:,} pesos. "
          f"Tiempo de CAE: unas {costo['horas_cae']:,} horas en total ({MIN_EXTRA} minuto por visita)."]
    (OUT / "anexo.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))

    cifras["anexo"] = {"coeficientes": coef.round(2).to_dict(),
                       "umbral_ns": ns.to_dict(orient="records"), "padron": pad, "costo": costo,
                       "n_entrenamiento": len(val["tr"]) + len(val["te"])}
    (OUT / "cifras_clave.json").write_text(json.dumps(cifras, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
