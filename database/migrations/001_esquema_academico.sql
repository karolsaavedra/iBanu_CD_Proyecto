-- =====================================================
-- iBanu - Migracion 001
-- Esquema academico inicial
-- PostgreSQL / Supabase
-- =====================================================

-- 1. PLANES DE ESTUDIO
CREATE TABLE IF NOT EXISTS public.planes_estudio (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo VARCHAR(30) NOT NULL UNIQUE,
    nombre VARCHAR(150) NOT NULL,
    version VARCHAR(30) NOT NULL,
    anio_inicio INTEGER NOT NULL,
    anio_fin INTEGER,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_plan_anios
        CHECK (anio_fin IS NULL OR anio_fin >= anio_inicio)
);

-- 2. ESTUDIANTES
CREATE TABLE IF NOT EXISTS public.estudiantes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo_estudiante VARCHAR(30) NOT NULL UNIQUE,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    correo VARCHAR(150) UNIQUE,
    anio_ingreso INTEGER NOT NULL,
    CONSTRAINT chk_anio_ingreso CHECK (anio_ingreso BETWEEN 2000 AND 2100),
    plan_estudio_id UUID NOT NULL REFERENCES public.planes_estudio(id)
        ON DELETE RESTRICT,
    estado VARCHAR(20) NOT NULL DEFAULT 'activo',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_estudiante_estado
        CHECK (estado IN ('activo', 'inactivo', 'graduado', 'retirado'))
);

-- 3. PROFESORES
CREATE TABLE IF NOT EXISTS public.profesores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo_profesor VARCHAR(30) UNIQUE,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    correo VARCHAR(150) UNIQUE,
    departamento VARCHAR(120),
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 4. ASIGNATURAS
CREATE TABLE IF NOT EXISTS public.asignaturas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo VARCHAR(30) NOT NULL UNIQUE,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    creditos INTEGER NOT NULL,
    activa BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_asignatura_creditos
        CHECK (creditos > 0)
);

-- 5. ASIGNATURAS POR PLAN DE ESTUDIO
CREATE TABLE IF NOT EXISTS public.plan_asignaturas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_estudio_id UUID NOT NULL
        REFERENCES public.planes_estudio(id) ON DELETE CASCADE,
    asignatura_id UUID NOT NULL
        REFERENCES public.asignaturas(id) ON DELETE RESTRICT,
    semestre INTEGER NOT NULL,
    obligatoria BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT uq_plan_asignatura
        UNIQUE (plan_estudio_id, asignatura_id),

    CONSTRAINT chk_plan_semestre
        CHECK (semestre BETWEEN 1 AND 20)
);

-- 6. PRERREQUISITOS
CREATE TABLE IF NOT EXISTS public.prerrequisitos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asignatura_id UUID NOT NULL
        REFERENCES public.asignaturas(id) ON DELETE CASCADE,
    prerrequisito_id UUID NOT NULL
        REFERENCES public.asignaturas(id) ON DELETE RESTRICT,

    CONSTRAINT uq_prerrequisito
        UNIQUE (asignatura_id, prerrequisito_id),

    CONSTRAINT chk_prerrequisito_diferente
        CHECK (asignatura_id <> prerrequisito_id)
);

-- =====================================================
-- INDICES PARA CONSULTAS FRECUENTES
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_estudiantes_plan
    ON public.estudiantes(plan_estudio_id);

CREATE INDEX IF NOT EXISTS idx_plan_asignaturas_plan
    ON public.plan_asignaturas(plan_estudio_id);

CREATE INDEX IF NOT EXISTS idx_plan_asignaturas_asignatura
    ON public.plan_asignaturas(asignatura_id);

CREATE INDEX IF NOT EXISTS idx_prerrequisitos_asignatura
    ON public.prerrequisitos(asignatura_id);

CREATE INDEX IF NOT EXISTS idx_prerrequisitos_requisito
    ON public.prerrequisitos(prerrequisito_id);
