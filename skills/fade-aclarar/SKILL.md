---
name: fade-aclarar
description: Conservar PRE/PEN y aclarar alcance, equipo y entorno. Usar en FADE para el rol facilitador de aclaraciones dentro de cierre.
---

# Facilitador de aclaraciones

Localiza la raíz instalada de FADE (contiene `AGENTS.md` y `framework/engine.py`).
Si esta skill fue instalada fuera del repositorio, consulta `framework-location.json`
junto a este archivo. Ejecuta comandos desde esa raíz; no uses el directorio de la skill
como raíz del expediente.

Lee `skills/contrato.md`, `configuracion/framework.json`, `configuracion/roles.json`
y `agentes/cierre.md` de esa raíz. Estos documentos contienen las instrucciones adaptadas
al flujo actual; los originales del ZIP solo son referencia comparativa.

Conservar PRE/PEN y aclarar alcance, equipo y entorno. No confundir respuesta con aprobación.

Aplica `reglas/presentacion-resultados.md`: resultado breve del paso y siguiente
acción; enlaza el respaldo sin volcarlo en el chat. Conserva evidencia, identificadores
y versiones; los JSON son soporte interno. Usa el estado real del expediente y las comprobaciones
del motor. Invocar una skill no inicia, finaliza ni aprueba por sí mismo una etapa.

## Ruta unificada vigente · 8 de noviembre de 2026

Leer `reglas/ruta-unificada-estimacion.md` antes de proponer método o pedir
productividad. Tabla cargada primero; actividades O/M/P para trabajo sin cobertura
suficiente. Recuperar respuestas y parámetros locales antes de preguntar. Esta
ruta prevalece sobre instrucciones anteriores que exigían otra fuente para preparar
una propuesta; conserva aprobaciones y salidas aceptadas.

## Cotización

Presenta solo preguntas que puedan cambiar alcance, esfuerzo o precio. Cuando haya un escenario viable, documenta el supuesto, la cantidad incluida, su límite y la condición de recotización. Aplica `reglas/preguntas-componentes.md`.

Coteja el alcance con A1 y A2. Cita las exclusiones y entregas parciales. Separa las consultas de diseño y del equipo de las decisiones que necesita el cliente.

**Cotizar con supuestos primero.** Preguntar al cliente solo si una decisión
comercial imprescindible impide cotizar incluso con un supuesto acotado o una
opción separada. Si hay una base viable, dejar el asunto como supuesto o pendiente
de diseño. Usar cifras de referencia disponibles para carga y dimensionamiento.
Diferir picos exactos, campos y contratos. Integrar los servicios ya descritos
y valorar como nuevo el trabajo propio sin evidencia de reutilización. Consultar
activos internamente solo si hay un indicio concreto que pueda cambiar la oferta.
