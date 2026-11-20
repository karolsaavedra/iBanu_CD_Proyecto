
BEGIN;

-- 1. Preparar las asignaciones y horarios simulados.
CREATE TEMP TABLE tmp_grupos_plan ON COMMIT DROP AS
WITH profesor_principal AS (
    SELECT DISTINCT ON (pa.asignatura_id)
        pa.asignatura_id,
        pa.profesor_id
    FROM public.profesores_asignaturas pa
    JOIN public.profesores p
        ON p.id = pa.profesor_id
    WHERE pa.activo = TRUE
      AND p.es_sintetico = TRUE
    ORDER BY
        pa.asignatura_id,
        pa.created_at,
        pa.profesor_id
),
base AS (
    SELECT
        a.id AS asignatura_id,
        a.codigo AS codigo_asignatura,
        pp.profesor_id,
        per.id AS periodo_id
    FROM public.asignaturas a
    JOIN profesor_principal pp
        ON pp.asignatura_id = a.id
    CROSS JOIN public.periodos_academicos per
    WHERE a.activa = TRUE
      AND per.es_sintetico = TRUE
),
numerados AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY periodo_id, profesor_id
            ORDER BY codigo_asignatura
        ) AS turno
    FROM base
)
SELECT
    asignatura_id,
    profesor_id,
    periodo_id,
    'G01'::varchar AS codigo_grupo,
    30::integer AS cupo,
    ((turno - 1) / 5 + 1)::smallint AS dia_semana,
    CASE ((turno - 1) % 5)
        WHEN 0 THEN TIME '07:00'
        WHEN 1 THEN TIME '09:00'
        WHEN 2 THEN TIME '11:00'
        WHEN 3 THEN TIME '14:00'
        ELSE TIME '16:00'
    END AS hora_inicio
FROM numerados;

-- 2. Crear los grupos.
INSERT INTO public.grupos (
    asignatura_id,
    profesor_id,
    periodo_id,
    codigo_grupo,
    cupo,
    modalidad,
    lugar,
    estado,
    es_sintetico
)
SELECT
    asignatura_id,
    profesor_id,
    periodo_id,
    codigo_grupo,
    cupo,
    'presencial',
    'Aula simulada',
    'activo',
    TRUE
FROM tmp_grupos_plan
ON CONFLICT (asignatura_id, periodo_id, codigo_grupo)
DO NOTHING;

-- 3. Relacionar cada grupo con su profesor titular.
INSERT INTO public.grupos_profesores (
    grupo_id,
    profesor_id,
    rol
)
SELECT
    g.id,
    t.profesor_id,
    'titular'
FROM tmp_grupos_plan t
JOIN public.grupos g
    ON g.asignatura_id = t.asignatura_id
   AND g.periodo_id = t.periodo_id
   AND g.codigo_grupo = t.codigo_grupo
ON CONFLICT (grupo_id, profesor_id)
DO NOTHING;

-- 4. Crear un horario semanal de dos horas por grupo.
INSERT INTO public.horarios_grupos (
    grupo_id,
    dia_semana,
    hora_inicio,
    hora_fin,
    lugar,
    observaciones
)
SELECT
    g.id,
    t.dia_semana,
    t.hora_inicio,
    (t.hora_inicio + INTERVAL '2 hours')::time,
    'Aula simulada',
    'Horario semanal simulado; no corresponde a una oferta oficial.'
FROM tmp_grupos_plan t
JOIN public.grupos g
    ON g.asignatura_id = t.asignatura_id
   AND g.periodo_id = t.periodo_id
   AND g.codigo_grupo = t.codigo_grupo
WHERE NOT EXISTS (
    SELECT 1
    FROM public.horarios_grupos h
    WHERE h.grupo_id = g.id
      AND h.dia_semana = t.dia_semana
      AND h.hora_inicio = t.hora_inicio
      AND h.hora_fin = (t.hora_inicio + INTERVAL '2 hours')::time
);

-- 5. Verificar los registros sintéticos.
SELECT
    (SELECT COUNT(*)
     FROM public.grupos
     WHERE es_sintetico = TRUE) AS grupos,

    (SELECT COUNT(*)
     FROM public.grupos_profesores gp
     JOIN public.grupos g ON g.id = gp.grupo_id
     WHERE g.es_sintetico = TRUE) AS asignaciones_docentes,

    (SELECT COUNT(*)
     FROM public.horarios_grupos h
     JOIN public.grupos g ON g.id = h.grupo_id
     WHERE g.es_sintetico = TRUE) AS horarios;

COMMIT;
