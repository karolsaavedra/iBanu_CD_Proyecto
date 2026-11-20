# -*- coding: utf-8 -*-
"""Evalúa la recuperación del RAG contra GET /webhook/ibanu/rag-prueba (20 preguntas + 2 de control).
Calcula acierto@1, acierto@5 y MRR y guarda las respuestas crudas en la carpeta evidencias."""
import os, json, sys, time, urllib.parse, urllib.request, datetime

BASE = "https://ksaavedra363.app.n8n.cloud/webhook/ibanu/rag-prueba"
TOKEN = os.environ["IBANU_TOKEN"]  # token de la app (cabecera X-Ibanu-Token)
REG = "reglamento"
# (pregunta, tipo, artículos aceptados | código | tipo esperado)
P = [
 ("¿Qué pasos tengo que hacer para quedar matriculado en un semestre?", {"art": ["4"]}),
 ("¿Qué pasa si no realizo mi matrícula en la fecha señalada?", {"art": ["8"]}),
 ("¿Puedo cancelar una materia ya matriculada y hasta cuándo?", {"art": ["13"]}),
 ("Dejé de estudiar un semestre, ¿cómo me reintegro a la universidad?", {"art": ["9"]}),
 ("¿Qué significa estar en estado académico condicional?", {"art": ["10"]}),
 ("¿Cuándo quedo en prueba académica?", {"art": ["11"]}),
 ("¿Cómo se calcula el promedio del período (PPA) y el promedio general acumulado (PGA)?", {"art": ["40"]}),
 ("¿Con qué nota se aprueba un curso y cómo es la escala de calificación?", {"art": ["37", "39"]}),
 ("Perdí un curso por inasistencia, ¿puedo habilitarlo?", {"art": ["46", "47"]}),
 ("No estoy de acuerdo con la nota de un parcial, ¿cómo pido que la revisen?", {"art": ["52"]}),
 ("Si repito una materia que perdí, ¿qué nota queda registrada?", {"art": ["53"]}),
 ("¿Cuántas horas de trabajo equivale un crédito académico?", {"art": ["32"]}),
 ("¿Qué requisitos me piden para homologar materias que cursé en otra universidad?", {"art": ["17", "18", "19"]}),
 ("¿Cuáles son los requisitos para obtener el título de pregrado?", {"art": ["67"]}),
 ("¿Cómo funciona la práctica académica y qué objetivos tiene?", {"art": ["55", "56", "57"]}),
 ("¿Qué se considera plagio y qué sanción puede tener?", {"art": ["101", "102", "104"]}),
 ("¿Cuántos créditos tiene Cálculo Diferencial y cuántas horas con el profesor?", {"cod": "MATE19029"}),
 ("¿Infraestructura Tecnológica tiene prerrequisitos y en qué semestre se ve?", {"cod": "COMP18039"}),
 ("¿Qué propone la UNAB para pasar de competencias informáticas a competencias digitales?", {"tipo": "competencias"}),
 ("¿De qué trata el programa de Ingeniería de Sistemas de la UNAB y cómo está organizado?", {"tipo": "programa"}),
]
CONTROL = ["¿Cuál es el horario de la cafetería?", "¿Cuánto cuesta un semestre en 2027?"]

def consultar(q, k=5):
    url = BASE + "?" + urllib.parse.urlencode({"q": q, "k": k})
    req = urllib.request.Request(url, headers={"X-Ibanu-Token": TOKEN})
    for intento in range(3):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.status, json.loads(r.read().decode("utf-8"))
        except Exception as e:
            err = str(e); time.sleep(5)
    return 0, {"error": err}

def acierta(meta, esp):
    if "art" in esp:
        return meta.get("tipo") == REG and str(meta.get("articulo")) in esp["art"]
    if "cod" in esp:
        return meta.get("codigo_asignatura") == esp["cod"] or meta.get("titulo") == esp["cod"]
    return meta.get("tipo") == esp["tipo"]

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    filas, crudo = [], []
    for i, (q, esp) in enumerate(P, 1):
        st, d = consultar(q)
        res = d.get("resultados", []) if isinstance(d, dict) else []
        pos = next((j + 1 for j, r in enumerate(res) if acierta(r.get("metadata", {}), esp)), None)
        crudo.append({"n": i, "pregunta": q, "esperado": esp, "http": st, "posicion": pos, "respuesta": d})
        filas.append((i, pos, res[0].get("similitud") if res else None))
        print(i, st, pos, filas[-1][2], flush=True)
        time.sleep(3)
    ctrl = []
    for q in CONTROL:
        st, d = consultar(q)
        res = d.get("resultados", []) if isinstance(d, dict) else []
        ctrl.append({"pregunta": q, "http": st, "respuesta": d})
        print("control", st, res[0].get("similitud") if res else None, flush=True)
        time.sleep(3)
    n = len(P)
    m = {"preguntas": n, "acierto_1": sum(1 for _, p, _ in filas if p == 1) / n,
         "acierto_5": sum(1 for _, p, _ in filas if p) / n,
         "mrr": sum(1 / p for _, p, _ in filas if p) / n}
    fecha = datetime.date.today().isoformat()
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "evidencias", "rag_evaluacion_%s.json" % fecha)
    json.dump({"fecha": fecha, "metricas": m, "preguntas": crudo, "control": ctrl}, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(m, ruta)

if __name__ == "__main__":
    main()
