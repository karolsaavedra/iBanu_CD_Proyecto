-- =====================================================================
-- iBanu - 04_embeddings_3072.sql
-- Migracion: la tabla public.ibanu_conocimiento pasa de vector(768) a
-- vector(3072). Idempotente: se puede ejecutar varias veces. Ejecutar en
-- Supabase > SQL Editor despues de 01_rag_vectorial.sql y ANTES de indexar.
--
-- Por que: el nodo nativo "Embeddings Google Gemini" de n8n no permite
-- fijar outputDimensionality y la API entrega 3072 valores por defecto.
-- Para que el flujo use solo ese nodo nativo, la columna debe aceptar 3072.
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. Proteccion: solo se altera la columna si la tabla esta vacia.
-- Cambiar la dimension de una columna con vectores de 768 los dejaria
-- invalidos; en ese caso se aborta con un aviso claro y no se toca nada.
-- (Si la columna ya es vector(3072), el script continua sin problema.)
-- ---------------------------------------------------------------------
do $$
declare
    filas bigint;
    dim   int;
begin
    select count(*) into filas from public.ibanu_conocimiento;
    select a.atttypmod into dim
    from pg_attribute a
    where a.attrelid = 'public.ibanu_conocimiento'::regclass
      and a.attname = 'embedding' and not a.attisdropped;
    if filas > 0 and dim is distinct from 3072 then
        raise exception 'ibanu_conocimiento tiene % filas con embeddings de % dimensiones. No se altera la columna. Vacia la tabla (truncate table public.ibanu_conocimiento) y vuelve a ejecutar este script; luego reindexa desde n8n.', filas, dim;
    end if;
end $$;

-- ---------------------------------------------------------------------
-- 2. Decision de indexado: busqueda exacta, sin indice vectorial.
-- pgvector limita el indice HNSW sobre el tipo vector a 2000 dimensiones,
-- y 3072 no cabe. Opciones: (a) indice HNSW sobre la expresion
-- embedding::halfvec(3072), con la funcion ordenando por el mismo cast; o
-- (b) busqueda exacta. Se elige (b): el corpus tiene del orden de 400 a
-- 500 fragmentos, un recorrido secuencial calcula 500 distancias en pocos
-- milisegundos, el recall es 100 % (un indice aproximado puede dejar
-- fuera resultados) y no hay que mantener un indice ni depender del cast.
-- Si el corpus creciera a decenas de miles de filas, se agrega el indice
-- sobre halfvec (ver el bloque comentado al final).
-- ---------------------------------------------------------------------
drop index if exists public.ibanu_conocimiento_embedding_hnsw;

-- ---------------------------------------------------------------------
-- 3. Columna a 3072 dimensiones (la tabla esta vacia o ya es 3072).
-- ---------------------------------------------------------------------
alter table public.ibanu_conocimiento
    alter column embedding type vector(3072);

comment on table public.ibanu_conocimiento is
    'Fragmentos del RAG de iBanu con su embedding (gemini-embedding-001, 3072 dimensiones, busqueda exacta por coseno). Los escribe n8n con la service role.';

-- ---------------------------------------------------------------------
-- 4. Funcion de busqueda con la nueva firma. Se elimina la de 768 para
-- que no queden dos sobrecargas y n8n no resuelva la equivocada. Misma
-- salida (id, content, metadata, similarity), mismo search_path y mismo
-- criterio: similarity = 1 - distancia coseno; filter con metadata @> filter.
-- ---------------------------------------------------------------------
drop function if exists public.ibanu_buscar_conocimiento(vector(768), int, jsonb);

create or replace function public.ibanu_buscar_conocimiento(
    query_embedding vector(3072),
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
    'Busqueda semantica exacta por coseno (3072 dimensiones) para el nodo Supabase Vector Store de n8n. similarity = 1 - distancia coseno; filter se aplica con metadata @> filter.';

-- ---------------------------------------------------------------------
-- 5. Permisos (se repiten por si la funcion se recreo)
-- ---------------------------------------------------------------------
revoke all on function public.ibanu_buscar_conocimiento(vector, int, jsonb) from public, anon, authenticated;
grant execute on function public.ibanu_buscar_conocimiento(vector, int, jsonb) to service_role;

-- ---------------------------------------------------------------------
-- Opcional, solo si el corpus crece mucho: indice aproximado sobre halfvec.
-- La funcion tendria que ordenar por (c.embedding::halfvec(3072)) <=>
-- (query_embedding::halfvec(3072)) para que el planificador lo use.
--
-- create index ibanu_conocimiento_embedding_hnsw
--     on public.ibanu_conocimiento
--     using hnsw ((embedding::halfvec(3072)) halfvec_cosine_ops);
-- ---------------------------------------------------------------------

-- Verificacion: debe mostrar vector(3072) y la funcion con vector(3072).
-- select format_type(a.atttypid, a.atttypmod) from pg_attribute a
--  where a.attrelid = 'public.ibanu_conocimiento'::regclass and a.attname = 'embedding';
-- select pg_get_function_arguments(oid) from pg_proc where proname = 'ibanu_buscar_conocimiento';
