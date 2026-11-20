import json
from pathlib import Path

ENTRADA = Path("rag/processed/reglamento/fragmentos_reglamento.jsonl")
SALIDA = Path("rag/processed/reglamento/registrar_fragmentos_reglamento.sql")

DOCUMENTO_ID = "47890187-7e0c-4e0e-8c3e-0d998483f8e0"


def sql_texto(valor):
    if valor is None:
        return "NULL"
    return "'" + str(valor).replace("'", "''") + "'"


def main():
    with ENTRADA.open(encoding="utf-8") as f:
        registros = [json.loads(line) for line in f if line.strip()]

    if len(registros) != 144:
        raise ValueError(f"Se esperaban 144 artículos; hay {len(registros)}")

    valores = []

    for r in registros:
        m = r["metadata"]

        metadata = {
            **m,
            "codigo_guia": r["codigo_guia"],
            "numero_fragmento": r["numero_fragmento"],
            "numero_articulo": r["numero_articulo"],
            "numero_pagina": r["numero_pagina"],
        }

        seccion = " | ".join(
            x for x in [
                m.get("titulo"),
                m.get("capitulo"),
                f"ARTÍCULO {r['numero_articulo']}"
            ] if x
        )

        valores.append(
            "("
            + sql_texto(DOCUMENTO_ID) + "::uuid, "
            + "NULL, "
            + sql_texto(r["contenido"]) + ", "
            + str(r["numero_fragmento"]) + ", "
            + str(r["numero_pagina"]) + ", "
            + sql_texto(seccion) + ", "
            + sql_texto(json.dumps(metadata, ensure_ascii=False)) + "::jsonb"
            + ")"
        )

    sql = """BEGIN;

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
""" + ",\n".join(valores) + """
ON CONFLICT (documento_id, numero_fragmento) DO NOTHING;

COMMIT;
"""

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(sql, encoding="utf-8")

    print("ARTÍCULOS PREPARADOS:", len(registros))
    print("DOCUMENTO UUID:", DOCUMENTO_ID)
    print("ARTÍCULO MÁS EXTENSO:", max(
        registros, key=lambda x: len(x["contenido"])
    )["numero_articulo"])
    print("ARCHIVO SQL:", SALIDA)
    print("TAMAÑO SQL:", SALIDA.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
