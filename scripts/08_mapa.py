"""HINE-21: mapa interactivo del semáforo de riesgo 2027 en León, sin y con intervención.

Uso: python scripts/08_mapa.py   (requiere 05_cartografia.py y 07_escenarios.py)
Resultado: outputs/mapa_escenarios.html   (abre directo en el navegador; requiere internet para el mapa base)

Capas:
  - Escenario (se elige uno): A sin intervención, B pesimista, B medio, B optimista
  - Top 50 secciones con mayor caída (contorno)
  - Preparatorias y universidades (brigadas de SE)
"""
import json
from pathlib import Path

import folium
import geopandas as gpd
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
PROC = RAIZ / "data" / "processed"
OUT = RAIZ / "outputs"

# Paleta de estado (dataviz): siempre acompañada de etiqueta en tooltip y leyenda
COLOR = {"rojo": "#d03b3b", "amarillo": "#fab219", "verde": "#0ca30c", None: "#b5b4ae"}
ETIQUETA = {"rojo": "Riesgo alto", "amarillo": "Riesgo medio", "verde": "Riesgo bajo", None: "Sin datos"}
ESCENARIOS = {
    "A": ("A · Sin intervención", "semaforo_A", "part_jov_2027", "part_2027"),
    "pesimista": ("B · Con intervención (pesimista)", "semaforo_B_pesimista", "part_jov_B_pesimista", "part_B_pesimista"),
    "medio": ("B · Con intervención (medio)", "semaforo_B_medio", "part_jov_B_medio", "part_B_medio"),
    "optimista": ("B · Con intervención (optimista)", "semaforo_B_optimista", "part_jov_B_optimista", "part_B_optimista"),
}


def fmt(v, suf="%"):
    return "—" if pd.isna(v) else f"{v:.1f}{suf}"


def cargar():
    geo = gpd.read_file(PROC / "leon_secciones.geojson")[["seccion", "geometry"]]
    esc = pd.read_csv(PROC / "escenarios_2027.csv")
    top50 = set(pd.read_csv(OUT / "top50_caida.csv").seccion)
    g = geo.merge(esc, on="seccion", how="left")
    g["top50"] = g.seccion.isin(top50)
    return g, gpd.read_file(PROC / "leon_escuelas.geojson")


def tooltip_html(r, sem, pj, pt):
    nivel = r[sem] if isinstance(r[sem], str) else None
    if nivel is None:
        return f"<b>Sección {r.seccion}</b><br>Sin datos de participación (sección nueva o sin registro)"
    extra = "<br><b>Top 50 de mayor caída</b>" if r.top50 else ""
    interv = "Sí" if r.intervenida else "No"
    return (f"<b>Sección {r.seccion}</b> · {ETIQUETA[nivel]}{extra}<br>"
            f"Jóvenes 18-29 en 2027: <b>{fmt(r[pj])}</b><br>"
            f"Participación total 2027: {fmt(r[pt])}<br>"
            f"Histórico total: 2021 {fmt(r.part_2021)} · 2024 {fmt(r.part_2024)}<br>"
            f"Jóvenes en lista nominal: {int(r.ln_jov_2024):,} ({fmt(r.pct_jov)})<br>"
            f"Recibe intervención: {interv} · Calidad del dato: {r.calidad}")


def capa_escenario(g, clave):
    nombre, sem, pj, pt = ESCENARIOS[clave]
    d = g[["seccion", "geometry"]].copy()
    d["color"] = [COLOR[s if isinstance(s, str) else None] for s in g[sem]]
    d["info"] = [tooltip_html(r, sem, pj, pt) for _, r in g.iterrows()]
    fg = folium.FeatureGroup(name=nombre, overlay=False, show=(clave == "A"))
    folium.GeoJson(
        json.loads(d.to_json(to_wgs84=True)),
        style_function=lambda f: {"fillColor": f["properties"]["color"], "color": "#fcfcfb",
                                  "weight": 0.6, "fillOpacity": 0.65},
        highlight_function=lambda f: {"weight": 2.5, "color": "#0b0b0b", "fillOpacity": 0.8},
        tooltip=folium.GeoJsonTooltip(fields=["info"], labels=False, sticky=True),
    ).add_to(fg)
    return fg


