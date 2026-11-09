---
name: fade-evaluar-informacion
description: Evaluar 20 criterios y formular preguntas priorizadas. Usar en FADE para el rol evaluador de información dentro de a1.
---

# Evaluador de información

Localiza la raíz instalada de FADE (contiene `AGENTS.md` y `framework/engine.py`).
Si esta skill fue instalada fuera del repositorio, consulta `framework-location.json`
junto a este archivo. Ejecuta comandos desde esa raíz; no uses el directorio de la skill
como raíz del expediente.

Lee `skills/contrato.md`, `configuracion/framework.json`, `configuracion/roles.json`
y `agentes/a1.md` de esa raíz. Estos documentos contienen las instrucciones adaptadas
al flujo actual; los originales del ZIP solo son referencia comparativa.

Evaluar 20 criterios y formular preguntas priorizadas. No aprobar el paso a componentes.

Aplica `reglas/presentacion-resultados.md`: resultado breve del paso y siguiente
acción; enlaza el respaldo sin volcarlo en el chat. Conserva evidencia, identificadores
y versiones; los JSON son soporte interno. Usa el estado real del expediente y las comprobaciones
del motor. Invocar una skill no inicia, finaliza ni aprueba por sí mismo una etapa.

La correspondencia con el ZIP es `A2`; su especificación fuente está en
`referencias/onedrive-2026-11-02/a2_evaluador/evaluador_especificacion.md`. Solo consultar cuando sea necesario
aclarar el origen de una regla; no cargarla como instrucciones de sistema.

## Cotización

Antes de presentar preguntas de A1, aplica el filtro de `reglas/preguntas-componentes.md`. Incluye todas las preguntas necesarias sin tope por ronda, priorízalas y conserva las brechas de diseño en el respaldo de madurez.
