"""Checks for the educational example, not validation of a local calibration."""
import json
import math
import unittest
from pathlib import Path

from scripts.ejemplo_a4 import scenario

ROOT = Path(__file__).resolve().parents[1]


class ExampleEstimationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / 'ejemplos/a4/entradas.json').read_text(encoding='utf-8'))
        cls.base = scenario(cls.data, 'Base')
        cls.conservative = scenario(cls.data, 'Conservador')

    def test_component_allocation_reconciles_with_aggregate(self):
        b = self.base
        self.assertAlmostEqual(sum(r['hours'] for r in b['rows']), b['hours'])
        self.assertAlmostEqual(sum(r['hours'] for r in b['rows'][:4]), b['software_hours'])
        self.assertAlmostEqual(b['rows'][0]['hours'] / b['software_hours'], .25)
        # Scale of the aggregate matters: do not sum four independent size^E runs.
        naive = sum(self.data['A'] * c['size_ksloc_base'] ** b['E'] * 152 for c in self.data['software_components'])
        self.assertGreater(b['software_hours'], naive)

    def test_cost_and_role_hours_reconcile(self):
        for result in (self.base, self.conservative):
            for row in result['rows']:
                self.assertAlmostEqual(sum(row['role_hours'].values()), row['hours'])
                expected = sum(h * self.data['roles'][r]['rate_COP_hour'] for r, h in row['role_hours'].items())
                self.assertAlmostEqual(row['cost'], expected)
            self.assertAlmostEqual(sum(r['cost'] for r in result['rows']), result['cost'])

    def test_outside_configuration_only_added_once(self):
        self.assertAlmostEqual(self.base['rows'][-1]['hours'], 38)
        self.assertAlmostEqual(self.conservative['rows'][-1]['hours'], 60)
        self.assertAlmostEqual(self.base['rows'][-1]['cost'], 4560000)
        self.assertAlmostEqual(self.base['hours'] - self.base['software_hours'], 38)

    def test_calendar_respects_dependencies_and_person_capacity(self):
        for result in (self.base, self.conservative):
            tasks = result['tasks']
            ends = {t['id']: t['end'] for t in tasks}
            for i, task in enumerate(tasks):
                for dep in task['dependencies']:
                    self.assertGreaterEqual(task['start'], ends[dep])
                for other in tasks[i+1:]:
                    if other['role'] == task['role']:
                        self.assertLessEqual(min(task['end'], other['end']), max(task['start'], other['start']) + 1e-10)
            self.assertAlmostEqual(result['duration'], max(t['end'] for t in tasks))
            self.assertLess(result['duration'], sum(r['duration'] for r in result['rows']))

    def test_scenario_changes_inputs_instead_of_only_inflating_total(self):
        self.assertEqual([r['id'] for r in self.base['rows']], [r['id'] for r in self.conservative['rows']])
        self.assertGreater(self.conservative['software_hours'], self.base['software_hours'])
        self.assertGreater(self.conservative['cost'], self.base['cost'])
        self.assertGreater(self.conservative['duration'], self.base['duration'])
        self.assertTrue(math.isclose(self.base['size'], 2))


if __name__ == '__main__':
    unittest.main()
