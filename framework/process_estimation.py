"""Explicit-parameter process sizing and feasible resource planning; no implicit approvals."""
import math
from framework.configuration import number
from framework.classification import classify_reuse


def calculate(components, parameters, information_level, reuse_bands=None):
    if information_level not in ('baja', 'media', 'alta'):
        raise ValueError('Nivel de información confirmado requerido: baja, media o alta.')
    required = ('hours_per_process', 'complexity_factors', 'environment_factors',
                'reuse_factors', 'management_fraction', 'range_bands')
    missing = [k for k in required if parameters.get(k) is None]
    if missing: raise ValueError('Parámetros por confirmar: ' + ', '.join(missing))
    number(parameters['management_fraction'], 'gestión', minimum=0, maximum=1, required=True)
    band = parameters['range_bands'][information_level]
    number(band['conservative'], 'banda conservadora', minimum=0, required=True)
    number(band['optimistic'], 'banda optimista', minimum=-1, maximum=0, strict=True, required=True)
    if not isinstance(components, list) or not components:
        raise ValueError('Se requieren componentes con procesos identificados.')
    ids, processes, rows = set(), set(), []
    for c in components:
        cid = c['id']
        if not isinstance(cid, str) or not cid.strip() or cid in ids:
            raise ValueError('ID de componente vacío o repetido.')
        ids.add(cid)
        if not isinstance(c.get('source'), str) or not c['source'].strip():
            raise ValueError(f'{cid}: falta fuente de la clasificación.')
        if 'reuse_percentage' in c:
            actual = classify_reuse(c['reuse_percentage'], reuse_bands)
            if actual is None or actual != c.get('reuse'):
                raise ValueError(f'{cid}: la clase de reúso no corresponde al porcentaje y escala vigentes.')
        listed = c['processes']
        if not isinstance(listed, list) or not listed:
            raise ValueError(f'{cid}: lista explícita de procesos requerida.')
        for pid in listed:
            if not isinstance(pid, str) or not pid.strip() or pid in processes:
                raise ValueError('Proceso duplicado o inválido; cada proceso se estima una sola vez.')
            processes.add(pid)
        try:
            hpp = parameters['hours_per_process'][c['archetype']]
            factors = [parameters[key][c[field]] for key, field in
                       [('complexity_factors', 'complexity'), ('environment_factors', 'environment'), ('reuse_factors', 'reuse')]]
        except KeyError as error:
            raise ValueError(f'{cid}: clasificación o factor sin definir: {error}') from error
        for n in [hpp, *factors]: number(n, 'factor', minimum=0, strict=True, required=True)
        hours = len(listed) * hpp
        for factor in factors: hours *= factor
        number(hours, 'horas calculadas', minimum=0, strict=True, required=True)
        rows.append({'id': cid, 'process_count': len(listed), 'hours': hours, 'source': c['source']})
    subtotal = math.fsum(c['hours'] for c in rows)
    management = subtotal * parameters['management_fraction']
    base = subtotal + management
    return {'status': 'experimental_no_aprobado', 'method': 'horas_por_proceso',
            'components': rows, 'subtotal_hours': subtotal, 'management_hours': management,
            'base_hours': base, 'conservative_hours': base * (1 + band['conservative']),
            'optimistic_reference_hours': base * (1 + band['optimistic']),
            'duration': None, 'cost': None,
            'notes': ['No combinar con COCOMO sobre la misma cobertura.',
                      'Gestión agregada una sola vez. No es una duración calendario ni un precio.',
                      'El optimista es solo referencia según INC-006; las bandas numéricas aún requieren calibración.']}


def fractions(value, label):
    if not isinstance(value, dict) or not value:
        raise ValueError(f'{label}: reparto por rol requerido.')
    for role, fraction in value.items():
        if not isinstance(role, str) or not role.strip(): raise ValueError('Rol inválido.')
        number(fraction, label, minimum=0, maximum=1, required=True)
    if not math.isclose(math.fsum(value.values()), 1, abs_tol=1e-9, rel_tol=0):
        raise ValueError(f'{label}: las fracciones deben sumar 1.')
    return value


