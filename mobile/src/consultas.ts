// Las cuatro consultas de la rúbrica, con preguntas redactadas para el agente.
export type Consulta = { clave: string; icono: string; titulo: string; pregunta: string };

export const CONSULTAS: Consulta[] = [
  {
    clave: 'matricula',
    icono: '📝',
    titulo: 'Matrícula',
    pregunta:
      'Quiero matricularme el próximo semestre. ¿Qué asignaturas puedo inscribir según mis prerrequisitos y mi avance, y qué debo tener en cuenta del reglamento (créditos máximos, fechas y requisitos)?',
  },
  {
    clave: 'estado',
    icono: '📊',
    titulo: 'Estado académico',
    pregunta:
      'Muéstrame mi estado académico actual: asignaturas aprobadas, en curso y pendientes, mi promedio, mis créditos cursados y si tengo alguna alerta o riesgo académico.',
  },
  {
    clave: 'proyeccion',
    icono: '🎯',
    titulo: 'Proyección',
    pregunta:
      'Hazme una proyección de mi carrera: cuántos semestres me faltan, qué asignaturas debería cursar en cada uno y cuál sería mi fecha estimada de graduación si sigo este ritmo.',
  },
  {
    clave: 'recomendaciones',
    icono: '💡',
    titulo: 'Recomendaciones',
    pregunta:
      'Dame recomendaciones personalizadas para tener éxito en el programa según mi desempeño: estrategias de estudio, recursos de autoaprendizaje, opciones de investigación y acciones concretas para este semestre.',
  },
];
