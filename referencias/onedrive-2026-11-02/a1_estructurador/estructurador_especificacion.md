# A1 · Estructurar · Especificación (v0.1)

Especificación independiente de la herramienta. Describe qué hace el agente, qué recibe, qué entrega y cómo se revisa su resultado; cada equipo lo implementa con la herramienta que elija.

Este documento es para quien construye y opera el agente. No se carga en el agente: el agente recibe sus instrucciones (`estructurador_instrucciones.md`), el esquema de salida (`faed_ficha.schema.json`) y, en cada ejecución, las fuentes nuevas y la ficha vigente.

## 1. Propósito y límites

**Propósito.** Convertir lo que comparte el cliente, y lo que se obtiene en las sesiones, en una ficha estructurada y con evidencia, que sirva de insumo a la evaluación de la información (anexo B.1 del documento del framework) y a la clasificación de componentes.

**Lugar en el recorrido.** Paso 3, realizar la sesión y evaluar. Procesa la solicitud inicial, lo que permite preparar la sesión con los vacíos detectados, y luego cada transcripción o fuente adicional, que enriquece la ficha.

**Qué lo dispara.** Llegan una o varias fuentes nuevas de una solicitud registrada: documentos del cliente, historias de usuario, correos, transcripciones de sesiones o notas internas del equipo.

**Qué hace.** Extrae la información relevante con cita literal, registra quién afirma cada dato, complementa los datos existentes sin borrar nada, registra las contradicciones y entrega la ficha completa en una versión nueva, con la lista de cambios.

**Lo que no hace.** No califica la información, no decide si alcanza para estimar, no propone componentes, horas ni precios, no recomienda tecnologías y no resuelve contradicciones por su cuenta: solo aplica las decisiones que una persona deja registradas en una nota interna.

## 2. Recorrido de una ejecución

1. **Preparar las fuentes.** Cada fuente nueva se convierte a texto con sus marcas de ubicación, como indica la guía del paquete.
2. **Estructurar.** A1 recibe las fuentes nuevas y la ficha vigente, y entrega la ficha en una versión nueva con la lista de cambios.
3. **Verificar.** `verificacion/revisar_ficha.py` comprueba que cada cita aparezca literal en su fuente y que nada de la versión vigente se pierda.
4. **Revisar.** El Tech lead revisa la versión y la marca como revisada. Con eso, A2 puede evaluarla.

## 3. Entradas y salida

**Entradas de cada ejecución.**

| Entrada | Descripción |
|---|---|
| Solicitud | Identificador de la solicitud y cliente registrado. |
| Ficha vigente | Última versión revisada de la ficha, o "ninguna" si es la primera. |
| Fuentes nuevas | Una o varias, cada una con su tipo (`documento_cliente`, `historias_usuario`, `correo`, `transcripcion_sesion`, `notas_internas` u `otro`), nombre y fecha. |

**Tipo de fuente según quién la escribe.** Los tipos `documento_cliente`, `historias_usuario`, `correo` y `otro` son solo para material escrito por el cliente. Todo lo que escribe el equipo, incluidas las historias de usuario que redacta y los correos internos, se entrega como `notas_internas`. El tipo define cuánto pesa cada dato en la evaluación de la información: un documento del equipo entregado como documento del cliente haría parecer documentado por el cliente algo que el cliente nunca escribió.

**Preparación de las fuentes.** Antes de entregarlas al agente, cada fuente se convierte a texto plano y cada línea empieza con su marca de ubicación: `[p. 3]` en documentos y `[min 12:40]` en transcripciones. Sin marcas, el agente no puede citar la ubicación.

**Requisito para las transcripciones.** Cada intervención indica quién habla y si es del cliente o del equipo, por ejemplo `[min 12:40] Arquitecto (cliente):`. Si la herramienta de transcripción no identifica a los hablantes, se etiquetan antes de entregar la transcripción al agente. Sin hablantes, el agente no puede distinguir un requisito del cliente de una propuesta del equipo y registra los datos como no identificados.

**Mensaje que recibe el agente.** Las instrucciones van como mensaje de sistema. Cada ejecución se entrega en un mensaje con esta forma:

```
<solicitud id="SOL-2026-0042" cliente="Nombre del cliente registrado" />
<ficha_vigente>
{ ...ficha vigente en JSON, o la palabra ninguna... }
</ficha_vigente>
<fuente tipo="transcripcion_sesion" nombre="Sesión de entendimiento 1" fecha="2026-10-09">
[marca de ubicación] Hablante (cliente o equipo): texto de la intervención
[marca de ubicación] Hablante (cliente o equipo): texto de la intervención
</fuente>
```

Si hay varias fuentes nuevas, se incluye una etiqueta `<fuente>` por cada una, en orden cronológico.

**Salida.** La ficha completa en su nueva versión, según `faed_ficha.schema.json`, con la lista de cambios frente a la ficha vigente.

**Cómo se usa el esquema.**

