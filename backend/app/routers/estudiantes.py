from fastapi import APIRouter, HTTPException

from backend.app.database import supabase

router = APIRouter(
    prefix="/estudiantes",
    tags=["Estudiantes"]
)


@router.get("/{codigo_estudiante}")
def consultar_estudiante(codigo_estudiante: str):
    respuesta = (
        supabase.table("estudiantes")
        .select(
            "codigo_estudiante,nombres,apellidos,estado,es_sintetico"
        )
        .eq("codigo_estudiante", codigo_estudiante)
        .eq("es_sintetico", True)
        .limit(1)
        .execute()
    )

    if not respuesta.data:
        raise HTTPException(
            status_code=404,
            detail="Estudiante no encontrado"
        )

    return respuesta.data[0]


@router.get("/{codigo_estudiante}/horario")
def consultar_horario_estudiante(codigo_estudiante: str):
    estudiante = (
        supabase.table("estudiantes")
        .select("id,codigo_estudiante,nombres,apellidos,es_sintetico")
        .eq("codigo_estudiante", codigo_estudiante)
        .eq("es_sintetico", True)
        .limit(1)
        .execute()
    )

    if not estudiante.data:
        raise HTTPException(
            status_code=404,
            detail="Estudiante sintético no encontrado"
        )

    datos_estudiante = estudiante.data[0]

    matriculas = (
        supabase.table("matriculas")
        .select("grupo_id,estado,fecha_matricula")
        .eq("estudiante_id", datos_estudiante["id"])
        .eq("estado", "activa")
        .execute()
    )

    horario = []

    for matricula in matriculas.data:
        grupo = (
            supabase.table("grupos")
            .select("*")
            .eq("id", matricula["grupo_id"])
            .eq("es_sintetico", True)
            .limit(1)
            .execute()
        )

        if not grupo.data:
            continue

        datos_grupo = grupo.data[0]

        asignatura = (
            supabase.table("asignaturas")
            .select("codigo,nombre,creditos")
            .eq("id", datos_grupo["asignatura_id"])
            .limit(1)
            .execute()
        )

        periodo = (
            supabase.table("periodos_academicos")
            .select("codigo,nombre")
            .eq("id", datos_grupo["periodo_id"])
            .limit(1)
            .execute()
        )

        horarios = (
            supabase.table("horarios_grupos")
            .select("dia_semana,hora_inicio,hora_fin,lugar")
            .eq("grupo_id", datos_grupo["id"])
            .execute()
        )

        relaciones = (
            supabase.table("grupos_profesores")
            .select("profesor_id,rol")
            .eq("grupo_id", datos_grupo["id"])
            .execute()
        )

        profesores = []

        for relacion in relaciones.data:
            profesor = (
                supabase.table("profesores")
                .select("codigo_profesor,nombres,apellidos")
                .eq("id", relacion["profesor_id"])
                .eq("es_sintetico", True)
                .limit(1)
                .execute()
            )

            if profesor.data:
                profesores.append({
                    **profesor.data[0],
                    "rol": relacion["rol"]
                })

        horario.append({
            "grupo": datos_grupo["codigo_grupo"],
            "asignatura": asignatura.data[0] if asignatura.data else None,
            "periodo": periodo.data[0] if periodo.data else None,
            "profesores": profesores,
            "horarios": horarios.data,
            "modalidad": datos_grupo["modalidad"],
            "lugar": datos_grupo["lugar"],
            "fecha_matricula": matricula["fecha_matricula"]
        })

    return {
        "tipo_datos": "sinteticos",
        "estudiante": {
            "codigo": datos_estudiante["codigo_estudiante"],
            "nombre": (
                datos_estudiante["nombres"] + " " +
                datos_estudiante["apellidos"]
            )
        },
        "total_asignaturas": len(horario),
        "horario": horario,
        "mensaje": (
            "Horario consultado correctamente."
            if horario
            else "El estudiante no tiene asignaturas matriculadas activas."
        )
    }


