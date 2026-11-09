"""One coverage ledger: table for eligible processes, O/M/P for uncovered work."""
import copy
import math

from framework.configuration import number
from framework.classification import proposal_key


def proposal_reference(item, estimation, quantity):
    model = estimation.get('proposal_model')
    if not model:
        raise ValueError('Falta el catálogo del Modelo Propuesta V2.')
    dimensions = item.get('dimensions')
    key = proposal_key(dimensions, model)
    size_basis = item.get('size_basis')
    if not isinstance(size_basis, str) or not size_basis.strip():
        raise ValueError(f'{item["id"]}: sustenta la talla y la unidad de comparación.')
    external_fit = item.get('external_fit')
    if type(external_fit) is not bool:
        raise ValueError(f'{item["id"]}: indica si la unidad es comparable con un proyecto completo de DatosExt.')
    if not external_fit:
        reason = item.get('external_exclusion')
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError(f'{item["id"]}: explica por qué DatosExt no es comparable.')
    if external_fit and quantity != 1:
        raise ValueError(f'{item["id"]}: una analogía con un proyecto completo de DatosExt requiere cantidad uno.')
    for sheet in ('DatosExt', 'IA') if external_fit else ('IA',):
        row = model['sheets'][sheet].get(key)
        if row is not None:
            hours, excel_row, records = row
            number(hours, 'horas de la referencia', minimum=0, strict=True, required=True)
            return hours, {'workbook': model['source'], 'sha256': model['sha256'], 'sheet': sheet,
                           'row': excel_row, 'records': records, 'dimensions': dimensions,
                           'size_basis': size_basis,
                           'external_exclusion': item.get('external_exclusion')}
    return None


def validate_package(package, item_id):
    if not isinstance(package, dict) or package.get('type') not in ('common', 'per_unit'):
        raise ValueError(f'{item_id}: indicar si el paquete es común o por unidad.')
    quantity = package.get('quantity')
    if type(quantity) is not int or quantity < 1 or (package['type'] == 'common' and quantity != 1):
        raise ValueError(f'{item_id}: cantidad entera positiva. El trabajo común se cuenta una sola vez.')
    for field in ('unit', 'assumption', 'limit', 'requote_when'):
        if not isinstance(package.get(field), str) or not package[field].strip():
            raise ValueError(f'{item_id}: falta {field} del paquete de cotización.')
    return {key: package[key] for key in ('type', 'quantity', 'unit', 'assumption', 'limit', 'requote_when')}


