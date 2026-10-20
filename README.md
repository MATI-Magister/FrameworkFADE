# Framework de estimación por agentes

Flujo local, trazable y sin dependencia de un proveedor de IA. Los agentes pueden
ejecutarse en Codex o en otra herramienta capaz de leer archivos y ejecutar Python.
El framework administra el flujo; el asistente de IA realiza el análisis.

## Instalación

Requiere Python 3.10 o superior. No requiere paquetes, cuenta ni clave de API.
Desde la carpeta del repositorio:

```sh
python scripts/install.py
python scripts/framework.py --project piloto status
python scripts/framework.py --project piloto serve
```

Abre http://127.0.0.1:8765. El servidor se limita a 127.0.0.1 y se detiene con Ctrl+C.
La portada es un manual con cajas seleccionables: cada etapa explica comandos,
acciones, condiciones de paso, salidas y carpetas de evidencia. Puedes copiar un
comando y ejecutarlo en el chat del agente; el portal no ejecuta agentes.

En **Mis proyectos**, cada carpeta directamente bajo `proyectos/` tiene su propia
tarjeta y flujo. Selecciona una etapa para consultar su estado y sus evidencias.
La consulta se actualiza cada 10 segundos desde los archivos locales, sin reiniciar
el servidor ni recargar toda la página. Las carpetas sin estado o con estado dañado
se distinguen de un proyecto pendiente; el portal no las modifica al consultarlas.

Usa el servidor para abrir el portal; abrir el HTML como archivo no permite consultar
la API local. Para usar otro puerto: `python scripts/framework.py serve --port 8766`.

En este chat escribe `!registrar`, `!madurez`, `!componentes`, `!clasificar`,
`!aclarar`, `!estimar`, `!revisar`, `!aprove`, `!estado` o `!tablero`.
`!dtimstr` es alias de `!estimar`. En otras herramientas proporciona
`AGENTS.md` como instrucciones del proyecto si no lo descubren automáticamente.
No hay un detector de comandos instalado dentro de otros productos: la compatibilidad
depende de que su agente siga el protocolo. Para herramientas sin terminal se necesita
un adaptador; no se incluye integración API en esta versión.

## Organización

```text
agentes/                      Fichas de registro, A1–A4, cierre y revisión
framework/                    Protocolo y motor del flujo
reglas/                       Reglas maestras versionadas y guía de definición
plantillas/                   Formato de entregables
proyectos/<id>/
  01-entradas/requerimientos/  Solicitudes y documentos originales del cliente
  01-entradas/contexto/       Arquitectura, equipo, restricciones y antecedentes
  01-entradas/respuestas/     Respuestas y aclaraciones del cliente
  02-trabajo/                 Notas y material intermedio
  03-entregables/             Resultado de cada etapa
  04-estado/                  Estado, historial y snapshots de reglas
tablero/                      Portal versionado: HTML, CSS, JavaScript y manual del flujo
scripts/                      Instalación y comandos portables
tests/                        Pruebas del flujo
```

Consulta `docs/que-compartir.md` para preparar tus insumos y `reglas/README.md`
para completar los criterios. No hay tarifas, umbrales ni factores ficticios.
A4 permanecerá bloqueado hasta que las reglas estén completas y aprobadas.

La versión vigente de reglas en revisión está en `reglas/propuesta-inicial.md`.
La base de madurez y dimensiones elegida por el usuario está en
`reglas/fuentes/Modelo_Madurez_Estimacion.xlsx`, con copia portable íntegra del
catálogo en `reglas/modelo-madurez.json`. Sustituye el borrador de seis dimensiones.
Consulta `reglas/modelo-madurez.md` para las decisiones aún pendientes.
El calculador local `scripts/madurez.py` genera preguntas y un informe legible;
no cambia etapas ni aprueba resultados. La ruta híbrida COCOMO II está documentada
en `reglas/cocomo-ii.md`; su calculador sigue pendiente de configuración/aprobación.
A2 divide en componentes estimables. El resumen del
requerimiento, los componentes y la estimación usan plantillas legibles para una
persona en `plantillas/`, separadas del estado técnico del motor.

