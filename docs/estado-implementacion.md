# Estado de implementación · integración de agentes

Actualizado el 2 de noviembre de 2026. Se distingue código terminado de método
aprobado y de una estimación real ejecutada.

## Funcionalidad implementada

| Parte | Qué está disponible | Comprobación |
| --- | --- | --- |
| Instalación | Proyecto predeterminado configurable, catálogos vacíos y skills en un solo comando; conserva archivos existentes | scripts/install.py, con --skills-target opcional |
| Orquestación | Comandos del chat, orden, reintentos, historial y aprobaciones; un asistente puede asumir los roles | AGENTS.md y motor de flujo |
| Roles y skills | Once responsabilidades, mapa y recursos portables; adaptadores con ruta de instalación | configuracion/roles.json y skills/ |
| Información A1 | B.1, 9 dimensiones/20 criterios, techo por evidencia, prioridades y rondas | scripts/madurez.py; sin conteo de sesiones |
| Componentes y clasificación | Instrucciones, plantillas, trazabilidad y PRE/PEN estables; ejecución por el asistente | agentes/a2.md y agentes/a3.md |
| Parámetros | Operación, costeo, capacidad, método y fuentes centrales; vacíos explícitos | configuracion/framework.json |
| Estimación por procesos | Esfuerzo, gestión una sola vez, costos por componente, Base/Conservador y optimista referencial | framework/process_estimation.py |
| Recursos | Capacidad por rol y dependencias; detección de ciclos, sin sobreasignar pools | Calendario reproducible; no optimiza fechas |
| Cálculo A4 con reglas aprobadas | Lee el snapshot, conserva entrada/resultado/informe y registra hashes; rechaza ensayo incompleto | scripts/estimar_procesos.py --approved |
| Revisión | Comprueba paquete y soportes numéricos; aprobación humana por versión | finish/approve revision |
| Aprendizaje | Comparación con línea base aceptada, cambios aprobados y horas reales; informe versionado | scripts/aprendizaje.py; no modifica etapas ni catálogos |
| Portal | Manual actualizado, consulta por carpeta y evidencias | tablero/ y servidor solo local |
| Diagnóstico | Separa errores de instalación de datos o aprobaciones pendientes | python scripts/framework.py doctor |

Los agentes realizan extracción, interpretación, división, juicio y redacción;
el motor no ejecuta modelos IA por su cuenta. Las pruebas automáticas comprueban
código y controles, no certifican el juicio de un modelo ni la fidelidad semántica
de un informe real. Las citas se revisan también contra las fuentes originales.

## Datos y decisiones que faltan para uso real

El motor está preparado para leer parámetros reales, pero todavía faltan moneda,
tarifas/costo horario, equipo, calibración de horas por proceso, factores y bandas,
fuentes y aprobación de reglas. No se cargaron los números ilustrativos del ZIP.
El costeo inicial elegido es costo horario único del equipo; su importe sigue sin definir.

Consultar los asuntos abiertos en reglas/integracion-agentes.md. INC-008/010/014 están resueltos: Validado/Definido/Supuesto por componente,
confirmación directa escrita o transcrita con hablante identificado y costo horario
único. Las cifras y la aprobación del método siguen siendo decisiones separadas.

## Funciones del paquete fuente que no se activaron

- Publicación, envío de propuestas o actas y conexiones automáticas a Jira/proveedores.
- Precios comerciales, modalidades, recargos o márgenes por defecto del ZIP.
- Registro automático en catálogos corporativos o recalibración sin confirmación.
- Armado DOCX del paquete original, con su plantilla e identidad de empresa.
- COCOMO II productivo: permanece como alternativa, sin implementación completa.

Estas funciones no son necesarias para estimar en el flujo local acordado y no se
presentan como integradas. Los originales se conservan como referencia, separados
del motor activo. Su validación funcional completa no equivale a la de esta adaptación.

## Verificación

La batería incluye una instalación aislada y un recorrido con datos sintéticos:
orden y aprobación A1, aprobación de reglas de prueba, cálculo A4, revisión,
aprobación de versión y aprendizaje desde horas reales ficticias. Comprueba
reconciliación de costos/esfuerzo, dependencias, capacidad y bloqueo por cambios
en snapshots o soportes. No ejecuta ni aprueba el piloto.

Ejecutar python -m unittest discover -s tests -q. Las once skills también pasan
la comprobación de su formato. doctor puede dar instalación técnica correcta y,
al mismo tiempo, indicar que faltan datos para estimar: son estados distintos.


INC-016 resuelto: escala ZIP de reutilización con bandas parametrizadas. Hay
verificación de límites y bloqueo de clases que no corresponden al porcentaje,
para evitar usar factores del ZIP con etiquetas invertidas del Excel. Los valores
de ahorro continúan por definir y aprobar.


## Comprobación final y entrega

La implementación técnica del flujo local incluye el bloqueo por modificación de
entregables aceptados, una demostración reproducible y un comando único de
verificación. scripts/verificar.py comprueba instalación y ejecuta las pruebas.
scripts/demo_procesos.py permite revisar el informe actual sin datos del cliente
ni aprobaciones reales. Los archivos de pruebas y demo no son resultados del piloto.

Las decisiones operativas INC-002/004/005/006/007/008/010/014/016 están resueltas;
las equivalencias restantes están documentadas. La configuración de negocio y la
calibración permanecen vacías por instrucción del usuario, para completarlas después.
Esto es configuración pendiente de uso real, no una interrupción del desarrollo.
Las funciones externas y comerciales listadas arriba permanecen fuera del flujo
local acordado; no se presentaron como implementadas ni se aprobaron por defecto.
