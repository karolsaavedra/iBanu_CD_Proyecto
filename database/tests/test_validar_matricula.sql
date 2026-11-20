BEGIN;

DO $$
DECLARE
    v_plan UUID := gen_random_uuid();
    v_estudiante UUID := gen_random_uuid();
    v_asignatura UUID := gen_random_uuid();
    v_periodo UUID := gen_random_uuid();
    v_grupo1 UUID := gen_random_uuid();
    v_grupo2 UUID := gen_random_uuid();
    v_sufijo TEXT := substring(replace(gen_random_uuid()::TEXT, '-', '') from 1 for 12);
    v_error TEXT;
BEGIN
    INSERT INTO public.planes_estudio
        (id, codigo, nombre, version, anio_inicio)
    VALUES
        (v_plan, 'TESTP-' || v_sufijo,
         'Plan de prueba', '1.0', 2026);

    INSERT INTO public.estudiantes
        (id, codigo_estudiante, nombres, apellidos,
         anio_ingreso, plan_estudio_id)
    VALUES
        (v_estudiante, 'TESTE-' || v_sufijo,
         'Estudiante', 'Prueba', 2026, v_plan);

    INSERT INTO public.asignaturas
        (id, codigo, nombre, creditos)
    VALUES
        (v_asignatura, 'TESTA-' || v_sufijo,
         'Asignatura de prueba', 3);

    INSERT INTO public.periodos_academicos
        (id, codigo, nombre, anio, semestre)
    VALUES
        (v_periodo, 'TESTPER-' || v_sufijo,
         'Periodo de prueba', 2026, 2);

    INSERT INTO public.grupos
        (id, asignatura_id, periodo_id, codigo_grupo)
    VALUES
        (v_grupo1, v_asignatura, v_periodo, '01'),
        (v_grupo2, v_asignatura, v_periodo, '02');

    INSERT INTO public.matriculas
        (estudiante_id, grupo_id, estado)
    VALUES
        (v_estudiante, v_grupo1, 'activa');

    BEGIN
        INSERT INTO public.matriculas
            (estudiante_id, grupo_id, estado)
        VALUES
            (v_estudiante, v_grupo2, 'activa');

        RAISE EXCEPTION
            'TEST_FAILED: se permitio la matricula duplicada';

    EXCEPTION WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS v_error = MESSAGE_TEXT;

        IF v_error =
            'El estudiante ya tiene una matricula activa en esta asignatura y periodo.' THEN
            RAISE NOTICE
                'TEST_OK: se bloqueo correctamente la matricula duplicada.';
        ELSE
            RAISE;
        END IF;
    END;
END;
$$;

ROLLBACK;
