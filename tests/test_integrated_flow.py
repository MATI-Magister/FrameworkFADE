"""Synthetic integration case: install, gated calculation, immutable review, actuals comparison."""
import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from framework.diagnostics import inspect
from framework.engine import Workflow
from framework.learning import compare
from framework.process_estimation import project_estimate, schedule
from scripts.aprendizaje import prepare
from scripts.install import install
from scripts.demo_procesos import run as run_demo

ROOT = Path(__file__).resolve().parents[1]


class IntegratedTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / 'tests', prefix='tmp-integrated-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ('framework', 'scripts', 'configuracion', 'reglas', 'agentes', 'roles', 'skills', 'tablero', 'referencias', 'ejemplos'):
            shutil.copytree(ROOT / name, self.root / name, ignore=shutil.ignore_patterns('__pycache__'))
        for name in ('AGENTS.md', 'README.md'):
            shutil.copy2(ROOT / name, self.root / name)
        self.config_path = self.root / 'configuracion/framework.json'
        self.config = json.loads(self.config_path.read_text(encoding='utf-8'))
        self.config['operation']['default_project'] = 'integracion'
        self.write_config()
        self.flow = install(self.root, self.root / 'installed-skills')
        self.data = {'information_level': 'alta', 'experience_level': 'media', 'source': 'Caso sintético, no comercial',
            'information_confirmed_by': 'Test', 'experience_confirmed_by': 'Test',
            'management_role_split': {'Gestion': 1}, 'direct_costs_source': 'Costo sintético de prueba',
            'direct_costs': [{'id': 'DIR-001', 'amount': 500, 'source': 'Test'}],
            'components': [{'id': 'C-001', 'name': 'Uno', 'processes': ['P-001', 'P-002'], 'archetype': 'aplicaciones',
                'complexity': 'media', 'environment': 'T1', 'reuse': 'R1', 'reuse_percentage': 0, 'source': 'Test',
                'dependencies': [], 'role_split': {'Dev': .8, 'QA': .2}},
                {'id': 'C-002', 'name': 'Dos', 'processes': ['P-003'], 'archetype': 'aplicaciones',
                'complexity': 'media', 'environment': 'T1', 'reuse': 'R1', 'reuse_percentage': 0, 'source': 'Test',
                'dependencies': ['C-001'], 'role_split': {'Dev': .8, 'QA': .2}}]}

    def write_config(self):
        self.config_path.write_text(json.dumps(self.config), encoding='utf-8')

    def parameters(self):
        e = self.config['estimation']
        e.update(currency='COP', costing_mode='por_rol', cfo_parameters={'description': 'Costo técnico, sin precio', 'source': 'Test'})
        e['rates'] = [{'role': r, 'amount': rate, 'unit': 'COP/hora', 'source': 'Test'}
                      for r, rate in [('Dev', 100), ('QA', 80), ('Gestion', 120)]]
        e['team'] = [{'role': r, 'people': 1, 'hours_per_week': hours, 'allocation': 1, 'source': 'Test'}
                     for r, hours in [('Dev', 10), ('QA', 5), ('Gestion', 2)]]
        p = e['process_method']; p.update(status='approved', management_fraction=.1)
        p['hours_per_process'] = {a: 10 for a in ('aplicaciones', 'integracion', 'datos_ia', 'plataforma', 'seguridad', 'modernizacion')}
        p['complexity_factors'] = {a: 1 for a in ('baja', 'media', 'alta', 'muy_alta')}
        p['environment_factors'] = {a: 1 for a in ('T1', 'T2', 'T3', 'T4')}
        p['reuse_factors'] = {a: 1 for a in ('R1', 'R2', 'R3', 'R4')}
        p['range_bands'] = {a: {'optimistic': -.1, 'conservative': .2} for a in ('baja', 'media', 'alta')}
        self.write_config()

    def finish(self, step):
        self.flow.start(step)
        out = self.flow.base / '03-entregables'
        (out / f'{step}.md').write_text('Contenido sintético de prueba', encoding='utf-8')
        if step == 'a1': (out / 'preguntas-a1.md').write_text('Preguntas revisadas en test', encoding='utf-8')
        self.flow.finish(step)

    def begin_a4(self):
        for step in ('registro', 'a1', 'a2', 'a3', 'cierre'):
            self.finish(step)
            if step == 'a1': self.flow.approve('a1', 'Test')
        self.parameters()
        path = self.root / 'reglas/estimacion.json'
        rules = json.loads(path.read_text(encoding='utf-8')); rules['status'] = 'approved'
        path.write_text(json.dumps(rules), encoding='utf-8')
        self.flow.approve_rules('Test')
        self.flow.start('a4')

    def run_calculation(self):
        source = self.flow.base / '02-trabajo/entrada-procesos.json'
        source.write_text(json.dumps(self.data), encoding='utf-8')
        p = subprocess.run([sys.executable, str(self.root / 'scripts/estimar_procesos.py'), '--project', self.flow.project,
            '--input', str(source), '--approved'], cwd=self.root, env={**os.environ, 'PYTHONUTF8': '1'}, capture_output=True)
        self.assertEqual(p.returncode, 0, p.stderr.decode('utf-8', errors='replace'))
        folder = next((self.flow.base / '02-trabajo').glob('calculo-a4-*'))
        return folder

    def test_install_is_idempotent_and_respects_selected_project(self):
        before = self.flow.path.read_bytes()
        catalog = self.root / 'datos-locales/catalogo_activos.json'
        catalog.write_text('{"activos": [{"id": "ACT-REAL"}]}', encoding='utf-8')
        install(self.root, self.root / 'installed-skills')
        self.assertEqual(before, self.flow.path.read_bytes())
        self.assertIn('ACT-REAL', catalog.read_text(encoding='utf-8'))
        self.assertFalse((self.root / 'proyectos/piloto').exists())
        self.assertEqual(len(list((self.root / 'installed-skills').glob('*/SKILL.md'))), 11)

    def test_unified_calculation_uses_approved_snapshot_and_freezes_coverage(self):
        self.begin_a4()
        self.data = json.loads((self.root / 'ejemplos/ruta-unificada/entrada.json').read_text(encoding='utf-8'))
        self.data['management_role_split'] = {'Gestion': 1}
        folder = self.run_calculation()
        result = json.loads((folder / 'resultado.json').read_text(encoding='utf-8'))
        self.assertEqual(result['method'], 'unified_processes_activities')
        self.assertAlmostEqual(result['scenarios'][0]['hours'], 19)
        self.assertAlmostEqual(result['scenarios'][0]['cost'], 1920)
        self.assertAlmostEqual(result['scenarios'][1]['hours'], 25.2)
        self.assertTrue((folder / 'cobertura.md').exists())
        (self.flow.base / '03-entregables/a4.md').write_text('Resultado sintético con cobertura revisada', encoding='utf-8')
        self.flow.finish('a4')
        (folder / 'cobertura.md').write_text('Cambio posterior', encoding='utf-8')
        with self.assertRaises(ValueError): self.flow.check_calculation(self.flow.read())

    def test_demo_is_reproducible_without_mutating_configuration_or_project(self):
        before_config = self.config_path.read_bytes()
        before_state = self.flow.path.read_bytes()
        folder = run_demo(self.root)
        result = json.loads((folder / 'resultado.json').read_text(encoding='utf-8'))
        self.assertEqual(result['status'], 'demostracion_ficticia_no_aprobada')
        self.assertEqual(result['scenarios'][0]['cost'], 3800)
        self.assertEqual(before_config, self.config_path.read_bytes())
        self.assertEqual(before_state, self.flow.path.read_bytes())
        self.assertTrue((folder / 'informe.md').exists())

    def test_doctor_distinguishes_draft_values_from_broken_install(self):
        report = inspect(self.root)
        self.assertTrue(all(c[1] for c in report['checks']))
        self.assertFalse(report['ready'])
        (self.root / 'skills/fade-evaluar-informacion/SKILL.md').unlink()
        self.assertTrue(any(not c[1] for c in inspect(self.root)['checks']))

    def test_cost_schedule_reconcile_and_missing_data_block_complete_mode(self):
        self.parameters()
        result = project_estimate(self.data, self.config, require_complete=True)
        base, conservative = result['scenarios']
        self.assertAlmostEqual(base['hours'], 33)
        self.assertAlmostEqual(base['cost'], 3740)
        self.assertAlmostEqual(conservative['cost'], 4388)
        self.assertAlmostEqual(base['duration_weeks'], 2.4)
        self.assertAlmostEqual(sum(r['cost'] for r in base['rows']) + base['unallocated_direct_cost'], base['cost'])
        self.assertAlmostEqual(base['rows'][1]['start_week'], 1.6)
        self.assertEqual(result['confidence'], 'media')
        for scenario in result['scenarios']:
            tasks = scenario['schedule']['tasks']
            for i, t in enumerate(tasks):
                for other in tasks[i+1:]:
                    if t['role'] == other['role']:
                        self.assertLessEqual(min(t['end_week'], other['end_week']), max(t['start_week'], other['start_week']) + 1e-9)
        self.config['estimation']['team'] = []
        with self.assertRaises(ValueError): project_estimate(self.data, self.config, require_complete=True)

    def test_cycles_bad_splits_and_rate_units_rejected(self):
        self.parameters()
        self.data['components'][0]['dependencies'] = ['C-002']
        with self.assertRaises(ValueError): project_estimate(self.data, self.config, True)
        self.data['components'][0]['dependencies'] = []
        self.data['components'][0]['role_split']['Dev'] = .9
        with self.assertRaises(ValueError): project_estimate(self.data, self.config, True)
        self.data['components'][0]['role_split']['Dev'] = .8
        self.config['estimation']['rates'][0]['unit'] = 'COP/dia'
        with self.assertRaises(ValueError): project_estimate(self.data, self.config, True)

    def test_single_cost_is_separate_explicit_option(self):
        self.parameters()
        self.config['estimation'].update(costing_mode='costo_unico', cost_per_hour=10)
        result = project_estimate(self.data, self.config, True)
        self.assertEqual(result['scenarios'][0]['cost'], 830)

    def test_complete_flow_blocks_mutated_calculation_and_prepares_learning(self):
        self.begin_a4()
        out = self.flow.base / '03-entregables'
        (out / 'a4.md').write_text('Informe real de prueba', encoding='utf-8')
        with self.assertRaises(ValueError): self.flow.finish('a4')
        folder = self.run_calculation()
        self.flow.finish('a4')
        self.flow.start('revision')
        for filename in ('revision.md', 'cliente.md', 'ajustes.md'):
            (out / filename).write_text('Paquete sintético de prueba', encoding='utf-8')
        self.flow.finish('revision')
        self.flow.approve('revision', 'Test')
        before = self.flow.path.read_bytes()
        actuals = self.flow.base / '02-trabajo/horas-reales.json'
        actuals.write_text(json.dumps({'source': 'Caso sintético', 'components': [{'id': 'C-001', 'hours': 30}, {'id': 'C-002', 'hours': 12}]}), encoding='utf-8')
        changes = self.flow.base / '02-trabajo/cambios.json'; changes.write_text('[]', encoding='utf-8')
        learning = prepare(self.flow, folder / 'resultado.json', actuals, changes)
        self.assertTrue((learning / 'informe.md').exists())
        self.assertEqual(before, self.flow.path.read_bytes())
        original = (folder / 'resultado.json').read_bytes()
        (folder / 'resultado.json').write_bytes(original + b' ')
        with self.assertRaises(ValueError): self.flow.check_calculation()
        with self.assertRaises(ValueError): prepare(self.flow, folder / 'resultado.json', actuals, changes)

    def test_changed_classification_catalog_invalidates_rule_hash(self):
        before = self.flow.rules()[1]
        path = self.root / 'reglas/modelo-madurez.json'
        d = json.loads(path.read_text(encoding='utf-8')); d['version'] = 'modificado'
        path.write_text(json.dumps(d), encoding='utf-8')
        self.assertNotEqual(before, self.flow.rules()[1])

    def test_experimental_result_cannot_be_registered_as_approved_calculation(self):
        self.begin_a4()
        folder = self.flow.base / '02-trabajo/ensayo'
        folder.mkdir()
        source = folder / 'entrada.json'; source.write_text('{}', encoding='utf-8')
        report = folder / 'informe.md'; report.write_text('Ensayo', encoding='utf-8')
        result = folder / 'resultado.json'
        digest = self.flow.read()['steps']['a4']['rules_hash']
        result.write_text(json.dumps({'status': 'experimental_no_aprobado', 'rules_hash': digest}), encoding='utf-8')
        with self.assertRaises(ValueError): self.flow.record_calculation([source, report, result], digest)
        self.assertNotIn('calculation', self.flow.read()['steps']['a4'])

    def test_modified_snapshot_prevents_calculation(self):
        self.begin_a4()
        item = self.flow.read()['steps']['a4']
        snapshot = self.root / item['rules_snapshot']
        snapshot.write_bytes(snapshot.read_bytes() + b' ')
        source = self.flow.base / '02-trabajo/entrada.json'
        source.write_text(json.dumps(self.data), encoding='utf-8')
        p = subprocess.run([sys.executable, str(self.root / 'scripts/estimar_procesos.py'), '--project', self.flow.project,
            '--input', str(source), '--approved'], cwd=self.root, env={**os.environ, 'PYTHONUTF8': '1'}, capture_output=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(list((self.flow.base / '02-trabajo').glob('calculo-a4-*')), [])


class LearningTests(unittest.TestCase):
    def test_zero_baseline_and_unknown_actuals_are_not_divided_or_filled(self):
        result = compare({'rows': [{'id': 'C-001', 'hours': 0}, {'id': 'C-002', 'hours': 10}]},
            {'source': 'Test', 'components': [{'id': 'C-001', 'hours': 5}, {'id': 'FUERA', 'hours': 3}]}, [])
        self.assertIsNone(result['components'][0]['deviation'])
        self.assertEqual(result['components'][0]['difference_hours'], 5)
        self.assertIsNone(result['actual_hours'])
        self.assertEqual(result['components_without_actuals'], ['C-002'])
        self.assertEqual(result['unassigned_components'], ['FUERA'])

    def test_unapproved_and_duplicate_scope_changes_rejected(self):
        baseline = {'rows': [{'id': 'C-001', 'hours': 10}]}
        actual = {'source': 'Test', 'components': [{'id': 'C-001', 'hours': 15}]}
        change = {'id': 'CAM-001', 'component': 'C-001', 'hours': 5, 'source': 'Test'}
        with self.assertRaises(ValueError): compare(baseline, actual, [change])
        change['approved_by'] = 'Test'
        self.assertEqual(compare(baseline, actual, [change])['components'][0]['difference_hours'], 0)
        with self.assertRaises(ValueError): compare(baseline, actual, [change, change])
