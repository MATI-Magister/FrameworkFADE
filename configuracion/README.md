# Configuración compartida

framework.json es la fuente de valores parametrizables. No escribir credenciales
ni datos de clientes aquí. null significa por confirmar; una lista vacía no es
evidencia de que no haya trabajo o equipo. No se cargan overrides local.json:
está reservado y excluido de Git para evitar su exposición accidental.

| Sección | Uso real |
| --- | --- |
| operation | Proyecto predeterminado, puerto; sin conteo ni límite de sesiones |
| estimation | Unidad, moneda, tarifas, costo horario, capacidad, margen y escenarios |
| estimation.process_method | Tabla técnica, factores, gestión y bandas iniciales cargados; calibración y umbrales opcionales pendientes |
| policies | Tratamiento actual de desconocidos y aprobación; cambios requieren adaptar las reglas |
| catalogs | Ubicaciones de activos, tecnologías e historia, mantenidos solo localmente |
| roles_file | Mapa de roles, skills y responsables humanos; sin dependencia de proveedor |
| source_candidates | Fuente original conservada; la ruta unificada habilita expresamente su tabla técnica, no sus cifras comerciales |

Consulta: python scripts/framework.py config

Roles: python scripts/framework.py roles

Tarifas: lista con role, amount positivo, unit y source. Equipo: rol, personas,
horas efectivas disponibles y dedicación, con fuente. CFO: description y source,
con valores/decisiones comerciales. Las fórmulas no cambian al ajustar valores.

Para cambiar un valor: registrar la fuente y decisión en reglas/revision.md,
actualizar este archivo e incrementar su versión. Los parámetros de estimation y
policies entran en la huella/snapshot de reglas A4; las opciones de operación quedan
fuera. Los snapshots anteriores no cambian. !aprove reglas sigue siendo necesario.

El instalador crea catálogos vacíos en datos-locales/ si faltan, sin sobrescribir.
Los valores ilustrativos se conservan en la referencia original para compararlos
contigo, sin promoverlos automáticamente. La configuración no activa un proveedor
IA: cada ejecución registra la herramienta/modelo realmente usado si está disponible.


estimation.costing_mode elige por_rol o costo_unico; null mantiene la decisión
pendiente. No se suma un costo único encima de tarifas por rol. En el modo único,
la capacidad y el reparto por roles siguen siendo necesarios para el calendario.
Equipo: role, people (entero), hours_per_week, allocation (0–1) y source.
Consulta de integridad y preparación: python scripts/framework.py doctor.
La instalación completa, con skills en el directorio elegido, se hace con
python scripts/install.py --skills-target <directorio>.


Decisiones vigentes INC-008/010/014: definición de componente con
Validado/Definido/Supuesto; confirmación directa escrita o transcripción identificada;
costo horario único inicial. cost_per_hour y currency siguen null hasta recibir
valores reales. Los repartos de esfuerzo y capacidad por rol siguen siendo necesarios.


classification.reuse contiene las bandas elegidas del ZIP con límites explícitos:
R1 [0,10), R2 [10,30), R3 [30,50], R4 (50,100]. El motor comprueba ausencia de
huecos/superposición y coherencia con la clase del componente. Las bandas entran
en la huella de reglas A4; cambiarlas requiere otra revisión y aprobación. Estos
umbrales no asignan automáticamente factores de ahorro ni porcentajes desconocidos.

## Ruta unificada y parámetros del expediente

Desde el 8 de noviembre de 2026 process_method contiene la tabla técnica cargada
y sus factores/bandas, habilitados como referencia inicial por el usuario.
status=draft y calibration_status=initial_reference_not_calibrated distinguen
su uso inicial de una validación productiva. No se importan cifras económicas
ni capacidades ilustrativas. unified_route define la selección común de métodos.
Los párrafos anteriores sobre no adoptar ejemplos no excluyen esta decisión explícita.

Antes de pedir información, consultar estimation-route con --project y leer las
fuentes vigentes. La consolidación de valores del propio proyecto se guarda en
01-entradas/respuestas/parametros-estimacion.json con dos objetos: estimation y
sources. estimation admite currency, cost_per_hour, costing_mode, rates, team y
cfo_parameters. sources requiere una referencia identificable por cada campo
aportado. Los valores se validan igual que los globales y entran en la huella
y snapshot del expediente. No permite cambiar la ruta ni aprobarla por un override.
Una fuente de chat del experto se conserva como tal, sin atribuirla al cliente.

No sustituir parámetros del proyecto al editar configuracion/framework.json:
eso afectaría a todos. No pedir valores nuevamente porque aún no estén consolidados.
Ejemplo mínimo de forma (cifras ilustrativas; no copiar a un proyecto):

```json
{
  "estimation": {"currency": "COP", "cost_per_hour": 100000},
  "sources": {"currency": "respuestas-componentes.md, R-001", "cost_per_hour": "respuestas-componentes.md, R-002"}
}
```

Detalles y contrato de partidas: reglas/ruta-unificada-estimacion.md.
