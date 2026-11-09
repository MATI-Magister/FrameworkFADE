import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from framework.configuration import load_config
from framework.engine import Workflow
from framework.roles import load_roles
from scripts.install_skills import install

ROOT = Path(__file__).resolve().parents[1]


class ConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT / 'tests', prefix='tmp-config-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for name in ('configuracion', 'reglas'):
            shutil.copytree(ROOT / name, self.root / name)
        self.path = self.root / 'configuracion/framework.json'

    def edit(self, fn):
        data = json.loads(self.path.read_text(encoding='utf-8'))
        fn(data)
        self.path.write_text(json.dumps(data), encoding='utf-8')

    def test_authorized_table_does_not_import_financial_examples(self):
        data = load_config(self.root)
        self.assertIsNone(data['estimation']['cost_per_hour'])
        self.assertIsNone(data['estimation']['target_margin'])
        self.assertEqual(data['estimation']['process_method']['hours_per_process']['aplicaciones'], 40)
        self.assertEqual(data['estimation']['process_method']['status'], 'draft')
        self.assertNotIn('max_client_questions', data['operation'])

    def test_business_change_changes_hash_ui_change_does_not(self):
        flow = Workflow(self.root)
        before = flow.rules()[1]
        self.edit(lambda d: d['operation'].update(portal_port=8766))
        self.assertEqual(before, flow.rules()[1])
        self.edit(lambda d: d['estimation'].update(cost_per_hour=100))
        self.assertNotEqual(before, flow.rules()[1])

    def test_invalid_financial_values_and_policy_bypass_rejected(self):
        for bad in (True, -1, float('inf'), float('nan')):
            with self.subTest(bad=bad):
                self.edit(lambda d: d['estimation'].update(cost_per_hour=bad))
                with self.assertRaises(ValueError): load_config(self.root)
        self.edit(lambda d: d['estimation'].update(cost_per_hour=None, target_margin=1))
        with self.assertRaises(ValueError): load_config(self.root)
        self.edit(lambda d: d['estimation'].update(target_margin=None))
        self.edit(lambda d: d['policies'].update(fast_track_bypasses_approval=True))
        with self.assertRaises(ValueError): load_config(self.root)

    def test_path_escape_rejected(self):
        self.edit(lambda d: d['catalogs'].update(assets='../escape.json'))
        with self.assertRaises(ValueError): load_config(self.root)

    def test_session_limit_is_not_an_operational_parameter(self):
        self.edit(lambda d: d['operation'].update(max_additional_sessions=2))
        with self.assertRaises(ValueError): load_config(self.root)

    def test_draft_configuration_does_not_enable_a4(self):
        flow = Workflow(self.root)
        rules, _, _ = flow.rules()
        self.assertEqual(rules['maturity_model']['kind'], 'information_b1')
        self.assertEqual(len(rules['maturity_model']['criteria']), 20)
        self.assertEqual(rules['currency'], None)
        with self.assertRaises(ValueError): flow.validate_rules()

    def test_role_routes_and_install_protects_edits(self):
        roles = load_roles(ROOT)['roles']
        self.assertEqual(len(roles), 11)
        self.assertEqual({r['id'] for r in roles if r['stage'] == 'a1'}, {'estructurador', 'evaluador'})
        target = self.root / 'installed'
        self.assertEqual(install(ROOT, target), 11)
        self.assertEqual(install(ROOT, target), 11)
        skill = target / 'fade-registrar/SKILL.md'
        skill.write_text('Edición local', encoding='utf-8')
        with self.assertRaises(ValueError): install(ROOT, target)
        self.assertEqual(skill.read_text(encoding='utf-8'), 'Edición local')

    def test_installer_does_not_overwrite_other_skill(self):
        target = self.root / 'installed'
        other = target / 'fade-orquestar'
        other.mkdir(parents=True)
        (other / 'SKILL.md').write_text('Ajena', encoding='utf-8')
        with self.assertRaises(ValueError): install(ROOT, target)
        self.assertEqual(list(target.iterdir()), [other])
