import json
from pathlib import Path

ORIGEN = Path("rag/documents/materias_sinteticas")
SALIDA = Path("rag/processed/materias_sinteticas/fragmentos_materias_sinteticas.jsonl")

MAX_CARACTERES = 1800

fragmentos = []

for archivo in sorted(ORIGEN.glob("*.md")):
    texto = archivo.read_text(encoding="utf-8").strip()
    codigo = archivo.stem

    # Dividir conservando encabezados y párrafos.
    bloques = []
    actual = []

    for linea in texto.splitlines():
        if linea.startswith("#") and actual:
            bloques.append("\n".join(actual).strip())
            actual = [linea]
        else:
            actual.append(linea)

    if actual:
        bloques.append("\n".join(actual).strip())

    acumulado = ""

    for bloque in bloques:
        if not bloque:
            continue

        candidato = (acumulado + "\n\n" + bloque).strip()

        if len(candidato) > MAX_CARACTERES and acumulado:
            fragmentos.append((codigo, archivo.name, acumulado))
            acumulado = bloque
        else:
            acumulado = candidato

    if acumulado:
        fragmentos.append((codigo, archivo.name, acumulado))

registros = []

for numero, (codigo, nombre, contenido) in enumerate(fragmentos):
    registros.append({
        "codigo_asignatura": codigo,
        "codigo_documento": f"SINTETICO-{codigo}",
        "numero_fragmento": numero,
        "contenido": contenido,
        "metadata": {
            "archivo_origen": nombre,
            "tipo_fuente": "contenido_sintetico",
            "institucion": "UNAB",
            "origen_contenido": "elaboracion_sintetica_iBanu",
            "estado_verificacion": "pendiente",
            "estado_vigencia": "pendiente_validacion",
            "advertencia": "CONTENIDO SINTETICO - NO OFICIAL"
        }
    })

SALIDA.parent.mkdir(parents=True, exist_ok=True)

with SALIDA.open("w", encoding="utf-8") as f:
    for registro in registros:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")

print("FRAGMENTACIÓN COMPLETADA")
print("Fichas originales:", len(list(ORIGEN.glob("*.md"))))
print("Fragmentos generados:", len(registros))
print("Asignaturas:", len(set(r["codigo_asignatura"] for r in registros)))
print("Fragmentos mayores a 1800 caracteres:",
      sum(len(r["contenido"]) > MAX_CARACTERES for r in registros))
print("Archivo:", SALIDA)
