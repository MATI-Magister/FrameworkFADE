# Qué puedes compartir para configurar el framework

Puedes entregarlo por partes, con ejemplos reales anonimizados si es necesario.
Indica siempre qué es una propuesta y qué está aprobado, quién lo aprueba y su fecha.

| Insumo | Qué necesitamos | Carpeta |
| --- | --- | --- |
| Requerimiento inicial | Objetivo, usuarios, procesos, funcionalidades, alcance y exclusiones | `proyectos/piloto/01-entradas/requerimientos/` |
| Documentación del cliente | RFP/RQ, anexos, flujos, criterios de aceptación y prioridades | misma carpeta de requerimientos |
| Contexto | Tecnología, integraciones, datos, seguridad, restricciones, equipo y disponibilidad | `proyectos/piloto/01-entradas/contexto/` |
| Aclaraciones | Preguntas y respuestas con responsable y fecha | `proyectos/piloto/01-entradas/respuestas/` |
| Madurez | Ya tenemos el modelo del Excel; falta acordar el criterio de paso y quién acepta | `reglas/` |
| Componentes y clasificación | Partes reconocibles de la solución, dimensiones, niveles y criterios | `reglas/` |
| Método de estimación | Fórmulas o procedimiento, unidad de esfuerzo, referencias históricas | `reglas/` |
| Costos y duración | Moneda, tarifa por rol/unidad, capacidad efectiva, paralelismo y parámetros CFO | `reglas/` |
| Escenarios | Dos escenarios definidos, sus diferencias, contingencias y exclusiones | `reglas/` |
| Entregable final | Ejemplo de informe, nivel de detalle y responsable de revisión | `reglas/` |

Sirven documentos Word/PDF, hojas de cálculo, ejemplos de propuestas anteriores o
explicaciones en texto. Cada herramienta IA deberá poder leer esos formatos.
Yo puedo convertir tus explicaciones en reglas estructuradas, señalar contradicciones
y preparar un borrador para tu aprobación. No necesito que esté todo definido ahora.

Para comenzar, comparte un requerimiento real y ejecuta `!registrar`. Después,
`!madurez` inicia A1 con las 11 dimensiones y 109 criterios del Excel incorporado.
El agente evalúa la información, entrega un resumen legible y pregunta por las brechas;
no declara aceptación automáticamente. No debes rellenar el JSON técnico: lo hace
el agente con tus documentos y respuestas.

Ya existe una propuesta para comenzar sin método previo en
`reglas/propuesta-inicial.md`. La revisaremos paso a paso. Los documentos finales
deben poder leerlos personas: resumen del requerimiento, componentes y estimación.
No necesitas proporcionar información propia de una historia de usuario.
