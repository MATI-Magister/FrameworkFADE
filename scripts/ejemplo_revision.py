"""Generate fictitious review and client documents; never approve a real project."""
import copy
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.ejemplo_a4 import scenario, money


def build_example():
    original = json.loads((ROOT / 'ejemplos/a4/entradas.json').read_text(encoding='utf-8'))
    revised = copy.deepcopy(original)
    # Hypothetical expert evidence: existing provider configuration reduces one activity.
    revised['configuration']['activities'][0].update(O=6, M=12, P=18)
    before = [scenario(original, name) for name in ('Base', 'Conservador')]
    after = [scenario(revised, name) for name in ('Base', 'Conservador')]
    return before, after


def render_review(before, after):
    lines = ['# Ejemplo · Revisión final del experto', '',
        '**Demostración ficticia, sin aprobación real.** Versiones ilustrativas: '
        'A4 v0.1 → revisión/cliente v0.2-demo. No corresponde al piloto.', '',
        '## Solicitud ilustrativa del experto', '',
        '«!ajustar C-005: el proveedor ya deja preconfigurado parte del conector. '
        'Revisar esa actividad con el anexo de configuración y recalcular ambos escenarios».', '',
        'EX-REV-01 es un anexo ficticio supuesto solo para mostrar cómo se fundamenta el ajuste. '
        'En un caso real deben existir fuente y responsable identificados. No es una instrucción '
        'real de aprobación, respuesta del usuario o cambio de reglas metodológicas.', '',
        '## Registro de ajustes', '',
        '| Código | Partida | Antes | Después | Razón y fuente | Estado |', '| --- | --- | --- | --- | --- | --- |',
        '| AJU-001 | C-005, configuración de conector/permisos | O/M/P: 12/18/30 h | O/M/P: 6/12/18 h | Preconfiguración provista por tercero; EX-REV-01 ficticio | Aplicado y verificado matemáticamente en el ejemplo; pendiente de aceptación |', '',
        'El resto de actividades, reglas, drivers, tarifas, capacidad y alcance se mantiene. '
        'Se recalcula A4: no se rebaja un total manualmente. El esfuerzo de C-005 pasa '
        'de 38 a 31 h base y de 60 a 48 h conservadoras. La reducción es 7/12 h, '
        '840.000/1.440.000 COP y 0,47/0,80 semanas, respectivamente.', '',
        '## Comparación para el experto', '',
        '| Escenario | Horas antes → después | Semanas antes → después | Mano de obra COP antes → después |',
        '| --- | --- | --- | --- |']
    for b, a in zip(before, after):
        lines.append(f'| {a["name"]} | {b["hours"]:.1f} → {a["hours"]:.1f} | {b["duration"]:.1f} → {a["duration"]:.1f} | {money(b["cost"])} → {money(a["cost"])} |')
    lines += ['', '## Comprobaciones realizadas', '',
        'Reconciliación de componentes/roles y costo; esfuerzo COCOMO del software sin cambio; '
        'actividad externa contada una sola vez; dependencias y capacidad comprobadas; '
        'dos escenarios recalculados; nube/licencias/comercial separados de mano de obra. '
        'El informe para cliente presenta las cifras revisadas y sus condiciones.', '',
        '## Decisión del experto', '',
        '**Pendiente.** Si pide otro ajuste, `!ajustar` reabre la revisión conservando '
        'la versión anterior. Si acepta el paquete real, `!aprove revision` registra '
        'su decisión sobre esa versión; este ejemplo no ejecuta esa operación. '
        'No se aprueba ni envía nada por generar estos documentos.', '',
        'El ejemplo de cliente limita su cifra a mano de obra. No es una propuesta '
        'comercial completa: nube, licencias, impuestos y margen requieren decisión '
        'antes de presentar un precio final. En un expediente real las brechas '
        'técnicas materiales deben aclararse o quedar fuera del alcance declarado.', '',
        '## Archivos de referencia', '',
        'Cliente: `docs/ejemplo-entregable-cliente.md`. Reproducción: '
        '`python scripts/ejemplo_revision.py`. Los originales ficticios de A4 '
        'permanecen en `docs/ejemplo-a4-estimacion.md` y `ejemplos/a4/entradas.json`.', '']
    return '\n'.join(lines)


