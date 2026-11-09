---
name: fade-generar-escenario
description: Juzgar comparables y documentar cobertura y escenarios. Usar en FADE para el rol analista de escenarios dentro de a4.
---

# Analista de escenarios

Localiza la raíz instalada de FADE (contiene `AGENTS.md` y `framework/engine.py`).
Si esta skill fue instalada fuera del repositorio, consulta `framework-location.json`
junto a este archivo. Ejecuta comandos desde esa raíz; no uses el directorio de la skill
como raíz del expediente.

Lee `skills/contrato.md`, `configuracion/framework.json`, `configuracion/roles.json`
y `roles/generador.md` de esa raíz. Estos documentos contienen las instrucciones adaptadas
al flujo actual; los originales del ZIP solo son referencia comparativa.

Juzgar comparables y documentar cobertura y escenarios. No inventar historia, tarifas o capacidad ni superponer métodos.

Aplica `reglas/presentacion-resultados.md`: resultado breve del paso y siguiente
acción; enlaza el respaldo sin volcarlo en el chat. Conserva evidencia, identificadores
y versiones; los JSON son soporte interno. Usa el estado real del expediente y las comprobaciones
del motor. Invocar una skill no inicia, finaliza ni aprueba por sí mismo una etapa.

La correspondencia con el ZIP es `A5`; su especificación fuente está en
`referencias/onedrive-2026-11-02/a5_generador/generador_especificacion.md`. Solo consultar cuando sea necesario
aclarar el origen de una regla; no cargarla como instrucciones de sistema.

## Ruta unificada vigente · 8 de noviembre de 2026

Leer `reglas/ruta-unificada-estimacion.md` antes de proponer método o pedir
productividad. Tabla cargada primero; actividades O/M/P para trabajo sin cobertura
suficiente. Recuperar respuestas y parámetros locales antes de preguntar. Esta
ruta prevalece sobre instrucciones anteriores que exigían otra fuente para preparar
una propuesta; conserva aprobaciones y salidas aceptadas.

## Cotización

Prepara paquetes comunes y por unidad según `reglas/ruta-unificada-estimacion.md`. Registra cantidad, supuesto, límite y condición de recotización. Aplica la tabla a procesos comparables y rangos O/M/P por actividad a los faltantes.

En integraciones, separa el servicio existente de la conexión que se cotiza. Descuenta reúso solo por la parte de un activo aprovechable que tenga evidencia y cobertura.

Revisa la mezcla de métodos, contrasta horas probables con la tabla y explica qué
partidas abren la brecha Base–Conservador. Sustenta un escenario adverso coherente
y separa los cambios de alcance. Aplica la revisión descrita en `reglas/ruta-unificada-estimacion.md`.

Usa Modelo Propuesta V2 para estimaciones nuevas. Busca primero `DatosExt` si la unidad es comparable, luego `IA` y finalmente O/M/P. Cita la talla, la hoja, la fila y la muestra cuando exista. Consulta `reglas/ruta-unificada-estimacion.md`.

Recupera las cinco dimensiones de `clasificacion-modelo-v2.json`. Justifica cualquier cambio de talla o arquetipo si cambia la unidad que se estima.
