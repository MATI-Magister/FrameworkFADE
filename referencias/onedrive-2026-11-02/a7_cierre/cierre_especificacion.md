# A7 · Cerrar y aprender · Especificación (v0.1)

Especificación independiente de la herramienta. Describe qué hace el agente, qué recibe, qué entrega y cómo se revisa su resultado.

Este documento es para quien construye y opera el agente. No se carga en el agente: el agente recibe sus instrucciones (`cierre_instrucciones.md`), el esquema de salida (`faed_cierre.schema.json`) y, en cada ejecución, la preparación del cierre, las fichas de los componentes, la propuesta, el catálogo de activos y las notas de cierre.

## 1. Propósito y límites

**Propósito.** Preparar el cierre de cada proyecto ejecutado para que el método aprenda: confirmar el reúso real de cada activo usado como evidencia, proponer la causa de cada desviación que supera el umbral, identificar los activos nuevos y, si el proyecto cerró fuera del rango, reunir los insumos de la revisión de cierre.

**Lugar en el recorrido.** Cuando el proyecto se cierra en la herramienta de gestión, dentro del plazo que defina la empresa. Lo conduce el dueño del framework con el líder del proyecto.

**El agente propone; el líder confirma; las funciones calculan y registran.** Una función consolida las horas de Jira y calcula las desviaciones; A7 propone lo que requiere criterio; el líder del proyecto lo confirma; otra función lo registra en el registro de proyectos y en el catálogo de activos.

**Lo que no hace.** No calcula horas ni desviaciones, no registra nada y no usa información que no esté en las notas, las fichas de los componentes, la propuesta o el catálogo.

## 2. Recorrido de un cierre

Los cinco pasos del cierre y aprendizaje del framework quedan así:

| Paso del framework | Quién lo hace |
|---|---|
| 1. Registrar horas reales y cambios de alcance; calcular la desviación | El equipo exporta las horas de Jira; la función `cierre` consolida y calcula |
| 2. Confirmar el reúso real | A7 propone; el líder del proyecto confirma |
| 3. Registrar la causa de cada desviación sobre el umbral | A7 propone; el líder del proyecto confirma |
| 4. Agregar los activos nuevos al catálogo | A7 propone; el líder confirma; la función de registro los agrega |
| 5. Marcar la solicitud como cerrada | El dueño del framework, en el registro único, después de registrar |

En la práctica:

1. **Exportar las horas.** Desde Jira, un CSV con las columnas `epica` y `horas`. Cada épica de un componente empieza por su código (`C01 Portal de autogestión`) y la de gestión contiene la palabra *gestión*. Los trabajos que no se estimaron, como el soporte posterior a la salida a producción, van en épicas que empiezan por `FUERA` (`FUERA Soporte a producción`): sus horas se registran aparte y no cuentan en la desviación. Puede haber varias filas por épica: la función las suma.
2. **Preparar.** La función compara las horas reales con la línea base (el escenario enviado), ajustada por los cambios de alcance aprobados:
   ```
   python calculo/faed_calculos.py cierre linea_base.json --jira horas.csv --cambios cambios.json > preparacion_cierre.json
   ```
   Lista las épicas que no corresponden a ningún componente y los componentes sin horas, para corregir la exportación antes de seguir.
3. **Proponer.** A7 entrega la propuesta de cierre.
4. **Verificar.** `verificacion/revisar_cierre.py` revisa la salida.
5. **Confirmar.** El líder del proyecto responde las preguntas, corrige lo que no comparte y deja cada reúso confirmado o descartado y cada causa elegida.
6. **Registrar.**
   ```
   python registro/registrar_cierre.py cierre_confirmado.json preparacion_cierre.json linea_base.json detalle.json --registro datos/registro_proyectos.json --catalogo datos/catalogo_activos.json --nombre "..." --cliente "..." --duracion 5 --salida-registro registro_v2.json --salida-catalogo catalogo_v2.json
   ```
   La función no registra un cierre con reúsos sin confirmar o causas por confirmar. Registra el arquetipo principal con las horas reales, porque así lo comparará A5 en las próximas cotizaciones, y escribe versiones nuevas del registro y del catálogo.
