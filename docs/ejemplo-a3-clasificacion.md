# Ejemplo A3 · Registro de solicitudes de soporte

**Caso ficticio para mostrar el formato. No pertenece al piloto ni es una estimación.**
Continúa C-001 del ejemplo A2 con aclaraciones adicionales expresamente inventadas
para esta demostración. No cambia el estado de las preguntas del ejemplo A2 original.

## Resumen para el experto

El componente permite registrar una solicitud con sus adjuntos. En este ejemplo
es una funcionalidad nueva de aplicación, tiene un proceso funcional identificado
y complejidad media. Utiliza el acceso compartido C-005 sin volver a construir su
integración. Falta confirmar reuso, límites de archivos y disponibilidad del equipo,
por lo que la clasificación es parcial y requiere cierre.

## Evidencias ficticias de esta demostración

| Referencia | Aclaración supuesta, no recibida del usuario |
| --- | --- |
| EX-01 | Toda la funcionalidad de C-001 es nueva. |
| EX-02 | Un proceso «registrar solicitud», que incluye adjuntos en la misma operación; movimientos de datos todavía sin detallar. |
| EX-03 | Análisis técnico: reglas 1, arquitectura 0, seguridad 1, procesamiento 0, dependencias 1. |
| EX-04 | Una interfaz simple conocida de C-001 con C-005, sin otras interfaces ni condiciones I3 en este límite. El directorio se integra en C-005. |
| EX-G01 | Condiciones comunes: nube y directorio corporativo; matriz de experiencia del equipo justifica familiaridad T2. |
| EX-G02 | Equipo parcialmente identificado, dedicación sin confirmar; sector del cliente: Comercio. |
| EX-G03 | Ausencia de proyectos comparables confirmada. |
| EX-05 | D8.01–D8.08 locales: 3, 2, 2, 1, 2, 2, 1, 0. Cinco elementos alcanzan ≥2. |

En un caso real las referencias apuntarán a documentos/respuestas codificadas,
con sección y versión. «Sustentado en el ejemplo» significa que existe una fuente
ficticia explicada aquí; no significa aprobado por el experto.

## C-001 · Clasificación por dimensión

| Dimensión | Resultado | Explicación para el experto | Fuente / origen | Estado |
| --- | --- | --- | --- | --- |
| D1 · Tipo de desarrollo | Nuevo desarrollo; 100 % del alcance funcional de C-001 nuevo | Se crea una capacidad nueva; esto no significa que no se reutilice código. | EX-01 / local | Sustentado en el ejemplo |
| D2 · Arquetipo | Aplicaciones y soluciones digitales | El propósito principal es registrar información de soporte; el acceso es compartido. | Alcance A2 y EX-01 / local | Sustentado en el ejemplo |
| D3 · Tamaño funcional | XS: un proceso; puntos funcionales por confirmar | Registro con adjuntos es una operación completa según el inventario. XS no significa una hora ni un punto funcional. | EX-02 / local | Conteo sustentado; medición detallada pendiente |
| D4 · Complejidad | Media: 3/10 | Reglas 1 + arquitectura 0 + seguridad 1 + procesamiento 0 + dependencias 1. | EX-03 / local | Sustentado en el ejemplo |
| D5 · Integración | I1: una interfaz simple | Consume acceso C-005. La construcción de la conexión al directorio se cuenta allí una sola vez. | EX-04 / local | Sustentado en el ejemplo |
| D6 · Reutilización | R pendiente; porcentaje desconocido | No hay inventario ni base de cálculo del reuso. No se usa cero por defecto. | C-001-PRE-005, C-001-PEN-001 | Por confirmar |
| D7 · Entorno tecnológico | Nube/directorio como condiciones; familiaridad T2 | T2 proviene de la experiencia del equipo, no de la palabra nube. | EX-G01 / global heredado | Sustentado en el ejemplo |
| D8 · Madurez del alcance | M3 · Definido, cinco elementos ≥2 | Hay vacíos en reglas, calidad y aceptación. M3 del componente es distinto del N3 global de A1. | EX-05 / local | Sustentado en el ejemplo |
| D9 · Contexto de ejecución | Parcialmente conocido | Parte del equipo está identificado; falta dedicación para planificar duración. | EX-G02, G-PRE-001 / global heredado | Parcial, dedicación por confirmar |
| D10 · Sector | Comercio | Se hereda del cliente, no se deduce del nombre del componente. Restricciones específicas requieren sus fuentes. | EX-G02 / global heredado | Sector sustentado en el ejemplo |
| D11 · Evidencia histórica | E1: cero comparables disponibles | Ausencia confirmada: limita la técnica disponible, no hay que repetir la pregunta sobre cantidad. | EX-G03 / global heredado | Condición conocida |

