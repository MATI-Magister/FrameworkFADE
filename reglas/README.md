# Reglas de estimación

Leer integracion-agentes.md y revision.md para decisiones actuales. A1 usa B.1
(modelo-informacion.json, 20 criterios/9 dimensiones); el Excel anterior permanece
como fuente de clasificación e historia. El método principal en evaluación es
horas por proceso, todavía sin factores calibrados ni aprobación productiva.

estimacion.json contiene el contrato y referencias; configuracion/framework.json
es la fuente de parámetros reales. El motor combina ambos y embebe modelo y
parámetros en la huella y snapshot. No duplicar tarifas o capacidades en reglas.

status=approved solo con decisión humana. Además !aprove reglas registra la
aceptación por expediente. Revisar fuentes, fórmulas, cobertura, unidades, moneda,
capacidad y escenarios. Elegir el modelo o método no aprueba el paquete completo.
Los dos escenarios actuales son Base y Conservador; INC-006 resuelto: optimista solo como referencia.

Cambiar un valor de negocio requiere revisar reglas y volver a aprobar antes de
A4. Nunca modificar snapshots. Un archivo válido no demuestra calidad de análisis.
Las referencias originales y ejemplos no suministran parámetros por defecto.
