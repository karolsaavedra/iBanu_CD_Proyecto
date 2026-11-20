-- =====================================================
-- iBanu - Migracion 002
-- Periodos, grupos, matriculas y notas
-- =====================================================

-- 1. PERIODOS ACADEMICOS
CREATE TABLE IF NOT EXISTS public.periodos_academicos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    anio INTEGER NOT NULL,
    semestre INTEGER NOT NULL,
    fecha_inicio DATE,
    fecha_fin DATE,
    activo BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_periodo_semestre
        CHECK (semestre IN (1, 2)),

    CONSTRAINT chk_periodo_fechas
        CHECK (
            fecha_fin IS NULL
            OR fecha_inicio IS NULL
            OR fecha_fin >= fecha_inicio
        )
);

-- 2. GRUPOS OFERTADOS
CREATE TABLE IF NOT EXISTS public.grupos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asignatura_id UUID NOT NULL
        REFERENCES public.asignaturas(id) ON DELETE RESTRICT,
    profesor_id UUID
        REFERENCES public.profesores(id) ON DELETE SET NULL,
    periodo_id UUID NOT NULL
        REFERENCES public.periodos_academicos(id) ON DELETE RESTRICT,
    codigo_grupo VARCHAR(20) NOT NULL,
    cupo INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_grupo_periodo
        UNIQUE (asignatura_id, periodo_id, codigo_grupo),

    CONSTRAINT chk_grupo_cupo
        CHECK (cupo IS NULL OR cupo > 0)
);

-- 3. MATRICULAS
CREATE TABLE IF NOT EXISTS public.matriculas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    estudiante_id UUID NOT NULL
        REFERENCES public.estudiantes(id) ON DELETE RESTRICT,
    grupo_id UUID NOT NULL
        REFERENCES public.grupos(id) ON DELETE RESTRICT,
    estado VARCHAR(20) NOT NULL DEFAULT 'activa',
    fecha_matricula TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_estudiante_grupo
        UNIQUE (estudiante_id, grupo_id),

    CONSTRAINT chk_matricula_estado
        CHECK (
            estado IN ('activa', 'cancelada', 'aprobada', 'reprobada')
        )
);

-- 4. NOTAS
CREATE TABLE IF NOT EXISTS public.notas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    matricula_id UUID NOT NULL
        REFERENCES public.matriculas(id) ON DELETE CASCADE,
    componente VARCHAR(100) NOT NULL,
    calificacion NUMERIC(4,2) NOT NULL,
    porcentaje NUMERIC(5,2),
    fecha_registro TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_nota_calificacion
        CHECK (calificacion BETWEEN 0 AND 5),

    CONSTRAINT chk_nota_porcentaje
        CHECK (porcentaje IS NULL OR porcentaje BETWEEN 0 AND 100),

    CONSTRAINT uq_nota_componente
        UNIQUE (matricula_id, componente)
);

-- =====================================================
-- INDICES
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_grupos_asignatura
    ON public.grupos(asignatura_id);

CREATE INDEX IF NOT EXISTS idx_grupos_profesor
    ON public.grupos(profesor_id);

CREATE INDEX IF NOT EXISTS idx_grupos_periodo
    ON public.grupos(periodo_id);

CREATE INDEX IF NOT EXISTS idx_matriculas_estudiante
    ON public.matriculas(estudiante_id);

CREATE INDEX IF NOT EXISTS idx_matriculas_grupo
    ON public.matriculas(grupo_id);

CREATE INDEX IF NOT EXISTS idx_notas_matricula
    ON public.notas(matricula_id);


-- =====================================================
-- VALIDACION: UNA ASIGNATURA ACTIVA POR PERIODO
-- =====================================================

CREATE OR REPLACE FUNCTION public.validar_matricula_unica()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_asignatura_id UUID;
    v_periodo_id UUID;
BEGIN
    IF NEW.estado = 'activa' THEN

        -- Serializar las matriculas del mismo estudiante.
        PERFORM 1
        FROM public.estudiantes
        WHERE id = NEW.estudiante_id
        FOR UPDATE;

        -- Obtener asignatura y periodo del grupo.
        SELECT asignatura_id, periodo_id
        INTO v_asignatura_id, v_periodo_id
        FROM public.grupos
        WHERE id = NEW.grupo_id;

        -- Comprobar si ya existe otra matricula activa.
        IF EXISTS (
            SELECT 1
            FROM public.matriculas m
            JOIN public.grupos g
                ON g.id = m.grupo_id
            WHERE m.estudiante_id = NEW.estudiante_id
              AND m.estado = 'activa'
              AND m.id IS DISTINCT FROM NEW.id
              AND g.asignatura_id = v_asignatura_id
              AND g.periodo_id = v_periodo_id
        ) THEN
            RAISE EXCEPTION
                'El estudiante ya tiene una matricula activa en esta asignatura y periodo.';
        END IF;

    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validar_matricula_unica
ON public.matriculas;

CREATE TRIGGER trg_validar_matricula_unica
BEFORE INSERT OR UPDATE
ON public.matriculas
FOR EACH ROW
EXECUTE FUNCTION public.validar_matricula_unica();
