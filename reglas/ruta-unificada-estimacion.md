# Ruta común de estimación

Decisión del usuario, 8 de noviembre de 2026: «implementa esa ruta unificada para
todos los proyectos, usando la tabla que cargué y el método por actividades para
los faltantes, sin volver a pedirme información que ya tenemos».

Prevalece sobre la exigencia anterior de conseguir otra tabla de productividad o
históricos antes de preparar una estimación. Aplica a todos los expedientes nuevos
y a sus próximas ejecuciones; no recalcula ni cambia entregas aceptadas.

## 1. Recuperar antes de preguntar

Ejecutar `python scripts/framework.py --project <id> estimation-route`. Consultar
las respuestas, adendas, alcance aceptado, supuestos vigentes y configuración del
expediente. No interpretar un campo null del archivo global como ausencia de dato
en el proyecto. No copiar respuestas o valores de otro cliente.

Consolidar valores ya aportados en
`01-entradas/respuestas/parametros-estimacion.json`, con fuente por campo. Este
archivo aplica solo al proyecto y entra en su huella/snapshot. No pedir otra vez
moneda, costo, equipo o capacidad si ya están documentados. Si existen decisiones
contradictorias y no se puede establecer la vigente, preguntar solo por el conflicto.
Conservar unidades originales: horas mensuales no son horas semanales. Una
conversión necesaria debe declararse y justificarse, sin volver a pedir el valor.

## 2. Asignar una sola valoración a cada unidad

Crear un inventario explícito de unidades estimables a partir de A2 y las adendas.
Cada unidad conserva su ID y tiene un componente. Registrar cobertura y método
en una misma entrada de cálculo, sin scripts de cálculo inventados por proyecto.

**Procesos con cobertura y clasificación suficientes:** usar la tabla ya cargada
en `configuracion/framework.json`, `estimation.process_method`. Aplicaciones 40,
integración 60, datos/IA 70, plataforma 50, seguridad 60 y modernización 50 horas
por proceso. Los factores y bandas del mismo archivo fuente se incorporan como
referencia inicial junto con la tabla; no constituyen productividad calibrada.
No se adoptan su costo horario, márgenes, capacidad por sprint ni bloque comercial.

**Trabajo fuera de cobertura:** proponer actividades concretas y horas optimistas
(O), probables (M) y pesimistas (P), con justificación y fuente. Base =
(O + 4M + P)/6; Conservador = P. Esto también permite estimar una partida cuyo
proceso aún no puede usar la tabla por falta de clasificación suficiente: explicar
el límite y usar actividades, sin inventar clases de complejidad, entorno o reúso.
El agente está autorizado a preparar esos rangos como juicio explícito para revisión;
no tiene que pedir al experto que produzca una tabla o un histórico inexistente.

Registrar qué trabajo cubre cada rango y sus límites. No sustituir un proceso
conocido y clasificable por horas arbitrarias. No estimar todo un componente y
sumar luego sus partes. El motor rechaza coberturas duplicadas, faltantes y extras
respecto del inventario declarado. El agente verifica además su correspondencia
semántica con A2: los IDs solos no prueban cobertura.

## 3. Gestión, escenarios y calendario

Declarar por partida si la gestión ya está incluida. Si lo está, no sumar el 15 %
del catálogo. Si no, agregarlo una sola vez y asignarlo a capacidad de un rol.
No aplicar la banda de incertidumbre de procesos sobre P de las actividades.
Ambos escenarios mantienen exactamente alcance, costo horario y equipo.

Antes de publicar, revisar cuántas partidas usaron la tabla y cuántas usaron
actividades. Si todas usan O/M/P, contrastar los procesos funcionales con la tabla
y justificar por qué sigue sin aplicar en cada familia. Comparar las horas
probables por unidad con la referencia disponible, incluso si se necesita O/M/P.
Comprobar que la preparación, integración y pruebas compartidas se cuenten una vez.

Explicar la brecha Base–Conservador y las partidas que más aportan. Sustentar P con
condiciones adversas concretas y compatibles con el escenario del proyecto. Revisar
si se acumularon contingencias independientes como si ocurrieran todas a la vez.
Una variante que exceda cantidades o límites se presenta como opción separada.
Si solo se tiene una suma de extremos, identificarla como tal en la revisión y
justificar el escenario antes de usarlo en una oferta. Evitar recortes o topes
porcentuales sin evidencia de calibración.

Usar costo y capacidad del propio expediente. El calendario común trabaja con
capacidad efectiva semanal por rol y dependencias explícitas entre componentes;
las tareas de distintos roles dentro de un componente pueden solaparse. Si esa
hipótesis no es válida, separar fases en unidades de planificación o declarar el
plazo como parcial hasta disponer de un plan sustentado. No prometer fechas.

## 4. Propuesta y aprobación

`!estimar` consulta esta ruta antes de intentar iniciar A4. Si faltan aprobaciones
formales, prepara una preestimación separada con la misma ruta y señala los
pendientes; no abandona el análisis exigiendo otra fuente de productividad.
Un dato material realmente ausente puede quedar como hipótesis explícita para
revisión o como pendiente; nunca se atribuye al cliente ni se transforma en cero.

Las aprobaciones de A1, reglas completas y revisión final se conservan. La orden
de unificar el método autoriza su uso inicial y la preparación de rangos, no aprueba
automáticamente un requerimiento, los rangos propuestos ni todo el paquete de A4.
Los snapshots existentes no se editan. La nueva configuración modifica la huella:
para una ejecución formal posterior se revisa/aprueba el nuevo paquete.

