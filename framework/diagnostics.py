"""Read-only checks distinguish broken installation from unfilled business data."""
import hashlib
import json
import re
from pathlib import Path

from framework.configuration import inside, load_config
from framework.engine import Workflow, STEPS
from framework.roles import load_roles
from framework.portal import project_summaries


def inspect(root):
    root = Path(root)
    checks, pending, optional = [], [], []
    try:
        config = load_config(root)
        checks.append(('Configuración', True, 'Formato válido; no se administran sesiones.'))
    except (OSError, ValueError, KeyError, TypeError) as error:
        return {'checks': [('Configuración', False, str(error))], 'pending': [], 'ready': False}
    try:
        roles = load_roles(root)['roles']
        for role in roles:
            content = inside(root, role['skill']).read_text(encoding='utf-8')
            if not re.search(r'^name: [a-z0-9-]+$', content, re.M) or not re.search(r'^description: .+', content, re.M):
                raise ValueError('Cabecera de skill incompleta: ' + role['skill'])
        missing = set(STEPS) - {r['stage'] for r in roles}
        if missing: raise ValueError('Etapas sin roles: ' + ', '.join(sorted(missing)))
        checks.append(('Roles y skills', True, f'{len(roles)} responsabilidades, recursos presentes y todas las etapas cubiertas.'))
    except (OSError, ValueError, KeyError, TypeError) as error:
        checks.append(('Roles y skills', False, str(error)))
    flow = Workflow(root, config['operation']['default_project'])
    try:
        rules, _, _ = flow.rules()
        model = rules['maturity_model']
        if model.get('kind') != 'information_b1' or len(model['dimensions']) != 9 or len(model['criteria']) != 20:
            raise ValueError('El modelo activo no coincide con B.1 elegido por el usuario.')
        reference = inside(root, model['source']['reference'])
        if hashlib.sha256(reference.read_bytes()).hexdigest() != model['source']['sha256']:
            raise ValueError('La rúbrica fuente cambió: revisar y versionar el catálogo.')
        checks.append(('Modelo de información', True, 'B.1: 9 dimensiones y 20 criterios; fuente íntegra.'))
    except (OSError, ValueError, KeyError, TypeError) as error:
        checks.append(('Modelo de información', False, str(error)))
    for kind, path in config['catalogs'].items():
        target = inside(root, path)
        try:
            if not target.exists():
                pending.append(f'Inicializar catálogo {kind} con scripts/install.py')
                continue
            data = json.loads(target.read_text(encoding='utf-8'))
            field = {'assets': 'activos', 'technologies': 'tecnologias', 'projects': 'proyectos'}[kind]
            if not isinstance(data.get(field), list): raise ValueError('Lista de catálogo ausente.')
            checks.append((f'Catálogo {kind}', True, f'{len(data[field])} registros locales; vacío no significa experiencia demostrada.'))
        except (OSError, ValueError, KeyError, TypeError) as error:
            checks.append((f'Catálogo {kind}', False, str(error)))
    broken = [p['id'] for p in project_summaries(root) if p['health'] == 'error']
    checks.append(('Expedientes', not broken, 'Estados legibles.' if not broken else 'Revisar: ' + ', '.join(broken)))
    try:
        flow.validate_rules()
        if flow.path.exists():
            approval = flow.read().get('rules_approval')
            if not approval or approval['hash'] != flow.rules()[1]:
                pending.append('Aprobación explícita de reglas para el proyecto predeterminado')
        else: pending.append('Inicializar proyecto predeterminado')
    except (OSError, ValueError, KeyError, TypeError) as error:
        pending.append('Estimación real: ' + str(error))
    e = config['estimation']
    for key in ('currency', 'costing_mode', 'team'):
        if not e.get(key): pending.append('Definir ' + key)
    if e.get('costing_mode') == 'costo_unico' and e.get('cost_per_hour') is None:
        pending.append('Definir cost_per_hour (costo horario único del equipo)')
    if e.get('costing_mode') == 'por_rol' and not e['rates']:
        pending.append('Definir tarifas por rol')
    required = {'hours_per_process', 'complexity_factors', 'environment_factors', 'reuse_factors', 'management_fraction', 'range_bands'}
    for key, value in e['process_method'].items():
        if value is None:
            (pending if key in required else optional).append('Definir process_method.' + key)
    return {'checks': checks, 'pending': pending, 'optional': optional, 'ready': all(c[1] for c in checks) and not pending}


def render(report):
    lines = ['Comprobación local de FADE']
    lines += [f'{"OK" if passed else "ERROR"} · {name}: {detail}' for name, passed, detail in report['checks']]
    lines += ['Por confirmar · ' + p for p in report['pending']]
    lines += ['Opcional según uso · ' + p for p in report.get('optional', [])]
    lines.append('Instalación técnica: ' + ('correcta' if all(c[1] for c in report['checks']) else 'requiere corrección'))
    lines.append('Preparado para estimar con datos reales: ' + ('sí' if report['ready'] else 'todavía no; revisar pendientes y aprobaciones'))
    return '\n'.join(lines)
