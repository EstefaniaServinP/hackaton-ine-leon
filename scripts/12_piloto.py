"""Piloto con grupo de comparación: la misma intervención, aplicada a la mitad de los hogares al azar.

Uso: python scripts/12_piloto.py   (requiere 07_escenarios.py)
Resultado: outputs/piloto.md y la clave "piloto" en outputs/cifras_clave.json

Diseño: en las secciones rojas, el CAE ya visita el hogar de cada persona sorteada y lo registra en el
"Talón acuse de recibo de la carta-notificación" (INE, Guía CAE 2023-2024, pp. 107-108). Se agrega la
casilla "volante joven entregado" y el volante se deja solo en la mitad de esos hogares, elegidos al azar
(por ejemplo, por el último dígito del código de barras del talón). Después, el INE compara de forma
interna y anonimizada la participación de los jóvenes de 18 a 29 años de los hogares con y sin volante,
con los registros de marca de voto de los cuadernillos. Supuesto: el INE puede ubicar a los jóvenes de
cada hogar por el domicilio registrado en el padrón.

Se calcula el efecto mínimo detectable (significancia 5 % a dos colas, potencia 80 %) y cuántos jóvenes
harían falta para detectar los efectos de los escenarios.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
Z = 1.96 + 0.84
EFECTO_DISENO = 1.5  # supuesto: jóvenes de un mismo hogar se parecen entre sí


def main():
    e = pd.read_csv(RAIZ / "data" / "processed" / "escenarios_2027.csv")
    rojas = e[e.intervenida]
    jov = float((rojas.alcance_hogares * rojas.ln_jov_2024).sum())  # jóvenes en hogares de personas sorteadas
    p = float((rojas.part_jov_2027 * rojas.ln_jov_2024).sum() / rojas.ln_jov_2024.sum()) / 100
    var = p * (1 - p) * EFECTO_DISENO
    mde = Z * np.sqrt(var * 4 / jov) * 100  # mitad y mitad
    necesarios = {ef: int(np.ceil(4 * var * (Z / (ef / 100)) ** 2)) for ef in [0.5, 1.0]}
    veces_leon = {ef: n / jov for ef, n in necesarios.items()}

    md = ["# Piloto con grupo de comparación", "",
          f"Jóvenes en hogares de personas sorteadas de las {len(rojas)} secciones rojas de León: ~{int(jov):,} "
          f"(~{int(jov / 2):,} por grupo). Participación juvenil predicha: {p:.1%}.", "",
          f"**Efecto mínimo detectable en León: {mde:.1f} puntos** (significancia 5 %, potencia 80 %, efecto de "
          f"diseño por hogar {EFECTO_DISENO}).", "",
          "| Efecto a detectar | Jóvenes necesarios (ambos grupos) | Equivale a |",
          "|---|---|---|"]
    md += [f"| {ef} pts | {n:,} | {veces_leon[ef]:.0f} veces las secciones rojas de León |" for ef, n in necesarios.items()]
    md += ["", "Lectura: con los efectos esperados (0.2 a 1.0 puntos), León solo no alcanza para medirlos. "
           "El piloto debe aplicarse en las secciones rojas de varios municipios o de una o más entidades; "
           "el mismo código genera el semáforo para cualquier municipio."]
    (RAIZ / "outputs" / "piloto.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))

    ruta = RAIZ / "outputs" / "cifras_clave.json"
    cifras = json.loads(ruta.read_text())
    cifras["piloto"] = {"jovenes_leon": int(jov), "mde_leon_pts": round(mde, 1),
                        "jovenes_necesarios": {str(k): v for k, v in necesarios.items()},
                        "veces_leon": {str(k): round(v) for k, v in veces_leon.items()}}
    ruta.write_text(json.dumps(cifras, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
