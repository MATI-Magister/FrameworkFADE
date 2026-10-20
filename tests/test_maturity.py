import hashlib
import json
import unittest
from pathlib import Path

from framework.maturity import calculate, render_report, validate_evidence
from scripts.import_maturity_model import build_model

ROOT = Path(__file__).resolve().parents[1]


class MaturityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = json.loads((ROOT / 'reglas/modelo-madurez.json').read_text(encoding='utf-8'))

    def test_import_matches_original_and_preserves_rubrics(self):
        source = ROOT / 'reglas/fuentes/Modelo_Madurez_Estimacion.xlsx'
        self.assertEqual(build_model(source), self.model)
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), self.model['source']['sha256'])
        self.assertEqual(len(self.model['criteria']), 109)
        self.assertEqual(len(self.model['dimensions']), 11)
        self.assertAlmostEqual(sum(d['weight'] for d in self.model['dimensions'] if d['core']), .7)

    def test_matches_workbook_cached_example(self):
        example = self.model['example']
        result = calculate(self.model, example['scores'])
        for dimension in result['dimensions']:
            self.assertAlmostEqual(dimension['maturity'], example['dimension_maturity'][dimension['id']], places=12)
        self.assertAlmostEqual(result['overall'], example['overall'], places=12)
        self.assertEqual(result['level'], example['level'])
        report = render_report('ejemplo', result, self.model, 'hash')
        self.assertIn('Preparar el paso de N3 a N4', report)
        self.assertIn('autorizar explícitamente', report)

    def test_empty_is_not_a_finished_assessment(self):
        result = calculate(self.model, {})
        self.assertEqual(result['level'], 'Sin evaluar')
        self.assertEqual(len(result['excluded_dimensions']), 6)
        self.assertAlmostEqual(result['included_weight'], .7)
        self.assertTrue(all(d['included'] for d in result['dimensions'][:5]))

    def test_core_cap_preserves_high_percentage(self):
        scores = {c['id']: 3 for c in self.model['criteria']}
        for c in self.model['criteria']:
            if c['dimension'] == 'D1': scores[c['id']] = 0
        result = calculate(self.model, scores)
        self.assertAlmostEqual(result['overall'], .88)
        self.assertEqual(result['level'], 'N3 - Intermedio')
        self.assertTrue(result['core_cap_applied'])

    def test_partial_complementary_includes_unanswered_maximum(self):
        result = calculate(self.model, {'D6.01': 3})
        dimension = next(d for d in result['dimensions'] if d['id'] == 'D6')
        self.assertTrue(dimension['included'])
        self.assertGreater(dimension['maturity'], 0)
        self.assertLess(dimension['maturity'], 1)
        self.assertGreater(dimension['missing'], 0)

    def test_na_is_only_allowed_where_declared(self):
        with self.assertRaises(ValueError): calculate(self.model, {'D1.01': 'N/A'})
        result = calculate(self.model, {'D1.03': 'N/A'})
        self.assertEqual(result['dimensions'][0]['na'], 1)
        self.assertNotIn('D1.03', [g['id'] for g in result['gaps']])

    def test_explicit_ratings_need_evidence_and_validation(self):
        with self.assertRaises(ValueError):
            validate_evidence(self.model, {'D11.01': {'score': None, 'gap_type': 'condicion_conocida'}})
        with self.assertRaises(ValueError): validate_evidence(self.model, {'D1.01': {'score': 1}})
        with self.assertRaises(ValueError): validate_evidence(self.model, {'D1.01': {'score': 3, 'evidence': 'documento'}})
        valid = {'D1.01': {'score': 3, 'evidence': 'documento sección 2', 'validated_by': 'responsable'}}
        self.assertEqual(validate_evidence(self.model, valid), {'D1.01': 3})

    def test_known_condition_is_not_reasked(self):
        scores = {c['id']: 3 for c in self.model['criteria']}
        scores['D11.01'] = 0
        result = calculate(self.model, scores, {'D11.01': 'condicion_conocida'})
        report = render_report('prueba', result, self.model, 'hash')
        question_section = report.split('## Primeras diez preguntas por prioridad')[1].split('## Registro completo')[0]
        self.assertNotIn('D11.01', question_section)
        self.assertIn('condicion conocida', report)

    def test_bad_scores_and_unknown_ids_rejected(self):
        for scores in [{'inventado': 2}, {'D1.01': True}, {'D1.01': 4}, {'D1.01': 1.5}]:
            with self.assertRaises(ValueError): calculate(self.model, scores)

    def test_level_boundaries(self):
        for score, expected in [(0, 'N1'), (1, 'N2'), (2, 'N4'), (3, 'N5')]:
            result = calculate(self.model, {c['id']: score for c in self.model['criteria']})
            self.assertTrue(result['level'].startswith(expected))


if __name__ == '__main__':
    unittest.main()
