"""Prepare evidence and calculate a readable report; never approve or finish A1."""
import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from framework.engine import Workflow, now
from framework.maturity import calculate, render_report, validate_evidence


def main():
    parser = argparse.ArgumentParser(description='Modelo de madurez importado del Excel')
    parser.add_argument('--project', default='piloto')
    parser.add_argument('command', choices=['template', 'evaluate'])
    parser.add_argument('--input', type=Path)
    args = parser.parse_args()
    try:
        flow = Workflow(ROOT, args.project)
        flow.read()
        raw = (ROOT / 'reglas/modelo-madurez.json').read_bytes()
        model = json.loads(raw)
        model_hash = hashlib.sha256(raw).hexdigest()
        target = flow.base / '01-entradas/respuestas/evaluacion-madurez.json'
        if args.command == 'template':
            if target.exists():
                raise ValueError('Ya existe la evaluación; no se sobrescribe.')
            data = {'model_hash': model_hash, 'criteria': {
                c['id']: {'score': None, 'evidence': '', 'validated_by': '', 'gap_type': 'informacion'} for c in model['criteria']}}
            target.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            print(target)
        else:
            data = json.loads((args.input or target).read_text(encoding='utf-8'))
            if data.get('model_hash') != model_hash:
                raise ValueError('La evaluación pertenece a otra versión del catálogo; revisar antes de recalcular.')
            scores = validate_evidence(model, data['criteria'])
            gap_types = {k: v['gap_type'] for k, v in data['criteria'].items() if 'gap_type' in v}
            result = calculate(model, scores, gap_types)
            result['model_hash'] = model_hash
            result['input_hash'] = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
            result['evaluation_input'] = data
            work = flow.base / '02-trabajo'
            previous = work / 'madurez-resultado.json'
            report = work / 'evaluacion-madurez.md'
            if previous.exists() or report.exists():
                archive = work / 'madurez-rondas' / now().replace(':', '-')
                archive.mkdir(parents=True)
                for old in (previous, report):
                    if old.exists():
                        shutil.copy2(old, archive / old.name)
            (work / 'madurez-resultado.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
            report.write_text(render_report(args.project, result, model, model_hash), encoding='utf-8')
            print(f'{result["overall"]:.1%} - {result["level"]}. Informe: {report}')
        return 0
    except (ValueError, OSError, KeyError) as error:
        print(f'No se ejecutó: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
