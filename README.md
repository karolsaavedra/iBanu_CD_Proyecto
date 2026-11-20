# iBanú: orientador académico para Ingeniería de Sistemas

Agente conversacional en n8n que acompaña al estudiante de Ingeniería de Sistemas en la **matrícula**, su **estado académico**, su **proyección** de avance, los **requisitos** del programa y las **recomendaciones** para tener éxito, con un enfoque de **educación de precisión** (cada consejo parte de los datos reales del estudiante) y de **autoaprendizaje** (rutas de estudio y formas de verificar el propio avance).

Trabajo final de Ciencia de Datos, segundo corte, tema A.

## Autores

- **Karol Stefany Saavedra Suárez**
- **Edson Julián Díaz Pinilla**

## Contenido

1. [Descripción y objetivo](#1-descripción-y-objetivo)
2. [Arquitectura](#2-arquitectura)
3. [Componentes](#3-componentes)
4. [Base de datos](#4-base-de-datos)
5. [RAG](#5-rag)
6. [Workflow de n8n](#6-workflow-de-n8n)
7. [Servidor MCP y webhook](#7-servidor-mcp-y-webhook)
8. [Aplicación móvil](#8-aplicación-móvil)
9. [Instalación y despliegue](#9-instalación-y-despliegue)
10. [Pruebas](#10-pruebas)
11. [Pertinencia pedagógica](#11-pertinencia-pedagógica)
12. [Limitaciones y trabajo futuro](#12-limitaciones-y-trabajo-futuro)
13. [Estructura del repositorio](#13-estructura-del-repositorio)
14. [Documentación adicional y referencias](#14-documentación-adicional-y-referencias)

Documentos relacionados: [manual de usuario](docs/manual_usuario.md), [arquitectura detallada](docs/arquitectura.md), [flujo de n8n](n8n/LEEME.md).

---

## 1. Descripción y objetivo

El estudiante abre la aplicación, escribe su código y consulta en lenguaje natural. Un único flujo de n8n valida la solicitud, aplica guardrails, y entrega la pregunta a un agente con herramientas que consulta la base de datos académica (por un servidor MCP) y los documentos institucionales (RAG sobre el reglamento, las guías de cátedra y el programa). La respuesta vuelve a la app en Markdown, con las fuentes citadas.

**Objetivo general.** Apoyar al estudiante de Ingeniería de Sistemas en su matrícula, su estado académico y su proyección, con requisitos y recomendaciones personalizadas para el éxito en el programa.

**Objetivos específicos.**

| Necesidad del enunciado | Cómo la cubre iBanú |
|---|---|
| Matrícula | Horario, turnos de inscripción, oferta de grupos con cupos y reglas del reglamento (reserva de cupo, cancelación, reintegro). iBanú solo informa: no inscribe ni cancela. |
| Estado académico | Asignaturas aprobadas, en curso y pendientes, créditos acumulados, promedio calculado con las notas y alertas (componentes con nota baja, reprobadas). |
| Proyección | Créditos pendientes, semestres restantes estimados con la carga real del historial y escenario de ruta, presentado como estimación. |
| Requisitos | Prerrequisitos y conocimientos previos de cada asignatura (tabla `prerrequisitos`, tomada de las guías de cátedra) y artículos del reglamento citados. |
| Recomendaciones | Plan de 3 a 5 acciones priorizadas con frecuencia y duración, rutas de autoaprendizaje y orientación hacia semilleros de investigación. |

**Importante.** Los estudiantes, notas, matrículas, grupos y turnos son **sintéticos** y el plan de estudios cargado es **provisional**: no representan información oficial de la UNAB. El agente lo indica en sus respuestas.

---

## 2. Arquitectura

![Arquitectura de iBanú](docs/img/arquitectura.png)

(Versión vectorial: [docs/img/arquitectura.svg](docs/img/arquitectura.svg). El script que la genera es [docs/img/generar_arquitectura.py](docs/img/generar_arquitectura.py).)

### Diagrama en Mermaid

```mermaid
flowchart LR
    E[Estudiante] --> APP[App Expo en Expo Go]
    APP -- "POST /webhook/ibanu/orientador<br/>X-Ibanu-Token" --> WH

    subgraph N8N[n8n Cloud: un solo flujo con cuatro disparadores]
        WH[Webhook chat] --> VAL[Validar solicitud<br/>401 / 400]
        VAL --> GIN[Guardrail de entrada<br/>reglas, 2 comprobaciones con Gemini,<br/>¿Bloqueo confirmado?]
        GIN -- bloqueado --> BLQ[Respuesta de bloqueo]
        GIN -- pasa --> AG[Agente orientador<br/>Gemini 3.5 Flash Lite<br/>Simple Memory 10 mensajes]
        AG -- "cruce determinista" --> ELEG[evaluar_elegibilidad<br/>Code Tool: plan y 25 prerrequisitos]
        AG -- error --> CONT[Respuesta de contingencia]
        AG --> GOUT[Guardrail de salida<br/>sanitiza y extrae fuentes]
        GOUT --> RESP[Responder al chat]
        BLQ --> RESP
        CONT --> RESP
        RESP --> LOG[Registrar turno]

        WH2[Webhook GET rag-prueba] --> VS2[Vector Store: cargar]
        MAN[Disparador manual:<br/>indexar] --> IDX[Leer, reconstruir,<br/>dividir 1500 / 150<br/>lotes de 10, pausa 65 s]
        FRM[Formulario:<br/>subir documento] --> PDF[Extraer texto del PDF] --> IDX
        IDX --> EMB2[Embeddings 3072] --> INS[Vector Store: insertar]
    end

    RESP -- "JSON: respuesta, fuentes" --> APP
    AG -- "MCP HTTP + X-API-Key" --> MCP
    AG -- "búsqueda semántica" --> VS[(ibanu_conocimiento<br/>pgvector 3072)]
    VS2 --> VS
    INS --> VS
    LOG --> CONV[(ibanu_conversaciones)]

    subgraph AZ[VM Azure mv-parcial2]
        MCP[Proxy MCP público :9001] --> MCPI[MCP interno :8001<br/>13 herramientas] --> BE[Backend FastAPI :8000]
    end
    BE --> SB[(Supabase PostgreSQL<br/>estudiantes, matrículas, notas,<br/>asignaturas, prerrequisitos)]
    VS --- SB
    CONV --- SB
```

### Flujo de datos de una consulta

1. La app envía `POST /webhook/ibanu/orientador` con el código del estudiante, el mensaje y un `sesion_id`, y la cabecera `X-Ibanu-Token`.
2. El nodo de validación responde 401 (token) o 400 (cuerpo) sin gastar modelo; si todo está bien genera el `sesion_id` faltante y toma la hora de inicio.
3. El guardrail de entrada revisa primero con reglas gratuitas (palabras clave, expresiones regulares, correo, teléfono, tarjeta, claves) y solo si pasa consulta a Gemini (intento de saltarse instrucciones, tema ajeno a la orientación académica).
4. El agente recibe el **código verificado** (no el que aparezca en el texto), recupera la memoria de la sesión, llama al MCP para los datos del estudiante y a la base documental para reglas y contenidos, y redacta la respuesta.
5. Para la elegibilidad de matrícula, el agente pasa los códigos aprobados, en curso y pendientes a la herramienta `evaluar_elegibilidad`, que cruza el plan con los prerrequisitos y suma créditos sin intervención del modelo.
6. El guardrail de salida enmascara tarjetas, IBAN, IP, claves y cabeceras internas; el flujo extrae las fuentes (ver sección 6), reemplaza cualquier código ajeno al verificado y limita la longitud.
7. El flujo responde a la app y, en paralelo, guarda el turno con su latencia en `ibanu_conversaciones`.

### Justificación de las decisiones de diseño

| Decisión | Razón |
|---|---|
| **Un solo flujo con cuatro entradas** (chat, prueba del RAG, indexación, subida) | Lo exige el proyecto y simplifica el despliegue: un único objeto que importar, publicar y versionar. Las cuatro entradas comparten almacén vectorial y credenciales. |
| **Agente de herramientas con guardrails nativos** en lugar de un clasificador de intención con subflujos | Un solo agente decide qué consultar (menos llamadas al modelo, menos piezas que fallen). Los guardrails nativos de n8n separan la seguridad de la lógica: primero lo que no usa modelo y después, solo si pasa, dos comprobaciones con Gemini. |
| **MCP sobre HTTP con clave de API** | El servidor MCP ya existía y consulta la base de datos; n8n Cloud solo puede llegar por Internet, así que se añadió un proxy público (puerto 9001) que exige `X-API-Key` y reenvía al MCP interno sin modificarlo. Las 13 herramientas son de solo lectura. |
| **Supabase PostgreSQL con pgvector** | Una sola base para los datos estructurados y los vectores; el nodo Supabase Vector Store de n8n funciona sobre ella con las columnas `content`, `metadata` y `embedding`. |
| **`gemini-3.5-flash-lite`** (respaldo `gemini-3.5-flash`) con temperatura 0,3 | Latencia y costo bajos para un chat con herramientas; la temperatura baja mantiene las cifras y citas estables. |
| **`gemini-embedding-001` con 3072 dimensiones y búsqueda exacta** | El nodo nativo de embeddings de n8n entrega 3072 valores y no deja fijar la dimensión. pgvector limita el índice HNSW a 2000 dimensiones, pero con unos cientos de fragmentos la búsqueda exacta por coseno tarda milisegundos y tiene recall del 100 %. |
| **Simple Memory (ventana de 10) por estudiante y sesión** | Da continuidad ("¿y qué me recomiendas para el próximo semestre?") sin infraestructura adicional; la clave `codigo_sesion` evita mezclar estudiantes. |
| **Tabla `ibanu_conversaciones`** | Trazabilidad: qué se preguntó, qué se respondió, qué bloqueó un guardrail y cuánto tardó. Alimenta el análisis de uso y de latencia. |
| **App Expo en Expo Go** | Una sola base de código, sin compilar un APK; llama directo al webhook de n8n. |
| **Cruce de prerrequisitos y sumas en código (`evaluar_elegibilidad`)** | En las primeras pruebas el modelo de chat se equivocó al cruzar prerrequisitos y al sumar créditos. Una herramienta Code Tool determinista entrega elegibles, bloqueadas y totales exactos; el modelo solo copia códigos y redacta. |
| **Identidad fijada por el flujo** | El código del estudiante se verifica en el webhook; el agente lo recibe en el mensaje de sistema y nunca lo toma del texto del usuario, lo que impide pedir datos de otra persona. |

---

## 3. Componentes

| Componente | Tecnología | Función |
|---|---|---|
| Orquestador | n8n Cloud 2.47 | Flujo único: webhook, guardrails, agente, herramientas, registro, indexación. |
| Base de datos | Supabase Cloud (PostgreSQL con pgvector 0.8.2) | Modelo académico, almacén vectorial y registro de conversaciones. |
| Agente y LLM | Agente de herramientas de n8n con Gemini 3.5 Flash Lite | Razonamiento, uso de herramientas y redacción. |
| RAG | Supabase Vector Store, `gemini-embedding-001` (3072) | Reglamento, guías de cátedra y programa. |
| Servidor MCP | FastMCP (Python) en VM Azure Ubuntu 24.04, con proxy de clave de API | 13 herramientas de lectura sobre el backend. |
| Backend | FastAPI en la misma VM (puerto 8000) | Consultas a Supabase usadas por el MCP. |
| Webhook | Webhook de n8n (`POST /ibanu/orientador`, `GET /ibanu/rag-prueba`) | Entrada de la app y prueba del RAG. |
| Aplicación | React Native y Expo SDK 58, Expo Go | Interfaz del estudiante. |

### Servidor MCP: las 13 herramientas

Todas son de solo lectura y llaman a una ruta del backend, que consulta Supabase. Código en [`mcp/server.py`](mcp/server.py).

| # | Herramienta | Parámetro | Qué devuelve |
|---|---|---|---|
| 1 | `consultar_estudiante` | `codigo_estudiante` | Datos básicos y estado. |
| 2 | `consultar_horario` | `codigo_estudiante` | Grupos matriculados, profesores, días y horas. |
| 3 | `consultar_historial` | `codigo_estudiante` | Matrículas con estado y notas por componente. |
| 4 | `consultar_materias_pendientes` | `codigo_estudiante` | Aprobadas, en curso y pendientes frente al plan. |
| 5 | `consultar_siguiente_semestre` | `codigo_estudiante` | Asignaturas del siguiente nivel con sus profesores. |
| 6 | `consultar_turnos` | `codigo_estudiante` | Turnos de inscripción (sintéticos). |
| 7 | `consultar_grupos` | `codigo_periodo` (ej. `SIM-2027-1`) | Grupos, profesores, horarios y cupos del periodo. |
| 8 | `consultar_asignatura` | `codigo_asignatura` | Nombre, créditos y profesores. |
| 9 | `consultar_profesor` | `codigo_profesor` | Departamento y asignaturas. |
| 10 | `buscar_profesor_por_nombre` | `nombre` | Profesores que coinciden. |
| 11 | `consultar_estado_plataforma` | ninguno | Estado del backend y de la conexión con Supabase. |
| 12 | `consultar_materias_semestre` | `numero_semestre` (1 a 9) | Asignaturas de un semestre del plan. |
| 13 | `buscar_asignatura_por_nombre` | `nombre` | Asignaturas que coinciden, con créditos y profesores. |

---

## 4. Base de datos

PostgreSQL en Supabase (proyecto `udixkdmmqgoxdkhiblzv`). El modelo académico viene de las migraciones 001 a 005; las tablas del agente y del RAG se agregan con los scripts de `database/migrations/n8n/`, que son aditivos e idempotentes (no tocan las tablas existentes).

### Modelo

```mermaid
erDiagram
    planes_estudio ||--o{ plan_asignaturas : contiene
    asignaturas ||--o{ plan_asignaturas : "se ubica en"
    planes_estudio ||--o{ estudiantes : "cursa"
    asignaturas ||--o{ prerrequisitos : "requiere (asignatura_id)"
    asignaturas ||--o{ prerrequisitos : "es requisito (prerrequisito_id)"
    asignaturas ||--o{ grupos : "se ofrece en"
    periodos_academicos ||--o{ grupos : tiene
    profesores ||--o{ grupos_profesores : dicta
    grupos ||--o{ grupos_profesores : tiene
    grupos ||--o{ horarios_grupos : tiene
    estudiantes ||--o{ matriculas : realiza
    grupos ||--o{ matriculas : recibe
    matriculas ||--o{ notas : tiene
    estudiantes ||--o{ turnos_inscripcion : tiene
    documentos_academicos ||--o{ fragmentos_documento : "se divide en"
```

| Tabla | Para qué sirve | Filas |
|---|---|---|
| `estudiantes` | Código (`U` + 8 dígitos), nombres, plan, año de ingreso, estado | 30 |
| `planes_estudio`, `plan_asignaturas` | Plan provisional de Ingeniería de Sistemas y su ubicación por semestre | 1 y 38 |
| `asignaturas` | Catálogo con código `IB26-Sxx-xx`, créditos y descripción | 38 |
| `prerrequisitos` | Pares (asignatura, requisito) | 25 |
| `profesores`, `profesores_asignaturas` | Directorio y asignaturas por profesor | 12 y 64 |
| `periodos_academicos`, `grupos`, `grupos_profesores`, `horarios_grupos` | Oferta de cada periodo | 10, 380, 76 y 76 |
| `matriculas`, `notas` | Historial de cada estudiante y calificaciones por componente con su porcentaje | 653 y 1533 |
| `turnos_inscripcion` | Turnos de inscripción sintéticos | 60 |
| `documentos_academicos`, `fragmentos_documento` | Documentos del RAG y sus fragmentos de origen | 41 y 341 |
| `ibanu_conocimiento` | Almacén vectorial del RAG (nueva) | ver sección 5 |
| `ibanu_conversaciones` | Registro de cada turno del chat (nueva) | crece con el uso |

Las filas son las medidas el 2026-11-19 (ver [`pruebas/`](pruebas/) y las capturas).

### Scripts

| Script | Contenido |
|---|---|
| [`database/migrations/001` a `005`](database/migrations/) | Esquema académico, matrículas y notas, documentos, profesores, horarios y turnos, marca de datos sintéticos. |
| [`database/seeds/001` a `004`](database/seeds/) | Catálogo del plan, estudiantes, profesores, grupos, horarios, matrículas, notas y turnos sintéticos. |
| [`database/migrations/n8n/01_rag_vectorial.sql`](database/migrations/n8n/01_rag_vectorial.sql) | Extensión `vector`, tabla `ibanu_conocimiento`, función `ibanu_buscar_conocimiento`, índices, RLS. |
| [`database/migrations/n8n/02_conversaciones.sql`](database/migrations/n8n/02_conversaciones.sql) | Tabla `ibanu_conversaciones` con dos índices. |
| [`database/migrations/n8n/03_prerrequisitos.sql`](database/migrations/n8n/03_prerrequisitos.sql) | 25 prerrequisitos documentados en las guías de cátedra (1 formal y 24 conocimientos previos). |
| [`database/migrations/n8n/04_embeddings_3072.sql`](database/migrations/n8n/04_embeddings_3072.sql) | Pasa la columna a `vector(3072)`, quita el índice HNSW y recrea la búsqueda exacta. |
| [`database/tests/99_verificacion.sql`](database/tests/99_verificacion.sql) | Doce consultas que muestran tablas con datos, extensiones, función, índices y RLS. |

### Evidencia del acceso al servidor y de las tablas con datos

Ejecución en el SQL Editor de Supabase. `03_prerrequisitos.sql` devolvió 25 filas:

![Prerrequisitos insertados](docs/img/sql_03_prerrequisitos_25_filas.jpg)

Verificación del bloque 1 (tablas con filas): `plan_asignaturas` 38, `planes_estudio` 1, `prerrequisitos` 25, `profesores` 12, `profesores_asignaturas` 64, `turnos_inscripcion` 60.

![Tablas con datos](docs/img/sql_99_tablas_con_datos.jpg)

Otros resultados de `99_verificacion.sql`: extensiones `vector` 0.8.2, `pgcrypto`, `uuid-ossp`; función `ibanu_buscar_conocimiento(query_embedding vector, match_count integer DEFAULT 5, filter jsonb DEFAULT '{}')`; RLS activo en `ibanu_conocimiento` e `ibanu_conversaciones`. Tras `04_embeddings_3072.sql` la tabla vectorial usa `vector(3072)` sin índice HNSW.

### Prerrequisitos: origen y límites

Ninguna guía de cátedra tiene una sección "Prerrequisitos". Solo dos usan la palabra: Infraestructura Tecnológica (COMP18039) "no tiene prerrequisito" e Internet de las Cosas (TELE18052) tiene como prerrequisito Infraestructura Tecnológica. Los otros 24 pares salen de la sección 2 de las guías, "Conocimientos previos requeridos para el curso", y cada fila del SQL lo indica en su comentario. Ocho asignaturas no tienen guía oficial (Expresión, Identidad, Creatividad, Matemáticas Computacionales, Ciencias de Datos, Teoría de Sistemas y Organizaciones, Ingeniería de Software II y Dinámica de Sistemas) y no se dedujo ninguna relación por el orden de los semestres.

---

## 5. RAG

### Documentos usados

| Categoría | Documentos | Fragmentos de origen |
|---|---|---|
| Reglamento | Reglamento Estudiantil de Pregrado UNAB (2019): 144 artículos | 144 |
| Guías de cátedra | 30 guías oficiales de las asignaturas de Ingeniería de Sistemas (semestres 1 a 9) y 8 guías sintéticas marcadas "CONTENIDO SINTÉTICO, NO OFICIAL" | 127 |
| Programa | Página oficial del programa de Ingeniería de Sistemas y Propuesta de Competencias Digitales UNAB V11 | 70 |
| **Total** | **41 documentos** (353.903 caracteres, unos 93.000 tokens) | **341** |

Los PDF originales y los textos procesados no se publican en el repositorio (ver `.gitignore`); los scripts de extracción están en [`rag/scripts/`](rag/scripts/).

### Pipeline

```mermaid
flowchart LR
    A[documentos_academicos<br/>fragmentos_documento] --> B[Reconstruir texto<br/>sin solape]
    B --> C{Tipo}
    C -- reglamento --> D[Un fragmento por artículo<br/>con prefijo de contexto]
    C -- guía o programa --> E[Divisor recursivo<br/>1500 caracteres, solape 150]
    D --> F[Embeddings Google Gemini<br/>gemini-embedding-001, 3072]
    E --> F
    F --> G[(ibanu_conocimiento<br/>content, metadata, embedding)]
    G --> H[Búsqueda exacta por coseno<br/>ibanu_buscar_conocimiento, k = 5]
    H --> I[Agente: herramienta de base documental]
```

El flujo reconstruye cada documento desde los fragmentos ya almacenados (no hace falta volver a los PDF), borra los fragmentos previos del mismo `documento_id` para no duplicar al reindexar, divide, vectoriza en lotes de **10 unidades** con una **pausa de 65 s** entre lotes (el plan gratuito de Gemini limita los embeddings por minuto: con lotes de 25 y pausa de 30 s la API devolvió vectores vacíos y la inserción falló) y los inserta. La indexación completa tarda **unos 22 minutos** (ejecución 12: 22 min 15 s, 401 fragmentos). Subir un PDF nuevo desde el formulario entra al mismo camino.

### Parámetros y justificación

| Parámetro | Valor | Justificación |
|---|---|---|
| Reglamento | Un fragmento por artículo; si pasa de 1800 caracteres, se parte por numerales y párrafos con solape de 150 | La unidad semántica del reglamento es el artículo: regula una sola materia y una pregunta casi siempre se responde con un artículo completo (mediana 549 caracteres). Cortar cada N caracteres mezclaba el final de un artículo con el inicio de otro. Además permite citar "Artículo N" y la página. |
| Guías y programa | Tamaño objetivo 1200, máximo 1500 caracteres, solape 150 (10 a 12 %) | 1200 a 1500 caracteres (unos 300 a 400 tokens) caben en una idea completa (una sección de la guía) sin diluir el vector. El solape de 150 evita perder una frase partida en el borde sin duplicar demasiado. Los fragmentos originales de 2200 caracteres arrastraban la cabecera institucional repetida y cortes por página. |
| Divisor | Recursivo, separadores `\n\n`, `\n`, `. `, `; `, ` ` | Prefiere cortar en párrafos y frases antes que en medio de una palabra. |
| Contexto | Prefijo en el texto vectorizado ("Reglamento Estudiantil de Pregrado UNAB, Capítulo X, Artículo 40: ...") | El vector lleva el nombre del documento y la sección, y la respuesta puede citar la fuente. |
| Modelo de embeddings | `gemini-embedding-001`, 3072 dimensiones | Modelo multilingüe de Google (el corpus está en español); es el que ofrece el nodo nativo de n8n y entrega 3072 valores por defecto. La misma familia de la clave del proyecto evita una credencial adicional. |
| Búsqueda | Exacta por coseno, k = 5 | pgvector limita HNSW a 2000 dimensiones; con unos 400 a 500 fragmentos la búsqueda exacta es rápida y no pierde resultados. |
| Metadatos | `tipo`, `titulo`, `fuente`, `version`, `articulo`, `capitulo`, `seccion`, `pagina`, `codigo_asignatura`, `semestre`, `sintetico`, `documento_id` | Permiten citar, filtrar (por ejemplo solo reglamento) y avisar cuando una respuesta se apoya en una guía sintética. |

El análisis completo del corpus (distribución de longitudes, cómo se fragmentó originalmente) está en [docs/arquitectura.md](docs/arquitectura.md).

### Evaluación de la recuperación

Indexación final: **401 fragmentos** en 41 documentos (reglamento 171, guías de cátedra 168, competencias 56, programa 6), todos con embeddings de 3072 valores, 41 `documento_id` distintos, longitud mediana de 900 caracteres y máxima de 1500, sin duplicados por reindexado (`pruebas/verificar_indice.py`). Se evaluó `GET /webhook/ibanu/rag-prueba` (k = 5) con 20 preguntas de respuesta conocida (16 del reglamento, 2 de guías, 1 de competencias y 1 del programa) y 2 preguntas de control fuera del corpus. Criterio: acierto si algún fragmento devuelto pertenece al artículo o documento esperado; la posición es el lugar del primer resultado correcto.

| Métrica | Valor | Meta | Cumple |
|---|---|---|---|
| Acierto@1 | 19 de 20 = **95 %** | 60 % | Sí |
| Acierto@5 | 20 de 20 = **100 %** | 85 % | Sí |
| MRR | **0,975** | sin meta | n/a |

| # | Pregunta (resumen) | Esperado | Pos. | Sim. del 1.º | Primer resultado |
|---|---|---|---|---|---|
| 1 | Pasos para quedar matriculado | Art. 4 | 1 | 0,736 | Art. 4 |
| 2 | Matrícula fuera de fecha | Art. 8 | 1 | 0,716 | Art. 8 |
| 3 | Cancelar materia y plazo | Art. 13 | 1 | 0,788 | Art. 13 |
| 4 | Reintegro | Art. 9 | 1 | 0,740 | Art. 9 |
| 5 | Estado académico condicional | Art. 10 | 2 | 0,751 | Art. 24 |
| 6 | Prueba académica | Art. 11 | 1 | 0,732 | Art. 11 |
| 7 | Cálculo de PPA y PGA | Art. 40 | 1 | 0,810 | Art. 40 |
| 8 | Nota aprobatoria y escala | Art. 37 o 39 | 1 | 0,734 | Art. 37 |
| 9 | Inasistencia y habilitación | Art. 46 o 47 | 1 | 0,721 | Art. 47 |
| 10 | Revisión de calificaciones | Art. 52 | 1 | 0,781 | Art. 52 |
| 11 | Repetición de cursos | Art. 53 | 1 | 0,756 | Art. 53 |
| 12 | Horas por crédito | Art. 32 | 1 | 0,787 | Art. 32 |
| 13 | Homologación | Art. 17 a 19 | 1 | 0,752 | Art. 19 |
| 14 | Requisitos del título | Art. 67 | 1 | 0,745 | Art. 67 |
| 15 | Práctica académica | Art. 55 a 57 | 1 | 0,726 | Art. 57 |
| 16 | Plagio y sanción | Art. 101, 102 o 104 | 1 | 0,764 | Art. 101 |
| 17 | Créditos de Cálculo Diferencial | MATE19029 | 1 | 0,740 | MATE19029 |
| 18 | Infraestructura Tecnológica | COMP18039 | 1 | 0,752 | COMP18039 |
| 19 | Competencias digitales | Propuesta V11 | 1 | 0,845 | Propuesta V11 |
| 20 | Programa de Ingeniería de Sistemas | Página del programa | 1 | 0,825 | Página del programa |

**Análisis del fallo.** En la pregunta 5 el artículo 24 (que lista los estados normal, condicional y prueba) quedó por delante del artículo 10 por 0,751 contra 0,749. Es razonable, porque el 24 también define el condicional, el artículo 10 queda segundo y el agente recibe los cinco resultados. Un reranker lo corregiría, pero no es necesario para cumplir la meta.

**Preguntas de control (fuera del corpus).** "¿Cuál es el horario de la cafetería?" devolvió la guía ESTA19029 con similitud 0,595 y "¿Cuánto cuesta un semestre en 2027?" devolvió la Propuesta de Competencias con 0,733 (por afinidad con "semestre"), comparable a un acierto real (0,715 a 0,845). No existe un umbral de similitud que separe limpiamente lo ajeno al corpus, así que la negativa a responder se apoya en el prompt del agente y en el guardrail de tema, no en un umbral; se comprueba en las pruebas del chat (consulta "f" de la sección 10).

**Limitación de la muestra.** Las 20 preguntas tienen redacción cercana al texto del reglamento; con preguntas coloquiales o ambiguas el acierto@1 puede bajar.

Reproducción: `IBANU_TOKEN=... python pruebas/evaluar_rag.py` y, para el estado del índice, `SUPABASE_URL=... SUPABASE_SECRET_KEY=... python pruebas/verificar_indice.py`. Resultado crudo: [`docs/evidencias/rag_evaluacion_2026-11-19.json`](docs/evidencias/rag_evaluacion_2026-11-19.json). La primera demostración con pocas consultas (hecha mientras la indexación seguía en curso) quedó en [`pruebas/rag_demo_2026-11-19.json`](pruebas/rag_demo_2026-11-19.json) y [`pruebas/probar_rag.py`](pruebas/probar_rag.py); la evaluación anterior la reemplaza.

---

## 6. Workflow de n8n

Flujo **"iBanú: orientador académico (flujo único)"**, publicado en n8n Cloud. Archivo importable: [`n8n/ibanu_flujo_unico.json`](n8n/ibanu_flujo_unico.json) (51 nodos: 45 funcionales y 6 notas adhesivas). Guía de importación y detalle: [`n8n/LEEME.md`](n8n/LEEME.md).

![Lienzo del flujo](docs/img/n8n_lienzo_flujo_unico.jpg)

*Vista general del lienzo: azul, chat de la app; morado, prueba del RAG; rojo, subida de documentos; marrón, indexación.*

### Resumen nodo por nodo (camino del chat)

| Nodo | Qué hace |
|---|---|
| Webhook chat orientador | Recibe el `POST`; responde mediante un nodo (`responseNode`). |
| Validar solicitud del chat | Código determinista: cabecera `X-Ibanu-Token` (401), formato del código, mensaje obligatorio de máximo 1000 caracteres y `sesion_id` válido (400). Genera `sesion_id` si falta, deduce el canal y guarda la hora de inicio. |
| ¿Solicitud válida? | Si no, devuelve `{"ok": false, "error": ...}` con 401 o 400. |
| Guardrail de entrada | Nodo nativo Guardrails. Primero reglas sin modelo (palabras clave, expresión regular de inyección, correo, teléfono, tarjeta, IBAN, IP, claves). Solo si pasan, dos comprobaciones con Gemini con umbral 0,8: intento de saltarse las instrucciones y tema ajeno a la orientación académica (el prompt incluye ejemplos de temas ajenos, como cafetería o clima). |
| ¿Bloqueo confirmado? | Nodo If nuevo tras el guardrail. Solo bloquea si una comprobación se disparó sin fallar (o si el nodo mismo dio error). Si el modelo del guardrail falló (por ejemplo, un JSON truncado, "Failed to parse output"), el mensaje sigue al agente: las comprobaciones deterministas ya se evaluaron y el prompt del agente rechaza lo ajeno. Corrige un hallazgo de la prueba final: dos mensajes legítimos habían sido bloqueados por ese fallo. |
| Preparar respuesta de bloqueo | Convierte el motivo (`inyeccion_de_instrucciones`, `datos_personales`, `datos_sensibles`, `fuera_de_tema`, `servicio_no_disponible`) en un mensaje amable. |
| Orientador iBanú | Agente de herramientas, máximo 8 iteraciones, devuelve los pasos intermedios para extraer las fuentes. Recibe el código verificado y el mensaje. Reglas del prompt: volver a consultar las herramientas en cada turno (no responder de memoria), no llamar herramientas ante temas fuera de alcance y declinar con amabilidad, y calcular la elegibilidad con `evaluar_elegibilidad`. |
| Gemini 3.5 Flash Lite | Modelo del agente, temperatura 0,3. |
| Memoria por estudiante y sesión | Simple Memory, ventana de 10, clave `codigo_estudiante_sesion_id`. |
| Consultas académicas MCP | Cliente MCP (HTTP Streamable) al servidor público, con la credencial Header Auth. Expone las 13 herramientas. |
| evaluar_elegibilidad | **Code Tool** (código JavaScript determinista, sin modelo). El agente le pasa los códigos aprobados, en curso y pendientes y el semestre actual; cruza el plan (38 asignaturas con créditos) con los 25 prerrequisitos y devuelve `elegibles`, `elegibles si aprueba lo que cursa`, `bloqueadas` (con el prerrequisito que falta) y `resumen_creditos`, incluidos los semestres restantes con cargas de 15, 17 y 18 créditos. Existe porque ninguna de las 13 herramientas MCP devuelve prerrequisitos y porque `gemini-3.5-flash-lite` inventó un prerrequisito y sumó mal los créditos en las primeras pruebas. La tabla de prerrequisitos también va en el prompt como respaldo. |
| Base documental iBanú | Supabase Vector Store como herramienta del agente: tabla `ibanu_conocimiento`, función `ibanu_buscar_conocimiento`, k = 5, con metadatos. Con `onError` en continuar: si el RAG falla, el agente responde con los datos del MCP y avisa "No pude consultar los documentos institucionales". |
| Respuesta de contingencia | Si el agente falla (cuota, red) devuelve un mensaje de reintento con `motivo = error_temporal`. |
| Guardrail de salida | Modo sanitizar: enmascara tarjetas, IBAN, IP, claves y cabeceras internas. |
| Extraer fuentes y depurar respuesta | Arma `fuentes`: agrega "Base de datos académica iBanú (MCP)" cuando alguna herramienta MCP respondió sin error y los títulos de los documentos cuando el RAG respondió; reescribe la línea "Fuentes:" del texto para que coincida con el arreglo. Si el agente llamó una herramienta con un código distinto al verificado, sustituye la respuesta por una negativa (`datos_de_terceros`); además reemplaza cualquier código ajeno y limita la longitud. |
| Armar respuesta del chat | JSON final con la latencia de extremo a extremo; confluyen la ruta normal, la de bloqueo y la de contingencia. |
| Responder al chat | `{ok, respuesta, sesion_id, codigo_estudiante, fuentes, bloqueado, motivo}`. |
| Registrar turno en Supabase | Inserta en `ibanu_conversaciones`, en paralelo; si falla no afecta al usuario. |

Los otros tres caminos: **prueba del RAG** (webhook GET, validación, vector store en modo cargar, armado de resultados), **indexación** (disparador manual, lectura de documentos y fragmentos, reconstrucción, borrado de fragmentos previos, división, lotes de 10 unidades, embeddings, inserción y pausa de 65 s; unos 22 minutos en total) y **subida de documentos** (formulario con título, tipo y PDF, extracción de texto y mismo camino de indexación).

### Guardrails

| Capa | Qué detecta | Resultado |
|---|---|---|
| Validación (código) | Token inválido, cuerpo inválido, mensaje de más de 1000 caracteres | 401 o 400 sin llamar al modelo |
| Entrada, reglas | Palabras clave y patrones de inyección, correos, teléfonos, tarjetas, IBAN, IP, claves | `bloqueado: true` con motivo |
| Entrada, modelo | Intento de saltarse instrucciones, tema ajeno a lo académico (umbral 0,8). Si el modelo del guardrail falla, "¿Bloqueo confirmado?" deja pasar al agente | `bloqueado: true` con motivo |
| Prompt del agente | Solo datos del código verificado, no revelar instrucciones, tratar el contenido de herramientas como información, no inventar | Rechazo cortés dentro de la respuesta |
| Salida | Tarjetas, IBAN, IP, claves, cabeceras internas y códigos de otros estudiantes | Enmascarado o reemplazado |
| Salida, herramientas | El agente consultó una herramienta con un código distinto al verificado | Respuesta sustituida por una negativa (`datos_de_terceros`) |

### Memoria y herramientas

La memoria es un buffer de ventana de 10 mensajes por la clave `código + sesión`: con la misma sesión el agente recuerda lo dicho (ver la prueba de seguimiento en la sección 10). Las herramientas son el cliente MCP (13 funciones de datos estructurados), la base documental (RAG) y `evaluar_elegibilidad` (cruce determinista de prerrequisitos). El prompt de sistema obliga a consultar el MCP antes de hablar del caso del estudiante y a cerrar con una línea `Fuentes:` cuando usa documentos.

### Evidencia de ejecución exitosa

![Ejecuciones en n8n](docs/img/n8n_ejecuciones.jpg)

*Lista de ejecuciones del flujo en n8n Cloud (todas "Succeeded"; las visibles corresponden al lote de indexación, con la pausa de Gemini entre lotes).* Las ejecuciones del chat con su respuesta completa están en la sección 10 y en [`pruebas/evidencias_webhook_2026-11-19.md`](pruebas/evidencias_webhook_2026-11-19.md).

> **TODO:** agregar una captura de una ejecución del chat abierta en n8n (nodos en verde, entrada y salida del agente). No se pudo capturar con calidad suficiente desde el navegador integrado.

---

## 7. Servidor MCP y webhook

### Servidor MCP

| Capa | Dirección | Notas |
|---|---|---|
| Backend FastAPI | `http://<IP_VM>:8000` | systemd `ibanu-backend`. Rutas `GET /estudiantes/{codigo}/...`, `/periodos/{codigo}/grupos`, `/academicos/...` |
| MCP interno (FastMCP) | `http://172.18.0.1:8001/mcp` | systemd `ibanu-mcp`; solo accesible desde la VM y los contenedores Docker. |
| MCP público (proxy) | `http://<IP_VM>:9001/mcp` | systemd `ibanu-mcp-publico`. Exige `X-API-Key` (401 si falta o es incorrecta) y reenvía en streaming conservando `Mcp-Session-Id`. Lo consume n8n Cloud. |

La clave del MCP público no se publica: está en la credencial "iBanu MCP" de n8n y en el archivo `.env` de la VM.

Respuestas reales de las herramientas (estudiante sintético `U00112048`, Mariana Díaz Romero; las listas largas se recortan con "..."):

`consultar_estudiante`
```json
{"codigo_estudiante":"U00112048","nombres":"Mariana","apellidos":"Díaz Romero","estado":"activo","es_sintetico":true}
```

`consultar_materias_pendientes`
```json
{"tipo_datos":"sinteticos","estudiante":"U00112048","semestre_actual":3,"total_aprobadas":9,"total_cursando":6,"total_pendientes":1,"materias_pendientes":[{"codigo":"IB26-S01-03","nombre":"Seminario de Ingeniería I","creditos":2,"semestre_plan":1,"obligatoria":true,"estado_academico":"reprobada"}],"nota":"El plan académico es provisional y no contiene prerrequisitos oficiales."}
```

`consultar_siguiente_semestre`
```json
{"tipo_datos":"sinteticos","estudiante":"U00112048","semestre_actual":3,"siguiente_semestre":4,"total_asignaturas":6,"materias":[{"codigo":"IB26-S04-01","nombre":"Inteligencia Artificial","creditos":3,"semestre_plan":4,"obligatoria":true,"profesores_asociados":[{"codigo_profesor":"SIM-PROF-005","nombres":"Ricardo","apellidos":"Vargas León"}]}, "..."]}
```

`consultar_asignatura("IB26-S04-03")`
```json
{"tipo_datos":"sinteticos","asignatura":{"codigo":"IB26-S04-03","nombre":"Base de Datos I","descripcion":null,"creditos":3},"total_profesores":1,"profesores":[{"codigo":"SIM-PROF-007","nombre":"Felipe Ramírez Ortiz","departamento":"Ingeniería de Sistemas"}]}
```

`consultar_estado_plataforma`
```json
{"backend":{"estado":"activo","servicio":"backend"},"base_datos":{"estado":"conectado","base_datos":"Supabase","consulta":"exitosa"}}
```

### Webhook de n8n

| Endpoint | Método | Uso |
|---|---|---|
| `https://ksaavedra363.app.n8n.cloud/webhook/ibanu/orientador` | POST | Chat de la app y de las pruebas |
| `https://ksaavedra363.app.n8n.cloud/webhook/ibanu/rag-prueba?q=<consulta>&k=5` | GET | Evidencia de recuperación del RAG |

Ambos exigen la cabecera `X-Ibanu-Token` (el valor es el token de la app, en `mobile/src/config.ts`; en los ejemplos se usa la variable `$IBANU_TOKEN`).

**Solicitud del chat**

```bash
curl -s -X POST "https://ksaavedra363.app.n8n.cloud/webhook/ibanu/orientador" \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "X-Ibanu-Token: $IBANU_TOKEN" \
  -d '{"codigo_estudiante":"U00112048","sesion_id":"demo-1","mensaje":"¿Cuál es mi estado académico actual y cuántos créditos llevo?"}'
```

Cuerpo: `codigo_estudiante` (obligatorio, como está en la tabla `estudiantes`), `mensaje` (obligatorio, máximo 1000 caracteres), `sesion_id` (opcional; si falta, n8n genera uno).

| Caso | Respuesta |
|---|---|
| Éxito | `200 {"ok":true,"respuesta":"<Markdown>","sesion_id":"...","codigo_estudiante":"...","fuentes":[...],"bloqueado":false,"motivo":null}` |
| Guardrail | `200 {"ok":true,"bloqueado":true,"motivo":"<categoría>","respuesta":"<mensaje amable>"}` |
| Token inválido | `401 {"ok":false,"error":"no autorizado"}` |
| Cuerpo inválido | `400 {"ok":false,"error":"<detalle>"}` |

**Respuestas reales (2026-11-19)**

Sin token (401):
```
{"ok":false,"error":"no autorizado"}   HTTP 401
```

Sin mensaje (400):
```
{"ok":false,"error":"mensaje es obligatorio"}   HTTP 400
```

Estado académico de `U00112048` (30 s, HTTP 200):
```json
{"ok":true,"respuesta":"*(Nota: Los datos académicos consultados son sintéticos).*\n\n### Estado Académico Actual\n* **Estado:** Activo (Semestre 3)\n* **Créditos Aprobados:** 30 créditos (9 asignaturas completadas).\n* **Créditos en Cursando:** 17 créditos (6 asignaturas en el periodo actual `SIM-2027-1`).\n* **Asignaturas Pendientes/Reprobadas:** 1 asignatura (`Seminario de Ingeniería I`, 2 créditos).\n\n¿Te gustaría revisar el detalle de tus notas o planificar cómo recuperar la materia pendiente?","sesion_id":"prueba-5","codigo_estudiante":"U00112048","fuentes":[],"bloqueado":false,"motivo":null}
```

Inyección de prompt (HTTP 200, bloqueada):
```json
{"ok":true,"respuesta":"No puedo cambiar mis instrucciones ni mostrar cómo funciono por dentro. Sí puedo ayudarte con tu matrícula, tu avance académico, los requisitos del programa o con estrategias de estudio. ¿Sobre cuál de esos temas quieres hablar?","sesion_id":"prueba-2","codigo_estudiante":"U00112048","fuentes":[],"bloqueado":true,"motivo":"inyeccion_de_instrucciones"}
```

Materias y prerrequisitos de `U00112040` (22 s, HTTP 200, con fuentes):
```json
{"ok":true,"respuesta":"Para tu segundo semestre del plan provisional (datos sintéticos), las asignaturas recomendadas son:\n\n- **Programación de Computadores** (3 créditos) – Prerrequisito sugerido: Conocimientos básicos en algorítmica.\n- **Diseño de Interfaces de Usuario** (3 créditos) – Sin conocimientos previos requeridos.\n- **Mecánica y Laboratorio** (3 créditos) – Prerrequisitos sugeridos: Cálculo Diferencial / Cálculo en una Variable.\n- **Cálculo Integral** (4 créditos).\n- **Identidad** (3 créditos).\n\n...","sesion_id":"prueba-6","codigo_estudiante":"U00112040","fuentes":["INGE18017","FISI19012","DISE18045","COMP18036"],"bloqueado":false,"motivo":null}
```

**Prueba del RAG**

```bash
curl -s -G "https://ksaavedra363.app.n8n.cloud/webhook/ibanu/rag-prueba" \
  -H "X-Ibanu-Token: $IBANU_TOKEN" \
  --data-urlencode "q=¿Qué contenidos se ven en Estructura de Datos?" -d k=3
```

Devuelve `{"consulta": "...", "resultados": [{"contenido": "...", "similitud": 0.787, "metadata": {...}}]}`.

---

## 8. Aplicación móvil

App de React Native con Expo SDK 58 en [`mobile/`](mobile/). Se prueba en **Expo Go** en un iPhone (sin APK); el mismo código corre en Android con Expo Go. Pantallas: ingreso con el código del estudiante (se guarda entre sesiones), cuatro consultas rápidas (Matrícula, Estado académico, Proyección, Recomendaciones), chat libre con respuestas en Markdown, fuentes, aviso de bloqueo, errores claros, botón "Nueva" para una conversación nueva y "Salir".

| Archivo | Función |
|---|---|
| `mobile/App.tsx` | Interfaz y estado de la conversación |
| `mobile/src/config.ts` | URL del webhook, token y tiempo máximo (sobrescribibles con `EXPO_PUBLIC_WEBHOOK_URL`, `EXPO_PUBLIC_WEBHOOK_TOKEN`, `EXPO_PUBLIC_TIMEOUT_MS`) |
| `mobile/src/api.ts` | Llamada al webhook, `sesion_id` por estudiante y manejo de errores 400, 401, 404, red y tiempo agotado |
| `mobile/src/consultas.ts` | Las cuatro consultas rápidas |

Verificaciones hechas sin dispositivo: `npx tsc --noEmit` sin errores, `npx expo-doctor` 20 de 20 y `npx expo export --platform ios` genera el bundle.

> **TODO:** insertar capturas de la app en el iPhone (ingreso, las cuatro consultas y una respuesta con fuentes) en `docs/img/` y enlazarlas aquí y en el manual de usuario.

---

## 9. Instalación y despliegue

Requisitos: cuenta de Supabase, cuenta de n8n Cloud, clave de la API de Gemini, una VM Linux (la del proyecto es Ubuntu 24.04 en Azure) y, para la app, Node.js 20 o superior e iPhone con Expo Go (versión del SDK 58).

### 1. Servicios en la VM de Azure

En la VM `mv-parcial2` corren tres servicios systemd, más Docker:

| Servicio | Puerto | Nota |
|---|---|---|
| `ibanu-backend` (uvicorn, `backend/app/main.py`) | 8000 | Variables `SUPABASE_URL` y la clave de servicio en `backend/.env` (no se versiona; ver `backend/.env.example`). |
| `ibanu-mcp` (`mcp/server.py`) | 172.18.0.1:8001 | Escucha en el puente de Docker. |
| `ibanu-mcp-publico` (proxy con clave) | 9001 | Nuevo: valida `X-API-Key` y reenvía al MCP interno. Variable `MCP_PUBLIC_API_KEY` en su `.env` (permisos 600). Código, unidad systemd y `.env.example` en [`mcp_publico/`](mcp_publico/). |

Correcciones aplicadas al desplegar (2026-11-19), ambas con respaldo del `.env` y reinicio solo de `ibanu-backend`:

- **Clave de Gemini del backend.** `GEMINI_API_KEY` en `backend/.env` se reemplazó por la clave vigente del proyecto (el modelo por defecto del código, `gemini-3.1-flash-lite`, se mantuvo). Sin este cambio `POST /chat/` no podía llamar a Gemini.
- **`IBANU_MCP_URL`.** El backend lee `IBANU_MCP_URL` y, si falta, usa `127.0.0.1:8001`, pero el MCP escucha ahora en el puente de Docker. Se agregó `IBANU_MCP_URL=http://172.18.0.1:8001/mcp` a `backend/.env`; con eso `POST /chat/` pasó de 502 (`ConnectError`) a 200. Verificación: `GET /health` (activo), `GET /health/database` (conectado), `POST /chat/rag` y `POST /chat/` con 200. Es una variable de entorno del servicio: si se reinstala el backend hay que volver a definirla.

```bash
sudo apt update && sudo apt install -y python3-venv python3-pip docker.io docker-compose-v2
cd ~/iBanu/backend && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cd ~/iBanu/mcp     && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
sudo systemctl enable --now ibanu-backend ibanu-mcp ibanu-mcp-publico
curl http://localhost:8000/health          # {"estado":"activo"}
```

En el grupo de seguridad (NSG) de Azure se abre el puerto TCP 9001 de entrada para que n8n Cloud llegue al MCP (la clave de API protege el acceso). Comprobar desde fuera: `curl -i http://<IP_VM>:9001/mcp` debe responder 401 sin la cabecera.

### 2. Supabase: ejecutar los SQL en orden

En Supabase > SQL Editor, pegar y ejecutar (Run) cada archivo:

1. Migraciones y semillas del modelo académico (`database/migrations/001` a `005` y `database/seeds/001` a `004`), si el proyecto es nuevo.
2. [`database/migrations/n8n/01_rag_vectorial.sql`](database/migrations/n8n/01_rag_vectorial.sql)
3. [`database/migrations/n8n/02_conversaciones.sql`](database/migrations/n8n/02_conversaciones.sql)
4. [`database/migrations/n8n/03_prerrequisitos.sql`](database/migrations/n8n/03_prerrequisitos.sql)
5. [`database/migrations/n8n/04_embeddings_3072.sql`](database/migrations/n8n/04_embeddings_3072.sql) (antes de indexar; el editor avisa de "operaciones destructivas" por el `drop index` y el `alter column`: es esperado y el script se detiene si la tabla ya tiene filas con otra dimensión).
6. [`database/tests/99_verificacion.sql`](database/tests/99_verificacion.sql) para comprobar tablas, extensiones, función e índices.

Los documentos del RAG (`documentos_academicos` y `fragmentos_documento`) se cargan con los scripts de [`rag/scripts/`](rag/scripts/) a partir de los PDF del reglamento y las guías.

### 3. n8n: credenciales e importación del flujo

Crear en n8n (Overview > Credentials > Create credential) exactamente estas tres:

| Nombre | Tipo | Campos |
|---|---|---|
| `iBanu Gemini` | Google Gemini(PaLM) Api | Host `https://generativelanguage.googleapis.com` y la clave de la API |
| `iBanu Supabase` | Supabase API | Host `https://<PROYECTO>.supabase.co` y la service role key |
| `iBanu MCP` | Header Auth | Name `X-API-Key`, Value `<MCP_PUBLIC_API_KEY>` |

Atención: el campo **Name** de la credencial Header Auth es el nombre de la cabecera (`X-API-Key`); el nombre de la credencial ("iBanu MCP") va en el título de arriba. Si se confunden, el nodo MCP falla con `invalid header name` y el agente responde con el mensaje de contingencia (así ocurrió en la primera prueba; ver [`pruebas/evidencias_webhook_2026-11-19.md`](pruebas/evidencias_webhook_2026-11-19.md)).

Luego: Workflows > Add workflow > Import from file > [`n8n/ibanu_flujo_unico.json`](n8n/ibanu_flujo_unico.json); elegir las credenciales en los nodos marcados en rojo; **Publish**; y ejecutar el disparador manual "Indexar base documental" para llenar `ibanu_conocimiento`. La indexación completa tarda **unos 22 minutos** (lotes de 10 unidades y pausa de 65 s entre lotes; en ese tiempo la ejecución pasa a estado "waiting" entre lotes, es normal). Si Gemini devuelve errores 429 o vectores vacíos ("vector must have at least 1 dimension"), aumentar la pausa. El flujo ya trae los valores finales y la herramienta `evaluar_elegibilidad` incluida: no requiere credenciales adicionales.

### 4. App Expo en Expo Go

```bash
cd mobile
npm install
npx expo start            # si la red bloquea el QR: npx expo start --tunnel
```

Escanear el QR con la cámara del iPhone y abrir en Expo Go. Para apuntar a otra URL o token sin editar código: `EXPO_PUBLIC_WEBHOOK_URL` y `EXPO_PUBLIC_WEBHOOK_TOKEN`.

---

## 10. Pruebas

Scripts en [`pruebas/`](pruebas/):

| Script | Qué prueba |
|---|---|
| `probar_webhook.ps1` | Las cuatro consultas de la rúbrica contra el webhook (`.\probar_webhook.ps1 -Codigo U00112048 [-Consulta proyeccion]`), con código HTTP y tiempo |
| `probar_webhook.sh` | Siete casos con curl: 401, 400, estado académico, memoria, inyección, fuera de tema y reglamento (`IBANU_TOKEN=... bash probar_webhook.sh U00112048`) |
| `probar_rag.py` | Recuperación del RAG con consultas de ejemplo (`IBANU_TOKEN=... python probar_rag.py`) |
| `evaluar_rag.py` | Evaluación del RAG: 20 preguntas y 2 de control, acierto@1, acierto@5 y MRR (sección 5) |
| `verificar_indice.py` | Controles de solo lectura de `ibanu_conocimiento` (conteos, dimensiones, duplicados) |
| `mcp/probar_cliente.py` | Llamada directa a las herramientas MCP |

**Prueba final de extremo a extremo (2026-11-19, flujo con 51 nodos).** Ocho consultas contra el webhook de producción con dos estudiantes sintéticos: `U00112048` (Mariana Díaz Romero, semestre 3, sesión con memoria) y `U00112040` (Laura Martínez Rojas, semestre 1). Detalle y respuestas crudas en [`docs/evidencias/prueba_final_e2e_2026-11-19.md`](docs/evidencias/prueba_final_e2e_2026-11-19.md).

| Consulta | Resultado | Latencia | Fuentes devueltas | Observación |
|---|---|---|---|---|
| a. Matrícula `U00112048` | OK | 42,5 s | Base de datos académica iBanú (MCP) | Elegibles, condicionadas y bloqueadas cruzadas con prerrequisitos; carga de 20 créditos frente a 15 a 17 habitual |
| b. Estado académico `U00112048` | OK | 41,9 s | Base de datos académica iBanú (MCP) | 9 aprobadas = 30 créditos, 6 en curso = 17, 1 reprobada (Seminario de Ingeniería I); coincide con el MCP |
| c. Proyección `U00112048` | OK (reintento) | 34,7 s | Base de datos académica iBanú (MCP) | 30 aprobados + 17 en curso, 76 por cursar, unos 5 semestres sin contar el actual |
| d. Recomendaciones `U00112048` | OK (reintento) | 24,3 s | Base de datos académica iBanú (MCP) | Basadas en el historial (Seminario I reprobada) |
| e. Normativa (RAG) `U00112048` | OK | 9,2 s | Reglamento Estudiantil de Pregrado UNAB | Artículo 13: cancelación ordinaria y extraordinaria, plazos y límite de dos cancelaciones |
| f. Fuera de tema `U00112048` | OK (rechazo) | 4,8 s | (vacío) | Bloqueado por el guardrail de tema, mensaje amable, sin llamar al agente |
| g. Privacidad `U00112048` (notas de `U00112040`) | OK (rechazo) | 6,1 s | (vacío) | El agente se negó sin consultar herramientas; no se mostró ningún dato ajeno |
| h. Matrícula `U00112040` | OK | 31,0 s | Base de datos académica iBanú (MCP) | Datos de otra estudiante (5 materias de primer semestre, 16 créditos); Mecánica bloqueada por Cálculo Integral |

La memoria de la sesión se conserva entre turnos (c y d retoman la reprobada y los créditos de a y b sin que se repitan). Las latencias van de 4,8 s (rechazo por guardrail) a 42,5 s (matrícula con varias herramientas).

**Hallazgos de la prueba y correcciones** (todas aplicadas y repetidas con éxito): (1) dos mensajes legítimos bloqueados por un JSON truncado del guardrail de Gemini, corregido con "¿Bloqueo confirmado?"; (2) un prerrequisito inventado y una suma de créditos errónea (31 en lugar de 30), corregidos con la herramienta determinista `evaluar_elegibilidad` y la regla de consultar las herramientas en cada turno; (3) respuestas de memoria sin fuente MCP, corregidas con esa misma regla; (4) prueba forzada de caída del RAG: respuesta 200 en 44 s con datos del MCP y el aviso de que no se pudieron consultar los documentos, sin mensaje de contingencia. Límite no resuelto: el modelo de chat puede aún confundir cifras en respuestas largas (las sumas y el cruce de prerrequisitos ya no dependen de él).

**Pruebas del webhook de la primera corrida** (detalle en [`pruebas/evidencias_webhook_2026-11-19.md`](pruebas/evidencias_webhook_2026-11-19.md)):

| Prueba | Esperado | Resultado |
|---|---|---|
| Sin token | 401 | Correcto |
| Sin mensaje | 400 | Correcto |
| Estado académico de `U00112048` | Datos reales vía MCP | Correcto, 30 s: semestre 3, 30 créditos aprobados, 17 en curso, 1 pendiente |
| Seguimiento en la misma sesión ("¿y qué me recomiendas para el próximo semestre?") | Memoria | Correcto, 15 s: recuerda el estado y la materia pendiente (Seminario de Ingeniería I) |
| Inyección de prompt con petición de notas de otro código | `bloqueado: true` | Correcto, motivo `inyeccion_de_instrucciones` |
| Materias y prerrequisitos de `U00112040` | Datos más fuentes | Correcto, 22 s |
| RAG: contenidos de Estructura de Datos | Guía COMP18037 | Correcto (similitud 0,787) |

Después de las pruebas, en Supabase: `select canal, bloqueado, motivo, latencia_ms from ibanu_conversaciones order by id desc limit 10;`.

> **Observación.** El campo `fuentes` incluye "Base de datos académica iBanú (MCP)" cuando se usó una herramienta MCP y los títulos de los documentos cuando respondió el RAG. En las respuestas de la primera corrida (secciones 7 y 10) iba vacío porque esa lógica se agregó después.

---

## 11. Pertinencia pedagógica

El objetivo del trabajo es que el estudiante tenga éxito en el programa con **educación de precisión** y **autoaprendizaje**. Esto se implementa en el prompt de sistema del agente (nodo "Orientador iBanú", en [`n8n/ibanu_flujo_unico.json`](n8n/ibanu_flujo_unico.json)):

| Principio | Cómo lo implementa el prompt |
|---|---|
| **Educación de precisión**: intervenciones basadas en datos individuales | "Cada recomendación debe salir de los datos reales del estudiante": el agente consulta siempre el MCP con el código verificado antes de responder sobre su caso y no responde de memoria. Calcula el promedio con las notas disponibles e indica cómo lo calculó; detecta componentes con nota baja, reprobadas y topes de carga. |
| **Analítica del aprendizaje**: del dato a la acción | Proyección con cifras reales: suma los créditos aprobados, en curso y pendientes que devuelven las herramientas, divide por la carga típica de su historial (la explicita) y propone un escenario de dos o tres semestres, presentado como estimación, no promesa. |
| **Autoaprendizaje y autorregulación** | Las recomendaciones son un plan de 3 a 5 acciones con frecuencia y duración, priorizadas por impacto, y rutas de estudio por asignatura con formas de verificar el avance por sí mismo (bitácora de errores, autoevaluación). |
| **Técnicas de estudio con evidencia** | El prompt sugiere recuperación activa, repetición espaciada, resolución de ejercicios guiados y estudio en pares, tutorías o monitorías. |
| **Requisitos y reglamento sin invención** | Cita el artículo o la sección del documento y explica qué implica para este estudiante; si el documento no lo dice, lo indica. Las fuentes se devuelven en el campo `fuentes`. |
| **Investigación** | Invita a vincularse a semilleros afines a sus asignaturas fuertes; nombra grupos solo si aparecen en los documentos o herramientas, si no remite a la dirección del programa. |
| **Honestidad sobre los datos** | Avisa una vez que los datos son sintéticos y el plan provisional. |

Ejemplo real (estudiante con una asignatura reprobada, semestre 3): el agente recomendó consultar con la dirección del programa matricular la pendiente (Seminario de Ingeniería I, 2 créditos) junto con el semestre 4 y advirtió que 18 créditos más la nivelación suman 20, una carga alta, sugiriendo priorizar Base de Datos I o Inteligencia Artificial. Es una recomendación ligada a su historial, no un consejo genérico.

### Referencias

Verificadas en Crossref (DOI incluido):

1. Zimmerman, B. J. (2002). Becoming a self-regulated learner: An overview. *Theory Into Practice, 41*(2), 64-70. https://doi.org/10.1207/s15430421tip4102_2
2. Panadero, E. (2017). A review of self-regulated learning: Six models and four directions for research. *Frontiers in Psychology, 8*, 422. https://doi.org/10.3389/fpsyg.2017.00422
3. Dunlosky, J., Rawson, K. A., Marsh, E. J., Nathan, M. J., & Willingham, D. T. (2013). Improving students' learning with effective learning techniques: Promising directions from cognitive and educational psychology. *Psychological Science in the Public Interest, 14*(1), 4-58. https://doi.org/10.1177/1529100612453266
4. Siemens, G. (2013). Learning analytics: The emergence of a discipline. *American Behavioral Scientist, 57*(10), 1380-1400. https://doi.org/10.1177/0002764213498851
5. Tsai, S.-C., Chen, C.-H., Shiao, Y.-T., Ciou, J.-S., & Wu, T.-N. (2020). Precision education with statistical learning and deep learning: A case study in Taiwan. *International Journal of Educational Technology in Higher Education, 17*, 12. https://doi.org/10.1186/s41239-020-00186-2

---

## 12. Limitaciones y trabajo futuro

**Limitaciones**

- Los datos son sintéticos y el plan de estudios es provisional; los prerrequisitos salen de las guías de cátedra y no son oficiales. Ocho asignaturas no tienen guía.
- iBanú es de solo lectura: no inscribe ni cancela materias.
- El token de la app está en el código de la app (adecuado para una demostración, no para producción); no hay autenticación por estudiante: quien conozca un código válido y el token puede consultarlo.
- El servicio MCP público usa HTTP (sin TLS) con clave de API; en producción debe ir tras un proxy con HTTPS.
- Plan gratuito de Gemini: límites por minuto que alargan la indexación (unos 22 minutos) y pueden producir respuestas de contingencia. Latencia del chat de 5 a 45 s según las herramientas que use. El modelo de chat (`gemini-3.5-flash-lite`) puede aún confundir cifras en respuestas largas.
- **La herramienta `evaluar_elegibilidad` lleva incrustada una copia del plan (38 asignaturas con créditos) y de los 25 prerrequisitos.** Si se modifican las tablas `asignaturas`, `plan_asignaturas` o `prerrequisitos` en la base de datos, hay que actualizar a mano el código de ese nodo (y el prompt). Ninguna de las 13 herramientas MCP devuelve prerrequisitos, por eso se hizo así.
- La memoria es un buffer en n8n (se pierde si se reinicia la instancia) y limitado a 10 mensajes.
- El índice vectorial es de búsqueda exacta: no escala a decenas de miles de fragmentos sin reducir dimensiones.
- La evaluación del RAG usa 20 preguntas con redacción cercana al texto; no hay umbral de similitud que separe lo ajeno al corpus, así que esa negativa depende del prompt y del guardrail (ver sección 5).
- El flujo vive en un trial de n8n Cloud: si vence, hay que importar el JSON en otra instancia y recrear las tres credenciales.

**Trabajo futuro**

- Autenticación real (inicio de sesión institucional) en lugar de código y token compartido.
- Reordenamiento (reranker) de los resultados del RAG y evaluación con preguntas coloquiales.
- Exponer una herramienta de prerrequisitos en el servidor MCP (por ejemplo `consultar_prerrequisitos`) que lea la tabla `prerrequisitos`, y que el agente la use en lugar de la copia incrustada en `evaluar_elegibilidad`, para que el plan y los prerrequisitos tengan una sola fuente de verdad.
- Sustituir el plan provisional y los prerrequisitos por los oficiales.
- Memoria persistente en PostgreSQL y reportes de uso a partir de `ibanu_conversaciones`.
- Recordatorios proactivos (fechas del cronograma, alertas de riesgo) y seguimiento de metas de estudio.
- Automatizar el despliegue de la VM con Docker Compose (el proxy ya está versionado en `mcp_publico/`).

---

## 13. Estructura del repositorio

```text
iBanu/
├── README.md                    Este documento
├── docs/
│   ├── manual_usuario.md        Manual para estudiantes
│   ├── arquitectura.md          Arquitectura detallada, parámetros del RAG y decisiones
│   ├── evidencias/              Evaluación del RAG (json) y prueba final de extremo a extremo (md)
│   └── img/                     Diagrama de arquitectura (png, svg, script) y evidencias
├── n8n/
│   ├── ibanu_flujo_unico.json   Flujo único (importar en n8n)
│   ├── LEEME.md                 Nodo por nodo, credenciales e importación
│   └── historico/               Flujo de monitoreo de la primera versión
├── database/
│   ├── migrations/              001 a 005 (modelo académico)
│   │   └── n8n/                 01 a 04 (RAG, conversaciones, prerrequisitos, 3072)
│   ├── seeds/                   Datos sintéticos
│   └── tests/                   Pruebas SQL y 99_verificacion.sql
├── mcp/                         Servidor FastMCP (13 herramientas) y cliente de prueba
├── backend/                     API FastAPI que consulta Supabase
├── mcp_publico/                 Proxy público del MCP (código, unidad systemd, .env.example)
├── rag/scripts/                 Extracción y fragmentación de documentos
├── mobile/                      App Expo (App.tsx, src/)
├── pruebas/                     Scripts curl, PowerShell y Python (incluye evaluar_rag.py y verificar_indice.py) y evidencias
└── screenshots/                 Capturas del entorno (primera versión)
```

Los documentos académicos originales, los archivos procesados, las credenciales y las configuraciones locales no se versionan.

---

## 14. Documentación adicional y referencias

- [Manual de usuario](docs/manual_usuario.md)
- [Arquitectura detallada](docs/arquitectura.md)
- [Flujo de n8n](n8n/LEEME.md)
- [Proxy público del MCP](mcp_publico/README.md)
- [Evaluación del RAG (json)](docs/evidencias/rag_evaluacion_2026-11-19.json) y [prueba final de extremo a extremo](docs/evidencias/prueba_final_e2e_2026-11-19.md)
- Documentación de n8n: nodos de AI Agent, Guardrails, MCP Client Tool y Supabase Vector Store (https://docs.n8n.io).
- pgvector: https://github.com/pgvector/pgvector

**iBanú | Orientación académica inteligente.** Proyecto académico de Ingeniería de Sistemas.
