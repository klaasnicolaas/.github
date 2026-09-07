# Maintenance epics and repository issues

Create one epic in `klaasnicolaas/.github` and one sub-issue in each affected repository. Add them to the maintenance project. Keep repository inventory cards separate from implementation issues. For code changes, link the PR with `Closes #<issue>` in the same repository; verify default-branch checks before setting the project task to Done.

The script uses Python's standard library and an authenticated `gh` CLI. Your account needs access to manage issues in each target repository and edit the project. Public repository issues are public even when the project is private. The preview prints each destination's visibility. Private repository issues remain private.

Prepare a local JSON manifest and a shared Markdown issue template:

```json
{
  "key": "poetry-to-uv",
  "project": "PROJECT_NODE_ID",
  "epic": {
    "repository": "klaasnicolaas/.github",
    "title": "Poetry → uv",
    "body": "Goal, scope, acceptance criteria and rollout order.",
    "fields": {"Item kind": "Epic", "Epic": "Poetry → uv", "Status": "Todo"}
  },
  "task_defaults": {
    "title": "{name}: Poetry → uv",
    "body_file": "uv-task.md",
    "fields": {"Item kind": "Task", "Epic": "Poetry → uv", "Status": "Todo"}
  },
  "tasks": [
    {"repository": "klaasnicolaas/python-gridnet", "fields": {"Batch": "Pilot"}},
    {"repository": "klaasnicolaas/pypackage-template", "fields": {"Batch": "Template"}}
  ]
}
```

`uv-task.md` contains the shared checklist and may use `{repository}` and `{name}`. Paths are relative to the manifest. Task entries override defaults; `fields` are merged. Existing text and single-select project fields are supported; add the epic option to the project before preparing a new rollout.

```sh
python scripts/maintenance.py /path/to/rollout.json
python scripts/maintenance.py /path/to/rollout.json --apply
```

The first command performs read-only preflight checks for every target, including visibility, access, existing issues and requested field values. Only `--apply` creates or converts issues and establishes relationships. A stable manifest `key` identifies the rollout. For multiple tasks in one repository, give each task a stable `key` as well.

Keep the manifest to resume interrupted work or add repositories later. The script matches its marker (including renamed issues) or an exact title across open and closed issues. Ambiguous matches and conflicting parent relationships stop execution. Repeated runs reuse issues and preserve existing descriptions, status and other project progress. Run only one instance for a rollout at a time; preflight and mutations are not atomic.

To convert an existing project draft without adding another card, supply its node ID as `draft_item` on the epic/task. Its body is replaced with the reviewed manifest body before conversion to an issue in the destination repository. Existing repository inventory cards must not be supplied as migration drafts. If a matching repository issue and an unconverted draft both exist, reconcile those manually first; the script does not delete either.

Check the resulting epic's sub-issue list, project counts and destination URLs after applying. Publishing issues can trigger repository issue automations. Implementation remains a separate step; issue creation does not migrate package code.

Tests:

```sh
python -m unittest discover -s scripts/tests -v
```
