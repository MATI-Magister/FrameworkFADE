import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from framework.configuration import load_config
from framework.engine import Workflow
from framework.estimation_route import describe
from framework.process_estimation import project_estimate
from framework.unified_estimation import render_coverage

ROOT = Path(__file__).resolve().parents[1]


class UnifiedEstimationTests(unittest.TestCase):
    def setUp(self):
        self.config = load_config(ROOT)
        self.config['estimation'].update(currency='DEM', cost_per_hour=100,
            team=[{'role': 'Dev', 'people': 1, 'hours_per_week': 40, 'allocation': 1, 'source': 'Prueba sintética'}])
        self.data = json.loads((ROOT / 'ejemplos/ruta-unificada/entrada.json').read_text(encoding='utf-8'))

    def test_mixed_methods_reconcile_and_do_not_apply_band_or_management_twice(self):
        result = project_estimate(self.data, self.config, require_complete=True)
        base, conservative = result['scenarios']
        # Process: 40 + 15% management. Activity: (4+4*8+12)/6=8,
        # already includes management. Conservative process 40*1.15*1.15.
        self.assertAlmostEqual(base['hours'], 54)
        self.assertAlmostEqual(conservative['hours'], 64.9)
        self.assertAlmostEqual(base['cost'], 5400)
        self.assertAlmostEqual(base['duration_weeks'], 54 / 40)
        self.assertEqual([r['method'] for r in result['coverage']], ['process_table', 'activities_omp'])
        self.assertEqual(result['pending'], [])
        self.assertIn('Prueba sintética', render_coverage(result))

    def test_missing_classification_uses_documented_activity_not_default_factors(self):
        work = self.data['components'][0]['work_items'][0]
        del work['complexity']
        work['omp'] = {'optimistic': 10, 'likely': 20, 'pessimistic': 30}
        result = project_estimate(self.data, self.config)
        self.assertEqual(result['coverage'][0]['method'], 'activities_omp')
        self.assertAlmostEqual(result['scenarios'][0]['hours'], 20 * 1.15 + 8)
        self.assertNotIn('complexity', result['coverage'][0]['basis'])

    def test_table_cannot_be_replaced_by_an_arbitrary_range(self):
        self.data['components'][0]['work_items'][0]['omp'] = {'optimistic': 1, 'likely': 2, 'pessimistic': 3}
        with self.assertRaises(ValueError): project_estimate(self.data, self.config)

    def test_proposal_model_prefers_external_and_falls_back_to_ia(self):
        item = self.data['components'][0]['work_items'][0]
        item.update(kind='analogy', dimensions={'development': 'Nuevo', 'archetype': 'Aplicaciones',
                    'size': 'XS', 'complexity': 'Baja', 'integration': 'I0'},
                    size_basis='Comparación sintética a la misma escala', external_fit=True)
        result = project_estimate(self.data, self.config)
        self.assertEqual(result['coverage'][0]['basis']['sheet'], 'DatosExt')
        self.assertEqual(result['coverage'][0]['basis']['records'], 9)
        self.assertEqual(result['coverage'][0]['base_hours'], 817.9)
        item['dimensions']['integration'] = 'I3'
        result = project_estimate(self.data, self.config)
        self.assertEqual(result['coverage'][0]['basis']['sheet'], 'IA')
        self.assertEqual(result['coverage'][0]['base_hours'], 38.4)
        item['dimensions']['integration'] = 'I0'
        item.update(external_fit=False, external_exclusion='Se trata de un módulo, no de un proyecto completo')
        result = project_estimate(self.data, self.config)
        self.assertEqual(result['coverage'][0]['basis']['sheet'], 'IA')
        self.assertEqual(result['coverage'][0]['base_hours'], 21.8)
        item['omp'] = {'optimistic': 1, 'likely': 2, 'pessimistic': 3}
        with self.assertRaisesRegex(ValueError, 'misma unidad'):
            project_estimate(self.data, self.config)

    def test_overlap_missing_and_extra_coverage_rejected(self):
        for covers in (['W-001'], ['W-003'], []):
            with self.subTest(covers=covers):
                data = copy.deepcopy(self.data)
                data['components'][0]['work_items'][1]['covers'] = covers
                with self.assertRaises(ValueError): project_estimate(data, self.config)

    def test_unsubstantiated_or_invalid_activity_ranges_rejected(self):
        for change in ({'source': ''}, {'routing_reason': ''}, {'includes_management': None},
                       {'omp': {'optimistic': 9, 'likely': 8, 'pessimistic': 12}},
                       {'omp': {'optimistic': 4, 'likely': True, 'pessimistic': 12}}):
            with self.subTest(change=change):
                data = copy.deepcopy(self.data)
                data['components'][0]['work_items'][1].update(change)
                with self.assertRaises(ValueError): project_estimate(data, self.config)

    def test_inconsistent_reuse_is_not_silently_turned_into_activity(self):
        self.data['components'][0]['work_items'][0]['reuse'] = 'R4'
        with self.assertRaises(ValueError): project_estimate(self.data, self.config)

    def test_deterministic_results_with_same_coverage_and_parameters(self):
        self.assertEqual(project_estimate(self.data, self.config), project_estimate(copy.deepcopy(self.data), copy.deepcopy(self.config)))

    def test_quote_packages_scale_units_but_count_shared_work_once(self):
        process, activity = self.data['components'][0]['work_items']
        package = {'type': 'per_unit', 'quantity': 3, 'unit': 'integración',
                   'assumption': 'Se adapta un conector existente', 'limit': 'Hasta tres integraciones comparables',
                   'requote_when': 'se requiere construir un conector nuevo'}
        process['package'] = package
        activity['package'] = {**package, 'type': 'common', 'quantity': 1, 'unit': 'entorno',
                               'limit': 'Un entorno compartido'}
        result = project_estimate(self.data, self.config, require_complete=True)
        self.assertAlmostEqual(result['scenarios'][0]['hours'], 40 * 3 * 1.15 + 8)
        self.assertAlmostEqual(result['scenarios'][1]['hours'], 40 * 1.15 * 3 * 1.15 + 12)
        self.assertIn(package['requote_when'], render_coverage(result))
        activity['package'].update(type='per_unit', quantity=2)
        self.assertAlmostEqual(project_estimate(self.data, self.config)['scenarios'][0]['hours'], 40 * 3 * 1.15 + 16)
        activity['package']['type'] = 'common'
        with self.assertRaises(ValueError):
            project_estimate(self.data, self.config)

    def test_known_single_hourly_cost_does_not_require_an_invented_calendar(self):
        del self.data['components'][0]['role_split']
        result = project_estimate(self.data, self.config)
        self.assertAlmostEqual(result['scenarios'][0]['cost'], 5400)
        self.assertIsNone(result['scenarios'][0]['duration_weeks'])
        with self.assertRaises(ValueError): project_estimate(self.data, self.config, require_complete=True)


class ProjectParametersTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(dir=ROOT / 'tests', prefix='tmp-route-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        for folder in ('configuracion', 'reglas'):
            shutil.copytree(ROOT / folder, self.root / folder)
        self.one, self.two = Workflow(self.root, 'uno'), Workflow(self.root, 'dos')
        self.one.init(); self.two.init()
        self.local = self.one.base / '01-entradas/respuestas/parametros-estimacion.json'

    def test_existing_parameters_are_local_sourced_and_hashed(self):
        before_one, before_two = self.one.rules()[1], self.two.rules()[1]
        self.local.write_text(json.dumps({'estimation': {'currency': 'COP', 'cost_per_hour': 100000},
            'sources': {'currency': 'Respuesta R-001', 'cost_per_hour': 'Respuesta R-002'}}), encoding='utf-8')
        self.assertEqual(load_config(self.root, 'uno')['estimation']['cost_per_hour'], 100000)
        self.assertIsNone(load_config(self.root, 'dos')['estimation']['cost_per_hour'])
        self.assertNotEqual(before_one, self.one.rules()[1])
        self.assertEqual(before_two, self.two.rules()[1])
        self.assertIn('100000', describe(self.root, 'uno'))
        self.assertIn('parametros-estimacion.json', describe(self.root, 'uno'))

    def test_local_method_bypass_or_missing_source_rejected(self):
        for data in ({'estimation': {'process_method': {'status': 'approved'}}, 'sources': {'process_method': 'Test'}},
                     {'estimation': {'currency': 'COP'}, 'sources': {}}):
            self.local.write_text(json.dumps(data), encoding='utf-8')
            with self.assertRaises(ValueError): load_config(self.root, 'uno')
