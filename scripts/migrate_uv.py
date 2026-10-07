#!/usr/bin/env python3
"""Preview or apply the verified Poetry-to-uv recipe to a clean package checkout."""
import argparse
import json
import re
import subprocess
import tomllib
from pathlib import Path

SETUP_UV = 'astral-sh/setup-uv@c18668ad3cf93ea998bef934396af7bb5c839dc7 # v10.2.0'


def command(root, *args):
    return subprocess.check_output(args, cwd=root, text=True).strip()


def requirement(name, value):
    if isinstance(value, str):
        version = value
        extras = []
    elif isinstance(value, dict) and set(value) <= {'version', 'extras'}:
        version = value['version']
        extras = value.get('extras', [])
    else:
        raise ValueError(f'Unsupported requirement: {name}={value!r}')
    if re.fullmatch(r'\^\d+(?:\.\d+)*', version):
        lower = version[1:]
        parts = [int(part) for part in lower.split('.')]
        index = next((i for i, part in enumerate(parts) if part), len(parts) - 1)
        upper = '.'.join(str(part) for part in parts[:index] + [parts[index] + 1] + [0] * (len(parts) - index - 1))
        suffix = '[' + ','.join(extras) + ']' if extras else ''
        return name + suffix + '>=' + lower + ',<' + upper
    if not re.fullmatch(r'\d[\w.+-]*', version):
        raise ValueError(f'Development requirement must be pinned: {name}={version}')
    suffix = '[' + ','.join(extras) + ']' if extras else ''
    return name + suffix + '==' + version


def migrate_project(text):
    data = tomllib.loads(text)
    poetry = data['tool']['poetry']
    if set(poetry) - {'packages', 'dependencies', 'group', 'requires-poetry'}:
        raise ValueError('Custom Poetry configuration requires manual review')
    if set(poetry.get('dependencies', {})) - {'python'}:
        raise ValueError('Runtime Poetry dependencies require manual review')
    if set(poetry.get('group', {})) != {'dev'}:
        raise ValueError('Custom dependency groups require manual review')
    if data['build-system']['build-backend'] != 'poetry.core.masonry.api':
        raise ValueError('Unexpected build backend')
    module = data['project']['name'].replace('-', '_').replace('.', '_').lower()
    if poetry.get('packages', [{'include': module, 'from': 'src'}]) != [{'include': module, 'from': 'src'}]:
        raise ValueError('Custom package layout requires manual review')
    dynamic = data['project'].get('dynamic', [])
    if dynamic and (dynamic != ['dependencies'] or not data['project'].get('dependencies')):
        raise ValueError('Dynamic metadata requires manual review')
    text = re.sub(r'email\s*=\s*"<([^">]+)>"', r'email="\1"', text)
    text = re.sub(r'(?m)^dynamic = \["dependencies"\]\n', '', text)
    text = re.sub(r'(?ms)^\[tool\.poetry(?:\.[^\]]+)?\]\n.*?(?=^\[|\Z)', '', text)
    lines = ['[dependency-groups]', 'dev = [']
    for name, value in poetry['group']['dev']['dependencies'].items():
        lines.append('  ' + json.dumps(requirement(name, value)) + ',')
    lines.extend([']', ''])
    text = text.replace('[tool.coverage.run]', '\n'.join(lines) + '\n[tool.coverage.run]')
    text = text.replace('build-backend = "poetry.core.masonry.api"', 'build-backend = "uv_build"')
    text = re.sub(r'requires = \["poetry-core[^\]]+\]', 'requires = ["uv_build>=0.12.13,<0.13"]', text)
    migrated = tomllib.loads(text)
    for key in ['dependencies', 'requires-python', 'name', 'version']:
        if migrated['project'].get(key) != data['project'].get(key):
            raise ValueError(f'Changed runtime metadata: {key}')
    return text


def migrate_workflow(text):
    pattern = r'      - name: 🏗 Set up Poetry\n.*?      - name: 🏗 Install (?:Python )?dependencies\n        run: poetry install --no-interaction\n'
    def replace(match):
        content = match.group()
        python = '${{ matrix.python }}' if '${{ matrix.python }}' in content else '${{ env.DEFAULT_PYTHON }}'
        release = 'poetry version' in text
        setup = f'      - name: 🏗 Set up uv\n        uses: {SETUP_UV}\n        with:\n          enable-cache: {"false" if release else "true"}\n          python-version: {python}\n      - name: 🐍 Install Python\n        run: uv python install\n'
        return setup if release else setup + '      - name: 🏗 Install dependencies\n        run: uv sync --locked\n'
    text, count = re.subn(pattern, replace, text, flags=re.S)
    if count == 0 and 'poetry' in text.lower():
        raise ValueError('Unrecognized Poetry workflow setup')
    text = text.replace('poetry run ', 'uv run ').replace('poetry version --no-interaction', 'uv version --frozen').replace('poetry build --no-interaction', 'uv build --no-sources')
    if 'Upload coverage artifact' in text and 'uv build' not in text:
        text = text.replace('      - name: ⬆️ Upload coverage artifact', '      - name: 🏗 Build package\n        if: matrix.python == env.DEFAULT_PYTHON\n        run: uv build --no-sources\n      - name: ⬆️ Upload coverage artifact')
    return text


