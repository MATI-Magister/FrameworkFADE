# Reglas de estimación

Lee primero `propuesta-inicial.md`: contiene las reglas propuestas para cada agente,
el método y los formatos legibles. `revision.md` registra la revisión por partes.
El usuario eligió el catálogo/modelo del Excel como base. Las decisiones operativas
restantes y COCOMO II siguen en revisión. Ver `modelo-madurez.md`,
`modelo-madurez.json` y `cocomo-ii.md`. Se retira la propuesta de seis dimensiones.

`estimacion.json` es el contrato inicial. Sus valores nulos representan decisiones
pendientes. `status` debe pasar a `approved` solo con autorización humana; además
el usuario registra la aprobación por proyecto con `!aprove reglas`.

Completa `maturity`, `dimensions`, `method`, `effort_unit`, `currency`, `rates`,
`capacity`, `cfo_parameters` y exactamente dos `scenarios`. Cada sección incluye
`source` para identificar su documento o decisión de origen. Para reglas sin parámetros
CFO adicionales, escribe explícitamente esa decisión y su fuente.

`rates` debe ser una lista con `role`, `amount` numérico positivo, `unit` y `source`.
Los escenarios contienen `name`, `description` y `source`. Las secciones narrativas
contienen `description` y `source`. Incrementa `version` cuando cambie el contenido.
La validación comprueba estructura; el revisor debe comprobar coherencia de fórmulas,
unidades, capacidad, moneda, impuestos y contingencias antes de aprobar.

Puedes agregar documentos de apoyo en esta carpeta y citarlos desde el JSON.
No incluyas secretos o credenciales. Una modificación posterior exige nueva aprobación.
El JSON conserva las decisiones metodológicas y referencia el catálogo completo.
El motor lo incorpora al snapshot de A4 y a la huella de aprobación;
mantén coherencia con la propuesta legible al editar. No cambies `status` por revisar
solo una sección. La validación automática es estructural: el agente debe comprobar
además el acuerdo de las reglas y la capacidad operativa real antes de aprobar el paquete.