7. **Revisar indicadores.** Con el registro actualizado, el dueño del framework revisa los indicadores y si se activó el disparador de recalibración:
   ```
   python calculo/faed_calculos.py indicadores registro_v2.json --catalogo catalogo_v2.json
   ```
8. **Revisión de cierre**, si el proyecto cerró fuera del rango: el responsable de la estimación y el dueño del framework la hacen con los insumos de A7.

## 3. Entradas y salida

| Entrada | Descripción |
|---|---|
| Solicitud | Identificador de la solicitud y cliente registrado |
| Preparación del cierre | Salida de la función `cierre` |
| Fichas de los componentes | Salida de A4 con la que se estimó |
| Propuesta | Textos de A6 que se enviaron, con sus supuestos |
| Catálogo de activos | `datos/catalogo_activos.json` vigente |
| Notas de cierre | Lo que registró el equipo, en texto plano y con una marca por línea: `[l. 4]` |

**Mensaje que recibe el agente.** Las instrucciones van como mensaje de sistema. Cada ejecución se entrega así:

```
<solicitud id="SOL-2026-0042" cliente="Nombre del cliente registrado" />
<preparacion>{ ...salida de la función cierre en JSON... }</preparacion>
<detalle>{ ...salida de A4 en JSON... }</detalle>
<propuesta>{ ...salida de A6 en JSON... }</propuesta>
<catalogo_activos>{ ...catálogo en JSON... }</catalogo_activos>
<fuente id="F3" tipo="notas_cierre">
[l. 1] ...
</fuente>
```

**Salida.** La propuesta de cierre según `faed_cierre.schema.json`, compatible con el modo estricto.

## 4. Reglas que conviene conocer

**Línea base.** Es el escenario que se envió al cliente. Las horas de cada cambio de alcance aprobado se suman a la línea base del componente y al rango, para no confundir un cambio del proyecto con un error de estimación.

**Umbral.** Requieren causa los componentes cuya desviación, en valor absoluto, supera el umbral de los valores del método (20 %). Una desviación hacia abajo también se explica: un reúso mayor al estimado es tan útil para recalibrar como uno menor.

**Revisión de cierre.** Se requiere cuando las horas reales del proyecto quedan fuera del rango ajustado. A7 solo prepara sus insumos en ese caso.

**Evidencia.** Todo lo que A7 confirma lleva una cita literal de las notas. Lo que las notas no sustentan queda en null o por confirmar, con su pregunta para el líder del proyecto. Por eso conviene que las notas de cierre cubran cada activo usado, cada componente desviado y lo que se construyó que pueda volver a usarse.

## 5. Revisión de cada salida

La revisión comprueba:

1. **Estructura.** La salida cumple el esquema y corresponde a la solicitud.
2. **Cobertura.** Hay un elemento de reúso por cada activo que se usó como evidencia y una causa por cada componente que la requiere.
3. **Citas.** Cada cita aparece literal en su línea de las notas.
4. **Evidencia.** Todo lo confirmado tiene cita; lo que no, queda en null o por confirmar, con pregunta para el líder.
5. **Activos nuevos.** Existen su componente de origen y sus procesos, y no están ya en el catálogo.
6. **Revisión de cierre.** Se llena solo si el proyecto cerró fuera del rango, y cada supuesto no cumplido está copiado tal como aparece en la propuesta o en las fichas de los componentes.
7. **Causa correcta.** Cada causa es la que mejor explica la desviación.
8. **Activo útil.** Cada activo nuevo se puede volver a usar de verdad.

Los puntos 1 a 6 los comprueba `verificacion/revisar_cierre.py`. Los puntos 7 y 8 los confirma el líder del proyecto.

## 6. Parámetros y buenas prácticas

- Nombrar las épicas de Jira con el código del componente desde el inicio del proyecto: es lo que permite comparar las horas reales con la estimación.
- Registrar los cambios de alcance aprobados en un archivo con el componente, las horas y la descripción, a medida que se aprueban.
- Escribir las notas de cierre con el equipo, antes de que se disperse.
- Fijar el modelo y su versión, usar la temperatura más baja que permita la herramienta y registrar la versión de las instrucciones y del esquema.
- Mantener los casos de ejemplo fuera del contexto al que tiene acceso el agente.
- Ajustar las instrucciones solo en `cierre_instrucciones.md`, con una versión nueva (v0.2, v0.3…).
