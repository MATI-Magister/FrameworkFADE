# Solución con agentes de FAED · Diseño del flujo (v0.1)

Este documento describe cómo la solución con agentes ejecuta el recorrido de una cotización de FAED, desde la solicitud del cliente hasta el cierre del proyecto ejecutado: qué hace cada agente, qué recibe y qué entrega, qué datos consulta, qué calcula sin inteligencia artificial y dónde decide una persona. Complementa el documento del framework y es independiente de la herramienta con la que se implemente.

**Para quién es.** Para todo el equipo: dirección, Tech leads, Gerencia de Proyectos y evaluadores. No requiere conocimientos de programación. Los términos del método se explican en el glosario de la sección 6; la operación técnica (comandos y archivos) está en `LEEME.md`.

## 1. Principios

- **La inteligencia artificial sugiere; las personas deciden.** Ningún agente aprueba, envía ni registra un resultado definitivo. Cada salida que afecta la estimación pasa por un control humano.
- **Los agentes juzgan; las funciones calculan.** Los agentes interpretan la información y aplican reglas. Los porcentajes, niveles, horas, rangos y precios los calculan funciones de código con los valores del método, para que cada número sea reproducible y auditable.
- **Todo con evidencia.** Cada dato tiene su fuente, cada puntaje su justificación y cada propuesta de un agente cita aquello en que se apoya.
- **Nada se pierde.** Las salidas se guardan como versiones y no se sobrescriben. Las correcciones crean una versión nueva.
- **Ante la duda, lo conservador.** Cuando la evidencia no alcanza, los agentes eligen la opción que no sobreestima: el puntaje menor, sin reúso, experiencia baja.

## 2. El proceso

![Proceso con agentes de FAED](diagramas/FAED_Proceso_Agentes_BPMN.png)

*Archivo editable: `diagramas/FAED_Proceso_Agentes_BPMN.drawio`.*

El proceso se divide en tres bandas unidas por eventos de enlace:

1. **Entrada e información suficiente.** El cliente envía la solicitud, el primer contacto la registra y el Tech lead evalúa su viabilidad. Si la solicitud es urgente, pasa por el carril rápido a la estimación. Si no, A1 estructura la información en la ficha del requerimiento y A2 evalúa su nivel de información. Mientras la información no alcance y queden sesiones disponibles, el Tech lead hace la sesión de entendimiento con las preguntas de A2, y la transcripción vuelve a A1, que crea una versión nueva de la ficha.
2. **Estimación.** A3 divide el proyecto en componentes, A4 detalla cada uno y las funciones calculan el reúso, la complejidad y las horas. A5 confirma los proyectos comparables y propone el primer bloque, y las funciones arman el escenario con su confianza y su precio. El validador o la dirección valida, según la ruta. Un rango preliminar no es una propuesta formal: lo revisa el validador y las señales de la ruta compleja se evalúan al emitir la propuesta formal. Mientras la empresa no defina los umbrales de valor y esfuerzo, la ruta estándar es provisional y la dirección la confirma.
3. **Propuesta y cierre.** A6 redacta los textos de la propuesta, la función la arma en la plantilla con las cifras del escenario y la Gerencia de Proyectos la revisa y la envía. Si el proyecto se gana y se ejecuta, al cerrarse en Jira la función compara las horas reales con la línea base, A7 prepara el cierre, el líder del proyecto lo confirma y la función lo registra en el registro de proyectos y en el catálogo de activos. Si el proyecto quedó fuera del rango estimado, se hace además la revisión de cierre.

## 3. Los agentes

| Agente | Qué hace | Control humano |
|---|---|---|
| A1 · Estructurar | Convierte la información del cliente en la ficha del requerimiento | El Tech lead revisa cada versión |
| A2 · Evaluar la información | Califica la información y dice qué falta | El Tech lead confirma el nivel de información |
| A3 · Dividir | Divide el proyecto en componentes | Se revisa en la validación |
| A4 · Detallar | Completa la ficha de cada componente | El Tech lead confirma el reúso de 30 % o más |
| A5 · Generar escenario | Busca comparables y arma el escenario | El validador o la dirección valida |
| A6 · Redactar propuesta | Llena la plantilla de propuesta | La Gerencia de Proyectos revisa y envía |
| A7 · Cerrar y aprender | Prepara el cierre del proyecto ejecutado | El líder del proyecto confirma |

