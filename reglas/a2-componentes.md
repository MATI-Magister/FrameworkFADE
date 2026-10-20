# A2 · División en componentes · propuesta para revisión

## Propósito y entrada

Transformar el resumen de requerimiento aceptado en un catálogo de partes de la
solución que puedan comprenderse y estimarse por separado. Usar A1, fuentes,
respuestas y pendientes autorizados por el experto. No se requieren historias
completas ni criterios de aceptación detallados para iniciar la división.

## Cómo dividir

1. Identificar capacidades, procesos y resultados expresados por el cliente.
2. Agrupar trabajo que persiga un mismo propósito y tenga límites comprensibles.
3. Separar cuando cambien propósito, dependencia externa, especialidad necesaria
   o condiciones de ejecución lo suficiente para estimarlo por separado.
4. No imponer una división por pantallas o capas técnicas: una capacidad puede
   requerir interfaz, lógica y datos dentro del mismo componente. Tampoco mantener
   una capacidad excesivamente amplia si oculta trabajos distintos.
5. Separar integraciones o trabajo transversal cuando el alcance lo justifique,
   registrándolo una sola vez. No añadir autenticación, migración, despliegue u
   otras capacidades automáticamente si no hay fuente o necesidad por confirmar.
6. Usar C-001… estables. No limitar el número de componentes ni asignar horas por
   su nombre. Si existen padres e hijos, indicar qué nivel se estima: el total
   del padre no se suma otra vez a sus hijos.
7. Verificar que cada parte del alcance esté cubierta; registrar exclusiones,
   contradicciones y dudas sin resolverlas mediante suposiciones silenciosas.

## Información de cada componente

| Campo | Qué debe poder entender el lector |
| --- | --- |
| Código y nombre | Identificador estable y nombre reconocible para negocio |
| Propósito | Qué necesidad resuelve y quién lo utiliza o recibe su resultado |
| Descripción | Cómo funcionaría a nivel general, con la información disponible |
| Incluye | Capacidades o trabajo que se atribuyen a este componente |
| No incluye | Límites confirmados; si un límite es desconocido, decir por confirmar |
| Resultado esperado | Qué quedaría disponible, sin inventar criterios de aceptación detallados |
| Dependencias | Componentes, sistemas o decisiones necesarios y su relación |
| Fuente | Documento/sección o respuesta que justifica su existencia y alcance |
| Supuestos y pendientes | Condiciones no confirmadas, preguntas e impacto sobre la estimación |
| Condiciones tecnológicas y de seguridad | Requeridas/preferidas/por definir, con fuente y aclaraciones identificadas |

Cada pregunta y cada tarea pendiente tiene un código propio, estable y contestable
individualmente: `C-001-PRE-001` / `C-001-PEN-001`. Usar el registro maestro y
protocolo de `preguntas-componentes.md`. No agrupar varias preguntas en un solo ID.

Tipos de desarrollo, arquetipos, tamaño, complejidad y las demás D1–D11 se
caracterizan formalmente en A3. A2 conserva indicios y preguntas útiles, pero no
fuerza puntuaciones ni elige COCOMO II ni produce estimaciones todavía.

## Resultado y control de calidad

Entregar `03-entregables/a2.md`: explicación de la división, tabla general, ficha
por componente, mapa de cobertura y preguntas pendientes. Usar
el registro `pendientes-componentes.md` y reflejar sus IDs en cada ficha. Usar
`plantillas/componentes.md`. No dejar marcadores de plantilla como contenido final.
Revisar que nombres sean claros, límites no se solapen, fuentes sean trazables y
dependencias visibles. Distinguir una falta de detalle estimable de una duda material
que cambie los límites: ante esta última, pedir aclaración sin inventar alcance.
El cierre posterior no justifica enviar a A3 componentes imposibles de distinguir.

No se agrega una aprobación humana nueva para A2 en esta propuesta; se conserva
el flujo actual. El experto puede pedir ajustes. Si cambiar componentes afecta el
alcance aceptado en A1, explicar el cambio y solicitar su revisión antes de continuar.

Ejemplo ficticio legible en `docs/ejemplo-a2-componentes.md`. No pertenece al piloto.
