import json
import shutil
import tempfile
import unittest
from pathlib import Path

from framework.engine import Workflow

ROOT = Path(__file__).resolve().parents[1]


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / 'tests')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ['tablero', 'reglas']:
            shutil.copytree(ROOT / name, self.root / name)
        self.flow = Workflow(self.root, 'test')
        self.flow.init()

    def finish(self, step, **options):
        self.flow.start(step)
        (self.flow.base / '03-entregables' / f'{step}.md').write_text('Contenido revisado', encoding='utf-8')
        if step == 'a1':
            (self.flow.base / '03-entregables/preguntas-a1.md').write_text('Preguntas para alcanzar N4 y brechas núcleo.', encoding='utf-8')
        if step == 'revision':
            for filename in ('cliente.md', 'ajustes.md'):
                (self.flow.base / '03-entregables' / filename).write_text('Paquete revisado', encoding='utf-8')
        self.flow.finish(step, **options)

    def through_a3(self, skip=False):
        self.finish('registro')
        self.finish('a1')
        self.flow.approve('a1', 'test human')
        self.finish('a2')
        self.finish('a3', context_complete=skip, evidence='A1: equipo y entorno definidos' if skip else None)

    def configure_rules(self):
        section = {'description': 'Criterio de prueba', 'source': 'Decisión de prueba'}
        rules = {'version': '1.0', 'status': 'approved', 'effort_unit': 'hora', 'currency': 'COP',
                 **{k: section for k in ['maturity', 'dimensions', 'method', 'capacity', 'cfo_parameters']},
                 'rates': [{'role': 'Dev', 'amount': 100, 'unit': 'COP/hora', 'source': 'Prueba'}],
                 'scenarios': [{'name': n, **section} for n in ['Base', 'Alterno']]}
        (self.root / 'reglas/estimacion.json').write_text(json.dumps(rules), encoding='utf-8')

    def test_order_and_human_gate(self):
        with self.assertRaises(ValueError): self.flow.start('a2')
        self.finish('registro')
        self.finish('a1')
        with self.assertRaises(ValueError): self.flow.start('a2')
        self.flow.approve('a1', 'human')
        self.flow.start('a2')

    def test_no_finish_without_deliverable(self):
        self.flow.start('registro')
        with self.assertRaises(ValueError): self.flow.finish('registro')

    def test_rules_gate_and_snapshot(self):
        self.through_a3(skip=True)
        with self.assertRaises(ValueError): self.flow.start('a4')
        self.configure_rules()
        with self.assertRaises(ValueError): self.flow.start('a4')
        self.flow.approve_rules('human')
        self.flow.start('a4')
        snapshot = self.flow.base / '04-estado/reglas-a4-1.json'
        self.assertTrue(snapshot.exists())
        original = snapshot.read_bytes()
        (self.root / 'reglas/estimacion.json').write_text('{}', encoding='utf-8')
        self.assertEqual(original, snapshot.read_bytes())

    def test_changed_rules_need_new_approval(self):
        self.through_a3(skip=True)
        self.configure_rules()
        self.flow.approve_rules('human')
        path = self.root / 'reglas/estimacion.json'
        rules = json.loads(path.read_text()); rules['version'] = '2.0'
        path.write_text(json.dumps(rules), encoding='utf-8')
        with self.assertRaises(ValueError): self.flow.start('a4')

    def test_closure_required_without_evidence(self):
        self.through_a3()
        with self.assertRaises(ValueError): self.flow.start('a4')
        self.assertEqual(self.flow.read()['steps']['cierre']['status'], 'pendiente')

    def test_retry_invalidates_and_preserves_history(self):
        self.through_a3(skip=True)
        self.flow.retry('a2')
        self.assertEqual(self.flow.read()['steps']['a3']['status'], 'pendiente')
        self.assertEqual(self.flow.read()['steps']['cierre']['status'], 'pendiente')
        self.assertFalse((self.flow.base / '03-entregables/a2.md').exists())
        self.assertTrue(list((self.flow.base / '04-estado/historial').glob('*/a2.md')))

    def test_changed_deliverable_cannot_be_approved(self):
        self.finish('registro'); self.finish('a1')
        (self.flow.base / '03-entregables/a1.md').write_text('Cambió', encoding='utf-8')
        with self.assertRaises(ValueError): self.flow.approve('a1', 'human')

    def test_full_flow_with_final_approval(self):
        self.through_a3()
        self.finish('cierre'); self.configure_rules(); self.flow.approve_rules('human')
        self.finish('a4'); self.finish('revision')
        self.assertEqual(self.flow.read()['steps']['revision']['status'], 'esperando_aprobacion')
        self.flow.approve('revision', 'human')
        self.assertEqual(self.flow.read()['steps']['revision']['status'], 'completado')

    def test_block_and_retry(self):
        self.flow.start('registro'); self.flow.block('registro', '<script>Cliente</script>')
        page = (self.root / 'tablero/index.html').read_text(encoding='utf-8')
        self.assertNotIn('<script>Cliente</script>', page)
        with self.assertRaises(ValueError): self.flow.start('registro')
        self.flow.retry('registro'); self.flow.start('registro')
        self.assertEqual(self.flow.read()['steps']['registro']['attempt'], 2)

    def test_project_path_validation(self):
        with self.assertRaises(ValueError): Workflow(self.root, '../escape')

    def ready_review(self):
        self.through_a3(); self.finish('cierre'); self.configure_rules()
        self.flow.approve_rules('human'); self.finish('a4')

    def test_review_requires_customer_deliverable_and_adjustments(self):
        self.ready_review(); self.flow.start('revision')
        (self.flow.base / '03-entregables/revision.md').write_text('Revisión', encoding='utf-8')
        with self.assertRaises(ValueError): self.flow.finish('revision')
        self.assertEqual(self.flow.read()['steps']['revision']['status'], 'en_ejecucion')

    def test_changed_customer_package_cannot_be_approved(self):
        self.ready_review(); self.finish('revision')
        (self.flow.base / '03-entregables/cliente.md').write_text('Nuevo valor', encoding='utf-8')
        with self.assertRaises(ValueError): self.flow.approve('revision', 'experto')

    def test_changed_a4_cannot_be_approved_in_review(self):
        self.ready_review(); self.finish('revision')
        (self.flow.base / '03-entregables/a4.md').write_text('Cálculo cambiado', encoding='utf-8')
        with self.assertRaises(ValueError): self.flow.approve('revision', 'experto')

    def test_changed_rules_cannot_be_approved_in_review(self):
        self.ready_review(); self.finish('revision')
        path = self.root / 'reglas/estimacion.json'
        rules = json.loads(path.read_text()); rules['version'] = '2.0'
        path.write_text(json.dumps(rules), encoding='utf-8')
        with self.assertRaises(ValueError): self.flow.approve('revision', 'experto')

    def test_adjust_reopens_and_archives_review_package(self):
        self.ready_review(); self.finish('revision')
        original_a4 = (self.flow.base / '03-entregables/a4.md').read_bytes()
        self.flow.adjust_review('AJU-001: corregir explicación del alcance')
        state = self.flow.read()
        self.assertEqual(state['steps']['revision']['status'], 'en_ejecucion')
        self.assertNotIn('approved_by', state['steps']['revision'])
        self.assertEqual(original_a4, (self.flow.base / '03-entregables/a4.md').read_bytes())
        for filename in ('cliente.md', 'ajustes.md', 'revision.md'):
            self.assertTrue(list((self.flow.base / '04-estado/historial').glob('*/' + filename)))
        with self.assertRaises(ValueError): self.flow.approve('revision', 'experto')

    def test_adjust_rejects_unstarted_and_approved_review(self):
        with self.assertRaises(ValueError): self.flow.adjust_review('Cambiar texto')
        self.ready_review(); self.finish('revision'); self.flow.approve('revision', 'experto')
        with self.assertRaises(ValueError): self.flow.adjust_review('Cambiar texto')

    def test_complement_reopens_pending_a1_without_approval(self):
        self.finish('registro'); self.finish('a1')
        self.flow.complement_a1('Documento adicional y respuestas del experto')
        state = self.flow.read()
        self.assertEqual(state['steps']['a1']['status'], 'en_ejecucion')
        self.assertEqual(state['steps']['a1']['attempt'], 2)
        self.assertNotIn('approved_by', state['steps']['a1'])
        self.assertTrue(list((self.flow.base / '04-estado/historial').glob('*/a1.md')))
        self.assertTrue(list((self.flow.base / '04-estado/historial').glob('*/preguntas-a1.md')))
        with self.assertRaises(ValueError): self.flow.approve('a1', 'experto')
        with self.assertRaises(ValueError): self.flow.start('a2')

    def test_complement_can_resume_blocked_a1(self):
        self.finish('registro'); self.flow.start('a1'); self.flow.block('a1', 'Faltan respuestas')
        self.flow.complement_a1('Respuestas entregadas')
        self.assertEqual(self.flow.read()['steps']['a1']['status'], 'en_ejecucion')

    def test_complement_cannot_reopen_approved_or_unstarted_a1(self):
        with self.assertRaises(ValueError): self.flow.complement_a1('Nuevo archivo')
        self.finish('registro'); self.finish('a1'); self.flow.approve('a1', 'experto')
        with self.assertRaises(ValueError): self.flow.complement_a1('Nuevo archivo')
        self.assertEqual(self.flow.read()['steps']['a1']['status'], 'completado')

    def test_complement_requires_input_reference(self):
        self.finish('registro'); self.flow.start('a1')
        with self.assertRaises(ValueError): self.flow.complement_a1(' ')
        self.assertEqual(self.flow.read()['steps']['a1']['attempt'], 1)

    def test_a1_requires_questions_before_expert_approval(self):
        self.finish('registro'); self.flow.start('a1')
        (self.flow.base / '03-entregables/a1.md').write_text('Resumen N3', encoding='utf-8')
        with self.assertRaises(ValueError): self.flow.finish('a1')
        self.assertEqual(self.flow.read()['steps']['a1']['status'], 'en_ejecucion')
        with self.assertRaises(ValueError): self.flow.start('a2')

    def test_a1_changed_questions_cannot_be_approved(self):
        self.finish('registro'); self.finish('a1')
        (self.flow.base / '03-entregables/preguntas-a1.md').write_text('Preguntas modificadas', encoding='utf-8')
        with self.assertRaises(ValueError): self.flow.approve('a1', 'experto')

    def test_retry_a1_preserves_question_history(self):
        self.finish('registro'); self.finish('a1'); self.flow.retry('a1')
        self.assertFalse((self.flow.base / '03-entregables/preguntas-a1.md').exists())
        self.assertTrue(list((self.flow.base / '04-estado/historial').glob('*/preguntas-a1.md')))

    def test_maturity_catalog_changes_invalidate_rule_approval(self):
        self.through_a3(skip=True)
        self.configure_rules()
        path = self.root / 'reglas/estimacion.json'
        rules = json.loads(path.read_text())
        rules['maturity']['model_file'] = 'reglas/modelo-madurez.json'
        path.write_text(json.dumps(rules), encoding='utf-8')
        self.flow.approve_rules('human')
        catalog_path = self.root / 'reglas/modelo-madurez.json'
        catalog = json.loads(catalog_path.read_text(encoding='utf-8'))
        catalog['version'] = 'new-version'
        catalog_path.write_text(json.dumps(catalog), encoding='utf-8')
        with self.assertRaises(ValueError): self.flow.start('a4')

    def test_snapshot_embeds_full_maturity_catalog(self):
        self.through_a3(skip=True)
        self.configure_rules()
        path = self.root / 'reglas/estimacion.json'
        rules = json.loads(path.read_text())
        rules['maturity']['model_file'] = 'reglas/modelo-madurez.json'
        path.write_text(json.dumps(rules), encoding='utf-8')
        self.flow.approve_rules('human'); self.flow.start('a4')
        snapshot = json.loads((self.flow.base / '04-estado/reglas-a4-1.json').read_text(encoding='utf-8'))
        self.assertEqual(len(snapshot['maturity_model']['criteria']), 109)


if __name__ == '__main__':
    unittest.main()
