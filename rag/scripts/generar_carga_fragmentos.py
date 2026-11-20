import json
from pathlib import Path

ENTRADA = Path("rag/processed/fragmentos_guias.jsonl")
SALIDA = Path("rag/processed/registrar_fragmentos.sql")


def sql_texto(valor):
    return "'" + str(valor).replace("'", "''") + "'"


def main():
    registros = [
        json.loads(line)
        for line in ENTRADA.read_text(encoding="utf-8").splitlines()
    ]

    if not registros:
        raise ValueError("No hay fragmentos para cargar.")

    codigos = set()
    for r in registros:
        if not r["contenido"].strip():
            raise ValueError("Se encontró un fragmento vacío.")
        codigos.add(r["codigo_guia"])

    valores = []

    for r in registros:
        metadata = dict(r["metadata"])
        metadata["codigo_guia"] = r["codigo_guia"]
        metadata["semestre"] = r["semestre"]

        valores.append(
            "("
            + ", ".join([
                sql_texto(r["codigo_guia"]),
                str(r["numero_fragmento"]),
                str(r["numero_pagina"]),
                sql_texto(r["contenido"]),
                sql_texto(json.dumps(metadata, ensure_ascii=False))
            ])
            + ")"
        )

    sql = """
BEGIN;

WITH datos (
    codigo_guia,
    numero_fragmento,
    numero_pagina,
    contenido,
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
        d.id,
        da.asignatura_id,
        datos.contenido,
        datos.numero_fragmento,
        datos.numero_pagina,
        NULL,
        datos.metadata::jsonb
    FROM datos
    JOIN documentos_academicos d
        ON d.nombre_archivo = datos.codigo_guia || '.pdf'
    JOIN documentos_asignaturas da
        ON da.documento_id = d.id
    WHERE NOT EXISTS (
        SELECT 1
        FROM fragmentos_documento f
        WHERE f.documento_id = d.id
          AND f.numero_fragmento = datos.numero_fragmento
    )
    RETURNING id
)
SELECT COUNT(*) AS fragmentos_insertados
FROM insertados;

COMMIT;
"""

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(sql, encoding="utf-8")

    print("Fragmentos preparados:", len(registros))
    print("Guías relacionadas:", len(codigos))
    print("Archivo SQL:", SALIDA)


if __name__ == "__main__":
    main()
