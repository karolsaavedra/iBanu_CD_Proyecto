-- =========================================================
-- iBanu - Catalogo academico inicial
-- Plan 2026 - Provisional, pendiente de verificacion
-- Codigos IB26: identificadores internos de iBanu
-- =========================================================

BEGIN;

-- 1. Crear o actualizar el plan provisional
INSERT INTO public.planes_estudio
    (codigo, nombre, version, anio_inicio, anio_fin, activo)
VALUES
    ('IBANU-PLAN-2026-PROV',
     'Ingenieria de Sistemas',
     '2026-provisional',
     2026,
     NULL,
     FALSE)
ON CONFLICT (codigo) DO UPDATE SET
    nombre = EXCLUDED.nombre,
    version = EXCLUDED.version,
    anio_inicio = EXCLUDED.anio_inicio,
    anio_fin = EXCLUDED.anio_fin,
    activo = FALSE;

-- 2. Registrar las asignaturas
INSERT INTO public.asignaturas (codigo, nombre, creditos)
VALUES
    ('IB26-S01-01', 'Fundamentos de Programación', 3),
    ('IB26-S01-02', 'Expresión', 4),
    ('IB26-S01-03', 'Seminario de Ingeniería I', 2),
    ('IB26-S01-04', 'Álgebra Lineal', 3),
    ('IB26-S01-05', 'Cálculo Diferencial', 4),

    ('IB26-S02-01', 'Programación de Computadores', 3),
    ('IB26-S02-02', 'Diseño de Interfaces de Usuario', 3),
    ('IB26-S02-03', 'Mecánica y Laboratorio', 3),
    ('IB26-S02-04', 'Cálculo Integral', 4),
    ('IB26-S02-05', 'Identidad', 3),

    ('IB26-S03-01', 'Estructura de Datos y Análisis de Algoritmos', 3),
    ('IB26-S03-02', 'Creatividad', 3),
    ('IB26-S03-03', 'Electromagnetismo y Laboratorio', 3),
    ('IB26-S03-04', 'Seminario de Ingeniería II', 2),
    ('IB26-S03-05', 'Matemáticas Computacionales', 3),
    ('IB26-S03-06', 'Cálculo en Varias Variables', 3),

    ('IB26-S04-01', 'Inteligencia Artificial', 3),
    ('IB26-S04-02', 'Estadística General', 3),
    ('IB26-S04-03', 'Base de Datos I', 3),
    ('IB26-S04-04', 'Ecuaciones Diferenciales', 3),
    ('IB26-S04-05', 'Desarrollo Multimedia', 3),
    ('IB26-S04-06', 'Tecnologías Móviles', 3),

    ('IB26-S05-01', 'Infraestructura Tecnológica', 3),
    ('IB26-S05-02', 'Base de Datos II', 3),
    ('IB26-S05-03', 'Ingeniería de Software I', 3),
    ('IB26-S05-04', 'Arquitectura de Software', 3),

    ('IB26-S06-01', 'Ética de la Ingeniería de Sistemas', 2),
    ('IB26-S06-02', 'Ciencias de Datos', 3),
    ('IB26-S06-03', 'Teoría de Sistemas y Organizaciones', 3),
    ('IB26-S06-04', 'Ingeniería de Software II', 3),
    ('IB26-S06-05', 'Internet de las Cosas', 3),

    ('IB26-S07-01', 'Ciberseguridad', 3),
    ('IB26-S07-02', 'Proyecto en Ingeniería de Sistemas I', 2),
    ('IB26-S07-03', 'Investigación de Operaciones I', 3),

    ('IB26-S08-01', 'Proyecto en Ingeniería de Sistemas II', 4),
    ('IB26-S08-02', 'Investigación de Operaciones II', 3),
    ('IB26-S08-03', 'Dinámica de Sistemas', 3),

    ('IB26-S09-01', 'Práctica en Ingeniería de Sistemas', 12)

ON CONFLICT (codigo) DO UPDATE SET
    nombre = EXCLUDED.nombre,
    creditos = EXCLUDED.creditos,
    activa = TRUE;

-- 3. Relacionar cada asignatura con su semestre
INSERT INTO public.plan_asignaturas
    (plan_estudio_id, asignatura_id, semestre, obligatoria)
SELECT
    p.id,
    a.id,
    v.semestre,
    TRUE
FROM (
    VALUES
        ('IB26-S01-01', 1), ('IB26-S01-02', 1),
        ('IB26-S01-03', 1), ('IB26-S01-04', 1),
        ('IB26-S01-05', 1),

        ('IB26-S02-01', 2), ('IB26-S02-02', 2),
        ('IB26-S02-03', 2), ('IB26-S02-04', 2),
        ('IB26-S02-05', 2),

        ('IB26-S03-01', 3), ('IB26-S03-02', 3),
        ('IB26-S03-03', 3), ('IB26-S03-04', 3),
        ('IB26-S03-05', 3), ('IB26-S03-06', 3),

        ('IB26-S04-01', 4), ('IB26-S04-02', 4),
        ('IB26-S04-03', 4), ('IB26-S04-04', 4),
        ('IB26-S04-05', 4), ('IB26-S04-06', 4),

        ('IB26-S05-01', 5), ('IB26-S05-02', 5),
        ('IB26-S05-03', 5), ('IB26-S05-04', 5),

        ('IB26-S06-01', 6), ('IB26-S06-02', 6),
        ('IB26-S06-03', 6), ('IB26-S06-04', 6),
        ('IB26-S06-05', 6),

        ('IB26-S07-01', 7), ('IB26-S07-02', 7),
        ('IB26-S07-03', 7),

        ('IB26-S08-01', 8), ('IB26-S08-02', 8),
        ('IB26-S08-03', 8),

        ('IB26-S09-01', 9)
) AS v(codigo, semestre)
JOIN public.asignaturas a ON a.codigo = v.codigo
JOIN public.planes_estudio p
    ON p.codigo = 'IBANU-PLAN-2026-PROV'

ON CONFLICT (plan_estudio_id, asignatura_id) DO UPDATE SET
    semestre = EXCLUDED.semestre,
    obligatoria = EXCLUDED.obligatoria;

COMMIT;
