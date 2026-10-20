# Ejemplo de resultado A2 · Portal de solicitudes de soporte

**Ejemplo ficticio para revisar el formato. No es un requerimiento del piloto.**

## Requerimiento de partida del ejemplo

«Necesitamos un portal donde los clientes registren solicitudes de soporte con
archivos adjuntos y consulten su estado. Los analistas deben revisar las solicitudes,
asignarlas y actualizar su estado. El cliente debe recibir un correo cuando cambie
el estado. Se utilizará el servicio de autenticación corporativa existente.
No se requieren chat ni pagos».

Para este ejemplo se supone que ese texto ya pasó la revisión de A1 y que el experto
autorizó trabajar con los pendientes identificados. No se inventan sus respuestas.

## Cómo dividimos la solución

Identificamos cinco componentes: recibir solicitudes, gestionarlas, permitir al
cliente consultarlas, comunicar cambios y conectar el acceso corporativo. La
separación distingue propósitos y dependencias; cada componente puede contener
pantallas, reglas y datos necesarios para cumplir su propósito.

El acceso corporativo se registra una sola vez como trabajo compartido. Los otros
componentes lo utilizan y no vuelven a incluir su implementación. Esta es la lista
de unidades que se clasificarán en A3; todavía no se asignan horas ni costos.

## Vista general

| Código | Componente | Para qué sirve | Resultado esperado | Dependencias |
| --- | --- | --- | --- | --- |
| C-001 | Registro de solicitudes | Recibir el caso y sus archivos | Solicitud guardada y disponible para atención | C-005 |
| C-002 | Gestión de solicitudes | Organizar y actualizar la atención | Solicitudes revisadas, asignadas y con estado actualizado | C-001, C-005 |
| C-003 | Consulta de solicitudes | Informar al cliente sobre sus casos | Consulta del estado de sus solicitudes | C-001, C-002, C-005 |
| C-004 | Avisos por correo | Comunicar cambios de estado | Aviso enviado al destinatario correspondiente | C-002 y servicio de correo por confirmar |
| C-005 | Acceso corporativo | Usar la autenticación existente | Clientes y analistas acceden con su identidad reconocida | Servicio corporativo existente |

## C-001 · Registro de solicitudes

El cliente registra un caso de soporte y adjunta archivos para explicar su necesidad.
La solicitud queda disponible para que los analistas la atiendan.

**Personas involucradas:** clientes que necesitan soporte.

**Incluye:** captura de la información de la solicitud, incorporación de archivos y
guardado del caso. Los campos y las validaciones específicas están por confirmar.

**No incluye:** asignar analistas ni actualizar estados, cubiertos por C-002.

**Resultado esperado:** una solicitud registrada con su información y archivos.

**Dependencias:** C-005 reconoce la identidad del cliente.

**Supuestos y pendientes:** confirmar campos obligatorios, tipos/tamaño de archivos
y volumen esperado. Estas decisiones afectan validaciones, almacenamiento y pruebas.

**Fuente:** primera oración del requerimiento ficticio.

### Preguntas y pendientes de C-001

| Código | Pregunta o acción pendiente | Responsable | Estado |
| --- | --- | --- | --- |
| C-001-PRE-001 | ¿Qué campos serán obligatorios al registrar una solicitud? | Por asignar | Pendiente |
| C-001-PRE-002 | ¿Qué tipos de archivos se podrán adjuntar? | Por asignar | Pendiente |
| C-001-PRE-003 | ¿Cuál será el tamaño máximo permitido por archivo? | Por asignar | Pendiente |
| C-001-PRE-004 | ¿Cuántas solicitudes se esperan por día? | Por asignar | Pendiente |

Impacto: validaciones, almacenamiento y pruebas. Estas filas representan los mismos
asuntos del registro maestro; no se duplican como tareas separadas.

## C-002 · Gestión de solicitudes

Los analistas revisan los casos recibidos, asignan su atención y actualizan su estado.

**Personas involucradas:** analistas de soporte; falta confirmar si hay supervisores.

**Incluye:** revisión, asignación y cambio de estado. Reglas de asignación y estados
permitidos por confirmar; no se presupone asignación automática.

