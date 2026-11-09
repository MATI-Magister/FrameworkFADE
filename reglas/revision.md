# Revisión de reglas · versión 0.3

Base indicada por el usuario: Modelo_Madurez_Estimacion.xlsx, dimensiones y modelo.
A1 debe evaluar si la información permite dimensionarlas, generar preguntas y subir
madurez con evidencia; A3 clasifica componentes en esas dimensiones. Considerar
COCOMO II para parte de la estimación. Registro: 17 de octubre de 2026.

| Parte | Estado | Decisión / pendiente |
| --- | --- | --- |
| Componentes e informes legibles | Solicitado por el usuario | Sin historias obligatorias |
| Catálogo/madurez del Excel | Base elegida por el usuario | Original y extracción conservados; sustituye propuesta 0.2 |
| Paso A1→A2 | Acordado por el usuario | Primero preguntas para elevar N3 a N4; experto decide si iterar o autorizar componentes. No avanzar por nivel automático. |
| Complementar A1 antes de aprobar | Solicitado por el usuario | !complementar incorpora nueva información y reevalúa; conserva historial y requiere nueva revisión |
| Diseño de A2 | Propuesto para revisión | Reglas, campos y ejemplo legible en a2-componentes.md; aún sin aprobación del diseño detallado |
| Códigos de preguntas/pendientes por componente | Solicitado por el usuario | PRE/PEN estables por componente, respuestas individuales, responsable, estado e historial |
| Límites y condiciones conocidas | Pendiente de acuerdo | Cinco puntos de modelo-madurez.md; no alterar rúbricas silenciosamente |
| A2/A3 | Adaptados a la base elegida | D1–D11 con valor, evidencia y pendientes |
| Diseño detallado de A3 | Propuesto para revisión | a3-clasificacion.md y ejemplo legible; aplicación local D8 explícita, sin modificar A1 |
| Cierre | Propuesto | Aclaraciones y supuestos con responsable |
| COCOMO II | Propuesto para parte del trabajo | Variante, tamaño/conversión, tablas, calibración y fases |
| Diseño detallado de A4 | Propuesto para revisión | a4-estimacion.md y ejemplo numérico reproducible ficticio; cobertura, roles, calendario y costos explícitos |
| Moneda, tarifas, equipo, costos | Pendientes | Ningún dato ficticio |
| Revisión final | Propuesta detallada para revisión | revision-final.md: ajustes AJU, recálculo, informe cliente y aprobación del paquete por versión |

Elegir una fuente no equivale a `!aprove reglas`. El paquete operativo sigue en borrador.


## 2 de noviembre de 2026 · especificaciones del ZIP

Solicitud: «validalo aqui estan la especificaciones de los agentes [...] agregalos en
nuestra configuracion actual [...] generemos de una vez skill y rolles que hagan falta».

Decisiones literales:
- «Adoptar ZIP: 9 dimensiones, 20 criterios y niveles baja/media/alta».
- «Evaluar horas por proceso como método principal».
- «Dejemos estos valores en el archivo de configuracion que te menciono».
- «Diez preguntas al cliente por ronda, como en el ZIP».

Se activa B.1 para A1 nuevo; se conserva el Excel como referencia histórica y de
clasificación. No se migran evaluaciones ni se reabren etapas por esta actualización.
Se centralizan parámetros en configuracion/framework.json. Valores económicos y
capacidad sin cifras confirmadas: null/listas vacías. Los factores ilustrativos no
se adoptan. Horas por proceso es dirección de evaluación, no aprobación productiva.

Roles y skills se mapean por responsabilidad conservando los IDs de etapas/comandos.
Las incompatibilidades restantes están registradas como INC-001…INC-015 en
integracion-agentes.md. !aprender prepara un cierre posterior a ejecución; no es
!aclarar ni autoriza registrar catálogos. La aprobación del paquete de reglas y la
aprobación del requerimiento/estimación del piloto siguen pendientes.


### Resolución de INC-005 e INC-006 · 2 de noviembre de 2026

- INC-005: «Dejar por confirmar y preguntar al experto». Se conserva lo desconocido
  sin puntaje de complejidad ni nivel tecnológico inferido; registrar PRE/PEN para
  que el experto aporte evidencia. No usar automáticamente los defaults del ZIP.
- INC-006: «Conservar Base y Conservador; optimista solo como referencia».
  Los dos escenarios formales se mantienen. El optimista no es un tercer escenario
  comprometido ni reemplaza el conservador. Las bandas/factores numéricos siguen
  pendientes de calibración y aprobación.

Estas decisiones resuelven ambas políticas; no aprueban las reglas completas ni
una etapa o estimación de un expediente.


### Resolución de INC-007 · 2 de noviembre de 2026

Instrucción del usuario: «el experto decide, tu nisiquiera debes tener registro de
las sesiones necesarias, solo generar lñas preguntas para resolver los puntos pendientes».