## Justificación de la complejidad

En EX-03 se supone: reglas con validaciones/excepciones (1), arquitectura conocida
(0), controles específicos de información/archivos (1), captura sin procesamiento
especializado (0) y dependencia de acceso/almacenamiento (1). Suma 3, clase media.
Si un factor estuviera sin definir en el caso real, no se lo trataría como cero.

## Justificación de M3 de alcance

| Elemento D8 local | Puntaje ficticio |
| --- | --- |
| D8.01 · Objetivo | 3 |
| D8.02 · Usuarios y roles | 2 |
| D8.03 · Funcionalidades | 2 |
| D8.04 · Reglas | 1 |
| D8.05 · Integraciones | 2 |
| D8.06 · Datos | 2 |
| D8.07 · Requisitos no funcionales | 1 |
| D8.08 · Criterios de aceptación | 0 |

Cinco elementos ≥2 corresponden a M3 (5–6). La aplicación de este checklist por
componente es una propuesta de A3; no modifica el nivel global de A1.

## Preguntas y pendientes para el experto

Conservar códigos de A2 y asignar nuevos solo a asuntos nuevos. Estas filas son
vistas del registro maestro; responsables por asignar en este ejemplo.

| Código | Pregunta o acción | Dimensiones | Origen | Estado |
| --- | --- | --- | --- | --- |
| C-001-PRE-001 | ¿Qué campos serán obligatorios al registrar una solicitud? | D3, D4, D8 | A2 | Pendiente |
| C-001-PRE-002 | ¿Qué tipos de archivos se podrán adjuntar? | D4, D8 | A2 | Pendiente |
| C-001-PRE-003 | ¿Cuál será el tamaño máximo permitido por archivo? | D4, D7 | A2 | Pendiente |
| C-001-PRE-004 | ¿Cuántas solicitudes se esperan por día? | D4, D7 | A2 | Pendiente |
| C-001-PRE-005 | ¿Qué porcentaje de C-001 puede resolverse con activos reutilizables identificados? | D6 | Nueva en A3 | Pendiente |
| C-001-PEN-001 | Entregar inventario de activos reutilizables con base de cálculo del porcentaje. | D6 | Nueva en A3, evidencia para PRE-005 | Pendiente |
| G-PRE-001 | ¿Qué dedicación tendrá cada integrante del equipo para este proyecto? | D9 | Compartida | Pendiente |

G-PRE-001 se registra una sola vez para todos los componentes con ese equipo.
Responder un asunto no cierra los demás ni aprueba la clasificación.

## Conclusión de clasificación

**Parcial; requiere cierre de aclaraciones.** Hay base ficticia para tipo,
arquetipo, conteo y complejidad; quedan pendientes reuso, archivos y dedicación.

**Método candidato:** descomposición técnica como primera vía a revisar. COCOMO II
puede estudiarse para el software si hay tamaño compatible, factores y calibración;
«XS» o «un proceso» no bastan para calcularlo. No hay horas/costos/duración aquí.

El informe completo repite la ficha D1–D11 para C-002…C-005 con fuentes y códigos
propios. No se copian las clases de C-001 a los demás componentes.
