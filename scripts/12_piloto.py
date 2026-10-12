"""Diseño del piloto con grupo de comparación: ¿qué efecto se podría detectar?

Uso: python scripts/12_piloto.py   (requiere 02_limpieza.py y 07_escenarios.py)
Resultado: outputs/piloto.md

Tres diseños, con significancia de 5 % (dos colas) y potencia de 80 %:
  A. Por sección: las secciones rojas se reparten al azar entre brigada y comparación; el resultado es
     la participación juvenil de cada sección (Conteos Censales). La variación entre secciones se toma
     del cambio 2015 -> 2021, ajustado por la participación juvenil de 2015.
  B. Por persona: dentro de las secciones rojas, el volante se entrega en hogares elegidos al azar y el
     INE compara, con los registros de marca de voto de los cuadernillos (la base de los Conteos
     Censales), la participación de jóvenes de hogares con y sin volante. Se aplica un efecto de diseño
     por agrupamiento en hogares.
  C. Con el talón (recomendado): el CAE ya registra cada visita a la ciudadanía sorteada en el
     "Talón acuse de recibo de la carta-notificación" (INE, Guía para la y el CAE 2023-2024,
     pp. 107-108). Se agrega la casilla "volante joven entregado" y el volante se entrega a la mitad de
     las personas sorteadas, elegidas al azar; se compara la participación de los jóvenes sorteados de
     cada grupo con su clave de elector. El sorteo selecciona al 13 % de la lista nominal (Guía, p. 16).
"""
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
Z = 1.96 + 0.84          # significancia 5 % (dos colas) y potencia 80 %
EFECTO_DISENO = 1.5      # supuesto: agrupamiento de jóvenes en un mismo hogar
SORTEO = 0.13            # primera insaculación: 13 % de la lista nominal


def cargar(nombre):
    spec = importlib.util.spec_from_file_location(nombre, RAIZ / "scripts" / f"{nombre}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    modelo = cargar("06_modelo")
    s, _, _ = modelo.tasas(pd.read_csv(RAIZ / "data" / "processed" / "leon_maestra.csv"))
    x = pd.concat([s.xs(2015).part_jov, s.xs(2021).part_jov], axis=1, keys=["a", "b"]).dropna()
    pend = np.polyfit(x.a, x.b, 1)
    sd = float((x.b - np.polyval(pend, x.a)).std())

    e = pd.read_csv(RAIZ / "data" / "processed" / "escenarios_2027.csv")
    rojas = e[e.semaforo_A == "rojo"]
    n_secc = len(rojas)
    jov = float(rojas.ln_jov_2024.sum())
    p = float((rojas.part_jov_2027 * rojas.ln_jov_2024).sum() / jov) / 100

    filas = []
    for n in [50, 100, n_secc // 2]:
        filas.append({"diseño": f"A. Por sección ({n} vs {n})", "efecto_minimo_pts": round(Z * sd * np.sqrt(2 / n), 2)})
    for frac in [0.5]:
        n = jov * frac
        mde = Z * np.sqrt(p * (1 - p) * EFECTO_DISENO * (1 / n + 1 / (jov - n))) * 100
        filas.append({"diseño": f"B. Por persona (hogares al azar, {int(n):,} vs {int(jov - n):,} jóvenes)",
                      "efecto_minimo_pts": round(mde, 2)})
    n = jov * SORTEO / 2
    filas.append({"diseño": f"C. Con el talón (sorteados al azar, {int(n):,} vs {int(n):,} jóvenes)",
                  "efecto_minimo_pts": round(Z * np.sqrt(p * (1 - p) * 2 / n) * 100, 2)})
    t = pd.DataFrame(filas)

    md = ["# Diseño del piloto con grupo de comparación", "",
          f"Secciones rojas: {n_secc}; jóvenes en ellas: {int(jov):,}; participación juvenil predicha: {p:.1%}.",
          f"Variación entre secciones (cambio 2015→2021 ajustado por 2015): {sd:.2f} pts.", "",
          t.to_markdown(index=False), "",
          "Significancia 5 % (dos colas), potencia 80 %. Efecto de diseño por hogar en B: "
          f"{EFECTO_DISENO} (supuesto).", "",
          "Lectura: medido por sección, el piloto solo distingue efectos de la magnitud del escenario medio "
          "o mayores. Con el talón (C), sin tareas nuevas para el CAE salvo una casilla, distingue efectos de "
          "~1.7 puntos entre jóvenes contactados, por debajo de lo que reporta la literatura (2.5 a 4.3)."]
    (RAIZ / "outputs" / "piloto.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