def leyenda(conteos):
    filas = "".join(
        f'<div style="display:flex;align-items:center;gap:8px;margin:3px 0">'
        f'<span style="width:14px;height:14px;border-radius:3px;background:{COLOR[k]}"></span>'
        f'<span>{ETIQUETA[k]}</span></div>' for k in ["rojo", "amarillo", "verde", None])
    tabla = "".join(f"<tr><td>{ESCENARIOS[k][0].split('·')[1].strip()}</td><td style='text-align:right'>{v}</td></tr>"
                    for k, v in conteos.items())
    return f"""
    <div style="position:fixed;bottom:24px;left:16px;z-index:9999;max-width:300px;background:#fcfcfb;color:#0b0b0b;
                padding:12px 14px;border-radius:8px;box-shadow:0 1px 6px rgba(0,0,0,.25);font:13px/1.4 system-ui,sans-serif">
      <div style="font-weight:700;font-size:14px;margin-bottom:4px">Riesgo de abstención juvenil 2027</div>
      <div style="color:#52514e;margin-bottom:6px">Participación predicha de jóvenes 18-29:
        alto &lt; 30 %, medio 30–40 %, bajo ≥ 40 %. Contorno negro: las 50 que más se han quedado atrás (prioridad).</div>
      {filas}
      <div style="display:flex;align-items:center;gap:8px;margin:3px 0">
        <span style="width:14px;height:14px;border:2.5px solid #0b0b0b;border-radius:3px"></span><span>Top 50 de mayor caída</span></div>
      <div style="display:flex;align-items:center;gap:8px;margin:3px 0">
        <span style="width:10px;height:10px;border-radius:50%;background:#6250d6;margin:0 2px"></span><span>Preparatoria / universidad</span></div>
      <table style="margin-top:6px;color:#52514e;font-size:12px;width:100%"><tr><td colspan=2><b>Secciones en riesgo alto</b></td></tr>{tabla}</table>
      <div style="color:#52514e;font-size:11px;margin-top:6px">Elige el escenario en el control de capas (arriba a la derecha).
        Fuente: INE, Conteos Censales 2009–2024 y Base Geográfica Digital.</div>
    </div>"""


def main():
    g, esc = cargar()
    centro = g.geometry.union_all().centroid
    m = folium.Map(location=[centro.y, centro.x], zoom_start=12, tiles=None, control_scale=True)
    # OpenStreetMap bloquea mosaicos pedidos desde archivo local; el lienzo gris de Esri no requiere clave
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ", name="Esri gris", max_zoom=16, control=False).add_to(m)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Reference/MapServer/tile/{z}/{y}/{x}",
        attr="Esri", name="Nombres", max_zoom=16, overlay=True, control=False).add_to(m)
    for clave in ESCENARIOS:
        capa_escenario(g, clave).add_to(m)

    top = folium.FeatureGroup(name="Top 50 de mayor caída", show=True)
    folium.GeoJson(json.loads(g[g.top50][["seccion", "geometry"]].to_json()),
                   style_function=lambda f: {"fill": False, "color": "#0b0b0b", "weight": 2.5},
                   interactive=False).add_to(top)
    top.add_to(m)

    escuelas = folium.FeatureGroup(name="Preparatorias y universidades (SE)", show=False)
    for r in esc.itertuples():
        folium.CircleMarker([r.geometry.y, r.geometry.x], radius=4, color="#fcfcfb", weight=2, fill=True,
                            fill_color="#6250d6", fill_opacity=1,
                            tooltip=f"{r.NOMBRE.title()} · {r.nivel} · sección {r.seccion}").add_to(escuelas)
    escuelas.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    todas = pd.read_csv(PROC / "escenarios_2027.csv")  # incluye las 13 secciones sin polígono
    conteos = {k: int((todas[v[1]] == "rojo").sum()) for k, v in ESCENARIOS.items()}
    m.get_root().html.add_child(folium.Element(leyenda(conteos)))
    m.get_root().header.add_child(folium.Element("<title>Mapa de Alerta de Abstención · León 2027</title>"))
    # Vista inicial: zona urbana (donde vive la mayoría del electorado); las rurales se ven al alejar
    x0, y0, x1, y1 = g[g.tipo_seccion == "U"].total_bounds
    m.fit_bounds([[y0, x0], [y1, x1]])
    salida = OUT / "mapa_escenarios.html"
    m.save(salida)
    print(f"{salida.relative_to(RAIZ)} ({salida.stat().st_size / 1e6:.1f} MB) · rojas por escenario: {conteos}")


if __name__ == "__main__":
    main()
