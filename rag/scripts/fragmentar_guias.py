import json
import re
from pathlib import Path

BASE = Path("rag/processed/materias/Ingeniería de sistemas")
SALIDA = Path("rag/processed/fragmentos_guias.jsonl")

TAMANO = 2200
SOLAPAMIENTO = 300


def limpiar(texto):
    texto = texto.replace("\r", "")
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()


def dividir_pagina(texto):
    texto = limpiar(texto)

    if not texto:
        return []

    fragmentos = []
    inicio = 0

    while inicio < len(texto):
        fin = min(inicio + TAMANO, len(texto))

        if fin < len(texto):
            corte = texto.rfind(" ", inicio, fin)

            if corte > inicio + TAMANO // 2:
                fin = corte

        fragmento = texto[inicio:fin].strip()

        if fragmento:
            fragmentos.append(fragmento)

        if fin >= len(texto):
            break

        inicio = max(fin - SOLAPAMIENTO, inicio + 1)

    return fragmentos


def main():
    archivos = sorted(BASE.glob("*/*.txt"))

    SALIDA.parent.mkdir(parents=True, exist_ok=True)

    total = 0
    documentos = 0

    with SALIDA.open("w", encoding="utf-8") as salida:
        for archivo in archivos:
            semestre = archivo.parent.name
            codigo = archivo.stem

            texto = archivo.read_text(encoding="utf-8")
            paginas = texto.split("\f")

            numero_fragmento = 0

            for numero_pagina, pagina in enumerate(paginas, start=1):
                if not pagina.strip():
                    continue

                fragmentos = dividir_pagina(pagina)

                for contenido in fragmentos:
                    registro = {
                        "codigo_guia": codigo,
                        "semestre": semestre,
                        "numero_pagina": numero_pagina,
                        "numero_fragmento": numero_fragmento,
                        "contenido": contenido,
                        "metadata": {
                            "archivo_origen": archivo.name,
                            "ruta_origen": str(archivo),
                            "metodo_extraccion": "pdftotext -layout"
                        }
                    }

                    salida.write(
                        json.dumps(registro, ensure_ascii=False) + "\n"
                    )

                    numero_fragmento += 1
                    total += 1

            documentos += 1

    print("DOCUMENTOS PROCESADOS:", documentos)
    print("FRAGMENTOS GENERADOS:", total)
    print("ARCHIVO:", SALIDA)


if __name__ == "__main__":
    main()
