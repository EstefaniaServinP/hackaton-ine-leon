"""HINE-7: descarga los Conteos Censales de Participación 2009-2024 y extrae Guanajuato.

Uso: python scripts/01_descarga.py
Resultado: data/raw/gto_<año>.csv, data/raw/descripcion_campos_<año>.txt y data/raw/descarga.log
"""
import urllib.request
import zipfile
from pathlib import Path

BASE = "https://www.ine.mx/wp-content/uploads"
URLS = {
    2009: f"{BASE}/2022/04/DatosAbiertos_DECEyEC_ConteosCensales2009.zip",
    2012: f"{BASE}/2022/04/DatosAbiertos_DECEyEC_ConteosCensales2012.zip",
    2015: f"{BASE}/2022/04/DatosAbiertos_DECEyEC_ConteosCensales2015.zip",
    2018: f"{BASE}/2022/04/DatosAbiertos_DECEyEC_ConteosCensales2018.zip",
    2021: f"{BASE}/2022/04/DatosAbiertos_DECEyEC_ConteosCensales2021.zip",
    2024: f"{BASE}/2025/08/DatosAbiertos_DECEyEC_ConteosCensales2024.zip",
}

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
ZIPS = RAW / "zips"


def descargar(anio, url):
    destino = ZIPS / f"cc{anio}.zip"
    if not destino.exists():
        print(f"Descargando {anio}...")
        urllib.request.urlretrieve(url, destino)
    return destino


def extraer_gto(anio, zip_path):
    """Extrae el CSV de Guanajuato y la descripción de campos; devuelve el número de filas de datos."""
    with zipfile.ZipFile(zip_path) as z:
        nombres = z.namelist()
        csv = [n for n in nombres if n.lower().endswith(("_gto.csv", "_11.csv"))]
        desc = [n for n in nombres if "descripcion" in n.lower()]
        if len(csv) != 1:
            raise RuntimeError(f"{anio}: no encontré un único CSV de Guanajuato en {nombres[:5]}...")
        salida = RAW / f"gto_{anio}.csv"
        salida.write_bytes(z.read(csv[0]))
        if desc:
            (RAW / f"descripcion_campos_{anio}.txt").write_bytes(z.read(desc[0]))
    with open(salida, "rb") as f:
        return sum(1 for _ in f) - 1


def main():
    ZIPS.mkdir(parents=True, exist_ok=True)
    log = []
    for anio, url in URLS.items():
        filas = extraer_gto(anio, descargar(anio, url))
        linea = f"{anio}\t{filas:,} filas"
        print(linea)
        log.append(linea)
    (RAW / "descarga.log").write_text("\n".join(log) + "\n")


if __name__ == "__main__":
    main()
