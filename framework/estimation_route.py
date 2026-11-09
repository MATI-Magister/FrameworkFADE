"""Read-only discovery of the shared method and project-specific evidence."""
from pathlib import Path

from framework.configuration import load_config


def describe(root, project):
    root = Path(root)
    config = load_config(root, project)
    e = config['estimation']
    route = e.get('unified_route')
    if not route:
        raise ValueError('Ruta unificada sin configurar.')
    base = root / 'proyectos' / project
    if not (base / '04-estado/estado.json').exists():
        raise ValueError('Proyecto sin inicializar.')
    lines = [f'# Ruta de estimación · {project}', '']
    if model := e.get('proposal_model'):
        lines += [f'Fuente: {model["source"]}. DatosExt ({len(model["sheets"]["DatosExt"])} filas utilizables) primero, '
                  f'IA ({len(model["sheets"]["IA"])} filas) después, y actividades O/M/P para lo que no tenga analogía.',
                  'Comparar la unidad y justificar la talla. Ver reglas/ruta-unificada-estimacion.md.', '']
    else:
        lines += ['Usar la tabla disponible y actividades O/M/P para trabajo sin cobertura.', '',
                  '| Tipo de trabajo | Horas por proceso |', '| --- | --- |']
        lines += [f'| {name} | {value} |' for name, value in e['process_method']['hours_per_process'].items()]
        lines.append('')
    lines += ['## Parámetros consolidados', '', f'Moneda: {e["currency"] or "por consolidar desde las fuentes del proyecto"}.',
              f'Costo horario: {e["cost_per_hour"] if e["cost_per_hour"] is not None else "por consolidar desde las fuentes del proyecto"}.',
              f'Roles con capacidad estructurada: {len(e["team"])}.', '',
              '## Fuentes que debe revisar el agente antes de preguntar', '']
    sources = set()
    for folder in ('01-entradas/respuestas', '01-entradas/contexto', '01-entradas/requerimientos'):
        sources.update(p for p in (base / folder).rglob('*') if p.is_file())
    for pattern in ('*supuestos*.md', '*supuestos*.json', 'adenda*.md', 'escenario*.json'):
        sources.update((base / '02-trabajo').glob(pattern))
    for filename in ('a1.md', 'a2.md', 'a3.md', 'cierre.md'):
        path = base / '03-entregables' / filename
        if path.exists(): sources.add(path)
    lines += ['- ' + p.relative_to(root).as_posix() for p in sorted(sources)]
    lines += ['', 'Consultar vigencia, autor y decisiones que sustituyen otras. Consolidar datos ya aportados en '
              '01-entradas/respuestas/parametros-estimacion.json, con fuente por parámetro. '
              'Una ausencia en JSON no demuestra ausencia en los documentos. Preguntar solo por contradicciones '
              'o decisiones materiales que ninguna fuente vigente resuelva. No modificar estados ni salidas aceptadas.']
    return '\n'.join(lines) + '\n'
