-- 03_prerrequisitos.sql
-- Prerrequisitos tomados SOLO de las guías de cátedra oficiales de la UNAB almacenadas en iBanu.
-- Cada fila cita la guía y dice si es "prerrequisito formal" (la guía usa esa palabra) o
-- "conocimiento previo requerido" (la guía lo nombra en la sección 2, Conocimientos previos requeridos).
-- Idempotente: no borra ni actualiza nada. Detalle en docs/arquitectura.md

begin;

-- Guía TELE 18052 INTERNET DE LAS COSAS: prerrequisito formal: Infraestructura Tecnológica (código de guía COMP 18039)
insert into public.prerrequisitos (asignatura_id, prerrequisito_id)
select a.id, p.id from public.asignaturas a, public.asignaturas p
where a.codigo = 'IB26-S06-05' and p.codigo = 'IB26-S05-01'
on conflict do nothing;

-- Guía MATE 19030 CÁLCULO INTEGRAL: conocimiento previo requerido: Cálculo Diferencial (código de guía MATE 19029)
insert into public.prerrequisitos (asignatura_id, prerrequisito_id)
select a.id, p.id from public.asignaturas a, public.asignaturas p
where a.codigo = 'IB26-S02-04' and p.codigo = 'IB26-S01-05'
on conflict do nothing;

-- Guía FISI 19012 MECÁNICA Y LABORATORIO: conocimiento previo requerido: Cálculo Diferencial (código de guía MATE 19029)
insert into public.prerrequisitos (asignatura_id, prerrequisito_id)
select a.id, p.id from public.asignaturas a, public.asignaturas p
where a.codigo = 'IB26-S02-03' and p.codigo = 'IB26-S01-05'
on conflict do nothing;

-- Guía FISI 19012 MECÁNICA Y LABORATORIO: conocimiento previo requerido: Cálculo Integral (código de guía MATE 19030)
insert into public.prerrequisitos (asignatura_id, prerrequisito_id)
select a.id, p.id from public.asignaturas a, public.asignaturas p
where a.codigo = 'IB26-S02-03' and p.codigo = 'IB26-S02-04'
on conflict do nothing;

-- Guía FISI 19013 ELECTROMAGNETISMO Y LABORATORIO: conocimiento previo requerido: Cálculo Diferencial (código de guía MATE 19029)
insert into public.prerrequisitos (asignatura_id, prerrequisito_id)
select a.id, p.id from public.asignaturas a, public.asignaturas p
where a.codigo = 'IB26-S03-03' and p.codigo = 'IB26-S01-05'
on conflict do nothing;

-- Guía FISI 19013 ELECTROMAGNETISMO Y LABORATORIO: conocimiento previo requerido: Cálculo Integral (código de guía MATE 19030)
insert into public.prerrequisitos (asignatura_id, prerrequisito_id)
select a.id, p.id from public.asignaturas a, public.asignaturas p
where a.codigo = 'IB26-S03-03' and p.codigo = 'IB26-S02-04'
on conflict do nothing;

-- Guía FISI 19013 ELECTROMAGNETISMO Y LABORATORIO: conocimiento previo requerido: Mecánica y Laboratorio (código de guía FISI 19012)
insert into public.prerrequisitos (asignatura_id, prerrequisito_id)
select a.id, p.id from public.asignaturas a, public.asignaturas p
where a.codigo = 'IB26-S03-03' and p.codigo = 'IB26-S02-03'
on conflict do nothing;

-- Guía INGE 18018 SEMINARIO DE INGENIERÍA II: conocimiento previo requerido: Seminario de Ingeniería I (código de guía INGE 18017)
insert into public.prerrequisitos (asignatura_id, prerrequisito_id)
select a.id, p.id from public.asignaturas a, public.asignaturas p
where a.codigo = 'IB26-S03-04' and p.codigo = 'IB26-S01-03'
on conflict do nothing;

