# Shared Python configuration

Central configuration for Klaas Nicolaas's Python packages. Each repository keeps its own workflows and explicitly selects these presets.

| Configuration | Central file | Reference in package repository |
| --- | --- | --- |
| Release Drafter | `.github/release-drafter-python.yml` | `config-name: klaasnicolaas/.github:release-drafter-python.yml` |
| Renovate | `renovate-python.json` | `extends: ["github>klaasnicolaas/.github:renovate-python"]` |
| Label Blueprint | `labels/python.yml` | `labels-file: https://raw.githubusercontent.com/klaasnicolaas/.github/main/labels/python.yml` |

## Usage

Add the Release Drafter reference under the action's `with` inputs (v7.7.0 or newer). Remove the old local `.github/release-drafter.yml`.

Replace `.github/renovate.json` with:

```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": ["github>klaasnicolaas/.github:renovate-python"]
}
```

Repository-specific Renovate overrides can remain alongside `extends`.

Set Label Blueprint's `labels-file` input to the URL above and remove the old local `.github/labels.yml`. Keep `issues: write`, a manual trigger, and a weekly schedule. Extra repository labels are preserved by default.

All references follow `main`: changes apply on the next corresponding run. Review central changes with the consuming repositories in mind. Workflows, licenses, package metadata, and tests remain local.

## Migration

Gridnet and the package template are the first consumers. Exclude their central configuration and consuming workflows from the old `github-config` synchronization before merging their adoption PRs. Other repositories can migrate individually.

These are explicit Python presets; this repository does not define an account-wide Release Drafter fallback or community-health defaults. Other owners can choose their own policy.

## Validation

CI runs the official Renovate validator:

```sh
npx --yes --package=renovate@44.65.0 renovate-config-validator --strict renovate-python.json
```
