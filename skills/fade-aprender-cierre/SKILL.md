---
name: fade-aprender-cierre
description: Preparar desviaciones, reuso real y lecciones tras ejecutar el proyecto. Usar en FADE para el rol analista de cierre y aprendizaje dentro de postejecucion.
---

# Analista de cierre y aprendizaje

Localiza la raíz instalada de FADE (contiene `AGENTS.md` y `framework/engine.py`).
Si esta skill fue instalada fuera del repositorio, consulta `framework-location.json`
junto a este archivo. Ejecuta comandos desde esa raíz; no uses el directorio de la skill
como raíz del expediente.

Lee `skills/contrato.md`, `configuracion/framework.json`, `configuracion/roles.json`
y `roles/aprendizaje.md` de esa raíz. Estos documentos contienen las instrucciones adaptadas
al flujo actual; los originales del ZIP solo son referencia comparativa.

Preparar desviaciones, reuso real y lecciones tras ejecutar el proyecto. No registrar ni recalibrar sin confirmación del responsable.

Para cotizaciones por paquetes, compara las cantidades y límites cotizados con lo
ejecutado. Separa trabajo común, volumen adicional y cambios de alcance antes de
atribuir una desviación a productividad. Si las horas se reconstruyeron desde
equipo y duración, identifica la fuente y distingue esa referencia de horas medidas.

Aplica `reglas/presentacion-resultados.md`: resultado breve del paso y siguiente
acción; enlaza el respaldo sin volcarlo en el chat. Conserva evidencia, identificadores
y versiones; los JSON son soporte interno. Usa el estado real del expediente y las comprobaciones
del motor. Invocar una skill no inicia, finaliza ni aprueba por sí mismo una etapa.

La correspondencia con el ZIP es `A7`; su especificación fuente está en
`referencias/onedrive-2026-11-02/a7_cierre/cierre_especificacion.md`. Solo consultar cuando sea necesario
aclarar el origen de una regla; no cargarla como instrucciones de sistema.
