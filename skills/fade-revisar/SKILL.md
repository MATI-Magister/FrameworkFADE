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

En cotizaciones por paquetes, coteja las cantidades, los límites y las condiciones
de recotización de la propuesta con el respaldo de A4. Comprueba que cada unidad
esté cubierta una vez y que el trabajo común se cobre una sola vez.

Aplica `reglas/presentacion-resultados.md`: resultado breve del paso y siguiente
acción; enlaza el respaldo sin volcarlo en el chat. Conserva evidencia, identificadores
y versiones; los JSON son soporte interno. Usa el estado real del expediente y las comprobaciones
del motor. Invocar una skill no inicia, finaliza ni aprueba por sí mismo una etapa.