**No incluye:** envío de correos, cubierto por C-004.

**Resultado esperado:** solicitudes con responsable y estado actualizado.

**Dependencias:** C-001 proporciona los casos y C-005 reconoce al analista.

**Supuestos y pendientes:** confirmar estados, transiciones y quién puede asignar.
Sus respuestas afectan reglas de negocio y permisos.

**Fuente:** segunda oración del requerimiento ficticio.

### Preguntas y pendientes de C-002

| Código | Pregunta o acción pendiente | Responsable | Estado |
| --- | --- | --- | --- |
| C-002-PRE-001 | ¿Qué estados puede tener una solicitud? | Por asignar | Pendiente |
| C-002-PRE-002 | ¿Qué cambios entre estados están permitidos? | Por asignar | Pendiente |
| C-002-PRE-003 | ¿Qué roles pueden asignar una solicitud? | Por asignar | Pendiente |
| C-002-PRE-004 | ¿Qué roles pueden cambiar su estado? | Por asignar | Pendiente |
| C-002-PRE-005 | ¿Habrá un rol de supervisor distinto del analista? | Por asignar | Pendiente |

Impacto: reglas de negocio y permisos.

## C-003 · Consulta de solicitudes

El cliente consulta el estado de sus solicitudes sin pedir esa información a un analista.

**Personas involucradas:** clientes.

**Incluye:** consulta de solicitudes del cliente y su estado registrado.

**No incluye:** cambiar su estado, cubierto por C-002. La posibilidad de editar o
cancelar una solicitud no está solicitada y requiere confirmación antes de incluirla.

**Resultado esperado:** el cliente puede conocer el estado actual de sus casos.

**Dependencias:** C-001 proporciona la solicitud, C-002 actualiza su estado y C-005
permite identificar al cliente.

**Supuestos y pendientes:** confirmar qué detalle se muestra y si habrá filtros o
historial de cambios. No se agregan estas funcionalidades al alcance por defecto.

**Fuente:** primera oración del requerimiento ficticio.

### Preguntas y pendientes de C-003

| Código | Pregunta o acción pendiente | Responsable | Estado |
| --- | --- | --- | --- |
| C-003-PRE-001 | ¿Qué información de la solicitud podrá ver el cliente? | Por asignar | Pendiente |
| C-003-PRE-002 | ¿Se necesitan filtros para consultar las solicitudes? | Por asignar | Pendiente |
| C-003-PRE-003 | ¿Debe mostrarse un historial de cambios de estado? | Por asignar | Pendiente |
| C-003-PRE-004 | ¿Se solicita incorporar edición de solicitudes al alcance? | Por asignar | Pendiente |
| C-003-PRE-005 | ¿Se solicita incorporar cancelación de solicitudes al alcance? | Por asignar | Pendiente |

Las dos últimas preguntas aclaran posibles ampliaciones: edición y cancelación
siguen fuera del alcance hasta una decisión expresa. Contestar no las incorpora
automáticamente al resumen aceptado.

## C-004 · Avisos por correo

Cuando cambia el estado de una solicitud, se prepara y envía un aviso al cliente.

**Personas y sistemas involucrados:** cliente destinatario y servicio de correo por confirmar.

**Incluye:** preparación del mensaje y envío asociado al cambio de estado.

**No incluye:** notificaciones por SMS u otros canales, que no fueron solicitados.

**Resultado esperado:** el cliente recibe el aviso previsto sobre el cambio.

**Dependencias:** C-002 produce el cambio de estado; falta identificar el servicio de correo.

**Supuestos y pendientes:** confirmar destinatarios, contenido, estados que generan
avisos y tratamiento de fallos de envío. Esto afecta integración y pruebas.

**Fuente:** tercera oración del requerimiento ficticio.

### Preguntas y pendientes de C-004

| Código | Pregunta o acción pendiente | Responsable | Estado |
| --- | --- | --- | --- |
| C-004-PRE-001 | ¿Qué servicio se utilizará para enviar los correos? | Por asignar | Pendiente |
| C-004-PRE-002 | ¿Quiénes serán los destinatarios del aviso? | Por asignar | Pendiente |
| C-004-PRE-003 | ¿Qué contenido debe tener el mensaje? | Por asignar | Pendiente |
| C-004-PRE-004 | ¿Qué cambios de estado deben generar un aviso? | Por asignar | Pendiente |
| C-004-PRE-005 | ¿Qué debe ocurrir si falla el envío de un correo? | Por asignar | Pendiente |

