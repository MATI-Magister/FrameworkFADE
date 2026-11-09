---
name: fade-estructurar
description: Extraer datos con citas, autores y contradicciones. Usar en FADE para el rol estructurador de requerimientos dentro de a1.
---

# Estructurador de requerimientos

Localiza la raíz instalada de FADE (contiene `AGENTS.md` y `framework/engine.py`).
Si esta skill fue instalada fuera del repositorio, consulta `framework-location.json`
junto a este archivo. Ejecuta comandos desde esa raíz; no uses el directorio de la skill
como raíz del expediente.

Lee `skills/contrato.md`, `configuracion/framework.json`, `configuracion/roles.json`
y `roles/estructurador.md` de esa raíz. Estos documentos contienen las instrucciones adaptadas
al flujo actual; los originales del ZIP solo son referencia comparativa.

Extraer datos con citas, autores y contradicciones. No calificar madurez, resolver conflictos ni ampliar alcance.

Aplica `reglas/presentacion-resultados.md`: resultado breve del paso y siguiente
acción; enlaza el respaldo sin volcarlo en el chat. Conserva evidencia, identificadores
y versiones; los JSON son soporte interno. Usa el estado real del expediente y las comprobaciones
del motor. Invocar una skill no inicia, finaliza ni aprueba por sí mismo una etapa.

La correspondencia con el ZIP es `A1`; su especificación fuente está en
`referencias/onedrive-2026-11-02/a1_estructurador/estructurador_especificacion.md`. Solo consultar cuando sea necesario
aclarar el origen de una regla; no cargarla como instrucciones de sistema.
