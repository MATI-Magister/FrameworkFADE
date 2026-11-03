# Agentes de FAED · Guía del paquete

Este paquete reúne lo necesario para operar los agentes de FAED, verificar lo que producen y calcular las horas y los precios sin inteligencia artificial.

**Para quién es cada documento.**

| Documento | Para quién | Para qué |
|---|---|---|
| `agentes_flujo.md` | Todo el equipo y los evaluadores | Entender el flujo: qué hace cada agente, dónde decide una persona y qué significa cada término (glosario en la sección 6) |
| Esta guía | Quien instala y opera los agentes | Cargar los agentes, preparar las fuentes y correr verificaciones y funciones |
| `*_especificacion.md` | Quien opera cada agente | Qué recibe, qué entrega y cómo se revisa |
| `*_instrucciones.md` y `*.schema.json` | El agente | Su texto de instrucciones y la forma de su respuesta |

Los comandos de esta guía se ejecutan en una terminal; quien no programa puede saltarlos y quedarse con la sección "Recorrido de una cotización".

## Contenido

| Carpeta o archivo | Qué contiene | Quién lo usa |
|---|---|---|
| `agentes_flujo.md` | Diseño del flujo: principios, proceso, fichas de los agentes, funciones, datos y controles humanos | Todo el equipo |
| `diagramas/` | Proceso con agentes en BPMN, en imagen y en archivo editable de draw.io | Todo el equipo |
| `a1_estructurador/` | Instrucciones, esquema de salida y especificación de A1 · Estructurar | El agente (instrucciones y esquema) y quien lo opera (especificación) |
| `a2_evaluador/` | Instrucciones, esquema de salida y especificación de A2 · Evaluar la información | El agente (instrucciones y esquema) y quien lo opera (especificación) |
| `a3_divisor/` | Instrucciones, esquema de salida y especificación de A3 · Dividir | El agente (instrucciones y esquema) y quien lo opera (especificación) |
| `a4_detallador/` | Instrucciones, esquema de salida y especificación de A4 · Detallar | El agente (instrucciones y esquema) y quien lo opera (especificación) |
| `a5_generador/` | Instrucciones, esquema de salida y especificación de A5 · Generar escenario | El agente (instrucciones y esquema) y quien lo opera (especificación) |
| `a6_redactor/` | Instrucciones, esquema de salida y especificación de A6 · Redactar propuesta | El agente (instrucciones y esquema) y quien lo opera (especificación) |
| `a7_cierre/` | Instrucciones, esquema de salida y especificación de A7 · Cerrar y aprender | El agente (instrucciones y esquema) y quien lo opera (especificación) |
| `datos/` | Catálogo de activos, mapa de tecnologías y registro de proyectos de la empresa, en blanco y con su formato; plantilla de propuesta | A4, A5, A7 y la función de armado |
| `verificacion/` | Verificación de las salidas de A1 a A7 | Quien revisa cada versión |
| `calculo/` | Funciones de cálculo y valores del método | Los agentes A4, A5 y A7, a través de las funciones |
| `armado/` | Función que arma la propuesta en la plantilla con los textos de A6 y las cifras del escenario | La Gerencia de Proyectos |
| `registro/` | Función que registra el cierre confirmado en el registro de proyectos y en el catálogo de activos | El dueño del framework |
| `pruebas/` | Casos de ejemplo y prueba del paquete | Quien prueba los agentes, **nunca el agente** |

## Recorrido de una cotización

Cada paso produce un archivo que recibe el siguiente. Los nombres son sugeridos.

| Paso | Lo hace | Recibe | Produce |
|---|---|---|---|
| 1. Estructurar | A1; el Tech lead revisa | Fuentes en texto y ficha vigente | `ficha_vN.json` |
| 2. Evaluar la información | A2; el Tech lead confirma | Ficha | `evaluacion_vN.json` |
| 3. Dividir | A3 | Ficha y evaluación | `componentes.json` |
| 4. Detallar | A4; el Tech lead confirma reúso y tecnologías nuevas | Ficha, componentes, catálogo y mapa | `detalle.json` |
| 5. Preparar el escenario | Función `preparar` | Detalle y registro de proyectos | `preparacion.json` |
| 6. Generar escenario | A5; el Tech lead indica la experiencia del equipo | Ficha, detalle y preparación | `juicio.json` |
| 7. Calcular el escenario | Función `escenario` | Detalle, juicio, registro y parámetros | `escenario.json` |
| 8. Validar | Validador o dirección, según la ruta | Escenario | Escenario aprobado |
| 9. Redactar | A6 | Ficha, evaluación, componentes, detalle y juicio | `propuesta.json` |
| 10. Armar | Función de armado; la Gerencia revisa y envía | Propuesta, escenario, juicio y detalle | `propuesta.docx`; el escenario enviado queda como `linea_base.json` |
| 11. Preparar el cierre | Función `cierre` | Línea base, horas de Jira y cambios de alcance | `preparacion_cierre.json` |
| 12. Cerrar y aprender | A7; el líder del proyecto confirma | Preparación del cierre, detalle, propuesta, catálogo y notas de cierre | `cierre.json` |
| 13. Registrar | Función de registro | Cierre confirmado, preparación, línea base y detalle | Versiones nuevas del registro de proyectos y del catálogo |
| 14. Revisar indicadores | Función `indicadores`; el dueño del framework | Registro y catálogo | Indicadores y disparador de recalibración |

