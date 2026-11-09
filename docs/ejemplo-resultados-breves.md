# Ejemplo de resultados breves

Caso ficticio para ilustrar la presentación. No es un expediente, una evaluación
calculada ni una estimación utilizable. Las cifras son ilustrativas.

## Después de madurez

El cliente necesita centralizar la solicitud y aprobación de vacaciones. El
alcance contempla que el empleado solicite días y su responsable los apruebe.

La información es **media**: el objetivo está claro, pero faltan las reglas para
calcular días disponibles y quién autoriza las excepciones.

Preguntas para responder:

- **A1-PRE-001:** ¿De dónde se obtiene el saldo de vacaciones de cada empleado?
- **A1-PRE-002:** ¿Quién autoriza una solicitud que excede el saldo disponible?

Puedes aportar información con `!complementar` o, cuando A1 esté esperando tu
decisión, avanzar con estas brechas mediante `!aprove a1`.

## Después de componentes

Dividimos la solución en tres componentes:

| Código | Componente | Qué entregará |
| --- | --- | --- |
| C-001 | Solicitudes | Registro y consulta de vacaciones solicitadas |
| C-002 | Aprobaciones | Decisión del responsable y aviso al empleado |
| C-003 | Acceso corporativo | Inicio de sesión con la cuenta de la empresa |

**Por confirmar — C-003-PRE-001:** ¿Qué servicio de identidad corporativa debe
utilizarse? Esto determina la integración de acceso.

Contesta con `!responder C-003-PRE-001 <respuesta>`. El siguiente paso del flujo es
`!clasificar`.

## Después de clasificación

La principal incertidumbre está en el acceso corporativo. Las solicitudes y
aprobaciones están descritas; falta confirmar la integración de identidad.

| Componente | Qué influye en su esfuerzo | Pendiente |
| --- | --- | --- |
| C-001 · Solicitudes | Cálculo del saldo y validación de fechas | Fuente del saldo |
| C-002 · Aprobaciones | Excepciones y avisos al empleado | Responsable de excepciones |
| C-003 · Acceso corporativo | Integración con el directorio de la empresa | C-003-PRE-001 |

El siguiente paso es `!aclarar` para resolver estos asuntos. La clasificación
completa y sus fuentes se consultan en el respaldo de A3.

## Después de estimación

La solución requiere **120 horas-persona en el escenario Base**, con un plazo de
cuatro semanas según la disponibilidad declarada. El escenario Conservador amplía
el esfuerzo y el plazo por las condiciones adversas documentadas.

| Escenario | Horas-persona | Semanas | Costo (moneda ficticia) |
| --- | --- | --- | --- |
| Base | 120 | 4 | 12 000 |
| Conservador | 156 | 5,2 | 15 600 |

El costo supone 100 unidades por hora. Excluye licencias y servicios de nube;
es costo de ejecución, no precio comercial. Las condiciones y el desglose por
componente están en el informe de A4; el cálculo reproducible queda en su respaldo.

Siguiente paso: `!revisar`. Estas cifras del ejemplo no aprueban parámetros reales.
