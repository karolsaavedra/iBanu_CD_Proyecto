import json
import re
from pathlib import Path

ENTRADA = Path("rag/processed/reglamento/reglamento_estudiantil.txt")
SALIDA = Path("rag/processed/reglamento/fragmentos_reglamento.jsonl")

PATRON_ARTICULO = re.compile(
    r"^\s*ARTÍCULO\s+(\d+)\.\s*(.*)$",
    re.IGNORECASE
)

PATRON_TITULO = re.compile(
    r"^\s*TÍTULO\s+(PRIMERO|SEGUNDO|TERCERO|CUARTO|QUINTO)\b.*$",
    re.IGNORECASE
)

PATRON_CAPITULO = re.compile(
    r"^\s*CAPÍTULO\s+"
    r"(PRIMERO|SEGUNDO|TERCERO|CUARTO|QUINTO|SEXTO|SÉPTIMO|OCTAVO|ÚNICO)\b.*$",
    re.IGNORECASE
)


def limpiar(texto):
    texto = texto.replace("\r", "")

    # Reconstruir palabras separadas por guion de final de línea.
    texto = re.sub(
        r"(?<=[A-Za-zÁÉÍÓÚÜÑáéíóúüñ])-\s*\n\s*(?=[a-záéíóúüñ])",
        "",
        texto
    )

    # Conservar la separación entre palabras al unir líneas.
    texto = re.sub(r"(?<=[,;:])(?=[A-Za-zÁÉÍÓÚÜÑáéíóúüñ])", " ", texto)
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)

    return texto.strip()


def main():
    texto = ENTRADA.read_text(encoding="utf-8")
    paginas = texto.split("\f")

    registros = []
    titulo_actual = None
    capitulo_actual = None
    articulo_actual = None

    def guardar_articulo():
        if articulo_actual is None:
            return

        contenido = limpiar("\n".join(articulo_actual["lineas"]))

        if not contenido:
            return

        registros.append({
            "codigo_guia": "UNAB-REGLAMENTO-PREGRADO-2019",
            "numero_fragmento": len(registros),
            "numero_articulo": articulo_actual["numero"],
            "numero_pagina": articulo_actual["pagina_inicio"],
            "contenido": contenido,
            "metadata": {
                "archivo_origen": "Reglamento-estudiantil-pregrado.pdf",
                "ruta_origen": "rag/documents/reglamento/Reglamento-estudiantil-pregrado.pdf",
                "metodo_extraccion": "pdftotext -layout",
                "tipo_fuente": "reglamento_estudiantil",
                "institucion": "UNAB",
                "version_documento": "2019",
                "numero_articulo": articulo_actual["numero"],
                "titulo": articulo_actual["titulo"],
                "capitulo": articulo_actual["capitulo"],
                "pagina_inicio_pdf": articulo_actual["pagina_inicio"],
                "pagina_fin_pdf": articulo_actual["pagina_fin"],
                "estado_verificacion": "pendiente",
                "estado_vigencia": "pendiente_validacion"
            }
        })

    for numero_pagina, contenido_pagina in enumerate(paginas, start=1):

        for linea in contenido_pagina.splitlines():

            linea_limpia = linea.strip()

            if not linea_limpia:
                if articulo_actual is not None:
                    articulo_actual["lineas"].append("")
                continue

            # El PDF tiene dos páginas iniciales sin numeración impresa.
            # Se eliminan solamente los pies que coinciden con ese desplazamiento.
            if (
                linea_limpia.isdigit()
                and int(linea_limpia) == numero_pagina - 2
            ):
                continue

            coincidencia_titulo = PATRON_TITULO.match(linea_limpia)
            coincidencia_capitulo = PATRON_CAPITULO.match(linea_limpia)

            if coincidencia_titulo:
                guardar_articulo()
                articulo_actual = None
                titulo_actual = linea_limpia
                capitulo_actual = None
                continue

            if coincidencia_capitulo:
                guardar_articulo()
                articulo_actual = None
                capitulo_actual = linea_limpia
                continue

            coincidencia_articulo = PATRON_ARTICULO.match(linea_limpia)

            if coincidencia_articulo:
                guardar_articulo()

                articulo_actual = {
                    "numero": int(coincidencia_articulo.group(1)),
                    "pagina_inicio": numero_pagina,
                    "pagina_fin": numero_pagina,
                    "titulo": titulo_actual,
                    "capitulo": capitulo_actual,
                    "lineas": [linea_limpia]
                }
                continue

            if articulo_actual is not None:
                articulo_actual["lineas"].append(linea)
                articulo_actual["pagina_fin"] = numero_pagina

    guardar_articulo()

    numeros = [r["numero_articulo"] for r in registros]

    if len(registros) != 144:
        raise ValueError(
            f"Se esperaban 144 artículos y se encontraron {len(registros)}."
        )

    if set(numeros) != set(range(1, 145)):
        raise ValueError("La numeración de los artículos tiene errores.")

    SALIDA.parent.mkdir(parents=True, exist_ok=True)

    with SALIDA.open("w", encoding="utf-8") as archivo:
        for registro in registros:
            archivo.write(
                json.dumps(registro, ensure_ascii=False) + "\n"
            )

    print("DOCUMENTO PROCESADO:", ENTRADA.name)
    print("ARTÍCULOS FRAGMENTADOS:", len(registros))
    print("PRIMER ARTÍCULO:", numeros[0])
    print("ÚLTIMO ARTÍCULO:", numeros[-1])
    print("ARCHIVO GENERADO:", SALIDA)


if __name__ == "__main__":
    main()
