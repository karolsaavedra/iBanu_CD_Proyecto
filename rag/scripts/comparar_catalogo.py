import csv
import unicodedata
from pathlib import Path

BASE = Path("rag/processed")

def normalizar(texto):
    texto = unicodedata.normalize("NFD", texto.lower())
    texto = "".join(
        c for c in texto
        if unicodedata.category(c) != "Mn"
    )
    return " ".join(texto.split()).replace(".", "")

with open(BASE / "inventario_guias.csv",
          encoding="utf-8-sig") as f:
    guias = list(csv.DictReader(f))

with open(BASE / "catalogo_plan_2026.csv",
          encoding="utf-8-sig") as f:
    materias = list(csv.DictReader(f))

por_nombre = {
    normalizar(m["nombre"]): m
    for m in materias
}

# Correcciones verificadas de errores de extracción PDF
por_nombre[normalizar("INVESTIGACIN DE OPERACIONES II")] = next(
    m for m in materias
    if normalizar(m["nombre"]) == normalizar("Investigación de Operaciones II")
)

resultado = []
codigos_encontrados = set()

for guia in guias:
    nombre = normalizar(guia["asignatura_extraida"])
    materia = por_nombre.get(nombre)

    if materia is None:
        resultado.append({
            "codigo_guia": guia["codigo"],
            "nombre_guia": guia["asignatura_extraida"],
            "semestre_guia": guia["semestre_carpeta"],
            "creditos_guia": guia["creditos_extraidos"],
            "codigo_catalogo": "",
            "nombre_catalogo": "",
            "semestre_catalogo": "",
            "creditos_catalogo": "",
            "estado": "REVISAR_NOMBRE"
        })
        continue

    codigos_encontrados.add(materia["codigo"])

    mismo_semestre = (
        guia["semestre_carpeta"].split()[0]
        == materia["semestre"]
    )
    mismos_creditos = (
        guia["creditos_extraidos"] == materia["creditos"]
    )

    estado = (
        "COINCIDE"
        if mismo_semestre and mismos_creditos
        else "REVISAR_SEMESTRE_O_CREDITOS"
    )

    resultado.append({
        "codigo_guia": guia["codigo"],
        "nombre_guia": guia["asignatura_extraida"],
        "semestre_guia": guia["semestre_carpeta"],
        "creditos_guia": guia["creditos_extraidos"],
        "codigo_catalogo": materia["codigo"],
        "nombre_catalogo": materia["nombre"],
        "semestre_catalogo": materia["semestre"],
        "creditos_catalogo": materia["creditos"],
        "estado": estado
    })

for materia in materias:
    if materia["codigo"] not in codigos_encontrados:
        resultado.append({
            "codigo_guia": "",
            "nombre_guia": "",
            "semestre_guia": "",
            "creditos_guia": "",
            "codigo_catalogo": materia["codigo"],
            "nombre_catalogo": materia["nombre"],
            "semestre_catalogo": materia["semestre"],
            "creditos_catalogo": materia["creditos"],
            "estado": "SIN_GUIA_PDF"
        })

salida = BASE / "comparacion_catalogo_guias.csv"

with open(salida, "w", newline="", encoding="utf-8-sig") as f:
    campos = resultado[0].keys()
    writer = csv.DictWriter(f, fieldnames=campos)
    writer.writeheader()
    writer.writerows(resultado)

print("Comparación generada:", salida)
print("Guías procesadas:", len(guias))
print("Asignaturas del catálogo:", len(materias))
print("\nResultados:")

for fila in resultado:
    print(
        fila["estado"],
        "|",
        fila["codigo_guia"] or fila["codigo_catalogo"],
        "|",
        fila["nombre_catalogo"] or fila["nombre_guia"]
    )

