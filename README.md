# FADE · Framework de estimación por agentes

Flujo local y trazable, independiente del proveedor de IA. El asistente interpreta
los comandos y realiza el análisis; Python controla etapas, historial y aprobaciones.
Los informes del requerimiento, componentes y estimación son legibles en Markdown.

Cada paso presenta primero su resultado, lo que requiere tu atención y la siguiente
acción. Los criterios, fuentes y cálculos quedan en un respaldo enlazado, sin repetir
todo el expediente. Consulta el [ejemplo de resultados breves](docs/ejemplo-resultados-breves.md)
y la [pauta de presentación](reglas/presentacion-resultados.md).

## Instalación paso a paso · independiente de la IA

FADE se instala como una carpeta local. Puedes cambiar de asistente sin cambiar
los expedientes, reglas ni scripts. La instalación del framework no configura un
proveedor de IA ni hace llamadas a sus servicios.

### 1. Preparar el equipo y elegir cómo usar la IA

Necesitas:

- **Python 3.10 o superior**, disponible en la terminal.
- **Git**, si vas a clonar el repositorio. También puedes descargarlo como ZIP y
  descomprimirlo; Git no es necesario para ejecutar esa copia.
- Un asistente capaz de **leer y editar archivos locales y ejecutar comandos** en
  la carpeta del framework, para operar el flujo desde su chat.
- Un navegador para consultar el tablero local.

Comprueba Python y, si lo utilizarás, Git:

```sh
python --version
git --version
```

Los ejemplos usan `python`. Si tu equipo lo identifica como `python3` o `py`, usa
ese comando en su lugar en todos los pasos. El flujo principal utiliza la biblioteca
estándar de Python: no requiere `pip install`, entorno virtual ni claves de API.
Las herramientas archivadas en `referencias/` no forman parte de esa instalación.

Si tu IA solo dispone de chat y no puede operar archivos o terminal, puedes usarla
como apoyo: tú ejecutas los comandos y compartes los insumos/resultados necesarios.
En esa modalidad los comandos del chat no se ejecutan automáticamente. La lectura
de adjuntos depende de la herramienta; aporta una conversión legible si hace falta.

### 2. Obtener el framework

Desde la terminal, en la carpeta donde guardarás la instalación:

```sh
git clone https://github.com/MATI-Magister/FrameworkFADE.git
cd FrameworkFADE
```

Si descargaste el ZIP, descomprímelo y abre la terminal en la carpeta extraída.
La **raíz** es la carpeta donde están `README.md`, `AGENTS.md`, `scripts/` y
`configuracion/`. Ejecuta todos los comandos siguientes desde esa carpeta.

### 3. Ejecutar la instalación local

```sh
python scripts/install.py
```

El instalador:

- Valida la configuración y los recursos de roles y skills.
- Crea el expediente `piloto`, que es el proyecto predeterminado inicial.
- Crea catálogos vacíos de activos, tecnologías y proyectos en `datos-locales/`.
- Conserva los expedientes y catálogos que ya existan.

Puedes volver a ejecutarlo. Si necesitas otro proyecto predeterminado, cambia
`operation.default_project` en `configuracion/framework.json` antes de instalar.
No se ejecutan agentes, estimaciones ni aprobaciones durante la instalación.

### 4. Comprobar la instalación

```sh
python scripts/framework.py doctor
python scripts/framework.py --project piloto status
```

Sustituye `piloto` si elegiste otro identificador. El diagnóstico distingue
**instalación técnica correcta** de **valores pendientes para estimar**. Es normal
que una instalación nueva indique moneda, costo horario, equipo y factores por
confirmar: puedes preparar requerimientos y trabajar sus aclaraciones antes de
completar esos valores.

Para ejecutar también la batería de pruebas:

```sh
python scripts/verificar.py
```

### 5. Conectar el asistente de IA que prefieras

Abre la carpeta raíz como proyecto o espacio de trabajo en tu herramienta de IA.
Permite que el asistente lea y edite esa carpeta y ejecute Python. El framework no
necesita acceso a correo, servicios externos ni credenciales de un proveedor.

Si la herramienta reconoce `AGENTS.md`, úsalo como instrucciones del proyecto.
Si no lo descubre automáticamente, indícale que lo lea o incorpora su contenido
en el mecanismo de instrucciones que ofrezca. Puedes comenzar con este mensaje:

