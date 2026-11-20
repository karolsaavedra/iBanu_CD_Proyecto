BEGIN;

ALTER TABLE public.estudiantes
ADD COLUMN IF NOT EXISTS es_sintetico BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE public.profesores
ADD COLUMN IF NOT EXISTS es_sintetico BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE public.periodos_academicos
ADD COLUMN IF NOT EXISTS es_sintetico BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE public.grupos
ADD COLUMN IF NOT EXISTS es_sintetico BOOLEAN NOT NULL DEFAULT FALSE;

COMMENT ON COLUMN public.estudiantes.es_sintetico
IS 'Indica si el registro del estudiante es completamente simulado.';

COMMENT ON COLUMN public.profesores.es_sintetico
IS 'Indica si el registro del profesor es completamente simulado.';

COMMENT ON COLUMN public.periodos_academicos.es_sintetico
IS 'Indica si el periodo académico es simulado.';

COMMENT ON COLUMN public.grupos.es_sintetico
IS 'Indica si el grupo académico es simulado.';

COMMIT;
