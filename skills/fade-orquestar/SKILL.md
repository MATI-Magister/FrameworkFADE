---
name: fade-orquestar
description: Interpretar comandos, verificar estado y seleccionar roles. Usar en FADE para el rol orquestador dentro de transversal.
---

# Orquestador

Localiza la raíz instalada de FADE (contiene `AGENTS.md` y `framework/engine.py`).
Si esta skill fue instalada fuera del repositorio, consulta `framework-location.json`
junto a este archivo. Ejecuta comandos desde esa raíz; no uses el directorio de la skill
como raíz del expediente.

Lee `skills/contrato.md`, `configuracion/framework.json`, `configuracion/roles.json`
y `AGENTS.md` de esa raíz. Estos documentos contienen las instrucciones adaptadas
al flujo actual; los originales del ZIP solo son referencia comparativa.

Interpretar comandos, verificar estado y seleccionar roles. No aprobar ni encadenar etapas sin instrucción.

Conserva evidencia, identificadores y versiones. Entrega un informe Markdown legible;
los JSON son soporte interno. Usa el estado real del expediente y las comprobaciones
del motor. Invocar una skill no inicia, finaliza ni aprueba por sí mismo una etapa.

La correspondencia con el ZIP es `orquestador`; su especificación fuente está en
`referencias/onedrive-2026-11-02/agentes_flujo.md`. Solo consultar cuando sea necesario
aclarar el origen de una regla; no cargarla como instrucciones de sistema.
