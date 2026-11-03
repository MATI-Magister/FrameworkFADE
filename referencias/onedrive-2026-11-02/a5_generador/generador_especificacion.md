# A5 · Generar escenario · Especificación (v0.1)

Especificación independiente de la herramienta. Describe qué hace el agente, qué recibe, qué entrega y cómo se revisa su resultado.

Este documento es para quien construye y opera el agente. No se carga en el agente: el agente recibe sus instrucciones (`generador_instrucciones.md`), el esquema de salida (`faed_juicio_escenario.schema.json`) y, en cada ejecución, la ficha, las fichas de los componentes y la preparación que calculan las funciones.

## 1. Propósito y límites

**Propósito.** Preparar los dos juicios que necesita el escenario: qué proyectos del registro son de verdad comparables y qué procesos forman el primer bloque de trabajo.

**Lugar en el recorrido.** Después de A4 · Detallar y del cálculo de horas de cada componente; antes de la validación.

**El agente juzga; las funciones calculan.** Las funciones preparan lo que recibe A5 (talla y arquetipos del proyecto, candidatos a comparables, horas de cada proceso) y, con los juicios de A5 y la respuesta del Tech lead sobre la experiencia del equipo, calculan la experiencia, la confianza, el rango, los precios de cada modalidad y la ruta.

**Lo que no hace.** No calcula ningún nivel, horas ni precios; no califica la experiencia del equipo; no agrega proyectos al registro ni cambia sus datos.

## 2. Recorrido de una ejecución

1. **Preparar.** La función arma lo que recibe el agente:
   ```
   python calculo/faed_calculos.py preparar detalle.json --registro datos/registro_proyectos.json > preparacion.json
   ```
   Un proyecto del registro es candidato si es del mismo arquetipo principal, de talla igual o adyacente y tiene horas reales: es la definición de proyecto comparable del framework. La preparación también cuenta los proyectos con componentes de cada arquetipo secundario y califica de 0 a 3 los datos registrados de cada candidato.
2. **Juzgar.** A5 confirma cada candidato y propone el primer bloque.
3. **Verificar.** `verificacion/revisar_escenario.py` revisa la salida.
4. **Calcular.** La función calcula el escenario con los juicios de A5 y la respuesta del Tech lead:
   ```
   python calculo/faed_calculos.py escenario detalle.json juicio.json --registro datos/registro_proyectos.json --nivel-informacion media --experiencia-equipo 2 [--modalidad bloque] [--cliente-estrategico]
   ```
5. **Validar.** El validador o la dirección, según la ruta, revisa el escenario.

## 3. Entradas y salida

| Entrada | Descripción |
|---|---|
| Solicitud | Identificador de la solicitud y cliente registrado |
| Parámetros | Tipo de estimación (formal o preliminar) y modalidad que pidió el cliente |
| Ficha | Última versión revisada de la ficha del requerimiento |
| Fichas de los componentes | Salida de A4 · Detallar, ya verificada |
| Preparación | Salida de la función `preparar` |

**Mensaje que recibe el agente.** Las instrucciones van como mensaje de sistema. Cada ejecución se entrega así:

```
<solicitud id="SOL-2026-0042" cliente="Nombre del cliente registrado" />
<parametros tipo_estimacion="formal" modalidad_solicitada="ninguna" />
<ficha>{ ...ficha en JSON... }</ficha>
<componentes>{ ...salida de A4 en JSON... }</componentes>
<preparacion>{ ...salida de la función preparar en JSON... }</preparacion>
```

**Salida.** Los juicios según `faed_juicio_escenario.schema.json`, compatible con el modo estricto.

**Entradas de la función de escenario que no vienen del agente.**

| Dato | Quién lo da |
|---|---|
| Nivel de información | Evaluación de A2, revisada por el Tech lead |
| Experiencia del equipo en proyectos similares (0 a 3) | Tech lead: 0 ninguna, 1 genérica, 2 uno a dos proyectos similares, 3 tres o más |
| Modalidad, cliente estratégico e infraestructura y licencias | Responsable de la propuesta |

## 4. Reglas que conviene conocer

**Comparables.** El agente solo puede descartar candidatos, nunca agregar. Cuenta un candidato solo si su descripción y sus componentes muestran que el trabajo principal se parece; ante la duda, no cuenta y queda en las advertencias para que el Tech lead lo resuelva, porque un comparable de más sube la experiencia y estrecha el rango sin respaldo. Con cero o un comparable, la experiencia es baja y la cotización sigue la ruta compleja.

**Arquetipo principal en casi empate.** Si otro arquetipo queda a menos de 5 puntos porcentuales del principal (valor del método), la preparación también trae los proyectos de ese arquetipo como candidatos y lo indica. Así, una diferencia mínima de horas no deja por fuera a los proyectos que más se parecen. Ante un empate exacto, el principal es el de más procesos.

**Datos de los comparables.** Los califica la función con la escala del anexo B.2 y toma el del comparable con datos menos completos, para no sobreestimar la experiencia.

**Primer bloque.** El agente no propone bloque si la estimación es preliminar, si el cliente pidió otra modalidad o si el proyecto completo cabe en un bloque. En los demás casos, el bloque reúne los procesos de una funcionalidad que el cliente puede usar, más las partes de otros componentes que esos procesos necesitan, y suma entre 320 y 480 horas con su parte de gestión. El responsable de la estimación revisa la propuesta y el responsable de la propuesta la acuerda con el cliente.

## 5. Revisión de cada salida

La revisión comprueba:

1. **Estructura.** La salida cumple el esquema y corresponde a la solicitud y a la versión de la ficha.
2. **Comparables.** Hay un juicio con justificación por cada candidato, en el mismo orden, y ningún proyecto de más.
3. **Bloque.** Se propone solo cuando corresponde; sus procesos existen, no se repiten y suman horas dentro del tamaño del bloque.
4. **Funcionalidad.** Está escrita sin códigos internos, porque pasa a la propuesta.
5. **Supuestos.** Si el bloque incluye procesos de componentes *Supuestos*, la salida lo advierte.
6. **Juicio de comparables.** Cada comparable que se contó se parece de verdad y cada duda registrada quedó resuelta.
7. **Valor del bloque.** La funcionalidad responde al problema del cliente y el bloque incluye lo que necesita para funcionar.

Los puntos 1 a 5 los comprueba `verificacion/revisar_escenario.py`. Los puntos 6 y 7 requieren criterio humano.

## 6. Parámetros y buenas prácticas

- Mantener el registro de proyectos al día: cada cierre agrega un proyecto, con sus horas reales, su duración, sus procesos medidos y su equipo. Un registro completo sube la calificación de los datos y la experiencia.
- Describir cada proyecto del registro con el tipo de solución, el tipo de cambio y sus capacidades principales: es lo que el agente compara.
- Fijar el modelo y su versión, usar la temperatura más baja que permita la herramienta y registrar la versión de las instrucciones, del esquema, del registro y de los valores del método.
- Guardar cada salida como un archivo nuevo ligado a la versión de la ficha.
- Mantener los casos de ejemplo fuera del contexto al que tiene acceso el agente.
- Ajustar las instrucciones solo en `generador_instrucciones.md`, con una versión nueva (v0.2, v0.3…).
