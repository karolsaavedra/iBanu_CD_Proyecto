import csv
import hashlib
from pathlib import Path

BASE = Path("rag/documents/materias/Ingeniería de sistemas")
INVENTARIO = Path("rag/processed/inventario_guias.csv")
COMPARACION = Path("rag/processed/comparacion_catalogo_guias.csv")
SALIDA = Path("rag/processed/registrar_guias.sql")


def sql(valor):
    """Convierte un valor Python en literal SQL seguro."""
    if valor is None:
        return "NULL"
    return "'" + str(valor).replace("'", "''") + "'"


with INVENTARIO.open(encoding="utf-8-sig", newline="") as f:
    inventario = list(csv.DictReader(f))

with COMPARACION.open(encoding="utf-8-sig", newline="") as f:
    comparacion = list(csv.DictReader(f))

relaciones = {
    fila["codigo_guia"]: fila
    for fila in comparacion
    if fila["estado"] == "COINCIDE"
}

registros = []
hashes = set()

for guia in inventario:
    codigo = guia["codigo"]
    relacion = relaciones.get(codigo)

    if not relacion:
        raise ValueError(f"No existe coincidencia para {codigo}")

    ruta = BASE / guia["semestre_carpeta"] / f"{codigo}.pdf"

    if not ruta.is_file():
        raise FileNotFoundError(ruta)

    contenido_hash = hashlib.sha256(ruta.read_bytes()).hexdigest()

    if contenido_hash in hashes:
        raise ValueError(f"PDF duplicado por contenido: {codigo}")

    hashes.add(contenido_hash)

    ruta_relativa = ruta.as_posix()
    nombre = ruta.name
    asignatura = relacion["nombre_catalogo"]

    registros.append({
        "codigo": codigo,
        "codigo_catalogo": relacion["codigo_catalogo"],
        "nombre": asignatura,
        "archivo": nombre,
        "ruta": ruta_relativa,
        "hash": contenido_hash,
    })


if len(registros) != 30:
    raise ValueError(f"Se esperaban 30 documentos, se encontraron {len(registros)}")


valores = []

for r in registros:
    valores.append(
        "("
        + ", ".join([
            sql(r["archivo"]),
            sql(r["archivo"]),
            "'pdf'",
            "'materias'",
            sql(
                "Guía de cátedra de " + r["nombre"]
                + ". Documento aportado por el usuario; pendiente de verificación institucional."
            ),
            "'usuario'",
            "'pendiente'",
            sql(r["ruta"]),
            sql(r["hash"]),
            sql(
                "Código de guía: " + r["codigo"]
                + ". Código del catálogo provisional: " + r["codigo_catalogo"]
            ),
        ])
        + ")"
    )

sql_script = """-- iBanú: registro inicial de 30 guías académicas
-- Origen usuario; verificación pendiente.
-- No se insertan fragmentos ni embeddings en esta etapa.

BEGIN;

WITH datos (
    nombre_archivo,
    nombre_original,
    tipo_archivo,
    categoria,
    descripcion,
    origen,
    estado_verificacion,
    ruta_archivo,
    hash_contenido,
    observaciones
) AS (
    VALUES
""" + ",\n".join(valores) + """
)
INSERT INTO public.documentos_academicos (
    nombre_archivo,
    nombre_original,
    tipo_archivo,
    categoria,
    descripcion,
    origen,
    estado_verificacion,
    ruta_archivo,
    hash_contenido,
    observaciones
)
SELECT
    d.nombre_archivo,
    d.nombre_original,
    d.tipo_archivo,
    d.categoria,
    d.descripcion,
    d.origen,
    d.estado_verificacion,
    d.ruta_archivo,
    d.hash_contenido,
    d.observaciones
FROM datos d
WHERE NOT EXISTS (
    SELECT 1
    FROM public.documentos_academicos existente
    WHERE existente.hash_contenido = d.hash_contenido
);

-- Vincular cada documento con su asignatura del catálogo provisional.
WITH relaciones (hash_contenido, codigo_catalogo) AS (
    VALUES
""" + ",\n".join(
    "(" + sql(r["hash"]) + ", " + sql(r["codigo_catalogo"]) + ")"
    for r in registros
) + """
)
INSERT INTO public.documentos_asignaturas (
    documento_id,
    asignatura_id,
    observaciones
)
SELECT
    d.id,
    a.id,
    'Relación por coincidencia de código y nombre con el catálogo provisional 2026.'
FROM relaciones r
JOIN public.documentos_academicos d
    ON d.hash_contenido = r.hash_contenido
JOIN public.asignaturas a
    ON a.codigo = r.codigo_catalogo
WHERE NOT EXISTS (
    SELECT 1
    FROM public.documentos_asignaturas da
    WHERE da.documento_id = d.id
      AND da.asignatura_id = a.id
);

COMMIT;
"""

SALIDA.parent.mkdir(parents=True, exist_ok=True)
SALIDA.write_text(sql_script, encoding="utf-8")

print("Archivo SQL generado:", SALIDA)
print("Documentos preparados:", len(registros))
print("Relaciones preparadas:", len(registros))
print("Hashes SHA-256 únicos:", len(hashes))
print("\nPrimeros 5 registros:")
for r in registros[:5]:
    print(
        r["codigo"],
        "|",
        r["codigo_catalogo"],
        "|",
        r["nombre"],
        "|",
        r["hash"][:16] + "..."
    )