Para preparar la evaluación de evidencia y calcularla con las rúbricas:

```sh
python scripts/madurez.py --project piloto template
python scripts/madurez.py --project piloto evaluate
```

El agente completa la plantilla técnica, cita evidencia y entrega el resumen para
personas. No usar la ficha Ejemplo del Excel como requerimiento real del piloto.

En A1 primero se preparan las preguntas para elevar N3 a N4. El experto revisa
el resumen y las preguntas y decide si continuar aclarando o autorizar componentes
con `!aprove a1`. No hay avance automático al alcanzar N4. El motor exige
`03-entregables/preguntas-a1.md` antes de registrar la aceptación.

Antes de aprobar puedes aportar documentos o respuestas y escribir `!complementar`.
El agente incorpora la información, conserva la versión previa y vuelve a evaluar
A1; el paso a componentes sigue esperando autorización del experto. El diseño de
A2 está propuesto en `reglas/a2-componentes.md`, con un ejemplo ficticio legible
en `docs/ejemplo-a2-componentes.md`.

Cada pregunta/pendiente por componente tiene código propio (`C-001-PRE-001` o
`C-001-PEN-001`). El experto puede contestar `!responder <código> <respuesta>` o
escribir código y respuesta en texto; el agente actualiza el registro local e
historial. Ver `reglas/preguntas-componentes.md`. Contestar no aprueba etapas.

La propuesta A3 está en `reglas/a3-clasificacion.md`. El ejemplo
`docs/ejemplo-a3-clasificacion.md` muestra D1–D11 de un componente con fuentes
ficticias identificadas, datos globales heredados y preguntas conservadas de A2.

La propuesta A4 está en `reglas/a4-estimacion.md`. El informe ficticio
`docs/ejemplo-a4-estimacion.md` se reproduce con `python scripts/ejemplo_a4.py`.
Este script demuestra un caso limitado y no habilita COCOMO productivo ni utiliza
datos del piloto. Incluye reconciliación de esfuerzo/costo y calendario de recursos.

La revisión final se propone en `reglas/revision-final.md`. `!ajustar <instrucción
y motivo/fuente>` reabre una revisión pendiente con historial; cambios numéricos
requieren recalcular A4 antes de otra aprobación. `!aprove revision` acepta la
versión presentada con su informe cliente y registro de ajustes; no envía documentos.
El motor rechaza la aprobación si cambió cualquiera de esos archivos, A4 o las reglas.
Ejemplos ficticios reproducibles con `python scripts/ejemplo_revision.py`:
`docs/ejemplo-revision-final.md` y `docs/ejemplo-entregable-cliente.md`.

`!nuevo nombre` crea otro expediente independiente. El portal muestra todos los
expedientes; cada uno conserva su estado e historial. Esta primera versión está
diseñada para un operador a la vez; no ejecutes escritores simultáneos.
Los documentos originales se conservan por separado de las reglas maestras.
Si no puedes leer un PDF, imagen o archivo Office en tu herramienta, solicita una
transcripción o conversión; nunca supongas su contenido.

## Verificación

El portal se utiliza **solo en local**. Su código sí se versiona; los expedientes,
credenciales, cachés, dependencias y restos de publicación externa están excluidos
por `.gitignore`. La fuente del modelo de madurez, plantillas, reglas vigentes y
ejemplos ficticios sí se incluyen porque permiten instalar, verificar y usar el framework.
Consulta `proyectos/README.md` para la organización y respaldo de expedientes.

```sh
python -m unittest discover -s tests -v
```

La batería cubre flujo/aprobaciones, madurez, cálculos ilustrativos y el portal:
proyectos independientes, carpetas sin estado, errores visibles y rutas de consulta
que no exponen documentos ni permiten modificar estados por HTTP.