def render_client(after):
    base, conservative = after
    lines = ['# Estimación de la solución · Portal de soporte', '',
        '**Ejemplo ficticio del documento para el cliente. No aprobado, no es una '
        'cotización real ni pertenece al piloto.** Versión v0.2-demo, 17 de octubre de 2026.', '',
        '## Objetivo de la solución', '',
        'Disponer de un portal donde los clientes registren solicitudes de soporte, '
        'adjunten archivos y consulten su estado. Los analistas podrán organizar '
        'la atención y actualizar los casos; el cliente recibirá avisos por correo.', '',
        '## Qué incluye', '',
        '| Código | Componente | Resultado esperado |', '| --- | --- | --- |',
        '| C-001 | Registro de solicitudes | Casos registrados con su información y archivos. |',
        '| C-002 | Gestión de solicitudes | Casos revisados, asignados y con estado actualizado. |',
        '| C-003 | Consulta de solicitudes | Clientes consultan el estado de sus casos. |',
        '| C-004 | Avisos por correo | Avisos asociados a los cambios de estado acordados. |',
        '| C-005 | Acceso corporativo | Acceso mediante configuración de un conector existente con el servicio de identidad. |', '',
        '## Resumen de la estimación', '',
        f'En el escenario base se estiman **{base["hours"]:.1f} horas-persona**, '
        f'**{base["duration"]:.1f} semanas** desde el inicio acordado y '
        f'**{money(base["cost"])} COP de mano de obra**. Las cifras dependen '
        'del alcance y de las condiciones de equipo y acceso descritas a continuación.', '',
        '| Escenario | Esfuerzo (horas-persona) | Duración aproximada (semanas) | Mano de obra (COP) |',
        '| --- | --- | --- | --- |']
    for s in after:
        lines.append(f'| {s["name"]} | {s["hours"]:.1f} | {s["duration"]:.1f} | {money(s["cost"])} |')
    lines += ['', 'Ambos escenarios incluyen la misma solución. El conservador considera '
        'mayor trabajo de implementación y configuración dentro de ese alcance; no '
        'incluye nuevas funcionalidades ni representa una garantía estadística.', '',
        '## Detalle por componente', '',
        '| Componente | Horas base | Horas conservadoras | Mano de obra base (COP) | Mano de obra conservadora (COP) |',
        '| --- | --- | --- | --- | --- |']
    for b, c in zip(base['rows'], conservative['rows']):
        lines.append(f'| {b["id"]} · {b["name"]} | {b["hours"]:.1f} | {c["hours"]:.1f} | {money(b["cost"])} | {money(c["cost"])} |')
    lines += [f'| **Total** | **{base["hours"]:.1f}** | **{conservative["hours"]:.1f}** | **{money(base["cost"])}** | **{money(conservative["cost"])}** |', '',
        'Horas-persona expresan trabajo; no equivalen a horas corridas ni días de calendario. '
        'Se calculó sin redondeos intermedios; las filas visibles pueden diferir del '
        'total por redondeo.', '',
        '## Cómo se ejecutaría', '',
        'Primero se configuraría el acceso corporativo. Luego se construirían registro '
        'y gestión de solicitudes, seguidos por consulta y avisos. Algunas pruebas '
        'se ejecutarían en paralelo con desarrollo de otro componente.', '',
        '| Componente | Inicio base (semana) | Fin base (semana) |', '| --- | --- | --- |']
    for r in sorted(base['rows'], key=lambda r: (r['start'], r['id'])):
        lines.append(f'| {r["id"]} | {r["start"]:.1f} | {r["end"]:.1f} |')
    lines += ['', 'El calendario supone una persona de Ingeniería y una de Calidad con '
        '30 horas efectivas semanales cada una y una de Plataforma con 15 horas '
        'semanales durante configuración. El plazo empieza con los accesos, '
        'ambientes y decisiones disponibles; esperas externas adicionales requieren '
        'replanificación. No se fija una fecha contractual de entrega.', '',
        '## Supuestos que sustentan las cifras', '',
        '- Se supone que el alcance funcional, estados, datos, archivos y avisos '
        'del ejemplo quedaron aclarados antes de la revisión final. Es una hipótesis '
        'didáctica, no el cierre real de los PRE/PEN de ejemplos anteriores.',
        '- Se usa el servicio de identidad existente mediante un conector soportado. '
        'El proveedor entrega parte de su configuración inicial; esta condición '
        'sustenta la reducción revisada de C-005.',
        '- El cliente proporciona documentación, accesos, ambientes y responsables '
        'disponibles para las validaciones. Si esas condiciones cambian, se revisarán '
        'esfuerzo y calendario.',
        '- Tarifas ficticias: Ingeniería 100.000 COP/h, Calidad 80.000 COP/h, '
        'Plataforma 120.000 COP/h. Reparto del software 75 % Ingeniería/25 % Calidad, '
        'elegido para esta demostración; no es productividad ni regla comercial aprobada.', '',
        '## Exclusiones y costos por confirmar', '',
        'Se excluyen chat, pagos, nuevos proveedores de identidad y cambios de alcance '
        'no descritos. El valor mostrado cubre **mano de obra**. Consumo de nube, '
        'licencias, servicios de terceros, impuestos, margen y precio de venta '
        'están por definir; no se consideran gratuitos ni incluidos.', '',
        '## Base y condiciones de revisión', '',
        'El desarrollo de software se contrastó con un modelo paramétrico COCOMO II '
        'de referencia y se distribuyó entre componentes. La configuración externa '
        'del acceso se estimó por actividades. En esta demostración no se duplican '
        'pruebas o gestión ya cubiertas por el software. Se emplearon tamaños y '
        'parámetros ficticios sin calibración local; un caso real requiere validarlos.', '',
        'La versión v0.2-demo incorpora el ajuste ilustrativo AJU-001 y sustituye '
        'sus cifras preliminares v0.1 para esta demostración. Los cálculos detallados '
        'y el motivo del cambio se conservan en el expediente de revisión.', '',
        '## Próximos pasos', '',
        'Validar alcance y condiciones con el cliente, confirmar equipo/disponibilidad '
        'y completar costos adicionales antes de establecer un precio comercial. '
        'La aprobación interna del experto se registra en el expediente sobre una '
        'versión identificada; no equivale a aceptación del cliente ni envío automático.', '',
        '**Estado de esta muestra:** pendiente de aprobación; no existe una aceptación '
        'real del experto o del cliente.', '']
    return '\n'.join(lines)


if __name__ == '__main__':
    before, after = build_example()
    assert math.isclose(before[0]['hours'] - after[0]['hours'], 7)
    assert math.isclose(before[0]['cost'] - after[0]['cost'], 840000)
    assert math.isclose(before[1]['hours'] - after[1]['hours'], 12)
    assert math.isclose(before[1]['cost'] - after[1]['cost'], 1440000)
    for b, a in zip(before, after):
        assert math.isclose(b['software_hours'], a['software_hours'])
        assert a['duration'] < b['duration']
    (ROOT / 'docs/ejemplo-revision-final.md').write_text(render_review(before, after), encoding='utf-8')
    (ROOT / 'docs/ejemplo-entregable-cliente.md').write_text(render_client(after), encoding='utf-8')
    print(json.dumps({s['name']: {k: round(s[k], 4) for k in ('hours', 'duration', 'cost')} for s in after}, indent=2))