### A1 · Estructurar

*Convierte lo que envía el cliente y lo que se dice en las sesiones en la ficha del requerimiento, sin interpretar.*

| | |
|---|---|
| **Entra** | Solicitud, transcripciones y notas internas; ficha vigente |
| **Sale** | Ficha versionada: cada dato con su cita, quién lo afirma y contradicciones; lista de cambios |
| **Consulta** | Registro único |
| **Llama a la función** | Ninguna. Su salida pasa por la verificación de la ficha |
| **Control humano** | El Tech lead revisa cada versión de la ficha |

**Reglas clave**
- Sin cita exacta de la fuente, el dato no entra.
- Una propuesta del equipo no es un requisito del cliente.
- Nada se borra; solo una persona descarta datos o resuelve contradicciones.

Archivos: carpeta `a1_estructurador/`.

### A2 · Evaluar la información

*Califica 20 criterios de 0 a 3 y dice qué falta para estimar con confianza.*

| | |
|---|---|
| **Entra** | Ficha revisada; sesiones realizadas y máximo permitido |
| **Sale** | Nivel de información, brechas, hasta 10 preguntas, supuestos y siguiente paso sugerido |
| **Consulta** | Solo la ficha |
| **Llama a la función** | Ninguna. Su salida pasa por la verificación de la evaluación |
| **Control humano** | El Tech lead confirma el nivel de información |

**Reglas clave**
- Lo que el cliente solo dijo vale máximo 1; lo que escribió, 2; lo que validó, 3.
- Ante la duda, el puntaje menor.
- Las preguntas se ordenan por cuánto subirían el nivel.

Archivos: carpeta `a2_evaluador/`.

### A3 · Dividir

*Divide el proyecto en componentes que se pueden construir y probar por separado.*

| | |
|---|---|
| **Entra** | Ficha con información suficiente, o preliminar, y su evaluación (en el carril rápido puede faltar) |
| **Sale** | Componentes de un solo arquetipo, cada uno con sus procesos funcionales, de la ficha o inferidos, y los criterios de división que lo originaron; talla probable de los candidatos si la información es baja; interfaces sin componente; supuestos |
| **Consulta** | La ficha y la evaluación; los arquetipos y los criterios de división están en sus instrucciones |
| **Llama a la función** | Ninguna. Su salida pasa por la verificación de los componentes |
| **Control humano** | Se revisa en la validación del escenario |

**Reglas clave**
- Un arquetipo por componente.
- El nivel de información fija la profundidad: con información baja o en carril rápido, solo componentes candidatos con su talla probable; con media o alta, componentes completos.
- Forma los componentes con una clave fija por arquetipo y aplica las separaciones en orden (riesgo, una sola vez, regulación, tecnología, reúso, complejidad, conocimiento), solo si la evaluación tiene 2 o más en el criterio que las sustenta.
- Cada interfaz que requiere construir o adaptar un conector es un componente de integración; las que ya existen o construye otro quedan como dependencias, con su motivo.
- Un componente de talla XL se divide.
- Puede agregar procesos que la ficha no menciona si la solución los necesita; cada uno queda marcado como inferido, con su justificación y un supuesto.

Archivos: carpeta `a3_divisor/`.

### A4 · Detallar

*Completa la ficha de cada componente con lo que necesita el cálculo de horas.*

| | |
|---|---|
| **Entra** | Componentes con sus procesos; ficha del requerimiento; catálogo de activos; mapa de tecnologías |
| **Sale** | Ficha del componente: complejidad, integración, entorno, reúso proceso por proceso y supuestos |
| **Consulta** | Catálogo de activos y mapa de tecnologías |
| **Llama a la función** | Cálculo de reúso, complejidad, integración, entorno y horas |
| **Control humano** | El Tech lead confirma el reúso de 30 % o más y las tecnologías que no están en el mapa |

**Reglas clave**
- Solo se usan activos del catálogo en estado vigente.
- El reúso se marca proceso por proceso, citando el activo que lo cubre.
- Ante la duda, el proceso no se cuenta como reutilizado.
- Un factor de complejidad sin evidencia se califica con 1, con su supuesto y su vacío.
- La madurez de cada componente (Validado, Definido o Supuesto) la define su proceso más débil, con la escala de evidencia de A2. No cambia las horas.