@router.get("/{codigo_estudiante}/historial")
def consultar_historial_academico(codigo_estudiante: str):
    estudiante = (
        supabase.table("estudiantes")
        .select("id,codigo_estudiante,nombres,apellidos,semestre_actual")
        .eq("codigo_estudiante", codigo_estudiante)
        .eq("es_sintetico", True)
        .limit(1)
        .execute()
    )

    if not estudiante.data:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    alumno = estudiante.data[0]

    matriculas = (
        supabase.table("matriculas")
        .select("id,grupo_id,estado,fecha_matricula")
        .eq("estudiante_id", alumno["id"])
        .execute()
    )

    historial = []

    for matricula in matriculas.data:
        grupo = (
            supabase.table("grupos")
            .select("asignatura_id,periodo_id,codigo_grupo")
            .eq("id", matricula["grupo_id"])
            .eq("es_sintetico", True)
            .limit(1)
            .execute()
        )

        if not grupo.data:
            continue

        datos_grupo = grupo.data[0]

        asignatura = (
            supabase.table("asignaturas")
            .select("codigo,nombre,creditos")
            .eq("id", datos_grupo["asignatura_id"])
            .limit(1)
            .execute()
        )

        periodo = (
            supabase.table("periodos_academicos")
            .select("codigo,nombre,anio,semestre")
            .eq("id", datos_grupo["periodo_id"])
            .limit(1)
            .execute()
        )

        notas = (
            supabase.table("notas")
            .select("componente,calificacion,porcentaje")
            .eq("matricula_id", matricula["id"])
            .execute()
        )

        historial.append({
            "asignatura": asignatura.data[0] if asignatura.data else None,
            "periodo": periodo.data[0] if periodo.data else None,
            "grupo": datos_grupo["codigo_grupo"],
            "estado": matricula["estado"],
            "fecha_matricula": matricula["fecha_matricula"],
            "notas": notas.data
        })

    return {
        "tipo_datos": "sinteticos",
        "estudiante": {
            "codigo": alumno["codigo_estudiante"],
            "nombre": alumno["nombres"] + " " + alumno["apellidos"],
            "semestre_actual": alumno["semestre_actual"]
        },
        "total_matriculas": len(historial),
        "historial": historial
    }


@router.get("/{codigo_estudiante}/materias-pendientes")
def consultar_materias_pendientes(codigo_estudiante: str):
    estudiante = (
        supabase.table("estudiantes")
        .select("id,codigo_estudiante,plan_estudio_id,semestre_actual")
        .eq("codigo_estudiante", codigo_estudiante)
        .eq("es_sintetico", True)
        .limit(1)
        .execute()
    )

    if not estudiante.data:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    alumno = estudiante.data[0]

    plan = (
        supabase.table("plan_asignaturas")
        .select("asignatura_id,semestre,obligatoria")
        .eq("plan_estudio_id", alumno["plan_estudio_id"])
        .lte("semestre", alumno["semestre_actual"])
        .execute()
    )

    matriculas = (
        supabase.table("matriculas")
        .select("grupo_id,estado")
        .eq("estudiante_id", alumno["id"])
        .execute()
    )

    estados_por_asignatura = {}

    for matricula in matriculas.data:
        grupo = (
            supabase.table("grupos")
            .select("asignatura_id")
            .eq("id", matricula["grupo_id"])
            .eq("es_sintetico", True)
            .limit(1)
            .execute()
        )

        if grupo.data:
            asignatura_id = grupo.data[0]["asignatura_id"]
            estados_por_asignatura.setdefault(asignatura_id, []).append(
                matricula["estado"]
            )

    pendientes = []
    cursando = []
    aprobadas = []

    for materia_plan in plan.data:
        asignatura_id = materia_plan["asignatura_id"]

        asignatura = (
            supabase.table("asignaturas")
            .select("codigo,nombre,creditos")
            .eq("id", asignatura_id)
            .limit(1)
            .execute()
        )

        if not asignatura.data:
            continue

        estados = estados_por_asignatura.get(asignatura_id, [])

        materia = {
            **asignatura.data[0],
            "semestre_plan": materia_plan["semestre"],
            "obligatoria": materia_plan["obligatoria"]
        }

        if "aprobada" in estados:
            aprobadas.append(materia)
        elif "activa" in estados:
            cursando.append(materia)
        elif "reprobada" in estados:
            materia["estado_academico"] = "reprobada"
            pendientes.append(materia)
        else:
            materia["estado_academico"] = "no_cursada"
            pendientes.append(materia)

    return {
        "tipo_datos": "sinteticos",
        "estudiante": alumno["codigo_estudiante"],
        "semestre_actual": alumno["semestre_actual"],
        "total_aprobadas": len(aprobadas),
        "total_cursando": len(cursando),
        "total_pendientes": len(pendientes),
        "materias_aprobadas": aprobadas,
        "materias_cursando": cursando,
        "materias_pendientes": pendientes,
        "nota": "El plan académico es provisional y no contiene prerrequisitos oficiales."
    }


