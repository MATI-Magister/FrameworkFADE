"""Deterministic scoring of the user-supplied workbook's maturity model."""
import math


def calculate(model, scores, gap_types=None):
    gap_types = gap_types or {}
    criteria = {c['id']: c for c in model['criteria']}
    if set(scores) - set(criteria):
        raise ValueError('Hay identificadores de criterio desconocidos.')
    if set(gap_types) - set(criteria) or any(v not in ('informacion', 'validacion', 'condicion_conocida') for v in gap_types.values()):
        raise ValueError('Tipo de brecha inválido.')
    for key, value in scores.items():
        if value is None:
            continue
        if value == 'N/A':
            if not criteria[key]['allow_na']:
                raise ValueError(f'{key} no admite N/A.')
        elif type(value) is not int or value not in range(4):
            raise ValueError(f'{key}: usa 0, 1, 2, 3, N/A o null.')
    dimensions, gaps = [], []
    for dimension in model['dimensions']:
        items = [c for c in criteria.values() if c['dimension'] == dimension['id']]
        numeric = sum(type(scores.get(c['id'])) is int for c in items)
        included = dimension['core'] or numeric > 0
        obtained = maximum = 0
        for criterion in items:
            score = scores.get(criterion['id'])
            if score == 'N/A':
                continue
            maximum += 3 * criterion['weight']
            obtained += (score or 0) * criterion['weight']
            if score is None or score < 3:
                gaps.append({'id': criterion['id'], 'dimension': dimension['id'],
                             'score': score, 'name': criterion['name'],
                             'gap_type': gap_types.get(criterion['id'], 'validacion' if score == 2 else 'informacion'),
                             'priority': (3 - (score or 0)) * criterion['weight'] * dimension['weight'],
                             'question': criterion['question'], 'evidence': criterion['expected_evidence'],
                             'gap': criterion['gap'] if score is None or score <= 1 else 'Completar o validar la evidencia.',
                             'included_dimension': included})
        dimensions.append({'id': dimension['id'], 'name': dimension['name'], 'core': dimension['core'],
                           'weight': dimension['weight'], 'included': included,
                           'maturity': obtained / maximum if maximum else 0,
                           'obtained': obtained, 'maximum': maximum, 'evaluated': numeric,
                           'missing': sum(scores.get(c['id']) is None for c in items),
                           'na': sum(scores.get(c['id']) == 'N/A' for c in items)})
    weight = math.fsum(d['weight'] for d in dimensions if d['included'])
    overall = math.fsum(d['weight'] * d['maturity'] for d in dimensions if d['included']) / weight
    level = max(l['number'] for l in model['levels'] if overall + 1e-12 >= l['minimum'])
    capped = any(d['core'] and d['maturity'] + 1e-12 < model['core_floor'] for d in dimensions)
    if capped:
        level = min(level, model['core_level_cap'])
    if not any(type(v) is int for v in scores.values()):
        level = None
    gaps.sort(key=lambda item: (-item['priority'], item['id']))
    selected = next((l for l in model['levels'] if l['number'] == level), None)
    return {'overall': overall, 'level': selected['name'] if selected else 'Sin evaluar',
            'technique': selected['technique'] if selected else 'Evaluar evidencia antes de seleccionar técnica.',
            'core_cap_applied': capped, 'included_weight': weight,
            'dimensions': dimensions, 'gaps': gaps,
            'excluded_dimensions': [d['id'] for d in dimensions if not d['included']]}


def validate_evidence(model, entries):
    """Agent evidence is required for every explicit rating, including a real zero."""
    if not isinstance(entries, dict):
        raise ValueError('criteria debe ser un objeto por ID de criterio.')
    scores = {}
    for key, entry in entries.items():
        if not isinstance(entry, dict):
            raise ValueError(f'{key}: se requiere objeto con score y evidence.')
        score = entry.get('score')
        if entry.get('gap_type', 'informacion') not in ('informacion', 'validacion', 'condicion_conocida'):
            raise ValueError(f'{key}: tipo de brecha inválido.')
        if entry.get('gap_type') == 'condicion_conocida' and score is None:
            raise ValueError(f'{key}: una condición conocida requiere puntuación y evidencia.')
        if score is not None:
            if not isinstance(entry.get('evidence'), str) or not entry['evidence'].strip():
                raise ValueError(f'{key}: falta evidencia o explicación de ausencia.')
            if score == 3 and (not isinstance(entry.get('validated_by'), str) or not entry['validated_by'].strip()):
                raise ValueError(f'{key}: puntaje 3 exige identificar quién validó la información.')
        scores[key] = score
    calculate(model, scores)
    return scores