def migrate_hooks(text):
    return (text.replace('poetry run ', 'uv run ')
            .replace(r'^poetry\.lock$', r'^uv\.lock$')
            .replace('- id: poetry\n        name: 📜 Check pyproject with Poetry', '- id: uv-lock\n        name: 📜 Check uv lockfile')
            .replace('entry: poetry check', 'entry: uv lock --check')
            .replace('[commit, push, manual]', '[pre-commit, pre-push, manual]'))


def plan(root):
    changes = {'pyproject.toml': migrate_project((root / 'pyproject.toml').read_text()),
               '.pre-commit-config.yaml': migrate_hooks((root / '.pre-commit-config.yaml').read_text())}
    for path in (root / '.github/workflows').glob('*.yaml'):
        text = path.read_text()
        if 'poetry' in text.lower():
            changes[str(path.relative_to(root))] = migrate_workflow(text)
    path = root / '.devcontainer/devcontainer.json'
    if path.exists():
        text = path.read_text().replace('ghcr.io/devcontainers-extra/features/poetry:2', 'ghcr.io/devcontainers-extra/features/uv:1')
        text = text.replace('poetry config virtualenvs.in-project true && poetry install', 'uv sync --locked').replace('poetry run ', 'uv run ')
        text = text.replace('    "ghcr.io/devcontainers-extra/features/pre-commit:2": {},\n', '')
        changes[str(path.relative_to(root))] = text
    path = root / 'README.md'
    text = path.read_text().replace('[Poetry][poetry]', '[uv][uv]').replace('[Poetry][poetry-install]', '[uv][uv-install]')
    text = text.replace('poetry install', 'uv sync --locked').replace('poetry run ', 'uv run ')
    text = re.sub(r'_Poetry creates by default an virtual environment where it installs all\n[^\n]+', '_uv creates a project virtual environment in `.venv` and installs the locked dependencies._', text)
    text = text.replace('[poetry-install]: https://python-poetry.org/docs/#installation', '[uv-install]: https://docs.astral.sh/uv/getting-started/installation/').replace('[poetry]: https://python-poetry.org', '[uv]: https://docs.astral.sh/uv/')
    changes['README.md'] = text
    path = root / '.github/renovate.json'
    if path.exists():
        data = json.loads(path.read_text())
        rule = {'matchManagers': ['pep621'], 'matchDepTypes': ['dependency-groups'], 'rangeStrategy': 'pin'}
        rules = data.setdefault('packageRules', [])
        if rule not in rules:
            rules.append(rule)
        changes[str(path.relative_to(root))] = json.dumps(data, indent=2) + '\n'
    for name, text in changes.items():
        if 'poetry' in text.lower():
            raise ValueError(f'Remaining Poetry configuration in {name}; inspect before applying')
    return changes


def preflight(root, repository=None):
    if command(root, 'git', 'status', '--porcelain'):
        raise ValueError('Checkout has local changes; refusing to overwrite them')
    if repository:
        issues = json.loads(command(root, 'gh', 'issue', 'list', '--repo', repository, '--state', 'open', '--search', '"Poetry → uv" in:title', '--json', 'number,title,url'))
        prs = json.loads(command(root, 'gh', 'pr', 'list', '--repo', repository, '--state', 'open', '--json', 'number,title,url,headRefName'))
        migrations = [p for p in prs if 'uv' in p['title'].lower() and 'migrat' in p['title'].lower()]
        if migrations:
            raise ValueError(f'Existing migration PRs: {migrations}')
        if len(issues) != 1:
            raise ValueError(f'Expected one existing migration task: {issues}')
        return issues[0]
    return None


def apply(root, changes):
    old_lock = tomllib.loads((root / 'poetry.lock').read_text())
    old = {p['name']: p['version'] for p in old_lock['package']}
    originals = {name: (root / name).read_text() for name in changes}
    if (root / 'uv.lock').exists():
        raise ValueError('Existing uv.lock requires manual review')
    try:
        for name, text in changes.items():
            (root / name).write_text(text)
        project = root / 'pyproject.toml'
        constraints = [f'{name}=={version}' for name, version in old.items()]
        project.write_text(changes['pyproject.toml'] + '\n[tool.uv]\nconstraint-dependencies = ' + json.dumps(constraints) + '\n')
        command(root, 'uv', 'lock')
        project.write_text(changes['pyproject.toml'])
        command(root, 'uv', 'lock')
        new = {p['name']: p['version'] for p in tomllib.loads((root / 'uv.lock').read_text())['package'] if 'editable' not in p['source']}
        if old != new:
            raise ValueError(f'Lock resolution changed: old={old}, new={new}')
        command(root, 'uv', 'lock', '--check')
        (root / 'poetry.lock').unlink()
    except Exception:
        for name, text in originals.items():
            (root / name).write_text(text)
        (root / 'uv.lock').unlink(missing_ok=True)
        raise
    return len(old)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('checkout', type=Path)
    parser.add_argument('--repository', help='owner/repo; verify the existing issue and reject duplicate migration PRs')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--apply', action='store_true')
    mode.add_argument('--dry-run', action='store_true', help='preview without writes (default)')
    args = parser.parse_args()
    root = args.checkout.resolve()
    issue = preflight(root, args.repository)
    changes = plan(root)
    result = {'checkout': str(root), 'issue': issue, 'files': list(changes) + ['poetry.lock -> uv.lock'], 'apply': args.apply}
    if args.apply:
        result['preserved_locked_dependencies'] = apply(root, changes)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
