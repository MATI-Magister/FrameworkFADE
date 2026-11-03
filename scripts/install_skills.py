"""Install repo-owned FADE skill adapters without copying business rules or data."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from framework.roles import load_roles


def install(root, destination):
    root = Path(root).resolve()
    destination = Path(destination).resolve()
    # Preflight all conflicts before writing. Never replace someone else's skill.
    plan = []
    for role in load_roles(root)['roles']:
        source = root / role['skill']
        folder = destination / source.parent.name
        marker = folder / 'framework-location.json'
        if folder.exists():
            if not marker.exists(): raise ValueError(f'Skill existente ajena a FADE: {folder}')
            previous = json.loads(marker.read_text(encoding='utf-8'))
            if previous.get('root') != str(root): raise ValueError(f'Skill de otra instalación: {folder}')
            existing = folder / 'SKILL.md'
            if existing.exists() and hashlib.sha256(existing.read_bytes()).hexdigest() != previous.get('installed_hash'):
                raise ValueError(f'Skill modificada localmente; conservar y revisar: {folder}')
        plan.append((source, folder))
    for source, folder in plan:
        folder.mkdir(parents=True, exist_ok=True)
        content = source.read_bytes()
        (folder / 'SKILL.md').write_bytes(content)
        (folder / 'framework-location.json').write_text(json.dumps({'root': str(root),
            'installed_hash': hashlib.sha256(content).hexdigest()}, ensure_ascii=False, indent=2), encoding='utf-8')
    return len(plan)


def main():
    p = argparse.ArgumentParser(description='Instala skills FADE en el directorio elegido por el operador')
    p.add_argument('--target', required=True, type=Path)
    args = p.parse_args()
    try:
        print(f'{install(ROOT, args.target)} skills instaladas en {args.target.resolve()}')
        return 0
    except (ValueError, OSError, KeyError) as error:
        print(f'No se instalaron las skills: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
