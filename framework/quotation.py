"""Validate the quotation decision register before publishing A1 questions."""
import re
import unicodedata

REGISTER = 'filtro-cotizacion-a1.json'
GROUPS = (
    ('questions', 'Decisiones del cliente', ('question', 'decision', 'impact', 'why_now', 'source')),
    ('assumptions', 'Supuestos de cotización', ('assumption', 'limit', 'requote_when', 'source')),
    ('design', 'Pendientes de diseño', ('detail', 'source')),
    ('internal', 'Consultas internas', ('question', 'source')),
)
PARTIAL = re.compile(r'\b(?:primer[ao]? (?:entrega|fase|etapa)|(?:entrega|fase|etapa) (?:inicial|parcial|1)|mvp)\b')
TECHNICAL_DETAIL = re.compile(
    r'\b(?:campos? (?:de entrada|de salida|del mensaje)|payloads?|esquemas? json|'
    r'ejemplos? de (?:mensajes?|peticiones?|respuestas?)|contratos? (?:de la api|de api|tecnicos?)|'
    r'carga pico|transacciones por (?:segundo|minuto)|versiones? exactas?)\b'
)


def required(item, field):
    value = item.get(field) if isinstance(item, dict) else None
    if not isinstance(value, str) or not value.strip() or len(value.splitlines()) != 1:
        raise ValueError(f'Filtro de cotización: {field} requiere texto en una línea.')
    return value.strip()


def render_questions(data):
    if not isinstance(data, dict) or data.get('scope') not in ('full', 'partial'):
        raise ValueError('Filtro de cotización: indica alcance completo o parcial.')
    source = required(data, 'scope_source')
    partial = data['scope'] == 'partial'
    scope = required(data, 'partial_scope') if partial else 'Todo lo solicitado en las fuentes vigentes.'
    lines = ['# Preguntas y supuestos de cotización', '', f'**Alcance.** {scope}', '', f'**Fuente.** {source}', '']
    if partial:
        lines.extend([f'**Evidencia de alcance parcial.** {required(data, "partial_evidence")}', ''])
    labels = {'decision': 'Decisión', 'impact': 'Impacto', 'source': 'Fuente revisada',
              'limit': 'Límite incluido', 'requote_when': 'Condición de recotización',
              'why_now': 'Por qué hace falta decidir ahora'}
    seen = set()
    for group, title, fields in GROUPS:
        items = data.get(group)
        if not isinstance(items, list):
            raise ValueError(f'Filtro de cotización: {group} debe ser una lista, incluso si está vacía.')
        lines.extend([f'## {title}', ''])
        if not items:
            lines.extend(['Ninguno identificado.', ''])
        for item in items:
            code = required(item, 'id')
            if code in seen or not re.fullmatch(r'A1-(?:PRE|PEN)-\d{3,}', code):
                raise ValueError(f'Filtro de cotización: código inválido o repetido {code}.')
            seen.add(code)
            values = {field: required(item, field) for field in fields}
            if group == 'questions':
                plain = unicodedata.normalize('NFKD', values['question'].lower())
                plain = ''.join(c for c in plain if not unicodedata.combining(c))
                if not partial and (item.get('partial_scope') or PARTIAL.search(plain)):
                    raise ValueError(f'{code}: una pregunta sobre entrega parcial requiere alcance parcial sustentado.')
                if TECHNICAL_DETAIL.search(plain):
                    raise ValueError(f'{code}: difiere el detalle técnico a diseño o pregunta solo por la obligación comercial que afecta la oferta.')
            lines.extend([f'### {code}', '', values[fields[0]], ''])
            lines.extend(f'- **{labels[field]}.** {values[field]}' for field in fields[1:])
            if item.get('criterion'):
                lines.append(f'- **Criterio.** {required(item, "criterion")}')
            if item.get('owner'):
                lines.append(f'- **Responsable.** {required(item, "owner")}')
            lines.append('')
    return '\n'.join(lines)
