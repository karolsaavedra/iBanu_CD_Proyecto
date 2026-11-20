# Proxy público del MCP de iBanú

Servicio pequeño (ASGI con `httpx`) que expone el servidor MCP interno a n8n Cloud. Valida la cabecera `X-API-Key` (comparación en tiempo constante) y reenvía en streaming la petición a `UPSTREAM_MCP` (por defecto `http://172.18.0.1:8001`), conservando cabeceras como `Mcp-Session-Id`. No modifica el MCP original. Sin clave o con clave incorrecta responde `401`; rutas que no empiezan por `/mcp`, `404`; si el MCP interno no responde, `502`.

| Archivo | Contenido |
|---|---|
| `proxy_pub.py` | Código del proxy |
| `ibanu-mcp-publico.service` | Unidad de systemd tal como corre en la VM (puerto 9001) |
| `.env.example` | Variables necesarias (con valores de ejemplo) |

## Instalación en la VM

```bash
mkdir -p ~/ibanu-mcp-publico && cp proxy_pub.py ~/ibanu-mcp-publico/
cp .env.example ~/ibanu-mcp-publico/.env && chmod 600 ~/ibanu-mcp-publico/.env   # editar la clave
# Usa el entorno virtual del MCP (necesita httpx, python-dotenv y uvicorn)
sudo cp ibanu-mcp-publico.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now ibanu-mcp-publico
```

Abrir el puerto TCP 9001 de entrada en el grupo de seguridad (NSG) de Azure. Comprobación:

```bash
curl -i http://<IP_VM>:9001/mcp                          # 401 sin clave
curl -i -H "X-API-Key: <clave>" http://<IP_VM>:9001/mcp  # responde el MCP
```

La clave real vive solo en el `.env` de la VM y en la credencial "iBanu MCP" de n8n.
