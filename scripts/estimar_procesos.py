"""Compute locally without approving or finalizing A4."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from framework.configuration import load_config
from framework.engine import Workflow, now
from framework.process_estimation import project_estimate, render_project


def main():
    parser = argparse.ArgumentParser(description='Calculo por procesos; no finaliza ni aprueba A4')
    parser.add_argument('--project', required=True)
    parser.add_argument('--input', type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--experimental', action='store_true')
    mode.add_argument('--approved', action='store_true', help='Usar snapshot aprobado del intento A4 activo')
    args = parser.parse_args()
    try:
        flow = Workflow(ROOT, args.project)
        state = flow.read()
        if args.approved:
            item = state['steps']['a4']
            if item['status'] != 'en_ejecucion' or not item.get('rules_snapshot'):
                raise ValueError('Primero iniciar A4 con reglas completas y aprobadas.')
            path = (ROOT / item['rules_snapshot']).resolve()
            if not path.is_relative_to(flow.base.resolve()): raise ValueError('Snapshot fuera del expediente.')
            raw = path.read_bytes()
            digest = hashlib.sha256(raw).hexdigest()
            if digest != item['rules_hash'] or flow.rules()[1] != digest:
                raise ValueError('Snapshot o reglas cambiados; requiere reintentar y aprobar de nuevo.')
            config = json.loads(raw)['configuration_parameters']
        else:
            config = load_config(ROOT)
            digest = flow.rules()[1]
        source = args.input.resolve()
        if not source.is_relative_to(flow.base.resolve()):
            raise ValueError('La entrada debe estar en el expediente indicado.')
        data = json.loads(source.read_text(encoding='utf-8'))
        result = project_estimate(data, config, require_complete=args.approved)
        result['status'] = 'calculado_pendiente_revision' if args.approved else 'experimental_no_aprobado'
        result['rules_hash'] = digest
        result['input_hash'] = hashlib.sha256(source.read_bytes()).hexdigest()
        prefix = 'calculo-a4-' if args.approved else 'ensayo-procesos-'
        folder = flow.base / '02-trabajo' / (prefix + now().replace(':', '-'))
        folder.mkdir(parents=True, exist_ok=False)
        (folder / 'resultado.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        (folder / 'informe.md').write_text(render_project(result, digest, experimental=not args.approved), encoding='utf-8')
        if args.approved:
            flow.record_calculation([source, folder / 'resultado.json', folder / 'informe.md'], digest)
        print(folder / 'informe.md')
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f'Calculo no ejecutado: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
