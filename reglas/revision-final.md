# Revisión final por el experto · propuesta para revisión

## Qué revisa

El experto recibe un paquete con alcance y componentes, escenarios, esfuerzo por
componente/rol, calendario, costos, método/cobertura, supuestos, exclusiones,
fuentes y PRE/PEN abiertos. Revisar cálculos, ausencia de doble conteo, capacidad,
coherencia de escenarios y claridad del mensaje para el cliente.

Los pendientes materiales que impidan sustentar el alcance o calcular deben
aclararse o delimitarse antes de aprobar. Las exclusiones conocidas y condiciones
aceptadas pueden permanecer si el experto las reconoce y el informe las declara.
No convertir una estimación parcial en una cotización completa por aprobarla.

## Cómo pedir ajustes

Con `!ajustar <instrucción y motivo/fuente>`, o una instrucción natural inequívoca,
el experto solicita modificar la versión presentada. El comando local `adjust`
archiva el paquete anterior y vuelve la revisión a ejecución, sin aprobación.
Recuperar el registro histórico y conservar códigos **AJU-001…**. Registrar:
componente/partida afectada, valor anterior, cambio solicitado, razón, evidencia,
autor, estado, efecto en ambos escenarios y nueva versión.

- **Corrección de explicación/presentación:** revisar documento, sin tocar cifras.
- **Cambio de esfuerzo/tamaño/capacidad/tarifa:** volver a A4 con entradas revisadas,
  recalcular sus dependencias y escenarios y presentar nueva revisión. Si cambian
  reglas aprobadas, versionarlas y obtener aprobación explícita antes de reestimar.
- **Cambio de alcance:** volver a A1/A2/A3 según el impacto, conservando historial.
- **Ajuste comercial:** separar precio/descuento/margen del costo técnico. No
  rebajar horas para hacer coincidir un presupuesto. Condiciones comerciales
  requieren datos y decisión explícita, no supuestos silenciosos del agente.

Un ajuste solicitado no se marca como aplicado hasta ejecutarlo y verificarlo.
Para cuestiones pendientes usar PRE/PEN existentes o nuevos, referenciados por AJU.
No perder ajustes anteriores al reabrir etapas: recuperarlos del historial.

## Qué se presenta para aprobación

1. `03-entregables/revision.md`: versión, comprobaciones realizadas, diferencias
   respecto de A4 original, resultados revisados, condiciones y decisión pendiente.
2. `03-entregables/ajustes.md`: registro AJU completo o declaración sin ajustes.
3. `03-entregables/cliente.md`: documento legible con objetivo, alcance, componentes,
   escenarios, calendario, costos y su cobertura, condiciones y exclusiones.
4. A4 y sus cálculos reproducibles, fuentes y snapshot de reglas en el expediente.

`finish revision` exige los documentos y deja el paquete esperando aprobación.
La revisión semántica sigue siendo responsabilidad del agente y el experto: la
existencia de archivos no garantiza calidad ni aceptación de sus contenidos.

## Cómo aprobar

`!aprove revision` registra aceptación explícita del experto sobre la versión
presentada. `!aprove` sin argumento mantiene la regla existente de destino único.
El motor verifica que revisión, informe cliente, ajustes, A4 y reglas no hayan
cambiado desde la revisión. Registra responsable, fecha UTC y huellas en el estado.
Esto es una constancia local del flujo, no firma digital ni verificación de identidad.

No modificar los archivos aprobados para agregar «aprobado»: su huella identifica
la versión aceptada. El estado del expediente acredita la decisión local. Una
modificación posterior exige nueva versión, reapertura explícita y nueva aprobación.
La aceptación no envía, publica ni convierte el informe en acuerdo con el cliente.

## Entregable para cliente

Usar `plantillas/entregable-cliente.md`. Mostrar supuestos y exclusiones que afecten
la decisión, aunque los cálculos y ajustes internos detallados queden en el expediente.
Identificar costo de ejecución, costos pendientes y precio comercial por separado.
Si nube/licencias no están valoradas, no rotular la mano de obra como costo total.
Exportaciones Word/PDF se pueden añadir cuando se soliciten; la versión actual
genera Markdown legible y portable en el repositorio.

Ejemplos ficticios: `docs/ejemplo-revision-final.md` y
`docs/ejemplo-entregable-cliente.md`. No representan aprobación real de un experto.
