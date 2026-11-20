
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException

from backend.app.database import supabase

router = APIRouter(
    prefix="/estudiantes",
    tags=["Turnos de inscripción"]
)

ZONA_COLOMBIA = ZoneInfo("America/Bogota")


def convertir_hora(fecha):
    fecha = datetime.fromisoformat(
        fecha.replace("Z", "+00:00")
    )
    return fecha.astimezone(ZONA_COLOMBIA)


def formato_hora(fecha):
    hora = fecha.hour
    minutos = fecha.minute
    periodo = "a. m." if hora < 12 else "p. m."

    hora_12 = hora % 12 or 12

    return f"{hora_12}:{minutos:02d} {periodo}"


@router.get("/{codigo_estudiante}/turnos")
def consultar_turnos(codigo_estudiante: str):

    estudiante = (
        supabase.table("estudiantes")
        .select("id,codigo_estudiante")
        .eq("codigo_estudiante", codigo_estudiante)
        .eq("es_sintetico", True)
        .limit(1)
        .execute()
    )

    if not estudiante.data:
        raise HTTPException(
            status_code=404,
            detail="Estudiante no encontrado"
        )

    estudiante_id = estudiante.data[0]["id"]

    turnos = (
        supabase.table("turnos_inscripcion")
        .select(
            "id,periodo_id,fecha_inicio,fecha_fin,estado,observaciones"
        )
        .eq("estudiante_id", estudiante_id)
        .order("fecha_inicio")
        .execute()
    )

    if not turnos.data:
        return {
            "codigo_estudiante": codigo_estudiante,
            "plataforma_referencia": "Cosmos",
            "tipo_datos": "sinteticos",
            "total_turnos": 0,
            "turnos": []
        }

    periodos = (
        supabase.table("periodos_academicos")
        .select("id,codigo,nombre")
        .eq("es_sintetico", True)
        .execute()
    )

    periodos_por_id = {
        periodo["id"]: periodo
        for periodo in periodos.data
    }

    periodo_ids = list({
        turno["periodo_id"]
        for turno in turnos.data
    })

    todos_turnos = (
        supabase.table("turnos_inscripcion")
        .select("id,periodo_id,fecha_inicio")
        .in_("periodo_id", periodo_ids)
        .order("fecha_inicio")
        .execute()
    )

    numeros_turno = {}
    contador_por_periodo = {}

    for turno_general in todos_turnos.data:
        periodo_id = turno_general["periodo_id"]

        contador_por_periodo[periodo_id] = (
            contador_por_periodo.get(periodo_id, 0) + 1
        )

        numeros_turno[turno_general["id"]] = (
            contador_por_periodo[periodo_id]
        )

    resultado = []

    for turno in turnos.data:
        periodo = periodos_por_id.get(turno["periodo_id"])

        if not periodo:
            continue

        inicio = convertir_hora(turno["fecha_inicio"])
        fin = convertir_hora(turno["fecha_fin"])

        resultado.append({
            "numero_turno": numeros_turno.get(turno["id"]),
            "nombre_turno": (
                f"Turno {numeros_turno.get(turno['id'])}"
            ),
            "periodo": periodo["codigo"],
            "nombre_periodo": periodo["nombre"],
            "fecha": inicio.strftime("%d/%m/%Y"),
            "hora_inicio": formato_hora(inicio),
            "hora_fin": formato_hora(fin),
            "fecha_inicio": turno["fecha_inicio"],
            "fecha_fin": turno["fecha_fin"],
            "estado": turno["estado"],
            "plataforma": "Cosmos",
            "observaciones": turno["observaciones"]
        })

    return {
        "codigo_estudiante": codigo_estudiante,
        "plataforma_referencia": "Cosmos",
        "tipo_datos": "sinteticos",
        "nota": (
            "Información académica simulada para iBanú. "
            "No existe conexión directa con Cosmos."
        ),
        "total_turnos": len(resultado),
        "turnos": resultado
    }

