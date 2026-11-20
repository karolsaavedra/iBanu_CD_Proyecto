import json
from pathlib import Path

ENTRADA = Path(
    "rag/processed/programa/fragmentos_competencias_digitales.jsonl"
)
SALIDA = Path(
    "rag/processed/programa/registrar_fragmentos_competencias_digitales.sql"
)

DOCUMENTO_ID = "9a991358-d7bb-4b21-8115-af7d9aaa8e53"

def sql_texto(valor):
    return "'" + str(valor).replace("'", "''") + "'"

with ENTRADA.open(encoding="utf-8") as f:
    registros = [json.loads(line) for line in f if line.strip()]

valores = []

for r in registros:
    metadata = r["metadata"].copy()
    metadata["seccion"] = r["seccion"]
    metadata["numero_fragmento"] = r["numero_fragmento"]
    metadata["codigo_documento"] = r["codigo_documento"]

    valores.append(
        "("
        f"'{DOCUMENTO_ID}'::uuid, "
        "NULL, "
        f"{sql_texto(r['contenido'])}, "
        f"{r['numero_fragmento']}, "
        "NULL, "
        f"{sql_texto(r['seccion'])}, "
        f"{sql_texto(json.dumps(metadata, ensure_ascii=False))}::jsonb"
        ")"
    )

sql = f"""BEGIN;

INSERT INTO fragmentos_documento (
    documento_id,
    asignatura_id,
    contenido,
    numero_fragmento,
    numero_pagina,
    seccion,
    metadata
)
VALUES
{',\n'.join(valores)}
ON CONFLICT (documento_id, numero_fragmento) DO NOTHING;

COMMIT;
"""

SALIDA.parent.mkdir(parents=True, exist_ok=True)
SALIDA.write_text(sql, encoding="utf-8")

print("SQL GENERADO")
print("Fragmentos preparados:", len(registros))
print("Documento:", DOCUMENTO_ID)
print("Archivo:", SALIDA)
print("Tamaño:", SALIDA.stat().st_size, "bytes")