-- Guía MATE 19031 CÁLCULO EN VARIAS VARIABLES: conocimiento previo requerido: Cálculo Diferencial (código de guía MATE 19029)
insert into public.prerrequisitos (asignatura_id, prerrequisito_id)
select a.id, p.id from public.asignaturas a, public.asignaturas p
where a.codigo = 'IB26-S03-06' and p.codigo = 'IB26-S01-05'
on conflict do nothing;

-- Guía MATE 19031 CÁLCULO EN VARIAS VARIABLES: conocimiento previo requerido: Cálculo Integral (código de guía MATE 19030)
insert into public.prerrequisitos (asignatura_id, prerrequisito_id)
select a.id, p.id from public.asignaturas a, public.asignaturas p
where a.codigo = 'IB26-S03-06' and p.codigo = 'IB26-S02-04'
on conflict do nothing;

-- Guía COMP 18038 INTELIGENCIA ARTIFICIAL: conocimiento previo requerido: Programación de Computadores (código de guía COMP 18036)
insert into public.prerrequisitos (asignatura_id, prerrequisito_id)
select a.id, p.id from public.asignaturas a, public.asignaturas p
where a.codigo = 'IB26-S04-01' and p.codigo = 'IB26-S02-01'
on conflict do nothing;

-- Guía INFO 18001 BASE DE DATOS I: conocimiento previo requerido: Estructura de Datos y Análisis de Algoritmos (código de guía COMP 18037)
insert into public.prerrequisitos (asignatura_id, prerrequisito_id)
select a.id, p.id from public.asignaturas a, public.asignaturas p
where a.codigo = 'IB26-S04-03' and p.codigo = 'IB26-S03-01'
on conflict do nothing;

-- Guía MATE 19032 ECUACIONES DIFERENCIALES: conocimiento previo requerido: Cálculo Diferencial (código de guía MATE 19029)
insert into public.prerrequisitos (asignatura_id, prerrequisito_id)
select a.id, p.id from public.asignaturas a, public.asignaturas p
where a.codigo = 'IB26-S04-04' and p.codigo = 'IB26-S01-05'
on conflict do nothing;

-- Guía MATE 19032 ECUACIONES DIFERENCIALES: conocimiento previo requerido: Cálculo Integral (código de guía MATE 19030)
insert into public.prerrequisitos (asignatura_id, prerrequisito_id)
select a.id, p.id from public.asignaturas a, public.asignaturas p
where a.codigo = 'IB26-S04-04' and p.codigo = 'IB26-S02-04'
on conflict do nothing;

-- Guía MATE 19032 ECUACIONES DIFERENCIALES: conocimiento previo requerido: Cálculo en Varias Variables (código de guía MATE 19031)
insert into public.prerrequisitos (asignatura_id, prerrequisito_id)
select a.id, p.id from public.asignaturas a, public.asignaturas p
where a.codigo = 'IB26-S04-04' and p.codigo = 'IB26-S03-06'
on conflict do nothing;

-- Guía PRAM 18001 DESARROLLO MULTIMEDIA: conocimiento previo requerido: Estructura de Datos y Análisis de Algoritmos (código de guía COMP 18037)
insert into public.prerrequisitos (asignatura_id, prerrequisito_id)
select a.id, p.id from public.asignaturas a, public.asignaturas p
where a.codigo = 'IB26-S04-05' and p.codigo = 'IB26-S03-01'
on conflict do nothing;

-- Guía TELE 18051 TECNOLOGÍAS MÓVILES: conocimiento previo requerido: Estructura de Datos y Análisis de Algoritmos (código de guía COMP 18037)
insert into public.prerrequisitos (asignatura_id, prerrequisito_id)
select a.id, p.id from public.asignaturas a, public.asignaturas p
where a.codigo = 'IB26-S04-06' and p.codigo = 'IB26-S03-01'
on conflict do nothing;

-- Guía INFO 18002 BASE DE DATOS II: conocimiento previo requerido: Base de Datos I (código de guía INFO 18001)
insert into public.prerrequisitos (asignatura_id, prerrequisito_id)
select a.id, p.id from public.asignaturas a, public.asignaturas p
where a.codigo = 'IB26-S05-02' and p.codigo = 'IB26-S04-03'
on conflict do nothing;

