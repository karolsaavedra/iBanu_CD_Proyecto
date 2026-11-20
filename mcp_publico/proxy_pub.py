"""Proxy publico del MCP de iBanu: valida X-API-Key y reenvia en streaming al MCP interno."""
import hmac
import os

import httpx
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

CLAVE = os.environ["MCP_PUBLIC_API_KEY"]
UPSTREAM = os.environ.get("UPSTREAM_MCP", "http://172.18.0.1:8001").rstrip("/")
SALTAR = {"host", "x-api-key", "content-length", "connection", "keep-alive",
          "transfer-encoding", "upgrade", "proxy-connection", "te", "trailer"}
SALTAR_RESP = {"content-length", "transfer-encoding", "connection", "keep-alive"}

cliente = httpx.AsyncClient(timeout=httpx.Timeout(None, connect=10.0))


async def _responder(send, status, cuerpo, tipo=b"application/json"):
    await send({"type": "http.response.start", "status": status,
                "headers": [(b"content-type", tipo), (b"content-length", str(len(cuerpo)).encode())]})
    await send({"type": "http.response.body", "body": cuerpo})


async def app(scope, receive, send):
    if scope["type"] == "lifespan":
        while True:
            msg = await receive()
            if msg["type"] == "lifespan.startup":
                await send({"type": "lifespan.startup.complete"})
            elif msg["type"] == "lifespan.shutdown":
                await cliente.aclose()
                await send({"type": "lifespan.shutdown.complete"})
                return
    if scope["type"] != "http":
        return

    cab = [(k.decode().lower(), v.decode()) for k, v in scope["headers"]]
    dado = next((v for k, v in cab if k == "x-api-key"), "")
    if not hmac.compare_digest(dado.encode(), CLAVE.encode()):
        await _responder(send, 401, b'{"error":"no autorizado"}')
        return
    if not scope["path"].startswith("/mcp"):
        await _responder(send, 404, b'{"error":"no encontrado"}')
        return

    async def cuerpo():
        while True:
            msg = await receive()
            if msg["type"] == "http.request":
                if msg.get("body"):
                    yield msg["body"]
                if not msg.get("more_body"):
                    return
            elif msg["type"] == "http.disconnect":
                return

    url = UPSTREAM + scope["path"]
    if scope["query_string"]:
        url += "?" + scope["query_string"].decode()
    cabs = {k: v for k, v in cab if k not in SALTAR}
    try:
        req = cliente.build_request(scope["method"], url, headers=cabs, content=cuerpo())
        r = await cliente.send(req, stream=True)
    except httpx.HTTPError:
        await _responder(send, 502, b'{"error":"mcp interno no disponible"}')
        return
    try:
        hs = [(k.encode(), v.encode()) for k, v in r.headers.items() if k.lower() not in SALTAR_RESP]
        await send({"type": "http.response.start", "status": r.status_code, "headers": hs})
        async for trozo in r.aiter_raw():
            await send({"type": "http.response.body", "body": trozo, "more_body": True})
        await send({"type": "http.response.body", "body": b""})
    finally:
        await r.aclose()