@router.get("/{codigo_estudiante}/siguiente-semestre")
def consultar_siguiente_semestre(codigo_estudiante: str):
    estudiante = (
        supabase.table("estudiantes")
        .select("id,codigo_estudiante,plan_estudio_id,semestre_actual")
        .eq("codigo_estudiante", codigo_estudiante)
        .eq("es_sintetico", True)
        .limit(1)
        .execute()
    )

    if not estudiante.data:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    alumno = estudiante.data[0]
    siguiente_semestre = alumno["semestre_actual"] + 1

    if siguiente_semestre > 9:
        return {
            "tipo_datos": "sinteticos",
            "estudiante": alumno["codigo_estudiante"],
            "semestre_actual": alumno["semestre_actual"],
            "siguiente_semestre": None,
            "total_asignaturas": 0,
            "materias": [],
            "mensaje": "El estudiante ya se encuentra en el último semestre del plan."
        }

    plan = (
        supabase.table("plan_asignaturas")
        .select("asignatura_id,semestre,obligatoria")
        .eq("plan_estudio_id", alumno["plan_estudio_id"])
        .eq("semestre", siguiente_semestre)
        .execute()
    )

    materias = []

    for materia_plan in plan.data:
        asignatura = (
            supabase.table("asignaturas")
            .select("id,codigo,nombre,creditos")
            .eq("id", materia_plan["asignatura_id"])
            .limit(1)
            .execute()
        )

        if not asignatura.data:
            continue

        datos_asignatura = asignatura.data[0]

        relaciones = (
            supabase.table("profesores_asignaturas")
            .select("profesor_id")
            .eq("asignatura_id", datos_asignatura["id"])
            .eq("activo", True)
            .execute()
        )

        profesores = []

        for relacion in relaciones.data:
            profesor = (
                supabase.table("profesores")
                .select("codigo_profesor,nombres,apellidos")
                .eq("id", relacion["profesor_id"])
                .eq("es_sintetico", True)
                .limit(1)
                .execute()
            )

            if profesor.data:
                profesores.append(profesor.data[0])

        materias.append({
            "codigo": datos_asignatura["codigo"],
            "nombre": datos_asignatura["nombre"],
            "creditos": datos_asignatura["creditos"],
            "semestre_plan": materia_plan["semestre"],
            "obligatoria": materia_plan["obligatoria"],
            "profesores_asociados": profesores
        })

    return {
        "tipo_datos": "sinteticos",
        "estudiante": alumno["codigo_estudiante"],
        "semestre_actual": alumno["semestre_actual"],
        "siguiente_semestre": siguiente_semestre,
        "total_asignaturas": len(materias),
        "materias": materias,
        "nota": (
            "Estas son asignaturas del siguiente nivel del plan provisional. "
            "Los profesores son asociaciones académicas sintéticas; "
            "no constituyen una confirmación de asignación a un grupo. "
            "No hay prerrequisitos oficiales registrados."
        )
    }