```text
Trabaja desde la raíz de este repositorio. Lee AGENTS.md, README.md y
framework/protocolo.md antes de operar. Usa el proyecto piloto en este chat.
Interpreta los comandos definidos en AGENTS.md y ejecuta sus acciones locales.
Consulta el estado antes de operar y respeta las aprobaciones humanas del flujo.
```

Cambia `piloto` por tu proyecto si corresponde. Después escribe en el **chat del
asistente**, no en la terminal:

```text
!estado
!roles
```

Debes obtener el estado real del expediente y el mapa de responsabilidades.
Los comandos `!…` son una convención que interpreta el asistente. No hay un servicio
de escucha instalado: el asistente consulta las instrucciones y utiliza el motor
Python. El mismo asistente puede asumir los diferentes roles; no necesita soporte
nativo de subagentes ni un SDK específico.

### 6. Instalar skills en la herramienta, si las admite (opcional)

Este paso solo aplica si tu herramienta reconoce paquetes `SKILL.md` y ofrece un
directorio donde instalarlos. Usa el directorio que indique esa herramienta:

```sh
python scripts/install.py --skills-target "DIRECTORIO_DE_SKILLS"
```

Reemplaza `DIRECTORIO_DE_SKILLS` por la ruta real; las comillas permiten rutas con
espacios. El comando reúne la instalación del framework y sus once skills.
Si el framework ya está instalado, conserva sus datos e instala los adaptadores.

Las skills apuntan a esta copia del framework y consultan sus reglas centrales.
El instalador protege skills ajenas o modificadas; no las reemplaza por fuerza.
Si mueves la instalación, crea los adaptadores en un directorio libre y configura
su descubrimiento en la herramienta. La detección o recarga depende del asistente
que utilices. Si no admite skills, opera mediante `AGENTS.md` como en el paso 5.

### 7. Levantar el tablero local

En una terminal situada en la raíz:

```sh
python scripts/framework.py serve
```

Abre **http://127.0.0.1:8765/** en tu navegador y mantén esa terminal abierta.
Detén el servidor con `Ctrl+C`. Si configuraste otro puerto, usa la dirección que
imprime el servidor. Para seleccionar uno al iniciar:

```sh
python scripts/framework.py serve --port 8766
```

La portada muestra el manual del flujo en cajas seleccionables. **Mis proyectos**
consulta las carpetas de `proyectos/` cada diez segundos y muestra estado, progreso
y rutas de evidencia. El portal es de consulta: copiar un comando no lo ejecuta.
Usa la dirección HTTP del servidor para consultar proyectos; abrir el HTML como
archivo no permite usar la API local. El servidor escucha solo en `127.0.0.1` y
no expone los documentos originales por HTTP.

### 8. Preparar el primer requerimiento

Puedes usar `piloto` o crear un expediente independiente desde el chat:

```text
!nuevo mi-proyecto
```

Indica al asistente que use `mi-proyecto` en ese chat. La alternativa en terminal es:

```sh
python scripts/framework.py init mi-proyecto
```

Guarda los documentos en la carpeta del proyecto elegido:

| Carpeta dentro de `proyectos/<id>/` | Qué colocar |
| --- | --- |
| `01-entradas/requerimientos/` | Solicitud y documentos originales del cliente |
| `01-entradas/contexto/` | Sistemas existentes, restricciones, equipo y antecedentes |
| `01-entradas/respuestas/` | Respuestas y aclaraciones con sus fuentes |

Después, en el chat del asistente:

```text
!registrar
!madurez
```

Ejecuta un comando cada vez y revisa su resultado. El asistente debe leer las fuentes,
producir el resumen y generar preguntas. Cuando hayas revisado A1, `!aprove a1`
autoriza pasar a `!componentes`. El resto del flujo está descrito más abajo y en
el manual del tablero. Si falta información, el agente identifica el pendiente.

### 9. Completar los parámetros antes de una estimación real