Impacto: integración de correo y pruebas.

## C-005 · Acceso corporativo

El portal se conecta con el servicio de autenticación existente para reconocer a
clientes y analistas. No se propone construir un nuevo sistema de identidad.

**Personas y sistemas involucrados:** clientes, analistas y servicio corporativo.

**Incluye:** conexión al servicio existente y reconocimiento de identidad/tipo de usuario.

**No incluye:** desarrollar un proveedor de identidad nuevo. El detalle del alta de
clientes y administración de cuentas está por confirmar, sin asumirlo incluido.

**Resultado esperado:** acceso al portal con identidad reconocida por el servicio existente.

**Dependencias:** documentación, accesos y ambiente de prueba del servicio corporativo.

**Supuestos y pendientes:** confirmar que el servicio admite clientes externos,
protocolo de conexión y datos de roles disponibles. La ausencia de estas condiciones
puede cambiar materialmente este componente y exige revisión con el experto.

**Fuente:** cuarta oración del requerimiento ficticio.

### Preguntas y pendientes de C-005

| Código | Pregunta o acción pendiente | Responsable | Estado |
| --- | --- | --- | --- |
| C-005-PRE-001 | ¿El servicio corporativo permite autenticar a los clientes externos del portal? | Por asignar | Pendiente |
| C-005-PRE-002 | ¿Qué protocolo de conexión debe utilizar el portal? | Por asignar | Pendiente |
| C-005-PRE-003 | ¿Qué datos de roles entrega el servicio de autenticación? | Por asignar | Pendiente |
| C-005-PRE-004 | ¿El alta de clientes forma parte de este proyecto? | Por asignar | Pendiente |
| C-005-PRE-005 | ¿La administración de cuentas forma parte de este proyecto? | Por asignar | Pendiente |
| C-005-PEN-001 | Entregar la documentación técnica del servicio de autenticación. | Por asignar | Pendiente |
| C-005-PEN-002 | Habilitar un ambiente de prueba para la integración. | Por asignar | Pendiente |
| C-005-PEN-003 | Proporcionar los accesos autorizados al ambiente de prueba por el canal acordado. | Por asignar | Pendiente |

Impacto: viabilidad de integración, límites de alcance y posibilidad de probar.
La documentación y el ambiente son entregas pendientes identificables; sus códigos
se mantienen aunque se resuelvan después de contestar las preguntas.

## Cómo responder por código

El experto puede contestar individualmente, por ejemplo:

```text
!responder C-005-PRE-002 El protocolo autorizado está especificado en el anexo técnico adjunto.
```

El agente registra la respuesta y fuente con el mismo código. La recepción deja
el asunto respondido; si el anexo no resuelve el dato, pasa a «requiere aclaración».
Solo queda resuelto cuando la evidencia cubre la pregunta. En este ejemplo no hay
respuestas reales registradas. Ver `reglas/preguntas-componentes.md` para el historial.

## Cobertura del alcance

| Parte del requerimiento | Componente que la cubre | Observación |
| --- | --- | --- |
| Registrar solicitudes con archivos | C-001 | Campos y límites pendientes |
| Revisar, asignar y actualizar | C-002 | Reglas de estados y asignación pendientes |
| Consultar estado | C-003 | Detalle visible pendiente |
| Recibir correo al cambiar estado | C-004 | Servicio y tratamiento de fallos pendientes |
| Autenticación corporativa existente | C-005 | Integración compartida, registrada una sola vez |
| Chat y pagos | Ninguno | Exclusiones expresas del requerimiento |

## Qué falta decidir

Priorizar compatibilidad del acceso corporativo con clientes externos, reglas de
asignación/estados y servicio de correo. No atribuir complejidad baja a estos
pendientes. Con las aclaraciones correspondientes, A3 caracterizará cada componente
en D1–D11; A4 determinará método y esfuerzo cuando existan las entradas necesarias.
