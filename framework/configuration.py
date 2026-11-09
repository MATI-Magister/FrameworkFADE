"""Shared, provider-independent configuration. Missing business values stay missing."""
import copy
import json
import math
import re
from pathlib import Path


def inside(root, relative):
    root = Path(root).resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError('La ruta de configuración debe permanecer dentro del framework.')
    return path


def load_config(root, project=None):
    data = json.loads(inside(root, 'configuracion/framework.json').read_text(encoding='utf-8'))
    if project is not None:
        if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,63}', project):
            raise ValueError('Proyecto inválido para parámetros locales.')
        local = inside(root, f'proyectos/{project}/01-entradas/respuestas/parametros-estimacion.json')
        if local.exists():
            overlay = json.loads(local.read_text(encoding='utf-8'))
            allowed = {'currency', 'cost_per_hour', 'costing_mode', 'rates', 'team', 'cfo_parameters'}
            if set(overlay) != {'estimation', 'sources'} or not isinstance(overlay['estimation'], dict) or not overlay['estimation'].keys() <= allowed:
                raise ValueError('Parámetros locales: solo moneda, costo, equipo y fuentes; no cambian el método compartido.')
            if not isinstance(overlay['sources'], dict) or any(not isinstance(overlay['sources'].get(k), str) or not overlay['sources'][k].strip() for k in overlay['estimation']):
                raise ValueError('Cada parámetro local requiere una fuente identificable.')
            data['estimation'].update(overlay['estimation'])
            data['estimation']['project_sources'] = overlay['sources']
    if data.get('schema_version') != 1:
        raise ValueError('Versión de configuración desconocida.')
    operation = data['operation']
    from framework.classification import validate_reuse_bands
    validate_reuse_bands(data['classification']['reuse']['bands'])
    # Older installations may still carry the retired question cap.
    operation.pop('max_client_questions', None)
    if set(operation) != {'default_project', 'portal_port'}:
        raise ValueError('Parámetros de operación desconocidos; no se administran cantidades de sesiones.')
    port = operation['portal_port']
    if type(port) is not int or not 1024 <= port <= 65535:
        raise ValueError('Puerto inválido: usa un entero entre 1024 y 65535.')
    if not isinstance(operation['default_project'], str):
        raise ValueError('Proyecto predeterminado inválido.')
    policies = data['policies']
    # A settings change cannot silently relax expert acceptance or invent a rating.
    if policies != {'missing_complexity': 'por_confirmar', 'unknown_technology': 'por_confirmar',
                    'unspecified_technology': 'por_confirmar', 'infer_processes': 'proponer_para_revision',
                    'fast_track_bypasses_approval': False,
                    'component_scope_scale': 'validado_definido_supuesto',
                    'client_confirmation': 'directa_escrita_o_transcripcion_identificada'}:
        raise ValueError('Cambio de políticas pendiente de revisión; registrar primero la decisión.')
    e = data['estimation']
    if e.get('costing_mode') not in (None, 'por_rol', 'costo_unico'):
        raise ValueError('Costeo: por_rol, costo_unico o null.')
    if e['method'] != 'horas_por_proceso_en_evaluacion':
        raise ValueError('Método aún no soportado por esta configuración.')
    if e['currency'] is not None and (not isinstance(e['currency'], str) or not e['currency'].strip()):
        raise ValueError('Moneda vacía: usa null si no está definida.')
    if not isinstance(e['rates'], list) or not isinstance(e['team'], list):
        raise ValueError('Tarifas y equipo deben ser listas.')
    from framework.process_estimation import resource_capacities
    resource_capacities(e['team'])
    roles = set()
    for rate in e['rates']:
        if not isinstance(rate, dict) or not isinstance(rate.get('role'), str) or not rate['role'].strip() or rate['role'] in roles:
            raise ValueError('Tarifa con rol vacío o repetido.')
        roles.add(rate['role'])
        number(rate.get('amount'), 'tarifa', minimum=0, strict=True, required=True)
        if not isinstance(rate.get('source'), str) or not rate['source'].strip() or not isinstance(rate.get('unit'), str) or not rate['unit'].strip():
            raise ValueError('La tarifa requiere unidad y fuente.')
    for key in ('cost_per_hour', 'sprint_capacity_hours', 'weeks_per_sprint',
                'complex_route_value_threshold', 'complex_route_effort_threshold'):
        number(e[key], key, minimum=0, strict=True)
    for key in ('target_margin', 'minimum_margin'):
        number(e[key], key, minimum=0, maximum=1, upper_strict=True)
    number(e['infrastructure_surcharge'], 'infrastructure_surcharge', minimum=0)
    if e['target_margin'] is not None and e['minimum_margin'] is not None and e['minimum_margin'] > e['target_margin']:
        raise ValueError('El margen mínimo supera el objetivo.')
    p = e['process_method']
    route = e.get('unified_route')
    if route is not None:
        if (route.get('version') != 1 or route.get('primary') != 'process_table'
                or route.get('fallback') != 'activities_omp' or route.get('repeat_known_questions') is not False
                or not isinstance(route.get('source'), str) or not route['source'].strip()):
            raise ValueError('Ruta unificada inválida.')
    if p['status'] not in ('draft', 'approved'):
        raise ValueError('Estado del método inválido.')
    archetypes = {'aplicaciones', 'integracion', 'datos_ia', 'plataforma', 'seguridad', 'modernizacion'}
    maps = {'hours_per_process': archetypes, 'complexity_factors': {'baja', 'media', 'alta', 'muy_alta'},
            'environment_factors': {'T1', 'T2', 'T3', 'T4'}, 'reuse_factors': {'R1', 'R2', 'R3', 'R4'}}
    for key, keys in maps.items():
        value = p[key]
        if value is not None:
            if not isinstance(value, dict) or set(value) != keys:
                raise ValueError(f'{key}: claves incompletas o desconocidas.')
            for k, n in value.items():
                number(n, f'{key}.{k}', minimum=0, strict=True, required=True)
    for key in ('management_fraction', 'secondary_archetype_threshold', 'near_tie_margin', 'deviation_threshold'):
        number(p[key], key, minimum=0, maximum=1)
    count = p['recalibration_project_count']
    if count is not None and (type(count) is not int or count < 1):
        raise ValueError('Cantidad para recalibrar inválida.')
    block = p['first_block_hours']
    if block is not None:
        if not isinstance(block, dict) or set(block) != {'minimum', 'maximum'}:
            raise ValueError('Bloque: se requieren minimum y maximum.')
        for k, n in block.items(): number(n, k, minimum=0, strict=True, required=True)
        if block['minimum'] > block['maximum']: raise ValueError('Rango del bloque invertido.')
    bands = p['range_bands']
    if bands is not None:
        if not isinstance(bands, dict) or set(bands) != {'baja', 'media', 'alta'}:
            raise ValueError('Bandas: se requieren baja, media y alta.')
        for key, band in bands.items():
            if not isinstance(band, dict) or set(band) != {'optimistic', 'conservative'}:
                raise ValueError(f'Banda incompleta: {key}')
            number(band['optimistic'], key, minimum=-1, maximum=0, strict=True, required=True)
            number(band['conservative'], key, minimum=0, required=True)
    for path in data['catalogs'].values(): inside(root, path)
    inside(root, data['roles_file'])
    inside(root, data['source_candidates'])
    return data


