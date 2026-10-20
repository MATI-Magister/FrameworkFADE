# Preguntas y pendientes por componente

Regla solicitada por el usuario: cada pregunta y cada pendiente tiene su código,
para responderlos o resolverlos individualmente. Aplica desde A2 y continúa en
A3 y cierre; no altera los IDs de criterios del modelo de madurez A1.

## Identificación estable

- `C-001-PRE-001`: primera pregunta del componente C-001.
- `C-001-PEN-001`: primera acción pendiente del componente C-001.
- Usar secuencias independientes por componente y tipo, con al menos tres dígitos.
- No renumerar al reordenar, cerrar, reintentar o agregar información. Consultar
  también el historial antes de asignar otro ID. No reutilizar códigos retirados.
- Una pregunta pide una sola decisión/dato. Separar «¿qué nube y qué región?» en
  dos códigos para poder contestar uno sin cerrar el otro.
- Una tarea pendiente identifica una acción o evidencia que debe entregarse;
  ejemplo: proporcionar documentación de la integración. Si depende de una pregunta,
  vincular su código. No duplicar la misma necesidad en dos registros independientes.
- Para un asunto compartido usar `G-PRE-001` o `G-PEN-001`, con todos los componentes
  afectados. Es un único asunto global con varias referencias, no varias preguntas.

## Registro y presentación

Registro maestro por proyecto: `03-entregables/pendientes-componentes.md`, usando
`plantillas/pendientes-componentes.md`. Las fichas de componentes muestran sus
preguntas/pendientes con el mismo código; cualquier listado consolidado es una vista
del registro maestro. A2 crea el registro si hay asuntos abiertos; A3 y cierre
lo consultan y agregan sin cambiar identidades. Si no hay asuntos, indicarlo.

Por asunto registrar código, componente(s), tipo, pregunta/acción clara, motivo o
impacto, dimensión/criterio si se conoce, responsable o «por asignar», estado y
evidencia de resolución. Mostrar las preguntas de forma comprensible para negocio.

Respuestas e historial en `01-entradas/respuestas/respuestas-componentes.md`:
código, texto de la respuesta, fuente/adjunto, responsable y fecha. Conservar
respuestas anteriores y señalar cuál reemplaza a cuál; no sobrescribir el historial.
No inventar quién responde ni tratar el propio agente como aprobación experta.

## Cómo contesta el experto

Puede responder en texto o con la convención de chat:

```text
!responder C-001-PRE-001 El proveedor de nube será el indicado en el contrato adjunto.
```

El agente identifica el registro y guarda la respuesta. Si el código no existe o
el texto no permite identificarlo sin duda, solicita aclaración antes de asociarlo.
También acepta varias respuestas, cada una con su código. Es una edición local
realizada por el agente, sin requerir un servicio externo o parser adicional.

Estados: **pendiente**, **respondido**, **requiere aclaración**, **resuelto**,
**descartado**. Recibir una respuesta deja el asunto respondido; solo marcarlo
resuelto cuando cubra la pregunta/acción y se incorpore o referencie la evidencia.
Una entrega parcial no cierra todo el asunto. Descartar requiere motivo y decisión
explícita; conservar el código y su historial.

## Efecto sobre el flujo

Responder no aprueba etapas ni recalcula madurez por sí solo. Si el experto pide
reevaluar A1 antes de aprobar, usar `!complementar`. Si cambia el alcance o afecta
una entrega finalizada, registrar impacto y adenda o solicitar el reintento aplicable;
no modificar silenciosamente un documento congelado. Para cerrar, verificar los
IDs materiales abiertos; no omitir el cierre porque algunos asuntos fueron respondidos.
