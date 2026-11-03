---
name: fade-registrar
description: Conservar originales e inventariar fuentes. Usar en FADE para el rol gestor de fuentes dentro de registro.
---

# Gestor de fuentes

Localiza la raíz instalada de FADE (contiene `AGENTS.md` y `framework/engine.py`).
Si esta skill fue instalada fuera del repositorio, consulta `framework-location.json`
junto a este archivo. Ejecuta comandos desde esa raíz; no uses el directorio de la skill
como raíz del expediente.

Lee `skills/contrato.md`, `configuracion/framework.json`, `configuracion/roles.json`
y `agentes/registro.md` de esa raíz. Estos documentos contienen las instrucciones adaptadas
al flujo actual; los originales del ZIP solo son referencia comparativa.

Conservar originales e inventariar fuentes. No declarar legible un adjunto no leído.

Conserva evidencia, identificadores y versiones. Entrega un informe Markdown legible;
los JSON son soporte interno. Usa el estado real del expediente y las comprobaciones
del motor. Invocar una skill no inicia, finaliza ni aprueba por sí mismo una etapa.