## Ejecución común

Para cotizaciones nuevas, agrupar las unidades en paquetes de trabajo. Separar el
trabajo común, como preparar un conector o una plantilla, del que se repite por
integración, reporte o servicio. Usar partidas separadas para familias con distinto
esfuerzo. Enumerar los IDs cubiertos una sola vez. La cantidad del paquete mide el
trabajo repetible y puede diferir del número de IDs que documentan su cobertura.

En cada `work_item` nuevo, agregar `package` con estos campos:

| Campo | Contenido |
| --- | --- |
| `type` | `common` para trabajo común o `per_unit` para trabajo repetible |
| `quantity` | Cantidad entera positiva. Para `common` siempre es 1 |
| `unit` | Unidad cotizada, como integración comparable o familia de reportes |
| `assumption` | Condición usada para valorar la partida y su fundamento |
| `limit` | Cantidad o condición máxima incluida |
| `requote_when` | Cambio verificable que requiere revisar la cotización |

Usar las horas de tabla por proceso equivalente o las horas O/M/P por unidad.
El motor multiplica cada escenario por la cantidad del paquete, aplica gestión
una vez donde corresponda y conserva los límites en el respaldo. Si un escenario
cambia el alcance, presentarlo como alternativa separada. Mantener en el informe
principal los límites y condiciones de recotización que afecten la decisión.
El formato previo sigue disponible para reproducir estimaciones existentes.

`scripts/estimar_procesos.py` admite componentes con `work_items`. Cada partida
declara id, kind (`process` o `activity`), description, source, routing_reason,
covers (IDs de trabajo) e includes_management. Los procesos declaran arquetipo,
clases de complejidad/entorno/reúso y porcentaje de reúso; si no bastan, aportan
omp. Las actividades siempre aportan omp: optimistic, likely y pessimistic.
Conservar role_split y dependencies por componente y management_role_split cuando
haya gestión adicional. `expected_work_ids` y `coverage_source` fijan el inventario.

Usar `--experimental` para preparar propuesta sin alterar etapas; `--approved`
solo después de iniciar A4 con snapshot aprobado. Ambos usan el mismo cálculo.
Los informes resultantes incluyen un respaldo legible de cobertura y fundamento.
El formato anterior de procesos se conserva para reproducir entradas existentes;
no generar nuevas estimaciones con scripts particulares de cada expediente.

Ejemplo estructurado: `ejemplos/ruta-unificada/entrada.json`.

## Modelo Propuesta V2 para cotizaciones nuevas

La fuente es `Modelos Propuesta V2.xlsx`, incorporada como catálogo de horas en
`configuracion/modelo-propuesta-v2.json`. Esta sección prevalece sobre las referencias
anteriores a la tabla de 40–70 horas por proceso. Para nuevas cotizaciones, buscar
primero una analogía en `DatosExt`, luego en `IA` y usar O/M/P cuando ninguna tenga
cobertura. Las entradas antiguas con `kind: process` siguen siendo reproducibles.

Buscar una coincidencia exacta en tipo de desarrollo, arquetipo, talla, complejidad
e integración. Justificar cada clasificación con la evidencia de A2 y A3. Un
componente compuesto puede dividirse en paquetes comparables, sin duplicar alcance.
La ausencia de factores de entorno o reúso del método anterior no impide la analogía.

`DatosExt` contiene 85 filas con esfuerzo numérico y muestra utilizable. Usarla
solo cuando la unidad sea comparable con los proyectos de la muestra. La talla de
cada conjunto externo se originó en quintiles de su propia métrica de tamaño. Por
eso, una etiqueta XS–XL de FADE por sí sola no establece equivalencia. Citar una
base comparable de talla y cobertura. Evitar multiplicar esfuerzo de proyecto por
reporte, conector o proceso. Si la fila no tiene horas o su unidad no es comparable,
consultar `IA`, que contiene 1.920 referencias de esfuerzo generado por el modelo.
Identificarlas como referencias modeladas y conservar hoja, fila y muestra cuando
exista. Los ejemplos de historias sirven para entender la escala de cada referencia.

La hora-persona de la fila es la Base por unidad. Sus dimensiones ya están reflejadas
en el valor. Las bandas vigentes definen el Conservador para analogías y la gestión
se suma según su cobertura. La duración se calcula con capacidad y dependencias del
expediente. La columna de tiempo de la muestra tiene otro significado y queda fuera
del calendario del proyecto. Aplicar O/M/P solo a trabajo sin analogía comparable.

En `work_items`, usar `kind: analogy` y declarar estos campos junto con el paquete:

```json
{
  "kind": "analogy",
  "dimensions": {
    "development": "Nuevo",
    "archetype": "Aplicaciones",
    "size": "XS",
    "complexity": "Baja",
    "integration": "I0"
  },
  "size_basis": "Ejemplo ficticio de módulo acotado. Citar la frontera y las operaciones comparadas.",
  "external_fit": false,
  "external_exclusion": "La unidad es un módulo, mientras la fila externa corresponde a proyectos completos."
}
```

Con `external_fit: true`, sustentar la comparabilidad en `routing_reason` y usar
cantidad uno. Si `DatosExt` carece de horas para la combinación, el motor usa `IA`.
Cuando una partida no tenga una analogía defendible, usar `kind: activity` y
justificar por qué ninguna hoja aplica. Si la misma unidad tiene analogía y un rango
O/M/P, el motor pide elegir una valoración. El catálogo entra en la huella y el
snapshot de reglas, con la fuente y las filas seleccionadas en el respaldo.
