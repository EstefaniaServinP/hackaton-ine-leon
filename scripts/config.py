"""Municipio a analizar. Todos los scripts leen de aquí qué estado y qué municipio usar y dónde guardar.

Por defecto: León, Guanajuato. Para otro municipio no hace falta editar nada; se pasa al correr todo:
    python scripts/00_todo.py --entidad 11 --municipio 17 --nombre Irapuato
(00_todo.py pone ENTIDAD, MUNICIPIO y NOMBRE como variables de entorno y corre los scripts en orden).

Claves: ENTIDAD es la clave del estado (01 a 32) y MUNICIPIO es la clave de municipio del INE (columna
MPIOCVE de los Conteos Censales; puede no coincidir con la del INEGI). Con --listar, 00_todo.py muestra las
claves de los municipios del estado.

Los resultados de León van en data/processed/ y outputs/. Los de cualquier otro municipio, en
data/processed/<nombre>/ y outputs/<nombre>/, para no mezclarlos.
"""
import os
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RAW = RAIZ / "data" / "raw"

# clave: (nombre del estado, sufijos del CSV de los Conteos Censales, % de ciudadanía sorteada que no se pudo
# localizar en la primera etapa de capacitación 2023-2024; INE, informe primera etapa, Tabla 2.17, p. 73)
ESTADOS = {
    1: ("Aguascalientes", ["ags"], 10.11), 2: ("Baja California", ["bc"], 17.21),
    3: ("Baja California Sur", ["bcs"], 22.52), 4: ("Campeche", ["camp"], 29.30),
    5: ("Coahuila", ["coah"], 15.43), 6: ("Colima", ["col"], 20.61), 7: ("Chiapas", ["chis"], 31.24),
    8: ("Chihuahua", ["chih"], 26.97), 9: ("Ciudad de México", ["cdmx"], 13.43), 10: ("Durango", ["dgo"], 22.71),
    11: ("Guanajuato", ["gto"], 21.57), 12: ("Guerrero", ["gro"], 28.70), 13: ("Hidalgo", ["hgo"], 14.47),
    14: ("Jalisco", ["jal"], 25.89), 15: ("México", ["mex"], 11.52), 16: ("Michoacán", ["mich"], 24.64),
    17: ("Morelos", ["mor"], 18.48), 18: ("Nayarit", ["nay"], 21.99), 19: ("Nuevo León", ["nl"], 13.74),
    20: ("Oaxaca", ["oax"], 27.10), 21: ("Puebla", ["pue"], 13.36), 22: ("Querétaro", ["qro"], 19.13),
    23: ("Quintana Roo", ["qroo"], 19.37), 24: ("San Luis Potosí", ["slp"], 18.78), 25: ("Sinaloa", ["sin"], 19.14),
    26: ("Sonora", ["son"], 18.99), 27: ("Tabasco", ["tab"], 23.11), 28: ("Tamaulipas", ["tamps", "tam"], 17.24),
    29: ("Tlaxcala", ["tlax"], 6.24), 30: ("Veracruz", ["ver"], 23.10), 31: ("Yucatán", ["yuc"], 16.65),
    32: ("Zacatecas", ["zac"], 28.82),
}

ENTIDAD = int(os.environ.get("ENTIDAD", 11))
MUNICIPIO = int(os.environ.get("MUNICIPIO", 20))
NOMBRE = os.environ.get("NOMBRE", "León")
ESTADO, SUFIJOS, NO_LOCALIZADO_PCT = ESTADOS[ENTIDAD]
ABREV = SUFIJOS[0]


def _slug(texto):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    return "".join(c if c.isalnum() else "_" for c in t).strip("_")


SLUG = _slug(NOMBRE)
ES_BASE = (ENTIDAD, MUNICIPIO) == (11, 20)
PROC = RAIZ / "data" / "processed" if ES_BASE else RAIZ / "data" / "processed" / SLUG
OUT = RAIZ / "outputs" if ES_BASE else RAIZ / "outputs" / SLUG
CENSO_DIR = RAW / "censo" if ENTIDAD == 11 else RAW / "censo" / f"{ENTIDAD:02d}"
CARTO = RAW / "cartografia"
PROC.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

MAESTRA = PROC / f"{SLUG}_maestra.csv"
SECCIONES = PROC / f"{SLUG}_secciones.geojson"
ESCUELAS = PROC / f"{SLUG}_escuelas.geojson"


def csv_estado(anio):
    """CSV de los Conteos Censales del estado para un año (lo extrae 01_descarga.py)."""
    return RAW / f"{ABREV}_{anio}.csv"
