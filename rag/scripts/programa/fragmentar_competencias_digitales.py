import json
import re
from pathlib import Path

ORIGEN = Path(
    "rag/documents/programa/"
    "Propuesta Competencias Digitales UNAB V11ADC_clean.md"
)
SALIDA = Path(
    "rag/processed/programa/fragmentos_competencias_digitales.jsonl"
)

MAX_CARACTERES = 2200

texto = ORIGEN.read_text(encoding="utf-8")
lineas = texto.splitlines()

# Normalización conservadora: no modificar el contenido académico.
lineas = [
    linea.replace("\\.", ".").replace("\\)", ")").replace("\\&", "&")
    for linea in lineas
]

secciones = []
titulo_actual = "Introducción"
bloques = []
parrafo = []
tabla = []

def guardar_parrafo():
    if parrafo:
        contenido = "\n".join(parrafo).strip()
        if contenido:
            bloques.append(("texto", contenido))
        parrafo.clear()

def guardar_tabla():
    if tabla:
        contenido = "\n".join(tabla).strip()
        if contenido:
            bloques.append(("tabla", contenido))
        tabla.clear()

def guardar_seccion():
    guardar_parrafo()
    guardar_tabla()
    if bloques:
        secciones.append((titulo_actual, bloques.copy()))
        bloques.clear()

for linea in lineas:
    limpia = linea.strip()

    # Cada encabezado inicia una sección independiente.
    if re.match(r"^#{1,6}\s+", limpia):
        guardar_seccion()
        titulo_actual = re.sub(r"^#{1,6}\s+", "", limpia).strip()
        continue

    # Conservar cada tabla completa.
    if limpia.startswith("|"):
        guardar_parrafo()
        tabla.append(limpia)
        continue

    guardar_tabla()

    if not limpia:
        guardar_parrafo()
    else:
        parrafo.append(limpia)

guardar_seccion()

def dividir_texto(contenido):
    """Divide bloques largos intentando respetar los finales de oración."""
    if len(contenido) <= MAX_CARACTERES:
        return [contenido]

    oraciones = re.split(r"(?<=[.!?])\s+", contenido)
    resultado = []
    actual = ""

    for oracion in oraciones:
        if len(oracion) > MAX_CARACTERES:
            if actual:
                resultado.append(actual)
                actual = ""

            for inicio in range(0, len(oracion), MAX_CARACTERES):
                resultado.append(oracion[inicio:inicio + MAX_CARACTERES])
            continue

        candidato = (actual + " " + oracion).strip()

        if len(candidato) > MAX_CARACTERES and actual:
            resultado.append(actual)
            actual = oracion
        else:
            actual = candidato

    if actual:
        resultado.append(actual)

    return resultado

fragmentos = []

for titulo, bloques_seccion in secciones:
    acumulado = ""

    for tipo, contenido in bloques_seccion:
        partes = [contenido] if tipo == "tabla" else dividir_texto(contenido)

        for parte in partes:
            candidato = (acumulado + "\n\n" + parte).strip()

            if len(candidato) > MAX_CARACTERES and acumulado:
                fragmentos.append((titulo, acumulado))
                acumulado = parte
            else:
                acumulado = candidato

    if acumulado:
        fragmentos.append((titulo, acumulado))

registros = []

for numero, (titulo, contenido) in enumerate(fragmentos):
    registros.append({
        "codigo_documento": "UNAB-PROP-COMP-DIGITALES-V11",
        "numero_fragmento": numero,
        "seccion": titulo,
        "contenido": contenido,
        "metadata": {
            "archivo_origen": ORIGEN.name,
            "ruta_origen": str(ORIGEN),
            "tipo_fuente": "propuesta_academica",
            "institucion": "UNAB",
            "version_documento": "V11ADC_clean",
            "estado_verificacion": "pendiente",
            "estado_vigencia": "pendiente_validacion",
            "metodo_fragmentacion": "por_encabezados_y_bloques",
            "tablas_conservadas": True
        }
    })

SALIDA.parent.mkdir(parents=True, exist_ok=True)

with SALIDA.open("w", encoding="utf-8") as archivo:
    for registro in registros:
        archivo.write(json.dumps(registro, ensure_ascii=False) + "\n")

print("FRAGMENTACIÓN CORREGIDA")
print("Encabezados identificados:", len(secciones))
print("Fragmentos generados:", len(registros))
print("Secciones únicas:", len(set(r["seccion"] for r in registros)))
print("Tablas conservadas:", sum("|" in r["contenido"] for r in registros))
print("Fragmentos mayores a 2200 caracteres:",
      sum(len(r["contenido"]) > MAX_CARACTERES for r in registros))
print("Archivo:", SALIDA)
