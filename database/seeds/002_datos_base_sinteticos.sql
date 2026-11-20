BEGIN;

-- =====================================================
-- 1. ESTUDIANTES SINTETICOS
-- =====================================================

INSERT INTO public.estudiantes (
    codigo_estudiante, nombres, apellidos, correo,
    anio_ingreso, plan_estudio_id, estado, es_sintetico
)
VALUES
('U00112040','Laura','Martínez Rojas','lmartinez040@unab.edu.co',2026,'4d26ab59-95a4-469b-9813-43eb446a8bcc','activo',TRUE),
('U00112041','Daniel','Gómez Pérez','dgomez041@unab.edu.co',2026,'4d26ab59-95a4-469b-9813-43eb446a8bcc','activo',TRUE),
('U00112042','Sofía','Ramírez Torres','sramirez042@unab.edu.co',2026,'4d26ab59-95a4-469b-9813-43eb446a8bcc','activo',TRUE),
('U00112043','Andrés','Castro Díaz','acastro043@unab.edu.co',2026,'4d26ab59-95a4-469b-9813-43eb446a8bcc','activo',TRUE),
('U00112044','Valentina','Rojas Mendoza','vrojas044@unab.edu.co',2026,'4d26ab59-95a4-469b-9813-43eb446a8bcc','activo',TRUE),
('U00112045','Mateo','Hernández Silva','mhernandez045@unab.edu.co',2026,'4d26ab59-95a4-469b-9813-43eb446a8bcc','activo',TRUE),
('U00112046','Camila','Moreno Vargas','cmoreno046@unab.edu.co',2026,'4d26ab59-95a4-469b-9813-43eb446a8bcc','activo',TRUE),
('U00112047','Samuel','Torres León','storres047@unab.edu.co',2026,'4d26ab59-95a4-469b-9813-43eb446a8bcc','activo',TRUE),
('U00112048','Mariana','Díaz Romero','mdiaz048@unab.edu.co',2026,'4d26ab59-95a4-469b-9813-43eb446a8bcc','activo',TRUE),
('U00112049','Nicolás','Vargas Ortiz','nvargas049@unab.edu.co',2026,'4d26ab59-95a4-469b-9813-43eb446a8bcc','activo',TRUE),
('U00112050','Isabella','Mendoza Ruiz','imendoza050@unab.edu.co',2026,'4d26ab59-95a4-469b-9813-43eb446a8bcc','activo',TRUE),
('U00112051','Sebastián','Silva Parra','ssilva051@unab.edu.co',2026,'4d26ab59-95a4-469b-9813-43eb446a8bcc','activo',TRUE),
('U00112052','Gabriela','León Acosta','gleon052@unab.edu.co',2026,'4d26ab59-95a4-469b-9813-43eb446a8bcc','activo',TRUE),
('U00112053','David','Romero Gil','dromero053@unab.edu.co',2026,'4d26ab59-95a4-469b-9813-43eb446a8bcc','activo',TRUE),
('U00112054','Luciana','Ortiz Reyes','lortiz054@unab.edu.co',2026,'4d26ab59-95a4-469b-9813-43eb446a8bcc','activo',TRUE),
('U00112055','Alejandro','Ruiz Méndez','aruiz055@unab.edu.co',2026,'4d26ab59-95a4-469b-9813-43eb446a8bcc','activo',TRUE),
('U00112056','Daniela','Parra Suárez','dparra056@unab.edu.co',2026,'4d26ab59-95a4-469b-9813-43eb446a8bcc','activo',TRUE),
('U00112057','Tomás','Acosta Vega','tacosta057@unab.edu.co',2026,'4d26ab59-95a4-469b-9813-43eb446a8bcc','activo',TRUE),
('U00112058','Sara','Gil Navarro','sgil058@unab.edu.co',2026,'4d26ab59-95a4-469b-9813-43eb446a8bcc','activo',TRUE),
('U00112059','Emiliano','Reyes Cruz','ereyes059@unab.edu.co',2026,'4d26ab59-95a4-469b-9813-43eb446a8bcc','activo',TRUE),
('U00112060','Manuela','Méndez Rincón','mmendez060@unab.edu.co',2026,'4d26ab59-95a4-469b-9813-43eb446a8bcc','activo',TRUE),
('U00112061','Juan','Suárez Pineda','jsuarez061@unab.edu.co',2026,'4d26ab59-95a4-469b-9813-43eb446a8bcc','activo',TRUE),
('U00112062','Antonella','Vega Duarte','avega062@unab.edu.co',2026,'4d26ab59-95a4-469b-9813-43eb446a8bcc','activo',TRUE),
('U00112063','Gabriel','Navarro Peña','gnavarro063@unab.edu.co',2026,'4d26ab59-95a4-469b-9813-43eb446a8bcc','activo',TRUE),
('U00112064','Paula','Cruz Herrera','pcruz064@unab.edu.co',2026,'4d26ab59-95a4-469b-9813-43eb446a8bcc','activo',TRUE),
('U00112065','Martín','Rincón Molina','mrincon065@unab.edu.co',2026,'4d26ab59-95a4-469b-9813-43eb446a8bcc','activo',TRUE),
('U00112066','Julieta','Pineda Cárdenas','jpineda066@unab.edu.co',2026,'4d26ab59-95a4-469b-9813-43eb446a8bcc','activo',TRUE),
('U00112067','Felipe','Duarte Salazar','fduarte067@unab.edu.co',2026,'4d26ab59-95a4-469b-9813-43eb446a8bcc','activo',TRUE),
('U00112068','Renata','Peña Beltrán','rpena068@unab.edu.co',2026,'4d26ab59-95a4-469b-9813-43eb446a8bcc','activo',TRUE),
('U00112069','Santiago','Herrera Lozano','sherrera069@unab.edu.co',2026,'4d26ab59-95a4-469b-9813-43eb446a8bcc','activo',TRUE)
ON CONFLICT (codigo_estudiante) DO NOTHING;


