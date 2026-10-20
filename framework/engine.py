"""Portable file-based workflow. No AI provider dependencies."""
import hashlib
import json
import re
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path

STEPS = ['registro', 'a1', 'a2', 'a3', 'cierre', 'a4', 'revision']
LABELS = ['Registro y carga', 'A1 · Madurez', 'A2 · Componentes', 'A3 · Clasificación',
          'Cierre condicional', 'A4 · Estimación', 'Revisión final']
DONE = {'completado', 'omitido'}


def now():
    return datetime.now(timezone.utc).isoformat()


def replace_file(source, destination):
    # Windows readers/antivirus can briefly hold a generated file open.
    for attempt in range(5):
        try:
            source.replace(destination)
            return
        except PermissionError:
            if attempt == 4:
                raise
            time.sleep(0.02 * (attempt + 1))


class Workflow:
    def __init__(self, root, project='piloto'):
        if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,63}', project):
            raise ValueError('ID inválido: usa minúsculas, números, guion o guion bajo.')
        self.root = Path(root)
        self.project = project
        self.base = self.root / 'proyectos' / project
        self.path = self.base / '04-estado' / 'estado.json'

    def init(self):
        if self.path.exists():
            raise ValueError('El proyecto ya existe; se conserva su estado.')
        for folder in ['01-entradas/requerimientos', '01-entradas/contexto',
                       '01-entradas/respuestas', '02-trabajo', '03-entregables', '04-estado']:
            (self.base / folder).mkdir(parents=True, exist_ok=True)
        state = {'project': self.project, 'created_at': now(), 'rules_approval': None,
                 'steps': {s: {'status': 'pendiente', 'attempt': 0} for s in STEPS}, 'events': []}
        self.save(state, 'Proyecto creado')

    def read(self):
        if not self.path.exists():
            raise ValueError('Proyecto sin inicializar. Ejecuta init <id>.')
        return json.loads(self.path.read_text(encoding='utf-8'))

    def save(self, state, event):
        state['updated_at'] = now()
        state['events'].append({'at': now(), 'message': event})
        temp = self.path.with_suffix('.tmp')
        temp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
        replace_file(temp, self.path)
        self.board(state)

    def rules(self):
        data = (self.root / 'reglas' / 'estimacion.json').read_bytes()
        rules = json.loads(data)
        model_file = (rules.get('maturity') or {}).get('model_file')
        if model_file:
            model_path = (self.root / model_file).resolve()
            if not model_path.is_relative_to(self.root.resolve()):
                raise ValueError('La fuente del modelo debe permanecer dentro del framework.')
            rules['maturity_model'] = json.loads(model_path.read_text(encoding='utf-8'))
            data = json.dumps(rules, ensure_ascii=False, sort_keys=True, indent=2).encode('utf-8')
        return rules, hashlib.sha256(data).hexdigest(), data

    def validate_rules(self):
        rules, digest, data = self.rules()
        def nonempty(value):
            return isinstance(value, str) and bool(value.strip())
        for key in ['version', 'effort_unit', 'currency']:
            if not nonempty(rules.get(key)):
                raise ValueError(f'Regla pendiente: {key}')
        if rules.get('status') != 'approved':
            raise ValueError('Las reglas siguen en borrador; requieren revisión humana.')
        for key in ['maturity', 'dimensions', 'method', 'capacity', 'cfo_parameters']:
            value = rules.get(key)
            if not isinstance(value, dict) or not all(nonempty(value.get(k)) for k in ['description', 'source']):
                raise ValueError(f'Regla incompleta: {key} (description, source)')
        rates = rules.get('rates')
        if not isinstance(rates, list) or not rates:
            raise ValueError('Faltan tarifas aprobadas.')
        for rate in rates:
            if (not isinstance(rate, dict) or
                not all(nonempty(rate.get(k)) for k in ['role', 'unit', 'source']) or
                type(rate.get('amount')) not in (int, float) or
                not 0 < rate['amount'] < float('inf')):
                raise ValueError('Tarifa inválida: role, amount positivo, unit, source.')
        scenarios = rules.get('scenarios')
        if not isinstance(scenarios, list) or len(scenarios) != 2:
            raise ValueError('Se requieren exactamente dos escenarios.')
        for scenario in scenarios:
            if not isinstance(scenario, dict) or not all(nonempty(scenario.get(k)) for k in ['name', 'description', 'source']):
                raise ValueError('Escenario incompleto.')
        if scenarios[0]['name'].strip() == scenarios[1]['name'].strip():
            raise ValueError('Los dos escenarios deben tener nombres diferentes.')
        return rules, digest, data

    def approve_rules(self, by):
        rules, digest, _ = self.validate_rules()
        state = self.read()
        if state['steps']['a4']['status'] != 'pendiente':
            raise ValueError('Reintenta A4 antes de cambiar sus reglas aprobadas.')
        state['rules_approval'] = {'hash': digest, 'version': rules['version'], 'by': by, 'at': now()}
        self.save(state, f'Reglas {rules["version"]} aprobadas por {by}')

    def check_step(self, step):
        if step not in STEPS:
            raise ValueError(f'Etapa desconocida: {step}')

    def start(self, step=None):
        state = self.read()
        step = step or next((s for s in STEPS if state['steps'][s]['status'] not in DONE), None)
        if step is None:
            raise ValueError('Todas las etapas están completadas.')
        self.check_step(step)
        for previous in STEPS[:STEPS.index(step)]:
            if state['steps'][previous]['status'] not in DONE:
                raise ValueError(f'Primero completa {previous}: {state["steps"][previous]["status"]}')
        item = state['steps'][step]
        if item['status'] == 'en_ejecucion':
            return f'Retomar {step}: lee agentes/{step}.md y produce el entregable.'
        if item['status'] != 'pendiente':
            raise ValueError(f'{step}: {item["status"]}. Requiere aprobación o reintento explícito.')
        if step == 'a4':
            rules, digest, data = self.validate_rules()
            if not state['rules_approval'] or state['rules_approval']['hash'] != digest:
                raise ValueError('Las reglas actuales necesitan aprobación explícita para este proyecto.')
            snapshot = self.base / '04-estado' / f'reglas-a4-{item["attempt"] + 1}.json'
            if snapshot.exists():
                raise ValueError('Ya existe el snapshot de este intento; no se sobrescribe.')
            snapshot.write_bytes(data)
            item['rules_snapshot'] = str(snapshot.relative_to(self.root))
            item['rules_hash'] = digest
        item.update(status='en_ejecucion', attempt=item['attempt'] + 1, started_at=now())
        self.save(state, f'Inicio {step}, intento {item["attempt"]}')
        return f'Ejecutar agentes/{step}.md. Guardar 03-entregables/{step}.md y finalizar con finish {step}.'

    def finish(self, step, context_complete=False, evidence=None):
        self.check_step(step)
        state = self.read()
        item = state['steps'][step]
        if item['status'] != 'en_ejecucion':
            raise ValueError('Solo se puede finalizar una etapa en ejecución.')
        output = self.base / '03-entregables' / f'{step}.md'
        if not output.exists() or not output.read_text(encoding='utf-8').strip():
            raise ValueError('Falta el entregable no vacío de la etapa.')
        if context_complete and (step != 'a3' or not evidence or not evidence.strip()):
            raise ValueError('Omitir cierre requiere A3 y evidencia concreta.')
        if step == 'a1':
            questions = self.base / '03-entregables' / 'preguntas-a1.md'
            if not questions.exists() or not questions.read_text(encoding='utf-8').strip():
                raise ValueError('A1 requiere preguntas-a1.md para revisión del experto antes de autorizar componentes.')
            item['questions_hash'] = hashlib.sha256(questions.read_bytes()).hexdigest()
            item['questions_output'] = str(questions.relative_to(self.root))
        if step == 'revision':
            reviewed = {}
            for filename in ('cliente.md', 'ajustes.md', 'a4.md'):
                artifact = self.base / '03-entregables' / filename
                if not artifact.exists() or not artifact.read_text(encoding='utf-8').strip():
                    raise ValueError(f'Revisión final requiere {filename} no vacío.')
                reviewed[filename] = hashlib.sha256(artifact.read_bytes()).hexdigest()
            item['reviewed_files'] = reviewed
        item.update(status='esperando_aprobacion' if step in ['a1', 'revision'] else 'completado',
                    finished_at=now(), output=str(output.relative_to(self.root)),
                    output_hash=hashlib.sha256(output.read_bytes()).hexdigest())
        if context_complete:
            state['steps']['cierre'].update(status='omitido', reason=evidence, finished_at=now())
        self.save(state, f'Finalización {step}: {item["status"]}')

    def approve(self, step, by):
        self.check_step(step)
        state = self.read()
        item = state['steps'][step]
        if step not in ['a1', 'revision'] or item['status'] != 'esperando_aprobacion':
            raise ValueError('Esta etapa no tiene aprobación pendiente.')
        output = self.base / '03-entregables' / f'{step}.md'
        if not output.exists() or hashlib.sha256(output.read_bytes()).hexdigest() != item['output_hash']:
            raise ValueError('El entregable cambió; reintenta la etapa antes de aprobar.')
        if step == 'a1':
            questions = self.base / '03-entregables' / 'preguntas-a1.md'
            if not questions.exists() or hashlib.sha256(questions.read_bytes()).hexdigest() != item.get('questions_hash'):
                raise ValueError('Las preguntas de A1 faltan o cambiaron; reintenta A1 antes de aprobar.')
        if step == 'revision':
            reviewed = item.get('reviewed_files', {})
            if set(reviewed) != {'cliente.md', 'ajustes.md', 'a4.md'}:
                raise ValueError('Falta el paquete de documentos revisados. Reabre la revisión.')
            for filename, digest in reviewed.items():
                artifact = self.base / '03-entregables' / filename
                if not artifact.exists() or hashlib.sha256(artifact.read_bytes()).hexdigest() != digest:
                    raise ValueError(f'{filename} cambió desde la revisión; recalcula/reabre antes de aprobar.')
            if self.rules()[1] != state['steps']['a4'].get('rules_hash'):
                raise ValueError('Las reglas cambiaron desde A4; reestima y revisa antes de aprobar.')
        item.update(status='completado', approved_by=by, approved_at=now())
        self.save(state, f'{step} aprobado por {by}')

    def block(self, step, reason):
        self.check_step(step)
        state = self.read()
        if state['steps'][step]['status'] != 'en_ejecucion':
            raise ValueError('Solo se puede bloquear una etapa en ejecución.')
        state['steps'][step].update(status='bloqueado', reason=reason)
        self.save(state, f'Bloqueo {step}: {reason}')

    def retry(self, step):
        self.check_step(step)
        state = self.read()
        if state['steps'][step]['status'] == 'pendiente':
            raise ValueError('La etapa está pendiente; usa start.')
        folder = self.base / '04-estado' / 'historial' / now().replace(':', '-')
        folder.mkdir(parents=True)
        (folder / 'estado.json').write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
        for name in STEPS[STEPS.index(step):]:
            output = self.base / '03-entregables' / f'{name}.md'
            if output.exists():
                shutil.move(str(output), str(folder / output.name))
            state['steps'][name] = {'status': 'pendiente', 'attempt': state['steps'][name]['attempt']}
        if STEPS.index(step) <= STEPS.index('a1'):
            questions = self.base / '03-entregables' / 'preguntas-a1.md'
            if questions.exists():
                shutil.move(str(questions), str(folder / questions.name))
        for filename in ('cliente.md', 'ajustes.md'):
            artifact = self.base / '03-entregables' / filename
            if artifact.exists():
                shutil.move(str(artifact), str(folder / artifact.name))
        self.save(state, f'Reintento {step}: salidas archivadas; etapas posteriores invalidadas')

    def complement_a1(self, reason):
        if not reason or not reason.strip():
            raise ValueError('Indica la información o respuestas que deben incorporarse.')
        state = self.read()
        if state['steps']['a1']['status'] not in ('en_ejecucion', 'bloqueado', 'esperando_aprobacion'):
            raise ValueError('Complementar aplica a A1 iniciado y aún no aprobado. Para un A1 aprobado solicita un reintento explícito.')
        self.retry('a1')
        message = self.start('a1')
        state = self.read()
        self.save(state, f'Nueva información para reevaluar A1, sin aprobación: {reason.strip()}')
        return message

    def adjust_review(self, reason):
        if not reason or not reason.strip():
            raise ValueError('Indica el ajuste solicitado y su motivo o fuente.')
        state = self.read()
        if state['steps']['revision']['status'] not in ('en_ejecucion', 'bloqueado', 'esperando_aprobacion'):
            raise ValueError('Ajustar aplica a una revisión iniciada y aún no aprobada. Para versiones aprobadas solicita reapertura explícita.')
        self.retry('revision')
        message = self.start('revision')
        state = self.read()
        self.save(state, f'Ajuste solicitado para revisión, sin aprobación: {reason.strip()}')
        return message

    def board(self, state=None):
        # The tracked portal reads all projects live; never overwrite its source
        # with a generated page containing client state.
        return self.root / 'tablero' / 'index.html'