Se elimina el parámetro de sesiones. No registrar, estimar, contar o limitar las
sesiones necesarias ni derivar una propuesta preliminar por haber agotado sesiones.
El agente identifica brechas y genera preguntas para resolver los pendientes;
el experto decide cuándo la información permite avanzar mediante aprobación explícita.
Las fuentes, respuestas y versiones se conservan como evidencia del requerimiento,
sin convertirlas en un registro de sesiones necesarias. Los contadores del ZIP no
se adoptan. No cambia el límite acordado de diez preguntas al cliente por ronda.


### Cierre técnico de la integración · 2 de noviembre de 2026

El usuario indicó: «Listo, no te detengas, ya terminaste de implementar todo?».
Se completan mecanismos técnicos sin aprobar valores: instalación unificada con
skills opcionales, comprobación doctor, esfuerzo/costo/calendario por componentes,
modo de cálculo desde snapshot aprobado y verificación de insumos/resultados antes
de finish A4 y revisión final. Se congela también el catálogo de clasificación.
Se agrega preparación reproducible del cierre con línea base aprobada y horas reales.

Se mantienen por confirmar cifras de negocio/calibración y las decisiones abiertas
INC-008, INC-010 e INC-014. La implementación no convierte esas decisiones en
aprobaciones. No se activa el registro corporativo ni las condiciones comerciales
del ZIP, y no se ejecuta ninguna etapa real del piloto durante las pruebas.


### Resolución de INC-008, INC-010 e INC-014 · 2 de noviembre de 2026

- INC-008: «Usar Validado / Definido / Supuesto, como en el ZIP».
  Se adopta para definición de cada componente, gobernada por el proceso con menor
  sustento. Es distinta de baja/media/alta de A1 y no multiplica el esfuerzo.
- INC-010: «Confirmación directa y explícita del cliente, escrita o en una
  transcripción identificada». Exigir fuente, ubicación, cita y hablante del cliente
  identificado cuando sea transcripción; un relato interno no confirma un dato.
- INC-014: «Costo horario único del equipo». Configuración inicial costo_unico,
  con importe y moneda todavía por confirmar. No sumar tarifas por rol encima;
  conservar roles y capacidad para repartir esfuerzo y planificar duración.

Estas decisiones actualizan reglas y parámetros; no constituyen aprobación del
paquete de reglas completo ni aprobación de un requerimiento o estimación.


Hallazgo adicional INC-016: las etiquetas R1–R4 de reúso tienen sentido inverso y
cortes diferentes en Excel y ZIP. Se registra para decisión del experto; mientras
tanto conservar porcentajes/activos y no reutilizar clases entre ambas escalas.
No se adopta automáticamente una escala ni se cambia ningún factor aprobado.


### Resolución de INC-016 · 2 de noviembre de 2026

Respuesta del usuario: «Usar ZIP: R1 <10 %, R2 10–<30 %, R3 30–50 %, R4 >50 %».
La escala activa queda parametrizada en classification.reuse de la configuración.
10 % corresponde a R2; 30 % y 50 % a R3; solo >50 % a R4. El dato desconocido
no se clasifica como cero. El cálculo verifica coherencia entre porcentaje y clase;
no importa etiquetas antiguas del Excel sin reclasificar a partir de su porcentaje.
La decisión no aprueba factores de ahorro, calibración ni el paquete de reglas.


### Verificación final del desarrollo · 2 de noviembre de 2026

El usuario indicó: «Adelante, te dije que no te detengas hasta que termines».
Se completa la verificación de instalación limpia, skills y flujo numérico,
protección de entregables aceptados y demostración reproducible. Los parámetros
reales y la calibración se mantienen por confirmar, sin bloquear el desarrollo
ni convertir la orden de terminar en aprobación de reglas o del piloto.


## 8 de noviembre de 2026 · ruta unificada para todos los proyectos

Instrucción literal: «Listo, implementa esa ruta unificada para todos los proyectos, usando la tabla que cargué y el método por actividades para los faltantes, sin volver a pedirme información que ya tenemos».

Se activa el uso de la tabla y parámetros técnicos del archivo cargado como referencia inicial, con fuente y huella; no se importan sus valores económicos ni de equipo. Trabajo sin cobertura suficiente usa actividades O/M/P propuestas con fundamento. Se consultan primero las fuentes vigentes del expediente y se consolidan parámetros locales sin copiar datos de otros proyectos. Esta decisión no es calibración ni aprobación automática de rangos, reglas completas o etapas. No se recalculan salidas aceptadas. Detalle operativo: reglas/ruta-unificada-estimacion.md.


## 9 de noviembre de 2026 · cotización por paquetes

Decisión del usuario. «Listo, implementa los tres primeros cambios para todos los proyectos: filtra las preguntas de cotización, usa supuestos con límites claros y estima por paquetes usando la tabla cargada y actividades para los faltantes.»

El filtro se aplica antes de presentar preguntas. Las partidas de cotización registran cantidad, supuesto, límite y condición de recotización. El cálculo distingue trabajo común de trabajo por unidad.


### Preguntas de cotización sin tope

El usuario pidió «eliminemola y que genere las preguntas que considere necesarias». Esta decisión sustituye el límite anterior de diez. Aplicar el filtro de cotización y conservar la priorización.
