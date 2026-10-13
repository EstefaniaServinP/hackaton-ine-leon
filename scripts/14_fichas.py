"""Fichas por sección: una hoja por cada sección roja de prioridad 1 (además está entre las 50 que más
se han quedado atrás), para que el INE las use en campo.

Uso: python scripts/14_fichas.py   (requiere 05_cartografia.py, 07_escenarios.py y 13_censo.py)
Resultado: outputs/fichas_prioridad1.pdf
"""
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
PROC = RAIZ / "data" / "processed"
SALIDA = RAIZ / "outputs" / "fichas_prioridad1.pdf"
ANIOS = [2015, 2018, 2021, 2024]
TIPO = {"U": "Urbana", "M": "Mixta", "R": "Rural"}
SUP, TXT, TXT2, REJ = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e0"
AZUL, NARANJA, GRIS, ROJO = "#2a78d6", "#eb6834", "#b5b4ae", "#d03b3b"
FUENTE = ("Fuente: elaboración propia con los Conteos Censales de Participación Ciudadana 2009–2024 y la Base Geográfica Digital (INE)\n"
          "y el Censo 2020 (INEGI). Participación capturada = votos / (votos + no votos).")


def historial(m):
    """Participación capturada total y juvenil por sección y año, y la de León."""
    m = m[m.anio.isin(ANIOS)]
    def tasa(g):
        return 100 * g.SV / (g.SV + g.NV)
    sec = m.groupby(["seccion", "anio"])[["SV", "NV"]].sum()
    jov = m[m.grupo_amplio == "18-29"].groupby(["seccion", "anio"])[["SV", "NV"]].sum()
    ciudad = m.groupby("anio")[["SV", "NV"]].sum()
    ciudad_j = m[m.grupo_amplio == "18-29"].groupby("anio")[["SV", "NV"]].sum()
    return tasa(sec).unstack(), tasa(jov).unstack(), tasa(ciudad), tasa(ciudad_j)


def dato(ax, y, etiqueta, valor):
    ax.text(0, y, etiqueta, fontsize=10, color=TXT2, transform=ax.transAxes)
    ax.text(1, y, valor, fontsize=11, color=TXT, ha="right", fontweight="bold", transform=ax.transAxes)


