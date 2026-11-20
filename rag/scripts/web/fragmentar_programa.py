import json
import re
from pathlib import Path

BASE = Path("rag/processed/web")
ENTRADA = BASE / "ingenieria_sistemas_unab_limpio.txt"
SALIDA = BASE / "fragmentos_programa.jsonl"

TAMANO = 2200
SOLAPAMIENTO = 300


def limpiar(texto):
    texto = texto.replace("\r", "")
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()


def dividir(texto):
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

        contenido = texto[inicio:fin].strip()

        if contenido:
            fragmentos.append(contenido)

        if fin >= len(texto):
            break

        inicio = max(fin - SOLAPAMIENTO, inicio + 1)

    return fragmentos


def main():
    if not ENTRADA.exists():
        raise FileNotFoundError(f"No existe: {ENTRADA}")

    texto = ENTRADA.read_text(encoding="utf-8")
    lineas = texto.splitlines()

    secciones = []
    nombre_seccion = "Información general"
    contenido_seccion = []

    for linea in lineas:
        coincidencia = re.match(r"^\s*\d+\.\s+([A-ZÁÉÍÓÚÜÑ][A-ZÁÉÍÓÚÜÑ\s]+)$", linea)

        if coincidencia:
            if contenido_seccion:
                secciones.append(
                    (nombre_seccion, "\n".join(contenido_seccion))
                )

            nombre_seccion = coincidencia.group(1).strip()
            contenido_seccion = [linea]
        else:
            contenido_seccion.append(linea)

    if contenido_seccion:
        secciones.append(
            (nombre_seccion, "\n".join(contenido_seccion))
        )

    registros = []
    numero_fragmento = 0

    for nombre, contenido in secciones:
        for parte in dividir(contenido):
            registros.append({
                "codigo_guia": "UNAB-ING-SISTEMAS-WEB",
                "semestre": None,
                "numero_pagina": None,
                "numero_fragmento": numero_fragmento,
                "contenido": parte,
                "metadata": {
                    "archivo_origen": ENTRADA.name,
                    "ruta_origen": str(ENTRADA),
                    "metodo_extraccion": "HTMLParser",
                    "tipo_fuente": "pagina_institucional",
                    "institucion": "UNAB",
                    "programa": "Ingeniería de Sistemas",
                    "seccion": nombre,
                    "url_origen": (
                        "https://unab.edu.co/programas/"
                        "ingenieria-de-sistemas/"
                    ),
                    "fecha_consulta": "2026-11-14",
                    "estado_verificacion": "pendiente",
                    "estado_plan_estudios": "pendiente_actualizacion"
                }
            })

            numero_fragmento += 1

    SALIDA.parent.mkdir(parents=True, exist_ok=True)

    with SALIDA.open("w", encoding="utf-8") as archivo:
        for registro in registros:
            archivo.write(
                json.dumps(registro, ensure_ascii=False) + "\n"
            )

    print("DOCUMENTO PROCESADO:", ENTRADA.name)
    print("SECCIONES IDENTIFICADAS:", len(secciones))
    print("FRAGMENTOS GENERADOS:", len(registros))
    print("ARCHIVO:", SALIDA)

    print("\nSECCIONES:")
    for nombre, _ in secciones:
        print("-", nombre)


if __name__ == "__main__":
    main()