def calculate_unified(data, config):
    from framework.process_estimation import calculate

    estimation = config['estimation']
    if not estimation.get('unified_route'):
        raise ValueError('Ruta unificada no configurada.')
    parameters = estimation['process_method']
    management = parameters['management_fraction']
    number(management, 'gestión', minimum=0, maximum=1, required=True)
    expected = data.get('expected_work_ids')
    if (not isinstance(expected, list) or not expected or
            any(not isinstance(i, str) or not i.strip() for i in expected) or len(set(expected)) != len(expected)):
        raise ValueError('Inventario explícito y único expected_work_ids requerido para comprobar cobertura.')
    if not isinstance(data.get('coverage_source'), str) or not data['coverage_source'].strip():
        raise ValueError('Identificar la fuente A2/adenda del inventario de trabajo.')
    components = data['components']
    if not isinstance(components, list) or not components:
        raise ValueError('Se requieren componentes.')
    packaged = any(isinstance(item, dict) and 'package' in item
                   for component in components if isinstance(component.get('work_items'), list)
                   for item in component['work_items'])
    seen, ids, item_ids, ledger = set(), set(), set(), []
    rows = {'Base': [], 'Conservador': []}
    optimistic = 0
    for component in components:
        cid = component['id']
        if not isinstance(cid, str) or not cid.strip() or cid in ids:
            raise ValueError('Componente vacío o duplicado.')
        ids.add(cid)
        if not isinstance(component.get('source'), str) or not component['source'].strip():
            raise ValueError(f'{cid}: fuente requerida.')
        items = component.get('work_items')
        if not isinstance(items, list) or not items:
            raise ValueError(f'{cid}: partidas explícitas requeridas.')
        totals = {s: [0.0, 0.0] for s in rows}
        for item in items:
            iid = item['id']
            if not isinstance(iid, str) or not iid.strip() or iid in item_ids:
                raise ValueError('Partida vacía o duplicada.')
            item_ids.add(iid)
            package = validate_package(item.get('package'), iid) if packaged else None
            for field in ('description', 'source'):
                if not isinstance(item.get(field), str) or not item[field].strip():
                    raise ValueError(f'{iid}: falta {field}.')
            coverage = item.get('covers')
            if (not isinstance(coverage, list) or not coverage or
                    any(not isinstance(i, str) or not i.strip() for i in coverage) or
                    len(set(coverage)) != len(coverage) or seen.intersection(coverage)):
                raise ValueError(f'{iid}: cobertura vacía o duplicada; no sumar métodos sobre el mismo trabajo.')
            seen.update(coverage)
            if item.get('kind') not in ('process', 'activity', 'analogy'):
                raise ValueError(f'{iid}: kind debe ser process, analogy o activity.')
            if type(item.get('includes_management')) is not bool:
                raise ValueError(f'{iid}: declarar si las horas ya incluyen gestión.')
            if not isinstance(item.get('routing_reason'), str) or not item['routing_reason'].strip():
                raise ValueError(f'{iid}: explicar cobertura y selección de método.')
            process = {**component, **item, 'id': cid, 'processes': coverage}
            factors_ready = all(process.get(field) in (parameters.get(key) or {}) for field, key in
                [('archetype', 'hours_per_process'), ('complexity', 'complexity_factors'),
                 ('environment', 'environment_factors'), ('reuse', 'reuse_factors')])
            # Unknown classes stay unknown; they do not become neutral multipliers.
            use_table = item['kind'] == 'process' and factors_ready and process.get('reuse_percentage') is not None
            reference = proposal_reference(item, estimation, package['quantity'] if package else 1) if item['kind'] == 'analogy' else None
            if reference:
                if item.get('omp') is not None:
                    raise ValueError(f'{iid}: analogía con cobertura. Retira la valoración O/M/P de la misma unidad.')
                base, basis = reference
                levels = ('baja', 'media', 'alta')
                info, experience = data.get('information_level'), data.get('experience_level')
                if info not in levels or (experience is not None and experience not in levels):
                    raise ValueError('Nivel de información o experiencia inválido para las bandas de cotización.')
                confidence = min(info, experience, key=levels.index) if experience is not None else info
                band = parameters['range_bands'][confidence]
                conservative = base * (1 + band['conservative'])
                low = base * (1 + band['optimistic'])
                method = 'proposal_model'
                basis['band'] = confidence
            elif use_table:
                if item.get('omp') is not None:
                    raise ValueError(f'{iid}: proceso cubierto por tabla; no añadir otra valoración O/M/P.')
                p = copy.deepcopy(parameters)
                p['management_fraction'] = 0
                bands = (config.get('classification') or {}).get('reuse', {}).get('bands')
                levels = ['baja', 'media', 'alta']
                info, experience = data.get('information_level'), data.get('experience_level')
                if info not in levels or experience is not None and experience not in levels:
                    raise ValueError('Nivel de información válido requerido para seleccionar la banda de tabla.')
                confidence = min(info, experience, key=levels.index) if experience is not None else info
                calculated = calculate([process], p, confidence, bands)
                base, conservative = calculated['base_hours'], calculated['conservative_hours']
                low = calculated['optimistic_reference_hours']
                if package:
                    # Coverage IDs track scope. Quantity tracks equivalent process occurrences.
                    base, conservative, low = (hours / len(coverage) for hours in (base, conservative, low))
                method = 'process_table'
                basis = {'archetype': process['archetype'], 'processes': coverage,
                         'hours_per_process': p['hours_per_process'][process['archetype']],
                         'complexity': process['complexity'], 'environment': process['environment'],
                         'reuse': process['reuse'], 'reuse_percentage': process['reuse_percentage'],
                         'band': confidence}
            else:
                omp = item.get('omp')
                if not isinstance(omp, dict) or set(omp) != {'optimistic', 'likely', 'pessimistic'}:
                    raise ValueError(f'{iid}: falta rango O/M/P de actividad; usar evidencia existente o proponer juicio explícito, no volver a pedir tabla de productividad.')
                low, likely, conservative = (omp[k] for k in ('optimistic', 'likely', 'pessimistic'))
                for value in (low, likely, conservative):
                    number(value, iid, minimum=0, required=True)
                if not 0 <= low <= likely <= conservative or conservative == 0:
                    raise ValueError(f'{iid}: rango O/M/P invertido o sin trabajo.')
                base = (low + 4 * likely + conservative) / 6
                method, basis = 'activities_omp', dict(omp)
            if package:
                base, conservative, low = (hours * package['quantity'] for hours in (base, conservative, low))
            extra = 0 if item['includes_management'] else management
            for value in (base, conservative, low):
                number(value, iid + ' horas calculadas', minimum=0, required=True)
            for scenario, value in [('Base', base), ('Conservador', conservative)]:
                totals[scenario][0] += value
                totals[scenario][1] += value * extra
            optimistic += low * (1 + extra)
            ledger.append({'id': iid, 'component': cid, 'description': item['description'],
                           'covers': coverage, 'method': method, 'basis': basis,
                           'source': item['source'], 'routing_reason': item['routing_reason'],
                           'includes_management': item['includes_management'],
                           'base_hours': base, 'conservative_hours': conservative,
                           'management_fraction_added': extra})
            if package:
                ledger[-1]['package'] = package
        for scenario, (technical, coordination) in totals.items():
            rows[scenario].append({'id': cid, 'hours': technical,
                                   'management_hours': coordination, 'source': component['source']})
    if seen != set(expected):
        raise ValueError('La cobertura no coincide con A2/adenda: faltan ' + str(sorted(set(expected) - seen)) +
                         '; sobran ' + str(sorted(seen - set(expected))))
    totals = {s: math.fsum(r['hours'] + r['management_hours'] for r in listed) for s, listed in rows.items()}
    return {'status': 'experimental_no_aprobado', 'method': 'unified_processes_activities',
            'components': rows['Base'], 'scenario_rows': rows, 'coverage': ledger,
            'table_source': parameters.get('source', 'configuracion/framework.json'),
            'table_source_sha256': parameters.get('source_sha256'),
            'coverage_source': data['coverage_source'], 'base_hours': totals['Base'],
            'conservative_hours': totals['Conservador'], 'optimistic_reference_hours': optimistic,
            'band_basis': ('Modelo Propuesta V2 por analogía: DatosExt primero, luego IA. '
                           'Las referencias usan las bandas configuradas. ' if any(row['method'] == 'proposal_model' for row in ledger) else '')
                          + 'Base de actividades = (O + 4M + P)/6; Conservador = P.',
            'notes': ['Parámetros iniciales autorizados para uso; no demuestran calibración.',
                      'Cada unidad de trabajo se cubre una sola vez. Gestión solo donde no esté incluida.']}