def ficha(pdf, r, geo, h_tot, h_jov, c_tot, c_jov):
    fig = plt.figure(figsize=(11, 8.5), dpi=150, facecolor=SUP)
    fig.text(0.05, 0.93, f"Sección {r.seccion}", fontsize=24, fontweight="bold", color=TXT)
    fig.text(0.05, 0.895, f"{TIPO.get(r.tipo_seccion, r.tipo_seccion)} · Distrito federal {int(r.distrito_federal):02d} · "
             f"Riesgo alto · Prioridad 1 (entre las 50 que más se han quedado atrás)", fontsize=12, color=TXT2)

    # Datos clave
    ax = fig.add_axes([0.05, 0.38, 0.38, 0.46]); ax.axis("off")
    filas = [
        ("Jóvenes de 18 a 29 en lista nominal (2024)", f"{int(r.ln_jov_2024):,}"),
        ("Jóvenes que votarían en 2027 (estimación)", f"{r.part_jov_2027:.0f} %"),
        ("Votaron en 2024: mujeres jóvenes", f"{r.part_jov_mujeres_2024:.0f} %"),
        ("Votaron en 2024: hombres jóvenes", f"{r.part_jov_hombres_2024:.0f} %"),
        ("Años de escolaridad promedio (2020)", "—" if pd.isna(r.escolaridad) else f"{r.escolaridad:.1f}"),
        ("Viviendas con internet (2020)", "—" if pd.isna(r.pct_internet) else f"{r.pct_internet:.0f} %"),
        ("Votarán por primera vez en 2027 (aprox.)", "—" if pd.isna(r.primer_voto) else f"{int(r.primer_voto):,}"),
        ("Volantes estimados (hogares visitados)", f"{int(r.volantes):,}"),
        ("Calidad del dato", "Poco confiable: menos de 100 jóvenes" if r.pocos_jovenes else str(r.calidad).capitalize()),
    ]
    for i, (k, v) in enumerate(filas):
        y = 0.95 - i * 0.107
        dato(ax, y, k, v)
        ax.plot([0, 1], [y - 0.035] * 2, color=REJ, linewidth=1, transform=ax.transAxes)

    # Historial frente a León
    ax2 = fig.add_axes([0.52, 0.42, 0.43, 0.40], facecolor=SUP)
    for serie, color, nombre, ancho in [(h_jov.loc[r.seccion], AZUL, "Jóvenes de la sección", 2.5),
                                        (c_jov, GRIS, "Jóvenes de León", 2), (h_tot.loc[r.seccion], NARANJA, "Total de la sección", 2)]:
        s = serie.reindex(ANIOS)
        ax2.plot(ANIOS, s.values, color=color, linewidth=ancho, marker="o", markersize=6, markeredgecolor=SUP,
                 markeredgewidth=1.5, label=nombre)
    ax2.set_xticks(ANIOS); ax2.set_ylim(0, 90)
    ax2.set_yticks(range(0, 91, 20), [f"{v}%" for v in range(0, 91, 20)])
    for lado in ["top", "right", "left"]:
        ax2.spines[lado].set_visible(False)
    ax2.spines["bottom"].set_color(REJ); ax2.tick_params(colors=TXT2, length=0)
    ax2.grid(axis="y", color=REJ, linewidth=1); ax2.set_axisbelow(True)
    ax2.set_title("Participación 2015–2024 (2015 y 2021 son intermedias)", loc="left", fontsize=11, color=TXT)
    ax2.legend(frameon=False, fontsize=9, loc="lower left", ncol=3, labelcolor=TXT)

    # Ubicación
    ax3 = fig.add_axes([0.05, 0.07, 0.38, 0.28]); ax3.set_axis_off()
    geo.plot(ax=ax3, color="#e9e8e3", edgecolor=SUP, linewidth=0.2)
    propia = geo[geo.seccion == r.seccion]
    if len(propia):
        propia.plot(ax=ax3, color=ROJO, edgecolor=TXT, linewidth=0.8)
    else:
        ax3.text(0.5, 0.5, "La sección no aparece en la cartografía\nde 2025: se dividió o cambió de límites.",
                 ha="center", va="center", fontsize=10, color=TXT, transform=ax3.transAxes,
                 bbox={"facecolor": SUP, "edgecolor": REJ})
    ax3.set_title("Ubicación en León", loc="left", fontsize=11, color=TXT)

    fig.text(0.52, 0.28, "Qué hacer", fontsize=13, fontweight="bold", color=TXT)
    fig.text(0.52, 0.08, "• Volante joven en cada hogar de persona sorteada\n   que el CAE visite (votar y actualizar credencial).\n"
             "• Registrar en el talón si se entregó el volante (piloto).\n"
             "• Si hay preparatoria o universidad cerca: módulo de\n   credencial con SMS voluntario y plática de SE.\n"
             "• Invitar a jóvenes interesados a un simulacro\n   de la segunda etapa.",
             fontsize=10.5, color=TXT, linespacing=1.6)
    fig.text(0.05, 0.025, FUENTE, fontsize=7.5, color=TXT2)
    pdf.savefig(fig, facecolor=SUP)
    plt.close(fig)


def main():
    e = pd.read_csv(PROC / "escenarios_2027.csv")
    censo = pd.read_csv(PROC / "censo_secciones.csv")[["seccion", "escolaridad", "pct_internet"]]
    e = e.merge(censo, on="seccion", how="left")
    m = pd.read_csv(PROC / "leon_maestra.csv")
    df = m[m.anio == 2024].groupby("seccion").distrito_federal.first().rename("distrito_federal")
    e = e.merge(df, on="seccion", how="left")
    p1 = e[e.prioridad == 1].sort_values("part_jov_2027")
    geo = gpd.read_file(PROC / "leon_secciones.geojson")[["seccion", "geometry"]]
    h_tot, h_jov, c_tot, c_jov = historial(m)

    with PdfPages(SALIDA) as pdf:
        fig = plt.figure(figsize=(11, 8.5), dpi=150, facecolor=SUP)
        fig.text(0.07, 0.75, "Fichas de secciones de prioridad 1", fontsize=28, fontweight="bold", color=TXT)
        fig.text(0.07, 0.68, "Mapa de Alerta de Abstención en León · Semáforo 2027", fontsize=15, color=TXT2)
        fig.text(0.07, 0.50, f"{len(p1)} secciones en riesgo alto que además están entre las 50 que más se han quedado\n"
                 "atrás del promedio de León. Ordenadas de menor a mayor participación juvenil esperada.\n\n"
                 "Cada ficha resume la sección, su historial frente a León y qué hacer en campo.",
                 fontsize=12, color=TXT, linespacing=1.6)
        fig.text(0.07, 0.08, FUENTE, fontsize=8, color=TXT2)
        pdf.savefig(fig, facecolor=SUP); plt.close(fig)
        for r in p1.itertuples():
            ficha(pdf, r, geo, h_tot, h_jov, c_tot, c_jov)
    print(f"{len(p1)} fichas -> {SALIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
