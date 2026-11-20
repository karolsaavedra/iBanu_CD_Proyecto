
import logging

from fastapi import FastAPI, HTTPException, Request

from backend.app.routers import (
    estudiantes,
    turnos,
    grupos,
    academicos,
    chat
)
from backend.app.database import supabase
from backend.app.monitoring import enviar_evento

logger = logging.getLogger("ibanu.api")

app = FastAPI(
    title="iBanú API",
    description="API del chatbot académico iBanú",
    version="1.0.0"
)


@app.middleware("http")
async def monitorear_solicitudes(request: Request, call_next):
    try:
        response = await call_next(request)

        if request.url.path not in ("/", "/health"):
            enviar_evento(
                evento="consulta_api",
                servicio=request.scope["route"].path if request.scope.get("route") else "ruta_desconocida",
                estado=str(response.status_code)
            )

        return response

    except Exception:
        enviar_evento(
            evento="error_api",
            servicio=request.scope["route"].path if request.scope.get("route") else "ruta_desconocida",
            estado="500"
        )
        logger.exception("Error procesando solicitud API")
        raise


app.include_router(estudiantes.router)
app.include_router(turnos.router)
app.include_router(grupos.router)
app.include_router(academicos.router)
app.include_router(chat.router)


@app.get("/")
def inicio():
    return {
        "proyecto": "iBanú",
        "mensaje": "API académica en funcionamiento",
        "estado": "activo"
    }


@app.get("/health")
def health():
    return {
        "estado": "activo",
        "servicio": "backend"
    }


@app.get("/health/database")
def health_database():
    try:
        supabase.table("periodos_academicos") \
            .select("id") \
            .eq("es_sintetico", True) \
            .limit(1) \
            .execute()

        return {
            "estado": "conectado",
            "base_datos": "Supabase",
            "consulta": "exitosa"
        }

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="No fue posible consultar Supabase"
        ) from error

