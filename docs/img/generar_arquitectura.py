"""Genera docs/img/arquitectura.png y arquitectura.svg con matplotlib (sin dependencias externas)."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

AQUI = os.path.dirname(os.path.abspath(__file__))
fig, ax = plt.subplots(figsize=(17, 10.5))
ax.set_xlim(0, 170)
ax.set_ylim(0, 105)
ax.axis("off")

C = {"app": "#F79800", "n8n": "#EA4B71", "guard": "#C0392B", "ia": "#6C3FC5",
     "mcp": "#0B7285", "db": "#2F9E44", "rag": "#1971C2", "log": "#868E96"}


def zona(x, y, w, h, titulo, color):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.5",
                                fc=color, ec=color, alpha=0.08, lw=1.5))
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.5",
                                fc="none", ec=color, lw=1.6))
    ax.text(x + 1.2, y + h - 1.6, titulo, fontsize=11, fontweight="bold", color=color, va="top")


def caja(x, y, w, h, texto, color, fs=8.6):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2,rounding_size=1",
                                fc="white", ec=color, lw=1.8))
    ax.text(x + w / 2, y + h / 2, texto, ha="center", va="center", fontsize=fs, linespacing=1.25)
    return (x, y, w, h)


def flecha(p, q, color="#343A40", estilo="-|>", ls="-", rad=0.0, texto=None, off=(0, 1.2)):
    a = FancyArrowPatch(p, q, arrowstyle=estilo, mutation_scale=13, lw=1.5, color=color,
                        linestyle=ls, connectionstyle=f"arc3,rad={rad}")
    ax.add_patch(a)
    if texto:
        ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], texto, fontsize=7.8,
                ha="center", color=color, style="italic")


ax.text(85, 102.5, "iBanú: arquitectura del sistema", ha="center", fontsize=17, fontweight="bold")

# Cliente
zona(1, 52, 24, 44, "Cliente", C["app"])
caja(3.5, 78, 19, 9, "Estudiante\n(iPhone)", C["app"])
caja(3.5, 58, 19, 15, "App móvil Expo\n(Expo Go)\nCódigo de estudiante,\n4 acciones rápidas,\nchat libre", C["app"], 8)
flecha((13, 78), (13, 73), C["app"])

# n8n
zona(32, 36, 78, 62, "n8n Cloud: un solo flujo con cuatro disparadores", C["n8n"])
w1 = caja(34, 80, 16, 9, "Webhook POST\n/ibanu/orientador\n(X-Ibanu-Token)", C["n8n"], 7.8)
w2 = caja(53, 80, 14, 9, "Validar\nsolicitud\n(401, 400)", C["n8n"], 8)
w3 = caja(70, 80, 15, 9, "Guardrail de\nentrada\n(nativo n8n)", C["guard"], 8)
w4 = caja(89, 80, 18, 9, "Bloqueo amable\n(inyección, datos,\nfuera de tema)", C["guard"], 7.6)
ag = caja(58, 59, 34, 15, "Agente Orientador iBanú (Tools Agent)\nGemini 3.5 Flash Lite, temperatura 0,3\nMemoria Simple Memory\n(ventana 10, estudiante + sesión)", C["ia"], 8.2)
w5 = caja(34, 62, 20, 11, "Respuesta de contingencia\n(si falla el agente)", C["n8n"], 8)
w6 = caja(63, 40, 20, 12, "Guardrail de salida\n(sanitiza), extraer\nfuentes y armar JSON", C["guard"], 7.8)
w7 = caja(86, 47, 22, 8, "Responder al chat\n{ok, respuesta, fuentes}", C["n8n"], 7.8)
w8 = caja(86, 37.5, 22, 7, "Registrar turno + latencia", C["log"], 7.8)
caja(34, 40, 26, 12, "Webhook GET\n/ibanu/rag-prueba\n(evidencia de recuperación)", C["rag"], 7.8)

flecha((22.5, 68), (34, 84.5), C["app"], estilo="<|-|>", texto="HTTPS: POST y JSON", off=(-2, 2.5))
flecha((50, 84.5), (53, 84.5))
flecha((67, 84.5), (70, 84.5))
flecha((85, 84.5), (89, 84.5), C["guard"], texto="bloquea", off=(0, 1.4))
flecha((77, 80), (75, 74), texto="pasa", off=(2.5, 0.2))
flecha((58, 66), (54, 67), C["n8n"], ls="--", texto="error", off=(-1, 3.2))
flecha((73, 59), (73, 52))
flecha((83, 46), (86, 50.5))
flecha((97, 47), (97, 44.5), C["log"], texto="en paralelo", off=(8, 0))
flecha((98, 80), (98, 55), C["guard"], ls=":", texto="bloqueado", off=(5.5, 0))

# Herramientas
zona(117, 56, 52, 42, "Herramientas del agente", C["mcp"])
m1 = caja(119, 77, 22, 14, "Servidor MCP público\nVM Azure mv-parcial2\nproxy :9001 con X-API-Key\n13 herramientas de lectura", C["mcp"], 8)
m2 = caja(145, 77, 22, 14, "MCP interno :8001\n(FastMCP)\n->\nBackend FastAPI :8000", C["mcp"], 8)
flecha((141, 84), (145, 84), C["mcp"], texto="HTTP", off=(0, 1.3))
caja(119, 59, 22, 14, "Supabase Vector Store\n(herramienta del agente)\nk = 5, con metadatos", C["rag"], 8)
caja(145, 59, 22, 14, "Embeddings Google Gemini\ngemini-embedding-001\n3072 dimensiones", C["rag"], 8)
flecha((141, 66), (145, 66), C["rag"])
flecha((92, 71), (119, 84), C["mcp"], texto="MCP HTTP Streamable", off=(2, 3.2))
flecha((92, 64), (119, 65), C["rag"], texto="consulta semántica", off=(5, -2.8))

# Datos
zona(117, 6, 52, 46, "Supabase Cloud (PostgreSQL + pgvector)", C["db"])
caja(119, 28, 22, 17, "Modelo académico\nestudiantes, matriculas,\nnotas, asignaturas,\nplan_asignaturas,\nprerrequisitos,\nprofesores, grupos", C["db"], 7.8)
caja(145, 28, 22, 17, "ibanu_conocimiento\n(content, metadata,\nembedding vector(3072))\nbúsqueda exacta por coseno\nibanu_buscar_conocimiento()", C["rag"], 7.6)
caja(119, 9, 22, 14, "ibanu_conversaciones\nmensaje, respuesta,\nbloqueado, motivo,\nlatencia_ms", C["log"], 7.8)
caja(145, 9, 22, 14, "documentos_academicos\nfragmentos_documento\n(41 documentos,\n341 fragmentos de origen)", C["db"], 7.6)
flecha((156, 77), (131, 45), C["mcp"], rad=0.15, texto="REST", off=(-8, 0))
flecha((130, 59), (156, 45), C["rag"], ls="--")
ax.text(142, 53.5, "", fontsize=1)

# Registro
flecha((108, 40), (119, 16), C["log"], rad=0.15, texto="INSERT", off=(-2, -2))

# Indexación y subida
zona(1, 6, 108, 26, "Ramas de ingesta (mismo flujo): indexación manual y subida de documentos", C["rag"])
i1 = caja(3, 15, 15, 9, "Disparador manual\nIndexar base\ndocumental", C["rag"], 7.8)
i2 = caja(21, 15, 17, 9, "Leer documentos y\nfragmentos de\nSupabase", C["db"], 7.8)
i3 = caja(41, 15, 17, 9, "Reconstruir texto\nsin solape y dividir\n(artículo / documento)", C["rag"], 7.8)
i4 = caja(61, 15, 21, 9, "Divisor recursivo\n1500 caracteres,\nsolape 150", C["rag"], 7.8)
i5 = caja(85, 15, 21, 9, "Embeddings 3072 +\nInsert en Vector Store\n(lotes de 25, pausa 30 s)", C["rag"], 7.6)
u1 = caja(3, 8, 20, 5.5, "Formulario: título, tipo, PDF", C["rag"], 7.6)
u2 = caja(26, 8, 22, 5.5, "Extraer texto del PDF", C["rag"], 7.6)
for a, b in [((18, 19.5), (21, 19.5)), ((38, 19.5), (41, 19.5)), ((58, 19.5), (61, 19.5)), ((82, 19.5), (85, 19.5)), ((23, 10.8), (26, 10.8))]:
    flecha(a, b, C["rag"])
flecha((48, 10.8), (52, 15), C["rag"], rad=-0.2)
flecha((106, 21), (145, 31), C["rag"], rad=-0.15, texto="INSERT vectores", off=(-5, 4))

# Leyenda
ax.text(2, 1.5, "Flechas continuas: flujo de datos. Discontinuas: caminos alternos (error, ingesta). Datos académicos sintéticos; plan de estudios provisional.",
        fontsize=8, color="#495057")

fig.savefig(os.path.join(AQUI, "arquitectura.png"), dpi=130, bbox_inches="tight", facecolor="white")
fig.savefig(os.path.join(AQUI, "arquitectura.svg"), bbox_inches="tight", facecolor="white")
print("listo")
