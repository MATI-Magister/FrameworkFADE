# A4 · Detallar · Especificación (v0.2)

Especificación independiente de la herramienta. Describe qué hace el agente, qué recibe, qué entrega y cómo se revisa su resultado.

Este documento es para quien construye y opera el agente. No se carga en el agente: el agente recibe sus instrucciones (`detallador_instrucciones.md`), el esquema de salida (`faed_detalle_componentes.schema.json`) y, en cada ejecución, la ficha, los componentes, el catálogo de activos y el mapa de tecnologías.

## 1. Propósito y límites

**Propósito.** Completar la ficha de cada componente con lo que lo describe (frontera, usuarios, capacidades, datos, requisitos de calidad), lo que alimenta el cálculo de horas (complejidad, integración, entorno y reúso) y qué tan confiable es su información (madurez, supuestos y vacíos).

**Lugar en el recorrido.** Después de A3 · Dividir y antes del cálculo de horas.

**El agente juzga; las funciones calculan.** A4 califica los cinco factores de complejidad, marca qué procesos cubre cada activo, registra las interfaces y las tecnologías. Las funciones de `calculo/faed_calculos.py` convierten esos juicios en el nivel de reúso, el nivel de complejidad, el nivel de integración, el entorno y las horas de cada componente.

**Lo que no hace.** No cambia los componentes ni los procesos de A3, no calcula ningún nivel ni las horas y no modifica la ficha, el catálogo ni el mapa.

## 2. Recorrido de una ejecución

1. **Detallar.** A4 recibe la ficha, los componentes, el catálogo de activos y el mapa de tecnologías, y entrega la ficha de cada componente.
2. **Verificar.** `verificacion/revisar_detalle.py` revisa la salida, calcula las horas de cada componente y lista las confirmaciones.
3. **Confirmar.** El Tech lead confirma cada reúso de 30 % o más y el nivel de cada tecnología que no está en el mapa.
4. **Seguir.** Con las fichas confirmadas, la función `preparar` arma lo que recibe A5.

## 3. Entradas y salida

| Entrada | Descripción |
|---|---|
| Solicitud | Identificador de la solicitud y cliente registrado |
| Ficha | Última versión revisada de la ficha del requerimiento |
| Componentes | Salida de A3 · Dividir, ya verificada |
| Catálogo de activos | `datos/catalogo_activos.json`: activos reutilizables, procesos que cubren y estado |
| Mapa de tecnologías | `datos/mapa_tecnologias.json`: tecnologías que conoce la empresa y su nivel (T1 a T4) |

**Mensaje que recibe el agente.** Las instrucciones van como mensaje de sistema. Cada ejecución se entrega así:

```
<solicitud id="SOL-2026-0042" cliente="Nombre del cliente registrado" />
<ficha>{ ...ficha en JSON... }</ficha>
<componentes>{ ...salida de A3 en JSON... }</componentes>
<catalogo_activos>{ ...catálogo en JSON... }</catalogo_activos>
<mapa_tecnologias>{ ...mapa en JSON... }</mapa_tecnologias>
```

**Salida.** Las fichas de los componentes según `faed_detalle_componentes.schema.json`, compatible con el modo estricto. Después, `python calculo/faed_calculos.py componentes detalle.json` calcula las horas de cada componente.

## 4. Reglas que conviene conocer

**Coherencia con la división.** A3 registra por qué separó cada componente (`criterios_aplicados`) y qué interfaces no generan componente (`dependencias_sin_componente`). A4 usa esa información como evidencia: un componente separado por riesgo o complejidad no queda con su factor en 0 sin explicarlo, uno separado por reúso revisa primero el activo que lo originó y las interfaces que construye otro cuentan en las dependencias externas de los componentes que las usan.

**Factores sin evidencia.** Si la ficha no dice nada sobre un factor de complejidad, el agente lo califica con 1 y registra el supuesto y el vacío. Calificar con 0 lo que no se conoce subestimaría el componente.

**Reúso.** Solo cuentan los activos vigentes del catálogo que cubren el proceso según el propio catálogo. Los activos que requieren actualización no cuentan y quedan en las advertencias. El Tech lead confirma el reúso cuando es de 30 % o más del componente.

**Entorno tecnológico.** El nivel de cada tecnología sale del mapa de la empresa, con el nombre que tiene en el mapa: si el cliente la llama de otra forma, el mapa la reconoce por sus alias. Una tecnología que no está en el mapa se registra como T3 y el Tech lead la confirma una sola vez, aunque la usen varios componentes. Los protocolos de intercambio (REST, SOAP, MQTT) no son tecnologías del mapa: su dificultad está en las interfaces. El entorno del componente es el de su tecnología menos conocida; si el cliente no exige tecnologías, se asume T1, porque la empresa usa las que conoce.

**Interfaces.** Un componente de integración registra la interfaz que construye. Un componente que usa información de otros sistemas registra todas las interfaces que usa, aunque cada una tenga su propio componente de integración. Así, el nivel de integración, que no suma horas pero es una señal de riesgo, muestra de cuántos sistemas depende cada parte de la solución.

**Madurez.** Usa la escala de evidencia de la evaluación de la información: *Validado* si todos los procesos salen de la ficha con datos confirmados por el cliente; *Definido* si salen de fuentes escritas del cliente sin confirmar; *Supuesto* si hay procesos inferidos, datos verbales, del equipo o en contradicción abierta. Manda el proceso más débil. La madurez no cambia las horas: le dice al validador dónde mirar y a la propuesta qué conviene confirmar primero con el cliente.

## 5. Revisión de cada salida

La revisión comprueba:

1. **Estructura.** La salida cumple el esquema y corresponde a la solicitud y a la versión de la ficha.
2. **Correspondencia.** Hay una ficha por cada componente de A3, con sus mismos nombres, arquetipos y procesos.
3. **Reúso.** Cada reúso se apoya en un activo vigente del catálogo y tiene justificación.
4. **Complejidad.** La evidencia de cada factor existe en la ficha, y cada factor sin evidencia tiene puntaje 1.
5. **Interfaces y tecnologías.** Coinciden con la ficha y con el mapa, o están en T3 si no están en el mapa.
6. **Madurez.** No es mayor que la que permite la evidencia de sus procesos.
7. **Preguntas.** Ningún vacío pregunta con códigos internos.
8. **Puntajes.** Cada factor de complejidad corresponde a su descripción en la rúbrica.
9. **Reúso real.** Cada activo cubre de verdad el proceso, más allá de lo que dice el catálogo.

Los puntos 1 a 7 los comprueba `verificacion/revisar_detalle.py`, que además calcula cada componente y lista las confirmaciones que requiere del Tech lead. Los puntos 8 y 9 requieren criterio humano.

## 6. Parámetros y buenas prácticas

- Mantener el catálogo de activos y el mapa de tecnologías al día: A4 solo sabe lo que ellos dicen. Los activos nuevos entran al catálogo en el cierre de cada proyecto.
- Fijar el modelo y su versión, usar la temperatura más baja que permita la herramienta y registrar la versión de las instrucciones, del esquema, del catálogo y del mapa.
- Guardar cada salida como un archivo nuevo ligado a la versión de la ficha.
- Mantener los casos de ejemplo fuera del contexto al que tiene acceso el agente.
- Ajustar las instrucciones solo en `detallador_instrucciones.md`, con una versión nueva (v0.2, v0.3…).
