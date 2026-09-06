# Shared GitHub configuration

Explicit presets for Klaas Nicolaas's Python packages. Repositories opt in through their own workflows and Renovate configuration.

| Policy | Central file | Consumer |
| --- | --- | --- |
| Releases | `.github/release-drafter-python.yml` | Release Drafter `config-name` |
| Dependencies | `renovate-python.json` | Renovate `extends` |
| Labels | `labels/python.yml` | Label Blueprint `labels-file` |

## Adopt in a Python package

In `.github/workflows/release-drafter.yaml`, add the following input to Release Drafter v7.7.0 or newer and remove the redundant local `.github/release-drafter.yml`:

```yaml
with:
  config-name: klaasnicolaas/.github:release-drafter-python.yml
```

Use this `.github/renovate.json`:

```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": ["github>klaasnicolaas/.github:renovate-python"]
}
```

Repository-specific overrides can remain alongside `extends`. The preset supports Poetry and PEP 621 projects, pins development dependencies and action digests, and preserves minor/patch dependency automerge and lock-file maintenance. Repository branch protections and CI should govern merge eligibility.

In `.github/workflows/sync-labels.yaml`, use Label Blueprint with:

```yaml
with:
  labels-file: https://raw.githubusercontent.com/klaasnicolaas/.github/main/labels/python.yml
```

The workflow needs `issues: write`. Retain a manual trigger and add a weekly schedule so central label changes propagate without a local commit. Remove the redundant `.github/labels.yml`. Label Blueprint's default `prune: false` preserves extra repository labels.

These references follow the central default branch (`main`): release and dependency changes take effect on the next corresponding run, and labels on the next scheduled or manual sync. Review changes here with all consumers in mind. A repository can temporarily pin a Release Drafter configuration with `@<ref>` or a Renovate preset with `#<ref>`; the label URL can use a commit instead of `main`.

## Release policy

The configuration uses Release Drafter's current `when` and `semver-increment` syntax. Breaking changes and explicit `major` labels increment major; new features and explicit `minor` labels increment minor; otherwise the increment is patch. PRs carrying `sync` are excluded from release notes and version calculation. Existing categories and dependency collapsing are preserved.

## Migration and ownership

Start with `python-gridnet` and `pypackage-template`. Before merging their adoption PRs, exclude these central files and their consuming workflows from legacy `github-config` synchronization. Other repositories keep their existing configuration until migrated individually.

Workflows, package metadata, tests, and licenses remain in each repository. This repository currently defines no account-wide community-health defaults and no implicit `release-drafter.yml` fallback. Product repositories and projects under other owners can choose a separate policy.

## Validation

CI validates the Renovate preset with the official strict validator and exercises release categories, version increments, sync exclusions, and label consistency using Release Drafter v7.7.0's own implementation. To run the release checks locally, clone that version, install its runtime dependencies with `npm ci --ignore-scripts --omit=dev`, and run with Node.js 24:

```sh
RELEASE_DRAFTER_SOURCE=/path/to/release-drafter node tests/validate.mjs
npx --yes --package=renovate@44.65.0 renovate-config-validator --strict renovate-python.json
```

References: [Release Drafter configuration loading](https://github.com/release-drafter/release-drafter/blob/v7.7.0/docs/configuration-loading.md), [Renovate shared presets](https://docs.renovatebot.com/config-presets/), [Label Blueprint](https://github.com/klaasnicolaas/action-label-blueprint).
