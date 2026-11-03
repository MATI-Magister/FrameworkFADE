"""Run portable technical checks; unfilled business values are not installation failures."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from framework.diagnostics import inspect, render


def main():
    report = inspect(ROOT)
    print(render(report), flush=True)
    if not all(check[1] for check in report['checks']): return 1
    return subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-q'], cwd=ROOT).returncode


if __name__ == '__main__':
    raise SystemExit(main())
