from pathlib import Path

DESTINO = Path("rag/documents/materias_sinteticas")

MATERIAS = [
    {
        "codigo": "IB26-S01-02",
        "nombre": "Expresión",
        "semestre": 1,
        "creditos": 4,
        "descripcion": "Explora la comunicación de ideas mediante diferentes lenguajes y formas de representación. Se enfoca en desarrollar habilidades para expresar, organizar y transmitir información de manera clara, coherente y adecuada a distintos contextos.",
        "proposito": "Fortalecer la capacidad de comunicar ideas, interpretar información y presentar propuestas de forma comprensible.",
        "temas": [
            "Comunicación oral y escrita.",
            "Comprensión e interpretación de textos.",
            "Organización y estructuración de ideas.",
            "Argumentación y pensamiento crítico.",
            "Representación visual de información.",
            "Presentación de proyectos y propuestas."
        ],
        "aplicaciones": [
            "Elaboración de informes técnicos.",
            "Presentación de proyectos de software.",
            "Documentación de soluciones tecnológicas."
        ]
    },
    {
        "codigo": "IB26-S02-05",
        "nombre": "Identidad",
        "semestre": 2,
        "creditos": 3,
        "descripcion": "Aborda la construcción de la identidad personal, social y profesional, así como la relación entre las personas, sus valores, sus decisiones y los entornos en los que participan.",
        "proposito": "Promover la reflexión sobre la identidad, la responsabilidad individual y la participación consciente en diferentes comunidades.",
        "temas": [
            "Identidad personal y colectiva.",
            "Autoconocimiento y proyecto de vida.",
            "Valores y responsabilidad.",
            "Identidad y ciudadanía.",
            "Diversidad y convivencia.",
            "Identidad en entornos digitales."
        ],
        "aplicaciones": [
            "Construcción de una identidad profesional.",
            "Participación responsable en comunidades digitales.",
            "Reflexión ética sobre el ejercicio profesional."
        ]
    },
    {
        "codigo": "IB26-S03-02",
        "nombre": "Creatividad",
        "semestre": 3,
        "creditos": 3,
        "descripcion": "Estudia procesos de generación, exploración y desarrollo de ideas para abordar situaciones y proponer alternativas de solución.",
        "proposito": "Estimular el pensamiento creativo y la capacidad de transformar ideas en propuestas que puedan analizarse y desarrollarse.",
        "temas": [
            "Pensamiento creativo y divergente.",
            "Identificación de problemas y oportunidades.",
            "Técnicas de generación de ideas.",
            "Design Thinking.",
            "Experimentación y prototipado.",
            "Evaluación y mejora de propuestas."
        ],
        "aplicaciones": [
            "Diseño de productos digitales.",
            "Prototipado de aplicaciones.",
            "Propuesta de soluciones innovadoras."
        ]
    },
    {
        "codigo": "IB26-S03-05",
        "nombre": "Matemáticas Computacionales",
        "semestre": 3,
        "creditos": 3,
        "descripcion": "Presenta conceptos matemáticos y computacionales que permiten representar, analizar y resolver problemas mediante procedimientos formales y herramientas computacionales.",
        "proposito": "Desarrollar capacidades de razonamiento lógico, modelación y solución estructurada de problemas.",
        "temas": [
            "Lógica matemática y proposicional.",
            "Conjuntos y relaciones.",
            "Funciones y estructuras discretas.",
            "Sistemas de numeración.",
            "Fundamentos de algoritmia.",
            "Modelación matemática de problemas."
        ],
        "aplicaciones": [
            "Diseño y análisis de algoritmos.",
            "Representación de información.",
            "Resolución computacional de problemas."
        ]
    },
    {
        "codigo": "IB26-S06-02",
        "nombre": "Ciencias de Datos",
        "semestre": 6,
        "creditos": 3,
        "descripcion": "Introduce el análisis de datos como proceso para obtener información, identificar patrones y apoyar la toma de decisiones mediante técnicas estadísticas y computacionales.",
        "proposito": "Comprender las etapas generales de un proyecto de análisis de datos y sus posibilidades de aplicación.",
        "temas": [
            "Fundamentos de ciencia de datos.",
            "Recolección y preparación de datos.",
            "Limpieza y transformación de información.",
            "Análisis exploratorio.",
            "Estadística descriptiva.",
            "Visualización de datos.",
            "Introducción al aprendizaje automático."
        ],
        "aplicaciones": [
            "Análisis de información empresarial.",
            "Construcción de visualizaciones.",
            "Identificación de patrones en conjuntos de datos."
        ]
    },
    {
        "codigo": "IB26-S06-04",
        "nombre": "Ingeniería de Software II",
        "semestre": 6,
        "creditos": 3,
        "descripcion": "Amplía los fundamentos de ingeniería de software mediante el estudio de actividades, métodos y prácticas para construir, verificar, mantener y evolucionar sistemas de software.",
        "proposito": "Comprender prácticas de desarrollo de software que permitan gestionar soluciones de mayor complejidad y mejorar su calidad.",
        "temas": [
            "Arquitectura y diseño de software.",
            "Patrones de diseño.",
            "Principios de calidad de software.",
            "Pruebas de software.",
            "Integración y despliegue.",
            "Mantenimiento y evolución.",
            "Gestión de configuración y versiones."
        ],
        "aplicaciones": [
            "Diseño de arquitecturas de aplicaciones.",
            "Construcción de pruebas automatizadas.",
            "Mantenimiento de sistemas de software."
        ]
    },
    {
        "codigo": "IB26-S06-03",
        "nombre": "Teoría de Sistemas y Organizaciones",
        "semestre": 6,
        "creditos": 3,
        "descripcion": "Estudia las organizaciones desde una perspectiva sistémica, considerando sus componentes, relaciones, objetivos, procesos e interacción con el entorno.",
        "proposito": "Comprender las organizaciones como sistemas y analizar cómo la tecnología puede apoyar sus procesos y objetivos.",
        "temas": [
            "Fundamentos del pensamiento sistémico.",
            "Concepto y características de los sistemas.",
            "Organizaciones como sistemas abiertos.",
            "Procesos y estructuras organizacionales.",
            "Relaciones entre sistemas y entorno.",
            "Sistemas de información en organizaciones.",
            "Análisis de problemas organizacionales."
        ],
        "aplicaciones": [
            "Análisis de procesos empresariales.",
            "Identificación de necesidades de información.",
            "Diseño de soluciones tecnológicas organizacionales."
        ]
    },
    {
        "codigo": "IB26-S08-03",
        "nombre": "Dinámica de Sistemas",
        "semestre": 8,
        "creditos": 3,
        "descripcion": "Aborda el estudio del comportamiento de sistemas complejos a través del tiempo, considerando relaciones de retroalimentación, acumulaciones, flujos y demoras.",
        "proposito": "Comprender y representar sistemas dinámicos para analizar comportamientos y explorar escenarios de evolución.",
        "temas": [
            "Fundamentos de dinámica de sistemas.",
            "Pensamiento sistémico.",
            "Diagramas causales.",
            "Bucles de retroalimentación.",
            "Variables de nivel y flujo.",
            "Modelos de simulación.",
            "Análisis de escenarios."
        ],
        "aplicaciones": [
            "Modelación de procesos organizacionales.",
            "Simulación de sistemas complejos.",
            "Análisis de escenarios para apoyar decisiones."
        ]
    }
]