La ruta común ya tiene la **tabla técnica cargada**: aplicaciones 40, integración
60, datos/IA 70, plataforma 50, seguridad 60 y modernización 50 horas por proceso.
Para partidas sin cobertura suficiente se usa estimación por actividades O/M/P.
Son referencias iniciales para revisión, sin afirmar calibración histórica. El
agente consulta primero las respuestas y decisiones del expediente; no pide otra
tabla de productividad para preparar la propuesta.

```sh
python scripts/framework.py --project mi-proyecto estimation-route
```

Este comando muestra la ruta, los parámetros consolidados y dónde buscar los
datos existentes. Los valores particulares se consolidan con fuente en
`proyectos/<id>/01-entradas/respuestas/parametros-estimacion.json`; se aplican solo
a ese expediente y quedan en su snapshot. Consulta la
[ruta unificada](reglas/ruta-unificada-estimacion.md) para cobertura, rangos,
gestión y separación entre propuesta y cálculo formal aprobado.

Edita `configuracion/framework.json`, con apoyo del asistente si lo deseas:

| Apartado | Qué definir |
| --- | --- |
| `operation` | Proyecto predeterminado, puerto y preguntas por ronda |
| `estimation.currency` y `cost_per_hour` | Moneda y costo horario único real del equipo |
| `estimation.team` | Roles, personas, horas disponibles, dedicación y fuente |
| `estimation.process_method` | Revisar tabla, factores, gestión y bandas ya cargados; calibrar con evidencia cuando exista |
| Parámetros comerciales, si aplican | Decisiones de costos adicionales y condiciones con sus fuentes |

`null` significa **por confirmar**, nunca cero. Las escalas elegidas y las políticas
vigentes ya están configuradas. Los datos ilustrativos no se adoptan como valores
reales. Consulta `configuracion/README.md` y registra las decisiones en
`reglas/revision.md`. La aprobación del paquete de reglas es una acción explícita
separada de la instalación; el asistente guía su revisión antes de `!aprove reglas`.

Para consultar y validar la configuración:

```sh
python scripts/framework.py config
```

A4 exige parámetros completos y reglas aprobadas para el expediente. Instalar o
abrir el tablero no concede esa aprobación.

### 10. Probar el cálculo sin datos del cliente (opcional)

```sh
python scripts/demo_procesos.py
```

El comando imprime la ruta de un informe Markdown en `insumos-locales/demo-procesos/`.
Ábrelo para ver Base y Conservador con esfuerzo, costo y calendario por componente.
Usa datos y moneda ficticios, sin modificar configuración, expedientes ni aprobaciones.

### Problemas frecuentes de instalación

| Situación | Qué hacer |
| --- | --- |
| `python` no se reconoce | Comprueba la instalación de Python y prueba `python3` o `py`; utiliza el comando disponible en todos los pasos. |
| No encuentra `scripts/install.py` | Abre la terminal en la raíz donde están `README.md` y `AGENTS.md`. |
| El asistente responde a `!estado` sin consultar archivos | Pídele leer `AGENTS.md` y comprobar acceso a archivos y terminal; sin esas capacidades el operador debe ejecutar las acciones locales. |
| El tablero no responde | Inicia `serve`, mantén la terminal abierta y abre la dirección que imprime. Si el puerto está ocupado, selecciona otro. |
| Las skills no aparecen | Comprueba el directorio y mecanismo de recarga de tu herramienta; puedes seguir usando `AGENTS.md`. |
| El diagnóstico muestra parámetros pendientes | Completa los valores reales y revisa las reglas; no es necesario reinstalar ni rellenar cifras ficticias. |

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
9 dimensiones, información baja/media/alta. Preguntas necesarias sin tope por ronda.
Preguntas internas y contradicciones se registran aparte. D9 y D11 alimentan experiencia.
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

Las once skills están en `skills/` y `AGENTS.md` indica cuáles corresponden a cada
etapa. Su instalación opcional en otra herramienta se explica en el paso 6. Los
adaptadores consultan esta instalación para mantener una sola fuente de reglas.

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


## Integridad de resultados y distribución

Las etapas posteriores comprueban las huellas de entregables previos: editar un
resultado aceptado exige reintentar esa etapa antes de continuar. El material binario
no usado del ZIP se conserva localmente, excluido de Git; el manifiesto distingue
archivos distribuidos y material archivado. Las especificaciones y el catálogo
necesarios para instalar y operar sí forman parte de la distribución.
