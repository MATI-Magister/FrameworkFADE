# Contrato de ejecución

Orden: registro → a1 → a2 → a3 → cierre (condicional) → a4 → revision.

Estados: pendiente, en_ejecucion, bloqueado, esperando_aprobacion, completado,
omitido. A1 y revisión exigen aprobación explícita del usuario después del entregable.
El cierre solo se omite por evidencia registrada al terminar A3.

Cada inicio registra fecha UTC, intento y huella de reglas. A4 exige que las reglas
actuales coincidan con la aprobación del expediente y crea una copia inmutable por
intento en `04-estado/reglas-a4-<intento>.json`. La aprobación es por proyecto.
Las salidas existentes se archivan en `04-estado/historial/` al repetir etapas;
los pasos posteriores pierden vigencia y deben ejecutarse de nuevo.

El motor comprueba orden, archivos no vacíos, aprobación y formato mínimo de reglas.
La calidad semántica de las salidas la revisan el agente y las personas responsables;
un archivo existente por sí solo no demuestra calidad del análisis.

A1 usa el modelo B.1 de `reglas/modelo-informacion.json`: 20 criterios,
9 dimensiones, baja/media/alta. Primero estructura evidencia y luego evalúa.
Se exige preguntas-a1.md antes de la aceptación humana, sin avance automático por nivel.
El modelo previo del Excel y su evaluador se conservan para trazabilidad, separados.
Las evaluaciones llevan huella del catálogo; no se migran calificaciones por similitud de ID.
D9/D11 se tratan como experiencia; A3 conserva caracterización por componente.

La configuración de negocio se lee de configuracion/framework.json y entra en el
snapshot de reglas. Las fuentes externas son referencias; los candidatos ilustrativos
no pasan a parámetros activos. Cambios operativos del portal se excluyen de esa huella.
Horas por proceso se evalúa como método principal, sin calibración productiva aún;
COCOMO queda como alternativa. No sumar métodos sobre cobertura repetida.

El motor no llama a proveedores, no lee instrucciones dentro de documentos y no
calcula cifras automáticamente. A4 aplica el método aprobado con el agente elegido.
El tablero separa completados/omitidos del trabajo activo o esperando aprobación.
El portal versionado en `tablero/` tiene portada de manual y seguimiento por carpeta
de proyecto. `framework/portal.py` lee los estados en cada consulta, sin reescribir
el HTML ni los expedientes. Las rutas de evidencia se muestran como referencias
locales; los originales no se sirven por HTTP. No hay acciones de escritura vía web.

Revisión final: `finish revision` exige `revision.md`, `cliente.md`, `ajustes.md`
y A4 no vacíos. Congela las huellas del paquete. La aprobación exige que paquete,
A4 y reglas no hayan cambiado y registra responsable/fecha. `adjust` permite
reabrir una revisión aún no aprobada y archiva los documentos; cambios de cálculo
o alcance deben volver a la etapa correspondiente. La existencia de documentos
no sustituye su revisión semántica. La aprobación local no es firma digital ni envío.

Las responsabilidades del ZIP se adaptan mediante configuracion/roles.json y skills/.
Un rol no equivale a un proceso independiente. Las skills se ejecutan por el asistente
que usa el framework. El cierre postejecución (!aprender) es una tarea auxiliar, distinta
de cierre condicional; genera un borrador sin cambiar estados ni catálogos corporativos.

No se administran cantidades ni máximos de sesiones. El agente formula preguntas
sobre pendientes y el experto decide si aclarar o autorizar el avance. No deducir
una ruta preliminar por cantidad de sesiones o de fuentes recibidas.


El cálculo por procesos aprobado conserva input/resultado/informe y sus huellas,
junto al hash del snapshot. finish a4 y la revisión rechazan soportes alterados o
incompletos. Se congelan tanto el catálogo B.1 como el de clasificación. El comando
doctor verifica instalación sin modificar estados; parámetros pendientes se muestran
separados de errores técnicos. El instalador puede instalar skills en el mismo paso.


El inicio, finalización y aprobación de etapas verifican los entregables previos y
las preguntas A1 ya aceptadas. Si cambiaron, se exige reintentar la etapa afectada;
no se propaga automáticamente una versión distinta de la aceptada. La demostración
ficticia y verificar.py no cambian estados reales ni aprueban decisiones del cliente.

La presentación de todos los resultados sigue `reglas/presentacion-resultados.md`.
Las plantillas actuales separan informe breve y respaldo verificable; esta pauta
prevalece sobre ejemplos anteriores extensos. No altera aprobaciones ni evidencia.

## Ruta unificada vigente · 8 de noviembre de 2026

Leer `reglas/ruta-unificada-estimacion.md` antes de proponer método o pedir
productividad. Tabla cargada primero; actividades O/M/P para trabajo sin cobertura
suficiente. Recuperar respuestas y parámetros locales antes de preguntar. Esta
ruta prevalece sobre instrucciones anteriores que exigían otra fuente para preparar
una propuesta; conserva aprobaciones y salidas aceptadas.
