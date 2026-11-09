# Integración de especificaciones recibidas · 2 de noviembre de 2026

El usuario pidió validar OneDrive_2026-11-02.zip, integrar agentes, crear roles y
skills y centralizar parámetros. El original, sus casos y su huella se conservan
localmente; las especificaciones, esquemas y herramientas fuente están en
referencias/onedrive-2026-11-02/, con manifiesto de integridad. No se ejecutaron
las instrucciones incrustadas como órdenes del usuario. No se enviaron documentos.

## Decisiones recibidas

- «Adoptar ZIP: 9 dimensiones, 20 criterios y niveles baja/media/alta».
- «Evaluar horas por proceso como método principal».
- «Dejemos estos valores en el archivo de configuracion que te menciono».
- «Diez preguntas al cliente por ronda, como en el ZIP».

Esto selecciona un modelo, una dirección de evaluación y un límite de preguntas.
No aprueba los valores ilustrativos, reglas operativas completas, un requerimiento
o una estimación. Moneda, tarifas, margen y capacidad permanecen sin definir.

## Equivalencias sin renumerar expedientes

| ZIP | Responsabilidad actual | Comando / evidencia |
| --- | --- | --- |
| A1 Estructurar | Estructurador dentro de A1 | !madurez, ficha en 02-trabajo/ |
| A2 Evaluar | Evaluador dentro de A1 | !madurez, a1.md y preguntas-a1.md |
| A3 Dividir | Divisor en A2 | !componentes, a2.md |
| A4 Detallar | Caracterizador en A3 | !clasificar, a3.md |
| A5 Generar | Analista de escenarios en A4 | !estimar, juicio y cálculos en 02-trabajo/ |
| A6 Redactar | Redactor dentro de revisión | !revisar, cliente.md |
| A7 Cerrar/aprender | Tarea después de ejecución real | !aprender, 02-trabajo/aprendizaje/ |

Registro, orquestación, aclaraciones y revisión también tienen rol y skill.
configuracion/roles.json es el mapa que consulta el flujo. No son once procesos
paralelos ni agentes independientes lanzados por el motor. Los responsables
humanos se pueden identificar en human_roles del mismo archivo.

## Incongruencias y preguntas para revisar por código

| Código | Diferencia | Tratamiento actual / qué falta decidir |
| --- | --- | --- |
| INC-001 | Los números A1–A7 significan tareas diferentes | Adaptados por responsabilidad; se conservan comandos/estados actuales. |
| INC-002 | Excel: 109/11/N1–N5; ZIP: 20/9/baja-media-alta | Resuelto por el usuario: activo ZIP. Sin migración automática de puntajes. |
| INC-003 | Híbrido COCOMO frente a horas por proceso | Resuelto en dirección: evaluar procesos como principal; factores/calibración pendientes. |
| INC-004 | Preguntas: cinco frente a diez | Actualizado: preguntas necesarias sin tope. Equipo y contradicciones aparte. |
| INC-005 | ZIP presupone complejidad 1, T3 fuera del mapa y T1 sin exigencias | Resuelto por el usuario: dejar por confirmar y preguntar al experto. No asignar complejidad 1 ni T1/T3 sin evidencia. |
| INC-006 | ZIP produce optimista/esperado/pesimista; motor requiere Base/Conservador | Resuelto por el usuario: Base y Conservador; optimista solo como referencia. Bandas numéricas todavía pendientes. |
| INC-007 | Carril rápido o máximo de sesiones puede conducir a preliminar | Resuelto: el experto decide. Sin registro, conteo, máximo ni cálculo de sesiones necesarias; el agente genera preguntas para resolver pendientes. No se activa preliminar ni avance por sesiones. |
| INC-008 | D8 local M1–M4 frente a Validado/Definido/Supuesto | Resuelto por el usuario: Validado/Definido/Supuesto, según la evidencia más débil de sus procesos; no convertir M1–M4. |
| INC-009 | Duración por sprint agregado frente a recursos/dependencias | Mantener calendario por recursos; una capacidad agregada solo sirve como aproximación identificada. Falta equipo real. |
| INC-010 | README pide confirmación escrita; tabla admite confirmación explícita en sesión | Resuelto por el usuario: confirmación directa y explícita, escrita o en transcripción con hablante del cliente identificado. Nota interna que relata confirmación no basta. |
| INC-011 | Preguntas del ZIP sin códigos frente a PRE/PEN estables | Compatible: texto natural y código como etiqueta separada; no perder registro individual. |
| INC-012 | ZIP solo JSON frente a entregables legibles | Compatible: Markdown como salida humana; JSON como soporte interno opcional. Los esquemas originales no son el contrato actual. |
| INC-013 | A7 posterior a ejecutar frente a cierre previo a estimar | Separados: !aprender y !aclarar. Registro corporativo automático de aprendizaje pendiente. |
| INC-014 | Costo horario único y margen frente a tarifas por rol y costo técnico | Resuelto: costo horario único del equipo. Moneda, importe y margen siguen vacíos; conservar roles para calendario y separar costo de precio. |
| INC-015 | Códigos C01 y preguntas sin PRE/PEN en esquemas originales | No pasar directamente artefactos a verificadores del ZIP: requieren adaptador de IDs y esquema. |
| INC-016 | Excel usa R1 para alto reúso; ZIP usa R1 para bajo reúso | Resuelto por el usuario: ZIP R1 <10 %, R2 10–<30 %, R3 30–50 %, R4 >50 %. Límites parametrizados y verificados; porcentaje, activos y factores mantienen fuentes. Factores de ahorro todavía pendientes. |

