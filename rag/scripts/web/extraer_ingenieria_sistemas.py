import re
import json
import hashlib
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo
from html.parser import HTMLParser
from html import unescape
from pathlib import Path

URL = "https://unab.edu.co/programas/ingenieria-de-sistemas/"

SALIDA = Path("rag/processed/web")
SALIDA.mkdir(parents=True, exist_ok=True)

class Extractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.textos = []
        self.ignorar = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "svg", "noscript"):
            self.ignorar += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "svg", "noscript") and self.ignorar:
            self.ignorar -= 1

    def handle_data(self, data):
        if not self.ignorar and data.strip():
            texto = re.sub(r"\s+", " ", unescape(data)).strip()
            if texto:
                self.textos.append(texto)

print("Descargando página oficial...")

peticion = urllib.request.Request(
    URL,
    headers={"User-Agent": "Mozilla/5.0 iBanu/1.0"}
)

with urllib.request.urlopen(peticion, timeout=30) as respuesta:
    html = respuesta.read().decode("utf-8", errors="replace")
    codigo_http = respuesta.status

parser = Extractor()
parser.feed(html)

# Unir y limpiar textos repetidos consecutivos
textos = []
for texto in parser.textos:
    if not textos or texto != textos[-1]:
        textos.append(texto)

contenido = "\n".join(textos)

# Registrar fuente y limitaciones
fecha = datetime.now(ZoneInfo("America/Bogota")).isoformat()

encabezado = f"""FUENTE INSTITUCIONAL: INGENIERÍA DE SISTEMAS UNAB

URL: {URL}
Fecha de consulta: {fecha}
Código HTTP: {codigo_http}
Tipo de contenido: página institucional
Estado de verificación: pendiente de revisión
Estado del plan de estudios: pendiente de actualización institucional.

NOTA IMPORTANTE:
El plan de estudios no se considera disponible ni actualizado en esta extracción.
No inferir asignaturas, semestres, créditos ni prerrequisitos.
La información provisional almacenada en otras fuentes de iBanú no debe
presentarse como el plan oficial vigente.

CONTENIDO EXTRAÍDO:
"""

documento = encabezado + contenido + "\n"

archivo_txt = SALIDA / "ingenieria_sistemas_unab.txt"
archivo_json = SALIDA / "ingenieria_sistemas_unab_metadata.json"

archivo_txt.write_text(documento, encoding="utf-8")

metadata = {
    "nombre": "Ingeniería de Sistemas UNAB",
    "url": URL,
    "fecha_consulta": fecha,
    "codigo_http": codigo_http,
    "origen": "institucional",
    "estado_verificacion": "pendiente",
    "estado_plan_estudios": "pendiente_actualizacion",
    "hash_sha256": hashlib.sha256(
        documento.encode("utf-8")
    ).hexdigest()
}

archivo_json.write_text(
    json.dumps(metadata, ensure_ascii=False, indent=4),
    encoding="utf-8"
)

print("\nEXTRACCIÓN COMPLETADA")
print("Código HTTP:", codigo_http)
print("Textos extraídos:", len(textos))
print("Caracteres:", len(contenido))
print("Archivo:", archivo_txt)
print("Metadatos:", archivo_json)
