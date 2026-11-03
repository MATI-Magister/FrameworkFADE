import copy
import unittest

from framework.evidence import component_scope, evidence_ceiling


class EvidenceTests(unittest.TestCase):
    def fact(self, confirmed=False, medium='escrito_cliente'):
        fact = {'source': 'F-001', 'location': 'p. 1', 'quote': 'Dato sintético',
                'author': 'cliente', 'medium': medium}
        if medium == 'sesion': fact['speaker'] = 'Responsable del cliente'
        if confirmed:
            fact['confirmed'] = True
            fact['confirmation'] = {'source': 'F-002', 'location': 'min 01:00', 'quote': 'Confirmo el dato',
                'author': 'cliente', 'medium': 'sesion', 'speaker': 'Responsable del cliente'}
        return fact

    def process(self, pid='P-001', confirmed=False):
        return {'id': pid, 'origin': 'ficha', 'evidence_items': [self.fact(confirmed)]}

    def test_identified_direct_confirmation_reaches_three(self):
        self.assertEqual(evidence_ceiling(self.fact(True)), 3)
        written = self.fact(True)
        written['confirmation']['medium'] = 'escrito_cliente'
        written['confirmation'].pop('speaker')
        self.assertEqual(evidence_ceiling(written), 3)

    def test_unidentified_transcription_or_internal_claim_cannot_confirm(self):
        fact = self.fact(True)
        fact['confirmation'].pop('speaker')
        with self.assertRaises(ValueError): evidence_ceiling(fact)
        fact = self.fact(True)
        fact['confirmation'].update(author='equipo', medium='notas_internas')
        with self.assertRaises(ValueError): evidence_ceiling(fact)
        verbal = self.fact(medium='sesion'); verbal.pop('speaker')
        with self.assertRaises(ValueError): evidence_ceiling(verbal)

    def test_scope_uses_weakest_process_and_is_separate_from_global_levels(self):
        self.assertEqual(component_scope([self.process(confirmed=True)])['label'], 'Validado')
        self.assertEqual(component_scope([self.process()])['label'], 'Definido')
        mixed = [self.process(confirmed=True), self.process('P-002')]
        self.assertEqual(component_scope(mixed)['label'], 'Definido')
        self.assertEqual(component_scope(mixed)['limiting_processes'], ['P-002'])
        mixed[1]['evidence_items'] = [self.fact(medium='sesion')]
        self.assertEqual(component_scope(mixed)['label'], 'Supuesto')

    def test_inferred_contradictory_and_missing_information_remain_assumed(self):
        for update in ({'origin': 'inferido'}, {'open_contradiction': True}, {'evidence_items': []}):
            process = self.process(confirmed=True); process.update(update)
            self.assertEqual(component_scope([process])['label'], 'Supuesto')
        self.assertEqual(component_scope([])['label'], 'Supuesto')

    def test_duplicate_processes_do_not_get_a_label(self):
        with self.assertRaises(ValueError): component_scope([self.process(), self.process()])