-- Guía SOFT 18053 INGENIERÍA DE SOFTWARE I: conocimiento previo requerido: Programación de Computadores (código de guía COMP 18036)
insert into public.prerrequisitos (asignatura_id, prerrequisito_id)
select a.id, p.id from public.asignaturas a, public.asignaturas p
where a.codigo = 'IB26-S05-03' and p.codigo = 'IB26-S02-01'
on conflict do nothing;

-- Guía SOFT 18053 INGENIERÍA DE SOFTWARE I: conocimiento previo requerido: Estructura de Datos y Análisis de Algoritmos (código de guía COMP 18037)
insert into public.prerrequisitos (asignatura_id, prerrequisito_id)
select a.id, p.id from public.asignaturas a, public.asignaturas p
where a.codigo = 'IB26-S05-03' and p.codigo = 'IB26-S03-01'
on conflict do nothing;

-- Guía SOFT 18053 INGENIERÍA DE SOFTWARE I: conocimiento previo requerido: Base de Datos I (código de guía INFO 18001)
insert into public.prerrequisitos (asignatura_id, prerrequisito_id)
select a.id, p.id from public.asignaturas a, public.asignaturas p
where a.codigo = 'IB26-S05-03' and p.codigo = 'IB26-S04-03'
on conflict do nothing;

-- Guía GSIN 18017 CIBERSEGURIDAD: conocimiento previo requerido: Internet de las Cosas (código de guía TELE 18052)
insert into public.prerrequisitos (asignatura_id, prerrequisito_id)
select a.id, p.id from public.asignaturas a, public.asignaturas p
where a.codigo = 'IB26-S07-01' and p.codigo = 'IB26-S06-05'
on conflict do nothing;

-- Guía INVE 18020 PROYECTO EN INGENIERÍA DE SISTEMAS II: conocimiento previo requerido: Proyecto en Ingeniería de Sistemas I (código de guía INVE 18019)
insert into public.prerrequisitos (asignatura_id, prerrequisito_id)
select a.id, p.id from public.asignaturas a, public.asignaturas p
where a.codigo = 'IB26-S08-01' and p.codigo = 'IB26-S07-02'
on conflict do nothing;

-- Guía OPER 18045 INVESTIGACIÓN DE OPERACIONES II: conocimiento previo requerido: Investigación de Operaciones I (código de guía OPER 18044)
insert into public.prerrequisitos (asignatura_id, prerrequisito_id)
select a.id, p.id from public.asignaturas a, public.asignaturas p
where a.codigo = 'IB26-S08-02' and p.codigo = 'IB26-S07-03'
on conflict do nothing;

-- Guía SIST 18015 PRÁCTICA EN INGENIERÍA DE SISTEMAS: conocimiento previo requerido: Proyecto en Ingeniería de Sistemas II (código de guía INVE 18020)
insert into public.prerrequisitos (asignatura_id, prerrequisito_id)
select a.id, p.id from public.asignaturas a, public.asignaturas p
where a.codigo = 'IB26-S09-01' and p.codigo = 'IB26-S08-01'
on conflict do nothing;

commit;

-- Cursos citados en las guías que NO se insertaron:
--   Mecánica y Laboratorio (FISI 19012): "Cálculo en una Variable" no es una asignatura del plan (se insertaron Cálculo Diferencial y Cálculo Integral, nombrados aparte).
--   Inteligencia Artificial (COMP 18038): "Bases de datos" no coincide con un nombre exacto (hay Base de Datos I y II); no se infiere.
--   Investigación de Operaciones I (OPER 18044): "Administración de Operaciones" no existe en asignaturas.

-- Verificación (solo lectura)
select count(*) as total_pares from public.prerrequisitos;

select a.codigo as asignatura_codigo, a.nombre as asignatura,
       p.codigo as prerrequisito_codigo, p.nombre as prerrequisito
from public.prerrequisitos r
join public.asignaturas a on a.id = r.asignatura_id
join public.asignaturas p on p.id = r.prerrequisito_id
order by a.codigo, p.codigo;
