# FADE · Framework de estimación por agentes

Flujo local y trazable, independiente del proveedor de IA. El asistente interpreta
los comandos y realiza el análisis; Python controla etapas, historial y aprobaciones.
Los informes del requerimiento, componentes y estimación son legibles en Markdown.

## Instalar y abrir

Requiere Python 3.10 o superior. El flujo principal no requiere paquetes externos
ni claves de API. Desde la raíz:

```sh
python scripts/install.py
python scripts/framework.py --project piloto status
python scripts/framework.py doctor
python scripts/framework.py serve
```

Abrir http://127.0.0.1:8765/. El servidor escucha solo en 127.0.0.1. La portada es
un manual con etapas seleccionables; Mis proyectos consulta cada carpeta de
proyectos/ cada diez segundos, con progreso, estado y rutas de evidencia. El portal
es de consulta; copiar un comando no lo ejecuta. Los documentos no se sirven por HTTP.

## Flujo y comandos

Registro → A1 información → A2 componentes → A3 clasificación → aclaraciones
condicionales → A4 estimación → revisión final.

!nuevo <id>, !registrar, !madurez, !complementar <fuentes>, !componentes,
!responder <código> <respuesta>, !clasificar, !aclarar, !estimar (alias !dtimstr),
!revisar, !ajustar <instrucción y motivo>, !estado, !tablero.

!aprove a1 autoriza componentes tras revisar resumen y preguntas; !aprove revision
acepta una versión del paquete. !aprove reglas es otra decisión explícita. Ningún
nivel permite saltar aprobaciones. !run ejecuta una sola etapa. Leer AGENTS.md.

Desde el 2026-11-02, por elección del usuario, A1 usa B.1 del ZIP: 20 criterios,
9 dimensiones, información baja/media/alta. Hasta diez preguntas al cliente por
ronda; preguntas internas y contradicciones aparte. D9 y D11 alimentan experiencia.
El Excel anterior se conserva para clasificación y trazabilidad, sin migrar puntajes.

```sh
python scripts/madurez.py --project piloto template
python scripts/madurez.py --project piloto evaluate
```

El agente completa evidencia, revisa fuentes, produce el resumen y presenta preguntas.
Estos comandos no finalizan A1 ni aprueban nada. La unidad es componente estimable,
no historia; PRE/PEN tienen códigos estables para responder individualmente.

## Roles, skills y parámetros

configuracion/framework.json centraliza operación, moneda, tarifas/costo, capacidad,
margen y parámetros del método. null significa por confirmar. Los valores ilustrativos
del ZIP no se usan por defecto. Los parámetros de negocio se congelan con las reglas
A4; cambiarlos requiere revisar y aprobar otra vez.

```sh
python scripts/framework.py config
python scripts/framework.py roles
```

También puedes consultar !configuracion y !roles en el chat. configuracion/roles.json
mapea once responsabilidades y sus skills en skills/. El mismo asistente puede
asumirlas; el motor no inicia procesos IA independientes. El mapa conecta números
A1–A7 del ZIP con las siete etapas existentes sin renumerar expedientes.

Las skills están preparadas en el repositorio y AGENTS.md las enruta. Si tu herramienta
requiere instalarlas en su directorio de descubrimiento, usa su ruta elegida:

```sh
python scripts/install.py --skills-target <directorio-de-skills-de-tu-herramienta>
```

El instalador genera un adaptador que apunta a esta instalación; no copia ni duplica
reglas o expedientes, y protege skills ajenas/modificadas. Cambiar de equipo requiere
reinstalar el adaptador. El soporte de descubrimiento depende de la herramienta;
para agentes sin skills, basta seguir AGENTS.md desde este repositorio.

