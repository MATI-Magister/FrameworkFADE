"""Post-execution comparison. Numerical differences do not establish their causes."""
import math
from framework.configuration import number


def compare(baseline, actuals, changes, threshold=None):
    if not isinstance(actuals.get('source'), str) or not actuals['source'].strip():
        raise ValueError('Falta fuente de horas reales.')
    if threshold is not None: number(threshold, 'umbral de desviación', minimum=0, maximum=1, required=True)
    rows = baseline['rows']
    base = {r['id']: r['hours'] for r in rows}
    if len(base) != len(rows): raise ValueError('Componente duplicado en línea base.')
    for value in base.values(): number(value, 'horas de línea base', minimum=0, required=True)
    actual = {}
    for item in actuals['components']:
        if item['id'] in actual: raise ValueError('Horas reales duplicadas; consolidar por componente.')
        number(item['hours'], 'horas reales', minimum=0, required=True)
        actual[item['id']] = item['hours']
    delta = {cid: 0 for cid in base}
    seen = set()
    for item in changes:
        if item['id'] in seen or item['component'] not in base:
            raise ValueError('Cambio repetido o componente de cambio desconocido.')
        seen.add(item['id'])
        number(item['hours'], 'cambio de alcance', required=True)
        if not item.get('source') or not item.get('approved_by'):
            raise ValueError('Todo cambio requiere fuente y aprobación humana.')
        delta[item['component']] += item['hours']
    report = []
    for cid, hours in base.items():
        adjusted = hours + delta[cid]
        if adjusted < 0: raise ValueError('Un cambio no puede dejar una línea base negativa.')
        real = actual.get(cid)
        difference = real - adjusted if real is not None else None
        deviation = difference / adjusted if difference is not None and adjusted else None
        report.append({'id': cid, 'baseline_hours': hours, 'approved_change_hours': delta[cid],
            'adjusted_hours': adjusted, 'actual_hours': real, 'difference_hours': difference,
            'deviation': deviation, 'exceeds_threshold': abs(deviation) > threshold if deviation is not None and threshold is not None else None,
            'cause': 'por_confirmar'})
    extra = sorted(set(actual) - set(base))
    missing = sorted(set(base) - set(actual))
    return {'status': 'propuesto_pendiente_confirmacion_lider', 'components': report,
            'unassigned_components': extra, 'components_without_actuals': missing,
            'adjusted_baseline_hours': math.fsum(r['adjusted_hours'] for r in report),
            'actual_hours': math.fsum(actual[cid] for cid in base if cid in actual) if not missing else None,
            'source': actuals['source'], 'threshold': threshold,
            'notes': ['Las causas, reutilización real y activos nuevos requieren evidencia y confirmación del líder.',
                      'No se modifican catálogos ni parámetros. Los registros sin correspondencia se revisan por separado.']}


def render(result):
    def fmt(v): return 'por confirmar' if v is None else f'{v:.1f}'
    lines = ['# Cierre de ejecución y aprendizaje', '', '**Propuesta pendiente de confirmación del líder.**', '',
             '| Componente | Base (h) | Cambio aprobado (h) | Base ajustada (h) | Real (h) | Diferencia (h) |',
             '| --- | --- | --- | --- | --- | --- |']
    for r in result['components']:
        cid = str(r['id']).replace('|', '\\|').replace('\n', ' ')
        lines.append('| ' + cid + ' | ' + ' | '.join(fmt(r[k]) for k in
            ('baseline_hours', 'approved_change_hours', 'adjusted_hours', 'actual_hours', 'difference_hours')) + ' |')
    lines += ['', '## Qué debe confirmar el líder', '']
    for i, r in enumerate(result['components'], 1):
        lines += [f'- APR-{i:03d}: explicar con evidencia el resultado del componente {r["id"]}; causa por confirmar.']
    if result['components_without_actuals']: lines += ['', 'Componentes sin horas: ' + ', '.join(result['components_without_actuals'])]
    if result['unassigned_components']: lines += ['', 'Registros sin correspondencia: ' + ', '.join(result['unassigned_components'])]
    lines += ['', 'Una línea base cero no admite desviación porcentual; se conserva la diferencia en horas.']
    lines += ['', *result['notes']]
    return '\n'.join(lines) + '\n'
