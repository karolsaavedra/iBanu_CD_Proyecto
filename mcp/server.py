import os
import re
import httpx
from urllib.parse import quote
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_request

API_URL = os.getenv("IBANU_API_URL", "http://127.0.0.1:8000").rstrip("/")

mcp = FastMCP("iBanu - MCP Académico")


def obtener_codigo_estudiante() -> str | None:
    try:
        request = get_http_request()
        codigo = request.headers.get("x-student-code", "")
        if re.fullmatch(r"U\d{8}", codigo):
            return codigo
    except RuntimeError:
        pass

    return None


def consultar_api(ruta: str) -> dict:
    try:
        respuesta = httpx.get(f"{API_URL}{ruta}", timeout=15.0)
        respuesta.raise_for_status()
        return respuesta.json()
    except httpx.HTTPStatusError as error:
        if error.response.status_code == 404:
            return {"error": "No se encontró la información solicitada."}
        return {"error": f"Error del backend: HTTP {error.response.status_code}"}
    except httpx.RequestError:
        return {"error": "No fue posible conectar con el backend de iBanú."}


def consultar_api_estudiante(sufijo: str) -> dict:
    codigo = obtener_codigo_estudiante()

    if not codigo:
        return {"error": "No se recibió un código de estudiante válido para esta consulta."}

    return consultar_api(f"/estudiantes/{codigo}{sufijo}")


@mcp.tool
def consultar_estudiante() -> dict:
    """Consulta los datos básicos del estudiante asociado a la solicitud."""
    return consultar_api_estudiante("")


@mcp.tool
def consultar_horario() -> dict:
    """Consulta el horario académico actual del estudiante asociado a la solicitud."""
    return consultar_api_estudiante("/horario")


@mcp.tool
def consultar_historial() -> dict:
    """Consulta el historial académico y las notas del estudiante asociado a la solicitud."""
    return consultar_api_estudiante("/historial")


@mcp.tool
def consultar_materias_pendientes() -> dict:
    """Consulta las materias aprobadas, actuales y pendientes del estudiante asociado."""
    return consultar_api_estudiante("/materias-pendientes")


@mcp.tool
def consultar_siguiente_semestre() -> dict:
    """Consulta las asignaturas del siguiente nivel del plan provisional del estudiante."""
    return consultar_api_estudiante("/siguiente-semestre")


@mcp.tool
def consultar_turnos() -> dict:
    """Consulta los turnos sintéticos asociados al estudiante de la solicitud."""
    return consultar_api_estudiante("/turnos")


@mcp.tool
def consultar_grupos(codigo_periodo: str) -> dict:
    """Consulta grupos, profesores, horarios y cupos de un periodo académico."""
    return consultar_api(f"/periodos/{codigo_periodo}/grupos")


@mcp.tool
def consultar_asignatura(codigo_asignatura: str) -> dict:
    """Consulta el catálogo académico por código de asignatura. Devuelve nombre, créditos y profesores asociados. UTILIZA ESTA HERRAMIENTA cuando el estudiante pregunte por una materia, quién es su profesor, quién la dicta o qué docentes están asignados."""
    return consultar_api(f"/academicos/asignaturas/{codigo_asignatura}")


@mcp.tool
def consultar_profesor(codigo_profesor: str) -> dict:
    """Consulta el directorio de profesores por código. Devuelve nombre, departamento y asignaturas asociadas. UTILIZA ESTA HERRAMIENTA cuando el estudiante pregunte por un profesor, qué materias dicta, qué asignaturas tiene asignadas o quién es un docente."""
    return consultar_api(f"/academicos/profesores/{codigo_profesor}")


@mcp.tool
def buscar_profesor_por_nombre(nombre: str) -> dict:
    """Busca profesores por nombre o apellido. UTILIZA ESTA HERRAMIENTA cuando el estudiante mencione el nombre de un profesor y pregunte qué asignaturas dicta, qué materias tiene asociadas o información sobre ese docente. No requiere código de profesor."""
    return consultar_api(f"/academicos/profesores/buscar/{httpx.URL('http://localhost').copy_with(path='/' + nombre).raw_path.decode().lstrip('/')}")


@mcp.tool
def consultar_estado_plataforma() -> dict:
    """Consulta el estado del backend y la conexión con Supabase."""
    backend = consultar_api("/health")
    base_datos = consultar_api("/health/database")
    return {"backend": backend, "base_datos": base_datos}




@mcp.tool
def consultar_materias_semestre(numero_semestre: int) -> dict:
    """
    Consulta las asignaturas de un semestre (1 a 9) del plan provisional
    de Ingeniería de Sistemas. Úsala cuando pregunten qué materias
    corresponden a cualquier semestre.
    """
    return consultar_api(
        f"/academicos/plan/semestres/{numero_semestre}"
    )


@mcp.tool
def buscar_asignatura_por_nombre(nombre: str) -> dict:
    """Busca una asignatura por nombre y devuelve sus créditos,
    descripción y profesores asociados. Úsala cuando pregunten
    quién dicta una materia o qué docentes tiene asignados."""
    nombre_codificado = quote(nombre, safe="")
    return consultar_api(
        f"/academicos/asignaturas/buscar/{nombre_codificado}"
    )


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8001)
