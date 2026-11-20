# Resumen final del proyecto iBanú

Fecha de cierre: 2026-11-19. Tema A, segundo corte de Ciencia de Datos (orientador académico para Ingeniería de Sistemas). Los valores secretos no están en este documento: están en `D:\KyE\_orquestacion\secretos_azure.env`.

## 1. Qué se construyó y dónde está

| Pieza | Dónde | Detalle |
|---|---|---|
| Flujo único de n8n | https://ksaavedra363.app.n8n.cloud/workflow/z0r4UPdcHKqi4LZH | "iBanú: orientador académico (flujo único)", id `z0r4UPdcHKqi4LZH`, publicado, 51 nodos (45 funcionales y 6 notas), versión activa `b4726453-e8a0-4286-bdb9-c742895450ab`. Cuatro disparadores: chat, prueba del RAG, indexación manual y subida de documentos. |
| Webhook del chat | `POST https://ksaavedra363.app.n8n.cloud/webhook/ibanu/orientador` | Cabecera `X-Ibanu-Token` (el token está en `mobile/src/config.ts` y en `D:\KyE\_orquestacion\06_contrato.md`). Cuerpo: `codigo_estudiante`, `mensaje`, `sesion_id` opcional. |
| Webhook del RAG | `GET https://ksaavedra363.app.n8n.cloud/webhook/ibanu/rag-prueba?q=...&k=5` | Misma cabecera. |
| MCP público | `http://20.201.114.161:9001/mcp` | Proxy con `X-API-Key` (`MCP_PUBLIC_API_KEY`) sobre el MCP interno (13 herramientas de solo lectura). Servicio `ibanu-mcp-publico`; regla de Azure `Permitir-MCP-iBanu-9001`. |
| Supabase (proyecto `udixkdmmqgoxdkhiblzv`) | SQL Editor | Objetos nuevos: tabla `ibanu_conocimiento` (`vector(3072)`, 401 filas), función `ibanu_buscar_conocimiento`, tabla `ibanu_conversaciones`, 25 filas en `prerrequisitos`. Scripts en `D:\KyE\sql`. |
| Backend y MCP en la VM | VM `mv-parcial2` (20.201.114.161) | Backend 8000, MCP interno 172.18.0.1:8001. Se corrigió la clave de Gemini y se agregó `IBANU_MCP_URL` (ver `cambios.md`). |
| App | `D:\KyE\iBanu\mobile` (Expo SDK 58) | Se prueba en Expo Go; llama directo al webhook de n8n. |
| Repositorio | `D:\KyE\iBanu` | README completo, manual de usuario, arquitectura, scripts SQL, MCP, proxy público (`mcp_publico/`), pruebas y evidencias. |
| Copia de entrega en Azure | `~/ibanu-entrega` en la VM | Copia de `iBanu`, `n8n`, `sql` y `evidencias` (123 archivos). No afecta a los servicios. |

## 2. Cómo probar

Define el token primero (cópialo de `mobile/src/config.ts`). En PowerShell:

```powershell
$h = @{ "X-Ibanu-Token" = "<token de la app>" }
$b = @{ codigo_estudiante = "U00112048"; sesion_id = "demo-1"; mensaje = "¿Cuál es mi estado académico y cuántos créditos llevo?" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "https://ksaavedra363.app.n8n.cloud/webhook/ibanu/orientador" -Headers $h -ContentType "application/json; charset=utf-8" -Body ([Text.Encoding]::UTF8.GetBytes($b)) -TimeoutSec 120
```

En curl (Git Bash):

```bash
curl -s -X POST "https://ksaavedra363.app.n8n.cloud/webhook/ibanu/orientador" \
  -H "Content-Type: application/json; charset=utf-8" -H "X-Ibanu-Token: $IBANU_TOKEN" \
  -d '{"codigo_estudiante":"U00112048","sesion_id":"demo-1","mensaje":"¿Qué materias puedo matricular el próximo semestre?"}'
curl -s -G "https://ksaavedra363.app.n8n.cloud/webhook/ibanu/rag-prueba" -H "X-Ibanu-Token: $IBANU_TOKEN" --data-urlencode "q=¿Cómo cancelo una materia?" -d k=5
curl -i http://20.201.114.161:9001/mcp        # debe responder 401 sin la clave
```

Scripts listos en `D:\KyE\iBanu\pruebas`: `probar_webhook.ps1` (las cuatro consultas de la rúbrica), `probar_webhook.sh` (siete casos), `probar_rag.py`, `evaluar_rag.py` y `verificar_indice.py`. Estudiantes de prueba: `U00112048` (Mariana Díaz Romero, semestre 3, una materia reprobada) y `U00112040` (Laura Martínez Rojas, semestre 1). Respuestas esperadas: sin token 401, sin mensaje 400, fuera de tema o inyección `bloqueado: true`.

