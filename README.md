# GitHub defaults

Shared configuration for repositories owned by `klaasnicolaas`.

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

Merge the legacy sync exclusions in [github-config #443](https://github.com/klaasnicolaas/github-config/pull/443) before the consumer changes in [Gridnet #1309](https://github.com/klaasnicolaas/python-gridnet/pull/1309) and [template #579](https://github.com/klaasnicolaas/pypackage-template/pull/579). Publish these central defaults and configure the label token before removing local consumer workflows.

New packages generated from the template need to be added to the central label target list. Other owners should configure their own central defaults and label synchronization. Workflows, licenses, tests and package metadata remain local.
