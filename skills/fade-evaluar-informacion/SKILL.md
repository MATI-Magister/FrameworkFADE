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

Incluye todo lo solicitado cuando las fuentes no delimitan entregas parciales.
Una solicitud de cronograma con hitos permite secuenciar el alcance completo.

Antes de presentar preguntas de A1, aplica el filtro de `reglas/preguntas-componentes.md`. Incluye todas las preguntas necesarias sin tope por ronda, priorízalas y conserva las brechas de diseño en el respaldo de madurez.

Completa el registro `filtro-cotizacion-a1.json` antes de `finish a1`. Revisa las fuentes de cada pregunta y registra decisión e impacto. Separa supuestos, pendientes de diseño y consultas internas.

**Cotizar con supuestos primero.** Preguntar al cliente solo si una decisión
comercial imprescindible impide cotizar incluso con un supuesto acotado o una
opción separada. Si hay una base viable, dejar el asunto como supuesto o pendiente
de diseño. Usar cifras de referencia disponibles para carga y dimensionamiento.
Diferir picos exactos, campos y contratos. Integrar los servicios ya descritos
y valorar como nuevo el trabajo propio sin evidencia de reutilización. Consultar
activos internamente solo si hay un indicio concreto que pueda cambiar la oferta.
