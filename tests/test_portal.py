import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from framework.engine import Workflow, STEPS
from framework.portal import make_handler, project_summaries

ROOT = Path(__file__).resolve().parents[1]


class FakeSocket:
    def __init__(self, request):
        self.request = io.BytesIO(request)
        self.response = io.BytesIO()

    def makefile(self, *args, **kwargs):
        return self.request

    def sendall(self, data):
        self.response.write(data)


class PortalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / 'tests')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT / 'tablero', self.root / 'tablero')

    def project(self, name):
        flow = Workflow(self.root, name)
        flow.init()
        return flow

    def request(self, path, method='GET'):
        request = FakeSocket(f'{method} {path} HTTP/1.0\r\nHost: localhost\r\n\r\n'.encode())
        handler = make_handler(self.root)
        handler.log_message = lambda *args: None
        handler(request, ('127.0.0.1', 12345), SimpleNamespace())
        headers, body = request.response.getvalue().split(b'\r\n\r\n', 1)
        return headers, body

    def test_lists_all_folders_including_uninitialized_and_corrupt(self):
        self.project('uno'); self.project('dos')
        (self.root / 'proyectos/sin-estado').mkdir()
        bad = self.root / 'proyectos/roto/04-estado'
        bad.mkdir(parents=True); (bad / 'estado.json').write_text('{bad', encoding='utf-8')
        projects = {p['id']: p for p in project_summaries(self.root)}
        self.assertEqual(set(projects), {'uno', 'dos', 'sin-estado', 'roto'})
        self.assertEqual(projects['sin-estado']['health'], 'sin_inicializar')
        self.assertEqual(projects['roto']['health'], 'error')
        self.assertEqual(projects['uno']['next_step'], 'registro')

    def test_progress_is_independent_and_api_reads_changes_without_restart(self):
        first = self.project('uno'); self.project('dos')
        first.start('registro')
        (first.base / '03-entregables/registro.md').write_text('Inventario', encoding='utf-8')
        first.finish('registro')
        projects = {p['id']: p for p in project_summaries(self.root)}
        self.assertEqual(projects['uno']['completed'], 1)
        self.assertEqual(projects['uno']['next_step'], 'a1')
        self.assertEqual(projects['dos']['completed'], 0)
        first.start('a1'); first.block('a1', '<script>pendiente</script>')
        headers, body = self.request('/api/projects')
        self.assertIn(b'200', headers)
        updated = {p['id']: p for p in json.loads(body)['projects']}
        self.assertEqual(updated['uno']['steps']['a1']['status'], 'bloqueado')

    def test_portal_is_read_only_and_does_not_expose_project_documents(self):
        flow = self.project('uno')
        before = flow.path.read_bytes()
        for path in ('/proyectos/uno/04-estado/estado.json', '/README.md', '/%2e%2e/.env', '/.git/config'):
            headers, _ = self.request(path)
            self.assertIn(b'404', headers)
        headers, _ = self.request('/api/projects', 'POST')
        self.assertIn(b'501', headers)
        self.request('/api/projects')
        self.assertEqual(before, flow.path.read_bytes())

    def test_missing_step_is_visible_error_not_fabricated_pending(self):
        flow = self.project('uno')
        state = flow.read(); del state['steps']['a3']
        flow.path.write_text(json.dumps(state), encoding='utf-8')
        project = project_summaries(self.root)[0]
        self.assertEqual(project['health'], 'error')
        self.assertIn('a3', project['message'])

    def test_serves_tracked_assets_and_protection_headers(self):
        for path in ('/', '/portal.js', '/portal.css', '/flujo.json'):
            headers, body = self.request(path)
            self.assertIn(b'200', headers)
            self.assertIn(b'Cache-Control: no-store', headers)
            self.assertIn(b'Content-Security-Policy:', headers)
            self.assertTrue(body)

    def test_manual_covers_real_stages_commands_and_evidence(self):
        stages = json.loads((self.root / 'tablero/flujo.json').read_text(encoding='utf-8'))['stages']
        self.assertEqual([s['id'] for s in stages], STEPS)
        for stage in stages:
            self.assertTrue(stage['command'].startswith('!'))
            self.assertTrue(stage['actions'])
            self.assertTrue(stage['evidence'])

    def test_board_does_not_overwrite_portal_with_project_information(self):
        page = self.root / 'tablero/index.html'
        before = page.read_bytes()
        flow = self.project('secreto')
        flow.start('registro'); flow.block('registro', 'texto del cliente')
        self.assertEqual(before, page.read_bytes())
        self.assertNotIn('texto del cliente', page.read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
