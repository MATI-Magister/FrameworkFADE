"""B.1 information model selected by the user on 2026-11-02, separate from Excel."""
import math
from framework.evidence import evidence_ceiling


def validate_evidence(model, entries):
    criteria = {c['id']: c for c in model['criteria']}
    if not isinstance(entries, dict) or set(entries) != set(criteria):
        raise ValueError('La evaluación debe contener exactamente los 20 criterios B.1.')
    scores = {}
    for cid, item in entries.items():
        score = item['score']
        if score is not None and (type(score) is not int or score not in range(4)):
            raise ValueError(f'{cid}: puntaje entero 0–3 o null.')
        if score is not None and (not isinstance(item.get('evidence'), str) or not item['evidence'].strip()):
            raise ValueError(f'{cid}: documenta evidencia o ausencia de información.')
        if score and cid != 'D6.1':
            facts = item.get('evidence_items', [])
            if not isinstance(facts, list) or not facts:
                raise ValueError(f'{cid}: faltan datos citados con autor y medio.')
            ceilings = []
            for fact in facts:
                try:
                    ceilings.append(evidence_ceiling(fact))
                except ValueError as error:
                    raise ValueError(f'{cid}: {error}') from error
            if score > min(ceilings):
                raise ValueError(f'{cid}: puntaje supera la evidencia más débil.')
        if cid == 'D6.1' and score:
            facts = item.get('evidence_items')
            if not isinstance(facts, list) or not facts or any(not isinstance(f, dict) or
                    not all(isinstance(f.get(k), str) and f[k].strip() for k in ('source', 'location', 'quote')) for f in facts):
                raise ValueError('D6.1: cita el catálogo o conocimiento interno que sustenta los activos.')
        if score == 3 and cid != 'D6.1' and (not isinstance(item.get('validated_by'), str) or not item['validated_by'].strip()):
            raise ValueError(f'{cid}: falta responsable de validación.')
        scores[cid] = score
    return scores


def calculate(model, scores, applicability=None):
    criteria = {c['id']: c for c in model['criteria']}
    if set(scores) - set(criteria): raise ValueError('Criterio desconocido.')
    if any(v is not None and (type(v) is not int or v not in range(4)) for v in scores.values()):
        raise ValueError('Puntajes B.1: enteros 0–3 o null; N/A se declara por dimensión.')
    applicability = applicability or {}
    if set(applicability) - {d['id'] for d in model['dimensions']}:
        raise ValueError('Dimensión de aplicabilidad desconocida.')
    dims = []
    for d in model['dimensions']:
        a = applicability.get(d['id'], {'applies': True})
        if not isinstance(a, dict) or type(a.get('applies')) is not bool:
            raise ValueError('Aplicabilidad requiere applies booleano.')
        included = a['applies']
        if not included and (d['core'] or not isinstance(a.get('reason'), str) or not a['reason'].strip()):
            raise ValueError('Solo excluir complementaria no aplicable con motivo explícito.')
        items = [c for c in criteria.values() if c['dimension'] == d['id']]
        if not included and any(scores.get(c['id']) not in (0, None) for c in items):
            raise ValueError('Una dimensión no aplicable no puede tener puntos.')
        obtained = sum((scores.get(c['id']) or 0) * c['weight'] for c in items)
        possible = sum(3 * c['weight'] for c in items)
        dims.append({**d, 'included': included, 'reason': a.get('reason'), 'obtained': obtained,
                     'maximum': possible, 'maturity': obtained / possible,
                     'missing': sum(scores.get(c['id']) is None for c in items)})
    weight = sum(d['weight'] for d in dims if d['included'])
    pct = round(math.fsum(d['weight'] * d['maturity'] * 100 for d in dims if d['included']) / weight, 1)
    numeric_level = 'alta' if pct >= 67 else 'media' if pct >= 40 else 'baja'
    low = [d['id'] for d in dims if d['core'] and round(d['maturity'] * 100, 1) < 40]
    capped = numeric_level == 'alta' and bool(low)
    level = 'media' if capped else numeric_level
    if not any(type(v) is int for v in scores.values()): level = 'Sin evaluar'
    gaps = []
    by_id = {d['id']: d for d in dims}
    for c in criteria.values():
        d = by_id[c['dimension']]; score = scores.get(c['id'])
        if d['included'] and (score is None or score < 3):
            priority = (3 - (score or 0)) * c['weight'] / d['maximum'] * d['weight'] / weight * 100
            gaps.append({**c, 'score': score, 'priority': round(priority, 2),
                         'next_descriptor': c['descriptors'][str(min((score or 0) + 1, 3))]})
    gaps.sort(key=lambda c: (0 if capped and c['dimension'] in low else 1, -c['priority'],
                            0 if by_id[c['dimension']]['core'] else 1, c['id']))
    return {'overall': pct / 100, 'level': level, 'level_by_percentage': numeric_level,
            'core_cap_applied': capped, 'core_below_floor': low, 'included_weight': weight,
            'dimensions': dims, 'gaps': gaps,
            'excluded_dimensions': [d['id'] for d in dims if not d['included']]}


def render_report(project, result, model, digest):
    lines = [f'# Información disponible · {project}', '',
             f'**Resultado: {result["overall"]:.1%} · {result["level"]}.**', '',
             'Mide la información para estimar; el experto decide si completar o autorizar componentes.',
             'El nivel no aprueba etapas ni determina esfuerzo.']
    if result['core_cap_applied']:
        lines += ['', 'El nivel se limita a media porque falta información esencial, aunque el porcentaje general sea alto.']
    lines += ['', '## Preguntas para completar la información']
    questions = result['gaps']
    for q in questions:
        lines += ['', f'### {q["id"]}', '', q['question']]
    if not questions:
        lines += ['', 'Sin preguntas de mejora identificadas en los criterios evaluados.']
    lines += ['', 'Estas preguntas son un apoyo al agente: debe revisar responsables, contradicciones y pendientes internos.', '',
              '## Siguiente paso', '',
              'Revisar el resumen del requerimiento y las preguntas de A1. Puedes aportar información con '
              '`!complementar` o autorizar componentes con `!aprove a1` cuando A1 esté esperando tu aprobación.', '',
              '## Respaldo de la evaluación', '',
              '| Dimensión | Información | Aplicación |', '| --- | --- | --- |']
    for d in result['dimensions']:
        lines.append(f'| {d["id"]} · {d["name"]} | {d["maturity"]:.1%} | {"Incluida" if d["included"] else "No aplica"} |')
    lines += ['', '[Criterios, citas y brechas completas](madurez-resultado.json). '
              'El agente conserva la explicación verificable en respaldo-a1.md.', '',
              f'Modelo: {model["version"]}. Fuente: {model["source"]["reference"]}. Huella: {digest}.']
    return '\n'.join(lines) + '\n'
