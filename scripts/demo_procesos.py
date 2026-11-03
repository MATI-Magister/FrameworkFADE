"""A reproducible fictional calculation; never creates projects or changes real parameters."""
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from framework.configuration import load_config
from framework.engine import now
from framework.process_estimation import project_estimate, render_project


def run(root):
    root = Path(root).resolve()
    payload = json.loads((root / 'ejemplos/procesos/demostracion.json').read_text(encoding='utf-8'))
    if payload.get('fictional') is not True: raise ValueError('La demostración debe estar marcada como ficticia.')
    payload['configuration']['classification'] = load_config(root)['classification']
    result = project_estimate(payload['input'], payload['configuration'], require_complete=True)
    base, conservative = result['scenarios']
    actual = {'base_hours': base['hours'], 'base_cost': base['cost'], 'base_weeks': base['duration_weeks'],
              'conservative_hours': conservative['hours'], 'conservative_cost': conservative['cost'],
              'conservative_weeks': conservative['duration_weeks']}
    if any(not math.isclose(actual[key], value, rel_tol=1e-9) for key, value in payload['expected'].items()):
        raise ValueError('La demostración no reproduce los valores esperados; revisar el cálculo.')
    digest = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()
    result['status'] = 'demostracion_ficticia_no_aprobada'
    result['fictional'] = True
    folder = root / 'insumos-locales/demo-procesos' / now().replace(':', '-')
    folder.mkdir(parents=True, exist_ok=False)
    (folder / 'entrada-y-parametros.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    (folder / 'resultado.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    report = '# Demostración ficticia · cálculo por procesos\n\n'
    report += 'Todos los importes, capacidades y factores de este caso son ficticios. No son una cotización ni parámetros aprobados.\n\n'
    report += render_project(result, digest, experimental=True)
    (folder / 'informe.md').write_text(report, encoding='utf-8')
    return folder


if __name__ == '__main__':
    try:
        print(run(ROOT) / 'informe.md')
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f'Demostración no generada: {error}', file=sys.stderr)
        raise SystemExit(1)
