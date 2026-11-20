-- =====================================================================
-- iBanu - 01_rag_vectorial.sql
-- Almacen vectorial del RAG (pgvector) para el nodo "Supabase Vector Store"
-- de n8n. Script idempotente: se puede ejecutar varias veces sin error.
-- Ejecutar en Supabase > SQL Editor. Solo agrega objetos nuevos; no toca
-- ninguna tabla existente (fragmentos_documento queda intacta).
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. Extension pgvector
-- Decision: el esquema ya expone el tipo public.vector, asi que la
-- extension esta instalada; "if not exists" la deja como esta y solo la
-- crea en un proyecto limpio. Es lo que permite columnas vector(N) y los
-- operadores de distancia (<=> coseno).
-- ---------------------------------------------------------------------
create extension if not exists vector;

-- ---------------------------------------------------------------------
-- 2. Tabla public.ibanu_conocimiento
-- Decision: tabla NUEVA y separada de fragmentos_documento por tres
-- razones: (a) fragmentos_documento tiene la columna embedding sin
-- dimension (tipo vector abierto), que no admite indice HNSW; (b) los
-- fragmentos actuales se cortaron por pagina de PDF con solape de 300
-- caracteres y se van a re-fragmentar por unidad semantica; (c) el nodo
-- Supabase Vector Store de n8n exige exactamente las columnas id, content,
-- metadata y embedding. La dimension 768 corresponde a gemini-embedding-001
-- con outputDimensionality = 768 (contrato del proyecto).
-- metadata (jsonb) guarda el origen de cada fragmento: tipo, titulo,
-- articulo, pagina, codigo de asignatura, etc. Sirve para citar fuentes y
-- para filtrar con el operador @>.
-- ---------------------------------------------------------------------
create table if not exists public.ibanu_conocimiento (
    id        bigserial primary key,
    content   text        not null,
    metadata  jsonb       not null default '{}'::jsonb,
    embedding vector(768)
);

comment on table public.ibanu_conocimiento is
    'Fragmentos del RAG de iBanu con su embedding (gemini-embedding-001, 768 dimensiones). Los escribe n8n con la service role.';
comment on column public.ibanu_conocimiento.metadata is
    'jsonb con tipo (reglamento, guia_catedra, programa, competencias), titulo, articulo, pagina, codigo_asignatura, etc.';

-- ---------------------------------------------------------------------
-- 3. Indice vectorial HNSW por coseno
-- Decision: HNSW (no IVFFlat) porque no requiere entrenar el indice con
-- datos previos, funciona bien con una tabla que crece por tandas y da
-- mejor recall con pocos miles de vectores. vector_cosine_ops porque los
-- embeddings de Gemini se comparan por angulo y la funcion de busqueda usa
-- el operador <=> (distancia coseno). m = 16 y ef_construction = 64 son
-- los valores por defecto de pgvector: suficientes para este volumen
-- (centenas a pocos miles de fragmentos).
-- ---------------------------------------------------------------------
create index if not exists ibanu_conocimiento_embedding_hnsw
    on public.ibanu_conocimiento
    using hnsw (embedding vector_cosine_ops)
    with (m = 16, ef_construction = 64);

-- Indice GIN para acelerar el filtro metadata @> filter de la funcion.
create index if not exists ibanu_conocimiento_metadata_gin
    on public.ibanu_conocimiento
    using gin (metadata jsonb_path_ops);

-- ---------------------------------------------------------------------
-- 4. Funcion de busqueda public.ibanu_buscar_conocimiento
-- Decision: la firma (query_embedding, match_count, filter) y las columnas
-- de salida (id, content, metadata, similarity) son las que el nodo de n8n
-- espera al configurar "Query Name". filter se aplica con metadata @> filter
-- (el filtro vacio '{}' coincide con todo). similarity = 1 - distancia
-- coseno, por lo que 1 es identico y valores cercanos a 0 son no
-- relacionados. Se declara stable y con search_path fijo para que el
-- operador <=> se resuelva siempre y la funcion no dependa de la sesion.
-- ---------------------------------------------------------------------
create or replace function public.ibanu_buscar_conocimiento(
    query_embedding vector(768),
    match_count     int   default 5,
    filter          jsonb default '{}'::jsonb
)
returns table (
    id         bigint,
    content    text,
    metadata   jsonb,
    similarity float
)
language plpgsql
stable
set search_path = public, extensions
as $$
begin
    return query
    select
        c.id,
        c.content,
        c.metadata,
        (1 - (c.embedding <=> query_embedding))::float as similarity
    from public.ibanu_conocimiento c
    where c.embedding is not null
      and c.metadata @> filter
    order by c.embedding <=> query_embedding
    limit match_count;
end;
$$;

comment on function public.ibanu_buscar_conocimiento(vector, int, jsonb) is
    'Busqueda semantica por coseno para el nodo Supabase Vector Store de n8n. similarity = 1 - distancia coseno; filter se aplica con metadata @> filter.';

-- ---------------------------------------------------------------------
-- 5. Seguridad: RLS y permisos
-- Decision: la tabla contiene contenido institucional y solo debe leerse y
-- escribirse desde n8n con la service role. Se activa RLS sin ninguna
-- politica: anon y authenticated no ven ni una fila; service_role omite
-- RLS por diseno de Supabase. Ademas se revocan los permisos por defecto
-- y se concede solo a service_role (cinturon y tirantes).
-- ---------------------------------------------------------------------
alter table public.ibanu_conocimiento enable row level security;

revoke all on table public.ibanu_conocimiento from anon, authenticated;
grant all on table public.ibanu_conocimiento to service_role;
grant usage, select on sequence public.ibanu_conocimiento_id_seq to service_role;

revoke all on function public.ibanu_buscar_conocimiento(vector, int, jsonb) from public, anon, authenticated;
grant execute on function public.ibanu_buscar_conocimiento(vector, int, jsonb) to service_role;

-- Verificacion rapida (debe devolver 0 filas hasta que n8n indexe):
-- select count(*) from public.ibanu_conocimiento;
