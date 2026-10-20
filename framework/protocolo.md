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

A1 usa las rúbricas de `reglas/modelo-madurez.json` para evaluar información con
la que caracterizar D1–D11 y generar preguntas. A3 caracteriza componentes con esas
dimensiones. El nivel no es esfuerzo ni aceptación automática. Antes de aceptar A1
se exige `preguntas-a1.md` con preguntas orientadas de N3 hacia N4. El experto
decide si continuar aclarando o autorizar componentes; el nivel no dispara el paso.
La aprobación conserva la huella del resumen y de las preguntas. El snapshot incorpora el
catálogo completo: cambiarlo invalida la aprobación previa. Riesgos van aparte.
COCOMO II es una ruta propuesta para parte del trabajo: ver `reglas/cocomo-ii.md`.
No hay calculador COCOMO habilitado ni se suma a otro método de igual cobertura.

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
