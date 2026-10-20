# Ejemplo · Revisión final del experto

**Demostración ficticia, sin aprobación real.** Versiones ilustrativas: A4 v0.1 → revisión/cliente v0.2-demo. No corresponde al piloto.

## Solicitud ilustrativa del experto

«!ajustar C-005: el proveedor ya deja preconfigurado parte del conector. Revisar esa actividad con el anexo de configuración y recalcular ambos escenarios».

EX-REV-01 es un anexo ficticio supuesto solo para mostrar cómo se fundamenta el ajuste. En un caso real deben existir fuente y responsable identificados. No es una instrucción real de aprobación, respuesta del usuario o cambio de reglas metodológicas.

## Registro de ajustes

| Código | Partida | Antes | Después | Razón y fuente | Estado |
| --- | --- | --- | --- | --- | --- |
| AJU-001 | C-005, configuración de conector/permisos | O/M/P: 12/18/30 h | O/M/P: 6/12/18 h | Preconfiguración provista por tercero; EX-REV-01 ficticio | Aplicado y verificado matemáticamente en el ejemplo; pendiente de aceptación |

El resto de actividades, reglas, drivers, tarifas, capacidad y alcance se mantiene. Se recalcula A4: no se rebaja un total manualmente. El esfuerzo de C-005 pasa de 38 a 31 h base y de 60 a 48 h conservadoras. La reducción es 7/12 h, 840.000/1.440.000 COP y 0,47/0,80 semanas, respectivamente.

## Comparación para el experto

| Escenario | Horas antes → después | Semanas antes → después | Mano de obra COP antes → después |
| --- | --- | --- | --- |
| Base | 995.7 → 988.7 | 32.5 → 32.0 | 95.542.363 → 94.702.363 |
| Conservador | 1284.1 → 1272.1 | 42.3 → 41.5 | 123.486.460 → 122.046.460 |

## Comprobaciones realizadas

Reconciliación de componentes/roles y costo; esfuerzo COCOMO del software sin cambio; actividad externa contada una sola vez; dependencias y capacidad comprobadas; dos escenarios recalculados; nube/licencias/comercial separados de mano de obra. El informe para cliente presenta las cifras revisadas y sus condiciones.

## Decisión del experto

**Pendiente.** Si pide otro ajuste, `!ajustar` reabre la revisión conservando la versión anterior. Si acepta el paquete real, `!aprove revision` registra su decisión sobre esa versión; este ejemplo no ejecuta esa operación. No se aprueba ni envía nada por generar estos documentos.

El ejemplo de cliente limita su cifra a mano de obra. No es una propuesta comercial completa: nube, licencias, impuestos y margen requieren decisión antes de presentar un precio final. En un expediente real las brechas técnicas materiales deben aclararse o quedar fuera del alcance declarado.

## Archivos de referencia

Cliente: `docs/ejemplo-entregable-cliente.md`. Reproducción: `python scripts/ejemplo_revision.py`. Los originales ficticios de A4 permanecen en `docs/ejemplo-a4-estimacion.md` y `ejemplos/a4/entradas.json`.