Archivos: carpeta `a4_detallador/`.

### A5 · Generar escenario

*Confirma los proyectos comparables y propone el primer bloque; las funciones arman el escenario con su confianza y su precio.*

| | |
|---|---|
| **Entra** | Fichas de los componentes; ficha del requerimiento; preparación de la función: talla y arquetipos del proyecto, candidatos a comparables y horas de cada proceso |
| **Sale** | Juicio de cada candidato a comparable y propuesta del primer bloque. Con ellos, la función entrega experiencia, confianza, escenario optimista, esperado y pesimista, precios por modalidad y ruta |
| **Consulta** | Registro de proyectos, a través de la preparación |
| **Llama a la función** | Preparación; experiencia, confianza y rango; precio por modalidad; ruta |
| **Control humano** | El Tech lead indica la experiencia del equipo en proyectos similares; el validador o la dirección valida la estimación y el precio |

**Reglas clave**
- Son candidatos los proyectos ejecutados del mismo arquetipo principal, de talla igual o adyacente y con horas reales. Los selecciona la función.
- El agente solo cuenta los candidatos cuyo trabajo se parece; ante la duda, no cuentan y el Tech lead resuelve.
- Si otro arquetipo queda en casi empate con el principal, sus proyectos también son candidatos.
- Con cero o un proyecto comparable, la experiencia es baja.
- La confianza es el menor entre el nivel de información y la experiencia.
- No propone bloque si la estimación es preliminar, si el cliente pidió otra modalidad o si el proyecto cabe en un bloque.
- El bloque es una funcionalidad que el cliente puede usar, con lo que necesita para funcionar, de 320 a 480 horas.

Archivos: carpeta `a5_generador/`.

### A6 · Redactar propuesta

*Redacta los textos de la propuesta; la función los pone en la plantilla con las cifras del escenario validado.*

| | |
|---|---|
| **Entra** | Ficha, evaluación, componentes, fichas de los componentes, juicios del escenario y la confianza validada |
| **Sale** | Textos de cada sección: nombre del proyecto, contexto, solución, incluye y no incluye, supuestos, información por pedir y objetivo del bloque o primer entregable |
| **Consulta** | Nada más: la plantilla la usa la función |
| **Llama a la función** | Armado de la propuesta, que agrega horas, precios por modalidad, bloque y duración |
| **Control humano** | La Gerencia de Proyectos completa los pendientes, revisa y envía |

**Reglas clave**
- No recibe cifras y no escribe ninguna: las pone la función desde el escenario validado.
- No inventa: si falta información, lo registra en las advertencias en lugar de completarla.
- Escribe en el lenguaje del cliente, sin códigos ni términos del método.
- Un dato en contradicción abierta se presenta como supuesto, no como hecho.
- La función presenta la inversión según la confianza: cifra única, rango o rango preliminar sin modalidades.

Archivos: carpeta `a6_redactor/` y función `armado/llenar_propuesta.py`.

### A7 · Cerrar y aprender

*Prepara el cierre de cada proyecto ejecutado para que el método aprenda.*

| | |
|---|---|
| **Entra** | Preparación del cierre de la función: horas reales de Jira contra la línea base ajustada por cambios de alcance, desviaciones y si requiere revisión de cierre; fichas de los componentes; propuesta enviada; catálogo de activos; notas de cierre del equipo |
| **Sale** | Reúso real de cada activo usado, causa de cada desviación sobre el umbral, activos nuevos, insumos para la revisión de cierre, descripción del proyecto para el registro y preguntas para el líder |
| **Consulta** | Catálogo de activos; Jira, a través de la exportación de horas |
| **Llama a la función** | Preparación del cierre, antes; registro del cierre, después de la confirmación |
| **Control humano** | El líder del proyecto confirma; el dueño del framework marca la solicitud como cerrada |

**Reglas clave**
- Las horas se consolidan por épica: cada épica empieza por el código de su componente.
- Los cambios de alcance aprobados se suman a la línea base antes de calcular la desviación.
- Requiere causa toda desviación sobre el umbral, hacia arriba o hacia abajo, con una de cinco causas: alcance o información, complejidad, reúso, integración o equipo.
- Todo lo que confirma lleva una cita literal de las notas; lo que no, queda por confirmar con su pregunta para el líder.
- La función no registra un cierre con reúsos o causas sin confirmar.

