from fastapi import APIRouter, HTTPException

from backend.app.database import supabase

router = APIRouter(
    prefix="/academicos",
    tags=["Asignaturas y profesores"]
)


@router.get("/asignaturas/{codigo_asignatura}")
def consultar_asignatura(codigo_asignatura: str):

    respuesta = (
        supabase.table("asignaturas")
        .select("id,codigo,nombre,descripcion,creditos,activa")
        .eq("codigo", codigo_asignatura)
        .eq("activa", True)
        .limit(1)
        .execute()
    )

    if not respuesta.data:
        raise HTTPException(
            status_code=404,
            detail="Asignatura no encontrada"
        )

    asignatura = respuesta.data[0]

    relaciones = (
        supabase.table("profesores_asignaturas")
        .select("profesor_id")
        .eq("asignatura_id", asignatura["id"])
        .eq("activo", True)
        .execute()
    )

    profesor_ids = list(set(
        r["profesor_id"] for r in relaciones.data
    ))

    profesores = []

    if profesor_ids:
        resultado_profesores = (
            supabase.table("profesores")
            .select(
                "codigo_profesor,nombres,apellidos,departamento"
            )
            .in_("id", profesor_ids)
            .eq("es_sintetico", True)
            .eq("activo", True)
            .execute()
        )

        profesores = [
            {
                "codigo": p["codigo_profesor"],
                "nombre": p["nombres"] + " " + p["apellidos"],
                "departamento": p["departamento"]
            }
            for p in resultado_profesores.data
        ]

    return {
        "tipo_datos": "sinteticos",
        "asignatura": {
            "codigo": asignatura["codigo"],
            "nombre": asignatura["nombre"],
            "descripcion": asignatura["descripcion"],
            "creditos": asignatura["creditos"]
        },
        "total_profesores": len(profesores),
        "profesores": profesores
    }


@router.get("/profesores/buscar/{nombre}")
def buscar_profesor_por_nombre(nombre: str):

    respuesta = (
        supabase.table("profesores")
        .select(
            "id,codigo_profesor,nombres,apellidos,departamento"
        )
        .eq("es_sintetico", True)
        .eq("activo", True)
        .execute()
    )

    termino = nombre.strip().casefold()

    coincidencias = [
        p for p in respuesta.data
        if termino in (
            p["nombres"] + " " + p["apellidos"]
        ).casefold()
    ]

    if not coincidencias:
        raise HTTPException(
            status_code=404,
            detail="No se encontró un profesor con ese nombre"
        )

    return {
        "tipo_datos": "sinteticos",
        "total_profesores": len(coincidencias),
        "profesores": [
            {
                "codigo": p["codigo_profesor"],
                "nombre": p["nombres"] + " " + p["apellidos"],
                "departamento": p["departamento"]
            }
            for p in coincidencias
        ]
    }


@router.get("/profesores/{codigo_profesor}")
def consultar_profesor(codigo_profesor: str):

    respuesta = (
        supabase.table("profesores")
        .select(
            "id,codigo_profesor,nombres,apellidos,correo,departamento"
        )
        .eq("codigo_profesor", codigo_profesor)
        .eq("es_sintetico", True)
        .eq("activo", True)
        .limit(1)
        .execute()
    )

    if not respuesta.data:
        raise HTTPException(
            status_code=404,
            detail="Profesor no encontrado"
        )

    profesor = respuesta.data[0]

    relaciones = (
        supabase.table("profesores_asignaturas")
        .select("asignatura_id")
        .eq("profesor_id", profesor["id"])
        .eq("activo", True)
        .execute()
    )

    asignatura_ids = list(set(
        r["asignatura_id"] for r in relaciones.data
    ))

    asignaturas = []

    if asignatura_ids:
        resultado_asignaturas = (
            supabase.table("asignaturas")
            .select("codigo,nombre,creditos")
            .in_("id", asignatura_ids)
            .eq("activa", True)
            .execute()
        )

        asignaturas = resultado_asignaturas.data

    return {
        "tipo_datos": "sinteticos",
        "profesor": {
            "codigo": profesor["codigo_profesor"],
            "nombre": profesor["nombres"] + " " + profesor["apellidos"],
            "correo": profesor["correo"],
            "departamento": profesor["departamento"]
        },
        "total_asignaturas": len(asignaturas),
        "asignaturas": asignaturas
    }


