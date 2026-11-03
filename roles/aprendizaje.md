# Cierre y aprendizaje · después de ejecutar el proyecto · !aprender

Es distinto de !aclarar. No pertenece a las siete etapas de estimación ni modifica
su estado. Leer revisión aprobada, línea base que realmente se ejecutó, horas reales
por C-001…, cambios de alcance aprobados y notas de cierre con fuentes/ubicaciones.
Si no hay horas reales o ejecución, solicitar esos insumos y no fabricar un cierre.

Guardar una versión nueva en 02-trabajo/aprendizaje/<version>/ con informe.md,
evidencias y cálculos reproducibles. Usar plantillas/aprendizaje.md. Comparar línea
base y horas ajustadas por cambios, separar trabajo fuera del alcance y advertir
componentes sin horas. Si la línea base es cero, desviación porcentual «no aplica»;
mostrar la diferencia absoluta. No calcular promedios con divisiones inválidas.

Proponer causa por desviación, reúso real por activo y activos reutilizables nuevos,
con cita y estado propuesto/confirmado/descartado. Las horas solas no prueban causas.
El umbral y disparador de recalibración del ZIP siguen pendientes de parametrizar;
sin ellos mostrar todas las diferencias y no afirmar que hay un disparador aprobado.

El líder confirma. No modificar catálogos compartidos, registro o reglas por esta
orden; presentar un cambio revisable y solicitar su confirmación explícita. Esta
versión prepara el informe; el registro corporativo automático permanece pendiente
de acordar su procedimiento. No reutilizar registrar_cierre.py del ZIP en datos
reales sin adaptar sus IDs, validaciones, autorizaciones y parámetros incrustados.


El soporte numérico se prepara con scripts/aprendizaje.py --project <id> --baseline
<resultado-A4-revisado> --actuals <horas-reales.json> --changes <cambios.json>.
La línea base es el resultado JSON de un cálculo incorporado a revisión aprobada;
--scenario elige Base o Conservador explícitamente. Usa el umbral del snapshot de
esa línea base y conserva hashes de los insumos. Las horas reales llevan source y
components con id/hours; cambios es una lista de id/component/hours/source/approved_by.
El script detecta faltantes, registros sin correspondencia y bases inválidas; no
finaliza la estimación ni confirma causas, activos o reutilización automáticamente.
Completa el informe con el criterio y las evidencias que exige este rol.
