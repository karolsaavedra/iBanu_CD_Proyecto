-- =====================================================
-- iBanu - Migracion 003
-- Documentos academicos y fragmentos para RAG
-- =====================================================

-- -----------------------------------------------------
-- 1. Documentos academicos
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS public.documentos_academicos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    nombre_archivo VARCHAR(255) NOT NULL,
    nombre_original VARCHAR(255) NOT NULL,
    tipo_archivo VARCHAR(30) NOT NULL,

    categoria VARCHAR(50) NOT NULL,

    descripcion TEXT,

    origen VARCHAR(30) NOT NULL DEFAULT 'pendiente',

    estado_verificacion VARCHAR(30) NOT NULL DEFAULT 'pendiente',

    version_documento VARCHAR(50),

    fecha_documento DATE,

    ruta_archivo TEXT,

    hash_contenido VARCHAR(128),

    observaciones TEXT,

    activo BOOLEAN NOT NULL DEFAULT TRUE,

    fecha_carga TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_documento_tipo
        CHECK (tipo_archivo IN (
            'pdf', 'docx', 'doc', 'txt', 'xlsx', 'pptx', 'otro'
        )),

    CONSTRAINT chk_documento_categoria
        CHECK (categoria IN (
            'programa',
            'materias',
            'reglamento',
            'practicas',
            'costos',
            'calendario',
            'faq',
            'otro'
        )),

    CONSTRAINT chk_documento_origen
        CHECK (origen IN (
            'oficial',
            'institucional',
            'usuario',
            'pendiente'
        )),

    CONSTRAINT chk_documento_verificacion
        CHECK (estado_verificacion IN (
            'verificado',
            'pendiente',
            'incompleto',
            'desactualizado',
            'rechazado'
        ))
);


-- -----------------------------------------------------
-- 2. Relacion entre documentos y asignaturas
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS public.documentos_asignaturas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    documento_id UUID NOT NULL
        REFERENCES public.documentos_academicos(id)
        ON DELETE CASCADE,

    asignatura_id UUID NOT NULL
        REFERENCES public.asignaturas(id)
        ON DELETE RESTRICT,

    observaciones TEXT,

    CONSTRAINT uq_documento_asignatura
        UNIQUE (documento_id, asignatura_id)
);


-- -----------------------------------------------------
-- 3. Fragmentos de documentos para RAG
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS public.fragmentos_documento (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    documento_id UUID NOT NULL
        REFERENCES public.documentos_academicos(id)
        ON DELETE CASCADE,

    asignatura_id UUID
        REFERENCES public.asignaturas(id)
        ON DELETE SET NULL,

    contenido TEXT NOT NULL,

    numero_fragmento INTEGER NOT NULL,

    numero_pagina INTEGER,

    seccion VARCHAR(255),

    metadata JSONB NOT NULL DEFAULT '{}'::JSONB,

    embedding VECTOR,

    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_fragmento_numero
        CHECK (numero_fragmento >= 0),

    CONSTRAINT chk_fragmento_pagina
        CHECK (numero_pagina IS NULL OR numero_pagina > 0),

    CONSTRAINT uq_documento_fragmento
        UNIQUE (documento_id, numero_fragmento)
);


-- -----------------------------------------------------
-- 4. Indices
-- -----------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_documentos_categoria
    ON public.documentos_academicos(categoria);

CREATE INDEX IF NOT EXISTS idx_documentos_verificacion
    ON public.documentos_academicos(estado_verificacion);

CREATE INDEX IF NOT EXISTS idx_documentos_activo
    ON public.documentos_academicos(activo);

CREATE INDEX IF NOT EXISTS idx_documentos_asignaturas_documento
    ON public.documentos_asignaturas(documento_id);

CREATE INDEX IF NOT EXISTS idx_documentos_asignaturas_asignatura
    ON public.documentos_asignaturas(asignatura_id);

CREATE INDEX IF NOT EXISTS idx_fragmentos_documento
    ON public.fragmentos_documento(documento_id);

CREATE INDEX IF NOT EXISTS idx_fragmentos_asignatura
    ON public.fragmentos_documento(asignatura_id);

CREATE INDEX IF NOT EXISTS idx_fragmentos_metadata
    ON public.fragmentos_documento USING GIN(metadata);


-- =====================================================
-- FIN MIGRACION 003
-- =====================================================
