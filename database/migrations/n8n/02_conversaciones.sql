-- =====================================================================
-- iBanu - 02_conversaciones.sql
-- Registro de conversaciones del orientador (auditoria, metricas de
-- latencia y evidencia de guardrails). Idempotente. Ejecutar en el SQL
-- Editor de Supabase. Solo agrega objetos nuevos.
-- =====================================================================

-- Decision: una fila por turno (mensaje + respuesta) en vez de un hilo
-- completo, porque n8n inserta una vez al final de cada ejecucion y asi se
-- calcula la latencia por consulta. sesion_id agrupa los turnos de una
-- misma conversacion; canal identifica el origen (app, curl, prueba).
-- bloqueado y motivo registran los casos detenidos por guardrails.
-- codigo_estudiante no lleva clave foranea a estudiantes a proposito:
-- tambien se deben registrar intentos con codigos inexistentes.
create table if not exists public.ibanu_conversaciones (
    id                bigserial primary key,
    creado_en         timestamptz not null default now(),
    codigo_estudiante text,
    sesion_id         text,
    canal             text,
    mensaje           text,
    respuesta         text,
    bloqueado         boolean not null default false,
    motivo            text,
    latencia_ms       int
);

comment on table public.ibanu_conversaciones is
    'Un registro por turno del chat de iBanu: mensaje, respuesta, si un guardrail lo bloqueo y la latencia.';

-- Decision: el patron de consulta es "historial de un estudiante ordenado
-- por fecha", por eso el indice compuesto (codigo_estudiante, creado_en).
create index if not exists idx_ibanu_conversaciones_estudiante_fecha
    on public.ibanu_conversaciones (codigo_estudiante, creado_en);

-- Indice auxiliar para recuperar una sesion completa.
create index if not exists idx_ibanu_conversaciones_sesion
    on public.ibanu_conversaciones (sesion_id);

-- Decision: mismas reglas de seguridad que el resto de objetos nuevos.
-- RLS activo sin politicas: solo la service role (n8n) lee y escribe.
alter table public.ibanu_conversaciones enable row level security;

revoke all on table public.ibanu_conversaciones from anon, authenticated;
grant all on table public.ibanu_conversaciones to service_role;
grant usage, select on sequence public.ibanu_conversaciones_id_seq to service_role;