- Si la herramienta permite fijar la salida estructurada con un esquema JSON, se carga `faed_ficha.schema.json` en esa opción. Es la alternativa preferida: garantiza que la respuesta siempre se pueda leer y le entrega al modelo las definiciones de cada campo.
- Si no lo permite, se agrega el contenido del esquema al final de las instrucciones, bajo el título "Esquema de salida".
- El esquema es compatible con el modo estricto de salida estructurada: todos los campos son obligatorios, los vacíos son explícitos y no usa restricciones que ese modo no admite en todos los proveedores. Las reglas que por eso no expresa, como que todo dato tenga al menos una cita o que una contradicción nombre al menos dos datos, se comprueban en la revisión de cada versión. Si el proveedor elegido admite esas restricciones, pueden agregarse al esquema.

## 4. Versiones, decisiones y revisión

**Versiones.** Cada salida del agente se guarda como un archivo nuevo, con su número de versión (por ejemplo, `SOL-2026-0042_ficha_v2.json`), y nunca se sobrescribe un archivo anterior. El contenido de una versión no se modifica: cualquier corrección o dato nuevo genera la versión siguiente.

**Contenido y estado de revisión.** Cada versión tiene dos partes: su contenido, que no cambia, y su estado de revisión (pendiente o revisada, con responsable y fecha), que se registra después, por ejemplo en el nombre de la carpeta o en un registro aparte. **Los demás agentes solo usan la última versión revisada.**

**Decisiones de una persona.** Las correcciones y las decisiones sobre contradicciones entran como una fuente de tipo `notas_internas`. Solo el responsable de la estimación agrega fuentes de ese tipo, y cada nota indica su autor; la herramienta que se use debe impedir que otra persona o proceso las agregue. Por ejemplo: "Responsable de la estimación: se confirma con el cliente que el plazo es de cuatro meses; se descarta el plazo de seis meses (PLZ-01)." El agente aplica la decisión en la versión siguiente: marca como descartados los datos que la decisión descarta, sin eliminarlos, y deja la contradicción resuelta con la decisión y la nota que la contiene.

**Quién afirma cada dato.** Solo los datos afirmados por el cliente son requisitos. Los del equipo pueden ser propuestas o conocimiento interno, como un activo reutilizable o lo que el equipo sabe del entorno del cliente; son insumo de la estimación, pero no requisitos. Para la evaluación de la información, un dato del cliente en una fuente escrita del cliente cuenta como documentado; uno dicho en una sesión o relatado en una nota interna cuenta como mencionado, salvo que el cliente lo haya validado explícitamente. La validación cuenta solo si su cita viene del cliente: una nota interna que dice "el cliente confirmó" no basta, así que una confirmación telefónica se le pide al cliente por escrito.

## 5. Revisión de cada versión

El responsable de la estimación revisa cada versión antes de marcarla como revisada. La revisión comprueba:

1. **Estructura.** La salida cumple el esquema.
2. **Conservación.** Están todos los datos y contradicciones de la versión anterior, con sus mismos identificadores; nada desapareció.
3. **Citas.** Cada cita aparece literal en la fuente y en la ubicación indicada.
4. **Fidelidad.** Cada enunciado y cada atributo dicen lo mismo que su cita: ni más, ni distinto.
5. **Nada inventado.** No hay datos sin respaldo en las fuentes.
6. **Origen.** Las propuestas y el conocimiento del equipo no quedaron registrados como afirmaciones del cliente, y cada dato marcado como no identificado se revisó uno por uno.
7. **Contradicciones.** Los conflictos entre fuentes quedaron registrados, con todos los datos involucrados, y ninguno se resolvió sin una decisión registrada.
8. **Cambios.** La lista de cambios coincide con lo que realmente cambió frente a la versión anterior.

Los puntos 1, 2, 3 y 8 se pueden automatizar con un script que compare la versión nueva con la anterior y con el texto de las fuentes. Los puntos 4 a 7 requieren criterio humano; para el punto 7, la revisión puede apoyarse en una comparación automática de los enunciados de cada sección que señale los pares parecidos.

## 6. Parámetros y buenas prácticas

- Fijar el modelo y su versión, usar la temperatura más baja que permita la herramienta y registrar en cada ejecución la versión de las instrucciones y del esquema. Así, un cambio en los resultados siempre se puede explicar.
- Entregar al agente la ficha vigente completa en cada ejecución: sin ella no puede conservar lo anterior ni detectar contradicciones.
- Vigilar el tamaño de la salida. La ficha completa crece con cada fuente; si se acerca al límite de salida del modelo, la respuesta llega cortada y no es un JSON válido. Citar solo el fragmento mínimo reduce el volumen. Si aun así se acerca al límite, el agente pasa a entregar solo los cambios de cada ejecución y estos se fusionan con la ficha vigente fuera del modelo.
- Mantener los casos de ejemplo y de prueba, con sus resultados esperados, fuera de la carpeta o del contexto al que tiene acceso el agente. Si el agente los lee, copia sus datos y las pruebas dejan de medir algo.
- Ajustar las instrucciones solo en `estructurador_instrucciones.md`, con una versión nueva (v0.2, v0.3…), para poder comparar resultados entre versiones.
