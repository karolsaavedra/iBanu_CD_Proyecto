
BEGIN;

-- Crear un turno individual por estudiante y periodo.
WITH estudiantes_periodos AS (
    SELECT
        e.id AS estudiante_id,
        p.id AS periodo_id,
        p.codigo AS codigo_periodo,
        ROW_NUMBER() OVER (
            PARTITION BY p.id
            ORDER BY e.codigo_estudiante
        ) AS numero_turno
    FROM public.estudiantes e
    CROSS JOIN public.periodos_academicos p
    WHERE e.es_sintetico = TRUE
      AND p.es_sintetico = TRUE
),
turnos_calculados AS (
    SELECT
        estudiante_id,
        periodo_id,
        CASE codigo_periodo
            WHEN 'SIM-2027-1' THEN
                DATE '2027-01-05'
                + ((numero_turno - 1) / 10)::integer
            WHEN 'SIM-2027-2' THEN
                DATE '2027-07-05'
                + ((numero_turno - 1) / 10)::integer
        END AS fecha_turno,
        TIME '08:00'
            + (((numero_turno - 1) % 10) * INTERVAL '74 minutes')
            AS hora_turno
    FROM estudiantes_periodos
)
INSERT INTO public.turnos_inscripcion (
    estudiante_id,
    periodo_id,
    fecha_inicio,
    fecha_fin,
    estado,
    observaciones
)
SELECT
    estudiante_id,
    periodo_id,
    (fecha_turno + hora_turno) AT TIME ZONE 'America/Bogota',
    (fecha_turno + hora_turno + INTERVAL '74 minutes') AT TIME ZONE 'America/Bogota',
    'programado',
    'Turno de inscripción simulado para pruebas de iBanu.'
FROM turnos_calculados
ON CONFLICT (estudiante_id, periodo_id)
DO UPDATE SET
    fecha_inicio = EXCLUDED.fecha_inicio,
    fecha_fin = EXCLUDED.fecha_fin,
    observaciones = EXCLUDED.observaciones;

-- Comprobar los turnos creados.
SELECT
    COUNT(*) AS total_turnos,
    COUNT(DISTINCT estudiante_id) AS estudiantes,
    COUNT(DISTINCT periodo_id) AS periodos,
    COUNT(*) FILTER (
        WHERE estado = 'programado'
    ) AS turnos_programados
FROM public.turnos_inscripcion
WHERE estudiante_id IN (
    SELECT id
    FROM public.estudiantes
    WHERE es_sintetico = TRUE
);

COMMIT;