Horas por proceso se evalúa como método principal. El motor calcula esfuerzo, costo y calendario por componente con capacidad y dependencias.
Falta calibrar y aprobar factores, bandas y datos reales; A4 real permanece bloqueado
hasta completar esos valores. scripts/estimar_procesos.py distingue --experimental
de --approved; este último exige un intento A4 iniciado y lee su snapshot aprobado.
Conserva entrada, resultado e informe con huellas; no finaliza ni aprueba la etapa. COCOMO II queda como alternativa.
Consultar reglas/horas-por-proceso.md y reglas/integracion-agentes.md, donde figuran
las contradicciones INC-001…INC-016 y decisiones pendientes para revisar por partes.

!aprender prepara un informe posterior a la ejecución real del proyecto. Usa horas,
cambios aprobados y notas de cierre; no es !aclarar. scripts/aprendizaje.py prepara el cálculo y el informe con una línea base aprobada,
horas reales y cambios autorizados. El líder debe confirmar antes de actualizar
catálogos o recalibrar; el registro corporativo automático no está activado.

## Carpetas

| Carpeta | Contenido |
| --- | --- |
| agentes/, roles/, skills/ | Etapas, responsabilidades y capacidades reutilizables |
| configuracion/ | Parámetros compartidos y mapa de roles |
| reglas/ | Modelo activo, método y decisiones con fuentes |
| plantillas/ | Entregables legibles |
| proyectos/<id>/01-entradas/ | Requerimientos, contexto y respuestas del cliente |
| proyectos/<id>/02-trabajo/ | Fichas, evaluaciones, cálculos y aprendizaje |
| proyectos/<id>/03-entregables/ | Informes de etapas y paquete para revisión |
| proyectos/<id>/04-estado/ | Estado, historial y snapshots |
| datos-locales/ | Activos, tecnologías e historia reales, excluidos de Git |
| referencias/onedrive-2026-11-02/ | Especificaciones, esquemas y herramientas originales como referencia |
| insumos-locales/ | ZIP y casos recibidos, excluidos de Git |
| tablero/, framework/, scripts/, tests/ | Portal, motor, comandos y verificación |

Las herramientas originales del ZIP no son el motor activo: tienen IDs, fórmulas,
dependencias y condiciones comerciales que deben adaptarse. No se ejecutan por
cargar una referencia. Los ejemplos anteriores de docs/ y ejemplos/ son ficticios
e históricos; no representan una estimación ni parámetros de un cliente.

Versionar fuentes del portal y del framework, nunca expedientes, catálogos reales,
credenciales o publicación cancelada. Consultar .gitignore. Respaldar datos locales
por separado. Un operador a la vez; no ejecutar escritores simultáneos.

## Verificar

```sh
python -m unittest discover -s tests -v
```

La validación automática comprueba operaciones y estructura; el experto verifica
la fidelidad de fuentes, la metodología y las decisiones. Aprobar no envía documentos.


Decisiones vigentes: los componentes usan Validado/Definido/Supuesto, con su proceso
más débil como fundamento; la confirmación procede directamente del cliente, por
escrito o en transcripción con hablante identificado. El costo inicial es horario
único del equipo, con valor y moneda aún por confirmar. La escala de reutilización elegida es la del ZIP (INC-016): R1 <10 %, R2 10–<30 %,
R3 30–50 %, R4 >50 %. Los factores numéricos requieren calibración por separado.


## Comprobar y ver una demostración

```sh
python scripts/verificar.py
python scripts/demo_procesos.py
```

verificar.py reúne diagnóstico y pruebas. demo_procesos.py genera un informe
legible con datos ficticios reproducibles en insumos-locales/demo-procesos/,
sin modificar configuración, expedientes ni aprobaciones. Usa moneda ficticia DEM;
los valores del ejemplo nunca se convierten en defaults. El informe muestra Base
y Conservador con esfuerzo, costo, capacidad y dependencias explícitas.

Las etapas posteriores comprueban las huellas de entregables previos: editar un
resultado aceptado exige reintentar esa etapa antes de continuar. El material binario
no usado del ZIP se conserva localmente, excluido de Git; el manifiesto distingue
archivos distribuidos y material archivado. Las especificaciones y el catálogo
necesarios para instalar y operar sí forman parte de la distribución.
