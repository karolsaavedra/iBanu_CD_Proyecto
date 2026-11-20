from fastapi import APIRouter, HTTPException

from backend.app.database import supabase

router = APIRouter(
    prefix="/periodos",
    tags=["Oferta académica"]
)

DIAS = {
    1: "Lunes",
    2: "Martes",
    3: "Miércoles",
    4: "Jueves",
    5: "Viernes",
    6: "Sábado",
    7: "Domingo"
}


@router.get("/{codigo_periodo}/grupos")
def consultar_grupos(codigo_periodo: str):

    periodo_respuesta = (
        supabase.table("periodos_academicos")
        .select("id,codigo,nombre")
        .eq("codigo", codigo_periodo)
        .eq("es_sintetico", True)
        .limit(1)
        .execute()
    )

    if not periodo_respuesta.data:
        raise HTTPException(
            status_code=404,
            detail="Periodo académico no encontrado"
        )

    periodo = periodo_respuesta.data[0]

    grupos_respuesta = (
        supabase.table("grupos")
        .select(
            "id,asignatura_id,codigo_grupo,cupo,modalidad,lugar,estado"
        )
        .eq("periodo_id", periodo["id"])
        .eq("es_sintetico", True)
        .eq("estado", "activo")
        .order("codigo_grupo")
        .execute()
    )

    grupos = grupos_respuesta.data

    if not grupos:
        return {
            "periodo": periodo["codigo"],
            "total_grupos": 0,
            "grupos": []
        }

    grupo_ids = [g["id"] for g in grupos]
    asignatura_ids = list(set(g["asignatura_id"] for g in grupos))

    asignaturas = (
        supabase.table("asignaturas")
        .select("id,codigo,nombre,creditos")
        .in_("id", asignatura_ids)
        .execute()
    )

    asignaturas_por_id = {
        a["id"]: a for a in asignaturas.data
    }

    relaciones = (
        supabase.table("grupos_profesores")
        .select("grupo_id,profesor_id,rol")
        .in_("grupo_id", grupo_ids)
        .execute()
    )

    profesor_ids = list(set(
        r["profesor_id"] for r in relaciones.data
    ))

    profesores = []

    if profesor_ids:
        profesores_respuesta = (
            supabase.table("profesores")
            .select(
                "id,codigo_profesor,nombres,apellidos,departamento"
            )
            .in_("id", profesor_ids)
            .eq("es_sintetico", True)
            .execute()
        )
        profesores = profesores_respuesta.data

    profesores_por_id = {
        p["id"]: p for p in profesores
    }

    horarios = (
        supabase.table("horarios_grupos")
        .select(
            "grupo_id,dia_semana,hora_inicio,hora_fin,lugar,observaciones"
        )
        .in_("grupo_id", grupo_ids)
        .order("dia_semana")
        .execute()
    )

    matriculas = (
        supabase.table("matriculas")
        .select("grupo_id")
        .in_("grupo_id", grupo_ids)
        .eq("estado", "activa")
        .execute()
    )

    ocupacion = {}

    for matricula in matriculas.data:
        grupo_id = matricula["grupo_id"]
        ocupacion[grupo_id] = ocupacion.get(grupo_id, 0) + 1

    profesores_por_grupo = {}

    for relacion in relaciones.data:
        profesor = profesores_por_id.get(relacion["profesor_id"])

        if profesor:
            profesores_por_grupo.setdefault(
                relacion["grupo_id"], []
            ).append({
                "codigo": profesor["codigo_profesor"],
                "nombre": (
                    profesor["nombres"] + " " +
                    profesor["apellidos"]
                ),
                "departamento": profesor["departamento"],
                "rol": relacion["rol"]
            })

    horarios_por_grupo = {}

    for horario in horarios.data:
        horarios_por_grupo.setdefault(
            horario["grupo_id"], []
        ).append({
            "dia": DIAS.get(
                horario["dia_semana"], "No definido"
            ),
            "hora_inicio": horario["hora_inicio"],
            "hora_fin": horario["hora_fin"],
            "lugar": horario["lugar"],
            "observaciones": horario["observaciones"]
        })

    resultado = []

    for grupo in grupos:
        grupo_id = grupo["id"]
        asignatura = asignaturas_por_id.get(
            grupo["asignatura_id"]
        )

        if not asignatura:
            continue

        matriculados = ocupacion.get(grupo_id, 0)
        cupo = grupo["cupo"]

        resultado.append({
            "asignatura": {
                "codigo": asignatura["codigo"],
                "nombre": asignatura["nombre"],
                "creditos": asignatura["creditos"]
            },
            "grupo": grupo["codigo_grupo"],
            "modalidad": grupo["modalidad"],
            "lugar": grupo["lugar"],
            "capacidad": cupo,
            "matriculados": matriculados,
            "cupos_disponibles": (
                max(cupo - matriculados, 0)
                if cupo is not None else None
            ),
            "profesores": profesores_por_grupo.get(
                grupo_id, []
            ),
            "horarios": horarios_por_grupo.get(
                grupo_id, []
            )
        })

    return {
        "periodo": periodo["codigo"],
        "nombre_periodo": periodo["nombre"],
        "total_grupos": len(resultado),
        "grupos": resultado
    }
