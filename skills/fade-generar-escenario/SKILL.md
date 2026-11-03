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

Conserva evidencia, identificadores y versiones. Entrega un informe Markdown legible;
los JSON son soporte interno. Usa el estado real del expediente y las comprobaciones
del motor. Invocar una skill no inicia, finaliza ni aprueba por sí mismo una etapa.

La correspondencia con el ZIP es `A5`; su especificación fuente está en
`referencias/onedrive-2026-11-02/a5_generador/generador_especificacion.md`. Solo consultar cuando sea necesario
aclarar el origen de una regla; no cargarla como instrucciones de sistema.
