"""Fixed educational example, NOT the production COCOMO II implementation."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def scenario(data, name):
    size_key = 'size_ksloc_base' if name == 'Base' else 'size_ksloc_conservative'
    components = data['software_components']
    size = math.fsum(c[size_key] for c in components)
    exponent = data['B'] + .01 * math.fsum(data['scale_factors_nominal'].values())
    pm = data['A'] * size ** exponent * math.prod(data['effort_multipliers_nominal'].values())
    software_hours = pm * data['hours_per_person_month']
    assert math.isclose(sum(data['software_role_split'].values()), 1)
    rows = []
    for c in components:
        hours = software_hours * c[size_key] / size
        role_hours = {r: hours * fraction for r, fraction in data['software_role_split'].items()}
        cost = math.fsum(h * data['roles'][r]['rate_COP_hour'] for r, h in role_hours.items())
        rows.append({'id': c['id'], 'name': c['name'], 'method': 'COCOMO II (grupo)',
                     'hours': hours, 'cost': cost, 'role_hours': role_hours})
    config = data['configuration']
    config_hours = math.fsum((a['O'] + 4*a['M'] + a['P']) / 6 if name == 'Base' else a['P'] for a in config['activities'])
    rows.append({'id': config['id'], 'name': config['name'], 'method': 'Actividades externas',
                 'hours': config_hours, 'cost': config_hours * data['roles'][config['role']]['rate_COP_hour'],
                 'role_hours': {config['role']: config_hours}})
    by_id = {r['id']: r for r in rows}
    # One person per role. Engineering for next component can overlap prior QA.
    tasks = [dict(id='Config', component='C-005', role='Plataforma', dependencies=[])]
    tasks += [dict(id=task_id, component=component, role=role, dependencies=deps) for task_id, component, role, deps in [
        ('Dev1', 'C-001', 'Ingenieria', ['Config']), ('QA1', 'C-001', 'Calidad', ['Dev1']),
        ('Dev2', 'C-002', 'Ingenieria', ['QA1']), ('QA2', 'C-002', 'Calidad', ['Dev2']),
        ('Dev3', 'C-003', 'Ingenieria', ['QA2']), ('QA3', 'C-003', 'Calidad', ['Dev3']),
        ('Dev4', 'C-004', 'Ingenieria', ['QA2']), ('QA4', 'C-004', 'Calidad', ['Dev4'])]]
    availability, ends = {}, {}
    for task in tasks:
        role = task['role']
        task['start'] = max([availability.get(role, 0)] + [ends[d] for d in task['dependencies']])
        task['hours'] = by_id[task['component']]['role_hours'][role]
        task['end'] = task['start'] + task['hours'] / data['roles'][role]['hours_week']
        availability[role] = ends[task['id']] = task['end']
    for row in rows:
        local = [t for t in tasks if t['component'] == row['id']]
        row['start'] = min(t['start'] for t in local)
        row['end'] = max(t['end'] for t in local)
        row['duration'] = row['end'] - row['start']
        assert math.isclose(sum(t['hours'] for t in local), row['hours'])
    for i, task in enumerate(tasks):
        assert all(task['start'] >= ends[d] - 1e-10 for d in task['dependencies'])
        for other in tasks[i+1:]:
            if other['role'] == task['role']:
                assert min(task['end'], other['end']) <= max(task['start'], other['start']) + 1e-10
    assert math.isclose(sum(r['hours'] for r in rows[:4]), software_hours)
    reference_months = data['schedule_C'] * pm ** (data['schedule_D'] + .2*(exponent-data['B']))
    return {'name': name, 'size': size, 'E': exponent, 'pm': pm, 'software_hours': software_hours,
            'hours': math.fsum(r['hours'] for r in rows), 'cost': math.fsum(r['cost'] for r in rows),
            'duration': max(t['end'] for t in tasks), 'rows': rows, 'tasks': tasks,
            'software_schedule_reference_weeks': reference_months * data['weeks_per_month_for_reference']}


def money(value):
    return f'{value:,.0f}'.replace(',', '.')


def render(data, base, conservative):
    lines = ['# Ejemplo A4 · Portal de soporte', '',
        '**Demostración ficticia para revisar el formato y el método. No corresponde al piloto, '
        'no es una cotización y no activa A4.** Continúa el ejemplo de componentes con aclaraciones '
        'técnicas adicionales supuestas, sin registrar respuestas reales.', '',
        '## Resultado en palabras', '',
        f'Con las hipótesis del ejemplo, el escenario base requiere **{base["hours"]:.1f} horas-persona**, '
        f'un calendario de **{base["duration"]:.1f} semanas** y **{money(base["cost"])} COP de mano de obra**. '
        'La programación depende de la capacidad parcial y la secuencia declaradas; no es una fecha comprometida.', '',
        '## Dos escenarios del mismo alcance', '',
        '| Escenario | Horas-persona | Semanas del plan | Mano de obra (COP) |', '| --- | --- | --- | --- |']
    for s in (base, conservative):
        lines.append(f'| {s["name"]} | {s["hours"]:.1f} | {s["duration"]:.1f} | {money(s["cost"])} |')
    lines += ['', 'Base: tamaño técnico supuesto de 2,0 KSLOC y actividades de configuración ponderadas. '
        'Conservador: mismo alcance, tamaño técnico superior de 2,5 KSLOC y valores altos de configuración. '
        'El aumento de tamaño es incertidumbre de implementación, no nuevas funciones. No es un percentil '
        'ni recargo universal. En un caso real estos rangos necesitan evidencia.', '',
        '## Esfuerzo y costo por componente', '',
        '| Componente | Método y cobertura | Horas base | Horas conservadoras | Costo base (COP) | Costo conservador (COP) |',
        '| --- | --- | --- | --- | --- | --- |']
    for b, c in zip(base['rows'], conservative['rows']):
        lines.append(f'| {b["id"]} · {b["name"]} | {b["method"]} | {b["hours"]:.1f} | {c["hours"]:.1f} | {money(b["cost"])} | {money(c["cost"])} |')
    lines += [f'| **Total** | Sin coberturas duplicadas | **{base["hours"]:.1f}** | **{conservative["hours"]:.1f}** | **{money(base["cost"])}** | **{money(conservative["cost"])}** |', '',
        'COCOMO cubre el software nuevo C-001…C-004, incluidos diseño, código, pruebas y gestión técnica. '
        'C-005 es solo configuración de un conector soportado existente; su consumo por la aplicación '
        'ya está en el grupo de software. Si exige código propio o sus actividades ya estaban cubiertas, '
        'hay que revisar la matriz antes de sumar.', '',
        '## Equipo y tarifas ficticias', '',
        '| Rol agrupado | Personas | Horas efectivas/semana | Tarifa COP/hora |', '| --- | --- | --- | --- |']
    for role, values in data['roles'].items():
        lines.append(f'| {role} | 1 | {values["hours_week"]} | {money(values["rate_COP_hour"])} |')
    lines += ['', 'El reparto de esfuerzo software es 75 % Ingeniería (diseño, código y gestión técnica) '
        'y 25 % Calidad. Es una regla ficticia expresamente elegida para el ejemplo; no sale de COCOMO '
        'ni es un estándar aprobado. C-005 usa Plataforma. No se añade una segunda partida de pruebas/gestión.', '',
        '## Calendario por componente', '',
        'Semanas continuas desde el inicio, con la disponibilidad efectiva declarada, sin vacaciones '
        'adicionales ni esperas externas. C-005 precede el acceso; C-002 espera C-001 probado; '
        'C-003/C-004 esperan C-002. Ingeniería trabaja C-003 antes de C-004 y puede solaparse con Calidad.', '',
        '| Componente | Inicio base | Fin base | Duración base (semanas) | Duración conservadora (semanas) |',
        '| --- | --- | --- | --- | --- |']
    for b, c in zip(base['rows'], conservative['rows']):
        lines.append(f'| {b["id"]} | {b["start"]:.1f} | {b["end"]:.1f} | {b["duration"]:.1f} | {c["duration"]:.1f} |')
    lines += ['', 'Las duraciones por componente no se suman: C-003 y C-004 se solapan parcialmente. '
        'El script verifica precedencias y ausencia de sobreasignación por persona/rol.', '',
        f'Como contraste, la referencia nominal de duración COCOMO del grupo software es '
        f'{base["software_schedule_reference_weeks"]:.1f} semanas base y '
        f'{conservative["software_schedule_reference_weeks"]:.1f} conservadoras (convención 52/12 semanas/mes). '
        'El calendario de recursos incluye además C-005 y sus restricciones; no se suman las dos '
        'duraciones del mismo software. Su coherencia debe revisarse con el experto.', '',
        '## Anexo de cálculo reproducible', '',
        'Early Design COCOMO II.2000 de referencia, sin calibración local: A=2,94; B=0,91. '
        'Los cinco factores nominales son PREC=3,72; FLEX=3,04; RESL=4,24; TEAM=3,29; PMAT=4,68. '
        'PERS, RCPX, PDIF, PREX, FCIL, RUSE y SCED se eligen explícitamente nominales (=1) solo '
        'para la demostración. Ninguno se tomó del porcentaje de madurez.', '',
        f'E = 0,91 + 0,01 × 18,97 = {base["E"]:.4f}. Base: '
        f'2,94 × 2^{base["E"]:.4f} = {base["pm"]:.6f} personas-mes; '
        f'×152 = {base["software_hours"]:.6f} horas-persona de software.', '',
        'Se estima el grupo completo y luego se reparte por tamaño porque todos sus drivers son '
        'homogéneos en este caso simplificado. No se suman cuatro modelos independientes. '
        'Los tamaños base son 0,5 / 0,7 / 0,5 / 0,3 KSLOC para C-001…C-004; son hipótesis '
        'técnicas de ejemplo, no conversiones de XS o COSMIC. Conservador: 0,625 / 0,875 / '
        '0,625 / 0,375 KSLOC. Sin adaptación, código autogenerado ni modelo de reuso.', '',
        'Para C-005 se separan actividades de servicio fuera de la cobertura software:', '',
        '| Actividad de configuración | O (h) | M (h) | P (h) |', '| --- | --- | --- | --- |']
    for a in data['configuration']['activities']:
        lines.append(f'| {a["name"]} | {a["O"]} | {a["M"]} | {a["P"]} |')
    lines += ['', 'Base C-005 = suma((O+4M+P)/6) = 38 h; conservador = suma(P) = 60 h. '
        'Costo = suma(horas de cada rol × tarifa). Ejemplo C-005 base: 38 × 120.000 = '
        '4.560.000 COP. Los totales se calculan sin redondeos intermedios.', '',
        '## Exclusiones y pendientes antes de usarlo en un proyecto real', '',
        '| Código ilustrativo | Pregunta o entrega requerida |', '| --- | --- |',
        '| G-PRE-002 | ¿Qué método y evidencia de tamaño se aprobarán para el software real? |',
        '| G-PRE-003 | ¿Qué parámetros/calibración y cobertura COCOMO se aprobarán? |',
        '| G-PRE-004 | ¿Qué tarifas, reparto por roles y capacidad efectiva se aprobarán? |',
        '| G-PRE-005 | ¿Qué costos directos, impuestos y margen incluirá el entregable comercial? |',
        '| C-005-PRE-006 | ¿La solución de acceso puede resolverse solo configurando el conector existente? |', '',
        'Códigos nuevos ilustrativos, posteriores a los del ejemplo A3; no son asuntos reales del piloto. '
        'G-PRE-001 sobre dedicación sigue siendo el mismo asunto del ejemplo previo: el conjunto de '
        'capacidades de esta demostración es una hipótesis, no su cierre real. Costos de nube/licencias '
        'y condiciones comerciales están por confirmar: el total mostrado solo es mano de obra.', '',
        '## Fuentes y reproducción', '',
        'Datos ficticios: `ejemplos/a4/entradas.json`. Ejecutar `python scripts/ejemplo_a4.py` '
        'reproduce este informe y verifica reconciliación, precedencias y recursos. '
        'No modifica el estado del piloto ni habilita COCOMO en el motor.', '',
        'Referencia: USC, *COCOMO II Model Definition Manual* v2.1, secciones 1.2, 3.3, 4 y 8. '
        '[Texto del manual reproducido](https://studylib.net/doc/11638144/cocomo-ii-model-definition-manual-version-2.1). '
        'Las hipótesis de este ejemplo no son recomendaciones de esa fuente.', '',
        '**Aprobación:** pendiente. Este documento explica una propuesta metodológica, no autoriza una ejecución real.', '']
    return '\n'.join(lines)


if __name__ == '__main__':
    data = json.loads((ROOT / 'ejemplos/a4/entradas.json').read_text(encoding='utf-8'))
    base, conservative = scenario(data, 'Base'), scenario(data, 'Conservador')
    assert conservative['hours'] > base['hours'] and conservative['duration'] > base['duration']
    assert math.isclose(base['rows'][-1]['hours'], 38)
    assert math.isclose(base['rows'][-1]['cost'], 4560000)
    destination = ROOT / 'docs/ejemplo-a4-estimacion.md'
    destination.write_text(render(data, base, conservative), encoding='utf-8')
    print(json.dumps({s['name']: {k: round(s[k], 4) for k in ['hours', 'cost', 'duration', 'software_schedule_reference_weeks']} for s in (base, conservative)}, indent=2))