def render_coverage(result):
    def cell(value):
        return str(value).replace('|', '\\|').replace('\n', ' ')
    lines = ['# Cobertura y fundamento del cálculo', '',
             'Cada unidad del inventario se estima una sola vez. Las horas siguientes son previas '
             'a la gestión adicional indicada por partida.', '',
             'Inventario de referencia: ' + cell(result['coverage_source']), '']
    if any(item['method'] == 'process_table' for item in result['coverage']):
        lines += ['Tabla anterior: ' + cell(result['table_source']), '',
                  'Huella de la fuente: ' + cell(result['table_source_sha256'] or 'ver snapshot de reglas'), '']
    for item in result['coverage']:
        label = {'process_table': 'Tabla por proceso', 'proposal_model': 'Modelo Propuesta V2',
                 'activities_omp': 'Actividades O/M/P'}[item['method']]
        lines += [f'## {cell(item["id"])} · {cell(item["description"])}', '',
                  f'Componente: {cell(item["component"])}. Método: {label}.', '',
                  'Cubre: ' + ', '.join(cell(i) for i in item['covers']) + '.', '',
                  cell(item['routing_reason']), '',
                  '| Base (horas-persona) | Conservador (horas-persona) | Gestión adicional |',
                  '| --- | --- | --- |',
                  f'| {item["base_hours"]:.2f} | {item["conservative_hours"]:.2f} | {item["management_fraction_added"]:.0%} |', '',
                  'Fundamento: ' + '; '.join(f'{cell(k)}: {cell(v)}' for k, v in item['basis'].items()), '',
                  'Fuente: ' + cell(item['source']), '']
        if 'package' in item:
            package = item['package']
            label = 'Trabajo común' if package['type'] == 'common' else 'Trabajo por unidad'
            lines += [f'**{label}.** Cantidad {package["quantity"]}. Unidad {cell(package["unit"])}.', '',
                      f'**Supuesto.** {cell(package["assumption"])}', '',
                      f'**Límite incluido.** {cell(package["limit"])}', '',
                      f'**Requiere recotizar si** {cell(package["requote_when"])}', '']
    return '\n'.join(lines) + '\n'
