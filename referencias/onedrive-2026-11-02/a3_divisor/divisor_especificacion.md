# A3 · Dividir · Especificación (v0.2)

Especificación independiente de la herramienta. Describe qué hace el agente, qué recibe, qué entrega y cómo se revisa su resultado.

Este documento es para quien construye y opera el agente. No se carga en el agente: el agente recibe sus instrucciones (`divisor_instrucciones.md`), el esquema de salida (`faed_componentes.schema.json`) y, en cada ejecución, la solicitud, los parámetros, la ficha y su evaluación.

## 1. Propósito y límites

**Propósito.** Dividir el proyecto en componentes que se pueden construir y probar por separado, cada uno de un solo arquetipo y con sus procesos funcionales. Es la base del conteo de horas: cada componente parte de sus procesos multiplicados por las horas por proceso de su arquetipo.

**Lugar en el recorrido.** Inicia la estimación. Se ejecuta cuando el Tech lead confirma que la información alcanza, cuando se alcanzó el máximo de sesiones (estimación preliminar) o cuando la solicitud es urgente (carril rápido).

**Qué entrega.** Los componentes con sus procesos, los criterios de división que originaron cada uno y, con información baja, su talla probable; los procesos de la ficha que no se asignaron y por qué; las interfaces que no generan componente y por qué; los supuestos y las advertencias.

**Lo que no hace.** No califica complejidad, reúso, entorno ni integración (lo hace A4), no calcula horas ni precios y no modifica la ficha.

## 2. Recorrido de una ejecución

1. **Decidir el tipo de estimación.** Con la evaluación confirmada, el Tech lead decide si la estimación es formal o preliminar.
2. **Dividir.** A3 recibe la ficha, su evaluación y el tipo de estimación. Con el nivel de información fija qué tan profundo divide; luego forma los componentes con claves fijas por arquetipo y aplica las separaciones que tengan evidencia en la evaluación. Entrega los componentes con sus procesos.
3. **Verificar.** `verificacion/revisar_componentes.py` comprueba que cada proceso de la ficha quede en un solo componente, que cada interfaz tenga su componente de integración o su motivo para no tenerlo y, si recibe la evaluación, que cada separación tenga evidencia.
4. **Seguir.** Los componentes pasan a A4; la división se revisa en la validación del escenario.

## 3. Entradas y salida

| Entrada | Descripción |
|---|---|
| Solicitud | Identificador de la solicitud y cliente registrado |
| Tipo de estimación | `formal` o `preliminar`, según la decisión del Tech lead o el carril rápido |
| Carril rápido | `si` si la solicitud es urgente; `no` en otro caso |
| Ficha | Última versión revisada de la ficha del requerimiento, completa |
| Evaluación | Salida de A2 sobre esa versión de la ficha, confirmada: nivel general y puntaje de cada criterio. En el carril rápido puede faltar; el agente trata entonces el nivel como bajo |

**Mensaje que recibe el agente.** Las instrucciones van como mensaje de sistema. Cada ejecución se entrega así:

```
<solicitud id="SOL-2026-0042" cliente="Nombre del cliente registrado" />
<parametros tipo_estimacion="formal" carril_rapido="no" />
<ficha>
{ ...última versión revisada de la ficha, en JSON... }
</ficha>
<evaluacion>
{ ...evaluación de A2 sobre esa versión, en JSON... }
</evaluacion>
```

**Salida.** Los componentes según `faed_componentes.schema.json`. Si la herramienta permite fijar la salida estructurada, se carga el esquema en esa opción; si no, se agrega al final de las instrucciones bajo el título "Esquema de salida". El esquema es compatible con el modo estricto.

## 4. Reglas que conviene conocer

**Procesos de la ficha e inferidos.** Cada proceso indica su origen. Los de la ficha citan el dato que los sustenta. Los inferidos son procesos que la solución necesita y la ficha no menciona, como recuperar la contraseña cuando el cliente pide un ingreso con credenciales. El agente puede agregarlos para no subestimar, pero nunca para ampliar el alcance, y cada uno lleva su justificación y genera un supuesto para la propuesta. La madurez de un componente con procesos inferidos no puede ser *Validado*.

**Integración y migración.** Cada interfaz que requiere un conector y cada migración de datos se estiman como componentes propios, de integración y de modernización. Así lo pide el framework, porque su esfuerzo no depende del componente que los usa.

**Profundidad y evidencia.** El nivel de información de la evaluación fija la profundidad: con información baja o en carril rápido, el agente propone componentes candidatos con su talla probable y solo aplica los criterios estructurales y el de riesgo (CR-01); con información media aplica cada familia de criterios donde haya evidencia, y con alta, todas. Una separación por riesgo, regulación u homogeneidad solo se hace si el criterio de la evaluación que la sustenta tiene 2 o más; si no, se registra un supuesto. Cada componente registra los criterios que lo originaron, para que la división sea reproducible y se pueda comparar con proyectos anteriores. La talla probable no cambia las horas, que siguen saliendo de los procesos listados: le avisa al validador cuando lo listado se queda corto.

**Conservación.** Cada proceso funcional vigente de la ficha queda en un componente o en la lista de procesos sin asignar, con su motivo. Un proceso que desaparece se deja de estimar; uno repetido se estima dos veces.

## 5. Revisión de cada salida

La revisión comprueba:

1. **Estructura.** La salida cumple el esquema y corresponde a la solicitud, a la versión de la ficha y al tipo de estimación recibidos.
2. **Conservación.** Cada proceso funcional vigente de la ficha está en un solo proceso o en la lista de sin asignar.
3. **Evidencia.** Cada dato citado existe en la ficha y está vigente.
4. **Inferidos.** Cada proceso inferido tiene justificación y su componente tiene supuesto.
5. **Interfaces y migraciones.** Cada interfaz y cada migración de la ficha tiene su componente, o un motivo para no tenerlo en `dependencias_sin_componente`.
6. **Talla.** Ningún componente pasa de 60 procesos.
7. **Evidencia de las separaciones.** Cada criterio de riesgo, regulación u homogeneidad registrado tiene 2 o más en su criterio de la evaluación, y la profundidad corresponde al nivel de información (talla probable solo con información baja o carril rápido).
8. **Agrupación.** Los componentes agrupan lo que se construye y se prueba junto, y el arquetipo de cada uno es el que explica la mayor parte de su esfuerzo.
9. **Inferidos necesarios.** Cada proceso inferido es realmente necesario y no amplía el alcance.

Los puntos 1 a 7 los comprueba `verificacion/revisar_componentes.py` (el 7, cuando se le pasa la evaluación). Los puntos 8 y 9 requieren criterio humano y se revisan en la validación del escenario.

## 6. Parámetros y buenas prácticas

- Fijar el modelo y su versión, usar la temperatura más baja que permita la herramienta y registrar en cada ejecución la versión de las instrucciones y del esquema.
- Guardar cada salida como un archivo nuevo ligado a la versión de la ficha (por ejemplo, `SOL-2026-0042_componentes_ficha_v2.json`).
- Mantener los casos de ejemplo fuera del contexto al que tiene acceso el agente.
- Ajustar las instrucciones solo en `divisor_instrucciones.md`, con una versión nueva (v0.2, v0.3…).
