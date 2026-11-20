# -*- coding: utf-8 -*-
"""Verificación de solo lectura de public.ibanu_conocimiento por la API REST de Supabase."""
import os, json, sys, collections, urllib.request
# Variables de entorno SUPABASE_URL y SUPABASE_SECRET_KEY (la clave de servicio no se versiona)
env = os.environ
U, K = env["SUPABASE_URL"].rstrip("/"), env["SUPABASE_SECRET_KEY"]
def get(path):
    r = urllib.request.Request(U + "/rest/v1/" + path, headers={"apikey": K, "Authorization": "Bearer " + K})
    return json.loads(urllib.request.urlopen(r, timeout=120).read().decode("utf-8"))
sys.stdout.reconfigure(encoding="utf-8")
filas, off = [], 0
while True:
    b = get("ibanu_conocimiento?select=id,content,metadata&order=id&limit=500&offset=%d" % off)
    filas += b
    if len(b) < 500: break
    off += 500
print("filas", len(filas))
print("por tipo", dict(collections.Counter(f["metadata"].get("tipo") for f in filas)))
por_doc = collections.Counter(f["metadata"].get("documento_id") for f in filas)
print("documentos", len(por_doc))
tit = {}
for f in filas: tit[f["metadata"].get("documento_id")] = f["metadata"].get("titulo")
print("fragmentos por documento (no reglamento):")
for d, n in por_doc.most_common():
    if tit[d] and not tit[d].startswith("Reglamento"): print(" ", n, tit[d], d)
print("reglamento", por_doc[[d for d in tit if (tit[d] or '').startswith('Reglamento')][0]])
dup = collections.Counter(f["content"] for f in filas)
print("contenido duplicado", sum(1 for c, n in dup.items() if n > 1))
lon = sorted(len(f["content"]) for f in filas)
print("longitud min/mediana/max", lon[0], lon[len(lon)//2], lon[-1])
print("sin metadata documento_id", sum(1 for f in filas if not f["metadata"].get("documento_id")))
for f in (filas[0], filas[len(filas)//2], filas[-1]):
    print(json.dumps({"id": f["id"], "metadata": f["metadata"], "content": f["content"][:200]}, ensure_ascii=False))
e = get("ibanu_conocimiento?select=id,embedding&limit=3")
for x in e:
    v = x["embedding"]; v = json.loads(v) if isinstance(v, str) else v
    print("embedding id", x["id"], "dim", len(v))
