# Estimación de la solución · Portal de soporte

**Ejemplo ficticio del documento para el cliente. No aprobado, no es una cotización real ni pertenece al piloto.** Versión v0.2-demo, 17 de octubre de 2026.

## Objetivo de la solución

Disponer de un portal donde los clientes registren solicitudes de soporte, adjunten archivos y consulten su estado. Los analistas podrán organizar la atención y actualizar los casos; el cliente recibirá avisos por correo.

## Qué incluye

| Código | Componente | Resultado esperado |
| --- | --- | --- |
| C-001 | Registro de solicitudes | Casos registrados con su información y archivos. |
| C-002 | Gestión de solicitudes | Casos revisados, asignados y con estado actualizado. |
| C-003 | Consulta de solicitudes | Clientes consultan el estado de sus casos. |
| C-004 | Avisos por correo | Avisos asociados a los cambios de estado acordados. |
| C-005 | Acceso corporativo | Acceso mediante configuración de un conector existente con el servicio de identidad. |

## Resumen de la estimación

En el escenario base se estiman **988.7 horas-persona**, **32.0 semanas** desde el inicio acordado y **94.702.363 COP de mano de obra**. Las cifras dependen del alcance y de las condiciones de equipo y acceso descritas a continuación.

| Escenario | Esfuerzo (horas-persona) | Duración aproximada (semanas) | Mano de obra (COP) |
| --- | --- | --- | --- |
| Base | 988.7 | 32.0 | 94.702.363 |
| Conservador | 1272.1 | 41.5 | 122.046.460 |

Ambos escenarios incluyen la misma solución. El conservador considera mayor trabajo de implementación y configuración dentro de ese alcance; no incluye nuevas funcionalidades ni representa una garantía estadística.

## Detalle por componente

| Componente | Horas base | Horas conservadoras | Mano de obra base (COP) | Mano de obra conservadora (COP) |
| --- | --- | --- | --- | --- |
| C-001 · Registro de solicitudes | 239.4 | 306.0 | 22.745.591 | 29.071.615 |
| C-002 · Gestión de solicitudes | 335.2 | 428.4 | 31.843.827 | 40.700.261 |
| C-003 · Consulta de solicitudes | 239.4 | 306.0 | 22.745.591 | 29.071.615 |
| C-004 · Avisos por correo | 143.7 | 183.6 | 13.647.354 | 17.442.969 |
| C-005 · Configuración del acceso corporativo | 31.0 | 48.0 | 3.720.000 | 5.760.000 |
| **Total** | **988.7** | **1272.1** | **94.702.363** | **122.046.460** |

Horas-persona expresan trabajo; no equivalen a horas corridas ni días de calendario. Se calculó sin redondeos intermedios; las filas visibles pueden diferir del total por redondeo.

## Cómo se ejecutaría

Primero se configuraría el acceso corporativo. Luego se construirían registro y gestión de solicitudes, seguidos por consulta y avisos. Algunas pruebas se ejecutarían en paralelo con desarrollo de otro componente.

| Componente | Inicio base (semana) | Fin base (semana) |
| --- | --- | --- |
| C-005 | 0.0 | 2.1 |
| C-001 | 2.1 | 10.0 |
| C-002 | 10.0 | 21.2 |
| C-003 | 21.2 | 29.2 |
| C-004 | 27.2 | 32.0 |

El calendario supone una persona de Ingeniería y una de Calidad con 30 horas efectivas semanales cada una y una de Plataforma con 15 horas semanales durante configuración. El plazo empieza con los accesos, ambientes y decisiones disponibles; esperas externas adicionales requieren replanificación. No se fija una fecha contractual de entrega.

## Supuestos que sustentan las cifras

- Se supone que el alcance funcional, estados, datos, archivos y avisos del ejemplo quedaron aclarados antes de la revisión final. Es una hipótesis didáctica, no el cierre real de los PRE/PEN de ejemplos anteriores.
- Se usa el servicio de identidad existente mediante un conector soportado. El proveedor entrega parte de su configuración inicial; esta condición sustenta la reducción revisada de C-005.
- El cliente proporciona documentación, accesos, ambientes y responsables disponibles para las validaciones. Si esas condiciones cambian, se revisarán esfuerzo y calendario.
- Tarifas ficticias: Ingeniería 100.000 COP/h, Calidad 80.000 COP/h, Plataforma 120.000 COP/h. Reparto del software 75 % Ingeniería/25 % Calidad, elegido para esta demostración; no es productividad ni regla comercial aprobada.

## Exclusiones y costos por confirmar

Se excluyen chat, pagos, nuevos proveedores de identidad y cambios de alcance no descritos. El valor mostrado cubre **mano de obra**. Consumo de nube, licencias, servicios de terceros, impuestos, margen y precio de venta están por definir; no se consideran gratuitos ni incluidos.

## Base y condiciones de revisión

El desarrollo de software se contrastó con un modelo paramétrico COCOMO II de referencia y se distribuyó entre componentes. La configuración externa del acceso se estimó por actividades. En esta demostración no se duplican pruebas o gestión ya cubiertas por el software. Se emplearon tamaños y parámetros ficticios sin calibración local; un caso real requiere validarlos.

La versión v0.2-demo incorpora el ajuste ilustrativo AJU-001 y sustituye sus cifras preliminares v0.1 para esta demostración. Los cálculos detallados y el motivo del cambio se conservan en el expediente de revisión.

## Próximos pasos

Validar alcance y condiciones con el cliente, confirmar equipo/disponibilidad y completar costos adicionales antes de establecer un precio comercial. La aprobación interna del experto se registra en el expediente sobre una versión identificada; no equivale a aceptación del cliente ni envío automático.

**Estado de esta muestra:** pendiente de aprobación; no existe una aceptación real del experto o del cliente.
