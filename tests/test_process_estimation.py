import copy
import unittest

from framework.process_estimation import calculate


class ProcessTests(unittest.TestCase):
    def setUp(self):
        # Synthetic test inputs, deliberately distinct from the ZIP's example values.
        self.parameters = {'hours_per_process': {'aplicaciones': 10},
            'complexity_factors': {'media': 1}, 'environment_factors': {'T1': 1},
            'reuse_factors': {'R1': 1}, 'management_fraction': .1,
            'range_bands': {'media': {'optimistic': -.1, 'conservative': .2}}}
        self.components = [{'id': 'C-001', 'processes': ['P-001', 'P-002'],
            'archetype': 'aplicaciones', 'complexity': 'media', 'environment': 'T1',
            'reuse': 'R1', 'source': 'Caso sintético de prueba'}]

    def test_management_and_band_applied_once(self):
        result = calculate(self.components, self.parameters, 'media')
        self.assertEqual(result['subtotal_hours'], 20)
        self.assertEqual(result['management_hours'], 2)
        self.assertAlmostEqual(result['conservative_hours'], 26.4)
        self.assertIsNone(result['cost'])
        self.assertIsNone(result['duration'])

    def test_duplicate_process_across_components_rejected(self):
        other = {**self.components[0], 'id': 'C-002'}
        with self.assertRaises(ValueError): calculate(self.components + [other], self.parameters, 'media')

    def test_unknown_classes_and_missing_parameters_do_not_get_defaults(self):
        self.components[0]['complexity'] = 'desconocida'
        with self.assertRaises(ValueError): calculate(self.components, self.parameters, 'media')
        self.parameters['hours_per_process'] = None
        with self.assertRaises(ValueError): calculate(self.components, self.parameters, 'media')

    def test_invalid_processes_and_nonfinite_factors_rejected(self):
        for bad in (2.9, [], ['P-001', 'P-001']):
            self.components[0]['processes'] = bad
            with self.assertRaises(ValueError): calculate(self.components, self.parameters, 'media')
        self.components[0]['processes'] = ['P-001']
        self.parameters['complexity_factors']['media'] = float('nan')
        with self.assertRaises(ValueError): calculate(self.components, self.parameters, 'media')
