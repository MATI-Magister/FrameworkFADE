"""Component classifications from explicit, versioned bands; unknown is not zero."""
import math
import re


PROPOSAL_REGISTER = 'clasificacion-modelo-v2.json'


def proposal_key(dimensions, model):
    axes = model['dimensions']
    if not isinstance(dimensions, dict) or set(dimensions) != set(axes):
        raise ValueError('Se requieren las cinco dimensiones del Modelo Propuesta V2.')
    choices = model.get('classification_catalog', {}).get('choices', {})
    for axis in axes:
        value = dimensions[axis]
        if not isinstance(value, str) or not value.strip() or '|' in value or (axis in choices and value not in choices[axis]):
            raise ValueError(f'{axis}: usar una categoría exacta del Modelo Propuesta V2.')
    return '|'.join(dimensions[axis] for axis in axes)


def validate_proposal_register(register, a2_text, model):
    expected = set(re.findall(r'^\s*\|\s*(C-\d{3,})\s*\|', a2_text, re.M))
    rows = register.get('components') if isinstance(register, dict) else None
    if not expected or not isinstance(rows, list):
        raise ValueError('A3 requiere una clasificación y los códigos de componentes en la tabla de A2.')
    seen = set()
    for row in rows:
        component = row.get('id') if isinstance(row, dict) else None
        if not isinstance(component, str) or component not in expected or component in seen:
            raise ValueError(f'A3: componente inexistente o repetido: {component}.')
        seen.add(component)
        key = proposal_key(row.get('dimensions'), model)
        if key not in model['sheets']['IA']:
            raise ValueError(f'{component}: la combinación no existe en el Modelo Propuesta V2.')
        evidence = row.get('evidence')
        if (not isinstance(evidence, dict) or set(evidence) != set(model['dimensions']) or
                any(not isinstance(value, str) or not value.strip() for value in evidence.values())):
            raise ValueError(f'{component}: justifica las cinco dimensiones con evidencia o supuestos acotados.')
        if row.get('status') not in ('sustentada', 'provisional'):
            raise ValueError(f'{component}: indica si la clasificación es sustentada o provisional.')
    if missing := expected - seen:
        raise ValueError('A3: faltan clasificaciones de ' + ', '.join(sorted(missing)) + '.')


def validate_reuse_bands(bands):
    if not isinstance(bands, list) or len(bands) != 4:
        raise ValueError('Se requieren cuatro bandas de reutilización.')
    if [b.get('label') for b in bands if isinstance(b, dict)] != ['R1', 'R2', 'R3', 'R4']:
        raise ValueError('Las bandas deben estar ordenadas R1, R2, R3, R4.')
    previous = None
    for band in bands:
        for key in ('minimum', 'maximum'):
            v = band.get(key)
            if type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 100:
                raise ValueError('Límites de reutilización entre 0 y 100 %.')
        if band['minimum'] >= band['maximum']:
            raise ValueError('Banda de reutilización vacía o invertida.')
        if any(type(band.get(k)) is not bool for k in ('include_minimum', 'include_maximum')):
            raise ValueError('Indicar inclusión de límites con booleanos.')
        if previous is not None:
            if previous['maximum'] != band['minimum'] or previous['include_maximum'] == band['include_minimum']:
                raise ValueError('Bandas de reutilización con hueco o superposición.')
        previous = band
    if bands[0]['minimum'] != 0 or not bands[0]['include_minimum'] or bands[-1]['maximum'] != 100 or not bands[-1]['include_maximum']:
        raise ValueError('Las bandas deben cubrir desde 0 hasta 100 %, incluidos.')


def classify_reuse(percentage, bands):
    validate_reuse_bands(bands)
    if percentage is None: return None
    if type(percentage) not in (int, float) or not math.isfinite(percentage) or not 0 <= percentage <= 100:
        raise ValueError('Porcentaje de reutilización: número entre 0 y 100 o null.')
    for band in bands:
        lower = percentage >= band['minimum'] if band['include_minimum'] else percentage > band['minimum']
        upper = percentage <= band['maximum'] if band['include_maximum'] else percentage < band['maximum']
        if lower and upper: return band['label']
    raise ValueError('Porcentaje sin banda de reutilización.')