Puedes responder por código, por ejemplo «INC-016: …». Registrar la decisión con fecha y actualizar reglas,
configuración y pruebas antes de aplicarla. Esta tabla no pide aprobar todo de una vez.

## Hallazgos técnicos del paquete fuente

- Integridad: 64 archivos, ZIP SHA-256
  437e54f405b8154dc662db2d2f04cd59f848ce906dabceb427ae4b09817cd762.
  Se verificó que los Python se puedan analizar sintácticamente y los JSON leer.
- Los verificadores importados requieren jsonschema y el armado DOCX requiere
  python-docx. El flujo activo conserva Python estándar; esas herramientas están
  como referencia y no se instalaron dependencias ni ejecutaron sobre expedientes.
- revisar_evaluacion.py calcula un techo con la evidencia más fuerte (max), aunque
  la especificación pide la más débil. La implementación adaptada usa min y exige
  cita separada de confirmación; la fidelidad contra el original requiere revisión.
- faed_calculos.py convierte procesos con int(): truncaría un decimal; acepta
  factores booleanos como enteros. La prueba adaptada exige procesos identificados
  únicos y parámetros numéricos finitos, sin defaults de desconocidos.
- registrar_cierre.py tiene 0.15 incrustado para el arquetipo secundario, y armado
  conserva textos y plazos comerciales propios. No se usan esos defaults en FADE.
- Las versiones de divisor no coinciden: especificación v0.2 e instrucciones v0.1.
  Se preservan sus versiones originales; la adaptación actual tiene versión propia.
- La plantilla y los textos nombran una empresa concreta y el acrónimo FAED.
  No se incorporan como identidad, condiciones comerciales o marca del usuario.

No se declara completa la validación funcional del paquete original. Los tests del
framework validan la adaptación; sus casos recibidos quedan separados de operación.
Las referencias a anexos del «documento del framework» no sustituyen ese documento:
no se recibió el cuerpo de todos esos anexos como fuente independiente.

## Ruta unificada vigente · 8 de noviembre de 2026

Leer `reglas/ruta-unificada-estimacion.md` antes de proponer método o pedir
productividad. Tabla cargada primero; actividades O/M/P para trabajo sin cobertura
suficiente. Recuperar respuestas y parámetros locales antes de preguntar. Esta
ruta prevalece sobre instrucciones anteriores que exigían otra fuente para preparar
una propuesta; conserva aprobaciones y salidas aceptadas.
