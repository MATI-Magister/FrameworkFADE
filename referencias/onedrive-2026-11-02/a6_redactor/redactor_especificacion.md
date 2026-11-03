# A6 · Redactar propuesta · Especificación (v0.1)

Especificación independiente de la herramienta. Describe qué hace el agente, qué recibe, qué entrega y cómo se revisa su resultado.

Este documento es para quien construye y opera el agente. No se carga en el agente: el agente recibe sus instrucciones (`redactor_instrucciones.md`), el esquema de salida (`faed_propuesta.schema.json`) y, en cada ejecución, la información ya revisada del proyecto.

## 1. Propósito y límites

**Propósito.** Redactar en el lenguaje del cliente los textos de cada sección de la plantilla de propuesta: contexto, solución, alcance, supuestos, información por pedir y plan de inicio.

**Lugar en el recorrido.** Después de la validación del escenario y antes de que la Gerencia de Proyectos revise y envíe.

**El agente redacta; la función arma.** A6 no recibe cifras y no escribe ninguna. La función de armado (`armado/llenar_propuesta.py`) pone sus textos en la plantilla junto con las cifras del escenario validado: horas, precios por modalidad, primer bloque y duración. Así, ninguna cifra de la propuesta pasa por el agente.

**Lo que no hace.** No calcula, no elige la modalidad, no cambia los componentes ni sus nombres y no agrega nada que no esté en la información que recibe.

## 2. Recorrido de una ejecución

1. **Redactar.** A6 entrega los textos.
2. **Verificar.** `verificacion/revisar_propuesta.py` revisa la salida.
3. **Armar.** La función pone los textos y las cifras en la plantilla:
   ```
   python armado/llenar_propuesta.py propuesta.json escenario.json juicio.json detalle.json --cliente "Nombre del cliente" -o propuesta.docx
   ```
   Opciones: `--contacto`, `--preparado-por`, `--codigo`, `--modalidades` (las que recomienda el responsable de la propuesta, en orden), `--vigencia` y `--pago` (en días, 30 por defecto) y `--sin-aceptacion` (cuando el cliente contrata con su propio proceso).
4. **Revisar y enviar.** La Gerencia de Proyectos completa lo que la función lista como pendiente, revisa el documento y lo envía.

## 3. Entradas y salida

| Entrada | Descripción |
|---|---|
| Solicitud | Identificador de la solicitud y cliente registrado |
| Parámetros | Confianza del escenario validado, tipo de estimación y si hay primer bloque |
| Ficha | Última versión revisada de la ficha del requerimiento |
| Evaluación | Salida de A2, con sus supuestos y preguntas |
| Componentes | Salida de A3, con sus supuestos |
| Fichas de los componentes | Salida de A4, con fronteras, capacidades, supuestos y vacíos |
| Juicios del escenario | Salida de A5, con la funcionalidad del primer bloque |

**Mensaje que recibe el agente.** Las instrucciones van como mensaje de sistema. Cada ejecución se entrega así:

```
<solicitud id="SOL-2026-0042" cliente="Nombre del cliente registrado" />
<parametros confianza="media" tipo_estimacion="formal" primer_bloque="si" />
<ficha>{ ...ficha en JSON... }</ficha>
<evaluacion>{ ...salida de A2 en JSON... }</evaluacion>
<componentes>{ ...salida de A3 en JSON... }</componentes>
<detalle>{ ...salida de A4 en JSON... }</detalle>
<escenario>{ ...salida de A5 en JSON... }</escenario>
```

El parámetro `primer_bloque` es `si` cuando A5 propuso un bloque y la estimación no es preliminar.

**Salida.** Los textos según `faed_propuesta.schema.json`, compatible con el modo estricto.

## 4. Reglas que conviene conocer

**Cómo presenta la función la inversión.** Sigue la sección 6 del framework:

| Caso | Sección 3 | Modalidades | Plan de inicio | Aceptación |
|---|---|---|---|---|
| Confianza alta | Cifra única: horas, inversión y duración | Las que indique el responsable | Primer bloque o arranque | Sí |
| Confianza media | Rango, que se confirma con el primer bloque o una fase de definición | Las que indique el responsable | Primer bloque o arranque | Sí |
| Confianza baja por experiencia | Rango, con una nota interna: la dirección define cómo presentarlo | Sin precio fijo | Primer bloque o arranque | Sí |
| Información baja | Rango preliminar | Ninguna | Completar la información para emitir la propuesta formal | No |

Si el cliente pidió una modalidad, va primero. La facturación sigue la primera modalidad: mensual por consumo real en bolsa de horas, por sprint completado en sprints y por hitos en primer bloque y precio fijo. Si no se cotizan infraestructura ni licencias, la función agrega su exclusión.

**Duración.** La función la calcula con los sprints redondeados al medio sprint y las semanas por sprint de los valores del método. Mientras la empresa no defina las semanas por sprint, la duración queda entre corchetes como pendiente.

**Pendientes.** Al terminar, la función lista lo que queda entre corchetes (contacto, responsable, firmas, fechas y equipo del arranque) y las decisiones que no tomó, como un precio fijo con confianza baja.

## 5. Revisión de cada salida

La revisión comprueba:

1. **Estructura.** La salida cumple el esquema y corresponde a la solicitud y a la versión de la ficha.
2. **Componentes.** Hay una descripción por cada componente, en el mismo orden.
3. **Sin cifras ni lenguaje interno.** Ningún texto tiene horas, precios, sprints, códigos ni términos del método; los plazos se marcan para confirmar que son del cliente.
4. **Bloque.** El objetivo del bloque y el primer entregable siguen los parámetros: con bloque, el objetivo; sin bloque, el primer entregable; en un rango preliminar, ninguno de los dos.
5. **Cobertura.** Hay supuestos, información por pedir y exclusiones cuando la evaluación y las fichas de los componentes los traen.
6. **Fidelidad.** Cada afirmación sale de la ficha, la evaluación o las fichas de los componentes, sin agregar funcionalidades, compromisos ni beneficios.
7. **Redacción.** Los textos son claros, formales y adecuados para el cliente.

Los puntos 1 a 5 los comprueba `verificacion/revisar_propuesta.py`. Los puntos 6 y 7 los revisa la Gerencia de Proyectos antes de enviar.

## 6. Parámetros y buenas prácticas

- La plantilla (`datos/plantilla_propuesta.docx`) la administra la Gerencia de Proyectos. La función localiza cada parte por su texto (títulos, campos entre corchetes y primeras palabras de las tablas); si la plantilla cambia esos textos, hay que ajustar la función.
- Fijar el modelo y su versión, usar la temperatura más baja que permita la herramienta y registrar la versión de las instrucciones, del esquema y de la plantilla.
- Guardar cada salida y cada documento armado como archivos nuevos ligados a la versión de la ficha y del escenario.
- Mantener los casos de ejemplo fuera del contexto al que tiene acceso el agente.
- Ajustar las instrucciones solo en `redactor_instrucciones.md`, con una versión nueva (v0.2, v0.3…).
