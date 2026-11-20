-- =====================================================
-- iBanu - Migracion 004
-- Profesores, horarios, grupos y turnos de inscripcion
-- Todos los datos de prueba seran sinteticos.
-- =====================================================

BEGIN;

-- 1. RELACION MUCHOS A MUCHOS: PROFESORES Y ASIGNATURAS

CREATE TABLE IF NOT EXISTS public.profesores_asignaturas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profesor_id UUID NOT NULL
        REFERENCES public.profesores(id) ON DELETE CASCADE,
    asignatura_id UUID NOT NULL
        REFERENCES public.asignaturas(id) ON DELETE RESTRICT,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    observaciones TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_profesor_asignatura
        UNIQUE (profesor_id, asignatura_id)
);

-- 2. RELACION MUCHOS A MUCHOS: PROFESORES Y GRUPOS

CREATE TABLE IF NOT EXISTS public.grupos_profesores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    grupo_id UUID NOT NULL
        REFERENCES public.grupos(id) ON DELETE CASCADE,
    profesor_id UUID NOT NULL
        REFERENCES public.profesores(id) ON DELETE RESTRICT,
    rol VARCHAR(30) NOT NULL DEFAULT 'profesor',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_grupo_profesor
        UNIQUE (grupo_id, profesor_id),

    CONSTRAINT chk_grupo_profesor_rol
        CHECK (rol IN ('titular', 'apoyo', 'coordinador', 'profesor'))
);

-- 3. AMPLIAR INFORMACION DE LOS GRUPOS

ALTER TABLE public.grupos
    ADD COLUMN IF NOT EXISTS modalidad VARCHAR(20)
        NOT NULL DEFAULT 'presencial',
    ADD COLUMN IF NOT EXISTS lugar VARCHAR(150),
    ADD COLUMN IF NOT EXISTS estado VARCHAR(20)
        NOT NULL DEFAULT 'activo';

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'chk_grupo_modalidad'
          AND conrelid = 'public.grupos'::regclass
    ) THEN
        ALTER TABLE public.grupos
            ADD CONSTRAINT chk_grupo_modalidad
            CHECK (modalidad IN ('presencial', 'virtual', 'hibrida'));
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'chk_grupo_estado'
          AND conrelid = 'public.grupos'::regclass
    ) THEN
        ALTER TABLE public.grupos
            ADD CONSTRAINT chk_grupo_estado
            CHECK (estado IN ('activo', 'cerrado', 'cancelado'));
    END IF;
END;
$$;

-- 4. HORARIOS DE LOS GRUPOS

CREATE TABLE IF NOT EXISTS public.horarios_grupos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    grupo_id UUID NOT NULL
        REFERENCES public.grupos(id) ON DELETE CASCADE,
    dia_semana SMALLINT NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    lugar VARCHAR(150),
    observaciones TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_horario_dia
        CHECK (dia_semana BETWEEN 1 AND 7),

    CONSTRAINT chk_horario_horas
        CHECK (hora_fin > hora_inicio)
);

-- 5. TURNOS INDIVIDUALES DE INSCRIPCION

CREATE TABLE IF NOT EXISTS public.turnos_inscripcion (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    estudiante_id UUID NOT NULL
        REFERENCES public.estudiantes(id) ON DELETE CASCADE,
    periodo_id UUID NOT NULL
        REFERENCES public.periodos_academicos(id) ON DELETE RESTRICT,
    fecha_inicio TIMESTAMPTZ NOT NULL,
    fecha_fin TIMESTAMPTZ NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'programado',
    observaciones TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_turno_estudiante_periodo
        UNIQUE (estudiante_id, periodo_id),

    CONSTRAINT chk_turno_fechas
        CHECK (fecha_fin > fecha_inicio),

    CONSTRAINT chk_turno_estado
        CHECK (estado IN (
            'programado',
            'abierto',
            'cerrado',
            'cancelado'
        ))
);

-- 6. MIGRAR ASIGNACIONES ANTIGUAS DE PROFESORES