Archivos: carpeta `a7_cierre/` y función `registro/registrar_cierre.py`.

## 4. Funciones de cálculo y datos

### Funciones

Las funciones son código, sin inteligencia artificial, y usan los valores del método vigentes (`calculo/valores_metodo.json`). Las de cálculo las llaman los agentes cuando necesitan un número; las de verificación se ejecutan sobre la salida de A1 y A2, antes de la revisión del Tech lead.

| Función | Cuándo | Qué calcula o comprueba | Archivo |
|---|---|---|---|
| Verificación de la ficha | Sobre cada versión que entrega A1 | Que cada cita aparezca literal en su fuente y en su ubicación, que nada se pierda entre versiones y que ningún descarte se haga sin una nota interna | `verificacion/revisar_ficha.py` |
| Verificación de los componentes | Sobre cada salida de A3 | Que cada proceso de la ficha quede en un solo componente, que los inferidos tengan justificación y supuesto, que interfaces y migraciones tengan componente o motivo, que ninguno sea XL y, con la evaluación, que cada separación tenga evidencia | `verificacion/revisar_componentes.py` |
| Verificación de la evaluación | Sobre cada evaluación que entrega A2 | Puntos, porcentajes, nivel, tope, techo por evidencia, prioridad y orden de las preguntas y siguiente paso | `verificacion/revisar_evaluacion.py` |
| Verificación de las fichas de componentes | Sobre cada salida de A4 | Correspondencia con A3, reúso en activos vigentes, factores sin evidencia en 1, niveles del mapa, madurez y confirmaciones requeridas | `verificacion/revisar_detalle.py` |
| Verificación de los juicios del escenario | Sobre cada salida de A5 | Un juicio por candidato y ninguno de más, bloque solo cuando corresponde y dentro del tamaño, funcionalidad sin códigos internos | `verificacion/revisar_escenario.py` |
| Verificación del cierre | Sobre cada salida de A7 | Un reúso por activo usado y una causa por componente desviado, citas literales en las notas, lo no sustentado por confirmar, activos nuevos fuera del catálogo y revisión de cierre solo fuera del rango | `verificacion/revisar_cierre.py` |
| Verificación de los textos de la propuesta | Sobre cada salida de A6 | Una descripción por componente, ninguna cifra, código ni término interno, bloque según el parámetro y supuestos, información y exclusiones cuando corresponden | `verificacion/revisar_propuesta.py` |
| Cálculo por componente | La llama A4 | Talla, porcentaje y nivel de reúso, suma y nivel de complejidad, nivel de integración, entorno y horas del componente | `calculo/faed_calculos.py` |
| Preparación del escenario | Antes de A5 | Talla y arquetipos del proyecto, candidatos a comparables con la calificación de sus datos y horas de cada proceso | `calculo/faed_calculos.py` |
| Experiencia, confianza y rango | La llama A5 | Participación de cada arquetipo, nivel de experiencia, confianza y escenario optimista, esperado y pesimista | `calculo/faed_calculos.py` |
| Precio por modalidad | La llama A5 | Precio por hora y precio en bolsa de horas, sprints, primer bloque y precio fijo | `calculo/faed_calculos.py` |
| Ruta | La llama A5 | Si la cotización sigue la ruta estándar o la compleja, con sus motivos y quién decide | `calculo/faed_calculos.py` |
| Armado de la propuesta | Después de A6 | Pone en la plantilla los textos de A6 y las cifras del escenario según la confianza, quita las instrucciones y lista los pendientes | `armado/llenar_propuesta.py` |
| Preparación del cierre | Antes de A7 | Horas reales por componente desde la exportación de Jira, desviación por componente y del proyecto después de sumar los cambios de alcance aprobados, componentes que requieren causa y si el proyecto cerró fuera del rango | `calculo/faed_calculos.py` |
| Registro del cierre | Después de la confirmación del líder | Agrega el proyecto al registro de proyectos, con sus horas reales, desviaciones y causas, y actualiza los usos y los activos nuevos del catálogo | `registro/registrar_cierre.py` |
| Indicadores y recalibración | Después de cada registro y en la revisión periódica | Desviación promedio, proyectos dentro del rango, reúso cumplido y si un arquetipo activó el disparador de recalibración | `calculo/faed_calculos.py` |

