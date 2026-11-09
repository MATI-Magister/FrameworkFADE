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

Aplica `reglas/presentacion-resultados.md`: resultado breve del paso y siguiente
acción; enlaza el respaldo sin volcarlo en el chat. Conserva evidencia, identificadores
y versiones; los JSON son soporte interno. Usa el estado real del expediente y las comprobaciones
del motor. Invocar una skill no inicia, finaliza ni aprueba por sí mismo una etapa.

La correspondencia con el ZIP es `orquestador`; su especificación fuente está en
`referencias/onedrive-2026-11-02/agentes_flujo.md`. Solo consultar cuando sea necesario
aclarar el origen de una regla; no cargarla como instrucciones de sistema.

## Ruta unificada vigente · 8 de noviembre de 2026

Leer `reglas/ruta-unificada-estimacion.md` antes de proponer método o pedir
productividad. Tabla cargada primero; actividades O/M/P para trabajo sin cobertura
suficiente. Recuperar respuestas y parámetros locales antes de preguntar. Esta
ruta prevalece sobre instrucciones anteriores que exigían otra fuente para preparar
una propuesta; conserva aprobaciones y salidas aceptadas.

## Cotización

Antes de presentar preguntas de A1, usa el registro publicado por `finish a1`.
Trata las preguntas de la rúbrica como diagnóstico interno y aplica primero
supuestos acotados u opciones separadas.

Al dirigir A1, A2, A3 o cierre, exige el filtro de preguntas de `reglas/preguntas-componentes.md`. Para nuevas cotizaciones A4, usa los paquetes definidos en `reglas/ruta-unificada-estimacion.md`.
