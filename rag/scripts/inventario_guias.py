import csv
import re
from pathlib import Path

carpeta = Path("rag/processed/materias/Ingeniería de sistemas")
salida = Path("rag/processed/inventario_guias.csv")

registros = []

for archivo in sorted(carpeta.rglob("*.txt")):
    lineas = archivo.read_text(
        encoding="utf-8", errors="replace"
    ).splitlines()

    codigo = archivo.stem
    nombre = ""
    creditos = ""

    for i, linea in enumerate(lineas):
        if "Nombre del Curso" not in linea:
            continue

        for j in range(i + 1, min(i + 8, len(lineas))):
            coincidencia = re.search(
                r"\s{2,}[A-Z]{3,5}\s+[A-Z]{3,5}\s+\d{5}\b",
                linea_actual := lineas[j]
            )

            if coincidencia:
                nombre = linea_actual[:coincidencia.start()].strip()

                # Recuperar una posible continuación del nombre.
                for siguiente in lineas[j + 1:j + 3]:
                    siguiente = siguiente.strip()

                    if not siguiente:
                        continue

                    if siguiente.startswith(
                        ("Facultad", "Programa", "Niveles", "Modalidad")
                    ):
                        break

                    if re.fullmatch(
                        r"[A-ZÁÉÍÓÚÜÑ0-9 .,'()/-]+", siguiente
                    ):
                        nombre += " " + siguiente

                    break

                break

        coincidencia_creditos = re.search(
            r"Número de creditos:\s*(\d+)",
            linea,
            re.IGNORECASE
        )
        if coincidencia_creditos:
            creditos = coincidencia_creditos.group(1)

        break

    registros.append({
        "archivo": archivo.name,
        "codigo": codigo,
        "semestre_carpeta": archivo.parent.name,
        "asignatura_extraida": re.sub(r"\s+", " ", nombre).strip(),
        "creditos_extraidos": creditos
    })

salida.parent.mkdir(parents=True, exist_ok=True)

with salida.open("w", newline="", encoding="utf-8-sig") as f:
    escritor = csv.DictWriter(f, fieldnames=registros[0].keys())
    escritor.writeheader()
    escritor.writerows(registros)

print(f"Total de guías: {len(registros)}")
print(f"Inventario: {salida}\n")

for r in registros:
    print(
        f'{r["codigo"]} | {r["asignatura_extraida"]} '
        f'| Créditos: {r["creditos_extraidos"]}'
    )

incompletos = [
    r for r in registros
    if not r["asignatura_extraida"] or not r["creditos_extraidos"]
]

print(f"\nRegistros que requieren revisión: {len(incompletos)}")
