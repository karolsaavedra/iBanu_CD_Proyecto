import json
from pathlib import Path

ORIGEN = Path("rag/processed/materias_sinteticas/fragmentos_materias_sinteticas.jsonl")
MANIFIESTO = Path("rag/processed/materias_sinteticas/documentos.json")
SALIDA = Path("rag/processed/materias_sinteticas/registrar_fragmentos.sql")

with ORIGEN.open(encoding="utf-8") as f:
    registros = [json.loads(line) for line in f if line.strip()]

documentos = json.loads(MANIFIESTO.read_text(encoding="utf-8"))
ids = {d["codigo"]: d["id"] for d in documentos}

def q(valor):
    return "'" + str(valor).replace("'", "''") + "'"

sentencias = ["BEGIN;"]

for r in registros:
    codigo = r["codigo_asignatura"]
    documento_id = ids[codigo]
    metadata = json.dumps(r["metadata"], ensure_ascii=False)

    sentencias.append(f"""
INSERT INTO fragmentos_documento (
    documento_id,
    asignatura_id,
    contenido,
    numero_fragmento,
    numero_pagina,
    seccion,
    metadata
)
SELECT
    '{documento_id}'::uuid,
    a.id,
    {q(r["contenido"])},
    {r["numero_fragmento"]},
    NULL,
    'contenido_sintetico',
    {q(metadata)}::jsonb
FROM asignaturas a
WHERE a.codigo = {q(codigo)}
ON CONFLICT (documento_id, numero_fragmento) DO NOTHING;
""".strip())

sentencias.append("COMMIT;")

SALIDA.write_text("\n\n".join(sentencias) + "\n", encoding="utf-8")

print("CARGA DE FRAGMENTOS PREPARADA")
print("Fragmentos:", len(registros))
print("Asignaturas:", len(set(r["codigo_asignatura"] for r in registros)))
print("Documentos relacionados:", len(set(ids[r["codigo_asignatura"]] for r in registros)))
print("SQL:", SALIDA)
print("Tamaño:", SALIDA.stat().st_size, "bytes")