### Datos

| Dato | Qué contiene | Lo administra | Lo usan |
|---|---|---|---|
| Registro único | Solicitudes, versiones de fichas y estimaciones, estados y resultados | Dueño del framework | A1, A7 |
| Catálogo de arquetipos | Los seis arquetipos y las escalas de las dimensiones | Dueño del framework | A3, A4 |
| Catálogo de activos | Activos reutilizables, procesos que cubren, estado y usos (`datos/catalogo_activos.json`) | Dueño del framework | A4, A7 |
| Mapa de tecnologías | Tecnologías que conoce la empresa, con su nivel de T1 a T4 (`datos/mapa_tecnologias.json`) | Dueño del framework | A4, A5 |
| Valores del método | Horas por proceso de cada arquetipo, factores, descuentos de reúso, amplitudes, costos y márgenes, en versiones aprobadas | Dueño del framework y responsable de valores financieros | Funciones |
| Registro de proyectos | Proyectos reconstruidos y cerrados, con su arquetipo, componentes, procesos, horas reales, duración y equipo (`datos/registro_proyectos.json`) | Dueño del framework | A5, A7 |
| Plantilla de propuesta | Estructura y textos base de la propuesta (`datos/plantilla_propuesta.docx`) | Gerencia de Proyectos | Función de armado |
| Jira | Horas reales registradas por épica de cada componente, exportadas en CSV | Equipo del proyecto | Preparación del cierre |
| Notas de cierre | Lo que el equipo registra al cierre: reúso, causas de las desviaciones y lo que se puede volver a usar | Líder del proyecto | A7 |

## 5. Controles humanos

| Momento | Quién | Qué confirma | Por qué ahí |
|---|---|---|---|
| Viabilidad | Dirección | El descarte de una solicitud no viable | Rechazar a un cliente es una decisión comercial |
| Cada versión de la ficha | Tech lead | Que la ficha sea fiel a las fuentes | Todo lo que sigue se apoya en la ficha |
| Nivel de información | Tech lead | Si la información alcanza para estimar | Decide entre otra sesión, estimar o un rango preliminar |
| Reúso de 30 % o más | Tech lead | Que el reúso propuesto sea real | Un reúso alto baja mucho las horas |
| Tecnología fuera del mapa | Tech lead | El nivel de familiaridad del equipo | Cambia el factor de entorno y la experiencia |
| Validación | Validador o dirección | La estimación y el precio | Es lo último antes de comprometerse con el cliente |
| Envío de la propuesta | Gerencia de Proyectos | El borrador y su envío | La propuesta habla en nombre de la empresa |
| Cierre | Líder del proyecto | Reúso real, causas de las desviaciones y activos nuevos | Estos datos recalibran el método |
| Revisión de cierre | Tech lead | Qué supuestos no se cumplieron | Mejora la sesión y la evaluación de la información |

## 6. Glosario

