"""Shared evidence rules for information criteria and component scope definition."""


def citation(value):
    if not isinstance(value, dict) or not all(isinstance(value.get(k), str) and value[k].strip()
            for k in ('source', 'location', 'quote')):
        raise ValueError('Cita incompleta: fuente, ubicación y texto literal requeridos.')


def evidence_ceiling(fact):
    citation(fact)
    if fact.get('author') not in ('cliente', 'equipo', 'no_identificado') or fact.get('medium') not in ('escrito_cliente', 'sesion', 'notas_internas'):
        raise ValueError('Origen de evidencia inválido.')
    if fact['author'] == 'cliente' and fact['medium'] == 'sesion' and not identified_speaker(fact):
        raise ValueError('La transcripción debe identificar al hablante del cliente.')
    confirmed = fact.get('confirmed', False)
    if type(confirmed) is not bool: raise ValueError('confirmed debe ser booleano.')
    ceiling = 2 if fact['author'] == 'cliente' and fact['medium'] == 'escrito_cliente' else 1
    if confirmed:
        confirmation = fact.get('confirmation', {})
        citation(confirmation)
        if confirmation.get('author') != 'cliente' or confirmation.get('medium') not in ('escrito_cliente', 'sesion'):
            raise ValueError('La confirmación debe proceder directamente del cliente, no de una nota interna.')
        if confirmation['medium'] == 'sesion' and not identified_speaker(confirmation):
            raise ValueError('La confirmación oral requiere transcripción con hablante identificado.')
        ceiling = 3
    return ceiling


def identified_speaker(value):
    return isinstance(value.get('speaker'), str) and bool(value['speaker'].strip())


def component_scope(processes):
    """The weakest process sets the label; no effect on effort factors or B.1 levels."""
    if not isinstance(processes, list) or not processes:
        return {'label': 'Supuesto', 'reason': 'Inventario de procesos por confirmar.', 'limiting_processes': []}
    levels, ids, reasons = [], [], []
    for process in processes:
        pid = process.get('id')
        if not isinstance(pid, str) or not pid.strip() or pid in ids:
            raise ValueError('Proceso sin ID o repetido al evaluar definición del componente.')
        ids.append(pid)
        facts = process.get('evidence_items')
        if process.get('origin') not in ('ficha', 'inferido'):
            raise ValueError('Cada proceso requiere origen ficha o inferido.')
        conflict = process.get('open_contradiction', False)
        if type(conflict) is not bool: raise ValueError('open_contradiction debe ser booleano.')
        if not facts:
            level, reason = 1, 'sin evidencia suficiente'
        elif not isinstance(facts, list):
            raise ValueError('evidence_items debe ser una lista de datos citados.')
        else:
            level = min(evidence_ceiling(fact) for fact in facts)
            reason = 'según la evidencia más débil'
        if process['origin'] == 'inferido' or conflict:
            level = 1
            reason = 'proceso inferido o contradicción abierta'
        levels.append(level); reasons.append(reason)
    weakest = min(levels)
    limiting = [pid for pid, level in zip(ids, levels) if level == weakest]
    return {'label': {1: 'Supuesto', 2: 'Definido', 3: 'Validado'}[weakest],
            'reason': '; '.join(f'{pid}: {reason}' for pid, level, reason in zip(ids, levels, reasons) if level == weakest),
            'limiting_processes': limiting}
