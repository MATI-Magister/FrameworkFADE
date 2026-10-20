"""Idempotent local installation with no downloads."""
import subprocess
import sys
from pathlib import Path

if sys.version_info < (3, 10):
    raise SystemExit('Se requiere Python 3.10 o superior.')
root = Path(__file__).resolve().parents[1]
if not (root / 'proyectos/piloto/04-estado/estado.json').exists():
    subprocess.run([sys.executable, str(root / 'scripts/framework.py'), 'init', 'piloto'], check=True)
else:
    subprocess.run([sys.executable, str(root / 'scripts/framework.py'), 'board'], check=True)
print('Instalación lista. Lee AGENTS.md en tu herramienta IA y escribe !estado.')