def resource_capacities(team):
    result = {}
    for item in team:
        role = item['role']
        if not isinstance(role, str) or not role.strip() or role in result:
            raise ValueError('Rol vacío o repetido en equipo; consolidar su capacidad.')
        if not isinstance(item.get('source'), str) or not item['source'].strip():
            raise ValueError(f'{role}: fuente de capacidad requerida.')
        if type(item['people']) is not int or item['people'] < 1:
            raise ValueError('Personas por rol: entero positivo.')
        number(item['hours_per_week'], role, minimum=0, maximum=168, strict=True, required=True)
        number(item['allocation'], role, minimum=0, maximum=1, strict=True, required=True)
        result[role] = item['people'] * item['hours_per_week'] * item['allocation']
    return result


def schedule(components, workloads, capacity):
    """Deterministic feasible schedule. Each task consumes its role pool; not an optimizer."""
    by_id = {c['id']: c for c in components}
    remaining, ends, free, tasks, timing = list(by_id), {}, {}, [], {}
    for c in components:
        deps = c.get('dependencies')
        if not isinstance(deps, list) or len(set(deps)) != len(deps) or any(d not in by_id or d == c['id'] for d in deps):
            raise ValueError(f'{c["id"]}: dependencias explícitas, únicas y válidas requeridas.')
    while remaining:
        ready = next((cid for cid in remaining if all(d in ends for d in by_id[cid]['dependencies'])), None)
        if ready is None: raise ValueError('Hay un ciclo de dependencias entre componentes.')
        dependency_end = max((ends[d] for d in by_id[ready]['dependencies']), default=0)
        local = []
        for role, hours in workloads[ready].items():
            if hours == 0: continue
            if role not in capacity: raise ValueError(f'Falta capacidad de {role}.')
            start = max(dependency_end, free.get(role, 0))
            finish = start + hours / capacity[role]
            task = {'component': ready, 'role': role, 'hours': hours, 'start_week': start, 'end_week': finish}
            tasks.append(task); local.append(task); free[role] = finish
        start = min((t['start_week'] for t in local), default=dependency_end)
        ends[ready] = max((t['end_week'] for t in local), default=dependency_end)
        timing[ready] = {'start_week': start, 'end_week': ends[ready], 'duration_weeks': ends[ready] - start}
        remaining.remove(ready)
    return {'tasks': tasks, 'components': timing, 'duration_weeks': max(ends.values(), default=0),
            'basis': 'Semanas continuas con capacidad constante y dependencias entre componentes. Las cargas de roles de un mismo componente se pueden solapar; validar esa hipótesis con el experto. Sin fechas, vacaciones ni esperas no declaradas. Plan factible según estos supuestos, no optimizado.'}


