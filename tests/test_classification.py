import copy
import json
import unittest
from pathlib import Path

from framework.classification import classify_reuse, validate_reuse_bands
from framework.process_estimation import calculate

ROOT = Path(__file__).resolve().parents[1]
BANDS = json.loads((ROOT / 'configuracion/framework.json').read_text(encoding='utf-8'))['classification']['reuse']['bands']


class ReuseTests(unittest.TestCase):
    def test_exact_approved_boundaries(self):
        for value, expected in [(0, 'R1'), (9.999, 'R1'), (10, 'R2'), (29.999, 'R2'),
                                (30, 'R3'), (50, 'R3'), (50.001, 'R4'), (100, 'R4')]:
            with self.subTest(percentage=value): self.assertEqual(classify_reuse(value, BANDS), expected)

    def test_unknown_is_not_zero(self):
        self.assertIsNone(classify_reuse(None, BANDS))
        for value in (-1, 101, True, float('nan'), float('inf'), '50'):
            with self.subTest(percentage=value):
                with self.assertRaises(ValueError): classify_reuse(value, BANDS)

    def test_boundary_gap_and_overlap_rejected(self):
        for inclusion in (True, False):
            bands = copy.deepcopy(BANDS)
            bands[0]['include_maximum'] = inclusion
            bands[1]['include_minimum'] = inclusion
            with self.assertRaises(ValueError): validate_reuse_bands(bands)

    def test_legacy_label_cannot_select_the_wrong_factor(self):
        component = {'id': 'C-001', 'processes': ['P-001'], 'archetype': 'aplicaciones',
            'complexity': 'media', 'environment': 'T1', 'reuse': 'R1', 'reuse_percentage': 80, 'source': 'Test'}
        params = {'hours_per_process': {'aplicaciones': 10}, 'complexity_factors': {'media': 1},
            'environment_factors': {'T1': 1}, 'reuse_factors': {'R1': 1, 'R4': .5},
            'management_fraction': 0, 'range_bands': {'media': {'optimistic': -.1, 'conservative': .2}}}
        with self.assertRaises(ValueError): calculate([component], params, 'media', BANDS)
        component['reuse'] = 'R4'
        self.assertEqual(calculate([component], params, 'media', BANDS)['base_hours'], 5)
