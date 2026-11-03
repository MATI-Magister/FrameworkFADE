"""Role routing is metadata, not a provider-specific agent launcher."""
import json
from framework.configuration import inside, load_config


def load_roles(root):
    config = load_config(root)
    data = json.loads(inside(root, config['roles_file']).read_text(encoding='utf-8'))
    ids = set()
    for role in data['roles']:
        if not isinstance(role.get('id'), str) or not role['id'].strip(): raise ValueError('ID de rol inválido.')
        if role.get('stage') not in ('registro', 'a1', 'a2', 'a3', 'cierre', 'a4', 'revision', 'transversal', 'postejecucion'):
            raise ValueError('Etapa de rol desconocida.')
        if role['id'] in ids: raise ValueError('Rol repetido.')
        ids.add(role['id'])
        for field in ('instruction', 'skill'):
            if not inside(root, role[field]).is_file(): raise ValueError(f'Falta recurso de rol: {role[field]}')
        if role.get('source_specification') and not inside(root, role['source_specification']).is_file():
            raise ValueError('Falta especificación fuente del rol.')
    return data


def for_stage(root, stage):
    return [r for r in load_roles(root)['roles'] if r['stage'] == stage]
