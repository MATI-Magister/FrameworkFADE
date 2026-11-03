"""One portable installation; preserve existing projects, catalogs and skill edits."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from framework.configuration import inside, load_config
from framework.engine import Workflow
from framework.roles import load_roles
from scripts.install_skills import install as install_skills


def install(root, skills_target=None):
    root = Path(root).resolve()
    config = load_config(root)
    load_roles(root)
    sources = root / 'referencias/onedrive-2026-11-02/datos'
    catalogs = []
    for kind, filename, array in [('assets', 'catalogo_activos.json', 'activos'),
                                 ('technologies', 'mapa_tecnologias.json', 'tecnologias'),
                                 ('projects', 'registro_proyectos.json', 'proyectos')]:
        source = sources / filename
        payload = json.loads(source.read_text(encoding='utf-8'))
        if payload[array]: raise ValueError('La plantilla de catálogo debe estar vacía, sin datos de ejemplo.')
        catalogs.append((inside(root, config['catalogs'][kind]), source.read_bytes()))
    flow = Workflow(root, config['operation']['default_project'])
    if skills_target is not None: install_skills(root, skills_target)
    for target, content in catalogs:
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists(): target.write_bytes(content)
    if not flow.path.exists(): flow.init()
    else: flow.read(); flow.board()
    return flow


def main():
    parser = argparse.ArgumentParser(description='Instala FADE sin descargas ni datos ficticios de operación')
    parser.add_argument('--skills-target', type=Path, help='Directorio de skills de la herramienta elegida (opcional)')
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        print('Se requiere Python 3.10 o superior.', file=sys.stderr)
        return 1
    try:
        flow = install(ROOT, args.skills_target)
        print(f'Instalación lista. Proyecto predeterminado: {flow.project}.')
        print('Lee AGENTS.md y escribe !estado. Verifica con python scripts/framework.py doctor.')
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f'Instalación incompleta: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
