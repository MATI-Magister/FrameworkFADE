"""Read-only local portal: project state is read on every request, never written."""
import json
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import unquote, urlsplit

STEP_IDS = ('registro', 'a1', 'a2', 'a3', 'cierre', 'a4', 'revision')
STATUSES = {'pendiente', 'en_ejecucion', 'bloqueado', 'esperando_aprobacion', 'completado', 'omitido'}
ASSETS = {'index.html', 'portal.css', 'portal.js', 'flujo.json'}


def project_summaries(root):
    directory = Path(root) / 'proyectos'
    result = []
    if not directory.exists():
        return result
    for folder in sorted(directory.iterdir(), key=lambda p: p.name.casefold()):
        if not folder.is_dir() or folder.is_symlink() or not folder.resolve().is_relative_to(directory.resolve()):
            continue
        item = {'id': folder.name, 'folder': f'proyectos/{folder.name}', 'health': 'sin_inicializar',
                'steps': {}, 'completed': 0, 'progress': 0, 'next_step': None, 'events': [],
                'message': 'Sin estado. Crea el expediente con !nuevo <id> o incorpora su estado existente.'}
        state_file = folder / '04-estado/estado.json'
        try:
            if not state_file.resolve().is_relative_to(folder.resolve()):
                raise ValueError('El estado apunta fuera del expediente.')
            if state_file.exists():
                state = json.loads(state_file.read_text(encoding='utf-8'))
                if not isinstance(state, dict) or not isinstance(state.get('steps'), dict):
                    raise ValueError('El estado no tiene la estructura esperada.')
                for step in STEP_IDS:
                    entry = state['steps'].get(step)
                    if not isinstance(entry, dict) or entry.get('status') not in STATUSES:
                        raise ValueError(f'Estado incompleto o inválido en {step}.')
                    item['steps'][step] = {key: entry[key] for key in
                        ('status', 'attempt', 'reason', 'started_at', 'finished_at', 'approved_by', 'approved_at', 'output') if key in entry}
                item['health'] = 'ok'
                item['message'] = ''
                item['completed'] = sum(s['status'] in ('completado', 'omitido') for s in item['steps'].values())
                item['progress'] = round(item['completed'] / len(STEP_IDS) * 100)
                item['next_step'] = next((s for s in STEP_IDS if item['steps'][s]['status'] not in ('completado', 'omitido')), None)
                item['updated_at'] = state.get('updated_at')
                item['rules_approved'] = bool(state.get('rules_approval'))
                events = state.get('events', [])
                item['events'] = [{'at': e.get('at', ''), 'message': e.get('message', '')}
                                  for e in events[-10:] if isinstance(e, dict)] if isinstance(events, list) else []
        except (OSError, ValueError, TypeError) as error:
            item.update(health='error', message=f'No se pudo leer el flujo: {error}', steps={}, completed=0, progress=0, next_step=None)
        result.append(item)
    return result


def make_handler(root):
    root = Path(root).resolve()
    static = root / 'tablero'

    class PortalHandler(BaseHTTPRequestHandler):
        def respond(self, code, body, content_type='application/json; charset=utf-8'):
            self.send_response(code)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; object-src 'none'; frame-ancestors 'none'")
            self.end_headers()
            if self.command != 'HEAD':
                self.wfile.write(body)

        def do_GET(self):
            path = unquote(urlsplit(self.path).path)
            if path == '/api/projects':
                body = json.dumps({'projects': project_summaries(root)}, ensure_ascii=False).encode('utf-8')
                return self.respond(200, body)
            filename = 'index.html' if path == '/' else path.lstrip('/')
            if filename not in ASSETS:
                return self.respond(404, b'{"error":"Recurso no disponible"}')
            target = static / filename
            if not target.resolve().is_relative_to(static.resolve()) or not target.is_file():
                return self.respond(404, b'{"error":"Archivo no disponible"}')
            content_type = {'portal.js': 'text/javascript', 'portal.css': 'text/css',
                            'flujo.json': 'application/json', 'index.html': 'text/html'}[filename]
            return self.respond(200, target.read_bytes(), content_type + '; charset=utf-8')

        def do_HEAD(self):
            self.do_GET()

    return PortalHandler
