"""Figura estática del semáforo 2027 (sin vs. con intervención, escenario medio) para el reporte.

Uso: python scripts/10_figura_mapa.py   (requiere 05_cartografia.py y 07_escenarios.py)
Resultado: outputs/fig_mapa_escenarios.png
"""
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
PROC = RAIZ / "data" / "processed"
OUT = RAIZ / "outputs"
SUPERFICIE, TEXTO, TEXTO_2 = "#fcfcfb", "#0b0b0b", "#52514e"
COLOR = {"rojo": "#d03b3b", "amarillo": "#fab219", "verde": "#0ca30c"}
ETIQUETA = {"rojo": "Riesgo alto", "amarillo": "Riesgo medio", "verde": "Riesgo bajo"}
SIN_DATOS = "#d6d5d0"


def main():
    g = gpd.read_file(PROC / "leon_secciones.geojson")[["seccion", "geometry"]]
    e = pd.read_csv(PROC / "escenarios_2027.csv")
    g = g.merge(e[["seccion", "tipo_seccion", "semaforo_A", "semaforo_B_medio"]], on="seccion", how="left").to_crs(32614)
    top50 = set(pd.read_csv(OUT / "top50_caida.csv").seccion)
    urb = g[g.tipo_seccion == "U"].total_bounds
    pad = 1500

    fig, axes = plt.subplots(1, 2, figsize=(12, 6.6), dpi=200, facecolor=SUPERFICIE)
    for ax, col, titulo in [(axes[0], "semaforo_A", "A · Sin intervención"),
                            (axes[1], "semaforo_B_medio", "B · Con Brigada CAE–SE Joven (escenario medio)")]:
        colores = g[col].map(COLOR).fillna(SIN_DATOS)
        g.plot(ax=ax, color=colores, edgecolor=SUPERFICIE, linewidth=0.25)
        g[g.seccion.isin(top50)].boundary.plot(ax=ax, color=TEXTO, linewidth=0.9)
        ax.set_xlim(urb[0] - pad, urb[2] + pad)
        ax.set_ylim(urb[1] - pad, urb[3] + pad)
        ax.set_axis_off()
        rojas = int((e[col] == "rojo").sum())
        ax.set_title(f"{titulo}\n{rojas} secciones en riesgo alto", loc="left", fontsize=11, color=TEXTO)
    leyenda = [Patch(facecolor=COLOR[k], label=ETIQUETA[k]) for k in COLOR] + \
              [Patch(facecolor=SIN_DATOS, label="Sin datos"), Patch(facecolor="none", edgecolor=TEXTO, label="Top 50 de mayor caída")]
    fig.legend(handles=leyenda, loc="lower center", bbox_to_anchor=(0.5, 0.025), ncol=5, frameon=False, fontsize=9.5, labelcolor=TEXTO)
    fig.suptitle("Semáforo de riesgo de abstención juvenil 2027, zona urbana de León", x=0.03, ha="left",
                 fontsize=14, fontweight="bold", color=TEXTO)
    fig.text(0.03, 0.005, "Riesgo según participación predicha de jóvenes 18–29: alto < 30 %, medio 30–40 %, bajo ≥ 40 %. "
             "Fuente: INE, Conteos Censales 2009–2024 y Base Geográfica Digital.", fontsize=7.5, color=TEXTO_2)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.86, bottom=0.08, wspace=0.04)
    fig.savefig(OUT / "fig_mapa_escenarios.png", facecolor=SUPERFICIE)
    plt.close(fig)


if __name__ == "__main__":
    main()
