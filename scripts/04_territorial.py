"""HINE-13 y HINE-14: comparación territorial y las 50 secciones con mayor caída.

Uso: python scripts/04_territorial.py   (requiere 01_descarga.py y 02_limpieza.py)
Resultado:
  outputs/tabla_leon_vs_gto.csv    participación León vs. resto de Guanajuato por año
  outputs/tabla_tiposec.csv        participación de León por tipo de sección y año
  outputs/fig_tiposec.png          ambas comparaciones
  outputs/caida_secciones.csv      métrica de caída para todas las secciones del panel
  outputs/top50_caida.csv          las 50 secciones que más se quedan atrás

Métrica de caída (ver outputs/notas_caida.md):
  participación capturada = SV / (SV + NV)   (excluye registros no especificados, NS)
  posición relativa       = participación de la sección - participación de León ese año
  caída                   = promedio de [pos 2021 - pos 2015] y [pos 2024 - pos 2018]
  Un año con NS > 20% de la lista nominal no se usa para esa sección.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
RAW = RAIZ / "data" / "raw"
OUT = RAIZ / "outputs"
ANIOS = [2009, 2012, 2015, 2018, 2021, 2024]
INTERMEDIAS = [2009, 2015, 2021]
PARES = [(2015, 2021), (2018, 2024)]  # mismo tipo de elección
MAX_NS = 0.20

SUPERFICIE, TEXTO, TEXTO_2, REJILLA, SOMBRA = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e0", "#f0efec"
FUENTE = "Fuente: INE, Conteos Censales de Participación Ciudadana 2009–2024. Participación = votos / lista nominal."


def pct(sv, ln):
    return (100 * sv / ln).round(1)


def comparacion_estatal():
    filas = []
    for a in ANIOS:
        d = pd.read_csv(RAW / f"gto_{a}.csv", encoding="utf-8-sig", usecols=["MPIOCVE", "LN", "SV"])
        leon = d[d.MPIOCVE == 20].sum()
        resto = d[d.MPIOCVE != 20].sum()
        filas.append({"anio": a, "leon": pct(leon.SV, leon.LN), "resto_gto": pct(resto.SV, resto.LN),
                      "gto_total": pct(d.SV.sum(), d.LN.sum())})
    t = pd.DataFrame(filas)
    t["dif_leon_vs_resto"] = (t.leon - t.resto_gto).round(1)
    return t


def por_tipo_seccion(m):
    g = m.groupby(["anio", "tipo_seccion"])[["SV", "LN"]].sum()
    t = pct(g.SV, g.LN).unstack()
    t["secciones_U"] = m[m.tipo_seccion == "U"].groupby("anio").seccion.nunique()
    t["secciones_M"] = m[m.tipo_seccion == "M"].groupby("anio").seccion.nunique()
    t["secciones_R"] = m[m.tipo_seccion == "R"].groupby("anio").seccion.nunique()
    return t


def linea(ax, x, y, color, etiqueta, dy=0):
    ax.plot(x, y, color=color, linewidth=2, marker="o", markersize=7, markeredgecolor=SUPERFICIE,
            markeredgewidth=2, solid_capstyle="round", label=etiqueta)
    ax.annotate(f"{etiqueta}  {y.iloc[-1]:.1f}%", (x.iloc[-1], y.iloc[-1]), xytext=(9, dy),
                textcoords="offset points", va="center", fontsize=9, color=TEXTO)


def grafica(est, tipo):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.2), dpi=200, facecolor=SUPERFICIE, sharey=True)
    for ax in axes:
        ax.set_facecolor(SUPERFICIE)
        for a in INTERMEDIAS:
            ax.axvspan(a - 1.2, a + 1.2, color=SOMBRA, zorder=0, linewidth=0)
        for lado in ["top", "right", "left"]:
            ax.spines[lado].set_visible(False)
        ax.spines["bottom"].set_color(REJILLA)
        ax.tick_params(colors=TEXTO_2, length=0, labelsize=9.5)
        ax.grid(axis="y", color=REJILLA, linewidth=1)
        ax.set_axisbelow(True)
        ax.set_xticks(ANIOS)
        ax.set_xlim(2007.5, 2031)
        ax.set_ylim(0, 75)
        ax.set_yticks(range(0, 71, 20), [f"{v}%" for v in range(0, 71, 20)])
    linea(axes[0], est.anio, est.leon, "#2a78d6", "León")
    linea(axes[0], est.anio, est.resto_gto, "#eb6834", "Resto de Gto.")
    axes[0].set_title("León vs. resto de Guanajuato", loc="left", fontsize=11, color=TEXTO)
    colores = {"U": ("#2a78d6", "Urbana", 0), "M": ("#eb6834", "Mixta", 7), "R": ("#1baf7a", "Rural", -7)}
    for k, (c, nombre, dy) in colores.items():
        if k in tipo:
            s = tipo[k].dropna()
            linea(axes[1], pd.Series(s.index), s.reset_index(drop=True), c, nombre, dy)
    axes[1].set_title("León por tipo de sección", loc="left", fontsize=11, color=TEXTO)
    for ax in axes:
        ax.legend(loc="lower left", frameon=False, fontsize=9, labelcolor=TEXTO, ncol=3)
        ax.text(2015, 73, "Intermedias sombreadas", ha="center", fontsize=8, color=TEXTO_2) if ax is axes[0] else None
    fig.suptitle("León vota más que el resto del estado (salvo en 2015); lo rural y mixto, menos", x=0.04, ha="left",
                 fontsize=14, fontweight="bold", color=TEXTO)
    fig.text(0.04, 0.015, FUENTE, fontsize=7.5, color=TEXTO_2)
    fig.subplots_adjust(left=0.05, right=0.97, top=0.84, bottom=0.11, wspace=0.12)
    fig.savefig(OUT / "fig_tiposec.png", facecolor=SUPERFICIE)
    plt.close(fig)


def caida(m):
    p = m[m.en_panel_2015_2024 & m.anio.isin([2015, 2018, 2021, 2024])]
    s = p.groupby(["anio", "seccion"])[["LN", "SV", "NV", "NS"]].sum()
    s["part_capturada"] = 100 * s.SV / (s.SV + s.NV)
    s.loc[s.NS / s.LN > MAX_NS, "part_capturada"] = float("nan")
    ciudad = p.groupby("anio")[["SV", "NV"]].sum()
    ciudad = 100 * ciudad.SV / (ciudad.SV + ciudad.NV)
    s["posicion"] = s.part_capturada - s.index.get_level_values("anio").map(ciudad)
    pos = s.posicion.unstack("anio")
    part = s.part_capturada.unstack("anio")
    r = pd.DataFrame({f"part_{a}": part[a].round(1) for a in [2015, 2018, 2021, 2024]})
    for a0, a1 in PARES:
        r[f"cambio_rel_{a0}_{a1}"] = (pos[a1] - pos[a0]).round(1)
    r["caida"] = r[[f"cambio_rel_{a0}_{a1}" for a0, a1 in PARES]].mean(axis=1, skipna=False).round(1)
    # Contexto 2024: tipo de sección, distritos, tamaño y peso de jóvenes
    m24 = m[m.anio == 2024]
    ctx = m24.groupby("seccion").agg(tipo_seccion=("tipo_seccion", "first"),
                                     distrito_federal=("distrito_federal", "first"),
                                     distrito_local=("distrito_local", "first"), ln_2024=("LN", "sum"))
    jov = m24[m24.grupo_amplio == "18-29"].groupby("seccion")[["LN", "SV"]].sum()
    ctx["pct_jovenes_ln"] = (100 * jov.LN / ctx.ln_2024).round(1)
    ctx["part_jovenes_2024"] = pct(jov.SV, jov.LN)
    r = r.join(ctx)
    r["datos_completos"] = r.caida.notna()
    return r.reset_index().sort_values("caida")


def main():
    m = pd.read_csv(RAIZ / "data" / "processed" / "leon_maestra.csv")
    est = comparacion_estatal()
    tipo = por_tipo_seccion(m)
    est.to_csv(OUT / "tabla_leon_vs_gto.csv", index=False)
    tipo.to_csv(OUT / "tabla_tiposec.csv")
    grafica(est, tipo)

    c = caida(m)
    c.to_csv(OUT / "caida_secciones.csv", index=False)
    top = c[c.datos_completos].head(50)
    assert len(top) == 50
    top.to_csv(OUT / "top50_caida.csv", index=False)

    print(est.to_string(index=False), "\n")
    print(tipo.to_string(), "\n")
    print(f"Secciones del panel: {len(c)} | con datos completos: {c.datos_completos.sum()}")
    print(f"Top 50: caída de {top.caida.min()} a {top.caida.max()} pts vs. León")
    print(top.head(10)[["seccion", "tipo_seccion", "part_2015", "part_2021", "part_2018", "part_2024", "caida",
                        "pct_jovenes_ln", "ln_2024"]].to_string(index=False))
    resto = c[c.datos_completos].iloc[50:]
    print("\nTop 50 vs resto | %% jóvenes en LN: %.1f vs %.1f | part. jóvenes 2024: %.1f vs %.1f | tipo:"
          % (top.pct_jovenes_ln.mean(), resto.pct_jovenes_ln.mean(), top.part_jovenes_2024.mean(),
             resto.part_jovenes_2024.mean()), top.tipo_seccion.value_counts().to_dict())


if __name__ == "__main__":
    main()
