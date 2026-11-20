import os
import logging
import requests

logger = logging.getLogger("ibanu.monitoring")

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")


def enviar_evento(evento: str, servicio: str, estado: str):
    if not N8N_WEBHOOK_URL:
        logger.warning("Webhook de monitoreo no configurado.")
        return

    datos = {
        "proyecto": "iBanu",
        "evento": evento,
        "servicio": servicio,
        "estado": estado,
        "tipo_datos": "sinteticos"
    }

    try:
        requests.post(
            N8N_WEBHOOK_URL,
            json=datos,
            timeout=3
        )
    except requests.RequestException:
        logger.exception("No se pudo enviar el evento a n8n.")
