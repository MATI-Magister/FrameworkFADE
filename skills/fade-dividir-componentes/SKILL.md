---
name: fade-dividir-componentes
description: Cubrir el alcance con componentes y procesos sin duplicados. Usar en FADE para el rol divisor de componentes dentro de a2.
---

# Divisor de componentes

Localiza la raíz instalada de FADE (contiene `AGENTS.md` y `framework/engine.py`).
Si esta skill fue instalada fuera del repositorio, consulta `framework-location.json`
junto a este archivo. Ejecuta comandos desde esa raíz; no uses el directorio de la skill
como raíz del expediente.

Lee `skills/contrato.md`, `configuracion/framework.json`, `configuracion/roles.json`
y `agentes/a2.md` de esa raíz. Estos documentos contienen las instrucciones adaptadas
al flujo actual; los originales del ZIP solo son referencia comparativa.

Cubrir el alcance con componentes y procesos sin duplicados. No convertir propuestas inferidas en alcance confirmado.

Aplica `reglas/presentacion-resultados.md`: resultado breve del paso y siguiente
acción; enlaza el respaldo sin volcarlo en el chat. Conserva evidencia, identificadores
y versiones; los JSON son soporte interno. Usa el estado real del expediente y las comprobaciones
del motor. Invocar una skill no inicia, finaliza ni aprueba por sí mismo una etapa.

La correspondencia con el ZIP es `A3`; su especificación fuente está en
`referencias/onedrive-2026-11-02/a3_divisor/divisor_especificacion.md`. Solo consultar cuando sea necesario
aclarar el origen de una regla; no cargarla como instrucciones de sistema.

## Cotización

Distingue el trabajo común del que se repite por integración, reporte o servicio. Para preguntas y pendientes, aplica el filtro de cotización de `reglas/preguntas-componentes.md`.
