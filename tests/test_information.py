import copy
import json
import unittest
from pathlib import Path

from framework.information import calculate, validate_evidence, render_report

ROOT = Path(__file__).resolve().parents[1]
MODEL = json.loads((ROOT / 'reglas/modelo-informacion.json').read_text(encoding='utf-8'))


class InformationTests(unittest.TestCase):
    def entries(self):
        return {c['id']: {'score': None, 'evidence': '', 'validated_by': '', 'evidence_items': []} for c in MODEL['criteria']}

    def fact(self, author='cliente', medium='escrito_cliente'):
        return {'source': 'F-001', 'location': 'p. 1', 'quote': 'Dato de prueba', 'author': author, 'medium': medium,
                **({'speaker': 'Representante del cliente'} if medium == 'sesion' else {})}

    def test_catalog_preserves_source_descriptors(self):
        source = json.loads((ROOT / 'referencias/onedrive-2026-11-02/verificacion/rubrica_b1.json').read_text(encoding='utf-8'))
        self.assertEqual(len(MODEL['criteria']), 20)
        self.assertEqual(len(MODEL['dimensions']), 9)
        for old, new in zip(source, MODEL['criteria']):
            self.assertEqual(old['id'], new['id'])
            self.assertEqual(old['P'], new['weight'])
            self.assertEqual({str(i): old[str(i)] for i in range(4)}, new['descriptors'])

    def test_unvalidated_written_information_cannot_reach_high(self):
        scores = {c['id']: 2 for c in MODEL['criteria']}
        result = calculate(MODEL, scores)
        self.assertEqual(result['overall'], .667)
        self.assertEqual(result['level'], 'media')
        self.assertFalse(result['core_cap_applied'])

    def test_missing_complementary_counts_as_zero_until_excluded(self):
        scores = {c['id']: 3 for c in MODEL['criteria']}
        scores['D8.1'] = None
        result = calculate(MODEL, scores)
        self.assertEqual(result['included_weight'], 90)
        self.assertEqual(result['excluded_dimensions'], [])
        excluded = calculate(MODEL, scores, {'D8': {'applies': False, 'reason': 'Motivo de prueba'}})
        self.assertEqual(excluded['overall'], 1)
        self.assertEqual(excluded['included_weight'], 83)
        with self.assertRaises(ValueError): calculate(MODEL, scores, {'D8': {'applies': False}})
        with self.assertRaises(ValueError): calculate(MODEL, scores, {'D1': {'applies': False, 'reason': 'No'}})

    def test_cap_only_changes_high_to_medium_and_prioritizes_core(self):
        scores = {c['id']: 3 for c in MODEL['criteria']}
        for key in scores:
            if key.startswith('D1.'): scores[key] = 0
        result = calculate(MODEL, scores)
        self.assertGreater(result['overall'], .67)
        self.assertEqual(result['level'], 'media')
        self.assertTrue(result['core_cap_applied'])
        self.assertEqual(result['gaps'][0]['dimension'], 'D1')
        low = calculate(MODEL, {c['id']: 0 for c in MODEL['criteria']})
        self.assertEqual(low['level'], 'baja')
        self.assertFalse(low['core_cap_applied'])

    def test_priority_uses_possible_points_and_normalized_weight(self):
        result = calculate(MODEL, {c['id']: 0 for c in MODEL['criteria']})
        d8 = next(c for c in result['gaps'] if c['id'] == 'D8.1')
        d3 = next(c for c in result['gaps'] if c['id'] == 'D3.1')
        self.assertEqual(d8['priority'], 7.78)
        self.assertEqual(d3['priority'], 6.67)

    def test_empty_is_not_completed_and_legacy_ids_rejected(self):
        self.assertEqual(calculate(MODEL, {})['level'], 'Sin evaluar')
        with self.assertRaises(ValueError): calculate(MODEL, {'D1.01': 2})
        for bad in (True, 2.0, 'N/A', -1, 4):
            with self.assertRaises(ValueError): calculate(MODEL, {'D1.1': bad})

    def test_weakest_evidence_wins(self):
        entries = self.entries()
        entries['D1.1'].update(score=2, evidence='Prueba', evidence_items=[self.fact(), self.fact('equipo', 'notas_internas')])
        with self.assertRaises(ValueError): validate_evidence(MODEL, entries)
        entries['D1.1']['score'] = 1
        self.assertEqual(validate_evidence(MODEL, entries)['D1.1'], 1)

    def test_confirmation_needs_direct_quote_not_internal_claim(self):
        entries = self.entries()
        fact = self.fact(); fact['confirmed'] = True
        entries['D1.1'].update(score=3, evidence='Prueba', validated_by='Experto', evidence_items=[fact])
        with self.assertRaises(ValueError): validate_evidence(MODEL, entries)
        fact['confirmation'] = self.fact('equipo', 'notas_internas')
        with self.assertRaises(ValueError): validate_evidence(MODEL, entries)
        fact['confirmation'] = self.fact('cliente', 'sesion')
        self.assertEqual(validate_evidence(MODEL, entries)['D1.1'], 3)

    def test_internal_assets_are_exception_but_still_need_source(self):
        entries = self.entries()
        entries['D6.1'].update(score=3, evidence='Catálogo revisado')
        with self.assertRaises(ValueError): validate_evidence(MODEL, entries)
        entries['D6.1']['evidence_items'] = [self.fact('equipo', 'notas_internas')]
        self.assertEqual(validate_evidence(MODEL, entries)['D6.1'], 3)

    def test_report_includes_all_twenty_questions(self):
        result = calculate(MODEL, {})
        report = render_report('prueba', result, MODEL, 'hash')
        self.assertEqual(report.count('### D'), 20)
        self.assertEqual(len(result['gaps']), 20)
