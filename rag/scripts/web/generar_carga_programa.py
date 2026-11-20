import json
from pathlib import Path

BASE = Path("rag/processed/web")
ENTRADA = BASE / "fragmentos_programa.jsonl"
SALIDA = BASE / "registrar_fragmentos_programa.sql"

DOCUMENTO_ID = "9a991358-d7bb-4b21-8115-af7d9aaa8e53"


def sql_texto(valor):
    return "'" + str(valor).replace("'", "''") + "'"


def main():
    registros = [
        json.loads(line)
        for line in ENTRADA.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    if not registros:
        raise ValueError("No hay fragmentos para cargar.")

    for r in registros:
        if not r["contenido"].strip():
            raise ValueError("Se encontró un fragmento vacío.")

        if r["codigo_guia"] != "UNAB-ING-SISTEMAS-WEB":
            raise ValueError("Código de fuente inesperado.")

        if r["metadata"]["estado_verificacion"] != "pendiente":
            raise ValueError("Estado de verificación inesperado.")

    valores = []

    for r in registros:
        valores.append(
            "(" + ", ".join([
                str(r["numero_fragmento"]),
                sql_texto(r["contenido"]),
                sql_texto(r["metadata"]["seccion"]),
                sql_texto(json.dumps(r["metadata"], ensure_ascii=False))
            ]) + ")"
        )

    sql = """
BEGIN;

WITH datos (
    numero_fragmento,
    contenido,
    seccion,
    metadata
) AS (
    VALUES
""" + ",\n".join(valores) + """
),
insertados AS (
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
        '""" + DOCUMENTO_ID + """'::uuid,
        NULL,
        datos.contenido,
        datos.numero_fragmento,
        NULL,
        datos.seccion,
        datos.metadata::jsonb
    FROM datos
    WHERE NOT EXISTS (
        SELECT 1
        FROM fragmentos_documento f
        WHERE f.documento_id = '""" + DOCUMENTO_ID + """'::uuid
          AND f.numero_fragmento = datos.numero_fragmento
    )
    RETURNING id
)
SELECT COUNT(*) AS fragmentos_insertados
FROM insertados;

COMMIT;
"""

    SALIDA.write_text(sql, encoding="utf-8")

    print("Fragmentos preparados:", len(registros))
    print("Documento:", DOCUMENTO_ID)
    print("Archivo SQL:", SALIDA)


if __name__ == "__main__":
    main()
