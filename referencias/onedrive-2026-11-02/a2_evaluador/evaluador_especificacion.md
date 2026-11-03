# A2 · Evaluar la información · Especificación (v0.1)

Especificación independiente de la herramienta. Describe qué hace el agente, qué recibe, qué entrega y cómo se revisa su resultado; cada equipo lo implementa con la herramienta que elija.

Este documento es para quien construye y opera el agente. No se carga en el agente: el agente recibe sus instrucciones (`evaluador_instrucciones.md`), que ya incluyen la rúbrica del anexo B.1 y las definiciones del anexo A que necesita (arquetipos y factores de complejidad), el esquema de salida (`faed_evaluacion.schema.json`) y, en cada ejecución, la solicitud, los parámetros y la ficha.

## 1. Propósito y límites

**Propósito.** Determinar qué tan completa es la información de una solicitud para estimarla, con la evaluación de la información del anexo B.1 del documento del framework, y convertir ese resultado en acciones: qué falta, qué preguntar y qué tendría que suponer la estimación.

**Lugar en el recorrido.** Paso 3, realizar la sesión y evaluar. El agente evalúa en dos momentos, que deduce del número de sesiones realizadas que recibe:

| Momento | Cuándo | Para qué sirve |
|---|---|---|
| `preparacion` | Aún no se ha hecho ninguna sesión de entendimiento. | El nivel es informativo. Las preguntas preparan la sesión de entendimiento. |
| `despues_de_sesion` | Ya se hizo al menos una sesión. | El nivel sustenta la decisión de seguir a la clasificación de componentes, hacer una sesión adicional o entregar un rango preliminar con fase de definición. |

**Qué lo dispara.** Una versión nueva de la ficha queda marcada como revisada.

**Qué entrega.**

1. **El nivel de información**, con el cálculo completo: puntaje de los 20 criterios, porcentaje de las 9 dimensiones, porcentaje general, nivel y tope.
2. **Lo que falta**: para cada criterio por debajo de 3, qué se necesita para llegar al puntaje siguiente.
3. **Las preguntas**, ordenadas por prioridad: como máximo diez para el cliente, las del equipo aparte y una por cada contradicción abierta.
4. **Los supuestos** que tendría que asumir la estimación por cada criterio con puntaje 0 o 1.

Además sugiere el siguiente paso y registra advertencias.

**Lo que no hace.** No modifica la ficha ni le agrega datos, no estima horas, no clasifica componentes, no evalúa la experiencia de la empresa (dimensiones D9 y D11) y no decide: el nivel y el siguiente paso los confirma el responsable de la estimación.

## 2. Recorrido de una ejecución

1. **Evaluar.** Cuando una versión de la ficha queda revisada, A2 la recibe con el número de sesiones realizadas y el máximo de sesiones adicionales, y entrega la evaluación.
2. **Verificar.** `verificacion/revisar_evaluacion.py` recalcula toda la aritmética, el techo de cada puntaje y el orden de las preguntas.
3. **Confirmar.** El Tech lead confirma el nivel de información y el siguiente paso: otra sesión, estimar o entregar un rango preliminar.

## 3. Entradas y salida

**Entradas de cada ejecución.**

| Entrada | Descripción |
|---|---|
| Solicitud | Identificador de la solicitud y cliente registrado. |
| Sesiones realizadas | Número de sesiones de entendimiento que ya se hicieron con el cliente, tengan o no transcripción. Lo registra quien opera el agente: el agente no lo deduce de las fuentes, porque una sesión puede no grabarse o quedar en varios archivos. |
| Máximo de sesiones adicionales | Número de sesiones adicionales que la empresa permite antes de entregar un rango preliminar. Es una política comercial: lo define la empresa y es el mismo para todas las solicitudes, salvo una decisión explícita del responsable. |
| Ficha | Última versión revisada de la ficha de la solicitud, completa. Nunca una versión pendiente de revisión. |

**Mensaje que recibe el agente.** Las instrucciones van como mensaje de sistema. Cada ejecución se entrega en un mensaje con esta forma:

```
<solicitud id="SOL-2026-0042" cliente="Nombre del cliente registrado" />
<parametros sesiones_realizadas="1" maximo_sesiones_adicionales="1" />
<ficha>
{ ...última versión revisada de la ficha, en JSON... }
</ficha>
```

**Salida.** La evaluación según `faed_evaluacion.schema.json`.

**Cómo se usa el esquema.**

- Si la herramienta permite fijar la salida estructurada con un esquema JSON, se carga `faed_evaluacion.schema.json` en esa opción. Es la alternativa preferida: garantiza que la respuesta siempre se pueda leer y le entrega al modelo las definiciones de cada campo.
- Si no lo permite, se agrega el contenido del esquema al final de las instrucciones, bajo el título "Esquema de salida".
- El esquema es compatible con el modo estricto de salida estructurada. Las reglas que por eso no expresa, como que estén los 20 criterios en orden o que las preguntas para el cliente sean como máximo diez, se comprueban en la revisión de cada evaluación.

