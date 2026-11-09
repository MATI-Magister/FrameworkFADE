# Resultados para personas

Esta pauta gobierna la presentación de todos los agentes y roles. Prevalece sobre
ejemplos antiguos que acumulen tablas o repitan el expediente. No cambia el modelo,
las evidencias requeridas, los cálculos ni las aprobaciones.

## Informe de cada paso

El archivo principal en 03-entregables/ responde: ¿qué produjo este paso?,
¿qué necesito revisar o contestar? y ¿cómo continúo?

- Abrir con el resultado concreto en dos o tres frases. No abrir con inventario de
  entradas, explicación del método, lista de controles o historia del proceso.
- Mostrar solo el producto de la etapa. Referenciar resultados anteriores en vez
  de copiarlos. En una reevaluación, destacar qué cambió.
- Usar títulos cotidianos y párrafos cortos. Explicar términos técnicos necesarios.
  Los códigos de criterios y dimensiones van al respaldo; conservar los códigos
  de componentes y preguntas que la persona necesita para responder.
- Procurar una página de lectura inicial. Es una orientación, no un límite para
  omitir componentes, riesgos o condiciones materiales. Si hay muchos componentes,
  mostrar un listado breve y enlazar las fichas completas.
- Usar tablas para comparar, normalmente con cuatro columnas como máximo.
  No repetir todos sus valores en prosa ni crear filas vacías.
- Destacar supuestos y pendientes que cambian alcance, cifras o decisión actual.
  Cada pregunta tiene código y una sola cuestión. El registro maestro conserva
  todos los pendientes, incluidos los no destacados.
- Cerrar con una siguiente acción y el comando correspondiente al estado real.
  No ofrecer aprobación si todavía existe un bloqueo.

## Respaldo separado

Guardar criterios, dimensiones completas, fuentes, citas, procesos, cobertura,
fórmulas y comprobaciones en 02-trabajo/, con enlaces relativos desde el informe.
El detalle se conserva en Markdown además del JSON cuando sea necesario para que
una persona pueda verificarlo. No trasladar al respaldo una condición material
sin mencionarla en el informe principal.

Usar respaldo-registro.md, respaldo-a1.md, respaldo-a2.md, respaldo-a3.md y
respaldo-revision.md en 02-trabajo/. A4 conserva su carpeta de cálculo versionada
y su informe de soporte. preguntas-a1.md, pendientes-componentes.md y ajustes.md
mantienen sus ubicaciones y códigos; enlazarlos sin copiarlos completos en cada paso.
Los informes automáticos son soporte: el agente redacta la conclusión específica
del requerimiento. No pegar su salida técnica como resultado principal.

## Respuesta en el chat

Presentar el resultado en un párrafo o tabla breve, las decisiones necesarias y
un enlace al informe. Orientación: 150–250 palabras; ampliar para preguntas que
el experto debe responder. No pegar todo el entregable, logs, huellas ni una lista
de archivos generados. Si hay muchas preguntas, usar una lista codificada clara o
enlazar su archivo. Un bloqueo se presenta como bloqueo, explicando qué falta.

## Antes de entregar

Comprobar: ¿se entiende el resultado sin conocer FADE?, ¿se ve qué debe decidir
el experto?, ¿las cifras tienen unidades?, ¿las condiciones materiales están
visibles?, ¿el respaldo permite verificarlo? Reescribir si la conclusión está oculta.
