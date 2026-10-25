"""Workflow wiring only: no claim that git history exists in this source copy."""
import copy
from pathlib import Path
import re
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]


def assert_pytest_history(workflow):
    """Every pytest job must have a preceding, explicitly full-history checkout."""
    checked = 0
    for name, job in workflow.get('jobs', {}).items():
        checkout = None
        for step in job.get('steps', []):
            if str(step.get('uses', '')).startswith('actions/checkout@'):
                checkout = step
            if not re.search(r'(?<![\w-])pytest(?![\w-])', str(step.get('run', ''))):
                continue
            checked += 1
            assert checkout is not None, f'{name}: pytest requires a preceding checkout'
            depth = checkout.get('with', {}).get('fetch-depth')
            assert str(depth) == '0', f'{name}: pytest requires fetch-depth: 0 for pinned-history integrity checks'
    return checked


class WorkflowHistoryTests(unittest.TestCase):
    def test_all_pytest_workflows_checkout_full_history(self):
        paths = sorted(set((ROOT / '.github/workflows').glob('*.yml')) | set((ROOT / '.github/workflows').glob('*.yaml')))
        checked = 0
        for path in paths:
            with self.subTest(workflow=path.name):
                workflow = yaml.load(path.read_text(), Loader=yaml.BaseLoader)
                checked += assert_pytest_history(workflow)
        self.assertGreaterEqual(checked, 2, 'Both deployment and PR validation must be checked')

    def workflow(self, depth='0'):
        return {'jobs': {'build': {'steps': [
            {'uses': 'actions/checkout@v4', 'with': {'fetch-depth': depth}},
            {'run': 'uv run --locked pytest -q -ra --fail-on-skip'},
        ]}}}

    def test_shallow_checkout_rejected(self):
        for depth in ('1', '2', None, '${{ inputs.depth }}'):
            with self.subTest(depth=depth), self.assertRaisesRegex(AssertionError, 'fetch-depth'):
                assert_pytest_history(self.workflow(depth))

    def test_default_checkout_depth_rejected(self):
        workflow = self.workflow()
        del workflow['jobs']['build']['steps'][0]['with']
        with self.assertRaisesRegex(AssertionError, 'fetch-depth'):
            assert_pytest_history(workflow)

    def test_late_checkout_rejected(self):
        workflow = self.workflow()
        workflow['jobs']['build']['steps'].reverse()
        with self.assertRaisesRegex(AssertionError, 'preceding checkout'):
            assert_pytest_history(workflow)

    def test_later_shallow_checkout_rejected(self):
        workflow = self.workflow()
        workflow['jobs']['build']['steps'].insert(1, {'uses': 'actions/checkout@v4'})
        with self.assertRaisesRegex(AssertionError, 'fetch-depth'):
            assert_pytest_history(workflow)

    def test_each_pytest_job_checked_independently(self):
        workflow = self.workflow()
        workflow['jobs']['other'] = copy.deepcopy(workflow['jobs']['build'])
        workflow['jobs']['other']['steps'].pop(0)
        with self.assertRaisesRegex(AssertionError, 'other: pytest requires a preceding checkout'):
            assert_pytest_history(workflow)

    def test_no_test_deploy_job_needs_no_checkout(self):
        workflow = self.workflow()
        workflow['jobs']['deploy'] = {'steps': [{'uses': 'actions/deploy-pages@v4'}]}
        self.assertEqual(assert_pytest_history(workflow), 1)


if __name__ == '__main__':
    unittest.main()
