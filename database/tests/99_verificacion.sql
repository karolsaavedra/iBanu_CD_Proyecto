-- =====================================================================
-- iBanu - 99_verificacion.sql
-- Consultas de solo lectura para mostrar evidencia de la base de datos
-- (criterios "Base de datos PostgreSQL" y "RAG" de la rubrica).
-- Ejecutar cada bloque por separado en el SQL Editor de Supabase y
-- capturar el resultado.
-- =====================================================================

-- 1. Tablas del esquema public con numero exacto de filas
select table_name as tabla,
       (xpath('/row/c/text()',
              query_to_xml(format('select count(*) as c from public.%I', table_name),
                           false, true, '')))[1]::text::int as filas
from information_schema.tables
where table_schema = 'public' and table_type = 'BASE TABLE'
order by table_name;

-- 2. Extensiones instaladas (debe aparecer vector)
select extname as extension, extversion as version
from pg_extension
order by extname;

-- 3. Funcion de busqueda vectorial y su firma
select p.proname as funcion,
       pg_get_function_arguments(p.oid) as argumentos,
       pg_get_function_result(p.oid) as resultado
from pg_proc p
join pg_namespace n on n.oid = p.pronamespace
where n.nspname = 'public' and p.proname = 'ibanu_buscar_conocimiento';

-- 4. Indices de las tablas nuevas (debe aparecer el HNSW por coseno)
select tablename, indexname, indexdef
from pg_indexes
where schemaname = 'public'
  and tablename in ('ibanu_conocimiento', 'ibanu_conversaciones')
order by tablename, indexname;

-- 5. RLS activo en las tablas nuevas
select relname as tabla, relrowsecurity as rls_activo
from pg_class
where relnamespace = 'public'::regnamespace
  and relname in ('ibanu_conocimiento', 'ibanu_conversaciones');

-- 6. Muestra de estudiantes
select codigo_estudiante, nombres, apellidos, anio_ingreso, semestre_actual, estado
from public.estudiantes
order by codigo_estudiante
limit 5;

-- 7. Muestra de asignaturas con su semestre en el plan
select pa.semestre, a.codigo, a.nombre, a.creditos
from public.plan_asignaturas pa
join public.asignaturas a on a.id = pa.asignatura_id
order by pa.semestre, a.codigo
limit 10;

-- 8. Muestra de matriculas (estudiante, asignatura, grupo, estado)
select e.codigo_estudiante, a.codigo as asignatura, g.codigo_grupo,
       m.estado, m.fecha_matricula
from public.matriculas m
join public.estudiantes e on e.id = m.estudiante_id
join public.grupos g on g.id = m.grupo_id
join public.asignaturas a on a.id = g.asignatura_id
order by m.fecha_matricula desc
limit 5;

-- 9. Muestra de notas (con estudiante y asignatura)
select e.codigo_estudiante, a.codigo as asignatura, n.componente,
       n.calificacion, n.porcentaje
from public.notas n
join public.matriculas m on m.id = n.matricula_id
join public.estudiantes e on e.id = m.estudiante_id
join public.grupos g on g.id = m.grupo_id
join public.asignaturas a on a.id = g.asignatura_id
order by n.fecha_registro desc
limit 5;

-- 10. Muestra de prerrequisitos (nombres legibles)
select a.codigo as asignatura, p.codigo as requiere
from public.prerrequisitos r
join public.asignaturas a on a.id = r.asignatura_id
join public.asignaturas p on p.id = r.prerrequisito_id
order by a.codigo
limit 10;

-- 11. Conocimiento indexado por tipo de documento
select coalesce(metadata->>'tipo', '(sin tipo)') as tipo,
       count(*) as fragmentos,
       count(embedding) as con_embedding
from public.ibanu_conocimiento
group by 1
order by 2 desc;

-- 12. Conversaciones registradas (despues de las pruebas del chat)
select creado_en, codigo_estudiante, canal, bloqueado, motivo, latencia_ms,
       left(mensaje, 60) as mensaje
from public.ibanu_conversaciones
order by creado_en desc
limit 10;