## 4. Reglas que conviene conocer

Las reglas completas están en las instrucciones. Estas son las que más afectan el resultado y las que el responsable debe tener presentes al revisarlo.

**Techo por evidencia.** El puntaje de un criterio no depende solo de cuánta información hay, sino de qué tan firme es. Por eso la ficha registra quién afirma cada dato, el medio de cada fuente y si el cliente confirmó el dato.

| Evidencia del dato | Puntaje máximo |
|---|---|
| Afirmado por el equipo o por alguien no identificado, sin confirmación del cliente | 1 |
| Afirmado por el cliente en una sesión, o relatado en una nota interna | 1 |
| Afirmado por el cliente en una fuente escrita del cliente (documento, historias de usuario, correo u otro) | 2 |
| Confirmado explícitamente por el cliente, con la cita de la validación en una fuente escrita del cliente o en una intervención del cliente en una sesión | 3 |

Si un puntaje necesita varios datos, el techo lo pone el más débil. La consecuencia práctica: lo que el cliente solo dijo en la sesión sube de 1 a 2 cuando lo envía por escrito, y a 3 cuando lo valida. Muchas preguntas útiles son pedidos de documentar o validar algo que ya se conversó.

Dos precisiones. Una confirmación que solo aparece en una nota interna ("el cliente confirmó") no cuenta: si el cliente confirma por teléfono, se le pide que lo confirme por escrito. Y D6.1 es la excepción al techo: mide lo que la empresa sabe de sus propios activos, que por naturaleza viene del equipo, así que se califica directamente con su descriptor.

El techo depende de que el tipo de cada fuente diga quién la escribió. Por eso, según la especificación del estructurador, todo lo que escribe el equipo se entrega como `notas_internas`, aunque sean historias de usuario o correos.

**Cálculo.** Cada criterio se califica de 0 a 3 y se multiplica por su peso (3, salvo D4.4, D5.3 y D6.1, que pesan 2). Cada dimensión obtiene un porcentaje, y el porcentaje general es el promedio de las dimensiones ponderado por sus pesos (D1 12, D2 11, D3 18, D4 15, D5 14, D6 5, D7 5, D8 7 y D10 3). Las dimensiones núcleo (D1 a D5) cuentan siempre. Las complementarias se excluyen solo si no aplican al proyecto; si aplican y no hay información, cuentan con 0.

**Nivel y tope.** Baja, menos de 40 %; media, de 40 % a menos de 67 %; alta, 67 % o más. Si alguna dimensión núcleo queda por debajo de 40 %, el nivel no puede ser alto y pasa a medio. El corte de 67 % es intencional: con todos los criterios en 2 el resultado es 66,7 %, media, porque sin información validada por el cliente no hay nivel alto.

**Siguiente paso sugerido.**

| Momento | Nivel | Sesiones adicionales realizadas | Siguiente paso |
|---|---|---|---|
| `preparacion` | Cualquiera | No aplica | `realizar_sesion` |
| `despues_de_sesion` | Media o alta | No aplica | `clasificar_componentes` |
| `despues_de_sesion` | Baja | Menos que el máximo | `sesion_adicional` |
| `despues_de_sesion` | Baja | Igual al máximo | `rango_preliminar_y_fase_de_definicion` |

El momento es `preparacion` cuando las sesiones realizadas son 0, y `despues_de_sesion` en otro caso. Las sesiones adicionales realizadas son las sesiones realizadas menos la primera.

**Prioridad de las preguntas.** La prioridad de cada criterio por debajo de 3 es cuántos puntos subiría el porcentaje general si ese criterio llegara a 3: (3 − puntaje) × peso del criterio ÷ puntos posibles de su dimensión × peso de la dimensión ÷ suma de los pesos de las dimensiones que cuentan × 100. Así las preguntas siguen los mismos pesos con los que se calcula el nivel. En empate va primero el criterio núcleo, y si el tope está aplicado van primero las dimensiones núcleo por debajo de 40 %, porque mientras alguna lo esté el nivel no puede ser alto, por mucho que suba el porcentaje.

Un efecto de los pesos del anexo B.1 que conviene conocer: un criterio que es el único de su dimensión concentra todo el peso de la dimensión. D8.1 vale hasta 7,8 puntos del porcentaje general, más que cualquier criterio núcleo (los de D3 valen 6,7 cada uno), así que con frecuencia encabeza las preguntas.

## 5. Archivos, decisiones y uso de la evaluación