def number(value, name, minimum=None, maximum=None, strict=False, upper_strict=False, required=False):
    if value is None and not required:
        return
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError(f'{name}: número finito requerido.')
    if minimum is not None and (value <= minimum if strict else value < minimum):
        raise ValueError(f'{name}: por debajo del límite permitido.')
    if maximum is not None and (value >= maximum if upper_strict else value > maximum):
        raise ValueError(f'{name}: por encima del límite permitido.')


def apply_configuration(root, rules, project=None):
    """Only business parameters enter the approval hash; UI settings do not."""
    config = load_config(root, project)
    result = copy.deepcopy(rules)
    e = config['estimation']
    for key in ('effort_unit', 'currency', 'rates', 'cfo_parameters', 'scenarios'):
        result[key] = copy.deepcopy(e[key])
    if e.get('costing_mode') == 'costo_unico' and e['cost_per_hour'] is not None and e['currency']:
        result['rates'] = [{'role': person['role'], 'amount': e['cost_per_hour'],
            'unit': e['currency'] + '/hora-persona', 'source': e['source']} for person in e['team']]
    result['capacity']['team'] = copy.deepcopy(e['team'])
    result['configuration_parameters'] = {'estimation': e, 'policies': config['policies']}
    result['configuration_parameters']['classification'] = copy.deepcopy(config['classification'])
    return result
