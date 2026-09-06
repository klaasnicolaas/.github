# GitHub defaults

Shared configuration for repositories owned by `klaasnicolaas`.

## Community defaults

Funding, generic issue forms and the pull request template live in `.github/`. GitHub uses these for repositories under `klaasnicolaas` when no local override exists. Add the issue-form labels (`bug`, `enhancement`, `new-feature`) to this repository and consumers before adoption.

Keep local files for intentional differences. In particular, an existing `ISSUE_TEMPLATE/config.yml` or valid issue form disables inheritance of the whole issue-template folder. Gridnet retains its Discussions link and local forms; Glow retains its hardware-specific issue and PR templates. Their identical funding files can be removed.

New personal packages use the account defaults through the package template's community-defaults option. Other owners can keep generated local templates and funding choices or opt into their own account defaults.

## Release Drafter

The default lives in `.github/release-drafter.yml`. Release Drafter automatically uses it when a repository under this owner has no local configuration. Keep the Release Drafter workflow in each repository; no `config-name` input is needed.

A repository can override the default with its own `.github/release-drafter.yml`, or extend it to override individual settings:

```yaml
---
_extends: klaasnicolaas/.github
name-template: "service-v$RESOLVED_VERSION"
```

Repositories under a different owner use that owner's defaults. The shared configuration uses Release Drafter v7.7.0's current syntax.

## Labels

`labels/base.yml` is synchronized by `.github/workflows/sync-labels.yaml`. Pull requests preview changes using the read-only workflow token; merges to `main` apply them. Manual runs are also supported. Extra repository labels are preserved.

The initial targets are `python-gridnet` and `pypackage-template`. Add other repositories to the workflow as they migrate, and remove their local label configuration and sync workflow.

For synchronization, add the `LABEL_SYNC_TOKEN` Actions secret here: a fine-grained token with Issues read/write access to every listed target repository. The built-in workflow token cannot update other repositories. Extend token access when adding a target. Previews can read labels from these public repositories without that secret.

## Renovate

Python packages retain only this `.github/renovate.json`, plus any repository-specific overrides:

```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": ["github>klaasnicolaas/.github:renovate-python"]
}
```

The shared preset lives in `renovate-python.json`; `.github/renovate.json` maintains this repository's own action dependencies. CI runs the official Renovate validator.

## Migration

The initial release/label pilot is merged: central defaults #1, github-config #443, Gridnet #1309 and template #579. Gridnet has successfully loaded the central Release Drafter policy. Community-default adoption follows the same order: publish defaults, exclude legacy sync paths, then remove redundant consumer files.

New packages generated from the template need to be added to the central label target list. Other owners should configure their own central defaults and label synchronization. Workflows, licenses, tests and package metadata remain local.

For the remaining legacy files, see the [github-config inventory and migration plan](docs/github-config-migration.md).