**Archivos.** Cada evaluación se guarda como un archivo nuevo ligado a la versión de la ficha que evaluó (por ejemplo, `SOL-2026-0042_evaluacion_ficha_v2.json`) y nunca se sobrescribe. Si se repite la evaluación sobre la misma versión, por ejemplo después de ajustar las instrucciones, se guarda con un sufijo de ejecución (`_r2`) y se registra la versión de las instrucciones usada.

**Decisión del responsable.** El responsable de la estimación revisa la evaluación y confirma o ajusta el nivel y el siguiente paso. La decisión se registra aparte, con responsable, fecha y, si ajusta un puntaje o el nivel, el motivo. El archivo de la evaluación no se modifica: así queda la diferencia entre lo que sugirió el agente y lo que decidió la persona, que es la información más útil para mejorar las instrucciones.

**Preguntas.** El responsable elige las preguntas que se usan, las ajusta si hace falta y las lleva a la guía de la sesión o a un correo al cliente. Las respuestas vuelven como fuentes nuevas al agente estructurador, que genera la versión siguiente de la ficha; esa versión, una vez revisada, se evalúa de nuevo.

**Contradicciones pendientes.** Se resuelven con una nota interna del responsable, que el agente estructurador aplica en la versión siguiente de la ficha. Conviene resolverlas antes de clasificar componentes.

**Supuestos.** Los supuestos de la última evaluación, con los ajustes del responsable, son insumo de los supuestos de la propuesta. Cada supuesto que el cliente confirme o corrija entra como fuente nueva y mejora la ficha.

## 6. Revisión de cada evaluación

El responsable de la estimación revisa cada evaluación antes de usarla. La revisión comprueba:

1. **Estructura.** La salida cumple el esquema, con los 20 criterios y las 9 dimensiones en orden, y corresponde a la solicitud y a la versión de la ficha entregadas.
2. **Evidencia.** Cada identificador citado existe en la ficha y está vigente, y ningún criterio con puntaje mayor que 0 carece de evidencia.
3. **Techo.** Ningún puntaje supera el techo que permite su evidencia.
4. **Aritmética.** Los puntos, los porcentajes de cada dimensión, el porcentaje general, el nivel y el tope coinciden con las reglas de cálculo.
5. **Siguiente paso.** Es coherente con las sesiones realizadas, el nivel y el máximo de sesiones adicionales.
6. **Preguntas: forma.** La prioridad de cada una está bien calculada, el orden es de mayor a menor, hay como máximo diez para el cliente y ninguna incluye códigos de FAED.
7. **Cobertura.** Hay un supuesto por cada criterio con puntaje 0 o 1 en una dimensión que cuenta y una pregunta por cada contradicción abierta de la ficha.
8. **Puntajes.** El descriptor elegido corresponde a los datos y, cuando el puntaje depende de varios datos, el techo lo puso el más débil. Ningún 3 se apoya en una confirmación que solo aparece en una nota interna. Las dimensiones excluidas realmente no aplican al proyecto.
9. **Preguntas: contenido.** Cada pregunta es concreta para el proyecto, está en el lenguaje del cliente, trata un solo tema y no pide algo que la ficha ya responde.
10. **Supuestos.** Cada supuesto es una condición que el cliente puede confirmar o corregir, sin cifras ni datos que no estén en la ficha.

Los puntos 1 a 7 se pueden automatizar con un script que recalcule la evaluación a partir de la ficha; la revisión del techo automatizada es una cota: detecta un puntaje por encima de la evidencia más fuerte, y el punto 8 completa la comprobación. Los puntos 8 a 10 requieren criterio humano.

## 7. Parámetros y buenas prácticas

- Fijar el modelo y su versión, usar la temperatura más baja que permita la herramienta y registrar en cada ejecución la versión de las instrucciones y del esquema.
- Recalcular siempre la aritmética fuera del modelo. El agente muestra todos los números para que se puedan verificar, pero un modelo de lenguaje puede equivocarse en una suma; si el recálculo no coincide, prevalece el recálculo y la diferencia se registra.
- Medir la estabilidad: de vez en cuando, evaluar dos veces la misma ficha y comparar. Si un mismo criterio cambia de puntaje entre ejecuciones, su descriptor es ambiguo y conviene precisarlo en la rúbrica.
- Mantener la rúbrica alineada con el documento del framework. Si cambia el anexo B.1, se actualizan las instrucciones y el esquema a la vez, con una versión nueva de ambos.
- Mantener los casos de ejemplo y de prueba, con sus resultados esperados, fuera de la carpeta o del contexto al que tiene acceso el agente. Si el agente los lee, imita sus puntajes y las pruebas dejan de medir algo.
- Ajustar las instrucciones solo en `evaluador_instrucciones.md`, con una versión nueva (v0.2, v0.3…), para poder comparar resultados entre versiones.
