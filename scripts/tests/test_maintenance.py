import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('maintenance', Path(__file__).parents[1] / 'maintenance.py')
maintenance = importlib.util.module_from_spec(spec)
spec.loader.exec_module(maintenance)


class MaintenanceTest(unittest.TestCase):
    def test_reuses_renamed_issue_by_marker(self):
        issue = {'title': 'Updated title', 'body': '<!-- marker -->'}
        self.assertIs(maintenance.find_issue([issue], '<!-- marker -->', 'Old title'), issue)

    def test_ambiguous_issues_stop(self):
        issues = [{'title': 'Migrate', 'body': ''}, {'title': 'Other', 'body': '<!-- marker -->'}]
        with self.assertRaises(ValueError):
            maintenance.find_issue(issues, '<!-- marker -->', 'Migrate')

    def test_shared_template_and_task_overrides(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            (path / 'body.md').write_text('Migrate {repository}')
            manifest = {'epic': {'repository': 'o/planning', 'title': 'Epic', 'body': 'Goal'},
                        'task_defaults': {'title': '{name}: migrate', 'body_file': 'body.md',
                                          'fields': {'Status': 'Todo', 'Batch': '1'}},
                        'tasks': [{'repository': 'o/package', 'fields': {'Batch': 'Pilot'}}]}
            (path / 'plan.json').write_text(json.dumps(manifest))
            task = maintenance.load_manifest(path / 'plan.json')['tasks'][0]
            self.assertEqual(task['title'], 'package: migrate')
            self.assertEqual(task['body'], 'Migrate o/package')
            self.assertEqual(task['fields'], {'Status': 'Todo', 'Batch': 'Pilot'})

    def test_preflight_failure_does_not_create_partial_rollout(self):
        manifest = {'key': 'migration', 'project': 'project',
                    'epic': {'repository': 'o/first', 'title': 'Epic', 'body': 'Goal'},
                    'tasks': [{'repository': 'o/blocked', 'title': 'Task', 'body': 'Work'}]}
        first = {'id': 'repo', 'nameWithOwner': 'o/first', 'isPrivate': False, 'issues': []}
        with patch.object(maintenance, 'project_fields', return_value=[]), \
             patch.object(maintenance, 'repository', side_effect=[first, ValueError('no access')]), \
             patch.object(maintenance, 'mutation') as mutate:
            with self.assertRaises(ValueError):
                maintenance.run(manifest, apply=True)
            mutate.assert_not_called()

    def test_rerun_preserves_progress_and_existing_parent(self):
        epic = {'id': 'epic', 'title': 'Epic', 'body': '', 'url': 'epic-url', 'parent': None}
        task = {'id': 'task', 'title': 'Task', 'body': '', 'url': 'task-url', 'parent': {'id': 'epic'}}
        repo = {'id': 'repo', 'nameWithOwner': 'o/r', 'isPrivate': False, 'issues': [epic, task]}
        manifest = {'key': 'migration', 'project': 'project',
                    'epic': {'repository': 'o/r', 'title': 'Epic', 'body': 'new body'},
                    'tasks': [{'repository': 'o/r', 'title': 'Task', 'body': 'new body'}]}
        with patch.object(maintenance, 'project_fields', return_value=[]), \
             patch.object(maintenance, 'repository', return_value=repo), \
             patch.object(maintenance, 'mutation', return_value={'item': {'id': 'item'}}) as mutate:
            maintenance.run(manifest, apply=False)
            mutate.assert_not_called()
            maintenance.run(manifest, apply=True)
            self.assertEqual([c.args[0] for c in mutate.call_args_list],
                             ['addProjectV2ItemById', 'addProjectV2ItemById'])


if __name__ == '__main__':
    unittest.main()
