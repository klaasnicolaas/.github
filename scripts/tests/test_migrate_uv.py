import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('migrate_uv', Path(__file__).parents[1] / 'migrate_uv.py')
migrate_uv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migrate_uv)

PROJECT = '''[project]
name = "sample"
version = "0.0.0"
requires-python = ">=3.12,<4.0"
dependencies = ["aiohttp>=3.0.0"]
[tool.poetry]
packages = [{include = "sample", from = "src"}]
[tool.poetry.dependencies]
python = "^3.12"
[tool.poetry.group.dev.dependencies]
coverage = {version = "7.16.2", extras = ["toml"]}
[tool.coverage.run]
source = ["sample"]
[build-system]
requires = ["poetry-core>=2.2.0"]
build-backend = "poetry.core.masonry.api"
'''


class MigrateUvTest(unittest.TestCase):
    def test_preserves_runtime_constraints_and_group_extras(self):
        import tomllib
        result = tomllib.loads(migrate_uv.migrate_project(PROJECT))
        original = tomllib.loads(PROJECT)
        self.assertEqual(result['project'], original['project'])
        self.assertEqual(result['dependency-groups']['dev'], ['coverage[toml]==7.16.2'])
        self.assertNotIn('poetry', result['tool'])
        self.assertEqual(result['build-system']['build-backend'], 'uv_build')

    def test_unknown_poetry_runtime_dependencies_are_rejected(self):
        text = PROJECT.replace('python = "^3.12"', 'python = "^3.12"\ncustom = "^1.0"')
        with self.assertRaisesRegex(ValueError, 'Runtime Poetry dependencies'):
            migrate_uv.migrate_project(text)

    def test_author_email_is_valid_after_backend_change(self):
        text = PROJECT.replace('version = "0.0.0"', 'version = "0.0.0"\nauthors = [{name = "Owner", email = "<owner@example.com>"}]')
        self.assertIn('email="owner@example.com"', migrate_uv.migrate_project(text))

    def test_caret_constraint_preserves_its_upper_bound(self):
        self.assertEqual(migrate_uv.requirement('types-pytz', '^2023.3.0.0'), 'types-pytz>=2023.3.0.0,<2024.0.0.0')
        self.assertEqual(migrate_uv.requirement('sample', '^0.0.3'), 'sample>=0.0.3,<0.0.4')

    def test_custom_package_layout_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Custom package layout'):
            migrate_uv.migrate_project(PROJECT.replace('from = "src"', 'from = "lib"'))

    def test_changed_lock_resolution_restores_original_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'pyproject.toml').write_text(PROJECT)
            (root / 'poetry.lock').write_text('[[package]]\nname = "example"\nversion = "1.0"\n')
            def fake_lock(*args):
                (root / 'uv.lock').write_text('[[package]]\nname = "example"\nversion = "2.0"\nsource = {registry = "https://pypi.org/simple"}\n')
                return ''
            with patch.object(migrate_uv, 'command', side_effect=fake_lock), self.assertRaisesRegex(ValueError, 'Lock resolution changed'):
                migrate_uv.apply(root, {'pyproject.toml': migrate_uv.migrate_project(PROJECT)})
            self.assertEqual((root / 'pyproject.toml').read_text(), PROJECT)
            self.assertTrue((root / 'poetry.lock').exists())
            self.assertFalse((root / 'uv.lock').exists())

    def test_local_changes_and_duplicate_prs_are_rejected(self):
        with patch.object(migrate_uv, 'command', return_value=' M README.md'), self.assertRaisesRegex(ValueError, 'local changes'):
            migrate_uv.preflight(Path('.'))
        with patch.object(migrate_uv, 'command', side_effect=['', '[{"number":1}]', '[{"title":"Migrate to uv"}]']), self.assertRaisesRegex(ValueError, 'Existing migration PRs'):
            migrate_uv.preflight(Path('.'), 'owner/repo')


if __name__ == '__main__':
    unittest.main()
