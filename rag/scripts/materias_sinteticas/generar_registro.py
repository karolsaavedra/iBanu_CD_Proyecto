import hashlib
import json
import uuid
from pathlib import Path

ORIGEN = Path("rag/documents/materias_sinteticas")
SALIDA_JSON = Path("rag/processed/materias_sinteticas/documentos.json")
SALIDA_SQL = Path("rag/processed/materias_sinteticas/registrar_documentos.sql")

documentos = []

for archivo in sorted(ORIGEN.glob("*.md")):
    codigo = archivo.stem
    contenido = archivo.read_bytes()

    documentos.append({
        "id": str(uuid.uuid4()),
        "codigo": codigo,
        "archivo": archivo.name,
        "hash": hashlib.sha256(contenido).hexdigest(),
        "ruta": str(archivo)
    })

if len(documentos) != 8:
    raise SystemExit(f"ERROR: Se esperaban 8 fichas y hay {len(documentos)}")

def q(valor):
    return "'" + str(valor).replace("'", "''") + "'"

sentencias = ["BEGIN;"]

for d in documentos:
    sentencias.append(f"""
INSERT INTO documentos_academicos (
    id, nombre_archivo, nombre_original, tipo_archivo,
    categoria, descripcion, origen, estado_verificacion,
    version_documento, ruta_archivo, hash_contenido,
    observaciones, activo
)
VALUES (
    '{d["id"]}',
    {q(d["archivo"])},
    {q("Ficha sintética: " + d["codigo"])},
    'otro',
    'materias',
    'Ficha académica sintética orientativa para iBanú.',
    'usuario',
    'pendiente',
    'sintetico-2026',
    {q(d["ruta"])},
    {q(d["hash"])},
    'CONTENIDO SINTÉTICO - NO OFICIAL. No corresponde a una guía de cátedra ni a un documento aprobado por la UNAB.',
    TRUE
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO documentos_asignaturas (
    documento_id, asignatura_id, observaciones
)
SELECT
    '{d["id"]}'::uuid,
    a.id,
    'Ficha sintética no oficial; pendiente de validación institucional.'
FROM asignaturas a
WHERE a.codigo = {q(d["codigo"])}
ON CONFLICT (documento_id, asignatura_id) DO NOTHING;
""".strip())

    sentencias.append("")

sentencias.append("COMMIT;")

SALIDA_JSON.parent.mkdir(parents=True, exist_ok=True)
SALIDA_JSON.write_text(
    json.dumps(documentos, ensure_ascii=False, indent=2),
    encoding="utf-8"
)
SALIDA_SQL.write_text("\n\n".join(sentencias), encoding="utf-8")

print("REGISTRO PREPARADO")
print("Documentos:", len(documentos))
print("Asignaturas vinculadas:", len({d["codigo"] for d in documentos}))
print("SQL:", SALIDA_SQL)
print("Manifiesto:", SALIDA_JSON)
print("Tamaño SQL:", SALIDA_SQL.stat().st_size, "bytes")

for d in documentos:
    print(d["codigo"], "|", d["id"])
