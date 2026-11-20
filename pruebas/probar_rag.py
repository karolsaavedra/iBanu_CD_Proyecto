"""Demostración de la recuperación del RAG: consulta GET /webhook/ibanu/rag-prueba.
Uso:  python probar_rag.py                 (consultas de ejemplo)
      python probar_rag.py "mi consulta"   (una consulta)
Variables: IBANU_TOKEN (obligatoria), IBANU_BASE (opcional).
"""
import json, os, sys, time, urllib.parse, urllib.request

BASE = os.environ.get("IBANU_BASE", "https://ksaavedra363.app.n8n.cloud/webhook")
TOKEN = os.environ["IBANU_TOKEN"]
K = 3
EJEMPLOS = [
    "¿Puedo cancelar una materia y hasta cuándo?",
    "¿Qué pasa si pierdo una asignatura dos veces?",
    "¿Qué contenidos se ven en Estructura de Datos?",
    "¿Qué prerrequisito tiene Internet de las Cosas?",
    "¿Cómo se evalúa Cálculo Diferencial?",
    "¿Qué competencias digitales debe desarrollar un estudiante de ingeniería?",
]

def buscar(q):
    url = f"{BASE}/ibanu/rag-prueba?" + urllib.parse.urlencode({"q": q, "k": K})
    req = urllib.request.Request(url, headers={"X-Ibanu-Token": TOKEN})
    t = time.time()
    with urllib.request.urlopen(req, timeout=90) as r:
        datos = json.load(r)
    return datos["resultados"], time.time() - t

for q in (sys.argv[1:] or EJEMPLOS):
    res, seg = buscar(q)
    print(f"\nConsulta: {q}  ({seg:.1f} s)")
    for x in res:
        m = x["metadata"]
        ref = m.get("articulo") and f"art. {m['articulo']}" or m.get("codigo_asignatura") or ""
        print(f"  {x['similitud']:.3f}  {m.get('tipo')}  {m.get('titulo')}  {ref}")