def project_estimate(data, config, require_complete=False):
    """Compute effort, cost and calendar when explicit inputs are present; never invent missing data."""
    estimation = config['estimation']
    info = data['information_level']
    experience = data.get('experience_level')
    levels = ['baja', 'media', 'alta']
    if info not in levels or experience is not None and experience not in levels:
        raise ValueError('Nivel de información o experiencia inválido.')
    if require_complete and (experience is None or not all(isinstance(data.get(k), str) and data[k].strip()
            for k in ('information_confirmed_by', 'experience_confirmed_by', 'source'))):
        raise ValueError('Falta experiencia o confirmación del experto sobre información/experiencia.')
    if require_complete and any('reuse_percentage' not in c for c in data['components']):
        raise ValueError('El cálculo completo requiere porcentaje de reúso explícito por componente.')
    confidence = min(info, experience, key=levels.index) if experience is not None else info
    bands = (config.get('classification') or {}).get('reuse', {}).get('bands')
    result = calculate(data['components'], estimation['process_method'], confidence, bands)
    # Cost and duration belong to each scenario; remove obsolete unknown placeholders.
    result.pop('cost', None)
    result.pop('duration', None)
    result.update(confidence=confidence if experience is not None else None,
                  band_basis='Confianza = menor nivel entre información y experiencia confirmadas.' if experience is not None else
                  'Ensayo solo con información; experiencia/confianza por confirmar.')
    components = data['components']
    by_id = {c['id']: c for c in components}
    management_fraction = estimation['process_method']['management_fraction']
    missing = []
    can_plan = all(c.get('role_split') and 'dependencies' in c for c in components)
    if not can_plan: missing.append('Repartos por rol y dependencias de cada componente')
    management_roles = data.get('management_role_split')
    if management_fraction and not management_roles:
        missing.append('Reparto de gestión por rol'); can_plan = False
    if management_roles: fractions(management_roles, 'Gestión')
    capacity = resource_capacities(estimation['team'])
    if not capacity: missing.append('Capacidad del equipo')
    rates = {}
    if estimation.get('costing_mode') == 'por_rol':
        for rate in estimation['rates']:
            if rate['role'] in rates: raise ValueError('Tarifa duplicada por rol.')
            if rate['unit'] not in (f'{estimation["currency"]}/hora', f'{estimation["currency"]}/hora-persona'):
                raise ValueError('La tarifa debe estar en la moneda configurada por hora o por hora-persona.')
            number(rate['amount'], 'tarifa', minimum=0, strict=True, required=True)
            if not rate.get('source'): raise ValueError('Fuente de tarifa requerida.')
            rates[rate['role']] = rate['amount']
    elif estimation.get('costing_mode') == 'costo_unico' and estimation.get('cost_per_hour') is not None:
        number(estimation['cost_per_hour'], 'costo único', minimum=0, strict=True, required=True)
    else:
        missing.append('Elección de costeo y tarifas/costo horario')
    if not estimation['currency']: missing.append('Moneda')
    direct_costs = data.get('direct_costs')
    if not isinstance(direct_costs, list) or not isinstance(data.get('direct_costs_source'), str) or not data['direct_costs_source'].strip():
        missing.append('Costos directos o decisión explícita de no incluirlos'); direct_costs = None
    else:
        seen = set()
        for cost in direct_costs:
            if cost['id'] in seen: raise ValueError('Costo directo duplicado.')
            seen.add(cost['id'])
            if cost.get('component') is not None and cost['component'] not in by_id:
                raise ValueError('Costo directo para componente inexistente.')
            number(cost['amount'], 'costo directo', minimum=0, required=True)
            if not cost.get('source'): raise ValueError('Costo directo sin fuente.')
    scenarios = []
    for name, total in [('Base', result['base_hours']), ('Conservador', result['conservative_hours'])]:
        multiplier = total / result['base_hours']
        rows, workloads = [], {}
        for row in result['components']:
            cid = row['id']; technical = row['hours'] * multiplier
            management = technical * management_fraction
            workload = {}
            if can_plan:
                split = fractions(by_id[cid]['role_split'], cid)
                for role, fraction in split.items(): workload[role] = technical * fraction
                for role, fraction in (management_roles or {}).items():
                    workload[role] = workload.get(role, 0) + management * fraction
            workloads[cid] = workload
            rows.append({'id': cid, 'name': by_id[cid].get('name', cid), 'technical_hours': technical,
                         'management_hours': management, 'hours': technical + management, 'role_hours': workload})
        plan = schedule(components, workloads, capacity) if can_plan and capacity else None
        labor_total = None
        if can_plan and estimation['currency']:
            all_roles = {role for w in workloads.values() for role, h in w.items() if h > 0}
            if estimation.get('costing_mode') == 'por_rol' and all_roles <= rates.keys():
                for row in rows: row['labor_cost'] = math.fsum(h * rates[r] for r, h in row['role_hours'].items() if h)
            elif estimation.get('costing_mode') == 'costo_unico' and estimation.get('cost_per_hour') is not None:
                for row in rows: row['labor_cost'] = row['hours'] * estimation['cost_per_hour']
            else:
                missing.append('Tarifas de todos los roles usados')
            if all('labor_cost' in r for r in rows): labor_total = math.fsum(r['labor_cost'] for r in rows)
        direct_total = math.fsum(c['amount'] for c in direct_costs) if direct_costs is not None else None
        total_cost = labor_total + direct_total if labor_total is not None and direct_total is not None else None
        for row in rows:
            row['direct_cost'] = math.fsum(c['amount'] for c in direct_costs if c.get('component') == row['id']) if direct_costs is not None else None
            row['cost'] = row['labor_cost'] + row['direct_cost'] if 'labor_cost' in row and row['direct_cost'] is not None else None
            if plan: row.update(plan['components'][row['id']])
        if not math.isclose(math.fsum(r['hours'] for r in rows), total, rel_tol=1e-9):
            raise ValueError('El reparto por componente no reconcilia con el total.')
        scenarios.append({'name': name, 'hours': total, 'rows': rows, 'schedule': plan,
            'duration_weeks': plan['duration_weeks'] if plan else None,
            'labor_cost': labor_total, 'direct_cost': direct_total, 'cost': total_cost,
            'unallocated_direct_cost': math.fsum(c['amount'] for c in direct_costs if c.get('component') is None) if direct_costs is not None else None})
    if any(s['cost'] is None for s in scenarios): missing.append('Costo completo por confirmar')
    if any(s['schedule'] is None for s in scenarios): missing.append('Calendario por confirmar')
    result['scenarios'] = scenarios
    result['currency'] = estimation['currency']
    result['pending'] = list(dict.fromkeys(missing))
    if require_complete and missing: raise ValueError('Estimación incompleta: ' + '; '.join(result['pending']))
    return result