-- Registrar primero la relacion profesor-asignatura de los grupos existentes.
INSERT INTO public.profesores_asignaturas (
    profesor_id,
    asignatura_id
)
SELECT DISTINCT
    profesor_id,
    asignatura_id
FROM public.grupos
WHERE profesor_id IS NOT NULL
ON CONFLICT (profesor_id, asignatura_id) DO NOTHING;

-- Conservar las asignaciones antiguas de profesores a grupos.
INSERT INTO public.grupos_profesores (
    grupo_id,
    profesor_id,
    rol
)
SELECT
    id,
    profesor_id,
    'titular'
FROM public.grupos
WHERE profesor_id IS NOT NULL
ON CONFLICT (grupo_id, profesor_id) DO NOTHING;

-- 7. VALIDAR QUE EL PROFESOR PUEDA ORIENTAR LA ASIGNATURA DEL GRUPO

CREATE OR REPLACE FUNCTION public.validar_profesor_grupo()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM public.grupos g
        JOIN public.profesores_asignaturas pa
          ON pa.asignatura_id = g.asignatura_id
         AND pa.profesor_id = NEW.profesor_id
         AND pa.activo = TRUE
        WHERE g.id = NEW.grupo_id
    ) THEN
        RAISE EXCEPTION
            'El profesor no tiene una asignacion activa para la asignatura de este grupo.';
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validar_profesor_grupo
ON public.grupos_profesores;

CREATE TRIGGER trg_validar_profesor_grupo
BEFORE INSERT OR UPDATE
ON public.grupos_profesores
FOR EACH ROW
EXECUTE FUNCTION public.validar_profesor_grupo();

-- 8. INDICES

CREATE INDEX IF NOT EXISTS idx_profesores_asignaturas_profesor
    ON public.profesores_asignaturas(profesor_id);

CREATE INDEX IF NOT EXISTS idx_profesores_asignaturas_asignatura
    ON public.profesores_asignaturas(asignatura_id);

CREATE INDEX IF NOT EXISTS idx_grupos_profesores_grupo
    ON public.grupos_profesores(grupo_id);

CREATE INDEX IF NOT EXISTS idx_grupos_profesores_profesor
    ON public.grupos_profesores(profesor_id);

CREATE INDEX IF NOT EXISTS idx_horarios_grupo_dia
    ON public.horarios_grupos(grupo_id, dia_semana);

CREATE INDEX IF NOT EXISTS idx_turnos_estudiante
    ON public.turnos_inscripcion(estudiante_id);

CREATE INDEX IF NOT EXISTS idx_turnos_periodo
    ON public.turnos_inscripcion(periodo_id);

CREATE INDEX IF NOT EXISTS idx_turnos_fechas
    ON public.turnos_inscripcion(fecha_inicio, fecha_fin);

-- 9. VALIDAR CUPO ANTES DE MATRICULAR

CREATE OR REPLACE FUNCTION public.validar_cupo_grupo()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_cupo INTEGER;
    v_ocupados INTEGER;
BEGIN
    IF NEW.estado = 'activa' THEN

        -- Bloquear el grupo para evitar sobreinscripciones simultaneas.
        SELECT cupo
        INTO v_cupo
        FROM public.grupos
        WHERE id = NEW.grupo_id
        FOR UPDATE;

        IF v_cupo IS NOT NULL THEN

            SELECT COUNT(*)
            INTO v_ocupados
            FROM public.matriculas
            WHERE grupo_id = NEW.grupo_id
              AND estado = 'activa'
              AND id IS DISTINCT FROM NEW.id;

            IF v_ocupados >= v_cupo THEN
                RAISE EXCEPTION
                    'No hay cupos disponibles en el grupo seleccionado.';
            END IF;

        END IF;
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validar_cupo_grupo
ON public.matriculas;

CREATE TRIGGER trg_validar_cupo_grupo
BEFORE INSERT OR UPDATE
ON public.matriculas
FOR EACH ROW
EXECUTE FUNCTION public.validar_cupo_grupo();

COMMIT;
