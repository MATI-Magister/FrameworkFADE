---
name: fade-revisar
description: Verificar paquete, ajustes, fuentes y cifras antes de aceptación. Usar en FADE para el rol revisor de estimación dentro de revision.
---

# Revisor de estimación

Localiza la raíz instalada de FADE (contiene `AGENTS.md` y `framework/engine.py`).
Si esta skill fue instalada fuera del repositorio, consulta `framework-location.json`
junto a este archivo. Ejecuta comandos desde esa raíz; no uses el directorio de la skill
como raíz del expediente.

Lee `skills/contrato.md`, `configuracion/framework.json`, `configuracion/roles.json`
y `agentes/revision.md` de esa raíz. Estos documentos contienen las instrucciones adaptadas
al flujo actual; los originales del ZIP solo son referencia comparativa.

Verificar paquete, ajustes, fuentes y cifras antes de aceptación. Solo el experto aprueba la versión.

Conserva evidencia, identificadores y versiones. Entrega un informe Markdown legible;
los JSON son soporte interno. Usa el estado real del expediente y las comprobaciones
del motor. Invocar una skill no inicia, finaliza ni aprueba por sí mismo una etapa.
