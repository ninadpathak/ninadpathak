import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'static' / 'templates' / 'documentation_placement_audit.py'
spec = importlib.util.spec_from_file_location('documentation_placement_audit', SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def item(**overrides):
    row = {
        'artifact': 'example',
        'external_reader_task': False,
        'sensitive_internal_context': False,
        'internal_operator_task': False,
        'owner': 'docs',
        'update_trigger': 'product change',
    }
    row.update(overrides)
    return row


class DocumentationPlacementAuditTests(unittest.TestCase):
    def test_external_task_without_internal_context_is_external(self):
        result = audit.classify(item(external_reader_task=True))
        self.assertEqual(result['placement'], 'external')

    def test_sensitive_internal_task_stays_internal(self):
        result = audit.classify(item(sensitive_internal_context=True, internal_operator_task=True))
        self.assertEqual(result['placement'], 'internal')

    def test_shared_subject_with_private_context_is_split(self):
        result = audit.classify(item(external_reader_task=True, sensitive_internal_context=True, internal_operator_task=True))
        self.assertEqual(result['placement'], 'split')

    def test_unowned_task_is_flagged_for_review(self):
        result = audit.classify(item())
        self.assertEqual(result['placement'], 'review')

    def test_missing_governance_fields_fail_validation(self):
        broken = item()
        broken.pop('owner')
        with self.assertRaisesRegex(ValueError, 'owner'):
            audit.validate(broken)


if __name__ == '__main__':
    unittest.main()