DESTINO.mkdir(parents=True, exist_ok=True)

for materia in MATERIAS:
    contenido = f"""# {materia['nombre']}

> **CONTENIDO SINTÉTICO — NO OFICIAL**
>
> Este documento es material de referencia elaborado para el chatbot académico iBanú. No corresponde a una guía de cátedra, microcurrículo ni documento aprobado o publicado por la UNAB. Los temas y aplicaciones son orientativos y deben contrastarse con la documentación institucional cuando esté disponible.

## Identificación

- Código interno: {materia['codigo']}
- Semestre: {materia['semestre']}
- Créditos: {materia['creditos']}
- Fuente: elaboración sintética para iBanú
- Estado de verificación: pendiente
- Estado de vigencia: pendiente de validación

## Descripción general

{materia['descripcion']}

## Propósito formativo orientativo

{materia['proposito']}

## Temáticas orientativas

""" + "\n".join(f"- {tema}" for tema in materia["temas"]) + """

## Posibles aplicaciones en Ingeniería de Sistemas

""" + "\n".join(f"- {aplicacion}" for aplicacion in materia["aplicaciones"]) + """

## Alcance y limitaciones

La información anterior constituye una aproximación temática general basada en el nombre de la asignatura y su ubicación en el catálogo provisional suministrado para iBanú. No permite confirmar contenidos oficiales, competencias, resultados de aprendizaje, metodología, evaluación, bibliografía, profesor ni prerrequisitos.

Para obtener información institucional definitiva se requiere una guía de cátedra o fuente oficial de la UNAB.
"""

    ruta = DESTINO / f"{materia['codigo']}.md"
    ruta.write_text(contenido, encoding="utf-8")

print("FICHAS SINTÉTICAS GENERADAS")
print("Total:", len(MATERIAS))

for materia in MATERIAS:
    print(materia["codigo"], "-", materia["nombre"])