def render_project(result, digest, experimental=True):
    def cell(value): return str(value).replace('|', '\\|').replace('\n', ' ')
    def display(value): return 'por confirmar' if value is None else f'{value:,.1f}'
    lines = ['# Estimación por componentes', '',
             '**Ensayo experimental, sin aprobación.**' if experimental else '**Cálculo con reglas aprobadas; pendiente de revisión final.**', '',
             'El esfuerzo incluye gestión una sola vez. El calendario depende de los recursos y precedencias declarados.', '',
             f'Moneda: {cell(result["currency"] or "por confirmar")}. Precio comercial: no incluido; se presenta costo de ejecución.', '',
             '| Escenario | Horas-persona | Semanas del plan | Costo de ejecución |', '| --- | --- | --- | --- |']
    for s in result['scenarios']:
        lines.append(f'| {s["name"]} | {display(s["hours"])} | {display(s["duration_weeks"])} | {display(s["cost"])} |')
    for s in result['scenarios']:
        lines += ['', f'## Componentes · {s["name"]}', '',
                  '| Componente | Horas-persona | Costo | Inicio (semana) | Fin (semana) |', '| --- | --- | --- | --- | --- |']
        for r in s['rows']:
            lines.append(f'| {cell(r["id"])} · {cell(r["name"])} | {display(r["hours"])} | {display(r["cost"])} | {display(r.get("start_week"))} | {display(r.get("end_week"))} |')
        lines += ['', f'Costos directos comunes fuera de componentes: {display(s["unallocated_direct_cost"])}.']
        if s['schedule']: lines += ['', s['schedule']['basis']]
    lines += ['', '## Pendientes y condiciones', '']
    lines += ['- ' + cell(p) for p in result['pending']] or ['Sin pendientes numéricos detectados; la revisión semántica y aceptación siguen siendo humanas.']
    lines += ['', result['band_basis'], '',
              f'Optimista solo como referencia: {display(result["optimistic_reference_hours"])} horas-persona.', '',
              '## Trazabilidad', '', f'Huella de reglas y parámetros: {digest}.',
              'Conservar entrada, resultado y fuentes de esta ejecución. No sumar otro método sobre la misma cobertura.']
    return '\n'.join(lines) + '\n'
