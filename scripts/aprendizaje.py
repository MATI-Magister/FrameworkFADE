"""Prepare a versioned learning package from an accepted calculation and actual evidence."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from framework.engine import Workflow, now
from framework.learning import compare, render


def prepare(flow, baseline_file, actuals_file, changes_file, scenario='Base'):
    state = flow.read()
    if state['steps']['revision']['status'] != 'completado':
        raise ValueError('Se requiere una revisión final aprobada como línea base.')
    paths = [Path(p).resolve() for p in (baseline_file, actuals_file, changes_file)]
    if any(not p.is_relative_to(flow.base.resolve()) for p in paths):
        raise ValueError('Los insumos de cierre deben estar en el expediente.')
    baseline_path, actuals_path, changes_path = paths
    calculation = state['steps']['a4'].get('calculation', {})
    relative = str(baseline_path.relative_to(flow.root.resolve()))
    expected = calculation.get('files', {}).get(relative)
    if not expected or hashlib.sha256(baseline_path.read_bytes()).hexdigest() != expected:
        raise ValueError('La línea base no coincide con el cálculo revisado.')
    baseline_data = json.loads(baseline_path.read_text(encoding='utf-8'))
    selected = next((s for s in baseline_data['scenarios'] if s['name'] == scenario), None)
    if selected is None: raise ValueError('Escenario de línea base desconocido.')
    snapshot_path = (flow.root / state['steps']['a4']['rules_snapshot']).resolve()
    if not snapshot_path.is_relative_to(flow.base.resolve()): raise ValueError('Snapshot fuera del expediente.')
    snapshot = snapshot_path.read_bytes()
    if hashlib.sha256(snapshot).hexdigest() != state['steps']['a4']['rules_hash']:
        raise ValueError('Snapshot de la línea base alterado.')
    parameters = json.loads(snapshot)['configuration_parameters']['estimation']['process_method']
    result = compare(selected, json.loads(actuals_path.read_text(encoding='utf-8')),
        json.loads(changes_path.read_text(encoding='utf-8')), parameters.get('deviation_threshold'))
    result['inputs'] = {str(p.relative_to(flow.root.resolve())): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    folder = flow.base / '02-trabajo/aprendizaje' / now().replace(':', '-')
    folder.mkdir(parents=True, exist_ok=False)
    (folder / 'resultado.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    (folder / 'informe.md').write_text(render(result), encoding='utf-8')
    return folder


def main():
    p = argparse.ArgumentParser(description='Cierre postejecución; no altera etapas ni catálogos')
    p.add_argument('--project', required=True)
    p.add_argument('--baseline', required=True, type=Path)
    p.add_argument('--actuals', required=True, type=Path)
    p.add_argument('--changes', required=True, type=Path)
    p.add_argument('--scenario', default='Base', choices=['Base', 'Conservador'])
    args = p.parse_args()
    try:
        print(prepare(Workflow(ROOT, args.project), args.baseline, args.actuals, args.changes, args.scenario) / 'informe.md')
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f'Cierre no preparado: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