Cada salida de un agente pasa por su verificación antes de que una persona la confirme.

## Qué se carga en cada agente

- **Las instrucciones** (`*_instrucciones.md`) van como mensaje de sistema.
- **El esquema** (`*.schema.json`) se carga como salida estructurada, si la herramienta lo permite. Si no, se agrega al final de las instrucciones bajo el título "Esquema de salida".
- **La especificación** (`*_especificacion.md`) no se carga en el agente: explica cómo operarlo y cómo revisar lo que entrega.

El formato del mensaje de cada ejecución está en la especificación de cada agente.

## Cómo preparar las fuentes para A1

1. Cada fuente se convierte a texto plano y cada línea empieza con su marca de ubicación: `[p. 3]` en documentos y `[min 12:40]` en transcripciones.
2. En las transcripciones, cada intervención indica quién habla y si es del cliente o del equipo: `[min 12:40] Arquitecto (cliente): ...`.
3. El tipo de la fuente depende de quién la escribió. `documento_cliente`, `historias_usuario`, `correo` y `otro` son solo para material del cliente. Todo lo que escribe el equipo se entrega como `notas_internas`.
4. Cada sesión se entrega como una sola fuente.
5. **Después de cada sesión, enviar un acta al cliente y pedirle que la confirme por correo.** Lo que el cliente solo dice en una sesión vale como máximo 1 en la evaluación de la información, porque es verbal. Su correo de confirmación es una fuente escrita del cliente: permite subir esos datos a 2, y a 3 si confirma explícitamente el dato. El acta la escribe el equipo, así que va como `notas_internas`; la respuesta del cliente va como `correo`.

Los archivos de `pruebas/fuentes/` muestran el formato.

## Cómo verificar lo que entregan los agentes

Requisitos: Python 3.10 o superior y los paquetes `jsonschema` y `python-docx` (`pip install jsonschema python-docx`). Los comandos se ejecutan desde la carpeta `agentes/`.

**Ficha de A1.** Se le pasan la ficha nueva, la ficha vigente (si existe) y el texto de cada fuente nueva:

```
python verificacion/revisar_ficha.py ficha_v2.json --vigente ficha_v1.json --fuente F2=transcripcion.txt
```

**Evaluación de A2.** Se le pasan la evaluación, la ficha que recibió el agente y los mismos parámetros:

```
python verificacion/revisar_evaluacion.py evaluacion.json ficha_v2.json --sesiones 1 --maximo 1
```

**Componentes de A3.** Se le pasan los componentes, la ficha que recibió el agente y el tipo de estimación; con la evaluación que recibió, revisa además la evidencia de cada separación (agrega `--carril-rapido` si la solicitud fue urgente):

```
python verificacion/revisar_componentes.py componentes.json ficha_v2.json --tipo formal --evaluacion evaluacion.json
```

**Fichas de componentes de A4.** Se le pasan la salida de A4, la ficha, los componentes de A3, el catálogo y el mapa:

```
python verificacion/revisar_detalle.py detalle.json ficha_v2.json componentes.json --catalogo datos/catalogo_activos.json --mapa datos/mapa_tecnologias.json
```

**Juicios de A5.** Se le pasan la salida de A5, la salida de A4, la preparación y los mismos parámetros que recibió el agente:

```
python verificacion/revisar_escenario.py juicio.json detalle.json preparacion.json --tipo formal --modalidad ninguna
```

**Textos de A6.** Se le pasan la salida de A6, la salida de A4, la salida de A5, la evaluación de A2 y los mismos parámetros de primer bloque y tipo de estimación que recibió el agente:

```
python verificacion/revisar_propuesta.py propuesta.json detalle.json juicio.json evaluacion.json --primer-bloque si --tipo formal
```

**Cierre de A7.** Se le pasan la salida de A7, la preparación del cierre, la salida de A4, la propuesta enviada, el catálogo y las notas de cierre:

```
python verificacion/revisar_cierre.py cierre.json preparacion_cierre.json detalle.json --propuesta propuesta.json --catalogo datos/catalogo_activos.json --notas F3=notas_de_cierre.txt
```

Cada verificación lista los errores y los avisos. Una versión con errores no se marca como revisada: se corrige con una ejecución nueva del agente. Los avisos señalan lo que el Tech lead debe mirar con atención.

## Cómo calcular

Las funciones reciben los juicios de los agentes y devuelven los números con los valores del método vigentes:

```
python calculo/faed_calculos.py componentes detalle.json
python calculo/faed_calculos.py preparar detalle.json --registro datos/registro_proyectos.json
python calculo/faed_calculos.py escenario detalle.json juicio.json --registro datos/registro_proyectos.json --nivel-informacion media --experiencia-equipo 2
python calculo/faed_calculos.py estimar entrada.json
python calculo/faed_calculos.py cierre linea_base.json --jira horas.csv --cambios cambios.json
python calculo/faed_calculos.py desviacion cierre.json
python calculo/faed_calculos.py indicadores datos/registro_proyectos.json --catalogo datos/catalogo_activos.json
```