def render_report(project, result, model, model_hash):
    def clean(value):
        return str(value).replace('|', '\\|').replace('\n', ' ').replace('<', '&lt;').replace('>', '&gt;')
    lines = [f'# Madurez de la información · {project}', '',
             'Evaluación de cuánto permite conocer el requerimiento sobre las dimensiones de estimación.',
             'No representa esfuerzo, complejidad ni probabilidad de éxito.', '',
             f'**Resultado:** {result["overall"]:.1%} · **{result["level"]}**.', '',
             f'**Técnica sugerida por el modelo:** {result["technique"]}', '',
             '**Aceptación humana:** pendiente. El nivel no autoriza avanzar automáticamente.', '',
             '## Madurez por dimensión', '',
             '| Dimensión | Tipo | Madurez | Criterios sin evaluar | Estado |',
             '| --- | --- | --- | --- | --- |']
    for d in result['dimensions']:
        lines.append(f'| {d["id"]} · {d["name"]} | {"Núcleo" if d["core"] else "Complementaria"} | '
                     f'{format(d["maturity"], ".1%") if d["included"] else "No incluida"} | {d["missing"]} | '
                     f'{"Incluida en el promedio" if d["included"] else "Sin calificaciones numéricas"} |')
    lines += ['', '## Cómo interpretar el resultado', '',
              'Un criterio sin calificar sigue pendiente: no prueba ausencia de interfaces, datos o trabajo.',
              'Las complementarias excluidas permanecen visibles; un promedio alto no implica cobertura completa.',
              'La calificación 3 requiere información completa y validada, no solo una respuesta de la IA.', '']
    if result['core_cap_applied']:
        lines += ['Se aplica el tope N3 porque alguna dimensión núcleo está por debajo del 40 %. '
                  'El porcentaje ponderado se conserva; el tope limita el nivel.', '']
    lines += ['## Preparar el paso de N3 a N4', '',
              'Antes de pasar a componentes, el experto revisa las preguntas y decide si solicitar '
              'otra ronda o autorizar explícitamente el avance. Alcanzar N4 no autoriza el paso automáticamente.', '',
              'El objetivo N4 requiere al menos 60 % ponderado y cada dimensión núcleo con al menos 40 %. '
              'Las respuestas deben justificar cambios según la rúbrica; no garantizan un nivel por sí solas.', '']
    below = [d for d in result['dimensions'] if d['core'] and d['maturity'] + 1e-12 < model['core_floor']]
    if below:
        lines += ['**Dimensiones núcleo que mantienen el tope:** ' +
                  ', '.join(f'{d["id"]} · {d["name"]} ({d["maturity"]:.1%})' for d in below) + '.', '']
    lines += ['## Primeras diez preguntas por prioridad', '',
              'Índice = (3 − puntaje) × peso interno × peso de dimensión. Sin calificar usa 0 para priorizar.', '']
    questions = [item for item in result['gaps'] if item['gap_type'] != 'condicion_conocida']
    for item in questions[:10]:
        lines += [f'### {item["id"]} · {clean(item["name"])}', '',
                  clean(item['question']), '', f'Evidencia que permitiría mejorar la calificación: {clean(item["evidence"])}.', '',
                  f'Estado: {"sin evaluar" if item["score"] is None else item["score"]}; prioridad: {item["priority"]:.3f}.', '']
    lines += ['## Registro completo de brechas', '',
              '| Criterio | Tipo de brecha | Pregunta / condición | Evidencia esperada | Prioridad |', '| --- | --- | --- | --- | --- |']
    for item in result['gaps']:
        text = item['name'] if item['gap_type'] == 'condicion_conocida' else item['question']
        lines.append(f'| {item["id"]} | {item["gap_type"].replace("_", " ")} | {clean(text)} | {clean(item["evidence"])} | {item["priority"]:.3f} |')
    lines += ['', '## Trazabilidad', '', f'Modelo: {model["version"]}. Huella del catálogo: {model_hash}.',
              f'Fuente conservada: reglas/fuentes/{model["source"]["file"]}.',
              'Los cruces de consistencia de Ficha!A61:G75 deben revisarse aparte con la caracterización. '
              'Este cálculo no ejecuta las fórmulas de Excel ni esos cruces automáticamente.', '']
    return '\n'.join(lines)
