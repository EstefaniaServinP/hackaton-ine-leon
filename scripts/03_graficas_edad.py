"""HINE-12: participación por edad y sexo en León, 2009-2024.

Uso: python scripts/03_graficas_edad.py   (requiere data/processed/leon_maestra.csv)
Resultado:
  outputs/fig_edad_leon.png         líneas 18-29 / 30-59 / 60+ por elección
  outputs/fig_edad_quinquenal.png   mapa de calor grupo quinquenal x elección
  outputs/tabla_brechas.csv         participación y brecha (60+ menos 18-29) por año y sexo
  outputs/tabla_quinquenal.csv      participación por grupo quinquenal y año
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
OUT = RAIZ / "outputs"

# Paleta categórica validada (dataviz, modo claro) y tokens de texto/superficie
SUPERFICIE = "#fcfcfb"
TEXTO = "#0b0b0b"
TEXTO_2 = "#52514e"
REJILLA = "#e6e5e0"
SOMBRA_INTERMEDIA = "#f0efec"
COLORES = {"18-29": "#2a78d6", "30-59": "#eb6834", "60+": "#1baf7a"}
NOMBRES = {"18-29": "Jóvenes 18-29", "30-59": "Adultos 30-59", "60+": "Mayores 60+"}
AZULES = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
ANIOS = [2009, 2012, 2015, 2018, 2021, 2024]
INTERMEDIAS = [2009, 2015, 2021]
FUENTE = "Fuente: INE, Conteos Censales de Participación Ciudadana 2009–2024. Participación = votos / lista nominal."


def tasa(df, por):
    g = df.groupby(por, observed=True)[["SV", "LN"]].sum()
    return (100 * g.SV / g.LN).round(1)


def estilo(ax):
    ax.set_facecolor(SUPERFICIE)
    for lado in ["top", "right", "left"]:
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color(REJILLA)
    ax.tick_params(colors=TEXTO_2, length=0, labelsize=10)
    ax.grid(axis="y", color=REJILLA, linewidth=1, linestyle="-")
    ax.set_axisbelow(True)


def grafica_lineas(t):
    fig, ax = plt.subplots(figsize=(10, 5.6), dpi=200, facecolor=SUPERFICIE)
    estilo(ax)
    for a in INTERMEDIAS:
        ax.axvspan(a - 1.2, a + 1.2, color=SOMBRA_INTERMEDIA, zorder=0, linewidth=0)
        ax.text(a, 87, "Intermedia", ha="center", va="top", fontsize=8.5, color=TEXTO_2)
    for grupo, color in COLORES.items():
        y = t.loc[grupo]
        ax.plot(ANIOS, y, color=color, linewidth=2, solid_capstyle="round", solid_joinstyle="round",
                marker="o", markersize=7, markeredgecolor=SUPERFICIE, markeredgewidth=2, label=NOMBRES[grupo])
        ax.annotate(f"{NOMBRES[grupo]}  {y[2024]:.1f}%", (2024, y[2024]), xytext=(10, 0),
                    textcoords="offset points", va="center", fontsize=10, color=TEXTO)
    ax.set_xticks(ANIOS)
    ax.set_xlim(2007.5, 2029.5)
    ax.set_ylim(0, 88)
    ax.set_yticks(range(0, 81, 20))
    ax.set_yticklabels([f"{v}%" for v in range(0, 81, 20)])
    ax.legend(loc="lower left", frameon=False, fontsize=9.5, labelcolor=TEXTO, ncol=3)
    brecha = t.loc["60+", 2024] - t.loc["18-29", 2024]
    fig.suptitle("En León, los jóvenes votan mucho menos que los mayores", x=0.06, ha="left",
                 fontsize=15, fontweight="bold", color=TEXTO)
    ax.set_title(f"Participación por grupo de edad, León, Gto. — brecha de {brecha:.0f} puntos en 2024",
                 loc="left", fontsize=10.5, color=TEXTO_2, pad=12)
    fig.text(0.06, 0.015, FUENTE, fontsize=8, color=TEXTO_2)
    fig.subplots_adjust(left=0.06, right=0.97, top=0.85, bottom=0.11)
    fig.savefig(OUT / "fig_edad_leon.png", facecolor=SUPERFICIE)
    plt.close(fig)


def grafica_calor(q):
    fig, ax = plt.subplots(figsize=(8, 7.5), dpi=200, facecolor=SUPERFICIE)
    cmap = LinearSegmentedColormap.from_list("azul", AZULES)
    im = ax.imshow(q.values, cmap=cmap, aspect="auto", vmin=20, vmax=85)
    ax.set_xticks(range(len(q.columns)), [str(c) + ("\nintermedia" if c in INTERMEDIAS else "") for c in q.columns])
    ax.set_yticks(range(len(q.index)), q.index)
    for i in range(q.shape[0]):
        for j in range(q.shape[1]):
            v = q.values[i, j]
            ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=8.5,
                    color="white" if v >= 55 else TEXTO)
    ax.tick_params(colors=TEXTO_2, length=0, labelsize=9.5)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xticks([x - 0.5 for x in range(1, len(q.columns))], minor=True)
    ax.set_yticks([y - 0.5 for y in range(1, len(q.index))], minor=True)
    ax.grid(which="minor", color=SUPERFICIE, linewidth=2)
    ax.tick_params(which="minor", length=0)
    ax.set_ylabel("Edad", color=TEXTO_2)
    cb = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.03)
    cb.outline.set_visible(False)
    cb.ax.tick_params(colors=TEXTO_2, labelsize=8.5, length=0)
    cb.set_label("Participación (%)", color=TEXTO_2)
    fig.suptitle("Votan menos los de 20 a 34 años; más, los de 60 a 74", x=0.04, ha="left",
                 fontsize=14, fontweight="bold", color=TEXTO)
    ax.set_title("Participación (%) por grupo de edad quinquenal, León, Gto.", loc="left",
                 fontsize=10, color=TEXTO_2, pad=10)
    fig.text(0.04, 0.012, FUENTE, fontsize=7, color=TEXTO_2)
    fig.subplots_adjust(left=0.1, right=0.95, top=0.88, bottom=0.1)
    fig.savefig(OUT / "fig_edad_quinquenal.png", facecolor=SUPERFICIE)
    plt.close(fig)


def main():
    d = pd.read_csv(RAIZ / "data" / "processed" / "leon_maestra.csv")
    t = tasa(d, ["grupo_amplio", "anio"]).unstack()
    q = tasa(d, ["grupo_edad", "anio"]).unstack()

    # Tabla de brechas: total y por sexo (No binario se excluye por tamaño de muestra)
    filas = []
    for sexo, sub in [("Total", d)] + [(s, d[d.sexo == s]) for s in ["Mujer", "Hombre"]]:
        ts = tasa(sub, ["grupo_amplio", "anio"]).unstack()
        for a in ANIOS:
            filas.append({"anio": a, "sexo": sexo, "tipo_eleccion": "Intermedia" if a in INTERMEDIAS else "Presidencial",
                          "p_18_29": ts.loc["18-29", a], "p_30_59": ts.loc["30-59", a], "p_60_mas": ts.loc["60+", a],
                          "brecha_60_vs_18_29": round(ts.loc["60+", a] - ts.loc["18-29", a], 1)})
    brechas = pd.DataFrame(filas)
    brechas.to_csv(OUT / "tabla_brechas.csv", index=False)
    q.to_csv(OUT / "tabla_quinquenal.csv")

    assert t.loc["18-29", 2024] == 47.9 and t.loc["60+", 2024] == 73.0
    grafica_lineas(t)
    grafica_calor(q)
    print(brechas.to_string(index=False))


if __name__ == "__main__":
    main()