- `componentes` calcula las horas de cada componente a partir de la salida de A4.
- `preparar` arma lo que recibe A5: talla y arquetipos del proyecto, candidatos a comparables y horas de cada proceso.
- `escenario` calcula experiencia, confianza, rango, precios y ruta con los juicios de A5. La experiencia del equipo (0 a 3) la indica el Tech lead; opcionalmente se agregan `--modalidad`, `--cliente-estrategico` e `--infraestructura`.
- `estimar` calcula lo mismo desde componentes ya clasificados.
- `cierre` arma lo que recibe A7: suma las horas de la exportación de Jira por componente y las compara con la línea base, ajustada por los cambios de alcance.
- `desviacion` calcula la desviación desde horas ya consolidadas.
- `indicadores` calcula la desviación promedio, el porcentaje de proyectos dentro del rango, el reúso cumplido y si algún arquetipo activó el disparador de recalibración (componentes que se desvían en el mismo sentido en el número mínimo de proyectos).

`pruebas/caso_anexo_c.json` es un ejemplo completo de entrada para `estimar`: componentes, nivel de información, respuestas de experiencia y horas del primer bloque. Cada componente puede llegar con la complejidad y el reúso ya clasificados, o con los cinco factores de complejidad y el número de procesos reutilizados, y en ese caso la función calcula los niveles.

## Cómo armar la propuesta

Con los textos de A6 verificados y el escenario validado, la función arma el documento en la plantilla:

```
python armado/llenar_propuesta.py propuesta.json escenario.json juicio.json detalle.json --cliente "Nombre del cliente" -o propuesta.docx
```

`escenario.json` es la salida de `faed_calculos.py escenario`. La función presenta la inversión según la confianza, quita las instrucciones de la plantilla y lista los pendientes: lo que queda entre corchetes y las decisiones que no tomó. Las demás opciones están en la especificación de A6.

## Cómo registrar un cierre

Cuando el líder del proyecto confirma la salida de A7, la función la registra y escribe versiones nuevas del registro de proyectos y del catálogo de activos:

```
python registro/registrar_cierre.py cierre_confirmado.json preparacion_cierre.json linea_base.json detalle.json --registro datos/registro_proyectos.json --catalogo datos/catalogo_activos.json --nombre "Nombre del proyecto" --cliente "Cliente" --duracion 5 --salida-registro registro_v2.json --salida-catalogo catalogo_v2.json
```

No registra un cierre con reúsos sin confirmar o causas por confirmar. El recorrido completo del cierre está en la especificación de A7.

## Datos de la empresa

`datos/catalogo_activos.json`, `datos/mapa_tecnologias.json` y `datos/registro_proyectos.json` vienen en blanco, con la descripción de cada campo en `_formato`. Los llena el dueño del framework: el catálogo con los activos que identifique el equipo y con los activos nuevos de cada cierre, el mapa con las tecnologías que conoce la empresa y el registro con los proyectos que se reconstruyan con la dirección y con cada proyecto cerrado. Sin proyectos en el registro, la experiencia es baja y las cotizaciones siguen la ruta compleja. `pruebas/` tiene un ejemplo de cada uno.

## Valores del método

`calculo/valores_metodo.json` contiene los valores iniciales e ilustrativos del documento del framework, con su versión. El costo por hora y el margen objetivo son los del caso del anexo C, solo para que el cálculo funcione; los define la empresa. El margen de casi empate entre arquetipos (5 puntos porcentuales) y el número mínimo de proyectos para el disparador de recalibración (3, como en el ejemplo del anexo C) también son iniciales. Los umbrales de la ruta compleja, el margen mínimo, el recargo de infraestructura y las semanas por sprint están vacíos hasta que la empresa los defina. Mientras falten los umbrales, la ruta estándar es provisional y la dirección la confirma; mientras falten las semanas por sprint, la duración queda como pendiente en la propuesta.

Cuando la dirección aprueba valores nuevos, se crea una versión nueva del archivo; el código no cambia. Cada estimación registra con qué versión se calculó.

## Pruebas

`pruebas/probar_paquete.py` verifica los ejemplos de A1 a A7, arma la propuesta del ejemplo, registra su cierre, comprueba que las verificaciones detecten errores sembrados y reproduce con las funciones de cálculo todas las cifras del caso del anexo C:

```
python pruebas/probar_paquete.py
```

La carpeta `pruebas/` debe quedar fuera del contexto al que tiene acceso el agente. Si el agente lee los casos de ejemplo, copia sus datos y las pruebas dejan de medir algo.

## Mantenimiento

- Las instrucciones y los esquemas cambian solo con una versión nueva (v0.2, v0.3…), para poder comparar resultados entre versiones. Los cambios se coordinan para mantener una sola fuente de cada archivo.
- Antes de usar una versión nueva de las instrucciones, se corre `probar_paquete.py` y se prueba el agente con los casos de ejemplo.