-- =====================================================
-- 2. PROFESORES SINTETICOS
-- =====================================================

INSERT INTO public.profesores (
    codigo_profesor, nombres, apellidos, correo,
    departamento, activo, es_sintetico
)
VALUES
('SIM-PROF-001','Carlos','Mendoza Ríos','cmendoza001@unab.edu.co','Ingeniería de Sistemas',TRUE,TRUE),
('SIM-PROF-002','Andrea','Pérez Salazar','aperez002@unab.edu.co','Ingeniería de Sistemas',TRUE,TRUE),
('SIM-PROF-003','Julián','Torres Medina','jtorres003@unab.edu.co','Ciencias Básicas',TRUE,TRUE),
('SIM-PROF-004','Natalia','Gómez Herrera','ngomez004@unab.edu.co','Ingeniería de Sistemas',TRUE,TRUE),
('SIM-PROF-005','Ricardo','Vargas León','rvargas005@unab.edu.co','Ingeniería de Sistemas',TRUE,TRUE),
('SIM-PROF-006','Paola','Castro Ruiz','pcastro006@unab.edu.co','Ciencias Básicas',TRUE,TRUE),
('SIM-PROF-007','Felipe','Ramírez Ortiz','framirez007@unab.edu.co','Ingeniería de Sistemas',TRUE,TRUE),
('SIM-PROF-008','Diana','Moreno Gil','dmoreno008@unab.edu.co','Ingeniería de Sistemas',TRUE,TRUE),
('SIM-PROF-009','Mauricio','Silva Reyes','msilva009@unab.edu.co','Ciencias Básicas',TRUE,TRUE),
('SIM-PROF-010','Carolina','Rojas Méndez','crojas010@unab.edu.co','Ingeniería de Sistemas',TRUE,TRUE),
('SIM-PROF-011','Esteban','Navarro Díaz','enavarro011@unab.edu.co','Ingeniería de Sistemas',TRUE,TRUE),
('SIM-PROF-012','Marcela','Acosta Peña','macosta012@unab.edu.co','Ingeniería de Sistemas',TRUE,TRUE)
ON CONFLICT (codigo_profesor) DO NOTHING;


-- =====================================================
-- 3. PERIODOS ACADEMICOS SINTETICOS
-- Fechas de demostracion, no oficiales.
-- =====================================================

INSERT INTO public.periodos_academicos (
    codigo, nombre, anio, semestre,
    fecha_inicio, fecha_fin, activo, es_sintetico
)
VALUES
(
    'SIM-2027-1',
    'Periodo académico simulado 2027-1',
    2027, 1,
    '2027-01-18', '2027-06-05',
    TRUE, TRUE
),
(
    'SIM-2027-2',
    'Periodo académico simulado 2027-2',
    2027, 2,
    '2027-07-19', '2027-12-04',
    FALSE, TRUE
)
ON CONFLICT (codigo) DO NOTHING;


-- =====================================================
-- 4. RELACIONAR PROFESORES Y ASIGNATURAS
-- Cada asignatura tendra entre 1 y 3 profesores.
-- La distribucion se genera de forma determinista.
-- =====================================================

WITH asignaturas_ordenadas AS (
    SELECT
        id AS asignatura_id,
        ROW_NUMBER() OVER (ORDER BY codigo)::INTEGER AS n
    FROM public.asignaturas
    WHERE activa = TRUE
),
asignaciones AS (
    -- Profesor principal
    SELECT
        asignatura_id,
        ((n - 1) % 12) + 1 AS profesor_numero
    FROM asignaturas_ordenadas

    UNION ALL

    -- Segundo profesor para parte de las asignaturas
    SELECT
        asignatura_id,
        ((n + 3) % 12) + 1
    FROM asignaturas_ordenadas
    WHERE n % 2 = 0

    UNION ALL

    -- Tercer profesor para parte de las asignaturas
    SELECT
        asignatura_id,
        ((n + 7) % 12) + 1
    FROM asignaturas_ordenadas
    WHERE n % 5 = 0
)
INSERT INTO public.profesores_asignaturas (
    profesor_id,
    asignatura_id,
    activo,
    observaciones
)
SELECT
    p.id,
    a.asignatura_id,
    TRUE,
    'Asignación académica completamente sintética para pruebas de iBanú.'
FROM asignaciones a
JOIN public.profesores p
    ON p.codigo_profesor =
       'SIM-PROF-' || LPAD(a.profesor_numero::TEXT, 3, '0')
ON CONFLICT (profesor_id, asignatura_id) DO NOTHING;

COMMIT;