Expo Go (iPhone):

1. Instala Expo Go desde la App Store (versión compatible con SDK 58).
2. En una terminal: `cd D:\KyE\iBanu\mobile`, luego `npm install` y `npx expo start` (si la red bloquea el QR, `npx expo start --tunnel`).
3. Escanea el QR con la cámara del iPhone y ábrelo en Expo Go.
4. Escribe `U00112048`, toca Continuar y prueba los cuatro botones (Matrícula, Estado académico, Proyección, Recomendaciones) y el chat libre. Cada respuesta tarda de 5 a 45 s.

## 3. Lista de verificación de la rúbrica (sin el scraper de noticias)

| Criterio (peso) | Evidencia |
|---|---|
| Arquitectura (10 %) | README sección 2 (diagrama `docs/img/arquitectura.png`, Mermaid, flujo de datos y justificación); `docs/arquitectura.md` |
| RAG (15 %) | README sección 5 (documentos, chunks 1500 y solape 150, `gemini-embedding-001`, evaluación con tabla); `docs/evidencias/rag_evaluacion_2026-11-19.json`; `D:\KyE\_orquestacion\14_evaluacion_rag.md`; resultado: 401 fragmentos, acierto@1 95 %, acierto@5 100 %, MRR 0,975 |
| Base de datos (10 %) | README sección 4; `D:\KyE\sql\*.sql` y `iBanu/database/`; capturas `evidencias/sql_03_prerrequisitos_25_filas.jpg` y `evidencias/sql_99_tablas_con_datos.jpg` |
| Workflows de n8n (15 %) | `iBanu/n8n/ibanu_flujo_unico.json` y `LEEME.md`; README sección 6; captura `docs/img/n8n_lienzo_flujo_unico.jpg`; `evidencias/prueba_final_e2e_2026-11-19.md` |
| MCP y webhook (10 %) | README sección 7 (13 herramientas con respuestas reales); `iBanu/mcp_publico/`; `evidencias/pruebas_webhook_2026-11-19.md` y `evidencias/prueba_final_e2e_2026-11-19.md` |
| App Android/móvil (15 %) | `iBanu/mobile`; README sección 8 y manual de usuario. Pendiente: capturas del iPhone (ver sección 4) |
| Documentación técnica (10 %) | `iBanu/README.md`, `iBanu/docs/manual_usuario.md`, `iBanu/docs/arquitectura.md`. Pendiente: subir a GitHub |
| Pertinencia pedagógica (5 %) | README sección 11 (prompt, educación de precisión, autoaprendizaje, referencias con DOI); respuestas personalizadas en la prueba final (consultas a, c y d) |

## 4. Pendientes del dueño


2. Capturas de pantalla en Expo Go (ingreso, las cuatro consultas, una respuesta con fuentes, un aviso de bloqueo): guárdalas en `iBanu/docs/img/` y enlázalas en README sección 8 y en `docs/manual_usuario.md` (donde dice TODO).
3. Opcional: captura de una ejecución del chat abierta en n8n (README sección 6, TODO).


## 5. Notas operativas

- **Trial de n8n Cloud.** La instancia es un trial: si vence, el flujo y los webhooks dejan de responder. Exporta el flujo (`D:\KyE\iBanu\n8n\ibanu_flujo_unico.json` ya es la copia final) y, si hace falta, impórtalo en otra instancia, recrea las tres credenciales, publica y reindexa. Haz las demostraciones y capturas antes del vencimiento.
- **Cuotas de Gemini.** El plan gratuito limita las llamadas por minuto; ante cuota agotada el chat responde con el mensaje de contingencia. Entre llamadas de prueba conviene esperar unos 25 s.
- **Reindexación.** Tarda unos 22 minutos (lotes de 10 unidades, pausa de 65 s; la ejecución queda en "waiting" entre lotes). Cada reindexado borra y reinserta por documento, sin duplicar. Solo es necesario si cambian los documentos.
- **Elegibilidad.** La herramienta `evaluar_elegibilidad` lleva una copia del plan y de los 25 prerrequisitos; si cambias esas tablas hay que actualizar el nodo (documentado en README sección 12).
- **Servicios en la VM.** `ibanu-backend`, `ibanu-mcp` e `ibanu-mcp-publico` están activos y no se tocaron al subir la entrega.