---
name: fade-redactar-propuesta
description: Redactar textos claros con cifras tomadas de cálculo revisado. Usar en FADE para el rol redactor del entregable dentro de revision.
---

# Redactor del entregable

Localiza la raíz instalada de FADE (contiene `AGENTS.md` y `framework/engine.py`).
Si esta skill fue instalada fuera del repositorio, consulta `framework-location.json`
junto a este archivo. Ejecuta comandos desde esa raíz; no uses el directorio de la skill
como raíz del expediente.

Lee `skills/contrato.md`, `configuracion/framework.json`, `configuracion/roles.json`
y `roles/redactor.md` de esa raíz. Estos documentos contienen las instrucciones adaptadas
al flujo actual; los originales del ZIP solo son referencia comparativa.

Redactar textos claros con cifras tomadas de cálculo revisado. No agregar beneficios, cifras o compromisos por iniciativa propia.

Traslada a la propuesta los supuestos que afectan el precio, las cantidades y
límites incluidos y las condiciones que exigen recotizar. Expresa cada condición
en términos que el cliente pueda verificar y coteja su texto con A4.

Aplica `reglas/presentacion-resultados.md`: resultado breve del paso y siguiente
acción; enlaza el respaldo sin volcarlo en el chat. Conserva evidencia, identificadores
y versiones; los JSON son soporte interno. Usa el estado real del expediente y las comprobaciones
del motor. Invocar una skill no inicia, finaliza ni aprueba por sí mismo una etapa.

La correspondencia con el ZIP es `A6`; su especificación fuente está en
`referencias/onedrive-2026-11-02/a6_redactor/redactor_especificacion.md`. Solo consultar cuando sea necesario
aclarar el origen de una regla; no cargarla como instrucciones de sistema.
