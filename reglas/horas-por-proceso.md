# Horas por proceso · método principal en evaluación

Dirección elegida por el usuario el 2026-11-02; todavía requiere calibración y
aprobación. Parámetros reales en configuracion/framework.json, sección estimation.
El archivo valores_metodo.json del ZIP contiene candidatos ilustrativos: 40–70 h
por proceso según arquetipo, factores, gestión 15 %, bandas de incertidumbre,
costo 85000 y margen 35 %. No son defaults ni decisiones aprobadas del usuario.

Fórmula candidata por componente: número de procesos × horas por proceso del
arquetipo × factor de complejidad × factor de entorno × factor de reúso.
Gestión se agrega una sola vez al subtotal de componentes y solo si no está ya
cubierta por la calibración. Toda partida debe declarar su cobertura.

Los procesos son capacidades funcionales identificadas, no historias completas ni
movimientos COSMIC ni líneas de código. Cada proceso tiene ID estable, nombre,
origen, fuente y componente. No sumar padre e hijo, ni duplicar procesos compartidos.
Separar una integración exige justificar quién construye o adapta el conector.

INC-005 resuelto: desconocidos por confirmar; preguntar al experto sin asignar
complejidad o tecnología por defecto. D8 usa Validado/Definido/Supuesto, sin cambiar factores de esfuerzo. Para reutilización exigir activo identificable y evidencia
de cobertura; el porcentaje estimado no prueba ahorro efectivo. La integración
puede ser señal de riesgo sin un multiplicador adicional; acordar con calibración.

## Ensayo reproducible

scripts/estimar_procesos.py --project <id> --input <archivo_del_expediente> --experimental

El JSON de entrada lleva information_level confirmado y components: id, processes
(lista de IDs únicos), archetype, complexity, environment, reuse y source. El
ensayo exige todos los factores configurados; no toma valores del ZIP por defecto.
Guarda resultado e informe experimental en 02-trabajo/, sin modificar estados.

Produce Base y Conservador según decisión explícita del usuario (INC-006); el
optimista del ZIP queda como referencia. La fórmula propuesta usa el menor nivel
entre información y experiencia confirmadas para seleccionar banda. El ensayo
puede explorar solo información si no hay experiencia, indicándolo como incompleto.
La calibración numérica y aprobación del método siguen siendo necesarias.

Duración depende de capacidad, asignaciones y dependencias. Costo usa inicialmente un costo horario único del equipo, elegido en INC-014. Precio comercial,
margen, impuestos e infraestructura son decisiones separadas. No inferir moneda.
La configuración vacía bloquea el ensayo y A4 real hasta completar y aprobar.
COCOMO II queda como alternativa, sin sumar ambos métodos sobre el mismo trabajo.


## Cálculo con snapshot aprobado

scripts/estimar_procesos.py --project <id> --input <archivo_del_expediente> --approved

Exige A4 en ejecución con reglas y parámetros completos aprobados. Lee exclusivamente
el snapshot de ese intento; rechaza cambios de reglas o del propio snapshot. Además
del formato de ensayo, completar:

- information_confirmed_by, experience_level, experience_confirmed_by y source.
- role_split por componente (fracciones que suman 1), dependencies (lista explícita,
  vacía si no tiene) y management_role_split cuando hay gestión.
- direct_costs y direct_costs_source; lista vacía solo como decisión explícita.

El costeo inicial elegido es estimation.costing_mode=costo_unico. El motor conserva
por_rol como alternativa que requeriría una decisión posterior explícita.
Las tarifas deben estar en la moneda configurada por hora/persona y tener fuente.
El equipo declara role, people, hours_per_week, allocation y source. El calendario
asigna cada tarea a su capacidad compartida, respeta precedencias y detecta ciclos;
es factible según esos datos, no un optimizador ni una promesa de fecha.

La gestión se reparte una vez por componente y rol; costo y horas reconcilian con
totales. Los costos directos comunes se muestran aparte para conservar la suma.
La ejecución escribe resultado e informe en 02-trabajo/calculo-a4-<fecha>/ y registra
sus huellas y la de la entrada. El agente prepara a4.md y revisa las cifras antes de
finish a4. Un soporte experimental, incompleto o alterado no habilita finalizar.
La revisión final y su aprobación también comprueban estos soportes.

Se implementó costo de ejecución, no precio de venta ni condiciones comerciales:
esas políticas del ZIP siguen pendientes y nunca se añaden porcentajes por defecto.


INC-016 resuelto: los porcentajes de reúso se clasifican con las bandas de
classification.reuse de la configuración, congeladas con el snapshot. Para modo
--approved cada componente incluye reuse_percentage (0–100) y reuse; se rechaza
una clase inconsistente o un porcentaje desconocido. La escala no define por sí
sola el descuento: reuse_factors permanece pendiente hasta revisión y calibración.