| Término | Qué significa |
|---|---|
| Ficha del requerimiento | Lo que se sabe del proyecto, organizado por temas. Cada dato dice de qué fuente sale, con una cita literal, y quién lo afirmó. A1 la crea y crea una versión nueva con cada fuente. |
| Fuente | Cada material que aporta información: la solicitud, un correo, unas historias de usuario, la transcripción de una sesión o una nota interna del equipo. |
| Nivel de información | Qué tanto sabemos del proyecto: baja, media o alta. Lo calcula A2 con los 20 criterios del anexo B.1 del framework. |
| Criterio (D1.1, D3.2…) | Cada pregunta de la evaluación de la información. La letra D y el primer número indican la dimensión (alcance, funcionalidad, integraciones…). Estos códigos son internos y nunca llegan al cliente. |
| Dimensiones núcleo | Las cinco dimensiones que más pesan en la evaluación (D1 a D5). Si una queda por debajo de 40 %, el nivel de información no puede ser alto. |
| Techo de evidencia | El puntaje máximo que admite un dato según su respaldo: 1 si solo se dijo o lo afirma el equipo, 2 si el cliente lo escribió, 3 si el cliente lo confirmó. |
| Componente | Parte del proyecto que se puede construir y probar por separado y que pertenece a un solo arquetipo. Es lo que se estima. |
| Proceso funcional | Algo que un usuario u otro sistema puede hacer con la solución, como consultar una póliza. Las horas se calculan por proceso. |
| Arquetipo | El tipo de trabajo que concentra el esfuerzo: aplicaciones, integración, datos e inteligencia artificial, plataforma, seguridad o modernización. El principal es el de más horas; los secundarios pesan 15 % o más. |
| Talla | Tamaño por número de procesos: XS (1 a 5), S (6 a 15), M (16 a 30), L (31 a 60) y XL (más de 60, se divide). |
| Complejidad | Suma de cinco factores (reglas, arquitectura, seguridad, procesamiento y dependencias) que ajusta las horas: baja, media, alta o muy alta. |
| Entorno tecnológico (T1 a T4) | Qué tanto conoce la empresa la tecnología: T1 conocida, T2 parcialmente conocida, T3 nueva, T4 experimental. Sale del mapa de tecnologías. |
| Integración (I0 a I3) | De cuántos sistemas depende un componente y qué tan difíciles son. No suma horas; I3 es una señal de riesgo. |
| Reúso (R1 a R4) | Porcentaje de los procesos de un componente que ya cubre un activo de la empresa. Descuenta horas. |
| Activo reutilizable | Algo que la empresa ya construyó y puede volver a usar, como un módulo de autenticación. Está en el catálogo de activos con un identificador ACT. En la ficha, lo que el equipo menciona como posible reúso lleva el prefijo REU. |
| Madurez de un componente | Qué tan confiable es la información de un componente: Validado, Definido o Supuesto. La define A4 y no cambia las horas. No es lo mismo que el nivel de información del proyecto. |
| Mapa de tecnologías | Lista de las tecnologías que conoce la empresa, con su nivel y los otros nombres con que el cliente puede llamarlas. |
| Registro único | Donde vive cada solicitud: versiones de la ficha y de la estimación, estados y resultado comercial. |
| Registro de proyectos | Los proyectos ejecutados, con sus horas reales. Es de donde salen los proyectos comparables. |
| Proyecto comparable | Proyecto ejecutado del mismo arquetipo principal, de talla igual o adyacente y con horas reales, cuyo trabajo se parece al que se cotiza. |
| Experiencia | Qué tanto ha hecho la empresa proyectos así: comparables, datos registrados, experiencia del equipo y tecnología. Baja, media o alta. |
| Confianza | El menor entre el nivel de información y la experiencia. Define qué tan amplio es el rango y cómo se presenta el precio. |
| Escenarios y rango | Horas optimistas, esperadas y pesimistas. El rango es la distancia entre el optimista y el pesimista. |
| Línea base | La estimación que se envió al cliente. Al cierre, las horas reales se comparan con ella. |
| Modalidad | Cómo se cotiza: bolsa de horas, sprints, primer bloque o precio fijo. |
| Primer bloque | Parte del proyecto, de 320 a 480 horas, que entrega algo que el cliente puede usar y permite confirmar el resto. |
| Ruta estándar, compleja o preliminar | Quién aprueba la cotización. La compleja la deciden el CIO o el CEO por riesgo técnico, experiencia baja, valor, esfuerzo o cliente estratégico. Un rango preliminar lo revisa el validador. |
| Desviación | Diferencia entre las horas reales y las de la línea base, dividida entre las de la línea base. |
| Revisión de cierre | Sesión corta cuando un proyecto cierra fuera del rango, para entender qué supuestos fallaron. |
| Valores del método | Las cifras que usa el cálculo (horas por proceso, factores, márgenes, umbrales), en versiones aprobadas por la dirección. |
| Función | Programa sin inteligencia artificial que calcula o arma algo a partir de lo que entregan los agentes. Da siempre el mismo resultado con los mismos datos. |
| Verificación | Programa que revisa la salida de un agente y lista errores y avisos antes de que una persona la confirme. |
| Instrucciones y esquema | Las instrucciones son el texto que guía al agente. El esquema define la forma exacta de su respuesta (un archivo JSON, un formato de datos estructurado), para que las funciones la puedan leer. |