@router.get("/asignaturas/buscar/{nombre}")
def buscar_asignatura_por_nombre(nombre: str):

    import unicodedata

    def normalizar(texto):
        texto = unicodedata.normalize("NFD", texto.casefold().strip())
        return "".join(
            c for c in texto if unicodedata.category(c) != "Mn"
        )

    respuesta = (
        supabase.table("asignaturas")
        .select("id,codigo,nombre,descripcion,creditos")
        .eq("activa", True)
        .execute()
    )

    termino = normalizar(nombre)

    coincidencias = [
        a for a in respuesta.data
        if termino in normalizar(a["nombre"])
    ]

    asignaturas = []

    for asignatura in coincidencias:
        relaciones = (
            supabase.table("profesores_asignaturas")
            .select("profesor_id")
            .eq("asignatura_id", asignatura["id"])
            .eq("activo", True)
            .execute()
        )

        profesor_ids = list(set(
            r["profesor_id"] for r in relaciones.data
        ))

        profesores = []

        if profesor_ids:
            resultado_profesores = (
                supabase.table("profesores")
                .select("codigo_profesor,nombres,apellidos,departamento")
                .in_("id", profesor_ids)
                .eq("es_sintetico", True)
                .eq("activo", True)
                .execute()
            )

            profesores = [
                {
                    "codigo": p["codigo_profesor"],
                    "nombre": p["nombres"] + " " + p["apellidos"],
                    "departamento": p["departamento"]
                }
                for p in resultado_profesores.data
            ]

        asignaturas.append({
            "codigo": asignatura["codigo"],
            "nombre": asignatura["nombre"],
            "descripcion": asignatura["descripcion"],
            "creditos": asignatura["creditos"],
            "total_profesores": len(profesores),
            "profesores": profesores
        })

    return {
        "tipo_datos": "sinteticos",
        "total_asignaturas": len(asignaturas),
        "asignaturas": asignaturas
    }


@router.get("/plan/semestres/{numero_semestre}")
def consultar_materias_por_semestre(numero_semestre: int):
    if numero_semestre < 1 or numero_semestre > 9:
        raise HTTPException(
            status_code=400,
            detail="El semestre debe estar entre 1 y 9."
        )

    plan = (
        supabase.table("planes_estudio")
        .select("id,codigo,nombre,version")
        .eq("codigo", "IBANU-PLAN-2026-PROV")
        .limit(1)
        .execute()
    )

    if not plan.data:
        raise HTTPException(
            status_code=404,
            detail="No se encontró el plan académico provisional."
        )

    datos_plan = plan.data[0]

    relaciones = (
        supabase.table("plan_asignaturas")
        .select("asignatura_id,semestre,obligatoria")
        .eq("plan_estudio_id", datos_plan["id"])
        .eq("semestre", numero_semestre)
        .execute()
    )

    materias = []

    for relacion in relaciones.data:
        asignatura = (
            supabase.table("asignaturas")
            .select("codigo,nombre,descripcion,creditos")
            .eq("id", relacion["asignatura_id"])
            .eq("activa", True)
            .limit(1)
            .execute()
        )

        if asignatura.data:
            materias.append({
                **asignatura.data[0],
                "semestre": numero_semestre,
                "obligatoria": relacion["obligatoria"]
            })

    return {
        "tipo_datos": "sinteticos",
        "plan": datos_plan["nombre"],
        "version": datos_plan["version"],
        "semestre": numero_semestre,
        "total_asignaturas": len(materias),
        "materias": materias,
        "nota": "Plan académico provisional; no representa una oferta oficial de la UNAB."
    }
